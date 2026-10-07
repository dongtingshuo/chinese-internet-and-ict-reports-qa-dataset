# Data Card — v2.1.0

## Dataset description

A unified Chinese-language QA candidate corpus about Internet, ICT, education technology, public health information systems, labor, and digital agriculture reports. It contains 2,508 records: the exact 2,000 rows from v2.0.0 plus 508 source-reconstructed, non-cloze questions. All rows remain in the recommended subset per dataset-owner instruction; recommendation does not change review status.

## Contents and composition

- 61 source documents from 50 report families and 10 consolidated publishing institutions.
- TRAIN/DEV/TEST: 1,681/397/430. The 508 v2.1 additions inherit registered source-family assignments and are split 304/97/107.
- 506 legacy CAICT records; 1,107 v2.0 sentence-cloze records; 508 v2.1 source-reconstructed questions.
- All v2.0.0 records, IDs, row content, splits, recommendation values, and review statuses are preserved byte-for-byte in the active record file's prefix and archived under `history/v2.0.0/`.
- No source report PDFs, images, tables, figures, or long passages are included. The 1,107 historical cloze records continue to contain one short licensed sentence each.

## Data creation and review

The 508 v2.1 questions were checked against official Chinese source PDFs using answer-free question packets. The audit records reconstructed answers, atomic required facts, physical PDF page locators, source PDF hashes, the review prompt hash, and the conclusion. The authoring and checking occurred in the same active AI session; neither independent review nor human review is claimed. New rows are marked `human_reviewed: false` and `gold_candidate: false`.

Table evidence locators carry the table identifier plus relevant row/column labels or footnote marker in `locator_details`; this metadata supports evidence lookup without including the source table itself.

The 542-question draft pool produced 508 release records. Twenty items without a completed reconstruction audit were deferred; six invalid-label items and eight near duplicates were excluded. See the complete question and reconstruction archives under `audit/v2_1_all_candidate_*` and `audit/v2_1_candidate_disposition_ledger.jsonl`.

The 1,107 v2.0 cloze rows remain `pending_ai_content_verification`; the answer was visible to the deterministic masking process, and third-party attribution screening is pending. The 833 historical records retain their prior pending review statuses. No corpus-wide human review or gold status is claimed.

## Sources and licensing

The corpus has mixed record-level licensing and no repository-wide license. The 508 v2.1 additions adapt/paraphrase official Chinese source content already registered in `sources.json`; each row carries its source license, attribution, adaptation/translation notices, and third-party limitations. Source PDFs and media are not redistributed. The v2.0 cloze records retain their short source excerpts and per-record CC BY-NC-SA 3.0 IGO terms. The dataset owner's authorization for the 506 legacy CAICT QA records is separate from the underlying report rights.

## Intended use and limitations

Use as a source-grounded Chinese QA candidate corpus. Filter on `review_status`, `task_family`, `task_subtype`, `split`, and `publication_rights`. Historical splits are post-annotation and not blind holdouts; prior system exposure has not been audited. The package contains no RAG baseline or model performance result.
