#include "tp1/neighbors.hpp"

#include <algorithm>
#include <cmath>
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
            ++result.distance_evaluations;
            if (are_neighbors(
                    system.particles[first],
                    system.particles[second],
                    system.domain,
                    cutoff
                )) {
                result.neighbors[first].push_back(second + 1);
                result.neighbors[second].push_back(first + 1);
                ++result.pair_count;
            }
        }
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
