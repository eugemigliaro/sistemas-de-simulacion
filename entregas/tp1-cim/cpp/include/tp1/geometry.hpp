#pragma once

#include "tp1/model.hpp"

namespace tp1 {

[[nodiscard]] bool is_valid(const Particle& particle) noexcept;
[[nodiscard]] bool is_valid(const Domain& domain) noexcept;

[[nodiscard]] bool is_inside_domain(
    const Particle& particle,
    const Domain& domain
) noexcept;

[[nodiscard]] Vec2 displacement(
    const Particle& from,
    const Particle& to,
    const Domain& domain
);

[[nodiscard]] double center_distance(
    const Particle& first,
    const Particle& second,
    const Domain& domain
);

[[nodiscard]] double edge_distance(
    const Particle& first,
    const Particle& second,
    const Domain& domain
);

[[nodiscard]] bool are_neighbors(
    const Particle& first,
    const Particle& second,
    const Domain& domain,
    double cutoff
);

}  // namespace tp1
