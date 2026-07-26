# GitHub Profile Presentation Strategy

This document records the public-profile patterns reviewed on July 26, 2026 and the decisions used to adapt them to Jerry R. Napier’s GitHub presence. It is a maintenance record, not customer-facing copy and not a software license.

## Objectives

- Help recruiters and collaborators understand the work within one short scan.
- Lead with verified outcomes rather than decorative statistics.
- Use a number only when Jerry can explain what was counted, where it came from, why it matters, and what limitation applies.
- Hold every public project—not only the profile headline—to the same source, scope, relevance, limitation, and plain-language standard.
- Keep the profile recognizably personal without copying another creator’s design or wording.
- Preserve stable project identities, exact release claims, accessibility, and low-maintenance reliability.
- Use GitHub’s native profile README and six-item pin surface before introducing external widgets.

## Benchmark index

| Reference | Useful pattern | Decision | Organic adaptation |
|---|---|---|---|
| [GitHub profile README guidance](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme) | The profile README should quickly explain who the account owner is and what they do. | Adopt | Keep a plain-language professional opening and direct Portfolio/LinkedIn paths. |
| [GitHub profile pinning guidance](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile) | Up to six pins provide the fastest native route to the strongest work. | Adopt | Maintain a six-project recruiter sequence spanning operations, governance, media, analytics, supervision, and product work. |
| [Cassidy Williams](https://github.com/cassidoo) | Conversational voice and a curated “things I made” list make a large body of work approachable. | Adopt selectively | Retain a human voice and curated project tiers without casual filler or a long undifferentiated catalog. |
| [Sarah Drasner](https://github.com/sdras) | Career authority and domain scope appear immediately, with little visual overhead. | Adopt | Keep credentials and professional domains near the top, then support them with project evidence. |
| [Anurag Hazra](https://github.com/anuraghazra) | A visual hero, quantified reach, and highlighted repositories make the page highly scannable. | Adopt the proof pattern only | Use a small number of traceable proof points with definitions and relevance; do not add external stat cards, traffic counters, or decorative technology icon rows. |
| [Simon Willison](https://github.com/simonw) | A current-focus statement and automatically refreshed work streams signal active practice. | Adopt the focus statement; defer automation | Add a stable current-focus line. Do not add a dynamic feed until there is a reliable, bounded source and a clear recruiter benefit. |
| [Sindre Sorhus](https://github.com/sindresorhus) | A distinctive personal visual identity is memorable. | Do not imitate | Preserve personality through clear language and project choices rather than retro graphics, animation, or borrowed visual motifs. |
| [Awesome GitHub Profile README](https://github.com/abhisheknaiidu/awesome-github-profile-readme) | The broader ecosystem includes dynamic feeds, badges, GIFs, stats cards, and highly visual layouts. | Use as a pattern catalog, not a template | Prefer minimal, native, accessible presentation; add a feature only when it communicates verified professional evidence. |

## Organic implementation

The profile applies the benchmark findings through five restrained changes:

1. **Current focus** — one sentence explains the unifying direction across information governance, analytics, and local automation.
2. **Selected evidence, with context** — three public figures show analytical scope, product scope, and portfolio governance. Every row defines the unit and explains why the figure matters.
3. **Curated review path** — flagship work, the delivery framework, supporting projects, and hiring guidance remain visibly separated.
4. **Hiring-team guidance** — a short section explains how to review the portfolio by role without repeating repository links or adding internal process language.
5. **Project-by-project speaking guide** — every public repository has one explainable core claim, public evidence sources, an interview-ready description, and an explicit limitation in [`PUBLIC_CLAIMS.md`](PUBLIC_CLAIMS.md).

The implementation deliberately avoids:

- dynamic third-party stat cards, visitor counters, trophies, or language-ranking widgets;
- animated banners, copied artwork, or decorative technology icon walls;
- unverifiable popularity claims, synthetic activity, or release inflation;
- private operating totals presented as publicly verifiable evidence;
- configuration limits, fixture results, historical records, or content counts presented as measured business performance;
- duplicated repository links that weaken the existing one-link-per-project profile contract;
- automated feeds that can go stale, break externally, or overshadow the work itself.

## Evidence policy

A figure belongs on the profile only when all five conditions are met:

1. **Public source** — a reviewer can trace it to a public repository, manifest, dataset, or test.
2. **Defined unit and scope** — the profile states what was counted, over what period or boundary, and what the figure does not represent.
3. **Professional relevance** — the number demonstrates analytical scale, product scope, governance, reliability, or another role-relevant capability.
4. **Documented limitation** — the source explains the main caveat so the figure is not mistaken for a broader claim.
5. **Plain-language explanation** — Jerry can explain the figure and its significance in about 30 seconds without relying on the README wording.

Numbers are not included merely because quantified profiles are fashionable. One defensible figure is stronger than several unexplained ones.

Private MediaTagger library and outcome totals were removed from the profile and the project README because the operating records are not public. The private workflow may still inform design decisions, but the public claim is limited to safeguards that can be reviewed in source and tests.

The detailed Reliable Project Delivery Framework scorecard remains in its case study, where the validation categories, historical-package boundary, and non-rerun limitation are explained. It is not used as an isolated headline metric on the profile.

## All-project claims standard

The same scrutiny applies below the profile headline. [`.github/public-claims.json`](.github/public-claims.json) is the machine-readable authority for all 18 public repositories, including the profile repository. [`PUBLIC_CLAIMS.md`](PUBLIC_CLAIMS.md) provides the corresponding human speaking guide.

Every repository record must include:

- one core public claim;
- a plain-language talk track;
- public evidence sources or a clearly labeled historical record;
- at least one limitation;
- README markers that support the claim and retire unsupported wording; and
- a classification for every important number.

Quantitative claims are separated into public-dataset measures, synthetic fixtures, content scope, configuration limits, authorization invariants, protocol constraints, historical records, market scope, and portfolio inventory. A five-second timeout is therefore described as a control, not speed. A synthetic eight-record fixture is test coverage, not a production KPI. A retained digest for an unavailable package is lineage evidence, not current public testing. A 10 GiB transfer cap is an admission boundary, not throughput.

Portfolio health checks this registry against every project README. A future public claim must pass the same source, definition, relevance, limitation, and explanation rules before it is accepted.

## Evidence definitions

### 13,333 public inspection records across three Chicago ZIP codes

- **Source:** [Chicago Food Inspection Outcomes, 2010–2018](https://github.com/Jnapier2/chicago-food-inspections-analysis), using a documented snapshot of the City of Chicago public dataset.
- **What was counted:** inspection records dated January 5, 2010 through June 13, 2018 in ZIP codes 60607, 60610, and 60622. One row is an inspection, not a unique restaurant.
- **Why it matters:** the project demonstrates reproducible public-data analysis and shows that recorded inspection outcomes and facility-risk classifications answer different questions.
- **Plain-language explanation:** “I analyzed 13,333 public inspection records across three Chicago ZIP codes. The important result was not the size alone; it was showing, through a reproducible notebook, that failure rate and facility-risk classification can point in different directions.”
- **Limitation:** the selected ZIP codes do not represent all of Chicago, facilities can appear more than once, and the analysis is descriptive rather than causal.

### 29 authored cases across five shifts

- **Source:** [Inbox From Hell](https://github.com/Jnapier2/inbox-from-hell), including its authored content and dependency-free full-campaign acceptance test.
- **What was counted:** 29 authored support cases distributed across a five-shift browser-game campaign.
- **Why it matters:** the count makes the product scope concrete and shows that branching decisions, persistent state, progression, accessibility, and campaign completion are exercised together.
- **Plain-language explanation:** “I built 29 branching support cases across five shifts and an automated test that completes the campaign. The number matters because each case interacts with shared state and progression; it is evidence of product scope, not a popularity metric.”
- **Limitation:** The figure describes authored product content. It does not claim a number of players, downloads, or market adoption.

### 17 public projects reconciled to exact GitHub source

- **Source:** [`.github/release-reconciliation.json`](.github/release-reconciliation.json), which records one reviewed default-branch commit and the represented/latest version state for each public project.
- **What was counted:** 17 public project records, excluding the profile repository itself and the two private workspaces.
- **Why it matters:** the ledger prevents the portfolio from presenting an older source tree as a newer final build and makes version gaps explicit instead of hiding them.
- **Plain-language explanation:** “I maintain a source-of-truth ledger for 17 public projects. Each entry is tied to the exact GitHub commit and version actually present, so a newer package is not claimed unless its source can be verified.”
- **Limitation:** The figure demonstrates portfolio governance. It is not a claim that every project has equal maturity, usage, or commercial adoption.

## Pin strategy

GitHub permits up to six pinned repositories or gists. The intended recruiter-facing order is:

1. `botops-manager` — operational reliability and support evidence
2. `digital-asset-governance-case-study` — governance, metadata, provenance, and stewardship
3. `media-tagger-bot` — conservative media operations with review and rollback controls
4. `chicago-food-inspections-analysis` — reproducible public-data analysis
5. `avalon-q-supervisor` — local supervision, health states, and bounded recovery
6. `beta-earth` — product design, resilient state, and tested browser delivery

Pin changes remain a GitHub account-setting action and are not represented as completed by source-controlled files alone.

## Maintenance rules

- Revisit this strategy after a material flagship release or at least quarterly.
- Change public evidence only when the supporting repository, manifest, dataset, test, or historical record is available and reviewed.
- Add or revise the matching record in `.github/public-claims.json` and `PUBLIC_CLAIMS.md` whenever a public claim changes.
- Remove or relocate a figure when its source is private, its definition requires too much explanation, or its professional relevance is weak.
- Keep the opening screen concise; move depth into project READMEs and reconciliation records.
- Prefer native Markdown and GitHub surfaces over externally rendered widgets.
- Keep all links HTTPS, descriptive, and useful without requiring authentication.
- Preserve the profile’s one-link-per-project contract and the canonical Portfolio, LinkedIn, and GitHub identities.
- Treat dynamic content as optional. Add it only with bounded failure behavior, an owned data source, and a clear maintenance path.

## Success signal

The strategy is working when a reviewer can answer these questions without opening every repository:

- What professional problems does Jerry solve?
- What does each headline number count, and why is it relevant?
- What can Jerry confidently say about every public project?
- Which three projects should be reviewed first?
- Where are the analytics, governance, automation, and product examples?
- What operating principles distinguish the work?
- How should a hiring team continue the conversation?

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not replace or infer a software license. Third-party components and referenced profiles retain their respective notices, licenses, and copyrights.
