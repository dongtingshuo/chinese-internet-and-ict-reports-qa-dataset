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

**Version:** 2.0.0 · **Language:** Chinese · **Records:** 387 active candidates · **Recommended AI candidate subset:** 60

This release contains source-grounded questions and concise answer candidates derived from public Chinese Internet, ICT, education-technology, and digital-agriculture reports. Each record links to physical PDF pages and records its source license, attribution, adaptation notice, and third-party-content limits.

## What is included

- 327 prior v1.1/v1.2 records retained as historical candidates, pending v2 source-file revalidation or answer-blind reconstruction. They are not in the recommended subset.
- 60 new AI-assisted candidates from four Chinese report documents, with a separate question-only review packet and source-page reconstruction audit.
- 15 report documents are registered across seven consolidated publishing institutions; four are new in v2.0.0. The original target of 60 reports and 10 institutions has not been reached. Five historical source files still need revalidation.
- 60 recommended candidates split TRAIN/DEV/TEST as 42/9/9. New report families were assigned to splits before question drafting.
- No source PDF, image, table, figure, or long source passage is included.

The active set has 387 records, below the 2,000-record target. This release excludes the 506 CAICT legacy rows from the active corpus because source-level permission to redistribute adaptations was not established in the v1.2.0 source registry. The 506 rows remain in `history/v1.2.0/` and are itemized in the migration ledger. CAICT is 0% of the active v2 corpus.

## Viewer configurations

- **candidates** includes all 387 active rows. Review status distinguishes pending historical candidates from the new AI-assisted set.
- **recommended** includes only the 60 newly source-reconstructed AI candidates. “Recommended” means a candidate subset for research use; it does not mean human verified or gold.

Use `answer_candidate` and `review_status` when loading Viewer rows. `record_json` preserves the full record, including evidence locators and source-rights metadata.

## License

This is a mixed-license dataset. **No single license applies to the repository as a whole.** Each record carries its applicable license and required source attributions. The recommended subset includes 51 records under CC BY-SA 3.0 IGO and 9 FAO-derived records under CC BY-NC-SA 3.0 IGO. Review `LICENSES.md`, `LICENSE_STATUS.md`, `ATTRIBUTION.md`, and the record's `publication_rights` before reuse. Hugging Face metadata uses `license: other` because the package has mixed record-level terms.

## Review and limitations

All new rows were checked against the cited Chinese source pages using an AI-assisted, answer-blind review packet. The same active AI session drafted and checked the questions; no independent reviewer is claimed. `human_reviewed` remains false and `gold_candidate` remains false for all new rows. Historical rows are still pending v2 review. Historical splits were assigned after annotation, and prior system exposure was not audited. No RAG baseline or model-performance result is included.

## Reproduce and validate

Run `python3 build_v2_package.py`, then `python3 build_hf_splits.py`, `python3 build_release_metadata.py`, and `python3 validate_v2_package.py`. See `PROJECT_CONTEXT.md` for the release workflow and `manifest.json` for exact counts and hashes.

## Files

- `records.jsonl`: canonical active record set.
- `sources.json`: report, rights, attribution, and source-file metadata.
- `split_assignments.jsonl`: historical and v2 split provenance.
- `data/`: Hugging Face Viewer splits for candidates and recommended subset.
- `audit/`: v1.2 migration ledger, v2 source-family allocation, and AI review artifacts.
- `history/v1.2.0/`: frozen v1.2.0 snapshot.
