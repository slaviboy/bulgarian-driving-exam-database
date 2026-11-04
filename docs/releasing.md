# Releasing a dataset

A dataset release is **two GitHub releases**:

| Tag | Contents | Marked latest |
|---|---|---|
| `media-YYYY.MM.DD` (one per official edition) | `images-original.zip`, `images-webp.zip`, every video as `<media id>.mp4` | never |
| `vX.Y.Z` | `manifest.json`, `categories.json`, `questions.json`, `exam-configs.json`, `master.sqlite`, `dataset-core-vX.Y.Z.zip`, `SHA256SUMS`, reports | yes |

Consumers start from `…/releases/latest/download/manifest.json`; the manifest points to the media
release by URL and SHA-256, so a media release is reused by every dataset version of the same edition.

## Choosing the version

* **MAJOR** — `schema_version` changes (breaking contract change).
* **MINOR** — a new official edition, or questions added/removed.
* **PATCH** — corrections, metadata, exam-rule fixes with the same questions.

## Option A — release workflow (recommended for later releases)

Actions → **release** → *Run workflow* with the version. The workflow extracts the official source
(incrementally, with a cache), downloads and verifies media, builds and validates, runs the licensing
gate (`qb verify`), publishes the media release if the edition is new, publishes `vX.Y.Z`, and opens a
pull request with the updated exports and reports.

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

## After publishing

```
curl -sSL https://github.com/slaviboy/bulgarian-driving-exam-database/releases/latest/download/manifest.json | head
```

must return the new manifest anonymously. Then update `CHANGELOG.md` and the Android app's pinned
dataset (`gradle/dataset.properties` in the app repository).
