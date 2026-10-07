#!/usr/bin/env python3
"""Build the v2.0.0 candidate package from the frozen v1.2.0 archive and source-grounded additions."""
from __future__ import annotations
import copy, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT / 'history' / 'v1.2.0'
OUT = ROOT

# This is the historical v2.0.0 builder. Once v2.1.0 is active it must not
# overwrite the unified release with an older corpus; use build_v2_1_package.py.
ACTIVE_RECORDS = OUT / 'records.jsonl'
if ACTIVE_RECORDS.exists() and b'"query_id":"IICR-V21-' in ACTIVE_RECORDS.read_bytes():
    raise SystemExit('Refusing to overwrite an active v2.1.0 package with the historical v2.0.0 builder. Use build_v2_1_package.py.')

# The family-to-split assignments were fixed before drafting the new questions.
FAMILIES = {
    'UNESCO-AI-EDU-POLICY-2021': ('v2-unesco-ai-education-policy-2021', 'TRAIN'),
    'UNESCO-GEM-TECH-2023-ZH-SUMMARY': ('v2-unesco-gem-technology-2023-summary', 'TRAIN'),
    'UNESCO-GENAI-GUIDANCE-2023-ZH': ('v2-unesco-genai-guidance-traditional-chinese', 'DEV'),
    'FAO-DIGITAL-AGRI-2019-ZH-BRIEF': ('v2-fao-digital-agriculture-2019-chinese-brief', 'TEST'),
}

PROMPT = (
    'Read the question and the cited Chinese source PDF only. Reconstruct a concise answer, '
    'atomic required facts, and physical 1-based PDF page locators without seeing any candidate answer. '
    'Use paraphrase; flag unsupported or ambiguous claims. This is an AI-assisted source reconstruction, '
    'not independent human annotation.'
)
PROMPT_SHA = hashlib.sha256(PROMPT.encode()).hexdigest()
MODEL = 'GPT-6 (Codex; exact deployment identifier not exposed)'
CLOZE_GENERATOR_PATH = ROOT / 'scripts' / 'generate_v2_cloze_candidates.py'
CLOZE_GENERATOR_SHA = hashlib.sha256(CLOZE_GENERATOR_PATH.read_bytes()).hexdigest()
REVIEW_DATE = '2026-10-07'

NEW_SOURCES = [
  {
    'source_id':'UNESCO-AI-EDU-POLICY-2021','publication_institution':'UNESCO','publisher':'联合国教育、科学及文化组织（UNESCO）',
    'publication_year':2021,'title_chinese':'《人工智能与教育：政策制定者指南》','title_english':'AI and education: Guidance for policy-makers',
    'text_language':'Chinese (Simplified)','document_type':'UNESCO Chinese edition of a policy guide',
    'translation_status':'UNESCO distributed a Chinese edition; this dataset uses the Chinese publication and does not translate the English original.',
    'original_report_url':'https://www.gcedclearinghouse.org/sites/default/files/resources/220221chi.pdf',
    'original_report_sha256':'c6f78640c8dc48613898d864289725cf24ceaefc4e282e8d51c84213d889bd25','source_pdf_page_count':51,
    'parent_report_url':'https://unesdoc.unesco.org/ark:/48223/pf0000376709','parent_report_sha256':None,
    'official_publication_page_url':'https://www.unesco.org/zh/digital-education/artificial-intelligence?hub=67076',
    'rights_holder':'UNESCO','license':'CC BY-SA 3.0 IGO','license_id':'CC-BY-SA-3.0-IGO','license_url':'https://creativecommons.org/licenses/by-sa/3.0/igo/',
    'rights_notice_location':{'document':'Chinese UNESCO PDF','pdf_page_1based':2,'url':'https://www.gcedclearinghouse.org/sites/default/files/resources/220221chi.pdf','pdf_page_count':51,'pdf_sha256':'c6f78640c8dc48613898d864289725cf24ceaefc4e282e8d51c84213d889bd25'},
    'required_attribution':'UNESCO. 2021. AI and education: Guidance for policy-makers (Chinese edition). Paris: UNESCO. CC BY-SA 3.0 IGO. https://www.gcedclearinghouse.org/sites/default/files/resources/220221chi.pdf',
    'required_adaptation_disclaimer':'本记录为对 UNESCO 出版物文本内容的改编摘要；改编责任由数据集发布者承担，不表示 UNESCO 认可。适用 CC BY-SA 3.0 IGO。',
    'translation_disclaimer':'使用 UNESCO 发布的中文版本；本数据集未自行翻译原报告。',
    'third_party_content_limitations':'许可页说明许可仅适用于文本；本记录仅概述叙述性文本，不复用图像、表格、图表或未明确归属 UNESCO 的第三方材料。',
    'source_pdf_included':False,'edition_note':'以 PDF 物理页码定位；不包含原 PDF 或原文长段。','source_file_audit_status':'sha256_verified_local_pdf_and_license_page'
  },
  {
    'source_id':'UNESCO-GEM-TECH-2023-ZH-SUMMARY','publication_institution':'UNESCO Global Education Monitoring Report Team','publisher':'联合国教科文组织全球教育监测报告团队（UNESCO GEM Report Team）',
    'publication_year':2023,'title_chinese':'《2023年全球教育监测报告》摘要：技术运用于教育：谁来做主？','title_english':'Global Education Monitoring Report Summary 2023: Technology in education: A tool on whose terms?',
    'text_language':'Chinese (Simplified)','document_type':'UNESCO official Chinese summary',
    'translation_status':'A Chinese-language summary is listed in the UNESCO Global Citizenship Education Clearinghouse and on the UNESCO GEM report site; no translation by this dataset.',
    'original_report_url':'https://www.gcedclearinghouse.org/sites/default/files/resources/230014chi.pdf',
    'original_report_sha256':'af522ed13f253cd740783f06f415deef30c4fe36bbf1110b7699ad6a87cc47b2','source_pdf_page_count':32,
    'parent_report_url':'https://www.unesco.org/gem-report/zh/publication/technology','parent_report_sha256':None,
    'official_publication_page_url':'https://www.unesco.org/gem-report/zh/publication/technology',
    'rights_holder':'UNESCO','license':'CC BY-SA 3.0 IGO','license_id':'CC-BY-SA-3.0-IGO','license_url':'https://creativecommons.org/licenses/by-sa/3.0/igo/',
    'rights_notice_location':{'document':'Chinese summary PDF','pdf_page_1based':4,'url':'https://www.gcedclearinghouse.org/sites/default/files/resources/230014chi.pdf','pdf_page_count':32,'pdf_sha256':'af522ed13f253cd740783f06f415deef30c4fe36bbf1110b7699ad6a87cc47b2'},
    'required_attribution':'UNESCO. 2023. Global Education Monitoring Report Summary 2023: Technology in education: A tool on whose terms? Chinese summary. Paris: UNESCO. CC BY-SA 3.0 IGO. https://www.gcedclearinghouse.org/sites/default/files/resources/230014chi.pdf',
    'required_adaptation_disclaimer':'本记录为对 UNESCO 出版物文本内容的改编摘要；改编责任由数据集发布者承担，不表示 UNESCO 认可。适用 CC BY-SA 3.0 IGO。',
    'translation_disclaimer':'使用 UNESCO 发布的中文摘要；本数据集未自行翻译原报告。',
    'third_party_content_limitations':'许可页说明许可仅适用于文本；本记录仅概述叙述性文本，不复用照片、图表、表格或第三方内容。',
    'source_pdf_included':False,'edition_note':'来源是32页中文摘要，而非526页完整报告；使用物理PDF页码。','source_file_audit_status':'sha256_verified_local_pdf_and_license_page'
  },
  {
    'source_id':'UNESCO-GENAI-GUIDANCE-2023-ZH','publication_institution':'Taiwan Academic Research Ethics Education Center (Ministry of Education, Taiwan)','publisher':'教育部臺灣學術倫理教育資源中心（AREE）',
    'publication_year':2023,'title_chinese':'《教育與研究之生成式人工智慧應用指引》','title_english':'Guidance for generative AI in education and research',
    'text_language':'Chinese (Traditional)','document_type':'Traditional Chinese translation prepared by AREE of the UNESCO 2023 guide',
    'translation_status':'AREE identifies UNESCO as the original author and itself as the Traditional Chinese translation/preparation center; the English original controls where the translation differs. This is not described as an official UNESCO Chinese edition.',
    'original_report_url':'https://ethics.moe.edu.tw/files/resource/ebook/file/ebook_04.pdf',
    'original_report_sha256':'bf155d250a3120ded78b894742e41857e1efd9c9e4d71b4b53d818cef622817b','source_pdf_page_count':67,
    'parent_report_url':'https://unesdoc.unesco.org/ark:/48223/pf0000386693','parent_report_sha256':None,
    'official_publication_page_url':'https://announce.yzu.edu.tw/index.php/tw/rd/rd-202512160911-03',
    'rights_holder':'UNESCO (original text); Taiwan Academic Research Ethics Education Center (Traditional Chinese translation)',
    'license':'CC BY-SA 3.0 IGO','license_id':'CC-BY-SA-3.0-IGO','license_url':'https://creativecommons.org/licenses/by-sa/3.0/igo/',
    'rights_notice_location':{'document':'AREE Traditional Chinese PDF','pdf_page_1based':2,'url':'https://ethics.moe.edu.tw/files/resource/ebook/file/ebook_04.pdf','pdf_page_count':67,'pdf_sha256':'bf155d250a3120ded78b894742e41857e1efd9c9e4d71b4b53d818cef622817b'},
    'required_attribution':'UNESCO. 2023. Guidance for generative AI in education and research. Traditional Chinese translation prepared by Taiwan Academic Research Ethics Education Center (AREE), Ministry of Education, Taiwan. CC BY-SA 3.0 IGO. https://ethics.moe.edu.tw/files/resource/ebook/file/ebook_04.pdf',
    'required_adaptation_disclaimer':'本记录改编自 UNESCO 原文及 AREE 繁体中文译本；改编责任由数据集发布者承担，不表示 UNESCO 或 AREE 认可。适用 CC BY-SA 3.0 IGO。',
    'translation_disclaimer':'AREE 制作的繁体中文版本；英文原文为准。署名 UNESCO 原作者及 AREE 译制机构。',
    'third_party_content_limitations':'只概述文本内容，不复用图像、表格、插图或第三方材料。',
    'source_pdf_included':False,'edition_note':'来源为AREE正式提供的繁体中文译本；使用物理PDF页码。','source_file_audit_status':'sha256_verified_local_pdf_license_and_translation_notice'
  },
  {
    'source_id':'FAO-DIGITAL-AGRI-2019-ZH-BRIEF','publication_institution':'Food and Agriculture Organization of the United Nations (FAO)','publisher':'联合国粮食及农业组织（FAO）',
    'publication_year':2019,'title_chinese':'《农业和农村地区数字技术：摘要文件》','title_english':'Digital technologies in agriculture and rural areas: Briefing paper',
    'text_language':'Chinese (Simplified)','document_type':'FAO Chinese-language briefing paper summarizing the status report',
    'translation_status':'FAO lists the Chinese briefing paper among the report-language downloads; this dataset does not translate the English report.',
    'original_report_url':'https://www.fao.org/3/ca4887zh/ca4887zh.pdf',
    'original_report_sha256':'54abd0d5ba6e647256cbff9d2ef8981bcc0fadcbd56590f1a36eec5d8e774f9f','source_pdf_page_count':26,
    'parent_report_url':'https://www.fao.org/3/ca4985en/ca4985en.pdf','parent_report_sha256':None,
    'official_publication_page_url':'https://www.fao.org/e-agriculture/news/read-digital-technologies-agriculture-and-rural-areas-report',
    'rights_holder':'Food and Agriculture Organization of the United Nations','license':'CC BY-NC-SA 3.0 IGO','license_id':'CC-BY-NC-SA-3.0-IGO','license_url':'https://creativecommons.org/licenses/by-nc-sa/3.0/igo/',
    'rights_notice_location':{'document':'Chinese briefing PDF','pdf_page_1based':26,'url':'https://www.fao.org/3/ca4887zh/ca4887zh.pdf','pdf_page_count':26,'pdf_sha256':'54abd0d5ba6e647256cbff9d2ef8981bcc0fadcbd56590f1a36eec5d8e774f9f'},
    'required_attribution':'Trendov, N. M., Varas, S. & Zeng, M. 2019. Digital technologies in agriculture and rural areas – Status report. Chinese briefing paper: 农业和农村地区数字技术：摘要文件. Rome: FAO. CC BY-NC-SA 3.0 IGO. https://www.fao.org/3/ca4887zh/ca4887zh.pdf',
    'required_adaptation_disclaimer':'本记录改编自 FAO 出版物文本内容；改编责任由数据集发布者承担，不表示 FAO 认可。适用 CC BY-NC-SA 3.0 IGO，非商业使用并按相同方式共享。',
    'translation_disclaimer':'使用 FAO 发布的中文摘要文件；本数据集未自行翻译原报告。',
    'third_party_content_limitations':'报告含第三方图片和内容；本记录仅概述叙述性事实，不复用图表、图像、地图、表格或第三方材料。',
    'source_pdf_included':False,'edition_note':'来源是26页中文摘要文件，不是完整英文状态报告；使用物理PDF页码。','source_file_audit_status':'sha256_verified_local_pdf_and_license_page'
  }
]

# The additional 32 source records and source-sentence cloze candidates are kept in
# audit inputs so this builder remains deterministic without bundling any source PDFs.
EXPANSION_SOURCE_DOC = json.loads((ROOT / 'audit' / 'v2_expansion_sources.json').read_text(encoding='utf-8'))
EXPANSION_SOURCES = EXPANSION_SOURCE_DOC['sources']
FAMILIES.update({s['source_id']: (s['source_family_id'], s['preassigned_split']) for s in EXPANSION_SOURCES})
NEW_SOURCES.extend(copy.deepcopy(EXPANSION_SOURCES))

# Each fact entry carries a short paraphrase of the corresponding page region. The region IDs are
# stable page locators; no source passage or source media is included in the package.
Q = []
def add(src, split, q, a, facts, family=None, group=None, task='single_document_retrieval', subtype='fact_lookup'):
    sids = src if isinstance(src, list) else [src]
    family_ids = [FAMILIES[s][0] for s in sids]
    expected = {FAMILIES[s][1] for s in sids}
    if len(expected) != 1 or split not in expected:
        raise ValueError(f'Family split mismatch: {sids} -> {split}')
    Q.append({'source_ids':sids,'split':split,'family_ids':family_ids,'connected_group_id':group or ('v20-'+re.sub(r'[^a-z0-9]+','-', '-'.join(s.lower() for s in sids)).strip('-')),
              'task_family':task,'task_subtype':subtype,'question':q,'answer':a,'facts':facts})

A='UNESCO-AI-EDU-POLICY-2021'; G='UNESCO-GEM-TECH-2023-ZH-SUMMARY'; T='UNESCO-GENAI-GUIDANCE-2023-ZH'; F='FAO-DIGITAL-AGRI-2019-ZH-BRIEF'

# UNESCO 2021 AI policy guide: 18 questions (TRAIN)
add(A,'TRAIN','指南提到，“人工智能”一词在1956年达特茅斯研讨会上用于描述什么？','它用于描述打造智能机器（尤其是智能计算机程序）的科学与工程。',[{'page':9,'fact':'1956年达特茅斯研讨会以“人工智能”描述制造智能机器、尤其是智能计算机程序的科学与工程。'}],subtype='historical_definition')
add(A,'TRAIN','指南转述的 COMEST 描述中，机器模仿的人类智能功能包括哪些方面？','包括感知、学习、推理、解决问题、语言互动和创造性工作。',[{'page':9,'fact':'COMEST所述人工智能功能涵盖感知、学习、推理、解决问题、语言互动及创造性工作。'}],subtype='definition_component_list')
add(A,'TRAIN','指南引用 IBM 的估算，互联网相关技术每天会产生多少新数据？','超过2.5万亿字节。',[{'page':9,'fact':'指南引用IBM估算，互联网及相关技术每天产生超过2.5万亿字节数据。'}],task='quantitative_retrieval',subtype='approximate_numeric_fact')
add(A,'TRAIN','指南将机器学习分为哪三种主要方法？','有监督学习、无监督学习和强化学习。',[{'page':11,'fact':'指南列出有监督学习、无监督学习与强化学习三种主要机器学习方法。'}],subtype='category_list')
add(A,'TRAIN','根据指南，有监督学习如何利用训练数据形成模型？','它使用带有人为标注的数据，将数据与标签关联起来，形成可用于类似新数据的模型。',[{'page':11,'fact':'有监督学习把已有标记数据与标签关联，用于构建可处理类似新数据的模型。'}],task='within_document_synthesis',subtype='mechanism_explanation')
add(A,'TRAIN','指南所说的无监督学习，主要在没有标签的数据中寻找什么？','它寻找隐藏模式或可用于归类新数据的簇。',[{'page':11,'fact':'无监督学习从未分类或未标记的数据中发现隐藏模式，并可形成数据簇。'}],task='within_document_synthesis',subtype='mechanism_explanation')
add(A,'TRAIN','指南如何概括强化学习与前两种机器学习方法的差别？','强化学习会依据反馈持续调整行为或决策；有监督和无监督学习则分别从标记数据或未标记数据中学习。',[{'page':11,'fact':'指南将有监督与无监督学习分别联系到标记与未标记数据；强化学习通过反馈调整行为。'}],task='within_document_synthesis',subtype='method_comparison')
add(A,'TRAIN','指南列出的人工神经网络通常包含哪三类层？','输入层、一个或多个隐藏的中间计算层，以及输出层。',[{'page':12,'fact':'人工神经网络由输入层、一个或多个隐藏中间层和输出层组成。'}],subtype='architecture_components')
add(A,'TRAIN','指南用 AlphaGo 举例时，记录了它在何年击败李世石？','2016年。',[{'page':12,'fact':'指南记载 AlphaGo 于2016年击败世界围棋冠军李世石。'}],task='quantitative_retrieval',subtype='year_lookup')
add(A,'TRAIN','指南所说的“弱人工智能”与通用或“强人工智能”在任务范围上有什么区别？','弱人工智能面向受约束的专门领域，不能直接迁移到其他领域；强人工智能则指通用能力设想。',[{'page':13,'fact':'指南把现有应用归为范围受限的专用人工智能，并将通用人工智能作为强人工智能概念讨论。'}],task='within_document_synthesis',subtype='concept_comparison')
add(A,'TRAIN','指南用哪两个例子说明专用人工智能不能自动迁移到其他领域？','天气预报人工智能不能因此预测股市波动；驾驶汽车的人工智能不能因此诊断肿瘤。',[{'page':13,'fact':'指南举例指出天气人工智能不能据此预测股市，汽车驾驶人工智能不能据此诊断肿瘤。'}],subtype='example_pair')
add(A,'TRAIN','指南在引言中预计，2024年人工智能教育应用市场规模会达到多少？','预计达到60亿美元。',[{'page':8,'fact':'引言引用预测称人工智能教育应用市场到2024年预计达到60亿美元。'}],task='quantitative_retrieval',subtype='forecast_lookup')
add(A,'TRAIN','指南把人工智能在教育领域的早期应用研究追溯到哪个年代？','20世纪70年代。',[{'page':16,'fact':'指南将人工智能在教育领域的应用追溯至20世纪70年代。'}],task='quantitative_retrieval',subtype='period_lookup')
add(A,'TRAIN','指南用哪三种说法概括人工智能与教育的不同互动方向？','使用人工智能来学习、学习人工智能本身，以及为与人工智能协作而学习。',[{'page':16,'fact':'指南区分使用人工智能学习、学习人工智能知识以及为人机协同而学习。'}],task='within_document_synthesis',subtype='framework_components')
add(A,'TRAIN','指南按受益对象把教育人工智能应用分为哪三类？','面向学生的学习与测评支持、面向教师的授课支持，以及面向系统的教育机构管理支持。',[{'page':16,'fact':'指南区分面向学生、面向教师和面向教育系统的人工智能应用。'}],task='within_document_synthesis',subtype='category_list')
add(A,'TRAIN','指南列举的教育管理信息系统相关任务有哪些？','包括招生、排课、考勤、作业监测和校务监管等行政任务。',[{'page':17,'fact':'系统层面的教育人工智能可用于招生、排课、考勤、作业监测和校务监管等。'}],subtype='application_list')
add(A,'TRAIN','指南如何描述智能导学系统在教育人工智能中的研究历史和使用情况？','它们已有超过40年的研究历史，是教育领域较常见的人工智能应用之一，服务的学生人数也很多。',[{'page':18,'fact':'指南称智能导学系统研究历史超过40年，是常见教育人工智能应用且面向大量学生。'}],task='within_document_synthesis',subtype='historical_and_scope_summary')
add(A,'TRAIN','指南比较人和计算机的优势时，列出哪些任务更依赖人的能力？','同理心、自我指导、常识和价值判断等任务更依赖人的能力；计算机更擅长基于数据、规律识别和统计推理的任务。',[{'page':26,'fact':'指南将同理心、自我指导、常识与价值判断列为人类优势，并将数据、模式识别和统计推理列为计算机优势。'}],task='within_document_synthesis',subtype='capability_comparison')

# UNESCO 2023 GEM Chinese summary: 18 questions (TRAIN)
add(G,'TRAIN','报告估计，疫情期间的远程学习未能覆盖多少学生？占全球学生的比例及最贫困学生的比例分别是多少？','至少5亿名学生未被覆盖，约占全球学生的31%；最贫困学生中有72%未被覆盖。',[{'page':5,'fact':'远程学习未覆盖至少5亿名学生（全球学生的31%）以及72%的最贫困学生。'}],task='quantitative_retrieval',subtype='multi_metric_fact')
add(G,'TRAIN','报告给出的全球学校互联网接入率，小学、初中和高中分别是多少？','小学40%、初中50%、高中65%。',[{'page':5,'fact':'报告列出互联网接入率：小学40%、初中50%、高中65%。'}],task='quantitative_retrieval',subtype='stage_comparison')
add(G,'TRAIN','报告称，有多少国家制定了改善学校或学生连通性的政策？','85%的国家。',[{'page':5,'fact':'报告称85%的国家有改善学校或学生连通性的政策。'}],task='quantitative_retrieval',subtype='percentage_lookup')
add(G,'TRAIN','报告中的中国案例向农村学生提供录播课程后，学生成绩和城乡收入差距分别出现了什么变化？','向1亿名农村学生提供高质量录播课程后，学生成绩提高32%，城乡收入差距缩小38%。',[{'page':5,'fact':'中国案例记录向1亿名农村学生提供高质量录播课程，学生成绩提高32%，城乡收入差距缩小38%。'}],task='within_document_synthesis',subtype='case_outcome_pair')
add(G,'TRAIN','报告称英国教育技术公司中，进行随机对照试验和使用第三方认证的比例各是多少？','分别为7%和12%。',[{'page':5,'fact':'英国教育技术公司中，7%进行随机对照试验，12%使用第三方认证。'}],task='quantitative_retrieval',subtype='paired_percentage')
add(G,'TRAIN','报告称有数字技能标准的国家占多少？这些标准通常由谁定义？','54%的国家有数字技能标准；报告称这些标准通常由非国家行为体、主要是商业行为体定义。',[{'page':6,'fact':'全球54%的国家有数字技能标准，标准通常由非国家行为体（主要是商业行为体）定义。'}],task='within_document_synthesis',subtype='percentage_and_qualifier')
add(G,'TRAIN','报告给出的2021年大规模开放在线课程参与人数至少是多少？','至少2.2亿名学生。',[{'page':6,'fact':'2021年参加大规模开放在线课程的学生超过2.2亿名。'}],task='quantitative_retrieval',subtype='approximate_count')
add(G,'TRAIN','报告如何描述开放教育资源的地域和语言分布？','相关高等教育资源库近90%的内容由欧洲和北美创建；OER Commons全球图书馆92%的内容为英文。',[{'page':6,'fact':'近90%的开放教育资源库内容来自欧洲和北美；OER Commons全球图书馆92%的内容为英文。'}],task='quantitative_retrieval',subtype='distribution_comparison')
add(G,'TRAIN','报告称，明确通过法律保障教育数据隐私以及出台相关政策的国家比例分别是多少？','分别是16%和29%。',[{'page':17,'fact':'只有16%的国家通过法律明确保障教育数据隐私，29%的国家有相关政策。'}],task='quantitative_retrieval',subtype='paired_percentage')
add(G,'TRAIN','报告中，负责教育技术的部门或机构覆盖率与由教育部负责相关战略的比例分别是多少？','82%的国家指定了负责教育技术的部门或机构；58%的国家由教育部负责战略和计划。',[{'page':17,'fact':'82%的国家指定教育技术部门或机构，58%的国家让教育部负责教育技术战略与计划。'}],task='quantitative_retrieval',subtype='governance_percentage_pair')
add(G,'TRAIN','2022年美国教育部门领导者中，有多少人表示自己定期参与技术规划和战略讨论？','41%。',[{'page':17,'fact':'2022年，41%的美国教育部门领导者表示定期参与技术规划和战略讨论。'}],task='quantitative_retrieval',subtype='percentage_lookup')
add(G,'TRAIN','疫情期间推荐给儿童学习的163种教育技术产品中，有多大比例可以或确实在课外监视儿童？','89%。',[{'page':17,'fact':'分析发现，在疫情期间推荐的163种教育技术产品中，89%可以或确实在教育环境之外监视儿童。'}],task='quantitative_retrieval',subtype='privacy_risk_percentage')
add(G,'TRAIN','报告调查的五个国家中，3至8岁儿童在疫情期间的屏幕接触时间增加了多少？','教育和休闲用途的屏幕接触时间都增加了50分钟。',[{'page':17,'fact':'澳大利亚、中国、意大利、瑞典和美国的家长调查显示，3至8岁儿童屏幕接触时间增加50分钟。'}],task='quantitative_retrieval',subtype='time_delta')
add(G,'TRAIN','中国报告为数字设备作为教学工具设置了什么时间上限？','不超过总教学时间的30%。',[{'page':17,'fact':'中国教育部将数字设备作为教学工具的使用限制为总教学时间的30%。'}],task='quantitative_retrieval',subtype='policy_threshold')
add(G,'TRAIN','TALIS调查覆盖的48个教育系统中，年长教师在什么方面相对较弱？','他们使用信息通信技术的技能较弱，自我效能感也较低。',[{'page':18,'fact':'TALIS 2018发现，48个教育系统的年长教师ICT技能较弱且自我效能感较低。'}],task='within_document_synthesis',subtype='survey_finding')
add(G,'TRAIN','报告中，初中教师表示培训后已准备好用技术教学、以及对用技术测评缺乏信心的比例各是多少？','43%的初中教师表示培训后已准备好用技术教学；78%的教师对用技术进行测评没有信心。',[{'page':18,'fact':'TALIS中43%的初中教师称培训后已准备好用技术教学；ICILS中78%的教师对技术测评缺乏信心。'}],task='quantitative_retrieval',subtype='paired_teacher_percentages')
add(G,'TRAIN','报告称，2016至2018年STEM高等教育毕业生中女性占多少？','35%。',[{'page':18,'fact':'2016至2018年，STEM高等教育毕业生中女性占35%。'}],task='quantitative_retrieval',subtype='demographic_percentage')
add(G,'TRAIN','报告建议政府评估教育技术时采用哪四项判断标准？','适当、公平、有证据支持、可持续。',[{'page':20,'fact':'报告建议在教育领域采用技术前，评估其适当性、公平性、证据基础和可持续性。'}],task='within_document_synthesis',subtype='decision_criteria')

# Six cross-document queries: both UNESCO families are pre-assigned to TRAIN.
add([A,G],'TRAIN','结合两份 UNESCO 文件，指南列出的三种“人工智能与教育”互动方向是什么？GEM报告列出的教育技术决策四项标准又是什么？','AI指南区分使用人工智能学习、学习人工智能本身、以及为人机协同而学习；GEM报告建议按适当、公平、有证据支持和可持续四项标准评估教育技术。',[{'page':16,'fact':'AI指南区分使用AI学习、学习AI知识和为人机协同而学习。'},{'page':20,'fact':'GEM报告给出适当、公平、有证据支持、可持续四项教育技术判断标准。'}],task='cross_document_synthesis',subtype='framework_pair')
add([A,G],'TRAIN','把两份报告的预测与评估信息放在一起看：AI教育应用市场的2024年预测规模是多少，GEM报告称教育技术产品平均多久更新一次？','AI教育应用市场的预测规模为60亿美元；教育技术产品平均每36个月更新换代。',[{'page':8,'fact':'AI政策指南引用对2024年AI教育应用市场达到60亿美元的预测。'},{'page':5,'fact':'GEM摘要称教育技术产品平均每36个月更新换代。'}],task='cross_document_synthesis',subtype='cross_report_numeric_pair')
add([A,G],'TRAIN','两份报告分别把人工智能教育应用和信息通信技术教育应用的历史追溯到何时？','AI政策指南将人工智能教育应用追溯到20世纪70年代；GEM摘要称自20世纪20年代无线电普及以来，ICT在教育中的应用已有约100年，而数字技术改变教育的潜力主要在过去40年显现。',[{'page':16,'fact':'AI政策指南将教育AI应用追溯到20世纪70年代。'},{'page':7,'fact':'GEM摘要称ICT教育应用约有100年历史，数字技术主要在过去40年具有改变教育的潜力。'}],task='cross_document_synthesis',subtype='cross_report_timeline_comparison')
add([A,G],'TRAIN','两份报告怎样界定教育技术与教师的关系：AI指南强调哪类能力互补，GEM报告建议技术对面对面师生互动发挥什么作用？','AI指南指出，人更擅长同理心、常识、自我指导和价值判断，计算机更擅长数据与统计任务；GEM报告建议数字技术补充而不是取代教师面对面互动。',[{'page':26,'fact':'AI指南区分人的社会认知与价值判断能力和计算机的数据与统计能力。'},{'page':20,'fact':'GEM报告建议数字技术作为教师面对面互动的补充，不应取代该互动。'}],task='cross_document_synthesis',subtype='cross_report_complementarity')
add([A,G],'TRAIN','AI政策指南按受益对象区分的三类教育AI应用是什么？GEM报告则把技术在教育中的作用概括为哪五个渠道？','AI指南列出面向学生、教师和教育系统的应用；GEM报告概括为教育投入、教学交付手段、技能、规划工具以及社会文化背景。',[{'page':16,'fact':'AI指南把教育AI应用分为面向学生、教师和系统的方向。'},{'page':21,'fact':'GEM报告将技术作用概括为投入、交付手段、技能、规划工具和社会文化背景。'}],task='cross_document_synthesis',subtype='cross_report_category_mapping')
add([A,G],'TRAIN','对照两份报告的证据讨论：AI指南提醒评估哪些方面的证据不足？GEM报告给出的英国教育技术公司随机对照试验和第三方认证比例是多少？','AI指南提醒人工智能教育效果的有力证据仍不足，并需要关注教学法与教师角色影响；GEM报告称英国仅7%的教育技术公司做过随机对照试验，12%使用第三方认证。',[{'page':18,'fact':'AI指南提醒AI教育应用效果证据有限，并提出教学法和教师角色等待评估问题。'},{'page':5,'fact':'GEM摘要报告英国7%的教育技术公司进行随机对照试验，12%采用第三方认证。'}],task='cross_document_synthesis',subtype='evidence_comparison')

# AREE Traditional Chinese translation of UNESCO generative-AI guidance: 9 questions (DEV)
add(T,'DEV','指引列出的生成式AI教育治理核心价值有哪些？','包括人类主体性、包容、公平、性别平等、语言与文化多样性，以及多元观点与表达自由。',[{'page':3,'fact':'指引将人类主体性、包容、公平、性别平等、语言文化多样性、多元观点和表达自由列为核心价值。'}],task='within_document_synthesis',subtype='values_list')
add(T,'DEV','指引建议政府监管生成式AI时优先采取哪两类用户保护措施？','强制保护数据隐私，并考虑设定使用年龄限制。',[{'page':3,'fact':'摘要建议政府要求数据隐私保护并考虑年龄限制。'}],task='within_document_synthesis',subtype='policy_measures')
add(T,'DEV','指引要求教育机构在引入生成式AI系统前核验哪些方面？','核验系统在伦理方面是否可接受，以及在教学方法上是否适合教育场景。',[{'page':3,'fact':'摘要要求教育机构核验生成式AI系统的伦理性与教学适切性。'}],task='within_document_synthesis',subtype='institutional_safeguard')
add(T,'DEV','指引提出生成式AI进入教育后，应取代人类智慧还是促使教育界重新思考知识与学习？','指引强调生成式AI不应取代人类智慧，而应促使人们重新思考知识和人类学习。',[{'page':8,'fact':'序言指出生成式AI不应取代人类智慧，而应促使重新思考知识和学习。'}],task='within_document_synthesis',subtype='principle_interpretation')
add(T,'DEV','指引列举生成式AI可模仿人类生成哪些类型的输出？','文本、图像、视频、音乐和软件代码。',[{'page':8,'fact':'指引列出生成式AI可生成文本、图像、视频、音乐及软件代码。'}],subtype='output_type_list')
add(T,'DEV','指引指出，文本GPT看似理解内容，但其输出为什么仍需批判性核验？','它主要依据训练数据中的语言模式生成文本，并不真正理解现实；因此输出可能不准确或包含错误。',[{'page':29,'fact':'指引指出GPT以训练文本中的模式生成内容，并不理解现实，可能生成不正确文本。'}],task='within_document_synthesis',subtype='limitation_explanation')
add(T,'DEV','指引把生成式AI的不透明性与训练数据偏差联系起来，指出了什么风险？','由于模型内部难以解释，训练数据中的偏差可能进入输出，并变得难以发现和纠正。',[{'page':27,'fact':'指引指出模型不透明会使训练数据偏差更难察觉和修正。'}],task='within_document_synthesis',subtype='risk_mechanism')
add(T,'DEV','指引担心生成式AI内容进入网络后会怎样影响后续模型？','若后续模型再用先前AI生成的材料训练，错误和偏见可能不断回流，形成递归污染。',[{'page':28,'fact':'指引指出后续GPT可能以先前GPT产出的网络文本为训练资料，造成错误与偏见反复传播。'}],task='within_document_synthesis',subtype='feedback_loop')
add(T,'DEV','指引列举了生成式AI图像和视频被滥用的哪些具体风险？','它们可被用于制造难辨真伪的深度伪造、散播假信息或仇恨内容，也可能未经同意合成他人面孔。',[{'page':30,'fact':'指引指出生成式AI可制作深度伪造并被用于假信息、仇恨内容及未经同意的人脸合成。'}],task='within_document_synthesis',subtype='misuse_examples')

# FAO Chinese briefing: 9 questions (TEST)
add(F,'TEST','FAO文件列出的数字农业转型基本条件有哪些？','可用性、连通性、可负担性、信息通信技术教育，以及支持性政策与计划。',[{'page':8,'fact':'文件将基本条件列为可用性、连通性、可负担性、ICT教育和支持数字战略的政策计划。'}],task='within_document_synthesis',subtype='enabling_conditions')
add(F,'TEST','FAO文件列出的数字农业转型支持因素有哪些？','使用互联网、手机和社交网络，具备数字技能，以及鼓励农业创业和创新的文化。',[{'page':13,'fact':'文件列出互联网、手机、社交网络使用，数字技能和农业创业创新文化等支持因素。'}],task='within_document_synthesis',subtype='enabling_conditions')
add(F,'TEST','文件称，在最不发达国家，互联网使用大约达到什么水平？','大约每七个人中有一人使用互联网。',[{'page':13,'fact':'文件引用ITU数据称，最不发达国家每七人中约一人使用互联网。'}],task='quantitative_retrieval',subtype='approximate_rate')
add(F,'TEST','肯尼亚的 M-Farm 应用通过提供什么信息帮助农民调整生产？','它提供农产品价格信息，帮助农民规划生产；文件举例称一些农民据此改变了种植模式。',[{'page':17,'fact':'M-Farm向农民提供价格信息，帮助规划生产；肯尼亚案例中农民据此改变种植模式。'}],task='within_document_synthesis',subtype='case_mechanism')
add(F,'TEST','FAO 的 EMA-i 系统用于什么目的？文件称它当时在哪些区域范围内已投入使用？','EMA-i用于实地动物卫生人员实时上报家畜疫病并提供早期预警；文件称当时已在非洲六个国家使用。',[{'page':17,'fact':'EMA-i支持实地人员高质量、实时报告家畜疫病并强化预警，已在非洲六国使用。'}],task='within_document_synthesis',subtype='system_function_and_scope')
add(F,'TEST','MyCrop 汇集哪些近实时信息来支持农民制定农场计划？','天气、土壤、病虫害和作物数据；它据此提供地理制图、作物安排和个体农场计划等支持。',[{'page':17,'fact':'MyCrop使用近实时天气、土壤、病虫害和作物数据提供地理制图、作物计划及农场管理支持。'}],task='within_document_synthesis',subtype='system_inputs_and_outputs')
add(F,'TEST','FAO文件举例说明，精准农业中的引导系统和无人机分别可降低哪些投入？','引导系统有助于节省种子、肥料和拖拉机燃料并减少田间作业时间；变量技术和无人机有助于减少用水、农药、劳动力和资源成本。',[{'page':18,'fact':'精准农业引导系统可节省种子、肥料、燃油与作业时间，变量技术和无人机可减少水、农药、劳动力和资源投入。'}],task='within_document_synthesis',subtype='technology_effect_comparison')
add(F,'TEST','文件指出，农业企业资源规划（ERP）软件可以贯通并精简哪些流程？','从采购、生产到分销的流程。',[{'page':18,'fact':'农业ERP软件可精简采购、生产和分销各环节。'}],subtype='process_scope')
add(F,'TEST','文件描述的农业人工智能监测方式如何帮助农民及早作出决策？','企业可用卫星或无人机数据扫描田地并跟踪生产周期；预测模型可帮助更早决策、提升资源利用效率，并支持全天候持续监测。',[{'page':18,'fact':'AI农业应用使用卫星或无人机记录扫描田地和监测生产周期，以预测模型支持早决策、资源效率和全天监测。'}],task='within_document_synthesis',subtype='monitoring_mechanism')

assert len(Q) == 60, len(Q)
EXPANSION_QAS = [json.loads(line) for line in (ROOT / 'audit' / 'v2_expansion_qas.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
for item in EXPANSION_QAS:
    # Candidate content is intentionally retained in the recommended subset at
    # the dataset owner's direction; its pending status remains explicit.
    add(item['source_ids'], item['split'], item['question'], item['answer'], item['facts'],
        task=item['task_family'], subtype=item['task_subtype'],
        family=item['family_ids'][0], group=item['connected_group_id'])
    Q[-1]['content_review_status'] = item['content_review_status']
    Q[-1]['generation_method'] = item['generation_method']
    Q[-1]['source_sentence_sha256'] = item['source_sentence_sha256']
assert len(Q) == 60 + len(EXPANSION_QAS), (len(Q), len(EXPANSION_QAS))

LICENSE_URLS = {
 'CC BY 3.0 IGO':'https://creativecommons.org/licenses/by/3.0/igo/',
 'CC BY 4.0':'https://creativecommons.org/licenses/by/4.0/',
 'CC BY-SA 3.0 IGO':'https://creativecommons.org/licenses/by-sa/3.0/igo/',
 'CC BY-NC-SA 3.0 IGO':'https://creativecommons.org/licenses/by-nc-sa/3.0/igo/',
}
def sha_bytes(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def row_sha(row): return sha_bytes(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def compact(obj): return json.dumps(obj,ensure_ascii=False,separators=(',',':'))
def read_jsonl(p): return [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
def write_jsonl(p, rows): p.parent.mkdir(parents=True,exist_ok=True); p.write_text('\n'.join(compact(x) for x in rows)+'\n',encoding='utf-8')

old_rows=read_jsonl(HISTORY/'records.jsonl')
old_assign=read_jsonl(HISTORY/'split_assignments.jsonl')
assert len(old_rows)==833 and len(old_assign)==833
# The v2 corpus is a union: retain every v1.2.0 record and append the new candidates.
historical_old=old_rows
historical_assign=old_assign
assert len(historical_old)==833
old_sources_doc=json.loads((HISTORY/'sources.json').read_text(encoding='utf-8'))
old_sources={s['source_id']:copy.deepcopy(s) for s in old_sources_doc['sources']}
new_source_map={s['source_id']:copy.deepcopy(s) for s in NEW_SOURCES}
needed_old_ids={sid for r in historical_old for sid in r.get('source_ids',[])}
for sid in needed_old_ids:
    assert sid in old_sources, sid
    src=old_sources[sid]
    if sid.startswith('CAICT-'):
        # The dataset owner confirmed reuse authorization for these legacy QA records.
        # Keep the prior record license distinct from any license on the source report.
        src['publication_institution']='CAICT'
        src['publication_year']=src.get('publication_year')
        src['title_chinese']=src.get('title')
        src['original_report_url']=src.get('official_pdf_url')
        src['original_report_sha256']=src.get('source_pdf_sha256')
        src['source_pdf_page_count']=src.get('pdf_page_count')
        src['required_attribution']=src.get('required_source_attribution_short_form')
        src['license']=None
        src['license_url']=None
        src['rights_notice_location']={'document':src.get('title'),'pdf_page_1based':src.get('copyright_notice',{}).get('page_1based'),
          'url':src.get('official_pdf_url'),'notice_summary':src.get('copyright_notice',{}).get('notice_summary')}
        src['record_reuse_authorization']={
          'status':'dataset_owner_confirmed_authorized',
          'basis':'The dataset owner confirmed authorization to redistribute these existing QA records.',
          'applies_to':'The historical question, answer, annotation and evidence-locator records under their prior CC-BY-4.0 dataset-record license.',
          'does_not_assert_source_report_license':True,
          'source_level_authorization_documents_independently_reaudited':False
        }
        src['v2_source_file_audit_status']='historical_registry_only'
    else:
        # Flag source-file revalidation explicitly; a prior file check is not current proof of access.
        status='pending_blind_second_pass'
        if sid in {'WB2014-RURAL','ADB2018-CITIES','ADB2023-YOUTH','ILO2026-LIFELONG-SKILLS','UNESCO2023-DIGITAL-CITIZENSHIP'}:
            status='pending_source_file_revalidation'
        src['v2_source_file_audit_status']=status
for src in NEW_SOURCES:
    # These hashes are from the exact local PDFs inspected for this release.
    src['source_file_sha256_verified']=True
    new_source_map[src['source_id']]['source_file_sha256_verified']=True

new_records=[]
question_only=[]
reconstruction_audit=[]
pending_content_audit=[]
for i,item in enumerate(Q,1):
    qid=f'IICR-V20-{i:04d}'
    pending_content_review=item.get('content_review_status')=='pending_ai_content_verification'
    fact_ids=[f'{qid}-F{j}' for j in range(1,len(item['facts'])+1)]
    evidence_sources=[]
    for fact_id,f in zip(fact_ids,item['facts']):
        # Cross-document items use one fact locator for each source; single-document items use one.
        sid=item['source_ids'][0] if len(item['source_ids'])==1 else None
        if sid is not None:
            evidence_sources.append({'source_id':sid,'element_id':f"{sid.lower()}-p{f['page']:04d}-source-sentence" if pending_content_review else f"{sid.lower()}-p{f['page']:04d}-narrative-region",'locator_type':'source_sentence_cloze' if pending_content_review else 'narrative_text_region','pdf_page':f['page'],'printed_page':None,'element_summary':f['fact'],'supports_fact_ids':[fact_id]})
    if len(item['source_ids'])>1:
        for sid,f,fact_id in zip(item['source_ids'],item['facts'],fact_ids):
            evidence_sources.append({'source_id':sid,'element_id':f"{sid.lower()}-p{f['page']:04d}-source-sentence" if pending_content_review else f"{sid.lower()}-p{f['page']:04d}-narrative-region",'locator_type':'source_sentence_cloze' if pending_content_review else 'narrative_text_region','pdf_page':f['page'],'printed_page':None,'element_summary':f['fact'],'supports_fact_ids':[fact_id]})
    else:
        evidence_sources=[{'source_id':item['source_ids'][0],'element_id':f"{item['source_ids'][0].lower()}-p{f['page']:04d}-source-sentence" if pending_content_review else f"{item['source_ids'][0].lower()}-p{f['page']:04d}-narrative-region",'locator_type':'source_sentence_cloze' if pending_content_review else 'narrative_text_region','pdf_page':f['page'],'printed_page':None,'element_summary':f['fact'],'supports_fact_ids':[fid]} for f,fid in zip(item['facts'],fact_ids)]
    pubs=[new_source_map[sid] for sid in item['source_ids']]
    licenses={s['license'] for s in pubs}
    if len(licenses)!=1: raise ValueError(f'Incompatible cross-doc license: {qid} {licenses}')
    lic=next(iter(licenses)); license_id=pubs[0]['license_id']; lic_url=pubs[0]['license_url']
    attributions=[s['required_attribution'] for s in pubs]
    disclaimers=[s['required_adaptation_disclaimer'] for s in pubs]
    translations=[s.get('translation_disclaimer') for s in pubs if s.get('translation_disclaimer')]
    obligations=[]
    for s in pubs:
        obligations.append({'source_id':s['source_id'],'source_license':s['license'],'license_url':s['license_url'],'required_attribution':s['required_attribution'],'required_adaptation_disclaimer':s['required_adaptation_disclaimer'],'translation_disclaimer':s.get('translation_disclaimer'),'third_party_content_limitations':s['third_party_content_limitations'],'sharealike_applies_to_adapted_record':'SA' in s['license']})
    source_refs=[]
    for s in pubs:
        source_refs.append({k:copy.deepcopy(s[k]) for k in ['source_id','publication_institution','publisher','publication_year','title_chinese','title_english','text_language','document_type','translation_status','original_report_url','original_report_sha256','source_pdf_page_count','rights_holder','license','license_id','license_url','rights_notice_location','required_attribution','required_adaptation_disclaimer','translation_disclaimer','third_party_content_limitations','source_pdf_included','edition_note'] if k in s})
    task_type=item['task_family']
    rec={
      'schema_version':'iicr_report_qa_v2_0','dataset_version':'2.0.0','annotation_version':'iicr-ai-assisted-candidate-v2.0',
      'query_id':qid,'gold_candidate':False,'question':item['question'],'answerability':'answerable','gold_answer':item['answer'],
      'required_facts':[{'fact_id':fid,'statement':f['fact']} for fid,f in zip(fact_ids,item['facts'])],
      'gold_evidence_sets':[{'evidence_set_id':f'{qid}-E1','equivalent_group_id':f'{qid}-EQ1','page_reference_scheme':'1-based physical PDF page; no printed page asserted unless separately verified','required_fact_ids':fact_ids,'sources':evidence_sources}],
      'gold_quality':{'source_support_status':'source_sentence_cloze_candidate_pending_content_review' if pending_content_review else 'ai_source_reconstructed_candidate','human_reviewed':False,'independent_human_double_annotation':'not_performed','heldout_gold_accessed':False,
        'source_review_provenance':{'reviewer':'rule-based source-sentence cloze generator','review_type':'licensed short-sentence cloze generation; content and locator not independently reconstructed','reviewed_on':None if pending_content_review else REVIEW_DATE,'source_text_written_to_package':True if pending_content_review else False,'candidate_answer_in_review_input':True if pending_content_review else False,'independent_reviewer':False},
        'required_facts_review':[{'fact_id':fid,'cited_element_ids':[next(x['element_id'] for x in evidence_sources if fid in x['supports_fact_ids'])],'review_status':'pending_source_content_verification' if pending_content_review else 'supported_by_source_page_and_locator'} for fid in fact_ids],
        'semantic_review_status_in_ledger':'pending_ai_content_verification' if pending_content_review else 'ai_answer_blind_reconstruction_match','reviewed_on':None if pending_content_review else REVIEW_DATE},
      'publication_rights':{'dataset_license':lic,'record_license':lic,'license_url':lic_url,'license_name':lic,'license_scope':'This record and adapted QA metadata only; no single license applies to the full mixed-license repository.','status':'licensed_record_level','rights_assessment_is_legal_opinion':False,'source_attribution_required':True,
        'required_source_attributions':attributions,'required_adaptation_disclaimers':disclaimers,'translation_disclaimers':translations,
        'modification_notice':'Source-reconstructed rows contain AI-assisted paraphrased metadata. Pending cloze candidates were created by deterministic masking of one short licensed source sentence; no long passage, PDF or media is included.',
        'source_license_obligations':obligations,'third_party_content_reused':None if pending_content_review else False,'third_party_content_review_status':'pending_attribution_screen' if pending_content_review else 'not_applicable_to_paraphrased_text','source_excerpt_included':pending_content_review,'source_media_included':False,'source_pdf_included':False,'source_pdf_redistribution':'not_included_in_package'},
      'source_ids':item['source_ids'],'source':'; '.join(s['title_chinese'] for s in pubs),**({'source_sentence_sha256':item['source_sentence_sha256']} if pending_content_review else {}),'source_refs':source_refs,
      'domain_id':'MAIN_INTERNET_ICT','document_id':item['family_ids'][0],'document_scope':item['source_ids'],'family_id':item['family_ids'][0],
      'family_ids':item['family_ids'],'connected_group_id':item['connected_group_id'],'split':item['split'],'split_assignment_version':'v2_source_families_preassigned_v1',
      'task_type':task_type,'task_family':item['task_family'],'task_subtype':item['task_subtype'],'modality_tags':['text'],'human_reviewed':False,
      'review_status':'pending_ai_content_verification' if pending_content_review else 'ai_answer_blind_reconstruction_match','review_provenance':{'reviewer':'rule-based source-sentence cloze generator' if pending_content_review else 'AI-assisted source reconstruction','model':None if pending_content_review else MODEL,'prompt':None if pending_content_review else PROMPT,'prompt_sha256':None if pending_content_review else PROMPT_SHA,'generation_method':'rule_based_sentence_masking' if pending_content_review else None,'generation_script':'scripts/generate_v2_cloze_candidates.py' if pending_content_review else None,'generation_script_sha256':CLOZE_GENERATOR_SHA if pending_content_review else None,'reviewed_on':None if pending_content_review else REVIEW_DATE,
         'source_files':[{'source_id':sid,'sha256':new_source_map[sid]['original_report_sha256']} for sid in item['source_ids']],
         'candidate_answer_in_review_input':True if pending_content_review else False,'reconstruction_conclusion':'pending_content_and_attribution_review' if pending_content_review else 'match_supported_by_cited_source_pages','independent_reviewer':False,
         'method_limit':'No per-record LLM inference was performed. A deterministic script masked a value or clause in a licensed short source sentence. Content, ambiguity, and third-party attribution have not been independently reviewed.' if pending_content_review else 'The same active AI session created and checked the items; answer-blind input was used, but independent reviewer or separate-session blindness is not claimed.'},
      'recommended_for_evaluation':True,'recommendation_status':'included per dataset-owner instruction; source content review pending; not gold or human reviewed' if pending_content_review else 'AI-assisted source-reconstructed candidate; not gold; no independent human review','supersedes_query_id':None,
      'split_provenance':{'assignment_version':'v2_source_families_preassigned_v1','assignment_timing':'source_family_assigned_before_question_drafting','split':'v2_source_family_preassignment','pre_annotation_split':True},
      'lineage':{'v2_annotation':'new_record','supersedes_query_id':None}
    }
    new_records.append(rec)
    question_only.append({'query_id':qid,'question':item['question'],'source_ids':item['source_ids'],'assigned_split':item['split'],'family_ids':item['family_ids'],'question_type':item['task_family'],'task_subtype':item['task_subtype']})
    if pending_content_review:
        pending_content_audit.append({'query_id':qid,'question':item['question'],'source_ids':item['source_ids'],'source_pdf_sha256':[new_source_map[sid]['original_report_sha256'] for sid in item['source_ids']],
          'source_sentence_sha256':item['source_sentence_sha256'],'evidence_page':item['facts'][0]['page'],'content_review_status':'pending_ai_content_verification',
          'generation_method':item['generation_method'],'answer_blind_reconstruction_performed':False,'recommended_for_evaluation':True,'human_reviewed':False})
    else:
        reconstruction_audit.append({'query_id':qid,'question':item['question'],'source_ids':item['source_ids'],'source_pdf_sha256':[new_source_map[sid]['original_report_sha256'] for sid in item['source_ids']],
           'reconstructed_answer':item['answer'],'reconstructed_required_facts':[{'fact_id':fid,'statement':f['fact']} for fid,f in zip(fact_ids,item['facts'])],
           'reconstructed_evidence':[{'source_id':x['source_id'],'pdf_page':x['pdf_page'],'element_id':x['element_id'],'supports_fact_ids':x['supports_fact_ids']} for x in evidence_sources],
           'model':MODEL,'prompt_sha256':PROMPT_SHA,'candidate_answer_in_review_input':False,'conclusion':'supported_candidate','human_reviewed':False,'independence_limit':'Same active AI session authored and checked this item; this does not establish independent review.'})

# Normalize all historical rows without changing their QA content, IDs, or assigned splits.
historical_v2=[]
migration=[]
for idx,(original,assignment) in enumerate(zip(historical_old,historical_assign)):
    r=copy.deepcopy(original)
    r['dataset_version']='2.0.0'
    # Normalize legacy source references and keep record permission separate from report terms.
    rights=r.setdefault('publication_rights',{})
    if not rights.get('record_license'):
        record_license=rights.get('dataset_license')
        if not record_license:
            raise ValueError(f"Historical row lacks a license: {r.get('query_id')}")
        rights['record_license']=record_license
        rights['license_scope']='This historical record and its adapted QA metadata only; no single license applies to all records in the v2 repository.'
        rights['required_adaptation_disclaimers']=[old_sources[sid].get('required_adaptation_disclaimer') for sid in r.get('source_ids',[]) if old_sources[sid].get('required_adaptation_disclaimer')]
        rights['translation_disclaimers']=[old_sources[sid].get('translation_disclaimer') for sid in r.get('source_ids',[]) if old_sources[sid].get('translation_disclaimer')]
        rights['source_license_obligations']=[{'source_id':sid,'source_license':old_sources[sid].get('license'),'license_url':old_sources[sid].get('license_url'),
          'required_attribution':old_sources[sid].get('required_attribution') or old_sources[sid].get('required_source_attribution_short_form'),
          'required_adaptation_disclaimer':old_sources[sid].get('required_adaptation_disclaimer'),
          'translation_disclaimer':old_sources[sid].get('translation_disclaimer'),'third_party_content_limitations':old_sources[sid].get('third_party_content_limitations'),
          'sharealike_applies_to_adapted_record':'SA' in str(old_sources[sid].get('license','')),
          'reuse_authorization_status':old_sources[sid].get('record_reuse_authorization',{}).get('status','source_license_recorded')} for sid in r.get('source_ids',[])]
        rights['license_url']=LICENSE_URLS.get(record_license,rights.get('license_url'))
    rights['dataset_license']=rights.get('record_license') or rights.get('dataset_license')
    rights.setdefault('record_license',rights['dataset_license'])
    rights.setdefault('license_scope','This historical QA record only; no single license applies to all records or to the underlying source reports.')
    if any(sid.startswith('CAICT-') for sid in r.get('source_ids',[])):
        rights['reuse_permission_status']='dataset_owner_confirmed_authorized'
        rights['reuse_permission_basis']='dataset_owner_confirmation_2026-10-07'
        rights['reuse_permission_note']='The dataset owner confirmed these historical QA records are authorized for redistribution; this does not assert that the underlying source report is CC BY licensed.'
    for ref in r.get('source_refs',[]):
        sid=ref.get('source_id')
        if sid in old_sources and sid.startswith('CAICT-'):
            ref.setdefault('license',old_sources[sid].get('license'))
            ref.setdefault('required_attribution',old_sources[sid].get('required_attribution'))
    refs=r.setdefault('source_refs',[])
    ref_ids={ref.get('source_id') for ref in refs}
    for sid in r.get('source_ids',[]):
        if sid not in ref_ids:
            missing_ref=copy.deepcopy(old_sources[sid])
            missing_ref['license']=old_sources[sid].get('license')
            missing_ref['required_attribution']=old_sources[sid].get('required_attribution') or old_sources[sid].get('required_source_attribution_short_form')
            refs.append(missing_ref)
            ref_ids.add(sid)
    old_type=r.get('task_type','single_document')
    if old_type=='unanswerable_absence': family='answerability_judgment'
    elif old_type=='cross_document_synthesis': family='cross_document_synthesis'
    elif old_type=='table_chart_reasoning': family='visual_data_reasoning'
    elif any(token in old_type for token in ['comparison','temporal','numeric','percentage','count','metric','forecast']): family='temporal_numeric_reasoning'
    elif any(token in old_type for token in ['multi_fact','list','framework','category']): family='within_document_synthesis'
    else: family='single_document_retrieval'
    r['task_family']=family
    r['task_subtype']=old_type
    unresolved=any(old_sources[sid]['v2_source_file_audit_status']=='pending_source_file_revalidation' for sid in r.get('source_ids',[]))
    r['review_status']='pending_source_file_revalidation' if unresolved else 'pending_v2_answer_blind_reconstruction'
    r['review_provenance']={'reviewer':'not_completed_for_v2','model':None,'prompt_sha256':None,'reviewed_on':None,
       'source_files':[{'source_id':sid,'sha256':old_sources[sid].get('original_report_sha256') or old_sources[sid].get('source_pdf_sha256')} for sid in r.get('source_ids',[])],
       'candidate_answer_in_review_input':None,'reconstruction_conclusion':'pending','independent_reviewer':False,
       'method_limit':'v1.1/v1.2 source checking is historical and does not count as the v2 answer-blind reconstruction.'}
    r['recommended_for_evaluation']=True
    r['recommendation_status']='included_in_recommended_subset_per_dataset_owner_instruction; review status remains pending and is not a gold or human-review claim'
    r['human_reviewed']=False
    r['supersedes_query_id']=None
    r['split_provenance']={'assignment_version':assignment.get('assignment_version') or original.get('split_assignment_version') or 'historical_split_v1','assignment_timing':'post_annotation_historical_split','split':'legacy_post_annotation_assignment','pre_annotation_split':False}
    r['historical_task_type']=old_type
    historical_v2.append(r)
    migration.append({'query_id':original['query_id'],'original_v1_2_row_index_1based':idx+1,'original_row_sha256':sha_bytes(compact(original).encode()),'historical_split':original.get('split'),
       'disposition':'retained_in_unified_v2_corpus; owner_attested_authorized' if any(sid.startswith('CAICT-') for sid in original.get('source_ids',[])) else 'retained_in_unified_v2_corpus',
       'active_v2':True,'recommended_for_evaluation':True,'supersedes_query_id':None,'v2_review_status':r['review_status']})

all_rows=historical_v2+new_records
assert len(all_rows)==833+len(Q)
all_rows.sort(key=lambda r: (r['split']!='TRAIN', r['split']!='DEV', r['query_id']))
# Keep records in ID order for convenient historic prefix auditing (old IDs then v2 IDs).
all_rows=sorted(all_rows,key=lambda r:r['query_id'])
write_jsonl(OUT/'records.jsonl',all_rows)

# Preserve active historical split assignments and add preassigned family assignments for v2 rows.
assignment_map={a['query_id']:copy.deepcopy(a) for a in historical_assign}
assignments=[]
for r in all_rows:
    if r['query_id'] in assignment_map:
        a=assignment_map[r['query_id']]
        a['v2_split_provenance']='historical_post_annotation_v1_assignment'
    else:
        a={'query_id':r['query_id'],'split':r['split'],'connected_component_id':r['connected_group_id'],'family_ids':r['family_ids'],'source_ids':r['source_ids'],
           'task_type':r['task_type'],'task_family':r['task_family'],'task_subtype':r['task_subtype'],'assignment_version':'v2_source_families_preassigned_v1',
           'assignment_timing':'before_question_drafting','pre_annotation_split':True,'human_reviewed':False}
    assignments.append(a)
write_jsonl(OUT/'split_assignments.jsonl',assignments)

source_ids={sid for r in all_rows for sid in r.get('source_ids',[])}
source_map={sid:copy.deepcopy(old_sources[sid]) for sid in needed_old_ids}
source_map.update({sid:copy.deepcopy(new_source_map[sid]) for sid in new_source_map})
# Add source family and active-v2 license audit fields without rewriting historical source rights.
for sid,src in source_map.items():
    src['active_v2_record_count']=sum(sid in r.get('source_ids',[]) for r in all_rows)
    institution=src.get('publication_institution','')
    if institution in {'World Bank','International Labour Organization','Asian Development Bank'}:
        entities=[institution]
    elif institution.startswith('International Telecommunication Union'):
        entities=['ITU']
    elif institution.startswith('World Health Organization'):
        entities=['WHO']
    elif institution.startswith('UNESCO Institute for Information Technologies'):
        entities=['UNESCO','Shanghai Open University']
    elif institution.startswith('UNESCO Global Education Monitoring') or institution=='UNESCO':
        entities=['UNESCO']
    elif institution.startswith('Taiwan Academic Research Ethics'):
        entities=['Taiwan Academic Research Ethics Education Center']
    elif 'Food and Agriculture Organization' in institution:
        entities=['FAO']
    else:
        entities=[institution]
    src['publishing_institution_entities']=entities
    if 'v2_source_file_audit_status' not in src:
        src['v2_source_file_audit_status']=src.get('source_file_audit_status','historical_registry_only')
source_doc={'schema_version':'iicr_source_registry_v2_0','dataset_version':'2.0.0','source_count':len(source_map),
  'record_level_license_policy':'The package contains record-level mixed licenses. Source licenses and attribution/adaptation/translation duties are stated where established. For legacy CAICT rows, the dataset-owner authorization confirmation applies to the QA records; no license is asserted for the source reports. No single license applies to all records.',
  'long_source_passage_or_media_included':False,'source_sentence_cloze_excerpts_included':True,'review_provenance':'The 32 added source PDFs and rights pages were checked for this release. The 1,107 cloze candidates have not had answer-blind content or third-party attribution review and remain marked pending; the dataset owner directed that pending items remain recommended. Authorization to republish legacy CAICT QA records was confirmed separately.','sources':sorted(source_map.values(),key=lambda s:s['source_id'])}
(OUT/'sources.json').write_text(json.dumps(source_doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Candidate and recommended Viewer configurations both contain the complete unified dataset.
viewer_splits={'TRAIN':'train','DEV':'validation','TEST':'test'}
for split,filename in viewer_splits.items():
    candidates=[r for r in all_rows if r['split']==split]
    recommended=[r for r in candidates if r['recommended_for_evaluation']]
    def viewer(r):
        return {'query_id':r['query_id'],'question':r['question'],'answer_candidate':r.get('gold_answer'),
          'answerability':r.get('answerability'),'split':r['split'],'task_family':r['task_family'],'task_subtype':r['task_subtype'],
          'source_ids':r['source_ids'],'review_status':r['review_status'],'recommended_for_evaluation':r['recommended_for_evaluation'],
          'record_license':r.get('publication_rights',{}).get('record_license'),'record_json':compact(r)}
    write_jsonl(OUT/'data'/f'candidates_{filename}.jsonl',[viewer(r) for r in candidates])
    write_jsonl(OUT/'data'/'recommended'/f'{filename}.jsonl',[viewer(r) for r in recommended])

write_jsonl(OUT/'audit'/'v2_question_only_review.jsonl',question_only)
write_jsonl(OUT/'audit'/'v2_answer_blind_reconstruction.jsonl',reconstruction_audit)
write_jsonl(OUT/'audit'/'v2_pending_content_review.jsonl',pending_content_audit)
write_jsonl(OUT/'audit'/'v2_migration_ledger.jsonl',sorted(migration,key=lambda x:x['original_v1_2_row_index_1based']))

split_manifest={'version':'v2_source_families_preassigned_v2','created_on':'2026-10-07','assignment_timing':'before drafting v2 questions',
  'family_assignments':[{'source_id':sid,'family_id':family,'split':split} for sid,(family,split) in FAMILIES.items()],
  'note':'The two UNESCO families used for cross-document questions are both assigned to TRAIN. Existing historical rows keep their post-annotation v1.1/v1.2 splits and are not described as blind holdout.'}
(OUT/'audit'/'v2_split_manifest.json').write_text(json.dumps(split_manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'audit'/'v2_review_prompt.md').write_text('# v2 AI source reconstruction prompt\n\n'+PROMPT+'\n\nThis prompt applies to the 60 answer-blind source-reconstructed questions only. The 1,107 sentence-cloze candidates were generated separately and remain pending content and attribution review. No independent human review is claimed.\n',encoding='utf-8')
print(f'Built {len(all_rows)} active records: historical={len(historical_v2)}, new={len(new_records)}, recommended={sum(r["recommended_for_evaluation"] for r in all_rows)}, sources={len(source_map)}')
print('Split counts:',dict(Counter(r['split'] for r in all_rows)))
print('Recommended split counts:',dict(Counter(r['split'] for r in all_rows if r['recommended_for_evaluation'])))
