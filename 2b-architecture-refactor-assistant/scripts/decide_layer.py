#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def score_layer(text: str) -> Dict[str, int]:
    score = {
        "entities": 0,
        "use_cases": 0,
        "gateways": 0,
        "controllers": 0,
        "presenters": 0,
        "infrastructure": 0,
    }

    rules: List[Tuple[str, str, int]] = [
        ("entities", r"\b(entidad|entity|value object|regla de negocio|invariante|dominio)\b", 3),
        ("use_cases", r"\b(caso de uso|use case|orquestar|workflow|servicio de aplicacion)\b", 3),
        ("gateways", r"\b(gateway|puerto|port|repositorio abstracto|contrato de salida)\b", 3),
        ("controllers", r"\b(controller|controlador|endpoint|request|input|cli command|argumentos)\b", 3),
        ("presenters", r"\b(presenter|view model|response model|output|serializar salida|render)\b", 3),
        ("presenters", r"\b(salida cli|respuesta|response|formato de salida)\b", 3),
        ("infrastructure", r"\b(sqlite|pymysql|sqlalchemy|requests|httpx|fastapi|flask|driver|sdk|framework|db)\b", 3),
        ("use_cases", r"\b(validar flujo|transaccion|coordinar)\b", 2),
        ("controllers", r"\b(parsing|parsear|tty|stdin|http|api)\b", 2),
        ("presenters", r"\b(formatear|markdown|json de salida|tabla|rich)\b", 2),
        ("infrastructure", r"\b(persistencia|filesystem|red|http client|orm)\b", 2),
    ]

    for layer, pattern, weight in rules:
        if re.search(pattern, text):
            score[layer] += weight
    return score


def decide(score: Dict[str, int]) -> str:
    max_score = max(score.values())
    if max_score == 0:
        return "use_cases"
    for preferred in ["infrastructure", "controllers", "presenters", "gateways", "use_cases", "entities"]:
        if score.get(preferred, 0) == max_score:
            return preferred
    return "use_cases"


def recommendation(layer: str) -> Dict[str, object]:
    recs = {
        "entities": {
            "reason": "Contiene reglas de negocio puras y no depende de detalles externos.",
            "allowed": ["typing", "src.entities.*"],
            "forbidden": ["src.infrastructure.*", "frameworks", "drivers", "http/db libs"],
            "path": "src/entities/",
        },
        "use_cases": {
            "reason": "Orquesta reglas de negocio y puertos sin acoplarse a implementaciones externas.",
            "allowed": ["src.entities.*", "src.interface_adapters.gateways.* (interfaces/ports)"],
            "forbidden": ["src.infrastructure.*", "vendors directos"],
            "path": "src/use_cases/",
        },
        "gateways": {
            "reason": "Define contratos/adaptadores entre casos de uso y detalles externos.",
            "allowed": ["src.entities.*", "src.use_cases.* (ports/contracts)"],
            "forbidden": ["framework SDK concreto directo en contratos"],
            "path": "src/interface_adapters/gateways/",
        },
        "controllers": {
            "reason": "Adapta entrada externa (CLI/API) hacia casos de uso.",
            "allowed": ["src.use_cases.*", "DTOs/adapters de entrada"],
            "forbidden": ["reglas de negocio complejas", "acceso DB directo"],
            "path": "src/interface_adapters/controllers/",
        },
        "presenters": {
            "reason": "Adapta la salida de casos de uso al formato requerido por UI/CLI/API.",
            "allowed": ["src.use_cases.*", "DTOs de salida"],
            "forbidden": ["controllers", "acceso DB directo"],
            "path": "src/interface_adapters/presenters/",
        },
        "infrastructure": {
            "reason": "Implementa detalles concretos de framework/librerias externas/DB.",
            "allowed": ["vendors", "drivers", "framework glue code"],
            "forbidden": ["reglas de negocio de dominio"],
            "path": "src/infrastructure/",
        },
    }
    return recs[layer]


def main() -> int:
    parser = argparse.ArgumentParser(description="Decide target layer for a new change.")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--change", required=True, help="Natural language description of the change")
    parser.add_argument("--json", action="store_true", help="Print json output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    text = normalize(args.change)
    score = score_layer(text)
    layer = decide(score)
    rec = recommendation(layer)

    result = {
        "repo_root": str(repo_root),
        "change": args.change,
        "recommended_layer": layer,
        "recommended_path": rec["path"],
        "reason": rec["reason"],
        "allowed_dependencies": rec["allowed"],
        "forbidden_dependencies": rec["forbidden"],
        "score": score,
        "next_checks": [
            "1a-project-structure-gate",
            "2a-project-architecture-gate",
        ],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"LAYER={result['recommended_layer']}")
        print(f"PATH={result['recommended_path']}")
        print(f"REASON={result['reason']}")
        print(f"ALLOWED={', '.join(result['allowed_dependencies'])}")
        print(f"FORBIDDEN={', '.join(result['forbidden_dependencies'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

