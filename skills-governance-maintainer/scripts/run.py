#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def list_skill_dirs(skills_root: Path):
    return sorted([p for p in skills_root.iterdir() if p.is_dir() and not p.name.startswith(".")], key=lambda p: p.name)


def custom_skills(skills_root: Path):
    return [p for p in list_skill_dirs(skills_root) if p.name not in {".system", "shared"}]


def parse_agents_entries(agents_md: str):
    names = []
    files = []
    for line in agents_md.splitlines():
        if not line.startswith("- "):
            continue
        m = re.match(r"^- ([a-z0-9-]+)", line)
        if m:
            names.append(m.group(1))
        fm = re.search(r"\(file:\s*([^)]+)\)", line)
        if fm:
            files.append(Path(fm.group(1).replace("/", "\\")))
    return names, files


def run(cmd: list[str], cwd: Path):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def ensure_line_after(path: Path, anchor: str, line_to_add: str) -> bool:
    text = read_text(path)
    if line_to_add in text:
        return False
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == anchor.strip():
            lines.insert(i + 1, line_to_add)
            write_text(path, "\n".join(lines) + "\n")
            return True
    return False


def auto_fix_precedence(skills_root: Path):
    fixes = []
    targets = [
        (
            skills_root / "frontend-testing-vue-ts-tailwind" / "SKILL.md",
            "## Cu\\u00e1ndo usarlo",
            "Si el pedido es general de testing pero el stack es Vue 3 + TypeScript + Tailwind, este skill tiene precedencia sobre `testing-general`.",
        ),
        (
            skills_root / "skill-backend-testing" / "SKILL.md",
            "## Alcance por defecto",
            "Si el pedido es de testing en Python/FastAPI, este skill tiene precedencia sobre `testing-general`.",
        ),
        (
            skills_root / "frontend-best-practices-audit" / "SKILL.md",
            "## Alcance de la Auditor\\u00eda",
            "Para auditorias de frontend Vue/TS/UI, este skill tiene precedencia sobre `clean-architecture-orchestrator`.",
        ),
        (
            skills_root / "skill-backend-code-audit" / "SKILL.md",
            "## Alcance",
            "Para auditorias backend Python/FastAPI, este skill tiene precedencia sobre `clean-architecture-orchestrator`.",
        ),
        (
            skills_root / "clean-architecture-orchestrator" / "SKILL.md",
            "## Integracion recomendada",
            "Si el pedido esta claramente acotado a frontend Vue/TS/UI o backend FastAPI, priorizar los skills especializados antes de `clean-architecture-orchestrator`.",
        ),
    ]

    for path, anchor, line in targets:
        if path.exists() and ensure_line_after(path, anchor, line):
            fixes.append(str(path))
    return fixes


def main() -> int:
    parser = argparse.ArgumentParser(description="Run skills governance audit")
    parser.add_argument("--auto-fix", action="store_true", help="Apply safe precedence fixes in SKILL.md files")
    args = parser.parse_args()

    me = Path(__file__).resolve()
    skills_root = me.parents[2]
    codex_root = skills_root.parent
    agents_path = codex_root / "AGENTS.md"

    auto_fixed = auto_fix_precedence(skills_root) if args.auto_fix else []

    all_dirs = list_skill_dirs(skills_root)
    custom = custom_skills(skills_root)
    installed_custom = [p.name for p in custom if (p / "SKILL.md").exists()]

    agents_txt = read_text(agents_path) if agents_path.exists() else ""
    listed_names, listed_files = parse_agents_entries(agents_txt)

    missing_in_agents = sorted(set(installed_custom) - set(listed_names))
    stale_in_agents = sorted(set([n for n in listed_names if n not in {"skill-creator", "skill-installer"}]) - set(installed_custom))
    broken_paths = [str(p) for p in listed_files if not p.exists()]

    lint_rc, lint_out = run(["python", str(skills_root / "shared" / "scripts" / "lint_skills.py")], skills_root)
    validator = skills_root / ".system" / "skill-creator" / "scripts" / "quick_validate.py"

    validation = []
    for s in custom:
        rc, out = run(["python", str(validator), str(s)], skills_root)
        validation.append((s.name, rc == 0, out.splitlines()[-1] if out else ""))

    overlap_notes = []
    pairs = [
        ("testing-general", "frontend-testing-vue-ts-tailwind"),
        ("testing-general", "skill-backend-testing"),
        ("clean-architecture-orchestrator", "frontend-best-practices-audit"),
        ("clean-architecture-orchestrator", "skill-backend-code-audit"),
    ]
    installed = set(installed_custom)
    for a, b in pairs:
        if a in installed and b in installed:
            overlap_notes.append(f"{a} <-> {b}")

    report = []
    report.append("# Skills Governance Report")
    report.append("")
    report.append(f"- Skills directories detected: {len(all_dirs)}")
    report.append(f"- Custom skills detected: {len(custom)}")
    report.append(f"- AGENTS.md listed skills: {len(listed_names)}")
    if args.auto_fix:
        report.append(f"- Auto-fix applied: {'yes' if auto_fixed else 'no changes needed'}")
    report.append("")
    report.append("## Catalog")
    report.append(f"- Missing in AGENTS.md: {', '.join(missing_in_agents) if missing_in_agents else 'none'}")
    report.append(f"- Stale AGENTS.md entries: {', '.join(stale_in_agents) if stale_in_agents else 'none'}")
    report.append(f"- Broken file paths in AGENTS.md: {len(broken_paths)}")
    for bp in broken_paths:
        report.append(f"  - {bp}")
    report.append("")
    report.append("## Validation")
    report.append(f"- lint_skills.py: {'OK' if lint_rc == 0 else 'FAIL'}")
    if lint_out:
        for line in lint_out.splitlines()[:10]:
            report.append(f"  - {line}")
    ok = sum(1 for _, good, _ in validation if good)
    report.append(f"- quick_validate.py: {ok}/{len(validation)} valid")
    for name, good, msg in validation:
        report.append(f"  - {name}: {'OK' if good else 'FAIL'} ({msg})")
    report.append("")
    report.append("## Overlap Risk")
    if overlap_notes:
        for n in overlap_notes:
            report.append(f"- {n}")
    else:
        report.append("- none")

    if args.auto_fix:
        report.append("")
        report.append("## Auto-fix Details")
        if auto_fixed:
            for p in auto_fixed:
                report.append(f"- Updated precedence note: {p}")
        else:
            report.append("- No precedence updates were required.")

    report.append("")
    report.append("## Recommended Actions")
    report.append("1. Resolve catalog mismatches first.")
    report.append("2. Keep lint + quick_validate green on every skill change.")
    report.append("3. Enforce specialized-over-generic precedence when overlap exists.")

    out_path = skills_root / "shared" / "reports" / "skills-governance-report.md"
    out_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote report: {out_path}")
    if args.auto_fix:
        print(f"Auto-fix updated files: {len(auto_fixed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
