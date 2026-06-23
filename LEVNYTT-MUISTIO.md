# LevNytt.se — Projektimuistio

Päivitetty: 2026-06-23

---

## Repo ja hosting

- **GitHub repo:** `freefeel-art/levnytt-site`
- **Hosting:** Cloudflare Pages — deployaa automaattisesti git pushin jälkeen (migroitu Netlifystä 20.6.2026)
- **Domain:** levnytt.se
- **Tiedostomuoto:** `.html`-päätteellä, Cloudflare Pages tarjoilee ilman päätettä URLissa (via _redirects)
  - `golden-home-care.html` → `levnytt.se/golden-home-care/`
  - `super-10.html` → `levnytt.se/super-10/`

---

## Paikallinen polku

```
~/levnytt-site/
```

---

## Kansiorakenne

```
~/levnytt-site/
├── index.html
├── golden-home-care.html
├── super-10.html
├── neolife-pro-vitality.html
├── neolife-carotenoid-complex.html
├── neolife-omega-3-plus.html
├── nutriance-organic.html
├── neolife-viktkontroll.html
├── neolife-historia.html
├── neolife-vetenskap.html
├── neolife-hallbarhet.html
├── direktforsaljning-fakta.html
├── neolife-affarsmojlighet.html
├── om-oss.html
├── integritetspolicy.html
└── images/
    ├── Neolife.Super.10.png
    ├── NeolifeAloeveras.png
    ├── NeolifekalmMag.png        (kalcium-magnesium)
    ├── NeolifeShake1.png
    ├── neolife-tea.png
    ├── Neolifetreenen.png
    ├── Neolifeupbeet.png
    ├── omega-3-plus.jpg
    ├── pro-vitality.jpg
    ├── resp-x.jpg
    ├── shake-bar-tea.jpg
    ├── tre-en-en.jpg
    ├── acidophilus-plus.jpg
    ├── betaguard.jpg
    ├── botanical-balance.jpg
    ├── carotenoid-complex.jpg
    ├── chelated-zinc.jpg
    ├── coq10.jpg
    ├── cruciferous-plus.jpg
    ├── elevate.jpg
    ├── flavonoid-complex.jpg
    ├── formula-iv.jpg
    ├── garlic-allium-complex.jpg
    └── magnesium-complex.jpg
```

---

## Git-komennot — uusi tiedosto

```bash
cp ~/Hämtningar/TIEDOSTO.html ~/levnytt-site/TIEDOSTO.html
cd ~/levnytt-site
git add .
git commit -m "Lyhyt kuvaus muutoksesta"
git push
```

---

## Git-komennot — useita tiedostoja kerralla

```bash
cp ~/Hämtningar/golden-home-care.html ~/levnytt-site/
cp ~/Hämtningar/super-10.html ~/levnytt-site/
cd ~/levnytt-site
git add .
git commit -m "Add LDC and Super 10 articles with cross-linking"
git push
```

---

## Git-komennot — kuva images-kansioon

```bash
cp ~/Hämtningar/KUVA.jpg ~/levnytt-site/images/
cd ~/levnytt-site
git add images/KUVA.jpg
git commit -m "Add image: KUVA.jpg"
git push
```

---

## Sponsor-ID ja shoppalinkit

- **Sponsor-ID:** 41-830928
- **Kundshop:** `https://se.neolifeshop.com/i/shop.html?sponsor=41-830928`
- **Distributör:** `https://se.neolifeshop.com/i/registration.html?type=reseller&sponsor=41-830928`

---

## Google & Pinterest verifiointi (lisätään kaikkiin sivuihin `<head>`-tagin ensimmäiselle riville)

```html
<meta name="google-site-verification" content="kAcoLDFGCpGh42gIFRgPeWlC253vTP3OLBs6wI8KDQ0">
<meta name="p:domain_verify" content="6a9e88f7014abe0735767f464c08f337"/>
```

---

## Featured image -nimeämiskäytäntö

Käytetään aina selkeää, avainsanariasta nimeä:
- `ldc-golden-home-care.jpg`
- `super-10-golden-home-care.jpg`
- `pro-vitality-neolife.jpg`

Alt-teksti aina ruotsiksi, kuvaava:
```html
<img src="/images/super-10-golden-home-care.jpg"
     alt="NeoLife Golden Super 10 grovrengöringsmedel koncentrat 1 liter flaska"
     width="800" height="450" loading="lazy">
```

---

## Olemassa olevat kuvat → sopivat sivut

| Kuva | Sopii sivulle |
|------|---------------|
| `Neolife.Super.10.png` | `/super-10/` |
| `pro-vitality.jpg` | `/neolife-pro-vitality/` |
| `carotenoid-complex.jpg` | `/neolife-carotenoid-complex/` |
| `omega-3-plus.jpg` | `/neolife-omega-3-plus/` |
| `tre-en-en.jpg` | `/neolife-tre-en-en/` (tuleva) |
| `formula-iv.jpg` | `/formula-iv/` (tuleva) |
| `elevate.jpg` | `/elevate/` (tuleva) |
| `Neolifeupbeet.png` | `/upbeet/` (tuleva) |
| `NeolifeShake1.png` | `/neolife-viktkontroll/` |
| `shake-bar-tea.jpg` | `/neolife-viktkontroll/` |
| `coq10.jpg` | `/coq10/` (tuleva) |
| `flavonoid-complex.jpg` | `/flavonoid-complex/` (tuleva) |
| `magnesium-complex.jpg` | `/magnesium-complex/` (tuleva) |

---

## Tulevat sivut (puuttuvat pilarit)

- [ ] `/super-10/` ✅ valmis 2026-05-16
- [ ] `/golden-home-care/` ✅ päivitetty 2026-05-16
- [ ] `/neolife-tre-en-en/`
- [ ] `/formula-iv/`
- [ ] `/neolife-carotenoid-complex/`
- [ ] `/elevate/`
- [ ] `/upbeet/`
- [ ] `/coq10/`
- [ ] `/nutriance-organic/` (laajennus)
- [ ] `/neolife-sport/`
