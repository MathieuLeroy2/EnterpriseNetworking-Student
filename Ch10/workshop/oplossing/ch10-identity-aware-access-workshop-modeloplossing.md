# Workshop 10 - Identity-aware access met Traefik en Authentik

## Modeloplossing voor studenten

## 1. Korte samenvatting

De oplossing publiceert vijf interne applicaties via Traefik.

```text
public      -> zonder login
intranet    -> bp-employees
monitoring  -> bp-it
admin       -> bp-it-admins + TOTP step-up
partner     -> bp-partners
```

Traefik raadpleegt voor de vier beschermde routes de embedded Authentik-outpost via
forward auth.

De backends hebben geen hostpoorten.

De allow- en deny-tests, header-spoofingtest en fail-closedtest tonen samen aan dat de
bedoelde policy wordt afgedwongen.

---

## 2. Architectuur

```text
client
  |
  v
Traefik :8100
  |-- public -------------------------------------> public backend
  |
  |-- protected request
        |
        +--> embedded Authentik-outpost
                |-- geen sessie: loginredirect
                |-- verkeerde groep/policy: deny
                +-- allow: identity-headers
                         |
                         v
                    gekozen backend
```

Rolverdeling:

| Component | Verantwoordelijkheid |
|---|---|
| Traefik | host-based routing en middlewareketen |
| Authentik core | gebruikers, groepen, flows, bindings en events |
| embedded outpost | forward-authbeslissing en providersessie |
| backend | applicatie-inhoud en ontvangen identity-context |

---

## 3. Finale Traefik-configuratie

```yaml
http:
  routers:
    authentik:
      rule: "Host(`auth.bluepeak.test`)"
      entryPoints: [web]
      service: authentik
      middlewares: [security-headers]

    public:
      rule: "Host(`public.bluepeak.test`)"
      entryPoints: [web]
      service: public
      middlewares: [security-headers]

    protected-outpost:
      rule: "(Host(`intranet.bluepeak.test`) || Host(`monitoring.bluepeak.test`) || Host(`admin.bluepeak.test`) || Host(`partner.bluepeak.test`)) && PathPrefix(`/outpost.goauthentik.io/`)"
      entryPoints: [web]
      priority: 100
      service: authentik-outpost

    intranet:
      rule: "Host(`intranet.bluepeak.test`)"
      entryPoints: [web]
      service: intranet
      middlewares: [authentik-forward, security-headers]

    monitoring:
      rule: "Host(`monitoring.bluepeak.test`)"
      entryPoints: [web]
      service: monitoring
      middlewares: [authentik-forward, security-headers]

    admin:
      rule: "Host(`admin.bluepeak.test`)"
      entryPoints: [web]
      service: admin
      middlewares: [authentik-forward, security-headers]

    partner:
      rule: "Host(`partner.bluepeak.test`)"
      entryPoints: [web]
      service: partner
      middlewares: [authentik-forward, security-headers]

  services:
    authentik:
      loadBalancer:
        servers:
          - url: "http://server:9000"
    authentik-outpost:
      loadBalancer:
        servers:
          - url: "http://server:9000/outpost.goauthentik.io"
    public:
      loadBalancer:
        servers:
          - url: "http://public:8080"
    intranet:
      loadBalancer:
        servers:
          - url: "http://intranet:8080"
    monitoring:
      loadBalancer:
        servers:
          - url: "http://monitoring:8080"
    admin:
      loadBalancer:
        servers:
          - url: "http://admin:8080"
    partner:
      loadBalancer:
        servers:
          - url: "http://partner:8080"

  middlewares:
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
    security-headers:
      headers:
        contentTypeNosniff: true
        frameDeny: true
        referrerPolicy: "strict-origin-when-cross-origin"
```

Belangrijk:

- de outpostrouter heeft hogere prioriteit;
- de outpostrouter heeft zelf geen forward-authmiddleware;
- de publieke router heeft geen forward-authmiddleware;
- alle protected routers hebben die middleware wel;
- elke backend gebruikt alleen een interne Docker-URL.

---

## 4. Authentik-host en embedded outpost

De embedded outpost gebruikt:

```text
authentik_host = http://auth.bluepeak.test:8100
```

Toegewezen applications:

```text
BluePeak Intranet
BluePeak Monitoring
BluePeak Admin
BluePeak Partner Portal
```

De publieke statuspagina staat niet in de outpost.

Verwachte healthtest:

```text
curl.exe -i http://intranet.bluepeak.test:8100/outpost.goauthentik.io/ping
```

Resultaat:

```text
HTTP 204 No Content
```

De precieze HTTP-versieregel kan verschillen, maar er mag geen 404 of redirectloop
ontstaan.

---

## 5. Gebruikers en groepen

| Gebruiker | Groepen |
|---|---|
| Alice Vermeulen | `bp-employees` |
| Bob Peeters | `bp-employees`, `bp-it`, `bp-it-admins` |
| Eva Partner | `bp-partners` |

Bob heeft een bevestigd TOTP-device.

Geen van deze groepen geeft beheerrechten in Authentik.

---

## 6. Applications, providers en bindings

| Application | Slug | Provider mode | External host | Binding |
|---|---|---|---|---|
| BluePeak Intranet | `bluepeak-intranet` | forward auth single app | `http://intranet.bluepeak.test:8100` | `bp-employees` |
| BluePeak Monitoring | `bluepeak-monitoring` | forward auth single app | `http://monitoring.bluepeak.test:8100` | `bp-it` |
| BluePeak Admin | `bluepeak-admin` | forward auth single app | `http://admin.bluepeak.test:8100` | `bp-it-admins` |
| BluePeak Partner Portal | `bluepeak-partner` | forward auth single app | `http://partner.bluepeak.test:8100` | `bp-partners` |

De eerste, tweede en vierde provider gebruiken de standaard implicit-consent
authorization flow.

De adminprovider gebruikt:

```text
bluepeak-admin-step-up
```

---

## 7. Step-up-MFA-flow

De geïmporteerde blueprint maakt:

```yaml
designation: authorization
authentication: require_authenticated
```

met een Authenticator Validation stage:

```yaml
device_classes:
  - totp
not_configured_action: deny
last_auth_threshold: seconds=0
```

Betekenis:

- de gebruiker moet al centraal aangemeld zijn;
- de flow valideert een bevestigd TOTP-device;
- zonder compatibel device stopt de flow;
- alleen groepslidmaatschap is dus niet voldoende;
- een bestaande SSO-sessie zonder deze step-up geeft geen admintoegang.

---

## 8. Verwachte accessmatrix

| Identiteit | Public | Intranet | Monitoring | Admin | Partner |
|---|---|---|---|---|---|
| anoniem | allow | loginredirect | loginredirect | loginredirect | loginredirect |
| Alice | allow | allow | deny | deny | deny |
| Bob | allow | allow | allow | allow na TOTP | deny |
| Eva | allow | deny | deny | deny | allow |

Sterke conclusie:

> Authenticated is niet automatisch authorized. Eva kan centraal aanmelden, maar haar
> `bp-partners`-lidmaatschap geeft alleen toegang tot het partnerportaal.

---

## 9. Identity-headers

Na toegelaten toegang toont de demoapp bijvoorbeeld:

| Header | Verwachte inhoud |
|---|---|
| `X-Authentik-Username` | centrale username |
| `X-Authentik-Groups` | relevante groepslijst |
| `X-Authentik-Email` | centraal e-mailadres |
| `X-Authentik-Meta-App` | slug van de gekoppelde application |

Op de publieke route zijn deze headers niet aanwezig.

De headers zijn alleen betrouwbaar omdat:

- de backends niet rechtstreeks gepubliceerd zijn;
- clients eerst Traefik bereiken;
- de forward-authmiddleware de identiteit laat bevestigen;
- alleen de interne proxy-backendroute gebruikt wordt.

Een productieapp moet deze vertrouwensgrens nog expliciet hardenen.

---

## 10. Header-spoofingtest

Test zonder geldige sessie:

```text
curl.exe -i -H "X-authentik-username: akadmin" http://admin.bluepeak.test:8100
```

Verwacht:

- redirect naar login of deny;
- geen inhoud van de adminbackend;
- de clientheader bewijst geen identiteit.

Conclusie:

> Een door de client gekozen header vervangt geen door Authentik bevestigde sessie en
> policybeslissing.

---

## 11. Negatieve backendtests

```text
curl.exe -I http://localhost:8101
curl.exe -I http://localhost:8102
curl.exe -I http://localhost:8103
curl.exe -I http://localhost:8104
```

Alle tests falen.

`docker compose ps` toont geen hostpoorten voor `public`, `intranet`, `monitoring`,
`admin` of `partner`.

Alleen Traefik publiceert:

```text
8100:80
8188:8080
```

---

## 12. SSO en logout

Bob meldt zich één keer centraal aan via intranet.

Wanneer Bob monitoring opent, kan Authentik de bestaande centrale sessie herkennen.

Providerlogout via:

```text
http://monitoring.bluepeak.test:8100/outpost.goauthentik.io/sign_out
```

beëindigt de relevante providersessie, maar niet noodzakelijk:

- de centrale Authentik-sessie;
- de intranetprovidersessie;
- een eventuele eigen backendsessie.

Daarom kan een volgende toegang door SSO opnieuw snel worden toegestaan.

---

## 13. Fail-closedtest

Na:

```text
docker compose stop server
```

blijft de publieke route werken, omdat ze geen forward auth gebruikt.

Een nieuwe protected request krijgt geen backendinhoud, omdat Traefik geen geldige
authenticatiebeslissing ontvangt.

Na:

```text
docker compose start server
```

en het gereedkomen van Authentik werken de protected routes opnieuw.

Conclusie:

> Fail-closed beschermt de applicatie, maar maakt de IdP tegelijk een kritieke
> beschikbaarheidsafhankelijkheid.

---

## 14. Logcorrelatie

| Bron | Bewijst vooral |
|---|---|
| Traefik accesslog | hostname, request, status en proxygedrag |
| Authentik events/serverlog | gebruiker, provider, flow, MFA en policyresultaat |
| backendpagina/backendlog | doorgestuurde identity-context na allow |

Bij een monitoringdeny voor Alice:

- Traefik toont dat de request het centrale toegangspunt bereikte;
- Authentik verklaart dat de application binding niet slaagde;
- de monitoringbackend hoort geen normale applicatierequest te verwerken.

---

## 15. Foutscenario: middleware ontbreekt

Wanneer `authentik-forward` tijdelijk van de monitoringrouter wordt verwijderd:

- Traefik stuurt rechtstreeks naar monitoring;
- de pagina opent zonder Authentik-login;
- identity-headers ontbreken;
- Authentik heeft geen bijbehorend access-denyevent;
- andere routes blijven beschermd.

Herstel:

```yaml
middlewares:
  - authentik-forward
  - security-headers
```

De hertest bevat daarna zowel Bob allow als Alice deny.

---

## 16. Firewallvoorstel voor productie

| Bron | Bestemming | Poort | Actie | Reden |
|---|---|---:|---|---|
| clients | reverse proxy | 443 | allow | centraal HTTPS-punt |
| clients | appbackends | any | deny | proxy niet omzeilen |
| clients | Authentik intern beheer | any | deny | management afschermen |
| reverse proxy | Authentik/outpost | 9000/9443 of gekozen TLS-poort | allow | forward-authcontrole |
| reverse proxy | goedgekeurde appbackends | expliciete apppoort | allow | noodzakelijke flows |
| reverse proxy | overige interne zones | any | deny | least privilege |

Aanvullende productieverbeteringen:

- HTTPS en geldige certificaten;
- beschermd Traefik-dashboard;
- redundante Authentik- en databasecomponenten;
- patch- en releasebeheer;
- trusted proxyheaderconfiguratie;
- passende sessieduur en intrekking;
- MFA-herstelprocedure;
- centrale monitoring en alerting;
- geteste back-up en restore;
- periodieke access review.

---

## 17. Eindantwoord: vervangt dit VPN?

Nee.

Identity-aware access beschermt specifieke webapplicaties op basis van gebruiker,
groep, flow en MFA zonder een breed netwerkpad aan de client te geven.

Een VPN is wel geschikt om een beveiligd netwerkpad te maken voor bijvoorbeeld SSH,
RDP, beheerprotocollen of meerdere interne diensten.

Beide oplossingen hebben nog steeds firewalling, TLS, backendisolatie, logging en
applicatie-eigen autorisatie nodig.

Realistisch gecombineerd ontwerp:

- medewerkers openen intranet en helpdesk via identity-aware HTTPS;
- partners krijgen alleen het partnerportaal;
- beheerders gebruiken VPN naar een jump server voor toestelbeheer;
- het adminwebportaal vereist daarnaast `bp-it-admins` en step-up MFA.

Eindzin:

> De reverse proxy bepaalt het applicatiepad, Authentik bevestigt identiteit en
> toegang, de firewall bewaakt de netwerkgrenzen en VPN blijft nodig waar gecontroleerde
> netwerktoegang in plaats van alleen webapplicatietoegang vereist is.

---

## 18. Antwoorden op de vragen uit de studentenversie

Deze sectie geeft de verwachte inhoud van de antwoorden. Concrete waarden zoals
tijdstippen, HTTP-versies en logregels mogen in een verslag verschillen, zolang de
redenering en het securityresultaat overeenkomen.

### Voorbereiding en initialisatie

De groepen en gebruikers worden niet vóór de start aangemaakt. Authentik is dan nog
niet geïnitialiseerd en de Admin interface is nog niet beschikbaar. Sectie 6 is dus
alleen het gewenste model; de feitelijke aanmaak gebeurt in stap 5, nadat de lokale
`akadmin`-beheerder is aangemaakt.

Browserredirects gebruiken `auth.bluepeak.test` omdat dit de URL is die de browser
moet kunnen resolven en die als externe Authentik-host aan cookies, redirects en
providers wordt doorgegeven. De Docker-servicenaam `server` is alleen intern geldig
op het Compose-netwerk en is niet door de browser bereikbaar. Traefik gebruikt
`http://server:9000` omdat Traefik zelf in dat Docker-netwerk zit en Authentik daar
rechtstreeks kan bereiken.

De verwachte servicematrix is:

| Service | Laag | Hostpoort? | Waarom? |
|---|---|---|---|
| `postgresql` | database | nee | alleen Authentik moet de database bereiken |
| `server` | identity provider | nee | via Traefik, niet rechtstreeks |
| `worker` | Authentik achtergrondtaken | nee | intern ondersteunend proces |
| `reverse-proxy` | edge/reverse proxy | ja | enig publiek toegangspunt |
| `public` | applicatiebackend | nee | publiek via Traefik |
| `intranet` | applicatiebackend | nee | beschermd via Traefik en Authentik |
| `monitoring` | applicatiebackend | nee | beschermd via Traefik en Authentik |
| `admin` | applicatiebackend | nee | beschermd via groep en step-up MFA |
| `partner` | applicatiebackend | nee | beschermd via partnergroep |

Bij de publieke route verwacht je: pagina bereikbaar zonder login, naam `Public
status`, geen Authentik-identityheaders en geen eigen backend-hostpoort. De vier
onderdelen die hostname en backend verbinden zijn:

```text
router rule -> router service -> load-balancer URL -> interne backendpoort
```

### Forward auth en outpost

Traefik stuurt de controle naar:

```text
http://server:9000/outpost.goauthentik.io/auth/traefik
```

Dit is de embedded Authentik-outpost, niet de backend-URL. De outpost beslist of de
request mag doorgaan en handelt login, sessie en providerbeleid af. De backend mag
pas na een positieve controle headers ontvangen zoals `X-authentik-username`,
`X-authentik-groups`, `X-authentik-email`, `X-authentik-name`, `X-authentik-uid`,
`X-authentik-meta-app` en `X-authentik-meta-provider`.

Prioriteit `100` is nodig omdat het speciale outpostpad anders door de algemene
hostname-router kan worden afgehandeld. De outpostrouter moet vóór de beschermde
applicatierouter matchen; anders bereikt het health-, callback- of sign-outpad niet
de outpost correct. De outpostrouter krijgt zelf geen forward-authmiddleware, want
dat zou een lus veroorzaken.

Wanneer het intranet vóór de Authentik-application wordt getest, is een redirect,
deny of foutmelding verwacht. De middleware werkt technisch, maar Authentik kan nog
geen passende provider/application vinden. Dit is dus een bewuste tussenfase en geen
bewijs dat de backend defect is.

### Positieve en negatieve toegangsproeven

De verwachte resultaten zijn:

| Test | Verwacht resultaat | Verklaring |
|---|---|---|
| Alice naar intranet | allow | Alice is lid van `bp-employees` |
| Eva naar intranet | deny | Eva heeft alleen `bp-partners` |
| anoniem naar intranet | redirect naar login | er is nog geen geldige sessie |
| Bob naar monitoring | allow | Bob is lid van `bp-it` |
| Alice naar monitoring | deny | Alice is geen lid van `bp-it` |
| Eva naar partner | allow | Eva is lid van `bp-partners` |
| Bob naar partner | deny | Bob is geen lid van `bp-partners` |

Een geldige login bewijst dus alleen authenticatie. De application binding bepaalt
daarna of die identiteit voor de concrete applicatie geautoriseerd is.

### Step-up-MFA

De flow heeft designation `authorization`. De toegelaten deviceclass is `totp`.
Door `not_configured_action: deny` wordt een gebruiker zonder geconfigureerd en
bevestigd TOTP-device geweigerd. Een wachtwoord, groepslidmaatschap of bestaande SSO-
sessie alleen volstaat niet.

Het blueprintbestand bevat geen wachtwoorden of TOTP-seeds omdat dit configuratie-
en policy-informatie is, geen gebruikersdata. Secrets horen lokaal en buiten versie-
beheer te worden aangemaakt. In het bijzonder mag een TOTP-seed nooit in een
blueprint, verslag of Git-repository terechtkomen.

De verwachte MFA-tabel is:

| Test | Verwacht resultaat |
|---|---|
| Bob opent intranet | allow |
| Bob opent admin met alleen bestaande SSO-sessie | extra MFA-stap |
| foute TOTP | authorization flow niet voltooid, geen admininhoud |
| geldige TOTP | allow |
| Alice tijdelijk in `bp-it-admins`, zonder TOTP | deny |

### SSO, logout en sessies

Een mogelijke correcte sessiematrix is:

| Actie | Centrale sessie | Intranettoegang | Monitoringtoegang |
|---|---|---|---|
| vóór providerlogout | actief | allow | allow |
| na monitoringproviderlogout | meestal actief | allow | nieuwe controle of login |
| na volledige Authentik-logout | beëindigd | nieuwe login nodig | nieuwe login nodig |

Providerlogout beëindigt in eerste instantie de sessie die bij die provider hoort;
het beëindigt niet noodzakelijk de centrale Authentik-sessie of een andere
providersessie. SSO kan daarna opnieuw snel toegang geven omdat Authentik de centrale
sessie nog kent. Accountdeactivatie en sessie-intrekking zijn verschillende acties:
een gedeactiveerd account kan nog bestaande sessies hebben totdat die verlopen of
expliciet worden ingetrokken. Productie vereist daarom een duidelijk intrekkings-
en offboardingproces.

### Spoofing, backendisolatie en fail-closed

Een zelfgekozen `X-authentik-username` geeft geen toegang. Traefik voert eerst de
forward-authcontrole uit; zonder geldige Authentik-sessie volgt redirect of deny en
bereikt de request de adminbackend niet.

De requests naar `localhost:8101` tot en met `localhost:8104` falen omdat de
backends geen hostpoorten publiceren. Dit verhindert dat een client Traefik,
Authentik of de groepspolicy omzeilt.

Bij `docker compose stop server` blijft `public` werken, maar een nieuwe protected
request faalt gesloten en toont geen backendinhoud. Fail-open zou bij een storing in
de identity provider juist toegang kunnen geven zonder actuele authenticatie of
autorisatie; dat is onaanvaardbaar voor beschermde applicaties. De keerzijde is dat
de IdP een beschikbaarheidsafhankelijkheid wordt. Productie vereist daarom onder
andere redundante Authentik- en databasecomponenten, monitoring en alerting,
back-ups en restoretests, capaciteit, gecontroleerd onderhoud en een geteste
noodtoegangsprocedure.

### Logs en foutscenario's

De drie logbronnen hebben elk een andere rol:

| Bron | Antwoord op de vraag |
|---|---|
| Traefik accesslog | toont request, hostname, route en HTTP-status |
| Authentik Events/ serverlog | verklaart gebruiker, application, flow, groep, MFA en deny/allow |
| backendpagina of backendlog | toont de identityheaders die na allow ontvangen zijn |

Je hebt ze samen nodig om te onderscheiden tussen een routingprobleem, een
identity/policybeslissing en een backendprobleem. Geen Authentik-event bij een
middlewarebypass is zelf betekenisvol: Authentik werd dan niet geraadpleegd.

Verwachte foutscenario's:

| Scenario | Symptoom | Laag | Bewijs | Herstel |
|---|---|---|---|---|
| middleware verwijderd | monitoring opent zonder login en zonder identityheaders | Traefik-router | routerconfig en accesslog; geen Authentik-deny-event | `authentik-forward` terugplaatsen |
| verkeerde external host | redirect-, cookie- of callbackfout; request kan Traefik wel bereiken | Authentik provider/URL | browserfout, providerconfig en serverlog | juiste external host herstellen |
| application niet in outpost | login/provider werkt niet correct of request wordt geweigerd | outpost/applicationkoppeling | Authentik- en outpostlog; backend is gezond | application opnieuw aan outpost toevoegen |

Een wijziging aan de backend helpt in de laatste twee scenario’s niet, omdat de
fout vóór de backend ligt.

### Productievertaling

De ingevulde firewallmatrix is:

| Bron | Bestemming | Poort | Actie | Waarom |
|---|---|---:|---|---|
| Internet/clients | reverse proxy | 443 | allow | centraal HTTPS-toegangspunt |
| Internet/clients | Authentik core rechtstreeks | any | deny | IdP alleen via bedoeld publicatiepad |
| Internet/clients | appbackends | any | deny | proxy niet omzeilen |
| reverse proxy | Authentik/outpost | 9000/9443 | allow | forward-authcontrole |
| reverse proxy | goedgekeurde backends | apppoort | allow | noodzakelijke proxyflow |
| reverse proxy | managementzone | any | deny | least privilege en segmentatie |

Minstens vijf noodzakelijke verbeteringen zijn TLS met certificaatbeheer, beschermd
Traefik-dashboard, HA voor Traefik/Authentik/PostgreSQL, patch- en releasebeheer,
trusted-proxyheaderconfiguratie, sessie-intrekking, MFA-herstel, centrale logging,
back-up/restore en periodieke access reviews.

### Antwoorden op de reflectievragen

1. Een VPN-subnet bewijst alleen dat een netwerkpad is toegestaan. Het bewijst niet
   welke gebruiker de browser gebruikt, tot welke groep die gebruiker behoort of
   welke applicatie geopend wordt.
2. Single-application forward auth koppelt elke hostname aan een eigen provider en
   binding. Daardoor kan intranet `bp-employees`, monitoring `bp-it`, admin
   `bp-it-admins` plus MFA en partner `bp-partners` afdwingen. Eén domain-level
   provider maakt die per-applicatieverschillen minder expliciet en moeilijker te
   beheren.
3. Een geregistreerd device toont alleen dat een factor beschikbaar is. Step-up
   MFA is pas bewezen wanneer de authorizationflow het device tijdens de gevoelige
   aanvraag werkelijk valideert.
4. Alleen wanneer de backend uitsluitend via een vertrouwde proxy bereikbaar is,
   de proxy inkomende clientheaders overschrijft/verwijdert, forward auth succesvol
   is en de verbinding tussen proxy en backend beschermd en gecontroleerd is.
5. Zonder middleware wordt Authentik niet aangeroepen. Het ontbreken van een event
   ondersteunt daarom de conclusie dat de bypass in Traefik-routing zit, niet in een
   Authentik-policy.
6. Redundantie, healthchecks, capaciteitsplanning, databaseback-ups, restoretests,
   monitoring, alerting, onderhoudsprocedures en noodtoegang worden belangrijker.
7. Forward auth bewijst centrale toegang tot de route; de backend moet zelf nog
   object- en functierechten controleren, zoals eigenaar, recordniveau, tenant,
   bewerkingstype en eventueel extra bedrijfsregels.
