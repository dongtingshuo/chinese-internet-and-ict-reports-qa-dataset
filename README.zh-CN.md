# 中文互联网与 ICT 报告问答数据集

**版本：** 2.0.0 · **语言：** 中文 · **活动候选记录：** 387 条 · **推荐 AI 候选子集：** 60 条

本版本收录基于公开中文互联网、ICT、教育技术与数字农业报告构建的问题和简要答案候选。每条记录提供 PDF 物理页码定位，并逐条注明来源许可、署名、改编说明和第三方内容限制。

## 本版本内容

- 保留 327 条 v1.1/v1.2 已登记许可的旧记录作为历史候选；它们仍待 v2 来源文件复核或答案盲化重建，暂不进入推荐子集。
- 新增 60 条 AI 辅助候选题，来自 4 份中文报告，并提供仅含问题的复核包和来源页重建记录。
- 来源清单登记 15 份报告、7 家归并后的发布机构，其中 4 份为 v2.0.0 新增。原定 60 份报告、10 家机构的目标尚未达到；另有 5 份历史来源文件待重新核验。
- 推荐子集按 TRAIN/DEV/TEST = 42/9/9 切分；新增报告家族在出题前分配切分。
- 不包含报告 PDF、图片、表格、图表或长段原文。

活动集共 387 条，尚未达到 2,000 条目标。由于 v1.2.0 来源清单未能证明 CAICT 来源允许改编再发布，原有 506 条 CAICT 记录不纳入 v2 活动集，仍保存在 `history/v1.2.0/`，并逐条列入迁移台账。CAICT 占活动 v2 数据的 0%。

## Hugging Face Viewer 配置

- **candidates**：全部 387 条活动记录。`review_status` 区分待复核旧记录和新增 AI 候选。
- **recommended**：仅含新增的 60 条来源页重建 AI 候选。“推荐”表示可供研究使用的候选子集，不代表人工核验或金标准。

读取 Viewer 时请使用 `answer_candidate` 和 `review_status`；`record_json` 保留完整记录、证据定位及许可元数据。

## 许可

本数据集采用逐条混合许可，**整个仓库不适用单一许可**。每条记录均附适用许可和来源署名要求。推荐子集中，51 条采用 CC BY-SA 3.0 IGO，9 条 FAO 来源记录采用 CC BY-NC-SA 3.0 IGO。复用前请查看 `LICENSES.md`、`LICENSE_STATUS.md`、`ATTRIBUTION.md` 和记录中的 `publication_rights`。由于许可混合，Hugging Face 元数据使用 `license: other`。

## 复核状态与限制

新增记录通过 AI 辅助的答案盲化复核包，根据中文来源页重建答案与证据。起草和复核由同一活动 AI 会话完成，不声称独立复核；所有记录的 `human_reviewed` 均为 false，新记录的 `gold_candidate` 为 false。旧记录仍待 v2 复核。历史切分是在标注后分配，既往系统接触情况未经审计。本版本不含 RAG 基线或模型性能结果。

## 构建与校验

依次运行 `python3 build_v2_package.py`、`python3 build_hf_splits.py`、`python3 build_release_metadata.py` 和 `python3 validate_v2_package.py`。发布流程见 `PROJECT_CONTEXT.md`，精确数量和哈希见 `manifest.json`。
