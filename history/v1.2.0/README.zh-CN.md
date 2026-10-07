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

# 中国互联网与信息通信报告问答数据集

简体中文 · [English](README.md)

版本 1.2.0 · 2026-10-06

## 项目简介

本版本包含基于 25 份公开互联网与信息通信报告构建的 833 条中文问答记录。v1.0.0 的 506 条和 v1.1.0 的 267 条记录、ID 与切分均保留；v1.2.0 新增 60 条 AI 辅助核查候选记录：无答案题、跨文档题、表格或图表题各 20 条。新增来源登记了国际劳工组织、UNESCO IITE 与上海开放大学的三份报告；本版本也使用了 v1.1.0 已登记且适用的报告。

每条记录包含必要事实摘要、证据定位、可回答性、来源引用和记录级许可信息。物理 PDF 页码与印刷页码分别记录。所有 v1.2.0 新记录均标记 `human_reviewed: false`。数据包不含原报告 PDF、抽取页文本、截图、图片或长段原文。

## 数据概览

- 记录数：833 条（可回答 812 条；无答案 21 条）
- 来源：25 份报告
- 切分：TRAIN 579 · DEV 128 · TEST 126
- v1.2.0 新增：60 条（无答案、跨文档、表格/图表各 20 条）
- 语言：中文
- 规范数据：`records.jsonl`，每行一条 JSON 记录
- Hugging Face Viewer 文件：`data/train.jsonl`、`data/validation.jsonl`、`data/test.jsonl`
- 许可：记录级混合许可，不存在覆盖整个数据包的单一许可

## 用途与局限

可用于原文档检索、跨文档问答、证据定位、可回答性判断以及表格/图表推理的原型评估。该数据集按目标抽样，不代表全部互联网与 ICT 报告。切分在标注后分配，不是前瞻性盲测；此前系统接触情况没有审计。数据包没有模型性能结果，也不声称经过独立人工复核。

20 条 v1.2.0 无答案题均记录核查范围、近似证据及其不足之处，但仍是候选标注，不应视作经过独立裁定的金标准。跨文档题要求至少两份报告共同支持答案。表格/图表题标出对应视觉材料和物理 PDF 页；原图表不会打包。

## 快速使用

```python
import json
from pathlib import Path

records = [json.loads(line) for line in Path("records.jsonl").read_text(encoding="utf-8").splitlines() if line]
train = [record for record in records if record["split"] == "TRAIN"]
print(f"records={len(records)}, train={len(train)}")
```

运行数据包校验：

```bash
python3 validate_package.py
```

从规范记录重建 Hugging Face Viewer 文件：

```bash
python3 build_hf_splits.py
```

## 记录结构

[`schema.json`](schema.json) 定义了历史记录、v1.1 与 v1.2 的 JSON Schema。v1.2 记录使用 `schema_version: iicr_report_qa_v1_2` 和 `IICR-V12-####` ID。Schema 要求无答案题提供检索范围和近似证据，跨文档题至少有两个来源，表格/图表题提供视觉依赖和页码定位。v1.2 的 `publication_rights` 为使用到的每个来源记录许可与义务。

Hugging Face Viewer 每行保留完整 `record_json`，并提供题型、来源 ID、适用记录许可和模态标签等可检索字段。PDF 物理页码从 1 开始；经单独核实的印刷页码另行记录。

## 核查与切分

v1.0.0 和 v1.1.0 的记录及切分前缀按字节保持不变。60 条 v1.2.0 新增记录按报告家族和证据连通组分配，同一来源、家族或连通组不跨切分。三类新增题型各自分配为 TRAIN 14 条、DEV 3 条、TEST 3 条。

| 切分 | v1.0.0 保留 | v1.1.0 新增 | v1.2.0 新增 | 合计 |
|---|---:|---:|---:|---:|
| TRAIN | 354 | 183 | 42 | 579 |
| DEV | 75 | 44 | 9 | 128 |
| TEST | 77 | 40 | 9 | 126 |

新增记录经过 AI 辅助核查，不声称独立人工复核或双人标注。切分在题目构造后分配，且未审计此前系统接触情况，因此 TEST 不能描述为前瞻性盲测。详情见 [`SPLIT_POLICY.md`](SPLIT_POLICY.md) 和 [`split_assignments.jsonl`](split_assignments.jsonl)。

## 记录级许可与署名

本数据包采用**记录级混合许可**，没有统一覆盖所有记录的许可。保留的 v1.0.0 记录和 v1.2.0 中 7 条 ILO 中文执行摘要改编记录采用 CC BY 4.0；v1.1.0 与 v1.2.0 中 50 条改编记录采用 CC BY 3.0 IGO；3 条 UNESCO 工具包改编记录采用 CC BY-SA 3.0 IGO，并在记录级继续采用相同条款。每条记录的适用许可、来源署名、改编/翻译说明和第三方内容限制均写在记录、`sources.json`、[`LICENSES.md`](LICENSES.md) 与 [`ATTRIBUTION.md`](ATTRIBUTION.md) 中。Hugging Face 元数据使用 `license: other`，避免暗示所有记录采用同一许可。

再次分发记录时，请保留对应来源引用，链接适用许可，说明做过改编，并保留来源特定声明。报告的许可不自动覆盖报告中的第三方内容。原始报告和媒体未纳入数据包，也不受此数据包许可覆盖。

## 引用

请引用数据集版本以及记录 `source_ids` 对应的原始报告。格式见 [`CITATION.cff`](CITATION.cff)、[`CITATION.md`](CITATION.md) 和 [`ATTRIBUTION.md`](ATTRIBUTION.md)。
