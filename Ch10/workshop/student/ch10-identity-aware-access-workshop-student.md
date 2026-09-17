# Workshop 10 - Identity-aware access met Traefik en Authentik

## 1. Situering

In hoofdstuk 8 publiceerde je interne webapplicaties via Traefik.

In hoofdstuk 9 koppelde je een applicatie rechtstreeks aan Authentik via OpenID
Connect.

In deze workshop bescherm je bestaande webapplicaties die zelf geen OIDC-koppeling
hebben.

Traefik blijft het applicatieverkeer proxyen. Voor elke beschermde request vraagt
Traefik eerst aan de embedded Authentik-outpost of de gebruiker toegang heeft.

Je bouwt dit stapsgewijs op:

1. Authentik, Traefik en vijf interne apps starten;
2. een publieke route controleren;
3. één intranetroute met forward auth beschermen;
4. een application en proxy provider aan een groep binden;
5. het patroon uitbreiden naar monitoring, admin en partner;
6. step-up MFA voor het adminportaal toepassen;
7. identity-headers, SSO, logout en logs onderzoeken;
8. negatieve tests en een fail-closedtest uitvoeren.

Belangrijk:

> Neem geen wachtwoorden, cookies, tokens, TOTP-seeds, QR-codes, herstelcodes of
> andere secrets op in je verslag.

---

## 2. Scenario

**BluePeak Services** heeft vijf webapplicaties.

| Applicatie | Doelgroep | Hostname | Policy |
|---|---|---|---|
| Publieke status | iedereen | `public.bluepeak.test` | geen login |
| Intranet | medewerkers | `intranet.bluepeak.test` | `bp-employees` |
| Monitoring | IT | `monitoring.bluepeak.test` | `bp-it` |
| Admin | IT-admins | `admin.bluepeak.test` | `bp-it-admins` + TOTP |
| Partnerportaal | externe partners | `partner.bluepeak.test` | `bp-partners` |

De backendcontainers mogen niet rechtstreeks via hostpoorten bereikbaar zijn.

De organisatie wil ook kunnen aantonen:

- welke requests via Traefik lopen;
- waarom een gebruiker toegang kreeg of werd geweigerd;
- welke identity-informatie bij een toegelaten backend aankomt;
- dat een zelf aangeleverde identity-header geen login omzeilt;
- dat beschermde applicaties sluiten wanneer Authentik niet beschikbaar is.

Centrale onderzoeksvraag:

> Hoe dwing je per webapplicatie een ander identiteitsbeleid af zonder elke backend
> zelf een volledige loginintegratie te geven?

---

## 3. Beginsituatie

Werk in:

```text
Ch10/workshop/configs/student/identity-aware-lab
```

Je krijgt:

| Bestand of map | Doel |
|---|---|
| `compose.yml` | PostgreSQL, Authentik, Traefik en vijf interne apps |
| `.env.example` | lokale omgevingsvariabelen zonder echte secrets |
| `.gitignore` | sluit lokale secrets en data uit |
| `traefik/dynamic.yml` | starterroutes voor Authentik en de publieke app |
| `apps/app.py` | demoapp die ontvangen identity-headers toont |
| `blueprints/bluepeak-admin-step-up.yaml` | MFA-authorization flow zonder secrets |

Bij de start zijn alleen deze routes geconfigureerd:

```text
auth.bluepeak.test:8100
public.bluepeak.test:8100
```

De beschermde backends draaien al intern, maar hebben nog geen Traefik-router.

---

## 4. Doelen

Na deze workshop kan je:

1. reverse proxy, Authentik core, embedded outpost en backend onderscheiden;
2. een publieke en een beschermde Traefik-route vergelijken;
3. een forward-authmiddleware configureren;
4. het speciale outpostpad met hogere routerprioriteit publiceren;
5. een proxy provider in single-application forward-authmodus maken;
6. applications met groepsbindings beschermen;
7. meerdere hostnames met afzonderlijke policies configureren;
8. step-up TOTP voor het adminportaal aantonen;
9. doorgestuurde identity-headers onderzoeken;
10. SSO- en logoutgedrag verklaren;
11. positieve, negatieve, spoofing- en fail-closedtests uitvoeren;
12. logs en events gebruiken om een fout te lokaliseren;
13. uitleggen waarom deze oplossing VPN en firewalling niet volledig vervangt.

---

## 5. Benodigdheden

Je hebt nodig:

- Docker Desktop of Docker Engine;
- Docker Compose v2;
- minstens 2 CPU-cores en 3 GB vrij RAM;
- terminal;
- browser met private/incognitovensters;
- `curl.exe`;
- een TOTP-compatibele authenticator;
- cursus hoofdstuk 8, 9 en 10.

Poorten:

| Hostpoort | Doel |
|---:|---|
| `8100` | alle app- en Authentik-hostnames via Traefik |
| `8188` | lokaal Traefik-dashboard voor het lab |

Het lab gebruikt bewust HTTP op lokale testhostnames. Productie vereist HTTPS.

---

## 6. Identity- en accessmodel

Gebruik onderstaande matrix als gewenst identity- en accessmodel. Op dit moment hoef
je de gebruikers en groepen nog niet aan te maken: Authentik wordt pas in stap 3
geïnitialiseerd. Je maakt de accounts en groepen aan in stap 5.

| Gebruiker | Groepen | TOTP |
|---|---|---|
| Alice Vermeulen | `bp-employees` | niet vereist |
| Bob Peeters | `bp-employees`, `bp-it`, `bp-it-admins` | bevestigd device |
| Eva Partner | `bp-partners` | niet vereist |

Gebruik unieke labwachtwoorden die je nergens anders gebruikt.

Vul vóór je begint de verwachte matrix in:

| Gebruiker | Public | Intranet | Monitoring | Admin | Partner |
|---|---|---|---|---|---|
| anoniem | ... | ... | ... | ... | ... |
| Alice | ... | ... | ... | ... | ... |
| Bob | ... | ... | ... | ... | ... |
| Eva | ... | ... | ... | ... | ... |

---

## 7. Stap 1: bereid de omgeving voor

Maak een lokale `.env`:

```powershell
Copy-Item .env.example .env
```

Vervang de twee `CHANGE_ME`-waarden door verschillende willekeurige labwaarden:

```text
PG_PASS=...
AUTHENTIK_SECRET_KEY=...
```

Neem `.env` niet op in je indiening.

Voeg aan je hosts file toe:

```text
127.0.0.1 auth.bluepeak.test
127.0.0.1 public.bluepeak.test
127.0.0.1 intranet.bluepeak.test
127.0.0.1 monitoring.bluepeak.test
127.0.0.1 admin.bluepeak.test
127.0.0.1 partner.bluepeak.test
```

Controleer:

```powershell
Resolve-DnsName auth.bluepeak.test
Resolve-DnsName intranet.bluepeak.test
```

Als je de hosts file niet mag aanpassen, kan je voor eenvoudige HTTP-tests
`curl.exe --resolve` gebruiken. Interactieve browserlogin werkt het duidelijkst met de
hosts file.

---

## 8. Stap 2: inspecteer en start de stack

Bekijk eerst de services zonder ze te starten:

```text
docker compose config --services
```

Classificeer ze:

| Service | Laag | Hostpoort? | Waarom? |
|---|---|---|---|
| `postgresql` | ... | ... | ... |
| `server` | ... | ... | ... |
| `worker` | ... | ... | ... |
| `reverse-proxy` | ... | ... | ... |
| `public` | ... | ... | ... |
| `intranet` | ... | ... | ... |
| `monitoring` | ... | ... | ... |
| `admin` | ... | ... | ... |
| `partner` | ... | ... | ... |

Start:

```text
docker compose up -d
docker compose ps
```

Wacht tot database, server en worker klaar zijn.

Controleer indien nodig:

```text
docker compose logs server
docker compose logs worker
docker compose logs reverse-proxy
```

Controlepunt:

> Alleen Traefik publiceert webpoorten naar de host. Authentik en de backends zijn
> intern via het Docker-netwerk bereikbaar.

---

## 9. Stap 3: initialiseer Authentik

Open exact:

```text
http://auth.bluepeak.test:8100
```

Maak de lokale `akadmin`-beheerder aan.

Gebruik geen productiewachtwoord en neem het wachtwoord niet op in je verslag.

Open daarna:

```text
http://auth.bluepeak.test:8100
```

Controleer in de Admin interface:

```text
Applications > Outposts > authentik Embedded Outpost
```

De `authentik_host` moet een volledige URL zijn:

```text
http://auth.bluepeak.test:8100
```

Pas dit aan als Authentik een andere host detecteerde.

Beantwoord:

- Waarom gebruiken browserredirects `auth.bluepeak.test` en niet de Docker-servicenaam
  `server`?
- Waarom gebruikt Traefik intern wel `http://server:9000`?

---

## 10. Stap 4: controleer de publieke route

Open:

```text
http://public.bluepeak.test:8100
```

Test ook:

```text
curl.exe -I http://public.bluepeak.test:8100
```

Vul in:

| Controle | Verwacht | Werkelijk |
|---|---|---|
| pagina opent zonder login | ja | ... |
| app-naam | Public status | ... |
| `X-authentik-username` zichtbaar | nee | ... |
| publieke backend heeft eigen hostpoort | nee | ... |

Bekijk `traefik/dynamic.yml`.

Welke vier onderdelen verbinden hostname en backend?

```text
router -> rule -> service -> interne URL
```

---

## 11. Stap 5: maak groepen en gebruikers

Je hebt nu toegang tot de Authentik Admin interface. Maak de groepen en gebruikers
aan volgens het identity- en accessmodel uit sectie 6. Gebruik je bestaande Ch9-
omgeving niet automatisch als bron: deze Ch10-stack heeft een eigen Authentik-
database.

Maak onder `Directory > Groups`:

```text
bp-employees
bp-it
bp-it-admins
bp-partners
```

Maak onder `Directory > Users`:

| Username | Naam | Groepen |
|---|---|---|
| `alice.vermeulen` | Alice Vermeulen | `bp-employees` |
| `bob.peeters` | Bob Peeters | `bp-employees`, `bp-it`, `bp-it-admins` |
| `eva.partner` | Eva Partner | `bp-partners` |

Maak de groepen niet superuser en geef ze geen Authentik-beheersrollen.

Als Bob nog geen bevestigd TOTP-device heeft, registreer dat via zijn
gebruikersinstellingen zoals in hoofdstuk 9.

Controlepunt:

> Groepslidmaatschap geeft nog geen toegang. Er bestaan nog geen applications en
> bindings voor deze vier beschermde hostnames.

---

## 12. Stap 6: voeg de technische forward-authlaag toe

Open:

```text
traefik/dynamic.yml
```

### 12.1 Middleware

Voeg onder `http.middlewares` een middleware toe:

```yaml
    authentik-forward:
      forwardAuth:
        address: "http://server:9000/outpost.goauthentik.io/auth/traefik"
        trustForwardHeader: true
        authResponseHeaders:
          - X-authentik-username
          - X-authentik-groups
          - X-authentik-email
          - X-authentik-name
          - X-authentik-uid
          - X-authentik-meta-app
          - X-authentik-meta-provider
```

Beantwoord:

- Naar welk intern component stuurt Traefik de controle?
- Waarom is dit niet de backend-URL?
- Welke headers mogen pas na een geslaagde controle bij de backend aankomen?

### 12.2 Outpostservice

Voeg onder `http.services` toe:

```yaml
    authentik-outpost:
      loadBalancer:
        servers:
          - url: "http://server:9000/outpost.goauthentik.io"
```

### 12.3 Outpostrouter

Voeg onder `http.routers` toe:

```yaml
    protected-outpost:
      rule: "(Host(`intranet.bluepeak.test`) || Host(`monitoring.bluepeak.test`) || Host(`admin.bluepeak.test`) || Host(`partner.bluepeak.test`)) && PathPrefix(`/outpost.goauthentik.io/`)"
      entryPoints:
        - web
      priority: 100
      service: authentik-outpost
```

Waarom heeft deze router prioriteit `100`?

Controleer de syntax via:

```text
docker compose logs reverse-proxy
```

---

## 13. Stap 7: publiceer het intranet als beschermde route

Voeg onder `http.routers` toe:

```yaml
    intranet:
      rule: "Host(`intranet.bluepeak.test`)"
      entryPoints:
        - web
      service: intranet
      middlewares:
        - authentik-forward
        - security-headers
```

Voeg onder `http.services` toe:

```yaml
    intranet:
      loadBalancer:
        servers:
          - url: "http://intranet:8080"
```

Test nu al:

```text
http://intranet.bluepeak.test:8100
```

De volledige login kan nog niet werken: er bestaat nog geen passende Authentik
application/proxy provider.

Noteer het symptoom en bekijk:

```text
docker compose logs reverse-proxy
docker compose logs server
```

Dit is een bewuste tussenfase.

---

## 14. Stap 8: maak de intranetapplication en proxy provider

Ga in Authentik naar:

```text
Applications > Applications > New Application
```

Maak application en provider als paar.

### Application

| Instelling | Waarde |
|---|---|
| Name | `BluePeak Intranet` |
| Slug | `bluepeak-intranet` |
| Launch URL | `http://intranet.bluepeak.test:8100` |
| Policy engine mode | `Any` |

### Proxy provider

| Instelling | Waarde |
|---|---|
| Provider type | Proxy Provider |
| Name | `BluePeak Intranet Proxy` |
| Authorization flow | standaard implicit-consentflow |
| Authentication flow | standaard authentication flow |
| Mode | Forward auth (single application) |
| External host | `http://intranet.bluepeak.test:8100` |

### Binding

Bind de application aan:

```text
bp-employees
```

Belangrijk:

> Zonder binding is een application standaard breder toegankelijk. Controleer dus
> expliciet dat de groepsbinding bestaat.

---

## 15. Stap 9: wijs intranet toe aan de embedded outpost

Ga naar:

```text
Applications > Outposts > authentik Embedded Outpost
```

Voeg `BluePeak Intranet` toe aan de geselecteerde applications en sla op.

Test de technische outpostroute:

```text
curl.exe -i http://intranet.bluepeak.test:8100/outpost.goauthentik.io/ping
```

Verwacht een succesvolle lege healthrespons, typisch status `204`.

Als dit niet werkt, controleer eerst:

- voer uit 'docker compose restart reverse-proxy' en wacht enkele seconden om de nieuwe outpost te activeren in Traefik
- hosts file;
- outpostrouter en prioriteit;
- outpostservice-URL;
- embedded-outposttoewijzing;
- `authentik_host`.

---

## 16. Stap 10: test intranet positief en negatief

Gebruik afzonderlijke private browsersessies.

### Alice

Open:

```text
http://intranet.bluepeak.test:8100
```

Meld aan als Alice.

Controleer op de backendpagina:

- username;
- groepen;
- e-mail;
- Authentik application slug.

### Eva

Open een nieuw private venster en herhaal als Eva.

Vul in:

| Test | Verwacht | Werkelijk | Bewijs zonder secrets |
|---|---|---|---|
| Alice naar intranet | allow | ... | ... |
| Eva naar intranet | deny | ... | ... |
| anoniem naar intranet | redirect naar login | ... | ... |

Controlepunt:

> Een geldige partnerlogin is geen geldige intranettoegang.

---

## 17. Stap 11: voeg monitoring en partner toe

Je bouwt nu twee extra beschermde routes. Werk eerst de Traefik-configuratie af en
maak daarna de bijhorende Authentik-configuratie. Test elke applicatie afzonderlijk;
voeg niet beide wijzigingen tegelijk toe zonder tussentijds te controleren.

### 11.1 Voeg de monitoringroute toe aan Traefik

Open `traefik/dynamic.yml` en voeg onder `http.routers` deze router toe:

```yaml
    monitoring:
      rule: "Host(`monitoring.bluepeak.test`)"
      entryPoints:
        - web
      service: monitoring
      middlewares:
        - authentik-forward
        - security-headers
```

Voeg onder `http.services` de interne service toe:

```yaml
    monitoring:
      loadBalancer:
        servers:
          - url: "http://monitoring:8080"
```

De hostname is de URL die de browser gebruikt. `monitoring:8080` is de interne
Docker-URL die alleen Traefik gebruikt. Publiceer geen hostpoort voor de
monitoringcontainer.

Controleer de configuratie:

```powershell
docker compose logs reverse-proxy
```

Open daarna:

```text
http://monitoring.bluepeak.test:8100
```

Een redirect naar Authentik of een weigering is op dit moment normaal: de
monitoringapplication bestaat nog niet of is nog niet aan de embedded outpost
toegevoegd. Een foutmelding in de Traefik-logs wijst wel op een configuratieprobleem.

### 11.2 Maak de monitoringapplication en provider

Ga in Authentik naar:

```text
Applications > Applications > New Application
```

Maak eerst de application aan:

| Instelling | Waarde |
|---|---|
| Name | `BluePeak Monitoring` |
| Slug | `bluepeak-monitoring` |
| Launch URL | `http://monitoring.bluepeak.test:8100` |
| Policy engine mode | `Any` |

Maak daarna via de providerconfiguratie een nieuwe `Proxy Provider`:

| Instelling | Waarde |
|---|---|
| Name | `BluePeak Monitoring Proxy` |
| Authorization flow | standaard implicit-consentflow |
| Authentication flow | standaard authentication flow |
| Mode | `Forward auth (single application)` |
| External host | `http://monitoring.bluepeak.test:8100` |

Koppel de provider aan `BluePeak Monitoring`.

### 11.3 Bind monitoring aan de IT-groep

Open de bindings van `BluePeak Monitoring` en voeg uitsluitend deze groep toe:

```text
bp-it
```

Controleer dat `bp-employees` en `bp-partners` niet aan deze application gebonden
zijn. Een gebruiker kan dus wel geldig aangemeld zijn bij Authentik en toch voor
monitoring geweigerd worden.

### 11.4 Voeg monitoring toe aan de embedded outpost

Ga naar:

```text
Applications > Outposts > authentik Embedded Outpost
```

Voeg `BluePeak Monitoring` toe aan de geselecteerde applications en sla op.

Controleer de technische outpostroute:

```powershell
curl.exe -i http://monitoring.bluepeak.test:8100/outpost.goauthentik.io/ping
```

Verwacht een lege succesvolle respons, typisch `HTTP 204 No Content`.

### 11.5 Test monitoring vóór je partner configureert

Gebruik voor elke identiteit een nieuw private browservenster of beëindig eerst de
bestaande Authentik-sessie.

1. Meld aan als Bob en open `http://monitoring.bluepeak.test:8100`. Bob hoort toegang
   te krijgen omdat hij lid is van `bp-it`.
2. Meld aan als Alice in een nieuw private venster. Alice hoort geweigerd te worden:
   `bp-employees` geeft geen monitoringtoegang.
3. Controleer op de backendpagina welke username, groepen en application slug bij
   een toegelaten Bob-request aankomen.
4. Noteer status, redirect of deny zonder wachtwoorden, cookies of tokens op te
   nemen.

### 11.6 Voeg de partnerroute toe aan Traefik

Voeg onder `http.routers` toe:

```yaml
    partner:
      rule: "Host(`partner.bluepeak.test`)"
      entryPoints:
        - web
      service: partner
      middlewares:
        - authentik-forward
        - security-headers
```

Voeg onder `http.services` toe:

```yaml
    partner:
      loadBalancer:
        servers:
          - url: "http://partner:8080"
```

Controleer opnieuw:

```powershell
docker compose logs reverse-proxy
```

Open `http://partner.bluepeak.test:8100`. Een loginredirect of deny vóór de
Authentik-configuratie is normaal.

### 11.7 Maak de partnerapplication en provider

Maak in Authentik een nieuwe application:

| Instelling | Waarde |
|---|---|
| Name | `BluePeak Partner Portal` |
| Slug | `bluepeak-partner` |
| Launch URL | `http://partner.bluepeak.test:8100` |
| Policy engine mode | `Any` |

Maak vervolgens de provider:

| Instelling | Waarde |
|---|---|
| Name | `BluePeak Partner Proxy` |
| Authorization flow | standaard implicit-consentflow |
| Authentication flow | standaard authentication flow |
| Mode | `Forward auth (single application)` |
| External host | `http://partner.bluepeak.test:8100` |

Koppel de provider aan `BluePeak Partner Portal`. Open daarna de bindings en voeg
uitsluitend toe:

```text
bp-partners
```

### 11.8 Voeg partner toe aan de embedded outpost

Ga opnieuw naar:

```text
Applications > Outposts > authentik Embedded Outpost
```

Voeg `BluePeak Partner Portal` toe aan de geselecteerde applications en sla op.

Test de technische route:

```powershell
curl.exe -i http://partner.bluepeak.test:8100/outpost.goauthentik.io/ping
```

Verwacht opnieuw typisch `HTTP 204 No Content`.

### 11.9 Test partner en controleer de volledige matrix

1. Meld Eva aan in een nieuw private venster en open
   `http://partner.bluepeak.test:8100`. Eva hoort toegang te krijgen.
2. Meld Bob aan in een nieuw private venster en open dezelfde URL. Bob hoort
   geweigerd te worden omdat hij geen lid is van `bp-partners`.
3. Test eventueel anoniem. De verwachte uitkomst is een loginredirect.
4. Controleer met `docker compose ps` dat de backendcontainers nog altijd geen
   hostpoorten publiceren.

Vul daarna de tabel in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| Bob naar monitoring | allow | ... |
| Alice naar monitoring | deny | ... |
| Eva naar partner | allow | ... |
| Bob naar partner | deny | ... |

Controleer bij een onverwachte uitkomst in deze volgorde: groepslidmaatschap,
application binding, providerinstellingen, toewijzing aan de embedded outpost,
`authentik_host`, hosts file en daarna pas de backendlogs.

---

## 18. Stap 12: importeer de step-up-MFA-flow

De map `blueprints/` bevat:

```text
bluepeak-admin-step-up.yaml
```

Lees het bestand vóór je het importeert.

Beantwoord:

- Welke designation heeft de flow?
- Welke MFA-deviceclass is toegelaten?
- Wat gebeurt met een gebruiker zonder geconfigureerd TOTP-device?
- Waarom bevat het bestand geen gebruikerswachtwoorden of TOTP-seeds?

Importeer de flow via de blueprint/flow-importfunctie van Authentik.

Controleer daarna onder `Flows and Stages > Flows` dat deze flow bestaat:

```text
bluepeak-admin-step-up
```

Controleer de stage binding.

Kernpunt:

> De flow controleert MFA tijdens de authorization van de gevoelige applicatie. Een
> bestaande SSO-sessie alleen is daardoor niet voldoende.

---

## 19. Stap 13: configureer het adminportaal

Configureer eerst de adminroute in Traefik. Pas daarna maak je de application en
provider in Authentik aan.

### 13.1 Voeg de adminrouter toe

Open:

```text
traefik/dynamic.yml
```

Voeg onder `http.routers` deze router toe:

```yaml
    admin:
      rule: "Host(`admin.bluepeak.test`)"
      entryPoints:
        - web
      service: admin
      middlewares:
        - authentik-forward
        - security-headers
```

De router gebruikt de bestaande `authentik-forward`-middleware. Daardoor wordt elke
adminrequest eerst door Authentik gecontroleerd. De bestaande
`security-headers`-middleware blijft daarnaast actief.

### 13.2 Voeg de adminservice toe

Voeg onder `http.services` deze service toe:

```yaml
    admin:
      loadBalancer:
        servers:
          - url: "http://admin:8080"
```

Let op het verschil tussen beide adressen:

| Adres | Betekenis |
|---|---|
| `admin.bluepeak.test:8100` | externe hostname die de browser gebruikt |
| `http://admin:8080` | interne Docker-URL waarnaar Traefik proxyt |

Maak geen hostpoort voor de `admin`-container aan. De backend mag alleen via Traefik
bereikbaar zijn.

### 13.3 Controleer de Traefik-configuratie

Sla `dynamic.yml` op en controleer de reverse-proxylogs:

```powershell
docker compose logs reverse-proxy
```

Controleer ook de containerstatus:

```powershell
docker compose ps
```

Er mag geen configuratie- of parsefout voor de adminrouter staan. De admincontainer
mag geen hostpoort publiceren.

### 13.4 Test de route vóór Authentik-configuratie

Open in een nieuw private browservenster:

```text
http://admin.bluepeak.test:8100
```

Een redirect naar Authentik of een weigering is in deze tussenfase normaal, want de
adminapplication en provider bestaan nog niet. De backend mag nog geen normale
admininhoud tonen zonder een geldige Authentik-configuratie.

Controleer de technische outpostroute:

```powershell
curl.exe -i http://admin.bluepeak.test:8100/outpost.goauthentik.io/ping
```

Verwacht typisch:

```text
HTTP 204 No Content
```

Als dit niet lukt, controleer dan eerst de hostname in de hosts file, de
`protected-outpost`-router, de prioriteit `100`, de service-URL
`http://server:9000/outpost.goauthentik.io` en `authentik_host`. Pas wanneer deze
technische route werkt, ga je verder met de application.

### 13.5 Maak de adminapplication en provider in Authentik

Ga naar:

```text
Applications > Applications > New Application
```

Maak de application aan:

| Instelling | Waarde |
|---|---|
| Application | `BluePeak Admin` |
| Slug | `bluepeak-admin` |
| Launch URL | `http://admin.bluepeak.test:8100` |
| Provider | `BluePeak Admin Proxy` |
| Mode | Forward auth (single application) |
| External host | `http://admin.bluepeak.test:8100` |
| Authentication flow | standaard authentication flow |
| Authorization flow | `bluepeak-admin-step-up` |
| Binding | `bp-it-admins` |

Als Authentik application en provider afzonderlijk laat aanmaken, maak dan eerst de
provider en koppel die daarna aan de application:

| Providerinstelling | Waarde |
|---|---|
| Name | `BluePeak Admin Proxy` |
| Provider type | `Proxy Provider` |
| Mode | `Forward auth (single application)` |
| External host | `http://admin.bluepeak.test:8100` |
| Authentication flow | standaard authentication flow |
| Authorization flow | `bluepeak-admin-step-up` |

Open de application bindings en voeg uitsluitend toe:

```text
bp-it-admins
```

Controleer dat de application niet aan `bp-employees`, `bp-it` of `bp-partners` is
gebonden. Bob hoort toegang te krijgen; Alice en Eva niet.

### 13.6 Voeg de adminapplication toe aan de embedded outpost

Ga naar:

```text
Applications > Outposts > authentik Embedded Outpost
```

Voeg `BluePeak Admin` toe aan de geselecteerde applications en sla op.

Test daarna opnieuw:

```text
http://admin.bluepeak.test:8100
```

De volledige adminlogin kan nu door naar de standaard authentication flow en daarna
naar `bluepeak-admin-step-up`. De extra TOTP-test zelf voer je uit in stap 14.

---

## 20. Stap 14: bewijs step-up MFA

Gebruik Bob met een bevestigd TOTP-device.

1. Meld Bob volledig af.
2. Open het intranet en meld Bob aan.
3. Controleer dat intranet werkt.
4. Open in hetzelfde browserprofiel het adminportaal.
5. Observeer de extra TOTP-validatie.
6. Test een foutieve code.
7. Test daarna een geldige code.

Vul in:

| Test | Verwacht | Werkelijk |
|---|---|---|
| Bob opent intranet | allow | ... |
| Bob opent admin met alleen bestaande SSO-sessie | MFA-stap | ... |
| foute TOTP | deny / flow niet voltooid | ... |
| geldige TOTP | allow | ... |

Negatieve test zonder geconfigureerde factor:

1. Voeg Alice tijdelijk toe aan `bp-it-admins`.
2. Open admin in een nieuwe private sessie als Alice.
3. Controleer dat groepslidmaatschap alleen niet volstaat.
4. Verwijder Alice opnieuw uit `bp-it-admins`.

Neem geen QR-code, TOTP-seed of code op in je verslag.

---

## 21. Stap 15: onderzoek SSO en logout

Meld Bob aan en open achtereenvolgens:

```text
http://intranet.bluepeak.test:8100
http://monitoring.bluepeak.test:8100
```

Observeer of het wachtwoord opnieuw gevraagd wordt.

Log daarna uit bij alleen de monitoringprovider:

```text
http://monitoring.bluepeak.test:8100/outpost.goauthentik.io/sign_out
```

Test opnieuw:

- monitoring;
- intranet;
- centrale Authentik-interface.

Vul in:

| Actie | Centrale sessie | Intranettoegang | Monitoringtoegang |
|---|---|---|---|
| vóór providerlogout | ... | ... | ... |
| na monitoringproviderlogout | ... | ... | ... |
| na volledige Authentik-logout | ... | ... | ... |

Beantwoord:

- Welke sessie werd door providerlogout beëindigd?
- Waarom kan SSO daarna opnieuw snel toegang geven?
- Waarom is accountdeactivatie niet automatisch hetzelfde als elke sessie intrekken?

---

## 22. Stap 16: test header spoofing en backendisolatie

Stuur zonder geldige sessie zelf een identity-header mee:

```text
curl.exe -i -H "X-authentik-username: akadmin" http://admin.bluepeak.test:8100
```

Verwacht:

- geen toegang tot de adminbackend;
- redirect of deny door Authentik;
- de zelfgekozen header omzeilt forward auth niet.

Controleer ook dat de backends geen hostpoort hebben:

```text
docker compose ps
curl.exe -I http://localhost:8101
curl.exe -I http://localhost:8102
curl.exe -I http://localhost:8103
curl.exe -I http://localhost:8104
```

Vul in:

| Test | Verwacht | Werkelijk | Securitybetekenis |
|---|---|---|---|
| gespoofte adminheader | geen bypass | ... | ... |
| `localhost:8101` | faalt | ... | ... |
| `localhost:8102` | faalt | ... | ... |
| `localhost:8103` | faalt | ... | ... |
| `localhost:8104` | faalt | ... | ... |

---

## 23. Stap 17: voer een fail-closedtest uit

Zorg eerst dat een protected route normaal werkt.

Stop daarna alleen Authentik server tijdelijk:

```text
docker compose stop server
```

Gebruik een nieuwe private browsersessie of een request zonder geldige providercookie.

Test:

```text
http://public.bluepeak.test:8100
http://intranet.bluepeak.test:8100
```

Vul in:

| Test tijdens IdP-storing | Verwacht | Werkelijk |
|---|---|---|
| public | blijft werken | ... |
| nieuwe protected request | faalt gesloten | ... |
| protected backend wordt toch getoond | nee | ... |

Start Authentik opnieuw:

```text
docker compose start server
```

Wacht tot de service klaar is en hertest.

Beantwoord:

- Waarom is fail-open gevaarlijk?
- Welk beschikbaarheidsrisico introduceert centrale identiteit?
- Welke maatregelen zijn nodig voor productie?

---

## 24. Stap 18: logs en events correleren

Voer kort na elkaar uit:

1. een toegelaten intranetrequest als Alice;
2. een geweigerde monitoringrequest als Alice;
3. een toegelaten adminrequest als Bob na MFA.

Bekijk:

```text
docker compose logs reverse-proxy
docker compose logs server
```

Bekijk in Authentik:

```text
Events > Logs
```

Vul in zonder cookies of tokens te kopiëren:

| Event | Tijd | Gebruiker | Applicatie/host | Resultaat | Bewijsbron |
|---|---|---|---|---|---|
| intranet allow | ... | ... | ... | ... | ... |
| monitoring deny | ... | ... | ... | ... | ... |
| admin MFA allow | ... | ... | ... | ... | ... |

Beantwoord:

- Welke bron toont de HTTP-status?
- Welke bron verklaart de groeps- of policybeslissing?
- Welke bron toont de headers die de backend ontving?
- Waarom heb je de drie bronnen samen nodig?

---

## 25. Foutscenario's

Voer minstens één scenario uit. Herstel de fout daarna.

### Scenario A: middleware verwijderen

Verwijder tijdelijk `authentik-forward` van de monitoringrouter.

Onderzoek:

- Opent de backend zonder login?
- Welke configuratieregel veroorzaakte de bypass?
- Waarom ziet Authentik geen deny-event?

### Scenario B: verkeerde external host

Wijzig in de monitoringprovider de external host naar een foutieve poort.

Onderzoek:

- Welke redirect, cookie- of providerfout ontstaat?
- Bereikt de request Traefik?
- Werkt `/outpost.goauthentik.io/ping` nog?

### Scenario C: application niet in outpost

Verwijder monitoring tijdelijk uit de embedded outpost.

Onderzoek:

- Welk symptoom ziet de gebruiker?
- Welke logbron wijst naar provider/outpost?
- Waarom helpt een wijziging aan de backend hier niet?

Rapporteer:

| Fout | Symptoom | Laag | Bewijs | Herstel |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

---

## 26. Typische fouten en hints

| Fout | Hint |
|---|---|
| hostname resolveert niet | controleer hosts file vóór Authentik |
| Authentik opent op verkeerde URL | controleer `auth.bluepeak.test:8100` en `authentik_host` |
| redirectloop | controleer outpostrouter, pad en prioriteit |
| 404 op outpostpad | controleer outpostservice en `PathPrefix` |
| app opent zonder login | controleer middleware op de app-router |
| iedereen krijgt toegang | controleer application binding |
| juiste groep krijgt deny | controleer groepslidmaatschap en outposttoewijzing |
| admin vraagt geen MFA | controleer authorization flow van adminprovider |
| gebruiker zonder TOTP komt door | controleer `Not configured action: Deny` |
| backendheader leeg | controleer `authResponseHeaders` |
| 502/503 | lokaliseer outpost of backend met logs |
| wijziging lijkt niet actief | controleer dashboard en herlaad provider/outpostconfig |

---

## 27. Productievertaling

Vul een minimale firewallmatrix in:

| Bron | Bestemming | Poort | Actie | Waarom |
|---|---|---:|---|---|
| Internet/clients | reverse proxy | 443 | ... | ... |
| Internet/clients | Authentik core rechtstreeks | any | ... | ... |
| Internet/clients | appbackends | any | ... | ... |
| reverse proxy | Authentik/outpost | 9000/9443 | ... | ... |
| reverse proxy | goedgekeurde backends | apppoort | ... | ... |
| reverse proxy | managementzone | any | ... | ... |

Noteer daarnaast minstens vijf productieverbeteringen tegenover het lab.

Denk aan:

- TLS;
- certificaten en DNS;
- high availability;
- dashboardbescherming;
- patchbeleid;
- trusted proxyheaders;
- sessiebeleid;
- MFA-herstel;
- logging en privacy;
- noodtoegang.

---

## 28. Reflectievragen

Beantwoord kort maar technisch onderbouwd:

1. Waarom is een toegelaten VPN-subnet geen bewijs dat de juiste gebruiker een
   applicatie opent?
2. Waarom past single-application forward auth beter bij deze accessmatrix dan één
   domain-level provider?
3. Waarom is een geregistreerd TOTP-device op zichzelf geen bewijs van step-up MFA?
4. Onder welke voorwaarden mag een backend `X-authentik-username` vertrouwen?
5. Waarom is de afwezigheid van een Authentik-event nuttig bewijs wanneer een
   middleware per ongeluk ontbreekt?
6. Welke beschikbaarheidsmaatregelen worden belangrijker zodra meerdere applicaties
   van één identity provider afhangen?
7. Welke autorisatie moet de backendapplicatie zelf nog uitvoeren nadat forward auth
   toegang gaf?

---

## 29. Mogelijke uitbreidingen

Wanneer er tijd over is, kies één uitbreiding:

- ontwerp een domain-level alternatief en noteer welke policies je daardoor niet meer
  per applicatie kan afdwingen;
- voeg lokaal TLS toe en onderzoek de impact op external hosts, cookies en redirects;
- ontwerp een einddatum- en reviewpolicy voor `bp-partners`;
- maak een HA-schema voor Traefik, Authentik en PostgreSQL;
- voeg een extra finance-app toe met `bp-finance` en step-up MFA;
- ontwerp monitoringregels voor een stijging van login failures, policy denies en
  forward-authfouten.

Documenteer bij elke uitbreiding het doel, de wijziging, positieve en negatieve tests
en het resterende risico.

---

## 30. Opruimen

Stop de omgeving zonder volumes te verwijderen:

```text
docker compose down
```

Verwijder volumes alleen wanneer je docent dit vraagt en je de labdata niet meer
nodig hebt.

Verwijder na de workshop indien gevraagd:

- tijdelijke hosts-filevermeldingen;
- het lokale lab-TOTP-device;
- tijdelijke groepslidmaatschappen;
- je lokale `.env` wanneer het lab definitief klaar is.

---

## 31. In te dienen

Lever een kort technisch dossier in met:

1. finale `traefik/dynamic.yml`;
2. architectuurschema met browser, Traefik, outpost, Authentik core en backends;
3. application-, provider-, hostname- en groepsmatrix;
4. positieve en negatieve testmatrix voor Alice, Bob en Eva;
5. bewijs van step-up MFA zonder QR-code, seed of TOTP-code;
6. bewijs dat de publieke route zonder login werkt;
7. bewijs dat backendpoorten niet rechtstreeks gepubliceerd zijn;
8. header-spoofingtest;
9. fail-closedtest;
10. gecorreleerde log- en eventanalyse;
11. één foutscenario met methodische analyse;
12. firewallmatrix en productieverbeteringen;
13. eindreflectie.

Neem niet op:

- `.env`;
- wachtwoorden;
- cookies;
- tokens;
- volledige gevoelige headers;
- TOTP-seed, QR-code of herstelcodes;
- interne gegevens uit een echte organisatie.

---

## 32. Eindvraag

Sluit af met een onderbouwd antwoord op:

> Is identity-aware access via Traefik en Authentik een vervanging voor VPN?

Betrek minstens:

- netwerktoegang versus applicatietoegang;
- webprotocollen versus andere protocollen;
- groepsbeleid en MFA;
- backendisolatie en firewalling;
- de IdP als kritieke afhankelijkheid;
- één realistisch scenario waarin beide oplossingen naast elkaar nodig zijn.
