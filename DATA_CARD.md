# Data Card — v2.0.0

## Dataset description

A Chinese-language, source-grounded question-answer candidate dataset about Internet, ICT, education technology, labor platforms, and digital agriculture reports. The canonical set is 387 active rows. A 60-row AI-assisted source-reconstructed subset is recommended for exploratory evaluation; it is not human verified and is not a gold benchmark.

## Contents and composition

- 327 historical v1.1/v1.2 licensed-source records, retained as candidates pending v2 review and excluded from the recommended subset.
- 60 new records across four Chinese report documents and four new source families.
- 15 source documents are registered across seven consolidated publishing institutions; four are new in v2.0.0, while five historical source files await revalidation.
- Recommended task families: single-document retrieval, numeric retrieval, within-document synthesis, and cross-document synthesis.
- Recommended splits: TRAIN 42, DEV 9, TEST 9.
- All 60 recommended rows are answerable. Historical rows include answerable and unanswerable items, but remain pending v2 review.

Targets of 2,000 records, 60 reports, and 10 publishing institutions were not met. The active set excludes the 506 CAICT legacy rows because source adaptation and redistribution rights were not established. The exact v1.2.0 package remains in the historical snapshot and migration ledger.

## Data creation

New question and answer candidates were created with AI assistance from four Chinese source documents. New family splits were assigned before question drafting. An answer-only-free review packet was used to reconstruct answers and evidence from the source PDFs. The same active AI session drafted and checked the new items; the work is not independent human annotation and does not establish cognitive blindness. Model label: GPT-6 (Codex; exact deployment identifier not exposed). Prompt and source file hashes are recorded under `audit/` and in each record.

## Source and evidence

Evidence locators identify physical, 1-based PDF pages and a narrative text region. The package excludes source passages, figures, tables, images, and PDFs. Where source licenses limit rights to text, only paraphrased narrative facts are used. Source metadata records translation status, license page and hash, required attribution, adaptation notice, and third-party limits.

## License

Mixed record-level terms apply. No single repository-wide license is asserted. New recommended rows include CC BY-SA 3.0 IGO and CC BY-NC-SA 3.0 IGO records. See `LICENSES.md`, `LICENSE_STATUS.md`, `ATTRIBUTION.md`, and `sources.json`.

## Review and intended use

Use as a candidate corpus for QA, evidence retrieval, source-grounding, and document understanding research. Review statuses must be retained during use. The new subset has AI source reconstruction but no human review. Historical rows require further source-file and answer-blind review. The historical splits were assigned after annotation; they are not prospective blind holdouts. Prior system exposure has not been audited.

## Limitations

The release is far below its expansion targets. Report coverage is concentrated in seven consolidated publishers and education-related sources. No independent human audit, gold-label claim, RAG baseline, or model-performance result is included. Some historical source files require revalidation, and all 327 historical candidates remain outside the recommended subset.
