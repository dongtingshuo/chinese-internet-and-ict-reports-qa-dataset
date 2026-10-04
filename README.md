---
license: other
license_name: mixed-record-level-licensing
license_link: https://huggingface.co/datasets/TingshuoDong/chinese-internet-and-ict-reports-qa-dataset/blob/main/LICENSES.md
language:
- zh
task_categories:
- question-answering
size_categories:
- 1K<n<10K
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

Version 1.1.0 · 2026-10-05

## Overview

This release contains 773 Chinese QA records from 22 public Internet and information-communications reports. It preserves the original 506 v1.0.0 records, IDs, and split assignments, and adds 267 AI-assisted, source-checked questions from eight licensed reports published by the World Bank, International Labour Organization, and Asian Development Bank.

Each record includes answerability, a concise answer, required facts, source and page locators, report metadata, and record-level reuse terms. New questions use narrative text only. No source PDFs, images, screenshots, extracted page text, or long source passages are bundled.

## Dataset at a glance

- Records: 773 (772 answerable; 1 unanswerable)
- Sources: 22 reports, including 8 additions from 3 institutions
- Split: TRAIN 537 · DEV 119 · TEST 117
- Language: Chinese
- Data format: JSON Lines (`records.jsonl`), one record per line
- New v1.1.0 records: 267, all answerable and text-based
- Historical table/chart/visual-related records: 30, retained from v1.0.0

## Intended use and limitations

Use the data to prototype source-grounded document retrieval and question answering. It is a purposive collection, not a representative sample of the full Internet/ICT domain. The split was assigned after annotation; it is not a prospective blind holdout, and prior system exposure has not been audited. The sole unanswerable example is a retained v1.0.0 item, so the package cannot support reliable no-answer performance estimates. No model-performance results are included.

The added records paraphrase material from official Chinese summaries, editions, or translations. `sources.json` records the institution, English and Chinese titles, language and translation status, official links, SHA-256 of the exact source PDF used, license, rights-notice location, required attribution, and third-party-content limits for every added report.

## Quick start

```python
import json
from pathlib import Path

records = [
    json.loads(line)
    for line in Path("records.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
train = [record for record in records if record["split"] == "TRAIN"]
print(f"records={len(records)}, train={len(train)}")
```

Run the package checks with Python 3:

```bash
python3 validate_package.py
```

## Record format

See [`schema.json`](schema.json) for the v1.0 and v1.1 record schemas. New records use `schema_version: iicr_report_qa_v1_1`, stable IDs `IICR-V11-####`, an answerability label, required-fact statements, and a page-level evidence locator. Physical PDF pages are one-based. `printed_page` is `null` when it was not separately verified.

The Hugging Face Viewer rows in `data/` include a `record_json` field containing the complete canonical record. Rebuild those files with `python3 build_hf_splits.py`.

## Review and split provenance

The 506 legacy records and their existing assignment rows are preserved byte-for-byte at the start of the v1.1 files. The 267 additions are marked `human_reviewed: false`; their page-level source checks were AI-assisted. Independent human review or double annotation is not claimed. The additions are grouped by report family, with each added report assigned to a single split.

| Split | v1.0.0 retained | v1.1.0 additions | Total |
|---|---:|---:|---:|
| TRAIN | 354 | 183 | 537 |
| DEV | 75 | 44 | 119 |
| TEST | 77 | 40 | 117 |

All records from the same known report family and connected evidence group stay in one split. The split was assigned after question annotation and is not a blind test. See [`SPLIT_POLICY.md`](SPLIT_POLICY.md) and [`split_assignments.jsonl`](split_assignments.jsonl).

## Files

- [`records.jsonl`](records.jsonl): canonical QA records.
- [`split_assignments.jsonl`](split_assignments.jsonl): ID-level split and grouping audit.
- [`sources.json`](sources.json): legacy sources and detailed metadata for all eight additions.
- [`data/`](data/): Hugging Face Viewer JSONL splits, generated from `records.jsonl`.
- [`schema.json`](schema.json): JSON Schema for both versions.
- [`DATA_CARD.md`](DATA_CARD.md) and [`DATA_STATEMENT.md`](DATA_STATEMENT.md): scope, construction, review, and limitations.
- [`ATTRIBUTION.md`](ATTRIBUTION.md): source references and required notices.
- [`LICENSES.md`](LICENSES.md): record-level license scope and obligations.
- [`LICENSE`](LICENSE): mixed-license scope notice; legacy CC BY 4.0 text is retained in [`LICENSE-CC-BY-4.0.txt`](LICENSE-CC-BY-4.0.txt).
- [`manifest.json`](manifest.json) and [`SHA256SUMS`](SHA256SUMS): package metadata and checksums.
- [`VALIDATION_REPORT.json`](VALIDATION_REPORT.json): latest release-gate summary.
- [`validate_package.py`](validate_package.py): structural, rights-metadata, split, and integrity checks.

## License and attribution

This package has **mixed record-level licensing**, not one blanket license. The 506 retained v1.0.0 records remain under CC BY 4.0. The 267 new `IICR-V11-` records are adaptations of the specific reports named in each record and are released under CC BY 3.0 IGO, subject to the original institution's attribution and adaptation notice. Each record's `publication_rights` and `source_refs` identify its applicable terms. HF metadata uses `license: other` because neither license applies uniformly to every row.

For new records, cite the dataset and the listed report, link the CC BY 3.0 IGO license, indicate that the QA is an AI-assisted paraphrase/adaptation, and include the institution-specific disclaimer shown in `ATTRIBUTION.md` and the record. The ADB sources also state that their English text is the only official version. Do not reuse third-party figures, tables, photographs, logos, or other material based on the report's license alone. Original reports and media are not included and are outside the package license.

## Citation

Cite this release and the original reports identified by `source_ids`. See [`CITATION.cff`](CITATION.cff), [`CITATION.md`](CITATION.md), and [`ATTRIBUTION.md`](ATTRIBUTION.md).
