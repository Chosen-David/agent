import hashlib
from pathlib import Path
import tempfile
import unittest

from agent_runtime.experiment_catalog import ExperimentCatalog
from agent_runtime.result_store import ResultStore


class CatalogTest(unittest.TestCase):
    def test_federated_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proof = root / 'old.log'
            proof.write_bytes(b'123')
            context = {'scope': 'matched start', 'execution': {'seed': 42}}
            ResultStore(root).register_history('older-name', 'original curve',
                [{'path': proof.name, 'sha256': hashlib.sha256(b'123').hexdigest()}], context=context)
            catalog = ExperimentCatalog(root / 'catalog.sqlite')
            try:
                self.assertEqual(catalog.scan(root)['refreshed'], 1)
                self.assertEqual(catalog.scan(root)['refreshed'], 0)
                self.assertEqual(catalog.find(context)[0]['decision'], 'verify_delta')
                self.assertEqual(catalog.find(dict(context, execution={'seed': 43})), [])
                proof.write_bytes(b'changed')
                self.assertEqual(catalog.find(context)[0]['validation_status'], 'stale')
            finally:
                catalog.db.close()
