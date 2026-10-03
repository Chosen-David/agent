"""Reproduce supplied timing values without aggregation or statistical analysis."""
from pathlib import Path
import os
import csv
import hashlib
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(HERE / '.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'measurements_snapshot.csv'
SNAPSHOT = HERE / 'measurements_snapshot.csv'
if SOURCE.resolve() != SNAPSHOT.resolve():
    shutil.copyfile(SOURCE, SNAPSHOT)
with SNAPSHOT.open(newline='') as file:
    rows = list(csv.DictReader(file))
required = ['workload', 'baseline_ms', 'candidate_ms', 'scope']
assert list(rows[0]) == required
assert all(all(row[k] != '' for k in required) for row in rows)
assert len({(r['scope'], r['workload']) for r in rows}) == len(rows)
assert set(r['scope'] for r in rows) == {'end_to_end', 'kernel_only'}
assert all(float(r[k]) >= 0 for r in rows for k in ['baseline_ms', 'candidate_ms'])

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9,
    'axes.labelsize': 9, 'xtick.labelsize': 8, 'ytick.labelsize': 9,
    'svg.fonttype': 'none', 'axes.edgecolor': '#a7afb6',
    'axes.linewidth': .6, 'text.color': '#202b35',
    'axes.labelcolor': '#202b35', 'xtick.color': '#56616b',
    'ytick.color': '#202b35', 'savefig.facecolor': 'white',
})
fig = plt.figure(figsize=(180/25.4, 100/25.4))
grid = fig.add_gridspec(2, 1, height_ratios=[3, 1.15],
                        left=.16, right=.95, bottom=.16, top=.84, hspace=.66)
axes = [fig.add_subplot(grid[i]) for i in range(2)]
series = [('baseline_ms', 'Baseline', '#255c85', 'o', -.13),
          ('candidate_ms', 'Candidate', '#c66523', 'D', .13)]
plotted = []
for ax, scope, title in zip(axes, ['end_to_end', 'kernel_only'],
                           ['a  End-to-end timing', 'b  Kernel-only timing']):
    group = [r for r in rows if r['scope'] == scope]
    y = np.arange(len(group))
    ax.set_title(title, loc='left', fontsize=10, fontweight='bold', pad=9)
    for field, name, color, marker, offset in series:
        values = np.array([float(r[field]) for r in group])
        points = ax.scatter(values, y + offset, s=34, color=color,
                            marker=marker, label=name, zorder=3,
                            edgecolors='white', linewidths=.45)
        actual = points.get_offsets()
        assert np.array_equal(actual[:, 0], values)
        for index, (value, row) in enumerate(zip(values, group)):
            ax.text(value + 5, index + offset, f'{value:g}', va='center',
                    ha='left', fontsize=8, color=color)
            plotted.append({'scope': scope, 'workload': row['workload'],
                            'series': name, 'value_ms': float(actual[index, 0])})
    ax.set_yticks(y, [r['workload'] for r in group])
    ax.set_ylim(len(group)-.55, -.55)
    ax.set_xlim(0, 250)
    ax.set_xticks(np.arange(0, 251, 50))
    ax.grid(axis='x', color='#e2e6e9', linewidth=.6, zorder=0)
    ax.tick_params(axis='y', length=0, pad=9)
    ax.tick_params(axis='x', length=3)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
axes[1].set_xlabel('Elapsed time (ms)', labelpad=7)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(.95, .985),
           ncol=2, frameon=False, handletextpad=.35, columnspacing=1.7)

fig.savefig(HERE / 'timing.svg')
fig.savefig(HERE / 'timing.png', dpi=300)
fig.savefig(HERE / 'timing_final_size.png', dpi=120)
plt.close(fig)
with Image.open(HERE / 'timing_final_size.png') as preview:
    preview.convert('L').save(HERE / 'timing_grayscale.png')
    page = Image.new('RGB', (round(210/25.4*120), round(297/25.4*120)), 'white')
    page.paste(preview.convert('RGB'), ((page.width-preview.width)//2, round(28/25.4*120)))
    page.save(HERE / 'timing_page_preview.png')

with (HERE / 'plotted_values.csv').open('w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['scope', 'workload', 'series', 'value_ms'])
    writer.writeheader()
    writer.writerows(plotted)
expected = {(r['scope'], r['workload'], name): float(r[field])
            for r in rows for field, name, *_ in series}
observed = {(r['scope'], r['workload'], r['series']): r['value_ms'] for r in plotted}
assert expected == observed
assert len(plotted) == 2*len(rows) == 8
qa = {
    'input_sha256': hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
    'input_rows': len(rows), 'plotted_points': len(plotted),
    'missing_values': 0, 'duplicate_scope_workload_keys': 0,
    'exact_plotted_value_match': expected == observed,
    'transforms': ['Numeric parsing; categorical placement; no aggregation or normalization'],
    'axes': {'both_panels': 'linear, 0 to 250 ms'},
    'physical_dimensions_mm': [180, 100], 'png_dpi': 300,
    'versions': {'python': sys.version.split()[0], 'matplotlib': matplotlib.__version__,
                 'numpy': np.__version__, 'Pillow': Image.__version__},
}
(HERE / 'numerical_qa.json').write_text(json.dumps(qa, indent=2) + '\n')
print(json.dumps(qa, indent=2))
