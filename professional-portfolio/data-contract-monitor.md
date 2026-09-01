# Data Contract Monitor

Data Contract Monitor turns readable data expectations into repeatable checks. It helps teams catch schema drift, invalid values, stale records, duplicate keys, referential breaks, and unreviewed sensitive fields before unreliable data reaches a report, model, or operating process.

[Explore the source](https://github.com/Jnapier2/data-contract-monitor) · [Download v0.3.3](https://github.com/Jnapier2/data-contract-monitor/releases/tag/v0.3.3) · [Try the included demos](https://github.com/Jnapier2/data-contract-monitor#try-the-included-demos)

## Current release

| Item | Verified state |
| --- | --- |
| Version | 0.3.3 public alpha prerelease |
| Build | `DCM-0.3.3-B20260831-WINDOWSFRESHNESS1` |
| Automated suite | 69 tests passed on the prepared Windows source tree |
| Release identity | 144/144 files managed by the public repository manifest verified |
| Distribution | Rebuilt ZIP, SHA-256 sidecar, and verification receipt attached to the GitHub release |
| License | Apache-2.0 |

The current release strengthens Windows browser freshness and narrowly contains a known local transport-reset condition without changing contract semantics. Its checksum sidecar and verification receipt are published with the release archive.

## What it does

- Validates CSV, JSON, JSON Lines, Parquet, and Excel inputs through a common contract model.
- Checks required fields, types, ranges, patterns, allowed values, uniqueness, freshness, aggregate reconciliation, and reference existence.
- Supports exact and bounded streaming profiles so reviewers can see where a result is complete or intentionally approximate.
- Produces JSON, CSV, Markdown, HTML, and local dashboard evidence from the same result model.
- Fits local review, command-line use, containers, and CI workflows without requiring a hosted service.
- Keeps state, logs, diagnostics, and recovery output project-local and excluded from source control.

## Design

![Data Contract Monitor architecture](assets/data-contract-monitor-architecture.svg)

Contracts remain readable YAML. The engine loads a contract, reads the selected data source, applies the same validation rules across interfaces, and records result evidence with the release identity that produced it.

## Evidence boundary

Historical v0.1.2 synthetic measurements remain available in the [benchmark review](evidence/data-contract-monitor-benchmark-review.json). They are retained as regression context, not presented as v0.3.3 throughput or a production service-level promise. Hardware, storage, format, row width, and rule complexity materially affect performance.

This is evaluation software, not a production certification, distributed processing service, or data-loss-prevention guarantee. The repository documents known limitations and includes synthetic examples for safe review.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
