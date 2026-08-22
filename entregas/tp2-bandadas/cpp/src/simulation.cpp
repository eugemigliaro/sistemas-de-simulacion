#include "tp2/simulation.hpp"

#include <cmath>
#include <numbers>
#include <stdexcept>

#include "tp2/geometry.hpp"

namespace tp2 {
namespace {

double aligned_angle(
    const System& system,
    const NeighborList& neighbors,
    std::size_t particle_index
) {
    double sum_x = std::cos(system.particles[particle_index].angle);
    double sum_y = std::sin(system.particles[particle_index].angle);
    for (std::size_t neighbor : neighbors[particle_index]) {
        sum_x += std::cos(system.particles[neighbor].angle);
        sum_y += std::sin(system.particles[neighbor].angle);
    }
    if (std::hypot(sum_x, sum_y) <= 1e-12) {
        return system.particles[particle_index].angle;
    }
    return std::atan2(sum_y, sum_x);
}

double copied_angle(
    const System& system,
    const NeighborList& neighbors,
    std::size_t particle_index,
    std::mt19937_64& generator
) {
    const std::size_t geometric_count = neighbors[particle_index].size();
    std::uniform_int_distribution<std::size_t> choice{
        0,
        geometric_count,
    };
    const std::size_t selected = choice(generator);
    if (selected == geometric_count) {
        return system.particles[particle_index].angle;
    }
    return system.particles[neighbors[particle_index][selected]].angle;
}

}  // namespace

bool is_valid(const DynamicsConfig& config) noexcept {
    const bool known_model = config.model == AlignmentModel::Vicsek
        || config.model == AlignmentModel::Voter;
    return known_model
        && std::isfinite(config.cutoff) && config.cutoff > 0.0
        && std::isfinite(config.speed) && config.speed > 0.0
        && std::isfinite(config.time_step) && config.time_step > 0.0
        && std::isfinite(config.eta)
        && config.eta >= 0.0 && config.eta <= 1.0;
}

bool is_valid(const InitializationConfig& config) noexcept {
    return config.particle_count > 0
        && std::isfinite(config.side) && config.side > 0.0;
}

System generate_system(const InitializationConfig& config) {
    std::mt19937_64 generator{config.seed};
    return generate_system(config, generator);
}

System generate_system(
    const InitializationConfig& config,
    std::mt19937_64& generator
) {
    if (!is_valid(config)) {
        throw std::invalid_argument{"invalid initialization configuration"};
    }

    std::uniform_real_distribution<double> position{0.0, config.side};
    std::uniform_real_distribution<double> angle{
        -std::numbers::pi_v<double>,
        std::numbers::pi_v<double>,
    };

    System system{
        .side = config.side,
        .time = 0.0,
    };
    system.particles.reserve(config.particle_count);
    for (std::size_t index = 0; index < config.particle_count; ++index) {
        system.particles.push_back(Particle{
            .id = index + 1,
            .position = {
                .x = position(generator),
                .y = position(generator),
            },
            .angle = angle(generator),
        });
    }
    return system;
}

void advance(
    System& system,
    const NeighborList& neighbors,
    const DynamicsConfig& config,
    std::mt19937_64& generator
) {
    if (!is_valid(system) || !is_valid(config)) {
        throw std::invalid_argument{"invalid system or dynamics configuration"};
    }
    if (neighbors.size() != system.particles.size()
        || !is_valid_neighbor_list(neighbors)) {
        throw std::invalid_argument{"invalid neighbor list"};
    }

    const double noise_amplitude = config.eta
        * std::numbers::pi_v<double>;
    std::uniform_real_distribution<double> noise{
        -noise_amplitude,
        noise_amplitude,
    };

    std::vector<Particle> next = system.particles;
    for (std::size_t index = 0; index < system.particles.size(); ++index) {
        const Particle& current = system.particles[index];
        next[index].position.x = wrap_coordinate(
            current.position.x
                + config.speed * std::cos(current.angle)
                    * config.time_step,
            system.side
        );
        next[index].position.y = wrap_coordinate(
            current.position.y
                + config.speed * std::sin(current.angle)
                    * config.time_step,
            system.side
        );

        const double base_angle = config.model == AlignmentModel::Vicsek
            ? aligned_angle(system, neighbors, index)
            : copied_angle(system, neighbors, index, generator);
        next[index].angle = normalize_angle(base_angle + noise(generator));
    }

    system.particles = std::move(next);
    system.time += config.time_step;
}

}  // namespace tp2
