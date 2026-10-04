# Data Card

## Identity

- Dataset: Chinese Internet and ICT Reports QA Dataset
- Version: 1.1.0 (2026-10-05)
- Records: 773; 267 added in this release
- Sources: 22 reports, including 8 new licensed sources from World Bank, ILO, and ADB
- Language: Chinese
- Splits: TRAIN 537 / DEV 119 / TEST 117
- License: mixed record-level terms; see `LICENSES.md`
- Independent human review: not claimed

## Intended use

Research and prototyping for source-grounded document retrieval and question answering, evidence localization, multi-fact answering, numerical retrieval, and report-based QA. No model-performance result is included.

## Construction and annotation

The 506 v1.0.0 records and split assignments are preserved without edits. The 267 new rows use eight public institutional reports for which the source records show a CC BY 3.0 IGO adaptation permission, the relevant rights notice, attribution, source hash, and third-party-content limits. The added records are concise paraphrases of narrative facts with one-based physical PDF page locators. They contain no copied source passages, PDFs, page images, screenshots, charts, or other media.

New annotations were drafted and page-checked with AI assistance. Every added row is marked `human_reviewed: false`; independent human double annotation or adjudication is not claimed. No new no-answer, cross-document, table, or chart items were forced into the release. All additions are answerable and text-only.

## Split

The original assignments remain TRAIN 354 / DEV 75 / TEST 77. Additions are TRAIN 183 / DEV 44 / TEST 40. A report family and its evidence group are kept in one split. The split was assigned after questions were created; it is not a prospective blind holdout, and prior system exposure was not audited. TEST has one no-answer item, retained from v1.0.0.

## Licensing and attribution

The package is not governed by one license across all rows. Legacy v1.0.0 records remain CC BY 4.0. Each `IICR-V11-` row is an adaptation of the report named in its `source_refs` and is published under CC BY 3.0 IGO with the report's attribution and adaptation notice. The ADB Chinese sources additionally identify the English original as the only official version. Use each row's `publication_rights`, `sources.json`, and `ATTRIBUTION.md`. `LICENSE` and `LICENSES.md` explain the scope; Hugging Face metadata says `license: other` to avoid implying uniform licensing.

The source PDF and hash identify the exact source artifact used; they do not grant rights to redistribute that PDF. No third-party material is reproduced. The package does not include original source PDFs, figures, photos, or extracts.

## Limitations

- Purposive historical collection; not representative of all ICT reports.
- Annotation is not independently human-adjudicated.
- Only one unanswerable question exists, in the legacy TEST split.
- New v1.1 questions are text-based; visual records are legacy-only and source media are absent.
- No formal privacy audit or prior-system-exposure audit is claimed.
- No model-performance results are reported.
