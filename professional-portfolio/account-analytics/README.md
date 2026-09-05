# Account Analyst Portfolio Showcase

Turn project spend into a reviewable story: client lookup rules, low-spend classification, complete-record savings, and a visible queue for missing inputs.

**Public synthetic-data edition 1.0.0 · Source demonstration, not a production release.**

## Explore the demonstration

Open [index.html](index.html) together with its adjacent [analytics.js](analytics.js) file in a browser that permits local files. The GitHub file viewer shows source rather than running the page. Keep both files in the same folder. No installation, credentials, imported data, or third-party library is required by the page. Do not change browser or endpoint protections to run it.

Filter by client, production type, or data quality. The summary, client comparison, chart, and record table use one calculation implementation. Reset returns to the complete bundled example; reloading discards filter choices.

## Existing work and public adaptation

The existing Account Analyst Excel portfolio work inspired this demonstration of lookups, classification, aggregation, and data-quality review. Source-workbook layout and formula inventory are intentionally omitted.

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

From the repository root, run `node --test tests/test_account_analytics.cjs` with Node.js 22 or later. These behavioral tests cover fixed totals, missing versus zero, inclusive thresholds, invalid input, all filter combinations, immutability, and reconciliation. Python repository tests check public-file boundaries. The hosted workflow also attempts a sandboxed browser smoke test covering rendered totals, filters, reset, and narrow-screen layout; consult that workflow's actual result rather than treating this paragraph as proof it passed.

Local browser navigation was blocked by the review environment's administrator policy. No protection was relaxed. Physical Windows, Norton, other browsers, formal assistive-technology testing, and production use are not qualified by the calculation tests. No hosted website deployment is claimed.

The page has no data ingestion, account access, persistent storage, external service integration, or payment functionality. No real business files should be added to this demonstration folder.

## Dependencies, rights, and recovery

Runtime: browser HTML/CSS/JavaScript only; no bundled third-party code. Verification: Node.js built-in test runner, Python standard library, and the hosted runner's installed Chrome/Chromium. Browser version is reported by the smoke test and is not pinned as a product dependency. Existing repository workflow actions remain unchanged.

The original private workbook is preserved. To recover the demo, reload its bundled files or restore this folder from a reviewed Git revision. [Repository rights](../../LICENSE.md) apply; public visibility does not create an open-source license.

[Professional Portfolio](../README.md)

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
