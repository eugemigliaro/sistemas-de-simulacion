#pragma once

#include <random>

#include "tp2/model.hpp"
#include "tp2/neighbors.hpp"

namespace tp2 {

[[nodiscard]] bool is_valid(const DynamicsConfig& config) noexcept;
[[nodiscard]] bool is_valid(const InitializationConfig& config) noexcept;

[[nodiscard]] System generate_system(const InitializationConfig& config);

[[nodiscard]] System generate_system(
    const InitializationConfig& config,
    std::mt19937_64& generator
);

void advance(
    System& system,
    const NeighborList& neighbors,
    const DynamicsConfig& config,
    std::mt19937_64& generator
);

}  // namespace tp2
