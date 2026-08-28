# Data Contract Monitor

**Executable data contracts for files, pipelines, and review workflows.**

Data Contract Monitor catches broken schemas, stale records, invalid values, duplicate keys, and unreviewed sensitive fields before unreliable data reaches a report, model, or operational process. It turns readable YAML expectations into evidence that people can review and automated workflows can enforce.

## Product status

| Item | Publicly supported statement |
| --- | --- |
| Program version | 0.1.2 |
| Build | `DCM-0.1.2-B20260828-LAUNCHISOLATION1` |
| Acceptance class | User-confirmed Windows working save state |
| Independent revalidation | Release identity passed across 115 managed files; 44 automated tests passed under Python 3.13.5 |
| Bounded performance check | A 100,000-row, six-column synthetic CSV completed three validation trials with a 0.747-second median in the independent Linux review environment |
| Source rights | Apache-2.0 in the canonical project |

The benchmark is a local synthetic regression measurement, not a production service-level promise. Hardware, storage, file format, rule complexity, and data distribution affect results.

## The problem

A dataset can remain technically readable while becoming operationally unsafe. A required column can disappear, a business key can duplicate, yesterday's feed can become stale, or an unapproved sensitive field can arrive without causing a parser error.

Data Contract Monitor makes those failures explicit and reviewable. A clean run and a failed run use the same engine, result model, severity rules, and report formats.

## Review workflow

1. Select or generate a readable YAML contract.
2. Validate a CSV, Excel, JSON, JSON Lines, or optional Parquet dataset.
3. Review failures by severity, rule, column, and affected-row count.
4. Inspect aggregate column profiles and privacy-field hints without exposing raw cell values in the report.
5. Export structured evidence for people, continuous integration, and security-review workflows.
6. Compare new schemas with an approved baseline to detect added, removed, type-changed, or nullability-changed fields.

## Architecture

![Data Contract Monitor architecture](assets/data-contract-monitor-architecture.svg)

One validation engine and one typed result model serve every interface. This prevents the dashboard, command line, API, Python package, and automation integration from developing different meanings for the same rule.

## Capabilities

| Capability | Practical value |
| --- | --- |
| Executable contracts | Required fields, types, nullability, uniqueness, ranges, lengths, patterns, approved values, and freshness become version-controlled checks |
| Dataset-level controls | Row-count ranges, composite uniqueness, null-ratio limits, and conditional completeness cover rules that cannot be expressed one column at a time |
| Drift monitoring | Approved schema baselines expose additions, removals, type changes, and observed-nullability changes |
| Privacy review | Heuristic field-name and bounded sample-pattern signals guide human review without claiming to be a data-loss-prevention product |
| Multiple evidence formats | Accessible HTML, JSON, JUnit XML, and SARIF support business review, automation, and code-scanning workflows |
| Shared interfaces | The command line, local API, dashboard, Python package, and composite action use the same validation semantics |
| Local-first operation | Temporary uploads are removed after each request; reports contain aggregate evidence rather than raw dataset values |

## Reliability design

- Release-mode startup verifies the version, build metadata, manifest, and every managed-file digest before normal execution.
- The Windows launcher derives the project root from its own location and keeps mutable outputs project-local.
- A preferred-port collision selects another reserved loopback endpoint instead of opening an unrelated local service.
- The browser opens only after the health response proves the exact service, version, build, and per-launch identity.
- Data-quality failure uses a different exit code from execution failure, allowing automation to distinguish bad data from a broken tool.
- Critical failures produce bounded, redacted local evidence rather than recursively copying the project.
- Recovery starts from a clean extraction of the known package instead of mixing managed files from different versions.

## Demonstrated scenario

The synthetic customer-order example includes a passing dataset and a deliberately broken dataset. The failed case produces twelve findings across schema, completeness, uniqueness, validity, freshness, and privacy review. The passing case produces none. No credentials or private records are required.

## What this demonstrates

- Translating business expectations into enforceable data rules.
- Designing evidence that serves both technical and nontechnical reviewers.
- Separating data failure from software failure.
- Building local-first software with explicit release integrity and recovery behavior.
- Connecting data quality, privacy review, schema governance, automation, and accessible reporting.

## Public boundary

This case study contains no private release archive, support export, user path, machine identifier, private package digest, account information, credential, or production dataset. It does not expose raw evidence from the private Windows acceptance run.

## Limitations

- The current engine is file-oriented and loads a dataset into memory; it is not a distributed or streaming validator.
- Privacy detection is heuristic and requires human review.
- Optional formats require their corresponding dependencies.
- First-run dependency installation may contact the configured package index.
- The public page is a product case study, not a substitute for the canonical release package or its acceptance evidence.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
