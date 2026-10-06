# Data Statement

## Source and population

Version 1.2.0 contains 833 Chinese QA records grounded in 25 public reports on Internet and information-communications topics. It preserves the 506 v1.0.0 and 267 v1.1.0 records and adds 60 candidates: 20 unanswerable, 20 cross-document, and 20 table/figure questions. Three newly catalogued sources are an ILO Chinese-language executive summary, a UNESCO IITE/Shanghai Open University Chinese toolkit, and an ILO Chinese translation. The collection is purposive and does not represent all reports or the wider domain.

## Collection and annotation

The new questions, answers, fact summaries, absence checks, and evidence locators were prepared and checked with AI assistance against the cited official Chinese PDFs. The package records physical PDF pages separately from printed page numbers. Cross-document items link required facts to at least two report sources; table/figure items identify the visual and page used. All additions are marked `human_reviewed: false`; independent human review and double annotation are not claimed.

## Content and privacy

The package contains QA text, concise fact summaries, source IDs, evidence locators, absence-verification metadata, and licensing metadata. It excludes original PDFs, images, screenshots, extracted page text, long quotations, logos, charts, table contents, and other source media. No formal privacy audit is claimed. Sources are public institutional publications; personal user data was not collected for this release.

## Split and evaluation

All prior v1.0.0 and v1.1.0 records and assignments are unchanged. The overall split is TRAIN 579 / DEV 128 / TEST 126; v1.2.0 contributes 42 / 9 / 9. New sources, report families, and connected evidence groups are each confined to one split. Assignment occurred after questions existed, so TEST is not a prospective blind holdout. Prior system exposure was not audited. The 21 unanswerable records comprise one retained legacy item and 20 v1.2.0 candidates.

## License and attribution

Licensing is record-level, with 513 CC BY 4.0, 317 CC BY 3.0 IGO, and 3 CC BY-SA 3.0 IGO records. Each record identifies the applicable license and source obligations. Preserve source attribution, link the applicable license, indicate adaptations, and include required source-specific adaptation and translation notices. The three CC BY-SA adaptations remain under CC BY-SA 3.0 IGO. Original reports and third-party materials are not included and remain outside this package license. See `LICENSES.md`, `ATTRIBUTION.md`, `sources.json`, and each record's `publication_rights`.
