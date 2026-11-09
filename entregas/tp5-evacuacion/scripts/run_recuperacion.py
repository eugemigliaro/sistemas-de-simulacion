"""Estudio de la recuperación de v_d en EDMD puro, con N = AGENTS y L = 50 m, semillas 701 a
710 (decisiones 8 del 2026-11-09 y del piloto):
- corridas completas: patadas con varios delta, TSDMD y el híbrido;
- ventana de WINDOW s simulados: las mismas variantes más la relajación analítica (0,01 rad),
  para comparar el costo por segundo simulado en la misma ventana. Con N = AGENTS la analítica
  no termina (el piloto no llegó al final en 9,5 h).
EDMD_OPTIONS es la regla de choque elegida para EDMD puro.

Uso: python scripts/run_recuperacion.py
"""
from common import AGENTS, DT, EDMD_OPTIONS, RAW, SECOND_TARGET, T_STAR, evacuate, run_all

SEEDS = range(701, 711)
KICKS = (0.01, 0.02, 0.05, 0.1, 0.2)
AIM = 0.01     # tolerancia de reapuntado por omisión
WINDOW = 30.0  # s simulados de la ventana


def variants() -> dict[str, dict]:
    out = {f"kicks{kick:g}": dict(scheme="edmd", relaxation="kicks", kick=kick, **EDMD_OPTIONS) for kick in KICKS}
    out["tsdmd"] = dict(scheme="tsdmd")
    out["hybrid"] = dict(scheme="hybrid", t_star=T_STAR)
    return out


def main() -> None:
    jobs = []
    for seed in SEEDS:
        base = dict(agents=AGENTS, dt=DT, seed=seed, **SECOND_TARGET)
        for name, options in variants().items():
            path = RAW / "recuperacion" / f"{name}_seed{seed}.txt"
            jobs.append((path, evacuate(path, **options, **base)))
        window = {**variants(), f"analytic{AIM:g}": dict(scheme="edmd", relaxation="analytic", aim_tolerance=AIM,
                                                          **EDMD_OPTIONS)}
        for name, options in window.items():
            path = RAW / "recuperacion" / f"ventana{WINDOW:g}" / f"{name}_seed{seed}.txt"
            jobs.append((path, evacuate(path, **options, **base, t_max=WINDOW)))
    run_all(jobs)


if __name__ == "__main__":
    main()
