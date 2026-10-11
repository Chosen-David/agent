"""Read-only, explicit per-project TASK view."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.task_context import task_view
from agent_runtime.context_serialization import render_context
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True);p.add_argument('--task-id',action='append',required=True)
    p.add_argument('--sha256',required=True);p.add_argument('--max-chars',type=int,default=20000)
    p.add_argument('--compact',action='store_true',help='omit JSON whitespace only; preserve every field')
    a=p.parse_args()
    print(render_context(task_view(a.root,a.task_id,a.sha256,max_chars=a.max_chars),compact=a.compact))
if __name__=='__main__':main()
