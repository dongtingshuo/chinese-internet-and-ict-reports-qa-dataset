# Data Statement

## Source and population

Version 1.1.0 contains 773 Chinese QA records based on 22 public reports on Internet and information-communications topics. It retains the original 506 CAICT-based rows and adds 267 questions from eight World Bank, International Labour Organization, and Asian Development Bank reports. This is a purposive collection, not a representative sample of reports or of the wider domain.

## Collection and annotation

The new questions, answers, required-fact summaries, and evidence locators were drafted and checked with AI assistance against the cited official Chinese PDF pages. They are paraphrases, not source excerpts. New rows are marked `human_reviewed: false`; independent human review and double annotation are not claimed. The source catalog records each report's publisher, bilingual title, language and translation status, official source file and page count, SHA-256, rights notice, license, attribution, and third-party limitations.

## Content and privacy

The package excludes original PDFs, images, screenshots, extracted page text, long quotations, logos, and third-party visuals. It contains QA text, concise fact summaries, source IDs, page-level locators, and license metadata. No formal privacy audit is claimed. Sources are public institutional publications; personal user data was not collected for this release.

## Split and evaluation

The v1.0.0 assignments are unchanged. New report families are each confined to a single split. The full split is TRAIN 537 / DEV 119 / TEST 117. Assignment happened after questions existed, so it is not a prospective blind test. Prior system exposure was not audited. The single unanswerable record is retained from v1.0.0 and remains in TEST.

## License and attribution

Licensing is record-level. Legacy v1.0.0 records retain CC BY 4.0. New rows use CC BY 3.0 IGO for adaptations of the specific licensed reports cited in their metadata. Preserve source attribution, link the applicable license, indicate that the QAs are adaptations, include the required institution-specific disclaimer, and do not imply endorsement. ADB sources additionally state that English is the only official text. Original reports and third-party media are not included and remain outside the dataset package license. Details are in `LICENSES.md`, `ATTRIBUTION.md`, `sources.json`, and each record's `publication_rights`.
