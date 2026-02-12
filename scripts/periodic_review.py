#!/usr/bin/env python3
"""Periodic review planner for Ralph Loop.

Creates a schedule (monthly or quarterly) and optionally initializes run folders.
"""

from __future__ import annotations

import argparse
from calendar import monthrange
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


def parse_weekday(value: str) -> int:
    mapping = {
        "mon": 0,
        "monday": 0,
        "tue": 1,
        "tues": 1,
        "tuesday": 1,
        "wed": 2,
        "wednesday": 2,
        "thu": 3,
        "thurs": 3,
        "thursday": 3,
        "fri": 4,
        "friday": 4,
        "sat": 5,
        "saturday": 5,
        "sun": 6,
        "sunday": 6,
    }
    key = value.strip().lower()
    if key not in mapping:
        raise ValueError(f"Unsupported weekday: {value}")
    return mapping[key]


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    delta = (weekday - first.weekday() + 7) % 7
    day = 1 + delta + (n - 1) * 7
    last_day = monthrange(year, month)[1]
    if day > last_day:
        # fallback to last occurrence of weekday in the month
        day = last_day
        while date(year, month, day).weekday() != weekday:
            day -= 1
    return date(year, month, day)


def iter_months(cadence: str, year: int) -> Iterable[int]:
    if cadence == "monthly":
        return range(1, 13)
    if cadence == "quarterly":
        return [1, 4, 7, 10]
    raise ValueError("cadence must be 'monthly' or 'quarterly'")


def write_plan(
    out: Path,
    year: int,
    cadence: str,
    weekday: int,
    week_of_month: int,
    timezone: str,
    window: str,
    owner: str,
    environment: str,
    create_runs: bool,
    runs_out: Path,
) -> None:
    rows = []
    for month in iter_months(cadence, year):
        run_date = nth_weekday(year, month, weekday, week_of_month)
        run_id = f"run-{run_date.isoformat()}"
        rows.append((run_id, run_date.isoformat(), window, timezone))
        if create_runs:
            run_dir = runs_out / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "manifest.json").write_text(
                "{\n"
                f"  \"run_id\": \"{run_id}\",\n"
                f"  \"created_at\": \"{datetime.utcnow().isoformat()}Z\",\n"
                f"  \"owner\": \"{owner}\",\n"
                f"  \"environment\": \"{environment}\"\n"
                "}\n",
                encoding="utf-8",
            )

    lines = [f"# Periodic Review Plan ({year})", "", f"Cadence: {cadence}", ""]
    lines.append("| Run ID | Date | Window | Timezone |")
    lines.append("|---|---|---|---|")
    for run_id, run_date, window, tz in rows:
        lines.append(f"| {run_id} | {run_date} | {window} | {tz} |")

    lines += [
        "",
        "## Defaults",
        f"- Week of month: {week_of_month}",
        f"- Weekday: {weekday}",
        f"- Owner: {owner}",
        f"- Environment: {environment}",
        "",
        "## Notes",
        "- If the nth weekday does not exist in a month, the last weekday is used.",
    ]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Periodic review planner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    plan = sub.add_parser("plan", help="Generate periodic review plan")
    plan.add_argument("--cadence", choices=["monthly", "quarterly"], default="quarterly")
    plan.add_argument("--year", type=int, default=date.today().year)
    plan.add_argument("--weekday", default="tue")
    plan.add_argument("--week", type=int, default=2, help="Week of month (1-5)")
    plan.add_argument("--timezone", default="Asia/Seoul")
    plan.add_argument("--window", default="09:00-18:00")
    plan.add_argument("--owner", default="Security Team")
    plan.add_argument("--env", default="staging")
    plan.add_argument("--out", default="docs/ralph_loop/periodic_plan.md")
    plan.add_argument("--create-runs", action="store_true")
    plan.add_argument("--runs-out", default="reports/ralph_loop")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "plan":
        weekday = parse_weekday(args.weekday)
        write_plan(
            Path(args.out),
            args.year,
            args.cadence,
            weekday,
            args.week,
            args.timezone,
            args.window,
            args.owner,
            args.env,
            args.create_runs,
            Path(args.runs_out),
        )
        print(f"Plan written: {args.out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
