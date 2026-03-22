import json
from pathlib import Path

from lint_skills import parse_frontmatter, read_text


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "shared" / "reports" / "skills-health-report.json"
GOV = ROOT / "shared" / "config" / "skill-governance.yaml"


def parse_governed(path: Path) -> set[str]:
    if not path.exists():
        return set()
    governed: set[str] = set()
    in_block = False
    for raw in read_text(path).splitlines():
        s = raw.strip()
        if s.startswith("governed_skills:"):
            in_block = True
            continue
        if in_block:
            if s.startswith("- "):
                governed.add(s[2:].strip())
                continue
            if s and not s.startswith("#"):
                in_block = False
    return governed


def main() -> int:
    governed = parse_governed(GOV)
    skill_dirs = [p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")]
    total = 0
    with_version = 0
    with_changelog = 0
    with_agents_yaml = 0
    governed_total = 0
    governed_ok = 0

    for sd in sorted(skill_dirs):
        smd = sd / "SKILL.md"
        if not smd.exists():
            continue
        total += 1
        fm, _ = parse_frontmatter(read_text(smd))
        if fm.get("version"):
            with_version += 1
        if (sd / "CHANGELOG.md").exists():
            with_changelog += 1
        if (sd / "agents" / "openai.yaml").exists():
            with_agents_yaml += 1
        if sd.name in governed:
            governed_total += 1
            if fm.get("version") and fm.get("owners") and fm.get("last_reviewed") and fm.get("maturity") and (sd / "CHANGELOG.md").exists():
                governed_ok += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "total_skills": total,
        "with_version": with_version,
        "with_changelog": with_changelog,
        "with_agents_openai_yaml": with_agents_yaml,
        "governed_total": governed_total,
        "governed_compliant": governed_ok,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
