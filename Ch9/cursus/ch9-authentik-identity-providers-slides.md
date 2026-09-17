---
marp: true
theme: default
paginate: true
size: 16:9
footer: Enterprise Networks - Hoofdstuk 9
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
    max-width: 790px;
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

## Hoofdstuk 9 - Authentik en identity providers

**Centrale identiteit, SSO en OIDC bewust ontwerpen en bewijzen**

---

# BluePeak krijgt te veel losse logins

BluePeak gebruikt steeds meer interne webapplicaties.

<span class="tag">intranet</span>
<span class="tag">helpdesk</span>
<span class="tag">monitoring</span>
<span class="tag">partnerportaal</span>

<div class="columns">
<div class="card">

### Vandaag

Elke applicatie heeft eigen accounts, rechten, sessies en logs.

</div>
<div class="card">

### Morgen

- centraal onboarden en offboarden;
- MFA voor gevoelige toegang;
- partners apart behandelen;
- login en toegang kunnen bewijzen.

</div>
</div>

> Niet: "kan de app login tonen?" Wel: "klopt het identity- en accessmodel?"

---

<!-- _class: question -->

## Startvraag

# Alice kan inloggen.

# Wat weet je nu nog niet?

Bespreek kort: welke vragen blijven open over **rechten**, **sessies**, **MFA**, **audit** en **offboarding**?

---

# Leerdoelen

Na deze les kan je:

1. authenticatie, autorisatie en centrale identiteit correct van elkaar onderscheiden;
2. lokale accounts vergelijken met een identity provider en SSO;
3. gebruikers, groepen, rollen, policies en lifecyclekeuzes analyseren;
4. LDAP, SAML, OAuth 2.0 en OIDC op hoofdlijnen vergelijken;
5. een OIDC authorization code flow, tokens, scopes en claims verklaren;
6. Authentik applications, providers, bindings, MFA en auditlogs controleren en troubleshooten.

---

# Lokale accounts lijken eenvoudig

```text
gebruiker -> account in intranet
gebruiker -> account in helpdesk
gebruiker -> account in monitoring
gebruiker -> account in documentatieplatform
```

Elke applicatie beslist zelf over:

- gebruikers aanmaken en verwijderen;
- wachtwoordopslag en resetproces;
- groepen en rechten;
- sessieduur;
- loginpogingen en auditinformatie.

**Klein netwerk:** overzichtelijk.  
**Enterprise-context:** verspreide waarheid.

---

# Verspreide identiteit wordt snel een securityprobleem

| Probleem | Praktisch gevolg |
|---|---|
| meerdere accounts per persoon | moeilijk bewijzen welke accounts bij dezelfde mens horen |
| verschillend wachtwoordbeleid | zwakste applicatie ondermijnt het model |
| wachtwoordhergebruik | lek in een app kan andere apps raken |
| offboarding per applicatie | vergeten account blijft bruikbaar |
| groepswijzigingen lopen achter | oude rechten blijven mogelijk actief |
| verspreide auditlogs | incidentonderzoek mist context |

> Het probleem is niet alleen extra werk, maar vooral dat toegang moeilijk aantoonbaar correct blijft.

---

# Centrale identiteit verplaatst de login

<div class="network-row">
  <div class="device"><strong>Gebruiker</strong><br>browser</div>
  <div class="arrow">-></div>
  <div class="device primary"><strong>Identity provider</strong><br>login, MFA, sessie</div>
  <div class="arrow">-></div>
  <div class="device"><strong>Applicaties</strong><br>intranet, helpdesk, monitoring</div>
</div>

Applicaties delegeren authenticatie aan de identity provider.

<div class="columns">
<div>

### Voordelen

- centrale accountlevenscyclus;
- centraal MFA-beleid;
- single sign-on;
- groepen en claims;
- centrale logs.

</div>
<div>

### Nieuwe afhankelijkheid

> De identity provider wordt kritieke infrastructuur.

</div>
</div>

---

# Centrale identiteit lost niet alles op

<div class="columns">
<div class="card">

### IdP centraliseert

- login;
- MFA;
- groepen;
- policies;
- sessies;
- audit.

</div>
<div class="card">

### Applicatie blijft nodig

- applicatielogica;
- eigen objecten;
- interne permissies;
- businessregels;
- lokale sessie.

</div>
</div>

**Kernidee:** de IdP bewijst identiteit en context; de applicatie beslist wat die gebruiker binnen de app kan doen.

---

# Authenticatie en autorisatie zijn twee vragen

| Begrip | Vraag | Voorbeeld |
|---|---|---|
| **Authenticatie** | wie ben je? | wachtwoord, passkey, certificaat, TOTP |
| **Autorisatie** | wat mag je doen? | portal openen, monitoring beheren, tickets zien |

```text
identiteit claimen
      |
      v
authenticatie: klopt die identiteit?
      |
      v
autorisatie: welke toegang hoort erbij?
```

> Authenticated is niet hetzelfde als authorized.

---

<!-- _class: question -->

## Wat kan hier misgaan?

Eva is partner bij BluePeak.

- Eva kan correct aanmelden bij Authentik.
- Eva is lid van `bp-partners`.
- De BluePeak Portal is bedoeld voor `bp-employees`.

Een beheerder zegt:

> "Eva's login werkt, dus de identity provider is correct geconfigureerd."

Welke test ontbreekt?

---

# Een IdP werkt via een vertrouwensrelatie

```text
+--------+     1. open app      +-------------+
| Browser| -------------------> | Applicatie  |
+--------+                      +-------------+
    |                                  |
    | 2. redirect naar IdP             |
    v                                  |
+-------------------+                  |
| Identity provider |                  |
+-------------------+                  |
    |                                  |
    | 3. loginresultaat                 |
    +--------------------------------->+
```

De applicatie ontvangt normaal **niet** het wachtwoord van de gebruiker.

Ze ontvangt een protocolresultaat dat ze moet controleren.

---

# Vertrouwen is technisch geconfigureerd

Bij OIDC vertrouwt een applicatie Authentik alleen als onder meer dit klopt:

| Controle | Waarom? |
|---|---|
| juiste issuer | token komt van de verwachte IdP |
| client ID | token is bedoeld voor deze client |
| redirect URI | callback is vooraf exact toegestaan |
| handtekening | token is niet zelfgemaakt of gewijzigd |
| geldigheid | token is niet verlopen |
| scopes en claims | app krijgt alleen bedoelde informatie |

**SSO is geen magie. Het is een expliciete afspraak tussen applicatie en identity provider.**

---

# SSO gebruikt minstens twee sessies

| Sessie | Beheerd door | Doel |
|---|---|---|
| **IdP-sessie** | identity provider | onthouden dat de gebruiker centraal aangemeld is |
| **applicatiesessie** | applicatie | gebruiker aangemeld houden in die app |

```text
Noor logt in bij Authentik.
Noor krijgt een IdP-sessie.
Noor opent het intranet.
Het intranet maakt een eigen applicatiesessie.
Noor sluit het intranet.
De Authentik-sessie kan nog bestaan.
```

**Test altijd welke sessie je beinvloedt.**

---

# Wanneer is SSO echt geslaagd?

SSO is correct ingericht wanneer drie dingen samen kloppen:

<div class="three">
  <div class="card"><strong>1. Login</strong><br>De gebruiker kan zich centraal aanmelden.</div>
  <div class="card"><strong>2. Vertrouwen</strong><br>De juiste apps accepteren de centrale login.</div>
  <div class="card"><strong>3. Begrenzing</strong><br>Onbevoegde gebruikers worden geweigerd.</div>
</div>

Alleen tonen dat Alice kan inloggen is onvoldoende.

Je moet ook tonen dat Eva, die niet in de juiste groep zit, geen toegang krijgt.

---

<!-- _class: divider -->

# Identitymodel

## Gebruikers, groepen, rollen, policies en lifecycle

---

# Een gebruiker is meer dan een username

Een gebruiker stelt een digitale identiteit voor.

<div class="columns">
<div>

### Voorbeelden

- `alice.vermeulen`;
- `bob.peeters`;
- externe partner;
- tijdelijk account.

</div>
<div>

### Attributen

<span class="tag">naam</span>
<span class="tag">e-mail</span>
<span class="tag">status</span>
<span class="tag">groepen</span>
<span class="tag">MFA-devices</span>
<span class="tag">sessies</span>

</div>
</div>

> Stelt dit account een mens, partner, beheerder of technische integratie voor?

---

# Groepen maken toegang beheerbaar

```text
application BluePeak Portal -> allow groep bp-employees
Alice in bp-employees -> toegang
Eva alleen in bp-partners -> geen toegang
```

| Groep | Betekenis |
|---|---|
| `bp-employees` | gewone medewerkers |
| `bp-it` | IT-medewerkers |
| `bp-finance` | finance |
| `bp-partners` | externe partners |

Groepen zijn nuttig omdat je toegang niet persoon per persoon beheert.

**Goede groepsnamen beschrijven waarom de groep bestaat.**

---

# Rol betekent niet overal hetzelfde

| Type | Voorbeeld | Waar gebruikt? |
|---|---|---|
| **IdP-groep** | `bp-it` | toegang tot apps en claims |
| **Authentik-rol** | beheerrechten binnen Authentik | administratie van Authentik zelf |
| **applicatierol** | `ticket-agent` | rechten binnen de doelapplicatie |

Belangrijke Authentik-nuance:

> Rollen in Authentik bundelen vooral beheerspermissies op Authentik-objecten.

Toegang tot een gekoppelde applicatie regel je meestal met **application bindings** op gebruikers, groepen of policies.

---

# Policies en bindings maken intentie technisch

Een policy beschrijft een voorwaarde.  
Een binding koppelt een gebruiker, groep of policy aan een object.

```text
application: BluePeak Portal
binding: groep bp-employees
resultaat: alleen leden van bp-employees krijgen toegang
```

Enterprise-denken:

- vertrek van zakelijke behoefte;
- vertaal die naar groep of policy;
- test allow en deny;
- documenteer default gedrag.

> Een binding is de plaats waar een ontwerpbeslissing technisch wordt toegepast.

---

<!-- _class: question -->

## Enterprise design choice

BluePeak wil het medewerkersportaal beperken.

| Keuze | Gevolg |
|---|---|
| Alice, Bob en Carol apart binden | snel voor drie users, slecht bij groei |
| groep `bp-employees` binden | functie volgt groepslidmaatschap |
| iedereen die kan aanmelden toelaten | makkelijk, maar geen least privilege |

Welke keuze is beheerbaar bij joiners, movers en leavers?

Welke negatieve test bewijst de grens?

---

# Identity lifecycle: joiner, mover, leaver

<div class="flow">
  <div class="node"><strong>Joiner</strong><br>account, groep, MFA, eigenaar</div>
  <div class="arrow">-></div>
  <div class="node"><strong>Mover</strong><br>oude rechten weg, nieuwe erbij</div>
  <div class="arrow">-></div>
  <div class="node"><strong>Leaver</strong><br>deactiveren, sessies en tokens intrekken</div>
  <div class="arrow">-></div>
  <div class="node"><strong>Audit</strong><br>bewijs wie wat wanneer deed</div>
</div>

Lifecyclebeheer voorkomt dat identity-informatie achterloopt op de werkelijkheid.

**Mover-risico:** nieuwe rechten worden toegevoegd, maar oude rechten blijven soms hangen.

---

# Offboarding vraagt meer dan account uitzetten

Bij een leaver wil je vooral voorkomen dat bestaande toegang blijft werken.

Controleer:

- kan de gebruiker nog aanmelden?
- bestaan er nog actieve IdP-sessies?
- bestaan er nog applicatiesessies?
- bestaan er nog tokens of app-specifieke wachtwoorden?
- is de gebruiker nog eigenaar van applicaties, secrets of groepen?
- verschijnt de wijziging in auditlogs?

> Alleen een wachtwoord wijzigen is geen volledige offboarding.

---

# MFA beperkt de impact van een gestolen wachtwoord

| Factorcategorie | Voorbeeld |
|---|---|
| iets wat je weet | wachtwoord of pincode |
| iets wat je hebt | authenticator, hardwaretoken, geregistreerd toestel |
| iets wat je bent | biometrisch kenmerk |

Een wachtwoord en een tweede wachtwoord zijn geen sterke twee factoren.

MFA is geen volledige oplossing:

- phishing blijft mogelijk;
- herstelproces kan een zwakke plek worden;
- sessies na login blijven belangrijk;
- beheerdersaccounts vragen extra bescherming.

---

# TOTP maakt MFA zichtbaar in het lab

```text
Authentik toont enrollment QR-code.
Authenticator bewaart gedeeld geheim.
Elke 30 seconden verschijnt een nieuwe code.
Authentik controleert de code binnen het tijdsvenster.
```

| Sterkte | Aandachtspunt |
|---|---|
| breed ondersteund | phishing blijft mogelijk |
| offline bruikbaar | enrollmentgeheim beschermen |
| didactisch zichtbaar | herstelcodes veilig bewaren |
| makkelijk te testen | tijdsafwijking geeft fouten |

In productie kunnen phishing-resistente factoren beter passen voor beheerders en kritieke toegang.

---

<!-- _class: question -->

## Wat bewijst een MFA-test?

Bob registreert TOTP.

Daarna opent hij de portal vanuit een browser waarin hij nog een actieve Authentik-sessie heeft.

Er verschijnt geen nieuwe TOTP-prompt.

Mogelijke verklaringen?

- MFA is niet afgedwongen in de effectieve flow.
- De bestaande IdP-sessie wordt hergebruikt.
- Het device is geregistreerd maar de policy vraagt het niet.
- De test startte niet vanuit een schone logincontext.

Welke test doe je opnieuw?

---

<!-- _class: divider -->

# Protocollen en OIDC

## Van directory lookup naar moderne loginflows

---

# Vier protocollen, vier andere vragen

| Protocol | Typisch doel | Belangrijke nuance |
|---|---|---|
| **LDAP** | gebruikers, groepen en attributen opvragen | geen modern browser-SSO-protocol |
| **SAML 2.0** | browser-SSO naar enterprise- of SaaS-app | XML, metadata en certificaten |
| **OAuth 2.0** | gedelegeerde toegang tot een API | op zichzelf geen loginprotocol |
| **OpenID Connect** | gebruiker aanmelden via een IdP | identity-laag bovenop OAuth 2.0 |

```text
LDAP  -> wie bestaat er in de directory?
SAML  -> meld deze browsergebruiker aan.
OAuth -> mag deze client een API gebruiken?
OIDC  -> wie is deze aangemelde gebruiker?
```

---

# LDAP is directorytoegang

Typische LDAP-vragen:

- bestaat gebruiker `alice`?
- zit `alice` in groep `bp-it`?
- welke attributen horen bij deze gebruiker?
- zijn deze credentials geldig via een bind?

```text
applicatie -> LDAP-server: bestaat gebruiker alice?
applicatie -> LDAP-server: zit alice in groep bp-it?
applicatie -> LDAP-server: klopt het wachtwoord van alice?
```

LDAP is nuttig voor oudere applicaties, netwerkdiensten en directoryinformatie.

**Het levert niet vanzelf een moderne SSO-flow met redirects, MFA en tokens.**

---

# SAML is federated browser-SSO

```text
browser -> service provider: open applicatie
service provider -> browser: ga naar identity provider
browser -> identity provider: login
identity provider -> browser: SAML assertion
browser -> service provider: lever assertion af
service provider: controleert handtekening, issuer, audience en geldigheid
```

| Begrip | Betekenis |
|---|---|
| identity provider | authenticeert de gebruiker |
| service provider | applicatie die de IdP vertrouwt |
| assertion | ondertekend XML-bericht met identity-informatie |
| metadata | endpoints en certificaten voor IdP en SP |

SAML komt vaak voor bij enterprise- en SaaS-applicaties.

---

# OAuth 2.0 is geen loginprotocol

OAuth 2.0 gaat primair over gedelegeerde toegang.

> Mag deze client beperkte toegang krijgen tot een resource?

```text
gebruiker -> applicatie: ik wil mijn agenda koppelen
applicatie -> authorization server: vraag toestemming
gebruiker -> authorization server: geeft toestemming
applicatie -> API: gebruikt access token
```

Het resultaat is meestal een **access token** voor een API.

Dat token is niet automatisch een betrouwbaar bewijs dat een gebruiker correct is aangemeld bij een webapplicatie.

---

# OIDC voegt identiteit toe aan OAuth 2.0

OpenID Connect voegt afspraken toe waarmee een applicatie betrouwbaar weet wie de gebruiker is.

Belangrijk extra resultaat:

> het **ID token** met identity-claims over de aangemelde gebruiker.

Typische OIDC-vraag:

> Deze browsergebruiker heeft ingelogd bij de identity provider. Welke identiteit hoort daarbij en mag mijn applicatie die login vertrouwen?

Kernzin:

**OAuth 2.0 gaat primair over toegang; OIDC voegt informatie over de aangemelde identiteit toe.**

---

# OIDC heeft vaste bouwstenen

| Onderdeel | Functie |
|---|---|
| issuer | unieke URL van de IdP die tokens uitgeeft |
| client ID | publieke identifier van de applicatie |
| client secret | geheim voor server-side tokenuitwisseling |
| redirect URI | exact toegelaten terugkeeradres |
| authorization endpoint | startpunt voor login en consent |
| token endpoint | code inwisselen voor tokens |
| ID token | identity-informatie voor de applicatie |
| UserInfo-endpoint | extra claims, indien toegestaan |

**Elke fout hoort bij een fase of bouwsteen.**

---

# Authorization code flow

<div class="vertical">
  <div class="node"><strong>1. Browser opent app</strong> - de OIDC-client start de loginflow.</div>
  <div class="node"><strong>2. Redirect naar Authentik</strong> - browser gaat naar het authorization endpoint.</div>
  <div class="node"><strong>3. Login, MFA en policy</strong> - Authentik controleert identiteit en toegang.</div>
  <div class="node"><strong>4. Callback met code</strong> - browser keert terug met een korte authorization code.</div>
  <div class="node"><strong>5. Token exchange</strong> - de client wisselt de code server-to-server in.</div>
  <div class="node"><strong>6. App-sessie</strong> - de applicatie houdt de gebruiker lokaal aangemeld.</div>
</div>

De applicatie ziet het gebruikerswachtwoord niet.

---

# Waarom eerst een authorization code?

| Onderdeel | Gaat via browser? | Doel |
|---|:---:|---|
| authorization code | ja | kort bewijs dat loginflow geslaagd is |
| token request | nee | code server-to-server inwisselen |
| ID token | naar de client | identity-informatie |
| app-sessie | lokaal in de app | gebruiker aangemeld houden |

De authorization code:

- is kort geldig;
- is bedoeld voor eenmalig gebruik;
- wordt via de browser teruggestuurd;
- wordt door de client ingewisseld bij het token endpoint.

---

# De client moet het resultaat controleren

| Controle | Beschermt tegen |
|---|---|
| `state` klopt | verwisselde of vervalste browserflows |
| redirect URI exact toegestaan | code naar verkeerde bestemming |
| issuer komt overeen | tokens van andere of valse IdP |
| tokenhandtekening geldig | zelfgemaakte of gewijzigde tokens |
| audience correct | token bedoeld voor andere client |
| tijdsclaims geldig | verlopen of nog niet geldige tokens |
| `nonce` hoort bij login | hergebruik uit andere loginpoging |

Een didactische labclient maakt de stappen zichtbaar, maar vervangt geen productie-implementatie van volledige tokenvalidatie.

---

# Redirect URI is een veiligheidsgrens

In het lab:

```text
http://localhost:8089/callback
```

| Redirect URI | Beoordeling |
|---|---|
| `https://portal.example.com/callback` | exact en HTTPS |
| `http://localhost:8089/callback` | aanvaardbaar in dit lokale lab |
| `https://portal.example.com/*` | te breed voor productie |
| `https://evil.example.net/callback` | fout: hoort niet bij de applicatie |

Authentik mag de browser alleen terugsturen naar URI's die vooraf exact zijn goedgekeurd.

---

# Client ID is niet hetzelfde als client secret

| Onderdeel | Geheim? | Betekenis |
|---|:---:|---|
| **client ID** | nee | zegt welke applicatie praat met de IdP |
| **client secret** | ja | confidential client bewijst zich bij token endpoint |

Voor een client secret:

- niet in broncode;
- niet in screenshots of verslagen;
- niet in publieke repositories;
- roteerbaar houden;
- niet gebruiken in pure browsercode of mobiele apps.

In het lab staat het secret in `.env`. Dat is beter dan hardcoderen, maar nog geen productie-secret-management.

---

# ID token, access token en refresh token

| Token | Doel | Aandachtspunt |
|---|---|---|
| **ID token** | identity-claims voor de applicatie | bedoeld voor de OIDC-client |
| **access token** | toegang tot resource of endpoint | behandelen als geheim |
| **refresh token** | nieuwe access tokens verkrijgen | vergroot impact bij diefstal |

Gebruik een access token niet als algemeen bewijs van login.

Vraag `offline_access` alleen wanneer de applicatie dit echt nodig heeft.

---

# Claims zijn identity-informatie

| Claim | Betekenis | Waarom belangrijk? |
|---|---|---|
| `iss` | issuer | welke IdP gaf het token uit? |
| `sub` | stabiele subject identifier | beste technische sleutel |
| `aud` | bedoelde client | voorkomt tokengebruik bij app B |
| `exp` | vervaltijd | token mag niet eindeloos geldig zijn |
| `email` | e-mailadres | handig, maar niet altijd stabiel |
| `preferred_username` | gebruikersnaam | leesbaar, minder uniek als sleutel |
| `groups` | groepen of rollen | bruikbaar voor toegang, maar bewust beperken |

**Dataminimalisatie:** geef een app alleen claims die ze nodig heeft.

---

# Decoderen is niet valideren

Een ID token is vaak een JWT:

```text
header.payload.signature
```

Twee verschillende acties:

| Actie | Betekenis |
|---|---|
| decoderen | inhoud leesbaar maken |
| valideren | controleren of de inhoud betrouwbaar is |

Een aanvaller kan zelf tekst in JWT-formaat maken.

Pas na controle van handtekening, issuer, audience en geldigheid mag een applicatie het token vertrouwen.

---

<!-- _class: question -->

## Mini-case - welke laag faalt?

Een gebruiker ziet na login een fout.

| Symptoom | Eerste richting |
|---|---|
| redirect URI wordt geweigerd | providerconfiguratie |
| client secret werkt niet | token endpoint / provider |
| app verschijnt niet in portaal | application en bindings |
| gebruiker krijgt deny | groep, policy of binding |
| claims ontbreken | scopes of property mappings |

Waar in de flow plaats je het probleem voor je instellingen wijzigt?

---

<!-- _class: divider -->

# Authentik toepassen

## Application, provider, binding en bewijs

---

# Application en provider zijn verschillende objecten

| Object | Beschrijft vooral | Voorbeelden |
|---|---|---|
| **Application** | gebruikers- en toegangskant | naam, launch URL, zichtbaarheid, bindings |
| **Provider** | protocolkant | client ID, secret, redirect URI, scopes, signing key |

Mentale scheiding:

```text
Application:
  "BluePeak Portal bestaat en is zichtbaar voor deze gebruikers."

Provider:
  "BluePeak Portal gebruikt OIDC met deze redirect URI, client ID en scopes."
```

Veel fouten ontstaan door die twee door elkaar te halen.

---

# Waar kijk je eerst bij troubleshooting?

| Probleem | Waar kijk je eerst? |
|---|---|
| app verschijnt niet | application en zichtbaarheid |
| gebruiker krijgt deny | application bindings |
| redirect URI geweigerd | provider |
| client secret fout | provider en lokale clientconfig |
| verkeerde claims zichtbaar | provider scopes/property mappings |
| gebruiker ziet app maar login faalt technisch | provider en clientconfiguratie |

> Eerst bepalen of het een autorisatieprobleem, protocolprobleem, sessieprobleem of lifecycleprobleem is.

---

# Groepsgebaseerde toegang bewijzen

Voorbeeldbeleid:

| Applicatie | Toegang |
|---|---|
| medewerkersportaal | `bp-employees` |
| monitoring | `bp-it` |
| finance | `bp-finance` |
| partnerportaal | `bp-partners` |

Testmatrix voor BluePeak Portal:

| Identiteit | Groep | Verwacht |
|---|---|:---:|
| Alice | `bp-employees` | allow |
| Bob | `bp-employees`, `bp-it` | allow |
| Eva | `bp-partners` | deny |
| gedeactiveerde Alice | `bp-employees` | deny voor nieuwe login |

---

<!-- _class: question -->

## Checkpoint - login, policy of sessie?

Alice is gedeactiveerd terwijl haar browser nog een portalpagina open heeft.

Testen:

1. bestaande pagina vernieuwen;
2. alleen lokaal uitloggen;
3. opnieuw via Authentik aanmelden;
4. centrale sessie intrekken;
5. opnieuw proberen.

Welke stap test de **applicatiesessie**?  
Welke stap test de **IdP-sessie**?  
Welke stap test **nieuwe authenticatie**?

---

# Auditlogs maken identitybeheer onderzoekbaar

Nuttige gebeurtenissen:

| Event | Wat kan je ermee aantonen? |
|---|---|
| geslaagde login | wie kreeg toegang en wanneer |
| mislukte login | fout wachtwoord of mogelijk brute-forcegedrag |
| MFA-validatie | tweede factor gevraagd en aanvaard |
| groepslidmaatschap gewijzigd | waarom toegang veranderde |
| application/provider gewijzigd | configuratiewijziging rond login |
| policy deny | autorisatiegrens afgedwongen |
| sessie ingetrokken | bestaande toegang afgebroken |
| account gedeactiveerd | offboarding technisch uitgevoerd |

Neem credentials, secrets en volledige tokens nooit op in een verslag.

---

# Een auditlog vraagt context

| Contextvraag | Waarom nodig? |
|---|---|
| wanneer? | koppelen aan incidenttijdlijn of offboarding |
| welke gebruiker? | betrokken identiteit bepalen |
| bronadres? | labmachine, intern netwerk of verdachte locatie |
| applicatie of flow? | admin, user login, OIDC of MFA |
| resultaat? | succes, fout, blokkering of policy deny |
| beheerwijziging vooraf? | verklaart plotse gedragswijziging |

Een auditlog voorkomt geen aanval.

Het helpt wel bij detectie, onderzoek, verantwoording en herstel.

---

# Service accounts zijn ook identities

Niet elke identiteit is een mens.

<div class="columns">
<div>

### Voorbeelden

- back-upsoftware;
- monitoringintegratie;
- CI/CD-pipeline;
- API-integratie.

</div>
<div>

### Regels

- duidelijke eigenaar;
- beperkt doel;
- least privilege;
- roteerbare credentials;
- monitoring en reviewdatum.

</div>
</div>

Interactieve MFA past meestal niet bij machine-to-machineverkeer.

---

# De identity provider is een netwerkservice

Veel applicaties hangen af van de IdP. Een fout kan veel logins tegelijk verstoren.

<div class="columns">
<div>

```text
gebruikers
    |
 HTTPS
    |
reverse proxy / load balancer
    |
identity provider
    |
database
```

</div>
<div>

### Kritieke afhankelijkheden

<span class="tag">DNS</span>
<span class="tag">TLS</span>
<span class="tag">database</span>
<span class="tag">tijd</span>
<span class="tag">signing keys</span>
<span class="tag">reverse proxy</span>

</div>
</div>

**HTTP op localhost is een labkeuze, geen productieontwerp.**

---

# Productievragen rond Authentik

| Vraag | Waarom belangrijk? |
|---|---|
| stabiele DNS-naam? | OIDC/SAML-clients verwachten dezelfde issuer |
| waar eindigt TLS? | credentials, cookies en tokens beschermen |
| admininterface bereikbaar vanaf waar? | beheerfuncties beperken |
| back-up van database en configuratie? | herstel na fout of uitval |
| gedrag bij IdP-uitval? | fail-closed, fail-open of onbruikbaar |
| tijdsynchronisatie? | tokens, sessies en TOTP vertrouwen op tijd |
| signing keys beschermd? | tokens blijven alleen betrouwbaar met veilige sleutels |

**Centrale identiteit vermindert verspreide risico's, maar concentreert afhankelijkheid.**

---

# Typische fouten horen bij herkenbare categorieen

| Fout | Gevolg | Betere aanpak |
|---|---|---|
| geen binding | toegang te breed of te smal | expliciete groepen en negatieve tests |
| client secret in Git | credentiallek | secret store en rotatie |
| wildcard redirect URI | code kan verkeerd eindigen | strikte redirect URI |
| MFA alleen geregistreerd | schijnveiligheid | flow en test controleren |
| adminaccount dagelijks gebruiken | grote impact bij compromis | apart beheerdersaccount |
| alleen positieve test | foutieve policy blijft onzichtbaar | allow- en deny-test |
| account gedeactiveerd, sessies actief | toegang duurt mogelijk voort | sessies en tokens intrekken |
| tijd niet correct | TOTP- en tokenproblemen | betrouwbare tijdsynchronisatie |

---

# Een goed identitytestplan test grenzen

| Test | Verwacht | Waarom? |
|---|---|---|
| medewerker meldt aan | login slaagt | basisflow |
| tweede app openen | SSO zonder nieuwe wachtwoordprompt | IdP-sessie |
| partner opent medewerkersapp | deny | autorisatiegrens |
| gebruiker krijgt claims | juiste username, e-mail, groepen | identity-informatie |
| TOTP-login | tweede factor gevraagd | MFA in flow |
| fout wachtwoord | login faalt en event verschijnt | foutafhandeling |
| gebruiker gedeactiveerd | nieuwe login faalt | lifecycle |
| verkeerde redirect URI | OIDC-request geweigerd | protocolgrens |

Een screenshot van een succesvolle login bewijst niet dat de policy volledig klopt.

---

# Van observatie naar professioneel advies

| Onderdeel | Voorbeeld BluePeak Portal |
|---|---|
| requirement | alleen medewerkers mogen de portal openen |
| observatie | Alice en Bob krijgen toegang; Eva krijgt deny |
| bewijs | usergroepen, binding, appresultaat en audit event |
| risico bij afwijking | partner of ex-medewerker kan interne app bereiken |
| maatregel | expliciete group binding en sessie-intrekking bij offboarding |
| acceptatie | allow-, deny-, MFA-, lifecycle- en audittest slagen |

Een sterk advies verbindt requirement -> bewijs -> risico -> maatregel -> acceptatietest.

---

# Labkeuze is geen productiegarantie

| In het lab | In productie aanvullend nodig |
|---|---|
| Authentik lokaal op `localhost` | stabiele DNS, TLS en reverse proxy |
| secret in `.env` | secret management en rotatie |
| TOTP zichtbaar testen | MFA-policy, recovery en phishingrisico beoordelen |
| enkele gebruikers en groepen | lifecycleproces en periodieke review |
| lokale OIDC-client | volledige tokenvalidatie en security hardening |
| manuele auditcontrole | centrale logging, alerting en tijdsynchronisatie |

**Benoem altijd wat de proof of concept bewijst en wat niet.**

---

<!-- _class: divider -->

# Van theorie naar praktijk

## Centrale identiteit bouwen, testen en bewijzen

---

# Van theorie naar praktijk

In de workshop bouw je een Authentik-proof-of-concept voor **BluePeak Services**.

Je zal:

- gebruikers en groepen modelleren;
- een Authentik application en OIDC-provider maken;
- een confidential OIDC-client koppelen;
- groepsgebaseerde toegang via een binding testen;
- SSO, MFA, claims, lifecycle en auditlogs onderzoeken;
- foutscenario's analyseren zonder secrets of tokens te publiceren.

> Doel: niet alleen login werkend maken, maar bewijzen dat het identity- en accessmodel klopt.

---

<!-- _class: question -->

## Voorbereidende case

BluePeak heeft:

- `alice.vermeulen` in `bp-employees`;
- `bob.peeters` in `bp-employees` en `bp-it`;
- `eva.partner` in `bp-partners`;
- een BluePeak Portal met OIDC-provider;
- een onbekende application binding;
- een actieve Authentik-sessie in de browser.

Welke drie tests voer je eerst uit om te bewijzen of de toegang correct begrensd is?

Welke conclusie mag je nog niet trekken?

---

# Wat moet je onthouden?

1. Centrale identiteit maakt login en identity-informatie consistenter, maar maakt de IdP kritieke infrastructuur.
2. Authenticatie bewijst wie iemand is; autorisatie bepaalt wat die identiteit mag.
3. SSO heeft minstens een IdP-sessie en een applicatiesessie; test dus expliciet welke sessie actief blijft.
4. OIDC gebruikt een authorization code flow, tokens, scopes en claims binnen een expliciete vertrouwensrelatie.
5. Bewijs identitysecurity met allow-tests, deny-tests, MFA-tests, lifecycle-tests en auditlogs.
