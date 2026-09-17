# Workshop 4 - Availability en secure management audit

## 1. Situering

In deze workshop analyseer je een bestaand enterprise-netwerk vanuit twee vragen:

1. Blijft het netwerk voldoende beschikbaar wanneer iets uitvalt?
2. Is beheer veilig, beperkt, traceerbaar en herstelbaar georganiseerd?

Je bouwt niet vanaf nul een nieuw netwerk. Je voert een professionele audit uit. Je zoekt risico's, koppelt die aan bedrijfsimpact en stelt verbeteringen voor.

Belangrijk:

> Een netwerk dat vandaag werkt, is niet automatisch beschikbaar, herstelbaar of veilig beheerbaar.

---

## 2. Scenario

Het bedrijf **BluePeak Services** heeft na een security-oefening zijn zones beter in kaart gebracht. Er zijn aparte zones voor Staff, Finance, IT, Servers, Guests, IoT, DMZ en Management.

De directie maakt zich nu zorgen over beschikbaarheid en beheer.

Recente incidenten:

- een access switch viel uit en een volledige afdeling verloor verbinding;
- een verkeerde configuratiewijziging op een trunk veroorzaakte serverproblemen;
- niemand wist zeker welke configuratie de laatste werkende versie was;
- managementinterfaces waren vanaf te veel clientzones bereikbaar;
- er was geen duidelijk overzicht van wie netwerktoestellen mag beheren;
- bij een storing wist men niet welk onderdeel eerst hersteld moest worden.

De directie vraagt:

> Kunnen jullie beoordelen of ons netwerk enterprise-ready is op vlak van beschikbaarheid en secure management?

---

## 3. Beginsituatie

Je krijgt een Packet Tracer-bestand, een netwerkdiagram of een configuratieset van BluePeak Services.

Voor deze workshop is er ook een configbijlage beschikbaar:

| Bestand of map | Doel |
|---|---|
| `Ch4/workshop/configs/student/` | beginsituatie voor studenten |
| `Ch4/workshop/configs/student/end-devices-student.md` | IP-instellingen voor eindtoestellen |
| `Ch4/workshop/configs/student/quick-tests-student.md` | snelle controletesten voor de beginsituatie |

De studentconfigs zijn bewust niet perfect. Ze vormen het startpunt voor je audit. Beschouw een werkende configuratie dus niet automatisch als een goed enterprise-ontwerp.

Het netwerk bevat typisch:

- meerdere access switches;
- een core- of distributionswitch;
- routing tussen VLAN's;
- een internetedge;
- een DMZ;
- een management VLAN;
- interne servers;
- een IT-zone;
- clients in verschillende zones.

Sommige delen zijn bewust onvolledig of risicovol ontworpen.

Voorbeelden:

- een access switch heeft maar een uplink;
- een gateway is niet redundant;
- management is bereikbaar vanuit staff of guest;
- er is geen duidelijke back-up- of rollbackprocedure;
- failover is niet getest;
- beheerrollen zijn niet uitgewerkt.

Pas niet meteen configuraties aan. Analyseer eerst.

---

## 4. Doelen

Na deze workshop kan je:

1. single points of failure aanduiden in een topologie;
2. de impact van een storing beschrijven per zone of bedrijfsproces;
3. redundantie beoordelen op switching-, gateway-, edge- en managementniveau;
4. een failovertestplan opstellen;
5. managementtoegang analyseren;
6. bepalen wie welk toestel mag beheren;
7. een secure management policy voorstellen;
8. een back-up- en rollbackprocedure ontwerpen;
9. een mini-disaster-recoveryplan maken;
10. prioriteiten formuleren voor verbetering.

---

## 5. Benodigdheden

Je hebt nodig:

- Cisco Packet Tracer of het meegegeven schema;
- dit workshopdocument;
- het cursushoofdstuk **High availability en secure management**;
- eventueel de output van `show`-commando's;
- een tekstverwerker of Markdown-editor.

Voorkennis:

- VLAN's en trunks;
- STP, EtherChannel en gateway redundancy conceptueel;
- routing en default routes;
- securityzones en managementzone;
- basis troubleshooting met `show`-commando's.

---

## 6. Werkwijze

Gebruik deze volgorde:

1. topologie en kritieke componenten verkennen;
2. single points of failure aanduiden;
3. impact van storingen inschatten;
4. bestaande redundantie beoordelen;
5. failovertesten ontwerpen;
6. managementtoegang analyseren;
7. rollen en rechten bepalen;
8. back-up en rollback uitwerken;
9. mini-DR-plan opstellen;
10. verbeterplan en eindconclusie schrijven.

---

## 7. Stap 1: verken de topologie

Maak een overzicht van de aanwezige netwerkonderdelen.

Vul deze tabel in:

| Onderdeel | Toestel(len) | Zone of functie | Kritiek? | Waarom? |
|---|---|---|---|---|
| Accesslaag | ... | clients | ... | ... |
| Core/distribution | ... | centrale switching/routing | ... | ... |
| Internetedge | ... | internet/DMZ | ... | ... |
| Management | ... | beheer | ... | ... |
| Servers | ... | applicaties | ... | ... |

Beantwoord:

- Waar gebeuren switching en routing?
- Waar zit de internetverbinding?
- Welke toestellen zijn nodig voor management?
- Welke toestellen zijn nodig voor servertoegang?
- Welke toestellen zijn nodig voor herstel bij problemen?

Controlepunt:

> Kan je op je schema aanduiden welke onderdelen het grootste bedrijfsrisico vormen bij uitval?

---

## 8. Stap 2: zoek single points of failure

Zoek onderdelen waarvan de uitval een volledige zone, dienst of beheerfunctie raakt.

Vul deze tabel in:

| Single point of failure | Wat valt uit? | Impact | Prioriteit |
|---|---|---|---|
| ... | ... | laag/middel/hoog | ... |
| ... | ... | laag/middel/hoog | ... |

Denk aan:

- access switch met een uplink;
- core switch zonder alternatief;
- enkele default gateway;
- enkele firewall of router;
- enkele internetverbinding;
- management VLAN bereikbaar via maar een pad;
- jump server of beheerpc zonder alternatief;
- configuratieback-ups die alleen lokaal bestaan.

Controlepunt:

> Een single point of failure is vooral belangrijk wanneer de bedrijfsimpact hoog is.

---

## 9. Stap 3: schat storingsimpact in

Kies minstens vijf mogelijke storingen en beschrijf de impact.

Gebruik deze tabel:

| Storing | Getroffen zones | Gebruikersimpact | Technische oorzaak | Ernst |
|---|---|---|---|---|
| Access uplink valt uit | ... | ... | ... | ... |
| Core switch valt uit | ... | ... | ... | ... |
| Default gateway valt uit | ... | ... | ... | ... |
| Internetedge valt uit | ... | ... | ... | ... |
| Managementzone onbereikbaar | ... | ... | ... | ... |

Beantwoord:

- Welke storing heeft de grootste impact?
- Welke storing maakt herstel zelf moeilijker?
- Welke storing raakt vooral comfort en welke raakt kritieke processen?
- Welke impact is aanvaardbaar en welke niet?

Controlepunt:

> Een storing in de managementzone kan extra ernstig zijn omdat ze herstel van andere storingen verhindert.

---

## 10. Stap 4: beoordeel redundantie

Beoordeel welke redundantie aanwezig is en of die ook bewezen is.

| Laag | Redundantie aanwezig? | Bewijs of controle | Opmerking |
|---|---|---|---|
| Access uplinks | ja/nee | ... | ... |
| STP/EtherChannel | ja/nee | ... | ... |
| Default gateway | ja/nee | ... | ... |
| Routing naar edge | ja/nee | ... | ... |
| Internetverbinding | ja/nee | ... | ... |
| Managementtoegang | ja/nee | ... | ... |
| Configuratieherstel | ja/nee | ... | ... |

Mogelijke controles:

```text
show interfaces trunk
show spanning-tree
show etherchannel summary
show standby
show ip route
show ip interface brief
show running-config
```

Controlepunt:

> Schrijf niet alleen "redundant". Noteer welk onderdeel mag falen en welk alternatief dan gebruikt wordt.

---

## 11. Stap 5: ontwerp failovertesten

Maak een failovertestplan. Je hoeft niet elke test echt uit te voeren als dat niet veilig of praktisch is, maar je moet wel exact beschrijven hoe je ze zou uitvoeren.

| Test | Actie | Verwacht resultaat | Controle | Rollback |
|---|---|---|---|---|
| Access uplink failover | ... | ... | ... | ... |
| Gateway failover | ... | ... | ... | ... |
| Internetedge failover | ... | ... | ... | ... |
| Managementbereikbaarheid | ... | ... | ... | ... |

Beantwoord:

- Welke test kan je uitvoeren zonder veel risico?
- Welke test moet in een onderhoudsvenster?
- Welke test bewijst alleen connectiviteit?
- Welke test bewijst echte failover?

Controlepunt:

> Een ping die opnieuw werkt is nuttig, maar je moet ook tonen welk pad of toestel de rol heeft overgenomen.

---

## 12. Stap 6: analyseer managementtoegang

Onderzoek hoe netwerktoestellen beheerd worden.

Vul deze tabel in:

| Toestel | Management-IP of zone | Beheerprotocol | Bereikbaar vanaf | Risico |
|---|---|---|---|---|
| ... | ... | SSH/HTTPS/Telnet/HTTP | ... | ... |
| ... | ... | ... | ... | ... |

Beantwoord:

- Zitten managementinterfaces in een apart management VLAN of zone?
- Is management bereikbaar vanuit staff?
- Is management bereikbaar vanuit guests?
- Is management bereikbaar vanuit DMZ of IoT?
- Wordt Telnet of HTTP gebruikt?
- Is SSH of HTTPS beperkt tot IT of een jump server?
- Is er logging van beheeracties?

Controlepunt:

> Een management VLAN is niet voldoende als iedereen dat VLAN kan bereiken.

---

## 13. Stap 7: bepaal rollen en rechten

Werk een eenvoudige role-based management policy uit.

Gebruik deze tabel:

| Rol | Wie? | Mag wel | Mag niet | Logging nodig? |
|---|---|---|---|---|
| Helpdesk | ... | ... | ... | ja/nee |
| Network operator | ... | ... | ... | ja/nee |
| Network admin | ... | ... | ... | ja/nee |
| Security admin | ... | ... | ... | ja/nee |
| Auditor | ... | ... | ... | ja/nee |

Beantwoord:

- Wie mag switches beheren?
- Wie mag routering wijzigen?
- Wie mag firewallregels aanpassen?
- Wie mag logs bekijken?
- Wie mag alleen status controleren?
- Welke acties moeten altijd gelogd worden?

Controlepunt:

> Niet iedereen die een netwerkprobleem onderzoekt, moet configuraties kunnen wijzigen.

---

## 14. Stap 8: ontwerp een secure management policy

Maak een gewenste managementpolicy.

Gebruik deze tabel:

| Onderdeel | Gewenst beleid | Waarom? |
|---|---|---|
| Managementzone | ... | ... |
| Toegestane bronzones | ... | ... |
| Beheerprotocollen | ... | ... |
| Jump server | ... | ... |
| Authenticatie | ... | ... |
| Autorisatie | ... | ... |
| Logging | ... | ... |
| Fallback bij storing | ... | ... |

Voorbeeldrichtingen:

- alleen IT of jump server mag naar managementinterfaces;
- geen management vanaf Guests, Staff, IoT of DMZ;
- SSH/HTTPS in plaats van Telnet/HTTP;
- centrale authenticatie conceptueel voorzien;
- rollen gebruiken voor beheerrechten;
- beheeracties loggen;
- console of out-of-band pad voorzien voor noodherstel.

Controlepunt:

> Beschrijf beleid. Schrijf geen wachtwoorden of secrets in je oplossing.

---

## 15. Stap 9: back-up- en rollbackprocedure

Ontwerp een eenvoudige procedure voor configuratieback-ups en rollback.

Vul deze tabel in:

| Onderdeel | Voorstel |
|---|---|
| Welke toestellen krijgen back-ups? | ... |
| Wanneer wordt een back-up genomen? | ... |
| Waar wordt de back-up bewaard? | ... |
| Wie mag back-ups bekijken? | ... |
| Hoe wordt een wijziging getest? | ... |
| Wanneer doe je rollback? | ... |
| Hoe documenteer je het resultaat? | ... |

Maak daarna een rollbacktabel:

| Mislukte wijziging | Symptoom | Rollbackactie | Controle na rollback |
|---|---|---|---|
| Trunkwijziging | ... | ... | ... |
| Management-ACL | ... | ... | ... |
| Default route | ... | ... | ... |
| Gateway redundancy | ... | ... | ... |

Controlepunt:

> Een rollbackplan moet bestaan voordat je de wijziging uitvoert.

---

## 16. Stap 10: mini-DR-plan

Maak een mini-disaster-recoveryplan voor BluePeak Services.

Kies minstens vier kritieke functies:

- managementtoegang;
- internetedge;
- core/distribution;
- interne servers;
- DMZ-dienst;
- finance-applicatie;
- configuratieback-ups.

Vul deze tabel in:

| Functie | Kritiek? | Gewenste RTO | Gewenste RPO | Herstelstrategie |
|---|---|---:|---:|---|
| Managementtoegang | ... | ... | ... | ... |
| Internetedge | ... | ... | ... | ... |
| Servers | ... | ... | ... | ... |
| DMZ | ... | ... | ... | ... |

Controlepunt:

> RTO en RPO moeten passen bij de bedrijfsimpact, niet bij wat technisch toevallig makkelijk is.

---

## 17. Verbeterplan

Formuleer minstens acht verbeterpunten.

| Verbeterpunt | Lost welk risico op? | Prioriteit | Hoe test je dit? |
|---|---|---|---|
| ... | ... | hoog/middel/laag | ... |
| ... | ... | hoog/middel/laag | ... |

Sterke verbeterpunten zijn concreet.

Niet:

> Maak management veiliger.

Wel:

> Beperk SSH/HTTPS naar managementinterfaces tot de IT-zone of een jump server en test dat Staff, Guests, IoT en DMZ management niet kunnen bereiken.

---

## 18. Eindconclusie

Schrijf een conclusie van 10 tot 15 regels.

Je conclusie moet minstens antwoorden op:

- Is het netwerk voldoende beschikbaar voor een enterprise-context?
- Welke single points of failure hebben de grootste impact?
- Welke redundantie is aanwezig maar nog niet bewezen?
- Is managementtoegang voldoende beperkt?
- Is rollback mogelijk na een foutieve wijziging?
- Welke drie verbeteringen hebben prioriteit?

Gebruik deze structuur:

```text
Het netwerk bevat ...

De belangrijkste beschikbaarheidsrisico's zijn ...

De belangrijkste managementrisico's zijn ...

De eerste verbeteringen zijn ...

Mijn eindconclusie is ...
```

---

## 19. In te dienen

Lever een kort auditrapport in.

Je rapport bevat minstens:

1. topologieschets met kritieke componenten;
2. tabel met single points of failure;
3. storingsimpactanalyse;
4. redundantiebeoordeling;
5. failovertestplan;
6. managementtoeganganalyse;
7. role-based management policy;
8. secure management policy;
9. back-up- en rollbackprocedure;
10. mini-DR-plan met RTO/RPO;
11. verbeterplan;
12. eindconclusie.

Het rapport hoeft niet lang te zijn. Het moet wel professioneel, toetsbaar en duidelijk gemotiveerd zijn.

---

## 20. Typische valkuilen

| Valkuil | Waarom is dit een probleem? |
|---|---|
| Alleen kijken of alles vandaag werkt | Beschikbaarheid gaat over gedrag bij uitval |
| Redundantie aannemen op basis van een diagram | Failover is pas bewezen met testen |
| Management VLAN gelijkstellen aan veilig beheer | Zonder filtering blijft beheer te breed bereikbaar |
| Geen rollbackplan maken | Een foutieve wijziging duurt langer en wordt riskanter |
| Alleen pings testen | Je ziet niet welk pad of toestel overnam |
| Iedereen adminrechten geven | Geen least privilege voor beheerders |
| Geen logging voorzien | Je weet achteraf niet wie wat deed |
| Back-ups alleen op het toestel zelf bewaren | Bij toesteldefect verlies je ook de back-up |
| RTO/RPO willekeurig kiezen | Hersteldoelen moeten passen bij bedrijfsimpact |
| Trial-and-error wijzigingen voorstellen | Enterprise beheer vraagt procedure en controle |

---

## 21. Eindvraag

Sluit je verslag af met een antwoord op deze vraag:

> Waarom horen high availability en secure management samen in een enterprise-netwerk?
