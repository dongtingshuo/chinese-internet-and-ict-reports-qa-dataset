#!/usr/bin/env python3
"""Build Hugging Face Viewer JSONL files from the canonical records."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUTS = {'TRAIN': 'train', 'DEV': 'validation', 'TEST': 'test'}
EXPECTED = {'TRAIN': 537, 'DEV': 119, 'TEST': 117}
rows = {split: [] for split in OUTPUTS}
for line in (ROOT / 'records.jsonl').read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    record = json.loads(line)
    split = record.get('split')
    if split not in rows:
        raise SystemExit(f'Invalid split: {split!r}')
    viewer_row = {
        'query_id': record['query_id'],
        'question': record['question'],
        'gold_answer': record['gold_answer'],
        'answerability': record['answerability'],
        'split': split,
        'task_type': record['task_type'],
        'record_json': json.dumps(record, ensure_ascii=False, separators=(',', ':')),
    }
    rows[split].append(json.dumps(viewer_row, ensure_ascii=False, separators=(',', ':')))
counts = {split: len(items) for split, items in rows.items()}
if counts != EXPECTED:
    raise SystemExit(f'Canonical split counts mismatch: {counts}')
for split, filename in OUTPUTS.items():
    path = ROOT / 'data' / f'{filename}.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(rows[split]) + '\n', encoding='utf-8')
print('Wrote data/train.jsonl (537), data/validation.jsonl (119), data/test.jsonl (117)')
