from pathlib import Path
import json, hashlib, subprocess, xml.etree.ElementTree as ET
from PIL import Image
BASE=Path(__file__).resolve().parent
SRC=BASE.parent/'inputs/architecture.json'
spec=json.loads(SRC.read_text())
node_style={
'a':(55,175,215,70,'#E8F1FA','#2A6597'),
'b':(55,315,215,70,'#E8F1FA','#2A6597'),
'sum':(355,245,170,70,'#ECF5F2','#397762'),
'softmax':(565,245,220,70,'#ECF5F2','#397762'),
'output':(825,245,200,70,'#EAF0FA','#365D8D'),
'v':(825,405,200,70,'#F5F0E8','#8B6E42')}
edge_paths={('a','sum'):'M 270 210 H 310 V 265 H 355',('b','sum'):'M 270 350 H 310 V 295 H 355',('sum','softmax'):'M 525 280 H 565',('softmax','output'):'M 785 280 H 825',('v','output'):'M 925 405 V 315'}
svg=['''<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="95mm" viewBox="0 0 1080 570" role="img" aria-labelledby="figure-title figure-desc">
<title id="figure-title">Two-path logit combination</title>
<desc id="figure-desc">Proposed schematic, synthetic specification, not implemented. Parallel paths A and B merge into z = a + b, then p = softmax(z). Fixed values V enter only the output y = p^T V.</desc>
<defs><marker id="data-arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto"><path d="M 0 0 L 10 5 L 0 10 Z" fill="#4B5B6A"/></marker></defs>
<rect width="1080" height="570" fill="white"/>
<g font-family="DejaVu Sans, sans-serif" fill="#203244">
<text x="55" y="58" font-size="29" font-weight="600">Two-path logit combination</text>
<text x="55" y="95" font-size="20" fill="#5B6875">PROPOSED SCHEMATIC · Synthetic specification · Not implemented</text>
<text x="55" y="150" font-size="19" fill="#5B6875">Parallel paths</text>''']
for s,t in spec['edges']:
 svg.append(f'<path id="edge-{s}-{t}" data-source="{s}" data-target="{t}" data-kind="data_flow" d="{edge_paths[s,t]}" fill="none" stroke="#4B5B6A" stroke-width="2.4" stroke-linejoin="round" marker-end="url(#data-arrow)"/>')
for n in spec['nodes']:
 x,y,w,h,fill,stroke=node_style[n['id']]
 svg.append(f'<g id="node-{n["id"]}" data-node-id="{n["id"]}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/><text x="{x+w/2}" y="{y+h/2+8}" text-anchor="middle" font-size="24">{n["label"]}</text></g>')
svg.append('''<text x="949" y="367" font-size="18" fill="#6E5B3D">Bypass</text>
<path d="M 55 524 H 106" fill="none" stroke="#4B5B6A" stroke-width="2.4" marker-end="url(#data-arrow)"/>
<text x="119" y="531" font-size="19" fill="#5B6875">Data flow</text>
<text x="1025" y="531" text-anchor="end" font-size="19" fill="#5B6875">No measured performance specified</text>
</g></svg>''')
(BASE/'architecture.svg').write_text('\n'.join(svg))
contract={'figure_id':'FIG-two-path-logits','run_id':'agent-forward-figure-split','status':spec['status'],'evidence_type':spec['evidence_type'],'source':{'path':'../inputs/architecture.json','sha256':hashlib.sha256(SRC.read_bytes()).hexdigest()},'nodes':[dict(n,type='declared computational object',inputs=[s for s,t in spec['edges'] if t==n['id']],outputs=[t for s,t in spec['edges'] if s==n['id']],source=f'/nodes/{i}',shapes_and_units='unspecified') for i,n in enumerate(spec['nodes'])],'edges':[{'id':f'edge-{s}-{t}','source':s,'target':t,'direction':'source_to_target','kind':spec['edge_kind'],'label':None,'evidence':f'/edges/{i}'} for i,(s,t) in enumerate(spec['edges'])],'groups':[],'invariants':spec['constraints'],'label_changes':[],'unknowns':['Tensor dimensions and units','Training/inference behavior','Implementation and empirical performance'],'rendering_only_annotations':['Parallel paths','Bypass','Data flow legend'],'semantic_changes':[]}
(BASE/'semantic_contract.json').write_text(json.dumps(contract,indent=2)+'\n')
root=ET.parse(BASE/'architecture.svg').getroot()
ns={'s':'http://www.w3.org/2000/svg'}
actual_nodes={g.attrib['data-node-id'] for g in root.findall('.//s:g',ns) if 'data-node-id' in g.attrib}
actual_edges={(p.attrib['data-source'],p.attrib['data-target']) for p in root.findall('.//s:path',ns) if 'data-source' in p.attrib}
assert actual_nodes=={n['id'] for n in spec['nodes']}
assert actual_edges=={tuple(e) for e in spec['edges']}
ids=[e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
assert len(ids)==len(set(ids))
assert not root.findall('.//s:image',ns)
for name,dpi in [('architecture.png',300),('final_size.png',96)]:
 subprocess.run(['inkscape',str(BASE/'architecture.svg'),'--export-type=png',f'--export-filename={BASE/name}',f'--export-dpi={dpi}'],check=True)
im=Image.open(BASE/'final_size.png').convert('RGB')
im.convert('L').save(BASE/'grayscale.png')
page=Image.new('RGB',(794,1123),'white'); page.paste(im,((794-im.width)//2,110)); page.save(BASE/'page_preview.png')
check={'xml':'pass','stable_node_ids':sorted(actual_nodes),'edges':sorted([list(e) for e in actual_edges]),'unique_svg_ids':'pass','external_image_resources':'none','png_dimensions':list(Image.open(BASE/'architecture.png').size),'final_size_dimensions':list(im.size),'source_sha256':contract['source']['sha256'],'inkscape_version':subprocess.check_output(['inkscape','--version'],text=True).strip()}
(BASE/'checks.json').write_text(json.dumps(check,indent=2)+'\n')
print(json.dumps(check,indent=2))
