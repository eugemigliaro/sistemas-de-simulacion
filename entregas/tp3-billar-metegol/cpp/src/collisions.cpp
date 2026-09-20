#include "tp3/collisions.hpp"

#include <cmath>

#include "tp3/geometry.hpp"

namespace tp3 {
namespace {

// Descarta tiempos negativos, NaN e infinitos negativos con una sola
// comparacion. El cero se acepta: ver la nota sobre esquinas en el header.
[[nodiscard]] double keep_future(double time) noexcept {
    return (time >= 0.0) ? time : no_collision;
}

}  // namespace

WallPrediction predict_wall_collision(
    const Table& table,
    const Particle& particle
) noexcept {
    const double radius = particle.radius;

    double short_time = no_collision;
    if (particle.velocity.x > 0.0) {
        short_time = (table.length - radius - particle.position.x)
            / particle.velocity.x;
    } else if (particle.velocity.x < 0.0) {
        short_time = (radius - particle.position.x) / particle.velocity.x;
    }
    short_time = keep_future(short_time);

    double long_time = no_collision;
    if (particle.velocity.y > 0.0) {
        long_time = (table.width - radius - particle.position.y)
            / particle.velocity.y;
    } else if (particle.velocity.y < 0.0) {
        long_time = (radius - particle.position.y) / particle.velocity.y;
    }
    long_time = keep_future(long_time);

    // Ante un empate exacto, que es el choque de esquina, se resuelve primero
    // la pared corta. La larga queda predicha a tiempo cero y se resuelve en el
    // evento siguiente, de modo que el rebote invierte ambas componentes.
    if (short_time <= long_time) {
        const double contact_y = particle.position.y
            + particle.velocity.y * short_time;
        return WallPrediction{
            .time = short_time,
            .kind = WallKind::Short,
            .on_goal = std::isfinite(short_time)
                && is_on_goal(table, contact_y),
        };
    }

    return WallPrediction{
        .time = long_time,
        .kind = WallKind::Long,
        .on_goal = false,
    };
}

double predict_disc_collision(
    const Vec2& first_position,
    const Vec2& first_velocity,
    double first_radius,
    const Vec2& second_position,
    const Vec2& second_velocity,
    double second_radius
) noexcept {
    const Vec2 relative_position = second_position - first_position;
    const Vec2 relative_velocity = second_velocity - first_velocity;

    const double approach = dot(relative_velocity, relative_position);
    if (!(approach < 0.0)) {
        return no_collision;  // se alejan, van paralelos o ya se tocaron
    }

    const double speed_squared = norm_squared(relative_velocity);
    if (speed_squared <= 0.0) {
        return no_collision;
    }

    const double sigma = first_radius + second_radius;
    const double gap = norm_squared(relative_position) - sigma * sigma;
    const double discriminant = approach * approach - speed_squared * gap;
    if (discriminant < 0.0) {
        return no_collision;  // pasan de largo sin tocarse
    }

    return keep_future(
        -(approach + std::sqrt(discriminant)) / speed_squared
    );
}

double predict_particle_collision(
    const Particle& first,
    const Particle& second
) noexcept {
    return predict_disc_collision(
        first.position, first.velocity, first.radius,
        second.position, second.velocity, second.radius
    );
}

double predict_obstacle_collision(
    const Particle& particle,
    const Obstacle& obstacle
) noexcept {
    return predict_disc_collision(
        particle.position, particle.velocity, particle.radius,
        obstacle.center, Vec2{}, obstacle.radius
    );
}

Vec2 resolve_wall_collision(const Vec2& velocity, WallKind kind) noexcept {
    if (kind == WallKind::Short) {
        return Vec2{.x = -velocity.x, .y = velocity.y};
    }
    return Vec2{.x = velocity.x, .y = -velocity.y};
}

VelocityPair resolve_particle_collision(
    const Particle& first,
    const Particle& second
) noexcept {
    const Vec2 relative_position = second.position - first.position;
    const Vec2 relative_velocity = second.velocity - first.velocity;
    const double sigma = first.radius + second.radius;

    const double impulse = 2.0 * first.mass * second.mass
        * dot(relative_velocity, relative_position)
        / (sigma * (first.mass + second.mass));

    const Vec2 impulse_vector = (impulse / sigma) * relative_position;

    return VelocityPair{
        .first = first.velocity + (1.0 / first.mass) * impulse_vector,
        .second = second.velocity + (-1.0 / second.mass) * impulse_vector,
    };
}

Vec2 resolve_obstacle_collision(
    const Particle& particle,
    const Obstacle& obstacle
) noexcept {
    const Vec2 relative_position = obstacle.center - particle.position;
    const double sigma = particle.radius + obstacle.radius;

    // Limite mj -> infinito: el factor 2 mi mj / (mi + mj) tiende a 2 mi y la
    // masa se cancela contra el 1/mi de la actualizacion.
    const double factor = 2.0 * dot(particle.velocity, relative_position)
        / (sigma * sigma);

    return particle.velocity + (-factor) * relative_position;
}

}  // namespace tp3
