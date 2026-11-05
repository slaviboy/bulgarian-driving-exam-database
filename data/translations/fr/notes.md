# French translation — notes for the reviewer

Language: French (fr-FR), Code de la route terminology, EU legal French (Directive 2006/126/EC,
Regulation (EC) No 561/2006, Regulation (EC) No 1073/2009) and the French text of the 1968 Vienna
Convention. Bulgarian stays authoritative.

## Key decisions (see glossary.json for the full list)

| Topic | Decision |
|---|---|
| ППС / МПС / автомобил | véhicule / véhicule à moteur / automobile (f.). лек автомобил = voiture particulière; товарен автомобил = véhicule de transport de marchandises (not "camion", which in French law means N2/N3 only, while the Bulgarian term includes vehicles up to 3,5 t that a category B driver may drive). |
| спиране / престой / паркиране | generic stopping = s'arrêter / immobilisation; престой (and "спиране за престой") = arrêt (exact Code de la route definition of "arrêt"); паркиране = stationnement. спиране as braking = freinage. |
| изпреварване / заобикаляне / разминаване | dépassement / contournement / croisement. Because "dépasser" is reserved for overtaking, превишавам (a speed or a value) = excéder. |
| допустима максимална маса | masse maximale autorisée (EU legal French; = French PTAC). Not abbreviated, so that "masse maximale autorisée de l'ensemble" stays correct for combinations. |
| правоспособност | "permis de catégorie X" when a category is named; "droit de conduire" otherwise; без правоспособност = sans permis; загуба на правоспособност = perte du droit de conduire. |
| Abbreviations | written in full (МПС, ППС, ПТП, ЗДвП, ДВГ…); ЕС = UE, ЕО = CE, ЕКМТ/СЕМТ = CEMT, ТИР = TIR. |
| Citations | чл. 157, ал. 4 ЗДвП = art. 157, al. 4, de la loi sur la circulation routière. |
| Typography | U+00A0 before ? : ; ! and inside « » (stored as the JSON escape  ); U+00A0 between a number and its unit; straight apostrophe U+0027; all Bulgarian quote styles become « ». |

## Labels

* `variants.*.effective_note`: "След 12.12.24г." = "Après le 12.12.24". The final "." of the Bulgarian is the
  abbreviation dot of "г." (година); it is dropped as the style guide's date example shows, and the 23 resulting
  `end_punct` warnings are recorded in lint-exceptions.json.
* `variants.*.description` ending in "ЗДвП." keep the final "." exactly where the Bulgarian has it (3 variants).
* `D.zaguba-na-pravosposobnost-po-reda-na-chl-157-al-4-zdvp-i-upk`: "…ЗДвП. и УПК". The stray "." after ЗДвП is a
  typo and is dropped. УПК is read as "удостоверение за професионална компетентност" = "certificat de capacité
  professionnelle"; the Bulgarian structure ("… и УПК", no preposition) is kept, so the French keeps the same
  ambiguity. **Please confirm the meaning of УПК.**
* `D.s-pravosposobnost-za-kategoria-s1-s-i-kategoria-v-sas-stazh-2g`: "със стаж 2г." = "avec 2 ans d'ancienneté"
  (attached to category B, as in the Bulgarian); the final "." is kept.
* Topic titles: агрегати = organes, възли = ensembles, системи/уредби = systèmes, предназначение = fonction,
  наименование = dénomination; "техника на безопасност" = sécurité du travail.

## Questions — source problems and decisions (id, problem, decision)

* iaaa-6164 — "провобуксуващата" is a typo for "противобуксуващата" (ASR) → "système antipatinage (ASR)".
* iaaa-5439 — a yes/no question that ends with "." in Bulgarian → French question with "?" (lint exception).
* iaaa-7560 — the stem "… което би причинило нарушаване на:" with the answers "повишаване/намаляване на
  стабилността/устойчивостта/управляемостта" does not read coherently in Bulgarian. Rendered as "… qui
  provoqueraient une perturbation : par augmentation / par diminution de la stabilité / de la dirigeabilité", which
  keeps the intended meaning (the correct answers are the two decreases) and the right/wrong status.
* iaaa-5438 — "хидравлична охладителна уредба" means a liquid cooling system → "système de refroidissement par
  liquide".
* iaaa-7700, iaaa-7731 — French has only one word for the inner tube ("chambre à air"), so "pneumatique sans
  chambre à air / à chambre à air" echoes the answer "la chambre à air". The Bulgarian has the same link
  (безкамерна/камерна гума ↔ камера = вътрешна гума); accepted.
* Typos without effect on the translation: iaaa-5483 "арматулното", iaaa-6165 "скоросттта", iaaa-7443
  "правволинейното", iaaa-7447 "мужду", iaaa-6163 "хлъзгъв", iaaa-7430 Latin "M" in "Mаксималната".
* "силовото предаване (трансмисията)" / "моторно /двигателно/ масло" / "кормилно колело /волан/": the Bulgarian
  gives two synonyms; French has one term (transmission / huile moteur / volant), so the synonym is not repeated.
* "ресорите /пружините/" = "ressorts à lames (ressorts hélicoïdaux)" (leaf springs / coil springs).
* iaaa-7711 — a2 "неправилнозадните гуми" is a typo (the word "неправилно" glued to "задните гуми") → "les
  pneumatiques arrière". The lint `hint` finding is a false positive caused by this typo (exception recorded).
* iaaa-7636 — the stem ends with "::" → single ":".
* iaaa-7691, iaaa-7449 — some Bulgarian answers are verb phrases that do not continue the stem grammatically
  ("причинява: … нарушава …", "да осигури: … да улесни …"); the French makes every answer a noun phrase that
  continues the stem, without changing what is said.
* iaaa-7693 — "спирачно закъснение" is braking deceleration (Bulgarian physics: закъснение = deceleration) →
  "décélération de freinage".
* iaaa-7688 — `hint` false positive (partitive article on a very short answer; exception recorded).
* iaaa-7544 — a3 "намаляване на скоростта…" does not continue "предназначена за задържане:" in Bulgarian either;
  the French mirrors this ("la réduction de la vitesse…") so that the distractor stays as it is.
* iaaa-7605 — the stem ends with "се:" and the answers repeat "се"; the French stem ends with the subject and the
  answers carry the verb ("se lit…").
* iaaa-12105 — a2 (the correct answer) starts with a capital "За" in Bulgarian, a typo that singles it out; the
  French starts in lower case like a1 (lint `case` exception).
* ККМ (контактно-кабелна мрежа, trolleybus) = "ligne aérienne de contact", written in full.
* iaaa-7426, iaaa-7456, iaaa-7558 — `hint` false positives caused by very short Bulgarian answers without articles
  (exceptions recorded with reasons).
* Trams (T06, T08): ватман = "wattman" (the established French word for a tram driver); токоснемател = "capteur de
  courant"; магнитнорелсова спирачка = "frein magnétique sur rail"; контролер = "combinateur"; колоос = "essieu";
  ККМ = "ligne aérienne de contact" (written "(LAC)" where the Bulgarian adds "(ККМ)").
* iaaa-12132, iaaa-12133, iaaa-13462 — the Bulgarian answers start with capitals (and 12132-a1 ends with "."); the
  French mirrors this, since every answer of the question is treated the same way.
* iaaa-13487 — "Началника на отдел …" / "Центъра за контрол и координация" start with capitals in Bulgarian; in French
  the answers continue "sur ordre :" with "du …" (lint `case` exceptions).
* iaaa-13491 — the Bulgarian answers end with ";" (list punctuation); kept, with U+00A0 before it.
* "влекач" = "tracteur" (towing vehicle / tractor unit); "седлови влекач" = "tracteur de semi-remorque"; "трактор" =
  "tracteur agricole". Pulling a trailer = "tracter / traction"; towing a broken-down vehicle = "remorquer /
  remorquage" (Bulgarian uses "теглене" for both).
* iaaa-7290 — `hint` exception: "véhicule de transport de marchandises" is the fixed term for "товарен автомобил".
* **пътно платно ≠ платно за движение.** The pivot glossary lists them as synonyms, but the bank defines them
  differently (iaaa-5230: "Пътното платно включва: банкетите, платното за движение, островите"; part 08: the
  "граница на платното за движение" separates the carriageway "от другите конструктивни елементи на пътното
  платно"). French: платно за движение = "chaussée"; пътно платно = "plate-forme routière" (chaussée + accotements +
  îlots), in every question, including those where Bulgarian uses "пътното платно" loosely (position of a vehicle "sur
  la plate-forme routière", stopping "le plus à droite possible sur la plate-forme routière"). **Reviewer: please
  confirm this choice.**
* iaaa-12112 — a3 (the correct answer) starts with a capital in Bulgarian; lower case in French (`case` exception).
* iaaa-5204 — "разрешената от компетентните органи" = "admise par les autorités compétentes" (the EU wording "déclarée
  admissible"), so that the French correct answer does not echo the word "autorisée" of the defined term.
* iaaa-7515, iaaa-7714, iaaa-7734, iaaa-7485 — `hint` exceptions (very short Bulgarian answers; ДВГ written out).
* iaaa-5176, iaaa-5177 — the bank counts mopeds among the "моторни ППС" (correct answer), unlike the pivot
  glossary's note that МПС excludes mopeds. Translated as written ("véhicules à moteur"); in French law
  (Code de la route) a "véhicule à moteur" includes the cyclomoteur, so the French reads consistently.
* "трактор" = "tracteur" (also "влекач" = "tracteur", "седлови влекач" = "tracteur de semi-remorque"); the context
  always shows which one is meant.
* релсово / нерелсово ППС = "véhicule sur rails / sans rails".
* iaaa-5299, iaaa-5313, iaaa-8230, iaaa-12140 — `hint` exceptions (one-word Bulgarian answers).
* iaaa-11575/11579/11580 — the schema (m-2f088af96c1d913a) shows A = one lane, B = carriageway, C = carriageway plus
  the side strips; this confirms "пътно платно" (C) = "plate-forme routière" ≠ "платно за движение" (B) = "chaussée".
* iaaa-5294/5295/5296 — the picture labels the three countdown posts "а.", "б.", "в." (Cyrillic). "а" is written
  with the identical Latin "a"; "б" and "в" have no Latin look-alike and are kept as printed so that the text
  matches the picture (lint `cyrillic` exceptions for 5295 and 5296). **Reviewer: confirm, or replace the picture.**
* iaaa-5244 — the source writes "ВUS" with a Cyrillic "В"; French "« BUS »" in Latin letters.
* iaaa-8247 — the source writes "cm3" (not "cm³") here; kept, because the digit is part of the number check.
* мигаща / проблясваща светлина = "lumière clignotante / à éclats" (iaaa-12075, iaaa-12073).
* iaaa-11575, iaaa-5228, iaaa-5232, iaaa-12074 — `hint` exceptions (fixed terms of different lengths).
* ППС is normally "véhicule". Where "пътни превозни средства" is contrasted with rail vehicles or with "моторни
  превозни средства" (iaaa-12072, iaaa-5181, iaaa-5145, iaaa-5147), it is "véhicules routiers", because "un véhicule
  sur rails assimilé aux véhicules" would lose the point of the question.
* Sign-description answers: предупреждава = "avertit", сигнализира = "signale", указва = "indique", обозначава =
  "désigne", забранява = "interdit", so that answers with different verbs stay different.
* iaaa-7079 — a3 repeats "не трябва" after the stem "… не трябва:"; mirrored ("ne doit pas : ne doit pas avoir été
  sanctionné…").
* iaaa-5199, iaaa-5231, iaaa-5145, iaaa-5146 — `hint` exceptions (МПС written out; one-word answers; fixed terms).
* Insurance (T14/T15): "обект на застраховане по застраховка X" = "couvert par l'assurance X";
  "Гражданска отговорност" = « responsabilité civile »; "Злополука" = « accidents »; имуществени /
  неимуществени вреди = dommages matériels / moraux; пропуснати ползи = manque à gagner.
* CMR / TIR / tachographs follow the French texts of the CMR Convention, the TIR Convention and Regulation (EU)
  165/2014 (lettre de voiture, prise en charge de la marchandise, transbordement, bureaux de douane de passage,
  carte de conducteur / d'entreprise / de contrôleur / d'atelier, feuille d'enregistrement, double équipage).
* iaaa-11662 — "лв." = "leva" (currency written out; the abbreviation dot is not kept; `end_punct` exceptions).
* iaaa-6859 — every answer repeats "до" (jusqu'à); the French keeps it in the answers and not in the stem.
* iaaa-6782 — the answers start with "трябва"/"може" although the stem ends with "е задължен:"; mirrored.
* iaaa-6727, iaaa-6728 — "00.00 часа … 24.00 часа" = "00:00 … 24:00" (24-hour clock, digits kept).
* iaaa-6750, iaaa-6753 — the source writes "4.5" with a point; French decimal comma "4,5".
* iaaa-12121 — a statement that ends with "?" in Bulgarian (answers вярно/невярно); the French keeps the statement
  word order and the "?".
* iaaa-11621 — "престоя на таксиметрови автомобили" = "effectuer un arrêt" (престой), while "спирането за …" =
  "s'arrêter pour …" (generic stopping), so that the legal terms stay distinct even next to "arrêt" (bus stop).
* "товарителница / пътен лист по образец" = "lettre de voiture type / feuille de route type".
* iaaa-6828, iaaa-6718 — `hint` exceptions; iaaa-6825-a2 — `length` exception (ПТП written out).
* Coupling devices (T17) follow the French text of UNECE Regulation No 55: теглич = timon, ремарке с теглич =
  remorque à timon, ремарке с шарнирно окачен теглич = remorque à timon articulé, окачен / неподвижно закрепен
  теглич = timon articulé / rigide, ухо = anneau d'attelage, ключалка (for the ball) = tête d'attelage, съединителен
  сферичен болт и носач = boule d'attelage et son support, седлово устройство = sellette d'attelage, присъединителен
  (царски) болт = pivot d'attelage (king-pin), стандартни / нестандартни = normalisés / non normalisés, опорна тележка
  = avant-train. In iaaa-7353 "ключалка" inside the fifth wheel is its lock ("verrou").
* Trams stopped at a stop: "спрелия на спирката трамвай" = "le tramway immobilisé à l'arrêt" (avoids "arrêté à
  l'arrêt" and keeps "arrêt" for the stop / престой).
* iaaa-7339 — question ending with "." in Bulgarian → "?" (`end_punct` exception).
* iaaa-6258/6260 — "спирането" (generic stopping) vs "престоят и паркирането": "l'immobilisation" vs "l'arrêt et
  le stationnement", so that the two answers stay legally different.
* упойващи вещества = "substances enivrantes" (iaaa-12124, "alcool et autres substances enivrantes").
* iaaa-6327, iaaa-6211, iaaa-6248, iaaa-6257 — `hint` exceptions (one-word answers, fixed vehicle terms).
* Signal meanings quoted in the bank (ЗДвП wording) are rendered as fixed French formulas in « »: "Преминаването е
  забранено / разрешено" = « Le passage est interdit / autorisé »; "Внимание, спри!" = « Attention, stop ! »;
  "Внимание" = « Attention »; "Забранено е влизането на …" = « Entrée interdite aux … ». Where the Bulgarian omits
  the "!" or the quotes, so does the French.
* iaaa-5979 — the stem is a question without "?" (it ends with the closing quote); mirrored.
* стеснен участък = "tronçon rétréci" (iaaa-11885, iaaa-11886, iaaa-6296).
* iaaa-6303, iaaa-5965, iaaa-5970, iaaa-5971, iaaa-6167, iaaa-12077, iaaa-6317 — `hint` exceptions ("aux …" before
  one-word answers; fixed term for товарен автомобил).

### Part 13

* iaaa-5925-a4 — the answer repeats the "че" that ends the stem ("…, че: че към прелеза…"); typo, translated without
  the duplicate ("un train s'approche du passage à niveau").
* iaaa-6220, iaaa-6238 ("предупреждават"), iaaa-6278 ("указват") — plural verb with the singular subject "пътният
  знак с допълнителна табела"; translated in the singular (« Le panneau avec panonceau avertit / indique »).
* iaaa-12126 — "дежурния диспечер КДЦ": КДЦ is the transport operator's control and dispatch centre (most probably
  "контролно-диспечерски център"); written out as "le régulateur de permanence du centre de contrôle et de
  régulation", because Cyrillic cannot stay. The exact expansion is not certain.
* iaaa-7266 — "30°С" is written with a Cyrillic С; rendered "30 °C".
* iaaa-7381 — "трябва се осъществява" (missing "да"); translated "doit s'effectuer".
* iaaa-12128 — the Bulgarian statement has no final full stop; mirrored.
* iaaa-6322, iaaa-6330 — "изкуствена неравност" = "irrégularité artificielle" (as in iaaa-5257), not "ralentisseur":
  that French word would give away the answer of iaaa-6330 ("à limiter la vitesse des véhicules").
* Traffic-controller answers in the first person: "мога да …" = "je peux …"; "(е) разрешено да …" = "je suis autorisé
  à …"; "забранено да …" = "il m'est interdit de …"; "преминаването ми е забранено" = "le passage m'est interdit".
* "място за задължително спиране" = "endroit où il faut obligatoirement s'arrêter" everywhere (iaaa-5290, iaaa-5930,
  iaaa-5933, iaaa-6322; iaaa-5928 and iaaa-5932 harmonised from « Lieu d'arrêt obligatoire »), so that "arrêt"
  stays reserved for престой.
* "крайпътен обект" = "installation en bordure de route" (iaaa-6214; iaaa-5198 corrected from "objet", which meant a
  physical object rather than a roadside facility).
* "пред знака / след знака" = "avant le panneau / après le panneau" (the wording of the French B21-1/B21-2 signs).
* "линия за изчакване" (iaaa-6322-a3, a distractor) = "ligne d'attente", literal.
* "повреда" = "panne" (iaaa-7382, iaaa-5955), in line with "повредено МПС = véhicule à moteur en panne".
* T20 braking terms follow the French text of UNECE Regulation No 13: freinage continu / semi-continu / à inertie
  (« par poussée »), freinage automatique, système de freinage antiblocage, système de freinage de secours / de
  stationnement; "въздух под налягане" = "air comprimé" (as in iaaa-7367).
* iaaa-5939 — `hint` exception: the correct answer is the Vienna Convention formula « que la route débouche sur un
  quai ou une berge », which is a wrong answer in iaaa-5936.

### Part 14

* iaaa-7272 — a statement written with "?" and answered правилно/неправилно; kept as an intonation question with
  correct/incorrect.
* iaaa-6429-a4, iaaa-6430-a4, iaaa-6431-a4 — the answers repeat the "че" that ends the stem; translated without it.
* iaaa-11731 — "…, е разрешено:" is moved into each answer (« les piétons sont autorisés à … », « le stationnement est
  autorisé … »), because a French "il est autorisé :" cannot be completed both by a noun and by "на децата да
  играят". The four answers stay parallel.
* iaaa-6495 — "освен при: завиване / заобикаляне / изпреварване" = "sauf pour : tourner / contourner / dépasser"
  (three parallel verbs; "changement de direction" would have singled out the first answer).
* iaaa-5627-a3 — "е с предимство" = "bénéficie de la priorité".
* iaaa-6697, iaaa-5846, iaaa-5852 — bare verb answers (diminue / augmente / ne change pas / dépend …), as in the
  Bulgarian.
* "принудително спиране" outside the fixed compounds = "immobilisation forcée" (iaaa-6364, iaaa-6502, iaaa-11588);
  "място за принудително спиране" = "emplacement d'arrêt d'urgence" (iaaa-6478), like "bande / aire d'arrêt
  d'urgence".
* "жп служител / железопътен служител" = "agent ferroviaire"; "машинисти" = "conducteurs de train" (iaaa-6472,
  iaaa-6364). "стаж" = "ancienneté" (iaaa-6682).
* iaaa-8264-a1 — "не обслужва пряко прилежащи територии" = "ne dessert pas directement les propriétés riveraines"
  (Vienna Convention definition of a motorway).
* iaaa-5825, iaaa-5812 — the sign names are the French ones: « Vitesse minimale obligatoire », « Vitesse conseillée ».
* iaaa-5854 — "дължината на спирачния път" = "sa distance de freinage" (the length is already the distance).
* iaaa-6369, iaaa-6371, iaaa-6372, iaaa-6374 — `hint` exceptions: one- or two-word place answers ("на жп прелез",
  "в тунел", "на надлез") become multi-word French terms.

### Part 15

* iaaa-11712-a4 — "130 кkm/h" contains a stray Cyrillic "к"; rendered "130 km/h".
* iaaa-11703, iaaa-11704 — "3 t." (abbreviation dot inside the sentence) = "3 t".
* iaaa-11692 — "леки моторни превозни средства с четири колела от категория АМ" = "quadricycles légers à moteur de
  catégorie AM" (the term of Directive 2006/126/EC for this vehicle).
* iaaa-12060-a3 — "спирам автомобила извън лентата за принудително спиране" is marked correct although the stem
  already says "Спирам, изключвам двигателя и:"; translated literally ("j'arrête l'automobile hors de la bande d'arrêt
  d'urgence"). Doubt for the reviewer: the source may mean something else.
* iaaa-12056-a1 — "в разделителната ивица между платната на релсовия път" = "sur le terre-plein entre les voies
  ferrées" (the video was not available; "платната" is read as the tracks).
* Video and picture questions: the stems keep their fixed French forms — "Как ще постъпите при тази ситуация?" =
  "Comment agirez-vous dans cette situation ?"; "Как трябва да постъпите …" = "Comment devez-vous agir …";
  "Какво трябва да направите при/в тази ситуация?" = "Que devez-vous faire dans cette situation ?"; "Какъв е
  правилният начин на действие …" = "Quelle est la bonne façon d'agir …"; "Какво е правилното действие …" =
  "Quelle est l'action correcte …". First-person answers stay in the first person; the Bulgarian "да + 1st person"
  answers become French infinitives with a first-person pronoun ("m'arrêter", "ma vitesse"); "скоростта си" = "ma
  vitesse", "скоростта" = "la vitesse".
* "съм с предимство" = "j'ai la priorité"; "стоп-палка" = "bâton stop"; "каруца" = "charrette"; "мястото за спиране"
  = "l'endroit où s'arrêter".
* iaaa-6387, iaaa-6273, iaaa-12026, iaaa-6382, iaaa-6396, iaaa-5634, iaaa-6236 — `hint` exceptions (legal formula
  "céder le passage", one-word vehicle names, the fixed term for товарен автомобил).

### Part 16

* iaaa-5828 — the stem has no colon ("На водача на МПС със специален режим на движение"); mirrored without final
  punctuation, each answer completing the sentence.
* With the driver as the subject, "е разрешено да …" = "est autorisé à …" and "е забранено да …" = "se voit interdire
  de …" (iaaa-5828, iaaa-11589), "е забранено да се движи" = "est interdit de circuler" (iaaa-5385).
* Stems that end with the preposition "на:" before bare nouns (iaaa-5390, iaaa-5391, iaaa-5398, iaaa-5399,
  iaaa-11585) end with "interdite aux :" and the answers are bare nouns, as in the Bulgarian.
* "велосипедна пътека" (a cycle crossing, parallel to "пешеходна пътека") = "passage pour cyclistes" (iaaa-5630);
  "велосипедна алея" stays "piste cyclable".
* "Мотопедисти" = "cyclomotoristes"; "проблясваща светлина" = "lumière à éclats" (harmonised in part 23; iaaa-11627-a4
  and iaaa-11628-a3 have the typo "пробляскваща"); "успоредно до друго двуколесно ППС" = "de front avec un autre véhicule à deux
  roues"; "хора с трайни увреждания" = "personnes ayant un handicap permanent"; "таксиметрови автомобили" =
  "automobiles de taxi".
* iaaa-6668, iaaa-6674 — "при условие, че:" = "à condition que :", with the answers in the subjunctive.
* iaaa-11684-a2 ("двиние"), iaaa-6352-a2 ("се намира" for the plural) — typos without effect on the meaning.
* iaaa-5640, iaaa-5602 — `hint` exceptions (multi-word French place terms; the iaaa-5602 answer is the wrong answer of
  iaaa-5607).

### BRIEF correction #1 (автомобилен път)

* "автомобилен път" is the signed road class for motor vehicles (sign E,6a, white car on blue), not an ordinary
  interurban road. It is now "route pour automobiles" (the Vienna Convention FR name of the sign) in the glossary and
  in iaaa-6041 (part 07), iaaa-5164, iaaa-11601, iaaa-11603 (part 08), iaaa-5752 (part 14), iaaa-11711 (part 15),
  iaaa-5391, iaaa-5411, iaaa-5412, iaaa-5413, iaaa-5416, iaaa-5417, iaaa-5418, iaaa-11354 (part 16); the part-20
  questions use it from the start. "скоростен път" stays "route express"; "автомагистрала" stays "autoroute".
  The touched parts were re-linted (0 errors, 0 warnings). Corrections #2–#4 already matched the work.

### Part 17

* iaaa-6356 — the stem ends with "…насрещно движещите се:" before bare nouns; rendered "…, lorsqu'ils viennent en
  sens inverse, aux :" with bare nouns.
* "е с предимство" (third person) = "bénéficie de la priorité" (iaaa-6593, iaaa-6235, iaaa-6305, iaaa-6388), as in
  iaaa-5627; "съм с предимство" (first person) = "j'ai la priorité".
* iaaa-5374, iaaa-5375, iaaa-6069, iaaa-6097, iaaa-9838 — правилно/неправилно agree with "la position" (= correcte /
  incorrecte); in true/false statements they stay correct/incorrect.
* iaaa-12008 — the stem ends with "…, поради?"; mirrored as "… en raison de ?".
* iaaa-11870 — a question written with a final ":" is rendered as a statement stem ("les véhicules indiqués autorisés
  à … sont :"), so that the colon stays and the answers complete it.
* iaaa-6572-a4 — "защото завива наляво" repeats the "защото" of the stem; translated without it.
* iaaa-6232 — "на товарния автомобил / на лекия автомобил" answers "кой от водачите" and is read as "the driver of
  …" = "celui du véhicule de transport de marchandises / de la voiture particulière".
* iaaa-5803 — "автомобилът на спешната медицинска помощ" = "l'ambulance".
* iaaa-5931, iaaa-5935, iaaa-11484 — "правилото за „предимството на дясностоящия”" = « la règle de la « priorité à
  droite » » (the French name of the rule).
* iaaa-12033 — the answers name the action to foresee, as infinitives.
* iaaa-5409-a2 ("раздилителната") — typo without effect.
* iaaa-6559, iaaa-6337 — `hint` exceptions ("céder le passage"; the legal category "véhicule sur rails").
* Harmonised while starting part 18: "с готовност за спиране" was "prêt à freiner" in parts 06, 07, 10 and 11 and
  "prêt à m'arrêter" from part 11 on. It is now "en étant prêt à m'arrêter / à vous arrêter / à s'arrêter"
  everywhere (iaaa-5759, iaaa-12020, iaaa-5775, iaaa-5778, iaaa-6031, iaaa-6030, iaaa-6032, iaaa-5586, iaaa-5589,
  iaaa-5583), because the Bulgarian "спиране" here is stopping (iaaa-6699: "с готовност да спра пред пешеходната
  пътека"). Parts 06, 07, 10 and 11 were re-linted.

### Part 18

* "При тази ситуация с предимство е (водачът на):" = "Dans cette situation, bénéficie de la priorité (le conducteur) :",
  with the subject after the verb, so that the answers stay noun phrases as in the Bulgarian.
* iaaa-6570 — "без предимство / с предимство" = "non prioritaire / prioritaire".
* iaaa-5944, iaaa-5945 — "„правилото на десния”" = « la règle de la « priorité à droite » », like
  "предимството на дясностоящия" in iaaa-5931.
* Picture statements with "съм задължен / трябва да пропусна …" = "je suis tenu de / je dois céder le passage à …";
  answers correct/incorrect.
* iaaa-6261, iaaa-6286 — statements that end with ":" in the Bulgarian keep the colon.
* iaaa-5944, iaaa-12054, iaaa-6512, iaaa-6531, iaaa-6535, iaaa-6515, iaaa-6528 — `hint` exceptions (the glossary
  term "agent réglant la circulation", one-word answers, "céder le passage" against "passer avant").

### Part 19

* iaaa-12037 — the stem is only "При тази ситуация?"; mirrored as "Dans cette situation ?".
* iaaa-5907, iaaa-5881, iaaa-5905 — "е достатъчно само да …" = "il me suffit de …" (the statements are false because
  that one measure is not enough; "suffire" carries the "only").
* iaaa-5405 — "водач, който отмине пътния възел за излизане" = "le conducteur qui a manqué l'échangeur de sortie", so
  that "dépasser" stays reserved for overtaking.
* "теглич" = "barre de remorquage" (iaaa-5730); "успоредно един до друг" = "de front" (iaaa-5633); "е в престой" =
  "est à l'arrêt" (iaaa-11629); "ППС от другия път" = "les véhicules de l'autre route".
* iaaa-5733-a1 ("дължинатана"), iaaa-9837-a4 ("навлизат" for the singular), iaaa-5952-a2/a3 and iaaa-6608-a2/a3
  ("пьтния" with ь) — typos without effect.
* iaaa-6542, iaaa-6544, iaaa-6565, iaaa-6576, iaaa-6702, iaaa-12007, iaaa-6476, iaaa-6612, iaaa-6673, iaaa-6553,
  iaaa-6556 — `hint` exceptions ("céder le passage", the fixed terms for товарен автомобил and регулировчик).

### Part 20

* Correction #1: iaaa-5334, iaaa-6449, iaaa-6707, iaaa-5423 use "route pour automobiles"; iaaa-8279 uses "route
  express". "С този пътен знак се обозначава:" = "Ce panneau désigne :".
* iaaa-7175 — the occasional-service types use the EU French terms: "обиколен превоз при затворени врати" =
  « circuit à portes fermées »; "пълен - празен" = « aller en charge – retour à vide »; "празен - пълен" = « aller à
  vide – retour en charge »; the distractor "обиколен превоз при „отворени врати”" is mirrored (« portes ouvertes »).
* iaaa-7181 — "каботажен превоз" = « transport de cabotage »; iaaa-7180 — "международен превоз" = « transport
  international ».
* "Спирането за престой е забранено:" = "L'arrêt est interdit :"; the plain "спирането" of iaaa-11590 and iaaa-5572 =
  "l'immobilisation" (generic stopping).
* iaaa-5832-a3 — the category is written “В” in Cyrillic; rendered « B ».
* iaaa-5334-a4 ("задължетелен"), iaaa-5797-a3/a4 ("забрананява"), iaaa-5783-a3 ("теглещия") — typos without effect.
* iaaa-5938, iaaa-5613, iaaa-5614, iaaa-5785, iaaa-5546, iaaa-7175 — `hint` exceptions; iaaa-5546-a2, iaaa-5542-a1 —
  `length` exceptions ("спирането за престой" = "l'arrêt").

### Part 21

* Bus transport (T23), following the EU French of Regulation (EC) No 1073/2009 where it exists: "случаен превоз" =
  « service occasionnel »; "совалков превоз" = « service de navette »; "специализиран превоз" = « service régulier
  spécialisé »; "превоз по автобусни линии" = "transport sur les lignes d'autobus"; "утвърдени транспортни схеми" =
  "schémas de transport approuvés"; общинска / областна / републиканска / междуобластна схема = "schéma municipal /
  régional / national / interrégional"; междуселищни / междуобщински / междуобластни линии = "lignes interurbaines /
  intercommunales / interrégionales"; "маршрутно разписание" = "horaire de ligne"; "курс" = "course"; "извънреден
  курс" = "course supplémentaire"; "автогара" = "gare routière"; "автоспирка" = "arrêt d'autobus"; "документ за
  платена превозна цена" = "titre de transport payé"; "табела" on the bus = "plaque".
* Documents: "пътен лист" = "feuille de route"; "пътна книжка" = "carnet de route"; "пътническа ведомост" = "relevé
  des passagers" (kept distinct from "списък на пътниците" = "liste des passagers"); "пътен формуляр" = "formulaire
  de voyage" (kept distinct from the feuille de route).
* Goods (T24): "товародател" = "chargeur"; "изпращач" = "expéditeur"; "получател" = "destinataire"; "спедитор" =
  "transitaire"; "товар" in the CMR questions = "marchandise", otherwise "chargement"; ATP: "специални транспортни
  средства" = "engins spéciaux", "удостоверение за годност" = "attestation de conformité"; "лесноразваляеми / бързо
  развалящи се продукти" = "denrées (alimentaires) périssables".
* iaaa-7094 — the stem lacks the noun after "специализирани"; translated as "services réguliers spécialisés".
* iaaa-7116 — the stem repeats "водачът" at the end; translated once.
* iaaa-6899, iaaa-6900 — "AТР" mixes a Latin A with Cyrillic ТР; rendered "ATP".
* iaaa-6922 — "излиза отстрани на ПС" = "déborde latéralement du véhicule" ("dépasser" stays reserved for overtaking);
  "лишаване от право за управление на МПС" = "privation du droit de conduire des véhicules à moteur" (as in part 08;
  harmonised during part 24).
* iaaa-11672 — "между 6,00 и 21,00 ч." = "entre 6:00 et 21:00".
* Typos without effect: iaaa-11754-a1 ("по-гомяма"), iaaa-7112-a3 ("всики"), iaaa-7163 ("тренспортни"),
  iaaa-6929-a1 ("товарана"), iaaa-6978-a2 ("възражениета"), iaaa-6972 ("може да се извършва").
* iaaa-7195, iaaa-6922 — `hint` exceptions (the long EU term; the one-word answer "глоба").

### Part 22

* "товар, който излиза … на най-издадената част на ППС" = "chargement qui déborde … de la partie la plus saillante
  du véhicule" ("dépasser" stays reserved for overtaking).
* CMR wording: "приемане на товара" = "prise en charge de la marchandise"; "видимото състояние" = "état apparent";
  "точността на данните в товарителницата" = "exactitude des mentions de la lettre de voiture"; iaaa-6990 — "30 jours
  après l'expiration du délai convenu".
* "Спогодбата ADR" = "l'accord ADR" (iaaa-6907); "ADR конвенцията" stays "la convention ADR" (iaaa-6908), as
  written. "Закон за автомобилните превози" = "loi sur les transports routiers". "бруто тегло" = « poids brut »;
  "тара" = « tare ».
* "светлини за движение през деня" = "feux de circulation diurne"; "денонощие" = "le jour ou la nuit"; "в светлата /
  тъмната част" = "pendant la période claire / sombre" (iaaa-6136).
* iaaa-6111 — the question asks whether the reaction time affects "дължината на спирачния път" (the braking distance)
  and the correct answer is "да"; strictly it affects the stopping distance. Translated literally ("distance de
  freinage"). Doubt for the reviewer.
* iaaa-6132-a1 ("предвижва" for "предвижда") — translated as "anticiper"; iaaa-5741-a2 ("може да приема" for "мога")
  — first person kept.
* Typos without effect: iaaa-5739-a2 ("за приеме"), iaaa-5743 ("уравлението"), iaaa-5716 ("продържително"),
  iaaa-5686-a4 ("автомобилитге"), iaaa-6910-a3 ("масата"), iaaa-6916 ("отдзад").
* iaaa-6884, iaaa-6973, iaaa-6924, iaaa-6977, iaaa-6985, iaaa-6984, iaaa-6125, iaaa-5679, iaaa-11634, iaaa-5743,
  iaaa-5723 — `hint` exceptions (one-word answers, CMR wording); iaaa-5679-a4 — `length` exception ("през тъмната
  част от денонощието" = "de nuit").

### Part 23

* Lights: stems ending in "с включени:" = "en ayant allumé :" (iaaa-11631, 5687, 5668, 7024); къси / дълги /
  габаритни / аварийни светлини = feux de croisement / de route / de position / de détresse. "Дневните светлини" in
  quotes (iaaa-11633) = « feux de jour »; "светлини за движение през деня" stays "feux de circulation diurne"
  (iaaa-8285).
* "през тъмната част на/от денонощието" = "de nuit" (iaaa-7006, 7008, 7009).
* Oversize transport (T26): извънгабаритно ППС = "véhicule hors gabarit"; the sign "Извънгабаритно пътно превозно
  средство" = « Véhicule routier hors gabarit »; Агенция „Пътна инфраструктура" = Agence « Infrastructure routière »;
  областно пътно управление = "direction régionale des routes"; ИА „АА" = Agence exécutive « Administration
  automobile » (written out); областен отдел „Пътна полиция" = service régional « Police de la route »; областни
  управители = gouverneurs régionaux; "администрация, управляваща пътя" = "administration gestionnaire de la route".
* iaaa-7012 — the Bulgarian answers are institution names with capitals (also "МВР"); the French answers start with
  capitals too. In iaaa-7014/7015 only a2 ("Агенция …") starts with a capital, in both languages.
* iaaa-7027 — "агенция „Пътна инфраструктура"" is in lower case in Bulgarian; French "l'Agence" (proper name).
* iaaa-6998–7002 — decimal points in the source ("2.8 м") → decimal comma.
* iaaa-7029 — a true/false statement that ends with ":" in Bulgarian; kept.
* iaaa-5714 — "Причина за … са:" (singular noun, plural verb) → "Les causes … sont :" (the plural verb is kept and
  does not reveal how many answers are correct).
* iaaa-6128 — "освежителни напитки, като силно кафе или чай" = "boissons revigorantes" ("rafraîchissantes" would
  suggest cold drinks).
* iaaa-6992, iaaa-6994 — "При коя от изброените …" is singular but has two correct answers; the French mirrors the
  singular ("Pour laquelle des …").
* iaaa-11874-a4 — "не е разрешено, само за автомобили с обща маса над 3,5 t" is ambiguous in Bulgarian; the French
  keeps the same structure ("ce n'est pas autorisé, uniquement pour …").
* iaaa-11635 — "да, но е неправилно" = "oui, mais c'est incorrect" (as in iaaa-11634).
* iaaa-5746 — "упойващо вещество" = "substance enivrante" (as in iaaa-12124).
* iaaa-7004 — "определена за допустима от компетентните органи" = "déclarée admissible par les autorités
  compétentes" (EU wording; see iaaa-5204).
* iaaa-5680, iaaa-6708 — "при значително намалена видимост" = "par visibilité considérablement réduite" (same adverb
  as iaaa-5679).
* iaaa-6110-a2 — "чистачките на предното стъкло" = "essuie-glaces du pare-brise" (the windscreen is named in the
  Bulgarian).
* Consistency edits in earlier parts: "проблясваща" = "à éclats" also in iaaa-11627, 11628 (part 16) and
  iaaa-6912-a4 (part 22). Part 13: the no-break space after « was missing in iaaa-6330, 7382, 7366, 7380, 7373 (two),
  7371, 7372 and 7278-a4; added.
* Typos without effect: iaaa-5724-a4 ("намялява"), iaaa-7062-a3 ("означенато"), iaaa-7004-a4 ("максималната
  масата"), iaaa-7009-a4 ("пред празнични"), iaaa-6992/6994 ("извън габаритно").
* `hint` exceptions: iaaa-11631, 5687, 5668, 7024, 5665 (fixed lighting terms of different lengths), 6138
  (symmetric one-word answers), 6113 (ПТП written out). `length` exceptions: iaaa-7009-a1, 7006-a3 ("de nuit"),
  7014-a4, 7015-a4 (ИА „АА" written out).

### Part 24

* Same-text questions reuse the French of their twins: iaaa-7043/5311 = 7269; 7045 = 7273; 7042 = 7274; 7048 = 7276
  (its a3 "да окаже съдействие за …" = "apporter son concours pour …"); 7047 = 7275; 7053 = 7281; 11429 = 7278;
  7054/7055 = 7282 (without "le conducteur", as in the Bulgarian); 7065 = 5986/5988; 7035–7039, 11828–11831, 11836
  = 5404/5522 ("Ce signe distinctif signale :"); 11835 = 11816. iaaa-7040 "С такъв опознавателен знак" = "Un tel
  signe distinctif".
* Masses (ЗДвП definitions): допустима максимална маса = masse maximale autorisée; технически допустима максимална
  маса = masse maximale techniquement admissible; натоварване на ос = charge sur l'essieu; собствена маса = masse à
  vide; "в (не)натоварено състояние" = "à l'état (non) chargé"; "определена за допустима от компетентните органи" =
  "déclarée admissible par les autorités compétentes" (as in iaaa-7004).
* Bus classes (UNECE Regulation No 107): клас I / II / III / A / B = classe I / II / III / A / B, always in Latin
  letters (the source mixes Cyrillic look-alikes, also in the categories "СЕ", "DЕ", "В", "С"); "площ за стоящи
  пътници" = "aire pour passagers debout"; "обособено място" = "espace distinct"; "освен мястото на водача" = "sans
  compter la place du conducteur" (as "без мястото на водача" in parts 04–07); салон = compartiment voyageurs.
* iaaa-7243 — the statement ends with ".:" (typo); the French ends with ":" only.
* "сгъване" (jackknifing) = « mise en portefeuille » (iaaa-7390, 7391). Brake lines (iaaa-7393): въздуховод
  „захранване" / „управление спирачки" = conduite « alimentation » / « commande des freins ».
* "три еднакви светещи тела … оранжева светлина" = "trois feux identiques émettant une lumière orange" (as in
  iaaa-7303). iaaa-7388 — the stem becomes "Trois feux identiques … signalent :", so that the plural and the singular
  answers both fit.
* "осигуряване … против потегляне" = "empêcher … de se mettre en mouvement" (iaaa-7056–7058); iaaa-7392 "осигурено
  срещу придвижване" = "immobilisée".
* Sanctions: "се наказва:" = "est puni :" (glossary); "с глоба" = "d'une amende"; "с лишаване от право да управлява
  МПС" = "de la privation du droit de conduire des véhicules à moteur" (as in iaaa-7120). iaaa-11738 — "системно"
  (in the ЗДвП, an offence committed three or more times within one year) = "répétée".
* "органите за контрол на МВР" / "контролните органи на МВР" = "les agents de contrôle du ministère de l'Intérieur" (as
  in iaaa-7278); "компетентната служба на МВР" = "le service compétent du ministère de l'Intérieur".
* "двустранен констативен протокол" = "constat amiable" (glossary); "нерегламентирани състезания" = "courses non
  réglementées"; "товаро-разтоварачи" = "manutentionnaires"; "незабавно да спре" = "s'arrêter sans délai" (iaaa-7396).
  iaaa-6922 (part 21) was harmonised to "droit de conduire des véhicules à moteur" like all other questions.
* iaaa-11411 — "платно за насрещно движение" = "chaussée de la circulation venant en sens inverse" (glossary);
  "скоростен път" = "route express".
* iaaa-11839 — "3 500 kg" keeps the Bulgarian digit grouping (with no-break spaces).
* Typos without effect: iaaa-7394 ("беде"), iaaa-7389 ("опастност"), iaaa-7421-a1 ("средсво"), iaaa-11413 (Latin "o"
  in "oрганизира"), iaaa-6918-a1 ("задвижението"), iaaa-7247-a2 ("седящ пътници"), iaaa-7390-a2 ("се задействат …
  от тези"), iaaa-11763 ("превишават"), iaaa-7035-a3 ("всички ремаркетата").
* `hint` exceptions: iaaa-5310 ("през деня" = "de jour"), 6020, 6021 (one-word "аптечка" = glossary "trousse de
  premiers secours").

### Part 25

* Same-text questions reuse their twins: iaaa-5996 = 6888; 5333 = 7045/7273; 5357 = 7054/7055; 5332 = 7276 (a1, a3);
  5319 = 7275; 5354 = 7281; 5304 = 7041; 6012/6013/6014 = 6913/6915/7767; 12059-a3 = 12027-a1 ("je réduis ma vitesse
  de circulation"); 5481/5485/5488/11376 and 5496/5497 share their stems and identical answers.
* Administrative-penal terms (ЗДвП / ЗАНН): фиш = "avis de contravention"; електронен фиш = "avis de contravention
  électronique"; акт (за установяване на административно нарушение) = "procès-verbal (de constatation de l'infraction
  administrative)"; наказателно постановление = "décision de sanction" ("влязло в сила" = "devenue définitive");
  временно отнемане на свидетелството за управление = "retrait temporaire du permis de conduire"; временно спиране от
  движение на МПС = "retrait temporaire de la circulation du véhicule à moteur" (as in iaaa-6854); прекратяване на
  регистрацията = "mettre fin à l'immatriculation" / "cessation d'office de l'immatriculation"; подлежи на обжалване =
  "est susceptible de recours"; немаловажно нарушение = "infraction non négligeable"; поради незнание = "par
  méconnaissance".
* "контролните органи" = "les agents de contrôle"; "представител на контролните органи" / "контролен орган" = "un
  agent de contrôle". "0,5 на хиляда" = "0,5 pour mille" (as in part 22). "принудително спрял" = "en immobilisation
  forcée" (as in part 14).
* Load marking: светлоотразител = "catadioptre"; червен / бял флаг = "drapeau rouge / blanc"; iaaa-6011 follows the
  wording of iaaa-6916.
* iaaa-6018 — the insurance "Каско" = « tous risques » (the French name of comprehensive own-damage cover).
* iaaa-6003 — "туристическо ремарке" = "caravane"; iaaa-5993 "товарно ремарке" = "remorque de transport de
  marchandises".
* iaaa-5305, iaaa-5321 — statements that end with ":" in Bulgarian although they are questions ("кои две …", "кои от
  изброените действия …"); the French is rephrased as a statement ending with ":" ("Les deux infractions … sont :",
  "Parmi les actions suivantes, le conducteur doit entreprendre … :").
* iaaa-11409 — "част 2 / част 1" of the registration certificate = "partie 2 / partie 1" (digits kept).
* iaaa-6002 — "пропускам колоната" = "je laisse passer la file" (letting the queue overtake, not a priority rule).
* iaaa-5994/5995 — "Задължение на водача е превозваният товар: да не закрива … / да е укрепен" = "Il incombe au
  conducteur que le chargement transporté : ne masque pas … / soit arrimé" (subjunctive in every answer); iaaa-5998
  "Задължително изискване е … да не закрива:" = "Il est obligatoire que le chargement transporté ne masque pas :".
* Typos without effect: iaaa-11362-a1 ("всичси"), iaaa-5536-a1 ("трябвада"), iaaa-5339-a2 ("сигнализара"), iaaa-8296
  ("изършено", "пълния размера"), iaaa-8294 ("електроннен"), iaaa-11367 (Latin "o" in "oрганизира"), iaaa-8292-a2
  ("съдържанието … са").
* `hint` exceptions: iaaa-5341 (ПТП participants), 5498 ("акт" = "procès-verbal"), 5509 (glossary terms);
  `end_punct` exception: iaaa-11385-a4 ("лв." = "leva", as in iaaa-11662).
* iaaa-8300 — "хора с трайни увреждания" = "personnes ayant un handicap permanent" (as in part 16).

## UI strings (ui-strings.json)

* 347 keys, 28 of them plurals with the French CLDR forms one / many / other (`--ui`: 0 errors, 0 warnings).
* Tone and form: formal "vous"; buttons in the infinitive as in the French Android system apps (Fermer, Annuler,
  Réessayer, Continuer, Vérifier); titles are nouns; French typography (no-break space before : ; ? ! and inside « »,
  "%1$d %%" with a no-break space).
* Vocabulary: app name "Шофьорски изпит" = "Examen du code" (the French name of the theory test); "Изпитен тест" =
  "Examen blanc" (the usual French term for a mock exam), "тест" = "test"; "упражнение / упражнявам" = "entraînement /
  s'entraîner"; "Отметки / отбелязани" = "Favoris"; "Напредък" = "Progrès"; "Настройки" = "Paramètres" (also inside
  the onboarding sentence that names the tab); "вариант" = "variante", the candidate's "случай" = "situation";
  "зачетен / незачетен" = "validée / non validée"; "предай теста / предаване" = "Remettre le test / remise";
  "Провери" = "Vérifier" (quoted exactly in feature_practice_multi_hint).
* ИААА is written in full ("Agence exécutive « Administration automobile »", glossary). Only the legal notices
  (feature_onboarding_disclaimer, feature_settings_attribution, feature_settings_not_affiliated,
  feature_settings_data_notice) add the Latin acronym "(IAAA)" after the full name and then use "l'IAAA", so that the
  long name is not repeated within one notice; the Cyrillic "(ИААА)" of the attribution cannot stay.
* Category blurbs: C / C1 / CE = "Camions de plus de 3,5 tonnes / Camions jusqu'à 7,5 tonnes / Camion avec remorque".
  In French law a "camion" is a goods vehicle over 3.5 t, which is exactly what these categories cover; the short
  word fits under the category code. The questions keep the glossary term "véhicule de transport de marchandises",
  because there the Bulgarian "товарен автомобил" also covers vehicles up to 3.5 t.
* Plurals: "many" (exact millions, read "un million de …") puts "de" before a noun ("%1$d de points", "%1$d de
  questions", "%1$d de fois"); before an adjective there is no "de" ("%1$d sur %2$d correctes"). Where the quantity is
  the total (%2$d) the noun follows %2$d ("Vous avez répondu à %1$d sur %2$d questions.", "%1$d sur %2$d réponses
  correctes", "Seuil de réussite : %1$d sur %2$d points") or the string becomes a label whose forms are identical
  ("Questions apprises : %1$d sur %2$d", "Lectures : %1$d sur %2$d"), so that every form agrees for any number.
* Statistics captions under a big number use a plural heading form that reads for any value: "questions", "points",
  "pour réussir", "minutes", "réponses en entraînement", "bonnes réponses", "jours consécutifs", "tests réussis",
  "examens blancs", "réussis", "score moyen".
* feature_statistics_chart_title — "за последните %1$d дни" = "sur %1$d jours" (the chart shows the most recent days;
  "les %1$d derniers jours" cannot take the singular form for 1 without sounding wrong).
* feature_settings_privacy_text, feature_settings_attribution, feature_settings_not_affiliated,
  feature_settings_data_notice and core_ui_translation_notice are translated closely ("fait foi" / "font foi" for
  "важи / валидни са").

## Whole check (`--all`)

* Final result: 10420 strings checked, 0 errors, 0 warnings, 123 accepted exceptions; coverage 25/25 parts,
  2476/2476 questions, 7465/7465 answers, labels and UI complete.
* Consistency harmonised in this step: iaaa-11828-a3 / 11829-a3 now read exactly like iaaa-11813-a3 ("…, la longueur
  du véhicule à moteur étant sans importance"); iaaa-7421 uses the glossary term "charge par essieu" like iaaa-11868
  (a duplicate glossary key "натоварване на ос" was removed).
* Typography sweep: eight strings of part 13 lacked the no-break space after « (now added); the "3500 kg" of
  iaaa-11832–11834 got its no-break space.

## Open doubts for the reviewer (summary)

1. УПК in the label "D.zaguba-…-zdvp-i-upk" — read as "удостоверение за професионална компетентност" (certificat de
   capacité professionnelle); please confirm.
2. "пътно платно" = "plate-forme routière" vs "платно за движение" = "chaussée" (BRIEF correction #2 confirms two
   terms; the French road-engineering term "plate-forme" is my choice).
3. iaaa-5295 / 5296 — the Cyrillic picture letters "б", "в" are kept as printed (BRIEF correction #4).
4. "товарен автомобил" = "véhicule de transport de marchandises" (not "camion", which would exclude vehicles up to
   3.5 t); "допустима максимална маса" = "masse maximale autorisée" written in full (not PTAC).
5. iaaa-12126 — the expansion of "КДЦ" ("centre de contrôle et de régulation") is an educated guess.
6. iaaa-12060-a3 — marked correct although it seems to contradict the stem; translated literally.
7. iaaa-12056-a1 — "платната на релсовия път" read as the railway tracks (the video was not available).
8. iaaa-6111 — "дължината на спирачния път" (braking distance) is what the source says; strictly the reaction time
   affects the stopping distance. Translated literally.
9. iaaa-6018 — "Каско" rendered by the French equivalent « tous risques ».
10. iaaa-11738 — "системно" (ЗДвП: an offence committed three or more times in one year) rendered "répétée".

## Review (wave 2)

Every change is logged in `review/fr/changes.json`; these decisions supersede the notes above.

* "автомобилен път" = "route à accès réglementé" (the French name of sign C107, white car on blue), replacing
  "route pour automobiles" in the glossary and in all 18 questions; "route express" and "autoroute" are unchanged.
  iaaa-5334 has a `hint` exception (the term is longer than "une autoroute").
* iaaa-5176–5178: "motorisés" (plain adjective), not "véhicules à moteur" (the МПС term).
* Driving times: "durée de conduite journalière / hebdomadaire" (Regulation (EC) No 561/2006, art. 4 k–l, art. 6);
  "temps de conduite" stays for the generic term.
* Doubt 8 (iaaa-6111): fixed to "distance d'arrêt"; the other "спирачен път" questions keep "distance de freinage".
* Doubts 1–7, 9 and 10: kept as translated.
* Impersonal stems "il faut :" take generic answers ("prêt à s'arrêter", "sa vitesse"); "il incombe au conducteur de
  veiller à ce que …" (iaaa-6888, 5994–5996).
