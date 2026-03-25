"""
Test de integración para 2a-layer-boundary-gate.

Crea un proyecto temporal y verifica que la skill detecta violaciones correctamente.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def create_test_project(tmp_path: Path, with_violations: bool = True) -> Path:
    """Crea un proyecto de prueba."""
    # Estructura base
    (tmp_path / "src" / "entities").mkdir(parents=True)
    (tmp_path / "src" / "use_cases").mkdir(parents=True)
    (tmp_path / "src" / "interface_adapters" / "presenters").mkdir(parents=True)
    (tmp_path / "src" / "interface_adapters" / "controllers").mkdir(parents=True)
    (tmp_path / "src" / "infrastructure").mkdir(parents=True)
    
    if with_violations:
        # Crear violación: use_cases importando infrastructure
        (tmp_path / "src" / "use_cases" / "business_logic.py").write_text('''
"""Path: src/use_cases/business_logic.py"""
from src.infrastructure.database import get_session

def process_data():
    session = get_session()
    return session.query()
''')
        
        # Crear violación: presenters importando controllers
        (tmp_path / "src" / "interface_adapters" / "presenters" / "json_presenter.py").write_text('''
"""Path: src/interface_adapters/presenters/json_presenter.py"""
from src.interface_adapters.controllers.base import BaseController

def present(data):
    return BaseController.format(data)
''')
    else:
        # Código válido
        (tmp_path / "src" / "use_cases" / "business_logic.py").write_text('''
"""Path: src/use_cases/business_logic.py"""
from src.entities.user import User

def process_data():
    return User()
''')
    
    return tmp_path


def test_2a_detects_violations():
    """2a detecta violaciones de layer-boundary."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        create_test_project(tmp_path, with_violations=True)
        
        result = subprocess.run(
            [sys.executable, "-m", "2a-layer-boundary-gate.scripts.layer_boundary_gate",
             "--repo-root", str(tmp_path), "--json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode != 0, "Debe fallar con violaciones"
        
        import json
        output = json.loads(result.stdout)
        assert output["ok"] is False
        assert output["critical_total"] >= 2  # Dos violaciones
        
        # Verificar que detectó las reglas específicas
        findings = output.get("findings", [])
        rules = [f["rule"] for f in findings]
        assert "use_cases_imports_infrastructure" in rules
        assert "presenters_imports_controllers" in rules
        
        print(f"[PASS] Detectó {len(findings)} violaciones")


def test_2a_passes_with_valid_code():
    """2a pasa cuando no hay violaciones."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        create_test_project(tmp_path, with_violations=False)
        
        result = subprocess.run(
            [sys.executable, "-m", "2a-layer-boundary-gate.scripts.layer_boundary_gate",
             "--repo-root", str(tmp_path), "--json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0, f"Debe pasar sin violaciones. stderr: {result.stderr}"
        
        import json
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert output["critical_total"] == 0
        
        print("[PASS] Pasa correctamente sin violaciones")


def test_2a_writes_todo():
    """2a escribe en docs/todo.md."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        create_test_project(tmp_path, with_violations=True)
        
        result = subprocess.run(
            [sys.executable, "-m", "2a-layer-boundary-gate.scripts.layer_boundary_gate",
             "--repo-root", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        todo_path = tmp_path / "docs" / "todo.md"
        assert todo_path.exists(), "Debe crear docs/todo.md"
        
        content = todo_path.read_text()
        assert "2a-layer-boundary-gate" in content
        assert "use_cases_imports_infrastructure" in content
        
        print("[PASS] Escribe docs/todo.md correctamente")


if __name__ == "__main__":
    import traceback
    
    tests = [
        test_2a_detects_violations,
        test_2a_passes_with_valid_code,
        test_2a_writes_todo,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
