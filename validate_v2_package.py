#!/usr/bin/env python3
"""Dependency-free structural and release-gate checks for dataset v2.0.0."""
import collections, hashlib, json, re, sys, difflib
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def digest(data): return hashlib.sha256(data).hexdigest()
def readj(path): return json.loads(path.read_text(encoding='utf-8'))
def readl(path): return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def check(condition, message, issues):
    if not condition: issues.append(message)

def validate(root=ROOT):
    issues=[]
    rows=readl(root/'records.jsonl'); assignments=readl(root/'split_assignments.jsonl')
    sources_doc=readj(root/'sources.json'); sources={x['source_id']:x for x in sources_doc['sources']}
    schema=readj(root/'schema.json'); check(schema.get('$schema')=='https://json-schema.org/draft/2020-12/schema','schema draft marker missing',issues)
    check(schema.get('title','').endswith('v2.0.0 record'),'schema release title mismatch',issues)
    qids=[r.get('query_id') for r in rows]
    check(len(qids)==len(set(qids)),'duplicate query_id',issues)
    check(len(rows)==387,f'active row count expected 387, got {len(rows)}',issues)
    active_ids=set(qids); assignment_ids=[x.get('query_id') for x in assignments]
    check(len(assignments)==len(rows) and set(assignment_ids)==active_ids,'split assignment IDs do not match active records',issues)
    by_id={r['query_id']:r for r in rows}
    for r in rows:
        qid=r.get('query_id','?'); check(r.get('dataset_version')=='2.0.0',f'{qid}: dataset_version',issues)
        required=['task_family','task_subtype','review_status','review_provenance','recommended_for_evaluation','split_provenance','supersedes_query_id']
        check(all(k in r for k in required),f'{qid}: missing normalized v2 fields',issues)
        check(r.get('split') in {'TRAIN','DEV','TEST'},f'{qid}: invalid split',issues)
        check(bool(r.get('question')) and bool(r.get('gold_answer')),f'{qid}: empty question/answer',issues)
        check(bool(r.get('source_ids')) and bool(r.get('source_refs')),f'{qid}: missing source references',issues)
        rights=r.get('publication_rights',{})
        check(rights.get('record_license') is not None,f'{qid}: missing record license',issues)
        check(bool(rights.get('required_source_attributions')),f'{qid}: missing attribution',issues)
        src_ref={x.get('source_id'):x for x in r.get('source_refs',[])}
        obligations={x.get('source_id'):x for x in rights.get('source_license_obligations',[])}
        check(set(obligations)==set(r.get('source_ids',[])),f'{qid}: source license obligations do not match source IDs',issues)
        check(rights.get('dataset_license')==rights.get('record_license'),f'{qid}: dataset/record license normalization mismatch',issues)
        for sid in r.get('source_ids',[]):
            check(sid in sources,f'{qid}: unknown source {sid}',issues)
            check(sid in src_ref,f'{qid}: source_ref missing {sid}',issues)
            if sid in sources and sid in src_ref:
                check(src_ref[sid].get('license')==sources[sid].get('license'),f'{qid}/{sid}: source license mismatch',issues)
                ob=obligations.get(sid,{})
                check(ob.get('source_license')==sources[sid].get('license'),f'{qid}/{sid}: obligation license mismatch',issues)
                check(ob.get('required_attribution')==sources[sid].get('required_attribution'),f'{qid}/{sid}: attribution mismatch',issues)
                if 'SA' in str(sources[sid].get('license','')):
                    check(ob.get('sharealike_applies_to_adapted_record') is True,f'{qid}/{sid}: ShareAlike flag missing',issues)
        check(not any(sid.startswith('CAICT-') for sid in r.get('source_ids',[])),f'{qid}: CAICT source in active v2',issues)
        if r.get('schema_version')=='iicr_report_qa_v2_0':
            check(r.get('query_id','').startswith('IICR-V20-'),f'{qid}: new ID format',issues)
            check(r.get('human_reviewed') is False and r.get('gold_candidate') is False,f'{qid}: overclaims human/gold status',issues)
            check(r.get('recommended_for_evaluation') is True,f'{qid}: new candidate not in recommended set',issues)
            check(r.get('review_provenance',{}).get('candidate_answer_in_review_input') is False,f'{qid}: answer not hidden from review input',issues)
            check(bool(r.get('review_provenance',{}).get('prompt_sha256')),f'{qid}: missing prompt hash',issues)
            facts={x['fact_id'] for x in r.get('required_facts',[])}
            evidence=r.get('gold_evidence_sets',[])
            check(len(evidence)>0,f'{qid}: missing evidence',issues)
            cited=set()
            for es in evidence:
                check(set(es.get('required_fact_ids',[]))==facts,f'{qid}: evidence required-fact coverage mismatch',issues)
                for loc in es.get('sources',[]):
                    sid=loc.get('source_id'); cited.update(loc.get('supports_fact_ids',[]))
                    check(sid in r.get('source_ids',[]),f'{qid}: evidence cites undeclared source {sid}',issues)
                    if sid in sources:
                        check(1<=loc.get('pdf_page',0)<=sources[sid].get('source_pdf_page_count',0),f'{qid}/{sid}: evidence page outside source PDF',issues)
                    check(loc.get('locator_type')=='narrative_text_region' and bool(loc.get('element_id')),f'{qid}: evidence locator is incomplete',issues)
            check(cited==facts,f'{qid}: evidence does not cover every required fact',issues)
            for ob in rights.get('source_license_obligations',[]):
                check(ob.get('source_license')==sources.get(ob.get('source_id'),{}).get('license'),f'{qid}: source obligation license mismatch',issues)
                check(bool(ob.get('required_attribution')) and bool(ob.get('required_adaptation_disclaimer')),f'{qid}: source obligation incomplete',issues)
            check(rights.get('source_pdf_included') is False and rights.get('source_media_included') is False,f'{qid}: source material bundled',issues)
        else:
            check(r.get('schema_version') in {'iicr_report_qa_v1_1','iicr_report_qa_v1_2'},f'{qid}: unknown historical schema',issues)
            check(r.get('recommended_for_evaluation') is False,f'{qid}: historical item recommended before v2 review',issues)
            check(r.get('review_status','').startswith('pending_'),f'{qid}: historical review not pending',issues)
    split_counts=dict(collections.Counter(r['split'] for r in rows))
    rec=[r for r in rows if r.get('recommended_for_evaluation')]
    rec_counts=dict(collections.Counter(r['split'] for r in rec))
    check(len(rec)==60,f'recommended count expected 60, got {len(rec)}',issues)
    check(rec_counts=={'TRAIN':42,'DEV':9,'TEST':9},f'recommended split counts mismatch: {rec_counts}',issues)
    # Historical source families/groups and new preassigned groups must each remain in one split.
    family_splits=collections.defaultdict(set); group_splits=collections.defaultdict(set); source_splits=collections.defaultdict(set)
    for r in rows:
        for fam in r.get('family_ids') or ([r.get('family_id')] if r.get('family_id') else []): family_splits[fam].add(r['split'])
        group=r.get('connected_group_id') or r.get('legacy_split_component_id')
        if group: group_splits[group].add(r['split'])
        for sid in r.get('source_ids',[]): source_splits[sid].add(r['split'])
    for name,groups in [('family',family_splits),('connected group',group_splits),('source',source_splits)]:
        for key,splits in groups.items(): check(len(splits)==1,f'{name} spans splits: {key} -> {splits}',issues)
    # Compare historical records with immutable archive: retain IDs, wording, answers, and splits.
    archived=readl(root/'history/v1.2.0/records.jsonl'); old_active={r['query_id']:r for r in archived[506:]}
    check(len(old_active)==327,'archive licensed-prefix count mismatch',issues)
    for qid,old in old_active.items():
        now=by_id.get(qid)
        check(now is not None,f'historical candidate missing: {qid}',issues)
        if now:
            for field in ['question','gold_answer','split','required_facts','gold_evidence_sets','source_ids']:
                check(now.get(field)==old.get(field),f'{qid}: historical field changed: {field}',issues)
    old_sha=digest((root/'history/v1.2.0/records.jsonl').read_bytes())
    split_sha=digest((root/'history/v1.2.0/split_assignments.jsonl').read_bytes())
    check(old_sha=='c1885bfb779928002171d6deb9bc02c2dccd6081364202d7fe69c9fa787a21ae','v1.2.0 records snapshot hash changed',issues)
    check(split_sha=='e6ea3fa7f1eb4bf656766ac90318ffd3a98a5fead2fbfa650e7f98d76a2a8b4d','v1.2.0 assignment snapshot hash changed',issues)
    # Review packet must not reveal candidate answers and must cover the recommended IDs.
    qpacket=readl(root/'audit/v2_question_only_review.jsonl'); audit=readl(root/'audit/v2_answer_blind_reconstruction.jsonl')
    check(len(qpacket)==60 and len(audit)==60,'new review packets must cover 60 rows',issues)
    check({x['query_id'] for x in qpacket}=={r['query_id'] for r in rec},'question-only packet IDs mismatch',issues)
    check({x['query_id'] for x in audit}=={r['query_id'] for r in rec},'reconstruction audit IDs mismatch',issues)
    for x in qpacket: check('gold_answer' not in x and 'answer' not in x and 'reconstructed_answer' not in x,f"{x.get('query_id')}: answer leaked to question-only packet",issues)
    # No source PDFs/media are included, including under package history.
    media=[p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.pdf','.png','.jpg','.jpeg','.webp'} and '.git' not in p.parts]
    check(not media,f'source PDF/media files found in package: {media[:5]}',issues)
    # Canonical records and both Viewer configs must agree on rows, IDs and splits.
    for config,prefix in [('candidates','candidates_'),('recommended','recommended/')]:
        for split,filename in [('TRAIN','train'),('DEV','validation'),('TEST','test')]:
            path=root/'data'/(f'{prefix}{filename}.jsonl' if config=='candidates' else f'recommended/{filename}.jsonl')
            vr=readl(path); expected=[r for r in rows if r['split']==split and (config=='candidates' or r['recommended_for_evaluation'])]
            check(len(vr)==len(expected),f'{config}/{split}: viewer row count mismatch',issues)
            check({x['query_id'] for x in vr}=={x['query_id'] for x in expected},f'{config}/{split}: viewer IDs mismatch',issues)
    # Exact and near-duplicate checks; do not silently discard historical candidate rows.
    normalized=[re.sub(r'\W+','',r['question']).lower() for r in rows]
    exact_dupes=len(normalized)-len(set(normalized))
    new_rows=[r for r in rows if r['query_id'].startswith('IICR-V20-')]
    near_pairs=[]
    for i,a in enumerate(new_rows):
        atext=re.sub(r'\s+','',a['question'].lower())
        for b in rows:
            if b['query_id']==a['query_id']: continue
            btext=re.sub(r'\s+','',b['question'].lower())
            ratio=difflib.SequenceMatcher(None,atext,btext).ratio()
            if ratio>=0.82: near_pairs.append({'query_ids':[a['query_id'],b['query_id']],'similarity':round(ratio,3)})
    check(not near_pairs,f'near-duplicate questions >=0.82: {near_pairs[:8]}',issues)
    # New source hashes and rights pages refer to the same verified local PDF.
    for sid,src in sources.items():
        if sid.startswith(('UNESCO-AI-EDU','UNESCO-GEM-TECH','UNESCO-GENAI','FAO-DIGITAL-AGRI')):
            rh=src.get('rights_notice_location',{})
            check(src.get('source_file_sha256_verified') is True,f'{sid}: source hash was not marked verified',issues)
            check(rh.get('pdf_sha256')==src.get('original_report_sha256'),f'{sid}: rights-page hash mismatch',issues)
            check(1<=rh.get('pdf_page_1based',0)<=src.get('source_pdf_page_count',0),f'{sid}: invalid rights notice page',issues)
    # Verify the v2 migration ledger accounts for every frozen source record exactly once.
    ledger=readl(root/'audit/v2_migration_ledger.jsonl')
    check(len(ledger)==833 and len({x['query_id'] for x in ledger})==833,'migration ledger does not cover frozen 833 rows exactly once',issues)
    caict_active=sum(any(sid.startswith('CAICT-') for sid in r.get('source_ids',[])) for r in rows)
    unique_publishers={s.get('publication_institution') for s in sources.values()}
    source_families={fam for r in rows for fam in (r.get('family_ids') or ([r.get('family_id')] if r.get('family_id') else []))}
    stats={'record_count':len(rows),'historical_retained_count':len(historical_ids(rows)),'new_record_count':sum(r['query_id'].startswith('IICR-V20-') for r in rows),
      'recommended_count':len(rec),'split_counts':split_counts,'recommended_split_counts':rec_counts,'source_count':len(sources),'source_document_count':len(sources),
      'report_family_count':len(source_families),'publisher_label_count':len(unique_publishers),'publishing_institution_count':len({entity for x in sources.values() for entity in x.get('publishing_institution_entities',[]) }),'caict_active_count':caict_active,
      'caict_active_share':caict_active/max(1,len(rows)),'exact_duplicate_question_count':exact_dupes,'near_duplicate_pair_count_at_0_82':len(near_pairs),'source_media_file_count':len(media),
      'v1_2_records_sha256':old_sha,'v1_2_split_assignments_sha256':split_sha}
    return issues,stats

def historical_ids(rows): return [r for r in rows if r['query_id'].startswith('IICR-V11-') or r['query_id'].startswith('IICR-V12-')]

if __name__=='__main__':
    problems,stats=validate()
    print(json.dumps({'issues':problems,'stats':stats},ensure_ascii=False,indent=2))
    sys.exit(1 if problems else 0)
