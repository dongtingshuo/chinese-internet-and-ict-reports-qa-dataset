#!/usr/bin/env python3
"""Validate the v1.2.0 package, frozen prefixes, mixed rights, evidence, Viewer and hashes."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEGACY_COUNT = 506
V11_COUNT = 267
V12_COUNT = 60
TOTAL = LEGACY_COUNT + V11_COUNT + V12_COUNT
V11_END = LEGACY_COUNT + V11_COUNT
EXPECTED_SPLITS = {'TRAIN': 579, 'DEV': 128, 'TEST': 126}
V12_SPLITS = {'TRAIN': 42, 'DEV': 9, 'TEST': 9}
V12_TYPE_COUNTS = {'unanswerable_absence': 20, 'cross_document_synthesis': 20, 'table_chart_reasoning': 20}
V12_TYPE_SPLITS = {t: {'TRAIN': 14, 'DEV': 3, 'TEST': 3} for t in V12_TYPE_COUNTS}
V12_NEW_SOURCES = {'ILO2026-LIFELONG-SKILLS', 'UNESCO2023-DIGITAL-CITIZENSHIP', 'ILO2021-EMPLOYMENT-RELATIONSHIP'}
V11_SOURCES = {
    'WB2014-RURAL', 'WB2016-DIGITAL', 'WB2019-WORK', 'WB2025-DIGITAL',
    'ILO2020-PLATFORM', 'ILO2021-PLATFORM', 'ADB2018-CITIES', 'ADB2023-YOUTH',
}
EXPECTED_LICENSE_URLS = {
    'CC-BY-3.0-IGO': 'https://creativecommons.org/licenses/by/3.0/igo/',
    'CC-BY-SA-3.0-IGO': 'https://creativecommons.org/licenses/by-sa/3.0/igo/',
    'CC-BY-4.0': 'https://creativecommons.org/licenses/by/4.0/',
}
FROZEN_V1_0_RECORDS = '7d4d3028b06c7926515607ecb9ad596984a74feccc91a0cea5fac2dc23fc6a6a'
FROZEN_V1_0_SPLITS = 'fe3ef765e94f142bcf4c40d4d1011b1c1cd42520b99ab7361421636b6add670e'
FROZEN_V1_1_RECORDS = 'f00ffbb66a5af9ac097c626717979ce055154d75b58d27aa4a4ea4267e2f21f4'
FROZEN_V1_1_SPLITS = '72d91d55dc53f97edbbce9e8512cc6b2eae8a3ba7fe25dc630cee8c390e024f3'
FROZEN_LICENSE = '9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def sha_bytes(blob):
    return hashlib.sha256(blob).hexdigest()


def sha(path):
    return sha_bytes(path.read_bytes())


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def package_files():
    return (p for p in ROOT.rglob('*') if p.is_file()
            and '.git' not in p.relative_to(ROOT).parts
            and '__pycache__' not in p.relative_to(ROOT).parts)


record_lines = (ROOT / 'records.jsonl').read_bytes().splitlines(keepends=True)
assignment_lines = (ROOT / 'split_assignments.jsonl').read_bytes().splitlines(keepends=True)
require(len(record_lines) == TOTAL, f'expected {TOTAL} records, got {len(record_lines)}')
require(len(assignment_lines) == TOTAL, f'expected {TOTAL} split assignments, got {len(assignment_lines)}')
require(sha_bytes(b''.join(record_lines[:LEGACY_COUNT])) == FROZEN_V1_0_RECORDS, 'frozen v1.0 record prefix changed')
require(sha_bytes(b''.join(assignment_lines[:LEGACY_COUNT])) == FROZEN_V1_0_SPLITS, 'frozen v1.0 assignment prefix changed')
require(sha_bytes(b''.join(record_lines[:V11_END])) == FROZEN_V1_1_RECORDS, 'frozen v1.1 record prefix changed')
require(sha_bytes(b''.join(assignment_lines[:V11_END])) == FROZEN_V1_1_SPLITS, 'frozen v1.1 assignment prefix changed')
require(sha(ROOT / 'LICENSE-CC-BY-4.0.txt') == FROZEN_LICENSE, 'legacy CC BY 4.0 license text changed')

records = [json.loads(x) for x in record_lines]
assignments = [json.loads(x) for x in assignment_lines]
manifest = read_json(ROOT / 'manifest.json')
sources_doc = read_json(ROOT / 'sources.json')
sources_list = sources_doc.get('sources', [])
sources = {s['source_id']: s for s in sources_list}
require(len(sources_list) == 25 and len(sources) == 25, 'source catalog must contain 25 unique sources')
require(sources_doc.get('source_count') == 25, 'source registry count mismatch')
require(sources_doc.get('dataset_version') == '1.2.0', 'source registry version mismatch')
require(manifest.get('version') == '1.2.0', 'manifest version mismatch')
require(manifest.get('record_count') == TOTAL, 'manifest record count mismatch')
require(manifest.get('legacy_record_count') == LEGACY_COUNT, 'manifest legacy count mismatch')
require(manifest.get('v1_1_record_count') == V11_COUNT, 'manifest v1.1 count mismatch')
require(manifest.get('v1_2_record_count') == V12_COUNT, 'manifest v1.2 count mismatch')
require(manifest.get('source_count') == 25, 'manifest source count mismatch')
require(manifest.get('v1_1_source_count') == 8, 'manifest v1.1 source count mismatch')
require(manifest.get('v1_2_new_source_count') == 3, 'manifest v1.2 new source count mismatch')
require(manifest.get('split_counts') == EXPECTED_SPLITS, 'manifest split counts mismatch')
require(manifest.get('v1_2_split_counts') == V12_SPLITS, 'manifest v1.2 split counts mismatch')
require(manifest.get('v1_2_question_type_counts') == V12_TYPE_COUNTS, 'manifest v1.2 question type counts mismatch')
require(manifest.get('v1_2_question_type_split_counts') == V12_TYPE_SPLITS, 'manifest v1.2 type/split matrix mismatch')
require(manifest.get('answerability_counts') == {'answerable': 812, 'unanswerable': 21}, 'answerability counts mismatch')
require(manifest.get('dataset_license') == 'mixed_record_level', 'package must declare record-level mixed licensing')
require(manifest.get('source_pdfs_or_media_included') is False, 'source PDFs/media must remain excluded')
require(manifest.get('human_reviewed') is False, 'package must not claim independent human review')
require(manifest.get('v1_0_records_and_splits_unchanged') is True, 'frozen v1.0 status missing')
require(manifest.get('v1_1_records_and_splits_unchanged') is True, 'frozen v1.1 status missing')

ids = [r.get('query_id') for r in records]
require(None not in ids and len(set(ids)) == TOTAL, 'query IDs missing or duplicated')
v11_rows = records[LEGACY_COUNT:V11_END]
v12_rows = records[V11_END:]
require(all(r.get('schema_version') == 'iicr_report_qa_v1_1' for r in v11_rows), 'v1.1 rows changed schema')
require([r['query_id'] for r in v11_rows] == [f'IICR-V11-{n:04d}' for n in range(1, V11_COUNT + 1)], 'v1.1 IDs changed')
require([r['query_id'] for r in v12_rows] == [f'IICR-V12-{n:04d}' for n in range(1, V12_COUNT + 1)], 'v1.2 IDs are not contiguous')
require(len({r['question'] for r in v12_rows}) == V12_COUNT, 'v1.2 questions contain duplicates')

# Known physical/printed page repair retained from v1.1.
for qid in ('IICR-V11-0079', 'IICR-V11-0080', 'IICR-V11-0081', 'IICR-V11-0082', 'IICR-V11-0083'):
    row = next(r for r in v11_rows if r['query_id'] == qid)
    loc = row['gold_evidence_sets'][0]['sources'][0]
    require(row.get('source_ids') == ['WB2019-WORK'], f'WDR2019 source changed on {qid}')
    require((loc.get('pdf_page'), loc.get('printed_page'), loc.get('element_id')) == (49, 37, 'wb2019-work-p0049-narrative'), f'WDR2019 page locator changed on {qid}')

assign_by_id = {a['query_id']: a for a in assignments}
require(len(assign_by_id) == TOTAL and set(ids) == set(assign_by_id), 'records and split assignments differ')
counts = Counter(r.get('split') for r in records)
require(dict(counts) == EXPECTED_SPLITS, f'unexpected total split counts: {dict(counts)}')
require(dict(Counter(r['split'] for r in v12_rows)) == V12_SPLITS, 'unexpected v1.2 split counts')
require(dict(Counter(r['task_type'] for r in v12_rows)) == V12_TYPE_COUNTS, 'v1.2 task type counts mismatch')
for task_type, expected in V12_TYPE_SPLITS.items():
    require(dict(Counter(r['split'] for r in v12_rows if r['task_type'] == task_type)) == expected, f'{task_type} split matrix mismatch')

all_group_splits = defaultdict(set)
all_family_splits = defaultdict(set)
all_source_splits = defaultdict(set)
for i, r in enumerate(records):
    qid = r['query_id']; split = r.get('split'); a = assign_by_id[qid]
    require(split in EXPECTED_SPLITS, f'invalid split on {qid}')
    require(a.get('split') == split, f'split assignment mismatch on {qid}')
    require(a.get('source_ids') == r.get('source_ids'), f'assignment sources mismatch on {qid}')
    require(r.get('gold_candidate') is True, f'candidate marker missing on {qid}')
    require(r.get('question') and isinstance(r.get('gold_answer'), str) and r.get('gold_answer'), f'empty QA on {qid}')
    require(r.get('answerability') in {'answerable', 'unanswerable'}, f'bad answerability on {qid}')
    quality = r.get('gold_quality', {})
    require(quality.get('human_reviewed') is not True, f'human review overclaim on {qid}')
    if r['answerability'] == 'answerable':
        require(r.get('required_facts') and r.get('gold_evidence_sets'), f'answerable row lacks facts/evidence: {qid}')
    component = r.get('legacy_split_component_id') if i < LEGACY_COUNT else r.get('connected_group_id')
    if component: all_group_splits[component].add(split)
    families = r.get('legacy_family_ids') or ([r['family_id']] if r.get('family_id') else [])
    for fam in families: all_family_splits[fam].add(split)
    for sid in r.get('source_ids', []):
        require(sid in sources, f'unknown source {sid} on {qid}')
        all_source_splits[sid].add(split)
    if i < LEGACY_COUNT:
        require(r.get('schema_version') == 'legacy_main_domain_gold_candidate_record_v1', f'legacy schema changed: {qid}')
    elif i < V11_END:
        require(r.get('human_reviewed') is False, f'v1.1 human review flag missing: {qid}')
        require(r.get('split_assignment_version') == 'dataset_split_v1_1', f'v1.1 split version mismatch: {qid}')
        require(r.get('answerability') == 'answerable', f'v1.1 row unexpectedly unanswerable: {qid}')
        require(r.get('modality_tags') == ['text'], f'v1.1 modality changed: {qid}')
        require(quality.get('source_support_status') == 'source_verified_candidate', f'v1.1 support state mismatch: {qid}')
        require(r.get('publication_rights', {}).get('record_license', r.get('publication_rights', {}).get('dataset_license')) == 'CC-BY-3.0-IGO', f'v1.1 record license changed: {qid}')
    else:
        require(r.get('schema_version') == 'iicr_report_qa_v1_2', f'v1.2 schema mismatch: {qid}')
        require(r.get('annotation_version') == 'iicr-ai-assisted-candidate-v1.2', f'v1.2 annotation version mismatch: {qid}')
        require(r.get('human_reviewed') is False and quality.get('human_reviewed') is False, f'v1.2 human_reviewed must be false: {qid}')
        require(r.get('split_assignment_version') == 'dataset_split_v1_2', f'v1.2 split version mismatch: {qid}')
        require(quality.get('independent_human_double_annotation') == 'not_performed', f'v1.2 independent review overclaim: {qid}')
        require(quality.get('heldout_gold_accessed') is False, f'v1.2 heldout access flag mismatch: {qid}')
        rights = r.get('publication_rights', {})
        require(rights.get('dataset_license') == rights.get('record_license'), f'dataset/record license mismatch on {qid}')
        lic = rights.get('record_license')
        require(lic in EXPECTED_LICENSE_URLS and rights.get('license_url') == EXPECTED_LICENSE_URLS[lic], f'unsupported license or URL on {qid}')
        require(rights.get('rights_assessment_is_legal_opinion') is False, f'rights opinion overclaim: {qid}')
        require(rights.get('source_attribution_required') is True, f'attribution flag missing: {qid}')
        require(rights.get('third_party_content_reused') is False and rights.get('source_excerpt_included') is False and rights.get('source_media_included') is False and rights.get('source_pdf_included') is False, f'prohibited source material flagged as included: {qid}')
        require(rights.get('source_pdf_redistribution') == 'not_included_in_package', f'source PDF distribution metadata mismatch: {qid}')
        require(r.get('source_ids') and len(set(r['source_ids'])) == len(r['source_ids']), f'bad source id list: {qid}')
        refs = {ref.get('source_id'): ref for ref in r.get('source_refs', [])}
        obligations = {o.get('source_id'): o for o in rights.get('source_license_obligations', [])}
        require(set(refs) == set(r['source_ids']), f'source refs do not match source IDs: {qid}')
        require(set(obligations) == set(r['source_ids']), f'license obligations do not match sources: {qid}')
        source_licenses = set()
        attributions = set(); disclaimers = set(); translations = set()
        for sid in r['source_ids']:
            src = sources[sid]; ref = refs[sid]; obligation = obligations[sid]
            src_license = src.get('license_id')
            require(src_license in EXPECTED_LICENSE_URLS, f'v1.2 source lacks recognized license: {sid}')
            source_licenses.add(src_license)
            require(src.get('license_url') == EXPECTED_LICENSE_URLS[src_license], f'source license URL mismatch: {sid}')
            require(rights.get('record_license') == src_license, f'record license differs from source license: {qid}/{sid}')
            require(ref.get('license_id') == src_license and ref.get('license_url') == src.get('license_url'), f'source ref license mismatch: {qid}/{sid}')
            require(ref.get('source_pdf_sha256') == src.get('original_report_sha256'), f'source hash mismatch: {qid}/{sid}')
            require(ref.get('official_pdf_url') == src.get('original_report_url'), f'source URL mismatch: {qid}/{sid}')
            require(ref.get('pdf_page_count') == src.get('source_pdf_page_count'), f'source page count mismatch: {qid}/{sid}')
            require(ref.get('rights_notice_location') == src.get('rights_notice_location'), f'rights notice locator mismatch: {qid}/{sid}')
            require(ref.get('required_source_attribution_short_form') == src.get('required_attribution'), f'attribution mismatch: {qid}/{sid}')
            for ref_field, source_field in (
                ('publisher', 'publisher'),
                ('title', 'title_chinese'),
                ('title_english', 'title_english'),
                ('text_language', 'text_language'),
                ('translation_status', 'translation_status'),
                ('official_publication_page_url', 'official_publication_page_url'),
                ('rights_holder', 'rights_holder'),
                ('license', 'license'),
                ('required_adaptation_disclaimer', 'required_adaptation_disclaimer'),
                ('translation_disclaimer', 'translation_disclaimer'),
                ('third_party_content_limitations', 'third_party_content_limitations'),
            ):
                require(ref.get(ref_field) == src.get(source_field), f'{ref_field} differs from source registry: {qid}/{sid}')
            require(ref.get('source_pdf_included') is False and src.get('source_pdf_included') is False, f'source PDF included: {qid}/{sid}')
            require(obligation.get('source_license') == src.get('license') and obligation.get('license_url') == src.get('license_url'), f'obligation license mismatch: {qid}/{sid}')
            require(obligation.get('required_attribution') == src.get('required_attribution'), f'obligation attribution mismatch: {qid}/{sid}')
            require(obligation.get('required_adaptation_disclaimer') == src.get('required_adaptation_disclaimer'), f'obligation disclaimer mismatch: {qid}/{sid}')
            require(obligation.get('translation_disclaimer') == src.get('translation_disclaimer'), f'translation disclaimer mismatch: {qid}/{sid}')
            require(obligation.get('third_party_content_limitations') == src.get('third_party_content_limitations'), f'third-party limits mismatch: {qid}/{sid}')
            require(obligation.get('sharealike_applies_to_adapted_record') == (src_license == 'CC-BY-SA-3.0-IGO'), f'SA flag mismatch: {qid}/{sid}')
            attributions.add(src['required_attribution']); disclaimers.add(src['required_adaptation_disclaimer'])
            if src.get('translation_disclaimer'): translations.add(src['translation_disclaimer'])
            require(isinstance(src.get('original_report_sha256'), str) and len(src['original_report_sha256']) == 64, f'invalid source hash: {sid}')
            require(isinstance(src.get('source_pdf_page_count'), int) and src['source_pdf_page_count'] > 0, f'invalid source PDF page count: {sid}')
        require(len(source_licenses) == 1, f'multi-license synthesis lacks a compatible single record license: {qid}')
        require(set(rights.get('required_source_attributions', [])) == attributions, f'required attributions mismatch: {qid}')
        require(set(rights.get('required_adaptation_disclaimers', [])) == disclaimers, f'adaptation notices mismatch: {qid}')
        require(set(rights.get('translation_disclaimers', [])) == translations, f'translation notices mismatch: {qid}')
        facts = {f.get('fact_id') for f in r.get('required_facts', [])}
        evidence_locs = [loc for es in r.get('gold_evidence_sets', []) for loc in es.get('sources', [])]
        for loc in evidence_locs:
            sid = loc.get('source_id')
            require(sid in r['source_ids'], f'evidence source not declared: {qid}/{sid}')
            require(isinstance(loc.get('pdf_page'), int) and 1 <= loc['pdf_page'] <= sources[sid]['source_pdf_page_count'], f'bad physical PDF page: {qid}/{sid}')
            require(loc.get('element_id'), f'locator element id missing: {qid}/{sid}')
            require(loc.get('supports_fact_ids') and set(loc['supports_fact_ids']) <= facts, f'evidence fact mapping invalid: {qid}/{sid}')
        if r['answerability'] == 'unanswerable':
            require(r['task_type'] == 'unanswerable_absence', f'no-answer task type mismatch: {qid}')
            require(not r.get('required_facts') and not r.get('gold_evidence_sets'), f'no-answer row has answer evidence: {qid}')
            av = r.get('absence_verification', {})
            require(av.get('missing_proposition') and av.get('search_terms') and av.get('review_method'), f'absence verification incomplete: {qid}')
            require(av.get('search_scope') and av.get('near_miss_evidence'), f'absence scope/near miss missing: {qid}')
            for scope in av['search_scope']:
                sid = scope.get('source_id'); pages = scope.get('pdf_pages_1based_inclusive', [])
                require(sid in r['source_ids'] and len(pages) == 2 and 1 <= pages[0] <= pages[1] <= sources[sid]['source_pdf_page_count'], f'bad absence scope: {qid}/{sid}')
            for near in av['near_miss_evidence']:
                sid = near.get('source_id')
                require(sid in r['source_ids'] and 1 <= near.get('pdf_page', 0) <= sources[sid]['source_pdf_page_count'], f'bad near-miss locator: {qid}/{sid}')
                require(near.get('element_id') and near.get('nearby_fact_summary') and near.get('why_insufficient'), f'near-miss explanation incomplete: {qid}')
        else:
            require(r['answerability'] == 'answerable', f'invalid v1.2 answerability: {qid}')
        if r['task_type'] == 'cross_document_synthesis':
            require(r['answerability'] == 'answerable' and len(r['source_ids']) >= 2, f'cross-document requires two sources: {qid}')
            located_sources = {loc.get('source_id') for loc in evidence_locs}
            covered_facts = set().union(*(set(loc.get('supports_fact_ids', [])) for loc in evidence_locs)) if evidence_locs else set()
            require(located_sources == set(r['source_ids']), f'cross-document evidence does not cover every source: {qid}')
            require(covered_facts == facts, f'cross-document evidence does not support every required fact: {qid}')
        elif r['task_type'] == 'table_chart_reasoning':
            visual = r.get('visual_dependency', {})
            require(r['answerability'] == 'answerable' and visual.get('requires_visual_reading') is True, f'visual dependency metadata missing: {qid}')
            require(visual.get('source_id') in r['source_ids'], f'visual dependency source mismatch: {qid}')
            require(visual.get('visual_type') in {'table', 'figure', 'chart'}, f'unknown visual type: {qid}')
            require(any(x in r.get('modality_tags', []) for x in ('table', 'figure', 'chart')), f'visual modality tag missing: {qid}')
            require(any(loc.get('source_id') == visual.get('source_id') and loc.get('pdf_page') == visual.get('pdf_page') for loc in evidence_locs), f'visual locator does not match evidence: {qid}')
            require(any(phrase in (visual.get('why') or '') for phrase in ('读取','比较','定位','配对','交叉','辨认')), f'visual dependency rationale missing: {qid}')
        else:
            require(r['task_type'] == 'unanswerable_absence', f'unknown v1.2 task type: {qid}')

require(all(len(v) == 1 for v in all_group_splits.values()), 'connected evidence group crosses splits')
require(all(len(v) == 1 for v in all_family_splits.values()), 'report family crosses splits')
require(all(len(v) == 1 for v in all_source_splits.values()), 'source crosses splits')

def split_group_counts(groups):
    return dict(Counter(next(iter(splits)) for splits in groups.values()))
require(split_group_counts(all_group_splits) == manifest.get('connected_component_counts'), 'connected component counts mismatch')
require(split_group_counts(all_family_splits) == manifest.get('family_counts'), 'family counts mismatch')
require(split_group_counts(all_source_splits) == manifest.get('source_counts'), 'source counts mismatch')

require({sid for r in v11_rows for sid in r['source_ids']} == V11_SOURCES, 'v1.1 source families changed')
v12_source_ids = {sid for r in v12_rows for sid in r['source_ids']}
require(v12_source_ids == set(manifest.get('v1_2_source_ids', [])), 'v1.2 source IDs mismatch')
require(V12_NEW_SOURCES <= set(sources), 'v1.2 source catalog additions missing')
require({sid for sid in v12_source_ids if sid in V12_NEW_SOURCES} == V12_NEW_SOURCES, 'not all three new source reports are represented')
new_publishers = {sources[sid]['publication_institution'] for sid in V12_NEW_SOURCES}
require(sorted(new_publishers) == sorted(manifest.get('v1_2_new_source_publishers', [])), 'v1.2 new source publisher list mismatch')
require(len(new_publishers) >= 2, 'v1.2 additions must include the two catalogued publishing institutions')
source_record_counts = Counter(sid for r in v12_rows for sid in r['source_ids'])
require(dict(source_record_counts) == manifest.get('v1_2_source_record_counts'), 'v1.2 source-record counts mismatch')
license_counts = Counter(r.get('publication_rights', {}).get('record_license', r.get('publication_rights', {}).get('dataset_license')) for r in records)
require(dict(license_counts) == manifest.get('record_license_counts'), 'record license count mismatch')
require(dict(Counter(r['publication_rights']['record_license'] for r in v12_rows)) == manifest.get('v1_2_record_license_counts'), 'v1.2 license count mismatch')

schema = read_json(ROOT / 'schema.json')
require(schema.get('$schema') == 'https://json-schema.org/draft/2020-12/schema', 'schema dialect mismatch')
require({'legacy_v1_0', 'iicr_report_qa_v1_1', 'iicr_report_qa_v1_2'} <= set(schema.get('$defs', {})), 'schema definitions missing')
require(len(schema.get('oneOf', [])) == 3, 'schema must include exactly legacy, v1.1 and v1.2 families')
try:
    import jsonschema
    jsonschema.Draft202012Validator.check_schema(schema)
    errors = []
    for i, r in enumerate(records):
        errors.extend((i, e.message) for e in jsonschema.Draft202012Validator(schema).iter_errors(r))
        if len(errors) >= 10: break
    require(not errors, f'JSON Schema validation errors: {errors[:10]}')
except ImportError:
    # Structural and conditional rules above remain mandatory where jsonschema is unavailable.
    pass

for split_name, split in {'train':'TRAIN','validation':'DEV','test':'TEST'}.items():
    viewer_path = ROOT / 'data' / f'{split_name}.jsonl'
    viewer = jsonl(viewer_path)
    canonical = {r['query_id']:r for r in records if r['split'] == split}
    require(len(viewer) == len(canonical), f'Viewer {split_name} count mismatch')
    seen = set()
    for row in viewer:
        qid = row.get('query_id')
        require(qid in canonical and qid not in seen, f'Viewer missing/duplicate row: {split_name}/{qid}')
        seen.add(qid); src = canonical[qid]
        require(row.get('split') == split and row.get('task_type') == src['task_type'], f'Viewer task/split mismatch: {qid}')
        require(row.get('source_ids') == src['source_ids'], f'Viewer source IDs mismatch: {qid}')
        require(row.get('record_license') == src.get('publication_rights',{}).get('record_license',src.get('publication_rights',{}).get('dataset_license')), f'Viewer license mismatch: {qid}')
        require(row.get('modality_tags') == src.get('modality_tags', []), f'Viewer modality mismatch: {qid}')
        require(json.loads(row.get('record_json','{}')) == src, f'Viewer canonical JSON mismatch: {qid}')
        require(row.get('question') == src['question'] and row.get('gold_answer') == src['gold_answer'], f'Viewer QA mismatch: {qid}')

report = read_json(ROOT / 'VALIDATION_REPORT.json')
require(report.get('version') == '1.2.0' and report.get('record_count') == TOTAL, 'validation report version/count mismatch')
require(report.get('validation_status') == 'passed', 'validation report status is not passed')
for p in package_files():
    require(p.suffix.lower() not in {'.pdf','.png','.jpg','.jpeg','.webp','.gif'}, f'source media must remain excluded: {p.relative_to(ROOT)}')
for entry in manifest.get('package_files', []):
    p = ROOT / entry['path']
    require(p.is_file(), f'manifest file missing: {entry["path"]}')
    require(sha(p) == entry['sha256'], f'manifest hash mismatch: {entry["path"]}')
    require(p.stat().st_size == entry['bytes'], f'manifest byte count mismatch: {entry["path"]}')
sums = ROOT / 'SHA256SUMS'; seen = set()
for line in sums.read_text(encoding='utf-8').splitlines():
    if line.strip():
        digest, rel = line.split('  ',1); p = ROOT / rel
        require(p.is_file() and sha(p) == digest, f'SHA256SUMS mismatch: {rel}')
        seen.add(rel)
expected = {p.relative_to(ROOT).as_posix() for p in package_files() if p.name != 'SHA256SUMS'}
require(seen == expected, 'SHA256SUMS file coverage mismatch')

print('PASS: v1.2.0; 833 rows; frozen v1.0/v1.1 records and splits; 60 additions (20 per task type); 579/128/126 splits; mixed per-record licenses and attribution; no-answer/cross-document/visual evidence checks; source/family/component split isolation; Viewer parity; manifest and SHA256 coverage.')
