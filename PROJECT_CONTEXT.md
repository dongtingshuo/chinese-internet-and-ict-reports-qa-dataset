# Project Context

## Project goal

Maintain a public Chinese Internet and ICT Reports QA dataset as a source-grounded, mixed record-license corpus. Keep each release reproducible and explicit about source attribution, review status, rights, and split provenance.

## Scope and non-goals

- Current release: keep all v1.2.0 records in the active v2.0.0 corpus, add new Chinese-source candidates, and publish one unified dataset to GitHub and Hugging Face.
- Do not add retrieval/RAG baselines, model experiments, source PDFs, source images, or long source passages.
- Do not claim human review, independent annotation, dataset-wide gold status, or blind holdout where these were not performed.
- The dataset owner confirmed authorization to republish the 506 legacy CAICT QA records. Their prior CC BY 4.0 record license is retained; this does not assert a license for the underlying reports.

## Technology and external services

- Canonical package: JSONL records and split assignments, JSON source registry/schema/manifest, Markdown release documentation, and Python build/validation scripts.
- Source PDFs are inspected outside the repository under `/private/tmp/chinese-ict-v2-sources`; never copy those PDFs into the package.
- GitHub: `dongtingshuo/chinese-internet-and-ict-reports-qa-dataset`; direct updates to `main` are authorized for this release.
- Hugging Face: `TingshuoDong/chinese-internet-and-ict-reports-qa-dataset`; metadata uses `license: other` for mixed record-level licensing.

## Directory map

- `records.jsonl`: canonical unified active corpus.
- `split_assignments.jsonl`: preserved historical assignments plus preassigned v2 source-family assignments.
- `sources.json`: source metadata, source-license terms where established, user-confirmed legacy authorization, attribution, hashes, and third-party limits.
- `schema.json`: record schema for the legacy and new record families.
- `data/`: candidate and recommended Hugging Face Viewer splits; both configs contain all active rows.
- `audit/`: migration ledger, question-only review packet, reconstruction provenance, and v2 split manifest.
- `history/v1.2.0/`: immutable original v1.2.0 package snapshot.
- `build_v2_package.py`: deterministic union of the snapshot and new records.
- `build_release_metadata.py`: validation report, manifest, and checksum generator.
- `validate_v2_package.py`: structural, rights, split, count, deduplication, and snapshot-integrity checks.

## Current v2.0.0 work state (2026-10-07)

- The immutable v1.2.0 snapshot comes from commit `1daf3e1e9adb14223fad95dd31612c3a884b997c`. Its original `records.jsonl` SHA-256 is `c1885bfb779928002171d6deb9bc02c2dccd6081364202d7fe69c9fa787a21ae`; original `split_assignments.jsonl` SHA-256 is `e6ea3fa7f1eb4bf656766ac90318ffd3a98a5fead2fbfa650e7f98d76a2a8b4d`.
- The unified corpus contains 893 rows: all 833 historical records and 60 new AI-assisted candidates. All 893 are in both candidate and recommended Viewer configs. Historical IDs, questions, answers, facts, evidence, and splits are checked against the frozen snapshot.
- Split counts are TRAIN/DEV/TEST = 621/137/135. Historical splits are post-annotation; the 60 new questions use source-family splits assigned before drafting.
- The source registry contains 29 documents, 31 report families, and 8 consolidated publishing institutions. The 506 CAICT records are 56.7% of the corpus, so the prior below-45% target is unmet.
- The owner confirmed authorization to republish the 506 legacy CAICT QA records. Their record license remains CC BY 4.0; the source-report license is not asserted. Their source attribution is retained.
- All 833 historical rows still have pending v2 answer-blind content review; some source files also await revalidation. Their inclusion in `recommended` is a maintainer decision, not a claim of review or gold status. New records remain AI-assisted and not human reviewed.
- The v1.2.0 snapshot hashes remain unchanged. The local validator currently passes; all 893 rows are present in the six Viewer files, with no exact or thresholded near-duplicate pairs and no source media included.
- The unified package was pushed to GitHub `main` in commit `ff3b3b5` and uploaded to the Hugging Face dataset repository. Downloaded Hub files match all 63 local package files by SHA-256; the remote has one extra pre-existing `.gitattributes` file. The current Hub data revision was `3a8309f91d96e52a1b7ec64f19b4b118629e735e` when checked.
- Hugging Face Viewer `/is-valid`, `/splits`, `/parquet`, and `/size` return HTTP 500 for this dataset. The same service returns HTTP 200 for the `stanfordnlp/imdb` control dataset, so the current dataset's split counts remain unverified. The v2.0.0 tag remains pending.
- Any later documentation or release-report update must be pushed to GitHub and synchronized to Hugging Face; the current 893-row data files are already present on both.

## Quality and licensing decisions

- Preserve the historical record-level license and source attribution. For the legacy CAICT QA records, the dataset-owner authorization confirmation is separate from the source report's unasserted license.
- CC BY-SA and CC BY-NC-SA obligations remain attached to affected records; no repository-wide single license is claimed.
- New records contain paraphrased facts and physical-page locators only; no report PDFs, media, or long text blocks are redistributed.
- Keep historical review status visible while including every historical row in the recommended set, as directed by the dataset owner.
- Do not describe historical splits as blind holdout; previous system exposure is unaudited.

## Validation and release procedure

1. Run `python3 build_v2_package.py` and `python3 build_hf_splits.py`.
2. Run `python3 validate_v2_package.py`, then `python3 build_release_metadata.py`; inspect record/source/license counts, IDs, source references, evidence bounds, split isolation, archive hashes, Viewer rows, and package checksums.
3. Review the diff and confirm no source PDFs or media entered the package.
4. Push the unified package directly to GitHub `main` and upload the same files to the Hugging Face dataset repository.
5. Compare remote file hashes; query Viewer splits and counts when the service is available. Add the v2.0.0 tag only after successful Viewer verification.

## Prioritized TODOs

1. Retry Hugging Face Viewer verification after its server-side error clears; tag v2.0.0 only after the 893-row split counts are confirmed.
2. Complete source-first, answer-blind review of the 833 historical rows; retain them in the recommended set while exposing their pending status.
3. Continue expanding source coverage toward 2,000 records, 60 reports, and 10 institutions while reducing the current 56.7% CAICT share through authorized non-CAICT sources.
