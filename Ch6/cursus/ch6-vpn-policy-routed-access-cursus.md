# Hoofdstuk 6 - VPN policy en routed access

## 1. Inleiding

In hoofdstuk 5 heb je onderzocht hoe een VPN een privaat netwerkpad bovenop het
internet bouwt. Met Tailscale maakte je een Debian-VM bereikbaar via een overlay-IP,
gebruikte je MagicDNS en vergeleek je directe toegang, subnet routing en een exit node.

De centrale vraag was toen:

> Kan mijn client het doel via de VPN bereiken?

In een enterprise-omgeving is dat slechts de eerste helft van het probleem. Een
werkende tunnel zegt nog niet dat de toegangsrechten correct zijn. Een gestolen laptop,
een vergeten test-VM of een fout getagde server kan technisch verbonden zijn en toch
geen brede toegang mogen krijgen.

De professionelere vraag luidt daarom:

> Mag deze bronidentiteit vanaf dit device naar deze dienst op dit protocol en deze
> poort, en blijft alle andere toegang geblokkeerd?

Dat verschil verandert ook de manier waarop je test. Eén succesvolle `curl` bewijst
alleen dat één flow werkt. Een degelijk testplan bewijst daarnaast dat:

| Controle | Wat toon je ermee aan? |
|---|---|
| noodzakelijke dienst werkt | de bedoelde bedrijfsflow is bruikbaar |
| andere poorten falen | de bestemming is niet breder bereikbaar dan nodig |
| ander intern systeem faalt | een route opent niet automatisch het hele subnet |
| verkeerde lokale user geen SSH krijgt | netwerktoegang is niet hetzelfde als loginrecht |
| oud device of oude key ingetrokken is | toegang volgt ook de lifecycle |

In de workshop behandel je je persoonlijke tailnet als een kleine organisatie. Jij bent
daar tegelijk gebruiker, device-eigenaar en beheerder. Dat is een labvereenvoudiging.
De ontwerpprincipes blijven enterpriseprincipes: identity-based access, least
privilege, scheiding van rollen, gecontroleerde onboarding, audit en cleanup.

Kernidee:

> Een professionele VPN-policy bewijst niet alleen dat de juiste toegang werkt, maar
> ook dat onnodige toegang niet werkt.

De rode draad door dit hoofdstuk is:

```text
behoefte -> bronidentiteit -> doelrol -> protocol/poort
         -> route -> policy -> positieve test -> negatieve test
         -> audit -> lifecycle
```

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. bereikbaarheid onderscheiden van autorisatie;
2. klassieke brede VPN-toegang vergelijken met een identity-aware toegangsmodel;
3. uitleggen waarom lidmaatschap van dezelfde tailnet geen voldoende securitybeleid is;
4. de rol van de tailnet policy file uitleggen;
5. het verschil tussen de standaard allow-all-policy en een expliciete deny-by-default-policy uitleggen;
6. ACL's en grants op hoofdlijnen vergelijken;
7. users, groups, autogroups, devices en tags correct plaatsen;
8. user-owned devices vergelijken met tagged devices;
9. uitleggen waarom tag ownership een securitygrens is;
10. auth keys veilig gebruiken voor serveronboarding;
11. auth key expiry onderscheiden van device- of node-key expiry;
12. een ACL lezen en vertalen naar bron, bestemming, protocol en poort;
13. directionele toegang en antwoordverkeer correct redeneren;
14. deny by omission en least privilege toepassen;
15. policytests met allow- en deny-asserties opstellen;
16. Tailscale SSH onderscheiden van OpenSSH over Tailscale;
17. de twee vereiste policylagen voor Tailscale SSH uitleggen;
18. een subnet router ontwerpen en systematisch troubleshooten;
19. routeadvertentie, routegoedkeuring, routeacceptatie en access policy onderscheiden;
20. SNAT en return routing bij subnet routing op hoofdlijnen uitleggen;
21. routed access beperken tot een specifieke host en service;
22. MagicDNS en Split DNS onderscheiden en in de juiste volgorde testen;
23. een subnet router onderscheiden van een exit node;
24. configuratielogs onderscheiden van netwerkflowlogs;
25. een reproduceerbaar test- en auditrapport schrijven zonder secrets te lekken.

---

## 3. Van bereikbaarheid naar een toegangsbeslissing

### 3.1 Wat hoofdstuk 5 aantoonde

Hoofdstuk 5 legde de nadruk op het netwerkpad. Je controleerde onder meer:

| Onderdeel | Vraag uit hoofdstuk 5 |
|---|---|
| overlay | zijn beide devices lid van dezelfde tailnet? |
| adressering | welk Tailscale-IP heeft de doelhost? |
| naamresolutie | kan MagicDNS de devicenaam oplossen? |
| datapad | is de verbinding direct of gerelayd? |
| route | bestaat een pad naar een achterliggend subnet? |
| exit node | verandert het publieke uitgaande IP-adres? |

Dat zijn noodzakelijke controles. Zonder netwerkpad kan geen enkele applicatieflow
werken. Maar een bestaand pad is nog geen toelating.

Voorbeeld:

```text
route naar 10.20.0.0/16 bestaat
        ≠
student mag elke host en poort in 10.20.0.0/16 gebruiken
```

Een route beantwoordt hoofdzakelijk de vraag **waarheen** een pakket gestuurd moet
worden. Een access policy beantwoordt **of** die flow toegelaten is.

### 3.2 Vier vragen per flow

Voor elke gewenste verbinding stel je minstens vier vragen:

| Vraag | Voorbeeld in het Ch6-lab |
|---|---|
| Wie start de verbinding? | jouw user-owned laptop |
| Naar welke resource? | VM1 met `tag:webserver` |
| Welk protocol en welke poort? | TCP/80 |
| Waarom is dit nodig? | de HTTP-dienst van VM1 testen |

De reden is geen technisch veld in de ACL, maar wel een essentieel ontwerpveld. Zonder
reden kan je achteraf niet beoordelen of een regel nog nodig is.

Een bruikbare policyregistratie bevat daarom meer dan syntaxis:

| Documentatieveld | Voorbeeld |
|---|---|
| business- of labbehoefte | student test webdienst op VM1 |
| bron | `autogroup:member` in het persoonlijke lab |
| bestemming | `tag:webserver` |
| service | TCP/80 |
| eigenaar | student als tailnetbeheerder |
| positieve test | HTTP-response ontvangen |
| negatieve test | TCP/443 niet bereikbaar |
| reviewmoment | na workshop verwijderen of herbeoordelen |

### 3.3 Klassieke VPN-reflex en ZTNA-reflex

Een klassieke remote-access-VPN werd vaak ervaren als een virtuele netwerkstekker. Na
de verbinding kreeg de client een intern adres of een adres uit een VPN-pool. Brede
firewallregels lieten die pool vervolgens naar verschillende interne subnetten toe.

Dat ontwerp kan technisch correct zijn, maar veroorzaakt een riskante denkfout:

> Verbonden met de VPN wordt gelijkgesteld aan vertrouwd.

Zero Trust Network Access, afgekort ZTNA, vertrekt vanuit expliciete toegang. Een
gebruiker wordt niet algemeen "binnen" geplaatst. Toegang hangt af van de identiteit,
het gebruikte device, de doelresource en het beleid voor die concrete flow.

| Brede VPN-reflex | Identity-aware reflex |
|---|---|
| VPN actief betekent intern | VPN actief levert alleen een mogelijk datapad |
| subnet of VPN-pool bepaalt vertrouwen | user, device en rol leveren policycontext |
| toegang tot een netwerksegment | toegang tot een specifieke resource of service |
| positieve test is voldoende | positieve én negatieve tests zijn nodig |
| tijdelijke brede regel blijft vaak staan | tijdelijke afwijking krijgt eigenaar en einddatum |

Tailscale ondersteunt identity-aware policy met users, groups, tags en andere
selectors. Dat maakt een ontwerp echter niet automatisch zero trust. Ook in Tailscale
kan je een regel schrijven die iedereen naar alles laat verbinden.

Kernzin:

> Het product levert policybouwstenen; de ontwerper bepaalt of die bouwstenen werkelijk
> least privilege afdwingen.

---

## 4. Labmodel en gewenste flows

### 4.1 Topologie

In dit hoofdstuk gebruik je een laptop, twee VM's en twee bestaande diensten in het
labnet.

```text
                    persoonlijke tailnet

 +------------------+       direct device access       +---------------------+
 | Laptop           | --------------------------------> | VM1                 |
 | user-owned       |                                   | tag:student-vm      |
 | testclient       |                                   | tag:webserver       |
 +--------+---------+                                   | HTTP TCP/80         |
          |                                             | Tailscale SSH-doel  |
          |                                             +---------------------+
          |
          | routed access
          v
 +---------------------+
 | VM2                 |
 | tag:subnet-router   |
 | route 10.20.0.0/16  |
 +----------+----------+
            |
            | intern labnet
            v
      10.20.0.1     DNS voor voltlab.lan
      10.20.10.4    NetBox via HTTPS
```

VM1 en VM2 krijgen hun gewone lab-IP via DHCP. Die adressen zijn dus meetwaarden die
je tijdens het labo noteert, geen waarden die je uit deze theorie kopieert.

NetBox staat vast op `10.20.10.4` en heeft de interne naam
`netbox.voltlab.lan`. Je gebruikt die server alleen als HTTPS-doel. Je krijgt geen
shell- of beheerrechten op NetBox.

### 4.2 Direct device access en routed access

De twee toegangsvormen lijken voor een gebruiker op elkaar, maar het netwerkpad en de
policydoelen verschillen.

| Kenmerk | Direct device access | Routed access |
|---|---|---|
| Tailscale op eindbestemming | ja | niet noodzakelijk |
| Voorbeeldbestemming | `tag:webserver` | `10.20.10.4` |
| Policydoel | device-identiteit of tag | IP-adres, hostalias of subnet |
| Gateway nodig | nee | VM2 als subnet router |
| Extra foutbronnen | dienst en hostfirewall | forwarding, route, SNAT/return path en LAN-firewall |
| Naamresolutie | MagicDNS voor tailnet-device | Split DNS voor interne zone |

VM1 leert je policy op een Tailscale-device. VM2 leert je dat een route naar een
achterliggend netwerk nog altijd een beperkte policy nodig heeft.

### 4.3 Gewenste en ongewenste flows

Voor de configuratie begint, leg je het verwachte gedrag vast.

| Bron | Doel | Service | Verwacht | Reden |
|---|---|---|---|---|
| laptop | VM1 | HTTP TCP/80 | allow | webdienst testen |
| laptop | VM1 | HTTPS TCP/443 | deny | geen HTTPS-dienst vereist |
| laptop | NetBox | HTTPS TCP/443 | allow | routed access testen |
| laptop | NetBox | SSH TCP/22 | deny | geen beheerrecht op NetBox |
| laptop | DNS-server | DNS UDP/53 en zo nodig TCP/53 | allow | interne zone oplossen |
| laptop | DNS-server | SSH TCP/22 | deny | resolver is geen beheerdoel |

Voor Tailscale SSH voeg je later een afzonderlijk tweelaags testmodel toe. Die feature
gebruikt TCP/22 als netwerktransport en daarnaast een `ssh`-policy voor de lokale user.

Waarom belangrijk?

> Als je de verwachte flows pas na de configuratie bedenkt, pas je je verwachting
> gemakkelijk aan een toevallig resultaat aan. Een vooraf vastgelegde matrix maakt de
> test controleerbaar.

---

## 5. De tailnet policy file

### 5.1 Centrale, declaratieve configuratie

Tailscale bewaart access control en verschillende bijbehorende definities in een
centrale tailnet policy file. De notatie is HuJSON: een JSON-achtige syntaxis waarin
onder meer commentaar en trailing commas mogelijk zijn.

Belangrijke top-levelsecties zijn:

| Sectie | Waarvoor dient ze? |
|---|---|
| `groups` | groepeert users onder een betekenisvolle naam |
| `hosts` | geeft een leesbare alias aan een IP-adres of subnet |
| `tagOwners` | bepaalt wie welke device-tags mag toekennen |
| `acls` | beschrijft netwerktoegang met de oorspronkelijke ACL-syntaxis |
| `grants` | beschrijft moderne netwerk- en eventueel applicatiecapabilities |
| `ssh` | bepaalt wie Tailscale SSH mag gebruiken en als welke lokale user |
| `autoApprovers` | automatiseert goedkeuring van routes of exit nodes voor bevoegde identiteiten |
| `tests` | legt netwerkverwachtingen vast als policy-asserties |
| `sshTests` | legt verwachtingen voor Tailscale SSH vast |

De policy file is meer dan een lijst firewallregels. Ze combineert namen,
identiteitsgroepen, roltoekenning, netwerktoegang en regressietests.

### 5.2 De standaard-policyvalkuil

Een nieuwe of nooit aangepaste tailnet kan een standaardpolicy hebben die brede
connectiviteit toelaat. Dat is gebruiksvriendelijk tijdens de eerste ingebruikname, maar
het betekent dat je niet zomaar mag veronderstellen dat ontbrekende regels automatisch
een deny veroorzaken.

Het onderscheid is cruciaal:

| Situatie | Praktisch gevolg |
|---|---|
| policy nooit aangepast of geen access-controlsectie | de standaard allow-all-policy kan gelden |
| expliciete `acls`- of `grants`-regels aanwezig | alleen gematchte flows worden toegestaan |
| expliciete lege access-controlsectie | geen netwerkflows toegestaan via die policylaag |

Typische fout:

> Een student verwijdert een allow-regel, maar laat geen expliciete deny-by-default
> access-controlconfiguratie achter en besluit dat de bestemming nu zeker geblokkeerd
> is.

Controleer daarom niet alleen de regel die je toevoegde. Controleer de volledige
effectieve policy en voer een negatieve test uit.

### 5.3 ACL's en grants

Tailscale kent twee syntaxisvormen voor access control:

| Eigenschap | ACL's | Grants |
|---|---|---|
| Status | oorspronkelijke syntaxis, blijft ondersteund | aanbevolen voor nieuwe policy's |
| Netwerktoegang | bron, doel, protocol en poort | bron, doel en netwerkcapabilities in `ip` |
| Applicatiecapabilities | nee | mogelijk via `app` als de applicatie dit ondersteunt |
| Voorbeeldveld voor service | `dst: ["tag:webserver:80"]` | `ip: ["tcp:80"]` |
| Gebruik in deze workshop | ja, om aan te sluiten op het bestaande labmateriaal | conceptueel vergelijken |

ACL-voorbeeld uit het lab:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["tag:webserver:80"]
}
```

Dezelfde netwerkbedoeling in grant-syntaxis:

```json
{
  "src": ["autogroup:member"],
  "dst": ["tag:webserver"],
  "ip": ["tcp:80"]
}
```

In dit hoofdstuk gebruik je ACL's omdat de workshop en voorbeeldbestanden daarop zijn
gebouwd. Dat is een bewuste didactische keuze, geen aanbeveling om elk nieuw
productieontwerp nog met de oudere syntaxis te starten.

ACL's en grants kunnen in dezelfde policy file bestaan. Hun toelatingen zijn
additief: een flow die door één passende regel wordt toegestaan, wordt niet opnieuw
geblokkeerd door een smallere regel in de andere sectie. Controleer bij een migratie
dus altijd het gecombineerde effect.

In productie:

> Beoordeel voor nieuwe policy's de actuele grant-syntaxis en plan een gecontroleerde
> migratie voor bestaande ACL's. Verander de syntaxis nooit zonder regressietests.

### 5.4 Vier eigenschappen van netwerkpolicy

Tailscale access control heeft enkele eigenschappen die je redenering bepalen.

| Eigenschap | Betekenis | Praktisch gevolg |
|---|---|---|
| deny by default na expliciete policy | niet-toegestane nieuwe flows worden geblokkeerd | je schrijft vooral allow-regels |
| directioneel | `A -> B` geeft niet automatisch `B -> A` | server krijgt geen initiatierecht naar client |
| stateful voor antwoordverkeer | antwoorden op een toegelaten verbinding mogen terug | geen spiegelregel nodig voor elke response |
| lokaal afgedwongen | devices ontvangen en handhaven packet filters | normale payload hoeft niet langs de control plane |

Directioneel betekent niet dat een TCP-response geblokkeerd wordt.

```text
laptop start TCP/80 naar VM1   -> policy controleert nieuwe flow
VM1 antwoordt binnen sessie    -> antwoordverkeer hoort bij toegelaten flow
VM1 start zelf nieuwe flow     -> aparte toelating nodig
```

Kernzin:

> Een directionele allow-regel geeft initiatierecht in één richting; ze verbiedt niet
> het noodzakelijke antwoordverkeer van die toegelaten sessie.

---

## 6. Users, groups, autogroups en devices

### 6.1 Users

Een user is een menselijke of organisatorische identiteit in de tailnet. De login komt
meestal uit een identity provider of een ondersteunde loginmethode.

| User | Mogelijke rol | Typisch device |
|---|---|---|
| `student01@example.edu` | student | persoonlijke laptop |
| `teacher@example.edu` | docent | beheerde werkplek |
| `netadmin@example.edu` | netwerkbeheerder | adminwerkplek |

Een user is een geschikte policybron voor persoonlijke endpoints. De organisatie kan
de user activeren, schorsen of verwijderen en zo nieuwe toegang beïnvloeden.

Voor servers is een persoonlijke gebruikersidentiteit minder stabiel. De server mag niet
van rol veranderen omdat de persoon die hem ooit installeerde van functie verandert.

### 6.2 Groups

Een group bundelt users met dezelfde toegangsbehoefte.

```json
"groups": {
  "group:students": [
    "student01@example.edu",
    "student02@example.edu"
  ],
  "group:teachers": [
    "teacher@example.edu"
  ]
}
```

Groups verbeteren meer dan alleen leesbaarheid.

| Voordeel | Concrete betekenis |
|---|---|
| centrale wijziging | een mover wijzig je in een groep, niet in elke regel |
| consistente rol | dezelfde groepsnaam kan in meerdere flows terugkomen |
| reviewbaarheid | een reviewer ziet sneller welke organisatorische rol toegang krijgt |
| minder kopieerfouten | adressen staan niet tientallen keren verspreid |

Een group is geen reden voor toegang. `group:students` mag niet automatisch naar alle
studentenservers. De regel moet nog altijd aangeven welke dienst nodig is.

### 6.3 Autogroups

Een autogroup is een ingebouwde selector die Tailscale zelf invult.

In dit hoofdstuk zijn vooral deze autogroups relevant:

| Autogroup | Betekenis | Gebruik |
|---|---|---|
| `autogroup:member` | devices van directe tailnetleden | eenvoudige bron in persoonlijke labtailnet |
| `autogroup:admin` | devices van users met adminrol | lab-eigenaar van tags |
| `autogroup:network-admin` | devices van netwerkbeheerders | fijnere productiebeheersrol |
| `autogroup:self` | andere devices van dezelfde user | persoonlijke device-to-deviceflow |
| `autogroup:internet` | internet als bestemming via exit nodes | toestemming om exit nodes te gebruiken |

`autogroup:member` en `*` betekenen niet hetzelfde. Een brede wildcard kan meer
bronnen selecteren dan gewone directe leden. Gebruik alleen een selector waarvan je de
scope kan uitleggen.

In het persoonlijke lab is `autogroup:member` praktisch omdat jij meestal het enige
gewone lid bent. In een gedeelde tailnet zou diezelfde selector alle directe leden
omvatten en mogelijk te breed zijn.

### 6.4 Devices

Een device, ook node genoemd, is een systeem waarop Tailscale draait.

| Device-eigenschap | Waarom relevant? |
|---|---|
| machine name | helpt het doel herkennen en wordt door MagicDNS gebruikt |
| Tailscale-IP | identificeert het overlay-endpoint |
| user of tags | bepaalt welke identity-based policy van toepassing is |
| online/last seen | ondersteunt operationele inventariscontrole |
| routes | toont of het device subnetten of een exit node aanbiedt |
| key expiry | bepaalt of herauthenticatie nodig wordt |
| Tailscale SSH-status | toont of het device poort 22 voor tailnetverkeer overneemt |

Een naam zoals `debian` is technisch bruikbaar maar organisatorisch zwak. Een naam
zoals `s01-ch6-web-01` toont student, hoofdstuk, rol en volgnummer.

Controleer:

> Kan je in de device-inventaris voor elke node de eigenaar, functie, policyrol en
> noodzaak uitleggen?

---

## 7. User-owned devices en tagged devices

### 7.1 User-owned device

Een user-owned device is gekoppeld aan de identiteit van een persoon. Een laptop is
het standaardvoorbeeld.

```text
Alice -> laptop-alice
```

Dat model past omdat:

| Kenmerk | Waarom passend voor een laptop? |
|---|---|
| persoonlijk gebruik | het toestel handelt namens één gebruiker |
| interactieve login | de gebruiker kan zich via de browser aanmelden |
| user lifecycle | schorsing of vertrek hoort toegang te beïnvloeden |
| policy op identiteit | rechten volgen de persoon of groep |

Een user-owned endpoint blijft ook een beveiligingsrisico. Als de user legitiem is
maar het device gecompromitteerd, kan toegestane toegang misbruikt worden. In productie
combineer je identiteit daarom waar relevant met devicebeheer en posturevoorwaarden.

### 7.2 Tagged device

Een tag geeft een niet-menselijk device een rolidentiteit.

| Tag | Betekenis in het lab |
|---|---|
| `tag:student-vm` | algemene serverrol voor VM1 |
| `tag:webserver` | VM1 biedt de HTTP-dienst aan |
| `tag:ssh-server` | device is een Tailscale SSH-doel |
| `tag:subnet-router` | VM2 biedt routes aan |
| `tag:exit-node` | device heeft een exit-nodefunctie |

Tags zijn niet gewoon labels voor rapportering. Zodra je een device tagt, gebruikt het
een tag-based identity in plaats van de user-based identity. Een device is dus niet
tegelijk user-owned en tagged.

Dat onderscheid voorkomt een veel voorkomende denkfout:

```text
fout:  server is van Alice én heeft tag:webserver
juist: server handelt als tagidentiteit; Alice kan beheerder van die tag zijn
```

### 7.3 Meerdere tags

Een device kan meerdere tags hebben. VM1 kan bijvoorbeeld tegelijk
`tag:student-vm`, `tag:webserver` en `tag:ssh-server` dragen.

De effectieve identiteit is de combinatie van die tags. Regels die een van die tags als
doel of bron selecteren, kunnen op het device van toepassing zijn. De tags werken dus
niet automatisch als een strenge doorsnede.

Voorbeeld:

| Regel | Gevolg voor VM1 met drie tags |
|---|---|
| HTTP naar `tag:webserver` | VM1 ontvangt HTTP-toegang |
| SSH naar `tag:ssh-server` | VM1 valt onder die SSH-doelrol |
| monitoring naar `tag:student-vm` | VM1 ontvangt ook die algemene serverflow |

Typische fout:

> Een beheerder voegt een extra tag toe om toegang te beperken, maar die extra tag
> activeert net een bijkomende brede allow-regel.

Controleer daarom het totale effect van alle tags.

### 7.4 Tag owners als securitygrens

Tags worden gedefinieerd via `tagOwners`. De owners mogen een device met die rol
authenticeren of de tag toekennen.

```json
"tagOwners": {
  "tag:student-vm": ["autogroup:admin"],
  "tag:webserver": ["autogroup:admin"],
  "tag:ssh-server": ["autogroup:admin"],
  "tag:subnet-router": ["autogroup:admin"]
}
```

Waarom is dat securitykritiek?

Stel dat een aanvaller zelf `tag:webserver` kan toekennen. Als andere systemen
uitgaande toegang naar webservers krijgen, kan het kwaadaardige device zich voordoen als
een toegelaten serverrol.

| Foute tag-ownerkeuze | Risico |
|---|---|
| alle members mogen servertags gebruiken | elke user kan een eigen device in een serverrol plaatsen |
| CI-systeem mag productietags uitdelen zonder begrenzing | compromis van CI wordt infrastructuurcompromis |
| persoonlijke admin blijft owner na functiewijziging | mover behoudt indirecte macht over toegang |
| geen review van taghiërarchie | een tag kan onverwacht andere tags toekennen |

In het persoonlijke lab is `autogroup:admin` verdedigbaar omdat jij de enige beheerder
bent. In productie scheid je bij voorkeur dagelijks gebruik, netwerkbeheer en
automatische provisioning.

De platformrollen Owner, Admin en Network admin hebben zelf brede mogelijkheden om
tags toe te kennen. Een strenge `tagOwners`-sectie compenseert dus niet voor te veel
users met zo'n beheerrol. Review zowel tag ownership als de centrale adminrollen.

Kernzin:

> Wie een tag mag toekennen, bepaalt indirect welke identity en welke toegangsrechten
> een device kan krijgen.

---

## 8. Auth keys en gecontroleerde serveronboarding

### 8.1 Waarom auth keys bestaan

Een persoonlijke laptop kan een interactieve browserlogin gebruiken. Een headless
server, container of automatisch uitgerolde VM heeft vaak geen geschikte interactieve
flow. Een auth key laat zo'n node registreren zonder browserlogin op die node.

Auth keys passen onder meer bij:

| Situatie | Waarom een auth key? |
|---|---|
| VM-template | onboarding moet herhaalbaar zijn |
| cloud-init | server registreert tijdens de eerste boot |
| container | workload kan kort leven en automatisch starten |
| IoT- of edge-device | er is geen lokale browser |
| infrastructuurautomatisatie | menselijke klikstappen moeten verdwijnen |

Een auth key is een credential. Wie de key kan gebruiken, kan onder de eigenschappen
van die key een node proberen registreren. Daarom hoort de key in een secret store en
niet in code, shell history, screenshots of verslagen.

### 8.2 Eigenschappen van een auth key

| Eigenschap | Wat betekent dit? | Wanneer logisch? | Belangrijk risico |
|---|---|---|---|
| one-off | key kan één registratie uitvoeren | één lab-VM of individuele server | verlies vóór gebruik laat één ongewenste registratie toe |
| reusable | key kan meerdere nodes registreren | gecontroleerde vlootuitrol | diefstal kan meerdere ongewenste nodes opleveren |
| ephemeral | inactieve tijdelijke node wordt automatisch verwijderd | containers en kortlevende jobs | niet geschikt als blijvende serveridentiteit nodig is |
| pre-approved | node omzeilt afzonderlijke device approval | vertrouwde automatisatie | provisioningpad krijgt extra macht |
| tagged | geregistreerde node neemt tagidentiteit aan | servers en infrastructuurnodes | verkeerde tag vergroot privileges |

Voor VM1 kies je bij voorkeur een one-off key met korte geldigheidsduur en de vereiste
servertags.

### 8.3 Drie soorten verval niet verwarren

Er bestaan verschillende momenten in de lifecycle.

| Begrip | Wat vervalt? | Effect |
|---|---|---|
| auth key expiry | de onboardingcredential | key kan geen nieuwe node meer registreren |
| auth key revocation | beheerder trekt de onboardingcredential in | toekomstige registraties met die key stoppen |
| device/node key expiry | de identiteitssleutel van een reeds geregistreerde node | node moet herauthenticeren of verliest connectiviteit |

Een verlopen auth key verwijdert een reeds geregistreerd device niet automatisch. De
key diende om de node binnen te brengen; daarna gebruikt het device eigen sleutels.

Tagged devices hebben device-key expiry doorgaans uitgeschakeld na authenticatie. Dat
is praktisch voor unattended servers, maar verhoogt het belang van inventarisreview en
expliciete offboarding.

### 8.4 Heraanmelding van VM1

Conceptueel verandert VM1 van een persoonlijke naar een servicegerichte identiteit.

```text
voor:
VM1 identity = jouw user

na tagged onboarding:
VM1 identity = tag:student-vm + tag:webserver
```

Een typische labflow is:

```text
sudo tailscale status
sudo tailscale logout
sudo tailscale up --auth-key=<AUTH-KEY> --hostname=<VM1-NAME>
tailscale status
tailscale ip -4
```

Gebruik alleen een placeholder in documentatie. Als je terminal de echte key toont,
maak je daarvan geen screenshot.

### 8.5 Onboardingcontrole

| Controle | Verwacht | Waarom? |
|---|---|---|
| machine name is betekenisvol | VM1 herkenbaar | voorkomt policy- en testverwarring |
| vereiste tags aanwezig | juiste serverrol | selectors moeten het bedoelde device matchen |
| oude user ownership verdwenen | tag-based identity actief | voorkomt fout mentaal model |
| auth key one-off of ingetrokken | niet herbruikbaar na lab | beperkt misbruik |
| key niet in verslag of history | credential blijft geheim | voorkomt lek via documentatie |
| device-keyexpiry bewust | gekende lifecycle | server blijft niet ongezien permanent actief |

Kernzin:

> Auth keys automatiseren onboarding; ze vervangen geen tag governance, secretbeheer
> of offboarding.

---

## 9. ACL's lezen en schrijven

### 9.1 Anatomie van een ACL

Een ACL-regel beschrijft welke bron een nieuwe netwerkflow naar welke bestemming mag
starten.

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "dst": ["tag:webserver:80"]
}
```

| Veld | Betekenis | Vraag die je beantwoordt |
|---|---|---|
| `action` | wat doet de regel bij een match? | wordt deze flow toegestaan? |
| `src` | startende identiteit of bronset | wie initieert de verbinding? |
| `dst` | doel en poort | welke resource en service? |
| `proto` | optioneel IP-protocol | alleen TCP, alleen UDP of ander protocol? |

Lees de regel altijd in een volledige zin:

> Devices van directe tailnetleden mogen een verbinding starten naar TCP of UDP-poort
> 80 op devices met `tag:webserver`.

Omdat `proto` ontbreekt, specificeert deze ACL niet uitsluitend TCP. Voor een HTTP-flow
is een expliciete `"proto": "tcp"` didactisch duidelijker:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["tag:webserver:80"]
}
```

ICMP gebruikt geen TCP- of UDP-poort. Zodra netwerktoegang voor een bron-doelpaar
bestaat, kan ICMP daardoor anders reageren dan je op basis van één poortregel verwacht.
Gebruik een ping dus als bereikbaarheidscontrole, niet als bewijs dat een applicatiepoort
open of dicht is.

### 9.2 Van mensentaal naar policy

Begin niet met wildcards. Begin met de behoefte.

Mensentaal:

> De laptop van een tailnetlid moet de HTTP-dienst op VM1 kunnen testen.

Vertaling:

| Beslissing | Keuze | Verantwoording |
|---|---|---|
| bron | `autogroup:member` | vereenvoudiging voor persoonlijke labtailnet |
| bestemming | `tag:webserver` | de rol blijft stabiel bij heruitrol |
| protocol | TCP | HTTP gebruikt hier TCP |
| poort | 80 | alleen de labwebdienst is nodig |

Policy:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["tag:webserver:80"]
}
```

### 9.3 Selectorprecisie

Elke selector bepaalt de scope.

| Selector | Scope | Beoordeling in het lab |
|---|---|---|
| individuele user | één identiteit | precies, maar minder schaalbaar |
| `group:students` | gedefinieerde studentengroep | logisch in gedeelde tailnet |
| `autogroup:member` | alle directe leden | bruikbaar in persoonlijke tailnet |
| `tag:webserver` | alle devices met die serverrol | stabiel en rolgericht |
| specifiek IP | één adres | precies, maar kan minder betekenisvol zijn |
| subnet-CIDR | alle adressen in prefix | alleen gebruiken als volledige scope nodig is |
| `*` | zeer breed | alleen met expliciete verantwoording |

De nauwkeurigheid van de regel wordt begrensd door haar breedste onderdeel. Een
specifieke poort compenseert niet altijd voor een bron die veel meer identities omvat
dan bedoeld.

### 9.4 Hosts als leesbare alias

Voor een vast intern IP kan je in een policy een hostalias definiëren.

```json
"hosts": {
  "netbox-lab": "10.20.10.4",
  "lab-dns": "10.20.0.1"
}
```

Daarna kan een regel leesbaarder worden:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["netbox-lab:443"]
}
```

Een alias verbetert leesbaarheid, niet security. Als `netbox-lab` naar een verkeerd IP
wijst, is de policy nog altijd fout.

### 9.5 Deny by omission

Na het definiëren van een expliciete deny-by-default access policy schrijf je normaal
geen afzonderlijke deny-regel voor elke verboden flow. Niet gematchte nieuwe flows zijn
geblokkeerd.

```text
allow TCP/80 naar tag:webserver
geen allow voor TCP/443
gevolg: TCP/443 is niet toegestaan
```

Typische fout:

> "SSH staat nergens als deny, dus misschien is het toch open."

Correcte redenering:

> Binnen een expliciete deny-by-default-policy moet er een passende allow bestaan.
> Zonder die allow wordt de nieuwe flow niet toegelaten.

Kernzin:

> Deny by omission werkt alleen als je de volledige effectieve policy kent en niet
> ongemerkt op de standaard allow-all-policy vertrouwt.

---

## 10. Policytests als regressiebeveiliging

### 10.1 Runtime-tests en policytests

Er zijn twee verschillende testniveaus.

| Testniveau | Voorbeeld | Wat bewijst het? |
|---|---|---|
| runtime-test | `curl`, `nc`, `ssh`, `nslookup` | werkelijk gedrag van route, policy, host en service |
| policytest | `tests` in de policy file | de policy-engine evalueert een verwachte allow of deny |

Een policytest start geen echte HTTP-sessie en controleert geen webserver. Ze voorkomt
wel dat een beleidswijziging een bekende verwachting verbreekt.

### 10.2 Voorbeeld van netwerkpolicytests

```json
"tests": [
  {
    "src": "<student-login-email>",
    "proto": "tcp",
    "accept": [
      "tag:webserver:80",
      "10.20.10.4:443"
    ],
    "deny": [
      "tag:webserver:443",
      "10.20.10.4:22",
      "10.20.0.1:22"
    ]
  }
]
```

Gebruik in een echte policy een concrete, bestaande bronidentiteit in plaats van de
placeholder.

| Assertie | Waarom nuttig? |
|---|---|
| webserverpoort 80 moet werken | voorkomt onbedoelde uitval van de labdienst |
| NetBox-poort 443 moet werken | bewaakt de vereiste routed flow |
| webserverpoort 443 moet falen | detecteert verbreding van device access |
| NetBox-poort 22 moet falen | beschermt beheerpoort achter subnet router |
| DNS-serverpoort 22 moet falen | voorkomt dat de resolver een algemeen beheerdoel wordt |

Als een test faalt, weigert Tailscale de gewijzigde policy. Dat maakt de test een
preventieve controle, geen rapport achteraf.

### 10.3 Protocolspecifieke tests

DNS gebruikt meestal UDP/53, maar kan onder bepaalde omstandigheden TCP/53 gebruiken,
bijvoorbeeld bij grotere antwoorden of fallback. Test daarom bewust welk protocol je
toelaat.

```json
{
  "src": "<student-login-email>",
  "proto": "udp",
  "accept": ["10.20.0.1:53"]
}
```

Als productievereisten ook TCP/53 vragen, voeg je daarvoor een afzonderlijke regel en
test toe. Zo zie je welk protocol faalt.

### 10.4 Wat policytests niet bewijzen

| Niet getest | Aanvullende runtimecontrole |
|---|---|
| proces luistert op poort | `ss -lntup` op beheerde doelhost |
| route is geïnjecteerd | routing table en Tailscale-status controleren |
| hostfirewall laat verkeer toe | firewallregels en verbindingspoging onderzoeken |
| DNS-record is correct | `nslookup` of `dig` uitvoeren |
| TLS-certificaat is geldig | normale HTTPS-client zonder `-k` gebruiken |
| applicatie is functioneel | applicatiespecifieke request uitvoeren |

Kernzin:

> Policytests bewaken de toegangsintentie; runtime-tests bewijzen het volledige
> end-to-endgedrag.

---

## 11. Least privilege en brede regels

### 11.1 Van dienstbehoefte naar minimale flow

Least privilege betekent dat de bron alleen de toegang krijgt die nodig is voor de
opdracht of bedrijfsfunctie.

| Behoefte | Te brede regel | Minimale regel |
|---|---|---|
| HTTP op VM1 | member naar `*:*` | member naar `tag:webserver:80` via TCP |
| NetBox openen | member naar `10.20.0.0/16:*` | member naar `10.20.10.4:443` via TCP |
| interne zone oplossen | member naar DNS-server op alle poorten | member naar UDP/53 en zo nodig TCP/53 |
| Tailscale SSH als `debian` | alle users naar alle servers als elke lokale user | bron naar specifieke tag, TCP/22 en user `debian` |

### 11.2 Waarom `*:*` gevaarlijk is

```json
{
  "action": "accept",
  "src": ["*"],
  "dst": ["*:*"]
}
```

Deze regel maakt bijna elke fijnere regel ernaast irrelevant voor beperking. Een
pakket hoeft maar één allow-regel te matchen. Een strenge regel onderaan herstelt dus
niet wat een eerdere brede allow al toestaat.

| Breed patroon | Praktisch risico |
|---|---|
| `src: ["*"]` | onverwachte identities kunnen verbindingen starten |
| `dst: ["*:*"]` | elke gevonden dienst wordt bereikbaar |
| volledig `/16` op alle poorten | honderden of duizenden mogelijke adressen vallen in scope |
| alle members naar servertag op `*` | beheer- en databasediensten liften mee |
| oude tijdelijke allow | testtoegang wordt onbedoeld permanent |

### 11.3 Systematisch versmallen

Gebruik bij een brede regel deze volgorde:

1. Schrijf de echte behoefte zonder syntaxis op.
2. Kies de kleinste passende bronidentiteit.
3. Kies een betekenisvolle doelrol of specifiek intern doel.
4. Beperk protocol en poort.
5. Leg de reden en eigenaar vast.
6. Voeg policytests toe.
7. Voer runtime allow- en deny-tests uit.
8. Verwijder de tijdelijke brede regel.

Voorbeeld:

| Stap | Uitwerking |
|---|---|
| behoefte | student bekijkt NetBox-HTTPS-pagina |
| bron | persoonlijk lab: `autogroup:member` |
| doel | `10.20.10.4` |
| service | TCP/443 |
| positieve test | `curl -kI https://10.20.10.4` |
| negatieve test | `nc -vz 10.20.10.4 22` |
| cleanup | routed allow na workshop herbeoordelen |

Kernzin:

> Een brede allow-regel wordt niet veilig door daarnaast ook een smalle regel te
> schrijven; de brede match moet weg.

---

## 12. Tailscale SSH en OpenSSH over Tailscale

### 12.1 Drie begrippen uit elkaar houden

Bij SSH over een tailnet worden drie zaken vaak door elkaar gehaald.

| Begrip | Wat gebeurt er? |
|---|---|
| klassieke SSH buiten Tailscale | OpenSSH-client bereikt `sshd` via een LAN- of publiek IP |
| OpenSSH over Tailscale | gewone SSH-client bereikt `sshd` via het Tailscale-IP |
| Tailscale SSH | `tailscaled` neemt inkomend TCP/22 op het Tailscale-IP over en gebruikt de tailnetidentiteit voor authenticatie en autorisatie |

Tailscale SSH verandert niets aan `sshd_config` of `authorized_keys` voor verbindingen
buiten het Tailscale-IP. De gewone SSH-server kan dus nog via andere interfaces werken,
afhankelijk van hostfirewall en configuratie.

### 12.2 Tailscale SSH gebruikt wel TCP/22

Tailscale SSH is een aparte autorisatielaag, maar geen poortloos protocol. Op de
bestemming neemt Tailscale TCP/22 over voor verkeer naar het Tailscale-IP.

Een toegelaten Tailscale SSH-sessie vereist daarom drie voorwaarden:

```text
1. Tailscale SSH staat aan op de bestemming
2. netwerkpolicy laat bron -> bestemming TCP/22 toe
3. ssh-policy laat bron -> bestemming -> lokale user toe
```

Als één voorwaarde ontbreekt, werkt de sessie niet.

Op een ondersteunde doelhost schakel je de feature bijvoorbeeld in met:

```text
sudo tailscale set --ssh
```

Controleer vóór je de feature later uitschakelt of een ander beheerspad bestaat. Een
wijziging aan de SSH-feature kan bestaande sessies onderbreken.

Voorbeeld van de netwerklaag:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["tag:student-vm:22"]
}
```

Voorbeeld van de SSH-laag:

```json
"ssh": [
  {
    "action": "accept",
    "src": ["autogroup:member"],
    "dst": ["tag:student-vm"],
    "users": ["debian"]
  }
]
```

Het lab gebruikt hier de algemene VM1-rol `tag:student-vm`. In een grotere omgeving kan
een aparte `tag:ssh-server` duidelijker afbakenen welke servers überhaupt een
SSH-doel mogen zijn.

### 12.3 Wat controleert elke laag?

| Laag | Vraag | Voorbeeld van mislukking |
|---|---|---|
| featurestatus op server | onderschept Tailscale TCP/22? | `--ssh` werd niet ingeschakeld |
| netwerkpolicy | mag de bron TCP/22 bereiken? | geen ACL/grant voor poort 22 |
| SSH-policy | mag deze bron als deze lokale user aanmelden? | `debian` toegelaten, `root` niet |
| lokale OS-context | bestaat de user en mag die werken? | lokale account `debian` ontbreekt |

Dit gelaagde model lijkt op netwerktoegang plus applicatieautorisatie. De netwerklaag
opent alleen het pad. De `ssh`-sectie beslist over de Tailscale SSH-login.

### 12.4 `accept` en `check`

Een SSH-regel kan een verbinding meteen accepteren of periodieke herauthenticatie
vereisen.

| Action | Gedrag | Geschikt voor |
|---|---|---|
| `accept` | bestaande tailnetidentiteit volstaat | laagrisico-lab of sterk begrensde flow |
| `check` | gebruiker moet volgens een periode opnieuw authenticeren | gevoelige beheeracties of productie |

Voorbeeld:

```json
{
  "action": "check",
  "src": ["group:netadmins"],
  "dst": ["tag:production"],
  "users": ["root"],
  "checkPeriod": "1h"
}
```

`check` vervangt geen least privilege. Het voegt herauthenticatie toe aan een reeds
beperkte SSH-flow.

### 12.5 Correct testen

Zowel `tailscale ssh debian@<vm1-name>` als een geschikte gewone SSH-client naar het
Tailscale-IP kan uiteindelijk de Tailscale SSH-server op TCP/22 bereiken wanneer die
feature actief is. Je kan die twee commands daarom niet betrouwbaar gebruiken om
"Tailscale SSH" tegenover "klassieke SSH op hetzelfde Tailscale-IP" te bewijzen.

Gebruik een testmatrix die de drie voorwaarden afzonderlijk varieert:

| Test | Verwacht | Wat bewijst dit? |
|---|---|---|
| netwerkregel voor TCP/22 ontbreekt | verbinding faalt | netwerkpoort is eerste gate |
| TCP/22 toegestaan, geen passende SSH-regel | login faalt | netwerktoegang is geen SSH-autorisatie |
| TCP/22 en SSH-user `debian` toegestaan | login werkt | beide policylagen kloppen |
| aanmelden als `root` zonder toelating | login faalt | lokale userscope is beperkt |
| verbinding via gewoon lab-IP | gedrag van OpenSSH/hostfirewall | dit pad valt buiten de tailnetpolicy |

Een `nc -vz <tailscale-ip> 22`-test controleert hoogstens of TCP/22 bereikbaar lijkt.
Hij bewijst niet dat een bepaalde user via Tailscale SSH mag aanmelden.

Typische fout:

> Een student verwacht dat Tailscale SSH werkt terwijl de netwerkpolicy TCP/22
> blokkeert, omdat de `ssh`-sectie volgens hem "apart" is.

Kernzin:

> Tailscale SSH heeft een aparte SSH-policy, maar heeft daarnaast nog altijd een
> toegelaten netwerkpad naar TCP/22 nodig.

---

## 13. Subnet routers

### 13.1 Wat een subnet router doet

Een subnet router is een Tailscale-device dat verkeer doorstuurt naar een netwerk
waarop de eindbestemmingen zelf geen Tailscale hoeven te draaien.

```text
laptop 100.x.y.z
      |
      | versleutelde tailnetflow
      v
VM2 subnet router
      |
      | intern labnet 10.20.0.0/16
      v
NetBox 10.20.10.4
```

Dit is nuttig voor legacyservers, printers, netwerktoestellen of een gefaseerde
migratie. Het vergroot tegelijk de scope: één router kan toegang bieden tot veel
adressen achter zich.

### 13.2 Voorwaarden voor een werkende routed flow

| Voorwaarde | Functie | Typische fout |
|---|---|---|
| Tailscale op VM2 | verbindt de router met de tailnet | node offline of verkeerd aangemeld |
| IP forwarding | laat het OS pakketten tussen interfaces doorsturen | forwarding alleen tijdelijk of niet actief |
| routeadvertentie | VM2 kondigt `10.20.0.0/16` aan | verkeerd prefix geadverteerd |
| routegoedkeuring | beheerder aanvaardt de aangekondigde route | route blijft pending |
| routeacceptatie op client | client installeert of aanvaardt de route | Linux-client accepteert routes niet |
| access policy | laat de concrete bron-doelflow toe | route bestaat maar packet filter blokkeert |
| LAN- en hostfirewall | interne flow wordt geaccepteerd | doelhost blokkeert bron of poort |
| return path of SNAT | antwoord vindt de weg terug | asymmetrische routing of ontbrekende route |

Routeadvertentie en policy werken op verschillende lagen.

```text
route zonder allow  -> pakket heeft een pad, maar wordt niet toegelaten
allow zonder route  -> policy zou flow toelaten, maar client kent geen pad
route + allow       -> noodzakelijke maar nog niet altijd voldoende combinatie
```

### 13.3 Adverteren, goedkeuren en accepteren

VM2 adverteert het labprefix bijvoorbeeld met:

```text
sudo tailscale up --advertise-routes=10.20.0.0/16 --hostname=<VM2-NAME>
```

Daarna volgt een bestuurlijke stap: een beheerder keurt de route goed, of een passende
`autoApprovers`-configuratie automatiseert dat voor een bevoegde identiteit.

Tot slot moet de client de subnetroute gebruiken. Windows, macOS en mobiele clients
accepteren routes doorgaans standaard. Een Linux-client vereist vaak een expliciete
instelling zoals:

```text
sudo tailscale set --accept-routes
```

Controleer altijd het werkelijke clientgedrag en de actuele routing table.

### 13.4 IP forwarding persistent maken

Dit command wijzigt IPv4-forwarding runtime:

```text
sudo sysctl -w net.ipv4.ip_forward=1
```

Na een reboot kan die instelling verdwenen zijn. In een productieopstelling leg je de
instelling persistent vast volgens de Linux-distributie en controleer je ook
IPv6-forwarding als je IPv6-prefixen routeert.

Labkeuze:

> Een runtime-`sysctl` volstaat om het datapad tijdens één workshop zichtbaar te
> maken. Het is geen volledige productiedeployment.

### 13.5 SNAT en return routing

Een Linux-subnetrouter gebruikt standaard doorgaans source NAT voor verkeer naar het
achterliggende subnet. De interne host ziet dan het LAN-IP van VM2 als bron, niet het
oorspronkelijke Tailscale-IP van de laptop.

| Ontwerp | Voordeel | Nadeel |
|---|---|---|
| standaard SNAT | interne hosts hebben geen route naar Tailscale-adressen nodig | oorspronkelijke client-IP is minder zichtbaar op doelhost |
| SNAT uit | doelhost ziet oorspronkelijke bron | interne omgeving heeft correcte return route nodig |

Als je SNAT uitschakelt, moet het interne netwerk weten hoe het Tailscale-adresbereik
via VM2 terug bereikt. Anders komt de heenweg aan maar verdwijnt het antwoord.

In productie:

> Kies SNAT niet alleen omdat het snel werkt. Weeg routingcomplexiteit,
> brontraceerbaarheid, firewallbeleid en logging tegen elkaar af.

---

## 14. Routed access beperken

### 14.1 Routebreedte en policybreedte

VM2 adverteert in het lab `10.20.0.0/16`. Dat brede prefix is nodig omdat zowel de
DNS-server op `10.20.0.1` als NetBox op `10.20.10.4` bereikbaar moeten kunnen zijn.

Een breed geadverteerd prefix verplicht je niet om het volledige prefix toe te laten.

| Laag | Labkeuze |
|---|---|
| route | `10.20.0.0/16` via VM2 |
| NetBox-policy | alleen `10.20.10.4:443` via TCP |
| DNS-policy | alleen `10.20.0.1:53` via vereiste protocollen |
| overige hosts en poorten | geen allow |

Voor NetBox:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "tcp",
  "dst": ["10.20.10.4:443"]
}
```

Deze regel geeft geen toegang tot:

| Niet toegelaten door deze regel | Waarom niet? |
|---|---|
| `10.20.10.4:22` | andere poort |
| `10.20.10.4:80` | andere poort |
| `10.20.10.5:443` | ander adres |
| VM2 op zijn Tailscale-IP | routerdevice is niet het routed doel-IP |
| volledige `10.20.0.0/16` | alleen één host wordt geselecteerd |

### 14.2 Routerdevice en subnet zijn verschillende doelen

Toegang tot `tag:subnet-router:22` is toegang tot VM2 zelf. Toegang tot
`10.20.10.4:443` loopt via VM2 naar NetBox.

```text
tag:subnet-router:22  -> management van VM2
10.20.10.4:443       -> HTTPS-dienst achter VM2
```

Een regel naar de routertag geeft niet automatisch toegang tot het subnet. Een regel
naar het subnet maakt de managementinterface van VM2 op zijn Tailscale-IP niet
automatisch bereikbaar.

### 14.3 Een route is wel zichtbaar zonder toegangsrecht

Access control beperkt bruikbare verbindingen, maar is niet hetzelfde als
routeontdekking. Een client kan weten dat een route bestaat terwijl een concrete flow
toch wordt geblokkeerd.

Dat is geen fout. Het toont de scheiding tussen:

| Controlestap | Vraag |
|---|---|
| route-injectie | langs welke gateway gaat dit prefix? |
| packet filtering | mag deze bron deze bestemming bereiken? |
| servicecontrole | luistert de applicatie en accepteert ze de request? |

### 14.4 Negatieve routed tests

| Test | Verwacht | Wat bewijst dit? |
|---|---|---|
| `curl -kI https://10.20.10.4` | werkt | route, TCP/443-policy en webdienst werken |
| `nc -vz 10.20.10.4 22` | faalt | NetBox-managementpoort is niet toegestaan |
| `nc -vz 10.20.10.4 80` | faalt tenzij bewust nodig | alleen HTTPS is toegelaten |
| `nc -vz 10.20.0.1 22` | faalt | DNS-server wordt geen algemeen beheerdoel |

Een gefaalde `nc`-test bewijst niet op zichzelf dat de ACL blokkeerde. De poort kan ook
gesloten zijn of een hostfirewall kan weigeren. Combineer runtimegedrag met de
policy preview, policytests en eventueel logs.

Kernzin:

> Een subnet router ontsluit een route; access policy begrenst welke diensten langs die
> route werkelijk bruikbaar zijn.

---

## 15. MagicDNS en Split DNS

### 15.1 MagicDNS

MagicDNS registreert namen voor devices in de tailnet. Als VM1 de machinenaam
`s01-ch6-web-01` heeft, kan een client die naam gebruiken in plaats van het
Tailscale-IP.

```text
curl http://s01-ch6-web-01
```

MagicDNS maakt van elke interne bedrijfsnaam geen record. Het kent in de eerste plaats
de namen van tailnet-devices.

### 15.2 Split DNS

Split DNS stuurt vragen voor een gekozen DNS-zone naar een specifieke resolver. Andere
DNS-vragen blijven naar hun gewone resolver gaan.

In het lab:

| Onderdeel | Waarde |
|---|---|
| restricted zone | `voltlab.lan` |
| interne resolver | `10.20.0.1` |
| record | `netbox.voltlab.lan` |
| antwoord | `10.20.10.4` |

Conceptueel:

```text
query netbox.voltlab.lan -> interne DNS 10.20.0.1
query www.example.com    -> gewone/global resolver
```

### 15.3 DNS heeft zelf een netwerkpad nodig

De DNS-configuratie zegt welke resolver een zone moet beantwoorden. Ze creëert geen
route en geen access-controltoelating naar die resolver.

Voor UDP/53:

```json
{
  "action": "accept",
  "src": ["autogroup:member"],
  "proto": "udp",
  "dst": ["10.20.0.1:53"]
}
```

Voeg TCP/53 alleen toe wanneer je requirements of tests aantonen dat dit nodig is.

De volledige afhankelijkheidsketen is:

```text
DNS-client accepteert Tailscale DNS-instellingen
        |
restricted zone wijst naar 10.20.0.1
        |
route naar 10.20.0.1 bestaat via VM2
        |
policy laat DNS toe
        |
resolver accepteert query en kent record
```

### 15.4 Waarom eerst via IP testen?

Test de afhankelijkheden in lagen:

```text
1. curl -kI https://10.20.10.4
2. nslookup netbox.voltlab.lan
3. curl -kI https://netbox.voltlab.lan
4. los een publieke naam op
```

| Test | Wat is bewezen als hij slaagt? |
|---|---|
| HTTPS via IP | route, access policy en service werken |
| `nslookup` intern record | Split DNS en resolverpad werken |
| HTTPS via naam | DNS-antwoord wordt in applicatieflow gebruikt |
| publieke DNS-query | andere zones blijven bruikbaar |

Als stap 1 al faalt, heeft wijzigen van DNS-records weinig zin. Als stap 1 werkt en stap
2 faalt, zoek je eerst in DNS-configuratie, UDP/TCP/53-policy en resolverbereikbaarheid.

### 15.5 MagicDNS en Split DNS vergelijken

| Vraag | MagicDNS | Split DNS |
|---|---|---|
| Welke namen? | tailnet-devices | records in gekozen interne zones |
| Voorbeeld | `s01-ch6-web-01` | `netbox.voltlab.lan` |
| Externe resolver nodig? | niet voor normale tailnetdevicenamen | ja, bijvoorbeeld `10.20.0.1` |
| Routed access nodig? | niet voor directe tailnetdevices | wel als resolver achter subnet router staat |
| Belangrijkste fout | verkeerde machinenaam of DNS-instellingen niet geaccepteerd | route, ACL, resolver of zoneconfiguratie fout |

Kernzin:

> MagicDNS benoemt tailnet-devices; Split DNS stuurt geselecteerde DNS-zones naar een
> passende resolver.

---

## 16. Exit nodes

### 16.1 Verschil met een subnet router

Een exit node stuurt internetverkeer van een client via een tailnet-device naar buiten.
Een subnet router stuurt verkeer naar specifieke achterliggende private prefixen.

| Eigenschap | Subnet router | Exit node |
|---|---|---|
| Doel | intern subnet bereikbaar maken | internet/default route via andere locatie |
| Typische routes | `10.20.0.0/16` | `0.0.0.0/0` en `::/0` |
| Selectie door client | subnetroute wordt gebruikt volgens routing | client kiest exit node |
| Hoofdtest | interne host/service werkt | publiek bron-IP verandert |
| Belangrijk risico | te brede interne ontsluiting | privacy, capaciteit en egresscontrole |

NetBox heeft geen exit node nodig. De route naar `10.20.0.0/16` via VM2 volstaat.

### 16.2 Policy voor internet via exit nodes

Toegang tot `autogroup:internet` bepaalt of een bron internet via exit nodes mag
gebruiken.

Conceptueel grant-voorbeeld:

```json
{
  "src": ["group:travelers"],
  "dst": ["autogroup:internet"],
  "ip": ["*"]
}
```

Die toestemming betekent niet dat de client automatisch een exit node selecteert. De
node moet aangeboden en goedgekeurd zijn, de policy moet internettoegang toelaten en de
client moet de exit node kiezen.

### 16.3 Beperkingen en productievraagstukken

Netwerkpolicy kan bepalen wie exit-nodefunctionaliteit mag gebruiken, maar is niet
bedoeld als selectie van precies één specifieke exit node per user. Ontwerp dus niet op
de onjuiste aanname dat een gewone ACL de keuze tussen individuele exit nodes volledig
afdwingt.

| Productievraag | Waarom belangrijk? |
|---|---|
| wie mag een exit node aanbieden? | voorkomt ongecontroleerde egresspunten |
| wie mag `autogroup:internet` bereiken? | beperkt full-tunnelgebruik |
| is gebruik verplicht of optioneel? | bepaalt gedrag buiten beheerde netwerken |
| wat gebeurt bij uitval? | exit node is datapadafhankelijkheid |
| welke capaciteit is nodig? | al het clientinternet kan erdoor lopen |
| welke metadata wordt gelogd? | gebruikers moeten privacy-impact kennen |
| mag lokaal LAN bereikbaar blijven? | bepaalt risico van gelijktijdige lokale toegang |

Kernzin:

> Een exit node verandert het internet-egresspad; een subnet router ontsluit specifieke
> private routes.

---

## 17. Meerdere controlelagen

Een werkende flow is het resultaat van meerdere onafhankelijke lagen.

```text
identity en device
        |
        v
route of direct peerpad
        |
        v
tailnet access policy
        |
        v
subnet router / hostfirewall
        |
        v
luisterende service
        |
        v
applicatieauthenticatie en -autorisatie
```

### 17.1 Welke laag beantwoordt welke vraag?

| Laag | Vraag | Voorbeeldcontrole |
|---|---|---|
| identity | wie of welke rol is de bron? | user, group, tags controleren |
| routing | waarheen gaat het pakket? | routing table en route approval |
| tailnetpolicy | is deze netwerkflow toegestaan? | preview, tests en runtimeverbinding |
| router/hostfirewall | wordt het pakket verder aanvaard? | firewall- en counters/logs |
| service | luistert het proces? | `ss`, `curl` of protocolclient |
| applicatie | mag de aangemelde gebruiker de actie doen? | applicatiegerichte allow/deny-test |

Een Tailscale ACL vervangt dus geen autorisatie binnen NetBox. TCP/443 bereikbaar maken
betekent alleen dat de HTTPS-service bereikbaar is. NetBox bepaalt nog altijd wie mag
inloggen en welke objecten die persoon mag beheren.

### 17.2 Foutscenario's correct lokaliseren

| Symptoom | Mogelijke laag | Eerste gerichte controle |
|---|---|---|
| Tailscale-IP van VM1 onbereikbaar | peerstatus of policy | `tailscale status` en policy preview |
| VM1 pingt, maar HTTP faalt | ACL, hostfirewall of webservice | TCP/80-policy en luisterende socket |
| route zichtbaar, NetBox faalt | ACL, forwarding, firewall of return path | test vanaf VM2 en controleer policy |
| HTTPS via IP werkt, via naam niet | DNS | restricted zone en query naar resolver |
| TCP/22 bereikbaar, SSH-login faalt | SSH-policy of lokale user | `ssh`-regel en bestaande OS-user |
| user kan openen maar niet beheren | applicatieautorisatie | rol of rechten in de applicatie |

Typische fout:

> Bij elk probleem tijdelijk `*:*` toelaten.

Dat maakt de diagnose minder betrouwbaar. Wijzig één hypothese tegelijk en behoud
negatieve controles.

---

## 18. Device lifecycle, audit en privacy

### 18.1 Lifecyclefasen

Een node blijft niet automatisch terecht in de tailnet staan.

| Fase | Beheeractie | Bewijs |
|---|---|---|
| aanvraag | doel, eigenaar en vereiste flows vastleggen | ticket of labplan |
| onboarding | identity, naam, tags en keytype kiezen | correcte device-inventaris |
| gebruik | policy en routes toepassen | allow- en deny-tests |
| review | noodzaak, last seen en rechten controleren | reviewdatum en conclusie |
| incident | key intrekken of device isoleren | toegang stopt en actie is traceerbaar |
| offboarding | node, routes en tijdelijke policy verwijderen | negatieve hertest en opgeschoonde inventaris |

Een auth key intrekken is niet hetzelfde als de al geregistreerde node verwijderen. Een
route uitschakelen is niet hetzelfde als de bijbehorende allow-regel verwijderen. Goed
offboarden controleert alle gekoppelde objecten.

### 18.2 Configuratie-auditlogs

Configuratie-auditlogs registreren wijzigingen aan de tailnetconfiguratie. Ze helpen
vragen beantwoorden zoals:

| Vraag | Mogelijk event |
|---|---|
| Wie wijzigde de policy? | update van tailnet policy file met diff |
| Wie keurde een route goed? | device- of routewijziging |
| Wanneer veranderde DNS? | update van DNS-configuratie |
| Wie wijzigde tags? | update van device-tags |
| Wanneer werd een key aangemaakt of ingetrokken? | keybeheer-event |

Configuratielogs tonen wie wat wanneer wijzigde. Ze tonen niet automatisch de inhoud
van elke netwerkverbinding.

### 18.3 Netwerkflowlogs

Netwerkflowlogs zijn een afzonderlijke functie. Ze beschrijven verkeersflows en niet
de payload. Beschikbaarheid en bewaartermijn kunnen van het abonnement afhangen.

Belangrijke nuance:

> Een geblokkeerde verbindingspoging verschijnt niet noodzakelijk als flowlog. Gebruik
> dus geen afwezige logregel als enig bewijs dat access control correct blokkeerde.

Combineer waar nodig:

| Bewijsbron | Sterkte |
|---|---|
| policytest | verwachte beslissing door policy-engine |
| runtime negatieve test | werkelijk clientgedrag |
| host- of firewalllog | plaats waar een pakket werd geweigerd of ontvangen |
| configuratie-auditlog | wie de beleidsconfiguratie wijzigde |
| netwerkflowlog | succesvolle verkeersflow en metadata, indien beschikbaar |

### 18.4 Privacy en secretbeheer

VPN- en flowmetadata kunnen informatie geven over gebruikers, devices, tijden en
diensten. Verzamel alleen wat nodig is, bepaal wie logs mag lezen en leg bewaartermijnen
vast.

| Wel opnemen in een labverslag | Niet opnemen |
|---|---|
| herkenbare devicenaam | auth key |
| tag en functionele rol | API-token |
| relevante Tailscale- of lab-IP's | loginlink of recovery code |
| geschoond policyfragment | wachtwoord of private key |
| verwacht en werkelijk testresultaat | volledige gevoelige terminalhistory |
| tijdstip van test | onnodige persoonsgegevens van andere users |

Als een secret toch zichtbaar werd, is blurren in één screenshot onvoldoende. Trek de
secret in of roteer hem en controleer waar hij nog gekopieerd staat.

Kernzin:

> Auditability vraagt voldoende bewijs om beslissingen te reconstrueren, zonder meer
> credentials of persoonsgegevens te verzamelen dan nodig.

---

## 19. Praktische testmethodiek

### 19.1 Eerst een baseline

Meet de beginsituatie voordat je policy wijzigt.

| Baseline | Waarom noteren? |
|---|---|
| devices en identities | toont welke nodes werkelijk deelnemen |
| Tailscale-IP's | koppelt tests aan correcte endpoints |
| VM1- en VM2-lab-IP | onderscheidt overlaypad en lokaal pad |
| bestaande policy | voorkomt dat een oude brede allow de resultaten beïnvloedt |
| route- en DNS-status | maakt latere wijzigingen vergelijkbaar |
| luisterende diensten op eigen VM's | voorkomt foutieve conclusie over ACL-deny |

### 19.2 Test van laag naar gebruikersflow

Gebruik een vaste volgorde:

1. Controleer identity, namen en tags.
2. Controleer of peers online zijn.
3. Test directe HTTP-toegang naar VM1.
4. Test onnodige VM1-poorten.
5. Configureer en test Tailscale SSH met beide policylagen.
6. Controleer forwarding en routeadvertentie op VM2.
7. Keur de route goed en controleer routeacceptatie op de client.
8. Test NetBox eerst via IP en TCP/443.
9. Test ongewenste routed poorten en andere interne doelen.
10. Configureer en test Split DNS.
11. Test de gebruikersflow via hostname.
12. Controleer policytests, auditlogs en cleanup.

### 19.3 Testmatrix

| ID | Bron | Doel | Test | Verwacht | Bewijst vooral |
|---|---|---|---|---|---|
| T1 | laptop | VM1 | HTTP TCP/80 | allow | directe device access |
| T2 | laptop | VM1 | HTTPS TCP/443 | deny | poortscope webserver |
| T3 | laptop | VM1 | Tailscale SSH als `debian` | allow na beide policyregels | netwerk- en SSH-policy |
| T4 | laptop | VM1 | Tailscale SSH als `root` | deny | lokale userscope |
| T5 | laptop | NetBox | HTTPS TCP/443 | allow | routed service access |
| T6 | laptop | NetBox | SSH TCP/22 | deny | routed least privilege |
| T7 | laptop | DNS-server | DNS UDP/53 | allow | resolverpad |
| T8 | laptop | DNS-server | SSH TCP/22 | deny | DNS-host niet breed open |
| T9 | laptop | DNS | `netbox.voltlab.lan` | `10.20.10.4` | Split DNS |
| T10 | laptop | publiek DNS | publieke naam | correct antwoord | split blijft beperkt tot zone |

### 19.4 Wat noteer je per test?

```text
Test-ID: T6
Bronidentity: <student-login-email>
Brondevice: <laptop-name>
Bestemming: 10.20.10.4
Protocol/poort: TCP/22
Verwachting: deny
Werkelijk: timeout / refused / policymelding
Aanvullend bewijs: policytest deny + relevante policyregel
Conclusie: geen allow voor NetBox-managementpoort
```

Maak onderscheid tussen mogelijke foutuitkomsten:

| Uitkomst | Mogelijke betekenis |
|---|---|
| timeout | filtering, routeprobleem of stil doel |
| connection refused | host bereikbaar, maar niets luistert of firewall reject |
| name not resolved | DNS-probleem vóór de verbinding |
| TLS-fout | TCP/443 werkt mogelijk, maar certificaat of hostname faalt |
| applicatie-403 | netwerk en HTTP werken, applicatie weigert autorisatie |

Een negatieve test is sterk wanneer je zowel het verwachte blokkeermechanisme als het
waargenomen resultaat kan aanwijzen.

### 19.5 Veilig testen

Gebruik alleen afgesproken doelen en poorten. Een brede scan van het volledige
`10.20.0.0/16` is niet nodig om least privilege aan te tonen en valt buiten het
labdoel.

Voorbeeld van voldoende bewijs:

- één toegelaten HTTPS-flow naar NetBox;
- enkele vooraf bepaalde geweigerde poorten;
- één DNS-flow naar de resolver;
- policytests voor de verwachte grenzen.

Kernzin:

> Test gericht genoeg om je ontwerp te bewijzen, niet breed genoeg om onnodig andere
> systemen te onderzoeken.

---

## 20. Troubleshooting zonder policy te verbreden

### 20.1 Een hypothese per stap

Gebruik bij een fout deze vragen:

1. Is de bronidentiteit wat ik denk dat ze is?
2. Selecteert de policy het juiste doel?
3. Bestaat het directe peerpad of de subnetroute?
4. Laat de policy het juiste protocol en de juiste poort toe?
5. Forwardt de router het pakket?
6. Kan de router de bestemming zelf bereiken?
7. Komt antwoordverkeer terug?
8. Luistert de dienst?
9. Is DNS pas daarna correct?

### 20.2 Gerichte commando's

| Doel | Mogelijke controle | Interpretatie |
|---|---|---|
| device-overzicht | `tailscale status` | peers, namen en toestand |
| eigen overlay-IP | `tailscale ip -4` | juiste bron- of doelcontext |
| Tailscale-pad | `tailscale ping <device>` | directe of relayconnectiviteit onderzoeken |
| gewone IP-route | OS-routing table | gekozen gateway voor intern prefix |
| poorttest | `nc -vz <ip> <poort>` | TCP-connectiviteit, geen applicatieautorisatie |
| HTTP-test | `curl -I http://<doel>` | HTTP-response en headers |
| HTTPS-test lab | `curl -kI https://<doel>` | service werkt ondanks labcertificaatcontrole |
| DNS-test | `nslookup` of `dig` | resolver en antwoord |
| luisterende poort eigen VM | `ss -lntup` | proces en socket op doelhost |

`tailscale ping --tsmp` kan het Tailscale-netwerkpad onderzoeken vóór de gewone
access-controlcheck. Een gewone applicatie- of ICMP-test onderzoekt een ander deel van
de keten. Kies het commando volgens de hypothese.

### 20.3 Veelzeggende foutcombinaties

| Observatie | Waarschijnlijke richting |
|---|---|
| Tailscale-peer zichtbaar, TCP/80 faalt | policy, hostfirewall of webservice |
| NetBox werkt vanaf VM2 maar niet vanaf laptop | routeacceptatie, tailnetpolicy of forwarding |
| NetBox via IP werkt, DNS-server niet bereikbaar | aparte DNS-ACL of routeprobleem |
| DNS-query werkt, HTTPS via naam geeft TLS-fout | certificaatnaam of trust, niet routing |
| TCP/22 werkt, Tailscale SSH als `root` faalt | SSH-userpolicy doet mogelijk correct haar werk |
| policytest slaagt, runtime faalt | probleem buiten de policy-engine |

Typische fout:

> Meerdere instellingen tegelijk wijzigen en daarna niet weten welke wijziging het
> resultaat veroorzaakte.

Betere aanpak:

> Leg een hypothese vast, verander één relevante variabele, herhaal dezelfde test en
> herstel tijdelijke wijzigingen.

---

## 21. Labkeuzes en productieontwerp

Het lab is klein genoeg om individueel te beheren. Productie vraagt extra governance,
beschikbaarheid en automatisatie.

| Thema | Labkeuze | Productieontwerp |
|---|---|---|
| tailnetrollen | student is member en admin | gescheiden owner-, admin-, auditor- en userrollen |
| bronselector | `autogroup:member` | functiegerichte groups en eventueel posture |
| tag owners | `autogroup:admin` | beperkte beheergroep of provisioningidentity |
| policy-syntaxis | ACL's voor bestaand lesmateriaal | grants beoordelen voor nieuwe policy |
| auth key | korte one-off key handmatig aangemaakt | secret store, OAuth-gebaseerde uitgifte of gecontroleerde automatisatie |
| routeapproval | handmatig in console | `autoApprovers` met strikte identity en change control |
| subnet router | één VM2 | redundante routers, monitoring en capaciteitsplanning |
| forwarding | runtime-`sysctl` | persistent configuratiebeheer |
| SNAT | standaard om labrouting eenvoudig te houden | bewuste keuze met logging en return routing |
| DNS | één restricted nameserver | redundante resolvers en gemonitorde zones |
| HTTPS | `curl -k` accepteert labcertificaat | geldige trust chain en hostnamevalidatie |
| policybeheer | webeditor | peer review, version control, tests en audittrail |
| logging | labbewijs en configuratielog | SIEM, bewaarbeleid en toegangscontrole |
| cleanup | na de workshop | geautomatiseerde lifecycle en periodieke review |

### 21.1 Beschikbaarheid

VM2 is in het lab een single point of failure. Als VM2 uitvalt, verdwijnen routed
access en de DNS-route naar `10.20.0.1` tegelijk.

Productievragen:

| Vraag | Waarom nodig? |
|---|---|
| zijn er twee subnet routers? | voorkomt één enkel datapad |
| adverteren ze exact dezelfde bedoelde routes? | failover moet voorspelbaar zijn |
| accepteren routers onnodig elkaars routes? | voorkomt omwegen of routingloops |
| wordt de einddienst gemonitord? | online router bewijst geen werkende applicatie |
| is DNS redundant? | naamresolutie mag geen apart single point of failure zijn |

### 21.2 Change management

Een policywijziging kan tegelijk veel devices beïnvloeden. Behandel ze daarom zoals
code:

```text
behoefte documenteren
-> kleine wijziging
-> policytests
-> review
-> gecontroleerde uitrol
-> runtimevalidatie
-> audit en rollbackmogelijkheid
```

Kernzin:

> De workshop toont de toegangslogica; productie voegt rolenscheiding, automatisatie,
> beschikbaarheid, monitoring en change control toe.

---

## 22. Typische fouten en betere aanpakken

| Fout | Gevolg | Betere aanpak |
|---|---|---|
| dezelfde tailnet als trustbewijs | laterale beweging wordt te gemakkelijk | expliciete flows per rol en dienst |
| veronderstellen dat lege policy altijd deny betekent | standaard allow-all kan actief blijven | effectieve volledige policy controleren |
| alleen `curl` als bewijs | overmatige toegang blijft onzichtbaar | positieve en negatieve testmatrix |
| `*:*` tijdelijk toevoegen | fijnere regels verliezen betekenis | één laag per hypothese onderzoeken |
| server user-owned laten | rol hangt aan persoon | tag-based identity voor niet-menselijke node |
| tag als gewoon label zien | privilege-escalatie via tag wordt gemist | tag owners als securitygrens behandelen |
| extra tag zou rechten beperken | andere tagregels kunnen extra toegang geven | totaaleffect van alle tags testen |
| reusable key in script | meerdere ongewenste nodes mogelijk | one-off of dynamisch uitgegeven key in secret store |
| auth key expiry gelijkstellen aan deviceverwijdering | bestaande node blijft actief | device lifecycle afzonderlijk beheren |
| routeapproval gelijkstellen aan access | subnet wordt conceptueel te breed behandeld | route en flowpolicy apart testen |
| volledige `/16` op alle poorten toelaten | onnodige interne diensten bereikbaar | host- en servicespecifieke allow |
| alleen UDP/53 toestaan zonder vereisten te testen | sommige DNS-antwoorden kunnen falen | protocolbehoefte meten en apart testen |
| DNS als eerste testen | routing- en DNS-fouten lopen door elkaar | eerst HTTPS via IP, dan DNS, dan hostname |
| Tailscale SSH als poortloos zien | SSH faalt ondanks `ssh`-regel | ook TCP/22 in netwerkpolicy toelaten |
| `nc` gebruiken als bewijs van SSH-loginrecht | alleen transport wordt onderzocht | Tailscale SSH-user allow/deny uitvoeren |
| Tailscale ACL als bescherming voor lokaal LAN-verkeer zien | lokaal pad omzeilt tailnetpolicy | host- en netwerkfirewalls behouden |
| flowlog zonder event als deny-bewijs zien | geblokkeerde pogingen kunnen ontbreken | policytest en runtimebewijs combineren |
| `curl -k` als productiecontrole gebruiken | certificaatfouten worden genegeerd | geldige TLS-validatie uitvoeren |
| cleanup overslaan | oude nodes, keys en routes blijven bestaan | eindcontrole met offboardingbewijs |

Gebruik de tabel niet alleen als checklist. Classificeer een fout eerst:

- identity- of ownershipprobleem;
- policy- of selectorsprobleem;
- route- of forwardingprobleem;
- DNS-probleem;
- service- of hostfirewallprobleem;
- lifecycle- of auditprobleem.

Die classificatie voorkomt willekeurige wijzigingen.

---

## 23. Controlevragen en denkvragen

### 23.1 Begripscontrole

1. Waarom bewijst een bestaande route geen toegangsrecht?
2. Wanneer geldt deny by omission en welke standaardpolicyvalkuil moet je kennen?
3. Wat is het verschil tussen een user-owned en een tagged device?
4. Waarom is `tagOwners` een securitycontrole?
5. Waarom kan een extra tag ook extra toegang geven?
6. Wat is het verschil tussen auth key expiry en device-key expiry?
7. Waarom heeft een Tailscale SSH-sessie zowel netwerkpolicy als SSH-policy nodig?
8. Wat is het verschil tussen MagicDNS en Split DNS?
9. Wat verandert SNAT aan wat een interne host als bron ziet?
10. Waarom is een exit node geen vervanging voor een subnet router?

### 23.2 Toepassingsvragen

1. Een student mag NetBox op HTTPS openen, maar geen enkel ander labdoel bereiken.
   Welke route, ACL en negatieve tests heb je nodig?
2. VM1 heeft `tag:webserver` en `tag:ssh-server`. Welke onverwachte toegang kan ontstaan
   als een van beide tags in een brede regel voorkomt?
3. Een policytest voor `10.20.10.4:443` slaagt, maar `curl` faalt. Welke lagen onderzoek
   je vervolgens en in welke volgorde?
4. `nslookup netbox.voltlab.lan` faalt, terwijl HTTPS via IP werkt. Welke vier controles
   voer je uit?
5. TCP/22 naar VM1 is bereikbaar, maar aanmelden als `root` faalt. Waarom kan dat exact
   het gewenste resultaat zijn?
6. Een reusable tagged auth key lekt. Welke acties voer je uit naast het verwijderen van
   de key uit het document?
7. VM2 wordt verwijderd. Welke policy-, route-, DNS- en inventarisobjecten controleer je
   tijdens cleanup?
8. Waarom is `autogroup:member` in een persoonlijke tailnet verdedigbaar maar mogelijk te
   breed in een organisatie?

### 23.3 Criteria voor een sterk antwoord

Een sterk antwoord:

- benoemt de bronidentiteit en het brondevice;
- onderscheidt direct device access van routed access;
- specificeert protocol en poort;
- scheidt route, policy, service en applicatieautorisatie;
- bevat minstens één positieve en één relevante negatieve test;
- benoemt een labvereenvoudiging en een productieverbetering;
- houdt rekening met lifecycle en secretbeheer;
- trekt geen conclusie die de gebruikte test niet kan bewijzen.

---

## 24. Samenvatting

Belangrijkste inzichten:

- VPN-connectiviteit is een datapad, geen blanco toegangsrecht;
- dezelfde tailnet betekent niet dezelfde trust of dezelfde rechten;
- een expliciete access policy volgt deny by default, maar een nooit aangepaste tailnet
  kan een standaard allow-all-policy hebben;
- ACL's blijven ondersteund, terwijl grants de aanbevolen syntaxis voor nieuwe policy's
  zijn;
- users en groups passen bij menselijke identities;
- tags geven niet-menselijke devices een rolidentiteit en vervangen user ownership;
- tag owners bepalen wie een device in een securityrol kan plaatsen;
- meerdere tags kunnen rechten optellen en moeten als geheel beoordeeld worden;
- auth keys maken headless onboarding mogelijk maar blijven gevoelige credentials;
- auth key expiry verwijdert een geregistreerd device niet;
- ACL's beschrijven bron, bestemming, protocol en poort;
- directionele policy laat antwoordverkeer van een toegelaten sessie terugkeren;
- policytests beschermen verwachte allow- en denybeslissingen tegen regressie;
- runtime-tests blijven nodig voor route, firewall, DNS en service;
- Tailscale SSH gebruikt TCP/22 én een afzonderlijke SSH-policy;
- een subnet router vraagt forwarding, routeadvertentie, goedkeuring, clientacceptatie,
  policy en een werkend return path;
- een breed routeprefix hoeft niet tot brede netwerktoegang te leiden;
- Split DNS heeft zelf route en policy naar de interne resolver nodig;
- een exit node routeert internetverkeer en is iets anders dan een subnet router;
- configuratie-auditlogs, netwerkflowlogs en runtimebewijs beantwoorden verschillende
  vragen;
- cleanup is een volwaardige fase van het toegangsontwerp.

Rode draad:

```text
identity -> device of tag -> route -> access policy
         -> servicepolicy -> positieve test -> negatieve test
         -> audit -> review -> cleanup
```

Kernzin:

> Professionele routed VPN-toegang is identity-aware, expliciet begrensd, gelaagd
> getest en gedurende de volledige lifecycle intrekbaar.
