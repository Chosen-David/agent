"""Fresh-context review cases. CPU-only; an invalid-input failure is retained."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.cluster_planning import plan_wave, PlanningError, verify_local_artifact


def fixture():
    return json.loads((ROOT / 'examples/cluster_planning.json').read_text())


def run(data, **bounds):
    return plan_wave(**data, now=1001, **bounds)


class IndependentCases(unittest.TestCase):
    def test_conservation_many_cpu_requests(self):
        d = fixture()
        template = deepcopy(d['tasks'][-1])
        template.update(depends_on=[], runtime_seconds={'small': 1}, artifacts=[],
                        scratch_bytes_per_node=1, ram_bytes_per_node=1)
        for capacity in range(0, 9):
            with self.subTest(capacity=capacity):
                d['inventory']['hosts'][0]['cpu_slots'] = capacity
                d['tasks'] = [dict(deepcopy(template), task_id=f'cpu-{i}') for i in range(5)]
                out = run(d)
                self.assertEqual(len(out['placements']), min(5, capacity // 2))
                self.assertLessEqual(sum(a['cpu_slots'] for p in out['placements'] for a in p['allocations']), capacity)

    def test_two_gpus_whole_local_gang_no_partial(self):
        d = fixture()
        t = deepcopy(d['tasks'][2]); t.update(task_id='gang', nodes=1, gpus_per_node=2,
                                             gpu_models=['A10'], artifacts=[], depends_on=[])
        s = dict(deepcopy(t), task_id='single', gpus_per_node=1, priority=0)
        d['tasks'] = [t, s]
        d['inventory']['hosts'][0]['gpus'][1]['available'] = False
        out = run(d)
        self.assertEqual([p['task_id'] for p in out['placements']], ['single'])
        self.assertEqual(out['placements'][0]['allocations'][0]['gpu_uuids'], ['GPU-small-0'])

    def test_fabric_mismatch_blocks_homogeneous_gang(self):
        d = fixture(); d['tasks'] = [d['tasks'][0]]
        for g in d['inventory']['hosts'][2]['gpus']: g['fabric'] = 'pcie'
        self.assertEqual(run(d)['placements'], [])

    def test_dependencies_require_prior_verified_not_current_placement(self):
        d = fixture()
        parent = deepcopy(d['tasks'][2]); parent.update(task_id='parent', depends_on=[], artifacts=[])
        child = dict(deepcopy(parent), task_id='child', depends_on=['parent'], priority=0)
        d['tasks'] = [parent, child]; d['verified_task_ids'] = []
        self.assertEqual([p['task_id'] for p in run(d)['placements']], ['parent'])
        d['verified_task_ids'] = ['parent']
        self.assertEqual([p['task_id'] for p in run(d)['placements']], ['child'])

    def test_expiry_exact_and_future(self):
        d = fixture()
        for now in (1000 - .0001, 1120, math.nan, math.inf, True):
            with self.subTest(now=now), self.assertRaises(PlanningError):
                plan_wave(**d, now=now)
        self.assertEqual(plan_wave(**d, now=1119.999)['status'], 'advisory-only')

    def test_source_absence_requires_matching_destination_cache(self):
        d = fixture(); d['tasks'] = [d['tasks'][1]]
        d['tasks'][0]['runtime_seconds'] = {'large-a': 1}
        d['inventory']['artifacts']['synthetic-input']['source_hosts'] = []
        self.assertEqual(run(d)['placements'], [])
        d['inventory']['hosts'][1]['cache']['synthetic-input'] = '0' * 64
        self.assertEqual(run(d)['placements'][0]['transfers'], [])

    def test_source_hash_mismatch_rejected_before_cache_use(self):
        d = fixture(); d['inventory']['hosts'][0]['cache']['synthetic-input'] = '1' * 64
        with self.assertRaises(PlanningError): run(d)

    def test_exact_candidate_cap_and_overflow_distinguished(self):
        d = fixture(); d['tasks'] = [d['tasks'][2]]
        d['tasks'][0].update(artifacts=[], runtime_seconds={'small': 1})
        self.assertEqual(len(run(d, candidate_limit=1)['placements']), 1)
        d['tasks'][0]['runtime_seconds']['large-a'] = 2
        out = run(d, candidate_limit=1)
        self.assertEqual(out['blocked'][0]['reason'], 'search-limit')
        self.assertEqual(out['placements'], [])

    def test_gpu_ram_disk_independent_limits(self):
        d = fixture(); d['tasks'] = [d['tasks'][2]]
        d['tasks'][0].update(gpu_models=['A10'], artifacts=[], runtime_seconds={'small': 1})
        for key, request in [('ram_bytes','ram_bytes_per_node'), ('disk_bytes','scratch_bytes_per_node')]:
            x = deepcopy(d); x['inventory']['hosts'][0][key] = x['tasks'][0][request] - 1
            self.assertEqual(run(x)['placements'], [])
        d['tasks'][0]['gpu_memory_bytes'] = 24 * 1024**3 + 1
        self.assertEqual(run(d)['placements'], [])

    def test_fixture_costs_and_resources_against_explicit_arithmetic(self):
        out = run(fixture())
        expected = {'distributed-eval': 25 + 1 + 2 * (.001 + 1 / 1024),
                    'large-eval': 20 + 1 + .001 + 1 / 1024,
                    'small-eval': 25 + 1 + .001 + 1 / 1024}
        used = []
        for p in out['placements']:
            self.assertAlmostEqual(p['estimated_seconds'], expected[p['task_id']], places=12)
            for a in p['allocations']:
                self.assertEqual(a['disk_bytes'], 1024**3 + 1024**2)
                self.assertEqual(a['cpu_slots'], 2)
                self.assertEqual(a['ram_bytes'], 8 * 1024**3)
                used.extend(a['gpu_uuids'])
        self.assertEqual(len(used), 4)
        self.assertEqual(len(set(used)), 4)
        self.assertTrue(all(math.isfinite(p['estimated_seconds']) for p in out['placements']))

    def test_empty_task_list_does_not_invent_work(self):
        d = fixture(); d['tasks'] = []
        self.assertEqual(run(d)['placements'], [])
        self.assertEqual(run(d)['blocked'], [])

    def test_local_zero_bytes_and_parent_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); p = root / 'empty'; p.write_bytes(b'')
            sha = hashlib.sha256(b'').hexdigest()
            self.assertEqual(verify_local_artifact(p, sha256=sha, size_bytes=0)['size_bytes'], 0)
            (root / 'alias').symlink_to(root, target_is_directory=True)
            with self.assertRaises(PlanningError):
                verify_local_artifact(root/'alias'/'empty', sha256=sha, size_bytes=0)

    def test_json_decoder_depth_has_documented_invalid_cli_response(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'deep.json'; p.write_text('[' * 10000 + '0' + ']' * 10000)
            proc = subprocess.run([sys.executable, str(ROOT/'scripts/plan_cluster.py'), 'plan',
                                   '--input', str(p), '--now', '1001'], capture_output=True, text=True, timeout=3)
            print('DEEP_JSON_CLI_RETURN', proc.returncode)
            print('DEEP_JSON_CLI_STDOUT', proc.stdout)
            print('DEEP_JSON_CLI_STDERR', proc.stderr)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)['status'], 'invalid')
            self.assertEqual(proc.stderr, '')

    def test_huge_json_integer_has_documented_invalid_cli_response(self):
        d = fixture(); d['inventory']['observed_at'] = 10**309
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'huge.json'; p.write_text(json.dumps(d))
            proc = subprocess.run([sys.executable, str(ROOT/'scripts/plan_cluster.py'), 'plan',
                                   '--input', str(p), '--now', '1001'], capture_output=True, text=True, timeout=3)
            print('HUGE_INTEGER_CLI_RETURN', proc.returncode)
            print('HUGE_INTEGER_CLI_STDOUT', proc.stdout)
            print('HUGE_INTEGER_CLI_STDERR', proc.stderr)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)['status'], 'invalid')


if __name__ == '__main__': unittest.main(verbosity=2)
