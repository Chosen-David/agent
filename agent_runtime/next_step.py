"""Structured next step: one executable follow-up attached to a result.

Absorbs npu_kernel_agent's ``next{action,command,reason}`` footer — a single,
validated follow-up on each deterministic result so a resumed consumer does not
re-derive "what now?". This module is the schema primitive; a result type opts
in by calling ``attach_next``. ``command`` is optional because library results
are not a CLI stage machine: an LLM-facing next step is often ``action`` +
``reason`` with no literal shell command.
"""
from __future__ import annotations

NEXT_SCHEMA = 'next-step/v1'


class NextStepError(ValueError):
    pass


def validate_next(footer):
    """Return the normalized ``next`` footer or raise for a malformed one."""
    if not isinstance(footer, dict) or set(footer) != {'action', 'command', 'reason'}:
        raise NextStepError('next footer must map action/command/reason exactly')
    action = footer.get('action')
    if not isinstance(action, str) or not action.strip():
        raise NextStepError('next action must be a nonempty string')
    command = footer.get('command')
    if command is not None and (not isinstance(command, str) or not command.strip()):
        raise NextStepError('next command must be a nonempty string or None')
    reason = footer.get('reason')
    if not isinstance(reason, str) or not reason.strip():
        raise NextStepError('next reason must be a nonempty string')
    return {'action': action.strip(), 'command': command, 'reason': reason.strip()}


def attach_next(result, *, action, command=None, reason):
    """Attach a validated ``next`` footer to a result dict, without overwriting."""
    if not isinstance(result, dict):
        raise NextStepError('result must be a dict to carry a next footer')
    if 'next' in result:
        raise NextStepError('result already carries a next footer; do not overwrite')
    result['next'] = validate_next({'action': action, 'command': command, 'reason': reason})
    return result
