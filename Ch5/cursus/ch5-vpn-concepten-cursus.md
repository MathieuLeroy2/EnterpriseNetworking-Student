# Hoofdstuk 5 - VPN-concepten

## 1. Inleiding

In hoofdstuk 4 stonden beschikbaarheid en veilig beheer centraal. Je leerde onder meer
dat een beheerpad gecontroleerd, gelogd en herstelbaar moet zijn. In dit hoofdstuk
verplaatsen we dat beheerpad en andere interne toegang buiten de fysieke organisatie.

De centrale vraag wordt:

> Hoe geef je gebruikers, beheerders, filialen of partners toegang tot interne
> systemen zonder het interne netwerk rechtstreeks op het internet te publiceren?

Dat probleem komt in bijna elke enterprise-omgeving voor.

| Situatie | Concrete behoefte | Risico zonder doordacht ontwerp |
|---|---|---|
| medewerker werkt thuis | intranet of ticketing bereiken | interne diensten worden te breed gepubliceerd |
| IT-beheerder grijpt remote in | jump server of monitoring bereiken | beheerinterfaces worden een internetdoelwit |
| consultant ondersteunt een project | één projectdienst bereiken | tijdelijke toegang wordt brede, permanente toegang |
| filiaal gebruikt centrale diensten | twee private netwerken verbinden | de sites vertrouwen elkaar onbedoeld volledig |
| cloudserver praat met on-premises server | private applicatieflow opzetten | gevoelige backendpoorten worden publiek gemaakt |

Een **Virtual Private Network** of **VPN** maakt gecontroleerde private communicatie
mogelijk over een netwerk dat je niet beheert, meestal het internet. De term *private*
betekent niet dat elk verbonden toestel automatisch vertrouwd is. Ze betekent dat er
een logisch afgeschermd communicatiepad bestaat.

Een professionele VPN-keuze beantwoordt minstens deze vragen:

| Ontwerpvraag | Waarom moet je dit vooraf bepalen? |
|---|---|
| Wie krijgt toegang? | een identiteit moet aan een zakelijke nood gekoppeld zijn |
| Vanaf welk toestel? | een gekende gebruiker op een onbekend toestel blijft een risico |
| Naar welke dienst en poort? | netwerkbrede toegang is zelden nodig |
| Via welk pad loopt het verkeer? | routes bepalen of verkeer lokaal, via VPN of via een exit gaat |
| Hoe wordt toegang ingetrokken? | accounts en toestellen blijven anders na vertrek actief |
| Welke gebeurtenissen worden gelogd? | zonder bewijs kan je fouten en misbruik moeilijk onderzoeken |
| Wat gebeurt er bij uitval? | remote werk of beheer kan van één gateway afhankelijk worden |

In de workshop gebruiken we **Tailscale**. Daarmee bouwen we een kleine overlay tussen
een laptop en een Debian-VM. Dat maakt moderne VPN-concepten zichtbaar: identiteit,
device-inventory, MagicDNS, split tunneling en een exit node.

De workshop is bewust klein. In een productieomgeving horen daar onder meer centrale
identity, MFA, expliciete access policy, monitoring, formele offboarding en redundantie
bij. De policylaag wordt in hoofdstuk 6 verder uitgewerkt.

Kernidee:

> Een VPN is een gecontroleerd toegangspad, geen bewijs dat de gebruiker of het toestel
> onbeperkt vertrouwd mag worden.

De rode draad door dit hoofdstuk is:

```text
identiteit -> toestel -> tunnel -> route -> policy -> test -> logging -> lifecycle
```

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. uitleggen welk probleem een VPN in een enterprise-omgeving oplost;
2. verklaren waarom het internet transport levert maar geen vertrouwen;
3. tunnel, encapsulatie, encryptie, authenticatie en integriteit onderscheiden;
4. remote-access- en site-to-site-VPN vergelijken;
5. client-based en clientless remote access onderscheiden;
6. full tunnel en split tunnel uitleggen en voor een scenario kiezen;
7. de gevolgen van VPN-adressering en subnet overlap analyseren;
8. de heenweg en terugweg van VPN-verkeer onderzoeken;
9. VPN-toegang koppelen aan securityzones en firewallbeleid;
10. de rol van interne DNS, split DNS en MagicDNS uitleggen;
11. externe partners toegang geven volgens least privilege en lifecyclebeheer;
12. Tailscale plaatsen als identity-aware overlay op basis van WireGuard;
13. control plane, data plane, directe verbinding en relay onderscheiden;
14. user identity, device identity en device lifecycle uit elkaar houden;
15. een exit node onderscheiden van een subnet router;
16. de risico's van VPN-gebaseerde managementtoegang uitleggen;
17. typische fouten systematisch lokaliseren;
18. een testmatrix met positieve, negatieve en bewijstesten opstellen;
19. een VPN-policy eerst in mensentaal formuleren;
20. labkeuzes onderscheiden van vereisten voor productie;
21. VPN-resultaten documenteren zonder credentials of secrets te lekken.

---

## 3. Waarom VPN?

Een intern systeem heeft meestal een private IP-adresruimte en staat achter één of meer
firewalls. Dat is een bewuste grens: een fileserver, hypervisor of managementinterface
hoort niet rechtstreeks vanaf elk internetadres bereikbaar te zijn.

Toch stopt de bedrijfsbehoefte niet aan de rand van het gebouw. Een VPN maakt het
mogelijk om een gecontroleerde route over die rand heen te bouwen.

| Use case | VPN-endpoints | Minimale gewenste flow |
|---|---|---|
| thuiswerker | laptop en VPN-gateway/overlay-node | medewerker naar intranet op TCP 443 |
| remote beheer | adminlaptop en bedrijfsomgeving | admin naar jump server op de beheerpoort |
| filiaal | router/firewall op beide locaties | filiaalapplicatie naar centrale server |
| cloudkoppeling | cloudgateway en on-premises gateway | applicatieserver naar databasepoort |
| partnerondersteuning | partnerclient en afgeschermde toegang | consultant naar één supportdoel |

### 3.1 Welke slechte alternatieven vermijdt een VPN?

Een VPN is niet altijd de enige oplossing, maar voorkomt vaak dat organisaties interne
diensten rechtstreeks publiceren.

| Zwakke aanpak | Waarom riskant? | Betere richting |
|---|---|---|
| elke interne dienst via port forwarding publiceren | elke dienst krijgt een publiek aanvalsoppervlak | private toegang via VPN of applicatieproxy |
| RDP/SSH rechtstreeks op internet | beheerprotocol wordt continu gescand en aangevallen | VPN naar een streng beveiligde jump server |
| gedeeld VPN-account gebruiken | acties zijn niet aan één persoon toe te schrijven | persoonlijke identiteit, MFA en logging |
| één brede partnerregel maken | compromis bij partner geeft groot lateraal bereik | aparte partnerzone en minimale flows |
| tijdelijke toegang niet registreren | niemand weet wanneer ze moet verdwijnen | eigenaar, einddatum en periodieke review |

Een VPN maakt een zwakke achterliggende dienst niet automatisch veilig. Als een
fileserver verouderd is of elke aangemelde gebruiker administrator maakt, blijft dat
probleem bestaan zodra de tunnel toegang geeft.

Waarom belangrijk?

> De VPN beperkt hoe je een dienst bereikt. De dienst en haar eigen autorisatie blijven
> verantwoordelijk voor wat een gebruiker na de verbinding kan doen.

### 3.2 VPN, proxy of gepubliceerde applicatie?

Niet elke remote gebruiker heeft netwerktoegang nodig.

| Behoefte | Mogelijke oplossing | Ontwerpoverweging |
|---|---|---|
| één moderne webapp gebruiken | reverse proxy of identity-aware application proxy | beperkt toegang tot de applicatie, niet tot een subnet |
| meerdere interne protocollen gebruiken | remote-access-VPN | flexibeler, maar vergroot het bereik van de client |
| twee netwerken permanent koppelen | site-to-site-VPN | routes en policies gelden voor hele netwerken |
| een beheerhandeling uitvoeren | VPN naar jump server | houdt managementinterfaces uit de gewone VPN-zone |

De juiste vraag is dus niet: *Welke VPN installeren we?* De juiste eerste vraag is:

> Welke concrete communicatie moet mogelijk worden, en welk minimaal toegangspad past
> daarbij?

Kernzin:

> Start bij de noodzakelijke flow en kies daarna de toegangstechniek.

---

## 4. Het internet is transport, geen trust zone

Het internet vervoert pakketten tussen de VPN-endpoints. Je beheert de tussenliggende
routers, providers, wifi-netwerken en NAT-apparaten niet. Daarom mag je van dat pad geen
vertrouwelijkheid, integriteit of betrouwbare identiteit verwachten.

De VPN moet zelf verschillende zekerheden toevoegen.

| Zekerheid | Vraag | Technische invulling |
|---|---|---|
| vertrouwelijkheid | kan een tussenpartij de inhoud lezen? | encryptie |
| integriteit | werd het pakket onderweg gewijzigd? | cryptografische integriteitscontrole |
| peer-authenticatie | praat ik met het bedoelde tunnelendpoint? | sleutels, certificaten of protocolidentiteit |
| user-authenticatie | welke mens vraagt toegang? | identity provider, wachtwoord, passkey of MFA |
| autorisatie | welke flow mag die identiteit gebruiken? | firewall-, VPN- of applicatiepolicy |
| auditability | kan ik achteraf reconstrueren wat gebeurde? | tijdgesynchroniseerde logs en inventaris |

### 4.1 Verbonden is niet hetzelfde als vertrouwd

Een veelgemaakte denkfout is:

> De gebruiker is met de VPN verbonden en zit dus veilig binnen.

Een VPN-verbinding bewijst hoogstens dat bepaalde authenticatievoorwaarden zijn
doorlopen en dat een beveiligd pad bestaat. Ze bewijst niet dat:

| Niet automatisch bewezen | Praktisch risico |
|---|---|
| het toestel malwarevrij is | malware gebruikt de toegestane netwerkflow mee |
| de gebruiker alle interne diensten nodig heeft | te brede toegang maakt laterale beweging mogelijk |
| de account nog bij een actieve medewerker hoort | slechte offboarding laat oude toegang bestaan |
| de achterliggende applicatie veilig is | een kwetsbare dienst blijft kwetsbaar via de tunnel |
| alle verkeer via de VPN loopt | bij split tunnel blijft publiek verkeer lokaal |

Een modern ontwerp behandelt VPN daarom als een aparte bronzone, bijvoorbeeld
`VPN-Staff`, `VPN-IT` of `VPN-Partner`. Vanuit die zone worden alleen noodzakelijke
flows toegelaten.

Kernzin:

> Een VPN verandert het pad van het verkeer; vertrouwen moet nog altijd expliciet
> worden toegekend.

---

## 5. Wat is een VPN-tunnel?

Een VPN-tunnel is een logisch communicatiepad tussen twee endpoints. Verkeer dat door
de tunnel moet, wordt door het VPN-protocol verwerkt en over een bestaand netwerk
vervoerd.

```text
origineel pakket
[ intern bron-IP | intern doel-IP | payload ]
                  |
                  | VPN verwerkt en beschermt
                  v
transport over internet
[ buitenste header | versleutelde VPN-data ]
                  |
                  | VPN-peer controleert en pakt uit
                  v
origineel pakket naar de bestemming
```

Dit wordt vaak **encapsulatie** genoemd: het oorspronkelijke pakket krijgt de vorm die
nodig is om het over het transportnetwerk te sturen. Welke headers precies zichtbaar
blijven, hangt van het protocol en de implementatie af.

### 5.1 Wat beschermt de tunnel wel en niet?

| Eigenschap | Beschermd? | Nuance |
|---|---|---|
| inhoud van het getunnelde verkeer | normaal wel | alleen tussen de VPN-endpoints |
| identiteit van de VPN-endpoints op internet | niet volledig verborgen | publieke adressen van endpoints of relays kunnen zichtbaar zijn |
| hoeveelheid en timing van verkeer | niet verborgen | verkeerspatronen blijven observeerbaar |
| verkeer buiten de geselecteerde routes | nee | bij split tunnel gaat dat verkeer niet door de VPN |
| data na het tunnelendpoint | niet automatisch | vanaf een subnet router kan verkeer verder over het LAN lopen |
| rechten in de doelapplicatie | nee | applicatieautorisatie blijft afzonderlijk nodig |

### 5.2 Welke endpoints bestaan er?

| Endpointtype | Voorbeeld | Waar eindigt de tunnel? |
|---|---|---|
| client naar gateway | thuislaptop naar bedrijfsfirewall | aan de laptop en centrale gateway |
| gateway naar gateway | filiaalrouter naar hoofdkantoorrouter | aan beide netwerkranden |
| device naar device | laptop naar server met Tailscale | rechtstreeks op beide devices |
| device naar subnet router | laptop naar router voor een legacy-LAN | op client en subnet router |
| device naar exit node | laptop naar gecontroleerde internetuitgang | op client en exit node |

Controleer:

- welke endpoint het pakket ontsleutelt;
- welke route bepaalt dat het pakket de tunnel gebruikt;
- welke policy de flow toelaat;
- welk netwerksegment na het tunnelendpoint nog volgt.

Kernzin:

> Je kan een VPN-pad pas beveiligen wanneer je weet waar de tunnel begint, waar ze
> eindigt en welke weg het pakket daarna nog aflegt.

---

## 6. Encryptie, authenticatie en integriteit

Deze begrippen vullen elkaar aan, maar betekenen niet hetzelfde.

| Principe | Doel | Wat gaat mis als dit ontbreekt? |
|---|---|---|
| encryptie | inhoud onleesbaar maken voor tussenpartijen | verkeer kan worden afgeluisterd |
| endpoint-authenticatie | bewijzen met welke VPN-peer je praat | een aanvaller kan zich als gateway voordoen |
| gebruikersauthenticatie | bewijzen welke gebruiker toegang vraagt | gedeelde of gestolen identiteit blijft onduidelijk |
| integriteit | wijziging onderweg detecteren | pakketten kunnen ongemerkt worden gemanipuleerd |
| autorisatie | bepalen wat een geldige identiteit mag | een correcte login krijgt mogelijk te veel toegang |

Een versleutelde tunnel naar de verkeerde peer is niet betrouwbaar. Een correct
geauthenticeerde gebruiker met een regel `allow any` is evenmin een veilig ontwerp.

### 6.1 Gebruiker en toestel authenticeren

Bij remote access zijn minstens twee identiteiten relevant:

```text
menselijke identiteit:  "Dit is Alice."
device-identiteit:       "Dit is de beheerde laptop van Alice."
```

| Situatie | Wat weet je? | Resterend risico |
|---|---|---|
| gekende gebruiker, onbekend toestel | accountcontrole is gelukt | privétoestel kan onveilig of onbeheerd zijn |
| gekend toestel, gestolen account | device is geregistreerd | aanvaller gebruikt geldige usercredentials |
| gebruiker en toestel gekend | twee contexten zijn beschikbaar | policy en endpointsecurity blijven nodig |
| gedeeld account | identiteit is niet persoonlijk | audit en offboarding zijn zwak |

Mogelijke controles zijn SSO, MFA, device approval, certificaten, posture checks,
groepslidmaatschap en tijdsgebonden toegang. Niet elke omgeving gebruikt al die
controles, maar gevoeliger toegang vraagt sterkere zekerheid.

### 6.2 Waarom MFA belangrijk is

MFA beperkt vooral het risico dat een gestolen wachtwoord alleen voldoende is.

| Aanval of fout | Wat MFA beperkt | Wat MFA niet oplost |
|---|---|---|
| wachtwoordlek | aanvaller mist normaal de tweede factor | sessiediefstal na een geldige login |
| password spraying | één geraden wachtwoord geeft niet meteen toegang | zwakke of vermoeiende pushflows |
| hergebruikt wachtwoord | extra factor blokkeert eenvoudige reuse | malware op een reeds aangemeld toestel |
| vertrokken medewerker | niets als account actief blijft | lifecycle en accountdeactivatie blijven nodig |

Voor beheer- en partnertoegang is MFA meestal een minimale maatregel. In productie moet
je ook bepalen hoe recovery, verloren factoren en noodtoegang veilig verlopen.

### 6.3 Integriteit is niet hetzelfde als betrouwbaarheid

Integriteitscontrole toont dat een pakket onderweg niet ongemerkt veranderde. Ze toont
niet dat de gebruiker een goede handeling uitvoert.

Voorbeeld:

> Een IT-beheerder kan via een perfect versleutelde, integere tunnel nog altijd per
> ongeluk de verkeerde firewallregel wijzigen.

Daarom blijven role-based access, change management, logging en rollback uit hoofdstuk
4 relevant.

Kernzin:

> Cryptografie beschermt de communicatie; identiteit en beleid begrenzen het gebruik.

---

## 7. Remote-access-VPN

Een remote-access-VPN geeft een individueel toestel toegang tot bepaalde resources van
een organisatie. De gebruiker werkt bijvoorbeeld thuis, onderweg of op een externe
site.

```text
remote gebruiker
      |
      | internet
      v
VPN-client of browser
      |
      | beveiligd toegangspad
      v
VPN-zone -> toegestane interne diensten
```

### 7.1 Rollen in remote access

| Rol | Concrete verantwoordelijkheid |
|---|---|
| gebruiker | meldt persoonlijk aan en beschermt het toestel |
| client/device | bouwt de tunnel en installeert routes |
| identity provider | bevestigt de gebruikersidentiteit en eventueel MFA |
| VPN-gateway of control plane | registreert devices, distribueert configuratie of accepteert tunnels |
| firewall/access policy | bepaalt welke bestemmingen en poorten bereikbaar zijn |
| doelservice | voert eigen applicatieautorisatie uit |
| loggingplatform | bewaart bruikbaar bewijs van verbindingen en wijzigingen |

### 7.2 Client-based en clientless toegang

| Model | Werking | Geschikt voor | Beperking |
|---|---|---|---|
| client-based VPN | software op het toestel bouwt een netwerkpad | meerdere protocollen en interne diensten | installatie, devicebeheer en routes nodig |
| clientless toegang | browser bereikt een gepubliceerde webdienst of portal | beperkte webtoegang | geen algemene netwerktoegang; niet elk protocol past |

*Clientless VPN* wordt soms als brede term gebruikt voor een browserportal. In moderne
omgevingen kan een identity-aware proxy hetzelfde applicatiegerichte doel vervullen.
Noem daarom altijd welke dienst en welk protocol werkelijk toegankelijk worden.

### 7.3 Remote access is een nieuwe ingang

| Beleidsvraag | Waarom belangrijk? |
|---|---|
| Mag elk personeelslid verbinden? | niet elke functie heeft remote netwerktoegang nodig |
| Zijn privétoestellen toegestaan? | de organisatie heeft minder controle over patches en malware |
| Is MFA verplicht? | remote login is sterk blootgesteld aan credentialmisbruik |
| Welke groepen bestaan er? | staff, finance, IT en partners hebben andere noden |
| Wanneer vervalt toegang? | vergeten accounts en devices vergroten het aanvalsoppervlak |
| Wat wordt gelogd? | succesvolle login alleen bewijst de gebruikte flows niet |

Voorbeeldbeleid:

| Groep | Toegang | Extra eis |
|---|---|---|
| Staff | intranet en ticketing | persoonlijk account en MFA |
| Finance | finance-applicatie | beheerd toestel en MFA |
| IT | jump server en monitoring | apart beheeraccount, MFA en logging |
| Partner | één partnerdienst | eigenaar, einddatum en beperkte poort |

Kernzin:

> Remote access wordt per rol en bedrijfsnood ontworpen, niet per gemak.

---

## 8. Site-to-site-VPN

Een site-to-site-VPN verbindt netwerken via gateways. Gebruikers starten doorgaans
geen individuele VPN-client; routers of firewalls onderhouden de tunnel.

```text
+------------------+       internet       +------------------+
| Hoofdkantoor     |====== VPN-tunnel ====| Filiaal          |
| 10.10.0.0/16     |                      | 10.20.0.0/16     |
+------------------+                      +------------------+
```

| Kenmerk | Remote access | Site-to-site |
|---|---|---|
| typische endpoints | individueel device en gateway/peer | twee gateways |
| identiteit | gebruiker en device | gateway en netwerkcontext |
| routes | op de remote client | op routers/firewalls van beide sites |
| schaalvraag | accounts en devices | subnetten, gateways en tunnels |
| typische fout | gebruiker krijgt te brede toegang | hele sites vertrouwen elkaar te breed |

### 8.1 Site-to-site is geen automatische trust

Een tunnel tussen twee sites maakt routes mogelijk. Ze hoeft geen vrije communicatie
tussen alle VLAN's toe te laten.

Voorbeeld:

| Bron filiaal | Doel hoofdkantoor | Actie | Reden |
|---|---|---|---|
| kassa-VLAN | centrale ERP-service | allow op vereiste poort | bedrijfsproces |
| staff-VLAN | intranet | allow op TCP 443 | medewerkersdienst |
| volledig filiaal | management-VLAN | deny | beheerzone afschermen |
| IoT-VLAN | databases | deny | geen zakelijke nood |

### 8.2 Ontwerpvragen

| Vraag | Mogelijk gevolg bij een fout antwoord |
|---|---|
| Welke subnetten worden geadverteerd? | onnodige netwerken worden bereikbaar |
| Is er subnet overlap? | verkeer kiest het verkeerde lokale of VPN-pad |
| Hoe loopt de return route? | de heenweg werkt, maar antwoorden verdwijnen |
| Welke DNS-zones zijn nodig? | applicaties werken alleen op IP-adres |
| Is er een redundante gateway? | één toestel wordt een single point of failure |
| Wat gebeurt er bij tunneluitval? | verkeer valt stil of neemt onverwacht een publiek pad |

Hoofdstuk 6 gaat dieper in op routed access. In dit hoofdstuk moet je vooral begrijpen
dat een netwerkroute en een toegangsrecht twee afzonderlijke voorwaarden zijn.

Kernzin:

> Een site-to-site-tunnel maakt een route mogelijk; firewallbeleid bepaalt welke
> communicatie over die route is toegestaan.

---

## 9. Full tunnel

Bij **full tunnel** stuurt een client zowel intern verkeer als normaal internetverkeer
via de VPN-uitgang.

```text
laptop
  |
  | default route via VPN
  v
VPN-gateway of exit node
  |                 |
  v                 v
interne diensten    internet
```

| Voordeel | Wat betekent dit concreet? |
|---|---|
| centrale internetuitgang | websites zien het publieke bronadres van de organisatie of exitlocatie |
| centrale filtering | webfiltering en egressbeleid kunnen op één plaats gebeuren |
| bescherming op onbetrouwbare wifi | lokaal netwerk ziet de inhoud van getunneld verkeer niet |
| voorspelbaar bronadres | externe diensten kunnen één bedrijfsadres toelaten |

| Kost of risico | Praktisch gevolg |
|---|---|
| extra bandbreedte | gewoon internetverkeer belast de VPN-uitgang |
| hogere latency | verkeer maakt mogelijk een geografische omweg |
| grotere afhankelijkheid | uitval van VPN of exit node raakt alle netwerktoegang |
| privacyvraag | organisatie kan meer metadata over internetgebruik verwerken |
| lokale toegang verandert | printer of lokaal subnet kan een uitzondering vereisen |

### 9.1 Full tunnel aantonen

Een groen VPN-icoon bewijst geen full tunnel. Controleer het pad.

| Test | Zonder full tunnel | Met full tunnel | Waarom nuttig? |
|---|---|---|---|
| publiek bron-IP opvragen | adres van lokale internetlijn | adres van VPN-uitgang | bewijst de internetuitgang |
| route naar `0.0.0.0/0` bekijken | lokale gateway | VPN-interface/exitpad | controleert de routingbeslissing |
| interne dienst openen | mogelijk via VPN | via VPN | toont alleen interne bereikbaarheid, niet full tunnel |
| exit node stoppen | internet blijft lokaal werken | internet kan wegvallen | toont de afhankelijkheid |

Typische fout:

> Alleen een interne server pingen en daaruit besluiten dat al het verkeer door de VPN
> loopt.

Kernzin:

> Full tunnel is een routekeuze voor de default route, geen synoniem voor "VPN staat
> aan".

---

## 10. Split tunnel

Bij **split tunnel** gaat alleen verkeer voor geselecteerde bestemmingen via de VPN.
Ander verkeer gebruikt de gewone lokale internetverbinding.

```text
                    +--> interne routes via VPN
laptop routekeuze --|
                    +--> overige routes via lokale gateway
```

| Voordeel | Concreet effect |
|---|---|
| minder VPN-bandbreedte | videostreaming en publieke websites belasten de VPN-uitgang niet |
| lagere latency | internetverkeer maakt geen onnodige omweg |
| kleinere storingsimpact | uitval van een interne VPN-route hoeft publiek internet niet te raken |
| gerichte toegang | alleen relevante subnetten of overlay-devices krijgen een VPN-pad |

| Risico | Waarom vraagt dit aandacht? |
|---|---|
| geen centrale controle over publiek verkeer | lokale internettoegang volgt het beleid van het endpoint/netwerk |
| misleidende gebruikersverwachting | "VPN actief" betekent niet dat alle flows beschermd zijn |
| routeconflict | lokaal en remote subnet kunnen hetzelfde prefix gebruiken |
| dubbele netwerkcontext | toestel is tegelijk verbonden met lokaal netwerk en remote resources |
| DNS-lek of fout pad | interne naam kan naar de verkeerde resolver gaan |

### 10.1 Split tunnel in Tailscale

Zonder geselecteerde exit node bereikt een Tailscale-device standaard andere toegelaten
tailnet-devices en eventueel geadverteerde subnetroutes via Tailscale. Gewoon
internetverkeer blijft via de lokale verbinding lopen.

In de workshop kan je dat als volgt aantonen:

| Observatie | Test | Verwacht |
|---|---|---|
| overlay werkt | HTTP naar Tailscale-IP van de VM | webpagina opent |
| naamresolutie werkt | HTTP naar MagicDNS-naam | dezelfde webpagina opent |
| publieke uitgang blijft lokaal | publiek bron-IP opvragen | adres van huidig netwerk |
| exit node verandert het pad | dezelfde IP-test na selectie | adres van exit node-netwerk |

### 10.2 Full of split kiezen

| Scenario | Waarschijnlijke keuze | Motivering |
|---|---|---|
| medewerker gebruikt alleen intern intranet | split tunnel | beperkt omweg en centrale belasting |
| laptop op onbetrouwbare wifi moet via gefilterde uitgang | full tunnel | centraal egresspad is onderdeel van de eis |
| partner heeft één interne webdienst nodig | split tunnel of applicatieproxy | internetverkeer van partner hoeft niet via de organisatie |
| externe dienst vereist vast bedrijfsbronadres | full tunnel voor die sessie/use case | verkeer moet via gekende uitgang komen |

Er bestaat geen universeel veiligste keuze. De juiste keuze volgt uit dreigingsmodel,
privacy, performance, beschikbaarheid en zakelijke behoefte.

Kernzin:

> Bij split tunnel moet je exact documenteren welke routes en DNS-queries wél via de
> private toegang lopen.

---

## 11. VPN-adressen en subnetten

Een VPN voegt adressen en routes toe aan het bestaande IP-plan.

| Adrestype | Voorbeeld | Functie |
|---|---|---|
| lokaal clientadres | `192.168.1.25` | adres op thuis- of campusnetwerk |
| VPN-pooladres | `10.250.10.14` | adres van klassieke remote client in VPN-zone |
| intern serveradres | `10.30.40.10` | doel achter de bedrijfsfirewall |
| overlay-adres | `100.x.y.z` bij Tailscale | stabiel adres van een tailnet-device |
| publiek endpointadres | adres van NAT/gateway | transport van tunnelpakketten over internet |

Tailscale gebruikt voor IPv4-adressen van devices de gedeelde adresruimte
`100.64.0.0/10`. Dat zijn geen gewone RFC 1918-adressen en ze zijn niet rechtstreeks
publiek bereikbaar. Andere VPN-producten kunnen eigen pools of IPv6-ranges gebruiken.

### 11.1 Subnet overlap

Subnet overlap ontstaat wanneer twee verschillende netwerken hetzelfde prefix
gebruiken.

```text
thuisnetwerk:    192.168.1.0/24
bedrijfsnetwerk: 192.168.1.0/24
```

De client heeft dan mogelijk al een direct aangesloten route naar `192.168.1.0/24`.
Een pakket voor de bedrijfsserver `192.168.1.50` vertrekt lokaal in plaats van via de
VPN.

| Symptoom | Mogelijke verklaring |
|---|---|
| server werkt op kantoor maar niet thuis | thuisprefix overlapt met bedrijfsprefix |
| DNS geeft het juiste IP, verbinding faalt | naamresolutie is correct maar routekeuze is fout |
| ander thuisnetwerk werkt wel | lokaal adresplan verschilt |
| brede NAT-workaround nodig | overlap wordt gemaskeerd in plaats van opgelost |

Betere aanpakken zijn een bewust enterprise-IP-plan, unieke cloud- en filiaalranges en
controle vóór een overname of partnerkoppeling. NAT kan in bestaande omgevingen een
workaround zijn, maar voegt complexiteit toe aan logging en troubleshooting.

### 11.2 VPN-pool als policybron

Bij een klassieke VPN maakt een aparte pool verkeer herkenbaar.

| Bron | Bestemming | Actie |
|---|---|---|
| Staff-VPN `10.250.10.0/24` | intranet TCP 443 | allow |
| IT-VPN `10.250.20.0/24` | jump server TCP 22 | allow |
| Partner-VPN `10.250.30.0/24` | partnerapp TCP 443 | allow |
| VPN-pools | management algemeen | deny behalve expliciete IT-flow |

Een IP-pool alleen bewijst niet welke mens het verkeer veroorzaakte. Combineer daarom
firewalllogs met VPN-, identity- en tijdsinformatie.

Kernzin:

> VPN-adressering moet routeerbaar, niet-overlappend en bruikbaar voor beleid én
> troubleshooting zijn.

---

## 12. Routing via VPN

Een tunnel kan technisch actief zijn terwijl de applicatie onbereikbaar blijft. De
meest voorkomende reden is dat niet het volledige pakketpad klopt.

```text
client -> VPN-pad -> firewall/router -> server
client <- VPN-pad <- firewall/router <- server
```

De heenweg en terugweg zijn beide nodig.

| Controle | Vraag |
|---|---|
| clientroute | kiest de client voor dit doel de VPN-interface? |
| geadverteerde route | kent de VPN-omgeving het interne prefix? |
| route approval | mag die route werkelijk gebruikt worden? |
| forwarding | stuurt de gateway pakketten tussen interfaces door? |
| interne return route | weet het LAN hoe het VPN-adres terug bereikbaar is? |
| NAT | wordt de bron bewust vertaald, en wat doet dat met logging? |
| firewall state | zijn de heenflow en bijhorende antwoordflow toegestaan? |

### 12.1 Route-based denken

Een route beantwoordt: *welk next hop of welke interface gebruik ik voor deze
bestemming?*

| Bestemming | Mogelijk pad |
|---|---|
| specifiek tailnet-device | Tailscale-interface |
| `10.30.40.0/24` | subnetroute via VPN |
| `10.30.99.0/24` | alleen via IT-VPN indien toegestaan |
| `0.0.0.0/0` | lokale gateway of geselecteerde exit node |

Langste-prefixmatching blijft gelden. Een specifiekere lokale route kan een bredere
VPN-route overstemmen. Daarom is "de tunnel staat up" onvoldoende bewijs.

### 12.2 Route bestaat, policy ontbreekt

Bereikbaarheid heeft verschillende voorwaarden:

```text
geldige identiteit
      + device toegelaten
      + route aanwezig
      + policy laat flow toe
      + firewall laat flow toe
      + dienst luistert
      = applicatie kan werken
```

Een route maakt een bestemming vindbaar. Ze geeft geen recht om de bestemming te
gebruiken.

### 12.3 Gericht controleren

| Test | Wat leer je? | Wat bewijst de test niet? |
|---|---|---|
| routingtabel bekijken | welk pad de client verwacht te gebruiken | dat firewall en service werken |
| `traceroute`/`tracert` | zichtbare hops of padverandering | elke tunnel verbergt of toont dezelfde hops niet |
| ping | ICMP-bereikbaarheid indien toegelaten | dat TCP 443 of de applicatie werkt |
| TCP-connectietest | bereikbaarheid van één servicepoort | correcte login of applicatiefunctie |
| applicatietest | volledige gebruikersflow | dat verboden flows ook geblokkeerd zijn |

Kernzin:

> Troubleshoot VPN-verkeer van route naar policy naar service, en controleer ook de
> terugweg.

---

## 13. VPN en firewallbeleid

VPN-verkeer mag niet buiten het firewallmodel vallen. Behandel een VPN als één of meer
aparte bronzones met expliciete rechten.

| Bronzone | Bestemming | Service | Actie | Zakelijke reden |
|---|---|---|---|---|
| VPN-Staff | intranet | TCP 443 | allow | medewerkersportaal |
| VPN-Staff | finance-app | TCP 443 | deny | geen financefunctie |
| VPN-Finance | finance-app | TCP 443 | allow | financieel proces |
| VPN-IT | jump server | beheerpoort | allow | gecontroleerd beheerpad |
| VPN-Partner | partnerportaal | TCP 443 | allow | contractuele support |
| VPN-Partner | servernetwerk | any | deny | laterale toegang voorkomen |
| VPN-any | managementzone | any | deny behalve IT naar jump server | management plane beschermen |

### 13.1 Deny by default

Een goed beleid vertrekt van:

> Niet beschreven toegang is niet toegestaan.

Dit is sterker dan eerst alles openen en achteraf uitzonderingen blokkeren.

| Effect van deny by default | Praktische betekenis |
|---|---|
| kleiner aanvalsoppervlak | nieuwe interne diensten zijn niet automatisch via VPN bereikbaar |
| duidelijkere audit | elke allow-regel hoort een doel en eigenaar te hebben |
| veiliger bij compromis | gestolen account bereikt alleen expliciet toegestane doelen |
| betere change discipline | nieuwe behoefte vraagt een bewuste policywijziging en test |

### 13.2 Meerdere policy-lagen

Bij een routed VPN-pad kunnen meerdere handhavingspunten bestaan.

| Laag | Voorbeeldcontrole |
|---|---|
| VPN- of overlaypolicy | mag deze user/device naar het doel? |
| perimeter/interne firewall | mag de VPN-zone naar de serverzone? |
| subnet router | wordt het pakket doorgestuurd? |
| hostfirewall | mag de bron de lokale luisterpoort bereiken? |
| applicatie | mag de aangemelde gebruiker deze functie uitvoeren? |

Een allow op laag één heft een deny op laag drie niet op. Tijdens troubleshooting moet
je dus het eerste punt zoeken waar werkelijk verkeer wordt geweigerd.

### 13.3 Groep is een middel, geen reden

Een naam als `VPN-users` zegt weinig. Een bruikbare groep verwijst naar een rol of
toegangsdoel, bijvoorbeeld `VPN-IT-admins` of `VPN-project-X-partners`.

Kernzin:

> De tunnel brengt verkeer tot aan een policygrens; expliciete regels bepalen hoe ver
> het daarna geraakt.

---

## 14. VPN en DNS

Veel VPN-problemen zijn eigenlijk naamresolutieproblemen.

Voorbeeld:

```text
curl https://10.30.40.10       -> werkt
curl https://intranet.example  -> werkt niet
```

De route en webdienst kunnen correct zijn terwijl de client de interne naam niet via
de juiste DNS-server opzoekt.

### 14.1 Welke DNS-vragen moet je beantwoorden?

| Vraag | Waarom relevant? |
|---|---|
| Welke resolver gebruikt de client? | een publieke resolver kent interne namen niet |
| Welke suffix of zone is intern? | alleen die queries hoeven naar interne DNS |
| Is de DNS-server via VPN bereikbaar? | correcte configuratie zonder route werkt nog steeds niet |
| Krijgt de partner dezelfde interne zone? | te veel DNS-informatie kan infrastructuur blootleggen |
| Wat gebeurt er wanneer VPN uit staat? | oude cache kan een misleidend testresultaat geven |
| Gebruik je IP of hostname in bewijs? | een IP-test is geen DNS-test |

### 14.2 Split DNS

Bij **split DNS** gaan queries voor bepaalde zones naar een specifieke resolver; andere
queries blijven via de normale resolver lopen.

| Query | Resolverpad |
|---|---|
| `intranet.bluepeak.internal` | interne DNS via VPN |
| `monitoring.bluepeak.internal` | interne DNS via VPN |
| `www.vives.be` | gewone publieke DNS |

Split DNS sluit goed aan bij split tunneling, maar voegt een extra beleidslaag toe.
Documenteer de zone, resolver, bereikbaarheid en fallback.

### 14.3 MagicDNS

MagicDNS geeft Tailscale-devices DNS-namen binnen de tailnet. Daardoor hoeft een
student het `100.x.y.z`-adres van de VM niet telkens op te zoeken.

```text
http://debian-vm
```

MagicDNS en split DNS zijn niet hetzelfde.

| Concept | Lost welk probleem op? |
|---|---|
| MagicDNS | namen van tailnet-devices automatisch bruikbaar maken |
| split DNS | specifieke DNS-zones naar aangewezen resolvers sturen |

Controleer:

1. werkt de applicatie op Tailscale-IP;
2. lost de MagicDNS-naam naar het verwachte adres op;
3. werkt dezelfde applicatie op naam;
4. faalt een niet-bestaande naam voorspelbaar.

Kernzin:

> Test IP-bereikbaarheid en naamresolutie afzonderlijk voordat je concludeert dat de
> VPN niet werkt.

---

## 15. VPN voor externe partners

Een partner heeft een zakelijke relatie, maar valt buiten het eigen beheerdomein. Je
beheert diens endpoint, personeel en interne securityprocessen niet volledig.

Daarom is "partner" geen variant van "medewerker".

| Beleidsaspect | Wat moet vastliggen? |
|---|---|
| scope | concrete applicatie, host en poort |
| identiteit | persoonlijke accounts, geen generieke leverancierslogin |
| authenticatie | MFA en eventueel devicevoorwaarden |
| eigenaar | interne verantwoordelijke die toegang kan verklaren |
| duur | startdatum, einddatum en reviewmoment |
| logging | welke login- en netwerkgebeurtenissen worden bewaard |
| incidentproces | wie contacteert wie bij verdacht gedrag |
| offboarding | hoe account, device en sessies worden ingetrokken |

### 15.1 Van supportvraag naar minimale flow

Slecht geformuleerd:

> Leverancier X heeft toegang tot het servernetwerk nodig.

Beter geformuleerd:

> De twee benoemde consultants van leverancier X mogen tot 30 september via MFA vanaf
> goedgekeurde devices HTTPS naar `support-app` gebruiken. Zij krijgen geen toegang tot
> management, databasepoorten of andere servers. De applicatie-eigenaar keurt
> verlenging goed.

| Onderdeel | Vertaling naar techniek of procedure |
|---|---|
| benoemde consultants | persoonlijke identities |
| HTTPS naar één doel | bestemming plus TCP 443 |
| geen andere servers | deny by default en negatieve tests |
| einddatum | automatische vervaldatum of reviewticket |
| applicatie-eigenaar | aantoonbare approval en recertificatie |

### 15.2 Noodzakelijke negatieve tests

| Test | Verwacht | Wat bewijst dit? |
|---|---|---|
| partner opent partnerapp | allow | noodzakelijke flow werkt |
| partner opent intranet | deny | medewerkerszone blijft afgeschermd |
| partner probeert SSH naar partnerhost | deny tenzij expliciet nodig | poortscope is correct |
| verlopen partneraccount meldt aan | deny | lifecycle wordt afgedwongen |

Kernzin:

> Partner-VPN-toegang is tijdelijk, persoonlijk, doelgebonden en aantoonbaar beperkt.

---

## 16. Tailscale als identity-aware overlay

Tailscale bouwt een private overlay bovenop bestaande netwerken. Elk deelnemend device
krijgt een Tailscale-identiteit en -adres. De software gebruikt WireGuard voor het
versleutelde datapad en een control plane voor onder meer registratie, peerinformatie,
routes, DNS-configuratie en access policy.

### 16.1 Klassieke concentrator en mesh vergelijken

| Klassieke remote-access-VPN | Tailscale-overlay |
|---|---|
| clients verbinden vaak met centrale concentrator | devices proberen peer-to-peer te verbinden |
| concentrator is datapad | control plane coördineert; payload loopt niet door die control plane |
| VPN-pool identificeert bronzone | users, devices, tags en adressen kunnen context leveren |
| interne subnetten liggen achter gateway | software kan rechtstreeks op doelen draaien of subnetten routeren |
| centrale gateway kan bottleneck zijn | directe dataverbindingen spreiden het datapad |

Dit betekent niet dat Tailscale zonder centrale afhankelijkheden werkt. Nieuwe
registraties, policywijzigingen, keydistributie en coördinatie vertrouwen op de control
plane. Reeds gekende peers kunnen bij een tijdelijke control-plane-uitval onder
bepaalde omstandigheden met gecachete informatie blijven communiceren, maar dat is
geen vervanging voor beschikbaarheidsplanning.

### 16.2 Control plane en data plane

| Plane | Taken | Draagt de normale applicatiepayload? |
|---|---|---|
| control plane | identiteit, device-registratie, peercoördinatie, routes, DNS en policy distribueren | nee |
| data plane | versleutelde pakketten tussen devices transporteren en filteren | ja |

Conceptueel:

```text
                 control plane
             identity, peers, policy
                /             \
               v               v
          laptop ==========> server
                 data plane
             WireGuard-beveiligd
```

### 16.3 Directe en gerelayde verbinding

Tailscale probeert een performant pad tussen peers te bouwen. Een verbinding kan
rechtstreeks via UDP lopen of, wanneer NAT/firewallcondities dat verhinderen, via een
relay. De payload blijft in beide gevallen end-to-end met WireGuard beschermd.

| Verbindingstype | Pad | Praktische impact |
|---|---|---|
| direct | device naar device | meestal laagste latency en hoogste throughput |
| peer relay | via aangewezen device in de tailnet | alternatief wanneer direct niet lukt |
| DERP relay | via Tailscale-relayinfrastructuur | robuuste fallback, mogelijk hogere latency |

Controleer met `tailscale status`, `tailscale ping` en indien nodig
`tailscale netcheck` welk pad werkelijk wordt gebruikt. Een applicatie kan via relay
perfect werken; het onderscheid is vooral belangrijk voor performance en
troubleshooting.

### 16.4 Wat Tailscale niet automatisch oplost

| Misvatting | Correctie |
|---|---|
| elk tailnet-device mag elkaar vertrouwen | access policy blijft nodig |
| encryptie maakt endpointsecurity overbodig | een gecompromitteerd endpoint blijft gevaarlijk |
| MagicDNS is volledige enterprise-DNS | het lost vooral tailnet-naamgeving op |
| directe verbinding betekent open inbound port forwarding | NAT traversal en coördinatie bouwen het pad dynamisch |
| product werkt, dus lifecycle is geregeld | oude devices en accounts moeten nog steeds worden verwijderd |

Kernzin:

> Tailscale scheidt centrale coördinatie van het versleutelde datapad, maar de
> organisatie blijft verantwoordelijk voor toegang, lifecycle en bewijs.

---

## 17. Tailnet, users, devices en identiteit

Een **tailnet** is de private netwerkomgeving waarin Tailscale users, devices, routes,
DNS en policies samenbrengt.

| Begrip | Betekenis | Beheervraag |
|---|---|---|
| user | menselijke of organisatorische identiteit | wie is verantwoordelijk? |
| device/node | systeem waarop Tailscale draait | is dit toestel gekend en nog nodig? |
| device name | beheers- en DNS-naam | is de naam uniek en betekenisvol? |
| Tailscale-IP | stabiel overlay-adres van het device | hoort dit adres bij het verwachte toestel? |
| tailnet | administratieve private omgeving | wie beheert membership en policy? |
| route | bereikbaar prefix via een routerdevice | is het prefix bewust en beperkt? |

### 17.1 User identity versus device identity

Eén user kan meerdere devices hebben. Eén serverdevice hoort niet noodzakelijk bij een
persoonlijke dagelijkse identiteit.

| User | Device | Andere securityvraag |
|---|---|---|
| Alice | beheerde werklaptop | is Alice actief en is de laptop compliant? |
| Alice | privételefoon | is dit type endpoint toegestaan? |
| IT-team | jump server | wie beheert de serveridentiteit en sleutels? |
| student | tijdelijke Debian-VM | wanneer wordt de VM uit de tailnet verwijderd? |

In hoofdstuk 6 leer je serverdevices met tags en expliciete policy behandelen. In Ch5
volstaat het om te herkennen dat persoonlijke ownership niet hetzelfde is als een
duurzame serverrol.

### 17.2 Betekenisvolle naamgeving

| Zwakke naam | Sterkere naam | Waarom beter? |
|---|---|---|
| `DESKTOP-83KQ92A` | `laptop-alice` | eigenaar en type zijn herkenbaar |
| `debian` | `student12-web-vm` | functie en labcontext zijn duidelijk |
| `server2` | `bp-jump-prod-01` | organisatie, rol, omgeving en volgnummer zijn zichtbaar |

Een naam is geen beveiligingscontrole. Ze voorkomt wel menselijke fouten en versnelt
troubleshooting.

### 17.3 Device lifecycle

| Fase | Actie | Bewijs of controle |
|---|---|---|
| onboarding | device aanmelden en eigenaar bepalen | zichtbaar in inventory |
| approval | controleren of toetreding toegestaan is | status en goedkeurder |
| gebruik | juiste naam, policy en routes toepassen | positieve en negatieve test |
| review | noodzaak, eigenaar en laatste activiteit bekijken | periodieke inventariscontrole |
| incident | device isoleren of verwijderen | toegang stopt en event wordt gelogd |
| offboarding | registratie, keys en eventuele routes intrekken | device verdwijnt of staat niet langer authorized |

Kernzin:

> Een device is niet "klaar" na onboarding; het moet gedurende zijn hele lifecycle
> herkenbaar, verantwoord en intrekbaar blijven.

---

## 18. Devicebeheer in de persoonlijke tailnet

In de Ch5-workshop gebruikt elke student een persoonlijke tailnet met minimaal:

| Component | Rol in het lab |
|---|---|
| laptop of tweede client | bron van de remote HTTP-test |
| Debian-VM | doelserver met webdienst |
| optioneel Devbit-device | exit node voor de challenge |

Dat is een labvereenvoudiging. De student is tegelijk gebruiker, device-eigenaar en
tailnetbeheerder. In productie zijn die rollen vaak gescheiden.

### 18.1 Wat inventariseer je?

| Veld | Waarom noteren? | Mag in een verslag? |
|---|---|---|
| device name | testresultaat aan juiste node koppelen | ja |
| functionele rol | verklaart waarom het device bestaat | ja |
| Tailscale-IP | directe connectiviteit aantonen | doorgaans ja in deze labcontext |
| gewone lab-IP | verschillende netwerkpaden vergelijken | ja |
| online/offline-status | actuele bereikbaarheid controleren | ja |
| account- of auth key | credential waarmee toegang kan worden verkregen | nee |
| recovery code of token | kan accountovername mogelijk maken | nooit |

### 18.2 Cleanup is deel van de workshop

Een tijdelijke VM die na de workshop geregistreerd blijft, is een vergeten endpoint.
Daarom hoort cleanup bij de bewijsvoering.

Controleer na afloop:

1. welke devices nog in de tailnet staan;
2. of de tijdelijke VM nog nodig is;
3. of een exit-node-advertentie nog actief is;
4. of screenshots geen secrets tonen;
5. of persoonlijke testtoegang verwijderd moet worden.

In productie:

> Gebruik centrale identity, formele ownership, namingstandaarden, periodieke review en
> geautomatiseerde offboarding waar mogelijk.

Kernzin:

> Ook een persoonlijke tailnet is een inventaris van actieve toegang, niet alleen een
> lijstje met computers.

---

## 19. Exit nodes

Een **exit node** laat een Tailscale-client zijn internetverkeer via een ander
tailnet-device naar buiten sturen. Conceptueel implementeert dit full tunnel voor de
default routes van de client.

```text
remote laptop
     |
     | versleuteld via Tailscale
     v
exit node
     |
     | NAT/forwarding naar buiten
     v
internet
```

### 19.1 Rollen en voorwaarden

| Stap | Wat gebeurt er? | Typische fout |
|---|---|---|
| aanbieden | device adverteert dat het exit node kan zijn | forwarding of platforminstelling ontbreekt |
| goedkeuren/toestaan | beheercontext laat gebruik toe | node wordt wel aangeboden maar niet bruikbaar |
| selecteren | client kiest de exit node | tester denkt dat selectie automatisch gebeurde |
| routeren | default verkeer gaat via exit node | lokale route of andere VPN conflicteert |
| uitgaand verbinden | exit node stuurt verkeer naar internet | firewall/NAT blokkeert de egressflow |

### 19.2 Exit node versus subnet router

| Eigenschap | Exit node | Subnet router |
|---|---|---|
| hoofddoel | internetverkeer uitrouteren | private subnetten bereikbaar maken |
| typische route | `0.0.0.0/0` en/of `::/0` | bijvoorbeeld `10.30.40.0/24` |
| voorbeeld | laptop gebruikt campus als publieke uitgang | laptop bereikt legacy-server achter router |
| belangrijkste test | publiek bron-IP verandert | doel in geadverteerd subnet wordt bereikbaar |
| belangrijk risico | alle internetverkeer hangt van node af | te breed intern prefix wordt ontsloten |

### 19.3 Exit node testen

| Test | Verwacht | Bewijs |
|---|---|---|
| publiek IP vóór selectie | lokaal/campusadres | genoteerd IP zonder gevoelige details |
| exit node selecteren | client toont gekozen node | statusoutput of instelling |
| publiek IP na selectie | adres van exitlocatie | vergelijking met baseline |
| interne HTTP-test | blijft werken indien policy/routing klopt | applicatierespons |
| exit node deselecteren | lokaal publiek IP keert terug | tweede vergelijking |

Een IP-wijziging toont het egresspad, maar niet dat alle securityfiltering of logging
correct is. Daarvoor zijn aanvullende controles op de exit node nodig.

### 19.4 Productierisico's

| Risico | Maatregel |
|---|---|
| single point of failure | redundantie, monitoring en herstelprocedure |
| privacy-impact | transparant log- en bewaarbeleid |
| bandbreedtebottleneck | capaciteit meten en begrenzen |
| misbruik als algemene proxy | toegang tot exit node expliciet beperken |
| onverwachte lokale netwerktoegang | clientinstellingen en uitzonderingen testen |

Kernzin:

> Een exit node verandert waar internetverkeer de tailnet verlaat en wordt daardoor
> tegelijk een router, securitygrens en beschikbaarheidsafhankelijkheid.

---

## 20. Subnet routers

Een **subnet router** maakt een netwerk achter een Tailscale-device bereikbaar voor
toegelaten tailnet-clients. De hosts in dat achterliggende netwerk hoeven zelf geen
Tailscale te draaien.

```text
tailnet-client
      |
      | Tailscale
      v
subnet router
      |
      | intern LAN
      v
legacy-server 10.30.40.10
```

### 20.1 Wanneer is een subnet router nuttig?

| Situatie | Waarom geen client op elk doel? |
|---|---|
| printers of netwerktoestellen | clientsoftware wordt niet ondersteund |
| legacy-servers | wijziging aan host is niet wenselijk of mogelijk |
| volledig bestaand VLAN | gefaseerde migratie vraagt netwerktoegang |
| industriële of embedded systemen | platform en lifecycle zijn beperkt |

Directe installatie op een specifieke server geeft vaak fijnere device-identiteit.
Subnet routing is breder en moet daarom bewust begrensd worden.

### 20.2 Van geadverteerde route naar werkende flow

| Voorwaarde | Functie |
|---|---|
| Tailscale op routerdevice | verbindt router met de tailnet |
| IP forwarding | laat het OS pakketten tussen interfaces doorsturen |
| route advertisement | meldt welk achterliggend prefix bereikbaar is |
| route approval/gebruik | maakt de route beschikbaar voor clients |
| access policy | beperkt wie naar welk doel mag |
| LAN- en hostfirewall | laat de uiteindelijke serviceflow toe |
| return route of bewuste SNAT | zorgt dat antwoorden terugkomen |

### 20.3 Breed prefix, breed risico

| Advertentie | Beoordeling |
|---|---|
| `10.30.0.0/16` | eenvoudig, maar kan veel VLAN's en diensten omvatten |
| `10.30.40.0/24` | beter begrensd tot serversegment |
| specifieke hostroute waar ondersteund en passend | klein bereik, maar meer beheer |

Een smaller geadverteerd prefix vervangt nog geen poortpolicy. Ook binnen één `/24`
kan een gebruiker slechts één HTTPS-dienst nodig hebben.

### 20.4 High availability

Een subnet router kan een single point of failure worden. Koppel daarom terug naar
hoofdstuk 4.

| HA-vraag | Wat moet je aantonen? |
|---|---|
| bestaat een tweede router? | dezelfde noodzakelijke routes en policy zijn voorbereid |
| hoe wordt uitval gedetecteerd? | monitoring ziet dat het datapad niet meer werkt |
| hoe lang duurt herstel? | RTO past bij de bedrijfsimpact |
| werkt return routing bij failover? | applicatietest via het nieuwe pad slaagt |
| hoe keer je terug? | failback veroorzaakt geen onverwachte onderbreking |

Kernzin:

> Een subnet router ontsluit bereikbaarheid voor systemen zonder VPN-client, maar
> vergroot tegelijk de route-, policy- en beschikbaarheidsscope.

---

## 21. VPN en managementtoegang

Remote management heeft meer impact dan gewone applicatietoegang. Een beheerder kan
configuraties wijzigen, accounts aanmaken, logs wissen of een netwerk onderbreken.

Daarom hoort management niet in een algemene staff-VPN-regel.

```text
adminlaptop
     |
     | VPN met sterke identity
     v
jump server
     |
     | beperkt managementpad
     v
managementzone
```

### 21.1 Rechtstreeks of via jump server

| Ontwerp | Voordeel | Risico/kost |
|---|---|---|
| VPN rechtstreeks naar elk beheertoestel | weinig tussenstappen | brede managementbereikbaarheid en verspreide logs |
| VPN naar jump server | centraal controle- en auditpunt | jump server wordt kritisch doel en mogelijke SPOF |
| application proxy naar één beheertool | zeer gerichte webtoegang | niet geschikt voor elk beheerprotocol |

### 21.2 Minimale eisen voor remote beheer

| Maatregel | Wat beperkt dit? |
|---|---|
| apart persoonlijk beheeraccount | dagelijks account heeft geen permanente adminimpact |
| MFA | gestolen wachtwoord alleen is onvoldoende |
| beheerd device | onbekende endpoints krijgen geen beheerpad |
| toegang alleen naar jump server | managementinterfaces blijven buiten directe VPN-reikwijdte |
| role-based access | beheerder krijgt alleen noodzakelijke functies |
| sessie- en wijzigingslogging | handelingen zijn beter te reconstrueren |
| noodpad en rollback | foutieve VPN- of policywijziging sluit beheerder niet definitief buiten |

### 21.3 Testen zonder jezelf buiten te sluiten

Voor een remote policywijziging heb je vooraf nodig:

1. een baseline van de werkende beheerflow;
2. een tweede of out-of-band beheerpad indien de impact groot is;
3. een concrete allow-test voor de admin;
4. een deny-test voor een gewone gebruiker;
5. een rollbackcriterium en -procedure;
6. logging waarmee je de policybeslissing kan terugvinden.

Kernzin:

> Hoe groter de mogelijke impact van een account, hoe smaller en beter aantoonbaar het
> remote beheerpad moet zijn.

---

## 22. Typische VPN-fouten en denkfouten

### 22.1 Technische fouten

| Fout | Waarschijnlijk symptoom | Eerste gerichte controle | Betere aanpak |
|---|---|---|---|
| tunnel niet actief | geen enkel VPN-doel bereikbaar | peer/device-status | authenticatie en endpointstatus controleren |
| route ontbreekt | specifieke subnetten werken niet | clientroutingtabel | doelprefix bewust distribueren |
| return route ontbreekt | request vertrekt, geen antwoord | route op LAN/gateway | retourpad of bewuste SNAT voorzien |
| firewall blokkeert | route klopt, servicepoort timeout | logs en TCP-test | exacte bron-doel-poortregel controleren |
| dienst luistert niet | host bereikbaar, applicatie niet | lokale service/status | service en hostfirewall testen |
| subnet overlap | werkt vanaf één netwerk, niet vanaf ander | lokale en VPN-prefixes vergelijken | IP-plan aanpassen of overlap bewust oplossen |
| verkeerde DNS-resolver | IP werkt, naam niet | resolver en queryresultaat | split DNS/MagicDNS correct instellen |
| exit node niet geselecteerd | publiek IP verandert niet | clientstatus en routes | selectie expliciet verifiëren |
| verbinding gebruikt relay | functioneel maar trager | `tailscale ping`/`netcheck` | NAT/firewallpad onderzoeken indien performance telt |

### 22.2 Security- en beheerfouten

| Fout | Gevolg | Betere aanpak |
|---|---|---|
| alle VPN-users mogen alles | groot lateraal bewegingsrisico | deny by default en rolgebaseerde flows |
| geen MFA | gestolen wachtwoord kan volstaan | MFA verplichten volgens risico |
| partner als gewone medewerker | externe trust wordt te breed | aparte partneridentity, zone en einddatum |
| management voor staff bereikbaar | management plane wordt blootgesteld | IT naar jump server als expliciet pad |
| oude devices blijven authorized | vergeten toegang blijft bestaan | periodieke review en cleanup |
| secrets in screenshots | credentiallek via verslag | output redigeren en secrets nooit opnemen |
| één subnet router/exit node | brede remote uitval | HA- en herstelplan |
| alleen succesvolle tests | te brede toegang blijft onzichtbaar | bij elke allow relevante deny-test uitvoeren |

### 22.3 Denkfouten

| Denkfout | Correcte redenering |
|---|---|
| "VPN is veilig omdat het versleuteld is." | encryptie beschermt het pad; policy begrenst toegang |
| "Ping werkt, dus de VPN werkt volledig." | ping test hoogstens ICMP; DNS, service, auth en deny-cases blijven open |
| "Full tunnel is altijd veiliger." | full tunnel centraliseert egress maar verhoogt afhankelijkheid, logging en privacy-impact |
| "Split tunnel is altijd onveilig." | gerichte routes kunnen goed bij least privilege passen als endpoint en DNS correct beheerd zijn |
| "Zelfde tailnet betekent zelfde trust." | membership en toegang zijn verschillende beslissingen |
| "Tijdelijke partnertoegang mag breed zijn." | tijdelijke toegang vraagt juist een eigenaar, scope en einddatum |

Kernzin:

> Verander niet willekeurig instellingen: bepaal eerst of de fout bij identiteit,
> tunnel, route, policy, DNS of service ligt.

---

## 23. Testplan voor VPN

Een professioneel testplan bevat drie soorten tests.

| Testtype | Vraag | Voorbeeld |
|---|---|---|
| positieve test | werkt de noodzakelijke flow? | staff opent intranet via HTTPS |
| negatieve test | blijft verboden toegang dicht? | staff kan jump server niet bereiken |
| bewijstest | toont het bewijs ook de bedoelde oorzaak of het pad? | publiek IP verandert na selectie van exit node |

### 23.1 Van laag naar gebruikersflow

| Volgorde | Test | Verwacht | Waarom test je dit? |
|---:|---|---|---|
| 1 | device verschijnt in inventory | juiste naam en status | onboarding en identiteit controleren |
| 2 | VPN/peerstatus controleren | peer is bereikbaar | tunnel- of overlaylaag controleren |
| 3 | route naar doel bekijken | verwacht VPN-pad | routingbeslissing aantonen |
| 4 | doel-IP bereiken | antwoord indien ICMP toegestaan | basisbereikbaarheid onderzoeken |
| 5 | servicepoort testen | TCP-verbinding slaagt | firewall en luisterpoort controleren |
| 6 | applicatie gebruiken | correcte inhoud of functie | end-to-end gebruikersflow bewijzen |
| 7 | verboden service proberen | blokkering | least privilege aantonen |
| 8 | logs controleren | event met juiste context | auditability aantonen |

Niet elk netwerk laat ping toe. Een mislukte ping is daarom geen automatisch bewijs dat
de VPN faalt. Gebruik een test die past bij de toegestane service.

### 23.2 Testmatrix BluePeak

| Identiteit/bron | Bestemming | Service | Verwacht | Bewijs |
|---|---|---|---|---|
| Staff-VPN | intranet | HTTPS | allow | pagina en relevante log |
| Staff-VPN | finance-app | HTTPS | deny | timeout/deny plus firewall- of policylog |
| Finance-VPN | finance-app | HTTPS | allow | werkende applicatieflow |
| Partner-VPN | partnerportaal | HTTPS | allow | portaal opent |
| Partner-VPN | intranet | HTTPS | deny | negatieve test en log |
| IT-VPN | jump server | beheerpoort | allow | persoonlijke beheersessie |
| Staff-VPN | jump server | beheerpoort | deny | policygrens bewezen |

### 23.3 Wat noteer je per test?

| Veld | Voorbeeld | Waarom nodig? |
|---|---|---|
| tijdstip | `2026-08-20 10:14 CEST` | logs correleren |
| identiteit | `alice.staff` | userpolicy aantonen |
| brontoestel | `laptop-alice` | devicecontext aantonen |
| bronpad | thuisnetwerk via Tailscale | netwerkcontext vastleggen |
| bestemming | `intranet` | scope duidelijk maken |
| protocol/poort | HTTPS/TCP 443 | exacte flow beschrijven |
| verwacht resultaat | allow | test vooraf falsifieerbaar maken |
| werkelijk resultaat | pagina laadt | observatie noteren |
| bewijs | beperkte screenshot/output/log-ID | resultaat reproduceerbaar maken |
| conclusie | policy werkt voor deze case | geen bredere claim maken dan de test bewijst |

### 23.4 Negatieve test veilig interpreteren

Een timeout kan betekenen dat policy blokkeert, maar ook dat de server uit staat. Een
sterke negatieve test vergelijkt daarom met een toegelaten bron of met een log van de
deny-beslissing.

Kernzin:

> Een geslaagde verbinding bewijst bereikbaarheid; een combinatie van allow-, deny- en
> bewijstests bewijst het ontwerp.

---

## 24. VPN-policy ontwerpen

Schrijf eerst het beleid in mensentaal en vertaal het daarna naar configuratie.

### 24.1 Minimale policy-inhoud

| Onderdeel | Vraag die de policy beantwoordt |
|---|---|
| doel | welk bedrijfsproces vereist remote toegang? |
| identities | welke users, groepen of services krijgen toegang? |
| devices | zijn privétoestellen toegestaan en hoe worden ze goedgekeurd? |
| authenticatie | welke MFA- of device-eisen gelden? |
| destinations | welke applicaties, hosts of subnetten zijn nodig? |
| services | welke protocollen en poorten horen bij de use case? |
| tunnelmodel | split of full, en waarom? |
| DNS | welke namen en resolvers zijn nodig? |
| logging | welke events worden bewaard en wie onderzoekt ze? |
| lifecycle | wie is eigenaar, wanneer volgt review en hoe stopt toegang? |
| beschikbaarheid | welke uitval is aanvaardbaar en welk herstelpad bestaat? |
| testplan | welke allow- en deny-cases bewijzen het beleid? |

### 24.2 Voorbeeldpolicy BluePeak Services

| Groep | Toegang | Authenticatie/device | Tunnelmodel |
|---|---|---|---|
| Staff | intranet en ticketing op HTTPS | persoonlijk account, MFA, gekend device | split |
| Finance | intranet en finance-app op HTTPS | MFA en beheerd device | split; exit node indien egress-eis |
| IT-admins | jump server en monitoring | apart beheeraccount, MFA, beheerd device | split of gecontroleerd full tunnel |
| Partners | partnerportaal op HTTPS | persoonlijk account, MFA, einddatum | split |

Expliciet verboden:

| Verboden flow | Reden |
|---|---|
| partner naar interne subnetten algemeen | contractuele scope is één applicatie |
| staff rechtstreeks naar management | management loopt via IT en jump server |
| elke VPN-user naar databasepoorten | applicaties, niet eindgebruikers, praten met databases |
| onbekend device naar beheeromgeving | device trust is onderdeel van de beheereis |

### 24.3 Van behoefte naar regel

Zwakke verantwoording:

> Ik heb TCP 443 geopend omdat het anders niet werkte.

Sterke verantwoording:

> Finance-medewerkers moeten thuis de finance-app via HTTPS bereiken. Daarom staat de
> flow `VPN-Finance -> finance-app -> TCP 443` toe. Een Staff-identiteit en een
> Partner-identiteit worden als negatieve tests gebruikt. Rechtstreekse database- en
> managementtoegang blijven geblokkeerd.

In hoofdstuk 6 vertaal je dit principe naar concrete Tailscale users, groups, tags en
access rules. De menselijke policy blijft de bron van de configuratiekeuze.

Kernzin:

> Een regel is pas verdedigbaar wanneer je doel, bron, bestemming, service, eigenaar en
> test kan benoemen.

---

## 25. Voorbereiding op de Tailscale-workshop

De workshop maakt een Debian-webserver via Tailscale bereikbaar vanaf een tweede
device. Het doel is niet alleen een werkende webpagina, maar een vergelijking van
netwerkpaden.

### 25.1 Labtopologie

```text
                    bestaande labnetwerken
                         (transport)
                      /              \
                     /                \
              laptop/client       Debian-VM
                     \                /
                      \              /
                       Tailscale-overlay
                             |
                         HTTP-test
```

| Component | Wat observeer je? |
|---|---|
| Debian-VM | gewone IP, Tailscale-IP, device name en webservice |
| client | huidige netwerkcontext, Tailscale-status en gekozen route |
| lokale HTTP-test | webserver werkt vóór je VPN troubleshoot |
| directe Devbit/eduroam-test | bestaand netwerkpad en filtering |
| Tailscale-HTTP-test | applicatie werkt via overlay-adres |
| MagicDNS-challenge | naamresolutie binnen tailnet |
| exit-node-challenge | verschil tussen split en full tunnel |

### 25.2 Waarom eerst lokaal testen?

Als de webserver lokaal niet antwoordt, heeft het weinig zin om eerst VPN-routes te
wijzigen.

```text
service lokaal correct?
        |
        v
device in tailnet?
        |
        v
VPN-pad naar IP?
        |
        v
naamresolutie?
        |
        v
exitpad/policy?
```

Deze volgorde beperkt het aantal mogelijke oorzaken per stap.

### 25.3 Drie paden vergelijken

| Testpad | Wat test je werkelijk? | Mogelijk resultaat |
|---|---|---|
| lokaal op VM | service en lokale luisterpoort | moet werken vóór remote tests |
| rechtstreeks via lab-IP | campusrouting en firewallregels | kan per netwerk verschillen |
| via Tailscale-IP/naam | overlay, device identity, route en service | moet onafhankelijk van directe labroute werken |

Een geslaagde directe test via Devbit bewijst niet dat Tailscale gebruikt werd. Noteer
daarom het gebruikte doeladres of de MagicDNS-naam.

### 25.4 Bewijs zonder secrets

Geschikt bewijs:

- device names en rollen;
- beperkte statusoutput;
- testcommando en relevante respons;
- vergelijking van publiek IP vóór en na exit node;
- korte risicoanalyse en conclusie.

Niet opnemen:

- wachtwoorden;
- auth keys;
- herstelcodes;
- sessiecookies;
- volledige tokens;
- screenshots met persoonlijke gegevens die niet nodig zijn.

Kernzin:

> De workshop is geslaagd wanneer je het gebruikte pad kan aantonen en kan uitleggen
> wat de test wel en niet bewijst.

---

## 26. Securityzones, risico en productieontwerp

VPN moet aansluiten op het zoneontwerp uit hoofdstuk 3 en de beheer- en
beschikbaarheidsprincipes uit hoofdstuk 4.

### 26.1 VPN als bronzone

| Zone | Vertrouwensniveau | Typische toegang |
|---|---|---|
| VPN-Staff | beperkt vertrouwd | algemene interne applicaties |
| VPN-Finance | gevoelig | finance-app via specifieke service |
| VPN-IT | hoge impact, streng gecontroleerd | jump server en monitoring |
| VPN-Partner | extern en minimaal vertrouwd | één contractueel doel |
| Management | zeer beschermd | alleen via gecontroleerd beheerpad |

De naam van een zone is geen controle. Het zijn routing, policy, identity, device-eisen
en logging die de grens afdwingen.

### 26.2 Risicoregister

| Risico | Waarschijnlijk gevolg | Maatregel | Noodzakelijke test |
|---|---|---|---|
| gestolen usercredential | aanvaller probeert remote login | MFA, detectie en snelle revocation | login zonder tweede factor faalt |
| verloren device | geregistreerd endpoint wordt misbruikt | device verwijderen en sessies intrekken | device kan niet opnieuw verbinden |
| te brede partnerpolicy | laterale toegang tot interne systemen | aparte zone en minimale flows | partner naar intranet faalt |
| subnet overlap | verkeerde route en onbereikbare dienst | uniek IP-plan | routecontrole vanaf conflicterend netwerk |
| exit node faalt | clients met full tunnel verliezen egress | redundantie of gedocumenteerde fallback | gecontroleerde uitvaltest |
| subnet router faalt | remote subnet verdwijnt | HA en monitoring | applicatieflow via reservepad |
| verkeerde DNS-policy | interne app werkt alleen op IP | split DNS/MagicDNS testen | IP én naam geven verwacht resultaat |
| oud device blijft actief | vergeten toegang | inventory review en cleanup | gedecommissioned device is unauthorized |

### 26.3 Lab versus productie

| Thema | In het lab | In productie |
|---|---|---|
| ownership | student beheert eigen tailnet | duidelijke scheiding user, owner en admin |
| identity | persoonlijk testaccount | centrale IdP, lifecycle en sterke MFA |
| devices | laptop en tijdelijke VM | beheerde inventory, posture en periodieke review |
| policy | beperkte demonstratie; verdieping in Ch6 | change-controlled least-privilegebeleid |
| availability | één VM of exit node kan volstaan | redundantie volgens RTO en impact |
| logging | screenshots en beperkte output | centrale, tijdgesynchroniseerde en beschermde logs |
| secrets | handmatig buiten verslag houden | secretmanagement, rotatie en incidentprocedure |
| support | student troubleshoot zelf | monitoring, runbooks, eigenaars en escalatie |

### 26.4 Minimale ontwerpdocumentatie

Een professioneel VPN-ontwerp bevat minstens:

1. doel en scope;
2. diagram met tunnelendpoints en trust boundaries;
3. users, groepen, devices en eigenaars;
4. adressen, routes en DNS-zones;
5. access matrix met bron, doel, service en actie;
6. keuze voor split of full tunnel;
7. authenticatie- en device-eisen;
8. logging, monitoring en bewaarbeleid;
9. onboarding-, review- en offboardingproces;
10. beschikbaarheids-, herstel- en rollbackkeuzes;
11. positieve, negatieve en failovertests;
12. gekende risico's en aanvaarde beperkingen.

Kernzin:

> Een VPN is pas enterprise-klaar wanneer toegang, risico, lifecycle, uitval en bewijs
> samen ontworpen zijn.

---

## 27. Controlevragen en denkvragen

### 27.1 Begripscontrole

1. Waarom is een VPN-tunnel geen automatisch vertrouwde zone?
2. Wat is het verschil tussen encryptie, endpoint-authenticatie en autorisatie?
3. Waar eindigt de bescherming van een tunnel naar een subnet router?
4. Hoe verschillen remote-access- en site-to-site-VPN in endpoints en identiteit?
5. Waarom bewijst een werkende interne webpagina niet dat full tunnel actief is?
6. Wat is het verschil tussen MagicDNS en split DNS?
7. Wat is het verschil tussen een exit node en een subnet router?
8. Waarom kan een directe Tailscale-verbinding sneller zijn dan een relayverbinding?
9. Waarom is een route geen toegangsrecht?
10. Welke drie testtypes horen in een professioneel VPN-testplan?

### 27.2 Toepassingsvragen

1. Alice kan `10.30.40.10` openen maar niet `intranet.bluepeak.internal`. Welke
   controles voer je uit, in welke volgorde?
2. Een thuiswerker gebruikt lokaal `192.168.1.0/24`; het bedrijf gebruikt hetzelfde
   subnet. Leg uit waarom DNS correct kan zijn terwijl de verbinding toch faalt.
3. Een partner moet één webapplicatie ondersteunen. Ontwerp de minimale regels voor
   identiteit, devices, routes, poorten en lifecycle.
4. `tailscale ping` bereikt een peer via relay. Is de verbinding daarom onveilig? Welke
   echte impact moet je onderzoeken?
5. Na selectie van een exit node werkt de interne VM nog, maar het publieke IP verandert
   niet. Welke mogelijke oorzaken onderzoek je?
6. Een subnetroute is goedgekeurd, maar de legacy-server antwoordt niet. Geef een
   troubleshootingvolgorde van client tot server en terug.
7. Een IT-admin wil rechtstreeks via VPN alle switchinterfaces beheren. Welke betere
   architectuur stel je voor en welke deny-test hoort daarbij?
8. Een vertrokken consultant staat niet meer in de identity provider, maar diens laptop
   staat nog in de device-inventory. Welke toegang moet je expliciet controleren en
   intrekken?

### 27.3 Criteria voor een sterk antwoord

| Criterium | Wat verwacht je? |
|---|---|
| conceptueel juist | tunnel, route, policy, DNS en service worden niet verward |
| scenario-gebonden | concrete bron, bestemming, service en identiteit worden benoemd |
| oorzaak en gevolg | technische keuze wordt aan risico of bedrijfsimpact gekoppeld |
| toetsbaar | zowel allow- als deny-test is beschreven |
| begrensd | antwoord zegt wat de gekozen maatregel niet oplost |
| lifecyclebewust | onboarding, review en intrekking zijn meegenomen |
| productiegericht | labvereenvoudiging wordt niet als eindontwerp voorgesteld |

---

## 28. Samenvatting

Belangrijkste inzichten:

- een VPN maakt private communicatie mogelijk over een niet-vertrouwd transportnetwerk;
- de tunnel verandert het netwerkpad, maar verleent niet automatisch vertrouwen;
- encryptie, authenticatie, integriteit en autorisatie hebben elk een andere functie;
- remote-access-VPN geeft individuele devices toegang; site-to-site-VPN verbindt
  netwerken via gateways;
- full tunnel stuurt default verkeer via een VPN-uitgang; split tunnel alleen
  geselecteerde routes;
- adressen, langste-prefixmatching, return routing en subnet overlap bepalen of het pad
  werkelijk werkt;
- DNS moet afzonderlijk van IP-bereikbaarheid worden getest;
- een VPN hoort in aparte securityzones met deny by default en minimale flows;
- partner- en managementtoegang vragen sterkere afbakening, MFA, ownership en logging;
- Tailscale gebruikt een centrale control plane en een WireGuard-beveiligd datapad;
- Tailscale-peers kunnen direct, via een peer relay of via DERP communiceren;
- een exit node routeert internetverkeer; een subnet router ontsluit private subnetten;
- device-inventory, naamgeving, review en cleanup zijn onderdelen van security;
- een werkende allow-test is onvoldoende zonder relevante deny- en bewijstests;
- labkeuzes moeten expliciet onderscheiden worden van productievereisten.

De rode draad blijft:

```text
identiteit -> toestel -> tunnel -> route -> policy -> test -> logging -> lifecycle
```

Kernzin:

> Een professionele VPN-oplossing bewijst niet alleen dat noodzakelijke toegang werkt,
> maar ook dat onnodige toegang niet werkt en dat toegang beheerd, ingetrokken en
> onderzocht kan worden.

---
