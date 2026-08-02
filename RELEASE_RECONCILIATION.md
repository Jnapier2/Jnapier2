# Public Project Release Reconciliation

This ledger distinguishes the source actually present on GitHub from newer verified builds that cannot yet be promoted safely. It prevents an older tree from being relabeled as code it does not contain while keeping successor evidence visible.

Last reconciled: **August 2, 2026 at 1:04 AM CDT**

All 17 public project default-branch heads and every declared version marker were checked in this pass. Exact 40-character reviewed heads are retained in [`.github/release-reconciliation.json`](.github/release-reconciliation.json). Dependency and installation controls for all 18 public repositories are recorded in [Dependency Reconciliation](DEPENDENCY_RECONCILIATION.md).

The profile case study **Reliable Project Delivery Framework v1.3.0** presents the current **v2.17.4** operating baseline as a concise, inspectable example of release discipline. Its public evidence emphasizes the controls, acceptance gates, and decision boundaries that can be reviewed directly.

| Repository | GitHub represents | Latest verified | Reviewed head | State |
|---|---:|---:|---|---|
| BotOps Manager | 1.13.0 | 1.13.0 | `58f6925d` | Current; fresh discovery is distinguished from retained registry evidence after incomplete scans |
| Digital Asset Governance Audit | Current | Current | `05e2513f` | Current; deterministic fixture results are explicitly separated from production KPIs |
| MediaTaggerBot | 0.5.7 | 0.5.7 | `97a669f5` | Current source authority; public documentation is limited to reviewable source, tests, and safeguards |
| Chicago Food Inspection Outcomes | Current | Current | `5cce90d6` | Current analysis; 13,333 is defined as inspection records, not unique restaurants; Matplotlib 3.11.1 passed the complete notebook workflow |
| Avalon Q Supervisor | Current | Current | `621791f9` | GitHub-only source authority; hardware recovery remains fixture-tested rather than physically executed here |
| Automation Reliability Case Studies | Current | Current | `553719f7` | Current documentation-only studies; no deployment claim |
| Beta Earth | 0.4.11 | 0.5.0 | `dd0d1c19` | Historical v0.5.0 record retained; unavailable archive checks are not presented as current public coverage |
| Safe Video Downloader | 1.14.2 | 1.14.2 | `a98adba5` | Current; media-signature fallback, mixed-batch exit behavior, and the watchdog are verified across Python 3.11, 3.12, and 3.13 |
| MP3 Downloader | 1.0.0 | 1.0.0 | `d0237b2f` | Current; Certifi 2026.7.22, the hash-locked runtime, and the Windows matrix are verified |
| Image Downloader | 2026.07.19.1 | 2026.07.19.1 | `8ef7ad1e` | Current; saved evidence redacts sensitive URL details, and Windows-safe filenames and the 15-second request floor are covered by tests |
| Large Text Chunker | 1.0.0 | 1.10.0 | `7a39f444` | Checksum companion retained; exact successor ZIP unavailable; promotion blocked |
| NetLossDoctor | 2.10.0 | 2.10.0 | `8252dbb6` | Current; diagnostic bounds and load context are not certified line-speed measurements |
| LAN Router Comms | 2.3.0 | 2.3.0 | `cb2afe75` | Current; transfer caps and protocol floors are configuration constraints, not throughput or certification |
| Windows Health Audit | Current | Current | `936271b5` | GitHub-only source authority; stale Action-version wording replaced with the immutable-pin control |
| Inbox From Hell | 0.9.0 | 0.9.0 | `b71b6a98` | Current; 36 authored cases, six shifts, and department progression describe inspectable product scope rather than adoption |
| Kalshi 10×1¢ Public Edition | 1.0.0 | 1.0.0 | `737ebe6d` | Current checksum-controlled learning release; quantities and payoff examples are not performance claims |
| Kalshi 15-Minute Sell Preview | 41.22.3 | 41.22.3 | `d2ed74f7` | Current checksum-controlled dry-run source; the newest downloadable ZIP remains clearly identified as 41.22.2 rev.2 |

## Promotion rule

A newer build is promoted only when the exact source or release bytes are available and can be matched to the recorded identity. The promotion pass must validate archive safety, manifests, rights and license metadata, third-party notices, secrets, dependencies, tests, launch behavior, diagnostics and export boundaries, and any relevant machine acceptance. Summaries or similarly named archives are not substitutes for source.

## Current blockers

### Beta Earth 0.5.0

The v0.5.0 final is recorded with SHA-256 `ea30ceb8a16566f0bcc20035360eba7bdeb8c8395e044d909ed99a2395e8f97b`, but its exact archive is not currently retrievable. [Issue #5](https://github.com/Jnapier2/beta-earth/issues/5) is the checksum-gated promotion record. GitHub therefore keeps v0.4.11 as the honest source identity while disclosing v0.5.0 as the newer recorded final. Originating checks remain historical evidence and are not described as rerunnable public coverage.

### Large Text Chunker 1.10.0

The checksum companion for the recorded v1.10.0 successor archive is retained and records SHA-256 `20a428ae390b0443ef08acc5bbcc562124f0f748be74be25b6d9e547916d8ebf`, but the exact ZIP is not currently retrievable. [Issue #3](https://github.com/Jnapier2/large-text-chunker/issues/3) is the checksum-gated promotion record. The public 1.0.0 source remains authoritative until those successor bytes are recovered and verified.

## Completed reconciliations

- **BotOps Manager 1.13.0:** the README no longer claims universal fresh observation. It explains that incomplete scans preserve earlier registry evidence and that control still requires fresh launcher and process identity checks.
- **Beta Earth v0.4.11 / recorded v0.5.0:** the historical successor digest remains visible, but the isolated originating test count was removed from the public README because the missing archive prevents rerun or inspection.
- **Windows Health Audit:** the README now describes the durable immutable Action pin instead of a stale checkout major-version label.
- **Reliable Project Delivery Framework v1.3.0:** the sealed public case study now reflects the v2.17.4 operating baseline. It shows how source authority, bounded risk, portable Windows releases, evidence-led acceptance, and independent local operation fit together without exposing private working material.
- **MediaTaggerBot 0.5.7:** the verified runtime set remains unchanged. The public README no longer uses private library or outcome counts as independently verifiable performance evidence; it limits public documentation to source, tests, and documented safeguards. CI still separates runtime, local-project, and test-tool installation, fails closed, preserves bounded diagnostics, and tests launcher/lock/metadata agreement. Monthly Actions proposals are review-only and never auto-merge.
- **Chicago Food Inspection Outcomes:** Matplotlib 3.11.1 passed binary installation, dependency checks, offline retrieval tests, and complete execution of the unchanged notebook and data snapshot on Python 3.12.
- **Safe Video Downloader 1.14.2:** fallback media-signature validation prevents an otherwise plausible response from being accepted blindly, while mixed batches now return an exit status that reflects partial failure. The full hosted matrix remains green on Python 3.11, 3.12, and 3.13.
- **MP3 Downloader 1.0.0:** Certifi 2026.7.22 was added to the existing SHA-256-locked runtime contract. Exact-hash installation, dependency checks, compilation, offline tests, Windows Python 3.11 and 3.13, and CodeQL passed before merge.
- **Image Downloader 2026.07.19.1:** output naming now handles Windows-reserved and bidirectional-text cases safely, while logs retain useful correlation evidence without exposing URL credentials. Standard and optional-browser dependency jobs remain green.
- **Large Text Chunker 1.0.0:** public wording now describes the successor archive generically and keeps the checksum-gated promotion boundary clear.
- **Inbox From Hell 0.9.0:** the public edition now includes 36 authored cases across six shifts, persistent department progression, migration coverage, and accessible interaction states. The same production URL serves the verified v0.9 source.
- **Kalshi 15-Minute Sell Preview 41.22.3:** visible naming is consistent and the README distinguishes the current 41.22.3 source tree from the latest downloadable 41.22.2 rev.2 release. The source manifest and SHA-256 inventory were regenerated together and passed the release-integrity, security, test, dependency-review, CodeQL, and cross-platform gates.

There are no active public promotion branches after this pass. Two checksum-gated successor records remain blocked until their exact archives are recovered. The machine-readable source authority is [`.github/release-reconciliation.json`](.github/release-reconciliation.json), and the Portfolio health workflow validates its completeness, exact version markers, and reviewed default-branch heads.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not replace or infer a software license. Third-party components retain their respective notices and licenses.
