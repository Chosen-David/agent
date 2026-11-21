import os
import unittest
from unittest.mock import patch


class DocumentFixtureCase(unittest.TestCase):
    def run(self, result=None):
        with patch.dict(os.environ):
            os.environ.pop("AGENT_DOC_ROOT", None)
            return super().run(result)
