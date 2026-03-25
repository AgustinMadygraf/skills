"""
Path: shared/audit_utils/report.py

Estructuras de reporte para hallazgos de auditoría.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["critical", "warning", "info"]


@dataclass
class Finding:
    """
    Un hallazgo de auditoría.
    
    Attributes:
        severity: Nivel de severidad (critical, warning, info)
        rule: Identificador de la regla violada
        file: Ruta al archivo relativo al repo
        line: Número de línea (1-indexed)
        detail: Descripción del hallazgo
    """
    severity: Severity
    rule: str
    file: str
    line: int
    detail: str
    
    def to_dict(self) -> dict[str, object]:
        """Convierte a diccionario para serialización."""
        return {
            "severity": self.severity,
            "rule": self.rule,
            "file": self.file,
            "line": self.line,
            "detail": self.detail,
        }
    
    def to_violation_string(self) -> str:
        """Formato compacto para logs: file:line:rule"""
        return f"{self.file}:{self.line}:{self.rule}"


@dataclass
class Report:
    """
    Reporte completo de auditoría.
    
    Attributes:
        findings: Lista de hallazgos
        ok: True si no hay hallazgos críticos
        critical_total: Conteo de críticos
        warning_total: Conteo de warnings
        info_total: Conteo de infos
    """
    findings: list[Finding] = field(default_factory=list)
    
    @property
    def ok(self) -> bool:
        """True si no hay hallazgos críticos."""
        return self.critical_total == 0
    
    @property
    def critical_total(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical")
    
    @property
    def warning_total(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")
    
    @property
    def info_total(self) -> int:
        return sum(1 for f in self.findings if f.severity == "info")
    
    def to_dict(self) -> dict[str, object]:
        """Convierte a diccionario completo."""
        return {
            "ok": self.ok,
            "critical_total": self.critical_total,
            "warning_total": self.warning_total,
            "info_total": self.info_total,
            "findings": [f.to_dict() for f in self.findings],
            "violations": [f.to_violation_string() for f in self.findings],
        }


class ReportBuilder:
    """
    Builder para construir reportes de auditoría.
    
    Example:
        builder = ReportBuilder()
        builder.add_finding("critical", "rule_name", "file.py", 10, "detail")
        report = builder.build()
    """
    
    def __init__(self) -> None:
        self._findings: list[Finding] = []
    
    def add_finding(
        self,
        severity: Severity,
        rule: str,
        file: str,
        line: int,
        detail: str,
    ) -> "ReportBuilder":
        """Agrega un hallazgo al reporte."""
        self._findings.append(Finding(
            severity=severity,
            rule=rule,
            file=file,
            line=line,
            detail=detail,
        ))
        return self
    
    def add_critical(self, rule: str, file: str, line: int, detail: str) -> "ReportBuilder":
        """Agrega un hallazgo crítico."""
        return self.add_finding("critical", rule, file, line, detail)
    
    def add_warning(self, rule: str, file: str, line: int, detail: str) -> "ReportBuilder":
        """Agrega un warning."""
        return self.add_finding("warning", rule, file, line, detail)
    
    def add_info(self, rule: str, file: str, line: int, detail: str) -> "ReportBuilder":
        """Agrega un info."""
        return self.add_finding("info", rule, file, line, detail)
    
    def build(self) -> Report:
        """Construye el reporte final."""
        return Report(findings=self._findings.copy())
    
    def extend(self, findings: list[Finding]) -> "ReportBuilder":
        """Extiende con una lista de hallazgos existentes."""
        self._findings.extend(findings)
        return self
