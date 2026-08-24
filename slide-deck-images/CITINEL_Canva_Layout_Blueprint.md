# CITINEL — CANVA LAYOUT BLUEPRINT · 15 SLIDES
Canvas 1920×1080 · origin top-left · 12-col grid (col width 130, gutter 24, margins 48; col k starts at x = 48+(k−1)·154) · usable zone y 140–1045 · **header band y 0–140 and bottom bars y 1045–1080 untouched on every slide** · % = px/1920 (x,w) and px/1080 (y,h).

## ASSET REGISTER (reconciled)
78 deck images (1.1–15.5) + 6 specials (SP1–SP6) = **84**. Six partner-logo PNGs are source material inside SP1/SP3, not placeable assets.
**Placed: 54 · Dropped: 30, all superseded by the special heroes you commissioned as replacements:** 6.1–6.6 (→SP4) · 7.1–7.5 (→SP5) · 9.1–9.6 (→SP1) · 13.1–13.6 (→SP2) · 15.1–15.5 (→SP6) · 8.5, 8.6 (→SP3 + slide-9 quarantine makes them redundant).
Text blocks from CITINEL_Slide_Text_Final.md: T1.1 T1.2 · T2.1 · T3.1–3 · T4.1–4 · T5.1 · T6.1–3 · T7.1 · T8.1–4 · T9.1 · T10.1 · T11.1 · T12.1 · T13.1 · T14.1–2 · T15.1 — **all placed once, verbatim**.
2:1 rail images ship with big white margins by design: **crop top/bottom to the content band** (noted per row); never stretch.

---

## Slide 1: Cover
```
[header band — untouched]
        (printed PROJECT NAME centre)
            T1.1  (PS line)
 [1.2]      [1.3 clock strip]      [1.4]
 (printed PRESENTED BY) T1.2
[bottom bars — untouched]
```
| ID | type | x px/% | y px/% | w px/% | h px/% | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 1.1 | image | 0 / 0 | 0 / 0 | 1920 / 100 | 1080 / 100 | 0 | — | full-bleed background; you set opacity; sits under printed header/footer |
| T1.1 | text | 360 / 18.8 | 610 / 56.5 | 1200 / 62.5 | 70 / 6.5 | 10 | centre | two lines, PS title verbatim |
| 1.2 | image | 140 / 7.3 | 640 / 59.3 | 246 / 12.8 | 246 / 22.8 | 2 | left | 1:1 |
| 1.3 | image | 664 / 34.6 | 700 / 64.8 | 592 / 30.8 | 296 / 27.4 | 3 | centre | 2:1; visible band sits mid-frame |
| 1.4 | image | 1500 / 78.1 | 640 / 59.3 | 246 / 12.8 | 246 / 22.8 | 4 | right | 1:1 |
| T1.2 | text | 80 / 4.2 | 955 / 88.4 | 500 / 26.0 | 60 / 5.6 | 10 | left | types into template's PRESENTED BY slot |
Assembly: 1.1 → 1.2 → 1.3 → 1.4 → T1.1 → T1.2. Area: full-bleed + 3 supports ≈ 80/20 ✓ (title band left clear by 1.1's own composition).

## Slide 2: Team Members
```
T2.1 (six member lines, full width)
[——————— 2.1 hex rail ———————]
[2.2 slabs]   [2.3 badge]   [2.4 column]
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| T2.1 | text | 48 / 2.5 | 150 / 13.9 | 1208 / 62.9 | 120 / 11.1 | 10 | left | 6 lines |
| 2.1 | image | 202 / 10.5 | 200 / 18.5 | 1516 / 79.0 | 758 / 70.2 | 1 | centre | 2:1; frame air overlaps neighbours — transparent, content band ~y 470–700 |
| 2.2 | image | 48 / 2.5 | 600 / 55.6 | 560 / 29.2 | 420 / 38.9 | 2 | left | 4:3 |
| 2.3 | image | 900 / 46.9 | 640 / 59.3 | 340 / 17.7 | 340 / 31.5 | 3 | centre | 1:1 |
| 2.4 | image | 1500 / 78.1 | 580 / 53.7 | 330 / 17.2 | 440 / 40.7 | 4 | right | 3:4 |
Assembly: 2.1 → 2.2 → 2.3 → 2.4 → T2.1. Area ≈ 78/22 ✓.

## Slide 3: Problem Statement
```
[3.6]  (printed Q1) T3.1        [——— 3.1 hero ———]
       (printed Q2) T3.2   [3.5][3.3]  [3.4]
       (printed Q3) T3.3
[—————— 3.2 clause rail (cropped band) ——————]
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 3.1 | image | 1050 / 54.7 | 205 / 19.0 | 800 / 41.7 | 450 / 41.7 | 1 | right | 16:9 |
| 3.6 | image | 115 / 6.0 | 216 / 20.0 | 260 / 13.5 | 260 / 24.1 | 2 | left | 1:1 |
| 3.5 | image | 770 / 40.1 | 530 / 49.1 | 240 / 12.5 | 320 / 29.6 | 3 | centre | 3:4; EXCEPTION <3 cols — single tall glyph stays legible |
| 3.3 | image | 1075 / 56.0 | 530 / 49.1 | 300 / 15.6 | 300 / 27.8 | 4 | centre | 1:1 |
| 3.4 | image | 1420 / 74.0 | 530 / 49.1 | 400 / 20.8 | 300 / 27.8 | 5 | right | 4:3 |
| 3.2 | image | 202 / 10.5 | 800 / 74.1 | 1516 / 79.0 | 230 / 21.3 | 6 | centre | 2:1 → crop to content band |
| T3.1 | text | 90 / 4.7 | 470 / 43.5 | 640 / 33.3 | 60 / 5.6 | 10 | left | under printed Q1 |
| T3.2 | text | 90 / 4.7 | 620 / 57.4 | 640 / 33.3 | 90 / 8.3 | 10 | left | under printed Q2 |
| T3.3 | text | 90 / 4.7 | 770 / 71.3 | 640 / 33.3 | 100 / 9.3 | 10 | left | under printed Q3; sits above 3.2's band top |
Assembly: 3.1 → 3.6 → 3.5 → 3.3 → 3.4 → 3.2 → texts. Area ≈ 79/21 ✓.

## Slide 4: Real-World Problem Alignment
```
(Q1) T4.1        [4.1 persona]  [4.3 gauges]
(Q2) T4.2        [4.2 chasm ]   [4.5 schemes]
(Q3) T4.3
(Q4) T4.4        [—— 4.4 runway band ——]
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 4.1 | image | 990 / 51.6 | 215 / 19.9 | 460 / 24.0 | 345 / 31.9 | 1 | centre | 4:3 |
| 4.3 | image | 1500 / 78.1 | 215 / 19.9 | 300 / 15.6 | 300 / 27.8 | 2 | right | 1:1 |
| 4.2 | image | 990 / 51.6 | 590 / 54.6 | 460 / 24.0 | 259 / 24.0 | 3 | centre | 16:9 |
| 4.5 | image | 1500 / 78.1 | 545 / 50.5 | 300 / 15.6 | 400 / 37.0 | 4 | right | 3:4 |
| 4.4 | image | 860 / 44.8 | 855 / 79.2 | 1000 / 52.1 | 180 / 16.7 | 5 | right | 2:1 → crop to content band |
| T4.1 | text | 90 / 4.7 | 420 / 38.9 | 700 / 36.5 | 55 / 5.1 | 10 | left | under printed Q1 |
| T4.2 | text | 90 / 4.7 | 575 / 53.2 | 700 / 36.5 | 80 / 7.4 | 10 | left | under printed Q2 |
| T4.3 | text | 90 / 4.7 | 725 / 67.1 | 700 / 36.5 | 80 / 7.4 | 10 | left | under printed Q3 |
| T4.4 | text | 90 / 4.7 | 872 / 80.7 | 700 / 36.5 | 80 / 7.4 | 10 | left | under printed Q4; clears 4.4 band (starts x 860) |
Assembly: 4.1 → 4.3 → 4.2 → 4.5 → 4.4 → texts. Area ≈ 78/22 ✓.

## Slide 5: Scale of Impact
```
[5.1 losses]      [5.2 segments] [5.3 funnel]
[5.4 speed ]  T5.1(centre)       [5.6 tile ]
        [—— 5.5 channel band ——]
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 5.1 | image | 96 / 5.0 | 216 / 20.0 | 800 / 41.7 | 450 / 41.7 | 1 | left | 16:9 |
| 5.2 | image | 980 / 51.0 | 216 / 20.0 | 440 / 22.9 | 330 / 30.6 | 2 | centre | 4:3 |
| 5.3 | image | 1497 / 78.0 | 216 / 20.0 | 300 / 15.6 | 300 / 27.8 | 3 | right | 1:1 |
| 5.6 | image | 1497 / 78.0 | 560 / 51.9 | 300 / 15.6 | 300 / 27.8 | 4 | right | 1:1 |
| 5.4 | image | 96 / 5.0 | 700 / 64.8 | 440 / 22.9 | 330 / 30.6 | 5 | left | 4:3 |
| 5.5 | image | 700 / 36.5 | 800 / 74.1 | 1100 / 57.3 | 200 / 18.5 | 6 | centre | 2:1 → crop to content band |
| T5.1 | text | 700 / 36.5 | 590 / 54.6 | 760 / 39.6 | 150 / 13.9 | 10 | left | centre strip |
Assembly: 5.1 → 5.2 → 5.3 → 5.6 → 5.4 → 5.5 → T5.1. Area ≈ 80/20 ✓.

## Slide 6: Proposed Solution — TEXT-MANDATED EXCEPTION
```
(Q1) T6.1 locked 130-word box     [                ]
(Q2) T6.2 four features           [   SP4 hero     ]
(Q3) T6.3 differentiator          [                ]
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| SP4 | image | 940 / 49.0 | 280 / 25.9 | 932 / 48.5 | 524 / 48.5 | 1 | right | 16:9; smallest labels ≈14 px — do not shrink |
| T6.1 | text | 80 / 4.2 | 486 / 45.0 | 820 / 42.7 | 125 / 11.6 | 10 | left | locked box, 14 px, clears printed Q2 |
| T6.2 | text | 80 / 4.2 | 648 / 60.0 | 820 / 42.7 | 112 / 10.4 | 10 | left | 4 feature lines |
| T6.3 | text | 80 / 4.2 | 800 / 74.1 | 820 / 42.7 | 55 / 5.1 | 10 | left | differentiator |
DROP: 6.1–6.6 — superseded by SP4 (your instruction: hero replaces the set).
Assembly: SP4 → T6.1 → T6.2 → T6.3. Area: image 26% / text 35% / air 39% — image below the 65 target because the locked 100–150-word box owns the left half; SP4 is at the maximum size that keeps its labels ≥14 px. Accepted trade.

## Slide 7: User Experience
```
[============ SP5 hero ============]
T7.1 (single caption line)
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| SP5 | image | 204 / 10.6 | 140 / 13.0 | 1511 / 78.7 | 850 / 78.7 | 1 | centre | 16:9 |
| T7.1 | text | 96 / 5.0 | 1000 / 92.6 | 1500 / 78.1 | 42 / 3.9 | 10 | left | one line |
DROP: 7.1–7.5 — superseded by SP5.
Assembly: SP5 → T7.1. Area ≈ 85/15 ✓.

## Slide 8: Tech Stack & Architecture
```
(H1) T8.1   [8.2 funnel      ] [8.1 tower][8.4]
(H2) T8.2   
(H3) T8.3   [8.3 roster] [   SP3 partners   ]
(H4) T8.4
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 8.2 | image | 680 / 35.4 | 190 / 17.6 | 620 / 32.3 | 349 / 32.3 | 1 | centre | 16:9 |
| 8.1 | image | 1330 / 69.3 | 165 / 15.3 | 300 / 15.6 | 400 / 37.0 | 2 | right | 3:4; EXCEPTION <3 cols — single tower glyph |
| 8.4 | image | 1660 / 86.5 | 190 / 17.6 | 212 / 11.0 | 212 / 19.6 | 3 | right | 1:1; EXCEPTION <3 cols — two-bar chart |
| 8.3 | image | 680 / 35.4 | 580 / 53.7 | 440 / 22.9 | 330 / 30.6 | 4 | centre | 4:3 |
| SP3 | image | 1160 / 60.4 | 580 / 53.7 | 580 / 30.2 | 435 / 40.3 | 5 | right | 4:3 |
| T8.1 | text | 80 / 4.2 | 285 / 26.4 | 560 / 29.2 | 90 / 8.3 | 10 | left | under printed heading 1 |
| T8.2 | text | 80 / 4.2 | 435 / 40.3 | 560 / 29.2 | 90 / 8.3 | 10 | left | under heading 2 |
| T8.3 | text | 80 / 4.2 | 598 / 55.4 | 560 / 29.2 | 90 / 8.3 | 10 | left | under heading 3 |
| T8.4 | text | 80 / 4.2 | 748 / 69.3 | 560 / 29.2 | 80 / 7.4 | 10 | left | under heading 4 |
DROP: 8.5 (quarantine corridor — duplicated in full by SP1 one slide later) · 8.6 (deploy/honesty card — content now carried by T8.3 + SP3).
Assembly: 8.2 → 8.1 → 8.4 → 8.3 → SP3 → texts. Area ≈ 70/30 ✓ (65–75 budget).

## Slide 9: Architecture Diagram
```
[============= SP1 hero =============]
              T9.1
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| SP1 | image | 195 / 10.2 | 150 / 13.9 | 1529 / 79.6 | 860 / 79.6 | 1 | centre | 16:9; replaces the template's three placeholder prompt lines (they are fill-in placeholders like "Team Name") |
| T9.1 | text | 480 / 25.0 | 1012 / 93.7 | 960 / 50.0 | 30 / 2.8 | 10 | centre | one line |
DROP: 9.1–9.6 — superseded by SP1.
Assembly: SP1 → T9.1. Area ≈ 89/11 ✓.

## Slide 10: Feasibility
```
[10.1 ladder      ] [10.2 steps][10.3 badges]
[10.5 FP band     ] T10.1      [10.4 scope ]
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 10.1 | image | 48 / 2.5 | 200 / 18.5 | 900 / 46.9 | 506 / 46.9 | 1 | left | 16:9 |
| 10.2 | image | 972 / 50.6 | 200 / 18.5 | 438 / 22.8 | 584 / 54.1 | 2 | centre | 3:4 |
| 10.3 | image | 1434 / 74.7 | 200 / 18.5 | 438 / 22.8 | 438 / 40.6 | 3 | right | 1:1 |
| 10.4 | image | 1434 / 74.7 | 660 / 61.1 | 438 / 22.8 | 329 / 30.5 | 4 | right | 4:3 |
| 10.5 | image | 48 / 2.5 | 810 / 75.0 | 900 / 46.9 | 190 / 17.6 | 5 | left | 2:1 → crop to content band |
| T10.1 | text | 972 / 50.6 | 810 / 75.0 | 430 / 22.4 | 180 / 16.7 | 10 | left | caption block |
Assembly: 10.1 → 10.2 → 10.3 → 10.4 → 10.5 → T10.1. Area ≈ 79/21 ✓.

## Slide 11: Practicability
```
[11.1 branch   ] [11.4 mocks][11.3 price]
[11.5 SIEM band]            [11.2 cache]
T11.1
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 11.1 | image | 48 / 2.5 | 170 / 15.7 | 700 / 36.5 | 394 / 36.5 | 1 | left | 16:9 |
| 11.4 | image | 786 / 40.9 | 170 / 15.7 | 438 / 22.8 | 584 / 54.1 | 2 | centre | 3:4 |
| 11.3 | image | 1372 / 71.5 | 170 / 15.7 | 462 / 24.1 | 462 / 42.8 | 3 | right | 1:1 |
| 11.5 | image | 48 / 2.5 | 606 / 56.1 | 700 / 36.5 | 160 / 14.8 | 4 | left | 2:1 → crop to content band |
| 11.2 | image | 1372 / 71.5 | 672 / 62.2 | 438 / 22.8 | 329 / 30.5 | 5 | right | 4:3 |
| T11.1 | text | 48 / 2.5 | 800 / 74.1 | 660 / 34.4 | 140 / 13.0 | 10 | left | caption block |
Assembly: 11.1 → 11.4 → 11.3 → 11.5 → 11.2 → T11.1. Area ≈ 78/22 ✓.

## Slide 12: Sustainability
```
[12.1 precedents] [12.2 wheel][12.3 runway]
[12.5 upkeep band][12.4 export]
T12.1
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 12.1 | image | 48 / 2.5 | 170 / 15.7 | 800 / 41.7 | 450 / 41.7 | 1 | left | 16:9 |
| 12.2 | image | 900 / 46.9 | 170 / 15.7 | 440 / 22.9 | 440 / 40.7 | 2 | centre | 1:1 |
| 12.3 | image | 1390 / 72.4 | 170 / 15.7 | 440 / 22.9 | 587 / 54.4 | 3 | right | 3:4 |
| 12.5 | image | 48 / 2.5 | 680 / 63.0 | 800 / 41.7 | 170 / 15.7 | 4 | left | 2:1 → crop to content band |
| 12.4 | image | 900 / 46.9 | 650 / 60.2 | 440 / 22.9 | 330 / 30.6 | 5 | centre | 4:3 |
| T12.1 | text | 48 / 2.5 | 880 / 81.5 | 800 / 41.7 | 130 / 12.0 | 10 | left | caption block |
Assembly: 12.1 → 12.2 → 12.3 → 12.5 → 12.4 → T12.1. Area ≈ 79/21 ✓.

## Slide 13: Business Model & Roadmap
```
[========== SP2 canvas ==========]
T13.1
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| SP2 | image | 222 / 11.6 | 150 / 13.9 | 1476 / 76.9 | 830 / 76.9 | 1 | centre | 16:9 |
| T13.1 | text | 222 / 11.6 | 990 / 91.7 | 1476 / 76.9 | 48 / 4.4 | 10 | left | two lines max |
DROP: 13.1–13.6 — superseded by SP2.
Assembly: SP2 → T13.1. Area ≈ 85/15 ✓.

## Slide 14: Thank You
```
[14.1 QR plate]  [—— 14.2 screens band ——]
 (QR ZONE)       [14.3 emblem ] [14.4 ask]
T14.1 / T14.2
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| 14.1 | image | 140 / 7.3 | 300 / 27.8 | 400 / 20.8 | 400 / 37.0 | 1 | left | 1:1 · **QR ZONE: keep x 190–490, y 350–650 empty — real QR goes here** |
| 14.2 | image | 620 / 32.3 | 220 / 20.4 | 1200 / 62.5 | 260 / 24.1 | 2 | right | 2:1 → crop to content band |
| 14.3 | image | 620 / 32.3 | 540 / 50.0 | 760 / 39.6 | 428 / 39.6 | 3 | centre | 16:9 |
| 14.4 | image | 1440 / 75.0 | 540 / 50.0 | 340 / 17.7 | 453 / 41.9 | 4 | right | 3:4 |
| T14.1 | text | 140 / 7.3 | 740 / 68.5 | 420 / 21.9 | 90 / 8.3 | 10 | left | URL caption under plate |
| T14.2 | text | 140 / 7.3 | 850 / 78.7 | 420 / 21.9 | 60 / 5.6 | 10 | left | contact line |
Assembly: 14.1 → 14.2 → 14.3 → 14.4 → texts. Area ≈ 74/26 ✓.

## Slide 15: Evidence & References
```
        [====== SP6 hero ======]
T15.1 lines 1–10        T15.1 lines 11–20
```
| ID | type | x | y | w | h | z | align | note |
|---|---|---|---|---|---|---|---|---|
| SP6 | image | 460 / 24.0 | 165 / 15.3 | 1000 / 52.1 | 563 / 52.1 | 1 | centre | 16:9 |
| T15.1 | text | 48 / 2.5 | 750 / 69.4 | 1824 / 95.0 | 280 / 25.9 | 10 | left | ONE block flowed as two columns: lines 1–10 at x 48 w 900, lines 11–20 at x 972 w 900; ~13–14 px, line-height 26 |
DROP: 15.1–15.5 — superseded by SP6.
Assembly: SP6 → T15.1. Area ≈ 72/28 ✓ (hero + dense reference block).

---

## FINAL SUMMARY
Images placed: **54** · Dropped: **30** (6.1–6.6, 7.1–7.5, 9.1–9.6, 13.1–13.6, 15.1–15.5 — each set superseded by its commissioned SP hero; 8.5 duplicated by SP1's quarantine; 8.6 carried by SP3 + T8.3). 54+30 = 84 ✓.
Text blocks placed: **26 of 26**, verbatim, none truncated.
Ratio integrity: every frame matches its generated ratio; the only deviation is the stated top/bottom **crop of 2:1 rails to their content band** (3.2, 4.4, 5.5, 10.5, 11.5, 12.5, 14.2) — never stretched. Three width exceptions under the 3-column minimum are flagged in place (3.5, 8.1, 8.4 — single-glyph images that stay legible).
**Confirmation: no element enters y 0–140 (title, kicker, logo strip) or y 1045–1080 (cyan/charcoal bars) on any slide; slide 1's z-0 background is the sole stated exception and sits beneath them. Headers and footers untouched on all 15 slides.**
