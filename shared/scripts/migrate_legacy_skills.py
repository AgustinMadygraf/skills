import argparse
from datetime import date
from pathlib import Path
from typing import Dict, Tuple

from lint_skills import parse_frontmatter, read_text


ROOT = Path(__file__).resolve().parents[2]
TODAY = str(date.today())


def serialize_frontmatter(data: Dict[str, str]) -> str:
    order = [
        "name",
        "description",
        "version",
        "owners",
        "last_reviewed",
        "maturity",
    ]
    lines = ["---"]
    for key in order:
        if key in data and data[key]:
            value = data[key]
            if key in {"description", "version", "owners", "last_reviewed", "maturity"}:
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f"{key}: {value}")
    for key, value in data.items():
        if key not in order and value:
            lines.append(f'{key}: "{value}"')
    lines.append("---")
    return "\n".join(lines)


def ensure_openai_yaml(skill_dir: Path, name: str, description: str, dry_run: bool) -> bool:
    path = skill_dir / "agents" / "openai.yaml"
    if path.exists():
        return False
    short = (description or "Skill especializada").strip()
    if len(short) > 72:
        short = short[:69] + "..."
    content = (
        "interface:\n"
        f'  display_name: "{name}"\n'
        f'  short_description: "{short}"\n'
        f'  default_prompt: "Use ${name} to execute its specialized workflow."\n\n'
        "policy:\n"
        "  allow_implicit_invocation: true\n"
    )
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return True


def ensure_changelog(skill_dir: Path, version: str, dry_run: bool) -> bool:
    path = skill_dir / "CHANGELOG.md"
    if path.exists():
        return False
    content = (
        "# Changelog\n\n"
        f"## {version} - {TODAY}\n"
        "- Governance migration: added versioning and metadata baseline.\n"
    )
    if not dry_run:
        path.write_text(content, encoding="utf-8")
    return True


def migrate_skill(skill_dir: Path, dry_run: bool) -> Tuple[bool, bool, bool]:
    skill_md = skill_dir / "SKILL.md"
    txt = read_text(skill_md)
    fm, body = parse_frontmatter(txt)
    changed_md = False

    fm.setdefault("version", "1.0.0")
    fm.setdefault("owners", "platform-team")
    fm.setdefault("last_reviewed", TODAY)
    fm.setdefault("maturity", "stable")

    serialized = serialize_frontmatter(fm) + "\n\n" + body.lstrip("\n")
    if serialized != txt:
        changed_md = True
        if not dry_run:
            skill_md.write_text(serialized, encoding="utf-8")

    created_agent = ensure_openai_yaml(skill_dir, fm.get("name", skill_dir.name), fm.get("description", ""), dry_run)
    created_changelog = ensure_changelog(skill_dir, fm.get("version", "1.0.0"), dry_run)
    return changed_md, created_agent, created_changelog


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy skills to governance baseline.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    changed_md = 0
    created_agents = 0
    created_changelog = 0

    for skill_dir in sorted(p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if skill_dir.name == "shared":
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        c_md, c_agent, c_ch = migrate_skill(skill_dir, args.dry_run)
        changed_md += int(c_md)
        created_agents += int(c_agent)
        created_changelog += int(c_ch)

    mode = "DRY-RUN" if args.dry_run else "APPLY"
    print(f"{mode}: changed SKILL.md={changed_md}, created agents={created_agents}, created changelog={created_changelog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
