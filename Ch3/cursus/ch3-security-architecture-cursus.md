# Hoofdstuk 3 - Security architecture

## 1. Inleiding

In hoofdstuk 1 leerde je een bestaand netwerk kritisch analyseren. In hoofdstuk 2
keek je naar redundantie, switching en routing. In dit hoofdstuk verschuift de focus
naar **security architecture**: het netwerk zo ontwerpen dat alleen verantwoorde
communicatie mogelijk is.

Een netwerk kan technisch correct functioneren en toch onveilig zijn. Routing kan
perfect werken terwijl gasten interne servers bereiken, een besmet IoT-toestel
managementinterfaces scant of een publieke webserver vrij naar de interne omgeving
kan communiceren.

| Technische observatie | Securityvraag |
|---|---|
| Een guestclient kan de interne server pingen. | Waarom zou een onbeheerd gasttoestel die server mogen bereiken? |
| Een medewerker kan alle VLAN's bereiken. | Welke applicaties heeft die medewerker werkelijk nodig? |
| De publieke website is bereikbaar vanaf internet. | Staat de publieke dienst in een gecontroleerde DMZ? |
| Een switch antwoordt op SSH. | Vanuit welke bronzone mag beheer plaatsvinden? |
| Een ACL bevat meerdere regels. | Dwingt ze het bedoelde beleid af op het werkelijke verkeerspad? |

De centrale vraag is dus niet:

> Hoe schrijf ik een ACL?

De centrale vraag is:

> Welke communicatie is nodig, welke communicatie is gevaarlijk, waar controleren we
> die communicatie en hoe bewijzen we dat de grens werkt?

Security architecture begint bij doelen en risico's. ACL's, firewalls, VLAN's,
identity policies en logging zijn middelen om het gekozen beleid af te dwingen en te
controleren.

De rode draad door dit hoofdstuk is:

```text
bedrijfseis
    |
    v
noodzakelijke verkeersstroom
    |
    v
zones en trust boundary
    |
    v
controlepunt en technische regel
    |
    v
positieve test + negatieve test + bewijs
```

In de workshop pas je dit toe op **BluePeak Services**. Dat netwerk bevat Staff,
Finance, IT, Servers, Guests, IoT, een DMZ en een Management-zone. De technische
segmentatie bestaat al, maar sommige regels zijn bewust te breed of verkeerd
ontworpen. Je taak is niet om willekeurig ACL-regels te wijzigen. Je moet eerst kunnen
uitleggen welk beleid nodig is.

Kernidee:

> Een netwerk is niet veilig omdat alles werkt. Het is veilig ontworpen wanneer alleen
> noodzakelijke stromen werken en verboden stromen aantoonbaar geblokkeerd blijven.

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. uitleggen waarom security een architectuurkeuze is en geen losse configuratiestap;
2. bedrijfseisen vertalen naar noodzakelijke verkeersstromen;
3. defense in depth en least privilege toepassen op een netwerkontwerp;
4. VLAN's, subnetten en securityzones van elkaar onderscheiden;
5. zones afbakenen op basis van functie, blootstelling en gevoeligheid;
6. trust boundaries herkennen en geschikte controlepunten aanduiden;
7. de rol en de beperkingen van een DMZ uitleggen;
8. router-ACL's en stateful firewalls conceptueel vergelijken;
9. uitleggen waarom NAT geen vervanging is voor firewallbeleid;
10. north-south en east-west traffic onderscheiden;
11. een firewallregelmatrix volgens least privilege opstellen;
12. beleidsregels vertalen naar technisch uitvoerbare regels;
13. regelvolgorde, richting en plaatsing analyseren;
14. positieve, negatieve en begrenzingstests ontwerpen;
15. logs en configuratie-output als bewijs gebruiken;
16. een securityrisico concreet formuleren;
17. labkeuzes onderscheiden van een productieontwerp;
18. typische fouten methodisch onderzoeken en verklaren.

---

## 3. Security als architectuur

Security architecture beschrijft hoe systemen, zones, vertrouwensgrenzen en
beveiligingsmaatregelen samen het gewenste securitybeleid realiseren.

Daarvoor moet je meer kennen dan IP-adressen en poorten. Je moet ook weten:

| Vraag | Waarom heb je dit nodig? |
|---|---|
| Welke bedrijfstaak moet werken? | Zonder doel kan je niet verantwoorden waarom verkeer toegelaten is. |
| Welke assets zijn gevoelig? | Een publieke webpagina en een finance-database vragen niet dezelfde bescherming. |
| Welke bron start de verbinding? | Regels zijn richtinggevoelig en stateful gedrag hangt af van de initiator. |
| Welke dienst is nodig? | `HTTPS naar één server` is veel beperkter dan `IP naar het servernetwerk`. |
| Welke zone is mogelijk gecompromitteerd? | Je ontwerpt grenzen om impact te beperken wanneer één laag faalt. |
| Waar passeert het verkeer werkelijk? | Een regel werkt alleen op een controlepunt dat het pakket passeert. |
| Hoe wordt de beslissing gelogd? | Zonder bewijs kan je fouten, misbruik en beleidsafwijkingen moeilijk onderzoeken. |

Een architectuur verbindt dus drie niveaus:

| Niveau | Voorbeeld | Centrale vraag |
|---|---|---|
| Bedrijf | medewerkers gebruiken het intranet | Waarom is toegang nodig? |
| Beleid | Staff mag via HTTPS naar `SRV-APP` | Welke communicatie staan we toe? |
| Techniek | firewall- of ACL-regel voor TCP/443 | Hoe dwingen we dat af? |

Een technische regel zonder beleidsreden wordt later moeilijk te beheren. Een
beleidszin zonder technisch controlepunt blijft alleen documentatie. Beide moeten met
elkaar verbonden zijn.

Kernzin:

> Architectuur bepaalt wat veilig gedrag is; configuratie dwingt dat gedrag af.

### 3.1 Slechte situatie: eerst alles routen

In een basislabo wordt security soms achteraf toegevoegd:

1. VLAN's en routing worden geconfigureerd;
2. volledige connectiviteit wordt getest;
3. alles kan met alles communiceren;
4. enkele ACL-regels moeten daarna ongewenst verkeer blokkeren.

Dit maakt **default allow** onbewust tot uitgangspunt. Nieuwe VLAN's of servers erven
dan vaak brede bereikbaarheid totdat iemand eraan denkt extra blokkeringen toe te
voegen.

Stel dat een bedrijf deze segmenten heeft:

| VLAN | Functie | Mogelijk risico zonder beleid |
|---:|---|---|
| 10 Staff | gewone medewerkers | een besmet toestel scant andere afdelingen |
| 20 Finance | gevoelige bedrijfsprocessen | niet-financemedewerkers bereiken finance-diensten |
| 30 IT | beheerderswerkstations | beheertoegang mengt met gewone clienttoegang |
| 40 Servers | interne applicaties | elke client bereikt elke serverpoort |
| 50 Guests | onbeheerde toestellen | gasten bereiken interne adressen |
| 60 IoT | camera's en sensoren | zwakke toestellen worden springplank naar intern |
| 70 DMZ | publiek bereikbare dienst | een gecompromitteerde server beweegt naar intern |
| 99 Management | netwerkbeheer | aanvallers bereiken switches en routers rechtstreeks |

Dat alle pings slagen, bewijst alleen dat routing werkt. Het bewijst niet dat het
ontwerp correct is.

Een betere volgorde is:

1. inventariseer functies en gevoelige assets;
2. groepeer systemen met vergelijkbare securitybehoeften in zones;
3. bepaal welke zone-overschrijdende stromen noodzakelijk zijn;
4. kies waar elke trust boundary wordt afgedwongen;
5. laat alleen gemotiveerde stromen toe;
6. log relevante allow- en deny-beslissingen;
7. test verwachte toegang én verwachte blokkering;
8. documenteer eigenaar, reden en geldigheidsduur van uitzonderingen.

### 3.2 Van asset naar verkeersstroom

Een bruikbare regel begint niet bij een poortnummer, maar bij een functie.

Voorbeeld:

```text
Bedrijfstaak:
medewerkers raadplegen de interne personeelsapplicatie

Asset:
SRV-APP in de serverzone

Benodigde stroom:
Staff -> SRV-APP -> TCP/443

Niet nodig:
Staff -> alle servers -> alle protocollen
```

Werk per behoefte minstens deze velden uit:

| Veld | Vraag | Voorbeeld |
|---|---|---|
| bron | wie of wat start? | Staff-zone |
| bestemming | welke concrete dienst ontvangt? | `SRV-APP` |
| protocol en poort | welk applicatiepad is nodig? | TCP/443 |
| richting | wie initieert de sessie? | Staff naar server |
| businessreden | welk proces ondersteunt dit? | personeelsapplicatie gebruiken |
| eigenaar | wie bevestigt dat de toegang nodig blijft? | applicatie-eigenaar HR |
| bewijs | hoe test je de regel? | browsertest plus firewalllog |

Typische fout:

> "Staff heeft toegang tot Servers" is geen voldoende precieze requirement.

De zin zegt niet welke server, welke dienst, wie de verbinding start of waarom die
toegang nodig is.

### 3.3 Ontwerpbeslissing versus configuratiedetail

Dezelfde beleidsbeslissing kan technisch op verschillende platformen uitgevoerd
worden.

| Beleidsbeslissing | Mogelijke technische uitvoering |
|---|---|
| Guests mogen niet naar intern | router-ACL, zone-based firewallpolicy of distributed firewallregel |
| Alleen IT mag switches beheren | managementfirewall, VTY access-class, jump host en AAA-policy |
| Internet mag alleen HTTPS naar de publieke dienst | perimeterfirewall, destination NAT en reverse proxy |
| DMZ mag alleen één backend bereiken | stateful firewallregel naar een specifiek serverobject en poort |

De syntax kan veranderen. De ontwerpvragen blijven gelijk:

- welk verkeer is nodig?
- op welke grens wordt het gecontroleerd?
- welke uitzondering ontstaat?
- hoe wordt ze getest en gelogd?

Controleer:

> Kan je een regel uitleggen zonder eerst de vendorsyntax voor te lezen?

Als dat niet lukt, is de beleidsreden waarschijnlijk nog onvoldoende duidelijk.

---

## 4. Defense in depth

**Defense in depth** betekent dat je meerdere verdedigingslagen combineert. Je
vertrouwt niet op één firewallregel, één wachtwoord of één beveiligingsproduct.

Elke laag heeft een eigen taak:

| Laag | Wat doet ze concreet? | Wat beperkt ze? |
|---|---|---|
| fysieke en linkbeveiliging | beschermt poorten, lokalen en switchtoegang | ongeautoriseerde fysieke aansluiting |
| segmentatie | verdeelt clients, servers, IoT en beheer | brede Layer 2- en Layer 3-bereikbaarheid |
| firewalling | controleert verkeer over trust boundaries | ongewenste verbindingen tussen zones |
| hardening | schakelt ongebruikte diensten uit en patcht systemen | misbruik van kwetsbare of overbodige services |
| identity en MFA | controleert wie toegang vraagt | misbruik van alleen een gestolen wachtwoord |
| autorisatie | beperkt acties na aanmelding | te brede rechten binnen een dienst |
| endpointbeveiliging | detecteert of blokkeert schadelijk gedrag op hosts | malware en lokale misconfiguratie |
| logging en monitoring | maakt gebeurtenissen zichtbaar | langdurig onopgemerkt misbruik |
| back-up en herstel | herstelt configuratie en data | blijvende impact van fouten of incidenten |

Deze lagen vervangen elkaar niet. Een firewall kan bijvoorbeeld niet bepalen of een
legitiem aangemelde gebruiker te veel rechten heeft in een finance-applicatie. MFA kan
dan weer niet voorkomen dat een kwetsbare server via een toegelaten HTTPS-verbinding
wordt aangevallen.

### 4.1 Ontwerpen voor het falen van één laag

Voorbeeld:

> Een medewerker opent een phishingbijlage en de laptop raakt besmet.

Zonder defense in depth:

```text
besmette laptop
    -> scant alle VLAN's
    -> bereikt beheerinterfaces
    -> benadert brede file shares
    -> beweegt naar servers
```

Met meerdere lagen:

| Beveiligingslaag | Verwacht effect na de besmetting |
|---|---|
| Staff-zone | beperkt welke interne subnetten bereikbaar zijn |
| serverregels | laat alleen noodzakelijke applicatiepoorten toe |
| managementzone | blokkeert rechtstreeks beheer vanaf Staff |
| endpointdetectie | signaleert verdacht proces- of netwerkgedrag |
| firewalllogging | toont scans en geblokkeerde verbindingen |
| beperkte gebruikersrechten | vermindert de lokale impact |

De besmetting blijft ernstig, maar één fout geeft niet automatisch toegang tot het
volledige netwerk.

### 4.2 Lagen moeten onafhankelijk betekenis hebben

Twee regels die allebei dezelfde verkeerde aanname gebruiken, vormen geen sterke
defense in depth.

Voorbeeld:

| Schijnbare laag | Probleem |
|---|---|
| een VLAN scheidt Guests van Servers | inter-VLAN routing laat alles toe |
| een ACL bevat `permit ip any any` | de trust boundary is technisch open |

Er zijn technisch twee componenten, maar geen twee werkende verdedigingslagen.

Sterker ontwerp:

| Laag | Onafhankelijke bijdrage |
|---|---|
| apart guest-VLAN | beperkt het broadcastdomein en maakt de bron herkenbaar |
| firewallpolicy Guest naar Internal | blokkeert routeerbaar verkeer naar interne zones |
| client isolation op wifi | beperkt verkeer tussen gasten onderling |
| logging en rate limiting | maakt scans zichtbaar en beperkt misbruik |

Kernzin:

> Defense in depth beperkt de schade wanneer een andere controle ontbreekt, faalt of
> omzeild wordt.

---

## 5. Least privilege

**Least privilege** betekent:

> Geef een gebruiker, toestel, applicatie of zone alleen de toegang die nodig is voor
> de taak, gedurende de periode waarin die toegang nodig is.

Op netwerkniveau maak je toegang zo precies mogelijk op meerdere dimensies:

| Dimensie | Te breed | Least privilege |
|---|---|---|
| bron | alle interne clients | Finance-zone |
| bestemming | volledig servernetwerk | `SRV-FIN` |
| dienst | alle IP-protocollen | TCP/443 |
| richting | beide richtingen | Finance initieert naar server |
| tijd | permanent | alleen zolang de applicatie bestaat |
| identiteit of rol | elke VPN-gebruiker | financegroep via specifieke policy |
| beheerpad | elk IT-toestel rechtstreeks | beheerde jump host |

Least privilege betekent niet dat je willekeurig zoveel mogelijk blokkeert. Een te
strenge regel die een noodzakelijk bedrijfsproces stillegt, is geen goed ontwerp. Je
zoekt de kleinste toegang die de functie betrouwbaar laat werken.

### 5.1 Waarom `permit ip any any` zelden een eindontwerp is

Een regel zoals:

```text
permit ip any any
```

heeft vier problemen:

| Probleem | Praktisch gevolg |
|---|---|
| onbekende bron | ook onverwachte of nieuwe toestellen vallen onder de regel |
| onbekende bestemming | gevoelige systemen worden onbedoeld bereikbaar |
| onbekende dienst | beheerpoorten en kwetsbare services staan mee open |
| ontbrekende reden | niemand kan later bepalen wat veilig verwijderd mag worden |

Zo'n regel kan tijdelijk nuttig zijn tijdens een gecontroleerde diagnose, maar dan
moeten eigenaar, doel, logging en eindtijd vastliggen. Een tijdelijke uitzondering
zonder einddatum wordt vaak een permanente zwakte.

Voorbeeld van verfijning:

```text
te breed:
Staff -> Servers -> any -> allow

beter:
Staff -> SRV-APP -> TCP/443 -> allow
Staff -> Servers -> overige -> deny
```

### 5.2 Least privilege vraagt applicatiekennis

Je kan geen precieze netwerkregels maken wanneer niemand weet hoe de applicatie werkt.

| Vraag aan de applicatie-eigenaar | Waarom belangrijk? |
|---|---|
| Welke clients gebruiken de dienst? | bepaalt de bron |
| Welke frontend en backend zijn betrokken? | bepaalt bestemmingen en tussenstromen |
| Welke protocollen en poorten zijn nodig? | voorkomt `any service` |
| Wie initieert elke verbinding? | bepaalt richting en stateful sessieopbouw |
| Is DNS, NTP of een identity provider nodig? | voorkomt vergeten afhankelijkheden |
| Wat gebeurt er bij uitval? | helpt veilige foutafhandeling ontwerpen |
| Wanneer mag de regel verwijderd worden? | ondersteunt lifecyclebeheer |

Typische fout:

> Een applicatie werkt niet na invoering van default deny, dus men opent tijdelijk alle
> poorten en laat de regel daarna staan.

Betere aanpak:

1. observeer welke stroom faalt;
2. controleer bron, bestemming, poort en richting;
3. vergelijk met de gedocumenteerde requirement;
4. voeg alleen de ontbrekende noodzakelijke stroom toe;
5. test opnieuw, inclusief verboden verkeer;
6. documenteer de wijziging.

Kernzin:

> Least privilege is niet "zo weinig mogelijk verkeer", maar "niet meer verkeer dan
> aantoonbaar nodig".

---

## 6. Securityzones

Een **securityzone** is een logische groep systemen waarvoor een vergelijkbaar
vertrouwens- en verkeersbeleid geldt.

Zones maken beleid begrijpelijker. In plaats van duizenden losse IP-adressen te
bespreken, kan je bijvoorbeeld zeggen:

> Guests mogen geen verbinding starten naar Internal.

Veelvoorkomende zones zijn:

| Zone | Typische systemen | Belangrijkste ontwerpbezorgdheid |
|---|---|---|
| Internet | onbekende externe hosts | volledig onvertrouwde bron |
| DMZ | reverse proxy, publieke webserver, mailgateway | publiek blootgesteld maar afgeschermd van intern |
| Guests | bezoekers en persoonlijke toestellen | onbeheerde endpoints alleen noodzakelijke externe toegang geven |
| Staff | werkstations van medewerkers | toegang tot bedrijfsapps zonder brede laterale beweging |
| Finance | financeclients of -diensten | gevoelige processen en data beperken tot bevoegde bronnen |
| IT | beheerde administratorwerkstations | verhoogde toegang gecontroleerd inzetten |
| Servers | interne applicaties | alleen applicatiegerichte toegang toelaten |
| Management | beheerinterfaces, jump hosts, monitoring | hoogste impact bij compromis; zeer beperkte toegang |
| IoT | camera's, printers, sensoren | vaak zwak beheerde toestellen strikt begrenzen |
| VPN | externe gebruikers | toegang bepalen volgens identiteit, toestelstatus en rol |

### 6.1 VLAN, subnet en zone zijn verschillende begrippen

| Begrip | Waarvoor dient het? | Voorbeeld |
|---|---|---|
| VLAN | Layer 2-segmentatie en broadcastdomein | VLAN 50 `GUESTS` |
| subnet | Layer 3-adressering en routing | `10.30.50.0/24` |
| zone | securitybeleid en vertrouwensrelatie | Guest-zone |

Vaak correspondeert één zone met één VLAN en één subnet. Dat maakt een labo
overzichtelijk, maar het is geen technische verplichting.

Voorbeeld met meerdere VLAN's in één zone:

| VLAN | Functie | Zone | Gemeenschappelijk beleid |
|---:|---|---|---|
| 110 | studenten lokaal A101 | Students | internet, leerplatform, lokale printer |
| 111 | studenten lokaal A102 | Students | internet, leerplatform, lokale printer |
| 112 | studenten lokaal A103 | Students | internet, leerplatform, lokale printer |

De VLAN's houden lokalen technisch uit elkaar. De zone beschrijft het algemene
securitybeleid. Binnen die zone kunnen extra regels gelden, bijvoorbeeld dat elk
lokaal alleen zijn eigen printer bereikt.

Ook het omgekeerde probleem bestaat. Eén groot server-VLAN kan systemen met sterk
verschillende risico's bevatten. Bij BluePeak staan `SRV-APP` en `SRV-FIN` beide in
VLAN 40. Ze zitten technisch in hetzelfde subnet, maar de finance-applicatie kan een
strenger beleid verdienen. Zonder extra hostgebaseerde of gedistribueerde filtering is
verkeer binnen hetzelfde VLAN niet zichtbaar op de routerfirewall.

Waarom belangrijk?

> Inter-VLAN filtering controleert alleen verkeer dat werkelijk routeert. Twee hosts in
> hetzelfde VLAN communiceren meestal rechtstreeks op Layer 2.

### 6.2 Hoe bepaal je een zone?

Gebruik niet alleen de afdeling als criterium. Kijk naar meerdere eigenschappen:

| Criterium | Vraag | Mogelijk gevolg voor zonering |
|---|---|---|
| functie | welke taak voert het systeem uit? | clients, servers en beheer scheiden |
| beheer | is het toestel door de organisatie beheerd? | Guests en BYOD apart behandelen |
| blootstelling | is de dienst vanaf internet bereikbaar? | publieke dienst in DMZ plaatsen |
| datagevoeligheid | verwerkt het systeem financiële of persoonlijke data? | strengere finance- of databasesegmentatie |
| technische kwaliteit | kan het toestel gepatcht en gemonitord worden? | IoT sterker isoleren |
| toegangsbehoefte | hebben systemen dezelfde toegelaten stromen? | systemen met verschillend beleid niet onnodig groeperen |
| impact bij compromis | welke vervolgstappen worden mogelijk? | management en identity-infrastructuur extra beschermen |

Een goede zone heeft een duidelijke beschrijving. Bijvoorbeeld:

```text
Zone: Guests
Inhoud: onbeheerde toestellen van bezoekers
Benodigde toegang: DNS en webverkeer naar internet
Niet toegestaan: verbindingen naar interne en managementzones
Controlepunt: firewall op de gateway van VLAN 50
Bewijs: internettest slaagt; tests naar interne server en management falen
```

### 6.3 Vertrouwen is geen eenvoudige ranglijst

Een vereenvoudigde voorstelling kan helpen:

```text
Internet < Guests / IoT < Staff < gevoelige diensten < Management
```

Maar vertrouwen is contextafhankelijk. Een financeclient is niet automatisch technisch
veiliger dan een gewone staffclient. De zone is vooral gevoeliger omdat ze toegang
heeft tot waardevolle processen en data.

Beoordeel daarom minstens drie aspecten:

| Aspect | Voorbeeldvraag |
|---|---|
| kans op compromis | is dit een publiek bereikbare of moeilijk patchbare host? |
| impact bij compromis | welke data of beheermogelijkheden worden bereikbaar? |
| noodzakelijke toegang | welke verbindingen moet de zone kunnen starten of ontvangen? |

Voorbeeld:

- Een DMZ-server is goed beheerd, maar publiek blootgesteld en daarom niet vertrouwd
  voor vrije toegang naar intern.
- Een managementhost is niet "veilig omdat hij in Management staat"; hij moet juist
  extra beschermd worden omdat compromis een zeer grote impact heeft.
- Een IoT-camera voert een kleine functie uit, maar kan een hoog risico vormen wanneer
  patches en monitoring beperkt zijn.

Kernzin:

> Een zonenaam is geen bewijs van veiligheid. Het afgedwongen beleid en het risico bij
> compromis bepalen hoe je de zone behandelt.

### 6.4 Trust boundaries

Een **trust boundary** is een grens waar verkeer van de ene securitycontext naar een
andere gaat.

Voorbeelden:

| Trust boundary | Waarom is controle nodig? |
|---|---|
| Internet naar DMZ | onbekende externe bronnen bereiken een publieke dienst |
| DMZ naar Internal | een publiek blootgestelde host mag geen vrij intern pad krijgen |
| Guests naar Internal | onbeheerde toestellen mogen bedrijfsassets niet bereiken |
| IoT naar Servers | een kwetsbaar toestel heeft slechts een beperkte applicatiestroom nodig |
| Staff naar Management | gewone gebruikers hebben geen netwerkbeheerfunctie |
| IT naar Management | verhoogde toegang moet beperkt, geauthenticeerd en gelogd worden |
| VPN naar Internal | externe toegang moet volgen uit identiteit en rol, niet alleen uit tunnelopbouw |

Op een boundary bepaal je:

| Controle | Concrete vraag |
|---|---|
| filtering | welke bron, bestemming en dienst zijn toegestaan? |
| authenticatie | moet de gebruiker of het toestel extra bewijzen wie het is? |
| inspectie | volstaat Layer 3/4-filtering of is applicatiecontext nodig? |
| logging | welke allow- en deny-gebeurtenissen zijn relevant? |
| monitoring | welk afwijkend gedrag moet een alert veroorzaken? |
| capaciteit en beschikbaarheid | blijft de grens werken onder piekbelasting of uitval? |
| documentatie | wie is eigenaar van de uitzonderingen? |

### 6.5 Segmentatie moet afgedwongen worden

Een apart VLAN zonder filtering creëert bereikbaarheidsscheiding op Layer 2, maar niet
automatisch op Layer 3.

Slechte situatie:

```text
Guest VLAN 50
      |
inter-VLAN router zonder beperkingen
      |
Server VLAN 40
```

De zonenaam bestaat, maar de trust boundary is open.

Betere situatie:

```text
Guest VLAN 50
      |
[ policy: deny Guest -> Internal ]
      |
interne VLAN's
```

Controleer:

- passeert verkeer de bedoelde firewall of ACL?
- is verkeer binnen hetzelfde VLAN ook relevant?
- bestaat er een alternatief routepad dat de controle omzeilt?
- zijn IPv4 en IPv6 allebei meegenomen?
- geldt dezelfde grens voor draadloos, VPN en bekabeld verkeer?

Kernzin:

> Segmentatie is pas een securitymaatregel wanneer verkeer over de grens effectief
> gecontroleerd wordt.

---

## 7. DMZ

Een **DMZ** of demilitarized zone is een aparte securityzone voor systemen die
bereikbaar moeten zijn vanuit een minder vertrouwde omgeving, meestal internet.

Een DMZ beperkt de rechtstreekse blootstelling van het interne netwerk. Ze gaat uit van
een realistische aanname:

> Een publiek bereikbare dienst kan ooit gecompromitteerd raken.

Het ontwerp moet daarom niet alleen inkomend internetverkeer controleren, maar ook
beperken wat een gecompromitteerde DMZ-host daarna kan bereiken.

Typische DMZ-systemen:

| Systeem | Rol in de DMZ | Belangrijk aandachtspunt |
|---|---|---|
| reverse proxy | ontvangt webverkeer en stuurt het gecontroleerd door | alleen vereiste backends en poorten bereiken |
| publieke webserver | levert publieke content | geen vrije toegang naar interne servers |
| mail gateway | verwerkt inkomende en uitgaande mailstromen | strikte koppeling met interne maildienst |
| VPN-gateway | beëindigt externe tunnels | tunnel betekent nog geen brede interne autorisatie |
| API gateway | publiceert en controleert API-verkeer | authenticatie, rate limiting en logging |
| bastion service | gecontroleerd extern beheerpad | sterke authenticatie en beperkte doelen |

### 7.1 Twee verschillende trust boundaries

Conceptueel:

```text
Internet
    |
    | boundary 1: alleen publieke dienst
    v
+---------+
|   DMZ   |
+---------+
    |
    | boundary 2: standaard geen vrije interne toegang
    v
Internal
```

De twee grenzen hebben verschillende doelen:

| Grens | Basisbeleid | Reden |
|---|---|---|
| Internet naar DMZ | alleen gepubliceerde diensten toelaten | extern gebruik mogelijk maken zonder andere poorten te openen |
| DMZ naar Internal | default deny, alleen specifieke backendstromen | laterale beweging na compromis beperken |

In een klein Packet Tracer-labo kan één router beide grenzen simuleren. Dat verandert
de logica niet: de regels moeten nog altijd twee afzonderlijke vertrouwensrelaties
voorstellen.

### 7.2 Wat maakt een DMZ technisch speciaal?

Een DMZ is meestal opgebouwd uit gewone netwerkcomponenten:

| Onderdeel | Voorbeeld bij BluePeak | Functie |
|---|---|---|
| apart VLAN | VLAN 70 `DMZ` | scheidt de hosts op Layer 2 |
| apart subnet | `10.30.70.0/24` | maakt routing en beleid herkenbaar |
| eigen gateway of firewallinterface | `10.30.70.1` | vormt een controlepunt voor routeerbaar verkeer |
| publicatieregel | HTTPS naar `SRV-WEB-DMZ` | maakt alleen de publieke dienst extern bereikbaar |
| outbound policy | DMZ naar Internal standaard deny | beperkt vervolgacties na compromis |
| beheerregel | alleen gecontroleerd beheerpad | beschermt beheerinterfaces en credentials |
| logging | sessie- en deny-events op beide grenzen | ondersteunt detectie en onderzoek |

Het woord `DMZ` op een VLAN maakt het netwerk niet veilig. De plaatsing en het beleid
maken het een DMZ.

### 7.3 Verkeersstromen rond een publieke webdienst

Voor een eenvoudige publieke website analyseer je minstens vier stromen:

| Stroom | Verwacht beleid | Waarom? |
|---|---|---|
| Internet naar DMZ-webserver TCP/443 | allow | publieke website moet bereikbaar zijn |
| Internet naar DMZ-webserver SSH | deny | beheer hoort niet publiek open te staan |
| Internet naar interne server | deny | interne diensten worden niet rechtstreeks gepubliceerd |
| DMZ-webserver naar Management | deny | een publieke host mag geen beheerpad krijgen |

Als de DMZ-dienst een interne backend nodig heeft, voeg je een vijfde, zeer specifieke
stroom toe:

```text
reverse proxy in DMZ -> interne applicatie -> TCP/443
```

Dat betekent niet:

```text
DMZ -> Internal -> any
```

De bestemming, poort en initiator blijven beperkt.

### 7.4 Waarom geen publieke server in het interne servernetwerk?

Slechte situatie:

```text
Internet -- port forwarding --> SRV-APP in intern VLAN 40
```

| Probleem | Praktisch gevolg |
|---|---|
| publieke en interne rollen mengen | een internetaanval bereikt meteen een intern segment |
| breed intern netwerkpad | compromis kan leiden tot scanning of laterale beweging |
| onduidelijke regels | interne en publieke toegang zijn moeilijk apart te beheren |
| gedeeld foutdomein | een wijziging voor de publieke dienst beïnvloedt interne servers |

Betere aanpak:

```text
Internet -- HTTPS --> DMZ reverse proxy/webserver
                           |
                           +-- alleen indien nodig --> specifieke backend
```

### 7.5 Reverse proxy: nuttig, maar geen vrijgeleide

Een reverse proxy kan:

- één gecontroleerd publicatiepunt vormen;
- TLS centraal afhandelen;
- aanvragen loggen;
- hostnames en URL-paden naar backends sturen;
- aanvullende authenticatie of filtering toepassen.

Maar een reverse proxy neemt niet alle security over.

| Verkeerde aanname | Correcte redenering |
|---|---|
| de proxy staat in de DMZ, dus de backend is automatisch veilig | de firewall moet het proxypad tot een specifieke backend beperken |
| alleen TCP/443 staat open, dus de webapp kan niet aangevallen worden | kwetsbare applicatieverzoeken lopen juist via TCP/443 |
| TLS maakt de inhoud veilig | TLS beschermt transport, niet tegen misbruik van de applicatie |
| de proxy mag alle interne webservers bereiken | alleen gepubliceerde backends zijn nodig |

### 7.6 Beheer, updates en monitoring van DMZ-hosts

Een DMZ-host heeft vaak meer stromen nodig dan alleen publiek inkomend verkeer. Denk
aan DNS, tijdsynchronisatie, updates, logging en beheer. Elke stroom moet bewust worden
ontworpen.

| Behoefte | Veilige ontwerpvraag |
|---|---|
| DNS | welke resolver mag de DMZ-host gebruiken? |
| NTP | welke betrouwbare tijdsbron is nodig voor logs en certificaten? |
| updates | gaat dit via een proxy of interne repository, en alleen outbound? |
| logging | mag de host logs naar een collector sturen zonder de rest van Management te bereiken? |
| beheer | gebeurt beheer via een jump host en sterke authenticatie? |
| back-up | welke data wordt gekopieerd en kan het back-uppad misbruikt worden? |

`DMZ naar Internal: deny` is dus een veilig uitgangspunt, geen excuus om echte
afhankelijkheden niet te onderzoeken.

### 7.7 Een DMZ is niet automatisch veilig

| Fout DMZ-beleid | Risico | Betere aanpak |
|---|---|---|
| Internet mag alle poorten naar de DMZ-host | onnodige services zijn aanvalbaar | alleen gepubliceerde dienst toelaten |
| DMZ mag vrij naar Servers | laterale beweging na compromis | specifieke backendregel of deny |
| DMZ mag Management bereiken | netwerkbeheer komt in gevaar | apart gecontroleerd beheerpad |
| beheer-SSH staat open vanaf internet | brute force en credentialmisbruik | VPN of jump host met MFA |
| geen logging op DMZ-grenzen | aanval en foutconfiguratie blijven onzichtbaar | relevante sessies en denies loggen |
| publieke dienst en database op dezelfde host | compromis raakt data direct | rollen en gegevensstromen scheiden waar risico dat vereist |

Kernzin:

> Een DMZ vermindert de impact van publieke blootstelling alleen wanneer zowel verkeer
> naar de DMZ als verkeer vanuit de DMZ strikt wordt begrensd.

---

## 8. Firewall placement

**Firewall placement** bepaalt waar je verkeer controleert. Een perfecte regel op een
toestel dat het verkeer niet passeert, heeft geen effect.

Veelvoorkomende controlepunten:

| Plaats | Verkeer | Hoofddoel |
|---|---|---|
| internetedge | internet ↔ organisatie | publicatie en outbound internetverkeer controleren |
| DMZ-grens | DMZ ↔ Internal | publieke systemen intern begrenzen |
| interzone-firewall | interne zone ↔ interne zone | laterale beweging beperken |
| VPN-ingang | VPN-gebruiker ↔ intern | toegang per identiteit of groep bepalen |
| managementgrens | beheerders ↔ infrastructuur | beheerpad strikt beperken en loggen |
| host- of workloadfirewall | host ↔ host, ook binnen subnet | fijnmazige microsegmentatie |

### 8.1 Teken eerst het verkeerspad

Voorbeeldvraag:

> Waar blokkeer je Guest naar `SRV-APP`?

Vereenvoudigd pad bij BluePeak:

```text
PC-GUEST
  -> access switch
  -> core switch
  -> R-FW subinterface VLAN 50
  -> routing- en filterbeslissing
  -> subinterface VLAN 40
  -> SRV-APP
```

Een inbound ACL op de guest-subinterface ziet het verkeer vroeg, dicht bij de bron.
Een ACL alleen op de internetinterface ziet deze interne stroom niet.

Gebruik bij plaatsing deze vragen:

| Vraag | Wat ontdek je? |
|---|---|
| Waar staat de default gateway van de bron? | waar verkeer het bron-VLAN verlaat |
| Zijn bron en doel in hetzelfde subnet? | of het verkeer de routerfirewall passeert |
| Welke interfaces passeert het pakket? | waar een ACL effect kan hebben |
| In welke richting ziet elke interface het pakket? | of `in` of `out` logisch is |
| Bestaat een tweede route? | of verkeer de controle kan omzeilen |
| Is het antwoordpad symmetrisch? | of een stateful firewall beide richtingen ziet |

Sterke analysezin:

> De regelinhoud is correct, maar de plaatsing is fout omdat deze verkeersstroom de
> gekozen interface niet passeert.

### 8.2 Stateful versus stateless filtering

Een klassieke router-ACL beoordeelt pakketten vooral op velden zoals bron-IP,
bestemmings-IP, protocol en poort. Ze houdt normaal geen volledige sessiestatus bij.

Een stateful firewall bouwt een toestandstabel op. Wanneer een toegelaten client een
TCP-sessie naar een server start, herkent de firewall terugkerende pakketten als deel
van die sessie.

```text
client 10.30.10.101:51514  -> server 10.30.40.10:443
                              allow en sessiestatus aanmaken

server 10.30.40.10:443     -> client 10.30.10.101:51514
                              toegestaan als return traffic
```

| Aspect | Stateless ACL | Stateful firewall |
|---|---|---|
| besliseenheid | individueel pakket | pakket plus sessiecontext |
| return traffic | vaak expliciet rekening mee houden | automatisch koppelen aan geldige sessie |
| beleid | interface- en richtinggericht | vaak zone-, object- en applicatiegericht |
| logging | meestal beperkter | vaak sessie-, policy- en applicatiecontext |
| complexe protocollen | moeilijker | kan extra protocolinspectie bieden |
| schaalbaarheid van beheer | snel veel losse regels | centrale objecten en policies mogelijk |

Stateful betekent niet automatisch veilig. Een te brede stateful allow-regel blijft te
breed. De firewall onthoudt dan alleen de toestand van verkeer dat nooit zo ruim
toegelaten had mogen worden.

### 8.3 Router-ACL en firewall

| Router-ACL | Enterprise-firewall |
|---|---|
| nuttig voor eenvoudige Layer 3/4-filtering | geschikt voor centrale zonepolicies |
| werkt goed als leerinstrument voor bron, doel en richting | biedt meestal stateful inspectie |
| vaak gebonden aan interface en richting | gebruikt vaak zones, adressen en serviceobjecten |
| beperkte applicatiecontext | kan applicaties, gebruikers of URL-categorieën herkennen |
| logging en rule lifecycle zijn eenvoudiger | rijkere logging, beheerworkflow en rapportage |

In de BluePeak-workshop simuleert een Cisco-router met subinterfaces en ACL's de
firewallfunctie. Dat is didactisch nuttig omdat regelvolgorde, interface en richting
zichtbaar worden.

In productie:

> Een echte enterprise-firewall zou doorgaans stateful, zone-based en centraal
> gelogd werken. De beleidsredenering uit het labo blijft wel dezelfde.

### 8.4 NAT is geen firewallbeleid

NAT vertaalt adressen of poorten. Het beantwoordt niet automatisch welke communicatie
volgens het securitybeleid toegestaan hoort te zijn.

Voorbeeld:

```text
203.0.113.1:443 -> 10.30.70.10:443
```

Deze destination NAT- of port-forwardingregel publiceert een dienst. Je hebt daarnaast
nog een securitybeslissing nodig:

| Vraag | Waarom nodig? |
|---|---|
| welke externe bronnen mogen verbinden? | publicatie kan algemeen of beperkt zijn |
| welke dienst wordt toegelaten? | alleen TCP/443, niet alle poorten |
| naar welke interne host wordt vertaald? | de vertaling mag niet naar `SRV-APP` in Internal wijzen |
| wat mag de doelhost daarna bereiken? | compromisimpact begrenzen |
| wat wordt gelogd? | publieke toegang onderzoeken |

Ook source NAT of PAT is geen sterke beveiligingslaag op zich. Het verbergt interne
adressen, maar vervangt geen expliciete filtering.

Kernzin:

> NAT bepaalt adresvertaling; firewallbeleid bepaalt toegestane communicatie.

### 8.5 Chokepoints en alternatieve paden

Een controlepunt is alleen betrouwbaar als relevant verkeer er niet omheen kan.

Let op:

- parallelle routers zonder identiek beleid;
- directe Layer 2-verbindingen tussen zones;
- VPN-tunnels die op een ander toestel eindigen;
- cloud- of draadloze paden buiten de centrale firewall;
- IPv6 terwijl alleen IPv4-regels bestaan;
- beheerinterfaces met een tweede, onbeveiligd adres;
- asymmetrische routing bij stateful firewalls.

Bij asymmetrische routing ziet firewall A het eerste pakket en firewall B het
antwoord. Geen van beide ziet dan noodzakelijk de volledige sessie. Dat kan geldige
verbindingen breken of logging onvolledig maken.

Controleer:

> Is het gekozen controlepunt technisch in-path voor zowel de aanvraag als het
> antwoord?

---

## 9. North-south en east-west traffic

**North-south traffic** is verkeer tussen de organisatie en een externe omgeving.

Voorbeelden:

| Stroom | Type | Securityvraag |
|---|---|---|
| Staff naar een website op internet | north-south | welke outbound diensten zijn nodig? |
| internetgebruiker naar DMZ-webserver | north-south | welke publieke dienst wordt gepubliceerd? |
| VPN-gebruiker naar interne applicatie | north-south | welke identiteit en rol bepalen toegang? |

**East-west traffic** is verkeer tussen interne zones, workloads of systemen.

| Stroom | Type | Securityvraag |
|---|---|---|
| Staff naar `SRV-APP` | east-west | alleen HTTPS of breder? |
| Finance naar `SRV-FIN` | east-west | wie mag de gevoelige applicatie bereiken? |
| IoT-camera naar loggingserver | east-west | welke ene dienst heeft de camera nodig? |
| DMZ-proxy naar interne backend | east-west | hoe beperken we het pad na compromis? |
| IT naar Management | east-west | via welk gecontroleerd beheerpad? |

Veel organisaties investeren eerst in een sterke internetfirewall. Toch kan een
aanvaller via phishing, gestolen VPN-credentials, een kwetsbare laptop of een
gecompromitteerde IoT-host binnen de perimeter terechtkomen.

Zonder interne filtering:

```text
initiële toegang -> interne scan -> credentialmisbruik -> laterale beweging
```

Interne segmentatie beperkt die vervolgstappen.

### 9.1 De richting hangt niet af van de tekening

`North`, `south`, `east` en `west` zijn conceptuele termen. De fysieke positie op een
netwerkschema is niet doorslaggevend.

Belangrijker is:

- gaat de stroom over de externe perimeter?
- blijft de stroom binnen de organisatie?
- welke zones en trust boundaries worden gekruist?
- wie initieert de sessie?

### 9.2 Begin met risicovolle interne grenzen

Wanneer volledige microsegmentatie nog niet haalbaar is, prioriteer dan grenzen met
hoge kans of impact:

| Prioriteit | Waarom eerst? |
|---|---|
| Guests naar Internal | onbeheerde toestellen hebben weinig interne noodzaak |
| IoT naar Management en Servers | toestellen zijn vaak moeilijk te patchen en monitoren |
| Staff naar Management | gewone clients mogen geen infrastructuur beheren |
| DMZ naar Internal | publieke blootstelling vergroot compromiskans |
| algemene clients naar gevoelige diensten | beperkt datatoegang en laterale beweging |

Kernzin:

> Een strenge perimeter voorkomt niet dat een aanvaller zich intern verplaatst nadat
> één endpoint of account is gecompromitteerd.

---

## 10. Firewallregelmatrix

Een **firewallregelmatrix** beschrijft het gewenste verkeer tussen zones voordat je
vendorsyntax schrijft.

Een minimummatrix bevat:

| Veld | Betekenis |
|---|---|
| bronzone of bronobject | wie start de communicatie? |
| doelzone of doelobject | welke dienst wordt aangesproken? |
| protocol en poort | welke technische dienst is nodig? |
| actie | allow of deny |
| reden | welk bedrijfsproces of risico verklaart de regel? |

Voor professioneel beheer voeg je toe:

| Extra veld | Waarom nuttig? |
|---|---|
| eigenaar | wie bevestigt dat de regel nodig blijft? |
| logging | welke gebeurtenissen moeten zichtbaar zijn? |
| ticket of wijzigingsreferentie | waarom en wanneer werd de regel ingevoerd? |
| verval- of reviewdatum | wanneer wordt tijdelijke of oude toegang herbekeken? |
| testmethode | hoe toon je aan dat de regel werkt? |
| omgeving | geldt de regel voor lab, test of productie? |

### 10.1 Voorbeeldmatrix voor BluePeak

| Bron | Doel | Dienst | Actie | Reden | Bewijstest |
|---|---|---|---|---|---|
| Staff | `SRV-APP` | HTTPS | allow | interne bedrijfsapp | browser vanaf `PC-STAFF` |
| Staff | Management | any | deny | geen beheerrol | SSH/HTTPS faalt vanaf `PC-STAFF` |
| Finance | `SRV-FIN` | HTTPS | allow | financeproces | browser vanaf `PC-FINANCE` |
| Finance | overige Servers | any | deny tenzij vereist | gevoelige toegang begrenzen | test naar `SRV-APP` faalt als niet nodig |
| IT | Management | SSH/HTTPS | allow | infrastructuurbeheer | SSH vanaf `PC-IT` |
| Guests | Internet | noodzakelijke diensten | allow | gastinternet | externe test vanaf `PC-GUEST` |
| Guests | Internal | any | deny | onbeheerde toestellen isoleren | test naar `SRV-APP` faalt |
| IoT | `SRV-APP` | HTTPS indien vereist | allow beperkt | telemetrie of applicatiekoppeling | TCP/443-test vanaf `CAM-IOT` |
| IoT | Management | any | deny | beheer beschermen | test naar management-IP faalt |
| Internet | `SRV-WEB-DMZ` | HTTPS | allow | publieke website | HTTPS-test vanaf ISP-zijde |
| Internet | Internal | any | deny | interne diensten niet publiceren | test naar `SRV-APP` faalt |
| DMZ | Internal | any standaard | deny | laterale beweging beperken | test van DMZ-host naar `SRV-APP` faalt |
| DMZ | Management | any | deny | beheer beschermen | test naar management-IP faalt |

Deze matrix is nog een ontwerpdocument. De concrete adressen, serviceobjecten,
interfacekeuze en return-trafficbehandeling volgen bij de implementatie.

### 10.2 Default deny

Bij **default deny** is communicatie geblokkeerd tenzij een expliciete allow-regel
bestaat.

Voordelen:

| Voordeel | Wat betekent dit concreet? |
|---|---|
| nieuwe systemen zijn niet automatisch bereikbaar | een extra server erft niet onbedoeld alle bestaande toegang |
| uitzonderingen worden zichtbaar | elke allow heeft een reden nodig |
| foutimpact wordt beperkt | vergeten regels leiden eerder tot geen toegang dan tot te brede toegang |
| audits worden duidelijker | de matrix toont welke stromen bewust toegestaan zijn |

Default deny vraagt wel voorbereiding. Applicaties hebben soms minder zichtbare
afhankelijkheden zoals DNS, NTP, identity, certificaatcontrole, logging of updates.
Blokkeren zonder analyse kan productie verstoren.

Een veilige invoering gebeurt daarom gefaseerd:

1. inventariseer en observeer bestaande stromen;
2. bevestig noodzakelijke afhankelijkheden met eigenaars;
3. maak expliciete allow-regels;
4. activeer relevante logging;
5. test in een gecontroleerde omgeving of onderhoudsperiode;
6. monitor denies en corrigeer alleen aantoonbaar noodzakelijke stromen.

### 10.3 Specifieke regels

Vergelijk:

| Bron | Doel | Dienst | Beoordeling |
|---|---|---|---|
| Staff | Servers | any | te breed: onbekende hosts en services |
| Staff | `SRV-APP` | TCP/443 | precies: één functie en één dienst |
| IT | Management | any | nog te breed als alleen SSH en HTTPS nodig zijn |
| IT jump host | netwerktoestellen | SSH | beter begrensd beheerpad |

Objectnamen maken beleid leesbaar, maar alleen als ze correct beheerd worden. Een
object `INTERNAL_SERVERS` dat per ongeluk ook DMZ- en managementhosts bevat, maakt een
op het eerste gezicht nette regel toch te breed.

Controleer daarom:

- welke adressen zitten werkelijk in het object?
- zijn subnetten niet groter dan nodig?
- verwijdert men oude hosts uit groepen?
- is IPv6-equivalent beleid aanwezig?
- is de poort aan de serverzijde bedoeld, niet de tijdelijke clientpoort?

### 10.4 Regelvolgorde en impliciete deny

Veel ACL's en firewalls verwerken regels van boven naar beneden. De eerste match
bepaalt de actie.

Slecht:

```text
permit ip 10.30.50.0/24 any
deny   ip 10.30.50.0/24 10.30.0.0/16
```

De brede permit matcht eerst. De deny wordt nooit bereikt voor guestverkeer.

Beter:

```text
deny   ip 10.30.50.0/24 10.30.0.0/16
permit ip 10.30.50.0/24 any
```

Bij klassieke Cisco ACL's bestaat bovendien een impliciete deny aan het einde. Verkeer
dat geen regel matcht, wordt geweigerd.

| Typische vergissing | Gevolg |
|---|---|
| alleen één deny toevoegen | ook gewenst overige verkeer kan door implicit deny stoppen |
| nieuwe permit onder oude brede deny plaatsen | nieuwe regel wordt nooit effectief |
| oude named ACL aanvullen zonder sequence te controleren | Packet Tracer behoudt onverwachte volgorde |
| alleen config lezen, geen hit counters bekijken | onduidelijk welke regel werkelijk matcht |

Voorbeeld uit het labo:

Een inbound ACL op VLAN 50 die een breed intern bereik blokkeert, kan ook verkeer naar
de eigen gateway blokkeren als die gateway binnen het gematchte bereik valt. Daarom
moet je het precieze pad en de volgorde begrijpen, niet alleen regels kopiëren.

### 10.5 Lifecycle van firewallregels

Een correcte regel kan later overbodig of fout worden.

| Lifecyclefase | Beheervraag |
|---|---|
| aanvraag | welke businessreden en eigenaar bestaan? |
| beoordeling | is de stroom zo klein mogelijk? |
| implementatie | op welk controlepunt en in welke volgorde? |
| validatie | slagen allow-, deny- en regressietests? |
| monitoring | wordt de regel gebruikt en ontstaan afwijkingen? |
| review | bestaat de applicatie of leverancierstoegang nog? |
| verwijdering | kan de regel veilig weg en is rollback voorzien? |

In productie:

> Voeg aan tijdelijke leveranciers- of migratieregels altijd een eigenaar en vervaldatum
> toe. "Tijdelijk" is geen technische toestand zonder opvolging.

Kernzin:

> Een firewallregelmatrix maakt toegang bespreekbaar vóór syntax en beheerbaar na de
> implementatie.

---

## 11. Van beleid naar technische regels

Een beleidszin beschrijft gewenst gedrag. Een technische regel moet dat gedrag precies
afdwingen op het gekozen platform.

### 11.1 Vertaalstappen

Gebruik deze volgorde:

```text
1. beleidszin
2. bron- en doelobject
3. dienst en initiator
4. verkeerspad
5. controlepunt en richting
6. regelvolgorde
7. logging
8. test en bewijs
```

Voorbeeldbeleid:

> Guests mogen interne zones niet bereiken, maar behouden gastinternet.

Conceptuele vertaling:

```text
deny   Guest -> Internal
allow  Guest -> Internet -> noodzakelijke diensten
```

Mogelijke ACL-denkwijze in het labo:

```text
deny   ip guest-subnet internal-subnets
permit ip guest-subnet any
```

Deze vereenvoudigde ACL zegt nog niet alles. Je moet ook bepalen:

- of DNS naar een interne resolver nodig is;
- of de eigen gateway bereikbaar moet blijven;
- welke interne subnetten exact onder `Internal` vallen;
- of `any` ook onverwachte private of VPN-routes omvat;
- of IPv6 apart wordt gefilterd;
- hoe return traffic verwerkt wordt.

### 11.2 Voorbeeld: alleen IT naar Management

Beleid:

> Alleen bevoegde IT-beheerders gebruiken SSH of HTTPS naar netwerkbeheerinterfaces.

Minimale labvertaling:

```text
permit tcp it-subnet management-subnet eq 22
permit tcp it-subnet management-subnet eq 443
deny   ip any management-subnet
```

Productievragen:

| Vraag | Waarom het labmodel niet volstaat |
|---|---|
| Is elk toestel in het IT-subnet een beheerhost? | subnetgebaseerd vertrouwen kan te breed zijn |
| Is een jump host verplicht? | centraliseert beheer, logging en hardening |
| Welke identiteit voert commando's uit? | IP-adres alleen identificeert geen persoon |
| Wordt MFA gebruikt? | beperkt misbruik van gestolen credentials |
| Zijn commando's en sessies gelogd? | maakt beheeracties auditbaar |
| Wat is het noodpad bij uitval? | beheer moet beschikbaar én gecontroleerd blijven |

### 11.3 Diensten bestaan uit afhankelijkheden

Een browsertest naar `https://app.example` kan meerdere stromen veroorzaken:

```text
client -> DNS resolver -> UDP/TCP 53
client -> webserver -> TCP 443
client -> identity provider -> TCP 443
client -> certificaatstatusdienst -> TCP 80/443, afhankelijk van ontwerp
```

Een firewallregel voor alleen de zichtbare applicatieserver kan dus onvoldoende zijn.
Open daarom niet meteen `any`. Breng de afhankelijkheden afzonderlijk in kaart.

| Symptoom | Mogelijke ontbrekende stroom |
|---|---|
| hostname werkt niet, IP-adres wel | DNS |
| login redirect faalt | identity provider of callbackpad |
| TLS-validatie faalt | tijd, certificaatketen of statuscontrole |
| app opent maar data ontbreekt | backend- of API-stroom |
| logs komen niet aan | syslog- of collectorstroom |

### 11.4 Logging als onderdeel van de regel

Niet elke toegelaten sessie hoeft op hetzelfde detailniveau gelogd te worden. Te veel
logging kan ruis en opslagproblemen veroorzaken. Te weinig logging maakt onderzoek
onmogelijk.

| Regeltype | Mogelijke loggingkeuze | Reden |
|---|---|---|
| Internet naar publieke dienst | sessiestart/einde en securityevents | blootgestelde dienst onderzoeken |
| deny naar Management | loggen en mogelijk alert | poging raakt zeer gevoelige zone |
| Guest naar Internal deny | tellers en geselecteerde logs | scans en foutconfiguratie herkennen |
| veelgebruikte interne HTTPS allow | sessie- of samenvattingslogs | gebruik aantonen zonder elk pakket te loggen |
| tijdelijke leveranciersregel | uitgebreide logging | uitzonderlijk en tijdelijk risico opvolgen |

Een deny-log beantwoordt idealiter:

- wanneer gebeurde het?
- wat waren bron en bestemming?
- welke poort en welk protocol?
- welke interface of zone was betrokken?
- welke regel of policy besliste?
- was dit één fout pakket of herhaald gedrag?

### 11.5 Labvereenvoudiging versus productie

| Thema | BluePeak-labo | Productie |
|---|---|---|
| firewall | router met stateless ACL's | vaak redundante stateful firewalls |
| zones | meestal één VLAN per zone | meerdere segmenten, VRF's of distributed policies mogelijk |
| identiteit | vooral bron-IP of subnet | koppeling aan gebruiker, toestelstatus of rol mogelijk |
| beheer | IT-subnet en VTY ACL | jump host, AAA, MFA, privileged access management |
| logging | `show access-lists` en beperkte events | centrale syslog/SIEM, tijdsynchronisatie en alerts |
| applicatiecontrole | protocol en poort | soms applicatie-, URL- of TLS-context |
| beschikbaarheid | één `R-FW` | redundant ontwerp en getest failovergedrag |

Het labo is geen slecht ontwerp omdat het vereenvoudigd is. Het wordt wel fout als je
de vereenvoudiging zonder uitleg als volledig productieontwerp presenteert.

---

## 12. Security testen

Security testen bewijst twee tegengestelde eigenschappen:

1. noodzakelijke communicatie werkt;
2. niet-toegestane communicatie werkt niet.

Alleen positieve tests bewijzen functionaliteit, geen begrenzing. Alleen negatieve
tests bewijzen blokkering, maar niet dat de bedrijfsdienst nog bruikbaar is.

### 12.1 Drie soorten tests

| Testsoort | Vraag | Voorbeeld |
|---|---|---|
| positieve test | werkt wat moet werken? | `PC-STAFF` opent `SRV-APP` via HTTPS |
| negatieve test | faalt wat niet mag werken? | `PC-GUEST` bereikt `SRV-APP` niet |
| begrenzingstest | is alleen de bedoelde dienst open? | HTTPS werkt, SSH naar dezelfde server faalt |

Een sterke regeltest gebruikt dus minstens een paar:

```text
allow-test: verwachte bron + verwachte dienst -> succes
deny-test: niet-bevoegde bron of niet-toegestane dienst -> blokkering
```

### 12.2 Schrijf de verwachting vooraf

Noteer vóór de test:

| Veld | Voorbeeld |
|---|---|
| test-ID | `GUEST-02` |
| bron | `PC-GUEST`, `10.30.50.101` |
| doel | `SRV-APP`, `10.30.40.10` |
| dienst | HTTPS/TCP 443 |
| verwacht | geblokkeerd |
| beleidsreden | Guests mogen Internal niet bereiken |
| bewijsbron | clientresultaat plus ACL-hitcounter of firewalllog |

Als je de verwachting pas na de test formuleert, bestaat het risico dat je elk
resultaat achteraf als juist verklaart.

### 12.3 Ping is geen applicatietest

`ping` test ICMP echo. Het zegt niet of HTTPS, SSH of DNS werkt.

| Resultaat | Wat mag je besluiten? | Wat niet? |
|---|---|---|
| ping slaagt | ICMP echo werkt over het pad | de webapplicatie of firewallpolicy is volledig correct |
| ping faalt | geen echoantwoord ontvangen | de host of alle TCP-diensten zijn zeker onbereikbaar |
| HTTPS slaagt | TCP/443 en de applicatierespons werken | andere poorten zijn geblokkeerd |
| SSH faalt | de SSH-test kreeg geen bruikbare sessie | zonder logs niet waar de blokkering zit |

Gebruik een test die past bij de regel:

| Te testen dienst | Geschikte observatie |
|---|---|
| ICMP | `ping` |
| routepad | `traceroute` of `tracert`, met aandacht voor filtering |
| HTTP/HTTPS | browser, `curl` of applicatieclient |
| SSH | SSH-client en server-/firewalllog |
| DNS | naamopzoeking en resolverlog |
| ACL-match | `show access-lists` en hit counters |
| interfaceplaatsing | `show ip interface` en running config |
| NAT-publicatie | NAT-configuratie en vertaaltabel waar ondersteund |

### 12.4 Clientresultaat en controlepunt samen lezen

Eenzelfde foutmelding kan meerdere oorzaken hebben.

| Clientobservatie | Mogelijke oorzaak | Aanvullend bewijs |
|---|---|---|
| timeout | firewall deny, routeprobleem, host down of service luistert niet | route, ARP, interface, log en counter controleren |
| connection refused | host bereikbaar maar poort gesloten of service gestopt | serverstatus en TCP-observatie |
| hostname onbekend | DNS-probleem | test IP-adres en DNS-query afzonderlijk |
| login geweigerd | applicatie-authenticatie of autorisatie | applicatie- en identitylogs |
| ping faalt, HTTPS werkt | ICMP geblokkeerd maar applicatie toegestaan | dit kan correct beleid zijn |

Een mislukte verbinding bewijst pas een securityregel wanneer je ook de reden kan
aantonen. Anders kan een kabelprobleem ten onrechte als geslaagde firewalltest gelden.

Kernidee:

> Een verwachte mislukking is alleen geldig bewijs als de bedoelde beveiligingsregel de
> oorzaak van die mislukking is.

### 12.5 Minimale testmatrix voor BluePeak

| Test | Verwacht | Waarom test je dit? | Zinvol bewijs |
|---|---|---|---|
| `PC-STAFF` naar `SRV-APP` via HTTPS | werkt | noodzakelijke Staff-app | browserresultaat en allow-counter |
| `PC-STAFF` naar Management via SSH/HTTPS | faalt | Staff heeft geen beheerrol | timeout/deny en policycounter |
| `PC-FINANCE` naar `SRV-FIN` | werkt | financeproces blijft beschikbaar | applicatierespons |
| `PC-GUEST` naar internet | werkt | guestdienst blijft bruikbaar | externe respons en NAT-observatie |
| `PC-GUEST` naar `SRV-APP` | faalt | Guest-isolatie | deny-counter op `GUEST_IN` |
| `PC-GUEST` naar eigen gateway | werkt volgens labontwerp | ACL blokkeert niet onbedoeld de gateway | ping plus eerste ACL-regel |
| `PC-IT` naar netwerkmanagement via SSH | werkt | gecontroleerd beheer | SSH-login en VTY-config |
| `CAM-IOT` naar `SRV-FIN` | faalt | IoT heeft geen financebehoefte | deny-counter op `IOT_IN` |
| ISP-zijde naar `SRV-WEB-DMZ` via HTTPS | werkt | publieke dienst staat in DMZ | HTTPS-respons en NAT-regel |
| ISP-zijde naar interne `SRV-APP` | faalt | intern wordt niet gepubliceerd | ontbrekende NAT/allow en testresultaat |
| `SRV-WEB-DMZ` naar `SRV-APP` | faalt tenzij expliciete backend vereist is | laterale beweging beperken | deny-counter op `DMZ_IN` |
| `SRV-WEB-DMZ` naar Management | faalt | beheerzone beschermen | deny-counter en clienttest |

### 12.6 Testvolgorde voor troubleshooting

Wanneer een resultaat afwijkt, wijzig niet meteen de ACL. Onderzoek systematisch:

1. **Controleer de testcontext.** Heeft de bron het verwachte IP, masker en gateway?
2. **Controleer de lokale verbinding.** Is de interface up en is het juiste VLAN actief?
3. **Teken het routepad.** Welke gateway en interfaces worden gebruikt?
4. **Controleer routing en ARP.** Is er een pad naar de bestemming en terug?
5. **Controleer de dienst.** Luistert de server op de bedoelde poort?
6. **Controleer policyplaatsing.** Staat de ACL op de juiste interface en richting?
7. **Controleer regelvolgorde.** Welke eerste regel matcht?
8. **Controleer counters en logs.** Verandert de verwachte teller tijdens de test?
9. **Wijzig één oorzaak tegelijk.** Test daarna opnieuw, inclusief regressietests.

Gebruik het patroon:

```text
verwacht -> observeer -> lokaliseer -> verklaar -> corrigeer -> hertest
```

---

## 13. Logging, monitoring en auditability

Filtering bepaalt wat mag. Logging helpt aantonen wat werkelijk gebeurde.

Securityarchitectuur zonder zichtbaarheid heeft drie problemen:

| Probleem | Gevolg |
|---|---|
| fouten zijn moeilijk te lokaliseren | beheerders openen mogelijk te brede tijdelijke regels |
| aanvallen blijven langer onopgemerkt | scans en mislukte beheerpogingen krijgen geen opvolging |
| wijzigingen zijn moeilijk te verantwoorden | bij een audit ontbreekt bewijs van werking en beheer |

Nuttige observaties zijn:

| Bron | Wat kan je ermee aantonen? |
|---|---|
| firewall allow-log | welke sessie door welke policy werd toegelaten |
| firewall deny-log | welke grens een verboden poging blokkeerde |
| ACL-hitcounter | dat verkeer een specifieke labregel raakte |
| NAT-tabel of -config | naar welk intern adres een publieke dienst vertaald wordt |
| serverlog | of de aanvraag de applicatie werkelijk bereikte |
| authenticatielog | welke identiteit toegang probeerde te krijgen |
| configuratiehistoriek | wie welke regel wanneer wijzigde |
| monitoringalert | of herhaald of afwijkend gedrag werd gedetecteerd |

### 13.1 Logcontext

Een logregel is pas bruikbaar met voldoende context:

| Context | Waarom nodig? |
|---|---|
| correcte tijd | events uit firewall, client en server op één tijdlijn plaatsen |
| bron en bestemming | betrokken systemen identificeren |
| protocol en poort | de dienst herkennen |
| interface of zone | de trust boundary bepalen |
| policy-ID of regelnaam | de technische beslissing verklaren |
| actie en reden | allow, deny, reset of timeout onderscheiden |
| identiteit indien beschikbaar | netwerkadres aan een gebruiker of service koppelen |

Daarom is tijdsynchronisatie ook een securityvereiste. Zonder consistente tijd wordt
incidentonderzoek onbetrouwbaar.

### 13.2 Logging is geen monitoring

| Begrip | Betekenis |
|---|---|
| logging | gebeurtenissen registreren |
| monitoring | gebeurtenissen actief opvolgen en trends herkennen |
| alerting | bij relevante voorwaarden een melding genereren |
| auditing | achteraf controleren of beleid en beheer aantoonbaar kloppen |

Een firewall die miljoenen denies opslaat maar niemand waarschuwt bij herhaalde SSH-
pogingen naar Management levert data, maar nog geen effectieve detectie.

### 13.3 Bewijs verzamelen in de workshop

Voor elk belangrijk resultaat verzamel je bij voorkeur bewijs aan twee kanten:

```text
clientobservatie + controlepuntobservatie
```

Voorbeeld:

| Test | Clientbewijs | Netwerkbewijs |
|---|---|---|
| Guest naar server geblokkeerd | browser of ping faalt | teller van relevante deny stijgt |
| IT naar management toegestaan | SSH-sessie opent | allow-counter of VTY-log |
| publieke website wijst naar DMZ | website antwoordt vanaf ISP | NAT-regel verwijst naar `10.30.70.10` |

Neem geen wachtwoorden, secrets of andere gevoelige informatie op in screenshots of
verslagen.

Kernzin:

> Logging maakt een beleidsbeslissing observeerbaar; monitoring maakt afwijkend gedrag
> opvolgbaar.

---

## 14. Risico's professioneel formuleren

Een technische vaststelling is nog geen volledige risicoanalyse.

Zwak:

> De firewall is slecht.

Sterker:

> `PC-GUEST` in VLAN 50 kan `SRV-APP` in de interne serverzone bereiken. Daardoor kan
> een onbeheerd gasttoestel interne diensten scannen of aanvallen. Blokkeer Guest naar
> Internal aan de guest-boundary en valideer dit met een negatieve HTTPS-test en een
> ACL-hitcounter.

Een bruikbare formulering bevat:

| Onderdeel | Vraag |
|---|---|
| vaststelling | wat observeer je concreet? |
| oorzaak | welke ontwerp- of configuratiefout maakt dit mogelijk? |
| dreiging | welk misbruik kan plaatsvinden? |
| impact | welke systemen, data of bedrijfsprocessen worden geraakt? |
| maatregel | welke gerichte verbetering beperkt het risico? |
| validatie | welke test bewijst de verbetering? |

### 14.1 Voorbeelden bij BluePeak

| Vaststelling | Risico en impact | Gerichte maatregel | Validatie |
|---|---|---|---|
| Guest bereikt `SRV-APP` | onbeheerde host kan intern scannen of aanvallen | Guest naar Internal blokkeren | Guest-internet werkt; Guest naar server faalt |
| Staff bereikt Management | gestolen usercredentials kunnen infrastructuurbeheer raken | alleen gecontroleerd IT-pad toelaten | Staff faalt; IT slaagt via SSH |
| NAT wijst naar interne `SRV-APP` | publieke aanval komt direct in Internal binnen | publiceer `SRV-WEB-DMZ` | NAT-config en externe HTTPS-test |
| DMZ bereikt heel VLAN 40 | compromis van publieke host leidt tot laterale beweging | default deny, alleen concrete backend indien nodig | DMZ naar niet-benodigde server faalt |
| IoT bereikt `SRV-FIN` | zwak beheerd toestel raakt gevoelige financefunctie | alleen noodzakelijke IoT-appstroom | bedoelde app werkt; finance faalt |
| Finance-server deelt een breed VLAN | hosts binnen VLAN 40 kunnen routerfilter omzeilen | apart segment of host/workloadfiltering | host-naar-hostbeleid testen |

### 14.2 Prioriteren

Niet elk risico kan tegelijk opgelost worden. Prioriteer op:

| Factor | Voorbeeld |
|---|---|
| kans | publieke DMZ-host wordt vaker aangevallen dan een offline labserver |
| impact | Management-compromis kan het hele netwerk beïnvloeden |
| blootstelling | internettoegang vergroot het aanvalsoppervlak |
| misbruikgemak | een brede `any any` vraagt weinig kennis van de aanvaller |
| detecteerbaarheid | ongecontroleerd east-west verkeer kan lang onzichtbaar blijven |
| herstelbaarheid | verlies van beheer of configuratie kan herstel vertragen |

Een eenvoudige prioriteit is onvoldoende zonder reden. Schrijf bijvoorbeeld:

> Managementtoegang beperken heeft prioriteit hoog omdat gewone staffclients momenteel
> een zone kunnen bereiken waarmee de volledige netwerkinfrastructuur beheerd wordt.

---

## 15. Methodische ontwerpaanpak

Gebruik bij een nieuw of bestaand netwerk een vaste werkwijze.

### Stap 1: inventariseer assets en functies

Documenteer:

- gebruikersgroepen;
- clients en onbeheerde toestellen;
- interne en publieke servers;
- gevoelige data en applicaties;
- netwerk- en securitybeheer;
- externe koppelingen, VPN en internetdiensten.

Output:

> Een lijst van systemen met eigenaar, functie, gevoeligheid en technische locatie.

### Stap 2: breng bestaande verkeersstromen in kaart

Gebruik documentatie, interviews, logs en gecontroleerde tests.

| Te documenteren | Voorbeeld |
|---|---|
| bron | Staff |
| doel | `SRV-APP` |
| dienst | HTTPS |
| initiator | client |
| frequentie | tijdens werkdagen |
| eigenaar | applicatiebeheer |

Observeer verkeer, maar verwar bestaand verkeer niet met noodzakelijk verkeer. Malware,
oude applicaties en foutconfiguraties genereren ook verkeer.

### Stap 3: ontwerp zones en trust boundaries

Groepeer systemen met vergelijkbaar beleid. Duid daarna aan waar verkeer tussen
verschillende contexten passeert.

Controlepunt:

> Kan je voor elke zone uitleggen welke systemen ze bevat, waarom ze samen horen en
> welke zone-overschrijdende toegang nodig is?

### Stap 4: stel een regelmatrix op

Begin met expliciete noodzakelijke allow-regels. Voeg daarna duidelijke standaard-
denybeslissingen per boundary toe.

Vermijd dat de matrix alleen subnetten bevat. Noteer ook businessreden, eigenaar en
testmethode.

### Stap 5: kies afdwingingspunten

Controleer:

- werkelijk routepad;
- interface en richting;
- stateful of stateless gedrag;
- Layer 2-verkeer binnen een subnet;
- redundante en alternatieve paden;
- logging en beschikbaarheid van het controlepunt.

### Stap 6: implementeer gecontroleerd

Maak vóór de wijziging:

- configuratieback-up;
- impactanalyse;
- testplan;
- rollbackplan;
- onderhouds- of communicatieafspraak waar nodig.

High availability, wijzigingen en rollback worden in hoofdstuk 4 verder uitgediept.

### Stap 7: valideer en monitor

Voer uit:

- positieve tests;
- negatieve tests;
- begrenzingstests;
- regressietests van bestaande diensten;
- controle van logs, counters en alerts.

### Stap 8: beheer de lifecycle

Review regels wanneer:

- een applicatie verhuist of stopt;
- een leverancier geen toegang meer nodig heeft;
- een subnet of zone wijzigt;
- een kwetsbaarheid nieuwe beperkingen vraagt;
- een tijdelijke uitzondering vervalt;
- logging langdurig geen gebruik toont.

Kernzin:

> Security architecture is geen eenmalige tekening, maar een beheerde cyclus van
> ontwerpen, afdwingen, testen en herzien.

---

## 16. BluePeak: van scenario naar ontwerp

De workshop gebruikt deze vereenvoudigde topologie:

```text
                         Internet / ISP
                              |
                           [ R-FW ]
                              |
                       802.1Q trunk
                              |
                         [ SW-CORE ]
                         /     |     \
                    access   DMZ    Management
                    switches server  jump host
                       |
       Staff - Finance - IT - Servers - Guests - IoT
```

De zone-indeling is:

| Zone | VLAN | Subnet | Voorbeeldhost |
|---|---:|---|---|
| Staff | 10 | `10.30.10.0/24` | `PC-STAFF` |
| Finance | 20 | `10.30.20.0/24` | `PC-FINANCE` |
| IT | 30 | `10.30.30.0/24` | `PC-IT` |
| Servers | 40 | `10.30.40.0/24` | `SRV-APP`, `SRV-FIN` |
| Guests | 50 | `10.30.50.0/24` | `PC-GUEST` |
| IoT | 60 | `10.30.60.0/24` | `CAM-IOT` |
| DMZ | 70 | `10.30.70.0/24` | `SRV-WEB-DMZ` |
| Management | 99 | `10.30.99.0/24` | `SRV-MGMT-JUMP`, switchmanagement |

### 16.1 Wat moet je in de beginsituatie onderzoeken?

| Onderzoeksvraag | Waarom belangrijk? |
|---|---|
| Kan Guest interne servers bereiken? | toont of de guest-boundary echt wordt afgedwongen |
| Kan Staff Management bereiken? | controleert bescherming van infrastructuurbeheer |
| Naar welke host wijst de publieke NAT-regel? | toont of de publieke dienst werkelijk in de DMZ staat |
| Kan de DMZ naar VLAN 40 of 99? | beoordeelt impact na compromis van de publieke host |
| Kan IoT alle servers bereiken? | controleert least privilege voor zwakke endpoints |
| Kan Finance alleen de finance-app bereiken? | beoordeelt gevoelig applicatiebeleid |
| Welke ACL matcht en waar staat ze? | verbindt beleidsfout met technische oorzaak |

### 16.2 De router is een firewallmodel

`R-FW` routeert tussen VLAN's via subinterfaces en gebruikt ACL's om boundaries te
simuleren.

Dat maakt volgende concepten zichtbaar:

- een ACL heeft een interface en richting;
- regels worden in volgorde verwerkt;
- een brede permit kan specifieke denies overschaduwen;
- een impliciete deny kan noodzakelijke toegang blokkeren;
- hit counters helpen bepalen welke regel matcht;
- NAT-publicatie moet naar de DMZ-host wijzen.

De beperkingen zijn even belangrijk:

| Labo | Wat zou productie sterker maken? |
|---|---|
| één routerfirewall | redundante stateful firewalls |
| subnetgebaseerde IT-toegang | jump host, individuele identiteit, AAA en MFA |
| beperkte Packet Tracer-logging | centrale logs met betrouwbare tijd en alerts |
| eenvoudige poortregels | applicatie- en identitycontext waar relevant |
| één VLAN voor twee interne servers | verdere segmentatie voor gevoelige workloads |

### 16.3 Sterke eindconclusie

Een goede conclusie bevat niet alleen dat regels "beter" moeten. Ze verbindt
vaststelling, risico en prioriteit.

Voorbeeld:

> BluePeak heeft herkenbare VLAN's en zones, maar de beginsituatie dwingt de
> trust boundaries onvoldoende af. Vooral Guest naar Internal, Staff naar Management,
> IoT naar Servers en DMZ naar Internal zijn te breed. De publieke NAT-regel moet naar
> `SRV-WEB-DMZ` wijzen. De eerste prioriteiten zijn Guest isoleren, beheer beperken tot
> een gecontroleerd IT-pad, DMZ-uitgaand verkeer standaard blokkeren en IoT alleen de
> noodzakelijke applicatiestroom geven. Elke wijziging moet met een positieve en een
> negatieve test plus ACL- of firewallbewijs gevalideerd worden.

---

## 17. Typische fouten en betere aanpakken

| Fout | Waarom problematisch? | Betere aanpak | Controle |
|---|---|---|---|
| VLAN's maken zonder interzonebeleid | Layer 3-bereikbaarheid blijft te breed | zones en boundaries expliciet afdwingen | negatieve test tussen zones |
| vertrouwen baseren op zonenaam | een host wordt niet veilig door zijn label | risico, beheer en toegang beoordelen | inhoud en beleid van zone controleren |
| `permit ip any any` als oplossing | bron, doel en dienst zijn onbeperkt | specifieke applicatiestromen | rule review en begrenzingstest |
| deny onder brede permit plaatsen | eerste match laat verkeer al toe | volgorde van specifiek naar algemeen | counters per regel bekijken |
| implicit deny vergeten | noodzakelijke overige stroom stopt | volledige policy inclusief permits ontwerpen | regressietests uitvoeren |
| ACL op verkeerde interface | verkeer passeert de regel niet | pad tekenen en richting bepalen | `show ip interface` |
| alleen internetedge filteren | laterale beweging blijft mogelijk | risicovolle east-west boundaries beveiligen | interzone-tests |
| publieke server intern publiceren | compromis komt direct in Internal | aparte DMZ en beperkte backendstromen | NAT-doel en DMZ-test controleren |
| DMZ vrij naar intern laten gaan | bufferzone verliest haar waarde | default deny vanaf DMZ | DMZ naar meerdere interne doelen testen |
| Management alleen in apart VLAN zetten | elke gerouteerde zone kan mogelijk nog verbinden | toegang beperken tot jump host of IT-policy | Staff deny en IT allow testen |
| IoT als gewone client behandelen | zwak beheerbaar toestel krijgt te veel bereik | aparte zone met minimale stromen | IoT naar finance en management testen |
| NAT als security zien | vertaling zegt niets over gewenst beleid | NAT en firewallregel apart beoordelen | publicatie- en denytest |
| alleen ping gebruiken | ICMP bewijst de applicatieregel niet | test werkelijke dienst | HTTPS-, SSH- of DNS-test |
| alleen succesvolle toegang testen | te brede policy blijft onzichtbaar | negatieve en begrenzingstests | niet-bevoegde bron en verkeerde poort testen |
| timeout automatisch als geslaagde deny zien | route- of serverfout kan oorzaak zijn | client- en controlepuntbewijs combineren | log of counter correleren |
| elke deny loggen zonder plan | ruis verbergt relevante events | logging per risico afstemmen | volume en alerts reviewen |
| tijdelijke regel zonder einddatum | uitzondering wordt permanent | eigenaar en vervaldatum | periodieke rule review |
| IPv6 negeren | hosts kunnen IPv4-policy omzeilen | gelijkwaardig IPv4- en IPv6-beleid | beide protocolstacks testen |
| zelfde VLAN voor gevoelige en gewone servers | routerfirewall ziet onderling verkeer niet | apart segment of hostfiltering | Layer 2-pad analyseren |

Gebruik bij troubleshooting deze categorieën:

| Categorie | Kernvraag |
|---|---|
| requirement | hoort deze stroom werkelijk te werken? |
| adressering | gebruiken bron en doel de verwachte adressen? |
| routing | passeert verkeer het veronderstelde controlepunt? |
| policy | matchen bron, doel, dienst en richting? |
| volgorde | welke eerste regel matcht? |
| state | wordt return traffic als deel van de sessie herkend? |
| applicatie | luistert de dienst en werkt de volledige afhankelijkheidsketen? |
| bewijs | welke log, counter of output bevestigt de oorzaak? |

---

## 18. Controlevragen en denkvragen

### 18.1 Begripscontrole

1. Waarom is een VLAN niet automatisch een securityzone?
2. Wat is het verschil tussen een beleidsregel en een technische firewallregel?
3. Waarom zijn er rond een DMZ minstens twee relevante trust boundaries?
4. Wat onthoudt een stateful firewall dat een klassieke stateless ACL niet onthoudt?
5. Waarom is NAT geen vervanging voor firewallbeleid?
6. Wat is het verschil tussen north-south en east-west traffic?
7. Waarom kan een impliciete deny zowel nuttig als verwarrend zijn?
8. Waarom bewijst een geslaagde ping niet dat een HTTPS-policy correct is?
9. Wat is het verschil tussen logging en monitoring?
10. Waarom heeft een tijdelijke firewallregel een eigenaar en vervaldatum nodig?

### 18.2 Toepassingsvragen

1. Een guestclient kan internet bereiken en ook de interne DNS-server gebruiken. Welke
   informatie heb je nodig voor je beslist of dat laatste een fout is?
2. `SRV-APP` en `SRV-FIN` staan in hetzelfde VLAN. Kan een ACL op hun routergateway
   verkeer tussen beide servers altijd blokkeren? Verklaar.
3. Een reverse proxy in de DMZ moet een interne applicatie bereiken. Formuleer een
   least privilege-regel en een bijbehorende negatieve test.
4. Staff naar Management faalt, maar de teller van de bedoelde deny-regel blijft nul.
   Welke mogelijke oorzaken onderzoek je?
5. Een firewall laat TCP/443 naar een webserver toe. Waarom kan die server nog altijd
   via de webapplicatie worden aangevallen?
6. Een organisatie activeert default deny en opent daarna tijdelijk `any any` omdat de
   applicatie niet werkt. Welke betere diagnosevolgorde stel je voor?
7. Een VPN-gebruiker heeft een geldige tunnel. Waarom betekent dit niet automatisch
   dat de gebruiker alle interne zones mag bereiken?
8. Welke bewijzen verzamel je om aan te tonen dat Internet naar DMZ wel werkt, maar
   Internet naar Internal niet?

### 18.3 Criteria voor een sterk antwoord

Een sterk antwoord:

- benoemt bron, doel, dienst en initiator;
- koppelt de stroom aan een bedrijfstaak of risico;
- duidt de trust boundary en het controlepunt aan;
- houdt rekening met regelvolgorde en return traffic;
- onderscheidt labgedrag van productieontwerp;
- stelt minstens één positieve en één negatieve test voor;
- noemt geschikt bewijs, zoals logs, counters of applicatie-output;
- vermijdt absolute uitspraken zoals "apart VLAN is veilig".

---

## 19. Samenvatting

Security architecture brengt bedrijfsbehoeften, netwerktopologie en technische
maatregelen samen.

| Concept | Wat moet je onthouden? |
|---|---|
| architectuur | bepaal eerst gewenst gedrag en risico, daarna pas syntax |
| defense in depth | één falende laag mag niet het volledige netwerk blootstellen |
| least privilege | laat niet meer toegang toe dan aantoonbaar nodig |
| zone | groepeert systemen met vergelijkbaar securitybeleid |
| trust boundary | grens waar een controlebeslissing nodig is |
| DMZ | begrenst zowel publieke toegang als vervolgverkeer naar intern |
| firewall placement | een regel werkt alleen op het werkelijke verkeerspad |
| stateful filtering | gebruikt sessiecontext voor onder meer return traffic |
| NAT | vertaalt adressen, maar bepaalt niet het securitybeleid |
| east-west security | beperkt laterale beweging binnen de organisatie |
| regelmatrix | vertaalt requirements naar beheerbare allow- en denybeslissingen |
| testing | combineert positieve, negatieve en begrenzingstests |
| bewijs | verbindt clientresultaat met logs, counters of configuratie-output |
| lifecycle | regels moeten aangevraagd, getest, herzien en verwijderd worden |

De vaste redeneerlijn is:

```text
Waarom is de stroom nodig?
Welke bron start naar welke dienst?
Welke trust boundary wordt gekruist?
Waar wordt het beleid afgedwongen?
Welke regel matcht als eerste?
Hoe werkt het antwoordpad?
Welke positieve test bewijst de functie?
Welke negatieve test bewijst de grens?
Welke log of counter bevestigt de oorzaak?
```

Kernzin:

> Een enterprise-netwerk is pas veilig ontworpen wanneer je voor elke toegelaten
> verkeersstroom kan uitleggen waarom ze nodig is, waar ze gecontroleerd wordt en hoe
> je bewijst dat alle niet-toegestane stromen geblokkeerd blijven.
