# Data Statement — v2.2.0

## Motivation and scope

This release supports research on Chinese question answering over Internet, ICT, digital development, public health, labor, education technology, and related reports. It includes 2,355 records with questions, answers, atomic required facts, evidence locators, split metadata, review provenance, and record-level rights.

## Language and sources

Records use registered Chinese-language sources, including institution-issued Chinese editions and summaries. The dataset does not translate English reports or redistribute source PDFs, images, tables, figures, or long source passages. The source registry records titles, URLs, hashes, rights notices, attribution, translation/adaptation statements, and third-party limitations.

## Annotation and review

The released subset contains 2,275 eligible records retained from v2.1.0 plus 80 source-grounded replacement records that passed v2.2.0 release gates. Baseline record IICR-V12-0030 is excluded because its question has multiple plausible source-supported answers. Two humans independently reviewed all 2,508 baseline rows; this method and answer-blind/no-assistance disclosure are dataset-owner-attested, not reviewer-signed. A third reviewer adjudicated designated cases. The answer-blind AI audit credited 2,506/2,508 baseline rows; the two without credit are excluded. Of 220 new replacement proposals, 140 did not pass and are absent from the active release.

Gold is a scoped operational label, not an external certification or guarantee of perfect answers. Review disclosures and counts are in audit/v2_2/RELEASE_AUDIT.json.

## Rights and redistribution

Licensing is mixed by record. Preserve publication_rights, source attribution, adaptation/translation notices, and all source-specific restrictions. No report PDF or media is redistributed. Dataset-owner-attested authorization for source-derived QA records does not assert an open license for the underlying report.

## Splits and prior exposure

Records sharing a report family or connected evidence group remain within one split. Counts are TRAIN 1,573, DEV 372, and TEST 410. Splits are historical, post-annotation assignments, not blind holdouts; prior system exposure has not been audited.
