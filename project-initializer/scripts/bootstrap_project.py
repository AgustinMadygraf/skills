#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict


DIRS = [
    "src/entities",
    "src/use_cases",
    "src/interface_adapters/presenters",
    "src/interface_adapters/gateways",
    "src/infrastructure",
    "src/infrastructure/settings",
    "docs",
    "tests",
]

GITKEEP_DIRS = [
    "src/entities",
    "src/use_cases",
    "src/interface_adapters/presenters",
    "src/interface_adapters/gateways",
    "docs",
    "tests",
]


def prompt_if_missing(value: str | None, label: str) -> str:
    if value:
        return value.strip()
    return input(f"{label}: ").strip()


def write_if_missing(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def parse_env_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keys: set[str] = set()
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap project initializer")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--project-name", help="Project name")
    parser.add_argument("--project-goal", help="Project goal")
    parser.add_argument("--runtime-command", help="Runtime command")
    parser.add_argument("--notes", help="Additional notes")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    created_dirs: list[str] = []
    created_files: list[str] = []

    project_name = prompt_if_missing(args.project_name, "Project name")
    project_goal = prompt_if_missing(args.project_goal, "Project goal")
    runtime_command = prompt_if_missing(args.runtime_command, "Runtime command (e.g. python run.py)")
    notes = prompt_if_missing(args.notes, "Notes")

    for rel in DIRS:
        p = repo_root / rel
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            created_dirs.append(rel)

    for rel in GITKEEP_DIRS:
        p = repo_root / rel / ".gitkeep"
        if write_if_missing(p, "", args.force):
            created_files.append(str(p.relative_to(repo_root)))

    readme_content = (
        "<!-- Path: README.md -->\n"
        f"# {project_name}\n\n"
        "## Bootstrap Context\n\n"
        f"- Project name: {project_name}\n"
        f"- Project goal: {project_goal}\n"
        f"- Runtime command: {runtime_command}\n"
        f"- Notes: {notes}\n"
    )
    if write_if_missing(repo_root / "README.md", readme_content, args.force):
        created_files.append("README.md")

    if write_if_missing(repo_root / "run.py", "", args.force):
        created_files.append("run.py")

    gitignore_content = (
        "# Path: .gitignore\n"
        "__pycache__/\n"
        "*.pyc\n"
        ".venv/\n"
        ".env\n"
        ".pytest_cache/\n"
        ".mypy_cache/\n"
        "reports/\n"
    )
    if write_if_missing(repo_root / ".gitignore", gitignore_content, args.force):
        created_files.append(".gitignore")

    env_content = (
        "# Path: .env\n"
        "APP_ENV=local\n"
        "LOG_LEVEL=INFO\n"
    )
    if write_if_missing(repo_root / ".env", env_content, args.force):
        created_files.append(".env")

    env_example_content = (
        "# Path: .env.example\n"
        "APP_ENV=local\n"
        "LOG_LEVEL=INFO\n"
    )
    if write_if_missing(repo_root / ".env.example", env_example_content, args.force):
        created_files.append(".env.example")

    config_py = (
        '"""\n'
        "Path: src/infrastructure/settings/config.py\n"
        '"""\n\n'
        "APP_ENV = 'local'\n"
        "LOG_LEVEL = 'INFO'\n"
    )
    if write_if_missing(repo_root / "src/infrastructure/settings/config.py", config_py, args.force):
        created_files.append("src/infrastructure/settings/config.py")

    logger_py = (
        '"""\n'
        "Path: src/infrastructure/settings/logger.py\n"
        '"""\n\n'
        "import logging\n\n"
        "def get_logger(name: str) -> logging.Logger:\n"
        "    return logging.getLogger(name)\n"
    )
    if write_if_missing(repo_root / "src/infrastructure/settings/logger.py", logger_py, args.force):
        created_files.append("src/infrastructure/settings/logger.py")

    env_keys = parse_env_keys(repo_root / ".env")
    env_example_keys = parse_env_keys(repo_root / ".env.example")
    env_parity_ok = env_keys == env_example_keys

    summary: Dict[str, object] = {
        "repo_root": str(repo_root),
        "created_dirs": created_dirs,
        "created_files": created_files,
        "env_parity_ok": env_parity_ok,
        "env_only": sorted(env_keys - env_example_keys),
        "env_example_only": sorted(env_example_keys - env_keys),
        "ok": env_parity_ok,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(f"BOOTSTRAP={'PASS' if env_parity_ok else 'FAIL'}")
        print(f"REPO={repo_root}")
        print(f"CREATED_DIRS={len(created_dirs)}")
        print(f"CREATED_FILES={len(created_files)}")
        print(f"ENV_PARITY_OK={env_parity_ok}")
        if not env_parity_ok:
            print(f"- env_only={summary['env_only']}")
            print(f"- env_example_only={summary['env_example_only']}")

    return 0 if env_parity_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())

