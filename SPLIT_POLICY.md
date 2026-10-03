# Split Policy

All 506 query IDs are assigned to TRAIN, DEV, or TEST. Records from the same document family or connected evidence component stay in one split.

| Split | Records | Connected components |
|---|---:|---:|
| TRAIN | 354 | 9 |
| DEV | 75 | 2 |
| TEST | 77 | 2 |

The split was assigned after the questions and answers had been annotated. It is not a prospective or preregistered holdout, and prior system exposure was not audited. The only unanswerable example is in TEST; TRAIN and DEV contain none. This split cannot support strong claims about no-answer performance or serve as an unbiased blind test.
