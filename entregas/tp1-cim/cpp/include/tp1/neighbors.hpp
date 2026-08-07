#pragma once

#include <cstddef>
#include <vector>

#include "tp1/model.hpp"

namespace tp1 {

using NeighborList = std::vector<std::vector<std::size_t>>;

struct NeighborSearchResult {
    NeighborList neighbors{};
    std::size_t pair_count{};
    std::size_t distance_evaluations{};
};

[[nodiscard]] NeighborSearchResult brute_force_neighbors(
    const ParticleSystem& system,
    double cutoff
);

[[nodiscard]] bool is_valid_neighbor_list(
    const NeighborList& neighbors
) noexcept;

[[nodiscard]] std::size_t count_neighbor_pairs(
    const NeighborList& neighbors
);

}  // namespace tp1
