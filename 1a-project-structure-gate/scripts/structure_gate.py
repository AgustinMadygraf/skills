#!/usr/bin/env python3
"""
Path: scripts/structure_gate.py

Structure Gate - Auditoria de estructura: env/layout/python-file.

Wrapper que ejecuta project_gate.py con --structure-gate-only --check.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Structure Gate")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--check", action="store_true", help="Only validate without writing files")
    parser.add_argument("--fix-python", action="store_true", help="Auto-fix python-file-policy issues")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    project_gate = script_dir / "project_gate.py"

    cmd = [
        sys.executable,
        str(project_gate),
        "--repo-root", args.repo_root,
        "--structure-gate-only",
    ]

    if args.check:
        cmd.append("--check")
    if args.fix_python:
        cmd.append("--fix-python")
    if args.json:
        cmd.append("--json")
    if args.force:
        cmd.append("--force")

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
