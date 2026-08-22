#pragma once

#include <cstddef>
#include <vector>

#include "tp2/model.hpp"

namespace tp2 {

using NeighborList = std::vector<std::vector<std::size_t>>;

struct NeighborSearchResult {
    NeighborList neighbors{};
    std::size_t pair_count{};
    std::size_t distance_evaluations{};
};

[[nodiscard]] NeighborSearchResult brute_force_neighbors(
    const System& system,
    double cutoff
);

[[nodiscard]] NeighborSearchResult cell_index_neighbors(
    const System& system,
    double cutoff,
    std::size_t cells_per_side
);

[[nodiscard]] std::size_t maximum_valid_cells_per_side(
    const System& system,
    double cutoff
);

[[nodiscard]] bool is_valid_neighbor_list(
    const NeighborList& neighbors
) noexcept;

}  // namespace tp2
