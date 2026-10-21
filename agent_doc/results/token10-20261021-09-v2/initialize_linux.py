"""WSL real installer and readonly fixture inventory, no model execution."""
import hashlib,importlib.util,json,os,platform,sqlite3,sys,tempfile,zipfile
from pathlib import Path
out=Path(__file__).resolve().parent
def inventory(root):
 files={};links={}
 for p in sorted(root.rglob('*')):
  if p.is_symlink():links[p.relative_to(root).as_posix()]={'target':str(p.resolve()),'link':os.readlink(p)}
  elif p.is_file():files[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 return {'files':files,'symlinks':links}
if '--inspect' in sys.argv:
 info=json.loads((out/'linux-fixture.json').read_bytes());print(json.dumps(inventory(Path(info['project']))));sys.exit()
base=Path(tempfile.mkdtemp(prefix='token10-role09-'));source=base/'source';source.mkdir();project=base/'project';project.mkdir()
z=zipfile.ZipFile(out/'source.zip');z.extractall(source)
expected=json.loads((out/'source-files.json').read_bytes())
assert all(hashlib.sha256((source/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in expected)
sys.path.insert(0,str(source));sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('token09_setup',source/'setup.py');setup=importlib.util.module_from_spec(spec);spec.loader.exec_module(setup)
setup.install(project);assert not setup.check(project)['errors']
info={'source':str(source),'project':str(project),'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version,'source_sha256':{r['path']:r['sha256'] for r in expected},'fixture':inventory(project)}
(out/'linux-fixture.json').write_bytes((json.dumps(info,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode())
with zipfile.ZipFile(out/'fixture.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for p in sorted(project.rglob('*')):
  if p.is_file() and not p.is_symlink():archive.write(p,p.relative_to(project).as_posix())
print(json.dumps({'installed':True,'symlinks':len(info['fixture']['symlinks']),'files':len(info['fixture']['files'])}))
