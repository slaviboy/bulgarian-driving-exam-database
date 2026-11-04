# Source investigation report

_Investigation date: 2026-11-04. Edition found: **2026-10-01**. All numbers below were measured,
not assumed; the evidence files are in `reports/investigation/`._

| | Official array (ИААА) | AvtoIzpit |
|---|---|---|
| URL | https://public-eis.rta.government.bg/exam-questions/ | https://avtoizpit.com/listovki#/sub-categories |
| Operator | Изпълнителна агенция „Автомобилна администрация“ | ИААА (signs the site's privacy notice) |
| Kind | Static files (Apache) | Knockout.js single-page app + JSON API (Cloudflare) |
| Authentication | None | None for the endpoints below |
| Full question bank | **Yes** — every question with correct answers marked | No — random test sets only; correct answers only after an assessment |
| Used for the dataset | **Yes (only source)** | No — comparison and exam-rule evidence only |

## 1. Official array

### 1.1 Discovery

`index.html` contains no data. Its inline script fetches `manifest.txt` and lists one link per
line (confirmed by the Playwright capture: the page makes exactly two requests, the document and
`manifest.txt`). `manifest.txt` lists **23 HTML files**, one per exam variant, each in its own
directory together with an `assets/` folder:

```
7_B_без_правоспособност_или_с_правоспособност_за_категория_АМ_01.10.2026/7_B_…_01.10.2026.html
```

File-name parts: order number, category token, description, edition date. The authoritative
category and description are taken from the file's `<h1>`, e.g.
`B. без правоспособност или с правоспособност за категория АМ (След 12.12.24г.)`.

| # | Category | Variant (candidate situation) |
|---|---|---|
| 1–4 | A | без правоспособност / с АМ · загуба по чл. 157, ал. 4 ЗДвП · притежаващ Ткт или Ттм · притежаващ В1 или В |
| 5–6 | AM | без правоспособност · загуба по чл. 157, ал. 4 ЗДвП |
| 7–10 | B | без правоспособност / с АМ · загуба по чл. 157 ЗДвП · с А, А1 или А2 · притежаващ В1 |
| 11 | C | с правоспособност за В/B(78) |
| 12, 15, 16 | C+E | с D1E · с С · загуба по чл. 157, ал. 4 ЗДвП |
| 13 | C1 | с правоспособност за В |
| 14 | C1+E | с правоспособност за D1E |
| 17–18 | D | с С1/С и В със стаж 2 г. (След 07.02.26г.) · загуба по чл. 157, ал. 4 ЗДвП и УПК |
| 19 | D (103) | тролейбус, с правоспособност за D |
| 20 | D+E | с правоспособност за D |
| 21–23 | Ттм | без правоспособност / с АМ · загуба по чл. 157, ал. 4 ЗДвП · притежаващ А…В(78) |

### 1.2 HTML structure

```
h1.text-category                          "<category>. <description> (След …)"
p.sectionTitle                            "Раздел N. <TITLE>"
table.tg.question#q<ID>                   one question
  td (1st)  > b                           original ИААА ID
  td (2nd)  > var                         points (1, 2 or 3)
  th.p-b-14 > b                           question text
  i.check / i.check.correct               answer marker (correct answers carry .correct)
  var.f-13                                text answer
  th.qpictureWrp.small > div.qpicture     picture answer: style="background-image: url(./assets/N.png)"
  td.qpictureWrp.w-30 > div.qpicture      question picture
  video > source[src=./assets/N_video.mp4] question video
```

Four question formats occur: text answers; picture answers; a question picture with text answers;
a question video with text answers.

### 1.3 Measured content (edition 2026-10-01)

* **13,763** question rows in the 23 files; **2,476** unique question IDs.
* 2–4 answers per question, 1–3 of them correct; **no question without a correct answer**.
  Multi-correct questions are common (e.g. B: 342 with two and 182 with three correct answers).
* Sections: 1–7 per file, **36 distinct section titles** (titles depend on the vehicle type,
  e.g. "ОБЩИ СВЕДЕНИЯ ЗА МОТОЦИКЛЕТА" / "…ЗА МОТОПЕДА").
* For the 2,426 IDs that occur in several files, **text, answers, correct markers and media are
  identical everywhere**, but **points differ for 1,211 IDs and the section differs for 1,041
  IDs**. Points and section are therefore properties of the (variant, question) pair.
* Media: **925 PNG images (239.0 MB, median 55 KB, max 0.82 MB)** and **57 MP4 videos (350.2 MB,
  max 8.4 MB)**. Every asset answered HTTP 200. Assets with the same name in different
  directories were byte-identical in every sample checked; the pipeline still deduplicates by
  SHA-256 because video names (`5_video.mp4`) are not guaranteed to be global.
* No explanations or commentary exist in the source.

### 1.4 HTTP behaviour

* No `robots.txt` (404). Static files carry `ETag` and `Last-Modified` (files of this edition:
  2026-09-30) and `Accept-Ranges: bytes`; the pipeline uses conditional and resumable requests.
* The largest HTML file (B) is 6.2 MB; downloading all 23 files takes well under a minute at one
  request per second.

## 2. AvtoIzpit

### 2.1 Endpoints actually used by the page

Read from `js/dist/avtoizpit-test.min.js` and confirmed by the Playwright capture
(`reports/investigation/network-capture.json`):

| Method | Path | Purpose | Used by this project |
|---|---|---|---|
| GET | `api/sub-categories` | categories with learning plans | yes (`qb avtoizpit metadata`) |
| GET | `i18n/test/bg.json`, `views/test/*.html` | UI texts and templates | no |
| POST | `api/test-sets` `{subCategoryId, learningPlanId, languageId}` | new random test set | yes, opt-in sample |
| POST | `api/test-sets/{id}/assessment` `{questions:[{id, answers:[{id, checked}]}]}` | score it, reveal correct answers | yes, opt-in sample |
| GET | `api/test-sets/{id}` | reload own test set | no |
| GET | `api/pictures/{id}.png?quality=`, `api/videos/video{id}.mp4` | media | no |
| GET | `api/vouchers/{n}/test-set` | **a candidate's personal exam review** | **never** |

A test set contains question `id`, `text`, `pictureId`, `videoFileId`, `points`,
`correctAnswersCount` and answers (`id`, `text`, `pictureId`) in shuffled order, plus
`subCategory.examDurationMinutes`. Correct answers appear only in the assessment response. The
client plays a video at most `MAX_VIDEO_PLAY_COUNT = 3` times and submits automatically when the
timer reaches zero. `languageId` 2 serves English texts (not collected).

### 2.2 Coverage compared with the official array

* 22 of the 23 official variants have a matching learning plan
  (`reports/investigation/avtoizpit-plan-matches.json`); **C1+E (#14) has no AvtoIzpit
  sub-category**.
* AvtoIzpit offers plans with no official file (A1, A2, B1, D1, Ткт, Ттб, "държавна поръчка",
  чл. 162, чл. 426 НК, ADR). They are not part of the dataset because the official array does not
  publish separate files for them.

### 2.3 Sample taken

With the maintainer's approval, `qb avtoizpit sample --per-plan 2 --assess` generated **2 test
sets per matched variant (44 sets)** on 2026-11-04, each submitted unanswered — about 90 requests,
never faster than one every 2 seconds. Numbers-only results:
`reports/investigation/avtoizpit-sample-summary.json`. Findings:

* Every test set has exactly the question count and total points of the law (see
  `docs/exam-rules.md`), and `examDurationMinutes` equals the legal duration.
* The **mix of 1-, 2- and 3-point questions is fixed per variant** (identical in both samples,
  e.g. B: 12 × 1 + 14 × 2 + 19 × 3 = 97).
* Test sets of categories A, AM, B and Ттм contain **exactly 2 video questions** (all their
  variants except A #4 and Ттм #23, which have none); C, C1, C+E, D, D (103) and D+E have none.

Section-level comparison and the question-by-question source comparison are produced in Phase 4
(`reports/source-comparison.{json,md}`, `reports/exam-rules-evidence.json`).

## 3. Limitations and inaccessible data

* Neither source publishes a licence (see `docs/licensing.md`).
* The official array has no explanations, no category descriptions and no English version.
* AvtoIzpit cannot be used to obtain the full bank without generating thousands of test sets; this
  project does not attempt it.
* Nothing behind authentication, CAPTCHAs or personal identifiers was accessed.

## 4. Reproduce

```
qb discover                      # official manifest → data/cache/official-manifest.json
qb capture                       # Playwright network capture (needs the browser extra)
qb avtoizpit metadata            # sub-categories + plan matching
qb avtoizpit sample --per-plan 2 --assess   # opt-in, rate-limited
qb avtoizpit summarize
qb rules methodology             # quota tables from the methodology PDF (dev extra)
```
