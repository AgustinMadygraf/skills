#!/usr/bin/env python3
"""
Path: 2a-layer-boundary-gate/scripts/layer_boundary_gate.py
Layer Boundary Gate - Valida fronteras entre capas de Clean Architecture.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Dict, List

TODO_START = "<!-- 2a-layer-boundary-gate:auto:start -->"
TODO_END = "<!-- 2a-layer-boundary-gate:auto:end -->"

# Reglas de dependencia permitidas (source -> [allowed_targets])
LAYER_RULES = {
    "entities": [],
    "use_cases": ["entities"],
    "interface_adapters": ["entities", "use_cases"],
    "infrastructure": ["entities", "use_cases", "interface_adapters"],
}

# Capas que no deben ser importadas desde ciertas capas
PROHIBITED_IMPORTS = {
    "use_cases": ["infrastructure"],
    "presenters": ["controllers"],
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


def detect_layer(path: Path) -> str | None:
    """Detecta la capa de un archivo basado en su ruta."""
    parts = path.parts
    if "entities" in parts:
        return "entities"
    if "use_cases" in parts:
        return "use_cases"
    if "interface_adapters" in parts:
        return "interface_adapters"
    if "infrastructure" in parts:
        return "infrastructure"
    if "controllers" in parts:
        return "controllers"
    if "presenters" in parts:
        return "presenters"
    return None


def audit_layer_boundaries(repo_root: Path) -> Dict[str, object]:
    findings: list[Dict[str, object]] = []
    src_root = repo_root / "src"
    
    if not src_root.exists():
        return {
            "ok": True,
            "critical_total": 0,
            "warning_total": 0,
            "info_total": 0,
            "findings": [],
            "violations": [],
        }
    
    all_files = py_files(src_root)
    
    for path in all_files:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
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
                    findings.append({
                        "severity": "critical",
                        "rule": "use_cases_imports_infrastructure",
                        "file": rel,
                        "line": node.lineno,
                        "detail": module,
                    })
                
                # presenters no debe importar de controllers
                if source_layer == "presenters" and "controllers" in module:
                    findings.append({
                        "severity": "critical",
                        "rule": "presenters_imports_controllers",
                        "file": rel,
                        "line": node.lineno,
                        "detail": module,
                    })
                
                # infrastructure no debe ser importado desde capas internas
                if source_layer in ["entities", "use_cases"] and "infrastructure" in module:
                    findings.append({
                        "severity": "critical",
                        "rule": f"{source_layer}_imports_infrastructure",
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
        "## 2a-Layer Boundary Gate (autogenerado)",
        "",
    ]
    
    findings = report.get("findings", [])
    if findings:
        for f in findings:
            lines.append(
                f"- [ ] [layer-boundary:{f['severity']}] `{f['rule']}` en `{f['file']}:{f['line']}`."
            )
    else:
        lines.append("- [ ] Sin hallazgos de layer-boundary-gate.")
    
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
    parser = argparse.ArgumentParser(description="Layer boundary gate")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--check", action="store_true", help="Check mode (fail on critical)")
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    report = audit_layer_boundaries(repo_root)
    todo_path = update_todo(repo_root, report)
    
    out = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        **report,
    }
    
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"2A_LAYER_BOUNDARY_GATE={'PASS' if report['ok'] else 'FAIL'}")
        print(f"TODO={todo_path}")
    
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
