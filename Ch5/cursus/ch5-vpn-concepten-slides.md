---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks - Hoofdstuk 5
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
    grid-template-columns: repeat(8, 1fr);
    gap: 9px;
    margin-top: 0.8em;
  }
  .pipeline .node {
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    padding: 13px 9px;
    text-align: center;
    font-size: 0.58em;
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
  .device.warn { border-top-color: var(--amber); }
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

## Hoofdstuk 5 - VPN-concepten

**Private toegang ontwerpen over een netwerk dat je niet beheert**

---

# BluePeak werkt niet meer alleen op kantoor

De interne diensten blijven achter firewalls, maar gebruikers en systemen zitten verspreid:

<span class="tag">thuiswerkers</span>
<span class="tag">IT-beheer</span>
<span class="tag">filialen</span>
<span class="tag">partners</span>
<span class="tag">cloudservers</span>

De centrale vraag:

> Hoe geef je toegang tot interne systemen zonder die systemen rechtstreeks op het internet te publiceren?

---

<!-- _class: question -->

## Startvraag

# Een interne webdienst moet remote bereikbaar zijn.

Wat is de slechtste snelle oplossing die technisch kan werken?

En welk risico introduceert die oplossing?

---

# Leerdoelen

Na deze les kan je:

1. verklaren welk enterprise-probleem een VPN oplost en wat een VPN niet bewijst;
2. tunnel, encapsulatie, encryptie, authenticatie, integriteit en autorisatie onderscheiden;
3. remote-access-, site-to-site-, full-tunnel- en split-tunnelkeuzes vergelijken;
4. VPN-routing, adressen, DNS en firewallbeleid analyseren bij een concrete flow;
5. Tailscale plaatsen als identity-aware overlay met control plane en data plane;
6. VPN-toegang testen, documenteren en beperken volgens least privilege en lifecyclebeheer.

---

# Een VPN is een toegangspad, geen vrijkaart

<div class="pipeline">
  <div class="node"><strong>identiteit</strong><br>wie vraagt toegang?</div>
  <div class="node"><strong>toestel</strong><br>welk endpoint?</div>
  <div class="node"><strong>tunnel</strong><br>welke private verbinding?</div>
  <div class="node"><strong>route</strong><br>welk pad?</div>
  <div class="node"><strong>policy</strong><br>welke flow mag?</div>
  <div class="node"><strong>test</strong><br>werkt en blokkeert het?</div>
  <div class="node"><strong>logging</strong><br>welk bewijs?</div>
  <div class="node"><strong>lifecycle</strong><br>wanneer stopt toegang?</div>
</div>

Een professionele VPN-keuze begint dus niet bij een product.

**Start bij de noodzakelijke communicatieflow.**

---

# Welke zwakke alternatieven vermijdt een VPN?

| Zwakke aanpak | Waarom riskant? | Betere richting |
|---|---|---|
| interne dienst port-forwarden | publiek aanvalsoppervlak per dienst | private toegang of applicatieproxy |
| RDP/SSH op internet | beheerprotocol wordt doelwit | VPN naar jump server |
| gedeeld VPN-account | acties niet persoonlijk traceerbaar | persoonlijke identiteit + logging |
| brede partnerregel | laterale toegang bij compromis | aparte partnerzone + minimale flows |
| tijdelijke toegang niet registreren | toegang blijft bestaan | eigenaar, einddatum en review |

> De VPN beperkt hoe je een dienst bereikt. De dienst zelf blijft ook verantwoordelijk voor autorisatie.

---

# VPN, proxy of gepubliceerde applicatie?

| Behoefte | Mogelijke oplossing | Ontwerpoverweging |
|---|---|---|
| een moderne webapp gebruiken | reverse proxy of identity-aware proxy | toegang tot applicatie, niet tot subnet |
| meerdere interne protocollen gebruiken | remote-access-VPN | flexibel, maar groter clientbereik |
| twee netwerken permanent koppelen | site-to-site-VPN | routes en policies voor hele netwerken |
| remote beheer uitvoeren | VPN naar jump server | management blijft afgeschermd |

**Enterprise design choice:** kies het kleinste toegangspad dat de zakelijke flow correct ondersteunt.

---

<!-- _class: divider -->

# 1 - Tunnel, vertrouwen en cryptografie

## Het internet levert transport, niet vertrouwen

---

# Het internet is geen trust zone

Je beheert de tussenliggende netwerken niet:

- publieke wifi;
- thuisrouter en NAT;
- providers;
- internetrouters;
- externe firewalls.

Een VPN voegt daarom zelf zekerheden toe:

<span class="tag">vertrouwelijkheid</span>
<span class="tag">integriteit</span>
<span class="tag">peer-authenticatie</span>
<span class="tag">user-authenticatie</span>
<span class="tag">autorisatie</span>
<span class="tag">auditability</span>

---

# Verbonden is niet hetzelfde als vertrouwd

| Een VPN-verbinding bewijst niet automatisch... | Praktisch risico |
|---|---|
| dat het toestel malwarevrij is | malware gebruikt toegestane flow mee |
| dat de gebruiker alle interne diensten nodig heeft | laterale beweging |
| dat de account nog terecht actief is | slechte offboarding |
| dat de applicatie veilig is | kwetsbare dienst blijft kwetsbaar |
| dat alle verkeer via VPN loopt | split tunnel laat publiek verkeer lokaal |

> Behandel VPN-verkeer als een aparte bronzone, niet als "binnen = vertrouwd".

---

# Wat doet een VPN-tunnel?

```text
origineel pakket
[ intern bron-IP | intern doel-IP | payload ]
                  |
                  | VPN verwerkt en beschermt
                  v
transport over internet
[ buitenste header | versleutelde VPN-data ]
                  |
                  | VPN-peer controleert en pakt uit
                  v
origineel pakket naar bestemming
```

**Encapsulatie:** het oorspronkelijke pakket krijgt een vorm die over het transportnetwerk kan.

---

# Waar eindigt de tunnel?

| Endpointtype | Voorbeeld | Waar eindigt de bescherming? |
|---|---|---|
| client naar gateway | laptop naar bedrijfsfirewall | laptop en gateway |
| gateway naar gateway | filiaal naar hoofdkantoor | beide netwerkranden |
| device naar device | laptop naar server met Tailscale | rechtstreeks op beide devices |
| device naar subnet router | laptop naar legacy-LAN | op client en subnet router |
| device naar exit node | laptop naar gecontroleerde internetuitgang | op client en exit node |

Controleer daarna altijd welk netwerksegment na het tunnelendpoint nog volgt.

---

# Begrippen die vaak door elkaar lopen

| Principe | Doel | Als dit ontbreekt... |
|---|---|---|
| encryptie | inhoud onleesbaar maken | verkeer kan worden afgeluisterd |
| endpoint-authenticatie | juiste VPN-peer bewijzen | aanvaller kan zich voordoen als gateway |
| user-authenticatie | mens of account bewijzen | gedeelde of gestolen identiteit blijft vaag |
| integriteit | wijziging detecteren | pakketten kunnen gemanipuleerd worden |
| autorisatie | bepalen wat mag | correcte login krijgt te brede toegang |

**Cryptografie beschermt communicatie; beleid begrenst gebruik.**

---

# Gebruiker en toestel zijn aparte identiteiten

```text
menselijke identiteit: "Dit is Alice."
device-identiteit:    "Dit is de beheerde laptop van Alice."
```

| Situatie | Wat weet je? | Resterend risico |
|---|---|---|
| gekende gebruiker, onbekend toestel | accountcontrole is gelukt | prive- of onveilig toestel |
| gekend toestel, gestolen account | device is geregistreerd | aanvaller gebruikt credentials |
| gebruiker en toestel gekend | twee contexten beschikbaar | policy blijft nodig |
| gedeeld account | identiteit is niet persoonlijk | audit en offboarding zijn zwak |

---

<!-- _class: question -->

## Wat kan hier misgaan?

Een beheerder zegt:

> "De VPN gebruikt encryptie en MFA, dus VPN-users mogen naar alle interne subnetten."

Welke ontbrekende ontwerpvragen zie je?

<span class="tag">rol</span>
<span class="tag">device</span>
<span class="tag">bestemming</span>
<span class="tag">poort</span>
<span class="tag">lifecycle</span>
<span class="tag">logging</span>

---

<!-- _class: divider -->

# 2 - VPN-modellen en routekeuzes

## Remote access, site-to-site, full tunnel en split tunnel

---

# Remote-access-VPN

Een individueel toestel krijgt toegang tot bepaalde resources.

```text
remote gebruiker
      |
      | internet
      v
VPN-client of browser
      |
      | beveiligd toegangspad
      v
VPN-zone -> toegestane interne diensten
```

| Rol | Verantwoordelijkheid |
|---|---|
| gebruiker | persoonlijk aanmelden |
| client/device | tunnel bouwen en routes installeren |
| identity provider | identiteit en MFA bevestigen |
| policy/firewall | toegestane flows afdwingen |
| doelservice | eigen applicatierechten toepassen |

---

# Remote access is een nieuwe ingang

| Beleidsvraag | Waarom belangrijk? |
|---|---|
| Mag elk personeelslid verbinden? | niet elke functie heeft remote netwerktoegang nodig |
| Zijn prive-toestellen toegestaan? | minder controle over patches en malware |
| Is MFA verplicht? | remote login is sterk blootgesteld |
| Welke groepen bestaan er? | staff, finance, IT en partners hebben andere noden |
| Wanneer vervalt toegang? | vergeten accounts vergroten het aanvalsoppervlak |
| Wat wordt gelogd? | login alleen bewijst de gebruikte flows niet |

Client-based toegang geeft een netwerkpad vanaf software op het toestel. Clientless toegang beperkt zich meestal tot browser- of applicatiegerichte toegang.

**Remote access wordt per rol en bedrijfsnood ontworpen, niet per gemak.**

---

# Site-to-site-VPN

Een site-to-site-VPN verbindt netwerken via gateways.

```text
+------------------+       internet       +------------------+
| Hoofdkantoor     |====== VPN-tunnel ====| Filiaal          |
| 10.10.0.0/16     |                      | 10.20.0.0/16     |
+------------------+                      +------------------+
```

| Kenmerk | Remote access | Site-to-site |
|---|---|---|
| endpoints | device en gateway/peer | twee gateways |
| identiteit | gebruiker en device | gateway en netwerkcontext |
| routes | op client | op routers/firewalls |
| typische fout | gebruiker krijgt te veel | hele sites vertrouwen elkaar te breed |

---

# Full tunnel

Bij full tunnel stuurt de client ook normaal internetverkeer via VPN.

```text
laptop
  |
  | default route via VPN
  v
VPN-gateway of exit node
  |                 |
  v                 v
interne diensten    internet
```

| Winst | Kost of risico |
|---|---|
| centrale internetuitgang | extra bandbreedte |
| centrale filtering | hogere latency |
| voorspelbaar bronadres | grotere afhankelijkheid |
| bescherming op onbetrouwbare wifi | privacy- en loggingvragen |

---

# Full tunnel aantonen

Een groen VPN-icoon bewijst geen full tunnel.

| Test | Zonder full tunnel | Met full tunnel |
|---|---|---|
| publiek bron-IP | lokale internetlijn | VPN-uitgang of exit node |
| route naar `0.0.0.0/0` | lokale gateway | VPN-interface/exitpad |
| interne dienst openen | kan via VPN | kan via VPN |
| exit node stoppen | internet blijft lokaal | internet kan wegvallen |

**Typische fout:** alleen een interne server pingen en besluiten dat al het verkeer door VPN loopt.

---

# Split tunnel

Bij split tunnel gaat alleen geselecteerd verkeer via VPN.

```text
                    +--> interne routes via VPN
laptop routekeuze --|
                    +--> overige routes via lokale gateway
```

| Voordeel | Risico |
|---|---|
| minder VPN-bandbreedte | geen centrale controle over publiek verkeer |
| lagere latency | "VPN actief" wordt misleidend |
| kleinere storingsimpact | routeconflict |
| gerichte toegang | DNS-lek of fout resolverpad |

---

# Full of split kiezen

| Scenario | Waarschijnlijke keuze | Motivering |
|---|---|---|
| medewerker gebruikt intranet | split tunnel | beperkt omweg en centrale belasting |
| onbetrouwbare wifi moet via gefilterde uitgang | full tunnel | centraal egresspad is onderdeel van de eis |
| partner heeft een webdienst nodig | split tunnel of applicatieproxy | partnerinternet hoeft niet via organisatie |
| externe dienst vereist vast bronadres | full tunnel voor die use case | verkeer moet via gekende uitgang |

> Er bestaat geen universeel veiligste keuze.

---

<!-- _class: question -->

## Checkpoint - modelkeuze

BluePeak wil dat een externe consultant een projectportaal op HTTPS kan bereiken.

Welke keuze verdedig je?

- remote-access-VPN of applicatieproxy?
- full tunnel of split tunnel?
- persoonlijke account of gedeeld account?
- toegang tot portaal of tot volledig servernetwerk?

---

<!-- _class: divider -->

# 3 - Adressen, routes, policy en DNS

## De tunnel is actief, maar werkt de flow?

---

# Subnet overlap breekt routekeuze

Een VPN voegt adressen en routes toe: lokale clientadressen, VPN-pooladressen, interne serveradressen, overlay-adressen en publieke endpointadressen.

```text
thuisnetwerk:    192.168.1.0/24
bedrijfsnetwerk: 192.168.1.0/24
```

Een pakket voor `192.168.1.50` kan lokaal vertrekken in plaats van via VPN.

| Symptoom | Mogelijke verklaring |
|---|---|
| server werkt op kantoor maar niet thuis | thuisprefix overlapt |
| DNS geeft juiste IP, verbinding faalt | naamresolutie klopt, route niet |
| ander thuisnetwerk werkt wel | lokaal adresplan verschilt |
| NAT-workaround nodig | overlap wordt gemaskeerd |

---

# Heenweg en terugweg moeten kloppen

```text
client -> VPN-pad -> firewall/router -> server
client <- VPN-pad <- firewall/router <- server
```

| Controle | Vraag |
|---|---|
| clientroute | kiest de client de VPN-interface? |
| geadverteerde route | kent de VPN-omgeving het prefix? |
| route approval | mag die route gebruikt worden? |
| forwarding | stuurt de gateway door? |
| return route | weet het LAN hoe het VPN-adres terug moet? |
| NAT | wordt bron bewust vertaald? |
| firewall state | zijn request en response toegestaan? |

---

# Route bestaat, policy ontbreekt

```text
geldige identiteit
      + device toegelaten
      + route aanwezig
      + policy laat flow toe
      + firewall laat flow toe
      + dienst luistert
      = applicatie kan werken
```

Een route beantwoordt:

> Welk next hop of welke interface gebruik ik voor deze bestemming?

Een route geeft geen recht om die bestemming te gebruiken.

---

# VPN hoort in het firewallmodel

| Bronzone | Bestemming | Service | Actie | Reden |
|---|---|---|:---:|---|
| VPN-Staff | intranet | TCP 443 | allow | medewerkersportaal |
| VPN-Staff | finance-app | TCP 443 | deny | geen financefunctie |
| VPN-Finance | finance-app | TCP 443 | allow | financieel proces |
| VPN-IT | jump server | beheerpoort | allow | gecontroleerd beheerpad |
| VPN-Partner | partnerportaal | TCP 443 | allow | contractuele support |
| VPN-Partner | servernetwerk | any | deny | laterale toegang voorkomen |
| VPN-any | managementzone | any | deny | management plane beschermen |

---

# Meerdere policy-lagen kunnen blokkeren

| Laag | Voorbeeldcontrole |
|---|---|
| VPN- of overlaypolicy | mag deze user/device naar het doel? |
| perimeter/interne firewall | mag VPN-zone naar serverzone? |
| subnet router | wordt het pakket doorgestuurd? |
| hostfirewall | mag de bron de luisterpoort bereiken? |
| applicatie | mag de gebruiker deze functie uitvoeren? |

Een allow op laag een heft een deny op laag drie niet op.

**Zoek het eerste punt waar werkelijk verkeer wordt geweigerd.**

---

# VPN en DNS: IP werkt, naam niet

```text
curl https://10.30.40.10       -> werkt
curl https://intranet.example  -> werkt niet
```

| Vraag | Waarom relevant? |
|---|---|
| Welke resolver gebruikt de client? | publieke DNS kent interne namen niet |
| Welke zone is intern? | alleen die queries moeten naar interne DNS |
| Is DNS-server via VPN bereikbaar? | configuratie zonder route werkt niet |
| Krijgt partner dezelfde zone? | te veel DNS-info kan lekken |
| Test je IP of hostname? | IP-test is geen DNS-test |

---

# Split DNS en MagicDNS

| Concept | Lost welk probleem op? |
|---|---|
| **split DNS** | queries voor interne zones naar een specifieke resolver sturen |
| **MagicDNS** | Tailscale-devices automatisch bruikbare tailnetnamen geven |

Voor MagicDNS controleer je:

1. werkt de applicatie op Tailscale-IP?
2. lost de MagicDNS-naam naar het verwachte adres op?
3. werkt dezelfde applicatie op naam?
4. faalt een niet-bestaande naam voorspelbaar?

---

<!-- _class: question -->

## Troubleshootingcase - IP werkt, naam niet

Alice kan `https://10.30.40.10` openen via VPN.

`https://intranet.bluepeak.internal` faalt.

Zet je controles in volgorde:

- resolver van de client;
- DNS-zone en suffix;
- bereikbaarheid van interne DNS;
- resultaat van de query;
- applicatietest op hostname.

Wat mag je nog niet concluderen?

---

<!-- _class: divider -->

# 4 - Tailscale als overlay

## Identity-aware toegang bovenop bestaande netwerken

---

# Tailscale in een enterprise-denkkader

Tailscale bouwt een private overlay bovenop bestaande netwerken.

Elk deelnemend device krijgt:

- een Tailscale-identiteit;
- een stabiel overlay-adres;
- peerinformatie en routes;
- DNS-configuratie;
- access policy.

De data plane gebruikt WireGuard voor het versleutelde datapad.

---

# Control plane en data plane

| Plane | Taken | Draagt applicatiepayload? |
|---|---|:---:|
| control plane | identiteit, device-registratie, peercoordinatie, routes, DNS en policy | nee |
| data plane | versleutelde pakketten tussen devices transporteren en filteren | ja |

```text
                 control plane
             identity, peers, policy
                /             \
               v               v
          laptop ==========> server
                 data plane
             WireGuard-beveiligd
```

---

# Direct, peer relay of DERP

Tailscale probeert een performant pad tussen peers te bouwen.

| Verbindingstype | Pad | Praktische impact |
|---|---|---|
| direct | device naar device | meestal laagste latency |
| peer relay | via aangewezen device in tailnet | alternatief wanneer direct niet lukt |
| DERP relay | via Tailscale-relayinfrastructuur | robuuste fallback, mogelijk hogere latency |

De payload blijft end-to-end met WireGuard beschermd.

Controleer pad en performance met `tailscale status`, `tailscale ping` en eventueel `tailscale netcheck`.

---

# Device lifecycle is security

| Fase | Vraag |
|---|---|
| onboarding | wie mag het toestel registreren? |
| naamgeving | kan een beheerder het toestel herkennen? |
| gebruik | welke routes en services mag het toestel bereiken? |
| review | is het toestel nog nodig en actueel? |
| cleanup | wordt toegang ingetrokken na lab, project of vertrek? |

Oude lab-VM's, tijdelijke laptops en vergeten devices zijn geen administratief detail.

**Ze zijn toegangspunten.**

---

<!-- _class: divider -->

# 5 - Exit nodes, subnet routers en beheer

## Breder bereik betekent bredere verantwoordelijkheid

---

# Exit node

Een exit node laat een Tailscale-client zijn internetverkeer via een ander tailnet-device uitsturen.

```text
remote laptop
     |
     | versleuteld via Tailscale
     v
exit node
     |
     | NAT/forwarding naar buiten
     v
internet
```

Conceptueel implementeert dit full tunnel voor de default routes van de client.

---

# Exit node versus subnet router

| Eigenschap | Exit node | Subnet router |
|---|---|---|
| hoofddoel | internetverkeer uitrouteren | private subnetten bereikbaar maken |
| typische route | `0.0.0.0/0`, `::/0` | bijvoorbeeld `10.30.40.0/24` |
| voorbeeld | laptop gebruikt campus als uitgang | laptop bereikt legacy-server |
| belangrijkste test | publiek bron-IP verandert | doel in subnet wordt bereikbaar |
| belangrijk risico | alle internet hangt van node af | breed intern prefix ontsloten |

---

# Van routeadvertentie naar werkende flow

| Voorwaarde | Functie |
|---|---|
| Tailscale op routerdevice | verbindt router met tailnet |
| IP forwarding | stuurt pakketten tussen interfaces |
| route advertisement | meldt achterliggend prefix |
| route approval | maakt route bruikbaar voor clients |
| access policy | beperkt wie naar welk doel mag |
| LAN- en hostfirewall | laat uiteindelijke serviceflow toe |
| return route of bewuste SNAT | zorgt dat antwoorden terugkomen |

---

# Remote management heeft hogere impact

```text
VPN-IT
  |
  | beperkte beheerflow
  v
jump server
  |
  | beperkt managementpad
  v
managementzone
```

| Ontwerp | Sterkte | Risico |
|---|---|---|
| VPN rechtstreeks naar elk beheertoestel | weinig tussenstappen | brede managementbereikbaarheid |
| VPN naar jump server | centraal controlepunt | extra component en logging nodig |

Management hoort niet in een algemene staff-VPN-regel.

---

<!-- _class: question -->

## Enterprise design choice

Een IT-admin vraagt:

> "Geef mijn VPN-account toegang tot alle switch- en firewallinterfaces. Dat is handig bij storingen."

Ontwerp een beter beheerpad.

Welke allow-test en deny-test horen daarbij?

---

<!-- _class: divider -->

# 6 - Testen, fouten en documentatie

## Bewijs dat noodzakelijke toegang werkt en onnodige toegang niet

---

# Typische VPN-fouten

| Fout | Waarschijnlijk symptoom | Eerste gerichte controle |
|---|---|---|
| tunnel niet actief | geen enkel VPN-doel bereikbaar | peer/device-status |
| route ontbreekt | specifiek subnet werkt niet | clientroutingtabel |
| return route ontbreekt | request vertrekt, geen antwoord | route op LAN/gateway |
| firewall blokkeert | route klopt, service timeout | logs en TCP-test |
| dienst luistert niet | host bereikbaar, app niet | service- en hostfirewallstatus |
| subnet overlap | werkt vanaf ene netwerk, niet ander | lokale en VPN-prefixes |
| DNS fout | IP werkt, naam niet | resolver en queryresultaat |

---

# Van laag naar gebruikersflow testen

| Volgorde | Test | Waarom? |
|---:|---|---|
| 1 | device verschijnt in inventory | onboarding en identiteit |
| 2 | VPN/peerstatus controleren | tunnel- of overlaylaag |
| 3 | route naar doel bekijken | routingbeslissing |
| 4 | doel-IP bereiken | basisbereikbaarheid indien toegestaan |
| 5 | servicepoort testen | firewall en luisterpoort |
| 6 | applicatie gebruiken | end-to-end gebruikersflow |
| 7 | verboden service proberen | least privilege |
| 8 | logs controleren | auditability |

---

# Testmatrix BluePeak

| Identiteit/bron | Bestemming | Service | Verwacht | Bewijs |
|---|---|---|:---:|---|
| Staff-VPN | intranet | HTTPS | allow | pagina + log |
| Staff-VPN | finance-app | HTTPS | deny | deny of timeout + log |
| Finance-VPN | finance-app | HTTPS | allow | applicatieflow |
| Partner-VPN | partnerportaal | HTTPS | allow | portaal opent |
| Partner-VPN | intranet | HTTPS | deny | negatieve test |
| IT-VPN | jump server | beheerpoort | allow | persoonlijke sessie |
| Staff-VPN | jump server | beheerpoort | deny | policygrens |

---

# VPN-policy eerst in mensentaal

| Onderdeel | Vraag |
|---|---|
| doel | welk bedrijfsproces vereist toegang? |
| identities | welke users, groepen of services? |
| devices | zijn prive-toestellen toegestaan? |
| authenticatie | welke MFA- of device-eisen? |
| destinations/services | welke hosts, subnetten, poorten? |
| tunnelmodel en DNS | split/full, resolver en zones |
| logging en lifecycle | welke events, eigenaar, review, offboarding? |
| testplan | welke allow- en deny-cases bewijzen het beleid? |

Daarna pas vertalen naar configuratie of access rules.

---

<!-- _class: question -->

## Voorbereidende case

Een partner moet tijdelijk een webapplicatie ondersteunen.

Formuleer de policy in mensentaal:

- identiteit en device-eis;
- bestemming en poort;
- tunnelmodel;
- looptijd en eigenaar;
- logging;
- positieve test;
- negatieve test.

---

<!-- _class: divider -->

# 7 - Naar de Tailscale-workshop

## Het gebruikte pad aantonen

---

# Labscenario

BluePeak heeft een Debian-VM met een webserver.

De VM staat achter een Proxmox-firewall die inkomende HTTP via het gewone netwerk blokkeert.

```text
Devbit client  --X-->  VM-IP:80

eduroam client --X-->  VM-IP:80

eduroam client + Tailscale  -->  Tailscale-IP:80
```

De opdracht is niet: "zet poort 80 open".

De opdracht is: **maak een private overlaytoegang aantoonbaar werkend.**

---

# Drie paden vergelijken

| Testpad | Wat test je werkelijk? | Mogelijk resultaat |
|---|---|---|
| lokaal op VM | service en lokale luisterpoort | moet eerst werken |
| rechtstreeks via lab-IP | campusrouting en firewallregels | kan per netwerk verschillen |
| via Tailscale-IP/naam | overlay, device identity, route en service | onafhankelijk van directe labroute |

Een geslaagde directe test via Devbit bewijst niet dat Tailscale gebruikt werd.

Noteer daarom altijd het gebruikte doeladres of de MagicDNS-naam.

---

# Van lab naar productie

| Thema | In het lab | In productie |
|---|---|---|
| identity | persoonlijk testaccount | centrale IdP, lifecycle en MFA |
| devices | laptop en tijdelijke VM | beheerde inventory en review |
| policy | beperkte demonstratie | change-controlled least privilege |
| availability | een VM kan volstaan | redundantie volgens impact |
| logging | screenshots en beperkte output | centrale, tijdgesynchroniseerde logs |
| secrets | handmatig weglaten | secretmanagement en rotatie |

---

# Wat moet je onthouden?

1. Een VPN maakt private communicatie mogelijk over niet-vertrouwd transport.
2. De tunnel verandert het pad, maar verleent niet automatisch vertrouwen.
3. Encryptie, authenticatie, integriteit, autorisatie, routes en DNS lossen verschillende problemen op.
4. Full tunnel stuurt default verkeer via VPN; split tunnel alleen geselecteerde routes.
5. Een professioneel VPN-ontwerp bewijst zowel **allow** als **deny** en beheert toegang doorheen de lifecycle.
