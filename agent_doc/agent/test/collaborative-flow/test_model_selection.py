from tests.document_fixture import DocumentFixtureCase
import os
"""Selection contracts use synthetic names, not a fixed vendor model pair."""
import importlib
import json
from pathlib import Path
import unittest
import hashlib
import sys
import tempfile
import subprocess
from unittest.mock import patch
from agent_runtime.plan_review import sha


class ModelSelectionTests(DocumentFixtureCase):
    def api(self):
        return importlib.import_module('agent_runtime.codex_models')

    def catalog(self):
        return [{'id': name + '-alias', 'model': name, 'description': name,
                 'inputModalities': ['text'], 'isDefault': name == 'model-A',
                 'defaultReasoningEffort': 'medium',
                 'supportedReasoningEfforts': [{'reasoningEffort': 'medium'}]}
                for name in ('model-A', 'model-B', 'model-C')]

    def test_effective_default_overrides_catalog_recommendation_and_pages_are_complete(self):
        api = self.api()
        rows = self.catalog()
        class Client:
            def call(self, method, params):
                if method == 'config/read':
                    return {'config': {'model': 'model-C-alias', 'model_provider': 'fixture'}}
                return {'data': rows[:1] if not params.get('cursor') else rows[1:],
                        'nextCursor': 'next' if not params.get('cursor') else None}
        snapshot = api.discover_models(Client(), Path('.'))
        self.assertEqual(snapshot['default_model'], 'model-C')
        self.assertEqual(set(snapshot['models']), {'model-A', 'model-B', 'model-C'})

    def test_single_canonical_model_and_stale_default_are_blocked_before_selection(self):
        api = self.api()
        rows = self.catalog()[:1]
        class Client:
            def call(self, method, params):
                return ({'config': {'model': 'model-missing'}} if method == 'config/read'
                        else {'data': rows, 'nextCursor': None})
        with self.assertRaises(ValueError):
            api.discover_models(Client(), Path('.'))
        for configured, available, error in (('model-A', self.catalog()[:1], 'two compatible'),
                                              ('missing', self.catalog()[:2], 'configured default is absent')):
            class Separate:
                def call(self, method, params):
                    return ({'config': {'model': configured}} if method == 'config/read'
                            else {'data': available, 'nextCursor': None})
            with self.subTest(default=configured), self.assertRaisesRegex(ValueError, error):
                api.discover_models(Separate(), Path('.'))

    def test_catalog_rejects_nontext_ultra_only_and_repeated_pagination(self):
        api = self.api()
        for fault in ('nontext', 'delegating', 'missing-efforts', 'cursor'):
            rows = self.catalog()[:2]
            if fault == 'nontext':rows[1]['inputModalities'] = []
            if fault == 'delegating':rows[1]['supportedReasoningEfforts'] = [{'reasoningEffort': 'ultra'}]
            if fault == 'missing-efforts':rows[1].pop('supportedReasoningEfforts')
            class Client:
                def call(self, method, params):
                    return ({'config': {'model': 'model-A'}} if method == 'config/read' else
                            {'data': rows, 'nextCursor': 'repeat' if fault == 'cursor' else None})
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                api.discover_models(Client(), Path('.'))

    def test_two_overrides_cannot_use_aliases_of_same_model(self):
        api = self.api()
        snapshot = {'default_model': 'model-A', 'provider_id': 'fixture',
                    'models': {r['model']: r for r in self.catalog()}}
        def invoke(*args, **kwargs):self.fail('same canonical pair must fail before model invocation')
        with self.assertRaisesRegex(ValueError, 'same canonical'):
            api.select_models(snapshot, {'writer_model': 'model-A-alias', 'reviewer_model': 'model-A'}, 'Task', invoke)

    def discover_catalog(self, rows, default='model-A'):
        class Client:
            def call(self, method, params):
                return ({'config': {'model': default, 'model_provider': 'fixture'}} if method == 'config/read'
                        else {'data': rows, 'nextCursor': None})
        return self.api().discover_models(Client(), Path('.'))

    def test_discovery_requires_explicit_valid_text_modalities(self):
        self.assertEqual(len(self.discover_catalog(self.catalog())['models']), 3)
        for field in ('missing', None, [], ['image'], 'text', ['text', None], ['text', '']):
            with self.subTest(field=field):
                rows=self.catalog()
                if field == 'missing':rows[2].pop('inputModalities')
                else:rows[2]['inputModalities']=field
                snapshot=self.discover_catalog(rows)
                self.assertNotIn('model-C',snapshot['models'])
                with self.assertRaisesRegex(ValueError,'two compatible'):
                    self.discover_catalog([rows[0],rows[2]])

    def test_discovery_hidden_entries_are_excluded(self):
        rows=self.catalog();rows[1]['hidden']=True
        snapshot=self.discover_catalog(rows)
        self.assertEqual(set(snapshot['models']),{'model-A','model-C'})
        self.assertNotIn('model-B-alias',snapshot['aliases'])
        with self.assertRaisesRegex(ValueError,'two compatible'):self.discover_catalog(rows[:2])
        with self.assertRaisesRegex(ValueError,'default is absent'):self.discover_catalog(rows,'model-B')

    def test_discovery_duplicate_capabilities_conflict_but_equal_aliases_normalize(self):
        rows=self.catalog()[:2]
        duplicate={**rows[0],'id':'alternate-A'}
        snapshot=self.discover_catalog([*rows,duplicate],'alternate-A')
        self.assertEqual(set(snapshot['models']),{'model-A','model-B'})
        self.assertEqual(snapshot['default_model'],'model-A')
        self.assertEqual(snapshot['aliases']['alternate-A'],'model-A')
        duplicate['supportedReasoningEfforts']=[{'reasoningEffort':'low'}]
        with self.assertRaisesRegex(ValueError,'conflicting canonical'):
            self.discover_catalog([*rows,duplicate])

    def test_discovery_ambiguous_aliases_across_canonical_models_are_blocked(self):
        for alias in ('model-A-alias','model-A'):
            with self.subTest(alias=alias):
                rows=self.catalog()[:2];rows[1]['id']=alias
                with self.assertRaisesRegex(ValueError,'ambiguous model alias'):self.discover_catalog(rows)

    def test_discovery_conflicting_duplicates_block_before_compatibility_filter_in_both_orders(self):
        for changed in ({'inputModalities':['image']}, {'inputModalities':['text','image']},
                        {'inputModalities':None}, {'supportedReasoningEfforts':[{'reasoningEffort':'ultra'}]},
                        {'supportedReasoningEfforts':[]}, {'supportedReasoningEfforts':None}, {'hidden':True}):
            for reverse in (False,True):
                with self.subTest(changed=changed,reverse=reverse):
                    rows=self.catalog();duplicate={**rows[0],**changed,'id':'alternate-A'}
                    rows=[duplicate,*rows] if reverse else [*rows,duplicate]
                    with self.assertRaisesRegex(ValueError,'conflicting canonical'):self.discover_catalog(rows)
        # Equivalent list order and distinct aliases normalize to the same
        # candidate regardless of response order; the input isn't mutated.
        rows=self.catalog()[:2]
        rows[0]['inputModalities']=['image','text']
        rows[0]['supportedReasoningEfforts']=[{'reasoningEffort':'medium'},{'reasoningEffort':'low'}]
        duplicate={**rows[0],'id':'alternate-A','inputModalities':['text','image'],
                   'supportedReasoningEfforts':list(reversed(rows[0]['supportedReasoningEfforts']))}
        first=self.discover_catalog([*rows,duplicate],'alternate-A')
        second=self.discover_catalog([duplicate,*rows],'alternate-A')
        self.assertEqual(first,second)
        self.assertEqual(first['default_model'],'model-A')
        self.assertEqual(rows[0]['inputModalities'],['image','text'])

    def test_default_model_really_selects_supported_pair_and_readiness_is_authenticated(self):
        api = self.api()
        snapshot = {'default_model': 'model-C', 'provider_id': 'fixture',
                    'models': {r['model']: r for r in self.catalog()}}
        calls = []
        def invoke(model, operation, prompt, schema, *, effort, provider):
            calls.append((model, operation, effort, provider))
            if operation == 'select-models':
                nonce = json.loads(prompt.split('\n', 1)[1])['nonce']
                result = {'writer_model': 'model-C', 'reviewer_model': 'model-A',
                          'reason': 'Choose from supplied capabilities', 'nonce': nonce}
            else:
                result = json.loads(prompt.split('\n', 1)[1])
            identity = {'model_id': model, 'provider_id': 'fixture', 'context_id': str(len(calls)),
                        'invocation_id': str(len(calls)), 'host_source': 'synthetic-test'}
            observed = {'identity': identity, 'status': 'completed', 'tools': [], 'response_sha256': sha(result)}
            return identity, result, observed
        selected = api.select_models(snapshot, {}, 'Fix a bounded parser bug', invoke)
        self.assertEqual((selected['writer_model'], selected['reviewer_model']), ('model-C', 'model-A'))
        self.assertEqual(calls[0][:2], ('model-C', 'select-models'))
        self.assertEqual({r['identity']['model_id'] for r in selected['readiness']}, {'model-C', 'model-A'})
        self.assertTrue(all(c[2] == 'medium' for c in calls))

    def test_selector_cannot_invent_model_or_collapse_to_same_canonical_model(self):
        api = self.api()
        snapshot = {'default_model': 'model-A', 'provider_id': 'fixture',
                    'models': {r['model']: r for r in self.catalog()}}
        for pair in (('model-A', 'model-A'), ('model-A', 'invented')):
            calls = []
            def invoke(model, operation, prompt, schema, **kwargs):
                calls.append(operation)
                value = json.loads(prompt.split('\n', 1)[1])
                identity = {'model_id': model, 'provider_id': 'fixture', 'context_id': 'x',
                            'invocation_id': 'x', 'host_source': 'synthetic-test'}
                result = {'writer_model': pair[0], 'reviewer_model': pair[1],
                          'reason': 'invalid fixture', 'nonce': value['nonce']}
                return identity, result, {'identity': identity,'status':'completed','tools':[], 'response_sha256': sha(result)}
            with self.subTest(pair=pair), self.assertRaisesRegex(ValueError, 'invalid/out-of-catalog/non-distinct'):
                api.select_models(snapshot, {}, 'Task', invoke)
            self.assertEqual(calls, ['select-models'])

    def test_selector_nonce_and_override_violations_fail_before_readiness(self):
        api = self.api()
        snapshot = {'default_model': 'model-A', 'provider_id': 'fixture',
                    'models': {r['model']: r for r in self.catalog()}}
        for fault in ('nonce', 'override'):
            calls = []
            def invoke(model, operation, prompt, schema, **kwargs):
                calls.append(operation)
                value = json.loads(prompt.split('\n', 1)[1])
                identity = {'model_id': model, 'provider_id': 'fixture', 'context_id': '1',
                            'invocation_id': '1', 'host_source': 'synthetic-test'}
                result = {'writer_model': 'model-A', 'reviewer_model': 'model-B', 'reason': 'valid metadata',
                          'nonce': 'wrong' if fault == 'nonce' else value['nonce']}
                return identity, result, {'identity':identity,'status':'completed','tools':[],'response_sha256':sha(result)}
            profile = {'writer_model':'model-C'} if fault == 'override' else {}
            with self.subTest(fault=fault), self.assertRaisesRegex(ValueError, 'invalid/out-of-catalog/non-distinct'):
                api.select_models(snapshot, profile, 'Task', invoke)
            self.assertEqual(calls, ['select-models'])

    def test_observed_identity_completion_and_independence_are_required(self):
        api = self.api()
        snapshot = {'default_model': 'model-A', 'provider_id': 'fixture',
                    'models': {r['model']: r for r in self.catalog()}}
        for fault in ('model', 'provider', 'metadata', 'incomplete', 'context', 'invocation', 'nonce'):
            calls = []
            def invoke(model, operation, prompt, schema, **kwargs):
                calls.append(model)
                value = json.loads(prompt.split('\n', 1)[1])
                result = ({'writer_model': 'model-A', 'reviewer_model': 'model-B',
                           'reason': 'fixture', 'nonce': value['nonce']} if operation == 'select-models' else value)
                identity = {'model_id': model, 'provider_id': 'fixture', 'context_id': str(len(calls)),
                            'invocation_id': str(len(calls)), 'host_source': 'synthetic-test'}
                if len(calls) > 1:
                    if fault == 'model':identity['model_id'] = 'wrong-model'
                    if fault == 'provider':identity['provider_id'] = 'wrong-provider'
                    if fault == 'context':identity['context_id'] = '1'
                    if fault == 'invocation':identity['invocation_id'] = '1'
                    if fault == 'nonce':result['nonce'] = 'wrong'
                observed = {'identity': dict(identity), 'status': 'completed', 'tools': [], 'response_sha256': sha(result)}
                if len(calls) > 1 and fault == 'metadata':observed['identity']['model_id'] = 'conflicting'
                if len(calls) > 1 and fault == 'incomplete':observed['status'] = 'failed'
                return identity, result, observed
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                api.select_models(snapshot, {}, 'Task', invoke)

    def runtime_fixture(self, directory, *, version=2, max_calls=20):
        from agent_runtime.codex_host import CodexHost
        from agent_runtime.collaborative_flow import Flow
        root = Path(directory)/'project'
        root.mkdir()
        profile = Path(directory)/'runtime.json'
        value = {'version': version, 'command': [sys.executable],
                 'executable_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                 'writer_model': 'model-A' if version == 1 else None,
                 'reviewer_model': 'model-B' if version == 1 else None,
                 'max_calls': max_calls, 'timeout_seconds': 100}
        if version == 2:value['selection_policy'] = 'default-model/v1'
        profile.write_text(json.dumps(value))
        rows = self.catalog()
        class Client:
            default = 'model-A'
            fault = False
            runs, rpc = [], []
            def __init__(self, *args):pass
            def call(self, method, params):
                self.rpc.append(method)
                return ({'config': {'model': self.default, 'model_provider': 'fixture'}} if method == 'config/read'
                        else {'data': rows, 'nextCursor': None})
            def run(self, model, prompt, schema, cwd, **options):
                self.runs.append((model, dict(options)))
                packet = json.loads(prompt.split('\n', 1)[1])
                if 'writer_model' in schema['properties']:
                    result = {'writer_model': packet['effective_default'],
                              'reviewer_model': next(r['model'] for r in rows if r['model'] != packet['effective_default']),
                              'reason': 'Synthetic model decision, not a live call', 'nonce': packet['nonce']}
                else:result = packet
                identity = {'model_id': model, 'provider_id': 'fixture', 'context_id': str(len(self.runs)),
                            'invocation_id': str(len(self.runs)), 'host_source': 'synthetic-test'}
                if self.fault and 'writer_model' not in schema['properties']:identity['model_id'] = 'wrong'
                return identity, result, {'identity': dict(identity), 'status': 'completed', 'tools': [],
                                          'response_sha256': sha(result)}
            def close(self):pass
        def build(task='AUTO-01', **kwargs):
            flow = Flow(root, task)
            if flow.state is None:flow.create('Fix bounded parser behavior', mode='dual-ai')
            return CodexHost(root, task, profile, workflow=Path(directory)/'workflow', project='test',
                             client_factory=Client, **kwargs)
        return build, Client, root, profile

    def test_single_writer_catalog_does_not_launch_reviewer_or_selector(self):
        from agent_runtime.collaborative_flow import Flow
        with tempfile.TemporaryDirectory() as directory:
            build, client, root, _ = self.runtime_fixture(directory)
            Flow(root, 'SOLO').create('Use one writer')
            host = build('SOLO')
            self.assertEqual(host.profile['writer_model'], 'model-A')
            self.assertIsNone(host.reviewer_model_id)
            self.assertEqual(client.runs, [])
            self.assertEqual(build('SOLO').profile['writer_model'], 'model-A')
            self.assertEqual(client.runs, [])

    def test_new_tasks_follow_changed_default_but_resume_keeps_signed_pair_without_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            build, client, _, _ = self.runtime_fixture(directory)
            first = build()
            before = first.ledger.read_bytes()
            count = len(client.runs)
            self.assertEqual(count, 2)
            client.default = 'model-C'
            again = build()
            self.assertEqual(again.profile['writer_model'], 'model-A')
            self.assertEqual(first.ledger.read_bytes(), before)
            self.assertEqual(len(client.runs), count)
            changed = build('AUTO-02')
            self.assertEqual(changed.profile['writer_model'], 'model-C')
            self.assertNotEqual(changed.profile['writer_model'], changed.reviewer_model_id)
            self.assertTrue(all(options['effort'] == 'medium' for _, options in client.runs))

    def test_resolved_and_stale_hosts_cannot_invoke_after_terminal_or_inflight_transition(self):
        from agent_runtime.collaborative_flow import Flow
        from agent_runtime.codex_host import object_schema, TEXT
        for phase in ('cancelled','done','inflight'):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as directory:
                build,client,root,profile=self.runtime_fixture(directory)
                stale=build();flow=Flow(root,'AUTO-01')
                if phase == 'inflight':flow.state['inflight']={'method':'discuss','revision':flow.state['revision'],'payload_sha256':'unknown'}
                else:flow.state['phase']=phase
                flow.save();state_before=flow.raw;ledger_before=stale.ledger.read_bytes()
                runs,rpc=len(client.runs),len(client.rpc)
                readonly=build()  # Historical authentication/context remains available.
                self.assertTrue(readonly.model_selection)
                for host in (stale,readonly):
                    with self.assertRaisesRegex(ValueError,'blocked'):
                        host._model_call('model-A','manual','Return exactly:\n'+json.dumps({'nonce':'x'}),object_schema({'nonce':TEXT}))
                    with self.assertRaisesRegex(ValueError,'blocked'):
                        host.discuss({'summary':'Must not replay an old action'})
                command=[sys.executable,'-B','-X','utf8','-m','agent_runtime.collaborative_flow',
                    '--project-root',str(root),'--project','test','--task-id','AUTO-01','--backend','codex',
                    '--runtime-profile',str(profile.parent/'does-not-exist.json')]
                result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=10)
                self.assertEqual(result.returncode,2 if phase=='inflight' else 0,result.stderr)
                self.assertEqual(Flow(root,'AUTO-01').raw,state_before)
                self.assertEqual(stale.ledger.read_bytes(),ledger_before)
                self.assertEqual((len(client.runs),len(client.rpc)),(runs,rpc))

    def test_live_dispatch_scope_cannot_be_reused_after_task_revision_changes(self):
        from agent_runtime.collaborative_flow import Flow
        from agent_runtime.codex_host import object_schema, TEXT
        with tempfile.TemporaryDirectory() as directory:
            build,client,root,_=self.runtime_fixture(directory);host=build()
            flow=Flow(root,'AUTO-01')
            prompt='Return exactly:\n'+json.dumps({'nonce':'current'})
            class Adapter:
                dispatch_context=host.dispatch_context
                def ready(self,payload):
                    if payload.get('change_revision'):
                        changed=Flow(root,'AUTO-01');changed.state['revision']+=1;changed.save()
                    return host._model_call('model-A','ready',prompt,object_schema({'nonce':TEXT}))
            flow.call(Adapter(),'ready',{})
            before=host.ledger.read_bytes();calls=len(client.runs)
            with self.assertRaisesRegex(ValueError,'ambiguous|state changed'):
                flow.call(Adapter(),'ready',{'change_revision':True})
            # A reconstructed controller cannot authorize the persisted marker.
            with self.assertRaisesRegex(ValueError,'invalid'):
                with host.dispatch_context(Flow(root,'AUTO-01'),'ready'):pass
            self.assertEqual(host.ledger.read_bytes(),before)
            self.assertEqual(len(client.runs),calls)

    def test_fixed_profile_migration_preserves_legacy_ledger_and_only_new_tasks_select(self):
        from agent_runtime.codex_host import enable_auto_profile
        with tempfile.TemporaryDirectory() as directory:
            build, client, _, profile = self.runtime_fixture(directory, version=1)
            old = build()
            before = old.ledger.read_bytes()
            enable_auto_profile(profile)
            client.default = 'model-C'
            resumed = build()
            self.assertEqual(resumed.profile['version'], 1)
            self.assertEqual(resumed.profile['writer_model'], 'model-A')
            self.assertEqual(old.ledger.read_bytes(), before)
            self.assertEqual(client.runs, [])
            new = build('NEW-02')
            self.assertEqual(new.profile['writer_model'], 'model-C')

    def test_selection_tampering_and_missing_key_do_not_trigger_reselection(self):
        with tempfile.TemporaryDirectory() as directory:
            build, client, _, _ = self.runtime_fixture(directory)
            host = build()
            count = len(client.runs)
            state = json.loads(host.ledger.read_text())
            state['selection']['reviewer_model'] = 'model-C'
            host.ledger.write_text(json.dumps(state))
            with self.assertRaisesRegex(ValueError, 'authentication'):
                build()
            self.assertEqual(len(client.runs), count)
            (host.base/'key').write_bytes(b'short')
            with self.assertRaisesRegex(ValueError, 'key invalid'):build()
            (host.base/'key').unlink()
            with self.assertRaisesRegex(ValueError, 'key missing'):
                build()
            self.assertEqual(len(client.runs), count)

    def test_failed_selection_requires_explicit_retry_preserves_budget_and_rejects_cancel(self):
        from agent_runtime.collaborative_flow import Flow
        with tempfile.TemporaryDirectory() as directory:
            build, client, root, profile = self.runtime_fixture(directory)
            client.fault = True
            with self.assertRaises(ValueError):build()
            ledger = profile.parent/'receipts'/sha([str(root.resolve()), 'AUTO-01'])/'ledger.json'
            failed = json.loads(ledger.read_text())
            self.assertEqual(failed['calls'], 2)
            with self.assertRaisesRegex(ValueError, 'retry-model-selection'):build()
            self.assertEqual(json.loads(ledger.read_text())['calls'], 2)
            client.fault = False
            ready = build(retry_selection_reason='Verified transport recovery')
            self.assertEqual(json.loads(ledger.read_text())['calls'], 4)
            self.assertEqual(len(json.loads(ledger.read_text())['selection_attempts']), 2)
            self.assertTrue(ready.model_selection)
        with tempfile.TemporaryDirectory() as directory:
            build, client, root, _ = self.runtime_fixture(directory)
            client.fault = True
            with self.assertRaises(ValueError):build()
            Flow(root, 'AUTO-01').cancel()
            count = len(client.runs)
            with self.assertRaisesRegex(ValueError, 'not active'):build(retry_selection_reason='Cannot revive cancellation')
            self.assertEqual(len(client.runs), count)

    def test_each_failed_attempt_retains_its_outcome_error_reason_and_call_references(self):
        with tempfile.TemporaryDirectory() as directory:
            build, client, _, profile = self.runtime_fixture(directory)
            client.fault = True
            with self.assertRaises(ValueError):build()
            original = client.call
            client.fault = False
            def unavailable(self, method, params):
                if method == 'model/list':raise ValueError('distinct catalog refresh failure')
                return original(self, method, params)
            client.call = unavailable
            with self.assertRaisesRegex(ValueError, 'catalog refresh'):
                build(retry_selection_reason='Retry after account refresh')
            client.call = original
            host = build(retry_selection_reason='Transport and catalog verified')
            state = json.loads(host.ledger.read_text())
            attempts = state['selection_attempts']
            self.assertEqual([a['outcome'] for a in attempts], ['failed','failed','resolved'])
            self.assertEqual([(a['calls_before'],a['calls_after']) for a in attempts], [(0,2),(2,2),(2,4)])
            self.assertIn('untrusted model',attempts[0]['error'])
            self.assertIn('distinct catalog',attempts[1]['error'])
            self.assertEqual(attempts[1]['reason'],'Retry after account refresh')
            self.assertEqual([len(a['invocation_ids']) for a in attempts],[2,0,2])
            self.assertEqual(len(attempts[0]['ambiguous_invocations']),0)
            self.assertNotIn('error',attempts[2])
            self.assertNotIn('selection_error',state)
            self.assertEqual(state['calls'],4)

    def test_selection_success_and_failure_updates_share_the_model_call_ledger_lock(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Event
        from unittest.mock import patch
        from agent_runtime import codex_host, file_lock
        for outcome in ('resolved','failed'):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as directory:
                build,client,_,_=self.runtime_fixture(directory);existing=build()
                state=json.loads(existing.ledger.read_text());state['selection_status']='failed'
                existing.ledger.write_text(json.dumps(state));client.fault=outcome=='failed'
                reached,resume,actor_started=Event(),Event(),Event();original_store=codex_host._store
                def paused(path,value):
                    if path==existing.ledger and value.get('selection_status')==outcome and len(value.get('selection_attempts',[]))==2:
                        reached.set()
                        if not resume.wait(10):raise RuntimeError('test barrier expired')
                    return original_store(path,value)
                def other_call(host=existing):
                    actor_started.set()
                    return host._model_call('model-A','interleaved-call','Return exactly:\n'+json.dumps({'nonce':'other','ready':True}),
                        codex_host.object_schema({'nonce':codex_host.TEXT,'ready':{'type':'boolean'}}),effort='medium',provider='fixture')
                with patch.object(codex_host,'_store',side_effect=paused),ThreadPoolExecutor(max_workers=2) as pool:
                    selection=pool.submit(build,retry_selection_reason='Controlled selection recovery')
                    try:
                        self.assertTrue(reached.wait(10));client.fault=False
                        actor=pool.submit(other_call);self.assertTrue(actor_started.wait(5))
                        with (existing.base/'lock').open('a+b') as lock:
                            with self.assertRaises(BlockingIOError):file_lock.flock(lock,file_lock.LOCK_EX|file_lock.LOCK_NB)
                    finally:resume.set()
                    if outcome=='failed':
                        with self.assertRaises(ValueError):selection.result(timeout=10)
                    else:selection.result(timeout=10)
                    with self.assertRaisesRegex(ValueError,'not resolved|stale model selection'):actor.result(timeout=10)
                state=json.loads(existing.ledger.read_text())
                self.assertEqual((state['calls'],len(state['invocations'])),(4,4))
                self.assertEqual(state['selection_status'],outcome)
                self.assertEqual(state['selection_attempts'][-1]['calls_after'],4)
                self.assertEqual(len(state['selection_attempts'][-1]['invocation_ids']),2)
                self.assertFalse(any(r['operation']=='interleaved-call' for r in state['invocations']))
                ready=build(retry_selection_reason='Failed selection explicitly recovered') if outcome=='failed' else build()
                before=json.loads(ready.ledger.read_text())['calls'];other_call(ready)
                after=json.loads(ready.ledger.read_text())
                self.assertEqual(after['calls'],before+1)
                self.assertEqual(after['selection_attempts'][-1]['calls_after'],before)

    def test_selection_exclusively_owns_call_gaps_and_failed_or_unresolved_states(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Event, get_ident
        from unittest.mock import patch
        from agent_runtime import codex_host
        with tempfile.TemporaryDirectory() as directory:
            build,client,_,_=self.runtime_fixture(directory);existing=build()
            def normal(host=existing,operation='normal'):
                return host._model_call('model-A',operation,'Return exactly:\n'+json.dumps({'nonce':'normal'}),
                                        codex_host.object_schema({'nonce':codex_host.TEXT}))
            state=json.loads(existing.ledger.read_text())
            for status in ('unresolved','failed'):
                state['selection_status']=status;existing.ledger.write_text(json.dumps(state));before=existing.ledger.read_bytes()
                with self.assertRaisesRegex(ValueError,'not resolved'):normal()
                with self.assertRaisesRegex(ValueError,'active initializer'):normal(operation='select-models')
                self.assertEqual(existing.ledger.read_bytes(),before);self.assertEqual(len(client.runs),2)
            stages=('select-models','model-readiness');reached={s:Event() for s in stages};resume={s:Event() for s in stages}
            active_host=[]
            original=codex_host.CodexHost._model_call
            def paused(host,model,operation,*args,**kwargs):
                result=original(host,model,operation,*args,**kwargs)
                if operation in stages and getattr(host,'_selection_owner',None)==get_ident():
                    active_host[:]=[host]
                    reached[operation].set()
                    if not resume[operation].wait(10):raise RuntimeError('test barrier expired')
                return result
            with patch.object(codex_host.CodexHost,'_model_call',paused),ThreadPoolExecutor(max_workers=1) as pool:
                selected=pool.submit(build,retry_selection_reason='Retry keeps exclusive selection ownership')
                try:
                    for index,stage in enumerate(stages):
                        self.assertTrue(reached[stage].wait(10));before=existing.ledger.read_bytes();calls=len(client.runs)
                        with self.assertRaisesRegex(ValueError,'not resolved'):normal()
                        with self.assertRaisesRegex(ValueError,'active initializer'):normal(operation='select-models')
                        with self.assertRaisesRegex(ValueError,'active initializer'):normal(active_host[0],operation='select-models')
                        self.assertEqual(existing.ledger.read_bytes(),before);self.assertEqual(len(client.runs),calls)
                        current=json.loads(before);self.assertEqual(current['calls'],3+index)
                        self.assertTrue(all(r['status']=='completed' for r in current['invocations']))
                        resume[stage].set()
                finally:
                    for event in resume.values():event.set()
                ready=selected.result(timeout=10)
            normal(ready)
            final=json.loads(ready.ledger.read_text());self.assertEqual(final['calls'],5)
            self.assertEqual([len(a['invocation_ids']) for a in final['selection_attempts']],[2,2])
            self.assertEqual(final['selection_attempts'][-1]['calls_after'],4)

    def test_selection_never_resets_an_exhausted_host_call_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            build, client, _, profile = self.runtime_fixture(directory, max_calls=2)
            client.fault = True
            with self.assertRaises(ValueError):build()
            client.fault = False
            with self.assertRaisesRegex(ValueError, 'budget'):build(retry_selection_reason='Keep budget')
            ledger = next((profile.parent/'receipts').glob('*/ledger.json'))
            self.assertEqual(json.loads(ledger.read_text())['calls'], 2)

    def test_selection_binding_is_atomic_with_task_cancellation_and_revision(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Event
        from unittest.mock import patch
        from agent_runtime.collaborative_flow import Flow
        from agent_runtime import codex_host
        for change in ('cancel','revision','unchanged'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                build,client,root,profile=self.runtime_fixture(directory)
                Flow(root,'AUTO-01').create('Fence the final model binding',mode='dual-ai')
                reached,resume=Event(),Event();original=codex_host.select_models
                def paused(*args,**kwargs):
                    result=original(*args,**kwargs);reached.set()
                    if not resume.wait(10):raise RuntimeError('test barrier expired')
                    return result
                with patch.object(codex_host,'select_models',side_effect=paused),ThreadPoolExecutor(max_workers=1) as pool:
                    future=pool.submit(build)
                    try:
                        self.assertTrue(reached.wait(10));flow=Flow(root,'AUTO-01')
                        if change=='cancel':flow.cancel()
                        if change=='revision':flow.state['revision']+=1;flow.save()
                        task_before=flow.raw
                    finally:resume.set()
                    if change=='unchanged':future.result(timeout=10)
                    else:
                        with self.assertRaisesRegex(ValueError,'state changed'):future.result(timeout=10)
                ledger=profile.parent/'receipts'/sha([str(root.resolve()),'AUTO-01'])/'ledger.json'
                state=json.loads(ledger.read_text())
                self.assertEqual(Flow(root,'AUTO-01').raw,task_before)
                self.assertEqual(state['calls'],2);self.assertEqual(len(client.runs),2)
                self.assertEqual(len(state['selection_attempts'][0]['invocation_ids']),2)
                if change=='unchanged':self.assertEqual(state['selection_status'],'resolved')
                else:
                    self.assertEqual(state['selection_status'],'failed')
                    self.assertNotIn('selection',state);self.assertNotIn('binding',state)

    def test_reconciliation_rechecks_state_after_racing_initializer_and_is_one_shot(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Event
        from unittest.mock import patch
        from agent_runtime import codex_host, file_lock
        with tempfile.TemporaryDirectory() as directory:
            build,client,root,profile=self.runtime_fixture(directory);host=build()
            state=json.loads(host.ledger.read_text());state['selection_status']='failed';host.ledger.write_text(json.dumps(state))
            reached,resume=Event(),Event();original=codex_host.flock
            def paused(stream,operation):
                if Path(stream.name).name=='selection.lock' and operation==file_lock.LOCK_EX|file_lock.LOCK_NB:
                    reached.set()
                    if not resume.wait(10):raise RuntimeError('test barrier expired')
                return original(stream,operation)
            def reconcile():return codex_host.CodexHost(root,'AUTO-01',profile,workflow=Path(directory)/'workflow',
                project='test',client_factory=client,reconcile_selection_reason='Race must not change a resolved initializer')
            with patch.object(codex_host,'flock',side_effect=paused),ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(reconcile)
                try:
                    self.assertTrue(reached.wait(10));ready=build(retry_selection_reason='Initializer wins before reconciliation lock')
                    before=ready.ledger.read_bytes();runs=len(client.runs);rpc=len(client.rpc)
                finally:resume.set()
                with self.assertRaisesRegex(ValueError,'already bound'):future.result(timeout=10)
            self.assertEqual(ready.ledger.read_bytes(),before)
            self.assertEqual((len(client.runs),len(client.rpc)),(runs,rpc))

    def test_reconciliation_rejects_foreign_pending_rows_without_mutation(self):
        from copy import deepcopy
        from agent_runtime import codex_host
        from agent_runtime.model_process import process_scope
        for owner in (None,'f'*32,'wrong-operation'):
            with self.subTest(owner=owner),tempfile.TemporaryDirectory() as directory:
                build,client,root,profile=self.runtime_fixture(directory);host=build()
                state=json.loads(host.ledger.read_text());state['selection_status']='failed'
                for field in ('binding','selection','selection_signature'):state.pop(field,None)
                attempt=state['selection_attempts'][-1];attempt['outcome']='failed'
                attempt['process_record']={'scope':process_scope(),'owner_pid':99999999,'phase':'closed','backend_pid':None}
                attempt['process_signature']=host._process_signature(attempt['id'],attempt['process_record'])
                row=deepcopy(state['invocations'][0]);row.update(id='e'*32,status='pending',
                    operation='ordinary' if owner=='wrong-operation' else 'select-models',
                    selection_attempt_id=attempt['id'] if owner=='wrong-operation' else owner)
                for field in ('response','response_sha256','observed'):row.pop(field,None)
                row['process_record']={'scope':process_scope(),'owner_pid':99999999,'phase':'reserved','backend_pid':None}
                row['process_signature']=host._process_signature(row['id'],row['process_record'])
                state['calls']+=1;state['invocations'].append(row);host.ledger.write_text(json.dumps(state))
                before=host.ledger.read_bytes();runs=len(client.runs);rpc=len(client.rpc)
                with self.assertRaisesRegex(ValueError,'not owned by the abandoned'):
                    codex_host.CodexHost(root,'AUTO-01',profile,workflow=Path(directory)/'workflow',project='test',
                        client_factory=client,reconcile_selection_reason='Must not consume unrelated work')
                self.assertEqual(host.ledger.read_bytes(),before)
                self.assertEqual((len(client.runs),len(client.rpc)),(runs,rpc))

    def test_crashed_selection_requires_verified_process_reconciliation_before_retry(self):
        from agent_runtime.codex_host import CodexHost
        from agent_runtime.collaborative_flow import Flow
        for crash in ('during-call', 'before-launch', 'discovery', 'unknown-launch', 'unknown-discovery-launch', 'caught-reserved'):
            with self.subTest(crash=crash), tempfile.TemporaryDirectory() as directory:
                build, client, root, profile = self.runtime_fixture(directory)
                Flow(root, 'AUTO-01').create('Preserve interrupted selection', mode='dual-ai')
                # Both subprocesses belong to this test. Never kill a ledger PID.
                backend = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(40)'])
                try:
                    script = Path(directory)/'crash.py'
                    script.write_text('''import json,os,sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,sys.argv[1])
from agent_runtime.codex_host import CodexHost
from tests.test_codex_model_selection import ModelSelectionTests
rows=ModelSelectionTests().catalog()
if sys.argv[5] in ('before-launch','caught-reserved'):
 original=CodexHost._update_ledger
 failed=[False]
 def interrupted(self,update):
  current=json.loads(self.ledger.read_text())
  if (sys.argv[5]=='caught-reserved' and not failed[0] and current.get('selection_status')=='selecting' and current['selection_attempts'][-1]['process_record']['phase']=='reserved'):
   failed[0]=True;raise ValueError('caught before discovery-start persistence')
  state=original(self,update)
  if sys.argv[5]=='before-launch' and state.get('selection_status')=='selecting' and state['selection_attempts'][-1]['process_record']['phase']=='reserved':os._exit(7)
  return state
 CodexHost._update_ledger=interrupted
class Client:
 count=0
 def __init__(self,*args):
  Client.count+=1
  if sys.argv[5]=='unknown-discovery-launch' or (sys.argv[5]=='unknown-launch' and Client.count==2):os._exit(7)
  if sys.argv[5]=='discovery' or Client.count>1:self.process=SimpleNamespace(pid=int(sys.argv[4]))
 def call(self,method,params):
  if sys.argv[5]=='discovery':os._exit(7)
  return {'config':{'model':'model-A','model_provider':'fixture'}} if method=='config/read' else {'data':rows,'nextCursor':None}
 def run(self,*args,**kwargs):os._exit(7)
 def close(self):pass
try:CodexHost(Path(sys.argv[2]),'AUTO-01',Path(sys.argv[3]),workflow=Path(sys.argv[2]).parent/'workflow',project='test',client_factory=Client)
except ValueError:
 if sys.argv[5]=='caught-reserved':os._exit(7)
 raise
''', encoding='utf8')
                    command = [sys.executable,'-B',str(script),str(Path(os.environ["AGENT_TEST_PROJECT_ROOT"])),
                               str(root),str(profile),str(backend.pid),crash]
                    child = subprocess.run(command,capture_output=True,text=True,timeout=15)
                    self.assertEqual(child.returncode,7,child.stderr)
                    ledger = profile.parent/'receipts'/sha([str(root.resolve()),'AUTO-01'])/'ledger.json'
                    before = json.loads(ledger.read_text())
                    calls = 1 if crash in ('during-call','unknown-launch') else 0
                    self.assertEqual(before['calls'],calls)
                    with self.assertRaisesRegex(ValueError,'reconcile-model-selection'):
                        build(retry_selection_reason='A reason alone cannot clear an unknown call')
                    self.assertEqual(client.runs,[])
                    def reconcile():
                        return CodexHost(root,'AUTO-01',profile,workflow=Path(directory)/'workflow',
                            project='test',client_factory=client,reconcile_selection_reason='Verify original local process absence')
                    if crash in ('during-call','discovery'):
                        with self.assertRaisesRegex(ValueError,'backend is still live'):reconcile()
                        self.assertEqual(json.loads(ledger.read_text()),before)
                    backend.terminate();backend.wait(timeout=10)
                    if crash in ('unknown-launch','unknown-discovery-launch'):
                        with self.assertRaisesRegex(ValueError,'PID unknown'):reconcile()
                        self.assertEqual(json.loads(ledger.read_text()),before)
                        continue
                    reconciled = reconcile()
                    self.assertEqual(client.runs,[])
                    interrupted = json.loads(ledger.read_text())
                    self.assertEqual(interrupted['calls'],calls)
                    self.assertEqual(interrupted['selection_attempts'][0]['outcome'],'failed' if crash=='caught-reserved' else 'interrupted')
                    if crash=='caught-reserved':
                        self.assertEqual(before['selection_status'],'failed')
                        self.assertIn('caught before discovery-start',interrupted['selection_attempts'][0]['error'])
                        self.assertEqual(interrupted['selection_attempts'][0]['reason'],'initial task selection')
                    self.assertEqual(len(reconciled.reconciliation['invocation_ids']),calls)
                    if calls:self.assertEqual(interrupted['invocations'][0]['status'],'reconciled-local-transport-ended')
                    ready = build(retry_selection_reason='Original transport reconciled; preserve all costs')
                    final = json.loads(ready.ledger.read_text())
                    self.assertEqual(final['calls'],calls+2)
                    self.assertEqual([a['outcome'] for a in final['selection_attempts']],['failed' if crash=='caught-reserved' else 'interrupted','resolved'])
                finally:
                    if backend.poll() is None:backend.terminate();backend.wait(timeout=10)

    def test_post_send_disconnect_stays_ambiguous_until_reconciled_but_prelaunch_failure_does_not(self):
        from agent_runtime.collaborative_flow import Flow
        from agent_runtime.codex_host import CodexHost, BackendStartupError, object_schema
        for failure in ('disconnect','startup-tagged'):
            with tempfile.TemporaryDirectory() as directory:
                build,client,root,profile=self.runtime_fixture(directory)
                Flow(root,'AUTO-01').create('Preserve ambiguous sent calls',mode='dual-ai')
                script=Path(directory)/'disconnect.py'
                script.write_text('''import json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from agent_runtime.codex_host import CodexHost,BackendStartupError
from agent_runtime.plan_review import sha
from tests.test_codex_model_selection import ModelSelectionTests
root,profile=Path(sys.argv[2]),Path(sys.argv[3])
rows=ModelSelectionTests().catalog()
class Client:
 constructed=0
 runs=0
 def __init__(self,*args):
  Client.constructed+=1
  if Client.constructed==2:
   self.process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(40)'],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 def call(self,method,params):
  return {'config':{'model':'model-A','model_provider':'fixture'}} if method=='config/read' else {'data':rows,'nextCursor':None}
 def run(self,*args,**kwargs):
  Client.runs+=1
  if sys.argv[4]=='startup-tagged':raise BackendStartupError('synthetic startup-tagged error after send')
  raise ValueError('synthetic disconnect after send')
 def close(self):
  if hasattr(self,'process'):
   self.process.terminate();self.process.wait(timeout=10)
def build(**kwargs):return CodexHost(root,'AUTO-01',profile,workflow=root.parent/'workflow',project='test',client_factory=Client,**kwargs)
try:build()
except ValueError:
 ledger=profile.parent/'receipts'/sha([str(root.resolve()),'AUTO-01'])/'ledger.json'
 before=ledger.read_bytes();constructors=Client.constructed
 try:build(retry_selection_reason='A retry reason cannot resolve a sent call')
 except ValueError as exc:assert 'reconcile-model-selection' in str(exc)
 else:raise AssertionError('sent call was retried without reconciliation')
 assert ledger.read_bytes()==before and Client.constructed==constructors and Client.runs==1
 os._exit(7)
raise AssertionError('disconnect fixture did not fail')
    ''',encoding='utf8')
                result=subprocess.run([sys.executable,'-B',str(script),str(Path(os.environ["AGENT_TEST_PROJECT_ROOT"])),
                                       str(root),str(profile),failure],capture_output=True,text=True,timeout=20)
                self.assertEqual(result.returncode,7,result.stderr)
                ledger=profile.parent/'receipts'/sha([str(root.resolve()),'AUTO-01'])/'ledger.json'
                failed=json.loads(ledger.read_text());row=failed['invocations'][0]
                self.assertEqual(failed['calls'],1);self.assertEqual(row['status'],'pending')
                self.assertEqual(row['process_record']['phase'],'closed')
                self.assertIn('exitcode',row['process_record'])
                self.assertEqual(failed['selection_attempts'][0]['ambiguous_invocations'],[row['id']])
                with self.assertRaisesRegex(ValueError,'reconcile-model-selection'):
                    build(retry_selection_reason='Still needs explicit reconciliation')
                self.assertEqual(client.rpc,[]);self.assertEqual(client.runs,[])
                recovery=CodexHost(root,'AUTO-01',profile,workflow=Path(directory)/'workflow',project='test',
                    client_factory=client,reconcile_selection_reason='Verified local termination only; remote outcome remains unknown')
                state=json.loads(ledger.read_text());self.assertEqual(state['calls'],1)
                self.assertEqual(state['invocations'][0]['status'],'reconciled-local-transport-ended')
                self.assertEqual(recovery.reconciliation['remote_completion'],'not-established')
                self.assertEqual(recovery.reconciliation['remote_billing'],'not-established')
                ready=build(retry_selection_reason='Separate retry after local reconciliation')
                state=json.loads(ready.ledger.read_text());self.assertEqual(state['calls'],3)
                self.assertEqual([a['outcome'] for a in state['selection_attempts']],['failed','resolved'])
                self.assertIn('after send',state['selection_attempts'][0]['error'])
                # Even hydrated operational metadata cannot turn this one-shot
                # recovery object into a reusable dispatcher.
                recovery.profile=ready.profile.copy()
                recovery.binding=ready.binding
                recovery.model_selection=ready.model_selection
                before=ready.ledger.read_bytes();runs=len(client.runs);rpc=len(client.rpc)
                with self.assertRaisesRegex(ValueError,'reconciliation-only'):
                    recovery._model_call('model-A','ordinary','Return exactly:\n'+json.dumps({'nonce':'x'}),
                                        object_schema({'nonce':{'type':'string'}}))
                with self.assertRaisesRegex(ValueError,'reconciliation-only'):
                    recovery._ensure_selection('Cannot reuse the reconciliation object')
                with self.assertRaisesRegex(ValueError,'one-shot'):
                    recovery._reconcile_selection('Cannot reconcile a second time')
                self.assertEqual(ready.ledger.read_bytes(),before)
                self.assertEqual((len(client.runs),len(client.rpc)),(runs,rpc))
        with tempfile.TemporaryDirectory() as directory:
            build,client,_,profile=self.runtime_fixture(directory);original=client.__init__;count=[0]
            def fail_before_run(self,*args):
                count[0]+=1
                if count[0]==2:raise BackendStartupError('synthetic known pre-model-start failure')
                original(self,*args)
            client.__init__=fail_before_run
            with self.assertRaisesRegex(ValueError,'pre-model-start'):build()
            ledger=next((profile.parent/'receipts').glob('*/ledger.json'));state=json.loads(ledger.read_text())
            self.assertEqual(state['calls'],1);self.assertEqual(state['invocations'][0]['status'],'not-started')
            self.assertEqual(client.runs,[])
            ready=build(retry_selection_reason='Known pre-model-start failure corrected')
            state=json.loads(ready.ledger.read_text());self.assertEqual(state['calls'],3)
            self.assertEqual(state['selection_attempts'][0]['calls_after'],1)

    def test_reconciliation_rejects_live_owner_tampering_and_resolved_selection(self):
        from agent_runtime.codex_host import CodexHost
        with tempfile.TemporaryDirectory() as directory:
            build, client, root, profile = self.runtime_fixture(directory)
            host=build()
            def reconcile():
                return CodexHost(root,'AUTO-01',profile,workflow=Path(directory)/'workflow',project='test',
                                 client_factory=client,reconcile_selection_reason='Verify without any calls')
            with self.assertRaisesRegex(ValueError,'already bound'):reconcile()
            state=json.loads(host.ledger.read_text())
            state['selection_status']='selecting'
            state['selection_attempts'][0]['outcome']='selecting'
            host.ledger.write_text(json.dumps(state))
            before=host.ledger.read_bytes()
            with self.assertRaisesRegex(ValueError,'owner is live'):reconcile()
            self.assertEqual(host.ledger.read_bytes(),before)
            state['selection_attempts'][0]['process_record']['owner_pid']=99999999
            host.ledger.write_text(json.dumps(state))
            with self.assertRaisesRegex(ValueError,'authentication-failed'):reconcile()
            self.assertEqual(len(client.runs),2)

    def test_concurrent_initializers_share_one_selection_and_call_budget(self):
        from concurrent.futures import ThreadPoolExecutor
        from agent_runtime.collaborative_flow import Flow
        import time
        with tempfile.TemporaryDirectory() as directory:
            build, client, root, _ = self.runtime_fixture(directory)
            Flow(root, 'AUTO-01').create('One bounded selection', mode='dual-ai')
            original = client.run
            def slow(self, *args, **kwargs):
                time.sleep(.04)
                return original(self, *args, **kwargs)
            client.run = slow
            with ThreadPoolExecutor(max_workers=2) as pool:
                hosts = list(pool.map(lambda _: build(), range(2)))
            self.assertEqual(len(client.runs), 2)
            self.assertEqual(hosts[0].binding, hosts[1].binding)
            self.assertEqual(json.loads(hosts[0].ledger.read_text())['calls'], 2)

    def test_cli_new_profile_needs_no_model_names_and_guarded_paths_are_never_written(self):
        from agent_runtime.codex_host import _store
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'runtime.json'
            result = subprocess.run([sys.executable, '-B', '-X', 'utf8', '-m', 'agent_runtime.codex_host',
                '--profile', str(path), '--codex', sys.executable], capture_output=True, encoding='utf8', timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(path.read_text())
            self.assertEqual(value['version'], 2)
            self.assertIsNone(value['writer_model'])
            self.assertIsNone(value['reviewer_model'])
            self.assertEqual(value['selection_policy'], 'default-model/v1')
            protected = Path(directory)/'agent_doc/guide/runtime.json'
            with self.assertRaises(ValueError):_store(protected, {})
            self.assertFalse(protected.exists())

    def test_default_runtime_profile_can_be_initialized_and_missing_profile_explains_setup(self):
        from agent_runtime import codex_host
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            profile = home / '.codex/chosen-agent/runtime.json'
            with patch.object(Path, 'home', return_value=home):
                with self.assertRaisesRegex(ValueError, r'codex_host.*--codex'):
                    codex_host.load_profile(profile)
                self.assertFalse(profile.exists())
                with patch.object(sys, 'argv', ['codex_host', '--codex', sys.executable]):
                    self.assertEqual(codex_host.main(), 0)
                self.assertEqual(codex_host.load_profile(profile)['selection_policy'], 'default-model/v1')

    def test_cli_preflight_refuses_before_opening_model_backend(self):
        from agent_runtime.collaborative_flow import Flow
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'project';root.mkdir()
            Flow(root, 'CLI-01').create('Check required arguments', mode='human')
            command = [sys.executable, '-B', '-X', 'utf8', '-m', 'agent_runtime.collaborative_flow',
                '--project-root', str(root), '--workflow-root', str(Path(directory)/'workflow'),
                '--project', 'test', '--task-id', 'CLI-01', '--backend', 'codex',
                '--runtime-profile', str(Path(directory)/'absent.json')]
            for extra, expected in (([], 'trust-project-code'), (['--trust-project-code'], 'output'),
                                    (['--trust-project-code', '--output', str(Path(directory)/'out')], 'task suite')):
                result = subprocess.run(command+extra, capture_output=True, encoding='utf8', timeout=10)
                self.assertEqual(result.returncode, 2)
                self.assertIn(expected, result.stderr)


if __name__ == '__main__':
    unittest.main()
