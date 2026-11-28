"""Peak incremental storage for an adapter-supplied concurrent allocation plan."""
import os
import shutil
from pathlib import Path


def storage_budget(root, plan):
    """Existing retained allocations already reduce free space; list only new ones.

    A phase lists allocations that can coexist, including asynchronous saves,
    replacement temporaries and staging. Shared allocations use one identity.
    """
    if not isinstance(plan.get('available', {}), dict):
        raise ValueError('available must map staging resources to capacities')
    allocations = plan.get('allocations')
    phases = plan.get('phases')
    if not isinstance(allocations, dict) or not isinstance(phases, list) or not phases:
        raise ValueError('allocations and at least one phase required')
    units = ('disk_bytes', 'inodes', 'cpu_bytes', 'pinned_bytes')
    if 'gpu_bytes' in plan.get('available', {}) or any(
            isinstance(item, dict) and 'gpu_bytes' in item for item in allocations.values()):
        units += ('gpu_bytes',)
    peak = dict.fromkeys(units, 0)
    used = set()
    for phase in phases:
        if not isinstance(phase, list) or any(type(name) is not str for name in phase):
            raise ValueError('phase must list allocation identities')
        if len(set(phase)) != len(phase):
            raise ValueError('duplicate allocation in phase')
        total = dict.fromkeys(units, 0)
        for name in phase:
            item = allocations.get(name)
            if not name or not isinstance(item, dict) or set(item) != set(units):
                raise ValueError('each allocation requires all four resource quantities')
            used.add(name)
            for unit in units:
                amount = item[unit]
                if type(amount) is not int or amount < 0:
                    raise ValueError('allocation must use nonnegative integer quantities')
                total[unit] += amount
        for unit in units:
            peak[unit] = max(peak[unit], total[unit])
    if used != set(allocations):
        raise ValueError('unaccounted allocation')
    path = Path(root).resolve(strict=True)
    capacity = {'disk_bytes': shutil.disk_usage(path).free, 'inodes': None}
    if hasattr(os, 'statvfs'):
        fs = os.statvfs(path)
        if fs.f_files:
            capacity['inodes'] = fs.f_favail
    for unit in (key for key in units if key.endswith('_bytes') and key != 'disk_bytes'):
        value = plan.get('available', {}).get(unit)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError('invalid staging capacity')
        capacity[unit] = value
    blocked = [unit for unit in units if peak[unit] and
               (capacity[unit] is None or peak[unit] > capacity[unit])]
    return {'status': 'blocked' if blocked else 'fits', 'estimated_peak_increment': peak,
            'available': capacity, 'limiting_or_unknown': blocked, 'destination': str(path)}
