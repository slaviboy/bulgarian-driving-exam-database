"""Trace flat-colour pictures (signs, plates, vehicle markings) into compact SVG paths.

Used where Wikimedia Commons has no drawing: the stamp-free official picture, enlarged 4× by Real-ESRGAN so
that its edges are sharp, is reduced to a few flat colours and every colour region becomes one path.

1. Colours: k-means in Lab over the visible pixels; centres closer than ``merge_delta`` are merged. Specks
   smaller than ``min_area`` take the colour that surrounds them.
2. Paths: each region's contours, holes included (even-odd fill), are split at corners and the smooth runs
   are fitted with cubic Béziers (Schneider's algorithm) within ``tolerance`` pixels.
3. Order: the largest region is painted first; every region is grown by one enlarged pixel (a quarter of an
   original pixel) so that no seam shows between neighbours.

The SVG uses the original picture's coordinates (``scale`` = enlargement factor of the input).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# ---------------------------------------------------------------------- colours


def _lab(rgb: np.ndarray) -> np.ndarray:
    import cv2

    return (
        cv2.cvtColor(rgb.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_RGB2LAB)
        .reshape(-1, 3)
        .astype(np.float32)
    )


@dataclass
class Palette:
    colours: list[tuple[int, int, int]]  # RGB per label
    labels: np.ndarray  # (h, w) int32, -1 = transparent


def quantise(rgba: np.ndarray, k_max: int = 8, merge_delta: float = 14.0, min_area: int = 24) -> Palette:
    import cv2

    h, w = rgba.shape[:2]
    visible = rgba[..., 3] >= 128
    rgb = rgba[..., :3][visible].astype(np.float32)
    lab = _lab(rgb)
    pick = np.random.default_rng(0).choice(len(lab), size=min(len(lab), 40_000), replace=False)
    sample, sample_rgb = lab[pick], rgb[pick]
    k = min(k_max, max(1, len(np.unique(sample.round(), axis=0))))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 60, 0.2)
    _, member, centres = cv2.kmeans(sample, k, None, criteria, 4, cv2.KMEANS_PP_CENTERS)
    member = member.ravel()
    # merge perceptually close centres (Lab), keeping each cluster's mean colour in RGB
    clusters: list[tuple[np.ndarray, np.ndarray, int]] = []  # (lab centre, rgb mean, size)
    for idx in np.argsort(-np.bincount(member, minlength=k)):
        sel = member == idx
        n = int(sel.sum())
        if n == 0:
            continue
        c_lab, c_rgb = centres[idx], sample_rgb[sel].mean(axis=0)
        for j, (m_lab, m_rgb, mn) in enumerate(clusters):
            if np.linalg.norm(c_lab - m_lab) < merge_delta:
                clusters[j] = (
                    (m_lab * mn + c_lab * n) / (mn + n),
                    (m_rgb * mn + c_rgb * n) / (mn + n),
                    mn + n,
                )
                break
        else:
            clusters.append((c_lab, c_rgb, n))
    palette = _drop_blends(np.array([c for _, c, _ in clusters]), np.array([n for _, _, n in clusters]))
    labels = np.full((h, w), -1, np.int32)
    labels[visible] = _assign(rgb, palette)
    labels = _remove_specks(labels, len(palette), min_area)
    colours = []
    for i in range(len(palette)):
        sel = labels == i
        mean = rgba[..., :3][sel].mean(axis=0) if sel.any() else palette[i]
        colours.append(tuple(int(v) for v in _snap(mean)))
    return Palette(colours, labels)


def _assign(rgb: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Label each pixel with a palette colour. An anti-aliased edge pixel is a blend of the two colours it
    sits between, so it goes to the nearer end of that pair rather than to whichever colour is closest."""
    d_single = np.linalg.norm(rgb[:, None] - palette[None], axis=-1)  # (n, k)
    best = d_single.min(axis=1)
    label = d_single.argmin(axis=1)
    for i in range(len(palette)):
        for j in range(i + 1, len(palette)):
            a, b = palette[i], palette[j]
            span = float((b - a) @ (b - a))
            if span < 1e-6:
                continue
            t = np.clip(((rgb - a) @ (b - a)) / span, 0, 1)
            d = np.linalg.norm(a + t[:, None] * (b - a) - rgb, axis=1)
            better = d < best - 1e-6
            best = np.where(better, d, best)
            label = np.where(better, np.where(t < 0.5, i, j), label)
    return label


def _drop_blends(
    palette: np.ndarray, sizes: np.ndarray, small: float = 0.04, near: float = 20.0
) -> np.ndarray:
    """Remove small clusters that are only anti-aliasing: in RGB their colour lies on the segment between two
    larger clusters (or next to one)."""
    total = sizes.sum()
    big = [i for i in range(len(palette)) if sizes[i] / total >= small]
    keep = np.ones(len(palette), bool)
    for c in range(len(palette)):
        if c in big or not big:
            continue
        p = palette[c]
        for i in big:
            for j in big:
                a, b = palette[i], palette[j]
                span = float((b - a) @ (b - a))
                t = 0.0 if span < 1e-6 else float(np.clip(((p - a) @ (b - a)) / span, 0, 1))
                if np.linalg.norm(a + t * (b - a) - p) < near:
                    keep[c] = False
    return palette[keep]


def _snap(rgb: np.ndarray) -> np.ndarray:
    """Near-white and near-black become exactly white and black (as they are on the real sign)."""
    if (rgb > 238).all():
        return np.array([255, 255, 255])
    if (rgb < 30).all():
        return np.array([0, 0, 0])
    return np.rint(rgb)


def _remove_specks(labels: np.ndarray, n: int, min_area: int) -> np.ndarray:
    import cv2

    out = labels.copy()
    for _ in range(2):
        for i in range(-1, n):
            mask = (out == i).astype(np.uint8)
            count, comp, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=4)
            for c in range(1, count):
                if stats[c, cv2.CC_STAT_AREA] >= min_area:
                    continue
                sel = comp == c
                ring = cv2.dilate(sel.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~sel
                neighbours = out[ring]
                neighbours = neighbours[neighbours != i]
                if len(neighbours):
                    values, freq = np.unique(neighbours, return_counts=True)
                    out[sel] = values[np.argmax(freq)]
    return out


# ---------------------------------------------------------------------- curve fitting (Schneider)


def _bezier(ctrl: np.ndarray, t: np.ndarray) -> np.ndarray:
    mt = 1 - t
    return (
        (mt**3)[:, None] * ctrl[0]
        + (3 * mt**2 * t)[:, None] * ctrl[1]
        + (3 * mt * t**2)[:, None] * ctrl[2]
        + (t**3)[:, None] * ctrl[3]
    )


def _bezier_d1(ctrl: np.ndarray, t: np.ndarray) -> np.ndarray:
    mt = 1 - t
    return (
        (3 * mt**2)[:, None] * (ctrl[1] - ctrl[0])
        + (6 * mt * t)[:, None] * (ctrl[2] - ctrl[1])
        + (3 * t**2)[:, None] * (ctrl[3] - ctrl[2])
    )


def _bezier_d2(ctrl: np.ndarray, t: np.ndarray) -> np.ndarray:
    mt = 1 - t
    return (6 * mt)[:, None] * (ctrl[2] - 2 * ctrl[1] + ctrl[0]) + (6 * t)[:, None] * (
        ctrl[3] - 2 * ctrl[2] + ctrl[1]
    )


def _chord_params(points: np.ndarray) -> np.ndarray:
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    return d / d[-1] if d[-1] > 0 else np.linspace(0, 1, len(points))


def _generate(points: np.ndarray, u: np.ndarray, t0: np.ndarray, t1: np.ndarray) -> np.ndarray:
    p0, p3 = points[0], points[-1]
    a0 = t0[None] * (3 * (1 - u) ** 2 * u)[:, None]
    a1 = t1[None] * (3 * (1 - u) * u**2)[:, None]
    c = np.array([[(a0 * a0).sum(), (a0 * a1).sum()], [(a0 * a1).sum(), (a1 * a1).sum()]])
    base = _bezier(np.array([p0, p0, p3, p3]), u)
    rhs = points - base
    x = np.array([(a0 * rhs).sum(), (a1 * rhs).sum()])
    det = c[0, 0] * c[1, 1] - c[0, 1] * c[1, 0]
    seg = np.linalg.norm(p3 - p0)
    if abs(det) > 1e-12:
        alpha0 = (x[0] * c[1, 1] - x[1] * c[0, 1]) / det
        alpha1 = (c[0, 0] * x[1] - c[1, 0] * x[0]) / det
    else:
        alpha0 = alpha1 = seg / 3
    eps = 1e-6 * seg
    if alpha0 < eps or alpha1 < eps:
        alpha0 = alpha1 = seg / 3
    return np.array([p0, p0 + t0 * alpha0, p3 + t1 * alpha1, p3])


def _reparametrise(ctrl: np.ndarray, points: np.ndarray, u: np.ndarray) -> np.ndarray:
    q, d1, d2 = _bezier(ctrl, u), _bezier_d1(ctrl, u), _bezier_d2(ctrl, u)
    num = ((q - points) * d1).sum(1)
    den = (d1 * d1).sum(1) + ((q - points) * d2).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        nu = np.where(np.abs(den) > 1e-12, u - num / den, u)
    return np.clip(nu, 0, 1)


def _max_error(ctrl: np.ndarray, points: np.ndarray, u: np.ndarray) -> tuple[float, int]:
    d = ((_bezier(ctrl, u) - points) ** 2).sum(1)
    i = int(np.argmax(d))
    return float(d[i]), i


def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def fit_cubic(
    points: np.ndarray, t0: np.ndarray, t1: np.ndarray, tolerance: float, depth: int = 0
) -> list[np.ndarray]:
    """Cubic Béziers (4 × 2 control points each) through ``points`` within ``tolerance`` (Schneider 1990)."""
    if len(points) == 2 or depth > 12:
        dist = np.linalg.norm(points[-1] - points[0]) / 3
        return [np.array([points[0], points[0] + t0 * dist, points[-1] + t1 * dist, points[-1]])]
    u = _chord_params(points)
    ctrl = _generate(points, u, t0, t1)
    err, split = _max_error(ctrl, points, u)
    tol2 = tolerance * tolerance
    if err < tol2:
        return [ctrl]
    if err < 4 * tol2:
        for _ in range(4):
            u = _reparametrise(ctrl, points, u)
            ctrl = _generate(points, u, t0, t1)
            err, split = _max_error(ctrl, points, u)
            if err < tol2:
                return [ctrl]
    split = min(max(split, 1), len(points) - 2)
    centre = _unit(points[split - 1] - points[split + 1])
    return fit_cubic(points[: split + 1], t0, centre, tolerance, depth + 1) + fit_cubic(
        points[split:], -centre, t1, tolerance, depth + 1
    )


def _corners(contour: np.ndarray, span: int = 4, max_angle: float = 140.0) -> list[int]:
    n = len(contour)
    if n < 2 * span + 2:
        return []
    prev = contour[(np.arange(n) - span) % n] - contour
    nxt = contour[(np.arange(n) + span) % n] - contour
    cos = (prev * nxt).sum(1) / (np.linalg.norm(prev, axis=1) * np.linalg.norm(nxt, axis=1) + 1e-12)
    angle = np.degrees(np.arccos(np.clip(cos, -1, 1)))
    sharp = angle < max_angle
    corners = []
    for i in np.nonzero(sharp)[0]:  # keep the sharpest point of each run of sharp points
        window = [(i + d) % n for d in range(-span, span + 1)]
        if angle[i] == min(angle[j] for j in window):
            corners.append(int(i))
    return sorted(set(corners))


def _smooth_run(run: np.ndarray, sigma: float, closed: bool) -> np.ndarray:
    """Gaussian smoothing along a run of contour points (pixel staircase → the edge it samples); a closed
    run is smoothed cyclically, an open one keeps its end points (corners) fixed."""
    n = len(run)
    if n < 5 or sigma <= 0:
        return run
    radius = max(1, int(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-radius, radius + 1) / sigma) ** 2)
    k /= k.sum()
    if closed:
        padded = np.concatenate([run[-radius:], run, run[:radius]])
    else:
        padded = np.concatenate([np.repeat(run[:1], radius, 0), run, np.repeat(run[-1:], radius, 0)])
    out = np.stack([np.convolve(padded[:, i], k, mode="valid") for i in range(2)], axis=1)
    if not closed:
        out[0], out[-1] = run[0], run[-1]
    return out


def contour_path(contour: np.ndarray, tolerance: float, sigma: float = 1.6) -> list[np.ndarray]:
    """Closed contour (N × 2, float) → list of Bézier segments."""
    pts = contour.astype(float)
    n = len(pts)
    if n < 3:
        return []
    corners = _corners(pts)
    if not corners:
        pts = _smooth_run(pts, sigma, closed=True)
        corners = [0, n // 4, n // 2, 3 * n // 4]
        smooth = True
    else:
        smooth = False
    segments = []
    for a, b in zip(corners, [*corners[1:], corners[0] + n], strict=True):
        idx = np.arange(a, b + 1) % n
        run = pts[idx] if smooth else _smooth_run(pts[idx], sigma, closed=False)
        if len(run) < 2:
            continue
        if smooth:
            t0 = _unit(pts[(a + 1) % n] - pts[(a - 1) % n])
            t1 = -_unit(pts[(b + 1) % n] - pts[(b - 1) % n])
        else:
            t0 = _unit(run[min(2, len(run) - 1)] - run[0])
            t1 = _unit(run[max(-3, -len(run))] - run[-1])
        segments += fit_cubic(run, t0, t1, tolerance)
    return segments


# ---------------------------------------------------------------------- SVG


def _fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _path_data(contours: list[np.ndarray], scale: float, tolerance: float) -> str:
    parts = []
    for contour in contours:
        segs = contour_path(contour, tolerance)
        if not segs:
            continue
        p0 = segs[0][0] / scale
        d = [f"M{_fmt(p0[0])} {_fmt(p0[1])}"]
        for s in segs:
            c = s[1:] / scale
            d.append("C" + " ".join(f"{_fmt(x)} {_fmt(y)}" for x, y in c))
        parts.append("".join(d) + "Z")
    return "".join(parts)


def trace(
    rgba: np.ndarray,
    *,
    scale: float = 4.0,
    tolerance: float = 1.6,
    k_max: int = 8,
    min_area: int = 24,
    keep=None,
) -> bytes:
    """SVG of ``rgba`` (an enlarged picture) in the original picture's coordinates (size / ``scale``).

    ``keep(rgb) -> bool`` limits the output to some colours, e.g. only the lettering of a number that is put
    on another drawing.
    """
    import cv2

    palette = quantise(rgba, k_max=k_max, min_area=min_area)
    h, w = rgba.shape[:2]
    order = sorted(range(len(palette.colours)), key=lambda i: -(palette.labels == i).sum())
    if keep is not None:
        order = [i for i in order if keep(palette.colours[i])]
    width, height = w / scale, h / scale
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_fmt(width)} {_fmt(height)}" '
        f'width="{_fmt(width)}" height="{_fmt(height)}">'
    ]
    for i in order:
        mask = (palette.labels == i).astype(np.uint8)
        if mask.sum() == 0:
            continue
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))  # one enlarged pixel of overlap against seams
        contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        contours = [c[:, 0, :] + 0.5 for c in contours if cv2.contourArea(c) >= min_area]
        d = _path_data(contours, scale, tolerance)
        if d:
            r, g, b = palette.colours[i]
            out.append(f'<path fill="#{r:02x}{g:02x}{b:02x}" fill-rule="evenodd" d="{d}"/>')
    out.append("</svg>")
    return "\n".join(out).encode()
