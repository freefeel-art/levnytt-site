# Editorial Plan: Kosttillskott för äldre 65+

**Plan ID**: EP-20260701-001
**Source**: Approved Research Brief RC-20260701-001
**Skapad**: 2026-07-01T12:10:00Z
**Författare**: Editorial Commander (pipeline mode)
**Konsumerad av**: LevNytt Writer

---

## 1. UPPDRAG

Skriv en komplett guide: "Kosttillskott för äldre 65+ — vad behöver du veta?"

**Målgrupp**: Personer 65–80 år och deras anhöriga. Primärt de som börjar fundera på om kosten räcker till.
**Tone**: Saklig, trygg, myndighetsförankrad. Inget dystert eller alarmistiskt. Normal svensk sakprosa.
**Format**: Portalliknande guide — täcker flera näringsämnen i en artikel, länkar vidare till djupdykningar.
**Längd**: 2000–3000 ord (inkl rubriker).
**Slug**: `kosttillskott-aldre-65`

---

## 2. STRUKTUR (obligatorisk)

1. **Ingress** — Varför behoven ändras efter 65. Livsmedelsverket har 2026 för första gången gett specifika råd för 65+.
2. **Livsmedelsverkets nya råd** — Nyhetskrok. D-vitamin 20 µg från 75 år, protein 1,2 g/kg, tio åtgärder mot undernäring.
3. **Protein — bygga och bevara muskelmassa** — Sarkopeni. När maten inte räcker. Golden Home Care som näringstillskott (15 g protein/portion).
4. **D-vitamin — mer än dubbelt så mycket** — Skillnad 10 vs 20 µg. Över 90% av äldre i Europa får för lite via kosten.
5. **B12 — därför är brist så vanlig** — Atrofisk gastrit, PPI-läkemedel (omeprazol). Sublingualt eller injektion ofta bättre.
6. **Kalcium och magnesium — ben och muskler** — Kalcium 1000 mg/dag. Cal-Mag-Zinc (tuggtablett för äldre). D-vitamin + kalcium minskar frakturrisk.
7. **Omega-3 — hjärta och kognition** — Antiinflammatoriskt. Kan bidra till kognitiv funktion. Omega-3 Plus.
8. **Multivitamin som basförsäkring** — Små brister som inte märks. Pro Vitality med CoQ10 och ALA.
9. **Läkemedel och kosttillskott — viktiga interaktioner** — PPI-B12, statiner-CoQ10, diuretika-magnesium.
10. **När maten inte räcker till** — Minskad aptit, tugg- och sväljsvårigheter. Flytande näring. Golden Home Care som proteinkälla + måltidsersättning.
11. **Praktisk daglig rutin** — Frukost/middag/kväll. Tabletter vs pulver vs flytande.
12. **Sammanfattning** — Börja med basen (D-vitamin + protein), bygg därifrån.

---

## 3. NYCKELPÅSTÅENDEN (måste inkluderas med källa)

| Påstående | Källa |
|---|---|
| "Livsmedelsverket rekommenderar 20 µg D-vitamin/dag för alla över 75 år, att jämföra med 10 µg för yngre vuxna." | Livsmedelsverket L 2026 nr 07 |
| "Proteinbehovet för äldre är minst 1,2 gram per kilo kroppsvikt och dag." | Livsmedelsverket + EFSA DRV |
| "Multivitamin har i en stor studie med 13 600 deltagare visats förbättra minnet hos äldre." | Xu et al., Food Science and Human Wellness, 2024 |
| "Vitamin D, omega-3 och probiotika är de tillskott som troligen har mest stöd för kognitiv hälsa hos äldre." | PMC systematic review, 2024 |
| "B12-brist drabbar uppskattningsvis 10–30% av alla över 65 år, främst på grund av nedsatt upptag i magen." | FSAI, 2021 |
| "Kalcium (1000 mg/dag) tillsammans med D-vitamin kan minska risken för frakturer." | EFSA, Dorrington 2020 |
| "54% av personer över 60 år i västvärlden tar någon form av multivitamin eller mineraltillskott." | Innova Market Insights, 2026 |

---

## 4. PRODUKTNÄMNANDEN (ska kännas naturliga, inte som katalog)

Produkterna ska presenteras som *svar på problem*, inte som produktrekommendationer:

| Problem → Lösning | Produkt | I vilket stycke |
|---|---|---|
| Minskat proteinintag + nedsatt aptit → proteinshake | Golden Home Care | Protein + "När maten inte räcker" |
| Behov av brett mineral/vitaminstöd → multivitamin | Pro Vitality | Multivitamin som basförsäkring |
| Tuggproblem → tuggtablett mineraler | Cal-Mag-Zinc | Kalcium och magnesium |
| Antiinflammation + kognition → omega-3 | Omega-3 Plus | Omega-3 |

**Regel**: Nämn endast produkter där specifik lösning krävs. Ingen produktlista i slutet.

---

## 5. INTERNA LÄNKAR (obligatoriska)

- `/d-vitamin-allt-du-behover-veta` — i D-vitamin-stycket
- `/nya-kostrad-65-plus-d-vitamin-magnesium` — i Livsmedelsverket-stycket
- `/magnesium-d-vitamin-kombination` — i magnesium-stycket
- `/omega-3-komplett-evidensbaserad-guide` — i omega-3-stycket
- `/nar-ska-man-ta-kosttillskott-timingguide` — i praktisk rutin
- `/behoever-jag-kosttillskott` — i ingressen eller multivitamin-stycket

---

## 6. YMYL-VARNINGAR (får INTE göras)

- Inga medicinska påståenden: säg inte "förebygger Alzheimers", "botar benskörhet", "förhindrar hjärtinfarkt"
- Använd: "kan bidra till", "stödjer", "forskning visar samband mellan..."
- Evidensen för sköra äldre är låg — nämn detta nyanserat
- Inga överdrifter om effektstorlekar
- Tala om när maten räcker — kosttillskott är komplement, inte ersättning

---

## 7. FORMATKRAV

- Svensk standard-sakprosa (ingen markdown i HTML — standard HTML-struktur)
- `<h2>` för huvudrubriker, `<h3>` för underrubriker
- `<p>` för brödtext
- `<ul>` / `<ol>` för listor (använd sparsamt)
- `<a href="...">` för interna länkar
- `<strong>` för nyckelbegrepp
- `<blockquote>` för citat ur Livsmedelsverket eller forskning
- `<table>` för jämförelser (om lämpligt)
- Microdata/JSON-LD: Article-schema, FAQPage-schema (för FAQ-stycket om det finns)

---

## 8. GODKÄNDA KÄLLOR (använd endast dessa — inget nytt Research)

1. Livsmedelsverket L 2026 nr 07 — Kostråd för vuxna över 65 år
2. Xu et al. 2024 — Multivitamin and memory systematic review
3. PMC systematic review 2024 — Vitamin D, probiotics, PUFAs and cognition
4. BMC Geriatrics 2024 — Exercise + nutrition reduces frailty
5. Dorrington N. 2020 — Review of nutritional requirements for adults ≥65
6. FSAI 2021 — Dietary guidelines for older adults in Ireland
7. EFSA DRV for calcium, vitamin D, protein
8. BMC Nutrition 2025 — Oral nutrition supplements in elderly
9. Paraskevas et al. 2025 — Micronutrient supplementation in frail elderly (låg evidens)
10. Innova Market Insights 2026 — Senior nutrition trends
11. Proceedings of Nutrition Society 2019 — Vitamin D insufficiency in Europe
12. Berg et al. 2025 — B vitamins and cognition systematic review

---

## 9. LEVERANS

- Skapa fil: `kosttillskott-aldre-65` (HTML-fil i repository-root)
- Efter färdig artikel: meddela för vidarebefordran till Publication Agent
- Publicera INTE själv — Publication Agent gör det
