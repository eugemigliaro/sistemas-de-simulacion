#include "tp4/forces.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>

namespace tp4 {
namespace {

// Celda propia y la mitad de las vecinas: cada par se visita una sola vez.
constexpr std::array<std::array<int, 2>, 5> half_neighborhood{{{0, 0}, {1, 0}, {-1, 1}, {0, 1}, {1, 1}}};

}  // namespace

ForceField::ForceField(const Billiard& billiard)
    : billiard_(billiard), obstacles_(obstacle_centers(billiard)) {
    validate(billiard);
    // La grilla cubre [-(R + r), R + r]: una partícula que toca la pared puede
    // tener el centro fuera de R - r.
    const double side = 2.0 * (billiard.radius + billiard.particle_radius);
    cells_per_side_ = std::max(1, static_cast<int>(side / (2.0 * billiard.particle_radius)));
    cell_size_ = side / cells_per_side_;
    cell_start_.resize(static_cast<std::size_t>(cells_per_side_ * cells_per_side_) + 1);
}

int ForceField::cell_coordinate(double coordinate) const noexcept {
    const auto cell = static_cast<int>(
        std::floor((coordinate + billiard_.radius + billiard_.particle_radius) / cell_size_));
    return std::clamp(cell, 0, cells_per_side_ - 1);
}

void ForceField::sort_into_cells(const std::vector<Particle>& particles) {
    const std::size_t n = particles.size();
    cell_of_.resize(n);
    sorted_.resize(n);
    std::fill(cell_start_.begin(), cell_start_.end(), 0U);
    for (std::size_t i = 0; i < n; ++i) {
        const Vec2& p = particles[i].position;
        if (!std::isfinite(p.x) || !std::isfinite(p.y)) {
            throw std::runtime_error("estado no finito: reducir dt");
        }
        const int cell = cell_coordinate(p.x) + cells_per_side_ * cell_coordinate(p.y);
        cell_of_[i] = static_cast<std::uint32_t>(cell);
        ++cell_start_[static_cast<std::size_t>(cell) + 1];
    }
    for (std::size_t c = 1; c < cell_start_.size(); ++c) {
        cell_start_[c] += cell_start_[c - 1];
    }
    cursor_.assign(cell_start_.begin(), cell_start_.end() - 1);
    for (std::size_t i = 0; i < n; ++i) {
        sorted_[cursor_[cell_of_[i]]++] = static_cast<std::uint32_t>(i);
    }
}

void ForceField::compute(
    const std::vector<Particle>& particles,
    std::vector<Vec2>& forces,
    std::vector<std::uint8_t>& touches_obstacle
) {
    const std::size_t n = particles.size();
    const double radius = billiard_.radius;
    const double r = billiard_.particle_radius;
    const double k = billiard_.stiffness;
    const double contact = 2.0 * r;
    const double contact_squared = contact * contact;
    forces.assign(n, Vec2{});
    touches_obstacle.assign(n, 0);

    sort_into_cells(particles);

    for (int cy = 0; cy < cells_per_side_; ++cy) {
        for (int cx = 0; cx < cells_per_side_; ++cx) {
            const auto cell = static_cast<std::size_t>(cx + cells_per_side_ * cy);
            if (cell_start_[cell] == cell_start_[cell + 1]) {
                continue;
            }
            for (const auto& [dx, dy] : half_neighborhood) {
                const int nx = cx + dx;
                const int ny = cy + dy;
                if (nx < 0 || nx >= cells_per_side_ || ny >= cells_per_side_) {
                    continue;
                }
                const auto neighbor = static_cast<std::size_t>(nx + cells_per_side_ * ny);
                for (std::uint32_t a = cell_start_[cell]; a < cell_start_[cell + 1]; ++a) {
                    const std::uint32_t i = sorted_[a];
                    const std::uint32_t first = neighbor == cell ? a + 1 : cell_start_[neighbor];
                    for (std::uint32_t b = first; b < cell_start_[neighbor + 1]; ++b) {
                        const std::uint32_t j = sorted_[b];
                        const Vec2 delta = particles[j].position - particles[i].position;
                        const double distance_squared = norm_squared(delta);
                        if (distance_squared >= contact_squared) {
                            continue;
                        }
                        if (distance_squared == 0.0) {
                            throw std::runtime_error("dos particulas en el mismo lugar");
                        }
                        const double distance = std::sqrt(distance_squared);
                        const Vec2 force = (k * (contact - distance) / distance) * delta;
                        forces[i] -= force;
                        forces[j] += force;
                    }
                }
            }
        }
    }

    const double free_squared = (radius - r) * (radius - r);
    for (std::size_t i = 0; i < n; ++i) {
        const Vec2& p = particles[i].position;
        if (!(norm_squared(p) <= free_squared)) {
            const double distance = norm(p);
            if (!std::isfinite(distance) || distance >= radius + r) {
                throw std::runtime_error("una particula atraveso la pared: reducir dt");
            }
            forces[i] -= (k * (distance + r - radius) / distance) * p;
        }
        for (const Vec2& obstacle : obstacles_) {
            const Vec2 delta = obstacle - p;
            const double distance_squared = norm_squared(delta);
            if (distance_squared >= contact_squared) {
                continue;
            }
            if (distance_squared == 0.0) {
                throw std::runtime_error("una particula en el centro de un obstaculo");
            }
            const double d = std::sqrt(distance_squared);
            forces[i] -= (k * (contact - d) / d) * delta;
            touches_obstacle[i] = 1;
        }
    }
}

}  // namespace tp4
