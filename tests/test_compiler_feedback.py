"""Synthetic compiler-log fixtures; these tests never run or benchmark CUDA."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/research-assistant/skills/research-implement-optimize/scripts/compiler_feedback.py'
spec = importlib.util.spec_from_file_location('compiler_feedback', SCRIPT)
feedback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feedback)


def entry(name='synthetic_a', arch='sm_90'):
    return f"ptxas info    : Compiling entry function '{name}' for '{arch}'\nptxas info    : Function properties for {name}\n"


class CompilerFeedbackTests(unittest.TestCase):
    def test_separate_functions_targets_and_provenance(self):
        raw = (entry() + '    32 bytes stack frame, 16 bytes spill stores, 8 bytes spill loads\n'
               'ptxas info : Used 96 registers, 2048 bytes smem, 360 bytes cmem[0]\n'
               + entry('synthetic_b', 'sm_100a') + '    0 bytes stack frame, 0 bytes spill stores, 0 bytes spill loads\n'
               'ptxas info : Used 64 registers, 0 bytes smem\n').encode()
        result = feedback.parse_log(raw)
        a, b = result['records']
        self.assertEqual(a['metrics'], {'registers_per_thread': 96, 'static_shared_bytes': 2048,
                                       'stack_frame_bytes': 32, 'spill_store_bytes': 16, 'spill_load_bytes': 8})
        self.assertEqual((b['function'], b['target'], b['metrics']['spill_load_bytes']), ('synthetic_b', 'sm_100a', 0))
        self.assertEqual(a['observations'][0]['line'], 3)
        self.assertEqual(a['observations'][-1]['line'], 4)
        self.assertEqual(result['log_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['parse_status'], 'parsed')
        self.assertIsNone(result['compile_success'])
        self.assertEqual(result['performance_verdict'], 'not_measured')

    def test_absence_is_unknown_not_zero(self):
        r = feedback.parse_log((entry() + 'ptxas info : Used 72 registers\n').encode())
        self.assertEqual(r['parse_status'], 'partial')
        self.assertIsNone(r['records'][0]['metrics']['static_shared_bytes'])
        self.assertIsNone(r['records'][0]['metrics']['spill_load_bytes'])

    def test_repeated_name_is_not_merged(self):
        r = feedback.parse_log((entry() + 'ptxas info : Used 72 registers\n' + entry() +
                                'ptxas info : Used 80 registers\n').encode())
        self.assertEqual([v['metrics']['registers_per_thread'] for v in r['records']], [72, 80])
        self.assertEqual([v['ordinal'] for v in r['records']], [1, 2])

    def test_device_function_does_not_inherit_arch_or_fields(self):
        r = feedback.parse_log((entry() + 'ptxas info : Used 72 registers\n'
                                'ptxas info : Function properties for helper\n'
                                '    16 bytes stack frame, 0 bytes spill stores, 0 bytes spill loads\n').encode())
        helper = r['records'][1]
        self.assertIsNone(helper['target'])
        self.assertIsNone(helper['metrics']['registers_per_thread'])
        self.assertEqual(helper['metrics']['stack_frame_bytes'], 16)
        self.assertEqual(helper['metrics']['spill_store_bytes'], 0)

    def test_conflicting_metrics_never_choose_last(self):
        r = feedback.parse_log((entry() + 'ptxas info : Used 72 registers\n'
                                'ptxas info : Used 80 registers\nptxas info : Used 72 registers\n').encode())
        record = r['records'][0]
        self.assertIsNone(record['metrics']['registers_per_thread'])
        self.assertEqual(record['conflicts'], ['registers_per_thread'])
        self.assertEqual([o['value'] for o in record['observations']], [72, 80, 72])

    def test_unknown_boundary_and_orphan_metrics(self):
        r = feedback.parse_log((entry() + 'ptxas info : Used 72 registers\n'
                                'ptxas info : Compiling entry function "new-format"\n'
                                'ptxas info : Used 80 registers\n').encode())
        self.assertEqual(r['records'][0]['metrics']['registers_per_thread'], 72)
        self.assertEqual([i['reason'] for i in r['issues']], ['unrecognized_function_boundary', 'unscoped_metrics'])

    def test_errors_and_unrelated_text_not_success_or_metrics(self):
        r = feedback.parse_log((entry() + 'random build message: Used 800 registers, 99 bytes smem\n'
                                'ptxas fatal : insufficient resources\n').encode())
        self.assertEqual(r['parse_status'], 'partial')
        self.assertIsNone(r['records'][0]['metrics']['registers_per_thread'])
        self.assertEqual(r['diagnostics'][0]['severity'], 'fatal')
        self.assertIsNone(r['compile_success'])
        self.assertEqual(feedback.parse_log(b'not a resource report')['parse_status'], 'no_records')

    def test_bounds_and_invalid_utf8(self):
        for raw in [b'\xff', b'x' * (feedback.MAX_BYTES + 1)]:
            with self.assertRaises(ValueError):
                feedback.parse_log(raw)

    def test_signed_decimal_and_thousands_are_not_integer_substrings(self):
        for number in ['-16', '1.5', '1,024', '+16', '1e3']:
            r = feedback.parse_log((entry() + f'ptxas info : Used 64 registers, {number} bytes smem\n').encode())
            self.assertIsNone(r['records'][0]['metrics']['static_shared_bytes'], number)

    def test_truncated_or_changed_info_clears_scope(self):
        for boundary in ['Compiling entry funct', "Compiling  entry function 'b' for 'sm_90'",
                         'Function proper', 'new diagnostic format']:
            r = feedback.parse_log((entry() + 'ptxas info : ' + boundary + '\n'
                                    'ptxas info : Used 80 registers\n').encode())
            self.assertIsNone(r['records'][0]['metrics']['registers_per_thread'], boundary)
            self.assertEqual(r['issues'][-1]['reason'], 'unscoped_metrics')

    def test_crlf_source_hash_and_cli_outside_repository(self):
        raw = (entry() + 'ptxas info : Used 72 registers\n').replace('\n', '\r\n').encode()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'input.log'; p.write_bytes(raw)
            result = subprocess.run([sys.executable, str(SCRIPT), str(p)], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['log_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(list(Path(tmp).iterdir()), [p])
            self.assertEqual(p.read_bytes(), raw)
            bad = subprocess.run([sys.executable, str(SCRIPT), str(p)+'-missing'], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, '')


if __name__ == '__main__':
    unittest.main()
