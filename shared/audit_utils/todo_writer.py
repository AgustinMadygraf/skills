"""
Path: shared/audit_utils/todo_writer.py

Gestión de docs/todo.md para skills de auditoría.
"""
from __future__ import annotations

from pathlib import Path

from .report import Finding


class TodoWriter:
    """
    Escribe hallazgos de auditoría en docs/todo.md.
    
    Mantiene secciones delimitadas por markers para cada skill:
    <!-- skill-name:auto:start -->
    <!-- skill-name:auto:end -->
    
    Example:
        writer = TodoWriter(Path("."), "3a-solid-gate")
        writer.write_findings(findings, title="3a-SOLID Gate")
    """
    
    def __init__(self, repo_root: Path, skill_name: str):
        """
        Args:
            repo_root: Raíz del repositorio
            skill_name: Nombre de la skill (usado en los markers)
        """
        self.repo_root = Path(repo_root).resolve()
        self.skill_name = skill_name
        self.marker_start = f"<!-- {skill_name}:auto:start -->"
        self.marker_end = f"<!-- {skill_name}:auto:end -->"
        self.todo_path = self.repo_root / "docs" / "todo.md"
    
    def write_findings(
        self,
        findings: list[Finding],
        title: str | None = None,
        empty_message: str = "Sin hallazgos.",
    ) -> Path:
        """
        Escribe los hallazgos en docs/todo.md.
        
        Args:
            findings: Lista de hallazgos a documentar
            title: Título de la sección (default: skill_name)
            empty_message: Mensaje cuando no hay hallazgos
        
        Returns:
            Path al archivo todo.md
        """
        # Asegurar que existe el directorio docs/
        self.todo_path.parent.mkdir(parents=True, exist_ok=True)
        
        title = title or self.skill_name
        block = self._build_block(findings, title, empty_message)
        
        # Leer contenido actual o crear nuevo
        if self.todo_path.exists():
            content = self.todo_path.read_text(encoding="utf-8", errors="ignore")
        else:
            content = "# TODO\n"
        
        # Actualizar o insertar el bloque
        new_content = self._upsert_block(content, block)
        
        # Escribir resultado
        self.todo_path.write_text(new_content, encoding="utf-8", newline="\n")
        return self.todo_path
    
    def clear_section(self) -> Path:
        """
        Limpia la sección de esta skill dejando solo el mensaje vacío.
        
        Returns:
            Path al archivo todo.md
        """
        return self.write_findings([], empty_message="Sin hallazgos pendientes.")
    
    def _build_block(
        self,
        findings: list[Finding],
        title: str,
        empty_message: str,
    ) -> str:
        """Construye el bloque de contenido para esta skill."""
        lines = [
            self.marker_start,
            f"## {title} (autogenerado)",
            "",
        ]
        
        if findings:
            for f in findings:
                lines.append(
                    f"- [ ] [{self.skill_name}:{f.severity}] "
                    f"`{f.rule}` en `{f.file}:{f.line}`."
                )
        else:
            lines.append(f"- [ ] {empty_message}")
        
        lines.append(self.marker_end)
        return "\n".join(lines) + "\n"
    
    def _upsert_block(self, content: str, new_block: str) -> str:
        """
        Inserta o actualiza el bloque en el contenido existente.
        
        Si ya existe la sección (markers), la reemplaza.
        Si no existe, la agrega al final.
        """
        start_idx = content.find(self.marker_start)
        end_idx = content.find(self.marker_end)
        
        # Caso 1: Existe una sección previa válida
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            end_idx += len(self.marker_end)
            before = content[:start_idx].rstrip()
            after = content[end_idx:].lstrip("\n")
            
            if before and after:
                return f"{before}\n\n{new_block}{after}"
            elif before:
                return f"{before}\n\n{new_block}"
            elif after:
                return f"{new_block}{after}"
            else:
                return new_block
        
        # Caso 2: No existe, agregar al final
        return content.rstrip() + "\n\n" + new_block
