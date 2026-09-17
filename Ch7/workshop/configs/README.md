# Ch7 workshop configs

Deze map bevat de ondersteunende bijlagen voor de workshop rond VPN security en NAT traversal met Tailscale.

## Student

| Bestand | Doel |
|---|---|
| `student/measurement-sheet-student.md` | resultaten van Devbit en eduroam/campusroam naast elkaar zetten |
| `student/quick-tests-student.md` | compacte checklist voor installatie, paden en securitytests |

## Teacher

| Bestand | Doel |
|---|---|
| `teacher/quick-tests-teacher-solution.md` | verwachte resultaten en geldige varianten |

## Bewuste afwezigheid van netwerkconfiguraties

Er zijn geen router-, switch-, NAT- of firewallconfiguraties meegeleverd.

Studenten hebben geen beheerrechten op de campusinfrastructuur. Ze gebruiken twee echte underlaynetwerken en observeren de uitkomst met:

```text
tailscale netcheck
tailscale ping
tailscale status
tcpdump
```

Direct, peer relay en DERP zijn allemaal geldige uitkomsten als ze correct gemeten en verklaard worden.

