#pragma once

#include <cstdint>
#include <functional>
#include <vector>

#include "tp4/billiard.hpp"

namespace tp4 {

// Se integra durante steps pasos de dt y se entrega el estado cada
// output_every pasos, es decir con dt2 = output_every * dt [TP04, p. 2].
struct Run {
    double dt{};
    std::uint64_t steps{};
    std::uint64_t output_every{1};
};

// Recibe el paso, el tiempo y el estado. El motor no calcula observables:
// solo entrega posiciones, velocidades y colores [COR02].
using FrameSink = std::function<void(std::uint64_t step, double time, const std::vector<Particle>&)>;

void validate(const Run& run);

// Verlet original [T04, p. 13]:
//   r(t + dt) = 2 r(t) - r(t - dt) + dt^2 F(t) / m
//   v(t) = [r(t + dt) - r(t - dt)] / (2 dt)
// El estado en t - dt se estima con Euler hacia atrás. Como v(t) requiere
// r(t + dt), cada cuadro se entrega después de calcular el paso siguiente.
void simulate(const Billiard& billiard, std::vector<Particle> particles, const Run& run, const FrameSink& sink);

}  // namespace tp4
