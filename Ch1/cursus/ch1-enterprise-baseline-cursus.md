# Hoofdstuk 1 - Enterprise baseline en design

## 1. Inleiding

In het vorige OPO **Introduction to Networks** heb je geleerd hoe je een basisnetwerk opbouwt en configureert. Je werkte onder andere met switches, routers, VLAN's, trunking, inter-VLAN routing, IP-adressering, DHCP, NAT/PAT, ACL's en eenvoudige troubleshooting.

In dit OPO, **Enterprise Networks**, verschuift de focus. Het is niet meer voldoende dat een netwerk technisch werkt. Je moet ook kunnen beoordelen of een netwerk geschikt is voor een professionele bedrijfsomgeving.

Een netwerk dat vandaag werkt, kan morgen toch problemen veroorzaken wanneer:

- het bedrijf groeit;
- er extra afdelingen of gebouwen bijkomen;
- medewerkers van thuis uit moeten werken;
- interne applicaties extern bereikbaar moeten zijn;
- gasten toegang tot internet nodig hebben;
- securityregels strenger worden;
- beheer en documentatie belangrijker worden;
- storingen sneller opgespoord moeten worden.

In een enterprise omgeving denk je dus niet alleen na over de vraag:

> Krijgen toestellen verbinding met elkaar?

Je denkt ook na over vragen zoals:

- Is het netwerk schaalbaar?
- Is het netwerk veilig genoeg?
- Wat gebeurt er als een toestel of verbinding uitvalt?
- Is het netwerk duidelijk gedocumenteerd?
- Kan een beheerder problemen snel onderzoeken?
- Zijn toegangsrechten logisch en beperkt?
- Kan het ontwerp meegroeien met de organisatie?

Dit hoofdstuk vormt daarom de overgang tussen een **werkend campusnetwerk** en een **professioneel enterprise netwerk**.

**Kernidee:**

> Een enterprise netwerk is niet geslaagd omdat er verkeer doorheen kan. Het is
> geslaagd wanneer het gewenste verkeer voorspelbaar werkt, ongewenst verkeer
> aantoonbaar wordt beperkt en beheerders het ontwerp kunnen begrijpen, wijzigen en
> herstellen.

Doorheen dit hoofdstuk gebruiken we daarom dezelfde redeneerketen:

```text
bedrijfsbehoefte
      |
      v
requirement: wat moet wel en niet kunnen?
      |
      v
ontwerp: zones, VLAN's, subnetten, paden en controles
      |
      v
configuratie: trunks, routing, ACL's, NAT/PAT en management
      |
      v
operationele toestand: wat doet het netwerk nu echt?
      |
      v
test en bewijs: komt het resultaat overeen met de requirement?
```

Elke pijl is belangrijk. Een juiste requirement met een verkeerde configuratie werkt
niet. Een correcte configuratieregel die nergens toegepast is, heeft geen effect. Een
succesvolle test zonder vooraf bepaald verwacht resultaat bewijst niet dat het ontwerp
correct is.

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. uitleggen wat het verschil is tussen een eenvoudig campusnetwerk en een enterprise netwerk;
2. beschrijven waarom schaalbaarheid, betrouwbaarheid, security en beheerbaarheid belangrijk zijn;
3. risico's herkennen in een bestaand netwerkontwerp;
4. het verschil uitleggen tussen een technisch werkend netwerk en een professioneel beheerd netwerk;
5. basisdocumentatie opstellen voor een bedrijfsnetwerk;
6. een bestaand netwerk analyseren aan de hand van VLAN's, IP-subnetten, zones, routing en ACL's;
7. het verschil aantonen tussen configuratie, operationele toestand en testbewijs;
8. positieve en negatieve testen ontwerpen vanuit een securityregelmatrix;
9. risico's formuleren met oorzaak, impact, bewijs en prioriteit;
10. verbeterpunten formuleren die concreet, toetsbaar en beheerbaar zijn;
11. uitleggen welke vereenvoudigingen aanvaardbaar zijn in een lab en wat een
    productieontwerp aanvullend nodig heeft.

---

## 3. Van een werkend netwerk naar een professioneel netwerk

Een netwerk kan technisch correct functioneren en toch slecht ontworpen zijn.

Stel bijvoorbeeld dat een bedrijf een netwerk heeft met:

- een router;
- enkele switches;
- drie VLAN's;
- DHCP voor clients;
- NAT/PAT voor internettoegang;
- een servernetwerk;
- een paar ACL's;
- internettoegang voor alle gebruikers.

Wanneer alle toestellen kunnen pingen, gebruikers op internet geraken en de server bereikbaar is, lijkt het netwerk op het eerste gezicht in orde. Voor een labo-oefening is dat vaak voldoende.

In een echte bedrijfsomgeving is dat niet genoeg.

Een professioneel netwerk moet niet alleen verbinding voorzien, maar ook gecontroleerd, beveiligd, uitbreidbaar en beheerbaar zijn. De configuratie moet niet alleen werken, maar ook logisch te verklaren zijn.

Een netwerkbeheerder moet bijvoorbeeld kunnen antwoorden op vragen zoals:

| Ontwerpvraag | Wat moet het antwoord duidelijk maken? | Risico als het antwoord ontbreekt |
|---|---|---|
| Waarom bestaat dit VLAN? | welke gebruikers, toestellen of dienst het VLAN groepeert | overbodige segmenten en onduidelijke toegangsregels |
| Welke toestellen horen in dit subnet? | hoe adressering aansluit bij functie, zone en groeiverwachting | adresconflicten, moeilijke uitbreiding en trage troubleshooting |
| Wie mag de servers bereiken? | welke functionele verkeersstromen nodig zijn | alle interne gebruikers krijgen impliciet te veel toegang |
| Welke requirement dwingt deze ACL af? | waarom elke belangrijke permit- of deny-regel bestaat | regels worden uit angst niet opgeruimd of onveilig verruimd |
| Wat gebeurt er als deze uplink uitvalt? | de impact en het eventuele alternatieve pad | een verborgen single point of failure legt een afdeling stil |
| Wie kan de managementadressen bereiken? | hoe toegang tot kritieke beheerfuncties beperkt is | gewone clients of gasten kunnen infrastructuur scannen of aanvallen |
| Welke componenten zijn bedrijfskritiek? | waar monitoring, herstelplanning en redundantie prioriteit krijgen | middelen worden willekeurig verdeeld en kritieke afhankelijkheden blijven onzichtbaar |
| Welke test bewijst de securityregel? | bron, doel, dienst, verwacht resultaat en bewijs | een aanwezige ACL wordt ten onrechte als werkende beveiliging beschouwd |

Daarom maken we in Enterprise Networks het onderscheid tussen:

| Technisch werkend netwerk | Professioneel beheerd netwerk |
|---|---|
| Toestellen hebben verbinding | Verbindingen zijn bewust ontworpen |
| VLAN's bestaan omdat ze nodig waren in de oefening | VLAN's passen binnen een logisch zone- en securitymodel |
| ACL's blokkeren of laten verkeer toe | ACL's zijn gedocumenteerd en gekoppeld aan requirements |
| IP-adressen zijn correct geconfigureerd | Het IP-plan is logisch, leesbaar en uitbreidbaar |
| Problemen worden opgelost door te proberen | Troubleshooting gebeurt methodisch en controleerbaar |
| Documentatie is beperkt of ontbreekt | Documentatie is een normaal onderdeel van het beheer |
| Security wordt achteraf toegevoegd | Security zit vanaf het ontwerp in het netwerk |

Het doel van dit hoofdstuk is dus niet om alle basisconfiguratie opnieuw aan te leren. Die kennis wordt verondersteld aanwezig te zijn. We gebruiken die kennis om een bestaand netwerk kritisch te analyseren.

### 3.1 Vijf niveaus van zekerheid

Bij een analyse moet je vijf uitspraken uit elkaar houden.

| Niveau | Voorbeeld | Wat weet je dan? | Wat weet je nog niet? |
|---|---|---|---|
| Requirement | Guests mogen alleen naar internet. | het gewenste gedrag | of het ontwerp dit ondersteunt |
| Ontwerp | Guests zitten in een aparte zone en VLAN. | hoe scheiding bedoeld is | of de configuratie klopt |
| Configuratie | Er bestaat een ACL met deny-regels naar interne subnetten. | dat regels geconfigureerd zijn | of de ACL correct actief is |
| Operationele toestand | De ACL is inbound toegepast en counters lopen op. | dat verkeer de controle passeert | of alle gewenste scenario's correct zijn |
| Testbewijs | Guest bereikt internet, maar niet de server of management-IP's. | dat de geteste requirement nu werkt | of niet-geteste diensten of paden ook correct zijn |

Deze niveaus voorkomen veel verkeerde conclusies.

**Typische fout:**

> `show access-lists` toont een ACL, dus het netwerk is beveiligd.

De output bewijst alleen dat de ACL bestaat. Je moet ook controleren waar en in welke
richting ze toegepast is, welk verkeer ze matcht en of positieve en negatieve testen
het verwachte resultaat geven.

**Kernzin:**

> Configuratie is een intentie; operationele toestand en gerichte testen tonen het
> werkelijke effect.

---

## 4. Wat maakt een netwerk enterprise?

Een enterprise netwerk is niet gewoon een groter netwerk. Het is een netwerk dat ontworpen is om op een gecontroleerde manier mee te groeien met een organisatie.

In een klein netwerk worden veel beslissingen snel en praktisch genomen:

- "We maken snel een extra VLAN."
- "We geven deze server gewoon een vrij IP-adres."
- "We laten tijdelijk verkeer toe, dan werkt de applicatie."
- "We gebruiken dezelfde switch ook voor management."
- "We lossen het later wel op als het probleem terugkomt."

Dat kan in een kleine labo-omgeving werken, maar in een bedrijfscontext zorgt dat vaak voor problemen. In een enterprise netwerk moet je bij elke technische beslissing nadenken over de impact op langere termijn.

Een enterprise netwerk moet vooral goed scoren op vier domeinen:

| Kwaliteitsdomein | Centrale vraag | Mogelijk bewijs |
|---|---|---|
| Schaalbaarheid | Kan het ontwerp groeien zonder grote herbouw? | capaciteitsplan, adresruimte en herhaalbaar aansluitmodel |
| Betrouwbaarheid | Blijft de noodzakelijke dienst beschikbaar bij een fout? | afhankelijkheidsanalyse en gecontroleerde failovertest |
| Security | Is toegang beperkt tot wat functioneel nodig is? | securityregelmatrix, allow-tests en deny-tests |
| Beheerbaarheid | Kan een andere beheerder het netwerk veilig begrijpen en wijzigen? | actuele documentatie, logging, back-up en wijzigingsprocedure |

Deze vier domeinen komen in bijna elke les van dit OPO terug.

---

### 4.1 Schaalbaarheid

**Schaalbaarheid** betekent dat een netwerk kan groeien zonder dat het ontwerp telkens volledig opnieuw moet worden opgebouwd.

Een netwerk is schaalbaar wanneer je relatief eenvoudig extra gebruikers, VLAN's, switches, servers, locaties of diensten kan toevoegen.

Een slecht schaalbare situatie:

> Een bedrijf gebruikt VLAN 10 voor alle medewerkers: administratie, verkoop, IT, directie en tijdelijke medewerkers. Iedereen zit in hetzelfde subnet `192.168.10.0/24`.

Waarom is dit slecht?

- Alle gebruikers zitten in dezelfde broadcast domain.
- Je kan moeilijk verschillende securityregels toepassen per afdeling.
- Je kan tijdelijke medewerkers niet eenvoudig beperken.
- Als het subnet vol raakt, moet je veel adressen en configuraties aanpassen.
- Troubleshooting wordt moeilijker omdat alle gebruikers logisch door elkaar zitten.

Een betere enterprise-aanpak:

- gebruik aparte VLAN's of zones voor verschillende functies;
- voorzie een logisch IP-plan;
- laat ruimte voor groei;
- documenteer welk subnet waarvoor dient;
- koppel VLAN's aan security- en beheerbehoeften.

Bijvoorbeeld:

| Zone | VLAN | Subnet | Doel |
|---|---:|---|---|
| Staff | 20 | `10.10.20.0/24` | gewone medewerkers |
| IT | 30 | `10.10.30.0/24` | IT-beheerders |
| Servers | 40 | `10.10.40.0/24` | interne servers |
| Guests | 50 | `10.10.50.0/24` | bezoekers |
| Management | 99 | `10.10.99.0/24` | beheerinterfaces |

Dit betekent niet dat elk bedrijf exact deze VLAN's nodig heeft. Het belangrijkste is dat het ontwerp logisch, uitbreidbaar en uitlegbaar is.

**Controleer:**

| Controle | Verwacht | Waarom controleer je dit? |
|---|---|---|
| aantal gebruikte en vrije adressen per subnet | voldoende reserve volgens de groeiverwachting | voorkomt een onverwachte hernummering |
| toevoeging van een nieuwe afdeling op papier | past in het VLAN-, subnet- en zoneplan | toont of het ontwerp herhaalbaar is |
| trunk- en routingimpact van een nieuw VLAN | wijziging blijft beperkt en voorspelbaar | voorkomt dat groei overal handwerk veroorzaakt |

Schaalbaarheid betekent dus niet dat je willekeurig zeer grote subnetten maakt. Te grote
broadcast domains en te brede trustzones kunnen security en beheerbaarheid juist
verslechteren.

---

### 4.2 Betrouwbaarheid

**Betrouwbaarheid** betekent dat het netwerk beschikbaar blijft wanneer er iets fout loopt.

In een enterprise omgeving moet je verwachten dat onderdelen kunnen falen:

- een switch kan defect gaan;
- een router kan uitvallen;
- een kabel kan loskomen;
- een uplinkpoort kan kapot gaan;
- een voeding kan defect raken;
- een configuratiefout kan impact hebben op meerdere VLAN's.

Een onbetrouwbare situatie:

> Alle VLAN's gebruiken dezelfde router als default gateway. Die router heeft een enkele verbinding naar de core switch. Als die router of die ene uplink uitvalt, ligt alle inter-VLAN routing en internettoegang stil.

Waarom is dit slecht?

- Een enkel toestel bepaalt de werking van het volledige netwerk.
- Een defecte kabel kan meerdere afdelingen tegelijk treffen.
- Er is geen alternatief pad.
- De impact van een storing is groot.
- De helpdesk krijgt meldingen van iedereen tegelijk, maar de oorzaak zit op een centraal punt.

Dit noemen we een **single point of failure**: een onderdeel waarvan het falen een grote dienst of het volledige netwerk onderbreekt.

Een betere enterprise-aanpak:

- voorzie redundante verbindingen waar dat nodig is;
- gebruik meerdere switches of routers voor kritieke functies;
- denk na over failover;
- documenteer welke componenten kritisch zijn;
- test wat er gebeurt wanneer een verbinding wegvalt;
- zorg dat monitoring een storing snel zichtbaar maakt.

In Packet Tracer zal je niet altijd alle redundantie volledig realistisch nabouwen, maar je moet ze wel kunnen herkennen en bespreken in een ontwerp.

**Controleer:**

| Test | Verwacht | Wat bewijst dit? |
|---|---|---|
| kritieke uplink administratief uitschakelen | verkeer gebruikt een voorzien alternatief pad, als dat ontworpen is | failover van het werkelijke gebruikersverkeer |
| kritisch toestel aanduiden en verwijderen uit het schema | impact is vooraf benoemd | inzicht in afhankelijkheden |
| verbinding herstellen | netwerk keert voorspelbaar terug naar normale toestand | herstelgedrag, niet alleen uitvalgedrag |

**In productie:** een failovertest plan je in een gecontroleerd onderhoudsvenster. Je
definieert vooraf stopcriteria, monitoring, een rollback en wie de dienst valideert. In
Packet Tracer mag de test eenvoudiger zijn, maar ook daar noteer je toestand voor,
tijdens en na de fout.

---

### 4.3 Security

**Security** betekent dat netwerktoegang bewust beperkt wordt volgens het principe van **least privilege**.

Least privilege betekent:

> Een gebruiker, toestel of systeem krijgt alleen de toegang die nodig is, en niets meer.

Een onveilige situatie:

> Het guest VLAN heeft internettoegang, maar kan ook de interne file server en de management-IP's van switches bereiken.

Waarom is dit slecht?

- Een bezoeker of onbekend toestel kan interne systemen scannen.
- Een besmet gasttoestel kan proberen verbinding te maken met servers.
- Managementinterfaces van switches en routers worden blootgesteld aan gebruikers die ze niet nodig hebben.
- Een fout wachtwoordbeleid of oud toestel kan sneller misbruikt worden.
- Het netwerk lijkt te werken, maar de toegangscontrole is veel te breed.

Een betere enterprise-aanpak:

- scheid gasten van interne netwerken;
- laat guests alleen naar internet;
- beperk managementtoegang tot IT-beheerders;
- plaats publieke diensten niet zomaar in het interne servernetwerk;
- gebruik ACL's of firewallregels die vertrekken vanuit duidelijke requirements;
- test zowel toegelaten als verboden verkeer.

Een goede securitytest is dus niet alleen:

> Kan de medewerker de server bereiken?

Maar ook:

> Kan de gast de server niet bereiken?

Verboden verkeer correct blokkeren is even belangrijk als toegelaten verkeer laten werken.

Een securitycontrole bestaat daarom minstens uit een testpaar:

| Testtype | Voorbeeld | Wat toon je aan? |
|---|---|---|
| Positieve test | Staff opent de noodzakelijke interne webdienst. | vereiste toegang blijft bruikbaar |
| Negatieve test | Guest probeert dezelfde interne webdienst te openen. | de trustgrens wordt afgedwongen |

Een ping alleen is niet altijd voldoende. Een server kan ICMP blokkeren en toch een
webdienst aanbieden, of ICMP toelaten terwijl de gevoelige applicatiepoort correct
gefilterd is. Test daarom waar mogelijk de dienst die in de requirement staat.

---

### 4.4 Beheerbaarheid

**Beheerbaarheid** betekent dat een netwerk begrijpelijk, documenteerbaar en onderhoudbaar is.

Een netwerk is slecht beheerbaar wanneer alleen de persoon die het heeft gebouwd nog begrijpt hoe het werkt.

Een slecht beheerbare situatie:

> Een bedrijf heeft meerdere VLAN's en ACL's, maar er is geen VLAN-tabel, geen IP-plan, geen zoneschema en geen overzicht van welke ACL waarvoor dient.

Waarom is dit slecht?

- Nieuwe beheerders verliezen veel tijd met uitzoeken.
- Troubleshooting gebeurt op basis van gokken.
- Een kleine wijziging kan onverwacht verkeer blokkeren.
- Oude testregels blijven actief omdat niemand weet waarvoor ze dienden.
- Het is moeilijk om securitykeuzes te verantwoorden.
- Bij een incident weet niemand snel welke systemen met elkaar mogen communiceren.

Een betere enterprise-aanpak:

- houd een VLAN- en IP-plan bij;
- documenteer zones en toegangsregels;
- geef toestellen en VLAN's duidelijke namen;
- noteer waar routing, NAT en filtering gebeuren;
- maak een testplan;
- bewaar configuraties en wijzigingen op een controleerbare manier.

Beheerbaarheid is geen extraatje dat je pas achteraf doet. In een enterprise netwerk is documentatie een onderdeel van het ontwerp.

**Praktische proef:** geef je documentatie aan een medestudent die het netwerk niet
heeft gebouwd. Kan die persoon de gateway van een VLAN vinden, uitleggen waar een ACL
actief is en een afwijkend testresultaat onderzoeken zonder eerst alle configuraties te
lezen? Zo niet, dan is het netwerk nog onvoldoende overdraagbaar.

---

### 4.5 Samenhang en afwegingen

De vier domeinen versterken elkaar vaak, maar niet elke verbetering is gratis.

| Ontwerpkeuze | Positief effect | Nieuwe kost of aandachtspunt |
|---|---|---|
| extra uplink | hogere beschikbaarheid | STP, EtherChannel of routing moet het extra pad correct beheren |
| fijnere segmentatie | kleinere fout- en trustdomeinen | meer VLAN's, regels en documentatie |
| strikte ACL | kleiner aanvalsoppervlak | foutieve of onvolledige requirements kunnen legitiem verkeer blokkeren |
| centrale netwerkdienst | consistenter beheer | de dienst wordt zelf een kritieke afhankelijkheid |
| uitgebreide logging | betere audit en troubleshooting | opslag, tijdsynchronisatie en opvolging zijn nodig |

Een enterprise-ontwerp zoekt dus geen maximum op één as. Het zoekt een onderbouwd
evenwicht op basis van bedrijfsimpact, risico, kost en complexiteit.

**Voorbeeld:** twee uplinks lijken betrouwbaarder dan één. Zonder correct loopvrij
ontwerp kunnen ze een switching loop veroorzaken en de beschikbaarheid net verlagen.
Hoofdstuk 2 werkt die afweging verder uit met STP, EtherChannel en gateway redundancy.

### 4.6 Praktische samenvatting

Wanneer je een netwerk analyseert, kan je altijd starten met deze vier vragen:

| Vraag | Waar let je concreet op? | Voorbeeld van een risico |
|---|---|---|
| Is het schaalbaar? | VLAN's, subnetten, groeiruimte, logisch IP-plan | alle gebruikers in een subnet |
| Is het betrouwbaar? | redundantie, uplinks, kritieke toestellen | een router als enige gateway voor alles |
| Is het veilig? | zones, ACL's, managementtoegang, guest access | guests kunnen interne servers bereiken |
| Is het beheerbaar? | documentatie, naamgeving, testplan, logging | niemand weet waarvoor een ACL dient |

Deze vragen vormen de basis voor de workshop bij dit hoofdstuk. Je krijgt een bestaand netwerk dat technisch grotendeels werkt, maar waarin meerdere ontwerpkeuzes professioneel beoordeeld moeten worden.

---

## 5. Denken in netwerkzones

In een basisnetwerk denk je vaak vooral in VLAN's en subnetten. In een enterprise netwerk denk je daarnaast ook in **zones**.

Een **zone** is een logisch deel van het netwerk met een bepaald doel en een bepaald vertrouwensniveau.

Voorbeelden van zones zijn:

- gebruikers;
- servers;
- gasten;
- management;
- internet;
- DMZ;
- VPN-gebruikers;
- IoT-toestellen.

Een zone is niet altijd exact hetzelfde als een VLAN. Soms bestaat een zone uit een VLAN, maar soms bestaat een zone uit meerdere VLAN's.

Bijvoorbeeld:

| Zone | Mogelijke VLAN's | Betekenis |
|---|---|---|
| Internal users | VLAN 10 Students, VLAN 20 Staff | gewone gebruikersnetwerken |
| Servers | VLAN 30 Servers | interne servers |
| Guests | VLAN 40 Guests | bezoekers of niet-vertrouwde toestellen |
| Management | VLAN 99 Management | beheerinterfaces van netwerktoestellen |
| Internet | ISP-netwerk | externe, niet-vertrouwde omgeving |

Het verschil is belangrijk:

- een **VLAN** is een technische netwerkindeling op laag 2;
- een **subnet** is een IP-adresbereik op laag 3;
- een **zone** is een ontwerpkeuze op basis van functie, risico en toegangsrechten.

Een VLAN helpt je om verkeer technisch te scheiden. Een zone helpt je om na te denken over wat die scheiding betekent voor security en beheer.

**Kernidee:**

> Een VLAN creëert een technische grens, maar wordt pas een betekenisvolle trustgrens
> wanneer routing en filtering het gewenste zonebeleid afdwingen.

Een zonebeleid heeft minstens vier elementen nodig:

| Element | Vraag | Voorbeeld |
|---|---|---|
| Bron | Wie start het verkeer? | `Guests` |
| Doel | Welke zone of host wordt benaderd? | interne DNS-server |
| Dienst | Welk protocol en welke poort zijn nodig? | UDP/TCP 53 |
| Beslissing | Wat moet de controle doen? | toestaan, blokkeren en eventueel loggen |

Alleen `Guests -> Servers: nee` noteren is een goede eerste ontwerpkeuze, maar soms te
grof voor implementatie. Als gasten een specifieke DNS- of captive-portal-dienst nodig
hebben, moet de uitzondering nauwkeurig beschreven worden.

Een **captive portal** is de webpagina waarop een gast eerst voorwaarden aanvaardt of
zich aanmeldt voordat gewone netwerktoegang beschikbaar wordt.

Conceptueel loopt zonering zo:

```text
bronhost -> access VLAN -> default gateway -> controlepunt -> doelzone
                                            |
                                            +-> ACL of firewallpolicy
```

Het controlepunt moet op het echte verkeerspad liggen. Een ACL op een interface waar
het verkeer nooit passeert, dwingt geen beleid af.

---

### 5.1 Waarom zones belangrijk zijn

Zonder zones wordt netwerktoegang snel onduidelijk.

Een slechte situatie:

> Een bedrijf heeft VLAN's voor Staff, Students, Guests en Servers. Routing tussen alle VLAN's is toegestaan. Er zijn geen duidelijke regels over wie welke servers mag bereiken.

Waarom is dit slecht?

- Het gastennetwerk kan mogelijk interne systemen bereiken.
- Studenten of gewone gebruikers kunnen servers scannen.
- Managementinterfaces kunnen bereikbaar zijn vanuit gewone gebruikersnetwerken.
- Bij een besmet toestel kan malware zich makkelijker door het netwerk bewegen.
- Het is moeilijk om te controleren of toegang correct beperkt is.

Het netwerk werkt technisch, maar het securitymodel is zwak.

Met zones stel je eerst de vraag:

> Welke groepen toestellen vertrouwen we evenveel, en welke groepen moeten van elkaar gescheiden worden?

Daarna bepaal je welke communicatie nodig is.

---

### 5.2 Vertrouwensniveaus

Niet elke zone is even betrouwbaar.

Een laptop van een medewerker is bijvoorbeeld betrouwbaarder dan een onbekend toestel van een bezoeker, maar minder betrouwbaar dan een beheerserver van de IT-afdeling.

Een mogelijke indeling:

| Zone | Vertrouwensniveau | Waarom? |
|---|---|---|
| Internet | Zeer laag | externe omgeving, niet onder controle van het bedrijf |
| Guests | Laag | toestellen van bezoekers zijn onbekend |
| Students of gewone users | Gemiddeld | gekende gebruikers, maar niet noodzakelijk beheerders |
| Staff | Gemiddeld tot hoog | interne medewerkers met toegang tot bedrijfsdiensten |
| Servers | Hoog | bevatten applicaties, data of infrastructuurdiensten |
| Management | Zeer hoog | geeft toegang tot beheer van netwerktoestellen |

Een lager vertrouwde zone mag niet automatisch toegang krijgen tot een hoger vertrouwde zone.

Een praktisch voorbeeld:

| Verkeersstroom | Gewenst? | Waarom? |
|---|---|---|
| Guest naar internet | Ja | bezoekers hebben internet nodig |
| Guest naar interne file server | Nee | bezoekers hebben geen toegang nodig tot bedrijfsdata |
| Student naar webserver voor cursusmateriaal | Ja | dit is een functionele behoefte |
| Student naar switch management-IP | Nee | studenten hoeven netwerktoestellen niet te beheren |
| IT-admin naar management VLAN | Ja | beheerders moeten netwerktoestellen kunnen beheren |
| Internet naar interne database | Nee | een interne database mag niet rechtstreeks publiek bereikbaar zijn |

Door dit expliciet te maken, voorkom je dat "alles naar alles" toegelaten wordt omdat dat tijdens het testen gemakkelijk lijkt.

---

### 5.3 Van zones naar toegangsregels

Zodra je zones hebt bepaald, kan je nadenken over toegangsregels.

Een toegangsregel beschrijft welke communicatie wel of niet toegelaten is.

Bijvoorbeeld:

| Bronzone | Doelzone | Toegang | Reden |
|---|---|---|---|
| Staff | Servers | Toegelaten | medewerkers gebruiken interne applicaties |
| Guests | Internet | Toegelaten | gasten hebben internet nodig |
| Guests | Servers | Geblokkeerd | gasten hebben geen toegang nodig tot interne servers |
| Students | Management | Geblokkeerd | studenten beheren geen netwerktoestellen |
| IT | Management | Toegelaten | IT moet switches en routers beheren |
| Internet | Internal users | Geblokkeerd | externe hosts mogen geen clients bereiken |

Dit soort tabel noemen we een **securityregelmatrix** of **traffic matrix**.

Een securityregelmatrix is belangrijk omdat ze de bedoeling van het ontwerp vastlegt voordat je begint te configureren.

Zonder zo'n matrix gebeurt dit vaak:

1. Iemand test een applicatie.
2. De applicatie werkt niet.
3. Er wordt snel een bredere ACL-regel toegevoegd.
4. De applicatie werkt.
5. Niemand documenteert waarom die regel bestaat.
6. Maanden later weet niemand nog of die toegang veilig of nodig is.

Dat is een typische slechte enterprise-situatie. De configuratie is gegroeid door losse ingrepen in plaats van door een duidelijk ontwerp.

Een bruikbare matrix bevat in productie meestal meer detail dan alleen `ja` of `nee`:

| Bron | Doel | Dienst | Actie | Eigenaar | Bewijs |
|---|---|---|---|---|---|
| Staff | Intranet | HTTPS/443 | allow | applicatie-eigenaar | webpagina opent en logevent is zichtbaar |
| Guests | Internal networks | alle IP | deny | netwerkteam | negatieve tests naar representatieve interne doelen |
| IT | Network management | SSH/22, HTTPS/443 | allow | infrastructuurteam | beheerlogin vanaf IT-host werkt |
| Students | Network management | alle IP | deny | infrastructuurteam | ping en beheerverbinding falen zoals verwacht |

De kolom **eigenaar** beantwoordt wie de functionele noodzaak kan bevestigen. De kolom
**bewijs** voorkomt dat een regel alleen op papier bestaat.

---

### 5.4 Voorbeeld: guest VLAN

Een guest VLAN lijkt eenvoudig: bezoekers moeten op internet kunnen.

Maar in een enterprise netwerk moet je meer vragen stellen:

- Krijgen gasten alleen internettoegang?
- Mogen gasten DNS gebruiken van interne servers?
- Mogen gasten printers bereiken?
- Kunnen gasten interne IP-adressen pingen?
- Kunnen gasten de loginpagina van switches of routers openen?
- Wordt guest traffic gelogd of gemonitord?

Een slechte situatie:

> Het guest VLAN gebruikt dezelfde router als alle interne VLAN's. Er is geen ACL actief op de guest-interface. Gasten kunnen naar internet, maar ook naar het servernetwerk en managementnetwerk.

Waarom is dit slecht?

- Een gasttoestel is niet beheerd door de organisatie.
- Je weet niet of het toestel malware bevat.
- Een bezoeker kan interne systemen ontdekken via scans.
- Een fout geconfigureerde server kan onbedoeld bereikbaar zijn.
- De organisatie heeft weinig controle over wat gasten intern proberen te bereiken.

Een betere aanpak:

- laat guests alleen naar internet;
- blokkeer verkeer naar interne private subnetten;
- blokkeer verkeer naar managementadressen;
- documenteer de guest-regels;
- test expliciet dat interne toegang niet werkt.

Een voorbeeld van gewenste testresultaten:

| Test | Verwacht resultaat | Waarom test je dit? |
|---|---|---|
| Guest-pc naar een externe testhost | werkt | basisinternetpad en eventuele NAT/PAT werken |
| Guest-pc naar interne webserver op de relevante dienst | werkt niet, tenzij expliciet nodig | interne serverzone is afgeschermd |
| Guest-pc naar switch management-IP | werkt niet | managementzone is niet bereikbaar |
| Guest-pc naar default gateway | werkt | de lokale laag 3-aansluiting functioneert |
| Guest-pc naar andere guest | afhankelijk van beleid | client isolation is een aparte ontwerpkeuze |

**Typische fout:** een publiek IP-adres zoals `8.8.8.8` in Packet Tracer behandelen alsof
het echte internet beschikbaar is. Gebruik het doel dat in de labtopologie als externe
host is voorzien en noteer die labvereenvoudiging in je testplan.

Let op: in sommige omgevingen wil je zelfs vermijden dat gasten elkaar kunnen bereiken. Dat heet vaak **client isolation**. Dat is nuttig op wifi-netwerken voor bezoekers.

---

### 5.5 Voorbeeld: managementzone

De managementzone is een van de meest gevoelige zones in het netwerk.

In de managementzone vind je bijvoorbeeld:

- management-IP's van switches;
- management-IP's van routers;
- beheerinterfaces van firewalls;
- controllers;
- monitoringservers;
- loggingservers;
- jump hosts of beheerservers.

Een slechte situatie:

> De switches hebben een management-IP in VLAN 99, maar VLAN 99 is bereikbaar vanuit alle andere VLAN's.

Waarom is dit slecht?

- Elke gebruiker kan proberen in te loggen op netwerktoestellen.
- Een aanvaller kan managementinterfaces scannen.
- Zwakke wachtwoorden of oude firmware worden gevaarlijker.
- Een gewone client-pc krijgt technisch een pad naar kritieke infrastructuur.
- Het onderscheid tussen gebruikersverkeer en beheerverkeer is onvoldoende.

Een betere aanpak:

- beperk managementtoegang tot IT-beheerders of een beheerserver;
- gebruik sterke authenticatie;
- gebruik SSH in plaats van Telnet;
- documenteer managementadressen;
- monitor mislukte loginpogingen;
- blokkeer managementtoegang vanuit gewone gebruikers- en guestnetwerken.

Voor dit hoofdstuk moet je nog niet alle beveiligingstechnieken kunnen configureren. Je moet vooral kunnen herkennen dat brede toegang tot managementinterfaces een ernstig ontwerp- en securityprobleem is.

Er bestaan twee grote modellen voor managementverkeer:

| Model | Betekenis | Aandachtspunt |
|---|---|---|
| In-band management | beheer loopt over dezelfde netwerkinfrastructuur als gebruikersverkeer | eenvoudig in een lab, maar filtering en beschikbaarheid verdienen extra aandacht |
| Out-of-band management | een apart beheerpad blijft los van het gewone datapad | sterker voor herstel en incidenten, maar vraagt extra infrastructuur |

De workshop gebruikt in-band management via een management-VLAN. Dat is een bewuste
labkeuze. In productie onderzoek je daarnaast minstens multi-factor authentication
(MFA), centraal beheer van authenticatie, autorisatie en accounting (AAA), centraal
logbeheer, veilige protocollen, bronbeperking, een jump host en eventueel een
out-of-band netwerk. Een **jump host** is een extra beveiligde beheerserver die als
gecontroleerd tussenstation naar infrastructuur dient.

**Controleer:**

| Test | Verwacht | Betekenis |
|---|---|---|
| IT-host naar management-IP via SSH of beschikbare beheerdienst | werkt | geautoriseerd beheerpad bestaat |
| gewone user naar hetzelfde management-IP | werkt niet | gebruikerszone heeft geen beheerpad |
| guest naar hetzelfde management-IP | werkt niet | laag vertrouwde zone is afgescheiden |
| mislukte beheerlogin | wordt waar mogelijk gelogd | poging is achteraf onderzoekbaar |

---

### 5.6 Zones als basis voor latere hoofdstukken

Het denken in zones komt later in het OPO opnieuw terug.

Bijvoorbeeld:

| Later thema | Link met zones |
|---|---|
| Security architecture | zones bepalen welke beveiligingsregels nodig zijn |
| High availability | kritieke zones vragen meer redundantie |
| VPN | VPN-gebruikers komen in een aparte toegangszone |
| Reverse proxy | publieke webtoegang wordt gescheiden van interne applicaties |
| Authentik | identiteit bepaalt welke gebruiker tot welke dienst mag |
| Monitoring en logging | kritieke zones moeten beter opgevolgd worden |
| NetBox | zones, VLAN's, IP-ranges en toestellen worden gedocumenteerd |

Zones zijn dus geen extra theorie naast VLAN's. Ze zijn een manier om technische netwerkkennis te koppelen aan bedrijfsvereisten.

---

## 6. Basisdocumentatie van een enterprise netwerk

In een professioneel netwerk is documentatie geen bijzaak. Documentatie is nodig om het netwerk te begrijpen, te beheren, te beveiligen en te troubleshooten.

Een netwerk zonder documentatie kan technisch werken, maar is kwetsbaar in de praktijk.

Een slechte situatie:

> Een bedrijf heeft een werkend netwerk, maar niemand heeft genoteerd welke VLAN's bestaan, welke subnetten gebruikt worden, waar ACL's actief zijn en welke switchpoorten naar kritieke toestellen gaan.

Waarom is dit slecht?

- Bij een storing moet de beheerder eerst uitzoeken hoe het netwerk in elkaar zit.
- Nieuwe collega's kunnen het netwerk niet veilig overnemen.
- Oude configuraties blijven staan omdat niemand weet of ze nog nodig zijn.
- Wijzigingen worden riskant omdat de impact onduidelijk is.
- Securityregels kunnen niet goed gecontroleerd worden.
- Een incidentonderzoek duurt langer omdat belangrijke informatie ontbreekt.

Documentatie moet daarom antwoord geven op praktische vragen:

- Welke toestellen zijn er?
- Hoe zijn ze verbonden?
- Welke VLAN's bestaan er?
- Welke IP-subnetten worden gebruikt?
- Waar gebeurt routing?
- Waar worden ACL's of firewallregels toegepast?
- Welke zones bestaan er?
- Welke verkeersstromen zijn toegelaten?
- Welke onderdelen zijn kritisch?
- Hoe testen we of het netwerk correct werkt?

Voor dit hoofdstuk gebruiken we een beperkte maar bruikbare set basisdocumentatie.

Goede documentatie beschrijft niet alleen de gewenste situatie. Ze maakt een duidelijk
onderscheid tussen:

| Informatie | Betekenis | Voorbeeld |
|---|---|---|
| Desired state | hoe het netwerk volgens het goedgekeurde ontwerp hoort te zijn | Guests mogen alleen naar internet. |
| Current state | wat configuratie, toestand en tests nu aantonen | Guest bereikt ook de serverzone. |
| Gap | verschil tussen gewenst en werkelijk | de guest-policy wordt niet of onvolledig afgedwongen |
| Actie | concrete wijziging die de gap verkleint | pas filtering toe op het echte routed pad |
| Validatie | test waarmee de wijziging aanvaard wordt | internet werkt; server- en managementtoegang falen |

Zonder dit onderscheid kan documentatie een vals gevoel van zekerheid geven. Een mooie
tekening toont wat iemand ooit bedoelde, niet noodzakelijk wat het netwerk vandaag doet.

---

### 6.1 Topologietekening

Een **topologietekening** toont hoe het netwerk is opgebouwd.

Er zijn twee soorten topologie die vaak door elkaar gehaald worden:

| Type | Wat toon je? | Voorbeeld |
|---|---|---|
| Fysieke topologie | kabels, switches, routers, fysieke verbindingen | Switch 1 is verbonden met Router 1 via poort G0/1 |
| Logische topologie | VLAN's, subnetten, zones, routing | VLAN 20 gebruikt subnet `10.10.20.0/24` en gateway `10.10.20.1` |

Beide zijn nuttig.

Een fysieke topologie helpt bij vragen zoals:

- Welke kabel kan defect zijn?
- Welke switch hangt achter welke uplink?
- Welk toestel vormt een single point of failure?
- Welke poort moet ik controleren?

Een logische topologie helpt bij vragen zoals:

- Welke VLAN's bestaan er?
- Waar gebeurt inter-VLAN routing?
- Welke zones zijn gescheiden?
- Welke subnetten kunnen met elkaar communiceren?

Een slechte situatie:

> Een student tekent alleen drie pc's, een switch en een router, maar noteert geen VLAN's, poorten, gateways of subnetten.

Waarom is dit onvoldoende?

- Je ziet niet welke pc in welk VLAN zit.
- Je ziet niet waar routing gebeurt.
- Je kan niet afleiden welke verkeersstromen logisch mogelijk zijn.
- Je kan de tekening moeilijk gebruiken bij troubleshooting.

Een betere topologietekening bevat minstens:

- namen van netwerktoestellen;
- belangrijke verbindingen;
- poortnamen bij uplinks;
- VLAN's;
- subnetten;
- default gateways;
- serverlocaties;
- internet- of ISP-verbinding;
- eventueel zones of kleurcodes.

De tekening moet niet grafisch perfect zijn. Ze moet vooral bruikbaar zijn.

---

### 6.2 VLAN-tabel

Een **VLAN-tabel** geeft een overzicht van alle VLAN's in het netwerk.

Voorbeeld:

| VLAN | Naam | Doel | Zone |
|---:|---|---|---|
| 10 | Students | studententoestellen | Internal users |
| 20 | Staff | medewerkers | Internal users |
| 30 | Servers | interne servers | Servers |
| 40 | Guests | bezoekers | Guests |
| 99 | Management | beheerinterfaces | Management |

Waarom is dit belangrijk?

- Je ziet snel welke VLAN's bestaan.
- Je ziet of VLAN-namen logisch zijn.
- Je kan controleren of elk VLAN een duidelijk doel heeft.
- Je merkt sneller overbodige of onduidelijke VLAN's op.
- Je kan VLAN's koppelen aan zones en securityregels.

Een slechte situatie:

> In de configuratie staan VLAN 10, VLAN 20, VLAN 30 en VLAN 77, maar VLAN 77 heeft geen naam en niemand weet waarvoor het dient.

Waarom is dit slecht?

- Het kan een oud test-VLAN zijn dat nooit verwijderd werd.
- Het kan nog actief verkeer bevatten.
- Het kan per ongeluk op trunks toegestaan zijn.
- Beheerders durven het niet te verwijderen omdat de impact onbekend is.

Een enterprise-aanpak is eenvoudig: elk VLAN heeft een naam, een doel en een eigenaar of verantwoordelijke context.

---

### 6.3 IP-adresplan

Een **IP-adresplan** toont welke subnetten gebruikt worden en waarvoor ze dienen.

Voorbeeld:

| VLAN | Subnet | Gateway | DHCP-range | Opmerking |
|---:|---|---|---|---|
| 10 | `10.10.10.0/24` | `10.10.10.1` | `10.10.10.50-10.10.10.200` | students |
| 20 | `10.10.20.0/24` | `10.10.20.1` | `10.10.20.50-10.10.20.200` | staff |
| 30 | `10.10.30.0/24` | `10.10.30.1` | geen of beperkt | servers |
| 40 | `10.10.40.0/24` | `10.10.40.1` | `10.10.40.50-10.10.40.200` | guests |
| 99 | `10.10.99.0/24` | `10.10.99.1` | geen | management |

Waarom is dit belangrijk?

- Je ziet welke subnetten bij welke VLAN's horen.
- Je vermijdt overlap tussen subnetten.
- Je weet welke adressen vast zijn en welke via DHCP komen.
- Je kan sneller controleren of een toestel in het juiste netwerk zit.
- Je kan het netwerk later uitbreiden zonder willekeurige adressen te kiezen.

Een slechte situatie:

> Servers krijgen willekeurige IP-adressen uit dezelfde DHCP-range als clients.

Waarom is dit slecht?

- Een serveradres kan wijzigen.
- DNS-records kunnen fout verwijzen.
- ACL's naar servers worden moeilijker.
- Troubleshooting wordt verwarrend.
- Een client kan per ongeluk een adres krijgen dat voor een server bedoeld was.

Een betere aanpak:

- gebruik vaste IP-adressen of gereserveerde adressen voor servers;
- documenteer die adressen;
- houd DHCP-ranges gescheiden van vaste adressen;
- gebruik logische subnetten per functie of zone.

---

### 6.4 Zoneschema

Een **zoneschema** beschrijft welke netwerkzones bestaan en welke VLAN's of subnetten daarbij horen.

Voorbeeld:

| Zone | VLAN's | Vertrouwensniveau | Voorbeelden |
|---|---|---|---|
| Internal users | VLAN 10, VLAN 20 | gemiddeld | studenten, medewerkers |
| Servers | VLAN 30 | hoog | file server, webserver, database |
| Guests | VLAN 40 | laag | bezoekers |
| Management | VLAN 99 | zeer hoog | switch- en routerbeheer |
| Internet | ISP | zeer laag | externe netwerken |

Waarom is dit belangrijk?

- Je ziet welke delen van het netwerk dezelfde functie hebben.
- Je kan securityregels formuleren per zone.
- Je vermijdt dat VLAN's alleen technisch bestaan zonder securitybetekenis.
- Je kan risico's beter inschatten.

Een slechte situatie:

> Het servernetwerk en het managementnetwerk worden allebei beschouwd als "intern", waardoor gewone gebruikers beide kunnen bereiken.

Waarom is dit slecht?

- Niet alle interne netwerken zijn even gevoelig.
- Managementtoegang is kritischer dan toegang tot een gewone applicatieserver.
- Een gebruiker die een webapplicatie nodig heeft, hoeft geen switchbeheer te kunnen bereiken.
- Bij een besmet clienttoestel is de impact groter.

Een enterprise netwerk behandelt interne zones dus niet automatisch als volledig vertrouwd.

---

### 6.5 Routingoverzicht

Een **routingoverzicht** beschrijft waar verkeer tussen netwerken wordt doorgestuurd.

Voor dit hoofdstuk volstaat een eenvoudig overzicht:

| Onderdeel | Vraag |
|---|---|
| Default gateways | Waar staat de gateway per VLAN? |
| Inter-VLAN routing | Gebeurt routing op een router, multilayer switch of firewall? |
| Internetroute | Waar staat de default route naar internet? |
| NAT/PAT | Waar wordt private adressering vertaald naar een publiek adres? |
| Redundantie | Is er maar een routingpad of bestaat er een alternatief? |

Waarom is dit belangrijk?

- Je weet waar je moet zoeken bij connectiviteitsproblemen.
- Je ziet welke toestellen kritisch zijn.
- Je begrijpt welke routes verkeer kan nemen.
- Je kan inschatten wat er gebeurt als een router of uplink faalt.

Een slechte situatie:

> Niemand weet of inter-VLAN routing gebeurt op de router, de core switch of de firewall.

Waarom is dit slecht?

- Troubleshooting start op de verkeerde plaats.
- ACL's worden mogelijk op het verkeerde toestel gezocht.
- Een wijziging aan de verkeerde interface heeft geen effect.
- De oorzaak van een storing wordt trager gevonden.

Een routingoverzicht hoeft in het begin niet complex te zijn. Het moet vooral duidelijk maken waar beslissingen over verkeer genomen worden.

---

### 6.6 Securityregelmatrix

Een **securityregelmatrix** beschrijft welke zones met elkaar mogen communiceren.

Voorbeeld:

| Bron | Doel | Toegang | Reden |
|---|---|---|---|
| Staff | Servers | Ja | toegang tot interne applicaties |
| Students | Servers | Beperkt | alleen cursusplatform of webdienst |
| Guests | Internet | Ja | internettoegang voor bezoekers |
| Guests | Servers | Nee | geen toegang tot interne systemen |
| Users | Management | Nee | geen beheerrechten |
| IT | Management | Ja | beheer van netwerktoestellen |
| Internet | Internal users | Nee | geen inkomende toegang naar clients |

Waarom is dit belangrijk?

- Je legt vast wat de bedoeling is voordat je ACL's configureert.
- Je kan testen of securityregels correct werken.
- Je kan discussies voeren op basis van requirements in plaats van losse commando's.
- Je ziet meteen waar toegang te breed of te beperkt is.

Een slechte situatie:

> Er staat een ACL op de router, maar niemand weet of die ACL bedoeld is om guests te blokkeren, servers te beschermen of internettoegang toe te laten.

Waarom is dit slecht?

- Beheerders durven de ACL niet aan te passen.
- Een fout in de ACL kan maanden onopgemerkt blijven.
- Testen wordt moeilijk omdat het verwachte gedrag onduidelijk is.
- Security wordt afhankelijk van toevallige configuratie.

Een securityregelmatrix maakt van security een ontwerpbeslissing in plaats van een verzameling losse regels.

---

### 6.7 Testplan

Een **testplan** beschrijft welke testen je uitvoert om te controleren of het netwerk correct werkt.

Een goed testplan test niet alleen wat moet werken, maar ook wat niet mag werken.

Voorbeeld:

| Test | Verwacht resultaat | Waarom? |
|---|---|---|
| Staff-pc naar interne server | werkt | medewerkers hebben servertoegang nodig |
| Guest-pc naar internet | werkt | gasten krijgen internettoegang |
| Guest-pc naar interne server | werkt niet | interne systemen moeten afgeschermd zijn |
| Student-pc naar switch management-IP | werkt niet | studenten mogen netwerktoestellen niet beheren |
| IT-pc naar switch management-IP | werkt | IT moet beheer kunnen uitvoeren |
| Externe host naar interne client | werkt niet | clients mogen niet rechtstreeks van buitenaf bereikbaar zijn |

Waarom is dit belangrijk?

- Je bewijst dat requirements gehaald worden.
- Je ontdekt te brede toegang.
- Je vermijdt dat ping de enige test wordt.
- Je kan resultaten vergelijken voor en na een wijziging.
- Je maakt troubleshooting minder afhankelijk van gokken.

Een slechte situatie:

> Studenten testen alleen of elke pc naar internet kan pingen en besluiten dat het netwerk correct is.

Waarom is dit onvoldoende?

- Internettoegang zegt niets over interne security.
- Je weet niet of guests te veel toegang hebben.
- Je weet niet of managementinterfaces beschermd zijn.
- Je test geen verboden verkeersstromen.

In Enterprise Networks is een test pas sterk wanneer hij het ontwerp controleert.

---

### 6.8 Risico- en verbeterpuntenlijst

Een **risico- en verbeterpuntenlijst** toont welke zwakke punten je hebt gevonden en wat je eraan zou doen.

Voorbeeld:

| Risico | Impact | Mogelijke verbetering |
|---|---|---|
| Guest VLAN kan servers bereiken | hoog | blokkeer guest-toegang naar interne subnetten |
| Management VLAN bereikbaar vanuit alle VLAN's | hoog | beperk toegang tot IT-zone |
| Geen redundante uplinks | middel tot hoog | voorzie alternatief pad |
| Geen VLAN-documentatie | middel | maak VLAN-tabel en zoneschema |
| ACL's zijn niet gedocumenteerd | middel | koppel ACL's aan securityregelmatrix |

Waarom is dit belangrijk?

- Je toont dat je verder kijkt dan "het werkt".
- Je kan prioriteiten bepalen.
- Je kan verbeteringen uitleggen aan niet-technische stakeholders.
- Je maakt duidelijk welke risico's bewust blijven bestaan.

Een slechte situatie:

> Een analyse eindigt met "alles werkt" terwijl guests de servers kunnen bereiken en alle switches beheerbaar zijn vanuit elk VLAN.

Waarom is dit slecht?

- Technische connectiviteit wordt verward met een goed ontwerp.
- Securityproblemen blijven onzichtbaar.
- De organisatie krijgt een vals gevoel van veiligheid.
- Latere incidenten hadden vermeden kunnen worden door een betere analyse.

Een goede risicoanalyse benoemt dus niet alleen fouten, maar ook de mogelijke impact.

---

### 6.9 Minimale documentatieset voor dit hoofdstuk

Voor de workshop bij dit hoofdstuk moet je minstens deze documenten of tabellen kunnen
opleveren:

| Artefact | Welke vraag beantwoordt het? | Wanneer is het bruikbaar? |
|---|---|---|
| topologietekening | welke toestellen en verbindingen vormen het netwerk? | poorten, uplinks en kritieke afhankelijkheden zijn zichtbaar |
| VLAN-tabel | welke laag 2-segmenten bestaan en waarvoor dienen ze? | elk VLAN heeft naam, functie en relevante poorten |
| IP-adresplan | welke subnetten, gateways en adresrollen worden gebruikt? | DHCP en vaste adressen zijn onderscheidbaar en overlap is uitgesloten |
| zoneschema | welke functies en vertrouwensniveaus worden gescheiden? | VLAN's en subnetten zijn aan duidelijke zones gekoppeld |
| routingoverzicht | waar wordt over het volgende pad beslist? | gateways, default route, NAT/PAT en kritieke routingpunten zijn bekend |
| securityregelmatrix | welk verkeer moet wel en niet kunnen? | bron, doel, gewenste actie en reden zijn expliciet |
| testplan | hoe bewijs je de requirements? | positieve en negatieve tests hebben een verwacht resultaat |
| risico- en verbeterpuntenlijst | welke gaps bestaan en wat krijgt prioriteit? | oorzaak, impact, bewijs en toetsbare verbetering zijn opgenomen |

Dit hoeft nog geen perfect professioneel document te zijn. Het doel is dat iemand anders je analyse kan lezen en begrijpt:

- hoe het netwerk is opgebouwd;
- welke onderdelen goed ontworpen zijn;
- welke onderdelen risico's vormen;
- welke testen je hebt uitgevoerd;
- welke verbeteringen je voorstelt.

Vanaf dit hoofdstuk is documentatie dus een deel van de technische opdracht. Een configuratie zonder uitleg is in een enterprise context onvoldoende.

---

### 6.10 Documentatie heeft een lifecycle

Documentatie veroudert zodra het netwerk verandert en de beschrijving niet mee wordt
aangepast. Daarom hoort bij elk belangrijk document minimaal context.

| Metadata | Waarom nodig? |
|---|---|
| titel en scope | maakt duidelijk welk netwerkdeel beschreven wordt |
| datum of versie | laat zien hoe actueel de informatie is |
| auteur of eigenaar | bepaalt wie vragen kan beantwoorden en wijzigingen opvolgt |
| bron van de informatie | onderscheidt observatie, configuratie-output en aanname |
| laatste validatie | toont wanneer de beschrijving voor het laatst met de werkelijkheid vergeleken is |
| openstaande afwijkingen | voorkomt dat gekende gaps als correcte toestand gelezen worden |

**Voorbeeld:** een IP-plan met `VLAN 40 = Guests` is onvoldoende als niet duidelijk is
of dit uit het ontwerpdocument komt of effectief met `show vlan brief`, clientconfiguratie
en routingoutput gevalideerd werd.

In een productieomgeving bewaar je netwerkdocumentatie bij voorkeur als een beheerde
bron van waarheid met toegangsbeheer, versiehistoriek en een wijzigingsproces. In de
workshop volstaat één helder analyseverslag, maar dezelfde principes blijven gelden:
noteer wat je observeerde, wanneer je het observeerde en welk bewijs je gebruikte.

---

### 6.11 Bewijs verzamelen zonder ruis

Een volledige `show running-config` kopiëren is zelden een goed analyseverslag. Bewijs
moet relevant, herhaalbaar en veilig zijn.

| Eigenschap | Goede aanpak | Zwakke aanpak |
|---|---|---|
| Relevant | toon de interface waarop de ACL actief is | plak de volledige configuratie zonder markering |
| Herhaalbaar | noteer toestel, commando, bronhost en testdoel | schrijf alleen `ping werkte` |
| Gedateerd | noteer wanneer de toestand gecontroleerd is | gebruik oude screenshots zonder context |
| Verklaard | koppel output aan een korte conclusie | laat de lezer zelf raden wat belangrijk is |
| Veilig | maskeer secrets zoals wachtwoorden en sleutels | plaats credentials in het verslag |

Een nuttige bewijsnotitie kan er zo uitzien:

```text
Vraag: Is management alleen bereikbaar vanuit IT?
Bron: IT-PC, 10.10.30.10
Doel: SW-ACCESS-1, 10.10.99.11
Test: SSH naar TCP/22
Verwacht: allow
Werkelijk: verbinding opent
Aanvullend bewijs: ACL MGMT-IN is actief op het routed pad
Conclusie: positieve test slaagt; voer ook deny-tests uit vanuit Users en Guests
```

**Kernzin:**

> Documentatie is pas operationeel waardevol wanneer een andere beheerder er een
> beslissing mee kan nemen of een test mee kan herhalen.

---

## 7. Praktische analysemethode

Wanneer je een bestaand netwerk krijgt, is het verleidelijk om meteen commando's uit te voeren en willekeurig te testen.

Bijvoorbeeld:

- je pingt enkele toestellen;
- je opent `show running-config`;
- je zoekt ergens naar VLAN's;
- je past misschien al iets aan;
- je probeert opnieuw te pingen.

Dat lijkt actief, maar het is geen goede analysemethode. Je loopt dan het risico dat je belangrijke ontwerpvragen overslaat.

In een enterprise context analyseer je een netwerk methodisch. Dat betekent dat je stap voor stap onderzoekt:

1. wat er aanwezig is;
2. hoe het netwerk bedoeld lijkt te zijn;
3. wat technisch werkt;
4. wat securitymatig correct of fout is;
5. welke risico's bestaan;
6. welke verbeteringen nodig zijn.

Voor de workshop gebruiken we de volgende analysemethode.

Tijdens elke stap gebruik je dezelfde kleine onderzoekscyclus:

```text
vraag -> verwachting -> observatie -> vergelijking -> conclusie -> volgende vraag
```

| Onderdeel | Voorbeeld |
|---|---|
| Vraag | Kan een guest de interne server bereiken? |
| Verwachting | Nee, want Guests is een laag vertrouwde zone. |
| Observatie | Een HTTP-verbinding naar de server opent. |
| Vergelijking | Werkelijk gedrag wijkt af van het zonebeleid. |
| Conclusie | De trustgrens wordt voor deze dienst niet afgedwongen. |
| Volgende vraag | Ontbreekt filtering, staat ze verkeerd of is er een ander pad? |

Dit is methodisch troubleshooting: je verandert niet willekeurig iets, maar gebruikt
elke observatie om de volgende hypothese scherper te maken.

---

### 7.1 Stap 1: verken de topologie

Begin met kijken, niet met aanpassen.

Je probeert eerst te begrijpen welke toestellen en verbindingen aanwezig zijn.

Vragen die je beantwoordt:

- Welke routers zijn er?
- Welke switches zijn er?
- Welke clients en servers zijn er?
- Waar zit de internetverbinding?
- Welke toestellen lijken centraal te staan?
- Zijn er redundante verbindingen of is alles enkelvoudig aangesloten?
- Welke verbindingen lijken uplinks tussen switches of routers?

Waarom is dit belangrijk?

Als je niet weet hoe het netwerk fysiek is opgebouwd, weet je ook niet waar een storing of risico impact heeft.

Een slechte situatie:

> Een student merkt dat een server niet bereikbaar is en begint ACL's te controleren, terwijl de server eigenlijk achter een switch hangt waarvan de enige uplink down is.

Waarom is dit slecht?

- De troubleshooting start op de verkeerde plaats.
- Er wordt tijd verloren aan configuratie die niet de oorzaak is.
- De fysieke afhankelijkheid van de server werd niet eerst bekeken.

Wat noteer je?

- toestelnamen;
- belangrijke verbindingen;
- uplinks;
- mogelijke single points of failure;
- toestellen die kritisch lijken.

Op het einde van deze stap moet je een eerste ruwe topologietekening kunnen maken.

---

### 7.2 Stap 2: breng VLAN's en subnetten in kaart

Daarna onderzoek je welke VLAN's en IP-netwerken bestaan.

Vragen die je beantwoordt:

- Welke VLAN's bestaan er?
- Welke namen hebben de VLAN's?
- Welke poorten horen bij welk VLAN?
- Welke trunks bestaan er tussen switches?
- Welke subnetten horen bij welke VLAN's?
- Welke default gateway gebruikt elk VLAN?
- Welke adressen zijn statisch en welke komen via DHCP?

Waarom is dit belangrijk?

VLAN's en subnetten vormen de basis van de logische netwerkindeling. Als je die niet correct begrijpt, kan je ook geen goede uitspraak doen over zones, security of schaalbaarheid.

Een slechte situatie:

> VLAN 40 heet `Guests`, maar enkele vaste pc's van medewerkers zitten ook in VLAN 40 omdat er toevallig vrije switchpoorten waren.

Waarom is dit slecht?

- De naam van het VLAN komt niet overeen met het echte gebruik.
- Securityregels voor guests kunnen per ongeluk medewerkers treffen.
- Medewerkers kunnen in een minder vertrouwde zone terechtkomen.
- Troubleshooting wordt verwarrend.

Wat noteer je?

- VLAN-ID;
- VLAN-naam;
- subnet;
- gateway;
- functie;
- gekoppelde zone;
- opvallende afwijkingen.

Op het einde van deze stap moet je een VLAN-tabel en IP-adresplan kunnen invullen.

---

### 7.3 Stap 3: bepaal waar routing en NAT gebeuren

Wanneer VLAN's en subnetten duidelijk zijn, onderzoek je hoe verkeer tussen netwerken loopt.

Vragen die je beantwoordt:

- Waar gebeurt inter-VLAN routing?
- Staat de default gateway op een router, multilayer switch of firewall?
- Welke routes bestaan er?
- Waar staat de default route naar internet?
- Waar gebeurt NAT/PAT?
- Welke interfaces zijn inside en outside?

**NAT**, of **Network Address Translation**, vertaalt IP-adressen. In veel campusnetwerken wordt NAT/PAT gebruikt om private IP-adressen naar een publiek adres te vertalen voor internettoegang.

Waarom is dit belangrijk?

Als je weet waar routing en NAT gebeuren, weet je waar beslissingen genomen worden over verkeer. Dat is essentieel voor troubleshooting en securityanalyse.

Een slechte situatie:

> Een gebruiker geraakt niet op internet. Een student controleert alleen de client en de switch, maar vergeet dat NAT op de edge-router fout geconfigureerd kan zijn.

Waarom is dit slecht?

- Internettoegang hangt niet alleen af van VLAN en gateway.
- Zonder NAT/PAT kan intern verkeer mogelijk wel de router bereiken, maar niet correct naar buiten vertaald worden.
- De oorzaak zit op een ander netwerklaag dan waar getest wordt.

Wat noteer je?

- routingtoestel per VLAN;
- default route;
- NAT/PAT-locatie;
- kritieke interfaces;
- mogelijke single points of failure.

Op het einde van deze stap moet je kunnen uitleggen welk pad verkeer neemt van een client naar een server en van een client naar internet.

---

### 7.4 Stap 4: onderzoek zones en toegangsregels

Nu kijk je niet alleen naar connectiviteit, maar naar toegangsrechten.

Vragen die je beantwoordt:

- Welke zones bestaan er?
- Welke VLAN's horen bij welke zone?
- Welke zones zijn hoog of laag vertrouwd?
- Welke zones mogen met elkaar communiceren?
- Welke ACL's of firewallregels zijn actief?
- Zijn er zones die te veel toegang hebben?
- Zijn managementinterfaces voldoende afgeschermd?

Waarom is dit belangrijk?

Een netwerk kan perfect pingen en toch onveilig zijn. Securityanalyse betekent dat je ook controleert of bepaald verkeer niet mogelijk is.

Een slechte situatie:

> De test "guest naar internet" werkt. De student besluit dat het guest VLAN correct is. Er wordt niet getest of guest ook naar interne servers kan.

Waarom is dit slecht?

- Alleen toegelaten verkeer werd getest.
- Verboden verkeer werd niet gecontroleerd.
- Een ernstig securityprobleem kan onopgemerkt blijven.

Wat noteer je?

- zones;
- toegelaten verkeersstromen;
- verboden verkeersstromen;
- actieve ACL's;
- ontbrekende of te brede regels;
- opvallende securityrisico's.

Op het einde van deze stap moet je een securityregelmatrix kunnen maken.

---

### 7.5 Stap 5: test gericht

Pas nadat je het ontwerp begrijpt, begin je gericht te testen.

Een goede test vertrekt altijd vanuit een verwachting.

Niet:

> Ik ping wat toestellen en kijk wat er gebeurt.

Wel:

> Een guest-pc mag naar internet, maar mag niet naar de interne server. Ik test beide verkeersstromen en noteer het resultaat.

Vragen die je beantwoordt:

- Welke verkeersstromen moeten werken?
- Welke verkeersstromen moeten geblokkeerd zijn?
- Welke test bewijst dat?
- Komt het werkelijke resultaat overeen met het verwachte resultaat?
- Indien niet: is dat een configuratiefout of een ontwerprisico?

Voorbeeld van gerichte testen:

| Bron en doel | Dienst of methode | Verwacht | Betekenis |
|---|---|---|---|
| Staff naar server | gebruikte applicatiedienst, bijvoorbeeld HTTPS | werkt | medewerkers kunnen de vereiste applicatie gebruiken |
| Guest naar externe testhost | ICMP of beschikbare internetdienst | werkt | bezoekers hebben het ontworpen externe pad |
| Guest naar server | dezelfde gevoelige dienst als bij de positieve test | werkt niet | interne servers zijn afgeschermd |
| Student naar management-IP | SSH, HTTPS of beschikbare beheerpoort | werkt niet | management is beschermd |
| IT naar management-IP | dezelfde beheerdienst | werkt | beheerders behouden noodzakelijke toegang |

Waarom is dit belangrijk?

Zonder verwacht resultaat is een test moeilijk te interpreteren. Als een ping lukt, weet je alleen dat er connectiviteit is. Je weet nog niet of die connectiviteit gewenst is.

Een slechte situatie:

> Een student ziet dat guest naar server kan pingen en noteert "connectiviteit OK".

Waarom is dit slecht?

- De test wordt technisch bekeken, maar niet securitymatig.
- Het resultaat is net een probleem, geen succes.
- De student verwart bereikbaarheid met correct ontwerp.

Wat noteer je?

- testbron;
- testdoel;
- verwacht resultaat;
- werkelijk resultaat;
- conclusie;
- mogelijke oorzaak bij afwijking.

Bewaar bij een onverwacht resultaat eerst de beginsituatie. Een onmiddellijke wijziging
vernietigt mogelijk precies het bewijs dat je nodig hebt om de oorzaak te begrijpen.

**Typische fout:** alleen ICMP testen en daaruit besluiten dat een applicatie werkt of
niet werkt. `ping` controleert bereikbaarheid met ICMP. De functionele requirement kan
over DNS, HTTP(S), SSH of een andere dienst gaan. Kies de test die bij de requirement
past.

Op het einde van deze stap moet je een bruikbaar testplan met resultaten hebben.

---

### 7.6 Stap 6: benoem risico's

Na de verkenning en testen formuleer je risico's.

Een risico is geen vaag gevoel zoals:

> Security is niet goed.

Een goed risico is concreet:

> Het guest VLAN kan de interne server bereiken. Daardoor kan een onbekend gasttoestel interne systemen scannen of aanvallen.

Vragen die je beantwoordt:

- Wat is het probleem?
- Welke impact kan dit hebben?
- Voor wie of wat is dit gevaarlijk?
- Hoe ernstig is het?
- Welke verbetering zou dit risico verminderen?

Om risico's te prioriteren, beoordeel je minstens **waarschijnlijkheid** en **impact**.
Je hoeft in dit hoofdstuk geen complexe numerieke methode te gebruiken.

| Waarschijnlijkheid | Betekenis in deze analyse |
|---|---|
| Laag | scenario vraagt uitzonderlijke omstandigheden of meerdere onafhankelijke fouten |
| Middel | scenario is realistisch, maar niet voortdurend aanwezig |
| Hoog | blootstelling bestaat nu of de fout zal waarschijnlijk optreden bij normale groei of uitval |

| Impact | Betekenis in deze analyse |
|---|---|
| Laag | beperkte hinder voor één toestel of niet-kritieke dienst |
| Middel | een team, zone of belangrijke functie wordt geraakt |
| Hoog | brede uitval, toegang tot kritieke infrastructuur of ernstige security-impact |

Een risico met hoge impact en hoge waarschijnlijkheid krijgt normaal eerder aandacht
dan een theoretisch probleem met lage impact. Noteer aannames: zonder logging of
productiedata blijft een inschatting soms voorlopig.

Voorbeeld:

| Risico | Waarom is dit een probleem? | Mogelijke verbetering |
|---|---|---|
| Guest kan server bereiken | onbekende toestellen krijgen toegang tot interne systemen | blokkeer guest naar interne subnetten |
| Management bereikbaar vanuit Students | gewone clients kunnen beheerinterfaces scannen | beperk management tot IT-zone |
| Een router doet alle routing | uitval legt meerdere VLAN's stil | onderzoek redundante gateway of tweede pad |
| Geen IP-plan | uitbreiding en troubleshooting worden moeilijk | documenteer subnetten en gateways |
| ACL's zonder uitleg | regels zijn moeilijk veilig aan te passen | koppel ACL's aan requirements |

Waarom is dit belangrijk?

In een enterprise omgeving moet je niet alleen problemen vinden, maar ook kunnen uitleggen waarom ze belangrijk zijn. Een beheerder moet prioriteiten kunnen stellen.

Een slechte situatie:

> Een analyse bevat alleen "VLAN 99 is bereikbaar".

Waarom is dit onvoldoende?

- Het zegt niet waarom dit erg is.
- Het zegt niet wie toegang heeft.
- Het zegt niet welke impact mogelijk is.
- Het bevat geen voorstel tot verbetering.

Op het einde van deze stap moet je minstens vijf concrete risico's of verbeterpunten kunnen formuleren.

---

### 7.7 Stap 7: formuleer verbeteringen

Een verbetering moet concreet en toetsbaar zijn.

Niet:

> Maak het netwerk veiliger.

Wel:

> Blokkeer verkeer van het guest VLAN naar alle interne private subnetten, maar laat verkeer naar internet toe.

Niet:

> Zorg voor betere documentatie.

Wel:

> Maak een VLAN-tabel met VLAN-ID, naam, subnet, gateway, doel en zone.

Waarom is dit belangrijk?

Vage verbeteringen zijn moeilijk uitvoerbaar en moeilijk te controleren. Concrete verbeteringen kan je plannen, configureren en testen.

Voorbeelden van concrete verbeteringen:

| Vaag | Concreet |
|---|---|
| Security verbeteren | guest VLAN blokkeren naar interne subnetten |
| Redundantie toevoegen | tweede uplink voorzien tussen access switch en core switch |
| Management beveiligen | SSH alleen toelaten vanaf IT-subnet |
| IP-plan verbeteren | subnetten per zone documenteren en groeiruimte voorzien |
| ACL's opruimen | per ACL noteren welke requirement ze afdwingt |

Een professioneel verbeterpunt bevat meer dan een technisch commando:

| Onderdeel | Vraag |
|---|---|
| Scope | Welke zone, dienst of component verandert? |
| Requirement | Welk gewenst gedrag moet ontstaan? |
| Implementatie | Welke ontwerp- en configuratiewijziging is nodig? |
| Acceptatietest | Welke allow- en deny-tests moeten slagen? |
| Neveneffect | Welk legitiem verkeer kan onbedoeld geraakt worden? |
| Rollback | Hoe keer je veilig terug als de wijziging fout loopt? |
| Documentatie | Welke tabellen, schema's en configuratiehistoriek moeten mee wijzigen? |

Op het einde van deze stap moet je advies kunnen geven alsof je aan een IT-verantwoordelijke rapporteert:

- wat is het probleem;
- waarom is het belangrijk;
- wat stel je voor;
- hoe kan je testen dat de verbetering werkt?

---

### 7.8 Stap 8: trek een conclusie

Een analyse eindigt met een duidelijke conclusie.

Je beantwoordt de centrale vraag van dit hoofdstuk:

> Is dit netwerk klaar om uit te groeien tot een enterprise netwerk?

Een goede conclusie is genuanceerd.

Bijvoorbeeld:

> Het netwerk werkt technisch voor basisconnectiviteit, maar is nog niet enterprise-ready. De belangrijkste problemen zijn de brede toegang vanuit het guest VLAN, de onvoldoende afgeschermde managementzone, het ontbreken van redundantie en de beperkte documentatie. Voor verdere groei zijn een duidelijk zoneschema, een securityregelmatrix en betere toegangscontrole nodig.

Waarom is dit belangrijk?

Een professioneel advies zegt niet alleen of iets werkt, maar ook welke risico's blijven bestaan en welke verbeteringen prioriteit hebben.

Een slechte conclusie:

> Alles werkt.

Waarom is dit slecht?

- Het zegt niets over security.
- Het zegt niets over schaalbaarheid.
- Het zegt niets over betrouwbaarheid.
- Het zegt niets over beheerbaarheid.
- Het helpt niet om verbeteringen te plannen.

In Enterprise Networks leer je dus om verder te kijken dan het eerste technische succes. Je analyseert, documenteert, test en verantwoordt je ontwerpkeuzes.

Gebruik in je conclusie eventueel deze compacte readiness-matrix:

| Domein | Vaststelling | Bewijs | Prioriteit |
|---|---|---|---|
| Schaalbaarheid | ... | IP-plan of capaciteit | ... |
| Betrouwbaarheid | ... | afhankelijkheid of failovertest | ... |
| Security | ... | matrix en positieve/negatieve test | ... |
| Beheerbaarheid | ... | documentatie en reproduceerbare analyse | ... |

Zo wordt `niet enterprise-ready` geen losse mening, maar een onderbouwde conclusie.

---

## 8. Show-commando's als onderzoekstools

In Cisco Packet Tracer en op Cisco-toestellen gebruik je vaak `show`-commando's om informatie op te vragen.

In dit hoofdstuk gebruiken we die commando's niet om basisconfiguratie opnieuw aan te leren. We gebruiken ze als onderzoekstools.

Een goed gekozen `show`-commando helpt je een concrete vraag te beantwoorden.

Niet:

> Ik voer `show running-config` uit en kijk wat ik tegenkom.

Wel:

> Ik wil weten welke ACL's actief zijn op een interface. Daarom controleer ik eerst de interfaceconfiguratie en daarna de ACL-inhoud.

Het verschil is belangrijk. Zonder onderzoeksvraag verdrink je snel in configuratie-output.

---

### 8.1 Eerst de vraag, dan het commando

Een professionele analyse start niet met een commando, maar met een vraag.

Voorbeelden:

| Onderzoeksvraag | Mogelijk commando | Wat kan dit aantonen? | Wat bewijst dit niet? |
|---|---|---|---|
| Welke VLAN's en accesspoorten bestaan er? | `show vlan brief` | lokale VLAN-database en poorttoewijzing | dat het VLAN end-to-end over trunks werkt |
| Welke trunks bestaan er? | `show interfaces trunk` | trunkstatus en toegestane VLAN's op dit toestel | dat de overzijde identiek en correct geconfigureerd is |
| Welke IP-adressen en statussen hebben interfaces? | `show ip interface brief` | beknopte laag 3-status | dat routing, ACL's en applicatiediensten correct werken |
| Welke routes kent het toestel? | `show ip route` | gekozen routes en next hops | dat het retourpad bestaat of het einddoel antwoordt |
| Welke ACL's bestaan er? | `show access-lists` | regelvolgorde en eventueel matchcounters | dat de ACL op het juiste pad actief is |
| Waar is een ACL toegepast? | gerichte delen van `show running-config` | interface en richting van de configuratie | dat alle vereiste verkeersstromen getest zijn |
| Is NAT/PAT actief? | `show ip nat translations` plus gerichte configuratie | aanwezige vertalingen na gegenereerd verkeer | dat DNS, routing en filtering volledig correct zijn |
| Welke interfaces zijn up of down? | `show ip interface brief` | administratieve en operationele status | dat een up-interface nuttig verkeer doorstuurt |

Waarom is dit belangrijk?

Een netwerkconfiguratie bevat veel informatie. Als je zonder doel begint te zoeken, mis je vaak de relevante details.

Een slechte situatie:

> Een student opent `show running-config`, scrollt door de volledige configuratie en zegt daarna: "Ik zie niets fout."

Waarom is dit slecht?

- Er was geen duidelijke onderzoeksvraag.
- De student weet niet welk deel van de configuratie relevant is.
- Belangrijke informatie zoals trunking, ACL-toepassing of routing kan gemakkelijk gemist worden.
- De analyse is moeilijk te controleren door iemand anders.

Een betere aanpak:

1. Formuleer je vraag.
2. Kies het commando dat die vraag beantwoordt.
3. Noteer het resultaat.
4. Vergelijk het resultaat met wat je verwacht.
5. Trek een conclusie.

Gebruik waar mogelijk meer dan één soort bewijs:

```text
ontwerpdocument -> configuratiecontrole -> operationele output -> end-to-end test
```

Als die bronnen elkaar tegenspreken, heb je geen reden om één bron blind te geloven.
De afwijking is zelf een belangrijk onderzoeksresultaat.

---

### 8.2 `show vlan brief`

Met `show vlan brief` krijg je een overzicht van VLAN's en accesspoorten.

Je gebruikt dit commando voor vragen zoals:

- Welke VLAN's bestaan er?
- Welke namen hebben de VLAN's?
- Welke switchpoorten zitten in welk VLAN?
- Zijn er poorten die in het verkeerde VLAN staan?
- Worden VLAN's logisch benoemd?

Voorbeeld van wat je kan afleiden:

| Observatie | Mogelijke conclusie |
|---|---|
| VLAN 40 heet `Guests` | er is een apart gastennetwerk voorzien |
| Poort Fa0/12 staat in VLAN 40 | het toestel op die poort zit in het guest VLAN |
| VLAN 99 heet `Management` | er is een apart management VLAN |
| Veel poorten staan nog in VLAN 1 | mogelijk slechte standaardconfiguratie |
| VLAN 77 heeft geen duidelijke naam | documentatie of ontwerp is onduidelijk |

Een slechte situatie:

> Een pc van een medewerker zit per ongeluk op een poort in VLAN 40 Guests.

Waarom is dit slecht?

- De medewerker krijgt mogelijk andere toegangsrechten dan bedoeld.
- De pc kan geblokkeerd worden van interne diensten.
- Of omgekeerd: een guest-poort kan te veel rechten krijgen als ze verkeerd benoemd is.
- Troubleshooting wordt moeilijk omdat het probleem niet op de pc zelf zit, maar op de switchpoort.

Wat noteer je in je analyse?

- bestaande VLAN's;
- VLAN-namen;
- opvallende of ontbrekende VLAN-namen;
- poorten die mogelijk verkeerd toegewezen zijn.

---

### 8.3 `show interfaces trunk`

Met `show interfaces trunk` controleer je trunkverbindingen.

Een **trunk** is een verbinding waarover meerdere VLAN's tussen netwerktoestellen worden vervoerd. Trunks worden vaak gebruikt tussen switches of tussen een switch en een router bij router-on-a-stick.

Je gebruikt dit commando voor vragen zoals:

- Welke poorten zijn trunkpoorten?
- Welke VLAN's mogen over de trunk?
- Welke native VLAN wordt gebruikt?
- Worden alle noodzakelijke VLAN's doorgestuurd?
- Worden er te veel VLAN's doorgestuurd?

Waarom is dit belangrijk?

Als een VLAN niet over een trunk mag, kunnen toestellen in dat VLAN mogelijk niet communiceren met andere delen van het netwerk.

Een slechte situatie:

> VLAN 30 Servers bestaat op twee switches, maar VLAN 30 is niet toegestaan op de trunk tussen die switches.

Waarom is dit slecht?

- Servers of clients in VLAN 30 kunnen elkaar mogelijk niet bereiken.
- Het VLAN lijkt correct te bestaan, maar wordt niet correct doorgegeven.
- Troubleshooting kan misleidend zijn als je alleen `show vlan brief` bekijkt.

Nog een slechte situatie:

> Alle VLAN's zijn toegestaan op elke trunk, ook VLAN's die daar niet nodig zijn.

Waarom is dit slecht?

- Onnodige VLAN's worden verspreid door het netwerk.
- De impact van configuratiefouten wordt groter.
- Securitysegmentatie wordt zwakker.
- Het wordt moeilijker om te controleren waar een VLAN echt gebruikt wordt.

Wat noteer je in je analyse?

- trunkpoorten;
- toegestane VLAN's;
- native VLAN;
- ontbrekende of overbodige VLAN's op trunks.

---

### 8.4 `show ip interface brief`

Met `show ip interface brief` krijg je snel een overzicht van interfaces, IP-adressen en interface-statussen.

Je gebruikt dit commando voor vragen zoals:

- Welke interfaces hebben een IP-adres?
- Welke interfaces zijn up of down?
- Welke subinterfaces bestaan er?
- Welke interface is mogelijk de gateway voor een VLAN?
- Zijn belangrijke verbindingen actief?

Waarom is dit belangrijk?

Dit commando geeft snel een eerste beeld van laag 3-connectiviteit en interfaceproblemen.

Een slechte situatie:

> Een VLAN kan niet naar buiten communiceren. De student controleert ACL's, maar de router-subinterface voor dat VLAN staat administratively down.

Waarom is dit slecht?

- Het probleem zit niet in security, maar in interface-status.
- Er wordt tijd verloren door op de verkeerde laag te zoeken.
- Een simpele statuscontrole had het probleem sneller zichtbaar gemaakt.

Wat noteer je in je analyse?

- interfaces met IP-adressen;
- down of administratively down interfaces;
- subinterfaces voor VLAN's;
- vermoedelijke gateways.

Let op: `show ip interface brief` vertelt niet alles. Je ziet bijvoorbeeld niet altijd welke ACL op een interface hangt. Daarvoor moet je gerichter verder kijken.

---

### 8.5 `show ip route`

Met `show ip route` controleer je de routingtabel.

De routingtabel toont welke netwerken een router of multilayer switch kent en via welke weg verkeer gestuurd wordt.

Je gebruikt dit commando voor vragen zoals:

- Kent het toestel alle nodige subnetten?
- Is er een default route naar internet?
- Welke routes zijn direct connected?
- Welke routes zijn statisch of dynamisch geleerd?
- Is er maar een pad of zijn er meerdere routes?

Waarom is dit belangrijk?

Een toestel kan alleen verkeer doorsturen naar netwerken waarvoor het een route kent.

Een slechte situatie:

> Clients kunnen hun default gateway bereiken, maar niet het internet. Er ontbreekt een default route op de router.

Waarom is dit slecht?

- Lokaal verkeer kan werken, maar extern verkeer faalt.
- De clientconfiguratie lijkt correct, maar het probleem zit in routing.
- Zonder routingtabel kan je dit moeilijk correct inschatten.

Nog een slechte situatie:

> Een router kent het servernetwerk niet, maar er wordt alleen getest vanaf clients die in hetzelfde VLAN zitten als de server.

Waarom is dit slecht?

- De test bewijst alleen lokale bereikbaarheid.
- Inter-VLAN of routed verkeer is niet getest.
- Een routingprobleem blijft verborgen.

Wat noteer je in je analyse?

- connected routes;
- default route;
- ontbrekende routes;
- routingtoestellen die kritisch zijn;
- mogelijke afhankelijkheid van een enkel pad.

---

### 8.6 `show access-lists`

Met `show access-lists` bekijk je de inhoud van ACL's.

Een **ACL**, of **Access Control List**, is een lijst regels die verkeer kan toestaan of blokkeren. ACL's worden vaak gebruikt om toegang tussen VLAN's, subnetten of zones te beperken.

Je gebruikt dit commando voor vragen zoals:

- Welke ACL's bestaan er?
- Welke regels staan in een ACL?
- Welk verkeer wordt toegestaan?
- Welk verkeer wordt geblokkeerd?
- Zijn de regels specifiek of te breed?

Waarom is dit belangrijk?

ACL's bepalen vaak of securityregels effectief afgedwongen worden.

Een slechte situatie:

> Er bestaat een ACL met een regel `permit ip any any` bovenaan.

Waarom is dit slecht?

- Die regel laat al het IP-verkeer toe.
- Regels die daaronder verkeer proberen te blokkeren, worden mogelijk nooit bereikt.
- De ACL lijkt aanwezig, maar beschermt in de praktijk weinig of niets.

Nog een slechte situatie:

> Een ACL blokkeert guest-verkeer naar servers, maar laat guest-verkeer naar het managementnetwerk wel toe.

Waarom is dit slecht?

- De ACL beschermt maar een deel van het netwerk.
- Managementinterfaces blijven bereikbaar vanuit een laag vertrouwde zone.
- De securityregelmatrix en de configuratie komen niet overeen.

Wat noteer je in je analyse?

- ACL-naam of nummer;
- belangrijke permit- en deny-regels;
- te brede regels;
- ontbrekende blokkeringen;
- match met de securityregelmatrix.

Let op: `show access-lists` toont de ACL-inhoud, maar niet altijd waar de ACL toegepast is. Een ACL die bestaat maar nergens op een interface hangt, heeft geen effect.

---

### 8.7 `show running-config`

Met `show running-config` bekijk je de actieve configuratie van een toestel.

Dit commando bevat veel informatie. Gebruik het daarom gericht.

Je gebruikt dit commando voor vragen zoals:

- Waar is een ACL toegepast?
- Welke subinterfaces bestaan er?
- Welke encapsulation hoort bij welk VLAN?
- Waar staat NAT/PAT geconfigureerd?
- Welke interfaces zijn inside of outside?
- Welke VLAN-namen zijn ingesteld?
- Welke managementinstellingen bestaan er?

Waarom is dit belangrijk?

Sommige informatie zie je niet volledig met korte overzichtscommando's. Dan moet je de running-config gericht controleren.

Een slechte situatie:

> Een ACL bestaat en ziet er correct uit, maar ze is op de verkeerde interface of in de verkeerde richting toegepast.

Waarom is dit slecht?

- De ACL-inhoud is correct, maar het effect is fout.
- Verkeer wordt misschien niet geblokkeerd waar je dat verwacht.
- Of correct verkeer wordt onbedoeld geblokkeerd.

Bij ACL's is niet alleen de inhoud belangrijk, maar ook:

- op welke interface ze hangt;
- in welke richting ze toegepast is;
- voor welk verkeer die interface logisch gebruikt wordt.

Een andere slechte situatie:

> NAT is geconfigureerd, maar de inside- en outside-interface zijn verwisseld.

Waarom is dit slecht?

- Clients kunnen mogelijk niet naar internet.
- De router vertaalt adressen niet zoals verwacht.
- De fout zit in de context van de interfaces, niet alleen in de NAT-regel zelf.

Wat noteer je in je analyse?

- relevante interfaceconfiguratie;
- ACL-toepassing;
- NAT-configuratie;
- subinterfaces;
- managementinstellingen;
- opvallende of onduidelijke configuratie.

Gebruik `show running-config` dus als naslag, niet als eerste en enige analyse-instrument.

---

### 8.8 `show ip nat translations` en NAT-controle

Met `show ip nat translations` kan je controleren of NAT/PAT actief vertalingen maakt.

Je gebruikt dit commando voor vragen zoals:

- Worden interne adressen vertaald?
- Welke interne hosts hebben actieve NAT-translaties?
- Wordt internetverkeer effectief via NAT/PAT behandeld?

Waarom is dit belangrijk?

Een NAT-configuratie kan aanwezig zijn, maar dat betekent niet automatisch dat ze correct werkt.

Een slechte situatie:

> De NAT-regels staan in de configuratie, maar er verschijnen geen NAT-translaties wanneer een client naar internet probeert te gaan.

Waarom is dit slecht?

- De NAT-regel matcht mogelijk het verkeer niet.
- De inside/outside-aanduiding kan fout zijn.
- De route naar internet kan ontbreken.
- De ACL die NAT-verkeer selecteert kan verkeerd zijn.

Wat noteer je in je analyse?

- of NAT/PAT gebruikt wordt;
- op welk toestel NAT gebeurt;
- of vertalingen verschijnen bij internetverkeer;
- mogelijke afwijkingen.

In Packet Tracer zijn sommige NAT-controles beperkter dan op echte toestellen, maar het principe blijft hetzelfde: controleer niet alleen of configuratie bestaat, maar ook of ze effect heeft.

---

### 8.9 Praktische commandostrategie

Gebruik bij een netwerkanalyse een vaste volgorde.

Een mogelijke volgorde:

1. `show vlan brief`
2. `show interfaces trunk`
3. `show ip interface brief`
4. `show ip route`
5. `show access-lists`
6. gerichte controle met `show running-config`
7. NAT-controle indien internettoegang deel is van de opdracht
8. gerichte connectiviteitstesten

Waarom deze volgorde?

- Je begint met de logische indeling.
- Daarna controleer je of VLAN's correct doorgegeven worden.
- Daarna bekijk je IP-interfaces en routing.
- Daarna onderzoek je securityregels.
- Pas daarna duik je gericht in de volledige configuratie.

Een slechte strategie:

> Meteen overal `show running-config` uitvoeren en proberen te onthouden wat je gezien hebt.

Waarom is dit slecht?

- Je mist structuur.
- Je documenteert minder gericht.
- Je verwart details met hoofdzaak.
- Je kan je analyse moeilijk verantwoorden.

Een goede strategie:

> Ik onderzoek eerst de VLAN-structuur, daarna routing, daarna securityregels en daarna test ik de verwachte verkeersstromen.

Dat is precies het soort werkwijze dat in Enterprise Networks belangrijk wordt.

---

### 8.10 Wat je altijd moet noteren

Tijdens een analyse moet je niet elk stukje configuratie overschrijven. Je noteert wat nodig is om het netwerk te begrijpen en te beoordelen.

Noteer minstens:

- VLAN's en namen;
- subnetten en gateways;
- trunks en toegestane VLAN's;
- routinglocatie;
- default route;
- NAT/PAT-locatie;
- ACL's en hun doel;
- waar ACL's toegepast zijn;
- management-IP's;
- opvallende risico's;
- testresultaten.

Een slechte situatie:

> Een student heeft veel commando's uitgevoerd, maar niets genoteerd. Op het einde weet niemand nog welke test welk resultaat gaf.

Waarom is dit slecht?

- Resultaten zijn niet controleerbaar.
- De analyse kan niet nagekeken of herhaald worden.
- Fouten worden moeilijk gekoppeld aan oorzaken.
- De conclusie is gebaseerd op geheugen in plaats van bewijs.

Een goede analyse laat sporen na: tabellen, testresultaten, korte conclusies en duidelijke verbeterpunten.

**Kernzin:**

> Een `show`-commando is geen ritueel. Het is een meetinstrument voor één concrete
> onderzoeksvraag.

---

## 9. Geïntegreerd voorbeeld: van vaststelling naar advies

In de workshop analyseer je het netwerk van **NetNova**. Het volgende voorbeeld toont
hoe je van losse technische observaties naar een professioneel advies gaat.

### 9.1 Beginsituatie

Stel dat je het volgende vaststelt:

- VLAN 40 heet `Guests`;
- clients in VLAN 40 krijgen via DHCP een correct adres;
- ze bereiken de externe testserver via NAT/PAT;
- de interne webserver en het management-IP van een switch antwoorden ook;
- op de router bestaat een ACL met de naam `GUEST-IN`;
- de documentatie vermeldt alleen dat het gastennetwerk "werkt".

Een zwakke conclusie is:

> VLAN 40 en de ACL zijn correct, want de guest-pc heeft connectiviteit.

Die conclusie gebruikt aanwezigheid en bereikbaarheid als bewijs voor security. Dat is
precies de denkfout die dit hoofdstuk wil vermijden.

### 9.2 Requirement reconstrueren

Vraag eerst wat gasten functioneel nodig hebben.

| Bron | Doel | Dienst | Gewenst | Reden |
|---|---|---|---|---|
| Guests | externe testhost of internet | vereiste externe diensten | allow | bezoekers hebben internettoegang nodig |
| Guests | interne webserver | interne applicatiedienst | deny | geen functionele noodzaak |
| Guests | Management | alle beheerdiensten | deny | gasten beheren geen infrastructuur |
| Guests | eigen gateway | noodzakelijke netwerkfunctie | allow | verkeer moet het VLAN kunnen verlaten |

Nu heb je een norm waarmee je het werkelijke gedrag kan vergelijken.

### 9.3 Bewijs verzamelen

| Onderzoeksvraag | Actie | Observatie | Tussenconclusie |
|---|---|---|---|
| Hoort de testclient echt bij Guests? | controleer adres, gateway, switchpoort en VLAN | client zit in VLAN 40 | bronzone klopt |
| Waar verlaat verkeer VLAN 40? | controleer gateway, subinterface en route | router is controlepunt | ACL moet op dit pad effect hebben |
| Wat staat in `GUEST-IN`? | bekijk regelvolgorde | ACL bevat relevante deny-regels | inhoud lijkt bedoeld voor de requirement |
| Waar is de ACL actief? | controleer interface en richting | ACL is niet toegepast op de guest-subinterface | configuratie bestaat, maar dwingt niets af |
| Wat doet het netwerk werkelijk? | voer allow- en deny-tests uit | alle doelen zijn bereikbaar | operationele toestand wijkt af van requirement |

### 9.4 Risico formuleren

Een volledig risico bevat meer dan een foutnaam.

| Element | Formulering |
|---|---|
| Bedrijfsmiddel | interne servers en managementinterfaces |
| Blootstelling | guest-clients hebben een routed pad naar interne zones |
| Oorzaak | de bedoelde ACL bestaat, maar is niet effectief toegepast |
| Impact | onbekende of besmette toestellen kunnen interne diensten en infrastructuur benaderen |
| Bewijs | negatieve HTTP- of beheertest slaagt terwijl deny verwacht werd |
| Prioriteit | hoog, omdat de blootstelling nu bestaat en gevoelige zones raakt |

### 9.5 Verbetering en acceptatie

Een bruikbaar advies luidt bijvoorbeeld:

> Dwing de goedgekeurde guest-regelmatrix af op het routed pad van VLAN 40. Laat alleen
> noodzakelijke externe en infrastructuurdiensten toe en blokkeer interne en
> managementnetwerken. Valideer na de wijziging zowel toegestane internettoegang als
> geweigerde toegang tot de interne webserver en managementdiensten. Werk de
> ACL-documentatie en het testverslag bij.

Acceptatiecriteria:

| Test | Verwacht na verbetering | Bewijs |
|---|---|---|
| Guest krijgt een correcte lease en bereikt de gateway | werkt | clientconfiguratie en gerichte test |
| Guest bereikt de voorziene externe dienst | werkt | functionele externe test en NAT/PAT-observatie |
| Guest bereikt interne webserver | werkt niet | negatieve diensttest |
| Guest bereikt managementdienst | werkt niet | negatieve beheerverbinding |
| Staff bereikt noodzakelijke interne webserver | werkt | regressietest vanuit een toegelaten zone |

Een **regressietest** controleert of gedrag dat vóór de wijziging correct was, daarna
nog steeds correct is. Die test is belangrijk: een securitywijziging is niet geslaagd
als ze het verboden verkeer blokkeert maar tegelijk noodzakelijke bedrijfscommunicatie
breekt.

**Kernzin:**

> Een goede analyse verbindt requirement, technisch bewijs, risico, verbetering en
> acceptatietest in één controleerbare redenering.

---

## 10. Labkeuzes en productieontwerp

Een lab maakt concepten zichtbaar binnen beperkte tijd en middelen. Dat is nuttig,
zolang je de vereenvoudiging niet verwart met een productieaanbeveling.

| Thema | Aanvaardbare labkeuze in dit hoofdstuk | Wat productie aanvullend vraagt |
|---|---|---|
| Topologie | één router kan inter-VLAN routing, NAT/PAT en filtering combineren | capaciteit, redundantie, functiescheiding en foutdomeinen beoordelen: delen die door één fout tegelijk geraakt worden |
| Beschikbaarheid | single points of failure herkennen zonder volledige high availability (HA) te bouwen | redundante voeding, toestellen, links, gateways en geteste failover waar de impact dit rechtvaardigt |
| Filtering | Cisco ACL's tonen bron-, doel- en richtinglogica | stateful firewalling die ook de toestand van verbindingen volgt, applicatiecontext, centraal policybeheer en logging kunnen nodig zijn |
| Management | management-VLAN met beperkte bronnetwerken | AAA, MFA, een beveiligde jump host, centraal logbeheer en eventueel out-of-band toegang |
| Internet | een gesimuleerde externe host stelt internet voor | echte ISP-afhankelijkheden, publieke adressering, DNS en beveiliging aan de externe netwerkgrens |
| Monitoring | handmatig `show`-commando's uitvoeren | continue monitoring, alerts, metrics, logs en bewaartermijnen |
| Documentatie | één analyseverslag en Packet Tracer-bestand | beheerde bron van waarheid, versiebeheer, eigenaarschap en changeproces |
| Testen | handmatige tests vanaf enkele representatieve hosts | herhaalbare acceptatie-, regressie-, failover- en hersteltests |
| Configuratieback-up | eventueel het `.pkt`-bestand bewaren | geautomatiseerde, beveiligde back-up en getest herstel |

**In productie:** meer technologie is niet automatisch beter. Elke extra redundante
component, securitycontrole of beheertool voegt ook configuratie, afhankelijkheden en
operationele verantwoordelijkheid toe. De keuze moet passen bij de bedrijfsimpact.

---

## 11. Typische fouten en betere aanpakken

| Typische fout | Waarom de redenering faalt | Betere aanpak |
|---|---|---|
| `ping` werkt, dus het netwerk is goed | bereikbaarheid zegt niets over gewenst beleid | vergelijk functionele en negatieve tests met requirements |
| een ACL bestaat, dus verkeer is beschermd | plaatsing, richting en regelvolgorde kunnen fout zijn | controleer configuratiecontext, counters en end-to-end effect |
| alle interne zones zijn vertrouwd | clients, servers en management hebben verschillende impact | ken trustniveau en minimaal benodigd verkeer per zone toe |
| meer VLAN's betekent automatisch meer security | zonder filtering blijft routed toegang mogelijk | ontwerp eerst zones en regels, koppel daarna technische segmentatie |
| elke mogelijke fout krijgt redundantie | kost en complexiteit groeien zonder impactanalyse | prioriteer kritieke diensten en foutdomeinen |
| documentatie wordt na de configuratie gemaakt | beslissingen en tijdelijke uitzonderingen raken verloren | documenteer requirement, wijziging en validatie als één proces |
| volledige configuraties gelden als analyse | veel output zonder conclusie is moeilijk bruikbaar | selecteer bewijs per onderzoeksvraag en leg de betekenis uit |
| alleen gewenste toegang wordt getest | te brede toegang blijft onzichtbaar | test bij elke grens minstens één representatieve deny-case |
| onmiddellijk configuratie wijzigen | baseline en oorzaak kunnen verdwijnen | observeer en bewaar bewijs vóór de wijziging |
| een verbetering is `maak het veiliger` | scope en acceptatie zijn niet toetsbaar | benoem bron, doel, dienst, maatregel en testcriteria |
| risico's zijn een ongesorteerde lijst | kritieke problemen verdrinken in kleine opmerkingen | beoordeel waarschijnlijkheid, impact en afhankelijkheden |
| een lab-IP of labserver wordt als echt internet gezien | de simulatie bewijst geen productieconnectiviteit | benoem het externe labdoel en de grens van het bewijs |

Gebruik deze tabel niet als afvinklijst zonder context. Een bevinding is pas nuttig als
je ze koppelt aan het concrete netwerk dat je onderzoekt.

---

## 12. Controlevragen en denkvragen

Beantwoord deze vragen zonder meteen in een configuratie te zoeken. Formuleer eerst wat
je verwacht en welk bewijs je nodig hebt.

### 12.1 Begripscontrole

1. Waarom kan een netwerk technisch werken en toch niet enterprise-ready zijn?
2. Wat is het verschil tussen een VLAN, een subnet en een zone?
3. Waarom bewijst het bestaan van een ACL niet dat een securityregel werkt?
4. Wat is het verschil tussen een positieve en een negatieve test?
5. Waarom is een single point of failure een bedrijfsrisico en niet alleen een technisch detail?
6. Wanneer is een IP-plan schaalbaar?
7. Wat maakt documentatie operationeel bruikbaar?
8. Waarom moet je bij een wijziging ook regressietests uitvoeren?

### 12.2 Toepassingsvragen

1. Een guest-pc bereikt internet en een interne server. Welke aanvullende informatie
   heb je nodig voordat je een ACL-wijziging voorstelt?
2. `show interfaces trunk` toont dat VLAN 30 toegestaan is op één switch. Welk bewijs
   ontbreekt nog om end-to-end bereikbaarheid van VLAN 30 te bevestigen?
3. Een access switch heeft twee uplinks. Waarom mag je niet onmiddellijk besluiten dat
   de aansluiting betrouwbaar is?
4. Een management-VLAN is alleen via SSH bereikbaar, maar wel vanuit elk user-VLAN.
   Welk kwaliteitsdomein is vooral onvoldoende en welke tests stel je voor?
5. Een netwerk heeft actuele schema's, maar niemand weet wie ze moet bijwerken. Welk
   beheerprobleem blijft bestaan?
6. Een deny-test faalt, maar de ACL-counter blijft op nul. Welke hypothesen onderzoek je?

### 12.3 Criteria voor een sterk antwoord

Een sterk antwoord:

- benoemt de requirement of de ontbrekende requirement;
- onderscheidt ontwerp, configuratie en operationele toestand;
- verwijst naar een concrete bron, doelzone en dienst;
- stelt relevant bewijs of een gerichte test voor;
- benoemt impact en eventuele neveneffecten;
- maakt duidelijk waar een aanname of labbeperking bestaat.

---

## 13. Samenvatting

Belangrijkste inzichten:

- een enterprise netwerk wordt beoordeeld op schaalbaarheid, betrouwbaarheid, security
  en beheerbaarheid;
- die kwaliteiten moeten aantoonbaar zijn, niet alleen aanwezig lijken;
- requirements beschrijven gewenst gedrag en horen vóór losse configuratieregels te
  komen;
- VLAN's en subnetten zijn technische bouwstenen, terwijl zones functie, vertrouwen en
  toegangsbeleid uitdrukken;
- een zonegrens heeft pas effect als filtering op het werkelijke verkeerspad wordt
  afgedwongen;
- least privilege vereist expliciete bron-, doel- en dienstkeuzes;
- documentatie moet desired state, current state, gaps, acties en validatie uit elkaar
  houden;
- een `show`-commando beantwoordt één onderzoeksvraag en heeft altijd grenzen aan wat
  het bewijst;
- configuratie, operationele toestand en end-to-end testbewijs zijn verschillende
  niveaus van zekerheid;
- positieve tests bewijzen vereiste functionaliteit, negatieve tests bewijzen dat
  grenzen werken en regressietests beschermen bestaand correct gedrag;
- een professioneel risico bevat oorzaak, asset, blootstelling, impact, bewijs en
  prioriteit;
- een professioneel verbeterpunt bevat scope, requirement, implementatie,
  acceptatietests, neveneffecten, rollback en documentatie-impact;
- Packet Tracer is geschikt om ontwerpprincipes en testredeneringen zichtbaar te maken,
  maar vereenvoudigt productieaspecten zoals high availability, monitoring, logging en
  changebeheer.

**Kernzin:**

> Een professioneel netwerk is niet alleen correct geconfigureerd. Het is bewust
> ontworpen, aantoonbaar getest, begrijpelijk gedocumenteerd en voorspelbaar beheerbaar
> bij groei, wijziging en storing.
