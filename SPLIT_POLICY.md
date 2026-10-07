# Split Policy — v2.1.0

## v2.1 source-family assignments

The 508 v2.1 additions inherit source-family assignments established before v2.0.0 question drafting. Cross-document items share the split assigned to their linked source family, and every source/evidence-connected group stays within one split. The mapping is recorded in `audit/v2_1_split_manifest.json` and `split_assignments.jsonl`.

| Split | v2.1 additions | Unified records | Recommended records |
|---|---:|---:|---:|
| TRAIN | 304 | 1,681 | 1,681 |
| DEV | 97 | 397 | 397 |
| TEST | 107 | 430 | 430 |
| **Total** | **508** | **2,508** | **2,508** |

The v2.1 additions follow inherited report-family constraints rather than independently rebalancing source documents. The original 2,000 v2.0.0 assignments remain byte-for-byte unchanged.

## Historical assignments

The v2.0.0 corpus retains all 833 v1.2.0 records and all subsequent v2.0.0 rows with their original IDs and split values. Historical splits were assigned after annotation; they are not prospective blind holdouts. Immutable v1.2.0 and v2.0.0 packages are kept under `history/`.

## Integrity checks

`validate_v2_package.py` checks assignment coverage, source/family/connected-group isolation, all 2,000 v2.0.0 rows and assignments against the frozen v2.0.0 snapshot, v2.1 audit alignment and evidence coverage, split Viewer files, licensing metadata, duplicate questions, and package integrity.
