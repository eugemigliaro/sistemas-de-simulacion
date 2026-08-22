#include "tp2/neighbors.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <stdexcept>

#include "tp2/geometry.hpp"

namespace tp2 {
namespace {

void require_searchable(const System& system, double cutoff) {
    if (!is_valid(system)) {
        throw std::invalid_argument{"invalid system"};
    }
    if (!std::isfinite(cutoff) || cutoff < 0.0) {
        throw std::invalid_argument{"cutoff must be finite and non-negative"};
    }
}

void require_cell_count(
    const System& system,
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
    if (cells_per_side > 1
        && !(system.side / static_cast<double>(cells_per_side) > cutoff)) {
        throw std::invalid_argument{"L/M must be greater than rc"};
    }
}

std::size_t cell_coordinate(
    double position,
    double cell_side,
    std::size_t cells_per_side
) noexcept {
    const auto coordinate = static_cast<std::size_t>(
        std::floor(position / cell_side)
    );
    return std::min(coordinate, cells_per_side - 1);
}

std::size_t shifted_periodic(
    std::size_t coordinate,
    int shift,
    std::size_t cells_per_side
) noexcept {
    if (shift < 0) {
        return coordinate == 0 ? cells_per_side - 1 : coordinate - 1;
    }
    if (shift > 0) {
        return coordinate + 1 == cells_per_side ? 0 : coordinate + 1;
    }
    return coordinate;
}

void evaluate_pair(
    const System& system,
    double cutoff,
    std::size_t first,
    std::size_t second,
    NeighborSearchResult& result
) {
    ++result.distance_evaluations;
    if (are_neighbors(
            system.particles[first],
            system.particles[second],
            system.side,
            cutoff
        )) {
        result.neighbors[first].push_back(second);
        result.neighbors[second].push_back(first);
        ++result.pair_count;
    }
}

}  // namespace

NeighborSearchResult brute_force_neighbors(
    const System& system,
    double cutoff
) {
    require_searchable(system, cutoff);
    NeighborSearchResult result{
        .neighbors = NeighborList(system.particles.size()),
    };

    for (std::size_t first = 0; first < system.particles.size(); ++first) {
        for (std::size_t second = first + 1;
             second < system.particles.size(); ++second) {
            evaluate_pair(system, cutoff, first, second, result);
        }
    }
    return result;
}

NeighborSearchResult cell_index_neighbors(
    const System& system,
    double cutoff,
    std::size_t cells_per_side
) {
    require_searchable(system, cutoff);
    require_cell_count(system, cutoff, cells_per_side);

    const std::size_t cell_count = cells_per_side * cells_per_side;
    const double cell_side = system.side
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
    };

    for (std::size_t cell_id = 0; cell_id < cell_count; ++cell_id) {
        const auto& own = cells[cell_id];
        for (std::size_t first = 0; first < own.size(); ++first) {
            for (std::size_t second = first + 1;
                 second < own.size(); ++second) {
                evaluate_pair(
                    system,
                    cutoff,
                    own[first],
                    own[second],
                    result
                );
            }
        }

        const std::size_t row = cell_id / cells_per_side;
        const std::size_t column = cell_id % cells_per_side;
        std::array<std::size_t, 8> adjacent{};
        std::size_t adjacent_count = 0;

        for (int row_shift = -1; row_shift <= 1; ++row_shift) {
            for (int column_shift = -1; column_shift <= 1; ++column_shift) {
                if (row_shift == 0 && column_shift == 0) {
                    continue;
                }
                const std::size_t adjacent_row = shifted_periodic(
                    row,
                    row_shift,
                    cells_per_side
                );
                const std::size_t adjacent_column = shifted_periodic(
                    column,
                    column_shift,
                    cells_per_side
                );
                const std::size_t adjacent_id =
                    adjacent_row * cells_per_side + adjacent_column;
                if (adjacent_id <= cell_id
                    || std::find(
                        adjacent.begin(),
                        adjacent.begin() + adjacent_count,
                        adjacent_id
                    ) != adjacent.begin() + adjacent_count) {
                    continue;
                }
                adjacent[adjacent_count++] = adjacent_id;
            }
        }

        for (std::size_t adjacent_index = 0;
             adjacent_index < adjacent_count; ++adjacent_index) {
            const auto& other = cells[adjacent[adjacent_index]];
            for (std::size_t first : own) {
                for (std::size_t second : other) {
                    evaluate_pair(system, cutoff, first, second, result);
                }
            }
        }
    }

    for (auto& particle_neighbors : result.neighbors) {
        std::sort(particle_neighbors.begin(), particle_neighbors.end());
    }
    return result;
}

std::size_t maximum_valid_cells_per_side(
    const System& system,
    double cutoff
) {
    require_searchable(system, cutoff);
    if (cutoff == 0.0 || !(system.side > cutoff)) {
        return 1;
    }
    std::size_t candidate = static_cast<std::size_t>(
        std::floor(system.side / cutoff)
    );
    candidate = std::max<std::size_t>(candidate, 1);
    while (candidate > 1
           && !(system.side / static_cast<double>(candidate) > cutoff)) {
        --candidate;
    }
    return candidate;
}

bool is_valid_neighbor_list(const NeighborList& neighbors) noexcept {
    for (std::size_t index = 0; index < neighbors.size(); ++index) {
        const auto& list = neighbors[index];
        if (!std::is_sorted(list.begin(), list.end())
            || std::adjacent_find(list.begin(), list.end()) != list.end()) {
            return false;
        }
        for (std::size_t neighbor : list) {
            if (neighbor >= neighbors.size() || neighbor == index
                || !std::binary_search(
                    neighbors[neighbor].begin(),
                    neighbors[neighbor].end(),
                    index
                )) {
                return false;
            }
        }
    }
    return true;
}

}  // namespace tp2
