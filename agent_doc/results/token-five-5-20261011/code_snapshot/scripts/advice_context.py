import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.advice_context import advice_view
def main():
    p=argparse.ArgumentParser(description='Read-only exact-version advice topics; not a human GUIDE reader.')
    p.add_argument('--root',required=True);p.add_argument('--path',required=True);p.add_argument('--heading',action='append',required=True)
    p.add_argument('--sha256',required=True);p.add_argument('--max-chars',type=int,default=20000)
    a=p.parse_args();print(json.dumps(advice_view(a.root,a.path,a.heading,a.sha256,max_chars=a.max_chars),ensure_ascii=False))
if __name__=='__main__':main()
