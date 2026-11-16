"""Estudio de la recuperación de v_d en EDMD puro, con N = AGENTS y L = 50 m, semillas 701 a
710: patadas con varios delta contra relajación analítica con varias tolerancias de
reapuntado, más TSDMD y el híbrido como referencias (decisión 7 del 2026-11-14: si el piloto
analítico tarda menos de 30 min, el estudio va completo; con N = 60 tarda de 31 a 84 s).
EDMD_OPTIONS es la regla de choque de EDMD puro.

Uso: python scripts/run_recuperacion.py
"""
from common import AGENTS, DT, EDMD_OPTIONS, HYBRID_OPTIONS, RAW, SECOND_TARGET, T_STAR, evacuate, run_all

SEEDS = range(701, 711)
KICKS = (0.01, 0.02, 0.05, 0.1, 0.2)
AIMS = (0.003, 0.01, 0.03, 0.1)


def variants() -> dict[str, dict]:
    out = {f"kicks{kick:g}": dict(scheme="edmd", relaxation="kicks", kick=kick, **EDMD_OPTIONS) for kick in KICKS}
    out.update({f"analytic{aim:g}": dict(scheme="edmd", relaxation="analytic", aim_tolerance=aim, **EDMD_OPTIONS)
                for aim in AIMS})
    out["tsdmd"] = dict(scheme="tsdmd")
    out["hybrid"] = dict(scheme="hybrid", t_star=T_STAR, **HYBRID_OPTIONS)
    return out


def main() -> None:
    jobs = []
    for seed in SEEDS:
        base = dict(agents=AGENTS, dt=DT, seed=seed, **SECOND_TARGET)
        for name, options in variants().items():
            path = RAW / "recuperacion" / f"{name}_seed{seed}.txt"
            jobs.append((path, evacuate(path, **options, **base)))
    run_all(jobs)


if __name__ == "__main__":
    main()
