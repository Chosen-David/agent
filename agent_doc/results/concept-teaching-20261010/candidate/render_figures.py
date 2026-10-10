"""Exact teaching figures; run with Python, NumPy, Matplotlib and Pillow.

No model measurement or sampled data. All inputs are given in prompts.md.
"""
from pathlib import Path
import json
import hashlib
import platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

ROOT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'svg.fonttype': 'none', 'axes.spines.top': False,
                     'axes.spines.right': False})
BLUE, ORANGE, INK, GRAY = '#2563a6', '#c46516', '#172b3a', '#dce2e8'

def save(fig, stem):
    fig.savefig(ROOT / f'{stem}.svg', facecolor='white')
    fig.savefig(ROOT / f'{stem}.png', dpi=160, facecolor='white')
    plt.close(fig)
    im = Image.open(ROOT / f'{stem}.png').convert('RGB')
    im.resize((720, round(im.height * 720 / im.width)), Image.Resampling.LANCZOS).save(ROOT / f'{stem}_720.png')

a = np.array([.50, .25, .15, .10])
selected = [0, 2]
mass = a[selected].sum()
top2 = np.sort(a)[-2:].sum()
assert np.isclose(a.sum(), 1)
assert np.isclose(mass, .65)
assert np.isclose(top2, .75)

fig, ax = plt.subplots(figsize=(9, 3.8))
fig.subplots_adjust(left=.09, right=.965, bottom=.25, top=.78)
fig.text(.09, .92, 'P1  Attention mass: one complete distribution', fontsize=16, color=INK, weight='bold')
fig.text(.09, .83, 'Fixed target layer, query and head; S = {0, 2}', color=INK)
left = 0
for i, w in enumerate(a):
    chosen = i in selected
    ax.add_patch(Rectangle((left, .24), w, .42, facecolor=BLUE if chosen else GRAY, edgecolor='white', linewidth=2))
    ax.text(left+w/2, .45, f'{w:.2f}', ha='center', va='center', color='white' if chosen else INK, fontsize=14, weight='bold')
    ax.text(left+w/2, .77, f'token {i}', ha='center', color=INK, fontsize=11)
    if chosen:
        ax.text(left+w/2, .08, 'in S', ha='center', color=BLUE, fontsize=11, weight='bold')
    left += w
ax.set_xlim(0, 1)
ax.set_ylim(0, .96)
ax.set_yticks([])
ax.set_xticks(np.arange(0, 1.01, .25))
ax.set_xlabel('Cumulative weight (total = 1)', labelpad=6)
ax.spines['left'].set_visible(False)
fig.text(.09, .045, 'Blue segments: 0.50 + 0.15 = 0.65 = 65% of all attention', color=BLUE, fontsize=13, weight='bold')
save(fig, 'attention_mass')

A = np.array([[1, 1], [0, 1]])
x = np.array([1, 2])
e1, e2 = np.eye(2, dtype=int).T
y = A @ x
assert np.array_equal(y, [3, 2])
assert np.array_equal(A @ e1, [1, 0])
assert np.array_equal(A @ e2, [1, 1])
assert np.array_equal(A @ x, A @ e1 + 2*(A @ e2))

fig, axs = plt.subplots(1, 2, figsize=(10, 5.3))
fig.subplots_adjust(left=.055, right=.98, bottom=.16, top=.77, wspace=.15)
fig.text(.055, .94, 'Linear map: move the basis, keep the coefficients', fontsize=17, weight='bold', color=INK)
fig.text(.055, .86, 'A = [[1, 1], [0, 1]]     x = (1, 2)     Ax = (3, 2)', fontsize=13, color=INK)

def arrow(ax, start, end, color, lw=2.5, style='-'):
    ax.annotate('', xy=end, xytext=start,
                arrowprops={'arrowstyle': '-|>', 'color': color, 'lw': lw,
                            'linestyle': style, 'mutation_scale': 15})

for ax in axs:
    ax.set_xlim(-.45, 3.65)
    ax.set_ylim(-.45, 2.8)
    ax.set_aspect('equal')
    ax.set_xticks([0,1,2,3]); ax.set_yticks([0,1,2])
    ax.grid(color='#edf0f2', lw=.8)
    ax.axhline(0, color='#b5bec7', lw=1)
    ax.axvline(0, color='#b5bec7', lw=1)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.tick_params(length=0, colors='#566675')
    ax.set_xlabel('coordinate 1')
axs[0].set_ylabel('coordinate 2')

ax = axs[0]
ax.set_title(r'P1  $x=1e_1+2e_2$', loc='left', fontsize=14, pad=15)
arrow(ax, (0,0), x, INK, 2)
arrow(ax, (0,0), e1, BLUE)
arrow(ax, (0,0), e2, ORANGE)
arrow(ax, (1,0), (1,1), ORANGE, 2, '--')
arrow(ax, (1,1), x, ORANGE, 2, '--')
ax.text(.53, -.27, r'$e_1$', color=BLUE, fontsize=14)
ax.text(-.35, .52, r'$e_2$', color=ORANGE, fontsize=14)
ax.text(1.14, .45, r'$+e_2$', color=ORANGE, fontsize=12)
ax.text(1.14, 1.45, r'$+e_2$', color=ORANGE, fontsize=12)
ax.scatter(*x, color=INK, s=22, zorder=5)
ax.text(.66, 2.15, r'$x=(1,2)$', color=INK, fontsize=13)

ax = axs[1]
ax.set_title(r'P2  $Ax=1(Ae_1)+2(Ae_2)$', loc='left', fontsize=14, pad=15)
arrow(ax, (0,0), y, INK, 2)
arrow(ax, (0,0), A@e1, BLUE)
arrow(ax, (0,0), A@e2, ORANGE)
arrow(ax, (1,0), (2,1), ORANGE, 2, '--')
arrow(ax, (2,1), y, ORANGE, 2, '--')
ax.text(.40, -.27, r'$Ae_1$', color=BLUE, fontsize=14)
ax.text(.04, .91, r'$Ae_2$', color=ORANGE, fontsize=14)
ax.text(1.65, .22, r'$+Ae_2$', color=ORANGE, fontsize=12)
ax.text(2.66, 1.20, r'$+Ae_2$', color=ORANGE, fontsize=12)
ax.scatter(*y, color=INK, s=22, zorder=5)
ax.text(2.34, 2.17, r'$Ax=(3,2)$', color=INK, fontsize=13)
fig.text(.055, .065, 'Blue: first basis vector   Orange: second basis vector   Dark: result', fontsize=12, color=INK)
fig.text(.055, .018, 'Dashed arrows: translated copies for vector addition. Both panels use equal scales.', fontsize=11, color='#526576')
save(fig, 'linear_map')

checks = {
    'type': 'deterministic teaching arithmetic, not model measurements',
    'attention_weights': a.tolist(), 'selected_indices': selected,
    'full_sum': float(a.sum()), 'selected_mass': float(mass),
    'top2_mass': float(top2), 'selected_over_top2': float(mass/top2),
    'A': A.tolist(), 'x': x.tolist(), 'Ae1': (A@e1).tolist(),
    'Ae2': (A@e2).tolist(), 'Ax': y.tolist(),
    'python': platform.python_version(), 'numpy': np.__version__,
    'matplotlib': matplotlib.__version__,
    'input_sha256': hashlib.sha256((ROOT.parent/'prompts.md').read_bytes()).hexdigest(),
    'assertions': 'all passed', 'independent_validation': 'not performed by producer',
    'external_sources': [], 'knowledge_refs': []
}
(ROOT/'arithmetic_checks.json').write_text(json.dumps(checks, indent=2, ensure_ascii=False)+'\n')
print(json.dumps(checks, indent=2, ensure_ascii=False))
