"""Observable resource invariants and failures; CPU fixtures, not GPU execution."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.cluster_planning import PlanningError, plan_wave, verify_local_artifact

ROOT = Path(__file__).resolve().parents[1]
G = 1024**3


class ClusterPlanningTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'examples/cluster_planning.json').read_text())

    def run_plan(self, **kwargs):
        return plan_wave(**self.data, now=1001, **kwargs)

    def test_ready_wave_and_whole_gang(self):
        out = self.run_plan()
        self.assertEqual(out['status'], 'advisory-only')
        self.assertEqual(len(out['placements']), 3)
        distributed = out['placements'][0]
        self.assertEqual({a['host_id'] for a in distributed['allocations']}, {'large-a', 'large-b'})
        self.assertTrue(distributed['gang'])
        self.assertEqual(out['blocked'], [{'task_id': 'join', 'reason': 'dependencies-unverified'}])
        devices = [d for p in out['placements'] for a in p['allocations'] for d in a['gpu_uuids']]
        self.assertEqual(len(devices), len(set(devices)))
        for host in self.data['inventory']['hosts']:
            allocs = [a for p in out['placements'] for a in p['allocations'] if a['host_id'] == host['host_id']]
            self.assertLessEqual(sum(a['cpu_slots'] for a in allocs), host['cpu_slots'])
            self.assertLessEqual(sum(a['ram_bytes'] for a in allocs), host['ram_bytes'])
            self.assertLessEqual(sum(a['disk_bytes'] for a in allocs), host['disk_bytes'])

    def test_dependency_gate_and_completed_skip(self):
        self.data['verified_task_ids'] = []
        self.assertEqual(self.run_plan()['placements'], [])
        self.data['verified_task_ids'] = ['prepare-verified', 'distributed-eval']
        self.assertNotIn('distributed-eval', [p['task_id'] for p in self.run_plan()['placements']])

    def test_memory_cannot_be_summed_across_gpus(self):
        self.data['tasks'] = [self.data['tasks'][1]]
        self.data['tasks'][0]['gpu_models'] = ['A10']
        self.assertEqual(self.run_plan()['placements'], [])
        self.data['tasks'][0]['gpu_memory_bytes'] = 20*G
        self.assertEqual(self.run_plan()['placements'][0]['allocations'][0]['host_id'], 'small')

    def test_gang_failure_does_not_reserve_partial(self):
        self.data['inventory']['hosts'][2]['capabilities'] = ['eval']
        out = self.run_plan()
        self.assertEqual(out['blocked'][0]['reason'], 'no-feasible-candidate')
        self.assertTrue(any(p['task_id'] == 'large-eval' for p in out['placements']))
        self.assertEqual(out['placements'][0]['allocations'][0]['gpu_uuids'], ['GPU-large-a-0'])

    def test_directional_rdma_links_required(self):
        for case in ('missing', 'tcp', 'slow'):
            with self.subTest(case=case):
                inv = deepcopy(self.data['inventory'])
                link = next(l for l in inv['links'] if l['source'] == 'large-a' and l['destination'] == 'large-b')
                if case == 'missing':
                    inv['links'].remove(link)
                elif case == 'tcp':
                    link['transport'] = 'tcp'
                else:
                    link['bytes_per_second'] = 100
                out = plan_wave(inv, self.data['tasks'], verified_task_ids=['prepare-verified'], now=1001)
                self.assertEqual(out['blocked'][0]['reason'], 'no-feasible-candidate')

    def test_cpu_ram_and_disk_limits(self):
        self.data['tasks'] = [self.data['tasks'][2]]
        task = self.data['tasks'][0]
        task['gpu_models'] = ['A10']
        host = self.data['inventory']['hosts'][0]
        for key, value in [('cpu_slots', 1), ('ram_bytes', G), ('disk_bytes', 1)]:
            with self.subTest(key=key):
                before = host[key]
                host[key] = value
                self.assertFalse(self.run_plan()['placements'])
                host[key] = before

    def test_wave_cpu_accounting_blocks_second_gpu_job(self):
        task = deepcopy(self.data['tasks'][2])
        task['gpu_models'] = ['A10']
        second = deepcopy(task)
        second['task_id'] = 'second-eval'
        self.data['tasks'] = [task, second]
        self.data['inventory']['hosts'][0]['cpu_slots'] = 2
        out = self.run_plan()
        self.assertEqual(len(out['placements']), 1)
        self.assertEqual(out['blocked'][0]['reason'], 'no-feasible-candidate')

    def test_gang_model_mismatch_and_unavailable_gpu(self):
        for gpu in self.data['inventory']['hosts'][2]['gpus']:
            gpu['model'] = 'H200'
        self.assertEqual(self.run_plan()['blocked'][0]['reason'], 'no-feasible-candidate')
        self.data['tasks'] = [self.data['tasks'][2]]
        self.data['tasks'][0]['gpu_models'] = ['A10']
        for gpu in self.data['inventory']['hosts'][0]['gpus']:
            gpu['available'] = False
        self.assertFalse(self.run_plan()['placements'])

    def test_staging_size_and_wrong_destination_cache(self):
        self.data['tasks'] = [self.data['tasks'][1]]
        task = self.data['tasks'][0]
        task['runtime_seconds'] = {'large-a': 1}
        host = self.data['inventory']['hosts'][1]
        host['disk_bytes'] = task['scratch_bytes_per_node']
        host['cache']['synthetic-input'] = 'f'*64
        self.assertFalse(self.run_plan()['placements'])
        host['cache']['synthetic-input'] = '0'*64
        p = self.run_plan()['placements'][0]
        self.assertFalse(p['transfers'])
        self.assertEqual(p['allocations'][0]['disk_bytes'], task['scratch_bytes_per_node'])

    def test_cache_and_transfer_cost(self):
        self.data['tasks'] = [self.data['tasks'][2]]
        task = self.data['tasks'][0]
        task['runtime_seconds'] = {'small': 1, 'large-a': 1}
        out = self.run_plan()['placements'][0]
        self.assertEqual(out['allocations'][0]['host_id'], 'small')
        self.assertEqual(out['transfers'], [])
        task['gpu_models'] = ['H100']
        out = self.run_plan()['placements'][0]
        self.assertAlmostEqual(out['estimated_seconds'], 2 + .001 + 1/1024)
        self.assertEqual(out['transfers'][0]['destination_host'], 'large-a')
        self.data['inventory']['links'] = []
        self.assertFalse(self.run_plan()['placements'])

    def test_source_hash_and_unknown_artifacts(self):
        inv = self.data['inventory']
        inv['hosts'][0]['cache']['synthetic-input'] = 'f'*64
        with self.assertRaisesRegex(PlanningError, 'source hash'):
            self.run_plan()
        inv['hosts'][0]['cache']['synthetic-input'] = '0'*64
        self.data['tasks'][0]['artifacts'] = ['not-listed']
        with self.assertRaisesRegex(PlanningError, 'unknown input'):
            self.run_plan()

    def test_time_and_numeric_validation(self):
        for time in (999, 1120, float('nan'), True, 10**309):
            with self.subTest(time=time), self.assertRaises(PlanningError):
                plan_wave(**self.data, now=time)
        for bad in (-1, True, float('inf')):
            with self.subTest(bad=bad):
                task = self.data['tasks'][0]
                before = task['gpu_memory_bytes']
                task['gpu_memory_bytes'] = bad
                with self.assertRaises(PlanningError):
                    self.run_plan()
                task['gpu_memory_bytes'] = before

    def test_huge_json_integers_reject_without_traceback(self):
        mutations = [
            lambda d: d['inventory'].update(observed_at=10**309),
            lambda d: d['inventory'].update(valid_for_seconds=10**309),
            lambda d: d['inventory']['links'][0].update(bytes_per_second=10**309),
            lambda d: d['tasks'][0].update(startup_seconds=10**309),
            lambda d: d['tasks'][0]['runtime_seconds'].update(small=10**309),
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'huge.json'
            for mutate in mutations:
                data = deepcopy(self.data)
                mutate(data)
                path.write_text(json.dumps(data))
                p = subprocess.run([sys.executable, str(ROOT/'scripts/plan_cluster.py'), 'plan',
                                    '--input', str(path), '--now', '1001'], capture_output=True, text=True)
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertEqual(json.loads(p.stdout)['status'], 'invalid')
                self.assertEqual(p.stderr, '')

    def test_identity_unknown_fields_and_cycles(self):
        before = deepcopy(self.data)
        for mutator in (
            lambda d: d['inventory']['hosts'][1]['gpus'][0].update(uuid='GPU-small-0'),
            lambda d: d['inventory']['hosts'][0]['gpus'][0].update(uuid='MIG-123'),
            lambda d: d['tasks'][0].update(shell='rm anything'),
            lambda d: d['tasks'][0].update(depends_on=['join']),
        ):
            self.data = deepcopy(before)
            mutator(self.data)
            with self.assertRaises(PlanningError):
                self.run_plan()

    def test_search_bound_distinct_from_infeasible(self):
        self.data['tasks'] = [self.data['tasks'][2]]
        out = self.run_plan(candidate_limit=1)
        self.assertEqual(out['blocked'][0]['reason'], 'search-limit')
        self.assertFalse(out['placements'])

    def test_snapshot_not_mutated_and_determinism(self):
        before = deepcopy(self.data)
        a = self.run_plan(max_inflight=1)
        b = self.run_plan(max_inflight=1)
        self.assertEqual(a, b)
        self.assertEqual(self.data, before)
        self.assertEqual(a['blocked'][0]['reason'], 'wave-limit')

    def test_cpu_only_job(self):
        self.data['tasks'] = [self.data['tasks'][-1]]
        self.data['tasks'][0]['depends_on'] = ['prepare-verified']
        p = self.run_plan()['placements'][0]
        self.assertEqual(p['allocations'][0]['gpu_uuids'], [])
        self.assertFalse(p['gang'])

    def test_verify_local_bytes_and_failure_edges(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'data'
            body = b'controlled-artifact'*100
            path.write_bytes(body)
            sha = hashlib.sha256(body).hexdigest()
            self.assertEqual(verify_local_artifact(path, sha256=sha, size_bytes=len(body))['status'], 'bytes-verified')
            for expected, size, cap in [(sha, len(body)-1, 10000), ('0'*64, len(body), 10000), (sha, len(body), 10)]:
                with self.assertRaises(PlanningError):
                    verify_local_artifact(path, sha256=expected, size_bytes=size, max_bytes=cap)
            link = Path(temp) / 'alias'
            link.symlink_to(path)
            with self.assertRaises(PlanningError):
                verify_local_artifact(link, sha256=sha, size_bytes=len(body))
            path.write_bytes(b'tampered' + body[8:])
            with self.assertRaises(PlanningError):
                verify_local_artifact(path, sha256=sha, size_bytes=len(body))

    def test_cli_and_malformed_json(self):
        cli = [sys.executable, str(ROOT/'scripts/plan_cluster.py'), 'plan', '--now', '1001', '--input']
        p = subprocess.run(cli + [str(ROOT/'examples/cluster_planning.json')], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout), self.run_plan())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'duplicate.json'
            path.write_text('{"inventory":{},"inventory":{}}')
            p = subprocess.run(cli + [str(path)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn('duplicate', p.stdout)
            fifo = Path(temp)/'pipe'
            os.mkfifo(fifo)
            p = subprocess.run(cli + [str(fifo)], capture_output=True, text=True, timeout=3)
            self.assertEqual(p.returncode, 2)
            self.assertIn('regular file', p.stdout)

    def test_deep_json_rejects_without_traceback(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'deep.json'
            path.write_text('['*10000 + '0' + ']'*10000)
            p = subprocess.run([sys.executable, str(ROOT/'scripts/plan_cluster.py'), 'plan',
                                '--input', str(path), '--now', '1001'], capture_output=True, text=True, timeout=3)
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertEqual(json.loads(p.stdout)['status'], 'invalid')
            self.assertEqual(p.stderr, '')


if __name__ == '__main__':
    unittest.main()
