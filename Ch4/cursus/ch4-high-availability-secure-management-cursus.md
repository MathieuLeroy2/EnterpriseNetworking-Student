# Hoofdstuk 4 - High availability en secure management

## 1. Inleiding

In hoofdstuk 2 keek je naar technische redundantie in switching en routing. In hoofdstuk 3 ontwierp je securityzones, trust boundaries en DMZ-beleid. In dit hoofdstuk breng je die twee lijnen samen.

Een enterprise netwerk moet niet alleen correct werken. Het moet ook:

- beschikbaar blijven wanneer er iets uitvalt;
- veilig beheerd kunnen worden;
- onderhoud toelaten zonder onnodige schade;
- herstelbaar zijn na een foutieve wijziging;
- aantoonbaar gecontroleerd en gedocumenteerd worden.

De centrale vraag van dit hoofdstuk is:

> Wat gebeurt er wanneer een kritisch onderdeel faalt of wanneer een beheerder een fout maakt?

In een klein labo is het vaak voldoende dat een ping werkt. In een bedrijf is dat niet genoeg. Een switch kan herstarten, een internetverbinding kan wegvallen, een configuratie kan verkeerd geplakt worden, of een beheeraccount kan misbruikt worden. Enterprise-denken betekent dat je zulke situaties vooraf inschat en beheersbaar maakt.

Kernidee:

> High availability beperkt de impact van technische uitval. Secure management beperkt
> de kans en de impact van beheerfouten of misbruik. Beide steunen op dezelfde aanpak:
> risico's vooraf herkennen, controles ontwerpen, herstel voorbereiden en het resultaat
> aantoonbaar testen.

Dit hoofdstuk bestaat uit twee grote delen:

1. **High availability**: hoe beperk je impact bij storingen?
2. **Secure management**: hoe zorg je dat beheer veilig, controleerbaar en herstelbaar gebeurt?

De rode draad door het hoofdstuk is:

```text
bedrijfsproces
      |
      v
technische afhankelijkheden
      |
      v
storing of beheerfout
      |
      v
impact beperken -> werking bewijzen -> herstel documenteren
```

In de workshop pas je die redenering toe op het netwerk van BluePeak Services. Je
voert een audit uit: je zoekt single points of failure, ontwerpt failovertesten,
beoordeelt managementtoegang en maakt een back-up-, rollback- en herstelvoorstel.
Het doel is dus niet alleen een werkende topologie, maar een verdedigbaar oordeel over
beschikbaarheid en beheer.

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. single points of failure herkennen in een enterprise-netwerk;
2. het verschil uitleggen tussen redundantie, failover en load balancing;
3. de impact van een storing inschatten per zone of bedrijfsproces;
4. uitleggen waarom redundantie getest moet worden;
5. een eenvoudig failovertestplan opstellen;
6. het nut van configuratieback-ups en rollback toelichten;
7. RTO en RPO conceptueel uitleggen;
8. een managementnetwerk beoordelen vanuit securitystandpunt;
9. uitleggen waarom Telnet en onbeperkte managementtoegang onveilig zijn;
10. lokale accounts, centrale authenticatie en AAA conceptueel vergelijken;
11. het doel van RADIUS en TACACS+ beschrijven;
12. role-based access toepassen op netwerkbeheer;
13. het nut van een jump server uitleggen;
14. logging van beheeracties koppelen aan troubleshooting en incidentanalyse;
15. een secure management policy opstellen;
16. een foutdomein en een verborgen gemeenschappelijke afhankelijkheid herkennen;
17. technische failover onderscheiden van volledig dienstherstel;
18. positieve en negatieve managementtests ontwerpen;
19. labvereenvoudigingen onderscheiden van een productieontwerp;
20. testresultaten formuleren als controleerbaar bewijs.

---

## 3. High availability

**High availability** betekent dat een systeem of netwerk beschikbaar blijft ondanks storingen, onderhoud of gedeeltelijke uitval.

High availability betekent niet dat er nooit iets fout gaat. Het betekent wel dat een fout niet meteen het volledige bedrijf stillegt.

Voorbeelden:

| Situatie | Zonder high availability | Met high availability |
|---|---|---|
| Een access uplink valt uit. | Een volledige afdeling verliest verbinding. | Een tweede uplink neemt over. |
| Een gateway-router faalt. | Clients raken niet meer buiten hun VLAN. | Een standby gateway neemt over. |
| Een internetlijn valt uit. | Internet en cloudapplicaties zijn onbereikbaar. | Een tweede verbinding neemt over. |
| Een configuratiefout wordt gemaakt. | Herstel duurt lang en is onzeker. | Rollback gebeurt met bekende vorige configuratie. |

Belangrijke gedachte:

> Beschikbaarheid gaat niet alleen over extra hardware. Het gaat ook over ontwerp, testen, procedures en documentatie.

High availability moet je onderscheiden van twee verwante begrippen:

| Begrip | Centrale vraag | Voorbeeld |
|---|---|---|
| High availability | Hoe blijft de dienst werken bij een verwachte storing? | een standby gateway neemt automatisch over |
| Resilience | Hoe blijft het geheel beheersbaar en herstelt het van verschillende verstoringen? | redundantie, monitoring, noodprocedures en geoefend herstel werken samen |
| Disaster recovery | Hoe bouwen we de dienst opnieuw op na een zware of langdurige verstoring? | toestellen vervangen en configuraties uit back-up herstellen |

De grenzen zijn niet absoluut, maar het onderscheid helpt bij ontwerpen. Een tweede
uplink is een HA-maatregel. Een gedocumenteerde restoreprocedure is vooral een
herstelmaatregel. Samen maken ze het netwerk veerkrachtiger.

### 3.1 Beschikbaarheid is een ontwerpkeuze

High availability begint niet met de vraag welke extra toestellen je kan kopen. Het begint met de vraag welke processen moeten blijven werken.

Voorbeelden:

| Proces | Technische afhankelijkheid | Beschikbaarheidsvraag |
|---|---|---|
| Medewerkers gebruiken interne applicaties. | access switches, core, servernetwerk, DNS, routing | Hoe lang mag de applicatie onbereikbaar zijn? |
| Finance verwerkt betalingen. | financeclient, finance-app, servernetwerk, securityregels | Mag dit tijdens kantooruren uitvallen? |
| IT lost incidenten op. | managementnetwerk, beheeraccounts, jump server | Kan IT nog beheren als het productienetwerk stuk is? |
| Externe klanten bereiken een webdienst. | internetedge, firewall, DMZ, webserver | Merken klanten uitval meteen? |

Een technisch klein onderdeel kan dus toch kritisch zijn als een belangrijk bedrijfsproces ervan afhangt. Omgekeerd hoeft niet elk onderdeel dubbel uitgevoerd te worden. Een printer in een vergaderruimte heeft een andere beschikbaarheidsbehoefte dan de core switch of managementtoegang.

Sterke analysezin:

> De beschikbaarheidsbehoefte wordt niet bepaald door het toestel zelf, maar door het bedrijfsproces dat afhankelijk is van dat toestel.

### 3.2 Degraded mode

Een netwerk hoeft bij een storing niet altijd volledig uit te vallen. Soms werkt het nog, maar met beperkingen. Dat noemen we een **degraded mode**.

Voorbeelden:

| Normale werking | Degraded mode |
|---|---|
| Twee internetlijnen zijn actief. | Een lijn valt weg; internet werkt trager of zonder backup. |
| Twee uplinks dragen verkeer. | Een uplink valt weg; alle verkeer loopt via een link. |
| Centrale AAA-server is bereikbaar. | Admins gebruiken tijdelijke lokale fallbackprocedure. |
| Monitoring en logging werken centraal. | Logs worden tijdelijk lokaal bewaard of later doorgestuurd. |

Degraded mode is beter dan volledige uitval, maar je moet de beperkingen kennen.

Belangrijke vragen:

- Welke diensten blijven werken?
- Welke diensten werken trager of beperkter?
- Welke risico's nemen toe tijdens degraded mode?
- Hoe lang mag degraded mode duren?
- Hoe weet je dat je in degraded mode zit?

Een netwerk dat stilzwijgend in degraded mode blijft draaien is gevaarlijk. Het lijkt te werken, maar de volgende storing kan dan plots veel zwaarder wegen omdat de reserve al opgebruikt is.

### 3.3 Beschikbaarheid meetbaar maken

Zeggen dat een dienst "zeer beschikbaar" moet zijn, is te vaag. Je moet eerst bepalen
wat **beschikbaar** betekent en over welke periode je meet.

Voor een interne applicatie kan beschikbaar betekenen:

- de gebruiker bereikt de applicatie via de juiste DNS-naam;
- authenticatie werkt;
- de applicatie kan haar database bereiken;
- antwoorden komen binnen de afgesproken tijd;
- beheer en monitoring kunnen een fout vaststellen.

Een geslaagde ping naar één interface bewijst dus niet dat de volledige dienst
beschikbaar is.

Een eenvoudige beschikbaarheidsberekening is:

```text
beschikbaarheid = (totale meettijd - onbeschikbare tijd) / totale meettijd x 100%
```

Een percentage krijgt pas betekenis wanneer de meetperiode en uitsluitingen duidelijk
zijn. Gepland onderhoud wel of niet meetellen kan het resultaat sterk veranderen.

| Vraag | Waarom nodig? |
|---|---|
| Welke dienst meet je? | een toestel kan bereikbaar zijn terwijl de gebruikersdienst faalt |
| Vanuit welk standpunt meet je? | interne gebruikers en externe klanten volgen mogelijk een ander pad |
| Welke periode gebruik je? | 99,9% per maand is iets anders dan 99,9% per jaar |
| Telt gepland onderhoud mee? | zonder afspraak kan hetzelfde cijfer anders geïnterpreteerd worden |
| Welke vertraging is nog aanvaardbaar? | een extreem trage dienst kan technisch up maar praktisch onbruikbaar zijn |

Twee operationele begrippen helpen verklaren waardoor beschikbaarheid verbetert:

| Begrip | Betekenis | Hoe verbeter je dit? |
|---|---|---|
| MTBF | gemiddelde tijd tussen storingen | betrouwbaardere componenten, betere omgeving en minder menselijke fouten |
| MTTR | gemiddelde tijd om een dienst te herstellen | monitoring, documentatie, reserveonderdelen, back-ups en geoefende procedures |

Je hoeft in dit OPO geen uitgebreide statistische berekeningen te maken. Het belangrijke
inzicht is dat redundantie vooral de impact van een storing kan beperken, terwijl goed
beheer en herstelprocedures vooral de hersteltijd verkorten.

Kernzin:

> Beschikbaarheid beoordeel je op het niveau van een gebruikersdienst, niet alleen op
> het niveau van een toestel of interface.

---

## 4. Single points of failure

Een **single point of failure** is een onderdeel waarvan de uitval een groter systeem doet falen.

Voorbeelden:

| Onderdeel | Mogelijke impact |
|---|---|
| Enige uplink van een access switch | Alle toestellen achter die switch verliezen toegang tot servers en internet. |
| Enige core switch | Meerdere VLAN's of zones vallen tegelijk uit. |
| Enige default gateway | Clients kunnen niet meer routen naar andere netwerken. |
| Enige internetverbinding | Cloud, VPN en externe toegang vallen weg. |
| Enige firewall | DMZ, internet en interne filtering worden afhankelijk van een toestel. |
| Enige beheerpc | Beheer wordt moeilijk bij defect of besmetting. |
| Enige configuratiekopie op het toestel zelf | Herstel na defect wordt traag of onmogelijk. |

Een single point of failure is niet altijd automatisch fout. Soms is het een bewuste keuze omdat de impact laag is of omdat redundantie te duur is.

Enterprise-analyse vraagt daarom altijd twee vragen:

1. Wat valt er uit als dit onderdeel faalt?
2. Is die impact aanvaardbaar voor dit bedrijfsproces?

### 4.1 Soorten single points of failure

Single points of failure zitten niet alleen in kabels of switches. Ze kunnen fysiek, logisch of organisatorisch zijn.

| Type | Voorbeeld | Waarom riskant? |
|---|---|---|
| Fysiek | een uplink, een voeding, een switch | defect veroorzaakt directe uitval |
| Logisch | een default route, een VLAN dat maar over een trunk loopt | configuratiefout of padverlies raakt meerdere diensten |
| Security | een enige firewallregelset zonder back-up | verkeerde policy kan toegang blokkeren of openzetten |
| Management | een enige jump server of beheerpc | beheer wordt onmogelijk of onveilig |
| Procedureel | een beheerder weet als enige hoe herstel werkt | kennis zit bij een persoon |
| Documentatie | geen actueel netwerkdiagram | troubleshooting duurt langer |

Voor studenten is dit belangrijk omdat Packet Tracer vooral fysieke en logische fouten zichtbaar maakt. In echte enterprise-netwerken zijn procedurele en documentatiefouten minstens even gevaarlijk.

### 4.2 Kritieke en minder kritieke zones

Niet elk onderdeel is even kritisch.

| Zone of functie | Typische beschikbaarheidsbehoefte |
|---|---|
| Management | hoog, want nodig voor herstel en beheer |
| Servers | hoog, want applicaties hangen ervan af |
| Finance | hoog tijdens kritieke periodes |
| Staff | middel tot hoog, afhankelijk van werkproces |
| Guests | laag tot middel |
| IoT | afhankelijk van functie, bijvoorbeeld camera's of productie |
| DMZ | hoog als publieke diensten belangrijk zijn |

Een gastennetwerk dat een uur niet werkt, is vervelend. Een beheerzone die onbereikbaar is tijdens een incident is veel ernstiger.

### 4.3 Verborgen single points of failure

Sommige single points of failure zijn niet meteen zichtbaar op een topologietekening.

Voorbeelden:

| Ziet er redundant uit | Verborgen probleem |
|---|---|
| Twee access uplinks | beide uplinks lopen naar dezelfde switch |
| Twee switches | beide hangen aan dezelfde stroomkring |
| Twee routers | alle clients gebruiken maar een fysiek gatewayadres |
| Twee internetverbindingen | beide komen via dezelfde provider of dezelfde kabelinvoer |
| Management VLAN | alle beheer loopt via dezelfde core die je nodig hebt om te herstellen |
| Configback-ups | back-ups staan op dezelfde laptop of cloudmap zonder toegangscontrole |

Een goede audit kijkt dus verder dan "er zijn twee kabels".

Sterke vragen:

- Zijn de redundante paden echt onafhankelijk?
- Is er een gemeenschappelijke component waar alles toch door moet?
- Is het alternatief getest?
- Is de documentatie actueel genoeg om het alternatief te gebruiken?

### 4.4 Foutdomeinen en gemeenschappelijke oorzaken

Een **foutdomein** is het deel van de omgeving dat door dezelfde storing geraakt kan
worden. Twee componenten zijn pas werkelijk onafhankelijk wanneer ze niet in hetzelfde
relevante foutdomein zitten.

| Gewenste bescherming | Gemeenschappelijk foutdomein dat de bescherming ondermijnt |
|---|---|
| twee uplinks | dezelfde kabelgoot wordt beschadigd |
| twee switches | dezelfde voeding, racktemperatuur of softwarebug |
| twee internetproviders | dezelfde straatinvoer of onderliggende carrier |
| twee AAA-servers | dezelfde VM-host, database of DNS-service |
| lokale en cloudback-up | hetzelfde beheerdersaccount kan beide verwijderen |

Dit noemen we ook een **common-mode failure**: één oorzaak schakelt meerdere zogenaamd
redundante onderdelen tegelijk uit.

Controleer:

1. Teken rond elk paar redundante componenten welke infrastructuur ze delen.
2. Kies één storing, bijvoorbeeld stroomuitval, DNS-uitval of een foutieve change.
3. Volg welke delen daardoor tegelijk geraakt worden.
4. Beslis of het resterende pad de vereiste dienst echt kan leveren.

Voorbeeld:

> Twee routers beschermen niet tegen een foutieve configuratie die door automatisatie
> op beide routers tegelijk wordt uitgerold.

Kernzin:

> Redundantie telt pas wanneer de alternatieven niet door dezelfde waarschijnlijke
> oorzaak tegelijk uitvallen.

---

## 5. Redundantie, failover en load balancing

Deze begrippen worden vaak door elkaar gebruikt, maar ze betekenen niet hetzelfde.

| Begrip | Betekenis | Voorbeeld |
|---|---|---|
| Redundantie | Er is een extra component of pad beschikbaar. | Twee uplinks naar de distributionlaag. |
| Failover | Een tweede component neemt over wanneer de eerste faalt. | Standby gateway wordt active. |
| Load balancing | Verkeer wordt verdeeld over meerdere componenten. | Twee actieve internetverbindingen verdelen verkeer. |

Een netwerk kan redundant lijken zonder goede failover.

Voorbeeld:

```text
+-----------+       +-----------+
| SW-ACC   |-------| SW-DIST-1 |
|           \      +-----------+
|            \
|             \    +-----------+
|              ----| SW-DIST-2 |
+-----------+      +-----------+
```

Dit ziet er redundant uit, maar je moet nog controleren:

- dragen beide trunks de juiste VLAN's?
- voorkomt STP loops?
- is de gateway redundant?
- is routing naar servers en internet redundant?
- is het failovergedrag getest?

Kernzin:

> Redundantie op een diagram is pas waardevol wanneer je kan bewijzen wat er gebeurt bij uitval.

### 5.1 Redundantie per laag

Redundantie moet je per laag beoordelen. Een redundant onderdeel op een laag lost geen probleem op een andere laag automatisch op.

| Laag | Mogelijke redundantie | Wat blijft nog te controleren? |
|---|---|---|
| Fysiek | dubbele kabels, dubbele voedingen | lopen ze niet via hetzelfde risico? |
| Layer 2 | STP, EtherChannel, dubbele uplinks | zijn VLAN's correct toegelaten? |
| Layer 3 | dynamische routing, tweede route | kiest routing het gewenste pad? |
| Gateway | HSRP of VRRP | gebruiken clients de virtual IP? |
| Internetedge | tweede router of lijn | werkt failover en NAT/firewallbeleid mee? |
| Management | jump server, console, out-of-band | kan IT nog beheren bij productiestoring? |
| Configuratie | back-ups, versiebeheer | kan je effectief herstellen? |

Voorbeeld:

Een access switch heeft twee uplinks. Dat is Layer 2-redundantie. Maar als de default gateway maar op een enkel toestel staat en dat toestel faalt, verliezen clients nog altijd inter-VLAN toegang. De uplinks zijn dan niet genoeg.

### 5.2 Active-passive en active-active

Redundante systemen kunnen op verschillende manieren werken.

| Model | Betekenis | Voorbeeld | Aandachtspunt |
|---|---|---|---|
| Active-passive | een component werkt, de andere wacht | standby gateway | failover moet snel en getest zijn |
| Active-active | meerdere componenten verwerken verkeer | load sharing over links | verdeling en asymmetrisch verkeer controleren |
| Active-backup path | primair pad actief, backup geblokkeerd | STP alternate port | blocked poort is niet automatisch fout |

Een veelgemaakte fout is denken dat alle redundante links tegelijk actief moeten zijn. Bij STP is het net normaal dat een pad geblokkeerd wordt om loops te vermijden. Bij EtherChannel worden meerdere fysieke links logisch samengenomen. Bij HSRP is vaak een gateway active en een andere standby.

Kernzin:

> Beschikbaarheid vraagt dat je weet welk model je gebruikt: standby, load sharing of gecontroleerd backup-pad.

### 5.3 Redundantie kan nieuwe complexiteit toevoegen

Meer redundantie betekent niet automatisch minder risico. Het netwerk wordt complexer.

Voorbeelden:

- extra uplinks vragen correct STP- of EtherChannel-gedrag;
- meerdere routers vragen correcte routing en gateway redundancy;
- twee internetlijnen vragen beleid voor NAT, firewallregels en return traffic;
- centrale AAA vraagt fallback als de AAA-server niet bereikbaar is;
- een jump server vermindert blootstelling, maar wordt zelf kritisch.

Daarom hoort bij elke redundantie ook documentatie:

| Vraag | Waarom? |
|---|---|
| Wat is primair en wat is backup? | troubleshooting wordt sneller |
| Welke storing wordt opgevangen? | verwachtingen blijven realistisch |
| Hoe test je failover? | redundantie wordt bewezen |
| Hoe herstel je de normale toestand? | failback gebeurt gecontroleerd |

### 5.4 Technische failover is nog geen dienstherstel

Een protocol kan correct overschakelen terwijl de gebruikersdienst toch niet herstelt.
Daarom moet je de volledige afhankelijkheidsketen testen.

Voorbeeld:

```text
client
  |
accesspad
  |
default gateway
  |
routing en firewall
  |
DNS / applicatie / database
```

HSRP kan een nieuwe active gateway tonen, maar dat bewijst nog niet dat:

- de nieuwe gateway een bruikbare route naar de server heeft;
- ACL- of firewallbeleid op het alternatieve pad klopt;
- return traffic via een geldige weg terugkomt;
- bestaande applicatiesessies de omschakeling overleven;
- monitoring de storing heeft gedetecteerd.

Dit verschil is extra belangrijk bij stateful functies.

| Functie | Mogelijk probleem bij failover |
|---|---|
| firewall | sessiestatus bestaat niet op het tweede toestel, waardoor verbindingen opnieuw moeten starten |
| NAT | het alternatieve toestel kent de bestaande vertalingen niet |
| DHCP | leases of configuratie zijn niet gesynchroniseerd |
| DNS | de dienst is bereikbaar, maar clients gebruiken nog een onbereikbaar adres uit cache |
| centrale AAA | netwerkbeheer werkt technisch, maar admins kunnen niet meer authenticeren |

Kernzin:

> Controleer na protocolfailover altijd de echte gebruikersflow én het beheerpad.

---

## 6. Failover testen

Een failovertest toont aan of het ontwerp echt werkt onder foutcondities.

Kernidee:

> Een failovertest is een gecontroleerd experiment: leg vooraf vast wat je verandert,
> wat je verwacht, waar je observeert en wanneer je stopt of terugrolt.

Een goed failovertestplan bevat:

| Onderdeel | Vraag |
|---|---|
| Testobject | Welke link, switch, router of dienst schakel je uit? |
| Verwacht gedrag | Wat moet blijven werken? |
| Impact | Welke korte onderbreking is aanvaardbaar? |
| Controle | Welke `show`-commando's of testen gebruik je? |
| Herstel | Hoe breng je de situatie terug naar normaal? |
| Conclusie | Is de redundantie bewezen of alleen verondersteld? |

Voorbeeld:

| Stap | Actie | Verwacht resultaat |
|---:|---|---|
| 1 | Start ping van client naar server. | Ping werkt. |
| 2 | Controleer actieve gateway of actieve uplink. | Actieve rol is duidelijk. |
| 3 | Schakel actieve uplink of gateway uit. | Kort verlies is mogelijk. |
| 4 | Controleer herstel. | Verkeer loopt via alternatief pad. |
| 5 | Controleer statuscommando's. | Nieuwe active of forwarding path is zichtbaar. |
| 6 | Herstel originele situatie. | Netwerk keert gecontroleerd terug. |

Slechte conclusie:

> Na een tijdje werkte ping weer.

Betere conclusie:

> Na het uitschakelen van de primaire uplink werd de alternatieve STP-poort forwarding. De client verloor tijdelijk pakketten, maar de server bleef daarna bereikbaar. De redundantie is functioneel voor deze linkfout.

Een sterke test verloopt in vier fasen:

| Fase | Actie | Bewijs |
|---|---|---|
| Baseline | controleer de normale gebruikersflow en de actieve component | ping/applicatietest plus relevante `show`-output |
| Fout injecteren | schakel exact één vooraf gekozen component uit | tijdstip en uitgevoerde actie |
| Failover valideren | meet impact en controleer het alternatieve pad | pakketverlies, nieuwe rol, route, STP-status en logevent |
| Failback en nazorg | herstel de component en controleer de eindtoestand | normale rolverdeling, werkende dienst en geen onverwachte alarmen |

Verander tijdens de meting niet meerdere instellingen tegelijk. Anders weet je niet
welke gebeurtenis het resultaat veroorzaakte.

### 6.1 Wat meet je tijdens failover?

Een failovertest gaat niet alleen over "werkt het weer?". Je wil ook weten hoe het netwerk zich gedraagt.

| Meting | Waarom belangrijk? |
|---|---|
| Starttijd storing | nodig om herstelduur te meten |
| Aantal verloren pings of sessieonderbreking | toont gebruikersimpact |
| Nieuwe actieve poort of gateway | bewijst welk onderdeel overnam |
| Routingtabel voor en na failover | toont of routes aangepast zijn |
| Logberichten | tonen of monitoring de storing ziet |
| Hersteltijd naar normale toestand | toont failbackgedrag |

Een korte onderbreking kan aanvaardbaar zijn voor gewone clienttoegang, maar niet voor alle toepassingen. Sommige applicaties herstellen vanzelf. Andere applicaties verbreken sessies en vragen opnieuw aanmelden.

### 6.2 Failover versus failback

**Failover** is het overnemen door een alternatief pad of toestel. **Failback** is de terugkeer naar de normale of primaire toestand.

Failback verdient evenveel aandacht als failover.

Voorbeeld:

| Stap | Risico |
|---|---|
| Primaire gateway valt uit. | standby neemt over |
| Primaire gateway komt terug. | verkeer kan opnieuw verschuiven |
| Preempt is actief. | primaire gateway neemt rol terug over |
| Routing of STP convergeert opnieuw. | korte tweede onderbreking mogelijk |

In sommige omgevingen wil je automatische failback. In andere omgevingen wil je manueel bepalen wanneer de primaire component terug actief wordt, bijvoorbeeld buiten kantooruren.

Sterke analysezin:

> De failovertest is pas volledig wanneer ook het herstel naar normale toestand gecontroleerd is.

### 6.3 Welke testen voer je niet zomaar live uit?

Niet elke failovertest is geschikt voor een productienetwerk tijdens normale werking.

| Test | Risico | Wanneer uitvoeren? |
|---|---|---|
| Access uplink down | beperkte groep kan korte hinder merken | labo of onderhoudsvenster |
| Core switch herstarten | netwerkbrede impact | alleen gepland en goedgekeurd |
| Edge-router uitschakelen | internet/DMZ kan wegvallen | onderhoudsvenster |
| Management-ACL wijzigen | beheer kan zichzelf buitensluiten | met console/noodpad klaar |
| AAA-server onbereikbaar maken | admins kunnen mogelijk niet aanmelden | met fallbackprocedure |

Professioneel testen betekent dus niet roekeloos testen. Je kiest een veilige scope, communiceert impact en hebt rollback klaar.

### 6.4 Positieve, negatieve en bewijstesten

Een beschikbaarheidstest bevat meer dan een succesvolle eindtoestand.

| Testtype | Voorbeeld | Wat toon je aan? |
|---|---|---|
| Positieve test | client bereikt server voor en na uplinkuitval | de gewenste dienst blijft of wordt opnieuw beschikbaar |
| Foutinjectie | primaire uplink wordt gecontroleerd uitgeschakeld | de test raakt werkelijk het bedoelde primaire pad |
| Negatieve controle | uitgeschakelde interface draagt geen verkeer meer | verkeer werkt niet toevallig nog via het zogezegd defecte onderdeel |
| Control-planebewijs | alternate poort wordt forwarding of standby wordt active | het verwachte mechanisme nam over |
| Data-planebewijs | applicatieflow of gerichte connectiviteit werkt | het nieuwe pad draagt echt gebruikersverkeer |
| Detectiebewijs | log of alarm meldt de storing | beheer weet dat de omgeving in degraded mode staat |

Typische fout:

> Alleen een doorlopende ping tonen zonder de actieve rol vóór en na de storing te
> controleren.

Die ping kan nuttig zijn, maar bewijst niet welk mechanisme de connectiviteit leverde.
In Packet Tracer zijn screenshots van `show spanning-tree`, `show standby`,
`show etherchannel summary` of `show ip route` daarom sterker wanneer ze gekoppeld
worden aan een concrete gebruikersflow.

Kies het commando op basis van de vraag die je wil beantwoorden:

| Controle | Mogelijk commando | Wat kan je ermee aantonen? |
|---|---|---|
| interface- en SVI-status | `show ip interface brief` | welke interfaces administratief en operationeel up zijn |
| trunkstatus en toegelaten VLAN's | `show interfaces trunk` | of het alternatieve Layer 2-pad de nodige VLAN's kan dragen |
| STP-rol en poorttoestand | `show spanning-tree` | welk pad forwarding of alternate is en hoe dat na uitval verandert |
| EtherChannelstatus | `show etherchannel summary` | of links werkelijk één bundel vormen en welke members actief zijn |
| first-hop redundancy | `show standby` | welke gateway active of standby is en of de rol wijzigt |
| routeringspad | `show ip route` | of een bruikbare route via het verwachte alternatief bestaat |
| effectieve configuratie | `show running-config` | welke instellingen het waargenomen gedrag kunnen verklaren |

Geen enkel commando bewijst op zichzelf de volledige gebruikersdienst. Combineer
statusoutput met een gerichte connectiviteits- of applicatietest.

### 6.5 Observatie is nog geen verklaring

Een professioneel testverslag scheidt drie zaken:

```text
Verwachting -> wat denk je dat het ontwerp zal doen?
Observatie  -> wat zag of mat je werkelijk?
Verklaring  -> welk mechanisme verklaart dat resultaat?
```

Voorbeeld:

| Onderdeel | Sterke formulering |
|---|---|
| Verwachting | na uitval van uplink A gebruikt `SW-ACC2` uplink B |
| Observatie | drie pings gingen verloren; poort G0/2 veranderde naar forwarding |
| Verklaring | RSTP convergeerde en activeerde het vooraf beschikbare alternatieve pad |
| Beperking | de test bewijst linkfailover, niet het gedrag bij volledige core-uitval |

De beperking hoort bij het resultaat. Zo voorkom je dat één geslaagde test wordt
voorgesteld als bewijs voor alle mogelijke storingen.

---

## 7. Onderhoudsvensters

Niet elke wijziging gebeurt tijdens normale kantooruren. Een **onderhoudsvenster** is een afgesproken periode waarin wijzigingen mogen gebeuren en waarin beperkte impact aanvaardbaar is.

Een goed onderhoudsvenster bevat:

| Onderdeel | Wat leg je vast? | Waarom? |
|---|---|---|
| Doel | gewenste technische en zakelijke uitkomst | voorkomt wijzigingen zonder duidelijke succesvoorwaarde |
| Scope | betrokken toestellen, interfaces, VLAN's en zones | begrenst het mogelijke foutdomein |
| Impact | verwachte onderbreking en getroffen gebruikers | maakt een bewuste planning mogelijk |
| Voorafcontrole | normale toestand en relevante outputs | levert een vergelijkingspunt |
| Back-up | huidige configuratie en versie | maakt herstel naar een bekende toestand mogelijk |
| Rollback | trigger, actie, eigenaar en maximale duur | voorkomt improvisatie onder tijdsdruk |
| Communicatie | wie vooraf, tijdens en na afloop informatie krijgt | gebruikers en support begrijpen wat gebeurt |
| Validatie | positieve, negatieve en beheertests | bewijst dat de change werkt zonder grenzen te openen |
| Documentatie | werkelijk resultaat en afwijkingen | houdt de baseline en audittrail actueel |

Waarom is dit belangrijk?

Zonder onderhoudsvenster worden technische wijzigingen bedrijfsrisico's. Een kleine configuratiefout op een core switch kan tijdens een les, vergadering, examen of productiemoment grote impact hebben.

### 7.1 Wat hoort in een onderhoudsvoorstel?

Voor een eenvoudige netwerkchange kan een onderhoudsvoorstel er zo uitzien:

| Veld | Voorbeeld |
|---|---|
| Change | Trunk naar `SW-ACC2` beperken tot noodzakelijke VLAN's. |
| Reden | Security en beheerbaarheid verbeteren. |
| Impact | Mogelijk korte onderbreking voor IT, IoT en Servers. |
| Voorafcontrole | `show interfaces trunk`, serverconnectiviteit, managementbereikbaarheid. |
| Back-up | Running-config van betrokken switches bewaren. |
| Uitvoering | Trunkconfiguratie aanpassen en direct testen. |
| Test na wijziging | VLAN 30, 40, 60 en 99 bereikbaar; andere VLAN's niet onnodig toegelaten. |
| Rollback | Vorige trunkconfiguratie terugzetten als server- of managementtest faalt. |
| Communicatie | IT en betrokken gebruikers verwittigen. |

Studenten hoeven geen zwaar enterprise-changeproces uit te werken, maar ze moeten leren dat een wijziging meer is dan een commando.

### 7.2 Onderhoudsvenster versus noodwijziging

Soms kan je niet wachten op een gepland onderhoudsvenster. Bij een ernstig securityprobleem of grote storing is een noodwijziging nodig.

Ook dan blijft structuur belangrijk.

| Geplande wijziging | Noodwijziging |
|---|---|
| ruim vooraf gecommuniceerd | snel beslist |
| volledige risicoanalyse | snelle risico-inschatting |
| uitgebreid testplan | minimale kritieke tests |
| normale goedkeuring | noodgoedkeuring achteraf documenteren |
| rustig rollbackpad | rollback zo eenvoudig mogelijk houden |

Een noodwijziging zonder documentatie wordt later vaak een nieuw probleem. Noteer daarom ook achteraf wat er veranderd is, waarom en welke testen geslaagd zijn.

### 7.3 Go/no-go-momenten

Een onderhoudsplan bevat best expliciete beslismomenten.

| Moment | Go wanneer | No-go of rollback wanneer |
|---|---|---|
| Voor de change | baseline klopt, back-up is bruikbaar en noodpad is getest | beginsituatie is al instabiel of herstelpad ontbreekt |
| Na de eerste wijziging | verwachte tussentoestand is zichtbaar | onverwachte zones of beheerflows vallen uit |
| Voor einde venster | alle kritieke tests slagen en logs zijn normaal | oorzaak van een kritieke fout is nog onduidelijk |
| Bij overdracht | documentatie en monitoring zijn bijgewerkt | omgeving blijft ongemerkt in degraded mode |

Dit maakt duidelijk wie op welk moment beslist. Vooral bij wijzigingen aan AAA,
managementrouting of ACL's wil je niet wachten tot het einde van het venster om te
ontdekken dat rollback te laat gestart is.

---

## 8. Configuratieback-ups

Een configuratieback-up is een kopie van de werkende configuratie van een toestel.

Voor netwerktoestellen wil je minstens weten:

| Vraag | Waarom belangrijk? |
|---|---|
| Van welke toestellen bestaat een back-up? | Zonder back-up wordt herstel manueel en traag. |
| Wanneer is de back-up genomen? | Een oude back-up kan fout of onvolledig zijn. |
| Waar wordt de back-up bewaard? | Alleen op het toestel zelf is onvoldoende. |
| Wie heeft toegang tot back-ups? | Configuraties kunnen gevoelige informatie bevatten. |
| Hoe wordt herstel getest? | Een back-up is pas nuttig als je ze kan gebruiken. |

In Packet Tracer kan dit eenvoudig blijven: studenten documenteren welke configuraties opgeslagen moeten worden en vergelijken running-config met de gewenste baseline.

Belangrijk:

> Een back-up is geen plan. Een back-up wordt pas waardevol wanneer je weet hoe je ermee herstelt.

Een bruikbare back-upstrategie beantwoordt vijf werkwoorden:

```text
verzamelen -> beschermen -> versie geven -> herstellen -> bewijzen
```

| Stap | Concrete betekenis |
|---|---|
| Verzamelen | neem van alle kritieke toestellen op het juiste moment een kopie |
| Beschermen | beperk toegang en bewaar minstens één kopie buiten het toestel |
| Versie geven | koppel datum, toestel, change en goedkeuringsstatus aan de configuratie |
| Herstellen | beschrijf hoe de configuratie op passend materiaal geladen wordt |
| Bewijzen | voer periodiek een restore-test uit en documenteer het resultaat |

### 8.1 Wat moet je bewaren?

Een bruikbare netwerkback-up bevat meer dan alleen een losse configuratiekopie.

| Item | Waarom bewaren? |
|---|---|
| Running-config | toont de actieve toestand op het moment van back-up |
| Startup-config | toont wat na reboot geladen wordt |
| Toestelnaam en model | nodig bij herstel of vervanging |
| Softwareversie | configuratiesyntax kan verschillen |
| Datum en tijd | je weet hoe recent de back-up is |
| Reden van wijziging | je begrijpt waarom de config zo staat |
| Netwerkdiagram | config alleen toont niet altijd fysieke context |
| Testresultaten | bewijzen dat de config toen werkte |

In Packet Tracer volstaat vaak een overzichtelijke verzameling running-configs en een notitie van de gewenste baseline. In een echte omgeving wordt dit vaak geautomatiseerd en in versiebeheer of een configuratiebeheersysteem geplaatst.

### 8.2 Back-ups moeten beschermd worden

Configuraties bevatten vaak gevoelige informatie, zelfs als je geen wachtwoorden noteert.

Voorbeelden:

- IP-adressen van managementinterfaces;
- VLAN- en zone-indeling;
- firewallregels;
- VPN- of AAA-verwijzingen;
- SNMP- of loggingbestemmingen;
- naamgeving van kritieke systemen.

Daarom mogen configuratieback-ups niet zomaar in een onbeveiligde map staan waar iedereen bij kan. Toegang tot back-ups hoort bij het rollenmodel.

Behandel een configuratieback-up als gevoelige beheerinformatie.

| Maatregel | Welk risico beperkt dit? |
|---|---|
| encryptie tijdens transport en opslag | onderscheppen of lezen van netwerk- en credentialinformatie |
| beperkte lees- en schrijfrechten | ongeoorloofde inzage of manipulatie |
| aparte beheeridentiteiten | onduidelijkheid over wie een back-up raadpleegde of wijzigde |
| versiegeschiedenis of immutabele kopie | ransomware of een foutieve change die ook oude kopieën aantast |
| secretbeheer buiten de config waar mogelijk | verspreiding van sleutels, community strings en wachtwoorden |

Een gehashte of versleutelde waarde in een configuratie mag je niet automatisch als
onschadelijk beschouwen. Ze kan nog altijd herbruikbaar zijn op een toestel of offline
aangevallen worden.

### 8.3 Back-upkwaliteit controleren

Een organisatie kan zeggen "we hebben back-ups", maar dat betekent niet automatisch dat ze bruikbaar zijn.

Controleer:

| Controle | Slecht teken |
|---|---|
| Recentheid | laatste back-up is maanden oud |
| Volledigheid | core switch ontbreekt |
| Herstelbaarheid | niemand weet hoe restore moet |
| Toegang | alleen een afwezige beheerder kent de locatie |
| Versie | config hoort bij ouder toestel of andere software |
| Test | back-up is nooit gebruikt in een hersteltest |

Sterke conclusie:

> Een niet-geteste back-up is een aanname, geen herstelgarantie.

### 8.4 Back-ups testen

Een back-up hebben is pas de eerste stap. Je moet ook testen of die back-up werkelijk gebruikt kan worden om een toestel of configuratie te herstellen.

Dat is belangrijk omdat een back-up op verschillende manieren waardeloos kan blijken:

| Probleem | Gevolg |
|---|---|
| De back-up is onvolledig. | Niet alle interfaces, VLAN's, routes of policies worden hersteld. |
| De back-up hoort bij een oudere configuratie. | Recente wijzigingen ontbreken. |
| De back-up hoort bij een ander toesteltype of softwareversie. | Configuratieregels werken niet of geven fouten. |
| De back-up bevat syntax die niet meer ondersteund wordt. | Restore lukt maar gedeeltelijk. |
| De back-up staat op een plaats waar niemand bij kan tijdens een incident. | Herstel vertraagt. |
| Niemand kent de restoreprocedure. | De back-up bestaat, maar herstel blijft improvisatie. |

De beste manier om back-ups te testen is een **restore-test** in een veilige omgeving. Je probeert de back-up dus niet zomaar op een productietoestel tijdens normale werking.

Een goede testaanpak:

| Stap | Actie | Doel |
|---:|---|---|
| 1 | Kies een representatieve back-up. | Niet alleen de makkelijkste back-up testen. |
| 2 | Gebruik een labtoestel, Packet Tracer-topologie of sandbox. | Productie niet onnodig riskeren. |
| 3 | Herstel de configuratie op een passend toestel of simulatie. | Controleren of de configuratie technisch laadbaar is. |
| 4 | Vergelijk de herstelde configuratie met de gewenste baseline. | Ontbrekende of foutieve onderdelen vinden. |
| 5 | Test kritieke functies. | Bewijzen dat VLAN's, trunks, routing, management en policies werken. |
| 6 | Noteer fouten en ontbrekende stappen. | De restoreprocedure verbeteren. |
| 7 | Documenteer testdatum en resultaat. | Aantonen dat back-ups bruikbaar zijn. |

Een back-uptest moet dus meer doen dan controleren of een bestand bestaat. Je moet nagaan of de configuratie:

- volledig is;
- op het juiste toesteltype past;
- recent genoeg is;
- zonder kritieke fouten geladen kan worden;
- de verwachte netwerkfuncties herstelt;
- door meerdere beheerders teruggevonden en gebruikt kan worden.

Voor netwerktoestellen zijn goede controlevragen:

| Controle | Vraag |
|---|---|
| Interfaces | Zijn de juiste interfaces actief en correct beschreven? |
| VLAN's en trunks | Zijn de juiste VLAN's aanwezig en toegelaten? |
| Routing | Zijn routes, OSPF-instellingen of default routes correct? |
| Securitybeleid | Zijn ACL's, firewallregels of managementbeperkingen aanwezig? |
| Management | Is het toestel veilig bereikbaar vanuit de juiste beheerzone? |
| Logging | Worden logs opnieuw naar de juiste bestemming gestuurd? |
| Documentatie | Klopt de herstelde toestand met het netwerkdiagram? |

In een onderwijscontext kan je dit eenvoudig simuleren:

- neem de running-config van een switch of router;
- plaats die in een leeg of gelijkaardig Packet Tracer-toestel;
- controleer of de configuratie geladen wordt;
- test de belangrijkste connectiviteit;
- vergelijk met het verwachte VLAN-, routing- en managementbeleid.

Belangrijk:

> Test back-ups regelmatig en niet pas tijdens een incident. Tijdens een storing wil je geen restoreprocedure voor het eerst ontdekken.

Sterke conclusie:

> Een goede back-upstrategie bestaat uit back-ups maken, back-ups veilig bewaren, restore testen en de testresultaten documenteren.

### 8.5 Wanneer neem je een nieuwe back-up?

Een vaste nachtelijke back-up is nuttig, maar changes vragen extra momenten.

| Moment | Doel |
|---|---|
| vóór een change | exacte terugkeerpositie vastleggen |
| na een geslaagde change | nieuwe goedgekeurde baseline bewaren |
| na noodherstel | vastleggen wat tijdens het incident werkelijk actief werd |
| periodiek automatisch | wijzigingen detecteren die buiten het changeproces gebeurden |
| vóór vervanging of upgrade | configuratie en context voor migratie bewaren |

Vergelijk ook `running-config` en `startup-config`. Een werkende running-config die
niet opgeslagen is, verdwijnt mogelijk bij een reboot. Omgekeerd kan een foutieve
startup-config pas tijdens de volgende herstart zichtbaar worden.

Controleer:

```text
Is de actieve configuratie de bedoelde configuratie?
Is de opstartconfiguratie daarmee in overeenstemming?
Is die toestand als goedgekeurde versie buiten het toestel bewaard?
```

---

## 9. Rollback

**Rollback** betekent dat je na een mislukte wijziging terugkeert naar een bekende werkende toestand.

Rollback is geen synoniem voor "alle commando's omgekeerd uitvoeren". Wijzigingen
kunnen toestand opbouwen, sessies verbreken of afhankelijkheden aanpassen. Een vooraf
geteste herstelactie is daarom betrouwbaarder dan tijdens het incident een omgekeerde
configuratie proberen te bedenken.

Een rollbackplan bevat:

- welke configuratie wordt teruggezet;
- op welke toestellen gebeurt dat;
- wie beslist dat rollback nodig is;
- welke testen bepalen dat de wijziging mislukt is;
- hoeveel tijd rollback mag duren;
- welke impact gebruikers merken;
- hoe je achteraf documenteert wat fout liep.

Voorbeeld:

| Wijziging | Rollbacktrigger | Rollbackactie |
|---|---|---|
| Nieuwe management-ACL | IT kan switches niet meer bereiken | vorige ACL terugzetten via console of alternatieve beheertoegang |
| Trunk pruning | VLAN 40 verliest servertoegang | vorige trunkconfiguratie herstellen |
| Nieuwe default route | internet valt weg | vorige route herstellen |
| HSRP-priority aanpassen | verkeerde gateway wordt active | vorige priority terugzetten |

Slechte aanpak:

> We proberen iets en lossen het achteraf wel op.

Betere aanpak:

> Voor de wijziging is duidelijk wat de vorige toestand was, hoe we terugkeren en welke test bepaalt of rollback nodig is.

### 9.1 Rollback versus roll forward

Bij een mislukte wijziging zijn er twee mogelijke strategieën:

| Strategie | Betekenis | Wanneer zinvol? |
|---|---|---|
| Rollback | terug naar vorige bekende werkende toestand | als impact hoog is of oorzaak onduidelijk |
| Roll forward | snel corrigeren naar een nieuwe werkende toestand | als fout klein, duidelijk en veilig herstelbaar is |

In een labo lossen studenten vaak verder op tot het werkt. In productie is dat niet altijd verstandig. Als een wijziging onverwacht een kritieke dienst raakt, is rollback vaak veiliger dan blijven proberen.

Voorbeeld:

Een nieuwe ACL blokkeert managementtoegang. Als je niet meteen ziet welke regel fout staat, is het beter om de vorige ACL terug te zetten dan om live verschillende regels te blijven proberen.

### 9.2 Rollback kan beheer verliezen

Sommige wijzigingen zijn extra gevaarlijk omdat ze het beheerpad zelf raken.

Voorbeelden:

- management-ACL aanpassen;
- trunk naar management VLAN aanpassen;
- default route van beheerzone wijzigen;
- AAA-configuratie wijzigen;
- jump server-firewallregel aanpassen.

Bij zulke wijzigingen moet je vooraf een noodpad hebben:

- fysieke console;
- alternatieve beheertoegang;
- out-of-band pad;
- iemand ter plaatse;
- duidelijke vorige configuratie.

Sterke waarschuwing:

> Een beheerwijziging zonder noodpad kan ervoor zorgen dat je jezelf buitensluit.

### 9.3 Rollbackcriteria

Een rollbackcriterium bepaalt wanneer je stopt met proberen en terugkeert.

Voorbeelden:

| Wijziging | Rollbackcriterium |
|---|---|
| Trunk pruning | server-VLAN of management VLAN is niet bereikbaar |
| Nieuwe ACL | IT kan managementinterfaces niet meer bereiken |
| Gateway redundancy | clients gebruiken geen werkende default gateway |
| Edge-route | internet of DMZ is langer dan afgesproken onbereikbaar |
| AAA-aanpassing | admins kunnen niet aanmelden via normale of fallbackmethode |

Zonder rollbackcriterium wordt discussie mogelijk op het slechtste moment: tijdens een storing.

### 9.4 Een rollbackbeslissing onder tijdsdruk

Gebruik bij een mislukte change een vaste beslisvolgorde:

1. Stop met bijkomende wijzigingen.
2. Bevestig welke kritieke test faalt.
3. Vergelijk de resterende tijd met de afgesproken rollbackduur.
4. Kies rollback als de oorzaak niet onmiddellijk duidelijk en veilig corrigeerbaar is.
5. Valideer na rollback opnieuw de kritieke gebruikers- en managementflows.
6. Bewaar logs en outputs voor analyse achteraf.

| Signaal | Waarschijnlijke keuze | Reden |
|---|---|---|
| fout is klein, lokaal en eenduidig | eventueel roll forward | één gecontroleerde correctie kan sneller zijn |
| meerdere onverwachte symptomen | rollback | foutdomein of oorzaak is onvoldoende begrepen |
| managementpad dreigt weg te vallen | onmiddellijke rollback via noodpad | verdere diagnose kan anders onmogelijk worden |
| onderhoudsvenster loopt af | rollback | herstelduur en gebruikersimpact dreigen te overschrijden |

Kernzin:

> Rollback is een vooraf ontworpen risicobeheersing, geen improvisatie nadat de change
> mislukt is.

---

## 10. Disaster recovery, RTO en RPO

**Disaster recovery** gaat over herstel na een ernstig incident, bijvoorbeeld brand, hardwaredefect, ransomware, verlies van een locatie of grote configuratiefout.

Twee begrippen zijn belangrijk:

| Begrip | Betekenis | Vraag |
|---|---|---|
| RTO | Recovery Time Objective | Hoe lang mag herstel duren? |
| RPO | Recovery Point Objective | Hoeveel gegevens of configuratiewijzigingen mag je verliezen? |

Voorbeelden:

| Systeem | Mogelijke RTO | Mogelijke RPO |
|---|---:|---:|
| Guest Wi-Fi | 1 werkdag | 1 dag |
| Managementtoegang | 30 minuten | laatste bekende configuratie |
| Finance-app | 2 uur | 15 minuten tot 1 uur |
| Publieke website | 1 uur | enkele uren |

RTO en RPO zijn geen technische waarden die je willekeurig kiest. Ze komen uit bedrijfsimpact.

Sterke analysezin:

> Voor de managementzone moet de RTO laag zijn, omdat beheertoegang nodig is om andere incidenten op te lossen.

RTO en RPO meten verschillende soorten verlies:

```text
incident -------------------------------> dienst hersteld
   |<-------------- RTO ---------------->|

laatste herstelpunt --------> incident
   |<---------- maximaal dataverlies volgens RPO ---------->|
```

Voor netwerkconfiguraties slaat het RPO niet alleen op bestanden. Het gaat ook over
wijzigingen sinds de laatste bruikbare en goedgekeurde configuratieversie.

### 10.1 Incident, outage en disaster

Niet elk probleem is een disaster.

| Niveau | Voorbeeld | Aanpak |
|---|---|---|
| Incident | een switchpoort staat fout | normale troubleshooting |
| Outage | een afdeling heeft geen netwerk | herstelprocedure en communicatie |
| Major outage | meerdere kritieke diensten liggen plat | prioriteiten, escalatie, managementcommunicatie |
| Disaster | locatie, core of veel systemen zwaar geraakt | disaster-recoveryplan |

Het verschil zit in impact, duur en herstelcomplexiteit.

Een foutieve VLAN-config op een accesspoort is meestal een incident. Een defecte core switch zonder back-upconfiguratie en zonder reserveplan kan een major outage of disaster worden.

### 10.2 RTO en RPO concreet toepassen

RTO en RPO worden vaak abstract besproken. Maak ze concreet met vragen.

| Vraag | Hoort bij |
|---|---|
| Hoe lang mag de finance-app onbereikbaar zijn? | RTO |
| Tot welke configuratieversie moeten we kunnen terugkeren? | RPO |
| Hoe recent moeten firewallregels herstelbaar zijn? | RPO |
| Hoe snel moet IT weer kunnen beheren? | RTO |
| Hoe lang mag de publieke website offline zijn? | RTO |

Voor netwerkconfiguraties betekent RPO bijvoorbeeld:

> Als een router vervangen moet worden, willen we maximaal de wijzigingen sinds de laatste goedgekeurde change verliezen.

Daarom neem je na een geslaagde wijziging opnieuw een back-up.

### 10.3 Herstelvolgorde

Bij een grote storing herstel je niet willekeurig. Je bepaalt een volgorde.

Een mogelijke herstelvolgorde:

1. managementtoegang herstellen;
2. core/distributionconnectiviteit herstellen;
3. routing en gatewayfuncties herstellen;
4. servernetwerk en kritieke applicaties herstellen;
5. internetedge en DMZ herstellen;
6. minder kritieke client- of guestdiensten herstellen;
7. monitoring en logging volledig valideren.

Deze volgorde kan verschillen per organisatie, maar management en core staan vaak hoog omdat ze nodig zijn voor verder herstel.

Sterke reflectievraag:

> Welke dienst moet eerst terugkomen omdat andere herstelacties ervan afhangen?

### 10.4 RTO en RPO toetsen op haalbaarheid

Een ambitieus hersteldoel zonder middelen is geen plan.

Voorbeeld:

> BluePeak kiest voor de core een RTO van 30 minuten. Er is echter geen reservetoestel,
> de configuratieback-up is drie maanden oud en de leverancier levert pas de volgende
> werkdag. Het doel en de herstelcapaciteit spreken elkaar tegen.

Toets elk hersteldoel daarom aan concrete voorwaarden:

| Voorwaarde | Vraag |
|---|---|
| Mensen | is er binnen de RTO iemand beschikbaar met de juiste rechten en kennis? |
| Materiaal | is vervanghardware of een alternatief pad tijdig beschikbaar? |
| Informatie | zijn recente configs, diagrammen, softwareversies en licenties beschikbaar? |
| Toegang | werkt console, out-of-band of fysieke toegang tijdens de storing? |
| Afhankelijkheden | zijn DNS, AAA, stroom en leverancierscontacten ook beschikbaar? |
| Oefening | is aangetoond dat de procedure binnen de gekozen tijd uitvoerbaar is? |

In productie:

> Een hersteldoel wordt geloofwaardig door middelen, eigenaarschap en tests. Alleen
> een getal in een document verlaagt de hersteltijd niet.

---

## 11. Secure management

Secure management gaat over de manier waarop netwerktoestellen beheerd worden.

Beheer is gevoelig omdat een beheerder:

- configuraties kan wijzigen;
- toegang tot zones kan openen of sluiten;
- routing kan aanpassen;
- logging kan uitzetten;
- beveiligingsregels kan verzwakken;
- toestellen kan herstarten.

Daarom verdient managementverkeer meer bescherming dan gewone gebruikerscommunicatie.

Belangrijke vraag:

> Wie mag welk toestel beheren, vanwaar, met welke rechten, en hoe wordt dat gelogd?

Kernidee:

> Secure management beschermt de volledige beheerketen: identiteit, beheertoestel,
> netwerkpad, protocol, doelinterface, bevoegdheden, logging en noodherstel.

Die keten ziet er conceptueel zo uit:

```text
beheerder
   |
sterke authenticatie
   |
beheertoestel of jump server
   |
beperkt managementpad
   |
SSH / HTTPS / veilige API
   |
managementinterface
   |
autorisatie + accounting
```

Als één schakel ontbreekt, kan de rest van het ontwerp verzwakken. Een sterke login
helpt bijvoorbeeld weinig wanneer elke besmette staff-pc de managementinterface kan
aanvallen. Een goed management VLAN helpt weinig wanneer alle beheerders hetzelfde
gedeelde account gebruiken.

### 11.1 Waarom beheer extra gevoelig is

Gewone gebruikersverkeer is belangrijk, maar beheer heeft meer macht. Wie beheerrechten heeft, kan de regels van het netwerk veranderen.

Voorbeelden:

| Beheeractie | Mogelijke impact |
|---|---|
| ACL aanpassen | zones worden te open of te strikt |
| Trunk aanpassen | VLAN's verdwijnen van paden |
| STP-priority wijzigen | verkeerspaden veranderen |
| Default route wijzigen | internetverkeer valt weg of loopt fout |
| Logging uitschakelen | incidenten worden onzichtbaar |
| AAA wijzigen | admins kunnen niet meer aanmelden |

Daarom is managementtoegang een high-value target. Een aanvaller die een gewone client overneemt, heeft beperkte macht. Een aanvaller die een netwerktoestel beheert, kan veel meer schade veroorzaken.

### 11.2 Managementtoegang heeft vier dimensies

Een secure management policy moet minstens vier vragen beantwoorden.

| Dimensie | Vraag | Voorbeeld |
|---|---|---|
| Bron | Vanwaar mag beheer starten? | alleen IT-zone of jump server |
| Doel | Welke toestellen mogen beheerd worden? | switches, routers, firewall |
| Protocol | Hoe gebeurt beheer? | SSH/HTTPS, geen Telnet/HTTP |
| Identiteit | Wie mag wat doen? | rollen en centrale authenticatie |

Als een van deze dimensies ontbreekt, blijft beheer te breed.

Slechte policy:

> Admins mogen switches beheren.

Betere policy:

> Network admins mogen via de jump server met SSH naar managementinterfaces van netwerktoestellen. Helpdesk mag alleen status bekijken. Alle aanmeldingen en wijzigingen worden gelogd.

Vier dimensies zijn het minimum. Voor een volledig ontwerp voeg je ook tijd, toestand
en bewijs toe.

| Extra dimensie | Vraag | Voorbeeld |
|---|---|---|
| Tijd | wanneer en hoelang geldt de toegang? | tijdelijk verhoogde rechten tijdens goedgekeurd onderhoud |
| Toestand | welk noodgedrag geldt bij uitval? | beperkte lokale fallback als TACACS+ onbereikbaar is |
| Bewijs | hoe toon je correct gebruik en misbruik aan? | centrale login-, commando- en changelogs met correcte tijd |

Een managementpolicy is dus niet alleen een ACL. Ze combineert netwerksegmentatie,
identiteit, autorisatie, protocollen, procedures en logging.

---

## 12. Management plane

Je kan een netwerktoestel conceptueel bekijken in drie functies:

| Plane | Doel | Voorbeeld |
|---|---|---|
| Data plane | verwerkt gebruikersverkeer | frames en pakketten doorsturen |
| Control plane | beslist over netwerkgedrag | routingprotocollen, STP |
| Management plane | laat beheer toe | SSH, HTTPS, SNMP, syslog |

Binnen de management plane hebben diensten verschillende richtingen en doelen.

| Beheerstroom | Typische richting | Doel |
|---|---|---|
| interactief beheer | beheerder of jump server naar toestel | configureren en onderzoeken via SSH/HTTPS |
| monitoring | monitoringsysteem naar toestel | status en meetwaarden ophalen |
| logging | toestel naar centrale logserver | gebeurtenissen buiten het toestel bewaren |
| tijdsynchronisatie | toestel naar of van vertrouwde tijdsbron | consistente timestamps verkrijgen |
| AAA | toestel naar centrale AAA-server | identiteit, rechten en accounting controleren |
| configuratieback-up | beheersysteem en toestel | versies veilig verzamelen en herstellen |

Niet elke stroom hoeft in beide richtingen en tussen alle systemen toegestaan te zijn.
Least privilege geldt ook voor managementverkeer.

De management plane moet strikt beschermd worden.

Slechte situatie:

> Elke client in elk VLAN kan de webinterface of SSH-service van switches bereiken.

Waarom is dit gevaarlijk?

- Aanvallers kunnen beheerinterfaces scannen.
- Zwakke accounts of fouten worden sneller misbruikt.
- Een besmet clienttoestel krijgt directe zichtbaarheid op kritieke infrastructuur.
- Beheeracties zijn moeilijker te herleiden.

Betere aanpak:

- beheerinterfaces in een management VLAN of managementzone;
- toegang alleen vanaf IT of jump server;
- geen beheer vanaf guest, staff, IoT of DMZ;
- logging van beheeracties;
- centrale authenticatie waar mogelijk;
- duidelijke rollen en wijzigingsprocedure.

### 12.1 Data plane, control plane en management plane in een storing

Het onderscheid tussen de planes helpt bij troubleshooting.

Voorbeeld:

| Symptoom | Mogelijke plane |
|---|---|
| Clients kunnen server niet bereiken. | data plane |
| OSPF-neighbor valt weg. | control plane |
| Admin kan niet meer inloggen op switch. | management plane |
| STP kiest verkeerde root bridge. | control plane |
| SSH werkt niet, maar forwarding wel. | management plane |

Dit onderscheid voorkomt verkeerde conclusies.

Voorbeeld:

> Een switch kan perfect frames blijven doorsturen terwijl SSH naar de switch niet werkt.

Dat betekent dat het dataverkeer nog kan functioneren, maar de management plane faalt. Voor beheer en herstel is dat alsnog een ernstig probleem.

### 12.2 Management plane beschermen tegen gewone zones

Managementverkeer moet niet dezelfde bereikbaarheid hebben als gewone applicaties.

| Bronzone | Managementtoegang? | Reden |
|---|---|---|
| IT | ja, gecontroleerd | beheerders hebben toegang nodig |
| Jump server | ja | centraal beheerpunt |
| Staff | nee | gewone gebruikers beheren geen infrastructuur |
| Guests | nee | laag vertrouwd |
| IoT | nee | laag vertrouwd en vaak zwak beheerbaar |
| DMZ | nee | publiek blootgestelde zone |
| Internet | nee, tenzij via specifiek beveiligd beheerontwerp | direct beheer vanaf internet vermijden |

Belangrijk:

> Het is veiliger om managementtoegang te openen voor enkele beheerbronnen dan om ze achteraf met losse denies te proberen beperken.

Een bruikbare controle combineert bereikbaarheid en toepassing:

| Test | Verwacht | Waarom test je dit? |
|---|---|---|
| IT of jump server opent SSH naar `SW-CORE` | allow | bewijst dat het noodzakelijke beheerpad bestaat |
| Staff opent SSH naar `SW-CORE` | deny | bewijst dat gewone gebruikers het beheerpad niet bereiken |
| Guest pingt of scant managementsubnet | deny of geen bruikbaar antwoord volgens beleid | controleert isolatie van een laag vertrouwde zone |
| IT bereikt een gewone servicedoelpoort op management-IP | alleen indien expliciet nodig | voorkomt dat het volledige toestel onnodig wordt blootgesteld |
| beheeractie uitvoeren | login en actie zijn terug te vinden | bewijst auditability, niet alleen bereikbaarheid |

Een ICMP-deny alleen bewijst niet dat SSH of HTTPS geblokkeerd is. Test waar mogelijk
het protocol waarop het beleid betrekking heeft.

---

## 13. Management VLAN en managementzone

Een **management VLAN** is een technisch VLAN waarin managementinterfaces geplaatst worden.

Een **managementzone** is het securityconcept dat bepaalt hoe management beschermd wordt.

| Begrip | Vraag |
|---|---|
| Management VLAN | In welk subnet zitten beheerinterfaces? |
| Managementzone | Wie mag beheerinterfaces bereiken en hoe? |

Het VLAN levert vooral Layer 2-scheiding. De zone voegt beleid en vertrouwen toe.
Daarom kunnen twee organisaties hetzelfde VLAN-nummer gebruiken en toch een totaal
ander securityniveau hebben.

Een management VLAN zonder toegangsbeperking is onvoldoende.

Slechte situatie:

| Eigenschap | Probleem |
|---|---|
| Switches hebben management-IP's in VLAN 99. | Op zich goed. |
| VLAN 99 is vanaf alle interne VLAN's bereikbaar. | Beheer is te breed. |
| Er is geen logging. | Misbruik of fouten zijn moeilijk traceerbaar. |

Betere situatie:

| Eigenschap | Voordeel |
|---|---|
| Managementinterfaces zitten in VLAN 99. | Technische scheiding. |
| Alleen IT of jump server mag naar VLAN 99. | Beperkte blootstelling. |
| Beheer gebeurt via SSH/HTTPS, niet Telnet. | Verkeer wordt beter beschermd. |
| Beheeracties worden gelogd. | Audit en incidentanalyse mogelijk. |

### 13.1 Management VLAN is niet automatisch out-of-band

Een management VLAN loopt vaak nog altijd over dezelfde switches, trunks en routers als het productienetwerk. Dat is **in-band management**.

Voorbeeld:

```text
PC-IT ---- SW-ACC ---- SW-CORE ---- VLAN 99 ---- managementinterfaces
```

Als `SW-CORE` of een kritieke trunk faalt, kan ook management onbereikbaar worden. Het management VLAN is dan wel logisch gescheiden, maar niet fysiek onafhankelijk.

Dat is niet automatisch fout. Veel organisaties gebruiken in-band management. Je moet alleen eerlijk documenteren wat het wel en niet oplost.

| Oplost | Lost niet automatisch op |
|---|---|
| management-IP's gescheiden van user-VLAN's | beheer bij core-uitval |
| eenvoudiger toegangsbeleid | fysieke onafhankelijkheid |
| duidelijker zoneschema | noodtoegang bij zware storing |

### 13.2 Routing naar management

Een veelgemaakte fout is dat managementsubnetten via normale inter-VLAN routing voor iedereen bereikbaar zijn.

Slechte situatie:

```text
Staff -> routing -> VLAN 99 management
Guests -> routing -> VLAN 99 management
IoT -> routing -> VLAN 99 management
```

Betere situatie:

```text
IT of jump server -> management
alle andere zones -> blokkeren
```

Conceptueel beleid:

| Bron | Doel | Actie |
|---|---|---|
| IT-zone | managementinterfaces SSH/HTTPS | allow |
| Jump server | managementinterfaces SSH/HTTPS | allow |
| Staff | managementinterfaces | deny |
| Guests | managementinterfaces | deny |
| IoT | managementinterfaces | deny |
| DMZ | managementinterfaces | deny |

Dit kan technisch vertaald worden naar firewallregels, router-ACL's, VTY access-lists of management policies. De syntax is minder belangrijk dan het beleid.

Defense in depth kan meerdere afdwingingspunten combineren:

| Afdwingingspunt | Wat beperkt het? | Beperking |
|---|---|---|
| firewall of routed ACL | welke bronzones het managementsubnet bereiken | een fout kan meerdere toestellen tegelijk blootstellen |
| VTY access-class | welke bronadressen interactieve CLI-toegang starten | beschermt niet automatisch webbeheer of SNMP |
| lokale serviceconfiguratie | welke beheerprotocollen op het toestel luisteren | zegt nog niet vanwaar ze bereikbaar zijn |
| hostfirewall op jump server | welke beheerflows de jump host zelf toelaat | beschermt alleen wanneer verkeer werkelijk via de jump host loopt |
| AAA-autorisatie | wat een geldige beheerder mag uitvoeren | voorkomt geen netwerkbereikbaarheid of protocolaanval |

Geen enkele laag vervangt de andere volledig. Samen verkleinen ze de kans dat één
configuratiefout onbeperkte toegang geeft.

### 13.3 Managementinterfaces beperken per toestel

Niet elk toestel hoeft op dezelfde manier beheerd te worden.

| Toesteltype | Beheerbehoefte | Extra aandacht |
|---|---|---|
| Access switch | poorten, VLAN's, trunkstatus | impact op lokale gebruikers |
| Core/distribution | centrale forwarding en routing | zeer kritisch, wijziging streng controleren |
| Router/firewall | routes, NAT, ACL/firewallbeleid | security en internetimpact |
| Server in managementzone | jump, logging of monitoring | hardening en logging |
| DMZ-host | beperkte beheerkanalen | nooit beheer vanaf internet |

Een sterke managementpolicy maakt onderscheid tussen gewone access-toestellen en kritieke core- of edgecomponenten.

### 13.4 In-band management testen zonder jezelf buiten te sluiten

Een wijziging aan VLAN 99, een trunk, een SVI, een route of een ACL kan het beheerpad
zelf verbreken. Gebruik daarom deze volgorde:

1. Teken het volledige pad van beheerbron tot managementinterface.
2. Noteer elk noodzakelijk VLAN, trunk, route- en filterpunt.
3. Bewaar de actieve configuratie van alle betrokken toestellen.
4. Zorg voor console of een ander vooraf getest noodpad.
5. Pas één afgebakende wijziging toe.
6. Test onmiddellijk de toegestane beheerbron.
7. Test daarna minstens één bron die geweigerd moet worden.
8. Controleer logging en bewaar de nieuwe baseline pas na succes.

Typische fout:

> Eerst de oude allow-regel verwijderen en pas daarna testen of de nieuwe bronregel
> correct werkt.

Bij remote beheer kan die volgorde de actieve sessie of alle volgende sessies
blokkeren. De juiste migratievolgorde is daarom onderdeel van het rollbackplan.

---

## 14. Out-of-band management

**Out-of-band management** betekent dat beheer via een apart beheerpad kan gebeuren, los van het gewone productienetwerk.

Voorbeelden:

- aparte consoleverbinding;
- aparte managementswitch;
- aparte beheernetwerkkaart;
- console server;
- cloud- of datacenter out-of-band oplossing.

Waarom is dit nuttig?

Als het productienetwerk stuk is, kan je nog steeds toestellen bereiken om het probleem op te lossen.

In Packet Tracer wordt dit meestal conceptueel behandeld. Studenten moeten vooral begrijpen:

> Als je beheertoegang volledig afhankelijk is van het netwerk dat stuk kan gaan, kan herstel veel moeilijker worden.

### 14.1 In-band versus out-of-band

| Type beheer | Pad | Voordeel | Nadeel |
|---|---|---|---|
| In-band | via het gewone netwerk | goedkoper en eenvoudiger | faalt mogelijk samen met productienetwerk |
| Out-of-band | via apart beheerpad | nuttig bij zware storing | extra infrastructuur en kost |

In een kleine onderwijsomgeving is out-of-band vaak conceptueel. In een echte enterprise-omgeving kan het verschil maken tussen snel herstel en wachten tot iemand fysiek ter plaatse is.

### 14.2 Wanneer is out-of-band belangrijk?

Out-of-band management is vooral nuttig voor:

- core switches;
- routers en firewalls aan de edge;
- datacenter- of serverrackapparatuur;
- remote sites waar niet altijd IT aanwezig is;
- toestellen die nodig zijn om VPN, internet of management te herstellen.

Voor een kleine access switch in een lokaal is out-of-band misschien overdreven. Voor een edge-firewall of core switch kan het zeer waardevol zijn.

Sterke analysezin:

> Out-of-band management is vooral belangrijk voor toestellen waarvan uitval ook het normale beheerpad kan breken.

### 14.3 Out-of-band is alleen nuttig als het zelf beheerd wordt

Een apart pad kan schijnveiligheid geven wanneer het vergeten of te breed toegankelijk
is.

| Productiecontrole | Waarom? |
|---|---|
| aparte toegangsbeperking en sterke authenticatie | OOB geeft vaak zeer krachtige consoletoegang |
| periodieke bereikbaarheidstest | een ongebruikt noodpad kan defect blijken op het moment dat het nodig is |
| onafhankelijke stroom en netwerkroute waar vereist | anders faalt OOB door dezelfde oorzaak als productie |
| logging van console- en beheersessies | noodtoegang moet ook traceerbaar blijven |
| actuele contact- en escalatieprocedure | iemand moet weten hoe en wanneer het pad gebruikt wordt |
| geen rechtstreekse brede internetblootstelling | een noodinterface mag geen permanente externe achterdeur worden |

In het lab:

> Packet Tracer toont vooral de logische managementzone. Noteer expliciet dat console
> of echt fysiek onafhankelijk OOB-beheer in de workshop een ontwerpvoorstel is, geen
> volledig geïmplementeerde productievoorziening.

---

## 15. SSH in plaats van Telnet

Telnet stuurt beheercommunicatie onversleuteld. SSH versleutelt de sessie.

| Protocol | Probleem of voordeel |
|---|---|
| Telnet | onversleuteld, niet geschikt voor professioneel beheer |
| SSH | versleuteld, standaardkeuze voor CLI-beheer |
| HTTP | onversleuteld voor webbeheer |
| HTTPS | versleuteld voor webbeheer |

Een ruimer protocoloverzicht:

| Functie | Onveilige of zwakkere keuze | Betere keuze | Belangrijke nuance |
|---|---|---|---|
| CLI-beheer | Telnet | SSH | controleer ook bronbeperking, accounts en host key |
| webbeheer | HTTP | HTTPS | een geldig en vertrouwd certificaat voorkomt verkeerde serveridentiteit |
| bestandoverdracht | TFTP of gewone FTP | SCP, SFTP of HTTPS | back-ups kunnen gevoelige configuratie bevatten |
| monitoring | SNMPv1/v2c met community string | SNMPv3 waar ondersteund | authenticatie en privacy moeten bewust geconfigureerd worden |
| automatisatie | credentials in scripts | veilige API/SSH met secretbeheer | beperk rechten en roteer credentials |

In dit OPO ligt de nadruk niet op het configureren van wachtwoorden. De belangrijke ontwerpregel is:

> Sta alleen veilige beheerprotocollen toe en beperk vanwaar ze bereikbaar zijn.

Voor Packet Tracer-configuraties in dit lesmateriaal worden geen wachtwoorden opgenomen.

### 15.1 Encryptie is nodig, maar niet genoeg

SSH is beter dan Telnet omdat de sessie versleuteld is. Maar SSH alleen maakt beheer niet automatisch veilig.

Slechte situatie:

> SSH staat aan op alle switches en is bereikbaar vanaf elk VLAN.

Waarom blijft dit risicovol?

- iedereen kan de beheerinterface bereiken;
- brute-forcepogingen of misbruik zijn makkelijker;
- een besmet clienttoestel kan netwerktoestellen aanvallen;
- logging en rollen kunnen ontbreken.

Betere aanpak:

| Maatregel | Doel |
|---|---|
| SSH/HTTPS gebruiken | beheercommunicatie beschermen |
| bronzones beperken | blootstelling verminderen |
| centrale authenticatie | accounts beheerbaar maken |
| rollen toepassen | rechten beperken |
| logging voorzien | acties traceerbaar maken |

SSH beschermt de verbinding, maar de client moet ook controleren met welk toestel hij
verbonden is. De **SSH host key** stelt de serveridentiteit voor. Een onverwachte
wijziging van die key kan een legitieme vervanging zijn, maar ook wijzen op een verkeerd
toestel of een man-in-the-middle-aanval.

Controleer:

| Controle | Waarom? |
|---|---|
| algoritmes en protocolversie | verouderde cryptografie kan de bescherming verzwakken |
| host key of certificaat | de beheerder moet het juiste doeltoestel herkennen |
| toegestane bron | versleuteling beperkt de blootstelling niet |
| individuele identiteit | een veilige tunnel met een gedeeld account blijft slecht auditeerbaar |
| autorisatie | een geldige login mag niet automatisch volledige configuratierechten geven |
| sessielogging en timeout | onbeheerde of misbruikte sessies moeten zichtbaar en begrensd zijn |

### 15.2 Onveilige beheerprotocollen herkennen

Tijdens een audit kijk je niet alleen of SSH bestaat. Je controleert ook of oude of onveilige beheerpaden nog openstaan.

Vragen:

- Is Telnet nog toegelaten?
- Is HTTP-webbeheer bereikbaar?
- Is SNMP gebruikt en zo ja, hoe wordt toegang beperkt?
- Zijn managementinterfaces vanaf gewone clientzones bereikbaar?
- Worden mislukte aanmeldingen gelogd?
- Is er een duidelijk beleid voor externe beheerverbindingen?

In dit hoofdstuk is het doel vooral conceptueel: studenten moeten kunnen uitleggen waarom een protocol of bereikbaarheid onveilig is en welk beleid beter is.

Kernzin:

> Een veilig beheerprotocol beschermt het verkeer; een secure-managementontwerp
> beschermt ook de bron, identiteit, rechten, bestemming en audittrail.

---

## 16. Lokale accounts, centrale authenticatie en AAA

In kleine netwerken worden accounts vaak lokaal op elk toestel beheerd. In enterprise-netwerken wordt dat snel onhandig en risicovol.

| Aanpak | Voordeel | Nadeel |
|---|---|---|
| Lokale accounts | eenvoudig, werkt zonder centrale server | moeilijk beheerbaar, inconsistent, lastig auditen |
| Centrale authenticatie | een plaats voor gebruikersbeheer | afhankelijk van centrale dienst |
| AAA | gestructureerd model voor toegang en logging | vraagt ontwerp en infrastructuur |

AAA staat voor:

| Letter | Betekenis | Vraag |
|---|---|---|
| Authentication | wie ben je? | Mag deze persoon aanmelden? |
| Authorization | wat mag je doen? | Welke rechten krijgt deze persoon? |
| Accounting | wat heb je gedaan? | Welke acties worden gelogd? |

Sterke enterprise-vraag:

> Kan je achteraf aantonen wie welke wijziging heeft uitgevoerd?

Een vereenvoudigde centrale AAA-flow:

```text
admin            netwerktoestel             AAA-server
  | login             |                         |
  |------------------>|                         |
  |                   | authenticatievraag     |
  |                   |------------------------>|
  |                   | identiteit + policy    |
  |                   |<------------------------|
  | commando          |                         |
  |------------------>| autorisatie/accounting |
  |                   |------------------------>|
  | resultaat         |                         |
  |<------------------|                         |
```

Het netwerktoestel is hierbij een AAA-client: het ontvangt de beheersessie en vraagt
aan de centrale dienst hoe die identiteit behandeld moet worden.

### 16.1 Waarom lokale accounts moeilijk worden

Lokale accounts lijken eenvoudig. Elk toestel heeft eigen gebruikers en rechten. Bij enkele toestellen is dat beheersbaar, maar bij tientallen toestellen ontstaan problemen.

Voorbeelden:

| Situatie | Probleem |
|---|---|
| Een beheerder vertrekt. | account moet op elk toestel verwijderd worden |
| Rechten wijzigen. | inconsistenties tussen toestellen |
| Audit vraagt wie iets deed. | gedeelde lokale accounts geven geen duidelijk antwoord |
| Wachtwoordbeleid verandert. | elk toestel moet apart aangepast worden |
| Nieuw toestel wordt geplaatst. | accounts moeten opnieuw correct ingesteld worden |

Centrale authenticatie lost niet alles op, maar maakt identiteitsbeheer consistenter.

### 16.2 AAA als denkmodel

AAA is niet alleen een protocolconfiguratie. Het is een manier van denken.

Voorbeeld:

Een network operator meldt aan op een switch.

| Stap | AAA-vraag | Mogelijk resultaat |
|---|---|---|
| 1 | Authentication | gebruiker is wie hij beweert te zijn |
| 2 | Authorization | gebruiker mag status bekijken en interfaces beheren |
| 3 | Accounting | login en uitgevoerde acties worden geregistreerd |

Zonder authorization krijgt een geldige gebruiker mogelijk te veel rechten. Zonder accounting weet je achteraf niet wat er gebeurd is.

Deze drie controles lossen elk een ander probleem op:

| AAA-onderdeel | Zonder deze controle | Sterk bewijs |
|---|---|---|
| Authentication | het toestel weet niet betrouwbaar wie aanmeldt | individuele identiteit en geslaagde of mislukte login |
| Authorization | elke geldige gebruiker kan mogelijk te veel | toegekende rol, privilege of toegelaten commando |
| Accounting | acties zijn niet aan een identiteit en tijdstip te koppelen | begin/einde sessie en relevante beheeracties |

Accounting voorkomt een foute of kwaadaardige change niet. Het verhoogt wel de kans
dat je ze snel kan verklaren en aan een change of identiteit kan koppelen.

### 16.3 Fallback bij centrale authenticatie

Centrale authenticatie introduceert een nieuwe afhankelijkheid. Wat als de AAA-server niet bereikbaar is?

Een goed ontwerp voorziet fallback, maar niet onbeperkt.

| Fallbackvraag | Waarom belangrijk? |
|---|---|
| Wie mag lokale noodtoegang gebruiken? | noodtoegang is gevoelig |
| Wanneer mag fallback gebruikt worden? | misbruik vermijden |
| Wordt fallback achteraf gelogd of gerapporteerd? | audit behouden |
| Hoe wordt toegang terug normaal gemaakt? | tijdelijke uitzonderingen opruimen |

Belangrijk:

> Fallback moet herstel mogelijk maken, maar mag geen permanente achterdeur worden.

Een belangrijk onderscheid is het verschil tussen een **timeout** en een **deny**.

| Resultaat van centrale AAA | Gewenste interpretatie |
|---|---|
| server antwoordt allow | pas de centrale autorisatie toe |
| server antwoordt deny | weiger; probeer niet automatisch een lokale achterdeur |
| server is werkelijk onbereikbaar of antwoordt niet | volg de beperkte en gedocumenteerde fallbackmethode |

Als elke expliciete weigering automatisch naar lokale authenticatie overschakelt, kan
centrale policy omzeild worden.

Een noodaccount vraagt daarom extra lifecyclebeheer:

| Controle | Praktische invulling |
|---|---|
| eigenaar | benoem wie gebruik mag goedkeuren |
| opslag | bewaar het credential gecontroleerd, niet in het cursusverslag of de configmap |
| gebruik | alleen bij vooraf bepaalde AAA- of netwerkuitval |
| detectie | genereer een alert of verplicht incidentregistratie |
| rotatie | wijzig het credential na gebruik en periodiek volgens beleid |
| test | bewijs in een onderhoudsvenster dat fallback werkt zonder normale AAA te omzeilen |

In productie:

> Voorzie waar mogelijk meerdere AAA-servers én een beperkte break-glassprocedure.
> Redundantie behandelt gewone serveruitval; break-glass behandelt uitzonderlijke
> herstelgevallen.

---

## 17. RADIUS en TACACS+ conceptueel

RADIUS en TACACS+ zijn protocollen die gebruikt worden voor centrale authenticatie en autorisatie.

| Eigenschap | RADIUS | TACACS+ |
|---|---|---|
| Veel gebruikt voor | netwerktoegang, Wi-Fi, VPN | beheer van netwerktoestellen |
| AAA-ondersteuning | authentication en accounting sterk aanwezig | scheidt authentication, authorization en accounting duidelijker |
| Typische context | gebruikers toegang geven tot netwerkdiensten | admins toegang geven tot routers en switches |

Technisch verschillen ze ook in transport en afscherming.

| Eigenschap | RADIUS | TACACS+ |
|---|---|---|
| Typisch transport | UDP, vaak 1812 voor authenticatie/autorisatie en 1813 voor accounting | TCP-poort 49 |
| Bescherming van protocolinhoud | klassieke RADIUS beschermt niet het volledige pakket; beschermend transport of netwerksegmentatie blijft belangrijk | schermt de protocolbody af met protocol-eigen obfuscatie, maar biedt op zichzelf geen moderne transportencryptie |
| Autorisatiemodel | vaak gekoppeld aan netwerktoegang en attributen | fijnmazige scheiding en commando-autorisatie zijn typische sterktes |
| Beschikbaarheid | timeouts en retries moeten bewust ingesteld zijn | TCP-sessie en serverbereikbaarheid moeten bewaakt worden |

Deze vergelijking betekent niet dat één protocol in elke situatie "veilig" en het
andere "onveilig" is. Implementatie, gedeelde secrets, transportbescherming,
bronbeperking, serverhardening en logging blijven belangrijk.

Voor dit vak moeten studenten vooral het ontwerp begrijpen:

- lokale accounts zijn vaak onvoldoende schaalbaar;
- centrale authenticatie maakt beheer consistenter;
- beheeracties moeten gelogd worden;
- fallback moet doordacht zijn als de centrale AAA-server niet bereikbaar is.

### 17.1 Waar past welk protocol?

In veel enterprise-omgevingen zie je grofweg dit onderscheid:

| Context | Vaak gebruikt |
|---|---|
| Wi-Fi-gebruikers authenticeren | RADIUS |
| VPN-gebruikers authenticeren | RADIUS |
| 802.1X-netwerktoegang | RADIUS |
| Admins op routers en switches | TACACS+ of RADIUS, afhankelijk van omgeving |

TACACS+ wordt vaak gekozen voor beheer van netwerktoestellen omdat autorisatie van beheercommando's fijnmaziger kan zijn. RADIUS is zeer breed gebruikt voor netwerktoegang.

Voor bachelorstudenten is het belangrijkste:

> RADIUS en TACACS+ zijn geen doel op zich. Ze ondersteunen een centraal en controleerbaar toegangsbeleid.

### 17.2 Centrale AAA is ook een beschikbaarheidsvraag

AAA hoort ook bij high availability.

Als de AAA-server uitvalt:

- kunnen admins mogelijk niet meer aanmelden;
- VPN- of Wi-Fi-gebruikers kunnen toegang verliezen;
- accountinglogs kunnen ontbreken;
- fallbackprocedures worden belangrijk.

Daarom stel je bij AAA ook beschikbaarheidsvragen:

| Vraag | Reden |
|---|---|
| Is er een tweede AAA-server? | centrale dienst mag geen SPOF zijn |
| Wat gebeurt er bij AAA-timeout? | admins moeten weten wat te verwachten |
| Is lokale fallback beperkt en gedocumenteerd? | noodtoegang zonder misbruik |
| Worden AAA-events gelogd? | incidentanalyse en audit |

### 17.3 AAA testen

Test niet alleen dat één administrator kan aanmelden.

| Test | Verwacht | Waarom? |
|---|---|---|
| network admin meldt centraal aan | login en toegestane beheertaak slagen | bewijst normale authenticatie en autorisatie |
| operator probeert verboden taak | taak wordt geweigerd en gelogd | bewijst least privilege |
| fout wachtwoord | login wordt geweigerd | controleert negatieve authenticatie |
| eerste AAA-server valt uit | tweede server neemt volgens ontwerp over | bewijst serverredundantie |
| alle AAA-servers zijn onbereikbaar | alleen gedocumenteerde fallback werkt | bewijst herstel zonder onbeperkte achterdeur |
| expliciet gedeactiveerd account | toegang blijft geweigerd | bewijst dat deny niet door fallback omzeild wordt |

Verzamel als bewijs zowel het resultaat op het netwerktoestel als het corresponderende
AAA- of accountingevent. Zo toon je niet alleen wat de gebruiker zag, maar ook welke
centrale beslissing genomen werd.

---

## 18. Role-based access

Niet elke beheerder heeft dezelfde rechten nodig.

Voorbeeldrollen:

| Rol | Mag wel | Mag niet |
|---|---|---|
| Helpdesk | basisstatus bekijken, poortstatus controleren | routing of securityregels wijzigen |
| Network operator | interfaces beheren, standaardcontroles uitvoeren | firewallbeleid aanpassen |
| Network admin | netwerkconfiguratie wijzigen | buiten change procedure werken |
| Security admin | policies beoordelen en goedkeuren | willekeurige operationele wijzigingen doen zonder logging |
| Auditor | logs en configuraties bekijken | wijzigingen uitvoeren |

Role-based access past het least privilege-principe toe op beheer.

Kernzin:

> Een beheeraccount mag niet automatisch alle rechten krijgen omdat het technisch gemakkelijk is.

RBAC werkt het best wanneer rechten aan rollen worden toegekend en mensen via hun
functie aan die rollen worden gekoppeld.

```text
persoon -> beheeridentiteit -> rol -> toegestane taken -> gelogde acties
```

Rechtstreeks uitzonderingen per persoon toevoegen lijkt snel, maar maakt het later
moeilijk om effectieve rechten te verklaren.

### 18.1 Rollen koppelen aan taken

Rollen werken alleen als ze gekoppeld zijn aan echte taken.

Voorbeelden:

| Taak | Geschikte rol |
|---|---|
| Controleren of een poort up is | Helpdesk of operator |
| VLAN op accesspoort aanpassen | Network operator of admin |
| OSPF-configuratie wijzigen | Network admin |
| Firewallregel goedkeuren | Security admin |
| Logs bekijken na incident | Security admin of auditor |
| Configuratieback-up valideren | Network admin of auditor |

Een rol die "mag alles" betekent, is eigenlijk geen rolmodel. Dan is er geen least privilege.

### 18.2 Scheiding van taken

In grotere organisaties wil je soms dat dezelfde persoon niet alles alleen kan beslissen en uitvoeren.

Voorbeeld:

| Stap | Rol |
|---|---|
| Change aanvragen | network admin |
| Securityimpact beoordelen | security admin |
| Change uitvoeren | network admin |
| Resultaat controleren | operator of auditor |

Voor dit OPO hoeft dit niet bureaucratisch te worden. De les is dat beheeracties controleerbaar en verantwoord moeten zijn.

Scheiding van taken is vooral relevant bij acties met hoge impact:

| Actie | Mogelijke scheiding | Risico dat je beperkt |
|---|---|---|
| firewallregel voor internet publiceren | één persoon vraagt aan, een andere beoordeelt | ongecontroleerde externe blootstelling |
| privileged rol toekennen | eigenaar vraagt aan, security keurt goed | stille rechtenuitbreiding |
| logretentie wijzigen | beheerder voert uit, auditor controleert | sporen verwijderen of te kort bewaren |
| disaster-recoverytest | operator herstelt, eigenaar valideert dienst | technisch herstel zonder zakelijke validatie |

### 18.3 Tijdelijke rechten

Soms heeft iemand tijdelijk extra rechten nodig, bijvoorbeeld tijdens een incident. Ook dat hoort gecontroleerd te gebeuren.

Vragen:

- Wie keurt tijdelijke rechten goed?
- Hoelang blijven ze actief?
- Worden acties extra gelogd?
- Worden de rechten achteraf weer ingetrokken?

Zonder opruimproces worden tijdelijke rechten vaak permanente risico's.

Sterke tijdelijke toegang is **just in time** en **time-bound**: ze wordt alleen voor
een concrete taak geactiveerd en vervalt automatisch of wordt aantoonbaar ingetrokken.

Controleer na afloop:

- is de tijdelijke rol verdwenen?
- zijn actieve privileged sessies beëindigd?
- zijn de uitgevoerde acties aan de change of het incident gekoppeld?
- bestaat er een uitzondering die bij de volgende review opnieuw beoordeeld moet worden?

### 18.4 Persoonlijk beheeraccount versus dagelijks account

Een beheerder gebruikt bij voorkeur niet dezelfde identiteit voor e-mail, browsen en
kritieke netwerkchanges.

| Accounttype | Doel | Waarom scheiden? |
|---|---|---|
| dagelijks account | gewone communicatie en applicaties | wordt vaker blootgesteld aan phishing en webinhoud |
| persoonlijk beheeraccount | beheer via gecontroleerd pad | rechten en logging zijn duidelijk aan één persoon gekoppeld |
| service account | automatisatie met beperkt technisch doel | lifecycle volgt de integratie, niet een medewerker |
| break-glassaccount | uitzonderlijk noodherstel | gebruik moet zeldzaam, beschermd en opvallend zijn |

Een persoonlijk beheeraccount mag niet gedeeld worden. Anders verliest accounting zijn
belangrijkste waarde: acties betrouwbaar aan een individuele identiteit koppelen.

---

## 19. Jump server

Een **jump server** is een beheersysteem van waaruit admins naar andere systemen of netwerktoestellen verbinden.

Conceptueel:

```text
+-----------+        +-------------+        +----------------+
| IT-admin | -----> | Jump server | -----> | Managementzone |
+-----------+        +-------------+        +----------------+
```

Voordelen:

- managementinterfaces zijn niet breed bereikbaar;
- beheer gebeurt vanaf een gecontroleerd systeem;
- logging kan centraal gebeuren;
- toegang van externe of minder vertrouwde zones wordt beperkt;
- MFA of extra controles kunnen op de jump server afgedwongen worden.

Belangrijk:

Een jump server is geen excuus om alles open te zetten. De jump server zelf wordt een kritisch systeem en moet dus sterk beschermd worden.

### 19.1 Wat lost een jump server op?

Zonder jump server:

```text
+------------------------+
| IT-laptop              |
| Staff-pc               +----> managementinterfaces
| andere interne clients |
+------------------------+
```

Met jump server:

```text
IT-laptop ----> jump server ----> managementinterfaces
```

Het doel is niet dat beheer magisch veilig wordt. Het doel is dat je het aantal plaatsen vanwaar beheer kan starten sterk beperkt.

Voordelen:

| Voordeel | Uitleg |
|---|---|
| Minder blootstelling | netwerktoestellen hoeven niet bereikbaar te zijn vanaf alle IT-toestellen |
| Centrale logging | beheeracties kunnen beter verzameld worden |
| Sterkere controle | MFA, sessiebeleid of extra monitoring mogelijk |
| Eenvoudiger firewallbeleid | alleen jump server naar managementzone toelaten |

Een jump server kan ook het verschil afdwingen tussen het gewone werkpad en het
beheerpad:

```text
dagelijks toestel --sterke login--> jump server --beperkte beheerflow--> netwerktoestel
```

In strengere omgevingen wordt daarnaast een **privileged access workstation** gebruikt:
een speciaal beheertoestel waarop geen gewone e-mail, vrije webbrowser of onnodige
software draait. Een jump server centraliseert het doorgangspunt; een privileged
workstation verlaagt het risico aan de kant van het beheertoestel. Ze lossen dus niet
precies hetzelfde probleem op.

### 19.2 Nieuwe risico's van een jump server

Een jump server wordt zelf een kritiek doelwit.

Risico's:

- als de jump server gecompromitteerd wordt, krijgt een aanvaller beheerpad naar veel toestellen;
- als de jump server uitvalt, kan beheer moeilijker worden;
- als logging op de jump server faalt, verlies je auditinformatie;
- als te veel gebruikers toegang krijgen, verschuift het probleem.

Daarom moet de jump server:

- sterk beperkt bereikbaar zijn;
- goed gepatcht en gemonitord worden;
- gelogd worden;
- in een geschikte managementzone staan;
- een nood- of fallbackprocedure hebben.

Sterke conclusie:

> Een jump server vermindert brede managementblootstelling, maar verhoogt het belang van goede beveiliging en beschikbaarheid van die ene beheerschakel.

### 19.3 Jump-serverbeleid testen

| Test | Verwacht | Bewijs |
|---|---|---|
| IT-beheerder bereikt jump server | allow met vereiste authenticatie | login- of MFA-event |
| gewone staffgebruiker bereikt jump server | deny | netwerk- of authenticatielog |
| jump server bereikt management-SSH | allow | succesvolle sessie plus toestellog |
| IT-laptop gaat rechtstreeks naar management-SSH | deny als beleid de jump server verplicht | mislukte verbinding en eventueel firewalllog |
| jump server probeert onnodige client- of internetflow | deny of strikt beperkt | regel- en logcontrole |
| beheeractie via jump server | herleidbaar tot individuele beheerder | jump-, AAA- en toestellogs met overeenkomende tijd |

Let op: als alle sessies op het netwerktoestel alleen de identiteit van de jump server
tonen, is de audittrail onvolledig. De keten moet de menselijke identiteit behouden of
via gecorreleerde logs aantoonbaar maken.

---

## 20. Logging van beheeracties

Logging is belangrijk voor:

| Doel | Wat levert logging op? |
|---|---|
| troubleshooting | een tijdlijn van interfaces, protocollen, fouten en beheeracties |
| audit | bewijs dat toegang en changes aan identiteit en beleid gekoppeld zijn |
| incident response | context over bron, doel, tijdstip en gevolg van mogelijk misbruik |
| change management | vergelijking tussen geplande wijziging en werkelijk gedrag |
| detectie | zichtbaarheid op mislukte logins, onverwachte rechten en kritieke configuratieacties |

Voor beheer wil je minstens weten:

| Vraag | Voorbeeld |
|---|---|
| Wie heeft aangemeld? | adminaccount of centrale identiteit |
| Waarvandaan? | bron-IP of jump server |
| Op welk toestel? | switch, router, firewall |
| Wanneer? | datum en tijd |
| Wat is gewijzigd? | configuratiefragment of change-id |
| Was de wijziging goedgekeurd? | koppeling met change request |

Zonder logging kan een organisatie vaak niet onderscheiden:

- een menselijke fout;
- een mislukte wijziging;
- misbruik van een account;
- een technisch defect.

Kernidee:

> Logs zijn pas auditbewijs wanneer ze voldoende context bevatten, betrouwbaar
> getimestamped zijn, buiten het beheerde toestel bewaard worden en tegen ongewenste
> wijziging beschermd zijn.

### 20.1 Welke logs zijn nuttig?

Voor secure management kijk je naar verschillende soorten logs.

| Logtype | Voorbeeldvraag |
|---|---|
| Authenticatielogs | Wie heeft aangemeld en wanneer? |
| Autorisatielogs | Welke rechten kreeg de gebruiker? |
| Configuratielogs | Welke commando's of wijzigingen zijn uitgevoerd? |
| Syslog van netwerktoestellen | Welke interfaces, routingevents of errors traden op? |
| Jump server-logs | Welke sessies liepen via de jump server? |
| Change logs | Welke wijziging was gepland en goedgekeurd? |

Niet elk systeem toont al deze informatie even uitgebreid. In dit vak gaat het vooral om de vraag welke informatie je nodig hebt voor troubleshooting en audit.

Combineer bronnen om een beheerketen te reconstrueren:

```text
change-id
   |
jump-login -> AAA-beslissing -> toestelsessie -> configwijziging -> service-impact
```

| Onderzoeksvraag | Primaire bron | Ondersteunende bron |
|---|---|---|
| Wie startte de sessie? | AAA- of jumpserverlog | bronadres op het toestel |
| Wat mocht die persoon doen? | autorisatie-event | rollenconfiguratie |
| Wat veranderde? | commando-accounting of configdiff | change-notitie |
| Welk technisch gevolg trad op? | syslog, routing- of interfacelog | monitoringmeting |
| Was het gepland? | changeplatform of onderhoudsvoorstel | uitvoerder en tijdvenster |

### 20.2 Tijd is belangrijk

Logs zijn pas bruikbaar als tijdstippen kloppen. Als elk toestel een andere tijd heeft, wordt incidentanalyse moeilijk.

Voorbeeld:

| Toestel | Logtijd | Probleem |
|---|---|---|
| Firewall | 10:04 | blokkeert verkeer |
| Switch | 09:58 | interface gaat down |
| AAA-server | 10:12 | admin login |

Als tijden niet gesynchroniseerd zijn, weet je niet zeker wat eerst gebeurde.

Conceptueel hoort daarom ook tijdsynchronisatie bij professioneel beheer, bijvoorbeeld via NTP. In Packet Tracer kan je dit conceptueel benoemen zonder uitgebreid te configureren.

Tijd zelf is ook een afhankelijkheid. Gebruik meerdere vertrouwde tijdsbronnen waar de
omgeving dat vereist en beperk wie tijd mag beïnvloeden. Een foutieve tijd kan niet
alleen analyse verstoren, maar ook certificaten, tokens en centrale authenticatie doen
falen.

### 20.3 Logs moeten gelezen worden

Logging aanzetten is niet genoeg. Iemand moet logs kunnen gebruiken.

Vragen:

- Welke gebeurtenissen veroorzaken een alert?
- Wie bekijkt de logs?
- Hoe lang worden logs bewaard?
- Zijn logs beschermd tegen wijziging?
- Worden logs gekoppeld aan changes of incidenten?

Een log die niemand bekijkt, helpt vaak pas achteraf. Monitoring en alerting komen later in het OPO uitgebreider terug, maar hier is de koppeling met beheer al belangrijk.

### 20.4 Van logregel naar bruikbaar bewijs

Een screenshot met één losse logregel is vaak onvoldoende. Noteer bij een test:

| Veld | Voorbeeld |
|---|---|
| Test-id | `MGMT-DENY-02` |
| Verwachting | Staff mag geen SSH naar management starten |
| Tijdstip | begin en einde van de test |
| Bronidentiteit en bron-IP | testgebruiker op `PC-STAFF` |
| Doel | management-IP van `SW-CORE`, TCP/22 |
| Clientresultaat | verbinding faalt |
| Controlepunt | ACL- of firewalllog toont deny voor dezelfde flow |
| Conclusie | netwerkbeleid blokkeert de verboden beheerflow |

Verwijder of maskeer wachtwoorden, gedeelde secrets, private keys en volledige
configuratieexports uit in te dienen bewijsmateriaal.

---

## 21. Change management

**Change management** is het proces waarmee wijzigingen gecontroleerd gebeuren.

Een eenvoudige change bevat:

| Onderdeel | Vraag |
|---|---|
| Reden | Waarom is de wijziging nodig? |
| Scope | Welke toestellen, VLAN's of zones worden geraakt? |
| Risico | Wat kan fout lopen? |
| Back-up | Is de huidige configuratie bewaard? |
| Testplan | Hoe bewijzen we dat het werkt? |
| Rollback | Hoe keren we terug? |
| Communicatie | Wie moet op de hoogte zijn? |
| Resultaat | Wat is na afloop vastgesteld? |

Change management hoeft in een labo niet zwaar of bureaucratisch te zijn. Het doel is dat studenten niet zomaar trial-and-error toepassen op kritieke infrastructuur.

Kernzin:

> Een professionele wijziging heeft vooraf een doel, risicoanalyse, testplan en rollbackpad.

Een compacte lifecycle:

```text
aanvragen -> beoordelen -> voorbereiden -> uitvoeren -> valideren -> afsluiten
```

| Fase | Belangrijk resultaat |
|---|---|
| Aanvragen | zakelijke reden, eigenaar en gewenste uitkomst zijn duidelijk |
| Beoordelen | impact, afhankelijkheden, conflicten en securityrisico zijn gekend |
| Voorbereiden | commando's, baseline, testplan, communicatie en rollback zijn klaar |
| Uitvoeren | wijziging gebeurt gecontroleerd binnen de afgesproken scope |
| Valideren | positieve, negatieve, beheer- en loggingtests zijn uitgevoerd |
| Afsluiten | werkelijke uitkomst, afwijkingen en nieuwe baseline zijn vastgelegd |

### 21.1 Kleine changes kunnen grote impact hebben

Netwerkchanges lijken soms klein omdat ze uit weinig regels bestaan.

Voorbeelden:

| Kleine wijziging | Mogelijke grote impact |
|---|---|
| VLAN uit trunk verwijderen | server- of managementzone verdwijnt |
| ACL-regel hoger plaatsen | verkeer wordt onverwacht geblokkeerd of toegelaten |
| STP-priority aanpassen | forwardingpad verandert |
| Default route wijzigen | internetverkeer valt weg |
| AAA-server aanpassen | admins kunnen niet meer aanmelden |
| Loggingbestemming wijzigen | incidentinformatie verdwijnt |

Daarom beoordeel je een change niet op het aantal commando's, maar op de impact van wat ze doet.

### 21.2 Voor en na vergelijken

Bij een change hoort een voor- en nacontrole.

| Moment | Controle |
|---|---|
| Vooraf | huidige status, back-up, verwachte paden, bereikbaarheid |
| Tijdens | onmiddellijke fouten, logging, sessies |
| Na afloop | kritieke flows, managementtoegang, logs, documentatie |

Voorbeeld:

Voor een management-ACL wijziging test je vooraf:

- IT naar management werkt;
- Staff naar management werkt mogelijk nog, als beginsituatie fout is;
- huidige ACL of policy is bewaard.

Na de wijziging test je:

- IT naar management werkt nog;
- Staff, Guests, IoT en DMZ naar management falen;
- logs tonen de beheeractie;
- rollback is niet nodig.

Gebruik dezelfde tests vóór en na de change waar dat logisch is. Zo kan je een verschil
aan de wijziging koppelen in plaats van aan een reeds bestaand probleem.

| Testcategorie | Voor de change | Na de change |
|---|---|---|
| toegestane gebruikersflow | baseline werkt | blijft werken |
| verboden flow | huidige fout of bestaande deny is gekend | gewenst deny-resultaat |
| managementpad | beheerbron bereikt alle betrokken toestellen | beheer blijft beschikbaar |
| control plane | verwachte STP-, HSRP- of routestatus | nieuwe verwachte status |
| logging | relevante bronnen ontvangen events | change en testevents zijn zichtbaar |

### 21.3 Change documentatie

Een korte change-notitie kan veel problemen voorkomen.

Minimaal:

| Veld | Inhoud |
|---|---|
| Datum | wanneer uitgevoerd |
| Uitvoerder | wie voerde uit |
| Doel | waarom nodig |
| Toestellen | welke componenten |
| Voorafcontrole | toestand voor wijziging |
| Wijziging | wat is aangepast |
| Testresultaat | wat werkte na afloop |
| Rollback | uitgevoerd of niet nodig |
| Opmerking | incidenten of afwijkingen |

Dit hoeft niet lang te zijn. Het moet wel later begrijpelijk zijn.

### 21.4 Configuratiedrift

**Configuratiedrift** betekent dat de werkelijke toestelconfiguratie geleidelijk afwijkt
van de goedgekeurde baseline.

Oorzaken:

| Oorzaak | Voorbeeld | Gevolg |
|---|---|---|
| noodwijziging niet verwerkt | tijdelijke allow-regel blijft bestaan | securitybeleid wordt ongemerkt ruimer |
| lokale handmatige change | poortconfiguratie wijkt af van documentatie | herstel en troubleshooting worden onzeker |
| gedeeltelijke uitrol | één switch mist een management-ACL | inconsistent beveiligingsniveau |
| restore van oude back-up | recente routes of VLAN's verdwijnen | technisch herstel brengt een functionele fout terug |

Periodieke configuratievergelijking helpt drift zichtbaar maken. Het doel is niet elke
tekstuele afwijking automatisch afkeuren, maar elke betekenisvolle afwijking kunnen
verklaren en goedkeuren.

Kernzin:

> De laatste running-config is niet automatisch de gewenste baseline; de gewenste
> baseline is de geteste en goedgekeurde toestand.

---

## 22. Typische fouten

| Fout | Waarom problematisch? | Betere aanpak |
|---|---|---|
| Redundantie tekenen maar niet testen | failover is niet bewezen | failovertest uitvoeren en documenteren |
| Alle beheerinterfaces bereikbaar vanuit staff | te brede aanvalsvector | alleen IT of jump server toelaten |
| Management VLAN zonder filtering | technische scheiding zonder beleid | managementzone afdwingen |
| Telnet of HTTP toestaan | onveilige beheerprotocollen | SSH/HTTPS gebruiken |
| Geen configuratieback-ups | herstel wordt traag en onzeker | back-upprocedure voorzien |
| Geen rollbackplan | mislukte wijziging blijft langer impact hebben | rollbacktrigger en actie bepalen |
| Iedereen adminrechten geven | geen least privilege | rollen definiëren |
| Geen logging van beheeracties | audit en incidentanalyse moeilijk | centrale logs of change log |
| Single internetverbinding voor kritieke cloudtoegang | cloudprocessen vallen weg bij lijnstoring | tweede verbinding of noodprocedure |
| Geen RTO/RPO-denken | prioriteiten blijven vaag | hersteldoelen koppelen aan bedrijfsimpact |
| Twee componenten in hetzelfde foutdomein | één oorzaak schakelt beide alternatieven uit | fysieke, logische en organisatorische onafhankelijkheid beoordelen |
| Alleen protocolstatus na failover controleren | gebruikersdienst kan nog steeds falen | control plane én echte serviceflow testen |
| Running-config niet als nieuwe baseline bewaren | reboot of restore brengt een andere toestand terug | running-, startup- en goedgekeurde back-up vergelijken |
| AAA-deny laat lokale fallback toe | centrale blokkering kan omzeild worden | fallback alleen bij echte onbereikbaarheid en gecontroleerde noodprocedure |
| Jump server zonder individuele herleidbaarheid | alle acties lijken van hetzelfde systeem te komen | identiteit doorgeven of logs betrouwbaar correleren |
| Logs alleen lokaal bewaren | aanvaller, defect of reset verwijdert het bewijs | centrale, beschermde logverzameling |

### 22.1 Hoe herken je deze fouten in een audit?

Tijdens een audit herken je fouten niet alleen door naar configuratie te kijken. Je combineert topologie, configuratie, testen en vragen aan beheerders.

| Fouttype | Hoe herken je het? |
|---|---|
| Redundantie niet getest | niemand kan testresultaten of failovergedrag tonen |
| Management te breed bereikbaar | pings, SSH of HTTPS naar management werken vanuit gewone clientzones |
| Geen rollback | er is geen vorige config of geen criterium om terug te keren |
| Geen rollenmodel | iedereen gebruikt hetzelfde type adminrechten |
| Geen logging | aanmeldingen of wijzigingen zijn achteraf niet terug te vinden |
| Geen RTO/RPO | herstelprioriteiten worden pas tijdens incident beslist |
| Gemeenschappelijk foutdomein | beide alternatieven delen stroom, pad, platform of beheeraccount |
| AAA-fallback te breed | een gedeactiveerd account kan via lokaal pad toch aanmelden |
| Configuratiedrift | running-config verschilt zonder verklaarde change van de baseline |
| Onvolledige audittrail | login is zichtbaar, maar rol, commando of change-id ontbreekt |

Een goede auditor schrijft niet alleen op dat iets fout is, maar ook hoe dat zichtbaar werd.

Voorbeeld:

> `PC-STAFF` kan de management-IP's van `SW-CORE` en `SW-ACC1` bereiken. Daardoor is het managementnetwerk niet beperkt tot IT of jump server. Dit verhoogt het risico dat een besmet clienttoestel beheerinterfaces aanvalt.

### 22.2 Typische denkfouten

Naast technische fouten bestaan er denkfouten.

| Denkfout | Waarom fout? |
|---|---|
| "Er zijn twee kabels, dus het is redundant." | VLAN's, STP, gateway en routing moeten ook kloppen. |
| "SSH staat aan, dus beheer is veilig." | Bereikbaarheid, rollen en logging zijn ook nodig. |
| "We hebben een back-up." | Back-up moet recent, volledig en herstelbaar zijn. |
| "Rollback is gewoon undo doen." | Rollback vraagt vooraf vastgelegde configuratie en testcriteria. |
| "Management kan via het gewone netwerk, dus dat is genoeg." | Bij storing kan dat gewone netwerk net het probleem zijn. |
| "RTO/RPO is alleen voor servers." | Netwerk en management hebben ook hersteldoelen. |
| "De standby-status bewijst dat de dienst redundant is." | Protocolstatus bewijst niet dat routing, policy en applicatieflow via het alternatief werken. |
| "Een apart VLAN is een aparte beheerzone." | Een zone vereist ook routingbeleid, bronbeperking, identiteit en logging. |
| "Centrale AAA vervangt lokale noodtoegang." | Centrale AAA kan zelf uitvallen; beperkte en gecontroleerde fallback blijft nodig. |
| "Meer logs is altijd beter." | Zonder context, correcte tijd, bescherming en opvolging ontstaat vooral ruis. |

Studenten moeten leren deze denkfouten te benoemen in professionele taal. Dat is sterker dan alleen "dit is slecht" schrijven.

---

## 23. Van theorie naar workshopaudit

In de workshop krijg je geen volledig redundant productieontwerp. Je onderzoekt een
bewust onvolmaakte Packet Tracer-omgeving van BluePeak Services. Gebruik de theorie om
van technische observaties naar verdedigbare conclusies te gaan.

Een sterke audit volgt deze keten:

```text
asset of proces
      |
afhankelijkheid
      |
storing of dreiging
      |
technische observatie
      |
bedrijfsimpact
      |
maatregel + test + prioriteit
```

Voorbeeld:

| Stap | Zwakke formulering | Sterke formulering |
|---|---|---|
| Observatie | `SW-ACC2` heeft één kabel | `SW-ACC2` heeft één actieve uplink naar `SW-CORE` en geen alternatief pad |
| Impact | dat is niet redundant | uitval van de uplink onderbreekt alle zones achter `SW-ACC2` |
| Bewijs | te zien op schema | topologie plus `show interfaces trunk` tonen slechts één bruikbare trunk |
| Verbetering | voeg een kabel toe | voeg een onafhankelijk tweede uplinkpad toe met bewust STP- of EtherChannelontwerp |
| Test | ping uitvoeren | meet serviceflow, padstatus, convergentietijd, logevent en failback |

### 23.1 Minimale bewijsset

| Auditonderdeel | Observatie of bewijs | Gewenste conclusie |
|---|---|---|
| Topologie | schema met access, core, edge, zones en management | kritieke afhankelijkheden zijn zichtbaar |
| SPOF | component plus getroffen dienst of zone | impact en prioriteit zijn gemotiveerd |
| Redundantie | fysieke paden en relevante `show`-output | exact één storingsscenario is aantoonbaar opgevangen |
| Failover | baseline, foutinjectie, herstelmeting en nieuwe status | werking is bewezen en beperking van de test is benoemd |
| Management allow | IT of jump server bereikt vereiste beheerprotocol | noodzakelijk beheer blijft mogelijk |
| Management deny | Staff, Guests, IoT of DMZ bereikt beheer niet | securitygrens wordt werkelijk afgedwongen |
| Rollen | taak-per-rolmatrix | least privilege is concreet vertaald |
| Back-up | versie, locatie, bescherming en restore-aanpak | herstel is meer dan een bestaand bestand |
| Rollback | trigger, actie, noodpad en nacontrole | mislukte change kan begrensd worden |
| DR | RTO, RPO, herstelvolgorde en voorwaarden | doel past bij bedrijfsimpact en beschikbare middelen |

### 23.2 Een testmatrix voor BluePeak

Pas adressen en toestelnamen aan de gekregen topologie aan.

| Test | Actie | Verwacht | Waarom test je dit? | Sterk bewijs |
|---|---|---|---|---|
| Baseline serverflow | client opent of bereikt interne server | allow | bevestigt geldige beginsituatie | clientresultaat plus route- of interfacecontrole |
| Uplinkuitval | schakel gekozen primaire uplink uit | alternatief pad neemt over, of gedocumenteerde outage als er geen redundantie is | toont werkelijke beschikbaarheid van accesspad | pings/verkeer plus STP- of EtherChannelstatus voor en na |
| Gatewayuitval | maak actieve gateway gecontroleerd onbeschikbaar | standby wordt active als voorzien | test first-hop redundancy | `show standby` plus inter-VLAN gebruikersflow |
| Management allow | IT/jump opent SSH naar managementinterface | allow | bewijst noodzakelijke beheerbaarheid | sessie plus loginlog |
| Management deny | Staff opent SSH naar hetzelfde doel | deny | bewijst zonegrens | foutresultaat plus ACL/firewalllog waar mogelijk |
| Onveilig protocol | controleer of Telnet/HTTP luistert | deny of uitgeschakeld | zoekt achterblijvend beheerpad | configuratie- en verbindingstest |
| Rollback | simuleer of beschrijf mislukte trunk- of ACL-change | vorige bekende toestand binnen doeltermijn | bewijst herstelbaarheid van change | configdiff en geslaagde nacontroles |
| Back-uprestore | laad representatieve config in veilige omgeving | kritieke functies komen terug | bewijst bruikbaarheid, niet alleen aanwezigheid | restorelog en functionele testresultaten |

### 23.3 Van bevinding naar prioriteit

Een verbeterpunt krijgt niet alleen een technische oplossing, maar ook een prioriteit.

| Factor | Vraag |
|---|---|
| Impact | hoeveel gebruikers, zones of kritieke processen worden geraakt? |
| Waarschijnlijkheid | hoe realistisch is de storing of het misbruik? |
| Herstelbaarheid | kan IT het probleem snel detecteren en herstellen? |
| Afhankelijkheid | blokkeert dit probleem ook andere herstelacties? |
| Bewijs | is het risico waargenomen, getest of alleen vermoed? |
| Inspanning | kan een kleine, veilige maatregel veel risico wegnemen? |

Voorbeeld van een hoge prioriteit:

> Managementinterfaces zijn via SSH bereikbaar vanuit Staff. Een besmet clienttoestel
> kan daardoor kritieke infrastructuur rechtstreeks benaderen. Beperk management tot
> IT of de jump server, behoud consoletoegang tijdens de change en bewijs zowel de
> toegestane als geweigerde flow.

## 24. Labkeuzes en productieontwerp

Packet Tracer maakt netwerkgedrag zichtbaar, maar simuleert niet elk productieaspect.
Een sterke student benoemt daarom welke conclusie wel en niet uit het lab volgt.

| Thema | In de workshop | In productie |
|---|---|---|
| Redundantie | beperkte topologie en enkele foutscenario's | onafhankelijke stroom, racks, kabelroutes, providers en locaties beoordelen |
| Failover | ping en `show`-commando's maken convergentie zichtbaar | echte applicaties, stateful sessies, monitoring en gebruikersimpact testen |
| Managementzone | VLAN, routing en ACL's modelleren de grens | firewalls, bastion/jump, hardened beheertoestellen en OOB combineren |
| Authenticatie | vaak conceptueel en zonder meegeleverde secrets | redundante AAA, sterke MFA waar passend, individuele accounts en gecontroleerde fallback |
| Logging | beperkte simulatoroutput of testnotitie | centrale verzameling, tijdsynchronisatie, retentie, bescherming en alerts |
| Back-up | running-config exporteren en vergelijken | geautomatiseerde versies, encryptie, toegangscontrole en periodieke restore-oefening |
| Rollback | commando's of vorige config in veilige topologie | platformfuncties, console/noodpad, eigenaarschap en harde tijdscriteria |
| DR | mini-plan met RTO/RPO | middelen, leveranciers, locaties, mensen en volledige oefeningen koppelen |

Labvereenvoudiging:

> Dat Packet Tracer een mechanisme niet volledig simuleert, betekent niet dat het
> productievereiste verdwijnt. Beschrijf het als beperking en leg uit hoe je het in een
> echte omgeving zou controleren.

## 25. Controlevragen en denkvragen

### 25.1 Begripscontrole

1. Waarom is high availability niet hetzelfde als "er zijn twee toestellen"?
2. Wat is het verschil tussen redundantie, failover en load balancing?
3. Wat bedoelen we met degraded mode en waarom moet die toestand zichtbaar zijn?
4. Wat is een foutdomein? Geef een voorbeeld van een common-mode failure.
5. Waarom bewijst een active standby-status niet dat de volledige dienst beschikbaar is?
6. Wat is het verschil tussen failover en failback?
7. Wat meten RTO en RPO elk?
8. Waarom is een management VLAN niet automatisch een veilige managementzone?
9. Welke drie vragen beantwoorden authentication, authorization en accounting?
10. Waarom mag een expliciete AAA-deny niet zomaar lokale fallback activeren?
11. Welk probleem lost een jump server op en welk nieuw risico creëert die?
12. Waarom zijn correcte tijd en centrale opslag belangrijk voor logs?

### 25.2 Toepassingsvragen

1. Twee uplinks van een access switch eindigen op dezelfde core switch. Tegen welke
   storing beschermt dit ontwerp wel en tegen welke niet?
2. Na HSRP-failover is de standby-router active, maar de finance-app werkt niet. Welke
   controles voer je uit voordat je concludeert dat HSRP faalde?
3. Een beheerder wil een management-ACL remote aanpassen. Welk noodpad, welke baseline,
   welke allow-test en welke deny-test zijn vooraf nodig?
4. De AAA-server is bereikbaar en weigert een vertrokken medewerker. Het toestel biedt
   daarna een lokaal loginpad aan. Waarom is dat een ontwerpfout?
5. Een configuratieback-up is van gisteren, maar niemand weet welke softwareversie het
   vervangtoestel gebruikt. Welk herstelrisico blijft bestaan?
6. Alle beheer loopt via één jump server. Welke beschikbaarheids- en securitymaatregelen
   horen bij die keuze?
7. BluePeak kiest een RTO van 15 minuten voor de core, maar heeft geen reservehardware
   of OOB-toegang. Hoe formuleer je dit als professionele auditbevinding?
8. Een failovertest toont nul verloren pings. Welk extra bewijs heb je nodig om uit te
   sluiten dat het verkeer nooit via het bedoelde primaire pad liep?

### 25.3 Criteria voor een sterk antwoord

Een sterk antwoord:

| Criterium | Wat verwacht je? |
|---|---|
| Conceptueel juist | begrippen zoals SPOF, failover, RTO, managementzone en AAA worden correct gebruikt |
| Scenario-gebonden | toestellen, zones en bedrijfsprocessen uit BluePeak worden concreet benoemd |
| Oorzaak en gevolg | technische observatie wordt gekoppeld aan gebruikers- of herstelimpact |
| Toetsbaar | er staat welke positieve en negatieve test de bewering bewijst |
| Begrensd | het antwoord zegt ook wat de test of maatregel niet oplost |
| Herstelbaar | back-up, rollback, fallback of noodpad is voorzien waar relevant |
| Professioneel | prioriteit en advies zijn gemotiveerd zonder vage termen zoals "beter beveiligen" |

## 26. Samenvatting

High availability en secure management gaan samen over controle.

Studenten moeten vooral onthouden:

- een single point of failure is alleen aanvaardbaar als de impact bewust gekozen is;
- redundante componenten moeten ook buiten hetzelfde relevante foutdomein liggen;
- failover is pas bewezen met een baseline, foutinjectie, control-planecontrole,
  gebruikersflow en gecontroleerde failback;
- technische protocolstatus is niet hetzelfde als beschikbaarheid van de volledige dienst;
- configuratieback-ups, restore-tests en rollback zijn deel van beschikbaarheid;
- RTO en RPO koppelen technische herstelkeuzes aan bedrijfsimpact en beschikbare middelen;
- managementtoegang is gevoeliger dan gewone netwerktoegang;
- een management VLAN is niet genoeg zonder bronbeperking, rollen en logging;
- SSH/HTTPS beschermen het verkeer, maar vervangen geen volledig managementbeleid;
- centrale authenticatie en AAA maken beheer schaalbaarder en controleerbaarder als
  redundantie en beperkte fallback voorzien zijn;
- role-based access past least privilege toe op admins;
- jump servers beperken het beheerpad, maar worden zelf kritieke infrastructuur;
- centrale logs, correcte tijd en change management maken wijzigingen traceerbaar;
- positieve én negatieve tests zijn nodig om een managementpolicy te bewijzen.

Kernzin:

> Een enterprise-netwerk is pas professioneel beheerbaar wanneer uitval, beheer en herstel niet afhangen van geluk, losse kennis of trial-and-error.

### 26.1 Rode draad van het hoofdstuk

De rode draad van dit hoofdstuk is:

```text
ontwerp -> risico -> impact -> test -> procedure -> documentatie
```

Je vertrekt dus niet van losse commando's. Je vertrekt van de vraag wat er mis kan gaan en wat de impact is. Daarna bepaal je hoe je dat risico beperkt, hoe je bewijst dat je oplossing werkt en hoe je handelt als er toch iets fout loopt.

Voor high availability betekent dit:

- single points of failure zoeken;
- redundantie bewust ontwerpen;
- failover testen;
- degraded mode begrijpen;
- hersteldoelen bepalen.

Voor secure management betekent dit:

- managementinterfaces afschermen;
- veilige beheerprotocollen gebruiken;
- beheerbronnen beperken;
- rollen en AAA gebruiken;
- logging en change management voorzien;
- rollback en noodtoegang voorbereiden.

### 26.2 Wat moet je kunnen uitleggen?

Na dit hoofdstuk moet je bij een enterprise-netwerk niet alleen kunnen zeggen of het werkt. Je moet kunnen uitleggen:

| Vraag | Verwacht antwoordtype |
|---|---|
| Wat is kritisch? | componenten, zones en bedrijfsprocessen |
| Wat kan falen? | single points of failure en verborgen afhankelijkheden |
| Wat gebeurt er dan? | impactanalyse |
| Welke redundantie bestaat? | ontwerp en bewijs |
| Hoe test je dat? | failovertestplan |
| Wie mag beheren? | secure management policy |
| Hoe herstel je na een fout? | back-up, rollback en DR |

Slotgedachte:

> Enterprise networking gaat niet meer alleen over connectiviteit. Het gaat over voorspelbaar gedrag onder druk.
