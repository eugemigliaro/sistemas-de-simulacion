#pragma once

#include <cstddef>
#include <iosfwd>

#include "tp2/model.hpp"

namespace tp2 {

struct RunConfig {
    InitializationConfig initialization{};
    DynamicsConfig dynamics{};
    std::size_t cells_per_side{9};
    std::size_t steps{};
    std::size_t trajectory_every{1};
};

struct RunSummary {
    std::size_t frames_written{};
    std::size_t observations_written{};
};

[[nodiscard]] bool is_valid(const RunConfig& config) noexcept;

[[nodiscard]] RunSummary run_simulation(
    const RunConfig& config,
    std::ostream& observations_output,
    std::ostream* trajectory_output = nullptr
);

}  // namespace tp2
