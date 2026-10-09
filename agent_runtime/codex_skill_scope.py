"""Explicit per-thread skill exclusions; preserve unknown skills and host policy."""
from pathlib import Path
import os

CONTRACT='codex-skill-scope/v1'


def _path(value):
    if not isinstance(value,str) or not value or len(value)>4096:
        raise ValueError('bounded absolute skill path required')
    path=Path(value)
    if not path.is_absolute() or path.name!='SKILL.md':
        raise ValueError('absolute SKILL.md file path required')
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('ambiguous symlinked skill path refused')
    path=path.resolve(strict=True)
    if not path.is_file():raise ValueError('regular skill file required')
    return os.path.normcase(str(path))


def _paths(values):
    if not isinstance(values,list) or len(values)>256:
        raise ValueError('bounded skill path list required')
    normalized=[_path(v) for v in values]
    if len(set(normalized))!=len(normalized):raise ValueError('duplicate skill paths')
    return normalized


def resolve_skill_scope(contract,catalog,current_skills_config):
    """All inputs come from the trusted host, never a worker's inferred needs.

    Exclude only explicitly named enabled user/repo skills. Required skills,
    system/admin skills, unlisted/plugin/unknown entries and other settings are
    unchanged. Existing effective array entries must be independently resolved
    by the host and are retained; no globally persisted config is written.
    This is catalog control, not authorization or an implementation of policy.
    """
    keys={'schema_version','requirements_complete','required_skill_paths','excluded_skill_paths'}
    if not isinstance(contract,dict) or set(contract)!=keys or contract['schema_version']!=CONTRACT:
        raise ValueError('explicit skill-scope contract required')
    if type(contract['requirements_complete']) is not bool:
        raise ValueError('requirements_complete must be boolean')
    required=_paths(contract['required_skill_paths']);excluded=_paths(contract['excluded_skill_paths'])
    if set(required)&set(excluded):raise ValueError('required skill cannot be excluded')
    if not isinstance(current_skills_config,list) or len(current_skills_config)>512:
        raise ValueError('host-resolved current skills config array required')
    existing={};config=[]
    for row in current_skills_config:
        if not isinstance(row,dict) or set(row)!={'path','enabled'} or type(row['enabled']) is not bool:
            raise ValueError('unsupported existing skill override; preserve host defaults')
        key=_path(row['path'])
        if key in existing:raise ValueError('ambiguous existing skill overrides')
        existing[key]=len(config);config.append(dict(row))
    default={'schema_version':'codex-skill-profile/v1','profile':'host-default','config_overrides':{},'excluded_skill_paths':[]}
    if not contract['requirements_complete']:return default
    if not isinstance(catalog,dict) or set(catalog)!={'cwd','skills','errors'} or catalog['errors']!=[]:
        raise ValueError('error-free native skill inventory required')
    if not isinstance(catalog['cwd'],str) or not Path(catalog['cwd']).is_absolute():
        raise ValueError('explicit catalog project root required')
    rows=catalog['skills']
    if not isinstance(rows,list) or len(rows)>1024:raise ValueError('bounded inventory required')
    inventory={}
    for row in rows:
        if not isinstance(row,dict) or type(row.get('enabled')) is not bool or not isinstance(row.get('scope'),str):
            raise ValueError('invalid skill inventory')
        key=_path(row.get('path'))
        if key in inventory:raise ValueError('ambiguous native skill inventory')
        inventory[key]=row
    for key in required:
        if key not in inventory or not inventory[key]['enabled'] or (key in existing and not config[existing[key]]['enabled']):
            raise ValueError('required skill unavailable; do not dispatch')
    actual=[]
    for key in excluded:
        row=inventory.get(key)
        if row is None or row['scope'] not in {'user','repo'}:
            raise ValueError('explicit discovered user/repo exclusion required')
        if not row['enabled'] or (key in existing and not config[existing[key]]['enabled']):continue
        actual.append(row['path'])
        if key in existing:config[existing[key]]['enabled']=False
        else:config.append({'path':row['path'],'enabled':False})
    if not actual:return default
    return {'schema_version':'codex-skill-profile/v1','profile':'explicit-skill-exclusions',
        'config_overrides':{'skills.config':config},'excluded_skill_paths':actual,
        'required_skill_paths':[inventory[k]['path'] for k in required],
        'reason':'host declares complete needs and explicitly names unrelated skill exclusions; unknown skills retained'}


def check_skill_catalog_delta(baseline_text,candidate_text,expected_entries):
    """Accept only exact full catalog-entry removals in a captured envelope.

    Caller binds each expected entry to its excluded native skill path and
    compares ALL other messages/tools/config separately. No blanket stripping
    of a skills block, root table, permissions, or invocation rules is allowed.
    """
    if not isinstance(baseline_text,str) or not isinstance(candidate_text,str):
        raise ValueError('actual captured plaintext required')
    if not isinstance(expected_entries,list) or not expected_entries or len(expected_entries)>256:
        raise ValueError('exact host-bound entry list required')
    for entry in expected_entries:
        if not isinstance(entry,str) or len(entry)>16384 or not entry.startswith('- ') or not entry.endswith('\n') or entry.count('\n')!=1 or '(file: ' not in entry:
            raise ValueError('one complete skill catalog line required')
    if len(set(expected_entries))!=len(expected_entries):raise ValueError('duplicate catalog entries')
    if max(len(baseline_text),len(candidate_text))>2097152:
        raise ValueError('captured instruction budget exceeded')
    lines=baseline_text.splitlines(keepends=True)
    headers=[i for i,line in enumerate(lines) if line=='### Available skills\n']
    closes=[i for i,line in enumerate(lines) if line.startswith('</skills_instructions>')]
    if len(headers)!=1 or len(closes)!=1 or closes[0]<=headers[0]:
        raise ValueError('one exact skill catalog section required')
    start,end=headers[0]+1,closes[0]
    removals=set()
    for entry in expected_entries:
        matches=[i for i in range(start,end) if lines[i]==entry]
        if len(matches)!=1:raise ValueError('excluded full catalog line missing or ambiguous')
        removals.add(matches[0])
    normalized=''.join(line for i,line in enumerate(lines) if i not in removals)
    if normalized!=candidate_text:raise ValueError('unexpected non-catalog instruction change')
    return {'removed_entries':len(expected_entries),'remaining_plaintext_exact':True}
