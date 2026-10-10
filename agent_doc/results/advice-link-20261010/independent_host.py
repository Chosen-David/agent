"""Fixed independently invoked CPU/source gate; no data-selected code or models."""
import hashlib,io,json,os,platform,subprocess,sys,unittest
from pathlib import Path
REL='agent_doc/results/advice-link-20261010'
EXPECTED={'agent_runtime/advice_poll.py','scripts/advice_poll.py','tests/test_advice_poll.py','tests/test_advice_context_scope.py',
          'agent_runtime/project_docs.py','agent_runtime/task_manifest.py','agent_runtime/result_validation.py','agent_runtime/legacy_result_paths.py'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def cpu(root):
    base=root/REL;sys.path.insert(0,str(root));config=read(base/'config.json');inventory=read(base/'source-inventory.json')['files']
    assert len(inventory)==8 and {f['path'] for f in inventory}==EXPECTED
    for f in inventory:assert sha(root/f['path'])==sha(root/f['archive_path'])==f['sha256']
    assert config['modules']==['tests.test_advice_poll','tests.test_advice_context_scope']
    assert not (base/'independent-linux-checks.json').exists()
    stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromNames(config['modules'])
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (base/'independent-linux-tests.log').write_text(stream.getvalue(),encoding='utf-8')
    observed={'actor':'host-advice-poll-reviewer','pid':os.getpid(),'python':sys.version,'platform':platform.platform(),
              'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
              'skipped':[{'test':str(t),'reason':r} for t,r in result.skipped],'paid_model_probes':0}
    dump(base/'independent-linux-checks.json',observed)
    assert platform.system()=='Linux' and result.testsRun==15 and result.wasSuccessful() and not result.skipped
    print(json.dumps(observed))
def verify(root,manifest,plan):
    root=Path(root);base=root/REL;private=root/'.agent-runs/advice-link-20261010';sys.path.insert(0,str(root))
    from agent_runtime.advice_poll import encode,observe_advice
    from agent_runtime.result_validation import validate_result_plan
    inventory=read(base/'source-inventory.json')['files']
    assert len(inventory)==8 and {f['path'] for f in inventory}==EXPECTED
    for f in inventory:
        assert set(f)=={'path','sha256','archive_path'} and f['archive_path']==REL+'/code_snapshot/'+f['path']
        assert sha(root/f['path'])==sha(root/f['archive_path'])==f['sha256']
    assert manifest['artifacts']['code']==[{'path':f['archive_path'],'sha256':f['sha256']} for f in inventory]
    producer=read(base/'producer-checks.json');linux=read(base/'independent-linux-checks.json')
    assert producer['actor']=='native-advice-poll-producer' and producer['tests_run']==15 and producer['failures']==producer['errors']==0
    assert len(producer['skipped'])==1 and producer['skipped'][0]['reason']=='host cannot create symbolic links'
    assert linux['actor']=='host-advice-poll-reviewer' and linux['tests_run']==15 and linux['failures']==linux['errors']==0 and linux['skipped']==[]
    assert linux['platform'].startswith('Linux') and producer['platform'].startswith('Windows')
    assert producer['paid_model_probes']==linux['paid_model_probes']==0
    assert 'Ran 15 tests' in (base/'producer-tests.log').read_text() and 'Ran 15 tests' in (base/'independent-linux-tests.log').read_text()
    # Reconstruct published metadata independently from original saved API bodies.
    facts=read(base/'source-facts.json');original=read(private/'inventory.json');history=read(private/'history.json');cycles=read(private/'cycles.json')
    assert original['head']==facts['frozen_commit']=='e771d2dd03704bf1cd1e16dd67511757f1a7acab'
    assert facts['repository']=='Chosen-David/sglang' and facts['branch']=='two-level-indexer'
    expected_inventory=[{'path':x['path'],'blob_sha':x['sha'],'size':x['size']} for x in original['live']+original['archive'] if x['type']=='file']
    assert facts['inventory']==expected_inventory
    assert facts['history']==[{'sha':x['sha'],'author_date':x['commit']['author']['date'],'message':x['commit']['message'].splitlines()[0]} for x in history] and len(history)==77
    assert len(facts['cycles'])==len(cycles)==8
    for frozen,original_cycle in zip(facts['cycles'],cycles):
        raw=read(private/('commit-'+frozen['sha'][:12]+'.json'))
        expected_files=[{'path':x['filename'],'previous_path':x.get('previous_filename'),'status':x['status'],'added':x['additions'],'removed':x['deletions']}
                        for x in raw['files'] if '/advice/' in x['filename']]
        assert frozen=={'sha':raw['sha'],'message':raw['commit']['message'].splitlines()[0],'files':expected_files}
        assert original_cycle['sha']==raw['sha']
    assert len(facts['selected_files'])==6
    for f in facts['selected_files']:assert sha(private/'files'/Path(f['path']).name)==f['sha256']
    live=[x for x in expected_inventory if '/archive/' not in x['path']];archive=[x for x in expected_inventory if '/archive/' in x['path']]
    observed={'live_files':len(live),'archive_files':len(archive),'live_bytes':sum(x['size'] for x in live),'archive_bytes':sum(x['size'] for x in archive),
              'native_tests_run':15,'native_tests_passed':14,'native_tests_skipped':1,'independent_linux_tests_passed':15}
    assert observed=={x['name']:x['value'] for x in manifest['metrics']}
    assert (len(live),len(archive),observed['live_bytes'],observed['archive_bytes'])==(2,52,20587,636293)
    # Real project CLI, not a fabricated no-change response; does not write advice.
    _,baseline=observe_advice(root);path=private/'independent-current-inventory.json';assert not path.exists();path.write_bytes(encode(baseline))
    command=[sys.executable,'-X','utf8',str(root/'scripts/advice_poll.py'),'--root',str(root),
             '--baseline',path.relative_to(root).as_posix(),'--baseline-sha256',sha(path)]
    run=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=60)
    assert run.returncode==0 and json.loads(run.stdout)['events']==[] and json.loads(run.stdout)['changed'] is False
    dump(base/'independent-real-cli.json',{'command':command,'returncode':run.returncode,'response':json.loads(run.stdout),'source_write':False})
    validate_result_plan(read(base/'task-chain.json'))
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for f in group:assert sha(root/f['path'])==f['sha256'];bindings[f['path']]=f['sha256']
    evidence=[{'path':REL+'/'+name,'sha256':sha(base/name)} for name in ('independent-linux-checks.json','independent-real-cli.json')]
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(base/'manifest.json'),'artifact_hashes':bindings,
            'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':manifest['scope'],
            'verifier':{'actor':'host-advice-poll-reviewer','source':'separate fixed host verifier invocation plus WSL CPU process',
                        'run_id':'ADV-POLL-01-verify','method':'source-bound CPU suite, real CLI and raw public-source receipt reconstruction','independent':True},
            'limitations':['Synthetic small CPU cases and frozen public Git metadata/text only; SGLang scientific assertions/tests not independently rerun.',
                           'No paid model A/B, token savings, cash or scheduler/runtime adoption claim.',
                           'Two directory observations are not an atomic filesystem transaction or wall-time guarantee; inventories do not authorize or close issues.'],
            'checks':{k:{'verdict':'pass','reason':v['acceptance'],'evidence':evidence} for k,v in plan['criteria'].items()}}
    dump(base/'independent-review.json',review);return review
if __name__=='__main__':
    assert sys.argv[1:] == ['cpu'];cpu(Path(__file__).resolve().parents[3])
