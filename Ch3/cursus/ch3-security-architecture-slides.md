---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks - Hoofdstuk 3
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
    padding: 44px 64px 72px;
    font-size: 26px;
  }
  h1, h2 { color: var(--blue); }
  h1 { font-size: 1.72em; margin-bottom: 0.42em; }
  h2 { font-size: 1.16em; margin-bottom: 0.38em; }
  h3 { color: var(--cyan); margin: 0 0 0.35em; }
  p, li { line-height: 1.22; }
  strong { color: var(--blue); }
  footer {
    font-size: 0.55em;
    color: var(--muted);
    bottom: 20px;
  }
  section::after {
    font-size: 0.55em;
    color: var(--muted);
    bottom: 20px;
  }
  blockquote {
    border-left: 8px solid var(--cyan);
    background: var(--sky);
    padding: 0.45em 0.8em;
    color: var(--blue);
  }
  table { width: 100%; font-size: 0.56em; }
  th { background: var(--blue); color: white; }
  td, th { padding: 0.26em 0.42em; }
  code { background: #edf1f4; color: #8a1c1c; }
  pre {
    background: var(--ink);
    color: #f5f7f8;
    border-radius: 8px;
    padding: 0.56em 0.72em;
    font-size: 0.72em;
  }
  pre code {
    background: transparent;
    color: #ffe7a3;
  }
  section.title {
    background: linear-gradient(135deg, var(--blue) 0%, #245b7c 68%, var(--cyan) 100%);
    color: white;
  }
  section.title h1,
  section.title h2,
  section.title strong { color: white; }
  section.title code,
  section.divider code {
    background: rgba(255,255,255,.18);
    color: #ffe7a3;
  }
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
    gap: 30px;
  }
  .columns-40-60 {
    display: grid;
    grid-template-columns: 0.8fr 1.2fr;
    gap: 30px;
  }
  .four {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }
  .card {
    background: var(--paper);
    border-top: 5px solid var(--cyan);
    padding: 12px 16px;
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
    gap: 8px;
    margin-top: 0.75em;
  }
  .pipeline .node {
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    padding: 11px 9px;
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
    gap: 12px;
    margin-top: 0.45em;
  }
  .zone-stack { display: grid; gap: 8px; }
  .zone {
    padding: 8px 12px;
    text-align: center;
    background: var(--paper);
    border-left: 6px solid var(--cyan);
    font-size: 0.74em;
  }
  .control {
    padding: 18px 13px;
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
    gap: 10px;
  }
  .step {
    min-height: 88px;
    padding: 10px 12px;
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

## Hoofdstuk 3 - Security architecture

**Van werkende connectiviteit naar aantoonbaar begrensde communicatie**

---

# BluePeak werkt - maar is het veilig ontworpen?

BluePeak Services heeft herkenbare segmenten:

<span class="tag">Staff</span>
<span class="tag">Finance</span>
<span class="tag">IT</span>
<span class="tag">Servers</span>
<span class="tag">Guests</span>
<span class="tag">IoT</span>
<span class="tag">DMZ</span>
<span class="tag">Management</span>

De basisconnectiviteit werkt. Net daarom wordt de securityvraag scherper:

> Welke communicatie is nodig, welke is gevaarlijk, waar controleren we die en hoe bewijzen we dat?

---

<!-- _class: question -->

## Startvraag

# Alles kan alles bereiken.

# Succes of probleem?

Bespreek kort: **welke verkeersstromen zouden in een enterprise-netwerk verdacht zijn, zelfs als ze technisch werken?**

---

# Leerdoelen

Na deze les kan je:

1. uitleggen waarom security architecture een ontwerpkeuze is en geen losse configuratiestap;
2. bedrijfseisen vertalen naar concrete verkeersstromen;
3. defense in depth en least privilege toepassen op een netwerkontwerp;
4. VLAN's, subnetten, zones en trust boundaries onderscheiden;
5. DMZ, firewall placement, NAT en stateful filtering conceptueel vergelijken;
6. regels, tests, logging en risico's professioneel verantwoorden.

---

# De lat verschuift van bereikbaarheid naar controle

| Technisch werkend | Security architecture |
|---|---|
| VLAN's bestaan | zones hebben een verklaard beleid |
| routing werkt | alleen noodzakelijke stromen routeerbaar |
| ping slaagt | de juiste applicatietest slaagt |
| ACL-regels bestaan | regels staan op het echte verkeerspad |
| NAT publiceert een host | de publieke dienst staat in de juiste zone |
| verboden verkeer faalt | logs of counters bewijzen waarom |

> Een netwerk is niet veilig omdat alles werkt. Het is veilig wanneer alleen verantwoord verkeer werkt.

---

# Goed securitydesign verbindt behoefte met bewijs

<div class="pipeline">
  <div class="node"><strong>Bedrijfseis</strong><br>welke taak moet werken?</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Verkeersstroom</strong><br>bron, doel, dienst, initiator</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Boundary</strong><br>welke grens wordt gekruist?</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Regel</strong><br>waar en hoe afdwingen?</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Bewijs</strong><br>allow + deny + log</div>
</div>

Een technische regel zonder beleidsreden wordt later moeilijk beheerbaar.

---

# Slechte gewoonte: eerst alles routen

In een basislabo gebeurt security vaak achteraf:

```text
VLAN's + routing -> alles kan alles bereiken -> ACL's achteraf
```

Dat maakt **default allow** onbewust het uitgangspunt: nieuwe VLAN's of servers erven brede bereikbaarheid.

## Enterprise design choice

| Keuze | Winst | Risico |
|---|---|---|
| eerst toelaten | snel resultaat | brede toegang wordt normaal |
| achteraf blokkeren | weinig analyse vooraf | vergeten stromen blijven open |
| eerst requirements | elke allow heeft reden | meer voorbereiding |
| default deny | nieuwe systemen erven geen toegang | dependencies moeten bekend zijn |

> Default deny is geen blind blokkeren. Het vraagt eerst zicht op noodzakelijke stromen.

---

# Defense in depth

Defense in depth betekent dat meerdere lagen elk een eigen bijdrage leveren.

| Laag | Wat beperkt ze? |
|---|---|
| segmentatie | brede bereikbaarheid |
| firewalling | ongewenste interzoneverbindingen |
| hardening | misbruik van overbodige services |
| identity en MFA | credentialmisbruik |
| logging en monitoring | onzichtbare fouten of aanvallen |

Een firewall vervangt geen hardening, identity of monitoring.

Case: een besmette stafflaptop mag geen vrije route worden naar Management en Servers.

```text
zonder lagen: besmetting -> scans -> management -> servers
met lagen:    Staff-zone -> serverregels -> managementblock -> logs
```

---

# Least privilege

Least privilege: geef alleen toegang die nodig is voor de taak, zolang die toegang nodig is.

| Dimensie | Te breed | Least privilege |
|---|---|---|
| bron | alle interne clients | Finance-zone |
| bestemming | volledig servernetwerk | `SRV-FIN` |
| dienst | alle IP-protocollen | TCP/443 |
| richting | beide richtingen | client initieert |
| beheerpad | elk IT-toestel | jump host of beheerzone |

`permit ip any any` is zelden een eindontwerp:

```text
permit ip any any
```

Onbekende bron, bestemming, dienst en reden maken beheer bijna onmogelijk.

---

# Van asset naar verkeersstroom

Begin niet bij een poortnummer, maar bij een functie.

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

**"Staff heeft toegang tot Servers" is geen precieze requirement.**

---

# Applicatiekennis voorkomt te brede regels

Een browseractie kan meerdere stromen vereisen:

```text
client -> DNS resolver -> UDP/TCP 53
client -> webserver -> TCP 443
client -> identity provider -> TCP 443
client -> certificaatstatusdienst -> TCP 80/443
```

| Symptoom | Mogelijke ontbrekende stroom |
|---|---|
| hostname werkt niet, IP wel | DNS |
| login redirect faalt | identity provider |
| TLS-validatie faalt | tijd, certificaatketen of statuscontrole |
| app opent maar data ontbreekt | backend- of API-stroom |

Open niet meteen `any`; onderzoek de dependency.

---

<!-- _class: divider -->

# Zones en trust boundaries

## Securitybeleid wordt pas bruikbaar wanneer je grenzen kan aanwijzen

---

# Securityzones

Een securityzone is een logische groep systemen met vergelijkbaar vertrouwens- en verkeersbeleid.

| Zone | Typische systemen | Ontwerpbezorgdheid |
|---|---|---|
| Guests | bezoekers, BYOD | onbeheerd, geen interne noodzaak |
| IoT | camera's, printers, sensoren | zwak beheerbaar |
| Staff | werkstations | bedrijfsapps zonder brede laterale beweging |
| Finance | financeclients of diensten | gevoelige data en processen |
| DMZ | publieke diensten | blootgesteld maar begrensd |
| Management | beheerinterfaces | hoge impact bij compromis |

---

# VLAN, subnet en zone beantwoorden andere vragen

| Begrip | Betekenis | Kernvraag |
|---|---|---|
| VLAN | Layer 2-segmentatie | welk broadcastdomein? |
| subnet | Layer 3-adressering | welk IP-bereik? |
| zone | securitybeleid | welk vertrouwen en welke toegang? |

Vaak is het in een labo 1 zone = 1 VLAN = 1 subnet.

Maar: twee hosts in hetzelfde VLAN communiceren meestal rechtstreeks op Layer 2. De routerfirewall ziet dat verkeer niet.

---

# Vertrouwen is context, geen ranglijst

| Zone | Behandel als... | Ontwerpimplicatie |
|---|---|---|
| Internet | onbekend en onvertrouwd | alleen expliciet gepubliceerde diensten |
| Guests | onbeheerde toestellen | internet, geen interne zones |
| Staff | beheerd maar beperkt | alleen vereiste bedrijfsapps |
| Servers | kritieke doelwitten | toegang per applicatiedienst |
| Management | controlezone | strikt beperkt en gelogd |

**Hoog vertrouwen betekent niet: mag overal naartoe.**

Ook servers, IT-hosts en managementsystemen krijgen minimale toegang.

---

# Verkeer tussen zones passeert een controlepunt

<div class="zones">
  <div class="zone-stack">
    <div class="zone"><strong>Guests</strong><br>laag vertrouwen</div>
    <div class="zone"><strong>Staff</strong><br>gekende gebruikers</div>
    <div class="zone"><strong>DMZ</strong><br>publiek blootgesteld</div>
  </div>
  <div class="arrow-large">-&gt;</div>
  <div class="control"><strong>Trust boundary</strong><br><br>routing + filtering<br><br>policy uit de matrix</div>
  <div class="arrow-large">-&gt;</div>
  <div class="zone-stack">
    <div class="zone"><strong>Internet</strong><br>extern</div>
    <div class="zone"><strong>Servers</strong><br>applicaties</div>
    <div class="zone"><strong>Management</strong><br>infrastructuur</div>
  </div>
</div>

Zonder filtering blijft een apart VLAN gewoon routed bereikbaar.

---

# Hoe bepaal je een zone?

Gebruik niet alleen de afdeling.

| Criterium | Vraag |
|---|---|
| functie | client, server, beheer of publieke dienst? |
| beheer | beheerd toestel of onbeheerde BYOD? |
| blootstelling | intern of vanaf internet bereikbaar? |
| datagevoeligheid | gewone app of finance/persoonsdata? |
| technische kwaliteit | patchbaar en monitorbaar? |
| impact bij compromis | welke vervolgstappen worden mogelijk? |

Een zone moet je kunnen beschrijven met inhoud, toegelaten stromen, verboden stromen, controlepunt en bewijs.

---

<!-- _class: question -->

## Checkpoint

# Is dit een securityzone?

`VLAN 40` bevat `SRV-APP` en `SRV-FIN`.

Bespreek:

- hebben beide servers hetzelfde risico?
- passeert verkeer tussen beide hosts de routerfirewall?
- welke extra maatregel kan nodig zijn als `SRV-FIN` gevoeliger is?

---

<!-- _class: divider -->

# DMZ

## Publieke bereikbaarheid ontwerpen alsof compromis mogelijk is

---

# DMZ: twee verschillende grenzen

Een DMZ is een aparte securityzone voor systemen die bereikbaar moeten zijn vanuit een minder vertrouwde omgeving.

```text
Internet -- boundary 1 --> DMZ -- boundary 2 --> Internal
            publicatie     standaard geen vrije interne toegang
```

| Grens | Basisbeleid | Reden |
|---|---|---|
| Internet naar DMZ | alleen gepubliceerde diensten | extern gebruik zonder andere poorten |
| DMZ naar Internal | default deny, specifieke backendstromen | impact na compromis beperken |

Het woord `DMZ` op een VLAN maakt het nog geen veilige DMZ.

Technisch herken je een DMZ aan een aparte zone, apart subnet, eigen controlepunt, publicatieregel, outbound policy en logging.

---

# Publieke webdienst: minimale stromen

| Stroom | Verwacht beleid | Waarom? |
|---|---|---|
| Internet naar DMZ-webserver TCP/443 | allow | publieke website |
| Internet naar DMZ-webserver SSH | deny | beheer niet publiek open |
| Internet naar interne server | deny | Internal niet rechtstreeks publiceren |
| DMZ-webserver naar Management | deny | beheerzone beschermen |

Als een backend nodig is:

```text
DMZ reverse proxy -> specifieke interne applicatie -> TCP/443
```

Niet: `DMZ -> Internal -> any`.

---

# Reverse proxy: nuttig, maar geen vrijgeleide

| Verkeerde aanname | Correcte redenering |
|---|---|
| de proxy staat in DMZ, dus backend is veilig | firewall beperkt het proxypad |
| alleen TCP/443 staat open | webaanvallen lopen net via TCP/443 |
| TLS maakt alles veilig | TLS beschermt transport, niet applicatielogica |
| proxy mag alle interne webservers bereiken | alleen gepubliceerde backends zijn nodig |

Een reverse proxy kan publiceren, TLS afhandelen en loggen.

Hij vervangt geen least privilege tussen DMZ en Internal.

---

# DMZ-hosts hebben beheer- en onderhoudsstromen

`DMZ -> Internal: deny` is een veilig uitgangspunt, geen excuus om dependencies te negeren.

| Behoefte | Veilige ontwerpvraag |
|---|---|
| DNS | welke resolver mag gebruikt worden? |
| NTP | welke tijdsbron maakt logs betrouwbaar? |
| updates | via proxy of repository, en alleen outbound? |
| logging | mag de host naar een collector zonder Management-breedte? |
| beheer | via jump host en sterke authenticatie? |
| back-up | welk pad en welke data? |

Elke onderhoudsstroom krijgt dezelfde bron-doel-dienst-reden-testanalyse.

---

<!-- _class: question -->

## Wat kan hier misgaan?

```text
Internet -- port forwarding --> SRV-APP in VLAN 40
SRV-APP staat samen met interne applicatieservers
```

Welke risico's ontstaan?

- welke boundary wordt overgeslagen?
- welke laterale beweging wordt mogelijk?
- welke test toont dat de publicatie verkeerd staat?
- welke verbetering past bij het DMZ-concept?

---

<!-- _class: divider -->

# Firewall placement

## Een correcte regel werkt alleen op het echte verkeerspad

---

# Firewall placement: teken eerst het pad

Voor BluePeak: waar blokkeer je Guest naar `SRV-APP`?

```text
PC-GUEST -> access -> core
         -> R-FW VLAN 50 -> filterbeslissing
         -> R-FW VLAN 40 -> SRV-APP
```

ACL op VLAN 50 ziet dit pad. ACL op de internetinterface niet.

| Vraag | Wat ontdek je? |
|---|---|
| waar staat de default gateway van de bron? | waar verkeer het VLAN verlaat |
| zijn bron en doel in hetzelfde subnet? | of routerfiltering het ziet |
| bestaat een tweede pad? | omzeiling of asymmetrie |

> De regelinhoud is correct, maar de plaatsing is fout.

---

# Stateless ACL, router-ACL en firewall

| Aspect | Stateless ACL | Stateful firewall |
|---|---|---|
| besliseenheid | individueel pakket | pakket plus sessiecontext |
| return traffic | vaak expliciet meenemen | onderdeel van sessie |
| beleid | interface en richting | zone-, object- en servicegericht |
| logging | beperkter | sessie- en policycontext |
| beheer | veel losse regels | centrale policies mogelijk |

Stateful betekent niet automatisch veilig: een brede allow blijft een brede allow.

In BluePeak simuleert `R-FW` firewallgedrag met subinterfaces en router-ACL's. In productie blijft de beleidsredenering gelijk, ook als een echte enterprise-firewall meer context biedt.

---

# NAT is geen firewallbeleid

```text
203.0.113.1:443 -> 10.30.70.10:443
```

Deze destination NAT-regel publiceert een dienst.

Ze beantwoordt niet:

- welke externe bronnen mogen verbinden;
- welke dienst wordt toegelaten;
- of het doel in DMZ of Internal staat;
- wat de doelhost daarna mag bereiken;
- wat gelogd wordt.

**NAT vertaalt adressen. Firewallbeleid bepaalt toegestane communicatie.**

---

# Chokepoints en alternatieve paden

Een controlepunt is alleen betrouwbaar als relevant verkeer er niet omheen kan.

Let op:

- parallelle routers zonder identiek beleid;
- directe Layer 2-verbindingen tussen zones;
- VPN-tunnels die op een ander toestel eindigen;
- cloud- of draadloze paden buiten de centrale firewall;
- IPv6 terwijl alleen IPv4-regels bestaan;
- beheerinterfaces met een tweede adres;
- asymmetrische routing bij stateful firewalls.

Controleer: **is het controlepunt echt in-path?**

---

# North-south en east-west traffic

| Stroom | Type | Securityvraag |
|---|---|---|
| Staff naar internet | north-south | welke outbound diensten zijn nodig? |
| Internet naar DMZ-webserver | north-south | welke publieke dienst publiceren we? |
| Staff naar `SRV-APP` | east-west | alleen HTTPS of breder? |
| DMZ-proxy naar backend | east-west | hoe beperken we compromisimpact? |
| IT naar Management | east-west | via welk beheerpad? |

Een sterke perimeter voorkomt geen laterale beweging na phishing, VPN-misbruik of IoT-compromis.

---

<!-- _class: divider -->

# Regelmatrix en technische vertaling

## Eerst beleid bespreekbaar maken, daarna pas syntax schrijven

---

# Firewallregelmatrix

Een firewallregelmatrix beschrijft gewenst verkeer tussen zones voordat je vendorsyntax schrijft.

| Veld | Betekenis |
|---|---|
| bronzone of bronobject | wie start de communicatie? |
| doelzone of doelobject | welke dienst wordt aangesproken? |
| protocol en poort | welke technische dienst is nodig? |
| actie | allow of deny |
| reden | welk bedrijfsproces of risico? |
| eigenaar | wie bevestigt dat toegang nodig blijft? |
| testmethode | hoe toon je werking aan? |

---

# BluePeak: voorbeeldmatrix

| Bron | Doel | Dienst | Actie | Bewijstest |
|---|---|---|:---:|---|
| Staff | `SRV-APP` | HTTPS | allow | browser vanaf `PC-STAFF` |
| Staff | Management | any | deny | SSH/HTTPS faalt |
| IT | Management | SSH/HTTPS | allow | SSH vanaf `PC-IT` |
| Guests | Internet | nodig | allow | externe test |
| Guests | Internal | any | deny | test naar `SRV-APP` faalt |
| Internet | `SRV-WEB-DMZ` | HTTPS | allow | HTTPS vanaf ISP-zijde |
| DMZ | Internal | any standaard | deny | DMZ naar `SRV-APP` faalt |

De matrix is ontwerpdocument, nog geen platformconfiguratie.

---

# Default deny veilig invoeren

Bij default deny is communicatie geblokkeerd tenzij een expliciete allow bestaat.

Veilige invoering:

1. inventariseer en observeer bestaande stromen;
2. bevestig noodzakelijke dependencies met eigenaars;
3. maak expliciete allow-regels;
4. activeer relevante logging;
5. test gecontroleerd;
6. monitor denies en corrigeer alleen aantoonbaar noodzakelijke stromen.

Default deny zonder analyse kan productie verstoren.

---

# Regelvolgorde en impliciete deny

Veel ACL's en firewalls verwerken regels van boven naar beneden.

```text
! slecht
permit ip 10.30.50.0/24 any
deny   ip 10.30.50.0/24 10.30.0.0/16

! beter
deny   ip 10.30.50.0/24 10.30.0.0/16
permit ip 10.30.50.0/24 any
```

Bij klassieke Cisco ACL's bestaat een impliciete deny op het einde.

Gebruik counters om te zien welke regel werkelijk matcht.

---

# Lifecycle van firewallregels

Een correcte regel kan later overbodig of fout worden.

| Fase | Beheervraag |
|---|---|
| aanvraag | welke businessreden en eigenaar? |
| beoordeling | is de stroom klein genoeg? |
| implementatie | welk controlepunt en welke volgorde? |
| validatie | slagen allow-, deny- en regressietests? |
| monitoring | wordt de regel gebruikt en ontstaan afwijkingen? |
| review | bestaat de toegang nog? |
| verwijdering | kan de regel veilig weg en is rollback voorzien? |

Tijdelijk zonder einddatum is meestal permanent.

---

# Van beleid naar technische regel

Beleid:

> Guests mogen interne zones niet bereiken, maar behouden gastinternet.

Conceptuele vertaling:

```text
deny   Guest -> Internal
allow  Guest -> Internet -> noodzakelijke diensten
```

Lab-denkwijze:

```text
deny   ip guest-subnet internal-subnets
permit ip guest-subnet any
```

Daarna controleer je plaatsing, richting, gatewaybereik, DNS, NAT en logging.

---

# Voorbeeld: alleen IT naar Management

Beleid:

> Alleen bevoegde IT-beheerders gebruiken SSH of HTTPS naar netwerkbeheerinterfaces.

Minimale labvertaling:

```text
permit tcp it-subnet management-subnet eq 22
permit tcp it-subnet management-subnet eq 443
deny   ip any management-subnet
```

Productievragen:

<span class="tag">jump host</span>
<span class="tag">AAA</span>
<span class="tag">MFA</span>
<span class="tag">sessielogging</span>
<span class="tag">noodpad</span>

---

<!-- _class: question -->

## Wat kan hier misgaan?

```text
Extended IP access list GUEST-IN
  10 deny ip 10.30.50.0/24 10.30.0.0/16
  20 permit ip 10.30.50.0/24 any
```

Een student concludeert: **"Guests zijn afgeschermd."**

Welke controles ontbreken nog?

- interface en richting;
- counters tijdens test;
- gateway en DNS;
- internetregressie;
- IPv6 of alternatief pad.

---

<!-- _class: divider -->

# Testen, logging en risico

## Securitybewijs bestaat uit toegelaten en verboden gedrag

---

# Drie soorten securitytests

Security testen bewijst twee eigenschappen: noodzakelijke communicatie werkt en verboden communicatie werkt niet.

| Testsoort | Vraag | Voorbeeld |
|---|---|---|
| positieve test | werkt wat moet werken? | Staff opent `SRV-APP` via HTTPS |
| negatieve test | faalt wat niet mag werken? | Guest bereikt `SRV-APP` niet |
| begrenzingstest | is alleen de bedoelde dienst open? | HTTPS werkt, SSH faalt |
| regressietest | bleef bestaand gedrag werken? | Guest-internet blijft werken |

Alleen positieve tests bewijzen geen begrenzing.

---

# Schrijf de verwachting vooraf

| Veld | Voorbeeld |
|---|---|
| test-ID | `GUEST-02` |
| bron | `PC-GUEST`, `10.30.50.101` |
| doel | `SRV-APP`, `10.30.40.10` |
| dienst | HTTPS/TCP 443 |
| verwacht | geblokkeerd |
| beleidsreden | Guests mogen Internal niet bereiken |
| bewijsbron | clientresultaat plus ACL-hitcounter |

Als je de verwachting pas achteraf formuleert, kan elk resultaat "juist" lijken.

---

# Ping is geen applicatietest

`ping` test ICMP echo.

| Resultaat | Wat mag je besluiten? | Wat niet? |
|---|---|---|
| ping slaagt | ICMP werkt over het pad | HTTPS-policy is correct |
| ping faalt | geen echoantwoord | alle TCP-diensten zijn onbereikbaar |
| HTTPS slaagt | TCP/443 en apprespons werken | andere poorten zijn dicht |
| SSH faalt | geen SSH-sessie | zonder logs niet waar de blokkering zit |

Gebruik een test die past bij de regel.

---

# Clientresultaat plus controlepuntbewijs

Eenzelfde symptoom kan meerdere oorzaken hebben.

| Clientobservatie | Mogelijke oorzaak | Aanvullend bewijs |
|---|---|---|
| timeout | deny, routeprobleem, host down | route, ARP, log, counter |
| connection refused | host bereikbaar, poort dicht | serverstatus |
| hostname onbekend | DNS-probleem | IP-test en DNS-query |
| ping faalt, HTTPS werkt | ICMP geblokkeerd | kan correct beleid zijn |

Een verwachte mislukking is pas securitybewijs als de bedoelde regel de oorzaak is.

---

# Minimale testmatrix voor BluePeak

| Test | Verwacht | Zinvol bewijs |
|---|:---:|---|
| `PC-STAFF` naar `SRV-APP` HTTPS | allow | browser + allow-counter |
| `PC-STAFF` naar Management | deny | clienttest + deny-counter |
| `PC-GUEST` naar internet | allow | externe respons + NAT-observatie |
| `PC-GUEST` naar `SRV-APP` | deny | deny-counter op `GUEST-IN` |
| `PC-IT` naar Management SSH | allow | SSH en VTY/ACL-context |
| ISP naar `SRV-WEB-DMZ` HTTPS | allow | HTTPS + NAT-doel |
| `SRV-WEB-DMZ` naar Management | deny | deny-counter + clienttest |

---

# Troubleshootingvolgorde

Wanneer een resultaat afwijkt, wijzig niet meteen de ACL.

```text
verwacht -> observeer -> lokaliseer -> verklaar -> corrigeer -> hertest
```

Controleer systematisch:

1. bron-IP, masker, gateway en VLAN;
2. lokale link en juiste access/trunkpad;
3. routepad, routing en ARP;
4. luistert de dienst;
5. ACL-interface en richting;
6. eerste match, counters en logs;
7. een wijziging tegelijk en daarna regressietest.

---

# Logging, monitoring en logcontext

Logs registreren wat gebeurde; monitoring volgt actief op en maakt afwijkingen zichtbaar.

Een nuttige logregel heeft genoeg context:

| Context | Waarom nodig? |
|---|---|
| correcte tijd | events op een tijdlijn plaatsen |
| bron en bestemming | systemen identificeren |
| protocol en poort | dienst herkennen |
| interface of zone | trust boundary bepalen |
| policy-ID of regelnaam | technische beslissing verklaren |

Zonder correcte tijd wordt incidentonderzoek onbetrouwbaar.

---

# Risico professioneel formuleren

<div class="columns">
<div>

### Zwak

> De firewall is slecht.

</div>
<div>

### Sterker

> `PC-GUEST` kan `SRV-APP` bereiken. Daardoor kan een onbeheerd gasttoestel interne diensten scannen. Blokkeer Guest naar Internal aan de guest-boundary en valideer met een negatieve HTTPS-test en een ACL-hitcounter.

</div>
</div>

Een sterk risico benoemt vaststelling, oorzaak, dreiging, impact, maatregel en validatie.

---

# Prioriteit volgt uit kans en impact

| Risico bij BluePeak | Kans | Impact | Waarom prioritair? |
|---|:---:|:---:|---|
| Guest bereikt Internal | hoog | middel | onbeheerde toestellen |
| Staff bereikt Management | middel | hoog | infrastructuurcontrole |
| NAT wijst naar Internal | hoog | hoog | publiek direct intern |
| DMZ bereikt Management | middel | hoog | compromis raakt beheer |
| IoT bereikt `SRV-FIN` | middel | hoog | zwak toestel raakt gevoelige data |

Een prioriteit zonder reden is geen professionele risicoanalyse.

---

# Methodische ontwerpaanpak

<div class="steps">
  <div class="step"><strong>1. Assets</strong>functies, eigenaars en gevoeligheid</div>
  <div class="step"><strong>2. Stromen</strong>bron, doel, dienst en initiator</div>
  <div class="step"><strong>3. Zones</strong>trust boundaries bepalen</div>
  <div class="step"><strong>4. Matrix</strong>allow en deny expliciet maken</div>
  <div class="step"><strong>5. Punten</strong>controlepunten en richting kiezen</div>
  <div class="step"><strong>6. Implementatie</strong>gecontroleerd wijzigen</div>
  <div class="step"><strong>7. Validatie</strong>testen, logs en regressie</div>
  <div class="step"><strong>8. Lifecycle</strong>reviewen en verwijderen</div>
</div>

Security architecture is een beheerde cyclus, geen eenmalige tekening.

---

# BluePeak: topologie en zones

<span class="tag">VLAN 10 Staff</span>
<span class="tag">VLAN 20 Finance</span>
<span class="tag">VLAN 30 IT</span>
<span class="tag">VLAN 40 Servers</span>
<span class="tag">VLAN 50 Guests</span>
<span class="tag">VLAN 60 IoT</span>
<span class="tag">VLAN 70 DMZ</span>
<span class="tag">VLAN 99 Management</span>

```text
Internet / ISP
      |
   [ R-FW ]  subinterfaces + stateless ACL's
      |
  [ SW-CORE ] -- DMZ -- Management
      |
Staff - Finance - IT - Servers - Guests - IoT
```

Productie voegt hier meestal stateful filtering, centrale logging en redundantie aan toe.

---

# BluePeak: sterke eindconclusie

Een goede conclusie verbindt vaststelling, risico en prioriteit.

Voor BluePeak onderzoek je vooral:

- Guest naar Internal;
- Staff naar Management;
- publieke NAT naar DMZ, niet naar Internal;
- DMZ naar Servers en Management;
- IoT naar gevoelige servers;
- Finance naar de juiste applicatie;
- welke ACL matcht en waar ze staat.

Elke verbetering vereist een positieve test, negatieve test en controlepuntbewijs.

---

# Van theorie naar praktijk

In de workshop pas je dit toe op BluePeak:

- zones en trust boundaries herkennen;
- te brede of verkeerd geplaatste ACL-regels analyseren;
- NAT-publicatie controleren;
- regelvolgorde en impliciete deny verklaren;
- testmatrix uitvoeren;
- logs, counters en configuratie-output als bewijs gebruiken;
- risico's concreet formuleren en prioriteren.

Geef niet zomaar "de juiste ACL". Verantwoord eerst het beleid.

---

<!-- _class: question -->

## Voorbereidende case

`PC-GUEST` kan internet bereiken en ook `SRV-APP` via HTTPS openen.

Voorspel je aanpak:

- Is dit gewenst gedrag?
- Welke boundary hoort dit te controleren?
- Waar verwacht je de ACL?
- Welke negatieve test gebruik je?
- Welke counter of log bewijst dat security de blokkering veroorzaakt?
- Welke regressietest toont dat gastinternet blijft werken?

---

# Wat moet je onthouden?

1. Security architecture vertrekt van gewenste stromen, risico's en bewijs.
2. VLAN's en subnetten zijn bouwstenen; zones beschrijven securitybeleid.
3. Een DMZ werkt alleen als verkeer naar en vanuit de DMZ begrensd wordt.
4. Een firewallregel werkt alleen op het echte verkeerspad en in de juiste volgorde.
5. Test wat moet werken en wat niet mag werken, met controlepuntbewijs.
