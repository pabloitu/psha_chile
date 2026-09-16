import re

Z = 60.0   # keep only cells with slab-top >= ~Z-7.5; try 50 and 60
txt = open("ssm_intraslab_point_sources.xml").read()
srcs = re.findall(r"<pointSource.*?</pointSource>", txt, re.S)
keep = [s for s in srcs
        if float(re.search(r"<upperSeismoDepth>\s*([\d.]+)", s).group(1)) >= Z]
head = txt[:txt.find("<pointSource")]
tail = txt[txt.rfind("</pointSource>") + len("</pointSource>"):]
open(f"ssm_intraslab_clip{int(Z)}.xml", "w").write(head + "\n".join(keep) + tail)
print(f"kept {len(keep)}/{len(srcs)} sources")