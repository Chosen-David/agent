import os
os.environ['MPLCONFIGDIR']='/tmp/mixed-figure-mpl'
from pathlib import Path
import json, hashlib, platform
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image, ImageOps
import panel_a,panel_b
ROOT=Path(__file__).resolve().parent
INPUT=ROOT.parent/'inputs'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'svg.fonttype':'none','pdf.fonttype':42,'axes.unicode_minus':False})

def save(fig,name):
    fig.savefig(ROOT/(name+'.svg'),facecolor='white')
    fig.savefig(ROOT/(name+'.png'),dpi=220,facecolor='white')
    plt.close(fig)

fig=plt.figure(figsize=(180/25.4,112/25.4))
fig.text(.035,.955,'A',fontsize=11,weight='bold')
fig.text(.08,.955,'Two-path logit combination',fontsize=10,weight='bold')
fig.text(.08,.913,'Proposed schematic · synthetic specification; not implemented',fontsize=8,color='#59636E')
panel_a.draw(fig,(.045,.525,.915,.36),INPUT/'architecture.json')
fig.text(.035,.475,'B',fontsize=11,weight='bold')
fig.text(.08,.475,'Provided timing values',fontsize=10,weight='bold')
handles=[Line2D([],[],marker='s',color='#59636E',ls='',markersize=4,label='Baseline'),Line2D([],[],marker='o',color='#007A94',ls='',markersize=4,label='Candidate')]
fig.legend(handles=handles,loc='upper right',bbox_to_anchor=(.96,.51),frameon=False,ncol=2,fontsize=8,handletextpad=.4,columnspacing=1.3)
panel_b.draw(fig,(.12,.125,.79,.28),INPUT/'measurements.csv')
fig.text(.08,.018,'Timing provenance and repeat counts are unspecified; no uncertainty estimates supplied.',fontsize=7.2,color='#59636E')
save(fig,'figure')
fig=plt.figure(figsize=(180/25.4,48/25.4)); panel_a.draw(fig,(.035,.08,.93,.78),INPUT/'architecture.json'); fig.text(.035,.92,'A  Proposed schematic — synthetic specification; not implemented',fontsize=9); save(fig,'panel_a')
fig=plt.figure(figsize=(180/25.4,54/25.4)); panel_b.draw(fig,(.12,.24,.79,.49),INPUT/'measurements.csv'); fig.text(.04,.92,'B  Provided timing values',fontsize=10,weight='bold'); fig.legend(handles=handles,loc='upper right',frameon=False,ncol=2,fontsize=8); save(fig,'panel_b')
im=Image.open(ROOT/'figure.png').convert('RGB'); ImageOps.grayscale(im).save(ROOT/'figure_gray.png')
# A4 page preview at 110 dpi; 180 mm figure shown without changing its physical size.
page=Image.new('RGB',(round(210/25.4*110),round(297/25.4*110)),'white')
small=im.resize((round(180/25.4*110),round(112/25.4*110)),Image.Resampling.LANCZOS)
page.paste(small,(round(15/25.4*110),round(30/25.4*110))); page.save(ROOT/'page_preview.png')
small.save(ROOT/'final_size_preview.png')
manifest={'run_id':'forward-figure-split','route':'mixed','owner':'single executing agent','execution':'Sequential local fallback workflows; no independent agents or network', 'dimensions_mm':[180,112],'provisional_size':True,'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUT.iterdir()},'versions':{'python':platform.python_version(),'matplotlib':matplotlib.__version__},'panels':[{'id':'A','route':'diagram','owner':'single executing agent','evidence_type':'proposed synthetic specification, not implemented','input':'architecture.json','editable_source':'panel_a.py','status':'ready-for-review'},{'id':'B','route':'data_visualization','owner':'single executing agent','evidence_type':'provided tabulated timings; acquisition provenance unspecified','input':'measurements.csv','editable_source':'panel_b.py','status':'ready-for-review'}],'assembly_source':'compose.py','transforms':'No aggregation, normalization, exclusions, interpolation, or uncertainty estimation. Scope split only.'}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Exact value and graph checks against what the drawing consumes.
import csv,xml.etree.ElementTree as ET
rows=list(csv.DictReader((INPUT/'measurements.csv').open()))
assert len(rows)==4
assert [(r['workload'],float(r['baseline_ms']),float(r['candidate_ms'])) for r in rows]==[('small',100,80),('medium',120,100),('large',200,220),('kernel',20,10)]
svg=ET.parse(ROOT/'figure.svg'); ids=[e.attrib['id'] for e in svg.iter() if 'id' in e.attrib]
assert len(ids)==len(set(ids))
spec=json.loads((INPUT/'architecture.json').read_text())
assert all('node_'+n['id'] in ids for n in spec['nodes'])
assert sorted(i for i in ids if i.startswith('edge_'))==sorted('edge_'+s+'_'+t for s,t in spec['edges'])
assert len(spec['nodes'])==6 and len(spec['edges'])==5
(ROOT/'programmatic_qa.txt').write_text('PASS: all 8 timing values preserved; 4 workloads; scopes separated.\nPASS: 6 nodes and exactly 5 specified directed edges.\nPASS: SVG parses and has unique IDs; editable SVG text enabled.\nNo external images or resource links used.\n')
print(json.dumps(manifest,indent=2))
