from pathlib import Path
import csv, json, hashlib, sys, os, math
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(OUT / '.mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sources = {n: hashlib.sha256((ROOT/'inputs'/n).read_bytes()).hexdigest() for n in ['project.json','measurements.csv','concept.txt']}
rows = list(csv.DictReader((ROOT/'inputs/measurements.csv').open()))
assert len(rows)==4 and len({r['workload'] for r in rows})==4
for r in rows:
    for k in ['baseline_ms','candidate_ms']:
        r[k]=float(r[k]); assert math.isfinite(r[k]) and r[k]>0
    assert r['scope'] in ['end_to_end','kernel_only']
    r['latency_change_pct']=(r['candidate_ms']/r['baseline_ms']-1)*100
    r['latency_reduction_pct']=-r['latency_change_pct']
    r['speedup']=r['baseline_ms']/r['candidate_ms']
with (OUT/'derived_metrics.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader();w.writerows(rows)
plt.rcParams.update({'font.size':11,'svg.fonttype':'none','pdf.fonttype':42})
fig,axs=plt.subplots(1,2,figsize=(10,4.4),gridspec_kw={'width_ratios':[3,1]},layout='constrained')
for ax,scope,title in zip(axs,['end_to_end','kernel_only'],['A  End-to-end workloads','B  Kernel only']):
    part=[r for r in rows if r['scope']==scope]
    for x,r in enumerate(part):
        for dx,key,color,label in [(-.18,'baseline_ms','#637686','Baseline'),(.18,'candidate_ms','#d98636','Candidate')]:
            v=r[key]; ax.bar(x+dx,v,.34,color=color,label=label if x==0 else None)
            ax.text(x+dx,v+4,f'{v:g}',ha='center',va='bottom',fontsize=10)
    ax.set_title(title,loc='left',fontsize=12,pad=12)
    ax.set_xticks(range(len(part)),[r['workload'] for r in part]);ax.set_ylim(0,255)
    ax.set_ylabel('Reported latency (ms)');ax.spines[['top','right']].set_visible(False)
    ax.set_axisbelow(True);ax.grid(axis='y',alpha=.2);ax.legend(frameon=False,fontsize=9,loc='upper left')
fig.suptitle('Available measurements · v2',fontsize=15)
fig.supxlabel('Separate scopes; repeat counts and uncertainty are not supplied.',fontsize=10)
for fmt in ['png','svg','pdf']: fig.savefig(OUT/f'figure_v2.{fmt}',dpi=180)
plt.close(fig)
manifest={'run_id':'run-v2-20261003','date':'2026-10-03','source_versions':{'measurements.csv':'v2 (project declaration)','concept.txt':'v1 (project state; no prior snapshot for comparison)','project.json':'provided snapshot'},'source_sha256':sources,'runtime':{'python':sys.version,'matplotlib':matplotlib.__version__},'checks':{'rows':len(rows),'positive_finite_latencies':True,'unique_workload_labels':True,'allowed_scopes':True},'new_experiments':0,'excluded_rows':0,'aggregation':'none','uncertainty':'not available; no fabricated intervals'}
(OUT/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'metrics':rows,'sources':sources,'python':sys.version.split()[0],'matplotlib':matplotlib.__version__},indent=2))
