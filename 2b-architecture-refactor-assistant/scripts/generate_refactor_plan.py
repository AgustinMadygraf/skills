#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


LAYER_RE = re.compile(
    r"\[layer-boundary:(?P<severity>[a-z]+)\]\s+`(?P<rule>[^`]+)`\s+en\s+`(?P<file>[^:]+):(?P<line>\d+)`\.",
    re.IGNORECASE,
)


def parse_todo(todo_path: Path) -> list[dict[str, str]]:
    if not todo_path.exists():
        return []
    findings: list[dict[str, str]] = []
    for raw in todo_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if "[layer-boundary:" not in line:
            continue
        m = LAYER_RE.search(line)
        if not m:
            continue
        findings.append(
            {
                "severity": m.group("severity").lower(),
                "rule": m.group("rule"),
                "file": m.group("file"),
                "line": m.group("line"),
            }
        )
    return findings


def recommendation_for_rule(rule: str) -> str:
    mapping = {
        "infrastructure_imports_controllers": "Mover la orquestacion al adaptador controller y dejar infraestructura solo con I/O.",
        "infrastructure_imports_presenters": "Inyectar output port desde use_case y evitar dependencia directa a presenter desde infraestructura.",
        "presenters_imports_controllers": "Eliminar acoplamiento presenter->controller; controller debe depender de presenter (no al reves).",
        "use_cases_imports_infrastructure": "Reemplazar dependencia concreta por puerto/gateway abstracto en use_case.",
        "vendor_import_outside_infrastructure": "Encapsular libreria externa en src/infrastructure/* y exponer interfaz interna.",
    }
    return mapping.get(rule, "Aplicar inversion de dependencias para romper acoplamiento de capas.")


def build_batches(findings: list[dict[str, str]], batch_size: int) -> list[list[dict[str, str]]]:
    ordered = sorted(findings, key=lambda x: (x["severity"] != "critical", x["rule"], x["file"], int(x["line"])))
    return [ordered[i : i + batch_size] for i in range(0, len(ordered), batch_size)]


def write_plan(repo_root: Path, findings: list[dict[str, str]], batch_size: int) -> Path:
    out_path = repo_root / "docs" / "refactor" / "architecture-refactor-plan.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    by_rule: dict[str, int] = defaultdict(int)
    by_severity: dict[str, int] = defaultdict(int)
    for f in findings:
        by_rule[f["rule"]] += 1
        by_severity[f["severity"]] += 1

    lines: list[str] = []
    lines.append("# Architecture Refactor Plan")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Total hallazgos layer-boundary: {len(findings)}")
    sev_summary = ", ".join(f"{k}={by_severity[k]}" for k in sorted(by_severity.keys()))
    lines.append(f"- Severidad: {sev_summary or 'sin hallazgos'}")
    lines.append("")
    lines.append("## Reglas afectadas")
    lines.append("")
    if not findings:
        lines.append("- Sin hallazgos de layer-boundary.")
    else:
        for rule in sorted(by_rule.keys()):
            lines.append(f"- `{rule}`: {by_rule[rule]}")
    lines.append("")
    lines.append("## Lotes de trabajo")
    lines.append("")

    batches = build_batches(findings, batch_size=batch_size)
    if not batches:
        lines.append("No hay lotes pendientes.")
    else:
        for idx, batch in enumerate(batches, start=1):
            lines.append(f"### Lote {idx}")
            lines.append("")
            rules = sorted({x["rule"] for x in batch})
            lines.append(f"- Objetivo: resolver {len(batch)} hallazgos ({', '.join(rules)})")
            lines.append("- Checklist:")
            lines.append("  - [ ] Aplicar cambios de codigo")
            lines.append("  - [ ] Correr 1a-project-structure-gate")
            lines.append("  - [ ] Correr 2a-project-architecture-gate")
            lines.append("  - [ ] Actualizar docs/todo.md")
            lines.append("- Hallazgos:")
            for f in batch:
                rec = recommendation_for_rule(f["rule"])
                lines.append(
                    f"  - [ ] [{f['severity']}] `{f['rule']}` en `{f['file']}:{f['line']}`. Accion: {rec}"
                )
            lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate architecture refactor plan from docs/todo.md")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--todo", default="docs/todo.md", help="Todo file path (relative to repo root)")
    parser.add_argument("--batch-size", type=int, default=3, help="Findings per refactor batch")
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    todo_path = (repo_root / args.todo).resolve()
    findings = parse_todo(todo_path)
    plan_path = write_plan(repo_root, findings, batch_size=max(1, args.batch_size))
    summary = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        "plan_path": str(plan_path),
        "layer_findings_total": len(findings),
        "ok": True,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(f"PLAN={plan_path}")
        print(f"LAYER_FINDINGS={len(findings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

