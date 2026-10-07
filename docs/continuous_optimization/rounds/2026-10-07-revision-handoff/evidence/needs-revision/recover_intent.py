"""Diagnostic driver: actual model finding payload, existing Mailbox, one owner.

Not a deployed adapter, scheduler, model restart, or concurrent atomic operation.
"""
import argparse
import json
import os
from pathlib import Path
import sys

def recover(intent_path, repo, interrupt=False):
    sys.path.insert(0, str(repo))
    from agent_runtime.communication import Mailbox
    intent = json.loads(intent_path.read_text())
    box = Mailbox(intent['db'], intent['plan'], intent['artifact_root'])
    receipt = next(row['receipt'] for row in box.status()
                   if row['seq'] == intent['incoming_seq']
                   and row['recipient'] == intent['recipient'])
    if receipt is not None and receipt != intent['receipt']:
        raise ValueError('incoming receipt conflict; reconcile before publication')
    result = box.publish(intent['event'])
    if interrupt:
        os._exit(73)
    box.acknowledge(intent['recipient'], intent['incoming_seq'], intent['receipt'])
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--intent', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--interrupt-after-publish', action='store_true')
    args = parser.parse_args()
    print(json.dumps(recover(args.intent, args.repo, args.interrupt_after_publish)))
