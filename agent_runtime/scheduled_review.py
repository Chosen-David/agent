"""Read-only Codex review and owner-host handoff for managed timer events."""
import hashlib
import json
from pathlib import Path
import subprocess

from .codex_host import AppServer, MAX_PACKET, TEXT, load_profile, object_schema
from .project_docs import assert_ai_writable, document_root
from .task_manifest import atomic_json


def codex_timer_reviewer(root, *, profile, writer_model, reviewer_model, owner_thread,
                         owner_socket, evidence):
    """Bind in a trusted supervisor adapter. evidence(run_id) returns current source/data."""
    root = Path(root).resolve()
    if not writer_model or not reviewer_model or reviewer_model == writer_model:
        raise ValueError('distinct task-bound writer and reviewer models required')
    if not owner_thread or not Path(owner_socket).is_absolute():
        raise ValueError('owner thread and absolute owner socket required')

    def review(run_id, event_id):
        config = load_profile(Path(profile))
        packet = json.dumps(evidence(run_id), ensure_ascii=False, allow_nan=False)
        prompt = ('Review the original goal against current source, prior advice and raw evidence. '
                  'Identify the next concrete implementation or validation step. Cite affected functions, '
                  'redundant work and applicable industrial or research references from the packet. '
                  'For performance '
                  'claims check matched workloads and whether the measured change isolates the '
                  'claimed optimization. Mark missing evidence pending.\n' + packet)
        if len(prompt.encode()) > MAX_PACKET:
            raise ValueError('review evidence exceeds packet limit; narrow the source and raw data explicitly')
        host = AppServer(config['command'], root, config['timeout_seconds'])
        try:
            identity, advice, observation = host.run(reviewer_model, prompt,
                object_schema({'findings': TEXT, 'next_step': TEXT}), root)
        finally:
            host.close()
        if identity['model_id'] != reviewer_model or identity['context_id'] == owner_thread:
            raise ValueError('reviewer identity differs from binding or shares writer context')
        key = hashlib.sha256((run_id + '\0' + event_id).encode()).hexdigest()
        path = assert_ai_writable(root, document_root(root) / 'advice' / f'supervisor-{key}.json')
        record = {'run_id': run_id, 'event_id': event_id, 'identity': identity,
                  'request_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                  'observation': observation, 'advice': advice}
        atomic_json(path, record)
        message = f'监督轮次 {event_id}：读取 {path}，核对建议并推进一个已授权步骤，记录实现与验收证据。'
        queued = subprocess.run([*config['command'], 'queue', '--thread', owner_thread,
                                 '--message', message, '--resume', '--remote', 'unix://' + str(owner_socket)],
                                cwd=root, capture_output=True, text=True, timeout=config['timeout_seconds'])
        return {'advice_path': str(path), 'delivery': 'queued_unconfirmed' if queued.returncode == 0
                else 'delivery_failed', 'returncode': queued.returncode, 'diagnostic': queued.stderr[-1000:]}
    return review
