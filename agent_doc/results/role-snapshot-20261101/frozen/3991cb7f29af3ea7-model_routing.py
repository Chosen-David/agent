"""Role preferences resolved against a trusted host's available model inventory.

No provider credentials, implicit discovery or task retries. Availability is a
host assertion, not inferred from a model name or environment-variable presence.
"""
from __future__ import annotations

import json
import re


EMPTY_INVENTORY = {'schema_version': 1, 'models': []}
CAPABILITIES = {'tools', 'vision'}


def _name(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/\[\]-]{0,199}', value)


def validate_inventory(value):
    """Reject malformed inventories and unexpected fields, including credentials."""
    if (not isinstance(value, dict) or set(value) != {'schema_version', 'models'}
            or type(value['schema_version']) is not int or value['schema_version'] != 1
            or not isinstance(value['models'], list) or len(value['models']) > 256):
        raise ValueError('invalid model inventory')
    seen = set()
    fields = {'provider', 'model', 'available', 'capabilities', 'transport'}
    for entry in value['models']:
        if (not isinstance(entry, dict) or set(entry) != fields
                or not _name(entry['provider']) or not _name(entry['model'])
                or type(entry['available']) is not bool
                or entry['transport'] not in ('native', 'adapter')
                or not isinstance(entry['capabilities'], list)
                or any(not isinstance(c, str) or c not in CAPABILITIES for c in entry['capabilities'])):
            raise ValueError('invalid inventory entry; use model metadata only')
        identity = (entry['provider'], entry['model'])
        if identity in seen:
            raise ValueError('duplicate inventory model')
        seen.add(identity)
    return json.loads(json.dumps(value))


def validate_policy(policy):
    if (not isinstance(policy, dict) or policy.get('schema_version') != 1
            or policy.get('fallback') != 'inherit' or not isinstance(policy.get('models'), dict)
            or not isinstance(policy.get('roles'), dict)):
        raise ValueError('invalid role model policy')
    for model in policy['models'].values():
        if (not isinstance(model, dict) or set(model) != {'provider', 'model'}
                or not all(_name(model[k]) for k in ('provider', 'model'))):
            raise ValueError('invalid policy model')
    for name, role in policy['roles'].items():
        if (not _name(name) or not isinstance(role, dict)
                or not isinstance(role.get('candidates'), list)
                or not role['candidates'] or len(role['candidates']) > 16
                or any(not isinstance(c, str) or c not in policy['models'] for c in role['candidates'])
                or not isinstance(role.get('requires'), list)
                or any(not isinstance(c, str) or c not in CAPABILITIES for c in role['requires'])):
            raise ValueError('invalid policy role')
    return policy


def resolve(policy, role, inventory=None, *, adapter_available=False, requires=()):
    """Select before execution; unknown access/capabilities preserve host default."""
    validate_policy(policy)
    if role not in policy['roles']:
        raise ValueError('unknown role')
    if any(c not in CAPABILITIES for c in requires):
        raise ValueError('unknown required capability')
    inventory = validate_inventory(EMPTY_INVENTORY if inventory is None else inventory)
    requirement = sorted(set(policy['roles'][role]['requires']) | set(requires))
    entries = {(m['provider'], m['model']): m for m in inventory['models']}
    skipped = []
    for candidate in policy['roles'][role]['candidates']:
        model = policy['models'][candidate]
        entry = entries.get((model['provider'], model['model']))
        reason = None
        if entry is None or not entry['available']:
            reason = 'unavailable_or_unknown'
        elif not set(requirement).issubset(entry['capabilities']):
            reason = 'missing_capability'
        elif entry['transport'] == 'adapter' and not adapter_available:
            reason = 'adapter_missing'
        if reason:
            skipped.append({'candidate': candidate, 'reason': reason})
            continue
        return {'role': role, 'provider': entry['provider'], 'model': entry['model'],
                'transport': entry['transport'], 'fallback': False, 'requires': requirement,
                'availability': 'host_declared', 'skipped': skipped}
    return {'role': role, 'provider': None, 'model': None, 'transport': 'native',
            'fallback': True, 'requires': requirement, 'availability': 'default_unverified',
            'skipped': skipped}


def routing_report(policy, inventory=None):
    return {'schema_version': 1, 'live_model_tested': False,
            'routes': {role: resolve(policy, role, inventory) for role in policy['roles']}}


def dispatch(policy, role, inventory, request, *, native, adapter=None, requires=()):
    """Invoke exactly one trusted handler. Execution exceptions propagate unchanged.

    Handlers own provider authentication, permissions, budget, tool execution and
    identity evidence. A different model does not establish independent review.
    """
    route = resolve(policy, role, inventory, adapter_available=adapter is not None, requires=requires)
    handler = adapter if route['transport'] == 'adapter' else native
    return route, handler({**request, 'operation': 'run', 'route': route})
