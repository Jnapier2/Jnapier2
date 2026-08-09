#!/usr/bin/env python3
"""Verify the public Reliable Project Delivery Framework release.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASE_DIR = ROOT / "case-studies" / "reliable-project-delivery-framework"
OUTPUT_DIR = Path(os.environ.get("PORTFOLIO_AUDIT_OUTPUT_DIR", ROOT / "audit-output"))
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
CASE_STUDY_VERSION = "1.5.0"
SOURCE_FRAMEWORK_VERSION = "2.17.6"
SOURCE_PACKAGE_SHA256 = "5dd39656afa5e8bcd0159e5ffa163d4de92a9ad4cb05c26aa63acf424ffe371f"
PUBLIC_POLICY_REVISION = "2026-08-09-canonical-entrypoints-project-local-outputs"
SOURCE_PACKAGE_ROLE = (
    "Private exact-source design baseline; ZIP CRC passed, 13 direct manifest file hashes matched, "
    "the two documented manifest self-reference sentinels were present as designed, and the package "
    "SHA-256 is recorded. The public case study exposes outcomes and boundaries, not internal operating text."
)
EXPECTED_FILES = {
    "MANIFEST.json",
    "PUBLIC_SCOPE.md",
    "README.md",
    "RIGHTS.md",
    "SHA256SUMS.txt",
    "VALIDATION_SUMMARY.json",
}
SEALED_FILES = EXPECTED_FILES - {"SHA256SUMS.txt"}
MANIFEST_CONTENT_FILES = SEALED_FILES - {"MANIFEST.json"}


def canonical_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".txt"}:
        return data.replace(b"\r\n", b"\n")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"Reliable Project Delivery Framework integrity failure: {message}")


def require_exact(mapping: dict, key: str, expected: object, context: str) -> None:
    if mapping.get(key) != expected:
        fail(f"{context} changed: {key}")


def main() -> int:
    if not CASE_DIR.is_dir():
        fail("case-study directory is missing")

    actual_files = {path.name for path in CASE_DIR.iterdir() if path.is_file()}
    if actual_files != EXPECTED_FILES:
        fail(f"release inventory differs: {sorted(actual_files ^ EXPECTED_FILES)}")

    manifest = json.loads((CASE_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    require_exact(manifest, "schema_version", 1, "manifest")
    require_exact(manifest, "version", CASE_STUDY_VERSION, "manifest")
    require_exact(manifest, "source_framework_version", SOURCE_FRAMEWORK_VERSION, "manifest")
    require_exact(manifest, "source_package_sha256", SOURCE_PACKAGE_SHA256, "manifest")
    require_exact(manifest, "source_package_role", SOURCE_PACKAGE_ROLE, "manifest")
    require_exact(manifest, "public_policy_revision", PUBLIC_POLICY_REVISION, "manifest")
    require_exact(manifest, "runtime_identity_gate_status", "not_applicable-documentation-only", "manifest")
    require_exact(manifest, "canonical_entrypoint_policy_status", "not_applicable-documentation-only", "manifest")
    require_exact(manifest, "project_local_output_policy_status", "not_applicable-documentation-only", "manifest")
    require_exact(manifest, "rights_notice", RIGHTS_NOTICE, "manifest")
    require_exact(manifest, "data_classification", "public", "manifest")
    require_exact(manifest, "third_party_content", "none included", "manifest")

    records = manifest.get("files")
    if not isinstance(records, list):
        fail("manifest file records are invalid")
    manifest_paths = {str(item.get("path", "")) for item in records if isinstance(item, dict)}
    if manifest_paths != MANIFEST_CONTENT_FILES:
        fail("manifest content inventory differs")
    for item in records:
        path = CASE_DIR / str(item["path"])
        if len(canonical_bytes(path)) != int(item["size_bytes"]):
            fail(f"size mismatch: {path.name}")
        if sha256(path) != str(item["sha256"]):
            fail(f"manifest hash mismatch: {path.name}")

    checksum_records: dict[str, str] = {}
    for raw in (CASE_DIR / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw)
        if not match:
            fail(f"invalid checksum record: {raw!r}")
        digest, name = match.groups()
        if name in checksum_records:
            fail(f"duplicate checksum record: {name}")
        checksum_records[name] = digest
    if set(checksum_records) != SEALED_FILES:
        fail("checksum inventory differs")
    for name, expected in checksum_records.items():
        if sha256(CASE_DIR / name) != expected:
            fail(f"checksum mismatch: {name}")

    summary = json.loads((CASE_DIR / "VALIDATION_SUMMARY.json").read_text(encoding="utf-8"))
    require_exact(summary, "case_study_version", CASE_STUDY_VERSION, "validation summary")
    require_exact(summary, "source_framework_version", SOURCE_FRAMEWORK_VERSION, "validation summary")
    require_exact(summary, "source_package_sha256", SOURCE_PACKAGE_SHA256, "validation summary")
    require_exact(summary, "source_package_role", SOURCE_PACKAGE_ROLE, "validation summary")
    require_exact(summary, "rights_notice", RIGHTS_NOTICE, "validation summary")

    revision = summary.get("public_policy_revision", {})
    require_exact(revision, "id", PUBLIC_POLICY_REVISION, "public policy revision")
    require_exact(
        revision,
        "status",
        "current independent-local-operation, public-evidence, runtime-identity, canonical-entrypoint, and project-local-output language",
        "public policy revision",
    )

    canonical = summary.get("canonical_execution", {})
    require_exact(canonical, "source_policy_status", "current", "canonical execution")
    require_exact(canonical, "case_study_status", "not_applicable-documentation-only", "canonical execution")
    canonical_outcomes = canonical.get("required_outcomes")
    if not isinstance(canonical_outcomes, list):
        fail("canonical execution outcomes are invalid")
    for required in [
        "one short ASCII Windows-safe execution namespace is unique case-insensitively",
        "one stable unversioned project-qualified canonical entrypoint serves people and automation",
        "required fixed legacy or upstream backend names remain behind a thin canonical wrapper",
        "version, build, and date remain in metadata and release archives rather than the normal canonical entrypoint",
    ]:
        if required not in canonical_outcomes:
            fail(f"canonical execution outcome is missing: {required}")

    output = summary.get("project_local_output", {})
    require_exact(output, "source_policy_status", "current", "project-local output")
    require_exact(output, "case_study_status", "not_applicable-documentation-only", "project-local output")
    output_outcomes = output.get("required_outcomes")
    if not isinstance(output_outcomes, list):
        fail("project-local output outcomes are invalid")
    for required in [
        "project root is derived from the canonical launcher or script location rather than caller working directory",
        "generated files stay under project-owned roots by default",
        "temporary work uses same-volume project-local staging, verification, and atomic finalization",
        "Desktop, Documents, Downloads, caller working directory, system temp, drive root, and another project are prohibited as silent fallbacks",
        "external output is explicitly selected or configured, normalized, validated, displayed, and recorded",
        "existing external legacy data is reported and mapped rather than silently moved or deleted",
    ]:
        if required not in output_outcomes:
            fail(f"project-local output outcome is missing: {required}")

    runtime_identity = summary.get("runtime_release_identity", {})
    require_exact(runtime_identity, "source_policy_status", "current", "runtime identity")
    require_exact(runtime_identity, "case_study_status", "not_applicable-documentation-only", "runtime identity")
    require_exact(
        runtime_identity,
        "control_files",
        ["VERSION.txt", "MANIFEST.json", "PACKAGE_METADATA.json"],
        "runtime identity",
    )
    identity_outcomes = runtime_identity.get("required_outcomes")
    if not isinstance(identity_outcomes, list):
        fail("runtime identity outcomes are invalid")
    for required in [
        "every package-managed immutable file is present and SHA-256 verified",
        "same-version mixed or unsafe packages block authenticated/live startup",
    ]:
        if required not in identity_outcomes:
            fail(f"runtime identity outcome is missing: {required}")

    validation = summary.get("validation", {})
    expected_metrics = {
        "source_package_integrity": "pass",
        "public_release_integrity": "manifest-and-checksum-verifiable",
        "control_review": "completed internally; itemized controls are outside public scope",
        "scenario_review": "completed internally; itemized scenarios are outside public scope",
        "document_review": "completed internally",
        "public_metrics": [
            "published file inventory",
            "published file sizes",
            "published SHA-256 checksums",
        ],
    }
    if validation != expected_metrics:
        fail("validation scorecard changed")

    boundary = summary.get("claim_boundary", {})
    expected_boundary_values = {
        "physical_multi_system_verification_claimed": False,
        "shared_coordinator_deployed": False,
        "cross_computer_launch_restrictions_included": False,
        "running_processes_modified": False,
        "executable_included": False,
        "public_release_integrity_verifiable": True,
        "internal_control_counts_published": False,
        "internal_scenario_counts_published": False,
        "runtime_identity_gate_documented": True,
        "runtime_identity_gate_applies_to_case_study": False,
        "canonical_entrypoint_policy_documented": True,
        "canonical_entrypoint_policy_applies_to_case_study": False,
        "project_local_output_policy_documented": True,
        "project_local_output_policy_applies_to_case_study": False,
        "software_control_placeholders_added": False,
    }
    for key, expected in expected_boundary_values.items():
        if boundary.get(key) is not expected:
            fail(f"claim boundary changed: {key}")

    readme = (CASE_DIR / "README.md").read_text(encoding="utf-8")
    required_policy_markers = [
        "every installation independently launchable",
        "may not block launch",
        "Multi-computer portability without cross-computer restrictions",
        "does not present internal totals as independently auditable results",
        "before credentials or authenticated startup",
        "same-version mixed package fails closed",
        "not applicable rather than adding empty software control files",
        "one stable, unversioned, project-qualified entrypoint",
        "version, build, and date belong in metadata and release archives",
        "launcher-derived project root",
        "no silent fallback to Desktop, Documents, Downloads, the caller's working directory, system temp, a drive root, or another project",
        "External output is explicit, validated, visible, and recorded",
    ]
    for marker in required_policy_markers:
        if marker not in readme:
            fail(f"README does not contain the required policy marker: {marker}")

    forbidden_policy_markers = [
        "single active writer across the fleet",
        "cross-computer ownership and clean-handoff design",
        "chatgpt_new_thread_parameters",
        "successor threads",
        "interface cannot be renamed",
        "26 / 26",
        "40 / 40",
        "20 / 20",
    ]
    for marker in forbidden_policy_markers:
        if marker in readme:
            fail(f"README retains retired or private policy language: {marker}")

    for name in EXPECTED_FILES:
        if name != "SHA256SUMS.txt" and name not in readme:
            fail(f"README does not reference {name}")

    public_scope = (CASE_DIR / "PUBLIC_SCOPE.md").read_text(encoding="utf-8")
    for marker in [
        "Project-specific execution namespaces, entrypoint aliases, backend targets, output-root maps, and migration shims",
        "empty `VERSION.txt`, `PACKAGE_METADATA.json`, launcher, or output-folder placeholders are intentionally not added",
        "rename a working backend",
        "move legacy data",
    ]:
        if marker not in public_scope:
            fail(f"PUBLIC_SCOPE does not contain the required boundary: {marker}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "case_study": "Reliable Project Delivery Framework",
        "case_study_version": CASE_STUDY_VERSION,
        "source_framework_version": SOURCE_FRAMEWORK_VERSION,
        "source_package_sha256": SOURCE_PACKAGE_SHA256,
        "public_policy_revision": PUBLIC_POLICY_REVISION,
        "runtime_identity_gate_status": "not_applicable-documentation-only",
        "canonical_entrypoint_policy_status": "not_applicable-documentation-only",
        "project_local_output_policy_status": "not_applicable-documentation-only",
        "files_verified": len(SEALED_FILES),
        "manifest_records_verified": len(records),
        "validation_scope": expected_metrics,
        "result": "PASS",
        "rights_notice": RIGHTS_NOTICE,
    }
    (OUTPUT_DIR / "reliable-project-delivery-framework-integrity.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        "Reliable Project Delivery Framework integrity: PASS "
        f"({len(SEALED_FILES)} sealed files, {len(records)} manifest records, "
        "runtime identity, canonical entrypoint, and project-local output N/A for documentation-only release)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
