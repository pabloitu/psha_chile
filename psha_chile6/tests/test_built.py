# Built source models against what they were meant to carry. The first tests run the check
# functions on a synthetic output folder; the others read the real outputs and skip if absent.

import json

import numpy as np
import pandas as pd
import pytest

import builtchecks as bc
from lib import gr, nrml, smooth

REF = {"interface": "mmin55", "intraslab": "ref", "crustal": "ref"}


def synthetic_interface(tmp_path, m0c=9.05):
    nd = tmp_path / "nrml"
    nd.mkdir()
    rows = []
    for gt, geom in (("seg", "segmented"), ("full", "non_segmented")):
        for rt, rate, chi in bc.RATES:
            for form in ("tgr", "tapered"):
                lam = 0.6 if rate == "seismic" else 0.9
                inc, e = gr.inc(lam, form, 0.9, 5.5, 9.0, 0.1, m0c, 9.6)
                nrml.model(nd / f"sub__{gt}__{rt}__{form}.xml", "m", [nrml.complex_fault("a", [[(-72, -35, 10), (-72, -34, 10)], [(-71, -35, 50), (-71, -34, 50)]], "Subduction Interface", nrml.mfd(inc, 5.5, 0.1), "StrasserInterface", 1.0, 90.0)])
                rows.append({"geom": geom, "rate": rate, "chi": chi, "form": form, "N7.0": lam * float(gr.cum(form, 0.9, 5.5, 9.0, 7.0, m0c, 9.6)),
                             "N8.0": lam * float(gr.cum(form, 0.9, 5.5, 9.0, 8.0, m0c, 9.6)), "m0_rate": lam * gr.mpr(form, 0.9, 5.5, 9.0, m0c, corner=9.6)})
    return nd, pd.DataFrame(rows)


def test_interface_check_passes_on_consistent_sources_and_flags_a_shifted_one(tmp_path):
    nd, bp = synthetic_interface(tmp_path)
    t = bc.interface_vs_table(nd, bp)
    assert not bc.worst(t), t
    inc, e = gr.inc(0.6, "tgr", 0.9, 5.5, 9.0, 0.1)
    edges = [[(-72, -35, 10), (-72, -34, 10)], [(-71, -35, 50), (-71, -34, 50)]]
    nrml.model(nd / "sub__seg__seis__tgr.xml", "m", [nrml.complex_fault("a", edges, "Subduction Interface", nrml.mfd(inc, 5.5, 0.1, 0.0), "StrasserInterface", 1.0, 90.0)])
    w = bc.worst(bc.interface_vs_table(nd, bp))        # the edge convention: bins half a step too high
    assert "M0" in w and "c0" in w


def test_points_check_matches_the_grid_it_was_written_from(tmp_path):
    e = smooth.edges(4.9, 7.4, 0.1)
    rb = smooth.tgr_bins(np.array([1.0, 2.0, 0.5]), 2.0, 0.9, e, 7.4)
    df = pd.DataFrame({"lon": [-70.0, -69.9, -69.8], "lat": [-33.0, -33.0, -33.0]})
    smooth.write(df, rb, e, tmp_path / "grid_total.csv")
    nd = tmp_path / "nrml"
    nd.mkdir()
    srcs = [nrml.point(f"p{i}", df.lon[i], df.lat[i], 0, 30, 15, "A", nrml.mfd(rb[i], e[0], 0.1), "WC1994", 1.0, [(1.0, 0, 90, 90)]) for i in range(3)]
    nrml.model(nd / "points_all.xml", "m", srcs)
    t = bc.points_vs_grid(nd, tmp_path / "grid_total.csv")
    assert abs(t["total"].iloc[0]) < 1e-6


def test_class_totals_agree_for_in_slab_files_and_crustal_grids(tmp_path):
    e = smooth.edges(4.9, 7.4, 0.1)
    for model in ("intraslab", "crustal"):
        out = tmp_path / model
        (out / "ssm").mkdir(parents=True)
        (out / "nrml").mkdir()
        rows = []
        for k, (floor, b, mmax) in {"a": (5.7, 0.94, 7.9), "b": (6.0, 0.94, 8.2), "c": (4.6, 0.96, 6.7)}.items():
            ee = smooth.edges(4.9, mmax, 0.1)
            rate = 1.2
            rb = smooth.tgr_bins(np.array([1.0, 2.0]), rate * 10 ** (-b * (4.9 - floor)), b, ee, mmax)
            df = pd.DataFrame({"lon": [-70.0, -69.9], "lat": [-33.0, -33.0]})
            smooth.write(df, rb, ee, out / "ssm" / f"grid_{k}.csv")
            nrml.model(out / "nrml" / f"intraslab_{k}.xml", "m", [nrml.point(f"p{i}", df.lon[i], df.lat[i], 0, 30, 15, "A", nrml.mfd(rb[i], ee[0], 0.1), "WC1994", 1.0, [(1.0, 0, 90, 90)]) for i in range(2)])
            rows.append({"class": k, "floor": floor, "rate_floor": rate, "b_used": b, "mmax": mmax})
        pd.DataFrame(rows).to_csv(out / "ssm" / "classes.csv", index=False)
        assert not bc.worst(bc.class_totals(out, model)), model
        pd.DataFrame(rows).assign(rate_floor=lambda d: d["rate_floor"] * 1.05).to_csv(out / "ssm" / "classes.csv", index=False)
        assert "total" in bc.worst(bc.class_totals(out, model))


def built(paths, model):
    import run
    from variants import VARIANTS
    c = run.config(model, VARIANTS[model][REF[model]])
    if not (c.OUT / "nrml").exists():
        pytest.skip(f"{model} not built: {c.OUT}")
    return c


@pytest.mark.built
def test_interface_sources_match_the_branch_table(paths):
    c = built(paths, "interface")
    pf = c.OUT / "patagonia" / "patagonia.json"
    pat = json.loads(pf.read_text()) if c.PATAGONIA and pf.exists() else None
    t = bc.interface_vs_table(c.OUT / "nrml", pd.read_csv(c.OUT / "rates" / "branches.csv", keep_default_na=False), c.M0_C, c.MMIN_HAZ, pat)
    assert not bc.worst(t), t.round(5).to_string()


@pytest.mark.built
@pytest.mark.parametrize("model", ["intraslab", "crustal"])
def test_class_rates_written_match_the_class_table(paths, model):
    c = built(paths, model)
    t = bc.class_totals(c.OUT, model)
    assert not bc.worst(t), t.to_string()


@pytest.mark.built
def test_pooled_in_slab_b_is_the_joint_weichert_fit_of_the_catalog(paths):
    import fit_check as fc
    from lib import cat
    c = built(paths, "intraslab")
    te = c.T_END or float(cat.load(paths.CATALOG)["year"].max())
    sub = fc.subsets("intraslab", c)
    g, data = [], {}
    for k in c.B_POOL:
        d = sub[k]["df"]
        m = d.loc[gr.complete(d, c.COMPLETENESS[k]), "mag"].to_numpy()
        data[k] = m
        g.append((m, c.COMPLETENESS[k], te, c.MMIN_FIT_BY_CLASS[k]))
    b = gr.weichert_joint(g, c.DM)["b"]
    cl = pd.read_csv(c.OUT / "ssm" / "classes.csv").set_index("class")
    for k in c.B_POOL:
        assert abs(cl.loc[k, "b_used"] - b) < 0.005, (k, cl.loc[k, "b_used"], b)
        w = gr.weichert(data[k], c.COMPLETENESS[k], te, c.MMIN_FIT_BY_CLASS[k], c.DM, b=b)
        assert abs(cl.loc[k, "rate_floor"] / w["rate"] - 1) < 2e-3, k


@pytest.mark.built
@pytest.mark.parametrize("model", ["intraslab", "crustal"])
def test_point_sources_match_the_smoothed_grid(paths, model):
    c = built(paths, model)
    t = bc.points_vs_grid(c.OUT / "nrml", c.OUT / "ssm" / "grid_total.csv").dropna()
    assert len(t) and not bc.worst(t), t.to_string()


@pytest.mark.built
def test_built_models_agree_with_fit_check(paths):
    import check_port
    from variants import VARIANTS
    import run
    rows = []
    for model in REF:
        c = built(paths, model)
        f = paths.ROOT / "outputs" / "fits" / model / "rates.csv"
        if not f.exists():
            pytest.skip("run fit_check.py first")
        fr = pd.read_csv(f)
        rows += check_port.rows_if(c, fr) if model == "interface" else check_port.rows_ssm(model, c, fr)
    t = pd.DataFrame(rows)
    t["diff"] = t["built"] / t["fit_check"] - 1
    pool = t["sub"].isin(["intra_slab", "slab_deep"])
    bad = t[~pool & (((t["item"] == "b") & ((t["built"] - t["fit_check"]).abs() > check_port.TOL_B)) | ((t["item"].str.startswith("N")) & (t["diff"].abs() > check_port.TOL_N)))]
    assert not len(bad), bad.to_string()


@pytest.mark.built
def test_config_completeness_tables_equal_the_fit_check_tables(paths):
    import run
    from variants import VARIANTS
    for model in REF:
        f = paths.ROOT / "outputs" / "fits" / model / "tables.json"
        if not f.exists():
            pytest.skip("run fit_check.py first")
        c = run.config(model, VARIANTS[model][REF[model]])
        for k, v in json.loads(f.read_text()).items():
            cfgt = c.COMPLETENESS if model == "interface" else c.COMPLETENESS.get(k)
            if (model == "interface" and k != "seg0_full") or not cfgt:
                continue
            a = sorted((round(float(x), 2), int(y)) for x, y in v)
            b = sorted((round(float(x), 2), int(y)) for x, y in cfgt)
            assert a == b, f"{model}/{k}: fit_check {a} config {b}"


def active_folders(paths):
    """Output folders of the reference variants and of every variant the final jobs read."""
    import run
    from variants import VARIANTS
    out = {(m, REF[m]) for m in REF}
    try:
        from hazard import logic_tree as lt
        for j in getattr(lt, "PRELIM_JOBS", []) + getattr(lt, "FINAL_JOBS", []):
            for fam in REF:
                for e in lt.JOBS[j].get(fam, []):
                    out.add((fam, e[0]))
    except Exception:
        pass
    return sorted({(m, run.config(m, VARIANTS[m][v]).OUT) for m, v in out}, key=str)


@pytest.mark.built
def test_folders_of_the_final_jobs_were_made_from_the_current_catalog(paths):
    import hashlib
    now = hashlib.sha256(open(paths.CATALOG, "rb").read()).hexdigest()[:16]
    stale = []
    for model, out in active_folders(paths):
        p = out / "decluster" / "input.json"
        if p.exists() and json.loads(p.read_text()).get("sha256") != now:
            stale.append(f"{model}/{out.name}")
    assert not stale, f"built on another catalog (rerun run_all.sh or delete): {stale}"
