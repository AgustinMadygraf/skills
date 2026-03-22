import re
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = ROOT / "skills"
AGENTS_MD = ROOT / "AGENTS.md"
DEPRECATION_CFG = SKILLS_ROOT / "shared" / "config" / "deprecation-policy.yaml"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> Dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    raw = text[4:end]
    data: Dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def parse_deprecation_policy(path: Path) -> Dict[str, Dict[str, str]]:
    if not path.exists():
        return {}
    data: Dict[str, Dict[str, str]] = {}
    lines = read_text(path).splitlines()
    in_block = False
    current = ""
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("deprecated_skills:"):
            in_block = True
            continue
        if not in_block:
            continue
        if s.endswith(":") and not s.startswith("- "):
            key = s[:-1].strip()
            if key and key != "deprecated_skills":
                current = key
                data[current] = {}
            continue
        if current and ":" in s:
            k, v = s.split(":", 1)
            data[current][k.strip()] = v.strip().strip('"').strip("'")
    return data


def discover_skills() -> List[Tuple[str, str, str, Path]]:
    found: List[Tuple[str, str, str, Path]] = []
    for skill_md in sorted(SKILLS_ROOT.rglob("SKILL.md")):
        if ".system" in skill_md.parts:
            # keep .system skills in the list as well
            pass
        data = parse_frontmatter(read_text(skill_md))
        name = data.get("name")
        description = data.get("description", "").strip()
        maturity = data.get("maturity", "").strip()
        if not name:
            continue
        found.append((name, description, maturity, skill_md))
    return found


def to_ascii(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def build_agents_md(skills: List[Tuple[str, str, str, Path]]) -> str:
    deprecated = parse_deprecation_policy(DEPRECATION_CFG)
    lines: List[str] = []
    lines.append("# AGENTS.md")
    lines.append("")
    lines.append("## Skills")
    lines.append("A skill is a set of local instructions stored in a `SKILL.md` file.")
    lines.append("")
    lines.append("### Available skills")
    for name, description, maturity, path in sorted(skills, key=lambda x: x[0]):
        desc = to_ascii(description)
        rel = path.as_posix().replace("C:/Users/usuario/.codex/", "C:/Users/usuario/.codex/")
        maturity_tag = f" [{maturity}]" if maturity else ""
        dep = deprecated.get(name, {})
        dep_tag = ""
        if dep:
            replacement = dep.get("replacement", "")
            dep_on = dep.get("deprecates_on", "")
            extra = []
            if replacement:
                extra.append(f"replacement={replacement}")
            if dep_on:
                extra.append(f"deprecates_on={dep_on}")
            dep_tag = f" [deprecated: {', '.join(extra)}]" if extra else " [deprecated]"
        lines.append(f"- {name}{maturity_tag}{dep_tag}: {desc} (file: {rel})")
    lines.append("")
    lines.append("### Trigger rules")
    lines.append("- If the user names a skill or the request clearly matches one, use it in that turn.")
    lines.append("- Use the minimum number of skills needed.")
    lines.append("- Read only the relevant parts of each `SKILL.md` and referenced files.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    skills = discover_skills()
    content = build_agents_md(skills)
    AGENTS_MD.write_text(content, encoding="utf-8")
    print(f"Updated {AGENTS_MD} with {len(skills)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
