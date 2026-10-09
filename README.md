---
license: other
language:
- zh
task_categories:
- question-answering
tags:
- chinese
- question-answering
- information-retrieval
- ict
- source-grounded
- gold-subset
configs:
- config_name: gold
  data_files:
  - split: train
    path: data/gold/train.jsonl
  - split: validation
    path: data/gold/validation.jsonl
  - split: test
    path: data/gold/test.jsonl
---

# Chinese Internet and ICT Reports QA Dataset

**Release:** v2.2.0 · **Language:** Chinese · **Gold subset:** 2,355 records

This release combines passing records from the earlier corpus with 80 new-ID, human-adjudicated replacements. It is one unified dataset. Only records that pass the documented Gold-subset gates appear in the active data files.

## Contents

- 2,355 source-grounded QA records: 1,573 train, 372 validation, and 410 test.
- 61 registered report sources across 20 source families and 10 publishing organizations.
- Questions, answers, required facts, evidence sets, physical PDF page locators, source hashes, task categories, split provenance, and record-level rights metadata.
- The Dataset Viewer exposes one gold configuration. records.jsonl is the canonical active record file.
- Source PDFs, images, charts, tables, and long passages are not redistributed.

## Gold-subset criteria and review

The gold label applies to these 2,355 released records, not to every historical or candidate item. The subset contains 2,275 eligible records retained from v2.1.0 and 80 passing v2.2.0 replacement records. Baseline item `IICR-V12-0030` was excluded because its question scope permits multiple plausible source-supported answers. Another 140 proposed replacements did not pass all release gates and are not included in this release.

Two reviewers (D and T) independently reconstructed answers, required facts, and evidence for the 2,508-record v2.1.0 baseline. The dataset owner attests that this review was answer/annotation-blind and used no AI or other-person assistance. A third reviewer (S) independently reconstructed and adjudicated designated cases; the owner attests that the first phase was blind and unassisted. Reviewer method statements are not signed in the returned workbooks, so these disclosures are identified as owner-attested. The blind AI audit credited 2,506/2,508 baseline records; the two without credit are excluded. Three historical protocol-deviation attempts were excluded from credit and their queries were separately rerun from clean source-first packets.

See audit/v2_2/RELEASE_AUDIT.md and GOLD_SELECTION_REPORT.json for the release criteria and counts. Gold is an operationally selected subset, not an external certification or a guarantee of zero annotation errors. Historical splits were assigned after annotation and are not blind holdouts. Prior system exposure has not been audited. This release includes no RAG baseline or model-performance claim.

## Licensing and attribution

The dataset has mixed, record-level terms; license: other intentionally avoids assigning one license to the corpus. Preserve each row's publication_rights and follow source-specific attribution and adaptation requirements. See sources.json, LICENSES.md, LICENSE_STATUS.md, and ATTRIBUTION.md. CAICT QA-record reuse authorization is dataset-owner-attested; this does not claim an open license for CAICT reports or permission to redistribute report PDFs.

## Viewer fields

The Viewer exposes query_id, question, answer_candidate, answerability, split, task_family, task_subtype, review_status, recommended_for_evaluation, and record_json. Consult record_json for required facts, evidence, review provenance, and rights. Use records only for purposes compatible with the license attached to each record.
