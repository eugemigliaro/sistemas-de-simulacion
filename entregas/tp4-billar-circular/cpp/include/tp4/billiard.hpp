#pragma once

#include <cstdint>
#include <optional>
#include <vector>

#include "tp4/vec2.hpp"

namespace tp4 {

// Billar circular del sistema 2 [TP04, p. 2]. Los obstáculos son fijos, del
// mismo radio que las partículas y están centrados en (-x0, 0) y (x0, 0); sin
// obstacle_x el billar está vacío.
struct Billiard {
    double radius{0.51};
    double particle_radius{0.0175};
    double particle_mass{0.025};
    double stiffness{1.0e4};
    double initial_speed{1.0};
    std::optional<double> obstacle_x{};
};

// Una partícula fresca pasa a usada al tocar por primera vez un obstáculo y no
// vuelve a cambiar [TP04, p. 3].
enum class Color : std::uint8_t { Fresh = 0, Used = 1 };

struct Particle {
    Vec2 position{};
    Vec2 velocity{};
    Color color{Color::Fresh};
};

void validate(const Billiard& billiard);
[[nodiscard]] std::vector<Vec2> obstacle_centers(const Billiard& billiard);

}  // namespace tp4
