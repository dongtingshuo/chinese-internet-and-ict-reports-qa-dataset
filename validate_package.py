#!/usr/bin/env python3
"""Validate structure, split isolation, provenance, and hashes for this package."""
import hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def package_files():
    return (p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts)
EXPECTED = {'TRAIN': 354, 'DEV': 75, 'TEST': 77}
def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)

records = jsonl(ROOT/'records.jsonl')
assignments = jsonl(ROOT/'split_assignments.jsonl')
manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
sources_doc = json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
sources = {s['source_id'] for s in sources_doc.get('sources', [])}
require(len(records)==506, f'expected 506 records, got {len(records)}')
require(len(assignments)==506, f'expected 506 assignments, got {len(assignments)}')
ids = [r.get('query_id') for r in records]
require(None not in ids and len(set(ids))==506, 'query_id missing or duplicated')
a_by_id = {a['query_id']:a for a in assignments}
require(len(a_by_id)==506 and set(ids)==set(a_by_id), 'records and split assignment IDs differ')
counts = Counter(r.get('split') for r in records)
require(dict(counts)==EXPECTED, f'unexpected split counts: {dict(counts)}')
require(manifest.get('split_counts')==EXPECTED, 'manifest split counts mismatch')
require(manifest.get('record_count')==506, 'manifest record count mismatch')
require(manifest.get('source_count')==14, 'manifest source count mismatch')
require(manifest.get('dataset_license')=='CC-BY-4.0', 'dataset license must be CC-BY-4.0')
require(manifest.get('dataset_license_url')=='https://creativecommons.org/licenses/by/4.0/', 'dataset license URL mismatch')
require(manifest.get('open_license_asserted') is True, 'package must identify its open dataset license')
require(manifest.get('source_attribution_required') is True, 'source attribution must be required')
require(manifest.get('source_pdfs_or_media_included') is False, 'original source PDFs/media must remain excluded')
require(manifest.get('human_reviewed') is False, 'package must not claim independent human review')
require(manifest.get('m3_formal_train_query_count')==0, 'legacy data must remain outside current M3 formal TRAIN')
require(manifest.get('legacy_train_query_count')==354, 'legacy TRAIN count mismatch')

group_splits = defaultdict(set)
family_splits = defaultdict(set)
source_splits = defaultdict(set)
for r in records:
    require(r.get('gold_candidate') is True, f'not marked Gold candidate: {r.get("query_id")}')
    require(r.get('split') in EXPECTED, f'invalid split: {r.get("query_id")}')
    require(bool(r.get('question')) and bool(r.get('gold_answer') is not None), f'missing QA field: {r.get("query_id")}')
    if r.get('answerability') == 'answerable':
        require(bool(r.get('gold_evidence_sets')) and bool(r.get('required_facts')), f'missing evidence/facts: {r.get("query_id")}')
    elif r.get('answerability') == 'unanswerable':
        # No-answer examples intentionally have no Required Facts; their absence evidence is retained.
        require(bool(r.get('gold_evidence_sets')), f'missing absence evidence: {r.get("query_id")}')
    else:
        require(False, f'invalid answerability label: {r.get("query_id")}')
    require(r.get('human_reviewed') is not True, f'false human-review claim: {r.get("query_id")}')
    rights = r.get('publication_rights', {})
    require(rights.get('dataset_license')=='CC-BY-4.0', f'dataset license mismatch: {r.get("query_id")}')
    require(rights.get('license_url')=='https://creativecommons.org/licenses/by/4.0/', f'license URL mismatch: {r.get("query_id")}')
    require(rights.get('status')=='licensed_under_CC_BY_4_0', f'release status mismatch: {r.get("query_id")}')
    require(rights.get('source_attribution_required') is True, f'missing source attribution requirement: {r.get("query_id")}')
    require(bool(rights.get('required_source_attributions')), f'missing source attribution: {r.get("query_id")}')
    require(all(ref.get('required_source_attribution_short_form') for ref in r.get('source_refs', [])), f'missing source citation detail: {r.get("query_id")}')
    split = r['split']
    group_splits[r['legacy_split_component_id']].add(split)
    for fid in r.get('legacy_family_ids', []):
        family_splits[fid].add(split)
    for sid in r.get('source_ids', []):
        require(sid in sources, f'unknown source_id {sid} in {r["query_id"]}')
        source_splits[sid].add(split)
    require(r['split']==a_by_id[r['query_id']]['split'], f'split assignment mismatch: {r["query_id"]}')
require(all(len(v)==1 for v in group_splits.values()), 'connected component crosses splits')
require(all(len(v)==1 for v in family_splits.values()), 'document family crosses splits')
require(all(len(v)==1 for v in source_splits.values()), 'source crosses splits')

for entry in manifest.get('package_files', []):
    p = ROOT / entry['path']
    require(p.is_file(), f'manifest file missing: {entry["path"]}')
    require(sha(p)==entry['sha256'], f'manifest hash mismatch: {entry["path"]}')
sums = ROOT/'SHA256SUMS'
if sums.exists():
    seen=set()
    for line in sums.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        digest, rel = line.split('  ',1)
        p=ROOT/rel
        require(p.is_file(), f'SHA256SUMS missing file: {rel}')
        require(sha(p)==digest, f'SHA256SUMS mismatch: {rel}')
        seen.add(rel)
    expected_files={p.relative_to(ROOT).as_posix() for p in package_files() if p.name!='SHA256SUMS'}
    require(seen==expected_files, 'SHA256SUMS file coverage mismatch')

for p in package_files():
    require(p.suffix.lower() not in {'.pdf','.png','.jpg','.jpeg','.webp'}, f'source media must not be bundled: {p.name}')
print('PASS: 506 records; frozen 354/75/77 split; group/family/source isolation; provenance; CC BY 4.0 attribution metadata; hashes')
