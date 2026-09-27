#pragma once

#include "tp3/simulation.hpp"

namespace tp3 {

// Motor ingenuo: recalcula todos los tiempos en cada evento con
// `find_next_event`, O(N^2) por evento. Es el oraculo contra el que se valida
// el motor con cola y la curva lenta del punto 1.1. No forma parte del motor
// entregado: el ZIP incluye unicamente la version final [TP03, p. 1].
//
// Modifica `system` in situ hasta `max_time` y emite los cuadros por `sink`,
// que puede ser vacio.
SimulationReport simulate_naive(
    System& system,
    const SimulationConfig& config,
    const FrameSink& sink
);

}  // namespace tp3
