# Explanations

The official question bank has no explanations (ИААА publishes none), so this repository adds **unofficial
explanations in Bulgarian** of why the correct answers are correct. Apps show them behind an (i) next to a question.

**The official question bank and the law prevail.** The explanations are a learning aid. They are written with AI
and reviewed as described below. They are not approved by ИААА.

## Where the explanations come from

No textbook or website can be used: they are protected works. The explanations are written from **the law
itself**:

* The legal corpus `data/legal/` holds the current text of four acts. Their text is not subject to copyright
  (ЗАПСП, чл. 4, т. 1); see `docs/licensing.md` §6.
  * the Закон за движението по пътищата;
  * its Правилник;
  * Наредба № РД-02-21-1/2023 on road signs;
  * Наредба № 2/2001 on road markings.
* Each act is split into articles, paragraphs, points and §.
* `data/legal/sources.json` records each act's file on a government site, its SHA-256 and the State Gazette issue
  it is consolidated to.

An explanation is either:
* **law:** it rests on provisions it quotes word for word, e.g. `чл. 50, ал. 1 ЗДвП`;
* **general:** technical or safety knowledge that no provision states (vehicle parts, first aid, physics). It has
  no quote.

## How they are made

1. **Work packages.** `qb explanations prepare --category B --out explanation-work/B` puts the category's
   questions not yet explained into parts of about 100, grouped by topic. Every question carries:
   * its answers with their letters and correct markers;
   * its content hash;
   * the paths of its pictures.
2. **Rules.** `data/explanations/style-guide.md` is binding:
   * Bulgarian, 1–4 sentences;
   * the rule behind every correct answer;
   * answers named by their words, never by letter;
   * quotes word for word;
   * nothing taken from textbooks, websites or apps;
   * a conflict instead of an explanation when the law seems to contradict the official answer.
3. **Writing.** One writer at a time works through a part. Provisions are found with
   `qb legal search --act zdvp <words>` and read with `qb legal show`. The pictures are opened one by one; for a
   video question the writer and the reviewer look at still frames of the clip (8 spread over it, one per second
   where needed) and name only what the frames clearly show.
4. **Checks.** `qb explanations lint --work <folder> --part N` checks:
   * coverage;
   * kind and length;
   * Bulgarian text;
   * every quote is word for word in the cited unit of the act;
   * no answer letters.
   A part is finished only with 0 errors.
5. **Independent review.** A second reviewer rereads every explanation against the question, its correct answers
   and the quoted provisions, and fixes errors. Changes are logged in `data/explanations/bg/review.json`.
6. **Merge.** `qb explanations merge --work <folder> --part N` refuses a part with errors or missing questions. It
   writes:
   * `data/explanations/bg/explanations.json`;
   * `conflicts.json`, the questions for the maintainer.

Category B comes first; the other categories follow. `qb explanations status` shows the coverage per category.

## In a release

`qb build` exports `explanation-bg.json` (`docs/data-contract.md` §5.5) and fills the explanation tables of
`master.sqlite`. It exports only the explanations whose `source_hash` equals the question's current `content_hash`,
and it checks every quote against the corpus again.
* A quote that is no longer in the act (the law changed) is an error and blocks the release.
* A changed question is left out until it is explained again.

`qb verify` in CI repeats the quote check on the curated file.

## Category B (dataset 1.2.0)

* **Coverage:** all 1,440 questions of category B: 1,433 explanations (1,304 `law`, 129 `general`) and 7
  conflicts. Many questions are shared, so other categories are covered too (e.g. A 1,263 of 1,284, AM 1,191 of
  1,203, ТТМ 912 of 959; `qb explanations status`).
* **Review:** 16 parts, each reviewed independently after the writer; every change is logged in
  `data/explanations/bg/review.json`. The reviews changed 7–20 % of each part, mostly legal references (a more
  specific provision, a fuller quote), picture readings and wording.
* **Video questions:** the clips end at the moment of decision, so for iaaa-12007, 12026, 12040, 12061 and 12067
  the frames don't show the reason for the official answer; their explanations state the rule only.

### Conflicts (no explanation exported)

The descriptions in `data/explanations/bg/conflicts.json` name each provision and the official answer.

| Questions | Official answer | The law (ЗДвП, ДВ бр. 55/2026) |
| --- | --- | --- |
| iaaa-6475, iaaa-6477 | a gap of „5 м“ / of two seconds when stopped in a tunnel over 500 m | the rule was чл. 63, т. 1, repealed by ДВ бр. 60/2012; no provision sets a tunnel gap |
| iaaa-6546, iaaa-6550, iaaa-6576 | at an unmarked junction the vehicle turning left goes first, or is let through by the oncoming driver | чл. 37, ал. 1: the driver turning left yields to oncoming vehicles; with чл. 48 the duties form a circle that no provision resolves |
| iaaa-11821 | „мотоциклети“ may not use the leftmost of three lanes | чл. 17 with the table of чл. 21, ал. 1: categories А and А2 have the same 90 km/h as В outside settlements, so only А1 is affected (the answer matches the outdated table of ППЗДвП чл. 73, ал. 1) |
| iaaa-11738 | over 50 km/h outside a settlement: deprived of the right to drive „когато нарушението е системно“ | чл. 182, ал. 2, т. 6: two months' deprivation for every such offence; repeated (ал. 4) and systematic (ал. 5) ones are punished more heavily |

In the junction questions the official answers follow one pattern: the vehicle whose right side is free goes
first and the right-hand rule prevails over the left-turn rule. No act states this.

### Where ППЗДвП is outdated

The explanations follow ЗДвП where the two differ:
* mopeds: up to 45 km/h (ЗДвП § 6, т. 14), not 50 km/h (ППЗДвП § 1, т. 27; the wrong answer of iaaa-11676);
* motorways: motor vehicles that can exceed 70 km/h (ЗДвП чл. 55, ал. 1), not „автомобили и мотоциклети“ over
  50 km/h (ППЗДвП чл. 116);
* overtaking in reduced visibility: banned when visibility is shorter than the overtaking needs (ЗДвП чл. 43,
  т. 1), not in any reduced visibility (ППЗДвП чл. 90, т. 1);
* children on the rear seat: no extra children allowed (ЗДвП чл. 133, ал. 1; ППЗДвП чл. 180, ал. 1 still allows
  them), and the front seat from 12 years (ЗДвП чл. 133, ал. 2; ППЗДвП чл. 180, ал. 2 says 10);
* towing: a red flag in at least two places (ЗДвП чл. 85, ал. 2; ППЗДвП чл. 150, ал. 2 says one), and the ban on
  towing motorcycles *with* a sidecar (ЗДвП чл. 87, т. 2; ППЗДвП чл. 154, т. 3 says *without*).

Also: ЗДвП чл. 171, т. 2, б. „а“ now stops a vehicle only for an „опасна неизправност“ (the answer of iaaa-8292
says „технически неизправно“), and the signs ordinance lists Ж17 without describing it (iaaa-6208).

### Corrections of the legal texts

The published files contain artefacts that the parser now removes or repairs:
* the print date of the PDF page headers ("19/04/2024 г.", "01/07/2024 г.") in ППЗДвП and the signs ordinance;
* comparatives that lost their hyphen ("поголяма") in ППЗДвП and the ordinances, or have a space after it
  ("по- малко") in ЗДвП;
* text struck down by the Constitutional Court, which the ЗДвП file keeps between lines of dashes: чл. 143, ал. 1,
  second sentence; чл. 159, ал. 2; чл. 171, т. 1, б. „д“ and т. 2, б. „к“; чл. 189, ал. 13 (no appeal of fines up
  to 50 лв.); the words "28 и" in чл. 189з; and the files' editor's notes.

## When the law changes

1. Download the new consolidated text from the government site.
2. Run `qb legal import --act <id> --file <file>` and update `later_amendments` in `sources.json`.
3. Run `qb explanations status`; it lists every quote that is no longer in the act. Those explanations go through
   a work package again (`--redo --only <ids>`).

## Reporting an error

Open an issue with the "Data issue" template. Include:
* the question number;
* what is wrong in the explanation;
* the provision, if you know it.
