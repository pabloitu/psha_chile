import re

Z = 50.0   # keep sources whose upperSeismoDepth >= Z; usd = slab top in
           # the original build, so Z = interface locking bottom. Try 50, 60.
SRC = "ssm_intraslab_point_sources.xml"

txt = open(SRC).read()
srcs = re.findall(r"<pointSource.*?</pointSource>", txt, re.S)
keep = [s for s in srcs
        if float(re.search(r"<upperSeismoDepth>\s*([\d.]+)", s).group(1)) >= Z]
head = txt[:txt.find("<pointSource")]
tail = txt[txt.rfind("</pointSource>") + len("</pointSource>"):]
out = f"ssm_intraslab_clip{int(Z)}.xml"
open(out, "w").write(head + "\n".join(keep) + tail)
print(f"kept {len(keep)}/{len(srcs)} sources -> {out}")