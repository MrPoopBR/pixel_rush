# -*- coding: utf-8 -*-
"""Apenas apresentação: traduções de literais históricos fora das 94 chaves.

Não altera IDs, saves, missões, métricas, recompensas, hitboxes ou regras.
Strings usadas no jogo permanecem no idioma original nos dados persistidos.
"""
from functools import lru_cache
import re

IDIOMAS = ('es_ES','ja_JP','fr_FR','de_DE','it_IT','tr_TR','pt_PT','hi_IN','zh_CN','ko_KR','ru_RU')
# Cada linha: texto original pt_BR | es | ja | fr | de | it | tr | pt_PT | hi | zh | ko | ru
_LINHAS = '''CANTINHO DOS PETS|RINCÓN DE MASCOTAS|ペットの部屋|COIN DES COMPAGNONS|HAUSTIER-ECKE|ANGOLO DEI PET|EV CİL HAYVAN KÖŞESİ|CANTINHO DOS ANIMAIS|पालतू साथी कक्ष|宠物小屋|펫 공간|УГОЛОК ПИТОМЦЕВ
LOJA DE PETS|TIENDA DE MASCOTAS|ペットショップ|BOUTIQUE DES COMPAGNONS|HAUSTIER-SHOP|NEGOZIO PET|EVCİL HAYVAN MAĞAZASI|LOJA DE ANIMAIS|पालतू साथी दुकान|宠物商店|펫 상점|МАГАЗИН ПИТОМЦЕВ
COMING SOON|PRÓXIMAMENTE|近日公開|BIENTÔT DISPONIBLE|BALD VERFÜGBAR|PROSSIMAMENTE|YAKINDA|BREVEMENTE|जल्द आ रहा है|即将推出|출시 예정|СКОРО
Pets em breve|Mascotas próximamente|ペットは近日登場|Compagnons bientôt disponibles|Haustiere kommen bald|Pet in arrivo|Evcil hayvanlar yakında|Animais em breve|पालतू साथी जल्द आएँगे|宠物即将上线|펫 출시 예정|Питомцы скоро появятся
INDISPONIVEL|NO DISPONIBLE|利用不可|INDISPONIBLE|NICHT VERFÜGBAR|NON DISPONIBILE|KULLANILAMIYOR|INDISPONÍVEL|उपलब्ध नहीं|不可用|사용 불가|НЕДОСТУПНО
PET BLOQUEADO|MASCOTA BLOQUEADA|ペット未解放|COMPAGNON VERROUILLÉ|HAUSTIER GESPERRT|PET BLOCCATO|KİLİTLİ HAYVAN|ANIMAL BLOQUEADO|साथी लॉक है|宠物未解锁|잠긴 펫|ПИТОМЕЦ ЗАКРЫТ
◀ ANTERIOR|◀ ANTERIOR|◀ 前へ|◀ PRÉCÉDENT|◀ ZURÜCK|◀ PRECEDENTE|◀ ÖNCEKİ|◀ ANTERIOR|◀ पिछला|◀ 上一页|◀ 이전|◀ НАЗАД
PRÓXIMA ▶|SIGUIENTE ▶|次へ ▶|SUIVANT ▶|WEITER ▶|SUCCESSIVO ▶|SONRAKİ ▶|SEGUINTE ▶|अगला ▶|下一页 ▶|다음 ▶|ДАЛЕЕ ▶
PRÓXIMO ▶|SIGUIENTE ▶|次へ ▶|SUIVANT ▶|WEITER ▶|SUCCESSIVO ▶|SONRAKİ ▶|SEGUINTE ▶|अगला ▶|下一页 ▶|다음 ▶|ДАЛЕЕ ▶
DESAFIO DIÁRIO|DESAFÍO DIARIO|デイリーチャレンジ|DÉFI QUOTIDIEN|TAGESAUFGABE|SFIDA GIORNALIERA|GÜNLÜK GÖREV|DESAFIO DIÁRIO|दैनिक चुनौती|每日挑战|일일 도전|ЕЖЕДНЕВНОЕ ЗАДАНИЕ
DESAFIO SEMANAL|DESAFÍO SEMANAL|週間チャレンジ|DÉFI HEBDOMADAIRE|WOCHENAUFGABE|SFIDA SETTIMANALE|HAFTALIK GÖREV|DESAFIO SEMANAL|साप्ताहिक चुनौती|每周挑战|주간 도전|ЕЖЕНЕДЕЛЬНОЕ ЗАДАНИЕ
CONCLUÍDO • RECOMPENSA RESGATADA|COMPLETADO • PREMIO COBRADO|達成済み・報酬受取済み|TERMINÉ • RÉCOMPENSE REÇUE|ERLEDIGT • BELOHNUNG ERHALTEN|COMPLETATO • PREMIO RISCOSSO|TAMAMLANDI • ÖDÜL ALINDI|CONCLUÍDO • PRÉMIO RECEBIDO|पूरा हुआ • इनाम प्राप्त|已完成 • 奖励已领取|완료 • 보상 수령|ВЫПОЛНЕНО • НАГРАДА ПОЛУЧЕНА
RELIQUIAS ANCESTRAIS|RELIQUIAS ANCESTRALES|古代の遺物|RELIQUES ANCESTRALES|URALTER RELIKTE|RELIQUIE ANCESTRALI|KADİM KALINTILAR|RELÍQUIAS ANCESTRAIS|प्राचीन अवशेष|远古遗物|고대 유물|ДРЕВНИЕ РЕЛИКВИИ
DESAFIO DE PERCURSO|DESAFÍO DE RECORRIDO|コースチャレンジ|DÉFI DE PARCOURS|STRECKENAUFGABE|SFIDA PERCORSO|PARKUR GÖREVİ|DESAFIO DE PERCURSO|मार्ग चुनौती|赛道挑战|코스 도전|ИСПЫТАНИЕ МАРШРУТА
Mesmo codigo e mesma semente inicial|Mismo código y semilla inicial|同じコード・同じ初期シード|Même code et même graine|Gleicher Code und Startwert|Stesso codice e seme iniziale|Aynı kod ve başlangıç tohumu|Mesmo código e semente inicial|एक ही कोड और शुरुआती सीड|相同代码与初始种子|같은 코드와 시작 시드|Один код и начальное зерно
JOGAR DESAFIO DO DIA|JUGAR DESAFÍO DEL DÍA|本日のチャレンジ|DÉFI DU JOUR|TAGESCHALLENGE SPIELEN|GIOCA SFIDA DEL GIORNO|GÜNÜN GÖREVİNİ OYNA|JOGAR DESAFIO DO DIA|आज की चुनौती खेलें|开始今日挑战|오늘의 도전 플레이|ИГРАТЬ ЗАДАНИЕ ДНЯ
CODIGO: TOQUE NUM DIGITO PARA MUDAR|CÓDIGO: TOCA UN DÍGITO PARA CAMBIAR|コード：数字を押して変更|CODE : TOUCHEZ UN CHIFFRE|CODE: ZIFFER ANTIPPEN|CODICE: TOCCA UNA CIFRA|KOD: RAKAMA DOKUN|CÓDIGO: TOQUE NUM DÍGITO|कोड: अंक छूकर बदलें|代码：点击数字修改|코드: 숫자를 눌러 변경|КОД: НАЖМИТЕ НА ЦИФРУ
Compartilhe o codigo manualmente|Comparte el código manualmente|コードを手動で共有|Partagez le code manuellement|Code manuell teilen|Condividi il codice a mano|Kodu elle paylaş|Partilhe o código manualmente|कोड खुद साझा करें|手动分享代码|코드를 직접 공유하세요|Поделитесь кодом вручную
Sem ranking online; percursos podem variar|Sin ranking online; los recorridos pueden variar|オンライン順位なし・コースは変化する場合あり|Pas de classement en ligne ; parcours variables|Keine Online-Rangliste; Strecke kann variieren|Nessuna classifica online; percorsi variabili|Çevrimiçi sıralama yok; parkur değişebilir|Sem classificação online; percursos podem variar|ऑनलाइन रैंकिंग नहीं; मार्ग बदल सकता है|无在线排行；赛道可能不同|온라인 순위 없음; 코스가 다를 수 있음|Без онлайн-рейтинга; маршруты могут отличаться
Melhores corridas salvas neste dispositivo|Mejores partidas guardadas en este dispositivo|この端末のベスト記録|Meilleures courses de cet appareil|Beste Läufe auf diesem Gerät|Migliori corse su questo dispositivo|Bu cihazda kayıtlı en iyi koşular|Melhores corridas guardadas neste dispositivo|इस डिवाइस की सर्वश्रेष्ठ दौड़|本设备保存的最佳跑步记录|이 기기에 저장된 최고 기록|Лучшие забеги на этом устройстве
Jogue uma partida para registrar seu primeiro resultado.|Juega una partida para registrar tu primer resultado.|プレイして最初の記録を残そう。|Jouez une partie pour enregistrer votre premier score.|Spiele, um deinen ersten Rekord zu speichern.|Gioca per salvare il tuo primo risultato.|İlk sonucunu kaydetmek için oyna.|Jogue para guardar o seu primeiro resultado.|पहला परिणाम दर्ज करने के लिए खेलें।|进行一局以记录首个成绩。|첫 기록을 남기려면 플레이하세요.|Сыграйте, чтобы сохранить первый результат.
DESAFIOS LOCAIS (recompensa única)|DESAFÍOS LOCALES (premio único)|ローカルチャレンジ（報酬1回）|DÉFIS LOCAUX (gain unique)|LOKALE AUFGABEN (einmaliger Preis)|SFIDE LOCALI (premio unico)|YEREL GÖREVLER (tek ödül)|DESAFIOS LOCAIS (prémio único)|स्थानीय चुनौतियाँ (एक बार इनाम)|本地挑战（单次奖励）|로컬 도전 (1회 보상)|МЕСТНЫЕ ЗАДАНИЯ (разовая награда)
RECORDES E PROGRESSO DO BIOMA|RÉCORDS Y PROGRESO DEL BIOMA|バイオーム別の記録と進捗|RECORDS ET PROGRÈS DU BIOME|REKORDE UND BIOM-FORTSCHRITT|RECORD E PROGRESSI DEL BIOMA|BİYOM REKORU VE İLERLEME|RECORDES E PROGRESSO DO BIOMA|क्षेत्र के रिकॉर्ड और प्रगति|生态区纪录与进度|지역 기록 및 진행도|РЕКОРДЫ И ПРОГРЕСС БИОМА
Sua base exibe troféus e lembranças da coleção.|Tu base muestra trofeos y recuerdos de la colección.|基地にはトロフィーや記念品が飾られます。|Votre base expose trophées et souvenirs.|Deine Basis zeigt Trophäen und Andenken.|La base mostra trofei e ricordi.|Üssünde kupalar ve hatıralar sergilenir.|A sua base exibe troféus e lembranças.|आपका अड्डा ट्रॉफ़ी और यादगार दिखाता है।|基地展示奖杯和收藏纪念品。|기지에서 트로피와 수집품을 볼 수 있습니다.|На базе хранятся трофеи и сувениры.
Decorações são cosméticas; não alteram atributos.|La decoración es estética; no cambia atributos.|装飾は見た目のみで能力に影響しません。|Les décors sont esthétiques, sans bonus.|Deko ist rein optisch, ohne Boni.|Le decorazioni sono solo estetiche.|Süsler sadece görseldir; özellik değiştirmez.|As decorações são cosméticas; não alteram atributos.|सजावट केवल दिखावटी है; गुण नहीं बदलते।|装饰仅影响外观，不改变属性。|장식은 외형만 바꾸고 능력치는 그대로입니다.|Украшения не влияют на характеристики.
TROFÉUS DE CHEFES|TROFEOS DE JEFES|ボスのトロフィー|TROPHÉES DES BOSS|BOSS-TROPHÄEN|TROFEI DEI BOSS|BOSS KUPALARI|TROFÉUS DE CHEFES|बॉस ट्रॉफ़ी|首领奖杯|보스 트로피|ТРОФЕИ БОССОВ
SKINS|ASPECTOS|スキン|SKINS|SKINS|SKIN|GÖRÜNÜMLER|VISUAIS|स्किन|皮肤|스킨|ОБЛИКИ
PETS|MASCOTAS|ペット|COMPAGNONS|HAUSTIERE|PET|EVCİL HAYVANLAR|ANIMAIS|पालतू साथी|宠物|펫|ПИТОМЦЫ
DISPONÍVEL|DISPONIBLE|利用可能|DISPONIBLE|VERFÜGBAR|DISPONIBILE|MEVCUT|DISPONÍVEL|उपलब्ध|可用|사용 가능|ДОСТУПНО
BLOQ.|BLOQ.|ロック|VERR.|GESP.|BLOCC.|KİLİTLİ|BLOQ.|लॉक|锁定|잠김|ЗАКР.
EQUIPADO|EQUIPADO|装備中|ÉQUIPÉ|AUSGERÜSTET|EQUIPAGGIATO|KUŞANILDI|EQUIPADO|सुसज्जित|已装备|장착됨|НАДЕТО
LIVRE|LIBRE|自由|LIBRE|FREI|LIBERO|BOŞ|LIVRE|मुक्त|空闲|자유|СВОБОДЕН
LOCK|BLOQ.|ロック|VERROU|SPERRE|BLOCC.|KİLİT|BLOQ.|लॉक|锁定|잠김|ЗАКР.
Nenhum|Ninguno|なし|Aucun|Keine|Nessuno|Yok|Nenhum|कोई नहीं|无|없음|Нет
DESBLOQUEADA • TOQUE PARA EQUIPAR|DESBLOQUEADA • TOCA PARA EQUIPAR|解放済み・タップで装備|DÉVERROUILLÉE • TOUCHEZ|FREI • ZUM ANLEGEN TIPPEN|SBLOCCATA • TOCCA PER EQUIPARE|AÇIK • KUŞANMAK İÇİN DOKUN|DESBLOQUEADA • TOQUE PARA EQUIPAR|अनलॉक • पहनने हेतु छुएँ|已解锁 • 点击装备|해제됨 • 눌러 장착|ОТКРЫТО • НАЖМИТЕ ДЛЯ НАДЕВАНИЯ
VOLTAR À LOJA|VOLVER A TIENDA|ショップに戻る|RETOUR BOUTIQUE|ZUM SHOP ZURÜCK|TORNA AL NEGOZIO|MAĞAZAYA DÖN|VOLTAR À LOJA|दुकान लौटें|返回商店|상점으로 돌아가기|В МАГАЗИН
DESAFIOS POR CODIGO|DESAFÍOS POR CÓDIGO|コードチャレンジ|DÉFIS PAR CODE|CODE-AUFGABEN|SFIDE CON CODICE|KOD GÖREVLERİ|DESAFIOS POR CÓDIGO|कोड चुनौतियाँ|代码挑战|코드 도전|ИСПЫТАНИЯ ПО КОДУ
Carinhos|Caricias|なでる|Caresses|Streicheln|Carezze|Sevgi|Carinhos|दुलार|抚摸|쓰다듬기|Ласка
Brincar|Jugar|遊ぶ|Jouer|Spielen|Giocare|Oyna|Brincar|खेलना|玩耍|놀기|Играть
Memórias|Recuerdos|思い出|Souvenirs|Erinnerungen|Ricordi|Anılar|Memórias|यादें|回忆|추억|Воспоминания
CONCLUÍDO|COMPLETADO|達成|TERMINÉ|ERLEDIGT|COMPLETATO|TAMAMLANDI|CONCLUÍDO|पूर्ण|完成|완료|ВЫПОЛНЕНО
RECOMPENSA|PREMIO|報酬|RÉCOMPENSE|BELOHNUNG|PREMIO|ÖDÜL|RECOMPENSA|इनाम|奖励|보상|НАГРАДА
MOEDAS|MONEDAS|コイン|PIÈCES|MÜNZEN|MONETE|ALTIN|MOEDAS|सिक्के|金币|코인|МОНЕТЫ
'''
_LINHAS += '''
Percorra 1200 metros|Corre 1200 metros|1200メートル走る|Parcourez 1200 mètres|Laufe 1200 Meter|Corri per 1200 metri|1200 metre koş|Percorra 1200 metros|1200 मीटर दौड़ें|奔跑1200米|1200미터 달리기|Пробегите 1200 метров
Colete 250 moedas|Recoge 250 monedas|コインを250枚集める|Ramassez 250 pièces|Sammle 250 Münzen|Raccogli 250 monete|250 altın topla|Recolha 250 moedas|250 सिक्के जुटाएँ|收集250金币|코인 250개 모으기|Соберите 250 монет
Faça 8 quase colisões|Logra 8 casi choques|ニアミスを8回達成|Faites 8 frôlements|Schaffe 8 Beinahe-Treffer|Fai 8 sfioramenti|8 yakın tehlike atlat|Faça 8 quase colisões|8 बाल-बाल बचाव करें|达成8次惊险闪避|아슬아슬 회피 8회|Совершите 8 опасных сближений
Alcance combo de 25|Logra un combo de 25|コンボ25を達成|Atteignez un combo de 25|Erreiche Combo 25|Raggiungi combo 25|25 kombo yap|Alcance combo de 25|25 का कॉम्बो बनाएँ|达成25连击|25콤보 달성|Достигните комбо 25
Visite 2 biomas na mesma corrida|Visita 2 biomas en una partida|1回で2つのバイオームを訪れる|Visitez 2 biomes en une partie|Besuche 2 Biome in einem Lauf|Visita 2 biomi in una corsa|Tek koşuda 2 biyom gör|Visite 2 biomas numa corrida|एक दौड़ में 2 क्षेत्र जाएँ|单局访问2个生态区|한 판에 지역 2곳 방문|Посетите 2 биома за забег
Percorra 12000 metros|Corre 12000 metros|12000メートル走る|Parcourez 12000 mètres|Laufe 12000 Meter|Corri per 12000 metri|12000 metre koş|Percorra 12000 metros|12000 मीटर दौड़ें|奔跑12000米|12000미터 달리기|Пробегите 12000 метров
Colete 2500 moedas|Recoge 2500 monedas|コインを2500枚集める|Ramassez 2500 pièces|Sammle 2500 Münzen|Raccogli 2500 monete|2500 altın topla|Recolha 2500 moedas|2500 सिक्के जुटाएँ|收集2500金币|코인 2500개 모으기|Соберите 2500 монет
Jogue 20 corridas|Juega 20 partidas|20回プレイする|Jouez 20 parties|Spiele 20 Läufe|Gioca 20 partite|20 kez oyna|Jogue 20 partidas|20 दौड़ खेलें|完成20局|20판 플레이|Сыграйте 20 забегов
Faça 100 quase colisões|Logra 100 casi choques|ニアミスを100回達成|Faites 100 frôlements|Schaffe 100 Beinahe-Treffer|Fai 100 sfioramenti|100 yakın tehlike atlat|Faça 100 quase colisões|100 बाल-बाल बचाव करें|达成100次惊险闪避|아슬아슬 회피 100회|Совершите 100 опасных сближений
Visite 5 biomas diferentes|Visita 5 biomas distintos|5つのバイオームを訪れる|Visitez 5 biomes différents|Besuche 5 verschiedene Biome|Visita 5 biomi diversi|5 farklı biyom gör|Visite 5 biomas diferentes|5 अलग क्षेत्रों में जाएँ|访问5个不同生态区|서로 다른 지역 5곳 방문|Посетите 5 разных биомов
Ímã Ancestral|Imán ancestral|古代の磁石|Aimant ancestral|Uralter Magnet|Magnete ancestrale|Kadim Mıknatıs|Íman Ancestral|प्राचीन चुंबक|远古磁铁|고대 자석|Древний магнит
Coração da Fênix|Corazón del fénix|不死鳥の心臓|Cœur du phénix|Phönixherz|Cuore della fenice|Anka Kalbi|Coração da Fénix|फ़ीनिक्स का दिल|凤凰之心|불사조의 심장|Сердце феникса
Núcleo Titã|Núcleo titán|タイタンの核|Noyau du titan|Titanenkern|Nucleo titanico|Titan Çekirdeği|Núcleo Titã|टाइटन कोर|泰坦核心|타이탄 핵|Ядро титана
Pérola Abissal|Perla abisal|深淵の真珠|Perle abyssale|Abgrundperle|Perla abissale|Uçurum İncisi|Pérola Abissal|अथाह मोती|深渊珍珠|심연의 진주|Жемчужина бездны
Ampulheta do Eco|Reloj de arena del eco|こだまの砂時計|Sablier de l'écho|Echosanduhr|Clessidra dell'eco|Yankı Kum Saati|Ampulheta do Eco|प्रतिध्वनि घड़ी|回响沙漏|메아리 모래시계|Песочные часы эха
Mapa Abissal|Mapa abisal|深淵の地図|Carte abyssale|Abgrundkarte|Mappa abissale|Uçurum Haritası|Mapa Abissal|अथाह मानचित्र|深渊地图|심연 지도|Карта бездны
Rosa dos Ventos|Rosa de los vientos|風配図|Rose des vents|Windrose|Rosa dei venti|Pusula Gülü|Rosa dos Ventos|दिशासूचक|风向玫瑰|나침반 장미|Роза ветров
+5% moedas em portais|+5% monedas en portales|ポータルのコイン+5%|+5 % pièces dans les portails|+5 % Münzen in Portalen|+5% monete nei portali|Portallarda +%5 altın|+5% moedas nos portais|पोर्टल सिक्के +5%|传送门金币+5%|포털 코인 +5%|+5% монет в порталах
Uma proteção extra a cada 3 níveis|Una protección extra cada 3 niveles|3レベルごとに追加シールド|Une protection tous les 3 niveaux|Extraschutz alle 3 Stufen|Una protezione ogni 3 livelli|Her 3 seviyede ekstra kalkan|Uma proteção extra a cada 3 níveis|हर 3 स्तर पर अतिरिक्त रक्षा|每3级额外护盾|3레벨마다 추가 보호막|Доп. защита каждые 3 уровня
+1 ponto de vida contra chefes|+1 vida contra jefes|ボス戦でHP+1|+1 PV contre les boss|+1 HP gegen Bosse|+1 vita contro i boss|Bosslara karşı +1 can|+1 vida contra chefes|बॉस के विरुद्ध +1 जीवन|对首领生命+1|보스전 체력 +1|+1 здоровье против боссов
+15% recompensas de biomas lendários|+15% premios de biomas legendarios|伝説のバイオーム報酬+15%|+15 % gains en biomes légendaires|+15 % Belohnung in legendären Biomen|+15% premi nei biomi leggendari|Efsanevi biyom ödülü +%15|+15% prémios em biomas lendários|पौराणिक क्षेत्र इनाम +15%|传说生态区奖励+15%|전설 지역 보상 +15%|+15% наград легендарных биомов
+10% XP permanente|+10% XP permanente|恒久XP+10%|+10 % XP permanent|+10 % dauerhafte EP|+10% XP permanente|Kalıcı XP +%10|+10% XP permanente|स्थायी XP +10%|永久经验+10%|영구 XP +10%|+10% постоянного опыта
+8% de moedas em rotas arriscadas|+8% monedas en rutas peligrosas|危険なルートのコイン+8%|+8 % pièces sur routes à risque|+8 % Münzen auf riskanten Routen|+8% monete su percorsi rischiosi|Riskli yollarda +%8 altın|+8% moedas em rotas arriscadas|जोखिमपूर्ण मार्ग सिक्के +8%|危险路线金币+8%|위험 경로 코인 +8%|+8% монет на опасных маршрутах
+8% de XP permanente|+8% XP permanente|恒久XP+8%|+8 % XP permanent|+8 % dauerhafte EP|+8% XP permanente|Kalıcı XP +%8|+8% XP permanente|स्थायी XP +8%|永久经验+8%|영구 XP +8%|+8% постоянного опыта
Colete 500 moedas|Recoge 500 monedas|コインを500枚集める|Ramassez 500 pièces|Sammle 500 Münzen|Raccogli 500 monete|500 altın topla|Recolha 500 moedas|500 सिक्के जुटाएँ|收集500金币|코인 500개 모으기|Соберите 500 монет
Sobreviva a 25 corridas|Sobrevive a 25 partidas|25回生き残る|Survivez à 25 parties|Überlebe 25 Läufe|Sopravvivi a 25 corse|25 koşudan sağ çık|Sobreviva a 25 corridas|25 दौड़ में बचें|存活25局|25회 살아남기|Выживите в 25 забегах
Derrote 5 chefes|Derrota a 5 jefes|ボスを5体倒す|Vainquez 5 boss|Besiege 5 Bosse|Sconfiggi 5 boss|5 boss yen|Derrote 5 chefes|5 बॉस हराएँ|击败5名首领|보스 5명 처치|Победите 5 боссов
Visite 3 biomas lendários|Visita 3 biomas legendarios|伝説のバイオーム3つを訪れる|Visitez 3 biomes légendaires|Besuche 3 legendäre Biome|Visita 3 biomi leggendari|3 efsanevi biyom gör|Visite 3 biomas lendários|3 पौराणिक क्षेत्र जाएँ|访问3个传说生态区|전설 지역 3곳 방문|Посетите 3 легендарных биома
Alcance 10.000 m totais|Alcanza 10.000 m totales|合計10000mを達成|Atteignez 10 000 m au total|Erreiche insgesamt 10.000 m|Raggiungi 10.000 m totali|Toplam 10.000 m koş|Alcance 10.000 m no total|कुल 10,000 मीटर पहुँचें|累计达到10000米|총 10,000m 달성|Пробегите всего 10 000 м
Reúna 8 fragmentos de relíquia|Reúne 8 fragmentos de reliquia|遺物の欠片を8個集める|Réunissez 8 fragments de relique|Sammle 8 Reliktfragmente|Raccogli 8 frammenti di reliquia|8 kalıntı parçası topla|Reúna 8 fragmentos de relíquia|8 अवशेष के टुकड़े जुटाएँ|收集8个遗物碎片|유물 조각 8개 모으기|Соберите 8 фрагментов реликвий
Reúna 16 fragmentos de relíquia|Reúne 16 fragmentos de reliquia|遺物の欠片を16個集める|Réunissez 16 fragments de relique|Sammle 16 Reliktfragmente|Raccogli 16 frammenti di reliquia|16 kalıntı parçası topla|Reúna 16 fragmentos de relíquia|16 अवशेष के टुकड़े जुटाएँ|收集16个遗物碎片|유물 조각 16개 모으기|Соберите 16 фрагментов реликвий
'''
_LINHAS += '''
Recursos visuais opcionais. Mesma jogabilidade.|Ayudas visuales opcionales. Sin cambios de juego.|表示補助のみ・ゲーム性は同じ|Aides visuelles sans changer le jeu.|Visuelle Hilfen; Spielablauf bleibt gleich.|Aiuti visivi senza cambiare il gioco.|Görsel yardımlar; oynanış aynı.|Ajudas visuais; jogabilidade igual.|दृश्य सहायता; खेल वही रहता है।|仅显示辅助；玩法不变。|시각 보조만 제공하며 플레이는 동일함|Визуальные настройки без изменения игры.
CONTRASTE DOS PERIGOS|CONTRASTE DE PELIGROS|危険物のコントラスト|CONTRASTE DES DANGERS|GEFAHRENKONTRAST|CONTRASTO DEI PERICOLI|TEHLİKE KONTRASTI|CONTRASTE DOS PERIGOS|खतरों का कंट्रास्ट|危险对比度|위험물 대비|КОНТРАСТ ОПАСНОСТЕЙ
SINAIS SEM DEPENDER DE COR|SEÑALES SIN COLOR|色に頼らない標識|SIGNES SANS COULEUR|ZEICHEN OHNE FARBE|SEGNALI SENZA COLORE|RENKSİZ İŞARETLER|SINAIS SEM COR|बिना रंग के संकेत|无颜色依赖标识|색에 의존하지 않는 표식|ЗНАКИ БЕЗ ЦВЕТА
REDUZIR FLASHES / CAMERA|REDUCIR DESTELLOS / CÁMARA|点滅・カメラ動作を減らす|RÉDUIRE FLASH / CAMÉRA|BLITZE / KAMERA REDUZIEREN|RIDUCI LAMPI / CAMERA|PARLAMA / KAMERA AZALT|REDUZIR FLASHES / CÂMARA|चमक / कैमरा घटाएँ|减少闪烁与镜头晃动|섬광 / 카메라 감소|УМЕНЬШИТЬ ВСПЫШКИ
Destaque sem modificar hitboxes.|Resaltado sin alterar colisiones.|当たり判定は変わりません。|Contours sans changer les collisions.|Umrisse ändern keine Trefferzonen.|Evidenza senza cambiare collisioni.|Vuruş alanı değişmez.|Destaque sem alterar colisões.|टक्कर क्षेत्र नहीं बदलता।|不会改变碰撞范围。|충돌 범위는 그대로입니다.|Обводка не меняет столкновения.
Sinais: solo / voador / buraco.|Señales: suelo / aire / hueco.|標識：地上・飛行・穴|Signes : sol / air / trou.|Zeichen: Boden / Flug / Lücke.|Segni: suolo / volo / buca.|İşaret: yer / uçan / çukur.|Sinais: solo / aéreo / buraco.|संकेत: ज़मीन / उड़ान / गड्ढा।|标识：地面 / 飞行 / 深坑。|표식: 지상 / 비행 / 구멍.|Знаки: земля / полёт / яма.
Sem flashes fortes e movimentos de camera.|Sin destellos fuertes ni sacudidas.|強い点滅や揺れを抑えます。|Sans flash violent ni secousse.|Keine starken Blitze oder Kamerawackeln.|Niente lampi o scosse forti.|Güçlü parlama ve sarsıntı yok.|Sem flashes fortes nem abanões.|तेज़ चमक या कैमरा झटके नहीं।|避免强闪光及镜头晃动。|강한 섬광과 흔들림 방지.|Без ярких вспышек и тряски.
SALVAR E VOLTAR|GUARDAR Y VOLVER|保存して戻る|ENREGISTRER ET REVENIR|SPEICHERN UND ZURÜCK|SALVA E TORNA|KAYDET VE DÖN|GUARDAR E VOLTAR|सहेजें और लौटें|保存并返回|저장 후 돌아가기|СОХРАНИТЬ И НАЗАД
CONTROLES PRO|CONTROLES AVANZADOS|詳細操作設定|COMMANDES AVANCÉES|ERWEITERTE STEUERUNG|COMANDI AVANZATI|GELİŞMİŞ KONTROLLER|CONTROLOS PRO|उन्नत नियंत्रण|高级控制|고급 조작|РАСШИРЕННОЕ УПРАВЛЕНИЕ
Estilo|Estilo|スタイル|Style|Stil|Stile|Stil|Estilo|शैली|风格|스타일|Стиль
Clássico|Clásico|クラシック|Classique|Klassisch|Classico|Klasik|Clássico|क्लासिक|经典|클래식|Классика
Gestos|Gestos|ジェスチャー|Gestes|Gesten|Gesti|Hareketler|Gestos|इशारे|手势|제스처|Жесты
2 botões|2 botones|2ボタン|2 boutons|2 Tasten|2 pulsanti|2 düğme|2 botões|2 बटन|2按钮|버튼 2개|2 кнопки
Sensibilidade|Sensibilidad|感度|Sensibilité|Empfindlichkeit|Sensibilità|Hassasiyet|Sensibilidade|संवेदनशीलता|灵敏度|민감도|Чувствительность
Mão dominante|Mano dominante|利き手|Main dominante|Führende Hand|Mano dominante|Baskın el|Mão dominante|प्रमुख हाथ|惯用手|주로 쓰는 손|Ведущая рука
Canhoto|Zurdo|左利き|Gaucher|Linkshändig|Mancino|Solak|Canhoto|बायाँ हाथ|左手|왼손잡이|Левша
Destro|Diestro|右利き|Droitier|Rechtshändig|Destro|Sağlak|Destro|दायाँ हाथ|右手|오른손잡이|Правша
Ajuda de pulo|Ayuda de salto|ジャンプ補助|Aide au saut|Sprunghilfe|Aiuto salto|Zıplama yardımı|Ajuda de salto|कूद सहायता|跳跃辅助|점프 보조|Помощь с прыжком
Ligada|Activada|オン|Activée|An|Attiva|Açık|Ligada|चालू|开启|켜짐|Включено
Desligada|Desactivada|オフ|Désactivée|Aus|Disattiva|Kapalı|Desligada|बंद|关闭|꺼짐|Выключено
Controle externo|Mando externo|ゲームパッド|Manette|Gamepad|Controller|Oyun kolu|Comando externo|गेमपैड|手柄|게임패드|Геймпад
Ligado|Activado|オン|Activé|An|Attivo|Açık|Ligado|चालू|开启|켜짐|Включено
Desligado|Desactivado|オフ|Désactivé|Aus|Disattivo|Kapalı|Desligado|बंद|关闭|꺼짐|Выключено
Toque: pular  /  Arrastar: agachar|Toque: saltar; arrastra: agacharse|タップ：ジャンプ・ドラッグ：しゃがむ|Touchez : saut / Glissez : baisser|Tippen: Sprung / Ziehen: Ducken|Tocca: salta / Trascina: abbassati|Dokun: zıpla / Sürükle: eğil|Toque: salto / Arraste: agachar|छुएँ: कूदें / खींचें: झुकें|轻触跳跃 / 拖动下蹲|탭: 점프 / 드래그: 숙이기|Касание: прыжок / свайп: присесть
Deslize para cima/baixo|Desliza arriba/abajo|上下にスワイプ|Glissez vers le haut/bas|Nach oben/unten wischen|Scorri su/giù|Yukarı/aşağı kaydır|Deslize cima/baixo|ऊपर/नीचे स्वाइप करें|上下滑动|위/아래로 스와이프|Проведите вверх/вниз
Pule e agache com 2 polegares|Salta y agáchate con 2 pulgares|両親指でジャンプ・しゃがむ|Sautez et baissez-vous avec 2 pouces|Mit 2 Daumen springen/ducken|Salta e abbassati con 2 pollici|İki başparmakla zıpla/eğil|Salte e agache-se com 2 polegares|दो अंगूठों से कूदें/झुकें|双拇指操作跳跃和下蹲|두 엄지로 점프·숙이기|Прыжок и приседание двумя пальцами
SALVAR / VOLTAR|GUARDAR / VOLVER|保存 / 戻る|SAUVER / RETOUR|SPEICHERN / ZURÜCK|SALVA / TORNA|KAYDET / DÖN|GUARDAR / VOLTAR|सहेजें / लौटें|保存 / 返回|저장 / 뒤로|СОХРАНИТЬ / НАЗАД
PULAR|SALTAR|ジャンプ|SAUTER|SPRINGEN|SALTA|ZIPLA|SALTAR|कूदें|跳跃|점프|ПРЫЖОК
BAIXO|AGACHAR|しゃがむ|BAISSER|DUCKEN|ABBASSATI|EĞİL|BAIXO|झुकें|下蹲|숙이기|ПРИСЕСТЬ
'''
_LINHAS += '''
Rotina de Campeão|Rutina de campeón|チャンピオンの日課|Routine de champion|Champion-Routine|Routine da campione|Şampiyon rutini|Rotina de Campeão|विजेता दिनचर्या|冠军日常|챔피언 루틴|Режим чемпиона
Conclua 30 desafios diários|Completa 30 desafíos diarios|デイリーチャレンジ30回達成|Terminez 30 défis quotidiens|Schaffe 30 Tagesaufgaben|Completa 30 sfide giornaliere|30 günlük görev tamamla|Conclua 30 desafios diários|30 दैनिक चुनौतियाँ पूरी करें|完成30次每日挑战|일일 도전 30회 완료|Выполните 30 ежедневных заданий
Lenda Semanal|Leyenda semanal|週間の伝説|Légende hebdomadaire|Wochenlegende|Leggenda settimanale|Haftanın efsanesi|Lenda Semanal|साप्ताहिक दिग्गज|每周传奇|주간 전설|Легенда недели
Conclua 12 desafios semanais|Completa 12 desafíos semanales|週間チャレンジ12回達成|Terminez 12 défis hebdomadaires|Schaffe 12 Wochenaufgaben|Completa 12 sfide settimanali|12 haftalık görev tamamla|Conclua 12 desafios semanais|12 साप्ताहिक चुनौतियाँ पूरी करें|完成12次每周挑战|주간 도전 12회 완료|Выполните 12 еженедельных заданий
Melhor Amigo|Mejor amigo|親友|Meilleur ami|Bester Freund|Migliore amico|En iyi dost|Melhor Amigo|सबसे अच्छा दोस्त|最好的伙伴|단짝 친구|Лучший друг
Desbloqueie 5 pets|Desbloquea 5 mascotas|ペット5体を解放|Débloquez 5 compagnons|Schalte 5 Haustiere frei|Sblocca 5 pet|5 evcil hayvan aç|Desbloqueie 5 animais|5 पालतू साथी खोलें|解锁5只宠物|펫 5마리 해제|Откройте 5 питомцев
Estilista Supremo|Estilista supremo|究極のスタイリスト|Styliste suprême|Stilmeister|Stilista supremo|Stil ustası|Estilista Supremo|श्रेष्ठ स्टाइलिस्ट|造型大师|최고 스타일리스트|Мастер стиля
Desbloqueie 12 skins|Desbloquea 12 aspectos|スキン12個を解放|Débloquez 12 skins|Schalte 12 Skins frei|Sblocca 12 skin|12 görünüm aç|Desbloqueie 12 visuais|12 स्किन खोलें|解锁12款皮肤|스킨 12개 해제|Откройте 12 обликов
Rei da Cidade|Rey de la ciudad|街の王|Roi de la ville|König der Stadt|Re della città|Şehir kralı|Rei da Cidade|शहर का राजा|城市之王|도시의 왕|Король города
Percorra 10000 m na cidade|Corre 10000 m en la ciudad|街で10000m走る|Parcourez 10000 m en ville|Laufe 10000 m in der Stadt|Percorri 10000 m in città|Şehirde 10000 m koş|Percorra 10000 m na cidade|शहर में 10000 मी दौड़ें|在城市奔跑10000米|도시에서 10000m 달리기|Пробегите 10000 м в городе
Dono das Dunas|Dueño de las dunas|砂丘の支配者|Maître des dunes|Herr der Dünen|Signore delle dune|Kumulların efendisi|Dono das Dunas|रेत का स्वामी|沙丘之主|모래언덕의 주인|Повелитель дюн
Percorra 10000 m no deserto|Corre 10000 m en el desierto|砂漠で10000m走る|Parcourez 10000 m au désert|Laufe 10000 m in der Wüste|Percorri 10000 m nel deserto|Çölde 10000 m koş|Percorra 10000 m no deserto|रेगिस्तान में 10000 मी दौड़ें|在沙漠奔跑10000米|사막에서 10000m 달리기|Пробегите 10000 м в пустыне
Lenda do Gelo|Leyenda del hielo|氷の伝説|Légende de glace|Eislegende|Leggenda di ghiaccio|Buz efsanesi|Lenda do Gelo|बर्फ की किंवदंती|寒冰传奇|얼음의 전설|Ледяная легенда
Percorra 10000 m na neve|Corre 10000 m en la nieve|雪の街で10000m走る|Parcourez 10000 m dans la neige|Laufe 10000 m im Schnee|Percorri 10000 m nella neve|Karda 10000 m koş|Percorra 10000 m na neve|बर्फ में 10000 मी दौड़ें|在雪地奔跑10000米|눈에서 10000m 달리기|Пробегите 10000 м по снегу
Colecionador de Poder|Coleccionista de poder|パワーコレクター|Collectionneur de pouvoirs|Power-Sammler|Collezionista di poteri|Güç koleksiyoncusu|Colecionador de Poder|शक्ति संग्राहक|能力收藏家|파워 수집가|Коллекционер усилений
Colete 1000 power-ups|Recoge 1000 potenciadores|パワーアップを1000個獲得|Ramassez 1000 bonus|Sammle 1000 Power-ups|Raccogli 1000 potenziamenti|1000 güçlendirici topla|Recolha 1000 potenciadores|1000 पावर-अप पाएँ|收集1000个强化道具|파워업 1000개 모으기|Соберите 1000 усилений
Febre Absoluta|Fiebre absoluta|完全フィーバー|Fièvre absolue|Absolutes Fieber|Febbre assoluta|Mutlak ateş|Febre Absoluta|पूर्ण फ़ीवर|极限狂热|완전 피버|Абсолютная лихорадка
Ative 5 febres em uma corrida|Activa 5 fiebres en una partida|1回でフィーバーを5回発動|Activez 5 fièvres en une partie|Aktiviere 5-mal Fieber pro Lauf|Attiva 5 febbri in una corsa|Bir koşuda 5 ateş modu aç|Ative 5 febres numa corrida|एक दौड़ में 5 फ़ीवर चलाएँ|单局触发5次狂热|한 판에 피버 5회 발동|Активируйте 5 лихорадок за забег
Combo Lendário|Combo legendario|伝説のコンボ|Combo légendaire|Legendäre Combo|Combo leggendaria|Efsanevi kombo|Combo Lendário|महान कॉम्बो|传说连击|전설의 콤보|Легендарное комбо
Alcance combo de 150 ações|Logra combo de 150 acciones|150アクションコンボを達成|Atteignez un combo de 150 actions|Erreiche eine 150er-Combo|Raggiungi una combo di 150 azioni|150 eylemlik kombo yap|Alcance combo de 150 ações|150 कार्यों का कॉम्बो बनाएँ|达成150次连击|150액션 콤보 달성|Достигните комбо 150 действий
Caçador de Tesouros|Cazador de tesoros|宝探し名人|Chasseur de trésors|Schatzjäger|Cacciatore di tesori|Hazine avcısı|Caçador de Tesouros|खज़ाना शिकारी|寻宝猎人|보물 사냥꾼|Охотник за сокровищами
Abra 500 baús secretos|Abre 500 cofres secretos|秘密の宝箱を500個開ける|Ouvrez 500 coffres secrets|Öffne 500 geheime Truhen|Apri 500 forzieri segreti|500 gizli sandık aç|Abra 500 baús secretos|500 गुप्त संदूक खोलें|开启500个秘密宝箱|비밀 상자 500개 열기|Откройте 500 тайных сундуков
Veterano Imortal|Veterano inmortal|不滅のベテラン|Vétéran immortel|Unsterblicher Veteran|Veterano immortale|Ölümsüz emektar|Veterano Imortal|अमर अनुभवी|不朽老兵|불멸의 베테랑|Бессмертный ветеран
Participe de 1000 corridas|Participa en 1000 partidas|1000回プレイする|Participez à 1000 parties|Spiele 1000 Läufe|Gioca 1000 partite|1000 koşuya katıl|Participe em 1000 corridas|1000 दौड़ खेलें|参加1000局|1000회 플레이|Сыграйте 1000 забегов
'''
_LINHAS += '''
CIDADE|CIUDAD|街|VILLE|STADT|CITTÀ|ŞEHİR|CIDADE|शहर|城市|도시|ГОРОД
DESERTO|DESIERTO|砂漠|DÉSERT|WÜSTE|DESERTO|ÇÖL|DESERTO|रेगिस्तान|沙漠|사막|ПУСТЫНЯ
NEVE|NIEVE|雪の街|NEIGE|SCHNEE|NEVE|KAR|NEVE|बर्फ़|雪地|설원|СНЕГ
VULCÃO|VOLCÁN|火山|VOLCAN|VULKAN|VULCANO|YANARDAĞ|VULCÃO|ज्वालामुखी|火山|화산|ВУЛКАН
CIDADE FUTURISTA|CIUDAD FUTURISTA|未来都市|VILLE FUTURISTE|ZUKUNFTSSTADT|CITTÀ FUTURISTICA|GELECEK ŞEHRİ|CIDADE FUTURISTA|भविष्य का शहर|未来都市|미래 도시|ГОРОД БУДУЩЕГО
FLORESTA DENSA|BOSQUE DENSO|密林|FORÊT DENSE|DICHTER WALD|FORESTA FITTA|SIK ORMAN|FLORESTA DENSA|घना जंगल|茂密森林|울창한 숲|ГУСТОЙ ЛЕС
ILHAS CELESTES|ISLAS CELESTIALES|天空の島々|ÎLES CÉLESTES|HIMMELSINSELN|ISOLE CELESTI|GÖK ADALARI|ILHAS CELESTIAIS|आकाशी द्वीप|天空群岛|하늘의 섬|НЕБЕСНЫЕ ОСТРОВА
EQUIPADA|EQUIPADA|装備中|ÉQUIPÉE|AUSGERÜSTET|EQUIPAGGIATA|KUŞANILDI|EQUIPADA|सुसज्जित|已装备|장착됨|НАДЕТО
Percorra 500 m|Recorre 500 m|500m走る|Parcourez 500 m|Laufe 500 m|Percorri 500 m|500 m koş|Percorra 500 m|500 मी दौड़ें|奔跑500米|500m 달리기|Пробегите 500 м
Alcance combo 30|Alcanza combo 30|コンボ30達成|Atteignez combo 30|Combo 30 erreichen|Raggiungi combo 30|30 kombo yap|Alcance combo 30|30 कॉम्बो बनाएँ|达成30连击|30콤보 달성|Достигните комбо 30
Derrote um chefe|Derrota a un jefe|ボスを1体倒す|Vainquez un boss|Besiege einen Boss|Sconfiggi un boss|Bir boss yen|Derrote um chefe|एक बॉस हराएँ|击败一名首领|보스 1명 처치|Победите босса
Consiga 500 moedas em uma corrida|Consigue 500 monedas en una partida|1回でコイン500枚|Gagnez 500 pièces en une partie|500 Münzen in einem Lauf|Ottieni 500 monete in una corsa|Tek koşuda 500 altın kazan|Obtenha 500 moedas numa corrida|एक दौड़ में 500 सिक्के पाएँ|单局获得500金币|한 판에 코인 500개|Получите 500 монет за забег
RECRUTA|RECLUTA|新兵|RECRUE|REKRUT|RECLUTA|ACEMİ|RECRUTA|नया खिलाड़ी|新手|신병|НОВОБРАНЕЦ
BRONZE|BRONCE|ブロンズ|BRONZE|BRONZE|BRONZO|BRONZ|BRONZE|कांस्य|青铜|브론즈|БРОНЗА
PRATA|PLATA|シルバー|ARGENT|SILBER|ARGENTO|GÜMÜŞ|PRATA|रजत|白银|실버|СЕРЕБРО
OURO|ORO|ゴールド|OR|GOLD|ORO|ALTIN|OURO|स्वर्ण|黄金|골드|ЗОЛОТО
PLATINA|PLATINO|プラチナ|PLATINE|PLATIN|PLATINO|PLATİN|PLATINA|प्लैटिनम|铂金|플래티넘|ПЛАТИНА
'''
_LINHAS += '''
COLEÇÃO COMPLETA!|¡COLECCIÓN COMPLETA!|コレクション完成！|COLLECTION COMPLÈTE !|SAMMLUNG VOLLSTÄNDIG!|COLLEZIONE COMPLETA!|KOLEKSİYON TAMAMLANDI!|COLEÇÃO COMPLETA!|संग्रह पूरा हुआ!|收藏已完成！|컬렉션 완료!|КОЛЛЕКЦИЯ СОБРАНА!
'''
_LINHAS += '''
PRONTA|LISTA|準備完了|PRÊTE|BEREIT|PRONTA|HAZIR|PRONTA|तैयार|就绪|준비됨|ГОТОВА
CORREDOR LASER|PASILLO LÁSER|レーザー通路|COULOIR LASER|LASERKORRIDOR|CORRIDOIO LASER|LAZER KORİDORU|CORREDOR LASER|लेज़र रास्ता|激光通道|레이저 통로|ЛАЗЕРНЫЙ КОРИДОР
Segure para subir / solte para descer|Mantén para subir / suelta para bajar|押すと上昇・離すと下降|Maintenez pour monter / relâchez pour descendre|Halten: hoch / loslassen: runter|Tieni per salire / rilascia per scendere|Yükselmek için tut / inmek için bırak|Segure para subir / largue para descer|ऊपर जाने को दबाएँ / नीचे को छोड़ें|按住上升 / 松开下降|누르면 상승 / 놓으면 하강|Удерживайте вверх / отпустите вниз
ATAQUE À VISTA! DESVIE|¡ATAQUE A LA VISTA! ¡ESQUIVA!|攻撃接近！避けて！|ATTAQUE ! ESQUIVEZ !|ANGRIFF! AUSWEICHEN!|ATTACCO! SCHIVA!|SALDIRI! KAÇIN!|ATAQUE À VISTA! ESQUIVE-SE!|हमला सामने! बचें!|攻击来袭！快躲开！|공격 임박! 피하세요!|АТАКА! УКЛОНИТЕСЬ!
AGACHE-SE! SENSOR À FRENTE|¡AGÁCHATE! SENSOR DELANTE|しゃがんで！センサー接近|BAISSEZ-VOUS ! CAPTEUR DEVANT|DUCKEN! SENSOR VORNE|ABBASSATI! SENSORE DAVANTI|EĞİL! SENSÖR ÖNDE|AGACHE-SE! SENSOR À FRENTE|झुकें! आगे सेंसर है!|下蹲！前方传感器！|숙이세요! 센서 접근!|ПРИСЕДАЙТЕ! ВПЕРЕДИ ДАТЧИК
SEGURE / DESLIZE PARA BAIXO|MANTÉN / DESLIZA ABAJO|押す・下へスワイプ|MAINTENIR / GLISSER VERS LE BAS|HALTEN / NACH UNTEN WISCHEN|TIENI / SCORRI IN BASSO|TUT / AŞAĞI KAYDIR|SEGURE / DESLIZE PARA BAIXO|दबाएँ / नीचे स्वाइप करें|按住 / 向下滑动|누르기 / 아래로 스와이프|УДЕРЖИВАЙТЕ / СВАЙП ВНИЗ
MENU DE TESTES|MENÚ DE PRUEBAS|テストメニュー|MENU DE TESTS|TESTMENÜ|MENU DI TEST|TEST MENÜSÜ|MENU DE TESTES|परीक्षण मेनू|测试菜单|테스트 메뉴|МЕНЮ ТЕСТОВ
Somente testes - progresso isolado|Solo pruebas: progreso independiente|テスト専用・進行状況は別保存|Tests seuls : sauvegarde séparée|Nur Tests: getrennter Spielstand|Solo test: progressi separati|Yalnızca test: kayıt ayrı|Apenas testes - progresso separado|केवल परीक्षण; प्रगति अलग|仅测试：进度独立|테스트 전용: 진행도 분리|Только тесты: отдельный прогресс
VOLTAR|VOLVER|戻る|RETOUR|ZURÜCK|INDIETRO|GERİ|VOLTAR|वापस|返回|뒤로|НАЗАД
'''
_LINHAS += '''
PATENTE / CORRIDAS|RANGO / CARRERAS|ランク・プレイ回数|RANG / COURSES|RANG / LÄUFE|GRADO / CORSE|RÜTBE / KOŞU|PATENTE / CORRIDAS|रैंक / दौड़|段位 / 对局|등급 / 게임|ЗВАНИЕ / ЗАБЕГИ
COLEÇÃO DE SKINS|COLECCIÓN DE ASPECTOS|スキンコレクション|COLLECTION DE SKINS|SKIN-SAMMLUNG|COLLEZIONE SKIN|GÖRÜNÜM KOLEKSİYONU|COLEÇÃO DE VISUAIS|स्किन संग्रह|皮肤收藏|스킨 컬렉션|КОЛЛЕКЦИЯ ОБЛИКОВ
RECORDE GERAL|RÉCORD GENERAL|総合最高記録|RECORD GÉNÉRAL|GESAMTREKORD|RECORD TOTALE|GENEL REKOR|RECORDE GERAL|कुल रिकॉर्ड|总纪录|전체 기록|ОБЩИЙ РЕКОРД
DISTÂNCIA TOTAL|DISTANCIA TOTAL|総走行距離|DISTANCE TOTALE|GESAMTSTRECKE|DISTANZA TOTALE|TOPLAM MESAFE|DISTÂNCIA TOTAL|कुल दूरी|总距离|총 거리|ОБЩАЯ ДИСТАНЦИЯ
MOEDAS COLETADAS|MONEDAS RECOGIDAS|獲得コイン|PIÈCES RAMASSÉES|GESAMMELTE MÜNZEN|MONETE RACCOLTE|TOPLANAN ALTIN|MOEDAS RECOLHIDAS|कुल सिक्के|收集金币|모은 코인|СОБРАНО МОНЕТ
MELHOR COMBO|MEJOR COMBO|最高コンボ|MEILLEUR COMBO|BESTE COMBO|MIGLIOR COMBO|EN İYİ KOMBO|MELHOR COMBO|सर्वश्रेष्ठ कॉम्बो|最高连击|최고 콤보|ЛУЧШЕЕ КОМБО
BASE|BASE|基地|BASE|BASIS|BASE|ÜS|BASE|अड्डा|基地|기지|БАЗА
RELÍQUIAS|RELIQUIAS|遺物|RELIQUES|RELIKTE|RELIQUIE|KALINTILAR|RELÍQUIAS|अवशेष|遗物|유물|РЕЛИКВИИ
CONQUISTAS|LOGROS|実績|SUCCÈS|ERFOLGE|TRAGUARDI|BAŞARILAR|CONQUISTAS|उपलब्धियाँ|成就|업적|ДОСТИЖЕНИЯ
'''
_LITERALS = {}
for _line in _LINHAS.strip().splitlines():
    if not _line.strip():
        continue
    _tokens = _line.split('|')
    if len(_tokens) != 12:
        raise ValueError(f'Tabela de localização secundária incompleta: {_tokens[0]} ({len(_tokens)})')
    _LITERALS[_tokens[0].replace('Toque: pular  /  Arrastar: agachar','Toque: pular | Arrastar: agachar')] = dict(zip(IDIOMAS, _tokens[1:]))

# Mensagens dinâmicas com valores vindos de saves; só a apresentação é alterada.
# Ordem das colunas é igual a IDIOMAS; chaves {n} etc não são alteradas.
_MODELOS = {
    'runs': ('{n} carreras','{n} 回','{n} courses','{n} Läufe','{n} corse','{n} koşu','{n} corridas','{n} दौड़','{n} 局','{n} 게임','{n} забегов'),
    'skins': ('{n} aspectos','{n} スキン','{n} skins','{n} Skins','{n} skin','{n} görünüm','{n} visuais','{n} स्किन','{n} 皮肤','{n} 스킨','{n} обликов'),
    'record_bioma': ('Récord en una carrera: {n} m','1回の最高記録: {n} m','Record d’une course : {n} m','Rekord pro Lauf: {n} m','Record in una corsa: {n} m','Tek koşu rekoru: {n} m','Recorde numa corrida: {n} m','एक दौड़ का रिकॉर्ड: {n} मी','单局纪录：{n} 米','한 판 기록: {n} m','Рекорд за забег: {n} м'),
    'distance_bioma': ('Distancia acumulada: {n} m','累計距離: {n} m','Distance cumulée : {n} m','Gesamtstrecke: {n} m','Distanza cumulata: {n} m','Toplam mesafe: {n} m','Distância acumulada: {n} m','कुल दूरी: {n} मी','累计距离：{n} 米','누적 거리: {n} m','Общая дистанция: {n} м'),
    'mastery_bioma': ('Maestría actual: nivel {n}/3','現在の熟練度: {n}/3','Maîtrise actuelle : niv. {n}/3','Meisterschaft: Stufe {n}/3','Maestria attuale: liv. {n}/3','Ustalık: seviye {n}/3','Maestria atual: nível {n}/3','मौजूदा कौशल: स्तर {n}/3','当前精通：等级 {n}/3','현재 숙련도: {n}/3','Мастерство: уровень {n}/3'),
    'achievementprogress': ('{n} LOGROS','{n} 実績','{n} SUCCÈS','{n} ERFOLGE','{n} TRAGUARDI','{n} BAŞARI','{n} CONQUISTAS','{n} उपलब्धियाँ','{n} 项成就','{n} 업적','{n} ДОСТИЖЕНИЯ'),
    'achievementreward': ('PREMIO: +{n}','報酬: +{n}','GAIN : +{n}','BELOHNUNG: +{n}','PREMIO: +{n}','ÖDÜL: +{n}','RECOMPENSA: +{n}','इनाम: +{n}','奖励：+{n}','보상: +{n}','НАГРАДА: +{n}'),
    'periodo': ('Período: {n}','期間: {n}','Période : {n}','Zeitraum: {n}','Periodo: {n}','Dönem: {n}','Período: {n}','अवधि: {n}','周期：{n}','기간: {n}','Период: {n}'),
    'reward': ('{n}  •  PREMIO {m} MONEDAS','{n}・報酬 {m} コイン','{n} • GAIN {m} PIÈCES','{n} • {m} MÜNZEN','{n} • PREMIO {m} MONETE','{n} • ÖDÜL {m} ALTIN','{n} • PRÉMIO {m} MOEDAS','{n} • इनाम {m} सिक्के','{n} • 奖励 {m} 金币','{n} • 보상 {m} 코인','{n} • НАГРАДА {m} МОНЕТ'),
    'collection': ('COLECCIÓN: {n} ASPECTOS','コレクション: {n} スキン','COLLECTION : {n} SKINS','SAMMLUNG: {n} SKINS','COLLEZIONE: {n} SKIN','KOLEKSİYON: {n} GÖRÜNÜM','COLEÇÃO: {n} VISUAIS','संग्रह: {n} स्किन','收藏：{n} 皮肤','컬렉션: {n} 스킨','КОЛЛЕКЦИЯ: {n} ОБЛИКОВ'),
    'level': ('NIVEL {n} • PARTIDAS {m}','レベル {n}・プレイ {m}','NIVEAU {n} • PARTIES {m}','STUFE {n} • SPIELE {m}','LIVELLO {n} • PARTITE {m}','SEVİYE {n} • OYUN {m}','NÍVEL {n} • PARTIDAS {m}','स्तर {n} • मैच {m}','等级 {n} • 对局 {m}','레벨 {n} • 게임 {m}','УРОВЕНЬ {n} • ИГР {m}'),
    'bosses': ('Jefes derrotados: {n}','ボス撃破: {n}','Boss vaincus : {n}','Besiegte Bosse: {n}','Boss sconfitti: {n}','Yenilen bosslar: {n}','Chefes derrotados: {n}','हराए गए बॉस: {n}','击败首领：{n}','보스 처치: {n}','Побеждено боссов: {n}'),
    'biomes': ('Biomas dominados: {n}','制覇したバイオーム: {n}','Biomes maîtrisés : {n}','Gemeisterte Biome: {n}','Biomi dominati: {n}','Ustalaşılan biyomlar: {n}','Biomas dominados: {n}','जीते हुए क्षेत्र: {n}','已精通生态区：{n}','정복한 지역: {n}','Освоено биомов: {n}'),
    'pet_unlock': ('Desbloqueadas {n} • Equipada: {m}','解放済み {n}・装備中: {m}','Débloqués {n} • Équipé : {m}','Freigeschaltet {n} • Aktiv: {m}','Sbloccati {n} • Equipaggiato: {m}','Açık {n} • Kuşanılan: {m}','Desbloqueados {n} • Equipado: {m}','अनलॉक {n} • चुना: {m}','已解锁 {n} • 装备：{m}','해제됨 {n} • 장착: {m}','Открыто {n} • Выбран: {m}'),
    'objective': ('Objetivo: {n}','目標: {n}','Objectif : {n}','Ziel: {n}','Obiettivo: {n}','Hedef: {n}','Objetivo: {n}','लक्ष्य: {n}','目标：{n}','목표: {n}','Цель: {n}'),
    'price': ('Precio: {n} monedas','価格: {n} コイン','Prix : {n} pièces','Preis: {n} Münzen','Prezzo: {n} monete','Fiyat: {n} altın','Preço: {n} moedas','कीमत: {n} सिक्के','价格：{n} 金币','가격: {n} 코인','Цена: {n} монет'),
    'record': ('TU RÉCORD: {n} m','最高記録: {n} m','VOTRE RECORD : {n} m','DEIN REKORD: {n} m','TUO RECORD: {n} m','REKORUN: {n} m','O SEU RECORDE: {n} m','आपका रिकॉर्ड: {n} मी','你的纪录：{n} 米','내 기록: {n} m','ВАШ РЕКОРД: {n} м'),
    'combo_rank': ('Combo {n} • Jefes {m} • Reliquias {r}','コンボ {n}・ボス {m}・遺物 {r}','Combo {n} • Boss {m} • Reliques {r}','Combo {n} • Bosse {m} • Relikte {r}','Combo {n} • Boss {m} • Reliquie {r}','Kombo {n} • Boss {m} • Kalıntı {r}','Combo {n} • Chefes {m} • Relíquias {r}','कॉम्बो {n} • बॉस {m} • अवशेष {r}','连击 {n} • 首领 {m} • 遗物 {r}','콤보 {n} • 보스 {m} • 유물 {r}','Комбо {n} • Боссы {m} • Реликвии {r}'),
    'distance_rank': ('{n} m • {m} monedas','{n} m・{m} コイン','{n} m • {m} pièces','{n} m • {m} Münzen','{n} m • {m} monete','{n} m • {m} altın','{n} m • {m} moedas','{n} मी • {m} सिक्के','{n} 米 • {m} 金币','{n} m • {m} 코인','{n} м • {m} монет'),
    'level_pet': ('NIVEL {n}/5 • XP {m}','レベル {n}/5・XP {m}','NIVEAU {n}/5 • XP {m}','STUFE {n}/5 • XP {m}','LIVELLO {n}/5 • XP {m}','SEVİYE {n}/5 • XP {m}','NÍVEL {n}/5 • XP {m}','स्तर {n}/5 • XP {m}','等级 {n}/5 • 经验 {m}','레벨 {n}/5 • XP {m}','УРОВЕНЬ {n}/5 • XP {m}'),
    'mood': ('Ánimo: {n}','気分: {n}','Humeur : {n}','Stimmung: {n}','Umore: {n}','Ruh hali: {n}','Humor: {n}','मूड: {n}','心情：{n}','기분: {n}','Настроение: {n}'),
    'bond': ('Vínculo {n}/100','絆 {n}/100','Lien {n}/100','Bindung {n}/100','Legame {n}/100','Bağ {n}/100','Vínculo {n}/100','लगाव {n}/100','亲密度 {n}/100','유대 {n}/100','Связь {n}/100'),
}
# Expressões ancoradas não substituem valores ou IDs dentro dos dados do jogo.
_PATTERNS = (
 (re.compile(r'^RECOMPENSA: \+(?P<n>\d+)$'), 'achievementreward'),
 (re.compile(r'^(?P<n>\d+) corridas$'), 'runs'),
 (re.compile(r'^(?P<n>\d+/\d+) skins$'), 'skins'),
 (re.compile(r'^Recorde em uma corrida: (?P<n>\d+) m$'), 'record_bioma'),
 (re.compile(r'^Distância acumulada: (?P<n>\d+) m$'), 'distance_bioma'),
 (re.compile(r'^Maestria atual: nível (?P<n>\d+/3)$'), 'mastery_bioma'),
 (re.compile(r'^(?P<n>\d+/\d+) CONQUISTAS$'), 'achievementprogress'),
 (re.compile(r'^RECOMPENSA: \+(?P<n>\d+)$'), 'achievementreward'),
 (re.compile(r'^Período: (?P<n>.+)$'), 'periodo'),
 (re.compile(r'^(?P<n>\d+/\d+)  •  RECOMPENSA (?P<m>\d+) MOEDAS$'), 'reward'),
 (re.compile(r'^COLEÇÃO: (?P<n>\d+/\d+) SKINS$'), 'collection'),
 (re.compile(r'^NÍVEL (?P<n>\d+)  •  PARTIDAS (?P<m>\d+)$'), 'level'),
 (re.compile(r'^Chefes derrotados: (?P<n>\d+)$'), 'bosses'),
 (re.compile(r'^Biomas dominados: (?P<n>\d+)$'), 'biomes'),
 (re.compile(r'^Desbloqueados (?P<n>\d+/\d+)  •  Equipado: (?P<m>.+)$'), 'pet_unlock'),
 (re.compile(r'^Objetivo: (?P<n>.+)$'), 'objective'),
 (re.compile(r'^Preço: (?P<n>\d+) moedas$'), 'price'),
 (re.compile(r'^SEU RECORDE: (?P<n>\d+) m$'), 'record'),
 (re.compile(r'^Combo (?P<n>\d+) • Chefes (?P<m>\d+) • Relíquias (?P<r>\d+)$'), 'combo_rank'),
 (re.compile(r'^(?P<n>\d+) m  •  (?P<m>\d+) moedas$'), 'distance_rank'),
 (re.compile(r'^NÍVEL (?P<n>\d+)/5  •  XP (?P<m>\d+)$'), 'level_pet'),
 (re.compile(r'^Humor: (?P<n>.+)$'), 'mood'),
 (re.compile(r'^Vínculo (?P<n>\d+)/100$'), 'bond'),
)

@lru_cache(maxsize=1024)
def localizar(texto, idioma):
    if idioma not in IDIOMAS:
        return texto
    texto = str(texto)
    fixo = _LITERALS.get(texto)
    if fixo is not None:
        return fixo[idioma]
    # Navegação paginada: prefixo traduzido e índice mantido.
    for cabecalho in ('PRÓXIMA ▶', 'PRÓXIMO ▶'):
        if texto.startswith(cabecalho):
            return _LITERALS[cabecalho][idioma] + texto[len(cabecalho):]
    # Recompensa e progresso são persistidos em português; somente o texto
    # anterior ao progresso numérico é localizado.
    if texto.endswith(')') and ' (' in texto:
        rotulo, separador, valor = texto.rpartition(' (')
        traducao = _LITERALS.get(rotulo)
        if traducao is not None:
            return traducao[idioma] + separador + valor
    # Rankings antigos guardam somente números; as descrições são traduzidas
    # na tela, preservando integralmente os valores e recompensas persistidos.
    if len(texto) > 4 and texto[:2] in ('✓ ', '○ ') and ' — ' in texto:
        descricao, status = texto[2:].rsplit(' — ', 1)
        original = _LITERALS.get(descricao)
        if original:
            descricao = original[idioma]
        if status in _LITERALS:
            status = _LITERALS[status][idioma]
        elif re.fullmatch(r'\+\d+ moedas', status):
            status = status.split(' ', 1)[0] + ' ' + _LITERALS['MOEDAS'][idioma]
        return texto[:2] + descricao + ' — ' + status
    for regex, nome in _PATTERNS:
        m = regex.fullmatch(texto)
        if m:
            valor = _MODELOS[nome][IDIOMAS.index(idioma)]
            return valor.format(**m.groupdict())
    return texto


def textos_unicode(idioma):
    """Caracteres usados nas fontes de subconjunto; função utilizada só no build/QA."""
    if idioma not in IDIOMAS:
        return ''
    return ''.join(v[idioma] for v in _LITERALS.values()) + ''.join(v[IDIOMAS.index(idioma)] for v in _MODELOS.values())
