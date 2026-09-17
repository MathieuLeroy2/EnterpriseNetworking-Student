# Workshop 2 - Redundant enterprise core

## 1. Situering

In dit hoofdstuk onderzoek je een enterprise-netwerk dat op het eerste gezicht redundant en professioneel lijkt.

Het netwerk bevat onder andere:

- access switches met redundante uplinks;
- een distributionlaag met multilayer switches;
- STP;
- EtherChannel;
- OSPF met meerdere areas;
- HSRP als gateway redundancy;
- een servernetwerk;
- een internet edge.

Je opdracht is niet om meteen commando's te typen en willekeurig zaken te herstellen. Je analyseert eerst wat er aanwezig is, wat correct werkt en waar het ontwerp risico's bevat.

Belangrijk:

> Een netwerk dat pings doorlaat, is niet automatisch enterprise-ready.

---

## 2. Scenario

Het bedrijf **Northwind Components** heeft een groeiende campus met twee kantoorvleugels, een magazijnzone, een servernetwerk en een centrale internetverbinding.

Het bedrijf wil dat het netwerk beter bestand is tegen storingen:

- een access uplink mag niet meteen een volledige zone offline halen;
- de default gateway van clients mag geen single point of failure zijn;
- routing tussen campusdelen moet schaalbaar blijven;
- de internetroute moet gecontroleerd beschikbaar zijn;
- failover moet getest kunnen worden.

Jij onderzoekt of het huidige Packet Tracer-netwerk dit effectief waarmaakt.

---

## 3. Beginsituatie

Je krijgt een Packet Tracer-bestand met een bestaand netwerk.

Het netwerk bevat bewust meerdere enterprise-bouwstenen. Sommige onderdelen werken correct, andere onderdelen moet je kritisch onderzoeken.

Werk methodisch:

- breng eerst de topologie in kaart;
- controleer daarna VLAN's en trunks;
- analyseer STP en root bridge-keuzes;
- controleer EtherChannel;
- onderzoek OSPF-neighbors en areas;
- analyseer routingtabellen;
- controleer HSRP;
- voer pas daarna gerichte failovertesten uit;
- formuleer risico's en verbeterpunten.

Pas niet meteen configuraties aan. Noteer eerst je vaststellingen.

---

## 4. Doelen

Na deze workshop kan je:

1. een redundant Packet Tracer-netwerk methodisch analyseren;
2. bepalen welke switches, links en gateways kritisch zijn;
3. VLAN's, trunks en toegelaten VLAN's controleren;
4. STP-root bridges per VLAN bepalen;
5. verklaren waarom een poort forwarding of blocked is;
6. controleren of een EtherChannel correct gevormd is;
7. OSPF-neighbors en OSPF-areas analyseren;
8. inter-area routes herkennen in een routing table;
9. nagaan of een default route verspreid wordt;
10. HSRP active/standby-rollen controleren;
11. failover testen en verklaren;
12. risico's en verbeterpunten formuleren vanuit enterprise-denken.

---

## 5. Benodigdheden

Je hebt nodig:

- Cisco Packet Tracer;
- het Packet Tracer-bestand van workshop 2;
- dit workshopdocument;
- het cursushoofdstuk **Switching/routing essentials**;
- een tekstverwerker of Markdown-editor voor je analyse;
- eventueel papier of een digitaal tekenprogramma voor een topologieschets.

Je gebruikt voorkennis over:

- VLAN's en trunks;
- STP;
- EtherChannel en LACP;
- OSPF;
- OSPF areas;
- HSRP;
- routingtabellen;
- `show`-commando's;
- `ping` en eventueel `traceroute`.

---

## 6. Werkwijze

Gebruik deze volgorde:

1. topologie verkennen;
2. VLAN's en trunks controleren;
3. STP-status analyseren;
4. root bridge bepalen;
5. EtherChannel controleren;
6. OSPF-neighbors controleren;
7. OSPF-areas en inter-area routes analyseren;
8. routingtabellen en default route controleren;
9. HSRP controleren;
10. link- en gatewayfailover simuleren;
11. risico's en verbeterpunten formuleren;
12. eindconclusie schrijven.

---

## 7. Stap 1: verken de topologie

Open het Packet Tracer-bestand en bekijk eerst de fysieke en logische opbouw.

Beantwoord:

- Welke routers zijn aanwezig?
- Welke multilayer switches zijn aanwezig?
- Welke access switches zijn aanwezig?
- Welke clients en servers zijn aanwezig?
- Waar zit de internet edge?
- Welke verbindingen lijken redundant?
- Welke toestellen lijken kritisch?
- Welke verbindingen lijken Layer 2-trunks?
- Welke verbindingen lijken routed links?

Maak een topologieschets.

Je tekening moet minstens tonen:

- toestelnamen;
- verbindingen tussen toestellen;
- belangrijke poorten;
- accesslaag;
- distributionlaag;
- core/edge;
- serverlocatie;
- redundante paden.

Vul aan:

| Toestel | Type | Rol in het netwerk | Kritisch? Waarom? |
|---|---|---|---|
| ... | ... | ... | ... |
| ... | ... | ... | ... |

Controlepunt:

> Kan iemand anders aan de hand van je tekening begrijpen waar redundantie aanwezig lijkt te zijn?

---

## 8. Stap 2: breng VLAN's in kaart

Onderzoek welke VLAN's bestaan en waar ze gebruikt worden.

Gebruik bijvoorbeeld:

```text
show vlan brief
show interfaces trunk
show running-config
```

Vul deze tabel in:

| VLAN | Naam | Waar gebruikt? | Functie | Opmerking |
|---:|---|---|---|---|
| ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |

Beantwoord:

- Welke VLAN's bestaan op de switches?
- Welke accesspoorten horen bij welk VLAN?
- Welke VLAN's gaan over trunks?
- Worden alleen noodzakelijke VLAN's over trunks toegelaten?
- Is de native VLAN expliciet gekozen?
- Zijn VLAN-namen en functies logisch?

Controlepunt:

> Is elk VLAN aanwezig waar het nodig is, maar niet breder verspreid dan nodig?

---

## 9. Stap 3: controleer trunks

Onderzoek de trunks tussen access switches en distribution switches.

Gebruik bijvoorbeeld:

```text
show interfaces trunk
show running-config interface ...
```

Vul deze tabel in:

| Switch | Poort | Naar | Trunk? | Allowed VLAN's | Native VLAN | Opmerking |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... |

Beantwoord:

- Welke poorten zijn trunks?
- Welke VLAN's zijn toegelaten?
- Zijn trunks consistent aan beide kanten?
- Zijn er trunks die te veel VLAN's toelaten?
- Welke trunks zijn belangrijk voor redundantie?

Controlepunt:

> Een trunk die technisch werkt, is niet automatisch goed ontworpen. Kan je uitleggen of de trunk beperkt en logisch is?

---

## 10. Stap 4: analyseer STP

Onderzoek STP per belangrijk VLAN.

Gebruik bijvoorbeeld:

```text
show spanning-tree
show spanning-tree vlan 10
show spanning-tree vlan 20
show spanning-tree vlan 30
show spanning-tree vlan 50
show spanning-tree vlan 99
```

Vul deze tabel in:

| VLAN | Root bridge | Waarom denk je dat? | Blocked/alternate poorten | Beoordeling |
|---:|---|---|---|---|
| 10 | ... | ... | ... | ... |
| 20 | ... | ... | ... | ... |
| 30 | ... | ... | ... | ... |
| 50 | ... | ... | ... | ... |
| 99 | ... | ... | ... | ... |

Beantwoord:

- Welke switch is root bridge per VLAN?
- Is die root bridge logisch?
- Welke poorten zijn forwarding?
- Welke poorten zijn blocked of alternate?
- Kan je verklaren waarom die poorten blocked zijn?
- Past de STP-keuze bij het enterprise-ontwerp?

Controlepunt:

> Een blocked poort is niet automatisch fout. Kan je verklaren welke loop STP probeert te vermijden?

---

## 11. Stap 5: controleer EtherChannel

Onderzoek of er EtherChannel gebruikt wordt tussen de distribution switches.

Gebruik bijvoorbeeld:

```text
show etherchannel summary
show interfaces trunk
show running-config interface port-channel 1
```

Vul deze tabel in:

| Toestel | Port-channel | Memberpoorten | Status | Trunk? | Allowed VLAN's | Opmerking |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... |

Beantwoord:

- Bestaat er een Port-channel?
- Welke fysieke poorten zitten in de bundel?
- Zijn alle verwachte memberlinks actief?
- Is de Port-channel een trunk?
- Zijn de allowed VLAN's op beide kanten consistent?
- Wat gebeurt er als een memberlink uitvalt?

Controlepunt:

> Kan je bewijzen dat twee fysieke kabels echt een logische bundel vormen?

---

## 12. Stap 6: controleer OSPF-neighbors

Onderzoek welke routers of multilayer switches OSPF-neighbors vormen.

Gebruik bijvoorbeeld:

```text
show ip ospf neighbor
show ip interface brief
show ip protocols
```

Vul deze tabel in:

| Toestel | Verwachte neighbor | Interface | Neighbor aanwezig? | Opmerking |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |

Beantwoord:

- Welke OSPF-neighbors bestaan?
- Welke OSPF-neighbors verwacht je op basis van de topologie?
- Ontbreekt er een neighbor?
- Is de fysieke/IP-link up?
- Past de OSPF-configuratie bij de link?

Controlepunt:

> Zonder OSPF-neighbor worden routes niet uitgewisseld. Controleer dus eerst neighbors voor je routes analyseert.

---

## 13. Stap 7: analyseer OSPF-areas

Onderzoek welke interfaces in welke OSPF-area zitten.

Gebruik bijvoorbeeld:

```text
show ip ospf interface
show ip protocols
show running-config | section router ospf
```

Vul deze tabel in:

| Toestel | Interface/netwerk | Area | Rol van toestel | Opmerking |
|---|---|---:|---|---|
| ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |

Beantwoord:

- Waar zit area 0?
- Welke toestellen zijn ABR's?
- Welke netwerken horen bij area 10?
- Welke netwerken horen bij area 20?
- Zijn beide kanten van elke OSPF-link in dezelfde area geplaatst?
- Zijn non-backbone areas logisch verbonden met area 0?

Controlepunt:

> Kan je uitleggen langs welke ABR routes van area 10 naar area 20 gaan?

---

## 14. Stap 8: analyseer routingtabellen

Onderzoek welke routes op de routers en multilayer switches aanwezig zijn.

Gebruik bijvoorbeeld:

```text
show ip route
show ip route ospf
```

Vul deze tabel in:

| Toestel | Route naar area 10? | Route naar area 20? | Inter-area routes `O IA`? | Default route? | Opmerking |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |

Beantwoord:

- Welke routes zijn rechtstreeks verbonden?
- Welke routes zijn via OSPF geleerd?
- Zie je `O IA` routes?
- Zijn alle VLAN-subnetten bereikbaar vanuit andere delen van het netwerk?
- Is er een default route?
- Waar komt de default route vandaan?

Controlepunt:

> Interne routes kunnen werken terwijl de default route ontbreekt. Controleer die twee zaken apart.

---

## 15. Stap 9: controleer HSRP

Onderzoek gateway redundancy per VLAN.

Gebruik bijvoorbeeld:

```text
show standby
show standby brief
show ip interface brief
```

Vul deze tabel in:

| VLAN | Virtual gateway | Active toestel | Standby toestel | Clientgateway correct? | Opmerking |
|---:|---|---|---|---|---|
| 10 | ... | ... | ... | ... | ... |
| 20 | ... | ... | ... | ... | ... |
| 30 | ... | ... | ... | ... | ... |
| 50 | ... | ... | ... | ... | ... |
| 99 | ... | ... | ... | ... | ... |

Beantwoord:

- Welke VLAN's hebben HSRP?
- Wat is de virtual IP per VLAN?
- Welk toestel is active?
- Welk toestel is standby?
- Gebruiken clients de virtual IP als default gateway?
- Is de HSRP active rol logisch ten opzichte van STP-rootkeuzes?

Controlepunt:

> HSRP helpt alleen als clients de virtual gateway gebruiken, niet het fysieke IP-adres van een switch.

---

## 16. Stap 10: voer gerichte connectiviteitstesten uit

Voer testen uit vanaf clients, servers en netwerktoestellen.

Vul deze tabel in:

| Test | Bron | Bestemming | Verwacht | Werkelijk | Conclusie |
|---|---|---|---|---|---|
| Gateway VLAN 10 | `PC-OFFICE-A` | gateway | werkt | ... | ... |
| Gateway VLAN 30 | `PC-OFFICE-B` | gateway | werkt | ... | ... |
| Client naar server | ... | `SRV-APP` | werkt | ... | ... |
| Client naar ISP | ... | `ISP-SERVER` | werkt indien default route correct is | ... | ... |
| Managementgateway | `PC-ADMIN` | gateway | werkt redundant | ... | ... |
| OSPF-neighbor | ... | ... | aanwezig | ... | ... |

Beantwoord:

- Welke testen slagen?
- Welke testen falen?
- Is een falende test een Layer 2-, Layer 3-, OSPF-, HSRP- of default-routeprobleem?
- Bewijst een succesvolle ping dat failover werkt?

Controlepunt:

> Noteer niet alleen "werkt" of "werkt niet". Leg uit waarom.

---

## 17. Stap 11: simuleer failover

Voer failovertesten pas uit nadat je de beginsituatie goed gedocumenteerd hebt.

Gebruik kleine, gecontroleerde acties. Zet na elke test de situatie terug.

Mogelijke testen:

| Test | Actie | Wat verwacht je? | Werkelijk resultaat | Verklaring |
|---|---|---|---|---|
| Access uplink failure | Schakel een uplink van een access switch uit | Alternatief pad wordt actief | ... | ... |
| EtherChannel member failure | Schakel een memberlink uit | Port-channel blijft up | ... | ... |
| HSRP active gateway failure | Schakel active SVI of toestel uit | Standby neemt over | ... | ... |
| OSPF routed link failure | Schakel een routed link uit | Alternatieve route indien aanwezig | ... | ... |
| Internet/default route | Test na routingcontrole | Default route blijft beschikbaar | ... | ... |

Gebruik indien nodig:

```text
shutdown
no shutdown
show spanning-tree vlan ...
show etherchannel summary
show standby
show ip route
show ip ospf neighbor
```

Controlepunt:

> Redundantie is pas bewezen als je kan uitleggen welk alternatief pad of toestel de functie overneemt.

---

## 18. Stap 12: risico's en verbeterpunten

Formuleer risico's vanuit enterprise-denken.

Vul deze tabel in:

| Vaststelling | Risico | Impact | Verbeterpunt |
|---|---|---|---|
| ... | ... | ... | ... |
| ... | ... | ... | ... |
| ... | ... | ... | ... |

Denk minstens aan:

- STP-rootkeuzes;
- blocked poorten;
- EtherChannel-status;
- trunkbeperkingen;
- native VLAN;
- OSPF-neighbors;
- OSPF-areas;
- inter-area routes;
- default route;
- HSRP;
- failovertesten.

Voorbeeldformulering:

> Dit werkt technisch, maar het risico is dat ...

of:

> Deze redundantie lijkt aanwezig, maar is niet bewezen omdat ...

---

## 19. Eindconclusie

Schrijf een korte conclusie van 10 tot 15 regels.

Je conclusie moet minstens antwoorden op:

- Is het netwerk enterprise-ready?
- Welke onderdelen zijn goed ontworpen?
- Welke onderdelen zijn risicovol of onduidelijk?
- Welke correcties zijn prioritair?
- Welke failovertesten bewijzen of het ontwerp echt redundant is?

Gebruik deze structuur:

```text
Het netwerk bevat ...

Sterke punten zijn ...

Belangrijkste risico's zijn ...

De eerste verbeteringen zijn ...

Mijn eindconclusie is ...
```

Controlepunt:

> Je conclusie moet meer zijn dan een lijst technische fouten. Leg uit wat de impact is voor het bedrijf.

