# Public Project Release Reconciliation

This ledger distinguishes the source actually present on GitHub from newer verified builds that cannot yet be promoted safely. It prevents an older tree from being relabeled as code it does not contain while keeping successor evidence visible.

Last reconciled: **July 25, 2026**

| Repository | GitHub represents | Latest verified | State |
|---|---:|---:|---|
| BotOps Manager | 1.13.0 | 1.13.0 | Current; GitHub retains later public hardening |
| Digital Asset Governance Audit | Current case study | Current case study | Current |
| MediaTaggerBot | 0.5.7 | 0.5.7 | GitHub source authority; exact packaged release still pending |
| Chicago Food Inspection Outcomes | Current analysis | Current analysis | Current |
| Avalon Q Supervisor | Current source | Current source | GitHub-only source authority |
| Automation Reliability Case Studies | Current studies | Current studies | Current |
| Beta Earth | 0.4.11 | 0.5.0 | Verified successor awaits exact checksum-matched source transfer |
| Safe Video Downloader | 1.14.2 | 1.14.2 | Current; verified no-progress watchdog merged into stronger public source |
| MP3 Downloader | 1.0.0 | 1.0.0 | Current; Drive label adds release-profile metadata only |
| Image Downloader | 2026.07.18.1 | 2026.07.19.1 | Verified successor under security-preserving reconciliation |
| Large Text Chunker | 1.0.0 | 1.10.0 | Checksum companion retained, exact successor ZIP unavailable; promotion blocked |
| NetLossDoctor | 2.10.0 | 2.10.0 | Current |
| LAN Router Comms | 2.3.0 | 2.3.0 | Current |
| Windows Health Audit | Current source | Current source | GitHub-only source authority |
| Inbox From Hell | 0.7.0 | 0.7.0 | Current GitHub source authority |
| Kalshi 10×1¢ Public Edition | 1.0.0 | 1.0.0 | Current checksum-controlled learning release |
| Kalshi 15m Sell Preview | 41.22.3 | 41.22.3 | Current checksum-controlled dry-run preview |

## Promotion rule

A newer build is promoted only when the exact source or release bytes are available and can be matched to the recorded identity. The promotion pass must validate archive safety, manifests, rights and license metadata, third-party notices, secrets, dependencies, tests, launch behavior, diagnostics/export boundaries, and any relevant machine acceptance. Summaries or similarly named archives are not substitutes for source.

## Current blockers

### Beta Earth 0.5.0

The v0.5.0 final is recorded with SHA-256 `ea30ceb8a16566f0bcc20035360eba7bdeb8c8395e044d909ed99a2395e8f97b`, but its exact archive is not currently retrievable. [Issue #5](https://github.com/Jnapier2/beta-earth/issues/5) is the checksum-gated promotion record. GitHub therefore keeps v0.4.11 as the honest source identity while disclosing v0.5.0 as the newer verified final.

### Large Text Chunker 1.10.0

The checksum companion for `ChatGPT_Text_Chunker_v1.10.0_20260718_0111_CDT.zip` is retained and records SHA-256 `20a428ae390b0443ef08acc5bbcc562124f0f748be74be25b6d9e547916d8ebf`, but the exact ZIP is not currently retrievable. The public 1.0.0 source remains authoritative until those successor bytes are recovered and verified.

## Completed reconciliations

- **Safe Video Downloader 1.14.2:** the verified five-second no-progress worker watchdog is merged into the stronger public URL, destination, cancellation, duplicate, visibility, and redaction controls. Silent-worker, activity-reset, and post-processing-disarm regression tests are retained; temporary application scaffolding removed itself after validation.

## Active reconciliation

- [Image Downloader 2026.07.19.1](https://github.com/Jnapier2/image-downloader/pull/4): merge the verified five-second per-image network budget without reverting public destination checks, content validation, visible output, duplicate controls, or browser guardrails.

The machine-readable authority is [`.github/release-reconciliation.json`](.github/release-reconciliation.json). The portfolio health workflow validates its completeness and version markers.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not replace or infer a software license. Third-party components retain their respective notices and licenses.
