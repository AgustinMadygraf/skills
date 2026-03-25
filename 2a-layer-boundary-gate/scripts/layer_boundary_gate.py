#!/usr/bin/env python3
"""
Path: 2a-layer-boundary-gate/scripts/layer_boundary_gate.py
Layer Boundary Gate - Valida fronteras entre capas de Clean Architecture.

Usa shared/audit_utils para utilidades comunes.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

# Agregar shared/ al path para importar audit_utils
SKILL_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT / "shared"))

from audit_utils import Finding, ReportBuilder, TodoWriter, parse_ast, py_files, relative_to_repo


# Capas que no deben ser importadas desde ciertas capas
PROHIBITED_IMPORTS = {
    "use_cases": ["infrastructure"],
    "presenters": ["controllers"],
}


def detect_layer(path: Path) -> str | None:
    """Detecta la capa de un archivo basado en su ruta.
    
    Verifica de más específico a más general:
    - Sub-capas de interface_adapters (controllers, presenters, gateways)
    - Capas principales
    """
    parts = path.parts
    # Sub-capas de interface_adapters (verificar primero, más específico)
    if "controllers" in parts:
        return "controllers"
    if "presenters" in parts:
        return "presenters"
    if "gateways" in parts:
        return "gateways"
    # Capas principales
    if "entities" in parts:
        return "entities"
    if "use_cases" in parts:
        return "use_cases"
    if "interface_adapters" in parts:
        return "interface_adapters"
    if "infrastructure" in parts:
        return "infrastructure"
    return None


def audit_layer_boundaries(repo_root: Path) -> dict[str, object]:
    """
    Valida que las fronteras entre capas de Clean Architecture se respeten.
    
    Args:
        repo_root: Raíz del repositorio
    
    Returns:
        Dict con el reporte completo
    """
    src_root = repo_root / "src"
    
    if not src_root.exists():
        return ReportBuilder().build().to_dict()
    
    builder = ReportBuilder()
    
    for path in py_files(src_root):
        rel = relative_to_repo(path, repo_root)
        source_layer = detect_layer(path)
        
        if not source_layer:
            continue
            
        tree = parse_ast(path)
        if tree is None:
            continue
            
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                
                # use_cases no debe importar de infrastructure
                if source_layer == "use_cases" and "infrastructure" in module:
                    builder.add_critical(
                        rule="use_cases_imports_infrastructure",
                        file=rel,
                        line=node.lineno,
                        detail=module,
                    )
                
                # presenters no debe importar de controllers
                if source_layer == "presenters" and "controllers" in module:
                    builder.add_critical(
                        rule="presenters_imports_controllers",
                        file=rel,
                        line=node.lineno,
                        detail=module,
                    )
                
                # infrastructure no debe ser importado desde capas internas
                if source_layer in ["entities", "use_cases"] and "infrastructure" in module:
                    builder.add_critical(
                        rule=f"{source_layer}_imports_infrastructure",
                        file=rel,
                        line=node.lineno,
                        detail=module,
                    )
    
    return builder.build().to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description="Layer boundary gate")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--check", action="store_true", help="Check mode (fail on critical)")
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    report_dict = audit_layer_boundaries(repo_root)
    
    # Escribir en docs/todo.md
    writer = TodoWriter(repo_root, "2a-layer-boundary-gate")
    findings = [Finding(**f) for f in report_dict.get("findings", [])]
    todo_path = writer.write_findings(
        findings,
        title="2a-Layer Boundary Gate",
        empty_message="Sin hallazgos de layer-boundary-gate.",
    )
    
    # Output
    out = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        **report_dict,
    }
    
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        ok = report_dict.get("ok", True)
        print(f"2A_LAYER_BOUNDARY_GATE={'PASS' if ok else 'FAIL'}")
        print(f"TODO={todo_path}")
    
    return 0 if report_dict.get("ok", True) else 2


if __name__ == "__main__":
    raise SystemExit(main())
