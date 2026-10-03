# Chinese Internet and ICT Reports QA Dataset / 中国互联网与信息通信报告问答数据集

简体中文 · [English](README.md)

版本 1.0.0 · 2026-10-03

## 数据集简介

本数据包收录了基于 14 份公开互联网与信息通信报告整理的 506 条中文问答记录，可用于研究有来源依据的文档检索与问答，包括证据定位、多事实答案、跨文档问题、数值推理，以及依赖表格、图表或视觉信息的问题。

记录按文档家族和连通组件切分。数据包还附有答案可回答性和必要事实标注、来源及页码定位、来源元数据、JSON Schema、校验和与校验器。包内不含源 PDF、页面图片、截图、解析后的整页文本或长段原文。

## 数据概况

- 记录数：506 条（可回答 505 条；无答案 1 条）
- 语言：中文
- 来源：14 份报告，归入 13 个连通组件
- 切分：TRAIN 354 · DEV 75 · TEST 77
- 表格/图表/视觉相关题目：30 条
- 数据格式：JSON Lines（`records.jsonl`），每行一条 JSON 记录

## 用途与局限

这批数据可用于验证有证据来源的文档检索和问答流程。它并不代表整个互联网与信息通信领域，单独使用也不足以证明模型性能。切分是在标注完成后进行的，不是前瞻式盲测；此前是否接触过系统尚未审计。TEST 中只有 1 条无答案题，无法可靠估计系统处理无答案问题的表现。数据包不含视觉源文件。

## 快速开始

运行示例和校验器需要 Python 3。读取 JSONL 文件不需要第三方 Python 包。

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
print(f"记录数={len(records)}，训练集={len(train_records)}")
```

在本目录运行数据包校验：

```bash
python3 validate_package.py
```

## 记录字段

`records.jsonl` 每行包含一条记录。完整的机器可读定义见 [`schema.json`](schema.json)。

| 字段 | 含义 |
|---|---|
| `query_id` | 稳定的记录标识符。 |
| `question` | 中文问题。 |
| `answerability`、`gold_answer` | 问题是否可回答及对应的标注答案。 |
| `required_facts` | 支撑答案所需的原子事实，适用时包含数值字段。 |
| `gold_evidence_sets` | 一组或多组可替代的充分证据，含来源、页码、元素及其支持事实的定位信息。 |
| `split` | 固定的 `TRAIN`、`DEV` 或 `TEST` 切分。 |
| `domain_id`、`document_id`、`family_id`、`connected_group_id` | 领域、文档、报告家族和证据连通组元数据。 |
| `source_ids`、`source`、`source_refs` | 来源标识、溯源记录，以及引用该记录时应保留的来源信息。 |
| `gold_candidate`、`gold_quality` | 候选集标记和来源核查记录。`gold_candidate: true` 不代表经过独立人工裁定。 |
| `publication_rights` | 数据集许可和记录级来源署名信息。 |

## 标注与核查来源

506 条记录均标记为 Gold 候选。来源支持状态分别为：401 条来源支持候选、55 条在修复定位后核验、8 条在修订内容后核验、40 条保留较早的来源核验状态、2 条记录了后续来源复核结果。核查过程使用 AI 辅助；数据包没有声称完成独立人工复核。完成记录中的定位修复、来源跟进和内容修订后，审查台账没有未解决的语义问题。这不等于独立人工认证。

## 切分与泄漏控制

同一文档家族和连通组件中的记录会放在同一切分中：TRAIN 354、DEV 75、TEST 77。切分是在问题和 Gold 候选标注完成后确定的。切分规则见 [`SPLIT_POLICY.md`](SPLIT_POLICY.md)，逐条 ID 审计见 [`split_assignments.jsonl`](split_assignments.jsonl)。

## 文件说明

- [`records.jsonl`](records.jsonl)：问答记录和证据定位。
- [`split_assignments.jsonl`](split_assignments.jsonl)：仅含 Query ID 的切分和分组审计。
- [`sources.json`](sources.json)：来源标题、官方链接、声明摘要和哈希。
- [`schema.json`](schema.json)：记录的 JSON Schema。
- [`DATA_CARD.md`](DATA_CARD.md)、[`DATA_STATEMENT.md`](DATA_STATEMENT.md)：数据范围、构建、溯源和局限。
- [`ATTRIBUTION.md`](ATTRIBUTION.md)：来源署名索引。
- [`LICENSE`](LICENSE)：数据集记录和标注采用 CC BY 4.0 的许可范围说明。
- [`LICENSE_STATUS.md`](LICENSE_STATUS.md)：许可与再分发状态。
- [`CITATION.md`](CITATION.md)、[`CITATION.cff`](CITATION.cff)：引用信息。
- [`manifest.json`](manifest.json)、[`SHA256SUMS`](SHA256SUMS)：数据包元数据与完整性校验。
- [`VALIDATION_REPORT.json`](VALIDATION_REPORT.json)：记录了许可元数据更新后尚未重新运行校验。
- [`validate_package.py`](validate_package.py)：结构和完整性校验器。

## 许可与来源署名

本数据包中的问答记录、标注、证据定位和数据集元数据采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可。你可以分享、改编和商用，但须适当署名、提供许可链接并说明改动。引用数据集时，也请按每条记录的 `source_ids` 引用对应原始报告；来源信息见 [`ATTRIBUTION.md`](ATTRIBUTION.md) 和 [`sources.json`](sources.json)。

本数据包不含原始报告、PDF、图片或其他来源媒体；数据集许可不适用于这些外部来源文件。许可范围和署名方式见 [`LICENSE`](LICENSE)、[`LICENSE_STATUS.md`](LICENSE_STATUS.md) 及每条记录的 `publication_rights` 字段。

## 引用

请同时引用本数据集和记录中列出的原始报告。引用格式见 [`CITATION.cff`](CITATION.cff)、[`CITATION.md`](CITATION.md) 和 [`ATTRIBUTION.md`](ATTRIBUTION.md)。

## 问题反馈与维护

如发现 Schema 或校验问题，请在托管本数据包的 GitHub 仓库提交 issue，并注明相关 `query_id` 或文件路径。请勿附上来源 PDF 或其他来源文件。本数据包由项目团队负责维护。
