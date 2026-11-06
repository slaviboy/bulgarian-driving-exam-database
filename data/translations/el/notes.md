# Greek (el) translation notes

Decisions and open questions for the reviewer. Format: id — problem — decision.

## General decisions

* Terminology follows the ΚΟΚ and the Greek EU texts; see `glossary.json` (`_notes`).
* ΚΟΚ defines **στάση** as the stop for boarding/alighting or loading/unloading (the Bulgarian **престой**) and
  **στάθμευση** as any longer stop (**паркиране**). The general Bulgarian **спиране** is rendered as
  **ακινητοποίηση** (verb σταματώ); when спиране means braking it is **φρενάρισμα / πέδηση**.
* **разминаване** (meeting oncoming traffic) is the ΚΟΚ **διασταύρωση**, always written with «με (αντίθετα
  κινούμενο) όχημα» so that it cannot be read as an intersection (кръстовище, also διασταύρωση in ΚΟΚ).
* **предавка** (gear) → **σχέση μετάδοσης**, because Greek ταχύτητα would be ambiguous between speed and gear.
* Bulgarian Road Traffic Act (ЗДвП) → «Νόμος για την Οδική Κυκλοφορία», never «ΚΟΚ», to avoid suggesting Greek law.
* **пътно платно ≠ платно за движение.** The pivot glossary lists them as synonyms, but the bank tests the
  difference (iaaa-5230: «пътното платно включва: пътните банкети, платното за движение, островите»; iaaa-5231,
  iaaa-5232, iaaa-5241, iaaa-11575/11579/11580). пътно платно → «κατάστρωμα της οδού» (the ΚΟΚ term for the part
  of the road that contains the carriageway and the shoulders); платно за движение → «οδόστρωμα». Applied everywhere,
  including the technical questions of parts 01–03.

## Labels

* variants (all) `effective_note` — «След 12.12.24г.»: the final full stop belongs to the Bulgarian abbreviation
  «г.» (year) — rendered «Μετά τις 12.12.24» without a stop.
* `D.s-pravosposobnost-za-kategoria-s1-s-i-kategoria-v-sas-stazh-2g` — «със стаж 2г.» — rendered «με εμπειρία 2 ετών»
  (стаж = years of experience as a licensed driver); the final stop belongs to «г.».
* `D.zaguba-na-pravosposobnost-po-reda-na-chl-157-al-4-zdvp-i-upk` — «ЗДвП. и УПК»: the stop after ЗДвП is a typo;
  УПК is read as «удостоверение за професионална компетентност» → «πιστοποιητικό επαγγελματικής επάρκειας», kept in
  the nominative so that the Greek stays as open as the Bulgarian («загуба … и УПК»). **Open doubt**: if УПК means the
  driver CPC (карта за квалификация), the Greek should be «πιστοποιητικό επαγγελματικής ικανότητας (ΠΕΙ)».
* topic `vidove-avtobusni-prevozi-transportni-shemi` — «транспортни схеми» (approved sets of routes and timetables) →
  «σχέδια δρομολογίων».

## Questions

* Obvious Bulgarian typos are translated by their intended meaning (e.g. iaaa-6164 «провобуксуващата» =
  противобуксуващата, iaaa-6163 «хлъзгъв», iaaa-6165 «скоросттта», iaaa-5483 «арматулното», iaaa-7443
  «правволинейното», iaaa-7447 «мужду», iaaa-7430 starts with a Latin «M»).
* iaaa-5439 — a direct question typed with «.» — Greek question mark used (lint exception).
* iaaa-7560 — stem «…, което би причинило нарушаване на:» followed by nominal answers («намаляване на устойчивостта»)
  does not combine literally — rendered «…, που θα προκαλούσαν διαταραχή:» + nominative answers (the answer names the
  disturbance); right/wrong status unchanged.
* iaaa-6101 — «изключени предавки» rendered «με το κιβώτιο ταχυτήτων στη νεκρά» (gears disengaged = neutral).
* iaaa-7711-a2 — «неправилнозадните гуми»: stray word «неправилно» glued to «задните» — translated «τα πίσω ελαστικά».
* iaaa-7636 — stem ends with «::» — one colon kept.
* Answers that do not grammatically continue their stem in Bulgarian (e.g. iaaa-7691-a2/a3, iaaa-7449-a3, iaaa-7520-a2)
  are mirrored, not repaired, so that no answer becomes more or less natural than in the source.
* «силово предаване (трансмисия)» — the Bulgarian synonym gloss in brackets is kept as «(τρανσμισιόν)», the Greek
  workshop word, because both Bulgarian words map to σύστημα μετάδοσης της κίνησης.
* ККМ (контактно-кабелна мрежа, trolleybus/tram overhead line) has no Greek abbreviation; it is always written out
  as «εναέριο δίκτυο επαφής». Where the Bulgarian gives both forms («контактно кабелната мрежа (ККМ)», iaaa-12096,
  iaaa-13476-a1) the bracketed abbreviation is not repeated.
* iaaa-13491 — the answers end with «;» used as a list separator; in Greek «;» is the question mark, so the
  separator is dropped.
* ватман (tram driver) → «ο οδηγός του τραμ»; трамвайна мотриса → «αυτοκινητάμαξα τραμ»; дежурен по депо →
  «εφημερεύων του αμαξοστασίου».
* iaaa-13487 — the Bulgarian capitalises answers a1 and a3 (names of units); Greek uses article-less genitives
  («Προϊσταμένου …», «Κέντρου …») so that the capitals are kept and every answer continues the stem.
* теглене: «έλξη» where a tractor unit / towing vehicle pulls a trailer, «ρυμούλκηση» where a vehicle tows another
  vehicle; колесар (converter dolly) → «φορείο ζεύξης»; съчленено ППС → «αρθρωτό όχημα».
* **Picture labels.** iaaa-11575/11579/11580: the diagram is labelled A, B, C → «Α», «Β» (Greek capitals, identical
  shapes) and Latin «C» (Greek has no letter shaped like C). iaaa-5294/5295/5296: the picture is labelled with the
  Cyrillic «а.», «б.», «в.»; the alphabetical Greek α, β, γ would point to the wrong sign, because «в» looks like β.
  Following correction 4 of the brief, а → «α» (look-alike letter), while «б» and «в», which have no Greek
  look-alike, are written exactly as printed (Cyrillic, with "cyrillic" lint exceptions for iaaa-5295/5296).
* **Road classes (correction 1).** автомагистрала → «αυτοκινητόδρομος»; скоростен път (expressway, 120 km/h) →
  «οδός ταχείας κυκλοφορίας»; автомобилен път (road for motor vehicles, sign E,6a, 90 km/h) → «οδός για αυτοκίνητα»
  (plural «οδοί για αυτοκίνητα»), the name of the Vienna Convention sign («route pour automobiles», «road for motor
  vehicles»). The earlier «υπεραστική οδός» was wrong and is replaced in iaaa-6041, iaaa-5164, iaaa-11601, iaaa-11603;
  the other 14 questions use the new term from the start. **Open doubt**: the Greek ΚΟΚ gives the E,6a sign (white car
  on blue) the name «οδός ταχείας κυκλοφορίας», but in Greece that class carries 110 km/h and corresponds in function to
  the Bulgarian expressway; the term is therefore kept for скоростен път (iaaa-11743 …) and автомобилен път gets the
  descriptive Vienna name. A reviewer who prefers the sign name would have to swap the two terms in all 30 questions.
* трактор → «τρακτέρ»; «γεωργικός ελκυστήρας» was avoided because it adds "agricultural".
* работен обем → «κυλινδρισμός» (EU licensing term); конструктивна максимална скорост → «μέγιστη εκ κατασκευής
  ταχύτητα»; мигаща светлина → «φως που αναβοσβήνει», проблясваща → «αναλάμπον».
* ЕКМТ/(СЕМТ) (the Bulgarian and the French abbreviation side by side) → «CEMT» once (iaaa-6840, iaaa-6841); the
  permits are «άδειες CEMT», the name used by the Greek transport ministry.
* Transport law follows the Greek texts of Reg. (EC) 561/2006, 165/2014, 1073/2009 and the CMR/TIR conventions:
  товарителница → «φορτωτική», карнет ТИР → «δελτίο TIR», тахографски лист → «φύλλο καταγραφής», карта на
  превозвача → «κάρτα επιχείρησης», сервизна карта → «κάρτα συνεργείου», екипно управление → «πολλαπλή
  επάνδρωση», лиценз → «άδεια», разрешително → «έγκριση» (to keep the two Bulgarian documents apart), превозна цена →
  «κόμιστρο», претоварване (CMR) → «μεταφόρτωση» (transhipment, not overloading).
* Currency «лв.» → «λέβα» written out (iaaa-11662, lint exception for the abbreviation stop).
* тъмната / светлата част на денонощието → «το σκοτεινό / φωτεινό μέρος του εικοσιτετραώρου» (literal, as the
  Bulgarian legal phrase).
* Trailing «;» used as a list separator at the end of answers (iaaa-12107-a1/a2, iaaa-6779-a1) is dropped, as in
  iaaa-13491. iaaa-6750 — «4.5» written with a decimal comma «4,5».
* **T17 coupling devices** follow the terms of UNECE Regulation No 55 (Greek EU text): ключалка (coupling head) →
  «κεφαλή ζεύξης», ухо → «δακτύλιος ζεύξης», тип «болт-ухо» → «πείρος-δακτύλιος», съединителен сферичен болт и носач
  → «σφαίρα ζεύξης και βραχίονας στήριξης», присъединителен (царски) болт → «πείρος ζεύξης (king pin)» (the bracket
  gives the international workshop word for the Bulgarian colloquial «царски болт»), седлово устройство → «διάταξη
  πέμπτου τροχού», теглич → «ράβδος έλξης», окачен / шарнирно окачен теглич → «αρθρωτή ράβδος έλξης» (R55 hinged
  drawbar), неподвижно закрепен теглич → «σταθερά στερεωμένη ράβδος έλξης» (rigid drawbar), стандартни /
  нестандартни → «τυποποιημένες / μη τυποποιημένες».
* iaaa-7327-a4 — typo «специализиран» (singular) for «специализирани»; translated «εξειδικευμένες».
* iaaa-7335-a2 «към ремаркето», iaaa-7354-a2 «към влекача» repeat the preposition of the stem; Greek cannot end a
  stem with a bare «σε», so the stem ends «στερεωμένες:» and every answer carries «στο / στα / στον» — the answers
  stay parallel. iaaa-7355-a2 (wrong answer without «с помощта на») is mirrored as a bare noun phrase.
* iaaa-7339 — yes/no question typed with «.»; Greek question mark used (lint exception).
* упойващи вещества → «τοξικές ουσίες» (the ΚΟΚ wording for intoxicating substances); наркотични вещества stays
  «ναρκωτικές ουσίες».
* Regulator questions (iaaa-5834 … 5869): the answers «на червения автомобил» are elliptical genitives in Greek
  («του κόκκινου αυτοκινήτου» = [the driver] of the red car), continuing «Για ποιον από τους οδηγούς …;».
* **Sign and signal names** are translated from the Bulgarian meaning, in « », keeping the Bulgarian form: the
  imperatives «Премини», «Пропусни», «спри» stay 2nd person singular («Πέρνα», «Άφησε να περάσουν», «σταμάτα»), and
  «Забранено е …» / «… е забранено» keep their word order («Απαγορεύεται …» / «… απαγορεύεται»). немигащ сигнал →
  «σταθερό σήμα» (the ΚΟΚ word for a steady light).
* «влизане срещу знака» (B2 no entry: entering while facing the sign) → «είσοδος με κατεύθυνση προς την πινακίδα»
  (iaaa-5990-a2, iaaa-5964); a literal «απέναντι / έναντι» would not be understood.
* Typos translated by their meaning: iaaa-5912 «Значенето», iaaa-5965-a1 «леки автомоби», iaaa-11868-a2/a3/a4
  «Забранено влизането» (missing «е»), iaaa-6171-a2 «с товар е по-голям» (= с товар, по-голям). iaaa-5979 lacks its
  question mark; Greek adds «;» like its twins iaaa-6172/6174. iaaa-11863 «3.5 t.» → «3,5 t» (stray stop).
* iaaa-11867-a1 (part 08) reworded «οχημάτων που φέρουν διακριτικό σήμα επικίνδυνων εμπορευμάτων» to match
  iaaa-12079-a1, which has the same Bulgarian answer. iaaa-5982/5983 (part 12) use the wording of iaaa-7415/7417
  (part 04) for «освен с полуремаркета или единични едноосни ремаркета».
* изкуствена неравност (iaaa-6322, iaaa-6330) → «τεχνητή ανωμαλία», keeping неравност → «ανωμαλία» as in iaaa-5194;
  the Greek everyday word would be «σαμαράκι».
* крайпътен обект (a roadside facility: petrol station, restaurant) → «παρόδια εγκατάσταση» (iaaa-6214-a4; iaaa-5198-a3
  in part 08 changed accordingly); крайпътни обекти, които ограничават видимостта (things beside the road) stay
  «παρόδια αντικείμενα» (part 06).
* Braking of combinations (T20) follows the Greek text of Directive 71/320/EEC, as already in iaaa-7377: непрекъснато /
  полунепрекъснато / инерционно / автоматично спиране → «συνεχής / ημισυνεχής / αδρανειακή / αυτόματη πέδηση»;
  резервна (аварийна) спирачна уредба → «εφεδρικό σύστημα πέδησης (έκτακτης ανάγκης)», mirroring the Bulgarian pair.
* iaaa-12126 — «КДЦ» (контролно-диспечерски център) has no Greek abbreviation; written out «Κέντρο Ελέγχου και
  Συντονισμού Κίνησης», диспечер → «συντονιστής». iaaa-12128 has no final punctuation in Bulgarian; mirrored.
* iaaa-5925-a4 repeats «че» after the stem «… че:»; mirrored («ότι …»), as the wrong answer is equally clumsy in the
  source.
* «жп прелез» (abbreviation, parts 14–15) is written out as «ισόπεδη σιδηροδρομική διάβαση», like every abbreviation;
  the resulting hint warnings (iaaa-6369, 6371, 6372, 6472) are documented exceptions.
* лента за принудително спиране → «λωρίδα έκτακτης ανάγκης» (ΚΟΚ); by analogy площадка / място за принудително
  спиране → «χώρος / θέση έκτακτης ανάγκης»; the act (принудително спиране в тунел, на прелез) → «αναγκαστική
  ακινητοποίηση». iaaa-6481-a2 «допълнителна пътна лента за принудително спиране» → «πρόσθετη λωρίδα κυκλοφορίας
  έκτακτης ανάγκης» (keeps «пътна»).
* интервал между автомобилите (iaaa-5864, iaaa-5866) → «διάστημα», neutral between time and distance, because the
  answers of iaaa-5866 mix seconds, metres and a car length.
* Redundant «че» at the start of an answer after «… че:» is mirrored (iaaa-6429/6430/6431-a4); iaaa-8264-a4 has a Latin
  «e» in «e разрешено»; iaaa-7272 is a statement typed with «?» and answered правилно/неправилно — the Greek keeps the
  question mark «;».
* iaaa-12058-a3 «пред прелеза» → «πριν από την ισόπεδη διάβαση»: the short Bulgarian form gets the short Greek form
  here, because the full term would make the correct answer the longest (2.4× the Bulgarian); the other answers speak of
  rails, so «ισόπεδη διάβαση» (the usual Greek word for a railway level crossing) is unambiguous.
* стоп-палка (iaaa-6351, iaaa-6353) → «σηματοδοτική ράβδος «STOP»»; палка (iaaa-6065) → «σηματοδοτική ράβδος».
* велосипедна пътека (iaaa-5630) → «διάβαση ποδηλάτων»: the rule «на велосипедна пътека и на по-малко от 5 м преди нея»
  mirrors the one for пешеходна пътека (διάβαση πεζών), so the crossing is meant, not a cycle track.
* осигурявам предимство (iaaa-12005, 12055, 12061) → «εξασφαλίζω προτεραιότητα», kept apart from давам предимство →
  «παραχωρώ προτεραιότητα».
* «трябва да пропусне / пропусна: само синия автомобил / двата автомобила» (iaaa-6540, 6561 and the group iaaa-6512 …
  6557) — Greek «αφήνω να περάσει / να περάσουν» agrees with what passes, and the stem is shared by singular and plural
  answers; the plural answers are therefore rendered «καθένα από τα δύο αυτοκίνητα / οχήματα» (each of the two), which
  keeps one stem «… να αφήσει / αφήσω να περάσει:» for all answers. A masculine answer stays in the nominative (iaaa-6532
  «ο μοτοσικλετιστής»).
  iaaa-6356 «насрещно движещите се: трамваи / … / мотоциклети» → «τα αντίθετα κινούμενα οχήματα: τραμ / … / μοτοσικλέτες»
  («οχήματα» added because the Greek participle would not agree with «μοτοσικλέτες»).
* «разположението … е: правилно / неправилно» (iaaa-5374, 5375, 6069, 6097, 9838) → «η θέση … είναι: σωστή / λανθασμένη»
  (adjectives agreeing with «θέση» instead of the fixed pair σωστό / λάθος).
* предимството на дясностоящия → «η προτεραιότητα του προερχόμενου από δεξιά» (the ΚΟΚ wording of the right-hand rule);
  разрешаващ / забраняващ сигнал → «επιτρεπτικό / απαγορευτικό σήμα».
* iaaa-12008 ends «… поради?» (a stem that the answers complete, typed with a question mark) — mirrored «… εξαιτίας;»;
  iaaa-12037 «При тази ситуация?» mirrored «Σε αυτή την κατάσταση;».
* теглич of a rigid tow (твърда връзка, iaaa-5730) → «ράβδος ρυμούλκησης», while the drawbar of a trailer (T17) stays
  «ράβδος έλξης». iaaa-9837-a4 has a plural verb «да навлизат» for a singular subject; mirrored («να εισέρχονται»).
* пропускам + masculine noun (пешеходеца, мотоциклетиста) → «αφήνω τον πεζό / τον μοτοσικλετιστή να περάσει», the natural
  Greek order; with neuter nouns «αφήνω να περάσει το … αυτοκίνητο».
* iaaa-5570/5602/5607-a3 «участъкът не е сигнализиран» → «το τμήμα της οδού …»: «της οδού» added so that the correct
  answer of iaaa-5602 does not become the longest (κατάστρωμα της οδού is a three-word term).
* iaaa-12060-a3 «спирам автомобила извън лентата за принудително спиране» is marked correct in the source; translated as
  written («εκτός της λωρίδας έκτακτης ανάγκης»), not corrected. iaaa-12056-a1 «в разделителната ивица между платната на
  релсовия път» is rendered literally (the tram track lies in the median between the carriageways).
* More slips translated by their meaning: iaaa-11712-a4 «130 кkm/h» (Cyrillic к), iaaa-5862 «Кой два» (= Кои два),
  iaaa-6098 «прaвилно» (Latin a), iaaa-11684-a2 «двиние», iaaa-11703/11704 «3 t.» (stray stop).
* Typos and grammar slips translated by their meaning: iaaa-6220/6238 «предупреждават» and iaaa-6278 «указват»
  (plural verb for one sign), iaaa-7370 «средсво», iaaa-7379 «продължителено», iaaa-7381 «трябва се», iaaa-7387
  «разедени», iaaa-7266 «темперетурата» and «30°С» typed with a Cyrillic С (→ «30 °C»).
* Part 20: «Теглене с гъвкава връзка по автомобилен път / скоростен път» (iaaa-5423, iaaa-8279) keeps the two road
  classes apart (οδός για αυτοκίνητα / οδός ταχείας κυκλοφορίας); изтегляне до най-близкото място за напускане на пътя →
  «ρυμούλκηση έως το πλησιέστερο σημείο εξόδου από την οδό». теглещият автомобил → «το ρυμουλκό αυτοκίνητο» (iaaa-5783,
  iaaa-5785). пътен възел (iaaa-6707-a4) → «οδικός κόμβος».
* iaaa-6581-a2 «трябва да се подготвя» is a first-person perfective (like «може да завия» in a3) → «πρέπει να
  προετοιμαστώ». Typos translated by their meaning: iaaa-5334-a4 «задължетелен», iaaa-5797-a3/a4 «забрананява»,
  iaaa-5783-a3 «теглещия» (for теглещият); iaaa-5546 has a space before the colon, ignored.
* T23 occasional transport (iaaa-7175): обиколен превоз при затворени / „отворени“ врати → «κυκλική μεταφορά με κλειστές
  / «ανοιχτές» πόρτες»; превоз от вида „пълен - празен“ → «μεταφορά του τύπου «γεμάτο - άδειο»». The EU texts call these
  «περιηγήσεις με κλειστές πόρτες» and services «με φορτίο κατά τη μετάβαση και κενές κατά την επιστροφή»; the Bulgarian
  wording is kept literal so the quoted names stay recognisable. каботажен превоз → «μεταφορά καμποτάζ».
* Part 21 (T23 bus transport): the Bulgarian administrative units are rendered by function — област → «περιφέρεια»,
  община → «δήμος», областен управител → «διοικητής περιφέρειας», републиканска транспортна схема → «εθνικό σχέδιο
  δρομολογίων» (the nationwide scheme). маршрутно разписание → «ωράριο διαδρομής», разписание → «ωράριο», курс →
  «δρομολόγιο». совалков превоз → «παλινδρομική μεταφορά» (the Greek EU term for shuttle services).
* iaaa-11343-a2 «пътен формуляр» (a wrong answer) → «έντυπο ταξιδιού», deliberately not «φύλλο πορείας», which is the
  Greek EU name of the real journey form and would make the distractor look right.
* iaaa-7159 / iaaa-7163 «… се утвърждават от съответните: кметове / областни управители / общински съвети» — Greek
  «αντίστοιχους / αντίστοιχα» would have to agree with each answer's gender and so mark one answer as odd; the stem says
  «εγκρίνονται, κατά περίπτωση, από:» and every answer carries its own article.
* iaaa-11672-a1 «между 6,00 и 21,00 ч.» → «μεταξύ 6:00 και 21:00» (24-hour clock, style guide).
* Slips translated by their meaning: iaaa-7116 repeats «водачът» at the end (dropped), iaaa-7094 lacks «превози» after
  «специализирани» (supplied), iaaa-11754-a1 «по-гомяма», iaaa-7163 «тренспортни», iaaa-7112-a3 «всики», iaaa-6929-a1
  «товарана», iaaa-6978-a2 «възражениета», iaaa-6922 «отстранини» and «ПС» (= превозно средство), iaaa-6900-a1
  «международен превози», iaaa-6972 «може да се извършва». iaaa-6899/6900 write «AТР» with a Latin A and Cyrillic ТР —
  rendered «ATP». iaaa-12087 has no final punctuation; mirrored.
* T24: товар in the CMR questions → «εμπορεύματα», elsewhere «φορτίο»; товародател → «φορτωτής», kept apart from
  изпращач → «αποστολέας». Конвенцията ADR / AТР → «Σύμβαση ADR / ATP» (the Bulgarian calls both conventions).
* Part 22: товар is «εμπορεύματα» wherever the question is about the CMR parties (sender, carrier, consignee,
  consignment note: iaaa-6975–6990, 6969, 6979) and «φορτίο» in the loading, securing and marking questions;
  Спогодбата ADR (iaaa-6907) → «Συμφωνία ADR», kept apart from Конвенция → «Σύμβαση».
* iaaa-6984 — the answers have no article in Greek («εμπορεύματα», «δεύτερο αντίτυπο της φορτωτικής»), because «τα
  εμπορεύματα» for the one-word «товара» would be 2.3 times longer and make the correct answers the longest.
* iaaa-5664-a1 «разминаване» (one word) → «σε διασταύρωση με όχημα»: the short form of the fixed term, which still names
  the oncoming vehicle; the full «διασταύρωση με αντίθετα κινούμενο όχημα» is used in the stems (iaaa-5684, 5686).
* светлини за движение през деня (iaaa-11632) → «φώτα για κίνηση κατά την ημέρα», literal, because the short Greek «φώτα
  ημέρας» is less than half the length of the Bulgarian and «φώτα πορείας ημέρας» would clash with φώτα πορείας
  (дълги светлини).
* iaaa-6924-a3 «назад» → «πίσω» (after «στραμμένα:»), not «προς τα πίσω», which would be 2.4 times longer.
* Slips translated by their meaning: iaaa-6916 «отдзад», iaaa-5739-a2 «за приеме», iaaa-5743 «уравлението», iaaa-5716
  «продържително», iaaa-6132-a1 «предвижва» (= предвижда), iaaa-5686-a4 «автомобилитге»; iaaa-6130 has a space before
  the colon.
* Part 23: the light questions iaaa-11631, 5687, 5668 keep the official names (φώτα διασταύρωσης / πορείας / θέσης);
  their hint warnings are documented exceptions, as for iaaa-5700. 11633 uses the short name «Дневните светлини» →
  «φώτα ημέρας», in quotes as in the Bulgarian.
* iaaa-5699/5705 «завиването в обратна посока» as a one-noun answer → «η εκτέλεση αναστροφής» (the bare «η αναστροφή»
  would be less than half the Bulgarian length).
* iaaa-7014/7015/7012 — authorities: Агенция „Пътна инфраструктура“ → «Οργανισμός «Οδική Υποδομή»» (name kept in
  quotes like «Διοίκηση Αυτοκινήτων»); областно пътно управление → «περιφερειακή διεύθυνση οδών»; ИА „АА“ written out.
  iaaa-7012 is a stem typed with «?» whose answers are bare names in the nominative (Bulgarian a4 alone has the article
  and a capital); mirrored.
* iaaa-7021-a2 «знак “Внимание! Други опасности”» lacks the preposition «с» of the other answers; mirrored («πινακίδα
  «Προσοχή! Άλλοι κίνδυνοι»»). iaaa-11874-a4 keeps the comma of «не е разрешено, само за …».
* Slips translated by their meaning: iaaa-5724-a4 «намялява», iaaa-7062-a3 «означенато», iaaa-5685-a3 «не по-повече»,
  iaaa-5712 «за водачът», iaaa-5663-a3 «с включен светлина»; iaaa-6996 and 6997 are stems typed with «?» — mirrored «;».
* длъжен е / задължен е → «υποχρεούται» everywhere (as in parts 01–19); the few «είναι υποχρεωμένος» of parts 21–23
  were harmonised.
* Part 24 (T27): bus classes I, II, III, A, B → «κλάση I / II / III / A / B» with Latin letters (Directive 2001/85/EC
  and UNECE R107 use «κλάση»); седящи / стоящи пътници → «καθήμενοι / όρθιοι επιβάτες». iaaa-7243 ends with «.:» — only
  the colon is kept.
* T28: въздуховод „захранване“ / „управление спирачки“ (iaaa-7393) → «αγωγός αέρα «τροφοδοσία» / «έλεγχος φρένων»», the
  labels quoted as on the coupling heads; „сгъване“ на състава → «δίπλωμα» (jackknifing), in quotes as in the source;
  теглещо МПС → «ρυμουλκό μηχανοκίνητο όχημα».
* T29/T30: the twins of parts 13–14 (iaaa-7269/7273/7274/7275/7276/7278/7281) are reused word for word;
  iaaa-5476-a2 «с проверочен изпит» → «με εξέταση ελέγχου γνώσεων» as in part 08. iaaa-11411 applies correction 1:
  скоростен път → «οδός ταχείας κυκλοφορίας».
* Slips translated by their meaning: iaaa-7394 «беде», iaaa-7389 «опастност», iaaa-6918-a1 «задвижението», iaaa-7421-a1
  «средсво», iaaa-7247-a2 «седящ пътници», iaaa-7390-a2 «се задействат … тези» (plural for one system), iaaa-11413
  «oрганизира» with a Latin «o», iaaa-7035-a3 «всички ремаркетата».
* Part 25 (T30, penalties): фиш → «κλήση», електронен фиш → «ηλεκτρονική κλήση», акт (за установяване на
  административно нарушение) → «έκθεση (διαπίστωσης διοικητικής παράβασης)», наказателно постановление → «πράξη
  επιβολής κύρωσης», временно спиране от движение → «προσωρινή θέση εκτός κυκλοφορίας», прекратяване на регистрацията
  → «διαγραφή της ταξινόμησης», регистриран → «ταξινομημένο», обжалване → «προσφυγή». These follow Greek administrative
  usage for the Bulgarian procedure; the Bulgarian names of the documents have no exact Greek counterpart.
* iaaa-6018-a2 застраховка „Каско“ (a wrong answer) → «ασφάλιση «Ίδιες ζημίες»», the Greek name of the same
  comprehensive cover, quoted like «Αστική ευθύνη».
* iaaa-6003 туристическо ремарке → «τροχόσπιτο»; iaaa-5993 товарно ремарке → «φορτηγό ρυμουλκούμενο».
* iaaa-11400-a4 «има наложено наказание глоба …» does not continue its stem (… който управлява …:); mirrored.
  iaaa-11425-a3 switches to the singular «да уведоми» after the impersonal a1/a2; mirrored, and kept identical to
  iaaa-11422-a3.
* Slips translated by their meaning: iaaa-11362-a1 «всичси», iaaa-5536-a1 «трябвада», iaaa-8296 «изършено»,
  iaaa-8294 «електроннен», iaaa-5339-a2 «сигнализара», iaaa-11367 «oрганизира» (Latin o).
* `--all` harmonisation: iaaa-7035-a1 now repeats iaaa-7411–7414-a1 («συμπεριλαμβανομένων και των ημιρυμουλκούμενων»)
  and iaaa-11828/11829-a3 repeat iaaa-11813-a3; the obsolete exception for iaaa-12105 was removed.

## UI strings

* Buttons use the verbal nouns of Greek Android (Ακύρωση, Κλείσιμο, Συνέχεια, Έναρξη, Επανάληψη, Έλεγχος, Υποβολή,
  Λήψη, Διαγραφή, Παράλειψη), titles are nouns, running text uses the formal «εσείς».
* Fixed UI terms: въпрос → «ερώτηση» (so the adjectives are feminine: Επόμενη / Προηγούμενη, Σωστές / Λανθασμένες,
  Νέες, Τυχαίες, Σημειωμένες); отметка / отбелязан → «σήμανση» / «σημειωμένη ερώτηση» (tab «Σημειωμένες»);
  вариант (the candidate's case) → «περίπτωση»; раздел → «ενότητα»; изпитен тест → «τεστ εξέτασης»; точка →
  «βαθμός»; упражнение → «εξάσκηση»; изтегляне → «λήψη»; издание (of the question bank) → «έκδοση», версия (of the
  database) → «έκδοση βάσης»; зачетен → «πιστώνεται».
* ИААА: the full name «Εκτελεστικός Οργανισμός «Διοίκηση Αυτοκινήτων»» followed by the Latin «(IAAA)» appears once,
  in feature_onboarding_disclaimer and feature_settings_attribution; every other caption and notice says «IAAA»
  (reviewer decision, wave 2). The questions keep the full name without the acronym.
* The Bulgarian «;» inside sentences becomes the Greek ano teleia «·» (the Greek «;» is the question mark).
* Captions under big numbers use heading-like plurals (ερωτήσεις, βαθμοί, λεπτά, συνεχόμενες ημέρες, επιτυχημένα
  τεστ). Greek plurals have the CLDR forms one / other; the quantity follows the note of each string (e.g. %2$d in
  «Μάθατε %1$d από %2$d ερωτήσεις»).
* шофьорска книжка → «άδεια οδήγησης» (glossary), not the colloquial «δίπλωμα».

## Open doubts for the reviewer

* автомобилен път → «οδός για αυτοκίνητα» (correction 1): the Greek ΚΟΚ names sign E,6a «οδός ταχείας κυκλοφορίας»,
  but that Greek class has a 110 km/h limit and would clash with скоростен път; the descriptive name keeps the three
  Bulgarian classes apart. A reviewer may prefer another descriptive name.
* Picture letters «б», «в» stay Cyrillic in iaaa-5295/5296 (correction 4); «а» is «α».
* УПК in the variant label (see Labels) — read as удостоверение за професионална компетентност.
* транспортна схема → «σχέδιο δρομολογίων», републиканска → «εθνικό», областен управител → «διοικητής περιφέρειας»:
  functional equivalents of Bulgarian administrative terms.
* МПС със специален режим на движение → «αυτοκίνητο με ειδικό καθεστώς κυκλοφορίας» (literal).
* Наредба → «Διάταγμα»; стаж → «εμπειρία»; упойващи вещества → «τοξικές ουσίες» (ΚΟΚ wording); велосипедна пътека
  in the stopping/parking rules → «διάβαση ποδηλάτων».
* CEMT permits are named «άδεια CEMT»; ΕΔΥΜ (the Greek abbreviation) is not used.
* Penalty procedure terms of part 25 (фиш → «κλήση», акт → «έκθεση», наказателно постановление → «πράξη επιβολής
  κύρωσης») are Greek functional equivalents, not legal identities.

## Review (wave 2): decisions on the open doubts

* автомобилен път → «οδός για αυτοκίνητα»: kept. The three road classes stay distinct as instructed (18 / 12 /
  автомагистрала → «αυτοκινητόδρομος»); no answer of 5391, 5334, 6449, 6707 or 5423 is made wrong by «για αυτοκίνητα».
* Picture letters «α» / «б» / «в» in iaaa-5294–5296: kept (correction 4).
* УПК → «πιστοποιητικό επαγγελματικής επάρκειας»: kept.
* транспортна схема / републиканска / областен управител: kept; used consistently in parts 20–21 and 24.
* МПС със специален режим на движение: kept («μηχανοκίνητο όχημα / αυτοκίνητο με ειδικό καθεστώς κυκλοφορίας»,
  following the Bulgarian noun).
* Наредба → «Διάταγμα»: kept in the glossary; the word does not occur in any question, label or UI string.
* стаж → «εμπειρία», упойващи вещества → «τοξικές ουσίες», велосипедна пътека → «διάβαση ποδηλάτων»: kept.
* «άδεια CEMT»: kept.
* Penalty procedure terms: kept; checked in parts 24–25, where they are used consistently.
* Fixed by the reviewer (see review/el/changes.json): моторни in 5176–5178 → «έχουν κινητήρα»; the Reg. 561/2006
  rest terms (дневна / седмична почивка → «ημερήσια / εβδομαδιαία περίοδος ανάπαυσης», parts 09–10); iaaa-6111 →
  «απόσταση ακινητοποίησης»; «временно се спира от движение» → «τίθεται προσωρινά εκτός κυκλοφορίας» everywhere
  (7144-a2, 6854-a2 aligned); «готовност за спиране» → «ετοιμότητα για φρενάρισμα» everywhere (5688-a2, 12068
  aligned); «разрешаващ сигнал» → «επιτρεπτικό σήμα» everywhere (5803-a3 aligned); 6855 «φορτηγό ρυμουλκούμενο».
* Source slip translated by its meaning: iaaa-9837-a4 «да навлизат» (plural after the singular stem «на водача е
  разрешено:», copied from 6087-a4) → singular «να εισέρχεται».
