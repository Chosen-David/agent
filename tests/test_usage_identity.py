"""Usage must be attributable to real opaque thread and turn identities."""
import copy
import unittest

from agent_runtime.token_usage import short_appserver_usage
from agent_runtime.turn_usage import current_turn_usage


def events(thread_id="thread", turn_id="turn"):
    usage = dict(inputTokens=10, cachedInputTokens=2, outputTokens=3,
                 totalTokens=13, reasoningOutputTokens=1)
    return [
        {"method": "turn/started", "params": {
            "threadId": thread_id, "turn": {"id": turn_id}}},
        {"method": "thread/tokenUsage/updated", "params": {
            "threadId": thread_id, "turnId": turn_id,
            "tokenUsage": {"last": usage.copy(), "total": usage.copy()}}},
        {"method": "turn/completed", "params": {
            "threadId": thread_id, "turn": {
                "id": turn_id, "status": "completed", "items": []}}},
    ]


class UsageIdentityTests(unittest.TestCase):
    parsers = (short_appserver_usage, current_turn_usage)

    def test_invalid_matching_identities_are_rejected(self):
        for parser in self.parsers:
            for invalid in (None, "", 0, False, [], {}):
                for thread, turn in ((invalid, "turn"), ("thread", invalid)):
                    with self.subTest(parser=parser.__name__, thread=thread, turn=turn):
                        with self.assertRaises(ValueError):
                            parser(events(thread, turn), thread, turn)

    def test_absent_event_identities_are_rejected(self):
        data = events()
        for event in data:
            params = event["params"]
            params.pop("threadId")
            params.pop("turnId", None)
            params.get("turn", {}).pop("id", None)
        for parser in self.parsers:
            with self.subTest(parser=parser.__name__):
                with self.assertRaises(ValueError):
                    parser(data, None, None)

    def test_valid_opaque_identities_and_input_preserved(self):
        for parser in self.parsers:
            for thread, turn in (("thread", "turn"), ("线程/1", "轮次:2"), (" ", "0")):
                data = events(thread, turn)
                before = copy.deepcopy(data)
                result = parser(data, thread, turn)
                self.assertEqual((result["thread_id"], result["turn_id"]), (thread, turn))
                self.assertEqual(result["total_tokens"], 13)
                self.assertEqual(data, before)

    def test_mismatched_valid_identities_are_rejected(self):
        for parser in self.parsers:
            for thread, turn in (("other", "turn"), ("thread", "other")):
                with self.subTest(parser=parser.__name__, thread=thread, turn=turn):
                    with self.assertRaises(ValueError):
                        parser(events(), thread, turn)

    def test_invalid_identity_does_not_consume_events(self):
        def unavailable():
            raise AssertionError("must validate before reading event stream")
            yield
        for parser in self.parsers:
            with self.assertRaises(ValueError):
                parser(unavailable(), None, "turn")


if __name__ == "__main__":
    unittest.main()
