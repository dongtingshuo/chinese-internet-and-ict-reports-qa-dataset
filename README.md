---
license: other
configs:
- config_name: candidates
  data_files:
  - split: train
    path: data/candidates_train.jsonl
  - split: validation
    path: data/candidates_validation.jsonl
  - split: test
    path: data/candidates_test.jsonl
- config_name: recommended
  data_files:
  - split: train
    path: data/recommended/train.jsonl
  - split: validation
    path: data/recommended/validation.jsonl
  - split: test
    path: data/recommended/test.jsonl
---

# Chinese Internet and ICT Reports QA Dataset

**Version:** 2.1.0 · **Language:** Chinese · **Unified corpus:** 2,508 records · **Recommended subset:** 2,508 records

Version 2.1.0 preserves the complete v2.0.0 corpus and appends 508 non-cloze, source-reconstructed QA records in the same dataset. The exact v2.0.0 package is archived under `history/v2.0.0/`.

## Contents

- 833 historical records, 60 earlier source-reconstructed candidates, 1,107 rule-generated sentence-cloze candidates, and 508 v2.1 source-reconstructed questions.
- 61 source documents across 50 report families and 10 consolidated publishing institutions. The 508 additions use already registered Chinese sources and do not add source documents.
- TRAIN/DEV/TEST contain 1,681/397/430 records. The 508 additions inherit preassigned source-family splits (304/97/107); linked source families stay together.
- Both Hugging Face Viewer configurations contain all 2,508 records. All rows remain in `recommended` per dataset-owner instruction; use each row's `review_status` when selecting data.
- The package contains no source report PDFs, images, tables, figures, or long source passages. The 1,107 v2.0 cloze rows retain their short licensed sentence excerpts and their pending review status.

## Review status and limitations

The 508 v2.1 questions received an AI-assisted second reconstruction from question-only packets and the cited official Chinese source PDFs. Answers, required facts, physical PDF page locators, and source hashes are recorded in `audit/v2_1_answer_blind_reconstruction.jsonl`. This was not an independent AI session or human review; every new row remains `human_reviewed: false` and is not labeled gold. Twenty draft questions without a completed reconstruction audit, six questions with invalid labels, and eight near duplicates were kept out of the v2.1 release; dispositions are recorded in `audit/v2_1_candidate_disposition_ledger.jsonl`.

For table-supported questions, `locator_details` identifies the table and the relevant row/column labels or footnote marker; narrative evidence points to the physical PDF page and text region. These locator details identify source evidence without reproducing the source table.

The 1,107 sentence-cloze candidates remain `pending_ai_content_verification`; their answer was available to the deterministic masking process, and third-party attribution screening remains pending. The 833 historical rows also retain their previous review statuses; v2.1 does not claim that they were answer-blind reconstructed. Recommendation is an owner decision and does not override review status.

## Sources and licensing

The corpus uses mixed record-level licenses; no single license applies to the repository. Each row carries the applicable record license, source attribution, adaptation notice, and other terms. The v2.1 additions are concise paraphrases from sources already listed in `sources.json`; their source hashes, license notices, and translation status are recorded. No report PDFs or media are redistributed. See `LICENSES.md`, `LICENSE_STATUS.md`, `ATTRIBUTION.md`, and per-record `publication_rights`.

Historical splits were assigned after annotation and are not blind holdouts; prior system exposure has not been audited. This package contains no RAG baselines or model-performance results and makes no corpus-wide gold-standard claim.

## Viewer fields

Use `answer_candidate`, `review_status`, and `recommended_for_evaluation` together. `record_json` contains the complete record, evidence locators, and licensing metadata.

## Reproduce and validate

The v2.1 package is rebuilt from the frozen v2.0.0 snapshot and the recorded question-only reconstruction audit:

```bash
python3 build_v2_1_package.py
python3 build_hf_splits.py
python3 validate_v2_package.py
python3 build_release_metadata.py
```

`build_v2_package.py` is the historical v2.0 builder and refuses to overwrite an active v2.1 package. Source PDFs and full extracted text remain outside the repository.
