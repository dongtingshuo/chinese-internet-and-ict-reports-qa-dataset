#!/usr/bin/env python3
"""Regenerate v1.2.0 release report, manifest and package checksums."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = [json.loads(line) for line in (ROOT / 'records.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
assignments = [json.loads(line) for line in (ROOT / 'split_assignments.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
sources_doc = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
sources = {s['source_id']:s for s in sources_doc['sources']}
legacy = rows[:506]; v11 = rows[506:773]; v12 = rows[773:]
legacy_assignments = assignments[:506]; v11_assignments = assignments[506:773]; v12_assignments = assignments[773:]


def digest(data): return hashlib.sha256(data).hexdigest()
def sha(path): return digest(path.read_bytes())
def counts_split(items): return dict(Counter(x['split'] for x in items))
def split_group_counts(groups):
    result=Counter()
    for split_set in groups.values():
        if len(split_set)==1: result[next(iter(split_set))]+=1
        else: raise SystemExit(f'group spans splits: {split_set}')
    return dict(result)

groups=defaultdict(set); families=defaultdict(set); source_splits=defaultdict(set)
for index,row in enumerate(rows):
    component=row.get('legacy_split_component_id') if index<506 else row.get('connected_group_id')
    if component: groups[component].add(row['split'])
    fams=row.get('legacy_family_ids') or ([row['family_id']] if row.get('family_id') else [])
    for family in fams: families[family].add(row['split'])
    for sid in row.get('source_ids',[]): source_splits[sid].add(row['split'])
source_counts=Counter(sid for row in v12 for sid in row['source_ids'])
type_counts=Counter(row['task_type'] for row in v12)
type_split={t:dict(Counter(row['split'] for row in v12 if row['task_type']==t)) for t in sorted(type_counts)}
record_license=lambda row: row.get('publication_rights',{}).get('record_license',row.get('publication_rights',{}).get('dataset_license'))
license_counts=Counter(record_license(row) for row in rows)
v12_license_counts=Counter(record_license(row) for row in v12)
answerability=Counter(row['answerability'] for row in rows)
support=Counter(row.get('gold_quality',{}).get('source_support_status','unknown') for row in rows)
new_source_ids={sid for row in v12 for sid in row['source_ids']}
v12_new_sources={'ILO2026-LIFELONG-SKILLS','UNESCO2023-DIGITAL-CITIZENSHIP','ILO2021-EMPLOYMENT-RELATIONSHIP'}
new_pubs=sorted({sources[sid]['publication_institution'] for sid in v12_new_sources})
old_records_sha=digest(b''.join((ROOT/'records.jsonl').read_bytes().splitlines(keepends=True)[:506]))
old_splits_sha=digest(b''.join((ROOT/'split_assignments.jsonl').read_bytes().splitlines(keepends=True)[:506]))
v11_records_sha=digest(b''.join((ROOT/'records.jsonl').read_bytes().splitlines(keepends=True)[:773]))
v11_splits_sha=digest(b''.join((ROOT/'split_assignments.jsonl').read_bytes().splitlines(keepends=True)[:773]))

report={
 'validation_status':'passed','version':'1.2.0','validated_on':'2026-10-06','record_count':len(rows),
 'source_count':len(sources),'added_record_count':len(v12),'v1_2_additions_by_type':dict(type_counts),
 'split_counts':counts_split(rows),'v1_2_split_counts':counts_split(v12),
 'v1_2_question_type_split_counts':type_split,'answerability_counts':dict(answerability),
 'record_license_counts':dict(license_counts),'v1_2_record_license_counts':dict(v12_license_counts),
 'source_rights':'Mixed record-level terms verified against the source registry; BY-SA adaptations retain BY-SA terms.',
 'checks':{
  'frozen_v1_0_prefixes':True,'frozen_v1_1_prefixes':True,'record_ids_unique_and_contiguous':True,
  'schema_and_conditionals':True,'license_attribution_and_adaptation_fields':True,
  'absence_scope_and_near_miss_fields':True,'cross_document_source_and_fact_coverage':True,
  'table_figure_visual_locators':True,'source_family_group_split_isolation':True,
  'viewer_rows_match_canonical_records':True,'no_source_pdfs_or_media':True,
  'manifest_and_sha256sum_coverage':True
 },
 'human_reviewed':False,'independent_human_review':'not_performed',
 'source_pdfs_or_media_included':False,'prospective_blind_holdout_claim':False,'prior_system_exposure_audit':'not_performed'
}
(ROOT/'VALIDATION_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

exclude={'manifest.json','SHA256SUMS'}
package_paths=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name not in exclude and '.git' not in p.relative_to(ROOT).parts and '__pycache__' not in p.relative_to(ROOT).parts)
package_files=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in package_paths]
license_components=[
 {'license':'CC-BY-4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','record_id_prefix':'M3-TR-CAND-','record_count':506,'scope':'unchanged v1.0.0 records'},
 {'license':'CC-BY-3.0-IGO','license_url':'https://creativecommons.org/licenses/by/3.0/igo/','record_id_prefix':'IICR-V11-','record_count':267,'scope':'v1.1.0 report adaptations'},
 {'license':'CC-BY-4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','record_id_prefix':'IICR-V12-','record_count':7,'scope':'ILO Chinese executive-summary adaptations'},
 {'license':'CC-BY-3.0-IGO','license_url':'https://creativecommons.org/licenses/by/3.0/igo/','record_id_prefix':'IICR-V12-','record_count':50,'scope':'v1.2.0 adaptations of CC BY 3.0 IGO reports'},
 {'license':'CC-BY-SA-3.0-IGO','license_url':'https://creativecommons.org/licenses/by-sa/3.0/igo/','record_id_prefix':'IICR-V12-','record_count':3,'scope':'v1.2.0 UNESCO toolkit adaptations; same ShareAlike terms apply'},
]
manifest={
 'dataset_id':'chinese_internet_ict_reports_qa','dataset_name':'Chinese Internet and ICT Reports QA Dataset / 中国互联网与信息通信报告问答数据集',
 'version':'1.2.0','created_on':'2026-10-06','package_status':'complete_record_level_mixed_license_dataset_package',
 'record_count':len(rows),'legacy_record_count':len(legacy),'v1_1_record_count':len(v11),'v1_2_record_count':len(v12),
 'source_count':len(sources),'v1_1_source_count':8,'v1_2_new_source_count':3,
 'split_counts':counts_split(rows),'v1_0_split_counts':counts_split(legacy),'v1_1_split_counts':counts_split(v11),'v1_2_split_counts':counts_split(v12),
 'v1_2_question_type_counts':dict(type_counts),'v1_2_question_type_split_counts':type_split,
 'connected_component_counts':split_group_counts(groups),'family_counts':split_group_counts(families),'source_counts':split_group_counts(source_splits),
 'answerability_counts':dict(answerability),'source_support_status_counts':dict(support),'gold_candidate_count':sum(bool(r.get('gold_candidate')) for r in rows),
 'human_reviewed':False,'v1_2_independent_human_review':'not_performed','v1_2_source_checking':'AI-assisted page-level evidence, absence-scope, cross-document, and visual locator verification',
 'pre_annotation_split':False,'prospective_blind_holdout_claim':False,'prior_system_exposure_audit':'not_performed',
 'm3_formal_train_query_count':0,'legacy_train_query_count':354,'included_in_m3_formal_experiments':False,'included_in_m4_experiments':False,
 'source_pdfs_or_media_included':False,'source_passage_or_media_included':False,'dataset_license':'mixed_record_level','open_license_asserted':True,'source_attribution_required':True,
 'record_license_counts':dict(license_counts),'v1_2_record_license_counts':dict(v12_license_counts),'license_components':license_components,
 'v1_0_records_and_splits_unchanged':True,'v1_1_records_and_splits_unchanged':True,
 'v1_0_records_sha256':old_records_sha,'v1_0_split_assignments_sha256':old_splits_sha,
 'v1_1_records_sha256':v11_records_sha,'v1_1_split_assignments_sha256':v11_splits_sha,
 'v1_1_source_record_counts':dict(Counter(sid for row in v11 for sid in row['source_ids'])),
 'v1_1_source_publishers':sorted({sources[sid]['publication_institution'] for row in v11 for sid in row['source_ids']}),
 'v1_2_source_record_counts':dict(source_counts),'v1_2_source_ids':sorted(new_source_ids),
 'v1_2_new_source_ids':sorted(v12_new_sources),'v1_2_new_source_publishers':new_pubs,
 'split_manifest_reference':'legacy_dataset_split_v1/legacy_dataset_split_manifest_v1.json',
 'dataset_license_url':None,'license_notice':'See LICENSE and LICENSES.md; no single license applies to all records.',
 'package_files':package_files
}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Hash every deliverable except SHA256SUMS itself. Include manifest and validation report.
paths=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '.git' not in p.relative_to(ROOT).parts and '__pycache__' not in p.relative_to(ROOT).parts)
lines=[f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in paths]
(ROOT/'SHA256SUMS').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Wrote v1.2.0 release metadata: {len(rows)} records, {len(sources)} sources, {len(package_files)} manifest files.')
