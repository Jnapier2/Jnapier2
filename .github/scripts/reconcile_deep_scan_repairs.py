from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
RIGHTS = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
GENERATED_UTC = "2026-08-11T03:58:00Z"
RECONCILED_CDT = "August 10, 2026 at 10:58 PM CDT"
MEDIA_HEAD = "22fd78f6aa89e91c17cca3699af6602751d32b32"
NETLOSS_HEAD = "7008d3c5c65638d39ccc39569ece6b1b0d15df44"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label} marker, found {count}: {old!r}")
    return text.replace(old, new, 1)


def patch_machine_ledger() -> None:
    path = ROOT / ".github" / "release-reconciliation.json"
    payload = json.loads(read_text(path))
    payload["generated_utc"] = GENERATED_UTC
    payload["review_scope"] = (
        "All 17 public project default-branch heads, declared version markers, release and dependency integrity, "
        "public documentation, review-only dependency monitoring, Python support claims, timeout defaults, "
        "source-versus-download distinctions, recovered-package provenance, the MediaTaggerBot v2.17.6 "
        "metadata repair, the NetLossDoctor collector/comparison project-local-output repairs, and a bounded "
        "18-repository source-signal scan; account-level About links, pins, rulesets, and Drive permissions are "
        "tracked separately."
    )
    projects = payload.get("projects")
    if not isinstance(projects, list):
        raise SystemExit("Machine ledger project list is missing")
    by_repo = {item.get("repository"): item for item in projects if isinstance(item, dict)}
    if set(("media-tagger-bot", "net-loss-doctor")) - set(by_repo):
        raise SystemExit("Expected repair projects are missing from the machine ledger")

    media = by_repo["media-tagger-bot"]
    media["note"] = (
        "The sanitized v0.5.9 source implements the v2.17.6 execution/output boundary without changing "
        "user-facing behavior. `Start_MediaTaggerBot.bat` remains the stable project-qualified entrypoint, "
        "caller CWD is not project-root authority, runtime-owned outputs are project-local, and external media "
        "roots remain explicit user bindings. The metadata repair now labels the source baseline as a Git SHA-1 "
        "commit instead of SHA-256. The clean-checkout identity gate verifies 92/92 managed files with zero "
        "mismatches, and the complete 197-test Python 3.11/3.13 PR matrix passed."
    )
    media["reviewed_head_sha"] = MEDIA_HEAD

    netloss = by_repo["net-loss-doctor"]
    netloss["note"] = (
        "The v2.10.0 public source now uses `Start-NetLossDoctor.cmd` as the stable entrypoint, resolves collector "
        "and comparison roots from validated NLD_HOME or their own script locations, rebases relative report "
        "paths under the project, and fails closed rather than using caller CWD, Desktop, or OS temp as final "
        "output authority. Windows PowerShell 5.1 safety contracts and both cross-working-directory tests passed. "
        "PUBLIC_SOURCE_METADATA.json explicitly records that the older public source has not yet implemented the "
        "v2.17.5 managed-file runtime identity gate."
    )
    netloss["reviewed_head_sha"] = NETLOSS_HEAD

    if len(projects) != int(payload.get("reviewed_public_project_count", -1)):
        raise SystemExit("Machine ledger project count changed")
    if payload.get("rights_notice") != RIGHTS:
        raise SystemExit("Machine ledger rights notice changed")
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def patch_human_ledger() -> None:
    path = ROOT / "RELEASE_RECONCILIATION.md"
    text = read_text(path)
    text = replace_once(
        text,
        "Project heads last reconciled: **August 9, 2026 at 4:31 PM CDT**",
        f"Project heads last reconciled: **{RECONCILED_CDT}**",
        "project-head timestamp",
    )

    framework_paragraph = (
        "The profile case study **Reliable Project Delivery Framework v1.5.0** presents the current **v2.17.6** "
        "operating baseline as a concise, inspectable example of release discipline. It preserves the v2.17.5 "
        "fail-closed runtime release-identity boundary and adds unique execution namespaces, one stable unversioned "
        "project-qualified canonical entrypoint, launcher-derived project roots, and project-local output "
        "containment. The documentation-only case study records executable implementation as project-specific and "
        "does not claim that all public runtimes have already completed migration.\n"
    )
    deep_scan_paragraph = framework_paragraph + (
        "\nA bounded deep scan cloned all 18 expected public repositories and reviewed entrypoint, root, output, "
        "runtime-identity, personal-path, and secret-like source signals. Manual triage of every high/critical "
        "snippet found no embedded literal secret or personal absolute path. It did identify two actionable "
        "conflicts: MediaTaggerBot mislabeled a Git commit SHA-1 as SHA-256, and NetLossDoctor retained "
        "caller-CWD/Desktop/OS-temp output fallbacks in its collector or comparison path. Both repairs passed "
        "their native hosted checks before merge. Remaining missing public metadata or runtime-identity controls "
        "are recorded as project-specific migration gaps rather than silently treated as complete.\n"
    )
    text = replace_once(text, framework_paragraph, deep_scan_paragraph, "framework paragraph")

    text = replace_once(
        text,
        "| MediaTaggerBot | 0.5.9 | 0.5.9 | `79e95bff` | Current v2.17.6-aligned source; stable entrypoint, launcher-derived root, project-local outputs, 108-file identity gate, and Python 3.11/3.13 matrices verified |",
        "| MediaTaggerBot | 0.5.9 | 0.5.9 | `22fd78f6` | Current v2.17.6-aligned source; corrected Git-hash metadata, stable entrypoint, project-local outputs, 92-file identity gate, and 197-test Python 3.11/3.13 matrices verified |",
        "MediaTaggerBot table row",
    )
    text = replace_once(
        text,
        "| NetLossDoctor | 2.10.0 | 2.10.0 | `8252dbb6` | Current; diagnostic bounds and load context are not certified line-speed measurements |",
        "| NetLossDoctor | 2.10.0 | 2.10.0 | `7008d3c5` | Current v2.17.6 output hardening; collector and comparison outputs are project-rooted and fail closed, while runtime managed-file identity remains explicitly unimplemented |",
        "NetLossDoctor table row",
    )

    old_media = (
        "- **MediaTaggerBot 0.5.9:** the v2.17.6 repair removed the caller-CWD project-root fallback while preserving "
        "`Start_MediaTaggerBot.bat` as the stable canonical launcher and keeping all runtime-owned outputs beneath "
        "the launcher-derived project root. Package metadata now records the execution namespace, backend target, "
        "output roots, explicit external media-root boundary, historical-launcher treatment, and cross-working-directory "
        "acceptance. The release manifests were regenerated and then corrected to hash Git-normalized LF bytes; the "
        "clean-checkout runtime identity gate verifies 108/108 managed files with zero mismatches. The final PR matrix "
        "passed 197 tests on both Python 3.11 and 3.13. User-facing version and media-processing behavior remain v0.5.9.\n"
    )
    new_media = (
        "- **MediaTaggerBot 0.5.9:** the v2.17.6 repair removed caller-CWD project-root authority while preserving "
        "`Start_MediaTaggerBot.bat` as the stable canonical launcher and keeping runtime-owned outputs beneath the "
        "launcher-derived project root. The follow-up metadata repair replaced a misleading `source_baseline_sha256` "
        "key, which held a 40-character Git SHA-1, with an explicit commit-SHA field and algorithm label; it also "
        "reconciled the current parameter digest and release-note ordering. The clean-checkout runtime identity gate "
        "verifies 92/92 managed files with zero mismatches, and the final 197-test matrix passed on Python 3.11 and "
        "3.13. User-facing version, dependencies, and media-processing behavior remain v0.5.9.\n"
    )
    text = replace_once(text, old_media, new_media, "MediaTaggerBot completed-reconciliation bullet")

    netloss_bullet = (
        "- **NetLossDoctor 2.10.0:** two v2.17.6 path-containment repairs preserve the read-only diagnostic behavior "
        "while removing caller working directory, Desktop, and operating-system temporary storage as final-output "
        "fallbacks. `Start-NetLossDoctor.cmd` remains the stable entrypoint; the collector and "
        "`Compare-NetLossDoctorReports.ps1` resolve from validated `NLD_HOME` or their own script locations, rebase "
        "relative report roots under the project, and fail closed on creation errors. Windows PowerShell 5.1 parsing, "
        "redaction and cleanup contracts, collector and comparison cross-working-directory tests, and both PR checks "
        "passed. The public metadata explicitly states that v2.17.5 managed-file startup verification is not yet "
        "implemented in this older public source tree.\n"
    )
    chicago_marker = "- **Chicago Food Inspection Outcomes:** Matplotlib 3.11.1 passed binary installation"
    if chicago_marker not in text:
        raise SystemExit("Chicago reconciliation marker was not found")
    text = text.replace(chicago_marker, netloss_bullet + chicago_marker, 1)

    old_final = (
        "There are no active public source-promotion branches after the recorded project-head pass. Beta Earth "
        "remains blocked because its exact v0.5.0 archive is unavailable; [Large Text Chunker issue #3]"
    )
    new_final = (
        "There are no unresolved public source-promotion pull requests from this repair pass. Temporary audit branches "
        "are evidence-only and are not source authority. Beta Earth remains blocked because its exact v0.5.0 archive "
        "is unavailable; [Large Text Chunker issue #3]"
    )
    text = replace_once(text, old_final, new_final, "final branch-status paragraph")

    if not text.rstrip().endswith(
        "This notice does not replace or infer a software license. Third-party components retain their respective notices and licenses."
    ):
        raise SystemExit("Human ledger final notice changed")
    write_text(path, text)


def main() -> int:
    patch_machine_ledger()
    patch_human_ledger()
    print(json.dumps({
        "generated_utc": GENERATED_UTC,
        "media_tagger_head": MEDIA_HEAD,
        "net_loss_doctor_head": NETLOSS_HEAD,
        "reconciled_cdt": RECONCILED_CDT,
        "rights_notice": RIGHTS,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
