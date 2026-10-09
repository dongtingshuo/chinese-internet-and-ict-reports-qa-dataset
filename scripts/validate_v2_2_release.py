#!/usr/bin/env python3
"""Validate the canonical active v2.2.0 Gold release and write integrity metadata."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.2.0"
EXPECTED = 2355
BASE_COUNT = 2508
EXPECTED_SPLITS = {"TRAIN": 1573, "DEV": 372, "TEST": 410}
BASE = ROOT / "history/v2.1.0"
BASE_RECORD_SHA = "e7b35f1ef9068f92072598307aa00edd61882f8f8750632741429a66ffa0a014"
BASE_SPLIT_SHA = "9636e14c406eff5379bdddceb98a9625a3d4ec20661229c47ea42580a8f1285d"
CORE_FILES = [
    "README.md", "README.zh-CN.md", "CITATION.cff", "CITATION.md", "DATA_CARD.md",
    "DATA_STATEMENT.md", "ATTRIBUTION.md", "LICENSE", "LICENSES.md", "LICENSE_STATUS.md",
    "SPLIT_POLICY.md", "GOLD_STANDARD.md", "GOLD_SELECTION_REPORT.json", "records.jsonl",
    "split_assignments.jsonl", "sources.json", "schema.json", "release_metadata.json",
    "VALIDATION_REPORT.json", "audit/v2_2/RELEASE_AUDIT.json", "audit/v2_2/RELEASE_AUDIT.md",
    "scripts/validate_v2_2_release.py",
    "data/gold/train.jsonl", "data/gold/validation.jsonl", "data/gold/test.jsonl",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", re.sub(r"[，。！？；：、,.!?;:'\"（）()【】\[\]{}—–-]+", "", text)).casefold()


def main() -> None:
    issues: list[str] = []
    records_path = ROOT / "records.jsonl"
    split_path = ROOT / "split_assignments.jsonl"
    records = read_jsonl(records_path)
    assignments = read_jsonl(split_path)
    ids = [r.get("query_id") for r in records]
    if len(records) != EXPECTED:
        issues.append(f"record_count:{len(records)}")
    if len(ids) != len(set(ids)):
        issues.append("duplicate_query_id")
    by_id = {r["query_id"]: r for r in records if r.get("query_id")}
    if len(assignments) != EXPECTED or {r.get("query_id") for r in assignments} != set(by_id):
        issues.append("split_assignment_coverage_mismatch")
    split_by_id = {r.get("query_id"): r.get("split") for r in assignments}
    split_counts = dict(Counter(split_by_id.values()))
    if split_counts != EXPECTED_SPLITS:
        issues.append(f"split_counts:{split_counts}")
    if any(by_id[qid].get("split") != split for qid, split in split_by_id.items() if qid in by_id):
        issues.append("record_split_assignment_mismatch")
    if any(r.get("dataset_version") not in {"2.0.0", "2.1.0", "2.2.0"} for r in records):
        issues.append("unexpected_record_dataset_version")
    if any(r.get("recommended_for_evaluation") is not True or r.get("gold_subset_member") is not True for r in records):
        issues.append("active_file_contains_non_gold_record")
    if any(r.get("human_reviewed") is not True or not r.get("review_status") for r in records):
        issues.append("active_record_missing_human_review_provenance")
    if any(not isinstance(r.get("publication_rights"), dict) or not r["publication_rights"].get("record_license") for r in records):
        issues.append("active_record_missing_record_license")
    if any(not r.get("gold_evidence_sets") for r in records):
        issues.append("active_record_missing_evidence_set")
    if any(r.get("answerability") == "answerable" and not r.get("required_facts") for r in records):
        issues.append("answerable_record_missing_required_facts")

    source_registry = read_json(ROOT / "sources.json")
    source_map = {r.get("source_id"): r for r in source_registry.get("sources", [])}
    referenced = {sid for r in records for sid in r.get("source_ids", [])}
    referenced |= {
        s.get("source_id") for r in records for e in r.get("gold_evidence_sets", [])
        for s in e.get("sources", []) if s.get("source_id")
    }
    if referenced - set(source_map):
        issues.append("unregistered_source:" + ",".join(sorted(referenced - set(source_map))))
    if len(referenced) != 61:
        issues.append(f"referenced_source_count:{len(referenced)}")

    for key in ("family_id", "connected_group_id"):
        group_splits: dict[str, set[str]] = defaultdict(set)
        for row in records:
            value = row.get(key)
            if value:
                group_splits[str(value)].add(str(row.get("split")))
        leaking = [group for group, splits in group_splits.items() if len(splits) > 1]
        if leaking:
            issues.append(f"{key}_cross_split_groups:{len(leaking)}")

    # Every Viewer row must round-trip to the canonical record JSON and appear once.
    viewer_counts: dict[str, int] = {}
    viewer_ids: list[str] = []
    for split_name, split in (("train", "TRAIN"), ("validation", "DEV"), ("test", "TEST")):
        path = ROOT / "data/gold" / f"{split_name}.jsonl"
        rows = read_jsonl(path)
        viewer_counts[split] = len(rows)
        for item in rows:
            try:
                payload = json.loads(item["record_json"])
            except Exception:
                issues.append(f"invalid_record_json:{split_name}")
                continue
            qid = payload.get("query_id")
            viewer_ids.append(qid)
            if qid not in by_id or payload != by_id[qid]:
                issues.append(f"viewer_record_mismatch:{qid}")
            if item.get("split") != split or item.get("recommended_for_evaluation") is not True:
                issues.append(f"viewer_status_or_split_mismatch:{qid}")
            if item.get("answer_candidate") != payload.get("gold_answer"):
                issues.append(f"viewer_answer_mismatch:{qid}")
    if viewer_counts != EXPECTED_SPLITS or len(viewer_ids) != EXPECTED or len(viewer_ids) != len(set(viewer_ids)) or set(viewer_ids) != set(by_id):
        issues.append("viewer_coverage_or_split_mismatch")

    # Verify baseline history and that 2,275 retained baseline IDs were unchanged.
    base_records_path, base_splits_path = BASE / "records.jsonl", BASE / "split_assignments.jsonl"
    if not base_records_path.is_file() or sha(base_records_path) != BASE_RECORD_SHA:
        issues.append("frozen_v2_1_record_hash_mismatch")
    if not base_splits_path.is_file() or sha(base_splits_path) != BASE_SPLIT_SHA:
        issues.append("frozen_v2_1_split_hash_mismatch")
    baseline = {r["query_id"]: r for r in read_jsonl(base_records_path)}
    retained = set(baseline) & set(by_id)
    if len(retained) != 2275:
        issues.append(f"retained_baseline_count:{len(retained)}")
    immutable = ("question", "answerability", "gold_answer", "required_facts", "gold_evidence_sets", "split", "source_ids", "publication_rights")
    changed_baseline = [qid for qid in retained if any(baseline[qid].get(k) != by_id[qid].get(k) for k in immutable)]
    if changed_baseline:
        issues.append(f"retained_baseline_content_changed:{len(changed_baseline)}")
    if {"IICR-V12-0026", "IICR-V12-0028"} & set(by_id):
        issues.append("baseline_uncredited_record_in_gold")
    release_audit = read_json(ROOT / "audit/v2_2/RELEASE_AUDIT.json")
    excluded_source_scope_ids = set(release_audit.get("baseline", {}).get("baseline_ids_excluded_for_unresolved_source_scope_findings", []))
    source_scope_ids_not_released = set(release_audit.get("baseline", {}).get("source_scope_finding_ids_not_in_release", []))
    if excluded_source_scope_ids - source_scope_ids_not_released:
        issues.append("release_audit_source_scope_exclusion_not_documented")
    if source_scope_ids_not_released & set(by_id):
        issues.append("baseline_record_with_unresolved_source_scope_finding_in_gold")
    replacements = [r for r in records if r.get("query_id", "").startswith("IICR-V22-")]
    if len(replacements) != 80:
        issues.append(f"replacement_count:{len(replacements)}")
    if any(not r.get("supersedes_query_id") for r in replacements):
        issues.append("replacement_missing_supersedes_link")
    if any(r.get("human_reviewed") is not True for r in replacements):
        issues.append("replacement_missing_human_review")

    # Public audit summary records the final overlap and replacement gates.
    overlap = release_audit.get("overlap_review", {})
    if (
        overlap.get("reviewed_pairs") != 208
        or overlap.get("retain_both") != 186
        or overlap.get("revise_one") != 22
        or overlap.get("revise_one_pairs_with_both_members_released") != 0
    ):
        issues.append("overlap_gate_failed_in_release_audit")
    replacement_gate = release_audit.get("v2_2_replacements", {})
    if replacement_gate.get("included_passing_replacements") != 80 or replacement_gate.get("excluded_after_release_gates") != 140:
        issues.append("replacement_gate_counts_mismatch_in_release_audit")
    manifest = release_audit
    if manifest.get("released_record_count") != EXPECTED:
        issues.append("release_audit_count_mismatch")
    schema = read_json(ROOT / "schema.json")
    if not isinstance(schema.get("anyOf"), list) or len(schema["anyOf"]) < 4:
        issues.append("composite_schema_missing_active_record_variants")
    front = (ROOT / "README.md").read_text(encoding="utf-8").split("---", 2)
    if len(front) < 3 or "config_name: gold" not in front[1] or "data/gold/" not in front[1]:
        issues.append("huggingface_gold_config_missing")
    if (ROOT / "data/candidates_train.jsonl").exists() or (ROOT / "data/recommended/train.jsonl").exists():
        issues.append("stale_candidate_viewer_files_remain")

    license_counts = Counter()
    for r in records:
        license_counts[r["publication_rights"]["record_license"]] += 1
    details = {
        "validation": "passed" if not issues else "failed",
        "validated_on": date.today().isoformat(),
        "release_version": VERSION,
        "gold_claim_scope": "active released subset only",
        "record_count": len(records),
        "split_counts": split_counts,
        "viewer_split_counts": viewer_counts,
        "retained_v2_1_ids": len(retained),
        "passing_v2_2_replacements": len(replacements),
        "all_active_records_human_reviewed": all(r.get("human_reviewed") is True for r in records),
        "all_active_records_have_record_rights": all(bool(r.get("publication_rights")) for r in records),
        "referenced_source_count": len(referenced),
        "registered_source_count": len(source_map),
        "license_counts": dict(license_counts),
        "overlap_pairs_reviewed": overlap.get("reviewed_pairs"),
        "revise_one_pairs_with_both_members_released": overlap.get("revise_one_pairs_with_both_members_released"),
        "frozen_v2_1_records_sha256": sha(base_records_path),
        "frozen_v2_1_split_assignments_sha256": sha(base_splits_path),
        "active_records_sha256": sha(records_path),
        "active_split_assignments_sha256": sha(split_path),
        "source_registry_sha256": sha(ROOT / "sources.json"),
        "issues": issues,
    }
    (ROOT / "VALIDATION_REPORT.json").write_text(json.dumps(details, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if issues:
        print(json.dumps(details, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    (ROOT / "release_metadata.json").write_text(json.dumps({
        "dataset_id": "chinese-internet-ict-reports-qa",
        "version": VERSION,
        "release_status": "release_ready_pending_remote_verification",
        "gold_claimed": True,
        "gold_claim_scope": f"active {EXPECTED:,}-record released subset only",
        "record_count": len(records),
        "split_counts": split_counts,
        "record_license_policy": "mixed, record-level; no repository-wide license",
        "source_pdf_media_included": False,
        "validation_status": "passed",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    missing = [name for name in CORE_FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("Release files missing: " + ", ".join(missing))
    file_manifest = [{"path": name, "sha256": sha(ROOT / name)} for name in CORE_FILES if name != "VALIDATION_REPORT.json"]
    # The validation report is added after being written above.
    file_manifest.append({"path": "VALIDATION_REPORT.json", "sha256": sha(ROOT / "VALIDATION_REPORT.json")})
    package = {
        "dataset_id": "chinese-internet-ict-reports-qa",
        "version": VERSION,
        "package_status": "release_ready_pending_remote_verification",
        "gold_claimed": True,
        "record_count": len(records),
        "split_counts": split_counts,
        "record_license_policy": "mixed, record-level; no repository-wide license",
        "source_pdf_media_included": False,
        "files": file_manifest,
        "frozen_history": {
            "version": "2.1.0",
            "record_count": BASE_COUNT,
            "records_sha256": BASE_RECORD_SHA,
            "split_assignments_sha256": BASE_SPLIT_SHA,
            "snapshot_manifest": "history/v2.1.0/SNAPSHOT_MANIFEST.json",
        },
    }
    (ROOT / "manifest.json").write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sums_paths = CORE_FILES + ["manifest.json"]
    (ROOT / "SHA256SUMS").write_text("".join(f"{sha(ROOT / name)}  {name}\n" for name in sums_paths), encoding="utf-8")

    # Read back the just-written hash inventory and manifest.
    for row in file_manifest:
        if sha(ROOT / row["path"]) != row["sha256"]:
            raise SystemExit(f"Manifest hash mismatch: {row['path']}")
    sum_lines = (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    for line in sum_lines:
        digest, name = line.split("  ", 1)
        if sha(ROOT / name) != digest:
            raise SystemExit(f"SHA256SUMS mismatch: {name}")
    print(json.dumps(details, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
