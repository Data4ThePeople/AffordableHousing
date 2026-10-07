"""Download the ACS 5-year tables from the Census API.

ACS (2005-2009, 2010-2014, 2015-2019, 2020-2024): B25063 gross rent, B19001 household income,
B19013 median household income, B19080 quintile limits (not in 2005-2009), B25119 median income by
tenure, B25118 renter households by income (for areas with no published renter median), B25064 median gross rent.
Levels: nation, states, counties, Connecticut towns.
Output: data/raw/acs/*.json"""
from common import ACS_VINTAGES, RAW, census

GEOS = {"us": {"for": "us:1"}, "state": {"for": "state:*"}, "county": {"for": "county:*", "in": "state:*"},
        "cttown": {"for": "county subdivision:*", "in": "state:09"}}
ACS_GROUPS = ["B25063", "B19001", "B19013", "B19080", "B25119", "B25118", "B25064"]


def main():
    for v in ACS_VINTAGES:
        for g in ACS_GROUPS:
            if g == "B19080" and v == 2009:
                continue
            for name, geo in GEOS.items():
                rows = census(f"{v}/acs/acs5", {"get": f"group({g})", **geo}, RAW / "acs" / f"{g}_{v}_{name}.json")
                print(v, g, name, len(rows) - 1)


if __name__ == "__main__":
    main()
