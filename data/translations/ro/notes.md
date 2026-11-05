# Romanian (ro) — translator notes

Open questions and decisions for the reviewer. Format: id — problem — decision.

## General decisions

* Terminology follows OUG 195/2002 (Codul rutier), its implementing regulation (HG 1391/2006), the Romanian texts of
  Directive 2006/126/EC and Regulation (EC) No 561/2006, and DRPCIV test usage. See `glossary.json`.
* Stopping: престой = **oprire**, паркиране = **staționare** (Romanian legal pair). „спиране за престой” is rendered
  „oprire” (the Bulgarian „спиране за” adds no meaning in Romanian); „спрян за престой” = „oprit”, „паркиран” =
  „staționat”. „забранени са престоят и паркирането” = „sunt interzise oprirea și staționarea”. When спиране means the
  act of braking (ABS, braking distance) it is „frânare”.
* изпреварване / заобикаляне / разминаване = depășire / ocolire / întâlnire (trecerea pe lângă vehiculul din sens opus).
  Note: the Romanian legal definition of „depășire” also covers passing an obstacle; „ocolire” is therefore used for
  every заобикаляне so that the Bulgarian distinction stays visible.
* ППС = vehicul, МПС = autovehicul (the OUG 195/2002 definition of „autovehicul” excludes mopeds and rail vehicles,
  like the Bulgarian МПС), автомобил = automobil, лек автомобил = autoturism.
* уредба = instalație (instalație de ungere, de răcire, de frânare…), система = sistem (sistem de frânare, sistem
  antiblocare…), so that the Bulgarian pair спирачна уредба / спирачна система stays distinguishable.
* пътно платно ≠ платно за движение. The question bank treats them as different (iaaa-5230: „Пътното платно включва:
  банкетите, платното за движение, островите”; iaaa-5232: „Банкетът е част от пътното платно”). Romanian: пътно платно
  = „platforma drumului” (OUG 195/2002 defines the acostament as the strip between the partea carosabilă and the edge of
  the platforma drumului), платно за движение = „partea carosabilă”. Used consistently, also in technical answers
  („poziția automobilului pe platforma drumului”).
* Dates: „След 12.12.24г.” = „După 12.12.24” (the final „г.” is the Bulgarian year abbreviation); lint exceptions added.

* Bulgarian institutions keep their identity: ИААА = „Agenția Executivă „Administrația Auto”” (in the interface
  „IAAA”, introduced with the full name in the attribution text), МВР = „Ministerul de Interne”, Агенция „Пътна
  инфраструктура” = „Agenția „Infrastructura Rutieră””, община / област = „municipalitate / regiune”. Romanian
  institutions (DRPCIV, prefecturi, județe) are never substituted.
* Lint exceptions (103) are all of the accepted kinds: hint ratios caused by Bulgarian abbreviations (ППС, МПС, жп),
  by one-word Bulgarian terms that are multi-word Romanian legal terms (къси светлини, автомобилен път, аптечка) or by
  case endings (genitive/dative -lor, colour adjectives); length ratios of single-word Romanian terms (întoarcerea,
  oprirea); date notes ending in „г.”; proper-name capitals. Each entry in `lint-exceptions.json` gives its reason.

## Per-question notes

* iaaa-6164 — Bulgarian typo „провобуксуващата” (for „противобуксуващата”) — translated as the anti-slip system (ASR).
* iaaa-6165-a4, iaaa-7443-a3, iaaa-7447, iaaa-5483 — small Bulgarian typos („скоростттa”, „правволинейното”, „мужду”,
  „арматулното”) — translated with the intended words.
* iaaa-5439 — the Bulgarian question ends with „.” instead of „?” (answers да/не) — Romanian ends with „?”; lint
  exception added.
* iaaa-7560 — the Bulgarian stem „…което би причинило нарушаване на:” combined with the answers („повишаване на
  стабилността”, „намаляване на устойчивостта”, „намаляване на управляемостта”) is garbled („would cause an impairment
  of: a decrease of stability”). Translated with the intended meaning „…ceea ce ar duce la:” + „creșterea / reducerea
  stabilității”, „reducerea maniabilității”; the right/wrong status of every answer is unchanged.
* iaaa-5438 — „хидравлична охладителна уредба” (literally „hydraulic cooling system”) means a liquid cooling system —
  „instalație de răcire cu lichid”.
* iaaa-7604, iaaa-7605 — the Bulgarian gives three names (ареометър /денсиметър, гъстотомер/); „денсиметър” and the
  native „гъстотомер” are the same word in Romanian („densimetru”), so Romanian has „areometru /densimetru/”.
* iaaa-7683 — „въздушна възглавница” here is the air spring of a pneumatic suspension, not an airbag — „pernă de aer”.
* iaaa-7680-a1/a3, iaaa-7544-a3 — answers that do not continue the stem grammatically in Bulgarian are nominalised in
  Romanian („îmbunătățirea…”, „stabilizarea…”), content unchanged.
* ККМ (контактна мрежа, trolleybus overhead line, T05) — no Romanian abbreviation; written out as „rețeaua de contact”.
* спирачни челюсти — „saboți de frână” in both drum and disc contexts, as the Bulgarian uses one word for both.
* T06/T08 (tram) — ватман = „vatman” (the Romanian word for a tram driver); where the Bulgarian says водач the
  translation says „conducătorul”. мотриса = „vagon motor”; мономотриса (iaaa-13461) = „tramvai cu un singur vagon
  motor”. Proper names of Sofia transport services („Център за контрол и координация”, отдел „Експлоатация”) are
  translated literally; iaaa-13480 swaps the order („Център за координация и контрол”) and so does the translation.
* iaaa-12138-a3 — „до първа спиркостоянка на маршрута без пътници в нея” (the pronoun can refer to the stop or to the
  tram) — Romanian „până la prima stație de pe traseu, fără pasageri”, keeping it as open as Romanian grammar allows.
* iaaa-7285…7290 — колесар = „cărucior dolly” (converter dolly).
* iaaa-5176…5178 — „Кои … са моторни?” lists mopeds among the correct answers; Romanian „autovehicul” excludes mopeds,
  so the question says „vehicule motorizate”, not „autovehicule”.
* iaaa-5297…5299 vs 5313…5316 — намалена видимост (weather: fog, dusk) = „vizibilitate redusă”; ограничена видимост
  (geometry: bends, crests, obstacles) = „vizibilitate limitată”. The distinction is the point of these questions.
* iaaa-8227, 8226, 8231 — the Bulgarian says „МПС от категория АМ” although mopeds are not МПС; translated literally
  („autovehicule din: categoria AM”).
* iaaa-5294, 5295, 5296 — the picture labels the three countdown markers with the Cyrillic letters „а.”, „б.”, „в.”.
  Romanian text cannot contain Cyrillic and only „а” has an identical Latin letter, so the labels are transliterated
  „a”, „b”, „v” (the standard transliteration, keeping the alphabetical order of the picture).
* iaaa-11575, 11579, 11580 — picture labels A, B, C written with Latin letters (the Bulgarian mixes „А” Cyrillic and
  „B”, „C” Latin).
* мигаща / проблясваща светлина (iaaa-12075, 12073) — „clipitoare” / „intermitentă”, kept distinct.
* разминаване — rendered by its meaning where a bare „întâlnire” would be unclear: iaaa-5541 „la trecerea pe lângă
  copiii bicicliști care vin din sens opus”.
* iaaa-11807 — „Състав от МПС от категория В … над 7000 kg но не повече от 12000 kg” → C1E: correct under Directive
  2006/126/EC (C1E also covers a category-B tractor with a heavy trailer); translated literally.
* iaaa-5381 (and same_text 6484, 6487) — bare „Този знак:” about the vehicle marking for transported children →
  „Acest semn:” (not „indicator”, which in Romanian means a road sign).
* iaaa-7079-a3 — the Bulgarian answer repeats the stem's negation („не трябва: … не трябва да е наказван”); kept as
  written („nu trebuie: … nu trebuie să fi fost sancționat”).
* ТОЛ такса (iaaa-11601, 11602) — the Bulgarian electronic toll; „taxă TOL”.
* iaaa-5238, 5241 — „пътните платна” (plural of пътно платно) = „platformele drumului”, consistent with the
  пътно платно / платно за движение distinction.
* iaaa-7339 — like iaaa-5439, a Bulgarian question written with a final „.”; Romanian uses „?” (lint exception).
* iaaa-6323 — „е разрешено да спрете за: престой / паркиране / престой и паркиране” → „vă este permisă: oprirea /
  staționarea / oprirea și staționarea” (the literal „să opriți pentru oprire” would be a tautology in Romanian, because
  престой = oprire).
* iaaa-5915 — мигаща жълта светлина of a traffic light = „lumina galbenă intermitentă” (the Romanian legal term for
  signals); the „clipitoare / intermitentă” pair is used only where the Bulgarian contrasts мигаща and проблясваща.
* T17 (coupling devices) — UNECE R55 / Directive 94/20/EC Romanian terms: теглич = proțap, ремарке с теглич = remorcă
  cu proțap, шарнирно окачен теглич = proțap articulat, ухо = ochi, ключалка = cap de cuplare (in iaaa-7353 the
  fifth-wheel „ключалка” is a jaw lock → „zăvor”), съединителен сферичен болт = bilă de cuplare, седлово устройство =
  șa de cuplare, присъединителен (царски) болт = pivot de cuplare („king-pin”), опорна тележка = cărucior de sprijin.
* Traffic-controller questions (iaaa-5834…5869) — answers „на червения автомобил” → „pentru conducătorul automobilului
  roșu” (the stem asks „Pentru care dintre conducători…”); all answers use the same pattern.
* iaaa-7495-a2 — „едносезонни и всесезонни масла” = „uleiuri monograde și multigrade” (the Romanian technical terms for
  single-season and all-season viscosity grades).
* iaaa-7700, 7730, 7731 — вътрешна гума / външна гума = cameră de aer / anvelopă exterioară.
* силово предаване (трансмисия) — Bulgarian glosses the native term with the loanword; Romanian: „sistemul de
  transmisie (transmisia)”. механизми за управление на автомобила = „mecanismele de conducere” (direcție + frânare).
* ресори /пружини/ — rendered „arcuri /resoarte/” (two Romanian synonyms, as in the Bulgarian); листов ресор = „arc cu
  foi”; клапанни пружини = „arcurile supapelor” (fixed Romanian term).
* iaaa-7711-a2 — the Bulgarian answer is garbled („неправилнозадните гуми”); translated as intended, „anvelopele din
  spate”.
* iaaa-7636 — the Bulgarian stem ends with a doubled colon „::” — Romanian uses a single „:”.
* iaaa-7612 — the Bulgarian writes the headlamp marking letter with Cyrillic „С”; the marking is the Latin letter C.
* iaaa-7580-a2 — „регулатор /клапан/ за налягане - балансьор” — „regulatorului /supapei/ de presiune – balansierul”
  (the Bulgarian trade name kept as a loan).
* iaaa-7529-a1 — „кормилно колело /волан/” = „volan” (Romanian has one term).
* iaaa-7449-a3, iaaa-7520-a2, iaaa-7644-a3 — the Bulgarian answer does not continue the stem grammatically; Romanian
  rephrases it so that stem + answer is one sentence, without changing the content.
* iaaa-7278-a4 — the Bulgarian writes the agency's name in lower case („изпълнителна агенция „Автомобилна
  администрация””) because the answer continues the stem; Romanian capitalises the proper name: „Agenției Executive
  „Administrația Auto””.
* iaaa-7273 — „Предприемането на кое от изброените действия е най-важно…” = „Care dintre acțiunile enumerate este cea
  mai importantă…”; the nominalisation „предприемането” is dropped, the meaning is unchanged.
* iaaa-12126 — КДЦ (контролно-диспечерски център) is spelled out: „centrul de control și dispecerat” (no Romanian
  abbreviation exists).
* iaaa-7044 — „обезопасяване на превозното средство” = „securizarea vehiculului”, not „asigurarea”, which a learner
  could read as insurance.
* iaaa-7368 / iaaa-7369 — влекач = „autotractor” when it pulls a semitrailer (articulated vehicle) and „vehiculul
  trăgător” when it pulls a trailer (road train), the same split as in the T17 questions.
* iaaa-5925-a4 — the Bulgarian answer repeats „че” after the stem's „че:”; dropped in Romanian.
* Bulgarian typos translated as intended: iaaa-6220 / 6238 „предупреждават” and iaaa-6278 „указват” (plural verbs
  for one sign), iaaa-7370 „средсво”, iaaa-7379 „продължителено”, iaaa-7381 „трябва се осъществява”, iaaa-7387
  „разедени” (= разедини), iaaa-7266 „темперетурата” and „30°С” with a Cyrillic С (Romanian „30°C”).
* iaaa-12128 — the Bulgarian statement has no final full stop; Romanian keeps it without one.
* iaaa-11851 / iaaa-11852 — „За престой / За паркиране … МПС се спира:” = „Pentru oprire / Pentru staționare …
  autovehiculul se poziționează:”; „se oprește” would give the tautology „Pentru oprire … se oprește”.
* iaaa-7281-a1 — „спешни и аварийни обаждания” = „apeluri de urgență”: Romanian uses one term for both.
* iaaa-6472 — „жп прелез” = „trecere la nivel cu calea ferată”, plain „прелез” = „trecere la nivel”, as in the
  Bulgarian.
* iaaa-6498-a2 — „завиване в обратна посока” is the single Romanian word „întoarcerea”.
* Bulgarian slips translated as intended: iaaa-8264-a4 (Latin „e” in „e разрешено”), iaaa-6429-a4 (repeated „че”),
  iaaa-6427 (space before the colon), iaaa-12035-a2 („зеленият” for „зеления”), iaaa-7267 („водачът” for „водача”).
* iaaa-12060 — the correct answer „спирам автомобила извън лентата за принудително спиране” („opresc automobilul în
  afara benzii de urgență”) is translated literally although it reads oddly after the stem „Спирам, изключвам
  двигателя и:”; it is a video question that could not be checked. „Спирам, изключвам двигателя” = „Opresc, închid
  motorul” (avoids „opresc, opresc motorul”).
* iaaa-12056-a1 — „разделителната ивица между платната на релсовия път” (video question) = „zona mediană cu șine
  dintre părțile carosabile”, keeping it neutral between tram and railway tracks.
* iaaa-6353-a1 — „лесно забелязващ се предмет” = „obiect ușor de observat” (not „ușor vizibil”, which can read as
  „barely visible”).
* iaaa-11712-a4 — the Bulgarian unit „кkm/h” (Cyrillic к) is a typo for km/h; iaaa-11684-a2 „двиние” = движение;
  iaaa-6098 has a Latin „a” in „прaвилно”.
* iaaa-11684 / 11685 / 11686 — „пътното платно да е с две и повече пътни ленти” = „platforma drumului să aibă două
  sau mai multe benzi”, following the пътно платно / платно за движение distinction.
* велосипедна пътека (iaaa-5630) — in Bulgarian this is the marked crossing for cyclists, the counterpart of
  „пешеходна пътека”, so it is „trecere pentru bicicliști”; „велосипедна алея” stays „pistă pentru biciclete”.
* iaaa-5828 — the Bulgarian stem has no colon although the answers continue it; Romanian keeps it without one.
* iaaa-5403 / iaaa-8276 — „На автомагистрала / скоростен път е забранено:” with answers of mixed gender = „Pe
  autostradă / Pe drumul expres se interzice:”.
* iaaa-5647 — „детските заведения” = „instituțiile preșcolare” (nurseries and kindergartens).
* iaaa-5648-a3 — Bulgarian „2.5 м” = „2,5 m”.
* „разрешаващ / забраняващ сигнал” = „semnal care permite trecerea / semnal care interzice trecerea” (glossary),
  also in iaaa-5828, 5822, 11589 (part 16) and iaaa-5803, 5935, 11484 (part 17).
* iaaa-12008 — the Bulgarian ends a stem with „поради?”; Romanian turns it into a real question („Din ce cauză nu
  trebuie să încep depășirea în această situație?”) so that the „?” is kept and the answers read naturally.
* iaaa-5374 / 5375 / 6069 / 6097 / 9838 — „правилно / неправилно” agree with „poziția” („corectă / incorectă”).
* iaaa-6572-a4 — the Bulgarian repeats „защото” after the stem's „защото:”; dropped. iaaa-5409-a2 „раздилителната” is
  a typo for „разделителната”.
* iaaa-5944 / 5945 — „правилото на десния” = „regula priorității de dreapta”, the Romanian name of the same rule
  („предимството на дясностоящия” in iaaa-5931).
* iaaa-6261 / 6286 — the Bulgarian statements end with „:” instead of „.”; Romanian keeps the colon.
* Part 18 — the many two-answer priority questions keep the same frame as part 17: „trebuie să acord prioritate X” /
  „să trec înaintea X”; colour adjectives and genitive/dative endings make several correct answers longer (accepted
  hint exceptions, no cue).
* iaaa-12037 — the Bulgarian stem is only „При тази ситуация?”; Romanian keeps it as „În această situație?”.
* iaaa-5730 — „теглич” for a rigid tow bar between two cars = „bara de tractare” (the T17 drawbar of a trailer stays
  „proțap”).
* iaaa-11629 — „е в престой, когато е спряно” = „se consideră oprit când este imobilizat”, to avoid „oprit … oprit”.
* iaaa-5405 — „отмине пътния възел” = „a trecut de nodul rutier” (not „a depășit”, which means overtaking).
* iaaa-5952 / 6608 — the Bulgarian writes „пьтния” with a Cyrillic soft sign; iaaa-5733 „дължинатана”; iaaa-9837
  plural „навлизат” — typos, translated as intended.
* iaaa-6562-a3 — „мотоциклетистът е с предимство, защото е двуколесно МПС” = „…deoarece conduce un autovehicul cu două
  roți” (the motorcyclist is not himself a vehicle).
* iaaa-6484 / 6487 — same_text with iaaa-5381, so the bare stem „Този знак:” stays „Acest semn:” although these are
  tunnel signs.
* BUS lane — „banda „BUS”” with Romanian quotes everywhere (iaaa-5234, 6446, 9835, 9840).
* iaaa-5334-a4 „задължетелен” and iaaa-5797 „забрананява” are Bulgarian typos; iaaa-11590 „Спирането … е забранено за
  паркиране” is kept literally („Oprirea … este interzisă pentru staționare”).
* iaaa-7175 — „превоз по автобусни линии” is kept literally („transport pe linii de autobuz”); „специализиран превоз” =
  „transport regulat special” (Regulation (EC) No 1073/2009 terminology, as in the glossary).
* Bulgarian administrative units (T23): община = „municipalitate” (общински = „municipal”), област = „regiune”,
  областен управител = „guvernator regional”, републиканска транспортна схема = „schema de transport națională”.
  Romanian „comună / județ / prefect” are avoided because they are Romanian institutions with other boundaries.
* „пътническа ведомост” (the passenger form of occasional transport) = „listă de pasageri”, kept distinct from
  „списък на пътниците” = „lista pasagerilor” (iaaa-7099, 7108) and from „пътен формуляр” = „formular de călătorie”.
* ADR / ATP — the Bulgarian calls both „конвенция”; Romanian uses their real names „Acordul ADR / Acordul ATP”
  (iaaa-6908, 6899, 6900; the Bulgarian 6899 / 6900 write „AТР” with a Cyrillic Т).
* iaaa-6888-a2 „застрахован” = „acoperită de o asigurare” (not „asigurată”, which would also read as „secured”).
* iaaa-7094 — the Bulgarian omits „превози” after „специализирани”; translated as intended. iaaa-7116 repeats
  „водачът”; iaaa-11754 „гомяма”, iaaa-7163 „тренспортни”, iaaa-6929 „товарана”, iaaa-6978 „възражениета”,
  iaaa-6922 „отстранини” are typos.
* iaaa-11672 — „между 6,00 и 21,00 ч.” = „dintre ora 6:00 și ora 21:00”.
* T24 — „товар” is „încărcătura” throughout (also in the CMR liability questions), „стока” = „marfa”; „видимото
  състояние на товара” = „starea aparentă a încărcăturii” (CMR wording).
* iaaa-6132 — „предвидлив” = „prevăzător” (anticipating dangers), not „previzibil”; the Bulgarian answer has the typo
  „предвижва” for „предвижда”.
* iaaa-11634-a2 „не е забранено, но е неправилно” = „nu este interzisă, dar este greșită” (agreeing with „folosirea”).
* iaaa-6111 — the Bulgarian says the reaction time affects the braking distance („спирачния път”); translated
  literally („distanța de frânare”) although strictly it is the stopping distance.
* iaaa-6123 / 11638 — „0,5 промили / 0,5 на хиляда” = „0,5 la mie”.
* iaaa-7012-a4 — the Bulgarian capitalises „Областните управители …” like the three proper names before it; Romanian
  keeps the capital („Guvernatorii regionali …”) so the four answers look alike.
* iaaa-6996 / 6997 / 7012 — the Bulgarian stems end with „?” although they are sentence stems; Romanian rephrases them
  as real questions („Care este lungimea maximă admisă…?”, „De cine se eliberează…?”).
* iaaa-11874-a4 „не е разрешено, само за автомобили с обща маса над 3,5 t” is ambiguous in Bulgarian; kept with the
  same comma („nu este permisă, numai pentru automobilele …”).
* iaaa-7021-a2 — „знак „Внимание! Други опасности”” = „indicatorul „Atenție! Alte pericole”” (sign name translated
  literally).
* iaaa-7243 — the Bulgarian ends the statement with „.:”; Romanian keeps the colon only.
* iaaa-7390 — „При спиране на състав „влекач – ремарке” има вероятност той да се „сгъне”?” has „when” answers; Romanian
  adds „în ce caz” so that the question matches its answers. „сгъване” = „frângere” (jackknifing).
* iaaa-7326 — „на път с наклон не по-малък: от 5% …” = „cu o pantă nu mai mică: de 5% …” (the „de” stays in the
  answers, as „от” does in Bulgarian).
* Same_text with earlier parts reused verbatim: iaaa-7043 / 5311 (= 7269), 7045 (= 7273), 7042 (= 7274), 7047 (= 7275),
  7048 (= 7276), 7053 (= 7281), 11429 (= 7278), 7065 (= 5986), 7035–7039 / 11828–11836 (= 5404, 5522), 11592 (= 5420),
  7004 (= 5204), 11832–11835 (= 11816).
* iaaa-7054 / 7055 — the stem is impersonal („може да се получи помощ”), unlike iaaa-7282 („водачът може да получи”);
  the answers are identical.
* iaaa-5503 — „контролни точки” = „puncte de control” (Bulgarian points system, glossary).
* iaaa-6888 / 5996 / 5994 — „застрахован” = „asigurată printr-o poliță de asigurare”: plain „asigurată” would also
  read as „secured”, and 5996 has „покрит” = „acoperită” (covered) as another answer.
* iaaa-6002 — „спирам и пропускам колоната” = „opresc și las coloana să treacă” (letting a queue pass is not a
  priority situation, so „a acorda prioritate” is not used here).
* T30 sanctions — „акт” = „proces-verbal”, „фиш / електронен фиш” = „fișă / fișă electronică”, „наказателно
  постановление” = „decizie de sancționare”, „прекратяване на регистрацията” = „anularea înmatriculării”,
  „временно спиране от движение” = „retragerea temporară din circulație” (as in iaaa-7144), „лв.” = „leva”.
* iaaa-11400-a4 — the Bulgarian answer does not continue the stem grammatically; translated as written.
* iaaa-11409 — „част 2 / част 1 на свидетелството за регистрация” = „partea a 2-a / partea 1 a certificatului de
  înmatriculare” (the two parts of the Bulgarian registration certificate).

## Interface (ui-strings.json)

* Formal address and the Romanian Android button style (polite imperative: „Verificați”, „Anulați”, „Încercați din
  nou”, „Continuați”); tabs are nouns („Acasă”, „Categorii”, „Progres”, „Marcaje”, „Setări”).
* App name „Examen auto” (the usual Romanian name for the driving test, 11 characters).
* Plurals use the three Romanian CLDR forms: one „1 punct”, few „2–19 puncte”, other „20 de puncte”. The plural is
  chosen by the placeholder named in the source note (e.g. the maximum points %2$d). core_ui_video_plays and
  feature_results_section_correct have the same text in all three forms because their noun does not follow the number
  that selects the form („Vizionări: %1$d din %2$d”, „%1$d din %2$d corecte”).
* Statistics captions under a big number are number-neutral plurals („întrebări”, „puncte”, „zile la rând”, „teste
  promovate”).
* feature_practice_multi_hint quotes the button exactly as feature_practice_check („Verificați”).
* The legal texts (privacy, attribution, not-affiliated, data notice) are translated closely, without additions.

## Final check

* `--all`: 2476/2476 questions, 7465/7465 answers, labels and UI complete; 0 errors, 0 warnings, 103 accepted
  exceptions. The last two consistency warnings (iaaa-12022 / 12036 and iaaa-11820 / 11836) were harmonised to the
  earlier wording.

## Open doubts

* Questions with video only (iaaa-12056, 12060 and the other video questions) could not be checked against the
  pictures; they are translated literally. iaaa-12060-a3 („спирам автомобила извън лентата за принудително спиране”) is
  marked correct although it reads oddly after the stem.
* iaaa-6111 says the reaction time affects the braking distance; kept literal, a reviewer may prefer „distanța de
  oprire”.
* „пътническа ведомост” = „listă de pasageri” and „специализиран превоз” = „transport regulat special” follow EU
  terminology; a reviewer with Bulgarian transport-law practice may want to confirm them.
* „temporarily withdrawn licence” wording: „временно отнемане на свидетелството” = „reținerea temporară a permisului”
  (Romanian administrative measure with the same effect); „лишаване от право да управлява” = „privarea de dreptul de a
  conduce autovehicule” (kept distinct from the Romanian „suspendarea exercitării dreptului de a conduce”).

## Main-agent changes at the gate (2026-11-05)

* iaaa-5295, iaaa-5296: the picture labels are the Cyrillic letters «б» and «в», exactly as printed in the diagrams
  (m-cb1c77ae4c1579b5, m-5079445745749caf); a transliterated or positional letter cannot be found in the picture.
  Lint exceptions added (check "cyrillic"), as in English.
