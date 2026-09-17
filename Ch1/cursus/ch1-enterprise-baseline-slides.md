---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks — Hoofdstuk 1
style: |
  :root {
    --ink: #17212b;
    --blue: #153b5b;
    --cyan: #008f95;
    --sky: #dff3f4;
    --paper: #f7f8f6;
    --muted: #5d6972;
    --red: #b42318;
    --green: #16794b;
    --amber: #b66a00;
  }
  section {
    font-family: Aptos, "Segoe UI", sans-serif;
    color: var(--ink);
    background: white;
    padding: 52px 68px;
    font-size: 29px;
  }
  h1, h2 { color: var(--blue); }
  h1 { font-size: 1.82em; margin-bottom: 0.5em; }
  h2 { font-size: 1.22em; margin-bottom: 0.45em; }
  h3 { color: var(--cyan); margin: 0 0 0.35em; }
  p, li { line-height: 1.28; }
  strong { color: var(--blue); }
  blockquote {
    border-left: 8px solid var(--cyan);
    background: var(--sky);
    padding: 0.45em 0.8em;
    color: var(--blue);
  }
  table { width: 100%; font-size: 0.68em; }
  th { background: var(--blue); color: white; }
  td, th { padding: 0.4em 0.55em; }
  code { background: #edf1f4; color: #8a1c1c; }
  pre {
    background: var(--ink);
    color: #f5f7f8;
    border-radius: 8px;
    padding: 0.7em 0.9em;
  }
  section.title {
    background: linear-gradient(135deg, var(--blue) 0%, #245b7c 68%, var(--cyan) 100%);
    color: white;
  }
  section.title h1,
  section.title h2,
  section.title strong { color: white; }
  section.title footer { color: rgba(255,255,255,.78); }
  section.divider {
    background: var(--blue);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.divider h1,
  section.divider h2 { color: white; }
  section.question { background: var(--paper); }
  section.question h1,
  section.question h2 { color: var(--cyan); }
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 38px;
  }
  .columns-40-60 {
    display: grid;
    grid-template-columns: 0.8fr 1.2fr;
    gap: 38px;
  }
  .four {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }
  .card {
    background: var(--paper);
    border-top: 5px solid var(--cyan);
    padding: 15px 19px;
  }
  .card p { margin: 0.2em 0; }
  .bad { color: var(--red); }
  .good { color: var(--green); }
  .warn { color: var(--amber); }
  .small { font-size: 0.72em; }
  .tiny { font-size: 0.61em; }
  .muted { color: var(--muted); }
  .big-claim {
    font-size: 1.48em;
    line-height: 1.18;
    color: var(--blue);
    font-weight: 700;
  }
  .pipeline {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr auto 1fr;
    align-items: stretch;
    gap: 9px;
    margin-top: 1em;
  }
  .pipeline .node {
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    padding: 14px 11px;
    text-align: center;
    font-size: 0.67em;
  }
  .pipeline .arrow {
    align-self: center;
    color: var(--cyan);
    font-size: 1.2em;
    font-weight: 700;
  }
  .zones {
    display: grid;
    grid-template-columns: 1fr auto 1.15fr auto 1fr;
    align-items: center;
    gap: 14px;
    margin-top: 0.6em;
  }
  .zone-stack { display: grid; gap: 10px; }
  .zone {
    padding: 10px 14px;
    text-align: center;
    background: var(--paper);
    border-left: 6px solid var(--cyan);
    font-size: 0.74em;
  }
  .control {
    padding: 22px 15px;
    text-align: center;
    background: var(--blue);
    color: white;
    font-size: 0.73em;
  }
  .control strong { color: white; }
  .arrow-large { color: var(--cyan); font-size: 1.35em; font-weight: 700; }
  .steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 13px;
  }
  .step {
    min-height: 106px;
    padding: 12px 14px;
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    font-size: 0.72em;
  }
  .step strong { display: block; font-size: 1.15em; margin-bottom: 0.25em; }
  .tag {
    display: inline-block;
    background: var(--sky);
    color: var(--blue);
    padding: 0.16em 0.5em;
    margin: 0.1em 0.12em;
    font-size: 0.72em;
    font-weight: 700;
  }
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

# Enterprise Networks

## Hoofdstuk 1 — Enterprise baseline en design

**Van een werkend campusnetwerk naar een professioneel beheerd netwerk**

---

# NetNova groeit — het netwerk moet mee

Vandaag:

- één gebouw en enkele VLAN's;
- één router voor routing, NAT/PAT en ACL's;
- internet en interne server zijn bereikbaar.

Morgen:

<span class="tag">meer medewerkers</span>
<span class="tag">extra diensten</span>
<span class="tag">thuiswerk</span>
<span class="tag">partners</span>
<span class="tag">strengere security</span>
<span class="tag">sneller herstel</span>

> Wat vandaag werkt, kan morgen een risico of bottleneck zijn.

---

<!-- _class: question -->

## Startvraag

# Het netwerk werkt.

# Maar is het ook professioneel?

Bespreek kort: **welk bewijs heb je nodig om dat te beoordelen?**

---

# Leerdoelen

Na deze les kan je:

1. een werkend campusnetwerk en een enterprise-ready netwerk vergelijken;
2. ontwerpen beoordelen op schaalbaarheid, betrouwbaarheid, security en beheerbaarheid;
3. VLAN's en subnetten vertalen naar zones en vereiste verkeersstromen;
4. configuratie, operationele toestand en testbewijs van elkaar onderscheiden;
5. een bestaand netwerk methodisch analyseren en documenteren;
6. risico's en concrete, toetsbare verbeteringen formuleren.

---

# De lat verschuift van connectiviteit naar controle

| Technisch werkend | Professioneel beheerd |
|---|---|
| Toestellen hebben verbinding | Verbindingen zijn bewust ontworpen |
| VLAN's bestaan | VLAN's passen in een zone- en securitymodel |
| ACL's laten of blokkeren verkeer | ACL's volgen gedocumenteerde requirements |
| IP-adressen zijn correct | Het IP-plan is logisch en uitbreidbaar |
| Problemen worden geprobeerd | Troubleshooting gebeurt methodisch |
| Security komt achteraf | Security zit in het ontwerp |

> De vraag is niet alleen **of** het werkt, maar ook **waarom**, **voor wie** en **onder welke voorwaarden**.

---

# Goed beheer verbindt behoefte met bewijs

<div class="pipeline">
  <div class="node"><strong>Bedrijfsbehoefte</strong><br>wat heeft de organisatie nodig?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Requirement</strong><br>wat moet wel en niet kunnen?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Ontwerp</strong><br>zones, paden en controles</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Configuratie</strong><br>trunks, routing, ACL, NAT</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Test & bewijs</strong><br>komt gedrag overeen?</div>
</div>

Een succesvolle ping zonder vooraf bepaald verwacht resultaat bewijst weinig.

---

# Enterprise-ready betekent evenwicht op vier domeinen

<div class="four">
  <div class="card"><strong>Schaalbaar</strong><br>Kan het ontwerp groeien zonder grote herbouw?</div>
  <div class="card"><strong>Betrouwbaar</strong><br>Blijft de noodzakelijke dienst werken bij een fout?</div>
  <div class="card"><strong>Veilig</strong><br>Is toegang beperkt tot wat functioneel nodig is?</div>
  <div class="card"><strong>Beheerbaar</strong><br>Kan een andere beheerder begrijpen, wijzigen en herstellen?</div>
</div>

**Enterprise is niet “maximaal” op één as, maar onderbouwd over alle vier.**

---

# Schaalbaarheid vraagt groeiruimte én structuur

<div class="columns">
<div>

### Risicovol

Iedereen in `192.168.10.0/24`:

- één groot broadcast- en trustdomein;
- weinig ruimte voor gerichte policies;
- uitbreiding vraagt ingrijpende wijzigingen.

</div>
<div>

### Groeit gecontroleerd

| VLAN | Subnet | Functie |
|---:|---|---|
| 10 | `10.10.10.0/24` | Students |
| 20 | `10.10.20.0/24` | Staff |
| 30 | `10.10.30.0/24` | Servers |
| 40 | `10.10.40.0/24` | Guests |
| 99 | `10.10.99.0/24` | Management |

</div>
</div>

**Groeivraag:** past een nieuwe afdeling in het bestaande VLAN-, subnet- en zoneplan?

---

# Betrouwbaarheid begint bij de impact van één defect

Een **single point of failure** is één onderdeel waarvan het falen een grote dienst onderbreekt.

<div class="columns">
<div class="card">

### Voorbeeld

Eén router is gateway voor alle VLAN's en gebruikt één uplink naar de core.

</div>
<div class="card">

### Onderzoek

- Welke diensten vallen uit?
- Bestaat een alternatief pad?
- Is herstel getest?
- Wordt de storing zichtbaar?

</div>
</div>

**Redundantie volgt uit impact, risico en budget — niet uit gewoonte.**

---

# Security bewijst zowel toegang als begrenzing

**Least privilege:** een gebruiker, toestel of systeem krijgt alleen de toegang die functioneel nodig is.

| Test | Voorbeeld | Wat bewijst dit? |
|---|---|---|
| Positief | Staff opent de interne webdienst | vereiste toegang blijft bruikbaar |
| Negatief | Guest opent die webdienst niet | de trustgrens wordt afgedwongen |
| Regressie | Staff werkt nog na een ACL-wijziging | correct bestaand gedrag bleef intact |

> Een netwerk is niet veilig omdat toegelaten verkeer werkt. Verboden verkeer moet aantoonbaar niet werken.

---

# Beheerbaarheid maakt kennis overdraagbaar

Een netwerk is slecht beheerbaar wanneer alleen de bouwer nog begrijpt hoe het werkt.

<div class="columns">
<div>

### Waarschuwingssignalen

- onduidelijke namen;
- geen IP- of VLAN-plan;
- onbekend doel van ACL-regels;
- wijzigingen niet traceerbaar;
- troubleshooting op basis van gokken.

</div>
<div>

### Professionele basis

- actuele documentatie;
- logging en monitoring;
- configuratieback-ups;
- test- en wijzigingsprocedure;
- duidelijk eigenaarschap.

</div>
</div>

---

# Een verbetering op één as kan een nieuwe fout creëren

## Enterprise design choice

| Keuze | Winst | Nieuwe aandacht |
|---|---|---|
| extra uplink | hogere beschikbaarheid | loopvrij ontwerp via STP, EtherChannel of routing |
| fijnere segmentatie | kleinere trust- en foutdomeinen | meer regels en documentatie |
| striktere ACL | kleiner aanvalsoppervlak | onvolledige requirements kunnen diensten breken |
| centrale netwerkdienst | consistenter beheer | centrale dienst wordt kritieke afhankelijkheid |
| uitgebreide logging | betere audit en troubleshooting | opslag, tijdsynchronisatie en opvolging |

> Meer technologie is niet automatisch een beter ontwerp.

---

<!-- _class: question -->

## Checkpoint — snelle audit

Een router verzorgt:

- alle default gateways;
- DHCP;
- NAT/PAT en internettoegang;
- alle ACL's.

**Welke van de vier enterprise-domeinen kunnen problematisch zijn?**

**Welk bijkomend bewijs heb je nodig vóór je een conclusie trekt?**

---

# Vijf niveaus voorkomen te snelle conclusies

| Niveau | Voorbeeld | Wat weet je? |
|---|---|---|
| Requirement | Guests mogen alleen naar internet | gewenst gedrag |
| Ontwerp | Guests zitten in een aparte zone en VLAN | bedoelde scheiding |
| Configuratie | ACL bevat deny-regels naar interne subnetten | regels bestaan |
| Operationele toestand | ACL is inbound actief; counters lopen op | verkeer passeert de controle |
| Testbewijs | Internet werkt; server en management niet | geteste requirement werkt nu |

**Configuratie is intentie; operationele toestand en testen tonen effect.**

---

<!-- _class: question -->

## Wat kan hier misgaan?

```text
show access-lists

Extended IP access list GUEST-IN
  10 deny ip 10.10.50.0 0.0.0.255 10.10.0.0 0.0.255.255
  20 permit ip 10.10.50.0 0.0.0.255 any
```

Een student concludeert: **“Guests zijn afgeschermd.”**

Welke controles ontbreken nog?

---

# VLAN, subnet en zone beantwoorden andere vragen

| Begrip | Betekenis | Kernvraag |
|---|---|---|
| **VLAN** | technisch gescheiden broadcast domain | welke laag-2-groep? |
| **Subnet** | IP-adresbereik | welke laag-3-adressen? |
| **Zone** | groepering volgens functie, risico en vertrouwen | welk beleid hoort hier? |

Een zone kan uit één of meerdere VLAN's bestaan.

> Een VLAN scheidt verkeer technisch. Een zone verklaart **waarom** die scheiding nodig is.

---

# Verkeer tussen zones passeert een bewust controlepunt

<div class="zones">
  <div class="zone-stack">
    <div class="zone"><strong>Guests</strong><br>laag vertrouwen</div>
    <div class="zone"><strong>Staff</strong><br>gekende gebruikers</div>
    <div class="zone"><strong>IT</strong><br>beheerders</div>
  </div>
  <div class="arrow-large">→</div>
  <div class="control"><strong>L3-gateway / firewall</strong><br><br>routing + filtering<br><br>policy uit de regelmatrix</div>
  <div class="arrow-large">→</div>
  <div class="zone-stack">
    <div class="zone"><strong>Internet</strong><br>extern</div>
    <div class="zone"><strong>Servers</strong><br>kritieke diensten</div>
    <div class="zone"><strong>Management</strong><br>infrastructuurcontrole</div>
  </div>
</div>

**Zonder filtering blijft een apart VLAN gewoon routed bereikbaar.**

---

# Vertrouwen is context, geen universele rangorde

| Zone | Behandel als… | Ontwerpimplicatie |
|---|---|---|
| Internet | niet vertrouwd | alleen expliciet gepubliceerde diensten |
| Guests | onbekende toestellen | geen functionele toegang tot interne zones |
| Users/Staff | beheerd maar beperkt | alleen vereiste bedrijfsdiensten |
| Servers | kritieke doelwitten | toegang beperken per dienst |
| Management | kritieke controlezone | alleen specifieke beheerders en protocollen |

**Belangrijk:** “hoog vertrouwen” betekent niet “mag overal naartoe”. Ook servers en beheertoestellen krijgen minimale toegang.

---

# Implementeerbaar beleid benoemt bron, doel, dienst en actie

| Bron | Doel | Dienst | Beslissing | Reden |
|---|---|---|:---:|---|
| Staff | interne webserver | HTTPS | allow | bedrijfsapplicatie |
| Guests | Internet | HTTPS/DNS | allow | bezoekersinternet |
| Guests | Servers | alle | deny | geen functionele noodzaak |
| Students | Management | SSH/HTTPS | deny | geen beheertaak |
| IT | Management | SSH/HTTPS | allow | infrastructuurbeheer |
| Internet | Database | alle | deny | niet rechtstreeks publiek |

**Eerst intentie, daarna ACL- of firewallconfiguratie.**

In productie noteer je ook de **eigenaar** van de requirement en het **bewijs** waarmee de regel gevalideerd wordt.

---

# Management is geen “gewoon extra VLAN”

Managementinterfaces geven controle over routers, switches en andere infrastructuur.

Daarom:

- alleen bereikbaar vanaf specifieke beheertoestellen of een beheerzone;
- uitsluitend via veilige beheerprotocollen;
- niet bereikbaar vanuit gewone client- of guest-VLAN's;
- acties en pogingen centraal loggen en monitoren;
- sterke authenticatie voorzien in een productieomgeving.

> Wie de managementzone bereikt, kan de werking van andere zones beïnvloeden.

---

# In-band en out-of-band management lossen andere problemen op

| Model | Beheerpad | Sterkte | Aandachtspunt |
|---|---|---|---|
| **In-band** | over dezelfde infrastructuur als gebruikersverkeer | eenvoudig en goedkoop | een storing in het datapad kan ook beheer blokkeren |
| **Out-of-band** | via een apart managementnetwerk | beheer blijft beschikbaar bij datapadproblemen | extra infrastructuur en beheer nodig |

De workshop gebruikt bewust **in-band management** via VLAN 99.

In productie onderzoek je aanvullend:

<span class="tag">AAA</span>
<span class="tag">MFA</span>
<span class="tag">jump host</span>
<span class="tag">centrale logging</span>
<span class="tag">bronbeperking</span>

---

<!-- _class: question -->

## Mini-case — Guests hebben internet nodig

Beslis per stroom: **allow, deny of eerst bijkomende informatie?**

- Guest → interne DNS-server
- Guest → printer
- Guest → switch management-IP
- Guest → publieke website in de DMZ
- Guest → externe website
- Guest → andere guest-client

Welke requirements ontbreken nog om verantwoord te beslissen?

**Guest → Guest** is een aparte keuze: client isolation kan onderlinge communicatie blokkeren.

---

<!-- _class: divider -->

# Documentatie en bewijs maken het netwerk controleerbaar

## Geen administratie achteraf, maar een deel van het ontwerp

---

# Een minimale documentatieset beantwoordt acht vragen

| Document | Beantwoordt vooral… |
|---|---|
| fysieke en logische topologie | wat is waarmee verbonden? |
| VLAN-tabel en IP-adresplan | welke groepen, subnetten en gateways bestaan? |
| zoneschema | welke trust- en securitygrenzen bestaan? |
| routingoverzicht | langs welk pad beweegt verkeer? |
| securityregelmatrix | welke stromen zijn functioneel nodig? |
| testplan | hoe bewijzen we gewenst en verboden gedrag? |
| risico- en verbeterlijst | wat is prioritair en waarom? |

**Een andere beheerder moet het netwerk kunnen begrijpen, testen en wijzigen.**

---

# Fysieke en logische topologie beantwoorden andere storingsvragen

<div class="columns">
<div class="card">

### Fysiek

- toestellen en locaties;
- poorten en bekabeling;
- uplinks en afhankelijkheden;
- mogelijke single points of failure.

**Vraag:** welke verbinding of component kan defect zijn?

</div>
<div class="card">

### Logisch

- VLAN's en subnetten;
- gateways en routing;
- zones en controlepunten;
- mogelijke verkeerspaden.

**Vraag:** waar wordt verkeer doorgestuurd of gefilterd?

</div>
</div>

Een bruikbare tekening toont minstens toestelnamen, uplinkpoorten, VLAN's, subnetten en gateways.

---

# VLAN-tabel en IP-plan leggen functie én adresrol vast

| VLAN | Naam | Zone | Subnet | Gateway | Adressering |
|---:|---|---|---|---|---|
| 10 | Students | Internal users | `10.10.10.0/24` | `.1` | DHCP `.50–.200` |
| 20 | Staff | Internal users | `10.10.20.0/24` | `.1` | DHCP `.50–.200` |
| 30 | Servers | Servers | `10.10.30.0/24` | `.1` | vast of gereserveerd |
| 40 | Guests | Guests | `10.10.40.0/24` | `.1` | DHCP `.50–.200` |
| 99 | Management | Management | `10.10.99.0/24` | `.1` | vaste adressen |

Controleer:

- naam en werkelijk poortgebruik komen overeen;
- subnetten overlappen niet;
- DHCP-ranges botsen niet met vaste adressen;
- er is aantoonbare groeiruimte.

---

# Het routingoverzicht toont waar verkeersbeslissingen vallen

| Onderdeel | Te documenteren vraag |
|---|---|
| Default gateway | waar verlaat elk VLAN zijn subnet? |
| Inter-VLAN routing | router, multilayer switch of firewall? |
| Default route | waar vertrekt verkeer naar de externe zone? |
| NAT/PAT | op welk toestel en via welke inside/outside-interfaces? |
| Filtering | op welk echt routed pad wordt zonebeleid afgedwongen? |
| Redundantie | bestaat één pad of een getest alternatief? |

> Als je niet weet waar de beslissing valt, zoek je ACL's en storingen op het verkeerde toestel.

---

# Documentatie leeft mee met elke wijziging

<div class="pipeline">
  <div class="node"><strong>Desired state</strong><br>wat hoort te werken?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Current state</strong><br>wat werkt nu echt?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Gap</strong><br>waar wijkt het af?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Actie</strong><br>wat verandert?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Validatie</strong><br>welk bewijs sluit af?</div>
</div>

Een configuratiewijziging zonder bijgewerkt testverslag en documentatie laat een nieuwe blinde vlek achter.

---

# Metadata bepaalt of documentatie nog te vertrouwen is

| Metadata | Waarom nodig? |
|---|---|
| titel en scope | welk netwerkdeel beschrijft dit? |
| datum of versie | hoe actueel is de informatie? |
| auteur of eigenaar | wie volgt vragen en wijzigingen op? |
| bron | ontwerp, configuratie-output, test of aanname? |
| laatste validatie | wanneer is dit met de werkelijkheid vergeleken? |
| openstaande afwijkingen | welke gekende gaps blijven bestaan? |

**“VLAN 40 = Guests” is pas betrouwbaar als duidelijk is waar dat gegeven vandaan komt en wanneer het gevalideerd werd.**

---

# Verzamel bewijs met een vraag, niet met een commandodump

<div class="columns">
<div>

### Minder sterk

“Ik voer alle `show`-commando's uit en kijk wat ik vind.”

</div>
<div>

### Methodisch

“Ik wil weten welke VLAN's bestaan en op welke poorten ze actief zijn.”

```text
show vlan brief
```

</div>
</div>

**Een commando is een meetinstrument voor één concrete onderzoeksvraag.**

---

# Elke observatie maakt de volgende vraag scherper

<div class="pipeline">
  <div class="node"><strong>Vraag</strong><br>kan Guest de server bereiken?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Verwachting</strong><br>nee, volgens het zonebeleid</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Observatie</strong><br>HTTPS opent wel</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Vergelijking</strong><br>gedrag wijkt af</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Volgende vraag</strong><br>ontbreekt filtering of ligt ze verkeerd?</div>
</div>

**Methodisch troubleshooten is hypotheses verfijnen, niet willekeurig wijzigen.**

---

# De audit volgt een vaste redeneerroute

<div class="steps">
  <div class="step"><strong>1 · Verken</strong>topologie en kritieke componenten</div>
  <div class="step"><strong>2 · Breng in kaart</strong>VLAN's, subnetten en gateways</div>
  <div class="step"><strong>3 · Zoek controlepunten</strong>routing, NAT en filtering</div>
  <div class="step"><strong>4 · Reconstrueer beleid</strong>zones en vereiste stromen</div>
  <div class="step"><strong>5 · Test gericht</strong>allow-, deny- en regressietests</div>
  <div class="step"><strong>6 · Benoem risico</strong>oorzaak, impact en bewijs</div>
  <div class="step"><strong>7 · Adviseer</strong>concreet en toetsbaar verbeteren</div>
  <div class="step"><strong>8 · Concludeer</strong>enterprise-ready of niet?</div>
</div>

---

# Reconstrueer het volledige pad vóór je een controle beoordeelt

```text
Guest-pc
   ↓ accesspoort in VLAN 40
access-switch
   ↓ trunk: is VLAN 40 toegestaan?
default gateway / subinterface
   ↓ routing + ACL: juiste interface en richting?
edge-router
   ↓ default route + NAT/PAT
externe testhost
```

Voor een intern doel buigt het pad na de gateway af naar de doelzone. Controleer dus:

- waar routing gebeurt;
- waar filtering hoort te gebeuren;
- of een alternatief pad dezelfde controle omzeilt;
- waar NAT/PAT alleen voor extern verkeer actief wordt.

---

# Elke onderzoeksvraag heeft een passend commando

| Onderzoeksvraag | Commando | Bewijst niet… |
|---|---|---|
| Welke VLAN's en accesspoorten bestaan? | `show vlan brief` | end-to-end trunkwerking |
| Welke trunks dragen welke VLAN's? | `show interfaces trunk` | correcte overzijde |
| Welke L3-interfaces zijn actief? | `show ip interface brief` | bruikbare end-to-end dienst |
| Welke routes kent het toestel? | `show ip route` | bestaand retourpad |
| Welke ACL-regels bestaan en matchen? | `show access-lists` | juiste plaats en richting |
| Waar is een feature toegepast? | gerichte `show running-config` | correct gedrag |
| Ontstaan NAT-vertalingen na verkeer? | `show ip nat translations` | correcte DNS en filtering |

---

# VLAN-database en trunkstatus bewijzen samen de laag-2-keten

<div class="columns">
<div>

```text
show vlan brief
```

Controleer:

- VLAN-ID en naam;
- accesspoorten per VLAN;
- onverwachte poorten in VLAN 1;
- VLAN's zonder duidelijk doel.

</div>
<div>

```text
show interfaces trunk
```

Controleer:

- welke poorten trunk zijn;
- toegestane en actieve VLAN's;
- native VLAN;
- ontbrekende of overbodige VLAN's.

</div>
</div>

**Een VLAN dat lokaal bestaat, hoeft nog niet end-to-end vervoerd te worden.**

---

# Interface-status en routingtabel lokaliseren laag-3-problemen

<div class="columns">
<div>

```text
show ip interface brief
```

Vindt snel:

- `down` versus `administratively down`;
- subinterfaces en gateways;
- IP-adressen op kritieke interfaces.

</div>
<div>

```text
show ip route
```

Vindt snel:

- connected subnetten;
- default route;
- ontbrekende netwerken;
- gekozen next hop of enkel pad.

</div>
</div>

**Een `up/up` interface bewijst nog geen retourpad of werkende applicatie.**

---

# ACL-inhoud krijgt pas betekenis door plaats en richting

```text
show access-lists
show running-config
```

Controleer de volledige context:

1. matcht de regel de juiste bron, het juiste doel en de juiste dienst?
2. staat een brede `permit` niet vóór een specifieke `deny`?
3. is de ACL toegepast op de interface waar het verkeer passeert?
4. klopt de richting: `in` of `out`?
5. veranderen matchcounters tijdens een gerichte test?

> Een correcte ACL die nergens actief is, heeft geen effect.

---

# NAT/PAT moet tijdens gegenereerd verkeer effect tonen

```text
show ip nat translations
show running-config
show ip route
```

Geen vertaling na een externe test? Onderzoek dan:

- matcht de NAT-selectie het bronsubnet?
- zijn inside en outside correct aangeduid?
- bestaat een default route naar buiten?
- wordt verkeer eerder door filtering geblokkeerd?
- test je werkelijk een externe host uit de labtopologie?

**Een NAT-regel in de configuratie is geen bewijs van een werkende internetketen.**

---

# Een testplan koppelt verwachting aan observeerbaar gedrag

| Bron | Doel | Dienst | Verwacht | Bewijs |
|---|---|---|:---:|---|
| Staff | interne webserver | HTTPS | allow | pagina opent |
| Guest | externe testhost | HTTPS | allow | dienst + NAT-vertaling |
| Guest | interne webserver | HTTPS | deny | verbinding faalt |
| Student | switch management | SSH | deny | sessie faalt |
| IT | switch management | SSH | allow | loginprompt bereikbaar |

Noteer altijd: **bron, doel, dienst, verwacht resultaat, werkelijk resultaat en conclusie**.

---

<!-- _class: question -->

## Troubleshootingcase — ACL aanwezig, grens werkt niet

**Symptoom:** Guest bereikt internet én de interne webserver.

**Bekend:** `GUEST-IN` bevat deny-regels naar interne subnetten.

Zet in een logische controlevolgorde:

- bronadres, gateway en VLAN van de guest-client;
- routed pad en controlepunt;
- interface en richting van `GUEST-IN`;
- regelvolgorde en matchcounters;
- positieve en negatieve diensttest.

> Eerst de baseline bewaren; pas daarna wijzigen.

---

# Van losse observatie naar professioneel advies

| Stap | NetNova — Guest VLAN 40 |
|---|---|
| Requirement | Guests alleen naar noodzakelijke externe diensten |
| Observatie | Internet, interne webserver en management-IP zijn bereikbaar |
| Oorzaak | `GUEST-IN` bestaat, maar is niet effectief toegepast |
| Risico | onbekende toestellen bereiken interne diensten en infrastructuur |
| Verbetering | dwing de goedgekeurde traffic matrix af op het routed pad |
| Acceptatie | internet werkt; interne web- en managementdiensten niet; Staff blijft werken |

**Sterk advies verbindt requirement → bewijs → risico → maatregel → acceptatietest.**

---

# NetNova’s bewijs lokaliseert de gap tussen ACL en gedrag

| Onderzoeksvraag | Actie | Observatie | Tussenconclusie |
|---|---|---|---|
| Zit de client echt in Guests? | adres, gateway, poort en VLAN controleren | client zit in VLAN 40 | bronzone klopt |
| Waar verlaat verkeer VLAN 40? | gateway en routed pad volgen | router is controlepunt | ACL moet hier effect hebben |
| Wat staat in `GUEST-IN`? | regelvolgorde bekijken | relevante deny-regels bestaan | inhoud lijkt bedoeld voor de requirement |
| Waar is de ACL actief? | interface en richting controleren | niet toegepast op guest-subinterface | configuratie dwingt niets af |
| Wat doet het netwerk? | allow- en deny-tests uitvoeren | alle doelen bereikbaar | gedrag wijkt af van requirement |

**Wanneer bronnen elkaar tegenspreken, is die afwijking zelf een onderzoeksresultaat.**

---

# Acceptatietests sluiten de wijziging controleerbaar af

| Test na verbetering | Verwacht | Rol |
|---|:---:|---|
| Guest krijgt lease en bereikt gateway | allow | lokale basisfunctie |
| Guest bereikt externe testdienst | allow | functionele requirement |
| Guest bereikt interne webserver | deny | trustgrens |
| Guest bereikt managementdienst | deny | kritieke zone beschermd |
| Staff bereikt interne webserver | allow | regressietest |

Een wijziging is pas geslaagd wanneer:

- het verboden verkeer geblokkeerd is;
- noodzakelijke bedrijfscommunicatie blijft werken;
- operationele output het effect bevestigt;
- documentatie en testverslag bijgewerkt zijn.

---

# Prioriteit volgt uit waarschijnlijkheid én impact

| Risico | Kans | Impact | Prioriteit |
|---|:---:|:---:|:---:|
| Guest bereikt management | hoog | hoog | 1 |
| Eén gateway voor alle VLAN's | middel | hoog | 2 |
| ACL zonder gedocumenteerd doel | hoog | middel | 3 |
| Onlogische VLAN-naam | middel | laag | 4 |

Een professioneel risico benoemt:

<span class="tag">bedrijfsmiddel</span>
<span class="tag">blootstelling</span>
<span class="tag">oorzaak</span>
<span class="tag">impact</span>
<span class="tag">bewijs</span>
<span class="tag">prioriteit</span>

---

# Een professioneel verbeterpunt is een klein wijzigingscontract

| Onderdeel | Te beantwoorden vraag |
|---|---|
| Scope | welke zone, dienst of component verandert? |
| Requirement | welk gewenst gedrag moet ontstaan? |
| Implementatie | welke ontwerp- en configuratiewijziging is nodig? |
| Acceptatie | welke allow-, deny- en regressietests moeten slagen? |
| Neveneffect | welk legitiem verkeer kan geraakt worden? |
| Rollback | hoe keer je veilig terug bij een fout? |
| Documentatie | welke tabellen, schema's en historiek wijzigen mee? |

Niet: **“maak het netwerk veiliger.”**

Wel: **“blokkeer Guest naar interne subnetten, behoud externe toegang en valideer beide paden.”**

---

# Readiness wordt per domein met bewijs onderbouwd

| Domein | Mogelijke vaststelling | Vereist bewijs | Prioriteit |
|---|---|---|:---:|
| Schaalbaarheid | adresplan heeft weinig groeiruimte | VLAN/IP-plan en groeiproef | … |
| Betrouwbaarheid | één gateway en uplink | afhankelijkheidsanalyse | … |
| Security | Guest bereikt interne zones | traffic matrix + diensttests | … |
| Beheerbaarheid | ACL-doel en plaats onbekend | documentatie + reproduceerbare output | … |

Een sterke conclusie is genuanceerd:

> Basisconnectiviteit werkt, maar het netwerk is nog niet enterprise-ready omdat aantoonbare gaps bestaan in security, beschikbaarheid en overdraagbaarheid.

---

# Veelgemaakte denkfouten verwarren aanwezigheid met werking

| Denkfout | Betere redenering |
|---|---|
| `ping` werkt, dus het netwerk is goed | vergelijk diensttests en deny-tests met requirements |
| een ACL bestaat, dus verkeer is beschermd | controleer inhoud, plaats, richting, counters en effect |
| meer VLAN's betekent automatisch meer security | filtering moet het zonebeleid afdwingen |
| elke mogelijke fout vraagt redundantie | prioriteer op bedrijfsimpact en foutdomein |
| volledige configuratie is voldoende bewijs | selecteer relevante, herhaalbare output per vraag |
| onmiddellijk wijzigen versnelt troubleshooting | bewaar eerst baseline en bewijs |

---

# Een sterk antwoord is specifiek, onderbouwd en begrensd

Bij een controlevraag of auditconclusie:

1. formuleer eerst de **requirement** of ontwerpintentie;
2. benoem de concrete **observatie**;
3. leg uit wat het bewijs **wel en niet** aantoont;
4. koppel de afwijking aan **impact en prioriteit**;
5. stel een **toetsbare verbetering** met acceptatietest voor;
6. noteer aannames en de grens van het Packet Tracer-bewijs.

> “Alles werkt” is geen conclusie; het is hoogstens één observatie zonder norm, risicoanalyse of bewijsgrens.

---

# Packet Tracer toont principes, geen volledig productieontwerp

| In het lab | In productie aanvullend nodig |
|---|---|
| één router combineert meerdere functies | capaciteit, functiescheiding en redundantie beoordelen |
| single points herkennen | gecontroleerde failover en herstel testen |
| ACL's tonen verkeerslogica | stateful filtering, centraal beleid en logging kunnen nodig zijn |
| handmatige `show`-commando's | continue monitoring, metrics en alerts |
| `.pkt` en analyseverslag | versiebeheer, eigenaarschap en changeproces |
| enkele handmatige tests | herhaalbare acceptatie-, regressie- en failovertests |

**Benoem altijd wat de simulatie bewijst — en wat niet.**

---

# Van theorie naar praktijk

In de workshop audit je het bestaande netwerk van **NetNova**.

Je zal:

- VLAN's, subnetten, gateways, trunks en controlepunten reconstrueren;
- zones en vereiste verkeersstromen vastleggen;
- `show`-commando's koppelen aan concrete onderzoeksvragen;
- toegelaten én verboden verkeersstromen testen;
- risico's prioriteren over de vier enterprise-domeinen;
- vijf concrete verbeteringen met acceptatietests formuleren.

> Doel: eerst begrijpen en bewijzen — nog niet meteen alles configureren.

---

<!-- _class: question -->

## Voorbereidende case

Het NetNova-netwerk heeft:

- duidelijke VLAN's en een logisch IP-plan;
- één router en één uplink voor alle diensten;
- volledige routing tussen alle VLAN's;
- een ACL met onbekende toepassing;
- werkende internettoegang.

**Welke drie controles voer je eerst uit?**

**Welke conclusie mag je nog niet trekken?**

---

# Wat moet je onthouden?

1. Een werkend netwerk is niet automatisch **enterprise-ready**.
2. Beoordeel steeds **schaalbaarheid, betrouwbaarheid, security en beheerbaarheid** in samenhang.
3. Vertrek van requirements en zones; vertaal die pas daarna naar VLAN's, routing en filtering.
4. Maak onderscheid tussen **configuratie, operationele toestand en testbewijs**.
5. Werk methodisch: **vraag → bewijs → risico → verbetering → acceptatietest**.
