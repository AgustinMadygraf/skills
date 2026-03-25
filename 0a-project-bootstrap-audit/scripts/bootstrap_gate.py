#!/usr/bin/env python3
"""
Script de auditoria de bootstrap inicial.
Valida estructura base minima sin modificar codigo.

Usa shared/audit_utils para estructura de reporte.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Agregar shared/ al path para importar audit_utils
SKILL_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT / "shared"))

from audit_utils import ReportBuilder, TodoWriter, relative_to_repo

# Estructura base requerida
DIRS = [
    "src/entities",
    "src/use_cases",
    "src/interface_adapters/presenters",
    "src/interface_adapters/gateways",
    "src/infrastructure",
    "src/infrastructure/settings",
    "docs",
    "tests",
]

REQUIRED_FILES = [
    "run.py",
    "README.md",
    ".gitignore",
    ".env",
    ".env.example",
    "src/infrastructure/settings/logger.py",
    "src/infrastructure/settings/config.py",
]

# Directorios que necesitan .gitkeep SOLO si estan vacios
GITKEEP_DIRS = [
    "src/entities",
    "src/use_cases",
    "src/interface_adapters/presenters",
    "src/interface_adapters/gateways",
    "docs",
    "tests",
]

FORBIDDEN_PATHS = [
    "src/cli.py",
    "src/infrastructure/config.py",
]


def _is_dir_empty(repo_root: Path, rel_dir: str) -> bool:
    """Check if directory has no files (excluding .gitkeep itself)."""
    dir_path = repo_root / rel_dir
    if not dir_path.exists():
        return False
    for item in dir_path.iterdir():
        if item.is_file() and item.name != ".gitkeep":
            return False
        if item.is_dir():
            return False
    return True


def _parse_env_keys(env_path: Path) -> set[str]:
    """Parse keys from .env file."""
    keys: set[str] = set()
    if not env_path.exists():
        return keys
    
    try:
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                keys.add(line.split("=", 1)[0].strip())
    except Exception:
        pass
    return keys


def audit_bootstrap(repo_root: Path) -> dict[str, object]:
    """
    Audita estructura base minima del proyecto.
    
    Args:
        repo_root: Raíz del repositorio
    
    Returns:
        Dict con el reporte completo
    """
    builder = ReportBuilder()
    
    # Layout policy
    for d in DIRS:
        if not (repo_root / d).is_dir():
            builder.add_critical("missing_dir", "", 0, f"Directorio requerido no existe: {d}")
    
    for f in REQUIRED_FILES:
        if not (repo_root / f).is_file():
            builder.add_critical("missing_file", "", 0, f"Archivo requerido no existe: {f}")
    
    for p in FORBIDDEN_PATHS:
        if (repo_root / p).exists():
            builder.add_critical("forbidden_path_present", "", 0, f"Path prohibido existe: {p}")
    
    # Check .gitignore has .tmp/
    gitignore_path = repo_root / ".gitignore"
    if gitignore_path.exists():
        has_tmp = False
        for raw in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if raw.strip() == ".tmp/":
                has_tmp = True
                break
        if not has_tmp:
            builder.add_critical("gitignore_missing_pattern", ".gitignore", 0, "Falta patron .tmp/")
    
    # Check .gitkeep in empty directories
    for d in GITKEEP_DIRS:
        if not (repo_root / d / ".gitkeep").is_file() and _is_dir_empty(repo_root, d):
            builder.add_warning("missing_gitkeep", d, 0, f"Directorio vacio sin .gitkeep: {d}")
    
    # Check forbidden .gitkeep in infrastructure
    infra_path = repo_root / "src" / "infrastructure"
    if infra_path.exists():
        for p in infra_path.rglob(".gitkeep"):
            rel = relative_to_repo(p, repo_root)
            builder.add_warning("forbidden_gitkeep_in_infrastructure", rel, 0, f".gitkeep prohibido en: {rel}")
    
    # Env policy
    env_path = repo_root / ".env"
    env_example_path = repo_root / ".env.example"
    
    if not env_path.exists():
        builder.add_critical("missing_env_file", "", 0, "Falta archivo .env")
    if not env_example_path.exists():
        builder.add_critical("missing_env_example_file", "", 0, "Falta archivo .env.example")
    
    if env_path.exists() and env_example_path.exists():
        env_keys = _parse_env_keys(env_path)
        example_keys = _parse_env_keys(env_example_path)
        missing_in_env = example_keys - env_keys
        for key in sorted(missing_in_env):
            builder.add_warning("env_key_missing_in_dotenv", ".env", 0, f"Key '{key}' en .env.example pero no en .env")
    
    # Python policy (basic - just __init__.py existence)
    src_path = repo_root / "src"
    if src_path.exists():
        for path in src_path.rglob("*"):
            if not path.is_dir():
                continue
            if path.name in ("__pycache__", "data"):
                continue
            init_file = path / "__init__.py"
            if not init_file.exists():
                rel = relative_to_repo(path, repo_root)
                builder.add_critical("missing_init", rel, 0, f"Falta __init__.py en: {rel}")
    else:
        builder.add_critical("src_directory_missing", "", 0, "No existe directorio src/")
    
    return builder.build().to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditoria de bootstrap inicial")
    parser.add_argument("--repo-root", required=True, help="Ruta raiz del repositorio")
    parser.add_argument("--check", action="store_true", help="Modo check (solo reportar)")
    parser.add_argument("--write-todo", action="store_true", help="Escribir hallazgos en docs/todo.md")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    report_dict = audit_bootstrap(repo_root)
    
    # Opcionalmente escribir en docs/todo.md
    if args.write_todo:
        writer = TodoWriter(repo_root, "0a-project-bootstrap-audit")
        from audit_utils import Finding
        findings = [Finding(**f) for f in report_dict.get("findings", [])]
        todo_path = writer.write_findings(
            findings,
            title="0a-Project Bootstrap Audit",
            empty_message="Estructura base correcta.",
        )
        print(f"TODO={todo_path}")
    
    # Output para parsers y humanos (mantener compatibilidad)
    ok = report_dict.get("ok", True)
    print(f"BOOTSTRAP={'OK' if ok else 'FAIL'}")
    print(f"REPO={repo_root}")
    print(f"CHECK_MODE={args.check}")
    print(f"BOOTSTRAP_GATE_OK={ok}")
    
    # Conteos por severidad
    print(f"CRITICAL_TOTAL={report_dict.get('critical_total', 0)}")
    print(f"WARNING_TOTAL={report_dict.get('warning_total', 0)}")
    print(f"INFO_TOTAL={report_dict.get('info_total', 0)}")
    
    if not ok:
        for v in report_dict.get("violations", []):
            print(f"- {v}")
    
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
