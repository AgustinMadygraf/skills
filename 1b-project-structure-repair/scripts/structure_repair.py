#!/usr/bin/env python3
"""
Path: 1b-project-structure-repair/scripts/structure_repair.py
Script de repair de estructura - ENFOQUE REACTIVO basado en docs/todo.md.

Este script NO detecta violaciones por sí mismo, sino que lee las detectadas
por 1a-project-structure-gate desde docs/todo.md y ejecuta las reparaciones.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


# Marcadores de sección en docs/todo.md
TODO_AUTOGEN_START = "<!-- project-gates:auto:start -->"
TODO_AUTOGEN_END = "<!-- project-gates:auto:end -->"


def parse_todo_items(repo_root: Path) -> Dict[str, List[str]]:
    """Parsea docs/todo.md y extrae items pendientes por categoría.
    
    Returns:
        Dict con claves: 'bootstrap-policy', 'env-policy', 'layout-policy', 
        'python-file-policy', 'layer-boundary', 'solid-lite', 'solid-strict'
    """
    todo_path = repo_root / "docs" / "todo.md"
    items_by_type: Dict[str, List[str]] = {
        "bootstrap-policy": [],
        "env-policy": [],
        "layout-policy": [],
        "python-file-policy": [],
        "layer-boundary": [],
        "solid-lite": [],
        "solid-strict": [],
        "solid-thresholds": [],
        "architecture-exemptions": [],
    }
    
    if not todo_path.exists():
        return items_by_type
    
    content = todo_path.read_text(encoding="utf-8", errors="ignore")
    
    # Buscar sección autogenerada
    start = content.find(TODO_AUTOGEN_START)
    end = content.find(TODO_AUTOGEN_END)
    
    if start == -1 or end == -1 or end <= start:
        return items_by_type
    
    section = content[start:end]
    
    # Parsear items pendientes (solo - [ ], no - [x])
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("- [ ]"):
            continue
        
        # Extraer tipo de política
        match = re.search(r'\[([^\]]+policy)\]', line)
        if match:
            policy_type = match.group(1)
            if policy_type in items_by_type:
                items_by_type[policy_type].append(line)
        
        # Extraer layer-boundary, solid-lite, etc.
        match = re.search(r'\[(layer-boundary|solid-lite|solid-strict|solid-thresholds|architecture-exemptions)', line)
        if match:
            policy_type = match.group(1)
            items_by_type[policy_type].append(line)
    
    return items_by_type


def extract_violation_detail(line: str) -> Optional[str]:
    """Extrae el detalle de una violación desde una línea de todo.md."""
    # Buscar patrones comunes
    match = re.search(r'Resolver:\s*`([^`]+)`', line)
    if match:
        return match.group(1)
    
    match = re.search(r'Agregar\s*`([^`]+)`', line)
    if match:
        return match.group(1)
    
    match = re.search(r'Corregir[^:]+:\s*`([^`]+)`', line)
    if match:
        return match.group(1)
    
    match = re.search(r'`([^`]+:\d+:[^`]+)`', line)
    if match:
        return match.group(1)
    
    return None


# ============================================================================
# REPARACIONES POR TIPO
# ============================================================================

def repair_layout_policy(repo_root: Path, items: List[str]) -> Dict[str, List[str]]:
    """Repara violaciones de layout-policy (bootstrap-policy incluido)."""
    results = {"created_gitkeep": [], "created_dirs": [], "created_files": []}
    
    gitkeep_dirs = ["src/entities", "src/use_cases", "src/interface_adapters/presenters", 
                    "src/interface_adapters/gateways", "docs", "tests"]
    
    for item in items:
        detail = extract_violation_detail(item)
        if not detail:
            continue
        
        # missing_gitkeep
        if "missing_gitkeep" in detail:
            dir_path = detail.split(":")[1].replace("/.gitkeep", "")
            if dir_path in gitkeep_dirs:
                gitkeep_path = repo_root / dir_path / ".gitkeep"
                if not gitkeep_path.exists() and dir_is_empty(repo_root, dir_path):
                    gitkeep_path.parent.mkdir(parents=True, exist_ok=True)
                    gitkeep_path.write_text("", encoding="utf-8", newline="\n")
                    results["created_gitkeep"].append(f"{dir_path}/.gitkeep")
        
        # missing_dir
        elif "missing_dir" in detail:
            dir_path = detail.split(":")[1]
            target = repo_root / dir_path
            if not target.exists():
                target.mkdir(parents=True, exist_ok=True)
                results["created_dirs"].append(dir_path)
        
        # missing_file
        elif "missing_file" in detail:
            file_path = detail.split(":")[1]
            # Nota: archivos esenciales como README.md, .env deben crearse manualmente
            pass
    
    return results


def repair_env_policy(repo_root: Path, items: List[str]) -> Dict[str, int]:
    """Repara violaciones de env-policy (sincronización de keys)."""
    results = {"added_to_example": 0, "added_to_env": 0}
    
    env_path = repo_root / ".env"
    env_example_path = repo_root / ".env.example"
    
    if not env_path.exists() or not env_example_path.exists():
        return results
    
    env_content = env_path.read_text(encoding="utf-8", errors="ignore")
    example_content = env_example_path.read_text(encoding="utf-8", errors="ignore")
    
    env_keys = set(re.findall(r'^([A-Z_][A-Z0-9_]*)=', env_content, re.MULTILINE))
    example_keys = set(re.findall(r'^([A-Z_][A-Z0-9_]*)=', example_content, re.MULTILINE))
    
    for item in items:
        if "Agregar" in item and "a `.env.example`" in item:
            match = re.search(r'`([^`]+)`', item)
            if match:
                key = match.group(1)
                if key in env_keys and key not in example_keys:
                    # Extraer valor de .env
                    val_match = re.search(rf'^{key}=(.+)$', env_content, re.MULTILINE)
                    if val_match:
                        value = val_match.group(1)
                        # Agregar a .env.example con valor placeholder si es secreto
                        if any(s in key.lower() for s in ['secret', 'password', 'token', 'key']):
                            placeholder = "your_" + key.lower() + "_here"
                        else:
                            placeholder = value
                        
                        with open(env_example_path, "a", encoding="utf-8") as f:
                            f.write(f"\n{key}={placeholder}")
                        results["added_to_example"] += 1
        
        elif "Agregar" in item and "a `.env`" in item:
            match = re.search(r'`([^`]+)`', item)
            if match:
                key = match.group(1)
                if key in example_keys and key not in env_keys:
                    # Extraer valor de .env.example
                    val_match = re.search(rf'^{key}=(.+)$', example_content, re.MULTILINE)
                    if val_match:
                        value = val_match.group(1)
                        with open(env_path, "a", encoding="utf-8") as f:
                            f.write(f"\n{key}={value}")
                        results["added_to_env"] += 1
    
    return results


def repair_python_file_policy(repo_root: Path, items: List[str]) -> Dict[str, List[str]]:
    """Repara violaciones de python-file-policy."""
    results = {
        "fixed_imports": [],
        "fixed_docstrings": [],
        "removed_unused_imports": {},
        "emptied_init": []
    }
    
    # Agrupar violaciones por archivo
    files_with_import_order = set()
    files_with_docstring = set()
    files_with_unused = set()
    files_with_non_empty_init = set()
    
    for item in items:
        detail = extract_violation_detail(item)
        if not detail:
            continue
        
        if ":import_order_invalid" in detail or ":unknown_src_import_group" in detail:
            file = detail.split(":")[0]
            files_with_import_order.add(file)
        
        elif ":missing_path_docstring" in detail or ":path_mismatch" in detail:
            file = detail.split(":")[0]
            files_with_docstring.add(file)
        
        elif "non_empty_init" in detail or "forbidden_dataclass" in detail:
            file = detail.split(":")[0] if ":" in detail else detail.replace("non_empty_init:", "")
            if "__init__.py" in file:
                files_with_non_empty_init.add(file)
    
    # Reparar orden de imports
    for rel_path in files_with_import_order:
        path = repo_root / rel_path
        if path.exists() and normalize_import_order_for_file(path):
            results["fixed_imports"].append(rel_path)
    
    # Reparar docstrings
    for rel_path in files_with_docstring:
        path = repo_root / rel_path
        if path.exists():
            if ensure_path_docstring_for_file(path, rel_path):
                results["fixed_docstrings"].append(rel_path)
    
    # Vaciar __init__.py no vacíos (sin exports)
    for rel_path in files_with_non_empty_init:
        path = repo_root / rel_path
        if path.exists() and path.name == "__init__.py":
            text = path.read_text(encoding="utf-8", errors="ignore")
            # Preservar si tiene exports intencionales
            if "__all__" in text or "from ." in text or "from src." in text:
                continue
            if text.strip() != "":
                path.write_text("", encoding="utf-8", newline="\n")
                results["emptied_init"].append(rel_path)
    
    # Eliminar imports no usados en todos los archivos .py
    removed = remove_unused_imports(repo_root)
    results["removed_unused_imports"] = removed
    
    return results


# ============================================================================
# FUNCIONES AUXILIARES (mantenidas del script original)
# ============================================================================

def py_files_under_src(repo_root: Path) -> list[Path]:
    """Lista todos los archivos .py bajo src/."""
    root = repo_root / "src"
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*.py") if p.is_file()])


def dir_is_empty(repo_root: Path, dir_path: str) -> bool:
    """Verifica si un directorio está vacío (necesita .gitkeep)."""
    d = repo_root / dir_path
    if not d.is_dir():
        return False
    
    for item in d.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_file():
            return False
        if item.is_dir():
            if not dir_is_empty(repo_root, str(item.relative_to(repo_root))):
                return False
    
    return True


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
    """Detecta si una línea es el inicio de un import multilinea."""
    stripped = line.strip()
    if not (stripped.startswith("import ") or stripped.startswith("from ")):
        return False
    return stripped.endswith("(") or ("(" in stripped and ")" not in stripped)


def extract_import_blocks(lines: list[str], start_idx: int) -> tuple[list[tuple[int, str]], int]:
    """Extrae bloques de imports, separando multilinea de unilinea."""
    blocks: list[tuple[int, str]] = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped == "":
            i += 1
            continue
        if stripped.startswith("#"):
            blocks.append((i, line))
            i += 1
            continue
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            break
        
        if is_multiline_import_start(line):
            multiline_block = [line]
            i += 1
            while i < len(lines):
                multiline_block.append(lines[i])
                if ")" in lines[i]:
                    i += 1
                    break
                i += 1
            blocks.append((i - len(multiline_block), "\n".join(multiline_block)))
        else:
            blocks.append((i, line))
            i += 1
    
    return blocks, i


def normalize_import_order_for_file(path: Path) -> bool:
    """Ordena los imports de un archivo según el ranking (versión segura)."""
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

    while i < len(lines) and (lines[i].strip() == "" or lines[i].strip().startswith("#")):
        i += 1
    start = i
    
    if i >= len(lines):
        return False
    if not (lines[i].strip().startswith("import ") or lines[i].strip().startswith("from ")):
        return False

    import_blocks, end = extract_import_blocks(lines, start)
    
    if len(import_blocks) <= 1:
        return False
    
    single_line_imports: list[tuple[int, str, str]] = []
    multiline_imports: list[tuple[int, str]] = []
    
    for idx, content in import_blocks:
        stripped = content.strip()
        if "\n" in content:
            multiline_imports.append((idx, content))
        else:
            single_line_imports.append((idx, content, stripped))
    
    all_stripped = [s for _, _, s in single_line_imports]
    if any(import_rank(s) == 5 for s in all_stripped):
        return False
    
    single_line_imports.sort(key=lambda x: (import_rank(x[2]), x[2]))
    
    new_block_lines: list[str] = []
    
    for _, original, _ in single_line_imports:
        new_block_lines.append(original)
    
    for _, content in multiline_imports:
        for ml_line in content.split("\n"):
            new_block_lines.append(ml_line)
    
    new_block_lines.append("")
    
    original_block = [lines[j] for j in range(start, end) if lines[j].strip() != ""]
    new_block_clean = [l for l in new_block_lines if l.strip() != ""]
    
    if original_block == new_block_clean:
        return False
    
    new_lines = lines[:start] + new_block_lines + lines[end:]
    path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return True


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
    rem2, second_header = strip_one_leading_docstring(remainder)
    if rem2 != remainder and "Path:" in second_header:
        remainder = rem2

    new_text = expected + "\n\n" + remainder.lstrip("\n")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8", newline="\n")
        return True
    return False


def get_used_names(tree: ast.AST) -> set[str]:
    """Extrae todos los nombres usados en el código (no en imports)."""
    used: set[str] = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                used.add(node.value.id)
        elif isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                used.add(node.value.id)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                used.add(node.func.id)
    
    return used


def extract_import_info(tree: ast.AST) -> list[tuple[ast.Import | ast.ImportFrom, list[str]]]:
    """Extrae imports y los nombres que importan.
    
    NOTA: Los imports de __future__ se detectan pero deben preservarse
    (son directives del compilador, no crean nombres usables).
    """
    imports_info = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name.split('.')[0] for alias in node.names]
            imports_info.append((node, names))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            # Preservar TODOS los imports de __future__
            if module == "__future__":
                continue  # No incluir en la lista de imports a verificar
            names = [alias.asname or alias.name for alias in node.names]
            imports_info.append((node, names))
    
    return imports_info


def remove_unused_imports(repo_root: Path) -> dict[str, list[str]]:
    """Elimina imports no usados en todo el proyecto."""
    results: dict[str, list[str]] = {}
    
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text)
        except SyntaxError:
            continue
        
        used_names = get_used_names(tree)
        imports_info = extract_import_info(tree)
        
        unused_imports: list[ast.Import | ast.ImportFrom] = []
        removed_names: list[str] = []
        
        for import_node, imported_names in imports_info:
            any_used = any(name in used_names or name == '*' for name in imported_names)
            if not any_used:
                unused_imports.append(import_node)
                removed_names.extend(imported_names)
        
        if not unused_imports:
            continue
        
        lines = text.splitlines()
        lines_to_remove: set[int] = set()
        
        for node in unused_imports:
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                for i in range(node.lineno - 1, node.end_lineno):
                    lines_to_remove.add(i)
            elif hasattr(node, 'lineno'):
                lines_to_remove.add(node.lineno - 1)
        
        new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
        
        if len(new_lines) != len(lines):
            path.write_text('\n'.join(new_lines) + ('\n' if text.endswith('\n') else ''), 
                           encoding="utf-8", newline="\n")
            results[str(path.relative_to(repo_root))] = removed_names
    
    return results


def archive_completed_tasks(repo_root: Path) -> tuple[int, bool]:
    """Mueve tareas completadas [x] de todo.md a todo.done.md."""
    todo_path = repo_root / "docs" / "todo.md"
    done_path = repo_root / "docs" / "todo.done.md"
    
    if not todo_path.exists():
        return 0, True
    
    content = todo_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    
    completed_lines: list[str] = []
    pending_lines: list[str] = []
    
    for line in lines:
        stripped = line.strip()
        if re.match(r"^\s*-\s*\[[xX]\]", stripped):
            completed_lines.append(line)
        else:
            pending_lines.append(line)
    
    if not completed_lines:
        return 0, True
    
    todo_path.write_text("\n".join(pending_lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    done_header = f"""# Tareas Completadas (`docs/todo.done.md`)

Archivo generado automaticamente. Tareas movidas desde `docs/todo.md`.

## Archivado: {timestamp}

"""
    
    done_content = "\n".join(completed_lines) + "\n"
    
    if done_path.exists():
        existing = done_path.read_text(encoding="utf-8", errors="ignore").rstrip()
        new_done = existing + "\n\n## Archivado: " + timestamp + "\n\n" + done_content
        done_path.write_text(new_done, encoding="utf-8", newline="\n")
    else:
        done_path.parent.mkdir(parents=True, exist_ok=True)
        done_path.write_text(done_header + done_content, encoding="utf-8", newline="\n")
    
    return len(completed_lines), True


# ============================================================================
# FLUJO PRINCIPAL REACTIVO
# ============================================================================

def run_repair(repo_root: Path, check_mode: bool = False) -> int:
    """Ejecuta el repair de estructura basado en docs/todo.md (ENFOQUE REACTIVO)."""
    
    if check_mode:
        print("REPAIR=SKIPPED (check mode - no hay modo check en enfoque reactivo)")
        return 0
    
    # 1. Leer items pendientes de docs/todo.md
    items_by_type = parse_todo_items(repo_root)
    
    # Contar items antes de reparar
    total_items = sum(len(items) for items in items_by_type.values())
    
    if total_items == 0:
        print("REPAIR=SKIPPED (no items pendientes en docs/todo.md)")
        print("SUGERENCIA: Ejecuta primero: $1a-project-structure-gate")
        return 0
    
    print(f"REPAIR_MODE=REACTIVE (basado en docs/todo.md)")
    print(f"TOTAL_ITEMS_PENDING={total_items}")
    
    # 2. Ejecutar reparaciones por tipo
    all_results = {}
    
    # Layout/Bootstrap
    layout_items = items_by_type.get("layout-policy", []) + items_by_type.get("bootstrap-policy", [])
    if layout_items:
        print(f"\n[1/3] Reparando {len(layout_items)} items de layout/bootstrap...")
        layout_results = repair_layout_policy(repo_root, layout_items)
        all_results["layout"] = layout_results
        print(f"  - Gitkeep creados: {len(layout_results['created_gitkeep'])}")
        print(f"  - Directorios creados: {len(layout_results['created_dirs'])}")
    
    # ENV
    env_items = items_by_type.get("env-policy", [])
    if env_items:
        print(f"\n[2/3] Reparando {len(env_items)} items de env-policy...")
        env_results = repair_env_policy(repo_root, env_items)
        all_results["env"] = env_results
        print(f"  - Agregados a .env.example: {env_results['added_to_example']}")
        print(f"  - Agregados a .env: {env_results['added_to_env']}")
    
    # Python file policy
    python_items = items_by_type.get("python-file-policy", [])
    if python_items:
        print(f"\n[3/3] Reparando {len(python_items)} items de python-file-policy...")
        python_results = repair_python_file_policy(repo_root, python_items)
        all_results["python"] = python_results
        print(f"  - Imports ordenados: {len(python_results['fixed_imports'])}")
        print(f"  - Docstrings arreglados: {len(python_results['fixed_docstrings'])}")
        print(f"  - Imports no usados eliminados: {sum(len(v) for v in python_results['removed_unused_imports'].values())}")
        print(f"  - __init__.py vaciados: {len(python_results['emptied_init'])}")
    
    # Nota: Items de arquitectura (layer-boundary, solid) NO los procesamos
    # Son responsabilidad de skills 2b/3b
    arch_items = (items_by_type.get("layer-boundary", []) + 
                  items_by_type.get("solid-lite", []) + 
                  items_by_type.get("solid-strict", []))
    if arch_items:
        print(f"\n[!] {len(arch_items)} items de arquitectura NO procesados (usar skills 2b/3b)")
    
    # 3. Archivar tareas completadas
    archived_count, _ = archive_completed_tasks(repo_root)
    
    # 4. Reporte final
    print(f"\n{'='*50}")
    print("REPAIR=DONE")
    print(f"ARCHIVED_TASKS={archived_count}")
    print(f"NOTA: Re-ejecuta $1a-project-structure-gate para verificar estado")
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair de estructura - ENFOQUE REACTIVO (lee docs/todo.md)"
    )
    parser.add_argument("--repo-root", required=True, help="Ruta raiz del repositorio")
    parser.add_argument("--check", action="store_true", help="[DEPRECATED] Use 1a para check")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root)
    return run_repair(repo_root, check_mode=args.check)


if __name__ == "__main__":
    sys.exit(main())
