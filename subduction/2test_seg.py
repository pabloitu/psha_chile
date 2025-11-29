import json
import matplotlib.pyplot as plt
from pathlib import Path

geom_path = Path("out/geometry_seg/locked_interface_2segments_geometry.json")
geom = json.loads(geom_path.read_text())

edges = geom["edges"]

def slice_edges_by_lat(edges, lat_min, lat_max):
    sliced = []
    for edge in edges:
        nodes = edge["nodes"]
        nodes_seg = [
            (n["lon"], n["lat"])
            for n in nodes
            if lat_min <= n["lat"] <= lat_max
        ]
        if len(nodes_seg) >= 2:
            sliced.append(nodes_seg)
    return sliced

seg1 = slice_edges_by_lat(edges, -45.6, -30.0)
seg2 = slice_edges_by_lat(edges, -30.0, -17.6)

fig, ax = plt.subplots(figsize=(6, 6))

for e in seg1:
    xs, ys = zip(*e)
    ax.plot(xs, ys, "-", label="seg1_south" if "seg1" not in ax.get_legend_handles_labels()[1] else None)

for e in seg2:
    xs, ys = zip(*e)
    ax.plot(xs, ys, "--", label="seg2_north" if "seg2" not in ax.get_legend_handles_labels()[1] else None)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend()
ax.set_title("Segmented interface edges (no slab)")
plt.tight_layout()
plt.show()
