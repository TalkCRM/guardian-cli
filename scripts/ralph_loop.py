#!/usr/bin/env python3
"""Ralph Loop helper.

Subcommands:
  init     Create a run folder with manifest and run log.
  validate Validate task YAML structure.
  summary  Generate a markdown summary from task YAML.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FIELDS = ["id", "objective", "steps", "pass_criteria", "evidence", "max_iterations"]


def load_tasks(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return []
    if isinstance(data, dict) and "task" in data:
        return [data["task"]]
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "tasks" in data:
        return data["tasks"]
    raise ValueError("Unsupported task format: expected 'task', 'tasks', or list")


def validate_tasks(paths: list[Path]) -> int:
    errors = []
    for path in paths:
        tasks = load_tasks(path)
        if not tasks:
            errors.append(f"{path}: no tasks found")
            continue
        for idx, task in enumerate(tasks, start=1):
            missing = [field for field in REQUIRED_FIELDS if field not in task]
            if missing:
                errors.append(f"{path} [task {idx}]: missing {', '.join(missing)}")
    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Validation OK")
    return 0


def init_run(out_dir: Path, run_id: str, owner: str, environment: str) -> None:
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "owner": owner,
        "environment": environment,
        "artifacts": {
            "logs": [],
            "metrics": [],
            "reports": [],
            "screenshots": [],
        },
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    template = Path("docs/ralph_loop/run_log_template.md")
    if template.exists():
        content = template.read_text(encoding="utf-8")
        content = content.replace("{{RUN_ID}}", run_id)
        content = content.replace("{{DATE}}", datetime.utcnow().date().isoformat())
        content = content.replace("{{OWNER}}", owner)
        content = content.replace("{{ENVIRONMENT}}", environment)
        (run_dir / "run_log.md").write_text(content, encoding="utf-8")


def summary(paths: list[Path], out: Path) -> None:
    rows = []
    for path in paths:
        for task in load_tasks(path):
            rows.append(
                {
                    "id": task.get("id", ""),
                    "objective": task.get("objective", ""),
                    "max_iterations": task.get("max_iterations", ""),
                    "evidence": ", ".join(task.get("evidence", [])),
                }
            )

    lines = ["# Ralph Loop Summary", "", f"Generated: {datetime.utcnow().isoformat()}Z", ""]
    lines.append("| ID | Objective | Max Iterations | Evidence |")
    lines.append("|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['objective']} | {row['max_iterations']} | {row['evidence']} |"
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ralph Loop helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init_p = sub.add_parser("init", help="Create run folder")
    init_p.add_argument("--out", default="reports/ralph_loop", help="Output base directory")
    init_p.add_argument("--run-id", default=None, help="Run ID (default: run-YYYY-MM-DD)")
    init_p.add_argument("--owner", default="Security Team", help="Owner name")
    init_p.add_argument("--env", default="staging", help="Environment")

    val_p = sub.add_parser("validate", help="Validate task YAML")
    val_p.add_argument("--tasks", nargs="+", required=True, help="Task YAML paths")

    sum_p = sub.add_parser("summary", help="Generate summary markdown")
    sum_p.add_argument("--tasks", nargs="+", required=True, help="Task YAML paths")
    sum_p.add_argument("--out", required=True, help="Output markdown path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "init":
        run_id = args.run_id or f"run-{datetime.utcnow().date().isoformat()}"
        init_run(Path(args.out), run_id, args.owner, args.env)
        print(f"Created run folder: {args.out}/{run_id}")
        return 0

    if args.cmd == "validate":
        paths = [Path(p) for p in args.tasks]
        return validate_tasks(paths)

    if args.cmd == "summary":
        paths = [Path(p) for p in args.tasks]
        summary(paths, Path(args.out))
        print(f"Summary written: {args.out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
