"""S5b: OpenQuake sources of the crustal model (fits 2026-11-16f on catalogue 2026-11-16c), the family tree and the
tornado rows. Rebuild of 16 Nov (Pablo): strict UCERF3 rupture set, equal weights, thickness tags t10 / t20.

Fault systems:
- segmented: single-fault simple-fault sources, the six MFD shapes, Leonard Mmax; psi x thickness x shape, equal
  weights (Pablo, 16 Nov: every weight equal);
- multi-fault: the Liquine-Ofqui faults of A by SHERIFS on the strict UCERF3 scenarios (mfsource.py; linked ruptures
  in one multi-fault source with its sections, single-fault LOFS ruptures as simple-fault sources with their SHERIFS
  MFD), every other fault with its single-fault rates (mean of the shapes); psi x thickness, equal weights; jump
  15 km, main traces.
Background: point sources on the crustal grid, per cell the four classes summed after the join with the branch-mean
fault MFD of the fault system, nodal planes per cell mixed from the B14 class distributions (npd_2026-11-16d); 0-30 km,
hypocentre 10 km, WC1994, aspect 1; source lists from MMIN_SRC.
Tree: declustering 0.5 / 0.5 x fault system 0.5 / 0.5 x its branches, flattened. Tornado rows: one choice changed
against the reference (multi-fault A, 15 km, psi 0.8, thickness 10 km, tapered fit, Gardner-Knopoff pattern).
Writes nrml/<DATE>/ (sources, sections, lt_crustal_tree.xml, lt_crustal_reference.xml, branches.json) and
tables/rates_<DATE>.csv.
"""
import json

import numpy as np
import pandas as pd

import background as BG
import faults as F
import join as J
import mfsource as M
import nrml as X

TAB = F.HERE / "tables"

# settings
DATE = "2026-11-16g"
NR = F.HERE / "nrml" / DATE
TRT = "Active Shallow Crust"
# source Mmin 5.5 (first bin centre), as interface and in-slab, for the tornado (Pablo, 16 Nov)
MMIN_SRC = 5.5
PT = dict(usd=0.0, lsd=30.0, hypo=10.0, msr="WC1994", aspect=1.0)
FLT = dict(usd=0.0, msr="Leonard2014_Interplate", aspect=2.0)
JUMP = 15.0
MF_T, MF_PSI = (10.0, 20.0), (0.6, 0.8, 1.0)
REF = dict(db="A", jump=JUMP, t=10.0, psi=0.8, shape="taper", decl="gk")
W_SYSTEM = {"seg": 0.5, "mf": 0.5}
# tornado rows beyond the reference's own factors
JUMP_ROWS = (5.0, 10.0)
PAD_ROWS = (0.0, 0.4)
FAULT_PAD_ROWS = (0.2, 0.4)


def tag(p):
    return f"{int(round(p * 100)):03d}"


def tt(z):
    return f"t{int(z):02d}"


def bgfile(fn, title, cls, pat, nd, rows):
    """Point sources of one background: cls the class lists on J.CENTRES, pat the pattern of one declustering option."""
    k = J.CENTRES >= MMIN_SRC - 1e-6
    r = np.array([cls[c][k] for c in F.CLASSES])
    w5 = r.sum(axis=1)
    P = pat[list(F.CLASSES)].to_numpy()
    cell = P @ r
    srcs = []
    for j in range(len(pat)):
        q = cell[j]
        if q.sum() <= 0:
            continue
        q = q[:np.nonzero(q > 0)[0].max() + 1]
        i = f"bg{j:05d}"
        srcs.append(X.point(i, pat.lon[j], pat.lat[j], PT["usd"], PT["lsd"], PT["hypo"], TRT, X.mfd(MMIN_SRC, q),
                            PT["msr"], PT["aspect"], BG.mix(P[j] * w5, nd)))
        rows.append(dict(file=fn, source=i, N=q.sum(), m_top=round(MMIN_SRC + 0.1 * (len(q) - 1), 2)))
    X.model(NR / fn, title, srcs)
    print(fn, len(srcs), round(cell.sum(), 4), flush=True)
    return dict(file=fn, kind="background", n_sources=len(srcs), N55=float(cell.sum()),
                N6=float(cell[:, J.CENTRES[k] >= 5.95].sum()))


def joined(fit, fm):
    return {c: J.background(fit[c], fm[c]) for c in F.CLASSES}


def sf(q, z, r, fn, rows, prefix="f"):
    """One simple-fault source of a row q with rates r on the fault grid."""
    r = r[:np.nonzero(r > 0)[0].max() + 1]
    sid = "MF_system" if getattr(q, "system", False) else X.sid(q.fid)
    rows.append(dict(file=fn, source=f"{prefix}_{sid}", N=r.sum(), m_top=round(F.R.MMIN + 0.1 * (len(r) - 1), 2)))
    return X.simple_fault(f"{prefix}_{sid}", q["name"], q.trace, FLT["usd"], z, q.dip, q.rake, TRT, X.mfd(F.R.MMIN, r),
                          FLT["msr"], FLT["aspect"])


def seg_files(s, rr, rows, fpad=0.0):
    files = []
    for j, (p, z, k) in enumerate(F.BR):
        fp = f"_fpad{int(round(fpad * 10)):02d}" if fpad else ""
        fn = f"cr_seg_A_psi{tag(p)}_{tt(z)}_{k}{fp}.xml"
        srcs = [sf(q, z, rr[i, j], fn, rows) for i, q in s.iterrows()]
        X.model(NR / fn, f"crustal faults A, segmented, psi {p}, thickness {z:g} km, {k}, fault pad {fpad}", srcs)
        files.append(dict(file=fn, kind="faults", system="seg", db="A", psi=p, thickness=z, fshape=k, fault_pad=fpad,
                          weight=1.0 / len(F.BR)))
    return files


def mf_file(db, jump, z, psi, s, rr, rows, splays=False, pad=0.2):
    """One multi-fault branch: the other faults (mean of the shapes), the LOFS single-fault ruptures (SHERIFS MFD) as
    simple-fault sources, the linked ruptures as one multi-fault source; the sections file of (db, thickness)."""
    x = M.system(db, jump, z, psi, s, rr, splays=splays, pad=pad)
    sp = "_splays" if splays else ""
    pp = f"_pad{int(round(pad * 10)):02d}" if pad != 0.2 else ""
    fn = f"cr_mf_{db}_j{jump:g}_psi{tag(psi)}_{tt(z)}{sp}{pp}.xml"
    sec = f"cr_sections_{db}_{tt(z)}.xml"
    srcs = [sf(s.loc[i], z, r, fn, rows) for i, r in zip(x["other"], x["other_rates"])]
    sl, rups = x["sl"], []
    m = F.R.MMIN + F.R.DM * np.arange(F.NB)
    pl = {k: X.planes(np.asarray(sl.trace[k]), z, float(sl.dip[k])) for k in range(len(sl))}
    ids = {k: [f"s_{db}_{tt(z)}_{X.sid(sl.fid[k])}_{n}" for n in range(len(pl[k]))] for k in pl}
    for q, r in zip(x["src"], x["rate"]):
        if r.sum() <= 0:
            continue
        mem = q["members"]
        if len(mem) == 1:
            srcs.append(sf(sl.loc[mem[0]], z, r, fn, rows))
            continue
        rake = float(sl.rake[max(mem, key=lambda k: sl.L[k])])
        for kk in np.nonzero(r > 0)[0]:
            rups.append((m[kk], [i for k in mem for i in ids[k]], rake, r[kk]))
    if rups:
        srcs.append(X.multi_fault(f"mf_{db}_lofs", f"Liquine-Ofqui multi-fault ruptures, {db}", TRT, rups))
        rows.append(dict(file=fn, source=f"mf_{db}_lofs", N=sum(u[3] for u in rups), m_top=round(max(u[0] for u in rups), 2)))
    X.model(NR / fn, f"crustal faults {db}, multi-fault, jump {jump:g} km, psi {psi}, thickness {z:g} km{sp}{pp}", srcs, itime=1.0)
    X.sections(NR / sec, f"Liquine-Ofqui sections {db}, 0-{z:g} km", [(i, [q]) for k in pl for i, q in zip(ids[k], pl[k])])
    print(fn, len(srcs), "sources", len(rups), "ruptures", flush=True)
    return dict(file=fn, sections=sec, kind="faults", system="mf", db=db, jump=jump, psi=psi, thickness=z, splays=splays,
                pad=pad, scenarios=x["scenarios"], n_ruptures=len(rups), weight=1.0 / (len(MF_T) * len(MF_PSI)))


def main():
    NR.mkdir(parents=True, exist_ok=True)
    rows, files = [], []
    nd = BG.npds()
    pats = {m: pd.read_csv(TAB / f"pattern_{m}_{BG.DATE}.csv") for m in BG.DECL}  # patterns and fault tables of BG.DATE / F.DATE (16e), unchanged
    BG.set_pad(0.2)
    fit = {sh: {c: J.on(*BG.mfd(c, sh)) for c in F.CLASSES} for sh in BG.SHAPES}
    dfit = {c: J.on(*BG.mfd(c, "taper", REF["decl"])) for c in F.CLASSES}
    pfit = {}
    for pad in PAD_ROWS:
        BG.set_pad(pad)
        pfit[pad] = {c: J.on(*BG.mfd(c, "taper")) for c in F.CLASSES}
    BG.set_pad(0.2)
    loaded = {db: F.load(db) for db in F.DBS}
    s, rr, _ = loaded["A"]
    cases = [(z, p) for z in MF_T for p in MF_PSI]
    rz, rp = REF["t"], REF["psi"]

    # segmented faults: the 36 branches, and the fault-pad rows at the reference psi / thickness
    seg = seg_files(s, rr, rows)
    files += seg
    segpad = {}
    for fp in FAULT_PAD_ROWS:
        F.FAULT_PAD = fp
        sp_, rp_, _ = F.load("A")
        fl = seg_files(sp_, rp_, rows, fpad=fp)
        segpad[fp] = [f for f in fl if f["psi"] == rp and f["thickness"] == rz]
        files += segpad[fp]
        F.FAULT_PAD = 0.0
    fc = J.fault_classes()
    segm = {c: fc[("A", c)][0] for c in F.CLASSES}

    # multi-fault files
    mf = {}
    for z in MF_T:
        for p in MF_PSI:
            mf[("A", JUMP, z, p, False, 0.2)] = mf_file("A", JUMP, z, p, s, rr, rows)
    for jk in JUMP_ROWS:
        mf[("A", jk, rz, rp, False, 0.2)] = mf_file("A", jk, rz, rp, s, rr, rows)
    mf[("A", JUMP, rz, rp, True, 0.2)] = mf_file("A", JUMP, rz, rp, s, rr, rows, splays=True)
    for pad in PAD_ROWS:
        mf[("A", JUMP, rz, rp, False, pad)] = mf_file("A", JUMP, rz, rp, s, rr, rows, pad=pad)
    for db in ("B", "Bmm"):
        mf[(db, JUMP, rz, rp, False, 0.2)] = mf_file(db, JUMP, rz, rp, loaded[db][0], loaded[db][1], rows)
    files += list(mf.values())

    # backgrounds joined with the branch-mean fault MFD of each system
    sysm = {("A", JUMP, False, 0.2): M.mean_cls("A", JUMP, cases)}
    for jk in JUMP_ROWS:
        sysm[("A", jk, False, 0.2)] = M.mean_cls("A", jk, cases)
    sysm[("A", JUMP, True, 0.2)] = M.mean_cls("A", JUMP, cases, splays=True)
    for pad in PAD_ROWS:
        sysm[("A", JUMP, False, pad)] = M.mean_cls("A", JUMP, cases, pad=pad)
    for db in ("B", "Bmm"):
        sysm[(db, JUMP, False, 0.2)] = M.mean_cls(db, JUMP, cases)
    bgs = {}

    def add(key, title, cls, m, **kw):
        fn = f"cr_bg_{key}_{m}.xml"
        bgs[(key, m)] = fn
        files.append({**bgfile(fn, title, cls, pats[m], nd, rows), "decl": m, **kw})

    g = REF["decl"]
    for m in BG.DECL:
        add("seg_A", "crustal background, segmented A", joined(fit["taper"], segm), m, system="seg", db="A", shape="taper")
        add("mf_A_j15", "crustal background, multi-fault A 15 km", joined(fit["taper"], sysm[("A", JUMP, False, 0.2)]), m,
            system="mf", db="A", jump=JUMP, shape="taper")
    add("mf_A_j15_trunc", "crustal background, multi-fault A 15 km, cut", joined(fit["trunc"], sysm[("A", JUMP, False, 0.2)]), g,
        system="mf", db="A", jump=JUMP, shape="trunc")
    add("mf_A_j15_declrates", "crustal background, multi-fault A 15 km, declustered rates", joined(dfit, sysm[("A", JUMP, False, 0.2)]), g,
        system="mf", db="A", jump=JUMP, shape="taper", rates="declustered")
    add("nofaults", "crustal background, no faults", fit["taper"], g, system="none", shape="taper")
    for jk in JUMP_ROWS:
        add(f"mf_A_j{jk:g}", f"crustal background, multi-fault A {jk:g} km", joined(fit["taper"], sysm[("A", jk, False, 0.2)]), g,
            system="mf", db="A", jump=jk, shape="taper")
    add("mf_A_j15_splays", "crustal background, multi-fault A 15 km with splays", joined(fit["taper"], sysm[("A", JUMP, True, 0.2)]), g,
        system="mf", db="A", jump=JUMP, splays=True, shape="taper")
    for pad in PAD_ROWS:
        pp = f"pad{int(round(pad * 10)):02d}"
        add(f"mf_A_j15_{pp}", f"crustal background, multi-fault A 15 km, Mmax pad {pad}", joined(pfit[pad], sysm[("A", JUMP, False, pad)]), g,
            system="mf", db="A", jump=JUMP, pad=pad, shape="taper")
        add(f"seg_A_{pp}", f"crustal background, segmented A, Mmax pad {pad}", joined(pfit[pad], segm), g, system="seg", db="A", pad=pad, shape="taper")
    for db in ("B", "Bmm"):
        add(f"mf_{db}_j15", f"crustal background, multi-fault {db} 15 km", joined(fit["taper"], sysm[(db, JUMP, False, 0.2)]), g,
            system="mf", db=db, jump=JUMP, shape="taper")

    # tree and tornado rows: a branch is (id, [files], weight)
    def mfb(db, jk, z, p, splays=False, pad=0.2):
        x = mf[(db, jk, z, p, splays, pad)]
        return [x["file"], x["sections"]]

    tree = []
    for m in BG.DECL:
        for f in seg:
            tree.append((f"seg_{m}_{f['file'][9:-4]}", [bgs[("seg_A", m)], f["file"]], BG.W_DECL[m] * W_SYSTEM["seg"] * f["weight"]))
        for z in MF_T:
            for p in MF_PSI:
                tree.append((f"mf_{m}_psi{tag(p)}_{tt(z)}", [bgs[("mf_A_j15", m)]] + mfb("A", JUMP, z, p),
                             BG.W_DECL[m] * W_SYSTEM["mf"] / len(cases)))
    ref = [("ref", [bgs[("mf_A_j15", g)]] + mfb("A", JUMP, rz, rp), 1.0)]
    seg_ref = [f for f in seg if f["psi"] == rp and f["thickness"] == rz]
    segrow = lambda bg, fl: [(f"r{j}", [bg, f["file"]], 1 / len(fl)) for j, f in enumerate(fl)]
    rows_t = {
        "reference": ("multi-fault A, jump 15 km, psi 0.8, thickness 10 km, tapered fit, Gardner-Knopoff pattern", ref),
        "decl_nn": ("pattern from nearest-neighbour declustering", [("r", [bgs[("mf_A_j15", "nn")]] + mfb("A", JUMP, rz, rp), 1.0)]),
        "fit_cut": ("background fit cut at Mmax", [("r", [bgs[("mf_A_j15_trunc", g)]] + mfb("A", JUMP, rz, rp), 1.0)]),
        "rates_declustered": ("background rates from the declustered fits (lower bound)", [("r", [bgs[("mf_A_j15_declrates", g)]] + mfb("A", JUMP, rz, rp), 1.0)]),
        "no_faults": ("smoothed seismicity only, no faults", [("r", [bgs[("nofaults", g)]], 1.0)]),
        "segmented": ("segmented single faults (six MFD shapes, 1/6 each), psi 0.8, thickness 10 km", segrow(bgs[("seg_A", g)], seg_ref)),
        "psi060": ("multi-fault psi 0.6", [("r", [bgs[("mf_A_j15", g)]] + mfb("A", JUMP, rz, 0.6), 1.0)]),
        "psi100": ("multi-fault psi 1.0", [("r", [bgs[("mf_A_j15", g)]] + mfb("A", JUMP, rz, 1.0), 1.0)]),
        "thickness20": ("multi-fault thickness 20 km", [("r", [bgs[("mf_A_j15", g)]] + mfb("A", JUMP, 20.0, rp), 1.0)]),
        **{f"jump{jk:g}": (f"multi-fault jump {jk:g} km", [("r", [bgs[(f"mf_A_j{jk:g}", g)]] + mfb("A", jk, rz, rp), 1.0)]) for jk in JUMP_ROWS},
        "splays": ("multi-fault with the NE secondary traces linking", [("r", [bgs[("mf_A_j15_splays", g)]] + mfb("A", JUMP, rz, rp, splays=True), 1.0)]),
        **{f"db_{db}": (f"fault database {db}, multi-fault 15 km", [("r", [bgs[(f"mf_{db}_j15", g)]] + mfb(db, JUMP, rz, rp), 1.0)]) for db in ("B", "Bmm")},
        **{f"mmax_pad{int(round(pad * 10)):02d}_mf": (f"class Mmax pad {pad} (background and multi-fault cap), multi-fault reference",
                                                     [("r", [bgs[(f"mf_A_j15_pad{int(round(pad * 10)):02d}", g)]] + mfb("A", JUMP, rz, rp, pad=pad), 1.0)]) for pad in PAD_ROWS},
        **{f"mmax_pad{int(round(pad * 10)):02d}_seg": (f"class Mmax pad {pad} (background), segmented reference",
                                                      segrow(bgs[(f"seg_A_pad{int(round(pad * 10)):02d}", g)], seg_ref)) for pad in PAD_ROWS},
        **{f"fault_pad{int(round(fp * 10)):02d}_seg": (f"single faults Leonard + {fp}, segmented reference", segrow(bgs[("seg_A", g)], segpad[fp]))
           for fp in FAULT_PAD_ROWS},
    }
    X.logic_tree(NR / "lt_crustal_tree.xml", [("sourceModel", [(b, f, w) for b, f, w in tree])])
    X.logic_tree(NR / "lt_crustal_reference.xml", [("sourceModel", ref)])
    pd.DataFrame(rows).to_csv(TAB / f"rates_{DATE}.csv", index=False, float_format="%.6e")
    out = dict(
        ready=False, date=DATE, fits=str(BG.FITS.name), catalogue=str(BG.CAT.name), npd=str(BG.NPD.name), trt=TRT, min_mag=MMIN_SRC,
        investigation_time=1.0, max_distance_km=300, point=PT, fault=FLT, reference=REF,
        weights=dict(decl=BG.W_DECL, system=W_SYSTEM, seg="1/36 each (psi x thickness x shape)", mf="1/6 each (psi x thickness)"),
        rupture_set="strict UCERF3 path rules on 5 km subsections, merged to whole-fault scenarios (rupset.py); jump 15 km; main traces",
        note=("Families add in rate space. A branch lists the files of one sourceModel (background, faults and, for the "
              "multi-fault branches, the sections file). Jobs need investigation_time = 1.0."),
        tree=[dict(id=b, files=f, weight=w) for b, f, w in tree],
        tornado={k: dict(label=lab, branches=[dict(id=b, files=f, weight=w) for b, f, w in br]) for k, (lab, br) in rows_t.items()},
        files=files)
    assert abs(sum(w for *_, w in tree) - 1) < 1e-9
    (NR / "branches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float))
    print(len(tree), "tree branches;", len(rows_t), "tornado rows;", len(files), "files")


if __name__ == "__main__":
    main()
