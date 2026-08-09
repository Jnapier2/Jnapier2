# Reliable Project Delivery Framework

[![Portfolio health](https://github.com/Jnapier2/Jnapier2/actions/workflows/profile-contract.yml/badge.svg)](https://github.com/Jnapier2/Jnapier2/actions/workflows/profile-contract.yml)

A repeatable control framework for moving complex software projects from uncertain inputs to verified, portable releases while preserving rollback, privacy, operator control, stable automation entrypoints, project-local outputs, and independent local operation.

## Why I built it

Complex projects often fail for ordinary reasons: multiple “final” versions, machine-specific paths, generic launchers, mixed-release folders, output written to unexpected locations, missing rollback evidence, unbounded diagnostics, unclear responsibility, and changes that cannot be proven safe. I designed this framework to turn those risks into explicit decisions, tests, and release evidence.

## What it does

- Selects a verified working baseline when source packages conflict.
- Keeps one shared package portable across distinct Windows environments.
- Uses capability detection and optional computer recognition for helpful local labels, paths, defaults, diagnostics, and performance guidance.
- Keeps every installation independently launchable; local process locks and duplicate protection never block another computer.
- Preserves one canonical project name and searchable aliases across releases, handoffs, and project branches.
- Gives each first-party project one stable execution namespace and one stable, unversioned, project-qualified entrypoint for people and automation.
- Namespaces first-party helpers while preserving required legacy or upstream backend filenames behind a thin wrapper.
- Keeps generated configuration, logs, state, temporary data, exports, diagnostics, reports, downloads, backups, and release output under the launcher-derived project root by default.
- Allows an external output destination only when it is explicitly selected, normalized, validated, visible, and recorded.
- Separates reversible local work from destructive, live-financial, credential, administrator, security, public, and bulk-write actions.
- Requires critical inputs to be recognized, validated, mapped, exercised, and confirmed.
- For released software, verifies running release identity and immutable package-managed files before credentials or authenticated startup; a same-version mixed package fails closed.
- Keeps local status, repair guidance, and bounded support evidence available after an identity block without silently rewriting release files.
- Produces bounded, redacted diagnostic packages that retain the most useful evidence.
- Preserves known-good state, rollback instructions, version history, rights metadata, dependency records, and checksums.
- Blocks release when source, validation, identity, output, entrypoint, or recovery evidence is incomplete.

## Public evidence

The public case study favors evidence a reviewer can inspect directly instead of presenting internal aggregate scores as stand-alone proof.

| Evidence | What a reviewer can verify |
|---|---|
| Source baseline | `MANIFEST.json` and `VALIDATION_SUMMARY.json` identify the reviewed source-framework version and exact package SHA-256 |
| Release inventory | Every published case-study file is declared in `MANIFEST.json` |
| File integrity | Published sizes and SHA-256 values are recorded in `MANIFEST.json` and `SHA256SUMS.txt` |
| Runtime-identity boundary | `VALIDATION_SUMMARY.json` records the software-release gate and marks this documentation-only release not applicable |
| Entry/output boundary | `VALIDATION_SUMMARY.json` records the canonical-entrypoint and project-local-output policies and marks this documentation-only release not applicable to runtime execution |
| Disclosure boundary | `PUBLIC_SCOPE.md` identifies what is included, withheld, and intentionally not claimed |

The private design baseline was reviewed for coverage, conflict handling, and consistency. Its itemized controls and scenario set are outside the public release, so this case study does not present internal totals as independently auditable results.

## Current operating policy

### Independent local operation across multiple computers

Each installation runs independently. Computer recognition may improve diagnostic labels, choose sensible local paths and defaults, organize local logs, state, and exports, or provide performance guidance. It may not block launch, assign cross-computer ownership, require a remote handoff, create shared leases or write fences, partition features by computer, or control another independently running copy.

Local duplicate protection remains project- and process-scoped on the computer where it runs. A lock or process record created on one computer has no authority over another computer.

### Persistent project and release identity

Each project keeps one canonical name across successor releases, transfer packages, audits, diagnostics, and release records. Prior names remain searchable aliases, while continuation or branch markers describe the current workstream without fragmenting project identity.

### Canonical execution namespace and entrypoint

Each first-party project uses one short, ASCII, Windows-safe execution namespace that is unique case-insensitively. It exposes one stable, unversioned, project-qualified entrypoint for routine launch and automation. First-party helpers use the same namespace instead of generic names such as `run`, `start`, `launch`, `main`, `app`, `bot`, or `menu`.

A required fixed legacy or third-party backend filename may remain unchanged behind the canonical wrapper. A deliberate entrypoint rename requires a migration map, a forwarding shim or approved alias when safe, a deprecation/removal version, and no duplicated launcher logic. The version, build, and date belong in metadata and release archives, not the normal canonical entrypoint.

### Project-local outputs

The project root is resolved from the canonical launcher or script location rather than from the caller's current working directory. Generated files default to project-owned folders such as `config`, `logs`, `state`, `temp`, `cache`, `exports`, `diagnostics`, `reports`, `downloads`, `backups`, and `releases`.

Temporary work stays on the same volume under project-local `temp`, is verified, and is atomically finalized under the intended project folder. There is no silent fallback to Desktop, Documents, Downloads, the caller's working directory, system temp, a drive root, or another project. External output is explicit, validated, visible, and recorded. Existing external legacy data is reported and mapped rather than silently moved or deleted.

### Runtime release identity before authenticated startup

Released software establishes its local root and logging first, then performs a read-only identity check before credentials or authenticated startup. The running version and build must agree with the package control metadata, and every immutable file declared as package-managed must be present and SHA-256 correct. Duplicate, absolute, escaping, out-of-root, missing, size-mismatched, or hash-mismatched managed paths block authenticated or live startup even when the visible version labels match.

Mutable configuration, secrets, logs, state, caches, exports, and user data remain outside the immutable release set. A blocked package may still expose local status, repair guidance, and redacted support evidence, but verification does not silently repair or rewrite the package. Documentation-only releases such as this case study mark the runtime gate not applicable rather than adding empty software control files.

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
    G --> H[Smoke test entrypoint, outputs, and recovery]
    H --> I{All release gates pass?}
    I -- No --> J[Block, repair, or roll back]
    I -- Yes --> K[Package, hash, document, release]
```

## Design choices

### Source and version control

Conflicting files are resolved through manifests, checksums, known-good records, and explicit lineage. Older artifacts remain historical until deliberately restored.

### Portability without code drift

One shared package adapts through runtime capability detection and small machine-local overlays. Configuration, logs, state, diagnostics, temporary files, and outputs stay local to each installation. Computer identity is descriptive and advisory, never a remote ownership or launch-control mechanism.

### Stable automation without generic launcher collisions

A project-qualified canonical entrypoint stays stable across compatible releases, while package archives carry version and date. Namespaced helpers reduce collisions when many projects share one computer. Legacy backends remain reachable through thin wrappers instead of risky bulk renames.

### Output containment and relocation safety

Launchers derive the project root from their own location, so shortcuts and alternate working directories do not redirect output. Project-local same-volume staging supports atomic finalization. Explicit external destinations remain possible but cannot be silently inferred.

### Safe execution

Low-risk local work remains easy to run. High-impact changes require an explicit boundary, a reversible plan, and evidence that the requested input reached the intended behavior.

### Stability and recovery

The framework favors bounded retries, backoff, atomic writes, graceful shutdown, state recovery, local duplicate protection where needed, and a clear first recovery step.

### Verifiable releases

A release is not complete until the source, running/package identity when applicable, canonical entrypoint, effective output roots, version, documentation, checks, rights, dependencies, diagnostics, rollback path, and final artifact agree. For authenticated software, managed-file verification is part of startup trust rather than only a packaging-time check.

## Skills demonstrated

- Information governance and source reconciliation
- Systems analysis and risk classification
- Release engineering and configuration management
- Runtime identity and mixed-release integrity control
- Canonical entrypoint and automation interface governance
- Project-local output containment and relocation-safe path design
- Quality assurance and scenario-based testing
- Windows portability and environment-aware design
- Multi-computer portability without cross-computer restrictions
- Observability, diagnostics, and recovery planning
- Privacy-by-design and controlled public disclosure
- Clear technical communication across complex project states

## Public scope

This case study contains no executable program and does not publish the complete implementation playbook. Machine profiles, raw reports, unique identifiers, credentials, account information, private locations, project-specific execution namespaces, private output roots, internal operating instructions, project-specific authenticated endpoints, and live thresholds remain excluded.

See [PUBLIC_SCOPE.md](PUBLIC_SCOPE.md) for the disclosure boundary and [VALIDATION_SUMMARY.json](VALIDATION_SUMMARY.json) for the machine-readable verification scope.

## Release files

| File | Purpose |
|---|---|
| [README.md](README.md) | Case study and design summary |
| [PUBLIC_SCOPE.md](PUBLIC_SCOPE.md) | Public disclosure boundary |
| [VALIDATION_SUMMARY.json](VALIDATION_SUMMARY.json) | Structured validation scope and limits |
| [RIGHTS.md](RIGHTS.md) | Rights and reuse terms |
| [MANIFEST.json](MANIFEST.json) | Canonical release inventory and metadata |
| [SHA256SUMS.txt](SHA256SUMS.txt) | File-integrity records |

Copyright © 2026 Gateway Information Group LLC. All rights reserved.

This notice does not create or replace a software license. No software is distributed in this case study.
