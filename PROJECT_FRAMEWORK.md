# Reliable Project Delivery Framework

This is the public principles document used across my software, automation, analytics, and game projects. It describes the shared operating boundaries without publishing private implementation playbooks, internal audit records, credentials, machine profiles, project-specific thresholds, or raw diagnostics.

## 1. One clear project identity

Each project keeps one canonical name and one stable, project-qualified launch surface. Versions and build identifiers belong in project metadata and release records rather than in the everyday launcher name.

A deliberate rename preserves a clear migration path. Thin compatibility wrappers may forward to the canonical launcher, but duplicate copies of the same business logic are avoided.

## 2. Local and portable by default

A project resolves its working root from its own launcher or script location rather than from the caller's current directory. Configuration, logs, state, temporary files, caches, exports, diagnostics, reports, downloads, and backups remain beneath that project root by default.

An external location is used only when the operator selects it explicitly and the project can validate and display the destination clearly.

## 3. Preserve known-good behavior

A confirmed working release is retained as the rollback baseline before significant changes. Repair comes before redesign, and a new feature should not silently replace behavior that is already working.

Dependency or platform changes are deliberate. Projects do not silently move to a newer API, package, or runtime without project-specific validation.

## 4. Keep changes reversible

Low-risk local work should remain easy to run. Destructive actions, administrator or security changes, public publishing, bulk writes, credential handling, and live-financial activity require an explicit boundary, a backup or simulation where practical, and clear operator confirmation.

Temporary output is written safely and finalized only after the result has been checked. Existing user data is not silently moved or deleted during migration.

## 5. Validate critical inputs end to end

A critical input is not considered supported merely because it was accepted by a form or configuration file. It must be recognized, validated, mapped to the intended behavior, exercised, and confirmed through visible evidence.

Ambiguous, ignored, shadowed, or unsupported critical inputs fail closed instead of producing a misleading success state.

## 6. Verify release identity before sensitive startup

Released software that may load credentials or perform authenticated activity checks that its running version, build identity, package metadata, and managed release files agree before sensitive startup.

A mixed or incomplete release does not proceed merely because its visible version label looks correct. Local status, diagnostics, and repair guidance may remain available without loading credentials or rewriting release files during verification.

## 7. Independent operation across computers

Computer recognition may provide useful labels, sensible local defaults, separated logs and exports, or performance guidance. It may not block launch, assign cross-computer ownership, require a handoff, create a shared lease, or prevent another installation from running independently.

Same-computer duplicate protection is used only when two simultaneous local instances would be unsafe.

## 8. Clear operator control

The operator should be able to see what a project is doing, where it is writing, what state it is using, and how to stop or recover it. Automated recovery is bounded and gives up safely when success cannot be verified.

Projects favor understandable status, graceful shutdown, bounded retries, backoff, state recovery, and a clear first recovery step.

## 9. Privacy-conscious diagnostics

Support evidence is limited, redacted, and reviewable. Diagnostic packages avoid credentials and unnecessary personal data, use project-local staging, verify archive integrity before finalization, and contain only the highest-value evidence needed for troubleshooting.

## 10. Transparent releases

First-party releases use clear versioning, project metadata, rights notices, dependency records when applicable, and integrity evidence appropriate to the project. Third-party notices and licenses remain intact.

A release is not described as complete when important launch, recovery, output, safety, or validation work remains unverified.

## Public boundary

This framework is intentionally outcome-focused. Private checklists, internal scoring systems, release ledgers, repository-wide audit machinery, credentials, raw support exports, unique machine identifiers, private paths, and project-specific operating thresholds remain outside the public repository.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not create or replace a software license.
