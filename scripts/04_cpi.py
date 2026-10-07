"""CPI-U, U.S. city average, all items, annual averages 2009 to 2024 (BLS series CUUR0000SA0).
Used only to carry a typed-in income, entered in 2024 dollars, back to each frame's income year,
and to bring 2024 incomes to 2023 dollars for the tax model.
Output: data/raw/bls/cpi_*.json, data/processed/cpi.json"""
import json

import requests

from common import PROC, RAW, get_key, load_env


def main():
    load_env()
    out = {}
    for a, b in [(2009, 2024)]:
        dest = RAW / "bls" / f"cpi_{a}_{b}.json"
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",
                              json={"seriesid": ["CUUR0000SA0"], "startyear": str(a), "endyear": str(b), "annualaverage": True,
                                    "registrationkey": get_key("BLS_API_KEY")}, timeout=90)
            r.raise_for_status()
            assert r.json()["status"] == "REQUEST_SUCCEEDED", r.text[:300]
            dest.write_text(r.text)
        for d in json.loads(dest.read_text())["Results"]["series"][0]["data"]:
            if d["period"] == "M13":
                assert d["year"] not in out, "duplicate year"
                out[d["year"]] = float(d["value"])
    assert sorted(out) == [str(y) for y in range(2009, 2025)], sorted(out)
    (PROC / "cpi.json").write_text(json.dumps(dict(sorted(out.items()))))
    print({y: out[y] for y in ("2009", "2014", "2019", "2023", "2024")})


if __name__ == "__main__":
    main()
