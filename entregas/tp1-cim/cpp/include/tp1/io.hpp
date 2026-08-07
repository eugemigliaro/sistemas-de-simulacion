#pragma once

#include <iosfwd>

#include "tp1/model.hpp"
#include "tp1/neighbors.hpp"

namespace tp1 {

void write_static(std::ostream& output, const ParticleSystem& system);

void write_dynamic(std::ostream& output, const ParticleSystem& system);

void write_neighbors(
    std::ostream& output,
    const NeighborList& neighbors
);

[[nodiscard]] ParticleSystem read_system(
    std::istream& static_input,
    std::istream& dynamic_input,
    BoundaryCondition boundary
);

}  // namespace tp1
