#!/usr/bin/env python3
"""Release-gate validation for the unified v2.1.0 dataset package."""
from __future__ import annotations

import collections
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def digest(data: bytes):
    return hashlib.sha256(data).hexdigest()


def validate(root: Path = ROOT):
    issues = []

    def check(condition, message):
        if not condition:
            issues.append(message)

    records_path = root / "records.jsonl"
    assignments_path = root / "split_assignments.jsonl"
    records_bytes = records_path.read_bytes()
    assignments_bytes = assignments_path.read_bytes()
    rows = read_jsonl(records_path)
    assignments = read_jsonl(assignments_path)
    sources_doc = read_json(root / "sources.json")
    sources = {item["source_id"]: item for item in sources_doc.get("sources", [])}
    schema = read_json(root / "schema.json")

    check(schema.get("title", "").endswith("v2.1.0 record"), "schema title is not v2.1.0")
    check(any(ref.get("$ref") == "#/$defs/new_candidate_v2_1" for ref in schema.get("oneOf", [])), "schema is missing the v2.1 record definition")
    check(sources_doc.get("dataset_version") == "2.1.0", "source registry version mismatch")
    check(sources_doc.get("source_count") == len(sources), "source registry count mismatch")
    check(len(sources) == 61, f"expected 61 registered sources, got {len(sources)}")

    frozen_dir = root / "history" / "v2.0.0"
    frozen_manifest = read_json(frozen_dir / "SNAPSHOT_MANIFEST.json")
    frozen_records = (frozen_dir / "records.jsonl").read_bytes()
    frozen_assignments = (frozen_dir / "split_assignments.jsonl").read_bytes()
    check(digest(frozen_records) == frozen_manifest.get("files", {}).get("records.jsonl"), "frozen v2.0.0 record snapshot hash mismatch")
    check(digest(frozen_assignments) == frozen_manifest.get("files", {}).get("split_assignments.jsonl"), "frozen v2.0.0 assignment snapshot hash mismatch")
    check(records_bytes.startswith(frozen_records), "the active corpus does not preserve the exact v2.0.0 record bytes as a prefix")
    check(assignments_bytes.startswith(frozen_assignments), "the active assignments do not preserve the exact v2.0.0 assignment bytes as a prefix")
    old_rows = read_jsonl(frozen_dir / "records.jsonl")
    old_assignments = read_jsonl(frozen_dir / "split_assignments.jsonl")
    check(len(old_rows) == 2000, f"frozen v2.0.0 row count mismatch: {len(old_rows)}")
    check(len(old_assignments) == 2000, f"frozen v2.0.0 assignment count mismatch: {len(old_assignments)}")

    ids = [row.get("query_id") for row in rows]
    check(len(rows) == 2508, f"expected 2,508 active rows, got {len(rows)}")
    check(len(ids) == len(set(ids)), "duplicate query_id in active records")
    by_id = {row["query_id"]: row for row in rows}
    new_rows = [row for row in rows if str(row.get("query_id", "")).startswith("IICR-V21-")]
    check(len(new_rows) == 508, f"expected 508 v2.1 additions, got {len(new_rows)}")
    check(all(row.get("dataset_version") == "2.0.0" for row in rows[:2000]), "one or more frozen rows have a changed dataset_version")
    check(all(re.fullmatch(r"IICR-V21-[0-9]{4}", row.get("query_id", "")) for row in new_rows), "v2.1 ID format mismatch")
    check(all(row.get("schema_version") == "iicr_report_qa_v2_1" and row.get("dataset_version") == "2.1.0" for row in new_rows), "v2.1 schema/version fields mismatch")
    check(all(row.get("recommended_for_evaluation") is True for row in rows), "not all active records are in recommended")
    check(all(row.get("recommended_for_evaluation") is True and row.get("human_reviewed") is False for row in new_rows), "v2.1 recommendation or human-review status mismatch")
    check(all(row.get("gold_candidate") is False and row.get("review_status") == "ai_answer_blind_reconstruction_match" for row in new_rows), "v2.1 review/gold labels mismatch")
    check(all("______" not in row.get("question", "") for row in new_rows), "a cloze question was included in the v2.1 additions")

    assignment_by_id = {item.get("query_id"): item for item in assignments}
    check(len(assignments) == len(rows) and set(assignment_by_id) == set(by_id), "split assignment IDs do not match the active corpus")
    check(all(by_id[item["query_id"]].get("split") == item.get("split") for item in assignments if item.get("query_id") in by_id), "split assignment disagrees with record split")
    new_assignment_by_id = {item["query_id"]: item for item in assignments if str(item.get("query_id", "")).startswith("IICR-V21-")}

    question_packet = read_jsonl(root / "audit" / "v2_1_question_only.jsonl")
    reconstruction_audit = read_jsonl(root / "audit" / "v2_1_answer_blind_reconstruction.jsonl")
    check(len(question_packet) == len(new_rows) and {item.get("query_id") for item in question_packet} == {item["query_id"] for item in new_rows}, "v2.1 question-only packet IDs mismatch")
    check(len(reconstruction_audit) == len(new_rows) and {item.get("query_id") for item in reconstruction_audit} == {item["query_id"] for item in new_rows}, "v2.1 reconstruction audit IDs mismatch")
    q_by_id = {item["query_id"]: item for item in question_packet}
    a_by_id = {item["query_id"]: item for item in reconstruction_audit}
    for item in question_packet:
        check(not any(key in item for key in ("answer", "gold_answer", "reconstructed_answer", "required_facts")), f"{item.get('query_id')}: answer leaked into question-only packet")

    family_manifest = read_json(root / "audit" / "v2_split_manifest.json")
    source_family_assignments = {item["source_id"]: item for item in family_manifest.get("family_assignments", [])}
    disposition_ledger = read_jsonl(root / "audit" / "v2_1_candidate_disposition_ledger.jsonl")
    disposition_counts = collections.Counter(item.get("disposition") for item in disposition_ledger)
    check(len(disposition_ledger) == 542, f"candidate disposition ledger must cover 542 drafts, got {len(disposition_ledger)}")
    check(disposition_counts == collections.Counter({"included_v2_1": 508, "deferred_unreviewed_not_released": 20, "rejected_not_released": 6, "excluded_near_duplicate": 8}), f"unexpected draft disposition counts: {dict(disposition_counts)}")

    v21_source_counts = collections.Counter()
    v20_source_counts = collections.Counter(sid for row in old_rows for sid in row.get("source_ids", []))
    all_source_splits = collections.defaultdict(set)
    all_family_splits = collections.defaultdict(set)
    all_group_splits = collections.defaultdict(set)
    split_counts = collections.Counter(row.get("split") for row in rows)
    for row in rows:
        for sid in row.get("source_ids", []):
            all_source_splits[sid].add(row.get("split"))
        for family in row.get("family_ids") or ([row.get("family_id")] if row.get("family_id") else []):
            all_family_splits[family].add(row.get("split"))
        group = row.get("connected_group_id") or row.get("legacy_split_component_id")
        if group:
            all_group_splits[group].add(row.get("split"))
    for label, map_value in (("source", all_source_splits), ("family", all_family_splits), ("connected group", all_group_splits)):
        for key, split_set in map_value.items():
            check(len(split_set) == 1, f"{label} spans splits: {key} -> {sorted(split_set)}")

    for row in new_rows:
        qid = row["query_id"]
        q = q_by_id.get(qid, {})
        audit = a_by_id.get(qid, {})
        source_ids = row.get("source_ids", [])
        source_ref_map = {item.get("source_id"): item for item in row.get("source_refs", [])}
        rights = row.get("publication_rights", {})
        obligations = {item.get("source_id"): item for item in rights.get("source_license_obligations", [])}
        facts = row.get("required_facts", [])
        fact_ids = [fact.get("fact_id") for fact in facts]
        check(q.get("question") == row.get("question"), f"{qid}: question-only packet differs from active question")
        check(q.get("source_ids") == source_ids, f"{qid}: question-only source IDs differ")
        check(q.get("split") == row.get("split"), f"{qid}: question-only split differs")
        check(audit.get("question") == row.get("question"), f"{qid}: audit question differs from active question")
        check(audit.get("reconstruction_conclusion") == "supported_candidate", f"{qid}: reconstruction is not supported")
        check(audit.get("candidate_answer_in_review_input") is False, f"{qid}: candidate answer was not hidden from the audit input")
        check(audit.get("human_reviewed") is False and audit.get("independent_reviewer") is False, f"{qid}: audit overstates review status")
        check(audit.get("reconstructed_answer") == row.get("gold_answer"), f"{qid}: answer differs from reconstruction audit")
        check(audit.get("required_facts") == facts, f"{qid}: required facts differ from reconstruction audit")
        check(row.get("review_provenance", {}).get("candidate_answer_in_review_input") is False, f"{qid}: active row does not record answer-blind input")
        check(row.get("review_provenance", {}).get("prompt_sha256") == audit.get("review_prompt_sha256"), f"{qid}: prompt hash mismatch")
        check(row.get("review_provenance", {}).get("reviewed_on") is not None, f"{qid}: review date missing")
        check(set(source_ids) == set(source_ref_map) == set(obligations), f"{qid}: source references or license obligations do not match source IDs")
        check(len({sources.get(sid, {}).get("license") for sid in source_ids}) == 1, f"{qid}: linked source licenses are not compatible")
        check(rights.get("record_license") == rights.get("dataset_license"), f"{qid}: record and dataset license fields differ")
        check(rights.get("source_pdf_included") is False and rights.get("source_media_included") is False and rights.get("source_excerpt_included") is False, f"{qid}: source content/media included or not explicitly excluded")
        check(bool(rights.get("required_source_attributions")) and bool(rights.get("required_adaptation_disclaimers")), f"{qid}: attribution/adaptation obligation missing")

        expected_source_hashes = []
        source_splits = set()
        expected_families = []
        for sid in source_ids:
            source = sources.get(sid, {})
            source_ref = source_ref_map.get(sid, {})
            obligation = obligations.get(sid, {})
            check(sid in sources, f"{qid}: unknown source {sid}")
            if sid not in sources:
                continue
            expected_source_hashes.append(source.get("original_report_sha256"))
            split_assignment = source_family_assignments.get(sid, {})
            source_splits.add(split_assignment.get("split") or source.get("preassigned_split"))
            family = split_assignment.get("family_id") or source.get("source_family_id")
            if family:
                expected_families.append(family)
            v21_source_counts[sid] += 1
            check(source_ref.get("license") == source.get("license"), f"{qid}/{sid}: source ref license mismatch")
            check(source_ref.get("original_report_sha256") == source.get("original_report_sha256"), f"{qid}/{sid}: source ref hash mismatch")
            check(obligation.get("source_license") == source.get("license"), f"{qid}/{sid}: source obligation license mismatch")
            check(obligation.get("required_attribution") == source.get("required_attribution"), f"{qid}/{sid}: attribution mismatch")
            check(obligation.get("required_adaptation_disclaimer") == source.get("required_adaptation_disclaimer"), f"{qid}/{sid}: adaptation disclaimer mismatch")
            check(bool(source.get("license")) and bool(source.get("required_attribution")) and bool(source.get("license_url")), f"{qid}/{sid}: source rights record incomplete")
            check(source.get("source_pdf_included") is False, f"{qid}/{sid}: source PDF marked as included")
        check(audit.get("source_pdf_sha256") == expected_source_hashes, f"{qid}: audit source PDF hashes mismatch")
        check(set(row.get("family_ids", [])) == set(expected_families), f"{qid}: family IDs differ from preassigned source families")
        check(source_splits == {row.get("split")}, f"{qid}: record split differs from source-family assignment")

        evidence_sets = row.get("gold_evidence_sets", [])
        check(len(evidence_sets) == 1, f"{qid}: expected one evidence set")
        evidence = evidence_sets[0].get("sources", []) if evidence_sets else []
        evidence_facts = {fid for locator in evidence for fid in locator.get("supports_fact_ids", [])}
        check(set(evidence_facts) == set(fact_ids), f"{qid}: evidence does not cover exactly the required facts")
        audit_evidence = audit.get("evidence", [])
        check(len(evidence) == len(audit_evidence), f"{qid}: active evidence locator count differs from audit")
        for locator in evidence:
            sid = locator.get("source_id")
            check(sid in source_ids, f"{qid}: evidence cites undeclared source {sid}")
            if sid in sources:
                check(1 <= locator.get("pdf_page", 0) <= sources[sid].get("source_pdf_page_count", 0), f"{qid}/{sid}: physical PDF page out of bounds")
            locator_type = locator.get("locator_type")
            check(locator_type in {"narrative_text_region", "table_cells", "table_footnote"} and bool(locator.get("element_id")) and bool(locator.get("element_summary")), f"{qid}: evidence locator is incomplete")
            if locator_type in {"table_cells", "table_footnote"}:
                details = locator.get("locator_details", {})
                check(bool(details.get("table_id")), f"{qid}: table locator has no table ID")
                if locator_type == "table_cells":
                    check(bool(details.get("row_labels") or details.get("column_labels") or details.get("cell_coordinates")), f"{qid}: table-cell locator has no row/column/cell coordinates")
                else:
                    check(bool(details.get("footnote_marker")), f"{qid}: table-footnote locator has no footnote marker")
            check(set(locator.get("supports_fact_ids", [])) <= set(fact_ids), f"{qid}: evidence refers to an undeclared fact")
        for locator, audit_locator in zip(evidence, audit_evidence):
            check(locator.get("source_id") == audit_locator.get("source_id") and locator.get("pdf_page") == audit_locator.get("pdf_page") and locator.get("element_id") == audit_locator.get("element_id") and locator.get("locator_type") == audit_locator.get("locator_type") and locator.get("supports_fact_ids") == audit_locator.get("supports_fact_ids") and locator.get("locator_details") == audit_locator.get("locator_details"), f"{qid}: active locator differs from answer-blind audit")

        assignment = new_assignment_by_id.get(qid, {})
        check(assignment.get("split") == row.get("split") and assignment.get("source_ids") == source_ids and assignment.get("family_ids") == row.get("family_ids"), f"{qid}: assignment entry differs from record")
        check(assignment.get("pre_annotation_split") is True, f"{qid}: preassigned split provenance missing")

    expected_splits = {"TRAIN": 1681, "DEV": 397, "TEST": 430}
    check(dict(split_counts) == expected_splits, f"split counts mismatch: {dict(split_counts)}")
    for sid, source in sources.items():
        check(source.get("active_v2_record_count") == v20_source_counts[sid] + v21_source_counts[sid], f"{sid}: active source record count mismatch")
        check(source.get("v2_0_record_count") == v20_source_counts[sid], f"{sid}: v2.0 source count mismatch")
        check(source.get("v2_1_added_record_count") == v21_source_counts[sid], f"{sid}: v2.1 source count mismatch")

    # Exact and near-duplicate check for every new question against the full active corpus.
    normalized = [re.sub(r"\W+", "", row.get("question", "")).lower() for row in rows]
    exact_dupes = len(normalized) - len(set(normalized))
    check(exact_dupes == 0, f"exact duplicate question count is {exact_dupes}")
    grams = [{text[i:i+4] for i in range(max(0, len(text)-3))} for text in normalized]
    gram_rows = collections.defaultdict(list)
    for idx, values in enumerate(grams):
        for value in values:
            gram_rows[value].append(idx)
    new_indexes = {idx for idx, row in enumerate(rows) if str(row.get("query_id", "")).startswith("IICR-V21-")}
    overlaps = collections.Counter()
    for idx in new_indexes:
        for value in grams[idx]:
            indexes = gram_rows[value]
            if len(indexes) > 100:
                continue
            for other in indexes:
                if other != idx:
                    overlaps[(min(idx, other), max(idx, other))] += 1
    near_pairs = []
    for (left, right), shared in overlaps.items():
        minimum = min(len(grams[left]), len(grams[right]))
        if shared < max(3, int(minimum * 0.2)):
            continue
        ratio = difflib.SequenceMatcher(None, normalized[left], normalized[right]).ratio()
        if ratio >= 0.82:
            near_pairs.append({"query_ids": [rows[left]["query_id"], rows[right]["query_id"]], "similarity": round(ratio, 3)})
    check(not near_pairs, f"near-duplicate question pairs >=0.82: {near_pairs[:10]}")

    for config, prefix in (("candidates", "candidates_"), ("recommended", "recommended/")):
        for split, filename in (("TRAIN", "train"), ("DEV", "validation"), ("TEST", "test")):
            path = root / "data" / (f"{prefix}{filename}.jsonl" if config == "candidates" else f"recommended/{filename}.jsonl")
            viewer = read_jsonl(path)
            expected = [row for row in rows if row.get("split") == split and (config == "candidates" or row.get("recommended_for_evaluation") is True)]
            check(len(viewer) == len(expected), f"{config}/{split}: viewer row count mismatch")
            check([item.get("query_id") for item in viewer] == [row.get("query_id") for row in expected], f"{config}/{split}: viewer row order/IDs mismatch")
            for item, row in zip(viewer, expected):
                check(item.get("recommended_for_evaluation") == row.get("recommended_for_evaluation"), f"{config}/{split}/{row['query_id']}: Viewer recommendation flag mismatch")
                try:
                    embedded = json.loads(item.get("record_json", "{}"))
                except json.JSONDecodeError:
                    embedded = {}
                check(embedded == row, f"{config}/{split}/{row['query_id']}: embedded record_json differs")

    media_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
    media = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file() and path.suffix.lower() in media_extensions and ".git" not in path.parts]
    check(not media, f"source PDFs or media found in package: {media[:10]}")

    report_families = {family for row in rows for family in (row.get("family_ids") or ([row.get("family_id")] if row.get("family_id") else []))}
    publishing_entities = {entity for source in sources.values() for entity in source.get("publishing_institution_entities", [])}
    license_counts = collections.Counter(row.get("publication_rights", {}).get("record_license") for row in rows)
    stats = {
        "record_count": len(rows),
        "v2_0_record_count": len(old_rows),
        "v2_1_added_record_count": len(new_rows),
        "recommended_count": sum(row.get("recommended_for_evaluation") is True for row in rows),
        "split_counts": dict(split_counts),
        "v2_1_split_counts": dict(collections.Counter(row.get("split") for row in new_rows)),
        "source_document_count": len(sources),
        "report_family_count": len(report_families),
        "publishing_institution_count": len(publishing_entities),
        "record_license_counts_raw": dict(license_counts),
        "exact_duplicate_question_count": exact_dupes,
        "near_duplicate_pair_count_at_0_82": len(near_pairs),
        "disposition_counts": dict(disposition_counts),
        "v2_0_records_sha256": digest(frozen_records),
        "v2_0_split_assignments_sha256": digest(frozen_assignments),
        "source_media_file_count": len(media),
    }
    return issues, stats


if __name__ == "__main__":
    problems, stats = validate()
    print(json.dumps({"issues": problems, "stats": stats}, ensure_ascii=False, indent=2))
    sys.exit(1 if problems else 0)
