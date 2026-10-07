# Data Statement — v2.0.0

## Motivation and scope

This dataset supports research on Chinese question answering over public Internet, ICT, education technology, labor, and digital-agriculture reports. It contains paraphrased questions, answer candidates, required-fact summaries, evidence-page locators, split metadata, and per-record source-rights information.

## Language and sources

The active records use Simplified or Traditional Chinese, depending on the cited source. New sources are official Chinese-language editions or summaries, or an institution-prepared Traditional Chinese translation. The dataset does not translate English reports itself. See `sources.json` for titles, language, translation provenance, original and parent URLs, file hashes, and rights notices.

## Annotation and review

New items are AI-assisted candidates. Review artifacts omit candidate answers from the question-only review input and record source-first reconstructed answers, page locators, prompt hash, model label, PDF hash, and conclusion. Drafting and checking were performed in the same active AI session; independent review and human review are not claimed. `human_reviewed=false`; new rows use `gold_candidate=false`.

Historical records preserve prior IDs, questions, answers, required facts, evidence, and splits. They are migrated as pending candidates. Source-file revalidation is pending for some historical families, and all historical records await the v2 answer-blind reconstruction. They are not included in the recommended subset.

## Rights and redistribution

Licensing is mixed by record. Each record carries source attribution and adaptation duties; source records also state translation and third-party-content limits. CC BY-SA and CC BY-NC-SA obligations remain attached to adapted records. The package contains no source report PDFs, images, tables, figures, or long excerpts. The 506 legacy CAICT rows remain only in the exact v1.2.0 archive and migration ledger because source-level adaptation and redistribution permission was not established for them.

## Splits and prior exposure

The 60 new records are assigned by source family before question drafting and grouped to prevent linked questions from crossing splits. Historical splits were assigned after annotation and retain their original provenance. No blind-holdout claim is made. Prior system exposure has not been audited.

## Intended and out-of-scope use

The dataset is intended for exploratory source-grounded QA and retrieval research. It does not supply model baselines or performance claims. It is not a human-verified gold benchmark. Users must respect row-level license and attribution obligations, and should not treat pending historical records as recommended evaluation data.
