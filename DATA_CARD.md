# Data Card

## Identity

- Dataset: Chinese Internet and ICT Reports QA Dataset
- Version: 1.0.0
- Domain: Internet and information-communications reports
- Records: 506
- Sources: 14 public reports
- Split: TRAIN 354 / DEV 75 / TEST 77
- Dataset license: CC BY 4.0
- Independent human review: not claimed

## Intended use

Use the dataset to study source-grounded document retrieval and question answering. It covers evidence localization, multi-fact answers, cross-document questions, numerical reasoning, and questions that depend on visual, table, or chart content. This legacy set is separate from the frozen CFQA data used in the current M3/M4 formal research track.

## Construction and annotations

The source reports came from their publishers' public pages. Based on those documents, the project annotated questions, answers, answerability labels, required facts, evidence locators, task and modality labels, and source and family metadata. The package contains no source PDFs, images, screenshots, full-page text, or long verbatim passages.

All records are marked as Gold candidates. Each row's source-support status describes the type and extent of source checking or correction. It does not mean that every row received human adjudication. The package records AI-assisted source and evidence checking; it does not claim independent human review.

## Split

Records from the same document family or connected evidence component stay in one split: TRAIN 354, DEV 75, and TEST 77. The split was assigned after the questions and Gold-candidate annotations existed, so it is not a prospective or preregistered holdout. Prior system exposure was not audited. TEST contains the only unanswerable item, too few to estimate no-answer performance reliably.

## Known limitations

- The data are a purposive historical collection, not a representative sample of the full Internet/ICT domain.
- There is one unanswerable item.
- There are 30 table/chart/visual-related items; the visual media are not included.
- Some locators depend on parser element IDs. Page numbers and source hashes are provided for traceability.
- The package contains no model-performance results.
- The original reports and visual media are not included; the dataset license applies to the packaged records and annotations, not to those external source files.
