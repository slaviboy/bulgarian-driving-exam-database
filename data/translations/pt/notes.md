# Notes — Portuguese (pt-PT) translation

Open questions and decisions for the reviewer. Format: id — problem — decision.

## General decisions

* кръстовище = «cruzamento» (the usual pt-PT word); разминаване is kept apart from it by using the verb «cruzar-se com» (or «cruzamento de veículos» when a noun is unavoidable), so the place and the manoeuvre never read alike.
* спиране (any stop) = «imobilização» / verb «parar»; престой = «paragem» (Código da Estrada, art. 48); паркиране = «estacionamento». спиране meaning braking = «travagem».
* ППС = «veículo»; МПС = «veículo a motor»; автомобил = «automóvel»; лек автомобил = «automóvel ligeiro».
* лента за принудително спиране = «faixa de paragem de emergência», so that банкет alone is «berma».
* пътно платно ≠ платно за движение: the bank treats «пътното платно» as carriageway + shoulders + islands (iaaa-5230; part 8 speaks of «платното за движение» and «другите конструктивни елементи на пътното платно»). So платно за движение = «faixa de rodagem» and пътно платно = «plataforma da via» (the pt-PT road-engineering term for carriageway + shoulders), everywhere.
* The candidate is addressed with formal third-person verb forms without «você» (Como procederá?), as in pt-PT test materials.
* генератор = «gerador» and алтернатор = «alternador», because the bank contrasts them (iaaa-7587).
* iaaa-5176…5178 — «Кои … са моторни?» is rendered «motorizados», not «veículos a motor»: mopeds are a correct answer there, and «veículo a motor» is reserved for МПС, which excludes mopeds.
* **автомобилен път / скоростен път (deviation from the pivot glossary).** The pivot glossary glosses «автомобилен път» as «public road (outside built-up areas)», but the bank uses it for a road category with its own rules: its sign is a white car on blue (iaaa-5334, the Portuguese H24 sign), mopeds, tractors and bicycles may not use it (iaaa-5391), parking and stopping are allowed only at marked places (iaaa-5412, 5413), and U-turns, reversing and entering the median are prohibited (iaaa-5411…5418, 11354). An ordinary «estrada» would teach a wrong rule, so автомобилен път = «via reservada a automóveis e motociclos» (the pt-PT name of that very sign), and скоростен път (expressway) = «via rápida». Parts 5, 7, 8, 14 and 15 were updated accordingly.
* велосипедна пътека (a marked cycle crossing, parallel to пешеходна пътека) = «passagem para velocípedes» (the Código da Estrada term); велосипедна алея = «pista ciclável».
* «продължавам движението си» is rendered «continuo a marcha» / «continuo a circular», never «continuo a marcha atrás de…», to avoid confusion with «marcha atrás» (reversing).

## Labels

* D.zaguba-na-pravosposobnost-po-reda-na-chl-157-al-4-zdvp-i-upk — the abbreviation «УПК» is not explained anywhere in the bank; it most likely stands for «удостоверение за професионална компетентност». Translated as «certificado de competência profissional». A reviewer should confirm.
* D.s-pravosposobnost-…-sas-stazh-2g — «със стаж 2г.» rendered as «com 2 anos de experiência» (two years holding category B).
* Effective notes «След 12.12.24г.» = «Após 12.12.24.» (the final full stop stands for the abbreviation dot of «г.»).

## Source typos and wording problems (translated by intended meaning)

* iaaa-6164 — «провобуксуващата» is a typo for «противобуксуващата» — translated as «sistema antipatinagem (ASR)».
* iaaa-6163 — «хлъзгъв» is a typo for «хлъзгав» — «via escorregadia».
* iaaa-5439 — a «ли» question closed with a full stop — Portuguese ends it with «?» (lint exception end_punct).
* iaaa-7560 — the stem «…което би причинило нарушаване на:» does not fit its answers («повишаване / намаляване на …»); translated by intended meaning: «…que provocariam:» + «um aumento / uma diminuição …».
* iaaa-7513 — unbalanced slash «Впръсквачът /дюзата» kept as «O injetor /bico injetor».
* iaaa-7711 — answer a2 reads «неправилнозадните гуми» (the word «неправилно» glued to «задните гуми») — translated as «pneus traseiros».
* iaaa-7636 — the stem ends with «::» — a single «:» is used.
* iaaa-7449 — answer a3 «да улесни…» does not fit the stem «…да осигури:» grammatically — rendered as a noun phrase «um arranque inicial mais fácil…» so that stem + answer is one sentence.
* iaaa-7649 — «/трансмисиятна» is a typo for «/трансмисията/ на» — «da cadeia de transmissão /transmissão/ do automóvel».
* iaaa-7602 — «маслоизмелвателната» is a typo for «маслоизмервателната» — «régua de medição do nível do óleo /vareta/».
* iaaa-7660 — answer a2 «2 два пъти в годината» repeats the number as digit and word — rendered «2 vezes por ano» (the digit is kept).
* iaaa-7544 — answer a3 («намаляване на скоростта…») does not continue the stem «…за задържане:» grammatically, in Bulgarian either; the mismatch is kept as in the source rather than rewriting the stem, so the answer is neither more nor less obviously wrong than in Bulgarian.
* iaaa-12105 — answer a2 starts with a capital letter in Bulgarian; kept («Para percorrer…»).
* iaaa-7339 — like iaaa-5439, a «ли» question closed with a full stop — «?» used (lint exception).
* iaaa-7355 — answer a2 «прикачно устройство тип “ухо”» lacks the preposition the stem needs; rendered «por meio de um dispositivo de engate do tipo «olhal»», parallel to a1.
* iaaa-6782 — the stem «…водачът е задължен:» is followed by answers that repeat the modality («трябва да…», «може да…»); the stem is rendered «…o condutor:» so that both answers stay grammatical.
* iaaa-6768 — stem «…когато e:» + answers «издадена…»; the verb is moved into the answers («foi emitido…») so all four answers read grammatically.
* iaaa-11662 — the fines «500 лв.» etc. are rendered «500 levs».
* iaaa-7075, 6812 (a4) — a doubled «за» is dropped.
* iaaa-6859 — a doubled «до» in the stem is dropped.
* iaaa-11863 — «3.5 t.» rendered «3,5 t» (decimal comma; the dot after «t» is not a sentence end).
* iaaa-5965 (a1) — «леки автомоби» is a typo for «леки автомобили» — «automóveis ligeiros».
* iaaa-5979 — the stem has no «?» in Bulgarian; none is added.
* iaaa-12115 — a doubled «стрелка» is dropped.
* iaaa-6750, 6753 — «4.5» rendered «4,5»; iaaa-6727, 6728 — the time «00.00» rendered «00:00».
* iaaa-7128 (part 8) and iaaa-5268 (part 6) were later harmonised with identical wording in parts 9 and 8.
* iaaa-6220, 6238, 6278 — singular subject «Пътният знак…» with a plural verb («предупреждават», «указват»); translated in the singular.
* iaaa-5925 (a4) — a doubled «че» (stem «…, че:» + answer «че към прелеза…») is dropped.
* iaaa-7266 (a1) — «30°С» is written with a Cyrillic «С»; rendered «30 °C» with the Latin unit symbol (also the typo «темперетурата»).
* iaaa-7381, 7370, 7379, 12126 — small typos («трябва се осъществява», «средсво», «продължителено», «събитие ,което») do not affect the meaning.
* iaaa-12128 — the statement has no final full stop in Bulgarian; none is added.
* iaaa-11712 (a4) — «130 кkm/h» contains a stray Cyrillic «к»; rendered «130 km/h».
* iaaa-11704, 11703 — «3 t.,» rendered «3 t,» (the dot is not a sentence end).
* iaaa-11684 (a2) — «двиние» is a typo for «движение»; iaaa-5862 — «Кой два» is a typo for «Кои два»; iaaa-6098 — a Latin «a» inside «прaвилно». None affects the meaning.
* iaaa-12060 (a3) — **Doubt:** the answer «спирам автомобила извън лентата за принудително спиране» («I stop the car outside the emergency lane») is marked correct, which looks contradictory (one would expect «извън лентата за движение» or «в лентата за принудително спиране»). Translated literally («paro o automóvel fora da faixa de paragem de emergência») so that the Portuguese says exactly what the Bulgarian says; a reviewer should check the source.
* iaaa-12127 — «водача» (for «водачът») and iaaa-7267 «на водачът» (for «на водача») are case typos with no effect.
* iaaa-5828 — the stem has no colon in Bulgarian; none is added (the answers still continue it).
* iaaa-11628, 11627 — «пробляскваща» is a typo for «проблясваща» — «cintilante»; iaaa-6091 — a Latin «o» inside «навлизанетo»; iaaa-6352 (a2) — «се намира» for «се намират». No effect on the meaning.
* iaaa-6572 (a4) — the answer repeats «защото» after the stem «…, защото:»; the doubled word is dropped.
* iaaa-6425, 11870 — the stems end with «:» although they read as a statement/question; the colon is kept as in Bulgarian. iaaa-12008 — «…, поради?» is rendered as a real question («devido a quê…?»).
* iaaa-5374, 5375, 6069, 6097, 9838 — «правилно/неправилно» agree with «a posição» in Portuguese: «correta/incorreta».
* iaaa-5409 (a2) «раздилителната», iaaa-6090 Latin «o» in «навлизанетo», iaaa-11719 (a3) «не по- висока» — typos with no effect.
* iaaa-5944, 5945 — «правилото на десния» (colloquial) = «regra da direita»; the fuller «правилото за „предимството на дясностоящия“» (iaaa-5931 etc.) = «regra da «prioridade de quem está à direita»».
* iaaa-6261, 6286 — statements answered «правилно/неправилно» end with «:» in Bulgarian; the colon is kept. iaaa-6570 — stray comma in «синият автомобил, е:»; dropped.
* iaaa-12037 — the stem is only «При тази ситуация?»; rendered literally «Nesta situação?» rather than inventing a question.
* iaaa-5733 (a1) «дължинатана», iaaa-5952/6608 «пьтния» (soft sign for «ъ»), iaaa-9837 (a4) plural «навлизат» — typos with no effect.
* iaaa-5730 — «теглич» in the towing of a broken-down vehicle is the rigid tow bar = «barra de reboque» (for trailers the same word is the drawbar, «lança»).
* iaaa-5766 (a1) — «не, във всички случаи» = «não, em caso algum» (the idiomatic pt-PT form of «no, in all cases»).
* iaaa-5334 (a4) «задължетелен», iaaa-5797 (a3/a4) «забрананява», iaaa-5783 (a3) «теглещия» — typos with no effect.
* iaaa-7175 — the bus-service types are rendered with the Regulation (EC) 1073/2009 vocabulary: «circuito com portas fechadas»; «пълен – празен» / «празен – пълен» = «cheio – vazio» / «vazio – cheio» (kept in quotation marks, as in Bulgarian).
* iaaa-7115 (a3) — «може да издава…» does not continue the stem «…е длъжен:»; the mismatch is kept («pode emitir…»), as in Bulgarian. iaaa-7176 (a2, a3) and iaaa-7178 (a2, a3) likewise do not continue their stems grammatically; kept.
* iaaa-7116 — the stem repeats «водачът» at the end; the repetition is dropped. iaaa-7094 — «При извършване на специализирани на деца…» lacks the noun «превози»; translated as «Nos serviços regulares especializados de crianças…».
* iaaa-7195 (a2) — the elliptical «при специализиран» is rendered «no serviço especializado» (short form of «serviço regular especializado», which would put the word «regular» into both answers).
* iaaa-6922 — «0.20 м» rendered «0,20 m». iaaa-12087 — no final full stop in Bulgarian; none added.
* iaaa-6899, 6900 — «AТР» is written with Cyrillic Т and Р; rendered «ATP». ADR and ATP are called «конвенция» in Bulgarian; they are rendered with their official Portuguese designation «acordo».
* Typos with no effect: iaaa-11754 «гомяма», 7112 «всики», 6929 «товарана», 6978 «възражениета», 7163 «тренспортни», 6922 «отстранини», 6900 «международен превози».
* Bulgarian administrative units (bus-transport topic): област = «distrito», областен управител = «governador de distrito», община = «município», общински съвет = «conselho municipal», кмет = «presidente da câmara»; републиканска транспортна схема = «esquema de transporte nacional».
* Bus documents: пътен лист = «folha de itinerário»; пътна книжка = «caderneta de folhas de itinerário»; пътен формуляр (EU journey form) = «folha de viagem»; пътническа ведомост = «relação de passageiros»; списък на пътниците = «lista de passageiros».
* товародател = «carregador» (kept distinct from изпращач = «expedidor»).
* Cargo topic (part 22): товар/товарът = «carga» (glossary); стока/стоката = «mercadoria». In part 21 two CMR questions (iaaa-6987, 6978) use «mercadoria» for «товарът»; both are correct pt-PT and the questions are independent.
* iaaa-6921 «1.0 м», iaaa-6915 «0.2 / 0.5 / 0.75 / 1.0 м» rendered with a decimal comma; iaaa-6123 «0,5 промили» = «0,5 por mil».
* iaaa-11634 (a2) — «не е забранено, но е неправилно» agrees with «a utilização»: «não é proibida, mas é incorreta»; a1 keeps the fixed answer word «correto».
* iaaa-6140 — «през деня / през нощта» rendered «de dia / de noite» in this question (the shorter natural pair), elsewhere «durante o dia / durante a noite».
* Typos with no effect: iaaa-6916 «отдзад», 6912 «пробляскваща», 5739 (a2) «за приеме», 5716 «продържително», 5743 «уравлението», 5686 (a4) «автомобилитге», 6132 (a1) «предвижва» (for «предвижда»).
* iaaa-7021 (a2) — «знак “Внимание! Други опасности”» lacks the preposition «с» of the other answers; rendered «com o sinal «Atenção! Outros perigos»» so that it continues the stem like a1.
* iaaa-6996, 6997, 7012 — statement-like stems ending in «?» («…е?», «…се издава от?») are rendered as real questions («Qual é…?», «Que entidade emite…?»). The answers of iaaa-7012 start with a capital letter in Bulgarian; kept.
* iaaa-5699, 5703, 5704, 5705 — «При намалена видимост под 50 м е забранено:» is rendered «…, proíbe-se:» so that masculine and feminine noun answers («o reboque», «a ultrapassagem») all continue the stem grammatically.
* Typos with no effect: iaaa-5724 (a4) «намялява», 7062 (a3) «означенато», 7009 (a4) «пред празнични», 5685 (a3) «не по-повече», 6994/6992 «извън габаритно».
* Oversize-vehicle permits: Агенция „Пътна инфраструктура“ = «Agência «Infraestrutura Rodoviária»»; областно пътно управление = «direção distrital de estradas»; extraordinary-load vehicle = «veículo de dimensões excecionais».
* iaaa-7243 — the statement ends with «.:» in Bulgarian; rendered with a single «:» (the lint keeps the colon).
* Bus classes (part 24): клас I / II / III and клас А / В (Cyrillic letters) = «classe I / II / III» and «classe A / B» (Latin); iaaa-11839 «3 500 kg» keeps the space as thousands separator.
* iaaa-7390, 7391 — «сгъване» of a tractor–trailer combination (jackknifing) = «fechar em canivete».
* iaaa-7049 — «каросерията на товарния автомобил» (the cargo body) = «caixa de carga».
* iaaa-11411 — the last occurrence of скоростен път = «via rápida» (see the road-category decision above).
* Typos with no effect: iaaa-7421 «средсво», 7394 «беде», 7389 «опастност», 6918 «задвижението», 7247 «седящ пътници», 11413 Latin «o» in «oрганизира», 11763 «превишават», 7390 «задействат».
* iaaa-12126 — «дежурния диспечер КДЦ» (КДЦ = командно-диспечерски център of the transport operator) = «operador de serviço do centro de comando e despacho»; «despachante» was avoided because in pt-PT it means a customs broker.
* Fines and procedure (part 25): глоба = «coima»; фиш = «talão»; електронен фиш = «talão eletrónico»; акт = «auto» (съставя се акт = «é levantado um auto»); акт за установяване на административното нарушение = «auto de contraordenação»; административно нарушение = «contraordenação»; наказателно постановление, влязло в сила = «decisão sancionatória definitiva»; служебно прекратяване на регистрацията = «cancelamento oficioso da matrícula». **Doubt:** Portuguese law has no exact counterpart of the Bulgarian «фиш» (a simplified on-the-spot fine ticket); «talão» is a neutral rendering, and «multa» was avoided because in pt-PT it is a criminal fine.
* iaaa-6018 (a2) — застраховка «Каско» = seguro de «danos próprios» (the pt-PT name of own-damage cover); the Bulgarian quotation marks are kept.
* iaaa-6007…6011 — the device «светлоотразител» = «refletor» (the adjective «светлоотразителен» stays «retrorrefletor», as in «colete retrorrefletor»).
* iaaa-5994, 5995 / iaaa-5997 — the same Bulgarian answers «да не закрива…», «да е укрепен» are rendered with the subjunctive under the stem «É obrigação do condutor que a carga transportada:» («não tape…», «esteja fixada») and with the infinitive under the question «A qual dos requisitos indicados deve obedecer a carga transportada?» («não tapar…»), so that each answer fits its own stem (the lint compares answers only under identical stems).
* iaaa-11385 (a4) — «20 лв.» = «20 levs» (lint exception end_punct, as iaaa-11662).
* Typos with no effect (part 25): iaaa-6011 «отдзад» (as in iaaa-6916), 8296 «изършено» and «пълния размера», 8294 «електроннен», 11367 Latin «o» in «oрганизира».

## Terminology notes (technical topics)

* силово предаване = «cadeia de transmissão»; трансмисия = «transmissão» (the bank often writes «силовото предаване (трансмисията)», rendered «cadeia de transmissão (transmissão)»).
* ресор = «feixe de molas»; листов ресор = «feixe de molas de lâminas»; пружина = «mola»; листове = «lâminas» (the bank pairs «ресорите /пружините/»).
* вътрешна гума / външна гума = «câmara de ar» / «cobertura».
* Tram topics: ватман = «guarda-freio» (the pt-PT word for a tram driver); (трамвайна) мотриса = «motora (do elétrico)»; трамвай = «elétrico»; колоос = «rodado»; талиги = «bogies»; стрелка / език = «agulha» / «lâmina»; пясъчници = «areeiros»; токоснемател = «coletor de corrente»; депо = «depósito»; крайна спирка = «paragem terminal»; мономотриса = «motora simples»; магнитнорелсова спирачка = «travão magnético de carril».
* Trolleybus topics: ККМ (контактно-кабелна мрежа) = «rede de contacto» (the abbreviation is not reproduced).
* iaaa-7285…7290, 7294 — «колесар» (a Bulgarian pole trailer for long loads) has no exact pt-PT legal term — rendered «reboque para cargas longas». **Doubt:** a reviewer may prefer another term.
* iaaa-13482 — «Тикет система» (the ticket/validation system) = «sistema de bilhética».
* iaaa-13462 — «част то талигите» is a typo for «част от талигите» — «parte dos bogies».
* iaaa-12133, 12132, 13487, 13462 — answers start with a capital letter in Bulgarian; the capital is kept.

## Picture labels

* iaaa-11575, 11579, 11580 — the diagram shows Latin-looking A, B, C; kept as «A», «B», «C».
* iaaa-5294, 5295, 5296 — the picture labels the three countdown markers with the Cyrillic letters «а.», «б.», «в.», which have no identical Latin letters (and Cyrillic is not allowed in the translation). They are rendered by alphabetical position «a», «b», «c». **Reviewer:** the picture itself still shows а/б/в.

## Other decisions (parts 6–7)

* каруца = «carroça» (the everyday word, as the Bulgarian is everyday); «ППС с животинска тяга», if it occurs, = «veículo de tração animal».
* мигаща светлина = «luz intermitente»; проблясваща светлина = «luz cintilante» (iaaa-12075 uses both words side by side).

## Whole check (`--all`)

* Final result: 0 errors, 0 warnings, 78 accepted exceptions (each with its reason in `lint-exceptions.json`); coverage 2476/2476 questions, 7465/7465 answers, labels and UI complete.
* iaaa-12022 (a3), 12025 (a1) in part 6 and iaaa-12036 (a1), 12052 (a1) in part 15 — the same answer had «continuo a marcha, sem alterar a velocidade» and «continuo a marcha sem alterar a velocidade»; harmonised to the form without a comma.
* «опознавателен знак за опасен товар» (iaaa-11867, 12079, 7065, 11649, 5351, 5321) and «МПС, превозващо опасен товар» (iaaa-5526) — parts 7, 8 and 12 had «carga perigosa», later parts «mercadorias perigosas»; harmonised to «mercadorias perigosas» (the ADR term). «a carga perigosa» stays only where the physical load is meant («retirar a carga perigosa da via», iaaa-11649, 5321; «o tipo de carga perigosa transportada», iaaa-5351).
* Corrections from BRIEF.md checked in the finished parts: all 18 questions with «автомобилен път» read «via reservada a automóveis e motociclos», all 12 with «скоростен път» read «via rápida»; пътно платно / платно за движение are «plataforma da via» / «faixa de rodagem» everywhere; «моторни» in iaaa-5176/5177 is the plain adjective «motorizados».

## Interface (`ui-strings.json`)

* App name: «Exame de condução» (17 characters).
* ИААА = «IAAA» in the interface (short labels). It is written out once as «Agência Executiva «Administração Automóvel» (IAAA)» in the onboarding disclaimer and in the attribution (where the Bulgarian itself writes the full name). In the question bank it is always written out.
* pt-PT Android vocabulary: Definições, ecrã, aplicação, dispositivo, ligação à Internet, transferir / transferência (download), eliminar (delete), guardar, «A carregar…»; buttons are infinitives (Cancelar, Tentar novamente, Verificar, Seguinte, Anterior, Saltar); titles are nouns; the user is addressed with the formal third person without «você».
* упражнение / упражни = «treino» / «treinar»; изпитен тест = «teste de exame»; предай теста = «entregar o teste»; зачетен / незачетен = «validada» / «não validada»; издържан / неиздържан = «aprovado» / «reprovado»; научени = «aprendidas»; въпрос = «pergunta» (so the feminine chips Novas, Erradas, Aleatórias, Marcadas); раздел = «secção»; вариант = «variante»; вашият случай = «a sua situação».
* Bookmarks: отметка = «marcador», отбелязани (bookmarked) = «marcadas»; «отбелязан в зелено» (highlighted) = «assinalada a verde», and the answers chosen in the exam are «selecionadas», so the three meanings of «отбелязан» never clash.
* Plurals: Portuguese needs one / many / other. «many» is the CLDR category for exact millions (1 000 000, 2 000 000…), where Portuguese puts «de» before the noun («1 000 000 de pontos»); the «many» forms therefore read «%1$d de pontos». Where the counted number is followed by an adjective («corretas»), «many» = «other». In this app these forms are practically never shown.
* feature_statistics_topic_answers — «%1$d верни от %2$d отговора» = «%1$d de %2$d respostas corretas», so that the noun agrees with the counted quantity (%2$d) whatever %1$d is; likewise feature_categories_mastered / feature_home_mastered = «%1$d de %2$d perguntas aprendidas».
* feature_results_time — «Използвано време от %1$d минути» = «Tempo utilizado de %1$d minutos» («de» = out of, as in «de 97 pontos» under the score).
* feature_home_update — «ново издание на въпросите от %1$s»: %1$s is the edition date, so «uma nova edição das perguntas, de %1$s».
* feature_settings_offline — «Данни без интернет» = «Dados offline» (the usual pt-PT technical label); elsewhere «sem Internet».
* feature_settings_privacy_text — «анализи» (analytics) = «análises»; «резервното копие на Android» = «a cópia de segurança do Android».

## Open doubts (summary for the reviewer)

1. iaaa-12060 (a3) — the correct answer «спирам автомобила извън лентата за принудително спиране» looks contradictory; translated literally (see above).
2. «колесар» (iaaa-7285…7290, 7294) — no pt-PT legal term; «reboque para cargas longas».
3. «УПК» in the label of variant D.zaguba-…-i-upk — read as «удостоверение за професионална компетентност» = «certificado de competência profissional».
4. iaaa-5294…5296 — the Cyrillic picture labels а/б/в are rendered a/b/c; the picture still shows а/б/в.
5. «МПС със специален режим на движение» (22 occurrences) = «veículo a motor em regime especial de circulação»: the Bulgarian legal category (vehicles using the blue flashing light and the siren) is kept literally rather than replaced by the Portuguese «veículos em marcha de urgência», whose conditions differ.
6. Tram vocabulary: (трамвайна) мотриса = «motora (do elétrico)», ватман = «guarda-freio» — traditional pt-PT (Lisbon/Porto) terms; a reviewer from the transport sector may prefer «veículo motor».
7. фиш / електронен фиш = «talão» / «talão eletrónico» (no Portuguese counterpart of the procedure).
8. UI plurals: the «many» forms use «de» («%1$d de pontos»); if the reviewers prefer «many» = «other», only those 26 forms change.

## Main-agent changes at the gate (2026-11-05)

* iaaa-5295, iaaa-5296: the picture labels are the Cyrillic letters «б» and «в», exactly as printed in the diagrams
  (m-cb1c77ae4c1579b5, m-5079445745749caf); a transliterated or positional letter cannot be found in the picture.
  Lint exceptions added (check "cyrillic"), as in English.
* feature_settings_update_auto_summary: «verifica-se se existe» → «a aplicação verifica se existe» (Android lint
  read «se se» as a typo; same meaning).

Main-agent gate: iaaa-6111 says «distância de paragem» (stopping distance), not the braking distance: the key counts the
driver's reaction time, so the Bulgarian «спирачен път» is meant as the whole stopping distance there.
