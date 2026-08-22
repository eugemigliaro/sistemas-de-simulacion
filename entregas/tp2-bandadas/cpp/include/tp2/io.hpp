#pragma once

#include <cstdint>
#include <iosfwd>
#include <string_view>

#include "tp2/model.hpp"

namespace tp2 {

struct RunMetadata {
    std::string_view model{};
    double density{};
    double eta{};
    std::uint64_t seed{};
};

struct Observation {
    double time{};
    double polarization{};
    double largest_cluster_fraction{};
    std::int64_t cim_time_ns{};
    std::size_t neighbor_pairs{};
    std::size_t distance_evaluations{};
};

void write_trajectory_header(std::ostream& output);
void write_observations_header(std::ostream& output);

void write_trajectory_frame(
    std::ostream& output,
    const RunMetadata& metadata,
    const System& system,
    double speed
);

void write_observation(
    std::ostream& output,
    const RunMetadata& metadata,
    const Observation& observation
);

}  // namespace tp2
