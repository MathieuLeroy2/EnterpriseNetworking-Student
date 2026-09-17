# Hoofdstuk 9 - Authentik en identity providers

## 1. Inleiding

In hoofdstuk 8 werden interne webapplicaties via een reverse proxy gepubliceerd.

Daarbij kon de reverse proxy bepalen:

- welke hostname bij welke applicatie hoort;
- naar welke backend het verkeer gaat;
- welke poorten publiek bereikbaar zijn;
- welke headers aan een antwoord worden toegevoegd.

De reverse proxy wist echter nog niet **wie** de gebruiker was.

Dat leidt tot nieuwe vragen:

- Moet elke applicatie eigen gebruikers en wachtwoorden bijhouden?
- Hoe trek je toegang van een vertrekkende medewerker centraal in?
- Hoe geef je IT meer rechten dan een gewone medewerker?
- Hoe verplicht je MFA voor gevoelige toegang?
- Hoe bewijs je achteraf wie zich heeft aangemeld?

Een identity provider helpt om die vragen centraal te beantwoorden.

In dit hoofdstuk gebruiken we **Authentik** als voorbeeld van een identity provider en
SSO-platform. De concepten zijn ook van toepassing op andere oplossingen, zoals
Microsoft Entra ID, Keycloak, Okta, Ping Identity of een bedrijfsdirectory met
federatiediensten.

Kernidee:

> Een identity provider centraliseert identiteit en authenticatie. De applicatie blijft
> verantwoordelijk voor wat een aangemelde gebruiker binnen de applicatie mag doen.

De rode draad door dit hoofdstuk is daarom:

```text
Wie is de gebruiker?
Hoe bewijst de gebruiker dat?
Welke applicatie vertrouwt dat bewijs?
Welke toegang volgt daaruit?
Hoe testen en auditen we dat achteraf?
```

In de workshop bouwen studenten deze keten stap voor stap op. Ze maken niet alleen een
login werkend, maar testen ook SSO, MFA, groepsgebaseerde toegang, negatieve toegang,
lifecycle en auditlogs.

---

## 2. Leerdoelen

Na dit hoofdstuk kan je:

1. authenticatie en autorisatie correct van elkaar onderscheiden;
2. lokale accounts vergelijken met centrale identiteit;
3. de rol van een identity provider uitleggen;
4. uitleggen hoe single sign-on werkt en welke sessies daarbij bestaan;
5. gebruikers, groepen, rollen en policies correct plaatsen;
6. het doel van MFA uitleggen;
7. LDAP, SAML, OAuth 2.0 en OpenID Connect op hoofdlijnen vergelijken;
8. de stappen van een OIDC authorization code flow uitleggen;
9. een Authentik application en provider van elkaar onderscheiden;
10. een OIDC-client registreren met een strikte redirect URI;
11. groepsgebaseerde toegang via een application binding configureren;
12. claims in identity-informatie onderzoeken;
13. positieve en negatieve toegangstesten uitvoeren;
14. een gebruiker deactiveren en de impact op bestaande sessies beoordelen;
15. authenticatie- en beheergebeurtenissen in auditlogs terugvinden;
16. risico's van SSO, MFA en centrale identiteit benoemen;
17. een identity- en accessmodel voor een organisatie documenteren.

---

## 3. Lokale accounts versus centrale identiteit

Bij lokale authenticatie houdt elke applicatie haar eigen accounts bij.

```text
gebruiker -> account in intranet
gebruiker -> account in helpdesk
gebruiker -> account in monitoring
gebruiker -> account in documentatieplatform
```

Elke applicatie beslist dan zelf over verschillende onderdelen van het
identiteitsbeheer. Daardoor raakt dat beheer verspreid over verschillende systemen.

| Keuze per applicatie | Waarom dat belangrijk is |
|---|---|
| gebruikers aanmaken | een nieuwe medewerker moet op meerdere plaatsen correct aangemaakt worden |
| wachtwoorden opslaan | elke applicatie wordt zelf verantwoordelijk voor veilige opslag en hashing |
| wachtwoorden resetten | supportprocessen verschillen en kunnen onveilig of inconsistent worden |
| groepen of rechten bepalen | dezelfde functie kan in elke applicatie andere rechten krijgen |
| sessieduur instellen | een gebruiker kan in de ene app snel uitgelogd zijn en in een andere lang actief blijven |
| loginpogingen loggen | onderzoek achteraf vraagt logs uit verschillende systemen |

Dit lijkt eenvoudig wanneer er maar één applicatie en enkele gebruikers zijn.

Op grotere schaal ontstaan verschillende problemen. De kern is niet alleen het extra
werk, maar vooral dat toegang moeilijk aantoonbaar correct blijft.

| Probleem | Gevolg in de praktijk |
|---|---|
| meerdere accounts per persoon | het is moeilijk te bewijzen welke accounts bij dezelfde mens horen |
| verschillend wachtwoordbeleid | de zwakste applicatie kan het hele toegangsmodel ondermijnen |
| wachtwoordhergebruik | een lek in één applicatie kan toegang tot andere applicaties geven |
| vertrek per applicatie verwerken | een vergeten account blijft mogelijk bruikbaar na offboarding |
| groepswijzigingen niet overal tegelijk | iemand kan oude rechten behouden of nieuwe rechten missen |
| verspreide auditinformatie | incidentonderzoek duurt langer en mist context |
| MFA per applicatie | sommige applicaties blijven zonder tweede factor bereikbaar |
| slapende accounts | ongebruikte accounts vergroten het aanvalsoppervlak |

Bij centrale identiteit delegeren applicaties de login aan een identity provider.

```text
                    +-------------------+
gebruiker --------> | Identity provider |
                    +-------------------+
                       |       |       |
                       v       v       v
                    intranet helpdesk monitoring
```

De applicaties vertrouwen op identity-informatie van de identity provider.

Voordelen:

| Voordeel | Wat betekent dit concreet? |
|---|---|
| centrale accountlevenscyclus | joiners, movers en leavers worden op één centrale plaats beheerd |
| centraal wachtwoord- en MFA-beleid | wachtwoordregels en tweede factoren hangen niet af van elke losse applicatie |
| single sign-on | de gebruiker meldt zich centraal aan en hoeft niet overal opnieuw credentials in te voeren |
| consistente groepen en claims | applicaties kunnen dezelfde identity-informatie gebruiken voor toegang en personalisatie |
| centrale authenticatielogs | loginpogingen, fouten en policybeslissingen zijn makkelijker terug te vinden |
| sneller blokkeren van een account | een gedeactiveerde identiteit kan geen nieuwe centrale logins meer starten |

Nieuwe afhankelijkheid:

> Als de identity provider niet beschikbaar of verkeerd geconfigureerd is, kunnen veel
> applicaties tegelijk onbereikbaar worden.

Centrale identiteit vermindert dus beheerproblemen, maar wordt zelf kritieke
infrastructuur.

### Praktisch voorbeeld

Stel dat Bob van support naar IT verhuist.

Bij lokale accounts moet iemand in elke applicatie apart controleren:

- bestaat Bob daar al?
- welke rechten had Bob vroeger?
- welke rechten moet Bob nu krijgen?
- zijn oude supportrechten verwijderd?
- klopt de auditinformatie achteraf nog?

Bij centrale identiteit wijzig je vooral het centrale identitymodel:

```text
Bob uit groep bp-support
Bob in groep bp-it
gekoppelde applicaties lezen of ontvangen die nieuwe groepscontext
```

Dat maakt de wijziging consistenter, maar alleen als applicaties hun toegang effectief
op die centrale identiteit baseren.

Belangrijke ontwerpvraag:

> Waar ligt de bron van waarheid voor identiteit, groepen en toegangsbeslissingen?

---

## 4. Authenticatie en autorisatie

Deze begrippen mogen niet door elkaar gebruikt worden.

### Authenticatie

Authenticatie beantwoordt:

> Wie ben je?

Voorbeelden:

- gebruikersnaam en wachtwoord;
- een passkey;
- een certificaat;
- een TOTP-code als extra factor;
- een reeds bestaande SSO-sessie.

Authenticatie gaat dus over het vertrouwen in een identiteitsclaim. Als Alice zegt
"ik ben Alice", dan moet het systeem controleren of dat geloofwaardig is.

In een klassieke applicatie doet de applicatie die controle zelf. In een SSO-omgeving
laat de applicatie die controle uitvoeren door de identity provider.

### Autorisatie

Autorisatie beantwoordt:

> Wat mag je doen?

Voorbeelden:

- een medewerker mag het intranet openen;
- een IT-medewerker mag het monitoringdashboard openen;
- een finance-medewerker mag facturen bekijken;
- alleen een applicatiebeheerder mag gebruikers in die applicatie beheren.

Autorisatie gebeurt na, of minstens op basis van, authenticatie. Eerst moet het systeem
weten welke identiteit het voor zich heeft. Daarna kan het bepalen welke toegang bij
die identiteit hoort.

Voorbeeld:

```text
Alice logt correct in.
Alice zit in groep bp-employees.
De applicatie laat Alice het medewerkersportaal openen.
De applicatie laat Alice het monitoringdashboard niet openen.
```

### Samenhang

```text
identiteit claimen
      |
      v
authenticatie: klopt die identiteit?
      |
      v
autorisatie: welke toegang hoort erbij?
```

Een geldige login betekent niet automatisch dat de gebruiker elke applicatie mag
openen.

Kernzin:

> Authenticated is niet hetzelfde als authorized.

Veel voorkomende denkfout:

> "De gebruiker kan inloggen bij Authentik, dus de gebruiker mag de applicatie openen."

Dat klopt alleen als de access policy of application binding dat ook toestaat.
In de workshop testen studenten daarom zowel een toegelaten gebruiker als een geweigerde
gebruiker.

---

## 5. Wat is een identity provider?

Een **identity provider**, afgekort **IdP**, authenticeert gebruikers en levert
betrouwbare identity-informatie aan applicaties.

Afhankelijk van het protocol krijgt de applicatie bijvoorbeeld:

- een SAML assertion;
- een ID token;
- claims via een UserInfo-endpoint;
- directoryattributen via LDAP.

De applicatie die op de IdP vertrouwt, wordt onder meer genoemd:

- service provider bij SAML;
- relying party of client bij OpenID Connect;
- relying application in algemene architectuur.

Conceptueel:

```text
+--------+     1. open app      +-------------+
| Browser| -------------------> | Applicatie  |
+--------+                      +-------------+
    |                                  |
    | 2. redirect naar IdP             |
    v                                  |
+-------------------+                  |
| Identity provider |                  |
+-------------------+                  |
    |                                  |
    | 3. login en resultaat             |
    +--------------------------------->+
```

De applicatie ontvangt normaal niet het wachtwoord van de gebruiker. Ze ontvangt een
protocolresultaat dat ze moet controleren.

### Wat centraliseert een IdP?

Een identity provider kan meerdere verantwoordelijkheden samenbrengen:

| Onderdeel | Wat betekent dit praktisch? |
|---|---|
| Login | gebruikers melden zich op een centrale plaats aan |
| MFA | tweede factoren worden centraal geregistreerd en afgedwongen |
| Groepen | applicaties kunnen dezelfde groepsinformatie gebruiken |
| Policies | toegang kan afhangen van groep, gebruiker, flow of context |
| Sessies | de IdP houdt een centrale aanmeldsessie bij |
| Audit | login- en beheeracties verschijnen op een centrale plaats |

Een IdP vervangt niet alle applicatielogica. Een ticketapplicatie moet bijvoorbeeld
nog altijd zelf weten wat een ticket, wachtrij of SLA is. De IdP levert vooral de
betrouwbare identiteit en context waarmee de applicatie beslissingen kan nemen.

### Vertrouwensrelatie

Een gekoppelde applicatie vertrouwt de IdP alleen als de technische configuratie klopt.

Bij OIDC betekent dat onder meer:

- de applicatie verwacht de juiste issuer;
- de client ID komt overeen;
- de redirect URI is vooraf geregistreerd;
- tokens zijn ondertekend door een vertrouwde sleutel;
- scopes en claims zijn bewust gekozen.

SSO is dus geen magie. Het is een expliciete vertrouwensrelatie tussen applicatie en
identity provider.

---

## 6. Single sign-on

**Single sign-on**, afgekort **SSO**, betekent dat een gebruiker zich eenmaal bij de
identity provider aanmeldt en daarna meerdere gekoppelde applicaties kan openen zonder
telkens opnieuw credentials in te voeren.

Voorbeeld:

1. Noor opent het intranet.
2. Het intranet stuurt Noor naar Authentik.
3. Noor meldt zich aan.
4. Authentik stuurt Noor terug naar het intranet.
5. Noor opent daarna de helpdesk.
6. De helpdesk stuurt Noor ook naar Authentik.
7. Authentik herkent de bestaande IdP-sessie.
8. Noor hoeft niet opnieuw haar wachtwoord in te voeren.

### Twee soorten sessies

Bij SSO bestaan meestal minstens twee sessies:

| Sessie | Beheerd door | Doel |
|---|---|---|
| IdP-sessie | identity provider | onthouden dat de gebruiker centraal aangemeld is |
| applicatiesessie | applicatie | onthouden dat de gebruiker in die app aangemeld is |

Daarom betekent uitloggen uit één applicatie niet altijd dat de centrale IdP-sessie of
andere applicatiesessies beëindigd zijn.

Concreet:

```text
Noor logt in bij Authentik.
Noor krijgt een IdP-sessie.
Noor opent het intranet.
Het intranet maakt een eigen applicatiesessie.
Noor sluit het intranet.
De Authentik-sessie kan nog bestaan.
```

Daarom moet je bij testen goed benoemen welke sessie je onderzoekt.

| Actie | Mogelijk effect |
|---|---|
| uitloggen uit de applicatie | alleen de applicatiesessie verdwijnt |
| uitloggen uit de IdP | centrale sessie verdwijnt, maar apps kunnen eigen sessies houden |
| account deactiveren | nieuwe logins falen, bestaande sessies vragen extra controle |
| sessies intrekken | gebruiker moet opnieuw authenticeren |

### Voordelen

Deze voordelen zijn vooral operationeel:

| Voordeel | Waarom nuttig? |
|---|---|
| minder wachtwoordprompts | gebruikers hoeven minder vaak credentials in te geven en lopen minder kans op wachtwoordmoeheid |
| minder lokale wachtwoorden | applicaties hoeven zelf minder secrets te bewaren en te beschermen |
| centrale beveiligingspolicy | MFA, sessieduur en toegangsvoorwaarden kunnen consistenter toegepast worden |
| snellere toegang | goedgekeurde gebruikers verliezen minder tijd tussen gekoppelde applicaties |

### Risico

Een gestolen actieve SSO-sessie kan toegang geven tot meerdere applicaties.

Daarom zijn meerdere beveiligingsmaatregelen nodig. Elke maatregel hieronder beperkt
een ander stuk van het risico:

| Maatregel | Wat beperkt dit? |
|---|---|
| korte en passende sessieduur | verkleint de periode waarin een gestolen sessie bruikbaar blijft |
| veilige cookies | voorkomt dat browsercookies te makkelijk uitlekken of via scripts misbruikt worden |
| TLS | beschermt credentials, cookies en tokens tijdens transport |
| MFA | maakt een gestolen wachtwoord op zichzelf minder bruikbaar |
| sessies kunnen intrekken | laat beheerders actief ingrijpen bij verlies, vertrek of incidenten |
| logging | maakt verdachte login- of toegangspatronen zichtbaar |
| bescherming van beheerdersaccounts | verlaagt de impact als een hoogbevoegd account aangevallen wordt |

### Wanneer is SSO geslaagd?

SSO is pas correct ingericht als drie dingen samen kloppen:

1. De gebruiker kan zich centraal aanmelden.
2. De juiste applicaties accepteren de centrale login.
3. Onbevoegde gebruikers worden geweigerd.

Alleen tonen dat Alice kan inloggen is dus onvoldoende. Je moet ook tonen dat Eva, die
niet in de juiste groep zit, geen toegang krijgt.

---

## 7. Gebruikers, groepen, rollen en policies

### Gebruiker

Een gebruiker stelt een identiteit voor.

Voorbeelden:

- `alice.vermeulen`;
- `bob.peeters`;
- een externe partner;
- een tijdelijk account.

Een account is niet noodzakelijk voor altijd actief. Een account heeft een
levenscyclus.

Een gebruiker is meer dan een gebruikersnaam. In een identity provider hangen aan een
gebruiker meestal attributen:

- naam;
- e-mailadres;
- status actief/inactief;
- groepen;
- eventueel MFA-devices;
- sessies;
- auditgeschiedenis.

In ontwerpen is het belangrijk om te bepalen of een account een mens, partner,
beheerder of technische integratie voorstelt.

### Groep

Een groep verzamelt gebruikers met een gemeenschappelijk kenmerk.

Voorbeelden:

- `bp-employees`;
- `bp-it`;
- `bp-finance`;
- `bp-partners`.

Een gebruiker kan lid zijn van meerdere groepen.

Groepen zijn handig omdat je toegang niet persoon per persoon hoeft te beheren.

Voorbeeld:

```text
application BluePeak Portal -> allow groep bp-employees
Alice in bp-employees -> toegang
Eva alleen in bp-partners -> geen toegang
```

Goede groepsnamen beschrijven waarom de groep bestaat. Een naam zoals `bp-it` of
`bp-finance` is nuttiger dan `groep1`.

### Rol

Een rol verzamelt rechten.

Algemeen RBAC-model:

```text
gebruiker -> groep -> rol -> permissies
```

Belangrijke Authentik-nuance:

> Rollen in Authentik bundelen vooral beheerspermissies op objecten binnen Authentik.
> Toegang tot een gekoppelde applicatie regel je meestal met application bindings op
> gebruikers, groepen of policies.

Binnen de doelapplicatie kunnen eigen rollen bestaan, zoals `ticket-agent` of
`report-viewer`. Die applicatierollen zijn niet automatisch hetzelfde als
Authentik-beheersrollen.

Praktisch onderscheid:

| Type | Voorbeeld | Waar wordt dit gebruikt? |
|---|---|---|
| IdP-groep | `bp-it` | toegang tot applicaties en claims |
| Authentik-rol | beheerrechten binnen Authentik | administratie van Authentik zelf |
| applicatierol | `ticket-agent` | rechten binnen de doelapplicatie |

Die drie kunnen met elkaar samenhangen, maar vallen niet automatisch samen.

### Policy en binding

Een policy beschrijft een voorwaarde.

Een binding koppelt een gebruiker, groep of policy aan een object, bijvoorbeeld een
applicatie.

Voorbeeld:

```text
application: BluePeak Portal
binding: groep bp-employees
resultaat: alleen leden van bp-employees krijgen toegang
```

Least privilege:

> Geef toegang op basis van een zakelijke behoefte, niet omdat een account toevallig
> bestaat.

Een binding is de plaats waar een ontwerpbeslissing technisch wordt toegepast.

Voorbeeldbeslissing:

> Alleen medewerkers mogen het BluePeak Portal openen.

Technische vertaling:

```text
application: BluePeak Portal
binding: groep bp-employees
```

Controleer altijd wat de standaardtoestand is. Een applicatie zonder correcte binding
kan te breed of net niet bereikbaar zijn, afhankelijk van de configuratie.

---

## 8. Identity lifecycle

Identiteitsbeheer gaat verder dan accounts aanmaken.

Een eenvoudige lifecycle:

```text
joiner -> mover -> leaver
```

Lifecyclebeheer voorkomt dat identity-informatie achterloopt op de werkelijkheid.
Toegang moet meebewegen met de functie en status van een persoon.

### Joiner

Een nieuwe medewerker start.

De vereiste taken en hun doel:

| Taak | Waarom? |
|---|---|
| identiteit registreren | de organisatie moet weten welke digitale identiteit bij welke persoon hoort |
| juiste groepen toekennen | toegang volgt uit functie, afdeling of contractuele rol |
| onboardingtoegang beperken | tijdelijke brede toegang mag niet permanent blijven bestaan |
| MFA registreren | de eerste login is een goed moment om tweede factor verplicht te maken |
| eigenaar en einddatum bepalen | tijdelijke of externe accounts moeten later opgevolgd kunnen worden |

Voorbeeld:

```text
Alice start als medewerker.
Alice krijgt account alice.vermeulen.
Alice wordt lid van bp-employees.
Alice registreert TOTP.
Alice krijgt geen bp-it, want dat hoort niet bij haar functie.
```

### Mover

Een medewerker verandert van functie.

De vereiste taken en hun doel:

| Taak | Waarom? |
|---|---|
| oude groepsrechten verwijderen | voorkomt rechtenstapeling doorheen de loopbaan |
| nieuwe rechten toevoegen | zorgt dat de medewerker het nieuwe werk kan uitvoeren |
| conflicterende rechten controleren | voorkomt combinaties zoals aanvragen en goedkeuren door dezelfde persoon |
| uitzonderingen documenteren | maakt tijdelijke afwijkingen controleerbaar bij audit of review |

De mover-fase is vaak riskanter dan onboarding. Nieuwe rechten worden toegevoegd, maar
oude rechten blijven soms hangen.

Voorbeeld:

```text
Bob verhuist van support naar IT.
Bob krijgt bp-it.
Bob verliest bp-support als die toegang niet meer nodig is.
```

### Leaver

Een medewerker of partner vertrekt.

De vereiste taken en hun doel:

| Taak | Waarom? |
|---|---|
| account deactiveren | voorkomt nieuwe logins met die identiteit |
| actieve sessies intrekken | voorkomt dat een reeds aangemelde browser actief blijft |
| tokens of app passwords intrekken | blokkeert toegang die niet via een gewone interactieve login loopt |
| groepslidmaatschappen en eigenaarschap controleren | voorkomt achterblijvende rechten of objecten zonder eigenaar |
| auditspoor bewaren | laat later aantonen wanneer en door wie de offboarding gebeurde |

Alleen een wachtwoord wijzigen is geen volledige offboarding.

Bij een leaver wil je vooral voorkomen dat bestaande toegang blijft werken.

Controleer daarom:

- kan de gebruiker nog aanmelden?
- bestaan er nog actieve sessies?
- bestaan er nog tokens of app-specifieke wachtwoorden?
- is de gebruiker nog eigenaar van applicaties, secrets of groepen?
- is duidelijk wie de offboarding heeft uitgevoerd?

---

## 9. Multi-factor authentication

MFA gebruikt factoren uit verschillende categorieën.

| Factorcategorie | Voorbeeld |
|---|---|
| iets wat je weet | wachtwoord of pincode |
| iets wat je hebt | authenticator, hardwaretoken of geregistreerd toestel |
| iets wat je bent | biometrisch kenmerk |

Een wachtwoord en een tweede wachtwoord zijn geen sterke twee factoren: beide zijn
kennisfactoren.

MFA verkleint vooral de impact van een gestolen wachtwoord. Als een wachtwoord via
phishing, hergebruik of datalek uitlekt, heeft een aanvaller nog een extra factor nodig.

MFA is geen volledige oplossing voor alle aanvallen. Een gebruiker kan bijvoorbeeld nog
altijd misleid worden om een code in te geven op een valse loginpagina.

### TOTP

Bij TOTP genereren de server en authenticator op basis van een gedeeld geheim en de
huidige tijd dezelfde tijdelijke code.

Voordelen:

| Voordeel | Betekenis |
|---|---|
| breed ondersteund | bijna elke authenticator-app en veel IdP's ondersteunen TOTP |
| offline bruikbaar | de authenticator hoeft geen netwerkverbinding te hebben om een code te tonen |
| eenvoudig in een lab | studenten kunnen enrollment, codegeneratie en validatie zichtbaar volgen |

Risico's:

| Risico | Waarom? |
|---|---|
| phishing blijft mogelijk | een gebruiker kan een TOTP-code nog altijd op een valse pagina invullen |
| enrollmentgeheim beschermen | wie het gedeelde geheim kopieert, kan dezelfde codes genereren |
| herstelcodes veilig bewaren | herstelcodes zijn vaak een alternatieve weg langs MFA |
| klokproblemen | TOTP werkt met tijdvensters; te veel tijdsafwijking veroorzaakt foutieve codes |

TOTP is geschikt voor een onderwijsomgeving omdat studenten duidelijk zien wat er
gebeurt:

```text
Authentik toont enrollment QR-code.
Authenticator bewaart gedeeld geheim.
Elke 30 seconden verschijnt een nieuwe code.
Authentik controleert of de code klopt binnen het tijdsvenster.
```

In productie kunnen phishing-resistente factoren, zoals passkeys of hardwarekeys, een
betere keuze zijn voor beheerders en kritieke toegang.

### MFA-policy

MFA kan bijvoorbeeld verplicht zijn voor:

- beheerders;
- finance-applicaties;
- toegang vanaf externe netwerken;
- externe partners;
- handelingen met hoge impact.

Alleen MFA **aanbieden** is niet hetzelfde als MFA **afdwingen**.

Controleer daarom zowel de effectieve loginflow als het registratie- en
herstelproces:

| Controle | Waarom? |
|---|---|
| wie MFA geregistreerd heeft | registratie alleen bij enkele gebruikers geeft geen organisatiebrede bescherming |
| bij welke flow MFA gevalideerd wordt | MFA moet in de effectieve loginflow zitten, niet alleen ergens geconfigureerd zijn |
| gebruiker zonder factor | het systeem moet duidelijk kiezen tussen blokkeren, enrollen of uitzonderen |
| herstel en verlies | een verloren toestel mag niet leiden tot oncontroleerbare workarounds |

Een bruikbare MFA-test bevat dus minstens twee vragen:

1. Wordt MFA gevraagd wanneer dat moet?
2. Kan een gebruiker zonder geldige tweede factor toch binnen?

De tweede vraag is de belangrijkste negatieve test.

---

## 10. Protocoloverzicht

Identity providers ondersteunen verschillende protocollen omdat niet elke applicatie
op dezelfde manier met identiteit werkt.

Sommige applicaties willen vooral gebruikers en groepen opzoeken. Andere applicaties
willen browser-SSO. Nog andere applicaties willen namens een gebruiker een API
aanroepen. Daarom is het belangrijk om niet alleen de protocolnaam te kennen, maar ook
te begrijpen welk probleem het protocol oplost.

| Protocol | Typisch doel | Belangrijke nuance |
|---|---|---|
| LDAP | gebruikers, groepen en attributen uit een directory opvragen | geen modern browser-SSO-protocol |
| SAML 2.0 | een gebruiker via de browser aanmelden bij een applicatie | vaak gebruikt bij enterprise- en SaaS-applicaties |
| OAuth 2.0 | een applicatie beperkte toegang geven tot een API | op zichzelf geen loginprotocol |
| OpenID Connect | een gebruiker aanmelden en identity-informatie aan een applicatie geven | bouwt verder op OAuth 2.0 |

Een korte vuistregel:

```text
LDAP  -> wie bestaat er in de directory en in welke groepen zit die persoon?
SAML  -> meld deze browsergebruiker aan bij deze enterprise-applicatie.
OAuth -> mag deze applicatie namens iemand een API gebruiken?
OIDC  -> wie is deze aangemelde gebruiker?
```

### LDAP

LDAP is een protocol om directorygegevens te benaderen.

Het wordt gebruikt wanneer een applicatie een centrale directory wil raadplegen.
Die directory bevat bijvoorbeeld gebruikers, groepen, e-mailadressen, afdelingen,
telefoonnummers of andere attributen.

Typische vragen die je met LDAP stelt:

- gebruikers zoeken;
- groepslidmaatschappen lezen;
- controleren of een gebruiker in een bepaalde groep zit;
- attributen opvragen.

LDAP kan ook gebruikt worden om een login te controleren via een **bind**. Een bind is
een aanmeldpoging tegen de directory. Als de directory de bind accepteert, waren de
credentials geldig.

Voorbeeld:

```text
applicatie -> LDAP-server: bestaat gebruiker alice?
applicatie -> LDAP-server: zit alice in groep bp-it?
applicatie -> LDAP-server: klopt het wachtwoord van alice?
```

LDAP is nuttig voor oudere applicaties, netwerkdiensten en systemen die vooral
directoryinformatie nodig hebben. Het lost moderne browser-SSO niet vanzelf op. Een
webapplicatie die alleen LDAP gebruikt, toont meestal nog altijd haar eigen loginpagina.
De gebruiker krijgt dan geen echte SSO-flow met redirects, centrale MFA en tokens.

In Authentik-context:

| Mogelijkheid | Betekenis |
|---|---|
| gebruikers en groepen in Authentik beheren | Authentik is dan zelf de centrale plek voor identitydata in het lab |
| integreren met externe directories | Authentik kan identitydata uit een bestaande bron gebruiken |
| OIDC of SAML voor moderne webapps | de webapp krijgt een echte SSO-flow in plaats van alleen een LDAP-logincontrole |

### SAML

SAML 2.0 is bedoeld voor federated browser-SSO. Dat betekent dat een gebruiker een
applicatie opent, naar de identity provider wordt gestuurd, daar inlogt, en daarna
terugkeert naar de applicatie met een ondertekend bewijs van identiteit.

Begrippen:

- **identity provider**: de partij die de gebruiker authenticeert;
- **service provider**: de applicatie die op de identity provider vertrouwt;
- **assertion**: het ondertekende XML-bericht met informatie over de gebruiker;
- **metadata**: XML-configuratie waarmee IdP en SP elkaars endpoints en certificaten kennen;
- **assertion consumer service URL**: de callback-URL van de applicatie waar de SAML assertion aankomt.

Een vereenvoudigde SAML-flow:

```text
browser -> service provider: open applicatie
service provider -> browser: ga naar identity provider
browser -> identity provider: login
identity provider -> browser: SAML assertion
browser -> service provider: lever assertion af
service provider: controleert handtekening, issuer, audience en geldigheid
```

SAML komt veel voor bij enterprise-applicaties en SaaS.

Voorbeelden:

- een bedrijf koppelt zijn IdP aan een SaaS-platform;
- medewerkers loggen met hun bedrijfsaccount in op een externe applicatie;
- de applicatie ontvangt naam, e-mailadres en groepen of rollen in een assertion.

Sterktes:

| Sterkte | Waarom nuttig? |
|---|---|
| breed enterprise-ondersteund | veel SaaS- en bedrijfsapplicaties bieden SAML-koppelingen aan |
| geschikt voor browser-SSO | de gebruiker kan via redirects bij de IdP aanmelden en terugkeren naar de app |
| metadata en certificaten | IdP en SP kunnen endpoints en sleutels formeel uitwisselen en controleren |

Aandachtspunten:

| Aandachtspunt | Praktisch gevolg |
|---|---|
| XML en certificaatbeheer | kleine fouten in metadata, certificaat of URL kunnen de volledige login breken |
| logout is complex | uitloggen uit één SAML-app betekent niet altijd dat alle sessies weg zijn |
| minder geschikt voor API of mobiel | OAuth 2.0/OIDC past meestal beter bij moderne API- en appscenario's |

### OAuth 2.0

OAuth 2.0 gaat over gedelegeerde toegang.

De centrale vraag van OAuth 2.0 is niet:

> Wie is de gebruiker?

De centrale vraag is:

> Mag deze client beperkte toegang krijgen tot een resource?

Voorbeeld:

> Een applicatie krijgt toestemming om een API te gebruiken zonder het wachtwoord van
> de gebruiker te ontvangen.

Concreet:

```text
gebruiker -> applicatie: ik wil mijn agenda koppelen
applicatie -> authorization server: vraag toestemming
gebruiker -> authorization server: geeft toestemming
applicatie -> API: gebruikt access token
```

Belangrijke rollen:

- **resource owner**: meestal de gebruiker die toegang kan toestaan;
- **client**: de applicatie die toegang vraagt;
- **authorization server**: de server die tokens uitgeeft;
- **resource server**: de API die met een token wordt aangesproken.

Het resultaat van OAuth 2.0 is meestal een **access token**. Dat token is bedoeld voor
de API, niet als bewijs dat een gebruiker correct is aangemeld bij een webapplicatie.

Daarom is deze zin belangrijk:

> OAuth 2.0 zegt vooral wat een applicatie mag doen, niet wie de gebruiker precies is.

In de praktijk wordt OAuth 2.0 vaak verkeerd als loginmechanisme gebruikt. Dat is
verwarrend, omdat een access token niet automatisch de juiste identity-informatie,
audience, issuer en logincontext bevat voor een applicatiesessie. Voor login gebruik je
daarom meestal OpenID Connect.

### OpenID Connect

OpenID Connect, afgekort OIDC, voegt een identity-laag toe aan OAuth 2.0.

OIDC gebruikt OAuth 2.0 als basis, maar voegt afspraken toe waarmee een applicatie
betrouwbaar kan weten wie de gebruiker is. Het belangrijkste extra resultaat is het
**ID token**. Dat token bevat identity-claims over de aangemelde gebruiker.

De belangrijke onderdelen en hun functie:

| Onderdeel | Waarvoor dient het? |
|---|---|
| issuer | unieke naam/URL van de identity provider die tokens uitgeeft |
| client ID | publieke identifier van de applicatie bij de IdP |
| client secret | geheim waarmee een server-side client zich bij het token endpoint bewijst |
| redirect URI | exact toegelaten terugkeeradres na login |
| authorization endpoint | startpunt waar de browser naartoe gaat voor login en consent |
| token endpoint | endpoint waar de applicatie de code inwisselt voor tokens |
| ID token | token met identity-informatie voor de applicatie |
| UserInfo-endpoint | endpoint voor extra gebruikersclaims, indien toegestaan |
| scopes | aanvraag voor soorten informatie of toegang |
| claims | concrete stukjes informatie over gebruiker of login |

Typische OIDC-vraag:

> Deze browsergebruiker heeft ingelogd bij de identity provider. Welke identiteit hoort
> daarbij en mag mijn applicatie die login vertrouwen?

Voorbeeld:

```text
applicatie -> Authentik: stuur gebruiker naar login
Authentik -> applicatie: authorization code
applicatie -> Authentik: wissel code in
Authentik -> applicatie: ID token, eventueel access token
applicatie -> Authentik: vraag eventueel extra claims via UserInfo
```

Een OIDC-client controleert onder meer:

- komt het token van de juiste issuer?
- is het token bedoeld voor mijn client ID?
- is de handtekening geldig?
- is het token nog geldig?
- hoort de login bij de juiste browserflow?

Claims zijn stukjes informatie over de gebruiker. Voorbeelden:

| Claim | Betekenis |
|---|---|
| `sub` | stabiele unieke identifier van de gebruiker |
| `preferred_username` | gebruikersnaam die je kan tonen |
| `email` | e-mailadres |
| `name` | volledige naam |
| `groups` | groepen of rollen, als de IdP die meegeeft |

Scopes bepalen welke informatie de applicatie vraagt. De scope `openid` is verplicht
voor OIDC. Andere scopes, zoals `profile`, `email` of `groups`, vragen extra claims.
Een goed ontwerp vraagt alleen claims die de applicatie echt nodig heeft.

Kernzin:

> OAuth 2.0 gaat primair over toegang; OIDC voegt informatie over de aangemelde
> identiteit toe.

In dit hoofdstuk gebruiken we OIDC omdat het goed past bij moderne webapplicaties en
de werking stap voor stap zichtbaar maakt:

| Reden | Wat leren studenten daaruit? |
|---|---|
| applicatie kent geen wachtwoord | credentials blijven bij de IdP en worden niet verspreid over apps |
| Authentik handelt login, MFA en policies af | centrale configuratie bepaalt de toegangsvoorwaarde |
| applicatie krijgt identity-informatie | studenten zien claims zoals username, e-mail en groepen |
| flow is observeerbaar | redirects, authorization code, token exchange en app-sessie worden tastbaar |

### Welk protocol kies je wanneer?

| Situatie | Logische keuze |
|---|---|
| Een oude applicatie kan alleen gebruikers in een directory opzoeken | LDAP |
| Een SaaS-applicatie vraagt om enterprise-SSO met metadata XML | SAML |
| Een applicatie moet namens een gebruiker een API aanroepen | OAuth 2.0 |
| Een moderne webapplicatie wil gebruikers laten inloggen via een IdP | OpenID Connect |
| Een reverse proxy moet een app zonder eigen SSO beschermen | vaak OIDC/SAML via de proxy of een IdP-outpost |

De keuze hangt dus niet af van welk protocol "het beste" is, maar van wat de
applicatie nodig heeft: directory lookup, browser-SSO, API-autorisatie of
identity-informatie.

---

## 11. OIDC authorization code flow

In de workshop gebruiken we een lokale OIDC-client.

Het doel van deze flow is dat de applicatie een gebruiker kan aanmelden zonder ooit
het wachtwoord van die gebruiker te zien. De browser wordt tijdelijk naar Authentik
gestuurd. Authentik doet de login, MFA en policycontrole. Daarna krijgt de applicatie
een korte code die ze server-side kan inwisselen voor tokens.

Belangrijk onderscheid:

| Onderdeel | Gaat via de browser? | Doel |
|---|---|---|
| authorization code | ja | kort bewijs dat de loginflow geslaagd is |
| token request | nee, server-to-server | code inwisselen voor tokens |
| ID token | naar de client | identity-informatie over de gebruiker |
| app-sessie | lokaal in de applicatie | gebruiker aangemeld houden in de app |

Vereenvoudigde flow:

```text
Browser          OIDC-client          Authentik
   |                  |                   |
   | 1. Open app      |                   |
   |----------------->|                   |
   |                  |                   |
   | 2. Redirect naar authorization endpoint
   |<-----------------|                   |
   |------------------------------------->|
   |                                      |
   | 3. Login, MFA en access policy       |
   |                                      |
   | 4. Redirect met korte code           |
   |<-------------------------------------|
   |----------------->|                   |
   |                  |                   |
   |                  | 5. Code inwisselen|
   |                  |------------------>|
   |                  |<------------------|
   |                  | tokens            |
   |                  |                   |
   | 6. App-sessie    |                   |
   |<-----------------|                   |
```

De authorization code:

- is kort geldig;
- is bedoeld voor eenmalig gebruik;
- wordt via de browser teruggestuurd;
- wordt door de client aan het token endpoint ingewisseld.

Waarom niet meteen tokens via de browser terugsturen?

De authorization code flow beperkt de blootstelling van tokens. De browser ziet vooral
een tijdelijke code. De applicatie wisselt die code daarna zelf in bij Authentik. In
een confidential webapplicatie kan de applicatie daarbij ook haar client secret
gebruiken.

De client voert verschillende controles uit, elk met een specifiek doel:

| Controle | Beschermt tegen |
|---|---|
| `state` klopt | verwisselde of vervalste browserflows |
| redirect URI exact toegestaan | codes die naar een verkeerde bestemming gestuurd worden |
| issuer komt overeen | tokens van een andere of valse IdP |
| tokenhandtekening geldig | zelfgemaakte of gewijzigde tokens |
| audience correct | token dat voor een andere client bedoeld was |
| tijdsclaims geldig | verlopen of nog niet geldige tokens |
| `nonce` hoort bij deze login | hergebruik van tokens uit een andere loginpoging |

De eenvoudige workshopclient maakt de stappen zichtbaar, maar is geen
productie-implementatie van volledige tokenvalidatie.

Wat studenten in het lab moeten herkennen:

- waar de browser wordt doorgestuurd;
- waar de authorization code verschijnt;
- wanneer Authentik de gebruiker controleert;
- wanneer de applicatie tokens ontvangt;
- welke claims de applicatie daarna kan tonen.

---

## 12. Redirect URI, client ID en client secret

### Redirect URI

Na authenticatie stuurt Authentik de browser terug naar een vooraf geregistreerde
redirect URI.

In het lab:

```text
http://localhost:8089/callback
```

Een te brede redirect URI kan een aanvaller helpen om codes of tokens naar een
ongewenste bestemming te sturen.

De redirect URI is dus een veiligheidsgrens. Authentik mag de browser alleen
terugsturen naar URI's die vooraf exact zijn goedgekeurd.

Gebruik daarom in productie de volgende richtlijnen:

| Richtlijn | Waarom? |
|---|---|
| HTTPS | voorkomt dat codes, tokens of sessiecookies leesbaar over het netwerk gaan |
| exacte redirect URI's | beperkt waar Authentik de browser na login naartoe mag sturen |
| geen onnodige wildcards | voorkomt dat een aanvaller een toegelaten subpad of host misbruikt |
| aparte registraties per omgeving | scheidt development, test en productie zodat secrets en redirects niet mengen |

Voorbeelden:

| Redirect URI | Beoordeling |
|---|---|
| `https://portal.example.com/callback` | goed: exact en HTTPS |
| `http://localhost:8089/callback` | aanvaardbaar in dit lokale lab |
| `https://portal.example.com/*` | te breed voor productie |
| `https://evil.example.net/callback` | fout: hoort niet bij de applicatie |

### Client ID

De client ID identificeert de applicatie.

De client ID is niet geheim.

Je mag een client ID vergelijken met een gebruikersnaam voor een applicatie-integratie:
het zegt welke client praat met de identity provider, maar bewijst op zichzelf nog niet
dat die client te vertrouwen is.

### Client secret

Een confidential client gebruikt een client secret om zich bij het token endpoint te
authenticeren.

Voor het client secret gelden de volgende eigenschappen:

| Eigenschap | Praktische betekenis |
|---|---|
| niet in broncode | code wordt gedeeld, gekopieerd en gecommit; secrets lekken daar makkelijk |
| niet in screenshots of verslagen | een verslag kan later breder verspreid worden dan bedoeld |
| niet in publieke repository | crawlers en scanners vinden gelekte secrets zeer snel |
| roteerbaar | bij vermoeden van lek moet je het secret kunnen vervangen zonder alles te herbouwen |
| niet in browsercode of mobiele app | code aan clientzijde is inspecteerbaar door de gebruiker |

Een client secret hoort bij server-side applicaties. Een pure browserapplicatie of
mobiele app kan een secret niet betrouwbaar geheim houden, omdat de gebruiker de code
of app kan inspecteren.

In het lab zetten studenten het secret in `.env`. Dat is beter dan hardcoderen, maar
nog geen volledige productie-secret-managementoplossing.

---

## 13. Tokens, scopes en claims

### ID token

Een ID token bevat claims over de authenticatie en identiteit.

Het ID token is bedoeld voor de applicatie die de gebruiker wil aanmelden. De
applicatie gebruikt het om te controleren welke identiteit Authentik heeft vastgesteld.

Mogelijke claims:

| Claim | Betekenis | Waarom belangrijk? |
|---|---|---|
| `iss` | issuer | toont welke IdP het token uitgegeven heeft |
| `sub` | stabiele subject identifier | beste technische sleutel om dezelfde gebruiker later opnieuw te herkennen |
| `aud` | bedoelde client | voorkomt dat een token voor app A gebruikt wordt bij app B |
| `exp` | vervaltijd | bepaalt tot wanneer het token geldig mag zijn |
| `iat` | uitgiftetijd | helpt beoordelen wanneer de logincontext gestart is |
| `email` | e-mailadres | handig voor communicatie of weergave, maar niet altijd stabiele identiteit |
| `preferred_username` | gebruikersnaam | leesbaar voor mensen, maar minder geschikt als unieke sleutel |
| `groups` | groepen of rollen | kan gebruikt worden voor applicatietoegang, maar moet bewust beperkt worden |

Een ID token is meestal een JWT.

Een JWT bestaat uit drie base64url-gecodeerde delen:

```text
header.payload.signature
```

Een token kunnen decoderen is niet hetzelfde als het token cryptografisch valideren.

Dat onderscheid is belangrijk:

```text
decoderen  -> de inhoud leesbaar maken
valideren  -> controleren of de inhoud betrouwbaar is
```

Een aanvaller kan zelf tekst in JWT-formaat maken. Pas na controle van handtekening,
issuer, audience en geldigheid mag een applicatie het token vertrouwen.

### Access token

Een access token geeft toegang tot een resource of endpoint binnen de toegekende
scope.

Het access token is geen wachtwoord, maar moet wel als geheim behandeld worden.

Gebruik een access token niet als algemeen bewijs van login. Het token is bedoeld voor
een resource server of API. Welke API het token accepteert, hangt af van audience,
scope en providerconfiguratie.

### Refresh token

Een refresh token kan gebruikt worden om nieuwe access tokens te verkrijgen.

Dat verlengt de mogelijke toegang en vraagt dus extra bescherming. Vraag
`offline_access` alleen wanneer de applicatie dit echt nodig heeft.

Refresh tokens zijn handig voor lange sessies of achtergrondtaken, maar vergroten de
impact van diefstal. Daarom worden ze in veel omgevingen extra beperkt, geroteerd of
niet aan elke client gegeven.

### Scopes

Een client vraagt scopes.

Veelgebruikte OIDC-scopes:

| Scope | Doel |
|---|---|
| `openid` | activeert OpenID Connect |
| `profile` | basisprofielclaims |
| `email` | e-mailclaims |
| `offline_access` | mogelijkheid tot refresh token, indien toegestaan |

Dataminimalisatie:

> Geef een applicatie alleen claims en scopes die ze nodig heeft.

Praktische vertaling:

| Applicatiebehoefte | Mogelijke scope/claim |
|---|---|
| gebruiker uniek herkennen | `openid` en `sub` |
| naam tonen in de UI | `profile` |
| e-mailadres tonen of gebruiken | `email` |
| toegang in app koppelen aan groepen | groepsclaim, indien bewust geconfigureerd |

Meer claims maken een applicatie niet automatisch veiliger. Ze geven de applicatie
vooral meer persoonsgegevens en meer beslissingsinformatie.

---

## 14. Authentik: application en provider

In Authentik zijn een application en een provider twee verschillende objecten.

Dat onderscheid is belangrijk omdat studenten anders snel alles onder "de app" plaatsen.
In Authentik beschrijft de application vooral de gebruikers- en toegangskant. De
provider beschrijft hoe het protocol technisch werkt.

### Application

De application beschrijft de functionele en gebruikersgerichte kant:

| Application-instelling | Functionele betekenis |
|---|---|
| naam en zichtbaarheid | bepaalt hoe gebruikers de applicatie herkennen in het portaal |
| launch URL | bepaalt waar de gebruiker naartoe gaat bij het openen van de app |
| gekoppelde provider | bepaalt welk protocol en welke technische koppeling gebruikt wordt |
| bindings | bepalen welke gebruikers, groepen of policies toegang krijgen |
| presentatie | maakt de applicatie begrijpelijk en onderscheidbaar voor eindgebruikers |

Vragen die bij een application horen:

- Hoe heet de applicatie voor gebruikers?
- Verschijnt ze in het gebruikersportaal?
- Welke groep of policy mag ze openen?
- Welke provider gebruikt ze achter de schermen?
- Waar moet de gebruiker naartoe wanneer de app gestart wordt?

### Provider

De provider beschrijft de protocolkant.

Voor een OAuth2/OIDC-provider omvat dat onder meer:

| Provider-instelling | Technische betekenis |
|---|---|
| client ID | identifier die de OIDC-client gebruikt |
| client secret | geheim voor server-side tokenuitwisseling |
| redirect URI's | toegelaten callback-adressen na login |
| authorization flow | bepaalt welke login- en policyflow doorlopen wordt |
| scopes | bepaalt welke informatie of toegang gevraagd kan worden |
| tokeninstellingen | beïnvloedt geldigheid, inhoud en type tokens |
| signing key | sleutel waarmee tokens betrouwbaar ondertekend worden |
| issuergedrag | bepaalt welke issuer clients in tokens en discovery verwachten |

Conceptueel:

```text
Application = welke app en wie mag ze zien/gebruiken?
Provider    = met welk protocol en welke technische parameters?
```

Een veelgemaakte fout is alleen een application maken zonder correct gekoppelde
provider, of de provider goed configureren maar geen toegangsbindings op de
application zetten.

Mentale scheiding:

```text
Application:
  "BluePeak Portal bestaat en is zichtbaar voor deze gebruikers."

Provider:
  "BluePeak Portal gebruikt OIDC met deze redirect URI, client ID en scopes."
```

Bij troubleshooting kijk je daarom in twee richtingen:

| Probleem | Waar kijk je eerst? |
|---|---|
| app verschijnt niet of gebruiker krijgt deny | application en bindings |
| redirect URI wordt geweigerd | provider |
| client secret werkt niet | provider |
| verkeerde claims zichtbaar | provider scopes/property mappings |
| gebruiker ziet app maar login faalt technisch | provider en clientconfiguratie |

---

## 15. Groepsgebaseerde applicatietoegang

Voorbeeldbeleid:

| Applicatie | Toegang |
|---|---|
| medewerkersportaal | `bp-employees` |
| monitoring | `bp-it` |
| finance | `bp-finance` |
| partnerportaal | `bp-partners` |

In Authentik kan een groep aan een application gebonden worden.

Groepsgebaseerde toegang vertaalt een organisatorische beslissing naar techniek.
De groep is niet het doel op zich. De groep is het middel om te zeggen:

> Deze personen hebben een zakelijke reden om deze applicatie te gebruiken.

Sterke testmatrix:

| Identiteit | Groep | Medewerkersportaal | Verwacht |
|---|---|---|---|
| Alice | `bp-employees` | openen | allow |
| Bob | `bp-employees`, `bp-it` | openen | allow |
| Eva | `bp-partners` | openen | deny |
| gedeactiveerde Alice | `bp-employees` | aanmelden | deny |

Test niet alleen de toegelaten gebruiker.

Kernzin:

> Een access policy is pas aangetoond wanneer zowel toegelaten als geweigerde gevallen
> correct getest zijn.

Waarom negatieve tests zo belangrijk zijn:

Een succesvolle login toont alleen dat minstens één pad werkt. Ze toont niet dat de
grenzen correct staan. Een foutieve binding kan bijvoorbeeld alle aangemelde gebruikers
toelaten. Dat merk je pas wanneer je ook een gebruiker test die geweigerd moet worden.

---

## 16. Audit logs

Identity-infrastructuur is een belangrijk auditpunt.

Nuttige gebeurtenissen:

| Gebeurtenis | Wat kan je ermee aantonen of onderzoeken? |
|---|---|
| geslaagde login | welke gebruiker toegang kreeg en wanneer |
| mislukte login | fout wachtwoord, verkeerde gebruiker of mogelijk brute-forcegedrag |
| MFA-validatie | of een tweede factor effectief gevraagd en aanvaard werd |
| gebruiker aangemaakt of aangepast | wie identitygegevens of status gewijzigd heeft |
| groepslidmaatschap gewijzigd | waarom toegang tot applicaties veranderde |
| application of provider gewijzigd | of een technische configuratiewijziging loginproblemen veroorzaakte |
| toegang geweigerd door een policy | dat autorisatiegrenzen effectief afgedwongen worden |
| sessie ingetrokken | dat een beheerder of systeem bestaande toegang heeft afgebroken |
| account gedeactiveerd | wanneer offboarding of blokkering technisch gebeurde |

Een logregel moet in context onderzocht worden. Die context maakt de gebeurtenis
bruikbaar:

| Contextvraag | Waarom nodig? |
|---|---|
| wanneer? | koppelt het event aan lessenrooster, werkuren, incidenttijdlijn of offboarding |
| welke gebruiker? | bepaalt welke identiteit of account onderzocht moet worden |
| bronadres? | helpt interne toegang, VPN, labmachine of verdachte locatie onderscheiden |
| applicatie of flow? | toont of het om admin, user login, OIDC of MFA ging |
| resultaat? | onderscheidt succesvolle toegang van fout, blokkering of policy deny |
| beheerwijziging vooraf? | verklaart waarom gedrag plots veranderde |

Een auditlog voorkomt geen aanval. Het helpt wel bij detectie, onderzoek,
verantwoording en herstel.

Neem credentials en volledige tokens nooit op in een verslag.

### Wat zoek je in auditlogs?

Auditlogs beantwoorden vragen achteraf.

Voorbeelden:

| Vraag | Mogelijke logcontext |
|---|---|
| Wie heeft Bob aan `bp-it` toegevoegd? | beheeractie op groepslidmaatschap |
| Waarom kon Eva niet inloggen? | policy deny of foutieve credentials |
| Heeft MFA gewerkt? | MFA-validatie of authenticator event |
| Wanneer is Alice gedeactiveerd? | user update of deactivation event |
| Welke app werd geopend? | application launch of authorization event |

Goede logging is alleen bruikbaar als tijd, bron, gebruiker en resultaat duidelijk zijn.
Daarom is tijdsynchronisatie ook voor identity-infrastructuur belangrijk.

---

## 17. Service accounts

Niet elke identiteit is een mens.

Voorbeelden:

- back-upsoftware;
- monitoringintegratie;
- CI/CD-pipeline;
- applicatie die een API aanroept.

Voor een service account gelden de volgende regels:

| Regel | Reden |
|---|---|
| duidelijke eigenaar | iemand moet verantwoordelijk zijn voor gebruik, rotatie en incidenten |
| beperkt doel | een service account voor back-ups mag niet ook beheerder van alles zijn |
| least privilege | een gelekt credential heeft dan minder impact |
| geen gedeeld persoonlijk account | automatisatie mag niet afhangen van het dienstverband van één persoon |
| roteerbare credentials | secrets moeten vervangen kunnen worden zonder de integratie te herbouwen |
| monitoring | machineaccounts vallen minder op, dus afwijkend gebruik moet zichtbaar zijn |
| vervaldatum of reviewdatum | voorkomt dat oude integraties jarenlang ongezien actief blijven |

Interactieve MFA past meestal niet bij machine-to-machineverkeer. Daarvoor bestaan
andere flows en credentials.

Belangrijk onderscheid:

| Menselijke identiteit | Service account |
|---|---|
| gekoppeld aan een persoon | gekoppeld aan een systeem of integratie |
| interactieve login mogelijk | meestal geen interactieve login |
| MFA vaak zinvol | MFA vaak niet bruikbaar |
| rechten volgen functie | rechten volgen technisch doel |
| account stopt bij vertrek | account stopt bij einde integratie |

Gebruik geen persoonlijk account voor automatisatie. Als Alice vertrekt, mag de back-up
niet plots stoppen omdat een script met haar persoonlijke login werkte.

---

## 18. Netwerkplaatsing en beschikbaarheid

Een identity provider is ook een netwerkservice.

Omdat veel applicaties van de IdP afhangen, moet je ze ontwerpen als kritieke
infrastructuur. Een fout in DNS, TLS, database, tijd of reverse proxy kan tegelijk veel
logins verstoren.

Bij een productieontwerp raakt elke vraag een ander betrouwbaarheids- of
veiligheidsaspect:

| Productievraag | Waarom moet je dit weten? |
|---|---|
| DNS-naam van de IdP | OIDC/SAML-clients verwachten een stabiele issuer en endpoints |
| waar TLS eindigt | bepaalt waar verkeer ontsleuteld wordt en welke segmenten beschermd zijn |
| bereikbaarheid van token- of metadata-endpoint | clients moeten tokens kunnen inwisselen en configuratie kunnen ophalen |
| toegang tot admininterface | beheerfuncties mogen niet voor elk netwerk bereikbaar zijn |
| back-up van database en configuratie | identityconfiguratie is nodig voor herstel na fout of uitval |
| gedrag bij uitval | bepaalt of applicaties fail-closed, fail-open of tijdelijk onbruikbaar worden |
| tijdsynchronisatie | tokens, sessies en TOTP vertrouwen op correcte tijd |
| certificaten en signing keys | bepalen of clients tokens en metadata kunnen vertrouwen |

Vereenvoudigd:

```text
gebruikers
    |
 HTTPS
    |
reverse proxy / load balancer
    |
identity provider
    |
database en beveiligde opslag
```

De workshop gebruikt HTTP op localhost om de flow zichtbaar te maken.

> HTTP op localhost is een labkeuze, geen productieontwerp.

Voor productie denk je minstens na over:

| Thema | Waarom belangrijk? |
|---|---|
| DNS | applicaties en browsers moeten dezelfde issuer stabiel bereiken |
| TLS | credentials, cookies en tokens mogen niet leesbaar over het netwerk |
| Back-up | gebruikers, groepen, flows en providers zijn configuratiekritiek |
| Redundantie | IdP-uitval kan veel applicaties blokkeren |
| Tijd | tokens en TOTP hangen af van correcte tijd |
| Signing keys | tokens blijven alleen betrouwbaar als sleutels beschermd zijn |
| Admin access | de beheerinterface mag niet breder openstaan dan nodig |

---

## 19. Typische risico's en fouten

| Fout | Gevolg | Betere aanpak |
|---|---|---|
| iedereen krijgt toegang omdat er geen binding is | te brede toegang | expliciete groepen en negatieve tests |
| client secret in Git of verslag | credentiallek | secret store en rotatie |
| wildcard redirect URI | code kan verkeerd eindigen | strikte redirect URI |
| MFA alleen geregistreerd, niet gevalideerd | schijnveiligheid | flow en test controleren |
| adminaccount voor dagelijks gebruik | grote impact bij compromis | apart beheerdersaccount |
| alleen positieve test | foutieve policy blijft onzichtbaar | allow- en deny-test |
| account gedeactiveerd, sessies blijven actief | toegang duurt mogelijk voort | sessies en tokens intrekken |
| geen TLS | credentials of sessies onderschepbaar | HTTPS |
| alle claims naar elke app | privacy- en datarisico | dataminimalisatie |
| IdP zonder back-up of redundantie | brede uitval | HA-, back-up- en herstelplan |
| tijd niet correct | TOTP- en tokenproblemen | betrouwbare tijdsynchronisatie |

Gebruik deze tabel als checklist bij ontwerpen en troubleshooting. Bij bijna elke fout
kan je dezelfde vragen stellen:

- Is dit een authenticatieprobleem?
- Is dit een autorisatieprobleem?
- Is dit een protocolconfiguratieprobleem?
- Is dit een sessie- of tokenprobleem?
- Is dit een lifecycleprobleem?

Die indeling helpt om niet willekeurig instellingen te wijzigen.

---

## 20. Testplan voor centrale identiteit

Een bruikbaar testplan bevat functionele, negatieve en lifecycle-tests.

| Test | Verwacht | Waarom test je dit? |
|---|---|---|
| medewerker meldt aan | login slaagt | bewijst dat authenticatie en basisflow werken |
| tweede gekoppelde app openen | SSO zonder nieuwe wachtwoordprompt | toont dat de IdP-sessie hergebruikt wordt |
| partner opent medewerkersapp | toegang geweigerd | bewijst dat autorisatiegrenzen werken |
| gebruiker krijgt juiste claims | username, e-mail en relevante groepen zichtbaar | controleert welke identity-informatie de app ontvangt |
| gebruiker met TOTP meldt opnieuw aan | tweede factor gevraagd | bewijst dat MFA in de loginflow zit |
| fout wachtwoord | login faalt en event verschijnt | controleert foutafhandeling en logging |
| gebruiker wordt gedeactiveerd | nieuwe login faalt | test lifecycle en offboarding |
| actieve sessie wordt ingetrokken | herauthenticatie nodig | controleert of bestaande toegang kan worden afgebroken |
| client gebruikt verkeerde redirect URI | OIDC-request geweigerd | test bescherming tegen foutieve of kwaadaardige callbacks |
| beheerder wijzigt groepslidmaatschap | wijziging verschijnt in auditlog | bewijst dat beheeracties traceerbaar zijn |

Een screenshot van een succesvolle login bewijst niet dat de policy volledig klopt.

Een goed testplan beschrijft steeds:

- welke identiteit je gebruikt;
- welke groep of status die identiteit heeft;
- welke applicatie je test;
- wat je verwacht;
- welk bewijs je verzamelt;
- waar je het event in de auditlogs terugvindt.

Voorbeeldnotatie:

```text
Test: Eva opent BluePeak Portal
Identiteit: eva.partner
Groep: bp-partners, niet bp-employees
Verwachting: deny
Bewijs: foutmelding of deny-scherm + audit event
```

Zo leren studenten niet alleen klikken, maar ook bewijzen dat hun ontwerp werkt.

---

## 21. Voorbereiding op hoofdstuk 10

In dit hoofdstuk koppelen we een applicatie rechtstreeks via OIDC aan Authentik.

In hoofdstuk 10 beschermen we applicaties die zelf geen OIDC ondersteunen via de
reverse proxy en Authentik.

Verschil:

```text
Ch9:
applicatie ondersteunt OIDC -> applicatie praat met Authentik

Ch10:
legacy app ondersteunt geen OIDC -> proxy/outpost voegt authenticatielaag toe
```

Dezelfde identity-principes blijven gelden:

- groepen;
- least privilege;
- MFA;
- sessies;
- auditlogs;
- positieve en negatieve tests.

---

## 22. Samenvatting

Belangrijkste inzichten:

- authenticatie bepaalt wie iemand is;
- autorisatie bepaalt wat die identiteit mag;
- een identity provider centraliseert authenticatie en identity-informatie;
- SSO gebruikt een centrale IdP-sessie naast applicatiesessies;
- groepen en application bindings kunnen applicatietoegang sturen;
- Authentik-rollen zijn niet automatisch rollen binnen een doelapplicatie;
- MFA registreren en MFA afdwingen zijn verschillende zaken;
- OAuth 2.0 en OIDC zijn niet hetzelfde;
- een OIDC-provider bevat de protocolconfiguratie;
- een Authentik-application bevat onder meer presentatie en toegangsbindings;
- redirect URI's en client secrets moeten zorgvuldig beheerd worden;
- claims moeten minimaal en doelgericht zijn;
- identity lifecycle omvat onboarding, functiewijziging en offboarding;
- auditlogs en negatieve tests zijn essentieel;
- de identity provider is kritieke infrastructuur en vraagt TLS, back-up en
  beschikbaarheidsplanning.

Kernzin:

> Centrale identiteit maakt toegang consistenter en beter beheerbaar, op voorwaarde dat
> authenticatie, autorisatie, lifecycle, sessies en auditing bewust ontworpen en getest
> worden.
