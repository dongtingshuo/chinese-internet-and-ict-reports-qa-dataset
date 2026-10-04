# Split Policy

Version 1.1.0 retains all 506 v1.0.0 record IDs and their split assignments unchanged. The 267 new records are assigned by complete report family; every new source and connected evidence group appears in exactly one split.

| Split | Legacy retained | New additions | Total |
|---|---:|---:|---:|
| TRAIN | 354 | 183 | 537 |
| DEV | 75 | 44 | 119 |
| TEST | 77 | 40 | 117 |

New source assignment:

- TRAIN: WB2014-RURAL, WB2019-WORK, WB2025-DIGITAL, ILO2020-PLATFORM, ADB2018-CITIES
- DEV: WB2016-DIGITAL, ADB2023-YOUTH
- TEST: ILO2021-PLATFORM

The split is post-annotation, not prospective or preregistered. Prior system exposure was not audited, so TEST must not be described as an unbiased blind holdout. There is one unanswerable item, retained from v1.0.0 and assigned to TEST; v1.1.0 adds no unanswerable examples.

See `split_assignments.jsonl` for the record-level audit. Legacy assignment rows are preserved byte-for-byte at the file prefix.
