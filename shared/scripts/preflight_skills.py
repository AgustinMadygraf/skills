import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def run(script: str) -> None:
    cmd = [sys.executable, str(HERE / script)]
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> int:
    run("lint_skills.py")
    run("test_lint_skills_smoke.py")
    run("sync_agents_catalog.py")
    run("skills_health_report.py")
    print("Preflight: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
