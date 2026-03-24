#!/usr/bin/env python3
"""
Path: 3b-solid-refactor-assistant/scripts/analyze_class_solid.py
Analiza una clase especifica segun principios SOLID.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Dict, List


def analyze_class_solid(file_path: Path, class_name: str) -> Dict:
    """Analiza una clase segun SOLID."""
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    tree = ast.parse(file_path.read_text(encoding="utf-8", errors="ignore"))
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return analyze_class_node(node)
    
    return {"error": f"Class {class_name} not found in {file_path}"}


def analyze_class_node(cls: ast.ClassDef) -> Dict:
    """Analiza un nodo de clase AST."""
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
    public_methods = [m for m in methods if not m.name.startswith("_")]
    private_methods = [m for m in methods if m.name.startswith("_")]
    
    # Contar lineas aproximadas
    lines = cls.end_lineno - cls.lineno if cls.end_lineno else 0
    
    # Detectar dependencias (atributos asignados en __init__)
    dependencies = []
    init_method = next((m for m in methods if m.name == "__init__"), None)
    if init_method:
        for stmt in init_method.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                        if target.value.id == "self":
                            dependencies.append(target.attr)
    
    analysis = {
        "class_name": cls.name,
        "line_number": cls.lineno,
        "metrics": {
            "total_methods": len(methods),
            "public_methods": len(public_methods),
            "private_methods": len(private_methods),
            "approx_lines": lines,
        },
        "dependencies": dependencies,
        "public_method_names": [m.name for m in public_methods],
        "solid_assessment": {
            "srp": assess_srp(lines, len(public_methods)),
            "isp": assess_isp(len(public_methods)),
            "dip": assess_dip(dependencies),
        },
    }
    
    return analysis


def assess_srp(lines: int, public_methods: int) -> Dict:
    """Evalua SRP (Single Responsibility Principle)."""
    concerns = []
    if lines > 200:
        concerns.append("Clase muy larga (>200 lineas)")
    if public_methods > 15:
        concerns.append("Demasiados metodos publicos (>15)")
    
    return {
        "compliant": len(concerns) == 0,
        "concerns": concerns,
        "recommendation": "Considerar extraer responsabilidades" if concerns else "OK",
    }


def assess_isp(public_methods: int) -> Dict:
    """Evalua ISP (Interface Segregation Principle)."""
    concerns = []
    if public_methods > 10:
        concerns.append("Interfaz muy grande (>10 metodos publicos)")
    
    return {
        "compliant": len(concerns) == 0,
        "concerns": concerns,
        "recommendation": "Considerar dividir interfaz" if concerns else "OK",
    }


def assess_dip(dependencies: List[str]) -> Dict:
    """Evalua DIP (Dependency Inversion Principle)."""
    concrete_patterns = ["db", "database", "conn", "connection", "client", "api"]
    suspicious = [d for d in dependencies if any(p in d.lower() for p in concrete_patterns)]
    
    return {
        "compliant": len(suspicious) == 0,
        "dependencies": dependencies,
        "suspicious_concrete": suspicious,
        "recommendation": "Verificar si dependencias son concretas" if suspicious else "OK",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze class SOLID compliance")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--file", required=True, help="Python file path relative to repo root")
    parser.add_argument("--class", dest="class_name", required=True, help="Class name to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    file_path = repo_root / args.file
    
    result = analyze_class_solid(file_path, args.class_name)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"CLASS_ANALYSIS={result.get('class_name', 'ERROR')}")
        if "error" in result:
            print(f"ERROR={result['error']}")
            return 1
        
        metrics = result.get("metrics", {})
        print(f"METRICS=methods:{metrics.get('total_methods')}, public:{metrics.get('public_methods')}")
        
        assessment = result.get("solid_assessment", {})
        for principle, data in assessment.items():
            status = "OK" if data.get("compliant") else "VIOLATION"
            print(f"{principle.upper()}={status}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
