# Clean, sharp pictures — how the enhanced media are made

The official pictures carry a tiled "ИААА" stamp and are small. From dataset **v1.3.0** apps receive, for every
picture, a stamp-free and enlarged WebP, and for road signs and vehicle markings also an SVG. The originals stay
published unchanged (`images-original.zip`). Package: `question_bank/media_enhance/`; commands: `qb enhance …`.

## 1. Removing the stamp (`stamp.py`, `fit.py`, `clean.py`)

The stamp is one 90 × 90 px tile (a logo and the word "ИААА" twice; white letters with a black outline, at most
77/255 opaque), composited with straight-alpha "over" at whole-pixel positions. Its lattice is anchored at the
picture centre: the tile containing the centre starts at `(⌈h/2⌉ − 74, ⌊w/2⌋ − 84)`.

* **Tile:** wherever a picture's own background is transparent, the published alpha *is* the stamp opacity and
  the published colour *is* the stamp colour. Folding those pixels of 321 pictures onto the tile and taking the
  most frequent exact 8-bit value per tile pixel gives the tile exactly.
* **Positions:** the stamp was a hand-made layer, so whole tiles sit up to two pixels off the lattice. For each
  tile and candidate shift, the edge energy left after removing it is summed over all pictures that contain it;
  the cheapest shift wins. A second pass re-measures each element in its own coordinates.
* **Removal:** `A0 = (A − a) / (1 − a)`, `C0 = (A·C − a·W) / (A0·(1 − a))`; pixels the stamp does not touch stay
  byte-identical (checked). A stamp score (correlation of the picture's detail with the stamp's expected
  detail) drops from a median 0.43 to −0.004 over the 830 pictures.

Files: `data/enhance/stamp/stamp-tile.png`, `shifts.json`.

## 2. Enlarging (`upscale.py`)

Real-ESRGAN x4plus (`realesrgan-ncnn-vulkan`, BSD-3, local GPU; `QB_REALESRGAN` or `data/cache/tools/realesrgan/`)
enlarges every non-sign picture 4×; the result is resized to about 1400 px on the long side (2–4× the original).
**Content check:** shrunk back to the original size, the enlargement must keep the stamp-free picture's
structure — PSNR after a light blur ≥ 30 dB and SSIM ≥ 0.9; the worst 16 px window is recorded. No generative
redrawing: details such as the а/б/в labels, arrows and numbers must stay as they are.

## 3. Signs and markings as vectors (`commons.py`, `signmatch.py`, `signs.py`, `trace.py`)

* **Drawings:** the Bulgarian sign drawings of Wikimedia Commons are downloaded by the maintainer's browser with
  `tools/commons-signs-download.html` (Wikimedia refuses scripts without a contact address; the project sends no
  personal data) and imported with `qb enhance commons-import <zip>` (SHA-1 checked).
* **Matching:** `signmatch` ranks the drawings for each picture; every choice was then made by hand on contact
  sheets (direction of arrows, curves and narrowings checked at full size).
* **Recipes** (`data/enhance/signs/recipes.json`) place drawings into boxes measured on the picture, so the SVG
  keeps the picture's size. Operations: `rotate` (plates), `exact` placement (traced pieces), `covers` (paint
  over a drawing's own number or distance panel before the picture's lettering is placed on top).
* **Tracing** (`trace.py`), for what Commons lacks: the stamp-free picture enlarged 4×, Lab k-means colours with
  anti-aliasing assigned to the nearer of the two colours it blends, contours with holes, corners kept,
  Schneider Bézier fitting. Pieces: `data/enhance/signs/traced/`.
* **Hand-drawn:** `data/enhance/markings/` (three-dot badge, slow-vehicle triangle).

All SVGs pass `svg.sanitise` (the static subset AndroidSVG draws: no scripts, external references, live text or
filters). `qb enhance signs-build` composes them and renders 4× raster copies.

## 4. Packs and release (`pack.py`)

`qb enhance pack --revision N` writes `images-webp.zip` (all 830 pictures) and `images-svg.zip` (303 signs and
markings) to `release/media-YYYY.MM.DD-rN/`, and records every file (size, SHA-256, dimensions, `process`,
`credits`) in `data/enhance/derivatives.json` and the packs in `data/enhance/pack.json`. A WebP as large as the
previous one is re-encoded, because some apps detect a new file by its size.

The packs are published once as a GitHub release (`gh release create media-YYYY.MM.DD-rN …`); CI never rebuilds
them: `qb media` downloads and verifies the pinned packs, and `qb build` checks every enhanced file against
`derivatives.json` and rebuilds the packs byte for byte before the manifest points at the revision's URLs.

## Commands, in order

```
qb enhance stamp-fit                     # data/enhance/stamp (tile, shifts)
qb enhance clean                         # data/media/enhance/clean + stamp scores
qb enhance upscale --classes scene,photo,traffic-light,dashboard-symbol,drawing
qb enhance upscale --classes sign,vehicle-marking --scale 4 --into upscaled4   # tracing input
qb enhance commons-import bg-road-signs-commons.zip
qb enhance signs-build --sheet signs-all # SVGs, raster copies, review sheet
qb enhance pack --revision 2             # packs, derivatives.json, pack.json
qb enhance review --name …               # local before/after sheets
```

Reviews and accepted flags: `data/enhance/review.json`. Inventory of all pictures by kind:
`data/enhance/inventory.json`.
