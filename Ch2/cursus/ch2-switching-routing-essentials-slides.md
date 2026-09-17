---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks — Hoofdstuk 2
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
    padding: 50px 66px;
    font-size: 28px;
  }
  h1, h2 { color: var(--blue); }
  h1 { font-size: 1.78em; margin-bottom: 0.48em; }
  h2 { font-size: 1.2em; margin-bottom: 0.42em; }
  h3 { color: var(--cyan); margin: 0 0 0.32em; }
  p, li { line-height: 1.25; }
  strong { color: var(--blue); }
  blockquote {
    border-left: 8px solid var(--cyan);
    background: var(--sky);
    padding: 0.42em 0.78em;
    color: var(--blue);
  }
  table { width: 100%; font-size: 0.67em; }
  th { background: var(--blue); color: white; }
  td, th { padding: 0.37em 0.5em; }
  code { background: #edf1f4; color: #8a1c1c; }
  pre {
    background: var(--ink);
    color: #f5f7f8;
    border-radius: 8px;
    padding: 0.64em 0.84em;
  }
  pre code {
    background: transparent;
    color: #f5f7f8;
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
    gap: 34px;
  }
  .columns-40-60 {
    display: grid;
    grid-template-columns: 0.8fr 1.2fr;
    gap: 34px;
  }
  .four {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .three {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  .card {
    background: var(--paper);
    border-top: 5px solid var(--cyan);
    padding: 14px 18px;
  }
  .card p { margin: 0.18em 0; }
  .bad { color: var(--red); }
  .good { color: var(--green); }
  .warn { color: var(--amber); }
  .small { font-size: 0.72em; }
  .tiny { font-size: 0.6em; }
  .muted { color: var(--muted); }
  .big-claim {
    font-size: 1.45em;
    line-height: 1.17;
    color: var(--blue);
    font-weight: 700;
  }
  .pipeline {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 9px;
    margin-top: 0.8em;
  }
  .pipeline .node {
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    padding: 13px 9px;
    text-align: center;
    font-size: 0.61em;
  }
  .flow {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
    align-items: stretch;
    gap: 10px;
    margin-top: 0.8em;
  }
  .flow .node {
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    padding: 14px 10px;
    text-align: center;
    font-size: 0.68em;
  }
  .arrow {
    align-self: center;
    color: var(--cyan);
    font-size: 1.25em;
    font-weight: 700;
  }
  .tag {
    display: inline-block;
    background: var(--sky);
    color: var(--blue);
    padding: 0.16em 0.48em;
    margin: 0.1em;
    font-size: 0.71em;
    font-weight: 700;
  }
  .device {
    background: var(--paper);
    border: 2px solid #bcc8cf;
    border-top: 6px solid var(--cyan);
    padding: 13px 16px;
    text-align: center;
  }
  .device.primary { border-top-color: var(--green); }
  .device.backup { border-top-color: var(--amber); }
  .network-row {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    gap: 14px;
    align-items: center;
    margin-top: 0.65em;
  }
  .vertical {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    max-width: 760px;
    margin: 0.4em auto 0;
  }
  .vertical .node {
    background: var(--paper);
    border-left: 7px solid var(--cyan);
    padding: 8px 14px;
    font-size: 0.66em;
  }
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

# Enterprise Networks

## Hoofdstuk 2 — Switching- en routingessentials

**Redundantie ontwerpen, begrijpen en bewijzen**

---

# Northwind Components groeit

De campus krijgt twee kantoorvleugels, een magazijn, een servernetwerk en één internet-edge.

<span class="tag">redundante uplinks</span>
<span class="tag">distributionlaag</span>
<span class="tag">meerdere VLAN's</span>
<span class="tag">dynamische routing</span>
<span class="tag">gatewayfailover</span>

De verwachting:

> Eén kabel, switch of gateway mag niet meteen een volledige bedrijfsdienst uitschakelen.

---

<!-- _class: question -->

## Startvraag

# Het diagram toont twee paden.

# Is het netwerk nu redundant?

Welk bewijs heb je nodig voor **Layer 2**, de **default gateway**, **routing** en de **einddienst**?

---

# Leerdoelen

Na deze les kan je:

1. STP-beslissingen per VLAN verklaren en root bridges bewust ontwerpen;
2. EtherChannel met LACP configureren, controleren en een gedegradeerde bundel herkennen;
3. multi-area OSPF ontwerpen rond area 0 en inter-area problemen methodisch analyseren;
4. HSRP-adressen, rollen en failovergedrag verklaren en controleren;
5. STP-root, HSRP-active en routed paden als één enterprise-ontwerp beoordelen;
6. redundantie bewijzen met een baseline, gerichte foutinjectie en acceptatietest.

---

# Beschikbaarheid is een keten

<div class="pipeline">
  <div class="node"><strong>1 · Fysiek</strong><br>link en toestel</div>
  <div class="node"><strong>2 · VLAN</strong><br>access en trunk</div>
  <div class="node"><strong>3 · L2-pad</strong><br>STP / LACP</div>
  <div class="node"><strong>4 · Gateway</strong><br>SVI en HSRP</div>
  <div class="node"><strong>5 · Routing</strong><br>OSPF-neighbor</div>
  <div class="node"><strong>6 · Route</strong><br>prefix / default</div>
  <div class="node"><strong>7 · Dienst</strong><br>end-to-end</div>
</div>

Een onderdeel kan afzonderlijk `up` lijken terwijl de gebruikersdienst toch faalt.

> Zoek de **vroegste afwijkende schakel** — niet het opvallendste protocol.

---

# Vier mechanismen, vier verschillende problemen

| Mechanisme | Lost op | Bewijs | Lost niet op |
|---|---|---|---|
| **STP / Rapid PVST+** | Layer 2-loops | root en poortrollen per VLAN | extra bandbreedte |
| **EtherChannel / LACP** | meerdere links als één bundel | actieve members + trunk | twee onafhankelijke switches |
| **OSPF** | routes leren en herberekenen | neighbors, areas en routes | clientgateway |
| **HSRP** | overneembare default gateway | virtual IP + active/standby | defect pad achter gateway |

**Protocolgezondheid én eind-tot-eindgedrag moeten kloppen.**

---

<!-- _class: divider -->

# 1 · STP en root bridge design

## Redundante Layer 2-paden zonder loops

---

# Een tweede kabel verandert het probleem

<div class="columns">
<div class="card">

### Eén uplink

- eenvoudig;
- voorspelbaar;
- <span class="bad">single point of failure</span>.

</div>
<div class="card">

### Twee losse uplinks

- alternatief pad;
- gesloten Layer 2-kring mogelijk;
- vereist een loopvrije beslissing.

</div>
</div>

> Extra kabels toevoegen is geen ontwerp. Wie beslist welk pad actief is?

---

# Waarom een switching loop escaleert

```text
          SW-DIST-1
          /       \
         /         \
   SW-ACCESS ---- SW-DIST-2
```

Ethernetframes hebben geen Layer 3-TTL die de kring doorbreekt.

| Effect | Zichtbaar symptoom |
|---|---|
| broadcast storm | VLAN wordt traag of onbruikbaar |
| MAC flapping | dezelfde MAC verschijnt op wisselende poorten |
| flooding | onnodig verkeer op veel links |
| hoge belasting | DHCP, ARP en gewone diensten vallen uit |

---

# STP bewaart het fysieke back-uppad

```text
                 SW-DIST-1
                 root bridge
                      |
                 forwarding
                      |
                  SW-ACCESS
                      |
             alternate / discarding
                      |
                 SW-DIST-2
```

- de kabel blijft fysiek aanwezig;
- STP maakt één loopvrije logische topologie;
- bij uitval kan het alternate pad forwarding worden.

**Een geblokkeerde poort kan precies correct gedrag zijn.**

---

# De root bridge bepaalt de STP-logica

Alle niet-root switches berekenen hun beste pad naar één referentiepunt.

| Rol | Praktische betekenis |
|---|---|
| **root bridge** | logisch middelpunt van de spanning tree |
| **root port** | beste lokale poort richting root |
| **designated port** | forwardingzijde voor een segment |
| **alternate/discarding** | kandidaat-back-uppad dat de loop voorkomt |

> Beoordeel nooit een blocked poort zonder eerst de root bridge van dat VLAN te kennen.

---

# Enterprise design choice — root in de distributionlaag

STP kiest de laagste **bridge ID**: priority, VLAN-component en uiteindelijk MAC-adres. Zonder bewuste priority kan een access switch toevallig winnen.

<div class="network-row">
  <div class="device primary"><strong>SW-DIST-1</strong><br>primary root</div>
  <div class="arrow">↔</div>
  <div class="device backup"><strong>SW-DIST-2</strong><br>secondary root</div>
  <div class="arrow">←</div>
  <div class="device"><strong>Access switches</strong><br>geen rootrol</div>
</div>

- paden lopen logisch naar de plaats waar verkeer samenkomt;
- failover blijft voorspelbaar;
- een access-switchreboot verandert niet onnodig het STP-middelpunt.

**Primary én secondary worden bewust gekozen.**

---

# Rapid PVST+ vraagt een beoordeling per VLAN

| VLAN | Root bridge | Beoordeling |
|---:|---|---|
| 10 | `SW-DIST-1` | logisch voor kantoorverkeer |
| 20 | `SW-DIST-2` | logisch als dit bewust gespreid is |
| 99 | `SW-ACCESS-3` | verdacht voor management |

- Rapid PVST+ gebruikt een snelle spanning-tree-instance per VLAN;
- RSTP spreekt over rol `alternate` en toestand `discarding`;
- controleer protocol, rol én toestand — niet één woord uit de output.

Edgepoorten kunnen PortFast gebruiken; bescherm ze in productie met BPDU Guard.

---

# Kies primary en secondary expliciet

```text
! SW-DIST-1
spanning-tree vlan 10,20,50,99 root primary

! SW-DIST-2
spanning-tree vlan 10,20,50,99 root secondary
```

Of met expliciete prioriteiten:

```text
spanning-tree vlan 10 priority 4096
spanning-tree vlan 10 priority 8192
```

Een lagere priority krijgt voorrang. **Controleer het resultaat achteraf.**

---

<!-- _class: question -->

## Wat kan hier misgaan?

```text
VLAN 10
  Root bridge : SW-ACC3
  Alternate   : uplink op SW-DIST-2
  Ping        : succesvol
```

1. Waarom is de ping geen goedkeuring van het ontwerp?
2. Welke verkeerspaden kunnen onlogisch worden?
3. Wie wordt root als `SW-ACC3` uitvalt?
4. Welk bewijs verzamel je vóór een wijziging?

---

# STP onderzoeken én failover bewijzen

```text
show spanning-tree vlan 10
```

| Fase | Te verklaren bewijs |
|---|---|
| baseline | root ID, lokale bridge ID, roles en states |
| foutinjectie | schakel exact één actieve uplink uit |
| observatie | alternate pad wordt forwarding; dienst herstelt |
| herstel | primary pad en bedoelde topologie keren terug |

**Checkpoint:** kan je een blocked poort nu beoordelen als correct, onlogisch of onvoldoende bewezen?

---

<!-- _class: divider -->

# 2 · EtherChannel en LACP

## Redundantie binnen één logische link

---

# Redundantie is niet hetzelfde als bundeling

| Twee losse links | EtherChannel met twee members |
|---|---|
| STP ziet twee paden | STP ziet één Port-channel |
| één link kan blocked zijn | compatibele members kunnen actief zijn |
| levert een back-uppad | levert capaciteit én memberredundantie |
| elke link heeft eigen L2-betekenis | configuratie hoort bij het logische geheel |

> Beslis vooraf: wil je een STP-back-uplink of één actieve linkbundel?

---

# EtherChannel maakt één Port-channel

```text
Fysiek                           Logisch

SW-DIST G0/1 ---- G0/1 SW-ACC   SW-DIST Po1 ===== Po1 SW-ACC
        G0/2 ---- G0/2                 members:
                                           G0/1
                                           G0/2
```

- verkeer wordt over members verdeeld met een hash;
- één gesprek gebruikt doorgaans één gekozen member;
- de bundel kan blijven werken wanneer één member uitvalt.

**Meer members betekent niet dat één TCP-sessie hun snelheden optelt.**

---

# LACP onderhandelt de bundel

| Zijde A | Zijde B | Vormt? | Reden |
|---|---|:---:|---|
| `active` | `active` | ja | beide starten onderhandeling |
| `active` | `passive` | ja | één zijde start |
| `passive` | `passive` | **nee** | niemand start |

LACP helpt bewaken of:

- beide zijden willen bundelen;
- de juiste compatibele poorten samen horen;
- een member actief tot de groep mag toetreden.

---

# Configureer de bundel als logisch geheel

```text
interface range g0/1 - 2
 channel-group 1 mode active

interface port-channel 1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50,99
```

Aan de overzijde:

- dezelfde memberlinks, speed/duplex en L2- of L3-modus;
- dezelfde LACP-, trunk-, native-VLAN- en allowed-VLAN-intentie;
- dezelfde twee logische buren aan alle members.

**Beheer trunkbeleid bij voorkeur op de Port-channel.**

Een gewone Port-channel kan niet over twee onafhankelijke distributionswitches worden gespreid.

---

# Controleer bundel én trunk

| Onderzoeksvraag | Bewijs |
|---|---|
| Bestaat `Po1`? | `show etherchannel summary` |
| Zijn alle verwachte members actief? | groeps- en memberstatus in dezelfde output |
| Is het een trunk? | `show interfaces trunk` |
| Draagt de bundel de nodige VLAN's? | allowed en active VLAN's |
| Ziet STP één logisch pad? | `show spanning-tree vlan ...` |

Een kabel die `up` is, is nog niet noodzakelijk **gebundeld**.

---

# Een werkende bundel kan gedegradeerd zijn

| Toestand | Dienst | Risico |
|---|---:|---|
| twee members actief | werkt | bedoelde capaciteit en redundantie |
| één member actief | werkt nog | minder capaciteit, geen memberreserve |
| geen members actief | valt uit | volledige Port-channel down |

> “De ping werkt nog” kan een verborgen verlies van redundantie maskeren.

Monitoring moet ook waarschuwen wanneer de dienst nog werkt maar de bundel niet meer aan de ontwerpbaseline voldoet.

---

<!-- _class: question -->

## Troubleshootingcase — `Po1` bestaat

**Verwacht:** `G0/1` en `G0/2` zijn actieve members; VLAN 10, 20, 50 en 99 lopen over `Po1`.

**Werkelijk:** alleen `G0/1` is gebundeld en pings slagen.

- Welke configuratie-eigenschappen vergelijk je aan beide kanten?
- Welk risico blijft bestaan ondanks de geslaagde ping?
- Welke member-failovertest bewijst het herstel?

---

<!-- _class: divider -->

# 3 · Multi-area OSPF

## Routing schaalbaar en lokaliseerbaar maken

---

# Eén area volstaat — tot het netwerk groeit

<div class="columns">
<div class="card">

### Single-area

- eenvoudig;
- geschikt voor kleine omgevingen;
- alle routers delen meer topologiedetail.

</div>
<div class="card">

### Multi-area

- details blijven beter lokaal;
- wijzigingen hebben een kleiner bereik;
- area-indeling en backbone worden cruciaal.

</div>
</div>

> Voeg areas toe voor schaal en structuur, niet om een klein lab ingewikkelder te maken.

---

# Area 0 vormt de backbone

<div class="network-row">
  <div class="device"><strong>Gebouw A</strong><br>area 10</div>
  <div class="arrow">→</div>
  <div class="device primary"><strong>Core / distribution</strong><br>area 0</div>
  <div class="arrow">←</div>
  <div class="device"><strong>Gebouw B</strong><br>area 20</div>
</div>

- non-backbone areas verbinden logisch met area 0;
- inter-area verkeer loopt via de backbone;
- een keten `area 10 — area 20 — area 30` zonder area 0 is geen correct normaal ontwerp.

<span class="tag">ABR: area 0 ↔ andere area</span>
<span class="tag">ASBR: externe routes → OSPF</span>

**Areas zijn routingzones — geen VLAN's of subnetten.** Vraag bij elke nieuwe area: waar is de verbinding met area 0?

---

# Conceptuele area-indeling

```text
router ospf 1
 router-id 1.1.1.1
 network 10.10.0.0 0.0.255.255 area 10
 network 10.0.0.0 0.0.0.3 area 0
```

Deze router heeft:

- usernetwerken van gebouw A in area 10;
- een transitlink naar de core in area 0;
- dus de rol van **ABR**.

In een echt ontwerp maak je de `network`-matches zo precies mogelijk.

---

# Passive interfaces: wel adverteren, geen buren zoeken

| Interface | Subnet adverteren | Neighbor vormen |
|---|:---:|:---:|
| transitlink naar core | ja | ja |
| SVI voor clients | ja | **nee** |
| server-VLAN zonder router | ja | **nee** |

```text
router ospf 1
 passive-interface default
 no passive-interface GigabitEthernet0/1
```

`passive-interface` stopt de subnetadvertentie niet; het stopt hello's en neighborship op die interface.

---

# Lees routecodes als ontwerpbewijs

```text
O    10.10.8.0/24  [110/2] via 10.0.0.1
O IA 10.20.30.0/24 [110/3] via 10.0.0.2
O*E2 0.0.0.0/0     [110/1] via 10.0.0.5
```

| Code | Betekenis |
|---|---|
| `O` | intra-area route |
| `O IA` | route uit een andere area |
| `O*E2` | externe OSPF-route, hier een default |

Een `FULL` neighbor bewijst nog niet dat de **specifieke doelroute** aanwezig is.

---

# Area mismatch: IP werkt, OSPF niet

| Linkzijde | IP-status | OSPF-area |
|---|:---:|---:|
| `R-A` naar core | up/up | 0 |
| core naar `R-A` | up/up | 10 |

Gevolg: geen correcte adjacency en geen route-uitwisseling.

```text
show ip ospf neighbor
show ip ospf interface
show ip protocols
```

Vergelijk eerst beide zijden van **dezelfde link**: area, subnet, timers en relevante OSPF-instellingen.

---

# Summarization begint bij het adresplan

```text
10.10.8.0/24
10.10.9.0/24     }  10.10.8.0/22
10.10.10.0/24
10.10.11.0/24
```

Op een ABR kan een correcte samenvatting:

- minder routes buiten de area opleveren;
- interne wijzigingen beter afschermen;
- routingtabellen overzichtelijker maken.

Een te brede samenvatting kan verkeer naar niet-bestaande of verkeerde netwerken trekken. **Areas repareren geen rommelig IP-plan.**

---

# De default route moet ergens ontstaan

```text
area 10 ── area 0 ── R-EDGE ── ISP
area 20 ─────┘
```

```text
router ospf 1
 default-information originate
```

Controleer in deze volgorde:

1. heeft `R-EDGE` zelf een bruikbare `0.0.0.0/0`?
2. injecteert de edge die route in OSPF?
3. bereikt de default alle relevante areas?
4. werkt het echte externe datapad?

---

<!-- _class: question -->

## Mini-case — Gebouw B is onbereikbaar

Op `R-A`:

- neighbor met de backbone is `FULL`;
- area 0-routes zijn aanwezig;
- er zijn geen `O IA`-routes naar `10.20.0.0/16`.

Waar zoek je nu eerst?

<span class="tag">R-B ↔ core-neighbor</span>
<span class="tag">area op transitlink</span>
<span class="tag">area 20-advertenties</span>
<span class="tag">summarization/filtering</span>

Formuleer een hypothese zonder al een configuratie te wijzigen.

---

<!-- _class: question -->

## Checkpoint — neighbor ≠ route ≠ dienst

Kan je voor elk niveau ander bewijs aanwijzen?

1. **Adjacency:** zijn de bedoelde routers buren?
2. **Route:** staat de exacte inter-area- of defaultprefix in de table?
3. **Data plane:** bereikt verkeer vanaf de echte bron de echte bestemming?
4. **Failover:** blijft dit waar wanneer de primaire transitlink uitvalt?

---

<!-- _class: divider -->

# 4 · Gateway redundancy

## De first hop van clients beschikbaar houden

---

# Eén default gateway blijft één foutpunt

Een client kan na gatewayuitval nog steeds:

- een geldig IP-adres hebben;
- link op de accesspoort tonen;
- lokale hosts in hetzelfde VLAN bereiken.

Maar zonder default gateway faalt communicatie naar:

<span class="tag">andere VLAN's</span>
<span class="tag">servers</span>
<span class="tag">internet</span>
<span class="tag">management</span>

> Lokale connectiviteit bewijst niet dat de first hop beschikbaar is.

---

# HSRP biedt één virtuele gateway

<div class="three">
  <div class="device primary"><strong>MLS-DIST1</strong><br>echt: `10.20.10.2`<br>active</div>
  <div class="device"><strong>Virtuele gateway</strong><br>`10.20.10.1`<br>client gebruikt deze</div>
  <div class="device backup"><strong>MLS-DIST2</strong><br>echt: `10.20.10.3`<br>standby</div>
</div>

Bij failover:

- het standbytoestel neemt de virtuele IP- en MAC-identiteit over;
- de client behoudt hetzelfde gatewayadres;
- korte pakketuitval blijft mogelijk tijdens convergentie.

HSRP is Cisco-eigen; VRRP is het open alternatief. Beide beschermen alleen de **first hop** — niet trunks, STP, routing of de applicatie.

---

# Drie instellingen bepalen wie hoort over te nemen

| Instelling | Functie |
|---|---|
| **priority** | maakt de preferred active expliciet |
| **preemption** | laat de betere gateway na herstel opnieuw active worden |
| **tracking** | verlaagt voorkeur wanneer een kritieke afhankelijkheid faalt |

Zonder tracking kan dit gebeuren:

```text
client → MLS-DIST1 active → X core-uplink
         MLS-DIST2 standby → ✓ core-uplink
```

> Een active gateway is pas bruikbaar als ook haar verdere datapad gezond is.

---

# HSRP conceptueel configureren

<div class="columns">
<div>

```text
interface vlan 10
 ip address 10.20.10.2 255.255.255.0
 standby 10 ip 10.20.10.1
 standby 10 priority 110
 standby 10 preempt
```

`MLS-DIST1`

</div>
<div>

```text
interface vlan 10
 ip address 10.20.10.3 255.255.255.0
 standby 10 ip 10.20.10.1
 standby 10 priority 100
 standby 10 preempt
```

`MLS-DIST2`

</div>
</div>

Clients gebruiken uitsluitend de **virtual IP `10.20.10.1`** als default gateway.

---

# Gateway redundancy is een keuze per VLAN

| VLAN | STP-root | HSRP-active | Beoordeling |
|---:|---|---|---|
| 10 | `MLS-DIST1` | `MLS-DIST1` | uitgelijnd |
| 20 | `MLS-DIST1` | `MLS-DIST1` | uitgelijnd |
| 50 | `MLS-DIST2` | `MLS-DIST2` | uitgelijnd als trunks kloppen |
| 99 | `SW-ACC1` | geen groep | management blijft kwetsbaar |

VLAN's over beide distributiontoestellen verdelen kan load sharing geven.

**Doe dit alleen bewust en documenteer primary/secondary per VLAN.**

---

# STP-root en HSRP-active horen samen

Mismatch voor VLAN 10:

```text
client
  → STP-pad eindigt bij MLS-DIST1
  → frame kruist inter-distributionlink
  → HSRP-active MLS-DIST2 routeert
```

Dit kan technisch werken, maar:

- gebruikt een langer pad;
- belast de inter-distributionlink onnodig;
- vergroot de impact van een extra linkfout;
- blijft onzichtbaar in een gewone pingtest.

---

# HSRP-failover testen

```text
show standby brief
show ip interface brief
show ip route
```

| Fase | Verwachting |
|---|---|
| baseline | juiste active/standby, virtual IP en werkende dienst |
| active gateway uit | standby wordt active; clientgateway blijft gelijk |
| upstream pad uit | tracking of routing stuurt naar gezond pad |
| herstel | preemption gedraagt zich volgens ontwerp |

Gebruik een doorlopende ping als indicatie, maar verklaar rolwissel en routes met protocoloutput.

---

<!-- _class: question -->

## Wat kan hier misgaan?

**Observatie:** `MLS-DIST2` neemt HSRP correct over. De virtual IP antwoordt, maar de server in een andere area blijft onbereikbaar.

Welke laag onderzoek je daarna?

- draagt het bron-VLAN het nieuwe actieve pad?
- heeft `MLS-DIST2` een OSPF-neighbor met de core?
- staat de specifieke doelroute in zijn routingtable?
- bestaat een retourpad en werkt de einddienst?

**HSRP is hier niet noodzakelijk de fout.**

---

<!-- _class: divider -->

# 5 · Eén ontwerp, één testverhaal

## Van protocoltoestand naar gebruikersdienst

---

# Werk van vroeg naar laat in de keten

<div class="vertical">
  <div class="node"><strong>1 · Client:</strong> adres, prefix en virtuele gateway</div>
  <div class="node"><strong>2 · Layer 2:</strong> VLAN, trunks en STP/Port-channel voor precies dat VLAN</div>
  <div class="node"><strong>3 · First hop:</strong> SVI up, juiste HSRP-active</div>
  <div class="node"><strong>4 · Control plane:</strong> bedoelde OSPF-neighbor aanwezig</div>
  <div class="node"><strong>5 · Data plane:</strong> specifieke route en retourpad</div>
  <div class="node"><strong>6 · Dienst:</strong> test vanaf de echte bron naar het echte doel</div>
</div>

Wijzig pas wanneer bewijs het foutdomein voldoende klein maakt.

---

# Control plane en data plane bewijzen iets anders

| Mechanisme | Control-planebewijs | Data-planebewijs |
|---|---|---|
| STP | root, roles, states | verkeer herstelt via nieuw pad |
| LACP | members in Port-channel | verkeer blijft lopen na memberuitval |
| OSPF | neighbor `FULL`, route geleerd | pakket gebruikt de bedoelde route |
| HSRP | active/standby, virtual IP | clientdienst blijft werken na rolwissel |

**Alleen control plane:** het protocol lijkt gezond, maar de dienst kan falen.  
**Alleen data plane:** het primaire pad werkt, maar het back-uppad kan verborgen defect zijn.

---

# Methodisch troubleshooten: verwacht → observeer → verklaar

| Stap | Voorbeeld OSPF-back-uppad |
|---|---|
| verwachting | `MLS-DIST2` vormt in area 0 een neighbor met `R-CORE` |
| observatie | link is up; neighbor ontbreekt |
| lokalisatie | IP-link werkt, OSPF-adjacency faalt |
| verklaring | beide linkzijden gebruiken een andere area |
| impact | gatewayfailover heeft geen route naar de core |
| maatregel | corrigeer de area op de bewezen foutlocatie |
| acceptatie | `FULL` + routes + geslaagde failoverdienst |

“OSPF werkt niet” is geen professionele diagnose.

---

# Elke failovertest heeft vier fasen

<div class="four">
  <div class="card"><strong>1 · Baseline</strong><br>roles, states, routes en werkende dienst</div>
  <div class="card"><strong>2 · Injectie</strong><br>schakel exact één gekend onderdeel uit</div>
  <div class="card"><strong>3 · Observatie</strong><br>protocolreactie, herstelduur en gebruikersimpact</div>
  <div class="card"><strong>4 · Herstel</strong><br>beginstaat terugzetten en opnieuw controleren</div>
</div>

Een screenshot zonder bron, verwachting en testfase is zwak bewijs.

---

# Minimale failovermatrix

| Test | Actie | Verwacht bewijs |
|---|---|---|
| STP-uplink | actieve uplink uit | alternate wordt forwarding; VLAN-dienst herstelt |
| EtherChannel-member | één member uit | `Po1` blijft up; minder members zichtbaar |
| HSRP-gateway | active SVI/toestel uit | standby neemt virtual IP over |
| upstream gatewaypad | core-uplink active uit | tracking/routing kiest gezond pad |
| OSPF-transit | primair routed pad uit | alternatieve route draagt verkeer |
| default route | extern doel testen | edge én interne router hebben bruikbare default |

Test één fout tegelijk; anders kan je oorzaak en gevolg niet betrouwbaar koppelen.

---

# Van observatie naar professioneel advies

| Onderdeel | Voorbeeld management-VLAN |
|---|---|
| requirement | beheer blijft beschikbaar bij uitval van één distribution-switch |
| observatie | client gebruikt fysiek SVI-adres; HSRP-groep 99 ontbreekt |
| risico | één gateway blijft een single point of failure |
| bedrijfsimpact | IT verliest beheerpad en herstel duurt langer |
| maatregel | HSRP per VLAN; virtual IP; STP/HSRP uitlijnen |
| acceptatie | rolwissel + managementdienst + routecontrole |

Een maatregel is pas sterk als het bewijs van succes vooraf vastligt.

---

# Labkeuze is geen productiegarantie

| Packet Tracer toont | Productie vereist aanvullend |
|---|---|
| STP-root en convergentie | protections, variantbeleid en monitoring |
| LACP met twee members | hashing, minimumlinks en platformlimieten |
| eenvoudige OSPF-areas | authenticatie, filtering, timers en schaalanalyse |
| HSRP bij toesteluitval | tracking, standbycapaciteit en onderhoudsbeleid |
| enkele pings en outputs | SLO/SLA, telemetry, logging en tijdsynchronisatie |

Meer redundantiemechanismen betekenen ook meer configuratie, expertise en testen.

Controleer bovendien gedeelde foutdomeinen: twee kabels, gateways of routed paden kunnen nog steeds dezelfde kabelgoot, voeding of core-router delen.

---

# Van theorie naar praktijk

In de workshop onderzoek je de campus van **Northwind Components**.

Je zal:

- redundante links, trunks en actieve STP-paden reconstrueren;
- root bridge-keuzes en EtherChannel-members beoordelen;
- OSPF-neighbors, areas, inter-area routes en default route onderzoeken;
- HSRP-groepen en clientgateways per VLAN controleren;
- één fout tegelijk injecteren en failover met gericht bewijs documenteren;
- observaties vertalen naar risico, bedrijfsimpact en acceptatietest.

> Eerst de toestand begrijpen en bewijzen; pas daarna gericht verbeteren.

---

<!-- _class: question -->

## Voorbereidende case

Een access switch heeft twee uplinks. De gewone ping naar de server werkt.

Je ontdekt:

- één uplink is STP-alternate;
- `Po1` bestaat tussen de distributionswitches;
- beide HSRP-gateways antwoorden op hun echte IP;
- één OSPF-neighbor ontbreekt.

**Welke conclusies mag je al trekken — en welke nog niet?**

Ontwerp één gerichte failovertest die de grootste verborgen afhankelijkheid zichtbaar maakt.

---

# Wat moet je onthouden?

1. Redundantie is een **end-to-endeigenschap**, geen vinkje bij één protocol.
2. STP maakt Layer 2 loopvrij; EtherChannel bundelt compatibele links tot één logisch pad.
3. OSPF-areas schalen rond area 0; een neighbor bewijst nog geen specifieke route of dienst.
4. HSRP beschermt de virtuele first hop; priority, preemption en tracking sturen de overname.
5. Bewijs failover met **baseline → één fout → protocolobservatie → einddienst → herstel**.
