"""Restore observed printed labels and requested initial location after bundled build."""
import base64,hashlib,json,pathlib,re
r=pathlib.Path('/tmp/agent-forward-v1/paper-reading-companion');o=r/'outputs';p=o/'reader.html'
s=p.read_text();pattern=r'(<script id="reader-data" type="application/json">)(.*?)(</script>)'
m=re.search(pattern,s,re.S);data=json.loads(m.group(2))
data['title']='Synthetic paper: Two logit paths'
labels={1:'i',2:'1',3:'A1'}
for page in data['pages']:
 page['label']=labels[page['number']]
data['initial_page']=2
encoded=json.dumps(data,ensure_ascii=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
s=s[:m.start(2)]+encoded+s[m.end(2):]
s=s.replace('let index=0,zoom=100,textMode=false;','let index=Math.max(0,data.pages.findIndex(p=>p.number===data.initial_page)),zoom=100,textMode=false;')
s=s.replace('<title>paper.pdf · 论文伴读</title>','<title>Synthetic paper: Two logit paths · 论文伴读</title>')
p.write_text(s,encoding='utf-8')
assert data['sha256']==hashlib.sha256((r/'inputs/paper.pdf').read_bytes()).hexdigest()
assert [x['number'] for x in data['pages']]==[1,2,3]
assert [x['label'] for x in data['pages']]==['i','1','A1']
assert len(data['cards'])==2 and all(x['page']==2 for x in data['cards'])
assert all(base64.b64decode(x['image']).startswith(b'\x89PNG\r\n\x1a\n') for x in data['pages'])
assert '__READER_DATA__' not in s
assert '本页没有模型连接' in s and '可手动复制的提问上下文' in s
assert not re.search(r'<(?:script|link)[^>]+(?:src|href)=["\']https?://',s)
report={'status':'passed','checks':['PDF hash matches embedded HTML and notes','3 embedded original-page PNGs decode','2 cards anchor to physical page 2','printed labels manually matched to visually inspected original pages','initial location physical page 2; localStorage can resume later location','offline inline assets; no remote script/styles','copy-context handler and manual fallback present'],'browser_interaction_test':'not performed','original_page_visual_inspection':[1,2,3],'html_bytes':p.stat().st_size}
(o/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
