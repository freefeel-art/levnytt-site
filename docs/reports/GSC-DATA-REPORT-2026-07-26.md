# GSC Data Report — LevNytt 26.7.2026

**Data source:** Google Search Console API, 90 days (27.4. – 26.7.2026)
**Site:** https://levnytt.se

---

## 1. Kokonaiskuva

| Mittari | Arvo |
|---|---|
| Hakukyselyitä | 136 |
| Klikkauksia | 2 |
| Näyttökertoja | 461 |
| CTR | 0,43 % |
| Keskimääräinen sijoitus | 32,2 |

**Tulkinta:** Sivusto on käytännössä näkymätön Googlelle. Kahden klikkauksen liikenne kolmessa kuukaudessa tarkoittaa, että yksikään merkittävä hakusana ei tuota liikennettä.

---

## 2. Mitä data paljastaa

### Mitä sivustolla ON

Sivusto näkyy lähinnä erikoisilla, tieteellisillä hakusanoilla:

| Hakusanaryhmä | Näyttökerrat | Paras sijoitus | Klikkauksia |
|---|---|---|---|
| Karotenoidit (karotenoid, karoten, betakaroten...) | 126 | 3,0 | 1 |
| Solukalvo (cellmembran...) | 46 | 22,0 | 0 |
| Nitraatit | 36 | 19,4 | 0 |
| Direktförsäljning | 56 | 11,5 | 0 |
| Omega-3 / EPA / DHA | 77 | 10,0 | 0 |
| NeoLife (branded) | 13 | 1,0 | 0 |

Nämä ovat matalan volyymin hakusanoja. Yksikään ei tuota merkittävää liikennettä, vaikka sijoitus olisi kohtuullinen (karotenoidit positiossa 6,9 — 17 näyttöä, nolla klikkiä).

### Mitä sivustolta PUUTTUU

Seuraavat hakusanat eivät näy GSC-datassa lainkaan:

- `magnesium` — ei näyttökertoja
- `d-vitamin` — ei näyttökertoja
- `probiotika` — ei näyttökertoja
- `multivitamin` — ei näyttökertoja
- `omega 3` (ilman EPA/DHA-tarkennusta) — ei näyttökertoja
- `kosttillskott` — ei näyttökertoja

**Nämä ovat hakusanat, joilla on todellista volyymia.** LevNyttillä on sivuja näistä aiheista, mutta ne eivät näy Googlen hakutuloksissa lainkaan (sijoitus > 100).

---

## 3. Juurisyyanalyysi

### Miksi liikennettä ei tule?

**1. Domain-auktoriteetti on lähes nolla.**
Uusi sivusto ilman merkittäviä takalinkkejä ei rankkaa kilpailluilla hakusanoilla. Magnesium, D-vitamiini ja probiootit ovat erittäin kilpailtuja — etusivulla ovat Livsmedelsverket, 1177.se, Apoteket.se, ja suuret terveyssivustot.

**2. Sisältö kohdistuu liian spesifeihin hakusanoihin.**
"Glukosinolater", "fytosteroler", "karotenoider" — nämä ovat tieteellisiä termejä, joita tavallinen kuluttaja ei hae. Sivustolla on 110 sivua, mutta hyvin harva kohdistuu hakusanaan jolla on todellista hakuvolyymia.

**3. Indeksointi on kesken.**
Magnesium-, D-vitamiini- ja probioottisivut eivät näy GSC:ssä lainkaan. Tämä voi tarkoittaa, että Google ei ole vielä indeksoinut niitä kunnolla, tai ne on indeksoitu mutta ne rankkaavat huonosti (position >100 rajalla).

**4. CTR on nolla myös kohtuullisilla sijoituksilla.**
"Karotenoider" positiossa 9,4 — 16 näyttöä, nolla klikkiä. "Karotenoid" positiossa 6,9 — 17 näyttöä, nolla klikkiä. Tämä viittaa siihen, että otsikko ja meta-kuvaus eivät vastaa hakuaikeeseen, tai brändi on tuntematon.

---

## 4. Kolme tärkeintä toimenpidettä seuraaville 30 päivälle

### 1. Varmista indeksointi ydinsivuille

Magnesium-, D-vitamiini-, probiootti- ja omega-3 -sivut eivät näy GSC:ssä. Jos ne eivät ole indeksoituneet, mikään optimointi ei auta.

**Toimenpide:** Mene Google Search Consoleen → Indexing → Pages. Tarkista, onko avainsivut indeksoitu. Jos ei: "Request Indexing" manuaalisesti. Päivitä sitemap.

### 2. Tuota 3-5 artikkelia saavutettaville hakusanoille

Nykyinen sisältö kohdistuu liian spesifeihin termeihin. Tarvitaan sisältöä hakusanoille, joilla on kohtuullinen volyymi mutta matala kilpailu — sellaisia, joihin uusi sivusto voi realistisesti rankata.

DataForSEO-analyysi paljastaisi tarkat hakusanat, mutta ilman sitäkin voidaan päätellä: pitkän hännän kysymysmuotoiset haut ("hjälper magnesium mot sömnproblem", "vilken magnesiumform är bäst för") ovat saavutettavampia kuin yhden sanan termit.

### 3. Korjaa CTR olemassa oleville sijoituksille

"Karotenoider" (pos 9,4) ja "direktförsäljning" (pos 13,7) saavat näyttökertoja mutta nolla klikkiä. Näiden sivujen title- ja meta description -tagit eivät ole tarpeeksi houkuttelevia.

**Toimenpide:** Tarkista karotenoidi- ja direktförsäljning-sivujen SERP-ulkoasu. Testaa houkuttelevampaa otsikkoa. Pienikin CTR-parannus (0% → 3%) moninkertaistaisi liikenteen näille sivuille.

---

## 5. Mitä data sanoo strategiastamme

**Aiempi oletus:** "Sivustolla on 110 sivua laadukasta sisältöä — liikenne seuraa automaattisesti."

**Mitä data sanoo:** Ei seuraa. Laadukas sisältö ilman domain-auktoriteettia, ilman kohdistusta todellisiin hakusanoihin ja ilman indeksointia ei tuota liikennettä.

**Tämä ei tarkoita että sisältö on huonoa.** Se tarkoittaa, että emme ole vielä rakentaneet perustaa: näkyvyyttä Googlessa. 110 sivua on hyvä alku, mutta ne kohdistuvat vääriin hakusanoihin.

---

## 6. Mitä ei kannata tehdä

- **Älä optimoi olemassa olevia sivuja.** Ne rankkaavat niin huonosti, että title-tagin parantaminen ei auta.
- **Älä rakenna lisää teknisiä työkaluja.** GSC-data on nyt käytössä — sitä pitää käyttää sisältöpäätöksiin, ei uusien työkalujen rakentamiseen.
- **Älä jahtaasi suuria hakusanoja.** "Magnesium" ja "kosttillskott" ovat liian kilpailtuja. Aloita pitkästä hännästä.
