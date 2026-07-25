#!/usr/bin/env python3
"""Verify the public Reliable Project Delivery Framework release.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASE_DIR = ROOT / "case-studies" / "reliable-project-delivery-framework"
OUTPUT_DIR = ROOT / "audit-output"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
CASE_STUDY_VERSION = "1.1.0"
SOURCE_FRAMEWORK_VERSION = "2.17.2"
SOURCE_PACKAGE_SHA256 = "e0615823cfde6ae6eff6d4c028a6f2f1f54d251df90bd64f3cad8a6475b6d1d6"
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        if path.stat().st_size != int(item["size_bytes"]):
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
    validation = summary.get("validation", {})
    expected_metrics = {
        "release_package_files": 15,
        "zip_integrity": "pass",
        "control_areas": {"passed": 26, "total": 26},
        "scenario_simulations": {"passed": 40, "total": 40},
        "negative_conflict_checks": {"passed": 20, "total": 20},
        "docx_render": {"pages": 11, "visual_review": "pass"},
        "docx_accessibility": {"high": 0, "medium": 0, "low": 0},
    }
    if validation != expected_metrics:
        fail("validation scorecard changed")
    boundary = summary.get("claim_boundary", {})
    if boundary.get("physical_multi_system_verification_claimed") is not False:
        fail("physical verification is being overclaimed")
    if boundary.get("shared_coordinator_deployed") is not False:
        fail("shared-coordinator deployment is being overclaimed")
    if boundary.get("running_processes_modified") is not False:
        fail("running-process modification is being overclaimed")
    if boundary.get("executable_included") is not False:
        fail("executable-content boundary changed")
    if summary.get("rights_notice") != RIGHTS_NOTICE:
        fail("validation summary rights notice changed")

    readme = (CASE_DIR / "README.md").read_text(encoding="utf-8")
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
        "files_verified": len(SEALED_FILES),
        "manifest_records_verified": len(records),
        "validation_scorecard": expected_metrics,
        "result": "PASS",
        "rights_notice": RIGHTS_NOTICE,
    }
    (OUTPUT_DIR / "reliable-project-delivery-framework-integrity.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        "Reliable Project Delivery Framework integrity: PASS "
        f"({len(SEALED_FILES)} sealed files, {len(records)} manifest records)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
