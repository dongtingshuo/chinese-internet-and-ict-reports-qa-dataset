# Split Policy — v2.0.0

## v2 source-family assignments

New report families were assigned before question drafting:

| Source family | Split |
|---|---|
| UNESCO AI and education policy guide (2021, Chinese) | TRAIN |
| UNESCO GEM 2023 technology summary (Chinese) | TRAIN |
| AREE Traditional Chinese translation of UNESCO GenAI guidance | DEV |
| FAO digital agriculture briefing (2019, Chinese) | TEST |

The six cross-document items combine only the two TRAIN UNESCO sources. Connected groups and source families remain within one split. The 60 new rows are distributed 42/9/9.

## Historical assignments

The 327 retained v1.1/v1.2 rows keep their prior IDs and split values. Those splits were assigned after annotation. They are historical partitions, not prospective blind holdouts. Historical rows do not enter the v2 recommended subset until the v2 source and answer review is complete.

## Integrity checks

The validator checks family, source, and connected-group isolation; active and recommended row counts; and exact preservation of the historical 327 records' question, answer, facts, evidence, source IDs, and split.
