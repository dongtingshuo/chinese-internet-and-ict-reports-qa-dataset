#!/usr/bin/env python3
"""Build the v1.2.0 source-grounded additions without rewriting the frozen v1.1 prefix."""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RECORDS = ROOT / "records.jsonl"
ASSIGNMENTS = ROOT / "split_assignments.jsonl"
SOURCES = ROOT / "sources.json"
NEW_COUNT = 60
BASE_COUNT = 773
REVIEW_DATE = "2026-10-06"

LICENSES = {
    "CC-BY-3.0-IGO": ("CC BY 3.0 IGO", "https://creativecommons.org/licenses/by/3.0/igo/"),
    "CC-BY-4.0": ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "CC-BY-SA-3.0-IGO": ("CC BY-SA 3.0 IGO", "https://creativecommons.org/licenses/by-sa/3.0/igo/"),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


baseline_records = RECORDS.read_bytes().splitlines(keepends=True)
baseline_assignments = ASSIGNMENTS.read_bytes().splitlines(keepends=True)
if len(baseline_records) != BASE_COUNT or len(baseline_assignments) != BASE_COUNT:
    raise SystemExit("Expected the frozen v1.1.0 package with 773 records and assignments")

old_records = [json.loads(line) for line in baseline_records]
old_sources_doc = json.loads(SOURCES.read_text(encoding="utf-8"))
source_catalog = copy.deepcopy(old_sources_doc["sources"])
source_by_id = {source["source_id"]: source for source in source_catalog}
source_ref_by_id = {}
family_by_id = {}
for row in old_records:
    for ref in row.get("source_refs", []):
        source_ref_by_id.setdefault(ref["source_id"], copy.deepcopy(ref))
    for sid in row.get("source_ids", []):
        family_by_id.setdefault(sid, row.get("family_id", f"family-{sid.lower()}"))

new_source_metadata = [
    {
        "source_id": "ILO2026-LIFELONG-SKILLS",
        "publication_institution": "International Labour Organization",
        "publisher": "国际劳工组织（ILO）",
        "publication_year": 2026,
        "title_chinese": "面向未来的终身学习与技能——执行摘要",
        "title_english": "Lifelong learning and skills for the future (Executive summary)",
        "text_language": "Chinese",
        "document_type": "Official Chinese-language executive summary in the World of Work report series",
        "translation_status": "Official Chinese-language executive summary hosted by ILO; the dataset author did not translate the source. The full flagship report is not included.",
        "original_report_url": "https://doi.org/10.54394/00033011",
        "official_publication_page_url": "https://www.ilo.org/zh-hans/publications/flagship-reports/面向未来的终身学习与技能-执行摘要",
        "original_report_sha256": "810eeaafd7acdfa2e30c36cde4f9b94be2d79d86ef8dc604f70614b601fff75e",
        "source_pdf_page_count": 12,
        "parent_report_url": "https://www.ilo.org/zh-hans/publications/flagship-reports/面向未来的终身学习与技能-执行摘要",
        "parent_report_sha256": None,
        "rights_holder": "International Labour Organization",
        "license": "CC BY 4.0",
        "license_id": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "rights_notice_location": {
            "document": "Chinese executive-summary PDF",
            "pdf_page_1based": 12,
            "url": "https://doi.org/10.54394/00033011",
            "pdf_page_count": 12,
            "pdf_sha256": "810eeaafd7acdfa2e30c36cde4f9b94be2d79d86ef8dc604f70614b601fff75e",
        },
        "required_attribution": "International Labour Organization. 2026. Lifelong learning and skills for the future (Chinese executive summary), World of Work report series. Geneva: ILO. © ILO 2026. CC BY 4.0. https://doi.org/10.54394/00033011",
        "required_adaptation_disclaimer": "This record is an AI-assisted paraphrase/adaptation of the cited ILO publication. Responsibility for this adaptation rests with the dataset publisher; no ILO endorsement is implied.",
        "translation_disclaimer": None,
        "third_party_content_limitations": "Only concise paraphrased facts and physical-page locators are used. No third-party table, figure, photograph, media, source passage, or PDF is included.",
        "source_pdf_included": False,
        "edition_note": "The released source is the 12-page official Chinese executive summary, not the full flagship report.",
    },
    {
        "source_id": "UNESCO2023-DIGITAL-CITIZENSHIP",
        "publication_institution": "UNESCO Institute for Information Technologies in Education and Shanghai Open University",
        "publisher": "联合国教科文组织教育信息技术研究所（UNESCO IITE）与上海开放大学",
        "publication_year": 2023,
        "title_chinese": "全球数字公民教育实践的测评与评价工具包：以人工智能为支撑，推动全球数字公民教育",
        "title_english": "Global Practices Evaluation & Assessment Toolkit: Advancing Artificial Intelligence-Supported Global Digital Citizenship Education",
        "text_language": "Chinese",
        "document_type": "Official Chinese-language toolkit published by UNESCO IITE and Shanghai Open University",
        "translation_status": "Official Chinese-language edition linked from the UNESCO IITE publication page; the dataset author did not translate the source.",
        "original_report_url": "https://iite.unesco.org/wp-content/uploads/2023/03/CHINESE_UNESCO-IITE-SOU.-2023.-Global-Practices-Evaluation-Assessment-Toolkit.-Advancing-Artificial-Intelligence-Supported-Global-Digital-Citizenship-Education.pdf",
        "official_publication_page_url": "https://iite.unesco.org/publications/global-practices-evaluation-assessment-toolkit-advancing-artificial-intelligence-supported-global-digital-citizenship-education/",
        "original_report_sha256": "06b67090ac204c60f5a5fa9857619e375d8c1f51b99c70756a63414e76025314",
        "source_pdf_page_count": 25,
        "parent_report_url": None,
        "parent_report_sha256": None,
        "rights_holder": "UNESCO Institute for Information Technologies in Education and Shanghai Open University",
        "license": "CC BY-SA 3.0 IGO",
        "license_id": "CC-BY-SA-3.0-IGO",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0/igo/",
        "rights_notice_location": {
            "document": "Chinese toolkit PDF",
            "pdf_page_1based": 2,
            "url": "https://iite.unesco.org/wp-content/uploads/2023/03/CHINESE_UNESCO-IITE-SOU.-2023.-Global-Practices-Evaluation-Assessment-Toolkit.-Advancing-Artificial-Intelligence-Supported-Global-Digital-Citizenship-Education.pdf",
            "pdf_page_count": 25,
            "pdf_sha256": "06b67090ac204c60f5a5fa9857619e375d8c1f51b99c70756a63414e76025314",
        },
        "required_attribution": "UNESCO IITE and Shanghai Open University. 2023. Global Practices Evaluation & Assessment Toolkit: Advancing Artificial Intelligence-Supported Global Digital Citizenship Education. CC BY-SA 3.0 IGO. https://iite.unesco.org/publications/global-practices-evaluation-assessment-toolkit-advancing-artificial-intelligence-supported-global-digital-citizenship-education/",
        "required_adaptation_disclaimer": "This record is an AI-assisted adaptation of the cited toolkit. The adapted record is released under CC BY-SA 3.0 IGO; no UNESCO or Shanghai Open University endorsement is implied.",
        "translation_disclaimer": None,
        "third_party_content_limitations": "The PDF contains third-party visual material, including an Unsplash image on physical page 11. This dataset uses only the toolkit-authored scoring tables on physical pages 19 and 22; it reproduces no image, table contents, source passage, or PDF.",
        "source_pdf_included": False,
        "edition_note": "The Chinese PDF states that the authors' views do not necessarily represent UNESCO or Shanghai Open University.",
    },
    {
        "source_id": "ILO2021-EMPLOYMENT-RELATIONSHIP",
        "publication_institution": "International Labour Organization",
        "publisher": "国际劳工组织（ILO）",
        "publication_year": 2021,
        "title_chinese": "平台工作与雇佣关系",
        "title_english": "Platform work and the employment relationship",
        "text_language": "Chinese",
        "document_type": "Chinese translation of ILO Working Paper 27",
        "translation_status": "The source PDF identifies itself as a Chinese translation and states that it was not created by the ILO and is not an official ILO translation; its disclaimer is retained per record.",
        "original_report_url": "https://www.ilo.org/sites/default/files/wcmsp5/groups/public/%40asia/%40ro-bangkok/%40ilo-beijing/documents/publication/wcms_816515.pdf",
        "official_publication_page_url": "https://www.ilo.org/zh-hans/publications/平台工作与雇佣关系",
        "original_report_sha256": "141416c46361de707b209db9868b9da1342433d2ba3ee7ebdeb69c7c0cd304b1",
        "source_pdf_page_count": 49,
        "parent_report_url": "https://www.ilo.org/publications/platform-work-and-employment-relationship",
        "parent_report_sha256": None,
        "rights_holder": "International Labour Organization",
        "license": "CC BY 3.0 IGO",
        "license_id": "CC-BY-3.0-IGO",
        "license_url": "https://creativecommons.org/licenses/by/3.0/igo/",
        "rights_notice_location": {
            "document": "Chinese Working Paper PDF",
            "pdf_page_1based": 2,
            "url": "https://www.ilo.org/sites/default/files/wcmsp5/groups/public/%40asia/%40ro-bangkok/%40ilo-beijing/documents/publication/wcms_816515.pdf",
            "pdf_page_count": 49,
            "pdf_sha256": "141416c46361de707b209db9868b9da1342433d2ba3ee7ebdeb69c7c0cd304b1",
        },
        "required_attribution": "International Labour Organization. 2021. Platform work and the employment relationship (Chinese translation), ILO Working Paper 27. Geneva: ILO. CC BY 3.0 IGO. https://www.ilo.org/zh-hans/publications/平台工作与雇佣关系",
        "required_adaptation_disclaimer": "This is an adaptation of an original work by the International Labour Office (ILO). Responsibility for the views expressed in this adaptation rests with the author(s) of the adaptation and is not endorsed by the ILO.",
        "translation_disclaimer": "This translation was not created by the International Labour Office (ILO) and should not be considered an official ILO translation. The ILO is not responsible for the content or accuracy of this translation.",
        "third_party_content_limitations": "The report reviews laws and case materials. Only concise paraphrases of the report's own study description and findings are used; no third-party legal text, case excerpt, image, table, media, source passage, or PDF is included.",
        "source_pdf_included": False,
        "edition_note": "The Chinese PDF is 49 physical pages; its printed pagination is recorded separately on evidence locators.",
    },
]

for source in new_source_metadata:
    if source["source_id"] in source_by_id:
        raise SystemExit(f"Source already exists: {source['source_id']}")
    source_catalog.append(source)
    source_by_id[source["source_id"]] = source


def locator(sid, page, element, locator_type="narrative_text_region", printed=None, visual=None):
    item = {
        "source_id": sid,
        "element_id": element,
        "locator_type": locator_type,
        "pdf_page": page,
        "printed_page": printed,
    }
    if visual is not None:
        item["visual_locator"] = visual
    return item


def fact(text, loc):
    return {"statement": text, "locator": loc}


def add_answerable(kind, split, question, answer, facts, visual_dependency=None):
    specs.append({
        "question_type": kind,
        "split": split,
        "question": question,
        "gold_answer": answer,
        "facts": facts,
        "visual_dependency": visual_dependency,
    })


def add_unanswerable(split, sid, question, answer, missing, pages, terms, method, near):
    specs.append({
        "question_type": "unanswerable_absence",
        "split": split,
        "source_ids": [sid],
        "question": question,
        "gold_answer": answer,
        "facts": [],
        "absence_verification": {
            "search_scope": [{
                "source_id": sid,
                "pdf_pages_1based_inclusive": pages,
                "scope_note": f"The checked retrieval scope is physical PDF pages {pages[0]} through {pages[1]} of the cited source.",
            }],
            "missing_proposition": missing,
            "search_terms": terms,
            "review_method": method,
            "near_miss_evidence": near,
        },
        "visual_dependency": None,
    })


def near(sid, page, element, summary, why, printed=None):
    return {
        "source_id": sid,
        "pdf_page": page,
        "printed_page": printed,
        "element_id": element,
        "nearby_fact_summary": summary,
        "why_insufficient": why,
    }


def table_locator(sid, page, printed, elem, table_id, title, row, column, value, table_note):
    visual = {
        "visual_id": table_id,
        "visual_title": title,
        "visual_type": "table",
        "row_label": row,
        "column_label": column,
        "cell_value": value,
        "visual_relation": table_note,
    }
    return locator(sid, page, elem, "table_cell", printed, visual)


def figure_locator(sid, page, printed, elem, figure_id, title, region, label, relation):
    visual = {
        "visual_id": figure_id,
        "visual_title": title,
        "visual_type": "figure",
        "region": region,
        "cell_or_node_label": label,
        "visual_relation": relation,
    }
    return locator(sid, page, elem, "figure_component", printed, visual)


specs = []

# 20 unanswerable items: each has an explicit scope, search terms, method, and a near miss.
S = "ILO2026-LIFELONG-SKILLS"
add_unanswerable("TRAIN", S, "执行摘要给出的全球终身学习公共支出占 GDP 的精确比例是多少？",
    "该12页中文执行摘要没有给出这一全球比例；它讨论公平融资和公共投资，但不能据此计算支出占 GDP 的比例。",
    "全球终身学习公共支出占 GDP 的数值", [1, 12], ["GDP", "国内生产总值", "公共支出", "融资", "投资", "百分比", "比例"],
    "对所列12页全文做提取文本检索并逐页复核包含融资、投资和全球现状的上下文；报告仅给出政策方向，没有该比例。",
    [near(S, 9, "ilo2026-ll-p0009-funding", "摘要建议公共投资优先支持弱势群体，并讨论雇主共同融资和个人学习账户。", "这些是政策建议，没有全球支出总额或 GDP 分母。", 8)])
add_unanswerable("TRAIN", S, "摘要报告的女性与男性终身学习参与率相差多少个百分点？",
    "摘要指出性别差距仍然存在，但未报告男女参与率或差距百分点。",
    "按性别分别统计的参与率以及男女百分点差", [1, 12], ["女性", "男性", "性别差距", "参与率", "百分点", "男女"],
    "检索性别、女性、男性和参与率等词，并复核有关学习机会和性别差异的整页段落；找到定性陈述，未找到可相减的男女数值。",
    [near(S, 5, "ilo2026-ll-p0005-learning-findings", "摘要说不同群体参与的学习类型和收益有显著差异，并指出性别差距仍存在。", "该段未按性别给出参与率或数值差。", 4)])
add_unanswerable("TRAIN", S, "报告列出的八个中高收入国家中，人工智能技能岗位的招聘广告占比各是多少？",
    "摘要提到八个国家的技能需求分析以及机器学习、人工智能相关技能，但没有列出各国 AI 岗位广告占比。",
    "八个国家各自的 AI 技能招聘广告数量或占比", [5, 8], ["八个国家", "招聘广告", "人工智能", "AI", "机器学习", "招聘信息", "占比", "百分比"],
    "在技能需求章节的物理页5至8检索国家名、招聘广告、AI、机器学习和比例，并复核对应段落；摘要说明分析范围与排序，不提供逐国岗位广告占比。",
    [near(S, 6, "ilo2026-ll-p0006-demanded-skills", "摘要指出社会情感技能和认知技能常处于高需求位置，也提及机器学习和 AI 技能。", "这类摘要结论没有逐国岗位数或百分比。", 5)])
add_unanswerable("TRAIN", S, "报告估算每位劳动者掌握 AI 技能后平均增加多少工资？",
    "摘要称技能复杂度与工资溢价相关，但没有给出掌握 AI 技能后的统一工资增幅。",
    "AI 技能对应的平均工资增幅或因果效应", [5, 8], ["工资溢价", "工资", "人工智能", "AI", "技能复杂度", "平均", "增加"],
    "检索工资、溢价、AI和技能复杂度，并逐页复核工资与技能组合的论述；摘要仅描述相关方向和情境差异，没有给出 AI 技能的统一增幅。",
    [near(S, 6, "ilo2026-ll-p0006-wage-premium", "摘要说技能复杂度提升与工资溢价上升相关，回报因国家、职业和技能组合而异。", "这不是 AI 技能单独的平均工资增幅或因果估计。", 5)])
add_unanswerable("TRAIN", S, "在八个国家中，雇主提供培训占劳动者全部终身学习活动的比例分别是多少？",
    "摘要说明雇主提供的培训是有组织学习活动的重要形式，但未给出八国的雇主培训占比。",
    "八个国家中雇主培训占全部学习活动的分国比例", [3, 9], ["雇主提供", "雇主培训", "八个国家", "终身学习活动", "占比", "百分比"],
    "检索雇主、培训、国家和百分比，复核学习类型及制度建议页面；出现了雇主培训这一类别，没有分国占比表。",
    [near(S, 5, "ilo2026-ll-p0005-organized-learning", "摘要将职业教育培训和雇主提供培训列为有组织学习活动的核心形式。", "分类说明未提供分国数量或占比。", 4)])
add_unanswerable("TRAIN", S, "摘要中参加 AI 专项培训的劳动者有多少人？",
    "摘要没有报告 AI 专项培训的参与人数；AI 主要出现在技能需求和高阶数字技能的讨论中。",
    "AI专项培训的劳动者人数", [1, 12], ["人工智能培训", "AI培训", "参加人数", "受训人数", "人次", "机器学习"],
    "检索 AI、机器学习、培训、参与人数和人次，复核摘要全页；找到 AI 技能需求论述，但没有 AI 专项培训项目样本人数。",
    [near(S, 6, "ilo2026-ll-p0006-ai-skills", "摘要将机器学习和人工智能列为高阶数字技能例子。", "技能例子不等同于 AI 培训参加人数。", 5)])
add_unanswerable("TRAIN", S, "摘要给出的学校教育、工作中学习和社会学习三类场景各自占比是多少？",
    "摘要提出这三类终身学习场景，但未给出各场景占全部学习活动的百分比。",
    "学校教育、工作中学习和社会学习各自的参与占比", [3, 5], ["学校教育", "工作中学习", "社会学习", "比例", "占比", "百分比"],
    "检索三类学习场景和比例相关表达，并复核概念框架及学习现状页；找到分类框架与群体差异，没有三场景的可比百分比。",
    [near(S, 4, "ilo2026-ll-p0004-three-pillars", "摘要将终身学习框架分为学校教育、工作中学习和更广泛的社会学习。", "框架列出维度，但没有每类学习活动的占比数据。", 3)])

S = "ILO2020-PLATFORM"
add_unanswerable("TRAIN", S, "ILO 2019年问卷中，表9所列接受工作相关技能培训者的绝对人数是多少？",
    "表9报告的是培训类别百分比，没有给出该类别的绝对人数；不能仅凭16.7%反推出人数。",
    "表9中工作相关技能培训类别的样本绝对人数或该项百分比的分母", [24, 24], ["表9", "工作相关的技能培训", "16.7%", "人数", "样本量", "分母"],
    "逐项核读物理页24（印刷页22）的表9行列，并检索人数、样本量和分母；表内给出百分比但未给出该行绝对人数或独立分母。",
    [near(S, 24, "ilo2020-platform-p0024-table9", "表9将工作相关技能培训列为16.7%。", "该单元格是比例，不含该类受访者的绝对计数或可据以还原计数的分母。", 22)])
add_unanswerable("TRAIN", S, "表9所列培训使猪八戒平台从业者平均收入提高了多少？",
    "表9统计培训类型和受访者对培训有用性的评价，不报告培训导致的收入变化。",
    "表9培训活动对应的平均收入变化或因果工资效应", [24, 24], ["表9", "收入", "工资", "培训效果", "提高", "平均", "因果"],
    "核对物理页24表9的全部行列，并检索收入、工资和变化；邻近文本评价培训内容和主观有用性，没有培训前后收入比较。",
    [near(S, 24, "ilo2020-platform-p0024-table9", "表9报告20.1%的培训机会、13.4%的参与率以及多种培训内容和有用性评价。", "这些是参与和主观评价指标，不是收入变化测量。", 22)])

S = "WB2014-RURAL"
add_unanswerable("TRAIN", S, "《中国农村信息化：三省研究》单独估算的农村家庭互联网使用率是多少？",
    "概要只报告“拥有个人电脑或使用互联网”的合并比例为20%，没有单独拆分互联网使用率。",
    "农村家庭中仅使用互联网的独立比例", [1, 4], ["互联网使用率", "使用互联网", "拥有个人电脑", "20%", "家庭比例"],
    "逐页核读4页中文概要并检索互联网使用率、家庭、电脑和20%；命中指标把电脑拥有与互联网使用合并报告，未发现拆分统计。",
    [near(S, 1, "wb2014-rural-p0001-narrative", "概要称20%的受访家庭拥有个人电脑或使用互联网。", "这是逻辑或合并口径，不能解释为单独的互联网使用率。")])
add_unanswerable("TRAIN", S, "该概要中完成数字技能课程的农村居民人数是多少？",
    "概要指出培训机会有限，但没有给出完成数字技能课程的居民人数。",
    "完成数字技能课程的农村居民绝对人数", [1, 4], ["数字技能课程", "培训完成", "完成课程", "学员人数", "培训人数"],
    "逐页检索技能培训、课程、完成和人数，并复核基础设施与建议章节；找到培训机会描述和不足10%的设施比例，没有课程完成人数。",
    [near(S, 1, "wb2014-rural-p0001-narrative", "概要称提供培训的公共信息化设施不到10%。", "设施比例不是学员人数，也没有给出完课统计。")])

S = "WB2025-DIGITAL"
add_unanswerable("TRAIN", S, "图O.1的四个C各自贡献了多少百分比的 AI 应用成效？",
    "图O.1是概念框架，没有为四个C标注贡献百分比或因果权重。",
    "Connectivity、Compute、Context、Competency各自的量化成效贡献", [14, 14], ["图O.1", "4C", "贡献", "百分比", "权重", "成效"],
    "直接检查物理页14的图O.1及其邻近说明，搜索贡献、权重和百分比；图中列出概念维度与关系，不包含数值轴或贡献值。",
    [near(S, 14, "wb2025-digital-p0014-figure-o1", "图O.1把四个C与本地需求的 AI 应用场景和负责任治理放在同一框架中。", "示意图没有数值轴、权重或百分比。", 2)])
add_unanswerable("TRAIN", S, "报告统计了多少比例的本地 AI 用例因为缺少 Context 而失败？",
    "报告没有给出按Context缺失分类的AI用例失败率；图O.1只把Context作为框架维度。",
    "因缺少Context导致的AI用例失败数量或比例", [14, 14], ["Context", "情境", "AI用例", "失败", "比例", "案例数量"],
    "直接核读图O.1和邻近说明，检索情境、失败、用例和比例；图示的是情境数据维度，不是失败率统计。",
    [near(S, 14, "wb2025-digital-p0014-figure-o1", "图中将Context解释为适合本地情境的高质量数据和内容。", "这一定义没有统计因缺少情境数据而失败的项目。", 2)])
add_unanswerable("TRAIN", S, "图O.10所示数据经纪阶段创造的年度收入总额是多少？",
    "图O.10展示数据生产链阶段和活动，没有列出数据经纪收入金额或年度统计。",
    "图O.10数据经纪阶段的年度收入数值", [24, 24], ["图O.10", "数据经纪", "收入", "年度", "美元", "金额"],
    "直接检查物理页24图O.10、阶段标签和箭头，并搜索收入、年度和金额；图示说明经纪活动类型，没有货币轴或金额。",
    [near(S, 24, "wb2025-digital-p0024-figure-o10", "数据经纪阶段列出变现、汇总和定制化分析等活动。", "活动清单没有提供其产生的收入数值。", 12)])

S = "ADB2023-YOUTH"
add_unanswerable("DEV", S, "报告分别给出了中国各省 ICT 行业青年失业率的哪些数值？",
    "报告把ICT列为新经济相关领域，但没有列出按省份和ICT行业交叉统计的青年失业率。",
    "各省ICT行业青年失业率的分省数值", [1, 16], ["省", "ICT", "信息通信技术", "青年失业率", "分省", "百分比"],
    "对16页中文报告检索省份、ICT、青年失业率和百分比，并复核新经济及就业分析页；报告给出全国青年失业率和地区政策建议，没有省份乘行业交叉表。",
    [near(S, 12, "adb2023-youth-p0012-narrative", "报告将信息与通信技术列为新经济领域，并讨论青年所需技能。", "领域与技能描述没有分省的ICT行业失业率。")])
add_unanswerable("DEV", S, "报告估算有多少比例的中国青年在数字劳工平台就业？",
    "报告没有估算青年数字劳工平台就业占比；其新经济讨论不等同于平台工作统计。",
    "中国青年数字劳工平台就业人数或占比", [1, 16], ["数字劳工平台", "平台就业", "青年", "占比", "比例", "人数"],
    "检索平台、数字劳工、青年就业、比例和人数，并复核就业与新经济章节；报告有青年就业和ICT领域论述，没有平台劳动者统计。",
    [near(S, 12, "adb2023-youth-p0012-narrative", "报告讨论ICT和低碳经济相关的新经济岗位及青年技能。", "新经济范围不是平台就业的定义，也未提供其青年占比。")])

S = "WB2016-DIGITAL"
add_unanswerable("DEV", S, "《数字红利》中文概述给出的印度数字身份项目节省的精确腐败成本是多少美元？",
    "概述只称该项目避免了数十亿美元的腐败成本，没有给出精确美元数值。",
    "印度数字身份项目避免腐败成本的精确金额", [1, 1], ["印度", "数字身份", "腐败成本", "美元", "精确金额", "数十亿美元"],
    "核读中文概述物理页1并检索金额、美元、腐败和数字身份；来源使用“数十亿美元”的概括表达，未给精确数值。",
    [near(S, 1, "wb2016-digital-p0001-narrative", "概述以印度数字身份避免数十亿美元腐败成本作为数字技术案例。", "“数十亿美元”是数量级表述，不能确定精确金额。")])

S = "ILO2021-PLATFORM"
add_unanswerable("TEST", S, "表1中的三个平台样本可以代表中国全部数字平台工作者的比例是多少？",
    "报告明确说无法确认样本具有统计代表性，且没有通用平台工作者数据库，因此不能从表1计算全国代表比例。",
    "三个平台样本占中国全部数字平台工作者的比例或代表性权重", [11, 12], ["代表性", "全国", "样本权重", "总体比例", "平台工作者数据库", "随机抽样"],
    "核读调查设计物理页11至12，并检索代表性、数据库、随机样本和权重；页12直接说明代表性未知且无法随机抽样。",
    [near(S, 12, "ilo2021-platform-p0012-table1-and-caveat", "表1给出三个入选平台的有效问卷数合计1071，紧接文字说明代表性未知。", "样本构成表没有全国总体分母或抽样权重。", 10)])
add_unanswerable("TEST", S, "根据表1，2019年中国所有数字劳工平台上工作的总人数是多少？",
    "表1列的是三个入选平台的问卷样本，不是全部平台从业者人口；报告还说明没有通用平台工作者数据库。",
    "2019年中国所有数字劳工平台工作者总体人数", [11, 12], ["表1", "总人数", "中国所有平台", "数据库", "从业者人口", "总体"],
    "核对物理页11至12的调查对象、样本平台与表1；表1仅统计受访者，报告说明没有全体平台工作者数据库。",
    [near(S, 12, "ilo2021-platform-p0012-table1-and-caveat", "表1统计时间财富、一品威客和猪八戒的样本数量。", "受访样本不是全部平台工作者的总体人数。", 10)])

S = "ILO2021-EMPLOYMENT-RELATIONSHIP"
add_unanswerable("TEST", S, "《平台工作与雇佣关系》作者自行调查了多少名中国平台工人？",
    "该报告分析各国判例法和立法，并未报告作者自行开展的中国工人问卷调查样本。",
    "该法律比较研究自行收集的中国平台工人问卷人数", [1, 49], ["中国工人问卷", "中国样本", "受访者", "调查样本", "问卷", "人数"],
    "检索49页报告中的中国、问卷、样本、受访者与人数，并核对摘要、引言和结论；报告说明研究对象是国家及超国家判例法与立法。",
    [near(S, 3, "ilo2021-global-p0003-abstract", "摘要说明文章分析平台工人就业性质的判例法和立法，并参考第198号建议书。", "法律比较研究的摘要没有描述作者的中国工人问卷或样本。", 1)])

# 20 cross-document synthesis items. Each required fact is independently supported by one cited source.
add_answerable("cross_document_synthesis", "TRAIN",
    "农村调查中“拥有个人电脑或使用互联网”的家庭比例是多少？结合图O.1，除连接性外的三个C是什么？",
    "该合并口径比例为20%；图O.1的另外三个C是算力（Compute）、情境（Context）和能力（Competency）。",
    [fact("2012年问卷调查中，20%的农村家庭拥有个人电脑或使用互联网；来源未将两者拆分。", locator("WB2014-RURAL", 1, "wb2014-rural-p0001-narrative")),
     fact("图O.1将四个C列为连接性、算力、情境和能力。", figure_locator("WB2025-DIGITAL", 14, 2, "wb2025-digital-p0014-figure-o1", "Figure O.1", "开发和利用AI技术的4C基础", "四个并列支柱", "Connectivity、Compute、Context、Competency", "读取四个并列图块，排除连接性后列出其余三项。"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "农村调查称所有乡村都已通电并能收到手机信号；根据图O.1，要形成高影响力的本地AI应用，框架还列出哪些支持维度？",
    "除基础连接条件外，图O.1还列出算力、情境和能力，并把它们放在面向本地需求的AI应用场景与负责任治理之间。",
    [fact("问卷调查称所有乡村通电且能收到手机信号。", locator("WB2014-RURAL", 1, "wb2014-rural-p0001-narrative")),
     fact("图O.1在四个C的连接性之外列出算力、情境、能力，并标注本地AI应用场景及协调且负责任的治理。", figure_locator("WB2025-DIGITAL", 14, 2, "wb2025-digital-p0014-figure-o1", "Figure O.1", "开发和利用AI技术的4C基础", "四C图块及上下方横栏", "Compute、Context、Competency", "需要同时读取上下横栏与四个支柱的关系。"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "农村概要说提供培训的公共信息化设施不到10%；图O.1的四个C中，哪一项直接指向劳动者的AI技能和专家人才？",
    "公共信息化设施中提供培训者不到10%；图O.1中直接指向AI技能劳动者和专家人才的维度是能力（Competency）。",
    [fact("提供培训的公共信息化设施不到10%。", locator("WB2014-RURAL", 1, "wb2014-rural-p0001-narrative")),
     fact("图O.1将Competency说明为具备AI技能的劳动力和AI专业技术人才。", figure_locator("WB2025-DIGITAL", 14, 2, "wb2025-digital-p0014-figure-o1", "Figure O.1", "开发和利用AI技术的4C基础", "Competency支柱", "Competency：劳动力和AI专业技术人才", "需要定位并读取Competency图块的说明。"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "农村概要指出低电脑/互联网使用与技能不足和不了解技术益处有关；图O.1中，哪个C描述本地情境所需的高质量数据和内容？",
    "农村概要把技能不足和不了解技术益处列为低使用的主要原因；图O.1把适合本地情境的高质量数据和内容放在Context维度。",
    [fact("概要把缺乏使用技能以及不了解电脑和互联网的好处列为低电脑/互联网使用的主要原因。", locator("WB2014-RURAL", 1, "wb2014-rural-p0001-narrative")),
     fact("图O.1中Context对应适合本地情境的高质量数据和内容。", figure_locator("WB2025-DIGITAL", 14, 2, "wb2025-digital-p0014-figure-o1", "Figure O.1", "开发和利用AI技术的4C基础", "Context支柱", "适合本地情境的高质量数据和内容", "需要将四C图块与其说明配对。"))])

add_answerable("cross_document_synthesis", "TRAIN",
    "WB2019提出的三类未来技能是什么？结合ILO表9，猪八戒培训中占比最高的是平台操作培训还是工作相关技能培训，各是多少？",
    "三类技能为高阶认知与问题解决、社交与团队合作、适应性与自我效能；表9中平台基本操作培训为48.6%，工作相关技能培训为16.7%，前者更高。",
    [fact("未来劳动者需要高阶认知与问题解决、社交与团队合作、适应性与自我效能。", locator("WB2019-WORK", 15, "wb2019-work-p0015-narrative")),
     fact("表9显示平台基本操作培训48.6%，工作相关技能培训16.7%。", table_locator("ILO2020-PLATFORM", 24, 22, "ilo2020-platform-p0024-table9", "Table 9", "猪八戒的培训情况（2019年）", "使用平台基本操作培训；与工作相关的技能培训", "百分比", "48.6%；16.7%", "比较两个不同培训类型的表格行。"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "WB2019说宽带支持哪些跨境工作？ILO关于数字劳工平台的报告说明，网络型平台如何组织这些分散劳动者？",
    "宽带连接为远程在线交易和远程工作提供条件；网络型平台通过公开招募把微任务或创意任务外包给地理分散的从业者。",
    [fact("宽带连接为远程在线交易和远程工作提供条件。", locator("WB2019-WORK", 15, "wb2019-work-p0015-narrative")),
     fact("网络型平台通过公开招募，将微任务或创意任务外包给地理上分散的从业者。", locator("ILO2020-PLATFORM", 6, "ilo2020-platform-p0006-narrative"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "WB2019如何解释数字平台扩大业务而不同比例增加雇员或实体资产？ILO报告把平台的核心作用概括为什么？",
    "WB2019用网络效应解释平台扩张；ILO报告把平台核心作用概括为在服务提供者和客户之间协调工作或服务。",
    [fact("数字平台可借助网络效应扩展规模，而不必同步增加大量雇员或实体资产。", locator("WB2019-WORK", 15, "wb2019-work-p0015-narrative")),
     fact("数字劳工平台在服务提供者与客户之间协调工作或服务。", locator("ILO2020-PLATFORM", 6, "ilo2020-platform-p0006-narrative"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "WB2019将平台规模扩张归因于网络效应；ILO报告区分的两类数字劳工平台按什么空间组织方式区分？",
    "网络效应可以推动平台扩张；ILO所述两类平台是通过网络公开征集、面向地理分散人群的网络型平台，以及把任务分配给特定地区个人的基于位置平台。",
    [fact("数字平台通过网络效应扩张规模。", locator("WB2019-WORK", 15, "wb2019-work-p0015-narrative")),
     fact("ILO报告区分网络型平台（地理分散的公开征集）和基于位置的平台（向特定地理区域内人员分派工作）。", locator("ILO2020-PLATFORM", 6, "ilo2020-platform-p0006-narrative"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "WB2019列出的未来劳动者技能包括哪些适应性相关能力？ILO表9中有用与很有用两档合计占多少？",
    "WB2019提到适应性和自我效能；ILO表9中“有用”52.8%与“很有用”38.9%合计91.7%。",
    [fact("未来劳动者技能清单包括适应性和自我效能。", locator("WB2019-WORK", 15, "wb2019-work-p0015-narrative")),
     fact("表9中有用为52.8%，很有用为38.9%。", table_locator("ILO2020-PLATFORM", 24, 22, "ilo2020-platform-p0024-table9", "Table 9", "猪八戒的培训情况（2019年）", "培训是否有用：有用；很有用", "百分比", "52.8%；38.9%", "读取培训有用性两行并合计百分比。"))])

add_answerable("cross_document_synthesis", "TRAIN",
    "WB2025把AI基础概括为大规模数据、算法和计算能力；ILO平台报告中算法承担什么工作？",
    "WB2025列出大规模数据、算法和计算能力三项基础；ILO报告说明平台算法用于快速匹配商品、服务和信息的供需。",
    [fact("报告将大规模数据、算法和计算能力概括为AI发展的重要基础。", locator("WB2025-DIGITAL", 13, "wb2025-digital-p0013-narrative")),
     fact("中国数字劳工平台通过平台控制的算法快速匹配商品、服务和信息的需求与供给。", locator("ILO2020-PLATFORM", 9, "ilo2020-platform-p0009-narrative"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "WB2025说明AI发展需要数据、算法和算力；WB2019指出未来劳动者需要哪些技能组合来适应技术变化？",
    "AI发展基础包括大规模数据、算法和计算能力；劳动者需具备高阶认知与问题解决、社交与团队合作，以及适应性和自我效能等技能。",
    [fact("AI发展的基础包括大规模数据、算法和计算能力。", locator("WB2025-DIGITAL", 13, "wb2025-digital-p0013-narrative")),
     fact("报告概括未来劳动者需要高阶认知与问题解决、社交和团队合作、适应性和自我效能。", locator("WB2019-WORK", 15, "wb2019-work-p0015-narrative"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "图O.1把本地AI用例与哪一治理框架相连？WB2019认为数字平台可通过什么机制扩张规模？",
    "图O.1将本地AI用例基础置于协调且负责任的AI治理之下；WB2019以网络效应解释平台扩张。",
    [fact("图O.1顶部标注面向本地需求的高影响力AI应用场景，底部标注协调和负责任的AI治理。", figure_locator("WB2025-DIGITAL", 14, 2, "wb2025-digital-p0014-figure-o1", "Figure O.1", "开发和利用AI技术的4C基础", "顶部与底部横栏", "本地用例；协调、负责任的治理", "读取图中上下横栏与四C支柱的层次关系。")),
     fact("WB2019指出数字平台可借助网络效应扩大规模。", locator("WB2019-WORK", 15, "wb2019-work-p0015-narrative"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "WB2025的4C图将Context解释为哪类数据和内容？WB2019强调劳动者还需要哪些适应性能力？",
    "图O.1中的Context是适合本地情境的高质量数据和内容；WB2019列出的适应性能力包括适应性和自我效能。",
    [fact("Context支柱指向适合本地情境的高质量数据和内容。", figure_locator("WB2025-DIGITAL", 14, 2, "wb2025-digital-p0014-figure-o1", "Figure O.1", "开发和利用AI技术的4C基础", "Context支柱", "适合本地情境的高质量数据和内容", "读取Context图块及其说明。")),
     fact("报告所列未来劳动者技能包括适应性和自我效能。", locator("WB2019-WORK", 15, "wb2019-work-p0015-narrative"))])
add_answerable("cross_document_synthesis", "TRAIN",
    "WB2025图O.1中Competency覆盖哪些人才能力；ILO表9中与工作相关技能培训占比是多少？",
    "图O.1将Competency指向AI技能劳动者和AI专业技术人才；ILO表9中与工作相关技能培训占16.7%。",
    [fact("图O.1的Competency维度包括具备AI技能的劳动力和AI专业技术人才。", figure_locator("WB2025-DIGITAL", 14, 2, "wb2025-digital-p0014-figure-o1", "Figure O.1", "开发和利用AI技术的4C基础", "Competency支柱", "具备AI技能的劳动力和AI专业技术人才", "读取Competency支柱说明。")),
     fact("表9中与工作相关的技能培训为16.7%。", table_locator("ILO2020-PLATFORM", 24, 22, "ilo2020-platform-p0024-table9", "Table 9", "猪八戒的培训情况（2019年）", "与工作相关的技能培训", "百分比", "16.7%", "读取技能培训行与百分比列。"))])

# DEV cross-document synthesis: World Bank digital-dividend concepts and ADB youth-employment evidence.
add_answerable("cross_document_synthesis", "DEV",
    "ADB把ICT列入哪些青年就业相关的新经济领域，并指出劳动者需要什么？WB2016认为数字投资还需要哪些非数字配套？",
    "ADB将信息与通信技术列为新经济领域，并指出青年需要符合新经济岗位的技能；WB2016要求配套促进准入与竞争的法规、劳动者技能和对公民负责的体制。",
    [fact("ADB报告把ICT列入新经济領域，並指出青年劳动者需具备符合新经济岗位需要的技能。", locator("ADB2023-YOUTH", 12, "adb2023-youth-p0012-narrative")),
     fact("WB2016概述列出促进准入与竞争的法规、帮助劳动者参与新经济的技能，以及对公民负责的体制。", locator("WB2016-DIGITAL", 1, "wb2016-digital-p0001-narrative"))])
add_answerable("cross_document_synthesis", "DEV",
    "ADB建议服务业在疫后复苏中承担什么青年就业作用？WB2016所说的非数字配套机制中，哪几项帮助数字技术效益实现？",
    "ADB建议提升服务业吸纳青年就业的能力；WB2016指出要以促进准入与竞争的法规、劳动者技能和问责体制支撑数字投资。",
    [fact("ADB报告建议提高服务业在疫后复苏中吸纳青年劳动力就业的能力。", locator("ADB2023-YOUTH", 12, "adb2023-youth-p0012-narrative")),
     fact("WB2016概述指出数字红利需要准入与竞争法规、劳动者技能以及对公民负责的体制。", locator("WB2016-DIGITAL", 1, "wb2016-digital-p0001-narrative"))])
add_answerable("cross_document_synthesis", "DEV",
    "ADB认为青年从ICT等新经济中受益需要什么技能？WB2016将数字技术发展效益归纳为哪三种机制？",
    "ADB强调要具备符合新经济岗位需要的技能；WB2016将数字技术效益归纳为包容性、效率和创新。",
    [fact("ADB报告指出青年劳动者需要符合新经济岗位需要的技能。", locator("ADB2023-YOUTH", 12, "adb2023-youth-p0012-narrative")),
     fact("WB2016将数字技术促进发展概括为包容性、效率和创新。", locator("WB2016-DIGITAL", 17, "wb2016-digital-p0017-narrative"))])

# TEST cross-document synthesis compares the China platform survey with a global legal review.
add_answerable("cross_document_synthesis", "TEST",
    "ILO中国平台调查表1统计了多少名有效受访者、来自哪些平台？《平台工作与雇佣关系》全球报告分析的证据类型是什么？",
    "中国调查有1071名有效受访者，来自时间财富、一品威客和猪八戒；全球报告分析国家及超国家判例法和立法。",
    [fact("中国平台调查经数据整理后确认1071份有效问卷，覆盖时间财富、一品威客和猪八戒。", table_locator("ILO2021-PLATFORM", 12, 10, "ilo2021-platform-p0012-table1", "Table 1", "被调查的平台和受访者的分布", "总计", "数量", "1071", "读取总计行并结合平台行识别样本范围。")),
     fact("全球报告分析平台工人就业性质的国家和超国家判例法与立法。", locator("ILO2021-EMPLOYMENT-RELATIONSHIP", 3, "ilo2021-global-p0003-abstract"))])
add_answerable("cross_document_synthesis", "TEST",
    "中国调查报告对三平台样本代表性的判断是什么？全球法律报告在判断雇佣关系时是否主张依赖单一指标？",
    "中国报告说样本的统计代表性未知，且无法随机抽样；全球报告结论说法院往往考量一系列广泛指标，而非单一指标。",
    [fact("中国调查报告明确说不知道受访样本是否具有平台工作者统计代表性，并说明没有通用数据库以便随机抽样。", locator("ILO2021-PLATFORM", 12, "ilo2021-platform-p0012-table1-and-caveat")),
     fact("全球法律报告总结说，法院在判断雇佣关系时往往考虑一系列广泛指标，不依赖单一指标。", locator("ILO2021-EMPLOYMENT-RELATIONSHIP", 31, "ilo2021-global-p0031-conclusion", "narrative_text_region", 29))])
add_answerable("cross_document_synthesis", "TEST",
    "表1中样本最多的平台及其有效受访者数量是什么？结合全球法律报告的结论，为什么该最大平台样本数不能直接决定平台工人的法律身份？",
    "样本最多的是猪八戒，有538名受访者；全球报告指出法律身份需根据一系列事实指标判断，而不是单一数据点。",
    [fact("表1显示猪八戒样本538人，为三个平台中最多。", table_locator("ILO2021-PLATFORM", 12, 10, "ilo2021-platform-p0012-table1", "Table 1", "被调查的平台和受访者的分布", "猪八戒", "数量", "538", "读取猪八戒行与数量列并和其他平台行比较。")),
     fact("全球法律报告认为法院通常会综合多项指标判断雇佣关系。", locator("ILO2021-EMPLOYMENT-RELATIONSHIP", 31, "ilo2021-global-p0031-conclusion", "narrative_text_region", 29))])

# 20 table/chart questions, 14 TRAIN, 3 DEV, and 3 TEST. Locators identify cells or figure structure.
FIG = "Figure O.1"
FIG_TITLE = "开发和利用AI技术的“4C”基础"
o1 = "wb2025-digital-p0014-figure-o1"
figure_questions = [
    ("图O.1列出的四个C分别是什么？", "连接性（Connectivity）、算力（Compute）、情境（Context）和能力（Competency）。", "四个并列支柱", "Connectivity、Compute、Context、Competency", "读取四个并列图块的标题，而不是从邻近正文推断。"),
    ("图O.1四个C上方的蓝色横栏标示了哪类AI应用场景？", "面向本地需求的高影响力AI应用场景。", "上方蓝色横栏", "面向本地需求的高影响力AI应用场景", "需要读取流程图的上方横栏及其层级位置。"),
    ("图O.1四个C下方的蓝色横栏强调哪种AI治理？", "协调和负责任的AI治理，旨在负责且公平地设计与部署AI。", "下方蓝色横栏", "协调和负责任的AI治理", "需要读取流程图底部横栏及其与四个支柱的关系。"),
    ("图O.1中Connectivity支柱把可靠连接和哪一项能源条件并列？", "可持续的能源。", "Connectivity支柱", "可靠的高质量宽带连接；可持续的能源", "需要定位Connectivity图块中的两项并列说明。"),
    ("图O.1的Compute支柱指向哪类可获得资源？", "可负担、可获取的高性能计算资源。", "Compute支柱", "可负担、可获取的高性能计算资源", "需要读取Compute图块的标签和描述。"),
    ("图O.1的Context支柱要求什么类型的数据和内容？", "适合本地情境的高质量数据和内容。", "Context支柱", "适合本地情境的高质量数据和内容", "需要将Context标题与其对应说明配对。"),
    ("图O.1的Competency支柱涵盖哪两类AI人才？", "具备AI技能的劳动力，以及AI专业技术人才。", "Competency支柱", "AI技能劳动力；AI专业技术人才", "需要读取Competency图块中的并列人才类别。"),
]
for q, ans, region, label, relation in figure_questions:
    vis = figure_locator("WB2025-DIGITAL", 14, 2, o1, FIG, FIG_TITLE, region, label, relation)
    add_answerable("table_chart_reasoning", "TRAIN", q, ans,
        [fact(ans, vis)],
        {"visual_type": "figure", "source_id": "WB2025-DIGITAL", "visual_id": FIG, "visual_title": FIG_TITLE,
         "pdf_page": 14, "printed_page": 2, "requires_visual_reading": True, "why": relation})

T9 = "ilo2020-platform-p0024-table9"
table9_questions = [
    ("表9中提供培训机会的猪八戒从业者比例是多少？", "20.1%", "提供培训机会", "20.1%", "读取该指标行与百分比单元格。"),
    ("表9中猪八戒从业者的培训参与率是多少？", "13.4%", "培训参与率", "13.4%", "读取参与率行，不能与培训机会行混淆。"),
    ("表9中使用平台基本操作培训的比例是多少？", "48.6%", "培训类型：使用平台基本操作培训", "48.6%", "读取培训类型列中平台操作对应的百分比单元格。"),
    ("表9中与工作相关的技能培训比例是多少？", "16.7%", "培训类型：与工作相关的技能培训", "16.7%", "读取培训类型行并区分平台操作培训。"),
    ("表9中认为培训“很有用”的受访者比例是多少？", "38.9%", "培训是否有用：很有用", "38.9%", "读取培训有用性分组对应的百分比单元格。"),
    ("表9中认为培训“不太有用”的受访者比例是多少？", "8.3%", "培训是否有用：不太有用", "8.3%", "读取培训有用性分组对应的百分比单元格。"),
    ("表9中认为培训“完全没有用”的受访者比例是多少？", "0.0%", "培训是否有用：完全没有用", "0.0%", "读取培训有用性分组对应的百分比单元格。"),
]
for q, ans, row, val, relation in table9_questions:
    vis = table_locator("ILO2020-PLATFORM", 24, 22, T9, "Table 9", "猪八戒的培训情况（2019年）", row, "百分比", val, relation)
    add_answerable("table_chart_reasoning", "TRAIN", q, ans,
        [fact(f"表9中{row}对应的比例为{val}。", vis)],
        {"visual_type": "table", "source_id": "ILO2020-PLATFORM", "visual_id": "Table 9", "visual_title": "猪八戒的培训情况（2019年）",
         "pdf_page": 24, "printed_page": 22, "requires_visual_reading": True, "why": relation})

# UNESCO scoring tables are licensed CC BY-SA 3.0 IGO and appear only in DEV.
UN = "UNESCO2023-DIGITAL-CITIZENSHIP"
UNESCO_EDU = "unesco-dce-p0019-table-educator-scoring"
UNESCO_COMM = "unesco-dce-p0022-table-community-scoring"
unesco_questions = [
    ("教育工作者评估表中，51分对应哪个评价等级？", "尚可。", 19, 18, UNESCO_EDU, "教育工作者评估系统评分", "48–53分", "评价", "尚可", "跨分数区间与评价列读取对应关系。"),
    ("教育工作者评估表中，42–47分区间对应什么评价？", "需要稍微改进。", 19, 18, UNESCO_EDU, "教育工作者评估系统评分", "42–47分", "评价", "需要稍微改进", "读取分数区间行与评价列的对应单元格。"),
    ("社区、国家和全球伙伴关系评估表中，8分及以下对应什么评价？", "需要重大改进。", 22, 21, UNESCO_COMM, "社区、国家和全球伙伴关系评估系统量表", "8分及以下", "评价", "需要重大改进", "读取另一张评分表的最低区间行与评价列。"),
]
for q, ans, page, printed, elem, title, row, col, val, relation in unesco_questions:
    vis = table_locator(UN, page, printed, elem, "UNESCO scoring table", title, row, col, val, relation)
    add_answerable("table_chart_reasoning", "DEV", q, ans,
        [fact(f"该评分表中{row}对应的评价为{val}。", vis)],
        {"visual_type": "table", "source_id": UN, "visual_id": "UNESCO scoring table", "visual_title": title,
         "pdf_page": page, "printed_page": printed, "requires_visual_reading": True, "why": relation})

ILO21_T1 = "ilo2021-platform-p0012-table1"
ILO21_T3T4 = "ilo2021-platform-p0020-tables3-4"
test_visual_questions = [
    ("表1中有效受访者数量最多的平台是哪一个，共有多少人？", "猪八戒，共538人。", 12, 10, ILO21_T1, "Table 1", "被调查的平台和受访者的分布", "猪八戒", "数量", "538", "读取各平台行与数量列并比较。"),
    ("表3总计列中，过去三个月在猪八戒工作时间最长的比例是多少？", "41.8%。", 20, 18, ILO21_T3T4, "Table 3", "过去3个月工人工作时间最长的平台（百分比）", "猪八戒", "总计", "41.8%", "读取猪八戒行与总计列的交叉单元格。"),
    ("表4总计列中，占比最高的主要平台工作行业及比例是什么？", "设计和相关照片处理，占23.6%。", 20, 18, ILO21_T3T4, "Table 4", "主要平台工作行业分布（百分比）", "设计和相关照片处理", "总计", "23.6%", "比较总计列行业行后识别最高单元格。"),
]
for q, ans, page, printed, elem, tid, title, row, col, val, relation in test_visual_questions:
    vis = table_locator("ILO2021-PLATFORM", page, printed, elem, tid, title, row, col, val, relation)
    add_answerable("table_chart_reasoning", "TEST", q, ans,
        [fact(ans, vis)],
        {"visual_type": "table", "source_id": "ILO2021-PLATFORM", "visual_id": tid, "visual_title": title,
         "pdf_page": page, "printed_page": printed, "requires_visual_reading": True, "why": relation})

if len(specs) != NEW_COUNT:
    raise SystemExit(f"Expected {NEW_COUNT} new QA specs, got {len(specs)}")
counts = Counter((spec["question_type"], spec["split"]) for spec in specs)
expected_categories = {"unanswerable_absence", "cross_document_synthesis", "table_chart_reasoning"}
if {kind for kind, _ in counts} != expected_categories:
    raise SystemExit(f"Question type mismatch: {counts}")
for kind in expected_categories:
    if counts[(kind, "TRAIN")] != 14 or counts[(kind, "DEV")] != 3 or counts[(kind, "TEST")] != 3:
        raise SystemExit(f"Unexpected type/split matrix: {counts}")


def source_ref_for(sid):
    if sid in source_ref_by_id:
        return copy.deepcopy(source_ref_by_id[sid])
    src = source_by_id[sid]
    return {
        "source_id": sid,
        "publisher": src["publisher"],
        "title": src["title_chinese"],
        "title_english": src["title_english"],
        "text_language": src["text_language"],
        "translation_status": src["translation_status"],
        "official_pdf_url": src["original_report_url"],
        "official_publication_page_url": src["official_publication_page_url"],
        "source_pdf_sha256": src["original_report_sha256"],
        "pdf_page_count": src["source_pdf_page_count"],
        "rights_holder": src["rights_holder"],
        "license": src["license"],
        "license_id": src["license_id"],
        "license_url": src["license_url"],
        "rights_notice_location": copy.deepcopy(src["rights_notice_location"]),
        "required_source_attribution_short_form": src["required_attribution"],
        "required_adaptation_disclaimer": src["required_adaptation_disclaimer"],
        "translation_disclaimer": src["translation_disclaimer"],
        "third_party_content_limitations": src["third_party_content_limitations"],
        "source_pdf_included": False,
    }


def row_license(sids):
    licenses = {source_by_id[sid]["license_id"] for sid in sids}
    if len(licenses) != 1:
        raise SystemExit(f"Cannot share one record license across mixed source licenses: {sids} {licenses}")
    license_id = next(iter(licenses))
    license_name, license_url = LICENSES[license_id]
    if any(source_by_id[sid]["license_url"] != license_url for sid in sids):
        raise SystemExit(f"Inconsistent source license URL for {sids}")
    obligations = []
    for sid in sids:
        src = source_by_id[sid]
        obligations.append({
            "source_id": sid,
            "source_license": src["license"],
            "license_url": src["license_url"],
            "required_attribution": src["required_attribution"],
            "required_adaptation_disclaimer": src["required_adaptation_disclaimer"],
            "translation_disclaimer": src.get("translation_disclaimer"),
            "third_party_content_limitations": src["third_party_content_limitations"],
            "sharealike_applies_to_adapted_record": license_id == "CC-BY-SA-3.0-IGO",
        })
    return {
        "dataset_license": license_id,
        "record_license": license_id,
        "license_url": license_url,
        "license_name": license_name,
        "license_scope": "This record and its adapted QA metadata only. The repository is released under mixed record-level terms; no single license applies to every record.",
        "status": "licensed_under_" + license_id.replace("-", "_"),
        "rights_assessment_is_legal_opinion": False,
        "source_attribution_required": True,
        "required_source_attributions": [source_by_id[sid]["required_attribution"] for sid in sids],
        "required_adaptation_disclaimers": [source_by_id[sid]["required_adaptation_disclaimer"] for sid in sids],
        "translation_disclaimers": [source_by_id[sid].get("translation_disclaimer") for sid in sids if source_by_id[sid].get("translation_disclaimer")],
        "modification_notice": "Question, answer, required-fact summaries, and evidence locators are AI-assisted paraphrase/adaptation metadata. Original source text, PDFs, and media are not included.",
        "source_license_obligations": obligations,
        "third_party_content_reused": False,
        "source_excerpt_included": False,
        "source_media_included": False,
        "source_pdf_included": False,
        "source_pdf_redistribution": "not_included_in_package",
    }


def family_ids(sids):
    result = []
    for sid in sids:
        if sid not in family_by_id:
            family_by_id[sid] = "iicr-v12-family-" + sid.lower()
        if family_by_id[sid] not in result:
            result.append(family_by_id[sid])
    return result


new_rows = []
new_assignment_rows = []
question_seen = {row["question"] for row in old_records}
for offset, spec in enumerate(specs, start=1):
    qid = f"IICR-V12-{offset:04d}"
    question = spec["question"]
    if question in question_seen:
        raise SystemExit(f"Duplicate question: {qid}: {question}")
    question_seen.add(question)
    if spec["question_type"] == "unanswerable_absence":
        sids = list(spec["source_ids"])
    else:
        sids = []
        for f in spec["facts"]:
            sid = f["locator"]["source_id"]
            if sid not in sids:
                sids.append(sid)
    fams = family_ids(sids)
    component = "iicr-v12-group-" + "--".join(sorted(sid.lower() for sid in sids))
    facts = []
    for index, fact_spec in enumerate(spec["facts"], start=1):
        fact_id = f"{qid}-F{index}"
        facts.append({"fact_id": fact_id, "statement": fact_spec["statement"]})
    if facts:
        locators = []
        for fact_id, fact_spec in zip((f["fact_id"] for f in facts), spec["facts"]):
            loc = copy.deepcopy(fact_spec["locator"])
            loc["supports_fact_ids"] = [fact_id]
            locators.append(loc)
        evidence = [{
            "evidence_set_id": f"{qid}-E1",
            "equivalent_group_id": f"{qid}-EQ1",
            "page_reference_scheme": "1-based physical PDF page; printed page is separate when verified",
            "required_fact_ids": [f["fact_id"] for f in facts],
            "sources": locators,
        }]
        fact_reviews = []
        for f, spec_fact in zip(facts, spec["facts"]):
            fact_reviews.append({
                "fact_id": f["fact_id"],
                "cited_element_ids": [spec_fact["locator"]["element_id"]],
                "review_status": "supported_by_source_page_and_locator",
            })
    else:
        evidence = []
        fact_reviews = []
    rights = row_license(sids)
    quality = {
        "source_support_status": "source_checked_unanswerable_candidate" if not facts else "source_verified_candidate",
        "human_reviewed": False,
        "independent_human_double_annotation": "not_performed",
        "heldout_gold_accessed": False,
        "source_review_provenance": {
            "reviewer": "AI-assisted source and evidence verification",
            "review_type": "page-level verification for v1.2.0 candidates; PDF locator and task-specific evidence checked",
            "reviewed_on": REVIEW_DATE,
            "source_text_written_to_package": False,
        },
        "required_facts_review": fact_reviews,
        "semantic_review_status_in_ledger": "ai_assisted_candidate",
        "reviewed_on": REVIEW_DATE,
    }
    row = {
        "schema_version": "iicr_report_qa_v1_2",
        "annotation_version": "iicr-ai-assisted-candidate-v1.2",
        "query_id": qid,
        "gold_candidate": True,
        "question": question,
        "answerability": "unanswerable" if not facts else "answerable",
        "gold_answer": spec["gold_answer"],
        "required_facts": facts,
        "gold_evidence_sets": evidence,
        "gold_quality": quality,
        "publication_rights": rights,
        "source_ids": sids,
        "source": "; ".join(source_by_id[sid]["title_chinese"] for sid in sids),
        "source_refs": [source_ref_for(sid) for sid in sids],
        "domain_id": "MAIN_INTERNET_ICT",
        "document_id": "iicr-v12-" + "--".join(sid.lower() for sid in sids),
        "document_scope": sids,
        "family_id": fams[0] if len(fams) == 1 else "iicr-v12-cross-family-" + "--".join(sid.lower() for sid in sids),
        "family_ids": fams,
        "connected_group_id": component,
        "split": spec["split"],
        "split_assignment_version": "dataset_split_v1_2",
        "task_type": spec["question_type"],
        "modality_tags": ["text"] if spec["question_type"] != "table_chart_reasoning" else ["text", spec["visual_dependency"]["visual_type"]],
        "human_reviewed": False,
    }
    if "absence_verification" in spec:
        row["absence_verification"] = copy.deepcopy(spec["absence_verification"])
    if spec.get("visual_dependency"):
        row["visual_dependency"] = copy.deepcopy(spec["visual_dependency"])
    new_rows.append(row)
    new_assignment_rows.append({
        "query_id": qid,
        "split": spec["split"],
        "source_ids": sids,
        "family_ids": fams,
        "connected_group_id": component,
        "assignment_version": "dataset_split_v1_2",
    })

new_record_counts = Counter(row["split"] for row in new_rows)
new_source_counts = Counter(sid for row in new_rows for sid in row["source_ids"])
if dict(new_record_counts) != {"TRAIN": 42, "DEV": 9, "TEST": 9}:
    raise SystemExit(f"New split count mismatch: {dict(new_record_counts)}")

# Append only. The first 773 serialized records and assignments remain byte-identical.
with RECORDS.open("ab") as f:
    for row in new_rows:
        f.write((compact(row) + "\n").encode("utf-8"))
with ASSIGNMENTS.open("ab") as f:
    for row in new_assignment_rows:
        f.write((compact(row) + "\n").encode("utf-8"))

old_sources_doc["dataset_version"] = "1.2.0"
old_sources_doc["source_count"] = len(source_catalog)
old_sources_doc["sources"] = source_catalog
old_sources_doc["record_level_license_policy"] = (
    "Mixed record-level licensing. Every record identifies its record license, source license, attribution, adaptation/translation notices, and third-party limitations. "
    "No single license applies to the complete package; CC BY-SA 3.0 IGO adaptations are released under the same terms."
)
old_sources_doc["review_provenance"] = {
    "v1_1": "AI-assisted page-level source and evidence verification; independent human review not performed.",
    "v1_2": "AI-assisted page, table, figure, cross-document, and absence-scope verification; all new rows set human_reviewed=false; independent human review not performed.",
}
SOURCES.write_text(json.dumps(old_sources_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "appended_records": len(new_rows),
    "new_split_counts": dict(new_record_counts),
    "new_question_types": dict(Counter(row["task_type"] for row in new_rows)),
    "new_sources": [source["source_id"] for source in new_source_metadata],
    "new_source_record_counts": dict(new_source_counts),
    "records_sha256": digest(RECORDS),
    "assignments_sha256": digest(ASSIGNMENTS),
}, ensure_ascii=False, indent=2))
