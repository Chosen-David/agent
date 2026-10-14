"""Read archived R6 native turns once; do not issue provider requests."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.token_usage import short_appserver_usage


def audit():
    source = ROOT / 'agent_doc/results/token-fifty-06-20261012'
    observations = {}
    for arm in ('baseline', 'candidate'):
        path = source / (arm + '.rpc.jsonl')
        events = [json.loads(line) for line in path.read_text().splitlines()]
        starts = [e for e in events if e.get('method') == 'turn/started']
        assert len(starts) == 1
        p = starts[0]['params']
        thread, turn = p['threadId'], p['turn']['id']
        identity = thread + '/' + turn
        usage = short_appserver_usage(events, thread, turn)
        ends = [e for e in events if e.get('method') == 'turn/completed']
        assert len(ends) == 1
        terminal = ends[0]['params']['turn']
        answer = json.loads(terminal['items'][0]['text'])
        oracle = json.loads((source / 'oracle.json').read_text())
        assert answer == oracle
        last = [e['params']['tokenUsage']['last'] for e in events if e.get('method') == 'thread/tokenUsage/updated'][-1]
        row = {
            'arm':arm, 'observed_call_identity':identity,
            'identity_scope':'native thread/turn, not provider internal request ID',
            'provider_request_id':None,
            'edge':{'sender':'frozen R6 short-probe host', 'recipient':'fresh no-tool native inference'},
            'observed_native_turns':1, 'provider_requests':None,
            **usage, 'cache_write_input_tokens':last.get('cacheWriteInputTokens'),
            'native_duration_ms':terminal.get('durationMs'),
            'observed_failed_turns':0, 'observed_retry_turns':0,
            'observed_tool_fanout':0, 'observed_invalidation_reruns':0,
            'provider_internal_retries':None, 'receiver_history_reinput_tokens':None,
            'actual_cost':None,
            'raw_trace':str(path.relative_to(ROOT)),
            'raw_trace_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'oracle_exact':True,
        }
        if identity in observations:
            assert observations[identity] == row, 'conflicting duplicate native turn'
        observations[identity] = row
    rows = list(observations.values())
    sums = {k:sum(r[k] for r in rows) for k in ('input_tokens','output_tokens','total_tokens','cached_input_tokens','cache_write_input_tokens','reasoning_output_tokens')}
    return {
        'schema_version':'historical-trace-audit/v1',
        'method':'one final fresh-turn snapshot per unique native thread/turn; never sum event snapshots or subtract cache; reasoning already included in output',
        'measurement_date':'2026-10-12', 'audit_date':'2026-10-14',
        'observations':rows, 'observed_pair_totals':sums,
        'new_provider_calls':0,
        'all_roles':{'input_tokens':None,'output_tokens':None,'cached_input_tokens':None,'actual_cost':None,'latency_ms':None},
        'unobserved_roles':['author','figures','visualization','review','orchestrator','this session and independent audit'],
        'limitations':['Only archived short no-tool probe edge is observed', 'Provider request IDs, hidden retries, receiver history attribution, all-role totals and monetary bill are unavailable', 'No production hotspot ranking or new savings claim', 'Native single-turn duration is not workflow latency or a statistical latency comparison']
    }


if __name__ == '__main__':
    Path(sys.argv[1]).write_text(json.dumps(audit(), indent=2)+'\n')
