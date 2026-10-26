"""Process-identity byte parsing; no tmux or model backend is required."""
import io
import json
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_runtime.task_supervisor import read_process_starttime


ROOT = Path(__file__).resolve().parents[1]


def stat_record(comm=b'python', ticks=b'012345'):
    # Fields 3..21 precede the known field-22 oracle.
    suffix = [b'S', *([b'0'] * 18), ticks, b'0', b'0']
    return b'7 (' + comm + b') ' + b' '.join(suffix) + b'\n'


class ProcessIdentityTests(unittest.TestCase):
    def parse(self, data):
        def opened(path, mode='r', *, encoding=None):
            self.assertEqual(path, '/proc/7/stat')
            stream = io.BytesIO(data)
            return stream if mode == 'rb' else io.TextIOWrapper(stream, encoding=encoding)
        with patch('builtins.open', side_effect=opened):
            return read_process_starttime(7)

    def test_name_bytes_do_not_change_identity(self):
        for comm in (b'python', '进程'.encode(), b'\xffpid', b'a (b) c', b'line\nname'):
            with self.subTest(comm=comm):
                self.assertEqual(self.parse(stat_record(comm)), '012345')

    def test_malformed_identity_is_unavailable(self):
        for data in (b'', b'7 (short) S 0', b' '.join([b'0'] * 25),
                     *(stat_record(ticks=t) for t in (b'-1', b'+1', b'12x', b'\xff'))):
            with self.subTest(data=data):
                self.assertIsNone(self.parse(data))

    def test_read_errors_are_unavailable(self):
        for error in (FileNotFoundError(), PermissionError(), OSError(), ValueError()):
            with self.subTest(error=type(error).__name__), patch('builtins.open', side_effect=error):
                self.assertIsNone(read_process_starttime(7))

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux PR_SET_NAME/procfs control')
    def test_native_byte_names_preserve_start_ticks(self):
        script = r'''
import ctypes, json, os, re
from agent_runtime.task_supervisor import read_process_starttime
libc = ctypes.CDLL(None, use_errno=True)
prctl = libc.prctl
prctl.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
prctl.restype = ctypes.c_int
rows = []
for name in (b'pid plain)', b'utf8_\xc3\xa9)', b'\xff pid )\n'):
    assert 0 < len(name) <= 15 and b'\0' not in name
    buffer = ctypes.create_string_buffer(name + b'\0')
    if prctl(15, ctypes.cast(buffer, ctypes.c_char_p), 0, 0, 0) != 0:
        raise ctypes.WinError() if os.name == 'nt' else OSError(ctypes.get_errno(), 'PR_SET_NAME failed')
    row = {'name_hex': name.hex(), 'pid': os.getpid(),
           'actual': read_process_starttime(os.getpid())}
    for label, path in (('self', '/proc/self/stat'), ('numeric', '/proc/%s/stat' % os.getpid())):
        with open(path, 'rb') as stream:
            raw = stream.read(4097)
        assert len(raw) < 4097
        match = re.match(rb'^([0-9]+) \(.*\) [A-Za-z] (?:-?[0-9]+ ){18}([0-9]+)(?: |$)', raw, re.S)
        assert match and int(match[2]) > 0
        row[label] = {'record_pid': int(match[1]), 'ticks': match[2].decode('ascii'),
                      'comm_present': b'(' + name + b') ' in raw,
                      'bytes': len(raw)}
    rows.append(row)
print(json.dumps(rows))
'''
        started = time.monotonic()
        result = subprocess.run([sys.executable, '-B', '-c', script], cwd=ROOT,
                                capture_output=True, text=True, timeout=4)
        elapsed = time.monotonic() - started
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLessEqual(elapsed, 5)
        rows = json.loads(result.stdout)
        print('PID_NAME_OBSERVATIONS ' + result.stdout.strip())
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row['numeric']['comm_present'] and row['self']['comm_present']
                            and row['numeric']['record_pid'] == row['self']['record_pid'] == row['pid']
                            and row['numeric']['ticks'] == row['self']['ticks']
                            for row in rows), rows)
        self.assertEqual([row['actual'] for row in rows], [row['numeric']['ticks'] for row in rows], rows)


if __name__ == '__main__':
    unittest.main()
