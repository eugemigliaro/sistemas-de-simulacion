#include "tp3/generation.hpp"

#include <cmath>
#include <numbers>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>

#include "tp3/geometry.hpp"

namespace tp3 {
namespace {

constexpr double two_pi = 2.0 * std::numbers::pi_v<double>;

}  // namespace

System generate_system(
    const InitializationConfig& config,
    const std::vector<Obstacle>& obstacles
) {
    if (!is_valid(config.table)) {
        throw std::invalid_argument("la mesa tiene dimensiones invalidas");
    }
    if (!std::isfinite(config.particle_radius) || config.particle_radius <= 0.0) {
        throw std::invalid_argument(
            "el radio de las particulas debe ser finito y positivo"
        );
    }
    if (!std::isfinite(config.particle_mass) || config.particle_mass <= 0.0) {
        throw std::invalid_argument(
            "la masa de las particulas debe ser finita y positiva"
        );
    }
    if (!std::isfinite(config.initial_speed) || config.initial_speed < 0.0) {
        throw std::invalid_argument(
            "la rapidez inicial debe ser finita y no negativa"
        );
    }
    if (config.max_placement_attempts == 0) {
        throw std::invalid_argument(
            "el tope de intentos de ubicacion debe ser positivo"
        );
    }

    validate_obstacles(config.table, obstacles, config.particle_radius);

    const double radius = config.particle_radius;
    if (2.0 * radius > config.table.length || 2.0 * radius > config.table.width) {
        throw std::invalid_argument(
            "una particula no entra en el dominio"
        );
    }

    System system{};
    system.table = config.table;
    system.time = 0.0;
    system.obstacles = obstacles;
    system.particles.reserve(config.particle_count);

    std::mt19937_64 generator(config.seed);
    // El centro de una particula solo puede caer en el dominio reducido: la
    // consigna pide posiciones a azar en toda el area disponible [TP03, p. 3].
    std::uniform_real_distribution<double> x_distribution(
        radius,
        config.table.length - radius
    );
    std::uniform_real_distribution<double> y_distribution(
        radius,
        config.table.width - radius
    );
    std::uniform_real_distribution<double> angle_distribution(0.0, two_pi);

    for (std::size_t index = 0; index < config.particle_count; ++index) {
        bool placed = false;

        for (std::size_t attempt = 0;
             attempt < config.max_placement_attempts;
             ++attempt) {
            const Vec2 candidate{
                .x = x_distribution(generator),
                .y = y_distribution(generator),
            };

            if (!is_free_placement(
                    config.table,
                    obstacles,
                    system.particles,
                    candidate,
                    radius
                )) {
                continue;
            }

            const double angle = angle_distribution(generator);
            system.particles.push_back(Particle{
                .id = index,
                .position = candidate,
                .velocity = {
                    .x = config.initial_speed * std::cos(angle),
                    .y = config.initial_speed * std::sin(angle),
                },
                .radius = radius,
                .mass = config.particle_mass,
                .state = ParticleState::Fresh,
                .collision_count = 0,
            });
            placed = true;
            break;
        }

        if (!placed) {
            std::ostringstream message;
            message << "no se pudo ubicar la particula " << index
                    << " de " << config.particle_count
                    << " tras " << config.max_placement_attempts
                    << " intentos: la configuracion no permite generar las N"
                       " particulas (restriccion ii del punto 1.2)";
            throw std::runtime_error(message.str());
        }
    }

    return system;
}

}  // namespace tp3
