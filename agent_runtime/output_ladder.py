"""Validate a producer's output ladder against an independent request.

This module checks closed schemas and byte identities.  It deliberately does
not execute generators or certify semantic, visual, interactive, or media
quality.  A ready result still requires an independent host observation.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import stat

from .external_json import ExternalJSONError, regular_bytes, strict_json


REQUEST_SCHEMA = "output-ladder-request/v1"
MANIFEST_SCHEMA = "output-ladder-manifest/v1"
VALIDATION_SCHEMA = "output-ladder-validation/v1"
LEVELS = ("controlled_text", "diagram", "interactive_web", "explainer_video")
ROLE_REQUIREMENTS = {
    "controlled_text": {"primary_text"},
    "diagram": {"editable_source", "rendered_preview", "caption", "alt_text"},
    "interactive_web": {"web_entry", "static_fallback", "interaction_spec",
                        "accessibility_report"},
    "explainer_video": {"video", "storyboard", "transcript", "captions",
                        "audio_provenance"},
}
JSON_LIMIT = 1024 * 1024
ARTIFACT_LIMIT = 256 * 1024 * 1024
PATH_LIMIT = 1024
STRING_LIMIT = 4096
ID_LIMIT = 128
MAX_CLAIMS = 256
MAX_ARTIFACTS = 128
MAX_CHECKS_PER_LEVEL = 32
HEX = frozenset("0123456789abcdef")


class OutputLadderError(ValueError):
    """The request, manifest, or artifact violates the structural contract."""


def _closed(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise OutputLadderError(f"{label} must have exactly: {', '.join(keys)}")


def _text(value, label, limit=STRING_LIMIT, *, nonempty=True):
    if type(value) is not str or (nonempty and not value) or len(value) > limit:
        raise OutputLadderError(f"{label} must be a bounded string")
    return value


def _identifier(value, label):
    value = _text(value, label, ID_LIMIT)
    if any(ord(char) < 0x21 or ord(char) > 0x7e for char in value):
        raise OutputLadderError(f"{label} must use visible ASCII")
    return value


def _digest(value, label):
    value = _text(value, label, 64)
    if len(value) != 64 or any(char not in HEX for char in value):
        raise OutputLadderError(f"{label} must be lowercase sha256")
    return value


def _string_list(value, label, *, limit=128, item_limit=STRING_LIMIT):
    if type(value) is not list or len(value) > limit:
        raise OutputLadderError(f"{label} must be a bounded list")
    result = [_text(item, f"{label} item", item_limit) for item in value]
    if len(result) != len(set(result)):
        raise OutputLadderError(f"{label} contains duplicates")
    return result


def _load_snapshot(path):
    try:
        data = regular_bytes(path, max_bytes=JSON_LIMIT)
        return strict_json(data), hashlib.sha256(data).hexdigest()
    except ExternalJSONError as exc:
        raise OutputLadderError(str(exc)) from exc


def _request(value):
    keys = ("schema_version", "request_id", "input_version", "audience", "language",
            "claims", "requested_level", "allow_downgrade", "require_contiguous",
            "required_checks", "capability_receipt_sha256")
    _closed(value, keys, "request")
    if value["schema_version"] != REQUEST_SCHEMA:
        raise OutputLadderError("unsupported request schema")
    _identifier(value["request_id"], "request_id")
    _text(value["input_version"], "input_version")
    _text(value["audience"], "audience")
    _text(value["language"], "language", 128)
    if type(value["allow_downgrade"]) is not bool or type(value["require_contiguous"]) is not bool:
        raise OutputLadderError("request booleans must be JSON booleans")
    if value["requested_level"] not in LEVELS:
        raise OutputLadderError("unknown requested_level")
    receipt = value["capability_receipt_sha256"]
    if receipt is not None:
        _digest(receipt, "capability_receipt_sha256")
    claims = value["claims"]
    if type(claims) is not list or not claims or len(claims) > MAX_CLAIMS:
        raise OutputLadderError("claims must be a nonempty bounded list")
    claim_ids = []
    for index, claim in enumerate(claims):
        _closed(claim, ("id", "text", "evidence_refs"), f"claim[{index}]")
        claim_ids.append(_identifier(claim["id"], "claim id"))
        _text(claim["text"], "claim text")
        _string_list(claim["evidence_refs"], "claim evidence_refs", limit=128,
                     item_limit=PATH_LIMIT)
    if len(claim_ids) != len(set(claim_ids)):
        raise OutputLadderError("duplicate claim id")
    checks = value["required_checks"]
    if type(checks) is not dict or set(checks) != set(LEVELS):
        raise OutputLadderError("required_checks must contain exactly the four levels")
    for level in LEVELS:
        identifiers = _string_list(checks[level], f"required_checks.{level}",
                                   limit=MAX_CHECKS_PER_LEVEL, item_limit=ID_LIMIT)
        for identifier in identifiers:
            _identifier(identifier, "request check id")
    return frozenset(claim_ids)


def _relative_path(value):
    value = _text(value, "artifact path", PATH_LIMIT)
    if "\x00" in value or "\\" in value:
        raise OutputLadderError("artifact path must be a POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise OutputLadderError("artifact path escapes its root")
    if path.as_posix() != value:
        raise OutputLadderError("artifact path must be lexically normalized")
    return path


def _artifact_parent_fd(root, relative):
    """Open every root/parent component without following a symlink."""
    if os.open not in os.supports_dir_fd or not hasattr(os, "O_NOFOLLOW"):
        raise OutputLadderError(
            "artifact validation requires fd-relative no-follow directory opens")
    absolute = Path(os.path.abspath(root))
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        fd = os.open(absolute.anchor or os.sep, flags)
    except OSError as exc:
        raise OutputLadderError("artifact root is unavailable") from exc
    try:
        for part in (*absolute.parts[1:], *relative.parts[:-1]):
            try:
                next_fd = os.open(part, flags, dir_fd=fd)
            except OSError as exc:
                raise OutputLadderError("artifact root and parents must be real directories") from exc
            os.close(fd)
            fd = next_fd
            if not stat.S_ISDIR(os.fstat(fd).st_mode):
                raise OutputLadderError("artifact root and parents must be real directories")
        return fd
    except Exception:
        os.close(fd)
        raise


def _open_artifact(root, relative):
    parent_fd = _artifact_parent_fd(root, relative)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        return os.open(relative.parts[-1], flags, dir_fd=parent_fd)
    except OSError as exc:
        raise OutputLadderError("artifact is unavailable") from exc
    finally:
        os.close(parent_fd)


def _artifact_snapshot(root, relative):
    fd = _open_artifact(root, relative)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise OutputLadderError("artifact must be a regular file")
        if before.st_size > ARTIFACT_LIMIT:
            raise OutputLadderError("artifact exceeds byte bound")
        digest = hashlib.sha256()
        count = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, ARTIFACT_LIMIT + 1 - count))
            if not chunk:
                break
            count += len(chunk)
            if count > ARTIFACT_LIMIT:
                raise OutputLadderError("artifact exceeds byte bound")
            digest.update(chunk)
        after = os.fstat(fd)
        identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
                    before.st_ctime_ns)
        if identity != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
                        after.st_ctime_ns) or count != after.st_size:
            raise OutputLadderError("artifact changed while being read")
    except OSError as exc:
        raise OutputLadderError("artifact could not be read") from exc
    finally:
        os.close(fd)
    check_fd = _open_artifact(root, relative)
    try:
        current_info = os.fstat(check_fd)
        if not stat.S_ISREG(current_info.st_mode):
            raise OutputLadderError("artifact path no longer names a regular file")
        if (current_info.st_dev, current_info.st_ino) != (after.st_dev, after.st_ino):
            raise OutputLadderError("artifact path changed after reading")
    finally:
        os.close(check_fd)
    return digest.hexdigest()


def _manifest(value, request, request_sha256, artifact_root):
    keys = ("schema_version", "request_id", "request_sha256", "producer",
            "delivered_levels", "claims_by_level", "artifacts", "checks",
            "limitations", "recovery")
    _closed(value, keys, "manifest")
    if value["schema_version"] != MANIFEST_SCHEMA:
        raise OutputLadderError("unsupported manifest schema")
    if value["request_id"] != request["request_id"]:
        raise OutputLadderError("request id mismatch")
    if _digest(value["request_sha256"], "manifest request_sha256") != request_sha256:
        raise OutputLadderError("request sha256 mismatch")
    _identifier(value["producer"], "producer")
    delivered = _string_list(value["delivered_levels"], "delivered_levels", limit=len(LEVELS),
                             item_limit=ID_LIMIT)
    if not delivered or delivered[0] != "controlled_text" or any(x not in LEVELS for x in delivered):
        raise OutputLadderError("controlled_text must be the first delivered level")
    if delivered != sorted(delivered, key=LEVELS.index):
        raise OutputLadderError("delivered_levels must use ladder order")
    target_index = LEVELS.index(request["requested_level"])
    if any(LEVELS.index(level) > target_index for level in delivered):
        raise OutputLadderError("manifest exceeds the independently requested level")
    if request["require_contiguous"]:
        expected = list(LEVELS[:LEVELS.index(delivered[-1]) + 1])
        if delivered != expected:
            raise OutputLadderError("request requires contiguous levels")
    reached = request["requested_level"] in delivered
    if not reached and not request["allow_downgrade"]:
        raise OutputLadderError("request forbids the delivered downgrade")
    claims = value["claims_by_level"]
    if type(claims) is not dict or set(claims) != set(delivered):
        raise OutputLadderError("claims_by_level must match delivered levels")
    expected_claims = {claim["id"] for claim in request["claims"]}
    for level in delivered:
        actual = _string_list(claims[level], f"claims_by_level.{level}", limit=MAX_CLAIMS,
                              item_limit=ID_LIMIT)
        if set(actual) != expected_claims or len(actual) != len(expected_claims):
            raise OutputLadderError("every delivered level must cover the exact claim set")
    _string_list(value["limitations"], "limitations", limit=128)
    _string_list(value["recovery"], "recovery", limit=128)

    artifacts = value["artifacts"]
    if type(artifacts) is not list or not artifacts or len(artifacts) > MAX_ARTIFACTS:
        raise OutputLadderError("artifacts must be a nonempty bounded list")
    artifact_ids, artifact_paths, roles = set(), set(), {level: set() for level in delivered}
    artifact_levels = {}
    actual_digests = {}
    for index, artifact in enumerate(artifacts):
        _closed(artifact, ("id", "level", "role", "path", "declared_sha256"),
                f"artifact[{index}]")
        aid = _identifier(artifact["id"], "artifact id")
        if aid in artifact_ids:
            raise OutputLadderError("duplicate artifact id")
        artifact_ids.add(aid)
        level = artifact["level"]
        if level not in delivered:
            raise OutputLadderError("artifact level is not delivered")
        role = _identifier(artifact["role"], "artifact role")
        if role not in ROLE_REQUIREMENTS[level] or role in roles[level]:
            raise OutputLadderError("artifact role is unknown or duplicated")
        roles[level].add(role)
        artifact_levels[aid] = level
        relative = _relative_path(artifact["path"])
        if relative.as_posix() in artifact_paths:
            raise OutputLadderError("one artifact path cannot fill multiple roles")
        artifact_paths.add(relative.as_posix())
        declared = _digest(artifact["declared_sha256"], "artifact declared_sha256")
        actual = _artifact_snapshot(artifact_root, relative)
        actual_digests[aid] = actual
        if actual != declared:
            raise OutputLadderError("artifact sha256 mismatch")
    for level in delivered:
        if roles[level] != ROLE_REQUIREMENTS[level]:
            raise OutputLadderError(f"{level} artifact roles are incomplete")

    checks = value["checks"]
    if type(checks) is not list or len(checks) > len(LEVELS) * MAX_CHECKS_PER_LEVEL:
        raise OutputLadderError("checks must be a bounded list")
    seen, check_ids, pending = set(), set(), not reached
    expected_checks = {(level, check_id) for level in delivered
                       for check_id in request["required_checks"][level]}
    for index, check in enumerate(checks):
        allowed = {"check_id", "level", "request_check_id", "status",
                   "evidence_artifact_ids", "producer_observer"}
        if type(check) is not dict or not set(check).issubset(allowed) or not allowed - {"producer_observer"} <= set(check):
            raise OutputLadderError(f"check[{index}] has unknown or missing fields")
        check_id = _identifier(check["check_id"], "check id")
        if check_id in check_ids:
            raise OutputLadderError("duplicate check id")
        check_ids.add(check_id)
        level = check["level"]
        if level not in delivered:
            raise OutputLadderError("check level is not delivered")
        request_check = _identifier(check["request_check_id"], "request check id")
        key = (level, request_check)
        if key not in expected_checks or key in seen:
            raise OutputLadderError("check is unrequested or duplicated")
        seen.add(key)
        if check["status"] not in ("pass", "fail", "not_run"):
            raise OutputLadderError("unknown check status")
        evidence = _string_list(check["evidence_artifact_ids"], "check evidence",
                                limit=MAX_ARTIFACTS, item_limit=ID_LIMIT)
        if any(aid not in artifact_ids for aid in evidence):
            raise OutputLadderError("check evidence references an unknown artifact")
        if any(artifact_levels[aid] != level for aid in evidence):
            raise OutputLadderError("check evidence must belong to the same output level")
        if check["status"] == "pass" and not evidence:
            raise OutputLadderError("passing checks require byte-bound evidence")
        if check["status"] != "pass":
            pending = True
        if "producer_observer" in check:
            _text(check["producer_observer"], "producer observer", ID_LIMIT)
    if seen != expected_checks:
        raise OutputLadderError("required check entry is missing")
    return ("pending" if pending else "ready-for-independent-review"), actual_digests, delivered


def validate_output_ladder(request_path, manifest_path, artifact_root):
    """Return a structural validation result; never an acceptance decision."""
    request_sha = manifest_sha = None
    try:
        request, request_sha = _load_snapshot(request_path)
        _request(request)
        manifest, manifest_sha = _load_snapshot(manifest_path)
        state, artifact_digests, delivered = _manifest(
            manifest, request, request_sha, artifact_root)
        return {"schema_version": VALIDATION_SCHEMA, "state": state,
                "request_sha256": request_sha, "manifest_sha256": manifest_sha,
                "requested_level": request["requested_level"],
                "delivered_levels": delivered, "artifact_sha256": artifact_digests,
                "findings": [], "independent_review_required": True}
    except OutputLadderError as exc:
        return {"schema_version": VALIDATION_SCHEMA, "state": "invalid",
                "request_sha256": request_sha, "manifest_sha256": manifest_sha,
                "requested_level": None, "delivered_levels": [], "artifact_sha256": {},
                "findings": [str(exc)], "independent_review_required": True}
