# Data notice — origin, attribution and redistribution status

## Where the question content comes from

All examination question content in this project's dataset releases — question
text, answer options, correct-answer markings, images and videos — is extracted
without modification of wording from the official question array published by:

> **Изпълнителна агенция „Автомобилна администрация“ (ИААА)**
> Executive Agency "Automobile Administration", Ministry of Transport and Communications, Bulgaria
> "Масив от изпитни въпроси за изготвяне на тестове за провеждане на теоретичните изпити за различните категории"
> https://public-eis.rta.government.bg/exam-questions/

Under Наредба № 38 от 16.04.2004 г., чл. 38, ал. 1, the exam questions are approved
by the Executive Director of ИААА. Every record in the dataset keeps its original
ИААА question ID, the URL of the official file it came from and that file's SHA-256.

**Attribution required for every reuse:** "Източник: Изпълнителна агенция
„Автомобилна администрация“ — https://public-eis.rta.government.bg/exam-questions/".

## Licence status — read before reusing

* ИААА publishes the array publicly but **does not attach any licence** to it.
  The source pages carry only the notice "© 2022-2026 Всички права запазени".
* No open-data release of the array exists on the national portal data.egov.bg
  (checked 2026-11-04).
* Bulgarian copyright law (ЗАПСП, чл. 4, т. 1) excludes normative and individual
  acts of state bodies from copyright protection. Whether this exemption covers
  the question array — and in particular its photographs and videos — has not
  been confirmed by ИААА or a court.
* The maintainer of this repository has **decided to republish the content with
  attribution**, accepting the legal uncertainty. This decision is recorded here
  and in every dataset manifest (`licensing.redistribution_status =
  "published_by_maintainer_decision"`). It is not a licence grant: **no licence
  of any kind is granted by this project for the question content**.
* The MIT licence in `LICENSE` applies only to the code, schemas and
  documentation written for this repository.

## Translations

The dataset also contains **unofficial translations** of the questions, the answers and their labels into nine
languages (`translation-<lang>.json`, see docs/translations.md):
* they were made with AI from the Bulgarian original and checked automatically and by an independent AI review;
* they are not approved by ИААА and may contain errors;
* **the Bulgarian original prevails.**

As derivative works of the same content, they have the same redistribution status: published by the maintainer's
decision, with no licence granted.

## Processed pictures (from dataset v1.3.0)

The official pictures carry a tiled, semi-transparent "ИААА" stamp and are small (scenes 712 × 394 px, signs about
150 px). From dataset v1.3.0 the **WebP pictures for apps** (`images-webp`) are processed, and road signs and
vehicle markings also come as **vector drawings** (`images-svg`); see docs/media-enhance.md:

* **Stamp removed** — the stamp was measured exactly from the pictures and its alpha compositing inverted; every
  pixel the stamp does not touch is unchanged. The maintainer decided to remove it (recorded 2026-11-11) and
  keeps the attribution to ИААА above in every release; the **original pictures, stamp included, stay published
  unchanged** in `images-original.zip`.
* **Enlarged** — scenes and photos were enlarged 2–4× with Real-ESRGAN (x4plus); an automatic check rejects any
  enlargement that changes the picture's structure (labels, arrows, numbers), and flagged ones were reviewed.
* **Signs as vectors** — each sign picture was matched by hand to a drawing of the same sign; signs that have no
  drawing (old or special signs, plates, vehicle markings) were traced from the stamp-free picture or drawn
  for this project. Every derivative records how it was made (`process`).

### Road-sign drawings from Wikimedia Commons

Most sign drawings are files from Wikimedia Commons ("BG road sign …", "Bulgaria road sign …"), used under their
own licences: 130 files in media revision r2, **CC BY-SA 4.0** (90) or **CC0** (40).
Each picture lists the drawings it uses, with author, licence and file page, in its `credits` (questions.json,
`media_credits` in master.sqlite). Pictures that contain a CC BY-SA drawing are adaptations of it and are shared
under the same licence; reusers must keep the credits.

## Not affiliated

This project is independent and is **not affiliated with, endorsed by or
connected to ИААА** or any other Bulgarian authority. The official source always
prevails; if you find a discrepancy, the official array is authoritative.

## Takedown / rights-holder requests

If you hold rights in any of the published content and want it removed or
attributed differently, open an issue using the "Rights holder / takedown
request" template, or contact the maintainer through the GitHub profile
https://github.com/slaviboy. Affected material will be withdrawn from future
releases and the request will be documented in `CHANGELOG.md`.

---

**Накратко (BG):** Въпросите, отговорите, изображенията и видеоклиповете са от
официалния масив на ИААА (public-eis.rta.government.bg) и се публикуват тук с
посочване на източника, без лиценз от ИААА и по решение на поддържащия проекта.
От версия 1.3.0 картинките за приложения са без воден знак „ИААА“ и уголемени, а
пътните знаци са векторни рисунки (главно от Wikimedia Commons, с посочени автори и
лицензи); оригиналите остават публикувани без промяна. Проектът не е свързан с ИААА.
Притежатели на права могат да поискат премахване чрез GitHub issue.
