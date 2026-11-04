#include "tp5/events.hpp"

#include <algorithm>
#include <cmath>
#include <utility>

namespace tp5 {

double contact_time(const Vec2& dr, const Vec2& dv, double sigma) noexcept {
    const double approach = dot(dv, dr);
    if (!(approach < 0.0)) {
        return never;  // se alejan o van paralelos
    }
    const double gap = norm_squared(dr) - sigma * sigma;
    if (gap <= 0.0) {
        return 0.0;  // ya en contacto y acercándose: choque inmediato
    }
    const double speed_squared = norm_squared(dv);
    const double discriminant = approach * approach - speed_squared * gap;
    if (discriminant < 0.0) {
        return never;
    }
    // Raíz menor escrita sin cancelación: (-b - sqrt(D)) / a = c / (-b + sqrt(D)).
    return gap / (-approach + std::sqrt(discriminant));
}

double segment_contact_time(const Vec2& position, const Vec2& velocity, double radius,
                            const Segment& segment) noexcept {
    double best = never;
    const Vec2 along = segment.b - segment.a;
    const double length = norm(along);
    const Vec2 unit = (1.0 / length) * along;
    const Vec2 normal = perpendicular(unit);
    const double distance = dot(position - segment.a, normal);
    const double normal_speed = dot(velocity, normal);
    double line_time = never;
    if (distance >= 0.0 && normal_speed < 0.0) {
        line_time = (distance - radius) / -normal_speed;
    } else if (distance < 0.0 && normal_speed > 0.0) {
        line_time = (-distance - radius) / normal_speed;
    }
    if (line_time < 0.0) {
        line_time = 0.0;  // ya tocando la recta y acercándose
    }
    if (line_time < never) {
        const double s = dot(position + line_time * velocity - segment.a, unit);
        if (s >= 0.0 && s <= length) {
            best = line_time;
        }
    }
    for (const Vec2& end : {segment.a, segment.b}) {
        const double t = contact_time(end - position, -velocity, radius);
        if (t < best) best = t;
    }
    return best;
}

double descent_time(const Vec2& position, const Vec2& velocity, double level) noexcept {
    if (!(velocity.y < 0.0)) {
        return never;
    }
    const double t = (position.y - level) / -velocity.y;
    return t > 0.0 ? t : 0.0;
}

double capsule_exit_time(const Vec2& position, const Vec2& velocity, const Segment& segment,
                         double radius) noexcept {
    // La cápsula es convexa: la recta la atraviesa en un solo intervalo, unión de los
    // intervalos de sus tres partes (rectángulo y dos discos). El retiro es el final.
    double last = -never;
    const double speed_squared = norm_squared(velocity);
    if (speed_squared <= 0.0) {
        return never;
    }
    for (const Vec2& end : {segment.a, segment.b}) {
        const Vec2 dr = position - end;
        const double b = dot(dr, velocity);
        const double c = norm_squared(dr) - radius * radius;
        const double discriminant = b * b - speed_squared * c;
        if (discriminant >= 0.0) {
            last = std::max(last, (-b + std::sqrt(discriminant)) / speed_squared);
        }
    }
    const Vec2 along = segment.b - segment.a;
    const double length = norm(along);
    const Vec2 unit = (1.0 / length) * along;
    const Vec2 normal = perpendicular(unit);
    double lo = -never;
    double hi = never;
    auto slab = [&](double start, double rate, double min, double max) {
        if (rate == 0.0) {
            if (start < min || start > max) {
                lo = never;
                hi = -never;
            }
            return;
        }
        double t1 = (min - start) / rate;
        double t2 = (max - start) / rate;
        if (t1 > t2) std::swap(t1, t2);
        lo = std::max(lo, t1);
        hi = std::min(hi, t2);
    };
    slab(dot(position - segment.a, unit), dot(velocity, unit), 0.0, length);
    slab(dot(position - segment.a, normal), dot(velocity, normal), -radius, radius);
    if (lo <= hi) {
        last = std::max(last, hi);
    }
    return last > 0.0 ? last : 0.0;
}

double tangential_restitution(const Params& p, double normal_speed) noexcept {
    return std::exp(-2.0 * p.kt * std::abs(normal_speed) / p.kn);
}

void resolve_pair(const Params& p, const Vec2& position_i, Vec2& velocity_i, double mass_i,
                  const Vec2& position_j, Vec2& velocity_j, double mass_j) noexcept {
    const Vec2 offset = position_i - position_j;
    const Vec2 n = (1.0 / norm(offset)) * offset;  // de j hacia i
    const Vec2 t = perpendicular(n);
    const Vec2 relative = velocity_i - velocity_j;
    const double vn = dot(relative, n);
    if (vn >= 0.0) {
        return;  // ya se separan
    }
    const double vt = dot(relative, t);
    const double et = tangential_restitution(p, vn);
    // Cambio de la velocidad relativa: vn -> -vn y vt -> et vt. El impulso es
    // mu * cambio, con mu la masa reducida: i se lleva mu/m_i y j, -mu/m_j.
    const Vec2 change = (-2.0 * vn) * n + ((et - 1.0) * vt) * t;
    const double total = mass_i + mass_j;
    velocity_i += (mass_j / total) * change;
    velocity_j -= (mass_i / total) * change;
}

void resolve_wall(const Params& p, const Vec2& position, const Vec2& contact, Vec2& velocity) noexcept {
    const Vec2 offset = position - contact;
    const Vec2 n = (1.0 / norm(offset)) * offset;
    const Vec2 t = perpendicular(n);
    const double vn = dot(velocity, n);
    if (vn >= 0.0) {
        return;
    }
    const double vt = dot(velocity, t);
    const double et = tangential_restitution(p, vn);
    velocity += (-2.0 * vn) * n + ((et - 1.0) * vt) * t;
}

}  // namespace tp5
