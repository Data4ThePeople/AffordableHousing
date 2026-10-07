# Datasets

One section per dataset, written before any analysis, updated whenever we learn
something new. Figures marked "to measure" are filled in by
`scripts/10_coverage.py`.

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
at "real" values. Our 2020-2024 frame uses tax year 2023, the last year
TAXSIM35 has federal law for, not 2024.

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
count the employee's share of payroll tax only. Refundable credits can make
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
