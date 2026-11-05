# Russian (ru) — translator notes

## General decisions

* Terminology: Russian ПДД, the Russian text of the 1968 Vienna Convention, ЕСТР/AETR. See `glossary.json`.
* ё is written consistently.
* Polite capitalised Вы / Вам / Ваш for the candidate.
* Units in Cyrillic symbols (км/ч, м, мм, кг, т, кВт …).
* Bulgarian "/…/" used as brackets is rendered with Russian round brackets.
* Answers that are spelled identically in Bulgarian and Russian ("да", "вода", "генератора", "стартера" …) trigger the
  lint warning `untranslated`; they are correct Russian and are listed in `lint-exceptions.json`.
* **Road classes (BRIEF correction #1).** "автомагистрала" = "автомагистраль"; "скоростен път" (expressway,
  120 km/h for B) = "скоростная дорога"; "автомобилен път" (the signed road for motor vehicles, white car on blue)
  = "дорога для автомобилей", the name of ПДД sign 5.3. The earlier rendering "автомобильная дорога" (any road in
  Russian) was replaced in all 18 questions (iaaa-6041, 5164, 11601, 11603, 5752, 11711, 5391, 5411, 5412, 5413,
  5416, 5417, 5418, 11354, 5334, 6449, 6707, 5423) with the agreement adjusted.

## Item notes (id — problem — decision)

### Part 01
* iaaa-6164 — source typo "провобуксуващата" — translated as intended: противобуксовочная система (ASR).
* iaaa-7560 — the stem "…би причинило нарушаване на:" with the answers "повишаване/намаляване на …" is
  self-contradictory if read literally ("a disturbance of the reduction of stability"). Translated by intended
  meaning: "…которое привело бы к:" + "повышению/снижению …". The correct/incorrect status is unchanged.
* iaaa-5439 — a question that ends with "." in the source; the period is kept.
* iaaa-5474, iaaa-11656 — "блокиране на двигателя" (oil-pressure warning) = engine seizure: "заклинивание двигателя".
* iaaa-5438 — "хидравлична охладителна уредба" is a liquid cooling system: "жидкостная система охлаждения".
* iaaa-11880, iaaa-11881 — "от 1 март до 15 ноември" / "от 15 ноември до 1 март" share their end dates; rendered
  literally as "с … до …" without deciding whether the end date is included.

### Part 02
* iaaa-7711 — answer a2 reads "неправилнозадните гуми" (a stray "неправилно" glued to "задните гуми") — translated as
  intended: "задними шинами".
* iaaa-7649 — a2 typo "/трансмисиятна" — translated as "силовой передачи (трансмиссии) автомобиля".
* iaaa-7636 — the stem ends with "::" — a single ":" is used.
* iaaa-7693 — "спирачно закъснение" is braking deceleration (Bulgarian "закъснение" = negative acceleration), not a
  delay: "тормозное замедление".
* iaaa-7691, iaaa-7449 — answers that do not fit the stem grammatically in Bulgarian (a verb after "причинява:", "да
  улесни" after "да осигури:") are rendered as nouns so that stem + answer is one sentence; meaning unchanged.

### Part 03
* iaaa-7428, iaaa-7429 — "работният /ходовият/ обем": Russian has only one term, "рабочий объём"; the synonym
  "ходовой" has no Russian equivalent and is not repeated (the alternative "литраж" would hint at the answer "литрах").
* iaaa-7680 — "стабилизираща щанга" rendered literally ("стабилизирующая штанга"), not as the Russian technical
  name "стабилизатор поперечной устойчивости", which would give away the answer "уменьшения бокового крена".
* iaaa-12104 — the correct answer "и двете" (7 characters) can only be rendered as "и то, и другое"; the lint
  `hint` warning is a length artefact (lint exception).
* iaaa-12101 — the stem's "вложката" = "вставка"; the answer "плъзгач" is rendered "ползун" so that the stem word is
  not repeated only in the correct answer.
* ККМ (контактно-кабелна мрежа) is written out as "контактно-кабельная сеть".

### Part 04
* iaaa-12096, iaaa-13476 — the abbreviation "(ККМ)" after the written-out term is not repeated, because the
  Russian text always writes the term out.
* iaaa-12096 — "постоянен(прав)": "прав ток" is only a Bulgarian synonym of "постоянен ток"; rendered "постоянный".
* Tram vocabulary: ватман = вагоновожатый; трамвайна мотриса = моторный вагон трамвая; мономотриса = одиночный
  моторный вагон; колоос = колёсная пара; талиги = тележки; токоснемател = токоприёмник; език (на стрелка) = остряк;
  крайна спирка = конечный остановочный пункт; "Тикет система" = билетная система. Trailer vocabulary: колесар =
  роспуск; съчленено ППС = сочленённое транспортное средство.
* iaaa-13466 — "не, само някои имат / да, всички имат" rendered "нет, только у некоторых / да, у всех".

### Part 05
* **пътно платно ≠ платно за движение.** The pivot glossary treats them as synonyms, but the question bank tests the
  difference (iaaa-5230: "Пътното платно" includes the shoulders, the carriageway and its islands; iaaa-5231 and
  iaaa-5232: the pavement and the shoulder are "част от пътното платно"). Decision: "пътно платно" = "дорожное
  полотно", "платно за движение" = "проезжая часть", everywhere — also where "пътно платно" is used loosely
  (iaaa-7620, iaaa-7690, iaaa-7622, iaaa-7624 in parts 01–03 were updated accordingly). "Проезжая часть" for
  "пътно платно" would make the correct answers of iaaa-5230/5231/5232 wrong under Russian ПДД.
* iaaa-5204 — "допустима максимална маса" keeps the ПДД term "разрешённая максимальная масса"; the Bulgarian
  definition (set by the competent authorities) differs from the Russian ПДД one (set by the manufacturer), but the
  question asks for the Bulgarian definition and the answers are translated literally.
* iaaa-12109 — the stem is a statement followed by "?" in the source; the "?" is kept.

### Part 06
* iaaa-5176, iaaa-5177, iaaa-5178 — mopeds are marked as "моторни" (correct): the plain adjective, broader than МПС.
  Reviewer (wave 2): rendered with the plain adjective "моторными", not "механическими" (the МПС term, which excludes
  mopeds in this translation and in the Vienna Convention RU text); the three stems are identical.
* iaaa-5297–5299 / iaaa-5313–5316 — "намалена видимост" (fog, rain, snow, dusk, dust, smoke) = "недостаточная
  видимость" and "ограничена видимост" (bends, slopes, obstacles) = "ограниченная видимость"; this matches the two
  Russian ПДД definitions exactly.
* iaaa-8214, iaaa-8215 — "бутам (мотопед, велосипед, ППС без двигател)" = "катить"; "водя (животни)" = "вести",
  so the Bulgarian contrast pushing/leading stays visible.
* iaaa-5759 — "Кое от следващите действия" is singular although three answers are correct; the singular is kept
  ("Какое из следующих действий").
* iaaa-6043, iaaa-6049 — the hand signal "за спиране" is rendered "сигнал торможения", the Russian name of that hand
  signal.
* "включване в движението" = "начало движения" (ПДД 8.1).

### Part 07
* iaaa-11575, iaaa-11579, iaaa-11580 — the picture labels A, B, C are written with the identical Cyrillic letters
  «А», «В», «С». The picture confirms the пътно платно/платно за движение decision: C (дорожное полотно) spans the
  pavements as well, B (проезжая часть) is between the kerbs.
* iaaa-5244 — the source writes "ВUS" with a Cyrillic В; the painted word is rendered «BUS» in Latin letters.
* iaaa-8247 — "50 cm3" is kept as "50 см3" (the digit 3 must stay; "см³" would lose it).
* iaaa-5222, iaaa-5254 — "стръмен наклон при изкачване / при спускане" = "крутой подъём / крутой спуск" (the names of
  the Russian signs 1.13/1.14).
* iaaa-5775, iaaa-5778, iaaa-6031, iaaa-5765 — "При тази ситуация трябва:" with first-person answers ("да управлявам")
  is rendered "В этой ситуации я должен:" + infinitives.
* "каруца" = "гужевая повозка" (ПДД term), shortened to "повозка" inside the answers.

### Part 08
* "След този пътен знак:" = "За этим дорожным знаком:"; "Този пътен знак предупреждава за:" = "Этот дорожный знак
  предупреждает о:"; "Този пътен знак сигнализира:" = "Этот дорожный знак сигнализирует:".
* iaaa-11601, iaaa-11602 — "ТОЛ такса" = "плата за проезд"; "винетна такса" = "виньеточный сбор".
* iaaa-11602-a3 — "движение само направо" = "движение только прямо" (Bulgarian направо = straight ahead).
* iaaa-12072, iaaa-5181 — "пътни превозни средства" (the group trams are assimilated to) = "транспортные средства"
  as everywhere; the contrast with "моторни превозни средства" = "механические транспортные средства" is kept.
* iaaa-7079-a3 — the wrong answer repeats "не трябва" after the stem "…не трябва:"; the repetition is kept.
* iaaa-11807 — "Състав от МПС от категория В с допустимата максимална маса над 7000 kg…": it is left open, as in
  Bulgarian, whether the mass refers to the combination.
* Passenger-transport vocabulary: багажна разписка = багажная квитанция; поименен билет = именной билет;
  преотстъпвам = уступать; лиценз на Общността = лицензия Сообщества; карта за квалификация = карта квалификации
  водителя; застраховка „Злополука“ на пътниците = страхование пассажиров «Несчастный случай».

### Part 09
* "товарителница" = "транспортная накладная", the current Russian legal name of the document that evidences a
  contract for the carriage of goods (Устав автомобильного транспорта, ст. 8); "товарно-транспортная накладная" is
  the older, longer name and is not used. With "CMR": "накладная CMR".
* "тахографски лист" = "регистрационный лист" (ЕСТР/AETR term); "дигитален тахограф" = "цифровой тахограф";
  "карта на превозвача" = "карта перевозчика" (literal; the EU calls it the company card).
* "ТИР" (Cyrillic) = "МДП" (Russian official name of the TIR system); the Latin "TIR" of iaaa-6932 stays "TIR".
* iaaa-6964 — "забрана за претоварване" in a consignment note means a ban on transhipment = "запрет перегрузки".
* iaaa-11662 — "лв." is written out ("левов"); the abbreviation period is therefore dropped (lint exception).
* iaaa-6859 — the stem ends with "до:" and every answer starts with "до" again; the duplicate "до" is not repeated
  in the Russian stem.
* "име" = "имя" and "наименование" = "наименование" exactly as in the source, so that right and wrong answers are
  not worded differently (iaaa-6951, iaaa-7214, iaaa-7215; "имената на пътника" = "полное имя пассажира").
* iaaa-6782-a1 — the correct answer repeats "трябва" after the stem "…водачът е задължен:"; kept ("должен …").

### Part 10
* Regulation 561/2006 vocabulary: нормална/намалена/разделена почивка = регулярный/сокращённый/разделённый отдых;
  време на управление = время управления; прекъсване = перерыв; друга работа = другая работа; време на разположение
  = время готовности; "седмица" = «неделя» and "неделя" = воскресенье (iaaa-6727, iaaa-6728); times 00.00/24.00 are
  written 00:00/24:00.
* iaaa-6750, iaaa-6753 — "4.5 часа" (decimal point in the source) is written with the Russian decimal comma.
* iaaa-11621 — both "престоя на таксиметрови автомобили" and "спирането за…" become "остановка …" here; the right/wrong
  status does not depend on the спиране/престой contrast in this question.
* iaaa-12116 — the movable part of an overhead trolleybus switch ("език на стрелката") = "перо стрелки".
* iaaa-12119 — "джоб" at a stop = "заездной карман".
* iaaa-6831 — the CMR convention is given its official Russian title "Конвенция о договоре международной дорожной
  перевозки грузов (CMR)"; iaaa-6723 — AETR is given the official Russian title of ЕСТР.

### Part 11
* Coupling devices (UNECE R55 vocabulary): теглително-прикачно устройство = тягово-сцепное устройство; теглич =
  дышло; ремарке с теглич = прицеп с дышлом; ремарке с шарнирно окачен теглич = прицеп с шарнирно подвешенным
  дышлом; окачени / неподвижно закрепени тегличи = подвешенные / неподвижно закреплённые дышла; ухо = петля;
  ключалка (coupling head, iaaa-7330–7333, 7344) = сцепная головка, but in iaaa-7353 "ключалка" is the lock of the
  fifth wheel = замок; съединителен сферичен болт и носач = сцепной шар и кронштейн; присъединителен (царски) болт =
  сцепной шкворень (кингпин); тип „болт-ухо“ = тип «шкворень — петля»; седлово устройство = седельное устройство;
  монтажна плоча = монтажная плита; опорна тележка = опорная тележка.
* iaaa-6323 — "разрешено да спрете за: престой / паркиране" is rendered "Вам разрешено совершать: остановку /
  стоянку", which avoids the tautology "остановиться для остановки".
* iaaa-6258, iaaa-6260 — a2 "забранено е спирането" (generic stopping) and a1 "престоят и паркирането" both contain
  "остановка" in Russian ("остановка" / "остановка и стоянка"); the answers still differ (начало/конец, with or
  without стоянка), so the right/wrong status is unchanged.
* iaaa-5867 ff. — "на червения автомобил" (= the driver of the red car) is rendered elliptically in the genitive,
  "красного автомобиля", after "Для кого из водителей…".
* iaaa-7339 — a question ending with "." in the source; kept.

### Part 12
* Quoted sign and signal names are translated literally from the Bulgarian (they are the Bulgarian names, not the
  Russian sign names): „Преминаването е забранено/разрешено“ = «Проезд запрещён/разрешён»; „Внимание, спри!“ =
  «Внимание, стой!»; „Премини, ако пътят е свободен“ = «Проезжай, если дорога свободна»; „Пропусни движещите се по
  пътя с предимство“ = «Пропусти движущихся по главной дороге»; „Пешеходна пътека“ = «Пешеходный переход» and
  „Пешеходна алея“ = «Пешеходная дорожка» (two different things); „Движение само надясно…“ = «Движение только
  направо…» (надясно = направо, направо = прямо).
* "забранено е влизането (на …) след знака / срещу знака" = "запрещён въезд … за знак".
* iaaa-6171, iaaa-6173 — the four mass/load answers are kept distinct: маса с товар = масса с грузом; товар = груз;
  товароносимост = грузоподъёмность; натоварване на ос = нагрузка на ось.
* iaaa-5922, iaaa-5923 — "две последователно мигащи една след друга червени светлини" = "два поочерёдно мигающих
  красных сигнала".
* iaaa-5965 ff. — "ППС теглени от животни" = "гужевые повозки" (ПДД term).
* iaaa-6210 — "пътят е без изход" = "дорога не имеет выезда".
* iaaa-5979 — the source stem has no final question mark; none is added.

### Part 13
* **"завиване в обратна посока" = "разворот"** (ПДД term; "завия в обратна посока" = "развернуться", "място за
  завиване в обратна посока" = "место для разворота"). The earlier calque "поворот в обратном направлении" was
  replaced everywhere (iaaa-6064 in part 06, iaaa-5266 in part 08). With "запрещено" the imperfective is used
  ("запрещено поворачивать направо / разворачиваться", iaaa-5871).
* iaaa-6278, iaaa-5194 — "начин за/на паркиране" = "способ постановки … на стоянку", the Russian name of the
  additional plate (8.6.x); iaaa-5194 in part 08 was aligned.
* iaaa-5925 — "луннобяла светлина" = "бело-лунный" (ПДД 6.9). The wrong answer a4 repeats "че" after the stem's
  "че:"; the repetition is not reproduced.
* iaaa-5962, iaaa-5963 — "влизане срещу знака / срещу него" = "въезд за знак / за него", as decided in part 12.
* iaaa-5946 — "водене на домашни животни" = "прогон домашних животных" (ПДД section 25).
* iaaa-6208, iaaa-6215 — "съоръжение за аварийно спиране" = "сооружение для аварийной остановки"; "уширение на
  пътното платно" = "расширение дорожного полотна" (as "уширение на платното" = "расширение проезжей части" in
  iaaa-5258).
* T20 (braking of combinations): "спиране" = "торможение" throughout; terms follow the Russian text of UNECE
  Regulation 13: "кръг" = "контур"; "резервна (аварийна) спирачна уредба" = "запасная (аварийная) тормозная система";
  "спирачна уредба за паркиране" = "стояночная тормозная система"; "инерционно спиране или спиране с „натиск“" =
  "инерционное торможение, или торможение «накатом»" (the Russian technical name of overrun braking; a literal
  "нажимом" is not a Russian term); "контролира степента на приплъзване" (ABS definition, iaaa-7380) = "регулирует
  степень проскальзывания", the R13 wording.
* Source typos translated as intended: iaaa-7370 "средсво", iaaa-7379 "продължителено", iaaa-7381 "трябва се
  осъществява", iaaa-7387 "разедени", iaaa-7266 "темперетурата".
* iaaa-12126 — "диспечер КДЦ": the Bulgarian abbreviation (most probably "контролно-диспечерски център" of the
  public-transport operator) is kept as "КДЦ" because its expansion is not certain.
* iaaa-12128 — the source statement has no final punctuation; none is added.
* iaaa-7266 — "30°С" is written "30 °C" (Russian spacing).
* iaaa-7282 — "пътна помощ" = "помощь на дорогах"; "спешна медицинска помощ" = "скорая медицинская помощь".
* iaaa-7278 — "общината" (the Bulgarian municipality) = "община", the usual Russian name of the Bulgarian unit.

### Part 14
* "жп" (железопътен) is written out: "жп прелез" = "железнодорожный переезд"; "жп служител" = "работник железной
  дороги". The resulting length growth of short correct answers is a lint artefact (iaaa-6369, 6371, 6372).
* "съобразена скорост" = "скорость, соответствующая условиям" (iaaa-5877; later "несъобразена" = "не
  соответствующая условиям").
* "напуснатата (пътна) лента" in the overtaking rules = "ранее занимаемая полоса (движения)" (ПДД 11.1 wording).
* "видимостта е намалена под 50 м" and the term "при намалена видимост (под 50 м)" are both rendered with the ПДД term:
  "при недостаточной видимости менее 50 м" (iaaa-6368, 6369, 5682, 5770; the scene note of iaaa-12070 reads
  "недостаточная видимость менее 50 м из-за тумана"). Reviewer (wave 2): the earlier "видимость снижена менее чем до
  50 м" dropped the term in correct answers while a wrong one kept it (iaaa-5682-a2). Without a threshold the plain
  description stays ("видимость снижена из-за тумана", iaaa-5864-a2; iaaa-11634).
* iaaa-6429-a4, iaaa-6430-a4, iaaa-6431-a4 — the wrong answers repeat "че" after the stem's "че:"; as in iaaa-5925,
  the repetition is not reproduced.
* iaaa-11851, iaaa-11852 — "За престой/паркиране … МПС се спира:" = "Для остановки/стоянки … ставят:", which avoids
  "для остановки … останавливают"; the answers keep the пътно платно/платно за движение contrast.
* iaaa-11731, iaaa-5754 — "е разрешено: / Забранено е:" with noun answers of different genders = "разрешается: /
  Запрещается:" so that every answer agrees.
* iaaa-6498 — the singular "коя от изброените маневри" is kept ("какого из … манёвров") although two answers are
  correct (as in iaaa-5759).
* iaaa-6427 — the space before the final colon is not reproduced.
* iaaa-7272 — a statement followed by "?" in the source; kept.
* iaaa-12051-a2 — "убедиться" has no first-person future form; "преди да се убедя" = "не убедившись".
* iaaa-6600/11587-a4 — "изцапване" (with water or mud) = "забрызгивание".
* iaaa-6697, iaaa-5846 — "намалява" = "снижается" (synonym of "уменьшается"; the longer word would make the correct
  answer stand out by length).

### Part 15
* "паркиран (правилно)" = "(правильно) поставлен на стоянку"; "спрян (правилно) за престой" = "(правильно) совершил
  остановку" (iaaa-5551, 5564, 5566, 5590, 5612, 5634).
* Video items: first-person present answers ("намалявам скоростта") = "снижаю скорость"; "да намаля скоростта" after
  "Какво трябва да направите…?" = infinitive "снизить скорость"; "трябва да намаля…" = "я должен снизить…". The mix of
  forms inside one question is kept as in the source (iaaa-12047, iaaa-12048).
* iaaa-12060-a3 — "спирам автомобила извън лентата за принудително спиране" is marked correct in the source although
  it reads oddly; translated literally ("вне полосы для вынужденной остановки"), status unchanged.
* iaaa-12056-a1 — "между платната на релсовия път" translated literally ("между проезжими частями рельсового пути").
* iaaa-6397, iaaa-6399 — "каруца" = "повозка" (as inside the answers of part 07), in the accusative after
  "обгонять".
* iaaa-6353, iaaa-6351 — "стоп-палка" = "сигнальный жезл".
* iaaa-6240, iaaa-6242 — "радиусът на завоя" (of the corner) = "радиус закругления".
* iaaa-6381, 6380, 6382 — "който се изкачва / спуска по наклона" = "движущийся вверх / вниз по уклону".
* iaaa-5892-a2 — "докато се убедя" = "пока не удостоверюсь" ("убедиться" has no first-person future).
* "Кои от посочените условия е необходимо да бъдат налице…" = "Какие из указанных условий должны быть выполнены…"
  (iaaa-6458, 11684–11686).
* iaaa-6084-a3 — "двата автомобила" (without "и") = "оба автомобиля", like "и двата автомобила".
* Source typos translated as intended: iaaa-11712-a4 "130 кkm/h" = "130 км/ч"; iaaa-5862 "Кой два" = "Какие два";
  iaaa-11684-a2 "двиние" = "движения".

### Part 16
* iaaa-5630 (and iaaa-5610 later) — "велосипедна пътека" is the marked cycle crossing (the rule "на … и на разстояние
  по-малко от 5 метра преди нея" mirrors the pedestrian crossing), so it is "велосипедный переезд", not
  "велосипедная дорожка" (= "велосипедна алея"). Doubt: the term is listed in the open questions.
* iaaa-5640 — "в подлез" (a road underpass) = "под путепроводом" (ПДД 12.4 wording "на … путепроводах … и под ними");
  "пешеходен подлез" stays "подземный пешеходный переход".
* "платното за насрещното движение" on a motorway = "проезжая часть встречного направления"; "лентата за насрещно
  движение" = "полоса встречного движения".
* iaaa-11627, iaaa-11628 — "проблясваща синя и/или червена светлина" = "синий и/или красный проблесковый огонь".
* iaaa-5828 — the source stem has no colon; none is added (each answer starts with "разрешено/запрещено").
* "след кръстовище / пешеходна пътека" (distance after) = "за перекрёстком / за пешеходным переходом".
* iaaa-5563 ff. — "паркирано ППС" = "транспортное средство, находящееся на стоянке"; "спряно за престой" = "совершившее
  остановку".
* iaaa-8284-a1 — "хора с трайни увреждания" = "люди с инвалидностью".
* iaaa-5570-a2 — the wrong answer says "паркиран" although the stem asks about престой; kept ("поставлен на стоянку").

### Part 17
* "пътен знак за осигуряване на предимство" = "дорожный знак, требующий уступить дорогу" (iaaa-5365, 7792, 8274);
  "пътни знаци относно предимството" = "дорожные знаки приоритета".
* "се съобразяват с (условия)" = "учитывать"; "се съобразяват с предписанията / сигналите" (conflicting signals) =
  "руководствоваться" (iaaa-6459, 5940, 5950).
* "е в нарушение" = "совершает нарушение" (iaaa-5649, 5656, 5657).
* iaaa-6232 — "на товарния автомобил, защото навлиза в съседната пътна лента" answers "Кой от водачите…" and means
  the driver of the truck (the correct answer only makes sense this way); rendered "водитель грузового автомобиля, …".
* iaaa-6572-a4 — the answer repeats "защото" after the stem's "защото:"; the repetition is not reproduced.
* iaaa-12008 — the stem ends "…поради?" in the source; the "?" is kept ("…из-за?").
* "предимството на дясностоящия" = «преимущество находящегося справа» (literal, in quotes as in the source).
* "е с предимство / преминавам с предимство" = "имеет преимущество / я имею преимущество" (iaaa-6335, 6575).
* iaaa-5374 ff. — "разположението … е: правилно / неправилно" = "расположение …: правильно / неправильно" (short
  adjective forms, identical to the yes/no words).
* iaaa-5409-a2 — source typo "раздилителната" = "разделительную".

### Part 18
* iaaa-5944, iaaa-5945 — „правилото на десния“ (the colloquial name of priority to the right) = «правило помехи
  справа», the colloquial Russian name; the more descriptive „предимството на дясностоящия“ (part 17) stays literal,
  «преимущество находящегося справа».
* "При тази ситуация с предимство е водачът на:" = "В этой ситуации преимущество имеет водитель:" + genitive answers;
  "… с предимство е:" = "… преимущество имеет:" + nominative answers; "съм с предимство" = "я имею преимущество".
* iaaa-6570 — "синият автомобил, е: без предимство / с предимство" = "не имеет преимущества / имеет преимущество".
* iaaa-6261, iaaa-6286 — statements that end with ":" in the source; the colon is kept.
* "При тази ситуация трябва:" (same text as iaaa-5775 ff.) = "В этой ситуации я должен:" + infinitives.

### Part 19
* iaaa-11629 — the definition "ППС е в престой, когато е спряно за ограничено време:" is rendered "Остановкой считается
  прекращение движения транспортного средства на ограниченное время:" (the ПДД definition pattern; "прекращение
  движения" keeps престой apart from the generic "спиране").
* iaaa-5730 — "тегличът" of a rigid tow (iaaa-5730) is the tow bar, "буксирная штанга" (the trailer drawbar of part 11
  stays "дышло").
* iaaa-5748 — "то трябва да бъде с изправна: кормилна / спирачна / осветителна уредба" = "оно должно иметь в
  исправном состоянии: рулевое управление / тормозную систему / систему освещения" (keeps every answer grammatical).
* iaaa-5760, iaaa-6683 — "теглещото МПС да е от категория, различна от тази на тегленото МПС" = "буксировка
  механическим транспортным средством иной категории, чем буксируемое".
* "авариен сигнал" = "аварийный сигнал" (as a noun) or "аварийная сигнализация" (with "включение / включённой").
* iaaa-12037 — the stem is only "При тази ситуация?"; kept ("В этой ситуации?").
* iaaa-11687 — the quoted plate name „бавнодвижещи се ППС“ = «тихоходные транспортные средства».
* Source typos: iaaa-5733-a1 "дължинатана" = "длина"; iaaa-5952/6608 "пьтния" = "дорожным".

### Part 20
* iaaa-5610 — "велосипедна пътека" = "велосипедный переезд", as in iaaa-5630 (part 16); "в подлез" = "под путепроводом".
* iaaa-7175 — "случаен превоз" = "нерегулярная перевозка"; "обиколен превоз при затворени врати" = «круговая
  перевозка с закрытыми дверями» (also in part 21); the quoted labels „пълен - празен“ / „празен - пълен“ are
  translated literally («полный — пустой» / «пустой — полный»). The quoted answers are kept in the nominative after
  "может быть:" because they are names of transport types.
* iaaa-11590 — "спирането … е: забранено за паркиране" = "остановка …: запрещена для стоянки" (literal; the
  answer contrasts generic stopping with parking as in Bulgarian).
* iaaa-5855 — "стоп-палка" = "сигнальный жезл" (as in part 15).
* iaaa-5832-a3 — the quoted category “В” = «B» (Latin).
* iaaa-6707-a4 — "пътен възел" = "транспортная развязка".
* Source typos: iaaa-5334-a4 "задължетелен"; iaaa-5797 "забрананява".

### Part 21
* Bus-transport vocabulary (Bulgarian Наредба № 33): случаен превоз = нерегулярная перевозка; специализиран превоз =
  специальная регулярная перевозка; совалков превоз = челночная перевозка; обиколен превоз при затворени врати =
  круговая перевозка с закрытыми дверями; транспортна схема (общинска / областна / републиканска / междуобластна) =
  транспортная схема (муниципальная / областная / республиканская / межобластная); маршрутно разписание = маршрутное
  расписание; курс = рейс; извънреден курс = внеплановый рейс; автогара = автовокзал; автоспирка = остановочный пункт
  (спирка = остановочный пункт throughout); междуселищна линия = междугородная линия; правостоящи пътници = стоящие
  пассажиры; пътен лист = путевой лист; пътна книжка = книжка путевых листов; пътен формуляр = путевой формуляр;
  пътническа ведомост = пассажирская ведомость; фактура = счёт-фактура; документ за платена превозна цена = документ
  об оплате проезда; кмет = мэр; областен управител = областной управитель.
* Cargo vocabulary: товародател = грузоотправитель; изпращач = отправитель; получател = получатель; спедитор =
  экспедитор; укрепване на товара = крепление груза; подреждане = размещение; бързо развалящи се / лесноразваляеми
  продукти = скоропортящиеся (пищевые) продукты; удостоверение за годност = свидетельство о пригодности.
* iaaa-6899, iaaa-6900 — the source writes "AТР" with a Latin A and Cyrillic Т, Р; the international abbreviation
  of the agreement is written "ATP" in Latin letters (as ADR).
* iaaa-7116 — the stem ends with a stray repeated "водачът"; it is not reproduced.
* iaaa-6922 — "излиза отстранини на ПС" (typo) = "выступающим сбоку за пределы транспортного средства"; "0.20 м" =
  "0,20 м".
* iaaa-11672-a1 — "между 6,00 и 21,00 ч." = "между 6:00 и 21:00 ч." (the final "ч." keeps the source's final period).
* iaaa-7176, iaaa-7178 — answers that do not continue the stem grammatically in Bulgarian are translated literally.
* Source typos translated as intended: iaaa-11754 "по-гомяма", iaaa-7112 "всики", iaaa-7163 "тренспортни",
  iaaa-6929 "товарана", iaaa-6978 "възражениета", iaaa-7094 (missing "превози").

### Part 22
* "липса на товара" (carrier's liability) = "утрата груза" (the CMR term); "стоката" = "товар"; "товарът се счита за
  изгубен" = "груз считается утраченным".
* "излиза … на най-издадената част на ППС" = "выступает … за наиболее выступающую часть транспортного средства";
  protruding loads are marked "красным флажком / красным огнём / белым огнём" (светлина = огонь, as in the towing
  questions).
* "допълнителна задна светлина за мъгла" = "дополнительный задний противотуманный фонарь"; "допълнителни светлини за
  мъгла" = "дополнительные противотуманные огни"; "светлини за движение през деня" = "дневные ходовые огни";
  "вериги за сняг" = "цепи противоскольжения"; "0,5 на хиляда / промили" = "0,5 промилле".
* iaaa-11639 — "ППС, което е спряно от движение" (an administrative ban on use) = "транспортное средство, которое
  отстранено от движения".
* iaaa-6685, iaaa-5690 — "рязкото подаване на газ" = "резкая подача газа"; "скоростен механизъм" = "коробка передач"
  ("изключването на скоростния механизъм" = "выключение передачи").
* iaaa-6132-a1 — source typo "предвижва" = "предвижда" ("предвидеть").

### Part 23
* "извънгабаритно ППС" = "крупногабаритное транспортное средство" (also the quoted name of the plate); "Агенция „Пътна
  инфраструктура“" = агентство «Дорожная инфраструктура»; "областно пътно управление" = "областное дорожное
  управление"; "ИА „АА“" is written out ("Исполнительное агентство «Автомобильная администрация»").
* iaaa-7004 — same text as iaaa-5204 (part 05); the stem and answer a2 are copied from there.
* Light-switching items: "с включени къси светлини" = "с включённым ближним светом фар"; where the answers are bare
  light names after "с включени:", the stem is turned so that every answer is grammatical ("должны быть включены:",
  "включают:", "двигаться, включив:" + "ближний свет фар / дальний свет фар / габаритные огни").
* iaaa-5663, iaaa-6684 — "светлина за осветяване на задната табела с регистрационния номер" = "фонарь освещения
  заднего регистрационного знака".
* iaaa-6991 — "хладилно или с изотермична надстройка ППС" = "транспортное средство-рефрижератор или с изотермическим
  кузовом".
* iaaa-6996, iaaa-6997, iaaa-7012 — statements ending with "?" in the source; the "?" is kept.
* iaaa-11876 — "влизане срещу пътния знак" = "въезд за дорожный знак" (decision of part 12).
* iaaa-5714 — the plural "са" with a singular subject is not reproduced ("является").
* Source typos: iaaa-5724-a4 "намялява", iaaa-5685-a3 "не по-повече", iaaa-7062-a3 "означенато".

### Part 24
* Same-text items copied from earlier parts: iaaa-7043, 5311 (= 7269), 7045 (= 7273), 7042 (= 7274), 7048 (= 7276),
  7047 (= 7275), 7053 (= 7281), 11429 (= 7278), 7065 (= 5986/5988), 7035–7039 and 11828–11836 (= 5404/5522/7411/
  11813/11814/11820). iaaa-7054/7055 reuse the answers of iaaa-7282.
* Bus classes keep their numerals/letters in Latin: "клас I, II, III, А, В" = "класс I, II, III, A, B".
* iaaa-7326 — "наклон не по-малък: от 5%" cannot be split the same way in Russian ("не менее" takes no "от"); the
  stem ends "с уклоном:" and each answer is "не менее 5% / 8% / 16% / 25%" (same meaning, all answers built alike).
* iaaa-7243 — the source ends with ".:" (typo). Reviewer (wave 2): the stray "." is dropped; the final ":" stays, as
  in the other statements that end with ":" (iaaa-7029, 11638, 11639).
* iaaa-7390 — a statement followed by "?" whose answers start with "когато"; kept as in the source.
* iaaa-11839 — "3 500 kg" keeps the digit grouping ("3 500 кг").
* "лишаване от право да управлява МПС" = "лишение права управления механическим транспортным средством" (literal, as
  in parts 08 and 21); "губи правоспособността си" = "утрачивает право управления".
* "двустранен констативен протокол" = "двусторонний протокол о ДТП"; "клинове" = "противооткатные упоры";
  "въздуховод" = "пневматическая магистраль".
* Source typos: iaaa-7394 "беде", iaaa-7389 "опастност", iaaa-6918 "задвижението", iaaa-7421 "средсво".

### Part 25
* Same-text items copied word for word: iaaa-5996 (= 6888), 12059 (answers shared with the 11997 group), 5304
  (= 7041), 5333 (= 7045/7273), 5357 (= 7054/7055), 5332 (= 7048/7276: stem, a1, a3), 5319 (= 7047/7275), 5354
  (= 7053/7281), 6014/6012/6013 (= 7767/6913/6915). iaaa-5993 uses the wording of iaaa-6855.
* "фиш" (the Bulgarian on-the-spot fine ticket) = "штрафной талон"; "електронен фиш" = "электронный штрафной талон".
  It has to stay different from "квитанция" (iaaa-5498-a3, a fine paid against a receipt) and from "акт" (the act
  that records an administrative violation, kept as "акт"). "наказателно постановление" = "постановление о наказании".
* "временно спиране от движение на МПС" = "временное отстранение механического транспортного средства от движения"
  (as in parts 08/09); "временно отнемане на свидетелството" = "временное изъятие водительского удостоверения";
  "служебно прекратяване на регистрацията" (iaaa-11409) = "принудительное прекращение регистрации" (terminated by
  the authorities, not at the owner's request).
* "светлоотразител" on a protruding load = "световозвращатель" (ПДД 23.4); "червена/бяла светлина" = "красным/белым
  огнём" and "червен флаг" = "красным флажком", as in part 22. "светлинни устройства" = "световые приборы" (as in
  iaaa-6889).
* "туристическо ремарке" (iaaa-6003) = "прицеп-дача", the ПДД term (ПДД 22.8); "товарно ремарке" = "грузовой прицеп".
* "данък МПС" (iaaa-6015-a4) = "транспортный налог", the Russian name of the same tax.
* iaaa-5305 — the answers are statistics categories and are rendered as such: "несоответствие скорости условиям
  движения", "непредоставление преимущества" (for "отнемане на предимство").
* iaaa-5509-a4 "джанта" = "обод" (as in part 01); iaaa-5506-a2 "най-дясната част на платното" = "у правого края
  проезжей части".
* "лв." = "левов" written out (iaaa-5491, 11385, 8294), as in iaaa-11662; the end_punct exception for 11385-a4 is listed.
* Source typos: iaaa-11362-a1 "всичси", iaaa-5536-a1 "трябвада", iaaa-6011 "отдзад", iaaa-8296 "изършено", iaaa-8294
  "електроннен", iaaa-5339-a2 "сигнализара", iaaa-11367 Latin "o" in "oрганизира".

## Labels (labels.json)
* Variant D "загуба на правоспособност по реда на чл. 157, ал. 4 ЗДвП. и УПК" — "УПК" is kept as written: its
  expansion could not be confirmed from the source (most probably "удостоверение за професионална компетентност", the
  professional-competence card of bus and lorry drivers). The stray period after "ЗДвП" is dropped because the law's
  name is written out ("…ч. 4 ст. 157 Закона о движении по дорогам и УПК").

## Interface strings (ui-strings.json)
* 347 strings, 28 of them plurals with the CLDR forms one/few/many/other. The "other" form (fractions) uses the
  genitive singular, as Russian Android resources do.
* Buttons use the infinitive, as Russian Android system apps do ("Закрыть", "Проверить", "Повторить", "Отмена").
* Terms: "упражнение" = "тренировка"; "отметка / отбелязан" = "закладка / в закладках"; "точки" (exam points) =
  "баллы"; "изпитен тест" = "экзаменационный тест"; "предавам теста" (submit) = "завершить тест" (Russian "сдать тест"
  would also mean "pass it"); "издържан / неиздържан" = "сдан / не сдан"; "зачетен" = "засчитан"; "изтеглям" =
  "скачать"; "Напредък" = "Прогресс"; the app name "Шофьорски изпит" = "Экзамен на права".
* After "из" the counted noun is genitive: one/other "из 21 балла / вопроса", few/many "из 22 / 97 баллов / вопросов".
* Where Android picks the plural by %2$d but a word would have to agree with %1$d, the string is built so that it reads
  correctly for every number: "Просмотров: %1$d из %2$d", "Проходной балл: %1$d из %2$d", "Правильных ответов: %1$d
  из %2$d", "%1$d из %2$d правильно".
* Captions under big numbers use a heading-like nominative plural, as the notes ask ("вопросы", "баллы", "минуты",
  "ответы", "дни подряд", "сданные тесты"); "за успех" = "проходной балл".
* ИААА is written out ("Исполнительное агентство «Автомобильная администрация»"), as in the glossary and the questions;
  the legal attribution keeps "(ИААА)" after the full name, as the source does. Reviewer (wave 2): in the interface the
  full name appears only in the onboarding disclaimer (which now adds "(ИААА)") and in the attribution; captions,
  bullets and notices use "ИААА", as the Bulgarian strings do. The questions keep the full name.
* Polite capitalised "Вы / Вас / Ваш", as in the questions.
* 20 lint exceptions: strings spelled the same in Russian and Bulgarian ("Категории", "Настройки", "Назад",
  "Правила", "Раздел", "Трамваи", "Статистика", "Версия %1$s", the few/other forms "%1$d варианта" …).

## Final check
* `--all`: 10448 strings checked · 0 errors · 0 warnings · 336 accepted exceptions; coverage 25/25 parts, 2476/2476
  questions, 7465/7465 answers, labels and UI complete. No consistency warnings remain.

## Open doubts for the reviewer
1. МПС = "механическое транспортное средство" (ПДД 1.2). The current Russian definition includes mopeds; the
   questions that hinge on this (iaaa-5176/5177/5178, BRIEF correction #3) are translated as written.
2. "престой" and the generic "спиране" are both "остановка" in Russian ПДД; where the Bulgarian contrasts them, the
   wording ("совершил остановку" / "остановился") carries the difference.
3. "пътно платно" = "дорожное полотно" (not a defined ПДД term) vs "платно за движение" = "проезжая часть" (BRIEF
   correction #2).
4. Interpretations from the context: "велосипедна пътека" = "велосипедный переезд" (the marked crossing), "в подлез"
   (parking bans) = "под путепроводом"; "срещу знака" and "след знака" are both "за знак".
5. "лишаване от право да управлява МПС" = "лишение права управления механическим транспортным средством" (literal);
   Russian law says "…транспортными средствами".
6. Bulgarian legal instruments without a Russian equivalent: "фиш" = "штрафной талон", "служебно прекратяване на
   регистрацията" = "принудительное прекращение регистрации"; "туристическо ремарке" = "прицеп-дача" (ПДД 22.8).
7. Abbreviations kept because their expansion is uncertain: "КДЦ" (iaaa-12126), "УПК" (labels).
8. Source items that look wrong but were not changed: iaaa-12060-a3 (marked correct), iaaa-5204 (the Bulgarian
   definition of the maximum mass differs from the Russian one), iaaa-7560 (rendered by its intended meaning).

Reviewer (wave 2) decisions: 1 — kept for МПС everywhere, but iaaa-5176/5177/5178 fixed: "моторни" there is the plain
adjective, so the stem says "моторными" (BRIEF #3). 2, 3, 4, 5, 6 — kept (checked in all parts; "пътно платно" is
"дорожное полотно" in all 35 places). 7 — kept; still open (in Russian a bare "УПК" reads as "Уголовно-процессуальный
кодекс"; the expansion should be confirmed). 8 — kept.

Main-agent gate: "УПК" is the driver's certificate of professional competence (Directive 2003/59/EC; Bulgarian
"удостоверение за професионална компетентност"), so the label writes it out with the glossary term
"удостоверение о профессиональной компетентности".

Main-agent gate: iaaa-6111 says «остановочный путь» (stopping distance), not the braking distance: the key counts the
driver's reaction time, so the Bulgarian «спирачен път» is meant as the whole stopping distance there.
