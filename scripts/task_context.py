"""Read-only, explicit per-project TASK view."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.task_context import task_view
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True);p.add_argument('--task-id',action='append',required=True)
    p.add_argument('--sha256',required=True);p.add_argument('--max-chars',type=int,default=20000)
    a=p.parse_args()
    print(json.dumps(task_view(a.root,a.task_id,a.sha256,max_chars=a.max_chars),ensure_ascii=False))
if __name__=='__main__':main()
