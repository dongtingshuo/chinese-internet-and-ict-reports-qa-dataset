# Chinese Internet and ICT Reports QA Dataset / 中国互联网与信息通信报告问答数据集

[简体中文](README.zh-CN.md) · English

Version 1.0.0 · 2026-10-03

## Overview

This package contains 506 Chinese question-answer records based on 14 public reports about Internet and information-communications topics. Researchers can use it to study evidence-grounded document retrieval and question answering, including evidence localization, multi-fact answers, cross-document questions, numerical reasoning, and questions that depend on table, chart, or visual content.

The records are split by document family and connected component. The package also includes answerability and required-fact annotations, source and page locators, source metadata, a JSON Schema, checksums, and a self-contained validator. It contains no source PDFs, page images, screenshots, extracted page text, or long source passages.

## Dataset at a glance

- Records: 506 (505 answerable; 1 unanswerable)
- Language: Chinese
- Sources: 14 reports in 13 connected components
- Split: TRAIN 354 · DEV 75 · TEST 77
- Visual/table/chart-related records: 30
- Data format: JSON Lines (`records.jsonl`), one JSON record per line

## Intended use and limitations

Use this dataset to prototype or evaluate evidence-grounded document retrieval and QA workflows. It is not a representative sample of the full Internet/ICT domain, and it should not be used alone to claim model performance. The split was created after annotation, not as a prospective blind holdout; prior system exposure was not audited. TEST contains the only unanswerable record, too few to estimate no-answer performance reliably. The package does not include visual source files.

## Quick start

Python 3 is required for the example and validator. Reading the JSONL file does not require third-party Python packages.

```python
import json
from pathlib import Path

records_path = Path("records.jsonl")
records = [
    json.loads(line)
    for line in records_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
train_records = [record for record in records if record["split"] == "TRAIN"]
print(f"records={len(records)}, train={len(train_records)}")
```

Run the package validator from this directory:

```bash
python3 validate_package.py
```

## Record format

Each line in `records.jsonl` contains one record. The full machine-readable definition is in [`schema.json`](schema.json).

| Field | Meaning |
|---|---|
| `query_id` | Stable record identifier. |
| `question` | Chinese question. |
| `answerability`, `gold_answer` | Whether the question is answerable and its annotated answer. |
| `required_facts` | Atomic facts needed to support an answer, with numeric fields when applicable. |
| `gold_evidence_sets` | Alternative sufficient evidence sets, with source, page, element, and supported-fact locators. |
| `split` | Frozen `TRAIN`, `DEV`, or `TEST` assignment. |
| `domain_id`, `document_id`, `family_id`, `connected_group_id` | Domain, document, report-family, and evidence-group metadata. |
| `source_ids`, `source`, `source_refs` | Source identifiers, provenance records, and the source attribution to retain when citing a record. |
| `gold_candidate`, `gold_quality` | Candidate-set and source-review records. `gold_candidate: true` does not mean independent human adjudication. |
| `publication_rights` | Dataset license and record-level attribution metadata. |

## Annotation and review provenance

All 506 rows are marked as Gold candidates. Their recorded source-support statuses are: 401 source-supported candidates, 55 verified after locator repair, 8 after content correction, 40 retaining an earlier source-verified status, and 2 with later source follow-up resolutions. The records show AI-assisted source checking; the package does not claim independent human review. After the recorded locator repairs, source follow-ups, and content corrections, the review ledger has no unresolved semantic-review items. That status is not independent human certification.

## Split and leakage controls

Records from the same document family and connected component stay in one split: TRAIN 354, DEV 75, and TEST 77. The split was assigned after the questions and Gold-candidate annotations existed. See [`SPLIT_POLICY.md`](SPLIT_POLICY.md) for the protocol and [`split_assignments.jsonl`](split_assignments.jsonl) for the ID-level audit.

## Files

- [`records.jsonl`](records.jsonl): QA records and evidence locators.
- [`split_assignments.jsonl`](split_assignments.jsonl): query-ID-only split and grouping audit.
- [`sources.json`](sources.json): source titles, official links, notice summaries, and hashes.
- [`schema.json`](schema.json): JSON Schema for the records.
- [`DATA_CARD.md`](DATA_CARD.md) and [`DATA_STATEMENT.md`](DATA_STATEMENT.md): scope, construction, provenance, and limitations.
- [`ATTRIBUTION.md`](ATTRIBUTION.md): source attribution index.
- [`LICENSE`](LICENSE): CC BY 4.0 license for the packaged dataset records and annotations.
- [`LICENSE_STATUS.md`](LICENSE_STATUS.md): license and redistribution status.
- [`CITATION.md`](CITATION.md) and [`CITATION.cff`](CITATION.cff): citation information.
- [`manifest.json`](manifest.json) and [`SHA256SUMS`](SHA256SUMS): package metadata and integrity checks.
- [`VALIDATION_REPORT.json`](VALIDATION_REPORT.json): the latest package validation report; the packaged validator last passed on 2026-10-04.
- [`validate_package.py`](validate_package.py): structural and integrity validator.

## License and attribution

The question-answer records, annotations, evidence locators, and dataset metadata in this package are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You may share and adapt them, including commercially, with appropriate attribution, a link to the license, and an indication of changes. Cite the dataset and the original reports identified for each record in `source_ids`; see [`ATTRIBUTION.md`](ATTRIBUTION.md) and [`sources.json`](sources.json).

The original reports, PDFs, images, and other source media are not included and are outside this dataset-package license. See [`LICENSE`](LICENSE), [`LICENSE_STATUS.md`](LICENSE_STATUS.md), and each record's `publication_rights` field for the license scope and attribution details.

## Citation

Cite this dataset and the original reports identified in the records. See [`CITATION.cff`](CITATION.cff), [`CITATION.md`](CITATION.md), and [`ATTRIBUTION.md`](ATTRIBUTION.md).

## Help and maintenance

For schema or validation issues, open an issue in the GitHub repository that hosts this package. Include the affected `query_id` or file path, and do not attach source PDFs or other source files. The project team maintains this package.
