# English (en) translation notes

British spelling and EU/UK terminology. Terminology is fixed in `glossary.json`; this file lists decisions a reviewer
should know and every place where the Bulgarian looked wrong.

## General decisions

* **автомобил**: “car” in traffic situations and rules; “vehicle” in the technical topics (systems, parts,
  maintenance), which are shared by categories B, C and D and where автомобил means the machine in general. ППС =
  road vehicle, МПС = motor vehicle, превозно средство = vehicle, лек автомобил = passenger car, товарен автомобил =
  goods vehicle.
* **спиране / престой / паркиране** = stopping / standing / parking. “Standing” is the Vienna Convention term
  (art. 23) for a stop only for the time needed to let people on or off or to load or unload.
* **изпреварване / заобикаляне / разминаване** = overtaking / going around / passing (an oncoming vehicle).
* **платно за движение / пътно платно** = carriageway / roadway. The bank treats them as different answers
  (iaaa-11575, iaaa-11579, iaaa-11580, diagram m-2f088af96c1d913a), so they need different English words.
* **генератор** = generator; **алтернатор** = alternator (iaaa-7587 defines the alternator as an AC generator).
* **техническа изправност** = good technical condition (also used for trams, where “roadworthy” would not fit).
* Bulgarian slashes used as brackets (“/антифриз/”) become English round brackets.
* Apostrophes are the straight ASCII apostrophe throughout; quotation marks are “ ”.

## Labels

* `УПК` (variant D.zaguba-…-i-upk) is read as “удостоверение за професионална компетентност” and rendered “CPC”
  (certificate of professional competence, the UK “Driver CPC”). The Bulgarian “… ЗДвП. и УПК” is ambiguous; the
  English keeps the same ambiguity (“… of the Road Traffic Act and CPC”).
* “След 12.12.24г.” = “After 12.12.24.” (the final full stop keeps the abbreviation point of “г.” = year).
* “с правоспособност” = “with a driving entitlement”; “притежаващ правоспособност” = “holding a driving
  entitlement”; “без правоспособност” = “without a driving entitlement”.

## Questions: source problems and decisions

| id | problem | decision |
|---|---|---|
| iaaa-5439 | Yes/no question ends with “.” | Ends with “?”; lint exception `end_punct`. |
| iaaa-6164 | “провобуксуващата” is a typo for “противобуксуващата” | Translated as traction control system (ASR). |
| iaaa-7560 | Stem “…, което би причинило нарушаване на:” does not fit the answers (“повишаване/намаляване на …”): “impairment of a reduction of stability” is nonsense. | Translated the intended meaning: “…, which would result in:”. |
| iaaa-7454 | “предавателна група” (the tappets, pushrods and rockers between camshaft and valves) | “a transmitting linkage” (glossary); not “valve train”, which would echo “valves” in the stem and give the answer away (review: note brought into line with the translation). |
| part 01 | Spelling slips with no effect on meaning: хлъзгъв (6163), скоросттта (6165), арматулното (5483), мужду (7447), правволинейното (7443), Latin “M” in “Mаксималната” (7430). | Translated normally. |
| iaaa-7711 | Answer a2 “неправилнозадните гуми”: the word “неправилно” is glued to “задните гуми”. | “the rear tyres”. |
| iaaa-7649 | a2 “/трансмисиятна автомобила” is a typo for “/трансмисията/ на автомобила”. | “the vehicle's power train (transmission)”. |
| iaaa-7636 | Stem ends with “::”. | Single “:”. |
| iaaa-7691, iaaa-7449, iaaa-7520 | Some answers are verb phrases or clauses that do not fit the stem grammatically (“причинява: нарушава …”, “да осигури: да улесни …”, “причина за: двигателят не може да се спре”). | Rendered as noun phrases with the same meaning so that stem + answer is grammatical; no answer became more explicit than the others. |
| iaaa-7525 | A question (“Какви видове … съществуват:”) ends with “:”. | Kept the question form and the colon. |
| iaaa-7533 | Statement without a final full stop. | Kept without one. |
| iaaa-7612 | “буква С” uses the Cyrillic С; the headlight marking is the Latin letter C. | Latin “C”. |
| iaaa-7635, iaaa-7529 | Synonym pairs where English has one word (“светлоотражател /рефлектор/”, “кормилно колело /волан/”). | One English word (“a reflector”, “the steering wheel”); lint exception `length` for 7635-a2. |
| iaaa-7435 | картер as an engine part. | “crankcase” here; “sump” where the oil level in it is meant (5484, 5439, 7482 …). |
| part 02 | Spelling slips with no effect on meaning: на.отделни (7691), повишавава (7690), регулиравка (7685), Latin “e” in “eжедневно” (7686), генеретора (7594). | Translated normally. |
| iaaa-7544 | Stem “… предназначена за задържане:”; the wrong answer a3 (“намаляване на скоростта …”) does not fit it grammatically. | Mirrored (“… designed for holding:”), so that “holding” is not added only to the correct answers. |
| iaaa-7660, iaaa-7687, iaaa-7646 | Digit plus number word (“2 два пъти”, “1 /един / път”, “1 /едно/”). | Both kept: “2 (two) times”, “1 (one) time”, “1 (one)”. |
| iaaa-5438, iaaa-7461 | “хидравлична охладителна уредба” and “течностна охладителна уредба” both mean a liquid cooling system. | Both “liquid cooling system”. |
| iaaa-7589 | “Стартерът е: … пусков електродвигател”. | стартер = “the starter” everywhere, so that the stem does not repeat the correct answer (“starter motor” / “starting electric motor”). |
| ККМ | Trolleybus “контактно-кабелна мрежа”. | “overhead contact network”. |
| part 03 | Spelling slips with no effect on meaning: маслоизмелвателната (7602), неоходимо (7630), възглавнца (7683), продължитерно (7545), Степенноста (7646), “с произвежда ел.енергия” (12094). | Translated normally. |
| iaaa-7285 … 7290, 7293, 7284 | Answers name vehicle types (“автомобил и ремарке”, “автомобил”, “товарен автомобил”). | автомобил = “car”: with “vehicle”, a wrong answer such as “a vehicle and a trailer” would describe a tractor unit with a semi-trailer as well. |
| колесар | Bulgarian trailer type. | “pole trailer” (only in wrong answers). |
| влекач за ремарке | Defined term (iaaa-7291, 7292). | “road tractor”, the EU term of Directive 2007/46/EC, Annex II (body code BD), whose definition the question repeats. |
| iaaa-13487, iaaa-13480 | The centre is called “Центъра за контрол и координация” in one question and “Центъра за координация и контрол” in the other. | Kept as written: “Control and Coordination Centre” / “Coordination and Control Centre”. |
| iaaa-13487 | Answers a1 and a3 start with a capital (official names). | With the article, as a2 “the depot duty officer” and 7014-a2 (“the Head of the “Operations” Department”, “the Control and Coordination Centre”); `case` exceptions (review: the article was restored). |
| iaaa-12138 | a3 “… до първа спиркостоянка на маршрута без пътници в нея” — “нея” may be the stop or the motor car. | Ambiguity kept: “… up to the first stop on the route, with no passengers in it”. |
| iaaa-12096 | “контактно кабелната мрежа (ККМ)” | The Bulgarian abbreviation in brackets is left out because the full English term is given. |
| part 04 | Answers ending with “;” (13491) or “.” (13505 a2, 12132 a1) and answers starting with a capital (12132, 12133, 13462) | Kept as in the Bulgarian. |
| part 04 | Spelling slips with no effect on meaning: линиии (12131), сътав (7300), “част то талигите” (13462), съоражения (13467), изклю¬чение (7411–7414), “са зареждат” (13478). | Translated normally. |
| манометър (7716, 7574, 7491 …) | “pressure gauge” would repeat “pressure” from the question only in the correct answer. | “manometer” everywhere (also the cognate of the Bulgarian word). |
| iaaa-12109 | The stem is a completion stem but ends with “?” (“… водачът на тролейбус е длъжен?”). | Made a real question: “… what must the trolleybus driver do?”; the answers keep their verb form. |
| iaaa-7539, iaaa-7468, iaaa-7488 | Answers that do not fit the stem grammatically (“се определят от: по преценка на водача”, “причинява: не нарушава …”, “чрез: визуално …”). | Rendered as noun phrases with the same meaning (“the judgement of the vehicle's driver”, “no disturbance of …”, “visual external inspection”). |
| iaaa-11745, iaaa-12113 | Stems without final punctuation. | Kept without. |
| iaaa-7627 | a2 “лоша /недобрелектрическа връзка” is a typo for “лоша /недобра/ електрическа връзка”. | “a bad (poor) electrical connection to “earth””. |
| part 05 | Spelling slips with no effect on meaning: уселвател (7568), отварянета (7738), техническаната (7576), “при работи” (7742). | Translated normally. |
| iaaa-5324 … 5329 | “Кое от показаните превозни средства е автомобил?” — the correct pictures are a concrete-mixer lorry, a trolleybus and a van; the wrong one is a tracked tractor. | “automobile”, not “car”: the legal category (= the Vienna Convention's “motor vehicle”, trolleybuses included) is tested, and “car” would make the correct pictures wrong. Same in 5177/5178 (“automobiles”). |
| iaaa-5176 … 5178 | “Кои … са моторни?” — the key counts mopeds and excludes trams. | “motorised” (review: the plain adjective, translated as written per BRIEF correction 3; “motor vehicles” is the glossary term for МПС, which excludes mopeds, so it taught a wrong rule. Trams are keyed wrong just as with Bulgarian «моторни»). |
| First-person answers (5848, 12004, 12022 …) | Bulgarian first-person answers (“подавам”, “трябва да пропусна”) start in lower case. | Kept in the first person; English capitalises “I”, recorded as lint exceptions `case`. |
| МПС със специален режим на движение | Legal term (vehicles using the special light and sound signals). | “motor vehicle with a special traffic regime”. |
| part 06 | Spelling slips with no effect on meaning: мощността (8255), “трябва сигнализира” (6052). | Translated normally. |
| iaaa-5294, 5295, 5296 | The diagram labels the three signs with the Cyrillic letters “а.”, “б.”, “в.”. | “a” is written with the identical Latin letter; “б” and “в” have no Latin look-alike and are kept as shown in the picture (lint exceptions `cyrillic`). |
| iaaa-5244 | “ВUS” is written with a Cyrillic В. | “BUS” (Latin, as painted). |
| iaaa-8247 | “50 cm3” (digit 3, not ³). | Kept as written. |
| iaaa-6041 | “автомобилни пътища” next to “автомагистрали”. | “roads for motor vehicles” (glossary: автомобилен път = road for motor vehicles, the Vienna Convention name of sign E,6a; changed from “motor road” in the review), distinct from “motorways”. |
| iaaa-5541 | разминаване with child cyclists. | “passing the oncoming child cyclists”: English “pass” alone could mean overtaking; разминаване always means opposite directions. |
| iaaa-12075, 12073 | “мигаща или проблясваща светлина” names two kinds of light. | мигаща = flashing (as in “flashing amber” of traffic lights), проблясваща = blinking. |
| iaaa-5228, 5230 | The key counts the islands as part of the roadway (пътно платно) but not of the carriageway (платно за движение). | Translated as keyed. |
| part 07 | Spelling slip with no effect on meaning: сигнарлизира (5294–5296). | Translated normally. |
| iaaa-5266, iaaa-5268 | “кръстовище с кръгово движение”. | “roundabout junction”. |
| iaaa-7079 | Answer a3 repeats “не трябва” from the stem (“… не трябва: не трябва да е наказван …”). | Repetition dropped (“must not: have been penalised for speeding”); the meaning is unchanged. |
| iaaa-7138 | Plural subject with singular verb (“Застраховани лица … е:”), answers in the singular. | “The insured person … is:”. |
| iaaa-7143 | a4 starts with “когато” and does not fit the stem. | Kept as a conditional clause (“if people were injured in the accident”). |
| Insurance names | “задължителна застраховка „Гражданска отговорност“ на автомобилистите”, “задължителна застраховка „Злополука“ на пътниците”. | “compulsory motor third-party liability insurance”, “compulsory passenger accident insurance”. |
| “умишлени престъпления от общ характер” | Bulgarian criminal-law term. | “intentional crimes of a general nature”. |
| part 08 | Spelling slips with no effect on meaning: Дейсвието (7132), Latin “e” in “опасeн” (5167), “превозното средства” (7128), Лиценза (7073), притежателят (7070). | Translated normally. |
| iaaa-7127, 7125, 7126 | Statement-form stems ending with “?” (“Не са обект на застраховане по …?”). | Rendered as real questions (“Who is not insured …?”, “What is insured …?”). |
| iaaa-6782 | Stem “водачът е задължен:” followed by answers with their own modal verb (“трябва да замени …”, “може да довърши …”). | Mirrored (“is obliged: must replace … / may complete …”) so that neither answer is smoothed more than the other. |
| iaaa-6768 | Stem “… когато e:” (Latin e); a4 (“водачът е управлявал …”) does not fit it. | Mirrored. |
| лв. | Bulgarian lev. | “BGN 500” (currency code); end_punct exceptions for 11662 because the Bulgarian full stop is the abbreviation point of “лв.”. |
| карта на превозвача | Tachograph card. | “company card” (EU term of the tachograph regulations). |
| iaaa-6953 | CMR items. | Literal (“the place of delivery of the goods”), without the CMR word “designated”, which the Bulgarian does not have. |
| part 09 | Spelling slips with no effect on meaning: “превозното средства” (7129–7131), осугуряват (6948), спесификация (6834). | Translated normally. |
| “… по образец” (6826, 6827, 6831) | Document “in the prescribed form”. | “standard” (“a standard consignment note”), short enough not to make the correct answers stand out. |
| iaaa-12121 | A statement ending with “?”, answered true/false. | Kept as a statement with “?”. |
| iaaa-12115, 12116 | Trolleybus “стрелка” is the switch in the overhead wires. | “overhead switch”, “switch blade” (rail “стрелка” = points). |
| ЕКМТ/(СЕМТ) | Both acronyms of the same body. | “ECMT (CEMT)”. |
| iaaa-6961 | Same text and answers as 6960 but not listed in `same_text`. | Translated identically. |
| part 10 | Spelling slips with no effect on meaning: “ва пътници” (12121), дължен (6825), прикючи (6776), движенито (12116), “стрелка стрелка” and “електродвигател двигател” (12115), “лиценза Общността” (6830). | Translated normally. |
| T17 coupling devices (7313–7362) | Technical terms of UNECE Regulation No 55. | coupling ball and towing bracket, coupling head (ключалка), drawbar eye (ухо), rigid / hinged drawbar, fifth wheel coupling, coupling pin (kingpin), mounting plate, guide wedges, remote control devices / remote indicators. |
| iaaa-7317 vs 7313–7319 | “ремарке с теглич” and “ремарке с шарнирно окачен теглич” are different Bulgarian terms. | “drawbar trailer” and “trailer with a hinged drawbar”. |
| iaaa-7353 | “ключалка” here is the latch of a fifth wheel coupling, not the coupling head of 7331–7333. | “a lock”. |
| iaaa-6320, 6321 | “спиране за престой”. | “stopping for standing” (glossary: спиране = stopping, престой = standing). |
| iaaa-5834 … 5869 | Answers “на червения автомобил” to “За кой от водачите …?”. | “the red car's” (elliptical possessive: the red car's driver). |
| iaaa-6244, 6248 | “автомобили” as a category on additional panels. | “automobiles” (cars, goods vehicles and buses together). |
| iaaa-7339 | Yes/no question ending with “.”. | Ends with “?”; lint exception. |
| Light and controller signals (5891 …) | Names of the signals in the Bulgarian rules. | green = “Proceeding is permitted”, red = “Proceeding is prohibited”, steady amber = “Caution, stop!”, flashing amber = “Caution”; немигащ = steady. |
| iaaa-5979 | Stem without final “?”. | Kept without. |
| iaaa-11863 | “над 3.5 t. да изпреварват” — a stray full stop after “t”. | Dropped. |
| “автомобили със специален режим на движение” (5965 …) | Category on a sign. | “automobiles with a special traffic regime”. |
| iaaa-6328 | a3 “не трябва да се съобразяват с пътната маркировка”. | “must not follow the road markings” (не трябва = must not). |
| part 12 | Spelling slips with no effect on meaning: Значенето (5912), “леки автомоби” (5965), “с товар е по-голям” (6171). | Translated normally. |
| iaaa-5845 … 5882, 5871 | Controller signals: “мога да завия …” and “е разрешено да завия …” are different wordings. | “I may turn …” and “it is permitted for me to turn …”, kept distinct. |
| iaaa-12126 | “дежурния диспечер КДЦ” (контролно-диспечерски център). | “the duty dispatcher of the control and dispatch centre”. |
| iaaa-7266 | “30°С” written with a Cyrillic С. | “30°C”. |
| iaaa-6220, 6238, 6278 | Plural verb with a singular subject (“Пътният знак … предупреждават”, “… указват”). | Singular in English. |
| iaaa-5925 | a4 repeats “че” after the stem's “че:”. | Mirrored: a4 also starts with “that”, like the Bulgarian. |
| part 13 | Spelling slips with no effect on meaning: средсво (7370), продължителено (7379), разедени (7387), темперетурата (7266), “трябва се осъществява” (7381). | Translated normally. |
| iaaa-7272 | A statement that ends with “?” and has the answers “правилно / неправилно”. | Kept as a statement with “?”; answers “correct / incorrect”. |
| iaaa-6429, 6430, 6431 | a4 repeats “че” after the stem's “че:” (as in 5925). | Mirrored: a4 starts with “that”. |
| iaaa-8264 | a4 “движението само на автомобили” — wrong because motorcycles may also use a motorway. | “only automobiles” (the legal category), not “only cars”. |
| iaaa-5756, 5754 | “теглене на двуколесни ППС” (towing them) next to “използване на двуколесни МПС за теглене” (towing with them). | “It is prohibited to tow: two-wheeled road vehicles …” and “using two-wheeled motor vehicles for towing”, kept distinct. |
| iaaa-6498 | “коя от изброените маневри е забранено” is singular although two answers are correct. | Singular kept (“Which of the following manoeuvres is prohibited …?”), as the pivot asks. |
| iaaa-12062 | “Какво трябва да очаквате …?” | “What should you expect …?” (“must expect” is not idiomatic). |
| iaaa-6465, 6469 | a2 “да се движа с готовност за спиране” and “да управлявам с готовност за спиране”. | Both “I must drive ready to brake” (same meaning; different questions' answers). |
| part 14 | Spelling slips with no effect on meaning: “водача на тролейбуса” (12127), “на водачът на автобус” (7267), “зеленият автомобил” (12035), “е длъжен :” (6427). | Translated normally. |
| Video questions (12003 …, 11997 …) | Answers mix “да + verb” (“да намаля скоростта”) and first-person present (“намалявам скоростта си”). | Kept apart: “да …” after “What must you do …?” is a bare infinitive (“reduce speed”), after “What is the correct course of action …?” it is “to …”; first-person answers stay “I reduce …”. |
| iaaa-12030, 12062 | “Какво трябва да очаквате?” with “да”-clauses (12030) or “че”-clauses (12062). | “expect the blue car to enter my lane” and “that the children will step onto the carriageway”, mirroring the Bulgarian. |
| iaaa-12056 | a1 “в разделителната ивица между платната на релсовия път” — the video presumably shows a rail track on the central reservation. | “on the central reservation between the carriageways, on the rail track”. |
| iaaa-6353, 6351 | “запалена факла” is a burning torch, not a British electric torch. | “a burning torch or a lantern”. |
| iaaa-5377, 5380, 5566, 5634, 5564, 5612 | “Кой от автомобилите …” where the answers are a goods vehicle, a bus or a passenger car. | “Which of the vehicles …”; “both vehicles” there, “both cars” where both are cars. |
| iaaa-11696, 11697, 11699 | “автомобил от категория В / В1” (category B1 covers quadricycles). | “a category B / B1 vehicle”. |
| iaaa-5630 | “велосипедна пътека” with “5 м преди / след” (built like “пешеходна пътека”, 7809). | “cycle crossing” (glossary), not “cycle path” (“велосипедна алея” = cycle track). |
| iaaa-5828 | Stem without a final colon. | Kept without. |
| iaaa-6446 | “таксиметровите автомобили”. | “taxis” (length exception). |
| iaaa-6219 | Stem ends with “…, като:” and the answers start with “трябва да …”. | “…; to this end, the driver:” + “must take account of …”. |
| iaaa-6091, 6352 | “навлизанетo” with a Latin o; “релсовите ППС се намира” (singular verb). | Translated normally. |
| iaaa-6425, 11870 | A statement (6425) and a question (11870) that end with “:”. | Colon kept. |
| iaaa-12008 | “… не трябва да предприема изпреварване, поради?” — a stem that ends with “?”. | “… I must not start overtaking because of what?” |
| iaaa-6232 | “Кой от водачите трябва да осигури предимство?” — the answers “на товарния автомобил, защото навлиза …” name whose driver it is. | “the driver of the goods vehicle, because it is entering …” |
| iaaa-5818, 6219 | Stem “…, като:” followed by answers with and without “трябва”. | “…; to this end, they:” + the answers as given (“must stop if necessary”, “clear sufficient space …”). |
| “разрешаващ сигнал” (5803, 5935, 11484) | Signal that permits passage. | “a signal permitting passage”. |
| part 17 | Slips with no effect on meaning: “раздилителната” (5409), “не по- висока” (11719). | Translated normally. |
| “правилото на десния” (5944, 5945), “правилото за „предимството на дясностоящия”” (5931, 5935, 11484) | Two wordings of the same rule. | Both “the “priority to the right” rule”. |
| iaaa-6261, 6286 | Statements (answers “правилно / неправилно”) that end with “:”. | Colon kept. |
| “При тази ситуация с предимство е …:” (5367 …, 6221 …) | Who has priority. | “In this situation, priority belongs to (the driver of):”. |
| part 18 | Slips with no effect on meaning: “автомобилa” with a Latin a (5367), “синият автомобил, е:” (6570). | Translated normally. |
| iaaa-12037 | The stem is only “При тази ситуация?”. | “In this situation?” — kept as it is; the answers say what the driver does. |
| iaaa-5730 | “тегличът” of a rigid towing link (glossary “теглич” = drawbar of a trailer). | “the tow bar” (glossary entry added). |
| iaaa-6562 | a3 “мотоциклетистът е с предимство, защото е двуколесно МПС”. | “… because they are on a two-wheeled motor vehicle”. |
| part 19 | Slips with no effect on meaning: “синия / червения автомобил е с предимство” (5370), “пьтния” with ь (5952, 6608), “дължинатана” (5733), “да навлизат” (9837). | Translated normally. |
| iaaa-7175 | a1 is quoted as a whole (“"обиколен превоз при затворени врати"”), a4 only in part (“при „отворени врати””). | Quotation marks mirrored: “closed-door tour” and tour with “open doors”; “пълен – празен” as the EU-style “laden – unladen”. |
| iaaa-6581 | a2 “трябва да се подготвя за потегляне” (first person implied, as in a3 “може да завия”). | “I must get ready to move off”. |
| part 20 | Slips with no effect on meaning: “задължетелен” (5334), “забрананява” (5797), “забранява :” (5546), “3,5 т” with a Cyrillic т (6401–6403). | Translated normally; “3.5 t”. |
| iaaa-6908, 6899, 6900 | “ADR конвенцията”, “Конвенцията AТР” (the latter in mixed Latin/Cyrillic letters). | The official English names: “the ADR Agreement”, “the ATP Agreement”. |
| iaaa-11343 | a2 “пътен формуляр” (wrong) next to the real document “пътен лист” (glossary “journey form”). | “a road form”, so that it cannot be taken for the journey form. |
| iaaa-11672 | “между 6,00 и 21,00 ч.” | “between 6:00 and 21:00” (24-hour clock; the digits are kept as in the source). |
| iaaa-7094 | “При извършване на специализирани на деца …” — the noun “превози” is missing. | “When special regular services are carried out for children …”. |
| iaaa-6922 | “товар, който излиза отстранини на ПС” — slips for “отстрани на ППС”. | “a load that … projects more than 0.20 m beyond the sides of the vehicle”. |
| iaaa-12087 | Statement without a final full stop. | Kept without. |
| part 21 | Slips with no effect on meaning: “по-гомяма” (11754), “водачът” repeated at the end (7116), “тренспортни” (7163), “всики” (7112), “товарана” (6929), “възражениета” (6978). | Translated normally. |
| iaaa-6111 | “Времето за реакция … оказва ли влияние на дължината на спирачния път?” — key “да”. Bulgarian “спирачен път” covers both the braking distance and the whole stopping distance; in UK terms reaction time changes the thinking distance, so the stopping distance, but not the braking distance. | “stopping distance” here, so that the keyed answer stays true; elsewhere (mass, tyres, surface, locked wheels) “braking distance”. |
| iaaa-6907 | “Спогодбата ADR”. | “The ADR Agreement” (as in 6908). |
| iaaa-6910, 8344 | “собствената маса на контейнера”, “тара на контейнера”. | “the unladen mass of the container”, “tare of the container”. |
| part 22 | Slips with no effect on meaning: “отдзад” (6916), “ПС” for ППС (6921), “предвижва” for “предвижда” (6132), “за приеме” (5739), “уравлението” (5743), “продържително” (5716), “автомобилитге” (5686), “е добре :” (6130). | Translated normally. |
| iaaa-6996, 6997, 7012 | Statement-like stems that end with “?”. | “?” kept. |
| iaaa-7029 | A statement (answers “правилно / неправилно”) that ends with “:”. | Colon kept. |
| iaaa-5714 | “Причина за … са:” — singular noun, plural verb; one correct answer. | “A cause of … is:”. |
| iaaa-7014, 7015 | a4 “областният отдел на ИА „АА”” (abbreviation). | Written out: “the regional department of the Executive Agency “Automobile Administration”” (length exception). |
| part 23 | Slips with no effect on meaning: “намялява” (5724), “не по-повече” (5685), “означенато” (7062), “извън габаритно” (6992, 6994), “включен светлина” (5663), “”Дневните светлини”” (11633). | Translated normally. |
| iaaa-7243 | Statement ending in “.:”. | Ends with “:” only. |
| iaaa-7326 | Stem “… на път с наклон не по-малък:” with the answers “от 5%” … (no words in the answers). | “… on a road with a gradient:” + “of not less than 5%” …, so that every answer is a phrase; meaning unchanged. |
| iaaa-7390 | A statement that ends with “?”, with “when …” answers. | Made a real yes/no question (“Is a … combination likely to “jackknife” when it brakes?”), as the Bulgarian «има вероятност …?» is; the “when …” answers still follow (review). |
| iaaa-7391, 7390, 7400 | “влекач” of a combination with a trailer. | “tractor unit” (glossary). |
| iaaa-5338 | “двустранния констативен протокол”. | “the bilateral accident statement” (the European accident statement of the glossary). |
| part 24 | Slips with no effect on meaning: “беде” (7394), “седящ пътници” (7247), “средсво” (7421), “задвижението” (6918), “опастност” (7389), “oрганизира” with a Latin o (11413), “DЕ” in mixed script (11763). | Translated normally; “DE”. |
| iaaa-6018 | a2 “застраховка "Каско"”. | “comprehensive insurance” (the English name of the product). |
| iaaa-5498, 11385, 11409 | “акт” (the statement establishing an administrative offence) as opposed to “фиш” (ticket). | “statement of offence” / “the statement establishing the administrative offence”; “ticket”, “electronic ticket”. |
| iaaa-5351, 7052 | “от най-съществено значение са данните: от опознавателния знак …”. | “the most essential data are those: from the identification sign, …”. |
| iaaa-11400, 11503 | Answers that do not continue the stem grammatically (“има наложено наказание глоба …”, “превиши …”). | Mirrored as they stand (“has a fine imposed …”, “exceeds …”), so that the wrong answers keep their form. |
| iaaa-6003 | “туристическо ремарке”. | “caravan”. |
| part 25 | Slips with no effect on meaning: “всичси” (11362), “изършено” (8296), “електроннен” (8294), “трябвада” (5536), “сигнализара” (5339), “oрганизира” with a Latin o (11367). | Translated normally. |
| part 15 | Slips with no effect on meaning: “Кой два” (5862), “двиние” (11684), “130 кkm/h” with a Cyrillic к (11712), “3 t.” with a stray full stop (11703, 11704), “прaвилно” with a Latin a (6098). | “Which two”, “130 km/h”, “3 t”; otherwise translated normally. |

## Recurring decisions in the questions

* **First-person answers** (“трябва да намаля скоростта”, “пропускам …”) stay in the first person: “I must reduce
  speed”, “I give way to …”. English capitalises “I”, so these answers have `case` exceptions (that is most of the
  293 entries in `lint-exceptions.json`; 3 were added in the review: 13487-a1/a3 `case`, 5334 `hint`).
* **Infinitive answers** (“да намаля скоростта”) are bare infinitives after “What must you do …?” and “to …” after
  “What is the correct course of action …?” or “it is necessary:”.
* **“е разрешено да …” vs “мога да …”** in first-person answers: “it is permitted for me to …” vs “I may …”, kept
  apart because the bank uses both wordings side by side.
* **Hours of day**: “тъмната / светлата част на денонощието” = “the hours of darkness” / “daylight hours” (harmonised in
  the final check: 5407, 5423, 5679, 6725, 7006, 7008, 7009, 8279); only iaaa-6136, whose stem asks “In which part of
  the day …?”, keeps “in the daylight part / in the dark part”.
* **Singular/plural of “Кое / Кои от изброените …”** is kept where English marks it (pivot rule); constructions such as
  “In which of the following cases …” are number-neutral in English, as they are in practice in Bulgarian.
* **Hint warnings**: wherever a correct answer grew only because English needs an article, a compound
  (“first-aid kit”), or a written-out abbreviation (ППС, МПС, ПТП, ДВГ, ИААА), the wording was kept and a `hint`
  exception explains why; real hints (e.g. “pressure gauge” repeating the stem) were reworded instead.

## Interface strings

* App name “Driving Theory Test” (19 characters); “изпитен тест” = “mock exam”, “тест” alone = “test”.
* ИААА is introduced once in full (“Executive Agency “Automobile Administration” (IAAA)”, onboarding disclaimer and
  attribution) and is “IAAA” elsewhere, because the interface lines are short.
* Buttons are imperatives in sentence case (“Try again”, “Start test”, “Remove bookmark”); British forms “practise”
  (verb), “practice” (noun), “learnt”, “colours”, “licences”.
* Plural forms are exactly “one” and “other”. Where English needs no inflection the two forms are identical
  (“%1$d of %2$d correct”). `core_ui_video_plays` is rendered “%1$d of %2$d play(s) used”, because “watched 1 of 3
  times” is unclear in English.
* The captions under big numbers (“questions”, “points”, “to pass”, “days in a row”) are plain plurals that read for
  any number, as the notes ask.

## Final check

* `--all`: 0 errors, 0 warnings, 290 accepted exceptions; coverage 25/25 parts, 2476/2476 questions, 7465/7465
  answers, labels and UI complete.
* The only consistency warning (iaaa-7035-a2 vs 7411–7414, “само полуремаркетата”) was harmonised to “semi-trailers
  only”.
* Duplicate keys in `glossary.json` (“поледица”, “маса с товар”, “совалков превоз”, “мъртва зона”,
  “теглително-прикачно устройство”) were merged.

## Open doubts for a reviewer

* iaaa-6111: “stopping distance” (not “braking distance”) so that the keyed “yes” stays true in UK terms.
* “Standing” (престой) is the Vienna Convention term but may be unfamiliar to UK readers, who know only “stopping”
  and “parking”.
* iaaa-12056: the position “в разделителната ивица между платната на релсовия път” could not be checked without the
  video.
* УПК in the labels is read as CPC (see Labels).
* iaaa-5176: the key counts mopeds among “моторни” vehicles (glossary note).
