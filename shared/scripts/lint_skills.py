import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT
GOV_PATH = ROOT / "shared" / "config" / "skill-governance.yaml"

REL_LINK_RE = re.compile(r"`((?:\.\./|\.\/)[^`]+)`")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MOJIBAKE_MARKERS = ("Ã", "â", "�")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    raw = text[4:end]
    body = text[end + 5 :]
    data: Dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data, body


def parse_governance_config(path: Path) -> Dict[str, object]:
    cfg: Dict[str, object] = {
        "governed_skills": set(),
        "required_frontmatter": [],
        "allowed_maturity": {"experimental", "stable", "deprecated"},
        "require_changelog": True,
        "require_default_prompt_skill_ref": True,
        "enforce_mojibake_check": False,
        "required_sections": {},
    }
    if not path.exists():
        return cfg

    lines = read_text(path).splitlines()
    mode = ""
    current_skill = ""
    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if not s or s.startswith("#"):
            continue

        if s.startswith("governed_skills:"):
            mode = "governed"
            continue
        if s.startswith("required_frontmatter:"):
            mode = "required_frontmatter"
            continue
        if s.startswith("required_sections:"):
            mode = "required_sections"
            current_skill = ""
            continue
        if s.startswith("allowed_maturity:"):
            vals = s.split(":", 1)[1].strip().strip("[]")
            cfg["allowed_maturity"] = {v.strip() for v in vals.split(",") if v.strip()}
            mode = ""
            continue
        if s.startswith("require_changelog:"):
            cfg["require_changelog"] = s.split(":", 1)[1].strip().lower() == "true"
            mode = ""
            continue
        if s.startswith("require_default_prompt_skill_ref:"):
            cfg["require_default_prompt_skill_ref"] = s.split(":", 1)[1].strip().lower() == "true"
            mode = ""
            continue
        if s.startswith("enforce_mojibake_check:"):
            cfg["enforce_mojibake_check"] = s.split(":", 1)[1].strip().lower() == "true"
            mode = ""
            continue

        if mode == "governed" and s.startswith("- "):
            cfg["governed_skills"].add(s[2:].strip())
            continue
        if mode == "required_frontmatter" and s.startswith("- "):
            cfg["required_frontmatter"].append(s[2:].strip())
            continue
        if mode == "required_sections":
            if s.endswith(":") and not s.startswith("- "):
                current_skill = s[:-1].strip()
                cfg["required_sections"].setdefault(current_skill, [])
                continue
            if s.startswith("- ") and current_skill:
                cfg["required_sections"][current_skill].append(s[2:].strip().strip('"'))
                continue

    return cfg


def check_openai_yaml(skill_dir: Path, skill_name: str, require_prompt_ref: bool) -> List[str]:
    errors: List[str] = []
    yaml_path = skill_dir / "agents" / "openai.yaml"
    if not yaml_path.exists():
        return errors
    text = read_text(yaml_path)
    for key in ["display_name:", "short_description:", "default_prompt:"]:
        if key not in text:
            errors.append(f"{yaml_path}: falta clave {key}")
    if require_prompt_ref and f"${skill_name}" not in text:
        errors.append(f"{yaml_path}: default_prompt debe incluir ${skill_name}")
    return errors


def check_relative_links(skill_md: Path, text: str) -> List[str]:
    errors: List[str] = []
    for match in REL_LINK_RE.finditer(text):
        rel = match.group(1).strip()
        target = (skill_md.parent / rel).resolve()
        if not target.exists():
            errors.append(f"{skill_md}: link relativo roto {rel}")
    return errors


def contains_mojibake(text: str) -> bool:
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        return True
    for ch in text:
        if ch == "\ufffd":
            return True
        cat = unicodedata.category(ch)
        if cat == "Cc" and ch not in ("\n", "\r", "\t"):
            return True
    return False


def lint_skill(skill_dir: Path, cfg: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return errors

    text = read_text(skill_md)
    fm, body = parse_frontmatter(text)
    if not fm:
        errors.append(f"{skill_md}: frontmatter YAML ausente o invalido")
        return errors

    name = fm.get("name", "")
    if not name:
        errors.append(f"{skill_md}: falta campo name")
        return errors
    if name != skill_dir.name:
        errors.append(f"{skill_md}: name '{name}' no coincide con carpeta '{skill_dir.name}'")

    if not fm.get("description"):
        errors.append(f"{skill_md}: falta campo description")

    governed = name in cfg["governed_skills"]
    required_frontmatter = cfg["required_frontmatter"]
    allowed_maturity = cfg["allowed_maturity"]
    required_sections = cfg["required_sections"].get(name, [])

    if governed:
        for key in required_frontmatter:
            if not fm.get(key):
                errors.append(f"{skill_md}: falta campo {key}")
        version = fm.get("version", "")
        if version and not VERSION_RE.match(version):
            errors.append(f"{skill_md}: version invalida '{version}', usar semver x.y.z")
        last_reviewed = fm.get("last_reviewed", "")
        if last_reviewed and not DATE_RE.match(last_reviewed):
            errors.append(f"{skill_md}: last_reviewed invalido '{last_reviewed}', usar YYYY-MM-DD")
        maturity = fm.get("maturity", "")
        if maturity and maturity not in allowed_maturity:
            errors.append(f"{skill_md}: maturity invalida '{maturity}'")
        if cfg["require_changelog"]:
            if not (skill_dir / "CHANGELOG.md").exists():
                errors.append(f"{skill_dir}: falta CHANGELOG.md")
        if cfg["enforce_mojibake_check"] and contains_mojibake(text):
            errors.append(f"{skill_md}: posible mojibake o encoding corrupto")

    for section in required_sections:
        if section not in body:
            errors.append(f"{skill_md}: falta seccion requerida {section}")

    errors.extend(check_relative_links(skill_md, text))
    errors.extend(check_openai_yaml(skill_dir, name, bool(cfg["require_default_prompt_skill_ref"])))
    return errors


def lint_skills(skills_dir: Path) -> List[str]:
    cfg = parse_governance_config(GOV_PATH)
    errors: List[str] = []
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith(".")):
        errors.extend(lint_skill(skill_dir, cfg))
    return errors


def main() -> int:
    errors = lint_skills(SKILLS_DIR)
    if errors:
        print("Skill lint: FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Skill lint: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
