# Data Statement — v2.0.0

## Motivation and scope

This dataset supports research on Chinese question answering over public Internet, ICT, education technology, labor, and digital-agriculture reports. The unified corpus combines all 833 v1.2.0 records with 60 new records. It contains questions, answer candidates, required-fact summaries, evidence-page locators, split metadata, and per-record rights information.

## Language and sources

Records use Simplified or Traditional Chinese according to the cited source. New sources are official Chinese editions or summaries, or an institution-prepared Traditional Chinese translation; the dataset does not translate English reports itself. See `sources.json` for titles, language, translation provenance, source links, hashes, and rights notices.

## Annotation and review

The 60 new items are AI-assisted candidates. Their question-only packet omits candidate answers; a separate audit records source-first reconstructed answers, page locators, prompt hash, model label, PDF hash, and conclusion. Drafting and checking occurred in the same active AI session; independent review and human review are not claimed. New rows use `human_reviewed=false` and `gold_candidate=false`.

The 833 historical rows retain their original IDs, questions, answers, required facts, evidence, source references, and split assignments. Their v2 answer-blind review is pending, and some source files also need revalidation. All 833 remain in both current Viewer configurations and in the recommended subset by dataset-owner instruction. The pending `review_status` values remain visible; recommendation is not a review or gold-status claim.

## Rights and redistribution

Licensing is mixed by record. The 506 legacy CAICT QA records retain their prior CC BY 4.0 record license and source attribution. The dataset owner confirmed authorization to republish these QA records; the underlying CAICT report license is not asserted. Other records retain their source-specific license, attribution, adaptation, translation, and third-party-content obligations. The package includes no report PDFs, images, tables, figures, or long source excerpts.

## Splits and prior exposure

The 60 new records were assigned by source family before question drafting and grouped to keep linked items within a split. The 833 historical splits were assigned after annotation and retain their original values and provenance. No blind-holdout claim is made; prior system exposure has not been audited.

## Intended and out-of-scope use

The dataset is intended for exploratory source-grounded QA and retrieval research. It does not provide model baselines or performance claims and is not a human-verified gold benchmark. Users should carry forward record-level license and attribution details and account for each record's review status in evaluation.
