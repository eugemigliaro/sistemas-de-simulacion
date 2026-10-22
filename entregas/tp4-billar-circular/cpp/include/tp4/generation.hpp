#pragma once

#include <cstddef>
#include <cstdint>
#include <string_view>
#include <vector>

#include "tp4/billiard.hpp"

namespace tp4 {

// Random: posiciones uniformes en el área disponible, sorteadas de a una y
// rechazando superposiciones con la pared, los obstáculos y las partículas ya
// ubicadas [TP04, p. 2]. Por encima de una fracción de área cercana a 0,55 el
// rechazo no ubica las N partículas.
//
// Lattice: para esas densidades se eligen N sitios al azar de una red
// triangular con orientación y traslación aleatorias, y se desordenan con
// barridos de Monte Carlo de discos rígidos.
enum class Layout { Random, Lattice };

[[nodiscard]] Layout parse_layout(std::string_view name);
[[nodiscard]] std::string_view to_string(Layout layout) noexcept;

struct Generation {
    std::size_t particle_count{};
    std::uint64_t seed{};
    Layout layout{Layout::Random};
    std::size_t max_attempts{1'000'000};
    std::size_t lattice_sweeps{500};
};

// Todas las partículas nacen frescas, con rapidez v0 y dirección uniforme en
// [0, 2pi) [TP04, p. 2].
[[nodiscard]] std::vector<Particle> generate(const Billiard& billiard, const Generation& generation);

}  // namespace tp4
