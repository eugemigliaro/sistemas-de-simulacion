#include "tp4/generation.hpp"

#include <cmath>
#include <numbers>
#include <random>
#include <stdexcept>
#include <string>

namespace tp4 {
namespace {

constexpr std::size_t none = static_cast<std::size_t>(-1);

// Conversión explícita a [0, 1): la secuencia depende solo de la semilla y no
// de la implementación de la biblioteca estándar.
double uniform(std::mt19937_64& rng) {
    return static_cast<double>(rng() >> 11) * 0x1.0p-53;
}

class Placement {
public:
    explicit Placement(const Billiard& billiard)
        : max_center_distance_(billiard.radius - billiard.particle_radius),
          contact_squared_(4.0 * billiard.particle_radius * billiard.particle_radius),
          obstacles_(obstacle_centers(billiard)) {}

    // Sin superposición con la pared, los obstáculos ni las partículas
    // ubicadas (salvo `skip`, la que se está moviendo).
    [[nodiscard]] bool fits(const Vec2& point, const std::vector<Particle>& placed, std::size_t skip = none) const {
        if (norm(point) > max_center_distance_) {
            return false;
        }
        for (const Vec2& obstacle : obstacles_) {
            if (norm_squared(point - obstacle) < contact_squared_) {
                return false;
            }
        }
        for (std::size_t i = 0; i < placed.size(); ++i) {
            if (i != skip && norm_squared(point - placed[i].position) < contact_squared_) {
                return false;
            }
        }
        return true;
    }

private:
    double max_center_distance_;
    double contact_squared_;
    std::vector<Vec2> obstacles_;
};

Vec2 random_velocity(double speed, std::mt19937_64& rng) {
    const double angle = 2.0 * std::numbers::pi * uniform(rng);
    return {speed * std::cos(angle), speed * std::sin(angle)};
}

std::vector<Particle> random_layout(const Billiard& billiard, const Generation& generation, std::mt19937_64& rng) {
    const Placement placement(billiard);
    const double max_distance = billiard.radius - billiard.particle_radius;
    std::vector<Particle> particles;
    particles.reserve(generation.particle_count);
    while (particles.size() < generation.particle_count) {
        Vec2 point;
        std::size_t attempts = 0;
        do {
            if (++attempts > generation.max_attempts) {
                throw std::runtime_error(
                    "el rechazo solo ubico " + std::to_string(particles.size()) + " de "
                    + std::to_string(generation.particle_count) + " particulas: usar --layout lattice");
            }
            // La raíz cuadrada hace que la posición sea uniforme en área.
            const double distance = max_distance * std::sqrt(uniform(rng));
            const double angle = 2.0 * std::numbers::pi * uniform(rng);
            point = {distance * std::cos(angle), distance * std::sin(angle)};
        } while (!placement.fits(point, particles));
        particles.push_back({point, random_velocity(billiard.initial_speed, rng), Color::Fresh});
    }
    return particles;
}

std::vector<Vec2> lattice_sites(const Billiard& billiard, std::size_t needed, std::mt19937_64& rng) {
    const Placement placement(billiard);
    const double spacing = 2.0 * billiard.particle_radius * (1.0 + 1e-6);
    const int extent = static_cast<int>(std::ceil(billiard.radius / spacing)) + 2;
    for (int attempt = 0; attempt < 100; ++attempt) {
        const double angle = 2.0 * std::numbers::pi * uniform(rng);
        const Vec2 offset{(uniform(rng) - 0.5) * spacing, (uniform(rng) - 0.5) * spacing};
        const double c = std::cos(angle);
        const double s = std::sin(angle);
        std::vector<Vec2> sites;
        for (int row = -extent; row <= extent; ++row) {
            for (int column = -extent; column <= extent; ++column) {
                const double x = (column + 0.5 * row) * spacing;
                const double y = row * spacing * std::numbers::sqrt3 / 2.0;
                const Vec2 site = Vec2{c * x - s * y, s * x + c * y} + offset;
                if (placement.fits(site, {})) {
                    sites.push_back(site);
                }
            }
        }
        if (sites.size() >= needed) {
            return sites;
        }
    }
    throw std::runtime_error("la red triangular no tiene lugar para " + std::to_string(needed) + " particulas");
}

std::vector<Particle> lattice_layout(const Billiard& billiard, const Generation& generation, std::mt19937_64& rng) {
    const std::size_t n = generation.particle_count;
    std::vector<Vec2> sites = lattice_sites(billiard, n, rng);
    for (std::size_t i = sites.size(); i > 1; --i) {
        std::swap(sites[i - 1], sites[static_cast<std::size_t>(uniform(rng) * static_cast<double>(i))]);
    }
    std::vector<Particle> particles(n);
    for (std::size_t i = 0; i < n; ++i) {
        particles[i].position = sites[i];
    }
    const Placement placement(billiard);
    const double step = 0.5 * billiard.particle_radius;
    for (std::size_t sweep = 0; sweep < generation.lattice_sweeps; ++sweep) {
        for (std::size_t trial = 0; trial < n; ++trial) {
            const auto i = static_cast<std::size_t>(uniform(rng) * static_cast<double>(n));
            const Vec2 moved = particles[i].position
                + Vec2{(2.0 * uniform(rng) - 1.0) * step, (2.0 * uniform(rng) - 1.0) * step};
            if (placement.fits(moved, particles, i)) {
                particles[i].position = moved;
            }
        }
    }
    for (Particle& particle : particles) {
        particle.velocity = random_velocity(billiard.initial_speed, rng);
    }
    return particles;
}

}  // namespace

Layout parse_layout(std::string_view name) {
    if (name == "random") return Layout::Random;
    if (name == "lattice") return Layout::Lattice;
    throw std::invalid_argument("layout desconocido: " + std::string(name));
}

std::string_view to_string(Layout layout) noexcept {
    return layout == Layout::Random ? "random" : "lattice";
}

std::vector<Particle> generate(const Billiard& billiard, const Generation& generation) {
    validate(billiard);
    if (generation.particle_count == 0) {
        throw std::invalid_argument("se necesita al menos una particula");
    }
    std::mt19937_64 rng(generation.seed);
    return generation.layout == Layout::Random
        ? random_layout(billiard, generation, rng)
        : lattice_layout(billiard, generation, rng);
}

}  // namespace tp4
