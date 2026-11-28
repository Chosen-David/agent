import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from agent_runtime.verifier_registry import resolve


class VerifierRegistryTest(unittest.TestCase):
    def test_read_pinned_bytes_and_reject_changed_source(self):
        with TemporaryDirectory(dir=Path.home()) as directory:
            base = Path(directory)
            adapter = base/'adapter.py'
            adapter.write_text('def verify(root, manifest, plan):\n    return manifest["id"]\n')
            registry = base/'registry.json'
            registry.write_text(json.dumps({
                'schema':'host-verifiers/v1',
                'capabilities':{'test':{'path':str(adapter),'sha256':hashlib.sha256(adapter.read_bytes()).hexdigest()}}
            }))
            self.assertEqual(resolve(registry,'test')(None,{'id':'bound'},None),'bound')
            adapter.write_text("raise RuntimeError('must never execute')\n")
            with self.assertRaisesRegex(ValueError, 'changed'):
                resolve(registry,'test')
            with self.assertRaises(KeyError):
                resolve(registry,'unregistered')
