#pragma once

#include <cstdint>
#include <limits>

#include "tp3/model.hpp"

namespace tp3 {

// Ausencia de colision futura. Usar infinito en lugar de un optional deja que
// la busqueda del proximo evento sea un minimo sin casos especiales.
inline constexpr double no_collision = std::numeric_limits<double>::infinity();

// Las paredes cortas son las de x = 0 y x = L: son las que llevan arco, porque
// L = 1.20 m corre sobre x y W = 0.68 m sobre y [TP03, p. 2]. En el lenguaje de
// la teorica son las paredes verticales [T03, p. 19]. Se las nombra por la
// consigna y no por su orientacion para que la condicion de gol quede atada al
// mismo vocabulario que la define.
enum class WallKind : std::uint8_t {
    Short,  // x = 0 y x = L
    Long,   // y = 0 e y = W
};

struct WallPrediction {
    double time{no_collision};
    WallKind kind{WallKind::Short};

    // Solo significativo para WallKind::Short: el punto de contacto cae dentro
    // del arco. Es geometria del evento, no un observable; el motor lo usa
    // para cambiar el color, que es estado del sistema, y nunca para contar
    // goles. Ng(t) y Fu(t) los calcula el post-proceso [TP03, p. 2] [COR02].
    bool on_goal{false};
};

// --- Prediccion -------------------------------------------------------------
//
// Todas las predicciones devuelven el tiempo que falta hasta el contacto,
// medido desde el estado actual, o `no_collision` si no hay choque futuro.
//
// Se aceptan tiempos cero. La invariante que lo vuelve seguro es que toda
// resolucion deja a los participantes alejandose, de modo que un evento de
// tiempo cero no puede repetirse. Aceptarlos es necesario para los choques de
// esquina: al rebotar contra la pared corta, la larga queda a distancia cero y
// descartarla haria que la particula la atravesara.

// Primer contacto contra alguna de las cuatro paredes [T03, p. 12].
[[nodiscard]] WallPrediction predict_wall_collision(
    const Table& table,
    const Particle& particle
) noexcept;

// Contacto entre dos discos moviles, resolviendo |Δr + Δv t| = σ con
// σ = Ri + Rj. Si no se acercan (Δv·Δr >= 0) o el discriminante es negativo no
// hay colision futura [T03, pp. 13-14].
[[nodiscard]] double predict_disc_collision(
    const Vec2& first_position,
    const Vec2& first_velocity,
    double first_radius,
    const Vec2& second_position,
    const Vec2& second_velocity,
    double second_radius
) noexcept;

[[nodiscard]] double predict_particle_collision(
    const Particle& first,
    const Particle& second
) noexcept;

// Un obstaculo es un disco de velocidad nula, asi que reusa la misma formula.
[[nodiscard]] double predict_obstacle_collision(
    const Particle& particle,
    const Obstacle& obstacle
) noexcept;

// --- Resolucion -------------------------------------------------------------
//
// Funciones puras: devuelven las velocidades posteriores al choque y no tocan
// ni las posiciones ni los contadores de colision. Quien lleve la cuenta de
// eventos es el motor.

struct VelocityPair {
    Vec2 first{};
    Vec2 second{};
};

// La pared corta invierte vx y la larga invierte vy [T03, p. 19].
[[nodiscard]] Vec2 resolve_wall_collision(
    const Vec2& velocity,
    WallKind kind
) noexcept;

// Choque elastico entre dos discos de masas posiblemente distintas. El impulso
// actua sobre la linea que une los centros [T03, p. 20]:
//
//   J = 2 mi mj (Δv·Δr) / (σ (mi + mj)),  Jx = J Δrx / σ,  Jy = J Δry / σ
//   vi' = vi + J/mi,  vj' = vj - J/mj
//
// Conserva momento lineal y energia cinetica. Se asume que las particulas
// estan en contacto; el motor solo la invoca en el instante predicho.
[[nodiscard]] VelocityPair resolve_particle_collision(
    const Particle& first,
    const Particle& second
) noexcept;

// Limite mj -> infinito de la formula anterior: 2 mi mj / (mi + mj) -> 2 mi, la
// masa de la particula se cancela y queda una reflexion especular respecto del
// plano tangente. El obstaculo no se mueve [TP03, p. 2] [T03, p. 21].
[[nodiscard]] Vec2 resolve_obstacle_collision(
    const Particle& particle,
    const Obstacle& obstacle
) noexcept;

}  // namespace tp3
