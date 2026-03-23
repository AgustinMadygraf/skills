#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Dict


DIRS = [
    "src/entities",
    "src/use_cases",
    "src/interface_adapters/presenters",
    "src/interface_adapters/gateways",
    "src/infrastructure",
    "src/infrastructure/settings",
    "docs",
    "tests",
]

REQUIRED_FILES = [
    "run.py",
    "README.md",
    ".gitignore",
    ".env",
    ".env.example",
    "src/infrastructure/settings/logger.py",
    "src/infrastructure/settings/config.py",
]

GITKEEP_DIRS = [
    "src/entities",
    "src/use_cases",
    "src/interface_adapters/presenters",
    "src/interface_adapters/gateways",
    "docs",
    "tests",
]

FORBIDDEN_PATHS = [
    "src/cli.py",
    "src/infrastructure/config.py",
]


KEY_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
SENSITIVE_KEY_RE = re.compile(
    r"(SECRET|TOKEN|PASSWORD|PRIVATE|API[_-]?KEY|ACCESS[_-]?KEY|CLIENT[_-]?SECRET|DATABASE_URL|DB_URL)",
    re.IGNORECASE,
)
VENDOR_DB_IMPORT_PREFIXES = (
    "sqlite3",
    "pymysql",
    "sqlalchemy",
    "aiosqlite",
)
VENDOR_APP_IMPORT_PREFIXES = (
    "requests",
    "httpx",
    "fastapi",
    "flask",
    "pydantic",
)
DEFAULT_SOLID_THRESHOLDS = {
    "max_use_case_classes_per_module": 1,
    "max_use_case_top_level_functions": 3,
    "max_gateway_public_methods": 7,
    "max_public_methods_per_class": 10,
}


def infer_project_name(repo_root: Path) -> str:
    readme = repo_root / "README.md"
    if readme.exists():
        for raw in readme.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line.startswith("# "):
                return line[2:].strip()
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        for raw in pyproject.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line.startswith("name") and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return repo_root.name


def infer_runtime_command(repo_root: Path) -> str:
    if (repo_root / "run.py").exists():
        return "python run.py"
    return ""


def resolve_context_field(
    explicit_value: str | None,
    inferred_value: str,
    fallback: str,
) -> str:
    if explicit_value and explicit_value.strip():
        return explicit_value.strip()
    if inferred_value and inferred_value.strip():
        return inferred_value.strip()
    return fallback


def write_if_missing(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def validate_layout_policy(repo_root: Path) -> Dict[str, object]:
    missing_dirs = [d for d in DIRS if not (repo_root / d).is_dir()]
    missing_files = [f for f in REQUIRED_FILES if not (repo_root / f).is_file()]
    forbidden_existing = [p for p in FORBIDDEN_PATHS if (repo_root / p).exists()]
    gitignore_has_tmp = False
    gitignore_path = repo_root / ".gitignore"
    if gitignore_path.exists():
        for raw in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if raw.strip() == ".tmp/":
                gitignore_has_tmp = True
                break

    missing_gitkeep = [d for d in GITKEEP_DIRS if not (repo_root / d / ".gitkeep").is_file()]
    infra_gitkeeps = [
        str(p.relative_to(repo_root))
        for p in (repo_root / "src" / "infrastructure").rglob(".gitkeep")
    ] if (repo_root / "src" / "infrastructure").exists() else []

    violations: list[str] = []
    for d in missing_dirs:
        violations.append(f"missing_dir:{d}")
    for f in missing_files:
        violations.append(f"missing_file:{f}")
    for p in forbidden_existing:
        violations.append(f"forbidden_path_present:{p}")
    for d in missing_gitkeep:
        violations.append(f"missing_gitkeep:{d}/.gitkeep")
    for g in infra_gitkeeps:
        violations.append(f"forbidden_gitkeep_in_infrastructure:{g}")
    if not gitignore_has_tmp:
        violations.append("gitignore_missing_pattern:.tmp/")

    return {
        "ok": len(violations) == 0,
        "missing_dirs": missing_dirs,
        "missing_files": missing_files,
        "forbidden_existing": forbidden_existing,
        "gitignore_has_tmp": gitignore_has_tmp,
        "missing_gitkeep": missing_gitkeep,
        "forbidden_gitkeep_in_infrastructure": infra_gitkeeps,
        "violations": violations,
    }


def src_dirs(repo_root: Path) -> list[Path]:
    root = repo_root / "src"
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*") if p.is_dir()] + [root])


def py_files_under_src(repo_root: Path) -> list[Path]:
    root = repo_root / "src"
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*.py") if p.is_file()])


def ensure_init_files(repo_root: Path, force: bool, check_mode: bool) -> tuple[list[str], list[str]]:
    created: list[str] = []
    missing: list[str] = []
    for d in src_dirs(repo_root):
        init_path = d / "__init__.py"
        rel = str(init_path.relative_to(repo_root))
        if init_path.exists():
            continue
        if check_mode:
            missing.append(rel)
        else:
            if write_if_missing(init_path, "", force):
                created.append(rel)
    return created, missing


def validate_init_empty(repo_root: Path) -> list[str]:
    violations: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name != "__init__.py":
            continue
        if path.read_text(encoding="utf-8", errors="ignore").strip() != "":
            violations.append(str(path.relative_to(repo_root)))
    return violations


def normalize_init_files(repo_root: Path) -> list[str]:
    fixed: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name != "__init__.py":
            continue
        if path.read_text(encoding="utf-8", errors="ignore").strip() == "":
            continue
        path.write_text("", encoding="utf-8", newline="\n")
        fixed.append(str(path.relative_to(repo_root)))
    return fixed


def ensure_path_docstring_for_file(path: Path, rel: str) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = text.replace("\ufeff", "")
    text = text.replace("ï»¿", "")
    expected = f'"""\nPath: {rel}\n"""'

    def strip_one_leading_docstring(payload: str) -> tuple[str, str]:
        s = payload.lstrip()
        if not (s.startswith('"""') or s.startswith("'''")):
            return payload, ""
        quote = s[:3]
        end = s.find(quote, 3)
        if end == -1:
            return payload, ""
        header = s[3:end]
        remainder = s[end + 3 :]
        return remainder, header

    remainder, _first_header = strip_one_leading_docstring(text)
    if remainder == text:
        remainder = text
    # If a second leading docstring exists and looks like another Path header, drop it too.
    rem2, second_header = strip_one_leading_docstring(remainder)
    if rem2 != remainder and "Path:" in second_header:
        remainder = rem2

    new_text = expected + "\n\n" + remainder.lstrip("\n")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8", newline="\n")
        return True
    return False


def normalize_path_docstrings(repo_root: Path) -> list[str]:
    fixed: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        if ensure_path_docstring_for_file(path, rel):
            fixed.append(str(path.relative_to(repo_root)))
    return fixed


def validate_path_docstring(repo_root: Path) -> list[str]:
    violations: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="ignore").lstrip()
        if not (text.startswith('"""') or text.startswith("'''")):
            violations.append(f"{rel}:missing_path_docstring")
            continue
        quote = text[:3]
        end = text.find(quote, 3)
        if end == -1:
            violations.append(f"{rel}:unclosed_docstring")
            continue
        header = text[3:end]
        if f"Path: {rel}" not in header:
            violations.append(f"{rel}:path_mismatch")
    return violations


def import_rank(line: str) -> int:
    s = line.strip()
    if s.startswith("from src.infrastructure"):
        return 1
    if s.startswith("from src.interface_adapters"):
        return 2
    if s.startswith("from src.use_cases"):
        return 3
    if s.startswith("from src.entities"):
        return 4
    if s.startswith("from src.") or s.startswith("import src."):
        return 5
    return 0


def validate_import_order(repo_root: Path) -> list[str]:
    violations: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        import_lines = []
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            if s.startswith("import ") or s.startswith("from "):
                import_lines.append(s)
        ranks = [import_rank(x) for x in import_lines]
        if any(r == 5 for r in ranks):
            violations.append(f"{rel}:unknown_src_import_group")
            continue
        if any(ranks[i] > ranks[i + 1] for i in range(len(ranks) - 1)):
            violations.append(f"{rel}:import_order_invalid")
    return violations


def normalize_import_order_for_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore").replace("\ufeff", "")
    text = text.replace("ï»¿", "")
    lines = text.splitlines()
    if not lines:
        return False

    i = 0
    first = lines[0].lstrip("\ufeff") if lines else ""
    if lines and first.startswith('"""'):
        if lines[0].count('"""') >= 2:
            i = 1
        else:
            i = 1
            while i < len(lines):
                if '"""' in lines[i]:
                    i += 1
                    break
                i += 1
    elif lines and first.startswith("'''"):
        if lines[0].count("'''") >= 2:
            i = 1
        else:
            i = 1
            while i < len(lines):
                if "'''" in lines[i]:
                    i += 1
                    break
                i += 1

    while i < len(lines) and (lines[i].strip() == "" or lines[i].strip().startswith("#")):
        i += 1
    start = i

    block: list[str] = []
    while i < len(lines):
        s = lines[i].strip()
        if s == "" or s.startswith("#") or s.startswith("import ") or s.startswith("from "):
            block.append(lines[i])
            i += 1
            continue
        break
    end = i

    import_lines = [ln.strip() for ln in block if ln.strip().startswith("import ") or ln.strip().startswith("from ")]
    if len(import_lines) <= 1:
        return False
    if any(import_rank(x) == 5 for x in import_lines):
        return False

    sorted_imports = sorted(import_lines, key=lambda x: (import_rank(x), x))
    current_imports = [ln.strip() for ln in block if ln.strip().startswith("import ") or ln.strip().startswith("from ")]
    if current_imports == sorted_imports:
        return False

    new_block = sorted_imports + [""]
    new_lines = lines[:start] + new_block + lines[end:]
    path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return True


def normalize_import_order(repo_root: Path) -> list[str]:
    fixed: list[str] = []
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        if normalize_import_order_for_file(path):
            fixed.append(str(path.relative_to(repo_root)))
    return fixed


def validate_no_dataclass(repo_root: Path) -> list[str]:
    violations: list[str] = []
    for path in py_files_under_src(repo_root):
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "from dataclasses import dataclass" in text:
            violations.append(f"{rel}:forbidden_dataclass_import")
            continue
        if "@dataclass" in text:
            violations.append(f"{rel}:forbidden_dataclass_decorator")
            continue
    return violations


def extract_import_lines(path: Path) -> list[tuple[int, str]]:
    imports: list[tuple[int, str]] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        line = raw.strip()
        if line.startswith("import ") or line.startswith("from "):
            imports.append((i, line))
    return imports


def imported_module(line: str) -> str:
    s = line.strip()
    if s.startswith("import "):
        return s[len("import ") :].split(" as ", 1)[0].strip().split(",", 1)[0].strip()
    if s.startswith("from "):
        return s[len("from ") :].split(" import ", 1)[0].strip()
    return ""


def validate_layer_boundary(repo_root: Path) -> Dict[str, object]:
    findings: list[Dict[str, object]] = []
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        imports = extract_import_lines(path)

        in_entities = rel.startswith("src/entities/")
        in_use_cases = rel.startswith("src/use_cases/")
        in_interface_adapters = rel.startswith("src/interface_adapters/")
        in_gateways = rel.startswith("src/interface_adapters/gateways/")
        in_presenters = rel.startswith("src/interface_adapters/presenters/")
        in_controllers = rel.startswith("src/interface_adapters/controllers/")
        in_infrastructure = rel.startswith("src/infrastructure/")

        for ln, imp in imports:
            module = imported_module(imp)
            if not in_infrastructure:
                if any(
                    module == p or module.startswith(f"{p}.")
                    for p in (VENDOR_DB_IMPORT_PREFIXES + VENDOR_APP_IMPORT_PREFIXES)
                ):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "vendor_import_outside_infrastructure",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
            if in_entities:
                if imp.startswith("from src.use_cases") or imp.startswith("import src.use_cases"):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "entities_imports_use_cases",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if imp.startswith("from src.interface_adapters") or imp.startswith("import src.interface_adapters"):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "entities_imports_interface_adapters",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if imp.startswith("from src.infrastructure") or imp.startswith("import src.infrastructure"):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "entities_imports_infrastructure",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
            if in_use_cases:
                if imp.startswith("from src.interface_adapters") or imp.startswith("import src.interface_adapters"):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "use_cases_imports_interface_adapters",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if imp.startswith("from src.infrastructure") or imp.startswith("import src.infrastructure"):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "use_cases_imports_infrastructure",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
            if in_interface_adapters:
                if imp.startswith("from src.infrastructure") or imp.startswith("import src.infrastructure"):
                    sev = "critical" if in_presenters else "warning"
                    findings.append(
                        {
                            "severity": sev,
                            "rule": "interface_adapters_imports_infrastructure",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if in_gateways and (
                    imp.startswith("from src.interface_adapters.presenters")
                    or imp.startswith("import src.interface_adapters.presenters")
                ):
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "gateways_imports_presenters",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if in_presenters and (
                    imp.startswith("from src.interface_adapters.gateways")
                    or imp.startswith("import src.interface_adapters.gateways")
                ):
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "presenters_imports_gateways",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if in_gateways and (
                    imp.startswith("from src.interface_adapters.controllers")
                    or imp.startswith("import src.interface_adapters.controllers")
                ):
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "gateways_imports_controllers",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if in_presenters and (
                    imp.startswith("from src.interface_adapters.controllers")
                    or imp.startswith("import src.interface_adapters.controllers")
                ):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "presenters_imports_controllers",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if in_controllers and (
                    imp.startswith("from src.interface_adapters.presenters")
                    or imp.startswith("import src.interface_adapters.presenters")
                ):
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "controllers_imports_presenters",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if in_controllers and (
                    imp.startswith("from src.interface_adapters.gateways")
                    or imp.startswith("import src.interface_adapters.gateways")
                ):
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "controllers_imports_gateways",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
            if in_infrastructure:
                if imp.startswith("from src.interface_adapters.presenters") or imp.startswith(
                    "import src.interface_adapters.presenters"
                ):
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "infrastructure_imports_presenters",
                            "file": rel,
                            "line": ln,
                            "import": imp,
                        }
                    )
                if imp.startswith("from src.interface_adapters.controllers") or imp.startswith(
                    "import src.interface_adapters.controllers"
                ):
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "infrastructure_imports_controllers",
                            "file": rel,
                            "line": ln,
                            "import": imp,
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


def load_solid_thresholds(path: Path) -> tuple[Dict[str, int], list[str], bool]:
    thresholds = dict(DEFAULT_SOLID_THRESHOLDS)
    warnings: list[str] = []
    loaded = False
    if not path.exists():
        return thresholds, warnings, loaded
    try:
        raw = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        if not isinstance(raw, dict):
            warnings.append("solid_thresholds_invalid_payload_type")
            return thresholds, warnings, loaded
        for key, default_value in DEFAULT_SOLID_THRESHOLDS.items():
            value = raw.get(key, default_value)
            if isinstance(value, int) and value >= 1:
                thresholds[key] = value
            else:
                warnings.append(f"solid_threshold_invalid:{key}")
        loaded = True
    except json.JSONDecodeError:
        warnings.append("solid_thresholds_invalid_json")
    return thresholds, warnings, loaded


def validate_solid_lite(repo_root: Path, thresholds: Dict[str, int]) -> Dict[str, object]:
    findings: list[Dict[str, object]] = []
    max_use_case_classes_per_module = thresholds["max_use_case_classes_per_module"]
    max_use_case_top_level_functions = thresholds["max_use_case_top_level_functions"]
    max_gateway_public_methods = thresholds["max_gateway_public_methods"]
    max_public_methods_per_class = thresholds["max_public_methods_per_class"]
    for path in py_files_under_src(repo_root):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except SyntaxError:
            findings.append(
                {
                    "severity": "warning",
                    "rule": "solid_lite_syntax_parse_failed",
                    "file": rel,
                    "line": 1,
                    "detail": "No se pudo analizar AST para reglas SRP/ISP.",
                }
            )
            continue

        in_use_cases = rel.startswith("src/use_cases/")
        in_gateways = rel.startswith("src/interface_adapters/gateways/")
        in_inner = rel.startswith("src/entities/") or rel.startswith("src/use_cases/")

        class_nodes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        top_level_funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]

        # SRP-lite: avoid multiple responsibilities per module in use_cases.
        if in_use_cases and len(class_nodes) > max_use_case_classes_per_module:
            findings.append(
                {
                    "severity": "warning",
                    "rule": "solid_srp_multiple_classes_use_case_module",
                    "file": rel,
                    "line": class_nodes[max_use_case_classes_per_module].lineno,
                    "detail": (
                        f"Modulo con {len(class_nodes)} clases; limite configurado="
                        f"{max_use_case_classes_per_module}."
                    ),
                }
            )
        if in_use_cases and len(top_level_funcs) > max_use_case_top_level_functions:
            findings.append(
                {
                    "severity": "warning",
                    "rule": "solid_srp_many_top_level_functions_use_case_module",
                    "file": rel,
                    "line": top_level_funcs[max_use_case_top_level_functions].lineno,
                    "detail": (
                        f"Modulo con {len(top_level_funcs)} funciones top-level; limite configurado="
                        f"{max_use_case_top_level_functions}."
                    ),
                }
            )

        for cls in class_nodes:
            public_methods = [
                n
                for n in cls.body
                if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
            ]
            # ISP-lite: gateway interfaces should stay small.
            if in_gateways and cls.name.lower().endswith(("gateway", "port", "interface", "protocol")):
                if len(public_methods) > max_gateway_public_methods:
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "solid_isp_fat_gateway_interface",
                            "file": rel,
                            "line": cls.lineno,
                            "detail": (
                                f"Interfaz {cls.name} con {len(public_methods)} metodos publicos; "
                                f"limite configurado={max_gateway_public_methods}."
                            ),
                        }
                    )
            # SRP-lite: too many public methods likely mixed responsibilities.
            if rel.startswith("src/use_cases/") or rel.startswith("src/interface_adapters/"):
                if len(public_methods) > max_public_methods_per_class:
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "solid_srp_class_many_public_methods",
                            "file": rel,
                            "line": cls.lineno,
                            "detail": (
                                f"Clase {cls.name} con {len(public_methods)} metodos publicos; "
                                f"limite configurado={max_public_methods_per_class}."
                            ),
                        }
                    )

        # DIP-lite: in inner layers, direct vendor imports are critical.
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if in_inner and any(module == p or module.startswith(f"{p}.") for p in (VENDOR_DB_IMPORT_PREFIXES + VENDOR_APP_IMPORT_PREFIXES)):
                        findings.append(
                            {
                                "severity": "critical",
                                "rule": "solid_dip_vendor_import_in_inner_layer",
                                "file": rel,
                                "line": node.lineno,
                                "detail": module,
                            }
                        )
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if in_inner and any(module == p or module.startswith(f"{p}.") for p in (VENDOR_DB_IMPORT_PREFIXES + VENDOR_APP_IMPORT_PREFIXES)):
                    findings.append(
                        {
                            "severity": "critical",
                            "rule": "solid_dip_vendor_import_in_inner_layer",
                            "file": rel,
                            "line": node.lineno,
                            "detail": module,
                        }
                    )
                if in_use_cases and module.startswith("src.interface_adapters.gateways"):
                    for alias in node.names:
                        imported = alias.name
                        if imported == "*" or imported.endswith(("Port", "Gateway", "Protocol", "Interface")):
                            continue
                        findings.append(
                            {
                                "severity": "warning",
                                "rule": "solid_dip_use_case_imports_non_port_gateway_symbol",
                                "file": rel,
                                "line": node.lineno,
                                "detail": imported,
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


def architecture_finding_key(finding: Dict[str, object]) -> str:
    return "|".join(
        [
            str(finding.get("severity", "")),
            str(finding.get("rule", "")),
            str(finding.get("file", "")),
            str(finding.get("line", "")),
        ]
    )


def load_architecture_baseline(path: Path) -> set[str]:
    if not path.exists():
        return set()
    raw = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not raw:
        return set()
    payload = json.loads(raw)
    if isinstance(payload, dict) and isinstance(payload.get("findings"), list):
        return {str(x) for x in payload["findings"]}
    if isinstance(payload, list):
        return {str(x) for x in payload}
    return set()


def save_architecture_baseline(path: Path, findings: list[Dict[str, object]]) -> None:
    keys = sorted({architecture_finding_key(x) for x in findings})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"findings": keys}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_python_policy(repo_root: Path, missing_inits: list[str]) -> Dict[str, object]:
    init_non_empty = validate_init_empty(repo_root)
    path_docstring_violations = validate_path_docstring(repo_root)
    import_order_violations = validate_import_order(repo_root)
    dataclass_violations = validate_no_dataclass(repo_root)
    violations: list[str] = []
    violations += [f"missing_init:{x}" for x in missing_inits]
    violations += [f"non_empty_init:{x}" for x in init_non_empty]
    violations += path_docstring_violations
    violations += import_order_violations
    violations += dataclass_violations
    return {
        "ok": len(violations) == 0,
        "missing_init": missing_inits,
        "non_empty_init": init_non_empty,
        "path_docstring_violations": path_docstring_violations,
        "import_order_violations": import_order_violations,
        "dataclass_violations": dataclass_violations,
        "violations": violations,
    }


def parse_env_file(path: Path) -> Dict[str, object]:
    result: Dict[str, object] = {"keys": set(), "values": {}, "invalid_lines": []}
    if not path.exists():
        return result
    keys: set[str] = set()
    values: Dict[str, str] = {}
    invalid_lines: list[str] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            invalid_lines.append(f"{path.name}:{i}:{raw}")
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not KEY_RE.match(key):
            invalid_lines.append(f"{path.name}:{i}:{raw}")
            continue
        keys.add(key)
        values[key] = value
    result["keys"] = keys
    result["values"] = values
    result["invalid_lines"] = invalid_lines
    return result


def looks_like_placeholder(value: str) -> bool:
    val = value.strip().strip('"').strip("'")
    if val == "":
        return True
    lowered = val.lower()
    if lowered in {"changeme", "change_me", "example", "sample", "dummy", "xxx", "replace_me"}:
        return True
    if lowered.startswith("<") and lowered.endswith(">"):
        return True
    if "your_" in lowered or "example" in lowered:
        return True
    return False


def detect_possible_secrets_in_example(values: Dict[str, str]) -> list[str]:
    leaks: list[str] = []
    for key, value in values.items():
        if SENSITIVE_KEY_RE.search(key) and not looks_like_placeholder(value):
            leaks.append(key)
    return sorted(leaks)


TODO_AUTOGEN_START = "<!-- project-gates:auto:start -->"
TODO_AUTOGEN_END = "<!-- project-gates:auto:end -->"
TODO_LEGACY_POLICY_START = "<!-- project-policy-gate:auto:start -->"
TODO_LEGACY_POLICY_END = "<!-- project-policy-gate:auto:end -->"
TODO_LEGACY_START = "<!-- project-initializer:auto:start -->"
TODO_LEGACY_END = "<!-- project-initializer:auto:end -->"


def build_todo_items(summary: Dict[str, object]) -> list[str]:
    items: list[str] = []
    run_structure_gate = bool(summary.get("run_structure_gate", True))
    run_architecture_gate = bool(summary.get("run_architecture_gate", True))

    if run_structure_gate and not bool(summary.get("env_policy_ok", True)):
        for key in summary.get("env_only", []):
            items.append(f"- [ ] [env-policy] Agregar `{key}` a `.env.example`.")
        for key in summary.get("env_example_only", []):
            items.append(f"- [ ] [env-policy] Agregar `{key}` a `.env`.")
        for line in summary.get("env_invalid_lines", []):
            items.append(f"- [ ] [env-policy] Corregir linea invalida: `{line}`.")
        for key in summary.get("possible_secrets_in_example", []):
            items.append(f"- [ ] [env-policy] Reemplazar secreto real por placeholder en `.env.example`: `{key}`.")

    if run_structure_gate and not bool(summary.get("layout_policy_ok", True)):
        for v in summary.get("layout_violations", []):
            items.append(f"- [ ] [layout-policy] Resolver: `{v}`.")

    if run_structure_gate and not bool(summary.get("python_policy_ok", True)):
        for v in summary.get("python_violations", []):
            items.append(f"- [ ] [python-file-policy] Resolver: `{v}`.")

    if run_architecture_gate:
        layer_details = summary.get("layer_boundary_details", {})
        findings = layer_details.get("findings", []) if isinstance(layer_details, dict) else []
        for finding in findings:
            sev = finding.get("severity", "unknown")
            rule = finding.get("rule", "unknown_rule")
            file = finding.get("file", "unknown_file")
            line = finding.get("line", "?")
            items.append(f"- [ ] [layer-boundary:{sev}] `{rule}` en `{file}:{line}`.")
        solid_details = summary.get("solid_lite_details", {})
        solid_findings = solid_details.get("findings", []) if isinstance(solid_details, dict) else []
        for finding in solid_findings:
            sev = finding.get("severity", "unknown")
            rule = finding.get("rule", "unknown_rule")
            file = finding.get("file", "unknown_file")
            line = finding.get("line", "?")
            items.append(f"- [ ] [solid-lite:{sev}] `{rule}` en `{file}:{line}`.")
        for w in summary.get("solid_thresholds_warnings", []):
            items.append(f"- [ ] [solid-thresholds:warning] Resolver configuracion: `{w}`.")

    if not items:
        items.append("- [ ] Sin tareas pendientes automaticas de project-gates.")
    return items


def upsert_todo_md(repo_root: Path, summary: Dict[str, object]) -> Path:
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    todo_path = docs_dir / "todo.md"
    auto_lines = [
        TODO_AUTOGEN_START,
        "## Project Gates (autogenerado)",
        "",
        *build_todo_items(summary),
        TODO_AUTOGEN_END,
    ]
    auto_block = "\n".join(auto_lines) + "\n"

    if not todo_path.exists():
        todo_path.write_text("# TODO\n\n" + auto_block, encoding="utf-8", newline="\n")
        return todo_path

    content = todo_path.read_text(encoding="utf-8", errors="ignore")
    # Clean deprecated auto-generated blocks so only the canonical block remains.
    for legacy_start, legacy_end in [
        (TODO_LEGACY_POLICY_START, TODO_LEGACY_POLICY_END),
        (TODO_LEGACY_START, TODO_LEGACY_END),
    ]:
        ls = content.find(legacy_start)
        le = content.find(legacy_end)
        if ls != -1 and le != -1 and le >= ls:
            content = content[:ls].rstrip() + "\n\n" + content[le + len(legacy_end) :].lstrip("\n")

    start = content.find(TODO_AUTOGEN_START)
    end = content.find(TODO_AUTOGEN_END)
    if start != -1 and end != -1 and end >= start:
        end = end + len(TODO_AUTOGEN_END)
    if start != -1 and end != -1 and end >= start:
        new_content = content[:start].rstrip() + "\n\n" + auto_block + content[end:].lstrip("\n")
    else:
        new_content = content.rstrip() + "\n\n" + auto_block
    todo_path.write_text(new_content, encoding="utf-8", newline="\n")
    return todo_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap project initializer")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--project-name", help="Project name")
    parser.add_argument("--project-goal", help="Project goal")
    parser.add_argument("--runtime-command", help="Runtime command")
    parser.add_argument("--notes", help="Additional notes")
    parser.add_argument("--report", default=".tmp/bootstrap.json", help="Bootstrap report path")
    parser.add_argument(
        "--scaffold-only",
        action="store_true",
        help="Only scaffold folders/files and skip policy enforcement as exit gate",
    )
    parser.add_argument(
        "--policy-only",
        action="store_true",
        help="Only run policies (layout/env/python/layer-boundary) and update docs/todo.md",
    )
    parser.add_argument(
        "--structure-gate-only",
        action="store_true",
        help="Run only structure gate (env/layout/python-file) and update docs/todo.md",
    )
    parser.add_argument(
        "--architecture-gate-only",
        action="store_true",
        help="Run only architecture gate (layer-boundary) and update docs/todo.md",
    )
    parser.add_argument(
        "--architecture-baseline",
        default=".tmp/architecture_baseline.json",
        help="Architecture baseline file path",
    )
    parser.add_argument(
        "--write-architecture-baseline",
        action="store_true",
        help="Write current architecture findings as baseline",
    )
    parser.add_argument(
        "--enforce-architecture-baseline",
        action="store_true",
        help="Fail if architecture findings appear that are not in baseline",
    )
    parser.add_argument(
        "--solid-thresholds",
        default="docs/architecture/solid-thresholds.json",
        help="Solid-lite thresholds file path",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only validate layout/env policy without writing files",
    )
    parser.add_argument(
        "--fix-python",
        action="store_true",
        help="Auto-fix python-file-policy mechanical issues (__init__, Path, import order)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()
    if args.scaffold_only and args.policy_only:
        parser.error("--scaffold-only and --policy-only are mutually exclusive")
    if args.structure_gate_only and args.architecture_gate_only:
        parser.error("--structure-gate-only and --architecture-gate-only are mutually exclusive")
    if args.scaffold_only and (args.structure_gate_only or args.architecture_gate_only):
        parser.error("--scaffold-only cannot be combined with gate-only flags")

    repo_root = Path(args.repo_root).resolve()
    created_dirs: list[str] = []
    created_files: list[str] = []

    should_scaffold = not args.check and not args.policy_only
    if should_scaffold:
        project_name = resolve_context_field(
            explicit_value=args.project_name,
            inferred_value=infer_project_name(repo_root),
            fallback="Unnamed Project",
        )
        project_goal = resolve_context_field(
            explicit_value=args.project_goal,
            inferred_value="",
            fallback="TBD",
        )
        runtime_command = resolve_context_field(
            explicit_value=args.runtime_command,
            inferred_value=infer_runtime_command(repo_root),
            fallback="python run.py",
        )
        notes = resolve_context_field(
            explicit_value=args.notes,
            inferred_value="",
            fallback="N/A",
        )

        for rel in DIRS:
            p = repo_root / rel
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                created_dirs.append(rel)

        for rel in GITKEEP_DIRS:
            p = repo_root / rel / ".gitkeep"
            if write_if_missing(p, "", args.force):
                created_files.append(str(p.relative_to(repo_root)))

        readme_content = (
            "<!-- Path: README.md -->\n"
            f"# {project_name}\n\n"
            "## Bootstrap Context\n\n"
            f"- Project name: {project_name}\n"
            f"- Project goal: {project_goal}\n"
            f"- Runtime command: {runtime_command}\n"
            f"- Notes: {notes}\n"
        )
        if write_if_missing(repo_root / "README.md", readme_content, args.force):
            created_files.append("README.md")

        solid_thresholds_content = (
            "{\n"
            '  "max_use_case_classes_per_module": 1,\n'
            '  "max_use_case_top_level_functions": 3,\n'
            '  "max_gateway_public_methods": 7,\n'
            '  "max_public_methods_per_class": 10\n'
            "}\n"
        )
        if write_if_missing(repo_root / "docs/architecture/solid-thresholds.json", solid_thresholds_content, args.force):
            created_files.append("docs/architecture/solid-thresholds.json")

        if write_if_missing(repo_root / "run.py", "", args.force):
            created_files.append("run.py")

        gitignore_content = (
            "# Path: .gitignore\n"
            "__pycache__/\n"
            "*.pyc\n"
            ".venv/\n"
            ".env\n"
            ".tmp/\n"
            ".pytest_cache/\n"
            ".mypy_cache/\n"
        )
        if write_if_missing(repo_root / ".gitignore", gitignore_content, args.force):
            created_files.append(".gitignore")

        env_content = (
            "# Path: .env\n"
            "APP_ENV=local\n"
            "LOG_LEVEL=INFO\n"
        )
        if write_if_missing(repo_root / ".env", env_content, args.force):
            created_files.append(".env")

        env_example_content = (
            "# Path: .env.example\n"
            "APP_ENV=local\n"
            "LOG_LEVEL=INFO\n"
        )
        if write_if_missing(repo_root / ".env.example", env_example_content, args.force):
            created_files.append(".env.example")

        config_py = (
            '"""\n'
            "Path: src/infrastructure/settings/config.py\n"
            '"""\n\n'
            "APP_ENV = 'local'\n"
            "LOG_LEVEL = 'INFO'\n"
        )
        if write_if_missing(repo_root / "src/infrastructure/settings/config.py", config_py, args.force):
            created_files.append("src/infrastructure/settings/config.py")

        logger_py = (
            '"""\n'
            "Path: src/infrastructure/settings/logger.py\n"
            '"""\n\n'
            "import logging\n\n"
            "def get_logger(name: str) -> logging.Logger:\n"
            "    return logging.getLogger(name)\n"
        )
        if write_if_missing(repo_root / "src/infrastructure/settings/logger.py", logger_py, args.force):
            created_files.append("src/infrastructure/settings/logger.py")

    created_init_files, missing_inits = ensure_init_files(
        repo_root=repo_root,
        force=args.force,
        check_mode=(args.check or args.policy_only),
    )
    created_files.extend(created_init_files)
    auto_fixed: Dict[str, list[str]] = {
        "init_emptied": [],
        "path_docstring_fixed": [],
        "import_order_fixed": [],
    }
    if args.fix_python and not args.check:
        auto_fixed["init_emptied"] = normalize_init_files(repo_root)
        auto_fixed["path_docstring_fixed"] = normalize_path_docstrings(repo_root)
        auto_fixed["import_order_fixed"] = normalize_import_order(repo_root)

    env_data = parse_env_file(repo_root / ".env")
    env_example_data = parse_env_file(repo_root / ".env.example")
    env_keys = env_data["keys"]
    env_example_keys = env_example_data["keys"]
    env_only = sorted(env_keys - env_example_keys)
    env_example_only = sorted(env_example_keys - env_keys)
    invalid_lines = sorted(env_data["invalid_lines"] + env_example_data["invalid_lines"])
    possible_secrets_in_example = detect_possible_secrets_in_example(env_example_data["values"])

    env_parity_ok = env_keys == env_example_keys
    env_policy_ok = (
        env_parity_ok
        and len(invalid_lines) == 0
        and len(possible_secrets_in_example) == 0
    )
    layout = validate_layout_policy(repo_root)
    layout_policy_ok = bool(layout["ok"])
    python_policy = validate_python_policy(repo_root, missing_inits=missing_inits)
    python_policy_ok = bool(python_policy["ok"])
    layer_boundary = validate_layer_boundary(repo_root)
    layer_boundary_ok = bool(layer_boundary["ok"])
    solid_thresholds_path = (repo_root / args.solid_thresholds).resolve()
    solid_thresholds, solid_thresholds_warnings, solid_thresholds_loaded = load_solid_thresholds(solid_thresholds_path)
    solid_lite = validate_solid_lite(repo_root, thresholds=solid_thresholds)
    solid_lite_ok = bool(solid_lite["ok"])
    policy_ok = env_policy_ok and layout_policy_ok and python_policy_ok and layer_boundary_ok and solid_lite_ok

    run_structure_gate = args.policy_only or args.structure_gate_only or (
        not args.scaffold_only and not args.architecture_gate_only
    )
    run_architecture_gate = args.policy_only or args.architecture_gate_only or (
        not args.scaffold_only and not args.structure_gate_only
    )

    baseline_path = (repo_root / args.architecture_baseline).resolve()
    baseline_written = False
    architecture_regression_ok = True
    architecture_new_findings: list[str] = []
    architecture_resolved_findings: list[str] = []
    if args.write_architecture_baseline:
        save_architecture_baseline(baseline_path, layer_boundary.get("findings", []))
        baseline_written = True
    if args.enforce_architecture_baseline and run_architecture_gate:
        baseline = load_architecture_baseline(baseline_path)
        current = {architecture_finding_key(x) for x in layer_boundary.get("findings", [])}
        architecture_new_findings = sorted(current - baseline)
        architecture_resolved_findings = sorted(baseline - current)
        architecture_regression_ok = len(architecture_new_findings) == 0

    summary: Dict[str, object] = {
        "repo_root": str(repo_root),
        "check_mode": args.check,
        "scaffold_only_mode": args.scaffold_only,
        "policy_only_mode": args.policy_only,
        "structure_gate_only_mode": args.structure_gate_only,
        "architecture_gate_only_mode": args.architecture_gate_only,
        "architecture_baseline_path": str(baseline_path),
        "write_architecture_baseline_mode": args.write_architecture_baseline,
        "enforce_architecture_baseline_mode": args.enforce_architecture_baseline,
        "architecture_baseline_written": baseline_written,
        "architecture_regression_ok": architecture_regression_ok,
        "architecture_new_findings": architecture_new_findings,
        "architecture_resolved_findings": architecture_resolved_findings,
        "solid_thresholds_path": str(solid_thresholds_path),
        "solid_thresholds_loaded": solid_thresholds_loaded,
        "solid_thresholds": solid_thresholds,
        "solid_thresholds_warnings": solid_thresholds_warnings,
        "fix_python_mode": args.fix_python,
        "created_dirs": created_dirs,
        "created_files": created_files,
        "auto_fixed": auto_fixed,
        "env_parity_ok": env_parity_ok,
        "env_only": env_only,
        "env_example_only": env_example_only,
        "env_invalid_lines": invalid_lines,
        "possible_secrets_in_example": possible_secrets_in_example,
        "env_policy_ok": env_policy_ok,
        "layout_policy_ok": layout_policy_ok,
        "layout_violations": layout["violations"],
        "layout_details": layout,
        "python_policy_ok": python_policy_ok,
        "python_violations": python_policy["violations"],
        "python_details": python_policy,
        "layer_boundary_ok": layer_boundary_ok,
        "layer_boundary_violations": layer_boundary["violations"],
        "layer_boundary_details": layer_boundary,
        "solid_lite_ok": solid_lite_ok,
        "solid_lite_violations": solid_lite["violations"],
        "solid_lite_details": solid_lite,
        "ok": policy_ok,
    }

    structure_gate_ok = env_policy_ok and layout_policy_ok and python_policy_ok
    architecture_gate_ok = layer_boundary_ok and solid_lite_ok and architecture_regression_ok
    selected_ok = True
    if run_structure_gate:
        selected_ok = selected_ok and structure_gate_ok
    if run_architecture_gate:
        selected_ok = selected_ok and architecture_gate_ok
    summary["structure_gate_ok"] = structure_gate_ok
    summary["architecture_gate_ok"] = architecture_gate_ok
    summary["run_structure_gate"] = run_structure_gate
    summary["run_architecture_gate"] = run_architecture_gate
    summary["ok"] = selected_ok

    todo_path = upsert_todo_md(repo_root, summary)
    summary["todo_path"] = str(todo_path)

    report_path = (repo_root / args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(f"BOOTSTRAP={'PASS' if policy_ok else 'FAIL'}")
        print(f"REPO={repo_root}")
        print(f"REPORT={report_path}")
        print(f"CHECK_MODE={args.check}")
        print(f"FIX_PYTHON_MODE={args.fix_python}")
        print(f"CREATED_DIRS={len(created_dirs)}")
        print(f"CREATED_FILES={len(created_files)}")
        print(f"ENV_PARITY_OK={env_parity_ok}")
        print(f"ENV_POLICY_OK={env_policy_ok}")
        print(f"LAYOUT_POLICY_OK={layout_policy_ok}")
        print(f"PYTHON_POLICY_OK={python_policy_ok}")
        print(f"LAYER_BOUNDARY_OK={layer_boundary_ok}")
        if not policy_ok:
            print(f"- env_only={env_only}")
            print(f"- env_example_only={env_example_only}")
            print(f"- env_invalid_lines={invalid_lines}")
            print(f"- possible_secrets_in_example={possible_secrets_in_example}")
            print(f"- layout_violations={layout['violations']}")
            print(f"- python_violations={python_policy['violations']}")
            print(f"- layer_boundary_violations={layer_boundary['violations']}")
            print(f"- solid_lite_violations={solid_lite['violations']}")
            print(f"- solid_thresholds_warnings={solid_thresholds_warnings}")
            print(f"- architecture_new_findings={architecture_new_findings}")

    if args.scaffold_only:
        return 0
    return 0 if bool(summary["ok"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
