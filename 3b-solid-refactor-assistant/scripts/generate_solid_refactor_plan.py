#!/usr/bin/env python3
"""
Path: 3b-solid-refactor-assistant/scripts/generate_solid_refactor_plan.py
Genera un plan de refactor SOLID basado en hallazgos de docs/todo.md.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Dict


def parse_todo_solid_findings(repo_root: Path) -> List[Dict[str, str]]:
    """Extrae hallazgos SOLID de docs/todo.md."""
    findings = []
    todo = repo_root / "docs" / "todo.md"
    
    if not todo.exists():
        return findings
    
    content = todo.read_text(encoding="utf-8", errors="ignore")
    
    # Buscar patrones de hallazgos SOLID
    pattern = r"- \[ \] \[solid:(\w+)\] `([^`]+)` en `([^:]+):(\d+)"  # noqa: W605
    matches = re.findall(pattern, content)
    
    for severity, rule, file, line in matches:
        findings.append({
            "severity": severity,
            "rule": rule,
            "file": file,
            "line": line,
        })
    
    return findings


def generate_refactor_plan(findings: List[Dict[str, str]]) -> str:
    """Genera un plan de refactor basado en los hallazgos."""
    lines = [
        "# Plan de Refactor SOLID",
        "",
        f"Total de hallazgos: {len(findings)}",
        "",
        "## Priorizacion",
        "",
        "1. **Critical**: Resolver primero (bloquean CI)",
        "2. **Warning**: Resolver en siguiente sprint",
        "3. **Info**: Mejoras opcionales",
        "",
        "## Hallazgos agrupados por tipo",
        "",
    ]
    
    # Agrupar por regla
    by_rule: Dict[str, List[Dict[str, str]]] = {}
    for f in findings:
        rule = f["rule"]
        if rule not in by_rule:
            by_rule[rule] = []
        by_rule[rule].append(f)
    
    for rule, items in sorted(by_rule.items()):
        lines.append(f"### {rule}")
        lines.append("")
        lines.append(f"**Cantidad**: {len(items)}")
        lines.append("")
        
        # Sugerencias específicas por tipo
        if "srp" in rule:
            lines.append("**Sugerencia**: Extraer responsabilidades a clases separadas.")
        elif "isp" in rule:
            lines.append("**Sugerencia**: Dividir interfaz en interfaces mas pequenas y especificas.")
        elif "dip" in rule:
            lines.append("**Sugerencia**: Introducir abstraccion (puerto) e inyectar dependencia.")
        
        lines.append("")
        lines.append("**Archivos afectados**:")
        for item in items:
            lines.append(f"- `{item['file']}:{item['line']}` ({item['severity']})")
        lines.append("")
    
    lines.extend([
        "## Proximos pasos",
        "",
        "1. Revisar hallazgos `critical` uno por uno",
        "2. Para cada hallazgo, crear rama de refactor",
        "3. Aplicar cambio con tests de respaldo",
        "4. Ejecutar `$3a-solid-gate` para validar",
        "5. Mergear y actualizar baseline si aplica",
        "",
    ])
    
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SOLID refactor plan")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--output", help="Output file (default: docs/refactor/solid-refactor-plan.md)")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    output_path = Path(args.output) if args.output else repo_root / "docs" / "refactor" / "solid-refactor-plan.md"
    
    findings = parse_todo_solid_findings(repo_root)
    plan = generate_refactor_plan(findings)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(plan, encoding="utf-8", newline="\n")
    
    print(f"SOLID_REFACTOR_PLAN={output_path}")
    print(f"FINDINGS={len(findings)}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
