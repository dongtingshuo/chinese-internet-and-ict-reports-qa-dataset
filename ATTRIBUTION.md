# Source attribution and adaptation notices

## Dataset-level citation

Cite: TingShuo Dong. 2026. *Chinese Internet and ICT Reports QA Dataset*, version 1.2.0. https://github.com/dongtingshuo/chinese-internet-and-ict-reports-qa-dataset. The package contains AI-assisted candidate adaptations under mixed record-level terms. For each reused row, cite every source in its `source_ids` and retain the terms in `publication_rights`.

## New v1.2.0 source reports

| Source ID | Report | Publisher | License / notice |
|---|---|---|---|
| ILO2026-LIFELONG-SKILLS | *Lifelong learning and skills for the future* (official Chinese executive summary) | International Labour Organization | CC BY 4.0; rights statement at physical PDF p. 12 |
| UNESCO2023-DIGITAL-CITIZENSHIP | *Global Practices Evaluation & Assessment Toolkit: Advancing Artificial Intelligence-Supported Global Digital Citizenship Education* (Chinese edition) | UNESCO IITE and Shanghai Open University | CC BY-SA 3.0 IGO; rights statement at physical PDF p. 2 |
| ILO2021-EMPLOYMENT-RELATIONSHIP | *Platform work and the employment relationship* (Chinese translation), ILO Working Paper 27 | International Labour Organization | CC BY 3.0 IGO; rights statement at physical PDF p. 2; Chinese translation disclaimer applies |

The source registry contains exact PDF URLs, hashes, page counts, rights-notice locations, attribution text, adaptation/translation notices, and third-party restrictions. New v1.2.0 records also reuse v1.1.0 reports. Use the exact source citation and notices stored on each record rather than inferring them from this summary table.

## Required notices

For every record, preserve all strings in `publication_rights.required_source_attributions`, `required_adaptation_disclaimers`, and `translation_disclaimers`, plus its license URL and modification notice. For cross-document rows, retain notices for every supporting source. Do not imply that an institution endorses the adaptation.

CC BY-SA 3.0 IGO adaptations remain under CC BY-SA 3.0 IGO. The three UNESCO-derived records are `IICR-V12-0055`–`IICR-V12-0057`. They use toolkit-authored scoring tables as evidence references but do not reproduce table contents, images, or other visual assets.

## Third-party content and source files

A report's license does not automatically apply to third-party text or media credited in the report. The package excludes source PDFs, screenshots, extracted page text, long quotations, photographs, logos, tables, charts, and other source media. Each source's third-party limitations are listed in `sources.json` and repeated in the row-level license obligations. Do not reuse the source reports or their third-party elements based only on this dataset notice.
