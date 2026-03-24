#!/usr/bin/env python3
"""
Script de auditoria de bootstrap inicial.
Valida estructura base minima sin modificar codigo.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

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


def validate_layout_policy(repo_root: Path) -> Dict[str, object]:
    """Valida politica de layout basica."""
    missing_dirs = [d for d in DIRS if not (repo_root / d).is_dir()]
    missing_files = [f for f in REQUIRED_FILES if not (repo_root / f).is_file()]
    forbidden_existing = [p for p in FORBIDDEN_PATHS if (repo_root / p).exists()]
    
    # Check .gitignore has .tmp/
    gitignore_has_tmp = False
    gitignore_path = repo_root / ".gitignore"
    if gitignore_path.exists():
        for raw in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if raw.strip() == ".tmp/":
                gitignore_has_tmp = True
                break
    
    # Only require .gitkeep in empty directories
    missing_gitkeep = [
        d for d in GITKEEP_DIRS
        if not (repo_root / d / ".gitkeep").is_file() and _is_dir_empty(repo_root, d)
    ]
    
    # Check for forbidden .gitkeep in infrastructure
    infra_gitkeeps: List[str] = []
    infra_path = repo_root / "src" / "infrastructure"
    if infra_path.exists():
        infra_gitkeeps = [
            str(p.relative_to(repo_root))
            for p in infra_path.rglob(".gitkeep")
        ]
    
    violations: List[str] = []
    for d in missing_dirs:
        violations.append(f"missing_dir:{d}")
    for f in missing_files:
        violations.append(f"missing_file:{f}")
    for p in forbidden_existing:
        violations.append(f"forbidden_path_present:{p}")
    for d in missing_gitkeep:
        violations.append(f"missing_gitkeep:{d}/.gitkeep")
    for g in infra_gitkeeps:
        violations.append(f"forbidden_gitkeep_in_infrastructure:{g}")
    if not gitignore_has_tmp:
        violations.append("gitignore_missing_pattern:.tmp/")
    
    return {
        "ok": len(violations) == 0,
        "missing_dirs": missing_dirs,
        "missing_files": missing_files,
        "forbidden_existing": forbidden_existing,
        "gitignore_has_tmp": gitignore_has_tmp,
        "missing_gitkeep": missing_gitkeep,
        "forbidden_gitkeep_in_infrastructure": infra_gitkeeps,
        "violations": violations,
    }


def validate_env_policy(repo_root: Path) -> Dict[str, object]:
    """Valida politica basica de .env y .env.example."""
    env_path = repo_root / ".env"
    env_example_path = repo_root / ".env.example"
    
    violations: List[str] = []
    
    if not env_path.exists():
        violations.append("missing_env_file")
    if not env_example_path.exists():
        violations.append("missing_env_example_file")
    
    # Check basic env parity (keys in example should exist in .env)
    if env_path.exists() and env_example_path.exists():
        try:
            env_keys = set()
            for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    env_keys.add(line.split("=", 1)[0].strip())
            
            example_keys = set()
            for line in env_example_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    example_keys.add(line.split("=", 1)[0].strip())
            
            missing_in_env = example_keys - env_keys
            for key in sorted(missing_in_env):
                violations.append(f"env_key_missing_in_dotenv:{key}")
        except Exception:
            pass  # If we can't read, other violations will catch it
    
    return {
        "ok": len(violations) == 0,
        "violations": violations,
    }


def validate_python_policy(repo_root: Path) -> Dict[str, object]:
    """Valida politica basica de archivos Python (solo existencia de __init__)."""
    src_path = repo_root / "src"
    if not src_path.exists():
        return {"ok": False, "violations": ["src_directory_missing"]}
    
    violations: List[str] = []
    missing_init: List[str] = []
    
    for path in src_path.rglob("*"):
        if not path.is_dir():
            continue
        # Skip __pycache__ directories
        if path.name == "__pycache__":
            continue
        # Skip data directories (non-code)
        if path.name == "data":
            continue
        init_file = path / "__init__.py"
        if not init_file.exists():
            missing_init.append(str(path.relative_to(repo_root)).replace("\\", "/"))
    
    for d in missing_init:
        violations.append(f"missing_init:{d}")
    
    return {
        "ok": len(violations) == 0,
        "missing_init": missing_init,
        "violations": violations,
    }


def run_audit(repo_root: Path, check_mode: bool = True) -> int:
    """Ejecuta la auditoria de bootstrap y retorna exit code."""
    layout = validate_layout_policy(repo_root)
    env = validate_env_policy(repo_root)
    python = validate_python_policy(repo_root)
    
    layout_ok = layout["ok"]
    env_ok = env["ok"]
    python_ok = python["ok"]
    
    all_violations = layout.get("violations", []) + env.get("violations", []) + python.get("violations", [])
    
    bootstrap_ok = layout_ok and env_ok and python_ok
    
    # Output para parsers y humanos
    print(f"BOOTSTRAP={'OK' if bootstrap_ok else 'FAIL'}")
    print(f"REPO={repo_root.resolve()}")
    print(f"CHECK_MODE={check_mode}")
    print(f"BOOTSTRAP_GATE_OK={bootstrap_ok}")
    print(f"LAYOUT_POLICY_OK={layout_ok}")
    print(f"ENV_POLICY_OK={env_ok}")
    print(f"PYTHON_POLICY_OK={python_ok}")
    
    if not bootstrap_ok:
        print(f"- layout_violations={layout.get('violations', [])}")
        print(f"- env_violations={env.get('violations', [])}")
        print(f"- python_violations={python.get('violations', [])}")
    
    return 0 if bootstrap_ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditoria de bootstrap inicial")
    parser.add_argument("--repo-root", required=True, help="Ruta raiz del repositorio")
    parser.add_argument("--check", action="store_true", help="Modo check (solo reportar)")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root)
    return run_audit(repo_root, check_mode=args.check)


if __name__ == "__main__":
    sys.exit(main())
