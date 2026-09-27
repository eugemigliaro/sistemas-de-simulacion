#include "tp3/generation.hpp"

#include <algorithm>
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

// Sitios de una red triangular de paso `spacing`, centrada en el dominio
// reducido que pueden ocupar los centros, descartando los que tocan un
// obstaculo.
std::vector<Vec2> triangular_sites(
    const Table& table,
    const std::vector<Obstacle>& obstacles,
    double radius,
    double spacing
) {
    const double span_x = table.length - 2.0 * radius;
    const double span_y = table.width - 2.0 * radius;
    const double row_height = spacing * std::sqrt(3.0) / 2.0;
    const auto rows = static_cast<std::size_t>(std::floor(span_y / row_height)) + 1;
    const auto even = static_cast<std::size_t>(std::floor(span_x / spacing)) + 1;
    const std::size_t odd = span_x >= spacing / 2.0
        ? static_cast<std::size_t>(std::floor((span_x - spacing / 2.0) / spacing)) + 1
        : 0;

    const double extent_x = std::max(
        static_cast<double>(even - 1) * spacing,
        odd == 0 ? 0.0 : spacing / 2.0 + static_cast<double>(odd - 1) * spacing
    );
    const double origin_x = radius + (span_x - extent_x) / 2.0;
    const double origin_y =
        radius + (span_y - static_cast<double>(rows - 1) * row_height) / 2.0;

    std::vector<Vec2> sites;
    for (std::size_t row = 0; row < rows; ++row) {
        const bool shifted = row % 2 == 1;
        const std::size_t columns = shifted ? odd : even;
        for (std::size_t column = 0; column < columns; ++column) {
            const Vec2 site{
                .x = origin_x + (shifted ? spacing / 2.0 : 0.0)
                    + static_cast<double>(column) * spacing,
                .y = origin_y + static_cast<double>(row) * row_height,
            };
            if (is_free_placement(table, obstacles, {}, site, radius)) {
                sites.push_back(site);
            }
        }
    }
    return sites;
}

// Red mas espaciada con al menos `count` sitios libres. La cantidad de sitios
// decrece con el paso, asi que se busca por biseccion manteniendo el invariante
// de que el extremo inferior siempre alcanza.
std::vector<Vec2> sparsest_triangular_sites(
    const Table& table,
    const std::vector<Obstacle>& obstacles,
    double radius,
    std::size_t count
) {
    // Un margen relativo minimo evita que el redondeo haga solapar a dos
    // vecinas que en aritmetica exacta solo se tocan.
    double low = 2.0 * radius * (1.0 + 1e-9);
    if (triangular_sites(table, obstacles, radius, low).size() < count) {
        std::ostringstream message;
        message << "no entran " << count
                << " particulas ni siquiera en la red triangular compacta";
        throw std::runtime_error(message.str());
    }
    double high = std::max(table.length, table.width);
    for (int iteration = 0; iteration < 200; ++iteration) {
        const double middle = 0.5 * (low + high);
        if (triangular_sites(table, obstacles, radius, middle).size() >= count) {
            low = middle;
        } else {
            high = middle;
        }
    }
    return triangular_sites(table, obstacles, radius, low);
}

Particle fresh_particle(
    std::size_t id,
    const Vec2& position,
    double angle,
    const InitializationConfig& config
) {
    return Particle{
        .id = id,
        .position = position,
        .velocity = {
            .x = config.initial_speed * std::cos(angle),
            .y = config.initial_speed * std::sin(angle),
        },
        .radius = config.particle_radius,
        .mass = config.particle_mass,
        .state = ParticleState::Fresh,
        .collision_count = 0,
    };
}

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

    if (config.layout == Layout::Triangular) {
        std::vector<Vec2> sites = sparsest_triangular_sites(
            config.table, obstacles, radius, config.particle_count
        );
        std::shuffle(sites.begin(), sites.end(), generator);
        for (std::size_t index = 0; index < config.particle_count; ++index) {
            system.particles.push_back(
                fresh_particle(index, sites[index], angle_distribution(generator), config)
            );
        }
        return system;
    }

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

            system.particles.push_back(
                fresh_particle(index, candidate, angle_distribution(generator), config)
            );
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
