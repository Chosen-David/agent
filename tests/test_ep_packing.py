"""Fractional-slot packing invariants and failures; CPU fixtures, not GPU execution."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from agent_runtime.ep_packing import PlanningError, plan_packing

ROOT = Path(__file__).resolve().parents[1]
GIB = 1024**3


class EpPackingTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'examples/ep_packing.json').read_text())

    def run_plan(self, **kwargs):
        return plan_packing(**self.data, now=1001, **kwargs)

    def test_fixture_replay_deterministic(self):
        out1, out2 = self.run_plan(), self.run_plan()
        self.assertEqual(out1, out2)
        self.assertEqual(out1['status'], 'advisory-only')
        got = {p['job_id']: (p['host_id'], p['gpu_uuid']) for p in out1['placements']}
        self.assertEqual(got, {
            'gov-sim-arm1': ('gpu-a', 'GPU-a0'),
            'gov-arm2': ('gpu-a', 'GPU-a1'),
            'repo-arm3': ('gpu-b', 'GPU-b0'),
            'mu-arm6': ('gpu-b', 'GPU-b0'),
            'qasper-arm4': ('gpu-b', 'GPU-b0'),
        })
        reasons = {b['job_id']: b['reason'] for b in out1['blocked']}
        self.assertEqual(reasons, {
            'qasper-arm5': 'no-feasible-gpu',
            'huge-arm8': 'memory-exceeds-any-gpu',
            'dep-arm9': 'dependencies-unverified',
        })

    def test_memory_never_overflows(self):
        out = self.run_plan()
        usable = {g['uuid']: g['usable_memory_bytes']
                  for h in self.data['inventory']['hosts'] for g in h['gpus']}
        for p in out['placements']:
            self.assertLessEqual(p['gpu_memory_bytes'], usable[p['gpu_uuid']])

    def test_exclusive_isolation_both_directions(self):
        out = self.run_plan()
        by_gpu = {}
        for p in out['placements']:
            by_gpu.setdefault(p['gpu_uuid'], []).append(p)
        for uid, group in by_gpu.items():
            exclusive = [p for p in group if p['exclusive']]
            if exclusive:
                self.assertEqual(len(group), 1, f'{uid}: exclusive co-located')

    def test_lpt_first_placement_is_longest(self):
        out = self.run_plan()
        self.assertEqual(out['placements'][0]['job_id'], 'gov-sim-arm1')

    def test_unavailable_gpu_never_used(self):
        out = self.run_plan()
        self.assertNotIn('GPU-b1', {p['gpu_uuid'] for p in out['placements']})

    def test_verified_jobs_not_replanned(self):
        out = self.run_plan()
        self.assertNotIn('done-arm7', {p['job_id'] for p in out['placements']})
        self.assertNotIn('done-arm7', {b['job_id'] for b in out['blocked']})

    def test_dependency_satisfied_by_verified(self):
        data = deepcopy(self.data)
        data['verified_job_ids'] = ['done-arm7', 'qasper-arm4']
        data['jobs'] = [j for j in data['jobs'] if j['job_id'] != 'qasper-arm5']
        out = plan_packing(**data, now=1001)
        self.assertNotIn('dep-arm9', {b['job_id'] for b in out['blocked']})
        self.assertIn('dep-arm9', {p['job_id'] for p in out['placements']})

    def test_stale_inventory_rejected(self):
        with self.assertRaises(PlanningError):
            plan_packing(**self.data, now=2000)

    def test_unknown_field_rejected(self):
        data = deepcopy(self.data)
        data['jobs'][0]['shell'] = 'rm -rf /'
        with self.assertRaises(PlanningError):
            plan_packing(**data, now=1001)

    def test_duplicate_gpu_uuid_rejected(self):
        data = deepcopy(self.data)
        data['inventory']['hosts'][1]['gpus'][0]['uuid'] = 'GPU-a0'
        with self.assertRaises(PlanningError):
            plan_packing(**data, now=1001)

    def test_dependency_cycle_rejected(self):
        data = deepcopy(self.data)
        data['jobs'][3]['depends_on'] = ['dep-arm9']
        with self.assertRaises(PlanningError):
            plan_packing(**data, now=1001)

    def test_wave_limit(self):
        out = self.run_plan(max_placements=2)
        self.assertEqual(len(out['placements']), 2)
        self.assertTrue(any(b['reason'] == 'wave-limit' for b in out['blocked']))

    def test_utilization_gate_blocks_busy_gpu(self):
        # b0(util=62) 被门槛 50 拦截 → 共享 job 无处可去（a 卡被独占 job 先占）
        out = self.run_plan(max_shared_utilization=50)
        shared_placed = {p['job_id'] for p in out['placements'] if not p['exclusive']}
        self.assertEqual(shared_placed, set())
        reasons = {b['job_id']: b['reason'] for b in out['blocked']}
        self.assertEqual(reasons.get('repo-arm3'), 'no-feasible-gpu')
        # 门槛 70 放行 b0 → 恢复 fixture 基线
        out2 = self.run_plan(max_shared_utilization=70)
        self.assertIn('repo-arm3', {p['job_id'] for p in out2['placements']})

    def test_invalid_utilization_rejected(self):
        data = deepcopy(self.data)
        data['inventory']['hosts'][0]['gpus'][0]['utilization_percent'] = 120
        with self.assertRaises(PlanningError):
            plan_packing(**data, now=1001)

    def test_share_cap_per_gpu(self):
        out = self.run_plan(max_share_per_gpu=1)
        from collections import Counter
        shared_per_gpu = Counter(p['gpu_uuid'] for p in out['placements'] if not p['exclusive'])
        self.assertTrue(all(n <= 1 for n in shared_per_gpu.values()))
        # b0 只能再吃 1 个共享 job，其余共享 job 无处可去
        self.assertIn('no-feasible-gpu', {b['reason'] for b in out['blocked']})

    def test_contention_factor_inflates_load(self):
        plain = self.run_plan()
        infl = self.run_plan(contention_factor=2.0)
        self.assertIn('contention_factor', infl['placements'][-1])
        b0_plain = max(p['gpu_serial_seconds'] for p in plain['placements'] if p['gpu_uuid'] == 'GPU-b0')
        b0_infl = max(p['gpu_serial_seconds'] for p in infl['placements'] if p['gpu_uuid'] == 'GPU-b0')
        self.assertGreater(b0_infl, b0_plain)


if __name__ == '__main__':
    unittest.main()
