#pragma once

#include "tp2/model.hpp"

namespace tp2 {

[[nodiscard]] bool is_valid(const Particle& particle) noexcept;
[[nodiscard]] bool is_valid(const System& system) noexcept;

[[nodiscard]] double wrap_coordinate(double value, double side);
[[nodiscard]] double normalize_angle(double angle);

[[nodiscard]] Vec2 periodic_displacement(
    const Particle& from,
    const Particle& to,
    double side
);

[[nodiscard]] double periodic_distance_squared(
    const Particle& first,
    const Particle& second,
    double side
);

[[nodiscard]] bool are_neighbors(
    const Particle& first,
    const Particle& second,
    double side,
    double cutoff
);

}  // namespace tp2
