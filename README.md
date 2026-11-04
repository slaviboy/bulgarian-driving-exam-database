# bulgarian-driving-exam-database

Open-source tools, structured data schemas and versioned resources for Bulgarian
driving licence examination question banks.

> **Status: under construction.** See [PROJECT_STATUS.md](PROJECT_STATUS.md).

This repository extracts the official theory-exam question array published by the
Executive Agency "Automobile Administration" (ИААА) at
https://public-eis.rta.government.bg/exam-questions/, validates it, and publishes it
as versioned JSON + SQLite datasets with media packs.

* Data contract: [docs/data-contract.md](docs/data-contract.md)
* Architecture: [docs/architecture.md](docs/architecture.md)
* Origin, attribution and redistribution status of the question content:
  [DATA_NOTICE.md](DATA_NOTICE.md) — **read before reusing the data**.

Code is MIT-licensed; the licence does not cover the question content.
This project is not affiliated with ИААА.
