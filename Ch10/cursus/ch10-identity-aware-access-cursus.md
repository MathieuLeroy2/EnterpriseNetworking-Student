# Hoofdstuk 10 - Identity-aware access met Traefik en Authentik

## 1. Inleiding

In hoofdstuk 8 publiceerden we interne webapplicaties via Traefik.

De reverse proxy kon toen technische keuzes maken over het webverkeer:

| Vraag | Antwoord van de reverse proxy |
|---|---|
| Welke applicatie vraagt de client? | de hostname matcht met een router |
| Waar draait die applicatie? | een service verwijst naar de interne backend |
| Welke poort is publiek bereikbaar? | alleen de proxy publiceert een hostpoort |
| Welke extra verwerking gebeurt? | middleware kan bijvoorbeeld headers toevoegen |
| Waar liep een request fout? | accesslogs en statuscodes geven een eerste aanwijzing |

De reverse proxy wist echter nog niet betrouwbaar **wie** de gebruiker was.

In hoofdstuk 9 voegden we daarom centrale identiteit toe met Authentik. Daar lag de
nadruk op een applicatie die zelf OpenID Connect ondersteunde.

| Identityvraag | Antwoord uit hoofdstuk 9 |
|---|---|
| Wie is de gebruiker? | Authentik voert de centrale authenticatie uit |
| Tot welke groepen behoort de gebruiker? | groepen en claims leveren identitycontext |
| Mag de gebruiker de application openen? | een application binding of policy beslist |
| Is MFA gevalideerd? | de actieve flow bepaalt of een tweede factor nodig is |
| Kan de beslissing onderzocht worden? | Authentik-events en applicatielogs leveren bewijs |

Niet elke bestaande applicatie ondersteunt OIDC of SAML. Veel organisaties hebben
legacywebapps, dashboards, beheerinterfaces en kleine interne tools die alleen HTTP
spreken en zelf geen moderne SSO-koppeling aanbieden.

In dit hoofdstuk brengen we daarom de twee voorgaande bouwstenen samen:

```text
hoofdstuk 8: hostname -> reverse proxy -> interne backend
hoofdstuk 9: gebruiker -> identity provider -> centrale identitybeslissing

hoofdstuk 10:
hostname -> reverse proxy -> identitycontrole -> toegelaten backend
```

De centrale vraag wordt:

> Hoe laat een reverse proxy alleen verkeer door wanneer Authentik bevestigt dat de
> gebruiker voor die specifieke applicatie geauthenticeerd en geautoriseerd is?

Dit noemen we in dit hoofdstuk **identity-aware access**.

Kernidee:

> Bereikbaarheid, identiteit en autorisatie zijn drie verschillende voorwaarden. Een
> veilige publicatie werkt pas wanneer alle drie bewust ontworpen en getest zijn.

De workshop maakt die keten zichtbaar met een publieke applicatie, verschillende
beschermde applicaties, groepsbindings, step-up MFA, identity-headers en zowel
positieve als negatieve tests.

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. netwerktoegang en applicatietoegang van elkaar onderscheiden;
2. uitleggen welk probleem identity-aware access oplost en welke problemen niet;
3. de rollen van Traefik, Authentik core, proxy provider, application, binding,
   outpost en backend beschrijven;
4. forward auth stap voor stap uitleggen voor een anonieme, toegelaten en geweigerde
   gebruiker;
5. publieke en beschermde applicatieroutes ontwerpen;
6. single-application en domain-level forward auth vergelijken;
7. uitleggen waarom het speciale outpostpad afzonderlijk gerouteerd wordt;
8. een applicatiematrix vertalen naar groepen, bindings, providers en proxyregels;
9. groepsgebaseerde toegang volgens least privilege ontwerpen en testen;
10. step-up MFA voor een gevoelige applicatie uitleggen;
11. het verschil aantonen tussen MFA registreren, MFA valideren en een recente
    MFA-validatie hergebruiken;
12. identity-headers correct plaatsen en de vertrouwensgrens rond die headers
    uitleggen;
13. SSO-, provider- en applicatiesessies van elkaar onderscheiden;
14. reverse-proxylogs, Authentik-events en backendobservaties correleren;
15. fail-closedgedrag en de IdP als kritieke afhankelijkheid analyseren;
16. een identity-aware omgeving methodisch troubleshooten;
17. uitleggen waarom identity-aware access geen volledige vervanging is voor VPN,
    firewalling, TLS of applicatie-autorisatie;
18. een test- en productieplan voor identity-aware webtoegang verantwoorden.

---

## 3. Van bereikbaarheid naar identiteit

### Netwerktoegang beantwoordt niet elke vraag

Een klassieke firewallregel kijkt bijvoorbeeld naar:

| Veld | Voorbeeld |
|---|---|
| Bron | VPN-subnet `10.60.0.0/24` |
| Bestemming | monitoringserver `10.30.20.15` |
| Protocol | TCP |
| Poort | 443 |
| Actie | allow |

Die regel kan een netwerkpad toelaten, maar zegt niet welke menselijke gebruiker de
monitoringapplicatie opent.

Dat verschil is belangrijk in enterpriseomgevingen:

| Situatie | Waarom een IP-adres onvoldoende identiteit bewijst |
|---|---|
| NAT | meerdere gebruikers verschijnen met hetzelfde publieke bronadres |
| VPN-subnet | verschillende VPN-gebruikers krijgen adressen uit dezelfde pool |
| gedeeld toestel | meerdere personen gebruiken hetzelfde endpoint |
| proxy | de backend ziet mogelijk vooral het adres van de proxy |
| dynamische adressen | een IP-adres hoort niet permanent bij dezelfde persoon |
| gecompromitteerd toestel | een toegelaten toestel kan door een aanvaller gebruikt worden |

Een bron-IP kan nog steeds nuttige context zijn. Het kan bijvoorbeeld aanduiden dat
verkeer uit een beheernetwerk of VPN komt. Het is alleen geen volledig bewijs van een
menselijke identiteit.

### Drie opeenvolgende vragen

Een identity-aware publicatie maakt drie vragen expliciet:

```text
1. Bereikbaarheid
   Kan de client het centrale toegangspunt bereiken?

2. Authenticatie
   Welke gebruiker is dit en hoe werd die identiteit bewezen?

3. Autorisatie
   Mag deze gebruiker deze specifieke applicatie openen?
```

Voorbeeld:

```text
Alice bereikt Traefik.                    -> netwerkpad werkt
Alice meldt zich correct aan bij Authentik. -> authenticatie slaagt
Alice zit niet in bp-it.                  -> monitoring wordt geweigerd
```

De eerste twee stappen kunnen dus slagen terwijl de derde stap correct faalt.

### Wat voegt identity-aware access toe?

| Extra beslissing | Praktische betekenis |
|---|---|
| account actief | een gedeactiveerde identiteit mag geen nieuwe toegang starten |
| groepslidmaatschap | toegang volgt uit functie of zakelijke behoefte |
| toepassingscontext | intranet, monitoring en admin krijgen niet automatisch hetzelfde beleid |
| MFA-context | een gevoelige applicatie kan extra verificatie eisen |
| sessiestatus | een verlopen of ingetrokken sessie moet opnieuw gecontroleerd worden |
| auditcontext | gebruiker, applicatie en policybeslissing kunnen achteraf gecorreleerd worden |

### Wat lost dit niet op?

Identity-aware access is geen universele beveiligingslaag.

| Resterend probleem | Waarom blijft een andere maatregel nodig? |
|---|---|
| kwetsbare backendsoftware | authenticatie patcht geen applicatiekwetsbaarheden |
| rechten binnen de applicatie | de app moet nog bepalen wie tickets mag wissen of instellingen wijzigen |
| niet-webprotocollen | forward auth voor HTTP beschermt niet automatisch SSH, RDP of databaseverkeer |
| malware op een aangemeld toestel | een geldige sessie kan op een gecompromitteerd endpoint misbruikt worden |
| netwerksegmentatie | backends moeten nog steeds van directe clienttoegang afgeschermd worden |
| transportbeveiliging | credentials en cookies hebben TLS nodig |

Controleer:

- Kan een gebruiker de proxy bereiken maar toch correct geweigerd worden?
- Kan een toegelaten netwerkadres zonder geldige identiteit de backend openen?
- Is duidelijk welke beslissing door de firewall, proxy, IdP en applicatie genomen
  wordt?

Kernzin:

> Netwerktoegang bepaalt of verkeer een pad krijgt. Identity-aware access bepaalt of
> een geïdentificeerde gebruiker een specifieke applicatie mag openen.

---

## 4. Componenten in de architectuur

Een werkende omgeving bestaat niet uit één magisch authenticatiecomponent. Meerdere
onderdelen voeren elk een afgebakende taak uit.

De belangrijkste verwarring ontstaat meestal tussen deze drie onderdelen:

- **Traefik**;
- de Authentik **proxy provider**;
- de Authentik **proxy outpost**.

Ze bevatten alle drie het woord of concept "proxy", maar ze zijn niet hetzelfde.

Kernidee:

```text
Proxy provider = configuratie en regels
Proxy outpost  = uitvoerende Authentik-component
Traefik        = reverse proxy die het applicatieverkeer doorstuurt
```

De proxy provider is dus geen container en ontvangt zelf geen netwerkrequests.

De outpost is wel een actieve component. Hij gebruikt de providerconfiguratie om
authenticatie- en autorisatiecontroles uit te voeren.

Traefik blijft in forward-authmodus de component die de normale browserrequest naar de
uiteindelijke backend proxyt.

### Rollen en verantwoordelijkheden

| Component | Soort onderdeel | Waarvoor dient het? | Wat doet het niet? |
|---|---|---|---|
| Browser/client | actieve client | vraagt een hostname op, volgt redirects en bewaart sessiecookies | beslist niet zelf of toegang toegestaan is |
| DNS of hosts file | naamresolutie | laat de hostname naar het adres van Traefik verwijzen | kent geen gebruikers, groepen of applicatiebindings |
| Traefik-router | configuratie in Traefik | matcht hostname en eventueel pad | valideert zelf geen Authentik-gebruiker |
| Traefik forward-authmiddleware | configuratie in Traefik | stuurt vóór backendtoegang een afzonderlijke authcheck naar de outpost | beheert zelf geen gebruikers of Authentik-policies |
| Authentik core | actieve identityservice | beheert gebruikers, groepen, flows, applications, providers, bindings, sessies en events | proxyt in forward-authmodus niet de normale applicatie-inhoud |
| Authentik application | configuratieobject | stelt de logische applicatie voor en bevat onder meer presentatie en toegangsbindings | is niet de backendcontainer en luistert niet op de applicatiepoort |
| Authentik proxy provider | configuratieobject | beschrijft met welke proxymodus, externe URL en flows de application beschermd wordt | is geen proces, container of vervanging voor Traefik |
| Authentik proxy outpost | actieve runtimecomponent | laadt toegewezen proxyproviders en verwerkt de authchecks voor die providers | bepaalt niet zelf welke backend-URL Traefik na allow gebruikt |
| Backendapplicatie | actieve applicatieservice | levert inhoud en voert eventueel eigen autorisatie uit | mag willekeurige clientheaders niet automatisch als identiteit vertrouwen |

### Configuratieobject versus runtimecomponent

Dit onderscheid helpt om de proxy provider en outpost correct te begrijpen.

| Type | Voorbeeld | Wat betekent dit? |
|---|---|---|
| Configuratieobject | application of proxy provider | informatie die in Authentik opgeslagen en beheerd wordt |
| Runtimecomponent | Authentik core, outpost of Traefik | actief proces dat netwerkrequests verwerkt |

Vergelijk het met een routerconfiguratie:

```text
routing table = regels die beschrijven waar verkeer heen moet
router        = toestel of proces dat die regels uitvoert
```

Bij Authentik:

```text
proxy provider = regels die beschrijven hoe een app beschermd wordt
proxy outpost  = component die die regels tijdens requests uitvoert
```

De provider "draait" dus niet. De outpost draait en gebruikt de provider.

### De proxy provider in detail

Een **proxy provider** is een technisch configuratieobject in Authentik voor een
applicatie die via een proxypatroon beschermd wordt.

De provider beschrijft onder meer:

| Provideronderdeel | Vraag die het beantwoordt |
|---|---|
| Mode | werkt de outpost zelf als proxy, of gebruikt een bestaande reverse proxy forward auth? |
| External host | via welke exacte URL bereikt de browser de beschermde applicatie? |
| Authentication flow | hoe meldt een gebruiker zich aan wanneer nog geen geldige centrale sessie bestaat? |
| Authorization flow | welke controles of extra verificaties gebeuren vóór toegang tot deze application? |
| Invalidation flow | wat moet gebeuren wanneer de providersessie wordt beëindigd? |
| Providercontext | welke application, sessie en identityheaders horen bij deze koppeling? |

Voorbeeld voor monitoring:

```text
Application:        BluePeak Monitoring
Proxy provider:     BluePeak Monitoring Proxy
Mode:               Forward auth (single application)
External host:      http://monitoring.bluepeak.test:8100
Authentication:     standaard centrale authentication flow
Authorization:      standaard authorization flow
Applicationbinding: bp-it
```

Deze provider zegt dus conceptueel:

> Requests voor deze externe monitoring-URL horen bij BluePeak Monitoring. Gebruik
> forward auth, laat de gebruiker via deze flows controleren en pas de bindings van
> deze application toe.

De provider zegt niet:

```text
stuur toegelaten requests naar http://monitoring:8080
```

Die interne backend-URL staat in deze workshop in de **Traefik-serviceconfiguratie**.

Dit is een belangrijk grensvlak:

| Vraag | Waar geconfigureerd? |
|---|---|
| Welke gebruiker of groep mag de app openen? | Authentik application en bindings |
| Welke auth- en authorization flow wordt gebruikt? | Authentik proxy provider |
| Welke hostname matcht? | Traefik-router en provider external host moeten overeenkomen |
| Naar welke interne backend gaat een toegelaten request? | Traefik-service |

Typische fout:

> De provider bestaat, dus Authentik zal het verkeer vanzelf naar de
> monitoringcontainer sturen.

Dat klopt niet in forward-authmodus. Traefik blijft verantwoordelijk voor de
backendroutering.

### De proxy outpost in detail

Een **outpost** is een actieve Authentik-component die bepaalde providertypes buiten
of naast de centrale core uitvoert.

Voor een proxy provider verwerkt de outpost de requests die nodig zijn voor proxy- en
forward-authfunctionaliteit.

De outpost voert conceptueel deze taken uit:

| Taak | Wat gebeurt er concreet? |
|---|---|
| providerconfiguratie laden | de outpost kent alleen de applications/providers die eraan toegewezen zijn |
| requestcontext lezen | hostname, pad, scheme, cookies en forwarded context worden onderzocht |
| providersessie controleren | de outpost kijkt of voor deze provider geldige sessiecontext bestaat |
| authenticatie starten | zonder geschikte sessie wordt de browser naar de Authentik-flow geleid |
| autorisatie toepassen | application bindings en relevante policies bepalen allow of deny |
| identityheaders teruggeven | bij allow kan de outpost bevestigde gebruikerscontext leveren |
| technische outpostpaden afhandelen | loginstart, callback, logout en ping verlopen via `/outpost.goauthentik.io/` |

De outpost ontvangt in forward-authmodus twee soorten requests:

1. interne authchecks van Traefik;
2. browserrequests naar het speciale outpostpad.

Conceptueel:

```text
Traefik -> outpost auth endpoint
          "Mag deze request naar monitoring door?"

Browser -> monitoring.bluepeak.test/outpost.goauthentik.io/...
           "Start of voltooi login, callback of logout."
```

De outpost ontvangt niet automatisch elke byte van de normale monitoringpagina.

Bij een geslaagde forward-authcheck gebeurt dit:

```text
outpost -> Traefik: allow + bevestigde identityheaders
Traefik -> backend: oorspronkelijke applicatierequest + geselecteerde headers
```

Bij deny:

```text
outpost -> Traefik: deny
Traefik -X-> backend
```

De normale request hoort de backend dan niet te bereiken.

### Waarom bestaat de outpost als afzonderlijk concept?

Authentik gebruikt outposts voor providers die een actieve netwerkfunctie nodig
hebben, zoals proxy-, LDAP- of RADIUS-functionaliteit.

Dat maakt verschillende plaatsingen mogelijk:

| Plaatsing | Praktische reden |
|---|---|
| dicht bij de reverse proxy | korte en gecontroleerde authverbinding |
| in een specifieke netwerkzone | providerfunctie hoeft niet breed door firewalls bereikbaar te zijn |
| als afzonderlijke deployment | eigen lifecycle, capaciteit en schaalbaarheid |
| embedded in Authentik | eenvoudig voor een kleine installatie of workshop |

De outpost krijgt alleen de applications/providers toegewezen die hij moet bedienen.
Dat beperkt zijn functionele scope en maakt de koppeling expliciet.

Als de application niet aan de outpost is toegewezen, bestaan de application en
provider wel in Authentik, maar kan deze outpost de provider niet correct afhandelen.

### Application, provider en outpost samen

De drie Authentik-onderdelen vormen een keten:

```text
+--------------------------+
| Authentik application    |
| BluePeak Monitoring      |
| binding: bp-it           |
+------------+-------------+
             |
             | gebruikt
             v
+--------------------------+
| Authentik proxy provider |
| mode: forward_single     |
| external host: monitoring|
| auth- en authzflows       |
+------------+-------------+
             |
             | toegewezen aan
             v
+--------------------------+
| Proxy outpost            |
| actieve runtimecomponent |
| verwerkt authchecks      |
+------------+-------------+
             ^
             |
             | forward-authrequest
             |
+------------+-------------+
| Traefik middleware       |
+--------------------------+
```

Kort samengevat:

| Onderdeel | Mentale vraag |
|---|---|
| Application | welke logische app is dit en wie mag ze gebruiken? |
| Proxy provider | volgens welk proxypatroon en welke flows wordt ze beschermd? |
| Outpost | welke actieve Authentik-component voert die providercontrole uit? |
| Traefik | welke requests worden gecontroleerd en naar welke backend gaan ze na allow? |

### Volledige samenhang met Traefik

```text
Browser
   |
   | GET http://monitoring.bluepeak.test:8100/
   v
+--------------------+
| Traefik-router     |
| matcht hostname    |
+---------+----------+
          |
          | vóór backendtoegang
          v
+--------------------+       gebruikt       +-----------------------+
| forward-auth       |---------------------->| Authentik proxy       |
| middleware         |                       | outpost                |
+--------------------+                       +-----------+-----------+
                                                     |
                                                     | voert regels uit van
                                                     v
                                           +-------------------------+
                                           | proxy provider +        |
                                           | application bindings    |
                                           +-------------------------+
          |
          | alleen na allow
          v
+--------------------+
| Traefik-service    |
| monitoring:8080    |
+---------+----------+
          |
          v
+--------------------+
| Monitoringbackend |
+--------------------+
```

De pijl van de outpost naar de provider is conceptueel: de provider is opgeslagen in
Authentik en wordt door de toegewezen outpost geladen. Het is geen afzonderlijke
netwerkservice waarnaar de outpost een HTTP-request stuurt.

### Dataflow en control flow

Het helpt om twee soorten verkeer te onderscheiden.

| Verkeerssoort | Voorbeeld | Doel |
|---|---|---|
| Applicatiedata | browserrequest naar monitoring en antwoord van de backend | eigenlijke gebruikersinhoud leveren |
| Identity/control flow | forward-authcheck, loginredirect, callback en policybeslissing | bepalen of de applicatiedata door mag |

Conceptueel:

```text
                     identity/control flow
                 +----------------------------+
                 |                            v
+---------+   +---------+                +-----------+
| Browser |-->| Traefik |--------------->| Outpost   |
+---------+   +---------+                +-----+-----+
                 |                            |
                 |                            | gebruikt identity-,
                 |                            | provider- en policydata
                 |                            v
                 |                      +-----------+
                 |                      | Authentik |
                 |                      | core      |
                 |                      +-----------+
                 |
                 | applicatiedata na allow
                 v
             +---------+
             | Backend |
             +---------+
```

Wanneer Authentik deny antwoordt, hoort Traefik de normale request niet naar de
backend te sturen.

De identity/control flow beslist dus over toegang. De applicatiedata blijft bij
forward auth via Traefik naar de backend lopen.

### Vertrouwensrelaties

Elke pijl in het ontwerp veronderstelt vertrouwen.

| Relatie | Wat moet betrouwbaar zijn? |
|---|---|
| client -> Traefik | DNS, TLS-certificaat en hostname moeten bij het bedoelde toegangspunt horen |
| Traefik -> outpost | de forward-auth-URL en doorgestuurde requestcontext moeten correct zijn |
| outpost -> Authentik core | de outpost moet geldige configuratie voor toegewezen providers kunnen laden en identitybeslissingen kunnen uitvoeren |
| Traefik -> backend | alleen toegelaten requests en betrouwbare identity-headers mogen aankomen |
| beheerder -> Authentik | beheerwijzigingen moeten beperkt, geauthenticeerd en geaudit zijn |

Een fout in één relatie kan de hele keten blokkeren of verzwakken.

### Embedded versus afzonderlijke outpost

De workshop gebruikt de **embedded outpost**. Die draait als onderdeel van de
Authentik-server en houdt het lab overzichtelijk.

| Keuze | Waar draait de outpost? | Voordeel | Aandachtspunt |
|---|---|---|---|
| Embedded outpost | in de Authentik-serverdeployment | weinig extra containers en eenvoudige lokale koppeling | lifecycle, schaal en beschikbaarheid zijn sterk gekoppeld aan Authentik core |
| Afzonderlijke outpost | in een eigen container, VM of clusterdeployment | aparte plaatsing, lifecycle, netwerkzone en schaalbaarheid mogelijk | extra deployment, outposttoken, monitoring en netwerkbeleid nodig |

Bij de embedded outpost wijst Traefik in het lab naar dezelfde Authentik-server op
poort 9000, maar naar een specifiek outpostpad:

```text
http://server:9000/outpost.goauthentik.io/auth/traefik
```

Dat betekent niet dat Authentik core en de outpost conceptueel hetzelfde onderdeel
zijn. Ze delen in deze labkeuze alleen dezelfde serverdeployment en luisterpoorten.

Bij een afzonderlijke outpost zou de forward-auth-URL naar de aparte outpostservice
wijzen.

In productie hangt de keuze af van netwerkzones, schaal, beschikbaarheid en beheer.

### Typische misverstanden

| Misverstand | Correcte uitleg |
|---|---|
| De proxy provider is een extra reverse-proxycontainer | de provider is configuratie; de outpost is de uitvoerende component |
| De outpost en Traefik doen exact hetzelfde | de outpost neemt de identitybeslissing; Traefik proxyt de normale apprequest |
| De application is de backend | de application is een logisch Authentik-object; de backend is een aparte service |
| Een provider maken publiceert de app automatisch | Traefik heeft nog routers, middleware en backendservice nodig |
| Een Traefik-router maken beschermt de app automatisch | de router moet expliciet de forward-authmiddleware gebruiken |
| Elke outpost bedient automatisch elke provider | applications/providers moeten aan de outpost toegewezen worden |
| De outpost ontvangt altijd alle applicatie-inhoud | in forward-authmodus behandelt hij vooral authchecks en speciale outpostpaden |

### Controleer je begrip

1. Waar staat de interne backend-URL `http://monitoring:8080`: in de proxy provider of
   in Traefik?
2. Welk onderdeel bevat de binding met `bp-it`?
3. Welk onderdeel voert de providercontrole tijdens een request actief uit?
4. Welk onderdeel stuurt de toegelaten normale request uiteindelijk naar monitoring?
5. Waarom moet BluePeak Monitoring aan de embedded outpost toegewezen worden?
6. Wat verandert er architecturaal wanneer je een afzonderlijke outpost gebruikt?

Kernzin:

> De proxy provider beschrijft de Authentik-regels, de outpost voert die regels uit,
> Traefik gebruikt het resultaat om de normale request wel of niet naar de backend te
> sturen en de backend blijft verantwoordelijk voor haar eigen applicatielogica.

---

## 5. Wat is forward auth?

### Definitie

Bij **forward auth** blijft Traefik verantwoordelijk voor het proxyen van het echte
applicatieverkeer. Vóór Traefik een request naar de backend stuurt, doet Traefik een
afzonderlijke controle bij de Authentik-outpost.

De kernbeslissing is eenvoudig:

```text
outpost laat toe  -> Traefik stuurt request naar backend
outpost weigert   -> Traefik stuurt request niet naar backend
login ontbreekt   -> browser wordt naar het authenticatieproces geleid
```

### Requestflow zonder bestaande sessie

```text
Browser          Traefik          Outpost/Authentik         Backend
   |                 |                    |                    |
   | GET intranet    |                    |                    |
   |---------------->|                    |                    |
   |                 | auth check         |                    |
   |                 |------------------->|                    |
   |                 | login nodig        |                    |
   |<----------------|<-------------------|                    |
   | redirect en login bij Authentik      |                    |
   |------------------------------------->|                    |
   | callback/cookie |                    |                    |
   |---------------->|                    |                    |
   |                 | nieuwe auth check  |                    |
   |                 |------------------->|                    |
   |                 | allow + headers    |                    |
   |                 |<-------------------|                    |
   |                 | originele request + identity-headers    |
   |                 |---------------------------------------->|
   |                 |                    | appantwoord        |
   |<----------------|<----------------------------------------|
```

De backend ziet het wachtwoord of de TOTP-code niet. Die gegevens horen bij het
authenticatieproces van de identity provider.

### Drie mogelijke uitkomsten

| Situatie | Beslissing | Zichtbaar gevolg | Bereikt de normale request de backend? |
|---|---|---|---|
| geen geldige sessie | login starten | redirect naar Authentik | nog niet |
| geldige identiteit, verkeerde groep | deny | fout- of denyweergave | nee |
| geldige identiteit en juiste policy | allow | applicatiepagina | ja |

Een loginredirect is dus nog geen bewijs dat autorisatie klopt. Pas een allow- én
deny-test tonen dat de grens correct staat.

### Wat configureert Traefik?

| Traefik-onderdeel | Vraag die het beantwoordt |
|---|---|
| router | welke hostname of welk pad matcht? |
| middleware | moet deze request eerst door forward auth? |
| service | naar welke interne backend gaat een toegelaten request? |
| outpostrouter | waar worden login-, callback-, logout- en pingpaden verwerkt? |

Voorbeeldlogica:

```text
Host(`public.bluepeak.test`)
  -> geen forward auth
  -> public backend

Host(`monitoring.bluepeak.test`)
  -> authentik-forward middleware
  -> alleen na allow naar monitoring backend
```

### Forward auth versus native OIDC

| Eigenschap | Native OIDC in de app | Forward auth voor de app |
|---|---|---|
| Wie implementeert het identityprotocol? | de applicatie | proxy/outpostlaag |
| Krijgt de app tokens of claims via OIDC? | ja, volgens de clientimplementatie | meestal identity-headers na proxycontrole |
| Geschikt voor legacyapp zonder SSO? | alleen na applicatiewijziging | vaak wel |
| Fijne autorisatie in de app | app kan claims en rollen zelf verwerken | app heeft nog eigen logica nodig voor acties binnen de app |
| Vertrouwensgrens | tokenvalidatie in de app | vertrouwde proxy en afgeschermde backend |

Native OIDC is vaak sterker geïntegreerd wanneer de applicatie het goed ondersteunt.
Forward auth is vooral nuttig wanneer je een bestaande webapp vóór de backend wilt
beschermen zonder haar loginprotocol te herschrijven.

Controleer:

- Is de forward-authmiddleware gekoppeld aan elke beschermde router?
- Bereikt een geweigerde request de backend niet?
- Komt een toegelaten request met de verwachte identitycontext aan?
- Blijft de publieke route bewust zonder identitycheck werken?

Kernzin:

> Forward auth laat de reverse proxy vóór elke beschermde backendroute een externe
> authenticatie- en autorisatiebeslissing vragen.

---

## 6. Publieke en beschermde routes

Niet elke applicatie heeft dezelfde doelgroep of gevoeligheid. Een ontwerp begint
daarom met classificatie, niet met het blind kopiëren van middleware.

### Voorbeeldbeleid van BluePeak

| Applicatie | Doelgroep | Gevoeligheid | Identitybeleid |
|---|---|---|---|
| Publieke status | iedereen | publiek | geen login |
| Intranet | medewerkers | intern | `bp-employees` |
| Monitoring | IT | vertrouwelijk | `bp-it` |
| Admin | IT-admins | kritisch | `bp-it-admins` + step-up MFA |
| Partnerportaal | externe partners | beperkt | `bp-partners` |

De publieke route is geen fout. Ze is een bewuste zakelijke keuze.

Ook een publieke applicatie heeft nog beveiliging nodig:

| Maatregel | Waarom ook bij public nodig? |
|---|---|
| TLS | beschermt integriteit en voorkomt dat gebruikers met een vervalste site praten |
| patching | publieke software is rechtstreeks blootgesteld aan requests |
| rate limiting | beperkt misbruik en overbelasting |
| logging | maakt fouten en verdachte patronen zichtbaar |
| minimale backendtoegang | de publieke app mag geen brede interne netwerktoegang krijgen |

### Classificatievragen

Voor elke nieuwe hostname stel je minstens deze vragen:

1. Moet een anonieme gebruiker de inhoud kunnen zien?
2. Welke zakelijke groep heeft toegang nodig?
3. Is een gewone SSO-sessie voldoende?
4. Is een recente extra factor nodig?
5. Welke identitygegevens heeft de backend werkelijk nodig?
6. Welke negatieve test bewijst dat de grens werkt?

### Typische fout: middleware vergeten

Wanneer de monitoringrouter wel naar de juiste backend wijst maar geen
forward-authmiddleware bevat, opent de applicatie rechtstreeks.

Dat is gevaarlijk omdat alles er technisch gezond kan uitzien:

- DNS werkt;
- de router matcht;
- de backend geeft status 200;
- de pagina verschijnt.

Precies daarom volstaat een positieve bereikbaarheidstest niet.

Controleer:

| Test | Verwacht | Waarom? |
|---|---|---|
| anoniem naar public | allow | bewijst dat de publieke route bewust werkt |
| anoniem naar monitoring | loginredirect | bewijst dat forward auth actief is |
| medewerker naar monitoring | deny | bewijst dat login niet automatisch IT-toegang geeft |
| IT-gebruiker naar monitoring | allow | bewijst dat de juiste groepspolicy werkt |

Kernzin:

> Een route is publiek of beschermd omdat het ontwerp dat expliciet beslist, niet
> omdat een middleware toevallig wel of niet aanwezig is.

---

## 7. Proxy provider en application

In Authentik zijn de **application** en de **proxy provider** twee verschillende
objecten. Dat onderscheid uit hoofdstuk 9 blijft gelden, maar de provider gebruikt nu
het proxyprotocol in plaats van OIDC voor een native client.

### Application: de functionele toegangskant

| Application-instelling | Betekenis |
|---|---|
| Name | herkenbare naam voor gebruiker en beheerder |
| Slug | technische identifier in Authentik |
| Launch URL | externe URL waarmee de gebruiker de app opent |
| Provider | technische koppeling waarmee de app beschermd wordt |
| Policy engine mode | bepaalt hoe meerdere bindings of policies gecombineerd worden |
| Bindings | koppelen gebruikers, groepen of policies aan toegang |

Vragen die bij de application horen:

- Wie heeft een zakelijke reden om deze app te openen?
- Welke groep vertaalt die doelgroep het best?
- Welke naam en URL moeten gebruikers herkennen?
- Wat gebeurt er wanneer geen binding aanwezig is?

### Proxy provider: de technische authkoppeling

| Providerinstelling | Technische betekenis |
|---|---|
| Mode | bepaalt proxy, single-application forward auth of domain-level forward auth |
| External host | exacte URL waarmee de browser de beschermde app bereikt |
| Authentication flow | bepaalt hoe een gebruiker zich aanmeldt als geen centrale login bestaat |
| Authorization flow | bepaalt welke extra stappen vóór toegang nodig zijn |
| Invalidation flow | bepaalt wat providerlogout doet |
| Token- of sessie-instellingen | beïnvloeden hoe lang providercontext geldig blijft |

De external host moet scheme, hostname en niet-standaardpoort correct bevatten.

Voorbeeld:

```text
http://monitoring.bluepeak.test:8100
```

Een fout zoals een ontbrekende `:8100` kan tot redirects, cookies of providermatching
op een andere origin leiden.

### Outposttoewijzing: de derde koppeling

Een application/providerpaar is nog niet voldoende. Een proxy provider moet door een
proxy outpost bediend worden.

```text
Application
    |
    v
Proxy provider
    |
    v
toegewezen aan embedded outpost
    |
    v
Traefik vraagt forward-authbeslissing
```

### Authentication flow versus authorization flow

| Flow | Vraag | Voorbeeld in BluePeak |
|---|---|---|
| Authentication flow | hoe bewijst de gebruiker zijn identiteit? | centrale login met wachtwoord en eventuele algemene MFA |
| Authorization flow | welke extra stap is nodig vóór deze provider toegang geeft? | TOTP-step-up voor admin |

Dat verschil is belangrijk bij SSO. Een gebruiker kan al centraal aangemeld zijn,
maar voor het adminportaal toch een extra authorizationstap moeten uitvoeren.

### Troubleshooting per object

| Symptoom | Controleer eerst |
|---|---|
| app verschijnt niet of gebruiker krijgt onverwachte deny | application en binding |
| verkeerde redirect of callback | provider external host en flows |
| provider wordt niet gevonden | outposttoewijzing |
| backend geeft 502/503 na allow | Traefik service en interne backendpoort |
| geen login vóór backend | middleware op Traefik-router |

Kernzin:

> De application beschrijft welke logische app voor wie toegankelijk is; de proxy
> provider beschrijft hoe die toegang technisch gecontroleerd wordt; de outpost voert
> die providercontrole uit.

---

## 8. Single-application versus domain-level forward auth

Authentik ondersteunt twee forward-authpatronen. De juiste keuze hangt af van de
gewenste policygranulariteit.

### Single-application forward auth

Elke beschermde applicatie krijgt een eigen application en proxy provider.

```text
intranet     -> provider intranet     -> bp-employees
monitoring   -> provider monitoring   -> bp-it
admin        -> provider admin        -> bp-it-admins + MFA-flow
partner      -> provider partner      -> bp-partners
```

| Voordeel | Concrete betekenis |
|---|---|
| afzonderlijke bindings | elke hostname krijgt een eigen doelgroep |
| aparte authorization flows | admin kan step-up MFA gebruiken zonder dat public of intranet dat beleid erft |
| duidelijke auditcontext | events kunnen aan een specifieke application/provider gekoppeld worden |
| least privilege per app | toegang tot één app opent niet automatisch alle apps onder het domein |

Nadeel:

| Beheerlast | Praktisch gevolg |
|---|---|
| meer objecten | elke app vraagt application, provider, binding en outposttoewijzing |
| consistente naamgeving nodig | slordige slugs en providernamen maken troubleshooting moeilijk |
| wijzigingen per app | een gedeelde policywijziging moet gecontroleerd over meerdere objecten gebeuren |

### Domain-level forward auth

Eén provider beschermt meerdere applicaties onder een gedeeld parent domain.

```text
*.bluepeak.test -> één domain-level provider -> gedeeld toegangsbeleid
```

| Voordeel | Concrete betekenis |
|---|---|
| minder providers | eenvoudiger wanneer veel apps exact hetzelfde beleid hebben |
| gedeelde providersessie | gebruikers ervaren minder afzonderlijke appautorisaties |
| centraal domeinbeleid | één consistente basiscontrole voor meerdere subdomeinen |

Belangrijke beperking:

> Domain-level forward auth kan niet per achterliggende applicatie een andere
> application binding of authorization flow afdwingen.

### Keuzematrix

| Requirement | Beste uitgangspunt | Waarom? |
|---|---|---|
| twintig interne tools, allemaal voor alle medewerkers | domain-level kan passen | hetzelfde beleid beperkt de nood aan aparte providers |
| intranet voor medewerkers en monitoring alleen voor IT | single-application | bindings verschillen per app |
| admin vereist step-up MFA | single-application | aparte authorization flow nodig |
| partner mag slechts één portaal zien | single-application | sterke scheiding van interne apps |

### Typische verkeerde aanname

> Eén domain-level provider beschermt alles, dus we kunnen binnen die provider nog
> eenvoudig per hostname een andere Authentik-application binding gebruiken.

Dat is precies de beperking. Traefik kan de hostnames wel naar verschillende backends
routeren, maar de gedeelde domain-level Authentik-provider heeft niet automatisch een
afzonderlijke applicationpolicy per backend.

Daarom gebruikt de workshop **single-application forward auth**.

Kernzin:

> Kies domain-level voor veel apps met hetzelfde beleid en single-application wanneer
> doelgroep, MFA of auditcontext per app moet verschillen.

---

## 9. De speciale outpost-route

### Waarvoor dient het pad?

Bij single-application forward auth moet elk beschermd applicatiedomein requests onder
dit pad naar de outpost sturen:

```text
/outpost.goauthentik.io/
```

Het pad ondersteunt verschillende onderdelen van de authenticatieketen:

| Functie | Praktische rol |
|---|---|
| start | begint het login- of authorizationproces |
| callback | verwerkt de terugkeer na Authentik-authenticatie |
| auth endpoint | beantwoordt de forward-authcontrole van Traefik |
| sign out | beëindigt de relevante providersessie |
| ping | controleert of de outpostroute technisch bereikbaar is |

### Waarom een afzonderlijke router?

De gewone router voor `monitoring.bluepeak.test` beschermt de applicatie met forward
auth. Het outpostpad moet daarentegen rechtstreeks naar de outpost gaan.

```text
Host(monitoring) + PathPrefix(/outpost.goauthentik.io/)
    -> outpostservice

Host(monitoring) + alle andere paden
    -> forward auth
    -> monitoringbackend na allow
```

De outpostrouter krijgt een hogere prioriteit zodat het specifiekere pad vóór de
algemene applicatieroute matcht.

### Wat gaat fout bij een verkeerde route?

| Fout | Mogelijk symptoom | Verklaring |
|---|---|---|
| outpostrouter ontbreekt | 404 of loginproces start niet | technisch authpad bereikt de outpost niet |
| outpostrouter heeft forward auth | redirectloop | de authroute probeert zichzelf opnieuw te authenticeren |
| prioriteit te laag | app-router vangt het pad op | request gaat naar de verkeerde service |
| verkeerde service-URL | 502/503 | Traefik bereikt de outpost niet correct |
| hostname ontbreekt in rule | één protected app werkt niet | het outpostpad matcht niet voor die host |

### Controleer met ping

Voorbeeld:

```text
http://monitoring.bluepeak.test:8100/outpost.goauthentik.io/ping
```

Een succesvolle lege healthrespons, typisch status `204`, bewijst:

- naamresolutie naar Traefik werkt;
- de Host-rule matcht;
- het pad krijgt de outpostrouter;
- Traefik bereikt de outpostservice.

De ping bewijst nog niet:

- dat de juiste groep toegang krijgt;
- dat de application binding klopt;
- dat MFA afgedwongen wordt;
- dat de backend bereikbaar is.

Dat vraagt afzonderlijke tests.

Kernzin:

> De applicatieroute is beschermd, maar het technische outpostpad moet afzonderlijk
> bereikbaar zijn om login, callback, logout en authcontrole mogelijk te maken.

---

## 10. Groepsgebaseerde toegang

Groepsbindings vertalen een zakelijke accessmatrix naar Authentik-configuratie.

### Van bedrijfsrol naar technische binding

BluePeak gebruikt dit model:

| Applicatie | Zakelijke doelgroep | Technische binding |
|---|---|---|
| Intranet | alle medewerkers | `bp-employees` |
| Monitoring | IT-team | `bp-it` |
| Admin | beperkt beheerteam | `bp-it-admins` |
| Partnerportaal | goedgekeurde externe partners | `bp-partners` |

De groep is niet het einddoel. De groep legt vast waarom een verzameling gebruikers
dezelfde toegang nodig heeft.

### Voorbeeldgebruikers

| Gebruiker | Groepen | Zakelijke betekenis |
|---|---|---|
| Alice | `bp-employees` | gewone interne medewerker |
| Bob | `bp-employees`, `bp-it`, `bp-it-admins` | medewerker met IT- en beperkte adminverantwoordelijkheid |
| Eva | `bp-partners` | externe identiteit zonder interne medewerkersrechten |

Verwachte accessmatrix:

| Gebruiker | Intranet | Monitoring | Admin | Partner |
|---|---|---|---|---|
| Alice | allow | deny | deny | deny |
| Bob | allow | allow | allow na MFA | deny |
| Eva | deny | deny | deny | allow |

### Waarom een aparte admingroep?

`bp-it` en `bp-it-admins` zijn bewust niet hetzelfde.

| Groep | Mogelijke verantwoordelijkheid |
|---|---|
| `bp-it` | dashboards bekijken en operationele informatie onderzoeken |
| `bp-it-admins` | instellingen wijzigen of acties met hoge impact uitvoeren |

Als elke IT-medewerker automatisch admin wordt, is least privilege niet toegepast.

### Standaardgedrag zonder binding

Een gevaarlijke denkfout is aannemen dat een Authentik-application zonder binding
automatisch gesloten is. Wanneer geen toepasselijke binding bestaat, kan de
application standaard breder toegankelijk zijn dan bedoeld.

Daarom controleer je niet alleen of een groep bestaat, maar ook:

| Controle | Bewijs |
|---|---|
| juiste groep aan juiste application gebonden | configuratieoverzicht zonder secrets |
| toegelaten lid krijgt toegang | positieve test |
| aangemelde niet-lid krijgt deny | negatieve test |
| groepswijziging verandert toegang | lifecycle- of wijzigingstest |
| beheerwijziging verschijnt in audit | Authentik-event |

### Lifecycle-impact

Groepsgebaseerde toegang werkt alleen als groepslidmaatschap actueel blijft.

Voorbeeld:

```text
Bob verlaat het adminteam.
Bob blijft medewerker en IT'er.

verwijder: bp-it-admins
behoud:    bp-employees en bp-it
```

De juiste uitkomst is dat Bob intranet en monitoring behoudt, maar admin verliest.

Kernzin:

> Een application binding is de technische vertaling van een zakelijke doelgroep;
> positieve én negatieve tests bewijzen of die vertaling correct is.

---

## 11. Step-up MFA voor gevoelige applicaties

### Wat is step-up authentication?

Niet elke applicatie heeft hetzelfde risico. Een bestaand intranet kan een geldige
centrale SSO-sessie vertrouwen, terwijl een adminportaal extra zekerheid vraagt.

**Step-up authentication** betekent dat een gebruiker voor een gevoeligere
applicatie of handeling een sterkere of recentere verificatie uitvoert.

Voorbeeld:

1. Bob meldt zich aan en opent het intranet.
2. Bob heeft nu een geldige centrale Authentik-sessie.
3. Bob opent daarna het adminportaal.
4. Groepslidmaatschap `bp-it-admins` maakt Bob kandidaat voor toegang.
5. De adminprovider voert een strengere authorization flow uit.
6. Authentik vraagt en valideert een TOTP-code.
7. Alleen na die validatie krijgt Bob admintoegang.

### Drie verschillende MFA-toestanden

| Toestand | Wat betekent dit? | Bewijst dit admintoegang? |
|---|---|---|
| device geregistreerd | de gebruiker heeft ooit TOTP enrolled | nee |
| MFA gevalideerd | een code werd in een flow correct gecontroleerd | alleen als het de relevante flow is |
| recent gevalideerd | policy mag een eerdere geldige MFA binnen een tijdsvenster hergebruiken | afhankelijk van het ingestelde thresholdbeleid |

Alleen controleren dat een gebruiker een TOTP-device bezit, creëert schijnveiligheid.
De actieve toegangsflow moet de factor ook werkelijk eisen.

### Waarom de authorization flow?

Bij SSO kan de centrale authentication flow al eerder voltooid zijn. Als de
adminprovider alleen vertrouwt op die bestaande sessie, verschijnt mogelijk geen
nieuwe factorcontrole.

Een aparte authorization flow kan extra verificatie uitvoeren vóór deze specifieke
provider toegang geeft.

| Instelling | Labkeuze | Effect |
|---|---|---|
| Designation | authorization | de flow hoort bij toegang tot de provider |
| Authentication | require authenticated | gebruiker moet eerst centraal bekend zijn |
| Device class | TOTP | alleen een bevestigd TOTP-device voldoet |
| Not configured action | Deny | gebruiker zonder geschikte factor krijgt geen toegang |
| Last validation threshold | `seconds=0` | de labflow kan de factor opnieuw vragen en zichtbaar maken |

### Deny, skip of configure

Wanneer een gebruiker geen geschikte factor heeft, bestaan conceptueel drie keuzes:

| Keuze | Gedrag | Risico of gebruik |
|---|---|---|
| Skip | ga verder zonder factor | ongeschikt wanneer MFA echt verplicht is |
| Deny | stop de toegang | duidelijk fail-closed, maar enrollment moet vooraf geregeld zijn |
| Configure | laat factor registreren in de flow | bruikbaar voor onboarding, maar recovery en identityproofing moeten kloppen |

De workshop kiest **Deny** voor admin. Dat maakt de negatieve test ondubbelzinnig.

### Sterke MFA-tests

| Test | Verwacht | Wat bewijst dit? |
|---|---|---|
| Bob opent eerst intranet | allow met gewone SSO | centrale sessie bestaat vóór step-up |
| Bob opent daarna admin | TOTP-prompt | admin gebruikt extra authorizationstap |
| Bob voert foute code in | toegang niet voltooid | factor wordt werkelijk gevalideerd |
| Bob voert geldige code in | allow | juiste groep en factor werken samen |
| Alice tijdelijk in admingroep zonder TOTP | deny | groepslidmaatschap alleen is onvoldoende |

### In productie

Voor kritieke beheertoegang onderzoek je ook:

| Thema | Productievraag |
|---|---|
| factorsterkte | is TOTP voldoende of is phishing-resistente WebAuthn/passkey nodig? |
| validatiefrequentie | hoe lang mag een eerdere MFA geldig blijven? |
| recovery | wie mag een verloren factor resetten en hoe wordt identiteit opnieuw bewezen? |
| break-glass | bestaat gecontroleerde noodtoegang en wordt elk gebruik geaudit? |
| device lifecycle | worden verloren, vervangen en oude devices verwijderd? |

Kernzin:

> Step-up MFA betekent niet dat een factor ergens geregistreerd staat, maar dat een
> passende extra factor voor de gevoelige toegang effectief en aantoonbaar gevalideerd
> wordt.

---

## 12. Identity-headers

Na een toegelaten forward-authcontrole kan de outpost identity-informatie aan Traefik
teruggeven. Traefik voegt geselecteerde responseheaders vervolgens toe aan de request
naar de backend.

### Veelgebruikte headers

| Header | Inhoud | Mogelijk gebruik door backend |
|---|---|---|
| `X-authentik-username` | centrale gebruikersnaam | remote-usermapping of weergave |
| `X-authentik-groups` | groepslidmaatschappen | beperkte applicatierolmapping |
| `X-authentik-email` | e-mailadres | contactinformatie of matching, niet altijd stabiele sleutel |
| `X-authentik-name` | weergavenaam | personalisatie in de UI |
| `X-authentik-uid` | stabiele gehashte identifier | technische koppeling aan lokaal profiel |
| `X-authentik-meta-app` | Authentik application slug | logging en controle van appcontext |
| `X-authentik-meta-provider` | providercontext | troubleshooting en audit |

### Hoe komen de headers bij de backend?

```text
1. Client stuurt request naar Traefik.
2. Traefik vraagt forward-authbeslissing.
3. Outpost antwoordt allow en levert identityheaders.
4. Traefik kopieert alleen geconfigureerde authResponseHeaders.
5. Backend ontvangt request met die identitycontext.
```

De lijst `authResponseHeaders` is dus een vorm van dataminimalisatie.

| Ontwerpkeuze | Waarom? |
|---|---|
| alleen noodzakelijke headers doorgeven | beperkt persoonsgegevens en beslissingsinformatie bij de backend |
| vaste headernamen documenteren | voorkomt dat applicaties verschillende aannames maken |
| geen tokens in screenshots of logs | tokens kunnen toegang of gevoelige claims bevatten |
| stabiele identifier gebruiken | naam of e-mail kan tijdens de lifecycle wijzigen |

### Wat mag de backend ermee doen?

Een backend kan identity-headers gebruiken voor:

- een centrale gebruikersnaam tonen;
- een lokaal profiel aan een stabiele centrale identiteit koppelen;
- auditregels met gebruikerscontext schrijven;
- een beperkte applicatierol afleiden;
- de gebruiker niet opnieuw om een lokaal wachtwoord vragen.

De backend blijft verantwoordelijk voor acties binnen haar eigen domein.

Voorbeeld:

```text
forward auth: Bob mag de ticketapp openen
ticketapp:    Bob mag tickets bekijken
ticketapp:    alleen ticket-managers mogen wachtrijen verwijderen
```

Kernzin:

> Identity-headers brengen bevestigde gebruikerscontext naar een legacybackend, maar
> vervangen de fijnmazige autorisatie binnen die applicatie niet.

---

## 13. Header spoofing en de vertrouwensgrens

### Het aanvalsidee

Stel dat een client zelf deze header meestuurt:

```text
X-authentik-username: akadmin
```

Als de backend rechtstreeks bereikbaar is en die header blind vertrouwt, kan een
client zichzelf mogelijk als een andere gebruiker voordoen.

Dat heet **header spoofing**.

### Wanneer is een identity-header betrouwbaar?

Een header krijgt pas betekenis door het volledige pad waarlangs ze aankomt.

| Voorwaarde | Waarom nodig? |
|---|---|
| backend heeft geen publieke hostpoort | client kan de proxy niet omzeilen |
| firewall laat alleen proxy naar backend toe | ook buiten Docker blijft het pad afgedwongen |
| proxy verwijdert of overschrijft clientheaders | client kan geen oude of valse identiteit behouden |
| forward auth levert de vertrouwde waarden | identiteit komt uit de gecontroleerde authbeslissing |
| backend vertrouwt alleen bekende proxybronnen | requests van andere bronnen worden geweigerd |
| TLS beschermt relevante netwerksegmenten | voorkomt manipulatie of onderschepping onderweg |

### Twee noodzakelijke negatieve tests

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

### Waarom één test niet volstaat

| Resultaat | Wat weet je? | Wat weet je nog niet? |
|---|---|---|
| gespoofte header via Traefik faalt | middleware accepteert de clientclaim niet als sessie | backend kan misschien nog direct bereikbaar zijn |
| directe hostpoort faalt | backend is niet via die hostpoort gepubliceerd | firewall- of andere netwerkpaden kunnen nog bestaan |
| beide falen en backend ziet alleen proxyverkeer | vertrouwensgrens is beter onderbouwd | productie-TLS en firewallbeleid moeten nog gecontroleerd worden |

### Typische fout

Een ontwikkelaar publiceert tijdelijk de backendpoort om sneller te debuggen en laat
die mapping staan. De applicatie werkt dan zowel via de beveiligde proxy als via een
onbeveiligde rechtstreekse route.

De positieve proxytest blijft slagen, waardoor de bypass onzichtbaar blijft zonder
negatieve test.

Kernzin:

> Een identity-header is alleen betrouwbaar wanneer clients de backend niet buiten de
> vertrouwde proxy- en authketen kunnen bereiken of beïnvloeden.

---

## 14. SSO, providercookies en logout

Identity-aware toegang gebruikt meerdere soorten sessies. Problemen ontstaan vaak
wanneer al die sessies simpelweg “de login” genoemd worden.

### Mogelijke sessielagen

| Sessie | Beheerd door | Doel |
|---|---|---|
| centrale Authentik-sessie | Authentik core | onthouden dat de gebruiker centraal aangemeld is |
| proxyprovidersessie | outpost/provider | onthouden dat toegang voor die provider werd verkregen |
| applicatiesessie | eventueel de backend | lokale applicatiestatus of fijnmazige rechten onthouden |

Voor een simpele demoapp kan de derde sessie ontbreken. Een echte applicatie kan ze
wel hebben.

### SSO over twee beschermde apps

```text
Bob opent intranet.
Bob meldt centraal aan bij Authentik.
Intranetprovider krijgt een geldige context.

Bob opent monitoring.
Monitoringprovider stuurt Bob naar Authentik.
Authentik herkent de centrale sessie.
Bob hoeft mogelijk niet opnieuw zijn wachtwoord in te geven.
```

SSO betekent dus niet dat elke applicatie exact dezelfde providersessie gebruikt. Het
betekent dat een bestaande centrale IdP-sessie nieuwe appautorisaties kan vereenvoudigen.

### Verschillende logoutacties

| Actie | Mogelijk effect | Wat kan blijven bestaan? |
|---|---|---|
| providerlogout | sessie voor de betrokken proxyprovider eindigt | centrale Authentik-sessie en andere appsessies |
| centrale Authentik-logout | centrale IdP-sessie eindigt | lokale backend- of providersessies afhankelijk van integratie |
| browser sluiten | tijdelijke cookies kunnen verdwijnen | persistente sessies of server-side sessiestatus |
| account deactiveren | nieuwe centrale logins worden geblokkeerd | reeds uitgegeven lokale sessies tot intrekking of expiry |
| sessies intrekken | actieve centrale toegang wordt afgebroken | afzonderlijke appsession kan nog controle vragen |

Providerlogout gebeurt bij single-application forward auth via het beschermde hostpad:

```text
/outpost.goauthentik.io/sign_out
```

### Waarom de starttoestand documenteren?

Dezelfde URL kan anders reageren naargelang cookies en sessies.

Een goed testverslag vermeldt daarom:

- nieuw private venster of bestaande browser;
- welke gebruiker centraal aangemeld is;
- welke provider al geopend werd;
- of MFA recent gevalideerd werd;
- welke logoutactie vooraf gebeurde.

Zonder die context is “ik kreeg geen loginprompt” geen betrouwbaar bewijs van een
fout. Het kan juist werkende SSO zijn.

### Lifecyclevoorbeeld

Alice wordt gedeactiveerd terwijl een bestaande applicatiesessie nog openstaat.

| Test | Mogelijk resultaat | Verklaring |
|---|---|---|
| bestaande apppagina vernieuwen | kan tijdelijk blijven werken | lokale sessie vraagt niet bij elke request opnieuw centrale login |
| nieuwe providersessie starten | deny | gedeactiveerd account mag niet opnieuw authenticeren |
| centrale sessies intrekken en opnieuw testen | herauthenticatie of deny | bestaande IdP-context is verwijderd |

Kernzin:

> Logout en accountdeactivatie zijn pas correct getest wanneer je benoemt welke
> centrale, provider- en applicatiesessies verdwijnen en welke mogelijk blijven.

---

## 15. Logging en auditing

Een identity-aware request laat sporen achter op meerdere plaatsen. Geen enkele bron
vertelt op zichzelf het volledige verhaal.

### Welke bron toont wat?

| Bron | Typische informatie | Sterk in |
|---|---|---|
| Traefik accesslog | hostname, pad, tijdstip, statuscode en proxyfout | requestpad en bereikbaarheid |
| Authentik server/outpostlog | providercontext, flowfout en technische authdetails | authenticatieketen en outpostproblemen |
| Authentik events | actor, application, policy, MFA en beheerwijziging | audit en verklaring van toegang |
| Backendlog of demopagina | ontvangen identity-headers en uitgevoerde appactie | bewijs van context na allow |

### Voorbeeld van logcorrelatie

Alice probeert monitoring te openen maar hoort geweigerd te worden.

```text
10:14:03 Traefik: request voor monitoring.bluepeak.test
10:14:03 Authentik: Alice, application BluePeak Monitoring, policy deny
10:14:03 Backend: geen normale applicatierequest voor Alice
```

De drie observaties samen bewijzen:

1. Alice bereikte het centrale toegangspunt.
2. Authentik herkende de identiteit maar weigerde autorisatie.
3. Traefik stuurde de normale request niet door naar de backend.

### Contextvragen voor elk event

| Vraag | Waarom nodig? |
|---|---|
| wanneer gebeurde het? | correleert bronnen en wijzigingen |
| welke gebruiker? | koppelt de beslissing aan een identiteit |
| welke hostname/application? | onderscheidt intranet, monitoring en admin |
| welke flow of provider? | verklaart login, step-up of logout |
| welk resultaat? | onderscheidt allow, deny en technische fout |
| welke wijziging ging vooraf? | een binding- of routerwijziging kan gedrag verklaren |

### Logging is geen volledige preventie

Logs blokkeren geen aanval. Ze ondersteunen:

| Doel | Voorbeeld |
|---|---|
| detectie | plots veel deny-events voor admin |
| troubleshooting | verkeerde external host na een wijziging |
| audit | wie voegde Bob aan `bp-it-admins` toe? |
| incidentonderzoek | welke apps werden met een gestolen sessie geopend? |
| herstel | controleren of sessie-intrekking effect had |

### Privacy en secret hygiene

Neem niet zomaar alle headers of cookies op in centrale logs.

| Niet opnemen | Waarom? |
|---|---|
| wachtwoorden en TOTP-codes | directe authenticatiegegevens |
| sessiecookies | kunnen een actieve sessie vertegenwoordigen |
| volledige tokens | kunnen claims en bruikbare toegang bevatten |
| TOTP-seed of QR-code | maakt het genereren van toekomstige codes mogelijk |
| onnodige persoonsgegevens | vergroot privacy- en datalekimpact |

Kernzin:

> Traefik toont het requestpad, Authentik verklaart de identitybeslissing en de
> backend toont wat na allow aankwam; pas de correlatie levert sterk bewijs.

---

## 16. Fail-closed en de IdP als kritieke afhankelijkheid

### Wat betekent fail-closed?

Wanneer Authentik of de outpost geen geldige beslissing kan geven, hoort een
beschermde route geen toegang tot de backend te geven.

> Geen geldige toegangsbeslissing betekent geen toegang tot de beschermde backend.

Dit is **fail-closed**.

Het tegenovergestelde, fail-open, zou verkeer doorlaten wanneer de authdienst faalt.
Dat verbetert schijnbaar de beschikbaarheid, maar kan de volledige toegangscontrole
omzeilen.

### Verschillende storingen

| Storing | Verwacht voor public | Verwacht voor protected |
|---|---|---|
| Authentik server down | public kan blijven werken | nieuwe authbeslissing faalt gesloten |
| outpostroute fout | public werkt | login/authcheck faalt, geen backendinhoud |
| backend down | public afhankelijk van eigen backend | auth kan slagen maar app geeft 502/503 |
| PostgreSQL/identitydata onbeschikbaar | public werkt | Authentik kan geen betrouwbare beslissing leveren |
| DNS voor authhost fout | public kan werken | browser kan loginredirect niet voltooien |

Deze verschillen helpen bij troubleshooting. Een backendfout na succesvolle auth is
niet hetzelfde als een IdP-fout vóór auth.

### Beschikbaarheid versus veiligheid

Identity-aware access centraliseert beveiliging, maar centraliseert ook afhankelijkheid.

| Maatregel | Welk risico beperkt dit? |
|---|---|
| meerdere Authentik-instanties | uitval van één core-instance |
| redundante database | verlies of onbeschikbaarheid van identitydata |
| reverse proxy/load balancer | verdeelt verkeer en vermijdt één toegangspunt |
| healthchecks en monitoring | detecteert problemen vóór gebruikers ze massaal melden |
| back-up en geteste restore | herstelt configuratie en data na fout of incident |
| onderhouds- en rollbackplan | beperkt impact van foutieve upgrades of policies |
| capaciteitstest | voorkomt dat loginpieken de IdP overbelasten |
| betrouwbare tijdsynchronisatie | voorkomt problemen met sessies, tokens en TOTP |

### Break-glass en noodtoegang

Een noodaccount mag geen verborgen permanente bypass worden.

| Eis | Waarom? |
|---|---|
| beperkt tot kritieke noodfunctie | voorkomt dagelijks misbruik |
| sterk beschermd credential | verlaagt kans op ongeoorloofd gebruik |
| afzonderlijk opgeslagen | blijft beschikbaar bij uitval van normale identityketen |
| elk gebruik gealert en geaudit | noodtoegang moet uitzonderlijk en zichtbaar zijn |
| regelmatig getest | een onbruikbaar noodpad helpt niet tijdens incidenten |
| gebruik achteraf gereviewd | controleert reden, acties en credentialrotatie |

### Labtest

In de workshop wordt alleen de Authentik-server tijdelijk gestopt.

| Test | Verwacht | Bewijs |
|---|---|---|
| public openen | blijft werken | route heeft geen forward auth nodig |
| nieuwe protected request | geen backendinhoud | proxy krijgt geen geldige authbeslissing |
| Authentik opnieuw starten | protected toegang herstelt na gereedkomen | afhankelijkheid is gelokaliseerd |

Kernzin:

> Fail-closed beschermt de applicatie bij identityproblemen, maar maakt
> beschikbaarheidsontwerp, monitoring en herstel van de IdP onmisbaar.

---

## 17. Typische fouten

| Fout | Gevolg | Hoe herken je dit? | Betere aanpak |
|---|---|---|---|
| forward-authmiddleware ontbreekt | app opent zonder login | anonieme request krijgt backendstatus 200 | middleware per protected router controleren |
| outpostrouter ontbreekt | login start niet of geeft 404 | pingpad bereikt outpost niet | apart outpostpad configureren |
| outpostrouter gebruikt zelf forward auth | redirectloop | browser blijft tussen authpaden navigeren | outpostpad rechtstreeks naar outpostservice |
| routerprioriteit fout | app-router vangt callback of ping | dashboard toont verkeerde routermatch | specifieker pad hogere prioriteit geven |
| external host fout | callback- of cookieprobleem | scheme, host of poort in redirect wijkt af | exacte browser-URL registreren |
| application niet aan outpost toegewezen | provider niet beschikbaar | outpostconfig mist app | application expliciet selecteren |
| application binding ontbreekt | toegang te breed | partner kan onverwacht interne app openen | binding plus negatieve test |
| verkeerde groep gebonden | onverwachte allow of deny | accessmatrix wijkt systematisch af | zakelijke matrix opnieuw vertalen |
| admin gebruikt gewone authorization flow | geen step-up MFA | Bob opent admin zonder nieuwe factor | adminprovider aan MFA-flow koppelen |
| MFA-stage gebruikt Skip | gebruiker zonder factor komt binnen | negatieve no-device-test slaagt onterecht | Deny of gecontroleerde enrollmentflow |
| backend heeft hostpoort | proxy en auth zijn te omzeilen | directe localhostpoort werkt | alleen proxy publiceert poorten |
| clientheader wordt vertrouwd | impersonatierisico | zelfgekozen header verandert backendidentiteit | headers overschrijven en backend isoleren |
| Authentik down wordt als backendfout gezien | verkeerde component aangepast | public werkt, protected auth faalt | logs per laag correleren |
| alleen positieve test | te brede policy blijft verborgen | één gebruiker werkt, grenzen onbekend | allow- en deny-cellen testen |
| lab-HTTP als productieontwerp | cookies en credentials onvoldoende beschermd | externe URL gebruikt HTTP | HTTPS, geldig DNS- en certificaatbeheer |

Gebruik de tabel niet als lijst van willekeurige fixes. Begin bij het symptoom en
bepaal eerst welke laag de verwachte beslissing niet uitvoert.

---

## 18. Methodisch troubleshooten

Werk van buiten naar binnen en wijzig per hypothese slechts één onderdeel.

### Overzicht per laag

| Laag | Centrale vraag | Controle | Typisch bewijs |
|---|---|---|---|
| 1. Naamresolutie | wijst de hostname naar Traefik? | DNS/hosts file en Host-header | resolve-output of gerichte curl |
| 2. Entry point en router | ontvangt en matcht Traefik de request? | dashboard en accesslog | gekozen host, pad en status |
| 3. Outpostpad | kan login/authtechniek de outpost bereiken? | pingendpoint en routerprioriteit | 204-respons en outpostlog |
| 4. Application/provider | bestaat de juiste technische koppeling? | external host, flow en outpostassignment | Authentik-config en events |
| 5. Identity/policy | is account actief en binding juist? | gebruiker, groep en policyresultaat | allow- of deny-event |
| 6. Backend | kan Traefik de interne app bereiken? | servicenaam, poort en backendlog | 200 of gerichte 502/503-analyse |
| 7. Headervertrouwen | krijgt backend alleen betrouwbare context? | spoofing- en direct-access-test | geen bypass, juiste headers na allow |

### Voorbeeld: Alice krijgt een 502 op monitoring

Een 502 wijst meestal op een probleem tussen proxy en een volgende service, maar je
controleert dit methodisch.

1. Resolveert `monitoring.bluepeak.test` naar Traefik?
2. Verschijnt de request in Traefik?
3. Werd Alice geauthenticeerd en door `bp-it` toegelaten?
4. Komt de 502 vóór of na de authbeslissing?
5. Wijst de Traefik-service naar `http://monitoring:8080`?
6. Draait de monitoringcontainer en luistert ze op poort 8080?

Als Authentik deny geeft, moet je de backend niet aanpassen. Als Authentik allow geeft
maar Traefik de backend niet bereikt, moet je de groepsbinding niet veranderen.

### Voorbeeld: Eva kan intranet openen

Mogelijke hypotheses:

| Hypothese | Gerichte controle |
|---|---|
| Eva zit per ongeluk in `bp-employees` | groepslidmaatschap controleren |
| application heeft geen binding | application bindings controleren |
| middleware ontbreekt | Traefik-router bekijken |
| bestaande sessie van Alice wordt hergebruikt | nieuw private venster en sessiestart documenteren |
| backend direct geopend | URL, poort en proxylogs controleren |

### Goede foutdocumentatie

```text
Symptoom:
Verwachting:
Waargenomen laag:
Hypothese:
Eén uitgevoerde controle:
Bewijs:
Correctie:
Positieve hertest:
Negatieve hertest:
```

Kernzin:

> Lokaliseer eerst DNS, route, outpost, provider, policy of backend; pas daarna wijzig
> je gericht de configuratie van die laag.

---

## 19. Is dit een vervanging voor VPN?

Nee. Beide technieken lossen een ander primair probleem op.

### Vergelijking

| Eigenschap | VPN | Identity-aware reverse proxy |
|---|---|---|
| Primair doel | beveiligd netwerkpad maken | gecontroleerde toegang tot specifieke webapps |
| Scope | subnetten, hosts en meerdere protocollen | meestal HTTP/HTTPS per hostname |
| Beslissing per webapp | niet automatisch | expliciete applicationpolicy |
| Clientsoftware | vaak nodig | browser volstaat meestal |
| SSH/RDP/databaseverkeer | geschikt mits beleid | meestal niet |
| Groeps- en MFA-context | mogelijk in VPN-platform | centraal onderdeel van appaccess |
| Backendafscherming | nog nodig | nog nodig |
| Fijnmazige appacties | niet opgelost | ook niet volledig opgelost |

### Scenario's

| Requirement | Passende oplossing |
|---|---|
| partner moet één webportaal gebruiken | identity-aware proxy zonder breed netwerkpad |
| beheerder moet via SSH naar switches | VPN naar managementzone en jump server |
| medewerker gebruikt intranet vanuit browser | identity-aware HTTPS kan passen |
| beheerder opent webadmin én beheert servers | identity-aware webtoegang plus VPN voor beheerprotocollen |
| volledige kantoorclient moet interne DNS en fileshares bereiken | VPN of andere gecontroleerde netwerktoegang |

### Waarom beide vaak naast elkaar bestaan

```text
externe medewerker
   |
   +-- browser -> identity-aware proxy -> intranet/helpdesk
   |
   +-- VPN -> jump server -> SSH/RDP naar managementzone
```

De gebruiker krijgt voor gewone webapps geen breed netwerkpad. Voor beheerwerk krijgt
de gebruiker via VPN alleen de noodzakelijke netwerktoegang, eventueel opnieuw met
MFA en devicepolicy.

Kernzin:

> VPN beschermt en begrenst netwerkconnectiviteit; identity-aware access beschermt
> individuele webapplicaties. Ze vullen elkaar aan.

---

## 20. Productiehardening

De workshop gebruikt lokale testhostnames, HTTP, één Traefik-instance, één
Authentik-server en eenvoudige demoapps. Dat maakt de keten zichtbaar, maar is geen
productieontwerp.

### Lab versus productie

| Thema | Labkeuze | Productievereiste | Risico zonder verbetering |
|---|---|---|---|
| Transport | HTTP op lokale hostnames | HTTPS met geldig certificaat | onderschepping van credentials en cookies |
| DNS | hosts file | beheerd intern/publiek DNS | foutieve of inconsistente naamresolutie |
| Traefik-dashboard | lokaal onbeveiligd | afschermen of uitschakelen | configuratie-informatie publiek zichtbaar |
| Backends | intern Docker-netwerk | aparte appzone en expliciete firewallregels | directe bypass van proxy |
| Authentik | enkele instance | passende HA en capacity planning | brede loginuitval |
| Database | één PostgreSQL-container | back-up, herstel en eventueel redundantie | verlies van identityconfiguratie en beschikbaarheid |
| Secrets | lokaal `.env` | secret store, rotatie en toegangsbeheer | credentiallek of moeilijk herstel |
| TOTP | didactische factor | passende factorsterkte en recovery | phishing- en herstelrisico |
| Logging | lokale containerlogs | centrale, beveiligde logging en retentie | zwakke detectie en audit |
| Versies | vastgezet voor het lab | ondersteunde, gepatchte releases | bekende kwetsbaarheden |

### Proxy- en headerhardening

| Controle | Doel |
|---|---|
| betrouwbare `Host` en `X-Forwarded-*`-keten | Authentik moet de oorspronkelijke requestcontext correct kennen |
| alleen bekende proxies vertrouwen | clients mogen forwarded headers niet vervalsen |
| identity-headers overschrijven | voorkomt dat clientwaarden de authcontext beïnvloeden |
| backend alleen vanuit proxyzone bereikbaar | dwingt de vertrouwensroute af |
| outpostpad correct maar minimaal publiceren | authflow werkt zonder andere interne interfaces open te zetten |

### Identity- en policybeheer

| Maatregel | Praktische betekenis |
|---|---|
| periodieke access review | controleert of groepen en bindings nog bij functies passen |
| joiner-mover-leaverproces | past toegang aan wanneer de werkelijkheid verandert |
| apart beheerdersaccount | beperkt dagelijks gebruik van hoge privileges |
| MFA-herstelprocedure | voorkomt onveilige ad-hoc bypasses |
| sessiebeleid | bepaalt passende duur, step-upthreshold en intrekking |
| wijzigingslogboek | koppelt policywijzigingen aan reden, eigenaar en testresultaat |

### Beschikbaarheid en herstel

Een productieplan beantwoordt minstens:

- Wat is de RTO wanneer Authentik uitvalt?
- Hoeveel identitydata mag verloren gaan volgens de RPO?
- Wie kan configuratie herstellen?
- Hoe worden signing keys, database en configuratie veilig geback-upt?
- Hoe test je een upgrade en rollback?
- Welke protected apps zijn kritiek tijdens een IdP-storing?
- Bestaat gecontroleerde noodtoegang?

Kernzin:

> De workshop bewijst de logica van de keten; productie vereist daarnaast TLS,
> segmentatie, secretbeheer, lifecycle, patching, monitoring, redundantie en herstel.

---

## 21. Teststrategie

Een bruikbaar testplan controleert niet alleen functionaliteit, maar ook de
veiligheidsgrenzen en fouttoestanden.

### Functionele en negatieve tests

| Test | Verwacht | Waarom test je dit? |
|---|---|---|
| publieke pagina zonder login | allow | bewijst dat public bewust buiten forward auth staat |
| anoniem naar intranet | loginredirect | bewijst dat protected route de authlaag gebruikt |
| Alice naar intranet | allow | bewijst employee-binding |
| Alice naar monitoring | deny | bewijst scheiding tussen medewerker en IT |
| Bob naar monitoring | allow | bewijst IT-binding |
| Bob met bestaande SSO naar admin | extra TOTP-stap | bewijst step-up in authorization flow |
| Bob met foute TOTP | deny | bewijst echte factorvalidatie |
| Bob met geldige TOTP | allow | bewijst groep en factor samen |
| Alice tijdelijk in admingroep zonder TOTP | deny | bewijst dat registratie/validatie verplicht is |
| Eva naar partnerportaal | allow | bewijst beperkte externe toegang |
| Eva naar intranet | deny | bewijst dat partner geen medewerker is |
| zelf aangeleverde adminheader | geen bypass | test headervertrouwensgrens |
| directe backendpoort | faalt | test backendisolatie |
| onbekende hostname | geen interne app | test default routegedrag |

### Fout- en beschikbaarheidstests

| Test | Verwacht | Waarom? |
|---|---|---|
| verkeerde backendpoort | 502/503 na gerichte route | onderscheidt backendfout van policyfout |
| application uit outpost verwijderen | provider/outpostfout | test technische toewijzing |
| middleware verwijderen | app opent onterecht | toont impact van één ontbrekende control |
| Authentik stoppen | public werkt, nieuwe protected request faalt gesloten | test afhankelijkheid en fail-closed |
| providerlogout | betrokken providersessie eindigt | onderzoekt sessielagen |
| centrale logout | nieuwe centrale auth nodig | onderscheidt provider- en IdP-sessie |

### Bewijs per test

| Bewijs | Wanneer nuttig? | Wat niet opnemen? |
|---|---|---|
| URL en verwacht resultaat | elke testcase | echte productiedomeinen indien gevoelig |
| Traefik-status/logregel | routering en statuscode | onnodige persoonsgegevens |
| Authentik-event | allow, deny, MFA en beheerwijziging | tokens, cookies of secrets |
| backendheaderweergave | bevestigen wat na allow aankomt | volledige gevoelige headerdump |
| `docker compose ps` | bewijzen dat backends geen hostpoort hebben | lokale secrets uit environment |
| korte configuratieuitsnede | middleware, rule of binding toelichten | `.env`, wachtwoorden of TOTP-seeds |

### Vaste testnotatie

```text
Testnaam:
Identiteit en groepen:
Sessiestarttoestand:
URL of actie:
Verwacht resultaat:
Werkelijk resultaat:
Bewijsbron:
Conclusie:
```

Voorbeeld:

```text
Testnaam: partner opent intranet
Identiteit en groepen: eva.partner, alleen bp-partners
Sessiestarttoestand: nieuw private venster
URL: http://intranet.bluepeak.test:8100
Verwacht resultaat: deny
Werkelijk resultaat: deny
Bewijsbron: Authentik applicationevent en geen normale intranetrequest
Conclusie: partnerbinding geeft geen toegang tot employees-app
```

Kernzin:

> Een screenshot van één geslaagde login bewijst alleen dat één pad werkt; een sterke
> teststrategie bewijst ook dat verkeerde identiteiten, bypassroutes en storingen het
> bedoelde veilige resultaat geven.

---

## 22. Samenvatting

Identity-aware access combineert gecontroleerde webpublicatie en centrale identiteit.

Belangrijkste inzichten:

| Inzicht | Wat moet je onthouden? |
|---|---|
| bereikbaarheid is geen identiteit | een IP-adres of VPN-subnet bewijst niet welke mens de app opent |
| Traefik bestuurt het webpad | routers, middleware en services bepalen welke request waarheen gaat |
| Authentik bestuurt identity en policy | gebruikers, groepen, flows en bindings bepalen toegang |
| forward auth controleert vóór de backend | zonder allow hoort de normale request de app niet te bereiken |
| application en provider verschillen | application beschrijft app en doelgroep; provider de technische authkoppeling |
| outposttoewijzing is noodzakelijk | de proxy provider moet door een outpost bediend worden |
| single-app geeft policy per hostname | verschillende groepen en MFA-eisen vragen afzonderlijke providers |
| het outpostpad is technisch noodzakelijk | login, callback, logout en ping moeten correct gerouteerd worden |
| binding vertaalt businessbeleid | groepen geven toegang op basis van zakelijke behoefte |
| step-up MFA moet echt valideren | een geregistreerd device alleen is geen bewijs |
| headers vereisen een vertrouwensgrens | backendisolatie en overschrijven voorkomen spoofing |
| SSO bevat meerdere sessies | providerlogout, centrale logout en appsession zijn niet hetzelfde |
| logs moeten gecorreleerd worden | proxy, Authentik en backend tonen elk een deel van de keten |
| protected hoort fail-closed te zijn | zonder geldige identitybeslissing geen backendtoegang |
| IdP wordt kritieke infrastructuur | HA, back-up, monitoring en herstel zijn nodig |
| VPN blijft een andere bouwsteen | netwerktoegang en webapplicatietoegang vullen elkaar aan |
| tests moeten grenzen bewijzen | allow, deny, spoofing, direct access en storing horen in het plan |

Eindzin:

> Een enterpriseapplicatie is niet veilig gepubliceerd omdat haar hostname en login
> werken, maar omdat routing, identiteit, autorisatie, MFA, sessies,
> backendisolatie, logging en foutgedrag samen aantoonbaar het bedoelde toegangsbeleid
> afdwingen.
