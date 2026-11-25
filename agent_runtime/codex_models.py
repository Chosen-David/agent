"""Discover capabilities, then ask the authenticated default model to choose roles."""
import json
import uuid

from .plan_review import _identity, sha

POLICY = 'default-model/v1'
EFFORTS = {'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max'}


def _name(value):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > 256:
        raise ValueError('canonical model/provider name required')
    return value


def model_effort(row):
    efforts = row.get('supportedReasoningEfforts')
    if not isinstance(efforts, list):
        raise ValueError('model has no advertised non-delegating reasoning effort')
    supported = [e['reasoningEffort'] for e in efforts
                 if isinstance(e, dict) and e.get('reasoningEffort') in EFFORTS]
    if not supported:
        raise ValueError('model has no advertised non-delegating reasoning effort')
    default = row.get('defaultReasoningEffort')
    return default if default in supported else supported[0]


def discover_models(client, cwd, *, writer_only=False):
    config = client.call('config/read', {'includeLayers': False, 'cwd': str(cwd)})['config']
    provider = config.get('model_provider')
    if provider is not None:
        _name(provider)
    models, aliases, defaults, seen = {}, {}, set(), set()
    advertisements, all_aliases = {}, {}
    cursor, total = None, 0
    for _ in range(10):
        params = {'limit': 100, 'includeHidden': False}
        if cursor is not None:
            params['cursor'] = cursor
        page = client.call('model/list', params)
        if not isinstance(page.get('data'), list):
            raise ValueError('model catalog missing')
        total += len(page['data'])
        if total > 100:
            raise ValueError('model catalog exceeds 100 entries; select an explicit pair')
        for row in page['data']:
            name = _name(row.get('model'))
            # Reconcile the entire advertised identity before filtering. An
            # incompatible/hidden duplicate must not erase a contradiction.
            entry = {k: row.get(k) for k in ('description', 'inputModalities',
                     'defaultReasoningEffort', 'supportedReasoningEfforts')}
            entry['hidden'] = bool(row.get('hidden'))
            for field in ('inputModalities', 'supportedReasoningEfforts'):
                if isinstance(entry[field], list):
                    entry[field] = sorted(entry[field], key=lambda value: json.dumps(value, sort_keys=True))
            if name in advertisements and advertisements[name] != entry:
                raise ValueError('conflicting canonical model capabilities')
            advertisements[name] = entry
            row_aliases = (name, _name(row.get('id', name)))
            for alias in row_aliases:
                if alias in all_aliases and all_aliases[alias] != name:
                    raise ValueError('ambiguous model alias')
                all_aliases[alias] = name
            modalities = row.get('inputModalities')
            if (row.get('hidden') or not isinstance(modalities, list) or 'text' not in modalities or
                    any(not isinstance(m, str) or not m.strip() for m in modalities)):
                continue
            try:
                model_effort(entry)
            except ValueError:
                continue
            models[name] = {'model': name, **{k: v for k, v in entry.items() if k != 'hidden'}}
            for alias in row_aliases:
                aliases[alias] = name
            if row.get('isDefault') is True:
                defaults.add(name)
        cursor = page.get('nextCursor')
        if cursor is None:
            break
        if not isinstance(cursor, str) or not cursor or cursor in seen:
            raise ValueError('invalid/repeated model catalog cursor')
        seen.add(cursor)
    else:
        raise ValueError('model catalog pagination exceeds bound')
    if not models:
        raise ValueError('no compatible writer model')
    if not writer_only and len(models) < 2:
        raise ValueError('two compatible canonical models required; dual-model execution blocked')
    configured = config.get('model')
    if configured is not None:
        default = aliases.get(_name(configured))
        if default is None:
            raise ValueError('configured default is absent from compatible catalog; reconcile configuration')
    elif len(defaults) == 1:
        default = next(iter(defaults))
    else:
        raise ValueError('unambiguous default model unavailable')
    return {'default_model': default, 'provider_id': provider,
            'models': dict(sorted(models.items())), 'aliases': dict(sorted(aliases.items()))}


def _completed(identity, result, observed, model, provider):
    actual = _identity(identity, model_required=True)
    if (actual['model_id'] != model or (provider is not None and actual['provider_id'] != provider) or
            _identity(observed.get('identity'), model_required=True) != actual or
            observed.get('status') != 'completed' or observed.get('tools') != [] or
            observed.get('response_sha256') != sha(result)):
        raise ValueError('selection/readiness requires exact authenticated completed model/provider identity')
    return actual


def select_writer(snapshot, profile):
    requested = profile.get('writer_model') or snapshot['default_model']
    writer = snapshot['aliases'].get(requested, requested)
    if writer not in snapshot['models']:
        raise ValueError('configured writer missing from supported catalog')
    return {'writer_model': writer, 'reviewer_model': None, 'selector': 'host-catalog',
            'provider_id': snapshot['provider_id'], 'efforts': {writer: model_effort(snapshot['models'][writer])},
            'decision': {'reason': 'single writer selected from host configuration'}}


def select_models(snapshot, profile, task, invoke):
    """invoke is a trusted, budget-accounted model call, not a model callback."""
    models = snapshot['models']
    aliases = snapshot.get('aliases', {row.get('id', name): name for name, row in models.items()})
    def override(field):
        value = profile.get(field)
        if value is None:
            return None
        name = value if value in models else aliases.get(value)
        if name not in models:
            raise ValueError('explicit role model missing from supported catalog: ' + field)
        return name
    writer, reviewer = override('writer_model'), override('reviewer_model')
    if writer is not None and writer == reviewer:
        raise ValueError('role aliases resolve to the same canonical model')
    nonce = uuid.uuid4().hex
    selector = snapshot['default_model']
    packet = {'nonce': nonce, 'task': task, 'effective_default': selector, 'candidates': models,
              'writer_override': writer, 'reviewer_override': reviewer}
    schema = {'type': 'object', 'properties': {
        'writer_model': {'enum': [writer] if writer else list(models)},
        'reviewer_model': {'enum': [reviewer] if reviewer else list(models)},
        'reason': {'type': 'string'}, 'nonce': {'type': 'string'}},
        'required': ['writer_model', 'reviewer_model', 'reason', 'nonce'], 'additionalProperties': False}
    prompt = ('Choose two DISTINCT canonical models for one serial code writer and an independent read-only reviewer. '
              'Use only supplied candidates and honor explicit overrides. Prefer the effective default writer unless '
              'task/capability evidence justifies another choice; balance review quality and token cost. '
              'Do not invent model capabilities or pricing. Echo nonce. No tools or delegation.\n' +
              json.dumps(packet, ensure_ascii=False))
    if len(prompt.encode('utf8')) > 64_000:
        raise ValueError('selection input exceeds 64KB; provide a bounded task or explicit fixed pair')
    identity, result, observed = invoke(selector, 'select-models', prompt, schema,
        effort=model_effort(models[selector]), provider=snapshot['provider_id'])
    identity = _completed(identity, result, observed, selector, snapshot['provider_id'])
    provider = identity['provider_id']
    chosen = (result.get('writer_model'), result.get('reviewer_model'))
    if (result.get('nonce') != nonce or not isinstance(result.get('reason'), str) or not result['reason'].strip() or
            any(name not in models for name in chosen) or chosen[0] == chosen[1] or
            (writer and chosen[0] != writer) or (reviewer and chosen[1] != reviewer)):
        raise ValueError('default model returned invalid/out-of-catalog/non-distinct selection')
    readiness = []
    for model in chosen:
        if model == selector:
            evidence = {**observed, 'readiness_kind': 'selector-completion', 'nonce': nonce}
        else:
            probe = {'nonce': uuid.uuid4().hex, 'ready': True}
            probe_schema = {'type': 'object', 'properties': {'nonce': {'type': 'string'}, 'ready': {'type': 'boolean'}},
                            'required': ['nonce', 'ready'], 'additionalProperties': False}
            actual, response, record = invoke(model, 'model-readiness',
                'Return exactly this JSON, without tools:\n' + json.dumps(probe), probe_schema,
                effort=model_effort(models[model]), provider=provider)
            _completed(actual, response, record, model, provider)
            if response != probe:
                raise ValueError('readiness nonce mismatch')
            evidence = {**record, 'readiness_kind': 'nonce-probe', 'nonce': probe['nonce']}
        readiness.append(evidence)
    if any(readiness[0]['identity'][field] == readiness[1]['identity'][field]
           for field in ('context_id', 'invocation_id')):
        raise ValueError('distinct authenticated role contexts/invocations required')
    return {'policy': POLICY, 'writer_model': chosen[0], 'reviewer_model': chosen[1], 'provider_id': provider,
            'efforts': {name: model_effort(models[name]) for name in chosen},
            'catalog_sha256': sha(snapshot), 'catalog_models': list(models), 'default_model': selector,
            'selector': identity, 'decision': result, 'readiness': readiness}
