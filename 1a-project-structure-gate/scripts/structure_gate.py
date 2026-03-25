#!/usr/bin/env python3
"""
Path: scripts/structure_gate.py

Structure Gate - Auditoria pura de estructura: env/layout/python-file.

Wrapper que ejecuta project_gate.py con --structure-gate-only --check.
NO realiza correcciones (para eso usar 1b-project-structure-repair).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project Structure Gate - Solo auditoria, sin correcciones"
    )
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    project_gate = script_dir / "project_gate.py"

    cmd = [
        sys.executable,
        str(project_gate),
        "--repo-root", args.repo_root,
        "--structure-gate-only",
        "--check",  # Siempre modo check (sin correcciones)
    ]

    if args.json:
        cmd.append("--json")

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
