"""Independent synthetic boundary/provenance review; no CUDA execution."""
import hashlib, importlib.util, json, pathlib, platform, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[4]
OUT=pathlib.Path(__file__).resolve().parent
SCRIPT=ROOT/'plugins/research-assistant/skills/research-implement-optimize/scripts/compiler_feedback.py'
spec=importlib.util.spec_from_file_location('reviewed',SCRIPT)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
header="ptxas info : Compiling entry function 'a' for 'sm_90'\nptxas info : Function properties for a\n"
stack='    0 bytes stack frame, 0 bytes spill stores, 0 bytes spill loads\n'
cases={
'normal': (header+stack+'ptxas info : Used 64 registers, 12 bytes smem\n', {'registers_per_thread':64,'static_shared_bytes':12}),
'negative_smem': (header+stack+'ptxas info : Used 64 registers, -12 bytes smem\n', {'static_shared_bytes':None}),
'fraction_smem': (header+stack+'ptxas info : Used 64 registers, 1.5 bytes smem\n', {'static_shared_bytes':None}),
'comma_smem': (header+stack+'ptxas info : Used 64 registers, 1,024 bytes smem\n', {'static_shared_bytes':None}),
'negative_spill': (header+'    0 bytes stack frame, -16 bytes spill stores, 0 bytes spill loads\nptxas info : Used 64 registers, 12 bytes smem\n', {'spill_store_bytes':None}),
'truncated_new_header': (header+stack+'ptxas info : Compiling entry funct\nptxas info : Used 80 registers\n', {'registers_per_thread':None}),
'whitespace_new_header': (header+stack+"ptxas info : Compiling  entry function 'b' for 'sm_90'\nptxas info : Used 80 registers\n", {'registers_per_thread':None}),
'known_unknown_boundary':(header+stack+'ptxas info : Compiling entry function "b"\nptxas info : Used 80 registers\n',{'registers_per_thread':None}),
'warning_not_success':(header+stack+'ptxas info : Used 64 registers, 12 bytes smem\nptxas warning : ignored option\n',{'registers_per_thread':64}),
}
results=[]
for name,(content,expected) in cases.items():
    raw=content.encode(); source=OUT/(name+'.log'); source.write_bytes(raw)
    actual=m.parse_log(raw); (OUT/(name+'.json')).write_text(json.dumps(actual,indent=2)+'\n')
    mismatch={k:{'expected':v,'actual':actual['records'][0]['metrics'][k]} for k,v in expected.items() if actual['records'][0]['metrics'][k]!=v}
    results.append({'case':name,'mismatches':mismatch,'passed':not mismatch,'sha_matches':actual['log_sha256']==hashlib.sha256(raw).hexdigest(),'parse_status':actual['parse_status']})
for count in [1000,4000]:
    raw=(header+'ptxas info : Used 64 registers\n'*count).encode()
    before=time.monotonic(); actual=m.parse_log(raw); elapsed=time.monotonic()-before
    results.append({'case':'repeat_scaling','lines':count,'input_bytes':len(raw),'elapsed_seconds':elapsed,'observations':len(actual['records'][0]['observations'])})
# CLI as an independent consumer, with a cwd outside the package and only stdlib.
cli=subprocess.run([sys.executable,str(SCRIPT),str(OUT/'normal.log')],cwd=OUT,capture_output=True,text=True,timeout=10)
results.append({'case':'standalone_cli','returncode':cli.returncode,'stderr':cli.stderr,'equals_api':json.loads(cli.stdout)==m.parse_log((OUT/'normal.log').read_bytes())})
# Package-local file closure is independently checked, not assumed from sync status.
mirror=ROOT/'plugins/research-assistant/skills/research-assistant/scripts/compiler_feedback.py'
results.append({'case':'script_mirror','byte_equal':SCRIPT.read_bytes()==mirror.read_bytes()})
report={'python':platform.python_version(),'script_sha256':hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),'cases':results}
(OUT/'adversarial-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
