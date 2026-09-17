# Hoofdstuk 8 - Reverse proxies

## 1. Inleiding

In de vorige hoofdstukken heb je gewerkt rond enterprise design, securityzones,
secure management en VPN-toegang.

Daarbij was de centrale vraag vaak:

> Hoe geef je toegang tot interne systemen zonder het interne netwerk te breed open te
> zetten?

In dit hoofdstuk verschuift de focus naar webapplicaties. Organisaties gebruiken onder
meer een intranet, helpdesk, monitoringdashboard, adminportaal, statuspagina en
documentatieplatform. Die applicaties draaien vaak op verschillende servers,
containers, poorten of subnetten.

Wanneer elke applicatie afzonderlijk gepubliceerd wordt, neemt niet alleen het aantal
firewallregels toe, maar groeit ook het aanvalsoppervlak. Ook certificaten, logging,
beveiligingsinstellingen en foutanalyse raken verspreid over meerdere systemen.

Een reverse proxy brengt die toegangslaag samen.

```text
+--------+        +----------------+        +----------------+
| Client | -----> | Reverse proxy  | -----> | Intranet       |
+--------+        +----------------+        +----------------+
                         |
                         +--------------->  | Helpdesk       |
                         |
                         +--------------->  | Statuspagina   |
```

De gebruiker verbindt met de reverse proxy. De reverse proxy onderzoekt de aanvraag,
kiest de juiste interne applicatie en stuurt het verzoek door. Het antwoord loopt langs
dezelfde weg terug.

Kernidee:

> Een reverse proxy is een gecontroleerd toegangspunt voor applicaties. Hij centraliseert
> de publicatie, maar maakt een applicatie niet automatisch veilig.

De rode draad door dit hoofdstuk is:

```text
Hoe bereikt de client de proxy?
Welke regel matcht de aanvraag?
Naar welke backend gaat het verzoek?
Welke beveiliging gebeurt onderweg?
Hoe bewijzen we dat de bedoelde route werkt?
Hoe bewijzen we dat een omweg niet werkt?
```

In de workshop bouwen studenten deze keten met Traefik stap voor stap op. De tool maakt
routers, services, entrypoints en middleware zichtbaar, maar het eigenlijke leerdoel is
het ontwerp achter de tool.

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. het verschil uitleggen tussen een forward proxy en een reverse proxy;
2. beschrijven welk publicatieprobleem een reverse proxy oplost;
3. een HTTP-request stap voor stap volgen van client tot backend;
4. uitleggen welke rol DNS en de HTTP `Host`-header spelen;
5. host-based en path-based routing vergelijken;
6. virtual hosting op één proxy-IP uitleggen;
7. de functie van een Traefik-entrypoint, router, rule, service en middleware uitleggen;
8. static en dynamic configuration in Traefik onderscheiden;
9. publieke luisterpoorten van interne backendpoorten onderscheiden;
10. uitleggen waarom backendservices niet rechtstreeks gepubliceerd worden;
11. TLS termination, TLS passthrough en TLS naar de backend conceptueel onderscheiden;
12. certificaatnamen en hostnames aan elkaar koppelen;
13. forwarded headers als vertrouwensgrens beoordelen;
14. reverse-proxyplaatsing in een DMZ of publicatiezone verantwoorden;
15. least-privilege-firewallregels voor proxyverkeer ontwerpen;
16. security headers en rate limiting correct plaatsen;
17. load balancing, health checks en beschikbaarheid conceptueel uitleggen;
18. logs, statuscodes en dashboardinformatie gebruiken bij troubleshooting;
19. positieve, negatieve en foutinjectietests opstellen;
20. reverse proxy, firewall, NAT, VPN en identity provider van elkaar onderscheiden;
21. labvereenvoudigingen van productievereisten onderscheiden;
22. een reverse-proxyontwerp documenteren en verantwoorden.

---

## 3. Wat doet een reverse proxy precies?

Een reverse proxy ontvangt requests voor één of meer applicaties en stuurt ze door naar
de bijbehorende backends.

De belangrijkste rollen zijn:

| Rol | Wat doet deze rol? | Voorbeeld in de workshop |
|---|---|---|
| client | start een HTTP- of HTTPS-request | browser of `curl.exe` |
| naamresolutie | vertaalt de applicatienaam naar het proxy-IP | hosts file voor `intranet.bluepeak.test` |
| reverse proxy | ontvangt, beoordeelt en routeert het request | Traefik |
| routeringsregel | bepaalt welke requests bij een route horen | `Host(intranet.bluepeak.test)` |
| backendservice | beschrijft waar de doelapplicatie bereikbaar is | `http://intranet:80` |
| backendapplicatie | verwerkt het eigenlijke applicatieverzoek | nginx-container met de intranetpagina |

Een volledige requestflow ziet er als volgt uit:

```text
1. browser vraagt naamresolutie voor intranet.bluepeak.test
2. naam resolveert naar het IP-adres van de reverse proxy
3. browser maakt verbinding met de publieke poort van de proxy
4. browser stuurt een HTTP-request met Host: intranet.bluepeak.test
5. proxy zoekt een router waarvan de rule matcht
6. proxy past eventuele middleware toe
7. router verwijst naar de intranetservice
8. service stuurt het request naar http://intranet:80
9. backend antwoordt aan de proxy
10. proxy antwoordt aan de browser
```

Elke stap kan afzonderlijk slagen of falen.

| Laag | Voorbeeld van een fout | Mogelijk symptoom |
|---|---|---|
| naamresolutie | hostname ontbreekt in DNS of hosts file | naam kan niet gevonden worden |
| client naar proxy | verkeerde hostpoort of firewallblokkering | connection refused of timeout |
| routermatch | verkeerde `Host(...)`-rule | 404 of geen passende router |
| middleware | foutieve redirect of toegangsregel | redirectloop of 403 |
| service | verkeerde backendnaam of -poort | vaak 502 Bad Gateway |
| backend | applicatie zelf faalt | applicatiefout of 5xx-antwoord |

Waarom belangrijk?

> Een reverse-proxyprobleem is geen enkelvoudig probleem. Methodisch troubleshooten
> betekent vaststellen tot welke stap het request geraakt.

Kernzin:

> Naamresolutie brengt de client naar de proxy; de router kiest een service; de service
> bereikt de backend.

---

## 4. Forward proxy versus reverse proxy

Een **forward proxy** werkt namens clients. Een client stuurt uitgaand verkeer naar de
proxy, waarna de proxy de externe bestemming benadert.

```text
+--------+        +---------------+        +----------+
| Client | -----> | Forward proxy | -----> | Internet |
+--------+        +---------------+        +----------+
```

Een **reverse proxy** werkt namens servers of applicaties. De client denkt dat hij de
applicatie benadert, maar maakt eerst verbinding met de proxy.

```text
+--------+        +---------------+        +--------------+
| Client | -----> | Reverse proxy | -----> | Interne app  |
+--------+        +---------------+        +--------------+
```

| Kenmerk | Forward proxy | Reverse proxy |
|---|---|---|
| vertegenwoordigt | clients | servers of applicaties |
| verkeersrichting | typisch uitgaand | typisch inkomend naar gepubliceerde apps |
| kent de client de proxy? | meestal wel of via transparant netwerkbeleid | niet noodzakelijk |
| typische policy | welke websites mag een gebruiker bezoeken? | welke app krijgt dit request? |
| typische logging | gebruikers en externe bestemmingen | hostnames, paden, statuscodes en backends |
| typische plaatsing | tussen clients en internet | voor applicaties, vaak in een publicatiezone |

Praktisch voorbeeld:

| Situatie | Juiste begrip | Waarom? |
|---|---|---|
| school filtert uitgaand webverkeer van studenten | forward proxy | de proxy handelt namens clients |
| bedrijf publiceert drie interne webapps op één IP | reverse proxy | de proxy handelt namens applicaties |
| gebruiker maakt een VPN-tunnel naar kantoor | geen van beide | een VPN levert een beveiligd netwerkpad |

Typische fout:

> Een reverse proxy omschrijven als een oplossing voor al het netwerkverkeer.

Een klassieke reverse proxy behandelt vooral applicatieprotocollen die hij begrijpt,
zoals HTTP en HTTPS. Hij geeft niet automatisch algemene toegang tot SMB, SSH, RDP of
een volledig subnet.

---

## 5. Waarom niet elke applicatie rechtstreeks publiceren?

Stel dat BluePeak Services drie webapplicaties heeft.

| Applicatie | Interne locatie | Functie |
|---|---|---|
| intranet | `10.30.10.21:80` | informatie voor medewerkers |
| helpdesk | `10.30.10.22:8080` | tickets behandelen |
| monitoring | `10.30.20.15:3000` | infrastructuur opvolgen |

Een rechtstreekse publicatie kan er zo uitzien:

```text
Internet -> aparte NAT/firewallregel -> 10.30.10.21:80
Internet -> aparte NAT/firewallregel -> 10.30.10.22:8080
Internet -> aparte NAT/firewallregel -> 10.30.20.15:3000
```

Dat werkt technisch, maar verdeelt de publicatiefunctie over elke backend.

| Probleem | Gevolg in de praktijk |
|---|---|
| elke backend is rechtstreeks bereikbaar | een fout in één app wordt onmiddellijk extern blootgesteld |
| meerdere publieke poorten | gebruikers en firewallbeheerders moeten poortnummers kennen en beheren |
| TLS per applicatie | certificaten, TLS-versies en vernieuwing raken verspreid |
| verspreide logging | incidentonderzoek vraagt correlatie van meerdere logbronnen |
| verschillende beveiligingsinstellingen | de zwakst beheerde applicatie bepaalt mee het risico |
| test- of admininterface per ongeluk gepubliceerd | een niet-bedoelde route kan buiten de centrale controle vallen |
| wijzigende backends | DNS, NAT en firewallregels moeten vaker aangepast worden |
| centrale authenticatie later toevoegen | elke applicatie vraagt een afzonderlijke integratie of ombouw |

Met een reverse proxy wordt het externe pad eenvoudiger:

```text
client -> reverse proxy:443 -> geselecteerde backend
```

| Centrale functie | Wat wordt beheerbaarder? |
|---|---|
| één publicatiepunt | de firewall laat webverkeer alleen naar de proxy toe |
| routing op hostname | gebruikers zien duidelijke applicatienamen in plaats van losse poorten |
| centraal TLS-beheer | certificaten en TLS-policy kunnen op één laag beheerd worden |
| centrale observatie | requests en fouten komen samen in proxylogs |
| gedeelde middleware | headers, redirects of toegangscontroles kunnen herbruikbaar zijn |
| backendafscherming | de client hoeft interne adressen en poorten niet te bereiken |

Belangrijke nuance:

> Een reverse proxy verbergt architectuurdetails, maar **security by obscurity** is geen
> beveiligingsmodel. De echte grens ontstaat door firewallregels, netwerksegmentatie,
> sterke configuratie, patching en toegangscontrole.

Kernzin:

> Publiceer het gecontroleerde toegangspunt, niet elke backend afzonderlijk.

---

## 6. Hostnames, DNS en de `Host`-header

Reverse proxies gebruiken vaak hostnames om meerdere applicaties via hetzelfde IP-adres
te publiceren.

| Hostname | Resolveert naar | Geselecteerde backend |
|---|---|---|
| `intranet.bluepeak.test` | proxy-IP | `intranet:80` |
| `helpdesk.bluepeak.test` | proxy-IP | `helpdesk:80` |
| `status.bluepeak.test` | proxy-IP | `status:80` |

### DNS brengt de client naar de proxy

DNS bepaalt niet welke backend gekozen wordt. DNS zorgt er eerst voor dat de client het
IP-adres van de reverse proxy vindt.

In de workshop wordt DNS tijdelijk nagebootst met een hosts file:

```text
127.0.0.1 intranet.bluepeak.test
127.0.0.1 helpdesk.bluepeak.test
127.0.0.1 status.bluepeak.test
```

Dat is een labvereenvoudiging. In productie beheer je records in interne of publieke
DNS, afhankelijk van wie de applicatie moet bereiken.

### De `Host`-header kiest de webapplicatie

Een HTTP/1.1-request bevat de bedoelde hostname:

```http
GET / HTTP/1.1
Host: intranet.bluepeak.test
```

De reverse proxy leest de `Host`-header en kan daardoor een router selecteren.

Dit verklaart waarom de volgende twee tests niet noodzakelijk hetzelfde resultaat
geven:

```text
http://localhost:8080
http://intranet.bluepeak.test:8080
```

Beide kunnen hetzelfde IP en dezelfde poort bereiken, maar alleen de tweede aanvraag
bevat de hostname waarop de intranetrouter matcht.

Een gerichte test zonder hosts-filewijziging kan de header expliciet zetten:

```text
curl.exe -H "Host: intranet.bluepeak.test" http://127.0.0.1:8080
```

### DNS is geen autorisatie

Een hostname niet publiceren in DNS maakt een applicatie niet automatisch beschermd.
Wie het proxy-IP en de verwachte `Host`-header kent, kan mogelijk nog altijd een request
sturen. Toegang moet daarom door netwerk- en applicatiebeleid worden afgedwongen.

| Controle | Verwacht | Waarom test je dit? |
|---|---|---|
| naam opzoeken | hostname wijst naar proxy-IP | bewijst de naamresolutie |
| request met juiste hostname | juiste applicatie antwoordt | bewijst host-based routing |
| request naar IP zonder juiste hostname | geen interne app of veilige default | controleert het standaardgedrag |
| onbekende hostname | geen interne app | controleert dat er geen te brede catch-all-route is |

Kernzin:

> DNS kiest het proxy-IP; de HTTP-hostname helpt de proxy de applicatie kiezen.

---

## 7. Virtual hosts en host-based routing

Met **virtual hosting** kunnen meerdere websites hetzelfde IP-adres en dezelfde poort
delen. De hostname onderscheidt de applicaties.

```text
één proxy-IP:443
  |
  +-- intranet.bluepeak.example -> intranetservice
  +-- helpdesk.bluepeak.example -> helpdeskservice
  +-- status.bluepeak.example   -> statusservice
```

Bij **host-based routing** kiest de reverse proxy de route op basis van de hostname.

Voorbeeld in Traefik:

```yaml
rule: "Host(`intranet.bluepeak.test`)"
```

| Voordeel | Wat betekent dit concreet? |
|---|---|
| herkenbare URL's | gebruikers openen een naam die bij de applicatie past |
| logische scheiding | cookies, policies en logs kunnen per hostname verschillen |
| één netwerktoegangspunt | meerdere apps delen het proxy-IP en de webpoort |
| flexibel backendbeheer | de interne locatie kan wijzigen zonder de gebruikers-URL te wijzigen |
| centrale uitbreiding | TLS, headers of identity-integratie kunnen per route toegevoegd worden |

Host-based routing scheidt applicaties logisch, maar niet automatisch organisatorisch.
Een route bestaat zodra de configuratie dat zegt. Wie de route mag gebruiken, vraagt
nog altijd expliciete authenticatie en autorisatie.

Typische fout:

> Het DNS-record van `helpdesk.bluepeak.example` wijst rechtstreeks naar de helpdeskserver.

De proxy wordt dan omzeild. Centrale headers, logging of toegangscontroles op de proxy
worden niet toegepast.

Controleer:

```text
hostname -> proxy-IP -> juiste router -> juiste service -> juiste backend
```

---

## 8. Path-based routing

Bij **path-based routing** kiest de proxy een backend op basis van het pad in de URL.

| URL | Mogelijke backend |
|---|---|
| `apps.bluepeak.test/intranet` | intranet |
| `apps.bluepeak.test/helpdesk` | helpdesk |
| `apps.bluepeak.test/status` | status |

```text
apps.bluepeak.test/intranet -> intranet:80
apps.bluepeak.test/helpdesk -> helpdesk:80
```

Deze aanpak kan nuttig zijn wanneer één domein bewust als applicatieportaal wordt
gebruikt. Ze vraagt wel medewerking van de applicatie.

| Mogelijk probleem | Waarom ontstaat dit? | Mogelijke maatregel |
|---|---|---|
| kapotte links | applicatie genereert absolute URL's vanaf `/` | base URL correct instellen of herschrijven |
| ontbrekende CSS of afbeeldingen | assets worden op `/assets` gezocht in plaats van onder het subpad | app subpath-aware maken |
| redirect naar verkeerde locatie | backend kent de externe prefix niet | forwarded prefix of redirectregels configureren |
| botsende cookies | meerdere apps gebruiken dezelfde cookienaam en hetzelfde domein | cookiepath en -namen bewust instellen |
| WebSocket- of API-pad faalt | niet alle subroutes zijn meegenomen | volledige routeboom testen |

Vergelijking:

| Ontwerpvraag | Host-based routing | Path-based routing |
|---|---|---|
| voorbeeld | `helpdesk.example.com` | `apps.example.com/helpdesk` |
| afhankelijk van app-ondersteuning voor subpaden | beperkt | sterk |
| scheiding van cookies en browserorigin | duidelijker per hostname | gedeelde origin vraagt extra aandacht |
| DNS-records | meestal één naam per app | mogelijk één gedeelde naam |
| workshopkeuze | gebruikt | niet gebruikt |

Kernzin:

> Host-based routing is vaak eenvoudiger; path-based routing werkt alleen betrouwbaar
> wanneer de applicatie haar externe pad correct begrijpt.

---

## 9. Traefik als reverse proxy

In de workshop gebruiken we Traefik. De concepten bestaan ook in andere reverse
proxies, al verschillen de namen en configuratiesyntax.

### De requestketen in Traefik

```text
entrypoint -> router + rule -> middleware -> service -> backendserver
```

| Traefik-onderdeel | Vraag die het beantwoordt | Voorbeeld |
|---|---|---|
| entrypoint | op welke lokale poort/protocol ontvangt Traefik verkeer? | `web` luistert op containerpoort 80 |
| router | welke configuratieroute behandelt dit request? | router `intranet` |
| rule | wanneer matcht die router? | `Host(intranet.bluepeak.test)` |
| middleware | welke extra verwerking gebeurt voor of na routing? | security headers toevoegen |
| service | naar welke logische backendgroep gaat het request? | service `intranet` |
| server URL | waar is een concrete backend bereikbaar? | `http://intranet:80` |

Een **Traefik service** is dus niet exact hetzelfde als een Docker Compose-service.
In de workshop krijgen ze bewust dezelfde naam, omdat dit de mapping leesbaar maakt.

```text
Traefik-service intranet
    -> server URL http://intranet:80
    -> Docker Compose-service intranet
    -> nginx luistert in de container op poort 80
```

### Static configuration

Static configuration bepaalt hoe Traefik zelf opstart. In de workshop staan de
instellingen als command-lineopties in `docker-compose.yml`.

| Static instelling | Functie in het lab |
|---|---|
| `--entrypoints.web.address=:80` | laat Traefik intern op poort 80 luisteren |
| `--providers.file.filename=...` | wijst naar het dynamic-configbestand |
| `--providers.file.watch=true` | volgt wijzigingen aan dat bestand |
| `--api.dashboard=true` | schakelt het dashboard in |
| `--api.insecure=true` | publiceert het dashboard onbeveiligd voor het lokale lab |
| `--accesslog=true` | activeert requestlogging |

### Dynamic configuration

Dynamic configuration beschrijft welke applicatieroutes bestaan. In de workshop staat
die configuratie in `traefik/dynamic.yml`.

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

De **file provider** vertelt Traefik dat dit bestand een configuratiebron is. Andere
providers kunnen configuratie uit bijvoorbeeld containerlabels of een orchestrator
halen. De workshop gebruikt de file provider omdat studenten daardoor de volledige
mapping expliciet kunnen lezen.

| Configuratielaag | Wijzig je wanneer... | Workshopbestand |
|---|---|---|
| static | Traefik zelf anders moet starten of luisteren | `docker-compose.yml` |
| dynamic | een app, route, backend of middleware wijzigt | `traefik/dynamic.yml` |

Typische fout:

> Een router bestaat in `dynamic.yml`, maar verwijst naar een servicenaam die niet onder
> `http.services` gedefinieerd is.

Controleer dan afzonderlijk of de router geladen is, of de service geladen is en of de
server URL intern bereikbaar is.

In productie:

> `api.insecure=true` is een labkeuze. Een beheerinterface hoort niet onbeveiligd en
> publiek bereikbaar te zijn.

---

## 10. Publieke poorten en interne backendpoorten

Een reverse-proxyontwerp bevat minstens twee verschillende verbindingen:

```text
client -- frontendverbinding --> proxy -- backendverbinding --> applicatie
```

| Verbinding | Adres in de workshop | Wie moet dit kunnen bereiken? |
|---|---|---|
| client naar proxy | `localhost:8080` | de client op de labhost |
| proxy naar intranet | `intranet:80` | alleen containers op het interne Docker-netwerk |
| dashboard | `localhost:8088` | alleen de student/beheerder in het lab |

De mapping `8080:80` betekent:

```text
hostpoort 8080 -> containerpoort 80 van Traefik
```

Dit zegt niets over de backendpoort. Traefik maakt daarna zelf een nieuwe verbinding
naar `intranet:80` op het Docker-netwerk.

### Waarom een backend geen `ports:` krijgt

Een Docker Compose-backend zonder hostpoort kan nog altijd door Traefik bereikt worden,
omdat beide containers lid zijn van `appnet`.

```yaml
intranet:
  image: nginx:alpine
  networks:
    - appnet
```

Wanneer een student dit toevoegt:

```yaml
ports:
  - "8081:80"
```

ontstaat een tweede pad:

```text
bedoeld: client -> Traefik:8080 -> intranet:80
omweg:   client -> host:8081    -> intranet:80
```

Via de omweg gelden proxylogging, middleware en latere authenticatie mogelijk niet.

| Test | Verwacht | Wat bewijst dit? |
|---|---|---|
| juiste hostname via poort 8080 | applicatie werkt | het bedoelde proxypad is actief |
| `localhost:8081` | verbinding faalt | intranet heeft geen rechtstreekse hostpublicatie |
| `localhost:8082` | verbinding faalt | helpdesk heeft geen rechtstreekse hostpublicatie |
| `localhost:8083` | verbinding faalt | status heeft geen rechtstreekse hostpublicatie |

Belangrijke nuance:

> Geen Docker-hostpoort is een nuttige labcontrole, maar productieafscherming vraagt ook
> netwerksegmentatie en firewallbeleid. Een andere host in hetzelfde backendnetwerk kan
> de service mogelijk nog rechtstreeks bereiken.

Kernzin:

> De frontendpoort publiceert de proxy; de backendpoort blijft alleen bereikbaar vanaf
> de noodzakelijke proxyzone.

---

## 11. TLS termination en certificaten

TLS beschermt HTTP-verkeer tegen meelezen en ongewenste wijziging tijdens transport.
Bij HTTPS moet bovendien de certificaatnaam passen bij de hostname die de client opent.

### TLS termination

Bij **TLS termination** eindigt de TLS-verbinding van de client op de reverse proxy.
De proxy ontsleutelt het request en maakt daarna een afzonderlijke verbinding naar de
backend.

```text
client -- HTTPS --> reverse proxy -- HTTP --> backend
```

| Voordeel | Praktische betekenis |
|---|---|
| centraal certificaatbeheer | vernieuwing en configuratie gebeuren op de publicatielaag |
| centrale TLS-policy | oude protocollen of zwakke ciphers hoeven niet per backend beheerd te worden |
| inhoud inspecteerbaar op proxy | routing, headers, logging en toegangsbeleid kunnen op HTTP-niveau werken |
| ondersteuning voor oudere backends | een interne app zonder moderne TLS kan achter een moderne frontend staan |

Het laatste voordeel is ook een risico: de backendverbinding is dan niet versleuteld.

### TLS naar de backend

De proxy kan na termination opnieuw TLS gebruiken:

```text
client -- HTTPS --> reverse proxy -- HTTPS --> backend
```

Dit wordt soms **TLS re-encryption** genoemd. Er bestaan dan twee afzonderlijke
TLS-sessies. De proxy moet het backendcertificaat correct valideren. Validatie
uitschakelen om een foutmelding weg te krijgen, verplaatst het probleem naar de
vertrouwenslaag.

### TLS passthrough

Bij **TLS passthrough** stuurt de proxy het versleutelde verkeer door zonder het zelf te
ontsleutelen.

```text
client -- versleutelde TLS-verbinding ----------------> backend
                  reverse proxy stuurt door
```

De proxy heeft dan minder mogelijkheden om HTTP-headers, paden of inhoud te inspecteren.
Routing kan bij TLS vaak nog op basis van SNI, maar HTTP-middleware is niet op dezelfde
manier beschikbaar.

| Model | TLS eindigt op | Kan proxy HTTP-inhoud inspecteren? | Typisch aandachtspunt |
|---|---|---|---|
| termination + HTTP-backend | proxy | ja | backendtraject is onversleuteld |
| termination + HTTPS-backend | proxy en daarna backend | ja | twee certificaatrelaties beheren |
| passthrough | backend | nee | minder L7-functionaliteit op proxy |

### Certificaten en namen

Een certificaat koppelt een cryptografische identiteit aan één of meer DNS-namen.

| Certificaatkeuze | Waarvoor bruikbaar? | Aandachtspunt |
|---|---|---|
| certificaat per hostname | afzonderlijke appnamen | meer certificaten beheren |
| multi-domaincertificaat | vaste set namen | wijzigingen vragen uitbreiding of heruitgifte |
| wildcardcertificaat | meerdere subdomeinen onder één zone | privésleutel heeft impact op veel namen |
| publieke CA | publiek vertrouwde namen | validatie en automatische vernieuwing organiseren |
| interne CA | interne bedrijfsnamen en clients | clients moeten de interne CA vertrouwen |
| self-signed | tijdelijk lokaal lab | browserwaarschuwing en geen schaalbaar trustmodel |

Een certificaat bewijst niet dat de applicatie veilig geprogrammeerd, gepatcht of juist
geautoriseerd is. Het beschermt de TLS-verbinding en helpt de client de endpointnaam te
controleren.

### Hostname vóór en na TLS

Bij HTTPS wordt de TLS-sessie opgezet vóór het HTTP-request gelezen kan worden. De
client stuurt daarom via **Server Name Indication** of SNI al vroeg de bedoelde
servernaam mee. Na ontsleuteling bevat HTTP ook de `Host`-header.

Controleer bij een certificaatfout:

| Controle | Vraag |
|---|---|
| DNS | bereikt de naam het juiste proxy-IP? |
| SNI/hostname | vraagt de client de bedoelde naam? |
| certificaatnamen | staat die naam in de SAN-velden van het certificaat? |
| trust chain | vertrouwt de client de uitgevende CA? |
| geldigheid | is het certificaat nog geldig? |

In de workshop:

> De workshop gebruikt bewust HTTP op localhost zodat routing eerst zichtbaar wordt.
> Dat is geen productieontwerp.

---

## 12. Clientinformatie en forwarded headers

De backend ziet vaak de reverse proxy als directe netwerkpeer. Zonder extra context kan
de applicatie daardoor het oorspronkelijke clientadres of protocol verliezen.

Reverse proxies voegen vaak headers toe zoals:

| Header | Mogelijke betekenis voor de backend |
|---|---|
| `X-Forwarded-For` | oorspronkelijk clientadres en eventuele proxyketen |
| `X-Forwarded-Proto` | oorspronkelijk protocol, bijvoorbeeld `https` |
| `X-Forwarded-Host` | oorspronkelijke hostname |
| `Forwarded` | gestandaardiseerde combinatie van forwardinginformatie |

Voorbeeld:

```text
client 203.0.113.25 -> proxy 10.20.0.10 -> backend 10.30.0.21

backend ziet als TCP-peer: 10.20.0.10
X-Forwarded-For: 203.0.113.25
X-Forwarded-Proto: https
```

Deze headers vormen een vertrouwensgrens. Een client kan zelf een
`X-Forwarded-For`-header meesturen. De proxy moet onbetrouwbare waarden daarom
overschrijven of gecontroleerd aanvullen. De backend mag forwarded headers alleen
vertrouwen wanneer het request van een gekende proxy komt.

| Foute aanname | Mogelijk gevolg |
|---|---|
| elke clientheader vertrouwen | aanvaller vervalst bronadres of protocolinformatie |
| backend rechtstreeks bereikbaar laten | client omzeilt de vertrouwde proxy en levert zelf headers aan |
| `X-Forwarded-Proto` niet verwerken | applicatie bouwt `http`-redirects of onveilige cookies |
| meerdere proxies niet documenteren | onduidelijk welk adres in de keten betrouwbaar is |

Kernzin:

> Forwarded headers zijn alleen betrouwbaar wanneer de volledige proxyketen en haar
> trust boundaries gekend zijn.

---

## 13. Reverse-proxyplaatsing en DMZ

Een internetgerichte reverse proxy staat vaak in een DMZ of afzonderlijke
publicatiezone. Daardoor komt een inkomend request niet rechtstreeks in de interne
appzone terecht.

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

De plaatsing alleen is niet voldoende. De toegelaten flows bepalen of de segmentatie
effectief iets beperkt.

| Bron | Bestemming | Poort | Actie | Reden |
|---|---|---:|---|---|
| internet | reverse proxy | 443 | allow | bedoelde publieke HTTPS-toegang |
| internet | backendzone | any | deny | rechtstreekse backendtoegang blokkeren |
| reverse proxy | intranetbackend | 80 of 443 | allow | noodzakelijke applicatieflow |
| reverse proxy | helpdeskbackend | 80 of 443 | allow | noodzakelijke applicatieflow |
| reverse proxy | beheerzone | any | deny | compromis van proxy mag beheer niet openen |
| beheernetwerk | proxybeheer | specifieke beheerpoort | allow | gecontroleerd beheerpad |

### Least connectivity

Least privilege geldt ook voor netwerkverbindingen:

> De proxy mag alleen de backends en poorten bereiken die nodig zijn voor zijn
> publicatiefunctie.

Een regel `reverse proxy -> intern netwerk -> any` maakt van de proxy een krachtige
springplank bij compromis.

### Interne en externe applicaties

Niet elke reverse proxy hoeft internetgericht te zijn. Een organisatie kan ook een
interne reverse proxy gebruiken voor applicaties die alleen vanaf het bedrijfsnetwerk
of via VPN bereikbaar zijn.

| Applicatietype | Mogelijke bereikbaarheid | Ontwerpvraag |
|---|---|---|
| publiek klantenportaal | internet naar publicatieproxy | welke routes zijn echt publiek? |
| medewerkersintranet | intern netwerk of VPN naar interne proxy | waarom zou dit internetgericht zijn? |
| adminportaal | alleen beheernetwerk via aparte route | zijn sterke authenticatie en bronbeperking actief? |
| partnerportaal | beperkte externe publicatie | hoe worden partners geïdentificeerd en gelogd? |

In productie:

> Publiceer niet automatisch alle routes van één proxy naar hetzelfde publiek. De
> doelgroep van elke applicatie bepaalt DNS, netwerktoegang en identitybeleid.

---

## 14. Backends afschermen

Een backend is correct afgeschermd wanneer het bedoelde pad via de proxy werkt en
onbedoelde rechtstreekse paden geblokkeerd zijn.

Dat vraagt meerdere maatregelen:

| Maatregel | Wat beperkt dit? |
|---|---|
| geen rechtstreekse hostpoort in het Docker-lab | lokale omweg rond Traefik |
| aparte backendzone | algemene bereikbaarheid vanuit clientnetwerken |
| firewallregel proxy naar specifieke backendpoort | laterale beweging vanuit de proxyzone |
| backend luistert alleen waar nodig | onnodige netwerkinterfaces en services |
| beheerinterface op apart beheerpad | blootstelling van beheerfuncties via gebruikersroute |
| authenticatie op backend of vertrouwde proxy-integratie | ongeautoriseerde applicatietoegang |
| logging op proxy én backend | vergelijking tussen frontendrequest en backendverwerking |

De reverse proxy is geen vervanging voor backendbeveiliging. Een kwetsbare applicatie
blijft kwetsbaar wanneer haar normale route via een proxy loopt.

Defense in depth:

```text
DNS en duidelijke naamgeving
        + netwerksegmentatie
        + firewallregels
        + reverse-proxyrouting
        + TLS
        + authenticatie en autorisatie
        + veilige applicatie
        + logging en monitoring
```

Typische fout:

> De backend is niet publiek in DNS opgenomen, dus hij is veilig.

DNS verbergen blokkeert geen netwerkpad. Test de bereikbaarheid vanaf relevante zones
en controleer de firewall- en containerpublicatie effectief.

---

## 15. Security headers

Een reverse proxy kan HTTP-responseheaders centraal toevoegen. Zulke headers sturen
het beveiligingsgedrag van de browser.

| Header | Doel | Belangrijke nuance |
|---|---|---|
| `X-Content-Type-Options: nosniff` | voorkomt dat de browser bepaalde contenttypes probeert te raden | correct `Content-Type` blijft nodig |
| `X-Frame-Options: DENY` | beperkt insluiten in frames en daarmee klassieke clickjacking | kan legitieme embedding blokkeren |
| `Referrer-Policy` | beperkt welke broninformatie naar een volgende site gaat | kies beleid volgens applicatiebehoefte |
| `Strict-Transport-Security` | laat de browser volgende bezoeken alleen via HTTPS uitvoeren | alleen gebruiken wanneer HTTPS blijvend correct is |
| `Content-Security-Policy` | beperkt toegelaten bronnen voor scripts, styles en andere content | vereist testen per applicatie; te brede policy helpt weinig |

In de workshop maakt Traefik een middleware:

```yaml
middlewares:
  security-headers:
    headers:
      contentTypeNosniff: true
      frameDeny: true
      referrerPolicy: "strict-origin-when-cross-origin"
```

Een middleware bestaat pas functioneel wanneer een router ernaar verwijst.

```yaml
middlewares:
  - security-headers
```

| Test | Verwacht | Waarom test je dit? |
|---|---|---|
| `curl.exe -I` naar intranet | drie verwachte headers | middleware werkt op intranetroute |
| dezelfde test naar helpdesk | dezelfde headers | middleware is ook daar gekoppeld |
| headers in backend zelf vergelijken | proxyheaders ontbreken mogelijk rechtstreeks | toont waar de header wordt toegevoegd |

Security headers vervangen geen invoervalidatie, patching, TLS, authenticatie of
autorisatie. Ze beperken specifieke browserrisico's.

Typische fout:

> HSTS toevoegen aan een lokaal HTTP-only lab.

HSTS heeft alleen betekenis wanneer HTTPS correct en duurzaam beschikbaar is. Een fout
HSTS-beleid kan gebruikers langdurig naar een onbereikbare HTTPS-versie dwingen.

---

## 16. Rate limiting en andere requestcontroles

Rate limiting beperkt hoeveel requests binnen een bepaalde periode worden toegelaten.

| Doel | Wat kan rate limiting doen? | Wat kan het niet bewijzen? |
|---|---|---|
| brute force afremmen | aantal snelle loginpogingen beperken | dat de login zelf sterk beveiligd is |
| backend beschermen | pieken per client of route afvlakken | volledige bescherming tegen grote DDoS-aanvallen |
| misbruik beperken | dure API-calls begrenzen | dat elke toegelaten call legitiem is |
| logs beheersbaar houden | herhalende requests vertragen | dat er geen aanval plaatsvindt |

Een limiet vraagt context. Tien requests per seconde kan streng zijn voor een mens,
maar te laag voor een API of te hoog voor een gevoelige loginroute.

| Ontwerpvraag | Waarom nodig? |
|---|---|
| waarop tel je? | bron-IP, gebruiker, API-key en route geven andere resultaten |
| over welk tijdvenster? | korte bursts en langdurig misbruik vragen ander beleid |
| wat gebeurt bij overschrijding? | blokkeren, vertragen en loggen hebben verschillende impact |
| welke gedeelde clients bestaan? | NAT kan veel gebruikers achter één bron-IP plaatsen |
| waar gebeurt de controle? | edge, reverse proxy en applicatie zien niet altijd dezelfde identiteit |

Andere mogelijke controles zijn request-bodylimieten, time-outs, methodebeperkingen en
regels voor specifieke paden. Elke controle moet aansluiten bij het gedrag van de
applicatie. Een te korte timeout kan bijvoorbeeld legitieme rapporten of uploads breken.

Kernzin:

> Rate limiting vermindert specifieke vormen van misbruik, maar is geen vervanging voor
> authenticatie, capaciteitsplanning of DDoS-bescherming.

---

## 17. Load balancing, health checks en beschikbaarheid

Een reverse proxy kan één logische service over meerdere backendservers verdelen.

```text
                    +--> intranet-1:80
client -> proxy ----+--> intranet-2:80
                    +--> intranet-3:80
```

Daarom heet het Traefik-onderdeel in de configuratie een `loadBalancer`, ook wanneer de
workshop maar één server URL bevat.

| Onderdeel | Functie |
|---|---|
| backendpool | verzamelt instanties die dezelfde applicatie leveren |
| verdeelalgoritme | kiest welke gezonde instantie het volgende request krijgt |
| health check | controleert of een backend geschikt is om verkeer te ontvangen |
| timeout | voorkomt dat een vastgelopen backend onbeperkt resources bezet |
| retry | probeert onder voorwaarden opnieuw, maar kan bij niet-idempotente requests riskant zijn |
| session affinity | houdt een client eventueel bij dezelfde backend |

### Health check is meer dan een open poort

Een TCP-poort kan open zijn terwijl de applicatie niet bruikbaar is. Een zinvolle
applicatie-healthcheck controleert daarom een doelgericht endpoint.

| Healthcheck | Wat bewijst dit? | Wat bewijst dit niet? |
|---|---|---|
| TCP-connectie | proces luistert op een poort | applicatie en databank werken |
| HTTP `200` op `/health` | webservice kan dat endpoint beantwoorden | volledige gebruikersflow werkt |
| readinesscheck met dependencies | instantie is klaar voor requests | elk businessproces is correct |

### De proxy zelf is ook een failure domain

Centralisatie maakt beheer eenvoudiger, maar creëert een kritisch component. Eén
reverse-proxyinstance zonder redundantie kan een single point of failure zijn.

In productie denk je na over:

| Vraag | Waarom belangrijk? |
|---|---|
| meerdere proxyinstances | uitval van één node mag niet alle apps blokkeren |
| load balancer of failover voor de proxies | clients moeten een gezonde proxy vinden |
| gedeelde of gesynchroniseerde configuratie | alle instances moeten dezelfde bedoelde routes kennen |
| certificaatbeheer | elke actieve instance moet correct TLS kunnen afhandelen |
| monitoring | route-, backend- en certificaatproblemen moeten tijdig zichtbaar zijn |
| capaciteitsplanning | de centrale laag moet de som van het applicatieverkeer aankunnen |

De workshop gebruikt één Traefik-container en één backend per applicatie. Dat is
geschikt om routing te leren, niet om high availability aan te tonen.

---

## 18. Logging en observability

Een reverse proxy is een waardevol observatiepunt omdat veel applicatieverkeer erdoor
loopt.

### Access logs en systeemlogs

| Logtype | Mogelijke inhoud | Gebruik |
|---|---|---|
| access log | hostname, pad, methode, statuscode, duur en clientcontext | requests en responspatronen onderzoeken |
| proxy-/systeemlog | geladen configuratie, routerfouten en backendconnecties | werking van Traefik zelf onderzoeken |
| backendlog | applicatiefout, intern pad en verwerking | bepalen wat na forwarding gebeurde |

Een proxylog alleen vertelt niet altijd waarom de backend intern faalde. Correlatie met
backendlogs blijft nodig.

### Statuscodes in context

| Code | Mogelijke betekenis | Eerste controlevraag |
|---:|---|---|
| 200 | request is succesvol beantwoord | kwam de verwachte applicatie-inhoud terug? |
| 301/302 | redirect | zijn doellocatie en protocol correct? |
| 401 | authenticatie nodig of mislukt | komt dit antwoord van proxy of backend? |
| 403 | request begrepen maar niet toegestaan | welke policy heeft geweigerd? |
| 404 | route of applicatiepad niet gevonden | matchte een router en bestaat het backendpad? |
| 429 | rate limit bereikt | welke limiet en identiteit telden mee? |
| 502 | ongeldige of mislukte respons van upstream | zijn backendnaam, poort en protocol correct? |
| 503 | service tijdelijk niet beschikbaar | zijn er gezonde backendinstanties? |
| 504 | upstream antwoordt niet tijdig | is backend traag, onbereikbaar of timeout te kort? |

Een statuscode is een aanwijzing, geen volledige diagnose. Dezelfde code kan door de
proxy of door de applicatie gegenereerd zijn.

### Wat log je bewust niet?

Requests kunnen gevoelige informatie bevatten.

| Gegeven | Risico bij logging |
|---|---|
| `Authorization`-header | token of credential kan uitlekken |
| sessiecookie | actieve sessie kan misbruikt worden |
| queryparameters | zoektermen, persoonsgegevens of tokens kunnen zichtbaar worden |
| requestbody | formulieren en API-payloads kunnen gevoelige data bevatten |

Goede logging zoekt een evenwicht tussen troubleshooting, auditwaarde, privacy,
bewaartermijnen en toegang tot de logs.

### Zinvol bewijs in de workshop

| Bewijs | Wat toont dit? |
|---|---|
| access-logregel met hostname en 200 | request liep via Traefik |
| dashboard met drie routers en services | dynamic configuration is geladen |
| security headers in `curl.exe -I` | middleware beïnvloedt het antwoord |
| log bij foute backendpoort | client bereikt proxy, maar proxy bereikt backend niet correct |

In productie:

> Een onbeveiligd dashboard is zelf een risico. Beperk beheerinterfaces tot een
> beheernetwerk, bescherm ze met sterke authenticatie en log beheeracties.

---

## 19. Methodisch troubleshooten

Wijzig niet willekeurig meerdere instellingen tegelijk. Start aan de clientzijde en
volg het request tot het punt waar bewijs ontbreekt.

```text
naam -> netwerkpad -> entrypoint -> router -> middleware -> service -> backend -> antwoord
```

| Stap | Vraag | Mogelijke controle |
|---:|---|---|
| 1 | resolveert de hostname naar de proxy? | hosts file, DNS-lookup |
| 2 | is de frontendpoort bereikbaar? | `curl.exe`, connectietest, firewalllog |
| 3 | bevat het request de juiste hostname? | URL of expliciete `Host`-header |
| 4 | is de router geladen en matcht de rule? | Traefik-dashboard en configuratie |
| 5 | is de juiste middleware gekoppeld? | headers, redirectgedrag, dashboard |
| 6 | verwijst de router naar de juiste service? | `dynamic.yml` |
| 7 | kloppen backendnaam, poort en protocol? | service URL, interne naamresolutie |
| 8 | antwoordt de backend zelf? | backendlog of test vanuit de proxyzone |
| 9 | komt het verwachte antwoord terug? | statuscode én inhoud controleren |

### Voorbeeld: verkeerde backendpoort

De helpdeskservice wordt tijdelijk gewijzigd naar:

```yaml
url: "http://helpdesk:8088"
```

Redenering:

1. De hostname resolveert nog altijd naar Traefik.
2. De client kan de proxypoort nog bereiken.
3. De helpdeskrouter matcht nog altijd.
4. Alleen de verbinding van proxy naar backend is fout.
5. Andere routes kunnen normaal blijven werken.

Deze fout bewijst waarom de frontendpoort en backendpoort niet door elkaar gehaald
mogen worden.

### Eén variabele per test

Wanneer je tegelijk DNS, routerrule en backendpoort wijzigt, weet je na een succesvolle
test niet welke wijziging nodig was. Verander daarom één hypothese per keer en noteer
het resultaat.

Kernzin:

> Troubleshooting is aantonen tot waar het request geraakt, niet instellingen proberen
> tot het toevallig werkt.

---

## 20. Typische fouten en betere aanpakken

| Fout | Waarschijnlijk gevolg | Betere aanpak |
|---|---|---|
| hostname wijst naar backend | proxy wordt omzeild | DNS naar de proxy laten wijzen |
| hosts file ontbreekt | labnaam resolveert niet | naamresolutie eerst controleren |
| alleen `localhost:8080` testen | routerrule matcht niet | juiste hostname of `Host`-header gebruiken |
| backend krijgt een hostpoort | app is rechtstreeks bereikbaar | alleen proxyfrontend publiceren |
| router ontbreekt | geen passende route | dynamic config en dashboard controleren |
| rule bevat verkeerde hostname | request matcht niet | verwachte en werkelijke hostname vergelijken |
| router verwijst naar verkeerde service | configuratie- of upstreamfout | objectnamen systematisch volgen |
| verkeerde backendnaam | naamresolutie tussen containers faalt | Compose-servicenaam en netwerk controleren |
| verkeerde backendpoort | vaak 502 | interne luisterpoort controleren |
| HTTP naar HTTPS-backend of omgekeerd | TLS-handshake- of upstreamfout | frontend- en backendprotocol documenteren |
| middleware bestaat maar is niet gekoppeld | headers of policy ontbreken | routerconfiguratie controleren |
| HSTS op HTTP-only omgeving | onverwacht browsergedrag | pas na werkende HTTPS activeren |
| forwarded headers blind vertrouwen | vervalste clientcontext | alleen gekende proxies vertrouwen |
| admininterface publiek | gevoelige configuratie of beheerfunctie zichtbaar | apart en sterk beschermd beheerpad |
| firewallregel naar heel intern netwerk | groot lateraal bereik bij compromis | alleen noodzakelijke backendflows toelaten |
| alleen 200-status controleren | verkeerde app kan toch antwoorden | ook inhoud en hostname controleren |
| alleen positieve tests | omwegen en te brede routes blijven onzichtbaar | positieve en negatieve tests combineren |
| alleen proxylog bekijken | backendoorzaak blijft onbekend | proxy- en backendlogs correleren |
| meerdere wijzigingen tegelijk | oorzaak blijft onduidelijk | één hypothese per test |

Gebruik bij elke fout dezelfde classificatievragen:

- Is dit naamresolutie?
- Is dit client-naar-proxyconnectiviteit?
- Is dit een routermatch?
- Is dit middlewaregedrag?
- Is dit proxy-naar-backendconnectiviteit?
- Is dit een backendapplicatiefout?
- Is dit een TLS- of vertrouwensprobleem?

Die indeling voorkomt trial-and-error.

---

## 21. Reverse proxy, firewall, NAT, VPN en identity

Deze componenten vullen elkaar aan, maar lossen verschillende problemen op.

| Component | Centrale vraag | Wat levert het? | Wat levert het niet automatisch? |
|---|---|---|---|
| firewall | welke netwerkflow mag passeren? | filtering op netwerk- en transportlaag | applicatie-identiteit of correcte webroute |
| NAT/PAT | welk adres of poortnummer wordt vertaald? | adres- en poortvertaling | authenticatie of applicatieve routing |
| reverse proxy | welke webapp krijgt dit request? | L7-publicatie en centrale webfuncties | algemene netwerktoegang of gebruikersidentiteit |
| VPN | welk beveiligd netwerkpad krijgt de client? | tunnel en bereikbaarheid volgens VPN-policy | publicatie per webhostname |
| identity provider | wie is de gebruiker en hoe authenticeert die? | centrale identiteit, login en mogelijk MFA | netwerksegmentatie of backendrouting |
| applicatie | wat mag de gebruiker binnen de app doen? | businesslogica en fijnmazige autorisatie | netwerkperimeterbeheer |

Voorbeeld van een gecombineerd ontwerp:

```text
externe medewerker
    |
    | HTTPS
    v
firewall -> reverse proxy -> identitycontrole -> helpdeskbackend

beheerder
    |
    | VPN
    v
beheernetwerk -> apart adminpad
```

Een reverse proxy kan een webapp ook alleen intern of via VPN publiceren. De keuze
hangt af van de doelgroep en het risico, niet van de aanwezigheid van de proxy zelf.

Kernzin:

> De firewall beperkt netwerkflows, de reverse proxy routeert webrequests en de
> identitylaag bepaalt wie toegang krijgt.

---

## 22. Reverse proxy en centrale identiteit

De reverse proxy in dit hoofdstuk routeert op technische requestkenmerken zoals
hostname en pad. Hij weet nog niet automatisch welke menselijke gebruiker het request
stuurt.

Dat leidt tot een volgende ontwerpstap:

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

In hoofdstuk 9 komt centrale identiteit met Authentik aan bod. In hoofdstuk 10 worden
reverse proxy en identity samengebracht voor applicaties die bescherming voor de
backend nodig hebben.

| Laag | Verantwoordelijkheid |
|---|---|
| reverse-proxyrule | request aan een applicatie koppelen |
| identity provider | gebruiker authenticeren en identitycontext leveren |
| access policy | bepalen welke identiteit de applicatie mag openen |
| backendapplicatie | rechten binnen de applicatie afdwingen |

Typische fout:

> De route bestaat alleen voor `status.bluepeak.test`, dus alleen IT kan ze gebruiken.

Een hostname is geen gebruikersautorisatie. Zonder toegangsbeleid kan iedereen die het
netwerkpad bereikt mogelijk de route aanvragen.

Kernzin:

> Eerst publiceer je de applicatie technisch correct; daarna koppel je identiteit en
> least-privilege-toegang aan die route.

---

## 23. Testplan en bewijsvoering

Een goed reverse-proxytestplan bevat meer dan geslaagde paginaweergaven.

### Vier soorten tests

| Testsoort | Vraag | Voorbeeld |
|---|---|---|
| positieve test | werkt het bedoelde pad? | intranet via juiste hostname geeft 200 en juiste inhoud |
| negatieve test | is een onbedoeld pad geblokkeerd? | directe backendhostpoort faalt |
| scheidingstest | komt elk request bij de juiste app? | helpdeskhostname toont geen intranetinhoud |
| foutinjectie | herkennen we een gecontroleerde fout? | verkeerde backendpoort veroorzaakt herkenbare upstreamfout |

### Testmatrix voor de workshop

| Test | Verwacht | Waarom test je dit? | Zinvol bewijs |
|---|---|---|---|
| `intranet.bluepeak.test:8080` | intranet, status 200 | router en service werken | response + access log |
| `helpdesk.bluepeak.test:8080` | helpdesk, status 200 | tweede virtual host werkt | inhoud + dashboardrouter |
| `status.bluepeak.test:8080` | statuspagina, status 200 | derde virtual host werkt | inhoud + access log |
| onbekende hostname | geen interne app | geen te brede default route | status en response |
| `localhost:8081` | verbinding faalt | intranet niet rechtstreeks gepubliceerd | terminaloutput + `docker compose ps` |
| `localhost:8082` | verbinding faalt | helpdesk niet rechtstreeks gepubliceerd | terminaloutput |
| `localhost:8083` | verbinding faalt | status niet rechtstreeks gepubliceerd | terminaloutput |
| headers op elke hostname | verwachte drie headers | middleware is overal gekoppeld | `curl.exe -I` |
| verkeerde helpdeskpoort | proxy-/upstreamfout | fout tussen proxy en backend herkenbaar | logregel + analyse |
| herstel naar poort 80 | helpdesk werkt opnieuw | hypothese en correctie kloppen | nieuwe response |

### Een sterke testbeschrijving

```text
Test: helpdesk openen via de reverse proxy
Request: http://helpdesk.bluepeak.test:8080
Verwachting: HTTP 200 en inhoud van de helpdeskpagina
Bewijs: responseheaders, herkenbare pagina-inhoud en Traefik access log
Conclusie: naamresolutie, frontendpoort, router en backendservice werken samen
```

Een screenshot van een pagina bewijst niet dat de backend afgeschermd is. Daarvoor is
een afzonderlijke negatieve test nodig.

### Interpretatie van een mislukte negatieve test

Wanneer `localhost:8081` onverwacht werkt, is dat geen succes omdat er "meer
bereikbaarheid" is. Het bewijst dat een omweg rond de proxy bestaat.

Kernzin:

> Een publicatieontwerp is pas aangetoond wanneer het bedoelde pad werkt en de bedoelde
> grenzen niet omzeild kunnen worden.

---

## 24. Van lab naar productie

De workshop maakt de requestketen bewust klein en zichtbaar. Productie vraagt extra
keuzes.

| Thema | Labkeuze | Productievereiste |
|---|---|---|
| naamresolutie | lokale hosts file | beheerde interne of publieke DNS-records |
| frontendprotocol | HTTP op `localhost:8080` | HTTPS met geldig certificaat en TLS-policy |
| proxybeschikbaarheid | één Traefik-container | redundantie, monitoring en herstelplan |
| dashboard | `api.insecure=true` op `localhost:8088` | geen publieke insecure API; beschermd beheerpad |
| backends | één gedeeld Docker-netwerk | gesegmenteerde appzone en expliciete firewallregels |
| backend-TLS | HTTP | risico beoordelen en waar nodig TLS met certificaatvalidatie |
| secrets | geen secrets in deze oefening | secretmanagement en rotatie |
| configuratie | lokaal bestand | versiebeheer, review, gecontroleerde deployment en rollback |
| logging | lokale containerlogs | centrale logs, retentie, privacy en alerting |
| health | eenvoudige statische nginxpagina | healthchecks die relevante dependencies meenemen |
| toegang | nog geen gebruikersauthenticatie | identity-, MFA- en autorisatiebeleid volgens doelgroep |
| capaciteit | beperkt lokaal verkeer | time-outs, limieten, schaal en piekbelasting testen |

### Productievragen per applicatie

| Vraag | Waarom moet je dit documenteren? |
|---|---|
| Wie is de doelgroep? | bepaalt of de app publiek, intern, via VPN of via partnernetwerk bereikbaar is |
| Welke hostname blijft stabiel? | beïnvloedt DNS, certificaten, cookies en integraties |
| Waar eindigt TLS? | bepaalt welke netwerksegmenten leesbare HTTP-inhoud zien |
| Welke backendflows zijn nodig? | vormt de basis voor least-privilege-firewallregels |
| Hoe wordt de gebruiker geïdentificeerd? | voorkomt dat bereikbaarheid met autorisatie verward wordt |
| Welke forwarded headers vertrouwt de app? | beschermt bron- en protocolcontext tegen spoofing |
| Welke time-outs en groottelimieten gelden? | voorkomt uitval of misbruik zonder legitiem gebruik te breken |
| Welke logs en metrics zijn nodig? | maakt incidentonderzoek en capaciteitsbeheer mogelijk |
| Wat gebeurt bij proxy- of backenduitval? | bepaalt beschikbaarheid en failovergedrag |
| Wie beheert de route en het certificaat? | maakt lifecycle en verantwoordelijkheid expliciet |

### Wijzigingsbeheer

Een nieuwe route is een securityrelevante wijziging. Ze kan een interne applicatie
bereikbaar maken voor een nieuwe doelgroep.

Een beheerbaar proces bevat daarom:

1. een beschreven applicatie-eigenaar en doelgroep;
2. review van hostname, route, middleware en backendflow;
3. positieve en negatieve tests;
4. gecontroleerde deployment;
5. monitoring na de wijziging;
6. een rollbackmogelijkheid;
7. verwijdering van routes wanneer de applicatie verdwijnt.

Lifecyclebeheer geldt dus niet alleen voor gebruikers, maar ook voor applicatieroutes,
DNS-records, certificaten en firewallregels.

### Controlevragen

Gebruik deze vragen om te controleren of je het ontwerp kan uitleggen en niet alleen de
configuratiesyntax herkent.

1. Een hostname resolveert correct en de client krijgt een 502. Welke delen van de
   requestketen zijn waarschijnlijk al geslaagd en waar zoek je daarna?
2. Waarom bewijst een ontbrekend publiek DNS-record niet dat een backend afgeschermd is?
3. Een applicatie werkt via Traefik én via `localhost:8081`. Waarom is de tweede test een
   ontwerpfout, hoewel de pagina technisch bereikbaar is?
4. Waarom is alleen een statuscode 200 onvoldoende om host-based routing te bewijzen?
5. Wanneer kies je TLS termination met HTTPS naar de backend in plaats van HTTP naar de
   backend?
6. Waarom mag een backend `X-Forwarded-For` niet vertrouwen van eender welke client?
7. Welke firewallregel voorkomt dat een gecompromitteerde proxy vrij door het interne
   netwerk beweegt?
8. Welke labkeuzes uit de workshop moet je aanpassen voordat hetzelfde ontwerp in
   productie verantwoord is?

---

## 25. Samenvatting

Belangrijkste inzichten:

- een forward proxy werkt namens clients; een reverse proxy werkt namens applicaties;
- DNS brengt een client naar het proxy-IP;
- de HTTP `Host`-header laat host-based routing meerdere apps onderscheiden;
- een Traefik-entrypoint ontvangt verkeer;
- een router en rule bepalen welk request matcht;
- middleware voert extra verwerking uit;
- een service verwijst naar één of meer backends;
- frontendpoorten en backendpoorten horen bij afzonderlijke verbindingen;
- backends mogen niet buiten de gecontroleerde proxyroute om gepubliceerd worden;
- TLS termination centraliseert frontend-TLS, maar beschermt het backendtraject niet
  automatisch;
- forwarded headers zijn alleen betrouwbaar binnen een gecontroleerde proxyketen;
- een DMZ en firewallregels beperken welke systemen de proxy kan bereiken;
- security headers en rate limiting zijn aanvullende maatregelen, geen volledige
  beveiliging;
- load balancing helpt backends verdelen, maar de proxy zelf vraagt ook redundantie;
- statuscodes, access logs, proxylogs en backendlogs vullen elkaar aan;
- troubleshooting volgt het request van naamresolutie tot backend;
- positieve tests bewijzen bereikbaarheid;
- negatieve tests bewijzen afscherming;
- een reverse proxy is geen firewall, VPN of identity provider;
- HTTP, een hosts file, één proxy en een onbeveiligd dashboard zijn bewuste
  labvereenvoudigingen, geen productieontwerp.

Kernzin:

> Een reverse proxy publiceert webapplicaties via een centraal en controleerbaar
> requestpad, terwijl netwerkbeleid, TLS, identity, backendbeveiliging en tests samen
> moeten bewijzen dat alleen de bedoelde toegang mogelijk is.
