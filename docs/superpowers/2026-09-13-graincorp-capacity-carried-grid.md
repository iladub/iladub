# graincorp-capacity, page 0 — the carried grid, and what verifies it

**Serves:** prog:criterion:etkl:02 — the artifact route step 3 of that document's
2026-08-20 hold note asks a reviewer to read against the source page.

**Doc impact: none.** A measurement record: no term, no behaviour, no released assertion.

Generated from the compiled graph (never transcribed) on 2026-09-13, by the span-donation
loop that closed [[R211]]. Source page: `corpus/ag-trade/graincorp-capacity-2026-08-04.pdf`.

## Why this is not a reading to be checked by eye

The hold note asked for *"a reviewer reading the carried grid against the source page"*.
The port association is instead established by four checks, each on a different
instrument, and the last two exist because the maintainer declined to accept a check the
agent had wrongly delegated. **Readings of 2026-09-13.**

| check | instrument | result |
| --- | --- | --- |
| structure | `region_tiles` / SHACL tiling shapes | 16 leaf columns covered exactly once; partition 1,1,2,2,2,2,2,2,2 |
| content | `pdftotext -layout`, measured in an earlier loop (spec § 2.5) | all seven distribution figures identical |
| per-cell geometry | each entry cell's bbox against its port's drawn interval | **406 of 406 inside, 0 outside** |
| ruling vs print | nearest printed label ink, using **no** drawn rules | **406 agree, 0 disagree** |

The fourth retires the claim that only an eye can settle whether the author's drawn rules
sit where the printed labels appear: assigning every data word to a port by proximity to
the printed label ink — a rule that never consults the ruling — reproduces the
drawn-interval assignment exactly. Every label is also wholly inside its own interval with
left and right gaps matching within about 1pt (`Mackay` 28.92/28.62, `Gladstone`
24.07/24.32, `Fisherman Islands` 8.85/9.93), which is what a centred label over its own
drawn cell looks like; an offset ruling would show as a lopsided or overflowing label.

## The zeros are invisible on the page — [[R213]], measured 2026-09-13

Every one of the **110** cells below reading `0` carries a glyph whose colour matches the
filled rectangle behind it: dark navy `(0.063, 0.2, 0.353)` on `(0.114, 0.169, 0.314)`.
Established by set identity rather than a coinciding count — 110 of 110, none genuinely
printed. **Where this grid says `0`, the page shows an empty dark cell.** The page's other
144 zero glyphs are black on pale blue: the zeros inside printed tonnages such as `10,000`.
That is a defect of the source reading, not of the span donation this grid demonstrates,
and R213 stays open — what to emit for an invisible glyph is a §8 classification.

## What is NOT claimed

- **No tonnage is grounded.** Under the corpus battery's abstaining proposer
  `ship:capacity` grounds 0 of 189. The values below are CARRIED; only the ports, the
  periods and the 14 years are grounded against the contract.
- **The year is absent on 25 of 27 rows** ([[R215]]): printed once per group, and nothing
  carries a suppressed key down without an arithmetic witness.
- Fisherman Islands / September 1st Half carries a flag and no tonnage — the one genuinely
  blank tonnage cell, which the spec measured in the same place.

## The grid

Cells read `<tonnage>/<flag>`; `0` means the page shows an empty dark cell; `—` means the
port carried no value on that row.

```
YEAR      PERIOD                     Mackay     Gladstone Fisherman Isl    Carrington   Port Kembla       Geelong      Portland
--------------------------------------------------------------------------------------------------------------------------------
2025/26   August 2nd Half               0/N      10,000/Y           0/N           0/N On Application/Y           0/N      14,000/Y
·         September 1st Half            0/N      12,500/Y             N           0/N On Application/Y           0/N           0/N
·         September 2nd Half            0/N      10,000/Y   Available/Y           0/N           0/N           0/N           0/N
2026/27   October 1st Half         10,000/Y      10,000/Y   Available/Y   Available/Y On Application/Y           0/N           0/N
·         October 2nd Half              0/N           0/N           0/N   Available/Y           0/N           0/N           0/N
·         November 1st Half             0/N           0/N   Available/Y   Available/Y On Application/Y           0/N           0/N
·         November 2nd Half             0/N           0/N   Available/Y   Available/Y On Application/Y           0/N           0/N
·         December 1st Half             0/N      10,000/Y           0/N   Available/Y           0/N           0/N           0/N
·         December 2nd Half        10,000/Y      10,000/Y           0/N           0/N On Application/Y           0/N           0/N
·         January 1st Half         10,000/Y      10,000/Y   Available/Y   Available/Y           0/N           0/N           0/N
·         January 2nd Half         10,000/Y      10,000/Y           0/N           0/N On Application/Y           0/N           0/N
·         February 1st Half        10,000/Y      10,000/Y   Available/Y           0/N           0/N           0/N           0/N
·         February 2nd Half        10,000/Y      10,000/Y           0/N           0/N On Application/Y           0/N           0/N
·         March 1st Half           25,000/Y      25,000/Y   Available/Y   Available/Y           0/N           0/N           0/N
·         March 2nd Half           25,000/Y      25,000/Y           0/N           0/N On Application/Y           0/N           0/N
·         April 1st Half           25,000/Y      25,000/Y           0/N           0/N           0/N           0/N           0/N
·         April 2nd Half           25,000/Y      25,000/Y           0/N           0/N On Application/Y           0/N           0/N
·         May 1st Half             25,000/Y      25,000/Y           0/N   Available/Y           0/N           0/N           0/N
·         May 2nd Half             25,000/Y      25,000/Y           0/N           0/N On Application/Y           0/N           0/N
·         June 1st Half            10,000/Y      10,000/Y   Available/Y   Available/Y           0/N           0/N           0/N
·         June 2nd Half            10,000/Y      10,000/Y           0/N   Available/Y On Application/Y           0/N           0/N
·         July 1st Half                 0/N      10,000/Y   Available/Y           0/N           0/N           0/N           0/N
·         July 2nd Half                 0/N      10,000/Y           0/N   Available/Y On Application/Y           0/N           0/N
·         August 1st Half               0/N           0/N   Available/Y           0/N           0/N           0/N           0/N
·         August 2nd Half               0/N           0/N           0/N   Available/Y On Application/Y           0/N           0/N
·         September 1st Half       10,000/Y      10,000/Y   Available/Y           0/N           0/N           0/N           0/N
·         September 2nd Half       10,000/Y      10,000/Y           0/N   Available/Y On Application/Y           0/N           0/N
```

189 records over 27 source rows x 7 ports.
