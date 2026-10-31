"""Capture unittest outcomes and its complete in-memory report together."""
import io
import json
from pathlib import Path
import traceback
import unittest


def capture(suite_factory, output):
    # Reserve a new artifact before running tests; never overwrite old evidence.
    with Path(output).open('x', encoding='utf-8') as target:
        stream = io.StringIO()
        record = {'completed': False, 'result': None, 'exception': None}
        try:
            suite = suite_factory()
            record['planned_methods'] = suite.countTestCases()
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
            record['result'] = {
                'tests_run': result.testsRun,
                'failures': [{'id': test.id(), 'traceback': text} for test, text in result.failures],
                'errors': [{'id': test.id(), 'traceback': text} for test, text in result.errors],
                'skipped': [{'id': test.id(), 'reason': reason} for test, reason in result.skipped],
                'expected_failures': [{'id': test.id(), 'traceback': text} for test, text in result.expectedFailures],
                'unexpected_successes': [test.id() for test in result.unexpectedSuccesses],
                'was_successful': result.wasSuccessful(),
            }
            record['completed'] = True
        except BaseException:
            record['exception'] = traceback.format_exc()
        finally:
            record['raw_unittest_report'] = stream.getvalue()
            json.dump(record, target, ensure_ascii=False, indent=2)
            target.write('\n')
    return record
