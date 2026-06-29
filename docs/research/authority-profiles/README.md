# Authority Profiles Library

This directory contains reusable, evidence-based evaluations of influential people, organizations, and institutions relevant to LevNytt.

## Purpose

Authority Profiles are **not biographies** and **not hero pages**. They are internal research tools designed to:

- Separate documented facts from opinion and philosophy.
- Surface conflicts of interest and potential bias.
- Provide historical context for authority articles.
- Prevent redundant background research across multiple articles.
- Improve fact-checking and source evaluation.

## Who this is for

- Researchers running the Authority Research Skill.
- Writers creating authority articles.
- Editors verifying claims and source quality.

## Design principles

| Principle | Meaning |
|---|---|
| **Evidence-based** | Profiles are built from sources, not admiration or dislike. |
| **Neutral** | No promotional or defensive framing. |
| **Transparent** | Conflicts of interest and limitations are stated explicitly. |
| **Reusable** | Profiles are referenced, not duplicated, in research reports. |
| **Not hero pages** | Influence is documented; endorsement is not implied. |

## Profile categories

| Category | Folder prefix | Purpose |
|---|---|---|
| Regulatory & Scientific Authorities | `regulatory-` | Government, regulatory, and scientific bodies |
| Business Philosophy | `business-` | Long-term thinking, value creation, decision quality |
| Leadership | `leadership-` | Leadership, personal development, communication |
| Direct Selling History | `direct-selling-` | Historical development of direct selling |
| Network Marketing Education | `network-marketing-` | Professional education and sales systems |

## File naming

```
<category-prefix>-<authority-slug>.md
```

Examples:

```
regulatory-ftc.md
business-warren-buffett.md
leadership-jim-rohn.md
direct-selling-carl-rehnborg.md
network-marketing-eric-worre.md
```

## Profile structure

Every profile follows the same structure. See `_template.md`.

## Relationship to other systems

```
Authority Profiles
        ↓
Authority Research reports
        ↓
Question Gap backlog
        ↓
Informational / Authority Articles
```

Authority Research reports reference profiles instead of repeating background information. The profile's Reliability Assessment and Conflicts of Interest should influence how the authority is used in articles.

## Usage rules

1. **Do not treat profiled individuals as scientific or regulatory evidence unless their category supports it.** A business philosopher's opinion is not peer-reviewed science.
2. **Always cite the primary source, not the profile, in published articles.** Profiles are internal tools.
3. **Update profiles when new evidence emerges.** Add a changelog entry at the bottom of the profile.
4. **Create placeholders for authorities encountered repeatedly.** A placeholder is better than no profile.
5. **Community opinions about an authority are not evidence.** They may be noted as signals of perception, but not as factual assessments.

## Current profiles

### Regulatory & Scientific Authorities

- [FTC](regulatory-ftc.md)
- [EFSA](regulatory-efsa.md)
- [PubMed](regulatory-pubmed.md)
- [Konsumentverket](regulatory-konsumentverket.md)
- [WFDSA](regulatory-wfdsa.md)

### Business Philosophy

- [Warren Buffett](business-warren-buffett.md)
- [Charlie Munger](business-charlie-munger.md)
- [Richard Branson](business-richard-branson.md)
- [Peter Drucker](business-peter-drucker.md)

### Leadership

- [Jim Rohn](leadership-jim-rohn.md)
- [John C. Maxwell](leadership-john-c-maxwell.md)
- [Stephen Covey](leadership-stephen-covey.md)

### Direct Selling History

- [Carl Rehnborg](direct-selling-carl-rehnborg.md)
- [Jay Van Andel](direct-selling-jay-van-andel.md)
- [Rich DeVos](direct-selling-rich-devos.md)
- [Jerry Brassfield](direct-selling-jerry-brassfield.md)

### Network Marketing Education

- [Eric Worre](network-marketing-eric-worre.md)
- [Richard Bliss Brooke](network-marketing-richard-bliss-brooke.md)

## Template

Start every new profile from `_template.md`.
