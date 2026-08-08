#include "tp1/neighbors.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <stdexcept>

#include "tp1/geometry.hpp"

namespace tp1 {
namespace {

void require_searchable_system(const ParticleSystem& system) {
    if (!is_valid(system.domain) || !std::isfinite(system.time)) {
        throw std::invalid_argument{"invalid particle system"};
    }

    for (std::size_t index = 0; index < system.particles.size(); ++index) {
        const Particle& particle = system.particles[index];
        if (!is_valid(particle) || particle.id != index + 1
            || !is_inside_domain(particle, system.domain)) {
            throw std::invalid_argument{"invalid particle system"};
        }
    }
}

double maximum_radius(const ParticleSystem& system) noexcept {
    double result = 0.0;
    for (const Particle& particle : system.particles) {
        result = std::max(result, particle.radius);
    }
    return result;
}

void require_valid_cell_count(
    const ParticleSystem& system,
    double cutoff,
    std::size_t cells_per_side
) {
    if (cells_per_side == 0) {
        throw std::invalid_argument{"M must be positive"};
    }
    if (cells_per_side
        > std::numeric_limits<std::size_t>::max() / cells_per_side) {
        throw std::invalid_argument{"M is too large"};
    }
    if (cells_per_side == 1) {
        return;
    }

    const double interaction_reach = cutoff
        + 2.0 * maximum_radius(system);
    const double cell_side = system.domain.side
        / static_cast<double>(cells_per_side);
    if (!std::isfinite(interaction_reach)
        || !std::isfinite(cell_side)
        || !(cell_side > interaction_reach)) {
        throw std::invalid_argument{
            "L/M must be greater than rc + 2*r_max"
        };
    }
}

std::size_t cell_coordinate(
    double position,
    double cell_side,
    std::size_t cells_per_side
) noexcept {
    const std::size_t coordinate = static_cast<std::size_t>(
        std::floor(position / cell_side)
    );
    return std::min(coordinate, cells_per_side - 1);
}

bool shifted_coordinate(
    std::size_t coordinate,
    int shift,
    std::size_t cells_per_side,
    BoundaryCondition boundary,
    std::size_t& result
) noexcept {
    if (shift == -1) {
        if (coordinate > 0) {
            result = coordinate - 1;
            return true;
        }
        if (boundary == BoundaryCondition::Periodic) {
            result = cells_per_side - 1;
            return true;
        }
        return false;
    }

    if (shift == 1) {
        if (coordinate + 1 < cells_per_side) {
            result = coordinate + 1;
            return true;
        }
        if (boundary == BoundaryCondition::Periodic) {
            result = 0;
            return true;
        }
        return false;
    }

    result = coordinate;
    return true;
}

void evaluate_pair(
    const ParticleSystem& system,
    double cutoff,
    std::size_t first,
    std::size_t second,
    NeighborSearchResult& result
) {
    ++result.distance_evaluations;
    if (are_neighbors(
            system.particles[first],
            system.particles[second],
            system.domain,
            cutoff
        )) {
        result.neighbors[first].push_back(system.particles[second].id);
        result.neighbors[second].push_back(system.particles[first].id);
        ++result.pair_count;
    }
}

}  // namespace

NeighborSearchResult brute_force_neighbors(
    const ParticleSystem& system,
    double cutoff
) {
    if (!std::isfinite(cutoff) || cutoff < 0.0) {
        throw std::invalid_argument{
            "cutoff must be finite and non-negative"
        };
    }
    require_searchable_system(system);

    NeighborSearchResult result{
        .neighbors = NeighborList(system.particles.size()),
        .pair_count = 0,
        .distance_evaluations = 0,
    };

    for (std::size_t first = 0; first < system.particles.size(); ++first) {
        for (std::size_t second = first + 1;
             second < system.particles.size();
             ++second) {
            evaluate_pair(system, cutoff, first, second, result);
        }
    }

    return result;
}

NeighborSearchResult cell_index_neighbors(
    const ParticleSystem& system,
    double cutoff,
    std::size_t cells_per_side
) {
    if (!std::isfinite(cutoff) || cutoff < 0.0) {
        throw std::invalid_argument{
            "cutoff must be finite and non-negative"
        };
    }
    require_searchable_system(system);
    require_valid_cell_count(system, cutoff, cells_per_side);

    const std::size_t cell_count = cells_per_side * cells_per_side;
    const double cell_side = system.domain.side
        / static_cast<double>(cells_per_side);
    std::vector<std::vector<std::size_t>> cells(cell_count);

    for (std::size_t index = 0; index < system.particles.size(); ++index) {
        const Particle& particle = system.particles[index];
        const std::size_t column = cell_coordinate(
            particle.position.x,
            cell_side,
            cells_per_side
        );
        const std::size_t row = cell_coordinate(
            particle.position.y,
            cell_side,
            cells_per_side
        );
        cells[row * cells_per_side + column].push_back(index);
    }

    NeighborSearchResult result{
        .neighbors = NeighborList(system.particles.size()),
        .pair_count = 0,
        .distance_evaluations = 0,
    };

    for (std::size_t cell_id = 0; cell_id < cell_count; ++cell_id) {
        const std::vector<std::size_t>& own_particles = cells[cell_id];
        for (std::size_t first = 0; first < own_particles.size(); ++first) {
            for (std::size_t second = first + 1;
                 second < own_particles.size();
                 ++second) {
                evaluate_pair(
                    system,
                    cutoff,
                    own_particles[first],
                    own_particles[second],
                    result
                );
            }
        }

        const std::size_t row = cell_id / cells_per_side;
        const std::size_t column = cell_id % cells_per_side;
        std::array<std::size_t, 8> adjacent_cells{};
        std::size_t adjacent_count = 0;

        for (int row_shift = -1; row_shift <= 1; ++row_shift) {
            for (int column_shift = -1;
                 column_shift <= 1;
                 ++column_shift) {
                if (row_shift == 0 && column_shift == 0) {
                    continue;
                }

                std::size_t adjacent_row{};
                std::size_t adjacent_column{};
                if (!shifted_coordinate(
                        row,
                        row_shift,
                        cells_per_side,
                        system.domain.boundary,
                        adjacent_row
                    )
                    || !shifted_coordinate(
                        column,
                        column_shift,
                        cells_per_side,
                        system.domain.boundary,
                        adjacent_column
                    )) {
                    continue;
                }

                const std::size_t adjacent_id =
                    adjacent_row * cells_per_side + adjacent_column;
                if (adjacent_id <= cell_id
                    || std::find(
                        adjacent_cells.begin(),
                        adjacent_cells.begin() + adjacent_count,
                        adjacent_id
                    ) != adjacent_cells.begin() + adjacent_count) {
                    continue;
                }
                adjacent_cells[adjacent_count] = adjacent_id;
                ++adjacent_count;
            }
        }

        for (std::size_t adjacent_index = 0;
             adjacent_index < adjacent_count;
             ++adjacent_index) {
            const std::vector<std::size_t>& other_particles =
                cells[adjacent_cells[adjacent_index]];
            for (std::size_t first : own_particles) {
                for (std::size_t second : other_particles) {
                    evaluate_pair(system, cutoff, first, second, result);
                }
            }
        }
    }

    for (std::vector<std::size_t>& particle_neighbors : result.neighbors) {
        std::sort(particle_neighbors.begin(), particle_neighbors.end());
    }
    return result;
}

bool is_valid_neighbor_list(const NeighborList& neighbors) noexcept {
    for (std::size_t index = 0; index < neighbors.size(); ++index) {
        const std::vector<std::size_t>& particle_neighbors = neighbors[index];
        if (!std::is_sorted(
                particle_neighbors.begin(),
                particle_neighbors.end()
            )
            || std::adjacent_find(
                particle_neighbors.begin(),
                particle_neighbors.end()
            ) != particle_neighbors.end()) {
            return false;
        }

        const std::size_t particle_id = index + 1;
        for (std::size_t neighbor_id : particle_neighbors) {
            if (neighbor_id == 0 || neighbor_id > neighbors.size()
                || neighbor_id == particle_id) {
                return false;
            }
        }
    }

    for (std::size_t index = 0; index < neighbors.size(); ++index) {
        const std::size_t particle_id = index + 1;
        for (std::size_t neighbor_id : neighbors[index]) {
            const std::vector<std::size_t>& reverse =
                neighbors[neighbor_id - 1];
            if (!std::binary_search(
                    reverse.begin(),
                    reverse.end(),
                    particle_id
                )) {
                return false;
            }
        }
    }
    return true;
}

std::size_t count_neighbor_pairs(const NeighborList& neighbors) {
    if (!is_valid_neighbor_list(neighbors)) {
        throw std::invalid_argument{"invalid neighbor list"};
    }

    std::size_t pair_count = 0;
    for (std::size_t index = 0; index < neighbors.size(); ++index) {
        const std::size_t particle_id = index + 1;
        for (std::size_t neighbor_id : neighbors[index]) {
            if (neighbor_id > particle_id) {
                ++pair_count;
            }
        }
    }
    return pair_count;
}

}  // namespace tp1
