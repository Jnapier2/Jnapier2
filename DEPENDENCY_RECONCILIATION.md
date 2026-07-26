# Public Dependency Reconciliation

This record identifies how each public repository controls third-party packages and installation behavior. It separates projects that need no application dependencies from exact pins, SHA-256 locks, bounded compatible ranges, and checksum-sealed releases.

Last reconciled: **July 26, 2026 at 2:40 AM CDT**

The machine-readable authority is [`.github/dependency-reconciliation.json`](.github/dependency-reconciliation.json). The Portfolio health workflow checks the declared files, version markers, installation commands, consistency gates, absence claims, and deferred compatibility decisions.

## Coverage

| Repository | Dependency contract | Current state |
|---|---|---|
| Jnapier2 profile | No third-party runtime | Standard-library audits; external Actions pinned to reviewed commit SHAs |
| BotOps Manager | No third-party runtime | Python standard library only |
| Digital Asset Governance Audit | No third-party runtime | Python standard library only |
| MediaTaggerBot | SHA-256 locked | Verified v0.5.7 runtime retained; fail-closed installation and launcher/lock agreement test added |
| Chicago Food Inspection Outcomes | Exact pins | Python 3.12 pins refreshed within existing major lines; binary install and `pip check` required |
| Avalon Q Supervisor | No third-party runtime | Python standard library only |
| Automation Reliability Case Studies | No third-party runtime | Documentation and standard-library tests only |
| Beta Earth | No third-party runtime | Public v0.4.11 declares no runtime dependencies; v0.5.0 remains checksum-gated |
| Safe Video Downloader | Exact pin | `yt-dlp[default]` fixed at 2026.07.04; binary install and `pip check` required |
| MP3 Downloader | SHA-256 locked | Exact Certifi and yt-dlp artifacts; `pip check` required before import and tests |
| Image Downloader | Bounded ranges | Requests, Beautiful Soup, and Pillow resolve inside reviewed major lines; binary install and `pip check` required |
| Large Text Chunker | No third-party runtime | Dependency-free public v1.0.0; v1.10.0 remains checksum-gated |
| NetLossDoctor | No third-party runtime | Windows PowerShell and operating-system tools only |
| LAN Router Comms | No third-party runtime | Windows PowerShell and operating-system cryptography/networking only |
| Windows Health Audit | No third-party runtime | Read-only Windows PowerShell with no package installation |
| Inbox From Hell | No third-party runtime | Dependency-free static browser game and Node acceptance test |
| Kalshi 10×1¢ Public Edition | Sealed and audited | Exact runtime and audit-tool pins; checksum verifier and `pip-audit` gate |
| Kalshi 15m Sell Preview | Sealed and audited | Hash-locked runtime and audit environments; `pip-audit` across the supported Python matrix |

## Updates applied in this pass

### MediaTaggerBot

The verified Requests 2.33.0 runtime was retained because the package metadata, SHA-256 lock, and primary BAT launcher already agreed on that version. CI now:

- separates runtime, local-project, and test-tool installation;
- exits on the first failed stage rather than allowing a later command to mask it;
- requires binary artifacts for the hash-locked runtime;
- records bounded runtime-install and dependency-check diagnostics only when the corresponding step fails; and
- runs a regression test that requires every locked package to have a SHA-256 hash and requires the project metadata, lock, and both launcher checks to agree.

### Chicago Food Inspection Outcomes

The Python 3.12 environment moved to compatible releases inside the existing major lines:

- `ipykernel==6.31.0`
- `matplotlib==3.10.9`
- `nbconvert==7.17.1`
- `pandas==2.3.3`

The dataset, notebook source, calculations, and reported findings did not change. CI now installs binary distributions, validates the dependency graph, runs the offline retrieval tests, and executes the notebook from the bundled data snapshot.

### Safe Video Downloader, MP3 Downloader, and Image Downloader

The existing application dependency versions remain unchanged. Their Windows workflows now tie pip caching to the declared requirements and validate the installed dependency graph before compilation and tests. Safe Video Downloader and Image Downloader require binary distributions; MP3 Downloader retains its complete SHA-256 lock.

## Deliberately deferred compatibility changes

- **MediaTaggerBot Requests 2.34.2:** requires one synchronized launcher, package-metadata, lock, test, and Windows launch pass. The known-good 2.33.0 contract remains active.
- **Chicago major-version lines:** ipykernel 7.x, Matplotlib 3.11.x, and pandas 3.x require a dedicated notebook-compatibility review. They were not mixed into the maintenance update.
- **Certifi:** authoritative package listings did not agree on the next release identity. MediaTaggerBot and MP3 Downloader retain the verified SHA-256-locked 2026.6.17 artifact.
- **Kalshi 15m cryptography 49.x:** the public preview is checksum sealed. A major dependency transition requires regenerated locks, SBOM, manifests, checksums, and the complete security matrix.
- **MP3 Downloader Action revisions:** its existing checkout and setup-python references remain immutable v6 commits. A v7 transition is deferred to a separate workflow-compatibility pass.

## Private workspace boundaries

- `-illuminati-card-game` is the private Alpha Miner USB build workspace. Its draft release line remains blocked until exact source, boot, mining-off, and physical-hardware evidence are complete.
- `illuminati-card-game` remains a private INWO research source containing third-party card materials and internal research records. It is not represented as a public software release.

## Operating rule

Dependency updates are adopted only when the exact change can be installed and validated within the repository’s existing safety and release boundary. Major-version changes, conflicting upstream records, and sealed-release mutations remain explicit follow-up work rather than silent upgrades.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not replace or infer a software license. Third-party components retain their respective notices and licenses.
