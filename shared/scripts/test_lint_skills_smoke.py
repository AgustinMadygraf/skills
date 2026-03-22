import tempfile
from pathlib import Path

from lint_skills import lint_skills


GOOD_SKILL = """---
name: skill-backend-testing
description: "desc"
version: "1.1.0"
owners: "platform-team"
last_reviewed: "2026-03-09"
maturity: "stable"
---

# Title

## Alcance por defecto

ok

## Flujo minimo

ok

## Integracion

ok
"""

BAD_SKILL = """---
name: wrong-name
description: "desc"
---

# Title
"""


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shared_cfg = root / "shared" / "config"
        shared_cfg.mkdir(parents=True)
        (shared_cfg / "skill-governance.yaml").write_text(
            (
                "version: 1\n"
                "governed_skills:\n"
                "  - skill-backend-testing\n"
                "  - skill-backend-orchestrator\n"
                "allowed_maturity: [experimental, stable, deprecated]\n"
            ),
            encoding="utf-8",
        )

        good = root / "skill-backend-testing"
        good.mkdir(parents=True)
        write(good / "SKILL.md", GOOD_SKILL)
        write(good / "CHANGELOG.md", "# Changelog\n")

        bad = root / "skill-backend-orchestrator"
        bad.mkdir(parents=True)
        write(bad / "SKILL.md", BAD_SKILL)

        errs = lint_skills(root)
        assert any("wrong-name" in e for e in errs), "Debe detectar name inconsistente"
        assert any("no coincide con carpeta" in e for e in errs), "Debe detectar nombre inconsistente"
        assert len(errs) > 0, "Debe reportar errores para skills invalidos"

    print("Smoke lint tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
