"""
Tests para audit_utils/files.py
"""
from __future__ import annotations

import ast
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from audit_utils.files import parse_ast, py_files, relative_to_repo, src_dirs


def test_py_files_empty_dir():
    """py_files retorna lista vacía para directorio inexistente."""
    with tempfile.TemporaryDirectory() as tmp:
        result = py_files(Path(tmp) / "nonexistent")
        assert result == []


def test_py_files_finds_python_files():
    """py_files encuentra archivos .py."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "test1.py").write_text("x = 1")
        (tmp_path / "test2.py").write_text("y = 2")
        (tmp_path / "not_python.txt").write_text("text")
        
        result = py_files(tmp_path)
        assert len(result) == 2
        assert all(f.suffix == ".py" for f in result)


def test_py_files_excludes_init_by_default():
    """py_files excluye __init__.py por defecto."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "module.py").write_text("x = 1")
        
        result = py_files(tmp_path, exclude_init=True)
        assert len(result) == 1
        assert result[0].name == "module.py"


def test_py_files_includes_init_when_requested():
    """py_files incluye __init__.py cuando exclude_init=False."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "module.py").write_text("x = 1")
        
        result = py_files(tmp_path, exclude_init=False)
        assert len(result) == 2


def test_src_dirs_empty_when_no_src():
    """src_dirs retorna lista vacía si no existe src/."""
    with tempfile.TemporaryDirectory() as tmp:
        result = src_dirs(Path(tmp))
        assert result == []


def test_src_dirs_finds_directories():
    """src_dirs encuentra todos los directorios bajo src/."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "src" / "entities").mkdir(parents=True)
        (tmp_path / "src" / "use_cases" / "sub").mkdir(parents=True)
        
        result = src_dirs(tmp_path)
        assert len(result) == 4  # src/, entities/, use_cases/, sub/


def test_parse_ast_valid_file():
    """parse_ast retorna AST para archivo válido."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1\n")
        
        result = parse_ast(test_file)
        assert isinstance(result, ast.AST)


def test_parse_ast_syntax_error():
    """parse_ast retorna None para archivo con error de sintaxis."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_file = tmp_path / "test.py"
        test_file.write_text("def broken(\n")  # Syntax error
        
        result = parse_ast(test_file)
        assert result is None


def test_parse_ast_nonexistent():
    """parse_ast maneja archivo inexistente."""
    result = parse_ast(Path("/nonexistent/file.py"))
    assert result is None


def test_relative_to_repo_with_forward_slashes():
    """relative_to_repo usa forward slashes."""
    repo = Path("/repo")
    file = Path("/repo/src/entities/user.py")
    
    result = relative_to_repo(file, repo)
    assert "/" in result
    assert "\\" not in result
    assert result == "src/entities/user.py"


def test_relative_to_repo_already_relative():
    """relative_to_repo maneja rutas ya relativas."""
    repo = Path("/repo")
    file = Path("src/entities/user.py")
    
    result = relative_to_repo(file, repo)
    assert result == "src/entities/user.py"


if __name__ == "__main__":
    # Run tests
    import traceback
    
    tests = [
        test_py_files_empty_dir,
        test_py_files_finds_python_files,
        test_py_files_excludes_init_by_default,
        test_py_files_includes_init_when_requested,
        test_src_dirs_empty_when_no_src,
        test_src_dirs_finds_directories,
        test_parse_ast_valid_file,
        test_parse_ast_syntax_error,
        test_parse_ast_nonexistent,
        test_relative_to_repo_with_forward_slashes,
        test_relative_to_repo_already_relative,
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
