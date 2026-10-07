"""Tie-out: recompute the page's numbers from the harmonized source counts with separate code, and
compare with what the built page shows in headless Chrome.

1. Every bucket count inlined in the page equals the harmonized count.
2. For each period and several settings: the national share within reach, the number of counties
   with a figure and the number under half, recomputed here, against the page's headline.
3. Dayton metro (Greene, Miami, Montgomery): cash-rent units and the share in buckets fully under
   $800 (2015-2019) and $1,100 (2020-2024), against the published Dayton post (116,730 and 49%;
   115,961 and 46%).
4. Two federal income tax figures worked by hand from the 2019 brackets.
Output: data/processed/tieout.csv; exits with an error on any difference."""
import base64
import bisect
import gzip
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

from common import COLLEGE_SHARE, FRAMES, INC_EDGES, PROC, RENTER_EDGES, RENT_EDGES, ROOT, STATE_INFO

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PCTS = [0.2, 0.4, 0.5, 0.6, 0.8]
STS = sorted(STATE_INFO)


def percentile(counts, edges, p):
    need, run = p * sum(counts), 0.0
    for k, n in enumerate(counts):
        if n > 0 and run + n >= need:
            return None if k == len(counts) - 1 else round(edges[k] + (edges[k + 1] - edges[k]) * (need - run) / n)
        run += n
    return None


def income(x, fk, prof):
    if prof == 5:
        return round(x["ri"]) if x["ri"] else percentile(x["ti"], RENTER_EDGES, 0.5)
    pub = x["mi"] if prof == 2 else (x["q"][{0: 0, 1: 1, 3: 2, 4: 3}[prof]] if x["q"] else None)
    return round(pub) if pub else percentile(x["i"], INC_EDGES[fk], PCTS[prof])


def tax(T, fk, ht, st, inc):
    g, t = T["inc"], T["tax"][fk][str(ht)][st]
    if inc <= 0:
        return 0.0
    if inc >= g[-1]:
        return t[-1] / g[-1] * inc
    j = bisect.bisect_right(g, inc) - 1
    return t[j] + (t[j + 1] - t[j]) * (inc - g[j]) / (g[j + 1] - g[j])


def share(r, edges, c):
    tot, below = sum(r), 0.0
    for k, n in enumerate(r):
        lo = edges[k]
        hi = edges[k + 1] if k + 1 < len(edges) else None
        if hi is None:
            break
        if c >= hi:
            below += n
        elif c > lo:
            below += n * (c - lo) / (hi - lo)
            break
        else:
            break
    return below / tot


def nation(H, T, cpi, fk, year, prof=5, pct=30, after=True, ht=1, typed=None, st=None, nocollege=False):
    a = t = n = under = 0
    for u, info in H["units"].items():
        x = info["f"][fk]
        if "na" in x or (st and info["st"] != st) or (nocollege and info["college"] >= COLLEGE_SHARE):
            continue
        inc = typed * cpi[str(year)] / cpi["2024"] if typed else income(x, fk, prof)
        if inc is None or sum(x["r"]) == 0:
            continue
        net = inc - (tax(T, fk, ht, info["st"], inc) if after else 0)
        v = share(x["r"], RENT_EDGES[fk], pct / 100 * net / 12)
        a += v * sum(x["r"]); t += sum(x["r"]); n += 1; under += v < 0.5
    return 100 * a / t, n, under


def fmt(v):
    return (f"{v:.1f}" if 0 < v < 1 or 99 < v < 100 else f"{v + 1e-9:.0f}") + "%"


def main():
    H = json.loads((PROC / "harmonized.json").read_text())
    T = json.loads((PROC / "tax_grid.json").read_text())
    cpi = json.loads((PROC / "cpi.json").read_text())
    html = (ROOT / "dist" / "index.html").read_text()
    bad = 0

    # 1. inlined counts
    b64 = re.search(r'const DATA_B64 = "([^"]+)"', html).group(1)
    D = json.loads(gzip.decompress(base64.b64decode(b64)))
    cells = 0
    for u in D["units"]:
        for fi, (fk, *_) in enumerate(FRAMES):
            x, y = H["units"][u["id"]]["f"][fk], u["f"][fi]
            if "na" in x:
                bad += "x" not in y
                continue
            bad += y["r"] != x["r"] or y["nc"] != x["nc"]
            cells += len(x["r"]) + 1
    print(f"1. inlined bucket counts checked: {cells:,} cells, differences: {bad}")

    # 2. headline numbers
    cases = [dict(), dict(prof=2), dict(prof=0), dict(after=False), dict(typed=60000), dict(ht=2, prof=1), dict(st="39"), dict(st="09"), dict(pct=40, after=False), dict(nocollege=True)]
    rows = []
    with tempfile.TemporaryDirectory() as d:
        Path(d, "p.html").write_text(html)
        for case in cases:
            for fk, label, _, year in FRAMES:
                v, n, under = nation(H, T, cpi, fk, year, **case)
                h = f"#f={fk}&p={6 if case.get('typed') else case.get('prof', 5)}&pct={case.get('pct', 30)}&tax={int(case.get('after', True))}&ht={case.get('ht', 1)}"
                h += f"&inc={case['typed']}" if case.get("typed") else ""
                h += f"&st={case['st']}" if case.get("st") else ""
                h += "&col=0" if case.get("nocollege") else ""
                dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000", "--window-size=1200,900", "--dump-dom",
                                      f"file://{d}/p.html{h}"], capture_output=True, text=True, timeout=300).stdout
                sub = re.search(r'id="sub"[^>]*>([^<]*)<', dom).group(1)
                m = re.search(r"could afford (?:at least )?([\d.]+%) of the rentals.*?In ([\d,]+) of ([\d,]+) counties", sub)
                page = (m.group(1), int(m.group(2).replace(",", "")), int(m.group(3).replace(",", ""))) if m else None
                ok = page == (fmt(v), under, n)
                bad += not ok
                rows.append({"setting": json.dumps(case) if case else "default", "period": label, "share_recomputed": round(v, 2), "counties": n, "under_half": under,
                             "page_share": page[0] if page else "", "page_under": page[1] if page else "", "page_counties": page[2] if page else "", "match": ok})
    t = pd.DataFrame(rows)
    t.to_csv(PROC / "tieout.csv", index=False)
    pd.set_option("display.width", 250)
    print("2. headline numbers, recomputed against the page")
    print(t.to_string(index=False))

    # 3. Dayton
    for fk, thr, want_units, want_pct in [("2019", 800, 116730, 49), ("2024", 1100, 115961, 46)]:
        e = RENT_EDGES[fk]
        r = [sum(v) for v in zip(*(H["units"][u]["f"][fk]["r"] for u in ("39057", "39109", "39113")))]
        below = sum(n for k, n in enumerate(r) if k + 1 < len(e) and e[k + 1] <= thr)
        ok = sum(r) == want_units and round(100 * below / sum(r)) == want_pct
        bad += not ok
        print(f"3. Dayton {fk}: {sum(r):,} cash-rent units (post: {want_units:,}); {100 * below / sum(r):.1f}% in buckets fully under ${thr:,} (post: {want_pct}%) {'ok' if ok else 'MISMATCH'}")

    # 4. federal income tax by hand, 2019 law: standard deduction $12,200 single and $24,400 joint; 10% then 12% brackets
    out = subprocess.run([str(ROOT / "data" / "raw" / "taxsim" / "taxsim35-osx.exe")], capture_output=True, text=True,
                         input="taxsimid,year,state,mstat,page,sage,depx,age1,age2,pwages\n1,2019,36,1,40,0,0,0,0,40000\n2,2019,36,2,40,40,0,0,0,80000\n").stdout
    got = [float(ln.split(",")[3]) for ln in out.strip().splitlines()[1:]]
    hand = [0.10 * 9700 + 0.12 * (40000 - 12200 - 9700), 0.10 * 19400 + 0.12 * (80000 - 24400 - 19400)]
    for g, h in zip(got, hand):
        ok = abs(g - h) < 1
        bad += not ok
        print(f"4. 2019 federal income tax: TAXSIM {g:,.0f}, by hand {h:,.0f} {'ok' if ok else 'MISMATCH'}")
    print("TIE-OUT", "CLEAN" if not bad else f"FAILED: {bad} differences")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
