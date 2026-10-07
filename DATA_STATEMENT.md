# Data Statement — v2.0.0

## Motivation and scope

The dataset supports research on Chinese question answering over Internet, ICT, education technology, health information systems, labor, and digital agriculture reports. The unified corpus has 2,000 rows: all 833 v1.2.0 records plus 1,167 new candidates. It contains questions, candidate answers, required-fact summaries, physical PDF page locators, split metadata, and record-level rights information.

## Language and sources

The 1,107 latest additions use text extracted from 32 Chinese-language PDFs published by ITU and WHO. The remaining new candidates use the source editions documented in `sources.json`. The dataset does not translate English reports itself. Source titles, languages, translation provenance, official links, hashes, and license notices are listed by source ID.

## Annotation and review

The 1,107 additions are rule-generated sentence clozes: each question embeds one short source sentence with a value, term, or clause masked. The answer was available to the deterministic generation process. There was no per-row LLM inference, answer-blind reconstruction, or independent human review. Each row is marked `pending_ai_content_verification` and carries its source sentence hash, physical page, source PDF hash, generation method, and script hash.

The other 60 new candidates were checked with an answer-free source reconstruction in the same AI-assisted session that drafted them; this is not independent review. The 833 historical rows retain their existing IDs, content, evidence, and splits. Their v2 answer-blind review is pending, as is revalidation for some historical source files. The dataset owner directed that all 2,000 rows remain in `recommended`; users should treat the review status as authoritative.

No human review, independent annotation, or corpus-wide gold status is claimed.

## Rights and redistribution

Licensing is mixed by record. The 1,107 cloze rows adapt short sentence excerpts from ITU and WHO reports with CC BY-NC-SA 3.0 IGO notices. Their exact source attribution, license link, adaptation notice, noncommercial and ShareAlike obligations are carried in each record. Third-party attribution screening remains pending for those candidates. No source PDFs or media are redistributed.

The 506 legacy CAICT QA records retain their prior CC BY 4.0 record license and source attribution. The dataset owner confirmed authorization to republish those QA records; the underlying CAICT report license is not asserted. See `LICENSES.md`, `LICENSE_STATUS.md`, `ATTRIBUTION.md`, and per-record `publication_rights`.

## Splits and prior exposure

The 1,167 new rows follow source-family assignments made before drafting; same-source items stay in one split. The 833 historical splits were assigned after annotation and retain their original values. The combined split counts are 1,377/300/323 for TRAIN/DEV/TEST. No blind-holdout claim is made; prior system exposure has not been audited.

## Intended and out-of-scope use

The corpus is intended for exploratory source-grounded QA and retrieval research. Most of the latest 1,107 additions are sentence-completion items; they should not be treated as a balanced complex-reasoning evaluation set. The package has no model baselines or performance claims and is not a human-verified gold benchmark.
