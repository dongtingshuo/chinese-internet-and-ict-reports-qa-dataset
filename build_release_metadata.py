#!/usr/bin/env python3
"""Generate v2.1.0 validation report, package manifest, and SHA-256 sums."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

from validate_v2_1_package import validate

ROOT = Path(__file__).resolve().parent
VERSION = "2.1.0"
VALIDATED_ON = "2026-10-07"
DYNAMIC_FILES = {"VALIDATION_REPORT.json", "manifest.json", "SHA256SUMS"}
IGNORED_PARTS = {".git", "__pycache__"}
IGNORED_NAMES = {".DS_Store"}


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def repo_files():
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(part in IGNORED_PARTS for part in rel.parts):
            continue
        if path.name in IGNORED_NAMES or path.suffix in {".pyc", ".pyo"}:
            continue
        yield path


def payload_fingerprint() -> str:
    payload = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}
        for path in repo_files()
        if path.name not in DYNAMIC_FILES
    ]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return sha_bytes(encoded)


def counts(rows, key):
    return dict(sorted(collections.Counter(row.get(key) for row in rows).items()))


def split_counts(rows):
    return dict(sorted(collections.Counter(row.get("split") for row in rows).items()))


def license_counts(rows):
    aliases = {
        "CC-BY-3.0-IGO": "CC BY 3.0 IGO",
        "CC BY 3.0 IGO": "CC BY 3.0 IGO",
        "CC-BY-4.0": "CC BY 4.0",
        "CC BY 4.0": "CC BY 4.0",
        "CC-BY-SA-3.0-IGO": "CC BY-SA 3.0 IGO",
        "CC BY-SA 3.0 IGO": "CC BY-SA 3.0 IGO",
        "CC BY-NC-SA 3.0 IGO": "CC BY-NC-SA 3.0 IGO",
        "CC-BY-NC-SA-3.0-IGO": "CC BY-NC-SA 3.0 IGO",
    }
    values = [row["publication_rights"]["record_license"] for row in rows]
    return dict(sorted(collections.Counter(aliases.get(value, value) for value in values).items()))


issues, stats = validate(ROOT)
if issues:
    raise SystemExit("Validation failed; refusing release metadata: " + "; ".join(issues[:10]))

rows = read_jsonl(ROOT / "records.jsonl")
sources_doc = read_json(ROOT / "sources.json")
sources = {source["source_id"]: source for source in sources_doc["sources"]}
old_rows = rows[:2000]
new_rows = rows[2000:]
recommended = [row for row in rows if row.get("recommended_for_evaluation") is True]
source_ids = sorted({sid for row in rows for sid in row.get("source_ids", [])})
family_ids = sorted({family for row in rows for family in (row.get("family_ids") or ([row.get("family_id")] if row.get("family_id") else []))})
publishers = sorted({entity for source in sources.values() for entity in source.get("publishing_institution_entities", [])})
ledger = read_jsonl(ROOT / "audit" / "v2_1_candidate_disposition_ledger.jsonl")
ledger_counts = dict(sorted(collections.Counter(item["disposition"] for item in ledger).items()))
new_evidence = [locator for row in new_rows for evidence_set in row.get("gold_evidence_sets", []) for locator in evidence_set.get("sources", [])]
table_evidence_count = sum(locator.get("locator_type") in {"table_cells", "table_footnote"} for locator in new_evidence)
table_question_count = sum(any(locator.get("locator_type") in {"table_cells", "table_footnote"} for evidence_set in row.get("gold_evidence_sets", []) for locator in evidence_set.get("sources", [])) for row in new_rows)
cloze_count = sum(row.get("task_subtype") == "sentence_cloze" or "______" in row.get("question", "") for row in rows)
source_pdf_hashes = {sid: sources[sid].get("original_report_sha256") for sid in source_ids if sid in sources}

current_fingerprint = payload_fingerprint()
previous_path = ROOT / "VALIDATION_REPORT.json"
previous_report = read_json(previous_path) if previous_path.exists() else {}
remote_verification = previous_report.get("remote_hf_viewer_verification") if previous_report.get("remote_payload_fingerprint") == current_fingerprint else None
remote_payload_verified = bool(remote_verification and remote_verification.get("dataset_payload_files_match"))
remote_viewer_verified = bool(remote_verification and remote_verification.get("dataset_viewer_verified"))

v20_manifest = read_json(ROOT / "history" / "v2.0.0" / "SNAPSHOT_MANIFEST.json")
v20_hashes = v20_manifest["files"]
report = {
    "validation_status": "passed_with_historical_review_statuses_preserved",
    "version": VERSION,
    "validated_on": VALIDATED_ON,
    "record_count": len(rows),
    "v2_0_preserved_record_count": len(old_rows),
    "v2_1_added_record_count": len(new_rows),
    "recommended_record_count": len(recommended),
    "all_active_records_recommended_per_owner_instruction": len(recommended) == len(rows),
    "source_document_count": len(sources),
    "report_family_count": len(family_ids),
    "publishing_institution_count": len(publishers),
    "split_counts": split_counts(rows),
    "v2_1_added_split_counts": split_counts(new_rows),
    "task_family_counts": counts(rows, "task_family"),
    "v2_1_task_family_counts": counts(new_rows, "task_family"),
    "task_subtype_counts": counts(rows, "task_subtype"),
    "review_status_counts": counts(rows, "review_status"),
    "v2_1_review_status_counts": counts(new_rows, "review_status"),
    "answerability_counts": counts(rows, "answerability"),
    "record_license_counts": license_counts(rows),
    "v2_1_record_license_counts": license_counts(new_rows),
    "source_ids": source_ids,
    "source_pdf_sha256_by_source_id": source_pdf_hashes,
    "v2_1_new_source_document_count": len({sid for row in new_rows for sid in row.get("source_ids", [])}),
    "source_documents_added_in_v2_1": 0,
    "all_record_rights_and_attribution_fields_present": True,
    "source_pdf_hashes_match_registry_for_v2_1": True,
    "v2_1_qa_quality_audit": {
        "new_non_cloze_count": len(new_rows) - sum("______" in row.get("question", "") for row in new_rows),
        "table_or_footnote_locators": table_evidence_count,
        "records_using_table_or_footnote_evidence": table_question_count,
        "new_question_answer_fact_evidence_coverage": True,
        "new_questions_reconstructed_from_question_only_input": True,
        "candidate_answer_present_in_reconstruction_input": False,
        "physical_pdf_page_numbers_and_source_hashes_recorded": True,
        "table_locators_include_table_and_row_column_or_footnote_details": True,
        "exact_duplicate_question_count": stats["exact_duplicate_question_count"],
        "near_duplicate_pairs_at_or_above_0_82": stats["near_duplicate_pair_count_at_0_82"],
    },
    "candidate_disposition_counts": ledger_counts,
    "cloze_record_count_preserved_from_v2_0": cloze_count,
    "source_pdfs_media_and_full_extracted_text_in_package": False,
    "human_reviewed": False,
    "independent_human_review": "not_performed",
    "independent_ai_session_review": "not_performed; same active AI session drafted and checked the new questions",
    "gold_benchmark_claim": False,
    "blind_holdout_claim": False,
    "prior_system_exposure_audit": "not_performed",
    "model_performance_results_included": False,
    "v2_0_snapshot_sha256": {
        "records.jsonl": v20_hashes["records.jsonl"],
        "split_assignments.jsonl": v20_hashes["split_assignments.jsonl"],
    },
    "v2_0_snapshot_unchanged": True,
    "remote_payload_fingerprint": current_fingerprint,
    "remote_hf_viewer_verification": remote_verification,
    "remote_payload_files_match": remote_payload_verified,
    "remote_dataset_viewer_verified": remote_viewer_verified,
    "checks": {
        "schema_and_version_fields": True,
        "unique_ids_and_v2_1_id_format": True,
        "old_2000_rows_content_ids_splits_recommendation_and_review_status_unchanged": True,
        "all_508_new_rows_non_cloze_recommended_and_ai_checked": True,
        "all_new_rows_have_source_specific_license_attribution_and_obligations": True,
        "all_v2_1_evidence_pages_in_bounds_and_fact_coverage_exact": True,
        "table_row_column_and_footnote_locators_present_and_audit_aligned": True,
        "source_family_and_evidence_group_split_isolation": True,
        "duplicate_and_near_duplicate_checks": True,
        "viewer_files_match_canonical_records_and_splits": True,
        "no_source_pdf_or_media_in_repository_payload": True,
        "v2_0_frozen_snapshot_hashes_match": True,
        "remote_dataset_payload_files_match": remote_payload_verified,
        "remote_dataset_viewer_counts_verified": remote_viewer_verified,
    },
    "pending_gates": [],
}
if not remote_payload_verified:
    report["pending_gates"].append("Synchronize the validated package to Hugging Face and compare the published file hashes.")
if not remote_viewer_verified:
    report["pending_gates"].append("Verify Hugging Face Dataset Viewer split counts after its processing job completes.")
(ROOT / "VALIDATION_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

package_files = [path for path in repo_files() if path.name not in {"manifest.json", "SHA256SUMS"}]
manifest = {
    "dataset_id": "chinese_internet_ict_reports_qa",
    "dataset_name": "Chinese Internet and ICT Reports QA Dataset / 中文互联网与 ICT 报告问答数据集",
    "version": VERSION,
    "created_on": VALIDATED_ON,
    "package_status": report["validation_status"],
    "record_count": len(rows),
    "v2_0_preserved_record_count": len(old_rows),
    "v2_1_added_record_count": len(new_rows),
    "recommended_record_count": len(recommended),
    "source_document_count": len(sources),
    "report_family_count": len(family_ids),
    "publishing_institution_count": len(publishers),
    "split_counts": split_counts(rows),
    "v2_1_added_split_counts": split_counts(new_rows),
    "task_family_counts": counts(rows, "task_family"),
    "task_subtype_counts": counts(rows, "task_subtype"),
    "review_status_counts": counts(rows, "review_status"),
    "answerability_counts": counts(rows, "answerability"),
    "record_license_counts": license_counts(rows),
    "v2_1_record_license_counts": license_counts(new_rows),
    "source_record_counts": dict(sorted(collections.Counter(sid for row in rows for sid in row.get("source_ids", [])).items())),
    "source_ids": source_ids,
    "record_license_policy": "mixed_record_level_no_repository_wide_license",
    "dataset_license": None,
    "huggingface_license_metadata": "other",
    "source_pdfs_media_and_full_extracted_text_included": False,
    "human_reviewed": False,
    "independent_human_review": "not_performed",
    "gold_benchmark_claim": False,
    "historical_splits_assigned_after_annotation": True,
    "v2_1_source_family_splits_preassigned": True,
    "prior_system_exposure_audit": "not_performed",
    "model_performance_results_included": False,
    "v2_0_snapshot_sha256": report["v2_0_snapshot_sha256"],
    "source_pdf_sha256_by_source_id": source_pdf_hashes,
    "target_progress": {"v2_1_new_qa_target": 506, "actual": len(new_rows), "met": len(new_rows) >= 506},
    "viewer_layout": {
        "candidate_config": "candidates",
        "recommended_config": "recommended",
        "candidate_split_counts": split_counts(rows),
        "recommended_split_counts": split_counts(recommended),
    },
    "validation_report": "VALIDATION_REPORT.json",
    "license_notice": "See LICENSE, LICENSES.md, LICENSE_STATUS.md, ATTRIBUTION.md, and per-record publication_rights; no single license applies to the full corpus.",
    "package_files": [
        {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}
        for path in package_files
    ],
}
(ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checksum_files = [path for path in repo_files() if path.name != "SHA256SUMS"]
(ROOT / "SHA256SUMS").write_text(
    "".join(f"{sha(path)}  {path.relative_to(ROOT).as_posix()}\n" for path in checksum_files),
    encoding="utf-8",
)
print(json.dumps({
    "version": VERSION,
    "records": len(rows),
    "v2_1_added": len(new_rows),
    "recommended": len(recommended),
    "split_counts": split_counts(rows),
    "package_file_count": len(package_files),
    "remote_hf_viewer_verified": remote_viewer_verified,
}, ensure_ascii=False, indent=2))
