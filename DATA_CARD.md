# Data Card — v2.2.0

## Dataset description

A unified source-grounded Chinese QA dataset about Internet, ICT, digital development, public health, labor, education technology, and related reports. The active release is the selected 2,355-record Gold subset.

## Contents and composition

- 2,355 records: 2,275 eligible v2.1.0 records and 80 passing v2.2.0 replacement records. IICR-V12-0030 was excluded for ambiguous question scope.
- Splits: TRAIN 1,573, DEV 372, TEST 410.
- 61 registered source documents, 20 report families, and 10 publishing organizations.
- Answerable/unanswerable: 2,336/19.
- Every active record includes question, answerability, answer, required facts, source evidence, split, review status, and record-level rights information.
- Source PDFs, media, and long passages are not included. The frozen v2.1.0 release remains in history/v2.1.0/.

## Creation and review

The v2.1.0 baseline contains 2,508 rows with two independent human reviews per row, as attested by the dataset owner. The AI answer-blind source audit credited 2,506 rows; two rows without credit were excluded. A third human reviewer adjudicated designated cases. Of 220 replacement proposals, 80 passed all release gates and 140 were not included.

Human reviewer identities, blindness, and no-assistance statements are owner-attested and are not supported by reviewer-signed method declarations. The review ledgers and limitations are summarized in audit/v2_2/RELEASE_AUDIT.json. The released Gold label denotes this operationally selected subset, not external certification or guaranteed zero annotation error.

## Sources and licensing

The active records use mixed record-level terms. No repository-wide license applies. Preserve publication_rights and follow the matching source attribution and adaptation requirements in sources.json. CAICT QA-record reuse authorization is owner-attested; it is separate from source-report licensing. No source PDFs or media are redistributed.

## Intended use and limitations

Use for Chinese source-grounded QA, retrieval, and evaluation research where the record's license permits. Prior system exposure has not been audited. Splits were assigned after annotation and are not blind holdouts. This release contains no retrieval baseline or model-performance results.
