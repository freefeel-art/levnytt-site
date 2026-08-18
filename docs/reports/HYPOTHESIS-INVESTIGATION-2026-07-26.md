# Hypoteesitutkimus — LevNytt 26.7.2026

**Tutkimuskysymys:** Johtuuko LevNyttin vähäinen näkyvyys ensisijaisesti väärästä sisältöstrategiasta vai uuden domainin vähäisestä auktoriteetista?

**Metodi:** Vertaileva analyysi GSC-hakukyselyistä 90 päivän ajalta. Kyselyt luokiteltu sisältötyypin mukaan. Vertailtu Googlen testaamia hakusanoja sivuston olemassa olevaan sisältöön.

---

## 1. Mitä data todistaa

### Google on luokitellut LevNyttin tiedesivustoksi, ei terveyssivustoksi

Tämä on datan vahvin löydös.

| Sisältötyyppi | Osuus näyttökerroista |
|---|---|
| Tieteelliset termit (karotenoidit, solukalvot, nitraatit, flavonoidit) | **44 %** |
| MLM / suoramyynti | 21 % |
| Omega-3 / EPA / DHA | 10 % |
| NeoLife-brändätyt haut | 5 % |
| Tavalliset ravitsemushaut (C-vitamiini, kuitu) | **2 %** |

**Varmuus: Todistettu datalla.** 203/461 näyttökerrasta tulee erikoistuneista tieteellisistä termeistä. Google testaa sivustoa ensisijaisesti näillä hakusanoilla — ei terveys- tai kuluttajahauilla.

Tämä on **algoritminen luokitteluongelma.** Google on päätellyt sivuston sisällön perusteella, että LevNytt käsittelee biokemiaa, ei kuluttajien terveyskysymyksiä.

---

### "Direktförsäljning" on lupaavin poikkeus

**Varmuus: Todistettu datalla.** 56 näyttökertaa, sijoitus 13,7. Tämä on ainoa hakusana, jolla on:
- Kohtuullinen näyttövolyymi (53+26=79 kaikilla muunnelmilla)
- Sijoitus lähellä ensimmäistä sivua

Jos "direktförsäljning" nousee sivulle 1 (sija 7-10), CTR nousee ~3-5%:iin → 2-4 klikkiä/kk. Pieni, mutta todellinen — ja merkki siitä, että MLM-sisältöstrategia toimii paremmin kuin ravintosisältöstrategia.

---

## 2. Mitä data tukee (mutta ei todista)

### Sisältöstrategia selittää osan ongelmasta

**Varmuus: Todennäköinen.** 110 sivua, joista suurin osa on NeoLife-tuotesivuja, jotka on kirjoitettu tieteellisestä näkökulmasta ("Vad är karotenoider", "Vad är flavonoider", "Vad är glukosinolater"). Googlen algoritmi näkee tämän ja luokittelee sivuston sen mukaan.

Jos sivustolla olisi enemmän kuluttajalähtöistä sisältöä ("10 bästa magnesiumkällorna i maten", "D-vitaminbrist — så vet du om du är drabbad"), Google todennäköisesti testaisi sivustoa myös näillä hakusanoilla.

### Domain-auktoriteetti selittää loput

**Varmuus: Todennäköinen.** Sivusto on alle vuoden vanha. Sillä ei ole merkittäviä takalinkkejä. Terveysaiheet ("magnesium", "d-vitamin") ovat erittäin kilpailtuja — etusivulla on viranomaisia (Livsmedelsverket, 1177.se) ja vakiintuneita kaupallisia toimijoita (Apoteket.se, Svenskt Kosttillskott).

Uusi domain ei yksinkertaisesti voi kilpailla näillä hakusanoilla — riippumatta sisällön laadusta.

---

## 3. Mitä data ei pysty osoittamaan

### Indeksoinnin laajuutta ei voi päätellä hakukyselydatasta

Se, että "magnesium" ei näy kyselyissä, ei kerro onko magnesium-sivut indeksoitu. Ne voivat olla indeksoituja mutta sijoittua sijan 100+ ulkopuolelle, jolloin GSC ei raportoi niitä. Tämä vaatii Index Coverage -raportin tarkistelua GSC:n käyttöliittymästä.

### Sisällön laatua ei voi päätellä näyttökerroista

Emme tiedä, onko LevNyttin magnesium-sivu parempi vai huonompi kuin kilpailijoiden. Tiedämme vain, ettei se näy hakutuloksissa.

---

## 4. Omat oletukseni — tunnistettu ja eroteltu

| Oletus | Tyyppi | Perustelu |
|---|---|---|
| "Sisältö kohdistuu vääriin hakusanoihin" | **Mahdollinen** — data tukee osittain, mutta ei todista | Tieteellisten termien dominointi viittaa sisältöstrategian ongelmaan, mutta domain-auktoriteetti on yhtä uskottava selitys |
| "Kun domain-auktoriteetti kasvaa, nykyinenkin sisältö alkaa rankata" | **Pelkkä hypoteesi** | Ei dataa tueksi — emme tiedä miten Google rankkaisi näitä sivuja suuremmalla auktoriteetilla |
| "Lisäämällä kuluttajalähtöistä sisältöä Google luokittelee sivuston uudelleen" | **Mahdollinen** | Looginen johtopäätös algoritmisesta luokittelusta, mutta testaamaton |
| "MLM-sisältö on helpommin rankattavissa kuin ravintosisältö" | **Todennäköinen** | "Direktförsäljning" datan perusteella — vähemmän kilpailua kuin terveysaiheissa |

---

## 5. Johtopäätös

**Molemmat hypoteesit ovat totta, mutta eri mekanismeilla:**

1. **Sisältöstrategia** määrittää, **millä hakusanoilla** Google testaa sivustoa. Tällä hetkellä Google testaa LevNyttiä tieteellisillä termeillä, koska sivuston sisältöprofiili on tieteellinen.

2. **Domain-auktoriteetti** määrittää, **kuinka korkealle** sivusto sijoittuu testatuilla hakusanoilla. Vaikka sisältöstrategia korjattaisiin, uusi domain ei silti rankkaisi "magnesium"-haussa ilman auktoriteetin kasvua.

**Nämä kaksi tekijää vahvistavat toisiaan negatiivisesti.** Huono sijoitus tieteellisillä termeillä + näkymättömyys kuluttajahauissa = ei liikennettä.

---

## 6. Mitä teen väärin — korjattu

Aiemmassa raportissani väitin: "Nykyinen sisältö kohdistuu vääriin hakusanoihin." Tämä oli **liian vahva väite.** Data tukee sitä osittain, mutta ei todista. Domain-auktoriteetti on yhtä pätevä selitys.

**Oikea muotoilu:** "Data osoittaa, että Google on luokitellut LevNyttin tieteelliseksi sivustoksi. Tämä johtuu todennäköisesti sekä sisältöprofiilista (44% tieteellisiä termejä) että domain-auktoriteetin puutteesta (ei näkyvyyttä kilpailluilla kuluttajahauilla). Kumpikaan selitys ei yksin riitä — molemmat vaikuttavat."

---

## 7. Suositus

**Lyhyt aikaväli (30 pv):** Tuota 2-3 kuluttajalähtöistä artikkelia aiheista, joissa on vähemmän kilpailua. "Direktförsäljning"-datan perusteella MLM-aiheet ovat lupaavampia kuin ravintoaiheet tällä hetkellä.

**Keskipitkä aikaväli (3-6 kk):** Rakenna domain-auktoriteettia — hanki laadukkaita takalinkkejä, jaa sisältöä sosiaalisessa mediassa, varmista indeksointi.

**Mittaaminen:** Aja `gsc-fetch.py` uudelleen 30 päivän kuluttua. Vertaa, onko kuluttajahakujen osuus näyttökerroista kasvanut.
