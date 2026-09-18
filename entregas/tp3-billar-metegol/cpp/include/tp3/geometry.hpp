#pragma once

#include <vector>

#include "tp3/model.hpp"

namespace tp3 {

// Álgebra vectorial mínima.
[[nodiscard]] Vec2 operator+(const Vec2& left, const Vec2& right) noexcept;
[[nodiscard]] Vec2 operator-(const Vec2& left, const Vec2& right) noexcept;
[[nodiscard]] Vec2 operator*(double scalar, const Vec2& vector) noexcept;
[[nodiscard]] double dot(const Vec2& left, const Vec2& right) noexcept;
[[nodiscard]] double norm_squared(const Vec2& vector) noexcept;
[[nodiscard]] double norm(const Vec2& vector) noexcept;

// Validación de la mesa y de los datos básicos.
[[nodiscard]] bool is_valid(const Table& table) noexcept;
[[nodiscard]] bool is_valid(const Particle& particle) noexcept;
[[nodiscard]] bool is_valid(const Obstacle& obstacle) noexcept;

// Extremos del arco sobre una pared corta: |y - W/2| <= d/2 [TP03, p. 2].
[[nodiscard]] double goal_lower_bound(const Table& table) noexcept;
[[nodiscard]] double goal_upper_bound(const Table& table) noexcept;

// Verdadero si un contacto contra una pared corta a la altura `y` cae dentro
// del arco. Para una pared vertical el punto de contacto comparte la
// coordenada y con el centro de la partícula.
[[nodiscard]] bool is_on_goal(const Table& table, double y) noexcept;

// Contención: el disco debe quedar íntegramente dentro del dominio. Tocar la
// pared de forma tangente se admite; sobresalir no.
[[nodiscard]] bool contains(
    const Table& table,
    const Vec2& center,
    double radius
) noexcept;

// Dos discos se solapan cuando la distancia entre centros es estrictamente
// menor que la suma de radios. El caso tangente no se considera solapamiento.
[[nodiscard]] bool discs_overlap(
    const Vec2& first_center,
    double first_radius,
    const Vec2& second_center,
    double second_radius
) noexcept;

// Validez geométrica de una disposición de obstáculos: íntegramente dentro del
// dominio, sin solaparse entre sí y con Rk >= r [TP03, p. 3].
//
// Acepta la lista vacía: la mesa vacía es un caso legítimo y obligatorio, ya
// que el punto 1.1 simula el sistema sin obstáculos y los puntos 1.2 y 1.3 la
// usan como referencia [TP03, p. 3].
//
// Lanza std::invalid_argument describiendo la primera violación encontrada.
void validate_obstacles(
    const Table& table,
    const std::vector<Obstacle>& obstacles,
    double particle_radius
);

// Validez de una configuración presentada a la competencia. Agrega la
// restricción (i) del punto 1.2, K > 0, que no aplica al motor en general
// [TP03, pp. 3].
void validate_competition_obstacles(
    const Table& table,
    const std::vector<Obstacle>& obstacles,
    double particle_radius
);

// Lugar libre para una partícula de radio `radius` centrada en `center`:
// dentro de la mesa, sin solapar obstáculos ni partículas ya ubicadas.
[[nodiscard]] bool is_free_placement(
    const Table& table,
    const std::vector<Obstacle>& obstacles,
    const std::vector<Particle>& placed,
    const Vec2& center,
    double radius
) noexcept;

}  // namespace tp3
