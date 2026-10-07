"""Download the ACS 5-year and Census 2000 tables from the Census API.

ACS (2005-2009, 2010-2014, 2015-2019, 2020-2024): B25063 gross rent, B19001 household income,
B19013 median household income, B19080 quintile limits (not in 2005-2009), B25119 median income by
tenure, B25064 median gross rent. Census 2000 SF3: H062, H063, P052, P053.
Levels: nation, states, counties, Connecticut towns; for 2000 also the county parts of Broomfield city.
Output: data/raw/acs/*.json, data/raw/sf3/*.json"""
from common import ACS_VINTAGES, RAW, census

GEOS = {"us": {"for": "us:1"}, "state": {"for": "state:*"}, "county": {"for": "county:*", "in": "state:*"},
        "cttown": {"for": "county subdivision:*", "in": "state:09"}}
ACS_GROUPS = ["B25063", "B19001", "B19013", "B19080", "B25119", "B25064"]
SF3 = [f"H062{i:03d}" for i in range(1, 25)] + [f"P052{i:03d}" for i in range(1, 18)] + ["H063001", "P053001"]


def main():
    for v in ACS_VINTAGES:
        for g in ACS_GROUPS:
            if g == "B19080" and v == 2009:
                continue
            for name, geo in GEOS.items():
                rows = census(f"{v}/acs/acs5", {"get": f"group({g})", **geo}, RAW / "acs" / f"{g}_{v}_{name}.json")
                print(v, g, name, len(rows) - 1)
    geos = dict(GEOS, broomfield={"for": "county (or part):*", "in": "state:08 place:09280"})
    for name, geo in geos.items():
        rows = census("2000/dec/sf3", {"get": "NAME," + ",".join(SF3), **geo}, RAW / "sf3" / f"sf3_{name}.json")
        print(2000, name, len(rows) - 1)


if __name__ == "__main__":
    main()
