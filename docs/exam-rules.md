# Official theory-exam rules

_Rules version **2024-12-12** (the date the current text of Наредба № 38 came into force).
Researched 2026-11-04. Every number below has a citation; nothing is assumed._

## 1. Sources

| Code | Document | Status |
|---|---|---|
| **N38** | Наредба № 38 от 16.04.2004 г. — consolidated text through ДВ бр. 77/10.09.2024, in force 12.12.2024 (IISDA copy: https://iisda.government.bg/no_frame/adm_services/service_regulatory_file/52977_242985) | in force; no later amendment found in the consolidated text |
| **MET** | ИААА "Методика за провеждане на изпитите…" (https://rta.government.bg/upload/13306/Metodika_izpiti.pdf, uploaded 2024-10-31) | marked **"Проект!"** (draft; approving order number left blank) |
| **OBS** | ИААА's own online simulator avtoizpit.com — 2 test sets per variant sampled 2026-11-04 (`reports/investigation/avtoizpit-sample-summary.json`) | observation |

Extracted evidence: `reports/investigation/methodology-2024-tables.json` (quota tables) and the
AvtoIzpit sample summary.

## 2. Rules that apply to every test

* Tests contain text questions, questions with static images and interactive video clips; they
  are solved on an electronic device and scored automatically; each candidate's test is individual
  and covers only the topics of the category — **N38 чл. 38, ал. 3**.
* Each question has 2, 3 or 4 answers, of which 1, 2 or 3 are correct. **A question counts as
  answered correctly only if all correct answers and none of the wrong ones are marked.** The test
  shows, for every question, **how many answers are correct and how many points (1, 2 or 3) it is
  worth** — **MET т. 1.4**.
* Where the category has approved video questions, **every test contains exactly two** —
  **MET т. 1.5**; confirmed by OBS for A, AM, B and Ттм.
* One question per page, plus a thumbnail overview of all questions of the test — **MET т. 3**.
* A video can be played at most **3 times**; when the time runs out the test is submitted
  automatically — **OBS** (simulator client: `MAX_VIDEO_PLAY_COUNT = 3`, auto-submit on expiry).
  These two are simulator behaviour, not law.
* The total points of a test equal the stated maximum (every OBS sample), and the **mix of 1-,
  2- and 3-point questions is fixed per variant** (both OBS samples of every variant identical).

## 3. Parameters per official variant

Q = questions, Max = maximum points, Pass = minimum points to pass, Min = minutes, Mix = number of
1/2/3-point questions observed, V = video questions.

| # | Variant | Q | Max | Pass | Min | N38 | MET (quota table) | OBS | Mix | V |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A — без правоспособност / с АМ | 40 | 90 | 81 | 40 | чл. 39 ал. 3, 10 | 2.2.2–2.2.3 (Т3) | ✔ | 8/14/18 | 2 |
| 2 | A — загуба по чл. 157, ал. 4 | 40 | 90 | 81 ¹ | 40 | чл. 39 ал. 3, 10 | 2.2.7 (Т6) | ✔ | 9/12/19 | 2 |
| 3 | A — притежаващ Ткт или Ттм | 15 | 31 | 27 | 20 | чл. 39 ал. 4, 10 | 2.2.5–2.2.6 (Т5) | ✔ | 4/6/5 | 2 |
| 4 | A — притежаващ В1 или В | 15 | 31 | 27 | 20 | чл. 39 ал. 4, 10 | 2.2.5–2.2.6 (Т4) | ✔ | 0/14/1 | 0 |
| 5 | AM — без правоспособност | 37 | 84 | 75 | 40 | чл. 39 ал. 8, 10 | 2.1.2–2.1.3 (Т1) | ✔ | 7/13/17 | 2 |
| 6 | AM — загуба по чл. 157, ал. 4 | 37 | 84 | 75 ¹ | 40 | чл. 39 ал. 8, 10 | 2.1.4 (Т2) | ✔ | 10/7/20 | 2 |
| 7 | B — без правоспособност / с АМ | 45 | 97 | 87 | 40 | чл. 39 ал. 1, 10 | 2.3.2–2.3.3 (Т7) | ✔ | 12/14/19 | 2 |
| 8 | B — загуба по чл. 157 | 45 | 97 | 87 ¹ | 40 | чл. 39 ал. 1, 10 | 2.3.8 (Т9) | ✔ | 9/20/16 | 2 |
| 9 | B — с А, А1 или А2 | 25 | 55 | 50 | 35 | чл. 39 ал. 2, 10 | 2.3.5–2.3.7 (Т8) | ✔ | 8/4/13 | 2 |
| 10 | B — притежаващ В1 | 45 | 97 | 87 | 40 | чл. 39 ал. 1, 10 | 2.3.4 (Т7) | ✔ | 12/14/19 | 2 |
| 11 | C — с В/B(78) | 30 | 66 | 57 | 30 | чл. 40 ал. 1–3 | 2.6.2–2.6.3 (Т16) | ✔ | 2/20/8 | 0 |
| 12 | C+E — с D1E | 15 | 29 | 26 | 20 | чл. 41 ал. 1 т. 6, ал. 2 | 2.8.8–2.8.10 (Т20) | ✔ | 1/14/0 | 0 |
| 13 | C1 — с В | 15 | 35 | 30 | 20 | чл. 41 ал. 1 т. 2, ал. 2 | 2.6.6–2.6.7 (Т17 ²) | ✔ | 2/6/7 | 0 |
| 14 | C1+E — с D1E | 15 | 29 | 26 | 20 | чл. 41 ал. 1 т. 5, ал. 2 | 2.8.5–2.8.7 (Т20) | — ³ | — | 0 |
| 15 | C+E — с С | 15 | 29 | 26 | 20 | чл. 41 ал. 1 т. 4, ал. 2 | 2.8.2–2.8.3 (Т19) | ✔ | 4/8/3 | 0 |
| 16 | C+E — загуба по чл. 157, ал. 4 | 15 | 29 | 26 ¹ | 20 | чл. 41 ал. 1 т. 4, ал. 2 | 2.8.4 (Т19) | ✔ | 4/8/3 | 0 |
| 17 | D — с С1/С и В, стаж 2 г. ⁴ | 15 | 32 | 28 | 20 | чл. 41 ал. 1 т. 3, ал. 2 | 2.7.2–2.7.3 (Т18) | ✔ | 4/5/6 | 0 |
| 18 | D — загуба по чл. 157, ал. 4 и УПК | 15 | 32 | 28 ¹ | 20 | чл. 41 ал. 1 т. 3, ал. 2 | 2.7.4 (Т18) | ✔ | 4/5/6 | 0 |
| 19 | D (103) — тролейбус | 15 | 32 | 28 | 20 | чл. 41 ал. 4 | 2.10.2–2.10.3 (Т22) | ✔ | 5/3/7 | 0 |
| 20 | D+E — с D | 15 | 29 | 26 | 20 | чл. 41 ал. 1 т. 4, ал. 2 | 2.9.2–2.9.3 (Т21) | ✔ | 4/8/3 | 0 |
| 21 | Ттм — без правоспособност / с АМ | 37 | 84 | 75 | 40 | чл. 39 ал. 8, 10 | 2.5.2–2.5.3 (Т13) | ✔ | 7/13/17 | 2 |
| 22 | Ттм — загуба по чл. 157, ал. 4 | 37 | 84 | 75 ¹ | 40 | чл. 39 ал. 8, 10 | 2.5.7 (Т15) | ✔ | 6/15/16 | 2 |
| 23 | Ттм — притежаващ А…В(78) | 15 | 31 | 27 | 20 | чл. 39 ал. 9, 10 | 2.5.5–2.5.6 (Т14) | ✔ | 2/10/3 | 0 |

"✔" in OBS means: question count, total points and duration observed in the simulator equal the
values in the table.

1. **Loss-of-licence variants.** N38 and MET define the composition of these tests (MET tables)
   but state no separate pass mark. The count, maximum and duration observed in the simulator equal
   the category's; the pass mark is therefore taken from the category rule and flagged
   `pass_points_basis = "category-rule"` in the configuration. An unanswered assessment cannot
   reveal a threshold, so this was not observed.
2. **Таблица 17 is internally inconsistent** in the draft (sections 1+9+1+1+1+1 = 14, stated total
   15). The section quotas for C1 are taken from the simulator observation once the samples are
   mapped to sections (Phase 4); the total of 15 is confirmed by N38 and OBS.
3. AvtoIzpit has no C1+E sub-category. Count, maximum, pass mark and duration come from N38 only,
   the section quotas from MET Т20; the points mix is unknown, so the generator only enforces the
   total of 29 points.
4. The official file name says "(След 07.02.26г.)". The consolidated N38 contains no 2026
   amendment and the simulator shows the unchanged 15/32/20 parameters; the date presumably refers
   to the candidates' eligibility, which does not affect the test.

## 4. Per-section quotas (MET)

| Table | Variant(s) | Quotas (section: questions) | Total |
|---|---|---|---|
| Т1 | AM | 1:1 · 2:5 · 3:5 · 4:20 · 5:3 · 6:3 | 37 |
| Т2 | AM загуба | 3:7 · 4:24 · 5:3 · 6:3 | 37 |
| Т3 | A | 1:1 · 2:5 · 3:5 · 4:23 · 5:3 · 6:3 | 40 |
| Т4 | A притежаващ В1/В | 1:15 | 15 |
| Т5 | A притежаващ Ткт/Ттм | 1:3 · 4:11 · 6:1 | 15 |
| Т6 | A загуба | 3:6 · 4:26 · 5:4 · 6:4 | 40 |
| Т7 | B, B притежаващ В1 | 1:1 · 2:5 · 3:8 · 4:25 · 5:3 · 6:3 | 45 |
| Т8 | B с А/А1/А2 | 1:4 · 4:16 · 6:5 | 25 |
| Т9 | B загуба | 3:16 · 4:23 · 5:3 · 6:3 | 45 |
| Т13 | Ттм | 1:1 · 2:1 · 3:5 · 4:7 · 5:18 · 6:2 · 7:3 | 37 |
| Т14 | Ттм притежаващ | 1:5 · 2:10 | 15 |
| Т15 | Ттм загуба | 4:10 · 5:19 · 6:3 · 7:5 | 37 |
| Т16 | C | 1:2 · 2:13 · 3:10 · 4:2 · 5:2 · 6:1 | 30 |
| Т17 | C1 | 1:1 · 2:9 · 3:1 · 4:1 · 5:1 · 6:1 (= 14, see note 2) | 15 |
| Т18 | D, D загуба | 1:2 · 2:4 · 3:3 · 4:3 · 5:2 · 6:1 | 15 |
| Т19 | C+E, C+E загуба | 1:2 · 2:2 · 3:4 · 4:3 · 5:4 | 15 |
| Т20 | C1+E / C+E с D1E | 3:6 · 4:9 | 15 |
| Т21 | D+E | 1:2 · 2:2 · 3:4 · 4:3 · 5:4 | 15 |
| Т22 | D (103) | 1:3 · 2:3 · 3:5 · 4:4 | 15 |

Т10–Т12 (Ткт) have no official question file and are not used. The sections listed in each table
are exactly the sections present in the corresponding official file.

## 5. How the rules become data

`data/exam-rules/exam-configs.source.json` holds one entry per variant with: question count, max
points, pass points, duration, section quotas, points mix (when observed), video questions, video
play limit, scoring (`all_or_nothing`), and an `evidence` block citing the documents above, plus a
`verification` block that states for every parameter whether it comes from N38, MET or OBS. The
pipeline checks that every configuration is **feasible** with the published questions (enough
questions per section, points mix and video count reachable) and fails the build otherwise.
Variants whose parameters are not fully sourced are published with `status = "unofficial"`;
the Android app then offers only a clearly labelled practice test for them.
