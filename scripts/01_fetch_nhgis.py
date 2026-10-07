"""Request and download the 1980 and 1990 long-form tables from IPUMS NHGIS.

1980 STF 3: NT68 household income (17 buckets), NT69 median household income, NT124 gross rent
(13 buckets + no cash rent), NT127 median gross rent.
1990 STF 3: NP80 household income (25), NP80A median, NH43 gross rent (16 + no cash rent), NH43A median,
NH91 imputation of gross rent, NP167 imputation of household income.
Levels: nation, state, county, county subdivision (towns rebuild Connecticut's planning regions and
the 1980 Yuma/La Paz and Valencia/Cibola splits).
IPUMS terms: the extract is not redistributed. It stays in data/raw/, which is not in git.
Output: data/raw/nhgis/extract.zip, unpacked CSVs and codebooks next to it."""
import json
import time
import zipfile

import requests

from common import RAW, get_key, load_env

API = "https://api.ipums.org/extracts"
Q = {"collection": "nhgis", "version": 2}
LEVELS = ["nation", "state", "county", "cty_sub"]
BODY = {"description": "D4TP affordable rentals: gross rent and household income, 1980 and 1990",
        "dataFormat": "csv_header", "breakdownAndDataTypeLayout": "single_file",
        "datasets": {"1980_STF3": {"dataTables": ["NT68", "NT69", "NT124", "NT127"], "geogLevels": LEVELS},
                     "1990_STF3": {"dataTables": ["NP80", "NP80A", "NH43", "NH43A", "NH91", "NP167"], "geogLevels": LEVELS}}}


def main():
    load_env()
    h = {"Authorization": get_key("IPUMS_API_KEY")}
    d = RAW / "nhgis"
    d.mkdir(parents=True, exist_ok=True)
    z = d / "extract.zip"
    if not z.exists():
        num = d / "extract_number.txt"
        if not num.exists():
            r = requests.post(API, params=Q, headers=h, json=BODY, timeout=120)
            assert r.ok, r.text[:500]
            num.write_text(str(r.json()["number"]))
        n = num.read_text().strip()
        while True:
            j = requests.get(f"{API}/{n}", params=Q, headers=h, timeout=120).json()
            print("extract", n, j["status"])
            if j["status"] == "completed":
                break
            assert j["status"] in ("queued", "started", "produced"), j
            time.sleep(20)
        (d / "extract_definition.json").write_text(json.dumps(j["extractDefinition"], indent=1))
        r = requests.get(j["downloadLinks"]["tableData"]["url"], headers=h, timeout=600)
        r.raise_for_status()
        z.write_bytes(r.content)
    with zipfile.ZipFile(z) as f:
        f.extractall(d)
        for n in f.namelist():
            print(n)


if __name__ == "__main__":
    main()
