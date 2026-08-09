# Public Project Release Reconciliation

This ledger ties every public project to the source, release, and default-branch commit actually present on GitHub. It keeps promotion evidence visible without relabeling an older tree as code it does not contain.

Project heads last reconciled: **August 8, 2026 at 10:09 PM CDT**
Framework policy alignment reviewed: **August 9, 2026 at 3:50 PM CDT**

All 17 public project default-branch heads and every declared version marker were checked in the recorded project-head pass. Exact 40-character reviewed heads are retained in [`.github/release-reconciliation.json`](.github/release-reconciliation.json). Dependency and installation controls for all 18 public repositories are recorded in [Dependency Reconciliation](DEPENDENCY_RECONCILIATION.md).

The profile case study **Reliable Project Delivery Framework v1.5.0** presents the current **v2.17.6** operating baseline as a concise, inspectable example of release discipline. It preserves the v2.17.5 fail-closed runtime release-identity boundary and adds unique execution namespaces, one stable unversioned project-qualified canonical entrypoint, launcher-derived project roots, and project-local output containment. The documentation-only case study records executable implementation as project-specific and does not claim that all public runtimes have already completed migration.

| Repository | GitHub represents | Latest verified | Reviewed head | State |
|---|---:|---:|---|---|
| BotOps Manager | 1.13.0 | 1.13.0 | `58f6925d` | Current; fresh discovery is distinguished from retained registry evidence after incomplete scans |
| Digital Asset Governance Audit | Current | Current | `05e2513f` | Current; deterministic fixture results are explicitly separated from production KPIs |
| MediaTaggerBot | 0.5.9 | 0.5.9 | `46d11751` | Current sanitized source; security pins, release notes, review gates, runtime identity, tests, and hosted security analysis passed |
| Chicago Food Inspection Outcomes | Current | Current | `5cce90d6` | Current analysis; 13,333 is defined as inspection records, not unique restaurants; Matplotlib 3.11.1 passed the complete notebook workflow |
| Avalon Q Supervisor | Current | Current | `621791f9` | GitHub-only source authority; hardware recovery remains fixture-tested rather than physically executed here |
| Automation Reliability Case Studies | Current | Current | `553719f7` | Current documentation-only studies; no deployment claim |
| Beta Earth | 0.4.11 | 0.5.0 | `dd0d1c19` | Historical v0.5.0 record retained; unavailable archive checks are not presented as current public coverage |
| Safe Video Downloader | 1.14.2 | 1.14.2 | `a98adba5` | Current; media-signature fallback, mixed-batch exit behavior, and the watchdog are verified across Python 3.11, 3.12, and 3.13 |
| MP3 Downloader | 1.0.0 | 1.0.0 | `d0237b2f` | Current; Certifi 2026.7.22, the hash-locked runtime, and the Windows matrix are verified |
| Image Downloader | 2026.08.08.1 | 2026.08.08.1 | `d8ee5070` | Current sanitized source; recoverable queue, three-transfer ceiling, session ledgers, managed-file integrity, CI, and CodeQL are verified |
| Large Text Chunker | 1.10.0 | 1.10.0 | `d68c091d` | Current stable release; estimate, exact, and automatic-fallback token evidence is verified on Windows and Ubuntu, while the recovered ZIP remains immutable provenance |
| NetLossDoctor | 2.10.0 | 2.10.0 | `8252dbb6` | Current; diagnostic bounds and load context are not certified line-speed measurements |
| LAN Router Comms | 2.3.0 | 2.3.0 | `cb2afe75` | Current; transfer caps and protocol floors are configuration constraints, not throughput or certification |
| Windows Health Audit | Current | Current | `936271b5` | GitHub-only source authority; stale Action-version wording replaced with the immutable-pin control |
| Inbox From Hell | 0.9.0 | 0.9.0 | `b71b6a98` | Current; 36 authored cases, six shifts, and department progression describe inspectable product scope rather than adoption |
| Kalshi 10×1¢ Public Edition | 1.0.0 | 1.0.0 | `737ebe6d` | Current checksum-controlled learning release; quantities and payoff examples are not performance claims |
| Kalshi 15-Minute Sell Preview | 41.22.3 | 41.22.3 | `caa58711` | Current checksum-controlled dry-run source with a downloadable v41.22.3 prerelease; live writes remain blocked |

## Promotion rule

A newer build is promoted only when the exact source or release bytes are available and can be matched to the recorded identity. The promotion pass must validate archive safety, manifests, rights and license metadata, third-party notices, secrets, dependencies, tests, launch behavior, diagnostics and export boundaries, and any relevant machine acceptance. Summaries or similarly named archives are not substitutes for source.

For executable first-party projects, the v2.17.6 policy requires a case-insensitively unique execution namespace, one stable unversioned project-qualified canonical entrypoint, metadata that records the backend target and runtime-owned output roots, and root resolution from the canonical launcher or script location rather than the caller’s working directory. Config, logs, state, temp, caches, exports, diagnostics, reports, downloads, backups, and release evidence default under that resolved project root. Cross-working-directory smoke tests must prove output containment. Released software that may load credentials or perform authenticated/live startup also retains the v2.17.5 runtime identity gate: running version/build and package metadata must agree, every immutable package-managed file must be present and SHA-256 correct, unsafe managed paths are rejected, and a same-version mixed package fails closed before authenticated activity. These framework policies do **not** claim that every existing runtime is already migrated; each project requires its own source, metadata, launcher, output-path, negative-path, support-evidence, and acceptance pass.

## Current blockers

### Beta Earth 0.5.0

The v0.5.0 final is recorded with SHA-256 `ea30ceb8a16566f0bcc20035360eba7bdeb8c8395e044d909ed99a2395e8f97b`, but its exact archive is not currently retrievable. [Issue #5](https://github.com/Jnapier2/beta-earth/issues/5) is the checksum-gated promotion record. GitHub therefore keeps v0.4.11 as the honest source identity while disclosing v0.5.0 as the newer recorded final. Originating checks remain historical evidence and are not described as rerunnable public coverage.

## Completed reconciliations

- **BotOps Manager 1.13.0:** the README no longer claims universal fresh observation. It explains that incomplete scans preserve earlier registry evidence and that control still requires fresh launcher and process identity checks.
- **Beta Earth v0.4.11 / recorded v0.5.0:** the historical successor digest remains visible, but the isolated originating test count was removed from the public README because the missing archive prevents rerun or inspection.
- **Windows Health Audit:** the README now describes the durable immutable Action pin instead of a stale checkout major-version label.
- **Reliable Project Delivery Framework v1.5.0:** the sealed public case study now reflects the exact v2.17.6 parameter package and preserves the v2.17.5 package as rollback. It documents unique execution namespaces, stable unversioned canonical entrypoints, launcher-derived project roots, project-local output containment, cross-working-directory acceptance, and the existing runtime release-identity/managed-file gate. It explicitly marks executable implementation project-specific and the runtime gate not applicable to this documentation-only release. No executable, credential path, or empty software-control placeholder was added.
- **MediaTaggerBot 0.5.9:** the sanitized public source now matches the current verified build. Its reviewed dependency set, pre-auth integrity gate for all 84 managed files, clean-clone suite with 192 passing tests and one environment-dependent skip, Windows matrix, and CodeQL passed before merge. Credential presence remains confined to redacted evidence, uncertain matches remain review-only, and private library counts are not presented as public performance claims.
- **Chicago Food Inspection Outcomes:** Matplotlib 3.11.1 passed binary installation, dependency checks, offline retrieval tests, and complete execution of the unchanged notebook and data snapshot on Python 3.12.
- **Safe Video Downloader 1.14.2:** fallback media-signature validation prevents an otherwise plausible response from being accepted blindly, while mixed batches now return an exit status that reflects partial failure. The full hosted matrix remains green on Python 3.11, 3.12, and 3.13.
- **MP3 Downloader 1.0.0:** Certifi 2026.7.22 was added to the existing SHA-256-locked runtime contract. Exact-hash installation, dependency checks, compilation, offline tests, Windows Python 3.11 and 3.13, and CodeQL passed before merge.
- **Image Downloader 2026.08.08.1:** the sanitized public source adds a persistent 100-item queue, automatic interruption recovery, a hard three-transfer ceiling, and timestamped session ledgers while retaining credential-safe evidence, Windows-safe naming, bounded discovery, and atomic finalization. The clean-clone integrity gate verified all 13 managed files after Windows checkout normalization; the built-in self-test, public unit tests, dependency jobs, and CodeQL passed before merge.
- **Large Text Chunker 1.10.0:** the promoted public source adds offline estimate, optional exact `tiktoken==0.13.0`, and visible automatic-fallback token modes; source and per-chunk token evidence; a dated, nonblocking upload-cap advisory; and backward verification for v1.0 manifests. Seventeen local tests passed with the optional integration skipped, then Windows and Ubuntu unit jobs, real-tokenizer exact smoke tests, and CodeQL passed at the reconciled head. Documentation-only PR #9 then clarified the upload-limit and tokenizer guidance without changing runtime behavior, dependencies, version, or release identity; its Windows and Ubuntu unit and real-tokenizer jobs plus CodeQL passed. The recovered ZIP remains identified by SHA-256 `20a428ae390b0443ef08acc5bbcc562124f0f748be74be25b6d9e547916d8ebf`; it was not recreated or attached to the GitHub release. Its original BAT preflight and self-test also passed from a spaced path on ALPHA while the signed Norton provider state and all ten source-file hashes remained unchanged.
- **Inbox From Hell 0.9.0:** the public edition now includes 36 authored cases across six shifts, persistent department progression, migration coverage, and accessible interaction states. The same production URL serves the verified v0.9 source.
- **Kalshi 15-Minute Sell Preview 41.22.3:** the checksum-sealed v41.22.3 public prerelease is now the current download, matching the reviewed source version and retaining the immutable write block. Security and test automation plus CodeQL passed at the reconciled head.

There are no active public source-promotion branches after the recorded project-head pass. Beta Earth remains blocked because its exact v0.5.0 archive is unavailable; [Large Text Chunker issue #3](https://github.com/Jnapier2/large-text-chunker/issues/3) is now the record for closing the completed cross-repository reconciliation, not a source-promotion blocker. The machine-readable source authority is [`.github/release-reconciliation.json`](.github/release-reconciliation.json), and the Portfolio health workflow validates its completeness, exact version markers, and reviewed default-branch heads.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not replace or infer a software license. Third-party components retain their respective notices and licenses.
