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
ROLLBACK_FRAMEWORK_VERSION = "2.17.5"
ROLLBACK_PACKAGE_SHA256 = "655564a81adeff17ddad1e33b1453ae64bde0f405a41e740e3b3a7f65934d2e0"
PUBLIC_POLICY_REVISION = "2026-08-09-canonical-entrypoints-project-local-outputs"
SOURCE_PACKAGE_ROLE = (
    "Private exact-source design baseline; ZIP CRC and all 15 internal manifest file size/hash "
    "checks passed, the deterministic rebuild matched, and the package SHA-256 is recorded. "
    "The public case study exposes outcomes and boundaries, not internal operating text."
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


def require_list_contains(container: object, required: set[str], label: str) -> None:
    if not isinstance(container, list):
        fail(f"{label} is not a list")
    values = {str(item) for item in container}
    missing = sorted(required - values)
    if missing:
        fail(f"{label} is missing: {missing}")


def main() -> int:
    if not CASE_DIR.is_dir():
        fail("case-study directory is missing")
    actual_files = {path.name for path in CASE_DIR.iterdir() if path.is_file()}
    if actual_files != EXPECTED_FILES:
        fail(f"release inventory differs: {sorted(actual_files ^ EXPECTED_FILES)}")

    manifest = json.loads((CASE_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    exact_manifest_values = {
        "schema_version": 1,
        "version": CASE_STUDY_VERSION,
        "source_framework_version": SOURCE_FRAMEWORK_VERSION,
        "source_package_sha256": SOURCE_PACKAGE_SHA256,
        "source_package_role": SOURCE_PACKAGE_ROLE,
        "rollback_source_framework_version": ROLLBACK_FRAMEWORK_VERSION,
        "rollback_source_package_sha256": ROLLBACK_PACKAGE_SHA256,
        "public_policy_revision": PUBLIC_POLICY_REVISION,
        "data_classification": "public",
        "runtime_identity_gate_status": "not_applicable-documentation-only",
        "execution_identity_policy_status": "documented-project-specific-implementation",
        "project_local_output_policy_status": "documented-project-specific-implementation",
        "rights_notice": RIGHTS_NOTICE,
        "third_party_content": "none included",
    }
    for key, expected in exact_manifest_values.items():
        if manifest.get(key) != expected:
            fail(f"manifest value changed: {key}")

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
    exact_summary_values = {
        "case_study_version": CASE_STUDY_VERSION,
        "source_framework_version": SOURCE_FRAMEWORK_VERSION,
        "source_package_sha256": SOURCE_PACKAGE_SHA256,
        "source_package_role": SOURCE_PACKAGE_ROLE,
        "rollback_source_framework_version": ROLLBACK_FRAMEWORK_VERSION,
        "rollback_source_package_sha256": ROLLBACK_PACKAGE_SHA256,
        "rights_notice": RIGHTS_NOTICE,
    }
    for key, expected in exact_summary_values.items():
        if summary.get(key) != expected:
            fail(f"validation summary value changed: {key}")

    revision = summary.get("public_policy_revision", {})
    if revision.get("id") != PUBLIC_POLICY_REVISION:
        fail("validation summary policy revision changed")
    if revision.get("status") != (
        "current independent-local-operation, runtime-identity, canonical-entrypoint, "
        "and project-local-output language"
    ):
        fail("validation summary policy status changed")

    execution_identity = summary.get("execution_identity", {})
    if execution_identity.get("source_policy_status") != "current":
        fail("execution identity policy is not current")
    if execution_identity.get("case_study_status") != "documented-policy-project-specific-implementation":
        fail("execution identity case-study boundary changed")
    require_list_contains(
        execution_identity.get("required_outcomes"),
        {
            "each first-party project has a case-insensitively unique execution namespace",
            "one stable unversioned project-qualified canonical entrypoint is recorded",
            "canonical launch files are included in the immutable managed-file inventory for executable releases",
        },
        "execution identity outcomes",
    )

    local_outputs = summary.get("project_local_outputs", {})
    if local_outputs.get("source_policy_status") != "current":
        fail("project-local output policy is not current")
    if local_outputs.get("case_study_status") != "documented-policy-project-specific-implementation":
        fail("project-local output case-study boundary changed")
    require_list_contains(
        local_outputs.get("required_outcomes"),
        {
            "project root resolves from the canonical launcher or script location rather than caller current working directory",
            "runtime-owned configuration, logs, state, temp, caches, exports, diagnostics, reports, downloads, backups, and release evidence default beneath project root",
            "smoke tests launch from another working directory and verify project-local output containment",
        },
        "project-local output outcomes",
    )

    runtime_identity = summary.get("runtime_release_identity", {})
    if runtime_identity.get("source_policy_status") != "current":
        fail("runtime identity policy is not current")
    if runtime_identity.get("case_study_status") != "not_applicable-documentation-only":
        fail("documentation-only runtime identity boundary changed")
    if runtime_identity.get("control_files") != [
        "VERSION.txt",
        "MANIFEST.json",
        "PACKAGE_METADATA.json",
    ]:
        fail("runtime identity control-file contract changed")
    require_list_contains(
        runtime_identity.get("required_outcomes"),
        {
            "every package-managed immutable file is present and SHA-256 verified",
            "same-version mixed or unsafe packages block authenticated/live startup",
        },
        "runtime identity outcomes",
    )

    validation = summary.get("validation", {})
    if validation.get("source_package_integrity") != "pass":
        fail("source package integrity is not pass")
    if validation.get("source_package_manifest_records_verified") != 15:
        fail("source manifest record count changed")
    if validation.get("source_package_deterministic_rebuild") != "pass":
        fail("source deterministic rebuild status changed")
    if validation.get("public_release_integrity") != "manifest-and-checksum-verifiable":
        fail("public release integrity status changed")

    boundary = summary.get("claim_boundary", {})
    exact_boundary_values = {
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
        "execution_identity_policy_documented": True,
        "execution_identity_applies_to_case_study": False,
        "project_local_output_policy_documented": True,
        "project_local_output_policy_applies_to_case_study": False,
        "portfolio_wide_runtime_migration_claimed": False,
        "software_control_placeholders_added": False,
    }
    for key, expected in exact_boundary_values.items():
        if boundary.get(key) is not expected:
            fail(f"claim boundary changed: {key}")

    readme = (CASE_DIR / "README.md").read_text(encoding="utf-8")
    required_policy_markers = [
        "every installation independently launchable",
        "may not block launch",
        "stable, unversioned, and project-qualified",
        "never from the caller’s current working directory",
        "launching from a different working directory",
        "before credentials or authenticated startup",
        "same-version mixed package fails closed",
        "not applicable rather than adding empty software control files",
        "does not present internal totals as independently auditable results",
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

    scope = (CASE_DIR / "PUBLIC_SCOPE.md").read_text(encoding="utf-8")
    for marker in [
        "canonical-entrypoint",
        "Project-root resolution from the launcher or script location",
        "Project-local output containment",
        "does not claim that every public project has already completed",
    ]:
        if marker not in scope:
            fail(f"PUBLIC_SCOPE.md is missing: {marker}")

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
        "execution_identity_policy_status": "documented-project-specific-implementation",
        "project_local_output_policy_status": "documented-project-specific-implementation",
        "files_verified": len(SEALED_FILES),
        "manifest_records_verified": len(records),
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
        "v2.17.6 canonical-entrypoint/project-local-output policy documented)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
