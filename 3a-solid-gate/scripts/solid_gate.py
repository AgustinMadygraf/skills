#!/usr/bin/env python3
"""
Path: 3a-solid-gate/scripts/solid_gate.py
SOLID Gate - Valida principios SOLID-lite: SRP, DIP, ISP.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Dict, List

TODO_START = "<!-- 3a-solid-gate:auto:start -->"
TODO_END = "<!-- 3a-solid-gate:auto:end -->"

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


def py_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*.py") if p.is_file() and p.name != "__init__.py"])


def parse_ast(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return None


def audit_solid(repo_root: Path, profile: str = "lite") -> Dict[str, object]:
    findings: list[Dict[str, object]] = []
    src_root = repo_root / "src"
    
    thresholds = STRICT_THRESHOLDS if profile == "strict" else DEFAULT_THRESHOLDS
    
    if not src_root.exists():
        return {
            "ok": True,
            "critical_total": 0,
            "warning_total": 0,
            "info_total": 0,
            "findings": [],
            "violations": [],
        }
    
    # SRP: Analizar use_cases
    use_cases_root = src_root / "use_cases"
    if use_cases_root.exists():
        for path in py_files(use_cases_root):
            rel = str(path.relative_to(repo_root)).replace("\\", "/")
            tree = parse_ast(path)
            if tree is None:
                continue
            
            classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
            functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
            
            # SRP: Demasiadas clases por modulo
            max_classes = thresholds.get("max_use_case_classes_per_module", 3)
            if len(classes) > max_classes:
                findings.append({
                    "severity": "warning" if profile == "lite" else "critical",
                    "rule": "srp_too_many_classes_per_module",
                    "file": rel,
                    "line": 1,
                    "detail": f"{len(classes)} clases (max {max_classes})",
                })
            
            # SRP: Demasiadas funciones top-level
            max_funcs = thresholds.get("max_use_case_top_level_functions", 5)
            if len(functions) > max_funcs:
                findings.append({
                    "severity": "warning" if profile == "lite" else "critical",
                    "rule": "srp_too_many_top_level_functions",
                    "file": rel,
                    "line": 1,
                    "detail": f"{len(functions)} funciones (max {max_funcs})",
                })
            
            # ISP: Clases con demasiados metodos publicos
            max_methods = thresholds.get("max_public_methods_per_class", 15)
            for cls in classes:
                public_methods = [
                    n for n in cls.body 
                    if isinstance(n, ast.FunctionDef) 
                    and not n.name.startswith("_")
                ]
                if len(public_methods) > max_methods:
                    findings.append({
                        "severity": "warning" if profile == "lite" else "critical",
                        "rule": "isp_too_many_public_methods",
                        "file": rel,
                        "line": cls.lineno,
                        "detail": f"{cls.name} tiene {len(public_methods)} metodos publicos (max {max_methods})",
                    })
    
    # ISP: Analizar gateways
    gateways_root = src_root / "interface_adapters" / "gateways"
    if gateways_root.exists():
        for path in py_files(gateways_root):
            rel = str(path.relative_to(repo_root)).replace("\\", "/")
            tree = parse_ast(path)
            if tree is None:
                continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    public_methods = [
                        n for n in node.body 
                        if isinstance(n, ast.FunctionDef) 
                        and not n.name.startswith("_")
                    ]
                    max_methods = thresholds.get("max_gateway_public_methods", 10)
                    if len(public_methods) > max_methods:
                        findings.append({
                            "severity": "warning" if profile == "lite" else "critical",
                            "rule": "isp_gateway_too_large",
                            "file": rel,
                            "line": node.lineno,
                            "detail": f"{node.name} tiene {len(public_methods)} metodos publicos (max {max_methods})",
                        })
    
    # DIP: Detectar imports de vendors en capas internas
    internal_layers = [src_root / "entities", src_root / "use_cases"]
    for layer_root in internal_layers:
        if not layer_root.exists():
            continue
        for path in py_files(layer_root):
            rel = str(path.relative_to(repo_root)).replace("\\", "/")
            tree = parse_ast(path)
            if tree is None:
                continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    # Import de vendor/externo en capa interna
                    if module and not module.startswith("src."):
                        # Excluir stdlib
                        first_part = module.split(".")[0]
                        if first_part not in ["typing", "abc", "dataclasses", "enum", "json", "pathlib"]:
                            findings.append({
                                "severity": "warning",
                                "rule": "dip_vendor_import_in_internal_layer",
                                "file": rel,
                                "line": node.lineno,
                                "detail": module,
                            })
    
    critical = [f for f in findings if f["severity"] == "critical"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    infos = [f for f in findings if f["severity"] == "info"]
    
    return {
        "ok": len(critical) == 0,
        "critical_total": len(critical),
        "warning_total": len(warnings),
        "info_total": len(infos),
        "findings": findings,
        "violations": [f"{x['file']}:{x['line']}:{x['rule']}" for x in findings],
    }


def update_todo(repo_root: Path, report: Dict[str, object]) -> Path:
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    todo = docs / "todo.md"
    
    lines = [
        TODO_START,
        "## 3a-SOLID Gate (autogenerado)",
        "",
    ]
    
    findings = report.get("findings", [])
    if findings:
        for f in findings:
            lines.append(
                f"- [ ] [solid:{f['severity']}] `{f['rule']}` en `{f['file']}:{f['line']}`."
            )
    else:
        lines.append("- [ ] Sin hallazgos de solid-gate.")
    
    lines.append(TODO_END)
    block = "\n".join(lines) + "\n"
    
    if not todo.exists():
        todo.write_text("# TODO\n\n" + block, encoding="utf-8", newline="\n")
        return todo
    
    content = todo.read_text(encoding="utf-8", errors="ignore")
    s = content.find(TODO_START)
    e = content.find(TODO_END)
    
    if s != -1 and e != -1 and e >= s:
        e = e + len(TODO_END)
        new_content = content[:s].rstrip() + "\n\n" + block + content[e:].lstrip("\n")
    else:
        new_content = content.rstrip() + "\n\n" + block
    
    todo.write_text(new_content, encoding="utf-8", newline="\n")
    return todo


def main() -> int:
    parser = argparse.ArgumentParser(description="SOLID gate")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--check", action="store_true", help="Check mode (fail on critical)")
    parser.add_argument("--solid-profile", default="lite", choices=["lite", "strict"])
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    report = audit_solid(repo_root, args.solid_profile)
    todo_path = update_todo(repo_root, report)
    
    out = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        "profile": args.solid_profile,
        **report,
    }
    
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"3A_SOLID_GATE={'PASS' if report['ok'] else 'FAIL'}")
        print(f"TODO={todo_path}")
    
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
