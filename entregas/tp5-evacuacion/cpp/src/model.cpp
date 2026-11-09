#include "tp5/model.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <string>

namespace tp5 {

Scheme parse_scheme(std::string_view name) {
    if (name == "tsdmd") return Scheme::TimeStep;
    if (name == "edmd") return Scheme::EventDriven;
    if (name == "hybrid") return Scheme::Hybrid;
    throw std::invalid_argument("esquema desconocido: " + std::string(name) + " (tsdmd, edmd o hybrid)");
}

std::string_view to_string(Scheme scheme) noexcept {
    switch (scheme) {
        case Scheme::TimeStep: return "tsdmd";
        case Scheme::EventDriven: return "edmd";
        case Scheme::Hybrid: return "hybrid";
    }
    return "?";
}

SecondTarget parse_second_target(std::string_view name) {
    if (name == "away") return SecondTarget::Away;
    if (name == "point") return SecondTarget::Point;
    throw std::invalid_argument("segundo target desconocido: " + std::string(name) + " (away o point)");
}

std::string_view to_string(SecondTarget target) noexcept {
    return target == SecondTarget::Away ? "away" : "point";
}

Relaxation parse_relaxation(std::string_view name) {
    if (name == "kicks") return Relaxation::Kicks;
    if (name == "analytic") return Relaxation::Analytic;
    throw std::invalid_argument("relajación desconocida: " + std::string(name) + " (kicks o analytic)");
}

std::string_view to_string(Relaxation relaxation) noexcept {
    return relaxation == Relaxation::Kicks ? "kicks" : "analytic";
}

void validate(const Params& p) {
    auto require = [](bool condition, const char* message) {
        if (!condition) throw std::invalid_argument(message);
    };
    require(p.agents > 0, "agents debe ser positivo");
    require(p.side > 0.0 && std::isfinite(p.side), "side debe ser positivo");
    require(p.door > 0.0 && p.door < p.side, "door debe estar en (0, side)");
    require(p.radius_min > 0.0 && p.radius_min <= p.radius_max, "radios inválidos");
    require(2.0 * p.radius_max < p.door, "la puerta debe ser más ancha que un agente");
    require(p.desired_speed > 0.0, "desired_speed debe ser positivo");
    require(p.exit_distance > p.radius_max, "exit_distance debe superar el radio máximo");
    require(p.target_fraction > 0.0 && p.target_fraction <= 1.0, "target_fraction debe estar en (0, 1]");
    // Un target común más cerca que el retiro haría que los agentes se amontonen en él.
    require(p.second_target != SecondTarget::Point || p.second_target_distance > p.exit_distance,
            "second_target_distance debe superar exit_distance");
    require(p.reference_radius > 0.0, "reference_radius debe ser positivo");
    require(p.mass > 0.0 && p.tau > 0.0 && p.kn > 0.0 && p.kt >= 0.0, "parámetros del SFM inválidos");
    require(p.dt > 0.0 && std::isfinite(p.dt), "dt debe ser positivo");
    require(p.noise >= 0.0 && p.noise_time >= p.dt, "noise debe ser >= 0 y noise_time >= dt");
    require(p.t_max > 0.0, "t_max debe ser positivo");
    require(p.clog_time > 0.0, "clog_time debe ser positivo");
    require(!(p.noise > 0.0 && p.scheme == Scheme::EventDriven && p.relaxation == Relaxation::Analytic),
            "la fluctuación no está implementada para EDMD con relajación analítica");
    require(p.output_dt >= 0.0, "output_dt no puede ser negativo");
    if (p.output_dt > 0.0) {
        const double steps = p.output_dt / p.dt;
        require(std::abs(steps - std::round(steps)) < 1e-9 * steps && steps >= 1.0,
                "output_dt debe ser un múltiplo entero de dt");
    }
    // Con T* >= dt el pase a TSDMD siempre ocurre en un paso anterior al contacto.
    require(p.t_star >= p.dt, "t_star debe ser al menos dt");
    require(p.t_out_factor >= 1.0, "t_out_factor debe ser al menos 1");
    require(p.speed_bound >= p.desired_speed, "speed_bound debe ser al menos desired_speed");
    require(p.relax_check_every >= 1, "relax_check_every debe ser al menos 1");
    require(p.kick > 0.0, "kick debe ser positivo");
    require(p.relax_tolerance > 0.0 && p.relax_tolerance < 1.0, "relax_tolerance debe estar en (0, 1)");
    require(p.aim_tolerance > 0.0 && p.aim_tolerance < 1.0, "aim_tolerance debe estar en (0, 1)");
    require(p.core_reduction >= 0.0 && p.core_reduction < 2.0 * p.radius_min,
            "core_reduction debe estar en [0, 2 radius_min)");
}

Room::Room(const Params& p)
    : side(p.side),
      door_left(0.5 * (p.side - p.door)),
      door_right(0.5 * (p.side + p.door)),
      target_left(0.5 * (p.side - p.target_fraction * p.door)),
      target_right(0.5 * (p.side + p.target_fraction * p.door)),
      exit_distance(p.exit_distance),
      second_target(p.second_target),
      second_point{0.5 * p.side, -p.second_target_distance},
      door{{door_left, 0.0}, {door_right, 0.0}},
      walls{{
          {{0.0, 0.0}, {door_left, 0.0}},
          {{door_right, 0.0}, {p.side, 0.0}},
          {{0.0, 0.0}, {0.0, p.side}},
          {{p.side, 0.0}, {p.side, p.side}},
          {{0.0, p.side}, {p.side, p.side}},
      }} {}

Vec2 Room::desired_direction(const Vec2& position, bool outside) const noexcept {
    Vec2 towards;
    if (!outside) {
        towards = Vec2{std::clamp(position.x, target_left, target_right), 0.0} - position;
    } else if (second_target == SecondTarget::Point) {
        towards = second_point - position;
    } else {
        towards = position - closest_point(door, position);  // gradiente de la distancia a la puerta
    }
    const double length = norm(towards);
    if (length < 1e-12) {
        return {0.0, -1.0};
    }
    return (1.0 / length) * towards;
}

double Room::door_distance(const Vec2& position) const noexcept {
    return norm(position - closest_point(door, position));
}

Vec2 closest_point(const Segment& segment, const Vec2& point) noexcept {
    const Vec2 along = segment.b - segment.a;
    const double length_squared = norm_squared(along);
    const double s = std::clamp(dot(point - segment.a, along) / length_squared, 0.0, 1.0);
    return segment.a + s * along;
}

}  // namespace tp5
