# Workshop 2 - Redundant enterprise core

## Modeloplossing voor studenten

## 1. Korte samenvatting

Het netwerk van **Northwind Components** bevat duidelijke enterprise-bouwstenen:

- redundante uplinks tussen access- en distributionlaag;
- STP om Layer 2-loops te voorkomen;
- EtherChannel tussen de distribution switches;
- HSRP voor gateway redundancy;
- OSPF met meerdere areas;
- een core- en edge-router;
- een servernetwerk en internetverbinding.

Toch is de beginsituatie niet volledig enterprise-ready.

De belangrijkste vaststellingen zijn:

- VLAN 99 heeft een access switch als root bridge;
- trunks laten te veel VLAN's toe en gebruiken nog native VLAN 1;
- de EtherChannel is aanwezig, maar de trunkconfiguratie is niet volledig consistent;
- `MLS-DIST2` vormt geen OSPF-neighbor met `R-CORE` door een foutieve area-indeling;
- user- en serverinterfaces op `MLS-DIST2` zijn niet passive in OSPF;
- de default route wordt niet via OSPF verspreid;
- VLAN 99 heeft geen HSRP-gateway;
- `PC-ADMIN` gebruikt een fysiek gatewayadres in plaats van een virtueel gatewayadres;
- failover is niet overal bewezen.

Belangrijke conclusie:

> Het netwerk lijkt redundant, maar meerdere redundantieonderdelen zijn niet correct of niet bewezen. Een enterprise-netwerk moet niet alleen werken tijdens normale omstandigheden, maar ook voorspelbaar blijven werken bij uitval.

---

## 2. Topologieanalyse

| Toestel | Type | Rol in het netwerk | Kritisch? Waarom? |
|---|---|---|---|
| `MLS-DIST1` | multilayer switch | distribution, inter-VLAN routing, HSRP, OSPF ABR | ja, verzorgt gateways en routing |
| `MLS-DIST2` | multilayer switch | tweede distribution switch, HSRP, OSPF ABR | ja, moet redundantie bieden |
| `SW-ACC1` | access switch | clients in VLAN 10 en 20 | ja, toegang voor gebruikers/magazijn |
| `SW-ACC2` | access switch | clients, server en managementclient | ja, bevat server en adminclient |
| `R-CORE` | router | backbone/core-router in area 0 | ja, verbindt distribution en edge |
| `R-EDGE` | router | internet edge | ja, levert default route naar buiten |
| `SRV-APP` | server | applicatieserver in VLAN 50 | ja, bedrijfsapplicatie |
| `ISP-SERVER` | server | externe testbestemming | nee, simulatie van internet |

Topologische vaststelling:

```text
Accesslaag  -> SW-ACC1, SW-ACC2
Distribution -> MLS-DIST1, MLS-DIST2
Core         -> R-CORE
Edge         -> R-EDGE
Internet     -> ISP-SERVER
```

De access switches hebben redundante uplinks naar beide distribution switches. Dat is positief, maar die redundantie moet gecontroleerd worden via STP, trunks en failovertesten.

De distribution switches vormen samen de gatewaylaag voor de VLAN's. Dat is een goed enterprise-principe, maar alleen als HSRP correct per VLAN werkt en clients de virtual gateway gebruiken.

---

## 3. VLAN-analyse

| VLAN | Naam | Waar gebruikt? | Functie | Opmerking |
|---:|---|---|---|---|
| 10 | `OFFICE_A` | `SW-ACC1`, distribution switches | kantoorvleugel A | hoort bij area 10 |
| 20 | `WAREHOUSE` | `SW-ACC1`, distribution switches | magazijn | hoort bij area 10 |
| 30 | `OFFICE_B` | `SW-ACC2`, distribution switches | kantoorvleugel B | hoort bij area 20 |
| 50 | `SERVERS` | `SW-ACC2`, distribution switches | applicatieserver | kritisch VLAN |
| 99 | `MGMT` | access en distribution switches | management | kritisch beheer-VLAN |

Analyse:

De VLAN-indeling is logisch gekozen. VLAN 10 en 20 horen bij gebouw of zone A, VLAN 30 en 50 bij gebouw of zone B, en VLAN 99 is bedoeld voor management.

Risico:

Het bestaan van correcte VLAN's betekent niet automatisch dat de VLAN's correct over trunks lopen. Dat moet apart gecontroleerd worden.

Sterke conclusie:

> De VLAN-namen en functies zijn logisch. De volgende controle is of deze VLAN's alleen aanwezig zijn waar ze nodig zijn en of trunkpoorten correct beperkt zijn.

---

## 4. Trunkanalyse

| Switch | Poort | Naar | Trunk? | Allowed VLAN's | Native VLAN | Opmerking |
|---|---|---|---|---|---|---|
| `SW-ACC1` | `Fa0/23` | `MLS-DIST1` | ja | te breed of default | VLAN 1 | trunk werkt, maar is niet beperkt |
| `SW-ACC1` | `Fa0/24` | `MLS-DIST2` | ja | te breed of default | VLAN 1 | trunk werkt, maar is niet beperkt |
| `SW-ACC2` | `Fa0/23` | `MLS-DIST1` | ja | te breed of default | VLAN 1 | trunk werkt, maar is niet beperkt |
| `SW-ACC2` | `Fa0/24` | `MLS-DIST2` | ja | te breed of default | VLAN 1 | trunk werkt, maar is niet beperkt |
| `MLS-DIST1` | `Po1` | `MLS-DIST2` | ja | `10,20,30,50,99` | VLAN 1 | bevat VLAN 50 |
| `MLS-DIST2` | `Po1` | `MLS-DIST1` | ja | `10,20,30,99` | VLAN 1 | VLAN 50 ontbreekt |

Analyse:

De trunks bestaan en zorgen ervoor dat VLAN's tussen access en distribution kunnen lopen. Toch is de trunkconfiguratie niet enterprise-ready:

- access trunks zijn te breed;
- native VLAN blijft VLAN 1;
- de EtherChannel trunk is niet consistent tussen beide distribution switches;
- VLAN 50 ontbreekt op de Port-channel-kant van `MLS-DIST2`.

Waarom is dit belangrijk?

Een trunk die alle VLAN's toelaat, werkt vaak in een lab, maar verspreidt VLAN's breder dan nodig. Dat maakt het netwerk minder overzichtelijk en vergroot de impact van fouten.

De mismatch op `Po1` is ernstiger. De EtherChannel lijkt aanwezig, maar de VLAN-toelating is niet aan beide kanten gelijk. Voor een server-VLAN zoals VLAN 50 is dat een risico.

Verbeterpunt:

```text
switchport trunk allowed vlan 10,20,30,50,99
```

Dit moet consistent toegepast worden op beide kanten van relevante trunks.

---

## 5. STP-analyse

| VLAN | Root bridge | Waarom? | Blocked/alternate poorten | Beoordeling |
|---:|---|---|---|---|
| 10 | `MLS-DIST1` | lagere STP-priority voor VLAN 10 | afhankelijk van access-uplinks | logisch |
| 20 | `MLS-DIST1` | lagere STP-priority voor VLAN 20 | afhankelijk van access-uplinks | logisch |
| 30 | `MLS-DIST2` | lagere STP-priority voor VLAN 30 | afhankelijk van access-uplinks | logisch |
| 50 | `MLS-DIST2` | lagere STP-priority voor VLAN 50 | afhankelijk van access-uplinks | logisch, maar controleer trunk VLAN 50 |
| 99 | `SW-ACC1` | `SW-ACC1` heeft lage priority voor VLAN 99 | distribution uplinks kunnen onlogisch reageren | niet logisch |

Voorbeeldbewijs voor VLAN 99:

```text
Root ID
  This bridge is the root
```

Wanneer dit op `SW-ACC1` verschijnt, betekent dit dat `SW-ACC1` zelf root bridge is voor VLAN 99.

Waarom is dit fout?

VLAN 99 is het management-VLAN. In een enterprise-ontwerp hoort een access switch normaal niet het STP-referentiepunt voor managementverkeer te zijn. De root bridge hoort eerder in de distributionlaag te staan.

Goede analyse:

> VLAN 99 werkt mogelijk technisch, maar de root bridge-keuze is onlogisch. Een access switch als root bridge maakt het STP-gedrag minder voorspelbaar en geeft een randtoestel te veel invloed op het management-VLAN.

Verbeterpunt:

- `MLS-DIST1` primary root voor VLAN 99;
- `MLS-DIST2` secondary root voor VLAN 99;
- `SW-ACC1` niet langer root voor VLAN 99.

Mogelijke correctie:

```text
MLS-DIST1(config)# spanning-tree vlan 99 priority 4096
MLS-DIST2(config)# spanning-tree vlan 99 priority 8192
SW-ACC1(config)# no spanning-tree vlan 99 priority 4096
```

---

## 6. EtherChannel-analyse

| Toestel | Port-channel | Memberpoorten | Status | Trunk? | Allowed VLAN's | Opmerking |
|---|---|---|---|---|---|---|
| `MLS-DIST1` | `Po1` | `Fa0/23`, `Fa0/24` | gevormd | ja | `10,20,30,50,99` | verwacht |
| `MLS-DIST2` | `Po1` | `Fa0/23`, `Fa0/24` | gevormd | ja | `10,20,30,99` | VLAN 50 ontbreekt |

Analyse:

De fysieke links tussen `MLS-DIST1` en `MLS-DIST2` zijn gebundeld in een EtherChannel. Dat is positief: STP ziet de bundel als een logische link en de twee fysieke links kunnen samen redundantie en capaciteit bieden.

Maar:

> De EtherChannel is pas betrouwbaar als de trunkinstellingen consistent zijn.

VLAN 50 ontbreekt aan de kant van `MLS-DIST2`. Daardoor is de bundel niet logisch gelijk geconfigureerd. Dit kan vooral impact hebben op het server-VLAN.

Sterke conclusie:

> `Po1` bestaat, maar de allowed VLAN-lijst is niet consistent. De EtherChannel lijkt daardoor correct aanwezig, maar is niet volledig betrouwbaar voor alle VLAN's.

Verbeterpunt:

```text
MLS-DIST2(config)# interface port-channel 1
MLS-DIST2(config-if)# switchport trunk allowed vlan 10,20,30,50,99
```

---

## 7. OSPF-neighboranalyse

| Toestel | Verwachte neighbor | Interface | Neighbor aanwezig? | Opmerking |
|---|---|---|---|---|
| `MLS-DIST1` | `R-CORE` | `Gi0/1` | ja | link in area 0 |
| `MLS-DIST2` | `R-CORE` | `Gi0/1` | nee | area mismatch |
| `R-CORE` | `MLS-DIST1` | `Gi0/0` | ja | correct |
| `R-CORE` | `MLS-DIST2` | `Gi0/1` | nee | area mismatch |
| `R-CORE` | `R-EDGE` | `Gi0/2` | ja | backbone link |
| `R-EDGE` | `R-CORE` | `Gi0/0` | ja | backbone link |

Analyse:

`MLS-DIST1` vormt correct een OSPF-neighbor met `R-CORE`. `R-EDGE` vormt ook correct een neighbor met `R-CORE`.

`MLS-DIST2` vormt geen OSPF-neighbor met `R-CORE`.

Oorzaak:

De link tussen `MLS-DIST2` en `R-CORE` gebruikt aan de ene kant area 20 en aan de andere kant area 0. Beide kanten van dezelfde OSPF-link moeten in dezelfde area zitten.

Sterke conclusie:

> De IP-link tussen `MLS-DIST2` en `R-CORE` kan fysiek up zijn, maar OSPF vormt geen neighbor omdat de area-instellingen niet overeenkomen. Hierdoor is de routingredundantie via `MLS-DIST2` niet betrouwbaar.

Correctie:

```text
MLS-DIST2(config)# router ospf 1
MLS-DIST2(config-router)# no network 10.0.0.4 0.0.0.3 area 20
MLS-DIST2(config-router)# network 10.0.0.4 0.0.0.3 area 0
```

---

## 8. OSPF-area-analyse

| Toestel | Interface/netwerk | Area | Rol van toestel | Opmerking |
|---|---|---:|---|---|
| `MLS-DIST1` | link naar `R-CORE` | 0 | ABR | correct |
| `MLS-DIST1` | VLAN 10, 20 | 10 | ABR | logisch voor zone A |
| `MLS-DIST1` | VLAN 30, 50, 99 | 20 | ABR | logisch voor zone B/management |
| `MLS-DIST2` | link naar `R-CORE` | 20 in beginsituatie | ABR bedoeld | fout, moet area 0 zijn |
| `MLS-DIST2` | VLAN 10, 20 | 10 | ABR bedoeld | logisch |
| `MLS-DIST2` | VLAN 30, 50, 99 | 20 | ABR bedoeld | logisch |
| `R-CORE` | links naar distribution en edge | 0 | backbone router | correct |
| `R-EDGE` | link naar `R-CORE` | 0 | edge/ASBR | correct |

Analyse:

Het conceptuele OSPF-area-ontwerp is goed:

- area 0 is de backbone;
- area 10 groepeert VLAN 10 en 20;
- area 20 groepeert VLAN 30, 50 en 99;
- de distribution switches zijn bedoeld als ABR's.

Maar de uitvoering is niet volledig correct, omdat `MLS-DIST2` zijn link naar `R-CORE` niet in area 0 plaatst. Daardoor is `MLS-DIST2` niet correct verbonden met de backbone.

Daarnaast zijn user- en serverinterfaces op `MLS-DIST2` niet passive. Daardoor kan OSPF hello's sturen op VLAN's waar geen OSPF-neighbors verwacht worden.

Verbeterpunt:

```text
MLS-DIST2(config)# router ospf 1
MLS-DIST2(config-router)# passive-interface default
MLS-DIST2(config-router)# no passive-interface gi0/1
```

Waarom?

De routed link naar `R-CORE` moet neighbors vormen. User- en server-VLAN's moeten wel geadverteerd worden, maar hoeven geen OSPF-neighbors te zoeken.

---

## 9. Routinganalyse

| Toestel | Route naar area 10? | Route naar area 20? | Inter-area routes `O IA`? | Default route? | Opmerking |
|---|---|---|---|---|---|
| `MLS-DIST1` | connected voor VLAN 10/20 | connected of OSPF voor VLAN 30/50/99 | ja, afhankelijk van routes | nee in beginsituatie | geen default geleerd |
| `MLS-DIST2` | connected voor VLAN's | connected voor VLAN's | onvolledig | nee in beginsituatie | OSPF-neighbor met core ontbreekt |
| `R-CORE` | via OSPF | via OSPF, maar onvolledig voor `MLS-DIST2` | ja | nee in beginsituatie | default ontbreekt |
| `R-EDGE` | via OSPF | via OSPF | ja | ja, statisch naar ISP | default niet gepropageerd |

Analyse:

Interne routing kan gedeeltelijk werken, vooral via `MLS-DIST1`, omdat `MLS-DIST1` wel een OSPF-neighbor vormt met `R-CORE`.

Toch is de routing niet enterprise-ready:

- `MLS-DIST2` heeft geen correcte OSPF-neighbor met `R-CORE`;
- routes via `MLS-DIST2` zijn daardoor niet betrouwbaar;
- de default route wordt niet verspreid naar interne routers of switches.

Belangrijk onderscheid:

> Interne routes kunnen werken terwijl internetverkeer faalt. Dat betekent dat OSPF gedeeltelijk werkt, maar dat de default route ontbreekt.

Correctie default route:

```text
R-EDGE(config)# router ospf 1
R-EDGE(config-router)# default-information originate
```

Na correctie zou op interne toestellen een default route zichtbaar moeten zijn, vaak als:

```text
O*E2 0.0.0.0/0
```

---

## 10. HSRP-analyse

| VLAN | Virtual gateway | Active toestel | Standby toestel | Clientgateway correct? | Opmerking |
|---:|---|---|---|---|---|
| 10 | `10.10.10.1` | `MLS-DIST1` | `MLS-DIST2` | ja | logisch |
| 20 | `10.10.20.1` | `MLS-DIST1` | `MLS-DIST2` | ja | logisch |
| 30 | `10.20.30.1` | `MLS-DIST2` | `MLS-DIST1` | ja | logisch |
| 50 | `10.20.50.1` | `MLS-DIST2` | `MLS-DIST1` | ja | logisch, maar trunk VLAN 50 controleren |
| 99 | geen HSRP in beginsituatie | n.v.t. | n.v.t. | nee | managementgateway is single point of failure |

Analyse:

HSRP werkt voor VLAN 10, 20, 30 en 50. Dat is positief. Clients gebruiken daar een virtual gateway.

Voor VLAN 99 ontbreekt HSRP. `PC-ADMIN` gebruikt `10.99.0.2`, het fysieke SVI-adres van `MLS-DIST1`, als default gateway.

Waarom is dit slecht?

Als `MLS-DIST1` uitvalt, verliest `PC-ADMIN` zijn gateway. `MLS-DIST2` kan dit niet automatisch overnemen, omdat er geen virtual gateway voor VLAN 99 is geconfigureerd en de client niet naar een virtual IP wijst.

Sterke conclusie:

> HSRP is aanwezig voor de meeste gebruikers- en server-VLAN's, maar niet voor het management-VLAN. Net het management-VLAN blijft daardoor afhankelijk van een fysieke gateway. Dat is een belangrijk enterprise-risico.

Extra observatie:

Als je meldingen ziet zoals:

```text
%HSRP-6-STATECHANGE: Vlan50 Grp 50 state Standby -> Active
```

dan moet je niet alleen naar HSRP kijken. Voor VLAN 50 moet je ook de onderliggende Layer 2-bereikbaarheid controleren. In deze case is de allowed VLAN-lijst op `Po1` niet consistent: VLAN 50 ontbreekt aan een kant van de EtherChannel. Daardoor kunnen HSRP-hellos of VLAN 50-verkeer onstabiel worden of via een onverwacht pad lopen.

Goede controlevolgorde:

```text
show standby
show interfaces trunk
show etherchannel summary
show spanning-tree vlan 50
```

Correctie:

Op `MLS-DIST1`:

```text
interface vlan 99
 standby 99 ip 10.99.0.1
 standby 99 priority 110
 standby 99 preempt
```

Op `MLS-DIST2`:

```text
interface vlan 99
 standby 99 ip 10.99.0.1
 standby 99 priority 100
 standby 99 preempt
```

Daarna moet `PC-ADMIN` deze gateway gebruiken:

```text
10.99.0.1
```

---

## 11. Connectiviteitstesten

| Test | Bron | Bestemming | Verwacht | Werkelijk in beginsituatie | Conclusie |
|---|---|---|---|---|---|
| Gateway VLAN 10 | `PC-OFFICE-A` | `10.10.10.1` | werkt | werkt normaal | HSRP VLAN 10 bereikbaar |
| Gateway VLAN 20 | `PC-WAREHOUSE` | `10.10.20.1` | werkt | werkt normaal | HSRP VLAN 20 bereikbaar |
| Gateway VLAN 30 | `PC-OFFICE-B` | `10.20.30.1` | werkt | werkt normaal | HSRP VLAN 30 bereikbaar |
| Servergateway | `SRV-APP` | `10.20.50.1` | werkt | afhankelijk van VLAN 50-pad | controleer Po1/VLAN 50 |
| Client naar server | `PC-OFFICE-A` | `10.20.50.10` | werkt na correcte routing/VLAN's | mogelijk onstabiel of faalt | VLAN 50 en routing controleren |
| Client naar ISP | interne pc | `198.51.100.2` | werkt als default route verspreid is | faalt | default route ontbreekt intern |
| Managementgateway fysiek | `PC-ADMIN` | `10.99.0.2` | werkt | werkt normaal | maar geen redundantie |
| Management virtual gateway | `PC-ADMIN` | `10.99.0.1` | zou moeten werken na HSRP | faalt | HSRP VLAN 99 ontbreekt |

Belangrijke interpretatie:

Een geslaagde ping naar een gateway bewijst alleen dat de gateway op dat moment bereikbaar is. Het bewijst niet dat failover werkt.

Sterke analyse:

> De basistesten tonen dat sommige VLAN's functioneel zijn, maar internettoegang en managementgatewayredundantie zijn niet correct. Daarom moet de conclusie verder gaan dan "pings werken".

---

## 12. Failovertestresultaten

### 12.1 Access uplink failure

| Test | Actie | Verwacht | Resultaat | Verklaring |
|---|---|---|---|---|
| Access uplink | shutdown actieve uplink op access switch | STP activeert alternatief pad | werkt na STP-convergentie als trunks correct zijn | STP voorkomt loop en gebruikt back-uppad |

Analyse:

Dit is normale Layer 2-redundantie. Een geblokkeerde STP-poort kan forwarding worden wanneer het actieve pad wegvalt.

### 12.2 EtherChannel member failure

| Test | Actie | Verwacht | Resultaat | Verklaring |
|---|---|---|---|---|
| EtherChannel member | shutdown `Fa0/23` of `Fa0/24` | `Po1` blijft up met minder memberlinks | werkt als andere member actief blijft | EtherChannel blijft logisch up |

Analyse:

Als een memberlink wegvalt, blijft de Port-channel werken via de overblijvende link. Dat is positief, maar de bundel is dan gedegradeerd.

Sterke conclusie:

> Het netwerk blijft werken, maar de EtherChannel heeft minder capaciteit en minder redundantie. Dit moet gemonitord worden.

### 12.3 HSRP failover VLAN 10/20/30/50

| VLAN | Actie | Verwacht | Resultaat | Verklaring |
|---:|---|---|---|---|
| 10 | active gateway op `MLS-DIST1` uitschakelen | `MLS-DIST2` wordt active | werkt normaal | HSRP neemt over |
| 20 | active gateway op `MLS-DIST1` uitschakelen | `MLS-DIST2` wordt active | werkt normaal | HSRP neemt over |
| 30 | active gateway op `MLS-DIST2` uitschakelen | `MLS-DIST1` wordt active | werkt normaal | HSRP neemt over |
| 50 | active gateway op `MLS-DIST2` uitschakelen | `MLS-DIST1` wordt active | controleer VLAN 50-trunk | HSRP kan werken, maar Layer 2-pad moet kloppen |

Analyse:

HSRP voorziet gatewayfailover voor deze VLAN's. De clientgateway blijft hetzelfde virtuele IP-adres.

### 12.4 HSRP failover VLAN 99

| Test | Actie | Verwacht enterprise-gedrag | Werkelijk in beginsituatie | Conclusie |
|---|---|---|---|---|
| Managementgateway | `MLS-DIST1` uit of SVI down | `MLS-DIST2` neemt virtual gateway over | failover werkt niet | VLAN 99 heeft geen HSRP |

Analyse:

VLAN 99 is niet beschermd door HSRP. `PC-ADMIN` gebruikt een fysiek gatewayadres. Dit is een single point of failure.

### 12.5 OSPF routed link failure

| Test | Actie | Verwacht | Werkelijk in beginsituatie | Conclusie |
|---|---|---|---|---|
| Link `MLS-DIST1` naar core uit | shutdown `MLS-DIST1 Gi0/1` | routes blijven via `MLS-DIST2` beschikbaar | faalt of onvolledig | `MLS-DIST2` heeft geen OSPF-neighbor met core |

Analyse:

De fysieke redundantie bestaat, maar de routingredundantie faalt zolang de OSPF area mismatch niet opgelost is.

Sterke conclusie:

> Redundante fysieke paden zijn onvoldoende als het routingprotocol niet correct over die paden werkt.

---

## 13. Risico's en verbeterpunten

| Vaststelling | Risico | Impact | Verbeterpunt |
|---|---|---|---|
| `SW-ACC1` is root bridge voor VLAN 99 | management-VLAN hangt logisch aan access switch | onvoorspelbare STP-topologie | `MLS-DIST1` primary root, `MLS-DIST2` secondary root |
| Trunks zijn te breed | VLAN's worden onnodig verspreid | groter foutdomein en minder overzicht | allowed VLAN's beperken |
| Native VLAN blijft VLAN 1 | zwakke standaardconfiguratie | minder professioneel ontwerp | aparte native VLAN gebruiken |
| `Po1` mist VLAN 50 op een kant | server-VLAN niet consistent over bundel | serverbereikbaarheid of failover kan falen | VLAN 50 toevoegen aan allowed list |
| `MLS-DIST2` vormt geen OSPF-neighbor met core | routingredundantie ontbreekt | failover via `MLS-DIST2` werkt niet | routed link in area 0 zetten |
| User/serverinterfaces op `MLS-DIST2` niet passive | OSPF zichtbaar op clientnetwerken | onnodige routing-ruis en slechter ontwerp | `passive-interface default` gebruiken |
| Default route niet gepropageerd | interne toestellen kennen internetroute niet | internetverkeer faalt | `default-information originate` op `R-EDGE` |
| VLAN 99 heeft geen HSRP | managementgateway is single point of failure | adminconnectiviteit faalt bij uitval `MLS-DIST1` | HSRP groep 99 toevoegen |
| `PC-ADMIN` gebruikt fysiek gateway-IP | HSRP zou niet helpen | gateway blijft toestelafhankelijk | gateway wijzigen naar `10.99.0.1` |
| Failover niet gedocumenteerd | redundantie blijft aanname | fouten blijven verborgen | testplan uitvoeren en resultaten noteren |

---

## 14. Mogelijke verbeterconfiguratie

### 14.1 STP-root VLAN 99

```text
MLS-DIST1(config)# spanning-tree vlan 99 priority 4096
MLS-DIST2(config)# spanning-tree vlan 99 priority 8192
SW-ACC1(config)# no spanning-tree vlan 99 priority 4096
```

### 14.2 EtherChannel VLAN 50 herstellen

```text
MLS-DIST2(config)# interface port-channel 1
MLS-DIST2(config-if)# switchport trunk allowed vlan 10,20,30,50,99
```

### 14.3 OSPF area mismatch herstellen

```text
MLS-DIST2(config)# router ospf 1
MLS-DIST2(config-router)# no network 10.0.0.4 0.0.0.3 area 20
MLS-DIST2(config-router)# network 10.0.0.4 0.0.0.3 area 0
```

### 14.4 Passive interfaces verbeteren

```text
MLS-DIST2(config)# router ospf 1
MLS-DIST2(config-router)# passive-interface default
MLS-DIST2(config-router)# no passive-interface gi0/1
```

### 14.5 Default route verspreiden

```text
R-EDGE(config)# router ospf 1
R-EDGE(config-router)# default-information originate
```

### 14.6 HSRP voor VLAN 99 toevoegen

Op `MLS-DIST1`:

```text
interface vlan 99
 standby 99 ip 10.99.0.1
 standby 99 priority 110
 standby 99 preempt
```

Op `MLS-DIST2`:

```text
interface vlan 99
 standby 99 ip 10.99.0.1
 standby 99 priority 100
 standby 99 preempt
```

Op `PC-ADMIN`:

```text
default gateway: 10.99.0.1
```

### 14.7 Trunks beperken

Beperk trunks niet overal met exact dezelfde VLAN-lijst. Laat per access switch alleen de VLAN's toe die daar nodig zijn. Anders maak je onnodige Layer 2-paden voor VLAN's die daar geen hosts hebben.

Op de interdistribution EtherChannel:

```text
interface port-channel 1
switchport trunk allowed vlan 10,20,30,50,99
```

Op de uplinks naar `SW-ACC1`, waar VLAN 10, 20 en management nodig zijn:

```text
interface fa0/1
 switchport trunk allowed vlan 10,20,99
```

Op `SW-ACC1` zelf:

```text
interface range fa0/23 - 24
 switchport trunk allowed vlan 10,20,99
```

Op de uplinks naar `SW-ACC2`, waar VLAN 30, 50 en management nodig zijn:

```text
interface fa0/2
 switchport trunk allowed vlan 30,50,99
```

Op `SW-ACC2` zelf:

```text
interface range fa0/23 - 24
 switchport trunk allowed vlan 30,50,99
```

Optioneel kan een aparte native VLAN gebruikt worden, bijvoorbeeld VLAN 999. Dit moet dan consequent op beide kanten van elke trunk gebeuren.

---

## 15. Eindcontrole na correcties

| Controle | Commando/test | Verwacht resultaat |
|---|---|---|
| STP VLAN 99 | `show spanning-tree vlan 99` | `MLS-DIST1` is root, `MLS-DIST2` secondary |
| EtherChannel | `show etherchannel summary` | `Po1` actief met beide memberlinks |
| Trunks | `show interfaces trunk` | VLAN 10,20,30,50,99 consistent toegelaten |
| OSPF neighbors | `show ip ospf neighbor` | `MLS-DIST1`, `MLS-DIST2`, `R-CORE`, `R-EDGE` vormen verwachte neighbors |
| OSPF routes | `show ip route` | `O IA` routes zichtbaar waar verwacht |
| Default route | `show ip route` | interne toestellen zien `0.0.0.0/0` via OSPF |
| HSRP | `show standby` | VLAN 10,20,30,50,99 hebben active/standby |
| HSRP VLAN 99 | ping `10.99.0.1` vanaf `PC-ADMIN` | werkt |
| Internettest | ping `198.51.100.2` vanaf client | werkt na default route |
| Failovertest | active gateway of uplink uitschakelen | korte onderbreking mogelijk, daarna herstel |

---

## 16. Modelconclusie

Het netwerk van Northwind Components bevat meerdere enterprise-bouwstenen, zoals redundante uplinks, STP, EtherChannel, multi-area OSPF en HSRP. Dat is een sterke basis.

De beginsituatie is echter niet volledig enterprise-ready. VLAN 99 heeft een access switch als root bridge, waardoor het management-VLAN een onlogische STP-topologie heeft. De EtherChannel tussen de distribution switches bestaat, maar de allowed VLAN-lijst is niet consistent omdat VLAN 50 aan een kant ontbreekt. `MLS-DIST2` vormt geen OSPF-neighbor met `R-CORE` door een area mismatch, waardoor routingredundantie richting core niet betrouwbaar is. De default route wordt niet via OSPF verspreid, waardoor internetverkeer vanuit interne netwerken kan falen. Voor VLAN 99 ontbreekt HSRP en gebruikt `PC-ADMIN` een fysiek gatewayadres, waardoor de managementgateway een single point of failure blijft.

De belangrijkste verbeteringen zijn: STP-root voor VLAN 99 verplaatsen naar de distributionlaag, EtherChannel-trunks consistent maken, de OSPF area mismatch oplossen, passive interfaces correct instellen, de default route propageren via OSPF en HSRP toevoegen voor VLAN 99.

Eindconclusie:

> Het netwerk lijkt redundant, maar de redundantie is niet overal correct uitgevoerd of bewezen. Na de correcties moet het netwerk opnieuw getest worden met gerichte failovertesten. Pas wanneer STP, EtherChannel, OSPF, HSRP en default route propagation samen correct blijven werken bij uitval, kan je spreken van een enterprise-ready redundant core-ontwerp.
