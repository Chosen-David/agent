"""Plan checkpoint writes against the physical output filesystem before launch."""
import argparse
import json
from pathlib import Path
import shutil


LIGHTWEIGHT = {"profile", "correctness", "spectral"}
POLICIES = LIGHTWEIGHT | {"convergence", "recovery", "final"}


def plan(output, run_id, policy, steps, checkpoint_bytes, extra_bytes, reserve_bytes,
         interval=None, quota_free_bytes=None, committed_bytes=0, staging_bytes=0,
         watermarks=(70, 80, 90, 95), essential=False, previous_pressure=None):
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
    if (min(committed_bytes, staging_bytes) < 0 or
            (quota_free_bytes is not None and quota_free_bytes < 0)):
        raise ValueError("negative quota, staging or outstanding reservation")
    if len(watermarks) != 4 or not 0 < watermarks[0] < watermarks[1] < watermarks[2] < watermarks[3] <= 100:
        raise ValueError("four strictly increasing watermarks required")
    required = count * checkpoint_bytes + extra_bytes + staging_bytes
    disk = shutil.disk_usage(ancestor)
    free = disk.free if quota_free_bytes is None else min(disk.free, quota_free_bytes)
    available = max(0, free - committed_bytes)
    projected = 100 * (disk.total - disk.free + committed_bytes + required) / disk.total
    stages = ("normal", "plan", "review-authorized-reclamation", "restrict", "emergency")
    pressure = stages[sum(projected >= limit for limit in watermarks)]
    if previous_pressure is not None and previous_pressure not in stages:
        raise ValueError("unknown previous storage pressure")
    if previous_pressure in stages[2:] and pressure == 'plan':
        pressure = 'review-authorized-reclamation'
    permitted = pressure != "emergency" and (pressure != "restrict" or essential)
    level = {"profile": "L0", "correctness": "L1", "spectral": "L1", "final": "L2",
             "convergence": "L3", "recovery": "L3"}[policy]
    if count and policy in LIGHTWEIGHT:
        level = "L3"
    return dict(run_id=run_id, policy=policy, planned_asset_level=level, configured_output=str(output),
                physical_output=str(path), steps=steps, interval=interval,
                save_final=save_final, checkpoint_count=count,
                checkpoint_bytes=checkpoint_bytes, extra_bytes=extra_bytes,
                estimated_bytes=required, reserve_bytes=reserve_bytes,
                free_bytes=free, available_after_reservations=available, quota_free_bytes=quota_free_bytes,
                disk_device=ancestor.stat().st_dev, watermarks=list(watermarks), essential=essential,
                committed_bytes=committed_bytes, staging_bytes=staging_bytes,
                projected_disk_percent=projected, pressure=pressure,
                fits=permitted and required + reserve_bytes <= available)


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
    parser.add_argument("--quota-free-bytes", type=int)
    parser.add_argument("--committed-bytes", type=int, default=0)
    parser.add_argument("--staging-bytes", type=int, default=0)
    parser.add_argument("--watermarks", type=float, nargs=4, default=(70,80,90,95))
    parser.add_argument("--essential", action="store_true")
    parser.add_argument("--previous-pressure")
    args = parser.parse_args()
    try:
        report = plan(**vars(args))
    except (ValueError, OSError, RuntimeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["fits"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
