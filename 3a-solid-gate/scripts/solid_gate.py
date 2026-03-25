#!/usr/bin/env python3
"""
Path: 3a-solid-gate/scripts/solid_gate.py
SOLID Gate - Valida principios SOLID-lite: SRP, DIP, ISP.

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

# Umbrales default (lite)
DEFAULT_THRESHOLDS = {
    "max_use_case_classes_per_module": 3,
    "max_use_case_top_level_functions": 5,
    "max_gateway_public_methods": 10,
    "max_public_methods_per_class": 15,
}

# Umbrales strict
STRICT_THRESHOLDS = {
    "max_use_case_classes_per_module": 2,
    "max_use_case_top_level_functions": 3,
    "max_gateway_public_methods": 7,
    "max_public_methods_per_class": 10,
    "max_ocp_conditional_branches": 5,
}


STDlib_MODULES = {"typing", "abc", "dataclasses", "enum", "json", "pathlib"}


def audit_solid(repo_root: Path, profile: str = "lite") -> dict[str, object]:
    """
    Audita principios SOLID en el código.
    
    Args:
        repo_root: Raíz del repositorio
        profile: "lite" o "strict"
    
    Returns:
        Dict con el reporte completo
    """
    src_root = repo_root / "src"
    
    if not src_root.exists():
        return ReportBuilder().build().to_dict()
    
    thresholds = STRICT_THRESHOLDS if profile == "strict" else DEFAULT_THRESHOLDS
    builder = ReportBuilder()
    
    # SRP: Analizar use_cases
    use_cases_root = src_root / "use_cases"
    if use_cases_root.exists():
        _audit_use_cases(builder, use_cases_root, repo_root, thresholds, profile)
    
    # ISP: Analizar gateways
    gateways_root = src_root / "interface_adapters" / "gateways"
    if gateways_root.exists():
        _audit_gateways(builder, gateways_root, repo_root, thresholds)
    
    # DIP: Detectar imports de vendors en capas internas
    for layer in ["entities", "use_cases"]:
        layer_root = src_root / layer
        if layer_root.exists():
            _audit_vendor_imports(builder, layer_root, repo_root)
    
    return builder.build().to_dict()


def _audit_use_cases(
    builder: ReportBuilder,
    use_cases_root: Path,
    repo_root: Path,
    thresholds: dict,
    profile: str,
) -> None:
    """Audita reglas SRP en use_cases."""
    max_classes = thresholds.get("max_use_case_classes_per_module", 3)
    max_funcs = thresholds.get("max_use_case_top_level_functions", 5)
    max_methods = thresholds.get("max_public_methods_per_class", 15)
    severity = "critical" if profile == "strict" else "warning"
    
    for path in py_files(use_cases_root):
        rel = relative_to_repo(path, repo_root)
        tree = parse_ast(path)
        if tree is None:
            continue
        
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        
        # SRP: Demasiadas clases por modulo
        if len(classes) > max_classes:
            builder.add_finding(
                severity=severity,
                rule="srp_too_many_classes_per_module",
                file=rel,
                line=classes[max_classes].lineno if len(classes) > max_classes else 1,
                detail=f"{len(classes)} clases (max {max_classes})",
            )
        
        # SRP: Demasiadas funciones top-level
        if len(functions) > max_funcs:
            builder.add_finding(
                severity=severity,
                rule="srp_too_many_top_level_functions",
                file=rel,
                line=functions[max_funcs].lineno if len(functions) > max_funcs else 1,
                detail=f"{len(functions)} funciones (max {max_funcs})",
            )
        
        # ISP: Clases con demasiados métodos públicos
        for cls in classes:
            public_methods = [
                n for n in cls.body
                if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
            ]
            if len(public_methods) > max_methods:
                builder.add_finding(
                    severity=severity,
                    rule="isp_too_many_public_methods",
                    file=rel,
                    line=cls.lineno,
                    detail=f"{cls.name} tiene {len(public_methods)} metodos publicos (max {max_methods})",
                )


def _audit_gateways(
    builder: ReportBuilder,
    gateways_root: Path,
    repo_root: Path,
    thresholds: dict,
) -> None:
    """Audita reglas ISP en gateways."""
    max_methods = thresholds.get("max_gateway_public_methods", 10)
    
    for path in py_files(gateways_root):
        rel = relative_to_repo(path, repo_root)
        tree = parse_ast(path)
        if tree is None:
            continue
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                public_methods = [
                    n for n in node.body
                    if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
                ]
                if len(public_methods) > max_methods:
                    builder.add_finding(
                        severity="warning",
                        rule="isp_gateway_too_large",
                        file=rel,
                        line=node.lineno,
                        detail=f"{node.name} tiene {len(public_methods)} metodos publicos (max {max_methods})",
                    )


def _audit_vendor_imports(
    builder: ReportBuilder,
    layer_root: Path,
    repo_root: Path,
) -> None:
    """Audita reglas DIP: vendor imports en capas internas."""
    for path in py_files(layer_root):
        rel = relative_to_repo(path, repo_root)
        tree = parse_ast(path)
        if tree is None:
            continue
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module and not module.startswith("src."):
                    first_part = module.split(".")[0]
                    if first_part not in STDlib_MODULES:
                        builder.add_finding(
                            severity="warning",
                            rule="dip_vendor_import_in_internal_layer",
                            file=rel,
                            line=node.lineno,
                            detail=module,
                        )


def main() -> int:
    parser = argparse.ArgumentParser(description="SOLID gate")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--check", action="store_true", help="Check mode (fail on critical)")
    parser.add_argument("--solid-profile", default="lite", choices=["lite", "strict"])
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    report_dict = audit_solid(repo_root, args.solid_profile)
    
    # Escribir en docs/todo.md
    writer = TodoWriter(repo_root, "3a-solid-gate")
    findings = [Finding(**f) for f in report_dict.get("findings", [])]
    todo_path = writer.write_findings(
        findings,
        title="3a-SOLID Gate",
        empty_message="Sin hallazgos de solid-gate.",
    )
    
    # Output
    out = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        "profile": args.solid_profile,
        **report_dict,
    }
    
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        ok = report_dict.get("ok", True)
        print(f"3A_SOLID_GATE={'PASS' if ok else 'FAIL'}")
        print(f"TODO={todo_path}")
    
    return 0 if report_dict.get("ok", True) else 2


if __name__ == "__main__":
    raise SystemExit(main())
