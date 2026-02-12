#!/usr/bin/env python3
"""AWS evidence collection helper (read-only + optional S3 upload)."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def parse_iso(value: str) -> datetime:
    if "T" not in value:
        # date-only -> midnight UTC
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def to_epoch_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def aws_cmd(args: list[str], profile: str | None, region: str | None) -> list[str]:
    cmd = ["aws"]
    if profile:
        cmd += ["--profile", profile]
    if region:
        cmd += ["--region", region]
    cmd += args
    return cmd


def run_cmd(cmd: list[str], dry_run: bool) -> str:
    if dry_run:
        print("DRY-RUN:", " ".join(cmd))
        return "{}"
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return proc.stdout


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(value: str) -> str:
    return value.strip("/").replace("/", "_").replace(":", "_")


@dataclass
class OutputFile:
    local_path: Path
    s3_key: str


def collect_cloudtrail(
    out_dir: Path,
    profile: str | None,
    region: str,
    start: datetime,
    end: datetime,
    dry_run: bool,
) -> OutputFile:
    ensure_dir(out_dir)
    filename = f"cloudtrail-events-{region}.json"
    local = out_dir / filename
    cmd = aws_cmd(
        [
            "cloudtrail",
            "lookup-events",
            "--start-time",
            start.isoformat(),
            "--end-time",
            end.isoformat(),
            "--output",
            "json",
        ],
        profile,
        region,
    )
    data = run_cmd(cmd, dry_run)
    if not dry_run:
        local.write_text(data, encoding="utf-8")
    return OutputFile(local_path=local, s3_key=f"logs/{filename}")


def collect_log_group(
    out_dir: Path,
    profile: str | None,
    region: str,
    log_group: str,
    start: datetime,
    end: datetime,
    dry_run: bool,
) -> OutputFile:
    ensure_dir(out_dir)
    safe_name = sanitize_filename(log_group)
    filename = f"cloudwatch-{region}-{safe_name}.json"
    local = out_dir / filename
    cmd = aws_cmd(
        [
            "logs",
            "filter-log-events",
            "--log-group-name",
            log_group,
            "--start-time",
            str(to_epoch_ms(start)),
            "--end-time",
            str(to_epoch_ms(end)),
            "--output",
            "json",
        ],
        profile,
        region,
    )
    data = run_cmd(cmd, dry_run)
    if not dry_run:
        local.write_text(data, encoding="utf-8")
    return OutputFile(local_path=local, s3_key=f"logs/{filename}")


def upload_s3(
    profile: str | None,
    region: str | None,
    bucket: str,
    prefix: str,
    run_id: str,
    outputs: Iterable[OutputFile],
    dry_run: bool,
) -> None:
    for item in outputs:
        key = f"{prefix}/{run_id}/{item.s3_key}"
        cmd = aws_cmd(["s3", "cp", str(item.local_path), f"s3://{bucket}/{key}"], profile, region)
        run_cmd(cmd, dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description="AWS evidence collector")
    parser.add_argument("--profile", default=None, help="AWS profile")
    parser.add_argument("--regions", nargs="+", help="Regions to scan")
    parser.add_argument("--log-group", action="append", default=[], help="Log group name")
    parser.add_argument("--cloudtrail", action="store_true", help="Collect CloudTrail events")
    parser.add_argument("--start", required=True, help="Start time (YYYY-MM-DD or ISO)")
    parser.add_argument("--end", required=True, help="End time (YYYY-MM-DD or ISO)")
    parser.add_argument("--out", default="compliance-evidence", help="Local output root")
    parser.add_argument("--run-id", default=None, help="Run ID (default: run-YYYY-MM-DD)")
    parser.add_argument("--s3-bucket", default=None, help="Upload to S3 bucket")
    parser.add_argument("--s3-prefix", default="compliance-evidence", help="S3 prefix")
    parser.add_argument("--s3-region", default=None, help="S3 region override")
    parser.add_argument("--dry-run", action="store_true", help="Print commands only")

    args = parser.parse_args()

    if not args.regions:
        raise SystemExit("--regions is required (e.g., ap-northeast-2 us-east-1)")

    start = parse_iso(args.start)
    end = parse_iso(args.end)
    run_id = args.run_id or f"run-{datetime.utcnow().date().isoformat()}"

    out_root = Path(args.out) / run_id / "logs"
    ensure_dir(out_root)

    outputs: list[OutputFile] = []
    for region in args.regions:
        if args.cloudtrail:
            outputs.append(collect_cloudtrail(out_root, args.profile, region, start, end, args.dry_run))
        for lg in args.log_group:
            outputs.append(
                collect_log_group(out_root, args.profile, region, lg, start, end, args.dry_run)
            )

    # build manifest
    manifest_path = Path(args.out) / run_id / "manifest.json"
    if not args.dry_run:
        manifest = {
            "run_id": run_id,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "files": {str(p.local_path): f"sha256:{sha256_file(p.local_path)}" for p in outputs},
        }
        ensure_dir(manifest_path.parent)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        outputs.append(OutputFile(local_path=manifest_path, s3_key="manifest.json"))

    if args.s3_bucket:
        upload_s3(
            args.profile,
            args.s3_region,
            args.s3_bucket,
            args.s3_prefix,
            run_id,
            outputs,
            args.dry_run,
        )

    print(f"Collected {len(outputs)} files in {args.out}/{run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
