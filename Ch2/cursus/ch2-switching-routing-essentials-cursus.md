# Hoofdstuk 2 - Switching- en routingessentials

## 1. Inleiding

In hoofdstuk 1 heb je een bestaand netwerk geanalyseerd vanuit een
enterprise-standpunt. Je keek niet alleen naar de vraag "werkt het netwerk?", maar ook
naar risico's zoals te brede trunks, single points of failure en een ontwerp dat
moeilijk schaalbaar wordt.

In dit hoofdstuk ga je een stap verder. Je onderzoekt hoe switching- en
routingmechanismen samen de beschikbaarheid van een campusnetwerk bepalen. Het
netwerk moet niet alleen werken op een rustige dag, maar ook voorspelbaar reageren
wanneer:

- een uplink uitvalt;
- een switch herstart;
- een extra verbinding wordt toegevoegd;
- het aantal VLAN's groeit;
- routes automatisch moeten worden uitgewisseld;
- clients een betrouwbare default gateway nodig hebben.

Dat verschil is belangrijk in enterprise-netwerken.

Een eenvoudige ping toont slechts dat één datapad op één tijdstip bruikbaar is. De
ping bewijst niet dat de tweede uplink de juiste VLAN's draagt, dat een OSPF-back-uppad
routes leert of dat een standby gateway kan overnemen.

Redundantie ontstaat bovendien niet door één protocol. De bereikbaarheid van een
client buiten zijn VLAN hangt af van een volledige keten:

```text
client
  -> accesspoort en VLAN
  -> trunk en actief STP-pad
  -> default gateway via HSRP
  -> routed uplink en OSPF
  -> bestemming of default route
```

Als één schakel in die keten ontbreekt, kan de dienst uitvallen terwijl verschillende
onderdelen afzonderlijk nog `up` lijken.

Daarom draait dit hoofdstuk rond vier vragen:

| Vraag | Waarom is die belangrijk? |
|---|---|
| Welke alternatieve paden bestaan er? | Zonder alternatief pad wordt elk kritisch toestel of elke kabel een single point of failure. |
| Wie beslist welk pad actief is? | Redundantie zonder controle kan loops, instabiliteit of onlogische verkeersstromen veroorzaken. |
| Werken Layer 2, de gateway en routing samen? | Redundantie in één laag compenseert geen fout in een andere laag. |
| Hoe bewijs je dat failover echt werkt? | Een netwerk dat redundant lijkt, is niet noodzakelijk redundant in de praktijk. |

Je gebruikt voorkennis over VLAN's, trunks, inter-VLAN-routing en
`show`-commando's. We bouwen die basis niet opnieuw vanaf nul op. We gebruiken haar
om STP, EtherChannel met LACP, multi-area OSPF en HSRP als één enterprise-ontwerp te
begrijpen.

In de workshop analyseer je een netwerk met bewuste fouten. Je noteert eerst wat je
verwacht, verzamelt daarna bewijs, voert een gecontroleerde negatieve test uit en
formuleert pas dan een verbetering.

Kernidee:

> In een enterprise-netwerk is "het werkt" geen eindpunt. Je moet kunnen aantonen
> welke functie overneemt wanneer een link, switch of gateway uitvalt.

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. redundantie, capaciteit en beschikbaarheid van elkaar onderscheiden;
2. uitleggen waarom een redundant Layer 2-ontwerp STP nodig heeft;
3. per VLAN de root bridge, root port en alternate poort herkennen en beoordelen;
4. een primary en secondary root bridge bewust in de distributionlaag plaatsen;
5. uitleggen hoe EtherChannel en LACP fysieke links tot één logisch kanaal bundelen;
6. een gedegradeerde of inconsistent geconfigureerde Port-channel herkennen;
7. de rol van area 0, internal routers, backbone routers, ABR's en ASBR's uitleggen;
8. een OSPF area mismatch, ontbrekende neighbor en ontbrekende default route
   methodisch onderzoeken;
9. uitleggen waarom passive interfaces routes blijven adverteren zonder neighbors te
   vormen op clientnetwerken;
10. echte SVI-adressen, een virtueel HSRP-adres en active/standby-rollen van elkaar
    onderscheiden;
11. STP-rootkeuzes en HSRP-active-rollen per VLAN op elkaar afstemmen;
12. aantonen dat redundantie over meerdere lagen werkt met positieve, negatieve en
    failovertesten;
13. relevante `show`-output selecteren en als bewijs interpreteren;
14. labvereenvoudigingen onderscheiden van vereisten voor een productieontwerp;
15. een technische vaststelling vertalen naar risico, bedrijfsimpact, verbetering en
    acceptatietest.

---

## 3. Waarom redundantie in switching belangrijk is

### 3.1 Van eenvoudige connectiviteit naar bedrijfszekerheid

In een klein labo of thuisnetwerk is een switch vaak voldoende. Alle toestellen hangen op die switch, de switch heeft een verbinding naar de router en daarmee is de basisconnectiviteit klaar.

In een bedrijf is dat te kwetsbaar. Een switch, kabel of uplink kan altijd uitvallen. Als er geen alternatief pad bestaat, wordt een klein technisch probleem meteen een gebruikersprobleem.

Voorbeeld:

| Situatie | Gevolg |
|---|---|
| `SW-ACCESS-1` heeft een uplink naar `SW-DIST-1`. | Als die uplink faalt, verliezen alle clients achter `SW-ACCESS-1` hun verbinding met servers, internet en andere VLAN's. |
| Alle pc's van de boekhouding hangen op een access switch. | Als die switch uitvalt, ligt de volledige afdeling stil. |
| Het servernetwerk is maar via een switch bereikbaar. | Een switchprobleem kan meerdere applicaties tegelijk onbereikbaar maken. |

Dit betekent niet dat elk toestel dubbel uitgevoerd moet worden. Redundantie kost geld en maakt het ontwerp complexer. Maar op kritische plaatsen wil je vermijden dat een defect onderdeel een hele zone offline haalt.

Een goede enterprise-vraag is daarom:

> Als deze kabel, poort of switch uitvalt, wie merkt dat dan?

Die vraag helpt je het verschil zien tussen een klein lokaal probleem en een netwerkbreed risico.

### 3.2 Redundante uplinks

Een access switch verbindt eindtoestellen zoals pc's, printers, telefoons of access points met de rest van het netwerk. In een enterprise ontwerp heeft zo'n access switch vaak twee uplinks naar een distributionlaag.

Conceptueel ziet dat er zo uit:

```text
             +-------------+
             | SW-DIST-1   |
             +------+------+
                    |
                    |
+-----------+       |
| SW-ACCESS |-------+
+-----------+       |
                    |
                    |
             +------+------+
             | SW-DIST-2   |
             +-------------+
```

Het doel is eenvoudig: als een uplink of distributionswitch uitvalt, blijft er een ander pad bestaan.

Belangrijk:

Redundantie betekent niet automatisch dat beide links tegelijk actief gebruikt worden. Soms wordt een link actief gebruikt en staat de andere klaar als back-up. Soms worden meerdere fysieke links gebundeld tot een logisch kanaal. Welke optie correct is, hangt af van het ontwerp en de gebruikte technologie.

In dit hoofdstuk komen daarom later twee belangrijke mechanismen terug:

- **STP (Spanning Tree Protocol)** voorkomt loops in redundante switched netwerken.
- **EtherChannel** met **LACP (Link Aggregation Control Protocol)** kan meerdere fysieke links als een logische verbinding behandelen.

Voor nu is vooral dit belangrijk:

> Extra kabels toevoegen is geen ontwerp. Je moet ook begrijpen hoe het netwerk beslist welke kabel gebruikt wordt.

### 3.3 Slechte situatie 1: access switch met slechts een uplink

Een access switch met slechts een uplink is eenvoudig en overzichtelijk, maar kwetsbaar.

```text
PC's ---- SW-ACCESS ---- SW-DIST ---- rest van het netwerk
```

Als de uplink tussen `SW-ACCESS` en `SW-DIST` uitvalt:

- blijven de pc's lokaal misschien nog met dezelfde switch verbonden;
- kunnen ze meestal hun gateway niet meer bereiken;
- valt communicatie met servers en internet weg;
- kan troubleshooting misleidend zijn, omdat de pc nog link heeft op zijn eigen switchpoort.

Waarom is dit slecht?

De fout zit niet noodzakelijk in de configuratie. Het ontwerp heeft gewoon geen alternatief pad. In een enterprise-netwerk is dat voor kritische zones zelden aanvaardbaar.

Betere aanpak:

- voorzie twee uplinks naar de distributionlaag;
- sluit die bij voorkeur niet allebei aan op exact hetzelfde fysieke risico;
- documenteer welke link primair is en welke failover biedt;
- test wat er gebeurt wanneer een uplink uitvalt.

Controlepunt:

> Kan je in de topologie aanwijzen welke access switches volledig afhankelijk zijn van een enkele uplink?

### 3.4 Slechte situatie 2: redundante verbindingen zonder STP-begrip

Een veelgemaakte denkfout is: "Als een kabel goed is, zijn twee kabels beter."

Bij switches is dat niet automatisch waar. Twee fysieke verbindingen tussen dezelfde switches kunnen een Layer 2-loop veroorzaken als het netwerk geen correct looppreventiemechanisme gebruikt.

```text
+-----------+      link 1      +-----------+
| SW-1      |------------------| SW-2      |
|           |------------------|           |
+-----------+      link 2      +-----------+
```

Zonder controle kan een broadcastframe blijven rondgaan. Switches werken op Layer 2 en hebben geen TTL-veld zoals IP-pakketten op Layer 3. Daardoor kan een loop blijven bestaan en steeds meer verkeer veroorzaken.

Mogelijke gevolgen:

| Probleem | Praktisch effect |
|---|---|
| Broadcast storm | Het netwerk wordt overspoeld met broadcastverkeer. |
| Instabiele MAC-tabellen | Switches zien hetzelfde MAC-adres afwisselend op verschillende poorten. |
| Hoge switchbelasting | Switches besteden capaciteit aan nutteloos verkeer. |
| Onvoorspelbare connectiviteit | Pings werken soms wel, soms niet, of vallen plots weg. |

Waarom is dit slecht?

De extra kabel was bedoeld als redundantie, maar veroorzaakt zonder begrip van STP mogelijk een storing die groter is dan het oorspronkelijke risico.

Betere aanpak:

- gebruik STP bewust en controleer welke poort geblokkeerd wordt;
- bepaal later bewust welke switch root bridge moet zijn;
- gebruik EtherChannel wanneer meerdere fysieke links samen een logische verbinding moeten vormen;
- controleer met `show`-commando's of de werkelijke toestand overeenkomt met je ontwerp.

Controlepunt:

> Zie je een redundant pad? Dan moet je ook kunnen verklaren welk mechanisme een switching loop voorkomt.

### 3.5 Slechte situatie 3: alle clients achter een switch zonder alternatief pad

Soms is er technisch gezien geen fout in de bekabeling of configuratie. Toch kan het ontwerp slecht zijn.

Voorbeeld:

```text
PC-OFFICE-1
PC-OFFICE-2
PC-OFFICE-3
PRINTER-OFFICE
AP-OFFICE
      |
      |
  SW-ACCESS-1
      |
      |
  SW-DIST-1
```

Als alle toestellen van een afdeling achter een switch hangen, wordt die switch operationeel kritisch. Een defecte voeding, foutieve herstart of verkeerde configuratiewijziging op die switch heeft meteen impact op iedereen achter dat toestel.

Waarom is dit slecht?

Het netwerk kan perfect werken tijdens normale omstandigheden, maar het heeft geen fouttolerantie op accessniveau. Bij kleine organisaties is dat soms een bewuste keuze. Bij kritische afdelingen of productieomgevingen is dat vaak onvoldoende.

Betere enterprise-aanpak:

- verdeel kritische toestellen waar mogelijk over meerdere access switches;
- voorzie redundante uplinks per access switch;
- documenteer welke bedrijfsprocessen afhankelijk zijn van welke switch;
- test niet alleen connectiviteit, maar ook impact bij uitval.

Belangrijke nuance:

Niet elk accessnetwerk moet volledig redundant zijn. Een vergaderlokaal of klein leslokaal kan minder kritisch zijn dan een serverrack, magazijnzone of productieomgeving. Enterprise-denken betekent dat je de technische keuzes koppelt aan bedrijfsimpact.

### 3.6 Redundantie moet bewezen worden

Een netwerkdiagram kan er redundant uitzien, maar dat bewijst nog niet dat failover werkt.

Voorbeelden:

| Ziet er redundant uit | Mogelijke realiteit |
|---|---|
| Twee uplinks naar de distributionlaag | Een uplink draagt geen juiste VLAN's. |
| Twee kabels tussen switches | STP blokkeert een link, wat normaal kan zijn. |
| EtherChannel met twee links | Een fysieke link zit niet echt in de bundel. |
| Twee routers richting internet | Clients gebruiken maar een default gateway zonder gateway redundancy. |

Daarom hoort bij redundantie altijd een testvraag:

> Wat gebeurt er als ik deze link administratief uitschakel of de kabel losmaak?

In Packet Tracer kan je dat didactisch testen door een link uit te schakelen of tijdelijk te verwijderen. Daarna controleer je niet alleen of een ping opnieuw werkt, maar ook waarom het netwerk hersteld is.

Typische controlevragen:

- Welke poort verandert van status?
- Blijft het juiste VLAN beschikbaar?
- Wordt een geblokkeerde STP-poort actief?
- Blijft routing naar andere netwerken werken?
- Merken clients de storing kort, lang of helemaal niet?

Samengevat:

> Redundantie is pas waardevol wanneer je kan uitleggen welk onderdeel mag falen, welk alternatief pad dan gebruikt wordt en hoe je dat met metingen of `show`-commando's bewijst.

### 3.7 Vier mechanismen, vier verschillende problemen

De technologieën uit dit hoofdstuk vullen elkaar aan. Ze zijn niet onderling
uitwisselbaar.

| Mechanisme | Welk probleem lost het op? | Wat lost het niet op? | Belangrijk bewijs |
|---|---|---|---|
| STP/Rapid PVST+ | voorkomt Layer 2-loops en kiest een loopvrije topologie | extra bandbreedte of Layer 3-routes | root bridge en poortrollen per VLAN |
| EtherChannel met LACP | bundelt compatibele links tot één logische verbinding | een back-up naar twee onafhankelijke switches | actieve memberlinks en consistente trunk op de Port-channel |
| OSPF | leert en herberekent routes tussen routed netwerken | de default gateway van een client | neighbors, area-indeling, routes en default route |
| HSRP | biedt clients een virtuele en overneembare default gateway | een defect trunk- of OSPF-pad achter de gateway | virtual IP, active/standby-rol en failover |

Voorbeeld:

Een standby HSRP-switch kan correct active worden, maar toch geen server bereiken als
zijn OSPF-neighbor met de core ontbreekt. HSRP-failover is dan geslaagd als protocol,
maar de gebruikersdienst blijft onbeschikbaar.

Waarom belangrijk?

> Beschikbaarheid is een eigenschap van de volledige keten, niet van één protocol.

Controleer daarom altijd twee zaken:

1. Is het mechanisme zelf gezond?
2. Blijft de bedoelde eind-tot-einddienst werken wanneer het mechanisme moet
   overnemen?

---

## 4. Switching loops en STP

### 4.1 Wat is een switching loop?

Een switching loop ontstaat wanneer er in een Layer 2-netwerk meer dan een pad bestaat tussen switches en frames kunnen blijven rondgaan.

Een eenvoudig voorbeeld:

```text
              +--------+
              | SW-1   |
              +---+----+
                 / \
                /   \
               /     \
       +------+       +------+
       | SW-2 |-------| SW-3 |
       +------+       +------+
```

De drie switches vormen samen een gesloten kring. Een broadcastframe kan van `SW-1` naar `SW-2`, van `SW-2` naar `SW-3` en daarna opnieuw naar `SW-1` blijven gaan.

Bij IP-routing bestaat er een TTL-veld. TTL staat voor Time To Live. Dat veld voorkomt dat een IP-pakket eindeloos blijft rondgaan. Bij gewone Ethernetframes op Layer 2 bestaat zo'n mechanisme niet. Een loop in een switched netwerk kan daarom zeer snel een groot probleem worden.

Belangrijke vaststelling:

> Redundante Layer 2-paden zijn nuttig, maar alleen als er een mechanisme bestaat dat loops voorkomt.

### 4.2 Waarom zijn switching loops gevaarlijk?

Een switching loop is niet gewoon "een extra pad". Het kan het hele VLAN instabiel maken.

#### Broadcast storms

Een broadcastframe wordt door een switch doorgestuurd naar alle poorten binnen hetzelfde VLAN, behalve de poort waar het frame binnenkwam.

Voorbeelden van broadcastverkeer:

- ARP-requests;
- DHCP-discoverberichten;
- sommige discovery- of managementprotocollen.

Als er een loop bestaat, kan zo'n broadcastframe blijven circuleren. Elke switch kopieert het frame opnieuw naar andere poorten. Daardoor ontstaat een broadcast storm: het netwerk wordt overspoeld met broadcastverkeer.

Praktisch merk je dat bijvoorbeeld zo:

| Symptoom | Mogelijke verklaring |
|---|---|
| Pings vallen plots weg. | Switches zijn druk met nutteloos Layer 2-verkeer. |
| Packet Tracer reageert traag. | Er loopt zeer veel verkeer door de simulatie. |
| Clients krijgen moeilijk een IP-adres. | DHCP- en ARP-verkeer raakt verstoord. |
| Een heel VLAN lijkt onstabiel. | De loop zit op Layer 2 en treft alle toestellen in dat VLAN. |

Waarom is dit belangrijk?

Een kleine bekabelingsfout kan zo een probleem voor een volledige afdeling worden. Daarom mag je redundante switchverbindingen nooit bekijken als "gewoon wat extra kabels".

#### Instabiele MAC-adrestabellen

Switches leren MAC-adressen door te kijken vanop welke poort een frame binnenkomt. Als een frame door een loop blijft rondgaan, kan dezelfde bron-MAC plots via verschillende poorten verschijnen.

Voorbeeld:

```text
PC-A stuurt een frame.
SW-1 leert: MAC van PC-A zit op Fa0/1.
Door de loop komt hetzelfde frame later terug via G0/1.
SW-1 past zijn MAC-adrestabel aan: MAC van PC-A zit nu op G0/1.
Even later gebeurt het opnieuw via een andere poort.
```

De switch blijft zijn MAC-adrestabel aanpassen. Dat heet MAC address table instability of MAC flapping.

Gevolg:

- frames worden naar de verkeerde poort gestuurd;
- verkeer wordt geflood omdat de switch niet meer stabiel weet waar een MAC-adres zit;
- connectiviteit wordt onvoorspelbaar;
- troubleshooting wordt moeilijk, omdat het probleem niet constant hetzelfde gedrag toont.

Controlepunt:

> Als hetzelfde MAC-adres afwisselend op verschillende switchpoorten verschijnt, welke soort fout vermoed je dan?

### 4.3 Wat doet STP?

STP betekent **Spanning Tree Protocol**. STP is een Layer 2-protocol dat switching loops voorkomt door in een redundant netwerk sommige poorten tijdelijk te blokkeren.

STP verwijdert de fysieke kabel niet. De link blijft bestaan. STP beslist alleen dat een bepaalde poort voorlopig geen gewone frames mag doorsturen.

Zo krijg je dit idee:

```text
             +-------------+
             | SW-DIST-1   |
             +------+------+
                    |
              forwarding
                    |
+-----------+       |
| SW-ACCESS |-------+
+-----------+       |
                    |
               blocked
                    |
             +------+------+
             | SW-DIST-2   |
             +-------------+
```

Dat lijkt op het eerste gezicht vreemd: je hebt twee uplinks, maar een ervan wordt geblokkeerd. Dat is niet per se fout. STP doet dit net om te voorkomen dat het redundant pad een loop veroorzaakt.

Belangrijke nuance:

> Een blocked poort is niet automatisch een probleem. Soms is het precies het bewijs dat STP een loop voorkomt.

Wat je wel moet controleren:

- Is de geblokkeerde poort logisch?
- Is de actieve weg het pad dat je als ontwerper verwacht?
- Wordt de juiste switch gekozen als centraal punt in de Layer 2-topologie?
- Komt een geblokkeerde poort correct in actie wanneer een actieve link uitvalt?

### 4.4 Root bridge

STP bouwt een loopvrije topologie rond een centrale switch: de **root bridge**.

De root bridge is het referentiepunt voor STP. Alle andere switches berekenen wat hun beste pad naar de root bridge is. In een enterprise ontwerp wil je daarom dat de root bridge een logische, krachtige en centrale switch is, meestal in de distribution- of corelaag.

In een eenvoudig campusnetwerk is dit vaak logisch:

```text
             +----------------+
             | SW-DIST-1      |
             | root bridge    |
             +-------+--------+
                     |
        +------------+------------+
        |                         |
   +----+----+               +----+----+
   | SW-ACC1 |               | SW-ACC2 |
   +---------+               +---------+
```

Waarom is dit belangrijk?

Omdat STP-paden worden berekend richting root bridge. Als een access switch per ongeluk root bridge wordt, kan verkeer via een onlogische weg lopen.

Slechte situatie:

```text
             +-------------+
             | SW-DIST-1   |
             +------+------+
                    |
                    |
             +------+------+
             | SW-ACCESS   |  <- per ongeluk root bridge
             +------+------+
                    |
                    |
             +------+------+
             | SW-DIST-2   |
             +-------------+
```

Waarom is dit slecht?

- De access switch wordt een centraal referentiepunt voor Layer 2.
- Verkeer kan via een accesslaag lopen terwijl de distributionlaag logischer zou zijn.
- Een minder belangrijke switch krijgt een te grote impact op het netwerk.
- Bij onderhoud of uitval van die access switch kan de STP-topologie onverwacht veranderen.

Betere aanpak:

- kies bewust welke switch root bridge wordt;
- kies meestal een distribution- of core-switch;
- gebruik een tweede switch als backup root;
- controleer de root bridge per VLAN.

Controlepunt:

> Als je in `show spanning-tree` ziet dat een access switch root bridge is voor een belangrijk VLAN, is dat dan logisch? Waarom wel of niet?

### 4.5 Root port, designated port en blocked/alternate port

STP gebruikt rollen om te bepalen welke poorten forwarding zijn en welke poorten geblokkeerd worden.

Je hoeft STP niet als een wiskundig algoritme uit het hoofd te leren. Voor enterprise troubleshooting moet je vooral begrijpen welke vraag elke poortrol beantwoordt.

| Poortrol | Betekenis | Praktische vraag |
|---|---|---|
| Root port | De beste poort van een niet-root switch richting root bridge. | Langs welke poort bereikt deze switch de root bridge het best? |
| Designated port | De poort die voor een bepaald segment verkeer mag doorsturen. | Welke kant van deze link mag frames forwarden voor dit segment? |
| Blocked of alternate port | Een poort die geen gewone frames doorstuurt om een loop te voorkomen. | Welke poort houdt STP bewust gesloten als back-uppad? |

Voorbeeld:

```text
             +----------------+
             | SW-DIST-1      |
             | root bridge    |
             +-------+--------+
                     |
                 forwarding
                     |
             +-------+--------+
             | SW-ACCESS      |
             +-------+--------+
                     |
                  blocked
                     |
             +-------+--------+
             | SW-DIST-2      |
             +----------------+
```

Op `SW-ACCESS` is de poort richting `SW-DIST-1` waarschijnlijk de root port, want dat is het beste pad naar de root bridge. De andere uplink kan blocked of alternate zijn, afhankelijk van de STP-variant en topologie.

Dat is geen mislukte redundantie. Het is een back-uppad dat klaarstaat. Als de actieve uplink faalt, kan STP een nieuwe loopvrije topologie maken.

### 4.6 Klassieke STP, RSTP en Rapid PVST+

De naam STP wordt vaak als verzamelnaam gebruikt, maar de variant bepaalt onder meer
hoe snel een netwerk op een wijziging reageert en welke termen in de output staan.

| Variant | Praktische betekenis |
|---|---|
| IEEE 802.1D STP | klassieke spanning tree met tragere overgang tussen poorttoestanden |
| IEEE 802.1w RSTP | snellere convergentie en expliciete alternate- en backuprollen |
| Cisco Rapid PVST+ | een snelle spanning-tree-instance per VLAN |

Bij klassieke STP spreek je onder meer over de toestand `blocking`. Bij RSTP heet de
loopvrije toestand `discarding`, terwijl `alternate` een **poortrol** is. Cisco-output
en Packet Tracer kunnen termen naast elkaar tonen. Trek daarom geen conclusie uit één
woord: lees altijd het protocol, de rol én de toestand.

| Vraag | Waarom belangrijk? |
|---|---|
| Gebruiken de switches een compatibele STP-variant? | Een gemengde of onverwachte modus kan gedrag en convergentie beïnvloeden. |
| Welke poort is alternate/discarding? | Dat is het kandidaat-back-uppad. |
| Hoe lang duurt herstel? | Een pad dat pas na lange tijd herstelt, kan voor de dienst onaanvaardbaar zijn. |
| Verandert de root bridge tijdens de test? | Failover mag niet onbedoeld een access switch centraal maken. |

Voor accesspoorten naar eindtoestellen wordt vaak PortFast gebruikt. Zo hoeft een pc-
of serverpoort niet op gewone STP-convergentie te wachten. Combineer dat in productie
met BPDU Guard: ontvangt zo'n randpoort toch een BPDU, dan wordt de poort beschermd
tegen een mogelijk aangesloten switch of een foutieve lus.

Typische fout:

> PortFast configureren op een willekeurige inter-switchlink om de poort sneller
> forwarding te maken.

Dat omzeilt geen nood aan een correct STP-ontwerp en kan een loop sneller impact laten
hebben. Gebruik edge-instellingen alleen op poorten waar volgens het ontwerp geen
switch hoort.

### 4.7 STP is per VLAN belangrijk

In veel Cisco-omgevingen werkt STP per VLAN. Dat betekent dat VLAN 10 een andere root bridge kan hebben dan VLAN 20.

Dat kan nuttig zijn, maar het kan ook verwarring veroorzaken.

Voorbeeld:

| VLAN | Root bridge | Mogelijke interpretatie |
|---:|---|---|
| 10 | `SW-DIST-1` | Logisch, bijvoorbeeld voor userverkeer. |
| 20 | `SW-DIST-2` | Kan logisch zijn als dit bewust gekozen is. |
| 99 | `SW-ACCESS-3` | Verdacht, management-VLAN heeft een access switch als root. |

Waarom is dit belangrijk?

Als je alleen `show spanning-tree` bekijkt zonder op VLAN te letten, kan je een verkeerde conclusie trekken. Een root bridge kan voor een VLAN goed gekozen zijn en voor een ander VLAN slecht.

Praktische vraag:

> Welke switch is root bridge voor het VLAN dat ik nu troubleshoot?

### 4.8 Praktische voorbeelden van slechte root bridge-keuzes

#### Voorbeeld 1: access switch wordt root bridge

Situatie:

Een access switch is later toegevoegd aan het netwerk. Niemand heeft de STP-prioriteit gecontroleerd. Door een lagere bridge ID wordt die switch root bridge voor VLAN 10.

Waarom is dat slecht?

- De access switch is niet ontworpen als centraal punt.
- Uplinks kunnen anders blokkeren dan verwacht.
- Verkeer volgt mogelijk een onlogische route.
- Bij een reboot van die access switch moet STP opnieuw convergeren.

Betere aanpak:

- stel de root bridge bewust in op de distributionlaag;
- controleer dit na elke topologiewijziging;
- documenteer welke switch root en backup root is.

#### Voorbeeld 2: root bridge verschilt onbedoeld per VLAN

Situatie:

VLAN 10 heeft `SW-DIST-1` als root bridge. VLAN 20 heeft door toeval `SW-ACCESS-2` als root bridge.

Waarom is dat slecht?

Het netwerkgedrag verschilt per VLAN zonder dat dit bewust ontworpen is. Daardoor kan dezelfde fysieke link voor het ene VLAN forwarding zijn en voor het andere VLAN blocked. Dat maakt troubleshooting moeilijker.

Betere aanpak:

- kies root bridges per VLAN bewust;
- hou het ontwerp eenvoudig in kleine labs;
- gebruik duidelijke namen en documentatie;
- controleer met `show spanning-tree vlan 10`, `show spanning-tree vlan 20` enzovoort.

#### Voorbeeld 3: backup root ontbreekt

Situatie:

`SW-DIST-1` is correct root bridge, maar er is geen duidelijke backup root. Als `SW-DIST-1` uitvalt, beslist STP opnieuw op basis van de resterende bridge ID's.

Waarom is dat slecht?

Failover gebeurt dan minder voorspelbaar. Misschien wordt een access switch de nieuwe root bridge.

Betere aanpak:

- kies een primaire root bridge;
- kies een secundaire root bridge;
- test wat er gebeurt wanneer de primaire distributionswitch uitvalt.

### 4.9 Hoe onderzoek je STP in Packet Tracer?

In Packet Tracer kan je STP zichtbaar maken door redundante switchverbindingen te bouwen en daarna te kijken welke poorten forwarding of blocked zijn.

Gebruik STP niet als een lijst commando's om vanbuiten te leren. Vertrek altijd van een onderzoeksvraag.

| Onderzoeksvraag | Mogelijk commando |
|---|---|
| Welke switch is root bridge? | `show spanning-tree` |
| Welke switch is root bridge voor VLAN 10? | `show spanning-tree vlan 10` |
| Welke poorten zijn forwarding of blocked? | `show spanning-tree` |
| Is de geblokkeerde poort logisch? | `show spanning-tree vlan ...` gecombineerd met de topologie |
| Verandert STP na een link failure? | Vergelijk de output voor en na de test. |

Voorbeeld van een goede analysezin:

> `SW-ACCESS-1` heeft twee uplinks. De link naar `SW-DIST-1` is forwarding en de link naar `SW-DIST-2` is blocked voor VLAN 10. Dat is logisch als `SW-DIST-1` de root bridge is en STP de tweede uplink als back-uppad gebruikt.

Voorbeeld van een risicovolle analysezin:

> Er is een blocked poort, dus er is een probleem.

Waarom is die tweede zin onvoldoende?

Een blocked poort kan net correct zijn. Je moet altijd verklaren waarom die poort blocked is en of dat past bij het ontwerp.

### 4.10 Mini-analyse: wat moet je kunnen uitleggen?

Wanneer je een redundant switched netwerk analyseert, moet je minstens deze vragen kunnen beantwoorden:

| Vraag | Waarom belangrijk? |
|---|---|
| Waar zitten de redundante Layer 2-paden? | Daar kan een loop ontstaan als STP niet correct werkt. |
| Welke switch is root bridge per VLAN? | De root bridge bepaalt de logica van de STP-topologie. |
| Welke poort is blocked of alternate? | Die poort voorkomt de loop en vormt mogelijk een back-uppad. |
| Is de root bridge logisch gekozen? | Een access switch als root bridge kan onlogische verkeersstromen veroorzaken. |
| Wat gebeurt er bij link failure? | Redundantie moet getest worden, niet alleen getekend. |

Samengevat:

> STP maakt redundante Layer 2-netwerken bruikbaar door loops te voorkomen. Een blocked poort is niet automatisch fout. De echte vraag is of de STP-beslissing past bij het enterprise-ontwerp.

---

## 5. Root bridge design

### 5.1 Waarom root bridge design belangrijk is

STP kiest altijd een root bridge. Als jij die keuze niet bewust maakt, doet STP het zelf op basis van de bridge ID.

De bridge ID bestaat conceptueel uit:

- een bridge priority;
- een VLAN-informatiecomponent bij per-VLAN STP;
- het MAC-adres van de switch.

De switch met de laagste bridge ID wordt root bridge. Dat betekent dat een switch root kan worden omdat hij toevallig een lagere priority of een lager MAC-adres heeft. Vanuit enterprise-standpunt is dat geen goed ontwerp.

Belangrijke gedachte:

> De root bridge moet gekozen worden door het ontwerp, niet door toeval.

Waarom?

Omdat alle andere switches hun beste pad richting root bridge bepalen. De root bridge wordt dus het logische middelpunt van de Layer 2-topologie. Als dat middelpunt verkeerd ligt, kunnen poorten anders blokkeren dan verwacht en kan verkeer een onlogische weg volgen.

### 5.2 Waar hoort de root bridge meestal te staan?

In een klassiek enterprise ontwerp heb je vaak een accesslaag en een distributionlaag.

- De accesslaag verbindt clients, printers, telefoons, access points en andere eindtoestellen.
- De distributionlaag verzamelt meerdere access switches en vormt vaak de overgang naar routing, security of coreverbindingen.

Daarom is de distributionlaag meestal de logische plaats voor de root bridge.

Voorbeeld van een logisch ontwerp:

```text
                    +----------------+
                    | SW-DIST-1      |
                    | root VLAN 10   |
                    +-------+--------+
                            |
             +--------------+--------------+
             |                             |
        +----+----+                   +----+----+
        | SW-ACC1 |                   | SW-ACC2 |
        +----+----+                   +----+----+
             |                             |
          clients                       clients
```

In dit ontwerp ligt het STP-referentiepunt bovenaan in de topologie, dicht bij de plaats waar verkeer toch al samenkomt. Dat maakt het gedrag voorspelbaarder.

Een vaak gebruikte aanpak:

| Rol | Switch | Reden |
|---|---|---|
| Primary root | `SW-DIST-1` | Hoofdpad voor de belangrijkste VLAN's. |
| Secondary root | `SW-DIST-2` | Neemt logisch over als `SW-DIST-1` uitvalt. |
| Geen root | access switches | Access switches horen eindtoestellen te verbinden, niet het STP-middelpunt te zijn. |

Dit betekent niet dat elke omgeving exact zo moet worden ontworpen. Het principe is wel belangrijk: kies de root bridge op een plaats waar je die rol ook echt wil.

### 5.3 Wat gebeurt er als een access switch root bridge wordt?

Stel dat een access switch per ongeluk root bridge wordt voor VLAN 10.

```text
              +-------------+
              | SW-DIST-1   |
              +------+------+
                     |
                     |
              +------+------+
              | SW-ACC1     |
              | root VLAN10 |
              +------+------+
                     |
                     |
              +------+------+
              | SW-DIST-2   |
              +-------------+
```

Dit kan gebeuren wanneer:

- niemand de STP-prioriteit instelt;
- een nieuwe switch wordt toegevoegd met een lagere bridge ID;
- een labtopologie snel opgebouwd wordt zonder STP-controle;
- een oude configuratie op een switch blijft staan.

Waarom is dit problematisch?

| Probleem | Gevolg |
|---|---|
| Access switch wordt logisch middelpunt. | Een toestel aan de rand krijgt te veel invloed op de Layer 2-topologie. |
| Poorten blokkeren onverwacht. | De actieve paden volgen niet noodzakelijk het gewenste ontwerp. |
| Verkeer kan via de accesslaag lopen. | Dat is onlogisch als de distributionlaag bedoeld is als verzamelpunt. |
| Onderhoud wordt riskanter. | Een herstart van een access switch kan STP-convergentie veroorzaken. |
| Troubleshooting wordt moeilijker. | De fysieke topologie lijkt logisch, maar STP kiest andere paden. |

Voor studenten is dit een belangrijk inzicht:

> Een netwerk kan pings doorlaten en toch een slecht STP-ontwerp hebben.

Met andere woorden: basisconnectiviteit bewijst niet dat de root bridge goed gekozen is.

### 5.4 Hoe kies je een root bridge bewust?

In Cisco-omgevingen kan je de STP-prioriteit beïnvloeden. Een lagere priority wint.

Conceptueel:

| Switch | Priority | Resultaat |
|---|---:|---|
| `SW-DIST-1` | 4096 | Wordt waarschijnlijk root bridge. |
| `SW-DIST-2` | 8192 | Wordt waarschijnlijk backup root. |
| `SW-ACC1` | 32768 | Wordt normaal geen root. |
| `SW-ACC2` | 32768 | Wordt normaal geen root. |

Je hoeft voor dit hoofdstuk niet alle STP-prioriteitsdetails uit het hoofd te leren. Je moet wel begrijpen dat een lagere waarde meer kans heeft om root bridge te worden.

Praktisch zie je in Cisco-configuraties vaak een van deze twee manieren:

```text
spanning-tree vlan 10 root primary
spanning-tree vlan 10 root secondary
```

of explicieter:

```text
spanning-tree vlan 10 priority 4096
spanning-tree vlan 10 priority 8192
```

De eerste vorm is didactisch handig omdat ze duidelijk maakt wat je bedoelt: deze switch moet primary root of secondary root worden. De tweede vorm toont expliciet met welke priority je werkt.

Belangrijk:

Gebruik commando's nooit blind. Controleer altijd achteraf of de gewenste switch effectief root bridge is.

### 5.5 Root bridge per VLAN kiezen

Omdat STP vaak per VLAN werkt, kan je de root bridge per VLAN kiezen.

In een eenvoudig onderwijsnetwerk hou je dit best overzichtelijk:

| VLAN | Functie | Primary root | Secondary root |
|---:|---|---|---|
| 10 | Office users | `SW-DIST-1` | `SW-DIST-2` |
| 20 | Warehouse | `SW-DIST-1` | `SW-DIST-2` |
| 50 | Servers | `SW-DIST-1` | `SW-DIST-2` |
| 99 | Management | `SW-DIST-1` | `SW-DIST-2` |

In grotere netwerken kan je VLAN's verdelen over twee distributionswitches. Bijvoorbeeld: `SW-DIST-1` is root voor VLAN 10 en 50, terwijl `SW-DIST-2` root is voor VLAN 20 en 60. Dat kan nuttig zijn om verkeer te spreiden, maar het maakt de analyse ook complexer.

Voor dit hoofdstuk is de belangrijkste regel:

> Verschillende root bridges per VLAN zijn alleen goed als dat bewust ontworpen en gedocumenteerd is.

Slecht voorbeeld:

| VLAN | Root bridge | Probleem |
|---:|---|---|
| 10 | `SW-DIST-1` | Logisch. |
| 20 | `SW-ACC2` | Onlogisch, waarschijnlijk toevallig. |
| 99 | `SW-ACC1` | Slecht voor managementverkeer. |

Betere conclusie:

> VLAN 20 en VLAN 99 hebben een access switch als root bridge. Dat is technisch mogelijk, maar niet logisch in dit ontwerp. De root bridge moet verplaatst worden naar de distributionlaag.

### 5.6 Root bridge en blocked ports samen lezen

Een blocked poort begrijp je pas goed als je weet wie de root bridge is.

Voorbeeld:

```text
                    +----------------+
                    | SW-DIST-1      |
                    | root VLAN 10   |
                    +-------+--------+
                            |
                       forwarding
                            |
                    +-------+--------+
                    | SW-ACC1        |
                    +-------+--------+
                            |
                         blocked
                            |
                    +-------+--------+
                    | SW-DIST-2      |
                    +----------------+
```

Analyse:

- `SW-DIST-1` is root bridge voor VLAN 10.
- `SW-ACC1` kiest zijn beste pad richting `SW-DIST-1`.
- De link richting `SW-DIST-2` kan blocked zijn om een loop te voorkomen.
- Dat is logisch als `SW-DIST-1` de gewenste root bridge is.

Maar stel dat `SW-ACC1` zelf root bridge is:

```text
                    +----------------+
                    | SW-DIST-1      |
                    +-------+--------+
                            |
                       forwarding
                            |
                    +-------+--------+
                    | SW-ACC1        |
                    | root VLAN 10   |
                    +-------+--------+
                            |
                       forwarding
                            |
                    +-------+--------+
                    | SW-DIST-2      |
                    +----------------+
```

Dan kan dezelfde fysieke topologie een heel andere STP-logica krijgen. Poorten kunnen forwarding of blocked worden op plaatsen die je niet verwacht.

Daarom analyseer je STP altijd in deze volgorde:

1. Welke VLAN bekijk ik?
2. Welke switch is root bridge voor dat VLAN?
3. Welke poort is root port op elke niet-root switch?
4. Welke poorten zijn designated?
5. Welke poorten zijn blocked of alternate?
6. Past dit bij het gewenste ontwerp?

### 5.7 Enterprise-denkvraag: is dit ontwerp logisch?

Stel dat je deze vaststelling doet:

```text
VLAN 10:
  Root bridge: SW-ACC3
  Blocked port: uplink van SW-DIST-2 naar SW-DIST-1
```

Een beginnende technicus kan zeggen:

> Er is connectiviteit, dus het is in orde.

Een enterprise-analyse gaat verder:

| Vraag | Waarom belangrijk? |
|---|---|
| Waarom is `SW-ACC3` root bridge? | Een access switch hoort meestal geen centraal STP-punt te zijn. |
| Is dit bewust gekozen? | Toeval is geen ontwerp. |
| Welke poorten blokkeren daardoor? | Misschien wordt een belangrijke uplink niet gebruikt. |
| Wat gebeurt er als `SW-ACC3` uitvalt? | De STP-topologie kan onverwacht veranderen. |
| Is er een backup root? | Failover moet voorspelbaar zijn. |

Modelconclusie:

> Het netwerk werkt op dit moment, maar de root bridge-keuze is niet enterprise-ready. `SW-ACC3` is een access switch en hoort niet het STP-referentiepunt te zijn. De root bridge moet bewust op de distributionlaag gekozen worden, met een duidelijke secondary root.

### 5.8 Praktische controle in Packet Tracer

In Packet Tracer kan je root bridge design onderzoeken met een kleine checklist.

| Stap | Actie | Verwachte vaststelling |
|---:|---|---|
| 1 | Teken de fysieke Layer 2-topologie. | Je ziet waar redundante paden zitten. |
| 2 | Noteer de VLAN's die over trunks lopen. | Je weet voor welke VLAN's STP relevant is. |
| 3 | Gebruik `show spanning-tree vlan 10`. | Je ziet wie root bridge is voor VLAN 10. |
| 4 | Herhaal dit voor andere belangrijke VLAN's. | Je ziet of root bridge-keuze consistent is. |
| 5 | Noteer forwarding en blocked poorten. | Je ziet welke paden actief zijn. |
| 6 | Simuleer link failure. | Je controleert of een back-uppad actief wordt. |

Voorbeeld van een goede notitie:

| VLAN | Root bridge | Blocked poort | Beoordeling |
|---:|---|---|---|
| 10 | `SW-DIST-1` | `SW-ACC1 G0/2` richting `SW-DIST-2` | Logisch, `SW-DIST-1` is primary root. |
| 20 | `SW-DIST-1` | `SW-ACC1 G0/2` richting `SW-DIST-2` | Logisch en consistent met VLAN 10. |
| 99 | `SW-ACC1` | `SW-DIST-2 G0/1` | Niet logisch, management-VLAN heeft access switch als root. |

Voorbeeld van een sterke conclusie:

> Voor VLAN 10 en 20 is de root bridge logisch gekozen op `SW-DIST-1`. Voor VLAN 99 is `SW-ACC1` root bridge. Dat is een risico, omdat managementverkeer afhankelijk wordt van een access switch als STP-referentiepunt. De STP-prioriteit voor VLAN 99 moet aangepast worden zodat `SW-DIST-1` primary root en `SW-DIST-2` secondary root wordt.

### 5.9 Typische fouten bij root bridge design

| Fout | Waarom problematisch? | Betere aanpak |
|---|---|---|
| Root bridge niet controleren. | STP kiest dan op basis van toeval. | Controleer root bridge per VLAN. |
| Access switch wordt root bridge. | De rand van het netwerk wordt logisch middelpunt. | Kies distribution/core als root. |
| Geen secondary root. | Failover is minder voorspelbaar. | Stel een backup root in. |
| Alleen naar fysieke kabels kijken. | STP kan een ander logisch pad kiezen. | Combineer topologie met `show spanning-tree`. |
| Blocked poort meteen als fout zien. | STP blokkeert bewust om loops te voorkomen. | Verklaar waarom die poort blocked is. |
| Root bridge per VLAN vergeten. | VLAN's kunnen verschillend gedrag vertonen. | Controleer per belangrijk VLAN. |

### 5.10 Samenvatting root bridge design

Root bridge design gaat niet over een losse STP-instelling. Het gaat over voorspelbaarheid.

Studenten moeten vooral onthouden:

- STP kiest altijd een root bridge.
- Als jij de root bridge niet kiest, gebeurt de keuze op basis van bridge ID.
- De root bridge hoort meestal in de distribution- of corelaag.
- Een access switch als root bridge is vaak een slecht teken.
- Een blocked poort is pas te beoordelen nadat je weet wie root bridge is.
- Root bridge-keuze kan per VLAN verschillen.
- Een goed enterprise ontwerp heeft een primary root en een secondary root.

Kernzin:

> Root bridge design zorgt ervoor dat STP niet alleen loops voorkomt, maar dat het dat doet op een manier die past bij het netwerkontwerp.

---

## 6. EtherChannel en LACP

### 6.1 Waarom meerdere fysieke links niet zomaar parallel werken

Na STP lijkt het logisch om te denken:

> Als STP een redundante link blokkeert, dan voeg ik gewoon extra kabels toe zodat er meer bandbreedte is.

Bij switches werkt dat niet automatisch. Als je twee of meer losse Layer 2-links tussen dezelfde switches legt, ziet STP mogelijk een loop. STP zal dan een of meer poorten blokkeren om het netwerk stabiel te houden.

Voorbeeld zonder EtherChannel:

```text
+-------------+        link 1        +-------------+
| SW-DIST-1   |----------------------| SW-ACCESS-1 |
|             |        link 2        |             |
|             |----------------------|             |
+-------------+                      +-------------+
```

Mogelijke STP-uitkomst:

| Link | STP-status | Gevolg |
|---|---|---|
| link 1 | forwarding | Wordt gebruikt voor verkeer. |
| link 2 | blocked | Wordt niet gebruikt zolang link 1 actief blijft. |

Dat is correct STP-gedrag. STP voorkomt een loop. Maar het betekent ook dat je niet automatisch extra bandbreedte krijgt door gewoon een tweede kabel te plaatsen.

Belangrijke gedachte:

> Twee kabels zijn niet automatisch een bundel. Zonder extra configuratie ziet de switch meestal twee aparte paden.

### 6.2 Redundantie versus bundeling

Redundantie en bundeling lijken op elkaar, maar ze beantwoorden een andere vraag.

| Concept | Vraag | Voorbeeld |
|---|---|---|
| Redundantie | Is er een alternatief pad als iets uitvalt? | Een tweede uplink die STP als back-up blokkeert. |
| Bundeling | Kunnen meerdere fysieke links samen als een logische verbinding werken? | Twee of vier links in een EtherChannel. |

Een redundant pad hoeft niet actief gebruikt te worden. Het kan klaarstaan als back-up.

Een bundel probeert meerdere fysieke links samen als een logisch geheel te behandelen. Voor STP lijkt die bundel dan op een link. Daardoor vermijd je dat STP elke fysieke kabel apart als mogelijke loop ziet.

### 6.3 Wat is EtherChannel?

**EtherChannel** is een techniek waarbij meerdere fysieke Ethernetlinks tussen dezelfde toestellen samengevoegd worden tot een logische verbinding.

Die logische verbinding heet vaak een **Port-channel**.

Voorbeeld:

```text
Fysiek:

+-------------+      G0/1      +-------------+
| SW-DIST-1   |----------------| SW-ACCESS-1 |
|             |      G0/2      |             |
|             |----------------|             |
+-------------+                +-------------+

Logisch:

+-------------+    Port-channel 1    +-------------+
| SW-DIST-1   |======================| SW-ACCESS-1 |
+-------------+                      +-------------+
```

Voor STP is `Port-channel 1` een logische link. STP hoeft dus niet een van de twee fysieke kabels te blokkeren om een loop tussen dezelfde twee switches te vermijden.

Voordelen:

- meer beschikbare bandbreedte tussen switches;
- redundantie binnen de bundel;
- eenvoudiger STP-gedrag;
- minder kans dat een losse link onverwacht blocked wordt;
- betere benutting van uplinks dan een gewone STP-back-uplink.

Belangrijke nuance:

EtherChannel betekent niet dat een enkele TCP-sessie altijd over alle fysieke links tegelijk verdeeld wordt. Switches gebruiken een load-balancingmechanisme, bijvoorbeeld op basis van bron- en doel-MAC of IP-adressen. Meerdere gesprekken kunnen dus over verschillende fysieke links verdeeld worden, maar een enkel gesprek gebruikt meestal een gekozen link binnen de bundel.

Voor dit hoofdstuk is vooral belangrijk:

> EtherChannel maakt van meerdere fysieke links een logische link die je als geheel configureert, controleert en troubleshoot.

### 6.4 Wat is LACP?

**LACP** betekent **Link Aggregation Control Protocol**.

LACP is een onderhandelingsprotocol waarmee switches kunnen afspreken of fysieke links samen in een EtherChannel mogen komen.

Waarom is dat nuttig?

Zonder onderhandeling kan een configuratiefout gevaarlijker zijn. De ene kant kan denken dat twee poorten een bundel vormen, terwijl de andere kant de poorten als losse links ziet. Dat kan leiden tot inconsistente forwarding, STP-problemen of een bundel die niet werkt zoals verwacht.

LACP helpt controleren of:

- beide kanten EtherChannel willen vormen;
- de juiste poorten samen horen;
- de links compatibele instellingen hebben;
- de bundel actief mag worden.

In Cisco-configuraties zie je vaak deze LACP-modi:

| Mode | Betekenis | Vormt channel met |
|---|---|---|
| `active` | Stuurt actief LACP-berichten. | `active` of `passive` |
| `passive` | Wacht op LACP-berichten. | `active` |

Voorbeeld:

| Switch A | Switch B | Resultaat |
|---|---|---|
| `active` | `active` | EtherChannel vormt. |
| `active` | `passive` | EtherChannel vormt. |
| `passive` | `passive` | EtherChannel vormt niet, want niemand start de onderhandeling. |

In onderwijsomgevingen is `active` aan beide kanten vaak het duidelijkst.

### 6.5 Welke links mag je samen bundelen?

Een EtherChannel is een contract tussen twee logische buren. Alle memberlinks moeten
dezelfde twee uiteinden verbinden en compatibele eigenschappen hebben.

| Voorwaarde | Waarom? |
|---|---|
| zelfde speed en duplex | members moeten verkeer op een vergelijkbare manier kunnen verwerken |
| zelfde Layer 2- of Layer 3-modus | één Port-channel kan niet tegelijk een trunk en routed link zijn |
| zelfde trunking, native VLAN en allowed VLAN's | elk frame moet onafhankelijk van de gekozen memberlink correct behandeld worden |
| zelfde channel group per lokale switch | de juiste fysieke interfaces moeten bij dezelfde logische bundel horen |
| compatibele LACP-modus aan beide kanten | minstens één zijde moet de onderhandeling actief starten |

Een gewone EtherChannel kan niet zomaar één access switch met twee **onafhankelijke**
distributionswitches bundelen:

```text
                  +-- MLS-DIST1
SW-ACCESS == Po1 =+
                  +-- MLS-DIST2
```

Voor de access switch zouden beide links één logische buur moeten vormen. Dat kan
alleen wanneer de twee distributietoestellen zich via een technologie zoals stacking,
virtual switching of multi-chassis link aggregation als één logisch systeem
presenteren. Zonder zo'n technologie gebruik je twee afzonderlijke uplinks en laat je
STP een loopvrij pad kiezen, of je maakt van de uplinks routed links wanneer het
ontwerp dat ondersteunt.

Kernzin:

> Bundel alleen links waarvan je aan beide kanten één logisch geheel kan maken.

### 6.6 Basisconfiguratie conceptueel

De exacte interface-namen hangen af van je Packet Tracer-toestellen. Conceptueel configureer je eerst de fysieke poorten en daarna de logische Port-channel.

Voorbeeld op switch A:

```text
interface range g0/1 - 2
 channel-group 1 mode active

interface port-channel 1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50,99
```

Voorbeeld op switch B:

```text
interface range g0/1 - 2
 channel-group 1 mode active

interface port-channel 1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50,99
```

Belangrijk:

De fysieke poorten binnen dezelfde EtherChannel moeten consistent zijn. Ze moeten bijvoorbeeld dezelfde snelheid, duplex, trunkmodus, native VLAN en allowed VLAN's gebruiken.

In de praktijk configureer je trunkinstellingen vaak op de Port-channel-interface, zodat de bundel als logisch geheel beheerd wordt.

### 6.7 Slechte situatie 1: twee kabels tussen switches zonder EtherChannel

Situatie:

Een student verbindt `SW-DIST-1` en `SW-ACCESS-1` met twee kabels, maar configureert geen EtherChannel.

```text
+-------------+        G0/1        +-------------+
| SW-DIST-1   |--------------------| SW-ACCESS-1 |
|             |        G0/2        |             |
|             |--------------------|             |
+-------------+                    +-------------+
```

Wat gebeurt er waarschijnlijk?

- STP ziet twee Layer 2-paden tussen dezelfde switches.
- STP blokkeert een van de poorten.
- Het netwerk blijft stabiel, maar gebruikt niet beide links actief.

Waarom is dit niet noodzakelijk fout?

STP doet wat het moet doen: een loop voorkomen.

Waarom is dit mogelijk niet wat je wilde?

Je verwachtte misschien extra bandbreedte, maar je hebt vooral een blocked back-uppad gemaakt. Dat is redundantie, geen bundeling.

Betere aanpak:

- beslis eerst wat je wil: back-uplink via STP of actieve bundel via EtherChannel;
- configureer EtherChannel als beide fysieke links samen gebruikt moeten worden;
- controleer met `show etherchannel summary` of de bundel echt actief is.

Controlepunt:

> Als je twee kabels ziet tussen dezelfde switches, kan je dan bewijzen of dit een EtherChannel is of gewoon twee losse STP-paden?

### 6.8 Slechte situatie 2: mismatch in VLAN- of trunkconfiguratie

EtherChannel vereist consistentie. Een bundel is geen magische oplossing voor slechte trunkconfiguratie.

Slechte situatie:

| Poort | Mode | Allowed VLAN's |
|---|---|---|
| `SW-DIST-1 G0/1` | trunk | 10,20,50,99 |
| `SW-DIST-1 G0/2` | trunk | 10,20 |

Deze twee poorten horen samen in dezelfde EtherChannel, maar ze laten niet dezelfde VLAN's toe.

Waarom is dit slecht?

- De bundel kan weigeren te vormen.
- Een fysieke poort kan uit de bundel blijven.
- Verkeer voor bepaalde VLAN's kan onvoorspelbaar worden.
- Troubleshooting wordt verwarrend: de kabel is up, maar de bundel is niet gezond.

Betere aanpak:

- configureer identieke instellingen op alle memberinterfaces;
- beheer trunkinstellingen op de Port-channel-interface;
- controleer zowel `show etherchannel summary` als `show interfaces trunk`;
- vergelijk de configuratie aan beide kanten.

Sterke analysezin:

> De fysieke links zijn up, maar ze vormen geen stabiele EtherChannel omdat de trunkinstellingen niet consistent zijn. Daardoor is de redundantie of bundeling niet betrouwbaar.

### 6.9 Slechte situatie 3: een link valt uit en niemand merkt het

Een EtherChannel kan blijven werken wanneer een fysieke link in de bundel uitvalt. Dat is net een voordeel.

Maar er zit ook een risico in:

> Omdat de verbinding blijft werken, merkt niemand dat de bundel gedegradeerd is.

Voorbeeld:

| Situatie | Gevolg |
|---|---|
| Port-channel heeft twee fysieke links. | Normaal gedrag. |
| Een fysieke link valt uit. | Port-channel blijft up via de overblijvende link. |
| Niemand controleert de bundel. | Het netwerk draait verder met minder capaciteit en minder redundantie. |
| De tweede link valt later ook uit. | De verbinding valt volledig weg. |

Waarom is dit belangrijk?

Redundantie mag geen excuus zijn om monitoring en controle over te slaan. Een gedegradeerde bundel werkt nog, maar is kwetsbaarder dan bedoeld.

Betere aanpak:

- controleer hoeveel memberlinks actief zijn;
- documenteer hoeveel links je verwacht;
- gebruik `show etherchannel summary`;
- test wat er gebeurt wanneer een memberlink uitvalt;
- behandel een ontbrekende memberlink als een probleem, ook als pings nog werken.

### 6.10 EtherChannel controleren

Gebruik `show`-commando's als onderzoekstools. Begin niet met de vraag "welk commando moet ik kennen?", maar met "wat wil ik bewijzen?".

| Onderzoeksvraag | Mogelijk commando | Waar let je op? |
|---|---|---|
| Bestaat de EtherChannel? | `show etherchannel summary` | Is er een Port-channel zichtbaar? |
| Welke poorten zitten in de bundel? | `show etherchannel summary` | Staan de juiste fysieke poorten bij dezelfde groep? |
| Is de bundel Layer 2 of Layer 3? | `show etherchannel summary` | Past het type bij je ontwerp? |
| Is de Port-channel trunk? | `show interfaces trunk` | Staat de Port-channel in de trunklijst? |
| Welke VLAN's mogen over de bundel? | `show interfaces trunk` | Zijn de allowed VLAN's correct beperkt? |
| Werkt STP op de Port-channel? | `show spanning-tree vlan ...` | Zie je de Port-channel als logisch pad? |

In `show etherchannel summary` zie je vaak symbolen bij de Port-channel en memberinterfaces. De exacte weergave kan verschillen per toestel of Packet Tracer-versie. De kernvraag blijft:

> Zitten alle verwachte fysieke poorten actief in dezelfde logische Port-channel?

Voorbeeld van een analyse:

| Verwacht | Werkelijk | Conclusie |
|---|---|---|
| `G0/1` en `G0/2` vormen `Po1`. | Alleen `G0/1` zit actief in `Po1`. | De bundel werkt gedegradeerd of is fout geconfigureerd. |
| `Po1` is trunk. | `Po1` verschijnt in `show interfaces trunk`. | De logische bundel vervoert VLAN's. |
| VLAN 10,20,50,99 zijn toegelaten. | VLAN 1-1005 zijn toegelaten. | De trunk is te breed geconfigureerd. |

### 6.11 EtherChannel en STP samen begrijpen

EtherChannel vervangt STP niet. STP blijft nodig om loops in het grotere Layer 2-netwerk te voorkomen.

Het verschil is:

- zonder EtherChannel ziet STP meerdere losse fysieke links;
- met EtherChannel ziet STP een logische Port-channel.

Voorbeeld zonder EtherChannel:

```text
SW-DIST-1 G0/1 -------- G0/1 SW-ACCESS-1   forwarding
SW-DIST-1 G0/2 -------- G0/2 SW-ACCESS-1   blocked
```

Voorbeeld met EtherChannel:

```text
SW-DIST-1 Po1 ========= Po1 SW-ACCESS-1    forwarding
  member: G0/1
  member: G0/2
```

In het tweede voorbeeld behandelt STP `Po1` als een link. De twee fysieke kabels zijn memberlinks binnen dezelfde logische verbinding.

Belangrijke conclusie:

> EtherChannel helpt om meerdere fysieke links nuttig te gebruiken, terwijl STP nog altijd waakt over een loopvrije Layer 2-topologie.

### 6.12 Typische fouten bij EtherChannel

| Fout | Waarom problematisch? | Betere aanpak |
|---|---|---|
| Twee kabels plaatsen zonder EtherChannel. | STP blokkeert waarschijnlijk een link. | Kies bewust: STP-back-up of EtherChannel. |
| LACP aan een kant `active`, andere kant niet geconfigureerd. | De bundel vormt niet correct. | Configureer beide kanten consistent. |
| Beide kanten `passive`. | Niemand start LACP-onderhandeling. | Gebruik minstens een kant `active`, vaak beide. |
| Trunkinstellingen verschillen per memberlink. | Poorten kunnen uit de bundel vallen. | Configureer consistent en controleer de Port-channel. |
| Allowed VLAN's staan te breed. | Onnodige VLAN's lopen over de uplink. | Laat alleen noodzakelijke VLAN's toe. |
| Een gedegradeerde bundel negeren. | Redundantie is verminderd zonder dat gebruikers iets merken. | Controleer aantal actieve memberlinks. |
| Alleen pingen als test. | Ping bewijst niet dat de bundel gezond is. | Gebruik `show etherchannel summary` en failovertesten. |

### 6.13 Samenvatting EtherChannel en LACP

EtherChannel is een manier om meerdere fysieke links als een logische verbinding te gebruiken. LACP helpt om die bundel dynamisch en gecontroleerd te vormen.

Studenten moeten vooral onthouden:

- meerdere kabels tussen switches zijn niet automatisch een EtherChannel;
- STP kan een losse redundante link blokkeren om loops te voorkomen;
- EtherChannel bundelt fysieke links in een Port-channel;
- LACP onderhandelt of poorten samen een bundel mogen vormen;
- trunk- en VLAN-instellingen moeten consistent zijn;
- een Port-channel kan blijven werken met een ontbrekende memberlink, maar is dan gedegradeerd;
- `show etherchannel summary` is essentieel om te bewijzen dat de bundel echt gezond is.

Kernzin:

> EtherChannel maakt redundantie en extra capaciteit bruikbaar, maar alleen als de fysieke poorten, trunkinstellingen en LACP-configuratie consistent zijn.

---

## 7. OSPF areas in een enterprise context

### 7.1 Waarom OSPF areas nu interessant worden

In het vorige OPO heb je OSPF al gebruikt om routers routes te laten uitwisselen. Je kent dus al de basis:

- OSPF-neighbors;
- router ID;
- `network`-statements;
- area 0 in eenvoudige labs;
- `show ip ospf neighbor`;
- `show ip route`;
- passive interfaces;
- default route propagation.

In dit hoofdstuk gebruiken we die voorkennis en voegen we een nieuw enterprise-concept toe: **OSPF areas**.

Een klein netwerk kan alle routers in area 0 plaatsen. Dat is eenvoudig en werkt prima in een labo. In een groter bedrijfsnetwerk wordt dat minder aantrekkelijk. Elke router moet dan te veel topologie-informatie kennen en elke wijziging kan een grotere impact hebben dan nodig.

OSPF areas helpen om een groot routed netwerk op te delen in kleinere logische delen.

Belangrijke gedachte:

> OSPF areas zorgen ervoor dat routing schaalbaarder en overzichtelijker wordt. Niet elke router hoeft elk detail van het volledige netwerk te kennen.

### 7.2 Herhaling in een minuut: wat blijft belangrijk?

Voor we naar areas gaan, blijft deze basis noodzakelijk:

| Basisconcept | Wat moet je nog weten? |
|---|---|
| OSPF-neighbor | Routers moeten neighbor worden voordat ze routes uitwisselen. |
| Router ID | Unieke OSPF-identiteit van een router. |
| Area | Logische OSPF-zone waarin routers topologie-informatie delen. |
| Area 0 | Backbone area. Andere areas moeten logisch met area 0 verbonden zijn. |
| Passive interface | Netwerk wordt geadverteerd, maar er worden geen neighbors gezocht op die interface. |
| Default route | Kan vanuit de edge naar het OSPF-domein verspreid worden. |

Dit deel herhaalt die basis niet uitgebreid. We gebruiken ze om multi-area OSPF te begrijpen.

### 7.3 Wat is een OSPF area?

Een OSPF area is een logisch deel van een OSPF-netwerk. Routers binnen dezelfde area delen gedetailleerde topologie-informatie met elkaar.

Routers in een andere area hoeven niet alle interne details te kennen. Ze krijgen routes naar netwerken in die area, maar niet noodzakelijk de volledige interne structuur.

Vergelijk het met een campus:

| Campusdeel | Mogelijke OSPF-area |
|---|---|
| Core/distribution | area 0 |
| Gebouw A | area 10 |
| Gebouw B | area 20 |
| Datacenter/servernetwerk | area 50 |
| Branch office | area 100 |

Een area is dus geen VLAN en ook geen subnet. Een area is een routing-ontwerpkeuze.

Belangrijk onderscheid:

| Concept | Laag | Functie |
|---|---|---|
| VLAN | Layer 2 | Broadcastdomeinen scheiden. |
| Subnet | Layer 3 | IP-adresruimte structureren. |
| OSPF area | Routing | Routinginformatie schaalbaar opdelen. |

### 7.4 Area 0: de backbone

Area 0 is de backbone area van OSPF. Andere areas moeten via area 0 met elkaar verbonden zijn.

Een eenvoudig multi-area ontwerp:

```text
             area 10              area 0              area 20
        +--------------+      +-------------+      +--------------+
        | R-BUILDING-A |------| R-CORE      |------| R-BUILDING-B |
        +--------------+      +-------------+      +--------------+
          users A              backbone              users B
```

In dit ontwerp:

- zit het coregedeelte in area 0;
- zit gebouw A in area 10;
- zit gebouw B in area 20;
- loopt verkeer tussen area 10 en area 20 via area 0.

Waarom is area 0 verplicht belangrijk?

OSPF gebruikt area 0 als centrale ruggengraat voor inter-area routing. Als areas niet correct met area 0 verbonden zijn, kan route-uitwisseling tussen areas mislopen.

Enterprise-denkvraag:

> Als je een nieuwe area toevoegt, hoe is die area verbonden met area 0?

### 7.5 Soorten routers in multi-area OSPF

In multi-area OSPF krijgen routers een rol afhankelijk van waar hun interfaces zitten.

| Routertype | Betekenis | Voorbeeld |
|---|---|---|
| Internal router | Alle OSPF-interfaces zitten in dezelfde area. | Router binnen gebouw A, alleen area 10. |
| Backbone router | Heeft minstens een interface in area 0. | Core-router in de backbone. |
| ABR | Area Border Router: verbindt area 0 met een andere area. | Distributionrouter tussen area 0 en area 10. |
| ASBR | Autonomous System Boundary Router: injecteert routes van buiten OSPF. | Edge-router die een default route naar internet verspreidt. |

Voor dit hoofdstuk is vooral de **ABR** belangrijk.

Een **ABR** of **Area Border Router** heeft interfaces in meerdere areas. Hij verbindt bijvoorbeeld area 10 met area 0.

Voorbeeld:

```text
                 area 10                 area 0
        +---------------------+   +-------------------+
        | VLANs gebouw A      |   | core/distribution |
        |                     |   |                   |
        |        R-ABR-A -----+---+----- R-CORE       |
        +---------------------+   +-------------------+
```

`R-ABR-A` is hier de router die de grens vormt tussen area 10 en area 0.

### 7.6 Waarom areas gebruiken?

Areas voegen complexiteit toe. Je gebruikt ze dus niet omdat het "mooi" is, maar omdat ze echte ontwerpvoordelen bieden.

| Voordeel | Praktisch effect |
|---|---|
| Minder topologiedetail buiten de area | Routers in andere areas hoeven minder interne details te kennen. |
| Betere schaalbaarheid | Grote netwerken blijven beheersbaar. |
| Minder impact van wijzigingen | Een wijziging binnen area 10 hoeft niet overal even zwaar door te wegen. |
| Mogelijkheid tot summarization | Een ABR kan meerdere routes samenvatten. |
| Duidelijker ontwerp | Campusdelen, gebouwen of branches kunnen logisch gescheiden worden. |

Voorbeeld:

Gebouw A heeft bijvoorbeeld deze aaneengesloten subnetten:

| VLAN | Subnet |
|---:|---|
| 10 | `10.10.8.0/24` |
| 20 | `10.10.9.0/24` |
| 30 | `10.10.10.0/24` |
| 40 | `10.10.11.0/24` |

Als het adresplan goed gekozen is, kan de ABR richting backbone eventueel samenvatten:

```text
10.10.8.0/22
```

Daardoor hoeven routers buiten gebouw A niet elk intern VLAN apart als detail te
kennen. De prefix is alleen correct omdat precies deze vier /24-netwerken samen binnen
het /22-blok vallen.

Belangrijke nuance:

> Areas lossen geen slecht adresplan op. Summarization werkt pas goed als subnetten logisch gegroepeerd zijn.

### 7.7 Single-area versus multi-area OSPF

Single-area OSPF:

```text
Alle routers in area 0
```

Voordelen:

- eenvoudig te configureren;
- makkelijk te begrijpen;
- goed voor kleine labs en kleine netwerken.

Nadelen:

- minder schaalbaar;
- alle routers delen meer topologiedetail;
- minder structuur bij groei.

Multi-area OSPF:

```text
area 10 ---- area 0 ---- area 20
```

Voordelen:

- beter schaalbaar;
- logische opdeling per gebouw, locatie of netwerkzone;
- summarization wordt mogelijk aan area-grenzen;
- wijzigingen blijven beter lokaal.

Nadelen:

- ontwerp moet kloppen;
- troubleshooting vraagt meer inzicht;
- area 0-connectiviteit wordt cruciaal;
- verkeerde area-toewijzing kan neighbors of routes breken.

Praktische conclusie:

> Gebruik single-area OSPF zolang eenvoud volstaat. Gebruik multi-area OSPF wanneer groei, structuur en schaalbaarheid belangrijk worden.

### 7.8 Voorbeeldtopologie voor Packet Tracer

Een haalbare Packet Tracer-topologie voor dit hoofdstuk:

```text
                  area 10
        VLAN 10/20 users A
                |
            +---+---+
            | R-A   |
            +---+---+
                |
                | area 0
            +---+---+
            | R-CORE|
            +---+---+
                |
                | area 0
            +---+---+
            | R-B   |
            +---+---+
                |
        VLAN 30/40 users B
                  area 20
```

Mogelijke rolverdeling:

| Router | Rol | Areas |
|---|---|---|
| `R-A` | ABR voor gebouw A | area 10 en area 0 |
| `R-CORE` | backbone router | area 0 |
| `R-B` | ABR voor gebouw B | area 20 en area 0 |

In dit ontwerp:

- usernetwerken van gebouw A zitten in area 10;
- usernetwerken van gebouw B zitten in area 20;
- de routed links tussen de routers zitten in area 0;
- verkeer tussen area 10 en area 20 gaat via area 0.

### 7.9 Conceptuele configuratie

Voorbeeld voor `R-A`:

```text
router ospf 1
 router-id 1.1.1.1
 network 10.10.0.0 0.0.255.255 area 10
 network 10.0.0.0 0.0.0.3 area 0
```

Conceptueel:

- de usernetwerken van gebouw A zitten in area 10;
- de link naar de core zit in area 0;
- `R-A` wordt daardoor een ABR.

Voorbeeld voor `R-CORE`:

```text
router ospf 1
 router-id 2.2.2.2
 network 10.0.0.0 0.0.0.3 area 0
 network 10.0.0.4 0.0.0.3 area 0
```

Conceptueel:

- `R-CORE` zit alleen in area 0;
- `R-CORE` is een backbone router.

Voorbeeld voor `R-B`:

```text
router ospf 1
 router-id 3.3.3.3
 network 10.0.0.4 0.0.0.3 area 0
 network 10.20.0.0 0.0.255.255 area 20
```

Conceptueel:

- de link naar de core zit in area 0;
- de usernetwerken van gebouw B zitten in area 20;
- `R-B` wordt een ABR.

Let op:

Deze configuratie is didactisch vereenvoudigd. In een echte omgeving kies je network statements nauwkeurig en combineer je dit met passive interfaces.

### 7.10 Passive interfaces: wel adverteren, geen neighbor zoeken

Een OSPF `network`-statement heeft twee gevolgen: OSPF wordt op een passende interface
actief en het aangesloten netwerk kan geadverteerd worden. Op een routed transitlink
wil je meestal neighbors vormen. Op een client-VLAN wil je het subnet wel bekendmaken,
maar verwacht je geen OSPF-router van een gebruiker.

Daarvoor dient een passive interface.

| Interfacetype | Netwerk adverteren? | Hello's sturen en neighbors vormen? | Gewenste keuze |
|---|---:|---:|---|
| routed link naar core | ja | ja | niet passive |
| SVI voor gebruikers-VLAN | ja | nee | passive |
| server-VLAN zonder OSPF-router | ja | nee | passive |
| ongebruikte interface | nee | nee | niet activeren in OSPF |

Een robuust configuratiepatroon is:

```text
router ospf 1
 passive-interface default
 no passive-interface GigabitEthernet0/1
```

Hierbij zijn alle OSPF-interfaces standaard passive. Alleen de expliciete transitlink
naar de echte neighbor wordt actief vrijgegeven.

Belangrijk:

> `passive-interface` stopt de advertentie van het aangesloten netwerk niet. Het
> verhindert OSPF-neighborvorming op die interface.

Waarom belangrijk?

- clients ontvangen geen onnodige OSPF-hello's;
- een onverwacht aangesloten router vormt niet zomaar een adjacency;
- de configuratie documenteert op welke links je werkelijk routingburen verwacht;
- het aantal foutlocaties bij troubleshooting wordt kleiner.

In productie combineer je dit met authenticatie waar passend, netwerksegmentatie en
controle van wie een transitnetwerk fysiek kan bereiken. `passive-interface` alleen is
geen volledige beveiligingsmaatregel.

### 7.11 Inter-area routes herkennen

In de routing table herken je OSPF-routes aan codes.

Typische codes:

| Code | Betekenis |
|---|---|
| `O` | OSPF-route binnen dezelfde area, intra-area. |
| `O IA` | OSPF inter-area route, geleerd uit een andere area. |
| `O*E2` | Externe OSPF-default route, bijvoorbeeld van een edge-router. |

Voor dit hoofdstuk is vooral `O IA` belangrijk.

Voorbeeld:

```text
O IA 10.20.30.0/24 [110/3] via 10.0.0.2
```

Analyse:

`R-A` ziet `10.20.30.0/24` als een inter-area route. Dat betekent dat het netwerk niet in dezelfde area zit als `R-A`, maar via een ABR uit een andere area geleerd werd.

Sterke analysezin:

> `R-A` leert het netwerk `10.20.30.0/24` als `O IA`. Dat past bij het ontwerp, want dit netwerk hoort bij gebouw B in area 20 en wordt via area 0 naar area 10 verspreid.

### 7.12 Area mismatch

Een veelgemaakte fout is een area mismatch op een routed link.

Voorbeeld:

| Router | Interface | OSPF-area |
|---|---|---:|
| `R-A` | link naar `R-CORE` | 0 |
| `R-CORE` | link naar `R-A` | 10 |

De twee kanten van dezelfde link zitten dus niet in dezelfde area.

Gevolg:

- OSPF-neighbor vormt niet correct;
- routes worden niet uitgewisseld over die link;
- troubleshooting lijkt soms verwarrend omdat IP-connectiviteit wel kan werken.

Controle:

```text
show ip ospf neighbor
show ip protocols
show ip ospf interface
```

Sterke conclusie:

> De IP-link tussen `R-A` en `R-CORE` is up, maar OSPF vormt geen neighbor omdat de interfaces in verschillende areas zitten. Beide kanten van dezelfde OSPF-link moeten dezelfde area gebruiken.

### 7.13 Non-backbone area zonder area 0

Een andere typische ontwerpfout is een non-backbone area die niet correct aan area 0 hangt.

Slecht ontwerp:

```text
area 10 ---- area 20 ---- area 30
```

Hier ontbreekt area 0 als backbone tussen de areas.

Beter ontwerp:

```text
area 10 ---- area 0 ---- area 20
                    |
                 area 30
```

Waarom is dit belangrijk?

OSPF verwacht dat inter-area verkeer via area 0 loopt. Als je areas rechtstreeks aan elkaar hangt zonder correcte backbone, kan routeverspreiding fout of onvolledig worden.

Enterprise-denkvraag:

> Als area 20 routes naar area 10 moet leren, via welke ABR en via welke backbone loopt dat dan?

### 7.14 ABR en summarization

Een ABR is de plaats waar summarization conceptueel interessant wordt.

Stel dat area 10 deze opeenvolgende netwerken bevat:

| Netwerk in area 10 |
|---|
| `10.10.8.0/24` |
| `10.10.9.0/24` |
| `10.10.10.0/24` |
| `10.10.11.0/24` |

Zonder summarization kunnen andere areas meerdere losse routes leren.

Met een goed adresplan kan de ABR richting area 0 een samenvatting adverteren, bijvoorbeeld:

```text
10.10.8.0/22
```

Waarom is dit nuttig?

- routers buiten area 10 krijgen minder routes;
- wijzigingen binnen area 10 blijven beter verborgen;
- de routing table wordt overzichtelijker;
- het ontwerp schaalt beter.

Belangrijk:

Summarization op een ABR is een ontwerpkeuze. Je doet dit alleen als het adresplan
klopt en de samenvatting geen verkeerde netwerken omvat. Een brede samenvatting die
ook niet-bestaande of elders gebruikte subnetten omvat, kan verkeer naar een verkeerde
ABR trekken en een black hole veroorzaken.

Slechte situatie:

> Een docent of student kiest willekeurige subnetten per VLAN. Later blijkt dat area 10 niet proper samen te vatten is. Het probleem zit dan niet in OSPF, maar in het adresplan.

### 7.15 Default route in multi-area OSPF

Default route propagation blijft belangrijk, maar in multi-area OSPF moet je ook nadenken waar de default route ontstaat.

Typisch ontwerp:

```text
area 10 ---- area 0 ---- R-EDGE ---- ISP
area 20 ---- area 0 -------+
```

`R-EDGE` is vaak een ASBR omdat hij een route van buiten OSPF binnenbrengt, bijvoorbeeld een default route naar de ISP.

Conceptueel:

```text
router ospf 1
 default-information originate
```

Zonder het sleutelwoord `always` adverteert Cisco IOS die default normaal alleen als
de router zelf een default route in zijn routingtable heeft. Dat is een nuttige
veiligheidsvoorwaarde: de edge belooft pas een uitweg wanneer hij er zelf één kent.

Waar let je op?

| Vraag | Waarom belangrijk? |
|---|---|
| Heeft de edge-router zelf een default route? | Anders heeft hij niets zinvols om te verspreiden. |
| Wordt de default route in OSPF geïnjecteerd? | Interne routers moeten onbekende bestemmingen leren. |
| Bereikt de default route alle areas? | Anders werkt internet in de ene area wel en in de andere niet. |
| Staat filtering of summarization niet in de weg? | Routebeleid kan verspreiding beperken. |

Analysevoorbeeld:

> Area 10 leert wel routes naar area 20, maar geen default route. Daardoor werkt interne communicatie tussen gebouwen, maar internetverkeer vanuit gebouw A faalt.

### 7.16 Packet Tracer-analyse: welke vragen stel je?

In een multi-area OSPF-lab vertrek je niet van commando's, maar van onderzoeksvragen.

| Onderzoeksvraag | Commando | Wat zoek je? |
|---|---|---|
| Welke routers zijn neighbors? | `show ip ospf neighbor` | Neighbor ID, state en interface. |
| In welke area zit een interface? | `show ip ospf interface` | Area per interface. |
| Welke networks worden in OSPF geactiveerd? | `show ip protocols` | Network statements en areas. |
| Welke routes komen uit een andere area? | `show ip route` | Routes met code `O IA`. |
| Is er een default route? | `show ip route` | `0.0.0.0/0`, vaak `O*E2`. |
| Welke router is ABR? | `show ip ospf` en topologieanalyse | Router met OSPF-interfaces in area 0 en een andere area. |

Een goede analysevolgorde:

1. Teken de routed topologie.
2. Noteer per link welke area gebruikt wordt.
3. Controleer neighbors.
4. Controleer of ABR's logisch geplaatst zijn.
5. Controleer inter-area routes met `show ip route`.
6. Controleer default routeverspreiding.
7. Beoordeel of het adresplan summarization mogelijk maakt.

### 7.17 Mini-case: gebouw B is niet bereikbaar

Situatie:

Een campusnetwerk gebruikt multi-area OSPF:

```text
Gebouw A       Backbone        Gebouw B
area 10  ----  area 0   ----   area 20
```

Vaststellingen op `R-A`:

| Controle | Resultaat |
|---|---|
| Neighbor met `R-CORE` | Full |
| Routes naar area 0-links | Aanwezig |
| Routes naar gebouw B | Ontbreken |
| `show ip route` | Geen `O IA` routes naar `10.20.0.0/16` |

Mogelijke oorzaken:

- `R-B` vormt geen neighbor met `R-CORE`;
- link tussen `R-B` en `R-CORE` zit in verkeerde area;
- area 20 is niet correct verbonden met area 0;
- network statements op `R-B` activeren de usernetwerken niet;
- summarization of filtering is fout geconfigureerd.

Sterke conclusie:

> `R-A` heeft een correcte neighbor met de backbone, maar leert geen inter-area routes naar gebouw B. Het probleem zit waarschijnlijk aan de area 20-kant: controleer de ABR `R-B`, de area-indeling op de link naar `R-CORE` en de OSPF-advertenties van de gebouw-B-netwerken.

### 7.18 Typische fouten bij OSPF areas

| Fout | Waarom problematisch? | Betere aanpak |
|---|---|---|
| Alles blijft in area 0 zonder ontwerpkeuze. | Werkt in kleine labs, maar schaalt minder goed. | Denk na over areas per gebouw, zone of locatie. |
| Area mismatch op een link. | Neighbor vormt niet correct. | Beide kanten van dezelfde link in dezelfde area zetten. |
| Non-backbone area hangt niet aan area 0. | Inter-area routing kan fout lopen. | Verbind non-backbone areas via area 0. |
| Access/usernetwerken willekeurig over areas verdelen. | Ontwerp wordt moeilijk te begrijpen. | Koppel areas aan logische delen van het netwerk. |
| Geen duidelijk ABR-concept. | Studenten weten niet waar routes tussen areas passeren. | Duid ABR's expliciet aan in de topologie. |
| Rommelig adresplan. | Summarization wordt moeilijk of onmogelijk. | Plan subnetten per area logisch. |
| Client-SVI's zijn niet passive. | Onnodige hello's en ongewenste neighborvorming worden mogelijk. | Maak interfaces standaard passive en open alleen transitlinks. |
| `default-information originate` zonder werkende uitweg. | Interne routers krijgen geen bruikbare internetroute. | Controleer eerst de default route op de edge en daarna de externe OSPF-route intern. |
| Alleen neighbors controleren. | Neighbors kunnen goed zijn terwijl routes ontbreken. | Controleer ook `O IA` routes en default routes. |

### 7.19 Samenvatting OSPF areas

OSPF areas maken van OSPF een schaalbaarder enterprise-routingprotocol.

Studenten moeten vooral onthouden:

- area 0 is de backbone area;
- non-backbone areas moeten logisch met area 0 verbonden zijn;
- een ABR verbindt meerdere OSPF-areas;
- routes uit andere areas verschijnen vaak als `O IA`;
- area mismatch kan neighborvorming breken;
- passive interfaces adverteren het netwerk zonder neighbors te zoeken op
  clientnetwerken;
- areas zijn geen VLAN's en geen subnetten, maar routing-ontwerpzones;
- summarization hoort bij een goed adresplan en gebeurt conceptueel aan area-grenzen;
- in Packet Tracer moet je per link kunnen uitleggen in welke area die zit en waarom.

Kernzin:

> OSPF areas zijn geen extra syntaxlaagje, maar een ontwerpmechanisme om grotere enterprise-netwerken logisch, schaalbaar en troubleshootbaar te houden.

---

## 8. Gateway redundancy conceptueel

### 8.1 Waarom een enkele default gateway een risico is

Clients in een VLAN gebruiken meestal een default gateway om andere netwerken te bereiken. Die default gateway is vaak het IP-adres van een routerinterface of een SVI op een multilayer switch.

Voorbeeld:

| VLAN | Subnet | Default gateway |
|---:|---|---|
| 10 | `10.20.10.0/24` | `10.20.10.1` |
| 20 | `10.20.20.0/24` | `10.20.20.1` |
| 99 | `10.20.99.0/24` | `10.20.99.1` |

Zolang de router of multilayer switch met dat gateway-adres werkt, is er geen probleem.

Maar stel:

- de gateway-router valt uit;
- de multilayer switch herstart;
- de uplink naar de gateway faalt;
- een software- of configuratiefout maakt de SVI onbereikbaar.

Dan hebben clients nog altijd een IP-adres, maar ze raken niet meer buiten hun eigen VLAN.

Belangrijke vaststelling:

> Een client kan lokaal perfect verbonden lijken, maar toch geen andere netwerken bereiken omdat de default gateway wegvalt.

Dit is een klassiek single point of failure.

### 8.2 Het probleem zichtbaar maken

Eenvoudige topologie zonder gateway redundancy:

```text
PC's in VLAN 10
      |
      |
  SW-ACCESS
      |
      |
  SW-DIST-1
  gateway: 10.20.10.1
      |
      |
 rest van het netwerk
```

Als `SW-DIST-1` uitvalt:

- clients behouden mogelijk hun IP-adres;
- clients kunnen misschien nog andere toestellen in hetzelfde VLAN bereiken;
- clients kunnen hun default gateway niet meer bereiken;
- verkeer naar servers, andere VLAN's of internet faalt.

Slechte conclusie:

> De switchpoort van de pc is up, dus het netwerk werkt.

Betere enterprise-conclusie:

> De client heeft lokale link, maar de default gateway is een single point of failure. Zonder gateway redundancy valt inter-VLAN verkeer uit wanneer `SW-DIST-1` faalt.

### 8.3 Het basisidee van gateway redundancy

Gateway redundancy zorgt ervoor dat meerdere routers of multilayer switches samen een default gateway kunnen aanbieden aan clients.

De clients gebruiken een **virtual IP address** als default gateway. Dat virtuele IP-adres hoort niet permanent bij een enkele fysieke router. Het wordt beheerd door een groep toestellen.

Conceptueel:

```text
                   virtual gateway IP
                       10.20.10.1
                            |
              +-------------+-------------+
              |                           |
        +-----+------+              +-----+------+
        | SW-DIST-1  |              | SW-DIST-2  |
        | active     |              | standby    |
        | 10.20.10.2 |              | 10.20.10.3 |
        +------------+              +------------+
              |                           |
              +-------------+-------------+
                            |
                       SW-ACCESS
                            |
                           PC's
```

De pc's gebruiken:

```text
default gateway: 10.20.10.1
```

Maar intern wordt dat virtuele gateway-adres gedragen door `SW-DIST-1` of `SW-DIST-2`.

Als `SW-DIST-1` faalt, kan `SW-DIST-2` de actieve rol overnemen. Voor de client blijft de default gateway hetzelfde IP-adres.

Dat is het grote voordeel:

> Clients hoeven hun default gateway niet te veranderen wanneer een gatewaytoestel faalt.

### 8.4 First-hop redundancy: HSRP en VRRP

Protocollen voor een redundante eerste routerhop heten **First Hop Redundancy
Protocols** of FHRP's. Ze beschermen de hop van de client naar zijn default gateway.
Ze controleren niet automatisch of de rest van het pad naar de bestemming gezond is.

Er bestaan verschillende FHRP's.

Twee belangrijke voorbeelden:

- **HSRP (Hot Standby Router Protocol)**;
- **VRRP (Virtual Router Redundancy Protocol)**.

HSRP is Cisco-eigen. VRRP is een open standaard. Conceptueel doen ze iets gelijkaardigs: meerdere routers of multilayer switches bieden samen een virtuele default gateway aan.

Voor dit hoofdstuk is vooral het concept belangrijk.

| Concept | Betekenis |
|---|---|
| Virtual IP | Het gateway-adres dat clients gebruiken. |
| Active router | Het toestel dat momenteel verkeer voor de virtual gateway verwerkt. |
| Standby router | Het toestel dat klaarstaat om over te nemen. |
| Priority | Waarde waarmee bepaald wordt welk toestel active wordt. |
| Preemption | Mogelijkheid waarbij een beter toestel de active rol opnieuw overneemt. |

In Packet Tracer is HSRP meestal de meest haalbare keuze om beperkt praktisch te tonen. VRRP kan conceptueel besproken worden als open alternatief.

### 8.5 Active en standby

Bij HSRP of VRRP is er per gatewaygroep meestal een active en een standby rol.

Voorbeeld voor VLAN 10:

| Toestel | Echt IP-adres | Rol | Virtual IP |
|---|---|---|---|
| `SW-DIST-1` | `10.20.10.2` | active | `10.20.10.1` |
| `SW-DIST-2` | `10.20.10.3` | standby | `10.20.10.1` |
| Clients | DHCP of statisch | gebruiken gateway | `10.20.10.1` |

Clients kennen dus niet `10.20.10.2` of `10.20.10.3` als default gateway. Zij gebruiken alleen het virtuele adres `10.20.10.1`.

Waarom is dat goed?

- clients hoeven niet te weten welk fysiek toestel active is;
- failover kan gebeuren zonder IP-aanpassing op clients;
- de gatewaylaag wordt robuuster;
- onderhoud aan een distributionswitch kan minder impact hebben.

Naast het virtuele IP-adres gebruikt de groep ook een virtuele MAC-identiteit. Wanneer
de active rol verandert, neemt het nieuwe toestel die virtuele identiteit over. De
bestaande IP-naar-MAC-koppeling op clients kan daardoor bruikbaar blijven, terwijl de
switches leren via welke poort de virtuele MAC nu bereikbaar is. De client hoeft geen
nieuw gatewayadres te krijgen.

### 8.6 Wat gebeurt er bij failover?

Normale toestand:

```text
SW-DIST-1 = active
SW-DIST-2 = standby
Virtual IP = 10.20.10.1
```

Fouttoestand:

```text
SW-DIST-1 valt uit
SW-DIST-2 neemt active rol over
Virtual IP blijft 10.20.10.1
```

Voor de client:

- default gateway blijft `10.20.10.1`;
- er kan kort pakketverlies zijn tijdens failover;
- na overname loopt verkeer via `SW-DIST-2`.

Belangrijke nuance:

Gateway redundancy garandeert niet dat elke storing onzichtbaar is. Er kan korte onderbreking zijn. Het doel is niet "nooit pakketverlies", maar wel "geen manuele herconfiguratie en geen langdurige uitval door een enkele gateway".

### 8.7 Priority, preemption en tracking

Drie instellingen bepalen samen of de gewenste gateway ook de **bruikbare** gateway
blijft.

| Instelling | Doel | Risico bij verkeerde aanname |
|---|---|---|
| priority | bepaalt welk toestel de voorkeur krijgt als active | beide toestellen gebruiken de standaardwaarde en de keuze wordt minder expliciet |
| preemption | laat een toestel met hogere priority na herstel opnieuw active worden | herstel leidt niet terug naar het ontworpen primaire pad, of veroorzaakt onnodige rolwissels |
| interface/object tracking | verlaagt de voorkeur wanneer een kritieke uplink of route wegvalt | een gateway blijft active hoewel zijn pad naar de core defect is |

Zonder tracking kan dit gebeuren:

```text
client -> MLS-DIST1 is nog active voor HSRP
                  X uplink naar core is defect

client -> MLS-DIST2 is standby
                  + uplink naar core werkt
```

De client bereikt nog steeds de virtuele gateway op `MLS-DIST1`, maar verkeer kan daar
vastlopen. Tracking kan de HSRP-priority van `MLS-DIST1` verlagen wanneer de kritieke
uplink of een relevant object faalt, zodat `MLS-DIST2` overneemt.

Conceptueel voorbeeld:

```text
track 1 interface GigabitEthernet0/1 line-protocol

interface vlan 10
 standby 10 priority 110
 standby 10 preempt
 standby 10 track 1 decrement 20
```

De exacte mogelijkheden hangen af van het platform en van Packet Tracer. In het lab
kan je HSRP-failover vereenvoudigd met een SVI- of toesteluitval testen. In productie
moet je ook een defect **achter** de nog actieve gateway kunnen detecteren.

Kernzin:

> Een gateway is pas een goede active gateway als ook zijn verdere datapad bruikbaar
> is.

### 8.8 Gateway redundancy is niet hetzelfde als routing redundancy

Gateway redundancy lost een specifiek probleem op: de default gateway van clients.

Het vervangt niet:

- STP;
- EtherChannel;
- OSPF;
- correcte trunkconfiguratie;
- fysieke redundantie;
- monitoring.

Voorbeeld:

```text
PC ---- SW-ACCESS ---- SW-DIST-1 / SW-DIST-2 ---- core ---- internet
```

Om dit robuust te maken, heb je meerdere lagen nodig:

| Laag | Mechanisme | Vraag |
|---|---|---|
| Access naar distribution | STP of EtherChannel | Blijft de uplink beschikbaar? |
| Default gateway | HSRP of VRRP | Blijft de gateway voor clients beschikbaar? |
| Routing naar core/internet | OSPF of static failover | Blijft er een route naar buiten? |
| Trunks/VLAN's | Correcte trunkconfiguratie | Blijft het VLAN op het juiste pad beschikbaar? |

Slechte situatie:

> Er is HSRP geconfigureerd, dus het netwerk is redundant.

Betere analyse:

> HSRP beschermt de default gateway, maar ik moet ook controleren of trunks, STP/EtherChannel en routing na failover correct blijven werken.

### 8.9 HSRP conceptueel in configuratie

Een vereenvoudigd HSRP-voorbeeld voor VLAN 10:

Op `SW-DIST-1`:

```text
interface vlan 10
 ip address 10.20.10.2 255.255.255.0
 standby 10 ip 10.20.10.1
 standby 10 priority 110
 standby 10 preempt
```

Op `SW-DIST-2`:

```text
interface vlan 10
 ip address 10.20.10.3 255.255.255.0
 standby 10 ip 10.20.10.1
 standby 10 priority 100
 standby 10 preempt
```

Conceptueel:

- `10.20.10.2` is het echte IP-adres van `SW-DIST-1`;
- `10.20.10.3` is het echte IP-adres van `SW-DIST-2`;
- `10.20.10.1` is het virtuele gateway-adres;
- de hoogste priority wordt active;
- `preempt` laat het toestel met hogere priority de active rol terugnemen.

Voor dit hoofdstuk is het niet nodig om HSRP-syntax uitgebreid vanbuiten te leren. Het belangrijkste is dat studenten de drie IP-adressen kunnen onderscheiden:

| Type adres | Voorbeeld | Wie gebruikt het? |
|---|---|---|
| Virtual gateway IP | `10.20.10.1` | Clients als default gateway. |
| Echt IP `SW-DIST-1` | `10.20.10.2` | Beheer, routing, toestelidentiteit. |
| Echt IP `SW-DIST-2` | `10.20.10.3` | Beheer, routing, toestelidentiteit. |

### 8.10 Gateway redundancy per VLAN

Gateway redundancy wordt meestal per VLAN of per subnet bekeken.

Voorbeeld:

| VLAN | Virtual gateway | Active | Standby |
|---:|---|---|---|
| 10 | `10.20.10.1` | `SW-DIST-1` | `SW-DIST-2` |
| 20 | `10.20.20.1` | `SW-DIST-1` | `SW-DIST-2` |
| 50 | `10.20.50.1` | `SW-DIST-2` | `SW-DIST-1` |
| 99 | `10.20.99.1` | `SW-DIST-1` | `SW-DIST-2` |

In sommige ontwerpen laat je een distributionswitch active zijn voor bepaalde VLAN's en de andere distributionswitch active voor andere VLAN's. Dat kan load sharing opleveren.

Maar let op:

> Load sharing via gateway redundancy is alleen zinvol als STP, EtherChannel en routing ook passen bij dat ontwerp.

Slecht voorbeeld:

- VLAN 50 heeft `SW-DIST-2` als active HSRP-router;
- STP-root voor VLAN 50 is `SW-DIST-1`;
- verkeer moet daardoor mogelijk een onlogisch pad volgen.

Betere aanpak:

- stem HSRP active rollen af op STP-rootkeuzes;
- documenteer per VLAN welke switch primary is;
- controleer failover per VLAN.

### 8.11 Gateway redundancy controleren

Bij HSRP gebruik je bijvoorbeeld:

```text
show standby
```

Afhankelijk van toestel en Packet Tracer-versie kan de output verschillen, maar je zoekt conceptueel naar:

| Vraag | Wat zoek je? |
|---|---|
| Welke groep is actief? | HSRP group, bijvoorbeeld groep 10. |
| Wat is de virtual IP? | Bijvoorbeeld `10.20.10.1`. |
| Is dit toestel active of standby? | Rol van de lokale router/switch. |
| Wie is de standby? | Het toestel dat overneemt bij falen. |
| Welke priority wordt gebruikt? | Bepaalt wie active wordt. |
| Is preempt actief? | Kan de primary rol terugkeren na herstel? |
| Wordt een kritieke uplink gevolgd? | Kan een toestel zijn active rol afstaan als het verdere pad faalt? |

Andere nuttige controles:

| Onderzoeksvraag | Mogelijk commando |
|---|---|
| Kan de client de virtual gateway pingen? | `ping 10.20.10.1` |
| Welke default gateway gebruikt de client? | IP-configuratie van de client |
| Is de SVI up? | `show ip interface brief` |
| Blijven routes beschikbaar na failover? | `show ip route` |
| Blijven VLAN's/trunks beschikbaar? | `show interfaces trunk` |

Sterke analysezin:

> `SW-DIST-1` is active voor HSRP groep 10 en `SW-DIST-2` is standby. De clients gebruiken `10.20.10.1` als default gateway. Bij uitval van `SW-DIST-1` moet `SW-DIST-2` active worden zonder dat clients een andere gateway moeten krijgen.

### 8.12 Failover testen

Gateway redundancy moet je testen. Alleen configureren is niet genoeg.

Mogelijke Packet Tracer-test:

| Stap | Actie | Verwachte observatie |
|---:|---|---|
| 1 | Ping vanaf client naar server in ander VLAN. | Ping werkt. |
| 2 | Controleer `show standby`. | Een toestel is active, het andere standby. |
| 3 | Schakel de active gatewayinterface uit. | Standby neemt active rol over. |
| 4 | Herhaal de ping. | Kort verlies is mogelijk, daarna herstel. |
| 5 | Controleer `show standby` opnieuw. | Nieuwe active is zichtbaar. |
| 6 | Herstel de eerste gateway. | Afhankelijk van preempt neemt die eventueel terug over. |

Een tweede test is minstens even belangrijk: laat het HSRP-toestel zelf actief, maar
onderbreek zijn routed uplink naar de core. Zonder tracking kan HSRP active blijven
terwijl eind-tot-eindverkeer faalt. Met correct trackinggedrag hoort het gezonde
toestel over te nemen.

Belangrijke reflectie:

> Een geslaagde failovertest betekent niet alleen dat ping opnieuw werkt. Je moet ook kunnen uitleggen welk toestel de active rol heeft overgenomen en waarom.

### 8.13 Typische fouten bij gateway redundancy

| Fout | Waarom problematisch? | Betere aanpak |
|---|---|---|
| Clients gebruiken het echte IP van `SW-DIST-1` als gateway. | Failover helpt niet, want clients wijzen naar een fysiek toestel. | Clients gebruiken de virtual IP. |
| HSRP/VRRP maar op een VLAN configureren. | Andere VLAN's blijven kwetsbaar. | Controleer gateway redundancy per VLAN. |
| Active gateway en STP-root zijn niet afgestemd. | Verkeer kan onlogische paden volgen. | Stem root bridge en active gateway af. |
| Geen failovertest uitvoeren. | Redundantie lijkt aanwezig, maar is niet bewezen. | Test uitval van active gateway. |
| Geen preempt waar het ontwerp dat verwacht. | Primary toestel neemt na herstel niet terug over. | Configureer preempt bewust. |
| Geen tracking van het verdere pad. | Een gateway zonder bruikbare coreverbinding blijft active. | Track een relevante uplink of bereikbaarheidsvoorwaarde. |
| Alleen naar ping kijken. | Ping toont niet welke gateway active is. | Gebruik `show standby` of equivalent. |
| Routing na failover niet controleren. | Gateway neemt over, maar routes naar buiten ontbreken. | Controleer ook routingtabellen. |

### 8.14 Samenvatting gateway redundancy

Gateway redundancy voorkomt dat de default gateway van clients een single point of failure blijft.

Studenten moeten vooral onthouden:

- clients gebruiken een default gateway om buiten hun subnet te communiceren;
- een enkele gateway is een single point of failure;
- HSRP en VRRP bieden een virtuele default gateway;
- clients gebruiken de virtual IP als gateway;
- een active toestel verwerkt verkeer, een standby toestel kan overnemen;
- priority, preemption en tracking bepalen wanneer een toestel active hoort te zijn;
- gateway redundancy moet per VLAN bekeken worden;
- HSRP/VRRP vervangt STP, EtherChannel of routing niet;
- failover moet getest en verklaard worden.

Kernzin:

> Gateway redundancy zorgt ervoor dat clients dezelfde default gateway blijven gebruiken, zelfs wanneer het fysieke gatewaytoestel verandert.

---

## 9. De mechanismen als één ontwerp lezen

STP, EtherChannel, OSPF en HSRP hebben elk een eigen toestand. Voor gebruikers telt
echter maar één resultaat: blijft de dienst bereikbaar?

### 9.1 Van fysiek pad naar gebruikersdienst

Gebruik bij analyse steeds deze afhankelijkheidsketen:

```text
1. fysieke link
      |
2. VLAN en trunk
      |
3. STP of Port-channel
      |
4. SVI en virtuele gateway
      |
5. routed link en OSPF-neighbor
      |
6. specifieke route of default route
      |
7. eind-tot-einddienst
```

Een fout hoger in de keten maakt controles lager in de keten mogelijk zinloos.
Bijvoorbeeld: als VLAN 50 niet over de trunk loopt, hoef je een falende serverping nog
niet met OSPF-instellingen te verklaren.

| Laag in de keten | Vraag | Mogelijk bewijs |
|---|---|---|
| fysiek | zijn de bedoelde interfaces operationeel? | `show ip interface brief`, interface-status en cabling |
| Layer 2 | bestaat het VLAN op de juiste switches en trunks? | `show vlan brief`, `show interfaces trunk` |
| loopvrije topologie | welk pad is actief voor dit VLAN? | `show spanning-tree vlan ...` |
| bundeling | zijn alle members actief en consistent? | `show etherchannel summary` |
| first hop | gebruikt de client de virtual IP en wie is active? | clientconfiguratie, `show standby brief` |
| routingcontrolplane | bestaan de verwachte neighbors? | `show ip ospf neighbor` |
| routingdataplane | staat de juiste route in de table? | `show ip route`, `show ip route ospf` |
| dienst | bereikt de echte bron de echte bestemming? | gerichte ping, traceroute en applicatietest |

Kernidee:

> Onderzoek eerst de vroegste schakel die niet aan de verwachting voldoet. Wijzig niet
> willekeurig een protocol verderop in de keten.

### 9.2 STP-root en HSRP-active afstemmen

Per VLAN is het meestal logisch dat de active HSRP-gateway ook de STP-root is. Het
Layer 2-pad vanaf de accesslaag eindigt dan rechtstreeks bij het toestel dat het verkeer
routeert.

Voorbeeld van een bewust gespreid ontwerp:

| VLAN | Functie | STP primary root | HSRP active | Beoordeling |
|---:|---|---|---|---|
| 10 | kantoor A | `MLS-DIST1` | `MLS-DIST1` | uitgelijnd |
| 20 | magazijn | `MLS-DIST1` | `MLS-DIST1` | uitgelijnd |
| 30 | kantoor B | `MLS-DIST2` | `MLS-DIST2` | uitgelijnd |
| 50 | servers | `MLS-DIST2` | `MLS-DIST2` | uitgelijnd als alle trunks VLAN 50 dragen |
| 99 | management | `SW-ACC1` | geen virtuele gateway | fout: root en gatewayredundantie ontbreken op de juiste laag |

Een mismatch kan onnodig verkeer over de inter-distributionlink veroorzaken:

```text
client
  -> STP brengt VLAN 10 naar MLS-DIST1
  -> HSRP active voor VLAN 10 staat op MLS-DIST2
  -> frame kruist eerst de inter-distributionlink
  -> MLS-DIST2 routeert het verkeer
```

Dit kan technisch werken, maar gebruikt een langer pad en maakt de inter-
distributionlink belangrijker dan nodig. Het is daarom geen fout die je alleen met een
ping ontdekt.

Controleer:

1. de root bridge per VLAN;
2. de HSRP-active-rol per VLAN;
3. de forwarding- en alternatepoorten;
4. of de benodigde VLAN's de inter-distributionlink passeren;
5. het gedrag na uitval van de primaire distributionswitch.

### 9.3 Redundantie en foutdomeinen

Redundantie beperkt uitval alleen wanneer redundante onderdelen niet hetzelfde
foutdomein delen.

| Ontwerp | Schijnbare redundantie | Gemeenschappelijk foutdomein |
|---|---|---|
| twee kabels in dezelfde kabelgoot | twee fysieke links | graaf- of brandschade treft beide |
| twee uplinks naar dezelfde lijnkaart | twee poorten | defect van de lijnkaart treft beide |
| twee gateways met één voeding of PDU | twee toestellen | stroomuitval treft beide |
| twee routed paden via dezelfde core-router | twee interfaces | core-router blijft single point of failure |
| HSRP zonder tweede bruikbare OSPF-route | twee gateways | routing achter de gateway is niet redundant |

In Packet Tracer zijn voeding, kabeltracés, control-planebelasting en hardwarefouten
sterk vereenvoudigd. De workshop bewijst protocolgedrag, niet de volledige
beschikbaarheid van een productieomgeving.

Kernzin:

> Twee exemplaren zijn pas echt redundant wanneer de relevante storing ze niet
> tegelijk uitschakelt.

---

## 10. Methodisch troubleshooten

Troubleshooting begint met een verwachte toestand. Zonder verwachting kan je wel
output verzamelen, maar niet bepalen wat afwijkend is.

### 10.1 Verwacht, observeer, verklaar

Gebruik voor elke vaststelling hetzelfde patroon:

| Stap | Vraag | Voorbeeld |
|---|---|---|
| verwachting | wat hoort volgens het ontwerp te gebeuren? | `MLS-DIST2` vormt via `Gi0/1` een OSPF-neighbor met `R-CORE` in area 0 |
| observatie | wat toont het toestel werkelijk? | de interface is up, maar de neighbor ontbreekt |
| lokalisatie | welke laag of welk protocol wijkt af? | IP-link werkt; OSPF-adjacency faalt |
| verklaring | welke configuratie verklaart dit bewijs? | de twee kanten van de link gebruiken een andere area |
| impact | welke dienst of redundantie wordt geraakt? | failover via `MLS-DIST2` kan geen routes naar de core gebruiken |
| verbetering | welke gerichte wijziging herstelt het ontwerp? | beide kanten van de transitlink in area 0 plaatsen |
| acceptatie | welke test bewijst het herstel? | neighbor wordt `FULL`, routes verschijnen en uplinkfailover slaagt |

Dit voorkomt een zwakke conclusie zoals:

> OSPF werkt niet.

Een professionele conclusie is specifieker:

> De routed link is operationeel, maar `MLS-DIST2` vormt geen OSPF-neighbor met
> `R-CORE` doordat de interfaces niet in dezelfde area zitten. Daardoor ontbreekt het
> routed back-uppad. Na correctie moeten de adjacency, de verwachte routes en de
> failovertest opnieuw gecontroleerd worden.

### 10.2 Eerst control plane, daarna data plane

De **control plane** bouwt de beslisinformatie op, zoals STP-rollen,
OSPF-neighborships en routes. De **data plane** gebruikt die beslissingen om echte
frames en pakketten door te sturen. Je controleert beide.

Bij elk protocol maak je onderscheid tussen de informatie waarmee toestellen een
beslissing opbouwen en het echte verkeer dat die beslissing gebruikt.

| Mechanisme | Control-planebewijs | Data-planebewijs |
|---|---|---|
| STP | root bridge, roles en states | verkeer gebruikt na linkuitval het nieuwe forwardingpad |
| LACP | members zijn gebundeld in de Port-channel | verkeer blijft lopen na uitval van één member |
| OSPF | neighbor is `FULL` en LSDB/routinginformatie wordt uitgewisseld | pakket volgt een geïnstalleerde route naar de bestemming |
| HSRP | active/standby en virtual IP zijn correct | clientverkeer blijft werken na rolwissel |

Alleen control-planebewijs is onvoldoende. Een OSPF-neighbor kan `FULL` zijn terwijl
het gewenste subnet niet geadverteerd wordt. Alleen data-planebewijs is ook
onvoldoende: een ping kan via één primair pad slagen terwijl het back-uppad defect is.

### 10.3 Een storing lokaliseren zonder gokken

Voorbeeld: `PC-OFFICE-A` bereikt de server in VLAN 50 niet.

Een gerichte onderzoeksvolgorde:

1. Controleer IP-adres, prefix en virtuele gateway op de client.
2. Test de virtuele gateway van het bron-VLAN.
3. Controleer welke HSRP-router active is.
4. Controleer of bron- en doel-VLAN over de bedoelde trunks en Port-channel lopen.
5. Lees STP voor precies die VLAN's.
6. Controleer OSPF-neighbors op de active gateway.
7. Zoek de specifieke route naar het doelnetwerk.
8. Test vanaf tussenliggende netwerktoestellen om het foutdomein te verkleinen.
9. Voer pas daarna een gerichte configuratiewijziging uit.
10. Herhaal de oorspronkelijke eind-tot-eindtest en de relevante negatieve test.

Typische fout:

> Meteen `no shutdown`, extra `network`-statements of ruimere allowed VLAN-lijsten
> toevoegen zonder eerst te bewijzen waar het pad breekt.

Zo'n wijziging kan het symptoom verplaatsen, securitygrenzen verbreden of een tweede
fout introduceren.

---

## 11. Testplan voor de redundante campus

Een goede test vergelijkt een gekende beginsituatie met één gecontroleerde wijziging.
Na de test herstel je de beginsituatie en controleer je of het ontwerp terugkeert naar
de gewenste toestand.

### 11.1 Vier fasen per failovertest

| Fase | Wat doe je? | Waarom? |
|---|---|---|
| baseline | noteer roles, states, routes en een werkende eind-tot-eindtest | zonder nulmeting kan je verandering niet betrouwbaar verklaren |
| injectie | schakel exact één gekend onderdeel uit | zo blijft oorzaak en gevolg afgebakend |
| observatie | meet protocoltoestand, herstelduur en gebruikersimpact | dit bewijst welk mechanisme overneemt |
| herstel | activeer het onderdeel opnieuw en controleer de eindtoestand | terugkeer naar het primaire pad kan andere problemen tonen dan failover |

Gebruik bij voorkeur een doorlopende ping als indicatie van onderbreking, maar combineer
die altijd met protocoloutput. Het precieze aantal verloren pings in Packet Tracer is
geen betrouwbare productie-SLA.

### 11.2 Minimale testmatrix

| Test | Actie | Verwacht | Negatief bewijs dat je wilt uitsluiten | Nuttig bewijs |
|---|---|---|---|---|
| STP-uplinkfailover | actieve access-uplink uitschakelen | alternate pad wordt forwarding en dienst herstelt | beide uplinks dragen niet dezelfde nodige VLAN's | STP-output voor/na en eind-tot-eindping |
| EtherChannel-member | één LACP-member uitschakelen | Port-channel blijft up met minder capaciteit | volledige Port-channel valt weg of verkeerde member was niet gebundeld | `show etherchannel summary` voor/na |
| HSRP-gateway | active SVI of toestel uitschakelen | standby wordt active; virtual IP blijft gelijk | client gebruikt fysiek gatewayadres | `show standby brief`, clientconfiguratie en ping |
| upstream gatewaypad | core-uplink van active gateway uitschakelen | tracking of routingontwerp stuurt verkeer via gezond pad | HSRP blijft active zonder bruikbare uitweg | HSRP-, OSPF- en route-output |
| OSPF-transitlink | primair routed pad uitschakelen | alternatieve adjacency/route draagt verkeer | tweede fysieke link heeft geen neighbor of juiste area | neighbors, route voor/na en traceroute |
| inter-area route | bestemming in andere area testen | route verschijnt als passend OSPF-route-type | neighbor is up maar doelnetwerk ontbreekt | `show ip route ospf` en ping |
| default route | extern testadres bereiken | interne router heeft een bruikbare `0.0.0.0/0` | alleen interne routes werken | route op edge én interne router, externe test |
| managementgateway | managementclient test virtual IP en failover | beheerpad blijft beschikbaar | VLAN 99 heeft geen FHRP of verkeerde STP-root | gatewayconfiguratie, STP en HSRP |

### 11.3 Bewijs verzamelen

Een goed bewijsstuk toont alleen wat nodig is om de conclusie te ondersteunen.

| Bewijs | Wat moet zichtbaar zijn? |
|---|---|
| STP-output | VLAN, root ID, lokale bridge ID, poortrol en toestand |
| EtherChannel-output | Port-channel, protocol en alle verwachte memberinterfaces |
| OSPF-neighboroutput | lokale context, neighbor ID, state en interface |
| routingtable | exacte doelprefix, routecode, next hop en eventueel default route |
| HSRP-output | VLAN/groep, virtual IP, local state, peer en priority |
| connectiviteitstest | bron, bestemming, tijdstip/fase en resultaat |

Noteer daarnaast altijd welke ingreep je uitvoerde. Een screenshot zonder bron,
verwachting of testfase is zwak bewijs.

Voorbeeldnotatie:

```text
Test: EtherChannel-member failure
Baseline: Po1 up, Fa0/23 en Fa0/24 gebundeld, serverping slaagt
Actie: shutdown Fa0/23 op MLS-DIST1
Verwacht: Po1 blijft up via Fa0/24; hoogstens korte onderbreking
Werkelijk: ...
Bewijs: show etherchannel summary + ping naar SRV-APP
Conclusie: ...
Herstel: no shutdown Fa0/23; beide members opnieuw actief
```

Kernzin:

> Een failovertest bewijst zowel welk protocol reageert als welke gebruikersdienst
> daardoor beschikbaar blijft.

---

## 12. Van technische observatie naar professioneel advies

Een lijst met commando-output is nog geen advies. Koppel elke relevante observatie aan
het risico en aan een verifieerbare verbetering.

Gebruik deze keten:

```text
requirement
  -> observatie en bewijs
  -> afwijking
  -> technisch risico
  -> bedrijfsimpact
  -> gerichte maatregel
  -> acceptatietest
```

Voorbeeld:

| Onderdeel | Uitwerking |
|---|---|
| requirement | het managementnetwerk moet bereikbaar blijven bij uitval van één distributionswitch |
| observatie | `PC-ADMIN` gebruikt `10.99.0.2`, het fysieke SVI-adres van `MLS-DIST1`; groep 99 ontbreekt in `show standby` |
| afwijking | VLAN 99 heeft geen virtuele gateway |
| risico | `MLS-DIST1` blijft een single point of failure voor beheerconnectiviteit |
| bedrijfsimpact | tijdens de storing kan IT netwerktoestellen niet via het management-VLAN bereiken en duurt herstel langer |
| maatregel | configureer HSRP op beide SVI's, gebruik de virtual IP op de client en lijn STP-root en active gateway uit |
| acceptatietest | schakel de active gateway gecontroleerd uit en bewijs rolwissel én bereikbaarheid van een managementdoel |

Een maatregel is sterker wanneer je ook de grens ervan benoemt:

> HSRP beschermt de first hop, maar niet automatisch het routed pad naar de core.
> Daarom hoort bij de acceptatietest ook een route- en eind-tot-eindcontrole.

---

## 13. Labkeuzes en productieontwerp

Packet Tracer maakt protocolgedrag zichtbaar, maar simuleert niet elk productierisico.

| Thema | In het lab | In productie |
|---|---|---|
| topologie | enkele switches en routers | capaciteit, foutdomeinen, bekabelingsroutes en onderhoudsvensters worden ontworpen |
| STP | root, alternate pad en convergentie observeren | ook edge protection, root protection, consistente variant en monitoring voorzien |
| EtherChannel | twee links en LACP-status testen | hashing, minimale actieve links, platformlimieten en multi-chassistechnologie beoordelen |
| OSPF | duidelijke areas en eenvoudige costs | adresplan, summarization, authenticatie, timers, filtering en failure scenarios documenteren |
| HSRP | SVI- of toesteluitval simuleren | tracking, capaciteit van de standby, beleid voor terugkeer en onderhoudsgedrag testen |
| bewijs | screenshots en `show`-output | monitoring, syslog, telemetry, tijdsynchronisatie en wijzigingsregistratie gebruiken |
| beschikbaarheid | enkele pings tijdens failover | meetbare SLO/SLA, convergentietijd en applicatie-impact vastleggen |

Een ontwerp is niet automatisch beter omdat elk mogelijk redundant mechanisme is
ingeschakeld. Extra complexiteit vraagt configuratiebeheer, monitoring, expertise en
testen. Kies redundantie op basis van bedrijfsimpact en hersteldoelstellingen.

In productie:

- documenteer primary en secondary rollen per VLAN en area;
- monitor ook gedegradeerde toestanden waarin de dienst nog werkt;
- beheer configuratiewijzigingen en voorzie een herstelplan;
- test tijdens een gecontroleerd venster en bepaal stopcriteria;
- controleer of het secundaire pad voldoende capaciteit heeft;
- behandel managementtoegang en tijdsynchronisatie als kritieke afhankelijkheden.

---

## 14. Typische laagoverschrijdende fouten

| Fout | Waarom misleidend? | Betere aanpak |
|---|---|---|
| twee uplinks tekenen en redundantie aannemen | één trunk kan een noodzakelijk VLAN missen | vergelijk VLAN-, trunk- en STP-toestand voor beide paden |
| alleen controleren dat `Po1` bestaat | een member kan ontbreken of de allowed VLAN-lijst kan verschillen | controleer members én logische trunkconfiguratie aan beide kanten |
| een `FULL` OSPF-neighbor als volledige routingtest zien | doelprefix of default route kan nog ontbreken | controleer de specifieke routes en de data plane |
| HSRP op enkele gebruikers-VLAN's configureren | management- of server-VLAN kan single point of failure blijven | maak een gatewaymatrix voor elk gerouteerd VLAN |
| de echte SVI als clientgateway gebruiken | de virtual IP kan dan niet overnemen | controleer client- en DHCP-gatewayconfiguratie |
| preemption gelijkstellen aan uplinktracking | een hogere priority zegt niets over de gezondheid van het verdere pad | track een relevante afhankelijkheid en test upstream failure |
| blocked/discarding als defect interpreteren | STP kan precies correct een loop voorkomen | koppel role en state aan root bridge en topologie |
| alleen de primaire toestand documenteren | verborgen fouten in het back-uppad blijven onzichtbaar | test elk relevant single-failure scenario afzonderlijk |
| alle VLAN's op elke trunk toelaten om fouten te vermijden | vergroot foutdomein en verbergt het bedoelde ontwerp | laat alleen noodzakelijke VLAN's toe en documenteer ze |
| meerdere fouten tegelijk herstellen | je weet niet welke wijziging het resultaat veroorzaakte | wijzig één bewezen oorzaak en hertest gericht |

---

## 15. Controlevragen en denkvragen

### 15.1 Begripscontrole

1. Waarom is een STP alternate/discarding poort niet automatisch een defecte poort?
2. Welke informatie bepaalt welke switch root bridge wordt?
3. Wat is het verschil tussen twee redundante uplinks en één EtherChannel met twee
   members?
4. Waarom vormt `passive` plus `passive` geen LACP-channel?
5. Waarom kan je één gewone Port-channel niet over twee onafhankelijke
   distributionswitches spreiden?
6. Wat is het verschil tussen een OSPF-neighbor, een `O IA`-route en een `O*E2`-
   default route?
7. Waarom blijft een aangesloten subnet geadverteerd wanneer zijn interface passive
   is in OSPF?
8. Welke drie IP-adressen verwacht je bij HSRP op twee gateways voor één VLAN?
9. Wat voegen preemption en tracking elk afzonderlijk toe aan HSRP?
10. Waarom bewijst een succesvolle eind-tot-eindping geen redundantie?

### 15.2 Toepassingsvragen

1. VLAN 50 heeft `MLS-DIST2` als STP-root en HSRP-active, maar VLAN 50 ontbreekt op één
   zijde van de inter-distribution Port-channel. Welke controles voer je uit en welke
   impact verwacht je?
2. `MLS-DIST2` kan zijn core-interface pingen, maar vormt geen OSPF-neighbor. Welke
   parameters vergelijk je eerst aan beide kanten van de link?
3. Een HSRP-groep wisselt correct van active router, maar de server blijft
   onbereikbaar. Toon met de afhankelijkheidsketen waar je verder zoekt.
4. Alle interne subnetten zijn bereikbaar, maar geen enkele client bereikt een extern
   adres. Welke route controleer je op de edge en op een interne router?
5. Een EtherChannel blijft werken na uitval van één member. Waarom moet een
   monitoringplatform dit toch als incident melden?
6. Formuleer voor een access switch met één uplink een professionele conclusie met
   observatie, risico, bedrijfsimpact, maatregel en acceptatietest.

### 15.3 Criteria voor een sterk antwoord

Een sterk antwoord:

- noemt de relevante laag en het mechanisme;
- maakt onderscheid tussen verwacht en werkelijk gedrag;
- verwijst naar concreet bewijs;
- beschrijft de impact op een dienst of bedrijfsproces;
- stelt een gerichte maatregel voor;
- eindigt met een positieve én negatieve of failovertest;
- benoemt waar een labtest geen volledige productiegarantie biedt.

---

## 16. Samenvatting

Belangrijkste inzichten:

- redundantie is een end-to-endeigenschap en geen vinkje bij één protocol;
- STP maakt redundante Layer 2-paden loopvrij;
- de root bridge hoort bewust gekozen te worden, meestal in de distributionlaag;
- Rapid PVST+ voert een snelle spanning-tree-instance per VLAN uit;
- EtherChannel bundelt compatibele fysieke links tot één Port-channel;
- LACP controleert de vorming van de bundel, maar corrigeert geen foutieve
  trunkintentie;
- een gewone EtherChannel vereist aan beide kanten één logische buur;
- OSPF-areas beperken topologiedetail en area 0 vormt de backbone;
- een ABR verbindt area 0 met een andere area en een ASBR brengt externe routes binnen;
- passive interfaces adverteren hun netwerk zonder daar neighbors te zoeken;
- een adjacency bewijst niet dat de specifieke inter-area- of default route aanwezig
  is;
- HSRP laat clients een virtuele default gateway gebruiken;
- priority, preemption en tracking bepalen samen welk toestel active hoort te zijn;
- STP-root en HSRP-active worden per VLAN bij voorkeur op elkaar afgestemd;
- een baseline, één gecontroleerde fout en bewijs voor én na de fout maken failover
  aantoonbaar;
- professioneel advies koppelt observatie aan risico, bedrijfsimpact, maatregel en
  acceptatietest;
- Packet Tracer toont protocolgedrag, maar vervangt geen productieontwerp,
  capaciteitsanalyse of monitoring.

Kernzin:

> Een redundant enterprise-netwerk is pas geloofwaardig wanneer de alternatieve
> paden logisch ontworpen, protocolmatig actief, eind-tot-eind getest en met gericht
> bewijs gedocumenteerd zijn.
