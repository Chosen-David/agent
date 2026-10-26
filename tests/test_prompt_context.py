import json
from pathlib import Path
import tempfile
import unittest
from agent_runtime.prompt_context import compose_entries, ENTRIES, MARKER, SHARED_MARKERS, _dedup_shared
from agent_runtime.token_usage import short_probe_usage

class PromptContextTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.block = MARKER + '\nPreserve pending and cancelled work; require independent evidence.'
        for key, path in ENTRIES.items():
            p = self.root/path; p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(('# '+key+'\n\n```text\n'+self.block+'\n【local】\nKeep '+key+' constraints.\n```\n').encode('utf-8'))

    def test_shared_global_policy_only_once_unique_rules_unchanged(self):
        full = compose_entries(self.root,deduplicate=False)
        chosen = compose_entries(self.root)
        self.assertEqual(full['prompt'].count(self.block),3)
        self.assertEqual(chosen['prompt'].count(self.block),1)
        self.assertLess(len(chosen['prompt']),len(full['prompt']))
        for key in ENTRIES:
            self.assertIn('Keep '+key+' constraints.',chosen['prompt'])
        self.assertEqual([r['policy'] for r in chosen['documents']],['shared-full','shared-reference','shared-reference'])

    def test_differing_policy_is_retained_and_source_not_modified(self):
        p = self.root/ENTRIES['research']
        p.write_bytes(p.read_bytes().replace(b'cancelled',b'cancelled and failed'))
        original = p.read_bytes()
        chosen=compose_entries(self.root)
        self.assertIn('cancelled and failed',chosen['prompt'])
        self.assertEqual(chosen['documents'][-1]['policy'],'retained')
        self.assertEqual(p.read_bytes(),original)

    def test_quote_ambiguous_scope_or_non_text_fence_never_pruned(self):
        for extra in ('\n> '+self.block+'\n', '\n```text\n'+self.block+'\n```\n'):
            p=self.root/ENTRIES['research']; original=p.read_bytes().decode('utf-8')+extra
            p.write_bytes(original.encode('utf-8'))
            chosen=compose_entries(self.root)
            # Quoted marker with a line-break body is not mistaken for a fresh shared block.
            if extra.startswith('\n```'):
                self.assertIn(original,chosen['prompt'])
        p=self.root/ENTRIES['research']; original='# quoted\n\n```python\n'+self.block+'\n```\n'
        p.write_bytes(original.encode('utf-8'))
        self.assertIn(original,compose_entries(self.root)['prompt'])

    def test_no_persistent_read_cache_standalone_and_cap_failure(self):
        one=compose_entries(self.root,['research'])
        self.assertIn(self.block,one['prompt'])
        self.assertEqual(one,compose_entries(self.root,['research']))
        with self.assertRaisesRegex(ValueError,'exceeds'): compose_entries(self.root,max_chars=20)
        with self.assertRaises(ValueError): compose_entries(self.root,['unknown'])
        p=self.root/ENTRIES['decision']; p.write_text('No canonical policy',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'missing'): compose_entries(self.root)

    def test_outer_fence_and_html_comment_are_not_global_instructions(self):
        p=self.root/ENTRIES['research']
        for original in ('# example\n\n~~~markdown\n```text\n'+self.block+'\n```\n~~~\n',
                         '# example\n\n<!--\n```text\n'+self.block+'\n```\n-->\n'):
            p.write_bytes(original.encode('utf-8'))
            result=compose_entries(self.root)
            self.assertIn(original,result['prompt'])
            self.assertEqual(result['documents'][-1]['policy'],'retained')

    def test_shared_markers_dedup_across_entries(self):
        # When a SHARED_MARKERS section is byte-identical across entries,
        # only the first occurrence is kept; later ones become short refs.
        shared_block = SHARED_MARKERS[0] + '\n' + '固定共享正文用于去重测试。'
        for key, path in ENTRIES.items():
            p = self.root/path
            text = p.read_text(encoding='utf-8')
            # Insert the shared block inside the existing ```text fence
            text = text.replace('```text\n', '```text\n' + shared_block + '\n', 1)
            p.write_text(text, encoding='utf-8')
        chosen = compose_entries(self.root)
        # The shared block appears fully only once
        self.assertEqual(chosen['prompt'].count('固定共享正文用于去重测试。'), 1)
        # Later entries got a short reference
        self.assertIn('已在前文完整提供，逐条适用', chosen['prompt'])
        # Source files are not modified
        for key, path in ENTRIES.items():
            p = self.root/path
            content = p.read_text(encoding='utf-8')
            self.assertIn('固定共享正文用于去重测试。', content)

    def test_differing_shared_marker_is_retained(self):
        # If a SHARED_MARKERS section differs across entries, both are kept.
        blockA = SHARED_MARKERS[0] + '\n' + '版本A专属内容。'
        blockB = SHARED_MARKERS[0] + '\n' + '版本B专属内容。'
        p = self.root/ENTRIES['general']
        p.write_text(p.read_text(encoding='utf-8').replace('```text\n', '```text\n' + blockA + '\n', 1), encoding='utf-8')
        p = self.root/ENTRIES['research']
        p.write_text(p.read_text(encoding='utf-8').replace('```text\n', '```text\n' + blockB + '\n', 1), encoding='utf-8')
        chosen = compose_entries(self.root)
        self.assertIn('版本A专属内容。', chosen['prompt'])
        self.assertIn('版本B专属内容。', chosen['prompt'])

    def test_all_shared_markers_deduped_from_real_files(self):
        # Real orchestrator.md and research_orchestrator.md share all 4 markers.
        # With dedup, the second file's shared sections become short refs.
        root = Path('.').resolve()
        full = compose_entries(root, deduplicate=False)
        chosen = compose_entries(root)
        # Total dedup savings includes the tmux section (1,667 chars)
        self.assertLess(len(chosen['prompt']), len(full['prompt']))
        # The tmux marker appears in short-ref form for the second entry
        self.assertIn('已在前文完整提供，逐条适用', chosen['prompt'])

    def test_dedup_shared_returns_newly_emitted(self):
        emitted = set()
        block = SHARED_MARKERS[0] + '\nhello\n'
        text = 'title\n\n```text\n' + block + '```\nsuffix'
        text2, newly = _dedup_shared(text, emitted)
        self.assertEqual(len(newly), 1)
        emitted.update(newly)
        # Second call with same block replaces it
        text3, newly2 = _dedup_shared(text, emitted)
        self.assertEqual(len(newly2), 0)
        self.assertIn('已在前文完整提供', text3)

    def test_symlink_read_refusal(self):
        p=self.root/ENTRIES['research']; saved=self.root/'saved.md'; p.rename(saved)
        try: p.symlink_to(saved)
        except OSError: self.skipTest('symlink permission unavailable')
        with self.assertRaisesRegex(ValueError,'symlink'): compose_entries(self.root)

class UsageTests(unittest.TestCase):
    def events(self,usage=None):
        return [{'type':'thread.started','thread_id':'fresh-id'},{'type':'turn.started'},
                {'type':'item.completed','item':{'type':'agent_message','text':'OK'}},
                {'type':'turn.completed','usage':usage or {'input_tokens':100,'cached_input_tokens':80,'output_tokens':20}}]
    def parse(self,events): return short_probe_usage(map(json.dumps,events))

    def test_server_total_does_not_subtract_cached_tokens(self):
        result=self.parse(self.events())
        self.assertEqual(result['total_tokens'],120)
        self.assertEqual(result['cached_input_tokens'],80)

    def test_missing_invalid_repeated_failure_and_tools_are_rejected(self):
        for events in (self.events()+[self.events()[-1]],self.events()+[{'type':'turn.failed'}],
                       self.events({'input_tokens':100,'output_tokens':20}),
                       self.events({'input_tokens':100,'cached_input_tokens':101,'output_tokens':20}),
                       self.events()+[{'type':'item.started','item':{'type':'command_execution'}}]):
            with self.assertRaises(ValueError): self.parse(events)

    def test_corrupt_json_and_reordered_events_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'damaged'):
            short_probe_usage([json.dumps(self.events()[0]),'{damaged tool event}',*map(json.dumps,self.events()[1:])])
        for events in (list(reversed(self.events())),[self.events()[1],self.events()[0],*self.events()[2:]],
                       self.events()+[self.events()[2]]):
            with self.assertRaises(ValueError): self.parse(events)

class AppServerUsageTests(unittest.TestCase):
    def events(self):
        usage={'inputTokens':100,'cachedInputTokens':80,'outputTokens':20,
               'reasoningOutputTokens':10,'totalTokens':120}
        return [
            {'method':'turn/started','params':{'threadId':'t','turn':{'id':'v','status':'inProgress'}}},
            {'method':'item/completed','params':{'threadId':'t','turnId':'v','item':{'type':'agentMessage'}}},
            {'method':'thread/tokenUsage/updated','params':{'threadId':'t','turnId':'v',
                'tokenUsage':{'last':dict(usage),'total':dict(usage)}}},
            {'method':'turn/completed','params':{'threadId':'t','turn':{'id':'v','status':'completed','items':[]}}}]

    def parse(self,events):
        from agent_runtime.token_usage import short_appserver_usage
        return short_appserver_usage(events,'t','v')

    def test_only_final_snapshot_is_counted_and_cache_is_not_subtracted(self):
        events=self.events(); events.insert(2,events[2])
        self.assertEqual(self.parse(events)['total_tokens'],120)

    def test_equal_floating_cumulative_counts_are_rejected(self):
        for key in self.events()[2]['params']['tokenUsage']['total']:
            with self.subTest(key=key):
                events=self.events()
                total=events[2]['params']['tokenUsage']['total']
                total[key]=float(total[key])
                with self.assertRaises(ValueError):
                    self.parse(json.loads(json.dumps(events)))

    def test_equal_boolean_cumulative_counts_are_rejected(self):
        for counts in ((0,0,0,0,0),(1,1,1,2,1)):
            keys=('inputTokens','cachedInputTokens','outputTokens','totalTokens','reasoningOutputTokens')
            usage=dict(zip(keys,counts))
            for key,value in usage.items():
                if value not in (0,1):
                    continue
                with self.subTest(counts=counts,key=key):
                    events=self.events()
                    events[2]['params']['tokenUsage']={'last':dict(usage),'total':dict(usage)}
                    events[2]['params']['tokenUsage']['total'][key]=bool(value)
                    with self.assertRaises(ValueError):
                        self.parse(json.loads(json.dumps(events)))

    def test_zero_integer_counts_retain_complete_output(self):
        events=self.events()
        for bucket in ('last','total'):
            events[2]['params']['tokenUsage'][bucket]=dict.fromkeys(
                events[2]['params']['tokenUsage'][bucket],0)
        actual=self.parse(json.loads(json.dumps(events)))
        expected=self.parse(self.events())
        for key in ('input_tokens','cached_input_tokens','output_tokens','total_tokens','reasoning_output_tokens'):
            expected[key]=0
        self.assertEqual(actual,expected)

    def test_prior_turn_failures_tools_and_inconsistent_total_are_rejected(self):
        for change in ('prior','failure','tools','sum','duplicate'):
            events=self.events()
            if change=='prior': events[2]['params']['tokenUsage']['total']['inputTokens']=200
            elif change=='failure': events[-1]['params']['turn']['status']='failed'
            elif change=='tools': events[1]['params']['item']['type']='commandExecution'
            elif change=='sum':
                for k in ('last','total'):events[2]['params']['tokenUsage'][k]['totalTokens']=119
            else:events.append(events[-1])
            with self.assertRaises(ValueError):self.parse(events)

class PromptPhysicalScopeTests(unittest.TestCase):
    setUp = PromptContextTests.setUp
    separators = ('\v', '\f', '\x1c', '\x1d', '\x1e', '\x85', '\u2028', '\u2029')

    def unknown(self, sep, marker=None):
        return ('# Literal source\nProse' + sep + '```text\n' +
                (self.block if marker is None else marker + '\nShared evidence constraint.') +
                '\n【local】\nKeep literal local context.\n```\n')

    def test_nonphysical_openers_never_authorize_policy_pruning(self):
        p = self.root / ENTRIES['research']
        for sep in self.separators:
            with self.subTest(separator=repr(sep)):
                original = self.unknown(sep)
                p.write_bytes(original.encode('utf-8'))
                result = compose_entries(self.root)
                self.assertIn(original, result['prompt'])
                self.assertEqual(result['documents'][-1]['policy'], 'retained')
                self.assertEqual(p.read_bytes(), original.encode('utf-8'))

    def test_unknown_canonical_scope_fails_closed(self):
        p = self.root / ENTRIES['decision']
        for sep in self.separators:
            with self.subTest(separator=repr(sep)):
                original = self.unknown(sep)
                p.write_bytes(original.encode('utf-8'))
                with self.assertRaisesRegex(ValueError, 'canonical shared decision scope'):
                    compose_entries(self.root)
                self.assertEqual(p.read_bytes(), original.encode('utf-8'))

    def test_extra_shared_markers_keep_unverified_source_exact(self):
        for sep in self.separators:
            for marker in SHARED_MARKERS:
                with self.subTest(separator=repr(sep), marker=marker):
                    original = self.unknown(sep, marker)
                    emitted = {marker + '\nShared evidence constraint.'}
                    actual, added = _dedup_shared(original, emitted)
                    self.assertEqual(actual, original)
                    self.assertEqual(added, [])
                    self.assertEqual(emitted, {marker + '\nShared evidence constraint.'})

    def test_nonphysical_closers_do_not_reject_real_global_scope(self):
        for sep in self.separators:
            with self.subTest(separator=repr(sep)):
                originals = {}
                for key, path in ENTRIES.items():
                    text = ('# ' + key + '\n```text\nProse' + sep + '```\n' +
                            self.block + '\n【local】\nKeep ' + key + ' constraints.\n```\n')
                    (self.root / path).write_bytes(text.encode('utf-8'))
                    originals[path] = text.encode('utf-8')
                result = compose_entries(self.root)
                self.assertEqual(result['prompt'].count(self.block), 1)
                self.assertEqual([row['policy'] for row in result['documents']],
                                 ['shared-full', 'shared-reference', 'shared-reference'])
                for key, path in ENTRIES.items():
                    self.assertIn('Prose' + sep + '```\n', result['prompt'])
                    self.assertIn('Keep ' + key + ' constraints.', result['prompt'])
                    self.assertEqual((self.root / path).read_bytes(), originals[path])

    def test_real_cli_preserves_unknown_scope_in_utf8_raw_and_json(self):
        import os, subprocess, sys
        p = self.root / ENTRIES['research']
        for sep in ('\u2028', '\u2029'):
            for as_json in (False, True):
                with self.subTest(separator=repr(sep), as_json=as_json):
                    original = self.unknown(sep)
                    p.write_bytes(original.encode('utf-8'))
                    before = {name: (self.root / name).read_bytes() for name in ENTRIES.values()}
                    command = [sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'scripts/prompt_context.py'),
                               '--root', str(self.root), *(['--json'] if as_json else [])]
                    completed = subprocess.run(command, capture_output=True, timeout=15,
                                               env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'))
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(completed.stderr, b'')
                    text = completed.stdout.decode('utf-8')
                    if as_json:
                        value = json.loads(text)
                        self.assertEqual(value['documents'][-1]['policy'], 'retained')
                        text = value['prompt']
                    self.assertIn(original, text)
                    self.assertEqual({name: (self.root / name).read_bytes() for name in ENTRIES.values()}, before)
