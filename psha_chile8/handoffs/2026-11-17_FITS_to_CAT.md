# FITS to CAT, 17 Nov: converted magnitudes of the Jujuy nest

## What FITS sees
The Jujuy nest fit bends at about Mw 5.8: b 1.23 from Mw 5.0, 0.92 from 5.5, 0.74 from 6.0 (`drafts/fits/crustal_nest/nest.png`, script `explore.py`; catalogue 17f). Since 1976, split by `mw_kind` (nest weight > 0, Mw ≥ 5.0):

| mw_kind | events | Aki–Utsu b from 5.0 | from 5.5 | b-positive (pairs) |
|---|---|---|---|---|
| direct | 110 | 0.89 | 0.92 | 0.93 (41) |
| proxy | 115 | 1.96 | 1.67 | 1.89 (25) |
| all | 225 | 1.24 | 1.01 | 1.16 (74) |

- The proxies are 87 ISC `ML`, 25 ISC `mb`, 3 ComCat `mb` (σ 0.18–0.24). 47 of them are in the bin 5.0 and 105 below 5.5; only one above 5.8 (Mw 6.8, ISC mb).
- Direct Mw (76 GCMT, 31 ISC MW / Mww / Mwr, 3 ComCat and CSN) spread evenly from 5.0 to 7.2.
- The split alone does not prove a bias: a converted value fills in where no direct Mw exists, which is mostly for small events, so the proxy subset is steep and the direct subset flat by selection. The in-slab classes show the same split (intermediate: direct b 0.90, proxy 1.93; shallow 0.89, 1.78), and their fits do not bend like the nest's. What would make the nest different is a bias in the conversion of a local ML at about 200 km depth, which piles converted events into Mw 5.0–5.4. Only a paired comparison (item 2) tells.

## Please check (CAT's call, `catalog/magnitude.py`)
1. Which relation converts ISC `ML` (and deep `mb`) to Mw for the nest events, and on which events it was fitted. Is it the "CSN ML deep" relation (σ 0.19)? Was it fitted on deep events at all?
2. On the nest events that have both a GCMT Mw and an ISC ML or mb: Mw against the converted value. A bias of +0.2 to +0.3 at Mw 5.0–5.4 would explain the bend.
3. If the nest pairs show a bias, the same pairs for intermediate in-slab (b 1.16, the other unit that fails a check).
4. If the relation changes: a rerun and a new frozen catalogue, or the change folded into A11 before FITS refits.

FITS waits for your answer before the nest is refitted; nothing in `fits/` changes for it. The interim alternative, a fit from Mw 5.5 for the nest only (b 0.92 ± 0.13, Mw ≥ 7 2.5 fitted / 2.6 observed), is not taken.
