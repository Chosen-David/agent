#!/usr/bin/env python3
"""Auto-discover available models from the host gateway and emit a model inventory.

Reads ANTHROPIC_BASE_URL and (optionally) ANTHROPIC_AUTH_TOKEN from the
environment, calls the gateway's /v1/models endpoint, applies capability
heuristics per model family, and writes a model inventory JSON compatible with
agent_runtime.model_routing.validate_inventory().

No inference is performed. The output is a capability-annotated inventory that can
be fed to setup.py --model-inventory, or used as a dry-run preview. When the
gateway is unreachable or returns an empty list, the script exits non-zero and
prints a human-readable diagnostic — it never silently produces an empty
inventory from a live but model-less gateway.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.external_json import load_json
from agent_runtime.model_routing import EMPTY_INVENTORY, validate_inventory

# ---------------------------------------------------------------------------
# Capability heuristics — keyed by substring matched against the model id.
# These are conservative defaults; a model can only gain capabilities here, never
# lose what the gateway actually provides. The transport is native because the
# mcli.sankuai.com proxy presents every backend through one uniform endpoint.
# ---------------------------------------------------------------------------

# Models known to support image/vision input (OpenAI-compatible format).
_VISION_PATTERNS = re.compile(
    r'(kimi|gemini|gpt-[56]|claude|qwen.*vl|llava|vision|multimodal)',
    re.I,
)

# Models that are explicitly deep-reasoning variants; flagged for routing.
_THINKING_PATTERNS = re.compile(r'(thinking|reasoner|pro|deepseek-v4-pro|o1|o3)', re.I)

# Flash/lightweight variants — prefer for high-throughput, non-reasoning work.
_FLASH_PATTERNS = re.compile(r'(flash|lite|mini|tiny|nano)', re.I)

# Code-specialist models.
_CODE_PATTERNS = re.compile(r'(coder|code|qwen3-coder|glm-5\.[123])', re.I)


def _infer_capabilities(model_id: str) -> list[str]:
    caps = ['tools']
    if _VISION_PATTERNS.search(model_id):
        caps.append('vision')
    return sorted(set(caps))


def _model_family(model_id: str) -> str:
    low = model_id.lower()
    if low.startswith('claude'):
        return 'anthropic'
    if low.startswith('deepseek'):
        return 'deepseek'
    if low.startswith('kimi'):
        return 'moonshot'
    if low.startswith('glm') or low.startswith('zai'):
        return 'zai'
    if low.startswith('gpt'):
        return 'openai'
    if low.startswith('gemini'):
        return 'google'
    if low.startswith('qwen'):
        return 'alibaba'
    if low.startswith('minimax'):
        return 'minimax'
    if low.startswith('grok'):
        return 'xai'
    if low.startswith('doubao'):
        return 'bytedance'
    if 'longcat' in low:
        return 'meituan'
    return 'unknown'


def fetch_models(base_url: str, auth_token: str | None, timeout: int = 15) -> list[str]:
    """Call GET {base_url}/v1/models and return the list of model id strings."""
    base = base_url.rstrip('/')
    req = urllib.request.Request(f'{base}/v1/models', headers={'Accept': 'application/json'})
    if auth_token:
        req.add_header('Authorization', f'Bearer {auth_token}')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'gateway returned HTTP {exc.code}: {exc.reason}') from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f'gateway unreachable: {exc.reason}') from exc
    # OpenAI-style envelope ({"data":[{"id":...}]})
    data = json.loads(payload)
    if isinstance(data, dict) and isinstance(data.get('data'), list):
        return [m['id'] for m in data['data'] if isinstance(m, dict) and m.get('id')]
    if isinstance(data, list):
        return [m['id'] for m in data if isinstance(m, dict) and m.get('id')]
    raise RuntimeError('unexpected /v1/models response shape')


def build_inventory(model_ids: list[str]) -> dict:
    """Turn a list of model ids into a validated model_inventory."""
    if not model_ids:
        raise RuntimeError('gateway returned zero models')
    seen = set()
    inventory = {'schema_version': 1, 'models': []}
    for mid in model_ids:
        identity = (_model_family(mid), mid)
        if identity in seen:
            continue
        seen.add(identity)
        inventory['models'].append({
            'provider': identity[0],
            'model': mid,
            'available': True,
            'capabilities': _infer_capabilities(mid),
            'transport': 'native',
        })
    return validate_inventory(inventory)


def _classify(model_id: str) -> dict:
    """Human-readable tags for a single model (dry-run display)."""
    tags = []
    if _THINKING_PATTERNS.search(model_id):
        tags.append('reasoning')
    if _FLASH_PATTERNS.search(model_id):
        tags.append('fast')
    if _CODE_PATTERNS.search(model_id):
        tags.append('code')
    if _VISION_PATTERNS.search(model_id):
        tags.append('vision')
    return tags


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', help='Gateway base URL (default: ANTHROPIC_BASE_URL env)')
    parser.add_argument('--auth-token', help='Bearer token (default: ANTHROPIC_AUTH_TOKEN env)')
    parser.add_argument('--output', type=Path, help='Write inventory JSON to this path (default: stdout)')
    parser.add_argument('--dry-run', action='store_true', help='Preview only; do not write')
    parser.add_argument('--from-inventory', type=Path,
                        help='Expand an existing model_inventory.json with heuristic capabilities')
    parser.add_argument('--timeout', type=int, default=15, help='HTTP timeout in seconds')
    args = parser.parse_args()

    if args.from_inventory:
        existing = load_json(str(args.from_inventory))
        for entry in existing.get('models', []):
            entry['capabilities'] = _infer_capabilities(entry['model'])
        inventory = validate_inventory(existing)
        if args.dry_run:
            print(json.dumps(inventory, ensure_ascii=False, indent=2))
            return 0
        if args.output:
            args.output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
            print(f'inventory written to {args.output}')
        else:
            print(json.dumps(inventory, ensure_ascii=False, indent=2))
        return 0

    base_url = args.base_url or os.environ.get('ANTHROPIC_BASE_URL')
    auth_token = args.auth_token or os.environ.get('ANTHROPIC_AUTH_TOKEN')
    if not base_url:
        parser.error('no gateway URL: pass --base-url or set ANTHROPIC_BASE_URL')

    try:
        model_ids = fetch_models(base_url, auth_token, timeout=args.timeout)
    except RuntimeError as exc:
        print(f'discovery failed: {exc}', file=sys.stderr)
        return 1

    inventory = build_inventory(model_ids)

    if args.dry_run:
        print(json.dumps(inventory, ensure_ascii=False, indent=2))
        print('\n--- Classification preview ---', file=sys.stderr)
        for entry in inventory['models']:
            tags = _classify(entry['model'])
            caps = ','.join(entry['capabilities'])
            tag_str = f' [{", ".join(tags)}]' if tags else ''
            print(f'  {entry["model"]:40s} provider={entry["provider"]:12s} caps={caps:15s}{tag_str}',
                  file=sys.stderr)
        return 0

    text = json.dumps(inventory, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(text)
        print(f'inventory ({len(inventory["models"])} models) written to {args.output}')
    else:
        print(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
