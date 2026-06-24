# LevNytt sivustoaudiitti — 2026-06-23

> Read-only audit. Ei yhtäkään tiedostomuutosta.
> Luokittelu perustuu sisältöön (title, H1, datePublished-schema),
> ei tiedostonimeen. Audit-skripti: `/home/yampa/.claude/skills/pillar-page-template/scripts/audit_pillar_page.py`.

---

## A. Täysi tiedostoinventaario

Yhteensä: **70 HTML-tiedostoa** (47 juuressa, 18 content/articles/, 5 alikansioissa index.html)

### A1. Juuren .html-tiedostot (47 kpl)

| Tiedosto | Title | Luokka | Huomio |
|---|---|---|---|
| `404.html` | Sidan hittades inte — 404 | SPECIAL | Virheesivu, ei canonical |
| `ala-vs-epa-vs-dha.html` | ALA vs EPA vs DHA — varför kan inte växtomega-3 ersätta fisk? | INFORMATIONAL-ARTICLE | "X vs Y" + datePublished |
| `den-fundersamma-mannen.html` | Den fundersamma mannen – berättelsen bakom LevNytt | PILLAR | Yksi 13:sta. Sisältö: author-profiili |
| `direktforsaljning-fakta.html` | Direktförsäljning vs pyramidspel — den juridiska skillnaden | INFORMATIONAL-ARTICLE | "Vad är X" H1 + datePublished. Sitemap luokittelee PILAARISIVUT (ks. D-kohta) |
| `ekologisk-stadning-greenwashing.html` | Greenwashing i städprodukter — hur känner du igen det? | INFORMATIONAL-ARTICLE | "Hur X" + datePublished |
| `finns-det-billigare-alternativ.html` | Finns det billigare alternativ? | EPÄSELVÄ | Ei canonical, ei datePublished. Sisältö: hintavertailu/jäsenyyslaskelma. Ks. C-kohta |
| `fytosteroler-cellmembran.html` | Vad är fytosteroler? Cellmembran, kolesterol och evidens | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished |
| `golden-home-care.html` | LDC: vad kostar diskmedlet egentligen per liter? | PILLAR | Yksi 13:sta. Canonical on `/golden-home-care/` (trailing slash, ks. D) |
| `index.html` | LevNytt – Vi undersöker. Du jämför. | PILLAR | Etusivu |
| `integritetspolicy.html` | Integritetspolicy | SPECIAL | Ei datePublished |
| `karotenoid-tillskott-vs-mat.html` | Karotenoider från mat eller tillskott — spelar källan roll? | INFORMATIONAL-ARTICLE | "X vs Y" + datePublished |
| `levnytt-se-master-template.html` | SIVUN OTSIKKO \| Levnytt.se | SPECIAL | Kehityspohja placeholder-teksteineen, ei julkinen sivu |
| `magnesiumglycinat-och-somn.html` | Magnesiumglycinat och sömn — vad säger forskningen? | INFORMATIONAL-ARTICLE | EI KOSKETA (eksplisiittinen poikkeus) |
| `multivitamin-kvinnor-over-40.html` | Multivitamin för kvinnor över 40 – vad säger forskningen? | INFORMATIONAL-ARTICLE | EI KOSKETA (eksplisiittinen poikkeus). Nav.js linkittää mutta ei sitemapissa |
| `neolife-acidophilus-plus.html` | NeoLife Acidophilus Plus: 5 miljarder mjölksyrabakterier, fem stammar | INFORMATIONAL-ARTICLE | datePublished löytyy, `@type:Article`, Breadcrumb→`/neolife-acidophilus-plus/`. Canonical trailing slash, ei hakemistoa. Ei sitemapissa. Ks. myös D-kohdan trailing-slash-taulukko |
| `neolife-affarsmojlighet.html` | NeoLife Affärsmöjlighet — Kompensationsplan och ärliga inkomstdata | PILLAR | Yksi 13:sta |
| `neolife-all-c.html` | Vad är C-vitamin — och hur mycket behöver man? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa. Ks. A3 (subdir-duplikaatti) |
| `neolife-betaguard.html` | Vad är antioxidanter — och varför räcker inte ett enda? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-botanical-balance.html` | Vad är adaptogener och växtextrakt — vad säger forskningen? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-carotenoid-complex.html` | Vad är karotenoider – och varför spelar källan roll? | PILLAR | Yksi 13:sta. Title on "Vad är X" + datePublished mutta sitemap: TUOTESIVUT |
| `neolife-chelated-zinc.html` | Vad är zink — och varför spelar chelatformen roll? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-coq10.html` | Vad är CoQ10 — och varför minskar det med åldern? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-cruciferous-plus.html` | Vad är glukosinolater — och varför lyfts korsblommiga grönsaker? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-elevate.html` | NeoLife Elevate — energi och fokus via hjärnkemi | INFORMATIONAL-ARTICLE | datePublished + `@type:Article` + `@type:FAQPage`. Canonical trailing slash `/neolife-elevate/`, ei hakemistoa. Ei sitemapissa. Ks. D |
| `neolife-flavonoid-complex.html` | Vad är flavonoider — och vad gör de i kroppen? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-formula-iv.html` | Vad ska ett multivitamin egentligen innehålla? | INFORMATIONAL-ARTICLE | "Vad ska X" + datePublished. Ei sitemapissa |
| `neolife-garlic-allium-complex.html` | Vad är allicin — och vad säger forskningen om vitlök? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-hallbarhet.html` | NeoLife Hållbarhet: Grönt sedan 1960-talet | PILLAR | Sitemap: PILAARISIVUT. Sisältö: brändin kestävyyspositiointi. datePublished löytyy mutta title ei "Vad är X". Canonical trailing slash. Ks. D |
| `neolife-historia.html` | NeoLifes historia: Från 1958 till global cellulär nutrition | PILLAR | Yksi 13:sta. Läpäisee auditin 13/13 |
| `neolife-kalmag-plus-d.html` | Kalcium, magnesium och D-vitamin — varför kombineras de? | INFORMATIONAL-ARTICLE | "Varför X" + datePublished. Ei sitemapissa |
| `neolife-magnesium-complex.html` | Vad är magnesium — och varför räcker inte kosten för alla? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-omega-3-plus.html` | Vad är EPA och DHA — och varför spelar formen roll? | PILLAR | Yksi 13:sta. Sitemap: TUOTESIVUT |
| `neolife-pro-vitality.html` | Vad är ett dagligt näringssystem — och vad bör det innehålla? | PILLAR | Yksi 13:sta. Sitemap: TUOTESIVUT |
| `neolife-resp-x.html` | Vad stödjer andningsvägars funktion — och vad säger forskningen? | INFORMATIONAL-ARTICLE | "Vad X" + datePublished. Ei sitemapissa |
| `neolife-shake-bar-tea.html` | NeoLife Shake, Bar & Tea: Komplett aktiv livsstil | EPÄSELVÄ | Tuotekeskeinen title, datePublished, canonical trailing slash. Ei sitemapissa. Ks. C |
| `neolife-tre-en-en-cellnaring.html` | Vad är spannmålslipider — och varför spelar de roll för cellerna? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-tre-en-en.html` | NeoLife Tre-en-en: Världens första fytonäringstillskott sedan 1958 | PILLAR | Sitemap: TUOTESIVUT. Tuotekeskeinen title. datePublished löytyy. Ei "Vad är X" rakenteessa. Sisältö: historiallinen tuotekuvaus |
| `neolife-upbeet.html` | Vad är nitrater från rödbeta — och vad säger forskningen? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-vetenskap.html` | NeoLifes Vetenskapliga rådet: Oberoende vetenskap sedan 1976 | PILLAR | Yksi 13:sta. Läpäisee auditin 13/13 |
| `neolife-viktkontroll.html` | NeoLife Viktkontroll: NeoLifeShake, GR2-teknologi och 18g protein | EPÄSELVÄ | Tuotekeskeinen title + kuvausteksti. datePublished löytyy. Sitemap: TUOTESIVUT. H2:t selittäviä mutta product-centric. Ks. C |
| `neolife-vitamin-d.html` | Vad är D-vitamin — och vem riskerar brist i Sverige? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-vitamin-e.html` | Vad är E-vitamin — naturlig vs syntetisk form? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Ei sitemapissa |
| `neolife-vita-squares.html` | Vad behöver barn för daglig näring — och vad saknas ofta? | INFORMATIONAL-ARTICLE | "Vad X" + datePublished. Ei sitemapissa. Ks. A3 (subdir-duplikaatti) |
| `om-oss.html` | Om LevNytt — Kunskapsplattform för välgrundade beslut | PILLAR | Yksi 13:sta |
| `personlig-vard.html` | Nutriance Organic — hudvård baserad på marina växter | EPÄSELVÄ | Tuotekeskeinen title (Nutriance-tuotesivut). datePublished löytyy. Canonical trailing slash. Nav.js linkittää kahdesti (`/personlig-vard/` ja `/personlig-vard.html`). Ei sitemapissa. Ks. C |
| `super-10.html` | Vad är ett koncentrerat rengöringsmedel — och är det ekonomiskt? | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Sitemap TUOTESIVUT (nimiluokitus, ei sisältö) |
| `varfor-fiskolja-inte-ar-likvardigt.html` | Varför fiskolja inte är likvärdigt — triglycerid vs etylester | INFORMATIONAL-ARTICLE | "Varför X" title. Ei datePublished — silti selittäjä-muotoinen. Sitemapissa |
| `vaxtbaserade-steroler-dagligen.html` | 2 g växtsteroler dagligen — varför räcker inte kosten? | INFORMATIONAL-ARTICLE | "Varför X" + datePublished. Sitemapissa |
| `viktuppgang-klimakteriet.html` | Viktkontroll i klimakteriet — hormonella mekanismer och kostansatser | INFORMATIONAL-ARTICLE | Ei datePublished. Title/H2-rakenne selvästi artikkeli. Sitemapissa. Ei "Vad är X" mutta sisältö on puhdas selittäjä |
| `zeaxantin-immunforsvar-2025.html` | Vad är zeaxantin? Forskning om ögon och immunförsvar | INFORMATIONAL-ARTICLE | "Vad är X" + datePublished. Sitemapissa |

---

### A2. content/articles/ -tiedostot (18 kpl)

Kaikki alla mainitut ovat **INFORMATIONAL-ARTICLE** (EI KOSKETA) paitsi kolme eksplisiittiä pilarisivua.

| Tiedosto | Title | Luokka | Sitemapissa? |
|---|---|---|---|
| `ar-dyra-kosttillskott-verkligen-battre.html` | Är dyra kosttillskott verkligen bättre? | INFORMATIONAL-ARTICLE | Kyllä |
| `ar-miljovanliga-rengoringsmedel-lika-effektiva.html` | Är miljövänliga rengöringsmedel lika effektiva? | INFORMATIONAL-ARTICLE | Ei |
| `cellmembran-funktion.html` | Cellmembran funktion – vad gör cellmembranet? | INFORMATIONAL-ARTICLE | Kyllä |
| `c-vitamin-tillskott-vs-serum-huden.html` | C-vitamin tillskott vs serum för huden | INFORMATIONAL-ARTICLE | Ei |
| **`forsknings-faq.html`** | Forsknings-FAQ – Vad betyder vetenskapliga begrepp? | **PILLAR** (yksi 13:sta) | Kyllä (`/forsknings-faq`) |
| `hudtecken-naringsbrist.html` | Hudtecken på näringsbrist | INFORMATIONAL-ARTICLE | Ei |
| **`levnytt-principer.html`** | LevNytt Principer – De fem redaktionella principerna | **PILLAR** (yksi 13:sta) | Kyllä (`/levnytt-principer`) |
| `lutein-zeaxantin-huden.html` | Lutein och zeaxantin för huden | INFORMATIONAL-ARTICLE | Ei |
| `naringsbrist.html` | Näringsbrist – vad det är, varför det uppstår | INFORMATIONAL-ARTICLE | Kyllä |
| `naringsbrist-symptom.html` | Näringsbrist symptom – vanliga tecken | INFORMATIONAL-ARTICLE | Kyllä |
| `nya-kostrad-65-plus-d-vitamin-magnesium.html` | Nya kostråd 65+: D-vitamin, protein och magnesium | INFORMATIONAL-ARTICLE | Kyllä |
| `retinol-pa-sommaren.html` | Retinol på sommaren – myt eller fara? | INFORMATIONAL-ARTICLE | Ei |
| `vad-ar-niacinamid.html` | Vad är niacinamid och vad gör det för huden? | INFORMATIONAL-ARTICLE | Ei |
| `vad-ar-vaxtsteroler.html` | Vad är växtsteroler? | INFORMATIONAL-ARTICLE | Kyllä |
| `varfor-ar-jag-trott-hela-tiden.html` | Varför är jag trött hela tiden? | INFORMATIONAL-ARTICLE | Kyllä |
| `varfor-tar-d-vitamin-slut-pa-ditt-magnesium.html` | Varför tar D-vitamin slut på magnesium? | INFORMATIONAL-ARTICLE | Kyllä |
| **`var-metod.html`** | Vår metod – Hur LevNytt granskar information | **PILLAR** (yksi 13:sta) | Kyllä (`/var-metod`) |
| `vilken-magnesiumform-ar-bast.html` | Vilken magnesiumform är bäst? | INFORMATIONAL-ARTICLE | Kyllä |

---

### A3. Alikansiot: index.html-tiedostot (5 kpl)

Nämä löytyivät `find . -name "index.html" -not -path "./.git/*"` -haulla.

| Polku | Title | Luokka | Vastaava root-.html? | Tilanne |
|---|---|---|---|---|
| `index.html` | LevNytt – Vi undersöker. | PILLAR | — | Etusivu |
| `neolife-kosttillskott/index.html` | NeoLife Kosttillskott — Vetenskapligt baserade produkter | PILLAR | Ei | Yksi 13:sta. Canonical `/neolife-kosttillskott` (clean) |
| `neolife-all-c/index.html` | NeoLife All-C — C-vitamin tuggtablett med Neo-Plex | PILLAR/PRODUCT | **Kyllä** — `neolife-all-c.html` | **KAKSI ERI SIVUA samalla nimellä.** Juuri: "Vad är C-vitamin" (informational). Hakemisto: tuotesivu (All-C-tabletti). Eri sisältö, eri pituus. Ei datePublished subdirissä. Canonical subdirissä: `/neolife-all-c/` |
| `neolife-vita-squares/index.html` | NeoLife Vita-Squares — Lättuggade vitaminer för barn | PILLAR/PRODUCT | **Kyllä** — `neolife-vita-squares.html` | **KAKSI ERI SIVUA samalla nimellä.** Juuri: "Vad behöver barn för daglig näring" (informational). Hakemisto: tuotesivu (Vita-Squares). Eri sisältö. Canonical subdirissä: `/neolife-vita-squares/` |
| `neolife-sustained-vitamin-c/index.html` | NeoLife Sustained Release Vitamin C — Fördröjd frisättning 6–8 timmar | PILLAR/PRODUCT | **Ei** | Vain tämä versio. Ei sitemapissa. Ei nav.js-linkkejä. Canonical: `/neolife-sustained-vitamin-c/` |
| `neolife-fibre-tablets/index.html` | NeoLife Fibre Tablets — Lösliga och olösliga fibrer | PILLAR/PRODUCT | **Ei** | Vain tämä versio. Ei sitemapissa. Ei nav.js-linkkejä. Canonical: `/neolife-fibre-tablets/` |

> **Huomio neolife-all-c ja neolife-vita-squares:** Subdir-versiot ovat tuotesivuja ilman datePublished-schemaa ja niillä on `/tuotenimi/` trailing-slash -kanoninen. Juuriversiot ovat informationaalisia artikkeleita datePublished-schemalla. Nämä ovat tarkoituksella eri sivuja, mutta **kumpikaan version ei tällä hetkellä ole sitemapissa** (juuriversiot eivät ole sitemapissa, subdirversiot eivät myöskään). Tarvitaan päätös siitä, kummalla versiolla on kanoninen URL.

---

## B. 13 nimetyn pilarisivun audit-tulokset

Ajettu: `python3 /home/yampa/.claude/skills/pillar-page-template/scripts/audit_pillar_page.py`

### Referenssipisteet (täydellinen tulos)

```
=== neolife-historia.html ===   → 13/13 PASS (kaikki OK)
=== neolife-vetenskap.html ===  → 13/13 PASS (kaikki OK)
```

### Sivut joissa on FAILeja

```
=== neolife-kosttillskott/index.html ===   → 12/13
  FAIL   at_least_3_breakpoints

=== golden-home-care.html ===              → 13/13 PASS

=== neolife-pro-vitality.html ===          → 12/13
  FAIL   at_least_3_breakpoints

=== neolife-carotenoid-complex.html ===    → 12/13
  FAIL   at_least_3_breakpoints

=== neolife-omega-3-plus.html ===          → 12/13
  FAIL   at_least_3_breakpoints

=== neolife-affarsmojlighet.html ===       → 13/13 PASS

=== om-oss.html ===                        → 11/13
  FAIL   no_inline_root_token_block
  FAIL   at_least_3_breakpoints

=== den-fundersamma-mannen.html ===        → 10/13
  FAIL   links_pillar_css
  FAIL   at_least_3_breakpoints
  FAIL   og_image_present

=== content/articles/var-metod.html ===    → 9/13
  FAIL   links_pillar_css
  FAIL   no_inline_root_token_block
  FAIL   at_least_3_breakpoints
  FAIL   og_image_present

=== content/articles/forsknings-faq.html === → 9/13
  FAIL   links_pillar_css
  FAIL   no_inline_root_token_block
  FAIL   at_least_3_breakpoints
  FAIL   og_image_present

=== content/articles/levnytt-principer.html === → 9/13
  FAIL   links_pillar_css
  FAIL   no_inline_root_token_block
  FAIL   at_least_3_breakpoints
  FAIL   og_image_present
```

### Yhteenveto per tarkistus (13 pilarisivua)

| Tarkistus | Hyväksytään | Hylätään | Hylkäävät sivut |
|---|---|---|---|
| nav_js_with_defer | 13 | 0 | — |
| footer_js_with_defer | 13 | 0 | — |
| no_hardcoded_nav_element | 13 | 0 | — |
| links_pillar_css | 10 | 3 | var-metod, forsknings-faq, levnytt-principer |
| no_inline_root_token_block | 10 | 3 | om-oss, var-metod, forsknings-faq (+ levnytt-principer) |
| playfair_display_loaded | 13 | 0 | — |
| inter_loaded | 13 | 0 | — |
| at_least_3_breakpoints | 6 | 7 | kosttillskott, pro-vitality, carotenoid-complex, omega-3-plus, om-oss, den-fundersamma-mannen, var-metod, forsknings-faq, levnytt-principer |
| img_width100_has_height_auto | 13 | 0 | — |
| canonical_is_clean_slug | 13 | 0 | — |
| og_image_present | 10 | 3 | den-fundersamma-mannen, var-metod, forsknings-faq (+ levnytt-principer) |
| viewport_meta_present | 13 | 0 | — |

> **Prioriteettijärjestys (vakavuuden mukaan):**
> 1. `var-metod` / `forsknings-faq` / `levnytt-principer` — 4 vikaa kukin (puuttuu pillar.css, inline :root-blokki, breakpoints, og:image)
> 2. `den-fundersamma-mannen` — 3 vikaa (puuttuu pillar.css, breakpoints, og:image)
> 3. `om-oss` — 2 vikaa (inline :root-blokki jäljellä, breakpoints)
> 4. `neolife-kosttillskott/index.html`, `neolife-pro-vitality`, `neolife-carotenoid-complex`, `neolife-omega-3-plus` — 1 vika kukin (breakpoints)

---

## C. EPÄSELVÄ-luokan sivut

### C1. `finns-det-billigare-alternativ.html`

**Miksi epäselvä:** Ei canonical-taggia lainkaan. Ei datePublished-schemaa. Title "Finns det billigare alternativ?" ei sovi "Vad är X / X vs Y / Varför X / Hur X" -kaavaan täsmällisesti. Sisältö on hintavertailu/jäsenyyslaskurikone — osittain "Home Care"-tyylinen kustannusanalyysi, osittain myyntipuhetta. Nav.js linkittää `href="/finns-det-billigare-alternativ/"` (trailing slash, ei hakemistoa). Ei sitemapissa.

**Avoin kysymys käyttäjälle:** Onko tämä vanha sivu jota ei enää kehitetä, vai aktiivinen sivu joka pitää yhtenäistää? Canonical puuttuu kokonaan — jos sivu on live, se on SEO-riski.

---

### C2. `neolife-shake-bar-tea.html`

**Miksi epäselvä:** Title "NeoLife Shake, Bar & Tea: Komplett aktiv livsstil" on tuotekeskeinen, ei "Vad är X" -muoto. datePublished löytyy. Canonical `/neolife-shake-bar-tea/` (trailing slash, ei hakemistoa). Ei sitemapissa. Sisältö on todennäköisesti informationaalinen artikkelimuotoinen tuotesivu (kuten acidophilus-plus, elevate).

**Avoin kysymys:** Onko tämä tarkoituksella jätetty sitemapista pois? Jos sivu on live, pitäisikö se lisätä sitemapiin ja korjata canonical trailing-slash-ongelma?

---

### C3. `neolife-viktkontroll.html`

**Miksi epäselvä:** Title "NeoLife Viktkontroll: NeoLifeShake, GR2-teknologi och 18g protein" on selvästi tuotekeskeinen. datePublished löytyy (luokittelu: INFORMATIONAL-ARTICLE). Sitemap merkitsee TUOTESIVUT-kategoriaan. Meta-description sanoo "Detaljerad genomgång" → enemmän informationaalinen. Canonical on `/neolife-viktkontroll` (clean, ei trailing-slashia). Sitemapissa.

**Huomio:** Käytännön kannalta nämä tiedot eivät vaikuta yhtenäistämiseen — sivu on joka tapauksessa in scope ja tarvitsee samat korjaukset.

---

### C4. `personlig-vard.html`

**Miksi epäselvä:** Title "Nutriance Organic — hudvård baserad på marina växter" on tuotekeskeinen (Nutriance-tuotesarjan esittely). datePublished löytyy. Canonical `/personlig-vard/` (trailing slash, ei hakemistoa). Ei sitemapissa. Nav.js linkittää **kahdesti**: `href="/personlig-vard/"` JA `href="/personlig-vard.html"` — duplikoitu nav-linkki eri URL-muodoilla.

**Avoin kysymys:** Nav-duplikaatti on selvä bugi. Kumpi muoto on kanoninen — trailing-slash vai `.html`?

---

### C5. `neolife-all-c/index.html` ja `neolife-vita-squares/index.html`

**Miksi epäselvä:** Katso A3-kohta. Kummallakin on root-tason duplikaatti joka on eri sivu. Cloudflare Pages palvelisi subdir-version osoitteessa `/neolife-all-c/` ja root-version osoitteessa `/neolife-all-c`. Molemmat ovat elossa mutta kumpikaan ei ole sitemapissa.

**Avoin kysymys käyttäjälle:** Onko subdir-versio (tuotesivu ilman nav/footer) vai root-versio (informationaalinen artikkeli) kanoninen? Vai molemmat tarkoituksella? Päätös tarvitaan ennen kuin jompaakumpaa kosketaan.

---

### C6. `neolife-sustained-vitamin-c/index.html` ja `neolife-fibre-tablets/index.html`

**Miksi epäselvä:** Ei sitemapissa. Ei nav.js-linkkejä. Ei root-tason vastinetta. Canonical trailing-slash. Nämä voivat olla joko (a) vanhoja luonnoksia joita ei ole koskaan julkaistu, (b) aktiivisia sivuja joita ei ole vielä lisätty sitemapiin, tai (c) turhia orpo-sivuja.

**Avoin kysymys käyttäjälle:** Kumpaan ne kuuluvat?

---

## D. Muut sivuston laajuiset poikkeamat

### D1. `sitemap.xml` viittaa olemattomaan tiedostoon

Sitemap sisältää:
```
<loc>https://levnytt.se/nutriance-organic</loc>
```
Hakemistossa ei ole `nutriance-organic.html` eikä `nutriance-organic/index.html`. Löytyy vain kuvatiedostoja (`images/nutrianceset.png`, `images/neolife-nutriance.png`). Tämä URL palauttaa todennäköisesti **404**. `personlig-vard.html` sisältää Nutriance-sivun sisällön — onko tämä se "oikea" sivu jota `/nutriance-organic` piti olla?

---

### D2. Root .html -tiedostot joiden canonical on trailing-slash mutta hakemistoa ei ole

Nämä tiedostot ovat root-tasolla `.html`-muodossa, mutta niiden canonical-tagi osoittaa trailing-slash-URL:iin jota ei palvella mistään hakemistosta:

| Tiedosto | Canonical | Hakemistoa? | Sitemapissa? |
|---|---|---|---|
| `golden-home-care.html` | `/golden-home-care/` | Ei | Kyllä (ilman slashia) |
| `neolife-acidophilus-plus.html` | `/neolife-acidophilus-plus/` | Ei | Ei |
| `neolife-elevate.html` | `/neolife-elevate/` | Ei | Ei |
| `neolife-hallbarhet.html` | `/neolife-hallbarhet/` | Ei | Kyllä (ilman slashia) |
| `neolife-shake-bar-tea.html` | `/neolife-shake-bar-tea/` | Ei | Ei |
| `personlig-vard.html` | `/personlig-vard/` | Ei | Ei |

`golden-home-care.html` on erityinen tapaus: sitemap sanoo `/golden-home-care` (ilman slashia), mutta canonical sanoo `/golden-home-care/` (slashilla). Nav.js linkittää `/golden-home-care/`. Kolme eri URL-muotoa samalle sivulle.

`neolife-hallbarhet.html` vastaavasti: sitemap `/neolife-hallbarhet`, canonical `/neolife-hallbarhet/`.

> **Huomio:** Cloudflare Pages saattaa palvella `.html`-tiedostoa molemmissa muodoissa (trailing-slash ja ilman) automaattisten "Pretty URLs" -asetusten kautta. Silti canonical/sitemap-ristiriita on SEO-riski.

---

### D3. Nav.js:ssä duplikoitu `/personlig-vard`-linkki

```javascript
href="/personlig-vard/"      // trailing-slash
href="/personlig-vard.html"  // .html-pääte
```
Kaksi linkkiä samaan sivuun eri muodoissa samassa nav-valikossa.

---

### D4. Nav.js linkittää sivuihin joita ei ole sitemapissa

| Nav-linkki | Tiedosto olemassa? | Sitemapissa? |
|---|---|---|
| `/finns-det-billigare-alternativ/` | Kyllä (root .html) | Ei |
| `/multivitamin-kvinnor-over-40/` | Kyllä (root .html) | Ei |
| `/personlig-vard/` | Kyllä (root .html) | Ei |

---

### D5. Suuri joukko informationaalisia artikkeleita puuttuu sitemapista

Juuren INFORMATIONAL-ARTICLE-tiedostoista nämä **puuttuvat sitemapista** (ei exkluusiolistalla, ei myöskään sitemapissa):

`neolife-acidophilus-plus`, `neolife-all-c`, `neolife-betaguard`, `neolife-botanical-balance`, `neolife-chelated-zinc`, `neolife-coq10`, `neolife-cruciferous-plus`, `neolife-elevate`, `neolife-flavonoid-complex`, `neolife-formula-iv`, `neolife-garlic-allium-complex`, `neolife-kalmag-plus-d`, `neolife-magnesium-complex`, `neolife-resp-x`, `neolife-shake-bar-tea`, `neolife-tre-en-en-cellnaring`, `neolife-upbeet`, `neolife-vitamin-d`, `neolife-vitamin-e`, `neolife-vita-squares`, `personlig-vard`

Lisäksi `content/articles/`:sta puuttuu sitemapista: `ar-miljovanliga-rengoringsmedel-lika-effektiva`, `c-vitamin-tillskott-vs-serum-huden`, `hudtecken-naringsbrist`, `lutein-zeaxantin-huden`, `retinol-pa-sommaren`, `vad-ar-niacinamid`.

> Nämä ovat informointia varten — ei tämän tehtävän scope. Mutta asiaan kannattaa palata sitemappi-päivityssessiossa.

---

### D6. `sitemap.xml` käyttää ei-kanonisia URL-muotoja (trailing-slash-ongelma)

Sitemap listaa sivut ilman trailing-slashia (`/golden-home-care`) mutta ao. tiedostojen canonical on trailing-slash (`/golden-home-care/`). Kaksi poikkeusta: `levnytt.se/` (etusivu) ja `levnytt.se/neolife-kosttillskott` ovat oikein.

---

*Audiitti tehty: 2026-06-23. Tiedostoja tarkistettu: 70. Ei yhtäkään tiedostomuutosta tehty.*
