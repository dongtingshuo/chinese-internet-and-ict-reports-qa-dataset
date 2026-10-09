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

**版本：** 2.1.0 · **语言：** 中文 · **统一数据集：** 2,508 条 · **推荐评测子集：** 2,508 条

v2.1.0 保留完整的 v2.0.0 数据集，并在同一个数据集中新增 508 条非填空、经来源重建的问答。v2.0.0 的原始发布包保存在 `history/v2.0.0/`。

## 数据内容

- 833 条历史记录、60 条既有来源重建候选题、1,107 条规则生成的句子填空题，以及 508 条 v2.1 来源重建题。
- 共 61 份来源文档、50 个报告家族和 10 家归并后的出版机构。508 条新增题使用已登记的中文来源，没有增加新报告文件。
- TRAIN/DEV/TEST 分别为 1,681/397/430 条。508 条新增记录继承了预先分配的报告家族切分，新增部分各切分为 304/97/107 条；跨报告来源保持在同一切分。
- Hugging Face Viewer 的 `candidates` 和 `recommended` 两种配置都包含全部 2,508 条。按数据集所有者要求，所有记录均保留在推荐子集；选择评测数据时仍需查看每条记录的 `review_status`。
- 数据包不含来源报告 PDF、图片、表格、图表或长段原文。v2.0.0 的 1,107 条填空记录仍保留各自的短句摘录及待核验状态。

## 复核状态与限制

508 条 v2.1 题目使用不含候选答案的问题包和引用的官方中文来源 PDF，进行了 AI 辅助的第二轮答案、必要事实、物理页码和来源哈希重建。完整记录见 `audit/v2_1_answer_blind_reconstruction.jsonl`。这不是独立 AI 会话或人工复核；所有新增记录继续标记 `human_reviewed: false`，不称为金标准。20 条缺少完整重建审计的草案、6 条标签无效题和8条近重复题未纳入本版，处理结果见 `audit/v2_1_candidate_disposition_ledger.jsonl`。

依赖表格的题目在 `locator_details` 中标明表号及相关行/列标签或脚注标记；叙述性证据则指向物理 PDF 页码和文本区域。这些定位信息用于找到来源证据，不会复现来源表格内容。

1,107 条填空题仍为 `pending_ai_content_verification`；确定性挖空时答案可见，第三方署名筛查仍待完成。833 条历史记录保留原有审核状态，本版不声称已对它们完成答案盲化重建。纳入推荐子集是所有者的决定，不代表审核状态已改变。

## 来源和许可

数据集采用逐条混合许可，不存在适用于全仓库的单一许可。每条记录都保留适用的数据许可、来源署名、改编声明和其他义务。v2.1 新增题目是对 `sources.json` 已登记来源的简要改写；来源哈希、授权声明和译本信息均有记录。数据包不再分发报告 PDF 或媒体。详情见 `LICENSES.md`、`LICENSE_STATUS.md`、`ATTRIBUTION.md` 及记录中的 `publication_rights`。

历史切分是在标注后分配的，不是盲测集；既有系统接触情况未审计。数据包不含 RAG 基线或模型性能结果，也不声称全库为金标准。

## Viewer 字段

请结合 `answer_candidate`、`review_status` 和 `recommended_for_evaluation` 使用。`record_json` 保存完整记录、证据定位和许可信息。

## 重建与校验

v2.1 从冻结的 v2.0.0 快照和记录的问题包/答案重建审计中生成：

```bash
python3 build_v2_1_package.py
python3 build_hf_splits.py
python3 validate_v2_package.py
python3 build_release_metadata.py
```

`build_v2_package.py` 是历史 v2.0 构建器；检测到活动 v2.1 数据后会停止，防止覆盖新发布。来源 PDF 和完整提取文本保留在仓库之外。
