import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.log_context import log_view
from agent_runtime.context_serialization import render_context
def main():
    p=argparse.ArgumentParser(description='Read-only exact-version log excerpts; no clearance inference.')
    p.add_argument('--root',required=True);p.add_argument('--path',required=True);p.add_argument('--sha256',required=True)
    p.add_argument('--needle',action='append',default=[])
    p.add_argument('--compact',action='store_true',help='preserve exact payload, omit JSON whitespace')
    p.add_argument('--encoding',choices=['lines','chunks'],default='lines',help='lossless selected-line transport')
    for name,default in (('head',2),('tail',2),('context',1),('max-chars',20000)):
        p.add_argument('--'+name,type=int,default=default)
    a=p.parse_args()
    print(render_context(log_view(a.root,a.path,a.sha256,needles=a.needle,head=a.head,tail=a.tail,context=a.context,max_chars=a.max_chars,encoding=a.encoding),compact=a.compact))
if __name__=='__main__':main()
