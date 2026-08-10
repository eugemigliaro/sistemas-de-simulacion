#include "tp1/generation.hpp"

#include <cmath>
#include <random>
#include <stdexcept>

#include "tp1/geometry.hpp"

namespace tp1 {
namespace {

bool overlaps_any(
    const Particle& candidate,
    const std::vector<Particle>& particles,
    const Domain& domain
) {
    for (const Particle& particle : particles) {
        if (edge_distance(candidate, particle, domain) < 0.0) {
            return true;
        }
    }
    return false;
}

}  // namespace

bool is_valid(const GenerationConfig& config) noexcept {
    return config.particle_count > 0
        && is_valid(config.domain)
        && std::isfinite(config.min_radius)
        && std::isfinite(config.max_radius)
        && config.min_radius > 0.0
        && config.max_radius >= config.min_radius
        && config.max_radius <= config.domain.side / 2.0
        && std::isfinite(config.property)
        && config.max_attempts_per_particle > 0;
}

ParticleSystem generate_system(const GenerationConfig& config) {
    if (!is_valid(config)) {
        throw std::invalid_argument{"invalid generation configuration"};
    }

    ParticleSystem result{
        .domain = config.domain,
        .time = 0.0,
        .particles = {},
    };
    result.particles.reserve(config.particle_count);

    std::mt19937_64 engine{config.seed};
    std::uniform_real_distribution<double> radius_distribution{
        config.min_radius,
        config.max_radius
    };
    for (std::size_t index = 0; index < config.particle_count; ++index) {
        const double radius = radius_distribution(engine);
        bool placed = false;

        for (std::size_t attempt = 0;
             attempt < config.max_attempts_per_particle;
             ++attempt) {
            std::uniform_real_distribution<double> position_distribution{
                radius,
                config.domain.side - radius
            };
            const Vec2 position{
                .x = position_distribution(engine),
                .y = position_distribution(engine),
            };

            Particle candidate{
                .id = index + 1,
                .position = position,
                .velocity = {.x = 0.0, .y = 0.0},
                .radius = radius,
                .property = config.property,
            };

            if (!overlaps_any(candidate, result.particles, config.domain)) {
                result.particles.push_back(candidate);
                placed = true;
                break;
            }
        }

        if (!placed) {
            throw std::runtime_error{
                "could not place every particle without overlaps; "
                "increase the domain or the attempt limit"
            };
        }
    }

    return result;
}

bool has_overlaps(const ParticleSystem& system) {
    if (!is_valid(system.domain)) {
        throw std::invalid_argument{"invalid domain"};
    }

    for (std::size_t first = 0; first < system.particles.size(); ++first) {
        if (!is_valid(system.particles[first])) {
            throw std::invalid_argument{"invalid particle"};
        }
        for (std::size_t second = first + 1;
             second < system.particles.size();
             ++second) {
            if (edge_distance(
                    system.particles[first],
                    system.particles[second],
                    system.domain
                ) < 0.0) {
                return true;
            }
        }
    }
    return false;
}

}  // namespace tp1
