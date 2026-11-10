# TODO before submission

## 1. Confirm with the organisers (blocking: correctness is graded)
- [ ] **Prevodník.** Our team filled it in; in the original file it is empty. Confirm:
  - [ ] that G1 and G2/Rev are really not supplied to Line 2 (they have stock in the existing SM but no column in Prevodník);
  - [ ] that each transmission uses 1 piece of each component.
- [ ] **AMR.** Do the 30 s load/unload apply per štapel or per stop?
- [ ] **Shifts.** Is Thursday on Line 2 really night shift only (N)?
- [ ] **Existing supermarket.** Does it also feed Line 1? For most 56 materials its stock covers only about 1 week of Line 2 demand.
- [ ] **Public repository.** Ask whether one is allowed. The slides say "Disclosure or duplication without consent is prohibited". If not, keep the repo private and add the jury as collaborators.

## 2. Check the numbers by hand
- [ ] Recalculate one material (e.g. IS2 (2_56), 64 pcs/štapel) in Excel from `output/material_calc.csv`:
  - [ ] d × LT_plan;
  - [ ] SS;
  - [ ] ROP = 28;
  - [ ] Min 1, Max 2.
- [ ] Check that the week plan in the app matches `vyrobny_plan.xlsx` (3610 pcs, 19 runs).

## 3. Presentation (≈ 5 min)
- [ ] Slides:
  - [ ] the problem;
  - [ ] the chain plan → trigger → AMR request;
  - [ ] the formulas;
  - [ ] the layout (34 positions, 37.6 m²);
  - [ ] the scenario table;
  - [ ] assumptions and risks.
- [ ] Live demo script:
  - [ ] Wednesday 22:40 on the time slider: 56 N2 → 46 N2 pre-stage (Changeover detail section);
  - [ ] the "AMR delay unplanned vs known" scenarios: 82 min line stop vs 0;
  - [ ] the "Line 2 supermarket by shift" table: shared slots vs a fixed slot per material.
- [ ] Decide who presents which part. Rehearse once with a timer.

## 4. Repository / delivery
- [ ] Create the GitHub repo and push.
- [ ] Optional: enable GitHub Pages so the jury gets one link.
- [ ] Optional: translate the UI and README to Slovak for the jury.

## 5. Nice to have (only if time is left)
- [ ] Keep partial štaple at Line 2 when the same material returns in the same shift (Saturday H2 → M2 → H2).
- [ ] Excel export of the simulated AMR requests.
- [ ] Editable Prevodník in the UI.
