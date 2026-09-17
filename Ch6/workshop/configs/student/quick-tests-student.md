# Ch6 student - quick tests

Gebruik deze snelle testmatrix.

## 1. Tailnetstatus

```text
tailscale status
tailscale ip -4
```

| Test | Verwacht | Werkelijk |
|---|---|---|
| laptop heeft Tailscale-IP | ja | ... |
| VM1 zichtbaar | ja | ... |
| VM1 tag klopt | ja | ... |
| VM2 zichtbaar | ja | ... |

## 2. HTTP-only ACL

```text
curl -I http://<vm1-tailscale-ip>
nc -vz <vm1-tailscale-ip> 22
nc -vz <vm1-tailscale-ip> 443
```

| Test | Verwacht | Werkelijk |
|---|---|---|
| HTTP TCP/80 | werkt | ... |
| TCP/22 | faalt | ... |
| TCP/443 | faalt tenzij toegestaan | ... |

## 3. Tailscale SSH

```text
tailscale ssh debian@<vm1-name>
ssh debian@<vm1-tailscale-ip>
```

| Test | Verwacht | Werkelijk |
|---|---|---|
| Tailscale SSH | volgens policy | ... |
| klassieke SSH | faalt tenzij TCP/22 open | ... |

## 4. Subnet router

VM2 routeert naar het labsubnet `10.20.0.0/16`.

NetBox is een bestaande HTTPS-dienst in dat subnet. Je gebruikt NetBox alleen als testdoel, niet als VM waarop je inlogt.

```text
tailscale status
curl -kI https://10.20.10.4
nc -vz 10.20.10.4 22
nc -vz 10.20.0.1 22
```

| Test | Verwacht | Werkelijk |
|---|---|---|
| route `10.20.0.0/16` via VM2 beschikbaar | ja | ... |
| HTTPS naar NetBox IP | werkt via VM2 | ... |
| SSH naar NetBox IP | faalt | ... |
| SSH naar DNS-server `10.20.0.1` | faalt | ... |

## 5. Split DNS

```text
nslookup netbox.voltlab.lan
curl -kI https://netbox.voltlab.lan
```

| Test | Verwacht | Werkelijk |
|---|---|---|
| DNS record | `10.20.10.4` | ... |
| HTTPS via hostname | werkt | ... |
