import hashlib,itertools,json,sys,tempfile
from pathlib import Path
from difflib import SequenceMatcher
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime import artifact_context as c
wire=lambda obj:json.dumps(obj,ensure_ascii=False,allow_nan=False,separators=(',',':'))
hashtext=lambda text:hashlib.sha256(text.encode()).hexdigest()
texts=[''.join(p) for n in range(3) for p in itertools.product(('a\n','甲\r\n','"\\'),repeat=n)]
checks=0
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder).resolve()
 for old,new in itertools.product(texts,repeat=2):
  refs=[]
  for name,text in (('old',old),('new',new)):
   (root/name).write_bytes(text.encode());refs.append(dict(path=name,sha256=hashtext(text)))
  a,b=refs;ol=old.splitlines(keepends=True);nl=new.splitlines(keepends=True)
  start=0
  while start<min(len(ol),len(nl)) and ol[start]==nl[start]:start+=1
  end=0
  while end<min(len(ol),len(nl))-start and ol[-end-1]==nl[-end-1]:end+=1
  sp=dict(base_sha256=a['sha256'],start=start,delete=len(ol)-start-end,insert=''.join(nl[start:len(nl)-end if end else len(nl)]))
  ed=[dict(start=i,delete=j-i,insert=''.join(nl[k:l])) for tag,i,j,k,l in SequenceMatcher(None,ol,nl,autojunk=False).get_opcodes() if tag!='equal']
  for full,multi,reuse in itertools.product((False,True),repeat=3):
   candidates=[dict(ref=b,representation='full',text=new)]
   if not full:
    candidates.append(dict(ref=b,representation='splice',splice=sp))
    if multi and 1<=len(ed)<=64:candidates.append(dict(ref=b,representation='edits',patch=dict(base_sha256=a['sha256'],edits=ed)))
    if reuse and old==new:candidates.append(dict(ref=b,representation='identical'))
   for counter in (None,lambda s:0 if '"representation":"edits"' in s else 1):
    packets=[dict(schema_version=c.SCHEMA,project_root=str(root),position_unit='lines with terminators',before=dict(ref=a,text=old),after=t) for t in candidates]
    expected=min(packets,key=(lambda p:len(wire(p))) if counter is None or full else lambda p:counter(wire(p)))
    actual=c.compare_artifacts(root,a,b,full=full,multi_edit=multi,reuse_identical=reuse,token_counter=counter,max_chars=10000)
    assert actual==expected,(old,new,full,multi,reuse,counter)
    assert c.restore_comparison(root,actual,a,b)==(old,new)
    checks+=1
 # Exact lower-bound equality must skip; custom counting must restore eligibility.
 b=dict(path='new',sha256='0'*64)
 bound=dict(ref=b,representation='edits',patch=dict(base_sha256='0'*64,edits=[dict(start=0,delete=0,insert='')]))
 n=len(wire(bound))-len(wire(dict(ref=b,representation='full',text='')))
 old='x'*n;new='y'*n
 refs=[]
 for name,text in (('old',old),('new',new)):
  (root/name).write_text(text);refs.append(dict(path=name,sha256=hashtext(text)))
 with patch.object(c,'_edits',side_effect=AssertionError('equal-bound called matcher')):
  actual=c.compare_artifacts(root,*refs,multi_edit=True)
 assert actual['after']['representation']=='full'
 with patch.object(c,'_edits',wraps=c._edits) as matcher:
  actual=c.compare_artifacts(root,*refs,multi_edit=True,token_counter=lambda s:0 if '"representation":"edits"' in s else 1)
  assert matcher.call_count==1 and actual['after']['representation']=='edits'
print(json.dumps(dict(oracle_checks=checks,distinct_pairs=len(texts)**2,exact_lower_bound_tie_pass=True,custom_counter_exclusion_pass=True,source_sha256=hashlib.sha256((ROOT/'agent_runtime/artifact_context.py').read_bytes()).hexdigest()),indent=2))
