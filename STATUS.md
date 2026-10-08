# Status

Project: AffordableHousing
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: rentals-within-reach
Step: 2f
Since: 2026-10-08

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | 2026-10-07 | Tie-out clean; independent tie-out by a fresh agent done; viz live on Pages |
| 2a | Draft with brackets resolved | 2026-10-08 | 12 edits accepted; title, subtitle, video embed set |
| 2b | Eric's edit, Claude's look-over | 2026-10-08 | 7 look-over edits accepted; limits section added |
| 2c | Slice markup | 2026-10-08 | Drop cap off, no dividers, 40px after both embeds |
| 2d | Hero 1680x1080 + alt text | 2026-10-08 | Default map at hero scale; headline 1,960 of 3,141 counties; alt 496 characters |
| 2e | SEO | 2026-10-08 | Dataset schema; 8 FAQ entries; meta title 52, description 151 characters; Dayton link on hold |
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
- 2026-10-07 Independent tie-out by a fresh agent came back: no data,
  geography or arithmetic error; headline numbers reproduced to within 0.02
  points. Fixed from its findings: headline now says "at least" when any
  county is top-coded; a top-coded 80th percentile is treated as a floor;
  Bedford VA shows its joined note; three DATASETS.md statements corrected.
  Recorded as limitations 15 to 18. Open for Eric: whether to remove the 2009
  Making Work Pay credit from the first period, and which household type is
  the tax default.
- 2026-10-07 Eric decided: remove the 2009 Making Work Pay credit from
  2005-2009 (default now reads 32.0, 27.6, 32.0, 31.3%, matching the
  independent agent's own figure); keep married with no children as the tax
  default. Added a low-reliability mark for median incomes with a margin over
  25% of the estimate, after Eric questioned Webster County WV.
- 2026-10-07 County panel: line chart replaced by two change columns; the
  share-over-time chart removed (Eric). Dayton post compared with the tool:
  the post's 49% to 46% drop comes from the whole-bucket rule in 2020-2024
  (46% is a floor; interpolated 56%). Eric to decide on a note to that post.
- 2026-10-07 Step 1 confirmed by Eric. Not covered by the independent agent,
  because they came after it: the income margin-of-error mark and the change
  columns. Claude's own tie-out is clean on the final build (commit 090ab5b).
- 2026-10-07 After Step 1: instant tooltips in the county panel; limitation 19
  (the renter pool changes over time) and a follow-up research list added to
  DATASETS.md at Eric's request. Contact address moved to the central env and
  removed from this repo's history.
- 2026-10-07 Step 2a opened. Slug: rentals-within-reach. posts/rentals-within-reach/POST.md created from the template; waiting for Eric's draft.
- 2026-10-07 Tutorial video built: video/rentals-within-reach-tutorial.mp4
  (57 s, 1920x1080, same format and music as the earlier tutorials). Sequence
  set by Eric: household income on the national map, Florida, Play, Miami-Dade
  panel, Broward and Holmes from the rankings, reset, search New York County.
  Captions are Claude's and await Eric's review.
- 2026-10-08 Step 2a: Eric's draft placed verbatim in POST.md with the viz
  embed, five images made from the tool (scripts/11_post_images.py) and a
  placeholder for the video. README.md written, since the draft sends readers
  to GitHub for instructions and methodology. Proposed edits sent to Eric as
  a numbered list; none applied.
- 2026-10-08 Step 2a: Eric accepted all 12 proposed edits; applied to POST.md.
- 2026-10-08 Step 2a: section headers added at Eric's request; title set by Eric (typo "afforability" corrected).
- 2026-10-08 Step 2a: title is "Rentals Within Reach: Visualizing the Affordability of Rentals Where You Live" (capital W and title case accepted by Eric).
- 2026-10-08 Step 2a: subtitle chosen by Eric from three options.
- 2026-10-08 Step 2a: tutorial video is on YouTube (zs0lN6o3SdE) and embedded in POST.md.
- 2026-10-08 Step 2a confirmed by Eric. Section is both Data 4 Thought and Visualization. Step 2b opened; Eric has begun editing POST.md directly.
- 2026-10-08 Step 2b: look-over done; Eric accepted items 1 to 3 and 5 to 8, confirmed the 20.9% homeowner cost figure himself, and asked for a limits section, drafted by Claude before \"Try it yourself\" and awaiting his review.
- 2026-10-08 Step 2b confirmed by Eric. Next: 2c, slice markup.
- 2026-10-08 Step 2c opened. Defaults applied; a 40px spacer added after each of the two embeds, since a heading follows both.
- 2026-10-08 Step 2c: drop cap turned off for this post and no divider dots (Eric).
- 2026-10-08 Step 2c confirmed by Eric. Step 2d opened.
- 2026-10-08 Step 2d: hero built from the default map at hero scale (scripts/12_hero.py), padded to 1680x1080; alt text written. Awaiting Eric.
- 2026-10-08 Step 2d: Eric did not follow the 31% national figure on the hero, so the headline is now the count of counties under half (1,960 of 3,141), read from the page.
- 2026-10-08 Step 2d confirmed by Eric. Step 2e opened.
- 2026-10-08 Step 2e: meta title, description, keywords and dataset schema fields drafted in the front matter on the pattern of the earlier visualization posts. Target searches and proposed page text sent to Eric.
- 2026-10-08 Step 2e: Eric accepted the data sentence, the free-to-use sentence and a Common questions section; the Dayton link is on hold. Both sentences added after the map. FAQ answers drafted for his review.
- 2026-10-08 Step 2e: Eric accepted all eight Common questions answers; added at the end under divider dots, with the before-tax count (1,084 of 3,141) checked against the page.
- 2026-10-08 Step 2e confirmed by Eric. Step 2f opened.
