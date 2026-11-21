from tests.document_fixture import DocumentFixtureCase
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.collaborative_flow import Flow


WORKFLOW = Path(os.environ["AGENT_TEST_PROJECT_ROOT"])


class ExternalFlowTests(DocumentFixtureCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name).resolve()
        self.project = base / 'code'
        self.project.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        subprocess.run(['git', '-C', str(self.project), 'remote', 'add', 'origin',
                        'https://example.invalid/example'], check=True)
        self.docs = base / 'agent_doc/example'
        self.suite = self.docs / 'test/FIX-01'
        self.suite.mkdir(parents=True)
        (self.suite / 'check.py').write_text('print("fixture")\n')
        self.manifest = {'version': 1, 'origin': 'https://example.invalid/example', 'checks': [
            {'id': 'acceptance', 'kind': 'python', 'path': 'check.py', 'timeout_seconds': 10,
             'requirement': 'Read the selected external acceptance suite'}]}
        (self.suite / 'suite.json').write_text(json.dumps(self.manifest))
        self.environment = patch.dict(os.environ, {'AGENT_DOC_ROOT': str(self.docs)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.flow = Flow(self.project, 'FIX-01')
        self.flow.create('Preserve the external acceptance binding')

    def prepare(self):
        try:
            self.flow.plan({'summary': 'Use existing external suite',
                            'steps': [{'id': 'fix', 'depends_on': []}]}, WORKFLOW, 'example')
        except (ValueError, OSError) as exc:
            self.fail(f'external acceptance planning refused: {exc}')

    def test_external_plan_and_recheck(self):
        self.prepare()
        self.flow.check_tests()
        self.assertEqual(self.flow.state['phase'], 'planned')
        self.assertTrue((self.docs / 'task/task_details/FIX-01.md').is_file())
        self.assertFalse((self.project / 'agent_doc').exists())

    def test_existing_anchor_without_environment(self):
        os.environ.pop('AGENT_DOC_ROOT')
        (self.project / 'agent_doc').symlink_to(self.docs, target_is_directory=True)
        self.prepare()
        self.flow.check_tests()
        self.assertTrue((self.project / 'agent_doc').is_symlink())

    def test_changed_external_check_requires_replanning(self):
        self.prepare()
        (self.suite / 'check.py').write_text('print("changed")\n')
        with self.assertRaisesRegex(ValueError, 'acceptance changed'):
            self.flow.check_tests()

    def test_changed_origin_refused_before_planning(self):
        self.manifest['origin'] = 'https://example.invalid/other'
        (self.suite / 'suite.json').write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, 'origin differs'):
            self.flow.plan({'summary': 'Use existing external suite',
                            'steps': [{'id': 'fix', 'depends_on': []}]}, WORKFLOW, 'example')


if __name__ == '__main__':
    unittest.main()
