# Security policy

## Supported versions

Only the latest dataset release and the `main` branch of the tooling receive fixes.

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Report them privately through GitHub's
"Report a vulnerability" button (Security → Advisories) on this repository, or contact the
maintainer through https://github.com/slaviboy.

Relevant reports include, for example:

* a way to make the pipeline publish data that was not validated, or to bypass the licensing gate;
* a malicious-input problem in the parsers (the official HTML, AvtoIzpit JSON, downloaded media);
* release artifacts whose checksums do not match the manifest.

You will receive an acknowledgement within a week. Fixed issues are listed in `CHANGELOG.md`.

## Integrity of the data

Every release manifest lists the SHA-256 of all files and media packs. Consumers must verify them
before use (see `docs/android-import-spec.md`). This project never stores credentials; the release
workflow uses the repository's short-lived `GITHUB_TOKEN`.
