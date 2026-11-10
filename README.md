# Line 2 Supermarket

**Magna Hackathon · Zadanie 6 · Inteligentný logistický supermarket**

A data model and minute-by-minute simulation that turns the weekly production plan of assembly line 2 into:
material demand → Min/Max and replenishment trigger → number of štaple → size and layout of the Line 2 supermarket → AMR transport requests → logistic changeover between variants. The goal is no line stop and no manual planning.

## Run it

1. **Open `index.html` in a browser.** There is nothing to install. The page reads its data from `data/input.js`.
2. **After the source Excel files change,** rebuild the data:

```bash
pip install openpyxl
```

```bash
python3 model/build_data.py
```

The script reads `data/raw/*.xlsx` and writes:
- `data/input.js` for the app;
- the input tables in `data/*.csv`;
- `output/material_calc.csv`, with Min / Max / trigger per material for checking in Excel.

**Live version via GitHub Pages:** Settings → Pages → branch `main`, folder `/`.

## How it works

```
data/raw/vyrobny_plan.xlsx ─┐
                            ├─ model/build_data.py ─→ data/input.js ─→ index.html (calculation + simulation + dashboard)
data/raw/SM_layout_...xlsx ─┘                      └→ data/*.csv, output/material_calc.csv
```

- **`model/build_data.py`** finds the Line 2 block in the plan and reads everything from the Excel files:
  - from the plan: the sequence (roman numerals), quantities, packaging and the shift codes D / N / D+N;
  - from `SM_layout_existujuci.xlsx`: the Prevodník (variant → 11 components), pcs per štapel, the active stock and the changeover zone.
- **`index.html`** computes Min/Max and triggers, then simulates the week in 30-second steps:
  - consumption at 55 JPH, breaks and changeovers;
  - line-side positions;
  - an AMR fleet with travel, loading and returns;
  - pre-staging before each changeover.

## Calculation logic (default parameters)

```
consumption while running   d       = 55 JPH × 1 pc/unit = 0.917 pcs/min
AMR travel                  200 m ÷ 66.7 m/min = 3.0 min
nominal lead time           LT_nom  = 5 prep + 0.5 load + 3.0 travel + 0.5 unload = 9.0 min
AMR cycle                   cycle   = 4 × 0.5 + 2 × 3.0 = 8.0 min
planning lead time          LT_plan = LT_nom + one cycle waiting for a free AMR = 17.0 min
safety stock (99.5 %)       SS      = z × d × CV × LT_plan = 2.576 × 0.917 × 0.3 × 17 = 12.0 pcs
trigger                     ROP     = ⌈d × LT_plan + SS⌉ = 28 pcs
štaple                      Min = ⌈ROP ÷ pcs per štapel⌉, Max = Min + 1
```

- **Trigger.** An AMR request is created when line-side stock plus stock on the way falls to ROP.
- **Run-out rule.** No replenishment is ordered if line-side stock already covers the rest of the run.
- **Changeover.** New material is pre-staged `LT_plan + ⌈n ÷ (2 × AMRs)⌉ × cycle + reserve` before the stop. A štapel goes into the free reserve slot of its consumption point if the old variant no longer needs that slot; otherwise it goes to a changeover position. Old štaple ride back on the return legs.
- **Priority.** Requests are ranked by time to stock-out, or for pre-staging by time to changeover start.

| Priority | Meaning |
|---|---|
| P1 | would arrive after stock-out |
| P2 | less than one LT_plan of slack |
| P3 | normal |
| P4 | return |

## Results (default parameters)

**Line 2 supermarket:** 22 positions at 11 consumption points + 4 changeover + 8 returns = **34 štapel positions**. That is 9.2 m² net, or 37.6 m² including the AMR aisle (trolley 630 × 430 mm).

| Scenario (task §7) | Line stop | Availability |
|---|---|---|
| Standard plan, 55 JPH | 0 min | 100 % |
| Mix change (46 N2 share 18 % → 46 %) | 0 min | 100 % |
| AMR +10 min per trip, unplanned | 82 min | 98.0 % |
| AMR +10 min per trip, known in advance (trigger 28 → 61 pcs) | 0 min | 100 % |
| Drop below trigger (3 materials) | 0 min | 100 % |
| Critical overlap: all materials at 12 pcs, 1 AMR | 28.5 min | 99.3 % |
| One of two AMRs down 2 h at the largest changeover | 0 min | 100 % |
| 1 AMR on the mix-change plan | 0 min | 100 % |

## Repository layout

```
index.html                       app: data model, simulation, dashboard (no build step)
model/build_data.py              Excel → data/input.js + CSV + output/material_calc.csv
data/raw/                        source files from the organisers (+ basket image)
data/input.js                    generated input for the app
data/*.csv                       generated input tables
output/material_calc.csv         generated Min / Max / trigger per material
TODO.md                          open points before submission
```

## Team

Two-person team. The merged solution combines:
- **The Excel data pipeline, Prevodník, preparation time and stress scenarios** from the first prototype (Python model).
- **The simulation with limited line-side capacity, changeover logistics, layout, plant flow and dashboard** from the second prototype (web app).
