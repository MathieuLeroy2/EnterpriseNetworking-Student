# Ch4 - High availability en secure management configs

Deze map bevat configuraties voor de Packet Tracer-case **BluePeak Services** bij workshop 4.

De configuraties bouwen verder op dezelfde logische zones als hoofdstuk 3:

- Staff;
- Finance;
- IT;
- Servers;
- Guests;
- IoT;
- DMZ;
- Management;
- Internet.

## Student

De map `student` bevat een beginsituatie die technisch grotendeels werkt, maar bewust auditpunten bevat:

- access switches hebben maar een uplink naar `SW-CORE`;
- er is maar een core/distribution switch;
- er is maar een router/firewall richting internet;
- trunks zijn functioneel maar niet beperkt;
- management is breed bereikbaar vanuit interne VLAN's;
- beheerprotocolkeuze is niet strak afgedwongen;
- logging is minimaal;
- er is geen configuratieback-up- of rollbackprocedure in de config zichtbaar.

## Teacher

De map `teacher` bevat een mogelijke aangescherpte configuratie binnen dezelfde topologie:

- trunks gebruiken een unused native VLAN;
- trunks zijn beperkt tot noodzakelijke VLAN's;
- ongebruikte poorten staan in VLAN 999 en zijn uitgeschakeld;
- managementtoegang wordt beperkt tot de IT-zone;
- beheertransport is beperkt tot SSH;
- logging naar de managementhost is voorzien;
- kritieke toestellen hebben duidelijkere descriptions;
- de core wordt expliciet STP-root voor de relevante VLAN's.

Let op: echte high availability vraagt soms extra hardware of extra links. Binnen deze configset wordt vooral getoond wat je met dezelfde topologie kan verbeteren. Single points of failure zoals een enkele core switch of een enkele internetedge blijven ontwerpbeperkingen die studenten moeten benoemen.

## Wachtwoorden

Er zijn bewust geen wachtwoorden, lokale gebruikers of secrets opgenomen. Voeg die niet toe in het lesmateriaal. Bespreek authenticatie, AAA en SSH conceptueel of via een aparte docentdemo wanneer nodig.

De configs bevatten wel `ip domain-name`, RSA-keygeneratie en `ip ssh version 2` zodat de protocolkeuze zichtbaar is. Een echte SSH-login vereist in Packet Tracer normaal ook lokale gebruikers, wachtwoorden of AAA. Die onderdelen zijn hier bewust weggelaten.

## Toestellen

Voor beide versies zijn configs voorzien voor:

- `R-FW`;
- `SW-CORE`;
- `SW-ACC1`;
- `SW-ACC2`;
- `ISP`;
- eindtoestellen via een aparte Markdown-tabel.
