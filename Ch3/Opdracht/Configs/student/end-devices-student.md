# BluePeak Services - student end devices

Configureer de eindtoestellen in Packet Tracer met deze IP-instellingen.

| Toestel | IP-adres | Mask | Gateway | Zone |
|---|---|---|---|---|
| `PC-STAFF` | `10.30.10.101` | `255.255.255.0` | `10.30.10.1` | Staff |
| `PC-FINANCE` | `10.30.20.101` | `255.255.255.0` | `10.30.20.1` | Finance |
| `PC-IT` | `10.30.30.101` | `255.255.255.0` | `10.30.30.1` | IT |
| `PC-GUEST` | `10.30.50.101` | `255.255.255.0` | `10.30.50.1` | Guests |
| `CAM-IOT` | `10.30.60.101` | `255.255.255.0` | `10.30.60.1` | IoT |
| `SRV-APP` | `10.30.40.10` | `255.255.255.0` | `10.30.40.1` | Servers |
| `SRV-FIN` | `10.30.40.20` | `255.255.255.0` | `10.30.40.1` | Servers/Finance app |
| `SRV-WEB-DMZ` | `10.30.70.10` | `255.255.255.0` | `10.30.70.1` | DMZ |
| `SRV-MGMT-JUMP` | `10.30.99.10` | `255.255.255.0` | `10.30.99.1` | Management |

Zet op de servers minstens HTTP aan. HTTPS mag gebruikt worden als Packet Tracer dit in jouw versie goed ondersteunt.

Bewuste fouten in de studentversie:

- `PC-GUEST` kan nog naar interne zones behalve Management.
- `CAM-IOT` heeft geen strikte interne beperking.
- `SRV-WEB-DMZ` staat wel in de DMZ, maar de publieke NAT verwijst naar `SRV-APP`.
- DMZ-verkeer naar interne subnetten is te breed.
- Managementtoegang op de netwerktoestellen is via Telnet en SSH bereikbaar en niet beperkt tot IT.
