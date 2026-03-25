"""
Tests para audit_utils/todo_writer.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from audit_utils.report import Finding
from audit_utils.todo_writer import TodoWriter


def test_todo_writer_initialization():
    """TodoWriter se inicializa correctamente."""
    with tempfile.TemporaryDirectory() as tmp:
        writer = TodoWriter(Path(tmp), "test-skill")
        assert writer.skill_name == "test-skill"
        assert writer.marker_start == "<!-- test-skill:auto:start -->"
        assert writer.marker_end == "<!-- test-skill:auto:end -->"


def test_todo_writer_creates_docs_dir():
    """TodoWriter crea docs/ si no existe."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        writer = TodoWriter(tmp_path, "test")
        writer.write_findings([])
        assert (tmp_path / "docs").exists()


def test_todo_writer_creates_new_file():
    """TodoWriter crea todo.md si no existe."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        writer = TodoWriter(tmp_path, "test")
        result = writer.write_findings([])
        assert result.exists()
        assert "# TODO" in result.read_text()


def test_todo_writer_empty_findings():
    """TodoWriter escribe mensaje cuando no hay hallazgos."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        writer = TodoWriter(tmp_path, "test")
        writer.write_findings([], empty_message="No issues found")
        content = (tmp_path / "docs" / "todo.md").read_text()
        assert "No issues found" in content


def test_todo_writer_with_findings():
    """TodoWriter escribe hallazgos correctamente."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        writer = TodoWriter(tmp_path, "test")
        findings = [Finding("critical", "rule", "file.py", 10, "detail")]
        writer.write_findings(findings)
        content = (tmp_path / "docs" / "todo.md").read_text()
        assert "[test:critical]" in content
        assert "rule" in content
        assert "file.py:10" in content


def test_todo_writer_updates_existing_section():
    """TodoWriter actualiza sección existente."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        writer = TodoWriter(tmp_path, "test")
        
        # Primera escritura
        writer.write_findings([Finding("critical", "old", "f.py", 1, "d")])
        
        # Segunda escritura (debe reemplazar)
        writer.write_findings([Finding("warning", "new", "f.py", 2, "d")])
        
        content = (tmp_path / "docs" / "todo.md").read_text()
        # Debe tener solo el nuevo
        assert "new" in content
        # El viejo no debe estar
        assert content.count("old") == 0


def test_todo_writer_multiple_skills():
    """Múltiples skills pueden escribir en el mismo todo.md."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        
        writer1 = TodoWriter(tmp_path, "skill-1")
        writer1.write_findings([Finding("critical", "r1", "f.py", 1, "d")])
        
        writer2 = TodoWriter(tmp_path, "skill-2")
        writer2.write_findings([Finding("warning", "r2", "f.py", 2, "d")])
        
        content = (tmp_path / "docs" / "todo.md").read_text()
        # Ambas secciones deben estar
        assert "skill-1:critical" in content
        assert "skill-2:warning" in content


def test_todo_writer_clear_section():
    """TodoWriter.clear_section limpia la sección."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        writer = TodoWriter(tmp_path, "test")
        
        # Escribir algo
        writer.write_findings([Finding("critical", "rule", "f.py", 1, "d")])
        
        # Limpiar
        writer.clear_section()
        
        content = (tmp_path / "docs" / "todo.md").read_text()
        assert "Sin hallazgos pendientes" in content


if __name__ == "__main__":
    import tempfile
    import traceback
    
    tests = [
        test_todo_writer_initialization,
        test_todo_writer_creates_docs_dir,
        test_todo_writer_creates_new_file,
        test_todo_writer_empty_findings,
        test_todo_writer_with_findings,
        test_todo_writer_updates_existing_section,
        test_todo_writer_multiple_skills,
        test_todo_writer_clear_section,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"[PASS] {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
