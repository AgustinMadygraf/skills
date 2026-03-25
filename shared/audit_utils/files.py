"""
Path: shared/audit_utils/files.py

Utilidades de filesystem para auditoría de código Python.
"""
from __future__ import annotations

import ast
from pathlib import Path


def py_files(root: Path, exclude_init: bool = True) -> list[Path]:
    """
    Lista archivos Python bajo un directorio.
    
    Args:
        root: Directorio raíz a escanear
        exclude_init: Si True, excluye __init__.py
    
    Returns:
        Lista ordenada de Path a archivos .py
    """
    if not root.is_dir():
        return []
    
    files = [p for p in root.rglob("*.py") if p.is_file()]
    
    if exclude_init:
        files = [p for p in files if p.name != "__init__.py"]
    
    return sorted(files)


def src_dirs(repo_root: Path) -> list[Path]:
    """
    Lista todos los directorios bajo src/.
    
    Args:
        repo_root: Raíz del repositorio
    
    Returns:
        Lista ordenada de Path a directorios (incluyendo src/)
    """
    root = repo_root / "src"
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*") if p.is_dir()] + [root])


def parse_ast(path: Path) -> ast.AST | None:
    """
    Parsea un archivo Python a AST.
    
    Args:
        path: Ruta al archivo .py
    
    Returns:
        AST del archivo o None si hay error de sintaxis o no existe
    """
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (SyntaxError, FileNotFoundError, OSError):
        return None


def relative_to_repo(path: Path, repo_root: Path) -> str:
    """
    Obtiene ruta relativa al repo con forward slashes.
    
    Args:
        path: Ruta absoluta o relativa
        repo_root: Raíz del repositorio
    
    Returns:
        String con ruta relativa usando /
    """
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")
