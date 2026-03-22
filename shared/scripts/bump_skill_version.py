import argparse
from datetime import date
from pathlib import Path
from typing import Dict, Tuple

from lint_skills import parse_frontmatter, read_text


ROOT = Path(__file__).resolve().parents[2]


def write_frontmatter(path: Path, fm: Dict[str, str], body: str) -> None:
    lines = ["---"]
    for key, value in fm.items():
        if key == "name":
            lines.append(f"{key}: {value}")
        else:
            lines.append(f'{key}: "{value}"')
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body.lstrip("\n"), encoding="utf-8")


def prepend_changelog(path: Path, version: str, note: str) -> None:
    today = str(date.today())
    entry = f"## {version} - {today}\n- {note}\n\n"
    if not path.exists():
        path.write_text("# Changelog\n\n" + entry, encoding="utf-8")
        return
    txt = path.read_text(encoding="utf-8")
    if txt.startswith("# Changelog\n\n"):
        rest = txt[len("# Changelog\n\n") :]
        path.write_text("# Changelog\n\n" + entry + rest, encoding="utf-8")
    else:
        path.write_text("# Changelog\n\n" + entry + txt, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump skill version and update changelog.")
    parser.add_argument("skill_name")
    parser.add_argument("new_version")
    parser.add_argument("--note", default="Version bump.")
    args = parser.parse_args()

    skill_dir = ROOT / args.skill_name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise SystemExit(f"Skill not found: {skill_md}")

    fm, body = parse_frontmatter(read_text(skill_md))
    if not fm:
        raise SystemExit("Invalid SKILL.md frontmatter")

    fm["version"] = args.new_version
    fm["last_reviewed"] = str(date.today())
    write_frontmatter(skill_md, fm, body)

    changelog = skill_dir / "CHANGELOG.md"
    prepend_changelog(changelog, args.new_version, args.note)
    print(f"Bumped {args.skill_name} to {args.new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
