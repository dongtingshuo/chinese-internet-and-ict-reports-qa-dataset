#!/usr/bin/env python3
"""Rebuild Hugging Face candidate and recommended Viewer JSONL splits."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rows=[json.loads(x) for x in (ROOT/'records.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
files={'TRAIN':'train','DEV':'validation','TEST':'test'}
def compact(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def viewer(r):
    return {'query_id':r['query_id'],'question':r['question'],'answer_candidate':r['gold_answer'],'answerability':r['answerability'],
      'split':r['split'],'task_family':r['task_family'],'task_subtype':r['task_subtype'],'source_ids':r['source_ids'],
      'review_status':r['review_status'],'recommended_for_evaluation':r['recommended_for_evaluation'],
      'record_license':r['publication_rights']['record_license'],'record_json':compact(r)}
for split,name in files.items():
    candidates=[viewer(r) for r in rows if r['split']==split]
    recommended=[viewer(r) for r in rows if r['split']==split and r['recommended_for_evaluation']]
    (ROOT/'data'/f'candidates_{name}.jsonl').write_text('\n'.join(map(compact,candidates))+'\n',encoding='utf-8')
    dest=ROOT/'data'/'recommended'/f'{name}.jsonl'; dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text('\n'.join(map(compact,recommended))+'\n',encoding='utf-8')
print('Wrote candidate Viewer rows:',{s:sum(r['split']==s for r in rows) for s in files})
print('Wrote recommended Viewer rows:',{s:sum(r['split']==s and r['recommended_for_evaluation'] for r in rows) for s in files})
