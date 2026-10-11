import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.log_context import log_view
def main():
    p=argparse.ArgumentParser(description='Read-only exact-version log excerpts; no clearance inference.')
    p.add_argument('--root',required=True);p.add_argument('--path',required=True);p.add_argument('--sha256',required=True)
    p.add_argument('--needle',action='append',default=[])
    for name,default in (('head',2),('tail',2),('context',1),('max-chars',20000)):
        p.add_argument('--'+name,type=int,default=default)
    a=p.parse_args()
    print(json.dumps(log_view(a.root,a.path,a.sha256,needles=a.needle,head=a.head,tail=a.tail,context=a.context,max_chars=a.max_chars),ensure_ascii=False))
if __name__=='__main__':main()
