from tests.document_fixture import DocumentFixtureCase
from tests.test_serial_recovery import SerialRecoveryTests as _SerialRecoveryTests
from tests.test_project_docs_init import ProjectDocumentInitTests as _ProjectDocumentInitTests


class SerialRecoveryTests(DocumentFixtureCase, _SerialRecoveryTests):
    pass


class ProjectDocumentInitTests(DocumentFixtureCase, _ProjectDocumentInitTests):
    pass

del _SerialRecoveryTests, _ProjectDocumentInitTests
