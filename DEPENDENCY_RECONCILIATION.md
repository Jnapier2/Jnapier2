# Public Dependency Reconciliation

This record identifies how each public repository controls third-party packages and installation behavior. It separates projects that need no application dependencies from exact pins, SHA-256 locks, bounded compatible ranges, and checksum-sealed releases. All 18 public repositories are covered.

Last reconciled: **July 26, 2026 at 11:05 AM CDT**

The machine-readable authorities are [`.github/dependency-reconciliation.json`](.github/dependency-reconciliation.json) and [`.github/dependabot-policy.json`](.github/dependabot-policy.json). Portfolio health validates dependency files, installation commands, consistency gates, absence claims, each Dependabot ecosystem block’s exact directory/cadence/PR limit, monitored workflows for automatic merge mechanisms, and open Dependabot PRs for enabled auto-merge.

## Coverage

| Repository | Dependency contract | Current state |
|---|---|---|
| Jnapier2 profile | No third-party runtime | Standard-library audits; external Actions pinned to reviewed commit SHAs |
| BotOps Manager | No third-party runtime | Python standard library only |
| Digital Asset Governance Audit | No third-party runtime | Python standard library only |
| MediaTaggerBot | SHA-256 locked | Verified v0.5.7 runtime; Actions-only monthly monitoring; runtime changes remain synchronized with the BAT launcher |
| Chicago Food Inspection Outcomes | Exact pins | Python 3.12 pins; binary install, `pip check`, notebook execution, and review-only monitoring |
| Avalon Q Supervisor | No third-party runtime | Python standard library only |
| Automation Reliability Case Studies | No third-party runtime | Documentation and standard-library tests only |
| Beta Earth | No third-party runtime | Public v0.4.11 declares no runtime dependencies; v0.5.0 remains checksum-gated |
| Safe Video Downloader | Exact pin | `yt-dlp[default]` fixed at 2026.07.04; binary install, `pip check`, and monthly review proposals |
| MP3 Downloader | SHA-256 locked | Certifi 2026.6.17 and yt-dlp 2026.7.4 remain synchronized with the application identity; Actions v7 passed native CI |
| Image Downloader | Bounded ranges | Standard dependencies plus Playwright 1.61.0 receive separate binary installation and consistency validation |
| Large Text Chunker | No third-party runtime | Dependency-free public v1.0.0; v1.10.0 remains checksum-gated |
| NetLossDoctor | No third-party runtime | Windows PowerShell and operating-system tools only |
| LAN Router Comms | No third-party runtime | Windows PowerShell and operating-system cryptography/networking only |
| Windows Health Audit | No third-party runtime | Read-only Windows PowerShell with no package installation |
| Inbox From Hell | No third-party runtime | Dependency-free static browser game and Node acceptance test |
| Kalshi 10×1¢ Public Edition | Sealed and audited | Exact runtime and audit-tool pins; checksum verifier and `pip-audit`; no unsealed monitoring file |
| Kalshi 15m Sell Preview | Sealed and audited | Hash-locked environments, `pip-audit`, and its existing weekly labeled monitoring queue |

## Monitoring policy applied

Review-only monitors create dependency or GitHub Actions proposals; they do not auto-merge and never replace native install, test, vulnerability, manifest, SBOM, or checksum gates. This is fail-closed: each ecosystem block is parsed separately, automatic merge commands/actions in monitored workflows are rejected, and any open Dependabot PR with auto-merge enabled fails Portfolio health.

- **MediaTaggerBot:** GitHub Actions monitoring only. Package proposals cannot update the two embedded BAT launcher maps, so runtime changes remain a coordinated release task.
- **Chicago Food Inspection Outcomes:** monthly grouped minor/patch Python and Action proposals, limited to one open proposal per ecosystem. Matplotlib 3.11.x is ignored until a dedicated figure-compatibility review.
- **Safe Video Downloader:** monthly grouped minor/patch Python and Action proposals, limited to one open proposal per ecosystem.
- **MP3 Downloader:** monthly grouped proposals remain behind the exact hash and embedded runtime-identity checks. The portfolio-validated checkout and setup-python v7 revisions passed both Windows jobs.
- **Image Downloader:** monthly grouped proposals plus a separate optional-browser job that installs `requirements-browser.txt`, runs `pip check`, and imports Playwright without downloading browsers.
- **Kalshi 10×1¢:** no monitoring file was merged because its sealed inventory rejected the unlisted file. Adding it requires a complete release regeneration.
- **Kalshi 15m:** the existing weekly monitored queue remains unchanged because a cadence-only edit would require resealing the entire preview.

## Applied and rejected candidates

- **Applied — Image Downloader Playwright 1.61.0:** standard tests and the optional-browser install, consistency, and import job passed; automated review found no remaining issue.
- **Applied — MP3 GitHub Actions v7:** exact reviewed Action commits passed the Python 3.11/3.13 matrix without changing the application or runtime lock.
- **Rejected — Chicago Matplotlib 3.11.1:** upstream text/font changes may alter rendered output; the current 3.10.9 line remains until a dedicated notebook and figure-regression pass.
- **Rejected — MP3 Certifi 2026.7.22:** exact artifacts installed, passed `pip check`, imported, and compiled, but native acceptance failed because the lock drifted from `EXPECTED_RUNTIME_PINS`. The known-good 2026.6.17 runtime remains active.

## Deliberately deferred compatibility changes

- **MediaTaggerBot runtime packages:** any update must synchronize package metadata, the SHA-256 lock, both BAT launcher maps, tests, and Windows launch evidence.
- **Chicago compatibility lines:** Matplotlib 3.11.x and other new major/minor lines require a dedicated notebook and rendered-figure review.
- **MP3 Certifi:** a future 2026.7.22 transition must update the embedded application identity and release evidence with the hash lock; a lock-only change is not accepted.
- **Kalshi 15m cryptography 49.x:** the public preview is checksum sealed. A major transition requires regenerated locks, SBOM, manifests, checksums, and the complete security matrix.

## Private workspace boundaries

- `-illuminati-card-game` is the private Alpha Miner USB build workspace. Its draft release line remains blocked until exact source, boot, mining-off, and physical-hardware evidence are complete.
- `illuminati-card-game` remains a private INWO research source containing third-party card materials and internal research records. It is not represented as a public software release.

## Operating rule

Dependency updates are adopted only when the exact change can be installed and validated within the repository’s existing safety and release boundary. Major-version changes, launcher-coupled updates, application/lock identity mismatches, and sealed-release mutations remain explicit follow-up work rather than silent upgrades.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not replace or infer a software license. Third-party components retain their respective notices and licenses.
