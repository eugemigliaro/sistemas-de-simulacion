#include "tp2/geometry.hpp"

#include <cmath>
#include <numbers>
#include <stdexcept>

namespace tp2 {
namespace {

void require_positive_finite(double value, const char* message) {
    if (!std::isfinite(value) || value <= 0.0) {
        throw std::invalid_argument{message};
    }
}

}  // namespace

bool is_valid(const Particle& particle) noexcept {
    return particle.id > 0
        && std::isfinite(particle.position.x)
        && std::isfinite(particle.position.y)
        && std::isfinite(particle.angle);
}

bool is_valid(const System& system) noexcept {
    if (!std::isfinite(system.side) || system.side <= 0.0
        || !std::isfinite(system.time)) {
        return false;
    }

    for (std::size_t index = 0; index < system.particles.size(); ++index) {
        const Particle& particle = system.particles[index];
        if (!is_valid(particle) || particle.id != index + 1
            || particle.position.x < 0.0
            || particle.position.x >= system.side
            || particle.position.y < 0.0
            || particle.position.y >= system.side) {
            return false;
        }
    }
    return true;
}

double wrap_coordinate(double value, double side) {
    require_positive_finite(side, "side must be finite and positive");
    if (!std::isfinite(value)) {
        throw std::invalid_argument{"coordinate must be finite"};
    }

    double wrapped = std::fmod(value, side);
    if (wrapped < 0.0) {
        wrapped += side;
    }
    if (wrapped >= side) {
        wrapped = 0.0;
    }
    return wrapped;
}

double normalize_angle(double angle) {
    if (!std::isfinite(angle)) {
        throw std::invalid_argument{"angle must be finite"};
    }
    constexpr double two_pi = 2.0 * std::numbers::pi_v<double>;
    double normalized = std::fmod(
        angle + std::numbers::pi_v<double>,
        two_pi
    );
    if (normalized < 0.0) {
        normalized += two_pi;
    }
    return normalized - std::numbers::pi_v<double>;
}

Vec2 periodic_displacement(
    const Particle& from,
    const Particle& to,
    double side
) {
    require_positive_finite(side, "side must be finite and positive");
    if (!is_valid(from) || !is_valid(to)) {
        throw std::invalid_argument{"invalid particle"};
    }

    return Vec2{
        .x = std::remainder(to.position.x - from.position.x, side),
        .y = std::remainder(to.position.y - from.position.y, side),
    };
}

double periodic_distance_squared(
    const Particle& first,
    const Particle& second,
    double side
) {
    const Vec2 delta = periodic_displacement(first, second, side);
    return delta.x * delta.x + delta.y * delta.y;
}

bool are_neighbors(
    const Particle& first,
    const Particle& second,
    double side,
    double cutoff
) {
    if (!std::isfinite(cutoff) || cutoff < 0.0) {
        throw std::invalid_argument{"cutoff must be finite and non-negative"};
    }
    if (first.id == second.id) {
        return false;
    }
    return periodic_distance_squared(first, second, side)
        <= cutoff * cutoff;
}

}  // namespace tp2
