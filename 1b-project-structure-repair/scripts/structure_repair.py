#!/usr/bin/env python3
"""
Script de repair de estructura.
Corrige env/layout/python-file policy.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def src_dirs(repo_root: Path) -> list[Path]:
    """Lista todos los directorios bajo src/."""
    root = repo_root / "src"
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*") if p.is_dir()] + [root])


def py_files_under_src(repo_root: Path) -> list[Path]:
    """Lista todos los archivos .py bajo src/."""
    root = repo_root / "src"
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*.py") if p.is_file()])


def dir_is_empty(repo_root: Path, dir_path: str) -> bool:
    """Verifica si un directorio está vacío (necesita .gitkeep).
    
    Un directorio está vacío si:
    - No tiene archivos (excluyendo .gitkeep)
    - No tiene subdirectorios con contenido (vacío recursivamente)
    
    Equivalente a: find . -type d -empty
    """
    d = repo_root / dir_path
    if not d.is_dir():
        return False
    
    for item in d.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_file():
            # Tiene archivos reales
            return False
        if item.is_dir():
            # Tiene subdirectorio - verificar si está vacío recursivamente
            if not dir_is_empty(repo_root, str(item.relative_to(repo_root))):
                # El subdirectorio tiene contenido, este directorio no está vacío
                return False
    
    # No tiene archivos ni subdirectorios con contenido
    return True


def normalize_init_files(repo_root: Path) -> list[str]:
    """Vacía __init__.py que no tengan exports intencionales.
    
    Preserva __init__.py que:
    - Tengan __all__ (exports explícitos)
    - Tengan imports de submódulos (re-exports)
    """
    fixed: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name != "__init__.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if text.strip() == "":
            continue
        # Preservar si tiene exports intencionales
        if "__all__" in text:
            continue
        # Preservar si tiene imports de otros módulos (re-exports)
        if "from ." in text or "from src." in text or "import src." in text:
            continue
        path.write_text("", encoding="utf-8", newline="\n")
        fixed.append(str(path.relative_to(repo_root)))
    return fixed


def ensure_path_docstring_for_file(path: Path, rel: str) -> bool:
    """Asegura que el archivo tenga el docstring de Path al inicio."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = text.replace("\ufeff", "").replace("ï»¿", "")
    expected = f'"""\nPath: {rel}\n"""'

    def strip_one_leading_docstring(payload: str) -> tuple[str, str]:
        s = payload.lstrip()
        if not (s.startswith('"""') or s.startswith("'''")):
            return payload, ""
        quote = s[:3]
        end = s.find(quote, 3)
        if end == -1:
            return payload, ""
        header = s[3:end]
        remainder = s[end + 3:]
        return remainder, header

    remainder, _first_header = strip_one_leading_docstring(text)
    if remainder == text:
        remainder = text
    # Si hay un segundo docstring que parece Path header, también lo quitamos
    rem2, second_header = strip_one_leading_docstring(remainder)
    if rem2 != remainder and "Path:" in second_header:
        remainder = rem2

    new_text = expected + "\n\n" + remainder.lstrip("\n")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8", newline="\n")
        return True
    return False


def normalize_path_docstrings(repo_root: Path) -> list[str]:
    """Normaliza los docstrings de Path en todos los archivos .py."""
    fixed: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        if ensure_path_docstring_for_file(path, rel):
            fixed.append(str(path.relative_to(repo_root)))
    return fixed


def import_rank(line: str) -> int:
    """Asigna ranking a imports para ordenarlos."""
    s = line.strip()
    if s.startswith("from src.infrastructure"):
        return 1
    if s.startswith("from src.interface_adapters"):
        return 2
    if s.startswith("from src.use_cases"):
        return 3
    if s.startswith("from src.entities"):
        return 4
    if s.startswith("from src.") or s.startswith("import src."):
        return 5
    return 0


def is_multiline_import_start(line: str) -> bool:
    """Detecta si una línea es el inicio de un import multilinea (termina con '(')."""
    stripped = line.strip()
    if not (stripped.startswith("import ") or stripped.startswith("from ")):
        return False
    return stripped.endswith("(") or ("(" in stripped and ")" not in stripped)


def extract_import_blocks(lines: list[str], start_idx: int) -> tuple[list[tuple[int, str]], int]:
    """Extrae bloques de imports, separando multilinea de unilinea.
    
    Returns:
        Lista de (índice_original, línea_texto) y índice_final
    """
    blocks: list[tuple[int, str]] = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Fin del bloque de imports
        if stripped == "":
            i += 1
            continue
        if stripped.startswith("#"):
            # Comentario dentro del bloque de imports - lo incluimos
            blocks.append((i, line))
            i += 1
            continue
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            break
        
        # Detectar import multilinea
        if is_multiline_import_start(line):
            # Es un import multilinea - lo tomamos completo tal cual
            multiline_block = [line]
            i += 1
            while i < len(lines):
                multiline_block.append(lines[i])
                if ")" in lines[i]:
                    i += 1
                    break
                i += 1
            # Agregar como un solo bloque con índice del inicio
            blocks.append((i - len(multiline_block), "\n".join(multiline_block)))
        else:
            # Import de una sola línea
            blocks.append((i, line))
            i += 1
    
    return blocks, i


def normalize_import_order_for_file(path: Path) -> bool:
    """Ordena los imports de un archivo según el ranking (versión segura).
    
    Características de seguridad:
    - Detecta y preserva imports multilinea intactos
    - Solo reordena imports de una sola línea
    - Mantiene comentarios asociados a imports
    - Preserva el docstring de Path al inicio
    """
    text = path.read_text(encoding="utf-8", errors="ignore").replace("\ufeff", "").replace("ï»¿", "")
    lines = text.splitlines()
    if not lines:
        return False

    # Encontrar dónde empieza el código (después del docstring)
    i = 0
    first = lines[0].lstrip("\ufeff") if lines else ""
    if lines and first.startswith('"""'):
        i = 1
        while i < len(lines):
            if '"""' in lines[i]:
                i += 1
                break
            i += 1
    elif lines and first.startswith("'''"):
        i = 1
        while i < len(lines):
            if "'''" in lines[i]:
                i += 1
                break
            i += 1

    # Saltar líneas vacías y comentarios sueltos antes de imports
    while i < len(lines) and (lines[i].strip() == "" or lines[i].strip().startswith("#")):
        i += 1
    start = i
    
    # Si no hay imports, salir
    if i >= len(lines):
        return False
    if not (lines[i].strip().startswith("import ") or lines[i].strip().startswith("from ")):
        return False

    # Extraer bloques de imports
    import_blocks, end = extract_import_blocks(lines, start)
    
    if len(import_blocks) <= 1:
        return False
    
    # Separar imports unilinea vs multilinea
    single_line_imports: list[tuple[int, str, str]] = []  # (idx, original, stripped)
    multiline_imports: list[tuple[int, str]] = []  # (idx, content)
    
    for idx, content in import_blocks:
        stripped = content.strip()
        if "\n" in content:
            # Es multilinea - preservar tal cual
            multiline_imports.append((idx, content))
        else:
            # Es unilinea
            single_line_imports.append((idx, content, stripped))
    
    # Si hay imports de grupo desconocido (rank 5), no tocar nada
    all_stripped = [s for _, _, s in single_line_imports]
    if any(import_rank(s) == 5 for s in all_stripped):
        return False
    
    # Ordenar solo los imports unilinea
    single_line_imports.sort(key=lambda x: (import_rank(x[2]), x[2]))
    
    # Reconstruir el bloque
    # Intercalar multilinea manteniendo su posición relativa aproximada
    # Estrategia: poner todos los unilinea ordenados primero, luego multilinea
    new_block_lines: list[str] = []
    
    # Agregar imports unilinea ordenados
    for _, original, _ in single_line_imports:
        new_block_lines.append(original)
    
    # Agregar imports multilinea (preservados tal cual)
    for _, content in multiline_imports:
        # Separar en líneas y agregar
        for ml_line in content.split("\n"):
            new_block_lines.append(ml_line)
    
    # Agregar línea vacía al final del bloque
    new_block_lines.append("")
    
    # Verificar si hubo cambios
    original_block = [lines[j] for j in range(start, end) if lines[j].strip() != ""]
    new_block_clean = [l for l in new_block_lines if l.strip() != ""]
    
    if original_block == new_block_clean:
        return False
    
    # Reconstruir archivo
    new_lines = lines[:start] + new_block_lines + lines[end:]
    path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return True


def normalize_import_order(repo_root: Path) -> list[str]:
    """Normaliza el orden de imports en todos los archivos .py."""
    fixed: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        if normalize_import_order_for_file(path):
            fixed.append(str(path.relative_to(repo_root)))
    return fixed


def ensure_gitignore_tmp(repo_root: Path) -> bool:
    """Agrega .tmp/ a .gitignore si falta."""
    path = repo_root / ".gitignore"
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if any(x.strip() == ".tmp/" for x in lines):
        return False
    if lines and lines[-1].strip() != "":
        lines.append("")
    lines.append(".tmp/")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return True


def ensure_gitkeep_files(repo_root: Path) -> list[str]:
    """Crea .gitkeep en directorios vacíos que no lo tengan."""
    gitkeep_dirs = [
        "src/entities",
        "src/use_cases",
        "src/interface_adapters/presenters",
        "src/interface_adapters/gateways",
        "docs",
        "tests",
    ]
    created: list[str] = []
    for d in gitkeep_dirs:
        # Solo crear .gitkeep si el directorio está vacío
        if dir_is_empty(repo_root, d):
            gitkeep_path = repo_root / d / ".gitkeep"
            if not gitkeep_path.exists():
                gitkeep_path.parent.mkdir(parents=True, exist_ok=True)
                gitkeep_path.write_text("", encoding="utf-8", newline="\n")
                created.append(f"{d}/.gitkeep")
    return created


def ensure_init_files(repo_root: Path) -> list[str]:
    """Crea __init__.py faltantes en src/."""
    created: list[str] = []
    for d in src_dirs(repo_root):
        if d.name == "__pycache__":
            continue
        if d.name == "data":
            continue
        init_file = d / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8", newline="\n")
            created.append(str(init_file.relative_to(repo_root)))
    return created


def archive_completed_tasks(repo_root: Path) -> tuple[int, bool]:
    """Mueve tareas completadas [x] de todo.md a todo.done.md.
    
    Returns:
        (num_tasks_moved, success)
    """
    todo_path = repo_root / "docs" / "todo.md"
    done_path = repo_root / "docs" / "todo.done.md"
    
    if not todo_path.exists():
        return 0, True
    
    content = todo_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    
    # Separar líneas completadas [x] de pendientes [ ] o sin checkbox
    completed_lines: list[str] = []
    pending_lines: list[str] = []
    
    for line in lines:
        stripped = line.strip()
        # Detectar líneas con checkbox completado [x] o [X]
        if re.match(r"^\s*-\s*\[[xX]\]", stripped):
            completed_lines.append(line)
        else:
            pending_lines.append(line)
    
    if not completed_lines:
        return 0, True
    
    # Escribir todo.md con solo tareas pendientes
    todo_path.write_text("\n".join(pending_lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    
    # Preparar contenido para todo.done.md
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    done_header = f"""# Tareas Completadas (`docs/todo.done.md`)

Archivo generado automaticamente. Tareas movidas desde `docs/todo.md`.

## Archivado: {timestamp}

"""
    
    done_content = "\n".join(completed_lines) + "\n"
    
    # Append a todo.done.md (o crear si no existe)
    if done_path.exists():
        existing = done_path.read_text(encoding="utf-8", errors="ignore").rstrip()
        # Insertar nuevo bloque después del header existente o al final
        if "## Archivado:" in existing:
            # Buscar última sección de archivado y agregar después
            new_done = existing + "\n\n## Archivado: " + timestamp + "\n\n" + done_content
        else:
            new_done = existing + "\n\n## Archivado: " + timestamp + "\n\n" + done_content
        done_path.write_text(new_done, encoding="utf-8", newline="\n")
    else:
        done_path.parent.mkdir(parents=True, exist_ok=True)
        done_path.write_text(done_header + done_content, encoding="utf-8", newline="\n")
    
    return len(completed_lines), True


def update_todo_md(repo_root: Path, violations: list[str]) -> bool:
    """Actualiza docs/todo.md consolidando bootstrap (0a) y estructura (1a)."""
    todo_path = repo_root / "docs" / "todo.md"
    
    # Primero, archivar tareas completadas
    archive_completed_tasks(repo_root)
    
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
    
    # Preparar sección de estructura
    if violations:
        structure_section = "### Estructura - Layout y Python File Policy (1a)\n"
        for v in violations:
            structure_section += f"- [ ] [structure-policy] Resolver: `{v}`.\n"
    else:
        structure_section = "### Estructura - Layout y Python File Policy (1a)\n- [x] [structure-policy] Estructura completa.\n"
    
    # Actualizar o insertar sección
    pattern = r"(<!-- project-structure:auto:start -->)[\s\S]*?(<!-- project-structure:auto:end -->)"
    
    if re.search(pattern, content):
        # Usar función lambda para evitar problemas con backslashes en el contenido
        def replacer(m):
            return m.group(1) + "\n## Project Structure Gate (autogenerado)\n\n" + structure_section + m.group(2)
        new_content = re.sub(pattern, replacer, content)
    else:
        new_content = content.rstrip() + f"\n\n<!-- project-structure:auto:start -->\n## Project Structure Gate (autogenerado)\n\n{structure_section}<!-- project-structure:auto:end -->\n"
    
    if new_content != content:
        todo_path.write_text(new_content, encoding="utf-8", newline="\n")
        return True
    return False


def run_audit_check(repo_root: Path) -> list[str]:
    """Ejecuta verificación rápida de violaciones de estructura."""
    violations: list[str] = []
    
    # Gitkeep check
    gitkeep_dirs = [
        "src/entities", "src/use_cases",
        "src/interface_adapters/presenters", "src/interface_adapters/gateways",
        "docs", "tests"
    ]
    for d in gitkeep_dirs:
        if not (repo_root / d / ".gitkeep").is_file():
            violations.append(f"missing_gitkeep:{d}/.gitkeep")
    
    # Init files check
    for d in src_dirs(repo_root):
        if d.name == "__pycache__":
            continue
        if d.name == "data":
            continue
        init_file = d / "__init__.py"
        if not init_file.exists():
            violations.append(f"missing_init:{str(d.relative_to(repo_root))}")
    
    # Non-empty init check
    for path in py_files_under_src(repo_root):
        if path.name != "__init__.py":
            continue
        if path.read_text(encoding="utf-8", errors="ignore").strip() != "":
            violations.append(f"non_empty_init:{str(path.relative_to(repo_root))}")
    
    # Path docstring check
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="ignore").lstrip()
        if not (text.startswith('"""') or text.startswith("'''")):
            violations.append(f"{rel}:missing_path_docstring")
            continue
        quote = text[:3]
        end = text.find(quote, 3)
        if end == -1:
            violations.append(f"{rel}:unclosed_docstring")
            continue
        header = text[3:end]
        if f"Path: {rel}" not in header:
            violations.append(f"{rel}:path_mismatch")
    
    # Import order check
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        import_lines = []
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            if s.startswith("import ") or s.startswith("from "):
                import_lines.append(s)
        ranks = [import_rank(x) for x in import_lines]
        if any(r == 5 for r in ranks):
            violations.append(f"{rel}:unknown_src_import_group")
            continue
        if any(ranks[i] > ranks[i + 1] for i in range(len(ranks) - 1)):
            violations.append(f"{rel}:import_order_invalid")
    
    # Gitignore check
    gitignore_path = repo_root / ".gitignore"
    if gitignore_path.exists():
        has_tmp = False
        for line in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip() == ".tmp/":
                has_tmp = True
                break
        if not has_tmp:
            violations.append("gitignore_missing_pattern:.tmp/")
    
    return violations


def run_repair(repo_root: Path, check_mode: bool = False) -> int:
    """Ejecuta el repair de estructura."""
    
    if check_mode:
        print("REPAIR=SKIPPED (check mode)")
        violations = run_audit_check(repo_root)
        for v in violations:
            print(f"  - {v}")
        return 0
    
    # Ejecutar reparaciones
    created_gitkeep = ensure_gitkeep_files(repo_root)
    created_init = ensure_init_files(repo_root)
    emptied_init = normalize_init_files(repo_root)
    fixed_docstrings = normalize_path_docstrings(repo_root)
    # Ordenar imports (algoritmo seguro: preserva multilinea, reordena unilinea)
    fixed_imports = normalize_import_order(repo_root)
    fixed_gitignore = ensure_gitignore_tmp(repo_root)
    
    # Archivar tareas completadas
    archived_count, _ = archive_completed_tasks(repo_root)
    
    # Verificar estado posterior
    remaining = run_audit_check(repo_root)
    updated_todo = update_todo_md(repo_root, remaining)
    
    print(f"REPAIR=DONE")
    print(f"CREATED_GITKEEP={len(created_gitkeep)}")
    print(f"CREATED_INIT={len(created_init)}")
    print(f"EMPTIED_INIT={len(emptied_init)}")
    print(f"FIXED_DOCSTRINGS={len(fixed_docstrings)}")
    print(f"FIXED_IMPORTS={len(fixed_imports)}")
    print(f"FIXED_GITIGNORE={fixed_gitignore}")
    print(f"ARCHIVED_TASKS={archived_count}")
    print(f"UPDATED_TODO_MD={updated_todo}")
    print(f"REMAINING_VIOLATIONS={len(remaining)}")
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair de estructura")
    parser.add_argument("--repo-root", required=True, help="Ruta raiz del repositorio")
    parser.add_argument("--check", action="store_true", help="Modo check (solo reportar)")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root)
    return run_repair(repo_root, check_mode=args.check)


if __name__ == "__main__":
    sys.exit(main())
