# Workshop 4 - Availability en secure management audit

## Modeloplossing voor studenten

## 1. Korte samenvatting

Het netwerk van **BluePeak Services** heeft een bruikbare enterprise-basis met herkenbare zones:

- Staff;
- Finance;
- IT;
- Servers;
- Guests;
- IoT;
- DMZ;
- Management;
- Internet.

Toch is het netwerk nog niet volledig enterprise-ready op vlak van beschikbaarheid en secure management.

De belangrijkste vaststellingen zijn:

- sommige access switches zijn afhankelijk van een enkele uplink;
- de core/distributionlaag is een belangrijk single point of failure;
- de internetedge is niet redundant;
- default gateway redundancy is niet aangetoond;
- managementtoegang is te breed bereikbaar;
- er is geen duidelijk rollenmodel voor beheer;
- configuratieback-ups en rollback zijn onvoldoende uitgewerkt;
- failover is niet systematisch getest;
- RTO en RPO zijn niet bepaald voor kritieke functies.

Belangrijke conclusie:

> Het netwerk werkt onder normale omstandigheden, maar het gedrag bij storing, beheerfout of herstel is onvoldoende gecontroleerd.

---

## 2. Kritieke onderdelen

| Onderdeel | Toestel(len) | Zone of functie | Kritiek? | Waarom? |
|---|---|---|---|---|
| Accesslaag | `SW-ACC1`, `SW-ACC2` | clients en servers aansluiten | ja | uitval raakt volledige groepen gebruikers |
| Core/distribution | `SW-CORE` | centraal switchingpad | zeer kritisch | meerdere VLAN's en trunks hangen eraan |
| Internetedge | `R-FW` | internet, DMZ, firewall/routing | zeer kritisch | externe toegang en zonecontrole hangen eraan |
| Management | VLAN 99, management-IP's, jump host | beheer en herstel | zeer kritisch | nodig voor troubleshooting en changes |
| Servers | `SRV-APP`, `SRV-FIN` | applicaties | kritisch | bedrijfsprocessen hangen ervan af |
| DMZ | `SRV-WEB-DMZ` | publieke dienst | middel/hoog | externe gebruikers merken uitval |

Analyse:

Vooral `SW-CORE`, `R-FW` en de managementzone zijn kritisch. Als een van deze onderdelen faalt, is de impact groter dan een lokaal clientprobleem. Management is extra belangrijk omdat het ook nodig is om andere problemen op te lossen.

---

## 3. Single points of failure

| Single point of failure | Wat valt uit? | Impact | Prioriteit |
|---|---|---|---|
| `SW-CORE` | centrale forwarding tussen meerdere zones | hoog tot zeer hoog | zeer hoog |
| `R-FW` | internet, DMZ, routing/firewallfunctie | hoog tot zeer hoog | zeer hoog |
| Uplink `SW-ACC1` naar core | Staff, Finance en Guests naar rest van netwerk | middel/hoog | hoog |
| Uplink `SW-ACC2` naar core | IT, IoT, Servers, DMZ en jump host | hoog | hoog |
| Enige default gateway | inter-VLAN verkeer voor clients | hoog | hoog |
| Enige internetverbinding | internet, cloud, externe toegang | hoog | hoog |
| Managementzone via productienetwerk | beheer bij storing moeilijk | hoog | hoog |
| Geen externe configuratieback-ups | herstel na fout of defect traag | hoog | hoog |

Sterke conclusie:

> De grootste risico's zitten bij centrale componenten en beheer. Als die falen, wordt niet alleen verkeer onderbroken, maar wordt herstel zelf ook moeilijker.

---

## 4. Storingsimpactanalyse

| Storing | Getroffen zones | Gebruikersimpact | Technische oorzaak | Ernst |
|---|---|---|---|---|
| Uplink `SW-ACC1` faalt | Staff, Finance, Guests | geen toegang tot servers/internet | enkelvoudige uplink | hoog |
| Uplink `SW-ACC2` faalt | IT, IoT, Servers, DMZ en Management | IT, servers, DMZ-web en jump host verliezen connectiviteit | enkelvoudige uplink | hoog |
| `SW-CORE` faalt | bijna alle zones | netwerkbreed probleem | centrale switch zonder alternatief | zeer hoog |
| `R-FW` faalt | Internet, DMZ, routing | internet en DMZ onbereikbaar | enige edge/router/firewall | zeer hoog |
| Management VLAN onbereikbaar | IT/admins | troubleshooting moeilijk | beheerpad afhankelijk van productienetwerk | hoog |
| Foutieve trunkwijziging | Servers of management | applicaties of beheer vallen weg | geen rollback of onvoldoende test | hoog |

Analyse:

De impact verschilt per storing. Guest-uitval is meestal minder kritisch dan finance-, server- of managementuitval. De managementzone verdient prioriteit omdat ze nodig is voor herstel.

---

## 5. Redundantiebeoordeling

| Laag | Redundantie aanwezig? | Bewijs of controle | Opmerking |
|---|---|---|---|
| Access uplinks | onvoldoende | topologie, `show interfaces trunk` | access switches hebben mogelijk maar een uplink |
| STP/EtherChannel | niet bewezen | `show spanning-tree`, `show etherchannel summary` | alleen relevant bij meerdere paden |
| Default gateway | niet bewezen | `show standby`, gatewayconfiguratie | clients gebruiken vermoedelijk fysiek gatewayadres |
| Routing naar edge | beperkt | `show ip route` | afhankelijk van een edgepad |
| Internetverbinding | nee | topologie | enige internetverbinding |
| Managementtoegang | onvoldoende | bereikbaarheidstesten naar VLAN 99 | beheer te breed of te kwetsbaar |
| Configuratieherstel | onvoldoende | back-upregister ontbreekt | herstel is ad hoc |

Sterke conclusie:

> Redundantie is niet hetzelfde als beschikbaarheid. BluePeak moet kunnen aantonen welk onderdeel mag falen, welk alternatief pad dan actief wordt en hoe dat getest is.

---

## 6. Failovertestplan

| Test | Actie | Verwacht resultaat | Controle | Rollback |
|---|---|---|---|---|
| Access uplink failover | primaire uplink van access switch uitschakelen | alternatief pad neemt over indien aanwezig | ping, `show spanning-tree`, trunkstatus | uplink opnieuw inschakelen |
| EtherChannel memberlink | een memberlink down zetten | port-channel blijft up met lagere capaciteit | `show etherchannel summary` | memberlink herstellen |
| Gateway failover | active gateway uitschakelen | standby neemt virtual gateway over | `show standby`, clientping | gateway herstellen |
| Internetedge failover | primaire route of edgepad uitschakelen | backup route of noodprocedure actief | `show ip route`, internettest | route herstellen |
| Managementbereikbaarheid | beheer vanaf Staff, Guest en IT testen | alleen IT of jump server werkt | SSH/HTTPS/ping test | policy herstellen indien nodig |

Opmerking:

Niet elke test hoort live tijdens normale werking. Tests op core, edge of gateway moeten in een onderhoudsvenster of labo-omgeving gebeuren.

Sterke testconclusie:

> Een geslaagde failovertest bewijst niet alleen dat verkeer terug werkt, maar ook welk alternatief pad of toestel de rol heeft overgenomen.

---

## 7. Managementtoeganganalyse

| Toestel | Management-IP of zone | Beheerprotocol | Bereikbaar vanaf | Risico |
|---|---|---|---|---|
| `SW-CORE` | VLAN 99 | SSH/HTTPS gewenst | IT of jump server | hoog indien bereikbaar vanaf staff |
| `SW-ACC1` | VLAN 99 | SSH/HTTPS gewenst | IT of jump server | staff/guest mogen niet beheren |
| `SW-ACC2` | VLAN 99 | SSH/HTTPS gewenst | IT of jump server | IoT/servers mogen niet beheren |
| `R-FW` | managementzone | SSH/HTTPS gewenst | IT of jump server | zeer kritisch toestel |
| `SRV-MGMT-JUMP` | managementzone | beheerportaal of SSH conceptueel | IT | jump server zelf wordt kritisch |

Analyse:

Een apart management VLAN is een goede start, maar onvoldoende als het vanaf alle interne zones bereikbaar is. Management moet beperkt worden tot de IT-zone of een jump server. Telnet en HTTP zijn ongeschikt voor professioneel beheer.

Sterke conclusie:

> De managementzone moet beschouwd worden als zeer hoog vertrouwd. Staff, Guests, IoT en DMZ mogen geen beheerinterfaces bereiken.

---

## 8. Role-based management policy

| Rol | Wie? | Mag wel | Mag niet | Logging nodig? |
|---|---|---|---|---|
| Helpdesk | eerstelijnsondersteuning | status bekijken, ticketinformatie verzamelen | configuraties wijzigen | ja |
| Network operator | netwerkteam | interfaces controleren, standaard troubleshooting | firewallbeleid of core-routing wijzigen zonder goedkeuring | ja |
| Network admin | senior netwerkbeheer | switching, routing en toestelconfiguratie wijzigen | changes zonder procedure uitvoeren | ja |
| Security admin | securityverantwoordelijke | management- en firewallbeleid beoordelen | operationele wijzigingen zonder logging doen | ja |
| Auditor | interne audit of docentrol | configuraties en logs bekijken | wijzigingen uitvoeren | ja |

Analyse:

Niet elke beheerder heeft volledige rechten nodig. Role-based access vermindert risico's bij menselijke fouten en misbruik van accounts.

Kernzin:

> Least privilege geldt ook voor beheerders.

---

## 9. Secure management policy

| Onderdeel | Gewenst beleid | Waarom? |
|---|---|---|
| Managementzone | apart VLAN of apart beheernetwerk | beheerinterfaces scheiden van gebruikersverkeer |
| Toegestane bronzones | IT-zone en jump server | beheer beperken tot gecontroleerde bronnen |
| Geblokkeerde bronzones | Staff, Guests, IoT, DMZ, Internet | blootstelling beperken |
| Beheerprotocollen | SSH en HTTPS | geen onversleuteld beheer |
| Jump server | gebruiken voor beheer naar kritieke toestellen | centraal controle- en logpunt |
| Authenticatie | centraal waar mogelijk, lokale fallback gecontroleerd | schaalbaar en beheerbaar |
| Autorisatie | rollen voor helpdesk, operator, admin en auditor | least privilege |
| Logging | aanmeldingen en wijzigingen loggen | audit en incidentanalyse |
| Fallback bij storing | console of out-of-band procedure | herstel mogelijk bij productienetwerkproblemen |

Belangrijk:

In configuraties en verslagen worden geen wachtwoorden of secrets opgenomen.

---

## 10. Back-up- en rollbackprocedure

| Onderdeel | Voorstel |
|---|---|
| Welke toestellen krijgen back-ups? | `R-FW`, `SW-CORE`, `SW-ACC1`, `SW-ACC2` en kritieke managementcomponenten |
| Wanneer wordt een back-up genomen? | voor elke wijziging, na geslaagde wijziging en periodiek |
| Waar wordt de back-up bewaard? | centraal, buiten het toestel, met toegangscontrole |
| Wie mag back-ups bekijken? | network admins en auditoren volgens rol |
| Hoe wordt een wijziging getest? | vooraf bepaald testplan met toegelaten en kritieke flows |
| Wanneer doe je rollback? | als kritieke testen falen of managementtoegang wegvalt |
| Hoe documenteer je het resultaat? | change-id, datum, toestellen, tests, resultaat en eventuele rollback |

Rollbackvoorbeelden:

| Mislukte wijziging | Symptoom | Rollbackactie | Controle na rollback |
|---|---|---|---|
| Trunkwijziging | server-VLAN niet bereikbaar | vorige trunkconfiguratie herstellen | serverconnectiviteit en trunkstatus |
| Management-ACL | IT kan switch niet bereiken | vorige ACL herstellen via console/noodpad | IT naar management werkt, Staff faalt |
| Default route | internet valt weg | vorige route terugplaatsen | internettest en `show ip route` |
| Gateway redundancy | verkeerde gateway active | vorige priority/preempt herstellen | `show standby` en clienttest |

Sterke conclusie:

> Rollback is geen improvisatie achteraf. Het rollbackpad moet bekend zijn voor de wijziging start.

---

## 11. Mini-DR-plan

| Functie | Kritiek? | Gewenste RTO | Gewenste RPO | Herstelstrategie |
|---|---|---:|---:|---|
| Managementtoegang | zeer hoog | 30 minuten | laatste bekende configuratie | console/out-of-band, jump server, configback-ups |
| Core/distribution | zeer hoog | 1 uur | laatste coreconfig | reservehardware of gedocumenteerde rebuild |
| Internetedge | hoog | 1-2 uur | laatste edgeconfig | reserveconfig, noodrouter of tweede verbinding |
| Interne servers | hoog | 2-4 uur | afhankelijk van applicatie | server- en netwerkherstel prioriteren |
| DMZ-webdienst | middel/hoog | 1-2 uur | laatste DMZ/proxyconfig | DMZ-host of publicatieregel herstellen |
| Finance-app | hoog | 2 uur | maximaal 1 uur | applicatie, netwerkpad en toegangsregels prioriteren |

Analyse:

De managementfunctie krijgt een lage RTO omdat ze nodig is om andere functies te herstellen. Guestnetwerk zou een veel langere RTO mogen hebben dan finance of management.

---

## 12. Verbeterplan

| Verbeterpunt | Lost welk risico op? | Prioriteit | Hoe test je dit? |
|---|---|---|---|
| Beperk management tot IT of jump server | beheerinterfaces te breed bereikbaar | hoog | Staff/Guest/IoT naar management faalt, IT werkt |
| Voorzie configuratieback-ups | herstel na defect of fout traag | hoog | back-upregister en restoretest controleren |
| Maak rollbackprocedure verplicht | foutieve wijziging blijft impact hebben | hoog | tabletop of rollbacktest |
| Documenteer failovertesten | redundantie niet bewezen | hoog | testresultaten met controles |
| Voorzie redundante uplinks voor kritieke access switches | afdeling valt weg bij linkfout | hoog | uplink failover testen |
| Onderzoek gateway redundancy | default gateway is SPOF | hoog | `show standby` of ontwerpcontrole |
| Voorzie noodpad voor management | beheer afhankelijk van productienetwerk | hoog | console/out-of-band procedure testen |
| Werk rollenmodel uit | te veel adminrechten | middel/hoog | rechtenmatrix reviewen |
| Log beheeracties | geen auditspoor | middel/hoog | logcontrole uitvoeren |
| Bepaal RTO/RPO per kritieke functie | herstelprioriteiten onduidelijk | middel | DR-plan reviewen |

Prioriteiten:

1. Managementtoegang beperken.
2. Back-up en rollback organiseren.
3. Kritieke single points of failure aanpakken.
4. Failover testen en documenteren.
5. Rollen, logging en DR-plan verfijnen.

---

## 13. Eindconclusie

Het netwerk van BluePeak Services bevat een herkenbare enterprise-structuur met duidelijke zones en centrale netwerkcomponenten. Onder normale omstandigheden kan het netwerk functioneren, maar het is nog niet voldoende bestand tegen storingen of foutieve beheeracties.

De belangrijkste beschikbaarheidsrisico's zijn `SW-CORE`, `R-FW`, enkelvoudige access-uplinks, ontbrekende gateway redundancy en een enige internetverbinding. Deze onderdelen kunnen bij uitval meerdere zones of kritieke diensten tegelijk raken.

De belangrijkste managementrisico's zijn te brede bereikbaarheid van managementinterfaces, ontbreken van duidelijke beheerrollen, onvoldoende logging en geen formele back-up- en rollbackprocedure. Een management VLAN alleen is onvoldoende als dat VLAN vanaf gewone clientzones bereikbaar blijft.

De eerste verbeteringen zijn managementtoegang beperken tot IT of een jump server, configuratieback-ups verplicht maken, rollbackprocedures uitschrijven, kritieke failovertesten documenteren en single points of failure prioriteren op bedrijfsimpact.

Eindconclusie:

> BluePeak Services heeft een werkend netwerk, maar nog geen volledig professioneel beheerbaar enterprise-netwerk. Pas wanneer uitval, beheer, logging, back-up en rollback voorspelbaar georganiseerd zijn, is het netwerk klaar voor een bedrijfscontext.
