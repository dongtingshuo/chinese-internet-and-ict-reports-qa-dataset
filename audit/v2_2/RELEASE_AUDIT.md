# v2.2.0 release audit

## Released subset

The active package contains 2,355 records: 2,275 eligible v2.1.0 rows and 80 passing v2.2.0 replacement rows. Split counts are TRAIN 1,573, DEV 372, and TEST 410. Baseline record IICR-V12-0030 was excluded because its question has multiple plausible source-supported answers. Another 140 proposed replacements did not pass all release gates and are not in the active package.

## Review evidence

- Source-grounded review covers all 2,508 frozen baseline rows; 2,506 earned answer-blind AI reconstruction credit. IICR-V12-0026 and IICR-V12-0028 did not earn credit and are excluded.
- Dataset-owner attestation records two independent human reviews (D and T) for each baseline row and a third reviewer (S) for designated adjudications and follow-ups. Reviewer-signed method declarations are not present.
- Three historical AI protocol-deviation attempts retain zero credit; all three queries have separately locked clean source-first reruns.
- 208 overlap pairs were reviewed (186 retain both; 22 revise one). Every revise-one pair has at least one member outside the released subset.
- Source PDF hashes match 61/61 registered sources. Rights remain source-specific; the dataset owner attests QA-record reuse authorization for CAICT rows. This is not a CAICT report-level open-license claim.

## Scope and limitations

The Gold label applies only to the active released records and reflects the documented operational selection gates. It is not an external certification or a guarantee that every answer is error-free. Human-review method and no-assistance disclosures are owner-attested, not reviewer-signed. Historical splits were assigned after annotation and are not blind holdouts. No report PDF or media is included. No model-performance result is claimed.

Machine-readable audit details: RELEASE_AUDIT.json.
