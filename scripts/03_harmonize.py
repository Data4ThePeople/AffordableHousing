"""Put every frame on one set of stable county units drawn on 2024 boundaries.

Bucket counts are only ever added or subtracted, never split by area, so every unit is exact.
  renames            old code -> new code
  merges             Virginia cities that merged with or annexed from a county, and Alaska areas whose
                     splits nest, are joined into one unit for every frame
  Connecticut        the nine planning regions are rebuilt from the 169 towns in the six frames
                     before 2020-2024 (towns nest exactly in the regions)
  Yuma / La Paz AZ, Valencia / Cibola NM
                     1980 is rebuilt from that census's county divisions
  Broomfield CO      2000: Broomfield is the city as it stood in 2000, and its four parent counties
                     have their part of the city taken out. 1980 and 1990: Broomfield, Boulder and
                     Adams are left blank (4% to 7% of the parents moved); Jefferson and Weld are kept
                     (under 1% moved)
Output: data/processed/harmonized.json"""
import json
import math

import geopandas as gpd
import pandas as pd

from common import ACS_VINTAGES, FKEYS, INC_EDGES, PROC, RAW, RENT_EDGES, STATE_INFO

NH = RAW / "nhgis" / "nhgis0009_csv"

RENAME = {"12025": "12086", "46113": "46102", "02270": "02158"}
# unit id -> (label, member codes in any frame)
MERGES = {
    "02016": ("Aleutians East Borough + Aleutians West Census Area, AK", ["02010", "02013", "02016"]),
    "02070": ("Dillingham Census Area + Lake and Peninsula Borough, AK", ["02070", "02164"]),
    "02185": ("North Slope Borough + Northwest Arctic Borough, AK", ["02140", "02185", "02188"]),
    "02290": ("Yukon-Koyukuk + Southeast Fairbanks + Denali, AK", ["02290", "02240", "02068"]),
    "02063": ("Chugach + Copper River Census Areas, AK", ["02261", "02063", "02066"]),
    "02130": ("Southeast Alaska outside Juneau, Sitka and Haines", ["02130", "02201", "02198", "02280", "02275", "02195",
                                                                 "02231", "02232", "02230", "02105", "02282"]),
    "30067": ("Park County + Yellowstone National Park, MT", ["30067", "30113"]),
    "51003": ("Albemarle County + Charlottesville, VA", ["51003", "51540"]),
    "51005": ("Alleghany County + Clifton Forge, VA", ["51005", "51560"]),
    "51015": ("Augusta County + Staunton + Waynesboro, VA", ["51015", "51790", "51820"]),
    "51019": ("Bedford County + Bedford city, VA", ["51019", "51515"]),
    "51059": ("Fairfax County + Fairfax city, VA", ["51059", "51600"]),
    "51081": ("Greensville County + Emporia, VA", ["51081", "51595"]),
    "51083": ("Halifax County + South Boston, VA", ["51083", "51780"]),
    "51095": ("James City County + Williamsburg, VA", ["51095", "51830"]),
    "51143": ("Pittsylvania County + Danville, VA", ["51143", "51590"]),
    "51153": ("Prince William County + Manassas, VA", ["51153", "51683"]),
    "51163": ("Rockbridge County + Buena Vista, VA", ["51163", "51530"]),
    "51165": ("Rockingham County + Harrisonburg, VA", ["51165", "51660"]),
    "51175": ("Southampton County + Franklin, VA", ["51175", "51620"]),
    "51177": ("Spotsylvania County + Fredericksburg, VA", ["51177", "51630"]),
}
MEMBER = {m: u for u, (_, ms) in MERGES.items() for m in ms}
# 1980 county divisions that became La Paz and Cibola
CCD_1980 = {("04", "027"): {"Parker division": "04012", "Somerton division": "04027", "Wellton division": "04027", "Yuma division": "04027"},
            ("35", "061"): {"Fence Lake division": "35006", "Grants division": "35006", "Laguna division": "35006",
                            "Zuni-Ramah Navajo division": "35006", "Belen division": "35061", "Los Lunas division": "35061"}}
BLANK = {("1980", "08013"): "Boulder County lost land to Broomfield County in 2001", ("1990", "08013"): "Boulder County lost land to Broomfield County in 2001",
         ("1980", "08001"): "Adams County lost land to Broomfield County in 2001", ("1990", "08001"): "Adams County lost land to Broomfield County in 2001",
         ("1980", "08014"): "Broomfield County was created in 2001", ("1990", "08014"): "Broomfield County was created in 2001"}


def unit_of(code):
    code = RENAME.get(code, code)
    return MEMBER.get(code, code)


def num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def rec(rent, nocash, inc, mi=None, mr=None, q=None, ri=None, moe=None, alloc=None):
    return {"r": [int(x) for x in rent], "nc": int(nocash), "i": [int(x) for x in inc], "mi": mi, "mr": mr, "q": q, "ri": ri,
            "moe": moe, "al": alloc, "n": 1}


def add(a, b, sign=1):
    """Sum (or subtract) two records. Published medians do not survive."""
    if a is None:
        assert sign == 1
        return dict(b, n=1)
    moe = None if a["moe"] is None or b["moe"] is None else math.hypot(a["moe"], b["moe"])
    al = None if a["al"] is None or b["al"] is None else [x + sign * y for x, y in zip(a["al"], b["al"])]
    out = {"r": [x + sign * y for x, y in zip(a["r"], b["r"])], "nc": a["nc"] + sign * b["nc"], "i": [x + sign * y for x, y in zip(a["i"], b["i"])],
           "mi": None, "mr": None, "q": None, "ri": None, "moe": moe, "al": al, "n": a["n"] + 1}
    assert min(out["r"]) >= 0 and min(out["i"]) >= 0 and out["nc"] >= 0
    return out


# ---------- readers: each returns {level: {code: record}} with level in us, state, county, town ----------
def read_nhgis(fk):
    ds, rent, inc, mi, mr = (("ds107_1980", "DFH", "DID", "DIE001", "DFK001") if fk == "1980" else ("ds123_1990", "EYT", "E4T", "E4U001", "EYU001"))
    nr, ni = len(RENT_EDGES[fk]), len(INC_EDGES[fk])
    out = {}
    for level, name in [("us", "nation"), ("state", "state"), ("county", "county"), ("town", "cty_sub")]:
        d = pd.read_csv(NH / f"nhgis0009_{ds}_{name}.csv", skiprows=[1], dtype=str, encoding="latin-1")
        if fk == "1980" and level != "us":
            for flag in ("SUPFLG01", "SUPFLG07", "SUPFLG08", "SUPFLG21"):
                keep = d.STATEA.str.zfill(2).isin(STATE_INFO)
                if level == "town":
                    sc = d.STATEA.str.zfill(2) + d.COUNTYA.str.zfill(3)
                    keep &= (d.STATEA.str.zfill(2) == "09") | sc.isin(["04027", "35061"])
                assert d[keep][flag].isna().all(), f"1980 {level}: suppressed table ({flag})"
        rows = {}
        for r in d.itertuples(index=False):
            r = r._asdict()
            st = "" if level == "us" else str(r["STATEA"]).zfill(2)
            if level != "us" and st not in STATE_INFO:
                continue
            al = [int(r["E0F001"]), int(r["E0F001"]) + int(r["E0F002"]), int(r["E2Q001"]), int(r["E2Q001"]) + int(r["E2Q002"])] if fk == "1990" else None
            x = rec([r[f"{rent}{i:03d}"] for i in range(1, nr + 1)], r[f"{rent}{nr + 1:03d}"], [r[f"{inc}{i:03d}"] for i in range(1, ni + 1)],
                    mi=num(r[mi]), mr=num(r[mr]), alloc=al)
            if level == "us":
                rows["us"] = x
            elif level == "state":
                rows[st] = x
            elif level == "county":
                rows[st + str(r["COUNTYA"]).zfill(3)] = x
            else:
                rows[(st, str(r["COUNTYA"]).zfill(3), r["CTY_SUB"], str(r["CTY_SUBA"]))] = x
        out[level] = rows
    return out


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


def read_sf3():
    out = {}
    for level, name in [("us", "us"), ("state", "state"), ("county", "county"), ("town", "cttown"), ("broomfield", "broomfield")]:
        j = json.loads((RAW / "sf3" / f"sf3_{name}.json").read_text())
        h = {c: i for i, c in enumerate(j[0])}
        rows = {}
        for row in j[1:]:
            code = row[h["county (or part)"]] if level == "broomfield" else code_of(level, row, h)
            if code is None:
                continue
            g = lambda v: row[h[v]]
            assert int(g("H062001")) == int(g("H062002")) + int(g("H062024"))
            rows[code] = rec([g(f"H062{i:03d}") for i in range(3, 24)], g("H062024"), [g(f"P052{i:03d}") for i in range(2, 18)],
                             mi=num(g("P053001")), mr=num(g("H063001")))
        out[level] = rows
    return out


def read_acs(v):
    nr = len(RENT_EDGES[str(v)])
    out = {}
    for level, name in [("us", "us"), ("state", "state"), ("county", "county"), ("town", "cttown")]:
        tabs = {}
        for g in ["B25063", "B19001", "B19013", "B19080", "B25119", "B25064"]:
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
                             moe=max(0.0, float(t["B25063_001M"])))
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
            by_name[f[8].lower()] = "09" + f[3]
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
        src = read_nhgis(fk) if fk in ("1980", "1990") else read_sf3() if fk == "2000" else read_acs(int(fk))
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
                region = ct_name.get((nm or "").lower()) if fk == "1980" else ct_code.get(sub)
                if region is None:
                    assert sum(x["r"]) + sum(x["i"]) == 0, f"{fk}: Connecticut town not in the crosswalk: {nm or sub}"
                    continue
                put(region, x, "rebuilt")
                n += 1
            assert n == 169, f"{fk}: {n} Connecticut towns"
            assert sum(sum(agg[u]["r"]) for u in agg) == sum(ct_sum["r"]) and sum(sum(agg[u]["i"]) for u in agg) == sum(ct_sum["i"])
            for u in [u for u in agg]:
                how[u] = "rebuilt"
        if fk == "1980":                                   # La Paz and Cibola from 1980 county divisions
            for (st, co), parts in CCD_1980.items():
                whole, got = county.pop(st + co), None
                for (s2, c2, nm, sub), x in src["town"].items():
                    if (s2, c2) == (st, co):
                        put(parts[nm], x, "rebuilt")
                        got = add(got, x)
                assert got["r"] == whole["r"] and got["i"] == whole["i"] and got["nc"] == whole["nc"], f"1980 divisions of {st}{co} do not add to the county"
                for u in set(parts.values()):
                    how[u] = "rebuilt"
        if fk == "2000":                                   # Broomfield from its city parts
            for co, part in src["broomfield"].items():
                put("08014", part, "rebuilt")
                county["08" + co] = dict(add(county["08" + co], part, -1), n=1)
            how["08014"] = "rebuilt"
        for code, x in county.items():
            put(unit_of(code), x, "direct")
        for co in ("001", "013", "059", "123"):
            if fk == "2000":
                how["08" + co] = "rebuilt"
        assert sum(sum(x["r"]) for x in agg.values()) == sum(us[fk]["r"]) and sum(sum(x["i"]) for x in agg.values()) == sum(us[fk]["i"]), f"{fk}: units do not add to the nation"
        extra = set(agg) - set(units)
        assert not extra, f"{fk}: source codes with no unit: {sorted(extra)}"
        for u, info in units.items():
            if (fk, u) in BLANK:
                info["f"][fk] = {"na": BLANK[(fk, u)]}
            elif u not in agg:
                raise AssertionError(f"{fk}: no data for unit {u} {info['name']}")
            else:
                x = agg[u]
                x["how"] = how[u]
                if x["how"] != "direct":
                    x["mi"] = x["mr"] = x["q"] = x["ri"] = None
                del x["n"]
                info["f"][fk] = x
        kinds = pd.Series([f.get("how", "blank") for f in (i["f"][fk] for i in units.values())]).value_counts().to_dict()
        log.append(f"{fk}: {len(county)} source counties -> {len(units)} units {kinds}; renter units {sum(us[fk]['r']) + us[fk]['nc']:,}; households {sum(us[fk]['i']):,}")
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
