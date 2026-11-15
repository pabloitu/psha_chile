"""Large events one by one (plan A6): selection, dossiers, report tables and figure.

The events of the brief are selected from the working catalogue. For each one and each property (time,
epicentre, depth, Mw, mechanism) the dossier lists what every linked source gives, the catalogue's choice, and the
literature values of A6/literature.csv (typed in by hand from the papers, with reference and page). Proposed
corrections are data: overrides_A6.csv, applied by magnitude.py and locate.py once a row is 'accepted'.
"""
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from match import SRC, OUT, FROZEN, DATES

# settings
RUN = "2026-11-13c"
A3 = "2026-11-11"
HERE = Path(__file__).resolve().parent
A6, FIGS = HERE / "A6", HERE / "figs" / "A6"
LIT, OVER = A6 / "literature.csv", HERE / "overrides_A6.csv"
BIG, MID = 6.95, 5.95
PERIODS = [("before 1904", "0000", "1904"), ("1904–1963", "1904", "1964"), ("1964–1975", "1964", "1976"), ("from 1976", "1976", "9999")]
NAMED = ["cl20100227082528", "cl20110107045522", "cl19600522185602", "cl19600606055549", "cl19221111043243", "cl19390125033214",
         "cl19501209213851", "cl19181204114751"]
# events outside the selection for which a paper read in A6 gives a moment
EXTRA = ["cl19710508004947"]
NAMED_DAYS = ["1878-01-23", "1928-12-02", "1919-03-02", "2025-05-02", "1647-05", "1768", "1786", "1918-12-18"]
LISTS = {"mw_iscgem_centennial": RUN, "id_disagree": A3, "pre1964_window": A3, "rm18_matches": A3, "close_events_m45": A3,
         "possible_splits": A3, "distant_events": RUN, "mech_mw_differs": RUN, "mech_m0_mismatch": RUN, "mw_large_proxy": RUN}
SRCS = ["rm2018", "centennial", "iscgem", "iscehb", "gccel", "isc", "comcat", "gcmt", "potin", "csn", "csn_isc", "cabello"]
TABLE_MW, TABLE_Z, TABLE_DM = 6.95, 30.0, 0.3
KIND = {"rm18": "Ruiz and Madariaga (2018)", "direct": "measured Mw", "centennial": "Centennial", "iscgem": "ISC-GEM",
        "cabello": "historical (Cabello et al.)", "proxy": "converted", "a6": "corrected in A6"}
COL = {"rm18": "#1b1b1b", "direct": "#2a78b5", "centennial": "#d9822b", "iscgem": "#3a9a5c", "cabello": "#8e6bb0", "proxy": "#b0b0b0",
       "a6": "#c0392b"}


def period(t):
    return next(n for n, a, b in PERIODS if a <= t[:4] < b)


def select(c):
    """Events of the brief: why -> event ids. c is the catalogue (in the domain only for groups 1 and 2)."""
    d = c[c.in_domain]
    why = {}
    add = lambda ids, w: [why.setdefault(i, []).append(w) for i in ids]
    add(d[d.mw >= BIG].event_id, "Mw >= 7")
    add(d[(d.mw >= MID) & (d.mw < BIG) & d.depth.isna()].event_id, "Mw 6-7 without depth")
    add([i for i in NAMED if i in set(c.event_id)], "named in the brief")
    add(c[c.time.str[:10].isin(NAMED_DAYS) | c.time.str[:7].isin(NAMED_DAYS)].query("mw >= 5.95").event_id, "named in the brief")
    add(EXTRA, "moment found in the literature")
    m6 = set(c[c.mw >= MID].event_id)
    for n, run in LISTS.items():
        f = OUT / "review" / f"{n}_{run}.csv"
        if not f.exists():
            continue
        x = pd.read_csv(f, low_memory=False)
        ids = pd.concat([x[k] for k in ("event_id", "event_a", "event_b", "to_event") if k in x]).dropna().unique()
        keep = set(ids) & m6 if n not in ("mech_mw_differs", "mech_m0_mismatch", "mw_large_proxy") else set(ids) & set(c.event_id)
        if n == "rm18_matches":
            keep = set(x[x.n_candidates > 1].event_id) & m6
        add(sorted(keep), f"review list {n}")
    return why


def source_rows(ids):
    """What each linked source gives for the selected events: one row per event, source record and property."""
    L = pd.read_csv(OUT / f"links_{A3}.csv", dtype=str, usecols=["event_id", "src", "src_id"]).drop_duplicates()
    L = L[L.event_id.isin(ids)]
    rows = []
    for s in SRCS:
        l = L[L.src == s]
        if l.empty:
            continue
        d = DATES.get(s, FROZEN)
        ev = pd.read_csv(Path(SRC) / f"{s}_{d}_events.csv", dtype=str)
        ev = ev[ev.prime.isin(["True", "true", "1"]) | ~ev.src_id.duplicated(keep=False)].drop_duplicates("src_id")
        ev = l.merge(ev, on=["src", "src_id"])
        for r in ev.itertuples():
            fl = ";".join(str(v) for v in (getattr(r, "depth_fixed", None), getattr(r, "depth_quality", None)) if isinstance(v, str) and v not in ("False", "nan"))
            rows += [(r.event_id, "time", s, r.src_id, r.time, ""), (r.event_id, "epicentre", s, r.src_id, f"{r.lat} {r.lon}", r.agency),
                     (r.event_id, "depth", s, r.src_id, r.depth, fl.replace("True", "fixed"))]
            if s == "rm2018":
                rows.append((r.event_id, "class hint", s, r.src_id, r.rm_class, f"domain {r.domain}; {r.basis}"))
        f = Path(SRC) / f"{s}_{d}_mags.csv"
        if f.exists():
            m = l.merge(pd.read_csv(f, dtype=str), on=["src", "src_id"])
            m = m[m.mag.notna() | (m.src == "rm2018")]
            rows += [(r.event_id, "Mw", s, r.src_id, r.mag if isinstance(r.mag, str) else r.note, f"{r.agency} {r.mag_type}" + (f"; {r.note}" if isinstance(r.note, str) and isinstance(r.mag, str) else ""))
                     for r in m.itertuples()]
    return pd.DataFrame(rows, columns=["event_id", "property", "source", "source_id", "value", "flags"]).drop_duplicates()


def dossiers(c, why):
    """dossiers.csv: source values, the catalogue's choice with its rule, literature values and the proposal."""
    x = c[c.event_id.isin(why)].set_index("event_id")
    S = source_rows(set(why))
    S["kind"] = "source"
    cat = []
    for i, r in x.iterrows():
        mech = f"{r.strike1:.0f}/{r.dip1:.0f}/{r.rake1:.0f}" if pd.notna(r.strike1) else ""
        cat += [(i, "time", r.loc_src, r.loc_src_id, r.time, ""), (i, "epicentre", r.loc_src, r.loc_src_id, f"{r.lat} {r.lon}", r.loc_flags),
                (i, "depth", r.depth_src, r.depth_src_id, r.depth, f"sigma {r.depth_sigma}; {r.depth_kind}"),
                (i, "Mw", r.mw_src, r.mw_src_id, r.mw, f"sigma {r.mw_sigma}; {r.mw_kind}; {r.mw_agency} {r.mw_type} {r.native_value}; {r.mw_flags}"),
                (i, "mechanism", r.mech_src, r.mech_id, mech, f"Mw of the tensor {r.mech_mw}; {r.mech_flag}")]
    C = pd.DataFrame(cat, columns=S.columns[:6]).assign(kind="catalogue")
    lit = pd.read_csv(LIT, dtype=str) if LIT.exists() else pd.DataFrame(columns=["event_id", "property", "value", "reference", "page", "read", "note"])
    Lt = pd.DataFrame({"event_id": lit.event_id, "property": lit.property, "source": lit.reference, "source_id": lit.page, "value": lit.value,
                       "flags": lit.note.fillna("") + np.where(lit["read"].eq("no"), " †", ""), "kind": "literature"})
    ov = pd.read_csv(OVER, dtype=str) if OVER.exists() else pd.DataFrame(columns=["event_id", "property", "new_value", "reference", "page", "reason", "status"])
    P = pd.DataFrame({"event_id": ov.event_id, "property": ov.property.replace({"mw": "Mw", "class_hint": "class hint", "lat": "epicentre", "lon": "epicentre", "exists": "existence"}),
                      "source": ov.reference, "source_id": ov.page, "value": ov.new_value, "flags": ov.reason, "kind": "proposal (" + ov.status + ")"})
    D = pd.concat([S, C, Lt, P], ignore_index=True)
    D = D[D.event_id.isin(why)]
    done = set(lit.event_id) | set(ov.event_id)
    seen = lit.groupby("event_id").reference.agg(lambda v: "; ".join(sorted(set(v)))) if len(lit) else pd.Series(dtype=str)
    same = [(i, "all", seen.get(i, ""), "", "checked, no change", "", "result") for i in why if i in done and i not in set(ov.event_id)]
    todo = [(i, "all", "source catalogues of the links", "", "source values compared, no literature read", "", "result") for i in why if i not in done]
    D = pd.concat([D, pd.DataFrame(same + todo, columns=D.columns)], ignore_index=True)
    D["time"], D["mw"] = D.event_id.map(x.time), D.event_id.map(x.mw)
    D["selected_for"] = D.event_id.map({k: "; ".join(dict.fromkeys(v)) for k, v in why.items()})
    o = {"time": 0, "epicentre": 1, "depth": 2, "Mw": 3, "mechanism": 4, "existence": 5, "class hint": 6, "all": 7}
    k = {"source": 0, "catalogue": 1, "literature": 2}
    D["o"], D["k"] = D.property.map(o), D.kind.map(k).fillna(3)
    D = D.sort_values(["time", "event_id", "o", "k"], kind="stable").drop(columns=["o", "k"])
    return D[["event_id", "time", "mw", "selected_for", "property", "kind", "source", "source_id", "value", "flags"]]


def figure(c, why):
    """Mw against time for Mw >= 6 in the domain, coloured by the kind of Mw; proposed Mw changes as arrows."""
    plt.rcParams["font.family"] = "Ubuntu"
    d = c[c.in_domain & (c.mw >= MID)].sort_values("mw")
    t = pd.to_datetime(d.time.str[:10], errors="coerce").dt.year + pd.to_datetime(d.time.str[:10], errors="coerce").dt.dayofyear / 365.25
    t = t.fillna(d.time.str[:4].astype(float))
    fig, ax = plt.subplots(2, 1, figsize=(13, 9), gridspec_kw={"height_ratios": [1, 1.4]})
    ov = pd.read_csv(OVER, dtype=str) if OVER.exists() else pd.DataFrame(columns=["event_id", "property", "new_value"])
    ov = ov[ov.property == "mw"].set_index("event_id").new_value.astype(float)
    for a, (lo, hi) in zip(ax, [(1500, 1904), (1904, 2027)]):
        for k, name in KIND.items():
            q = (d.mw_kind == k).to_numpy() & (t >= lo).to_numpy() & (t < hi).to_numpy()
            if q.any():
                a.scatter(t[q], d.mw[q], s=8 + 14 * (d.mw[q] - 6) ** 2, c=COL[k], label=f"{name} ({int(q.sum())})", lw=0.3, ec="white", zorder=3)
        for i, v in ov.items():
            j = d.event_id == i
            if j.any() and lo <= t[j].iloc[0] < hi:
                a.annotate("", (t[j].iloc[0], v), (t[j].iloc[0], d.mw[j].iloc[0]), arrowprops=dict(arrowstyle="->", color=COL["a6"], lw=1.3), zorder=4)
        a.set_xlim(lo, hi)
        a.set_ylim(5.9, 9.8)
        a.set_ylabel("Mw")
        a.grid(alpha=0.25, lw=0.5)
        a.legend(loc="upper left", fontsize=9, ncol=3, frameon=False)
    ax[0].set_title(f"Events of Mw ≥ 6 in the model domain, by the kind of their Mw; arrows: corrections proposed in A6 ({len(ov)})", loc="left", fontsize=11)
    ax[1].set_xlabel("year")
    FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGS / "large_events.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def tables(c, s):
    """Report tables: counts by period, the changes for Pablo to accept or reject, events still without depth."""
    ov = pd.read_csv(OVER, dtype=str)
    x = c.set_index("event_id")
    ov["time"], ov["period"] = ov.event_id.map(x.time), ov.event_id.map(x.time).map(period)
    ov["mw"], ov["depth"] = ov.event_id.map(x.mw), ov.event_id.map(x.depth)
    n = pd.crosstab(s.period, s.result).reindex([p[0] for p in PERIODS])
    n = n.join(pd.crosstab(ov.period, ov.property).add_prefix("proposed: "), how="left").fillna(0).astype(int)
    n.loc["all"] = n.sum()
    n.to_csv(A6 / "counts.csv")
    num = pd.to_numeric(ov.new_value, errors="coerce") - pd.to_numeric(ov.old_value, errors="coerce")
    k = (ov.property != "class_hint") & ((ov.mw >= TABLE_MW) | ((ov.property == "depth") & (num.abs() >= TABLE_Z)) | ((ov.property == "mw") & (num.abs() >= TABLE_DM - 1e-9)))
    ov[k][["event_id", "time", "property", "old_value", "new_value", "sigma", "reference", "page", "reason"]].to_csv(A6 / "changes_for_review.csv", index=False)
    hint = ov[ov.property == "class_hint"].groupby("event_id").agg(hint=("new_value", lambda v: " / ".join(dict.fromkeys(v))), ref=("reference", lambda v: "; ".join(dict.fromkeys(v))))
    d = s[s.depth.isna() & (s.mw >= MID)].join(hint, on="event_id")
    d[["event_id", "time", "lat", "lon", "mw", "mw_kind", "period", "hint", "ref"]].to_csv(A6 / "no_depth.csv", index=False)
    print(n.to_string())
    print("for review:", int(k.sum()), "| without depth after A6:", len(d), "of them with a class hint:", int(d.hint.notna().sum()))


def main():
    A6.mkdir(exist_ok=True)
    c = pd.read_csv(OUT / f"catalog_{RUN}.csv", low_memory=False)
    why = select(c)
    D = dossiers(c, why)
    D.to_csv(A6 / "dossiers.csv", index=False)
    s = c[c.event_id.isin(why)][["event_id", "time", "lat", "lon", "depth", "mw", "mw_kind", "in_domain"]].copy()
    s["period"], s["selected_for"] = s.time.map(period), s.event_id.map({k: "; ".join(dict.fromkeys(v)) for k, v in why.items()})
    res = D[D.kind == "result"].set_index("event_id").value
    s["result"] = s.event_id.map(res).fillna("change proposed")
    s.to_csv(A6 / "selection.csv", index=False)
    figure(c, why)
    tables(c, s)
    print("selected", len(s), s.period.value_counts().to_dict())
    print(pd.crosstab(s.period, s.result).to_string())
    g = s.selected_for.str.split("; ").explode().value_counts()
    print(g.to_string())


if __name__ == "__main__":
    main()
