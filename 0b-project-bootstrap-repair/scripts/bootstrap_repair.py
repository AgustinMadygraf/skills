#!/usr/bin/env python3
"""
Script de repair de bootstrap inicial.
Crea/normaliza estructura y archivos base del proyecto.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List

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


def write_if_missing(path: Path, content: str) -> bool:
    """Escribe archivo si no existe."""
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def repair_dirs(repo_root: Path) -> List[str]:
    """Crea directorios faltantes."""
    created: List[str] = []
    for d in DIRS:
        dir_path = repo_root / d
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created.append(d)
    return created


def repair_gitkeep(repo_root: Path) -> List[str]:
    """Crea .gitkeep en directorios vacios que lo necesiten."""
    created: List[str] = []
    for d in GITKEEP_DIRS:
        gitkeep_path = repo_root / d / ".gitkeep"
        if not gitkeep_path.exists() and _is_dir_empty(repo_root, d):
            write_if_missing(gitkeep_path, "")
            created.append(f"{d}/.gitkeep")
    return created


def repair_init_files(repo_root: Path) -> List[str]:
    """Crea __init__.py faltantes en src/."""
    created: List[str] = []
    src_path = repo_root / "src"
    if not src_path.exists():
        return created
    
    for path in src_path.rglob("*"):
        if not path.is_dir():
            continue
        if path.name == "__pycache__":
            continue
        if path.name == "data":
            continue
        init_file = path / "__init__.py"
        if not init_file.exists():
            write_if_missing(init_file, "")
            created.append(str(init_file.relative_to(repo_root)).replace("\\", "/"))
    return created


def repair_gitignore(repo_root: Path) -> bool:
    """Agrega .tmp/ a .gitignore si falta."""
    gitignore_path = repo_root / ".gitignore"
    if not gitignore_path.exists():
        return False
    
    lines = gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if any(x.strip() == ".tmp/" for x in lines):
        return False
    
    if lines and lines[-1].strip() != "":
        lines.append("")
    lines.append(".tmp/")
    gitignore_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return True


def repair_missing_files(repo_root: Path) -> dict[str, bool]:
    """Crea archivos esenciales faltantes con contenido minimo."""
    created: dict[str, bool] = {}
    
    # run.py
    run_py = repo_root / "run.py"
    if not run_py.exists():
        content = '''#!/usr/bin/env python3
"""
Path: run.py

Entry point para ejecucion local.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.infrastructure.fastapi.app:app", host="127.0.0.1", port=8899, reload=True)
'''
        write_if_missing(run_py, content)
        created["run.py"] = True
    
    # README.md
    readme = repo_root / "README.md"
    if not readme.exists():
        content = '''# Project

Backend API.

## Ejecucion local

```bash
python -m venv .venv
source .venv/bin/activate  # o .venv\\Scripts\\activate en Windows
pip install -r requirements.txt
python run.py
```
'''
        write_if_missing(readme, content)
        created["README.md"] = True
    
    # .env.example
    env_example = repo_root / ".env.example"
    if not env_example.exists():
        content = '''# App
APP_ENVIRONMENT=development
APP_LOG_LEVEL=INFO

# CORS (desarrollo)
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
'''
        write_if_missing(env_example, content)
        created[".env.example"] = True
    
    # .env (solo si no existe)
    env_file = repo_root / ".env"
    if not env_file.exists() and env_example.exists():
        write_if_missing(env_file, env_example.read_text(encoding="utf-8"))
        created[".env"] = True
    
    # src/infrastructure/settings/logger.py
    logger_py = repo_root / "src/infrastructure/settings/logger.py"
    if not logger_py.exists():
        content = '''"""
Path: src/infrastructure/settings/logger.py

Configuracion de logging.
"""
import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO") -> None:
    """Configura logging basico."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
'''
        write_if_missing(logger_py, content)
        created["src/infrastructure/settings/logger.py"] = True
    
    # src/infrastructure/settings/config.py
    config_py = repo_root / "src/infrastructure/settings/config.py"
    if not config_py.exists():
        content = '''"""
Path: src/infrastructure/settings/config.py

Configuracion de la aplicacion.
"""
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Settings base de la aplicacion."""
    app_name: str = "api"
    app_environment: str = "development"
    app_log_level: str = "INFO"


def load_settings() -> Settings:
    """Carga settings desde variables de entorno."""
    return Settings(
        app_name=os.getenv("APP_NAME", "api"),
        app_environment=os.getenv("APP_ENVIRONMENT", "development"),
        app_log_level=os.getenv("APP_LOG_LEVEL", "INFO"),
    )
'''
        write_if_missing(config_py, content)
        created["src/infrastructure/settings/config.py"] = True
    
    return created


def update_todo_md(repo_root: Path, violations: List[str]) -> bool:
    """Actualiza docs/todo.md con el estado del bootstrap en formato consolidado."""
    todo_path = repo_root / "docs" / "todo.md"
    
    # Leer o crear archivo base
    if todo_path.exists():
        content = todo_path.read_text(encoding="utf-8", errors="ignore")
    else:
        todo_path.parent.mkdir(parents=True, exist_ok=True)
        content = """# Agenda de Tareas Backend (`docs/todo.md`)

Documento de compatibilidad.

La fuente operativa vigente es `docs/roadmap/todo.md`.

- Backlog activo: ver `docs/roadmap/todo.md`.
- Historial de ejecucion: ver `docs/roadmap/todo.done.md`.
- Ultima sincronizacion de alias: `2026-03-14`.

<!-- project-structure:auto:start -->
<!-- project-structure:auto:end -->
"""
    
    # Preparar sección de bootstrap
    if violations:
        bootstrap_section = "### Bootstrap (0a)\n"
        for v in violations:
            bootstrap_section += f"- [ ] [bootstrap-policy] Resolver: `{v}`.\n"
    else:
        bootstrap_section = "### Bootstrap (0a)\n- [x] [bootstrap-policy] Bootstrap completo.\n"
    
    # Actualizar o insertar sección dentro de project-structure
    pattern = r"(<!-- project-structure:auto:start -->)[\s\S]*?(<!-- project-structure:auto:end -->)"
    
    if re.search(pattern, content):
        # Reemplazar sección existente
        replacement = r"\1\n## Project Structure Gate (autogenerado)\n\n" + bootstrap_section + r"\2"
        new_content = re.sub(pattern, replacement, content)
    else:
        # Agregar nueva sección
        new_content = content.rstrip() + f"\n\n<!-- project-structure:auto:start -->\n## Project Structure Gate (autogenerado)\n\n{bootstrap_section}<!-- project-structure:auto:end -->\n"
    
    if new_content != content:
        todo_path.write_text(new_content, encoding="utf-8", newline="\n")
        return True
    return False


def run_audit_check(repo_root: Path) -> List[str]:
    """Ejecuta verificación rápida de violaciones restantes."""
    violations: List[str] = []
    
    # Layout checks
    for d in DIRS:
        if not (repo_root / d).is_dir():
            violations.append(f"missing_dir:{d}")
    
    for f in REQUIRED_FILES:
        if not (repo_root / f).is_file():
            violations.append(f"missing_file:{f}")
    
    gitignore_path = repo_root / ".gitignore"
    if gitignore_path.exists():
        has_tmp = False
        for line in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip() == ".tmp/":
                has_tmp = True
                break
        if not has_tmp:
            violations.append("gitignore_missing_pattern:.tmp/")
    else:
        violations.append("missing_file:.gitignore")
    
    return violations


def run_repair(repo_root: Path, check_mode: bool = False) -> int:
    """Ejecuta el repair y retorna exit code."""
    
    if check_mode:
        print("REPAIR=SKIPPED (check mode)")
        return 0
    
    created_dirs = repair_dirs(repo_root)
    created_files = repair_missing_files(repo_root)
    created_gitkeep = repair_gitkeep(repo_root)
    created_init = repair_init_files(repo_root)
    fixed_gitignore = repair_gitignore(repo_root)
    
    total_created = len(created_dirs) + len(created_files) + len(created_gitkeep) + len(created_init)
    
    # Verificar violaciones restantes y actualizar docs/todo.md
    remaining = run_audit_check(repo_root)
    updated_todo = update_todo_md(repo_root, remaining)
    
    print(f"REPAIR=DONE")
    print(f"CREATED_DIRS={len(created_dirs)}")
    print(f"CREATED_FILES={len(created_files)}")
    print(f"CREATED_GITKEEP={len(created_gitkeep)}")
    print(f"CREATED_INIT={len(created_init)}")
    print(f"FIXED_GITIGNORE={fixed_gitignore}")
    print(f"UPDATED_TODO_MD={updated_todo}")
    print(f"REMAINING_VIOLATIONS={len(remaining)}")
    
    if total_created > 0:
        print(f"\nDetalle:")
        for d in created_dirs:
            print(f"  + dir: {d}")
        for f, _ in created_files.items():
            print(f"  + file: {f}")
        for g in created_gitkeep:
            print(f"  + gitkeep: {g}")
        for i in created_init:
            print(f"  + init: {i}")
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair de bootstrap inicial")
    parser.add_argument("--repo-root", required=True, help="Ruta raiz del repositorio")
    parser.add_argument("--check", action="store_true", help="Modo check (solo reportar, no modificar)")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root)
    return run_repair(repo_root, check_mode=args.check)


if __name__ == "__main__":
    sys.exit(main())
