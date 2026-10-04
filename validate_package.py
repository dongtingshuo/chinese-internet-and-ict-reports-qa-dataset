#!/usr/bin/env python3
"""Validate the v1.1.0 package, frozen legacy prefix, source rights, splits and hashes."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD_RECORDS = 506
NEW_RECORDS = 267
TOTAL_RECORDS = OLD_RECORDS + NEW_RECORDS
OLD_RECORD_PREFIX_SHA256 = '7d4d3028b06c7926515607ecb9ad596984a74feccc91a0cea5fac2dc23fc6a6a'
OLD_SPLIT_PREFIX_SHA256 = 'fe3ef765e94f142bcf4c40d4d1011b1c1cd42520b99ab7361421636b6add670e'
OLD_LICENSE_SHA256 = '9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411'
EXPECTED_SPLITS = {'TRAIN': 537, 'DEV': 119, 'TEST': 117}
EXPECTED_ADDITIONS = {'TRAIN': 183, 'DEV': 44, 'TEST': 40}
EXPECTED_NEW_SOURCES = {
    'WB2014-RURAL', 'WB2016-DIGITAL', 'WB2019-WORK', 'WB2025-DIGITAL',
    'ILO2020-PLATFORM', 'ILO2021-PLATFORM', 'ADB2018-CITIES', 'ADB2023-YOUTH',
}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def package_files():
    return (
        p for p in ROOT.rglob('*')
        if p.is_file() and '.git' not in p.relative_to(ROOT).parts
        and '__pycache__' not in p.relative_to(ROOT).parts
    )


records_path = ROOT / 'records.jsonl'
assignments_path = ROOT / 'split_assignments.jsonl'
record_lines = records_path.read_bytes().splitlines(keepends=True)
assignment_lines = assignments_path.read_bytes().splitlines(keepends=True)
require(len(record_lines) == TOTAL_RECORDS, f'expected {TOTAL_RECORDS} record lines, got {len(record_lines)}')
require(len(assignment_lines) == TOTAL_RECORDS, f'expected {TOTAL_RECORDS} assignment lines, got {len(assignment_lines)}')
require(digest(b''.join(record_lines[:OLD_RECORDS])) == OLD_RECORD_PREFIX_SHA256, 'legacy records prefix changed')
require(digest(b''.join(assignment_lines[:OLD_RECORDS])) == OLD_SPLIT_PREFIX_SHA256, 'legacy split prefix changed')
require(sha(ROOT / 'LICENSE-CC-BY-4.0.txt') == OLD_LICENSE_SHA256, 'legacy CC BY 4.0 license text changed')

records = [json.loads(line) for line in record_lines]
assignments = [json.loads(line) for line in assignment_lines]
manifest = read_json(ROOT / 'manifest.json')
sources_doc = read_json(ROOT / 'sources.json')
sources_list = sources_doc.get('sources', [])
sources = {s['source_id']: s for s in sources_list}
require(len(sources_list) == 22 and len(sources) == 22, 'source catalog must have 22 unique sources')
require(sources_doc.get('source_count') == 22, 'source registry count mismatch')
require(sources_doc.get('dataset_version') == '1.1.0', 'source registry version mismatch')
require(manifest.get('version') == '1.1.0', 'manifest must identify version 1.1.0')
require(manifest.get('record_count') == TOTAL_RECORDS, 'manifest record count mismatch')
require(manifest.get('legacy_record_count') == OLD_RECORDS, 'manifest legacy record count mismatch')
require(manifest.get('v1_1_record_count') == NEW_RECORDS, 'manifest v1.1 record count mismatch')
require(manifest.get('source_count') == 22, 'manifest source count mismatch')
require(manifest.get('v1_1_source_count') == 8, 'manifest new source count mismatch')
require(manifest.get('split_counts') == EXPECTED_SPLITS, 'manifest split counts mismatch')
require(manifest.get('v1_1_split_counts') == EXPECTED_ADDITIONS, 'manifest addition split counts mismatch')
require(manifest.get('answerability_counts') == {'answerable': 772, 'unanswerable': 1}, 'manifest answerability counts mismatch')
require(manifest.get('dataset_license') == 'mixed_record_level', 'manifest must declare mixed record-level licensing')
require(manifest.get('source_pdfs_or_media_included') is False, 'source PDFs/media must remain excluded')
require(manifest.get('human_reviewed') is False, 'package must not claim independent human review')
require(manifest.get('v1_0_records_and_splits_unchanged') is True, 'manifest must assert frozen legacy rows and splits')
require(manifest.get('open_license_asserted') is True, 'manifest must identify the open license components')

record_ids = [r.get('query_id') for r in records]
require(None not in record_ids and len(set(record_ids)) == TOTAL_RECORDS, 'query IDs missing or duplicated')
new_records = records[OLD_RECORDS:]
require(all(r.get('schema_version') == 'iicr_report_qa_v1_1' for r in new_records), 'new record schema version mismatch')
require(all(r.get('query_id', '').startswith('IICR-V11-') for r in new_records), 'new record ID prefix mismatch')
require([r['query_id'] for r in new_records] == [f'IICR-V11-{n:04d}' for n in range(1, NEW_RECORDS + 1)], 'new record IDs must be contiguous and stable')
require(len({r['question'] for r in new_records}) == NEW_RECORDS, 'new questions contain duplicates')

# The 2019 report's printed page 37 is physical PDF page 49.
for qid in ('IICR-V11-0079', 'IICR-V11-0080', 'IICR-V11-0081', 'IICR-V11-0082', 'IICR-V11-0083'):
    row = next(r for r in new_records if r['query_id'] == qid)
    locator = row['gold_evidence_sets'][0]['sources'][0]
    require(row.get('source_ids') == ['WB2019-WORK'], f'printed-page correction source mismatch: {qid}')
    require(locator.get('pdf_page') == 49 and locator.get('printed_page') == 37, f'printed/PDF page mapping mismatch: {qid}')
    expected_element = 'wb2019-work-p0049-narrative'
    require(locator.get('element_id') == expected_element, f'printed-page correction element mismatch: {qid}')
    require(row['gold_quality']['required_facts_review'][0].get('cited_element_ids') == [expected_element], f'printed-page review locator mismatch: {qid}')

assign_by_id = {a['query_id']: a for a in assignments}
require(len(assign_by_id) == TOTAL_RECORDS and set(record_ids) == set(assign_by_id), 'records and assignments IDs differ')
record_counts = Counter(r.get('split') for r in records)
new_counts = Counter(r.get('split') for r in new_records)
require(dict(record_counts) == EXPECTED_SPLITS, f'unexpected total split counts: {dict(record_counts)}')
require(dict(new_counts) == EXPECTED_ADDITIONS, f'unexpected added split counts: {dict(new_counts)}')

all_group_splits = defaultdict(set)
all_family_splits = defaultdict(set)
all_source_splits = defaultdict(set)
for i, r in enumerate(records):
    qid = r['query_id']
    a = assign_by_id[qid]
    split = r.get('split')
    require(split in EXPECTED_SPLITS, f'invalid split on {qid}')
    require(a.get('split') == split, f'assignment mismatch on {qid}')
    require(r.get('gold_candidate') is True, f'missing candidate marker on {qid}')
    require(r.get('question') and isinstance(r.get('gold_answer'), str) and r.get('gold_answer'), f'empty QA on {qid}')
    require(r.get('answerability') in {'answerable', 'unanswerable'}, f'invalid answerability on {qid}')
    if r['answerability'] == 'answerable':
        require(r.get('required_facts') and r.get('gold_evidence_sets'), f'answerable row lacks facts/evidence: {qid}')
    else:
        require(r.get('gold_evidence_sets'), f'unanswerable row lacks absence evidence: {qid}')
    quality = r.get('gold_quality', {})
    require(quality.get('human_reviewed') is not True, f'human review overclaim on {qid}')
    component = r.get('legacy_split_component_id') if i < OLD_RECORDS else r.get('connected_group_id')
    if component:
        all_group_splits[component].add(split)
    fams = r.get('legacy_family_ids') or ([r['family_id']] if r.get('family_id') else [])
    for family in fams:
        all_family_splits[family].add(split)
    for sid in r.get('source_ids', []):
        require(sid in sources, f'unknown source {sid} on {qid}')
        all_source_splits[sid].add(split)
    require(a.get('source_ids') == r.get('source_ids'), f'assignment source metadata mismatch on {qid}')
    if i < OLD_RECORDS:
        require(r['schema_version'] == 'legacy_main_domain_gold_candidate_record_v1', f'legacy row changed schema: {qid}')
    else:
        require(r.get('human_reviewed') is False, f'new row must explicitly set human_reviewed=false: {qid}')
        require(r.get('split_assignment_version') == 'dataset_split_v1_1', f'new split version mismatch: {qid}')
        require(r.get('answerability') == 'answerable', f'new rows must be answerable: {qid}')
        require(r.get('modality_tags') == ['text'], f'new rows must be text-based: {qid}')
        require(quality.get('source_support_status') == 'source_verified_candidate', f'new source status mismatch: {qid}')
        require(quality.get('independent_human_double_annotation') == 'not_performed', f'new review provenance mismatch: {qid}')
        rights = r.get('publication_rights', {})
        require(rights.get('dataset_license') == 'CC-BY-3.0-IGO', f'new record license mismatch: {qid}')
        require(rights.get('license_url') == 'https://creativecommons.org/licenses/by/3.0/igo/', f'new license URL mismatch: {qid}')
        require(rights.get('status') == 'licensed_under_CC_BY_3_0_IGO', f'new rights status mismatch: {qid}')
        require(rights.get('source_attribution_required') is True, f'attribution flag missing: {qid}')
        require(rights.get('required_source_attributions') and rights.get('required_adaptation_disclaimer'), f'required attribution/disclaimer missing: {qid}')
        require(rights.get('modification_notice') and rights.get('third_party_content_reused') is False, f'modification/third-party field mismatch: {qid}')
        require(rights.get('source_excerpt_included') is False and rights.get('source_media_included') is False and rights.get('source_pdf_included') is False, f'source text or media included flag mismatch: {qid}')
        require(len(r.get('source_ids', [])) == 1 and len(r.get('source_refs', [])) == 1, f'new rows must identify exactly one source: {qid}')
        sid = r['source_ids'][0]
        require(sid in EXPECTED_NEW_SOURCES, f'unexpected new source ID on {qid}: {sid}')
        src = sources[sid]
        ref = r['source_refs'][0]
        require(ref.get('source_id') == sid, f'source reference mismatch: {qid}')
        require(ref.get('license_id') == 'CC-BY-3.0-IGO' and ref.get('license_url') == rights['license_url'], f'source license reference mismatch: {qid}')
        for ref_field, source_field in (
            ('publisher', 'publisher'),
            ('title', 'title_chinese'),
            ('title_english', 'title_english'),
            ('text_language', 'text_language'),
            ('translation_status', 'translation_status'),
            ('official_pdf_url', 'original_report_url'),
            ('official_publication_page_url', 'official_publication_page_url'),
            ('source_pdf_sha256', 'original_report_sha256'),
            ('pdf_page_count', 'source_pdf_page_count'),
            ('rights_holder', 'rights_holder'),
            ('license', 'license'),
            ('rights_notice_location', 'rights_notice_location'),
            ('required_source_attribution_short_form', 'required_attribution'),
            ('required_adaptation_disclaimer', 'required_adaptation_disclaimer'),
            ('translation_disclaimer', 'translation_disclaimer'),
            ('third_party_content_limitations', 'third_party_content_limitations'),
        ):
            require(ref.get(ref_field) == src.get(source_field), f'{ref_field} differs from source registry: {qid}')
        require(ref.get('source_pdf_sha256') == src.get('original_report_sha256'), f'source file hash mismatch: {qid}')
        require(ref.get('official_pdf_url') == src.get('original_report_url'), f'source file URL mismatch: {qid}')
        require(ref.get('required_source_attribution_short_form') == src.get('required_attribution'), f'attribution mismatch: {qid}')
        require(rights.get('required_source_attributions') == [src.get('required_attribution')], f'package attribution mismatch: {qid}')
        require(rights.get('required_adaptation_disclaimer') == src.get('required_adaptation_disclaimer'), f'adaptation disclaimer mismatch: {qid}')
        require(rights.get('translation_disclaimer') == src.get('translation_disclaimer'), f'translation disclaimer mismatch: {qid}')
        require(ref.get('source_pdf_included') is False, f'new source PDF included: {qid}')
        for evidence in r.get('gold_evidence_sets', []):
            fact_ids = {f.get('fact_id') for f in r.get('required_facts', [])}
            require(set(evidence.get('required_fact_ids', [])) <= fact_ids, f'evidence references unknown fact on {qid}')
            for loc in evidence.get('sources', []):
                require(loc.get('source_id') == sid, f'evidence points to wrong source on {qid}')
                require(isinstance(loc.get('pdf_page'), int) and 1 <= loc['pdf_page'] <= src['source_pdf_page_count'], f'invalid page locator on {qid}')
                require(loc.get('supports_fact_ids') and set(loc['supports_fact_ids']) <= fact_ids, f'bad locator fact mapping on {qid}')

require(all(len(v) == 1 for v in all_group_splits.values()), 'connected evidence group crosses splits')
require(all(len(v) == 1 for v in all_family_splits.values()), 'report family crosses splits')
require(all(len(v) == 1 for v in all_source_splits.values()), 'source crosses splits')

def counts_by_split(groups):
    return dict(Counter(next(iter(split_set)) for split_set in groups.values()))

require(counts_by_split(all_group_splits) == manifest.get('connected_component_counts'), 'manifest connected-component counts mismatch')
require(counts_by_split(all_family_splits) == manifest.get('family_counts'), 'manifest family counts mismatch')
require(counts_by_split(all_source_splits) == manifest.get('source_counts'), 'manifest source-per-split counts mismatch')

new_source_ids = {sid for r in new_records for sid in r['source_ids']}
require(new_source_ids == EXPECTED_NEW_SOURCES, 'not all eight new sources are represented')
new_publishers = {sources[sid]['publication_institution'] for sid in new_source_ids}
require(len(new_publishers) >= 3, 'new sources must cover at least three publishers')
new_source_counts = Counter(sid for r in new_records for sid in r['source_ids'])
require(dict(new_source_counts) == manifest.get('v1_1_source_record_counts'), 'manifest per-source record counts mismatch')
require(sorted(new_publishers) == sorted(manifest.get('v1_1_source_publishers', [])), 'manifest new publisher list mismatch')
for sid in EXPECTED_NEW_SOURCES:
    s = sources[sid]
    require(s.get('license_id') == 'CC-BY-3.0-IGO', f'wrong license in source registry: {sid}')
    require(s.get('license_url') == 'https://creativecommons.org/licenses/by/3.0/igo/', f'wrong license URL in registry: {sid}')
    require(len(s.get('original_report_sha256', '')) == 64, f'missing source PDF SHA-256: {sid}')
    require(s.get('source_pdf_included') is False, f'source PDF included in registry: {sid}')
    require(s.get('rights_notice_location', {}).get('pdf_page_1based'), f'missing rights notice page: {sid}')
    require(s.get('required_attribution') and s.get('required_adaptation_disclaimer'), f'missing rights wording: {sid}')
    require(s.get('third_party_content_limitations'), f'missing third-party restriction: {sid}')
    require(s.get('publication_institution') in {'World Bank', 'International Labour Organization', 'Asian Development Bank'}, f'unexpected publisher: {sid}')
    require(len(s.get('original_report_sha256', '')) == 64 and s.get('source_pdf_page_count', 0) > 0, f'invalid source hash/page count: {sid}')
    require(s.get('original_report_url', '').startswith('https://') and s.get('official_publication_page_url', '').startswith('https://'), f'missing official source URLs: {sid}')

schema = read_json(ROOT / 'schema.json')
require(schema.get('$schema') == 'https://json-schema.org/draft/2020-12/schema', 'schema dialect mismatch')
require({'legacy_v1_0', 'iicr_report_qa_v1_1'} <= set(schema.get('$defs', {})), 'schema must define both record versions')
require(len(schema.get('oneOf', [])) == 2, 'schema must accept exactly the legacy and v1.1 record families')

viewer_expected = {'train': 'TRAIN', 'validation': 'DEV', 'test': 'TEST'}
for filename, split in viewer_expected.items():
    path = ROOT / 'data' / f'{filename}.jsonl'
    rows = jsonl(path)
    canonical = {r['query_id']: r for r in records if r['split'] == split}
    require(len(rows) == len(canonical), f'Viewer {filename} count mismatch')
    ids = set()
    for row in rows:
        qid = row.get('query_id')
        require(qid in canonical and qid not in ids, f'Viewer row missing/duplicated: {filename}/{qid}')
        ids.add(qid)
        require(row.get('split') == split, f'Viewer split label mismatch: {qid}')
        require(json.loads(row.get('record_json', '{}')) == canonical[qid], f'Viewer record JSON mismatch: {qid}')
        require(row.get('question') == canonical[qid]['question'] and row.get('gold_answer') == canonical[qid]['gold_answer'], f'Viewer field mismatch: {qid}')

for entry in manifest.get('package_files', []):
    p = ROOT / entry['path']
    require(p.is_file(), f'manifest file missing: {entry["path"]}')
    require(sha(p) == entry['sha256'], f'manifest hash mismatch: {entry["path"]}')
    require(p.stat().st_size == entry['bytes'], f'manifest byte count mismatch: {entry["path"]}')

sums = ROOT / 'SHA256SUMS'
seen = set()
for line in sums.read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    digest_value, rel = line.split('  ', 1)
    p = ROOT / rel
    require(p.is_file(), f'SHA256SUMS missing file: {rel}')
    require(sha(p) == digest_value, f'SHA256SUMS mismatch: {rel}')
    seen.add(rel)
expected_files = {p.relative_to(ROOT).as_posix() for p in package_files() if p.name != 'SHA256SUMS'}
require(seen == expected_files, 'SHA256SUMS file coverage mismatch')
for p in package_files():
    require(p.suffix.lower() not in {'.pdf', '.png', '.jpg', '.jpeg', '.webp', '.gif'}, f'source media must remain excluded: {p.name}')

print('PASS: v1.1.0 package; 773 records; frozen v1.0.0 rows/splits; +267 source-verified candidates; 22 sources; 3 new publishers; report/source/group split isolation; per-record CC BY 3.0 IGO attribution; HF Viewer counts and JSON parity; package hashes.')
