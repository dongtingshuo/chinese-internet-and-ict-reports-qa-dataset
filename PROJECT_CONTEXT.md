# Project Context

## Project goal

Maintain the public Chinese Internet and ICT Reports QA Dataset as a source-grounded, multilingual, record-level mixed-license QA corpus. Keep versioned releases reproducible and honest about evidence quality, licensing, split provenance, and review status.

## Scope and non-goals

- Current release work: curate v2.0.0 from the immutable v1.2.0 archive, add licensed Chinese reports, normalize task/review metadata, and publish synchronized GitHub and Hugging Face artifacts.
- Do not add retrieval/RAG baselines, model experiments, source PDFs, source images, or long source passages.
- Do not claim human review, independent annotation, a gold standard, or blind holdout where these were not performed.
- Historical records with unestablished source reuse rights remain only in the v1.2.0 archive; they are excluded from the active v2 corpus.

## Technology and external services

- Canonical package: JSONL records and split assignments, JSON source registry/schema/manifest, Markdown release documentation, Python validation/build scripts.
- Source PDFs are inspected outside the repository under `/private/tmp/chinese-ict-v2-sources`; never copy those PDFs into the package.
- GitHub: `dongtingshuo/chinese-internet-and-ict-reports-qa-dataset`, direct updates to `main` are preferred when release is authorized.
- Hugging Face: `TingshuoDong/chinese-internet-and-ict-reports-qa-dataset`; repository metadata must describe mixed record-level licensing.

## Directory map

- `records.jsonl`: active v2 candidate records.
- `split_assignments.jsonl`: historical assignments plus preassigned v2 source-family splits.
- `sources.json`: source metadata, license terms, hashes, attribution, and third-party limits.
- `schema.json`: release record schema.
- `data/`: candidate Viewer splits and recommended evaluation subset.
- `audit/`: migration ledger, question-only review packet, reconstruction provenance, and v2 split manifest.
- `history/v1.2.0/`: exact package snapshot from Git tag `v1.2.0`.
- `build_v2_package.py`: deterministic migration and package-data builder.
- `build_release_metadata.py`: manifest/report/checksum generator.
- `validate_v2_package.py`: v2 structural, rights, split, count, and file checks.

## Current v2.0.0 work state (2026-10-07)

- The exact v1.2.0 package is archived from commit `1daf3e1e9adb14223fad95dd31612c3a884b997c`; original `records.jsonl` SHA-256 is `c1885bfb779928002171d6deb9bc02c2dccd6081364202d7fe69c9fa787a21ae`, and original `split_assignments.jsonl` SHA-256 is `e6ea3fa7f1eb4bf656766ac90318ffd3a98a5fead2fbfa650e7f98d76a2a8b4d`.
- Active package generation currently produces 387 candidate records: 327 prior licensed-source records retained pending v2 review and 60 new AI-assisted candidates. The 506 CAICT legacy rows remain in the historical archive only.
- New records use UNESCO AI education guidance, UNESCO GEM 2023 Chinese summary, an AREE Traditional Chinese translation of UNESCO GenAI guidance, and FAO's Chinese digital-agriculture briefing. New split counts are TRAIN/DEV/TEST = 42/9/9; new report families were assigned before question drafting.
- The new set is AI-reconstructed from cited physical PDF pages, with answer values excluded from the question-only review packet. The same active AI session drafted and checked the set; independent review is not claimed. The 60 records are candidate annotations, not human-verified gold data.
- Historical candidates are not recommended for evaluation until their v2 source/hash and answer-blind checks are complete. Some source files remain pending revalidation.
- Hugging Face package upload completed; the current Hub revision is `279480c9a61707f9be29aec701cfce30763695f6`. Remote Git blob IDs and file sizes match all 63 local files; the only extra remote file is the pre-existing `.gitattributes`. Obsolete root-level v1.2 Viewer files were removed.
- Hugging Face Dataset Viewer `/is-valid`, `/splits`, and `/parquet` endpoints currently return HTTP 500 (“server is busier than usual”); the same `/splits` endpoint works for a control dataset. Viewer counts are not verified, so the `v2.0.0` tag remains pending.
- The v2.0.0 candidate package was pushed directly to GitHub `main` in commit `0180fde`. The version tag is intentionally pending successful Viewer verification.

## Quality and licensing decisions

- Every record carries a source-derived record license and attribution/adaptation notices. No repository-wide single license is claimed.
- CC BY-SA adaptations retain share-alike terms; FAO-derived records retain CC BY-NC-SA 3.0 IGO terms.
- Only paraphrased narrative facts and physical-page locators are included for new sources; no visuals or report text blocks are redistributed.
- The old 506 CAICT items have no verified source-level permission in the v1.2.0 registry and are excluded from the active v2 evaluation corpus pending rights evidence.
- Historical splits were assigned after annotation; only v2 source-family assignments are preassigned. No blind-holdout claim is made.

## Validation and release procedure

1. Run `python3 build_v2_package.py` after reviewing source metadata/questions.
2. Run `python3 validate_v2_package.py` and the release metadata builder; inspect schema, IDs, source references, licensing, evidence pages, group isolation, deduplication, archive hashes, Viewer counts, and package checksums.
3. Review the full diff and release documents; ensure no source PDFs/media entered the repository.
4. Commit and push directly to GitHub `main`; add the `v2.0.0` tag after the release commit.
5. Retry Hugging Face Viewer checks after the current service-side HTTP 500 clears; compare all six split counts with the local manifest and record the verified Hub revision.

## Prioritized TODOs

1. Retry the Hugging Face Viewer checks after the service-side 500 clears; update the release report and tag v2.0.0 only after counts and hashes pass.
2. Continue source-first review of the 327 retained historical candidates before recommending any of them.
3. Expand only with additional official Chinese sources whose adaptation rights and evidence locators are verified; current release remains below its scale targets (387/2,000 records, 15/60 documents, 7/10 institutions).
