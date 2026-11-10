# Line 2 Supermarket

**Magna Hackathon · Zadanie 6 · Inteligentný logistický supermarket**

Dátový model a simulácia po minútach, ktoré z týždenného výrobného plánu montážnej linky 2 vypočítajú:
spotreba materiálu → Min/Max a replenishment trigger → počet štapľov → veľkosť a layout supermarketu pri linke 2 → transportné požiadavky pre AMR → logistický changeover medzi variantmi. Cieľ: žiadne zastavenie linky a žiadne manuálne plánovanie.

## Spustenie

1. **Otvorte `index.html` v prehliadači.** Nič netreba inštalovať. Stránka číta dáta z `data/input.js`.
2. **Keď sa zmenia zdrojové Excely,** dáta znovu vygenerujte:

```bash
pip install openpyxl
```

```bash
python3 model/build_data.py
```

Skript načíta `data/raw/*.xlsx` a zapíše:
- `data/input.js` pre aplikáciu;
- vstupné tabuľky do `data/*.csv`;
- `output/material_calc.csv` s Min / Max / triggerom pre každý materiál na kontrolu v Exceli.

**Živá verzia cez GitHub Pages:** Settings → Pages → vetva `main`, priečinok `/`.

## Ako to funguje

```
data/raw/vyrobny_plan.xlsx ─┐
                            ├─ model/build_data.py ─→ data/input.js ─→ index.html (výpočet + simulácia + dashboard)
data/raw/SM_layout_...xlsx ─┘                      └→ data/*.csv, output/material_calc.csv
```

- **`model/build_data.py`** nájde v pláne blok linky 2 a všetko načíta z Excelov:
  - z plánu: poradie (rímske čísla), množstvá, balenie a zmeny D / N / D+N;
  - zo `SM_layout_existujuci.xlsx`: prevodník (variant → 11 komponentov), kusy na štapeľ, aktívne zásoby a prestavbovú zónu.
- **`index.html`** vypočíta Min/Max a triggre a potom simuluje týždeň po 30 sekundách:
  - spotreba pri 55 JPH, prestávky a changeovery;
  - pozície pri linke;
  - flotila AMR s jazdou, nakládkou a spiatočnými jazdami;
  - príprava materiálu pred každým changeoverom.

## Logika výpočtu (predvolené parametre)

```
spotreba počas výroby      d       = 55 JPH × 1 ks/prevodovku = 0,917 ks/min
jazda AMR                  200 m ÷ 66,7 m/min = 3,0 min
nominálny lead time        LT_nom  = 5 príprava + 0,5 nakládka + 3,0 jazda + 0,5 vykládka = 9,0 min
cyklus AMR                 cyklus  = 4 × 0,5 + 2 × 3,0 = 8,0 min
plánovací lead time        LT_plan = LT_nom + jeden cyklus čakania na voľné AMR = 17,0 min
bezpečnostná zásoba        SS      = z × d × CV × LT_plan = 2,576 × 0,917 × 0,3 × 17 = 12,0 ks
trigger                    ROP     = ⌈d × LT_plan + SS⌉ = 28 ks
štaple                     Min = ⌈ROP ÷ ks na štapeľ⌉, Max = Min + 1
```

- **Trigger.** Požiadavka pre AMR vznikne, keď zásoba pri linke spolu so zásobou na ceste klesne na ROP.
- **Pravidlo dobehu.** Doplnenie sa neobjedná, ak zásoba pri linke už pokryje zvyšok dávky.
- **Changeover.** Nový materiál sa pripraví `LT_plan + ⌈n ÷ (2 × AMR)⌉ × cyklus + rezerva` pred zastavením linky. Štapeľ ide na voľnú rezervnú pozíciu svojho miesta spotreby, ak ju starý variant už nepotrebuje. Inak ide na changeover pozíciu. Staré štaple sa vracajú spiatočnými jazdami.
- **Priorita.** Požiadavky sú zoradené podľa času do stock-outu, pri príprave changeoveru podľa času do jeho začiatku.

| Priorita | Význam |
|---|---|
| P1 | prišla by až po stock-oute |
| P2 | rezerva menej ako jeden LT_plan |
| P3 | bežná |
| P4 | vrátenie |

## Výsledky (predvolené parametre)

**Supermarket pri linke 2:** 22 pozícií na 11 miestach spotreby + 4 changeover + 8 vratných = **34 pozícií pre štaple**. To je 9,2 m² čistej plochy, resp. 37,6 m² aj s uličkou pre AMR (vozík 630 × 430 mm).

| Scenár (zadanie §7) | Zastavenie linky | Dostupnosť |
|---|---|---|
| Štandardný plán, 55 JPH | 0 min | 100 % |
| Zmena mixu (podiel 46 N2 18 % → 46 %) | 0 min | 100 % |
| AMR +10 min na jazdu, nezohľadnené | 82 min | 98,0 % |
| AMR +10 min na jazdu, zadané vopred (trigger 28 → 61 ks) | 0 min | 100 % |
| Pokles pod trigger (3 materiály) | 0 min | 100 % |
| Súbeh kritických materiálov: všetky na 12 ks, 1 AMR | 28,5 min | 99,3 % |
| Výpadok 1 z 2 AMR na 2 h pri najväčšom changeoveri | 0 min | 100 % |
| 1 AMR pri zmenenom mixe | 0 min | 100 % |

## Štruktúra repozitára

```
index.html                           aplikácia: dátový model, simulácia, dashboard (bez buildu)
model/build_data.py                  Excel → data/input.js + CSV + output/material_calc.csv
data/raw/                            zdrojové súbory od organizátorov (+ obrázok košíka)
data/input.js                        vygenerovaný vstup pre aplikáciu
data/*.csv                           vygenerované vstupné tabuľky
output/material_calc.csv             vygenerované Min / Max / trigger pre každý materiál
TODO.md                              otvorené body pred odovzdaním
```

## Tím

Dvojčlenný tím. Spojené riešenie kombinuje:
- **Načítanie dát z Excelu, prevodník, čas prípravy a stresové scenáre** z prvého prototypu (Python model).
- **Simuláciu s obmedzenou kapacitou pri linke, logistiku changeoveru, layout, materiálový tok a dashboard** z druhého prototypu (webová aplikácia).
