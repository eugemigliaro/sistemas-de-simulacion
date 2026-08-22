#pragma once

#include "tp2/model.hpp"
#include "tp2/neighbors.hpp"

namespace tp2 {

[[nodiscard]] double polarization(const System& system);

[[nodiscard]] double largest_cluster_fraction(
    const NeighborList& neighbors
);

}  // namespace tp2
