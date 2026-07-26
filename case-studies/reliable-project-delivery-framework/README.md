# Reliable Project Delivery Framework

[![Portfolio health](https://github.com/Jnapier2/Jnapier2/actions/workflows/profile-contract.yml/badge.svg)](https://github.com/Jnapier2/Jnapier2/actions/workflows/profile-contract.yml)

A repeatable control framework for moving complex software projects from uncertain inputs to verified, portable releases without sacrificing rollback, privacy, operator control, or independent local operation.

## Why I built it

Complex projects often fail for ordinary reasons: multiple “final” versions, machine-specific paths, fragile launchers, missing rollback evidence, unbounded diagnostics, unclear responsibility, and changes that cannot be proven safe. I designed this framework to turn those risks into explicit decisions, tests, and release evidence.

## What it does

- Selects a verified working baseline when source packages conflict.
- Keeps one shared package portable across distinct Windows environments.
- Uses capability detection and optional computer recognition for helpful local labels, paths, defaults, diagnostics, and performance guidance.
- Keeps every installation independently launchable; local process locks and duplicate protection never block another computer.
- Preserves one canonical project name and searchable aliases across thread transfers and project branches.
- Separates reversible local work from destructive, live-financial, credential, administrator, security, public, and bulk-write actions.
- Requires critical inputs to be recognized, validated, mapped, exercised, and confirmed.
- Produces bounded, redacted diagnostic packages that preserve the most useful evidence.
- Preserves known-good state, rollback instructions, version history, rights metadata, dependency records, and checksums.
- Blocks release when source, validation, or recovery evidence is incomplete.

## Validation scorecard

| Measure | Result |
|---|---:|
| Historical validation package | 15 files; ZIP integrity passed |
| Rule families represented | **26 / 26** |
| Representative scenarios passed | **40 / 40** |
| Negative/conflict safeguards passed | **20 / 20** |
| Document quality | 11-page DOCX visually reviewed; accessibility audit found 0 high, 0 medium, and 0 low findings |
| Privacy boundary | Raw machine reports and unique identifiers excluded |

The scorecard records the document-level validation performed on the historical v2.17.2 source package. Public case-study v1.2.0 corrects the active computer-coordination policy without rewriting that checksum-verified historical package or claiming that its original scenario totals were rerun.

## Policy correction in public case study v1.2.0

### Independent local operation across multiple computers

Each installation runs independently. Computer recognition may improve diagnostic labels, choose sensible local paths and defaults, organize local logs, state, and exports, or provide performance guidance. It may not block launch, assign cross-computer ownership, require handoff, create shared leases or write fences, partition features by computer, or control another independently running copy.

Local duplicate protection remains project- and process-scoped on the computer where it runs. A lock or process record created on one computer has no authority over another computer.

### Persistent project and thread identity

Each project keeps one canonical name across successor threads, transfer packages, audits, diagnostics, and release records. Prior names remain searchable aliases, while continuation or branch markers describe the current workstream without fragmenting the project identity. When an interface cannot be renamed, the framework records a truthful suggested title rather than claiming the change occurred.

## Decision flow

```mermaid
flowchart LR
    A[Current evidence] --> B{Sources agree?}
    B -- No --> C[Choose verified baseline]
    B -- Yes --> D[Classify risk]
    C --> D
    D --> E[Plan reversible change]
    E --> F[Validate inputs and environment]
    F --> G[Implement in small batches]
    G --> H[Smoke test and collect evidence]
    H --> I{All release gates pass?}
    I -- No --> J[Block, repair, or roll back]
    I -- Yes --> K[Package, hash, document, release]
```

## Design choices

### Source and version control

Conflicting files are resolved through manifests, checksums, known-good records, and explicit lineage. Older artifacts remain historical until deliberately restored.

### Portability without code drift

One shared package adapts through runtime capability detection and small machine-local overlays. Configuration, logs, state, diagnostics, and temporary files stay local to each installation. Computer identity is descriptive and advisory, never a remote ownership or launch-control mechanism.

### Safe execution

Low-risk local work remains easy to run. High-impact changes require an explicit boundary, a reversible plan, and evidence that the requested input reached the intended behavior.

### Stability and recovery

The framework favors bounded retries, backoff, atomic writes, graceful shutdown, state recovery, local duplicate protection where needed, and a clear first recovery step.

### Verifiable releases

A release is not complete until the source, version, documentation, checks, rights, dependencies, diagnostics, rollback path, and final artifact agree.

## Skills demonstrated

- Information governance and source reconciliation
- Systems analysis and risk classification
- Release engineering and configuration management
- Quality assurance and scenario-based testing
- Windows portability and environment-aware design
- Multi-computer portability without cross-computer restrictions
- Observability, diagnostics, and recovery planning
- Privacy-by-design and controlled public disclosure
- Clear technical communication across complex project states

## Public scope

This case study contains no executable program and does not publish the full operating framework. Machine profiles, raw reports, unique identifiers, credentials, account information, private locations, internal operating instructions, and project-specific live thresholds remain excluded.

See [PUBLIC_SCOPE.md](PUBLIC_SCOPE.md) for the disclosure boundary and [VALIDATION_SUMMARY.json](VALIDATION_SUMMARY.json) for the machine-readable scorecard.

## Release files

| File | Purpose |
|---|---|
| [README.md](README.md) | Case study and design summary |
| [PUBLIC_SCOPE.md](PUBLIC_SCOPE.md) | Public disclosure boundary |
| [VALIDATION_SUMMARY.json](VALIDATION_SUMMARY.json) | Structured validation results and limits |
| [RIGHTS.md](RIGHTS.md) | Rights and reuse terms |
| [MANIFEST.json](MANIFEST.json) | Canonical release inventory and metadata |
| [SHA256SUMS.txt](SHA256SUMS.txt) | File-integrity records |

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not create or replace a software license. No software is distributed in this case study.
