"""Reproduce FIG-20261003-01 from the original CSV; no aggregation or inference."""
from pathlib import Path
import os
import csv
import hashlib
import json
import platform

OUT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(OUT / '.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

INPUT = OUT.parents[1] / 'inputs' / 'measurements.csv'
with INPUT.open(newline='') as f:
    rows = list(csv.DictReader(f))
assert rows and all(set(r) == {'workload', 'baseline_ms', 'candidate_ms', 'scope'} for r in rows)
assert len({(r['scope'], r['workload']) for r in rows}) == len(rows)
for r in rows:
    assert all(r.values()), 'Missing value is not zero'
    for key in ['baseline_ms', 'candidate_ms']:
        r[key] = float(r[key])
        assert r[key] > 0
    assert r['scope'] in ['end_to_end', 'kernel_only']
    r['latency_change_pct'] = 100 * (r['candidate_ms'] / r['baseline_ms'] - 1)
    r['speedup'] = r['baseline_ms'] / r['candidate_ms']
with (OUT / 'derived_values.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

# Style is separate from the data transformations above.
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'axes.titlesize': 10, 'axes.labelsize': 9,
                     'svg.fonttype': 'none', 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': .6,
                     'xtick.major.size': 0, 'ytick.major.size': 3,
                     'savefig.facecolor': 'white'})
colors = ['#596778', '#007F91']
fig, axes = plt.subplots(1, 2, figsize=(180/25.4, 85/25.4),
                         gridspec_kw={'width_ratios': [3, 1.3]})
fig.subplots_adjust(left=.09, right=.98, bottom=.22, top=.73, wspace=.42)
for ax, scope, title, ymax in zip(axes, ['end_to_end','kernel_only'],
    ['(a) end_to_end', '(b) kernel_only'], [320, 32]):
    selected = [r for r in rows if r['scope'] == scope]
    for j, r in enumerate(selected):
        for k, field in enumerate(['baseline_ms','candidate_ms']):
            value = r[field]
            ax.bar(j + (k-.5)*.32, value, width=.29, color=colors[k],
                   edgecolor='#263444', linewidth=.5, hatch='///' if k else None,
                   zorder=3)
            ax.text(j+(k-.5)*.32, value+ymax*.025, f'{value:g}', ha='center', va='bottom', fontsize=9)
        change = r['latency_change_pct']
        label = f'{abs(change):.1f}'.rstrip('0').rstrip('.') + '% ' + ('higher' if change>0 else 'lower') + '\nlatency'
        ax.text(j, ymax*.96, label, ha='center', va='top', fontsize=8.5,
                color='#9B321D' if change>0 else '#243344',
                weight='bold' if change>0 else 'normal')
    ax.set_xticks(range(len(selected)), [r['workload'] for r in selected])
    ax.set_xlim(-.6, len(selected)-.4)
    ax.set_ylim(0,ymax)
    ax.set_yticks([0,50,100,150,200,250,300] if scope=='end_to_end' else [0,5,10,15,20,25,30])
    ax.set_ylabel('Latency (ms)')
    ax.set_title(title, loc='left', pad=11, weight='bold')
    ax.grid(axis='y', color='#E3E7EB', lw=.6, zorder=0)
fig.legend(handles=[Patch(facecolor=colors[0], edgecolor='#263444', label='Baseline'),
                    Patch(facecolor=colors[1], edgecolor='#263444', hatch='///', label='Candidate')],
           loc='upper center', bbox_to_anchor=(.52,.965), ncol=2, frameon=False)
fig.text(.09,.09,'Separate timing scopes; y-axis scales differ. Lower latency is better.', fontsize=8)
fig.text(.09,.035,'Reported values only; repetitions and uncertainty were not provided.', fontsize=8, color='#4D535B')
fig.savefig(OUT / 'results.svg')
fig.savefig(OUT / 'results.png', dpi=300)
fig.savefig(OUT / 'results_size_preview.png', dpi=120)
metadata = {'figure_id':'FIG-20261003-01', 'input':str(INPUT),
            'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
            'python':platform.python_version(), 'matplotlib':matplotlib.__version__,
            'size_mm':[180,85], 'png_dpi':300, 'source_rows':len(rows),
            'missing_values':0, 'aggregate_or_exclude':False,
            'replication':'Unknown; one reported value per method/workload/scope, not an n=1 experiment claim'}
(OUT/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata, indent=2))
print('Wrote SVG, PNG, physical-size preview, and derived values.')
