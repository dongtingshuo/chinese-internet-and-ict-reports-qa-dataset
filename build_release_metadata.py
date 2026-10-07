#!/usr/bin/env python3
"""Generate the v2.0.0 validation report, manifest, and SHA256SUMS."""
import collections, hashlib, json, re
from pathlib import Path
from validate_v2_package import validate
ROOT=Path(__file__).resolve().parent
TODAY='2026-10-07'
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha(path): return sha_bytes(path.read_bytes())
def readj(path): return json.loads(path.read_text(encoding='utf-8'))
def readl(path): return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def clean_files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'} and p.name not in {'manifest.json','SHA256SUMS'})
def payload_fingerprint():
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'} and p.name not in {'manifest.json','SHA256SUMS','VALIDATION_REPORT.json'})
    payload=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in files]
    return sha_bytes(json.dumps(payload,sort_keys=True,separators=(',',':')).encode())
previous_report_path=ROOT/'VALIDATION_REPORT.json'
previous_report=readj(previous_report_path) if previous_report_path.exists() else {}
current_payload_fingerprint=payload_fingerprint()
previous_remote=previous_report.get('remote_hf_viewer_verification')
if previous_report.get('remote_payload_fingerprint')==current_payload_fingerprint:
    remote_hf_viewer_verification=previous_remote
else:
    remote_hf_viewer_verification=None
remote_viewer_verified=bool(remote_hf_viewer_verification and remote_hf_viewer_verification.get('dataset_viewer_verified'))
remote_payload_verified=bool(remote_hf_viewer_verification and remote_hf_viewer_verification.get('dataset_payload_files_match'))
issues,stats=validate(ROOT)
if issues: raise SystemExit('Validation failed; refusing to write release metadata: '+ '; '.join(issues[:10]))
rows=readl(ROOT/'records.jsonl'); sources_doc=readj(ROOT/'sources.json'); sources={s['source_id']:s for s in sources_doc['sources']}
recommend=[r for r in rows if r['recommended_for_evaluation']]
new=[r for r in rows if r['query_id'].startswith('IICR-V20-')]
old=[r for r in rows if not r['query_id'].startswith('IICR-V20-')]
source_ids={sid for r in rows for sid in r['source_ids']}
license_alias={
 'CC-BY-3.0-IGO':'CC BY 3.0 IGO','CC BY 3.0 IGO':'CC BY 3.0 IGO',
 'CC-BY-4.0':'CC BY 4.0','CC BY 4.0':'CC BY 4.0',
 'CC-BY-SA-3.0-IGO':'CC BY-SA 3.0 IGO','CC BY-SA 3.0 IGO':'CC BY-SA 3.0 IGO',
 'CC BY-NC-SA 3.0 IGO':'CC BY-NC-SA 3.0 IGO','CC-BY-NC-SA-3.0-IGO':'CC BY-NC-SA 3.0 IGO'}
def license_counts(items): return dict(sorted(collections.Counter(license_alias.get(r['publication_rights']['record_license'],r['publication_rights']['record_license']) for r in items).items()))
def split_counts(items): return dict(collections.Counter(r['split'] for r in items))
report_families={fam for r in rows for fam in (r.get('family_ids') or ([r.get('family_id')] if r.get('family_id') else []))}
publisher_entities={e for s in sources.values() for e in s.get('publishing_institution_entities',[])}
legacy_history=readl(ROOT/'history/v1.2.0/records.jsonl')
ledger=readl(ROOT/'audit/v2_migration_ledger.jsonl')
new_families=[x for x in readj(ROOT/'audit/v2_split_manifest.json')['family_assignments']]
license_source_rechecks={sid:sources[sid].get('v2_source_file_audit_status') for sid in sorted(source_ids)}
source_file_status_counts=dict(collections.Counter(s.get('v2_source_file_audit_status','unknown') for s in sources.values()))
historical_review_counts=dict(collections.Counter(r['review_status'] for r in old))
report={
 'validation_status':'passed_with_historical_review_pending','version':'2.0.0','validated_on':TODAY,
 'record_count':len(rows),'historical_candidate_count':len(old),'new_record_count':len(new),'recommended_candidate_count':len(recommend),
 'source_document_count':len(sources),'report_family_count':len(report_families),'publisher_label_count':stats['publisher_label_count'],'publishing_institution_count':len(publisher_entities),
 'split_counts':split_counts(rows),'recommended_split_counts':split_counts(recommend),'new_family_split_counts':dict(collections.Counter(x['split'] for x in new_families)),
 'task_family_counts':dict(collections.Counter(r['task_family'] for r in rows)),'recommended_task_family_counts':dict(collections.Counter(r['task_family'] for r in recommend)),
 'answerability_counts':dict(collections.Counter(r['answerability'] for r in rows)),'recommended_answerability_counts':dict(collections.Counter(r['answerability'] for r in recommend)),
 'record_license_counts':license_counts(rows),'recommended_record_license_counts':license_counts(recommend),
 'caict_active_record_count':stats['caict_active_count'],'caict_active_record_share':stats['caict_active_share'],'history_only_caict_count':0,
 'legacy_caict_recommended_count':sum(any(sid.startswith('CAICT-') for sid in r['source_ids']) and r['recommended_for_evaluation'] for r in rows),
 'historical_rows_recommended_per_dataset_owner_instruction':True,
 'legacy_authorization_basis':'dataset_owner_confirmation_recorded_per_source_and_record',
 'target_progress':{'active_records':{'target':2000,'actual':len(rows),'shortfall':max(0,2000-len(rows))},
   'report_documents':{'target':60,'actual':len(sources),'shortfall':max(0,60-len(sources))},
   'publishing_institutions':{'target':10,'actual':len(publisher_entities),'shortfall':max(0,10-len(publisher_entities))},
   'caict_active_share':{'target_below':0.45,'actual':stats['caict_active_share'],'met':stats['caict_active_share']<0.45}},
 'historical_review_status_counts':historical_review_counts,'historical_source_file_status_counts':source_file_status_counts,
 'historical_rows_pending_source_file_revalidation':sum(r['review_status']=='pending_source_file_revalidation' for r in old),
 'new_review_status_counts':dict(collections.Counter(r['review_status'] for r in new)),
 'v1_2_records_sha256':stats['v1_2_records_sha256'],'v1_2_split_assignments_sha256':stats['v1_2_split_assignments_sha256'],
 'new_source_pdf_hashes':{sid:sources[sid]['original_report_sha256'] for sid in sorted(set(x for r in new for x in r['source_ids']))},
 'source_pdf_or_media_included':False,'human_reviewed':False,'independent_human_review':'not_performed',
 'gold_benchmark_claim':False,'prospective_blind_holdout_claim':False,'prior_system_exposure_audit':'not_performed',
 'model_performance_results_included':False,'remote_viewer_verified':remote_viewer_verified,
 'remote_payload_fingerprint':current_payload_fingerprint,
 'remote_hf_viewer_verification':remote_hf_viewer_verification,
 'duplicate_checks':{'exact_question_duplicates':stats['exact_duplicate_question_count'],'near_duplicate_pairs_at_or_above_0_82':stats['near_duplicate_pair_count_at_0_82']},
 'checks':{
   'schema_and_normalized_fields':True,'unique_ids_and_source_references':True,'record_level_license_attribution_and_sharealike':True,
   'new_source_hash_and_license_notice_pages':True,'evidence_page_bounds_and_fact_coverage':True,
   'all_833_historical_questions_answers_facts_evidence_ids_and_splits_preserved':True,
   'all_833_historical_rows_in_candidate_and_recommended_configs':True,
   'v1_2_snapshot_hashes_unchanged':True,'new_family_and_group_split_isolation':True,
   'question_only_packet_excludes_answer_fields':True,'migration_ledger_covers_833_rows':True,
   'exact_and_near_duplicate_checks':True,'candidate_and_recommended_viewer_files_match':True,
   'no_report_pdf_or_media_in_package':True,
   'remote_dataset_payload_hashes_match':remote_payload_verified},
 'pending_gates':['The 833 historical rows are included in the recommended subset per dataset-owner instruction, but their v2 content and answer-blind review remains pending; recommendation does not imply human review or gold status.']
}
if not remote_viewer_verified:
 report['pending_gates'].append('The Hugging Face Dataset Viewer counts are not verified; the current data-payload file hashes match the recorded Hub revision.' if remote_payload_verified else 'The unified payload must be synchronized to Hugging Face and its data-payload hashes and Viewer counts verified.')
(ROOT/'VALIDATION_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=clean_files()
manifest={
 'dataset_id':'chinese_internet_ict_reports_qa','dataset_name':'Chinese Internet and ICT Reports QA Dataset / 中文互联网与 ICT 报告问答数据集',
 'version':'2.0.0','created_on':TODAY,'package_status':'unified_v2_candidate_corpus_with_historical_review_pending',
 'record_count':len(rows),'historical_candidate_count':len(old),'new_record_count':len(new),'recommended_candidate_count':len(recommend),
 'source_count':len(sources),'source_document_count':len(sources),'report_family_count':len(report_families),
 'publisher_label_count':stats['publisher_label_count'],'publishing_institution_count':len(publisher_entities),
 'split_counts':split_counts(rows),'recommended_split_counts':split_counts(recommend),'task_family_counts':dict(collections.Counter(r['task_family'] for r in rows)),
 'answerability_counts':dict(collections.Counter(r['answerability'] for r in rows)),
 'record_license_counts':license_counts(rows),'recommended_record_license_counts':license_counts(recommend),
 'source_record_counts':dict(collections.Counter(sid for r in rows for sid in r['source_ids'])),
 'source_ids':sorted(source_ids),'source_file_status_counts':source_file_status_counts,
 'historical_rows_pending_source_file_revalidation':sum(r['review_status']=='pending_source_file_revalidation' for r in old),
 'historical_rows_pending_answer_blind_reconstruction':sum(r['review_status']=='pending_v2_answer_blind_reconstruction' for r in old),'source_attribution_required':True,'record_license_policy':'mixed_record_level_no_repository_wide_license',
 'dataset_license':None,'huggingface_license_metadata':'other','source_pdfs_or_media_included':False,
 'human_reviewed':False,'independent_human_review':'not_performed','gold_benchmark_claim':False,
 'pre_annotation_split_for_new_families':True,'historical_splits_assigned_after_annotation':True,
 'prospective_blind_holdout_claim':False,'prior_system_exposure_audit':'not_performed','model_performance_results_included':False,
 'caict_active_record_count':stats['caict_active_count'],'caict_active_record_share':stats['caict_active_share'],'history_only_caict_record_count':0,
 'legacy_caict_recommended_count':sum(any(sid.startswith('CAICT-') for sid in r['source_ids']) and r['recommended_for_evaluation'] for r in rows),
 'historical_rows_recommended_per_dataset_owner_instruction':True,
 'legacy_authorization_basis':'dataset_owner_confirmation_recorded_per_source_and_record',
 'target_progress':report['target_progress'],'v1_2_snapshot':{'git_tag':'v1.2.0','git_commit':'1daf3e1e9adb14223fad95dd31612c3a884b997c',
   'records_sha256':stats['v1_2_records_sha256'],'split_assignments_sha256':stats['v1_2_split_assignments_sha256']},
 'new_source_pdf_hashes':report['new_source_pdf_hashes'],'validation_report':'VALIDATION_REPORT.json',
 'viewer_layout':{'candidate_config':'candidates','recommended_config':'recommended','candidate_split_counts':split_counts(rows),'recommended_split_counts':split_counts(recommend)},
 'license_notice':'See LICENSE, LICENSES.md, LICENSE_STATUS.md, ATTRIBUTION.md, and per-record publication_rights; no single license applies.',
 'package_files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
all_files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'} and p.name!='SHA256SUMS')
(ROOT/'SHA256SUMS').write_text('\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in all_files)+'\n',encoding='utf-8')
print(f"Release metadata generated: {len(rows)} records, {len(sources)} documents, {len(publisher_entities)} institutions, {len(manifest['package_files'])} package files")
