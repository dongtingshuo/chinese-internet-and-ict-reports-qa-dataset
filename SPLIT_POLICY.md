# Split Policy — v2.2.0

The active Gold subset uses report-family and evidence-connected assignments. Records linked by the same report family or connected evidence group remain within a single split. The assignment for every active ID is in split_assignments.jsonl.

| Split | Active records |
|---|---:|
| TRAIN | 1,573 |
| DEV | 372 |
| TEST | 410 |
| **Total** | **2,355** |

These assignments were made after annotation and are not blind holdouts. Prior exposure to systems or training data has not been audited. The frozen v2.1.0 release, including its original 2,508 rows and assignments, remains under history/v2.1.0/.
