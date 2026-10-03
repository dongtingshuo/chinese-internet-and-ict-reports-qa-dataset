# Data Statement

## Source and population

The dataset contains 506 Chinese-language question and answer records based on 14 public reports about Internet and information-communications topics. The reports cover industry statistics, digital infrastructure, AI, cloud, and related policy or research themes. This is a purposive historical collection, not a representative sample of all reports or of the wider domain.

## Collection and annotation

The project created questions, answers, required facts, answerability labels, source locators, and task and modality labels as research annotations. Source and evidence checking used AI assistance for locator repair, source follow-up, and source-grounded content corrections. Each row retains its source-support status. Independent human double annotation or adjudication is not claimed.

## Content and privacy

The package excludes original source PDFs, images, screenshots, extracted page text, and long source passages. Records contain questions, answers, concise required-fact summaries, source, page, and element locators, source identifiers, and hashes. The sources are listed in sources.json and ATTRIBUTION.md. No formal privacy audit is claimed. The corpus was built from public institutional reports, not personal user data.

## Split and evaluation

The family and connected-component split was assigned after candidate questions and answer annotations existed. It is frozen for reproducibility, but it is not a prospective blind test. Prior system exposure was not audited. The single unanswerable record is in TEST.

## License and attribution

The packaged question-answer records, annotations, evidence locators, and dataset metadata are licensed under CC BY 4.0. Each record retains source identifiers and attribution details; cite this dataset and the source reports identified in `sources.json` and `ATTRIBUTION.md`. The original reports, PDFs, images, and other source media are not included and are outside this dataset-package license.
