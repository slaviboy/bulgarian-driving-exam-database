# Releasing a dataset

A dataset release is **two GitHub releases**:

| Tag | Contents | Marked latest |
|---|---|---|
| `media-YYYY.MM.DD` (one per official edition) | `images-original.zip`, `images-webp.zip`, every video as `<media id>.mp4` | never |
| `media-YYYY.MM.DD-rN` (media revision, since 1.3.0) | enhanced `images-webp.zip` and `images-svg.zip` | never |
| `vX.Y.Z` | `manifest.json`, `categories.json`, `questions.json`, `exam-configs.json`, `master.sqlite`, `dataset-core-vX.Y.Z.zip`, `SHA256SUMS`, reports | yes |

Consumers start from `…/releases/latest/download/manifest.json`; the manifest points to the media
release by URL and SHA-256, so a media release is reused by every dataset version of the same edition.

## Choosing the version

* **MAJOR** — `schema_version` changes (breaking contract change).
* **MINOR** — a new official edition, or questions added/removed.
* **PATCH** — corrections, metadata, exam-rule fixes with the same questions.

## Option A — release workflow (used for v1.1.0)

Actions → **release** → *Run workflow* with the version. The workflow extracts the official source
(incrementally, with a cache), downloads and verifies media, builds and validates, runs the licensing
gate (`qb verify`), publishes the media release if the edition is new, publishes `vX.Y.Z`, and opens a
pull request with the updated exports and reports.

* The run takes about 40 minutes without a cache, most of it the polite media download.
* Opening the pull request needs *Allow GitHub Actions to create and approve pull requests* (Settings →
  Actions → General). Without it, the workflow pushes the branch `release/vX.Y.Z`, warns, and the
  maintainer opens the pull request from that branch.
* Merge the pull request after its checks pass, so `main` holds the published exports.

## Option B — from a maintainer machine (used for v1.0.0)

```
qb extract && qb media
qb build --dataset-version X.Y.Z      # must end with completeness: complete and 0 errors
qb verify
git add data/exports reports contract && git commit -m "Dataset vX.Y.Z" && git push

tag=media-YYYY.MM.DD                  # from manifest.json → media_base_url
gh release create "$tag" release/$tag/* --latest=false --title "Media $tag" --notes "…"
gh release create vX.Y.Z release/vX.Y.Z/* reports/validation-report.md reports/extraction-report.md \
   --latest --title "Dataset vX.Y.Z" --notes "…"
```

## Media revisions (enhanced pictures)

The enhanced pictures (docs/media-enhance.md) are built on a maintainer machine — they need the GPU, the
Commons drawings and the reviewed recipes — and published **before** the dataset release that uses them:

```
qb enhance pack --revision N             # release/media-YYYY.MM.DD-rN, data/enhance/{derivatives,pack}.json
gh release create media-YYYY.MM.DD-rN release/media-YYYY.MM.DD-rN/* --latest=false    --title "Media YYYY.MM.DD-rN (enhanced pictures)" --notes "…"
git add data/enhance && git commit -m "Pin media revision rN" && git push
```

From then on every build uses the pinned packs: `qb media` downloads and verifies them, and `qb build` fails if
a local file differs from the published one (`PinnedPackMismatch`). A new official edition needs a new
revision of its own (the stamp model, inventory and recipes are reviewed again for changed pictures).

## After publishing

```
curl -sSL https://github.com/slaviboy/bulgarian-driving-exam-database/releases/latest/download/manifest.json | head
```

must return the new manifest anonymously. Then update `CHANGELOG.md` and the Android app's pinned
dataset (`gradle/dataset.properties` in the app repository).
