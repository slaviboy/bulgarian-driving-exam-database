# Translation style guide — Bulgarian driving-theory question bank

Applies to every language. It is written for translators (human or AI) of the official ИААА question bank
and of the app's interface. Bulgarian is the source and stays authoritative: translations are an unofficial
learning aid that learners read next to the Bulgarian original and switch to when they do not understand it.

**Accuracy beats style.** A translation that reads well but shifts the meaning teaches the wrong rule and
can make a correct answer wrong. When fluency and precision conflict, choose precision.

## 1. Meaning — the non-negotiable rules

1. **Translate from Bulgarian.** Every element of meaning survives:
   * who and what (subject, object, vehicle type);
   * conditions: когато, ако, при, в случай че;
   * exceptions: освен, с изключение на;
   * negations: не, никога, без, нито;
   * quantifiers: всички, само, поне, най-малко, не повече от, над, до, между;
   * time and place: преди, след, в населено място, извън населено място.
2. **Modality is legal content.** Keep each degree distinct and use your language's usual legal forms for it:

   | Bulgarian | Meaning |
   |---|---|
   | длъжен е, трябва, задължително | must / is obliged |
   | може, има право | may / is entitled |
   | разрешено е | is permitted |
   | забранено е, не се разрешава | is prohibited |
   | препоръчително е | is advisable |

3. **Comparisons and limits stay exact.**
   * "над 3,5 т" means more than 3.5 t.
   * "не повече от" means not more than.
   * "до" means up to and including.
   * "най-малко" means at least.
4. **Nothing is added, removed, explained or corrected.**
   * Do not add examples, explanations or the reason for a rule.
   * Do not resolve an ambiguity the Bulgarian keeps.
   * If the Bulgarian looks wrong or has a typo, translate its intended meaning and write the case in `notes.md`.
5. **Every answer stays exactly as right or as wrong as in Bulgarian.**
   * The `correct` flags let you check that the translation preserves this. Read the question with each answer and
     ask: "is this still the correct/incorrect answer under my wording?"
   * Never use the flags to "improve" an answer.
6. **No hints.**
   * Keep the answers parallel in length, precision, register and grammar.
   * Do not make the correct answer more natural, more official or more complete than the wrong ones.
   * Do not repeat a word of the question only in the correct answer, unless the Bulgarian does.
   * Do not make wrong answers obviously absurd if the Bulgarian ones are plausible.
7. **Two different Bulgarian answers must never become the same translation**, and identical Bulgarian text in
   the same context must get the identical translation (`same_text` lists the other questions with the same text).

## 2. Structure

* **A stem that ends with ":"** is completed by each answer.
  * Keep the ":".
  * Translate each answer so that *stem + answer* is one grammatical sentence (agreement, case, prepositions, articles).
  * Start such answers in lower case unless your language requires a capital (German nouns, names, abbreviations).
* **A stem that ends with "?"** stays a question.
  * Greek ends questions with ";".
  * Spanish opens them with "¿".
  * French puts a no-break space (U+00A0) before ? : ; ! and inside « ».
* **Statements** (true/false items) stay statements.
* **Common yes/no-type answers** are translated consistently, e.g. да/не, правилно/неправилно, разрешено/забранено,
  вярно/невярно. Keep the Bulgarian lower case unless your language capitalises.
* **Keep the question and answer IDs and their order.** Never merge or split answers. Picture-only answers have no
  text and get no translation.
* **Punctuation inside the text** follows your language's norms. Quotation marks are your language's:

  | Language | Quotation marks |
  |---|---|
  | en | “ ” |
  | de | „ “ |
  | fr | « » (with U+00A0) |
  | es | « » |
  | pt | « » |
  | ru | « » |
  | el | « » |
  | tr | “ ” |
  | ro | „ ” |
  | hi | “ ” |

## 3. Terminology

* Use the **official road-traffic terminology of your language**. References, in order:
  1. the EU texts in your language: Directive 2006/126/EC on driving licences, Regulation (EC) No 561/2006 on driving
     times, Directive 2003/59/EC, ADR;
  2. the official text of the 1968 Vienna Convention on Road Traffic (official in EN, FR, RU, ES; national
     translations exist for the others);
  3. your country's traffic code and theory-test materials:

  | Language | National traffic code |
  |---|---|
  | de | StVO / FeV |
  | fr | Code de la route |
  | es | Reglamento General de Circulación / DGT |
  | pt | Código da Estrada / IMT |
  | el | ΚΟΚ |
  | ro | Codul rutier, OUG 195/2002 |
  | tr | 2918 Karayolları Trafik Kanunu |
  | ru | ПДД and the Vienna Convention RU text |
  | hi | Motor Vehicles Act 1988, Hindi version (मोटर यान अधिनियम) |
  | en | EU and UK usage (Highway Code), British spelling |

* **Build your glossary before translating, then follow it.** One Bulgarian term maps to one target term everywhere.
  `glossary-pivot.md` defines the Bulgarian terms, with an English pivot. The pivot is for understanding; translate
  the Bulgarian concept into your language's legal term, not the English word.
* **Keep the distinctions Bulgarian law makes**:

  | Bulgarian | Meaning |
  |---|---|
  | изпреварване | overtaking a vehicle moving the same way |
  | заобикаляне | going around a stationary vehicle or an obstacle |
  | разминаване | passing a vehicle coming the other way |
  | спиране | stopping in general |
  | престой | stopping for the time needed to let people on or off, or to load or unload |
  | паркиране | any other stopping |
  | ППС | road vehicle (any vehicle) |
  | МПС | motor vehicle (excludes mopeds) |
  | автомобил | a motor vehicle with ≥ 4 wheels |
  | платно за движение | carriageway |
  | пътна лента | traffic lane |
  | банкет | shoulder |
  | лента за принудително спиране | emergency lane |
  | прекъсване | break (in driving) |
  | почивка | rest period |

## 4. Codes, names and labels

* **Licence categories** are the official Latin codes everywhere: AM, A1, A2, A, B1, B, BE, C1, C1E, C, CE, D1, D1E,
  D, DE.
  * Bulgarian often writes them with Cyrillic look-alike letters: "категория В" is **B** (not V), "С" is C,
    "ВЕ" is BE, "АМ" is AM.
  * Never transliterate them. Russian uses the Latin codes too.
* **National categories** are Ткт (tractors), Ттб (trolleybuses) and Ттм (trams).
  * Russian keeps the Cyrillic form.
  * All other languages write Tkt, Ttb, Ttm.
* **Bus classes:** "клас А/В" is class A/B (Latin). Roman numerals I, II, III stay.
* **Picture labels:** a letter that marks something in a picture (e.g. „А") is written with the visually identical
  letter of your script, so it matches the picture: Latin A, Greek Α, Cyrillic А in Russian. A letter with no
  visually identical letter in your script (б, в, г …) stays in Cyrillic exactly as printed (iaaa-5295, 5296: «б»,
  «в»). Never transliterate it or replace it by its position (b/v, b/c): the reader could not find it in the picture.
* **Latin acronyms** stay exactly as written: ABS, ESP, ASR, BUS (the word painted on the lane), IRU, LED, ADR, CMR,
  TIR.
* **Bulgarian abbreviations** become your language's full term or its standard abbreviation. Decide once, in your
  glossary:

  | Abbreviation | Meaning |
  |---|---|
  | МПС | motor vehicle |
  | ППС | road vehicle |
  | ПТП | road traffic accident |
  | ЗДвП | Road Traffic Act |
  | ППЗДвП | Rules for implementing the Road Traffic Act |
  | МВР | Ministry of the Interior |
  | КАТ | Traffic Police |
  | ИААА | Executive Agency "Automobile Administration" |
  | ЕО | EC |
  | ЕС | EU |
  | ДВГ | internal combustion engine |
  | ТОЛ | toll |
  | ЕКМТ/СЕМТ | ECMT |
  | ТИР | TIR |

* **Legal citations** keep their numbers in your language's citation style. For example, "чл. 157, ал. 4 ЗДвП" is
  "Art. 157(4) of the Road Traffic Act".

## 5. Numbers, units, dates

* **Values never change.**
  * Use your decimal separator: "." in en and hi, "," in all other languages.
  * Thousands may be grouped as your language does.
  * Digits stay digits and number words stay words.
  * Hindi uses the digits 0–9, not Devanagari digits.
* **Units** keep the SI symbols of the source: km/h, km, m, cm, kg, t, kW, ‰, %, °C, bar.
  * Russian may use its standard Cyrillic symbols (км/ч, м, кг, т); decide once.
  * Never convert to other units.
* **Time of day** uses the 24-hour clock (22:00).
* **Dates** keep their digits ("След 12.12.24г." becomes "after 12.12.24" in your language's wording).

## 6. Register and style

* **Register:** neutral and formal, like official theory-test questions in your country.
* **Address:** when the Bulgarian addresses the candidate, use the formal address your country's tests use (Sie,
  vous, usted, Вы, siz, dumneavoastră, आप, εσείς…). Portuguese follows the forms customary in Portuguese
  (Portugal) test materials.
* **Gender:** use the generic forms of your legal language. No gender stars, slashes or double forms.
* **Language variants:**
  * es means Spain;
  * pt means Portugal (European Portuguese, the 1990 spelling), with words like condutor, peão, passadeira,
    autoestrada, carta de condução — never Brazilian forms;
  * en means British spelling and EU/UK terms (licence, tyre, kerb, motorway, carriageway).
* **Capitalisation:**
  * sentence case for questions and answers;
  * topic titles become sentence-case titles, not ALL CAPS.
* **No markdown, HTML or explanations** inside any string.

## 7. When in doubt

* Look at the picture. Each part gives `picture_dir`; the file is `<picture_dir>\<media id>.png`.
* Look at the questions in `same_text`.
* Ask yourself how the official theory test of your country would phrase it.
* Choose the reading that keeps the Bulgarian meaning and the right/wrong status of every answer.
* Write the case in `notes.md` (id, problem, decision). Never leave a string untranslated.
