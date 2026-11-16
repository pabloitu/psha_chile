"""Liquine-Ofqui multi-fault fault systems for the source model (S3/S5b): per database, jump distance, thickness and
psi, the SHERIFS partition (multifault.py) on the strict UCERF3 scenarios (rupset.py), averaged over SEEDS, and the
fault MFD per crustal class of the whole system (the other faults with their single-fault rates, the mean of the six
shapes at that psi and thickness). Results cached in tables/mfsrc_<case>_<DATE>.pkl.
"""
import pickle

import numpy as np

import faults as F
import join as J
import multifault as MF

TAB = F.HERE / "tables"
DATE = F.DATE
SEEDS = tuple(range(1, 11))


def case(db, jump, z, psi, splays=False, pad=0.2, fpad=0.0):
    """Cache key: database, jump, thickness, psi, traces, background Mmax pad, fault Mmax pad."""
    k = f"{db}_j{jump:g}_t{z:g}_psi{int(round(psi * 100)):03d}"
    if splays:
        k += "_splays"
    if pad != 0.2:
        k += f"_pad{int(round(pad * 10)):02d}"
    if fpad:
        k += f"_fpad{int(round(fpad * 10)):02d}"
    return k


def system(db, jump, z, psi, s=None, rr=None, splays=False, pad=0.2, fpad=0.0):
    """
    Fault system of one multi-fault branch: the LOFS faults by SHERIFS on the strict UCERF3 scenarios (rupset.py),
    main traces or main plus splays, scenarios above the class Mmax of `pad` dropped; the other faults with the mean
    of the shapes at (psi, z) and FAULT_PAD = fpad.

    Returns
    -------
    dict
        sl: the LOFS faults; src: SHERIFS sources (members, area, lo, hi); rate: mean rate per source and bin
        (MMIN + DM k); other: index of the non-LOFS faults in s and their rates; cls: per class the fault MFD on
        J.CENTRES (LOFS sources by the class of their longest member).
    """
    fn = TAB / f"mfsrc_{case(db, jump, z, psi, splays, pad, fpad)}_{DATE}.pkl"
    if fn.exists():
        return pickle.loads(fn.read_bytes())
    import geopandas as gpd
    import background as BG
    gpd.options.io_engine = "fiona"
    BG.set_pad(pad)
    F.FAULT_PAD = fpad
    if s is None:
        s, rr, _ = F.load(db)
    sysn = gpd.read_file(F.DBS[db]["file"]).set_index("fid")["system"]
    isl = s.fid.map(sysn).eq(MF.LOFS).to_numpy()
    sl = s[isl].reset_index(drop=True)
    MF.MIN_SR, MF.JUMP_KM, MF.PSI = (0.0 if splays else MF.MAIN_SR[db]), jump, psi
    ch = MF.strict(sl, jump)
    b = F.bvals()["arc"]
    rate = None
    for sd in SEEDS:
        src, _, r, _ = MF.run(z, sl, ch, b, np.random.default_rng(sd))
        rate = r if rate is None else rate + r
    rate /= len(SEEDS)
    j = [i for i, (p, zz, _) in enumerate(F.BR) if p == psi and zz == z]
    oth = np.where(~isl)[0]
    ro = rr[oth][:, j].mean(axis=1)
    k0 = int(round((F.R.MMIN - J.CENTRES[0]) / F.R.DM))
    n = min(F.NB, J.CENTRES.size - k0)
    cls = {c: np.zeros(J.CENTRES.size) for c in F.CLASSES}
    for i, c in zip(oth, s.cls.to_numpy()[oth]):
        cls[c][k0:k0 + n] += ro[list(oth).index(i)][:n]
    for q, r in zip(src, rate):
        c = sl.cls[max(q["members"], key=lambda f: sl.L[f])]
        cls[c][k0:k0 + n] += r[:n]
    out = dict(db=db, jump=jump, thickness=z, psi=psi, splays=splays, pad=pad, sl=sl, src=src, rate=rate, other=oth,
               other_rates=ro, cls=cls, scenarios=len(ch))
    fn.write_bytes(pickle.dumps(out))
    BG.set_pad(0.2)
    F.FAULT_PAD = 0.0
    return out


def mean_cls(db, jump, cases, splays=False, pad=0.2):
    """Per class the fault MFD of a fault system averaged over its (thickness, psi) branches, equal weights."""
    out = {c: np.zeros(J.CENTRES.size) for c in F.CLASSES}
    for z, psi in cases:
        x = system(db, jump, z, psi, splays=splays, pad=pad)
        for c in F.CLASSES:
            out[c] += x["cls"][c] / len(cases)
    return out
