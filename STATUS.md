# Status

Project: AffordableHousing
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: none yet
Step: 1
Since: 2026-10-07

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | | |
| 2a | Draft with brackets resolved | | |
| 2b | Eric's edit, Claude's look-over | | |
| 2c | Slice markup | | |
| 2d | Hero 1680x1080 + alt text | | |
| 2e | SEO | | |
| 2f | Pushed to Prismic (draft) | | |
| 2g | Mailchimp teaser | | |

## Stale

None.

## Log

- 2026-10-07 Step 1 opened. Topic: county map of the share of rental units a
  household can afford at 30% of income, by income profile or a typed-in
  income, animated over time, with a one-state filter. Rent from ACS B25063.
- 2026-10-07 Plan approved. Seven frames that share no sample: 1980, 1990,
  2000, 2005-2009, 2010-2014, 2015-2019, 2020-2024. Post-tax income by default
  (Eric). Built: DATASETS.md, fetch scripts, 3,120 stable county units, tax
  grid, page at dist/index.html (not in git yet), coverage check, tie-out
  clean. Working title "Rentals Within Reach" is a placeholder.
- 2026-10-07 Open before the page can be public: IPUMS permission to publish
  the 1980 and 1990 county rent buckets (ipums@umn.edu). Until then
  data/processed/ and dist/ stay out of git and the repo stays private.
- 2026-10-07 Scope changed by Eric: four ACS periods only (2005-2009,
  2010-2014, 2015-2019, 2020-2024); the 1980, 1990 and 2000 censuses are
  dropped because the older distributions did not look comparable. Bubble map
  only. Traffic-light colors with breaks at 40, 50, 65 and 80%. No IPUMS data
  is used, so the earlier permission hold is lifted and data/processed/ and
  dist/ are back in git. Tie-out clean on the four-period build. Target
  publish date: October 8, 2026.
- 2026-10-07 Eric spotted Oregon jumping in 2020-2024. Cause: TAXSIM35 in one
  large batch returned Oregon 2023 state tax about $37,000 too low. Fixed by
  running each state on its own with an order check. Only Oregon 2020-2024
  changed (65% within reach before the fix read as 93%; now 61%). National
  2020-2024 moved from 65.98% to 65.53%.
- 2026-10-07 Eric accepted: default profile is the median renter household
  (B25119; estimated from B25118 buckets where not published); "priced within
  reach" wording; tax assumptions shown by the control; 13 limitations for the
  post (DATASETS.md section 7). Color breaks now 30, 40, 50, 65, 80% because
  the renter default put 86% of rentals in one band. Independent tie-out by a
  fresh agent started; rule added to CLAUDE.md and PROCESS.md.
- 2026-10-07 Added at Eric's request: a checkbox to leave out 71 college
  counties (15% or more of residents enrolled in college or graduate school,
  B14001, 2020-2024), limitation 14, and a county chart of all rentals against
  rentals priced within reach by period. Tie-out clean.
