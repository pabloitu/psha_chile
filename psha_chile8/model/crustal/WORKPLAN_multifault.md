# Work plan: multi-fault ruptures for the crustal faults (S3 follow-up)

15 Nov 2026. For Pablo to approve before any code. References in `../../../refs/faults/`.

## Why

- **The problem.** The arc count test (REPORT_S3, section 1b) rejects the fault model with Leonard Mmax:
  - The short Liquiñe–Ofqui faults (10–120 km, Mmax 6.0–7.4) spend their whole slip-rate moment on Mw 6–7, giving 3–8 times the observed Mw 6–7 rate.
  - Nothing in the model can produce Aysén 1960 (Mw 7.7).
- **Fixes rejected so far:**
  - The class maximum: unphysical, about 38 m of slip on a 35 km segment (Pablo).
  - New joined traces: rejected by Pablo.
- **What this plan does.** It keeps the fault geometry of A and B as it is. It adds ruptures that break several existing faults together, and shares each fault's slip-rate moment between its single-fault and multi-fault ruptures.

## What stays as it is

- Fault traces, dips, depths, slip rates and ψ of A, B and B-mm (D16, D16b, DECISIONS).
- Leonard (2014) for every rupture's magnitude from its area, single or linked (DECISIONS; Pablo, 15 Nov).
- Fault Mmin 6.0 and moments at the bin centres (DECISIONS, LEARNINGS).
- The background and the join rule: below 6.0 the fit; from 6.0 the fit minus the faults; zero from the first bin the faults fill (Pablo, 15 Nov). It now uses the total fault MFD of each class, single plus linked ruptures.

## Steps

**1. Rupture set: which faults may break together.**
- Rule: the UCERF3 plausibility filters (Milner et al. 2013, Appendix T, Table T1). On the whole set of faults of each database, no hand selection.

| filter | threshold | source |
|---|---|---|
| jump between the closest points of two faults (3-D) | ≤ 5 km | Milner et al. 2013, T1; consistent with the jumps of the Wesnousky (2008) rupture database, as Milner et al. say |
| azimuth change at a junction | ≤ 60° | T1 |
| azimuth change start to end of the rupture | ≤ 60° | T1 |
| cumulative azimuth change | ≤ 560° | T1 |
| cumulative rake change | ≤ 180° | T1 |
| sinistral to dextral junction | azimuth of the sinistral fault reversed | Appendix T, "Junction azimuth change" |
| Coulomb filter | **not applied** | needs ΔCFF per junction (Parsons et al. 2012); stated as a simplification |

- **Units: whole faults** of the database, not subsections. UCERF3 cuts faults into subsections half the seismogenic thickness long (Milner et al. 2013); SHERIFS suggests sections about the seismogenic depth (Chartier et al. 2019).
  - With whole faults a linked rupture always takes the full length of each member. Partial ruptures of one fault stay as OpenQuake's floating ruptures on the simple-fault source.
  - Subsections are the step to take only if the quick estimate shows the unit size matters.
  - The "at least two subsections per fault" filter then does not apply.
- Output: the list of ruptures (members, length, area), a map of the linked chains, a table per class.

**2. Magnitudes of each rupture.**
- Mmax by Leonard (2014) on the summed area of the members, one value per depth branch, as now.
- A linked rupture hosts the bins above the largest Mmax of its members, up to its own Mmax. That is the range drawn in Chartier et al. (2017), Fig. 1b: fault-to-fault scenarios carry the bins above the single faults.
  - Reason: a linked rupture has a fixed surface, the union of the members, so it cannot carry events smaller than its members already carry.
  - This range is read from the figure, not stated in the text.

**3. Rates: the SHERIFS moment partition** (Chartier et al. 2017, section 2, step 4; Chartier et al. 2019), reimplemented, not their code:
- Each fault's budget is ψ × slip rate, cut into increments dsr of 0.01 mm/yr (the 2017 paper's example).
- Loop until every budget is spent:
  1. Draw a magnitude bin from the target MFD of the fault system, in moment rate.
  2. Draw at random a source that can host it (a single fault or a linked rupture).
  3. Add dM0 = μ A dsr and the rate dM0 / M0(Mi) to that source (eqs. 1–2).
  4. Remove dsr from every member's budget.
- **Anchoring:** once a fault taking part in the three largest bins is exhausted, the level of the target is fixed.
  - The third-largest bin is held at no more than twice the mean of the two largest (Chartier et al. 2019).
  - From then on an increment that would exceed the target in its bin becomes non-main-shock (NMS) slip, not earthquakes.
- **The target MFD shape:**
  - Gutenberg–Richter with the b of the class (B11 fit; Patagonia the forearc b), from 6.0 to the largest rupture Mmax of the system.
  - Chartier et al. (2017, 2019) impose a GR shape on the whole fault system.
  - The background share R per bin of SHERIFS is not used: our join rule does that job (decision 3 below).
- **The fault system** is each connected group of faults of the rupture set (step 1). An isolated fault is a system of its own.
- **Outputs:**
  - the rate of every rupture
  - the NMS share of every fault, i.e. how much of its slip rate the target cannot use
  - Chartier et al. (2019): NMS above 30–40 % means the inputs need to be reconsidered.
- **Randomness:** the drawing is random, so one seed per branch, plus a check that two seeds give rates within a few per cent.

**4. The fault tree.**
- ψ (3) × depth (2) as now (DECISIONS). The SHERIFS partition runs per branch, because the budget (ψ) and the Mmax (depth) change.
- The six MFD shapes (DECISIONS) do not fit SHERIFS, where the system shape is imposed and each fault's MFD comes out of the partition (decision 2).

**5. The join and the checks.**
- Per class: the total fault MFD (single plus linked; a linked rupture goes to the class of most of its length) against the fit, with the join rule.
- The arc count test (`arc.py`) repeated.
- **Independent checks**, since SHERIFS imposes the shape but not the level:
  - the NMS share per fault
  - the rate of Mw ≥ 7 against the record (Aysén 1960, 1927)
  - the recurrence of the largest Liquiñe–Ofqui ruptures
- Moment balance per fault: earthquakes plus NMS equals ψ × slip rate (test).

**6. OpenQuake files.**
- Single-fault ruptures stay simple-fault sources, with the MFD the partition gives them.
- Linked ruptures go in one multi-fault source per database and branch: the faults as sections, a list of ruptures with magnitude and rate. That is the OpenQuake form for multi-fault ruptures (as for UCERF3 and NSHM23 in OpenQuake).
- Background files from the new join.
- Parse check of all files, as `oqcheck.py`.

## Quick estimate first (before the full model)

- **Scope:** database A, arc class only, ψ 0.8, depths 10 and 20 km, whole faults as units, one seed.
- **Builds:** steps 1–3 and the arc count test.
- **Shows:**
  - how many linked ruptures the rule allows and how long the chains get
  - the new arc MFD against the record
  - the NMS share of the Liquiñe–Ofqui faults
- No OpenQuake files. About an hour.

## Full model after that

- Steps 1–6 for A, B and B-mm, all classes, all ψ × depth branches, two seeds.
- Join, report section, figures, tests, parse check.

## Decisions for Pablo

1. **DECISIONS** says "Multi-fault ruptures: not in the model (aborted, future work) (Oct)". This plan reopens it; the line needs his word.
2. **MFD shapes.**
   - SHERIFS imposes one GR shape on each fault system, and each fault's MFD follows from the partition.
   - Either the six shapes of DECISIONS go for linked systems (isolated faults keep them), or SHERIFS replaces them for every fault (one rule).
   - Proposed: SHERIFS for every fault, so that one rule makes every fault MFD. The shape uncertainty then sits in the target shape (GR with the class b, and the b bounds of the fit).
3. **Background.** SHERIFS splits each magnitude bin between faults and background by an expert ratio R (Chartier et al. 2019, Fig. 1). We keep our join rule instead: it uses the catalogue fit directly and has no expert ratio.
4. **Coulomb filter** of UCERF3 left out (it needs ΔCFF per junction). The remaining filters are geometric.
5. **Units:** whole faults for the quick estimate; subsections (half the seismogenic thickness, Milner et al. 2013) only if needed.

## References

- Chartier, T., Scotti, O., Lyon-Caen, H., Boiselet, A. (2017). Methodology for earthquake rupture rate estimates of fault networks: example for the western Corinth rift, Greece. NHESS 17, 1857–1869. doi:10.5194/nhess-17-1857-2017.
- Chartier, T., Scotti, O., Lyon-Caen, H. (2019). SHERIFS: Open-source code for computing earthquake rates in fault systems and constructing hazard models. SRL 90(4), 1678–1688. doi:10.1785/0220180332.
- Milner, K. R., Page, M. T., Field, E. H., Parsons, T., Biasi, G. P., Shaw, B. E. (2013). Appendix T: Defining the inversion rupture set using plausibility filters. In Field et al., UCERF3, USGS OFR 2013-1165.
- Field, E. H., et al. (2014). UCERF3: the time-independent model. BSSA 104(3), 1122–1180. doi:10.1785/0120130164.
- Wesnousky, S. G. (2006). Predicting the endpoints of earthquake ruptures. Nature 444, 358–360 (text not extractable; the 5 km jump rests on Milner et al. citing Wesnousky 2008).
- Leonard, M. (2014). Self-consistent earthquake fault-scaling relations. BSSA 104(6).
- Parsons, T., et al. (2012), cited by Milner et al. for the Coulomb filter (not used).
