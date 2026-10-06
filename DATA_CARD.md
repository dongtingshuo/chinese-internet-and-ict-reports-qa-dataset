# Data Card

## Identity

- Dataset: Chinese Internet and ICT Reports QA Dataset
- Version: 1.2.0 (2026-10-06)
- Records: 833; 60 added in this release
- Sources: 25 public institutional reports
- Language: Chinese
- Splits: TRAIN 579 / DEV 128 / TEST 126
- Question types added: 20 unanswerable, 20 cross-document, 20 table/figure
- License: mixed record-level terms; see `LICENSES.md`
- Independent human review: not claimed

## Intended use

Research and prototyping for source-grounded document retrieval and question answering, no-answer detection, cross-document synthesis, table/figure reasoning, evidence localization, and split-safe evaluation. No model-performance results are included.

## Construction and annotation

The 506 v1.0.0 and 267 v1.1.0 records, IDs, and split assignments are preserved. The 60 v1.2.0 additions reuse eligible licensed reports and add three source records: an ILO Chinese executive summary (CC BY 4.0), a Chinese UNESCO IITE/Shanghai Open University toolkit (CC BY-SA 3.0 IGO), and an ILO Chinese translation (CC BY 3.0 IGO). Each source has an official link, exact source PDF SHA-256, page count, license notice location, attribution, adaptation/translation notice, and third-party content limits in `sources.json`.

The additions comprise 20 no-answer candidates with search scope and near-miss evidence, 20 cross-document questions supported by at least two sources, and 20 table/figure questions with physical PDF page locators and an explicit visual dependency. All were drafted and checked with AI assistance. Every new row is marked `human_reviewed: false`; independent human double annotation or adjudication is not claimed. The package contains no source PDFs, source page images, screenshots, extracted page text, copied long passages, or source media.

## Split

The v1.0.0 and v1.1.0 rows and assignments remain byte-identical. Additions are TRAIN 42 / DEV 9 / TEST 9, with each new task type allocated TRAIN 14 / DEV 3 / TEST 3. Sources, report families, and connected evidence groups are kept within one split. Assignment happened after questions were created; it is not a prospective blind holdout, and prior system exposure was not audited.

## Licensing and attribution

The package is not governed by one license across all rows. Totals by record-level license are 513 CC BY 4.0, 317 CC BY 3.0 IGO, and 3 CC BY-SA 3.0 IGO. The three ShareAlike adaptations are individually released under CC BY-SA 3.0 IGO. Each row's `publication_rights`, `source_refs`, and `sources.json` entry identify the applicable source terms. Retain the source citation, license link, adaptation notice, translation notice where applicable, and any institution-specific disclaimer. Hugging Face metadata uses `license: other` to reflect the mixed scope.

Original reports and third-party media remain outside the package license. The UNESCO source contains third-party imagery; only toolkit-authored scoring tables were used as evidence and no table contents or images are reproduced.

## Limitations

- Purposive collection; not representative of all Internet and ICT reports.
- New candidates have not received independent human adjudication.
- No-answer labels reflect the recorded report and page scope, not all possible external information.
- Post-annotation split; no prospective blind holdout or prior-system-exposure audit is claimed.
- No formal privacy audit or model-performance evaluation is included.
