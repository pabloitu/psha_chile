from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple, List

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from obspy.imaging.beachball import beachball as bb
from obspy.imaging.beachball import mt2plane

from cat_no_mech_handler import paths

# ---------------- Parameters ----------------
BB_SIZE_PT  = 220
DPI_OUT     = 50
FMT         = "png"
MAX_WORKERS = None   # or set an int if you want to limit processes

ONLY_DOUBLE_COUPLE = True
PREFERRED_DC_PLANE = 1  # 1 or 2

# ---------------- Class labels & colors (FINAL CLASSES) ----------------
CLASS_COLORS: Dict[str, str] = {
    "intraarc":       "firebrick",
    "slab_interface": "deepskyblue",
    "intra_slab":     "teal",
    "slab_deep":      "teal",
    "outer_rise":     "burlywood",
    "forearc":        "orange",
    "unclassified":   "purple",
}
DEFAULT_COLOR = "#7f7f7f"

IN_CSV: Path   = Path(paths.cat_classified)
OUT_ROOT: Path = Path(paths.BEACHBALLS)

_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _finite(x: object) -> bool:
    try:
        return np.isfinite(float(x))
    except Exception:
        return False


def has_tensor(row: dict) -> bool:
    comps: List[float] = []
    for k in ("Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp"):
        try:
            f = float(row.get(k))
        except (TypeError, ValueError):
            return False
        if not np.isfinite(f):
            return False
        comps.append(f)
    return any(abs(f) > 1e-12 for f in comps)


def has_sdr(row: dict) -> bool:
    return all(_finite(row.get(k)) for k in ("strike1", "dip1", "rake1"))


def get_sdr_for_dc(row: dict) -> Optional[Tuple[float, float, float]]:
    """
    For DC-only mode: prefer explicit nodal plane 1 if available,
    otherwise derive it from the moment tensor.
    """
    if has_sdr(row):
        return (float(row["strike1"]), float(row["dip1"]), float(row["rake1"]))
    if has_tensor(row):
        mt = [
            float(row["Mrr"]), float(row["Mtt"]), float(row["Mpp"]),
            float(row["Mrt"]), float(row["Mrp"]), float(row["Mtp"])
        ]
        try:
            p1, p2 = mt2plane(mt)
            return p1 if int(PREFERRED_DC_PLANE) == 1 else p2
        except Exception:
            return None
    return None


def get_class(row: dict) -> str:
    """
    Use the final 'class' column from cat_classified.
    Falls back to 'unclassified' if missing.
    """
    if "class" in row and row["class"] is not None:
        return str(row["class"]).strip()
    # Very defensive fallback in case of weird column naming
    for k in row.keys():
        if str(k).strip().lower() == "class":
            return str(row[k]).strip()
    return "unclassified"


def class_color(label: str) -> str:
    return CLASS_COLORS.get(label, DEFAULT_COLOR)


def _safe_id(s: object) -> str:
    if s is None:
        return ""
    sid = str(s).strip()
    sid = sid.replace(" ", "_")
    sid = _SANITIZE_RE.sub("_", sid)
    return sid or ""


def draw_one_png(
    out_path: Path,
    facecolor: str,
    mt: Optional[List[float]] = None,
    sdr: Optional[Tuple[float, float, float]] = None,
    width_pt: int = BB_SIZE_PT,
) -> None:
    fig = plt.figure(figsize=(width_pt / 72.0, width_pt / 72.0), dpi=72)
    fig.patch.set_alpha(0.0)

    if mt is not None:
        bb(
            mt,
            width=width_pt,
            facecolor=facecolor,
            edgecolor="black",
            linewidth=0.8,
            bgcolor="w",
            fig=fig,
        )
    else:
        bb(
            tuple(sdr),
            width=width_pt,
            facecolor=facecolor,
            edgecolor="black",
            linewidth=0.8,
            bgcolor="w",
            fig=fig,
        )

    for ax in fig.axes:
        ax.set_facecolor("none")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        str(out_path),
        format=FMT,
        dpi=DPI_OUT,
        bbox_inches="tight",
        pad_inches=0.0,
        transparent=True,
    )
    plt.close(fig)


def _render_row(row_dict: dict, out_dir: Path) -> Tuple[str, str, str]:
    """
    Return (kind, id, msg):
      kind in {"mt", "sdr", "dc", "skip", "err"}
    """
    try:
        eid = _safe_id(row_dict.get("id"))
        if not eid or eid.lower() == "nan":
            return ("skip", eid, "no id")

        label = get_class(row_dict)
        color = class_color(label)
        out_path = out_dir / f"{eid}.{FMT}"

        if ONLY_DOUBLE_COUPLE:
            sdr = get_sdr_for_dc(row_dict)
            if sdr is None:
                return ("skip", eid, "no DC info")
            draw_one_png(out_path, color, mt=None, sdr=sdr)
            return ("dc", eid, "")

        # Fallback: full MT if available, else SDR
        if has_tensor(row_dict):
            mt = [
                float(row_dict["Mrr"]), float(row_dict["Mtt"]), float(row_dict["Mpp"]),
                float(row_dict["Mrt"]), float(row_dict["Mrp"]), float(row_dict["Mtp"])
            ]
            draw_one_png(out_path, color, mt=mt, sdr=None)
            return ("mt", eid, "")

        if has_sdr(row_dict):
            sdr = (
                float(row_dict["strike1"]),
                float(row_dict["dip1"]),
                float(row_dict["rake1"]),
            )
            draw_one_png(out_path, color, mt=None, sdr=sdr)
            return ("sdr", eid, "")

        return ("skip", eid, "no MT/SDR")
    except Exception as e:
        return ("err", _safe_id(row_dict.get("id")), str(e))


def render_catalog(csv_path: Path, out_dir: Path) -> None:
    if not csv_path.exists():
        print(f"[skip] not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    if "id" not in df.columns:
        print(f"[skip] {csv_path} has no 'id' column.")
        return

    rows = df.to_dict("records")

    ok_mt = ok_sdr = ok_dc = skipped = errs = 0

    # Parallel rendering
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(_render_row, r, out_dir) for r in rows]
        for fut in as_completed(futures):
            kind, _, _ = fut.result()
            if kind == "mt":
                ok_mt += 1
            elif kind == "sdr":
                ok_sdr += 1
            elif kind == "dc":
                ok_dc += 1
            elif kind == "skip":
                skipped += 1
            else:
                errs += 1

    mode = "DC-only" if ONLY_DOUBLE_COUPLE else "auto(MT→SDR)"
    total = len(rows)
    print(
        f"[classified] mode={mode}  MT:{ok_mt} SDR:{ok_sdr} DC:{ok_dc} "
        f"skipped:{skipped} errors:{errs} total:{total} -> {out_dir}"
    )


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    render_catalog(IN_CSV, OUT_ROOT)


if __name__ == "__main__":
    main()
