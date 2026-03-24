#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Dict, List


PORT_SUFFIXES = ("Port", "Gateway", "Protocol", "Interface")
TODO_START = "<!-- 4b-ports-contract-repair:auto:start -->"
TODO_END = "<!-- 4b-ports-contract-repair:auto:end -->"


def py_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*.py") if p.is_file() and p.name != "__init__.py"])


def parse_ast(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return None


def is_port_name(name: str) -> bool:
    return name.endswith(PORT_SUFFIXES)


def recommendation_for_finding(rule: str) -> str:
    if rule == "ports_missing_gateways_folder_content":
        return "Crear al menos un contrato de puerto en `src/interface_adapters/gateways/` (ej: `example_port.py` con clase `ExamplePort`)."
    if rule == "ports_use_case_imports_non_port_symbol":
        return "Reemplazar import del simbolo concreto por un contrato con sufijo de puerto (Port/Gateway/Protocol/Interface)."
    if rule == "ports_use_case_imports_infrastructure":
        return "Eliminar import directo a infraestructura desde use_cases e inyectar dependencia via contrato."
    if rule == "ports_contract_class_naming_invalid":
        return "Renombrar clase para terminar en `Port`, `Gateway`, `Protocol` o `Interface`."
    if rule == "ports_gateway_file_without_contract_class":
        return "Agregar clase de contrato al archivo o mover el contenido a otra capa."
    if rule == "ports_ast_parse_failed":
        return "Corregir errores de sintaxis para permitir analisis AST."
    return "Resolver manualmente segun politica de puertos/contratos del proyecto."


def audit_ports(repo_root: Path) -> Dict[str, object]:
    findings: list[Dict[str, object]] = []
    gateways_root = repo_root / "src" / "interface_adapters" / "gateways"
    use_cases_root = repo_root / "src" / "use_cases"

    gateway_files = py_files(gateways_root)
    use_case_files = py_files(use_cases_root)

    if use_case_files and not gateway_files:
        findings.append(
            {
                "severity": "warning",
                "rule": "ports_missing_gateways_folder_content",
                "file": "src/interface_adapters/gateways",
                "line": 1,
                "detail": "Hay use_cases pero no contratos en gateways.",
            }
        )

    for path in gateway_files:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        tree = parse_ast(path)
        if tree is None:
            findings.append(
                {
                    "severity": "warning",
                    "rule": "ports_ast_parse_failed",
                    "file": rel,
                    "line": 1,
                    "detail": "No se pudo analizar el archivo.",
                }
            )
            continue
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        if not classes:
            findings.append(
                {
                    "severity": "warning",
                    "rule": "ports_gateway_file_without_contract_class",
                    "file": rel,
                    "line": 1,
                    "detail": "Archivo de gateways sin clase de contrato.",
                }
            )
        for cls in classes:
            if not is_port_name(cls.name):
                findings.append(
                    {
                        "severity": "warning",
                        "rule": "ports_contract_class_naming_invalid",
                        "file": rel,
                        "line": cls.lineno,
                        "detail": f"Clase {cls.name} no termina en {PORT_SUFFIXES}.",
                    }
                )

    for path in use_case_files:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        tree = parse_ast(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("src.interface_adapters.gateways"):
                    for alias in node.names:
                        imported = alias.name
                        if imported == "*" or is_port_name(imported):
                            continue
                        findings.append(
                            {
                                "severity": "critical",
                                "rule": "ports_use_case_imports_non_port_symbol",
                                "file": rel,
                                "line": node.lineno,
                                "detail": imported,
                            }
                        )
                if module.startswith("src.infrastructure"):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "ports_use_case_imports_infrastructure",
                            "file": rel,
                            "line": node.lineno,
                            "detail": module,
                        }
                    )

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


def apply_mechanical_repairs(repo_root: Path, apply_changes: bool) -> List[Dict[str, str]]:
    actions: List[Dict[str, str]] = []
    gateways_root = repo_root / "src" / "interface_adapters" / "gateways"
    gateways_init = gateways_root / "__init__.py"

    if not gateways_root.exists():
        actions.append(
            {
                "action": "create_dir",
                "target": "src/interface_adapters/gateways",
                "status": "fixed" if apply_changes else "would_fix",
            }
        )
        if apply_changes:
            gateways_root.mkdir(parents=True, exist_ok=True)

    if not gateways_init.exists():
        actions.append(
            {
                "action": "create_file",
                "target": "src/interface_adapters/gateways/__init__.py",
                "status": "fixed" if apply_changes else "would_fix",
            }
        )
        if apply_changes:
            gateways_init.parent.mkdir(parents=True, exist_ok=True)
            gateways_init.write_text("", encoding="utf-8", newline="\n")

    if not actions:
        actions.append(
            {
                "action": "no_changes_needed",
                "target": "-",
                "status": "skipped",
            }
        )
    return actions


def update_todo(repo_root: Path, report: Dict[str, object], actions: List[Dict[str, str]], apply_changes: bool) -> Path:
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    todo = docs / "todo.md"
    lines = [
        TODO_START,
        "## 4b-Ports Contract Repair (autogenerado)",
        "",
        f"- Modo: `{'apply' if apply_changes else 'dry-run'}`",
        f"- Resumen: `critical={report.get('critical_total', 0)}` `warning={report.get('warning_total', 0)}` `info={report.get('info_total', 0)}`",
        "- Acciones:",
    ]
    for action in actions:
        lines.append(f"  - `{action['status']}` `{action['action']}` en `{action['target']}`.")
    lines.append("")
    lines.append("- Estado posterior:")
    findings = report.get("findings", [])
    if findings:
        for f in findings:
            lines.append(
                f"  - [ ] [ports-contract:{f['severity']}] `{f['rule']}` en `{f['file']}:{f['line']}`."
            )
            lines.append(f"    - Recomendacion: {recommendation_for_finding(str(f['rule']))}")
    else:
        lines.append("  - [ ] Sin hallazgos de ports-contract-repair.")
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
    parser = argparse.ArgumentParser(description="Ports contract repair")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--apply", action="store_true", help="Apply deterministic repairs")
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    before = audit_ports(repo_root)
    actions = apply_mechanical_repairs(repo_root, args.apply)
    after = audit_ports(repo_root)
    todo_path = update_todo(repo_root, after, actions, args.apply)
    out = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        "mode": "apply" if args.apply else "dry-run",
        "before": before,
        "after": after,
        "delta": {
            "critical": int(after.get("critical_total", 0)) - int(before.get("critical_total", 0)),
            "warning": int(after.get("warning_total", 0)) - int(before.get("warning_total", 0)),
            "info": int(after.get("info_total", 0)) - int(before.get("info_total", 0)),
        },
        "actions": actions,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"4B_PORTS_CONTRACT_REPAIR={'PASS' if after['ok'] else 'FAIL'}")
        print(f"TODO={todo_path}")
        print(f"ACTIONS={len(actions)}")
        print(
            "DELTA="
            f"critical:{out['delta']['critical']} "
            f"warning:{out['delta']['warning']} "
            f"info:{out['delta']['info']}"
        )
    return 0 if after["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
