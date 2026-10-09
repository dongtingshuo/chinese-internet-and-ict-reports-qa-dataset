#!/usr/bin/env python3
"""Build v2.1.0 by appending audited QA to the frozen v2.0.0 corpus."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT / "history" / "v2.0.0"
AUDIT = ROOT / "audit"
REVIEW_DATE = "2026-10-07"
REVIEW_MODEL = "GPT-6 (Codex; exact deployment identifier not exposed)"
PROMPT_SHA256 = "7c9bac662fbd4fcaad057a79aa15c32b789a23a9878f4c131eec66569bbc30bd"
SPLIT_VERSION = "v2.1_inherited_source_family_assignment_v1"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(compact(row) + "\n" for row in rows), encoding="utf-8")


def sha256(data: bytes):
    return hashlib.sha256(data).hexdigest()


def source_ref(source):
    keys = (
        "source_id", "publication_institution", "publisher", "publication_year",
        "title_chinese", "title_english", "text_language", "document_type",
        "translation_status", "original_report_url", "original_report_sha256",
        "source_pdf_page_count", "rights_holder", "license", "license_id",
        "license_url", "rights_notice_location", "required_attribution",
        "required_adaptation_disclaimer", "translation_disclaimer",
        "third_party_content_limitations", "source_pdf_included", "edition_note",
    )
    return {key: copy.deepcopy(source[key]) for key in keys if key in source}


def main():
    frozen_manifest = read_json(HISTORY / "SNAPSHOT_MANIFEST.json")
    frozen_records_bytes = (HISTORY / "records.jsonl").read_bytes()
    frozen_assignments_bytes = (HISTORY / "split_assignments.jsonl").read_bytes()
    for filename, payload in (
        ("records.jsonl", frozen_records_bytes),
        ("split_assignments.jsonl", frozen_assignments_bytes),
    ):
        expected = frozen_manifest["files"][filename]
        actual = sha256(payload)
        if actual != expected:
            raise SystemExit(f"Frozen v2.0.0 {filename} hash mismatch: {actual} != {expected}")

    old_records = [json.loads(line) for line in frozen_records_bytes.decode("utf-8").splitlines() if line.strip()]
    old_assignments = [json.loads(line) for line in frozen_assignments_bytes.decode("utf-8").splitlines() if line.strip()]
    if len(old_records) != 2000 or len(old_assignments) != 2000:
        raise SystemExit("Frozen v2.0.0 snapshot must contain exactly 2,000 records and assignments")

    all_questions_path = AUDIT / "v2_1_all_candidate_questions.jsonl"
    all_audits_path = AUDIT / "v2_1_all_candidate_reconstructions.jsonl"
    question_path = AUDIT / "v2_1_question_only.jsonl"
    audit_path = AUDIT / "v2_1_answer_blind_reconstruction.jsonl"
    if not all_questions_path.exists():
        (AUDIT / "v2_1_question_only.jsonl").replace(all_questions_path)
    if not all_audits_path.exists():
        (AUDIT / "v2_1_answer_blind_reconstruction.jsonl").replace(all_audits_path)
    questions = read_jsonl(all_questions_path)
    audits = read_jsonl(all_audits_path)
    if len(questions) != 542 or len({x.get("query_id") for x in questions}) != len(questions):
        raise SystemExit("Expected 542 unique v2.1 draft questions in the review archive")
    if any("answer" in x or "gold_answer" in x or "reconstructed_answer" in x for x in questions):
        raise SystemExit("The answer-blind question packet contains a candidate answer")

    audit_by_id = {x["query_id"]: x for x in audits}
    question_by_id = {x["query_id"]: x for x in questions}
    if len(audit_by_id) != len(audits):
        raise SystemExit("Duplicate query_id in the answer-blind audit archive")

    disposition_rows = []
    selected = []
    for question in questions:
        qid = question["query_id"]
        number = int(qid.rsplit("-", 1)[1])
        audit = audit_by_id.get(qid)
        if audit is None:
            disposition, reason = "deferred_unreviewed_not_released", "No completed answer-blind source reconstruction was recorded."
        elif audit.get("reconstruction_conclusion") != "supported_candidate":
            disposition, reason = "rejected_not_released", audit.get("rejection_reason") or "Question failed source-supported reconstruction."
        elif audit.get("deduplication_status") == "near_duplicate_excluded":
            disposition, reason = "excluded_near_duplicate", audit.get("deduplication_reason", "Near-duplicate candidate excluded.")
        elif 61 <= number <= 80:
            disposition, reason = "deferred_unreviewed_not_released", "This draft batch was not independently reconstructed in the release audit packet."
        else:
            disposition, reason = "included_v2_1", "Answer-blind reconstruction supported; source license and locators match the source registry."
            selected.append((question, audit))
        disposition_rows.append({
            "query_id": qid,
            "disposition": disposition,
            "reason": reason,
            "duplicate_of_query_id": audit.get("duplicate_of_query_id") if audit else None,
            "human_reviewed": False,
        })

    if len(selected) < 506:
        raise SystemExit(f"Only {len(selected)} eligible v2.1 additions; at least 506 are required")
    if len(selected) != 508:
        raise SystemExit(f"Expected the audited release set to contain 508 rows, got {len(selected)}")
    selected_ids = {q["query_id"] for q, _ in selected}
    release_questions = [q for q in questions if q["query_id"] in selected_ids]
    release_audits = [a for a in audits if a["query_id"] in selected_ids]
    write_jsonl(question_path, release_questions)
    write_jsonl(audit_path, release_audits)
    write_jsonl(AUDIT / "v2_1_candidate_disposition_ledger.jsonl", disposition_rows)

    source_doc = read_json(ROOT / "sources.json")
    source_map = {source["source_id"]: source for source in source_doc["sources"]}
    v2_split_doc = read_json(AUDIT / "v2_split_manifest.json")
    family_assignment = {item["source_id"]: item for item in v2_split_doc["family_assignments"]}
    new_records = []
    new_assignments = []
    for question, audit in selected:
        qid = question["query_id"]
        source_ids = question["source_ids"]
        source_rows = [source_map.get(sid) for sid in source_ids]
        if any(source is None for source in source_rows):
            raise SystemExit(f"{qid}: source registry entry missing")
        if source_ids != audit.get("source_ids"):
            raise SystemExit(f"{qid}: source IDs differ between question packet and reconstruction")
        actual_hashes = [source["original_report_sha256"] for source in source_rows]
        if actual_hashes != audit.get("source_pdf_sha256"):
            raise SystemExit(f"{qid}: reconstructed source PDF hash does not match the registry")
        split = question.get("split")
        family_ids = [family_assignment.get(sid, {}).get("family_id") or source.get("source_family_id") or f"iicr-family-{sid.lower()}" for sid, source in zip(source_ids, source_rows)]
        source_splits = {family_assignment.get(sid, {}).get("split") or source.get("preassigned_split") for sid, source in zip(source_ids, source_rows)}
        if len(source_splits) != 1:
            raise SystemExit(f"{qid}: linked sources were assigned to different splits")
        assigned_source_split = next(iter(source_splits))
        if assigned_source_split and assigned_source_split != split:
            raise SystemExit(f"{qid}: question split differs from preassigned source-family split")
        licenses = {source.get("license") for source in source_rows}
        if None in licenses or len(licenses) != 1:
            raise SystemExit(f"{qid}: cross-document record has missing or incompatible source licenses")
        license_name = next(iter(licenses))
        facts = audit.get("required_facts", [])
        evidence = audit.get("evidence", [])
        fact_ids = [fact["fact_id"] for fact in facts]
        evidence_sources = []
        for item in evidence:
            evidence_sources.append({
                "source_id": item["source_id"],
                "element_id": item["element_id"],
                "locator_type": item["locator_type"],
                "pdf_page": item["pdf_page"],
                "printed_page": None,
                "element_summary": item["element_summary"],
                "supports_fact_ids": item["supports_fact_ids"],
                **({"locator_details": copy.deepcopy(item["locator_details"])} if item.get("locator_details") else {}),
            })
        cited_fact_ids = {fact_id for item in evidence_sources for fact_id in item["supports_fact_ids"]}
        if cited_fact_ids != set(fact_ids):
            raise SystemExit(f"{qid}: cited evidence does not cover all reconstructed facts")
        if any(set(item["supports_fact_ids"]) - set(fact_ids) for item in evidence_sources):
            raise SystemExit(f"{qid}: evidence refers to an undeclared reconstructed fact")
        if any(item["source_id"] not in source_ids for item in evidence_sources):
            raise SystemExit(f"{qid}: evidence cites an undeclared source")

        attributions = [source["required_attribution"] for source in source_rows]
        adaptation_notices = [source["required_adaptation_disclaimer"] for source in source_rows]
        translations = [source["translation_disclaimer"] for source in source_rows if source.get("translation_disclaimer")]
        obligations = []
        for source in source_rows:
            obligations.append({
                "source_id": source["source_id"],
                "source_license": source["license"],
                "license_url": source["license_url"],
                "required_attribution": source["required_attribution"],
                "required_adaptation_disclaimer": source["required_adaptation_disclaimer"],
                "translation_disclaimer": source.get("translation_disclaimer"),
                "third_party_content_limitations": source["third_party_content_limitations"],
                "sharealike_applies_to_adapted_record": "SA" in source["license"],
                "reuse_authorization_status": "source_license_recorded",
            })
        facts_review = []
        for fact in facts:
            locators = [item["element_id"] for item in evidence_sources if fact["fact_id"] in item["supports_fact_ids"]]
            facts_review.append({"fact_id": fact["fact_id"], "cited_element_ids": locators, "review_status": "supported_by_source_page_and_locator"})

        connected_group = "v2_1-" + "--".join(sid.lower() for sid in source_ids)
        task_family = question["task_family"]
        record = {
            "schema_version": "iicr_report_qa_v2_1",
            "dataset_version": "2.1.0",
            "annotation_version": "iicr-ai-assisted-candidate-v2.1",
            "query_id": qid,
            "gold_candidate": False,
            "question": question["question"],
            "answerability": "answerable",
            "gold_answer": audit["reconstructed_answer"],
            "required_facts": facts,
            "gold_evidence_sets": [{
                "evidence_set_id": f"{qid}-E1",
                "equivalent_group_id": f"{qid}-EQ1",
                "page_reference_scheme": "1-based physical PDF page; no printed page asserted unless separately verified",
                "required_fact_ids": fact_ids,
                "sources": evidence_sources,
            }],
            "gold_quality": {
                "source_support_status": "ai_source_reconstructed_candidate",
                "human_reviewed": False,
                "independent_human_double_annotation": "not_performed",
                "heldout_gold_accessed": False,
                "source_review_provenance": {
                    "reviewer": "AI-assisted answer-blind source reconstruction",
                    "review_type": "question-only reconstruction against cited official Chinese source PDF",
                    "reviewed_on": REVIEW_DATE,
                    "source_text_written_to_package": False,
                    "candidate_answer_in_review_input": False,
                    "independent_reviewer": False,
                },
                "required_facts_review": facts_review,
                "semantic_review_status_in_ledger": "ai_answer_blind_reconstruction_match",
                "reviewed_on": REVIEW_DATE,
            },
            "publication_rights": {
                "dataset_license": license_name,
                "record_license": license_name,
                "license_url": source_rows[0]["license_url"],
                "license_name": license_name,
                "license_scope": "This record and its adapted QA metadata only; no single license applies to all records in the mixed-license repository.",
                "status": "licensed_record_level",
                "rights_assessment_is_legal_opinion": False,
                "source_attribution_required": True,
                "required_source_attributions": attributions,
                "required_adaptation_disclaimers": adaptation_notices,
                "translation_disclaimers": translations,
                "modification_notice": "Question, answer and required-fact summaries are AI-assisted paraphrases of cited source content. No source PDF, image, table, figure, map or long source passage is included.",
                "source_license_obligations": obligations,
                "third_party_content_reused": False,
                "third_party_content_review_status": "not_applicable_to_paraphrased_text; third-party source content is not reproduced",
                "source_excerpt_included": False,
                "source_media_included": False,
                "source_pdf_included": False,
                "source_pdf_redistribution": "not_included_in_package",
            },
            "source_ids": source_ids,
            "source": "; ".join(source["title_chinese"] for source in source_rows),
            "source_refs": [source_ref(source) for source in source_rows],
            "domain_id": "MAIN_INTERNET_ICT",
            "document_id": family_ids[0],
            "document_scope": source_ids,
            "family_id": family_ids[0],
            "family_ids": family_ids,
            "connected_group_id": connected_group,
            "split": split,
            "split_assignment_version": SPLIT_VERSION,
            "task_type": task_family,
            "task_family": task_family,
            "task_subtype": question["task_subtype"],
            "modality_tags": ["text"],
            "human_reviewed": False,
            "review_status": "ai_answer_blind_reconstruction_match",
            "review_provenance": {
                "reviewer": "AI-assisted source reconstruction",
                "model": audit["review_model"],
                "prompt_sha256": audit["review_prompt_sha256"],
                "reviewed_on": REVIEW_DATE,
                "source_files": [{"source_id": sid, "sha256": source["original_report_sha256"]} for sid, source in zip(source_ids, source_rows)],
                "candidate_answer_in_review_input": False,
                "reconstruction_conclusion": "match_supported_by_cited_source_pages",
                "independent_reviewer": False,
                "method_limit": audit["review_method_limit"],
            },
            "recommended_for_evaluation": True,
            "recommendation_status": "AI-assisted source-reconstructed candidate; not gold; no independent human review; included in the unified recommended subset per dataset-owner instruction",
            "supersedes_query_id": None,
            "split_provenance": {
                "assignment_version": SPLIT_VERSION,
                "assignment_timing": "inherited from source-family assignments made before v2.0.0 question drafting",
                "split": "inherited_pre_annotation_source_family_assignment",
                "pre_annotation_split": True,
            },
            "lineage": {"v2_annotation": "new_v2_1_record", "supersedes_query_id": None},
        }
        new_records.append(record)
        new_assignments.append({
            "query_id": qid,
            "split": split,
            "connected_component_id": connected_group,
            "family_ids": family_ids,
            "source_ids": source_ids,
            "task_type": task_family,
            "task_family": task_family,
            "task_subtype": question["task_subtype"],
            "assignment_version": SPLIT_VERSION,
            "assignment_timing": "inherited_from_source_family_assignments_made_before_v2.0.0_question_drafting",
            "pre_annotation_split": True,
            "human_reviewed": False,
        })

    if any("______" in r["question"] for r in new_records):
        raise SystemExit("A cloze candidate cannot enter the v2.1 addition set")
    combined_records = old_records + new_records
    combined_assignments = old_assignments + new_assignments
    if len(combined_records) != 2000 + len(new_records):
        raise SystemExit("Unexpected combined record count")
    if len({r["query_id"] for r in combined_records}) != len(combined_records):
        raise SystemExit("Duplicate IDs in combined dataset")

    # Write exact frozen v2.0.0 bytes first, then append v2.1 records.
    (ROOT / "records.jsonl").write_bytes(frozen_records_bytes + "".join(compact(row) + "\n" for row in new_records).encode("utf-8"))
    (ROOT / "split_assignments.jsonl").write_bytes(frozen_assignments_bytes + "".join(compact(row) + "\n" for row in new_assignments).encode("utf-8"))

    old_counts = Counter(sid for row in old_records for sid in row.get("source_ids", []))
    current_counts = Counter(sid for row in combined_records for sid in row.get("source_ids", []))
    for source in source_doc["sources"]:
        sid = source["source_id"]
        source["v2_0_record_count"] = old_counts[sid]
        source["v2_1_added_record_count"] = current_counts[sid] - old_counts[sid]
        source["active_v2_record_count"] = current_counts[sid]
        if "target_records" in source:
            source["v2_0_planned_record_count"] = source.pop("target_records")
    source_doc.update({
        "schema_version": "iicr_source_registry_v2_1",
        "dataset_version": "2.1.0",
        "source_count": len(source_map),
        "review_provenance": "The 508 v2.1 records use answer-blind AI reconstruction against official Chinese source editions already registered and licensed in v2.0.0. Twenty additional drafts were deferred because no completed reconstruction audit was present; six invalid-label drafts and eight near duplicates were excluded. No independent human review is claimed. The 1,107 v2.0.0 sentence-cloze records remain pending content and third-party attribution review and remain in recommended per owner instruction.",
    })
    (ROOT / "sources.json").write_text(json.dumps(source_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (ROOT / "audit" / "v2_1_split_manifest.json").write_text(json.dumps({
        "version": SPLIT_VERSION,
        "dataset_version": "2.1.0",
        "assignment_timing": "v2.1 records inherit source-family assignments fixed before v2.0.0 question drafting",
        "source_family_assignments": sorted([
            {
                "source_id": sid,
                "source_family_id": family_assignment.get(sid, {}).get("family_id") or source_map[sid].get("source_family_id"),
                "split": family_assignment.get(sid, {}).get("split") or source_map[sid].get("preassigned_split"),
            }
            for sid in {sid for row in new_records for sid in row["source_ids"]}
        ], key=lambda item: item["source_id"]),
        "new_record_count": len(new_records),
        "split_counts": dict(Counter(row["split"] for row in new_records)),
        "cross_document_source_sets_share_one_preassigned_split": True,
        "historical_and_v2.0.0_assignments_preserved_byte_for_byte": True,
        "human_reviewed": False,
        "note": "All v2.1 records use source documents already in the v2.0.0 registry. The 20 unaudited draft questions are deferred and are not active records.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "record_count": len(combined_records),
        "v2_1_added": len(new_records),
        "v2_1_split_counts": dict(Counter(r["split"] for r in new_records)),
        "v2_1_dispositions": dict(Counter(row["disposition"] for row in disposition_rows)),
        "v2_0_records_sha256": sha256(frozen_records_bytes),
        "v2_0_split_assignments_sha256": sha256(frozen_assignments_bytes),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
