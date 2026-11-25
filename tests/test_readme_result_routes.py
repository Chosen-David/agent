import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.result_store import METADATA_LIMIT, ResultStore
from agent_runtime.task_manifest import _prior_result_search, _review_prior_candidates


class ReadmeRoutes(unittest.TestCase):
    def test_legacy_routes_and_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'AGENT_DOC_ROOT': tmp + '/docs'}):
            home = Path(tmp, 'docs/results')
            for name in ('a', 'b', 'c'):
                (home / name).mkdir(parents=True)
            store = ResultStore(Path(tmp, 'code'))
            self.assertNotIn('readme_routes', store.search('optimizer'))
            index = home / 'README.md'
            index.write_text('| Directory | Contents |\n|---|---|\n| [a](./a/) | optimizer |\n| [x](a/) | optimizer trace |\n'
                             '| [b](b/) | optimizer trace |\n| [c](https://host/c/) | optimizer |\n'
                             '| [c](../c/) | optimizer |\n| [c](/c/) | optimizer |\n'
                             '| [c](%63/) | optimizer |\n| [c](c/nested/) | optimizer |\n')
            search = _prior_result_search(store, 'optimizer trace')
            routes = search['readme_routes']
            self.assertEqual([(r['directory'], r['line']) for r in routes], [('a', 4), ('b', 5)])
            self.assertEqual(store.search('optimizer', max_scan=1)['readme_routes'][0]['directory'], 'a')
            self.assertTrue(store.search('optimizer', limit=1)['partial'])
            self.assertEqual(search['results'], [])
            refs = [dict(directory=r['directory'], row_sha256=r['row_sha256'], decision='reject',
                         reason='different topology') for r in routes]
            task = {'produces_data': True, 'prior_result_review': dict(decision='rerun', reason='new scope',
                                                                       record_refs=[], readme_routes=refs)}
            _review_prior_candidates(task, search)
            for bad in [refs[:1], refs+refs[:1], [dict(refs[0], row_sha256='stale'), refs[1]],
                        [dict(refs[0], directory='outside'), refs[1]]]:
                task['prior_result_review']['readme_routes'] = bad
                with self.assertRaises(ValueError):
                    _review_prior_candidates(task, search)
            isolated = '| [a](./a/) | optimizer |'
            index.write_text(isolated + '\n\n```md\n| Dir | Info |\n|---|---|\n' + isolated + '\n```')
            with index.open('a') as stream:
                stream.write('\n\n    | Dir | Info |\n    |---|---|\n    ' + isolated)
            self.assertNotIn('readme_routes', store.search('optimizer'))
            with index.open('a') as stream:
                stream.write('\n\n| Dir | Info |\n|---|---|\n' + isolated)
            self.assertEqual([r['directory'] for r in store.search('optimizer')['readme_routes']], ['a'])
            for header in ['| Directory |', '| Directory | Contents ||']:
                index.write_text(header + '\n|---|---|\n' + isolated)
                self.assertNotIn('readme_routes', store.search('optimizer'))
            clean = {'results': [], 'partial': False, 'errors': []}
            task['prior_result_review']['readme_routes'] = refs
            with self.assertRaises(ValueError):
                _review_prior_candidates(task, clean)
            _review_prior_candidates({'produces_data': True}, clean)
            index.write_bytes(b'x' * (METADATA_LIMIT+1))
            self.assertTrue(store.search('optimizer')['partial'])
            index.unlink()
            index.symlink_to(Path(tmp, 'outside'))
            result = store.search('optimizer')
            self.assertNotIn('readme_routes', result)
            self.assertTrue(result['partial'])
            self.assertEqual(result['errors'][-1]['path'], 'agent_doc/results/README.md')
