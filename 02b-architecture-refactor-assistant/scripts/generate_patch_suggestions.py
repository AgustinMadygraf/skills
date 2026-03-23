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


def suggested_pattern(rule: str) -> tuple[str, str]:
    mapping: dict[str, tuple[str, str]] = {
        "use_cases_imports_infrastructure": (
            "Use case importando implementacion concreta de infraestructura.",
            "Reemplazar por puerto/gateway abstracto e inyectar implementacion en composition root.",
        ),
        "presenters_imports_controllers": (
            "Presenter acoplado a controller.",
            "Mover tipos compartidos a DTO/use_case output y eliminar import hacia controllers.",
        ),
        "infrastructure_imports_presenters": (
            "Infraestructura importando presenter.",
            "Retornar datos neutros en infraestructura y mapear a presenter en adapter/controller.",
        ),
        "infrastructure_imports_controllers": (
            "Infraestructura importando controller.",
            "Mover wiring hacia controller/composition root; infraestructura no conoce entrada.",
        ),
        "vendor_import_outside_infrastructure": (
            "Vendor import fuera de infraestructura.",
            "Encapsular vendor en src/infrastructure/* y exponer interfaz interna estable.",
        ),
    }
    return mapping.get(
        rule,
        (
            "Acoplamiento de capas detectado.",
            "Aplicar inversion de dependencias y mover detalle hacia adapters/infrastructure.",
        ),
    )


def render_patch_block(file_path: str, rule: str, line: str) -> str:
    problem, target = suggested_pattern(rule)
    return (
        "```diff\n"
        f"# file: {file_path}\n"
        f"# line: {line}\n"
        f"# rule: {rule}\n"
        f"# problem: {problem}\n"
        f"# target: {target}\n"
        "- from src.infrastructure.<impl> import <ConcreteDependency>\n"
        "+ from src.interface_adapters.gateways.<port_file> import <PortInterface>\n"
        "```\n"
    )


def write_suggestions(repo_root: Path, findings: list[dict[str, str]]) -> Path:
    out = repo_root / "docs" / "refactor" / "architecture-patch-suggestions.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    by_rule: dict[str, list[dict[str, str]]] = defaultdict(list)
    for f in findings:
        by_rule[f["rule"]].append(f)

    lines: list[str] = []
    lines.append("# Architecture Patch Suggestions")
    lines.append("")
    lines.append("Documento de propuestas de patch (no aplicadas automaticamente).")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Hallazgos layer-boundary: {len(findings)}")
    lines.append(f"- Reglas afectadas: {len(by_rule)}")
    lines.append("")
    lines.append("## Propuestas")
    lines.append("")

    if not findings:
        lines.append("Sin hallazgos para sugerir patch.")
    else:
        for idx, f in enumerate(
            sorted(findings, key=lambda x: (x["severity"] != "critical", x["rule"], x["file"], int(x["line"]))),
            start=1,
        ):
            problem, target = suggested_pattern(f["rule"])
            lines.append(f"### Suggestion {idx}: `{f['rule']}`")
            lines.append("")
            lines.append(f"- Severidad: `{f['severity']}`")
            lines.append(f"- Ubicacion: `{f['file']}:{f['line']}`")
            lines.append(f"- Problema: {problem}")
            lines.append(f"- Direccion de cambio: {target}")
            lines.append("")
            lines.append("Patch sugerido (plantilla):")
            lines.append("")
            lines.append(render_patch_block(f["file"], f["rule"], f["line"]).rstrip())
            lines.append("")

    lines.append("## Checklist de aplicacion")
    lines.append("")
    lines.append("- [ ] Ajustar imports y contratos segun propuesta")
    lines.append("- [ ] Revisar wiring/composition root")
    lines.append("- [ ] Ejecutar `01-project-structure-gate`")
    lines.append("- [ ] Ejecutar `02a-project-architecture-gate`")
    lines.append("- [ ] Actualizar `docs/todo.md`")
    lines.append("")

    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate architecture patch suggestions from docs/todo.md")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--todo", default="docs/todo.md", help="Todo file path")
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    todo_path = (repo_root / args.todo).resolve()
    findings = parse_todo(todo_path)
    output = write_suggestions(repo_root, findings)
    summary = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        "output_path": str(output),
        "layer_findings_total": len(findings),
        "ok": True,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(f"SUGGESTIONS={output}")
        print(f"LAYER_FINDINGS={len(findings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

