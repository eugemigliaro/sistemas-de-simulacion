#include "tp3/geometry.hpp"

#include <cmath>
#include <cstddef>
#include <sstream>
#include <string>
#include <stdexcept>

namespace tp3 {
namespace {

void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::invalid_argument(message);
    }
}

}  // namespace

Vec2 operator+(const Vec2& left, const Vec2& right) noexcept {
    return Vec2{.x = left.x + right.x, .y = left.y + right.y};
}

Vec2 operator-(const Vec2& left, const Vec2& right) noexcept {
    return Vec2{.x = left.x - right.x, .y = left.y - right.y};
}

Vec2 operator*(double scalar, const Vec2& vector) noexcept {
    return Vec2{.x = scalar * vector.x, .y = scalar * vector.y};
}

double dot(const Vec2& left, const Vec2& right) noexcept {
    return left.x * right.x + left.y * right.y;
}

double norm_squared(const Vec2& vector) noexcept {
    return dot(vector, vector);
}

double norm(const Vec2& vector) noexcept {
    return std::sqrt(norm_squared(vector));
}

bool is_valid(const Table& table) noexcept {
    return std::isfinite(table.length) && table.length > 0.0
        && std::isfinite(table.width) && table.width > 0.0
        && std::isfinite(table.goal_width) && table.goal_width > 0.0
        && table.goal_width <= table.width;
}

bool is_valid(const Particle& particle) noexcept {
    return std::isfinite(particle.position.x)
        && std::isfinite(particle.position.y)
        && std::isfinite(particle.velocity.x)
        && std::isfinite(particle.velocity.y)
        && std::isfinite(particle.radius) && particle.radius > 0.0
        && std::isfinite(particle.mass) && particle.mass > 0.0;
}

bool is_valid(const Obstacle& obstacle) noexcept {
    return std::isfinite(obstacle.center.x)
        && std::isfinite(obstacle.center.y)
        && std::isfinite(obstacle.radius) && obstacle.radius > 0.0;
}

double goal_lower_bound(const Table& table) noexcept {
    return 0.5 * table.width - 0.5 * table.goal_width;
}

double goal_upper_bound(const Table& table) noexcept {
    return 0.5 * table.width + 0.5 * table.goal_width;
}

bool is_on_goal(const Table& table, double y) noexcept {
    // Se compara contra las mismas cotas que expone la interfaz para que no
    // haya dos criterios distintos separados por el error de representacion.
    // El borde exacto es un caso de medida nula: con W = 0.68 y d = 0.20 el
    // valor nominal 0.24 no es representable y queda del lado de afuera.
    return y >= goal_lower_bound(table) && y <= goal_upper_bound(table);
}

bool contains(
    const Table& table,
    const Vec2& center,
    double radius
) noexcept {
    return center.x - radius >= 0.0
        && center.x + radius <= table.length
        && center.y - radius >= 0.0
        && center.y + radius <= table.width;
}

bool discs_overlap(
    const Vec2& first_center,
    double first_radius,
    const Vec2& second_center,
    double second_radius
) noexcept {
    const double sum = first_radius + second_radius;
    return norm_squared(second_center - first_center) < sum * sum;
}

void validate_obstacles(
    const Table& table,
    const std::vector<Obstacle>& obstacles,
    double particle_radius
) {
    require(is_valid(table), "la mesa tiene dimensiones invalidas");
    require(
        std::isfinite(particle_radius) && particle_radius > 0.0,
        "el radio de las particulas debe ser finito y positivo"
    );

    for (std::size_t index = 0; index < obstacles.size(); ++index) {
        const Obstacle& obstacle = obstacles[index];
        std::ostringstream prefix;
        prefix << "obstaculo " << index << ": ";

        require(is_valid(obstacle), prefix.str() + "datos no finitos o radio no positivo");
        require(
            obstacle.radius >= particle_radius,
            prefix.str() + "se exige Rk >= r"
        );
        require(
            contains(table, obstacle.center, obstacle.radius),
            prefix.str() + "no queda integramente dentro del dominio"
        );

        for (std::size_t other = 0; other < index; ++other) {
            require(
                !discs_overlap(
                    obstacle.center,
                    obstacle.radius,
                    obstacles[other].center,
                    obstacles[other].radius
                ),
                prefix.str() + "se solapa con el obstaculo "
                    + std::to_string(other)
            );
        }
    }
}

void validate_competition_obstacles(
    const Table& table,
    const std::vector<Obstacle>& obstacles,
    double particle_radius
) {
    require(
        !obstacles.empty(),
        "la configuracion de competencia exige K > 0 obstaculos"
    );
    validate_obstacles(table, obstacles, particle_radius);
}

bool is_free_placement(
    const Table& table,
    const std::vector<Obstacle>& obstacles,
    const std::vector<Particle>& placed,
    const Vec2& center,
    double radius
) noexcept {
    if (!contains(table, center, radius)) {
        return false;
    }
    for (const Obstacle& obstacle : obstacles) {
        if (discs_overlap(center, radius, obstacle.center, obstacle.radius)) {
            return false;
        }
    }
    for (const Particle& particle : placed) {
        if (discs_overlap(center, radius, particle.position, particle.radius)) {
            return false;
        }
    }
    return true;
}

}  // namespace tp3
