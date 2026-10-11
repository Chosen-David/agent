"""Opt-in host gate for acknowledged maintenance; never a scheduler or verifier.

The trusted observer must cover external events and deadlines outside report.
State is process-local: restart/replacement always performs the first call.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import threading
import time


@dataclass(frozen=True)
class MaintenanceOutcome:
    status: str

    def __post_init__(self):
        if self.status not in ('handled', 'pending', 'unchanged'):
            raise ValueError('unknown maintenance outcome')


def _json_value(value, depth=0, budget=None):
    budget = [0, 0] if budget is None else budget
    budget[0] += 1
    if budget[0] > 8192:
        raise ValueError('maintenance checkpoint node budget exceeded')
    if type(value) is str:
        budget[1] += len(value)
    elif type(value) is int:
        budget[1] += value.bit_length() * 30103 // 100000 + 2
    if budget[1] > 65536:
        raise ValueError('maintenance checkpoint character budget exceeded')
    if depth > 32:
        raise ValueError('maintenance checkpoint nesting exceeded')
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for child in value:
            _json_value(child, depth + 1, budget)
        return
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise ValueError('checkpoint object keys must be strings')
            _json_value(key, depth + 1, budget)
            _json_value(child, depth + 1, budget)
        return
    raise ValueError('checkpoint requires finite strict JSON values')


class MaintenanceGate:
    """Wrap build()['maintain'] explicitly, keeping worker/scheduler unchanged.

    Only MaintenanceOutcome('handled') acknowledges this exact observation.
    None/pending, exceptions and observations changed during handling never ACK.
    max_quiet_seconds bounds suppression; it does not replace wait/lease limits.
    observe() must be cheap, current and complete for the host's wake sources.
    """
    def __init__(self, maintain, observe, *, project_root, run_id,
                 max_quiet_seconds, clock=time.monotonic):
        if not callable(maintain) or not callable(observe) or not callable(clock):
            raise ValueError('trusted maintain/observe/clock callbacks required')
        root = Path(project_root).resolve(strict=True)
        if not root.is_dir() or type(run_id) is not str or not run_id:
            raise ValueError('project directory and run_id required')
        if type(max_quiet_seconds) not in (int, float) or not math.isfinite(max_quiet_seconds) or max_quiet_seconds <= 0:
            raise ValueError('positive finite quiet limit required')
        self.maintain, self.observe = maintain, observe
        self.project_root, self.run_id = str(root), run_id
        self.limit, self.clock = max_quiet_seconds, clock
        self._handled = None
        self._handled_at = None
        self._lock = threading.Lock()

    def _now(self):
        value = self.clock()
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('finite nonnegative clock required')
        return value

    def _fingerprint(self, report):
        if type(report) is not dict or report.get('run_id') != self.run_id:
            raise ValueError('maintenance report run mismatch')
        external = self.observe()
        if (type(external) is not dict or set(external) != {'project_root', 'run_id', 'events'}
                or external['project_root'] != self.project_root or external['run_id'] != self.run_id
                or type(external['events']) is not dict):
            raise ValueError('host checkpoint project/run/events binding required')
        # Bound traversal/characters before copying or serializing host data.
        _json_value({'report': report, 'external': external})
        view = deepcopy(report)
        # Only publish()'s top-level presentation timestamp is omitted.
        view.pop('updated_at', None)
        value = {'report': view, 'external': external}
        _json_value(value)
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf-8')
        if len(encoded) > 65536:
            raise ValueError('maintenance checkpoint byte budget exceeded')
        return hashlib.sha256(encoded).hexdigest()

    def __call__(self, report):
        if not self._lock.acquire(blocking=False):
            raise RuntimeError('maintenance already in flight')
        try:
            before = self._fingerprint(report)
            now = self._now()
            if (before == self._handled and self._handled_at is not None
                    and 0 <= now - self._handled_at < self.limit):
                return MaintenanceOutcome('unchanged')
            # Clear ACK before invoking: pending/failure after a forced refresh
            # must not fall back to a previously handled observation.
            self._handled = self._handled_at = None
            outcome = self.maintain(deepcopy(report))
            after = self._fingerprint(report)
            end = self._now()
            if (type(outcome) is MaintenanceOutcome and outcome.status == 'handled'
                    and before == after and end >= now):
                self._handled, self._handled_at = after, end
            return outcome
        except Exception:
            self._handled = self._handled_at = None
            raise
        finally:
            self._lock.release()
