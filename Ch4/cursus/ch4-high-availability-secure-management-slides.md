---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks — Hoofdstuk 4
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
  .chain {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    align-items: stretch;
    margin-top: 0.8em;
  }
  .chain .node {
    background: var(--paper);
    border-left: 5px solid var(--cyan);
    padding: 13px 10px;
    text-align: center;
    font-size: 0.64em;
  }
  .timeline {
    display: grid;
    grid-template-columns: 1fr 1.4fr 1fr;
    gap: 12px;
    margin-top: 1em;
  }
  .timeline div {
    background: var(--paper);
    border-top: 5px solid var(--cyan);
    padding: 15px;
    text-align: center;
    font-size: 0.72em;
  }
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

# Enterprise Networks

## Hoofdstuk 4 — High availability en secure management

**Voorspelbaar blijven werken, beheren en herstellen wanneer er iets fout gaat**

---

# BluePeak onder druk

Op een drukke werkdag:

- valt de primaire uplink van een access switch uit;
- blijft de interne applicatie eerst bereikbaar;
- kan IT plots niet meer aanmelden op de core switch;
- blijkt de configuratieback-up drie maanden oud.

<span class="tag">technische uitval</span>
<span class="tag">degraded mode</span>
<span class="tag">beheerpad</span>
<span class="tag">herstelbaarheid</span>

> Beschikbaarheid en secure management blijken één probleemketen te vormen.

---

<!-- _class: question -->

## Startvraag

# Het verkeer werkt nog.

# Is het incident dan opgelost?

Bespreek kort: **welke bijkomende informatie heb je nodig om dat te beoordelen?**

---

# Leerdoelen

Na deze les kan je:

1. single points of failure en gemeenschappelijke foutdomeinen analyseren;
2. redundantie, failover en load balancing correct vergelijken;
3. een failovertest ontwerpen en onderbouwen met control- én data-planebewijs;
4. back-up, rollback, RTO en RPO koppelen aan bedrijfsimpact;
5. een secure-managementbeleid ontwerpen rond bron, protocol, identiteit en rechten;
6. managementtoegang, AAA, logging en changes gericht controleren en troubleshooten.

---

<!-- _class: divider -->

# High availability begint bij impact

## Niet: “hoeveel extra hardware hebben we?”

---

# High availability voorkomt geen fouten

**High availability:** een dienst blijft bruikbaar ondanks een verwachte storing, onderhoud of gedeeltelijke uitval.

| Zonder HA | Met HA |
|---|---|
| uplink valt uit → afdeling offline | alternatief pad neemt over |
| gateway faalt → geen inter-VLAN routing | standby gateway wordt actief |
| internetlijn valt uit → cloud onbereikbaar | tweede verbinding neemt over |
| foutieve change → lang improviseren | bekende rollbackpositie beschikbaar |

> HA beperkt de impact. **Resilience** voegt detectie, procedures en herstelvermogen toe.

---

# Beschikbaarheid volgt het bedrijfsproces

| Proces | Technische keten | Beschikbaarheidsvraag |
|---|---|---|
| interne applicatie | access → core → DNS → server | hoe lang mag de dienst wegvallen? |
| financebetalingen | client → policy → finance-app | wanneer is onderbreking onaanvaardbaar? |
| incidentherstel | beheerpad → account → toestel | kan IT nog beheren bij productiestoring? |
| publieke website | provider → edge → DMZ → web | welke uitval merkt de klant? |

**Een klein toestel kan kritisch zijn omdat een belangrijk proces ervan afhangt.**

---

# Degraded mode is beschikbaar, maar kwetsbaarder

<div class="columns">
<div class="card">

### Normaal

- twee uplinks beschikbaar;
- centrale AAA bereikbaar;
- logs gaan naar centrale opslag;
- redundantie is intact.

</div>
<div class="card">

### Degraded

- alle traffic via één uplink;
- tijdelijke fallbackprocedure;
- logging mogelijk beperkt;
- volgende fout heeft grotere impact.

</div>
</div>

**Onzichtbare degraded mode is gevaarlijk:** het netwerk lijkt gezond terwijl de reserve al opgebruikt is.

---

# Meet de gebruikersdienst, niet alleen het toestel

```text
beschikbaarheid = (meettijd - onbeschikbare tijd) / meettijd × 100%
```

| Eerst vastleggen | Waarom? |
|---|---|
| dienst en meetpunt | een interface kan up zijn terwijl de applicatie faalt |
| meetperiode | 99,9% per maand ≠ 99,9% per jaar |
| geplande uitsluitingen | onderhoud beïnvloedt het cijfer |
| maximale vertraging | extreem traag kan praktisch onbruikbaar zijn |

<span class="tag">MTBF: tijd tussen storingen</span>
<span class="tag">MTTR: tijd tot herstel</span>

---

# Single points of failure zijn niet alleen hardware

| Type | Voorbeeld | Mogelijke impact |
|---|---|---|
| fysiek | enige uplink of voeding | directe onderbreking |
| logisch | enige default route of VLAN-pad | meerdere diensten onbereikbaar |
| security | enige firewallpolicy zonder herstelkopie | toegang te open of volledig dicht |
| management | enige jump server of beheerpc | herstel wordt moeilijk |
| procedureel | één persoon kent de aanpak | MTTR stijgt sterk |
| documentatie | geen actueel schema | foutlokalisatie vertraagt |

**SPOF is een impactanalyse, geen telling van kabels.**

---

<!-- _class: question -->

## Wat kan hier misgaan?

BluePeak heeft:

- twee uplinks van `SW-ACC2`;
- twee edge-routers;
- twee AAA-servers;
- een lokale én cloudback-up.

**Welke gedeelde afhankelijkheden kunnen deze vier oplossingen tegelijk minder redundant maken dan ze lijken?**

---

# Een foutdomein bepaalt wat samen kan uitvallen

| Redundant op papier | Gemeenschappelijk foutdomein |
|---|---|
| twee uplinks | dezelfde kabelgoot |
| twee switches | dezelfde stroomkring of softwarebug |
| twee providers | dezelfde straatinvoer of carrier |
| twee AAA-servers | dezelfde VM-host, DNS of database |
| lokale en cloudback-up | hetzelfde beheerdersaccount |

> Redundantie telt pas wanneer één waarschijnlijke oorzaak niet alle alternatieven tegelijk uitschakelt.

---

# Redundantie, failover en load balancing verschillen

| Begrip | Centrale betekenis | Voorbeeld |
|---|---|---|
| **Redundantie** | extra component of pad bestaat | tweede uplink |
| **Failover** | alternatief neemt over na een fout | standby gateway wordt active |
| **Load balancing** | meerdere componenten dragen verkeer | verkeer verdeeld over twee lijnen |

Een netwerk kan redundant getekend zijn zonder bruikbare failover.

**De bewijs-vraag:** wat gebeurt er werkelijk wanneer de primaire component verdwijnt?

---

# Redundantie moet door de volledige stack kloppen

| Laag of functie | Mogelijk mechanisme | Nog te bewijzen |
|---|---|---|
| fysiek | dubbele kabel of voeding | onafhankelijk foutdomein |
| Layer 2 | STP, EtherChannel | juiste VLAN's over alternatief pad |
| Layer 3 | tweede route | bruikbaar heen- én retourpad |
| gateway | HSRP of VRRP | clients gebruiken het virtual IP |
| edge | tweede lijn/router | NAT en policy volgen mee |
| management | jump, console, OOB | IT kan bij storing nog beheren |
| configuratie | back-up en versie | restore werkt echt |

---

# Kies bewust een actief model

| Model | Normale toestand | Aandachtspunt |
|---|---|---|
| active-passive | één actief, één standby | detectie en overnametijd |
| active-active | meerdere dragen verkeer | verdeling en asymmetrisch verkeer |
| active-backup path | primair forwarding, backup geblokkeerd | convergentie na fout |

Een STP-poort in `alternate` is niet defect. Ze bewaart een loopvrij reservepad.

> Beschikbaarheid vraagt dat je het bedoelde normale én foutgedrag kent.

---

# Protocolfailover is nog geen dienstherstel

<div class="chain">
  <div class="node"><strong>Client</strong><br>adres en sessie</div>
  <div class="node"><strong>Access</strong><br>VLAN en uplink</div>
  <div class="node"><strong>Gateway</strong><br>virtual IP</div>
  <div class="node"><strong>Routing</strong><br>heen en terug</div>
  <div class="node"><strong>Policy</strong><br>ACL / firewall</div>
  <div class="node"><strong>Dienst</strong><br>DNS en applicatie</div>
</div>

`show standby` kan een nieuwe active gateway tonen terwijl de finance-app nog faalt.

**Test daarom het mechanisme én de volledige gebruikersflow.**

---

<!-- _class: question -->

## Checkpoint — enterprise design choice

Na uitval van `R-FW1` wordt `R-FW2` active. Clients kunnen de server nog pingen, maar de webapp opent niet.

Welke hypotheses onderzoek je eerst?

<span class="tag">route</span>
<span class="tag">return traffic</span>
<span class="tag">policy</span>
<span class="tag">DNS</span>
<span class="tag">sessiestatus</span>
<span class="tag">monitoring</span>

**Welke observatie zou HSRP bevestigen zonder de dienst te bewijzen?**

---

# Een failovertest is een gecontroleerd experiment

| Onderdeel | Vooraf beantwoorden |
|---|---|
| testobject | welke link, gateway of dienst schakel je uit? |
| verwachting | wat blijft werken en welk pad neemt over? |
| impact | welke onderbreking is aanvaardbaar? |
| observatie | welke flow, status en logs verzamel je? |
| stopcriterium | wanneer ga je niet verder? |
| herstel | hoe keer je gecontroleerd terug? |

> Verander tijdens de meting exact één vooraf gekozen foutconditie.

---

# Vier fasen leveren herhaalbaar bewijs

<div class="steps">
  <div class="step"><strong>1 · Baseline</strong>gebruikersflow en actieve component vastleggen</div>
  <div class="step"><strong>2 · Fout injecteren</strong>één gekozen component uitschakelen en tijd noteren</div>
  <div class="step"><strong>3 · Failover valideren</strong>impact, nieuw pad, status en logevent meten</div>
  <div class="step"><strong>4 · Failback</strong>herstellen, eindtoestand en tweede impact controleren</div>
</div>

**Zonder baseline weet je niet of de test werkelijk iets veranderde.**

---

# Eén testresultaat heeft meerdere bewijsniveaus

| Bewijs | Voorbeeld | Wat toont het? |
|---|---|---|
| positieve test | applicatie werkt opnieuw | gewenste dienst is bruikbaar |
| foutinjectie | primaire uplink is down | bedoelde fout is echt aanwezig |
| negatieve controle | down-link draagt geen verkeer | succes komt niet via het oude pad |
| control plane | alternate wordt forwarding | mechanisme nam over |
| data plane | gerichte client-serverflow werkt | alternatief draagt gebruikersverkeer |
| detectie | log of alarm verschijnt | degraded mode is zichtbaar |

---

# Kies het commando op basis van de bewijs-vraag

| Vraag | Mogelijk commando |
|---|---|
| Welke interfaces zijn operationeel? | `show ip interface brief` |
| Draagt het L2-alternatief de nodige VLAN's? | `show interfaces trunk` |
| Welke STP-poort nam over? | `show spanning-tree` |
| Vormt de bundel werkelijk één logisch pad? | `show etherchannel summary` |
| Welke gateway is active of standby? | `show standby` |
| Welke route gebruikt het toestel? | `show ip route` |

**Geen enkel `show`-commando bewijst op zichzelf de volledige dienst.**

---

# Failback kan een tweede onderbreking veroorzaken

```text
primair actief → fout → failover → degraded mode
                                 ↓
normale toestand ← failback ← primair hersteld
```

Controleer bij terugkeer:

- neemt het primaire toestel automatisch opnieuw over?
- veroorzaakt `preempt` een tweede verschuiving?
- convergeren STP en routing opnieuw zoals verwacht?
- blijven gebruikerssessies werken?
- eindigt monitoring in een gezonde, niet-degraded toestand?

---

<!-- _class: question -->

## Troubleshootingcase — de ping bewijst te weinig

Na het uitschakelen van uplink A blijven pings naar de server zonder verlies werken.

1. Hoe bewijs je dat verkeer vóór de fout via uplink A liep?
2. Hoe bewijs je dat uplink B daarna forwarding werd?
3. Welke echte diensttest voeg je toe?
4. Welke beperking blijft zelfs na een geslaagde test bestaan?

> Formuleer **verwachting → observatie → verklaring → beperking**.

---

<!-- _class: divider -->

# Beschikbaarheid vraagt voorbereid herstel

## Onderhoud, back-up, rollback en hersteldoelen

---

# Een onderhoudsvenster begrenst het risico

| Leg vooraf vast | Professionele vraag |
|---|---|
| doel en scope | wat verandert, op welke toestellen en waarom? |
| impact | wie merkt welke onderbreking? |
| baseline en back-up | wat is de bekende beginsituatie? |
| validatie | welke allow-, deny- en beheertests moeten slagen? |
| rollback | welke trigger, actie, eigenaar en maximale duur? |
| communicatie | wie krijgt voor, tijdens en na informatie? |

**Go/no-go:** start niet als de beginsituatie instabiel is of het noodpad ontbreekt.

---

# Een back-up is nog geen herstelplan

<div class="pipeline">
  <div class="node"><strong>Verzamelen</strong><br>kritieke toestellen</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Beschermen</strong><br>beperkte toegang</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Versies</strong><br>datum en change</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Herstellen</strong><br>passend platform</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Bewijzen</strong><br>restore-test</div>
</div>

> Een niet-geteste back-up is een aanname, geen herstelgarantie.

---

# Bewaar configuratie én context

<div class="columns">
<div>

### Technische toestand

- running- en startup-config;
- toestelmodel en softwareversie;
- datum, tijd en changereferentie;
- netwerkdiagram en afhankelijkheden.

</div>
<div>

### Bescherming

- kopie buiten het toestel;
- beperkte lees- en schrijfrechten;
- versiehistoriek of immutabele kopie;
- secrets buiten de config waar mogelijk.

</div>
</div>

**De actieve config, startup-config en goedgekeurde externe baseline moeten overeenkomen.**

---

# Een restore-test bewijst bruikbaarheid

<div class="steps">
  <div class="step"><strong>1 · Selecteer</strong>een representatieve back-up</div>
  <div class="step"><strong>2 · Herstel</strong>in lab, sandbox of passend reservetoestel</div>
  <div class="step"><strong>3 · Vergelijk</strong>met de goedgekeurde baseline</div>
  <div class="step"><strong>4 · Valideer</strong>VLAN's, routing, policy, beheer en logs</div>
</div>

Controleer ook of meerdere beheerders het bestand en de procedure tijdig kunnen vinden.

---

# Rollback en roll forward zijn andere keuzes

| Strategie | Keuze | Geschikt wanneer… |
|---|---|---|
| **Rollback** | terug naar bekende werkende toestand | impact hoog of oorzaak onduidelijk is |
| **Roll forward** | gecontroleerd corrigeren naar nieuwe toestand | fout klein, lokaal en eenduidig is |

Een rollbackplan bepaalt vooraf:

- de rollbacktrigger en beslisser;
- de exacte vorige toestand en uitvoeringswijze;
- het beschikbare noodpad;
- de maximale duur en de nacontroles.

---

# Wijzigingen aan het beheerpad verdienen extra controle

<div class="columns">
<div class="card">

### Risicovolle changes

- management-ACL;
- trunk of route voor VLAN 99;
- AAA-server of fallback;
- jump-serverpolicy;
- default route van de beheerzone.

</div>
<div class="card">

### Noodpad vooraf

- fysieke console;
- getest OOB-pad;
- alternatieve beheertoegang;
- iemand ter plaatse;
- gekende vorige configuratie.

</div>
</div>

> Een beheerwijziging zonder noodpad kan de herstelmogelijkheid zelf uitschakelen.

---

# RTO en RPO meten ander verlies

<div class="timeline">
  <div><strong>Laatste herstelpunt</strong><br>goedgekeurde config</div>
  <div><strong>Incident</strong><br><span class="warn">RPO kijkt terug</span><br><span class="good">RTO kijkt vooruit</span></div>
  <div><strong>Dienst hersteld</strong><br>geteste toestand</div>
</div>

| Begrip | Vraag |
|---|---|
| **RTO** — Recovery Time Objective | hoe lang mag herstel duren? |
| **RPO** — Recovery Point Objective | hoeveel changes of data mag je verliezen? |

**De bedrijfsimpact bepaalt het doel; techniek en procedures moeten het haalbaar maken.**

---

# Herstel in volgorde van afhankelijkheid

1. managementtoegang en noodpad;
2. core- en distributionconnectiviteit;
3. routing en gatewayfuncties;
4. servernetwerk en kritieke applicaties;
5. internetedge en DMZ;
6. minder kritieke client- en guestdiensten;
7. monitoring en logging volledig valideren.

> Welke dienst moet eerst terugkomen omdat andere herstelacties ervan afhangen?

---

<!-- _class: question -->

## Enterprise design choice — ambitie zonder middelen

BluePeak kiest voor de core een **RTO van 30 minuten**.

- geen reservetoestel;
- laatste back-up is drie maanden oud;
- geen console server of OOB-pad;
- levering van hardware: volgende werkdag.

**Formuleer dit als een professionele auditbevinding met impact, bewijs en advies.**

---

<!-- _class: divider -->

# Secure management beschermt de controlelaag

## Wie mag wat beheren, vanwaar en met welk bewijs?

---

# Bescherm de volledige beheerketen

<div class="chain">
  <div class="node"><strong>Beheerder</strong><br>persoonlijke identiteit</div>
  <div class="node"><strong>Login</strong><br>sterke authenticatie</div>
  <div class="node"><strong>Bron</strong><br>beheertoestel of jump</div>
  <div class="node"><strong>Pad</strong><br>beperkte managementzone</div>
  <div class="node"><strong>Protocol</strong><br>SSH / HTTPS</div>
  <div class="node"><strong>Doel</strong><br>rechten + accounting</div>
</div>

Een sterke login helpt weinig wanneer elke staff-pc de managementinterface kan aanvallen.

> Secure management is een keten, geen checkbox.

---

# Een managementpolicy beantwoordt minstens vier vragen

| Dimensie | Vraag | BluePeak-voorbeeld |
|---|---|---|
| bron | vanwaar start beheer? | alleen IT of jump server |
| doel | welke toestellen? | switches, router en firewall |
| protocol | hoe gebeurt beheer? | SSH/HTTPS, geen Telnet/HTTP |
| identiteit | wie mag wat? | helpdesk leest, admin wijzigt |

Voeg voor een volledig ontwerp toe:

<span class="tag">tijd</span>
<span class="tag">noodtoestand</span>
<span class="tag">logging en bewijs</span>

---

# Drie planes verklaren verschillende symptomen

| Plane | Functie | Voorbeeldsymptoom |
|---|---|---|
| data plane | gebruikersverkeer doorsturen | client bereikt server niet |
| control plane | paden en rollen bepalen | OSPF-neighbor of STP-root verandert |
| management plane | beheren en observeren | SSH naar switch faalt |

Een switch kan frames correct blijven doorsturen terwijl SSH niet werkt.

**Voor de gebruiker is de dienst up; voor herstel is de situatie toch riskant.**

---

# Een management VLAN is nog geen managementzone

| Management VLAN | Managementzone |
|---|---|
| Layer 2-segment en subnet | security- en trustconcept |
| groepeert managementinterfaces | bepaalt bron, protocol en identiteit |
| maakt gericht beleid mogelijk | dwingt least privilege af |
| kan routed bereikbaar blijven | bevat filtering, logging en noodgedrag |

> Technische scheiding zonder toegangsbeleid verandert de bereikbaarheid niet genoeg.

---

# Ontwerp expliciete managementflows

| Bron | Doel | Dienst | Actie |
|---|---|---|:---:|
| jump server | netwerktoestellen | SSH | allow |
| IT-zone | jump server | vereiste login | allow |
| IT-laptop | managementinterface | SSH | deny als jump verplicht is |
| Staff | managementinterfaces | alle | deny |
| Guests / IoT / DMZ | managementsubnet | alle | deny |
| toestel | centrale logging / AAA | vereiste flow | allow |

Test het bedoelde protocol: een mislukte ping bewijst niet dat TCP/22 geblokkeerd is.

---

# Defense in depth verdeelt de controle

| Afdwingingspunt | Beperkt vooral… | Bewijst niet… |
|---|---|---|
| routed ACL of firewall | bronzones naar managementsubnet | welke commando's admin mag uitvoeren |
| VTY access-class | bronadressen naar CLI | webbeheer of SNMP |
| services op toestel | welke protocollen luisteren | vanwaar ze bereikbaar zijn |
| jump-hostpolicy | flows vanaf beheerpunt | individuele rechten op doeltoestel |
| AAA-autorisatie | taken van geldige identiteit | netwerkblootstelling |

**Geen enkele laag vervangt de andere volledig.**

---

# In-band en out-of-band lossen andere risico's op

| Model | Pad | Sterkte | Beperking |
|---|---|---|---|
| in-band | over productie-infrastructuur | eenvoudiger en goedkoper | kan samen met datapad falen |
| out-of-band | apart beheerpad | beheer bij zware storing | extra kost en eigen risico's |

OOB is vooral waardevol voor core, edge, remote sites en toestellen die het normale beheerpad dragen.

**Ook OOB vereist sterke toegang, onafhankelijke stroom, logging en periodieke tests.**

---

# SSH is nodig, maar niet genoeg

| Zwakke keuze | Betere keuze | Extra controle |
|---|---|---|
| Telnet | SSH | bronbeperking, host key, individuele identiteit |
| HTTP | HTTPS | vertrouwd certificaat en beperkte bron |
| TFTP / FTP | SCP, SFTP of HTTPS | bescherm back-ups en credentials |
| SNMPv1/v2c | SNMPv3 waar ondersteund | authenticatie, privacy en policy |

> Een veilig protocol beschermt de verbinding; het managementontwerp beschermt ook bron, doel, rechten en audittrail.

---

# AAA verdeelt drie verschillende beslissingen

<div class="four">
  <div class="card"><strong>Authentication</strong><br>Wie ben je?<br><span class="small">persoonlijke identiteit en login</span></div>
  <div class="card"><strong>Authorization</strong><br>Wat mag je?<br><span class="small">rol, privilege of commando</span></div>
  <div class="card"><strong>Accounting</strong><br>Wat deed je?<br><span class="small">sessie en beheeracties</span></div>
  <div class="card"><strong>Enterprise-winst</strong><br>Consistent beheer<br><span class="small">centraal, schaalbaar, auditeerbaar</span></div>
</div>

**Een geldige login zonder autorisatie kan nog altijd te veel macht geven.**

---

<!-- _class: question -->

## Wat kan hier misgaan? — AAA fallback

Een vertrokken medewerker probeert aan te melden.

1. De centrale AAA-server is bereikbaar.
2. De server antwoordt expliciet **deny**.
3. Het toestel probeert daarna automatisch een lokaal account.

**Waarom is dit geen beschikbaarheidsoplossing maar een policy-omzeiling?**

Wanneer mag beperkte lokale fallback wél starten?

---

# RADIUS en TACACS+ ondersteunen ander gebruik

| Eigenschap | RADIUS | TACACS+ |
|---|---|---|
| typische context | Wi-Fi, VPN, 802.1X | beheer van netwerktoestellen |
| transport | UDP, vaak 1812/1813 | TCP 49 |
| autorisatie | vaak netwerktoegang en attributen | fijnmaziger beheer- en commandoautorisatie |
| aandacht | bescherm transport, server en shared secret | protocol is geen vervanging voor segmentatie |

**Ontwerpvraag:** zijn serverredundantie, timeouts, beperkte fallback en accounting mee voorzien?

---

# Role-based access vertaalt least privilege naar taken

| Rol | Mag wel | Mag niet |
|---|---|---|
| helpdesk | status en poortconditie bekijken | routing of policy wijzigen |
| operator | interfaces en standaardtaken beheren | firewallregels goedkeuren |
| network admin | netwerkconfiguratie wijzigen | buiten changeprocedure werken |
| security admin | policy beoordelen en goedkeuren | ongecontroleerd operationeel wijzigen |
| auditor | logs en configuraties bekijken | changes uitvoeren |

<span class="tag">persoon → beheeridentiteit → rol → taak → gelogde actie</span>

---

# Een jump server verkleint het beheeroppervlak

```text
IT-admin  ──>  jump server  ──>  managementzone
Staff     ──X
Internet  ──X
```

Voordelen:

- één gecontroleerd startpunt voor beheer;
- eenvoudiger bronbeperking en centrale logging;
- extra authenticatie en sessiebeleid mogelijk;
- directe toegang vanaf gewone clients kan dicht.

**Nieuwe afhankelijkheid:** compromis of uitval van de jump server raakt veel beheerflows.

---

# Bewijs het jump-serverbeleid end-to-end

| Test | Verwacht | Bewijs |
|---|:---:|---|
| IT-admin → jump server | allow | login- of MFA-event |
| Staff → jump server | deny | netwerk- of authenticatielog |
| jump → management-SSH | allow | sessie plus toestellog |
| IT-laptop → management-SSH | deny | mislukte flow en policylog |
| beheeractie via jump | herleidbaar | jump-, AAA- en toesteltijd correleren |

Als het doeltoestel alleen “jump-server” logt, ontbreekt de menselijke identiteit in de auditketen.

---

# Logs reconstrueren de beheerketen

```text
change-id
   ↓
jump-login → AAA-beslissing → toestelsessie → configwijziging → service-impact
```

Een bruikbare audittrail bevat:

- individuele identiteit, bron en doel;
- toegekende rol en relevante actie;
- correcte, gesynchroniseerde tijd;
- centrale opslag buiten het beheerde toestel;
- koppeling met change of incident.

> Logging zonder context, betrouwbare tijd en opvolging levert vooral ruis.

---

# Een professionele change heeft een vaste lifecycle

<div class="pipeline">
  <div class="node"><strong>Aanvragen</strong><br>reden en eigenaar</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Beoordelen</strong><br>impact en risico</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Voorbereiden</strong><br>baseline en rollback</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Uitvoeren</strong><br>begrensde scope</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Valideren</strong><br>tests en nieuwe baseline</div>
</div>

Voor en na vergelijk je dezelfde gebruikersflow, deny-flow, managementtoegang, control plane en logging.

---

# Configuratiedrift ondermijnt de goedgekeurde baseline

| Oorzaak | Voorbeeld | Gevolg |
|---|---|---|
| noodchange blijft staan | tijdelijke allow-regel | policy wordt ongemerkt ruimer |
| lokale handmatige change | poort wijkt af van documentatie | herstel wordt onzeker |
| gedeeltelijke uitrol | één switch mist management-ACL | inconsistent beveiligingsniveau |
| oude restore | recente VLAN's of routes verdwijnen | technisch herstel creëert functionele fout |

> De laatste running-config is niet automatisch de gewenste baseline; de gewenste baseline is getest en goedgekeurd.

---

<!-- _class: question -->

## Integratiecase — één change, twee risicoassen

BluePeak wil remote de ACL naar VLAN 99 aanscherpen.

**Ontwerp vóór uitvoering:**

- één noodzakelijke allow-test en twee deny-tests;
- de relevante baseline-output;
- een rollbacktrigger;
- een noodpad;
- logging waarmee je de actie en het effect koppelt;
- het beschikbaarheidsrisico als centrale AAA tegelijk uitvalt.

---

# Van theorie naar praktijk

In de workshop audit je de bewust onvolmaakte BluePeak-topologie.

Je zal:

- kritieke afhankelijkheden en single points of failure aantonen;
- één foutscenario voorbereiden met baseline, foutinjectie en bewijs;
- management allow- en deny-flows controleren;
- back-up, rollback en herstelvolgorde beoordelen;
- bevindingen koppelen aan bedrijfsimpact en prioriteit;
- labbewijs begrenzen tegenover een productieontwerp.

> Doel: niet alleen zien wat ontbreekt, maar aantonen waarom het risico relevant is.

---

<!-- _class: question -->

## Voorbereidende case

Je ziet bij BluePeak:

- `SW-ACC2` heeft één bruikbare uplink;
- Staff bereikt de management-IP van `SW-CORE` via SSH;
- een configuratiebestand bestaat, maar zonder datum of restore-test;
- de core heeft een RTO van 30 minuten.

**Welke drie observaties verzamel je eerst?**

**Welke conclusie mag je nog niet trekken zonder foutinjectie of diensttest?**

---

# Wat moet je onthouden?

1. Beschikbaarheid vertrekt van **bedrijfsimpact en volledige dienstketens**, niet van het aantal toestellen.
2. Redundantie is pas bewezen met **baseline, foutinjectie, control-plane-, data-plane- en detectiebewijs**.
3. Back-up, rollback, RTO en RPO maken herstel **voorbereid en toetsbaar**.
4. Secure management beschermt **bron, pad, protocol, identiteit, rechten en audittrail** als één keten.
5. Een professionele beheerchange eindigt met **allow-, deny-, regressie- en herstelbewijs plus een nieuwe baseline**.
