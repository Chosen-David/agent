"""Offline native/JSONL shape rejection, with complete valid-output controls."""
import copy
import json
import unittest

from agent_runtime.token_usage import short_appserver_usage, short_probe_usage
from agent_runtime.turn_usage import current_turn_usage


def native_events():
    usage = dict(inputTokens=10, cachedInputTokens=2, outputTokens=3,
                 totalTokens=13, reasoningOutputTokens=1)
    return [
        {'method': 'turn/started', 'params': {'threadId': 'thread', 'turn': {'id': 'turn'}}},
        {'method': 'thread/tokenUsage/updated', 'params': {'threadId': 'thread', 'turnId': 'turn',
            'tokenUsage': {'last': usage.copy(), 'total': usage.copy()}}},
        {'method': 'turn/completed', 'params': {'threadId': 'thread',
            'turn': {'id': 'turn', 'status': 'completed', 'items': []}}},
    ]


def jsonl_events():
    return [{'type': 'thread.started', 'thread_id': 'thread'}, {'type': 'turn.started'},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'done'}},
            {'type': 'turn.completed', 'usage': {
                'input_tokens': 10, 'cached_input_tokens': 2, 'output_tokens': 3}}]


class UsageShapeTests(unittest.TestCase):
    def reject(self, parse, data):
        data = json.loads(json.dumps(data))
        before = copy.deepcopy(data)
        try:
            try:
                parse(data)
            except ValueError:
                pass
            except Exception as exc:
                self.fail('expected controlled ValueError, got ' + type(exc).__name__ + ': ' + str(exc))
            else:
                self.fail('malformed event accepted')
        finally:
            self.assertEqual(data, before)

    def test_native_wrong_containers_fail_controlled(self):
        paths = [(0,), (0, 'params'), (0, 'params', 'turn'), (1, 'params'),
                 (1, 'params', 'tokenUsage'), (1, 'params', 'tokenUsage', 'last'),
                 (1, 'params', 'tokenUsage', 'total'), (2, 'params'), (2, 'params', 'turn')]
        for parser in (short_appserver_usage, current_turn_usage):
            parse = lambda data: parser(data, 'thread', 'turn')
            for path in paths:
                for wrong in (None, False, 1, 'bad', []):
                    data = native_events()
                    parent = data
                    for key in path[:-1]:
                        parent = parent[key]
                    parent[path[-1]] = wrong
                    with self.subTest(parser=parser.__name__, path=path, wrong=wrong):
                        self.reject(parse, data)
            for wrong in (None, False, 1, 'bad', {}, [None], [False], [1], ['bad'], [[]]):
                data = native_events()
                data[-1]['params']['turn']['items'] = wrong
                with self.subTest(parser=parser.__name__, items=wrong):
                    self.reject(parse, data)
            for wrong in (None, False, 1, 'bad', []):
                data = native_events()
                data.insert(1, {'method': 'item/completed', 'params': {
                    'threadId': 'thread', 'turnId': 'turn', 'item': wrong}})
                with self.subTest(parser=parser.__name__, item=wrong):
                    self.reject(parse, data)
                data = native_events()
                data.insert(1, {'method': 'thread/tokenUsage/updated', 'params': {
                    'threadId': 'thread', 'turnId': 'turn', 'tokenUsage': wrong}})
                with self.subTest(parser=parser.__name__, earlier_snapshot=wrong):
                    self.reject(parse, data)

    def test_jsonl_wrong_item_containers_fail_controlled(self):
        for wrong in (None, False, 1, 'bad', []):
            data = jsonl_events()
            data[2]['item'] = wrong
            with self.subTest(item=wrong):
                self.reject(lambda rows: short_probe_usage(map(json.dumps, rows)), data)

    def test_native_complete_outputs_and_scope_preserved(self):
        for parser, source, scope in (
            (short_appserver_usage, 'Codex app-server final fresh-turn tokenUsage snapshot',
             'one no-tool inference turn; cache not subtracted; development/this chat excluded'),
            (current_turn_usage, 'native final current-turn tokenUsage.last; never cumulative summation or subtraction',
             'this one no-tool turn, including all history charged as current input; already paid parent actions excluded; cache not subtracted'),
        ):
            for zero in (False, True):
                data = native_events()
                if zero:
                    for bucket in ('last', 'total'):
                        data[1]['params']['tokenUsage'][bucket] = dict.fromkeys(
                            data[1]['params']['tokenUsage'][bucket], 0)
                # Unrelated metadata and omitted optional terminal items retain their scope.
                data.insert(0, {'method': 'heartbeat', 'params': {'threadId': 'thread', 'extra': None}})
                data[-1]['params']['turn'].pop('items')
                data = json.loads(json.dumps(data))
                before = copy.deepcopy(data)
                expected = dict(thread_id='thread', turn_id='turn', input_tokens=0 if zero else 10,
                    cached_input_tokens=0 if zero else 2, output_tokens=0 if zero else 3,
                    total_tokens=0 if zero else 13, reasoning_output_tokens=0 if zero else 1,
                    source=source, scope=scope)
                with self.subTest(parser=parser.__name__, zero=zero):
                    self.assertEqual(parser(data, 'thread', 'turn'), expected)
                    self.assertEqual(data, before)
        data = native_events()
        data[1]['params']['tokenUsage']['total'] = {
            k: v * 3 for k, v in data[1]['params']['tokenUsage']['total'].items()}
        before = copy.deepcopy(data)
        self.assertEqual(current_turn_usage(data, 'thread', 'turn')['total_tokens'], 13)
        self.assertEqual(data, before)
        with self.assertRaises(ValueError):
            short_appserver_usage(data, 'thread', 'turn')
        self.assertEqual(data, before)

    def test_jsonl_complete_output_preserved(self):
        for zero in (False, True):
            data = jsonl_events()
            if zero:
                data[-1]['usage'] = dict.fromkeys(data[-1]['usage'], 0)
            before = copy.deepcopy(data)
            self.assertEqual(short_probe_usage(map(json.dumps, data)), {
                'thread_id': 'thread', 'input_tokens': 0 if zero else 10,
                'cached_input_tokens': 0 if zero else 2, 'output_tokens': 0 if zero else 3,
                'total_tokens': 0 if zero else 13, 'source': 'Codex fresh single turn.completed server usage',
                'scope': 'whole short no-tool inference turn; cached input not subtracted; development/this chat excluded'})
            self.assertEqual(data, before)


if __name__ == '__main__':
    unittest.main()
