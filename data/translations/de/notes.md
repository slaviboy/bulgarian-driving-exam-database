# German (de) — translator notes

Reviewer notes for the German translation. Format: id — problem — decision.

## General decisions

See `glossary.json` (`_notes`) for the full list. The ones a reviewer is most likely to question:

* ППС = Fahrzeug, МПС = Kraftfahrzeug, автомобил = Kraftwagen (≥ 4 wheels). "Kraftwagen" sounds formal, but it is
  the StVO/FeV word and keeps the three Bulgarian concepts apart. лек/товарен автомобил = Personenkraftwagen /
  Lastkraftwagen, written out as in the StVO (the abbreviations Pkw/Lkw would make those answers shorter than the
  others, a length hint the Bulgarian does not give).
* спиране = Anhalten (any stop, also one forced by traffic; in braking contexts = Bremsen), престой = Halten,
  паркиране = Parken.
* изпреварване = Überholen, заобикаляне = Vorbeifahren, разминаване = Begegnen.
* предимство = Vorfahrt at junctions and on roads; Vorrang elsewhere (narrow sections, pedestrians, rail vehicles,
  vehicles with special signals), as the StVO does.
* банкет = Seitenstreifen; лента за принудително спиране = Standstreifen (kept apart on purpose).
* Road classes (BRIEF correction 1): автомагистрала = Autobahn; автомобилен път = „Kraftfahrstraße“ (the road for
  motor vehicles, StVO Zeichen 331.1, white car on blue); скоростен път = „Schnellstraße“ (expressway, 120 km/h for
  B). The earlier „Landstraße“ (автомобилен път) and „Kraftfahrstraße“ (скоростен път) were replaced in parts 05,
  07, 08, 14 and 15 (iaaa-11743, 6041, 5164, 11601, 11603, 5752, 8280, 11711, 11712).
* Carriageway terms (BRIEF correction 2): платно за движение = „Fahrbahn“; пътно платно = „Straßenkrone“ in every
  question, also in rule questions („möglichst weit rechts auf der Straßenkrone“, „die Straßenkrone hat zwei und
  mehr Fahrstreifen“), so that the two never share a term. „Straßenkrone“ is the German road-engineering word for
  the carriageway together with shoulders and islands, which is the Bulgarian legal definition (iaaa-5230).
* ЗДвП = Straßenverkehrsgesetz (never "StVG", which is the German act).
* Labels: the effective notes ("След 12.12.24г.") become "Nach dem 12.12.24" without the full stop of the
  Bulgarian year abbreviation "г." (the updated lint now recognises this itself, so no exception is needed).
* Labels: D variant "… загуба на правоспособност по реда на чл. 157, ал. 4 ЗДвП. и УПК" — УПК is read as
  "удостоверение за професионална компетентност" (the driver's certificate of professional competence) and
  translated "Befähigungsnachweis" (the 2003/59/EC term). The stray full stop after "ЗДвП" is dropped. A reviewer
  should confirm what УПК means in this variant.

## Source errors translated by their intended meaning

| id | problem | decision |
|---|---|---|
| iaaa-5439 | yes/no question ends with "." | ends with "?" in German (lint exception) |
| iaaa-7560 | "…което би причинило нарушаване на:" does not fit the answers ("повишаване/намаляване на …") | translated as "…, was Folgendes verursachen würde:" so that each answer reads as the consequence, keeping the correct answers a2/a3 correct |
| iaaa-5437 | answers a2/a3 say "Използването … не се използва" (the use is not used) | rendered as "wird nicht praktiziert" (is not practised), the intended meaning |
| iaaa-7711-a2 | garbled "неправилнозадните гуми" (a stray "неправилно" glued to "задните гуми") | translated as "bei den Hinterreifen" (the rear tyres); lint hint exception |
| iaaa-7525 | a question ("Какви видове …") that ends with ":" | kept the ":" (the answers continue it), as the lint and style guide require |
| iaaa-7636 | stem ends with "::" | single ":" |
| iaaa-7691, iaaa-7449, iaaa-7520, iaaa-7544, iaaa-7680, iaaa-7506, iaaa-7438, iaaa-7548 | some answers do not fit the stem grammatically (noun vs. verb phrase, a stray "за") | translated by intended meaning so that every answer completes the stem (style guide §2); where needed the stem's verb was moved into all answers equally (iaaa-7449, iaaa-7544) |
| iaaa-7660-a2 | "2 два пъти в годината" (digit and word duplicated) | "2 (zwei) Mal im Jahr" keeps both |
| iaaa-12105, iaaa-12104, iaaa-12100, iaaa-12097 | ККМ = контактно-кабелна мрежа (overhead contact network of the trolleybus) | "Fahrleitungsnetz" |
| iaaa-7284, iaaa-7296, iaaa-7297 | съчленено ППС | "Gelenkfahrzeug" (literal "articulated vehicle"), not "Sattelkraftfahrzeug": the latter would repeat "Sattel-" from the correct answer "Kraftfahrzeug mit Sattelanhänger", a hint the Bulgarian does not give |
| iaaa-7294, iaaa-7295 | "седлови влекач … полуремаркета": German "Sattelzugmaschine … Sattelanhänger" share the morpheme "Sattel" | unavoidable with the official German terms; kept |
| iaaa-13489 | "входяща стрелка" | read as a facing switch, "spitz befahrene Weiche" (the tongue must lie tight for a train entering from the toe); a tram specialist should confirm |
| iaaa-13491 | answers end with ";" (list artefact) | dropped |
| iaaa-12132-a1, iaaa-13505-a2 | only one answer ends with "." | kept as in the source (no hint either way) |
| iaaa-5230 | definition "Пътното платно включва: банкетите, платното за движение, островите" — here "пътно платно" is broader than "платно за движение" (Roads Act sense), so "Fahrbahn" for both would give "die Fahrbahn umfasst die Fahrbahn" | "пътно платно" = „Straßenkrone“ (German road-engineering term: carriageway + shoulders/verges + islands, excluding ditches), here and in every other question (BRIEF correction 2) |
| iaaa-12109 | stem "… водачът на тролейбус е длъжен?" (a statement turned into a question by "?") | "Wozu ist der Fahrer … verpflichtet, …?" so that it stays a question and the "да …" answers fit |
| iaaa-7627-a2 | garbled "лоша /недобрелектрическа връзка" (= "лоша /недобра/ електрическа връзка") | "schlechter (mangelhafter) elektrischer Verbindung" |
| iaaa-12112 | "звуковия сигнал не работи" (the device) | "die Hupe" (the device), while "звуков сигнал" as a signal stays "Schallzeichen" |
| iaaa-5176, 5177, 5178 | "Кои … пътни превозни средства са моторни?" — mopeds count as correct, trams as wrong | Translator: "Kraftfahrzeuge" (German legal sense: machine-powered, not rail-bound). Reviewer (2026-11-06): changed to „motorisiert“ (BRIEF correction 3, REVIEW point 3): „Kraftfahrzeug“ is the glossary term for МПС, which excludes mopeds, so with it the key taught that mopeds are МПС. The trams stay wrong exactly as in the Bulgarian, where the plain «моторни» has the same tension (a tram has motors too) |
| iaaa-5759 | "Кое от следващите действия …" (singular) with three correct answers | singular kept: "Welche Maßnahme aus den folgenden …" (the pivot asks to keep the number) |
| all | "специален режим на движение" | "Sonderrechte" ("Kraftfahrzeug mit Sonderrechten") |
| iaaa-5230, 11579, 11580, 11575, 5232 (and the definitions of "граница на платното за движение" in part 08) | the bank contrasts "пътно платно" (carriageway + shoulders + islands, Roads Act) with "платно за движение" (carriageway) | "пътно платно" = „Straßenkrone“ in all 34 questions that use it, including the rule questions (first decided only for the definitions; extended by BRIEF correction 2, e.g. iaaa-7620, 7690, 7622, 7624, 6208, 6215, 5933, 6481, 6247, 6237, 11684–11686, 6071) |
| iaaa-5294, 5295, 5296 | picture labels "а.", "б.", "в." (Cyrillic) | „a“ (Latin look-alike); „б“ and „в“ written in Cyrillic exactly as printed in the diagrams (BRIEF correction 4, lint exceptions „cyrillic“) |
| iaaa-12075 | "жълта мигаща или проблясваща светлина" (two kinds of flashing light) | "gelbem blinkendem oder aufblitzendem Licht" to keep both words; elsewhere "жълта/синя проблясваща светлина" = "gelbes/blaues Blinklicht" (StVO) |
| iaaa-5244 | "граница на платното за движение" | "Fahrbahnbegrenzung" (StVO term); the source writes "ВUS" with a Cyrillic "В" — rendered „BUS“ |
| iaaa-7079-a3 | after the stem "… не трябва:" the answer repeats "не трябва да е наказван" (double negative) | translated by intended meaning without the repeated negation ("… bestraft worden sein") |
| iaaa-7077, 7079 | "умишлени престъпления от общ характер" | "vorsätzliche, von Amts wegen verfolgte Straftaten" (the meaning of "от общ характер" = prosecuted ex officio) |
| all | "превозвач" (carrier) vs "транспортно предприятие" (transport company) | "Beförderer" vs "Verkehrsunternehmen", kept apart |
| iaaa-11678 | garbled quotes "“Бавнодвижещо” се е …" | „Langsam fahrend“ ist ein Fahrzeug … |
| iaaa-12121 | a statement ending with "?" and answered "вярно/невярно" | kept as a statement with "?" (German echo question), answers „zutreffend/unzutreffend“ |
| iaaa-6750 | "4.5 часа", "5.5 часа" with a decimal point | German decimal comma ("4,5 Stunden") |
| iaaa-6934 | "Нередовността на товарителницата" | „Mangelhaftigkeit des Frachtbriefs“ (the CMR Art. 4 wording) |
| iaaa-11662 | amounts in "лв." | "Lewa" |
| iaaa-7339 | yes/no question with "ли" that ends with "." | ends with "?" in German (lint exception) |
| T17 (iaaa-7313 … 7367) | coupling-device definitions taken from UN Regulation No. 55 | German terms of the German R55 / Directive 94/20/EC where they exist: теглително-прикачно устройство = „Verbindungseinrichtung“, стандартни/нестандартни = „genormte/nicht genormte“, ухо = „Zugöse“, седлово устройство = „Sattelkupplung“, монтажна плоча = „Montageplatte“, устройства за дистанционно управление / дистанционни индикатори = „Fernbedienungseinrichtungen / Fernanzeigen“, инерционни устройства = „Auflaufeinrichtungen“. теглич = „Deichsel“ (ремарке с теглич = „Deichselanhänger“, шарнирно окачен теглич = „Gelenkdeichsel“), so the Bulgarian link between „теглич“ and „ремарке с теглич“ survives; теглително устройство = „Zugeinrichtung“ |
| iaaa-7331 … 7333, 7330 | „ключалки“ (coupling heads that lock onto the tow ball) | „Kupplungsköpfe“ (literal for R55 "coupling heads"); the official German „Zugkugelkupplungen“ was not used because its „Zug-“ suggests the towing vehicle, which is the wrong answer in iaaa-7332. In iaaa-7353 „ключалка“ is the lock of the fifth wheel: „Verschluss“ |
| iaaa-7353 … 7355 | „присъединителен болт (царски болт)“ | „Kupplungszapfen (Königszapfen)“ instead of the R55 term „Sattelzapfen“: in iaaa-7354 „Sattelzapfen … befestigt an: den Sattelanhängern“ would share „Sattel-“ with the correct answer, a hint the Bulgarian does not give |
| iaaa-7317 | „опорна тележка“ (support dolly under a semi-trailer) | „Untersetzachse“; the different word „колесар“ elsewhere stays „Dolly“ |
| iaaa-7339, iaaa-7362 | „предпазните устройства са задействани“ | „die Sicherungseinrichtungen aktiviert sind“ (R55 English: "the locking devices have engaged") |
| iaaa-5867 … 5841 | „За кой от водачите …? — на червения автомобил“ (the head noun „водача“ is elided) | „für den Fahrer des roten Kraftwagens“, so that the answer fits „Für welchen der Fahrer …?“; the same in all four answers |
| iaaa-5979 | question „Значението на кой от пътните знаци е „…”“ without „?“ | ends with „?“ in German (no lint finding) |
| iaaa-11863 | „3.5 t.“ (decimal point and a stray full stop) | „3,5 t“ |
| iaaa-6171-a2 | garbled „с товар е по-голям от означения“ | rendered like the clean variant in iaaa-6173-a3 („deren Ladung größer als die angegebene ist“) |
| iaaa-6171, 6172, 6173, 6174, 5979, 11868, 5982, 5983 | sign names „Забранено е влизането на …“ | „Verboten ist die Einfahrt von …“ (same word order as the Bulgarian, aligned with part 04: „die Einfahrt von Kraftfahrzeugen mit Anhängern“); маса с товар = „Masse mit Ladung“, товароносимост = „Nutzlast“, натоварване на която и да е от осите = „Last auf einer beliebigen Achse“. During the final check the part-12 strings were found glued („vonFahrzeuge“) by the earlier alignment edit and repaired to „von Fahrzeugen / Kraftfahrzeugen / Lastkraftwagen“ |
| iaaa-5428 | „МПС, принудително спряло на автомагистрала“ | „auf der Autobahn liegengebliebenes Kraftfahrzeug“ (StVO § 15 „Liegenbleiben“) |
| iaaa-5965 … 6170, 5966, 12076 | „На кои от изброените превозни средства е забранено/разрешено да навлизат …?“ | „Für welche der genannten Fahrzeuge ist das Einfahren … verboten/erlaubt?“, so that the answers stay bare plural nouns as in the Bulgarian |
| iaaa-5925-a4 | the answer repeats the stem's „че“ („че към прелеза …“) | not repeated in German |
| iaaa-12126 | abbreviation „КДЦ“ (контролно-диспечерски център) | „Betriebsleitstelle“ (no Cyrillic allowed) |
| iaaa-7266-a1 | „30°С“ with a Cyrillic „С“ | „30 °C“ |
| iaaa-6220, 6238, 6278 | singular subject with a plural verb („знакът … предупреждават / указват“) | singular in German |
| iaaa-7373 | „инерционно спиране“ / спиране с „натиск“ | „Auflaufbremsung“ / Bremsung durch „Schub“ (инерционни устройства = Auflaufeinrichtungen in T17) |
| iaaa-7371, 7372, 7366 | „непрекъснато / полунепрекъснато / автоматично спиране“ (UN R13 definitions) | „durchgehende / halbdurchgehende / automatische Bremsung“ |
| iaaa-6330, 6322 | „изкуствена неравност“ (speed hump) | „künstliche Bodenschwelle“ |
| iaaa-11852, 11851 | the correct „най-вдясно на платното за движение“ against the wrong „най-вдясно на пътното платно“ | the definitional contrast again: „auf der Fahrbahn“ against „auf der Straßenkrone“ (see iaaa-5230) |
| iaaa-7272 | statement ending with „?“ and answered правилно/неправилно | kept as a statement with „?“ (as iaaa-12121) |
| iaaa-5428, 6364 / 6502, 11588 | „принудително спиране / спряло“ | for a broken-down vehicle (motorway, railway crossing) „liegenbleiben“ (StVO § 15); for the tunnel rule, which also covers stops in congestion, „erzwungenes Anhalten“ |
| пътник | „пътниците“ in the general traffic rules (iaaa-6364, 5592) | „Mitfahrer“; in the passenger-transport topics (T16, T21) „Fahrgäste“ |
| iaaa-6429-a4, 6430-a4, 6431-a4 | the answer repeats the stem's „че“ | not repeated |
| iaaa-8264-a4 | Latin „e“ in „e разрешено“ | no effect |
| iaaa-5828 | stem without the final ":" although the answers complete it | mirrored (no colon); the twin iaaa-11589 has the colon |
| iaaa-5630 (and part 20) | „велосипедна пътека“ (the marked crossing for cyclists, parallel to „пешеходна пътека“; the 5 m rule matches iaaa-7809) | „Radfahrerfurt“; „велосипедна алея“ (cycle path) stays „Radweg“ |
| iaaa-5412, 5413, 5599, 5621, 5594, 5602, 5607 | the answers offer „най-вдясно на платното за движение“ and „най-вдясно на пътното платно“ side by side | „ganz rechts auf der Fahrbahn“ against „ganz rechts auf der Straßenkrone“ |
| iaaa-7115 | stem „… е длъжен:“ but answer a3 says „може да издава …“ (may issue) | stem „Für den Fahrer … gilt:“, the obligation moved into a1/a2 („er ist verpflichtet, …“), a3 „er darf …“ — each answer keeps its own modality |
| iaaa-7178 | answer a2/a3 („превозното средство се връща …“) do not continue the stem „… пътуването на групата:“ | „die Fahrt der Gruppe“ moved from the stem into a1, so that all three answers complete „… eine Beförderung, bei der:“ |
| iaaa-7094 | „При извършване на специализирани на деца …“ (the noun „превози“ is missing) | translated as „Sonderformen des Linienverkehrs mit Kindern …“ |
| iaaa-7116 | „водачът“ repeated at the end of the question | not repeated |
| iaaa-6899, 6900 | „AТР“ written with Cyrillic „Т“ and „Р“ | „ATP“ |
| T23 | Bulgarian administrative units: община / област | „Gemeinde“ / „Bezirk“ (областен управител = „Bezirksgouverneur“; републиканска транспортна схема = „landesweites Transportschema“) |
| iaaa-6111 | „Влияе ли времето за реакция … на дължината на спирачния път?“, key „да“ | Translator: literal „Bremsweg“. Reviewer (2026-11-06, REVIEW findings): „Anhalteweg“ (Reaktionsweg + Bremsweg), the intended meaning, because with „Bremsweg“ the key „ja“ would be false; only here — 7696, 5852, 5858, 5849, 5854 keep „Bremsweg“. |
| iaaa-5692, 5690 / 6685 | „изключването на скоростния механизъм“ (taking the gearbox out of gear) / „превключването на скоростния механизъм“ | „das Schalten des Getriebes in den Leerlauf“ / „das Schalten der Gänge“ |
| iaaa-6132-a1 | „да предвижва възможните опасности“ (typo for „предвижда“) | „vorherzusehen“ |
| iaaa-6910 | „общата маса на контейнера и масата на товара“ (garbled double „маса“) | „die Gesamtmasse des Containers und der Ladung“ (as in iaaa-8344-a3) |
| iaaa-6125, 6126, 6127 | „почивка“ in the sense of a short rest stop, not the regulated rest period of T15 | „Rast“ („zur Rast anhalten“); T15 keeps „Ruhezeit“ |
| iaaa-5686 | „подаде сигнал чрез светлините“ | „ein Leuchtzeichen gibt“ (StVO term for a headlight signal) |
| iaaa-11634 | answers „правилно“ / „не е забранено, но е неправилно“ | „richtig“ / „es ist nicht verboten, aber falsch“ |
| iaaa-11874-a4 | „не е разрешено, само за автомобили с обща маса над 3,5 t“ (ambiguous: forbidden only for these, or allowed only for these) | kept literally with the same comma: „es ist nicht erlaubt, nur für Kraftwagen mit einer Gesamtmasse von mehr als 3,5 t“ |
| iaaa-11591 | „габаритна светлина отзад“ (rear position light) | „Begrenzungsleuchte hinten“ (one glossary term for габаритни светлини, as in the Bulgarian; German would also say „Schlussleuchte“) |
| iaaa-5744 | „Трябва ли да се управлява МПС …?“, key „не трябва да се управлява“ (prohibition) | „Darf ein Kraftfahrzeug … geführt werden?“ / „es darf nicht geführt werden“ (glossary: не трябва = darf nicht) |
| iaaa-5714 | „Причина … са:“ (singular noun, plural verb) | „Ursache … ist:“ |
| iaaa-6996, 6997, 7012 | statements ending in „е?“ / „се издава от?“ | turned into real questions („Wie groß ist …?“, „Von wem wird … erteilt?“) so that „?“ is kept |
| iaaa-7243 | statement ends in „.:“ | ends in „:“ (the lint requires the colon of the source) |
| iaaa-7393 | air lines „захранване“ / „управление спирачки“ | „Vorrat“ / „Bremse“, the labels of the German coupling heads (red supply line, yellow brake line); the function is the same |
| T26/T29 (iaaa-7040, 7038, 7039, 7050, 7051) | „опасен товар“ (singular) next to „опасни товари“ (plural, iaaa-5522, 12074) | „gefährliches Gut“ / „gefährliche Güter“, so that the two source forms stay distinct; the sign name „Erkennungszeichen für gefährliche Güter“ stays plural |
| iaaa-5338 | „двустранния констативен протокол“ (without „Европейски“) | „gemeinsamer Unfallbericht“ |
| T27, iaaa-11839, 11762, 11763 | bus classes „клас А / В“, licence classes „категория В / С“, „СЕ“, „DЕ“ typed with Cyrillic letters | Latin „Klasse A / B“, „Klasse B / C“, „CE“, „DE“ |
| iaaa-7392, 7057, 7056, 7058 | „осигурен срещу придвижване“ / „против потегляне“ | „gegen Wegrollen gesichert“ in both cases (the idiomatic German term; „gegen Anfahren“ could be read as „hitting“) |
| T30 (iaaa-5498, 5499, 11385, 11387, 11501, 8294, 8296, 8297, 8299, 11409) | Bulgarian penalty documents: „фиш“ / „електронен фиш“, „акт (за установяване на административно нарушение)“, „наказателно постановление“ | „Strafzettel“ / „elektronischer Strafzettel“, „Protokoll (zur Feststellung der Ordnungswidrigkeit)“, „Strafbescheid“; kept apart because the questions contrast them (fiш vs акт) |
| T30 (iaaa-5491, 5495, 5481 …) | „временно отнемане на свидетелството“ (the document is taken) vs „лишаване от право да управлява“ (the right is withdrawn) | „vorübergehende Abnahme des Führerscheins“ vs „Entzug des Rechts, ein Kraftfahrzeug zu führen“; „спиране от движение“ = „aus dem Verkehr ziehen“ / „Stilllegung“ |
| iaaa-11400-a4 | „има наложено наказание глоба, …“ does not continue the stem „… който управлява моторното превозно средство:“ | „während gegen ihn eine … Geldbuße verhängt ist“ (grammatical, same content) |
| T30 (iaaa-6009, 6007, 6010, 6008, 6011) | „светлоотразител“ | „Rückstrahler“ |
| T30 (iaaa-5993, 6003) | „товарно ремарке“ / „туристическо ремарке“ | „Lastanhänger“ / „Wohnanhänger“ |
| T16 (iaaa-5601, 5593, 5589, 5583, 5579 / 5596, 5595) | „спрелия на спирката трамвай“ (has stopped) vs „спиращия трамвай“ (is stopping); iaaa-5597 contrasts both | „die an der Haltestelle angehalten hat“ vs „die anhaltende Straßenbahn“ |
| iaaa-12037 | stem „При тази ситуация?“ is a fragment (the question word is missing); the answers are first-person actions („намалявам …“, „ускорявам …“) | Reviewer: „Was tun Sie in dieser Situation?“ (intended meaning, style guide) instead of the literal „In dieser Situation?“ |

## Spelling typos in the source (meaning clear, no effect on the translation)

iaaa-6164 провобуксуващата (= противобуксуващата), iaaa-6163-a1 хлъзгъв, iaaa-5483 арматулното,
iaaa-6165-a4 скоросттта, iaaa-7430 Latin "M" in "Mаксималната", iaaa-7443-a3 правволинейното, iaaa-7447 мужду,
iaaa-7649-a2 трансмисиятна (= трансмисията/ на), iaaa-7690-a1 повишавава, iaaa-7685-a2 регулиравка, iaaa-7686-a1
Latin "e" in "eжедневно", iaaa-7691 "на.отделни", iaaa-7484 space before ":", iaaa-7594-a2 генеретора,
iaaa-7602-a2 маслоизмелвателната, iaaa-7630 неоходимо, iaaa-7683-a2 възглавнца, iaaa-7545-a2 продължитерно,
iaaa-7646 Степенноста, iaaa-12094-a2 "с произвежда", iaaa-12105-a2 "малки разстояние", iaaa-12092 Latin "e" in
"eнергия", iaaa-12131 линиии, iaaa-13467-a2 съоражения, iaaa-13462 "част то талигите", iaaa-13478 "да са зареждат",
iaaa-7300 сътав, iaaa-7411…7414-a3 "изклю¬чение" (soft-hyphen artefact), iaaa-7568-a3 уселвател, iaaa-7576-a2
техническаната, iaaa-7738 отварянета, iaaa-7742-a3 "при работи", iaaa-7764-a2 "не се налагат спазване",
iaaa-6052 "трябва сигнализира", iaaa-5294…5296 сигнарлизира, iaaa-5167-a1 Latin "e" in "опасeн", iaaa-7132
Дейсвието, iaaa-8250 "моторни средства" (= моторни превозни средства), iaaa-7128 "превозното средства",
iaaa-5912 Значенето, iaaa-5965-a1 "леки автомоби", iaaa-11868-a2…a4 "Забранено влизането" (without "е"),
iaaa-7370 средсво, iaaa-7379 продължителено, iaaa-7381 "трябва се осъществява", iaaa-7387 разедени (= разедини),
iaaa-7266-a1 темперетурата, iaaa-12126 "събитие ,което", iaaa-6916 отдзад, iaaa-5739-a2 "за приеме", iaaa-5716 продържително, iaaa-5743 уравлението, iaaa-5686-a4 автомобилитге, iaaa-6910-a3 "максималната масата", iaaa-5724-a4 намялява, iaaa-5663-a3 "включен светлина", iaaa-5685-a3 "не по-повече", iaaa-5712 "за водачът", iaaa-6151 риска, iaaa-7062-a3 означенато, iaaa-7004-a4 "максималната масата", iaaa-7394 беде, iaaa-7421-a1 средсво, iaaa-7389 опастност, iaaa-6918-a1 задвижението, iaaa-7247-a2 "седящ пътници", iaaa-7035-a3 "всички ремаркетата", iaaa-11413 Latin "o" in oрганизира, iaaa-11763 превишават, iaaa-7390-a2 "се задействат … тези", iaaa-5536-a1 трябвада, iaaa-11362-a1 всичси, iaaa-8296 изършено, iaaa-8294 електроннен, iaaa-5339-a2 сигнализара, iaaa-11367 Latin "o" in oрганизира.

## UI strings (ui-strings.json)

* 347 keys, 28 plurals with the German CLDR forms one/other; all placeholders kept (`%%` in
  feature_practice_summary_accuracy becomes „%1$d %% richtige Antworten“, with the German space before the per-cent
  sign).
* категория = „Klasse“ in the interface too (nav tab „Klassen“), as in the questions and labels.
* отметка / отбележи / отбелязани = „Markierung“ / „markieren“ / „markiert“ (tab „Markiert“, „Frage markieren“,
  „Markierung entfernen“, „Markierte Fragen“), one word family instead of mixing „Lesezeichen“ and „merken“.
* раздел = „Abschnitt“, изпитен тест = „Prüfungstest“, вариант / случай = „Variante“ / „Fall“, издание (of the
  question bank) = „Ausgabe“, база = „Fragendatenbank“, научени = „gelernt“, зачетен = „gewertet“.
* ИААА: the interface uses the short form „IAAA“; the full name „Exekutivagentur „Automobilverwaltung““ (glossary)
  introduces it in feature_settings_attribution. The questions keep the full name.
* Buttons are infinitives as in German Android apps („Schließen“, „Abbrechen“, „Erneut versuchen“, „Prüfen“,
  „Test abgeben“); „Предишен / Следващ“ = „Vorherige / Nächste“ (the question), „Назад“ = „Zurück“.
* Captions under big numbers (fact_*, home_answered, statistics_*) are number-neutral plurals or adjectives
  („Fragen“, „Punkte“, „Tage in Folge“, „richtig“, „bestanden“).
* Forms that German does not inflect stay identical in one/other („Mal“, „richtig“): core_ui_video_plays,
  feature_examination_rule_video_plays, feature_results_section_correct, feature_statistics_chart_day.
* Theme option „Като системата“ = „Systemstandard“, language option „Като системата“ = „Systemsprache“
  (German Android wording; same Bulgarian, two contexts).

## Whole check (--all)

* Final run: 0 errors, 0 warnings, 86 accepted exceptions, coverage 25/25 parts, 2476/2476 questions,
  7465/7465 answers, labels and UI complete.
* The only consistency warning (iaaa-7035-a1 against iaaa-7411…7414-a1, „ремаркетата, включително и
  полуремаркетата“) was harmonised to „die Anhänger, einschließlich der Sattelanhänger“.
* „nur wenn“ / „nur, wenn“: both comma variants are correct German and occur in different parts; identical
  Bulgarian texts always have identical German (checked by the lint).

## Open doubts for a reviewer

* УПК in the D variant label (read as „удостоверение за професионална компетентност“ = „Befähigungsnachweis“).
* „входяща стрелка“ (iaaa-13489) = „spitz befahrene Weiche“; a tram specialist should confirm.
* жилищна зона = „verkehrsberuhigter Bereich“ (StVO Zeichen 325.1), the closest German equivalent.
* „Kupplungsköpfe“ for the R55 „ключалки“ (iaaa-7330 … 7333) instead of the official „Zugkugelkupplungen“.
* Shared stems „с предимство е …“ use „Vorfahrt“ even where the picture may show a narrow-road or tram situation
  (e.g. iaaa-6365), where the StVO would say „Vorrang“; the stem must be identical across the group.
* „Straßenkrone“ for пътно платно also in rule questions („möglichst weit rechts auf der Straßenkrone“) is
  required by BRIEF correction 2 but is unusual German outside road engineering.
* „Schnellstraße“ for скоростен път: Germany has no statutory road class of that name (it is used colloquially
  and in Austria); chosen because it must differ from „Autobahn“ and „Kraftfahrstraße“.
* област = „Bezirk“ (T23, T26), главен път = „Hauptstraße“.
* iaaa-6111: reaction time and „Bremsweg“ (see the table above).

## Reviewer (wave 2, 2026-11-06)

All 25 parts, the labels and the 347 UI strings were compared with the Bulgarian and the `correct` flags; every
change (40) is logged in `review/de/changes.json`. Final `--all`: 10392 strings, 0 errors, 0 warnings, 87 accepted
exceptions (one added: iaaa-5957-a1 „length“, the StVO sign name is shorter than the Bulgarian one), coverage
complete. Verdicts on the open doubts above:

* УПК = „Befähigungsnachweis“ — kept (the 2003/59/EC term; the source alone cannot settle the abbreviation).
* iaaa-13489 „spitz befahrene Weiche“ — kept: it is the German railway term for a facing switch.
* жилищна зона = „verkehrsberuhigter Bereich“ — kept (StVO Zeichen 325.1 is the functional equivalent).
* „Kupplungsköpfe“ (iaaa-7330 … 7333) — kept, for the hint reason given above.
* Shared „с предимство е …“ stems — „Vorfahrt“ kept. iaaa-6365 (picture: U-turn through the median while the lorry
  comes on the through carriageway) reads correctly with it. Questions with their own stem where the picture
  shows a lane-change conflict, not a junction (iaaa-6234, 6223, 6226), correctly say „Vorrang“.
* „Straßenkrone“ (пътно платно) / „Fahrbahn“ (платно за движение) — kept; checked in every occurrence (no other
  German term keeps the two Bulgarian concepts apart).
* „Schnellstraße“ — kept; all 12 скоростен път and all 18 автомобилен път („Kraftfahrstraße“) occurrences are
  consistent and distinct from „Autobahn“.
* област = „Bezirk“, главен път = „Hauptstraße“ — kept (consistent in T23/T26: Bezirksgouverneur,
  Bezirksstraßenverwaltung, Bezirkstransportschema).
* iaaa-6111 — fixed: „Anhalteweg“ (see the table).

Reviewer decisions applied across the bank:

* iaaa-5176 … 5178: „motorisiert“ instead of the МПС term (see the table).
* StVO sign names where the Bulgarian names the same sign: Zeichen 205 „Vorfahrt gewähren!“, 308 „Vorrang vor dem
  Gegenverkehr“, 125 „Gegenverkehr“, 267 „Verbot der Einfahrt“ (iaaa-5159, 5953, 5954, 5957, 5958, 5960, 5990).
  Descriptive answers and the structured variant sets (iaaa-5200 „Achtung! …“, 6171 … 6174, 5979, 11868, 5982,
  5983, 6196) stay literal so that their answers remain parallel.
* автомобил = „Kraftwagen“ kept: „Pkw“ would be wrong where автомобил also covers lorries and buses, and identical
  Bulgarian needs one rendering.
* временно отнемане на свидетелството = „den Führerschein vorübergehend abnehmen“ everywhere (iaaa-7144, 6854,
  7137, 6845 changed from „vorläufig entzogen“; „Entzug“ stays reserved for лишаване от право);
  временно спиране от движение = „vorübergehend aus dem Verkehr ziehen“ (7144-a2, 6854-a2 aligned).
* Singular stems «Кой / Коя / Кое от …» stay visibly singular where the German verb does not show the number:
  „Welche Maßnahme / Anforderung aus den genannten …“, „Auf welche Art aus den genannten …“ (iaaa-5901, 6889, 5997,
  5695, 5696, 5697, 8282, 6007 … 6010). Stems with a singular verb („Welche der genannten Handlungen ist …“) and
  plural «Кои» stems were left as they are.
* The noun «спирането за престой» = „das Halten“ (iaaa-5703, 5704, 5705, 5305 aligned with the T22 questions);
  the verb «спря(л) за престой» stays „zum Halten angehalten“.
* общинска транспортна схема = „Gemeindetransportschema“ also in iaaa-7263 (part 05); in the adjective list of
  iaaa-12085 „kommunale“ stays (German has no adjective of „Gemeinde-“ in common use).

## Main-agent change at the gate (2026-11-05)

* feature_home_streak, feature_statistics_streak: «Tage in Folge» → «Tage hintereinander» (Android lint read
  «in Folge» as a typo of «infolge»; same meaning).
