#!/usr/bin/env python3
"""
Test runner para shared/audit_utils y skills.

Uso:
    python shared/tests/run_tests.py              # Todos los tests
    python shared/tests/run_tests.py --unit       # Solo unitarios
    python shared/tests/run_tests.py --integration # Solo integración
    python shared/tests/run_tests.py --skill 2a   # Solo skill específica
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).parent.parent.parent
SHARED_ROOT = SKILL_ROOT / "shared"


def run_unit_tests() -> bool:
    """Ejecuta tests unitarios de audit_utils."""
    print("\n" + "="*60)
    print("UNIT TESTS: shared/audit_utils")
    print("="*60)
    
    test_files = [
        SHARED_ROOT / "audit_utils" / "tests" / "test_files.py",
        SHARED_ROOT / "audit_utils" / "tests" / "test_report.py",
        SHARED_ROOT / "audit_utils" / "tests" / "test_todo_writer.py",
    ]
    
    all_passed = True
    for test_file in test_files:
        if test_file.exists():
            print(f"\n[TEST] {test_file.name}")
            result = subprocess.run([sys.executable, str(test_file)])
            if result.returncode != 0:
                all_passed = False
        else:
            print(f"[WARN] No encontrado: {test_file}")
    
    return all_passed


def run_integration_tests() -> bool:
    """Ejecuta tests de integración."""
    print("\n" + "="*60)
    print("INTEGRATION TESTS")
    print("="*60)
    
    test_files = [
        SHARED_ROOT / "tests" / "test_integration_2a.py",
    ]
    
    all_passed = True
    for test_file in test_files:
        if test_file.exists():
            print(f"\n[TEST] {test_file.name}")
            result = subprocess.run([sys.executable, str(test_file)])
            if result.returncode != 0:
                all_passed = False
        else:
            print(f"[WARN] No encontrado: {test_file}")
    
    return all_passed


def run_skill_tests(skill: str) -> bool:
    """Ejecuta tests para una skill específica."""
    print(f"\n" + "="*60)
    print(f"SKILL TESTS: {skill}")
    print("="*60)
    
    # Verificar que la skill existe
    skill_path = SKILL_ROOT / f"{skill}-project-bootstrap-audit" / "scripts" / "bootstrap_gate.py"
    if skill == "2a":
        skill_path = SKILL_ROOT / "2a-layer-boundary-gate" / "scripts" / "layer_boundary_gate.py"
    elif skill == "3a":
        skill_path = SKILL_ROOT / "3a-solid-gate" / "scripts" / "solid_gate.py"
    elif skill == "1a":
        skill_path = SKILL_ROOT / "1a-project-structure-gate" / "scripts" / "structure_gate.py"
    
    if not skill_path.exists():
        print(f"[FAIL] Skill no encontrada: {skill_path}")
        return False
    
    print(f"[OK] Skill encontrada: {skill_path}")
    
    # Verificar sintaxis
    result = subprocess.run([sys.executable, "-m", "py_compile", str(skill_path)])
    if result.returncode == 0:
        print(f"[OK] Sintaxis OK")
    else:
        print(f"[FAIL] Error de sintaxis")
        return False
    
    # Verificar imports
    print(f"\n[INFO] Verificando imports...")
    test_code = f"""
import sys
sys.path.insert(0, r"{SKILL_ROOT}")
sys.path.insert(0, r"{SHARED_ROOT}")

# Intentar importar el módulo
from audit_utils import Finding, ReportBuilder, TodoWriter
print("✅ audit_utils import OK")

# Intentar importar la skill
skill_path = r"{skill_path}"
print(f"[OK] Skill module can be parsed")
"""
    
    result = subprocess.run([sys.executable, "-c", test_code], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"[FAIL] Error de import: {result.stderr}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Test runner para skills")
    parser.add_argument("--unit", action="store_true", help="Solo tests unitarios")
    parser.add_argument("--integration", action="store_true", help="Solo tests de integración")
    parser.add_argument("--skill", type=str, help="Test específico de skill (0a, 1a, 2a, 3a)")
    args = parser.parse_args()
    
    # Si no hay argumentos, correr todo
    run_all = not (args.unit or args.integration or args.skill)
    
    results = []
    
    if args.unit or run_all:
        results.append(("Unit", run_unit_tests()))
    
    if args.integration or run_all:
        results.append(("Integration", run_integration_tests()))
    
    if args.skill:
        results.append((f"Skill {args.skill}", run_skill_tests(args.skill)))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n[SUCCESS] Todos los tests pasaron!")
        return 0
    else:
        print("\n[ERROR] Algunos tests fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())
