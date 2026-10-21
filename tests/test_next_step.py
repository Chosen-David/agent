"""Structured next footer: attach and validate the action/command/reason shape."""
import unittest

from agent_runtime.next_step import NextStepError, attach_next, validate_next


class NextStepTests(unittest.TestCase):
    def test_attach_next_normalizes_and_preserves_existing_keys(self):
        result = attach_next({'status': 'done'}, action='read changed docs',
                             command=None, reason='document_delta found changes')
        self.assertEqual(result['next'],
                         {'action': 'read changed docs', 'command': None,
                          'reason': 'document_delta found changes'})
        self.assertEqual(result['status'], 'done')

    def test_validate_next_roundtrips(self):
        footer = validate_next({'action': ' a ', 'command': 'run x', 'reason': ' r '})
        self.assertEqual(footer, {'action': 'a', 'command': 'run x', 'reason': 'r'})

    def test_command_is_optional_but_action_and_reason_are_required(self):
        with self.assertRaisesRegex(NextStepError, 'action must be'):
            validate_next({'action': ' ', 'command': None, 'reason': 'why'})
        with self.assertRaisesRegex(NextStepError, 'reason must be'):
            validate_next({'action': 'a', 'command': None, 'reason': ''})
        with self.assertRaisesRegex(NextStepError, 'command must be'):
            validate_next({'action': 'a', 'command': '', 'reason': 'why'})

    def test_footer_shape_and_overwrite_are_rejected(self):
        with self.assertRaisesRegex(NextStepError, 'exactly'):
            validate_next({'action': 'a'})
        with self.assertRaisesRegex(NextStepError, 'already carries'):
            attach_next({'next': {}}, action='a', reason='why')

    def test_non_dict_result_is_rejected(self):
        with self.assertRaisesRegex(NextStepError, 'dict'):
            attach_next([], action='a', reason='why')


if __name__ == '__main__':
    unittest.main()
