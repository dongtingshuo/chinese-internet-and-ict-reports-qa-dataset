---
license: other
license_name: mixed-record-level-licensing
license_link: https://huggingface.co/datasets/TingshuoDong/chinese-internet-and-ict-reports-qa-dataset/blob/main/LICENSES.md
language:
- zh
task_categories:
- question-answering
size_categories:
- n<1K
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train.jsonl
  - split: validation
    path: data/validation.jsonl
  - split: test
    path: data/test.jsonl
---

# Chinese Internet and ICT Reports QA Dataset / 中国互联网与信息通信报告问答数据集

[简体中文](README.zh-CN.md) · English

Version 1.2.0 · 2026-10-06

## Overview

This release contains 833 Chinese question-answer records grounded in 25 public Internet and information-communications reports. It preserves the 506 v1.0.0 and 267 v1.1.0 records, IDs, and split assignments, and adds 60 AI-assisted candidate records: 20 answerability checks, 20 cross-document questions, and 20 table or figure questions. The three new source reports are from ILO, UNESCO IITE and Shanghai Open University; v1.2.0 also reuses eligible reports already catalogued in v1.1.0.

Every record contains concise required facts, evidence locators, answerability, source references, and applicable record-level licensing information. Evidence locators distinguish physical PDF pages from printed page numbers. New v1.2.0 records are marked `human_reviewed: false`. The package contains no source PDFs, extracted page text, screenshots, images, or copied long passages.

## Dataset at a glance

- Records: 833 (812 answerable; 21 unanswerable)
- Sources: 25 reports
- Split: TRAIN 579 · DEV 128 · TEST 126
- v1.2.0 additions: 60 (20 unanswerable, 20 cross-document, 20 table/figure)
- Language: Chinese
- Canonical data: `records.jsonl`, one record per line
- Hugging Face Viewer data: `data/train.jsonl`, `data/validation.jsonl`, `data/test.jsonl`
- Licensing: mixed record-level terms; no single license applies to the complete package

## Intended use and limitations

Use the dataset to prototype source-grounded document retrieval, multi-document question answering, evidence localization, answerability detection, and table/figure reasoning. It is a purposive collection, not a representative sample of Internet and ICT reports. The split was assigned after annotation; it is not a prospective blind holdout, and prior system exposure has not been audited. The package reports no model-performance results and makes no claim of independent human review.

The 20 v1.2.0 no-answer records are candidates grounded in the stated report/page search scope, with nearby evidence and an explanation of why it does not answer the question. They should not be treated as independently adjudicated gold labels. Cross-document records require evidence from at least two reports. Visual reasoning records identify a table or figure and a physical PDF page; the source visual is not bundled.

## Quick start

```python
import json
from pathlib import Path

records = [json.loads(line) for line in Path("records.jsonl").read_text(encoding="utf-8").splitlines() if line]
train = [record for record in records if record["split"] == "TRAIN"]
print(f"records={len(records)}, train={len(train)}")
```

Run the package checks with Python 3:

```bash
python3 validate_package.py
```

Rebuild Hugging Face Viewer files from the canonical records:

```bash
python3 build_hf_splits.py
```

## Record format

See [`schema.json`](schema.json) for the legacy, v1.1, and v1.2 JSON Schemas. New records use `schema_version: iicr_report_qa_v1_2` and stable IDs `IICR-V12-####`. The v1.2 schema requires absence-verification details for no-answer candidates, at least two sources for cross-document questions, and a visual dependency locator for table/figure questions. `publication_rights` records the license and obligations for every source used by a v1.2 record.

The Hugging Face Viewer rows include a `record_json` field with the complete canonical row, plus searchable task type, source IDs, record license, and modality tags. Physical PDF pages are one-based; a separately verified printed page is recorded independently.

## Review and split provenance

The v1.0.0 and v1.1.0 rows and split assignment prefixes are preserved byte-for-byte. The 60 v1.2.0 additions are grouped by report family and evidence-connected group; each source and group is kept within one split. Each of the three v1.2.0 question types contributes 14 TRAIN, 3 DEV, and 3 TEST records.

| Split | v1.0.0 retained | v1.1.0 additions | v1.2.0 additions | Total |
|---|---:|---:|---:|---:|
| TRAIN | 354 | 183 | 42 | 579 |
| DEV | 75 | 44 | 9 | 128 |
| TEST | 77 | 40 | 9 | 126 |

All new annotations were checked with AI assistance. Independent human review or double annotation is not claimed. The split was assigned after annotation, and prior system exposure was not audited; do not describe TEST as a prospective blind holdout. See [`SPLIT_POLICY.md`](SPLIT_POLICY.md) and [`split_assignments.jsonl`](split_assignments.jsonl).

## Record-level licensing and attribution

The package has **mixed record-level licensing** and no blanket license. The retained v1.0.0 records and seven v1.2.0 ILO executive-summary records use CC BY 4.0; v1.1.0 adaptations and 50 v1.2.0 adaptations use CC BY 3.0 IGO; three v1.2.0 UNESCO toolkit adaptations use CC BY-SA 3.0 IGO. The ShareAlike records carry that same license at the record level. The exact terms, source attribution, adaptation/translation notices, and third-party limits are recorded in each row, `sources.json`, [`LICENSES.md`](LICENSES.md), and [`ATTRIBUTION.md`](ATTRIBUTION.md). Hugging Face metadata uses `license: other` because one license does not cover every row.

When redistributing a record, retain its source citation, link its applicable license, state that changes/adaptations were made, and preserve all source-specific notices. A report's license does not automatically cover third-party content within it. Original reports and media are not included and remain outside this package's license.

## Citation

Cite the dataset version and each source report identified by a record's `source_ids`. See [`CITATION.cff`](CITATION.cff), [`CITATION.md`](CITATION.md), and [`ATTRIBUTION.md`](ATTRIBUTION.md).
