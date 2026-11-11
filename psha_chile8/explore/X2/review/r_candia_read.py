"""Candia and Macedo (2026) catalogue (SRL supplement xlsx) scored with the X2 checks and matched to our events."""
XLSX = "/home/pciturri/Downloads/srl-2025449_supplement.xlsx"

import csv, re, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
src, out = XLSX, str(Path(__file__).resolve().parents[1] / "cache")
N = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
z = zipfile.ZipFile(src)
ss = []
for ev, el in ET.iterparse(z.open("xl/sharedStrings.xml")):
    if el.tag == N + "si":
        ss.append("".join(t.text or "" for t in el.iter(N + "t")))
        el.clear()
def col(r):
    c = re.match(r"[A-Z]+", r).group()
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n - 1
for sh in ("sheet2",):
    with open(f"{out}/candia_macedo.csv", "w", newline="") as f:
        w = csv.writer(f)
        for ev, el in ET.iterparse(z.open(f"xl/worksheets/{sh}.xml")):
            if el.tag == N + "row":
                row = {}
                for c in el.findall(N + "c"):
                    v = c.find(N + "v")
                    if v is None:
                        t = c.find(N + "is")
                        val = "".join(x.text or "" for x in t.iter(N + "t")) if t is not None else ""
                    else:
                        val = ss[int(v.text)] if c.get("t") == "s" else v.text
                    row[col(c.get("r"))] = val
                if row:
                    w.writerow([row.get(i, "") for i in range(max(row) + 1)])
                el.clear()
