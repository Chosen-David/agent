import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from agent_runtime.grid_context import grid_view, restore_grid_view, MAX_VALUE


class GridTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.path = 'grid.json'
        self.data = {'rule': 'pending current independent verification', 'coordinates': [100000 + i * 3 for i in range(64)], 'unit': 'ticks', 'unknown': {'failed': True, 'cancelled': ['old']}}
        self.write(self.data)

    def write(self, data):
        raw = json.dumps(data, ensure_ascii=False, indent=2).encode() + b'\r\n'
        (self.root/self.path).write_bytes(raw)
        self.sha = hashlib.sha256(raw).hexdigest()

    def view(self, **kwargs):
        return grid_view(self.root, self.path, self.sha, **kwargs)

    def restore(self, value):
        return restore_grid_view(self.root, json.dumps(value, ensure_ascii=False), self.path, self.sha)

    def test_complete_values_order_types_and_source_bytes(self):
        raw = (self.root/self.path).read_bytes()
        v = self.view()
        self.assertEqual(v['encoding'], 'arithmetic')
        self.assertEqual(json.dumps(self.restore(v)), json.dumps(self.data))
        self.assertEqual((self.root/self.path).read_bytes(), raw)
        self.assertEqual(self.restore(self.view(full=True)), self.data)

    def test_negative_step(self):
        self.data['coordinates'].reverse(); self.write(self.data)
        v = self.view(); self.assertEqual(v['data']['coordinates']['step'], -3)
        self.assertEqual(self.restore(v), self.data)

    def test_full_fallback_retains_every_value(self):
        for coordinates in ([], [1], [1,2], [1,2,3], [7]*64, [True,2,3], [1,2.0,3], [1,2,4], [MAX_VALUE+1+i for i in range(64)], [None, {}, 'x']):
            self.data['coordinates'] = coordinates; self.write(self.data)
            v = self.view(); self.assertEqual(v['encoding'], 'full')
            self.assertEqual(json.dumps(self.restore(v)), json.dumps(self.data))

    def test_step_outside_bound_falls_back(self):
        self.data['coordinates'] = [-MAX_VALUE, MAX_VALUE, -MAX_VALUE]; self.write(self.data)
        self.assertEqual(self.view()['encoding'], 'full')
        self.assertEqual(self.restore(self.view()), self.data)

    def test_signed_endpoints_restore_without_overflow_or_rounding(self):
        for start, step in ((MAX_VALUE, -1), (-MAX_VALUE, 1)):
            self.data['coordinates'] = [start+i*step for i in range(64)]; self.write(self.data)
            self.assertEqual(self.view()['encoding'], 'arithmetic')
            self.assertEqual(self.restore(self.view()), self.data)

    def test_tampered_start_step_count_and_shapes(self):
        for key, value in (('start',True), ('start',MAX_VALUE+1), ('start',100001), ('step',0), ('step',True), ('step',4), ('step',MAX_VALUE), ('count',True), ('count',2), ('count',65), ('count',50001)):
            v = self.view(); v['data']['coordinates'][key] = value
            with self.assertRaises(ValueError): self.restore(v)
        v = self.view(); v['data']['coordinates']['unknown'] = 1
        with self.assertRaises(ValueError): self.restore(v)

    def test_unchanged_values_do_not_allow_metadata_or_key_order_changes(self):
        v = self.view(); v['data']['unknown']['failed'] = False
        with self.assertRaises(ValueError): self.restore(v)
        v = self.view(); v['data'] = dict(reversed(list(v['data'].items())))
        with self.assertRaises(ValueError): self.restore(v)
        v = self.view(full=True); v['data']['coordinates'].reverse()
        with self.assertRaises(ValueError): self.restore(v)

    def test_frame_binding_and_unknown_keys(self):
        for key, value in (('project_root','foreign'), ('source',{}), ('scope','authority'), ('schema_version','v0'), ('encoding','unknown'), ('extra',True)):
            v = self.view(); v[key] = value
            with self.assertRaises(ValueError): self.restore(v)

    def test_stale_source_for_encoder_and_decoder(self):
        v = self.view(); (self.root/self.path).write_bytes(b'{}')
        with self.assertRaises(ValueError): self.view()
        with self.assertRaises(ValueError): self.restore(v)

    def test_strict_entire_source(self):
        for raw in (b'{"coordinates":[],"coordinates":[]}', b'{"coordinates":[],"x":NaN}', b'{"coordinates":[],"x":1e999}', b'{"coordinates":[],"x":"\\ud800"}', b'\xff', b'[]', b'{"coordinates":{}}'):
            (self.root/self.path).write_bytes(raw); self.sha = hashlib.sha256(raw).hexdigest()
            with self.assertRaises((ValueError, UnicodeError)): self.view()

    def test_invalid_serialized_frame(self):
        v = self.view(); text = json.dumps(v)
        for bad in (text[:-1], text+'{}', '[1]', text[:-1]+',"encoding":"full"}'):
            with self.assertRaises(ValueError): restore_grid_view(self.root, bad, self.path, self.sha)
        with self.assertRaises(ValueError): restore_grid_view(self.root, v, self.path, self.sha)

    def test_full_frame_list_shape_and_untouched_numeric_type(self):
        v = self.view(full=True); v['data']['coordinates'] = {}
        with self.assertRaises(ValueError): self.restore(v)
        v = self.view(full=True); v['data']['coordinates'][0] = float(v['data']['coordinates'][0])
        with self.assertRaises(ValueError): self.restore(v)

    def test_source_path_sha_root_boundaries(self):
        for path, sha in (('../grid.json',self.sha), (self.path,'BAD'), (self.path,'0'*64)):
            with self.assertRaises((ValueError,FileNotFoundError)): grid_view(self.root,path,sha)
        with self.assertRaises(ValueError): grid_view('.',self.path,self.sha)

    def test_flags_and_display_budget(self):
        for budget in (True,0,1000001,10):
            with self.assertRaises(ValueError): self.view(max_chars=budget)
        with self.assertRaises(ValueError): self.view(full=1)
        with self.assertRaises(ValueError): restore_grid_view(self.root,json.dumps(self.view()),self.path,self.sha,max_chars=10)

    def test_source_byte_and_count_caps(self):
        (self.root/self.path).write_bytes(b' '* (2*1024*1024+1)); self.sha = hashlib.sha256((self.root/self.path).read_bytes()).hexdigest()
        with self.assertRaises(ValueError): self.view()
        self.data['coordinates'] = [1]*50001; self.write(self.data)
        with self.assertRaises(ValueError): self.view()

    def test_encoded_input_does_not_bypass_expansion_budget(self):
        self.data['coordinates'] = [MAX_VALUE-i for i in range(50000)]
        self.data['padding'] = 'x'*250000; self.write(self.data)
        v = self.view(max_chars=1000000)
        self.assertEqual(v['encoding'], 'arithmetic')
        self.assertLess(len(json.dumps(v,separators=(',',':'))), 1000000)
        with self.assertRaisesRegex(ValueError, 'restored complete grid exceeds budget'):
            self.restore(v)

    def test_symlink_refusal(self):
        link = self.root/'link.json'
        try: link.symlink_to(self.root/self.path)
        except OSError: self.skipTest('host symlink unavailable')
        with self.assertRaises(ValueError): grid_view(self.root,'link.json',self.sha)

    def test_cli_full_and_compact_match_api(self):
        script = Path(__file__).resolve().parents[1]/'scripts/grid_context.py'
        for full in (False,True):
            cmd = [sys.executable,'-X','utf8',str(script),'--root',str(self.root),'--path',self.path,'--sha256',self.sha,'--compact'] + (['--full'] if full else [])
            out = subprocess.check_output(cmd)
            self.assertEqual(json.loads(out), self.view(full=full))

    def test_cli_enforces_exact_json_depth_boundary(self):
        script = Path(__file__).resolve().parents[1]/'scripts/grid_context.py'
        for optimized in (False, True):
            for depth, expected in ((256, 0), (257, 2)):
                raw = ('{"coordinates":[],"extra":' + '[' * depth + '0' +
                       ']' * depth + '}').encode()
                (self.root/self.path).write_bytes(raw)
                self.sha = hashlib.sha256(raw).hexdigest()
                cmd = [sys.executable] + (['-O'] if optimized else []) + [
                    str(script),'--root',str(self.root),'--path',self.path,
                    '--sha256',self.sha,'--compact']
                result = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                if expected:
                    self.assertIn('nesting', json.loads(result.stderr)['error'])


if __name__ == '__main__':
    unittest.main()
