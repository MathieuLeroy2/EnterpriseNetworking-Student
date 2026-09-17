# Ch3 - Security architecture configs

Deze map bevat de configuraties voor de Packet Tracer-case **BluePeak Services**.

## Student

De map `student` bevat de beginsituatie voor de opgave. Deze configuratie werkt technisch grotendeels, maar bevat bewust securityproblemen:

- guest is onvoldoende geisoleerd;
- DMZ mag te breed naar intern;
- IoT heeft geen strikte interne beperking;
- publieke NAT verwijst naar de interne applicatieserver;
- management is via Telnet en SSH bereikbaar en niet beperkt tot IT;
- trunks zijn functioneel, maar niet beperkt.

## Teacher

De map `teacher` bevat een mogelijke oplossing met aangescherpt securitybeleid:

- guest wordt geblokkeerd naar interne subnetten;
- staff en finance krijgen alleen specifieke applicatietoegang;
- IoT krijgt beperkte toegang;
- DMZ mag niet vrij naar interne zones;
- publieke NAT verwijst naar de DMZ-webserver;
- management is SSH-only en beperkt tot de IT-zone;
- trunks zijn beperkt en gebruiken VLAN 999 als unused native VLAN.

## Toestellen

Voor beide versies zijn configs voorzien voor:

- `R-FW`;
- `SW-CORE`;
- `SW-ACC1`;
- `SW-ACC2`;
- `ISP`;
- eindtoestellen via een aparte Markdown-tabel.
