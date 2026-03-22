#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys


def clamp(name: str, value: int, min_v: int, max_v: int) -> int:
    if value < min_v or value > max_v:
        raise ValueError(f"{name} fuera de rango ({min_v}-{max_v}): {value}")
    return value


def score_duda(evidencia: int, alcance: int, riesgo_decision: int, reversibilidad: int) -> int:
    return riesgo_decision + reversibilidad + max(0, alcance - evidencia)


def clasificar(evidencia: int, alcance: int, score: int) -> str:
    if evidencia >= 2 and score <= 2:
        return "certeza"
    if score >= 3:
        return "duda"
    if score == 2 and alcance >= 2:
        return "duda"
    return "certeza"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calcula SCORE_DUDA y clasificacion para Clean Architecture Orchestrator")
    parser.add_argument("--evidencia", type=int, required=True, help="0-3")
    parser.add_argument("--alcance", type=int, required=True, help="0-3")
    parser.add_argument("--riesgo-decision", type=int, required=True, help="0-3")
    parser.add_argument("--reversibilidad", type=int, required=True, help="0-2")
    parser.add_argument("--json", action="store_true", help="Salida en JSON")
    args = parser.parse_args()

    try:
        evidencia = clamp("EVIDENCIA", args.evidencia, 0, 3)
        alcance = clamp("ALCANCE", args.alcance, 0, 3)
        riesgo_decision = clamp("RIESGO_DECISION", args.riesgo_decision, 0, 3)
        reversibilidad = clamp("REVERSIBILIDAD", args.reversibilidad, 0, 2)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    score = score_duda(evidencia, alcance, riesgo_decision, reversibilidad)
    tipo = clasificar(evidencia, alcance, score)
    puntaje = f"EVIDENCIA={evidencia} ALCANCE={alcance} RIESGO_DECISION={riesgo_decision} REVERSIBILIDAD={reversibilidad} SCORE_DUDA={score}"

    payload = {
        "evidencia": evidencia,
        "alcance": alcance,
        "riesgo_decision": riesgo_decision,
        "reversibilidad": reversibilidad,
        "score_duda": score,
        "clasificacion": tipo,
        "puntaje": puntaje,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"SCORE_DUDA={score}")
        print(f"CLASIFICACION={tipo}")
        print(f"PUNTAJE={puntaje}")
        print("MD: - Puntaje: `" + puntaje + "`")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
