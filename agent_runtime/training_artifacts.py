"""Plan checkpoint writes against the physical output filesystem before launch."""
import argparse
import json
from pathlib import Path
import shutil


LIGHTWEIGHT = {"profile", "correctness", "spectral"}
POLICIES = LIGHTWEIGHT | {"convergence", "recovery", "final"}


def plan(output, run_id, policy, steps, checkpoint_bytes, extra_bytes, reserve_bytes,
         interval=None):
    if policy not in POLICIES or steps < 1 or min(checkpoint_bytes, extra_bytes, reserve_bytes) < 0:
        raise ValueError("invalid policy, steps or byte estimate")
    if not run_id.strip() or (interval is not None and interval < 1):
        raise ValueError("run ID and positive checkpoint interval required")
    path = Path(output).expanduser().resolve()
    ancestor = path
    while not ancestor.exists():
        ancestor = ancestor.parent
    if not ancestor.is_dir():
        raise ValueError("output ancestor must be a directory")
    save_final = policy not in LIGHTWEIGHT
    if interval is None and policy in {"convergence", "recovery"}:
        interval = max(1, (steps + 1) // 2)
    periodic = steps // interval if interval else 0
    count = periodic + int(save_final and (interval is None or steps % interval != 0))
    if count and not checkpoint_bytes:
        raise ValueError("supply a positive complete checkpoint byte estimate")
    required = count * checkpoint_bytes + extra_bytes
    free = shutil.disk_usage(ancestor).free
    return dict(run_id=run_id, policy=policy, configured_output=str(output),
                physical_output=str(path), steps=steps, interval=interval,
                save_final=save_final, checkpoint_count=count,
                checkpoint_bytes=checkpoint_bytes, extra_bytes=extra_bytes,
                estimated_bytes=required, reserve_bytes=reserve_bytes,
                free_bytes=free, fits=required + reserve_bytes <= free)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    parser.add_argument("run_id")
    parser.add_argument("policy", choices=sorted(POLICIES))
    parser.add_argument("--steps", type=int, required=True)
    parser.add_argument("--checkpoint-bytes", type=int, default=0)
    parser.add_argument("--extra-bytes", type=int, required=True)
    parser.add_argument("--reserve-bytes", type=int, required=True)
    parser.add_argument("--interval", type=int)
    args = parser.parse_args()
    try:
        report = plan(**vars(args))
    except (ValueError, OSError, RuntimeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["fits"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
