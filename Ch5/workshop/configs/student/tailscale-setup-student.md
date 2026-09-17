# Ch5 student - Debian en Tailscale commands

Gebruik deze commands binnen de afspraken van de docent.

Neem geen loginlinks, auth keys of tokens op in je verslag.

## 1. Eigen Tailscale-account

Maak een eigen Tailscale-account aan of gebruik je bestaande account.

Meld zowel je Debian VM als je laptop/testclient aan met datzelfde account.

Controle:

```text
tailscale status
```

Op beide devices moet je het andere device als peer zien.

## 2. VM inventariseren

```text
hostname
ip -br addr
ip route
```

## 3. Webserver lokaal testen

```text
curl -I http://127.0.0.1
curl http://127.0.0.1
```

Als de webserver niet werkt:

```text
systemctl status nginx
systemctl status apache2
```

Gebruik alleen de service die effectief geinstalleerd is.

## 4. Directe HTTP-test vanaf Devbit

Vanaf een client op Devbit:

```text
curl -I http://<VM-IP>
```

Verwacht:

- de test faalt door de Proxmox-firewall.

## 5. Directe HTTP-test vanaf eduroam

Vanaf een client op eduroam:

```text
curl -I http://<VM-IP>
```

Verwacht:

- de test faalt;
- eduroam is een apart netwerk.

## 6. Tailscale installeren op de VM

Voor Debian kan dit bijvoorbeeld:

```text
curl -fsSL https://tailscale.com/install.sh | sh
```

Daarna:

```text
sudo tailscale up
```

Volg de loginflow met je eigen Tailscale-account.

Plak de loginlink niet in je verslag.

## 7. Tailscale controleren op de VM

```text
tailscale status
tailscale ip -4
ip -br addr show tailscale0
```

## 8. Tailscale installeren op je testclient

Installeer Tailscale ook op je laptop of andere testclient.

Meld aan met hetzelfde account als op de VM.

Controleer:

```text
tailscale status
tailscale ip -4
```

## 9. Peer-connectiviteit testen

Vanaf je testclient:

```text
tailscale ping <vm-name>
ping <tailscale-ip-van-je-VM>
```

## 10. HTTP via Tailscale testen

Vanaf je testclient, bij voorkeur verbonden met eduroam:

```text
curl -I http://<tailscale-ip-van-je-VM>
curl -I http://<magicdns-naam-van-je-VM>
```

## 11. Challenge: exit node via Devbit

Op de VM:

```text
sudo tailscale up --advertise-exit-node
```

Keur daarna de exit node goed in je eigen Tailscale admin console.

Op je testclient selecteer je de VM als exit node.

Test:

```text
curl https://ifconfig.me
```

## 12. Opruimen

Na de workshop:

```text
tailscale down
```

Verwijder eventueel de VM uit je Tailscale admin console als je ze niet meer gebruikt.
