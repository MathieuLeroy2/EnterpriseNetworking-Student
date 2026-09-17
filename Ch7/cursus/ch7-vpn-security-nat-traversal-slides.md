---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks — Hoofdstuk 7
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
    padding: 44px 62px 76px;
    font-size: 25px;
  }
  h1, h2 { color: var(--blue); }
  h1 { font-size: 1.62em; margin-bottom: 0.42em; }
  h2 { font-size: 1.08em; margin-bottom: 0.38em; }
  h3 { color: var(--cyan); margin: 0 0 0.3em; }
  p, li { line-height: 1.2; }
  ul, ol { margin-top: 0.35em; margin-bottom: 0.35em; }
  strong { color: var(--blue); }
  blockquote {
    border-left: 7px solid var(--cyan);
    background: var(--sky);
    padding: 0.38em 0.72em;
    color: var(--blue);
  }
  table {
    width: 100%;
    font-size: 0.58em;
    border-collapse: collapse;
  }
  th { background: var(--blue); color: white; }
  td, th {
    padding: 0.32em 0.46em;
    border: 1px solid #bcc8cf;
    vertical-align: top;
  }
  code { background: #edf1f4; color: #8a1c1c; }
  pre {
    background: #f5f7f8;
    color: var(--ink);
    border-left: 7px solid var(--blue);
    border-radius: 6px;
    padding: 0.55em 0.72em;
    font-size: 0.62em;
    line-height: 1.18;
    white-space: pre-wrap;
    overflow: hidden;
  }
  pre code { background: transparent; color: inherit; }
  footer {
    left: 62px;
    right: 62px;
    bottom: 20px;
    font-size: 0.52em;
    color: var(--muted);
  }
  section::after {
    right: 62px;
    bottom: 20px;
    font-size: 0.55em;
    color: var(--muted);
  }
  section.title {
    background: var(--blue);
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
  section.question h2 { color: var(--blue); }
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    align-items: start;
  }
  .columns-40-60 {
    display: grid;
    grid-template-columns: 0.8fr 1.2fr;
    gap: 30px;
    align-items: start;
  }
  .four {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
  }
  .card {
    background: white;
    border: 1px solid #bcc8cf;
    border-left: 6px solid var(--cyan);
    padding: 12px 16px;
    overflow: hidden;
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
    gap: 7px;
    margin-top: 0.75em;
  }
  .pipeline .node {
    background: var(--paper);
    border: 1px solid #bcc8cf;
    border-bottom: 5px solid var(--cyan);
    padding: 10px 9px;
    text-align: center;
    font-size: 0.58em;
    overflow-wrap: anywhere;
  }
  .pipeline .arrow {
    align-self: center;
    color: var(--cyan);
    font-size: 1em;
    font-weight: 700;
  }
  .steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 11px;
  }
  .step {
    min-height: 90px;
    padding: 10px 12px;
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    font-size: 0.62em;
    overflow: hidden;
  }
  .step strong { display: block; font-size: 1.15em; margin-bottom: 0.25em; }
  .tag {
    display: inline-block;
    background: white;
    color: var(--blue);
    border: 1px solid #bcc8cf;
    padding: 0.12em 0.42em;
    margin: 0.1em 0.12em;
    font-size: 0.64em;
    font-weight: 700;
  }
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

# Enterprise Networks

## Hoofdstuk 7 — VPN security, NAT traversal en zichtbaarheid

**Waarom een VPN veilig kan werken over een netwerk dat je niet vertrouwt**

---

# BluePeak werkt van overal

Een beheerder wil een Debian-server bereiken:

- vanuit Devbit;
- daarna vanuit eduroam of campusroam;
- zonder publieke applicatiepoort;
- zonder port forwarding;
- zonder wijzigingen aan campusinfrastructuur.

> De vraag is niet alleen: **werkt de verbinding?**  
> De vraag is: **waarom werkt ze, langs welk pad, en wat blijft zichtbaar?**

---

<!-- _class: question -->

## Startvraag

# Je zit op onbekende wifi.

# Waarom zou een VPN daar veilig kunnen zijn?

Bespreek eerst apart:

- wat een aanvaller kan lezen;
- wat hij kan wijzigen;
- wat hij kan blokkeren;
- welke metadata hij nog ziet.

---

# Leerdoelen

Na deze les kan je:

1. verklaren waarom een VPN veilig kan werken over een onbekend netwerk;
2. encryptie, integriteit, authenticatie en autorisatie onderscheiden;
3. NAT, PAT en stateful firewalls koppelen aan VPN-connectiviteit;
4. NAT traversal, endpoint discovery, hole punching en DERP conceptueel uitleggen;
5. analyseren welke inhoud en metadata zichtbaar blijven voor verschillende beheerders;
6. meetresultaten zoals `netcheck`, `tailscale ping`, captures en throughput verantwoord interpreteren.

---

# De redeneerlijn van dit hoofdstuk

<div class="pipeline">
  <div class="node"><strong>Bescherming</strong><br>wat levert de tunnel?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Bereikbaarheid</strong><br>hoe vinden peers elkaar?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Padkeuze</strong><br>direct, peer relay of DERP?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Zichtbaarheid</strong><br>wie ziet welke data?</div>
  <div class="arrow">→</div>
  <div class="node"><strong>Bewijs</strong><br>welke meting toont dat?</div>
</div>

Een webpagina die opent, bewijst connectiviteit. Nog niet het pad, de policy of de privacyverwachting.

---

# Het onderliggende netwerk is niet vertrouwd

Op hotelwifi, campusroam, mobiel internet of thuisnetwerk weet je niet:

- wie het netwerk beheert;
- wie mee op hetzelfde segment zit;
- of DNS gemanipuleerd wordt;
- of UDP of bepaalde poorten geblokkeerd worden;
- welke logging of filtering onderweg gebeurt.

**VPN-ontwerp vertrekt dus niet van vertrouwen in het netwerk, maar van wantrouwen.**

---

# Wat betekent "beveiligd" bij een VPN?

| Eigenschap | Vraag | VPN-voorbeeld |
|---|---|---|
| Vertrouwelijkheid | kan iemand inhoud lezen? | HTTP-request zit versleuteld in de tunnel |
| Integriteit | kan iemand verkeer wijzigen? | aangepast pakket wordt verworpen |
| Authenticatie | spreek ik met de juiste peer? | peer bewijst bezit van private key |
| Autorisatie | mag deze peer naar deze service? | ACL/grant laat alleen nodige poorten toe |
| Replaybescherming | kan oud verkeer opnieuw geldig zijn? | oude pakketten worden geweigerd |
| Forward secrecy | blijft oud verkeer beschermd? | sessiesleutels worden vernieuwd |

---

# Encryptie is niet hetzelfde als autorisatie

```json
{
  "action": "accept",
  "src": ["*"],
  "dst": ["*:*"]
}
```

Deze regel maakt de tunnel niet minder versleuteld.

Maar ze maakt het toegangsmodel wel gevaarlijk breed:

- elke bron mag naar elke bestemming;
- elke service wordt bereikbaar;
- least privilege ontbreekt;
- negatieve tests zullen weinig aantonen.

> Encryptie beschermt de transportweg. Policy bepaalt of het verkeer daar mag zijn.

---

# Een VPN is geen magisch veilig netwerk

Een VPN lost vooral dit probleem op:

> Hoe communiceren endpoints veilig over een netwerk dat we niet vertrouwen?

Een VPN lost niet automatisch:

- besmette endpoints;
- gecompromitteerde accounts;
- te brede ACL's;
- kwetsbare applicaties;
- foutieve DNS;
- ontbrekende interne segmentatie;
- afwezige of overdreven logging.

**VPN-security blijft een laag in een groter enterprise-ontwerp.**

---

# Man-in-the-middle: wat verandert er?

<div class="columns">
<div class="card">

### Zonder bescherming

```text
Laptop -- aanvaller -- server
```

- inhoud lezen;
- inhoud aanpassen;
- sessies verstoren;
- DNS of verkeer omleiden.

</div>
<div class="card">

### Met correcte VPN

```text
Laptop == tunnel == server
```

- inhoud normaal niet leesbaar;
- wijziging wordt gedetecteerd;
- peeridentiteit wordt gecontroleerd;
- blokkeren blijft mogelijk.

</div>
</div>

---

# Eén pakketstroom, meerdere controles

```text
browser
  -> origineel IP/TCP/HTTP-pakket
  -> VPN-client versleutelt en authenticeert
  -> onbetrouwbaar netwerk vervoert buitenste pakketten
  -> VPN-peer controleert en ontsleutelt
  -> policy beslist of bestemming en poort mogen
  -> applicatie verwerkt de request
```

**Sterke conclusie vraagt meer dan één test:**

<span class="tag">peer klopt</span>
<span class="tag">inhoud beschermd</span>
<span class="tag">service toegelaten</span>
<span class="tag">ongewenste service geweigerd</span>

---

# WireGuard als moderne VPN-basis

Tailscale gebruikt WireGuard voor de data plane.

| Kenmerk | Betekenis |
|---|---|
| moderne cryptografie | encryptie, authenticatie en integriteit horen samen |
| UDP-gebaseerd | tunnelprotocol beheert zelf handshakes en roaming |
| public/private keys | peers worden cryptografisch herkenbaar |
| kleine protocolscope | WireGuard doet tunnelbescherming, geen volledig identityplatform |
| cryptokey routing | peeridentiteit en toegelaten tunneladressen hangen samen |

---

# Handshake en sessiesleutels

Conceptueel:

```text
1. Peer A kent public key van peer B.
2. Peer B kent public key van peer A.
3. Peers voeren een handshake uit.
4. Beide kanten leiden sessiesleutels af.
5. Dataverkeer wordt versleuteld en geauthenticeerd.
6. Sessiesleutels worden regelmatig vernieuwd.
```

**Belangrijk:** de private key wordt niet doorgestuurd. De peer bewijst dat hij ze bezit.

---

# WireGuard lost niet alles alleen op

| Vraag | WireGuard | Beheerlaag |
|---|---|---|
| Is de tunnel cryptografisch beschermd? | ja | protocolkeuze en updates bewaken |
| Welke gebruiker hoort bij dit device? | beperkt | identity en devicebeheer |
| Welke service mag bereikt worden? | niet volledig | ACL's, grants, tags |
| Welke DNS en routes gelden? | beperkt | control plane en policy |
| Wanneer wordt een device verwijderd? | niet automatisch | lifecycle en audit |

> WireGuard beschermt de tunnel. Het enterprise-ontwerp bepaalt wie de tunnel waarvoor mag gebruiken.

---

<!-- _class: divider -->

# Pad, policy en planes

## De verbinding kan online zijn terwijl de applicatie nog faalt

---

# Data plane en control plane

<div class="columns">
<div class="card">

### Data plane

Waar echte gebruikerspakketten lopen:

- HTTP;
- SSH;
- DNS;
- RDP;
- file transfer.

Bij Tailscale: WireGuard-verkeer tussen endpoints of via relay.

</div>
<div class="card">

### Control plane

Helpt bepalen:

- welke devices bestaan;
- welke keys en endpoints bekend zijn;
- welke ACL's gelden;
- welke DNS en routes gepubliceerd worden;
- welke DERP-regio's beschikbaar zijn.

</div>
</div>

---

# Control plane is niet automatisch datapad

```text
control plane:
  helpt peers elkaar vinden en policy kennen

data plane direct:
  Laptop A == encrypted UDP == Laptop B

data plane via DERP:
  Laptop A == encrypted == DERP == encrypted == Laptop B
```

De centrale vraag:

> Wie helpt de verbinding opzetten, en wie kan de inhoud lezen?

Bij een goed ontwerp zijn dat niet zomaar dezelfde partijen.

---

# Storingen worden duidelijker per plane

| Storing | Mogelijk effect | Wat kan nog werken? |
|---|---|---|
| control plane onbereikbaar | geen nieuwe login, key- of policyupdate | bestaande peers met cache kunnen soms blijven praten |
| direct datapad valt weg | verlies, vertraging of padwissel | DERP of peer relay kan overnemen |
| DERP onbereikbaar | fallback via die regio faalt | direct pad of andere relay kan werken |
| policy weigert verkeer | peer lijkt online, service faalt | andere toegelaten diensten kunnen werken |

**Typische fout:** "de peer staat online, dus de applicatie moet werken."

---

# Waarom moderne VPN's vaak UDP gebruiken

UDP is nuttig als buitenste tunneltransport:

- het VPN-protocol beheert zelf handshakes;
- geen tweede TCP-retransmissionlaag rond elk pakket;
- minder transportoverhead;
- gerichte keepalives kunnen NAT-state actief houden;
- roaming tussen netwerken is eenvoudiger.

**Nuance:** TCP-gebaseerde VPN's kunnen werken, maar TCP-over-TCP kan bij verlies extra vertraging geven.

---

# UDP en firewalls

| Verkeer | Typische rol | Betekenis |
|---|---|---|
| outbound UDP vanaf Tailscale-client | directe WireGuard-paden | externe peerpoorten zijn dynamisch |
| outbound UDP naar `3478` | STUN en endpointobservatie | helpt publiek endpoint ontdekken |
| outbound TCP naar `443` | control plane en DERP | coördinatie en fallback blijven mogelijk |

Poort `41641/udp` is vaak de lokale Tailscale-luisterpoort, maar is configureerbaar.

> Schrijf firewallregels op basis van actuele configuratie en productdocumentatie, niet op basis van geheugen.

---

# NAT mapping: tijdelijke vertaling

Een laptop achter NAT:

```text
192.168.1.50:41641 -> 203.0.113.20:45123
```

De NAT-router onthoudt:

| Binnen | Buiten |
|---|---|
| `192.168.1.50:41641` | `203.0.113.20:45123` |

Eigenschappen:

- ontstaat meestal door uitgaand verkeer;
- heeft een timeout;
- is protocol- en poortgebonden;
- kan per bestemming verschillen;
- laat alleen passend retourverkeer toe.

---

# PAT maakt clients makkelijk, peers moeilijk

Voor webverkeer:

```text
client -> internet:443
antwoord -> bestaande mapping -> client
```

Voor mesh VPN:

```text
Laptop A achter NAT A  <==?>  Laptop B achter NAT B
```

Probleem:

- beide kanten lijken "binnen" te zitten;
- private adressen zijn niet routeerbaar over internet;
- geen van beide heeft vanzelf een publiek inbound endpoint.

Daarom is NAT traversal nodig.

---

# Stateful firewall is niet hetzelfde als NAT

| Mechanisme | Vraag | Voorbeeld |
|---|---|---|
| Routing | waar moet het pakket naartoe? | default route naar internetgateway |
| NAT/PAT | welk adres en welke poort worden vertaald? | private bron wordt publiek endpoint |
| Stateful firewall | past dit bij toegestane state of beleid? | retourverkeer wordt doorgelaten |
| VPN-policy | mag deze identiteit deze service gebruiken? | student mag HTTP, niet SSH |

Een pakket kan correct gerouteerd en vertaald worden, maar alsnog geweigerd worden.

---

# Troubleshootingvolgorde

```text
route aanwezig?
  -> NAT/endpoint bruikbaar?
    -> firewall laat transport toe?
      -> VPN-pad bestaat?
        -> VPN-policy laat service toe?
          -> applicatie luistert en antwoordt?
```

Deze volgorde voorkomt dat je willekeurig policy verruimt terwijl het echte probleem bijvoorbeeld een verkeerde listener is.

---

<!-- _class: question -->

## Wat kan hier misgaan?

`tailscale status` toont de server als online.

Maar:

```text
curl http://100.x.y.z:8080
```

faalt.

Welke controles doe je vóór je ACL's of firewallregels versoepelt?

---

# NAT traversal: het doel

Twee peers achter NAT willen rechtstreeks praten.

```text
Laptop A achter NAT A
Laptop B achter NAT B
```

Ze moeten ontdekken:

- welke publieke endpoints de buitenwereld ziet;
- welke lokale endpoints bruikbaar zijn;
- hoe NAT en firewall zich gedragen;
- of beide kanten bijna gelijktijdig kunnen uitsturen;
- of de mapping lang genoeg blijft bestaan.

---

# Endpoint discovery met STUN

Een client kent lokaal:

```text
192.168.1.50:41641
```

De buitenwereld ziet misschien:

```text
203.0.113.20:45123
```

STUN beantwoordt één vraag:

> Van welk publiek IP-adres en welke bronpoort ontving jij mijn UDP-pakket?

STUN transporteert niet de applicatie-inhoud en opent geen onbeperkte inbound toegang.

---

# UDP hole punching

Sterk vereenvoudigd:

```text
1. Peer A stuurt UDP naar publiek endpoint van B.
2. NAT A maakt een mapping.
3. Peer B stuurt UDP naar publiek endpoint van A.
4. NAT B maakt een mapping.
5. Als timing en NAT-gedrag gunstig zijn, laten beide kanten verkeer door.
```

Het lijkt alsof peers inkomend verkeer ontvangen.

Technisch hebben beide kanten eerst zelf uitgaand verkeer gestuurd.

---

# Waarom lukt NAT traversal niet altijd?

| Probleem | Effect |
|---|---|
| symmetric NAT | mapping hangt sterk af van externe bestemming |
| strenge outbound firewall | UDP naar onbekende bestemmingen wordt geblokkeerd |
| korte UDP-timeout | mapping verdwijnt snel |
| geen hairpinning | publiek endpoint werkt niet goed binnen dezelfde NAT |
| double NAT | mapping op één laag volstaat niet |
| CGNAT | gebruiker kan ISP-NAT niet configureren |
| captive portal | verkeer wordt eerst onderschept |

**NAT traversal is een poging, geen garantie.**

---

# Wat bewijst een directe verbinding?

Een direct pad bewijst:

- peers vonden op dat moment een bruikbaar UDP-pad;
- dit peerpaar kon de NAT/firewallcombinatie passeren;
- het actuele netwerk liet dat toe.

Het bewijst niet:

- dat één peer permanent publiek bereikbaar is;
- dat elk ander netwerk direct zal werken;
- dat policy en applicatiebeveiliging correct zijn;
- dat toekomstige mappings gelijk blijven.

> Eén eerste DERP-pong is ook geen bewijs dat direct onmogelijk is.

---

# Port mapping en port forwarding

| Mechanisme | Wie configureert? | Lifecycle | Risico |
|---|---|---|---|
| UPnP, NAT-PMP, PCP | client vraagt aan gateway | dynamisch | onbeheerde clients kunnen mappings krijgen |
| handmatige port forwarding | beheerder configureert gateway | blijft vaak staan | vergeten regels vergroten aanvalsoppervlak |
| host firewallregel | endpointbeheerder | lokaal | helpt niet door upstream NAT heen |

Voorbeeld:

```text
WAN UDP 41641 -> 192.168.1.50 UDP 41641
```

---

# Enterprise design choice: forwarding of niet?

| Endpoint | Meestal verstandig? | Waarom |
|---|---|---|
| mobiele laptop | nee | wisselend netwerk, geen serverrol |
| tijdelijke lab-VM | meestal nee | lifecycle en eigenaar zijn tijdelijk |
| subnet router | soms | vaste rol en veel verkeer |
| exit node | soms | performance en centrale internetroute |
| site-to-site gateway | vaak | beheerde infrastructuur |

**Port forwarding is een performance- en beheerkeuze, geen vervanging voor VPN-policy.**

---

<!-- _class: divider -->

# Direct, peer relay of DERP

## Het pad bepaalt performance en metadata, niet automatisch de inhoudelijke veiligheid

---

# DERP als encrypted relay

DERP staat voor **Designated Encrypted Relay for Packets**.

```text
Device A == WireGuard encrypted == DERP == WireGuard encrypted == Device B
```

DERP kan:

- connectieopbouw helpen;
- een eerste bruikbaar datapad geven;
- fallback blijven wanneer direct verkeer faalt.

DERP hoort de tunnelinhoud niet te ontsleutelen.

---

# Hoe Tailscale een pad kiest

```text
nieuw peerpaar
    |
    v
DERP als onmiddellijk bruikbaar pad
    |
    +--> NAT traversal slaagt --------> direct UDP
    |
    +--> direct faalt, peer relay beschikbaar --> peer relay
    |
    +--> alternatieven falen ---------> DERP blijft datapad
```

Een verbinding kan later opnieuw wisselen wanneer netwerk, mapping of firewallstate verandert.

---

# Connection types correct interpreteren

| Observatie | Correcte interpretatie |
|---|---|
| eerste pongs via DERP, daarna direct | normale opbouw terwijl NAT traversal loopt |
| blijvend `peer-relay` | direct lukt niet, maar tailnetpeer relayeert |
| blijvend `relay <regio>` | DERP blijft fallback |
| eerst direct, later relay | pad, mapping of firewallstate veranderde |
| `UDP: true` in `netcheck` | UDP werkt naar testinfrastructuur, niet noodzakelijk naar elke peer |

**Bewijsregel:** noteer bronnetwerk, doelpeer, tijdstip, connection type en latency samen.

---

# Direct is meestal sneller

<div class="columns">
<div class="card">

### Direct

```text
Laptop A == encrypted UDP == Laptop B
```

- minder hops;
- lagere latency;
- hogere throughput;
- geen relaycapaciteit als bottleneck.

</div>
<div class="card">

### Relayed

```text
Laptop A == encrypted == Relay == encrypted == Laptop B
```

- extra tussenpunt;
- mogelijk geografische omweg;
- extra capaciteitsgrens;
- meer zichtbare relaymetadata.

</div>
</div>

---

# Eerlijke vergelijking: Devbit versus campusroam

Houd zoveel mogelijk constant:

| Meetveld | Waarom noteren? |
|---|---|
| datum en tijd | belasting verandert doorheen de dag |
| bron- en doelnetwerk | NAT/firewallpad verandert |
| connection type | direct en relay zijn niet gelijkwaardig |
| RTT over meerdere samples | eerste pongs kunnen opbouw bevatten |
| throughput en testduur | korte piek is geen duurzame capaciteit |
| packet loss, jitter, MTU | verklaren symptomen voorbij "snel/traag" |
| CPU en applicatiegedrag | voorkomen een verkeerde netwerkdiagnose |

Verander bij voorkeur één variabele: **het netwerk van de laptop**.

---

<!-- _class: question -->

## Mini-case

Een student meet:

- Devbit: `direct`, 12 ms, goede throughput;
- campusroam: `relay fra`, 58 ms, lagere throughput;
- HTTP via Tailscale werkt in beide gevallen;
- HTTP via Devbit-IP faalt vanaf campusroam.

Welke conclusies zijn sterk?

Welke conclusies zijn te groot voor dit bewijs?

---

<!-- _class: divider -->

# Zichtbaarheid

## Versleutelde inhoud is niet hetzelfde als onzichtbare metadata

---

# Wat ziet de lokale netwerkbeheerder?

Mogelijk zichtbaar:

- MAC-adres en lokaal IP;
- DHCP-hostname of device fingerprinting;
- ARP/NDP;
- DNS als lokale DNS gebruikt wordt;
- buitenste bestemmings-IP's;
- poorten en protocollen;
- timing en volume;
- VPN-, relay- of control-planeverkeer.

Normaal niet zichtbaar:

- HTTP-pad binnen de tunnel;
- SSH-commando's;
- interne payload;
- bestanden of tokens binnen de tunnel.

---

# Zichtbaarheid verschilt per observator

| Observator | Ziet meestal wel | Ziet normaal niet |
|---|---|---|
| lokaal LAN/wifi | lokaal device, buitenste flows, timing, volume | tunnelinhoud en interne payload |
| bedrijfsfirewall | policy hits, blokkeringen, buitenste metadata | end-to-end WireGuard-plaintext |
| ISP | publieke endpoints, poorten, timing, volume | interne IP's en applicatiepayload |
| VPN-control plane | devices, users, keys, policy, DNS/routes | niet automatisch peer-to-peer plaintext |
| DERP-beheerder | endpoints, regio, volume, timing | HTTP/SSH-inhoud in de tunnel |
| endpoint zelf | ontsleutelde data die het verwerkt | niets buiten zijn context |

---

# Packet captures: binnenkant versus buitenkant

| Capturepunt | Verwacht | Verkeerde conclusie |
|---|---|---|
| `tailscale0` | binnenste IP-verkeer en testpayload | "de VPN versleutelt niet" |
| fysieke interface bij direct pad | buitenste UDP-flow naar peerendpoint | "niemand ziet iets" |
| fysieke interface bij DERP | verkeer naar relay, vaak TCP/443 | "DERP ontsleutelt de tunnel" |

Een capture is observatiebewijs.

Combineer met:

<span class="tag">protocolkennis</span>
<span class="tag">peeridentiteit</span>
<span class="tag">path status</span>
<span class="tag">negatieve toegangstest</span>

---

# Split tunnel en full tunnel

| Vraag | Split tunnel | Full tunnel |
|---|---|---|
| Welke routes gaan door VPN? | alleen specifieke routes | meestal `0.0.0.0/0` via VPN |
| Ziet lokale wifi gewone websites? | ja, buiten VPN | meestal minder |
| Ziet VPN-exit internetmetadata? | beperkt | veel meer |
| Is centraal internetbeleid eenvoudiger? | minder | meer |
| Is privacy automatisch beter? | nee | nee |

Bij IPv6 moet je dezelfde vraag apart controleren.

> Full tunnel verschuift zichtbaarheid naar de exit node.

---

# Subnet router en exit node

<div class="columns">
<div class="card">

### Subnet router

```text
Laptop -> VPN -> subnet router -> 10.20.10.4
```

- maakt intern subnet bereikbaar;
- ziet interne bestemming en poort;
- SNAT beïnvloedt bronzichtbaarheid.

</div>
<div class="card">

### Exit node

```text
Laptop -> VPN -> exit node -> internet
```

- routeert internetverkeer;
- ziet externe bestemmingen en metadata;
- wordt nieuw vertrouwenspunt.

</div>
</div>

---

# VPN en DNS

DNS kan veel verklappen:

```text
netbox.voltlab.lan
admin.internal.example
git.company.local
```

Test DNS apart van bereikbaarheid:

| Test | Diagnose bij afwijking |
|---|---|
| MagicDNS-naam resolveert naar Tailscale-IP | MagicDNS of client-DNS fout |
| Split DNS-zone gebruikt bedoelde resolver | resolverroute of DNS-policy fout |
| verbinding naar geresolveerd IP werkt | routing, ACL, host firewall of applicatie |
| interne query zichtbaar in lokale capture | DNS lekt buiten bedoelde route |

---

# Firewalls rond de VPN

<div class="columns">
<div>

### Voor de VPN

- inbound naar vaste gateway;
- outbound UDP voor direct pad;
- TCP/443 voor control plane en DERP;
- logging van allow en deny;
- rate limiting voor publieke endpoints.

</div>
<div>

### Achter de VPN

- segmentatie blijft nodig;
- VPN-gebruiker mag niet automatisch alle VLAN's bereiken;
- partner, medewerker, student en admin krijgen verschillende toegang;
- host firewall blijft relevant.

</div>
</div>

---

# Defense in depth vraagt positieve én negatieve tests

| Laag | Positieve test | Negatieve test |
|---|---|---|
| buitenste firewall | verwachte VPN-flow verschijnt | onverwachte inbound service blijft dicht |
| VPN-policy | toegelaten identiteit bereikt service | niet-toegelaten poort wordt geweigerd |
| host firewall | service werkt via VPN-interface | service niet via LAN of publiek adres |
| applicatie | geldige request slaagt | ongeldige identity of functie faalt |

> VPN-toegang is een pad, geen toestemming tot alles achter dat pad.

---

<!-- _class: question -->

## Checkpoint

Een beheerder zegt:

> "De VPN is versleuteld, dus we hoeven alleen de tunnelpoort open te zetten."

Welke ontwerpvragen ontbreken nog?

Denk aan:

<span class="tag">identity</span>
<span class="tag">policy</span>
<span class="tag">host firewall</span>
<span class="tag">DNS</span>
<span class="tag">logging</span>
<span class="tag">lifecycle</span>

---

# Typische misverstanden

| Misverstand | Betere formulering |
|---|---|
| VPN maakt mij anoniem | VPN verschuift vertrouwen en zichtbaarheid |
| versleuteld betekent veilig | encryptie zonder least privilege blijft riskant |
| relay betekent onveilig | relaygebruik is vaak performance- en metadata-vraag |
| direct is altijd beter | direct is sneller, maar beleid kan centraal pad eisen |
| firewall lastig, dus alles open | meet, open minimaal, test opnieuw |

---

# Analysecase: bedrijfsfirewall laat alleen TCP/443 toe

Gevolg:

- control plane en DERP kunnen bereikbaar blijven;
- directe WireGuard-UDP lukt mogelijk niet;
- verbinding werkt, maar blijft relayed;
- latency en throughput kunnen slechter zijn.

Sterke conclusie:

> De firewall verhindert directe VPN-data plane, niet noodzakelijk de volledige VPN-connectiviteit.

Ontwerpvraag: welke minimale UDP-toegang is verantwoord, en voor welke endpointrol?

---

# Van observatie naar ontwerpbeslissing

```text
Observatie:
  tailscale ping blijft via DERP; RTT is hoger op campusroam.

Verklaring:
  direct UDP lukt voor dit peerpaar niet.

Risico:
  inhoud blijft versleuteld, maar relaymetadata en latency blijven.

Beslissing:
  mobiele laptop: relay aanvaarden.
  vaste gateway: gerichte UDP-bereikbaarheid onderzoeken.

Bewijs:
  connection type, RTT, throughput, logs en negatieve servicetest.
```

---

# Van theorie naar praktijk

In de workshop onderzoek je met Tailscale:

- een Debian-server in Devbit;
- een laptop die wisselt tussen Devbit en eduroam/campusroam;
- `tailscale netcheck`, `tailscale ping` en `tailscale status`;
- directe, peer-relay- of DERP-paden;
- captures op `tailscale0` en de fysieke interface;
- split tunnel, DNS en zichtbare metadata;
- positieve en negatieve securitytests.

Doel: **meten, interpreteren en verantwoorden**, niet een gewenst pad afdwingen.

---

<!-- _class: question -->

## Voorbereidende case

Je meet vanaf campusroam:

- `tailscale ping` toont eerst DERP en daarna direct;
- `curl` naar het Tailscale-IP werkt;
- `curl` naar het Devbit-IP faalt;
- capture op `tailscale0` toont de HTTP-marker;
- capture op de fysieke interface toont de marker niet.

Welke drie conclusies kan je onderbouwen?

Welke ene conclusie mag je nog niet trekken?

---

# Wat moet je onthouden?

1. Een VPN is veilig over een onbekend netwerk omdat de tunnel niet op dat netwerk vertrouwt.
2. Encryptie, integriteit, authenticatie en autorisatie zijn verschillende eigenschappen.
3. NAT traversal probeert een direct pad te vinden, maar firewalls en NAT bepalen mee of dat lukt.
4. DERP of relaygebruik is niet automatisch onveilig, maar beïnvloedt performance en metadata.
5. Professionele VPN-analyse koppelt bescherming, padkeuze, zichtbaarheid, policy en meetbewijs.
