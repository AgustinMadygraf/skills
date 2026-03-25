"""
Tests para audit_utils/report.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from audit_utils.report import Finding, Report, ReportBuilder


def test_finding_creation():
    """Finding se crea correctamente."""
    f = Finding(
        severity="critical",
        rule="test_rule",
        file="test.py",
        line=10,
        detail="Test detail"
    )
    assert f.severity == "critical"
    assert f.rule == "test_rule"
    assert f.file == "test.py"
    assert f.line == 10
    assert f.detail == "Test detail"


def test_finding_to_dict():
    """Finding.to_dict() serializa correctamente."""
    f = Finding(
        severity="warning",
        rule="test_rule",
        file="test.py",
        line=5,
        detail="Detail"
    )
    d = f.to_dict()
    assert d["severity"] == "warning"
    assert d["rule"] == "test_rule"
    assert d["line"] == 5


def test_finding_to_violation_string():
    """Finding.to_violation_string() formato correcto."""
    f = Finding("critical", "rule", "file.py", 10, "detail")
    assert f.to_violation_string() == "file.py:10:rule"


def test_report_empty_is_ok():
    """Report vacío tiene ok=True."""
    r = Report(findings=[])
    assert r.ok is True
    assert r.critical_total == 0
    assert r.warning_total == 0
    assert r.info_total == 0


def test_report_with_critical_is_not_ok():
    """Report con críticos tiene ok=False."""
    r = Report(findings=[
        Finding("critical", "rule", "file.py", 1, "detail")
    ])
    assert r.ok is False
    assert r.critical_total == 1


def test_report_counts_by_severity():
    """Report cuenta correctamente por severidad."""
    r = Report(findings=[
        Finding("critical", "r1", "f.py", 1, "d"),
        Finding("critical", "r2", "f.py", 2, "d"),
        Finding("warning", "r3", "f.py", 3, "d"),
        Finding("warning", "r4", "f.py", 4, "d"),
        Finding("warning", "r5", "f.py", 5, "d"),
        Finding("info", "r6", "f.py", 6, "d"),
    ])
    assert r.critical_total == 2
    assert r.warning_total == 3
    assert r.info_total == 1


def test_report_to_dict():
    """Report.to_dict() incluye todos los campos."""
    r = Report(findings=[Finding("warning", "rule", "file.py", 1, "detail")])
    d = r.to_dict()
    assert "ok" in d
    assert "critical_total" in d
    assert "warning_total" in d
    assert "info_total" in d
    assert "findings" in d
    assert "violations" in d


def test_report_builder_empty():
    """ReportBuilder vacío crea report vacío."""
    builder = ReportBuilder()
    r = builder.build()
    assert r.ok is True
    assert len(r.findings) == 0


def test_report_builder_add_finding():
    """ReportBuilder.add_finding agrega hallazgo."""
    builder = ReportBuilder()
    builder.add_finding("critical", "rule", "file.py", 10, "detail")
    r = builder.build()
    assert len(r.findings) == 1
    assert r.findings[0].severity == "critical"


def test_report_builder_add_critical():
    """ReportBuilder.add_critical es shorthand correcto."""
    builder = ReportBuilder()
    builder.add_critical("rule", "file.py", 10, "detail")
    r = builder.build()
    assert r.findings[0].severity == "critical"
    assert r.ok is False


def test_report_builder_add_warning():
    """ReportBuilder.add_warning es shorthand correcto."""
    builder = ReportBuilder()
    builder.add_warning("rule", "file.py", 10, "detail")
    r = builder.build()
    assert r.findings[0].severity == "warning"


def test_report_builder_add_info():
    """ReportBuilder.add_info es shorthand correcto."""
    builder = ReportBuilder()
    builder.add_info("rule", "file.py", 10, "detail")
    r = builder.build()
    assert r.findings[0].severity == "info"


def test_report_builder_chaining():
    """ReportBuilder permite chaining."""
    builder = ReportBuilder()
    builder.add_critical("r1", "f.py", 1, "d").add_warning("r2", "f.py", 2, "d")
    r = builder.build()
    assert len(r.findings) == 2


def test_report_builder_extend():
    """ReportBuilder.extend agrega múltiples findings."""
    findings = [
        Finding("critical", "r1", "f.py", 1, "d"),
        Finding("warning", "r2", "f.py", 2, "d"),
    ]
    builder = ReportBuilder()
    builder.extend(findings)
    r = builder.build()
    assert len(r.findings) == 2


if __name__ == "__main__":
    import traceback
    
    tests = [
        test_finding_creation,
        test_finding_to_dict,
        test_finding_to_violation_string,
        test_report_empty_is_ok,
        test_report_with_critical_is_not_ok,
        test_report_counts_by_severity,
        test_report_to_dict,
        test_report_builder_empty,
        test_report_builder_add_finding,
        test_report_builder_add_critical,
        test_report_builder_add_warning,
        test_report_builder_add_info,
        test_report_builder_chaining,
        test_report_builder_extend,
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
