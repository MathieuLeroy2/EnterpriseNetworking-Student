# Workshop 9 - Centrale identiteit en SSO met Authentik

## Modeloplossing voor studenten

## 1. Korte samenvatting

In deze workshop werd Authentik als centrale identity provider ingericht.

De labomgeving bevatte:

- PostgreSQL voor persistente Authentik-data;
- Authentik server voor web- en protocolverkeer;
- Authentik worker voor achtergrondtaken;
- een lokale OIDC-client op poort 8089.

De identitystructuur:

| Gebruiker | Groepen | Portal |
|---|---|---|
| Alice | `bp-employees` | allow |
| Bob | `bp-employees`, `bp-it` | allow |
| Eva | `bp-partners` | deny |

De application `BluePeak Portal` werd via een OAuth2/OIDC-provider aan de lokale client
gekoppeld. Een group binding op `bp-employees` bepaalde de toegang.

Kernconclusie:

> Authentik authenticeert de gebruiker centraal. De application binding autoriseert
> alleen medewerkers. De OIDC-client krijgt identity-claims, maar niet het
> gebruikerswachtwoord.

---

## 2. Componenten

| Component | Functie |
|---|---|
| `postgresql` | bewaart users, groups, configuratie, sessies en events |
| `server` | biedt de webinterface en identity/protocolendpoints aan |
| `worker` | voert achtergrondtaken uit |
| `oidc-client` | vertrouwende applicatie die login aan Authentik delegeert |

De Docker socket werd niet gemount.

Waarom?

- hoofdstuk 9 gebruikt geen automatisch beheerde outpost;
- een Docker socket geeft verregaande controle over de Docker-host;
- least privilege geldt ook voor infrastructuurcontainers.

`.env` werd niet ingediend omdat het database-, Authentik- en OIDC-secrets bevat.

---

## 3. Gebruikers- en groepenmodel

Gemaakte groepen:

```text
bp-employees
bp-it
bp-partners
```

Toekenning:

```text
alice.vermeulen -> bp-employees
bob.peeters     -> bp-employees + bp-it
eva.partner     -> bp-partners
```

Bob zit in twee groepen omdat twee eigenschappen tegelijk waar zijn:

- Bob is medewerker;
- Bob werkt voor IT.

`bp-it` werd geen superusergroep.

Reden:

> IT-medewerker zijn betekent niet automatisch dat iemand de identity provider mag
> beheren.

Voor een echt partneraccount ontbreken in het eenvoudige lab nog:

- zakelijke eigenaar;
- contract- of einddatum;
- periodieke access review;
- recoveryprocedure;
- automatische offboarding;
- formele goedkeuring.

---

## 4. Application versus provider

Application:

| Instelling | Waarde |
|---|---|
| Name | `BluePeak Portal` |
| Slug | `bluepeak-portal` |
| Launch URL | `http://localhost:8089/` |
| Group binding | `bp-employees` |

Provider:

| Instelling | Waarde |
|---|---|
| Type | OAuth2/OIDC |
| Client type | confidential |
| Redirect URI | strict: `http://localhost:8089/callback` |
| Scopes | `openid profile email` |
| Signing key | beschikbare Authentik signing key |

Verschil:

> De application beschrijft de zichtbare app en wie ze mag gebruiken. De provider
> beschrijft hoe de OIDC-koppeling technisch werkt.

De client ID identificeert de client en hoeft niet geheim te zijn.

Het client secret authenticeert de confidential client aan het token endpoint en moet
wel geheim blijven.

Een strikte redirect URI voorkomt dat Authentik een authorization code naar een
willekeurige of te breed gematchte bestemming stuurt.

`offline_access` was niet nodig omdat de labclient geen refresh token nodig heeft.

---

## 5. Authorization code flow

De waargenomen flow:

1. Browser opent de OIDC-client.
2. Client maakt `state` en `nonce`.
3. Client redirect de browser naar Authentik.
4. Authentik vraagt credentials en eventueel MFA.
5. Authentik controleert de application binding.
6. Authentik redirect de browser met een korte code naar de callback.
7. De OIDC-client wisselt de code server-to-server in.
8. Authentik levert tokens aan de client.
9. De client vraagt UserInfo op met het access token.
10. De client maakt een lokale applicatiesessie.

Schema:

```text
Browser -> OIDC-client -> Authentik authorization
Browser <- redirect ---- Authentik
Browser -> OIDC-client callback met code
OIDC-client -> Authentik token endpoint
OIDC-client -> Authentik UserInfo endpoint
Browser <- lokale applicatiesessie
```

Authentik vroeg het gebruikerswachtwoord.

De OIDC-client ontving het wachtwoord niet.

De callback was:

```text
http://localhost:8089/callback
```

---

## 6. Positieve test met Alice

Verwacht resultaat:

| Controle | Resultaat |
|---|---|
| credentials geldig | ja |
| centraal geauthenticeerd | ja |
| lid van `bp-employees` | ja |
| application binding geslaagd | ja |
| callback naar client | ja |
| UserInfo opgehaald | ja |
| lokale app-sessie | ja |

De zichtbare claims hangen af van de geselecteerde property mappings.

Typische claims:

```text
sub
preferred_username
name
email
groups
```

De groepenclaim hoort `bp-employees` te bevatten wanneer de standaard mapping groepen
meelevert.

Sterke conclusie:

> Alice werd eerst geauthenticeerd door Authentik en daarna geautoriseerd door de
> application binding. Pas daarna maakte de OIDC-client een eigen sessie.

---

## 7. Single sign-on

Na `Alleen lokaal uitloggen`:

- de labsessie van de OIDC-client was verwijderd;
- de Authentik-sessie bleef bestaan.

Bij een nieuwe login:

1. de client redirect opnieuw naar Authentik;
2. Authentik herkent de bestaande centrale sessie;
3. Authentik hoeft het wachtwoord niet opnieuw te vragen;
4. de client krijgt opnieuw een authorizationresultaat;
5. de client maakt een nieuwe lokale sessie.

Dit bewijst SSO.

Het bewijst geen single logout.

| Handeling | App-sessie | IdP-sessie |
|---|---:|---:|
| alleen lokaal uitloggen | beëindigd | actief |
| uitloggen bij Authentik | mogelijk nog actief | beëindigd |
| volledige single logout | beëindigd | beëindigd |

---

## 8. Negatieve test met Eva

Verwacht resultaat:

| Controle | Resultaat |
|---|---|
| credentials geldig | ja |
| centraal geauthenticeerd | ja |
| lid van `bp-employees` | nee |
| application binding geslaagd | nee |
| portaltoegang | deny |
| lokale aangemelde app-sessie | nee |

Eva kan dus een geldige Authentik-identiteit hebben zonder toegang tot BluePeak Portal.

De toegang wordt geweigerd door de application binding op `bp-employees`.

Sterke conclusie:

> Authentication success kan gevolgd worden door authorization deny.

---

## 9. MFA-test met Bob

Bob registreerde een TOTP-device via zijn gebruikersinstellingen.

Na volledige logout en een nieuwe login:

| Test | Verwacht |
|---|---|
| correct wachtwoord zonder voltooide TOTP | flow niet voltooid |
| foute TOTP | validatie faalt |
| correcte TOTP | authenticatie slaagt |
| portalbinding | slaagt via `bp-employees` |

De factoren:

| Factor | Categorie |
|---|---|
| wachtwoord | iets wat je weet |
| TOTP-authenticator | iets wat je hebt |

`bp-it` veroorzaakt niet automatisch MFA. Groepslidmaatschap en authentication flow
zijn aparte configuraties.

Belangrijke nuance:

> Dat Bob met TOTP aanmeldt, bewijst nog niet dat elke IT-gebruiker verplicht een
> factor registreert.

Een productiepolicy moet bepalen:

- welke groepen MFA moeten hebben;
- wat gebeurt zonder geregistreerde factor;
- welke factorsoorten toegelaten zijn;
- hoe recovery verloopt;
- welke applicaties step-up MFA vragen.

---

## 10. Claimanalyse

Voorbeeld:

| Claim | Nodig? | Gebruik | Risico |
|---|---|---|---|
| `sub` | ja | stabiele technische user key | correlatie tussen diensten bij onzorgvuldig gebruik |
| `preferred_username` | meestal | weergave en herkenning | kan wijzigen |
| `email` | alleen indien functioneel nodig | notificatie of contact | persoonsgegevens onnodig delen |
| `groups` | indien app groepsautorisatie doet | approllen mappen | interne organisatiestructuur lekken |
| `name` | optioneel | gebruiksvriendelijke weergave | extra persoonsgegevens |

Een e-mailadres is niet altijd een goede primaire sleutel:

- het kan wijzigen;
- het kan worden hergebruikt;
- hoofdletters en aliassen geven inconsistentie;
- het is vaak persoonlijk identificeerbare informatie.

`sub` is bedoeld als technische subject identifier binnen de issuercontext.

De labclient toont geen volledige tokens omdat bearer tokens bruikbare credentials
kunnen zijn. Ook een kortlevend token hoort niet in een verslag.

---

## 11. Lifecycle-test

Verwachte observatie:

| Test | Verwacht | Verklaring |
|---|---|---|
| bestaande lokale pagina vernieuwen | kan blijven werken | app vertrouwt op eigen sessie |
| nieuwe login als gedeactiveerde Alice | faalt | IdP laat account niet opnieuw authenticeren |
| na centrale sessie-intrekking | herauthenticatie nodig en faalt | IdP-sessie is beëindigd |

Waarom blijft een bestaande applicatiesessie mogelijk werken?

- de app heeft al een lokale sessie gemaakt;
- niet elke app controleert bij elk request opnieuw de accountstatus bij de IdP;
- logout- of revocationpropagatie is niet automatisch universeel;
- de labsessie leeft maximaal volgens de clientconfig.

Een volledige offboarding omvat daarom:

- account deactiveren;
- IdP-sessies intrekken;
- applicatiesessies beëindigen waar ondersteund;
- tokens en app passwords intrekken;
- groepsrechten verwijderen;
- eigenaarschap en serviceaccounts controleren.

---

## 12. Audit events

Voorbeeld van een ingevulde analyse:

| Event | Actor/target | Resultaat | Relevantie |
|---|---|---|---|
| succesvolle login | Alice | success | bevestigt centrale authentication |
| policy/application deny | Eva / BluePeak Portal | deny | bevestigt autorisatiebeleid |
| authenticator validation failure | Bob | failure | signaal voor fout of aanval |
| user update | `akadmin` / Alice | status gewijzigd | verklaart lifecycle-resultaat |
| provider authorization | Alice of Bob / portal | success | koppelt user aan appgebruik |

Nuttige auditvelden:

- tijd;
- actor;
- target;
- bronadres;
- applicatie of flow;
- resultaat;
- beheerwijziging.

Voor SIEM-forwarding zijn vooral login failures, policy denies, adminwijzigingen,
MFA-wijzigingen, sessieacties en providerfouten interessant.

Credentials horen niet in logs omdat logs breed toegankelijk, langdurig bewaard en
doorgestuurd kunnen worden.

---

## 13. Foutscenario's

### Foute redirect URI

Flowfase:

```text
authorization request / callbackvalidatie
```

Analyse:

- de browser bereikt Authentik;
- Authentik vergelijkt de gevraagde callback met de providerconfig;
- een mismatch wordt geweigerd;
- de code hoort niet naar een niet-geregistreerde callback te gaan.

Herstel:

```text
http://localhost:8089/callback
```

met strict matching.

### Fout client secret

Flowfase:

```text
server-to-server token exchange
```

Analyse:

- login en authorization kunnen slagen;
- de browser keert met een code terug;
- de client kan zich niet correct aan het token endpoint authenticeren;
- de labclient toont een tokenuitwisselingsfout;
- de clientlogs geven de foutfase aan.

Herstel:

- juiste secret lokaal in `.env`;
- `docker compose up -d`;
- secret roteren als het gelekt is.

### Ontbrekende group binding

Analyse:

- een Authentik-application zonder binding is standaard niet beperkt tot
  `bp-employees`;
- toegang kan onverwacht breder worden;
- Eva moet opnieuw als negatieve test gebruikt worden.

Herstel:

```text
BluePeak Portal -> Policy / Group / User Bindings -> bp-employees
```

---

## 14. Identity- en accessmodel

### Gebruikers en groepen

| Type | Groep | Eigenaar | Review | Offboarding |
|---|---|---|---|---|
| medewerker | `bp-employees` | HR + leidinggevende | per kwartaal | deactiveren en sessies intrekken |
| IT | `bp-it` plus `bp-employees` | IT-manager | maandelijks | privileged access direct verwijderen |
| partner | `bp-partners` | interne sponsor | maandelijks en op einddatum | automatisch vervallen |

### Applicatiematrix

| Applicatie | Toegang | MFA | Minimale claims |
|---|---|---|---|
| intranet | `bp-employees` | volgens basispolicy | `sub`, naam |
| helpdesk | `bp-employees` | extern verkeer | `sub`, naam, e-mail |
| monitoring | `bp-it` | verplicht | `sub`, relevante groepen |
| adminportaal | aparte admingroep | phishingresistente MFA | `sub`, adminrol |
| partnerportaal | `bp-partners` | verplicht | `sub`, partnerorganisatie |

### MFA-policy

Voorbeeld:

- MFA is verplicht voor IT, beheerders, finance en partners.
- Voor gevoelige beheeracties is step-up authentication vereist.
- TOTP is minimum voor het lab; phishingresistente factoren hebben voorkeur voor
  beheerders.
- Enrollment gebeurt gecontroleerd na identiteitsverificatie.
- Recovery vereist een tweede gecontroleerde procedure.
- Helpdesk mag MFA niet verwijderen zonder logging en goedkeuring.
- Enrollment, removal, failures en recovery worden gemonitord.

---

## 15. Productieverbeteringen

De workshop is geen productieontwerp.

Voor productie zijn onder meer nodig:

- geldige DNS-naam;
- HTTPS met betrouwbaar certificaat;
- databaseback-up en restoretest;
- hoge beschikbaarheid volgens risico;
- beveiligde secretopslag;
- beperkte admininterface;
- aparte beheerdersaccounts;
- sessie- en tokenbeleid;
- signing-keybeheer en rotatie;
- monitoring en SIEM-forwarding;
- geteste offboarding;
- recoveryprocedure;
- change management;
- periodieke access reviews.

De identity provider is een kritieke afhankelijkheid.

Een uitval of foutieve policy kan meerdere applicaties tegelijk raken.

---

## 16. Eindantwoord

Centrale authenticatie zorgt ervoor dat applicaties geen afzonderlijke wachtwoorden
hoeven te beheren.

Groepsbindings zorgen dat een geldige identiteit niet automatisch elke applicatie mag
openen.

MFA beperkt het risico van alleen een gestolen wachtwoord.

Lifecyclebeheer trekt toegang in wanneer een gebruiker van functie verandert of
vertrekt.

Auditlogs maken login-, deny- en beheeracties onderzoekbaar.

Het nieuwe risico is concentratie:

- een gecompromitteerde IdP-sessie kan meerdere applicaties raken;
- uitval van de IdP kan breed toegang blokkeren;
- een foutieve centrale policy heeft een grote impact.

Eindzin:

> Centrale identity verbetert security en beheerbaarheid wanneer authenticatie,
> autorisatie, MFA, sessies, lifecycle en audit als één samenhangend systeem worden
> ontworpen en negatief én positief worden getest.
