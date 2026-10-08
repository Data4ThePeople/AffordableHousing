# Rentals Within Reach

An interactive map of every U.S. county showing the share of rental homes a
household can afford at 30% of its income, across four periods from 2005-2009
to 2020-2024. Free to use. Built by [Data 4 The People](https://www.data4thepeople.com).

**Open the map:** https://data4thepeople.github.io/AffordableHousing/

Nothing you enter leaves your browser. The page is one self-contained file. It
loads no outside scripts and sends no data anywhere.

## How to use it

1. **Read the map.** Each bubble is a county, sized by its number of rentals.
   The color is the share of those rentals priced at or under what the
   household can pay. Dark red is under 30%, red is 30% to 40%, orange is 40%
   to 50%, yellow is 50% to 65%, light green is 65% to 80%, and dark green is
   80% and up. Under 50%, the household cannot afford the middle rental in its
   own county.
2. **Pick the household income.** The map starts with each county's median
   renter household. You can switch to the median of all households, or to
   the 20th, 40th, 60th or 80th percentile of all households in the county.
3. **Or enter an income.** Choose "Enter an income" and type a yearly income
   in 2024 dollars. The same income is then used in every county. For earlier
   periods it is carried back with the Consumer Price Index.
4. **Set the share of income for rent.** The slider starts at 30% and runs
   from 10% to 50%.
5. **Count income before or after taxes.** "After taxes" is the default. It
   takes off federal and state income tax and payroll tax. "Taxed as" sets the
   household used for that: single with no children, married with no children
   (the default), or married with two children.
6. **Move through time.** Drag the Period slider or press Play to step through
   2005-2009, 2010-2014, 2015-2019 and 2020-2024.
7. **Zoom to one state** with "Show one state". Scroll or pinch to zoom
   further, and drag to pan.
8. **Leave out college counties** with the checkbox. Students who rent report
   little income, which pulls the renter median down in those counties.
9. **Click a county, or search for one by name.** The panel on the right shows:
   - the share of rentals priced within reach
   - the math: income, taxes, income after taxes, and the monthly rent ceiling
   - the two direct Census reads on either side of our estimate
   - the county's rentals by monthly rent, with the ceiling drawn across them
     (hover a bar for its count)
   - the change in all rentals and in rentals priced within reach from
     2005-2009 to 2020-2024
10. **Use the rankings** under the county panel to jump to the counties with
    the fewest or the most rentals within reach.
11. **Reset** puts every control back to its starting setting.

## What the number means

For one county and one period:

1. Take a yearly household income.
2. If "After taxes" is on, subtract federal income tax, state income tax and
   the employee's payroll tax.
3. Multiply by the share of income for rent (30% by default) and divide by 12.
   That is the monthly rent ceiling.
4. Count the county's rentals with gross rent at or under the ceiling, as a
   share of all its rentals that pay cash rent.

Gross rent is the rent plus the estimated cost of utilities when the tenant
pays them. The headline above the map adds every county's rentals within reach
of that county's own household. That sum is ours. It is not a Census figure.

## Data

- **Rents:** U.S. Census Bureau, American Community Survey 5-year estimates,
  table B25063 (gross rent), for 2005-2009, 2010-2014, 2015-2019 and
  2020-2024. These four periods share no survey sample, which is why the map
  has four steps and not sixteen.
- **Incomes:** the same four files. B25119 (median income of renter
  households), B19013 (median household income), B19080 (income quintile
  limits), B19001 (households by income) and B25118 (renter households by
  income).
- **Taxes:** NBER TAXSIM 35 for federal and state income tax (Feenberg and
  Coutts, "An Introduction to the TAXSIM Model", Journal of Policy Analysis
  and Management, 1993, taxsim.nber.org), and Social Security Administration
  rates and wage bases for payroll tax.
- **Prices:** Bureau of Labor Statistics, CPI-U, U.S. city average, annual
  averages. Used only for a typed-in income.
- **Boundaries:** Census Bureau cartographic boundary files, 2024.

Full notes on each source, with its quirks and how we handled them, are in
[DATASETS.md](DATASETS.md).

## Method notes

- **Inside a rent bucket.** The Census Bureau publishes rents in buckets, such
  as $1,000 to $1,249. When the ceiling falls inside a bucket we assume the
  rents in it are spread evenly. The county panel also shows the two direct
  reads: buckets fully under the ceiling, and that figure plus the bucket the
  ceiling falls in.
- **Top of the rent scale.** The top bucket is "$2,000 or more" in the first
  two periods and "$3,500 or more" in the last two. When the ceiling is above
  that, the figure is shown as "at least".
- **Percentiles before 2010.** The Census Bureau did not publish income
  quintile limits for 2005-2009. For that period we estimate the 20th, 40th,
  60th and 80th percentiles from the income buckets, and the page says so.
- **Renter median where none is published.** For a few areas we estimate it
  from renter income buckets, and the page says so.
- **County changes.** The map is drawn on 2024 boundaries. Connecticut's nine
  planning regions are rebuilt from town data for the three earlier periods.
  Bedford County and Bedford city, Virginia, are joined. Two groups of Alaska
  areas whose boundaries changed are joined. Counts are only ever added, never
  split by area.
- **Taxes.** One wage earner aged 40 with no other income. Each period uses
  the tax law of its last year, except that the 2009 Making Work Pay credit is
  removed because it lasted only two years. The 2020-2024 period uses 2023
  law. Payroll tax is the employee's share.
- **College counties.** A county where 15% or more of residents are enrolled
  in college or graduate school (ACS table B14001, 2020-2024). There are 71.
- **Low reliability.** A county is marked when it has fewer than 200 rentals,
  or when the margin of error on its rentals or on its median income is
  large. Marked counties are left out of the rankings.

## What this does not tell you

- **It counts occupied rentals, not vacancies.** The data records what current
  tenants pay. It says nothing about what is on the market today, and
  long-time or subsidized tenants raise the count of low-rent units.
- **A low-rent unit may already be taken by a higher-income household.** The
  tool counts price, not availability.
- **Unit size is ignored.** A studio and a three-bedroom count the same.
- **Each county is measured against its own household,** unless you enter an
  income. A higher share does not mean cheaper rents.
- **After-tax income is modeled.** Local income taxes are not counted, so the
  share is too high where they exist. All income is treated as wages, which
  overstates tax for retirees and households on benefits.
- **30% of after-tax income is stricter than the usual standard,** which uses
  income before taxes. Switch to "Before taxes" to compare with published
  cost-burden figures.
- **State tax law for 2020-2024 is 2021 law carried forward,** so states that
  cut rates since then are taxed slightly too high.
- **The household type used for taxes moves the result.** Single in place of
  married with no children lowers the national figure by about 4 points.
- **These are 5-year averages,** each in its own final-year dollars.
- **Small counties are noisy.** Published medians for small and mid-sized
  counties move between periods from sampling alone.
- **The pool of renters changes over time.** A rising median renter income
  does not mean the same renters are doing better. For change over time, a
  fixed typed-in income is the cleaner read.

The full list, with the numbers behind each point, is in
[DATASETS.md](DATASETS.md), section 7.

## How it was checked

- A tie-out script recomputes every figure in the page from the downloaded
  Census files and stops the build on any difference.
- A second, independent check pulled the Census tables again, rebuilt the
  calculation with separate code, and ran the tax model one household at a
  time. Its figures matched the page to within 0.02 percentage points.

## Rebuild it yourself

You need Python 3.9 or later, a free Census API key and a free BLS API key in
your environment as `CENSUS_API_KEY` and `BLS_API_KEY`, and the TAXSIM 35
program from taxsim.nber.org saved in `data/raw/taxsim/`.

The scripts read keys and a contact address for the download User-Agent
through a small helper that is kept outside this repo. To run them elsewhere,
replace `get_key(...)` and `load_env()` in `scripts/common.py` with reads from
`os.environ`, and set `D4TP_CONTACT_EMAIL` to your own address.

```
pip install -r requirements.txt
cd scripts
python 02_fetch_census.py     # ACS tables
python 03_harmonize.py        # stable county units
python 04_cpi.py              # CPI-U
python 05_taxsim.py           # tax grid
python 06_build_geo.py        # shapes
python 07_build_data.py       # data for the page
python 08_coverage.py         # what is measured and what is estimated
python 09_build_viz.py        # dist/index.html
python 10_tieout.py           # the tie-out
```

## Credit and reuse

Data: U.S. Census Bureau, American Community Survey; NBER TAXSIM; Social
Security Administration; Bureau of Labor Statistics. The underlying data is in
the public domain. Please credit Data 4 The People when you use the map or
figures from it. Terms: https://www.data4thepeople.com/terms-of-use
