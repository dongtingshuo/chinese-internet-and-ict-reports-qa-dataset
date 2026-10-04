# License status

## Dataset rows

The v1.1.0 package uses mixed record-level terms:

- The original 506 v1.0.0 records, IDs, and split assignments are preserved unchanged and remain licensed under CC BY 4.0 as stated in the original release.
- The 267 new records (`IICR-V11-0001` through `IICR-V11-0267`) are concise AI-assisted paraphrases/adaptations of eight reports explicitly marked CC BY 3.0 IGO. Each row carries the applicable report citation, license link, modification notice, and institution-specific adaptation disclaimer.

There is no blanket license applying uniformly to `records.jsonl`; use the per-record `publication_rights` and `source_refs`. Hugging Face metadata therefore identifies the repository license as `other` and explains the mixed terms.

## Source rights evidence

`sources.json` records the official source file URL, SHA-256, language and translation identity, rights-holder, license URL, rights notice location, required attribution, adaptation and translation notices, and third-party restrictions for every new report. The World Bank, ILO, and ADB rights pages permit adaptations under CC BY 3.0 IGO subject to attribution and stated conditions. These records are not legal opinions.

ADB's Chinese publications state that English is the only official version. The ILO Chinese PDFs state that the translations are not official ILO translations. The World Bank WDR 2019 catalog identifies the Chinese report as Final, while its PDF cover bears “会议版本”; both facts are retained in the source record.

## Exclusions

The package contains no original source PDF, source page image, screenshot, long quote, chart, table, logo, or third-party media. The source hash is for provenance, not a permission to redistribute the source file. No reuse claim is made for third-party items inside the reports.

## License links

- Legacy rows: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- New rows: [CC BY 3.0 IGO](https://creativecommons.org/licenses/by/3.0/igo/)
