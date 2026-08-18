# CTO:n strateginen katsaus — LevNytt 2026-07-26

**Tyyppi:** Strateginen tulevaisuuskatsaus, ei auditointi
**Edelliset raportit:** AUDIT-REPORT.md (2026-06-23), STRATEGIC-AUDIT-2026-07-26.md
**Identiteetti:** docs/specifications/IDENTITY.md

---

## 1. Nykytila

### Missä LevNytt on nyt?

Projekti on teknisesti **vahvin tila koskaan**. Session aikana:

- 7 kriittistä tuotantobugiä korjattu (_redirects catch-all, rikkinäiset linkit, canonical-ongelma)
- Sprint 22 valmis (Markdown-lähteet suojattu, `source/articles/`)
- Julkaisuputki automatisoitu (`publish.py`, `sync-root-articles.py`)
- 52 orpoa tiedostoa poistettu, yksi 329KB base64-kuva purettu
- `_redirects` auto-ylläpito `md-to-article.py`:ssä
- 16 uutta root-kopiota luotu → sisältö nyt palveltavissa oikeilla URL:illa

Dokumentaatio on ajan tasalla. Arkkitehtuuri on yhtenäinen. Työkalut toimivat.

### Valmiusaste: Tekninen perusta 85%, sisältö 40%

Tekninen infrastruktuuri on lähes valmis. Julkaisu, SEO-perusta, reititys, brändijärjestelmä — kaikki toimii.

Sisältö sen sijaan on vasta alussa. Noin 110 sivua on hyvä alku, mutta "Ruotsin paras NeoLife-tietoalusta" vaatii 200-300 syvällistä, kattavaa artikkelia. Nykyisellä tuotantovauhdilla tähän menee vuosia.

### Suurimmat vahvuudet

1. **Arkkitehtuurin yksinkertaisuus.** Vanilla HTML + Cloudflare Pages. Ei build-askelta, ei palvelinta, ei tietokantaa. Tämä on ikuisesti ylläpidettävä.

2. **Automatisoitu julkaisuputki.** `publish.py` tekee Markdownista tuotantosivun yhdellä komennolla. Tämä on kilpailuetu — uuden sisällön julkaisu on sekunneissa, ei tunneissa.

3. **Dokumentaatiojärjestelmä.** DECISIONS.md, PROJECT-STATUS.md, CURRENT-SPRINT.md, IDENTITY.md. Uusi kehittäjä tai AI-agentti ymmärtää projektin viidessä minuutissa.

4. **FAQPage-schema.** Jokaisessa putken kautta generoidussa artikkelissa on strukturoitu Q&A-data. Tämä on paras mahdollinen GEO-optimointi.

### Suurimmat riskit

1. **Sisällöntuotannon hitaus.** Tekniset työkalut ovat valmiit, mutta sisältöä ei tuoteta riittävällä volyymilla. 200 artikkelin tavoite vaatii systemaattista tuotantoa.

2. **Sisäinen linkitys puuttuu.** Artikkelit ovat irrallisia saaria. Google ja AI-hakukoneet eivät näe aiheklustereita. Tämä heikentää koko sivuston auktoriteettia.

3. **Tuotesivujen laadun vaihtelu.** Osa NeoLife-tuotesivuista on erinomaisia (3000 sanaa), osa ohuita (alle 1000 sanaa). Ohuet sivut eivät rankkaa.

4. **Avainhenkilöriippuvuus.** Tällä hetkellä LevNytt-Hermes kantaa sekä teknisen että strategisen vastuun. Jos omistaja ei pysty tuottamaan sisältöä, projekti pysähtyy.

---

## 2. Tekninen arvio

### Kriittiset ongelmat — EI MITÄÄN

Session jälkeen repositoriossa ei ole kriittisiä teknisiä ongelmia. `_redirects` on korjattu. Canonical-URL:t ovat kunnossa. Rikkinäisiä linkkejä ei ole. Base64-kuvia ei ole (yksi korjattu, kaksi tunnistettu mutta ne ovat olemassa olevia artikkeleita — `retinol-pa-sommaren.html` 222KB ja `vilken-magnesiumform-ar-bast.html` 552KB — eivät uusia ongelmia, korjataan kun artikkeleita päivitetään).

### Suositeltavat parannukset

1. **Sisäinen linkitys klustereittain.** Jokaiseen artikkeliin automaattinen "Relaterade artiklar" -osio. Toteutus: laajenna `md-to-article.py`:tä lisäämään klusterilinkit frontmatterin `cluster`-kentän perusteella. **Vaikutus: suurin yksittäinen SEO-parannus jäljellä.**

2. **FAQPage-schema kaikkiin artikkeleihin.** Kaikki putken kautta generoidut artikkelit saavat FAQ-scheman automaattisesti. Mutta vanhemmissa artikkeleissa (ennen md-to-article.py:tä) sitä ei välttämättä ole. Lisää FAQPage-schema manuaalisesti kirjoitettuihin artikkeleihin. **Vaikutus: suurin yksittäinen GEO-parannus.**

3. **Ohuiden tuotesivujen laajentaminen.** `neolife-acidophilus-plus.html` (640 sanaa) ja `neolife-shake-bar-tea.html` (750 sanaa) tarvitsevat lisää sisältöä. Alle 1000 sanan sivut harvoin rankkaavat hyvin.

### Pienet viimeistelyt

- Korjaa 8 sivulta puuttuva `<h1>` (SEO-perusvaatimus)
- Korjaa 14 sivulta puuttuva `og:image` (somejaot)
- Pura kaksi jäljellä olevaa base64-kuvaa (`retinol-pa-sommaren.html`, `vilken-magnesiumform-ar-bast.html`) kun artikkeleita päivitetään
- Poista `components.js`:n `productMap` kun `product-data.js` on kaikilla sivuilla

### Asiat, joita EI kannata enää koskea

- **Älä migroi frameworkiin.** Vanilla HTML on oikea valinta tälle projektille. Templatointi tulee ajankohtaiseksi vasta 200+ sivun kohdalla.
- **Älä muuta URL-rakennetta.** Nykyiset URL:t toimivat. `/artiklar/`-prefixi uusille sivuille on harkittava, mutta vanhojen siirtäminen on riski ilman hyötyä.
- **Älä automatisoi sitemap-generointia.** Manuaalinen sitemap pakottaa intentionaalisuuden. Validoi sen sijaan.
- **Älä yhdistä artikkeleita jotka palvelevat eri hakuaikeita.** Aiemmin raportoitu 9 kannibalisointiparia — oikeasti vain 2 on aitoja ongelmia. Loput toimivat kuten pitääkin.

---

## 3. Arkkitehtuurin vakaus

### Onko nykyinen arkkitehtuuri riittävän vakaa viidelle vuodelle?

**Kyllä — yhdellä varauksella.**

| Osa-alue | Arvio | Perustelu |
|---|---|---|
| Hakemistorakenne | ✅ Vakaa | `source/` → `content/` → root. Selkeä, yksisuuntainen, automatisoitu. |
| Dokumentaatio | ✅ Erinomainen | 6 ydindokumenttia. Uusi IDENTITY.md. Kaikki ajan tasalla. |
| Julkaisuprosessi | ✅ Automatisoitu | `publish.py`. Yksi komento. Ei enää manuaalisia vaiheita. |
| Skriptit | ✅ Toimivat | Testattu. `publish.py`, `sync-root-articles.py`, `md-to-article.py`. |
| Ylläpidettävyys | ✅ Hyvä | AI-agentti ymmärtää arkkitehtuurin. Dokumentaatio ohjaa. |
| Tekninen velka | ✅ Hallinnassa | Poistettu ~14MB orpoja tiedostoja. Bugit korjattu. Velka vähenee. |

**Ainoa varaus:** 110+ HTML-tiedostoa repositorion juuressa. 200 sivun kohdalla tämä alkaa olla hallinnan rajoilla. Mutta tämä ei ole viiden vuoden ongelma — se on kahden vuoden ongelma. Ratkaisu: `/artiklar/`-prefixi uusille artikkeleille 2027 alkaen. Vanhat säilyvät.

---

## 4. Tuotantosuunnitelma — 12 kuukautta

### Periaate: 80% sisältöä, 20% teknistä ylläpitoa

Tekninen perusta on rakennettu. Nyt sillä pitää tuottaa.

### Kuukaudet 1-3: Sisältöperustan vahvistaminen

**Tavoite:** 20 uutta informaatioartikkelia + FAQPage-schema kaikkiin olemassa oleviin.

- Täytä pahimmat sisältöaukot: B12, CoQ10, E-vitamiini, sinkki — jokaisesta "komplett guide"
- Lisää FAQPage-schema manuaalisesti kirjoitettuihin artikkeleihin (ne jotka eivät tulleet `md-to-article.py`:n kautta)
- Laajenna 2 ohutta tuotesivua (acidophilus-plus, shake-bar-tea)

### Kuukaudet 4-6: Klusterit valmiiksi

**Tavoite:** 30 uutta artikkelia + sisäinen linkitys käyttöön.

- Täydennä jokainen aiheklusteri (magnesium, D-vitamiini, omega-3, probiootit, kuidut, monivitamiinit) vähintään 6-8 artikkeliin
- Ota käyttöön automaattinen klusterilinkitys `publish.py`:ssä
- Ensimmäinen "täysi klusteri" valmiina: magnesium (10 artikkelia + sisäiset linkit)

### Kuukaudet 7-9: Syventäminen ja työkalut

**Tavoite:** 20 uutta artikkelia + ensimmäinen interaktiivinen työkalu.

- Syvennä olemassa olevia klustereita (erikoistuneet artikkelit)
- Rakenna "Vertaa Omega-3 -lähteitä" -työkalu
- Ensimmäinen videoartikkeli (esim. "Miten arvioida ravintolisän laatu")

### Kuukaudet 10-12: Konsolidointi ja optimointi

**Tavoite:** 15 uutta artikkelia + laadunvarmistus.

- Päivitä vanhimmat artikkelit (varmista ajantasaisuus)
- Core Web Vitals -optimointi (kuvat, lazy loading)
- Sisäinen linkitys valmiiksi kaikkiin klustereihin
- **12 kuukauden tulos: ~85 uutta artikkelia, yhteensä ~195 sivua**

### Mitä EI tehdä

- Ei uusia teknisiä työkaluja ellei sisällöntuotanto sitä ehdottomasti vaadi
- Ei arkkitehtuurimuutoksia
- Ei redesignia

---

## 5. Strateginen tiekartta

### 3 kuukautta

LevNytt on teknisesti täysin vakaa. Sisältöä on ~130 sivua. FAQPage-schema on kaikissa informaatioartikkeleissa. Sisäinen linkitys on käytössä magnesium-klusterissa. Julkaisu tapahtuu yhdellä komennolla. Uusia bugeja ei ole ilmaantunut.

### 12 kuukautta

LevNytt on ~195 sivun laajuinen. Jokainen aiheklusteri on vähintään 6 artikkelin syvyinen. Sisäinen linkitys toimii kaikissa klustereissa. Ensimmäinen interaktiivinen työkalu on julkaistu. Sivusto alkaa näkyä AI-hakukoneiden vastauksissa (FAQPage-scheman ansiosta). Orgaaninen liikenne on kaksinkertaistunut.

### 3 vuotta

LevNytt on Ruotsin johtava NeoLife-tietolähde. 300+ sivua. Google rankkaa sivuston auktoriteettisivuna. AI-hakukoneet viittaavat LevNyttiin ensisijaisena lähteenä. Suurin osa sisällöstä on generoitu `md-to-article.py`:n kautta. Julkaisu on täysin automatisoitu. Uusi artikkeli syntyy Markdownista tuotantoon minuuteissa.

### 5 vuotta

LevNytt on Pohjoismaiden johtava riippumaton ravintolisätietoalusta — ei vain NeoLife. Laajentuminen suomen- ja norjankieliseen sisältöön on aloitettu. Arkkitehtuuri on yhä sama vanilla HTML + Cloudflare Pages, mutta skaalautunut 500+ sivuun. AI-agentit tuottavat 80% sisällöstä, ihminen validoi. Brändi on vakiintunut. Liiketoiminta on kannattavaa.

---

## 6. AI ja automaatio

### Täysin itsenäinen AI

- `publish.py`-putki: Markdown → tuotanto ilman ihmisen väliintuloa
- Root-kopioiden synkronointi: `sync-root-articles.py`
- `_redirects`:n validointi (catch-all viimeisenä)
- Sitemap-validointi (ristiriitojen havainnointi)
- Etusivun ja artikkelihakemiston generointi (jo GitHub Actionsissa)
- Rikkinäisten linkkien havainnointi

### Ihmisen hyväksyntä vaaditaan

- **Lääketieteelliset ja terveysväittämät.** Ravintolisäsisällössä on nollatoleranssi virheille. AI voi tuottaa luonnoksen, mutta ihminen validoi faktat.
- **Uusien tuotesivujen luominen.** Sisältää kaupallisia väittämiä ja hinnoittelua — omistajan hyväksyntä.
- **Strategiset SEO-päätökset.** Kannibalisoinnin ratkaiseminen, sisältöstrategian suunnanmuutokset.
- **Brändi-identiteettiin vaikuttavat muutokset.** Uudet sivutyypit, uudet design-elementit.

### Optimaalinen työnjako

| Vastuu | LevNytt-Hermes | Omistaja |
|---|---|---|
| Tekninen ylläpito | 100% | 0% |
| Julkaisuautomaatio | 100% | 0% |
| Bugien korjaus | 100% | 0% |
| Dokumentaatio | 100% | 0% |
| Sisällön generointi (Markdown → HTML) | 100% | 0% |
| Sisällön kirjoittaminen (tutkimus, teksti) | 30% (luonnos) | 70% (validointi, viimeistely) |
| SEO-strategia | 40% (analyysi, suositukset) | 60% (päätökset) |
| Tuotestrategia | 20% (data, analyysi) | 80% (päätökset) |
| Brändi | 10% (tekninen toteutus) | 90% (luova suunta) |

---

## 7. Liiketoimintanäkökulma

### Tukeeko nykyinen rakenne pitkän aikavälin kasvua?

**Kyllä.** Vanilla HTML + Cloudflare Pages on äärimmäisen kustannustehokas. Ei palvelinkuluja, ei tietokantakuluja, ei kehittäjäriippuvuutta. Ainoa kustannus on domain ja sisällöntuotanto. Tämä skaalautuu 50 sivusta 500 sivuun ilman kustannusten kasvua.

### Puuttuuko jotain, joka vaikeuttaa tulevaa laajentumista?

**Kansainvälistymisen tuki puuttuu.** Jos LevNytt laajenee suomeksi tai norjaksi, nykyinen arkkitehtuuri ei tue monikielisyyttä suoraan. Tämä ei ole akuutti ongelma, mutta se on huomioitava 3-5 vuoden tähtäimellä.

**Analytiikan puute.** Ei kävijäseurantaa, ei klikkausdataa, ei konversioseurantaa repositoriossa. Sisältöpäätökset perustuvat oletuksiin, eivät dataan. Google Analytics tai vastaava olisi hyödyllinen.

### Missä vaiheessa tekninen kehitys kannattaa lopettaa?

**Nyt.** Tekninen perusta on 85% valmis. Jäljellä oleva 15% (template-järjestelmä, kuvien optimointi, GEO-schema-laajennukset) voidaan tehdä ylläpitotyönä sisällöntuotannon rinnalla. Ensisijainen fokus pitää siirtää sisältöön.

Poikkeus: jos uusi sisältötyyppi (esim. interaktiivinen työkalu) vaatii teknistä kehitystä, se tehdään. Mutta "rakennetaan lisää työkaluja" ei ole strategia. "Tuotetaan lisää sisältöä" on.

---

## 8. Haasta aikaisemmat johtopäätöksesi

### Mitkä suositukset olivat oikeita?

1. **`_redirects` catch-all -korjaus.** Tämä oli kriittinen. 7 sivua palasi tuotantoon.
2. **Sprint 22.** Markdown-lähteiden suojaaminen oli oikea prioriteetti.
3. **`publish.py`.** Yhden komennon julkaisuputki poistaa 4 manuaalista vaihetta.
4. **`sync-root-articles.py`.** Root-kopioiden automatisointi eliminoi suurimman manuaalisen ylläpitotaakan.
5. **FAQPage-scheman tunnistaminen GEO-vahvuudeksi.** Tämä oli oikea havainto — se on alihyödynnetty kilpailuetu.

### Mitkä olivat liian kunnianhimoisia?

1. **"Yhdistä 9 kannibalisoivaa artikkeliparia."** Oikeasti vain 2 paria tarvitsee yhdistämistä. Loput palvelevat eri hakuaikeita ja toimivat oikein. Liian aggressiivinen suositus.
2. **"Sitemap-automaatio."** Väärä ratkaisu oikeaan ongelmaan. Validointi on parempi.
3. **"Templatointi."** Oikea ratkaisu, mutta väärä ajoitus. Ajankohtainen vasta 200+ sivun kohdalla.

### Mitkä olivat virheellisiä?

1. **"85% umpikujasivuja on suurin SEO-ongelma."** Väärin. Informaatioartikkelit ovat vastaussivuja — bounce rate on normaali. Sisäinen linkitys on hyödyllinen, ei kriittinen.
2. **"Footerin linkit `var-metod` ja `forsknings-faq` ovat rikki."** Väärin. Ne toimivat `_redirects`:n kautta. Analyysi ei huomioinut rewrite-sääntöjä.

### Mitä en enää suosittelisi?

1. **Sitemap-generaattoria.** Manuaalinen sitemap pakottaa intentionaalisuuden. Validointi on parempi.
2. **Artikkelien yhdistämistä ilman hakuaikeiden erittelyä.** Vain todelliset kannibalisointitapaukset (identtinen H1, identtinen hakuaie) kannattaa yhdistää.
3. **Uusien työkalujen rakentamista ennen sisällön tuottamista.** Työkalut ovat hyviä, mutta sisältö on tärkeämpää juuri nyt.

---

## 9. CTO:n kolme päätöstä

Jos saisin tehdä vain kolme päätöstä LevNyttin tulevaisuudesta:

### 1. Siirrä fokus sisällöntuotantoon. Nyt.

**Perustelu:** Tekninen perusta on 85% valmis. Julkaisuputki toimii. SEO-perusta on kunnossa. Jokainen uusi tekninen työkalu tuottaa vähenevää marginaalihyötyä. Jokainen uusi laadukas artikkeli tuottaa kasvavaa marginaalihyötyä (enemmän hakusanoja, enemmän auktoriteettia, enemmän sisäisiä linkkejä). Seuraavat 12 kuukautta: 80% sisältöä, 20% teknistä ylläpitoa.

### 2. Lisää FAQPage-schema jokaiseen informaatioartikkeliin.

**Perustelu:** Tämä on suurin yksittäinen GEO-parannus, joka voidaan tehdä olemassa olevaan sisältöön. FAQPage-schema on suoraa syötettä AI-hakukoneille (ChatGPT, Claude, Gemini, Perplexity). Jokainen Q&A-pari on täydellinen RAG-chunk. Tämä on kilpailuetu, jota harvalla ruotsinkielisellä sivustolla on. Kustannus: yksi läpikäynti olemassa oleviin artikkeleihin.

### 3. Ota käyttöön automaattinen klusterilinkitys.

**Perustelu:** Sisäinen linkitys on suurin jäljellä oleva SEO-parannus. Kun jokainen artikkeli linkkaa saman klusterin muihin artikkeleihin, Google ja AI näkevät aihekokonaisuudet. Tämä nostaa koko klusterin auktoriteettia, ei vain yksittäisten sivujen. Toteutus: laajenna `publish.py`:tä. Kustannus: yksi iltapäivä.

---

## 10. Hallituksen yhteenveto

### Missä olemme nyt?

LevNytt on teknisesti vakaa, hyvin dokumentoitu, automatisoitu NeoLife-tietoalusta. 110+ sivua. Toimiva julkaisuputki. Ei kriittisiä bugeja. Arkkitehtuuri on yksinkertainen ja ylläpidettävä — vanilla HTML, Cloudflare Pages, ei palvelinkuluja.

### Minne olemme menossa?

Ruotsin johtavaksi riippumattomaksi NeoLife-tietoalustaksi. 12 kuukauden tavoite: ~195 sivua, täydet aiheklusterit, sisäinen linkitys, FAQPage-schema kaikissa artikkeleissa. 3 vuoden tavoite: 300+ sivua, AI-hakukoneiden ensisijainen lähde. 5 vuoden tavoite: Pohjoismainen laajentuminen.

### Mitä teemme seuraavaksi?

Lopetamme teknisten työkalujen rakentamisen ja siirrymme sisällöntuotantoon. 80% resursseista sisältöön, 20% ylläpitoon. Seuraavat 3 kuukautta: 20 uutta informaatioartikkelia, FAQPage-schema olemassa oleviin, sisäinen linkitys käyttöön. Kaikki uusi sisältö julkaistaan `publish.py`:llä — yksi komento, ei manuaalisia vaiheita.

### Miksi uskon tämän onnistuvan?

1. Tekninen perusta on valmis. Ei enää teknisiä esteitä skaalautumiselle.
2. FAQPage-schema on todellinen kilpailuetu — harva kilpailija käyttää sitä systemaattisesti.
3. Vanilla HTML -arkkitehtuuri on äärimmäisen kustannustehokas — skaalautuu ilman lisäkustannuksia.
4. AI-agentti (LevNytt-Hermes) hoitaa teknisen ylläpidon itsenäisesti — omistaja voi keskittyä sisältöön.

### Mitä riskejä hallituksen tulee tiedostaa?

1. **Sisällöntuotannon hitaus.** Jos sisältöä ei tuoteta suunnitellulla volyymilla, kasvu pysähtyy. Työkalut eivät tuota sisältöä — ihmiset tuottavat.
2. **Googlen algoritmimuutokset.** Hakukoneoptimointi on liikkuva maali. Mikään tekninen ratkaisu ei takaa sijoituksia ikuisesti.
3. **Avainhenkilöriippuvuus.** Projekti on tällä hetkellä riippuvainen yhdestä henkilöstä sekä sisällön että strategian osalta. Tämä on pitkän aikavälin riski.
4. **Kilpailu.** NeoLife ei ole ainoa ravintolisäbrändi. Jos kilpailijat tuottavat parempaa sisältöä, LevNytt menettää asemansa riippumatta teknisestä laadusta.
