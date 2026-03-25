"""
Path: shared/audit_utils/__init__.py

Utilidades compartidas para skills de auditoría (0a, 1a, 2a, 3a).

Scope: Solo utilidades puras sin estado. NO incluye lógica de reglas específicas.
"""
from __future__ import annotations

from .files import parse_ast, py_files, relative_to_repo, src_dirs
from .report import Finding, ReportBuilder, Severity
from .todo_writer import TodoWriter

__all__ = [
    # files
    "py_files",
    "src_dirs",
    "parse_ast",
    "relative_to_repo",
    # report
    "Finding",
    "Severity",
    "ReportBuilder",
    # todo_writer
    "TodoWriter",
]

__version__ = "1.0.0"
