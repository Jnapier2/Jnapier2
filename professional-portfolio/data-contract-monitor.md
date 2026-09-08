# Data Contract Monitor

**Turn data-quality expectations into checks people can understand and act on.**

Data Contract Monitor helps teams identify unreliable data before it reaches a report, model, or operating process. It translates readable business expectations into repeatable checks for schema changes, invalid values, stale records, duplicate keys, broken references, and unreviewed sensitive fields.

[Explore the source](https://github.com/Jnapier2/data-contract-monitor) · [Download v0.3.4](https://github.com/Jnapier2/data-contract-monitor/releases/tag/v0.3.4) · [Try the included demos](https://github.com/Jnapier2/data-contract-monitor/tree/main/examples)

## What it does

It validates CSV, JSON, JSON Lines, Parquet, and Excel inputs against an explicit contract. Reviewers can examine required fields, types, ranges, patterns, allowed values, uniqueness, freshness, aggregate reconciliation, and reference existence. Results are available in readable reports and structured formats for further analysis.

## What makes the design distinctive

The same contract and result model support different review interfaces, keeping the meaning of a check consistent. Exact and bounded streaming profiles make it clear when a result is complete and when an approximation is intentional. The emphasis is not simply on finding an error, but on explaining which expectation failed and leaving evidence that can be reviewed.

## Why it is useful

Analysts, data stewards, and operations teams can make data acceptance criteria explicit, repeat checks across incoming files, and investigate quality problems before relying on the affected information. The project demonstrates how business rules become executable controls without making those rules inaccessible to reviewers.

<details>
<summary>Version-specific evidence and evaluation limits</summary>

## Release qualification record

| Item | Recorded state |
| --- | --- |
| Version | 0.3.4 public alpha prerelease |
| Build | `DCM-0.3.4-B20260901-SECURITY1` |
| Automated suite | 71 tests passed on the prepared Windows source tree |
| Release identity | 145/145 files managed by the public repository manifest verified |
| Distribution | ZIP, checksum, and verification receipt available with the release |
| License | Apache-2.0 |

These are published historical qualification results, not a new test run. See [repository checks](https://github.com/Jnapier2/data-contract-monitor/actions) for dated, commit-specific results.

## Evidence boundary

Historical v0.1.2 synthetic measurements remain available in the [benchmark review](evidence/data-contract-monitor-benchmark-review.json). They are retained as regression context, not presented as v0.3.4 throughput or a production service-level promise. Performance depends on the environment, file format, dataset, and rules evaluated.

This is evaluation software, not a production certification, distributed processing service, or data-loss-prevention guarantee. Included examples are synthetic.

</details>

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
