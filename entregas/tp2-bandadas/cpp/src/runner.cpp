#include "tp2/runner.hpp"

#include <chrono>
#include <random>
#include <stdexcept>
#include <string_view>

#include "tp2/io.hpp"
#include "tp2/neighbors.hpp"
#include "tp2/observables.hpp"
#include "tp2/simulation.hpp"

namespace tp2 {
namespace {

std::string_view model_name(AlignmentModel model) {
    switch (model) {
        case AlignmentModel::Vicsek:
            return "vicsek";
        case AlignmentModel::Voter:
            return "voter";
    }
    throw std::invalid_argument{"unknown alignment model"};
}

}  // namespace

bool is_valid(const RunConfig& config) noexcept {
    return is_valid(config.initialization)
        && is_valid(config.dynamics)
        && config.cells_per_side > 0
        && config.trajectory_every > 0;
}

RunSummary run_simulation(
    const RunConfig& config,
    std::ostream& observations_output,
    std::ostream* trajectory_output
) {
    if (!is_valid(config)) {
        throw std::invalid_argument{"invalid run configuration"};
    }

    std::mt19937_64 generator{config.initialization.seed};
    System system = generate_system(config.initialization, generator);
    if (config.cells_per_side
        > maximum_valid_cells_per_side(system, config.dynamics.cutoff)) {
        throw std::invalid_argument{"M is invalid for L and rc"};
    }

    const RunMetadata metadata{
        .model = model_name(config.dynamics.model),
        .density = static_cast<double>(system.particles.size())
            / (system.side * system.side),
        .eta = config.dynamics.eta,
        .seed = config.initialization.seed,
    };

    write_observations_header(observations_output);
    if (trajectory_output != nullptr) {
        write_trajectory_header(*trajectory_output);
    }
    RunSummary summary{};

    for (std::size_t step = 0; step <= config.steps; ++step) {
        const auto start = std::chrono::steady_clock::now();
        const NeighborSearchResult search = cell_index_neighbors(
            system,
            config.dynamics.cutoff,
            config.cells_per_side
        );
        const auto finish = std::chrono::steady_clock::now();
        const auto elapsed = std::chrono::duration_cast<
            std::chrono::nanoseconds
        >(finish - start).count();

        write_observation(
            observations_output,
            metadata,
            Observation{
                .time = system.time,
                .polarization = polarization(system),
                .largest_cluster_fraction =
                    largest_cluster_fraction(search.neighbors),
                .cim_time_ns = elapsed,
                .neighbor_pairs = search.pair_count,
                .distance_evaluations = search.distance_evaluations,
            }
        );
        ++summary.observations_written;

        if (trajectory_output != nullptr
            && step % config.trajectory_every == 0) {
            write_trajectory_frame(
                *trajectory_output,
                metadata,
                system,
                config.dynamics.speed
            );
            ++summary.frames_written;
        }

        if (step < config.steps) {
            advance(system, search.neighbors, config.dynamics, generator);
        }
    }
    return summary;
}

}  // namespace tp2
