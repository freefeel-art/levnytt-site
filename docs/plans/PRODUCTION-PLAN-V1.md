# Production Plan v1 — LevNytt 6kk kasvusuunnitelma

**Perustuu:** GSC-dataan (26.7.2026), repositorion nykytilaan, aiempiin strategisiin päätöksiin
**Ajanjakso:** 27.7.2026 – 27.1.2027

---

## 1. Kuuden kuukauden päätavoitteet

Viisi priorisoitua tavoitetta:

| # | Tavoite | Mittari | Mistä tiedämme onnistuimmeko |
|---|---|---|---|
| 1 | Ensimmäinen orgaanisen liikenteen läpimurto | GSC-klikit | Vähintään 50 klikkiä/kk GSC:n mukaan (nyt 0,7/kk) |
| 2 | Sivu 1 -sijoitus ei-brändätyllä hakusanalla | GSC-sijoitus | Yksi sivu positiossa 1-10 hakusanalla jolla on >50 imp/kk |
| 3 | Kaksi täyttä aiheklusteria sisäisellä linkityksellä | Repo | Magnesium (10 sivua) + MLM (10 sivua), kaikki ristiinlinkitetty |
| 4 | Kuukausittainen GSC-datan seurantarytmi | Prosessi | 6 peräkkäistä kuukausiraporttia `docs/reports/gsc-monthly/` |
| 5 | Vähintään 48 uutta/parannettua sivua | Repo | ~158 sivua yhteensä (nyt ~110) |

**Perustelu tavoitteiden määrälle:** Viisi on maksimi mitä voi seurata ilman että fokus hajoaa. Jokaisella on yksi selkeä mittari.

---

## 2. Sisältöstrategia

### Mitä julkaistaan — ja miksi juuri tämä määrä

| Sisältötyyppi | Määrä / 6kk | Perustelu |
|---|---|---|
| **Uudet informaatioartikkelit** | 25 | GSC-data osoittaa, että kuluttajahaut puuttuvat kokonaan. Tarvitaan sisältöä hakusanoille joita ihmiset oikeasti hakevat — ei lisää "vad är glukosinolater" -tyyppistä. 25 artikkelia = ~1/viikko, realistinen yhdelle kirjoittajalle. |
| **Päivitetyt olemassa olevat artikkelit** | 15 | Nykyiset tieteelliset artikkelit (karotenoidit, solukalvot, nitraatit) tarvitsevat kuluttajalähtöisemmän näkökulman. Ei kirjoiteta uudestaan — lisätään osioita kuten "Mitä tämä tarkoittaa sinulle?" ja "Näin saat tätä ruoasta". |
| **Uudet MLM-artikkelit** | 5 | GSC:n lupaavin data: "direktförsäljning" 79 imp, sijoitus 13,7. MLM-klusteri on ainoa alue jossa on todellista hakuvolyymia ja saavutettavia sijoituksia. 5 uutta = klusteri 8 → 13 sivua. |
| **Tuotesivujen laajennukset** | 3 | Kaksi ohutta tuotesivua (acidophilus-plus 640 sanaa, shake-bar-tea 750 sanaa) + yksi keskeinen tuotesivu (pro-vitality). Laajennus 1000+ sanaan. |
| **Yhteensä** | **48** | ~8/kk, ~2/viikko |

### Mitä EI tehdä

- Ei uusia tuotesivuja — nykyiset 26 riittävät, laajennetaan olemassa olevia
- Ei uusia "Vad är X" -tiedesivuja — nämä eivät tuota liikennettä (data todistaa)
- Ei työkaluja tai laskureita ennen kuin perusliikenne on olemassa

---

## 3. Julkaisutahti

**2 artikkelia / viikko, 8 / kuukausi.**

**Miksi juuri tämä tahti:**

1. **Ylläpidettävä.** Yksi henkilö kirjoittaa, tutkii ja julkaisee. Kaksi artikkelia viikossa tarkoittaa ~4 tuntia per artikkeli — riittävästi laadukkaaseen tutkimuspohjaiseen sisältöön, mutta ei niin paljon että laatu kärsii.

2. **Googlen kannalta riittävä.** Google arvostaa säännöllistä julkaisutahtia — se signaloi että sivusto on aktiivinen. 8 artikkelia kuukaudessa on "aktiivinen" ilman että se on "sisältötehdas".

3. **Indeksoitumisen kannalta optimaalinen.** Liian nopea julkaisutahti (>1/päivä) uudella domainilla voi näyttää spämmiltä. 2/viikko on luonnollinen tahti.

**Milloin poiketaan:** Jos kuukausittainen GSC-data osoittaa, että uudet artikkelit indeksoituvat välittömästi ja tuottavat näyttökertoja, tahtia voi nostaa. Jos vanhatkaan eivät indeksoidu, tahtia lasketaan ja keskitytään indeksointiongelmien ratkaisuun.

---

## 4. GSC-ohjattu työ

### Miten GSC-data vaikuttaa jokaiseen julkaisuun

| GSC-signaali | Toimenpide |
|---|---|
| Hakusana positiossa 5-15, yli 20 imp/kk | **Tarkista ja paranna.** Onko sivu olemassa? Onko otsikko houkutteleva? |
| Hakusana positiossa 1-4, matala CTR | **Korjaa otsikko/metakuvaus välittömästi.** Tämä on matalalla roikkuva hedelmä. |
| Hakusana ei näy datassa, mutta volyymia on | **Uusi artikkeli.** DataForSEO:lla validoidaan volyymi ensin. |
| Sivu indeksoitu mutta yli 90 pv vanha, ei imp | **Päivitä ja paranna.** Sisältö ei vastaa hakukysyntään. |
| Vain 1 imp, sijoitus >50 | **Älä tee mitään.** Yksittäinen näyttökerta satunnaisella haulla ei kerro mitään. |

### Kuukausittainen GSC-rytmi

- **Jokaisen kuun 1. päivä:** Aja `gsc-fetch.py --days 30`. Vertaa edelliseen kuukauteen.
- **Jos uusi hakusana ilmestyy top-20:een:** Priorisoi sen sivun parantaminen seuraavalla viikolla.
- **Jos mikään ei muutu:** Vaihda strategiaa — nykyinen sisältö ei toimi.

---

## 5. Markkinointi

### Missä järjestyksessä, mitä tehdään

**Vaihe 1 (kk 1-2): Google ensin.** Ilman Google-liikennettä mikään muu ei tuota tulosta.

- Varmista indeksointi kaikille ydinsivuille (GSC → Index Coverage)
- Julkaise 8 MLM-artikkelia — ainoa alue jossa on todistettua hakuvolyymia
- Korjaa CTR ongelmasivuilla (tehty: karotenoidit, direktförsäljning)

**Vaihe 2 (kk 3-4): Sisältö + yhteisö.** Kun perusliikenne on olemassa.

- Jaa jokainen uusi artikkeli NeoLife-yhteisössä (Facebook-ryhmät, foorumit)
- Jokainen jaettu artikkeli = yksi mahdollinen takalinkki
- Aloita Pinterest — terveysaiheet toimivat siellä (osta pinni jokaisesta artikkelista)

**Vaihe 3 (kk 5-6): Ulkoiset linkit.** Domain-auktoriteetin rakentaminen.

- Etsi ruotsalaisia terveysblogeja — tarjoa vierasartikkelia
- Listaa sivusto relevantteihin hakemistoihin
- Jaa tutkimuspohjaiset artikkelit LinkedInissä (ammattilaisyleisö)

### Mitä EI tehdä

- Ei maksettua mainontaa (Google Ads) ennen kuin orgaaninen perusta on kunnossa
- Ei some-markkinointia ilman jaettavaa sisältöä
- Ei sähköpostilistaa — ei vielä liikennettä jota kerätä

---

## 6. Mittarit

### Kuukausittainen seuranta

| Mittari | Lähde | Miksi tämä kertoo kasvusta |
|---|---|---|
| **Näyttökerrat** | GSC | Kasvava määrä = Google testaa sivustoa useammilla hakusanoilla |
| **Klikit** | GSC | Ainoa mittari joka kertoo todellisesta kävijäliikenteestä |
| **Keskimääräinen sijoitus** | GSC | Laskeva = sivut nousevat hakutuloksissa |
| **Hakusanojen määrä** | GSC | Kasvava = uusi sisältö indeksoituu ja löytää yleisönsä |
| **Top 3 -hakusanat** | GSC | Mitkä kolme hakusanaa tuottavat eniten näyttöjä — onko trendi nouseva? |
| **Sivuja** | Repo | Julkaistujen sivujen kokonaismäärä |
| **Indeksoidut sivut** | GSC | Kuinka monta sivua Google on indeksoinut (vs. lähetetyt) |

**Mitä ei seurata:** "Sivulla vietetty aika", "bounce rate" — nämä vaativat Analyticsin jota ei ole asennettu, eivätkä kerro kasvusta ennen kuin liikennettä on merkittävästi.

---

## 7. Riskit

| Riski | Todennäköisyys | Varautuminen |
|---|---|---|
| **Google ei indeksoi uusia sivuja** | Keskitaso | Jos 30 pv julkaisun jälkeen uusi sivu ei näy GSC:ssä, pysäytä julkaisutahti ja tutki syy. Mahdollinen syy: tekninen ongelma, manuaalinen toimenpide, liian nopea tahti. |
| **MLM-aiheet eivät tuota liikennettä odotetusti** | Keskitaso | "Direktförsäljning" datan perusteella tämä on todennäköisin reitti liikenteeseen, mutta jos 3kk jälkeen ei edistystä, vaihda fokus ravintosisältöön. |
| **Kirjoittaja ei pysty ylläpitämään 2 artikkeli/viikko -tahtia** | Korkea | Yhden henkilön tuottama 8 artikkelia kuukaudessa on kunnianhimoista. Varatahti: 1/viikko (4/kk). Jos sekään ei onnistu, priorisoidaan MLM-artikkelit ensin. |
| **Google algoritmipäivitys rankaisee sivustoa** | Matala | Matala riski koska sivustolla ei ole mitään manipuloivaa (ei ostettuja linkkejä, ei avainsanaspämmiä, ei AI-sisältöä ilman validointia). |

---

## 8. Ensimmäinen sprintti — 2 viikkoa

### Viikko 1: MLM-klusterin vahvistaminen

| Päivä | Tehtävä | Tuntia |
|---|---|---|
| **Ma** | Tutki "direktförsäljning"-klusterin hakuvolyymit (DataForSEO tai ilmainen vaihtoehto). Listaa 5 uutta MLM-aihetta. | 2 |
| **Ti** | Kirjoita artikkeli #1: "MLM-företag i Sverige — lista och jämförelse" | 4 |
| **Ke** | Julkaise artikkeli #1 (`publish.py`). Päivitä sitemap. Jaa somessa. | 1 |
| **To** | Kirjoita artikkeli #2: "Hur mycket tjänar man på MLM? Verkliga inkomstsiffror" | 4 |
| **Pe** | Julkaise artikkeli #2. GSC-tarkistus: onko "direktförsäljning" noussut? | 1 |

### Viikko 2: Magnesium-klusterin sisäinen linkitys

| Päivä | Tehtävä | Tuntia |
|---|---|---|
| **Ma** | Lisää sisäinen linkitys kaikkiin 10 magnesium-artikkeliin. "Relaterade artiklar" -osio joka sivuun. | 3 |
| **Ti** | Päivitä `magnesium-komplett-guide.html` — lisää kuluttajalähtöinen ingressi. | 2 |
| **Ke** | Kirjoita artikkeli #3: "Magnesium mot värk — vad säger forskningen?" | 4 |
| **To** | Julkaise artikkeli #3. Päivitä magnesium-klusterin sisäiset linkit. | 1 |
| **Pe** | Ensimmäisen sprintin retrospektiivi: julkaistiinko 3 artikkelia? Toimivatko sisäiset linkit? Mitä GSC näyttää? | 2 |

---

## 9. Kuukausittainen voittokysymys

Jokaisen kuukauden lopussa vastataan yhteen kysymykseen datalla:

> **Voitimmeko tässä kuussa?**

Ei tunteella. Ei työmäärällä. Ei julkaisumäärällä.

Vastaus perustuu näihin GSC-mittareihin:

| Mittari | Heinäkuu 2026 (lähtötaso) | Tavoite Tammikuu 2027 |
|---|---|---|
| Näyttökerrat/kk | 154 | 1000+ |
| Klikit/kk | 1 | 50+ |
| Hakusanoja | 136 | 300+ |
| Keskim. sijoitus | 32,2 | <25 |
| Indeksoituja sivuja | ? (tarkistettava GSC:stä) | 158/158 |

Jos kuun lopussa GSC-data näyttää nousua kolmessa viidestä mittarista → **voitimme.** Jos kahdessa tai vähemmän → **emme voittaneet,** ja seuraavan kuun strategiaa muutetaan.
