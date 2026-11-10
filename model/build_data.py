#!/usr/bin/env python3
"""Line 2 Supermarket - data pipeline.

Reads the source Excel files and writes everything the web app and the jury need:
  data/input.js              window.INPUT for index.html (plan, BOM, pcs per stapel, stock, shifts)
  data/*.csv                 the same inputs as plain tables
  output/material_calc.csv   Min / Max / trigger per material (same formulas as the app)

Usage:  python3 model/build_data.py [data/raw]
Needs:  openpyxl   (pip install openpyxl)
"""
import csv
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "raw"
DATA, OUT = ROOT / "data", ROOT / "output"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}

# Parameters given by the task (Zadanie 6) - the app uses the same defaults
JPH, SPEED_KMH, DIST_M, HANDLING_MIN, PREP_MIN = 55, 4, 200, 0.5, 5
SERVICE_Z, LT_CV = 2.5758, 0.3          # 99.5 % material availability
BASKET = {"l": 0.63, "w": 0.43, "h": 0.135, "kg": 10.3, "name": "Trolley 80 C, TM00171"}  # Baskets dimensions sheet (image)


def norm_variant(s):
    """'56_H2', '56H2', '56 H2' -> '56 H2'; 'Inv. D3.6' -> 'INV D3.6'."""
    s = str(s).strip()
    if s.lower().startswith("inv"):
        return "INV D3.6"
    m = re.match(r"^(\d{2})([A-Z]\d)$", s.replace(" ", "").replace("_", ""))
    return f"{m.group(1)} {m.group(2)}" if m else s


def read_plan(path):
    """Line 2 block of the weekly plan: sequence (roman numeral) and quantity per day."""
    ws = load_workbook(path, data_only=True)["Plan"]
    start = next(r for r in range(1, ws.max_row + 1)
                 if any(str(ws.cell(r, c).value or "").replace(" ", "") == "LINE2" for c in range(1, 12)))
    head = next(r for r in range(start, start + 12) if ws.cell(r, 5).value in ("Type", "Typ"))
    first = head + 2
    end = next(r for r in range(first, ws.max_row + 1) if "New projects" in str(ws.cell(r, 3).value or ""))
    # columns: day d -> sequence in column 8+2d, quantity in column 9+2d (1-based); shift codes sit in the project row
    shifts = [str(ws.cell(first, 8 + 2 * d).value or "").strip() for d in range(7)]
    runs = []
    for r in range(first, end):
        typ = ws.cell(r, 5).value or ws.cell(r, 6).value
        if not typ:
            continue
        variant = norm_variant(typ)
        pack = "Carton" if "Carton" in str(ws.cell(r, 4).value or "") else "Steel rack"
        drive = str(ws.cell(r, 7).value or "").replace(" ", "")
        for d in range(7):
            seq, qty = ws.cell(r, 8 + 2 * d).value, ws.cell(r, 9 + 2 * d).value
            if isinstance(qty, (int, float)) and qty > 0 and str(seq).strip() in ROMAN:
                runs.append(dict(day=d, seq=ROMAN[str(seq).strip()], v=variant, drive=drive, pack=pack, q=int(qty)))
    runs.sort(key=lambda x: (x["day"], x["seq"]))
    cap = [ws.cell(end + 2, 9 + 2 * d).value or 0 for d in range(7)]
    return runs, shifts, cap


def read_layout(path):
    wb = load_workbook(path, data_only=True)
    pcs, stock, special = {}, {}, {}
    for row in wb["Skladované materiály"].iter_rows(min_row=2, values_only=True):
        act, mat, _, per, n = (list(row) + [None] * 5)[:5]
        if not mat:
            continue
        mat = str(mat).strip()
        if per:
            pcs.setdefault(mat.split(" (")[0], int(per))
            if str(act).strip() == "OK":
                stock[mat] = int(n or 0)
        else:
            special[mat] = int(n or 0)
    # Prevodnik: header row holds 'Typ prevodovky' followed by the component columns
    rows = list(wb["Prevodník"].iter_rows(values_only=True))
    hdr = rows[0]
    tcol = next(i for i, v in enumerate(hdr) if v and "Typ" in str(v))
    comps = [("GRev" if str(v).strip().lower() == "grev" else str(v).strip()) for v in hdr[tcol + 1:] if v]
    bom = {}
    for row in rows[1:]:
        if not row[tcol]:
            continue
        mats = [str(m).strip() for m in row[tcol + 1:tcol + 1 + len(comps)] if m]
        bom[norm_variant(row[tcol])] = {m.split(" (")[0]: m for m in mats}
    return pcs, stock, special, comps, bom


def derived():
    rate = JPH / 60
    travel = DIST_M / (SPEED_KMH * 1000 / 60)
    lt_nom = PREP_MIN + HANDLING_MIN + travel + HANDLING_MIN
    cycle = 4 * HANDLING_MIN + 2 * travel
    lt_plan = lt_nom + cycle
    ss = SERVICE_Z * rate * LT_CV * lt_plan
    rop = math.ceil(rate * lt_plan + ss)
    return dict(rate=rate, travel=travel, lt_nom=lt_nom, cycle=cycle, lt_plan=lt_plan, ss=ss, rop=rop)


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    runs, shifts, cap = read_plan(RAW / "vyrobny_plan.xlsx")
    pcs, stock, special, comps, bom = read_layout(RAW / "SM_layout_existujuci.xlsx")
    used = sorted({r["v"] for r in runs})
    missing = [v for v in used if v != "INV D3.6" and v not in bom]
    if missing:
        sys.exit(f"Prevodník has no row for: {missing}")

    plan = [[{k: r[k] for k in ("v", "q", "drive", "pack")} for r in runs if r["day"] == d] for d in range(7)]
    payload = dict(generated=date.today().isoformat(), source=["vyrobny_plan.xlsx", "SM_layout_existujuci.xlsx"],
                   comps=[{"id": c, "pcs": pcs[c]} for c in comps], bom=bom, plan=plan, shifts=shifts, cap=cap,
                   exist=stock, coZone=special.get("PRESTAVBOVA ZONA", 8), emptyPos=special.get("PRAZDNE KOSIKY", 12),
                   basket=BASKET)
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    (DATA / "input.js").write_text("// generated by model/build_data.py - do not edit by hand\nwindow.INPUT = "
                                   + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")

    write_csv(DATA / "production_plan_line2.csv", ["day", "sequence", "variant", "drive", "packaging", "quantity", "shift"],
              [[DAYS[r["day"]], r["seq"], r["v"], r["drive"], r["pack"], r["q"], shifts[r["day"]]] for r in runs])
    write_csv(DATA / "materials.csv", ["component", "pcs_per_stapel"], [[c, pcs[c]] for c in comps])
    write_csv(DATA / "existing_supermarket_stock.csv", ["material", "stapel_count"], sorted(stock.items()))
    write_csv(DATA / "prevodnik.csv", ["variant"] + comps, [[v] + [b.get(c, "") for c in comps] for v, b in bom.items()])

    # Min / Max / trigger per material, same formulas as index.html
    D = derived()
    week = {}
    for r in runs:
        for m in (bom.get(r["v"]) or {}).values():
            week[m] = week.get(m, 0) + r["q"]
    rows = []
    for m, q in sorted(week.items()):
        p = pcs[m.split(" (")[0]]
        mn = max(1, math.ceil(D["rop"] / p))
        ex = stock.get(m, 0)
        rows.append([m, p, q, math.ceil(q / p), round(p / D["rate"]), round(D["rate"] * D["lt_plan"], 1),
                     round(D["ss"], 1), D["rop"], mn, mn + 1, ex, round(ex * p / q, 1)])
    write_csv(OUT / "material_calc.csv",
              ["material", "pcs_per_stapel", "week_demand_pcs", "stapel_per_week", "stapel_lasts_min", "demand_in_LT",
               "safety_stock", "ROP_pcs", "Min_stapel", "Max_stapel", "existing_SM_stapel", "existing_SM_weeks"], rows)

    print(f"plan: {len(runs)} runs, {sum(r['q'] for r in runs)} pcs, shifts {dict(zip(DAYS, shifts))}")
    print(f"BOM: {len(comps)} components {comps}; variants {list(bom)}")
    print(f"LT_plan {D['lt_plan']:.1f} min, SS {D['ss']:.1f} pcs, ROP {D['rop']} pcs; {len(rows)} materials -> output/material_calc.csv")


if __name__ == "__main__":
    main()
