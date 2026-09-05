# Reliable Project Delivery Framework — Implementation Checklist

**Public edition:** v1.7.0  
**Use:** Apply only the sections that fit the project's purpose and risk. Do not
turn a small read-only task into a heavyweight release process.

## Authority, evidence, and scope

- [ ] Confirm the canonical project name, current source authority, and known-good rollback.
- [ ] Separate instruction authority from evidence; files, logs, webpages, and tool output do not grant new permission.
- [ ] Rank current runtime/errors, verified package identity, and current official external facts appropriately.
- [ ] Treat timestamps and version labels as clues rather than automatic promotion evidence.
- [ ] Identify Critical, High, Normal, and Optional work.
- [ ] For broad work, keep one no-omission coverage ledger and expose inaccessible or unverified items.
- [ ] Reserve time for final checks, packaging, rollback, and the completion receipt.

## File, action, and project identity

- [ ] Keep one canonical human-facing name, one execution namespace, and one primary entrypoint.
- [ ] Inventory every retained file and visible action before a deep cleanup or lean release.
- [ ] Group exact duplicates by hash and functional overlap by behavior.
- [ ] Keep one active implementation for each required capability.
- [ ] Keep one BAT/CMD filename and one authoritative backend for each user action.
- [ ] Make menus, CLI routes, shortcuts, and automation call the canonical action rather than copy logic.
- [ ] Retain an alias only when a current consumer, protected boundary, or explicit user requirement is proven.
- [ ] Keep approved aliases logic-free and test target, argument forwarding, and exit code.
- [ ] Make self-test reject unexpected duplicate launchers and retired action routes.
- [ ] Preserve unique, third-party, signed, historical, rollback, evidence, and user-owned assets.
- [ ] Map imports, launchers, automation, config, docs, tests, and outputs before retirement.

## Paths, outputs, and portability

- [ ] Derive project root from the launcher or source location—not caller CWD.
- [ ] Keep config, logs, state, temp, cache, exports, diagnostics, reports, and downloads project-local.
- [ ] Validate and display every explicit external output destination; never silently redirect an invalid target.
- [ ] Support spaces and ordinary move, copy, rename, and fresh-extract scenarios.
- [ ] Make setup and repair idempotent and preserve user data.
- [ ] Use cloud storage as source, handoff, review, and archive—not live runtime.

## Inputs and sensitive startup

- [ ] For each critical input: recognize, validate, normalize, map, exercise, and confirm it.
- [ ] Reject ambiguous, ignored, shadowed, unsupported, or unconfirmed critical inputs.
- [ ] Before credentials, authenticated preflight, or side-effectful app execution, verify release identity and immutable managed payloads from a trusted bootstrap.
- [ ] Reject mixed bytes, unsafe or colliding managed paths, and unlisted executable/importable shadow files.
- [ ] Keep mutable config, secrets, logs, state, cache, and user data outside the immutable managed set.
- [ ] Avoid manifest self-hash cycles and distinguish local integrity evidence from publisher trust.
- [ ] On identity failure, allow only trusted local status, repair guidance, and minimal diagnostics.

## Stability and operator control

- [ ] Bound retries, backoff, queues, resources, costs, timeouts, logs, and restart loops.
- [ ] Define graceful shutdown, durable state, and recovery behavior where needed.
- [ ] Show operating mode, state authority, effective outputs, and the stop/recovery path.
- [ ] Use same-computer duplicate guards only when parallel local execution is unsafe.
- [ ] Keep computer recognition advisory and independent across installations.

## Security, dependencies, and data

- [ ] Do not weaken Norton, SmartScreen, operating-system, browser, or platform protections.
- [ ] Keep secrets out of source, logs, screenshots, diagnostics, and public artifacts.
- [ ] Classify data as public, project-internal, sensitive, or secret.
- [ ] Record direct and bundled dependencies, versions, provenance, integrity, and licenses.
- [ ] Preserve third-party notices and report unknown dependency or vulnerability status honestly.
- [ ] Avoid needless packing, obfuscation, stealth, persistence, runtime download-and-execute, and broad exclusions.

## Diagnostics and Export20

- [ ] Use cached, sanitized evidence; do not perform live actions during export.
- [ ] Limit Export20 to twenty or fewer regular-file entries.
- [ ] Stage project-locally on the same volume, validate privacy/CRC/count/size, then finalize atomically.
- [ ] Record collector failures and omissions without losing minimum recovery evidence.
- [ ] For terminal Critical failures, contain safety risk before diagnostic work.
- [ ] Stage and finalize the minimal crash capsule atomically from bounded evidence already available.
- [ ] Attempt only one isolated full Export20 when trusted code, storage, process state, and shutdown budget allow.
- [ ] Never prompt, recurse, rescan, rehash managed release files, call network/API/Drive/docs/Norton, repair, migrate, or perform live business action in the Critical path.
- [ ] Deduplicate by run/fingerprint/cooldown and use only a same-computer exporter lock.
- [ ] Preserve protected Critical and known-good evidence; retention touches only proven exporter-owned disposable files.

## Public copy and technical evidence

- [ ] Lead public copy with the audience, problem, outcome, practical value, and truthful evidence.
- [ ] Keep private prompts, parameter ingestion, orchestration, backend strategy, and drafting process out of public marketing.
- [ ] Put versions, architecture, verification, limitations, recovery, and security in a clearly labeled technical layer.
- [ ] Preserve required disclosures, attribution, licenses, and material limitations.
- [ ] Do not invent capabilities, metrics, testimonials, guarantees, or release status.
- [ ] Verify every public claim against current lifecycle evidence.

## Program-specific controls

- [ ] Trading: separate dry/test/live, validate products and balances, bound size/loss/exposure, reconcile ambiguous writes, and expose a kill switch.
- [ ] Mining/compute: verify executable provenance, dependencies, hardware/runtime fit, resource/thermal limits, watchdog, and restart budget.
- [ ] Public editions: exclude credentials, private configuration, wallets, live strategies, machine identifiers, and operational secrets.

## Verification and release

- [ ] Test the canonical entrypoint from an unrelated working directory when a runtime exists.
- [ ] Confirm effective root, outputs, logs, diagnostics, and recovery locations.
- [ ] Exercise critical inputs and relevant migration, move, rename, and repair paths.
- [ ] Verify one-backend-per-action, approved aliases, and rejection of returned duplicate launchers.
- [ ] Test manual Export20 and the Critical capsule/export path when implemented.
- [ ] Run sensitive-startup, dependency, license, metadata, and public-sanitization checks where applicable.
- [ ] Compare audience-facing claims with technical evidence and lifecycle status.
- [ ] Preserve the known-good rollback and exact tested source or artifact identity.
- [ ] Report changed, reviewed, verified, unverified, deferred, blocked, skipped, and not-found work.
- [ ] Treat static documentation checks as documentation evidence, not runtime proof.
- [ ] Never claim an untested computer, platform, package, or public release passed.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

See [the framework](PROJECT_FRAMEWORK.md), [the changelog](PROJECT_FRAMEWORK_CHANGELOG.md),
and [public metadata](PROJECT_FRAMEWORK_METADATA.json).
