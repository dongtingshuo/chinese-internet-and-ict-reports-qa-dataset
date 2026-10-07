# Data Statement — v2.1.0

## Motivation and scope

The dataset supports research on Chinese question answering over Internet, ICT, education technology, health information systems, labor, and digital agriculture reports. The unified corpus has 2,508 rows: all 2,000 v2.0.0 records plus 508 new non-cloze, source-reconstructed QA records. It contains questions, candidate answers, required-fact summaries, physical PDF page locators, split metadata, and per-record rights information.

## Language and sources

The v2.1 additions use official Chinese-language reports or official Chinese editions already listed in `sources.json`; the dataset does not translate English reports. The new items add no report documents and include no source PDFs, media, or long passages. Source titles, official links, hashes, language/translation provenance, and licensing obligations are registered by source ID.

## Annotation and review

The 508 v2.1 additions were checked from question-only packets against the cited source PDFs. The audit stores the reconstructed answers, required facts, physical PDF pages, and source hashes. The same active AI session drafted and checked the questions; there was no independent human review. The 20 unaudited drafts, six invalid-label candidates, and eight near duplicates were not released.

Table-based evidence includes a compact locator for the table identifier and applicable row/column labels or footnote marker. It does not include the table or its image.

The 1,107 v2.0 additions remain rule-generated sentence clozes with the answer visible to the masking process; they are still pending content verification and third-party attribution screening. The 833 historical records retain their earlier statuses. All rows remain in `recommended` per dataset-owner instruction, which does not imply that they are verified or gold.

## Rights and redistribution

Licensing is mixed by record. Preserve each row's `publication_rights`, its source attribution, and adaptation/translation notices. The v2.1 records are concise paraphrases and contain no report PDF or media. The 1,107 cloze rows retain short source sentence excerpts under their row-level terms. The 506 legacy CAICT QA records retain their prior record license based on the dataset owner's authorization confirmation; this does not assert a license for the underlying reports.

## Splits and prior exposure

The v2.1 records inherit source-family assignments made before v2.0.0 question drafting; linked reports and evidence groups remain in one split. Their TRAIN/DEV/TEST counts are 304/97/107. The full corpus counts are 1,681/397/430. The exact v2.0.0 rows and assignments remain unchanged. Historical splits were assigned after annotation and are not blind holdouts; prior system exposure has not been audited.

## Intended and out-of-scope use

The corpus is intended for exploratory source-grounded QA and retrieval research. It is not a human-reviewed gold benchmark. No retrieval baseline or model-performance result is included.
