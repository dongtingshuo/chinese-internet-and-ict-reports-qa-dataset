# Source attribution and adaptation notices

## Dataset-level attribution

Cite: TingShuo Dong. 2026. *Chinese Internet and ICT Reports QA Dataset*, version 1.1.0. https://github.com/dongtingshuo/chinese-internet-and-ict-reports-qa-dataset. Indicate that the release contains AI-assisted paraphrases/adaptations and link the applicable record-level license. Cite the original report listed by the row's `source_ids`.

## New v1.1.0 sources

For each record, use the full citation in its `source_refs.required_source_attribution_short_form`. The same source metadata, exact PDF hash, rights notice page, and official URLs are in `sources.json`.

| Source ID | Report | Publisher | License notice |
|---|---|---|---|
| WB2014-RURAL | *Information and Communications in the Chinese Countryside: A Study of Three Provinces* (official Chinese summary) | World Bank | CC BY 3.0 IGO; parent report rights notice, PDF p. 6 |
| WB2016-DIGITAL | *World Development Report 2016: Digital Dividends* (Chinese overview) | World Bank | CC BY 3.0 IGO; overview p. 4; cite the final report as directed by the overview |
| WB2019-WORK | *World Development Report 2019: The Changing Nature of Work* (Chinese-language version) | World Bank | CC BY 3.0 IGO; source PDF p. 6; World Bank catalog says Final, while cover says “会议版本” |
| WB2025-DIGITAL | *Digital Progress and Trends Report 2025: Strengthening AI Foundations* (Chinese overview) | World Bank | CC BY 3.0 IGO; source PDF p. 6 |
| ILO2020-PLATFORM | *Digital Labour Platforms and Labour Protection in China* (Chinese edition), ILO Working Paper 11 | ILO | CC BY 3.0 IGO; source PDF p. 2 |
| ILO2021-PLATFORM | *Online Digital Labour Platforms in China: Working Conditions, Policy Issues and Prospects* (Chinese edition), ILO Working Paper 24 | ILO | CC BY 3.0 IGO; source PDF p. 2 |
| ADB2018-CITIES | *50 Climate Solutions from Cities in the People’s Republic of China* (Chinese edition) | ADB | CC BY 3.0 IGO; source PDF p. 3; English is the only official text |
| ADB2023-YOUTH | *Youth Employment and the Pandemic Recovery in the People’s Republic of China* (bilingual) | ADB | CC BY 3.0 IGO; source PDF p. 4; English is the only official text |

## Required change and adaptation notices

All new QA items are paraphrases/adaptations prepared with AI assistance. When redistributing them, retain the row's source citation and CC BY 3.0 IGO link, state that the question, answer, fact summary, and locator were adapted, and include the applicable notice below. The notice is not an endorsement by the source institution.

### World Bank records

Use the source-specific citation in `sources.json` and this notice:

> 这是对世界银行原著作的改编。本改编作品中的观点和看法完全是改编者的责任，世界银行对改编内容不表示认可。

### ILO records

Use the source-specific citation in `sources.json` and this notice:

> 该作品是对国际劳工局所著原作的改编。作品中所表达的观点和意见完全由改编作者负责，不代表国际劳工局对其观点和意见表示认可。

The Chinese ILO source PDFs also state that the Chinese translations are not official ILO translations and that ILO does not take responsibility for translation accuracy. That note is preserved in each applicable source record. Do not use the ILO logo.

### ADB records

Use the source-specific citation in `sources.json` and the complete disclaimer in each row's `publication_rights.required_adaptation_disclaimer`. In substance, it says the work adapts the named ADB work, the views belong to the adapter, ADB does not endorse or guarantee the adaptation, and ADB accepts no responsibility for its use. The Chinese sources identify English as the only official version; preserve that note. Do not use the ADB logo.

## Third-party content and source files

Only concise paraphrased narrative facts and page locators are included in the new rows. The package does not include source PDFs, extracted pages, photographs, logos, charts, tables, or other third-party media. The report-level CC BY 3.0 IGO license does not automatically apply to such third-party components. See each source's recorded limitations before reusing any material outside this dataset.
