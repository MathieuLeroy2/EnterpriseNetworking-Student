---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks - Hoofdstuk 10
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
  .small { font-size: 0.72em; }
  .tiny { font-size: 0.61em; }
  .muted { color: var(--muted); }
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
  .tag {
    display: inline-block;
    background: var(--sky);
    color: var(--blue);
    padding: 0.16em 0.5em;
    margin: 0.1em 0.12em;
    font-size: 0.72em;
    font-weight: 700;
  }
  .flow {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
    align-items: center;
    gap: 10px;
    margin-top: 0.75em;
    margin-bottom: 1.05em;
  }
  .flow .box {
    background: var(--paper);
    border-bottom: 5px solid var(--cyan);
    min-height: 76px;
    padding: 11px 9px;
    text-align: center;
    font-size: 0.67em;
    color: var(--ink);
  }
  .flow .box strong { color: var(--blue); }
  .flow .arrow {
    color: var(--cyan);
    font-size: 1.2em;
    font-weight: 700;
  }
  .flow + table { margin-top: 0.55em; }
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: "" -->

# Enterprise Networks

## Hoofdstuk 10 - Identity-aware access met Traefik en Authentik

**Van een bereikbare webapp naar aantoonbaar gecontroleerde gebruikerstoegang**

---

# BluePeak publiceert meer dan een website

In hoofdstuk 8 publiceerden we webapps via **Traefik**.

In hoofdstuk 9 voegden we centrale identiteit toe met **Authentik**.

Nu komt de enterprisevraag:

> Hoe laat je een bestaande webapp alleen door wanneer de juiste gebruiker, groep en context bevestigd zijn?

<span class="tag">legacy apps</span>
<span class="tag">dashboards</span>
<span class="tag">beheerinterfaces</span>
<span class="tag">partners</span>
<span class="tag">MFA</span>
<span class="tag">audit</span>

---

<!-- _class: question -->

## Startvraag

# Een gebruiker kan de applicatie bereiken.

# Mag die gebruiker de applicatie ook openen?

Bespreek kort: **welke component kan dat beslissen, en welk bewijs heb je nodig?**

---

# Leerdoelen

Na deze les kan je:

1. netwerktoegang, authenticatie en autorisatie van elkaar onderscheiden;
2. de rollen van Traefik, Authentik core, application, proxy provider en outpost verklaren;
3. forward auth stap voor stap uitleggen en troubleshooten;
4. publieke, beschermde en gevoelige applicatieroutes ontwerpen;
5. groepsbindings, step-up MFA en identity-headers verantwoord testen;
6. fail-closedgedrag, logging, sessies en productiehardening analyseren.

---

# De basisvraag verandert

| Hoofdstuk | Centrale vraag | Belangrijk bewijs |
|---|---|---|
| Ch8 - reverse proxy | Welke hostname gaat naar welke backend? | router, middleware, service, accesslog |
| Ch9 - centrale identiteit | Wie is de gebruiker en welke claims horen erbij? | login, groep, flow, event |
| Ch10 - identity-aware access | Mag deze identiteit deze webapp openen? | allow-, deny- en bypass-tests |

**Kernidee:** bereikbaarheid, identiteit en autorisatie zijn drie verschillende voorwaarden.

---

# Een IP-adres is geen menselijke identiteit

| Situatie | Probleem |
|---|---|
| NAT | meerdere gebruikers delen hetzelfde publieke adres |
| VPN-pool | verschillende gebruikers zitten in hetzelfde subnet |
| gedeeld toestel | dezelfde endpoint kan meerdere personen dienen |
| proxy | backend ziet vooral het proxyadres |
| dynamische adressen | IP-adres is geen stabiele persoonskoppeling |
| gecompromitteerd toestel | toegelaten endpoint kan misbruikt worden |

Een bron-IP blijft nuttige **context**, maar geen volledig bewijs van **wie**.

---

# Drie opeenvolgende vragen

<div class="pipeline">
  <div class="node"><strong>1. Bereikbaarheid</strong><br>kan de client Traefik bereiken?</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>2. Authenticatie</strong><br>wie is dit en hoe bewezen?</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>3. Autorisatie</strong><br>mag deze gebruiker deze app openen?</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Backend</strong><br>alleen na allow</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Audit</strong><br>kan je dit achteraf verklaren?</div>
</div>

```text
Alice bereikt Traefik.                     -> netwerkpad werkt
Alice meldt correct aan bij Authentik.     -> authenticatie slaagt
Alice zit niet in bp-it.                   -> monitoring wordt geweigerd
```

---

# Wat voegt identity-aware access toe?

<div class="columns">
<div>

### Extra beslissingen

- account actief;
- groepslidmaatschap;
- applicatiecontext;
- MFA-context;
- sessiestatus;
- auditcontext.

</div>
<div>

### Niet opgelost

- kwetsbare backendsoftware;
- rechten binnen de app;
- SSH, RDP of databaseverkeer;
- malware op endpoint;
- netwerksegmentatie;
- transportbeveiliging.

</div>
</div>

**Identity-aware access is een toegangslaag, geen volledige securitystrategie.**

---

<!-- _class: question -->

## Denkvraag

Een medewerker zit op het VPN en opent `monitoring.bluepeak.test`.

- Traefik is bereikbaar.
- Authentik-login lukt.
- De monitoringpagina verschijnt niet.

**Welke van de drie vragen is waarschijnlijk nog niet positief beantwoord?**

---

<!-- _class: divider -->

# De architectuur

## Provider, outpost en Traefik zijn niet hetzelfde ding

---

# Drie "proxy"-begrippen, drie rollen

```text
Proxy provider = configuratie en regels
Proxy outpost  = uitvoerende Authentik-component
Traefik        = reverse proxy voor normaal applicatieverkeer
```

| Component | Mentale vraag |
|---|---|
| Application | welke logische app is dit en wie mag ze gebruiken? |
| Proxy provider | volgens welk proxypatroon en welke flows beschermen we ze? |
| Proxy outpost | welke runtimecomponent voert de authchecks uit? |
| Traefik | welke request matcht, wordt gecontroleerd en gaat naar welke backend? |

---

# Configuratieobject versus runtimecomponent

| Type | Voorbeeld | Betekenis |
|---|---|---|
| Configuratieobject | application, proxy provider | informatie opgeslagen en beheerd in Authentik |
| Runtimecomponent | Authentik core, outpost, Traefik | actief proces dat netwerkrequests verwerkt |

| Component | Dient voor | Doet niet |
|---|---|---|
| Traefik-router | hostname en pad matchen | gebruiker valideren |
| forward-authmiddleware | authcheck naar outpost sturen | gebruikers beheren |
| Authentik core | identities, groepen, flows, events | normale appinhoud proxyen |
| proxy outpost | providerchecks uitvoeren | backend-URL bepalen |
| backend | applicatie-inhoud leveren | clientheaders blind vertrouwen |

---

# De provider bevat policycontext

Voor monitoring:

```text
Application:        BluePeak Monitoring
Proxy provider:     BluePeak Monitoring Proxy
Mode:               Forward auth (single application)
External host:      http://monitoring.bluepeak.test:8100
Authentication:     centrale authentication flow
Authorization:      standaard authorization flow
Applicationbinding: bp-it
```

De provider zegt **niet**:

```text
stuur toegelaten requests naar http://monitoring:8080
```

Die interne backend-URL staat in de **Traefik-serviceconfiguratie**.

---

# De outpost voert providercontroles uit

Een proxy outpost verwerkt:

- authchecks van Traefik;
- loginstart en callbacks;
- providerlogout;
- ping en technische outpostpaden;
- identityheaders bij een toegelaten request.

```text
Traefik -> outpost auth endpoint
          "Mag deze request naar monitoring door?"

Browser -> monitoring.bluepeak.test/outpost.goauthentik.io/...
           "Start of voltooi login, callback of logout."
```

---

# Dataflow en control flow

<div class="flow">
  <div class="box"><strong>Browser</strong><br>GET monitoring</div>
  <div class="arrow">-&gt;</div>
  <div class="box"><strong>Traefik</strong><br>router + middleware</div>
  <div class="arrow">-&gt;</div>
  <div class="box"><strong>Outpost</strong><br>authcheck + policy</div>
  <div class="arrow">-&gt;</div>
  <div class="box"><strong>Backend</strong><br>alleen na allow</div>
</div>

| Flow | Loopt naar | Doel |
|---|---|---|
| identity/control flow | outpost en Authentik | beslissen of data door mag |
| applicatiedata | Traefik naar backend | inhoud leveren na allow |

Wanneer Authentik **deny** geeft, hoort Traefik de normale request niet naar de backend te sturen.

---

# Vertrouwen en outpostplaatsing

| Relatie | Wat moet betrouwbaar zijn? |
|---|---|
| client -> Traefik | DNS, hostname en in productie TLS-certificaat |
| Traefik -> outpost | forward-auth-URL en requestcontext |
| outpost -> Authentik core | toegewezen providers, identities, flows en policies |
| Traefik -> backend | alleen toegelaten requests en betrouwbare headers |

| Outpostkeuze | Voordeel | Aandachtspunt |
|---|---|---|
| embedded | eenvoudig voor workshop | lifecycle, schaal en beschikbaarheid gekoppeld |
| afzonderlijk | eigen zone, lifecycle en schaalbaarheid | extra deployment, token en monitoring |

---

<!-- _class: question -->

## Checkpoint

Een student zegt:

> "De Authentik proxy provider is de reverse proxy voor monitoring."

Wat klopt hier niet?

Beantwoord met de rollen van:

- proxy provider;
- proxy outpost;
- Traefik-service;
- monitoringbackend.

---

<!-- _class: divider -->

# Forward auth

## De backend krijgt pas verkeer nadat de authlaag allow zegt

---

# Definitie

Bij **forward auth** blijft Traefik de reverse proxy voor het echte applicatieverkeer.

Voor een beschermde route doet Traefik eerst een aparte controle bij de outpost.

```text
outpost laat toe  -> Traefik stuurt request naar backend
outpost weigert   -> Traefik stuurt request niet naar backend
login ontbreekt   -> browser wordt naar authenticatie geleid
```

De backend ziet geen wachtwoord of TOTP-code. Die horen bij de identity provider.

---

# Requestflow zonder bestaande sessie

```text
Browser          Traefik          Outpost/Authentik          Backend
   | GET app        |                    |                      |
   |--------------->|                    |                      |
   |                | auth check         |                      |
   |                |------------------->|                      |
   |                | login nodig        |                      |
   |<---------------|<-------------------|                      |
   | redirect en login bij Authentik     |                      |
   |------------------------------------>|                      |
   | callback/cookie |                   |                      |
   |--------------->|                    |                      |
   |                | nieuwe auth check  |                      |
   |                |------------------->|                      |
   |                | allow + headers    |                      |
   |                |<-------------------|                      |
   |                | originele request + identityheaders        |
   |                |------------------------------------------->|
```

---

# Drie mogelijke uitkomsten

| Situatie | Beslissing | Zichtbaar gevolg | Bereikt backend? |
|---|---|---|:---:|
| geen geldige sessie | login starten | redirect naar Authentik | nog niet |
| geldige identiteit, verkeerde groep | deny | fout- of denyweergave | nee |
| geldige identiteit en juiste policy | allow | applicatiepagina | ja |

Een loginredirect bewijst alleen dat de authlaag actief is.

**Allow en deny samen bewijzen of de grens correct staat.**

---

# Wat configureert Traefik?

| Traefik-onderdeel | Vraag die het beantwoordt |
|---|---|
| router | welke hostname of welk pad matcht? |
| middleware | moet deze request eerst door forward auth? |
| service | naar welke interne backend gaat een toegelaten request? |
| outpostrouter | waar gaan login-, callback-, logout- en pingpaden heen? |

```text
Host(`public.bluepeak.test`)
  -> geen forward auth
  -> public backend

Host(`monitoring.bluepeak.test`)
  -> authentik-forward middleware
  -> alleen na allow naar monitoring backend
```

---

# Forward auth versus native OIDC

| Eigenschap | Native OIDC in de app | Forward auth voor de app |
|---|---|---|
| Wie implementeert identityprotocol? | applicatie | proxy/outpostlaag |
| Krijgt app tokens of claims? | ja | meestal identityheaders |
| Legacyapp zonder SSO? | niet zonder appwijziging | vaak wel |
| Fijne appautorisatie | app kan claims verwerken | app blijft verantwoordelijk |
| Vertrouwensgrens | tokenvalidatie in app | vertrouwde proxy + backendisolatie |

Native OIDC is sterker wanneer de app het goed ondersteunt.

Forward auth is nuttig voor bestaande webapps die je voor de backend wilt beschermen.

---

<!-- _class: question -->

## Wat kan hier misgaan?

Monitoring geeft anoniem status `200`.

Bekend:

- DNS wijst naar Traefik;
- de monitoringbackend draait;
- de Authentik-provider bestaat;
- Bob kan inloggen in Authentik.

**Welke configuratiekoppeling controleer je eerst?**

---

<!-- _class: divider -->

# Routes en policies

## Niet elke hostname hoort dezelfde toegang te krijgen

---

# BluePeak-classificatie

| Applicatie | Doelgroep | Gevoeligheid | Identitybeleid |
|---|---|---|---|
| Publieke status | iedereen | publiek | geen login |
| Intranet | medewerkers | intern | `bp-employees` |
| Monitoring | IT | vertrouwelijk | `bp-it` |
| Admin | IT-admins | kritisch | `bp-it-admins` + step-up MFA |
| Partnerportaal | externe partners | beperkt | `bp-partners` |

De publieke route is geen fout.

**Ze moet even bewust ontworpen en getest worden als protected routes.**

---

# Classificatie en routetests

Voor elke hostname:

1. Moet anonieme toegang kunnen?
2. Welke zakelijke groep heeft toegang nodig?
3. Is gewone SSO voldoende?
4. Is een recente extra factor nodig?
5. Welke negatieve test bewijst de grens?

| Test | Verwacht | Bewijst |
|---|---|---|
| anoniem naar public | allow | public is bewust bereikbaar |
| anoniem naar monitoring | loginredirect | forward auth is actief |
| medewerker naar monitoring | deny | login is niet automatisch IT-toegang |
| IT-gebruiker naar monitoring | allow | juiste groepspolicy werkt |

---

# Application, provider en outposttoewijzing

<div class="pipeline">
  <div class="node"><strong>Application</strong><br>naam, URL, bindings</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Proxy provider</strong><br>mode, external host, flows</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Outpost</strong><br>bedient toegewezen provider</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Traefik</strong><br>middleware vraagt beslissing</div>
  <div class="arrow">-&gt;</div>
  <div class="node"><strong>Backend</strong><br>alleen na allow</div>
</div>

Ontbreekt een schakel, dan kan de applicatie bestaan maar toch niet correct beschermd zijn.

---

# Authentication flow, authorization flow en symptomen

| Flow | Vraag | BluePeak-voorbeeld |
|---|---|---|
| Authentication flow | hoe bewijst de gebruiker zijn identiteit? | centrale login |
| Authorization flow | welke extra stap is nodig voor deze provider? | TOTP-step-up voor admin |

| Symptoom | Controleer eerst |
|---|---|
| onverwachte deny | application en binding |
| verkeerde redirect | provider external host en flows |
| provider niet gevonden | outposttoewijzing |
| 502/503 na allow | Traefik-service en backendpoort |
| geen login voor backend | middleware op router |

---

# Single-application versus domain-level

| Patroon | Past wanneer | Beperking |
|---|---|---|
| Single-application | doelgroep, MFA of auditcontext verschilt per app | meer objects en consistente naamgeving nodig |
| Domain-level | veel apps exact hetzelfde beleid delen | geen aparte binding of authorization flow per backend |

```text
single-app:
intranet   -> bp-employees
monitoring -> bp-it
admin      -> bp-it-admins + MFA

domain-level:
*.bluepeak.test -> gedeeld toegangsbeleid
```

De workshop gebruikt **single-application forward auth**.

---

# Het speciale outpostpad

Bij single-application forward auth moet elk beschermd applicatiedomein dit pad naar de outpost sturen:

```text
/outpost.goauthentik.io/
```

```text
Host(monitoring) + PathPrefix(/outpost.goauthentik.io/)
    -> outpostservice

Host(monitoring) + alle andere paden
    -> forward auth
    -> monitoringbackend na allow
```

De outpostrouter krijgt hogere prioriteit en mag zelf geen forward auth gebruiken.

---

# Ping bewijst de technische outpostroute

Voorbeeld:

```text
http://monitoring.bluepeak.test:8100/outpost.goauthentik.io/ping
```

Een typische `204` bewijst:

- naamresolutie naar Traefik werkt;
- Host-rule matcht;
- pad krijgt de outpostrouter;
- Traefik bereikt de outpostservice.

Het bewijst **niet** dat groepen, MFA, backend of authorization correct zijn.

---

<!-- _class: question -->

## Wat kan hier misgaan?

De outpostrouter heeft zelf ook forward auth.

Een browser probeert naar monitoring te gaan.

**Welk symptoom verwacht je?**

**Waarom is dit geen probleem met de monitoringbackend?**

---

<!-- _class: divider -->

# Groepen, MFA en headers

## Identitycontext moet precies genoeg zijn

---

# Groepsgebaseerde toegang

| Applicatie | Zakelijke doelgroep | Technische binding |
|---|---|---|
| Intranet | alle medewerkers | `bp-employees` |
| Monitoring | IT-team | `bp-it` |
| Admin | beperkt beheerteam | `bp-it-admins` |
| Partnerportaal | goedgekeurde externe partners | `bp-partners` |

| Gebruiker | Groepen | Intranet | Monitoring | Admin | Partner |
|---|---|:---:|:---:|:---:|:---:|
| Alice | `bp-employees` | allow | deny | deny | deny |
| Bob | `bp-employees`, `bp-it`, `bp-it-admins` | allow | allow | allow na MFA | deny |
| Eva | `bp-partners` | deny | deny | deny | allow |

---

# Binding en lifecycle

Een gevaarlijke denkfout:

> "Geen binding betekent automatisch gesloten."

Controleer:

- juiste groep aan juiste application gebonden;
- toegelaten lid krijgt toegang;
- aangemelde niet-lid krijgt deny;
- groepswijziging verandert toegang;
- beheerwijziging verschijnt in audit.

---

# Lifecycle-impact van groepswijzigingen

Lifecyclevoorbeeld:

```text
Bob verlaat adminteam.
verwijder: bp-it-admins
behoud:    bp-employees en bp-it
```

Verwacht gedrag:

- Bob behoudt toegang tot intranet;
- Bob behoudt toegang tot monitoring;
- Bob verliest admintoegang;
- Bob krijgt geen partnertoegang.

---

# Step-up MFA voor gevoelige applicaties

Step-up authentication betekent:

> Voor een gevoeligere applicatie of handeling voert de gebruiker een sterkere of recentere verificatie uit.

Voor Bob:

1. Bob opent intranet met gewone SSO.
2. Bob opent admin.
3. `bp-it-admins` maakt Bob kandidaat.
4. De adminprovider voert een strengere authorization flow uit.
5. Authentik vraagt en valideert TOTP.
6. Pas daarna volgt admintoegang.

---

# MFA-toestanden en keuzes

| Toestand | Betekenis | Bewijst admintoegang? |
|---|---|---|
| device geregistreerd | gebruiker heeft ooit TOTP enrolled | nee |
| MFA gevalideerd | code werd in een flow correct gecontroleerd | alleen als het de relevante flow is |
| recent gevalideerd | eerdere validatie binnen threshold | afhankelijk van beleid |

| Keuze zonder factor | Gedrag | Gebruik |
|---|---|---|
| Skip | ga verder zonder factor | ongeschikt bij verplichte MFA |
| Deny | stop toegang | duidelijk fail-closed |
| Configure | laat registreren | onboarding, mits recovery klopt |

---

# Sterke MFA-tests

| Test | Verwacht | Bewijst |
|---|---|---|
| Bob opent eerst intranet | allow | centrale SSO werkt |
| Bob opent daarna admin | TOTP-prompt | extra authorizationstap |
| Bob voert foute code in | geen toegang | factor wordt echt gevalideerd |
| Bob voert geldige code in | allow | groep en factor werken samen |
| Alice tijdelijk in admingroep zonder TOTP | deny | groep alleen is onvoldoende |

**MFA testen zonder negatieve test geeft schijnzekerheid.**

---

# Identity-headers en backendverantwoordelijkheid

| Header | Inhoud | Mogelijk gebruik |
|---|---|---|
| `X-authentik-username` | centrale gebruikersnaam | remote-usermapping |
| `X-authentik-groups` | groepen | beperkte rolmapping |
| `X-authentik-email` | e-mailadres | contact of matching |
| `X-authentik-uid` | stabiele identifier | lokaal profiel koppelen |
| `X-authentik-meta-app` | application slug | audit en context |

```text
forward auth: Bob mag de ticketapp openen
ticketapp:    Bob mag tickets bekijken
ticketapp:    alleen ticket-managers mogen wachtrijen verwijderen
```

Identity-headers vervangen geen fijnmazige appautorisatie.

---

# Header spoofing en vertrouwensgrens

Aanvalsidee:

```text
X-authentik-username: akadmin
```

Een identity-header is alleen betrouwbaar wanneer:

- clients de backend niet buiten Traefik bereiken;
- de proxy clientheaders verwijdert of overschrijft;
- forward auth de vertrouwde waarden levert;
- de backend alleen bekende proxybronnen vertrouwt;
- relevante netwerksegmenten in productie met TLS beschermd zijn.

---

# Twee noodzakelijke negatieve tests

#### Test 1: zelfgekozen header

```text
curl.exe -i -H "X-authentik-username: akadmin" http://admin.bluepeak.test:8100
```

Zonder geldige sessie mag dit geen adminbackend tonen.

#### Test 2: directe backendpoort

```text
curl.exe -I http://localhost:8101
```

Wanneer backends geen hostpoorten publiceren, hoort deze test te falen.

---

<!-- _class: question -->

## Checkpoint

Bob ziet in de backend:

```text
X-authentik-username: bob
X-authentik-groups: bp-employees,bp-it
```

**Welke drie dingen moet je nog aantonen voordat je deze headers betrouwbaar noemt?**

---

# SSO, logout en teststart

| Sessie | Beheerd door | Doel |
|---|---|---|
| centrale Authentik-sessie | Authentik core | gebruiker centraal aangemeld houden |
| proxyprovidersessie | outpost/provider | toegang voor die provider onthouden |
| applicatiesessie | backend | lokale appstatus of rechten |

Een testverslag vermeldt:

- nieuw private venster of bestaande browser;
- welke gebruiker centraal aangemeld is;
- welke provider al geopend werd;
- of MFA recent gevalideerd werd;
- welke logoutactie vooraf gebeurde.

Logout is geen enkelvoudige knop: providerlogout, centrale logout, browsersessies,
accountdeactivatie en sessie-intrekking kunnen elk een andere laag raken.

Providerlogout gebruikt:

```text
/outpost.goauthentik.io/sign_out
```

---

# Logging: correlatie en hygiene

| Bron | Ziet vooral | Sterk in |
|---|---|---|
| Traefik accesslog | host, pad, tijdstip, statuscode | requestpad |
| Authentik server/outpostlog | flow- en providerproblemen | authketen |
| Authentik events | actor, app, policy, MFA | audit |
| Backendlog | ontvangen headers en appactie | context na allow |

```text
10:14:03 Traefik: request voor monitoring.bluepeak.test
10:14:03 Authentik: Alice, application BluePeak Monitoring, policy deny
10:14:03 Backend: geen normale applicatierequest voor Alice
```

Log geen wachtwoorden, TOTP-codes, sessiecookies, volledige tokens of TOTP-seeds.

---

# Fail-closed

Wanneer Authentik of de outpost geen geldige beslissing kan geven, hoort een beschermde route geen backendtoegang te geven.

| Storing | Verwacht voor public | Verwacht voor protected |
|---|---|---|
| Authentik server down | kan blijven werken | nieuwe authbeslissing faalt gesloten |
| outpostroute fout | werkt | login/authcheck faalt |
| backend down | afhankelijk van backend | auth kan slagen, app geeft 502/503 |
| identitydatabase down | werkt | geen betrouwbare identitybeslissing |
| DNS voor authhost fout | kan werken | loginredirect kan niet voltooien |

**Geen geldige toegangsbeslissing betekent geen toegang tot de beschermde backend.**

Daarom wordt de IdP kritieke infrastructuur: denk aan HA, databaseherstel,
monitoring, capaciteit, betrouwbare tijd en gecontroleerde break-glass.

---

<!-- _class: divider -->

# Troubleshooting en productie

## Eerst lokaliseren, daarna pas wijzigen

---

# Typische fouten en lagen

| Fout | Gevolg | Herkenning |
|---|---|---|
| middleware ontbreekt | app opent zonder login | anoniem krijgt backendstatus `200` |
| outpostrouter ontbreekt | login start niet | pingpad geeft 404 |
| outpostrouter gebruikt forward auth | redirectloop | authpad authenticeert zichzelf |
| external host fout | callback- of cookieprobleem | redirect wijkt af van echte URL |
| binding ontbreekt | toegang te breed | partner opent interne app |
| adminflow zonder step-up | geen extra MFA | Bob opent admin met gewone SSO |
| backend heeft hostpoort | bypass | directe localhostpoort werkt |
| alleen positieve test | te brede policy verborgen | grenzen onbekend |

---

# Methodische controle per laag

| Laag | Centrale vraag | Typisch bewijs |
|---|---|---|
| 1. Naamresolutie | wijst hostname naar Traefik? | hosts file, resolve of gerichte curl |
| 2. Entry point en router | matcht Traefik de request? | dashboard of accesslog |
| 3. Outpostpad | bereikt authtechniek de outpost? | `204` op pingendpoint |
| 4. Application/provider | klopt technische koppeling? | external host, flow, outpostassignment |
| 5. Identity/policy | is account actief en binding juist? | allow- of deny-event |
| 6. Backend | kan Traefik de app bereiken? | `200` of 502/503-analyse |
| 7. Headervertrouwen | is er geen bypass? | spoofing- en direct-access-test |

---

# Twee troubleshootingvoorbeelden

<div class="columns">
<div>

### Alice krijgt 502

Controleer:

- komt de 502 voor of na auth?
- geeft Authentik allow of deny?
- wijst Traefik naar `monitoring:8080`?
- draait de backend?

</div>
<div>

### Eva kan intranet openen

Controleer:

- zit Eva in `bp-employees`?
- heeft de app een binding?
- ontbreekt middleware?
- hergebruik je Alice-sessie?
- is de backend direct geopend?

</div>
</div>

**Lokaliseer de laag voor je de configuratie wijzigt.**

---

# Is dit een vervanging voor VPN?

| Eigenschap | VPN | Identity-aware reverse proxy |
|---|---|---|
| Primair doel | beveiligd netwerkpad | gecontroleerde webappaccess |
| Scope | subnetten, hosts, meerdere protocollen | meestal HTTP/HTTPS per hostname |
| Beslissing per webapp | niet automatisch | expliciete applicationpolicy |
| Clientsoftware | vaak nodig | browser volstaat meestal |
| SSH/RDP/database | geschikt mits beleid | meestal niet |
| Backendafscherming | nog nodig | nog nodig |

Ze vullen elkaar vaak aan: VPN begrenst netwerkconnectiviteit, identity-aware access
begrenst webapplicatietoegang.

---

# VPN of identity-aware access?

| Requirement | Passende oplossing |
|---|---|
| partner gebruikt een webportaal | identity-aware proxy |
| beheerder SSH't naar switches | VPN naar managementzone en jump server |
| medewerker gebruikt intranet | identity-aware HTTPS kan passen |
| beheerder opent webadmin en beheert servers | identity-aware webtoegang plus VPN |

De keuze vertrekt van het vereiste toegangspad: **webapp**, **netwerkprotocol** of beide.

---

# Lab versus productiehardening

| Thema | Labkeuze | Productievereiste |
|---|---|---|
| Transport | HTTP op lokale hostnames | HTTPS met geldig certificaat |
| DNS | hosts file | beheerd DNS |
| Traefik-dashboard | lokaal onbeveiligd | afschermen of uitschakelen |
| Backends | intern Docker-netwerk | appzone en firewallregels |
| Authentik | enkele instance | HA en capaciteit |
| Database | een PostgreSQL-container | back-up, restore en eventueel redundantie |
| Secrets | lokaal `.env` | secret store, rotatie en toegangbeheer |
| Logging | containerlogs | centrale beveiligde logging |

Productie vraagt ook access reviews, joiner-mover-leaver, MFA-herstel, RTO/RPO en rollbacktests.

---

# Teststrategie

Een sterk testplan controleert:

| Type | Voorbeeld |
|---|---|
| functioneel | public werkt zonder login |
| protected baseline | anoniem naar intranet geeft loginredirect |
| positieve policy | Alice naar intranet, Bob naar monitoring |
| negatieve policy | Alice naar monitoring, Eva naar intranet |
| MFA | Bob naar admin vraagt en valideert TOTP |
| bypass | gespoofte header en directe backendpoort falen |
| storing | Authentik down laat protected fail-closed |
| sessies | providerlogout en centrale logout onderscheiden |

---

# Van theorie naar praktijk

In de workshop bouw en test je de BluePeak-keten.

Je zal:

- publieke en beschermde hostnames onderscheiden;
- Authentik applications, providers, bindings en outposttoewijzing koppelen;
- Traefik-routers, middleware, services en outpostroutes controleren;
- groepsgebaseerde toegang en step-up MFA testen;
- identity-headers en spoofingrisico onderzoeken;
- logs, sessies en fail-closed gedrag gebruiken als bewijs.

> Doel: aantonen dat routing, identiteit, policy en backendisolatie samen werken.

---

# Wat moet je onthouden?

1. Bereikbaarheid, authenticatie en autorisatie zijn drie verschillende voorwaarden.
2. Traefik bestuurt het webpad; Authentik bestuurt identity, flows en policies.
3. Forward auth beschermt de backend alleen wanneer middleware, outpostroute, provider en binding samen kloppen.
4. Identity-headers zijn pas betrouwbaar binnen een afgedwongen proxy- en backendvertrouwensgrens.
5. Een enterprise-testplan bewijst allow, deny, MFA, bypass, sessies, logging en fail-closed gedrag.
