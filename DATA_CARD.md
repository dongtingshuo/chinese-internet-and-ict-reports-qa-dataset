# Data Card — v2.0.0

## Dataset description

A Chinese-language, source-grounded question-answer dataset about Internet, ICT, education technology, labor platforms, and digital agriculture reports. The unified corpus contains 893 records: all 833 records from v1.2.0 and 60 new AI-assisted candidates. All 893 are in the recommended evaluation subset at the dataset owner's direction. Recommendation does not replace the record-level `review_status` and is not a claim that all labels have been freshly reviewed.

## Contents and composition

- 833 historical records preserve their original IDs, question/answer content, evidence, source references, and split assignments.
- 60 new records cover four Chinese report documents and four new source families.
- Unified TRAIN/DEV/TEST counts are 621/137/135. Exact source and consolidated publisher counts are in `manifest.json`.
- The recommended subset has the same 893 records and split counts as the full corpus.
- The 506 CAICT legacy records are 56.7% of the merged corpus, so the prior goal of reducing that share below 45% is not met.
- No source PDF, image, table, figure, or long text passage is included.

## Data creation and review

The new questions and answers were created with AI assistance from four Chinese source documents. New source-family splits were assigned before drafting. An answer-free review packet was used to reconstruct answers and evidence from cited source PDF pages. Drafting and checking occurred in the same active AI session; independent review and human review are not claimed. The model label, prompt hash, source PDF hashes, locators, and review status are recorded under `audit/` and in each new record.

All 833 earlier records remain pending v2 answer-blind content reconstruction; some historical source files also await revalidation. Their current inclusion is an explicit maintainer decision. Historical split assignments were made after annotation and are not prospective blind holdouts. Prior system exposure has not been audited. Legacy candidate labels are preserved as historical metadata; the dataset does not make a corpus-wide gold-standard claim.

## Sources and licensing

Records use mixed record-level terms. No repository-wide license is asserted. The 506 legacy CAICT QA records retain their prior CC BY 4.0 record license and source attribution; the dataset owner confirmed authorization to republish them. This does not assert a CC BY 4.0 license for the underlying reports. See `LICENSES.md`, `LICENSE_STATUS.md`, `ATTRIBUTION.md`, and `sources.json` for exact obligations.

New records use the license and attribution shown for each source, including ShareAlike and noncommercial requirements where applicable. The package does not redistribute report text blocks, PDFs, or media. Source metadata records Chinese edition or translation status, license notice, source hashes, and third-party-content limits.

## Intended use and limitations

Use as a candidate corpus for Chinese source-grounded QA, retrieval, and document-understanding research. Keep `review_status` and row-level license metadata with every extracted record. Users should design evaluation protocols that account for pending historical review, post-annotation historical splits, and unaudited prior system exposure.

The corpus remains below the scale targets of 2,000 records, 60 reports, and 10 publishing institutions. It does not include RAG baselines or model-performance results, and it is not a human-verified gold benchmark.
