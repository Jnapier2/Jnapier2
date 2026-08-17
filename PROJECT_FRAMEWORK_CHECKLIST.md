# Reliable Project Delivery Framework — Implementation Checklist

**Public edition:** v1.6.0  
**Use:** Apply the sections that match the project's purpose and risk. Do not
turn a small read-only task into a heavyweight release process.

## Authority and scope

- [ ] Confirm the canonical project name, current source authority, and known-good rollback.
- [ ] Rank evidence: current runtime and exact errors before assumptions or filenames.
- [ ] Identify Critical, High, Normal, and Optional work.
- [ ] For broad work, create a coverage ledger with no silent omissions.
- [ ] Reserve time for final checks, packaging, rollback, and the completion report.

## File surface and project identity

- [ ] Keep one canonical execution namespace and one primary entrypoint.
- [ ] Inventory every retained file before a deep cleanup or lean release.
- [ ] Group exact duplicates by hash and functional overlap by behavior.
- [ ] Keep one canonical implementation for each required capability.
- [ ] Parameterize safe variants; retain compatibility names only as thin forwarders.
- [ ] Preserve unique, third-party, signed, historical, rollback, evidence, and user-owned assets.
- [ ] Map imports, launchers, automation, config, docs, tests, and outputs before retirement.
- [ ] Record keep, merge, parameterize, forward, archive, remove, and unresolved decisions.

## Paths, outputs, and portability

- [ ] Derive project root from the launcher or source location—not caller CWD.
- [ ] Keep config, logs, state, temp, exports, diagnostics, reports, and downloads project-local.
- [ ] Validate and display every explicit external output destination.
- [ ] Support spaces and ordinary move, copy, rename, and fresh-extract scenarios.
- [ ] Make setup and repair idempotent and preserve user data.
- [ ] Use cloud storage as source, handoff, and archive—not live runtime.

## Inputs and sensitive startup

- [ ] For each critical input: recognize, validate, map, exercise, and confirm it.
- [ ] Reject ambiguous, ignored, shadowed, unsupported, or unconfirmed critical inputs.
- [ ] Before credentials or authenticated activity, verify version, build, metadata, manifest, and managed hashes.
- [ ] On identity failure, allow only safe read-only status, diagnostics, and repair guidance.
- [ ] Do not rewrite package-managed files while deciding whether they are trusted.

## Stability and operator control

- [ ] Bound retries, backoff, queues, resources, timeouts, logs, and restart loops.
- [ ] Define graceful shutdown, durable state, and recovery behavior where needed.
- [ ] Show operating mode, state authority, effective outputs, and the stop/recovery path.
- [ ] Use same-computer duplicate guards only when parallel local execution is unsafe.
- [ ] Keep computer recognition advisory and independent across installations.

## Security, dependencies, and data

- [ ] Do not weaken endpoint, operating-system, browser, or platform protections.
- [ ] Keep secrets out of source, logs, screenshots, diagnostics, and public artifacts.
- [ ] Classify data as public, project-internal, sensitive, or secret.
- [ ] Record direct and bundled dependencies, versions, provenance, integrity, and licenses.
- [ ] Preserve third-party notices and report unknown dependency status honestly.
- [ ] Avoid needless packing, obfuscation, stealth, persistence, and broad exclusions.

## Diagnostics and Export20

- [ ] Use cached, sanitized evidence; do not perform live actions during export.
- [ ] Limit Export20 to twenty or fewer high-value, redacted, read-only items.
- [ ] Build in project-local temp, test archive integrity, then finalize atomically.
- [ ] Record collector failures and omissions without losing minimum recovery evidence.

## Program-specific controls

- [ ] Trading: separate dry/test/live, validate products and balances, bound size/loss/exposure, reconcile ambiguous writes, and expose a kill switch.
- [ ] Mining/compute: verify executable provenance, dependencies, hardware/runtime fit, resources, temperature policy, watchdog, and restart budget.
- [ ] Public editions: exclude credentials, private configuration, wallets, live strategies, machine identifiers, and operational secrets.

## Verification and release

- [ ] Test the canonical entrypoint from an unrelated working directory.
- [ ] Confirm effective root, outputs, logs, diagnostics, and recovery locations.
- [ ] Exercise critical inputs and relevant migration, move, rename, and repair paths.
- [ ] Run sensitive-startup, dependency, license, metadata, and public-sanitization checks where applicable.
- [ ] Preserve the known-good rollback and exact tested source or artifact identity.
- [ ] Report changed, reviewed, verified, unverified, deferred, blocked, skipped, and not-found work.
- [ ] Never claim an untested computer, platform, package, or public release passed.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

See [the framework](PROJECT_FRAMEWORK.md), [the changelog](PROJECT_FRAMEWORK_CHANGELOG.md),
and [public metadata](PROJECT_FRAMEWORK_METADATA.json).
