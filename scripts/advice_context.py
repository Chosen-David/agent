import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.advice_context import advice_view
from agent_runtime.context_serialization import render_context
def main():
    p=argparse.ArgumentParser(description='Read-only exact-version advice topics; not a human GUIDE reader.')
    p.add_argument('--root',required=True);p.add_argument('--path',required=True);p.add_argument('--heading',action='append',required=True)
    p.add_argument('--sha256',required=True);p.add_argument('--max-chars',type=int,default=20000)
    p.add_argument('--compact',action='store_true',help='preserve exact payload, omit JSON whitespace')
    a=p.parse_args();print(render_context(advice_view(a.root,a.path,a.heading,a.sha256,max_chars=a.max_chars),compact=a.compact))
if __name__=='__main__':main()
