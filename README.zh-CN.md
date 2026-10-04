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

# 中国互联网与信息通信报告问答数据集 / Chinese Internet and ICT Reports QA Dataset

简体中文 · [English](README.md)

版本 1.1.0 · 2026-10-05

## 数据集简介

本版本包含基于 22 份公开互联网与信息通信报告整理的 773 条中文问答记录。原 v1.0.0 的 506 条记录、ID 和切分保持不变；新增 267 条经 AI 辅助逐页核查的题目，来自世界银行、国际劳工组织和亚洲开发银行发布的 8 份许可明确的报告。

每条记录包含可回答性、答案、必要事实、来源和页码定位、报告元数据及记录级许可信息。新增题目只依据报告正文，不包含源 PDF、图片、截图、整页解析文本或长段原文。

## 数据概况

- 记录数：773 条（可回答 772 条；无答案 1 条）
- 来源：22 份报告，其中新增 8 份，来自 3 家出版机构
- 切分：TRAIN 537 · DEV 119 · TEST 117
- 语言：中文
- 数据格式：JSON Lines（`records.jsonl`），每行一条记录
- v1.1.0 新增：267 条，均可回答且基于文本
- 表格、图表或视觉相关题目：30 条，均为原 v1.0.0 保留记录

## 用途与局限

数据可用于原型验证有来源依据的文档检索与问答流程。它是目的性收集的数据，不代表整个互联网与信息通信领域。切分是在问题标注后确定的，不是前瞻式盲测；此前的系统接触情况尚未审计。唯一的无答案题来自保留的 v1.0.0 数据，无法据此可靠估计拒答表现。数据包不含模型性能结果。

新增题目依据官方中文概要、版本或译本进行改写。`sources.json` 为每份新增报告记录发布机构、中英文标题、文本语言和译本身份、官方链接、所用源 PDF 的 SHA-256、许可、权利声明页、署名要求和第三方内容限制。

## 快速开始

```python
import json
from pathlib import Path

records = [
    json.loads(line)
    for line in Path("records.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
train = [record for record in records if record["split"] == "TRAIN"]
print(f"记录数={len(records)}，训练集={len(train)}")
```

使用 Python 3 运行数据包校验：

```bash
python3 validate_package.py
```

## 记录格式

[`schema.json`](schema.json) 包含 v1.0 和 v1.1 两种记录结构。新增记录使用 `schema_version: iicr_report_qa_v1_1`、`IICR-V11-####` ID、可回答性标签、必要事实摘要和逐页证据定位。PDF 页码从 1 开始；未单独核实印刷页码时，`printed_page` 为 `null`。

Hugging Face Viewer 的 `data/` 文件含有 `record_json` 字段，可还原完整记录。可运行 `python3 build_hf_splits.py` 从规范数据重建 Viewer 文件。

## 核查与切分

原有 506 条记录及其切分文件前缀按字节保持不变。新增 267 条均标记为 `human_reviewed: false`；逐页来源核查由 AI 辅助完成，不声称独立人工复核或双人标注。新增数据按报告家族分组，每份新增报告只进入一个切分。

| 切分 | 保留的 v1.0.0 | v1.1.0 新增 | 合计 |
|---|---:|---:|---:|
| TRAIN | 354 | 183 | 537 |
| DEV | 75 | 44 | 119 |
| TEST | 77 | 40 | 117 |

同一已知报告家族和证据连通组中的记录不会跨切分。题目标注完成后才进行切分，因此这不是盲测。详见 [`SPLIT_POLICY.md`](SPLIT_POLICY.md) 和 [`split_assignments.jsonl`](split_assignments.jsonl)。

## 文件说明

- [`records.jsonl`](records.jsonl)：规范问答记录。
- [`split_assignments.jsonl`](split_assignments.jsonl)：逐条 ID 切分和分组审计。
- [`sources.json`](sources.json)：原有来源及 8 份新增报告的完整元数据。
- [`data/`](data/)：由 `records.jsonl` 生成的 Hugging Face Viewer 切分文件。
- [`schema.json`](schema.json)：两种版本的 JSON Schema。
- [`DATA_CARD.md`](DATA_CARD.md)、[`DATA_STATEMENT.md`](DATA_STATEMENT.md)：范围、构建、核查和局限。
- [`ATTRIBUTION.md`](ATTRIBUTION.md)：来源引用和必须保留的声明。
- [`LICENSES.md`](LICENSES.md)：记录级许可范围和义务。
- [`LICENSE`](LICENSE)：混合许可范围说明；原 CC BY 4.0 文本保存在 [`LICENSE-CC-BY-4.0.txt`](LICENSE-CC-BY-4.0.txt)。
- [`manifest.json`](manifest.json)、[`SHA256SUMS`](SHA256SUMS)：数据包元数据和校验和。
- [`VALIDATION_REPORT.json`](VALIDATION_REPORT.json)：最近一次发布门槛检查摘要。
- [`validate_package.py`](validate_package.py)：结构、许可元数据、切分和完整性校验。

## 许可与来源署名

本数据包**采用混合的记录级许可**，没有一项许可统一适用于全部记录。保留的 506 条 v1.0.0 记录继续采用 CC BY 4.0；新增 `IICR-V11-` 记录是对各记录所列报告的改编，采用 CC BY 3.0 IGO，并遵守原机构的署名和改编声明要求。每条记录的 `publication_rights` 和 `source_refs` 均标明适用条款。由于不存在适用于全体记录的单一许可，Hugging Face 卡片使用 `license: other`。

再发布新增记录时，请引用数据集及对应报告，提供 CC BY 3.0 IGO 许可链接，说明问答是 AI 辅助改写/改编，并附上 `ATTRIBUTION.md` 和记录中列明的机构免责声明。ADB 来源还明确说明英文文本是唯一官方版本。不能仅凭报告许可复用第三方图表、表格、照片、标识或其他材料。原始报告和媒体不在数据包内，也不受本数据包许可覆盖。

## 引用

请引用本版本及每条记录 `source_ids` 对应的原始报告。格式见 [`CITATION.cff`](CITATION.cff)、[`CITATION.md`](CITATION.md) 和 [`ATTRIBUTION.md`](ATTRIBUTION.md)。
