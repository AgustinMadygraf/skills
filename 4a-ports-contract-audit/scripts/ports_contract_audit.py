#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Dict, List


PORT_SUFFIXES = ("Port", "Gateway", "Protocol", "Interface")
TODO_START = "<!-- 4a-ports-contract-audit:auto:start -->"
TODO_END = "<!-- 4a-ports-contract-audit:auto:end -->"


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


def update_todo(repo_root: Path, report: Dict[str, object]) -> Path:
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    todo = docs / "todo.md"
    lines = [
        TODO_START,
        "## 4a-Ports Contract Audit (autogenerado)",
        "",
    ]
    findings = report.get("findings", [])
    if findings:
        for f in findings:
            lines.append(
                f"- [ ] [ports-contract:{f['severity']}] `{f['rule']}` en `{f['file']}:{f['line']}`."
            )
    else:
        lines.append("- [ ] Sin hallazgos de ports-contract-audit.")
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
    parser = argparse.ArgumentParser(description="Ports contract audit")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report = audit_ports(repo_root)
    todo_path = update_todo(repo_root, report)
    out = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        **report,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"4A_PORTS_CONTRACT_AUDIT={'PASS' if report['ok'] else 'FAIL'}")
        print(f"TODO={todo_path}")
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
