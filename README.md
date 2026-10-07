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

**Version:** 2.0.0 · **Language:** Chinese · **Unified corpus:** 893 records · **Recommended subset:** 893 records

This version keeps all 833 records from v1.2.0 in the current corpus and adds 60 new AI-assisted candidates. Every record retains its original ID and split; the exact v1.2.0 package is also preserved under `history/v1.2.0/`.

## Contents

- 833 historical v1.2.0 records and 60 new candidates.
- Both `candidates` and `recommended` Viewer configurations contain the same 893 records. The historical records are included in the recommended subset at the dataset owner's direction; their `review_status` remains explicit and must be considered by users.
- Unified TRAIN/DEV/TEST counts are 621/137/135. Historical splits were assigned after annotation; the 60 new records use source-family assignments made before drafting.
- The source registry, record metadata, and manifest give exact document, institution, split, license, review, and hash counts.
- No source PDF, image, table, figure, or long source passage is included.

## Review status and limitations

All 833 historical rows still need the v2 answer-blind content reconstruction; some historical source files also need revalidation. Their inclusion in `recommended` does not imply completed review, human verification, or gold-standard status. The 60 new records have AI-assisted source-page reconstruction, but no independent human review. Historical splits are not blind holdouts, and prior system exposure has not been audited.

The merged corpus contains 506 CAICT legacy records (56.7% of the total), so the prior goal of reducing CAICT below 45% is not met. These records retain their existing CC BY 4.0 license for the QA records. The dataset owner confirmed authorization to republish them; this does not assert that the underlying CAICT reports use CC BY 4.0. Original source reports are not included.

No RAG baseline or model-performance result is included. See `DATA_CARD.md`, `LICENSE_STATUS.md`, and `VALIDATION_REPORT.json` for scope and release gates.

## Licensing

This is a mixed-license dataset. **No single license applies to the repository as a whole.** Each record carries its applicable record license and required attribution. For legacy CAICT rows, the record license applies to the QA record only; the source report's license is not asserted. See `LICENSES.md`, `ATTRIBUTION.md`, `sources.json`, and each record's `publication_rights` before reuse. Hugging Face metadata uses `license: other`.

## Viewer fields

Use `answer_candidate`, `review_status`, and `recommended_for_evaluation` when loading Viewer rows. `record_json` preserves each full record, including evidence locators and record-level rights metadata.

## Reproduce and validate

Run `python3 build_v2_package.py`, `python3 build_hf_splits.py`, `python3 validate_v2_package.py`, then `python3 build_release_metadata.py`. See `PROJECT_CONTEXT.md` for the release workflow and `manifest.json` for exact counts and hashes.
