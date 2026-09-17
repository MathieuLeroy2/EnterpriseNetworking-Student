---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks - Hoofdstuk 8
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
    padding: 46px 66px 82px;
    font-size: 27px;
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
  pre code span {
    background: transparent !important;
    color: #f5f7f8 !important;
  }
  pre .hljs-attr,
  pre .hljs-attribute,
  pre .hljs-name,
  pre .hljs-title { color: #8bd3ff !important; }
  pre .hljs-string,
  pre .hljs-meta .hljs-string { color: #b7f7c2 !important; }
  pre .hljs-keyword,
  pre .hljs-literal,
  pre .hljs-selector-tag { color: #ffe08a !important; }
  pre .hljs-comment { color: #c4ced6 !important; }
  footer {
    color: var(--muted);
    font-size: 0.52em;
    bottom: 18px;
  }
  section::after {
    color: var(--muted);
    font-size: 0.58em;
    bottom: 18px;
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
  section.divider strong { color: white; }
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
  .three {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  .four {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
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
  section.compact { font-size: 25.5px; }
  section.compact pre { margin: 0.35em 0; }
  section.compact p { margin: 0.42em 0; }
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
    grid-template-columns: 1fr auto 1fr auto 1fr;
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
  .flow.wide {
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
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
  .vertical {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    max-width: 820px;
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

## Hoofdstuk 8 - Reverse proxies

**Webapplicaties publiceren via een gecontroleerd requestpad**

---

# BluePeak publiceert meer webapplicaties

BluePeak Services gebruikt vandaag:

- een intranet voor medewerkers;
- een helpdesk voor medewerkers en IT;
- een statuspagina voor operations;
- later mogelijk monitoring, documentatie en adminportalen.

<span class="tag">meerdere hostnames</span>
<span class="tag">verschillende backends</span>
<span class="tag">centrale logging</span>
<span class="tag">TLS</span>
<span class="tag">security controls</span>

> Hoe geef je toegang zonder elke backend rechtstreeks open te zetten?

---

<!-- _class: question -->

## Startvraag

# Drie interne webapps moeten bereikbaar worden.

# Publiceer je drie poorten, of een centraal toegangspunt?

Welke risico's ontstaan als elke applicatie haar eigen externe pad krijgt?

---

# Leerdoelen

Na deze les kan je:

1. forward proxies en reverse proxies vergelijken vanuit hun rol in het verkeer;
2. een HTTP-request volgen van client, DNS en `Host`-header tot backend;
3. host-based routing, path-based routing en virtual hosting verklaren;
4. Traefik-entrypoints, routers, rules, services en middleware aan elkaar koppelen;
5. reverse-proxypoorten, backendpoorten, TLS-modellen en forwarded headers beoordelen;
6. een reverse-proxyontwerp testen, troubleshooten en verantwoorden met positief en negatief bewijs.

---

# De oude oplossing schaalt slecht

```text
+----------+      NAT/firewall       +------------------+
| Client  | ----------------------> | intranet:80      |
|         | ----------------------> | helpdesk:8080    |
|         | ----------------------> | status:3000      |
+----------+                         +------------------+
```

| Wat werkt technisch? | Wat wordt moeilijker? |
|---|---|
| elke app is bereikbaar | veel firewallregels en poorten |
| elke backend beheert zichzelf | verspreide TLS, logs en headers |
| snel gebouwd | grotere kans op per ongeluk gepubliceerde admin- of testinterface |

**Connectiviteit is hier niet het probleem. Controle wel.**

---

# Een reverse proxy maakt een gecontroleerd requestpad

<div class="flow wide">
  <div class="node"><strong>Client</strong><br>browser of curl</div>
  <div class="arrow">&rarr;</div>
  <div class="node"><strong>DNS</strong><br>naam naar proxy-IP</div>
  <div class="arrow">&rarr;</div>
  <div class="node"><strong>Reverse proxy</strong><br>matcht route</div>
  <div class="arrow">&rarr;</div>
  <div class="node"><strong>Backend</strong><br>app verwerkt request</div>
</div>

De reverse proxy:

- ontvangt requests voor meerdere webapplicaties;
- kiest op basis van requestkenmerken de juiste backend;
- centraliseert publicatie, logging en bepaalde websecurityfuncties.

> Centraliseren maakt controle mogelijk, maar niet automatisch security.

---

# Forward proxy versus reverse proxy

| Kenmerk | Forward proxy | Reverse proxy |
|---|---|---|
| werkt namens | clients | servers of applicaties |
| typische richting | uitgaand naar internet | inkomend naar gepubliceerde apps |
| centrale vraag | welke sites mag een client bezoeken? | welke app krijgt dit request? |
| typische logging | gebruiker en externe bestemming | hostname, pad, statuscode, backend |
| plaatsing | tussen clients en internet | voor applicaties, vaak publicatiezone |

```text
client -> forward proxy -> internet
client -> reverse proxy -> interne webapp
```

Een VPN is geen proxy: die levert een beveiligd netwerkpad.

---

<!-- _class: question -->

## Mini-case

BluePeak heeft drie situaties:

- studentenwebverkeer wordt centraal gefilterd;
- medewerkers openen `helpdesk.bluepeak.test`;
- een beheerder maakt een VPN-tunnel naar kantoor.

**Welke situatie hoort bij forward proxy, reverse proxy of geen van beide?**

Leg uit vanuit: **namens wie werkt het component?**

---

# Waarom niet elke applicatie rechtstreeks publiceren?

| Probleem | Praktisch gevolg |
|---|---|
| backend rechtstreeks bereikbaar | een appfout wordt direct extern blootgesteld |
| meerdere publieke poorten | gebruikers en firewallbeheerders beheren losse uitzonderingen |
| TLS per applicatie | certificaten en TLS-policy raken verspreid |
| verspreide logging | incidentonderzoek vraagt correlatie achteraf |
| verschillende securityinstellingen | de zwakst beheerde app bepaalt mee het risico |
| wijzigende backendlocaties | DNS, NAT en firewall moeten vaker mee veranderen |

> Publiceer het gecontroleerde toegangspunt, niet elke backend afzonderlijk.

---

# Wat centraliseert de reverse proxy?

<div class="four">
  <div class="card"><strong>Publicatie</strong><br>een beperkt aantal frontendpoorten naar de proxy.</div>
  <div class="card"><strong>Routing</strong><br>hostnames of paden naar interne services.</div>
  <div class="card"><strong>Webcontrols</strong><br>TLS, headers, redirects of rate limits.</div>
  <div class="card"><strong>Observability</strong><br>access logs, statuscodes en routerinformatie.</div>
</div>

Belangrijke nuance:

**De proxy verbergt details, maar security by obscurity is geen beveiligingsmodel.**

---

<!-- _class: divider -->

# 1. Van hostname naar backend

## DNS brengt je naar de proxy; HTTP kiest de app

---

# De requestflow stap voor stap

<div class="pipeline">
  <div class="node"><strong>1</strong><br>browser vraagt hostname</div>
  <div class="node"><strong>2</strong><br>naam wijst naar proxy-IP</div>
  <div class="node"><strong>3</strong><br>client opent frontendpoort</div>
  <div class="node"><strong>4</strong><br>HTTP `Host` gaat mee</div>
  <div class="node"><strong>5</strong><br>routerrule matcht</div>
  <div class="node"><strong>6</strong><br>service kiest backend</div>
  <div class="node"><strong>7</strong><br>antwoord loopt terug</div>
</div>

**Elke stap kan apart slagen of falen.**

Troubleshooting begint dus met: tot waar geraakt het request aantoonbaar?

---

# DNS doet minder dan veel studenten denken

| Onderdeel | Vraag | Voorbeeld |
|---|---|---|
| DNS of hosts file | welk IP-adres hoort bij de naam? | `intranet.bluepeak.test -> 127.0.0.1` |
| TCP-connectie | welke proxypoort wordt bereikt? | `localhost:8080` |
| HTTP `Host`-header | welke webapp bedoelt de client? | `Host: intranet.bluepeak.test` |
| reverse-proxyrule | welke route matcht? | `Host(...)` |

**DNS kiest niet de backend. DNS brengt de client eerst naar de proxy.**

---

# De `Host`-header maakt virtual hosting mogelijk

```http
GET / HTTP/1.1
Host: intranet.bluepeak.test
```

Daardoor kan een enkele proxy-IP meerdere applicaties publiceren:

```text
proxy-IP:443
  +-- intranet.bluepeak.test -> intranetservice
  +-- helpdesk.bluepeak.test -> helpdeskservice
  +-- status.bluepeak.test   -> statusservice
```

De hostname zit dus niet alleen in DNS, maar ook in het HTTP-request.

---

# Twee tests, zelfde IP, ander resultaat

```text
http://localhost:8080
http://intranet.bluepeak.test:8080
```

Beide kunnen dezelfde proxypoort bereiken.

Het verschil:

- `localhost` bevat niet de hostname waarop de intranetrouter matcht;
- `intranet.bluepeak.test` bevat wel de bedoelde `Host`-waarde;
- zonder juiste hostname kan de proxy terecht geen backend kiezen.

Gericht testen kan ook zo:

```text
curl.exe -H "Host: intranet.bluepeak.test" http://127.0.0.1:8080
```

---

<!-- _class: question -->

## Wat kan hier misgaan?

Een student test:

```text
curl.exe http://localhost:8080
```

en concludeert:

> "Traefik werkt niet, want ik krijg niet het intranet."

Welke twee ontbrekende controles moet je eerst uitvoeren?

Welke hostname verwacht de router eigenlijk?

---

# DNS is geen autorisatie

Een niet-gepubliceerd DNS-record beschermt een applicatie niet vanzelf.

| Controle | Verwacht | Wat bewijst dit? |
|---|---|---|
| naam opzoeken | hostname wijst naar proxy-IP | naamresolutie |
| juiste hostname aanvragen | juiste app antwoordt | host-based routing |
| onbekende hostname aanvragen | geen interne app | geen te brede route |
| IP zonder juiste hostname | veilige default | geen onbedoelde catch-all |

Wie proxy-IP en `Host`-header kent, kan mogelijk nog steeds een request sturen.

**Toegang moet door netwerk- en applicatiebeleid worden afgedwongen.**

---

# Host-based en path-based routing

| Ontwerpvraag | Host-based routing | Path-based routing |
|---|---|---|
| voorbeeld | `helpdesk.example.com` | `apps.example.com/helpdesk` |
| scheiding in browser | duidelijker per hostname | gedeelde origin vraagt aandacht |
| afhankelijk van app-subpad | beperkt | sterk |
| typische valkuil | DNS wijst naar backend | app begrijpt externe prefix niet |
| workshopkeuze | gebruikt | niet gebruikt |

> Host-based routing is vaak eenvoudiger; path-based routing werkt alleen betrouwbaar wanneer de app haar externe pad correct begrijpt.

---

<!-- _class: divider -->

# 2. Traefik als concreet model

## Entrypoint, router, rule, middleware, service, backend

---

# De Traefik-keten

```text
entrypoint -> router + rule -> middleware -> service -> backendserver
```

| Onderdeel | Beantwoordt de vraag... |
|---|---|
| entrypoint | op welke lokale poort/protocol ontvangt Traefik verkeer? |
| router | welke configuratieroute behandelt dit request? |
| rule | wanneer matcht die router? |
| middleware | welke extra verwerking gebeurt onderweg? |
| service | naar welke logische backendgroep gaat het request? |
| server URL | waar is een concrete backend bereikbaar? |

Een Traefik-service is niet exact hetzelfde als een Docker Compose-service.

---

# Traefik-service versus Docker-service

```text
Traefik-service intranet
    -> server URL http://intranet:80
    -> Docker Compose-service intranet
    -> nginx luistert in de container op poort 80
```

Waarom dezelfde naam in de workshop?

- de mapping blijft leesbaar;
- studenten kunnen router, service en container volgen;
- de concepten blijven wel gescheiden.

**Bij troubleshooting volg je de naamketen expliciet.**

---

# Static configuration start Traefik zelf

Static config bepaalt hoe Traefik opstart.

| Static instelling | Functie in het lab |
|---|---|
| `--entrypoints.web.address=:80` | Traefik luistert intern op poort 80 |
| `--providers.file.filename=...` | dynamic config komt uit een bestand |
| `--providers.file.watch=true` | wijzigingen worden opgevolgd |
| `--api.dashboard=true` | dashboard staat aan |
| `--api.insecure=true` | onbeveiligd dashboard voor het lokale lab |
| `--accesslog=true` | requestlogging staat aan |

In productie is `api.insecure=true` een risico, geen normale keuze.

---

# Dynamic configuration beschrijft applicatieroutes

```yaml
http:
  routers:
    intranet:
      rule: "Host(`intranet.bluepeak.test`)"
      entryPoints:
        - web
      service: intranet

  services:
    intranet:
      loadBalancer:
        servers:
          - url: "http://intranet:80"
```

Dynamic config wijzig je wanneer een app, route, backend of middleware verandert.

---

<!-- _class: question -->

## Checkpoint - objecten volgen

Een request naar `helpdesk.bluepeak.test:8080` krijgt een upstreamfout.

Wat controleer je in volgorde?

1. frontendpoort en hostname;
2. router `helpdesk`;
3. rule `Host(...)`;
4. gekoppelde service;
5. server URL;
6. bereikbaarheid van de backendcontainer.

Waar zou je bewijs verwachten in het dashboard of de logs?

---

<!-- _class: divider -->

# 3. Poorten, backends en omwegen

## Het bedoelde pad werkt, het rechtstreekse pad niet

---

# Frontendpoort en backendpoort zijn twee verbindingen

```text
client -- frontendverbinding --> proxy -- backendverbinding --> applicatie
```

| Verbinding | Workshopadres | Wie moet dit kunnen bereiken? |
|---|---|---|
| client naar proxy | `localhost:8080` | de client op de labhost |
| proxy naar intranet | `intranet:80` | alleen containers op `appnet` |
| dashboard | `localhost:8088` | alleen student/beheerder in het lab |

`8080:80` betekent:

```text
hostpoort 8080 -> containerpoort 80 van Traefik
```

Het zegt niets over de poort van de backend.

---

<!-- _class: compact -->

# Waarom backends geen `ports:` krijgen

<div class="columns">
<div>

### Bedoeld

Backend zonder hostpoort:

```yaml
intranet:
  image: nginx:alpine
  networks:
    - appnet
```

Traefik bereikt de backend via het interne Docker-netwerk.

</div>
<div>

### Omweg

Met dit erbij ontstaat een omweg:

```yaml
ports:
  - "8081:80"
```

```text
bedoeld: client -> Traefik:8080 -> intranet:80
omweg:   client -> host:8081    -> intranet:80
```

</div>
</div>

> Via de omweg gelden proxylogging, middleware en latere authenticatie mogelijk niet.

---

# Positieve en negatieve poorttests

| Test | Verwacht | Wat bewijst dit? |
|---|---|---|
| juiste hostname via `8080` | app werkt | bedoelde proxypad is actief |
| `localhost:8081` | faalt | intranet is niet rechtstreeks gepubliceerd |
| `localhost:8082` | faalt | helpdesk is niet rechtstreeks gepubliceerd |
| `localhost:8083` | faalt | status is niet rechtstreeks gepubliceerd |

**Een mislukte negatieve test is een ontwerpbevinding.**

Als `localhost:8081` werkt, heb je niet "meer bereikbaarheid"; je hebt een bypass.

---

<!-- _class: question -->

## Enterprise design choice

BluePeak wil de helpdesk publiceren.

| Keuze | Gevolg |
|---|---|
| `Internet -> helpdesk:8080` | backend rechtstreeks bereikbaar |
| `Internet -> proxy:443 -> helpdesk:80` | centraal route-, log- en securitypunt |

Welke keuze is beter beheerbaar?

Welke firewallregel moet voorkomen dat de proxy bij compromis het hele interne netwerk bereikt?

---

<!-- _class: divider -->

# 4. TLS, certificaten en trust boundaries

## Versleuteling is een ontwerpkeuze per verbinding

---

# TLS termination

Bij TLS termination eindigt de client-TLS-verbinding op de reverse proxy.

```text
client -- HTTPS --> reverse proxy -- HTTP --> backend
```

Voordelen:

- centraal certificaatbeheer;
- centrale TLS-policy;
- de proxy kan HTTP-inhoud inspecteren voor routing, headers en logging;
- oudere backends kunnen achter een moderne frontend staan.

Risico:

**de backendverbinding is dan niet versleuteld.**

---

# Drie TLS-modellen

| Model | TLS eindigt op | Kan proxy HTTP-inhoud inspecteren? | Aandachtspunt |
|---|---|:---:|---|
| termination + HTTP-backend | proxy | ja | backendtraject is leesbaar |
| termination + HTTPS-backend | proxy en backend | ja | backendcertificaat valideren |
| passthrough | backend | nee | minder L7-functionaliteit op proxy |

Controleer bij certificaatfouten: DNS, SNI/hostname, SAN-namen, trust chain en geldigheid.

In de workshop gebruiken we bewust HTTP op localhost.

> Dat maakt routing zichtbaar, maar is geen productieontwerp.

---

# Forwarded headers bewaren clientcontext

De backend ziet de proxy vaak als directe netwerkpeer.

```text
client 203.0.113.25 -> proxy 10.20.0.10 -> backend 10.30.0.21

backend ziet TCP-peer: 10.20.0.10
X-Forwarded-For: 203.0.113.25
X-Forwarded-Proto: https
```

| Header | Mogelijke betekenis |
|---|---|
| `X-Forwarded-For` | oorspronkelijk clientadres |
| `X-Forwarded-Proto` | oorspronkelijk protocol |
| `X-Forwarded-Host` | oorspronkelijke hostname |
| `Forwarded` | gestandaardiseerde forwardinginfo |

---

# Forwarded headers zijn een vertrouwensgrens

Een client kan zelf een `X-Forwarded-For`-header meesturen.

| Foute aanname | Mogelijk gevolg |
|---|---|
| elke clientheader vertrouwen | bronadres of protocolcontext kan vervalst zijn |
| backend rechtstreeks bereikbaar laten | client omzeilt proxy en levert eigen headers |
| `X-Forwarded-Proto` negeren | verkeerde redirects of onveilige cookies |
| proxyketen niet documenteren | onduidelijk welk adres betrouwbaar is |

**De backend mag forwarded headers alleen vertrouwen vanaf gekende proxies.**

---

<!-- _class: divider -->

# 5. Plaatsing en security controls

## De proxy is een toegangspunt, geen vrijbrief

---

# Reverse proxy in een publicatiezone

```text
Internet
   |
edge firewall
   |
DMZ / publicatiezone
   |  reverse proxy
   |
interne firewall
   |
applicatiezone
```

De DMZ verhindert niet vanzelf alle risico's.

De toegelaten flows bepalen of segmentatie effectief begrenst:

- internet mag naar de proxy;
- internet mag niet rechtstreeks naar backends;
- proxy mag alleen naar noodzakelijke backendpoorten;
- beheer loopt via een apart gecontroleerd pad.

---

# Least connectivity voor proxyverkeer

| Bron | Bestemming | Poort | Actie | Reden |
|---|---|---:|:---:|---|
| internet | reverse proxy | 443 | allow | publieke HTTPS-toegang |
| internet | backendzone | any | deny | rechtstreekse backendtoegang blokkeren |
| reverse proxy | intranetbackend | 80/443 | allow | noodzakelijke appflow |
| reverse proxy | helpdeskbackend | 80/443 | allow | noodzakelijke appflow |
| reverse proxy | beheerzone | any | deny | proxycompromis mag beheer niet openen |
| beheernetwerk | proxybeheer | specifiek | allow | gecontroleerd beheerpad |

Regel `proxy -> intern netwerk -> any` maakt de proxy te krachtig.

---

# Backends afschermen vraagt defense in depth

<div class="vertical">
  <div class="node"><strong>Naamgeving:</strong> duidelijke hostnames en geen valse aannames over DNS</div>
  <div class="node"><strong>Netwerk:</strong> backendzone en expliciete firewallflows</div>
  <div class="node"><strong>Proxy:</strong> routes, TLS, headers en logging centraal</div>
  <div class="node"><strong>Applicatie:</strong> authenticatie, autorisatie en patching blijven nodig</div>
  <div class="node"><strong>Bewijs:</strong> positieve en negatieve tests per route</div>
</div>

Een kwetsbare applicatie blijft kwetsbaar wanneer haar normale route via een proxy loopt.

---

# Security headers beperken browserrisico's

| Header | Doel | Nuance |
|---|---|---|
| `X-Content-Type-Options` | content sniffing beperken | juiste `Content-Type` blijft nodig |
| `X-Frame-Options` | framing/clickjacking beperken | kan legitieme embedding blokkeren |
| `Referrer-Policy` | referrerinformatie beperken | kies beleid per applicatie |
| `Strict-Transport-Security` | browser dwingt HTTPS af | alleen bij blijvend correcte HTTPS |
| `Content-Security-Policy` | bronnen voor scripts/styles beperken | vraagt app-specifieke test |

Headers zijn aanvullende maatregelen.

Ze vervangen geen TLS, login, autorisatie, patching of invoervalidatie.

---

# Middleware bestaat pas wanneer ze gekoppeld is

```yaml
middlewares:
  security-headers:
    headers:
      contentTypeNosniff: true
      frameDeny: true
      referrerPolicy: "strict-origin-when-cross-origin"
```

Koppel de middleware aan de router:

```yaml
middlewares:
  - security-headers
```

Test per hostname:

```text
curl.exe -I http://intranet.bluepeak.test:8080
```

Zoek niet alleen of de middleware bestaat, maar of ze de response echt beinvloedt.

---

# Load balancing verdeelt een logische service

```text
                    +--> intranet-1:80
client -> proxy ----+--> intranet-2:80
                    +--> intranet-3:80
```

| Onderdeel | Functie |
|---|---|
| backendpool | instanties die dezelfde app leveren |
| verdeelalgoritme | kiest een gezonde instantie |
| health check | bepaalt of een backend verkeer mag krijgen |
| timeout | voorkomt eindeloos wachten op een backend |
| retry | kan helpen, maar is riskant bij niet-idempotente acties |
| session affinity | houdt client eventueel bij dezelfde backend |

Daarom heet het Traefik-onderdeel `loadBalancer`, ook bij een server URL.

---

# Health checks en proxybeschikbaarheid

Een health check is meer dan een open poort.

| Check | Bewijst vooral | Bewijst niet |
|---|---|---|
| TCP-connectie | proces luistert op een poort | applicatieflow werkt |
| HTTP `200` op `/health` | webservice antwoordt op dat endpoint | volledige gebruikersflow werkt |
| readinesscheck | instantie is klaar voor requests | elk businessproces is correct |

Een zinvolle check test een endpoint dat iets zegt over applicatie-readiness.

De reverse proxy zelf is ook een failure domain:

- een enkele proxyinstance kan een single point of failure zijn;
- meerdere proxies vragen gedeelde configuratie, certificaten en monitoring;
- capaciteit moet de som van appverkeer aankunnen.

---

<!-- _class: divider -->

# 6. Logging en troubleshooting

## Bewijs tot waar het request geraakt

---

# Logs vertellen verschillende delen van het verhaal

| Logtype | Mogelijke inhoud | Gebruik |
|---|---|---|
| access log | hostname, pad, methode, statuscode, duur | requests en responspatronen onderzoeken |
| proxy-/systeemlog | geladen configuratie, routerfouten, backendconnecties | werking van Traefik zelf onderzoeken |
| backendlog | applicatiefout, intern pad, verwerking | bepalen wat na forwarding gebeurde |

Let op met gevoelige data:

<span class="tag">Authorization-header</span>
<span class="tag">sessiecookie</span>
<span class="tag">querytokens</span>
<span class="tag">requestbody</span>

Troubleshootingwaarde moet in evenwicht blijven met privacy en logtoegang.

---

# Statuscodes zijn aanwijzingen, geen diagnoses

| Code | Mogelijke betekenis | Eerste controlevraag |
|---:|---|---|
| 200 | request succesvol | kwam de verwachte inhoud terug? |
| 301/302 | redirect | klopt locatie en protocol? |
| 401 | authenticatie nodig of mislukt | proxy of backend? |
| 403 | request niet toegestaan | welke policy weigerde? |
| 404 | route of pad niet gevonden | matchte een router? |
| 429 | rate limit bereikt | welke limiet telde mee? |
| 502 | upstreamrespons faalt | backendnaam, poort en protocol correct? |
| 503 | service niet beschikbaar | gezonde instanties aanwezig? |
| 504 | upstream timeout | backend traag of onbereikbaar? |

Dezelfde code kan door proxy of backend gegenereerd zijn.

---

# Methodisch troubleshooten volgt de keten

<div class="vertical">
  <div class="node"><strong>1. Naam:</strong> resolveert hostname naar de proxy?</div>
  <div class="node"><strong>2. Frontend:</strong> is de proxypoort bereikbaar?</div>
  <div class="node"><strong>3. Request:</strong> bevat het de juiste hostname?</div>
  <div class="node"><strong>4. Router:</strong> is de rule geladen en matcht ze?</div>
  <div class="node"><strong>5. Middleware:</strong> verandert ze headers, redirects of policy?</div>
  <div class="node"><strong>6. Service:</strong> wijst die naar de juiste backend?</div>
  <div class="node"><strong>7. Backend:</strong> kloppen naam, poort, protocol en antwoord?</div>
</div>

> Troubleshooting is aantonen tot waar het request geraakt, niet instellingen proberen tot het toevallig werkt.

---

# Voorbeeld: verkeerde backendpoort

De helpdeskservice wordt tijdelijk:

```yaml
url: "http://helpdesk:8088"
```

Redenering:

1. hostname wijst nog altijd naar Traefik;
2. client bereikt de frontendpoort;
3. helpdeskrouter matcht;
4. alleen proxy-naar-backend is fout;
5. andere routes kunnen normaal blijven werken.

**Wijzig een variabele per test.**

---

<!-- _class: question -->

## Troubleshootingcase

**Symptoom:** `helpdesk.bluepeak.test:8080` geeft 502.  
**Bekend:** intranet en status werken wel.

Orden de controles:

- hosts file of DNS;
- routerrule voor helpdesk;
- serviceverwijzing in `dynamic.yml`;
- server URL `http://helpdesk:80`;
- containernaam en intern netwerk;
- logs van Traefik.

Welke hypothese is nu het meest waarschijnlijk?

---

# Testplan: meer dan pagina opent

| Testsoort | Vraag | Voorbeeld |
|---|---|---|
| positief | werkt het bedoelde pad? | intranet via hostname geeft 200 en juiste inhoud |
| negatief | is een omweg geblokkeerd? | directe backendhostpoort faalt |
| scheiding | komt elk request bij de juiste app? | helpdesk toont geen intranetinhoud |
| foutinjectie | herkennen we een gecontroleerde fout? | verkeerde backendpoort geeft upstreamfout |

Een screenshot van een pagina bewijst niet dat de backend afgeschermd is.

Daarvoor heb je een afzonderlijke negatieve test nodig.

---

# Workshoptestmatrix

| Test | Verwacht | Zinvol bewijs |
|---|---|---|
| `intranet.bluepeak.test:8080` | intranet 200 | response + access log |
| `helpdesk.bluepeak.test:8080` | helpdesk 200 | inhoud + dashboardrouter |
| `status.bluepeak.test:8080` | status 200 | inhoud + access log |
| onbekende hostname | geen interne app | status en response |
| `localhost:8081` | faalt | geen directe intranetpoort |
| headers per hostname | drie headers | `curl.exe -I` |
| verkeerde helpdeskpoort | upstreamfout | logregel + analyse |
| herstel naar poort 80 | werkt opnieuw | nieuwe response |

---

# Reverse proxy is niet hetzelfde als andere lagen

| Component | Centrale vraag | Levert niet automatisch |
|---|---|---|
| firewall | welke netwerkflow mag passeren? | applicatieve routing |
| NAT/PAT | welk adres of poortnummer wordt vertaald? | authenticatie |
| reverse proxy | welke webapp krijgt dit request? | algemene netwerktoegang |
| VPN | welk beveiligd netwerkpad krijgt de client? | publicatie per hostname |
| identity provider | wie is de gebruiker? | netwerksegmentatie |
| applicatie | wat mag de gebruiker binnen de app? | perimeterbeheer |

**Firewall beperkt flows, reverse proxy routeert webrequests, identity bepaalt wie toegang krijgt.**

---

# Brug naar centrale identiteit

Een route zegt nog niet wie de gebruiker is.

```text
request bereikt proxy
        |
        v
welke applicatieroute?
        |
        v
wie is de gebruiker?
        |
        v
mag die identiteit deze route gebruiken?
        |
        v
request naar backend
```

In hoofdstuk 9 komt centrale identiteit aan bod. In hoofdstuk 10 worden reverse proxy en identity samengebracht.

---

# Van lab naar productie

| Thema | Labkeuze | Productievereiste |
|---|---|---|
| naamresolutie | hosts file | beheerde DNS |
| frontendprotocol | HTTP op localhost | HTTPS met geldig certificaat |
| proxybeschikbaarheid | een Traefik-container | redundantie en monitoring |
| dashboard | `api.insecure=true` | beschermd beheerpad |
| backendnetwerk | gedeeld Docker-netwerk | segmentatie en firewallregels |
| backend-TLS | HTTP | risico beoordelen |
| configuratie | lokaal bestand | versiebeheer, review, rollback |
| toegang | nog geen gebruikersauth | identity, MFA en autorisatie |

De workshop toont principes, geen volledig productieontwerp.

---

# Van theorie naar praktijk

In de workshop bouw je een reverse-proxyomgeving voor **BluePeak Services**.

Je zal:

- Traefik starten met static config;
- drie backendcontainers toevoegen zonder hostpoort;
- host-based routers en services schrijven in `dynamic.yml`;
- security headers via middleware koppelen;
- dashboard en logs gebruiken als bewijs;
- positieve en negatieve tests uitvoeren;
- een foutscenario analyseren;
- een productiegericht firewallvoorstel formuleren.

> Doel: de requestketen bewust opbouwen en bewijzen.

---

<!-- _class: question -->

## Voorbereidende case

BluePeak heeft:

- `intranet.bluepeak.test`, `helpdesk.bluepeak.test` en `status.bluepeak.test`;
- een Traefik-proxy op `localhost:8080`;
- drie nginx-backends op een intern Docker-netwerk;
- security headers die centraal moeten worden toegevoegd.

**Welke drie tests voer je eerst uit om te bewijzen dat het ontwerp geen backendbypass bevat?**

Welke conclusie mag je nog niet trekken uit alleen HTTP 200?

---

# Wat moet je onthouden?

1. Een reverse proxy publiceert webapplicaties via een centraal en controleerbaar requestpad.
2. DNS brengt de client naar de proxy; de `Host`-header helpt de proxy de app kiezen.
3. Traefik routeert via entrypoints, routers, rules, middleware en services naar backends.
4. Frontendpoorten en backendpoorten zijn verschillende verbindingen; backends krijgen geen omweg rond de proxy.
5. Security vraagt segmentatie, firewallregels, TLS-keuzes, forwarded-headervertrouwen, logs en positieve en negatieve tests.
