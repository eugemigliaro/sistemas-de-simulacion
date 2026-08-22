#include "tp2/observables.hpp"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <vector>

#include "tp2/geometry.hpp"

namespace tp2 {
namespace {

class DisjointSet {
public:
    explicit DisjointSet(std::size_t size)
        : parent_(size), component_size_(size, 1) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    std::size_t find(std::size_t item) {
        if (parent_[item] != item) {
            parent_[item] = find(parent_[item]);
        }
        return parent_[item];
    }

    void unite(std::size_t first, std::size_t second) {
        first = find(first);
        second = find(second);
        if (first == second) {
            return;
        }
        if (component_size_[first] < component_size_[second]) {
            std::swap(first, second);
        }
        parent_[second] = first;
        component_size_[first] += component_size_[second];
    }

    std::size_t size(std::size_t item) {
        return component_size_[find(item)];
    }

private:
    std::vector<std::size_t> parent_;
    std::vector<std::size_t> component_size_;
};

}  // namespace

double polarization(const System& system) {
    if (!is_valid(system) || system.particles.empty()) {
        throw std::invalid_argument{"polarization requires a non-empty system"};
    }

    double sum_x = 0.0;
    double sum_y = 0.0;
    for (const Particle& particle : system.particles) {
        sum_x += std::cos(particle.angle);
        sum_y += std::sin(particle.angle);
    }
    return std::hypot(sum_x, sum_y)
        / static_cast<double>(system.particles.size());
}

double largest_cluster_fraction(const NeighborList& neighbors) {
    if (neighbors.empty()) {
        throw std::invalid_argument{"S requires at least one particle"};
    }
    if (!is_valid_neighbor_list(neighbors)) {
        throw std::invalid_argument{"invalid neighbor list"};
    }

    DisjointSet components{neighbors.size()};
    for (std::size_t first = 0; first < neighbors.size(); ++first) {
        for (std::size_t second : neighbors[first]) {
            if (first < second) {
                components.unite(first, second);
            }
        }
    }

    std::size_t largest = 1;
    for (std::size_t index = 0; index < neighbors.size(); ++index) {
        largest = std::max(largest, components.size(index));
    }
    return static_cast<double>(largest)
        / static_cast<double>(neighbors.size());
}

}  // namespace tp2
