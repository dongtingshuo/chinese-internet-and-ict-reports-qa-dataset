# Split Policy

Version 1.2.0 retains the v1.0.0 and v1.1.0 records and split assignments unchanged. The 60 v1.2.0 records are grouped by report family and evidence-connected group. Every source, report family, and connected group is assigned to one split only.

| Split | v1.0.0 retained | v1.1.0 additions | v1.2.0 additions | Total |
|---|---:|---:|---:|---:|
| TRAIN | 354 | 183 | 42 | 579 |
| DEV | 75 | 44 | 9 | 128 |
| TEST | 77 | 40 | 9 | 126 |

Each v1.2.0 task type has the same allocation: TRAIN 14, DEV 3, TEST 3. This places no-answer, cross-document, and table/figure candidates in TEST while preserving source and evidence-group isolation. Cross-document sources are kept together in one split.

The assignment happened after annotation. It is not prospective, preregistered, or a blind holdout; prior system exposure was not audited. The package has 21 unanswerable records overall: one retained legacy record and 20 new candidate records. The 20 new candidates include their report/page search scope and nearby evidence but have not received independent human adjudication.

See `split_assignments.jsonl` for the record-level audit. The original v1.0.0 and v1.1.0 assignment prefixes are preserved byte-for-byte.
