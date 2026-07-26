# Public Project Release Reconciliation

This ledger distinguishes the source actually present on GitHub from newer verified builds that cannot yet be promoted safely. It prevents an older tree from being relabeled as code it does not contain while keeping successor evidence visible.

Last reconciled: **July 26, 2026 at 2:40 AM CDT**

All 17 public project default-branch heads and every declared version marker were checked in this pass. Exact 40-character reviewed heads are retained in [`.github/release-reconciliation.json`](.github/release-reconciliation.json). Dependency and installation controls for all 18 public repositories are recorded in [Dependency Reconciliation](DEPENDENCY_RECONCILIATION.md).

The profile case study **Reliable Project Delivery Framework v1.1.0** represents framework **v2.17.2**, including the 26/26 rule-family, 40/40 scenario, and 20/20 negative-safeguard results.

| Repository | GitHub represents | Latest verified | Reviewed head | State |
|---|---:|---:|---|---|
| BotOps Manager | 1.13.0 | 1.13.0 | `f5a8c5db` | Current; GitHub retains later public hardening |
| Digital Asset Governance Audit | Current | Current | `05e2513f` | Current |
| MediaTaggerBot | 0.5.7 | 0.5.7 | `a4728e77` | Current source authority; fail-closed dependency installation and launcher/lock contract |
| Chicago Food Inspection Outcomes | Current | Current | `ed7783d8` | Current analysis; compatible Python 3.12 dependency refresh |
| Avalon Q Supervisor | Current | Current | `621791f9` | GitHub-only source authority |
| Automation Reliability Case Studies | Current | Current | `553719f7` | Current |
| Beta Earth | 0.4.11 | 0.5.0 | `99c05ae3` | Verified successor awaits exact checksum-matched source transfer |
| Safe Video Downloader | 1.14.2 | 1.14.2 | `68cf9627` | Current; exact dependency consistency gate added |
| MP3 Downloader | 1.0.0 | 1.0.0 | `236dcbb2` | Current; hash-locked dependency consistency gate added |
| Image Downloader | 2026.07.19.1 | 2026.07.19.1 | `9a61d2a6` | Current; bounded-range dependency consistency gate added |
| Large Text Chunker | 1.0.0 | 1.10.0 | `4bca8818` | Checksum companion retained; exact successor ZIP unavailable; promotion blocked |
| NetLossDoctor | 2.10.0 | 2.10.0 | `8252dbb6` | Current; immutable CI reference retained |
| LAN Router Comms | 2.3.0 | 2.3.0 | `cb2afe75` | Current; immutable CI reference retained |
| Windows Health Audit | Current | Current | `9185f61e` | GitHub-only source authority |
| Inbox From Hell | 0.7.0 | 0.7.0 | `8752ac02` | Current GitHub source authority; immutable CI references retained |
| Kalshi 10×1¢ Public Edition | 1.0.0 | 1.0.0 | `737ebe6d` | Current checksum-controlled learning release |
| Kalshi 15m Sell Preview | 41.22.3 | 41.22.3 | `15fba07c` | Current checksum-controlled dry-run preview |

## Promotion rule

A newer build is promoted only when the exact source or release bytes are available and can be matched to the recorded identity. The promotion pass must validate archive safety, manifests, rights and license metadata, third-party notices, secrets, dependencies, tests, launch behavior, diagnostics and export boundaries, and any relevant machine acceptance. Summaries or similarly named archives are not substitutes for source.

## Current blockers

### Beta Earth 0.5.0

The v0.5.0 final is recorded with SHA-256 `ea30ceb8a16566f0bcc20035360eba7bdeb8c8395e044d909ed99a2395e8f97b`, but its exact archive is not currently retrievable. [Issue #5](https://github.com/Jnapier2/beta-earth/issues/5) is the checksum-gated promotion record. GitHub therefore keeps v0.4.11 as the honest source identity while disclosing v0.5.0 as the newer verified final.

### Large Text Chunker 1.10.0

The checksum companion for `ChatGPT_Text_Chunker_v1.10.0_20260718_0111_CDT.zip` is retained and records SHA-256 `20a428ae390b0443ef08acc5bbcc562124f0f748be74be25b6d9e547916d8ebf`, but the exact ZIP is not currently retrievable. [Issue #3](https://github.com/Jnapier2/large-text-chunker/issues/3) is the checksum-gated promotion record. The public 1.0.0 source remains authoritative until those successor bytes are recovered and verified.

## Completed reconciliations

- **MediaTaggerBot 0.5.7:** the verified runtime set remains unchanged. CI now separates runtime, local-project, and test-tool installation; fails closed on the first failed stage; preserves bounded diagnostics; and tests that project metadata, the SHA-256 lock, and both BAT launcher checks agree.
- **Chicago Food Inspection Outcomes:** exact Python 3.12 pins moved to compatible releases within the existing major-version lines. CI now uses binary distributions, checks the resolved environment, runs the offline retrieval tests, and executes the unchanged notebook and data snapshot.
- **Safe Video Downloader 1.14.2:** the verified five-second no-progress worker watchdog remains current. CI now ties caching to the requirements file, installs binary dependencies, and checks the resolved environment before compilation and tests.
- **MP3 Downloader 1.0.0:** the existing SHA-256-locked binary runtime remains unchanged. CI now checks the installed dependency graph before runtime imports, compilation, and offline tests.
- **Image Downloader 2026.07.19.1:** the verified five-second per-image request budget and content safeguards remain current. CI now resolves binary dependencies inside the reviewed ranges and checks the resulting environment before the offline safety suite.

There are no active public promotion branches. Two checksum-gated successor records remain blocked until their exact archives are recovered. The machine-readable source authority is [`.github/release-reconciliation.json`](.github/release-reconciliation.json), and the Portfolio health workflow validates its completeness, exact version markers, and reviewed default-branch heads.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not replace or infer a software license. Third-party components retain their respective notices and licenses.
