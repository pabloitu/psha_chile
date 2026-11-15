import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

C = {'lit': ('#e3defa', '#6250d6', 'review paper / hand-checked'),
     'best': ('#cfeee2', '#1baf7a', 'measured moment, calibrated or depth-phase'),
     'local': ('#fbdccf', '#eb6834', 'local network (relocated)'),
     'glob': ('#cde2fb', '#2a78d6', 'global catalogue / converted magnitude'),
     'hist': ('#e6e5df', '#8a897f', 'historical')}
INK, MUTED = '#1f1f1d', '#6b6a63'

panels = [
 ('Magnitude (Mw): the first that exists',
  [('before 1904', [('Ruiz & Madariaga 2018', 'lit'), ('Cabello et al. 2025', 'hist')]),
   ('1904 – 1975', [('Ruiz & Madariaga 2018', 'lit'), ('Centennial Mw (from a moment)', 'best'),
                    ('ISC-GEM direct Mw (from a moment)', 'best'), ('Centennial Ms / mB, converted', 'glob'),
                    ('ISC-GEM proxy Mw', 'glob')]),
   ('1976 – today', [('GCMT (Mw ≥ 5.4)', 'best'), ('W-phase / regional Mw\n(USGS, CSN, GFZ)', 'best'),
                     ('GCMT below 5.4, slightly lowered', 'best'),
                     ('CSN Mw of the ISC Bulletin (GUC MW),\nonly if no other measured Mw', 'best'), ('Ruiz & Madariaga 2018', 'lit'),
                     ('Converted: Ms (shallow) → CSN ML\n→ ISC mb → NEIC mb → INPRES ML', 'glob')])],
  'No usable magnitude → no Mw, event listed.  Conversions fitted on Chilean pairs (native on Mw, inverted).'),
 ('Epicentre: the first source that has the event',
  [('before 1904', [('Cabello et al. 2025', 'hist')]),
   ('1904 – 1963', [('Centennial, where relocated\n(1918–42, 1956 on)', 'best'), ('ISC-GEM', 'glob'), ('ISC', 'glob')]),
   ('1964 – today\noutside the network,\nand all of 1964–1981', [('GCCEL', 'best'), ('ISC-EHB L1 / L2', 'best'), ('ISC', 'glob'),
                    ('USGS ComCat', 'glob'), ('Potin / CSN', 'local')]),
   ('1982 – today\ninside the network\n(18–46°S, west of the arc)', [('Potin et al. 2024\n(CSN after July 2020)', 'local'), ('GCCEL', 'best'),
                    ('ISC-EHB L1 / L2', 'best'), ('ISC', 'glob'), ('USGS ComCat', 'glob')])],
  'Check: a local record more than 50 km from every global record of the event is not used.'),
 ('Depth: the first measured depth',
  [('before 1904', [('Not measured\n(Cabello\'s depths are estimates)', 'hist')]),
   ('1904 – 1963', [('Centennial free-depth solution', 'best'), ('ISC-GEM depth quality A or B', 'best')]),
   ('1964 – today\noutside the network,\nor > 20 km offshore', [('GCCEL', 'best'), ('ISC-EHB L1 / L2', 'best'), ('ISC', 'glob'),
                    ('USGS ComCat', 'glob'), ('Potin / CSN', 'local')]),
   ('1982 – today\ninside the network,\non land or near the coast', [('Potin et al. 2024\n(CSN after July 2020)', 'local'), ('GCCEL', 'best'),
                    ('ISC-EHB L1 / L2', 'best'), ('ISC', 'glob'), ('USGS ComCat', 'glob')])],
  'Skipped as not measured: fixed depths, agency defaults (10, 33, 35 km…), ISC-EHB L3, GCMT centroid.  '
  'None left → unknown.\n'
  'Class known from the literature but no measured depth → depth assigned from the class and the slab model, flagged "assigned" (any period).'),
]

BH, GAP, HEAD = 0.66, 0.14, 1.75
heights = [HEAD + max(len(b) for _, b in cols) * (BH + GAP) + 0.95 for _, cols, _ in panels]
fig = plt.figure(figsize=(13, sum(heights) * 0.62 + 1.0), dpi=160)
fig.patch.set_facecolor('white')
y0 = 1 - 0.035
tot = sum(heights)
for (title, cols, note), h in zip(panels, heights):
    fh = h / tot * 0.90
    ax = fig.add_axes([0.03, y0 - fh, 0.94, fh]); y0 -= fh + 0.012
    ax.set_xlim(0, 4); ax.set_ylim(0, h); ax.axis('off')
    ax.text(0, h - 0.05, title, fontsize=13.5, fontweight='bold', color=INK, va='top')
    w = 4 / len(cols)
    for i, (per, boxes) in enumerate(cols):
        x = i * w
        ax.text(x + w / 2, h - 0.52, per, fontsize=9.6, color=MUTED, ha='center', va='top', linespacing=1.15)
        if i: ax.plot([x, x], [0.55, h - 0.5], color='#dddcd5', lw=0.8)
        for k, (lab, kind) in enumerate(boxes):
            yb = h - HEAD - 0.1 - (k + 1) * (BH + GAP) + GAP
            fill, edge, _ = C[kind]
            ax.add_patch(FancyBboxPatch((x + 0.09, yb), w - 0.18, BH, boxstyle='round,pad=0,rounding_size=0.06',
                                        fc=fill, ec=edge, lw=1.1))
            ax.text(x + 0.16, yb + BH / 2, str(k + 1), fontsize=10, fontweight='bold', color=edge, va='center')
            ax.text(x + 0.27, yb + BH / 2, lab, fontsize=8.6 if '\n' in lab else 9.2, color=INK, va='center', linespacing=1.1)
    ax.text(0, 0.30, note, fontsize=8.8, color=MUTED, va='center', style='italic', linespacing=1.3)
    ax.plot([0, 4], [0.0, 0.0], color='#dddcd5', lw=0.8)
# legend
ax = fig.add_axes([0.03, 0.0, 0.94, 0.035]); ax.axis('off'); ax.set_xlim(0, 4); ax.set_ylim(0, 1)
x = 0
for k in ['lit', 'best', 'local', 'glob', 'hist']:
    fill, edge, lab = C[k]
    ax.add_patch(FancyBboxPatch((x, 0.3), 0.07, 0.45, boxstyle='round,pad=0,rounding_size=0.02', fc=fill, ec=edge, lw=1.1))
    ax.text(x + 0.09, 0.52, lab, fontsize=8.8, color=INK, va='center'); x += 0.12 + len(lab) * 0.0215
fig.savefig('catalog_rules.png', facecolor='white')
