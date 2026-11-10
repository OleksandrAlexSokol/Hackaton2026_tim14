# TODO pred odovzdaním

## 1. Overiť s organizátormi (blokujúce: hodnotí sa správnosť výpočtov)
- [ ] **Prevodník.** Doplnil ho náš tím, v pôvodnom súbore je prázdny. Overiť:
  - [ ] či G1 a G2/Rev naozaj nejdú na linku 2 (majú zásobu v existujúcom SM, ale v prevodníku nemajú stĺpec);
  - [ ] či každá prevodovka potrebuje 1 ks z každého komponentu.
- [ ] **AMR.** Platí 30 s nakládka/vykládka na jeden štapeľ, alebo na celú zastávku?
- [ ] **Zmeny.** Je vo štvrtok na linke 2 naozaj len nočná zmena (N)?
- [ ] **Existujúci supermarket.** Zásobuje aj linku 1? Pre väčšinu materiálov 56 kryje jeho zásoba len asi 1 týždeň potreby linky 2.
- [ ] **Verejný repozitár.** Opýtať sa, či je povolený. Na slajdoch je uvedené „Disclosure or duplication without consent is prohibited“. Ak nie, nechať repozitár súkromný a pridať porotu ako collaborators.

## 2. Ručne skontrolovať čísla
- [ ] Prepočítať jeden materiál (napr. IS2 (2_56), 64 ks/štapeľ) v Exceli podľa `output/material_calc.csv`:
  - [ ] d × LT_plan;
  - [ ] SS;
  - [ ] ROP = 28;
  - [ ] Min 1, Max 2.
- [ ] Skontrolovať, že týždenný plán v aplikácii sedí s `vyrobny_plan.xlsx` (3 610 ks, 19 dávok).

## 3. Prezentácia (3 min podľa štruktúry organizátorov)
- [ ] Slajdy podľa blokov:
  - [ ] krátky úvod;
  - [ ] architektúra v skratke (60 s);
  - [ ] ukážka kódu a živé demo (60 s);
  - [ ] prínos riešenia (30 s);
  - [ ] krátke zhrnutie.
- [ ] Scenár živého dema:
  - [ ] streda 22:40 na časovom posuvníku: príprava changeoveru 56 N2 → 46 N2;
  - [ ] scenáre „AMR delay unplanned vs known“: 82 min zastavenia vs 0.
- [ ] Rozdeliť, kto prezentuje ktorú časť. Raz to nacvičiť so stopkami.

## 4. Repozitár / odovzdanie
- [ ] Vytvoriť GitHub repozitár a nahrať kód.
- [ ] Voliteľne: zapnúť GitHub Pages, aby porota mala jeden odkaz.
- [ ] Pripraviť záložnú verziu offline: PDF prezentácie a `index.html` s priečinkom `data/`.

## 5. Ak zostane čas
- [ ] Nechávať čiastočné štaple pri linke, keď sa ten istý materiál vráti v tej istej zmene (sobota H2 → M2 → H2).
- [ ] Export simulovaných AMR požiadaviek do Excelu.
- [ ] Editovateľný prevodník priamo v aplikácii.
