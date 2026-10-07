# Split Policy — v2.0.0

## v2 source-family assignments

New report families were assigned before question drafting:

| Source family | Split |
|---|---|
| UNESCO AI and education policy guide (2021, Chinese) | TRAIN |
| UNESCO GEM 2023 technology summary (Chinese) | TRAIN |
| AREE Traditional Chinese translation of UNESCO GenAI guidance | DEV |
| FAO digital agriculture briefing (2019, Chinese) | TEST |

The six cross-document items combine only the two TRAIN UNESCO sources. The 60 new rows are distributed 42/9/9 across TRAIN/DEV/TEST.

## Historical assignments and unified counts

All 833 v1.2.0 records retain their original IDs and split values. Those splits were assigned after annotation; they are historical partitions, not prospective blind holdouts. All 833 are present in both current Viewer configurations and the recommended subset. The unified corpus and recommended subset each contain 621 TRAIN, 137 DEV, and 135 TEST records.

## Integrity checks

The validator checks family, connected-group, and source split isolation; assignment IDs and counts; all 893 current/recommended rows; and exact preservation of the 833 historical questions, answers, required facts, evidence, source IDs, and splits. It also verifies that all historical rows appear in the migration ledger and recommended subset.
