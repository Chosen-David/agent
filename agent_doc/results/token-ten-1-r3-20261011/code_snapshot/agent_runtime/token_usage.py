"""Strict server accounting for a fresh one-turn, no-tool Codex short probe."""
import json

def short_appserver_usage(events, thread_id, turn_id):
    """Account one fresh no-tool RPC turn; never sum cumulative updates."""
    starts = []
    completed = []
    snapshots = []
    done = False
    allowed_items = {'userMessage', 'agentMessage', 'reasoning'}
    for event in events:
        method = event.get('method', '')
        params = event.get('params', {})
        if method == 'error':
            raise ValueError('server error during probe')
        if params.get('threadId') != thread_id:
            continue
        if method in ('turn/started', 'turn/completed'):
            turn = params.get('turn', {})
            if turn.get('id') != turn_id:
                raise ValueError('unexpected turn on fresh probe thread')
            if done:
                raise ValueError('duplicate or out-of-order terminal event')
            if method == 'turn/started':
                starts.append(turn)
            else:
                if not starts or turn.get('status') != 'completed' or turn.get('error'):
                    raise ValueError('probe turn did not successfully complete')
                if any(i.get('type') not in allowed_items for i in turn.get('items', [])):
                    raise ValueError('probe executed tools or other work')
                completed.append(turn)
                done = True
        elif method == 'thread/tokenUsage/updated':
            if done or not starts or params.get('turnId') != turn_id:
                raise ValueError('usage outside active fresh turn')
            snapshots.append(params.get('tokenUsage', {}))
        elif method in ('item/started', 'item/completed'):
            if done or not starts or params.get('turnId') != turn_id:
                raise ValueError('item outside active fresh turn')
            if params.get('item', {}).get('type') not in allowed_items:
                raise ValueError('probe executed tools or other work')
    if len(starts) != 1 or len(completed) != 1 or not snapshots:
        raise ValueError('one complete fresh turn and server usage are required')
    snapshot = snapshots[-1]
    last, total = snapshot.get('last', {}), snapshot.get('total', {})
    keys = ('inputTokens', 'cachedInputTokens', 'outputTokens', 'totalTokens', 'reasoningOutputTokens')
    if any(type(last.get(k)) is not int or last[k] < 0 for k in keys):
        raise ValueError('missing/noninteger server token usage')
    if any(total.get(k) != last[k] for k in keys):
        raise ValueError('cumulative history on purported fresh thread')
    if (last['totalTokens'] != last['inputTokens'] + last['outputTokens'] or
            last['cachedInputTokens'] > last['inputTokens'] or
            last['reasoningOutputTokens'] > last['outputTokens']):
        raise ValueError('inconsistent server token accounting')
    return {'thread_id': thread_id, 'turn_id': turn_id,
            'input_tokens': last['inputTokens'], 'cached_input_tokens': last['cachedInputTokens'],
            'output_tokens': last['outputTokens'], 'total_tokens': last['totalTokens'],
            'reasoning_output_tokens': last['reasoningOutputTokens'],
            'source': 'Codex app-server final fresh-turn tokenUsage snapshot',
            'scope': 'one no-tool inference turn; cache not subtracted; development/this chat excluded'}

def short_probe_usage(lines):
    events = []
    for line in lines:
        try:
            value = json.loads(line)
        except (ValueError, TypeError) as exc:
            raise ValueError('damaged stdout JSONL; stderr must be captured separately') from exc
        if not isinstance(value,dict) or not isinstance(value.get('type'),str):
            raise ValueError('invalid stdout event')
        events.append(value)
    phase = 'new'
    for event in events:
        kind = event['type']
        if kind == 'thread.started' and phase == 'new':
            phase = 'thread'
        elif kind == 'turn.started' and phase == 'thread':
            phase = 'turn'
        elif kind == 'turn.completed' and phase == 'turn':
            phase = 'done'
        elif kind.startswith('item.') and phase == 'turn':
            pass
        else:
            raise ValueError('unexpected or out-of-order event; require one fresh complete turn')
    if phase != 'done':
        raise ValueError('incomplete fresh turn')
    starts = [e for e in events if e.get('type') == 'thread.started']
    turns = [e for e in events if e.get('type') == 'turn.completed']
    if (len(starts) != 1 or len(turns) != 1 or
            sum(e.get('type') == 'turn.started' for e in events) != 1 or
            any(e.get('type') in ('error','turn.failed') for e in events)):
        raise ValueError('need one successful fresh server turn; no resumed/cumulative snapshots')
    if any(e.get('type','').startswith('item.') and
           e.get('item',{}).get('type') not in ('agent_message','reasoning') for e in events):
        raise ValueError('probe executed tools or other work; bounded no-tool accounting is invalid')
    usage = turns[0].get('usage', {})
    required = ('input_tokens','cached_input_tokens','output_tokens')
    if not isinstance(usage,dict) or any(type(usage.get(k)) is not int or usage[k] < 0 for k in required):
        raise ValueError('missing/noninteger server token usage')
    if usage['cached_input_tokens'] > usage['input_tokens']:
        raise ValueError('cached input must be a subset, not extra tokens')
    if not isinstance(starts[0].get('thread_id'),str) or not starts[0]['thread_id']:
        raise ValueError('missing fresh thread identity')
    return {'thread_id':starts[0]['thread_id'], 'input_tokens':usage['input_tokens'],
            'cached_input_tokens':usage['cached_input_tokens'], 'output_tokens':usage['output_tokens'],
            'total_tokens':usage['input_tokens'] + usage['output_tokens'],
            'source':'Codex fresh single turn.completed server usage',
            'scope':'whole short no-tool inference turn; cached input not subtracted; development/this chat excluded'}
