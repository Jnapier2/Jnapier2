# Account Analyst Portfolio Showcase

**Make client-level spend and savings easier to interpret—and incomplete records harder to overlook.**

This interactive browser demonstration brings client lookups, spend classification, filtered savings summaries, and missing-input review into one experience. It shows how familiar spreadsheet analysis can become a more transparent decision-support tool without allowing incomplete records to distort the eligible savings calculation.

**Public synthetic-data edition 1.0.0 · Source demonstration, not a production release.**

## What makes the design distinctive

Missing values are treated differently from genuine zeroes. Incomplete records remain visible in a review queue but are excluded from both savings and the eligible spend denominator. The summary, client comparison, chart, and record table share one calculation implementation, and client totals reconcile with the filtered results.

The result is an example of analytical judgment as well as presentation: explain who is included in a measure, keep exceptions visible, and make the totals traceable to the records behind them. All displayed outcomes are synthetic, not realized client savings.

## Explore the demonstration

Open [index.html](index.html) together with its adjacent [analytics.js](analytics.js) file in a browser that permits local files. The GitHub file viewer shows source rather than running the page. Keep both files in the same folder. No installation, credentials, imported data, or third-party library is required by the page. Do not change browser or endpoint protections to run it.

Filter by client, production type, or data quality. Reset returns to the complete bundled example; reloading discards filter choices.

<details>
<summary>Demonstration rules, provenance, and evaluation limits</summary>

## Existing work and public adaptation

Existing Account Analyst Excel portfolio work inspired this demonstration of lookups, classification, aggregation, and data-quality review. Source-workbook layout and formula inventory are intentionally omitted.

This is a new browser adaptation of that workflow, **not a recovered version of the original workbook**. All twelve records, amounts, client labels, regions, and thresholds in this edition are invented. The original workbook, its financial figures, document metadata, and underlying business records are not distributed. The public results are not realized savings, client results, or a forecast.

## Calculation contract

| Rule | Public demonstration behavior |
| --- | --- |
| Client lookup | Each bundled client maps to one region; unknown values are rejected |
| Low spend | Spend is at or below the type-specific synthetic threshold |
| Missing inputs | A missing hard or soft savings value creates a Review record; a genuine zero stays valid |
| Complete-record reporting | Incomplete rows remain visible but contribute neither savings nor eligible denominator spend |
| Savings rate | Sum of eligible savings divided by eligible spend; no eligible spend returns Not available |
| Reconciliation | Client totals reconcile to the filtered records and summary |

Complete-record reporting is an explicit rule of this public adaptation, not a claim that the original workbook used the same exclusion rule.

## Verification and limitations

From the repository root, run `node --test tests/test_account_analytics.cjs` with Node.js 22 or later. Behavioral checks cover totals, missing versus zero, thresholds, invalid input, filters, immutability, and reconciliation. Repository workflows provide dated test and browser-smoke results; this description is not a substitute for those results.

Physical Windows, Norton, other browsers, formal assistive-technology testing, and production use are not qualified by the calculation tests. No hosted website deployment is claimed.

The page has no data ingestion, account access, persistent storage, external service integration, or payment functionality. No real business files should be added to this demonstration folder.

## Dependencies, rights, and recovery

The page uses browser HTML/CSS/JavaScript with no bundled third-party code. To recover the demonstration, reload its bundled files or restore this folder from a reviewed Git revision. [Repository rights](../../LICENSE.md) apply; public visibility does not create an open-source license. The original private workbook is unchanged.

</details>

[Professional Portfolio](../README.md)

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
