# Classification method (draft, 18 Nov)

How each event gets its class weights, why, and how the method is set and validated. Rules: DECISIONS, Classification (D-CLS). Open questions: Q-46, Q-60, Q-68, Q-69, Q-47. CAT implements and tests; STATS reads the weights.

## 1. Idea in one paragraph

Each event gets a weight per class (interface, in-slab, crustal, outer rise, non-earthquake) that adds up to 1. A weight is the probability that the event belongs to that class, given its position, its depth with its error, and its mechanism if it has one. The rates of a class are the sum of its weights, which is the expected number of events of that class. Where the data decide, an event takes one class; where they do not, it is split, and the split carries the uncertainty into the rates instead of hiding it.

## 2. Inputs

- Catalogue: epicentre, depth and depth σ (D-CAT-14), Mw, mechanism (D-CAT-16), literature class hints (D-CAT-17).
- Slab2: slab top, thickness, uncertainty.
- Trench (PB2002), and the class polygons from DATA (forearc, arc, backarc, Patagonia; Jujuy nest; Scotia–Antarctic).

## 3. Rules, in order

1. **Known class, weight 1:** literature class (Ruiz and Madariaga, overrides with a reference); non-earthquake flagged by a source; outer rise (west of the trench, or west of the forearc polygon and not interface or in-slab).
2. **Depth score over the shallow slab** (slab top ≤ 50 km), after Haynie et al. (2026):
   - interface: a band around the slab top, centred at Slab2 + offset, with a width and a lower end that fades out. **Offset, width and lower end are set from data (section 5)**, per latitude band where the data allow;
   - crustal and in-slab share the rest, above and below the slab top (Moho at 40 km);
   - the scores are averaged over the event's depth error (a normal distribution with its σ, cut at the ground). This averaging is ours; Haynie et al. use the depth as exact.
3. **Mechanism:** a mechanism that fits the slab plane slipping in the convergence direction (m ≤ 1) multiplies the interface odds by a factor; one that does not removes the interface share. The factor is measured, not chosen (section 5). A mechanism never decides alone.
4. **Deeper slab:** depth with its error above or below the slab surface; below the slab is in-slab.
5. **No usable depth** (none, agency default, locator-fixed): position rules (no slab: crustal; deep slab and all rejected depths ≥ 70 km: in-slab); otherwise the shares of the depth-classified events at the same place and magnitude. In the probability reading these are the local prior shares, the best estimate when the depth says nothing (D-CLS-13). Historical forearc events without a hint: no crustal share (D-CLS-06).
6. **Rounding:** a weight ≥ 0.8 becomes 1 (D-CLS-05). Stated as a simplification: it moves the class totals by about 5 % (psha_chile8 A7 sensitivity).
7. **Sub-classes** by position (D-CLS-07); **assigned depths** only for literature classes (D-CLS-02).

## 4. Why weights and not one class

- A rate is a count. If an event is 60 % likely interface, the honest contribution to the interface count is 0.6. Forcing it to 1 or 0 makes each event look certain and biases the class with the larger share upward.
- The sum of the weights is the expected count of the class (the mean of a sum of Bernoulli variables). That is the whole statistical justification for summing weights in the rates.
- It holds only if the weights are **calibrated**: events given 0.3 must be crustal about 30 % of the time. Section 6 tests exactly that.

## 5. Setting the parameters from data

**Interface band (Q-69).**
- Events: interface-like thrusts (m ≤ 1) over the shallow slab, with the best depths (ISC-EHB L1, GCCEL, depth-phase depths); then all depths as a check.
- For each latitude band (the four interface segments, finer where events allow): d = depth − Slab2 top.
  - **offset:** median of d;
  - **width:** the spread of d with the depth errors removed, by the simple moment correction w² = var(d) − mean(σ²) (a robust spread in place of the variance); the band is offset ± 2w;
  - **lower end:** the depth where the interface thrusts run out (their 95th percentile), with the fade over the spread above it.
- Uncertainty: bootstrap over events (Efron and Tibshirani 1993) gives a range for each parameter; its 5th and 95th percentiles become the tornado rows (D-CLS-08: today top 0 / 10, bottom 50 / 60).
- Checks: the same parameters in magnitude bins and periods (mechanisms depend on both); the lower end against Tichelaar and Ruff (1991; 48–53 km, change near 28° S) and Heuret et al. (2011); in Riedel-Hornig et al. (2026) inside Chile, the same parameters from its sharper depths.

**Mechanism factor.** The ratio of the share of m ≤ 1 mechanisms inside the band to their share well outside it (psha_chile8: 3.9), remeasured with the new band, per latitude band if stable.

## 6. Validation

1. **Hidden mechanisms (Q-68).** Classify the events that have a mechanism without it; compare the weights with the class their mechanism indicates. Scores: Brier and log score (Brier 1950; Gneiting and Raftery 2007) and a reliability diagram (DeGroot and Fienberg 1983), per class and region. Settings are chosen on some regions and scored on the others (block cross-validation; Roberts et al. 2017). Baselines: the fixed ± 15 km band, and one constant weight per place. psha_chile8 found depth alone barely beats the constant (Brier 0.20 against 0.18); the new band has to do better, or the paper says depth adds little and the mechanisms and shares carry the classification.
2. **Riedel-Hornig check (Q-69).** On the ~19 000 matched events (2017–2021, inside Chile), our weights with our depths against the classes from its depths. A check, not ground truth: it uses the same Chilean stations.
3. **Figures for every run:** depth below the slab top by class weight and slab-top depth (Q-46); shallow in-slab reverse events against the offset; rates with weight-1 events only against all (D-STA-15).

## 7. Limits (stated in the paper)

- Depth σ are partly floors we set, and formal errors are too small; the width depends on them.
- Offshore depths are one-sided (5–12 km shallow): an apparent offset there can be bias.
- Slab2 was itself built partly from earthquake locations, interface thrusts included; the offset from Slab2 is partly circular. The Riedel-Hornig check is the independent part.
- The crustal–in-slab boundary (the Moho) is not observed; the crustal share over the shallow slab rests on a fixed Moho depth.
- Mechanisms exist mostly from about Mw 5 and from 1976; the method is tested on those events and assumed for the rest.

## 8. Paragraph for the paper (draft)

> Each event receives class weights that add up to one and are read as class probabilities; class rates are sums of weights, the expected counts per class. Over the shallow slab the weights follow the depth scores of Haynie et al. (2026), averaged over the depth error of each event, with the interface band (offset below Slab2, width and lower end) measured from the depths of interface-type thrusts with well-constrained depths, per segment, rather than fixed. A mechanism consistent with the plate interface raises the interface odds by a measured factor. Events without a usable depth take the class shares of the classified events nearby. The weights were validated against withheld focal mechanisms with proper scoring rules and a reliability diagram, using regional block cross-validation, and checked against the local catalogue of Riedel-Hornig et al. (2026). The band's bootstrap range enters the sensitivity analysis.

## 9. References (to place in `refs/` and check before citing)

Haynie et al. (2026); Hayes et al. (2018, Slab2); Tichelaar and Ruff (1991); Heuret et al. (2011); Riedel-Hornig et al. (2026); Brier (1950); Gneiting and Raftery (2007); DeGroot and Fienberg (1983); Roberts et al. (2017); Efron and Tibshirani (1993). Kept as a possible supplement check, not the method: a full mixture model with per-event errors (McLachlan and Peel 2000; Bovy, Hogg and Roweis 2011).
