#!/usr/bin/env python3
"""List gateway model IDs without asserting access or tool/vision capabilities.

Discovery performs no inference. Listed IDs produce unavailable, empty-capability
inventory entries until the host verifies the exact interface and identity.
Use --from-inventory to validate explicit host declarations without guessing.
"""
from __future__ import annotations

import argparse
from http.client import HTTPException
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.external_json import load_json, strict_json
from agent_runtime.model_routing import validate_inventory

MAX_MODEL_RESPONSE_BYTES = 1024 * 1024

# Name-based labels are preview hints only, never routing capabilities.
_VISION_PATTERNS = re.compile(
    r'(kimi|gemini|gpt-[56]|claude|qwen.*vl|llava|vision|multimodal)',
    re.I,
)

_THINKING_PATTERNS = re.compile(r'(thinking|reasoner|pro|deepseek-v4-pro|o1|o3)', re.I)

_FLASH_PATTERNS = re.compile(r'(flash|lite|mini|tiny|nano)', re.I)

_CODE_PATTERNS = re.compile(r'(coder|code|qwen3-coder|glm-5\.[123])', re.I)


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
    try:
        req = urllib.request.Request(f'{base}/v1/models', headers={'Accept': 'application/json'})
        if auth_token:
            req.add_header('Authorization', f'Bearer {auth_token}')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read(MAX_MODEL_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'gateway returned HTTP {exc.code}') from exc
    except (urllib.error.URLError, OSError) as exc:
        raise RuntimeError('gateway request failed or timed out') from exc
    except (ValueError, HTTPException) as exc:
        raise RuntimeError('invalid gateway URL or HTTP request') from exc
    if len(payload) > MAX_MODEL_RESPONSE_BYTES:
        raise RuntimeError('gateway model response exceeds 1 MiB')
    try:
        data = strict_json(payload)
    except ValueError as exc:
        raise RuntimeError('invalid gateway model JSON') from exc
    entries = data.get('data') if isinstance(data, dict) else data
    if not isinstance(entries, list) or any(
            not isinstance(entry, dict) or not isinstance(entry.get('id'), str)
            or not entry['id'].strip() for entry in entries):
        raise RuntimeError('unexpected /v1/models response shape or model ID')
    return [entry['id'] for entry in entries]


def build_inventory(model_ids: list[str]) -> dict:
    """Return schema-valid inactive entries; a listing does not verify access."""
    if not model_ids:
        raise RuntimeError('gateway returned zero models')
    seen = set()
    inventory = {'schema_version': 1, 'models': []}
    for mid in model_ids:
        if not isinstance(mid, str) or not mid.strip():
            raise ValueError('invalid discovered model ID')
        identity = (_model_family(mid), mid)
        if identity in seen:
            continue
        seen.add(identity)
        inventory['models'].append({
            'provider': identity[0],
            'model': mid,
            'available': False,
            'capabilities': [],
            'transport': 'native',
        })
    return validate_inventory(inventory)


def _classify(model_id: str) -> list[str]:
    """Human-readable tags for a single model (dry-run display)."""
    tags = []
    if _THINKING_PATTERNS.search(model_id):
        tags.append('reasoning')
    if _FLASH_PATTERNS.search(model_id):
        tags.append('fast')
    if _CODE_PATTERNS.search(model_id):
        tags.append('code')
    if _VISION_PATTERNS.search(model_id):
        tags.append('vision?')
    return tags


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', help='Gateway base URL (default: ANTHROPIC_BASE_URL env)')
    parser.add_argument('--auth-token', help='Bearer token (default: ANTHROPIC_AUTH_TOKEN env)')
    parser.add_argument('--output', type=Path, help='Write inventory JSON to this path (default: stdout)')
    parser.add_argument('--dry-run', action='store_true', help='Preview only; do not write')
    parser.add_argument('--from-inventory', type=Path,
                        help='Validate explicit host inventory while preserving declared capabilities')
    parser.add_argument('--timeout', type=int, default=15, help='HTTP timeout in seconds')
    args = parser.parse_args()

    if args.timeout < 1:
        parser.error('--timeout must be positive')
    try:
        if args.from_inventory:
            inventory = validate_inventory(load_json(args.from_inventory))
        else:
            base_url = args.base_url or os.environ.get('ANTHROPIC_BASE_URL')
            auth_token = args.auth_token or os.environ.get('ANTHROPIC_AUTH_TOKEN')
            if not base_url:
                parser.error('no gateway URL: pass --base-url or set ANTHROPIC_BASE_URL')
            inventory = build_inventory(fetch_models(base_url, auth_token, timeout=args.timeout))
        text = json.dumps(inventory, ensure_ascii=False, indent=2) + '\n'
        if args.dry_run or not args.output:
            print(text, end='')
        else:
            args.output.write_text(text, encoding='utf-8')
            print(f'inventory ({len(inventory["models"])} models) written to {args.output}')
        if args.dry_run and not args.from_inventory:
            print('Name-based preview hints only; access/tools/vision remain unverified.', file=sys.stderr)
            for entry in inventory['models']:
                print(f'  {entry["model"]}: {", ".join(_classify(entry["model"]))}', file=sys.stderr)
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f'discovery failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
