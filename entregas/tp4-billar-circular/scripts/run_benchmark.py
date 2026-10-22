#!/usr/bin/env python3
"""2.1.b: tiempo de ejecución en función de N, TP4 frente al punto 1.1 del TP3 [TP04, p. 3].

Las corridas son secuenciales y conviene no usar la computadora mientras
tanto. Cada medición se guarda apenas termina; si se interrumpe, al volver a
correr se retoman las que faltan.
"""
import platform
import subprocess

from common import BENCHMARK, COUNTS, DT, RESULTS, SEEDS, read_csv, write_csv, write_json
from tp4analysis import stats

TF = 30.0
RUNS = RESULTS / "benchmark-runs.csv"


def measure(engine: str, n: int, seed: int) -> dict:
    output = subprocess.run([str(BENCHMARK), engine, str(n), str(seed), repr(DT), repr(TF)],
                            check=True, capture_output=True, text=True).stdout
    values = dict(line.split() for line in output.splitlines())
    return {"engine": engine, "n": n, "seed": seed, "seconds": float(values["seconds"]),
            "events": int(values.get("events", 0))}


def cpu_name() -> str:
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def main() -> None:
    if not BENCHMARK.exists():
        raise SystemExit("falta el harness: correr make bench")
    done = read_csv(RUNS) if RUNS.exists() else []
    finished = {(r["engine"], int(r["n"]), int(r["seed"])) for r in done}
    for seed in SEEDS:
        for n in COUNTS:
            for engine in ("tp4", "tp3"):
                if (engine, n, seed) in finished:
                    continue
                done.append(measure(engine, n, seed))
                write_csv(RUNS, done)
                print(f"{engine} N={n} semilla={seed}: {done[-1]['seconds']:.3f} s", flush=True)
    summary = []
    for engine in ("tp4", "tp3"):
        for n in COUNTS:
            values = [float(r["seconds"]) for r in done if r["engine"] == engine and int(r["n"]) == n]
            events = [int(r["events"]) for r in done if r["engine"] == engine and int(r["n"]) == n]
            mean, std = stats.mean_and_std(values)
            summary.append({"engine": engine, "n": n, "realizations": len(values), "seconds_mean": mean,
                            "seconds_std": std, "events_mean": sum(events) / len(events)})
    write_csv(RESULTS / "benchmark-summary.csv", summary)
    write_json(RESULTS / "benchmark-machine.json",
               {"cpu": cpu_name(), "system": platform.platform(), "dt_s": DT, "tf_s": TF})


if __name__ == "__main__":
    main()
