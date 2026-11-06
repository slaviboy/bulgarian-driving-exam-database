# Licensing and provenance record

_Recorded 2026-11-04. This is a factual record, not legal advice._

## 1. Findings per source

| Question | Official array (ИААА) | AvtoIzpit |
|---|---|---|
| Licence attached to the content | **None found** | **None found** |
| Copyright notice | "© 2022-2026 Всички права запазени" (site footer) | none on the pages read; privacy notice signed by ИААА |
| Terms of use / reuse statement | none on rta.government.bg or the array page | none |
| Open-data release (data.egov.bg) | none found | none found |
| Redistribution of text permitted? | not stated | not stated |
| Redistribution of images/videos permitted? | not stated | not stated |
| Modification permitted? | not stated | not stated |
| Commercial use permitted? | not stated | not stated |
| Attribution requirement | none stated; this project always attributes | — |
| Third-party rights | photographs, drawings and videos may involve third-party authors; unknown | same media served by ИААА |

## 2. Legal context (as found, unverified by a lawyer)

* **Наредба № 38 от 16.04.2004 г., чл. 38, ал. 1** (verified in the consolidated text): the exam
  questions are approved by the Executive Director of ИААА ("…изпълнителният директор на
  Изпълнителна агенция „Автомобилна администрация“ утвърждава изпитни въпроси…"); ал. 2 (since
  12.12.2024) requires coordination with the chair of ДАБДП before approval.
* **ЗАПСП, чл. 4, т. 1** (quoted from secondary sources): normative and individual acts of state
  bodies and their official translations are not subject to copyright. Whether an approved
  question array — and particularly its photographs and videos — falls under this exemption is not
  settled.
* **ЗДОИ** (re-use of public-sector information) could not be read verbatim during the
  investigation; it typically excludes information subject to third parties' intellectual
  property rights.

## 3. Decision

Licensing is **unclear**. The maintainer decided on 2026-11-04 to **publish the full content
(question text, answers, correct markers, images and videos) with attribution**, explicitly
accepting the legal uncertainty. The decision is recorded in:

* `DATA_NOTICE.md` (human-readable notice, takedown process);
* every manifest: `licensing.redistribution_status = "published_by_maintainer_decision"`,
  `licensing.license = "none granted by source"`;
* the release workflow, which refuses to publish data whose source status is not in its
  allow-list.

No licence for the content is granted by this project. The MIT licence covers code, schemas and
documentation only.

## 4. How the content is handled

* **Attribution** on every release, in the manifest, in the app's About screen, and in the source
  table of `master.sqlite`.
* **Provenance per record:** original ИААА question ID, source file URL and SHA-256, media source
  URL and SHA-256.
* **No modification of wording.** Only Unicode NFC and whitespace normalisation are applied.
* **Images:** the original files are published unchanged (`images-original.zip`). The WebP files
  for the app (`images-webp.zip`) are format conversions of those originals, recorded as
  derivatives with their own checksums.
* **AvtoIzpit:** none of its content is redistributed. Raw samples stay out of git; only
  numeric summaries and question-level difference reports are published.
* **Takedown:** rights-holder requests via the issue template are honoured in the next release
  and logged in `CHANGELOG.md`.

## 5. Consumers

Anyone reusing the dataset must keep the attribution and make their own assessment of the
licensing situation described above.

## 6. Legal texts (corpus of the explanations)

_Recorded 2026-11-06._ The explanations quote the acts in `data/legal/`. Each one is stored with its
source URL and SHA-256 in `data/legal/sources.json`:

* the Закон за движението по пътищата;
* its Правилник;
* Наредба № РД-02-21-1/2023 on road signs;
* Наредба № 2/2001 on road markings.

* **ЗАПСП, чл. 4, т. 1:** normative acts of state bodies are not subject to copyright, so their text may
  be quoted and redistributed.
* **Sources:** only files published on government sites, namely the Ministry of Transport (the ЗДвП,
  consolidated to ДВ бр. 55/2026), the Ministry of the Interior (the Правилник) and the State Agency
  for Road Safety (the two ordinances).
  * Some of these files are exports of a commercial legal information system; their footer names it.
  * Only the wording of the acts is used: no annotations, case law or editorial content of that system.
* **Not used:** textbooks, driving-school material and other apps' explanations. They are protected
  works; explanations are written from the acts alone.
