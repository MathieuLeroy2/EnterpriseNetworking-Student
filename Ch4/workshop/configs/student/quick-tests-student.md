# Ch4 student - quick tests

Gebruik deze testen om de beginsituatie te verkennen. Sommige resultaten tonen bewust auditpunten.

| Test | Bron | Doel | Verwacht in studentconfig | Auditinterpretatie |
|---|---|---|---|---|
| Staff naar app | `PC-STAFF` | `10.30.40.10` | werkt | basisconnectiviteit |
| Finance naar app | `PC-FINANCE` | `10.30.40.20` | werkt | basisconnectiviteit |
| IT naar management | `PC-IT` | `10.30.99.2` | werkt | IT kan beheren |
| Staff naar management | `PC-STAFF` | `10.30.99.2` | werkt | auditpunt: management te breed bereikbaar |
| Guest naar management | `PC-GUEST` | `10.30.99.2` | werkt | auditpunt: management te breed bereikbaar |
| Internettest | `PC-STAFF` | `198.51.100.1` | werkt | NAT en default route werken |
| Publieke webdienst | `ISP` | `203.0.113.1` HTTP | werkt indien HTTP-test mogelijk is | NAT naar DMZ |
| Trunkcontrole | `SW-CORE` | `show interfaces trunk` | trunks breed | auditpunt: geen trunk pruning |
| STP-controle | `SW-CORE` | `show spanning-tree` | rootkeuze niet bewust | auditpunt: geen expliciete root |

