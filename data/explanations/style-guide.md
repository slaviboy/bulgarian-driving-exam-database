# Style guide — explanations (Bulgarian)

Binding for every writer and reviewer of `data/explanations/bg/`. An explanation appears behind the (i) button
next to a question in the app. It tells a learner **why the correct answer is correct**.

## 1. Sources: the law and your own words only

* Base every rule on the legal corpus in `data/legal/`:
  * `zdvp`: ЗДвП;
  * `ppzdvp`: ППЗДвП;
  * `signs`: Наредба № РД-02-21-1/2023 for road signs;
  * `marking`: Наредба № 2/2001 for road markings.
  * Find provisions with `qb legal search --act zdvp <words>` and read them with
    `qb legal show --act zdvp "чл. 50, ал. 1"`.
* **Never** use or paraphrase textbooks, driving-school material, websites, forums or other apps. They are
  protected works. Write every sentence yourself.
* Never change, doubt or "correct" the official answer. If the cited law seems to say something else, write
  a conflict instead of an explanation (§ 6).

## 2. Kinds

| `kind` | When | References |
|---|---|---|
| `law` | A provision of the corpus states the rule the answer rests on. | 1–4. Each one has the unit and a word-for-word quote. |
| `general` | Vehicle technology, physics, first aid, driver behaviour, loads: knowledge that no provision states. | None. |

Prefer `law` whenever a provision fits, including definitions (`§ 6` of ЗДвП) and the descriptions of signs
and markings.

## 3. The text

* **Bulgarian**, plain and precise, in the terminology of ЗДвП: пътно превозно средство, платно за
  движение, лента за движение, кръстовище, водач, пешеходец, пътен знак, пътна маркировка.
  * Formal and impersonal ("водачът е длъжен…", "трябва да се…"). Never use "ти".
* **1–4 sentences, 80–900 characters.** Most explanations need 150–450.
* Explain the **rule behind the correct answer**. If there are several correct answers, cover each of them.
  When it helps, say in one short clause why the most tempting wrong answer is wrong.
* Refer to answers **by their words in „…“**, never by letter.
  * Right: "Верен е отговорът „да пропусне пешеходците“."
  * Wrong: "Верен е отговор „б“." The letters are a display detail.
* **Pictures and videos** (paths are in the work package): look at them. Name what matters in one clause:
  "На снимката автомобилът е на път без предимство…". For a video question, describe the situation from the
  question and the answers; never claim details you cannot see.
* **Signs:** use the code and name from the signs ordinance, e.g. знак Б2 „Спри! Пропусни движещите се по
  пътя с предимство!“, and cite the article that gives its meaning.
* **Numbers** (speeds, distances, masses, times) only as the corpus or the question states them. Never
  invent a value.
* **Do not repeat the question.** No markdown, no lists, no emojis. Do not address the reader as "вие" more
  than needed.

## 4. References (kind `law`)

```json
{"act": "zdvp", "unit": "чл. 50, ал. 1", "quote": "водачите на пътни превозни средства от другите пътища са длъжни да пропуснат"}
```

* **`unit`**: the most specific unit, in exactly this form:
  * `чл. N`, `чл. N, ал. M`, `чл. N, ал. M, т. K`;
  * `§ N` or `§ N, т. K`.
  * Letters belong to the number: `чл. 80а`, `ал. 2а`.
* **`quote`**: 3–70 words, copied **word for word** from that unit. Leave out the part numbers. Cut at word
  boundaries, never mid-word. The quote must show the rule the explanation states, not just be on the same
  topic.
* The build checks every quote against the corpus. A quote that is not in the unit is an error and blocks
  the release.

## 5. Examples

**Law** (question: "Водач, който навлиза в кръстовище от път без предимство, е длъжен:"):

```json
{"kind": "law",
 "text": "Когато единият от пътищата на кръстовището е сигнализиран като път с предимство, водачите от другите пътища трябва да пропуснат движещите се по него пътни превозни средства. Затова верен е отговорът „да пропусне пътните превозни средства, движещи се по пътя с предимство“.",
 "references": [{"act": "zdvp", "unit": "чл. 50, ал. 1", "quote": "водачите на пътни превозни средства от другите пътища са длъжни да пропуснат пътните превозни средства, които се движат по пътя с предимство"}]}
```

**General** (question: "Съединителят е предназначен:"):

```json
{"kind": "general",
 "text": "Съединителят свързва и разделя двигателя и предавателната кутия. Когато педалът му е натиснат, силовата връзка се прекъсва и предавките могат да се сменят плавно, без удари в трансмисията. Затова верен е отговорът „да прекъсва силовата връзка между двигателя и предавателната кутия“."}
```

## 6. Conflicts

If the current text of the law seems to contradict the official correct answer (for example, the rule changed
after the question was written), do **not** explain it. Write instead:

```json
{"conflict": "чл. N, ал. M ЗДвП (ред. ДВ бр. 55/2026) изисква X, а официалният верен отговор е Y."}
```

The maintainer decides. Such questions are listed in `conflicts.json` and get no (i) in the app.

## 7. Checks

`qb explanations lint --work <folder> --part N` must report **0 errors** before a part is finished. Warnings
need a look:
* a letter reference;
* Latin words;
* a unit that is not split, where the quote was found in the enclosing unit.
