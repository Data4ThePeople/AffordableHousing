"""Put the four ACS periods on one set of stable county units drawn on 2024 boundaries.

Bucket counts are only ever added, never split by area, so every unit is exact.
  renames            Shannon County SD -> Oglala Lakota (2015), Wade Hampton AK -> Kusilvak (2015)
  merges             areas whose boundaries changed after 2009 are joined into one unit in every period:
                     Bedford city into Bedford County VA (2013); Valdez-Cordova AK split into Chugach
                     and Copper River (2019); Petersburg, Hoonah-Angoon and Prince of Wales-Hyder AK
                     (land and 613 people moved among them in 2013)
  Connecticut        the nine planning regions are rebuilt from the 169 towns in the three periods
                     before 2020-2024 (towns nest exactly in the regions)
Output: data/processed/harmonized.json"""
import json
import math
import re

import geopandas as gpd
import pandas as pd

from common import COLLEGE_SHARE, FKEYS, PROC, RAW, RENT_EDGES, STATE_INFO

RENAME = {"46113": "46102", "02270": "02158"}
# unit id -> (label, member codes in any period)
MERGES = {
    "02063": ("Chugach + Copper River Census Areas, AK", ["02261", "02063", "02066"]),
    "02195": ("Petersburg + Hoonah-Angoon + Prince of Wales-Hyder, AK", ["02195", "02105", "02198"]),
    "51019": ("Bedford County + Bedford city, VA", ["51019", "51515"]),
}
MEMBER = {m: u for u, (_, ms) in MERGES.items() for m in ms}


def unit_of(code):
    code = RENAME.get(code, code)
    return MEMBER.get(code, code)


def num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def rec(rent, nocash, inc, mi=None, mr=None, q=None, ri=None, moe=None, alloc=None, ti=None, pm=None):
    return {"r": [int(x) for x in rent], "nc": int(nocash), "i": [int(x) for x in inc], "ti": [int(x) for x in ti], "mi": mi, "mr": mr, "q": q, "ri": ri,
            "moe": moe, "al": alloc, "pm": pm, "n": 1}


def add(a, b, sign=1):
    """Sum (or subtract) two records. Published medians do not survive."""
    if a is None:
        assert sign == 1
        return dict(b, n=1)
    moe = None if a["moe"] is None or b["moe"] is None else math.hypot(a["moe"], b["moe"])
    al = None if a["al"] is None or b["al"] is None else [x + sign * y for x, y in zip(a["al"], b["al"])]
    out = {"r": [x + sign * y for x, y in zip(a["r"], b["r"])], "nc": a["nc"] + sign * b["nc"], "i": [x + sign * y for x, y in zip(a["i"], b["i"])],
           "ti": [x + sign * y for x, y in zip(a["ti"], b["ti"])],
           "mi": None, "mr": None, "q": None, "ri": None, "moe": moe, "al": al, "pm": None, "n": a["n"] + 1}
    assert min(out["r"]) >= 0 and min(out["i"]) >= 0 and out["nc"] >= 0
    return out


# ---------- reader: returns {level: {code: record}} with level in us, state, county, town ----------
def norm(name):
    return re.sub(r"[^a-z]", "", re.sub(r"\b(town)\b", "", str(name).lower()))


def code_of(level, row, h):
    if level == "us":
        return "us"
    st = row[h["state"]]
    if st not in STATE_INFO:
        return None
    if level == "state":
        return st
    if level == "county":
        return st + row[h["county"]]
    return (st, row[h["county"]], None, row[h["county subdivision"]])


def read_acs(v):
    nr = len(RENT_EDGES[str(v)])
    out = {}
    for level, name in [("us", "us"), ("state", "state"), ("county", "county"), ("town", "cttown")]:
        tabs = {}
        for g in ["B25063", "B19001", "B19013", "B19080", "B25119", "B25118", "B25064"]:
            p = RAW / "acs" / f"{g}_{v}_{name}.json"
            if not p.exists():
                continue
            j = json.loads(p.read_text())
            h = {c: i for i, c in enumerate(j[0])}
            for row in j[1:]:
                code = code_of(level, row, h)
                if code is not None:
                    tabs.setdefault(code, {}).update({c: row[i] for c, i in h.items() if c.startswith(g)})
        rows = {}
        for code, t in tabs.items():
            rent = [t[f"B25063_{i:03d}E"] for i in range(3, 3 + nr)]
            nocash = t[f"B25063_{3 + nr:03d}E"]
            assert int(t["B25063_001E"]) == sum(map(int, rent)) + int(nocash), (v, code)
            q = [num(t.get(f"B19080_{i:03d}E")) for i in range(1, 5)]
            mi = num(t.get("B19013_001E"))
            rows[code] = rec(rent, nocash, [t[f"B19001_{i:03d}E"] for i in range(2, 18)],
                             mi=mi if mi and 2500 < mi < 250000 else None, mr=num(t.get("B25064_001E")),
                             q=q if all(q) else None, ri=(lambda x: x if x and 2500 < x < 250000 else None)(num(t.get("B25119_003E"))),
                             moe=max(0.0, float(t["B25063_001M"])),
                             pm=[num(t.get("B19013_001M")), num(t.get("B25119_003M"))], ti=[t[f"B25118_{i:03d}E"] for i in range(15, 26)])
            assert sum(rows[code]["ti"]) == int(t["B25118_014E"]), (v, code)
        out[level] = rows
    return out


def ct_regions():
    """Town code and town name -> planning region code."""
    by_code, by_name = {}, {}
    lines = (RAW / "cb" / "ct_crosswalk.txt").read_text(encoding="utf-8-sig").splitlines()
    for ln in lines:
        f = ln.split("|")
        if len(f) > 8 and f[0] == "09" and f[5] != "00000":
            by_code[f[5]] = "09" + f[3]
            by_name[norm(f[8])] = "09" + f[3]
    assert len(by_code) == 169 and len(by_name) == 169
    return by_code, by_name


def main():
    cb = gpd.read_file(f"zip://{RAW / 'cb' / 'cb_2024_us_county_500k.zip'}", ignore_geometry=True)
    cb = cb[cb.STATEFP.isin(STATE_INFO)]
    names = {r.GEOID: f"{r.NAMELSAD}, {STATE_INFO[r.STATEFP][0]}" for r in cb.itertuples()}
    units = {}
    for code in sorted(names):
        u = unit_of(code)
        units.setdefault(u, {"name": MERGES[u][0] if u in MERGES else names[u], "st": u[:2], "members": [], "f": {}})["members"].append(code)
    ct_code, ct_name = ct_regions()
    states, us, log = {s: {} for s in STATE_INFO}, {}, []

    for fk in FKEYS:
        src = read_acs(int(fk))
        us[fk] = src["us"]["us"]
        for s in STATE_INFO:
            states[s][fk] = src["state"][s]
        county = dict(src["county"])
        # the county rows of all 50 states and DC add to the national row
        for key in ("r", "i"):
            assert sum(sum(x[key]) for x in county.values()) == sum(us[fk][key]), f"{fk}: counties do not add to the nation ({key})"
        agg, how = {}, {}

        def put(u, x, kind):
            agg[u] = add(agg.get(u), x)
            how[u] = kind if agg[u]["n"] == 1 else "merged" if how.get(u) in (None, "direct", "merged") and kind == "direct" else "rebuilt"

        if fk != "2024":                                   # Connecticut from towns
            ct_sum = None
            for c in [c for c in county if c[:2] == "09"]:
                ct_sum = add(ct_sum, county.pop(c))
            n = 0
            for (st, co, nm, sub), x in src["town"].items():
                if st != "09":
                    continue
                region = ct_code.get(sub)
                if region is None:
                    assert sum(x["r"]) + sum(x["i"]) == 0, f"{fk}: Connecticut town not in the crosswalk: {sub}"
                    continue
                put(region, x, "rebuilt")
                n += 1
            assert n == 169, f"{fk}: {n} Connecticut towns"
            assert sum(sum(agg[u]["r"]) for u in agg) == sum(ct_sum["r"]) and sum(sum(agg[u]["i"]) for u in agg) == sum(ct_sum["i"])
            for u in [u for u in agg]:
                how[u] = "rebuilt"
        for code, x in county.items():
            put(unit_of(code), x, "direct")
        assert sum(sum(x["r"]) for x in agg.values()) == sum(us[fk]["r"]) and sum(sum(x["i"]) for x in agg.values()) == sum(us[fk]["i"]), f"{fk}: units do not add to the nation"
        extra = set(agg) - set(units)
        assert not extra, f"{fk}: source codes with no unit: {sorted(extra)}"
        for u, info in units.items():
            if u not in agg:
                raise AssertionError(f"{fk}: no data for unit {u} {info['name']}")
            else:
                x = agg[u]
                x["how"] = how[u]
                if x["how"] != "direct":
                    x["mi"] = x["mr"] = x["q"] = x["ri"] = x["pm"] = None
                del x["n"]
                info["f"][fk] = x
        kinds = pd.Series([f.get("how", "blank") for f in (i["f"][fk] for i in units.values())]).value_counts().to_dict()
        log.append(f"{fk}: {len(county)} source counties -> {len(units)} units {kinds}; renter units {sum(us[fk]['r']) + us[fk]['nc']:,}; households {sum(us[fk]['i']):,}")
    # college counties: enrolled in college or graduate school as a share of residents age 3 and over, 2020-2024
    j = json.loads((RAW / "acs" / "B14001_2024_county.json").read_text())
    h = {c: i for i, c in enumerate(j[0])}
    enr = {}
    for row in j[1:]:
        if row[h["state"]] in STATE_INFO:
            e = enr.setdefault(unit_of(row[h["state"]] + row[h["county"]]), [0, 0])
            e[0] += int(row[h["B14001_008E"]]) + int(row[h["B14001_009E"]])
            e[1] += int(row[h["B14001_001E"]])
    assert set(enr) == set(units)
    for u, info in units.items():
        info["college"] = round(enr[u][0] / enr[u][1], 4) if enr[u][1] else 0
        info["joined"] = len(MERGES[u][1]) if u in MERGES else 1          # codes ever joined here, even if only one exists today
    log.append(f"college counties (enrollment at or over {COLLEGE_SHARE:.0%} of residents): {sum(i['college'] >= COLLEGE_SHARE for i in units.values())}")
    for s in states.values():
        for x in s.values():
            x.pop("n", None)
    for x in us.values():
        x.pop("n", None)
    PROC.mkdir(parents=True, exist_ok=True)
    (PROC / "harmonized.json").write_text(json.dumps({"units": units, "states": states, "us": us}, separators=(",", ":")))
    print("\n".join(log))
    print(f"{len(units)} units from {len(names)} counties; merged units: {sum(len(i['members']) > 1 for i in units.values())}")


if __name__ == "__main__":
    main()
