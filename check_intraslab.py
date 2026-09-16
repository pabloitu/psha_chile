import hashlib, os
import numpy as np, pandas as pd

FILES = {"old": "ssm/ssm_outputs/ssm_mfd_grid.csv",
         "new": "ssm_intraslab/ssm_intraslab_outputs/ssm_mfd_grid.csv"}

for tag, f in FILES.items():
    h = hashlib.sha256(open(f, "rb").read()).hexdigest()[:12]
    print(f"{tag}: sha {h}  mtime {pd.Timestamp(os.path.getmtime(f), unit='s')}  {f}")

for tag, f in FILES.items():
    df = pd.read_csv(f)
    rc = [c for c in df.columns if c.startswith("rate_")]
    lo = np.array([float(c.split("_")[1].lstrip("M")) for c in rc])
    tot = df[rc].sum().to_numpy()
    for m in (4.9, 6.0, 7.0, 7.5):
        print(tag, f"lambda(M>={m}) = {tot[lo >= m - 1e-6].sum():.4f} /yr")
    print(tag, "top bin:", rc[-1], "| cells:", len(df))