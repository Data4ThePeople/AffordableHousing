"""Total tax on a household's income, by frame, state, household type and income.

Federal and state income tax come from NBER TAXSIM35, run offline. Payroll tax is computed here
from the statutory employee rates and wage bases (Social Security Administration), because
TAXSIM35's payroll output uses a 2023 wage base of $153,600 against the statutory $160,200.
Assumptions: all income is wages of one earner aged 40; the spouse, if any, is 40 with no
earnings; children are 5 and 8; standard deduction; no local income tax.
The 2020-2024 frame is in 2024 dollars and TAXSIM35 stops at tax year 2023, so those incomes are
brought to 2023 dollars with the CPI-U, taxed under 2023 law, and the tax is scaled back up.
Output: data/processed/tax_grid.json"""
import io
import json
import subprocess

import pandas as pd

from common import FRAMES, PROC, RAW, STATE_INFO

EXE = RAW / "taxsim" / "taxsim35-osx.exe"
# household types: (label, mstat, dependents)
TYPES = [("Single, no children", 1, 0), ("Married, no children", 2, 0), ("Married, two children", 2, 2)]
# income grid in dollars: 0 and 160 points from $250 to $2,000,000, evenly spaced in ratio
GRID = [0] + [round(250 * (8000 ** (k / 159))) for k in range(160)]
# employee payroll tax: (Social Security rate, wage base, Medicare rate, Medicare capped at the wage base).
# From 2013 an extra 0.9% applies above $200,000 (single) or $250,000 (joint).
FICA = {2009: (0.062, 106800, 0.0145, False), 2014: (0.062, 117000, 0.0145, False), 2019: (0.062, 132900, 0.0145, False),
        2024: (0.062, 168600, 0.0145, False)}


def payroll(year, wages, mstat):
    ss, base, med, capped = FICA[year]
    t = ss * min(wages, base) + med * (min(wages, base) if capped else wages)
    if year >= 2013:
        t += 0.009 * max(0, wages - (250000 if mstat == 2 else 200000))
    return t


def main():
    cpi = json.loads((PROC / "cpi.json").read_text())
    soi = {f: i + 1 for i, f in enumerate(sorted(STATE_INFO, key=lambda f: STATE_INFO[f][1]))}   # TAXSIM state codes: alphabetical by name
    assert soi["39"] == 36 and soi["56"] == 51 and soi["11"] == 9
    rows, key = [], []
    for fk, _, _, year in FRAMES:
        law = min(year, 2023)
        k = cpi[str(law)] / cpi[str(year)]
        for ti, (_, mstat, dep) in enumerate(TYPES):
            for st in sorted(STATE_INFO):
                for gi, inc in enumerate(GRID):
                    rows.append(f"{len(rows) + 1},{law},{soi[st]},{mstat},40,{40 if mstat == 2 else 0},{dep},{5 if dep else 0},{8 if dep else 0},{inc * k:.2f}")
                    key.append((fk, ti, st, gi, year, mstat, inc, k))
    text = "taxsimid,year,state,mstat,page,sage,depx,age1,age2,pwages\n" + "\n".join(rows) + "\n"
    res = subprocess.run([str(EXE)], input=text, capture_output=True, text=True, timeout=1800)
    out = pd.read_csv(io.StringIO(res.stdout))
    out.columns = [c.strip() for c in out.columns]
    assert len(out) == len(rows), f"TAXSIM returned {len(out)} of {len(rows)} rows: {res.stdout[-400:]}"
    grid = {}
    detail = []
    for (fk, ti, st, gi, year, mstat, inc, k), fed, sta in zip(key, out.fiitax, out.siitax):
        pay = payroll(year, inc, mstat)
        tot = fed / k + sta / k + pay
        grid.setdefault(fk, {}).setdefault(ti, {}).setdefault(st, []).append(round(tot))
        if st == "39" and inc and gi % 20 == 0:
            detail.append((fk, TYPES[ti][0], inc, round(fed / k), round(sta / k), round(pay), round(100 * tot / inc, 1)))
    (PROC / "tax_grid.json").write_text(json.dumps({"inc": GRID, "types": [t[0] for t in TYPES], "tax": grid}, separators=(",", ":")))
    print(pd.DataFrame(detail, columns=["frame", "type", "income", "federal", "state", "payroll", "pct"]).query("type=='Married, two children'").to_string(index=False))
    print(f"rows {len(rows):,}; negative total tax in {sum(v < 0 for f in grid.values() for t in f.values() for s in t.values() for v in s):,} cells")


if __name__ == "__main__":
    main()
