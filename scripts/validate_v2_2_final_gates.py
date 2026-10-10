#!/usr/bin/env python3
"""Reconcile the final v2.2.0 Gold release gates from canonical audit artifacts.

This is intentionally separate from the historical review-material validator:
batch progress files are dated snapshots, while this command validates the
current full-corpus disposition and the released Gold subset.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit" / "v2_2"
OUTPUT = AUDIT / "FINAL_GATE_RECONCILIATION_2026-10-10.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = []
    checks: dict[str, Any] = {}

    def check(name: str, passed: bool, evidence: Any = None, failure: str | None = None) -> None:
        checks[name] = {"passed": bool(passed), "evidence": evidence}
        if not passed:
            failures.append(failure or name)

    status = read_json(AUDIT / "AUDIT_STATUS.json")
    source_coverage = read_json(AUDIT / "FULL_CORPUS_SOURCE_AUDIT_COVERAGE_2026-10-09.json")
    gate_reconciliation = read_json(AUDIT / "V2_2_CANDIDATE_GOLD_GATE_RECONCILIATION_2026-10-09.json")
    candidate_validation = read_json(AUDIT / "V2_2_CANDIDATE_VALIDATION_2026-10-09.json")
    selection = read_json(AUDIT / "V22_GOLD_SUBSET_SELECTION_REPORT_2026-10-09.json")
    candidate_selection = read_json(ROOT / "outputs" / "v2_2_reviewed_candidate" / "GOLD_SUBSET_SELECTION.json")
    candidate_report = read_json(ROOT / "outputs" / "v2_2_reviewed_candidate" / "CANDIDATE_REPORT.json")
    release_audit = read_json(AUDIT / "RELEASE_AUDIT.json")
    rights = read_json(AUDIT / "RIGHTS_EVIDENCE_RECONCILIATION.json")
    supplemental = read_json(AUDIT / "SUPPLEMENTAL_REVIEW_STATUS_2026-10-09.json")
    third_human_method = read_json(AUDIT / "THIRD_HUMAN_METHOD_ATTESTATION_2026-10-09.json")

    # Recompute blind-credit totals from the immutable row-level locks and
    # post-lock comparisons. Do not trust summary counts alone: an earlier
    # failed attempt reviewed the same 25 IDs but earned zero credit.
    primary_lock_rows = read_jsonl(AUDIT / "ai_reconstruction_results.jsonl")
    primary_credit_ids = {row.get("query_id") for row in primary_lock_rows if row.get("query_id")}
    hashfirst_recon_path = AUDIT / "FRESH_BLIND_AI_RECONSTRUCTIONS_HASHFIRST_2026-10-09.jsonl"
    hashfirst_comparison = read_json(AUDIT / "FRESH_BLIND_AI_COMPARISON_HASHFIRST_2026-10-09.json")
    hashfirst_manifest = read_json(AUDIT / "FRESH_BLIND_AI_RECONSTRUCTIONS_HASHFIRST_2026-10-09.MANIFEST.json")
    hashfirst_source_audit_path = AUDIT / "FRESH_BLIND_AI_SOURCE_HASH_AUDIT_HASHFIRST_2026-10-09.json"
    hashfirst_source_audit = read_json(hashfirst_source_audit_path)
    hashfirst_recon_rows = read_jsonl(hashfirst_recon_path)
    hashfirst_credit_ids = {
        row.get("query_id") for row in hashfirst_comparison.get("records", [])
        if row.get("blind_credit_decision") == "awarded"
    }
    clean5_recon_path = AUDIT / "FRESH_BLIND_AI_RECHECK_RECONSTRUCTIONS_CLEAN5_2026-10-09.jsonl"
    clean5_comparison = read_json(AUDIT / "FRESH_BLIND_AI_RECHECK_COMPARISON_CLEAN5_2026-10-09.json")
    clean5_recon_rows = read_jsonl(clean5_recon_path)
    clean5_credit_ids = {
        row.get("query_id") for row in clean5_comparison.get("rows", [])
        if row.get("credit_counted") is True
    }
    primary_packet = read_jsonl(AUDIT / "ai_question_only_packet.jsonl")
    primary_packet_ids = {row.get("query_id") for row in primary_packet if row.get("query_id")}
    hashfirst_packet_path = AUDIT / "BLIND_AI_CREDIT_PACKET_2026-10-09.jsonl"
    hashfirst_packet = read_jsonl(hashfirst_packet_path)
    hashfirst_packet_ids = {row.get("query_id") for row in hashfirst_packet if row.get("query_id")}
    hashfirst_source_checks = hashfirst_source_audit.get("sources", [])
    hashfirst_sources_pass = bool(hashfirst_source_checks) and all(
        source.get("status") == "PASS"
        and source.get("expected_sha256") == source.get("measured_sha256")
        and source.get("expected_pdf_page_count") == source.get("measured_pdf_page_count")
        for source in hashfirst_source_checks
    )
    hashfirst_packet_hash = sha256(hashfirst_packet_path)
    hashfirst_lock_hash = sha256(hashfirst_recon_path)
    hashfirst_source_audit_hash = sha256(hashfirst_source_audit_path)
    clean5_lock_hash = sha256(clean5_recon_path)

    released = read_jsonl(ROOT / "records.jsonl")
    candidate = read_jsonl(ROOT / "outputs" / "v2_2_reviewed_candidate" / "records.jsonl")
    released_ids = {row.get("query_id") for row in released}
    candidate_ids = {row.get("query_id") for row in candidate}

    expected_splits = Counter({"TRAIN": 1573, "DEV": 372, "TEST": 410})
    actual_splits = Counter(row.get("split") for row in released)
    active_v22 = [row for row in released if str(row.get("query_id", "")).startswith("IICR-V22-")]
    active_v21 = [row for row in released if row not in active_v22]

    check(
        "published_gold_subset_shape",
        len(released) == 2355 and len(released_ids) == len(released) and actual_splits == expected_splits
        and len(active_v21) == 2275 and len(active_v22) == 80
        and selection.get("gold_subset_count") == 2355 and selection.get("excluded_v22_replacements") == 140,
        {
            "records": len(released),
            "unique_ids": len(released_ids),
            "splits": dict(actual_splits),
            "retained_baseline_rows": len(active_v21),
            "passing_replacements": len(active_v22),
        },
    )
    check(
        "failed_or_uncredited_baseline_rows_excluded",
        not ({"IICR-V12-0026", "IICR-V12-0028", "IICR-V12-0030"} & released_ids),
        {"excluded_query_ids": ["IICR-V12-0026", "IICR-V12-0028", "IICR-V12-0030"]},
    )
    excluded_replacements = set(candidate_report.get("excluded_v22_replacements_without_blind_ai_credit", []))
    check(
        "nonpassing_replacements_excluded",
        len(excluded_replacements) == 140 and not (excluded_replacements & released_ids)
        and candidate_selection.get("gold_subset_count") == 2355,
        {"excluded_replacement_count": len(excluded_replacements), "excluded_ids_in_release": sorted(excluded_replacements & released_ids)},
    )

    check(
        "full_corpus_source_grounded_ai_audit",
        source_coverage.get("source_grounded_review_rows_completed") == 2508
        and source_coverage.get("source_grounded_review_rows_remaining") == 0
        and source_coverage.get("answer_blind_ai_reconstruction_rows") == 2483
        and source_coverage.get("supplemental_nonblind_source_review_rows") == 25
        and source_coverage.get("supplemental_nonblind_blind_credit") == 0,
        {
            "source_grounded_rows": source_coverage.get("source_grounded_review_rows_completed"),
            "answer_blind_reconstructions": source_coverage.get("answer_blind_ai_reconstruction_rows"),
            "nonblind_supplement_rows": source_coverage.get("supplemental_nonblind_source_review_rows"),
            "nonblind_credit": source_coverage.get("supplemental_nonblind_blind_credit"),
        },
    )
    review = gate_reconciliation.get("review_coverage", {})
    no_credit_ids = set(review.get("baseline_rows_without_ai_blind_credit_excluded_from_recommendation", []))
    blind_credit_union = primary_credit_ids | hashfirst_credit_ids | clean5_credit_ids
    hashfirst_lock_ids = {row.get("query_id") for row in hashfirst_recon_rows if row.get("query_id")}
    clean5_lock_ids = {row.get("query_id") for row in clean5_recon_rows if row.get("query_id")}
    hashfirst_withheld_ids = {
        row.get("query_id") for row in hashfirst_comparison.get("records", [])
        if row.get("blind_credit_decision") != "awarded"
    }
    row_level_credit_evidence = {
        "primary_credit_rows": len(primary_credit_ids),
        "primary_rows_are_subset_of_full_question_only_packet": primary_credit_ids <= primary_packet_ids,
        "hashfirst_rows_cover_primary_packet_gap": hashfirst_lock_ids == (primary_packet_ids - primary_credit_ids),
        "hashfirst_reconstruction_rows": len(hashfirst_recon_rows),
        "hashfirst_comparison_rows": hashfirst_comparison.get("record_count"),
        "hashfirst_credited_ids": len(hashfirst_credit_ids),
        "hashfirst_withheld_ids": sorted(hashfirst_withheld_ids),
        "hashfirst_rows_disjoint_from_primary": not bool(hashfirst_lock_ids & primary_credit_ids),
        "hashfirst_lock_packet_ids_match": hashfirst_lock_ids == hashfirst_packet_ids,
        "hashfirst_lock_hash_matches_manifest": hashfirst_lock_hash == hashfirst_manifest.get("sha256"),
        "hashfirst_packet_hash_matches_comparison": hashfirst_packet_hash == hashfirst_comparison.get("packet_sha256"),
        "hashfirst_source_audit_hash_matches_comparison": hashfirst_source_audit_hash == hashfirst_comparison.get("source_hash_audit_sha256"),
        "hashfirst_source_audit_hash_matches_manifest": hashfirst_source_audit_hash == hashfirst_manifest.get("source_hash_audit_sha256"),
        "hashfirst_sources_pass": hashfirst_sources_pass,
        "hashfirst_lock_precedes_comparison_attested": hashfirst_manifest.get("locked_before_dataset_or_prior_review_access") is True,
        "clean5_rows": len(clean5_recon_rows),
        "clean5_credited_ids": sorted(clean5_credit_ids),
        "clean5_lock_hash_matches_comparison": clean5_lock_hash == clean5_comparison.get("phase1_integrity", {}).get("locked_reconstructions_sha256_verified"),
        "clean5_credits_disjoint_from_prior_credit": not bool(clean5_credit_ids & (primary_credit_ids | hashfirst_credit_ids)),
        "total_unique_credited_ids": len(blind_credit_union),
        "no_credit_ids_in_total": sorted((primary_packet_ids | hashfirst_packet_ids | clean5_lock_ids) - blind_credit_union),
    }
    row_level_credit_pass = (
        len(primary_credit_ids) == 2483
        and primary_credit_ids <= primary_packet_ids
        and len(hashfirst_recon_rows) == 25
        and hashfirst_comparison.get("record_count") == 25
        and len(hashfirst_credit_ids) == 20
        and hashfirst_lock_ids == hashfirst_packet_ids
        and hashfirst_lock_ids == (primary_packet_ids - primary_credit_ids)
        and not (hashfirst_lock_ids & primary_credit_ids)
        and hashfirst_lock_hash == hashfirst_manifest.get("sha256") == hashfirst_comparison.get("locked_reconstruction_sha256")
        and hashfirst_packet_hash == hashfirst_comparison.get("packet_sha256")
        and hashfirst_source_audit_hash == hashfirst_comparison.get("source_hash_audit_sha256") == hashfirst_manifest.get("source_hash_audit_sha256")
        and hashfirst_sources_pass
        and hashfirst_manifest.get("locked_before_dataset_or_prior_review_access") is True
        and len(clean5_recon_rows) == 5
        and len(clean5_credit_ids) == 3
        and clean5_lock_hash == clean5_comparison.get("phase1_integrity", {}).get("locked_reconstructions_sha256_verified")
        and not (clean5_credit_ids & (primary_credit_ids | hashfirst_credit_ids))
        and len(blind_credit_union) == 2506
        and (primary_packet_ids | hashfirst_packet_ids | clean5_lock_ids) - blind_credit_union == {"IICR-V12-0026", "IICR-V12-0028"}
    )
    check(
        "blind_ai_credit_and_exclusions",
        row_level_credit_pass
        and review.get("answer_blind_ai_credited_baseline_rows") == 2506
        and no_credit_ids == {"IICR-V12-0026", "IICR-V12-0028"}
        and not (no_credit_ids & released_ids)
        and review.get("answer_blind_ai_credited_baseline_rows_in_gold_subset") == 2275,
        {"credited_baseline_rows": review.get("answer_blind_ai_credited_baseline_rows"), "excluded_without_credit": sorted(no_credit_ids), "row_level_evidence": row_level_credit_evidence},
    )

    reviewers = status.get("reviewer_1_workbook_metadata", {}), status.get("reviewer_2_workbook_metadata", {})
    check(
        "two_reviewer_baseline_coverage",
        [row.get("record_rows") for row in reviewers] == [2508, 2508]
        and status.get("reviewer_answer_blindness_disclosure", {}).get("status") == "dataset_owner_attested_fully_answer_and_annotation_blind"
        and status.get("reviewer_assistance_disclosure", {}).get("status") == "owner_attested_no_ai_or_other_assistance",
        {"reviewers": [row.get("reviewer_id") for row in reviewers], "rows_each": [row.get("record_rows") for row in reviewers], "method_basis": "dataset-owner-attested"},
    )

    expected_human_files = {
        "alignment": ("THIRD_HUMAN_FOLLOWUP_ADJUDICATION_RESULTS_2026-10-09.jsonl", 199),
        "question_revisions": ("THIRD_HUMAN_FOLLOWUP_QUESTION_REVISION_RESULTS_2026-10-09.jsonl", 115),
        "source_dispositions": ("THIRD_HUMAN_FOLLOWUP_SOURCE_DISPOSITION_RESULTS_2026-10-09.jsonl", 15),
        "overlap": ("THIRD_HUMAN_FOLLOWUP_OVERLAP_RESULTS_2026-10-09.jsonl", 208),
        "locator_addenda": ("THIRD_HUMAN_LOCATOR_RESULTS_2026-10-09.jsonl", 19),
        "locator_patches": ("THIRD_HUMAN_LOCATOR_PATCHES_2026-10-09.jsonl", 13),
        "supplemental_cases": ("THIRD_HUMAN_SUPPLEMENTAL_RESULTS_2026-10-09.jsonl", 10),
    }
    human_counts = {name: len(read_jsonl(AUDIT / file_name)) for name, (file_name, _) in expected_human_files.items()}
    human_counts_pass = all(human_counts[name] == expected for name, (_, expected) in expected_human_files.items())
    human_followup = review.get("third_human_followup", {})
    open_findings = [
        human_followup.get("open_question_source_findings"),
        human_followup.get("cross_sheet_disposition_conflicts"),
        human_followup.get("overlap_rationale_gaps"),
    ]
    check(
        "third_human_adjudication_and_followups",
        human_counts_pass and all(not finding for finding in open_findings)
        and supplemental.get("third_human_supplement_rows_reviewed") == 10
        and supplemental.get("third_human_supplement_rows_unresolved") == 0
        and third_human_method.get("reviewer_identity", {}).get("id") == "S"
        and third_human_method.get("reviewer_assistance_disclosure", {}).get("status") == "dataset_owner_attested_no_ai_or_other_assistance",
        {"completed_ledgers": human_counts, "open_findings": open_findings, "method_basis": "dataset-owner-attested; not reviewer-signed"},
    )

    overlap_rows = read_jsonl(AUDIT / "THIRD_HUMAN_FOLLOWUP_OVERLAP_RESULTS_2026-10-09.jsonl")
    def overlap_decision(row: dict[str, Any]) -> str:
        value = row.get("final_decision_and_specific_reason", "")
        prefix = value.split("；", 1)[0].strip()
        return "revise_one" if prefix.startswith("revise_one") else "retain_both" if prefix.startswith("retain_both") else "unclassified"

    overlap_counts = Counter(overlap_decision(row) for row in overlap_rows)
    both_revise_one_released = []
    for row in overlap_rows:
        if overlap_decision(row) == "revise_one":
            members = row.get("query_ids", [])
            if len(members) == 2 and all(qid in released_ids for qid in members):
                both_revise_one_released.append(row.get("case_id"))
    check(
        "overlap_review_and_release_separation",
        len(overlap_rows) == 208 and not both_revise_one_released
        and gate_reconciliation.get("overlap_review", {}).get("reviewed_pairs") == 208
        and gate_reconciliation.get("overlap_review", {}).get("decisions") == {"retain_both": 186, "revise_one": 22},
        {"reviewed_pairs": len(overlap_rows), "decisions": dict(overlap_counts), "revise_one_pairs_with_both_released": both_revise_one_released},
    )

    deviations = read_jsonl(AUDIT / "AI_RECONSTRUCTION_PROTOCOL_DEVIATIONS.jsonl")
    deviation_rows = []
    for row in deviations:
        rerun = row.get("clean_rerun", {})
        lock_path = AUDIT / rerun.get("lock_file", "")
        lock_match = lock_path.is_file() and sha256(lock_path) == rerun.get("locked_reconstruction_sha256")
        deviation_rows.append({"query_id": row.get("query_id"), "rerun_batch": rerun.get("batch_id"), "lock_hash_verified": lock_match, "original_attempt_credit": row.get("ai_blind_coverage_credit")})
    check(
        "protocol_deviation_reruns",
        len(deviations) == 3 and all(row["lock_hash_verified"] and row["original_attempt_credit"] is False for row in deviation_rows)
        and gate_reconciliation.get("protocol_deviations", {}).get("pending_clean_reruns") == 0,
        deviation_rows,
    )

    rights_summary = gate_reconciliation.get("rights", {})
    check(
        "source_rights_and_hash_coverage",
        rights_summary.get("registered_sources") == 61
        and rights_summary.get("source_pdf_hashes_verified") == 61
        and rights.get("source_hash_gate", {}).get("unmatched") == 0
        and rights_summary.get("owner_attested_qa_reuse_sources") == 19
        and rights_summary.get("permission_instruments_independently_inspected") is False,
        {
            "registered_sources": rights_summary.get("registered_sources"),
            "verified_source_hashes": rights_summary.get("source_pdf_hashes_verified"),
            "owner_attested_record_reuse_sources": rights_summary.get("owner_attested_qa_reuse_sources"),
            "CAICT_report_license_or_permission_instrument_claimed": False,
        },
    )

    check(
        "candidate_and_release_validators",
        candidate_validation.get("validation") == "passed"
        and candidate_validation.get("recommended_record_count") == len(released)
        and candidate_validation.get("issues") == []
        and release_audit.get("released_record_count") == len(released)
        and release_audit.get("gold_claim_scope") == "Only the 2,355 released records; no Gold claim is made for excluded historical or candidate rows.",
        {"candidate_validation": candidate_validation.get("validation"), "release_record_count": release_audit.get("released_record_count"), "candidate_issues": candidate_validation.get("issues")},
    )

    historical_validation_path = AUDIT / "REVIEW_MATERIALS_VALIDATION.json"
    historical_validation = read_json(historical_validation_path) if historical_validation_path.exists() else {}
    report = {
        "audit_id": "V22-FINAL-GATE-RECONCILIATION-2026-10-10",
        "reconciled_on": "2026-10-10",
        "release_version": "2.2.0",
        "status": "passed" if not failures else "failed",
        "scope": "The 2,355-record active Gold subset only; excluded historical and candidate rows are not certified.",
        "checks": checks,
        "historical_review_material_validator": {
            "status": historical_validation.get("validation", "not_run"),
            "issue_count": len(historical_validation.get("issues", [])),
            "classification": "Historical batch-progress snapshots and pre-release status fields are internally stale; this report preserves that failure separately from the canonical candidate and release validators.",
        },
        "limitations": [
            "Human independence, answer blindness, and no-assistance disclosures are dataset-owner-attested rather than reviewer-signed.",
            "Source-specific record reuse authorization for 19 sources is owner-attested; this is not a publisher open-license claim.",
            "Two baseline rows without blind AI credit and all non-passing proposals are excluded from the active subset.",
            "Historical splits are post-annotation and are not blind holdouts.",
        ],
        "failures": failures,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
