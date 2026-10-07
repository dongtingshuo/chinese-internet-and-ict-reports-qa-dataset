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
    check(len(rows)>=2000,f'active row count must meet the v2 target of 2000, got {len(rows)}',issues)
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
        if any(sid.startswith('CAICT-') for sid in r.get('source_ids',[])):
            check(rights.get('record_license') in {'CC-BY-4.0','CC BY 4.0'},f'{qid}: legacy CAICT record license was not preserved',issues)
            check(rights.get('reuse_permission_status')=='dataset_owner_confirmed_authorized',f'{qid}: owner authorization attestation missing',issues)
            check(r.get('recommended_for_evaluation') is True,f'{qid}: owner-authorized legacy item missing from recommendation',issues)
            for sid in r.get('source_ids',[]):
                if sid.startswith('CAICT-'):
                    check(sources.get(sid,{}).get('record_reuse_authorization',{}).get('status')=='dataset_owner_confirmed_authorized',f'{qid}/{sid}: source registry authorization attestation missing',issues)
                    check(sources.get(sid,{}).get('license') is None,f'{qid}/{sid}: a source-report license was asserted for legacy CAICT',issues)
        if r.get('schema_version')=='iicr_report_qa_v2_0':
            check(r.get('query_id','').startswith('IICR-V20-'),f'{qid}: new ID format',issues)
            check(r.get('human_reviewed') is False and r.get('gold_candidate') is False,f'{qid}: overclaims human/gold status',issues)
            check(r.get('recommended_for_evaluation') is True,f'{qid}: new candidate not in recommended set',issues)
            pending=r.get('review_status')=='pending_ai_content_verification'
            if pending:
                check(r.get('review_provenance',{}).get('candidate_answer_in_review_input') is True,f'{qid}: pending cloze provenance must disclose answer-visible generation',issues)
                check(r.get('recommended_for_evaluation') is True,f'{qid}: pending item not retained in recommended subset',issues)
                check(r.get('publication_rights',{}).get('source_excerpt_included') is True,f'{qid}: cloze excerpt disclosure missing',issues)
                check(r.get('publication_rights',{}).get('third_party_content_reused') is None,f'{qid}: pending attribution status is overstated',issues)
                question=r.get('question','')
                check(question.count('______')==1,f'{qid}: pending cloze question must have one answer slot',issues)
                check(r.get('gold_answer','') not in question,f'{qid}: candidate answer remains visible in cloze question',issues)
                check(r.get('task_family')=='single_document_retrieval' and 'cloze' in r.get('task_subtype',''),f'{qid}: cloze task family/subtype mismatch',issues)
                check(r.get('review_provenance',{}).get('model') is None and r.get('review_provenance',{}).get('prompt_sha256') is None,f'{qid}: rule-based generation is mislabeled as per-row model review',issues)
                script_path=root/r.get('review_provenance',{}).get('generation_script','')
                check(script_path.is_file(),f'{qid}: cloze generation script missing',issues)
                if script_path.is_file():
                    check(digest(script_path.read_bytes())==r.get('review_provenance',{}).get('generation_script_sha256'),f'{qid}: cloze generation script hash mismatch',issues)
                source_hash=r.get('source_sentence_sha256')
                check(bool(re.fullmatch(r'[a-f0-9]{64}',str(source_hash))),f'{qid}: source sentence hash missing or invalid',issues)
                if question.count('______')==1 and source_hash:
                    quoted=question.split('“',1)[-1].rsplit('”',1)[0]
                    restored=quoted.replace('______',r['gold_answer'])
                    check(digest(restored.encode('utf-8'))==source_hash,f'{qid}: reconstructed sentence does not match its source sentence hash',issues)
            else:
                check(r.get('review_provenance',{}).get('candidate_answer_in_review_input') is False,f'{qid}: answer not hidden from review input',issues)
                check(bool(r.get('review_provenance',{}).get('prompt_sha256')),f'{qid}: missing answer-blind reconstruction prompt hash',issues)
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
                    check(loc.get('locator_type') in {'narrative_text_region','source_sentence_cloze'} and bool(loc.get('element_id')),f'{qid}: evidence locator is incomplete',issues)
            check(cited==facts,f'{qid}: evidence does not cover every required fact',issues)
            for ob in rights.get('source_license_obligations',[]):
                check(ob.get('source_license')==sources.get(ob.get('source_id'),{}).get('license'),f'{qid}: source obligation license mismatch',issues)
                check(bool(ob.get('required_attribution')) and bool(ob.get('required_adaptation_disclaimer')),f'{qid}: source obligation incomplete',issues)
            check(rights.get('source_pdf_included') is False and rights.get('source_media_included') is False,f'{qid}: source material bundled',issues)
        else:
            check(r.get('schema_version') in {'iicr_report_qa_v1_1','iicr_report_qa_v1_2','legacy_main_domain_gold_candidate_record_v1'},f'{qid}: unknown historical schema',issues)
            check(r.get('recommended_for_evaluation') is True,f'{qid}: historical item missing from unified recommended subset',issues)
            check(r.get('review_status','').startswith('pending_'),f'{qid}: historical review not pending',issues)
    split_counts=dict(collections.Counter(r['split'] for r in rows))
    rec=[r for r in rows if r.get('recommended_for_evaluation')]
    rec_counts=dict(collections.Counter(r['split'] for r in rec))
    check(len(rec)==len(rows),f'recommended subset must contain all active rows, got {len(rec)}/{len(rows)}',issues)
    check(rec_counts==split_counts,f'recommended split counts mismatch: {rec_counts} vs {split_counts}',issues)
    # Historical source families/groups and new preassigned groups must each remain in one split.
    family_splits=collections.defaultdict(set); group_splits=collections.defaultdict(set); source_splits=collections.defaultdict(set)
    for r in rows:
        for fam in r.get('family_ids') or ([r.get('family_id')] if r.get('family_id') else []): family_splits[fam].add(r['split'])
        group=r.get('connected_group_id') or r.get('legacy_split_component_id')
        if group: group_splits[group].add(r['split'])
        for sid in r.get('source_ids',[]): source_splits[sid].add(r['split'])
    for name,groups in [('family',family_splits),('connected group',group_splits),('source',source_splits)]:
        for key,splits in groups.items(): check(len(splits)==1,f'{name} spans splits: {key} -> {splits}',issues)
    # Compare all 833 historical records with the immutable archive; only release metadata is normalized.
    archived=readl(root/'history/v1.2.0/records.jsonl'); historical={r['query_id']:r for r in archived}
    check(len(historical)==833,'archive row count mismatch',issues)
    for qid,old in historical.items():
        now=by_id.get(qid)
        check(now is not None,f'historical record missing from unified corpus: {qid}',issues)
        if now:
            for field in ['question','gold_answer','split','required_facts','gold_evidence_sets','source_ids']:
                check(now.get(field)==old.get(field),f'{qid}: historical field changed: {field}',issues)
            check(now.get('recommended_for_evaluation') is True,f'{qid}: historical record excluded from recommendation',issues)
            check(now.get('human_reviewed') is False,f'{qid}: historical human-review status changed',issues)
    old_sha=digest((root/'history/v1.2.0/records.jsonl').read_bytes())
    split_sha=digest((root/'history/v1.2.0/split_assignments.jsonl').read_bytes())
    check(old_sha=='c1885bfb779928002171d6deb9bc02c2dccd6081364202d7fe69c9fa787a21ae','v1.2.0 records snapshot hash changed',issues)
    check(split_sha=='e6ea3fa7f1eb4bf656766ac90318ffd3a98a5fead2fbfa650e7f98d76a2a8b4d','v1.2.0 assignment snapshot hash changed',issues)
    # Review packet must not reveal candidate answers and must cover the recommended IDs.
    qpacket=readl(root/'audit/v2_question_only_review.jsonl'); audit=readl(root/'audit/v2_answer_blind_reconstruction.jsonl')
    pending_audit=readl(root/'audit/v2_pending_content_review.jsonl')
    new_ids={r['query_id'] for r in rows if r['query_id'].startswith('IICR-V20-')}
    reviewed_ids={r['query_id'] for r in rows if r['query_id'].startswith('IICR-V20-') and r['review_status']=='ai_answer_blind_reconstruction_match'}
    pending_ids={r['query_id'] for r in rows if r['query_id'].startswith('IICR-V20-') and r['review_status']=='pending_ai_content_verification'}
    check(len(qpacket)==len(new_ids) and {x['query_id'] for x in qpacket}==new_ids,'question-only packet IDs mismatch',issues)
    check({x['query_id'] for x in audit}==reviewed_ids,f'answer-blind reconstruction audit ID mismatch: {len(audit)} vs {len(reviewed_ids)}',issues)
    check({x['query_id'] for x in pending_audit}==pending_ids,f'pending content audit ID mismatch: {len(pending_audit)} vs {len(pending_ids)}',issues)
    pending_audit_by_id={x['query_id']:x for x in pending_audit}
    for qid in pending_ids:
        record=by_id.get(qid,{}); audit=pending_audit_by_id.get(qid,{})
        check(audit.get('source_sentence_sha256')==record.get('source_sentence_sha256'),f'{qid}: pending audit/source sentence hash mismatch',issues)
        check(audit.get('evidence_page')==record.get('gold_evidence_sets',[{}])[0].get('sources',[{}])[0].get('pdf_page'),f'{qid}: pending audit/evidence page mismatch',issues)
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
    # Use a character 4-gram index to shortlist plausible matches before the slower
    # SequenceMatcher check. This keeps the release audit practical at 2k+ rows.
    normalized_questions=[re.sub(r'\W+','',r['question']).lower() for r in rows]
    grams=[{value[i:i+4] for i in range(max(0,len(value)-3))} for value in normalized_questions]
    gram_rows=collections.defaultdict(list)
    for idx,values in enumerate(grams):
        for value in values: gram_rows[value].append(idx)
    pair_overlap=collections.Counter()
    new_indexes={idx for idx,r in enumerate(rows) if r['query_id'].startswith('IICR-V20-')}
    for value,indexes in gram_rows.items():
        if len(indexes)>100: continue
        relevant=[idx for idx in indexes if idx in new_indexes]
        if len(relevant)==0: continue
        for i in relevant:
            for j in indexes:
                if i<j: pair_overlap[(i,j)]+=1
                elif j<i: pair_overlap[(j,i)]+=1
    near_pairs=[]
    for (i,j),overlap in pair_overlap.items():
        minimum=min(len(grams[i]),len(grams[j]))
        if overlap<max(3,int(minimum*0.20)): continue
        ratio=difflib.SequenceMatcher(None,normalized_questions[i],normalized_questions[j]).ratio()
        if ratio>=0.82: near_pairs.append({'query_ids':[rows[i]['query_id'],rows[j]['query_id']],'similarity':round(ratio,3)})
    check(not near_pairs,f'near-duplicate questions >=0.82: {near_pairs[:8]}',issues)
    # New source hashes and rights pages refer to the same verified local PDF.
    expansion_doc=readj(root/'audit/v2_expansion_sources.json')
    expansion_sources={s['source_id']:s for s in expansion_doc.get('sources',[])}
    check(len(expansion_sources)==32,f'expected 32 added source documents, got {len(expansion_sources)}',issues)
    for sid,src in expansion_sources.items():
        actual=sources.get(sid,{})
        rh=actual.get('rights_notice_location',{})
        check(actual.get('source_file_sha256_verified') is True,f'{sid}: source hash was not marked verified',issues)
        check(bool(re.fullmatch(r'[a-f0-9]{64}',str(src.get('extracted_text_sha256','')))),f'{sid}: extracted-text hash missing from expansion provenance',issues)
        check(actual.get('extracted_text_sha256')==src.get('extracted_text_sha256'),f'{sid}: extracted-text hash missing from source registry',issues)
        check(rh.get('pdf_sha256')==actual.get('original_report_sha256'),f'{sid}: rights-page hash mismatch',issues)
        check(1<=rh.get('pdf_page_1based',0)<=actual.get('source_pdf_page_count',0),f'{sid}: invalid rights notice page',issues)
        check(actual.get('license')=='CC BY-NC-SA 3.0 IGO',f'{sid}: unexpected license or missing license review',issues)
        check(bool(actual.get('required_attribution')) and bool(actual.get('required_adaptation_disclaimer')),f'{sid}: attribution/adaptation terms missing',issues)
        check(actual.get('source_pdf_included') is False,f'{sid}: source PDF declared as bundled',issues)
        src_rows=[r for r in rows if sid in r.get('source_ids',[])]
        check(len(src_rows)==src.get('target_records'),f'{sid}: source question count {len(src_rows)} != planned {src.get("target_records")}',issues)
        check(all(r['split']==src.get('preassigned_split') for r in src_rows),f'{sid}: source questions do not follow preassigned split',issues)
    # Verify the v2 migration ledger accounts for every frozen source record exactly once.
    ledger=readl(root/'audit/v2_migration_ledger.jsonl')
    check(len(ledger)==833 and len({x['query_id'] for x in ledger})==833,'migration ledger does not cover frozen 833 rows exactly once',issues)
    check(all(x.get('active_v2') is True and x.get('recommended_for_evaluation') is True for x in ledger),'migration ledger marks an old row inactive or unrecommended',issues)
    caict_active=sum(any(sid.startswith('CAICT-') for sid in r.get('source_ids',[])) for r in rows)
    unique_publishers={s.get('publication_institution') for s in sources.values()}
    source_families={fam for r in rows for fam in (r.get('family_ids') or ([r.get('family_id')] if r.get('family_id') else []))}
    stats={'record_count':len(rows),'historical_retained_count':len(historical_ids(rows)),'new_record_count':sum(r['query_id'].startswith('IICR-V20-') for r in rows),
      'recommended_count':len(rec),'split_counts':split_counts,'recommended_split_counts':rec_counts,'source_count':len(sources),'source_document_count':len(sources),
      'report_family_count':len(source_families),'publisher_label_count':len(unique_publishers),'publishing_institution_count':len({entity for x in sources.values() for entity in x.get('publishing_institution_entities',[]) }),'caict_active_count':caict_active,
      'caict_active_share':caict_active/max(1,len(rows)),'exact_duplicate_question_count':exact_dupes,'near_duplicate_pair_count_at_0_82':len(near_pairs),'source_media_file_count':len(media),
      'v1_2_records_sha256':old_sha,'v1_2_split_assignments_sha256':split_sha}
    return issues,stats

def historical_ids(rows): return [r for r in rows if not r['query_id'].startswith('IICR-V20-')]

if __name__=='__main__':
    problems,stats=validate()
    print(json.dumps({'issues':problems,'stats':stats},ensure_ascii=False,indent=2))
    sys.exit(1 if problems else 0)
