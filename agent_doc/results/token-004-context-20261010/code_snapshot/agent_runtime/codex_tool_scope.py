"""Explicit per-thread capability exposure; never edit host config/permissions."""

def resolve_tool_scope(contract):
    """The trusted host supplies requirements; unknown/incomplete keeps defaults.

    Empty requirements are an explicit assertion about this task, not an LLM
    guess from its prompt. Tools required for external retrieval retain the
    ordinary catalog. This does not enforce a security sandbox or forbid shell
    tools; the host's existing permission/instruction boundary still applies.
    """
    if not isinstance(contract, dict) or set(contract) != {
            'schema_version', 'requirements_complete', 'external_tool_requirements'}:
        raise ValueError('explicit tool-scope contract required')
    if contract['schema_version'] != 'codex-tool-scope/v1':
        raise ValueError('unsupported tool-scope version')
    if type(contract['requirements_complete']) is not bool:
        raise ValueError('requirements_complete must be boolean')
    required = contract['external_tool_requirements']
    if (not isinstance(required, list) or len(required) > 64 or
            any(not isinstance(x, str) or not x.strip() or len(x) > 128 for x in required) or
            len(set(required)) != len(required)):
        raise ValueError('bounded unique external tool requirements required')
    narrow = contract['requirements_complete'] and not required
    return {'schema_version': 'codex-tool-profile/v1',
            'profile': 'no-external-tools' if narrow else 'host-default',
            'config_overrides': {'mcp_servers.node_repl.enabled': False, 'features.apps': False} if narrow else {},
            'reason': 'complete explicit empty external requirements' if narrow else 'preserve required or unknown capabilities'}

def check_scoped_catalog(profile, servers, *, has_more=False):
    """Reject a supposedly empty catalog before inference, including new servers."""
    if has_more:
        raise ValueError('incomplete tool catalog; resolve pagination before dispatch')
    if not isinstance(servers, list):
        raise ValueError('tool catalog list required')
    for server in servers:
        if not isinstance(server, dict) or not isinstance(server.get('tools'), dict) or server.get('toolsError'):
            raise ValueError('unavailable tool catalog')
    if profile == 'no-external-tools':
        if any(server['tools'] for server in servers):
            raise ValueError('unexpected external tools remain; do not dispatch this profile')
    elif profile != 'host-default':
        raise ValueError('unknown tool profile')
