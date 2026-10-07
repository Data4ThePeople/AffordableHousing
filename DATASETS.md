# Datasets

One section per dataset, written before any analysis, updated whenever we learn
something new. The measured coverage figures are in the last section, from
`scripts/08_coverage.py`.

The map has seven frames that share no survey sample: 1980, 1990, 2000,
2005-2009, 2010-2014, 2015-2019 and 2020-2024.

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
("allocation"). Share of gross rent answers allocated: to measure from B25063's
companion allocation table where published.

**Changes over time.** Buckets are the same from 2005-2009 through 2010-2014:
under $100, $50 steps to $799, $800-899, $900-999, $1,000-1,249,
$1,250-1,499, $1,500-1,999, and $2,000 or more. From the 2011-2015 file on,
the top bucket is split into $2,000-2,499, $2,500-2,999, $3,000-3,499 and
$3,500 or more, and the "no cash rent" cell moves from _024 to _027. So our
2005-2009 and 2010-2014 frames top out at $2,000 and the last two at $3,500.
Connecticut is reported for eight counties through the 2017-2021 file and for
nine planning regions from 2018-2022 on.

**Suppressed, censored or masked values.** The top bucket is open-ended. When
a rent ceiling lands inside it we report "at least" the share below it. No
cells are suppressed in B25063 at county level, but small counties have
estimates of zero in many buckets with wide margins.

**Missing data.** Annotation values such as -666666666 appear in median tables,
not in bucket counts. A county with zero renter units paying cash rent has no
share.

**Revisions.** None. We pin the four vintages.

**Units and rounding.** Housing units. Dollars are nominal. In a 5-year file
rents reported in earlier years are adjusted by the Census Bureau to the final
year's dollars with the CPI before bucketing.

**Known quirks.** The universe is all renter-occupied units. The decennial
tables (sections 4 and 5) leave out one-family houses on 10 or more acres. Not
corrected; the difference is very likely small in most counties but is larger
in farm counties. Rents cluster at round numbers, which sit at bucket floors,
so a straight-line spread inside a bucket is an approximation.

**Uncertainty.** Margins of error are published at the 90% level for every
cell. We carry the margin on total renter-occupied units per county and mark
counties where it is large against the estimate.

**License and attribution.** Public domain. Credit: U.S. Census Bureau,
American Community Survey 5-year estimates, table B25063.

## 2. ACS 5-year income tables B19001, B19013, B19080, B25119 (Census Bureau)

**What it is.** B19001: households by income bucket (16 buckets, top $200,000
or more). B19013: median household income. B19080: upper limits of the first
four household income quintiles (the 20th, 40th, 60th and 80th percentiles)
and the lower limit of the top 5%. B25119: median household income by tenure
(all, owner, renter).

**Where it comes from.** Census API, same endpoint and cache as section 1.

**Version and vintage.** Same four vintages.

**Coverage.** Counties, states, nation, Connecticut towns. B19080 does not
exist in the 2005-2009 file; it starts with 2006-2010. Where a percentile is
not published we estimate it by straight-line interpolation inside the B19001
bucket that contains it, and the page marks the value as estimated. Share of
profile values published against estimated, by frame: to measure.

**Changes over time.** B19001 buckets are unchanged across all four vintages
and match the 2000 census table P52.

**Suppressed, censored or masked values.** Medians are top-coded at 250,001
and bottom-coded at 2,499 (shown as "250,000+" and "2,500-"). B19080 values
are missing for some small counties (negative annotation codes). We treat
those as not published and interpolate.

**Missing data.** Negative values (-666666666 and similar) mean no estimate.

**Revisions.** None.

**Units and rounding.** Dollars of the final year of the 5-year period. Income
is money income before taxes. It leaves out noncash benefits and tax credits
such as the Earned Income Tax Credit.

**Known quirks.** Income in the past 12 months is collected all year, so the
reference period is not a calendar year. Rebuilt Connecticut regions have no
published median for the six earlier frames; we interpolate from summed
buckets.

**Uncertainty.** Published margins of error at the 90% level. Not carried into
the page for income; the rent-side reliability mark covers thin counties.

**License and attribution.** Public domain. Credit: U.S. Census Bureau,
American Community Survey 5-year estimates.

## 3. Census 2000 Summary File 3, tables H62, H63, P52, P53 (Census Bureau)

**What it is.** H62: specified renter-occupied housing units by gross rent (21
cash-rent buckets, top $2,000 or more, plus no cash rent). H63: median gross
rent. P52: households by income in 1999 (16 buckets, top $200,000 or more).
P53: median household income in 1999. From the long form, a sample of about 1
in 6 households.

**Where it comes from.** Census API, `api.census.gov/data/2000/dec/sf3`.

**Version and vintage.** Final. Not revised.

**Coverage.** Counties, states, nation, Connecticut towns, and the parts of
Broomfield city, Colorado, in each of its four counties (summary level 155).

**Changes over time.** Rent and income buckets match the ACS through 2010-2014.

**Suppressed, censored or masked values.** Open-ended top buckets. No county
cells suppressed.

**Missing data.** None at county level.

**Revisions.** None.

**Units and rounding.** Rent in 2000 dollars; income for calendar 1999.

**Known quirks.** "Specified" renter-occupied leaves out one-family houses on
10 or more acres. Broomfield County did not exist until November 15, 2001.

**Uncertainty.** Sample data; SF3 publishes no cell margins. Sampling error is
larger in small counties.

**License and attribution.** Public domain. Credit: U.S. Census Bureau, Census
2000 Summary File 3.

## 4. 1980 and 1990 census long-form tables, via IPUMS NHGIS

**What it is.** 1980 STF 3: NT68 households by income in 1979 (17 buckets, top
$75,000 or more), NT69 median household income, NT124 specified
renter-occupied units by gross rent (13 cash-rent buckets, top $500 or more,
plus no cash rent), NT127 median gross rent. 1990 STF 3: NP80 households by
income in 1989 (25 buckets, top $150,000 or more), NP80A median, NH43 gross
rent (16 cash-rent buckets, top $1,000 or more, plus no cash rent), NH43A
median, NH91 imputation of gross rent, NP167 imputation of household income.

**Where it comes from.** IPUMS NHGIS extract through the IPUMS API
(`scripts/01_fetch_nhgis.py`), CSV with codebooks, into `data/raw/nhgis/`.
Needs a free IPUMS account and API key. Neither year is on the Census API.

**Version and vintage.** NHGIS Version 21.0 (2026). The underlying tables are
final.

**Coverage.** Nation, states, counties and county subdivisions. Long form:
about 1 in 6 households in 1990, about 1 in 5 in 1980 (1 in 2 in places under
2,500 people). Share of answers imputed by the Census Bureau, 1990: to measure
from NH91 and NP167. 1980 STF 3 has no imputation table for these items in
our extract.

**Changes over time.** Bucket edges differ in each census (see
`scripts/common.py`). 1980 collected electricity and gas as average monthly
costs; 1990 collected yearly utility costs and divided by 12. County lists
differ from today's; section 6 covers how we handle that. NHGIS links units by
name and code only and does not adjust for boundary changes.

**Suppressed, censored or masked values.** 1980 STF 3 suppressed tables for
areas with very few people or housing units; the file carries 27 suppression
flags per row, and a suppressed table reads as zeros. We read the flags and
treat a suppressed rent or income table as missing, not zero. Top buckets are
open-ended: $500 in 1980 and $1,000 in 1990 for rent.

**Missing data.** A missing median is 0 in the file.

**Revisions.** NHGIS reissues files with corrections under new version
numbers. We pin the extract and keep its definition in
`data/raw/nhgis/extract_definition.json`.

**Units and rounding.** Nominal dollars; income for 1979 and 1989; rent for
the census month.

**Known quirks.** "Specified" renter-occupied leaves out one-family houses on
10 or more acres. 1980 medians are published only for cash-rent units. A unit
with no cash contract rent stays "no cash rent" even if the tenant pays
utilities.

**Uncertainty.** Sample data with no published cell margins.

**License and attribution.** The tables are Census Bureau products, but the
files come under the IPUMS terms of use: we may not redistribute the data
without permission, and we must cite NHGIS. The raw extract is not in git. The
published page would carry county rent buckets for 1980 and 1990 taken from
this extract, so **we need IPUMS's permission before the page is public**
(ipums@umn.edu). IPUMS also asks that the title and citation of anything
published with the data be added to its bibliography. Citation:

> Jonathan Schroeder, David Van Riper, Steven Manson, Grace Cooper, Zachary
> Krause, Tracy Kugler, Tsu Zhu, and Steven Ruggles. IPUMS National Historical
> Geographic Information System: Version 21.0 [dataset]. Minneapolis, MN:
> IPUMS. 2026. http://doi.org/10.18128/D050.V21.0

Short form for the page footer: "IPUMS NHGIS, University of Minnesota,
www.nhgis.org".

## 5. County boundaries and changes (Census Bureau)

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
frame.

**Coverage.** 50 states and DC. Puerto Rico is left out.

**Changes over time.** Every change since 1980 that Census lists as
substantial is handled in `scripts/04_geo_units.py`: renames by code map,
merged or annexed Virginia cities by joining city and county, nesting Alaska
splits by joining the pieces, Connecticut by rebuilding the nine regions from
169 towns in every frame. A unit shows an earlier frame only if the population
moved is under 1% of the unit or the frame was rebuilt exactly from smaller
pieces. Otherwise it is blank for that frame.

**Suppressed, censored or masked values.** None.

**Missing data.** None.

**Revisions.** Census reissues boundary files yearly. Pinned to 2024.

**Units and rounding.** Simplified for drawing; shapes are not used for any
calculation.

**Known quirks.** Census counts a change as substantial at 200 or more people
or 10 square miles. Smaller annexations between Virginia cities and counties
are not corrected. Connecticut towns nest exactly in both the old counties and
the planning regions; the regions do not nest in the counties.

**Uncertainty.** Not applicable.

**License and attribution.** Public domain. Credit: U.S. Census Bureau.

## 6. TAXSIM35 (National Bureau of Economic Research)

**What it is.** A tax calculator. Given a tax year, state, filing status,
dependents and income, it returns federal income tax, state income tax and
payroll (FICA) tax. We use it to turn a pre-tax household income into a
post-tax one.

**Where it comes from.** `taxsim.nber.org/taxsim35/`, the offline binary for
macOS, CSV in and out. No login.

**Version and vintage.** TAXSIM35. Federal law through 2023; state law 1977
through 2021, with 2022 and later computed from 2021 state law carried forward
at "real" values. The offline program refuses tax year 2024. Our 2020-2024
frame is in 2024 dollars, so we bring each income to 2023 dollars with the
CPI-U, tax it under 2023 law, and scale the tax back up.

**Coverage.** All states and DC. Federal from 1960, state from 1977, so all
seven frames are covered. Everything it returns is modeled, not measured.

**Changes over time.** Tax law itself: the Earned Income Tax Credit grows in
1986, 1990 and 1993; the child tax credit starts in 1998; payroll tax rates
rise through 1990.

**Suppressed, censored or masked values.** None.

**Missing data.** None.

**Revisions.** NBER updates the program as laws change. We keep the grid we
computed in `data/processed/tax_grid.csv`.

**Units and rounding.** Dollars of the tax year.

**Known quirks and our assumptions.** No local income taxes (city and school
district taxes in Ohio, Pennsylvania, Maryland counties, New York City and
others are left out, so post-tax income is overstated there). We treat all
household income as wages of one earner aged 40, which overstates tax for
retirees and for households living on benefits. Three household types: single
with no children, married with no children, married with two children. We
take income tax only from TAXSIM. Payroll tax is computed in
`scripts/05_taxsim.py` from the statutory employee rates and wage bases
(Social Security Administration), because TAXSIM35's payroll output does not
match the law in two of our years: it returns 5.6% of wages for 1979 against
the statutory 6.13%, and a 2023 wage base of $153,600 against $160,200. Its
1989 to 2019 figures match the statute. Three 1979 federal income tax figures
worked by hand from the rate schedules match TAXSIM to the dollar
(`scripts/10_tieout.py`). Refundable credits can make
total tax negative for low-income households with children, which puts
post-tax income above pre-tax income.

**Uncertainty.** NBER says the model ignores some limits, floors and ceilings
on deductions. For wage-only households at these incomes the error is very
likely small against the assumptions above.

**License and attribution.** No formal license. NBER asks for this citation
when results are published: Feenberg, Daniel, and Elisabeth Coutts, "An
Introduction to the TAXSIM Model", Journal of Policy Analysis and Management
12(1), Winter 1993, pages 189-194, with the URL `taxsim.nber.org`.

## 7. Consumer Price Index, CPI-U, U.S. city average, all items (BLS)

**What it is.** Annual average of series CUUR0000SA0. Used only to carry a
typed-in income, entered in 2024 dollars, back to each frame's income year.

**Where it comes from.** BLS API v2, with `BLS_API_KEY`.

**Version and vintage.** Not seasonally adjusted, so not revised.

**Coverage.** 1979 to 2024, every year measured.

**Changes over time.** The method for housing costs changed in 1983. BLS does
not restate earlier years in CPI-U, so 1979 dollars are slightly overstated
against a consistent method (the CPI-U-RS series corrects this). We use CPI-U
because it is the headline series readers know.

**Suppressed, censored or masked values.** None in annual averages.

**Missing data.** October 2025 was not published because of the federal
shutdown; it does not affect the years we use.

**Revisions.** None.

**Units and rounding.** Index, 1982-84 = 100, one decimal through 2006, three
after.

**Known quirks.** The profile households (median, percentiles) do not use the
CPI at all: their income and the rents come from the same survey.

**Uncertainty.** BLS publishes sampling error for 12-month changes of about
0.1 point.

**License and attribution.** Public domain. Credit: U.S. Bureau of Labor
Statistics.

## 8. Source coverage, measured (October 7, 2026)

From `scripts/08_coverage.py` and `scripts/03_harmonize.py`.

- **Units.** 3,144 counties become 3,120 stable units. 21 units join two or
  more counties or cities. In every frame the units add exactly to the
  national row for both rent and income. Three units are blank in 1980 and
  1990 (Boulder, Adams and Broomfield, Colorado).
- **Read directly, joined, or rebuilt.** 3,086 to 3,103 of the 3,120 units are
  a single county read straight from the source in each frame. 16 to 20 are
  sums of counties. 9 to 14 are rebuilt from smaller areas (Connecticut's nine
  regions in six frames; La Paz, Yuma, Cibola and Valencia in 1980; Broomfield
  and its four parents in 2000).
- **Income profiles.** In 1980, 1990, 2000 and 2005-2009 only the median is
  published, so the four percentile profiles are our estimates: 80.2% of
  profile values in those frames. From 2010-2014 on, under 1% are estimated.
  Median renter income exists only in the four ACS frames.
- **How close the estimates run.** Our straight-line median from buckets
  against the published median, single-county units: income within 0.4%
  typically and 2% to 3% at the 95th percentile in the ACS frames, and equal
  in 1980 and 1990; rent within 0.1% typically. The Census Bureau computes its
  medians the same way from finer buckets, so this checks our bucket handling.
  It does not check how rents are spread inside a bucket.
- **Top rent bucket.** At the default setting the rent ceiling lands in the
  open top bucket in 14 units in 1980, 6 in 1990, 0 in 2000, 2 in 2005-2009,
  6 in 2010-2014 and none after.
- **Low reliability.** 5% to 7% of units in each frame have under 200
  cash-rent units or an ACS margin implying a coefficient of variation over
  30%. They hold under 0.1% of rentals.
- **Imputed answers, 1990.** The Census Bureau filled in gross rent for 6.6%
  of renter units and some part of income for 18.9% of households. The 1980
  file in our extract has no equivalent table, and we did not pull the ACS
  allocation tables.
- **1980 suppression.** No county, and none of the county divisions we use,
  carries a suppression flag for total population, housing units, occupied
  units or renter-occupied units.
- **1980 La Paz and Cibola.** Rebuilt from the 1980 county divisions of Yuma
  (Parker division to La Paz) and Valencia (Fence Lake, Grants, Laguna and
  Zuni-Ramah Navajo divisions to Cibola). The divisions add exactly to the
  1980 counties. That each division lies wholly on one side of the later
  county line is our reading of the division names and household counts; it
  has not been checked against a 1980 boundary file.
- **Not corrected.** The 2007 land exchange between York County and Newport
  News, Virginia, and other changes under the Census threshold of 200 people.
- **Dayton check.** Greene, Miami and Montgomery counties add to 116,730
  cash-rent units in 2015-2019 and 115,961 in 2020-2024, with 49.2% and 46.3%
  in buckets fully under $800 and $1,100. These match the published Dayton
  post.
