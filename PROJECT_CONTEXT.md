# Project Context

## Project goal

Maintain the Chinese Internet and ICT Reports QA Dataset as a standalone, source-grounded, mixed record-license corpus. Keep every release reproducible and explicit about source attribution, evidence, review status, rights, and split provenance.

## Scope and non-goals

- This repository is separate from the multimodal RAG graduation project.
- Keep historical and newly added records together in one active dataset; archive snapshots under `history/` for reproducibility.
- Do not add RAG baselines or model-performance experiments here.
- Do not claim human review, independent annotation, corpus-wide gold status, or blind holdout when those were not performed.
- The dataset owner confirmed authorization to republish the 506 legacy CAICT QA records under their prior CC BY 4.0 record license; this does not assert a license for the source reports.

## Technology and external services

- Canonical package: JSONL records and Viewer splits, JSON Schema/source registry/manifest, bilingual Markdown documentation, and Python build/validation scripts.
- Source PDFs and page-marked extracted text stay outside the repository under `/private/tmp/chinese-ict-v2-sources`; never package report PDFs, media, or full extracted text.
- GitHub: `dongtingshuo/chinese-internet-and-ict-reports-qa-dataset`; direct push to `main` is authorized by the dataset owner.
- Hugging Face: `TingshuoDong/chinese-internet-and-ict-reports-qa-dataset`; account `TingshuoDong` is logged in. `license: other` reflects mixed record-level terms, not one corpus-wide license.

## Directory map and entry points

- `records.jsonl`: unified active corpus.
- `split_assignments.jsonl`: historical assignments plus new records' source-family assignments.
- `sources.json`: official report metadata, file hashes, Chinese-version/translation provenance, rights notices, attribution, and third-party limitations.
- `schema.json`: schemas for historical rows and v2.0/v2.1 rows; v2.1 table evidence includes `locator_details`.
- `data/`: Hugging Face `candidates` and `recommended` Viewer configs, each split into train/validation/test JSONL files.
- `audit/`: original v2 artifacts plus v2.1 question-only packets, answer-blind reconstruction, candidate dispositions, and split manifest.
- `history/v1.2.0/`, `history/v2.0.0/`: frozen release snapshots.
- `build_v2_1_package.py`: builds the unified corpus from the frozen v2.0.0 snapshot and v2.1 audit files.
- `build_hf_splits.py`: regenerates both Hugging Face Viewer configurations.
- `validate_v2_1_package.py` / `validate_v2_package.py`: validate the active v2.1 release and historical integrity.
- `build_release_metadata.py`: emits `VALIDATION_REPORT.json`, `manifest.json`, and `SHA256SUMS` after validation.

## Current v2.1.0 release state (2026-10-07)

- Active corpus has 2,508 rows: exact 2,000-row v2.0.0 prefix plus 508 new `IICR-V21-####` non-cloze QA rows. All rows remain in the recommended subset per owner instruction; recommendation never overrides each row's review status.
- The original v2.0.0 `records.jsonl` SHA-256 is `820edd48ad06930bb432c84db3d16e391616acea843876201f782877cb0851ba`; `split_assignments.jsonl` SHA-256 is `294f6e608d98e7221209e1f0095f98ef5aa99beb6a96bfb38c3a6f83605366a7`. Active v2.1 records and assignments preserve both original files byte-for-byte as prefixes.
- TRAIN/DEV/TEST = 1,681/397/430 overall; the 508 v2.1 additions are 304/97/107. The corpus has 61 source documents, 50 report families, and 10 consolidated publishing institutions. Additions use sources already registered in v2.0.0.
- Every new record has `dataset_version: 2.1.0`, `human_reviewed: false`, `gold_candidate: false`, and `review_status: ai_answer_blind_reconstruction_match`. The question-only review input excludes candidate answers; the same active AI session drafted and checked the questions, so independent review is not claimed.
- The 542-draft ledger records 508 included, 20 deferred without completed reconstruction audit, 6 rejected for invalid labels, and 8 excluded as near duplicates. Exact and near-duplicate checks at the 0.82 threshold report zero collisions among active records.
- Table evidence uses physical PDF page numbers plus table IDs and row/column or footnote details. A locator audit corrected the standard-definition rationale question to cite physical page 13 and the related terminology table on page 20.
- Per-record licenses and source obligations remain mixed; there is no repository-wide license. The 1,107 sentence-cloze rows remain pending content and third-party attribution review; the 833 older historical rows retain prior review statuses and have not received v2.1 answer-blind reconstruction.
- Local package validation passes with zero findings; Viewer files match canonical split counts and SHA256SUMS verifies. No source PDFs/media/full extracted text are in the package. GitHub and Hugging Face v2.1 synchronization and remote Viewer verification are the remaining release steps.

## Release procedure

1. Keep source PDFs and full extracted text outside this repository; verify each source hash against `sources.json`.
2. Run `python3 build_v2_1_package.py` and `python3 build_hf_splits.py`.
3. Run `python3 validate_v2_package.py`, then `python3 build_release_metadata.py`; verify `SHA256SUMS` and inspect the release report/manifest.
4. Push the reviewed package to GitHub `main` and upload the same package to the Hugging Face dataset repo.
5. Compare remote files with local hashes and verify all six Viewer splits/counts after processing completes; do not claim Viewer verification before it succeeds.

## Prioritized TODOs

1. Push v2.1.0 to GitHub and Hugging Face; verify remote package hashes and Dataset Viewer counts.
2. Complete content and third-party attribution review of the 1,107 sentence-cloze candidates while keeping their status visible.
3. Complete v2 answer-blind reconstruction for the 833 historical rows and revalidate sources whose status is pending.
4. Continue balancing complex question types only with source-supported records and verified rights.
