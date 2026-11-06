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
   `qb legal search --act zdvp <words>` and read with `qb legal show`.
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
