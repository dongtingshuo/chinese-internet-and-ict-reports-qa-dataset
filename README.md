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

**Version:** 2.0.0 · **Language:** Chinese · **Unified corpus:** 2,000 records · **Recommended subset:** 2,000 records

This release keeps all 833 records from v1.2.0 in one unified corpus and adds 1,167 records. The exact v1.2.0 package remains under `history/v1.2.0/`.

## Contents

- 833 historical records, 60 AI-assisted source-reconstructed candidates, and 1,107 rule-generated sentence-cloze candidates.
- 61 source documents across 50 report families and 10 consolidated publishing institutions. CAICT accounts for 506 records (25.3%).
- TRAIN/DEV/TEST contain 1,377/300/323 records. New source families were assigned before question drafting; historical splits retain their post-annotation provenance.
- Both Hugging Face Viewer configurations contain the same 2,000 records. All rows remain in `recommended` at the dataset owner's direction; use each row's `review_status` when selecting evaluation data.
- Each of the 1,107 cloze questions contains one short sentence excerpt from an authorized Chinese source, with one masked value, term, or clause. No source PDF, image, figure, table, or long passage is included.

## Review status and limitations

The 1,107 cloze candidates were produced by a deterministic script from local text extracted from 32 ITU and WHO Chinese PDFs. They have not received per-item answer-blind or independent content review. The answer, physical PDF page, source-file hash, sentence hash, generation method, and script hash are recorded, and their status remains `pending_ai_content_verification`. No per-record language-model inference is claimed for these rows.

The 60 other v2 records have AI-assisted source-page reconstruction, without independent human review. The 833 historical rows retain their existing content and split; their v2 answer-blind reconstruction remains pending and some historical source files await revalidation. Inclusion in `recommended` is an owner decision, not a claim of verification or gold status. This release is dominated by short sentence-completion tasks and is not a balanced high-complexity benchmark.

Source rights notices and PDF hashes were checked for the new ITU and WHO documents. Their records carry CC BY-NC-SA 3.0 IGO terms, attribution, adaptation notices, and ShareAlike/noncommercial obligations. Third-party attribution screening for the pending cloze candidates remains incomplete. CAICT's 506 legacy QA rows retain their CC BY 4.0 record license under the dataset owner's republishing authorization; this does not assert a license for the underlying reports.

Historical splits are not blind holdouts, and prior system exposure has not been audited. This package has no RAG baselines or model-performance results and makes no corpus-wide gold-standard claim.

## Licensing

The repository has mixed record-level licensing; no single license applies to the whole dataset. Keep `publication_rights`, source attribution, and applicable adaptation notices with every redistributed row. See `LICENSES.md`, `LICENSE_STATUS.md`, `ATTRIBUTION.md`, and `sources.json`. Hugging Face metadata uses `license: other`.

## Viewer fields

Use `answer_candidate`, `review_status`, and `recommended_for_evaluation` together. `record_json` contains the full record, including source locators and rights metadata.

## Reproduce and validate

With page-marked UTF-8 text extracted locally from the listed source PDFs, regenerate cloze candidates with:

```bash
python3 scripts/generate_v2_cloze_candidates.py --extracted-text-dir /path/to/extracted-text
```

Then run `python3 build_v2_package.py`, `python3 build_hf_splits.py`, `python3 validate_v2_package.py`, and `python3 build_release_metadata.py`. Source PDFs and extracted full-text files are not included in this repository.
