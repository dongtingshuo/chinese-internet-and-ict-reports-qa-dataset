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

**版本：** 2.0.0 · **语言：** 中文 · **合并数据集：** 893 条 · **推荐评测子集：** 893 条

本版本将 v1.2.0 的 833 条记录全部保留在当前数据集中，并新增 60 条 AI 辅助候选题。旧题 ID 和切分保持不变；v1.2.0 原始文件也完整保存在 `history/v1.2.0/`。

## 数据内容

- 833 条历史记录和 60 条新增候选题。
- Hugging Face Viewer 的 `candidates` 与 `recommended` 配置均包含相同的 893 条记录。按数据集所有者的要求，旧题也进入推荐子集；每条记录仍保留真实的 `review_status`，使用者应结合复核状态判断适用性。
- TRAIN/DEV/TEST 共 621/137/135 条。历史切分在标注后分配；新增 60 条按来源家族在出题前分配。
- 来源、机构、切分、许可、复核状态和哈希的精确统计见 `manifest.json` 与 `VALIDATION_REPORT.json`。
- 数据包不包含报告 PDF、图片、表格、图表或长段原文。

## 复核状态与限制

833 条旧记录尚未完成 v2 答案盲化内容重建，部分旧报告文件也待重新核验。它们进入 `recommended` 不代表已完成复核、人工核验或达到金标准。新增 60 条通过 AI 辅助对照来源页重建答案和证据，但没有独立人工复核。旧切分不是盲测集，历史系统接触情况未审计。

合并后包含 506 条 CAICT 旧记录，占总量约 56.7%，因此 CAICT 占比低于 45% 的扩展目标尚未达到。这些记录沿用 QA 记录原有的 CC BY 4.0 许可；数据集所有者已确认其可重新发布。该许可不代表底层 CAICT 报告本身采用 CC BY 4.0，数据包也不包含报告原件。

本版本不含 RAG 基线或模型性能结果。范围和发布门槛见 `DATA_CARD.md`、`LICENSE_STATUS.md` 与 `VALIDATION_REPORT.json`。

## 许可

本数据集采用逐条混合许可，**整个仓库不适用单一许可**。每条记录携带适用的记录许可和署名信息。CAICT 旧题的许可仅适用于 QA 记录，不对原报告许可作额外声明。复用前请查看 `LICENSES.md`、`ATTRIBUTION.md`、`sources.json` 和记录中的 `publication_rights`。由于许可混合，Hugging Face 元数据使用 `license: other`。

## Viewer 字段

读取 Viewer 时请同时查看 `answer_candidate`、`review_status` 和 `recommended_for_evaluation`。`record_json` 保留完整题目、证据定位和逐条权利信息。

## 构建与校验

依次运行 `python3 build_v2_package.py`、`python3 build_hf_splits.py`、`python3 validate_v2_package.py` 和 `python3 build_release_metadata.py`。发布流程见 `PROJECT_CONTEXT.md`，精确数量和哈希见 `manifest.json`。
