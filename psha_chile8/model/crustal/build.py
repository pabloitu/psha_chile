"""S5b: OpenQuake sources of the crustal model, the family tree and the tornado rows. Inputs from CURRENT.md (through
background.py and faults.py); final-tree choices of DECISIONS (Logic tree, 17 Nov).

Fault systems (fault linkage, a team level at 0.5 / 0.5):
- segmented: single-fault simple-fault sources, the six MFD shapes, Leonard Mmax + the single-fault pad; psi x
  thickness x shape x pad;
- multi-fault: the Liquine-Ofqui faults by SHERIFS on the strict UCERF3 scenarios (mfsource.py; linked ruptures in one
  multi-fault source with its sections, single-fault LOFS ruptures as simple-fault sources with their SHERIFS MFD),
  every other fault with its single-fault rates (mean of the shapes); psi x thickness x LOFS secondary traces; jump
  15 km.
Fault database A in the tree; B and B-mm only as single-fault tornado rows (Pablo, 18 Nov). Background: point sources on the crustal grid, per
cell the four classes summed after the join with the branch-mean fault MFD of its branch set (database, system,
single-fault pad or secondary traces), nodal planes per cell mixed from the B14 class distributions; 0-30 km,
hypocentre 10 km, WC1994, aspect 1; source lists from MMIN_SRC; tapered fit, class Mmax pad 0.2, full-catalogue rates,
one pattern algorithm (background.DC).
Tornado rows: one choice changed against the reference (multi-fault A, 15 km, psi 0.8, thickness 10 km, main traces,
tapered fit, pattern DC).
Writes nrml/<DATE>/ (sources, sections, tree.json: the final tree; tornado.json: the one-at-a-time rows; branches.json:
the file inventory with inputs; lt_crustal_tree.xml, lt_crustal_reference.xml) and
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
# tag of the build (background.DATE: tables, caches and this folder)
DATE = BG.DATE
NR = F.HERE / "nrml" / DATE
TRT = "Active Shallow Crust"
# crustal source Mmin of the final model (first bin centre): 5.0, the fit floor (Pablo, 18 Nov, CR); 5.5 was the
# tornado value. Faults start at 6.0.
MMIN_SRC = 5.0
PT = dict(usd=0.0, lsd=30.0, hypo=10.0, msr="WC1994", aspect=1.0)
FLT = dict(usd=0.0, msr="Leonard2014_Interplate", aspect=2.0)
# fixed (DECISIONS, Logic tree, 17 Nov): jump 15 km, class Mmax pad 0.2, tapered background, full-catalogue rates
JUMP = 15.0
# branches: psi (both systems), LOFS secondary traces (multi-fault); thickness 20 km fixed (Pablo, 18 Nov, CR)
MF_T, MF_PSI = tuple(F.THICK), (0.6, 0.8, 1.0)
W_SPLAYS = {False: 0.5, True: 0.5}
# team levels at equal weight until the co-authors answer (Pablo, 17 Nov): single-fault Mmax pad, fault linkage; a
# different answer sets a weight to 0
# fault database: A alone in the tree; B and B-mm as single-fault tornado rows only, no multi-fault (Pablo, 18 Nov, CR)
DB = "A"
DB_ROWS = ("B", "Bmm")
W_FPAD = {0.0: 1 / 3, 0.2: 1 / 3, 0.4: 1 / 3}
W_SYSTEM = {"seg": 0.5, "mf": 0.5}
REF = dict(db="A", jump=JUMP, t=MF_T[0], psi=0.8, shape="taper", decl=BG.DC, splays=False, fpad=0.0)
# tornado rows beyond the tree's own levels
JUMP_ROWS = (5.0, 10.0)
PAD_ROWS = (0.0, 0.4)
FAULT_PAD_ROWS = (0.2, 0.4)
# tornado rows: level, value, the row it is measured against (DECISIONS, Hazard runs, 16 Nov: single-fault rows
# against the segmented row)
_o = {"gk": "nn", "nn": "gk"}[BG.DC]
ROW_META = {"reference": ("reference", f"multi-fault A, 15 km, psi 0.8, {MF_T[0]:g} km, main traces", None),
            f"decl_{_o}": ("spatial pattern", _o.upper(), "reference"),
            "fit_cut": ("background MFD", "cut at Mmax", "reference"),
            "rates_declustered": ("background rates", "declustered fits", "reference"),
            "no_faults": ("with faults", "no faults", "reference"),
            "segmented": ("fault linkage", "segmented", "reference"),
            "psi060": ("aseismic coefficient psi", 0.6, "reference"),
            "psi100": ("aseismic coefficient psi", 1.0, "reference"),
            "jump5": ("max. jump distance", 5.0, "reference"),
            "jump10": ("max. jump distance", 10.0, "reference"),
            "splays": ("LOFS secondary traces", "main + NE secondary", "reference"),
            "db_B": ("fault database, single-fault", "B", "segmented"),
            "db_Bmm": ("fault database, single-fault", "B-mm", "segmented"),
            "mmax_pad00_mf": ("class Mmax pad, multi-fault", 0.0, "reference"),
            "mmax_pad04_mf": ("class Mmax pad, multi-fault", 0.4, "reference"),
            "mmax_pad00_seg": ("class Mmax pad, segmented", 0.0, "segmented"),
            "mmax_pad04_seg": ("class Mmax pad, segmented", 0.4, "segmented"),
            "fault_pad02_seg": ("single-fault Mmax pad", 0.2, "segmented"),
            "fault_pad04_seg": ("single-fault Mmax pad", 0.4, "segmented")}

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


def seg_files(db, s, rr, rows, fpad=0.0):
    files = []
    for j, (p, z, k) in enumerate(F.BR):
        fp = f"_fpad{int(round(fpad * 10)):02d}" if fpad else ""
        fn = f"cr_seg_{db}_psi{tag(p)}_{tt(z)}_{k}{fp}.xml"
        srcs = [sf(q, z, rr[i, j], fn, rows) for i, q in s.iterrows()]
        X.model(NR / fn, f"crustal faults {db}, segmented, psi {p}, thickness {z:g} km, {k}, fault pad {fpad}", srcs)
        files.append(dict(file=fn, kind="faults", system="seg", db=db, psi=p, thickness=z, fshape=k, fault_pad=fpad,
                          weight=1.0 / len(F.BR)))
    return files


def segcls(s, rr):
    """Per class the branch-mean fault MFD of a segmented system on J.CENTRES (as join.fault_classes)."""
    k = int(round((F.R.MMIN - J.CENTRES[0]) / F.R.DM))
    n = min(F.NB, J.CENTRES.size - k)
    m = np.tensordot(F.W, rr, axes=(0, 1))
    out = {c: np.zeros(J.CENTRES.size) for c in F.CLASSES}
    for c in F.CLASSES:
        out[c][k:k + n] = m[(s.cls == c).to_numpy()].sum(axis=0)[:n]
    return out


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


def branch_sets():
    """The branch sets of the final tree, each with its branches and weights and the system it applies to."""
    b = lambda d: [dict(value=k, weight=w) for k, w in d.items()]
    return [dict(id="system", level="fault linkage", applies="all", branches=b(W_SYSTEM)),
            dict(id="fault_pad", level="single-fault Mmax pad (Leonard +)", applies="seg", branches=b(W_FPAD)),
            dict(id="psi", level="aseismic coefficient psi", applies="all", branches=b({p: 1 / len(MF_PSI) for p in MF_PSI})),
            *([dict(id="thickness", level="seismogenic thickness (km)", applies="all", branches=b({z: 1 / len(MF_T) for z in MF_T}))]
              if len(MF_T) > 1 else []),
            dict(id="shape", level="fault MFD shape", applies="seg", branches=b({k: 1 / len(F.R.SHAPES) for k in F.R.SHAPES})),
            dict(id="splays", level="LOFS secondary traces", applies="mf", branches=b(W_SPLAYS))]


def check(nr):
    """tree.json: every branch set adds up to 1 with no weight-0 branch, every path weight is the product of its
    branches, paths add up to 1, every path holds one branch of each set that applies, every file exists;
    tornado.json: every row's branches add up to 1 and its `against` row exists."""
    tj = json.loads((nr / "tree.json").read_text())
    sets = {s["id"]: s for s in tj["branch_sets"]}
    for s in sets.values():
        w = [x["weight"] for x in s["branches"]]
        assert min(w) > 0 and abs(sum(w) - 1) < 1e-9, s["id"]
    for q in tj["paths"]:
        need = {k for k, s in sets.items() if s["applies"] in ("all", q["branches"]["system"])}
        assert set(q["branches"]) == need, q["id"]
        w = np.prod([next(x["weight"] for x in sets[k]["branches"] if x["value"] == q["branches"][k]) for k in need])
        assert abs(w - q["weight"]) < 1e-12 and q["weight"] > 0, q["id"]
        assert all((nr / f).exists() for f in q["files"]), q["id"]
    assert abs(sum(q["weight"] for q in tj["paths"]) - 1) < 1e-9
    assert len({q["id"] for q in tj["paths"]}) == len(tj["paths"])
    tor = json.loads((nr / "tornado.json").read_text())
    ids = {r["id"] for r in tor["rows"]}
    for r in tor["rows"]:
        assert abs(sum(x["weight"] for x in r["branches"]) - 1) < 1e-9 and (r["against"] is None or r["against"] in ids), r["id"]
        assert all((nr / f).exists() for x in r["branches"] for f in x["files"]), r["id"]
    print("tree.json:", len(sets), "branch sets,", len(tj["paths"]), "paths, each set adds up to 1;",
          "tornado.json:", len(tor["rows"]), "rows")


def main():
    assert BG.MMIN <= MMIN_SRC + 1e-9, "background lists start above MMIN_SRC"
    assert f"nrml/{DATE}/" not in (F.ROOT / "CURRENT.md").read_text(), f"nrml/{DATE}/ is named in CURRENT.md"
    NR.mkdir(parents=True, exist_ok=True)
    rows, files = [], []
    nd = BG.npds()
    pats = {m: pd.read_csv(BG.TAB / f"pattern_{m}_{BG.DATE}.csv") for m in BG.DECL}
    BG.set_pad(0.2)
    fit = {sh: {c: J.on(*BG.mfd(c, sh)) for c in F.CLASSES} for sh in BG.SHAPES}
    dc, g = REF["decl"], REF["decl"]
    other = [m for m in BG.DECL if m != dc]
    dfit = {c: J.on(*BG.mfd(c, "taper", dc)) for c in F.CLASSES}
    pfit = {}
    for pad in PAD_ROWS:
        BG.set_pad(pad)
        pfit[pad] = {c: J.on(*BG.mfd(c, "taper")) for c in F.CLASSES}
    BG.set_pad(0.2)
    cases = [(z, p) for z in MF_T for p in MF_PSI]
    rz, rp = REF["t"], REF["psi"]

    # segmented faults: 36 files per single-fault pad for A, the pad-0 files for the database rows
    seg, segm, loaded = {}, {}, {}
    for db in (DB,) + DB_ROWS:
        for fp in (W_FPAD if db == DB else (0.0,)):
            F.FAULT_PAD = fp
            s_, r_, _ = F.load(db)
            if fp == 0.0:
                loaded[db] = (s_, r_)
            seg[(db, fp)] = seg_files(db, s_, r_, rows, fpad=fp)
            segm[(db, fp)] = segcls(s_, r_)
            files += seg[(db, fp)]
        F.FAULT_PAD = 0.0
    s, rr = loaded[DB]

    # multi-fault files, A only: the tree (traces x thickness x psi) and the jump and class-pad rows
    mf = {}
    for sp in W_SPLAYS:
        for z, p in cases:
            mf[(DB, JUMP, z, p, sp, 0.2)] = mf_file(DB, JUMP, z, p, s, rr, rows, splays=sp)
    for jk in JUMP_ROWS:
        mf[("A", jk, rz, rp, False, 0.2)] = mf_file("A", jk, rz, rp, s, rr, rows)
    for pad in PAD_ROWS:
        mf[("A", JUMP, rz, rp, False, pad)] = mf_file("A", JUMP, rz, rp, s, rr, rows, pad=pad)
    files += list(mf.values())

    # backgrounds joined with the branch-mean fault MFD of each branch set
    sysm = {(DB, JUMP, sp, 0.2): M.mean_cls(DB, JUMP, cases, splays=sp) for sp in W_SPLAYS}
    for jk in JUMP_ROWS:
        sysm[("A", jk, False, 0.2)] = M.mean_cls("A", jk, cases)
    for pad in PAD_ROWS:
        sysm[("A", JUMP, False, pad)] = M.mean_cls("A", JUMP, cases, pad=pad)
    bgs = {}

    def add(key, title, cls, m, **kw):
        fn = f"cr_bg_{key}_{m}.xml"
        bgs[(key, m)] = fn
        files.append({**bgfile(fn, title, cls, pats[m], nd, rows), "decl": m, **kw})

    fps = lambda fp: f"_fpad{int(round(fp * 10)):02d}" if fp else ""
    sps = lambda sp: "_splays" if sp else ""
    for db, fp in segm:
        add(f"seg_{db}{fps(fp)}", f"crustal background, segmented {db}, fault pad {fp}", joined(fit["taper"], segm[(db, fp)]), g,
            system="seg", db=db, fault_pad=fp, shape="taper")
    for sp in W_SPLAYS:
        add(f"mf_{DB}_j15{sps(sp)}", f"crustal background, multi-fault {DB} 15 km{' with splays' if sp else ''}",
            joined(fit["taper"], sysm[(DB, JUMP, sp, 0.2)]), g, system="mf", db=DB, jump=JUMP, splays=sp, shape="taper")
    for m in other:
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
    for pad in PAD_ROWS:
        pp = f"pad{int(round(pad * 10)):02d}"
        add(f"mf_A_j15_{pp}", f"crustal background, multi-fault A 15 km, Mmax pad {pad}", joined(pfit[pad], sysm[("A", JUMP, False, pad)]), g,
            system="mf", db="A", jump=JUMP, pad=pad, shape="taper")
        add(f"seg_A_{pp}", f"crustal background, segmented A, Mmax pad {pad}", joined(pfit[pad], segm[("A", 0.0)]), g, system="seg", db="A",
            pad=pad, shape="taper")

    # tree and tornado rows: a branch is (id, [files], weight)
    def mfb(db, jk, z, p, splays=False, pad=0.2):
        x = mf[(db, jk, z, p, splays, pad)]
        return [x["file"], x["sections"]]

    tree = []
    for fp in W_FPAD:
        for f in seg[(DB, fp)]:
            tree.append((f"seg_{g}_{f['file'][7:-4]}", [bgs[(f"seg_{DB}{fps(fp)}", g)], f["file"]],
                         W_SYSTEM["seg"] * W_FPAD[fp] * f["weight"],
                         dict(system="seg", fault_pad=fp, psi=f["psi"], shape=f["fshape"], **({"thickness": f["thickness"]} if len(MF_T) > 1 else {}))))
    for sp in W_SPLAYS:
        for z, p in cases:
            tree.append((f"mf_{g}_{DB}_psi{tag(p)}_{tt(z)}{sps(sp)}", [bgs[(f"mf_{DB}_j15{sps(sp)}", g)]] + mfb(DB, JUMP, z, p, sp),
                         W_SYSTEM["mf"] * W_SPLAYS[sp] / len(cases), dict(system="mf", psi=p, splays=sp, **({"thickness": z} if len(MF_T) > 1 else {}))))
    ref = [("ref", [bgs[("mf_A_j15", g)]] + mfb("A", JUMP, rz, rp), 1.0)]
    seg_ref = lambda fp: [f for f in seg[("A", fp)] if f["psi"] == rp and f["thickness"] == rz]
    segrow = lambda bg, fl: [(f"r{j}", [bg, f["file"]], 1 / len(fl)) for j, f in enumerate(fl)]
    one = lambda bg, fl: [("r", [bg] + fl, 1.0)]
    nm = {"gk": "Gardner-Knopoff", "nn": "nearest-neighbour"}
    rows_t = {
        "reference": (f"multi-fault A, jump 15 km, psi 0.8, thickness {rz:g} km, main traces, tapered fit, {nm[g]} pattern", ref),
        **{f"decl_{m}": (f"pattern from {nm[m]} declustering", one(bgs[("mf_A_j15", m)], mfb("A", JUMP, rz, rp))) for m in other},
        "fit_cut": ("background fit cut at Mmax", one(bgs[("mf_A_j15_trunc", g)], mfb("A", JUMP, rz, rp))),
        "rates_declustered": ("background rates from the declustered fits (lower bound)", one(bgs[("mf_A_j15_declrates", g)], mfb("A", JUMP, rz, rp))),
        "no_faults": ("smoothed seismicity only, no faults", [("r", [bgs[("nofaults", g)]], 1.0)]),
        "segmented": (f"segmented single faults (six MFD shapes, 1/6 each), psi 0.8, thickness {rz:g} km", segrow(bgs[("seg_A", g)], seg_ref(0.0))),
        "psi060": ("multi-fault psi 0.6", one(bgs[("mf_A_j15", g)], mfb("A", JUMP, rz, 0.6))),
        "psi100": ("multi-fault psi 1.0", one(bgs[("mf_A_j15", g)], mfb("A", JUMP, rz, 1.0))),
        **({"thickness20": ("multi-fault thickness 20 km", one(bgs[("mf_A_j15", g)], mfb("A", JUMP, 20.0, rp)))} if 10.0 in MF_T and 20.0 in MF_T else {}),
        **{f"jump{jk:g}": (f"multi-fault jump {jk:g} km", one(bgs[(f"mf_A_j{jk:g}", g)], mfb("A", jk, rz, rp))) for jk in JUMP_ROWS},
        "splays": ("multi-fault with the NE secondary traces linking", one(bgs[("mf_A_j15_splays", g)], mfb("A", JUMP, rz, rp, splays=True))),
        **{f"db_{db}": (f"fault database {db}, segmented (six MFD shapes), psi 0.8, thickness {rz:g} km",
                        segrow(bgs[(f"seg_{db}", g)], [f for f in seg[(db, 0.0)] if f["psi"] == rp and f["thickness"] == rz])) for db in DB_ROWS},
        **{f"mmax_pad{int(round(pad * 10)):02d}_mf": (f"class Mmax pad {pad} (background and multi-fault cap), multi-fault reference",
                                                     one(bgs[(f"mf_A_j15_pad{int(round(pad * 10)):02d}", g)], mfb("A", JUMP, rz, rp, pad=pad))) for pad in PAD_ROWS},
        **{f"mmax_pad{int(round(pad * 10)):02d}_seg": (f"class Mmax pad {pad} (background), segmented reference",
                                                      segrow(bgs[(f"seg_A_pad{int(round(pad * 10)):02d}", g)], seg_ref(0.0))) for pad in PAD_ROWS},
        **{f"fault_pad{int(round(fp * 10)):02d}_seg": (f"single faults Leonard + {fp}, segmented reference", segrow(bgs[(f"seg_A{fps(fp)}", g)], seg_ref(fp)))
           for fp in FAULT_PAD_ROWS},
    }
    X.logic_tree(NR / "lt_crustal_tree.xml", [("sourceModel", [(b, f, w) for b, f, w, _ in tree])])
    X.logic_tree(NR / "lt_crustal_reference.xml", [("sourceModel", ref)])
    pd.DataFrame(rows).to_csv(TAB / f"rates_{DATE}.csv", index=False, float_format="%.6e")
    out = dict(
        ready=False, date=DATE, fits=BG.FITS0.name, fits_declustered=BG.DECL_FITS.name, pad_fits=[x.name for x in BG.PAD_FITS.values()],
        catalogue=BG.CAT.name, declustered={m: x.name for m, x in BG.DECL.items()}, npd=BG.NPD.name, grid=BG.GRID.name,
        fault_db={k: v["file"].name for k, v in F.DBS.items()}, trt=TRT, min_mag=MMIN_SRC,
        investigation_time=1.0, max_distance_km=300, point=PT, fault=FLT, reference=REF,
        db=DB, db_rows=DB_ROWS, weights=dict(system=W_SYSTEM, fault_pad={str(k): v for k, v in W_FPAD.items()}, splays={str(k): v for k, v in W_SPLAYS.items()},
                     decl={m: BG.W_DECL[m] for m in BG.DECL}, seg="1/36 each (psi x thickness x shape)", mf="1/6 each (psi x thickness)"),
        rupture_set="strict UCERF3 path rules on 5 km subsections, merged to whole-fault scenarios (rupset.py); jump 15 km",
        note=("Families add in rate space. A branch lists the files of one sourceModel (background, faults and, for the "
              "multi-fault branches, the sections file). Jobs need investigation_time = 1.0."),
        files=files)
    (NR / "branches.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float))
    sets = branch_sets()
    tj = dict(family="crustal", date=DATE, trt=TRT, investigation_time=1.0, min_mag=MMIN_SRC, branch_sets=sets,
              fixed=dict(fault_database=DB, thickness_km=MF_T[0] if len(MF_T) == 1 else None, jump_km=JUMP, class_mmax_pad=0.2, background_mfd="tapered", background_rates="full catalogue",
                         pattern=BG.DECL_M[g], rupture_set="strict UCERF3, whole-fault scenarios"),
              note="A path is one sourceModel: its files, its branch of every set that applies, its weight (the product).",
              paths=[dict(id=b, branches=v, files=f, weight=w) for b, f, w, v in tree])
    (NR / "tree.json").write_text(json.dumps(tj, indent=1, ensure_ascii=False, default=float))
    tor = dict(family="crustal", date=DATE, reference="reference", rows=[
        dict(id=k, level=ROW_META[k][0], value=ROW_META[k][1], against=ROW_META[k][2], label=lab,
             branches=[dict(id=b, files=f, weight=w) for b, f, w in br]) for k, (lab, br) in rows_t.items()])
    (NR / "tornado.json").write_text(json.dumps(tor, indent=1, ensure_ascii=False, default=float))
    check(NR)
    print(len(tree), "tree branches;", len(rows_t), "tornado rows;", len(files), "files")


if __name__ == "__main__":
    main()
