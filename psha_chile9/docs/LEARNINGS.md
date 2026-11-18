# LEARNINGS

What earlier rounds (psha_chile4–8) taught us: methods tried and why they were kept or dropped, and pitfalls to avoid. Lessons only; the rules are in `orchestration/DECISIONS.md`, the open points in `QUESTIONS.md`. Reviewed with Pablo on 18 Nov; numbers are from psha_chile8 unless said otherwise.

## Methods tried

### Catalogue and magnitudes
- Deduplication with a magnitude criterion (|dM| ≤ 0.8) and fixed windows: dropped. The magnitude criterion biased the later calibration pairs, and fixed windows missed large duplicates (Arauco 2011 twice, CSN and GCMT 6 s and 59 km apart).
- Constant agency offsets (ISC +0.3, CSN +0.1, USGS −0.1): dropped. The offset grows with magnitude (mb saturates above about 5.2), so one shift over-corrects small events and under-corrects large ones, and b comes to depend on the floor. A full reverse-regression re-homogenization on top over-corrected ML.
- The A2 correction (published NEIC mb relation, a hinge on ISC mb above 5.2, offsets for Md and others, dithering) made b stop depending on the floor. It was a patch on Cabello's conversions; the rebuild replaced it with one relation per agency and scale, fitted against one reference Mw.
- Hand classes for unknown-depth events: withdrawn, chosen by hazard relevance instead of evidence. A neighbour vote for unknown depths: removed. Unknown depths now take the local class shares.

### Old classifier (cat_handler_2)
- First-match rules (position against Slab2, arc polygon, trench, mechanism) plus 18 hand overrides: neither checkable nor reproducible. Hence class weights.
- Its weak spots: many events were interface only because the depth was unknown and the slab shallow; many unknown depths over the deep slab stayed unresolved; sub-slab events clustered under the flat slab and next to Jujuy. Unknown depths need a rule of their own.
- Code names and display names differed, and "intraslab" meant both a family and a class. One name per class, the same in code and figures.

### Completeness
- Tables read by hand (KS in 10-year windows, edited): defensible, not reproducible. The table must come from a rule in code.
- Shape-based Mc needs the small events: on a set cut near the fit floor every method reads the cut back. Read Mc with events from Mw 3.5. Maximum curvature reads too low everywhere: not used.
- Completeness belongs to place and time, not to the class. One Mc for the whole margin reads too high (regions with different b add up to a curved distribution), and a class-only series in a quiet segment cannot see its own history. Read Mc on all events, region by region.
- Mc by b-stability or KS reads too low in small samples (about 2 000 events needed); Mc maps with few events per cell are biased low.
- Rules that compare rates between periods (Stepp, change points, a joint likelihood) take the sequences of 2010–2015 as the normal level and call earlier periods incomplete. They work on stationary synthetic catalogues: the problem is the rate change, not the code.
- The rate rule is one-sided: it objects to too few events, never to too many, so it cannot see an excess (old in-slab magnitudes). On synthetic catalogues it puts historical steps decades early. Call it cautious, not validated.
- Tried and dropped: an ensemble of perturbed tables; a stationarity audit; a network-history table; a change-point table; a table read on crustal events alone. Each moved the table without good reason or failed the large-event check.

### b-value and rates
- Weichert on the completeness table is the reference: on synthetic catalogues built like ours it recovers b and rates and its intervals hold the truth about as often as they should. Aki–Utsu and least squares scatter much more.
- Kijko–Smit agrees with Weichert when the table fits: a check of the table, not a second b. b-positive needs no table: a cross-check, noisy for small classes.
- Converted magnitudes overcount (their errors push events above any threshold). The weight exp(−β²σ²/2) per event brings converted and measured counts together. Weight every event the same way; never move magnitudes.
- Tapered and truncated lines give the same b and rates up to about Mw 7 and part only above. A corner at the observed maximum gives the moment of a line truncated 0.2 above it.
- A small class cannot hold its own b; with the family b each crustal class reproduces its old large events. Borrow b, keep the local rate (rechecked in Q-61).
- In-slab classes keep separate b: their mechanisms and stress states differ (shallow mostly reverse, intermediate mostly normal). That the data could not tell them apart only says pooling is allowed, not that it is right.
- The large-event check (fitted against observed counts at Mw ≥ 7 and 8) is the most convincing test of b. Keep it on every run.
- Split events (weights between 0 and 1) change the rates, hardly b: weight-1 events alone give about 0.4 of the forearc rate, 0.5 of shallow in-slab, 0.75 of the interface.
- Over the shallow slab the crustal rate is mostly fractions of split events; check it against weight-1 events and hidden mechanisms (Q-68) before trusting it.
- Tried and dropped: the joint fit of b and detection (Ogata–Katsura; below Mw 5 the catalogue mixes regions and agencies); random-effects pooling; b averaged over floors. Kept as diagnostics: fits per epoch, b against the fit floor.

### Declustering
- Window methods (Gardner–Knopoff and its variants) and nearest neighbour give very different catalogues: GK removes most interface events and lowers b strongly; NN removes fewer and keeps b. The algorithm matters for rates, b and patterns.
- The full catalogue is strongly clustered: bootstrap whole clusters, not single events.
- Keep the largest event of a cluster, not the first: keeping the first dropped great mainshocks for their foreshocks (Valdivia 1960, Iquique 2014).
- Decluster per family: run on all classes together, both methods remove crustal and in-slab events as interface aftershocks.
- Nearest neighbour with the threshold set on the modern record links great historical events decades apart, and its two-Gaussian threshold counts some background events as clustered. State both as limits.
- The GK hazard increase is a b pivot (b about 0.94 → 0.74 on the margin), not evidence. b-positive, insensitive to clustering, gives about 0.88, near NN: the full-catalogue b may be slightly raised by aftershock sequences.

### Clustering in the hazard (spin-off)
- A negative binomial with one dispersion α for all magnitudes, applied per source, makes great earthquakes bursty: on the margin fit, 8–10 M ≥ 8 in some 50-year windows. Applied per rupture, the sum over many ruptures collapses to Poisson. α must fall with magnitude and be applied at source level; stochastic event sets bypass the occurrence model entirely.

### Spatial pattern
- Weighting pattern events by their completeness period let single early events dominate a city's rate (one event made most of Concepción's in-slab rate). Check the share of each city's rate from its largest single event whenever old events enter the map (Q-58).
- A calibrated Gaussian kernel and the power-law kernel gave nearly the same result; the number of neighbours matters more than the shape.
- Zoning by latitude: rejected. Masking or clipping the grid under the coast moves or deletes rate: neither adopted.

### Interface
- A time-dependent moment-deficit branch was rejected; the geodetic branch is a moment balance (revisit with Q-11).
- Mmax by moment closure (northern segments would need 9.2–9.4): a diagnostic only.
- Old tornado: aspect ratio, Allen–Hayes, top and bottom depth each moved the hazard by up to 5–10 %; tapered against truncated about 3 %.
- Classification tolerance and default-depth events moved the hazard by ≤ 5 % (Puerto Montt 9 %).

### In-slab
- Old intermediate events of Mw ≥ 7 are almost three times as frequent before 1976 as after. Completeness cannot make an excess. Measured cause: the deep Abe (1982) values read about 0.36 high and are most of the old Mw ≥ 7. Ruled out: deep-focus events, class weights, merging shallow and intermediate, an in-slab-only completeness table. What remains is a bend of b below about Mw 5.8.
- One fraction of the Slab2 thickness (0.475) holds along the margin, across magnitudes and in both depth sets; a 95 % depth per place follows the worst depths instead.
- Old depth rule (top + 7.5 km) against thickness fractions, separate against pooled b, Mmax pad: each ≤ 4–7 % of the hazard.

### Crustal and faults
- The first multi-fault attempt (moment partition, pairs at fault ends within 5 km) was aborted; hence the SHERIFS route.
- Fault depth from crustal seismicity (D90) piled up at 30 km because the old classifier capped crustal depths there. Take D90 from clearly crustal events with good depths, away from the slab (Q-20).
- The fault count test: full coupling over-predicts the observed Mw ≥ 6 near faults, mostly at Liquiñe–Ofqui; the data pull ψ down (Q-22).
- FaultQuake's length cap cuts long faults far more than short ones (it halves Ushuaia's hazard) and is not a coupling. If fault moment must fall, cut it evenly with ψ and say why.
- Faults carried about a fifth of the crustal rate at Mw ≥ 6 in an earlier round; recompute.

### GMMs and sites
- A GMM that needs inputs we do not have cannot be in the tree (Idini et al. 2017 needs a soil class).
- A soil series at Vs30 380 squeezed the in-slab GMM spread through the nonlinear site term: compare models on rock (Vs30 800); comparisons with other maps use their Vs30.
- GMM choice is the largest epistemic term everywhere (in-slab most).
- On Chilean records the global NGA-Sub models predict too low at short periods; their South America versions halve that.
- Interface event terms rise with depth and events at 40–60 km are underpredicted, possibly partly the interface / in-slab boundary of the classification.
- LLH weights over many GMMs come out nearly flat; rank shares from the bootstrap separate the models better. LLH weights alone cannot justify the tree.

### Sensitivity
- Integration distance 400 against 500 km: little difference.
- The family split is exact (proven) and within about 1 % by sampling.
- Single-GMM results need no jobs of their own: each model's curve is in the realizations of the set job.
- A geodetic branch copies the b of the seismic fit; under a declustered b the same moment moves into large events (Q-56).

## Pitfalls

### Magnitudes
- Cabello's file relation differs from its paper, and several native scales enter as Mw unchanged. Convert from native magnitudes only, and validate every relation against GCMT on pairs matched by time and distance alone.
- Forward fits (Mw on the native magnitude) are biased: GCMT has few small events, so at low native values only events with a high Mw are paired; small events are pushed up, the catalogue heaps, b comes out high. Regress the native magnitude on Mw and invert; this needs a scale reported at every size (mb, ML; not Ms).
- ISC mb and NEIC mb errors are strongly correlated: averaging them does not halve σ.
- Potin's magnitudes are the CSN bulletin values; its early coda values are unreliable.
- Heaping and combs: a conversion with slope below 1 plus rounding puts two native values in one bin and leaves the next empty; step offsets leave gaps. Dither within the native bin (uniform, or the truncated exponential of Stallone and Spassiani 2026) and use continuous corrections.
- A magnitude limit on a converted value is a cut on a noisy value and biases the count; a test that passes is not proof: check against withheld measured Mw.
- Converted mb reads about 0.1 high against regional Mw at 5.0–5.5; cause not found.
- Agency-dependent magnitudes show up as completeness steps and a floor-dependent b, not as an obvious error.
- Converting every ISC agency costs homogeneity and adds little.
- After any change of a magnitude rule, look at the largest events one by one: rate, b and histogram tests do not see a few large events moving by 0.5.

### Locations and depths
- Each agency has its own default-depth spikes (not only 0 / 10 / 33 / 35 km); ISC fixed depths at odd values are its locator's regional grid, ISC-EHB L1 fixed depths are depth-phase depths. Find defaults as histogram spikes per agency, and use the catalogues' own quality flags.
- ISC-GEM depths are ISC-EHB copies; GCMT centroids are about 12 km deeper than hypocentres.
- Potin is excellent at 18–36° S but poor south of 36° S, in the backarc, above 30 km, and 25–60 km too deep under the flat slab; distant CSN events can be off by 100 s and 900 km.
- GCCEL is a shallow benchmark and one-sided offshore (depths there 5–12 km shallower); teleseismic locations sit about 20 km east of GCCEL in the far south.
- A cut on depth σ is a cut on depth (σ is set per source and depth range): select depth sources, not σ values.
- Riedel-Hornig and Potin agree under the flat slab because both use Chilean stations only; their agreement is no test there.

### Matching
- A magnitude criterion makes calibration pairs circular: match by time and distance only, wider windows for large events, check new large pairs by eye.
- Sources list events twice (the unreviewed ISC Bulletin, Potin, ComCat).
- Before 1964 the same event differs by up to 13 s and 260 km between catalogues.
- Cut the domain on the final location (relocation moved events across the border).
- Dates and times can be wrong in a source (local time, swapped day and month): check large events against two sources.
- The legacy USGS moment tensors of 2010–2011 in ComCat carry wrong moments.

### Classification
- Depth against Slab2 hardly beats one constant weight per place; test a rule against withheld mechanisms before tuning its inputs.
- The number of split events is not a quality measure: a sharp band edge inside a continuous depth error splits every event near the edge.
- With our depth errors no rule classes more than about two thirds of the shallow-slab events right.
- Misfit plots against one mechanism hide the other mechanism families; the Kagan angle mixes plane and slip.
- Per-cell in-slab depth statistics jump at the 50 km slab-top line because of the interface band (Q-46).
- In Riedel-Hornig thrusts form a layer about 5 km below Slab2: most likely the interface with Slab2 slightly shallow, not in-slab thrusts (Q-69).

### Large events
- Split events without depth leak great events into small classes; list the split events behind any crustal Mmax or N(≥ 7).
- A literature class reaches the classification only through a row of the overrides file.
- Count independent determinations, not catalogues: every Mw 7.7 of Aysén 1960 traces back to one paper.
- A converted magnitude depends on the depth: rerun the magnitude step after depth hints.
- Tsunami validity grades the tsunami, not the earthquake.
- Large historical events north of 17° S carry unchecked classes (southern Peru giants; two 1600 events may be volcanic): check them before moving the domain north (Q-55).
- Withdrawn claims (so they do not return): "Cabello Mw 0.4 too high at M 4–4.5" was a binning artefact.

### Fits
- Say which question a test answers: "does the correction make the fit pass?" and "is the rate constant?" can answer differently.
- A count ratio without the magnitude-error weight overstates a rate change; a weight on part of the events makes results depend on the rest. One rule for all events.
- Empty bins between the largest event and Mmax raise b in small classes; an open line above Mmax adds too many large events.
- A cumulative plot carries an excess at large magnitudes down into every point below it: judge the fit bin by bin, period by period.
- An Mmax set by a split event is set by its weakest property: use weight-1 events.
- For small classes the table moves the result more than the estimator; the bootstrap does not contain the table. A fit that leaves out the old large events can be tested against them.
- Completeness steps too close together make the fit swing; a table read as a lookup gives nonsense b.
- Anchor the rate at the first complete magnitude; never change b without refitting the rate; b/√N is too optimistic.
- Sequence-rich short windows raise b; Mc and rates must use one basis (full or declustered).
- Snap magnitudes to the 0.1 grid before binned methods; check what a loader keeps before calling a method blind.
- Moving magnitudes for the error correction biases them: weight the counts.

### Source models
- Magnitudes are bin centres and OpenQuake's `min_mag` is the first centre; edges shifted every source 0.05 low, and mixed conventions once gave faults half their rate. One convention, in one place, with a moment-balance test per source.
- Zero or missing fields in fault files fall back silently (13 Fagnano segments had max_mag 0); the same trace can appear in two databases.
- The no-fault baseline must use the uncapped background grid.
- Trimmed point-source MFDs drop trailing zero bins: compare with ≤, not ==.
- The fault–background join must meet in the same bin: the first fault bin is the first lowered background bin.
- UCERF3 thresholds alone make branching chains that drain slip; SHERIFS keeps one slip budget per fault, so a partly ruptured fault cannot be represented.
- OpenQuake 3.27 multi-fault files: comma-separated section ids, one planar surface per section, ids unique across files.
- Classes on the same cells: write one point source per cell with the summed MFD (same hazard, about half the run time).
- Key caches by their inputs, not by a date.

### Hazard
- Realization order is not the tree order: write labels into the tree and read them from the datastore; sortable ids; check that the weighted mean of the realizations equals the stored mean; a physical guard (no-fault branch lowest).
- Keep the calculation id and build with every result table.
- Different Mmin across families in one job is fine; Mmin must meet at joins, and runs that are compared must share it.
- Fault sources above 52 000 ruptures need `strict = false`.
- Check for stale jobs before a batch (rows "executing" with no live process); know whether a job is in preclassical or classical.
- Sites come back sorted by longitude: match by coordinates.
- hazard2csep: mesh, precision and depth-factor traps; compare projected rates with the source totals.

### Working
- A check that finds a problem tends to produce a patch rule for a few events. Before adding one, ask whether it has a citation or whether a stated limitation would do.
- Pablo does git by hand; an automated commit script once deleted working files.
- The file bridge sometimes writes the old version: re-read and compare after every write.
- Code tested without OpenQuake or Slab2 is untested for those parts; say so.
- A process pool with numpy needs `OMP_NUM_THREADS=1`.
- Old folders hold stray copies of files: check which copy is imported before editing.

## Why the psha_chile9 design is this way
- Four generations of fit code and hand edits left no reproducible path: one builder per stage.
- Hard-coded dates went stale: settings in config, a stage reads the newest run before it.
- A shared input published five times a day meant five rebuilds: update against change reruns.
- Decisions lagged in session logs: sessions report, the orchestrator writes DECISIONS.
