"""Recompute the supplied v2 snapshot; never executes a benchmark."""
from pathlib import Path
import csv, hashlib, json, math, os, platform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
os.environ['MPLCONFIGDIR'] = str(HERE / '.mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

raw = list(csv.DictReader((ROOT / 'inputs/measurements.csv').open()))
assert raw and len({r['workload'] for r in raw}) == len(raw)
rows = []
for line, r in enumerate(raw, 2):
    b, c = float(r['baseline_ms']), float(r['candidate_ms'])
    assert all(math.isfinite(x) and x > 0 for x in (b, c))
    assert r['scope'] in {'end_to_end', 'kernel_only'}
    rows.append(dict(workload=r['workload'], scope=r['scope'], baseline_ms=b,
                     candidate_ms=c, speedup=b/c, latency_change_pct=100*(c/b-1),
                     latency_saved_ms=b-c, source_csv_line=line))
with (HERE/'metrics.csv').open('w') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

plt.rcParams.update({'font.size': 10, 'svg.fonttype': 'none', 'pdf.fonttype': 42})
fig, axes = plt.subplots(1, 2, figsize=(8, 3.5), gridspec_kw={'width_ratios': [3, 1]})
for ax, scope, title in zip(axes, ['end_to_end', 'kernel_only'],
                          ['(a) End-to-end', '(b) Kernel only']):
    group = [r for r in rows if r['scope']==scope]
    x = list(range(len(group)))
    for offset, key, color, label in [(-.18,'baseline_ms','#465b73','Baseline'),
                                      (.18,'candidate_ms','#d17b38','Candidate')]:
        bars=ax.bar([i+offset for i in x], [r[key] for r in group], .34,
                    color=color,label=label)
        ax.bar_label(bars, fmt='%.0f', padding=3, fontsize=9)
    ax.set_xticks(x,[r['workload'] for r in group])
    ax.set_ylim(0,max(r['baseline_ms'] for r in rows)*1.30)
    ax.set_title(title,loc='left',fontsize=11)
    ax.set_ylabel('Reported latency (ms)')
    ax.spines[['top','right']].set_visible(False)
    ax.set_axisbelow(True); ax.grid(axis='y',alpha=.18)
axes[0].legend(frameon=False,loc='upper left')
fig.text(.5,.025,'Supplied v2 values; repetition counts and uncertainty unavailable.',
         ha='center',fontsize=9)
fig.tight_layout(rect=(0,.07,1,1))
for ext in ['png','svg','pdf']:
    fig.savefig(HERE/f'figure_v2.{ext}',dpi=200)
plt.close(fig)

manifest = {'run_id': HERE.name, 'input_versions': {
    'measurements.csv': 'v2 (project.json declaration)',
    'concept.txt': 'v1 (project.json declaration; no old snapshot comparison possible)',
    'project.json': 'supplied unversioned snapshot'},
    'inputs': {p.name: {'path': str(p), 'sha256': sha(p)}
               for p in sorted((ROOT/'inputs').iterdir()) if p.is_file()},
    'runtime': {'python': platform.python_version(), 'matplotlib':matplotlib.__version__},
    'checks': {'rows':len(rows),'positive_finite_times':True,'unique_workload_labels':True,
               'known_scopes':True,'scope_aggregation':False,'new_experiments':False},
    'outputs': {p.name:sha(p) for p in sorted(HERE.iterdir())
                if p.is_file() and p.suffix in {'.csv','.png','.svg','.pdf','.py'}}}
(HERE/'analysis_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'rows': rows, 'runtime': manifest['runtime']},indent=2))
