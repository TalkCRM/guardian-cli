#!/usr/bin/env python3
"""AWS evidence collection helper (read-only + optional S3 upload)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import yaml


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


def classify_env(name: str, rules: list[tuple[str, list[str]]]) -> str:
    for label, patterns in rules:
        for pattern in patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return label
    return "unknown"


def build_env_rules(defaults: dict) -> list[tuple[str, list[str]]]:
    cfg = defaults.get("env_classification", {})
    if cfg:
        return [(label, list(patterns)) for label, patterns in cfg.items()]
    return [
        ("staging", ["stg", "staging", "stage", "dev", "test", "sandbox"]),
        ("prod", ["prod", "production"]),
    ]


def discover_log_groups(
    profile: str | None,
    region: str,
    prefixes: list[str],
    keywords: str,
    max_items: int,
    dry_run: bool,
) -> list[str]:
    pattern = re.compile(keywords, re.IGNORECASE)
    found: set[str] = set()
    for prefix in prefixes:
        cmd = aws_cmd(
            [
                "logs",
                "describe-log-groups",
                "--log-group-name-prefix",
                prefix,
                "--max-items",
                str(max_items),
                "--output",
                "json",
            ],
            profile,
            region,
        )
        data = run_cmd(cmd, dry_run)
        if dry_run:
            continue
        payload = json.loads(data)
        for group in payload.get("logGroups", []):
            name = group.get("logGroupName", "")
            if pattern.search(name):
                found.add(name)

    if not prefixes:
        cmd = aws_cmd(
            [
                "logs",
                "describe-log-groups",
                "--max-items",
                str(max_items),
                "--output",
                "json",
            ],
            profile,
            region,
        )
        data = run_cmd(cmd, dry_run)
        if dry_run:
            return sorted(found)
        payload = json.loads(data)
        for group in payload.get("logGroups", []):
            name = group.get("logGroupName", "")
            if pattern.search(name):
                found.add(name)

    return sorted(found)


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
    parser.add_argument("--config", default=None, help="Config YAML path")
    parser.add_argument(
        "--discover-log-groups",
        action="store_true",
        help="Discover log groups by keyword across regions",
    )
    parser.add_argument(
        "--discover-keywords",
        default="aicc|talkcrm|llm|chat|rag|bedrock",
        help="Regex keywords for discovery",
    )
    parser.add_argument(
        "--discover-prefix",
        action="append",
        default=["/aws/lambda", "/aws/ecs", "/aws/apigateway", "/ecs/"],
        help="Log group prefix to scan (repeatable)",
    )
    parser.add_argument(
        "--discover-max-items",
        type=int,
        default=200,
        help="Max items per prefix query",
    )
    parser.add_argument(
        "--discover-out",
        default=None,
        help="Write discovered log groups to file",
    )
    parser.add_argument(
        "--env-filter",
        choices=["staging", "prod", "unknown", "all"],
        default="all",
        help="Filter discovered log groups by environment",
    )

    args = parser.parse_args()

    defaults: dict = {}
    if args.config:
        cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
        defaults = cfg.get("aws_evidence", {})

        def has(flag: str) -> bool:
            return flag in sys.argv

        if not has("--profile"):
            args.profile = defaults.get("profile", args.profile)
        if not has("--regions"):
            args.regions = defaults.get("regions", args.regions)
        if not has("--s3-bucket"):
            args.s3_bucket = defaults.get("s3_bucket", args.s3_bucket)
        if not has("--s3-prefix"):
            args.s3_prefix = defaults.get("s3_prefix", args.s3_prefix)
        if not has("--discover-log-groups"):
            args.discover_log_groups = defaults.get("discover_log_groups", args.discover_log_groups)
        if not has("--discover-keywords"):
            args.discover_keywords = defaults.get("discover_keywords", args.discover_keywords)
        if not has("--discover-prefix") and defaults.get("discover_prefixes"):
            args.discover_prefix = defaults.get("discover_prefixes", args.discover_prefix)
        if not has("--discover-max-items"):
            args.discover_max_items = defaults.get("discover_max_items", args.discover_max_items)
        if not has("--env-filter"):
            args.env_filter = defaults.get("env_filter", args.env_filter)

        if defaults.get("log_groups") and not has("--log-group"):
            for lg in defaults.get("log_groups", []):
                args.log_group.append(lg)

        if defaults.get("cloudtrail") is True and not has("--cloudtrail"):
            args.cloudtrail = True

    if not args.regions:
        raise SystemExit("--regions is required (e.g., ap-northeast-2 us-east-1)")

    start = parse_iso(args.start)
    end = parse_iso(args.end)
    run_id = args.run_id or f"run-{datetime.utcnow().date().isoformat()}"

    out_root = Path(args.out) / run_id / "logs"
    ensure_dir(out_root)

    outputs: list[OutputFile] = []
    discovered: dict[str, list[dict[str, str]]] = {}
    env_rules = build_env_rules(defaults if args.config else {})
    region_log_groups: dict[str, list[str]] = {r: [] for r in args.regions}

    if args.discover_log_groups:
        for region in args.regions:
            groups = discover_log_groups(
                args.profile,
                region,
                args.discover_prefix,
                args.discover_keywords,
                args.discover_max_items,
                args.dry_run,
            )
            classified = []
            for group in groups:
                env = classify_env(group, env_rules)
                classified.append({"name": group, "env": env})
                if args.env_filter == "all" or env == args.env_filter:
                    region_log_groups[region].append(group)
            discovered[region] = classified
        if args.discover_out and not args.dry_run:
            out_path = Path(args.discover_out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(discovered, indent=2), encoding="utf-8")

    if args.log_group:
        for region in args.regions:
            for group in args.log_group:
                env = classify_env(group, env_rules)
                if args.env_filter == "all" or env == args.env_filter:
                    region_log_groups[region].append(group)

    for region in region_log_groups:
        region_log_groups[region] = sorted(set(region_log_groups[region]))

    for region in args.regions:
        if args.cloudtrail:
            outputs.append(collect_cloudtrail(out_root, args.profile, region, start, end, args.dry_run))
        for lg in region_log_groups[region]:
            outputs.append(collect_log_group(out_root, args.profile, region, lg, start, end, args.dry_run))

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
