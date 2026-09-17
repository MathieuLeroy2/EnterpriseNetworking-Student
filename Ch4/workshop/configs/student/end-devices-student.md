# Ch4 student - end devices

Configureer de eindtoestellen statisch.

| Toestel | VLAN/zone | IP-adres | Subnetmask | Default gateway | Opmerking |
|---|---|---|---|---|---|
| `PC-STAFF` | Staff | `10.30.10.101` | `255.255.255.0` | `10.30.10.1` | gewone medewerker |
| `PC-FINANCE` | Finance | `10.30.20.101` | `255.255.255.0` | `10.30.20.1` | financeclient |
| `PC-IT` | IT | `10.30.30.101` | `255.255.255.0` | `10.30.30.1` | beheerclient |
| `PC-GUEST` | Guests | `10.30.50.101` | `255.255.255.0` | `10.30.50.1` | gastclient |
| `CAM-IOT` | IoT | `10.30.60.101` | `255.255.255.0` | `10.30.60.1` | IoT-simulatie |
| `SRV-APP` | Servers | `10.30.40.10` | `255.255.255.0` | `10.30.40.1` | interne applicatie, HTTP aan |
| `SRV-FIN` | Servers | `10.30.40.20` | `255.255.255.0` | `10.30.40.1` | finance-applicatie, HTTP aan |
| `SRV-WEB-DMZ` | DMZ | `10.30.70.10` | `255.255.255.0` | `10.30.70.1` | publieke webdienst, HTTP aan |
| `SRV-MGMT-JUMP` | Management | `10.30.99.10` | `255.255.255.0` | `10.30.99.1` | conceptuele jump/loghost |

