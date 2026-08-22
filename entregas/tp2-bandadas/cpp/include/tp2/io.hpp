#pragma once

#include <cstddef>
#include <cstdint>
#include <iosfwd>
#include <string_view>

#include "tp2/model.hpp"

namespace tp2 {

struct RunMetadata {
    std::string_view model{};
    double density{};
    std::size_t particle_count{};
    double side{};
    std::size_t cells_per_side{};
    double cutoff{};
    double speed{};
    double time_step{};
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
