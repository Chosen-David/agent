"""Synthetic app-server fault fixture; never evidence of real model execution."""
import json
import sys

mode = sys.argv[1]

if mode in ("startup-sqlite", "startup-unknown"):
    sys.stderr.write("private-fixture-token " * 10000)
    if mode == "startup-sqlite":
        sys.stderr.write("failed to open state DB: (code: 14) unable to open database file")
    sys.stderr.flush()
    raise SystemExit(1)


def send(value):
    print(json.dumps(value), flush=True)


for line in sys.stdin:
    message = json.loads(line)
    method = message.get('method')
    if 'id' not in message:
        continue
    result = {}
    if method == 'config/read':
        result = {'config': {'mcp_servers': {'fixture-server': {'enabled': True}},
                             'plugins': {'fixture-plugin': {'enabled': True}}}}
    if method == 'thread/start':
        config = message['params']['config']
        assert config['mcp_servers']['fixture-server']['enabled'] is False
        assert config['plugins']['fixture-plugin']['enabled'] is False
        assert config['web_search'] == 'disabled'
        result = {'model': 'fixture-writer', 'modelProvider': 'fixture',
                  'sandbox': {'type': 'readOnly' if mode != 'writable' else 'workspaceWrite'},
                  'thread': {'id': 'fixture-thread'}}
    if method == 'turn/start':
        result = {'turn': {'id': 'fixture-turn'}}
    send({'id': message['id'], 'result': result})
    if method == 'turn/start':
        params = {'threadId': 'fixture-thread', 'turnId': 'fixture-turn'}
        if mode == 'approval':
            send({'id': 99, 'method': 'item/commandExecution/requestApproval', 'params': params})
            continue
        if mode == 'tool':
            send({'method': 'item/started', 'params': {**params, 'item': {'type': 'commandExecution'}}})
        send({'method': 'item/completed', 'params': {**params, 'item': {
            'type': 'agentMessage', 'text': '{"ready":true}'}}})
        send({'method': 'turn/completed', 'params': {**params, 'turn': {
            'id': 'stale-turn' if mode == 'stale' else 'fixture-turn',
            'status': 'failed' if mode == 'failed' else 'completed'}}})
