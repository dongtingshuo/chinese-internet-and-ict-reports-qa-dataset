# Split Policy — v2.0.0

## New source-family assignments

All 1,167 new rows follow source-family assignments made before drafting. Every source and connected group is restricted to one split. The exact source-family mapping is in `audit/v2_split_manifest.json` and `split_assignments.jsonl`.

| Split | Unified records | Recommended records |
|---|---:|---:|
| TRAIN | 1,377 | 1,377 |
| DEV | 300 | 300 |
| TEST | 323 | 323 |

This is approximately 68.9%/15.0%/16.2% overall. Source-family constraints take precedence over exact proportions.

## Historical assignments

All 833 v1.2.0 records retain their original IDs and split values. Those splits were assigned after annotation; they are historical partitions, not prospective blind holdouts. The archive under `history/v1.2.0/` preserves the original package and its hashes. All historical records remain in the unified recommended subset by dataset-owner instruction.

## Integrity checks

`validate_v2_package.py` checks unique IDs, assignment coverage, same-split source/family/connected groups, row and recommended counts, exact preservation of historical question/answer/fact/evidence/source/split fields, and the frozen v1.2.0 hashes. It also verifies each pending cloze's sentence hash after restoring the masked answer and checks the Viewer split files against the canonical records.
