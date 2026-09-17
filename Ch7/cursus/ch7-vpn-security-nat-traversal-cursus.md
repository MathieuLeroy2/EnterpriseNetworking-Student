# Hoofdstuk 7 - VPN security, NAT traversal en zichtbaarheid

## 1. Inleiding

In hoofdstuk 5 gebruikte je Tailscale om een private verbinding op te zetten. In hoofdstuk 6 leerde je die toegang professioneel beperken met tags, ACL's, subnet routing, Split DNS, Tailscale SSH en audit.

In dit hoofdstuk kijken we onder de motorkap.

De centrale vraag is niet meer alleen:

> Wie mag naar welke service?

De centrale vraag wordt:

> Waarom kan een VPN veilig werken op een netwerk dat je niet vertrouwt?

Dat lijkt op het eerste gezicht vreemd. Je laptop zit misschien op een hotelnetwerk, een luchthavenwifi, een thuisnetwerk van iemand anders, een mobiel netwerk met carrier-grade NAT of een bedrijfsnetwerk met strenge firewallregels. Toch kan je via een VPN veilig met interne systemen communiceren.

Dat komt omdat een goede VPN niet vertrouwt op het netwerk ertussen. De security zit niet in de wifi, de provider of de router onderweg. De security zit in cryptografie, authenticatie, sleutels, policy en correcte endpointcontrole.

Dit hoofdstuk gaat daarom dieper in op:

- waarom een VPN "beveiligd" kan zijn;
- wat encryptie, integriteit en authenticatie betekenen;
- waarom metadata niet hetzelfde is als inhoud;
- hoe NAT en stateful firewalls verkeer doorlaten of blokkeren;
- hoe NAT traversal probeert directe verbindingen mogelijk te maken;
- waarom DERP of andere relays nodig kunnen zijn;
- wat een netwerkbeheerder onderweg wel en niet kan zien;
- waarom port forwarding of expliciete UDP-toegang hogere snelheden kan geven;
- welke ontwerpkeuzes je als enterprise network engineer moet kunnen uitleggen.

Dit hoofdstuk combineert theorie met een meetgerichte Tailscale-workshop. In die workshop blijft een Debian-server in het Devbit-netwerk staan, terwijl de laptop achtereenvolgens via Devbit en eduroam of campusroam test. Zonder router- of switchconfiguratie onderzoek je met `tailscale netcheck`, `tailscale ping`, `tailscale status` en packet captures hoe NAT traversal, directe verbindingen, DERP, zichtbaarheid en performance zich in de praktijk gedragen. Je hoeft niet elk cryptografisch detail wiskundig te kunnen bewijzen. Je moet wel kunnen uitleggen welke bescherming een VPN biedt, welke bescherming niet, en hoe firewalls en NAT bepalen of een verbinding direct of via relay loopt.

Doorheen het hoofdstuk gebruiken we dezelfde redeneringsketen:

```text
bescherming -> bereikbaarheid -> gekozen pad -> zichtbaarheid -> meetbewijs
```

| Vraag | Wat moet je uiteindelijk kunnen aantonen? |
|---|---|
| Welke bescherming biedt de tunnel? | De buitenste capture toont versleuteld transport; de applicatie-inhoud is alleen aan de binnenkant zichtbaar. |
| Waarom kunnen de peers elkaar bereiken? | NAT- en firewallstate, endpoint discovery en eventueel port mapping maken een pad mogelijk. |
| Welk pad wordt werkelijk gebruikt? | `tailscale ping` en `tailscale status` tonen direct, peer relay of DERP. |
| Wie ziet welke informatie? | Een zichtbaarheidstabel onderscheidt inhoud, netwerkmetadata en beheerinformatie. |
| Is het ontwerp aanvaardbaar? | Een positieve én negatieve test ondersteunen de security- en performancekeuze. |

Deze volgorde is belangrijk. Dat een webpagina opent, bewijst alleen dat er
connectiviteit is. Het bewijst nog niet dat het pad direct is, dat ongewenste toegang
geblokkeerd wordt of dat je privacyverwachting klopt.

Belangrijke gedachte:

> Een VPN is niet veilig omdat het netwerk onderweg betrouwbaar is. Een VPN is veilig omdat het ontwerp ervan uitgaat dat het netwerk onderweg onbetrouwbaar is.

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. uitleggen waarom een VPN veilig kan werken op een onbekend of onveilig netwerk;
2. het verschil toelichten tussen encryptie, integriteit, authenticatie en autorisatie;
3. uitleggen waarom een aanvaller op hetzelfde wifi-netwerk de inhoud van VPN-verkeer normaal niet kan lezen;
4. beschrijven welke metadata zichtbaar kan blijven, ook wanneer de inhoud versleuteld is;
5. het verschil uitleggen tussen data plane en control plane;
6. uitleggen waarom moderne VPN's vaak UDP gebruiken;
7. NAT, PAT en stateful firewalls koppelen aan VPN-connectiviteit;
8. beschrijven wat een NAT mapping is;
9. uitleggen waarom inkomend verkeer zonder bestaande state meestal geblokkeerd wordt;
10. NAT traversal conceptueel uitleggen;
11. STUN, endpoint discovery, hole punching en port mapping op hoofdlijnen plaatsen;
12. uitleggen waarom sommige netwerken directe peer-to-peer VPN-verbindingen verhinderen;
13. DERP als encrypted relay verklaren;
14. het verschil tussen directe verbinding, peer relay en DERP relay uitleggen;
15. analyseren waarom directe verbindingen meestal sneller zijn dan relayed verbindingen;
16. uitleggen hoe port forwarding of UDP-openstelling performance kan verbeteren;
17. beschrijven wat een netwerkbeheerder op lokaal netwerk, firewall, ISP of relayniveau wel en niet kan zien;
18. privacyverwachtingen rond VPN correct nuanceren;
19. typische misverstanden over VPN-security herkennen;
20. ontwerpkeuzes formuleren voor enterprisegebruik van VPN, firewalls, logging en performance.

---

## 3. Wat betekent "beveiligd" bij een VPN?

### 3.1 Beveiligd is geen enkelvoudig begrip

Wanneer iemand zegt "de VPN is beveiligd", moet je vragen wat daarmee bedoeld wordt.

Beveiliging bestaat uit meerdere eigenschappen.

| Eigenschap | Vraag | Voorbeeld bij VPN |
|---|---|---|
| Vertrouwelijkheid | Kan iemand de inhoud lezen? | Een aanvaller op wifi ziet geen HTTP-request in klare tekst binnen de tunnel. |
| Integriteit | Kan iemand verkeer aanpassen zonder detectie? | Een aangepast pakket wordt verworpen. |
| Authenticatie | Weet ik met wie ik spreek? | De peer bewijst dat hij de juiste private key bezit. |
| Autorisatie | Mag deze peer deze service bereiken? | ACL's laten alleen HTTP naar een webserver toe. |
| Replaybescherming | Kan oud verkeer opnieuw afgespeeld worden? | Oude pakketten worden niet opnieuw als geldig aanvaard. |
| Forward secrecy | Blijft oud verkeer beschermd als later een sleutel lekt? | Sessiesleutels worden regelmatig vernieuwd. |

Een VPN kan sterk zijn op encryptie en toch zwak zijn op autorisatie. Dat zag je in Ch6 al:

```json
{
  "action": "accept",
  "src": ["*"],
  "dst": ["*:*"]
}
```

Die regel maakt het netwerk niet minder versleuteld, maar wel minder veilig. Iedereen mag dan naar alles. Encryptie beschermt de transportweg. Policy bepaalt wie welke toegang krijgt.

De eigenschappen vullen elkaar aan, maar zijn niet onderling uitwisselbaar.

| Ontbrekende eigenschap | Wat kan nog altijd fout lopen? | Geschikte controle |
|---|---|---|
| Vertrouwelijkheid | Een tussenpartij leest applicatie-inhoud. | Vergelijk een capture op de VPN-interface met een capture op de fysieke interface. |
| Integriteit | Gewijzigde pakketten zouden als geldig verwerkt kunnen worden. | Controleer protocolontwerp en foutlogs; een gewone ping kan dit niet bewijzen. |
| Authenticatie | Je bouwt mogelijk een tunnel met de verkeerde peer. | Controleer device-identiteit, keydistributie en registratie in de control plane. |
| Autorisatie | Een geldige peer bereikt te veel services. | Voer een allow-test en een deny-test uit met verschillende bronidentiteiten of poorten. |
| Replaybescherming | Eerder onderschepte pakketten zouden opnieuw effect kunnen hebben. | Controleer dat het gebruikte protocol replaybescherming biedt; dit is geen veilige manuele labtest. |
| Forward secrecy | Een later sleutelcompromis kan ouder bewaard verkeer in gevaar brengen. | Beoordeel het protocol en sleutelbeheer, niet alleen de huidige connectiviteit. |

Kernzin:

> Encryptie beschermt het verkeer onderweg. Autorisatie bepaalt of dat verkeer er überhaupt mag zijn.

### 3.2 Een VPN is geen magisch veilig netwerk

Een VPN maakt geen enkel device automatisch betrouwbaar.

Als een laptop malware bevat, helpt encryptie onderweg niet tegen wat die laptop zelf doet. Als een server slecht gepatcht is, maakt een VPN die server niet automatisch veilig. Als een ACL te breed is, kan een correct versleutelde tunnel nog altijd te veel toegang geven.

Een VPN lost dus vooral dit probleem op:

> Hoe communiceren twee endpoints veilig over een netwerk dat we niet vertrouwen?

Een VPN lost niet automatisch de volgende problemen op:

| Probleem buiten de tunnel | Gevolg | Aanvullende maatregel |
|---|---|---|
| Endpoint is besmet | Malware gebruikt de toegelaten tunnel vanaf een geldig device. | Endpointbeheer, EDR, patching en isolatie. |
| Gebruikersaccount is gecompromitteerd | Een aanvaller kan een nieuw of bestaand device misbruiken. | MFA, sessiebeheer en identity-monitoring. |
| Policy is te breed | Correct versleuteld verkeer bereikt te veel systemen. | Least privilege, tags, grants/ACL's en negatieve tests. |
| Serverapplicatie is kwetsbaar | De applicatie kan via een toegelaten netwerkpad worden aangevallen. | Patching, hardening en applicatiebeveiliging. |
| DNS is fout of manipuleerbaar | De gebruiker bereikt de verkeerde host of interne namen lekken. | Split DNS, beveiligde resolvers en DNS-controles. |
| Interne segmentatie ontbreekt | Eén toegelaten ingang geeft een te groot lateraal bereik. | Netwerksegmentatie en host firewalls. |
| Logging is afwezig of te breed | Incidenten blijven onzichtbaar of privacy wordt onnodig geschaad. | Doelgerichte audit- en flowlogs met retentiebeleid. |

**Kernidee:** een VPN is één beveiligingslaag. Endpointvertrouwen, identiteit,
autorisatie, segmentatie en auditing blijven afzonderlijke ontwerpvragen.

---

## 4. Het dreigingsmodel: onveilig netwerk

### 4.1 Wat kan fout lopen op onbekende wifi?

Stel dat je laptop verbonden is met wifi in een luchthaven.

Je kent niet:

- wie de access points beheert;
- wie nog op hetzelfde netwerk zit;
- of er client isolation actief is;
- of er logging gebeurt;
- of DNS gemanipuleerd wordt;
- of verkeer wordt geblokkeerd of omgeleid.

Mogelijke aanvallen en storingen:

| Aanval of risico | Wat gebeurt er? | Wat beperkt de VPN? | Wat blijft mogelijk of zichtbaar? |
|---|---|---|---|
| Passief afluisteren | Iemand bekijkt verkeer op hetzelfde netwerk. | De inhoud van VPN-pakketten blijft versleuteld. | Bron, buitenste bestemming, timing en volume blijven metadata. |
| Evil twin wifi | Een aanvaller maakt namaak-wifi met een vertrouwde naam. | De tunnel beschermt verkeer nadat de veilige peers geauthenticeerd zijn. | Captive-portalverkeer en beschikbaarheid blijven risicopunten. |
| DNS-manipulatie | Een lokale resolver geeft een fout IP-adres terug. | VPN-DNS of Split DNS kan interne queries aan de lokale resolver onttrekken. | Queries buiten de VPN kunnen nog gemanipuleerd of gelogd worden. |
| ARP spoofing | Een aanvaller probeert gatewayverkeer te onderscheppen. | VPN-inhoud blijft beschermd tegen lezen en ongemerkte wijziging. | De aanvaller kan pakketten nog droppen, vertragen of omleiden. |
| UDP-blokkering | Het netwerk laat direct VPN-UDP niet door. | Een relay kan de connectiviteit behouden. | Het pad wordt trager en relaygebruik wordt zichtbaar. |
| Captive portal | Eerst is webauthenticatie op het lokale netwerk nodig. | Na portaltoegang kan de VPN opnieuw bescherming bieden. | Voor de portal vrijgegeven verkeer valt niet automatisch onder de tunnel. |

De VPN gaat er niet vanuit dat het netwerk eerlijk is. Het netwerk mag pakketten bekijken, vertragen, droppen of omleiden. Wat het niet mag kunnen, is geldige versleutelde VPN-inhoud lezen of ongemerkt aanpassen.

### 4.2 Wat betekent "man-in-the-middle"?

Een man-in-the-middle zit logisch tussen twee endpoints.

```text
Laptop  ----  aanvaller/netwerk  ----  server
```

Zonder cryptografie kan de aanvaller mogelijk:

- inhoud lezen;
- inhoud aanpassen;
- sessies overnemen;
- verkeer naar een andere server sturen;
- credentials verzamelen.

Met een correct ontworpen VPN ziet de situatie er anders uit:

```text
Laptop == versleutelde tunnel == server
        over onbetrouwbaar netwerk
```

De aanvaller kan nog steeds:

- zien dat er verkeer is;
- IP-adressen of relaybestemmingen zien;
- timing en volume observeren;
- verkeer blokkeren;
- verbindingen verstoren.

De aanvaller kan normaal niet:

- de originele pakketinhoud lezen;
- TCP/HTTP/SSH-inhoud binnen de tunnel aanpassen;
- zich voordoen als peer zonder juiste sleutel;
- oude pakketten zomaar opnieuw geldig maken.

Belangrijke nuance:

> VPN beschermt tegen meelezen en manipuleren, maar niet tegen alle vormen van metadata-analyse of beschikbaarheidsaanvallen.

**Controleer:** formuleer bij elk dreigingsscenario afzonderlijk wat de aanvaller kan
lezen, afleiden, wijzigen en blokkeren. Het woord "veilig" zonder die vier vragen is te
vaag voor een professioneel ontwerp.

---

## 5. Encryptie, integriteit en authenticatie

### 5.1 Encryptie

Encryptie maakt inhoud onleesbaar voor wie de sleutel niet heeft.

Zonder VPN:

```text
GET /admin HTTP/1.1
Host: internal.example
Cookie: session=...
```

Met VPN ziet iemand onderweg alleen versleutelde VPN-pakketten. De HTTP-request of SSH-sessie zit binnen de tunnel.

Encryptie beantwoordt de vraag:

> Kan iemand de inhoud lezen?

### 5.2 Integriteit

Integriteit betekent dat een ontvanger kan controleren of een pakket onderweg gewijzigd werd.

Zonder integriteitsbescherming zou een aanvaller theoretisch bits kunnen aanpassen. Bij moderne VPN-protocollen worden pakketten cryptografisch geauthenticeerd. Als iemand een pakket wijzigt, klopt de authenticator niet meer en wordt het pakket verworpen.

Integriteit beantwoordt de vraag:

> Kan iemand de inhoud wijzigen zonder dat we het merken?

### 5.3 Authenticatie

Authenticatie betekent dat peers bewijzen wie ze zijn.

Bij moderne VPN's gebeurt dat vaak met publieke en private sleutels.

Conceptueel:

| Sleuteltype | Betekenis |
|---|---|
| Private key | Geheim op het device. Mag niet gedeeld worden. |
| Public key | Mag gedeeld worden. Wordt gebruikt om de peer te herkennen. |

Een peer bewijst niet door zijn private key te tonen, maar door cryptografisch te bewijzen dat hij die bezit.

Authenticatie beantwoordt de vraag:

> Spreek ik met de juiste peer?

### 5.4 Autorisatie

Autorisatie komt pas daarna.

Zelfs als een peer echt is, mag hij niet automatisch alles bereiken.

Voorbeeld:

| Peer | Geauthenticeerd? | Mag naar NetBox? |
|---|---|---|
| Laptop van student | ja | misschien alleen HTTPS |
| Partnerdevice | ja | alleen partnerportaal |
| Adminlaptop | ja | meer toegang, eventueel met MFA |
| Oude test-VM | ja of ooit ja | liever geen toegang meer |

Autorisatie beantwoordt de vraag:

> Welke acties mag deze geauthenticeerde identiteit uitvoeren?

Dit is waarom Ch6 zo sterk focuste op policy. Een cryptografisch sterke tunnel met zwakke autorisatie is nog steeds een risico.

### 5.5 De vier eigenschappen in één pakketstroom

Stel dat een student vanaf een beheerlaptop `https://netbox.voltlab.lan` opent.

```text
browser
  -> origineel HTTPS/IP-pakket
  -> VPN-client versleutelt en authenticeert
  -> onbetrouwbaar netwerk transporteert buitenste UDP/TCP-pakketten
  -> juiste VPN-peer controleert en ontsleutelt
  -> policy laat of weigert de bestemming
  -> NetBox verwerkt alleen toegelaten verkeer
```

| Stap | Securityvraag | Mogelijk bewijs in het labo |
|---|---|---|
| Tunnel opbouwen | Is dit de bedoelde peer? | Peeridentiteit en status in Tailscale. |
| Pakket beschermen | Is inhoud vertrouwelijk en integer? | Buitenste capture toont geen interne HTTP-inhoud. |
| Toegang beslissen | Mag deze bron naar deze dienst? | Toegelaten webtest én geweigerde test naar een niet-toegelaten poort. |
| Applicatie verwerken | Is de dienst zelf veilig? | HTTPS- en applicatielogs; dit wordt niet uitsluitend door de VPN bewezen. |

**Typische fout:** een succesvolle `ping` als volledig securitybewijs gebruiken. Een
ping bewijst bereikbaarheid voor één protocolpad. Hij bewijst geen vertrouwelijkheid,
geen correcte applicatieautorisatie en geen deny-regel.

**Kernzin:**

> Een veilige pakketstroom vereist een juiste peer, beschermde inhoud, beperkte toegang en een veilige eindapplicatie.

---

## 6. WireGuard als voorbeeld van moderne VPN-cryptografie

### 6.1 Waarom WireGuard relevant is

Tailscale gebruikt WireGuard als data-plane protocol. Dat betekent dat de daadwerkelijke netwerkpakketten tussen devices met WireGuard versleuteld worden.

Je hoeft WireGuard niet volledig te kunnen configureren in dit hoofdstuk. Je moet wel begrijpen waarom WireGuard vaak gebruikt wordt als voorbeeld van een moderne VPN:

| Kenmerk | Wat betekent dit concreet? | Wat betekent dit niet? |
|---|---|---|
| Relatief kleine protocol- en codebasis | Het ontwerp is doelgericht en beter afgebakend dan een allesomvattende VPN-suite. | Klein betekent niet automatisch foutloos of correct beheerd. |
| Moderne cryptografische keuzes | Encryptie, authenticatie en integriteit vormen één samenhangend protocolontwerp. | Studenten hoeven de wiskundige primitieve niet zelf te implementeren. |
| UDP-gebaseerd | WireGuard kan tunnelverkeer vervoeren zonder een tweede TCP-betrouwbaarheidslaag. | UDP betekent niet dat applicaties hun TCP-betrouwbaarheid verliezen. |
| Peers hebben publieke sleutels | Een tunnelpeer wordt cryptografisch herkenbaar. | Een sleutel vertelt zonder beheerlaag nog niet welke mens of bedrijfsrol erachter zit. |
| Cryptokey routing | Peer, toegelaten tunneladressen en routing hangen samen. | Dit vervangt geen enterprise-policy voor gebruikers, services en lifecycle. |

### 6.2 Cryptokey routing

WireGuard gebruikt het idee van cryptokey routing.

Conceptueel betekent dit:

> Welke IP-adressen via een peer mogen lopen, hangt samen met de publieke sleutel van die peer.

Een klassieke route zegt:

```text
10.10.20.0/24 via router X
```

Bij WireGuard wordt dat idee gekoppeld aan een peer:

```text
10.10.20.0/24 via peer met public key ABC...
```

Dat is belangrijk omdat routing en identiteit dichter bij elkaar komen te liggen. Een pakket voor een bepaalde tunnelbestemming hoort bij een bepaalde cryptografische peer.

### 6.3 Handshake en sessiesleutels

Een WireGuard-verbinding gebruikt een handshake om veilige sessiesleutels af te spreken. Daarna worden datapakketten met die sessiesleutels versleuteld.

Conceptueel:

```text
1. Peer A kent public key van peer B.
2. Peer B kent public key van peer A.
3. Peers voeren handshake uit.
4. Beide peers leiden sessiesleutels af.
5. Dataverkeer wordt versleuteld en geauthenticeerd.
6. Sessiesleutels worden regelmatig vernieuwd.
```

Belangrijke eigenschappen:

| Eigenschap | Praktische betekenis | Ontwerprisico als je dit verkeerd interpreteert |
|---|---|---|
| Wederzijdse authenticatie | Beide kanten controleren de cryptografische peer. | Een geldig device is nog niet automatisch voor elke service geautoriseerd. |
| Replaybescherming | Oude transportpakketten kunnen niet zomaar opnieuw geldig verwerkt worden. | Dit voorkomt geen herhaling op applicatieniveau met nieuwe geldige requests. |
| Forward secrecy | Regelmatig vernieuwd sessiemateriaal beperkt de impact van een later sleutelverlies op oud verkeer. | Een actief gecompromitteerd endpoint kan huidige plaintext nog steeds zien. |
| Authenticated encryption | Versleuteling en integriteitscontrole worden samen toegepast. | Een packet capture zonder plaintext bewijst op zichzelf niet het volledige protocolontwerp. |

### 6.4 Wat WireGuard niet alleen oplost

WireGuard bepaalt niet automatisch:

- welke gebruiker eigenaar is van een device;
- of een laptop compliant is;
- welke ACL's gelden;
- welke DNS-instellingen gebruikt worden;
- welke routes goedgekeurd zijn;
- hoe devices worden verwijderd;
- welke logs een organisatie bewaart.

Daarvoor heb je een beheerlaag nodig. Bij Tailscale is dat de control plane met identity, devicebeheer, policy, DNS, route approval en logging.

Dat creëert een gedeelde verantwoordelijkheid:

| Laag | Waarop vertrouw je? | Typische beheersmaatregel |
|---|---|---|
| Endpoint | Private keys en ontsleutelde applicatiedata blijven beschermd. | Hardening, patching, schijfbeveiliging en EDR. |
| Data plane | Alleen de bedoelde peers kunnen geldige pakketten uitwisselen. | Actuele VPN-client en correcte packet filters. |
| Control plane | Juiste public keys, routes en policies worden verdeeld. | Sterke adminauthenticatie, auditlogs, beperkte beheerders en eventueel extra key-verificatie. |
| Applicatie | De dienst verwerkt alleen legitieme requests. | Eigen authenticatie, autorisatie, TLS en logging. |

Kernzin:

> WireGuard beschermt de tunnel. Het enterprise-ontwerp bepaalt wie de tunnel waarvoor mag gebruiken.

---

## 7. Data plane en control plane

### 7.1 Data plane

De data plane is het pad waar echte gebruikerspakketten doorheen gaan.

Voorbeelden:

- HTTP naar VM1;
- SSH naar een server;
- HTTPS naar NetBox;
- DNS naar een interne resolver;
- RDP naar een beheerserver.

Bij Tailscale loopt de data plane via WireGuard. Als twee devices direct verbonden zijn, gaan de versleutelde pakketten rechtstreeks tussen die devices.

### 7.2 Control plane

De control plane helpt bepalen hoe devices elkaar vinden en welke regels gelden.

Voorbeelden:

- device aanmelden;
- public keys verspreiden;
- ACL's publiceren;
- DNS-configuratie verdelen;
- routes goedkeuren;
- node metadata bijhouden;
- DERP-regio's bekendmaken.

De control plane hoeft niet per se de inhoud van je dataverkeer te zien. Ze beheert vooral wie er bestaat, welke keys en endpoints bekend zijn, en welke policy geldt.

Bij Tailscale ontvangen endpoints de informatie en packet filters die ze nodig hebben.
De uiteindelijke versleuteling, ontsleuteling en pakketverwerking gebeurt op de devices.
Dat maakt de control plane belangrijk zonder hem automatisch in het datapad te plaatsen.

### 7.3 Waarom dit onderscheid belangrijk is

Stel dat twee laptops via Tailscale rechtstreeks met elkaar praten.

```text
control plane: helpt peers elkaar vinden en policy kennen
data plane: versleutelde WireGuard-pakketten rechtstreeks tussen peers
```

Als directe connectiviteit niet lukt, kan de data plane via een relay lopen:

```text
Laptop A == encrypted == DERP relay == encrypted == Laptop B
```

De relay ziet dat er verkeer is, maar de VPN-inhoud blijft end-to-end versleuteld tussen de endpoints.

Belangrijke vraag:

> Wie helpt de verbinding opzetten, en wie kan de inhoud lezen?

Bij een goed ontwerp zijn dat niet dezelfde dingen.

### 7.4 Wat gebeurt er bij een storing?

Het onderscheid helpt ook bij troubleshooting.

| Storing | Mogelijk effect | Wat kan nog werken? |
|---|---|---|
| Control plane tijdelijk onbereikbaar | Geen nieuwe login, key- of policyupdate of nieuwe peerverbinding via de control plane. | Reeds verbonden peers kunnen met gecachete policy en bestaande paden nog communiceren. |
| Direct datapad valt weg | De applicatiestroom ondervindt verlies of vertraging. | Tailscale kan een ander direct endpoint, peer relay of DERP proberen. |
| DERP onbereikbaar | Connectieopbouw en fallback via die regio falen. | Een bestaand direct pad of een andere bereikbare relay kan blijven werken. |
| Policy weigert verkeer | De peer kan online en cryptografisch bereikbaar lijken, maar de service blijft geblokkeerd. | Control-planeconnectiviteit en verkeer naar andere toegelaten doelen. |

**Typische fout:** "de peer staat online, dus de applicatie moet werken". Online status,
padselectie, policy en applicatieluisterpoort zijn verschillende controles.

**Controleer:**

| Vraag | Geschikt bewijs |
|---|---|
| Kent de control plane beide devices? | Device-overzicht en `tailscale status`. |
| Is er een bruikbaar datapad? | `tailscale ping` en de overgang van DERP naar direct of peer relay. |
| Laat policy de echte service toe? | Een applicatietest op de bedoelde poort. |
| Blokkeert policy een ongewenste service? | Een expliciete negatieve test. |

---

## 8. Waarom VPN's vaak UDP gebruiken

### 8.1 UDP als transport

Veel moderne VPN's gebruiken UDP. WireGuard doet dat ook.

UDP heeft geen ingebouwde sessie zoals TCP. Dat klinkt primitief, maar is nuttig voor VPN:

| Eigenschap | Waarom nuttig voor een tunnel? |
|---|---|
| Geen eigen connectieopbouw voor elk tunnelpad | Het VPN-protocol beheert zelf handshakes, roaming en peers. |
| Geen ingebouwde retransmission | De ingekapselde applicatie bepaalt zelf of en hoe verlies hersteld wordt. |
| Beperkte transportoverhead | Er is geen tweede TCP-flowcontrol- en betrouwbaarheidslaag rond elk pakket. |
| Eigen keepalives mogelijk | De VPN kan gericht NAT- en firewallstate actief houden. |
| Geschikt voor endpointwissels | Een client kan van wifi naar mobiel netwerk migreren zonder dat UDP zelf een sessie-identiteit oplegt. |

### 8.2 TCP-over-TCP-probleem

Stel dat je een TCP-verbinding binnen een TCP-gebaseerde VPN stopt.

```text
Applicatie TCP
  binnen
VPN TCP
  binnen
IP-netwerk
```

Als er pakketverlies optreedt, proberen beide TCP-lagen herstel te regelen. Dat kan leiden tot extra vertraging en onvoorspelbare performance. Daarom is UDP vaak aantrekkelijker als buitenste transportlaag voor VPN-tunnels.

Dit betekent niet dat TCP-gebaseerde VPN's nooit werken. Het betekent wel dat UDP vaak efficiënter is voor het transport van gemengd verkeer.

### 8.3 UDP en firewalls

UDP heeft ook een nadeel:

> Sommige netwerken blokkeren of beperken outbound UDP.

Voorbeelden:

- gastennetwerk laat alleen webverkeer toe;
- bedrijfsfirewall laat geen onbekende UDP-poorten naar buiten;
- hotelwifi laat UDP pas na captive portal toe;
- mobiele provider gebruikt agressieve NAT-timeouts.

Daarom hebben moderne VPN-systemen fallbackmechanismen nodig. Als directe UDP niet lukt, kan een relay via HTTPS-achtige paden soms toch connectiviteit bieden, maar meestal met lagere performance.

Voor Tailscale zijn verschillende netwerkpaden functioneel verschillend:

| Verkeer | Typische rol | Productiebetekenis |
|---|---|---|
| Uitgaand UDP vanaf de Tailscale-luisterpoort, standaard `41641` | Directe WireGuard-paden naar peers. | Bestemmingspoorten van mobiele of externe peers zijn niet vooraf betrouwbaar te voorspellen. |
| Uitgaand UDP naar `3478` | STUN voor endpointobservatie. | Helpt bepalen welk publiek IP en welke poort de buitenwereld ziet. |
| Uitgaand TCP naar `443` | Control-plane- en DERP-bereikbaarheid. | Houdt coördinatie en fallback mogelijk wanneer direct UDP faalt. |

Poort `41641` is een standaardwaarde en kan gewijzigd zijn. Schrijf daarom geen
firewallregel op basis van geheugen alleen: controleer de werkelijke clientconfiguratie
en de actuele productdocumentatie.

**In productie:** begin bij egressbeleid en stateful return traffic voor gewone
clients. Maak niet elk clientdevice met een brede inboundregel publiek bereikbaar.

---

## 9. NAT en PAT herbekeken

### 9.1 NAT als adresvertaling

NAT vertaalt IP-adressen. In thuis- en kleine bedrijfsnetwerken zie je meestal Source NAT of PAT.

Een laptop heeft bijvoorbeeld:

```text
192.168.1.50
```

Wanneer die naar internet gaat, vertaalt de router dat naar:

```text
203.0.113.20:45123
```

De router houdt een tabel bij:

| Binnen | Buiten |
|---|---|
| `192.168.1.50:51820` | `203.0.113.20:45123` |

Als een antwoord terugkomt naar `203.0.113.20:45123`, weet de NAT-router dat het naar `192.168.1.50:51820` moet.

### 9.2 NAT mapping

Een NAT mapping is zo'n tijdelijke vertaling.

Belangrijke eigenschappen:

| Eigenschap | Concrete betekenis voor VPN-verkeer |
|---|---|
| Ontstaat meestal door uitgaand verkeer | De interne peer maakt eerst state door zelf een UDP-pakket te sturen. |
| Heeft een timeout | Zonder verkeer kan de vertaling verdwijnen en moet het pad opnieuw opgebouwd worden. |
| Is protocol- en poortgebonden | TCP-state en UDP-state zijn niet dezelfde mapping. |
| Kan bestemmingsafhankelijk zijn | Het externe bronpoortnummer kan veranderen naargelang de server waarmee de client praat. |
| Laat passend retourverkeer toe | Niet elk willekeurig inbound pakket voldoet aan de bestaande state. |
| Kan door meerdere NAT-lagen lopen | Elke laag maakt een eigen vertaling die afzonderlijk kan vervallen of blokkeren. |

Daarom sturen veel VPN's keepalives: kleine pakketten die ervoor zorgen dat NAT-state niet te snel verdwijnt.

### 9.3 PAT en poorten

PAT gebruikt poorten om meerdere interne clients achter een publiek IP te laten delen.

```text
192.168.1.10:50000 -> 203.0.113.20:41001
192.168.1.11:50000 -> 203.0.113.20:41002
192.168.1.12:50000 -> 203.0.113.20:41003
```

Voor gewone webclients is dit ideaal. Clients starten verbindingen naar buiten en antwoorden komen terug via de bestaande mapping.

Voor peer-to-peer VPN is het lastiger. Beide kanten zitten vaak achter NAT en willen elkaar rechtstreeks bereiken.

### 9.4 Voorspelbare en bestemmingsafhankelijke mappings

Niet elke NAT maakt mappings op dezelfde manier.

```text
voorspelbaarder:
192.168.1.50:41641 -> 203.0.113.20:45123
dezelfde publieke poort voor meerdere bestemmingen

moeilijker:
naar STUN A -> 203.0.113.20:45123
naar peer B -> 203.0.113.20:53784
```

In het tweede geval kan een endpoint dat via STUN werd ontdekt onbruikbaar zijn voor
een andere bestemming. Dit wordt vaak als een vorm van *hard NAT* beschreven.

| Observatie | Voorzichtige conclusie | Wat mag je nog niet besluiten? |
|---|---|---|
| `MappingVariesByDestIP: false` | De mapping lijkt in deze meting niet per bestemmings-IP te variëren. | Dat elk toekomstig peerpad direct zal werken. |
| `MappingVariesByDestIP: true` | Bestemmingsafhankelijk gedrag maakt hole punching moeilijker. | Dat relay de enige mogelijke oplossing is aan elke peerzijde. |
| `PortMapping` meldt een mechanisme | Een router ondersteunt mogelijk automatische mapping. | Dat de vereiste mapping actief, veilig en bruikbaar is. |
| Geen publiek IPv4-adres op de client | NAT is aanwezig of IPv4-connectiviteit is anders opgebouwd. | Dat IPv6 of een direct pad onmogelijk is. |

**Controleer:** behandel `tailscale netcheck` als een momentopname van de lokale
netwerkomgeving. Het commando beschrijft niet zelfstandig de volledige verbinding
tussen twee specifieke peers.

---

## 10. Stateful firewalls

### 10.1 Outbound is vaak toegestaan

Veel firewalls werken stateful.

Dat betekent:

> Verkeer naar buiten mag vaak starten. Antwoorden op toegestane sessies mogen terugkomen. Nieuwe verbindingen van buiten naar binnen worden geblokkeerd.

Voor webverkeer is dat normaal:

```text
laptop -> internet:443       toegestaan
internet:443 -> laptop       toegestaan als antwoord
internet -> laptop random    geblokkeerd
```

### 10.2 VPN-gevolg

Een VPN-client op een laptop kan meestal zelf naar buiten verbinden. Dat werkt goed voor klassieke client-server-VPN's:

```text
laptop -> vpn.example.com:443 of UDP-poort
```

Bij mesh-VPN's willen devices elkaar rechtstreeks bereiken:

```text
laptop A -> laptop B
laptop B -> laptop A
```

Als beide achter NAT/firewall zitten, is er aan beide kanten geen open inkomende poort. Toch kan directe connectiviteit soms lukken door NAT traversal.

### 10.3 Firewall is niet hetzelfde als NAT

NAT en firewall worden vaak door hetzelfde toestel uitgevoerd, maar ze zijn conceptueel verschillend.

| Functie | Vraag |
|---|---|
| NAT | Hoe worden adressen en poorten vertaald? |
| Firewall | Welk verkeer mag door? |

Een router kan NAT doen zonder strenge firewallregels. Een firewall kan stateful filtering doen zonder NAT. In de praktijk zitten ze vaak samen in een thuisrouter, bedrijfsfirewall of cloud security gateway.

### 10.4 Vier beslissingen die vaak verward worden

| Mechanisme | Beslissing | Voorbeeld |
|---|---|---|
| Routing | Waar moet het pakket naartoe? | Default route naar de internetgateway. |
| NAT/PAT | Welk adres en welke poort worden vertaald? | `192.168.1.50:41641` wordt een publiek endpoint. |
| Stateful firewall | Past dit pakket binnen toegelaten state of beleid? | Retour-UDP bij een bestaande mapping wordt aanvaard. |
| VPN-policy | Mag deze geauthenticeerde bron de tunnelbestemming gebruiken? | Student mag TCP/80 maar niet TCP/22 naar de server. |

Een pakket kan dus correct gerouteerd en vertaald worden, maar alsnog door een
firewall of VPN-policy geweigerd worden.

**Troubleshootingvolgorde:**

```text
route aanwezig?
  -> NAT/endpoint bruikbaar?
    -> firewall laat transport toe?
      -> VPN-pad bestaat?
        -> VPN-policy laat service toe?
          -> applicatie luistert en antwoordt?
```

Deze volgorde voorkomt dat je willekeurig ACL's versoepelt terwijl de applicatie
bijvoorbeeld alleen op `127.0.0.1` luistert.

---

## 11. NAT traversal

### 11.1 Het probleem

Twee peers willen rechtstreeks praten.

```text
Laptop A achter NAT A
Laptop B achter NAT B
```

Geen van beide heeft zomaar een publiek bereikbaar UDP-endpoint. Als A een pakket stuurt naar het private adres van B, werkt dat niet. Private adressen zijn niet routeerbaar over internet.

De peers moeten dus ontdekken:

| Te ontdekken vraag | Waarom nodig? |
|---|---|
| Welk publiek IP en welke poort ziet de buitenwereld voor A en B? | Peers kunnen geen internetpakket naar elkaars private RFC1918-adres sturen. |
| Welke lokale en publieke endpoints zijn kandidaten? | Op hetzelfde LAN kan een lokaal endpoint beter zijn dan een publiek ompad. |
| Hoe gedragen NAT en firewall zich? | Bestemmingsafhankelijke mappings of strenge return filters kunnen kandidaten onbruikbaar maken. |
| Kunnen beide kanten bijna gelijktijdig uitsturen? | Daardoor ontstaat aan beide zijden passende state. |
| Blijft die state lang genoeg bestaan? | Een verlopen mapping breekt het directe pad. |

### 11.2 Endpoint discovery

Een peer kent lokaal bijvoorbeeld:

```text
192.168.1.50:41641
```

Maar de buitenwereld ziet misschien:

```text
203.0.113.20:45123
```

Om dat te ontdekken kan een client een server op internet vragen:

> Van welk IP en welke poort zie jij mijn pakket komen?

Dat idee ken je als STUN: *Session Traversal Utilities for NAT*. Het doel is niet om
de applicatie-inhoud door die STUN-server te sturen, maar om het waargenomen publieke
endpoint te ontdekken.

STUN beantwoordt dus een observatievraag:

```text
"Van welk publiek IP-adres en bronpoort ontving jij mijn UDP-pakket?"
```

STUN opent zelf geen onbeperkte inbound toegang en is geen vervanging voor een relay.

### 11.3 Hole punching

UDP hole punching gebruikt het feit dat NAT en stateful firewalls state maken voor uitgaand verkeer.

Sterk vereenvoudigd:

```text
1. Peer A stuurt UDP naar het publieke endpoint van B.
2. NAT A maakt een mapping voor A.
3. Peer B stuurt UDP naar het publieke endpoint van A.
4. NAT B maakt een mapping voor B.
5. Als timing en NAT-gedrag gunstig zijn, laten beide kanten verkeer door.
```

Het lijkt alsof beide peers "inkomend" verkeer ontvangen, maar technisch gezien hebben beide kanten eerst zelf uitgaand verkeer gestuurd. De firewalls zien daarna antwoorden of passend verkeer binnen bestaande state.

De control plane en DERP kunnen endpointinformatie helpen uitwisselen, maar het
uiteindelijke directe datapad loopt niet via de control plane:

```text
coördinatie: A -> control/DERP <- B
endpointinfo: A <------------> B
hole punching: A ==== UDP ====> B
datapad:       A == WireGuard == B
```

### 11.4 Waarom dit niet altijd lukt

NAT traversal is geen garantie.

Mogelijke blokkades:

| Probleem | Effect |
|---|---|
| Symmetric NAT | Mapping hangt sterk af van externe bestemming. |
| Strenge outbound firewall | UDP naar onbekende bestemmingen wordt geblokkeerd. |
| Korte UDP-timeout | Mapping verdwijnt snel. |
| Geen hairpinning | Peers achter dezelfde CGNAT kunnen elkaar moeilijk bereiken via publiek endpoint. |
| Double NAT | Port mapping werkt alleen op eerste NAT-laag. |
| CGNAT | Gebruiker kan ISP-NAT niet configureren. |
| Captive portal | Verkeer wordt eerst onderschept of beperkt. |
| UDP volledig geblokkeerd | Directe WireGuard-verbinding lukt niet. |

Daarom heb je fallback nodig.

### 11.5 Wat bewijst een directe verbinding?

Een directe verbinding bewijst dat de peers op dat moment een bruikbaar UDP-pad
hebben gevonden. Ze bewijst niet automatisch dat één peer permanent publiek
bereikbaar is.

| Test | Verwacht bij direct pad | Waarom test je dit? |
|---|---|---|
| `tailscale ping <peer>` meermaals uitvoeren | Eerste pakketten kunnen via DERP lopen; daarna verschijnt een `ip:poort`-pad. | NAT traversal en mogelijke upgrade vragen tijd. |
| `tailscale status` na actief verkeer | `direct` bij de betreffende peer. | Status is per peerpaar en wordt duidelijker na werkelijk verkeer. |
| Laptop naar ander netwerk verplaatsen | Endpoint of connection type kan wijzigen. | Bewijst dat padselectie afhangt van beide actuele netwerken. |
| Applicatietest herhalen | Service blijft bereikbaar of herstelt na padwissel. | Meet beschikbaarheid bovenop de padselectie. |

**Typische fout:** één `tailscale ping` bewaren waarop alleen de eerste DERP-pong
zichtbaar is en besluiten dat direct verkeer onmogelijk is.

Kernzin:

> NAT traversal probeert een direct pad te vinden, maar het netwerk onderweg beslist mee hoe moeilijk dat wordt.

---

## 12. Port mapping en port forwarding

### 12.1 Automatische port mapping

Sommige routers ondersteunen protocollen waarmee een client een port mapping kan aanvragen.

Voorbeelden:

- UPnP IGD;
- NAT-PMP;
- PCP.

Conceptueel vraagt een device:

```text
Forward publieke UDP-poort X naar mijn lokale UDP-poort Y.
```

Als de router dit toestaat, wordt het device beter rechtstreeks bereikbaar. Dat kan NAT traversal eenvoudiger maken.

De drie mechanismen betekenen niet hetzelfde:

| Mechanisme | Wie vraagt of configureert? | Lifecycle | Belangrijk risico |
|---|---|---|---|
| UPnP IGD, NAT-PMP of PCP | Client vraagt dynamisch aan de lokale gateway. | Vaak tijdelijk en automatisch vernieuwd. | Onbeheerde clients kunnen mappings aanvragen als routerbeleid te ruim is. |
| Handmatige port forwarding | Netwerkbeheerder configureert de gateway. | Blijft meestal staan tot iemand ze verwijdert. | Vergeten regels en verkeerd intern doel vergroten het aanvalsoppervlak. |
| Alleen een host-firewallregel | Beheerder laat verkeer op het endpoint toe. | Lokaal op het endpoint. | Helpt niet als upstream NAT geen bruikbare mapping heeft. |

### 12.2 Handmatige port forwarding

Bij handmatige port forwarding configureert een beheerder expliciet:

```text
WAN UDP 41641 -> 192.168.1.50 UDP 41641
```

Of bij een server:

```text
WAN UDP <vpn-poort> -> VPN-gateway
```

Dit kan directe verbindingen betrouwbaarder maken, vooral voor een vaste server, subnet router of exit node.

### 12.3 Waarom dit performance kan verbeteren

Een directe verbinding heeft meestal:

- minder hops;
- lagere latency;
- hogere throughput;
- minder afhankelijkheid van relaycapaciteit;
- minder kans op geografisch omwegverkeer.

Vergelijk:

```text
direct:
Laptop A == encrypted UDP == Laptop B

relay:
Laptop A == encrypted == Relay == encrypted == Laptop B
```

De relay kan ver weg staan, extra latency toevoegen of bandbreedte beperken. Direct verkeer blijft daarom meestal de beste performancekeuze.

### 12.4 Securityafweging bij port forwarding

Port forwarding kan performance verbeteren, maar het is geen gratis keuze.

Vragen:

| Vraag | Waarom moet je dit vóór de wijziging weten? |
|---|---|
| Welke poort en welk protocol worden publiek bereikbaar? | Een regel voor alleen de nodige UDP-poort is kleiner dan een brede poortreeks. |
| Draait daar alleen de bedoelde VPN-service? | Een verkeerde bind of DNAT-doel kan een andere dienst blootstellen. |
| Is het endpoint gepatcht en gehard? | Publiek bereikbare code ontvangt scans en ongewenste pakketten. |
| Staat de host firewall correct? | De gatewayregel is niet de enige beschermingslaag. |
| Is logging en monitoring actief? | Je wil afwijkend gebruik en configuratiefouten kunnen onderzoeken. |
| Heeft het device een stabiel intern adres? | Anders kan de forwarding later naar het verkeerde endpoint wijzen. |
| Wie is eigenaar en wanneer volgt review? | Permanente uitzonderingen zonder lifecycle blijven vaak onnodig bestaan. |

Belangrijke nuance:

> Een VPN-poort forwarden is niet hetzelfde als interne services publiek maken, maar het vergroot wel het publieke aanvalsoppervlak van de VPN-endpoint.

### 12.5 Enterprise-richtlijn

Voor gewone laptops en mobiele clients wil je meestal geen handmatige port forwarding. Die zitten op wisselende netwerken en horen geen publiek bereikbaar endpoint te worden.

Voor vaste infrastructuur kan het wel zinvol zijn:

| Endpoint | Port forwarding zinvol? | Waarom |
|---|---|---|
| Laptop van medewerker | meestal niet | wisselend netwerk, geen serverrol |
| Subnet router | soms wel | performance en bereikbaarheid voor routed access |
| Exit node | soms wel | veel verkeer, performance belangrijk |
| Site-to-site gateway | vaak wel | vaste infrastructuur, beheerbaar |
| Tijdelijke lab-VM | meestal niet | lifecycle en risico moeilijker te beheren |

**Labkeuze:** in de workshop wijzig je geen campusrouter, geen eduroam-firewall en
geen NAT-configuratie. Je meet de bestaande situatie en ontwerpt alleen een
beargumenteerde wijziging. Dat houdt de observatie reproduceerbaar en voorkomt dat een
performanceproef onbedoeld productie-infrastructuur wijzigt.

---

## 13. DERP en relays

### 13.1 Wat is DERP?

DERP staat voor Designated Encrypted Relay for Packets.

In Tailscale is DERP een relaymechanisme dat helpt bij connectieopbouw en als fallback kan dienen wanneer directe connectiviteit niet lukt.

Belangrijk:

> DERP is een relay voor versleutelde pakketten. Het is geen systeem dat de inhoud van je VPN-verkeer moet ontsleutelen.

Conceptueel:

```text
Device A == WireGuard encrypted == DERP == WireGuard encrypted == Device B
```

De endpoints houden de cryptografische bescherming. De relay transporteert pakketten.

### 13.2 Waarvoor dient DERP?

DERP heeft twee grote functies:

| Functie | Uitleg | Wat ziet DERP daarbij? |
|---|---|---|
| Connectieopbouw helpen | Devices kunnen elkaar bereiken via een bekend relaypunt terwijl ze directe endpoints uitwisselen. | Endpoint- en timingmetadata voor de relayverbinding, geen ontsleutelde applicatiepayload. |
| Eerste bruikbare datapad | Een nieuw peerpaar kan onmiddellijk via DERP beginnen terwijl het een beter pad zoekt. | Reeds versleutelde WireGuard-pakketten. |
| Fallback relay | Als direct verkeer en een beschikbare peer relay niet lukken, kan verkeer via DERP blijven werken. | Volume, timing en verbonden endpoints, maar niet de tunnelplaintext. |

Dit verklaart waarom een VPN soms "werkt maar traag is". De verbinding is dan misschien relayed.

### 13.3 Direct, peer relay en DERP

Tailscale kent meerdere connection types.

| Type | Pad | Typische eigenschap |
|---|---|---|
| Direct | device naar device via UDP | laagste latency en hoogste throughput |
| Peer relay | via een ander device in dezelfde tailnet | extra hop, vaak beter dan verre DERP |
| DERP relay | via DERP-server | robuuste fallback, meestal trager |

Performanceverschil is belangrijker dan het verschil in vertrouwelijkheid van de
inhoud. De WireGuard-inhoud blijft bij alle drie de types end-to-end versleuteld. De
metadata, beheerpartij, capaciteit en locatie van het tussenpunt verschillen wel.

### 13.4 Hoe Tailscale een pad kiest

Bij Tailscale start een nieuwe verbinding tussen peers via DERP. Daarna probeert het
systeem het pad te verbeteren.

```text
nieuw peerpaar
    |
    v
DERP als onmiddellijk bruikbaar pad
    |
    +--> NAT traversal slaagt --------> direct UDP
    |
    +--> direct faalt, peer relay beschikbaar --> peer-relay
    |
    +--> beide alternatieven falen ---> DERP blijft datapad
```

Tailscale controleert later opnieuw of een beter pad beschikbaar wordt. Een verbinding
kan door veranderende netwerkomstandigheden ook van direct terugvallen naar relay.

| Observatie | Correcte interpretatie |
|---|---|
| Eerste pongs via DERP, daarna direct | Normale opbouw: de bereikbaarheid bestond al terwijl NAT traversal nog liep. |
| Blijvend `peer-relay` | Direct lukt niet, maar een bereikbaar tailnetdevice relayeert. |
| Blijvend `relay <regio>` | Direct en peer relay zijn niet bruikbaar; DERP blijft fallback. |
| Eerst direct, later relay | Het netwerkpad, de mapping of firewallstate is veranderd. |

Een korte DERP-fase is dus geen fout. Langdurig relaygebruik is vooral een aanleiding
om performance en netwerkbeleid te onderzoeken.

### 13.5 Hoe herken je relaygebruik?

Bij Tailscale kan je bijvoorbeeld denken aan:

```text
tailscale status
tailscale ping <peer>
tailscale netcheck
```

Je zoekt conceptueel naar:

| Controle | Mogelijke observatie | Betekenis en beperking |
|---|---|---|
| `tailscale ping <peer>` | eerst `via DERP(fra)`, later `via 198.51.100.8:41641` | Toont de opbouw en uiteindelijke route voor dit peerpaar; meerdere pongs zijn nodig. |
| `tailscale status` | `direct <ip:poort>` | Er was recent een actief direct pad naar die peer. |
| `tailscale status` | `relay <regio>` | Dataverkeer liep via DERP. |
| `tailscale status` | `peer-relay <endpoint>` | Een tailnetdevice trad op als relay. |
| `tailscale netcheck` | `UDP: true` | UDP werkt naar de geteste infrastructuur; dit garandeert nog geen direct pad naar elke peer. |
| `tailscale netcheck` | mapping- of port-mappinginformatie | Verklaart waarom traversal makkelijker of moeilijker kan zijn. |

In een cursus hoef je niet elke outputvariant uit het hoofd te kennen. Je moet vooral begrijpen wat je onderzoekt:

> Loopt mijn VPN-data rechtstreeks tussen peers, of via een tussenpunt?

**Bewijsregel:** noteer altijd tijdstip, bronnetwerk, doelpeer, connection type en
gemeten latency/throughput samen. Een losse screenshot zonder context is niet
vergelijkbaar met een tweede meting.

---

## 14. Firewalls en VPN-performance

### 14.1 Security en performance botsen soms

Een firewall die alleen outbound HTTPS toelaat, is eenvoudig te controleren:

```text
clients -> internet TCP/443
```

Maar een mesh VPN wil vaak direct UDP-verkeer tussen peers:

```text
peer A -> peer B UDP
peer B -> peer A UDP
```

Als dat niet mag, blijft de verbinding misschien wel werken via relay, maar trager.

### 14.2 Wat kan een netwerkbeheerder toestaan?

Voor betere VPN-performance kan een beheerder doelgericht volgende paden en
eigenschappen beoordelen:

| Maatregel | Wat verbetert dit? | Randvoorwaarde |
|---|---|---|
| Uitgaand UDP en passend retourverkeer toelaten | Vergroot de kans op directe WireGuard-paden. | De bronpoort kan standaard `41641` zijn, maar is configureerbaar; externe peers zijn dynamisch. |
| STUN naar UDP/3478 toelaten | Maakt endpointobservatie mogelijk. | Een succesvolle STUN-test garandeert geen direct peerpad. |
| TCP/443 naar control plane en DERP toelaten | Behoudt coördinatie en robuuste fallback. | Blokkeer relay niet om direct verkeer af te dwingen. |
| UDP-state niet onnodig kort maken | Vermindert het voortdurend vervallen van mappings. | Timeouts moeten passen bij het algemene firewallbeleid. |
| IPv6 correct filteren en routen | Kan NAT-complexiteit verminderen en een direct pad bieden. | IPv6 vereist evenzeer firewallbeleid; het is geen onbeveiligde bypass. |
| Gerichte forwarding voor vaste gateways | Maakt een stabiele subnet router of exit node beter bereikbaar. | Alleen na risicoanalyse, eigenaar, monitoring en reviewdatum. |
| Peer relay in beheerde infrastructuur | Biedt een gecontroleerde fallback die vaak dichterbij ligt dan DERP. | Vraagt capaciteit, bereikbaarheid en eigen beheer. |

### 14.3 Wat moet je niet zomaar doen?

Slechte reflexen:

| Actie | Probleem |
|---|---|
| Alle inbound UDP naar clients openzetten | Onnodig groot aanvalsoppervlak. |
| UPnP overal inschakelen zonder beleid | Devices kunnen zelf mappings maken. |
| VPN-relays blokkeren om direct verkeer te forceren | Verbindingen kunnen volledig breken. |
| Logging uitschakelen voor performance | Incidentanalyse wordt moeilijker. |
| `*:*` in VPN-policy zetten om snelheid te testen | Autorisatie wordt onveilig. |

Betere aanpak:

1. Meet eerst of verbinding direct of relayed is.
2. Bepaal of performanceprobleem door relay, latency, packet loss of applicatie komt.
3. Open alleen de noodzakelijke firewallpaden.
4. Test opnieuw.
5. Documenteer de keuze.

Een wijziging is pas geslaagd wanneer je dezelfde meting vóór en na uitvoert.

| Voor/na-bewijs | Verwacht bij een nuttige wijziging |
|---|---|
| Connection type | Van blijvend DERP naar direct of een bewust gekozen peer relay. |
| RTT | Lager of stabieler, gemeten over meerdere pakketten. |
| Throughput | Hoger bij dezelfde endpoints, tool en testduur. |
| Negatieve securitytest | Een niet-toegelaten service blijft geweigerd. |
| Logs | De nieuwe firewallregel matcht alleen het bedoelde verkeer. |

---

## 15. Wat kan een netwerkbeheerder zien?

### 15.1 Lokaal netwerkbeheerder

Een beheerder van het wifi- of LAN-netwerk ziet mogelijk:

- MAC-adres van je device op het lokale netwerk;
- lokaal IP-adres;
- DHCP-hostname of device fingerprinting;
- ARP/NDP-verkeer;
- DNS-verkeer als je lokale DNS gebruikt;
- bestemmings-IP's waarmee je device verbinding maakt;
- poorten en protocollen op de buitenkant;
- hoeveelheid verkeer;
- timing van verkeer;
- captive portal login;
- dat je VPN gebruikt of naar een relay/control-plane gaat.

Die beheerder ziet normaal niet:

- de inhoud van pakketten binnen de VPN-tunnel;
- welke interne host binnen de tunnel exact wordt benaderd, als die informatie volledig in de tunnel zit;
- SSH-commando's binnen de tunnel;
- HTTP-paden binnen de tunnel;
- applicatiedata binnen de tunnel.

Nuance:

> Als DNS buiten de VPN gebeurt, kan DNS veel verklappen. Als DNS binnen de VPN of via Split DNS loopt, ziet de lokale netwerkbeheerder minder over interne namen.

### 15.2 Bedrijfsfirewallbeheerder

Een beheerder van de bedrijfsfirewall waar je uitgaand doorheen gaat, kan meer context hebben:

- gebruiker of device via NAC/proxy;
- bestemming van VPN-control-plane of relay;
- hoeveelheid VPN-verkeer;
- tijdstippen;
- blokkeringen;
- of UDP lukt;
- of verkeer via TCP/443 fallback loopt;
- policy hits;
- eventueel TLS SNI voor niet-VPN-verkeer.

Maar ook hier geldt:

> Versleutelde VPN-inhoud is niet leesbaar zonder endpoint- of sleutelcompromis.

### 15.3 ISP

Een internetprovider ziet vooral netwerkmetadata:

- klantlijn of mobiel abonnement;
- publieke IP's;
- bestemmings-IP's;
- poorten;
- volume;
- timing;
- mogelijk dat VPN/relay gebruikt wordt.

De ISP ziet normaal niet:

- inhoud van VPN-verkeer;
- interne IP's binnen de tunnel;
- bestanden of commando's binnen de VPN;
- applicatiepayload binnen de tunnel.

### 15.4 VPN-beheerder

De VPN-beheerder is een andere categorie. Die beheert de tailnet of VPN-omgeving.

Afhankelijk van product en instellingen kan die zien:

- welke users bestaan;
- welke devices aangemeld zijn;
- device namen;
- public keys;
- tags;
- ACL-policy;
- routes;
- DNS-instellingen;
- online/offline-status;
- login- en configuratielogs;
- SSH-policy;
- soms network flow logs of audit logs;
- welke devices mogelijk met elkaar communiceren.

De VPN-beheerder ziet niet automatisch de inhoud van end-to-end versleutelde datastromen. Maar hij heeft wel veel metadata en beleidscontrole.

Belangrijke privacyzin:

> Een VPN verbergt niet alles voor de VPN-beheerder. Hij verschuift vertrouwen van het lokale netwerk naar de VPN-omgeving en de endpoints.

### 15.5 Relaybeheerder

Een relay ziet:

- welke endpoints met de relay verbonden zijn;
- volume en timing;
- relayregio;
- mogelijk bron-IP's van clients;
- dat er versleutelde pakketten worden doorgestuurd.

Een relay ziet normaal niet:

- de plaintext inhoud;
- de HTTP-request binnen de tunnel;
- SSH-inhoud;
- bestanden;
- wachtwoorden binnen de VPN-tunnel.

Dat is het verschil tussen:

```text
transporteren van encrypted packets
```

en:

```text
ontsleutelen van de sessie
```

### 15.6 Eén zichtbaarheidstabel

Dezelfde pakketstroom verschijnt anders bij elke observator.

| Observator | Ziet meestal wel | Ziet normaal niet door de VPN alleen | Vertrouwens- of governancevraag |
|---|---|---|---|
| Lokaal LAN/wifi | Lokaal device, buitenste bestemmingen, protocol, timing en volume; mogelijk lokale DNS. | Interne IP-header en applicatiepayload in de tunnel. | Wie beheert wifi, DHCP, DNS en retentie? |
| Bedrijfsfirewall | Gebruikers/devicecontext, policy hits, buitenste flowmetadata en blokkeringen. | End-to-end WireGuard-plaintext. | Worden VPN-flows uitzonderlijk gelogd of beperkt? |
| ISP | Klantaansluiting, publieke endpoints, timing en volume. | Interne tunnelbestemmingen en applicatie-inhoud. | Welke wettelijke en contractuele retentie geldt? |
| Tailscale-control plane | Devices, identities, public keys, policy, routes, DNS- en coördinatiemetadata. | Niet automatisch de plaintext van het peer-to-peer datapad. | Wie mag beheerwijzigingen uitvoeren en logs raadplegen? |
| DERP-beheerder | Verbonden endpoints, regio, timing en doorgestuurd volume. | Ontsleutelde HTTP-, SSH- of bestandsinhoud in WireGuard. | Welke relayregio en beheerpartij worden gebruikt? |
| Subnet router | Tunnelbron, interne bestemming, poort, timing en volume; soms vertaald bronadres. | Applicatieplaintext als daarboven nog HTTPS/SSH actief is. | Is SNAT actief en welke logs bewaart de router? |
| Exit node | Internetbestemmingen, poorten, timing, volume en mogelijk DNS. | HTTPS-inhoud zonder aanvullende endpoint- of TLS-controle. | De exit node neemt zichtbaarheid over van het lokale netwerk. |
| Endpoint zelf | Ontsleutelde netwerk- en applicatiedata die het verwerkt. | Niets wat buiten zijn toegelaten of gekraakte context valt. | Endpointcompromis doorbreekt de beschermingsgrens. |

**Kernzin:**

> Encryptie verwijdert zichtbaarheid niet; ze verdeelt zichtbaarheid anders over endpoints, beheerlijnen en tussenliggende netwerken.

---

## 16. Wat kan een beheerder niet zien?

Een goed geconfigureerde VPN beperkt zichtbaarheid van de inhoud.

Een tussenliggende netwerkbeheerder kan normaal niet zien:

- welke URL binnen een interne webapp geopend wordt;
- welke SQL-query naar een database gaat;
- welk bestand via SMB binnen de tunnel wordt geopend;
- welke commando's over SSH lopen;
- welke HTTP-headers binnen de tunnel zitten;
- welke interne cookies of tokens in die sessie gebruikt worden.

Maar let op: "niet zien" betekent niet "niets afleiden".

Uit metadata kan soms veel blijken:

| Metadata | Mogelijke inferentie |
|---|---|
| Veel verkeer naar relay in kantooruren | gebruiker werkt via VPN |
| Hoge upload naar vaste peer | backup of file transfer |
| Regelmatige korte sessies | monitoring of keepalive |
| VPN-verkeer stopt na policywijziging | toegang geblokkeerd of client offline |
| Relayed verbinding met hoge latency | direct pad faalt waarschijnlijk |

Daarom is privacy nooit alleen een cryptografische vraag. Het is ook een logging-, beleid- en governancevraag.

### 16.1 Wat bewijst een packet capture?

In de workshop vergelijk je twee observatiepunten.

| Capturepunt | Wat verwacht je? | Sterk bewijs | Verkeerde conclusie |
|---|---|---|---|
| Virtuele Tailscale-interface | Binnenste IP-verkeer en mogelijk herkenbare testpayload. | Je identificeert de doelservice en het oorspronkelijke verkeer. | "De VPN versleutelt niet", omdat het endpoint na ontsleuteling plaintext verwerkt. |
| Fysieke wifi- of ethernetinterface bij direct pad | Buitenste UDP-flow naar het publieke peerendpoint. | De interne HTTP-testpayload is daar niet leesbaar. | "Niemand ziet iets"; IP, poort, timing en volume blijven zichtbaar. |
| Fysieke interface bij DERP | Versleuteld verkeer naar de DERP-regio, vaak via een toegestaan relaypad. | De relaybestemming is zichtbaar, de interne applicatiepayload niet. | "DERP ontsleutelt de tunnel", enkel omdat het in het netwerkpad staat. |

Een capture is observatiebewijs, geen wiskundig bewijs van alle cryptografische
eigenschappen. Combineer hem met protocolkennis, peeridentiteit en een negatieve
toegangstest.

---

## 17. Full tunnel, split tunnel en zichtbaarheid

### 17.1 Split tunnel

Bij split tunnel gaat alleen bepaald verkeer door de VPN.

Voorbeeld:

```text
10.20.0.0/16 -> via VPN
internet -> rechtstreeks via lokaal netwerk
```

Gevolg:

- interne bedrijfsdiensten zijn beschermd via VPN;
- gewone websites lopen via het lokale netwerk;
- lokale netwerkbeheerder ziet nog gewone internetbestemmingen;
- VPN-beheerder ziet niet al het internetverkeer.

Een split-tunnelclaim moet je per bestemming testen:

| Test | Verwacht | Waarom test je dit? |
|---|---|---|
| Tailscale-IP van de server | Via de Tailscale-interface. | Bewijst dat overlayverkeer de tunnel gebruikt. |
| Publiek testadres | Via de gewone default route, zolang geen exit node actief is. | Bewijst dat niet al het internetverkeer door de tunnel gaat. |
| Interne MagicDNS-naam | Resolveert naar het bedoelde Tailscale-adres. | Scheidt naamresolutie van routing. |
| Niet-bestaande of niet-toegelaten interne dienst | Resolveert eventueel wel, maar verbinding faalt. | Bewijst dat DNS-succes geen autorisatiebewijs is. |

### 17.2 Full tunnel

Bij full tunnel gaat al het verkeer door de VPN of exit node.

```text
0.0.0.0/0 -> via VPN
```

Gevolg:

- lokaal netwerk ziet vooral VPN-verkeer;
- VPN-exit ziet meer internetmetadata;
- organisatie kan internetbeleid centraal afdwingen;
- latency kan stijgen;
- privacy verschuift naar de exit node of organisatie.

Bij IPv6 moet je dezelfde vraag afzonderlijk stellen. Alleen een IPv4-default route
door de VPN sturen terwijl IPv6 rechtstreeks blijft uitgaan, kan beleid en
privacyverwachtingen doorbreken.

### 17.3 Zichtbaarheidsvergelijking

| Vraag | Split tunnel | Full tunnel |
|---|---|---|
| Ziet lokale wifi gewone websites? | ja, voor verkeer buiten VPN | meestal minder |
| Ziet VPN-beheerder internetverkeer? | meestal alleen interne routes | veel meer metadata |
| Is performance vaak beter? | vaak ja | hangt af van exit node |
| Is centraal securitybeleid eenvoudiger? | minder | meer |
| Is privacy automatisch beter? | niet absoluut | niet absoluut |

Kernzin:

> Full tunnel verbergt meer voor het lokale netwerk, maar geeft meer zichtbaarheid en verantwoordelijkheid aan de VPN-uitgang.

---

## 18. Subnet routers, exit nodes en zichtbaarheid

### 18.1 Subnet router

Een subnet router maakt een intern subnet bereikbaar.

```text
Laptop -> VPN -> subnet router -> 10.20.10.4
```

De subnet router ziet mogelijk:

- bronverkeer vanuit de tailnet;
- bestemmingen in het interne subnet;
- poorten;
- volume;
- timing.

Maar als de applicatie zelf HTTPS gebruikt, ziet de subnet router niet noodzakelijk de applicatie-inhoud. Hij routeert of NAT het verkeer.

Bronzichtbaarheid hangt af van SNAT:

| Ontwerp | Wat ziet de interne doelserver? | Beheergevolg |
|---|---|---|
| Subnet router voert SNAT uit | Het bronadres van de subnet router. | Retourrouting is eenvoudig, maar individuele tailnetbronnen zijn minder zichtbaar in serverlogs. |
| Routing zonder SNAT | Het Tailscale-bronadres van de client. | Betere brontraceerbaarheid, maar het interne netwerk heeft een retourroute naar de tailnetrange nodig. |

### 18.2 Exit node

Een exit node routeert internetverkeer.

```text
Laptop -> VPN -> exit node -> internet
```

De exit node kan veel metadata zien:

- externe bestemmings-IP's;
- poorten;
- DNS als DNS via exit loopt;
- volume;
- timing.

Bij HTTPS ziet de exit node normaal niet de HTTP-inhoud, maar wel meer dan een willekeurig lokaal wifi-netwerk zou zien wanneer full tunnel actief is.

### 18.3 Enterprisevraag

Bij elke route moet je vragen:

| Vraag | Waarom |
|---|---|
| Wie beheert de router of exit node? | Die partij krijgt metadatazicht. |
| Welke logs worden bewaard? | Privacy en incident response. |
| Is NAT actief op de subnet router? | Bepaalt zichtbaarheid van echte bron-IP's. |
| Welke ACL's beperken toegang? | Voorkomt te breed bereik. |
| Is dit nodig voor alle users? | Least privilege. |

**In productie:** een subnet router en exit node zijn concentratiepunten voor
beschikbaarheid, capaciteit en metadata. Voorzie een eigenaar, monitoring, patching,
capaciteitsmeting en indien nodig redundantie. Een werkende lab-VM is nog geen
productieontwerp.

---

## 19. VPN en DNS

### 19.1 DNS kan veel verklappen

Zelfs als applicatieverkeer versleuteld is, kan DNS zichtbaar maken wat je probeert te bereiken.

Voorbeeld:

```text
netbox.voltlab.lan
admin.internal.example
git.company.local
```

Als die queries via een lokaal onbetrouwbaar netwerk gaan, lekt informatie.

### 19.2 MagicDNS en Split DNS

In Ch6 zag je:

| Feature | Doel |
|---|---|
| MagicDNS | tailnet-devices bij naam bereiken |
| Split DNS | specifieke interne zones via interne resolver |

Split DNS kan ervoor zorgen dat interne namen via de VPN-resolver gaan, terwijl gewone internetnamen normaal blijven werken.

### 19.3 DNS als troubleshooting- en privacylaag

DNS-problemen zijn niet alleen beschikbaarheidsproblemen. Ze zijn ook privacy- en securityproblemen.

Vraag altijd:

- welke resolver krijgt de query;
- gaat de query door de VPN;
- is de interne zone beperkt;
- mag DNS-verkeer naar de interne resolver;
- worden queries gelogd;
- kan een lokaal netwerk DNS manipuleren;
- wordt DNSSEC of DoH/DoT gebruikt waar relevant?

Gebruik DNS-tests in lagen:

| Test | Verwacht | Diagnose bij afwijking |
|---|---|---|
| Query naar MagicDNS-naam | Tailscale-adres van het juiste device. | MagicDNS, client DNS-configuratie of verkeerde naam. |
| Query naar interne Split DNS-zone | Antwoord van de bedoelde interne resolver. | Resolverroute, DNS-policy of zoneconfiguratie. |
| Verbinding naar het geresolveerde IP | Service bereikbaar volgens policy. | Routing, ACL/grant, host firewall of applicatie. |
| Query zichtbaar in lokale capture? | Interne query hoort bij correct Split DNS niet in klare tekst naar de lokale resolver te gaan. | DNS lekt buiten de bedoelde resolverroute. |

**Typische fout:** na een mislukte naamtest meteen de VPN-policy verruimen. Test eerst
het Tailscale-IP. Als dat werkt, zit het probleem waarschijnlijk in resolutie en niet in
het datapad naar de service.

Kernzin:

> Een VPN beschermt veel verkeer, maar DNS bepaalt vaak hoeveel naam-informatie zichtbaar blijft.

---

## 20. VPN en firewalls in enterprise-ontwerp

### 20.1 Firewall voor de VPN

Een firewall voor de VPN-endpoint bepaalt of clients de VPN kunnen bereiken.

Voor klassieke concentrators:

```text
internet -> firewall -> VPN concentrator
```

Voor mesh VPN:

```text
client -> outbound firewall -> internet/relay/peer
```

Je denkt dan aan:

| Controle | Functie | Typische fout |
|---|---|---|
| Gerichte inbound UDP naar een vaste gateway | Maakt het beheerde endpoint voorspelbaar bereikbaar. | Dezelfde brede inboundregel op alle gebruikersclients toepassen. |
| Outbound UDP en return traffic voor clients | Maakt directe peerpaden mogelijk. | Alleen UDP/41641 als bestemmingspoort toestaan terwijl dat standaard de lokale bronpoort is. |
| Outbound TCP/443 naar control plane en relay | Behoudt beheer en fallback. | Statische relay-IP's gebruiken zonder lifecycle. |
| Logging van allow en deny | Ondersteunt diagnose en incidentanalyse. | Payloadinspectie beloven terwijl alleen flowmetadata beschikbaar is. |
| Rate limiting en DDoS-bescherming | Beschermt publiek bereikbare vaste endpoints. | Legitieme UDP-flow zo streng beperken dat de tunnel instabiel wordt. |
| Gescheiden managementtoegang | Beperkt wijzigingsbevoegdheid. | VPN-datapad en firewallbeheer met dezelfde brede rol beheren. |

### 20.2 Firewall achter de VPN

Na de VPN is er nog altijd segmentatie nodig.

```text
VPN client -> firewall/ACL -> interne service
```

Een VPN-gebruiker mag niet automatisch alle VLANs bereiken.

Voorbeelden:

| Bron | Toegang |
|---|---|
| medewerker | intranet en helpdesk |
| IT-admin | management via jump host |
| externe partner | alleen partnerportaal |
| studentlab | alleen labdiensten |

### 20.3 Host firewall

Ook endpoints hebben firewalls.

Een server kan via VPN bereikbaar zijn, maar host firewall kan nog steeds bepalen:

- TCP/80 open;
- TCP/22 dicht;
- alleen bepaalde bron-IP's;
- logging van denied traffic;
- applicatiepoort beperkt tot VPN-interface.

Dat is defense in depth. Elke laag heeft een eigen bewijs:

| Laag | Positieve test | Negatieve test |
|---|---|---|
| Buitenste firewall | Verwachte VPN-handshake of relayverbinding verschijnt in flowlogs. | Onverwachte inbound servicepoort blijft geblokkeerd. |
| VPN-policy | Toegelaten identiteit bereikt de bedoelde service. | Niet-toegelaten identiteit of poort krijgt deny. |
| Host firewall | Service is bereikbaar via de bedoelde interface en bron. | Dezelfde service is niet onbedoeld via LAN of publiek adres bereikbaar. |
| Applicatie | Geldige applicatierequest slaagt. | Ongeldige identity of functie wordt door de applicatie geweigerd. |

Kernzin:

> VPN-toegang is een pad, geen toestemming tot alles achter dat pad.

---

## 21. Performance: waarom direct sneller is

### 21.1 Latency

Latency is de tijd die een pakket nodig heeft om heen en terug te gaan.

Direct:

```text
Belgie -> Nederland
```

Relayed:

```text
Belgie -> relay in Duitsland -> Nederland
```

Als de relay geografisch of netwerkmatig ongunstig ligt, stijgt latency.

Meet niet één pakket, maar een reeks. De eerste pongs kunnen de padopbouw bevatten en
zijn daardoor niet representatief voor de stabiele RTT.

### 21.2 Throughput

Throughput is hoeveel data per seconde door de verbinding kan.

Relays kunnen beperkt worden door:

- uplink van client A;
- relaycapaciteit;
- pad naar relay;
- pad van relay naar client B;
- packet loss;
- CPU op endpoints;
- MTU-problemen;
- QoS of rate limiting.

De laagste capaciteit in het volledige pad bepaalt de haalbare throughput. Een snelle
serververbinding compenseert geen trage laptopuplink.

```text
haalbare throughput <= minimum(
  uplink A,
  pad A-naar-tussenpunt,
  relaycapaciteit indien gebruikt,
  pad tussenpunt-naar-B,
  downlink B,
  endpoint-CPU en applicatiecapaciteit
)
```

### 21.3 Jitter en packet loss

Realtime verkeer zoals voice, video of remote desktop heeft last van:

- variabele vertraging;
- packet loss;
- extra hops;
- congestie.

Directe verbindingen zijn niet altijd perfect, maar ze vermijden minstens een extra tussenpunt.

### 21.4 MTU

VPN voegt overhead toe aan pakketten. Daardoor kan de effectieve MTU lager zijn.

Als MTU fout zit, zie je soms:

- kleine pings werken;
- grote transfers hangen;
- websites laden gedeeltelijk;
- TLS-sessies gedragen zich vreemd;
- sommige applicaties falen.

Voor de analyse in cursus en workshop is vooral dit belangrijk:

> VPN-performance gaat niet alleen over bandbreedte. Latency, relaygebruik, packet loss, MTU en CPU tellen mee.

### 21.5 Een eerlijke vergelijking maken

Wanneer je Devbit en eduroam/campusroam vergelijkt, verander je bij voorkeur slechts
één onafhankelijke variabele: het netwerk van de laptop. De Debian-server, service,
testduur en meettool blijven gelijk.

| Meetveld | Waarom noteren? |
|---|---|
| Datum en tijd | Netwerkbelasting verandert doorheen de dag. |
| Bron- en doelnetwerk | Bepaalt welke NAT- en firewallpaden betrokken zijn. |
| Connection type | Direct, peer relay en DERP zijn niet eerlijk vergelijkbaar zonder label. |
| RTT over meerdere samples | Toont centrale tendens en variatie. |
| Throughput en testduur | Een korte piek is geen duurzame capaciteit. |
| Packet loss en jitter | Verklaren slechte realtime-ervaring ondanks redelijke throughput. |
| CPU-belasting | Voorkomt dat je een endpointbottleneck als netwerkprobleem benoemt. |
| MTU-gerelateerde observatie | Verklaart waarom kleine tests werken en grote stromen falen. |

**Kernzin:**

> Een performancemeting zonder padtype en meetcontext is een getal, geen diagnose.

---

## 22. Port forwarding voor hogere snelheden

### 22.1 Wanneer helpt het?

Port forwarding helpt vooral wanneer een belangrijk endpoint anders vaak relayed is.

Voorbeelden:

- subnet router thuis of in lab;
- exit node;
- site-to-site gateway;
- server die vaak door meerdere clients gebruikt wordt.

Als dat endpoint direct bereikbaar wordt via UDP, kunnen veel peers sneller verbinden.

### 22.2 Voorbeeldscenario

Zonder port forwarding:

```text
Student laptop == DERP relay == subnet router == labnet
```

Met port forwarding op de router voor de subnet router:

```text
Student laptop == direct UDP == subnet router == labnet
```

De tweede situatie kan sneller zijn, omdat de relay uit het datapad verdwijnt.

### 22.3 Wanneer helpt het niet?

Port forwarding helpt niet altijd.

| Situatie | Waarom niet |
|---|---|
| Clientnetwerk blokkeert alle UDP | De andere kant kan nog steeds niet direct praten. |
| Endpoint zit achter CGNAT zonder publiek IP | Je kan de ISP-NAT niet forwarden. |
| Firewall blokkeert outbound naar die UDP-poort | Direct pad faalt. |
| Performanceprobleem zit in CPU of applicatie | Netwerkpad is niet de bottleneck. |
| Relay was al snel genoeg | Verschil is beperkt. |

### 22.4 Securitychecklist

Voor je port forwarding inzet:

| Controle | Vraag |
|---|---|
| Endpointrol | Is dit een vaste gateway of serverrol? |
| Poort | Is alleen de noodzakelijke UDP-poort open? |
| Host firewall | Accepteert alleen VPN-verkeer op die poort? |
| Updates | Is de VPN-software actueel? |
| Logging | Kan je misbruik of scans detecteren? |
| Documentatie | Staat de forwarding in het netwerkdocument? |
| Review | Is de forwarding nog nodig na het labo/project? |

Belangrijke gedachte:

> Port forwarding is een performance-optimalisatie en beheerkeuze, geen vervanging voor VPN-policy.

### 22.5 Beslissingsmodel

```text
Is de applicatie traag?
  |
  +-- nee --> geen firewallwijziging nodig
  |
  +-- ja --> is het pad blijvend relayed?
              |
              +-- nee --> onderzoek loss, MTU, CPU, wifi en applicatie
              |
              +-- ja --> is één endpoint vaste beheerde infrastructuur?
                          |
                          +-- nee --> liever geen handmatige forwarding
                          |
                          +-- ja --> publiek IP en beheer over upstream NAT?
                                      |
                                      +-- nee --> peer relay/hosting/ander pad overwegen
                                      |
                                      +-- ja --> minimale UDP-opening ontwerpen,
                                                  risico beoordelen en voor/na testen
```

**Negatieve test na optimalisatie:** controleer dat TCP/22 of een andere niet-toegelaten
service nog steeds geweigerd wordt. Een sneller datapad mag de autorisatiegrens niet
veranderen.

---

## 23. Typische misverstanden

### 23.1 "VPN maakt mij anoniem"

Niet noodzakelijk.

Een VPN kan je lokale netwerk minder zicht geven op inhoud en bestemmingen, vooral bij full tunnel. Maar de VPN-provider, exit node of organisatie kan juist meer metadata zien. Websites kunnen je nog herkennen via login, cookies, browserfingerprinting of accountgedrag.

Betere formulering:

> Een VPN verschuift vertrouwen en zichtbaarheid. Het maakt je niet automatisch anoniem.

### 23.2 "Als het versleuteld is, is het veilig"

Niet genoeg.

Encryptie beschermt onderweg. Maar als iedereen via de tunnel overal naartoe mag, is het ontwerp nog steeds slecht.

Betere formulering:

> Encryptie zonder least privilege beschermt de transportlaag, maar niet het toegangsmodel.

### 23.3 "Relay betekent onveilig"

Niet noodzakelijk.

Bij end-to-end versleutelde VPN's transporteert een relay versleutelde pakketten. De relay kan metadata zien, maar niet automatisch inhoud.

Betere formulering:

> Relaygebruik is meestal een performance- en metadata-vraag, niet automatisch een inhoudelijke securitybreuk.

### 23.4 "Direct is altijd beter"

Meestal beter voor performance, maar niet altijd beleidsmatig.

Sommige organisaties willen verkeer bewust via gecontroleerde gateways sturen voor logging, DLP, egress filtering of compliance. Directe mesh-connectiviteit moet dan passen binnen het securitybeleid.

Betere formulering:

> Direct is vaak technisch sneller, maar enterprisebeleid bepaalt of het gewenst is.

### 23.5 "De firewall is lastig, dus we zetten alles open"

Dit is precies de verkeerde reflex.

Een firewall die VPN-performance beperkt, vraagt analyse:

- welke verbinding is relayed;
- welke UDP-poort of bestemming ontbreekt;
- welke endpointrol heeft vaste bereikbaarheid nodig;
- welke logging is nodig;
- welke minimale opening lost het probleem op?

Niet:

```text
allow any any
```

Maar:

```text
laat noodzakelijke outbound UDP of specifieke forwarding toe voor de juiste gateway
```

---

## 24. Analysevragen voor cases

Naast de workshop gebruik je deze cases om situaties te analyseren die je niet veilig of betrouwbaar in het campusnetwerk kan afdwingen. Bij elke case vertrek je van dezelfde vragen.

### 24.1 Basisvragen

| Vraag | Waarom |
|---|---|
| Welke endpoints praten met elkaar? | Bepaalt het pad. |
| Is de verbinding direct of relayed? | Bepaalt performanceanalyse. |
| Welke NAT/firewall zit aan elke kant? | Bepaalt traversalkansen. |
| Welke poorten en protocollen zijn nodig? | Bepaalt firewallontwerp. |
| Welke inhoud is versleuteld? | Bepaalt security. |
| Welke metadata blijft zichtbaar? | Bepaalt privacy en logging. |
| Wie beheert relay, exit node of subnet router? | Bepaalt vertrouwen. |
| Welke policy beperkt toegang? | Bepaalt autorisatie. |

### 24.2 Case 1: hotelwifi

Situatie:

Een medewerker gebruikt hotelwifi. Tailscale werkt, maar de verbinding naar een interne server is traag.

Analyse:

- mogelijk blokkeert hotelwifi UDP;
- verbinding valt terug op DERP;
- inhoud blijft versleuteld;
- hotel ziet VPN/relayverkeer, timing en volume;
- directe performance is niet haalbaar zolang het hotelnetwerk UDP blokkeert;
- oplossing kan zijn: ander netwerk, mobiele hotspot, of accepteren van relay.

Sterke conclusie:

> De VPN is niet inhoudelijk onveilig omdat DERP gebruikt wordt, maar performance is lager omdat directe UDP-connectiviteit niet lukt.

### 24.3 Case 2: subnet router achter CGNAT

Situatie:

Een lab-subnet router staat thuis bij een student achter CGNAT. Verkeer werkt via relay, maar grote transfers zijn traag.

Analyse:

- handmatige port forwarding op de thuisrouter helpt niet door ISP-CGNAT;
- directe inbound bereikbaarheid ontbreekt;
- NAT traversal kan soms nog werken, maar niet gegarandeerd;
- relay blijft fallback;
- vaste infrastructuur met publiek IP zou beter zijn voor performance;
- alternatief: host subnet router in lab/cloud met betere UDP-bereikbaarheid.

Sterke conclusie:

> De bottleneck zit niet in VPN-encryptie alleen, maar in het feit dat het endpoint niet rechtstreeks bereikbaar is door CGNAT en daardoor vaak relayed werkt.

### 24.4 Case 3: bedrijfsfirewall laat alleen TCP/443 toe

Situatie:

Een organisatie laat uitgaand alleen TCP/443 toe. VPN-connectiviteit werkt nog via relay, maar direct peer-to-peer werkt niet.

Analyse:

- outbound UDP is nodig voor directe WireGuard-verbindingen;
- relay kan via toegestane webachtige paden werken;
- performance is lager;
- beheerder moet afwegen of specifieke outbound UDP toegestaan kan worden;
- logging en egress policy blijven belangrijk.

Sterke conclusie:

> De firewall verhindert directe VPN-data plane, niet noodzakelijk de volledige VPN-connectiviteit.

### 24.5 Case 4: netwerkbeheerder wil weten wat hij kan loggen

Situatie:

Een schoolnetwerk wil VPN-gebruik monitoren zonder inhoud te inspecteren.

Zichtbaar:

- brondevice op het LAN;
- tijdstip en volume;
- bestemming van relay/control-plane;
- UDP toegestaan of geblokkeerd;
- firewall hits;
- DNS als die lokaal gebeurt.

Niet zichtbaar:

- interne applicatie-inhoud binnen de VPN;
- SSH-commando's;
- HTTP-paden;
- bestanden binnen de tunnel.

Sterke conclusie:

> Logging kan nuttige metadata geven voor beheer en incidentanalyse, maar inhoudelijke inspectie van end-to-end VPN-verkeer is niet realistisch zonder endpointcontrole of TLS/VPN-breuk.

---

## 25. Ontwerpprincipes

### 25.1 Voor security

| Principe | Concrete ontwerpbeslissing | Controle |
|---|---|---|
| Vertrouw het onderliggende netwerk niet | Bescherm peerverkeer cryptografisch, ook op intern of campusnetwerk. | Buitenste capture bevat geen interne testpayload. |
| Gebruik een modern en ondersteund VPN-protocol | Kies onderhouden clients en een duidelijk sleutel- en updateproces. | Versies, releasebeleid en protocolarchitectuur zijn gedocumenteerd. |
| Bescherm private keys | Laat private sleutels op het endpoint en beveilig het endpoint zelf. | Geen secrets in screenshots, Git of gedeelde verslagen. |
| Bescherm de control plane | Gebruik MFA, beperkte adminrollen en auditlogging. | Adminlogin en configuratiewijziging zijn traceerbaar. |
| Pas least privilege toe | Beperk bron, bestemming en service met grants/ACL's, tags en rollen. | Allow-test én deny-test slagen. |
| Vermijd `*:*` als eindontwerp | Maak uitzonderingen tijdelijk, beargumenteerd en reviewbaar. | Policyreview toont geen onnodig brede regel. |
| Beheer de device lifecycle | Verwijder verlopen, verloren of niet meer beheerde devices en keys. | Offboardingtest en periodieke inventaris. |
| Gebruik defense in depth | Combineer VPN-policy, segmentatie, host firewall en applicatieauthenticatie. | Elke laag heeft een afzonderlijke positieve en negatieve test. |

### 25.2 Voor performance

| Principe | Concrete ontwerpbeslissing | Controle |
|---|---|---|
| Meet vóór je wijzigt | Registreer connection type, RTT, loss en throughput. | Baseline bevat tijd, endpoints, netwerken en testduur. |
| Geef direct UDP een eerlijke kans | Laat noodzakelijke egress en stateful return toe waar beleid dit verantwoordt. | `netcheck`, `ping` en flowlogs ondersteunen dezelfde conclusie. |
| Optimaliseer vaste infrastructuur gericht | Overweeg forwarding of peer relay voor subnet router, exit node of gateway. | Voor/na-meting toont een echte verbetering. |
| Plaats routers dicht bij resources | Vermijd onnodige omwegen tussen VPN-ingang en doelservice. | Route- en latencyanalyse tonen het werkelijke pad. |
| Onderzoek MTU en loss | Baseer diagnose niet alleen op een kleine ping. | Kleine én grotere pakketten of echte transfers worden getest. |
| Monitor endpointcapaciteit | CPU, wifi en applicatiesnelheid kunnen de bottleneck zijn. | Netwerkconclusie vermeldt uitgesloten alternatieve oorzaken. |
| Documenteer publieke bereikbaarheid | Koppel eigenaar, doel, poort, risico en reviewdatum aan de regel. | Firewallreview kan aantonen waarom de uitzondering nog bestaat. |

### 25.3 Voor privacy en governance

| Principe | Concrete ontwerpbeslissing | Controle |
|---|---|---|
| Beschrijf metadata per observator | Onderscheid LAN, ISP, control plane, relay, subnet router, exit node en endpoint. | Zichtbaarheidstabel benoemt inhoud, metadata en inferenties apart. |
| Beperk toegang en retentie van logs | Verzamel wat nodig is voor beheer en incident response, met eigenaar en bewaartermijn. | Rollen en retentiebeleid zijn gedocumenteerd. |
| Ontwerp DNS bewust | Routeer interne zones naar de bedoelde resolver en beperk onnodige naamlekkage. | IP-, naam- en capturetest geven een consistent resultaat. |
| Kies split of full tunnel op basis van beleid | Bepaal welke bestemmingen centraal moeten worden gestuurd en gelogd. | IPv4 en IPv6 volgen de bedoelde route. |
| Benoem de vertrouwensverschuiving | Leg uit wie de exit node, subnet router en relay beheert. | Gebruikersdocumentatie belooft geen absolute anonimiteit. |
| Minimaliseer beheerzicht | Geef alleen bevoegde rollen toegang tot device-, flow- en auditmetadata. | Toegangsreview en auditlog tonen gebruik van de logs. |

### 25.4 Van observatie naar ontwerpbeslissing

Een professionele conclusie bevat meer dan "het werkt" of "het is traag".

```text
Observatie:
  tailscale ping blijft via DERP(fra); mediane RTT is hoger op campusroam.

Verklaring:
  direct UDP lukt voor dit peerpaar niet; DERP blijft daarom in het datapad.

Risico:
  applicatie-inhoud blijft end-to-end versleuteld, maar relaymetadata en extra
  latency blijven aanwezig.

Beslissing:
  voor een mobiele studentlaptop geen inbound opening maken; relay aanvaarden.
  voor een vaste productiegateway eventueel gerichte UDP-bereikbaarheid of een
  beheerde peer relay onderzoeken.

Bewijs na wijziging:
  connection type, RTT, throughput, firewalllogs en negatieve servicetest.
```

Deze structuur dwingt je om feiten, verklaring, afweging en advies uit elkaar te
houden.

---

## 26. Controle- en reflectievragen

### 26.1 Begrip

1. Waarom kan een VPN veilig zijn op een onbekend wifi-netwerk?
2. Wat is het verschil tussen encryptie en integriteit?
3. Waarom is authenticatie niet hetzelfde als autorisatie?
4. Waarom gebruikt WireGuard UDP?
5. Wat is een NAT mapping?
6. Waarom blokkeren stateful firewalls vaak nieuwe inkomende verbindingen?
7. Wat probeert NAT traversal te bereiken?
8. Waarom lukt NAT traversal niet altijd?
9. Wat is DERP?
10. Waarom is DERP meestal trager dan direct verkeer?

### 26.2 Analyse

1. Een VPN werkt, maar `tailscale status` toont relay. Welke oorzaken onderzoek je?
2. Een subnet router achter CGNAT is traag. Waarom helpt port forwarding op de thuisrouter mogelijk niet?
3. Een netwerkbeheerder zegt dat hij "alles kan zien omdat jij zijn wifi gebruikt". Wat klopt daar wel en niet aan?
4. Een gebruiker denkt dat full tunnel anoniem maakt. Hoe nuanceer je dat?
5. Een firewallbeheerder wil alle UDP blokkeren. Welke impact heeft dat op mesh VPN?
6. Een admin wil UPnP inschakelen voor betere performance. Welke risico's bespreek je?
7. Een relaybeheerder ziet veel verkeer tussen twee devices. Welke inhoud ziet hij normaal niet?
8. Een VPN-policy laat `10.20.0.0/16:*` toe. Waarom is dat een autorisatieprobleem, ook als encryptie sterk is?

### 26.3 Ontwerp

1. Wanneer zou je port forwarding wel toestaan voor een VPN-endpoint?
2. Welke logging is nuttig zonder privacy onnodig te schenden?
3. Hoe ontwerp je VPN-toegang voor externe partners?
4. Wanneer kies je split tunnel en wanneer full tunnel?
5. Welke maatregelen neem je om relaygebruik te verminderen zonder security te verzwakken?

### 26.4 Voorbereiding op de workshop

Voorzie voor elke test vooraf een verwachting. Zo vermijd je dat je achteraf elke
uitkomst als "normaal" beschrijft.

| Onderzoeksvraag | Positieve test | Negatieve of contrasterende test | Zinvol bewijs |
|---|---|---|---|
| Is de bedoelde HTTP-service bereikbaar? | Request naar het Tailscale-adres en de juiste poort slaagt. | Request naar een niet-toegelaten poort faalt. | Commando, tijdstip, statuscode/fout en relevante policy. |
| Wordt een direct pad gebruikt? | Meerdere `tailscale ping`-resultaten eindigen via een `ip:poort`. | Vergelijk met een netwerk waar het pad relayed blijft. | Volledige pingreeks en `tailscale status`. |
| Welke NAT-eigenschappen zijn zichtbaar? | `tailscale netcheck` rapporteert UDP-, mapping- en relayinformatie. | Herhaal na wissel van laptopnetwerk. | Beide outputs met bronnetwerk en tijdstip. |
| Is de buitenkant versleuteld? | Capture op fysieke interface toont buitenste VPN/relayflow zonder interne payload. | Capture op Tailscale-interface toont het binnenste testverkeer. | Twee beperkte captures met gemarkeerde interfaces en filters. |
| Werkt split tunnel? | Tailscale-doel gebruikt overlayroute. | Publiek doel gebruikt zonder exit node de gewone default route. | Routetabel, doeladressen en capture/route-output. |
| Werkt MagicDNS? | Naam resolveert en service is via die naam bereikbaar. | IP-test werkt terwijl een bewust foutieve naam faalt. | Resolveroutput afzonderlijk van applicatietest. |
| Blijft least privilege gelden? | Toegelaten service werkt. | Niet-toegelaten service of bron wordt geweigerd. | Allow- en deny-resultaat plus relevante log of policyregel. |

**Privacy:** maskeer publieke IP-adressen, usernames, device-ID's en andere gegevens
die niet nodig zijn voor het leerbewijs. Verwijder geen context die nodig is om de
technische conclusie te beoordelen.

---

## 27. Samenvatting

Een VPN is veilig over een onbekend netwerk omdat de security niet afhankelijk is van dat netwerk. Moderne VPN's gebruiken cryptografie om vertrouwelijkheid, integriteit en authenticatie te bieden. Het netwerk onderweg mag onbetrouwbaar zijn: het kan pakketten zien, vertragen, blokkeren of omleiden, maar het mag de inhoud niet kunnen lezen of ongemerkt aanpassen.

Toch is VPN-security meer dan encryptie. Autorisatie, devicebeheer, tags, ACL's, DNS, lifecycle en logging bepalen of het ontwerp professioneel is. Een tunnel die iedereen naar alles laat, is nog steeds een slecht ontwerp.

NAT en stateful firewalls maken directe peer-to-peer VPN-connectiviteit moeilijker. NAT traversal probeert via endpoint discovery, hole punching en soms port mapping toch een direct UDP-pad te vinden. Als dat niet lukt, kan verkeer via een relay zoals DERP lopen. Dat is meestal trager, maar bij end-to-end encryptie niet automatisch inhoudelijk onveilig.

Port forwarding of expliciete UDP-openstelling kan performance verbeteren voor vaste endpoints zoals subnet routers, exit nodes of site-to-site gateways. Dat moet wel bewust gebeuren, met beperkte poorten, host firewall, updates, logging en documentatie.

Een netwerkbeheerder onderweg ziet vaak metadata: IP's, poorten, timing, volume, DNS afhankelijk van configuratie, en mogelijk dat VPN of relay gebruikt wordt. Hij ziet normaal niet de inhoud binnen de versleutelde tunnel. De VPN-beheerder ziet andere metadata, zoals devices, users, tags, routes en policy. VPN verschuift vertrouwen en zichtbaarheid; het maakt niet automatisch anoniem.

Rode draad:

```text
untrusted network -> encrypted tunnel -> NAT traversal -> direct or relay -> policy -> visibility -> performance
```

Slotgedachte:

> Een professionele VPN-ontwerper kan niet alleen zeggen dat de tunnel veilig is, maar ook uitleggen wat beschermd wordt, wat zichtbaar blijft, waarom een verbinding direct of relayed loopt, en welke firewallkeuze daarbij hoort.

---

## 28. Bronnen voor verdieping

- [Tailscale Docs - Connection types](https://tailscale.com/docs/reference/connection-types)
- [Tailscale Docs - Control and data planes](https://tailscale.com/docs/concepts/control-data-planes)
- [Tailscale Docs - DERP servers](https://tailscale.com/docs/reference/derp-servers)
- [Tailscale Docs - Firewall ports](https://tailscale.com/docs/reference/faq/firewall-ports)
- [Tailscale Blog - How NAT traversal works](https://tailscale.com/blog/how-nat-traversal-works)
- [WireGuard - Protocol and cryptography](https://www.wireguard.com/protocol/)
