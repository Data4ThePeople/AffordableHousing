"""Shared paths, frames, table layouts and HTTP helpers for the pipeline."""
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import get_key, load_env  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
UA = "Mozilla/5.0 (Macintosh) Data4ThePeople research"

# Seven frames that share no sample. key, label, source, income year (also the tax year)
FRAMES = [("1980", "1980", "nhgis", 1979), ("1990", "1990", "nhgis", 1989), ("2000", "2000", "sf3", 1999),
          ("2009", "2005-2009", "acs", 2009), ("2014", "2010-2014", "acs", 2014),
          ("2019", "2015-2019", "acs", 2019), ("2024", "2020-2024", "acs", 2024)]
FKEYS = [f[0] for f in FRAMES]
ACS_VINTAGES = [2009, 2014, 2019, 2024]

# Gross rent buckets: lower edge of every cash-rent bucket, in table order. The last one is open-ended.
RENT_1980 = [0, 60, 80, 100, 120, 150, 170, 200, 250, 300, 350, 400, 500]
RENT_1990 = [0, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 1000]
RENT_2000 = [0, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 900, 1000, 1250, 1500, 2000]
RENT_2015 = RENT_2000 + [2500, 3000, 3500]
RENT_EDGES = {"1980": RENT_1980, "1990": RENT_1990, "2000": RENT_2000, "2009": RENT_2000, "2014": RENT_2000,
              "2019": RENT_2015, "2024": RENT_2015}
# Household income buckets: lower edges, last one open-ended
INC_1980 = [0] + list(range(2500, 30000, 2500)) + [30000, 35000, 40000, 50000, 75000]
INC_1990 = [0, 5000] + list(range(10000, 50000, 2500)) + [50000, 55000, 60000, 75000, 100000, 125000, 150000]
INC_2000 = [0] + list(range(10000, 50000, 5000)) + [50000, 60000, 75000, 100000, 125000, 150000, 200000]
INC_EDGES = {"1980": INC_1980, "1990": INC_1990, **{k: INC_2000 for k in FKEYS[2:]}}
assert len(RENT_1980) == 13 and len(RENT_1990) == 16 and len(RENT_2000) == 21 and len(RENT_2015) == 24
assert len(INC_1980) == 17 and len(INC_1990) == 25 and len(INC_2000) == 16

STATE_INFO = {"01": ("AL", "Alabama"), "02": ("AK", "Alaska"), "04": ("AZ", "Arizona"), "05": ("AR", "Arkansas"),
              "06": ("CA", "California"), "08": ("CO", "Colorado"), "09": ("CT", "Connecticut"),
              "10": ("DE", "Delaware"), "11": ("DC", "District of Columbia"), "12": ("FL", "Florida"),
              "13": ("GA", "Georgia"), "15": ("HI", "Hawaii"), "16": ("ID", "Idaho"), "17": ("IL", "Illinois"),
              "18": ("IN", "Indiana"), "19": ("IA", "Iowa"), "20": ("KS", "Kansas"), "21": ("KY", "Kentucky"),
              "22": ("LA", "Louisiana"), "23": ("ME", "Maine"), "24": ("MD", "Maryland"),
              "25": ("MA", "Massachusetts"), "26": ("MI", "Michigan"), "27": ("MN", "Minnesota"),
              "28": ("MS", "Mississippi"), "29": ("MO", "Missouri"), "30": ("MT", "Montana"),
              "31": ("NE", "Nebraska"), "32": ("NV", "Nevada"), "33": ("NH", "New Hampshire"),
              "34": ("NJ", "New Jersey"), "35": ("NM", "New Mexico"), "36": ("NY", "New York"),
              "37": ("NC", "North Carolina"), "38": ("ND", "North Dakota"), "39": ("OH", "Ohio"),
              "40": ("OK", "Oklahoma"), "41": ("OR", "Oregon"), "42": ("PA", "Pennsylvania"),
              "44": ("RI", "Rhode Island"), "45": ("SC", "South Carolina"), "46": ("SD", "South Dakota"),
              "47": ("TN", "Tennessee"), "48": ("TX", "Texas"), "49": ("UT", "Utah"), "50": ("VT", "Vermont"),
              "51": ("VA", "Virginia"), "53": ("WA", "Washington"), "54": ("WV", "West Virginia"),
              "55": ("WI", "Wisconsin"), "56": ("WY", "Wyoming")}


def fetch(url, dest, tries=6):
    """Download url to dest unless it already exists. Returns False on 404."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    for i in range(tries):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=(20, 180))
            if r.status_code == 404:
                return False
            if r.status_code in (429, 503):
                time.sleep(5 * (i + 1))
                continue
            r.raise_for_status()
            tmp = dest.with_suffix(dest.suffix + ".part")
            tmp.write_bytes(r.content)
            os.replace(tmp, dest)
            return True
        except requests.RequestException:
            if i == tries - 1:
                raise
            time.sleep(2 ** i)
    raise RuntimeError(f"gave up on {url}")


def census(path, params, dest, tries=6):
    """One Census API call, cached on disk as JSON rows. Returns the rows (header first)."""
    dest = Path(dest)
    if not dest.exists():
        load_env()
        dest.parent.mkdir(parents=True, exist_ok=True)
        for i in range(tries):
            r = requests.get(f"https://api.census.gov/data/{path}", params={**params, "key": get_key("CENSUS_API_KEY")}, timeout=180)
            if r.status_code == 200:
                json.loads(r.text)
                dest.write_text(r.text)
                break
            if r.status_code == 204:
                dest.write_text("[]")
                break
            if i == tries - 1:
                raise RuntimeError(f"{path} {params.get('for')} {params.get('in', '')}: HTTP {r.status_code} {r.text[:200]}")
            time.sleep(3 * (i + 1))
    return json.loads(dest.read_text())
