#pragma once

#include <cstdint>
#include <iosfwd>
#include <vector>

#include "tp4/billiard.hpp"
#include "tp4/generation.hpp"
#include "tp4/oscillator.hpp"
#include "tp4/simulation.hpp"

namespace tp4 {

// Archivos de texto: una cabecera de líneas '#' con los parámetros y después
// los cuadros. En el billar cada cuadro es
//
//   frame <paso> <tiempo>
//   <x> <y> <vx> <vy> <color>      (N líneas; color 0 fresca, 1 usada)
//
// y en el oscilador cada línea es "<paso> <tiempo> <x> <v>".

void write_billiard_header(
    std::ostream& stream,
    const Billiard& billiard,
    const Generation& generation,
    const Run& run
);
void write_frame(std::ostream& stream, std::uint64_t step, double time, const std::vector<Particle>& particles);

void write_oscillator_header(std::ostream& stream, const Oscillator& oscillator, Integrator integrator, double dt);
void write_sample(std::ostream& stream, const OscillatorSample& sample);

}  // namespace tp4
