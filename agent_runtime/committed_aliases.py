"""Resolve pinned Git file aliases without following working-tree links."""
import posixpath
from pathlib import PurePosixPath


class CommittedAliases:
    """Export only file targets in the existing shared Skill namespaces.

    The caller supplies a fixed Git tree and blob reader, and checks which
    origins may be aliases. ``sources`` includes each traversed dependency for
    callers that must reject dirty installation inputs.
    """
    def __init__(self, entries, read_blob):
        self.entries = entries
        self.read_blob = read_blob
        self.blobs = {}
        self.sources = set()

    def resolve(self, logical):
        current, seen = logical, set()
        while True:
            entry = self.entries.get(current)
            if entry is None or entry[1] != 'blob' or current in seen or len(seen) >= 32:
                raise ValueError('Unsafe committed skill alias: ' + logical)
            mode, _, sha = entry
            if sha not in self.blobs:
                self.blobs[sha] = self.read_blob(sha)
            self.sources.add(current)
            if mode in ('100644', '100755'):
                return self.blobs[sha]
            if mode != '120000':
                raise ValueError('Unsafe committed skill alias: ' + logical)
            seen.add(current)
            target = self.blobs[sha].decode('utf-8')
            if (not target or target.startswith('/') or '\\' in target
                    or any(ord(char) < 32 for char in target)):
                raise ValueError('Unsafe committed skill alias: ' + logical)
            current = posixpath.normpath(posixpath.join(posixpath.dirname(current), target))
            parts = PurePosixPath(current).parts
            allowed = ((len(parts) == 2 and parts[0] == 'shared-references')
                       or (len(parts) == 2 and parts[0] == 'agent_runtime'
                           and parts[1].endswith('.py'))
                       or (len(parts) == 4 and parts[:3] == ('plugins', 'research-assistant', 'shared-scripts')
                           and parts[3].endswith('.py')))
            if not allowed:
                raise ValueError('Unsafe committed skill alias: ' + logical)
