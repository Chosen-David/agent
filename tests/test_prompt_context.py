import json
from pathlib import Path
import tempfile
import unittest
from agent_runtime.prompt_context import compose_entries, ENTRIES, MARKER
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
