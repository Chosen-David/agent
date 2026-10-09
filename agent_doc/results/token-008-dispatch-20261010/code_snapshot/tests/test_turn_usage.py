import copy,unittest
from agent_runtime.turn_usage import current_turn_usage
class TurnUsageTests(unittest.TestCase):
    def events(self):
        last={'inputTokens':100,'cachedInputTokens':30,'outputTokens':20,'reasoningOutputTokens':5,'totalTokens':120}
        total={'inputTokens':300,'cachedInputTokens':90,'outputTokens':60,'reasoningOutputTokens':15,'totalTokens':360}
        return [{'method':'turn/started','params':{'threadId':'child','turn':{'id':'now'}}},
          {'method':'thread/tokenUsage/updated','params':{'threadId':'child','turnId':'now','tokenUsage':{'last':last,'total':total}}},
          {'method':'turn/completed','params':{'threadId':'child','turn':{'id':'now','status':'completed','error':None,'items':[]}}}]
    def test_count_last_with_history_charged_once(self):
        e=self.events();before=copy.deepcopy(e);r=current_turn_usage(e,'child','now')
        self.assertEqual(r['total_tokens'],120);self.assertEqual(r['input_tokens'],100);self.assertEqual(r['cached_input_tokens'],30);self.assertEqual(e,before)
    def test_refuse_wrong_tool_early_duplicate_and_bad_counters(self):
        samples=[]
        e=self.events();e[1]['params']['turnId']='past';samples.append(e)
        e=self.events();e.append(e[-1]);samples.append(e)
        e=self.events();e[1],e[0]=e[0],e[1];samples.append(e)
        e=self.events();e[-1]['params']['turn']['items']=[{'type':'commandExecution'}];samples.append(e)
        for field,value in [('inputTokens',True),('cachedInputTokens',101),('totalTokens',121)]:
            e=self.events();e[1]['params']['tokenUsage']['last'][field]=value;samples.append(e)
        for e in samples:
            with self.assertRaises(ValueError):current_turn_usage(e,'child','now')
if __name__=='__main__':unittest.main()
