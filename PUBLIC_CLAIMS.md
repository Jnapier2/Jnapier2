# Public Project Claims and Speaking Guide

This guide explains what each public repository can support, how to describe it in plain language, and where the claim stops. It is designed for interviews, recruiter conversations, portfolio reviews, and future README maintenance.

A project does not need a large number to be impressive. A claim belongs in the public portfolio when it is:

1. traceable to public source, tests, documentation, a dataset, or a clearly labeled historical record;
2. defined precisely enough to explain what was measured or built;
3. relevant to the professional skill being demonstrated;
4. accompanied by the most important limitation; and
5. explainable without memorizing promotional wording.

Version numbers, configured limits, fixture results, content counts, test scope, historical records, and real operating outcomes are different kinds of evidence. They are not presented as interchangeable.

## Portfolio governance and Reliable Project Delivery Framework

**What to say:** I manage the public portfolio as a governed source system. Each project is tied to the version and exact GitHub commit that is actually present, and newer packages are not claimed when their source cannot be verified.

**Evidence to point to:** `RELEASE_RECONCILIATION.md`, `.github/release-reconciliation.json`, `DEPENDENCY_RECONCILIATION.md`, Portfolio health, and the Reliable Project Delivery Framework case study.

**Numbers you can explain:** The release ledger covers 17 public project repositories. That count excludes the profile repository and the two private workspaces. The framework’s 26/26, 40/40, and 20/20 figures describe a historical document-validation package and remain in the detailed case study, where their categories and non-rerun limitation are visible.

**Do not overclaim:** The portfolio ledger does not mean every project has equal maturity, external adoption, production deployment, or physical-machine acceptance.

## BotOps Manager

**What to say:** BotOps Manager is a local Windows console that discovers candidate automation projects, preserves prior registry evidence when a scan is incomplete, and rechecks launcher and process identity before it permits a project-scoped control action.

**Evidence to point to:** `bot_manager.py`, the deterministic test suite, the launcher-safety audit, the process-identity checks, and the bounded support exporter.

**Numbers you can explain:** None are needed. Its strongest evidence is the control boundary: stale registry data or a stored PID is not accepted by itself as authority to act.

**Do not overclaim:** It does not guarantee discovery of inaccessible folders, control every process beneath a root, administer remote machines, or prove the safety of child application logic.

## Digital Asset Governance Audit

**What to say:** This is a read-only catalog audit that turns schema, provenance, confidence, and duplicate signals into an ordered human review queue without changing the source catalog.

**Evidence to point to:** `catalog_audit.py`, the synthetic fixture, reason-coded queue output, and the unit tests.

**Numbers you can explain:** The 8-record percentages and queue counts are deterministic fixture results. They exist to exercise every audit path; they are not production catalog KPIs.

**Do not overclaim:** The tool is not a live DAM connector, semantic entity-resolution system, retention authority, risk certification, or automatic remediation engine.

## MediaTaggerBot

**What to say:** MediaTaggerBot uses public metadata and local evidence to propose media matches, but complete-scan, confidence, ambiguity, dry-run, journal, readback, and rollback controls determine whether a file can be changed.

**Evidence to point to:** The source, controlled provider tests, dependency and launcher contract tests, `apply-safe` rules, SQLite journal, verification flow, and rollback manifests.

**Numbers you can explain:** No private library or outcome total is used as public performance evidence. The public project is strongest when explained through its review and mutation safeguards.

**Do not overclaim:** The public repository does not prove a correction rate across a private library, guarantee provider accuracy, or make `apply-all` safe for unattended use.

## Chicago Food Inspection Outcomes, 2010–2018

**What to say:** I used a reproducible notebook and a bounded City of Chicago dataset snapshot to compare inspection outcomes with facility-risk classifications across three ZIP codes. The main finding is that the two measures can point in different directions.

**Evidence to point to:** The bundled data snapshot, data provenance notes, retrieval script, executed notebook, validation tests, and result table.

**Numbers you can explain:** 13,333 means inspection records from January 5, 2010 through June 13, 2018 in ZIP codes 60607, 60610, and 60622. One row is an inspection, not a unique restaurant. The original 2018 notebook reported 12,971; the 2026 public snapshot contains 13,333, and the repository explains why that difference cannot be resolved from the surviving files.

**Do not overclaim:** The analysis is descriptive, the selected ZIP codes do not represent all of Chicago, facilities can appear repeatedly, and the results do not rank restaurant safety or establish causation.

## Avalon Q Supervisor

**What to say:** This project converts local miner telemetry into explicit health states and allows reboot recovery only after repeated critical evidence, two operator-controlled gates, identity checks, and a durable restart-budget reservation.

**Evidence to point to:** The protocol adapter, deterministic hardware-free fixture, recovery-state logic, interprocess lock tests, audit events, and documented manual-intervention conditions.

**Numbers you can explain:** The two gates are configuration enablement and the runtime `--execute` flag. They are authorization controls, not performance measurements.

**Do not overclaim:** Publication testing used synthetic protocol responses; no live Avalon Q reboot was executed from the publication environment. The project is not a mining-profitability model or security certification.

## Automation Reliability Case Studies

**What to say:** These are three design studies showing how a controller should reconcile authoritative state before retrying across exchange, process-supervision, and media-transfer boundaries.

**Evidence to point to:** The three public case-study documents, explicit invariants, synthetic failure scenarios, link and scope tests, and the shared decision flow.

**Numbers you can explain:** Three is the number of documented studies, not a deployment count.

**Do not overclaim:** The repository contains no deployable integration and does not demonstrate production trading, mining, transfer activity, profitability, platform endorsement, or regulatory approval.

## Beta Earth

**What to say:** Beta Earth is a working local browser-RPG vertical slice with layered domain logic, validated content, revision-safe saves, a loopback-only interface, and source-portability tests on the public v0.4.11 tree.

**Evidence to point to:** The current source, game catalogs, schemas, save migrations, UI, tests, startup dry run, and CI matrix.

**Numbers you can explain:** The six-room Sprawl 15 scenario is public product scope. Version 0.5.0 is a recorded newer final with a retained digest, but its exact archive is unavailable. The historical issue records originating checks; those checks are not presented as current public test coverage because they cannot be rerun from this repository.

**Do not overclaim:** The public source is v0.4.11, not v0.5.0. This is a single-player vertical slice, not a complete or hosted game, and hosted CI is not physical acceptance on every named computer.

## Safe Video Downloader

**What to say:** This is an authorized-media retrieval workflow whose GUI and CLI share the same planning, public-network checks, duplicate controls, isolated worker, interruption recovery, and final output validation.

**Evidence to point to:** `safe_media_downloader.py`, offline boundary tests, the visible-output default, worker isolation, redaction tests, and the output validator.

**Numbers you can explain:** Five seconds is the configured no-progress watchdog for a silent worker. It is a failure-detection threshold, not a promise that a download completes in five seconds.

**Do not overclaim:** The tool does not determine whether a download is lawful, bypass access controls, guarantee extractor compatibility, or create a complete SSRF isolation boundary.

## MP3 Downloader

**What to say:** MP3 Downloader turns one authorized URL into a validated audio-only result through metadata preflight, bounded recovery, output checks, duplicate reconciliation, and tightly limited support exports.

**Evidence to point to:** The hash-locked requirements, submitted-URL checks, metadata preflight, FFprobe validation, SQLite/SHA-256 duplicate logic, offline tests, and local self-test boundary.

**Numbers you can explain:** No performance count is needed. “One URL” describes the workflow boundary, not throughput.

**Do not overclaim:** Metadata preflight cannot prove ownership or permission, the URL guard is not a complete SSRF containment boundary, and extractor compatibility depends on upstream sites and the pinned dependency.

## Image Downloader

**What to say:** Image Downloader collects permitted images through bounded page discovery and provisional transfers that must pass destination, type, size, decode, duplicate, and integrity checks before atomic finalization.

**Evidence to point to:** Standard and optional browser modes, destination checks, active-content rejection, duplicate layers, resume validator, atomic writes, and the offline safety suite.

**Numbers you can explain:** Five seconds is the per-image network budget covering preflight, attempts, bounded backoff, reconnects, and streamed transfer. It is a deadline control, not a speed or completion guarantee.

**Do not overclaim:** This is not a crawler, archival guarantee, permission detector, or complete hostile-network isolation boundary. Browser mode is not an authentication bypass.

## Large Text Chunker

**What to say:** Large Text Chunker separates readable overlap from raw source boundaries so chunks can retain context while the normalized source can still be reconstructed and hash-verified exactly.

**Evidence to point to:** The split and verify commands, source/raw/output hashes, manifest, reconstruction checks, collision-safe output, and unit tests.

**Numbers you can explain:** Version 1.10.0 is a recorded historical successor whose checksum companion remains, but the exact ZIP is unavailable; public source remains v1.0.0. Token values are conservative estimates, not model-specific billing counts.

**Do not overclaim:** Exact reconstruction applies to the normalized text defined by the tool, not the original byte-for-byte newline representation. The missing successor archive is not represented as current source.

## NetLossDoctor

**What to say:** NetLossDoctor collects time-bounded Windows network evidence across gateway, route, DNS, TCP, latency, events, and optional captures so support can compare layers instead of relying on a single ping.

**Evidence to point to:** `NetLossDoctor.ps1`, safe default doctor mode, explicit active modes, optional-capture cleanup, redaction tests, synthetic examples, and safety-contract tests.

**Numbers you can explain:** Lookback days, record caps, intervals, and load limits are operator-selected collection bounds. Throughput under load is context, not a certified line-speed measurement.

**Do not overclaim:** It is not an outage authority, packet-forensics platform, security audit, or replacement for ISP/vendor instrumentation. Intermediate-hop ICMP loss alone is not proof of an outage.

## LAN Router Comms

**What to say:** LAN Router Comms provides authenticated text and resumable file exchange between two managed Windows computers on a trusted private network, with durable queues and hash receipts instead of blind resend behavior.

**Evidence to point to:** TLS and certificate checks, HMAC envelopes, replay controls, DPAPI-protected local state, resume logic, receipt hashes, bounded sessions, firewall rollback, and safety tests.

**Numbers you can explain:** The 10 GiB transfer cap is a configured admission limit, not demonstrated throughput. TLS 1.2 and RSA 2048 are minimum protocol constraints, not claims of formal security certification.

**Do not overclaim:** The protocol has not received an independent security review, is not designed for internet exposure, and provides no NAT traversal, cloud relay, non-Windows client, or remote shell.

## Windows Health Audit

**What to say:** Windows Health Audit returns one read-only, privacy-preserving endpoint snapshot and treats unavailable collectors as missing evidence rather than proof of failure.

**Evidence to point to:** `Get-WindowsHealthSnapshot.ps1`, the no-remediation command policy, no-network/no-elevation source checks, failure-isolated collectors, synthetic report, and immutable CI workflow.

**Numbers you can explain:** Event lookback days and maximum error records are collection bounds chosen by the caller. They are not health scores or benchmarks.

**Do not overclaim:** The output is a review aid, not a diagnostic authority, security scanner, monitoring service, or proof that an endpoint is healthy or unhealthy.

## Inbox From Hell

**What to say:** Inbox From Hell is a static browser game that uses branching support decisions to exercise persistent state, short- and long-term progression, accessible interaction, and a complete campaign test.

**Evidence to point to:** The authored content, state engine, responsive UI, save migrations, live static demo, and dependency-free acceptance test.

**Numbers you can explain:** The public project contains 29 authored cases across five shifts, six player metrics, and a six-room office system. These numbers describe product scope that can be inspected in source and exercised by the campaign test; they are not player, download, retention, or revenue metrics.

**Do not overclaim:** The architecture could inform training simulations, but this game is not validated training software and has no claimed user-adoption or business-impact record.

## Kalshi 10×1¢ Public Edition

**What to say:** This is a verification-led educational order planner with a deliberately narrow write surface, explicit activation, exact order constraints, persistent exposure accounting, and fail-closed checks. The default path remains verification, scan, and dry run.

**Evidence to point to:** `TRADING_DISABLED`, `run_bot.py verify --ci`, exact manifests and dependency pins, route and payload guards, ledger and lock tests, security documentation, and the official API references recorded in the repository.

**Numbers you can explain:** 10 contracts at 1¢ means at most $0.10 principal for a fully filled order before fees. The 80-contract session cap and eight create-attempt limit are configured safety ceilings. A possible $10 gross settlement if all ten contracts win is conditional payoff arithmetic, not expected return or performance evidence.

**Do not overclaim:** The heuristic is not a prediction model or market edge. Verification is not a warranty or legal approval. Orders may not fill, fees apply, the full principal can be lost, and account eligibility and every trading decision remain the operator’s responsibility.

## Kalshi 15-Minute Sell Preview

**What to say:** This is a checksum-sealed, dry-run-only learning preview whose retained engine can inspect market and account state while every mutating request is blocked before signing or transmission.

**Evidence to point to:** `PUBLIC_PREVIEW_ONLY`, launcher and engine guards, pre-signing mutation boundary, sealed inventory, security tests, exact dependencies, CodeQL, and the documented preview scope.

**Numbers you can explain:** “15-minute” describes the event-market cadence, not setup time or performance. One cycle is the default observation boundary. Any simulated price or quantity is planning output, not profit or proceeds.

**Do not overclaim:** The preview cannot submit orders and has no verified live-money performance record. A passing verifier does not make the strategy profitable, bug-free, or suitable for an account.

## Private workspace boundaries

- `-illuminati-card-game` remains the private Alpha Miner USB build workspace. No approved source package, ISO, checksum, or physical-hardware claim is presented publicly while its acceptance evidence is incomplete.
- `illuminati-card-game` remains private INWO research containing third-party card materials and internal evidence. It is not presented as a public software release.

## Maintenance rule

Before adding a new number or strong public claim, record its source, definition, relevance, limitation, and 30-second explanation in `.github/public-claims.json` and this guide. When those elements cannot be supplied, use a narrower qualitative claim or leave the statement out.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not replace or infer a software license. Each linked repository and third-party component retains its own notices, licenses, and rights.
