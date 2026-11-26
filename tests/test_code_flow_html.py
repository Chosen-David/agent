import json
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
            source.write_text(json.dumps(graph))
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), '--out',
                                     str(root / 'out')], capture_output=True, text=True)
            html = (root / 'out/index.html').read_text() if (root / 'out/index.html').exists() else ''
            svg = (root / 'out/flow.svg').read_text() if (root / 'out/flow.svg').exists() else ''
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

    def test_packaged_source_example_exports_valid_svg(self):
        import xml.etree.ElementTree as ET
        graph = json.loads((SCRIPT.parent.parent / 'references/flow.example.json').read_text())
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
