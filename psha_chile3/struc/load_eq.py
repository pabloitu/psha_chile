import numpy as np
import re
import os


# ---------- SMC FORMAT READER (for .smc from CESMD/USGS) ----------

def load_smc(filename, strict=False):
    """
    Load a USGS SMC-format strong-motion file (ASCII).

    Returns
    -------
    t : np.ndarray
        Time vector in seconds.
    acc : np.ndarray
        Acceleration in cm/s^2 (as stored in the file).

    Parameters
    ----------
    strict : bool
        If True, raise an error when the number of parsed samples differs
        from the header NPTS. If False (default), use whatever number of
        samples is actually found and print a warning.
    """
    with open(filename, "r") as f:
        lines = f.readlines()

    # SMC time-series structure (per NSMP / SMC format):
    #  - 11 text-header lines
    #  - 6 integer-header lines (48 ints total, 8 per line)
    #  - 10 real-header lines (50 reals total, 5 per line)
    #  - N_comment lines (integer header cell #16)
    #  - time-series block (integer header cell #17 values)

    # --- integer headers (6 lines) ---
    int_hdr_lines = lines[11:11 + 6]
    int_vals = []
    for line in int_hdr_lines:
        l = line.rstrip("\n")
        l = l.ljust(80)  # ensure fixed width
        for i in range(0, 80, 10):
            field = l[i:i + 10].strip()
            if field:
                int_vals.append(int(field))

    if len(int_vals) < 48:
        raise ValueError(f"Expected 48 integer header values, got {len(int_vals)}")

    # --- real headers (10 lines) ---
    real_hdr_lines = lines[11 + 6:11 + 6 + 10]
    real_vals = []
    for line in real_hdr_lines:
        l = line.rstrip("\n")
        l = l.ljust(75)  # 5 fields * 15 chars
        for i in range(0, 75, 15):
            field = l[i:i + 15].strip()
            if field:
                field = field.replace("D", "E").replace("d", "e")
                real_vals.append(float(field))

    if len(real_vals) < 50:
        raise ValueError(f"Expected 50 real header values, got {len(real_vals)}")

    # Integer header cell #16 (1-based) -> number of comment lines
    n_comments = int_vals[15]
    # Integer header cell #17 (1-based) -> number of time-series values (nominal)
    n_values_header = int_vals[16]

    # Real header cell #2 (1-based) -> sampling rate [Hz]
    fs = real_vals[1]
    if fs <= 0:
        raise ValueError("Sampling rate in SMC header is undefined or non-positive.")
    dt = 1.0 / fs

    # Data start index: 11 text + 6 int + 10 real + n_comments lines
    data_start = 11 + 6 + 10 + n_comments
    data_lines = lines[data_start:]

    # Parse time-series values (format is something like 8(1PE10.4E1), but we
    # can safely just split on whitespace and parse floats)
    values = []
    for line in data_lines:
        tokens = line.strip().split()
        for tok in tokens:
            tok = tok.replace("D", "E").replace("d", "e")
            try:
                values.append(float(tok))
            except ValueError:
                # ignore anything that isn't a number
                continue

    n_found = len(values)

    if strict and n_found != n_values_header:
        raise ValueError(
            f"Header says NPTS={n_values_header}, but parsed {n_found} values."
        )

    if not strict and n_found != n_values_header:
        print(
            f"Warning: header NPTS={n_values_header}, but parsed {n_found} values "
            f"in '{filename}'. Using {n_found} samples."
        )

    acc = np.asarray(values, dtype=float)  # use all parsed values
    n_samples = len(acc)
    t = np.arange(n_samples) * dt
    return t, acc


# ---------- AT2-LIKE READER (for many .r2, .at2 with NPTS/DT) ----------

def load_at2_like(filename, dt_override=None):
    """
    Load a COSMOS/PEER-style strong-motion file with a 'NPTS= ... DT= ...' header line.
    This often works for .at2, some .r2, and similar ASCII formats.

    If dt_override is given, it is used instead of any DT found in the header.

    Returns
    -------
    t : np.ndarray
        Time vector in seconds.
    acc : np.ndarray
        Acceleration values (units as in file).
    """
    with open(filename, "r") as f:
        lines = f.readlines()

    header_line_idx = None
    npts = None
    dt = None

    # Look for a line containing NPTS and DT
    for i, line in enumerate(lines[:50]):  # usually header is early
        if "NPTS" in line.upper() and "DT" in line.upper():
            header_line_idx = i
            # Try to parse
            n_match = re.search(r"NPTS\s*=\s*(\d+)", line, re.IGNORECASE)
            dt_match = re.search(r"DT\s*=\s*([\d\.Ee+-]+)", line, re.IGNORECASE)
            if n_match:
                npts = int(n_match.group(1))
            if dt_match:
                dt = float(dt_match.group(1))
            break

    if header_line_idx is None:
        raise ValueError(
            f"Could not find 'NPTS'/'DT' header line in file: {filename}"
        )

    if dt_override is not None:
        dt = dt_override
    if dt is None or dt <= 0:
        raise ValueError("DT could not be parsed or is invalid; set dt_override.")

    # Data are typically after this header line
    data = np.loadtxt(filename, skiprows=header_line_idx + 1)
    acc = np.asarray(data).flatten()
    if npts is not None:
        acc = acc[:npts]

    t = np.arange(len(acc)) * dt
    return t, acc


# ---------- WRAPPER + RESAMPLING ----------

def load_cesmd_record(filename, dt_override=None):
    """
    Load a CESMD strong-motion file, trying to detect format from extension
    and header content. Supports:

      - .smc  -> SMC format (USGS NSMP)
      - .r2, .at2, etc. -> 'AT2-like' with NPTS/DT header (if present)

    Parameters
    ----------
    filename : str
        Path to file.
    dt_override : float, optional
        If given, overrides the DT read from AT2-like header.

    Returns
    -------
    t : np.ndarray
        Time vector in seconds.
    acc : np.ndarray
        Acceleration (as in file; usually cm/s^2 for SMC).
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".smc":
        return load_smc(filename)

    # For everything else (.r2, .v2, .at2, etc.) try AT2-like
    try:
        return load_at2_like(filename, dt_override=dt_override)
    except Exception as e:
        raise RuntimeError(
            f"Could not parse file '{filename}' as AT2-like format. "
            f"If this is a different CSMIP/COSMOS format, you'll need a "
            f'more specific parser or a conversion step.\nOriginal error: {e}'
        )


def resample_to_dt(t, acc, dt_new=0.1):
    """
    Resample an accelerogram (t, acc) to a new time step dt_new using linear interpolation.

    Parameters
    ----------
    t : array-like
        Original time array (s).
    acc : array-like
        Original acceleration array.
    dt_new : float
        Desired time step (s).

    Returns
    -------
    t_new : np.ndarray
        New time array (s).
    acc_new : np.ndarray
        Resampled acceleration array.
    """
    t = np.asarray(t)
    acc = np.asarray(acc)
    t_end = t[-1]
    t_new = np.arange(0, t_end, dt_new)
    acc_new = np.interp(t_new, t, acc)
    return t_new, acc_new


# ---------- EXAMPLE USAGE ----------

# ---------- EXAMPLE USAGE ----------
# ---------- EXAMPLE USAGE ----------

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Seaborn style matching your hazard plots
    sns.set_style(
        "darkgrid",
        {
            "ytick.left": True,
            "xtick.bottom": True,
            "axes.facecolor": ".9",
            "font.family": "Ubuntu",
        },
    )

    # Example: Iquique record from CESMD
    fname = "20140401_2346.corrected.GO01.HNN.C._a.smc"  # or .r2

    # 1) Load original Iquique record
    t, acc_cm = load_cesmd_record(fname)

    # 2) Convert to g
    g = 981.0  # cm/s^2
    acc_g = acc_cm / g

    # 3) Resample to 0.1 s
    dt_new = 0.1
    t_01, acc_g_01 = resample_to_dt(t, acc_g, dt_new=dt_new)

    # 4) WRITE RESAMPLED RECORD TO FILE (time s, accel g)
    out_eq_file = "iquique_resampled_dt0p1s.txt"
    with open(out_eq_file, "w") as f:
        f.write("# Iquique earthquake, resampled\n")
        f.write("# Columns: time_s  accel_g  (dt = {:.3f} s)\n".format(dt_new))
        for ti, ai in zip(t_01, acc_g_01):
            f.write(f"{ti:.3f}  {ai:.6e}\n")

    # 5) Plot ONLY the resampled time history, in the same style as your hazard curves
    import os
    os.makedirs("figures", exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(t_01, acc_g_01, color="darkred", lw=1.2, label=r"Iquique HNN, $\Delta t = 0.1\,\mathrm{s}$")

    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("Acceleration (g)", fontsize=10)
    ax.set_title("Iquique 2014", fontsize=11)

    # Tick + grid styling like your hazard code
    ax.tick_params(which="major", axis="y", length=8, color="gray", width=0.5)
    ax.tick_params(which="minor", axis="y", length=4, color="gray", width=0.5)
    ax.tick_params(which="major", axis="x", length=5, color="gray", width=0.5)

    ax.grid(axis="y", which="major", linewidth=1)
    ax.grid(axis="y", which="minor", linewidth=0.4)
    ax.grid(axis="x", which="major", linewidth=1)
    ax.grid(axis="x", which="minor", linewidth=0.4)

    ax.legend(loc="best", frameon=True)

    fig.tight_layout()
    fig.savefig("figures/iquique_resampled_dt0p1s.png",
                dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.show()
    plt.close(fig)
