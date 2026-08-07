#include "tp1/geometry.hpp"

#include <cmath>
#include <stdexcept>

namespace tp1 {
namespace {

bool is_finite(const Vec2& value) noexcept {
    return std::isfinite(value.x) && std::isfinite(value.y);
}

bool has_known_boundary(BoundaryCondition boundary) noexcept {
    switch (boundary) {
        case BoundaryCondition::Walls:
        case BoundaryCondition::Periodic:
            return true;
    }
    return false;
}

void require_valid(const Particle& particle) {
    if (!is_valid(particle)) {
        throw std::invalid_argument{"invalid particle"};
    }
}

void require_valid(const Domain& domain) {
    if (!is_valid(domain)) {
        throw std::invalid_argument{"invalid domain"};
    }
}

double minimum_image(double delta, double side) noexcept {
    return delta - side * std::round(delta / side);
}

}  // namespace

bool is_valid(const Particle& particle) noexcept {
    return particle.id > 0
        && is_finite(particle.position)
        && is_finite(particle.velocity)
        && std::isfinite(particle.radius)
        && particle.radius > 0.0
        && std::isfinite(particle.property);
}

bool is_valid(const Domain& domain) noexcept {
    return std::isfinite(domain.side)
        && domain.side > 0.0
        && has_known_boundary(domain.boundary);
}

bool is_inside_domain(
    const Particle& particle,
    const Domain& domain
) noexcept {
    if (!is_valid(particle) || !is_valid(domain)) {
        return false;
    }

    switch (domain.boundary) {
        case BoundaryCondition::Walls:
            return particle.position.x >= particle.radius
                && particle.position.x <= domain.side - particle.radius
                && particle.position.y >= particle.radius
                && particle.position.y <= domain.side - particle.radius;

        case BoundaryCondition::Periodic:
            return particle.position.x >= 0.0
                && particle.position.x < domain.side
                && particle.position.y >= 0.0
                && particle.position.y < domain.side;
    }

    return false;
}

Vec2 displacement(
    const Particle& from,
    const Particle& to,
    const Domain& domain
) {
    require_valid(from);
    require_valid(to);
    require_valid(domain);

    Vec2 result{
        .x = to.position.x - from.position.x,
        .y = to.position.y - from.position.y,
    };

    if (domain.boundary == BoundaryCondition::Periodic) {
        result.x = minimum_image(result.x, domain.side);
        result.y = minimum_image(result.y, domain.side);
    }

    return result;
}

double center_distance(
    const Particle& first,
    const Particle& second,
    const Domain& domain
) {
    const Vec2 delta = displacement(first, second, domain);
    return std::hypot(delta.x, delta.y);
}

double edge_distance(
    const Particle& first,
    const Particle& second,
    const Domain& domain
) {
    return center_distance(first, second, domain)
        - first.radius
        - second.radius;
}

bool are_neighbors(
    const Particle& first,
    const Particle& second,
    const Domain& domain,
    double cutoff
) {
    if (!std::isfinite(cutoff) || cutoff < 0.0) {
        throw std::invalid_argument{"cutoff must be finite and non-negative"};
    }

    require_valid(first);
    require_valid(second);
    require_valid(domain);

    if (first.id == second.id) {
        return false;
    }

    return edge_distance(first, second, domain) < cutoff;
}

}  // namespace tp1
