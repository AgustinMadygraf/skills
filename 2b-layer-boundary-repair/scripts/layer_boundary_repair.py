#!/usr/bin/env python3
"""
Path: 2b-layer-boundary-repair/scripts/layer_boundary_repair.py
Layer Boundary Repair - Aplica fixes mecanicos para fronteras entre capas.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

TODO_START = "<!-- 2b-layer-boundary-repair:auto:start -->"
TODO_END = "<!-- 2b-layer-boundary-repair:auto:end -->"


def apply_mechanical_repairs(repo_root: Path, apply_changes: bool) -> List[Dict[str, str]]:
    """Aplica reparaciones mecanicas de bajo riesgo."""
    actions: List[Dict[str, str]] = []
    src_root = repo_root / "src"
    
    if not src_root.exists():
        actions.append({
            "action": "skip",
            "target": "src/",
            "status": "skipped",
            "reason": "src/ no existe",
        })
        return actions
    
    # Verificar directorios de capas
    layers = ["entities", "use_cases", "interface_adapters", "infrastructure"]
    
    for layer in layers:
        layer_path = src_root / layer
        if not layer_path.exists():
            actions.append({
                "action": "create_dir",
                "target": f"src/{layer}",
                "status": "fixed" if apply_changes else "would_fix",
            })
            if apply_changes:
                layer_path.mkdir(parents=True, exist_ok=True)
        
        init_file = layer_path / "__init__.py"
        if layer_path.exists() and not init_file.exists():
            actions.append({
                "action": "create_file",
                "target": f"src/{layer}/__init__.py",
                "status": "fixed" if apply_changes else "would_fix",
            })
            if apply_changes:
                init_file.write_text("", encoding="utf-8", newline="\n")
    
    # Verificar subdirectorios de interface_adapters
    ia_root = src_root / "interface_adapters"
    if ia_root.exists():
        ia_subdirs = ["gateways", "controllers", "presenters"]
        for subdir in ia_subdirs:
            subdir_path = ia_root / subdir
            if not subdir_path.exists():
                actions.append({
                    "action": "create_dir",
                    "target": f"src/interface_adapters/{subdir}",
                    "status": "fixed" if apply_changes else "would_fix",
                })
                if apply_changes:
                    subdir_path.mkdir(parents=True, exist_ok=True)
            
            init_file = subdir_path / "__init__.py"
            if subdir_path.exists() and not init_file.exists():
                actions.append({
                    "action": "create_file",
                    "target": f"src/interface_adapters/{subdir}/__init__.py",
                    "status": "fixed" if apply_changes else "would_fix",
                })
                if apply_changes:
                    init_file.write_text("", encoding="utf-8", newline="\n")
    
    if not actions:
        actions.append({
            "action": "no_changes_needed",
            "target": "-",
            "status": "skipped",
        })
    
    return actions


def update_todo(repo_root: Path, actions: List[Dict[str, str]], apply_changes: bool) -> Path:
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    todo = docs / "todo.md"
    
    lines = [
        TODO_START,
        "## 2b-Layer Boundary Repair (autogenerado)",
        "",
        f"- Modo: `{'apply' if apply_changes else 'dry-run'}`",
        "- Acciones:",
    ]
    
    for action in actions:
        lines.append(f"  - `{action['status']}` `{action['action']}` en `{action['target']}`.")
    
    lines.append("")
    lines.append("- Nota: Los hallazgos de layer-boundary deben resolverse manualmente.")
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
    parser = argparse.ArgumentParser(description="Layer boundary repair")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--apply", action="store_true", help="Apply deterministic repairs")
    parser.add_argument("--json", action="store_true", help="Print json summary")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    actions = apply_mechanical_repairs(repo_root, args.apply)
    todo_path = update_todo(repo_root, actions, args.apply)
    
    out = {
        "repo_root": str(repo_root),
        "todo_path": str(todo_path),
        "mode": "apply" if args.apply else "dry-run",
        "actions": actions,
    }
    
    if args.json:
        import json
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"2B_LAYER_BOUNDARY_REPAIR={'OK'}")
        print(f"TODO={todo_path}")
        print(f"ACTIONS={len(actions)}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
