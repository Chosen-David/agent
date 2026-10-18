import copy, hashlib, io, json, pathlib, subprocess, sys, unittest
sys.path.insert(0, str(pathlib.Path.cwd()))
from tests import test_usage_identity as t
from agent_runtime.token_usage import short_appserver_usage
from agent_runtime.turn_usage import current_turn_usage
root=pathlib.Path('.agent-runs/usage-identity20')
old=[]
for path,name in [('agent_runtime/token_usage.py','short_appserver_usage'),('agent_runtime/turn_usage.py','current_turn_usage')]:
    ns={};exec(subprocess.check_output(['git','show','HEAD:'+path]),ns);old.append(ns[name])
orig=t.UsageIdentityTests.parsers
summaries={}
for label,parsers,initial in [('baseline-initial',old,True),('baseline-final',old,False),('candidate-final',orig,False)]:
    t.UsageIdentityTests.parsers=tuple(parsers)
    names=unittest.defaultTestLoader.getTestCaseNames(t.UsageIdentityTests)
    if initial:names.remove('test_invalid_identity_does_not_consume_events')
    stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(t.UsageIdentityTests(n) for n in names))
    (root/(label+'-independent.log')).write_text(stream.getvalue())
    summaries[label]={'methods':r.testsRun,'failures':len(r.failures),'errors':len(r.errors)}
t.UsageIdentityTests.parsers=orig
checks=0
for parser,baseline in zip(orig,old):
    # Valid requested IDs cannot use missing event identities, each location separately.
    for index,key in [(0,'threadId'),(1,'threadId'),(2,'threadId'),(0,'id'),(1,'turnId'),(2,'id')]:
        data=t.events();p=data[index]['params'];(p['turn'] if key=='id' else p).pop(key)
        try:parser(data,'thread','turn')
        except ValueError:pass
        else:raise AssertionError((parser.__name__,index,key))
        checks+=1
    for bad in (None,'',0,False,[],{}):
        for args in ((bad,'turn'),('thread',bad)):
            class Untouched:
                def __iter__(self):raise AssertionError('consumed events')
            try:parser(Untouched(),*args)
            except ValueError:pass
            else:raise AssertionError('accepted invalid identity')
            checks+=1
    for thread,turn in [('线程/1','轮次:2'),(' ','\t'),('0','0')]:
        for n in (0,1,10,100000):
            data=t.events(thread,turn);u=data[1]['params']['tokenUsage'];u['last']={k:0 for k in u['last']};u['last'].update(inputTokens=n,totalTokens=n)
            u['total']=u['last'].copy()
            before=copy.deepcopy(data)
            assert parser(data,thread,turn)==baseline(data,thread,turn)
            assert data==before
            checks+=1
# Inherited totals permitted only in current-turn path, exact full return preserved.
data=t.events();data[1]['params']['tokenUsage']['total']={k:3*v for k,v in data[1]['params']['tokenUsage']['last'].items()}
assert current_turn_usage(data,'thread','turn')==old[1](data,'thread','turn')
checks+=1
try:short_appserver_usage(data,'thread','turn')
except ValueError:pass
else:raise AssertionError('fresh parser accepted inherited totals')
checks+=1
summaries['extra_checks']=checks
summaries['hashes']={p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in ['agent_runtime/token_usage.py','agent_runtime/turn_usage.py','tests/test_usage_identity.py']}
print(json.dumps(summaries,indent=2))
