# Integratieopdracht Enterprise Networks - PixelPeak Studios

## 1. De opdracht in een zin

Ontwerp, bouw, beveilig, test en documenteer een enterprise-omgeving voor een kleine game- en mediastudio. Je combineert een gestructureerd campusontwerp met een zelf opgebouwde Proxmox-labomgeving, VPN-toegang, Docker, Traefik, Jellyfin, Minecraft, meerdere webdiensten en centrale identiteit via Authentik.

> Een verzameling losse containers is geen enterprise-omgeving. Elke component moet een duidelijke rol hebben, correct afgeschermd zijn en door positieve én negatieve tests aantoonbaar samenwerken met de rest van de omgeving.

### 1.1 Abstracte opdracht

In deze opdracht werk je als team een eigen enterprise-laboplossing uit voor PixelPeak Studios.
Jullie bouwen een kleine maar samenhangende omgeving waarin verschillende diensten elk hun eigen toegangspad en beveiligingslaag krijgen.
Het eindresultaat moet werken, maar het proces waarmee jullie daar geraken is minstens even belangrijk.

Je vertrekt niet van een volledig ingevuld stappenplan.
Je onderzoekt zelf welke configuratiekeuzes nodig zijn, probeert die uit, test ze en stuurt bij wanneer iets niet klopt.
Daarbij toon je dat je het verschil begrijpt tussen netwerkbereikbaarheid, authenticatie, autorisatie en applicatiespecifieke toegang.
Een gebruiker die ergens kan verbinden, mag dus niet automatisch overal binnen.
Een gebruiker die kan aanmelden, mag ook niet automatisch elke dienst gebruiken.

Het procesdossier is daarom een kernonderdeel van deze opdracht.
Daarin noteer je hoe jullie oplossing stap voor stap is ontstaan.
Je beschrijft welke ontwerpkeuzes je maakte, waarom je die keuzes maakte en welke alternatieven je eventueel verworpen hebt.
Je documenteert ook fouten, mislukte pogingen, aannames, controles en verbeteringen.
Dat dossier moet tonen dat jullie niet alleen iets werkend kregen, maar ook begrepen waarom het werkt.

Beschouw je repository dus als meer dan een plaats voor configuratiebestanden.
Ze is ook het bewijs van jullie leer- en bouwproces.
Commits, issues, beslissingsnotities, testresultaten en troubleshootingnotities moeten samen een controleerbaar verhaal vormen.
Een buitenstaander moet kunnen volgen hoe jullie van ontwerp naar werkende omgeving gingen.

Tijdens de verdediging kan de docent vragen waarom een bepaalde stap gezet werd, waarom een poort gesloten is, waarom een gebruiker geweigerd wordt of hoe een fout onderzocht werd.
Je moet dan kunnen verwijzen naar je documentatie, tests en eigen redenering.
Het doel is dus niet om de grootste of meest spectaculaire omgeving te bouwen.
Het doel is een beperkte enterprise-omgeving correct ontwerpen, veilig afbakenen, betrouwbaar testen en professioneel verantwoorden.

---

## 2. Scenario

**PixelPeak Studios** ontwikkelt games en maakt interne trainings- en demovideo's. Het bedrijf heeft medewerkers op kantoor, thuiswerkers, IT-beheerders en externe playtesters.

PixelPeak wil een kleine, samenhangende dienstenomgeving aanbieden:

1. een kleine **Jellyfin-mediaserver** voor medewerkers;
2. een kleine **Minecraft Java-server** voor gecontroleerde playtests;
3. een **publieke uitnodigingspagina** voor kandidaat-playtesters;
4. een **gegenereerde wereldkaart** die alleen een specifieke Authentik-groep mag bekijken.

De diensten stellen verschillende security-eisen:

- Jellyfin is een webapplicatie en moet uitsluitend via Traefik bereikbaar zijn;
- Jellyfin gebruikt Authentik als centrale identity provider via OpenID Connect;
- de uitnodigingspagina is zonder login bereikbaar binnen het afgesproken publieke labbereik en legt uit hoe een kandidaat een persoonlijke uitnodiging kan verkrijgen en gebruiken;
- zelfregistratie in Authentik kan alleen met een geldige, tijdsgebonden uitnodiging en levert aanvankelijk geen game- of kaartrechten op;
- de wereldkaart wordt via Traefik en Authentik forward auth beschermd en is alleen zichtbaar voor de daarvoor bestemde Authentik-groep;
- een interne adminpagina wordt via Traefik forward auth en MFA beschermd;
- Minecraft is geen gewone webapplicatie en wordt niet via de HTTP-reverse proxy gepubliceerd;
- Minecraft is lokaal rechtstreeks bereikbaar en voor externe spelers via Tailscale en een fijnmazige VPN-policy;
- playtesters mogen niet automatisch bij Jellyfin, SSH of beheerinterfaces;
- medewerkers mogen niet automatisch op de Minecraft-server;
- beheerders krijgen meer rechten, maar alleen waar die technisch nodig zijn;
- backendpoorten, databases en managementinterfaces mogen niet breed bereikbaar zijn.

De centrale vraag is:

> Hoe bied je verschillende soorten diensten gebruiksvriendelijk aan zonder van VPN-toegang, een reverse proxy of een geslaagde login te veronderstellen dat daarmee automatisch de volledige omgeving veilig is?

---

## 3. Eindresultaat

Op het einde demonstreert je team minstens deze vijf toegangspatronen.

### 3.1 Jellyfin: VPN, reverse proxy en centrale identiteit

```text
medewerker
    |
    | Tailscale en toegangsbeleid
    v
edge01 - Traefik
    |
    | host-based routing
    v
media01 - Jellyfin
    |
    | OIDC authorization code flow
    v
media01 - Authentik
```

De gebruiker bereikt Jellyfin nooit rechtstreeks via poort `8096`. De normale toegang loopt via Traefik. Voor een nieuwe browsersessie authenticeert de gebruiker via Authentik.

### 3.2 Minecraft: directe toegang met VPN-policy voor externen

```text
externe playtester
    |
    | Tailscale en beperkte VPN-regel
    v
game01 - eigen Tailscale-node
    |
    | alleen TCP/25565
    v
game01 - Minecraft
```

Minecraft wordt niet via de HTTP-reverse proxy gepubliceerd en gebruikt geen Authentik-weblogin. Lokale spelers verbinden rechtstreeks met het labadres van `game01`. Externe spelers verbinden via Tailscale; daar beperkt de Tailscale-policy wie TCP/25565 mag bereiken. In beide gevallen blijft de Minecraft-whitelist een tweede, applicatiespecifieke controle.

### 3.3 Adminpagina: identity-aware access

```text
IT-beheerder
    |
    | Tailscale
    v
edge01 - Traefik
    |
    | forward auth + groep + TOTP
    v
kleine adminapp
```

Deze route toont hoe een eenvoudige applicatie zonder eigen OIDC-implementatie toch met Authentik kan worden beschermd.

### 3.4 Uitnodigingspagina: publiek front-end, afgeschermde backend

```text
kandidaat-playtester
    |
    | publieke labroute, geen login
    v
edge01 - Traefik
    |
    | alleen naar de webbackend
    v
media01 - statische uitnodigingspagina
```

De pagina is eenvoudige HTML/CSS en bevat geen registratiebackend of gevoelige gegevens. Ze legt uit hoe iemand toegang aanvraagt en hoe een persoonlijke Authentik-uitnodiging wordt gebruikt. **Publiek** betekent hier: bereikbaar voor iedere testclient in het door de docent afgesproken labbereik, zonder Tailscale- of Authentik-login. Publicatie op het echte internet is niet vereist.

### 3.5 Wereldkaart: groepsgebonden toegang tot een backend op de gameserver

```text
goedgekeurde kaartgebruiker
    |
    | Tailscale
    v
edge01 - Traefik
    |
    | forward auth + pp-map-viewers
    v
game01 - statische of lichtgewicht wereldkaartservice
```

De kaartservice draait verplicht op `game01`, niet op de reverse-proxymachine. Zo toon je dat Traefik veilig naar een backend op een andere VM routeert. De kaart is een beperkte, gegenereerde weergave van de labowereld; continue live rendering is niet vereist.

---

## 4. Team, infrastructuur en verantwoordelijkheid

- Je werkt normaal in een team van **drie studenten**.
- Een groep van twee kan alleen na toestemming van de docent en krijgt eventueel een beperktere scope.
- Elk teamlid bouwt technisch mee en begrijpt de volledige architectuur.
- Gebruik Git vanaf week 1 en commit kleine, betekenisvolle wijzigingen.
- Werk met issues of een eenvoudig projectbord voor taken, risico's, fouten en beslissingen.
- Voorzie per teamlid een korte bijdrage- en reflectienota.
- Reken op ongeveer **25 tot 30 uur werk per student**, verspreid over het semester.

Een mogelijke primaire taakverdeling is:

| Rol | Primaire verantwoordelijkheid |
|---|---|
| netwerk en infrastructuur | Proxmox-netwerken, VM's, routing, filtering en Tailscale |
| platform en applicaties | Docker, Compose, Traefik, Jellyfin en Minecraft |
| identity en operations | Authentik, OIDC, forward auth, MFA, logging en testen |

Dit zijn geen afgesloten eilanden. Elke technische wijziging wordt door minstens één ander teamlid nagekeken en ieder teamlid voert ook tests uit buiten de eigen hoofdtaak.

### 4.1 Aangeboden Proxmox-machine

Elke groep krijgt één afgeschermde Proxmox-machine met maximaal:

- **5 processorkernen**;
- **15 GB RAM**;
- **75 GB opslag**.

De buitenste Proxmox-machine is de harde resourcegrens van de groep. Je team maakt daarin zelf de vereiste virtuele netwerken en Debian-VM's aan.

Belangrijke regels:

- draai geen applicatieworkloads rechtstreeks op de Proxmox-host;
- wijzig de door de docent aangeduide managementinterface of uplink niet;
- maak geen onnodige VM's, snapshots of grote virtuele disks;
- gebruik geen geheugenovercommit die de Proxmox-machine laat swappen;
- houd minstens 15 GB vrije opslagruimte over voor Proxmox, tijdelijke bestanden en logs;
- bewaar maximaal één tijdelijke snapshot per VM en verwijder die na de test;
- monitor CPU-, RAM- en opslaggebruik tijdens Jellyfin- en Minecrafttests.

### 4.2 Beginsituatie en aangeboden materiaal

Je krijgt:

- toegang tot de Proxmox-machine van je groep;
- een Debian-installatie-ISO of een minimale Debian-template;
- de netwerkgegevens van het lab;
- beperkte voorbeeldconfiguraties uit de workshops;
- één of twee kleine, legale testmediabestanden of richtlijnen om die zelf te maken.

Je krijgt geen volledig ingevulde eindoplossing. Je team maakt zelf de VM's, installeert de software, schrijft de finale Compose-bestanden en configureert routing, filtering, Traefik, Tailscale en Authentik.

Je mag workshopmateriaal hergebruiken wanneer je:

- duidelijk vermeldt wat je hebt hergebruikt;
- het aanpast aan deze architectuur;
- kan uitleggen hoe het werkt;
- de geïntegreerde werking opnieuw test.

---

## 5. Architectuur en resourcebudget

### 5.1 Verplichte VM's

Je bouwt drie Debian-VM's.

| VM | Rol | Richtwaarde resources | Maximale disk |
|---|---|---:|---:|
| `edge01` | filtering, Tailscale, interne DNS en Traefik | 1 vCPU, 1,5 GB RAM | 10 GB |
| `media01` | Tailscale, Jellyfin, Authentik, PostgreSQL, worker, adminapp en uitnodigingspagina | 2 vCPU, 5,5 GB RAM | 28 GB |
| `game01` | Tailscale, Minecraft Java-server en beperkte wereldkaartservice | 2 vCPU, 3,5 GB RAM | 12 GB |

Deze verdeling gebruikt maximaal vijf toegewezen vCPU's, ongeveer 10,5 GB RAM en 50 GB virtuele disk. De resterende resources zijn nodig voor de Proxmox-host, overhead, logs en tijdelijke bestanden.

Je mag de verdeling beperkt aanpassen wanneer je de wijziging vooraf motiveert in een resourcebudget en de totale grenzen respecteert.

### 5.2 Labnetwerk en adresblok

Koppel elke Debian-VM met één VirtIO-netwerkkaart rechtstreeks aan de bestaande Proxmox-bridge `vmbr0`. Maak voor deze opdracht geen extra bridge of VLAN. De VM's gebruiken het standaardnetwerk `10.20.0.0/16` en de door de docent opgegeven labgateway.

Voor dit labo is `10.20.27.0/24` administratief gereserveerd. Elke groep krijgt daarbinnen een blok van tien opeenvolgende adressen. Alle adressen van de buitenste Proxmox-VM, `edge01`, `media01` en `game01` moeten binnen het groepsblok blijven. De grens van tien adressen is geen subnetgrens: configureer op de VM's het labmasker `/16`, geen `/28`, `/29` of `/24`. Controleer vooraf op adresconflicten en documenteer de gebruikte adressen.

Omdat de drie VM's hetzelfde laag-2-netwerk delen, is `edge01` het normale toegangspunt voor webdiensten. Traefik biedt de webapplicaties aan op het lokale labadres en op het Tailscale-adres; Authentik verzorgt daarna de toegangscontrole. `edge01` blijft de trust boundary voor webtoegang, maar is niet de default gateway of NAT-router voor het gewone internetverkeer van `media01` en `game01`.

### 5.3 Docker-netwerken

Gebruik op `media01` afzonderlijke Docker-netwerken voor minstens:

- de applicatiecontainers;
- Authentik server en worker;
- de PostgreSQL-backend, uitsluitend gedeeld met de Authentik-componenten die de database nodig hebben.

Traefik en de webbackends draaien op verschillende VM's. Een lokaal Docker-bridgenetwerk overspant die VM's dus niet. Publiceer alleen de noodzakelijke webbackendpoorten op het interne labadres van de juiste VM en laat alleen `edge01` die backends bereiken. Eindgebruikers gebruiken voor webdiensten altijd Traefik, lokaal of via Tailscale. Minecraft is de uitzondering: die poort mag rechtstreeks op het labadres en op het Tailscale-adres van `game01` beschikbaar zijn.

De database hoort niet op hetzelfde onbeperkte netwerk als alle applicatiecontainers. Publiceer geen databasepoort op de VM-host.

## 6. Technische requirements

### 6.1 VM-baseline en secure management

Voor elke Debian-VM:

1. installeer je een schone Debian-omgeving of kloon je een minimale template;
2. stel je een correcte hostname en netwerkidentiteit in;
3. gebruik je een niet-rootaccount met `sudo`;
4. voer je updates uit en controleer je tijdsynchronisatie;
5. gebruik je SSH-sleutels voor beheer;
6. installeer je alleen de noodzakelijke software;
7. publiceer je webbackends alleen op de noodzakelijke interface en alleen voor het bedoelde toegangspad via `edge01`;
8. inventariseer je luisterpoorten voor en na de installatie;
9. documenteer je installatie reproduceerbaar.

Managementtoegang is alleen toegestaan voor de IT-beheerdersrol. Gewone media-users en playtesters krijgen geen SSH-toegang.

### 6.2 Docker en Compose

Alle applicatiediensten draaien als containers via Docker Compose.

Installeer Docker Engine en Docker Compose v2 op elke VM met een reproduceerbare methode. Documenteer je keuze en controleer na installatie dat beide componenten correct werken.

Minimale kwaliteitsregels:

- geen handmatige `docker run`-commando's als finale deployment;
- geen gedachteloos gebruik van `latest`;
- persistente data in benoemde volumes of duidelijk beheerde bind mounts;
- restart policies en healthchecks waar zinvol;
- CPU- en geheugenlimieten voor Jellyfin en Minecraft;
- `.env` buiten Git en een veilige `.env.example` in Git;
- geen privileged containers zonder expliciete, goedgekeurde motivatie;
- reproduceerbare herstart vanaf Compose en documentatie.

### 6.3 Securityzones en toegangsbeleid

Gebruik minstens deze logische zones:

| Zone | Inhoud |
|---|---|
| Staff | gewone medewerkers |
| IT | beheerderswerkstations |
| Media services | Jellyfin, Authentik, adminapp en uitnodigingspagina |
| Game | Minecraft en wereldkaartbackend |
| Management | beheerinterfaces |
| Guest | niet-vertrouwde toestellen |
| DMZ/edge | Traefik en toegangspunt |

Je levert een toegangsregelmatrix met minstens twaalf relevante verkeersstromen. Elke regel bevat bron, doel, protocol/poort, actie, reden, enforcement point en test-ID. In de werkende Proxmox-omgeving levert Tailscale externe toegang tot het labosysteem, terwijl Authentik het primaire enforcement point voor webtoegang is. Alleen Minecraft gebruikt een functionele Tailscale-gebruikersregel voor externe spelers.

Minimale policy:

- Guest bereikt geen interne of managementzone;
- Staff bereikt geen managementinterfaces;
- de DMZ/edge bereikt alleen noodzakelijke backendpoorten;
- alleen Traefik op `edge01` bereikt de webbackends; de backendpoorten op `media01` en `game01` zijn niet rechtstreeks voor eindgebruikers bereikbaar;
- de wereldkaartbackend aanvaardt alleen verkeer vanaf `edge01` en is niet rechtstreeks bereikbaar voor eindgebruikers;
- alleen Authentik bereikt PostgreSQL;
- Jellyfin is niet rechtstreeks via `8096` bereikbaar voor eindgebruikers;
- Minecraft is rechtstreeks bereikbaar op het labadres van `game01` en voor externe spelers via Tailscale;
- RCON is uitgeschakeld en poort `25575` blijft gesloten;
- lidmaatschap van het tailnet betekent niet automatisch toegang tot alle nodes of poorten;
- ontbrekende toegang wordt via **deny by omission** geweigerd.

### 6.4 Tailscale-routing en Minecraft-policy

Installeer Tailscale afzonderlijk op `edge01`, `media01` en `game01`. Elke VM wordt een eigen tailnet-node met een herkenbare hostname en een eigen tag. Gebruik geen subnetrouter en adverteer geen routes naar het groepsblok of labnetwerk.

Tailscale dient in deze opdracht in de eerste plaats voor externe bereikbaarheid. Iedere gewone tailnetgebruiker mag de interne DNS en Traefik op `edge01` bereiken. Die netwerktoegang geeft nog geen applicatierechten: Authentik authenticeert de gebruiker en beslist via zijn groepen over Jellyfin, de wereldkaart en de adminapp. Lokale labgebruikers bereiken dezelfde webdiensten via het labadres van `edge01` en moeten voor beschermde webdiensten evengoed door Authentik.

Minecraft vormt de enige functionele gebruikersautorisatie in de Tailscale-policy. Alleen de daarvoor aangemaakte Tailscale-gebruikersgroep mag via Tailscale TCP/25565 op `game01` bereiken. Tags horen in Tailscale bij nodes, niet bij gebruikers: tag daarom `game01` en laat de gebruikersgroep uitsluitend naar TCP/25565 op die getagde node toe.

Gebruik één gecontroleerde project-tailnet voor het team. Deel nooit accounts of inloggegevens: elk teamlid gebruikt een eigen identiteit. Duid één beheerder en minstens één reservebeheerder aan en documenteer hoe de drie VM-nodes, testdevices en tijdelijke rechten na de opdracht worden verwijderd.

Maak in Tailscale slechts het onderscheid dat voor netwerkbereikbaarheid nodig is:

| Tailscale-identiteit | Traefik en DNS | Minecraft `25565` |
|---|---:|---:|
| gewone tailnetgebruiker | bereikbaar; Authentik beslist verder | geweigerd |
| lid van de Minecraft-groep | bereikbaar; Authentik beslist verder | toegestaan |

SSH wordt niet door Authentik afgehandeld en blijft afzonderlijk beveiligd met Linux-accounts en SSH-sleutels.

Je oplossing bevat:

- remote toegang naar Traefik op `edge01`;
- lokale Minecraft-toegang naar het labadres van `game01` en rechtstreekse Tailscale-toegang naar `game01`, extern uitsluitend op TCP/25565 voor leden van de Minecraft-groep;
- tags voor de drie VM-nodes en één afzonderlijke Minecraft-gebruikersgroep;
- geen subnetroutes, exit nodes of brede regels naar het groepsblok of volledige labnetwerk;
- netwerktoegang tot DNS en Traefik voor gewone tailnetgebruikers, zonder daarmee applicatierechten toe te kennen;
- Split DNS voor minstens Jellyfin, de wereldkaart en Minecraft;
- positieve en negatieve policytests;
- analyse van direct, peer relay of DERP zonder een pad kunstmatig af te dwingen;
- een zichtbaarheidstabel voor lokaal netwerk, ISP, Tailscale, relay en bestemmingsdienst.

Wanneer dezelfde student voor een test meerdere rollen moet simuleren, documenteer je hoe je afzonderlijke testidentiteiten of testdevices controleerbaar hebt gebruikt.

### 6.5 Traefik en publicatie

Traefik draait op `edge01` via Docker Compose en vormt het enige normale toegangspunt voor de webapplicaties.

Gebruik minstens deze hostnames:

| Dienst | Hostname | Beveiliging |
|---|---|---|
| Jellyfin | `jellyfin.pixelpeak.test` | Tailscale + Traefik + Authentik OIDC |
| Authentik | `auth.pixelpeak.test` | vereiste login- en enrollmentflows; beheer alleen voor IT |
| Adminapp | `admin.pixelpeak.test` | Tailscale + forward auth + IT-groep + TOTP |
| Uitnodigingspagina | `join.pixelpeak.test` | lokale en Tailscale-route via Traefik, zonder login |
| Wereldkaart | `map.pixelpeak.test` | Tailscale + forward auth + `pp-map-viewers` |

Vereisten:

- static en dynamic config zijn duidelijk gescheiden;
- host-based routing werkt voor alle routes;
- het lokale en het Tailscale-entrypoint bieden dezelfde webroutes via Traefik aan; beschermde diensten tonen pas inhoud na correcte Authentik-authenticatie en autorisatie;
- het vereiste Authentik-outpostpad heeft de juiste route en prioriteit;
- Traefik kan de backends op `media01` en `game01` bereiken, maar eindgebruikers niet rechtstreeks;
- security headers worden centraal toegepast waar ze de applicatie niet breken;
- WebSockets en forwarded headers voor Jellyfin werken correct;
- Traefik staat in Jellyfin als gekende proxy ingesteld;
- accesslogging staat aan zonder gevoelige Jellyfin-URL's of tokens onnodig te bewaren;
- het Traefik-dashboard is niet onbeveiligd bereikbaar;
- een foutieve route of backend kan via logs methodisch worden onderzocht.

De uitnodigingspagina toont het verschil tussen een publiek toegankelijke route en een publiek bereikbare backend. **Publiek** betekent in deze labo-opdracht niet dat je iets werkelijk op het internet moet publiceren. Beschrijf exact welk labsubnet of welke testclient als publieke buitenzijde geldt.

### 6.6 Authentik-groepen, enrollment en lifecycle

Authentik draait op `media01` en vormt de centrale identity provider voor de webdiensten. Maak minstens deze groepen:

- `pp-pending-players` voor nieuw ingeschreven kandidaten zonder servicerechten;
- `pp-playtesters` voor goedgekeurde Minecraft-playtesters;
- `pp-map-viewers` voor gebruikers die de wereldkaart mogen bekijken;
- `pp-media-users` voor Jellyfin-gebruikers;
- `pp-it-admins` voor beheerders.

Voorzie minstens vijf testidentiteiten waarmee je pending-, playtester-, media-, map- en IT-rechten afzonderlijk kunt aantonen. Eén gebruiker mag meerdere goedgekeurde groepen combineren, maar je tests moeten bewijzen dat lidmaatschap van `pp-playtesters` op zichzelf geen kaart- of Jellyfin-toegang geeft.

Bouw een gecontroleerde enrollmentflow:

1. een kandidaat leest op `join.pixelpeak.test` hoe toegang wordt aangevraagd;
2. een IT-beheerder maakt voor de kandidaat een persoonlijke, tijdsgebonden uitnodiging aan;
3. de kandidaat registreert via de Authentik-enrollmentflow met die uitnodiging;
4. het nieuwe account komt automatisch in `pp-pending-players` en krijgt nog geen toegang tot Jellyfin, de wereldkaart, Minecraft of beheer;
5. een IT-beheerder controleert de aanvraag en kent daarna alleen de noodzakelijke groep of groepen toe;
6. lidmaatschap van de Tailscale Minecraft-groep en de Minecraft-whitelist worden afzonderlijk toegekend; Authentik-groepen geven geen Minecraft-netwerktoegang;
7. bij offboarding verwijdert de beheerder de Authentik-groepen, VPN-toegang en Minecraft-whitelist en onderzoekt het team bestaande sessies.

Gebruik voor de demonstratie een eenmalige of kort geldige uitnodiging. Plaats geen herbruikbare uitnodigingslink of uitnodigingstoken op de publieke pagina, in Git of in screenshots. Een ongeldig, verlopen of reeds gebruikt exemplaar moet veilig worden geweigerd.

Documenteer de lifecycle als een kleine toestandsketen:

```text
uitgenodigd -> pending -> goedgekeurde groep(en) -> gedeactiveerd
```

Noteer per overgang wie ze mag uitvoeren, welk audit-event je verwacht en welke toegang vóór en na de overgang verandert.

### 6.7 Publieke uitnodigingspagina

Plaats op `media01` een kleine statische webservice voor `join.pixelpeak.test` met zelfgemaakte HTML en CSS.

De pagina bevat minstens:

- een korte voorstelling van de PixelPeak Minecraft-playtest;
- de voorwaarden voor deelname en een verwijzing naar de gedragsregels;
- uitleg dat registratie alleen met een persoonlijke uitnodiging mogelijk is;
- een duidelijke actie voor iemand die al een uitnodiging ontvangen heeft;
- uitleg dat registratie nog geen automatische toelating tot de server betekent;
- geen formulierbackend, wachtwoorden, tokens, persoonsgegevens of dynamische database.

De container draait niet op `edge01`. Traefik routeert vanaf het lokale en het Tailscale-entrypoint naar de backend op `media01`. Alleen `edge01` mag de backendpoort bereiken. De pagina zelf vereist geen Authentik-login; de daaropvolgende enrollmentflow wel een geldige uitnodiging.

### 6.8 Jellyfin via Authentik OIDC

Jellyfin draait op `media01` als container. Gebruik de door de docent goedgekeurde versie van de Jellyfin SSO/OIDC-plugin om Jellyfin met Authentik te koppelen.

Gebruik uitsluitend labowachtwoorden die nergens anders worden gebruikt.

Minimale requirements:

- één Jellyfin-library met één of twee korte testbestanden;
- maximaal 1 GB testmedia in totaal;
- eigen, docentgeleverde of publiek beschikbare legale media;
- mediabestanden read-only gemount;
- browsergebaseerde test; native televisie- en mobiele clients zijn niet vereist;
- direct play als normale test; transcoding wordt niet beoordeeld;
- geen hardware acceleration;
- geen brede directe publicatie van poort `8096`;
- een strikte OIDC redirect URI;
- relevante scopes en claims zonder volledige tokens te publiceren;
- alleen de bedoelde Authentik-groep krijgt toegang;
- login-, deny- en beheerwijzigingen zijn terug te vinden in de audit events;
- de deactivatie van een testaccount wordt met een nieuwe én een bestaande sessie onderzocht;
- een lokaal, gecontroleerd break-glassaccount blijft beschikbaar en wordt veilig gedocumenteerd zonder het wachtwoord op te nemen;
- bestaande en nieuwe sessies worden afzonderlijk onderzocht bij IdP-uitval.

Je mag bijvoorbeeld deze publiek beschikbare testvideo van Internet Archive als bron gebruiken:

```text
https://archive.org/download/pdcartooncollection/Brementown%20Musicians%20UB%20Iwerks%20ComiColor.mp4
```

Het is jullie verantwoordelijkheid om het mediabestand correct, legaal en controleerbaar in de Jellyfin-library te krijgen.

Je toont minstens:

1. een nieuwe login via Authentik;
2. de authorization code flow;
3. een toegelaten media-user;
4. een geweigerde playtester;
5. SSO-gedrag;
6. afspelen van één testbestand;
7. logout- en sessiegedrag;
8. het resultaat van een nieuwe login wanneer Authentik niet beschikbaar is.

### 6.9 Adminapp via forward auth en MFA

Maak een kleine, ongevaarlijke adminapp. Dit mag een eenvoudige statische beheerpagina of veilige testcontainer zijn die ontvangen identity-informatie toont.

De adminapp:

- heeft zelf geen OIDC-implementatie;
- is uitsluitend via Traefik bereikbaar;
- gebruikt Authentik forward auth;
- is gebonden aan de IT-beheerdersgroep;
- vereist TOTP als step-up MFA;
- toont alleen niet-gevoelige identity-informatie;
- vertrouwt identity-headers uitsluitend van Traefik;
- sluit wanneer Authentik of de outpost niet beschikbaar is.

Voer ook een header-spoofingtest uit waarmee je aantoont dat een zelf aangeleverde identity-header de login niet omzeilt.

### 6.10 Wereldkaart via Authentik-groep

Maak op `game01` een kleine webservice die een gegenereerde kaart of momentopname van de Minecraft-labowereld toont. Je mag:

- een beperkte statische kaart genereren en de uitvoer met een lichte webcontainer aanbieden; of
- na voorafgaande goedkeuring een lichte kaartrenderer gebruiken waarvan CPU-, RAM- en diskgebruik begrensd zijn.

Minimumscope:

- de kaart komt aantoonbaar uit de gebruikte labowereld;
- één beperkte verkende zone en één handmatige generatie volstaan;
- continue live rendering en live spelerlocaties zijn niet vereist;
- de gegenereerde kaart gebruikt maximaal 1 GB opslag;
- de kaartwebcontainer gebruikt maximaal 256 MB RAM en een eventuele renderer maximaal 1 vCPU en 1 GB RAM;
- de renderer draait niet tijdens de normale performancetest of mondelinge verdediging;
- alleen de webpoort die Traefik nodig heeft, wordt op het labadres van `game01` gebonden;
- eindgebruikers kunnen de backendpoort niet rechtstreeks bereiken.

Publiceer de dienst als `map.pixelpeak.test` via Traefik en bescherm ze met Authentik forward auth. Alleen `pp-map-viewers` en, indien zo gemotiveerd, `pp-it-admins` krijgen toegang. Een aangemelde gebruiker uit uitsluitend `pp-playtesters`, `pp-media-users` of `pp-pending-players` wordt geweigerd.

Toon dat de kaartservice niet op `edge01` draait en dat een zelf aangeleverde identity-header de groepscontrole niet omzeilt. Bij uitval van Authentik of de outpost sluit de kaartroute veilig.

### 6.11 Minecraft via VPN

De Minecraft Java-server draait op `game01` via Docker Compose.

Beperk de server tot een kleine labomgeving:

- vanilla of een door de docent goedgekeurde lichte variant;
- een vastgelegde en geteste serverversie;
- expliciete aanvaarding van de Minecraft-server-EULA in de lokale configuratie;
- maximaal vijf spelers;
- maximaal 2 GB Java-heap;
- containerlimiet van maximaal 2,5 GB RAM;
- beperkte `view-distance` en `simulation-distance`;
- geen mods of grote pluginsets;
- persistent volume voor de wereld;
- `online-mode` ingeschakeld;
- whitelist ingeschakeld;
- RCON uitgeschakeld;
- geen publieke port forwarding;
- TCP/25565 lokaal via het labadres van `game01` en extern via de bedoelde VPN-policy.

Minstens één teamlid toont een echte verbinding met een gelicentieerde Minecraft-client. Wanneer geen enkel teamlid over een geschikte client beschikt, bespreek je vooraf met de docent een gratis alternatief of een gelijkwaardige protocoltest.

Je toont dat:

- een playtester de server via Tailscale en Split DNS bereikt;
- een media-only gebruiker niet kan verbinden;
- poort `25565` lokaal via het labadres werkt en extern alleen via de bedoelde Tailscale-policy werkt;
- SSH en andere gamehostpoorten voor playtesters gesloten blijven;
- de Minecraft-whitelist een tweede, applicatiespecifieke controle vormt;
- de wereld na herstart behouden blijft.

### 6.12 Logging en troubleshooting

Houd een wijzigings- en probleemlogboek bij. Onderzoek minstens één incident over meerdere lagen.

Voor Jellyfin kan de onderzoeksketen zijn:

```text
DNS -> lokaal edgeadres of Tailscale edgeadres -> Traefik -> OIDC -> Authentik -> Jellyfin
```

Voor Minecraft kan de onderzoeksketen zijn:

```text
DNS -> lokaal `GAME_IP` of Tailscale-policy naar `GAME_TAILSCALE_IP` -> containerpoort -> whitelist
```

Voor de wereldkaart kan de onderzoeksketen zijn:

```text
DNS -> lokaal edgeadres of Tailscale edgeadres -> Traefik -> forward auth -> Authentik-groep -> kaartcontainer op game01
```

Het incidentrapport bevat:

1. symptoom en impact;
2. verwachte werking;
3. hypothesen in logische volgorde;
4. gebruikte commando's, logs of events;
5. root cause;
6. oplossing;
7. postchecks;
8. preventieve maatregel;
9. preventieve opvolging.

---

## 7. Verplichte acceptatietests

Neem onderstaande tests op in één centrale testmatrix.

| ID | Type | Minimale test |
|---|---|---|
| `PVE-01` | resource | de drie VM's blijven samen binnen CPU-, RAM- en diskbudget |
| `SEC-01` | negatief | Guest bereikt geen interne of managementzone |
| `SEC-02` | negatief | Staff of playtester kan geen beheerinterface bereiken |
| `MGT-01` | positief | een IT-beheerder bereikt de bedoelde VM via SSH |
| `VPN-01` | positief | media-user bereikt Jellyfin extern via Traefik over Tailscale en moet nog altijd via Authentik |
| `VPN-02` | positief | playtester bereikt de Tailscale-node van `game01` op TCP/25565 |
| `VPN-03` | negatief | media-only gebruiker bereikt Minecraft niet |
| `VPN-04` | gelaagd | playtester bereikt de proxy, maar Authentik weigert Jellyfin; SSH weigert zonder geldig account en sleutel |
| `DNS-01` | positief | Jellyfin, wereldkaart en Minecraft worden via Split DNS correct opgelost |
| `PRX-01` | positief | Traefik routeert Jellyfin, Authentik, admin, uitnodiging en wereldkaart correct |
| `PRX-02` | negatief | Jellyfin-poort `8096` is niet rechtstreeks bereikbaar voor eindgebruikers |
| `PRX-03` | negatief | database-, uitnodigings- en kaartbackendpoorten en het Traefik-dashboard zijn niet breed bereikbaar |
| `WEB-01` | positief | de uitnodigingspagina is zonder login bereikbaar vanaf de afgesproken lokale labzijde en via Tailscale |
| `WEB-02` | segmentatie | de uitnodigingspagina draait op `media01` en alleen `edge01` bereikt haar backendpoort |
| `JEL-01` | positief | toegelaten gebruiker meldt aan via OIDC en speelt een testbestand af |
| `JEL-02` | negatief | playtester zonder mediagroep krijgt geen Jellyfin-toegang |
| `IAM-01` | MFA | adminapp vereist IT-groep en TOTP |
| `IAM-02` | negatief | zelf aangeleverde identity-header omzeilt forward auth niet |
| `IAM-03` | enrollment | een geldige, tijdsgebonden uitnodiging maakt een account in `pp-pending-players` |
| `IAM-04` | negatief | een ongeldige, verlopen of hergebruikte uitnodiging wordt geweigerd |
| `IAM-05` | least privilege | een pending account krijgt geen Jellyfin-, kaart-, Minecraft- of beheerrechten |
| `IAM-06` | lifecycle | goedkeuring en offboarding wijzigen alleen de bedoelde groeps-, VPN- en whitelistrechten |
| `MAP-01` | positief | een lid van `pp-map-viewers` kan via Traefik de gegenereerde kaart op `game01` bekijken |
| `MAP-02` | negatief | een aangemelde gebruiker zonder `pp-map-viewers` wordt geweigerd |
| `MAP-03` | segmentatie | de kaartbackend op `game01` is niet rechtstreeks bereikbaar en vertrouwt geen aangeleverde identity-header |
| `FAIL-01` | uitval | nieuwe Jellyfin-login, adminapp en wereldkaart reageren veilig bij IdP/outpost-uitval; de publieke uitnodigingspagina blijft statisch bereikbaar |
| `MC-01` | positief | toegelaten en gewhiteliste playtester kan de Minecraft-server joinen |
| `MC-02` | negatief | niet-toegelaten externe gebruiker bereikt Minecraft niet via Tailscale en RCON is niet bereikbaar |

Voor elke test noteer je:

- datum en uitvoerder;
- precondities en gebruikte identiteit;
- concrete actie;
- verwacht resultaat;
- werkelijk resultaat;
- status `PASS`, `FAIL` of `BLOCKED`;
- beknopt en geredigeerd bewijs;
- verwijzing naar een issue bij afwijkingen.

Een screenshot zonder testcontext is geen voldoende bewijs.

---

## 8. Wekelijkse mijlpalen

Elke mijlpaal eindigt met bijgewerkte documentatie, relevante tests en een herkenbare Git-tag of release.

| Week | Mijlpaal | Minimale output |
|---|---|---|
| 1 | baseline en projectcharter | teamrollen, resourcebudget, architectuurschets, risico's en VM-plan |
| 2 | VM- en netwerkbasis | Proxmox-VM's, IP-plan, basisconnectiviteit en listenerinventaris |
| 3 | securityarchitectuur | zones, trust boundaries, Proxmox-netwerken en eerste toegangsregelmatrix |
| 4 | beheer en baselinebeveiliging | managementpolicy, SSH-toegang, loggingafspraken en eerste negatieve tests |
| 5 | VPN-baseline | Tailscale op alle drie VM's, tags, rollen en remote-accesspolicy |
| 6 | directe game access | Tailscale-IP van `game01`, Split DNS, beperkte Minecraft-container en positieve/negatieve VPN-tests |
| 7 | VPN-securityanalyse | padmeting, NAT/relay-analyse, zichtbaarheidstabel en aangescherpte policy |
| 8 | diensten via reverse proxy | Traefik, Jellyfin, publieke uitnodigingspagina op `media01`, kaartbackend op `game01`, backendisolatie en direct-playtest |
| 9 | centrale identiteit | Authentik, invitation-based enrollment, pendingstatus, groepsgoedkeuring, Jellyfin-OIDC, SSO, lifecycle en audit |
| 10 | identity-aware toegang | adminapp en wereldkaart via forward auth, groepsbindingen, TOTP, spoofingtests en fail-closedtests |
| 11 | finale integratie | volledige testmatrix, procesdossier, incidentrapport, documentatie en demo-oefening |
| 12 | verdediging | werkende demonstratie, verantwoording en individuele vragen |

Een mijlpaal is een controlepunt, geen afzonderlijk eindverslag. Werk één levend technisch dossier bij.

---

## 9. Op te leveren repository

Gebruik minstens deze herkenbare structuur.

```text
README.md
docs/
  architecture/
    overview.md
    resource-budget.md
    decisions/
  network/
    ip-plan.md
    zones-access-matrix.md
  access/
    tailscale-policy.md
    reverse-proxy.md
    identity-access-matrix.md
    enrollment-lifecycle.md
  operations/
    installation-runbook.md
    incident-report.md
  testing/
    acceptance-tests.md
    risk-register.md
proxmox/
  vm-inventory.md
  network-plan.md
edge01/
  compose.yml
  traefik/
  dns/
media01/
  compose.yml
  authentik/
  adminapp/
  join-page/
game01/
  compose.yml
  minecraft/
  world-map/
scripts/
.env.example
.gitignore
```

De repository bevat minstens:

- een startpagina die een nieuwe lezer door het project leidt;
- VM-, netwerk- en resource-inventaris;
- alle niet-gevoelige Compose- en configuratiebestanden;
- een overkoepelend architectuurschema;
- netwerk-, Tailscale- en identity-accessmatrix;
- Jellyfin-, Minecraft-, uitnodigingspagina-, wereldkaart-, Traefik- en Authentikconfiguratie zonder secrets;
- installatie-, proces-, test- en incidentdocumentatie;
- één incidentrapport;
- een risicoanalyse met resterende risico's;
- een bijdrageoverzicht per teamlid.

### 9.1 Procesdossier en eigen oplossing

Naast de finale configuratie lever je een eigen procesdossier op. Dit dossier beschrijft hoe jullie oplossing stap voor stap tot stand kwam, zodat niet alleen het eindresultaat maar ook jullie aanpak beoordeeld kan worden.

Het procesdossier bevat minstens:

- een chronologische bouwvolgorde per grote laag: VM's, netwerk, VPN, reverse proxy, identity, applicaties en tests;
- de belangrijkste ontwerpkeuzes en waarom jullie die gemaakt hebben;
- verwijzingen naar relevante commits, issues, beslissingen en test-ID's;
- de gebruikte bronnen of documentatie, met korte toelichting waarvoor ze gebruikt zijn;
- problemen, mislukte pogingen en bijsturingen die technisch relevant waren;
- controles waarmee jullie bepaalden dat een laag klaar was voor de volgende stap;
- een korte reflectie op wat jullie achteraf anders of beter zouden doen.

Dit is geen kopie van workshopmateriaal, officiële documentatie of een modeloplossing. Het moet aantonen dat jullie de eigen omgeving begrijpen en dat jullie werk reproduceerbaar, controleerbaar en verdedigbaar is. Neem geen secrets, persoonlijke tokens, volledige logs met gevoelige gegevens of uitnodigingslinks op.

Lever geen volledige VM-images, Docker-volumes, databases, Minecraft-werelden of mediabestanden in tenzij de docent dit uitdrukkelijk vraagt.

---

## 10. Secrets, privacy, media en versiebeheer

Neem nooit de volgende gegevens op in Git, screenshots of het dossier:

- wachtwoorden;
- Tailscale auth keys of loginlinks;
- Authentik-uitnodigingslinks of -tokens;
- OIDC client secrets;
- cookies of volledige tokens;
- TOTP-seeds, QR-codes, codes of herstelcodes;
- Minecraft operator- of whitelistgegevens die niet nodig zijn als bewijs;
- ongeredigeerde publieke IP-adressen;
- auteursrechtelijk beschermd materiaal waarvoor je geen gebruiksrecht hebt.

Gebruik minstens:

- een volledige `.gitignore`;
- `.env.example` met lege of duidelijk fictieve waarden;
- lokale `.env`-bestanden buiten Git;
- testaccounts en testdata;
- geredigeerde logs en screenshots;
- zelfgemaakte, docentgeleverde of legaal herbruikbare testmedia.

Wanneer toch een secret in Git belandt, is verwijderen uit het laatste bestand niet genoeg. Stop, meld het, trek het secret in, maak een nieuw secret aan en documenteer het incident zonder het secret te herhalen.

---

## 11. Mondelinge verdediging

Voorzie ongeveer **20 minuten per team**:

1. **architectuuroverzicht** - maximaal 4 minuten;
2. **live demonstratie van uitnodiging/enrollment, Jellyfin, wereldkaart en Minecraft** - maximaal 8 minuten;
3. **aangewezen negatieve test of foutscenario** - maximaal 5 minuten;
4. **individuele vragen** - resterende tijd.

De docent bepaalt tijdens de verdediging welke gebruikersrol, policytest of fout wordt getoond. Een vooraf opgenomen video vervangt de live omgeving niet, maar kan als reservebewijs dienen bij een aantoonbaar infrastructuurprobleem.

Elke student moet:

- de volledige verkeersketen voor de webdiensten en Minecraft kunnen uitleggen;
- minstens één component buiten de eigen hoofdtaak kunnen toelichten;
- een onverwachte fout methodisch kunnen onderzoeken;
- het verschil tussen netwerktoegang en applicatieauthenticatie uitleggen;
- resterende productie- en beschikbaarheidsrisico's kunnen benoemen.

---

## 12. Evaluatie

### 12.1 Teamproduct - 80 punten

| Criterium | Punten | Waarop wordt gelet? |
|---|---:|---|
| Proxmox-, VM- en containerbasis | 10 | resourcebeheer, zelf opgebouwde VM's, segmentatie en reproduceerbare Compose-deployments |
| Securityarchitectuur | 10 | zones, trust boundaries, least privilege, enforcement points en negatieve tests |
| Tailscale en Minecraft-toegang | 13 | drie afzonderlijke nodes, tags, beperkte policy, Split DNS, Minecraftbeveiliging en negatieve tests |
| Traefik en webpublicatie | 12 | routes naar meerdere VM's, lokale/remote entrypoints, backendisolatie, WebSockets, logging en werkende direct play |
| Authentik en identity-aware access | 17 | invitation-based enrollment, pendingstatus, groepsgoedkeuring, Jellyfin-OIDC, forward auth, SSO, MFA, lifecycle, audit, sessiegedrag en fail-closedroutes |
| Integratie, testen en troubleshooting | 12 | samenhang, testmatrix, bewijs, incidentanalyse en foutoplossing |
| Documentatie en repositorykwaliteit | 6 | actualiteit, traceerbaarheid, leesbaarheid, procesdossier, beslissingen en bijdrageoverzicht |

### 12.2 Individuele verdediging - 20 punten

| Criterium | Punten | Waarop wordt gelet? |
|---|---:|---|
| Architectuur en ontwerpkeuzes uitleggen | 6 | samenhang begrijpen en alternatieven kunnen afwegen |
| Testresultaten interpreteren | 5 | niet alleen tonen dat iets werkt, maar verklaren waarom |
| Methodisch troubleshooten | 5 | hypothesen, relevante controles, root cause en oplossing |
| Eigen bijdrage en professionele reflectie | 4 | aantoonbare bijdrage, resterende risico's en productieverbetervoorstellen |

Technische complexiteit zonder betrouwbare basis levert geen hogere score op. Een kleine, goed afgeschermde en volledig geteste mediaserver en Minecraft-wereld zijn sterker dan grote, instabiele omgevingen.

---

## 13. Mogelijke uitbreidingen

Werk pas aan uitbreidingen wanneer alle minimumtests slagen. Bonus is beperkt tot **maximaal 5 punten**, met een totaalscore van maximaal 100.

Mogelijke uitbreidingen:

- TLS met een goed gedocumenteerde interne CA of veilige ACME-opstelling;
- centrale monitoring van VM's, containers, proxy, IdP, Jellyfin en Minecraft;
- waarschuwingen bij hoog CPU-, RAM- of diskgebruik;
- geautomatiseerde configuratie- of securitychecks in CI;
- extra policytests die automatisch aantonen dat verboden toegang verboden blijft;
- een eenvoudige statuspagina met veilige healthinformatie.

Een uitbreiding telt alleen wanneer ze gedocumenteerd, beveiligd en getest is.

---

## 14. Buiten scope van de minimumopdracht

Je hoeft voor het minimum niet:

- Jellyfin of Minecraft werkelijk op het publieke internet te plaatsen;
- de uitnodigingspagina of Authentik-enrollmentflow werkelijk op het publieke internet te plaatsen;
- e-mailverzending, een publiek aanvraagformulier of volledig onbeheerde zelfregistratie te bouwen;
- meer dan twee mediabestanden of 1 GB media te voorzien;
- videotranscoding of hardware acceleration te configureren;
- native Jellyfin-clients voor tv of smartphone te ondersteunen;
- een grote Minecraft-wereld, mods of pluginsets te installeren;
- een volledige wereld vooraf te genereren of de kaart continu en live te renderen;
- Kubernetes, Docker Swarm of een volledig orchestratieplatform te gebruiken;
- een productieklare Authentik-, PostgreSQL- of Proxmox-cluster te bouwen;
- een bepaald direct of DERP-pad kunstmatig af te dwingen;
- campusrouters, access points of centrale firewalls aan te passen;
- echte organisatieaccounts of productiegegevens te gebruiken.

---

## 15. Eindcheck voor indiening

Controleer voor je indient:

- [ ] drie Debian-VM's functioneren binnen het resourcebudget;
- [ ] alle applicaties worden via Compose beheerd;
- [ ] Jellyfin werkt via Traefik en Authentik OIDC;
- [ ] één testbestand speelt af zonder onnodige zware transcoding;
- [ ] de uitnodigingspagina draait op `media01` en is zonder login lokaal en via Tailscale via Traefik bereikbaar;
- [ ] Authentik maakt via een geldige uitnodiging eerst een account zonder servicerechten aan;
- [ ] goedkeuring en offboarding wijzigen aantoonbaar de Authentik-groepen, Tailscale Minecraft-groep en Minecraft-whitelist;
- [ ] de wereldkaart draait op `game01` en is alleen zichtbaar voor `pp-map-viewers`;
- [ ] de uitnodigings- en kaartbackendpoorten zijn alleen vanaf `edge01` bereikbaar;
- [ ] de adminapp gebruikt forward auth en TOTP;
- [ ] Minecraft is lokaal rechtstreeks bereikbaar en extern alleen via de bedoelde VPN-policy;
- [ ] backend-, database-, RCON- en managementpoorten zijn afgeschermd;
- [ ] alleen leden van de Tailscale Minecraft-groep bereiken TCP/25565 via Tailscale;
- [ ] alle verplichte acceptatietests hebben context, resultaat en bewijs;
- [ ] negatieve tests zijn even zorgvuldig uitgevoerd als positieve tests;
- [ ] de repository bevat geen secrets, mediabestanden of persoonlijke gegevens;
- [ ] elk teamlid kan beide toegangspatronen uitleggen en demonstreren.

Sluit het dossier af met een onderbouwd antwoord op deze vraag:

> Waarom hebben de publieke uitnodigingspagina, Jellyfin, de groepsgebonden wereldkaart en Minecraft verschillende beveiligingslagen nodig, en hoe voorkomen jullie dat registratie, VPN-toegang, een reverse proxy of een geslaagde login onbedoeld te veel vertrouwen geeft?
