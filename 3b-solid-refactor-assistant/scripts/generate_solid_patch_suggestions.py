#!/usr/bin/env python3
"""
Path: 3b-solid-refactor-assistant/scripts/generate_solid_patch_suggestions.py
Genera sugerencias de patch para hallazgos SOLID.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def generate_patch_suggestions(repo_root: Path) -> str:
    """Genera sugerencias de patch para hallazgos SOLID."""
    lines = [
        "# Sugerencias de Patch SOLID",
        "",
        "Este documento contiene sugerencias de cambios para resolver hallazgos SOLID.",
        "",
        "## Nota importante",
        "",
        "Los cambios deben aplicarse manualmente tras revision. No usar autofix ciego.",
        "",
        "## Patrones comunes",
        "",
        "### SRP - Extraer clase",
        "",
        "```python",
        "# Antes: Clase con multiples responsabilidades",
        "class OrderService:",
        "    def create_order(self): ...",
        "    def send_email(self): ...  # <- Mover a EmailService",
        "    def log_activity(self): ...  # <- Mover a Logger",
        "",
        "# Despues: Responsabilidades separadas",
        "class OrderService:",
        "    def create_order(self): ...",
        "",
        "class EmailService:",
        "    def send_email(self): ...",
        "```",
        "",
        "### ISP - Dividir interfaz",
        "",
        "```python",
        "# Antes: Interfaz grande",
        "class IRepository(ABC):",
        "    @abstractmethod",
        "    def get(self, id): ...",
        "    @abstractmethod",
        "    def list(self): ...",
        "    @abstractmethod",
        "    def create(self, data): ...",
        "    @abstractmethod",
        "    def update(self, id, data): ...",
        "    @abstractmethod",
        "    def delete(self, id): ...",
        "",
        "# Despues: Interfaces especificas",
        "class IReadable(ABC):",
        "    @abstractmethod",
        "    def get(self, id): ...",
        "    @abstractmethod",
        "    def list(self): ...",
        "",
        "class IWritable(ABC):",
        "    @abstractmethod",
        "    def create(self, data): ...",
        "    @abstractmethod",
        "    def update(self, id, data): ...",
        "    @abstractmethod",
        "    def delete(self, id): ...",
        "```",
        "",
        "### DIP - Invertir dependencia",
        "",
        "```python",
        "# Antes: Dependencia concreta",
        "class OrderUseCase:",
        "    def __init__(self):",
        "        self.db = PostgresDB()  # <- Concreto",
        "",
        "# Despues: Dependencia abstracta",
        "class OrderUseCase:",
        "    def __init__(self, db: DatabasePort):  # <- Puerto",
        "        self.db = db",
        "```",
        "",
        "## Workflow recomendado",
        "",
        "1. Identificar hallazgo en `docs/todo.md`",
        "2. Crear rama: `refactor/solid-{rule}-{file}`",
        "3. Aplicar patron correspondiente",
        "4. Ejecutar tests",
        "5. Ejecutar `$3a-solid-gate`",
        "6. Commit y PR",
        "",
    ]
    
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SOLID patch suggestions")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--output", help="Output file (default: docs/refactor/solid-patch-suggestions.md)")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    output_path = Path(args.output) if args.output else repo_root / "docs" / "refactor" / "solid-patch-suggestions.md"
    
    suggestions = generate_patch_suggestions(repo_root)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(suggestions, encoding="utf-8", newline="\n")
    
    print(f"SOLID_PATCH_SUGGESTIONS={output_path}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
