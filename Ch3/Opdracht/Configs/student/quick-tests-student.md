# Quick tests - studentversie

Doel: snel controleren of de beginsituatie de bedoelde fouten bevat.

| Nr. | Test | Verwacht resultaat |
|---:|---|---|
| 1 | `PC-STAFF` pingt gateway `10.30.10.1` | werkt |
| 2 | `PC-GUEST` pingt gateway `10.30.50.1` | werkt |
| 3 | `PC-GUEST` probeert `SRV-APP` `10.30.40.10` te bereiken | werkt, bewust fout |
| 4 | `PC-GUEST` probeert management `10.30.99.10` te bereiken | faalt |
| 5 | `CAM-IOT` probeert `SRV-APP` `10.30.40.10` te bereiken | werkt, bewust fout |
| 6 | Controleer `DMZ_WEAK` op `R-FW`: `show access-lists DMZ_WEAK` | bevat `permit ip 10.30.70.0 ... 10.30.0.0 ...`, bewust fout |
| 7 | Controleer NAT op `R-FW`: `show run \| include static tcp` | wijst naar `10.30.40.10`, bewust fout |
| 8 | Controleer VTY op `R-FW`: `show run \| section line vty` | `transport input telnet ssh`, bewust fout |

Als deze resultaten kloppen, is de studentversie correct als foutieve beginsituatie.

Opmerking:

> Test 6 is bewust een configcontrole. Server-to-server tests in Packet Tracer kunnen afhangen van services en toestelgedrag. De securityfout is dat de ACL DMZ-verkeer naar interne subnetten toelaat.
