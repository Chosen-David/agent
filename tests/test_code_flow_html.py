import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/research-assistant/skills/code-reading/scripts/render_flow.py'


class CodeFlowHTMLTests(unittest.TestCase):
    def run_cli(self, graph):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'flow.json'
            source.write_text(json.dumps(graph), encoding='utf-8')
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), '--out',
                                     str(root / 'out')], capture_output=True, text=True, encoding='utf-8')
            html = (root / 'out/index.html').read_text(encoding='utf-8') if (root / 'out/index.html').exists() else ''
            svg = (root / 'out/flow.svg').read_text(encoding='utf-8') if (root / 'out/flow.svg').exists() else ''
            return result, html, svg

    def graph(self):
        evidence = {'commit': 'a' * 40, 'path': 'module.py', 'symbol': 'run',
                    'start_line': 1, 'end_line': 4}
        return {'title': '<script>alert(1)</script>', 'nodes': [
            {'id': 'input', 'label': '输入', 'kind': 'source_fact', 'detail': '真实入口', 'evidence': [evidence]},
            {'id': 'output', 'label': '输出', 'kind': 'unknown', 'detail': '运行状态未验证', 'evidence': [evidence]}],
            'edges': [{'source': 'input', 'target': 'output', 'label': 'x → y',
                       'kind': 'static_inference', 'condition': 'x 非空', 'evidence': [evidence]}]}

    def test_real_cli_exports_offline_escaped_evidence(self):
        result, html, svg = self.run_cli(self.graph())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>alert', html)
        self.assertIn('<details', html)
        self.assertIn('静态推断', svg)
        self.assertIn('x 非空', html)
        self.assertIn('module.py', html)
        self.assertNotIn('https://', html)
        self.assertIn('viewBox=', svg)

    def test_repeat_preserves_identical_outputs_and_repairs_same_size_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = [sys.executable, str(SCRIPT),
                       str(SCRIPT.parent.parent / 'references/flow.example.json'), '--out', tmp]
            subprocess.run(command, check=True)
            page, svg = root / 'index.html', root / 'flow.svg'
            original = page.read_bytes()
            for path in (page, svg):
                os.utime(path, (1000000000, 1000000000))
            timestamp = svg.stat().st_mtime_ns
            subprocess.run(command, check=True)
            self.assertEqual(page.stat().st_mtime_ns, timestamp)
            page.write_bytes(b'!' + original[1:])
            subprocess.run(command, check=True)
            self.assertEqual(page.read_bytes(), original)
            self.assertEqual(svg.stat().st_mtime_ns, timestamp)

    def test_packaged_source_example_exports_valid_svg(self):
        import xml.etree.ElementTree as ET
        graph = json.loads((SCRIPT.parent.parent / 'references/flow.example.json').read_text(encoding='utf-8'))
        result, page, svg = self.run_cli(graph)
        self.assertEqual(result.returncode, 0, result.stderr)
        ET.fromstring(svg)
        self.assertIn('source_evidence.py', svg)
        self.assertIn('Python AST', page)

    def test_invalid_graphs_rejected_without_crash(self):
        for mutation in ('dangling', 'evidence', 'duplicate', 'kind'):
            graph = self.graph()
            if mutation == 'dangling':
                graph['edges'][0]['target'] = 'missing'
            elif mutation == 'evidence':
                graph['edges'][0]['evidence'] = []
            elif mutation == 'duplicate':
                graph['nodes'][1]['id'] = 'input'
            else:
                graph['nodes'][0]['kind'] = 'executed'
            result, _, _ = self.run_cli(graph)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('flow rejected:', result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_xml_forbidden_characters_rejected_before_export(self):
        for character in ('\x00', '\x01', '\x0b', '\x1f', '\ud800', '\ufffe', '\uffff'):
            for location in ('title', 'node', 'edge', 'evidence'):
                with self.subTest(character=repr(character), location=location):
                    graph = self.graph()
                    if location == 'title':
                        graph['title'] += character
                    elif location == 'node':
                        graph['nodes'][0]['label'] += character
                    elif location == 'edge':
                        graph['edges'][0]['condition'] += character
                    else:
                        graph['nodes'][0]['evidence'][0]['symbol'] += character
                    result, page, svg = self.run_cli(graph)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn('characters forbidden in XML', result.stderr)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertEqual((page, svg), ('', ''))

    def test_xml_legal_whitespace_and_unicode_preserved(self):
        import xml.etree.ElementTree as ET
        graph = self.graph()
        graph['title'] = '中文\t<&>\n\r\U0001f600'
        result, _, svg = self.run_cli(graph)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = ET.fromstring(svg)
        self.assertIn('中文', parsed.find('{http://www.w3.org/2000/svg}title').text)
        self.assertIn('\U0001f600', svg)

    def test_repeat_export_preserves_files_and_repairs_changed_outputs(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / 'flow.json'
            graph = self.graph()
            manifest.write_text(json.dumps(graph), encoding='utf-8')
            command = [sys.executable, str(SCRIPT), str(manifest), '--out', str(root / 'out')]
            def export():
                result = subprocess.run(command, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            export()
            files = [root / 'out/index.html', root / 'out/flow.svg']
            expected = [path.read_bytes() for path in files]
            timestamp = 1600000000000000000
            for path in files:
                os.utime(path, ns=(timestamp, timestamp))
            export()
            self.assertEqual([path.read_bytes() for path in files], expected)
            self.assertEqual([path.stat().st_mtime_ns for path in files], [timestamp] * 2)
            files[1].unlink()
            export()
            self.assertEqual(files[1].read_bytes(), expected[1])
            self.assertEqual(files[0].stat().st_mtime_ns, timestamp)
            files[0].write_bytes(b'corrupt')
            export()
            self.assertEqual(files[0].read_bytes(), expected[0])
            graph['title'] = 'Updated title'
            manifest.write_text(json.dumps(graph), encoding='utf-8')
            export()
            self.assertTrue(all(path.read_bytes() != previous for path, previous in zip(files, expected)))
