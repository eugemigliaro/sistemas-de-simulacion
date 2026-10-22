#include "tp4/billiard.hpp"

#include <cmath>
#include <stdexcept>

namespace tp4 {
namespace {

bool positive(double value) noexcept { return std::isfinite(value) && value > 0.0; }

}  // namespace

void validate(const Billiard& billiard) {
    if (!positive(billiard.radius) || !positive(billiard.particle_radius)
        || !positive(billiard.particle_mass) || !positive(billiard.stiffness)
        || !std::isfinite(billiard.initial_speed) || billiard.initial_speed < 0.0) {
        throw std::invalid_argument("parametros del billar invalidos");
    }
    if (billiard.particle_radius >= billiard.radius) {
        throw std::invalid_argument("las particulas no entran en el billar");
    }
    if (billiard.obstacle_x) {
        const double x0 = *billiard.obstacle_x;
        if (!std::isfinite(x0) || x0 < billiard.particle_radius
            || x0 > billiard.radius - billiard.particle_radius) {
            throw std::invalid_argument("x0 debe estar entre r (obstaculos en contacto) y R - r (contacto con la pared)");
        }
    }
}

std::vector<Vec2> obstacle_centers(const Billiard& billiard) {
    if (!billiard.obstacle_x) {
        return {};
    }
    return {{-*billiard.obstacle_x, 0.0}, {*billiard.obstacle_x, 0.0}};
}

}  // namespace tp4
