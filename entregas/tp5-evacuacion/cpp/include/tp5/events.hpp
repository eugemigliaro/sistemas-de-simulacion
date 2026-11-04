#pragma once

#include <limits>

#include "tp5/model.hpp"

namespace tp5 {

inline constexpr double never = std::numeric_limits<double>::infinity();

// Tiempo hasta el primer contacto de dos discos en movimiento rectilíneo
// uniforme, con dr = x_j - x_i, dv = v_j - v_i y sigma = r_i + r_j [T03, pp. 13-14].
// Devuelve 0 si ya se tocan (o se superponen por redondeo) y se acercan, y
// `never` si no chocan.
[[nodiscard]] double contact_time(const Vec2& dr, const Vec2& dv, double sigma) noexcept;

// Disco de radio r contra un segmento fijo: tramo recto y extremos (marcos de la
// puerta, esquinas). Mismo criterio que contact_time.
[[nodiscard]] double segment_contact_time(const Vec2& position, const Vec2& velocity, double radius,
                                          const Segment& segment) noexcept;

// Tiempo hasta que la coordenada y llega a `level` moviéndose hacia abajo.
[[nodiscard]] double descent_time(const Vec2& position, const Vec2& velocity, double level) noexcept;

// Tiempo hasta que un punto en MRU sale de la cápsula {p : dist(p, segmento) <= radius}
// (retiro a exit_distance de la puerta). 0 si ya está afuera; `never` si no sale.
[[nodiscard]] double capsule_exit_time(const Vec2& position, const Vec2& velocity, const Segment& segment,
                                       double radius) noexcept;

// Restitución tangencial del límite de disco duro del contacto del SFM: integrando
// la fricción k_t xi dv_t durante medio período del resorte k xi, la velocidad
// tangencial relativa queda multiplicada por exp(-2 k_t |v_n| / k). La normal
// es elástica porque el resorte del SFM no tiene amortiguamiento (ver docs).
[[nodiscard]] double tangential_restitution(const Params& params, double normal_speed) noexcept;

// Choque instantáneo entre dos agentes en contacto: la velocidad relativa normal
// se invierte y la tangencial se multiplica por tangential_restitution; el cambio
// se reparte con la masa reducida, así que se conserva el momento.
void resolve_pair(const Params& params, const Vec2& position_i, Vec2& velocity_i, double mass_i,
                  const Vec2& position_j, Vec2& velocity_j, double mass_j) noexcept;

// Choque contra una pared (masa infinita): `contact` es el punto de la pared más cercano.
void resolve_wall(const Params& params, const Vec2& position, const Vec2& contact, Vec2& velocity) noexcept;

}  // namespace tp5
