#!/usr/bin/env python3
"""Periodic review planner for Ralph Loop.

Creates a schedule (monthly or quarterly), optionally initializes run folders,
and can output a calendar (.ics) or a monthly markdown calendar.
"""

from __future__ import annotations

import argparse
from calendar import monthrange, month_name
from datetime import date, datetime, time
from pathlib import Path
from typing import Iterable
import sys

import yaml


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


def build_schedule(
    year: int,
    cadence: str,
    weekday: int,
    week_of_month: int,
) -> list[tuple[str, date]]:
    rows: list[tuple[str, date]] = []
    for month in iter_months(cadence, year):
        run_date = nth_weekday(year, month, weekday, week_of_month)
        run_id = f"run-{run_date.isoformat()}"
        rows.append((run_id, run_date))
    return rows


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
    schedule = build_schedule(year, cadence, weekday, week_of_month)
    rows = [(run_id, run_date.isoformat(), window, timezone) for run_id, run_date in schedule]
    if create_runs:
        for run_id, run_date in schedule:
            run_dir = runs_out / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "manifest.json").write_text(
                "{\n"
                f"  \"run_id\": \"{run_id}\",\n"
                f"  \"created_at\": \"{datetime.utcnow().isoformat()}Z\",\n"
                f"  \"owner\": \"{owner}\",\n"
                f"  \"environment\": \"{environment}\",\n"
                f"  \"planned_date\": \"{run_date.isoformat()}\"\n"
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


def write_calendar_md(
    out: Path,
    year: int,
    cadence: str,
    weekday: int,
    week_of_month: int,
) -> None:
    schedule = build_schedule(year, cadence, weekday, week_of_month)
    by_month: dict[int, list[date]] = {}
    for _, run_date in schedule:
        by_month.setdefault(run_date.month, []).append(run_date)

    lines = [f"# Periodic Review Calendar ({year})", ""]
    for month in iter_months(cadence, year):
        lines.append(f"## {month_name[month]}")
        dates = by_month.get(month, [])
        if not dates:
            lines.append("- (none)")
        else:
            for d in dates:
                lines.append(f"- {d.isoformat()}")
        lines.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def write_ics(
    out: Path,
    year: int,
    cadence: str,
    weekday: int,
    week_of_month: int,
    window: str,
    timezone: str,
    summary: str,
) -> None:
    schedule = build_schedule(year, cadence, weekday, week_of_month)
    start_str, end_str = window.split("-", 1)
    start_t = time.fromisoformat(start_str)
    end_t = time.fromisoformat(end_str)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//TalkCRM//RalphLoop//EN",
        "CALSCALE:GREGORIAN",
    ]
    for run_id, run_date in schedule:
        dt_start = datetime.combine(run_date, start_t)
        dt_end = datetime.combine(run_date, end_t)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{run_id}@talkcrm",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;TZID={timezone}:{dt_start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID={timezone}:{dt_end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:Periodic Ralph Loop review ({run_id})",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")

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
    plan.add_argument("--calendar-md", default=None, help="Output markdown calendar path")
    plan.add_argument("--calendar-ics", default=None, help="Output ICS calendar path")
    plan.add_argument("--summary", default="Ralph Loop Review", help="Calendar event summary")
    plan.add_argument("--config", default=None, help="Config YAML path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "plan":
        if args.config:
            cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
            defaults = cfg.get("ralph_loop", {})

            def has(flag: str) -> bool:
                return flag in sys.argv

            if not has("--cadence"):
                args.cadence = defaults.get("cadence", args.cadence)
            if not has("--year"):
                args.year = defaults.get("year", args.year)
            if not has("--weekday"):
                args.weekday = defaults.get("weekday", args.weekday)
            if not has("--week"):
                args.week = defaults.get("week", args.week)
            if not has("--timezone"):
                args.timezone = defaults.get("timezone", args.timezone)
            if not has("--window"):
                args.window = defaults.get("window", args.window)
            if not has("--owner"):
                args.owner = defaults.get("owner", args.owner)
            if not has("--env"):
                args.env = defaults.get("environment", args.env)
            if not has("--out"):
                args.out = defaults.get("plan_output", args.out)
            if not has("--runs-out"):
                args.runs_out = defaults.get("run_output", args.runs_out)
            if not has("--calendar-md"):
                args.calendar_md = defaults.get("calendar_md", args.calendar_md)
            if not has("--calendar-ics"):
                args.calendar_ics = defaults.get("calendar_ics", args.calendar_ics)

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
        if args.calendar_md:
            write_calendar_md(Path(args.calendar_md), args.year, args.cadence, weekday, args.week)
        if args.calendar_ics:
            write_ics(
                Path(args.calendar_ics),
                args.year,
                args.cadence,
                weekday,
                args.week,
                args.window,
                args.timezone,
                args.summary,
            )
        print(f"Plan written: {args.out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
