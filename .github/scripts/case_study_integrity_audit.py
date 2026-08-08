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
CASE_STUDY_VERSION = "1.4.0"
SOURCE_FRAMEWORK_VERSION = "2.17.5"
SOURCE_PACKAGE_SHA256 = "655564a81adeff17ddad1e33b1453ae64bde0f405a41e740e3b3a7f65934d2e0"
PUBLIC_POLICY_REVISION = "2026-08-07-runtime-release-identity-integrity"
SOURCE_PACKAGE_ROLE = (
    "Private exact-source design baseline; ZIP CRC and all 15 internal manifest file size/hash checks "
    "passed, and the package SHA-256 is recorded. The public case study exposes outcomes and boundaries, "
    "not internal operating text."
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
    """Return repository-canonical bytes for sealed text files.

    Git may check text files out with CRLF on Windows while storing LF in the
    repository. The release manifest records the repository bytes, so local
    verification normalizes that checkout-only difference.
    """
    data = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".txt"}:
        return data.replace(b"\r\n", b"\n")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"Reliable Project Delivery Framework integrity failure: {message}")


def main() -> int:
    if not CASE_DIR.is_dir():
        fail("case-study directory is missing")
    actual_files = {path.name for path in CASE_DIR.iterdir() if path.is_file()}
    if actual_files != EXPECTED_FILES:
        fail(f"release inventory differs: {sorted(actual_files ^ EXPECTED_FILES)}")

    manifest = json.loads((CASE_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("version") != CASE_STUDY_VERSION:
        fail("manifest identity is invalid")
    if manifest.get("source_framework_version") != SOURCE_FRAMEWORK_VERSION:
        fail("source framework version is invalid")
    if manifest.get("source_package_sha256") != SOURCE_PACKAGE_SHA256:
        fail("source package SHA-256 is invalid")
    if manifest.get("source_package_role") != SOURCE_PACKAGE_ROLE:
        fail("source package role is invalid")
    if manifest.get("public_policy_revision") != PUBLIC_POLICY_REVISION:
        fail("public policy revision is invalid")
    if manifest.get("runtime_identity_gate_status") != "not_applicable-documentation-only":
        fail("documentation-only runtime identity status is invalid")
    if manifest.get("rights_notice") != RIGHTS_NOTICE:
        fail("canonical rights notice is missing from the manifest")
    if manifest.get("data_classification") != "public":
        fail("manifest data classification is not public")
    if manifest.get("third_party_content") != "none included":
        fail("third-party content declaration changed")

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
    if summary.get("case_study_version") != CASE_STUDY_VERSION:
        fail("validation summary case-study version changed")
    if summary.get("source_framework_version") != SOURCE_FRAMEWORK_VERSION:
        fail("validation summary source version changed")
    if summary.get("source_package_sha256") != SOURCE_PACKAGE_SHA256:
        fail("validation summary source package hash changed")
    if summary.get("source_package_role") != SOURCE_PACKAGE_ROLE:
        fail("validation summary source package role changed")

    revision = summary.get("public_policy_revision", {})
    if revision.get("id") != PUBLIC_POLICY_REVISION:
        fail("validation summary policy revision changed")
    if revision.get("status") != (
        "current independent-local-operation, public-evidence, and runtime-identity language"
    ):
        fail("validation summary policy status changed")

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
    required_outcomes = runtime_identity.get("required_outcomes")
    if not isinstance(required_outcomes, list) or (
        "every package-managed immutable file is present and SHA-256 verified"
        not in required_outcomes
    ):
        fail("managed-file integrity outcome is missing")
    if (
        "same-version mixed or unsafe packages block authenticated/live startup"
        not in required_outcomes
    ):
        fail("mixed-release block outcome is missing")

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
        "software_control_placeholders_added": False,
    }
    for key, expected in expected_boundary_values.items():
        if boundary.get(key) is not expected:
            fail(f"claim boundary changed: {key}")
    if summary.get("rights_notice") != RIGHTS_NOTICE:
        fail("validation summary rights notice changed")

    readme = (CASE_DIR / "README.md").read_text(encoding="utf-8")
    required_policy_markers = [
        "every installation independently launchable",
        "may not block launch",
        "Multi-computer portability without cross-computer restrictions",
        "does not present internal totals as independently auditable results",
        "before credentials or authenticated startup",
        "same-version mixed package fails closed",
        "not applicable rather than adding empty software control files",
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
        "runtime identity N/A for documentation-only release)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
