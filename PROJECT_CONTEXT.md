# Project Context

## Project goal

Maintain the Chinese Internet and ICT Reports QA Dataset as a standalone, source-grounded, mixed record-license corpus. Keep releases reproducible and explicit about source attribution, review status, rights, and split provenance.

## Scope and non-goals

- Maintain this dataset in its own repository, outside the multimodal RAG project folder.
- v2.0.0 unifies all v1.2.0 records with new records in one active dataset; do not make separate version-specific active datasets.
- Do not add RAG baselines or model experiments in this dataset repository.
- Do not claim human review, independent annotation, dataset-wide gold status, or blind holdout where these were not performed.
- The dataset owner confirmed authorization to republish 506 legacy CAICT QA records under their prior CC BY 4.0 record license; this does not assert a license for the underlying source reports.

## Technology and external services

- Canonical package: JSONL records/splits, JSON schema/source registry/manifest, bilingual Markdown docs, and Python build/validation scripts.
- The 32 added ITU/WHO source PDFs and page-marked extracted text are kept outside the repository under `/private/tmp/chinese-ict-v2-sources`; the repository includes neither PDFs nor full extracted text.
- GitHub: `dongtingshuo/chinese-internet-and-ict-reports-qa-dataset`; direct push to `main` is authorized by the dataset owner.
- Hugging Face: `TingshuoDong/chinese-internet-and-ict-reports-qa-dataset`; `license: other` reflects mixed record-level terms.

## Directory map

- `records.jsonl`: unified active corpus.
- `split_assignments.jsonl`: historical assignments plus preassigned new source-family splits.
- `sources.json`: source metadata, official PDF hashes, license notice locations, text extraction hashes for the 32 new sources, attributions, and third-party limits.
- `schema.json`: schema for historical and v2 records.
- `data/`: Hugging Face candidate and recommended split files; both configs include all active rows.
- `audit/`: migration ledger, question-only packet, answer-blind audit for 60 records, pending cloze audit, source manifest, and split manifest.
- `history/v1.2.0/`: immutable v1.2.0 snapshot.
- `scripts/generate_v2_cloze_candidates.py`: deterministic generator for 1,107 sentence-cloze candidates; source text must be extracted separately.
- `build_v2_package.py`: constructs a unified corpus from the frozen v1.2.0 archive and new candidate rows.
- `build_release_metadata.py`: emits the validation report, package manifest, and SHA-256 checksums.
- `validate_v2_package.py`: checks counts, IDs, licenses, evidence, sentence hashes, split isolation, duplicate questions, Viewer rows, and historical snapshot integrity.

## Current v2.0.0 local release state (2026-10-07)

- The frozen v1.2.0 package came from commit `1daf3e1e9adb14223fad95dd31612c3a884b997c`. Its `records.jsonl` SHA-256 is `c1885bfb779928002171d6deb9bc02c2dccd6081364202d7fe69c9fa787a21ae`; its split-assignment SHA-256 is `e6ea3fa7f1eb4bf656766ac90318ffd3a98a5fead2fbfa650e7f98d76a2a8b4d`.
- Unified corpus: 2,000 rows (833 historical + 60 source-reconstructed candidates + 1,107 rule-generated cloze candidates). All rows remain in both Viewer configurations and in `recommended`, per owner instruction.
- Coverage: 61 source documents, 50 report families, 10 consolidated publishing institutions. TRAIN/DEV/TEST = 1,377/300/323. The 506 CAICT records are 25.3% of the unified corpus.
- All 1,107 cloze items are explicitly `pending_ai_content_verification`. The deterministic generator masks one value, term, or clause in a short licensed source sentence; no per-record LLM inference, answer-blind reconstruction, or human review was performed. Third-party attribution screening remains pending. Each record carries a source sentence hash and generator hash.
- The 60 other new candidates have AI-assisted answer-blind source reconstruction without independent human review. All 833 historical rows preserve their original question/answer/facts/evidence/source IDs/splits and remain pending v2 answer-blind reconstruction; some historical source files also await revalidation.
- The 1,107 cloze rows use 32 ITU/WHO Chinese source documents with CC BY-NC-SA 3.0 IGO notices. Their row-level attribution, adaptation, noncommercial, and ShareAlike terms are retained. No source PDFs/media or full extracted text are packaged; each cloze question contains one short sentence excerpt.
- Local package validation passed with zero structural, rights-field, split, hash, and duplicate findings. Exact/near duplicate counts are zero at the current 0.82 threshold. The v1.2.0 snapshot hashes match.
- GitHub `main` was pushed at commit `4e4a472`. Hugging Face received the 2,000-row package at commit `0b8cb466ea3f5e1b326094d9039b4103bd820d7b`; all 65 paths listed in `SHA256SUMS` matched the downloaded Hub files. Dataset Viewer endpoints `/is-valid`, `/splits`, `/parquet`, and `/size` still return HTTP 500, while the `stanfordnlp/imdb` control returns HTTP 200. Viewer counts are therefore unverified; do not tag v2.0.0 until they succeed.

## Important decisions

- Keep historical and newly added rows together in one unified dataset.
- All 2,000 records remain in `recommended` at the dataset owner's direction. `review_status` is authoritative; recommendation does not imply verification.
- Keep record-level mixed licensing. Do not claim a repository-wide license. The 506 legacy CAICT record authorization is separate from any source-report license.
- Keep sentence-cloze excerpts transparently marked and licensed; do not include reports, images, tables, figures, or long passages.
- New source families are assigned before drafting. Historical splits were assigned after annotation and are not blind holdouts; prior system exposure is unaudited.

## Release procedure

1. If regenerating clozes, extract page-marked UTF-8 text from the source PDFs outside the repo and run `python3 scripts/generate_v2_cloze_candidates.py --extracted-text-dir <directory>`; extraction hashes are checked against `audit/v2_expansion_sources.json`.
2. Run `python3 build_v2_package.py` and `python3 build_hf_splits.py`.
3. Run `python3 validate_v2_package.py`, then `python3 build_release_metadata.py`; inspect `VALIDATION_REPORT.json`, `manifest.json`, and `SHA256SUMS`.
4. Confirm no source PDFs/media/full extracted text are packaged. Push the unified dataset directly to GitHub `main` and synchronize the same payload to Hugging Face.
5. Compare remote data-file hashes and verify Viewer counts/splits. Add a release tag only after Viewer verification succeeds.

## Prioritized TODOs

1. Sync final validation metadata to GitHub and Hugging Face, verify all Hub file hashes, and retry Viewer split counts; tag v2.0.0 only after Viewer verification succeeds.
2. Complete content and third-party attribution review of the 1,107 sentence-cloze candidates while keeping their status visible.
3. Complete v2 answer-blind reconstruction for the 833 historical rows and revalidate source files marked pending.
4. Add a more balanced set of multi-hop, cross-document, table/figure, and answerability tasks before describing the corpus as a complex reasoning benchmark.
