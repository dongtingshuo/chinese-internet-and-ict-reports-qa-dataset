---
license: other
configs:
- config_name: candidates
  data_files:
  - split: train
    path: data/candidates_train.jsonl
  - split: validation
    path: data/candidates_validation.jsonl
  - split: test
    path: data/candidates_test.jsonl
- config_name: recommended
  data_files:
  - split: train
    path: data/recommended/train.jsonl
  - split: validation
    path: data/recommended/validation.jsonl
  - split: test
    path: data/recommended/test.jsonl
---

# 中文互联网与 ICT 报告问答数据集

**版本：** 2.0.0 · **语言：** 中文 · **统一数据集：** 2,000 条 · **推荐评测子集：** 2,000 条

本版本将 v1.2.0 的 833 条记录与新增 1,167 条合并在同一数据集中。v1.2.0 原始包仍保存在 `history/v1.2.0/`。

## 数据内容

- 833 条历史记录、60 条 AI 辅助来源重建候选题、1,107 条规则生成的句子填空候选题。
- 共 61 份来源文档、50 个报告家族、10 家归并后的出版机构。CAICT 记录 506 条，占 25.3%。
- TRAIN/DEV/TEST 分别为 1,377/300/323 条。新报告家族在出题前分配切分；历史切分保留原有的标注后分配说明。
- Hugging Face 的 `candidates` 和 `recommended` 两种配置都包含这 2,000 条。按数据集所有者要求，所有记录均保留在推荐子集；筛选时请同时查看每条记录的 `review_status`。
- 1,107 条填空题各含一条经授权中文来源中的短句，并挖去一个数值、术语或短语。数据包不含报告 PDF、图片、图表、表格或长段原文。

## 复核状态与限制

1,107 条填空候选由确定性脚本处理从 32 份 ITU 和 WHO 中文 PDF 提取的文本生成，尚未逐条进行答案盲化或独立内容复核。数据记录包含答案、PDF 物理页码、来源文件哈希、原句哈希、生成方法和脚本哈希；状态为 `pending_ai_content_verification`。这些记录没有逐条调用语言模型。

另外 60 条 v2 候选题经过 AI 辅助的来源页重建，但没有独立人工复核。833 条历史题保留原内容和切分，其 v2 答案盲化重建仍待完成，部分历史来源文件也待复核。按所有者要求纳入 `recommended` 不代表已经核验或达到金标准。本版新增量主要是短句填空，复杂推理题型并不均衡。

新增 ITU 和 WHO 文档的许可页及 PDF 哈希已核对。相应记录适用 CC BY-NC-SA 3.0 IGO，并逐条记录署名、改编声明、相同方式共享和非商业义务。1,107 条待复核填空题的第三方署名筛查尚未完成。506 条 CAICT 历史 QA 记录依据数据集所有者授权继续使用原有 CC BY 4.0 记录许可；这不表示底层报告也采用该许可。

历史切分不是盲测集，既有系统接触情况未审计。数据包不含 RAG 基线或模型性能结果，也不声称全库是金标准。

## 许可

本仓库采用逐条混合许可，整个数据集没有单一适用许可。重新分发记录时，须保留 `publication_rights`、来源署名和适用的改编声明。详情见 `LICENSES.md`、`LICENSE_STATUS.md`、`ATTRIBUTION.md` 和 `sources.json`。Hugging Face 元数据使用 `license: other`。

## Viewer 字段

请结合 `answer_candidate`、`review_status` 和 `recommended_for_evaluation` 使用。`record_json` 保存完整记录、证据定位和许可信息。

## 重建与校验

先从所列来源 PDF 在本地提取带物理页分隔符的 UTF-8 文本，再运行：

```bash
python3 scripts/generate_v2_cloze_candidates.py --extracted-text-dir /path/to/extracted-text
```

随后运行 `python3 build_v2_package.py`、`python3 build_hf_splits.py`、`python3 validate_v2_package.py` 和 `python3 build_release_metadata.py`。仓库不包含来源 PDF 或完整提取文本。
