# Datasets

One section per dataset, updated whenever we learn something new. The measured
coverage figures are in the last section, from `scripts/08_coverage.py`.

The map has four periods that share no survey sample: 2005-2009, 2010-2014,
2015-2019 and 2020-2024, all from the American Community Survey. An earlier
build reached back to the 1980, 1990 and 2000 censuses. Eric dropped those on
October 7, 2026 because the older rent and income distributions did not look
comparable with the ACS. Nothing from IPUMS NHGIS is used or published.

## 1. ACS 5-year table B25063, gross rent (Census Bureau)

**What it is.** Count of renter-occupied housing units in each gross rent
bucket, plus a count paying no cash rent. Gross rent is contract rent plus the
estimated monthly cost of utilities and fuels when the renter pays them. Each
cell is a survey estimate with a published margin of error.

**Where it comes from.** Census API, `api.census.gov/data/<vintage>/acs/acs5`,
group B25063. A key is required for data calls. JSON, cached one file per
vintage and geography in `data/raw/acs/`.

**Version and vintage.** Four 5-year files, chosen so no two share sample:
2005-2009, 2010-2014, 2015-2019 and 2020-2024 (API vintages 2009, 2014, 2019,
2024). The 2020-2024 file was released January 29, 2026. A new 5-year file
comes out each year; earlier files are not revised.

**Coverage.** Every county and county equivalent, every state, the nation, and
county subdivisions (used for Connecticut towns). All values are sample
estimates; none are filled by the publisher at table level. Individual answers
that were missing are filled by the Census Bureau before tabulation
("allocation"). We did not pull the allocation tables, so the share of rent
answers that were filled in is not measured here.

**Changes over time.** In 2005-2009 and 2010-2014 the buckets are: under $100,
$50 steps to $799, $800-899, $900-999, $1,000-1,249, $1,250-1,499,
$1,500-1,999, and $2,000 or more. From the 2011-2015 file on, the top bucket
is split into $2,000-2,499, $2,500-2,999, $3,000-3,499 and $3,500 or more, and
the "no cash rent" cell moves from _024 to _027. So the first two periods top
out at $2,000 and the last two at $3,500. Connecticut is reported for eight
counties through the 2017-2021 file and for nine planning regions from
2018-2022 on.

**Suppressed, censored or masked values.** The top bucket is open-ended. When
a rent ceiling lands inside it we report "at least" the share below it. No
cells are suppressed in B25063 at county level, but small counties have
estimates of zero in many buckets with wide margins.

**Missing data.** A county with zero renter units paying cash rent has no
share.

**Revisions.** None. We pin the four vintages.

**Units and rounding.** Housing units. In a 5-year file, rents reported in
earlier years are adjusted by the Census Bureau to the final year's dollars
with the CPI before bucketing. Each period is therefore in its own final-year
dollars.

**Known quirks.** The universe is renter-occupied units, occupied at the time
of the survey. Vacant units for rent are not in it, so this is what tenants
pay, not what is on the market. Rents cluster at round numbers, which sit at
bucket floors, so a straight-line spread inside a bucket is an approximation.
The 2020-2024 file includes 2020, when pandemic disruption cut response.

**Uncertainty.** Margins of error are published at the 90% level for every
cell. We carry the margin on total renter-occupied units per county and mark
counties where it is large against the estimate.

**License and attribution.** Public domain. Credit: U.S. Census Bureau,
American Community Survey 5-year estimates, table B25063.

## 2. ACS 5-year income tables B19001, B19013, B19080, B25119 (Census Bureau)

**What it is.** B19001: households by income bucket (16 buckets, top $200,000
or more). B19013: median household income. B19080: upper limits of the first
four household income quintiles (the 20th, 40th, 60th and 80th percentiles).
B25119: median household income by tenure (all, owner, renter). B25118: renter households by income (11 buckets, top $150,000 or more), used
to estimate a renter median where none is published. B25064, median gross
rent, is pulled only as a check.

**Where it comes from.** Census API, same endpoint and cache as section 1.

**Version and vintage.** Same four vintages.

**Coverage.** Counties, states, nation, Connecticut towns. B19080 does not
exist in the 2005-2009 file; it starts with 2006-2010. Where a percentile is
not published we estimate it by straight-line interpolation inside the B19001
bucket that contains it, and the page marks the value as estimated.

**Changes over time.** B19001 buckets are unchanged across all four vintages.

**Suppressed, censored or masked values.** Medians are top-coded at 250,001
and bottom-coded at 2,499. B19080 values are missing for a few small counties.
We treat those as not published and interpolate. A percentile that falls in
the open top income bucket cannot be estimated and is left out. A published
80th percentile of 250,001 is a top code: we keep it as a floor and the page
shows the share as "at least" (29 unit-periods, 28 of them in 2020-2024,
including Manhattan, Santa Clara and San Francisco).

**Missing data.** Negative values (-666666666 and similar) mean no estimate.

**Revisions.** None.

**Units and rounding.** Dollars of the final year of the 5-year period. Income
is money income before taxes. It leaves out noncash benefits and tax credits
such as the Earned Income Tax Credit.

**Known quirks.** Income in the past 12 months is collected all year, so the
reference period is not a calendar year. Rebuilt Connecticut regions and
joined units have no published median or quintiles; we interpolate from summed
buckets, and median renter income is not available for them.

**Uncertainty.** Published margins of error at the 90% level. Not carried into
the page for income; the rent-side reliability mark covers thin counties.

**License and attribution.** Public domain. Credit: U.S. Census Bureau,
American Community Survey 5-year estimates.

## 3. County boundaries and changes (Census Bureau)

**What it is.** Cartographic boundary files for counties and states, 2024
vintage, 1:500,000; the Census list of substantial county changes by decade;
and the Connecticut crosswalk from towns to old counties and new planning
regions.

**Where it comes from.**
`www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip`,
`cb_2024_us_state_500k.zip`;
`census.gov/programs-surveys/geography/technical-documentation/county-changes.html`;
`www2.census.gov/geo/docs/reference/ct_change/ct_cou_to_cousub_crosswalk.txt`.

**Version and vintage.** 2024 boundaries. The map is drawn on these for every
period.

**Coverage.** 50 states and DC. Puerto Rico is left out.

**Changes over time.** Every change since 2009 that Census lists as
substantial is handled in `scripts/03_harmonize.py`. Renames by code map:
Shannon County SD to Oglala Lakota, Wade Hampton AK to Kusilvak (both 2015).
Joined into one unit for every period: Bedford city with Bedford County VA
(merged 2013); Chugach with Copper River AK (split from Valdez-Cordova in
2019); Petersburg, Hoonah-Angoon and Prince of Wales-Hyder AK (land and 613
people moved among them in 2013). Connecticut: the nine planning regions are
rebuilt from 169 towns in the three periods before 2020-2024. Counts are only
added, never split by area.

**Suppressed, censored or masked values.** None.

**Missing data.** None.

**Revisions.** Census reissues boundary files yearly. Pinned to 2024.

**Units and rounding.** Simplified for drawing; shapes are not used for any
calculation.

**Known quirks.** Census counts a change as substantial at 200 or more people
or 10 square miles. Smaller annexations are not corrected. Connecticut towns
nest exactly in both the old counties and the planning regions; the regions do
not nest in the counties.

**Uncertainty.** Not applicable.

**License and attribution.** Public domain. Credit: U.S. Census Bureau.

## 4. TAXSIM35 (National Bureau of Economic Research)

**What it is.** A tax calculator. Given a tax year, state, filing status,
dependents and income, it returns federal and state income tax. We use it to
turn a pre-tax household income into a post-tax one.

**Where it comes from.** `taxsim.nber.org/taxsim35/`, the offline binary for
macOS, CSV in and out. No login.

**Version and vintage.** TAXSIM35. Federal law through 2023; state law through
2021, with 2022 and later computed from 2021 state law carried forward. The
offline program refuses tax year 2024. Our 2020-2024 period is in 2024
dollars, so we bring each income to 2023 dollars with the CPI-U, tax it under
2023 law, and scale the tax back up.

**Coverage.** All states and DC. Tax years 2009, 2014, 2019 and 2023 are used.
Everything it returns is modeled, not measured.

**Changes over time.** Tax law itself: the 2009 Making Work Pay credit (which
we remove, see section 7 item 15), and the 2018 changes to rates, the standard deduction and the child tax credit.

**Suppressed, censored or masked values.** None.

**Missing data.** None.

**Revisions.** NBER updates the program as laws change. We keep the grid we
computed in `data/processed/tax_grid.json`.

**Units and rounding.** Dollars of the tax year.

**Known quirks and our assumptions.** No local income taxes (city and school
district taxes in Ohio, Pennsylvania, Maryland counties, New York City and
others are left out, so post-tax income is overstated there). We treat all
household income as wages of one earner aged 40, which overstates tax for
retirees and for households living on benefits. Three household types: single
with no children, married with no children, married with two children (ages 5
and 8). Refundable credits can make total tax negative for low-income
households, which puts post-tax income above pre-tax income. We take income
tax only from TAXSIM. The employee's payroll tax is computed in
`scripts/05_taxsim.py` from the statutory rates and wage bases (Social
Security Administration), because TAXSIM35's payroll output uses a 2023 wage
base of $153,600 against the statutory $160,200. For 2020-2024 we apply the
2024 wage base ($168,600) to the 2024-dollar income directly. TAXSIM35 run as one large batch returned Oregon 2023
state tax about $37,000 too low on every row (found October 7, 2026, when
Oregon's 2020-2024 bubbles turned dark green). The same households run alone
come back normal. Each period, household type and state is now its own TAXSIM
run, done twice in opposite income order, and the build stops unless the two
agree to the dollar and state tax is plausible. Two 2019 federal income tax
figures worked by hand from the brackets match TAXSIM to the dollar
(`scripts/10_tieout.py`).

**Uncertainty.** NBER says the model ignores some limits, floors and ceilings
on deductions. For wage-only households at these incomes the error is very
likely small against the assumptions above.

**License and attribution.** No formal license. NBER asks for this citation
when results are published: Feenberg, Daniel, and Elisabeth Coutts, "An
Introduction to the TAXSIM Model", Journal of Policy Analysis and Management
12(1), Winter 1993, pages 189-194, with the URL `taxsim.nber.org`.

## 5. Consumer Price Index, CPI-U, U.S. city average, all items (BLS)

**What it is.** Annual average of series CUUR0000SA0. Used to carry a typed-in
income, entered in 2024 dollars, back to each period's final year, and to
bring 2024 incomes to 2023 dollars for the tax model.

**Where it comes from.** BLS API v2, with `BLS_API_KEY`.

**Version and vintage.** Not seasonally adjusted, so not revised.

**Coverage.** 2009 to 2024, every year measured.

**Changes over time.** None that matters between 2009 and 2024.

**Suppressed, censored or masked values.** None in annual averages.

**Missing data.** October 2025 was not published because of the federal
shutdown; it does not affect the years we use.

**Revisions.** None.

**Units and rounding.** Index, 1982-84 = 100, three decimals.

**Known quirks.** The profile households (median, percentiles) do not use the
CPI at all: their income and the rents come from the same survey period.

**Uncertainty.** BLS publishes sampling error for 12-month changes of about
0.1 point.

**License and attribution.** Public domain. Credit: U.S. Bureau of Labor
Statistics.

## 6. Source coverage, measured (October 7, 2026)

- **Units.** 3,144 counties become 3,141 stable units. In every period the
  units add exactly to the national row for both rent and income. No unit is
  blank in any period.
- **Read directly, joined, or rebuilt.** 3,130 to 3,139 units per period are a
  single county read straight from the ACS. One or two are sums of counties.
  Nine (Connecticut's regions) are rebuilt from towns in the first three
  periods.
- **Income profiles.** In 2005-2009 only the median is published, so the 20th,
  40th, 60th and 80th percentile profiles are our estimates from income
  buckets: 80.1% of profile values in that period. From 2010-2014 on, under
  0.5% are estimated. Median renter income is published for 3,112 to 3,131
  units per period.
- **How close the estimates run.** Our straight-line median from buckets
  against the published median, single-county units: income within 0.3% to
  0.6% typically and 1.9% to 3.2% at the 95th percentile; rent within 0.04%
  typically. This checks our bucket handling. It does not check how rents are
  spread inside a bucket.
- **Top rent bucket.** At the default setting the rent ceiling lands in the
  open top bucket in 2 units in 2005-2009, 6 in 2010-2014 and none after.
- **Low reliability.** 5% to 6% of units in each period have under 200
  cash-rent units or an ACS margin implying a coefficient of variation over
  30%. They hold under 0.1% of rentals.
- **Dayton check.** Greene, Miami and Montgomery counties add to 116,730
  cash-rent units in 2015-2019 and 115,961 in 2020-2024, with 49.2% in
  buckets fully under $800 and 46.3% in buckets fully under $1,000 (the last
  bucket edge below the post's $1,100 line). These match the published Dayton
  post.

## 7. Limitations to state in the post (accepted by Eric, October 7, 2026)

1. Occupied units, not vacancies. The data says nothing about what is on the
   market today, and long-tenured or subsidized tenants raise the low-rent
   counts.
2. A cheap unit may already be taken by a higher-income household. The tool
   counts price, not availability.
3. Unit size is ignored. A studio and a three-bedroom count the same.
4. Each county is measured against its own household. A higher share does not
   mean cheaper rents.
5. Post-tax income is modeled: one wage earner, no other income, no local
   income taxes. Reach is overstated where local income taxes exist, and tax
   is overstated for retirees and households on benefits.
6. 30% of after-tax income is stricter than the usual standard, which uses
   pre-tax income. The shares are not comparable with published cost-burden
   figures unless the reader switches to "before taxes".
7. The 2020-2024 period is taxed under 2023 law and includes 2020, when
   pandemic disruption cut survey response.
8. Percentile profiles for 2005-2009 are our estimates. Census published only
   the median for that file. The renter median is our estimate from renter
   income buckets in 10 to 29 units per period (Connecticut's rebuilt regions,
   joined units, and small counties with no published figure); against the
   published figure elsewhere the estimate runs within 1.1% to 1.6% typically
   and 5.5% to 7.6% at the 95th percentile.
9. Inside a rent bucket we assume rents are spread evenly.
10. These are 5-year averages, each in its own final-year dollars.
11. Small counties are noisy. About 5% to 6% are marked low reliability; they
    hold under 0.1% of rentals.
12. The national and state figures are our sums, not a Census statistic.
13. The percentile profiles are for all households in the county; only the
    median is available for renters alone. Comparing profiles shows how reach
    differs along the income scale, not what happens to one household whose
    income falls.
14. College counties. Students who rent report little income, which pulls
    the renter median down and makes rentals look further out of reach than
    they are for non-student renters. We mark a county as a college county
    when 15% or more of its residents age 3 and over are enrolled in college
    or graduate school (ACS table B14001, 2020-2024): 71 counties. The page
    has a checkbox to leave them out of the map, the totals and the rankings.
    They are included by default. The 15% line is our choice.
15. Tax law is one year per period. Each period is taxed under its final
    year's law. 2009 law includes the Making Work Pay credit ($400 single,
    $800 joint), which existed only in 2009 and 2010. We take it out of the
    2005-2009 period (Eric, October 7, 2026): left in, it lifted that period
    for the median renter household from 31.95% to 34.54%. Other one-year
    features of a final year's law are not adjusted.
16. State tax law for 2020-2024 is 2021 law carried forward, so states that
    cut rates in 2022 or 2023 are taxed too high (North Carolina by about $365
    on $80,000, Idaho $380, Utah $250, Kentucky $237). North Carolina would
    read 34.3% against 33.9%. Oregon's 2019 law in the model is about 19%
    below 2018 and 2020, which fits a one-time rebate; Oregon's 2015-2019
    share would be 25.7% against 26.9% with 2018 law.
17. The household type used for taxes moves the result. Single instead of
    married with no children takes the 2020-2024 national figure from 31.3%
    to 26.9%.
18. Published median incomes for mid-sized counties swing between periods
    from sampling alone, and the share swings with them (Baldwin County,
    Georgia reads 80%, 46%, 80% across three periods for all households). The
    low-reliability mark now also covers a published median income whose
    margin of error is over 25% of the estimate (for the median renter
    household, 442 to 727 units per period holding about 1% of rentals), but
    swings inside that margin are not flagged. A 5% change in the rent ceiling moves a typical county's share
    by about 4 points.

## 8. Independent tie-out (fresh agent, October 7, 2026)

A separate agent pulled every ACS table again from the Census API, rebuilt the
units and the calculation with its own code, and ran TAXSIM one household per
process for the whole grid (98,532 runs) and once per county at the exact
county income (50,362 runs).

- Inlined data against its fresh pull: 282,690 rent cells, 12,564 no-cash-rent
  counts, 75,384 income profile values, 12,564 renter medians, 3,141 college
  flags. No mismatches.
- Geography: every code that differs from 2024 boundaries is covered by a
  rename or a join; units add to the national row in every period;
  Connecticut's 169 towns all assigned.
- Headline numbers for 13 settings across four periods: its figures match the
  page to under 0.005 points, and to within 0.02 points when it bypassed our
  tax grid entirely.
- Tax grid: no cell differs from one-household-per-process TAXSIM by more than
  $1. Federal tax by hand matched in 132 of 144 cases; the 12 others are at
  $220,000 or more in 2009 and 2014, where its hand calculation left out the
  exemption phaseout and the alternative minimum tax, so they are unverified.
  Payroll matches Social Security Administration figures. Six flat-tax states
  match published schedules to the dollar.
- It could not check: the even-spread assumption inside a rent bucket; ACS
  allocation rates; the 2005-2009 percentile estimates against any published
  figure; state schedules beyond about 12 states; map shapes.
- Method findings are limitations 15 to 18 above and the "at least" and
  top-code fixes made the same day.

## 9. Small counties with very low renter income (October 7, 2026)

Webster County, West Virginia shows a median renter income of $12,364 in
2020-2024 against $43,839 for all households. This is what the ACS publishes,
and it is consistent across the four periods ($13,933, $14,558, $16,068,
$12,364). About 77% of households there own; the 658 renter households are a
small and much poorer group. The margin of error on the 2020-2024 renter
median is plus or minus $5,346, 43% of the estimate. The typical county's
renter median is 62% of its all-household median; 41 units are under 40%.
These counties now carry the low-reliability mark when the margin is over 25%
of the estimate, and are left out of the rankings.
