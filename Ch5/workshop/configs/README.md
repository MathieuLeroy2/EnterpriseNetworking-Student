# Ch5 - Debian HTTP via Tailscale configs

Deze map bevat bijlagen voor workshop 5.

De workshop gebruikt per student een Debian VM.

Elke student maakt en gebruikt een **eigen Tailscale-account**.

De student meldt minstens twee devices aan in de persoonlijke tailnet:

- Debian VM;
- laptop of testclient.

De VM heeft:

- een lokale webserver;
- een Proxmox-firewall die inkomende HTTP naar het gewone VM-IP blokkeert;
- internettoegang om Tailscale te installeren;
- na configuratie een Tailscale-interface `tailscale0`.

De centrale oefening:

> Bereik HTTP via het Tailscale-IP van de VM, terwijl HTTP direct naar het VM-IP geblokkeerd blijft.

## Student

De map `student` bevat:

- account-, VM- en IP-plan;
- Tailscale-installatie- en testcommands;
- quick tests voor Devbit, eduroam, Tailscale en exit node.

Studenten vullen zelf hun VM-IP, Tailscale-IP en MagicDNS-naam aan.

Tailscale-IP's worden automatisch toegekend.

## Teacher

De map `teacher` bevat:

- voorbereiding van de Debian VM en Proxmox-firewall;
- labplan;
- verplichte VM-challenges;
- verwachte testresultaten.

## Secrets

Neem nooit secrets op in deze bestanden of in studentindieningen:

- wachtwoorden;
- auth keys;
- loginlinks;
- recovery codes;
- private keys;
- persoonlijke tokens.
