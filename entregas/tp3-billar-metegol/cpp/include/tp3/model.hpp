#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace tp3 {

// Parámetros físicos fijados por la consigna [TP03, p. 2].
inline constexpr double default_length = 1.20;        // L, eje x
inline constexpr double default_width = 0.68;         // W, eje y
inline constexpr double default_goal_width = 0.20;    // d, largo del arco
inline constexpr double default_particle_radius = 0.0175;
inline constexpr double default_particle_mass = 0.025;
inline constexpr double default_initial_speed = 1.0;  // v0

struct Vec2 {
    double x{};
    double y{};

    bool operator==(const Vec2&) const = default;
};

// Una partícula fresca (azul) pasa a usada (roja) en su primer contacto con un
// arco. El color es estado del sistema, no un observable: la consigna pide
// imprimirlo junto a posiciones y velocidades [TP03, p. 2].
enum class ParticleState : std::uint8_t {
    Fresh,
    Used,
};

struct Particle {
    std::size_t id{};
    Vec2 position{};
    Vec2 velocity{};
    double radius{default_particle_radius};
    double mass{default_particle_mass};
    ParticleState state{ParticleState::Fresh};

    // Cantidad de choques ya resueltos. La cola de prioridad lo usa para
    // descartar eventos invalidados sin tener que borrarlos de la cola.
    std::uint64_t collision_count{};

    bool operator==(const Particle&) const = default;
};

// Obstáculo circular fijo, modelado como partícula de masa infinita
// [TP03, p. 2] [T03, p. 21].
struct Obstacle {
    std::size_t id{};
    Vec2 center{};
    double radius{};

    bool operator==(const Obstacle&) const = default;
};

// Mesa rectangular con paredes fijas e indeformables. Los arcos ocupan el
// centro de las dos paredes cortas (x = 0 y x = L).
struct Table {
    double length{default_length};
    double width{default_width};
    double goal_width{default_goal_width};

    bool operator==(const Table&) const = default;
};

struct System {
    Table table{};
    double time{};
    std::vector<Particle> particles{};
    std::vector<Obstacle> obstacles{};

    bool operator==(const System&) const = default;
};

struct InitializationConfig {
    std::size_t particle_count{};
    Table table{};
    double particle_radius{default_particle_radius};
    double particle_mass{default_particle_mass};
    double initial_speed{default_initial_speed};
    std::uint64_t seed{};

    // Tope de candidatos sorteados por particula antes de declarar que la
    // configuracion no permite generar las N particulas. No es un parametro
    // fisico: acotar el muestreo por rechazo evita que una configuracion
    // demasiado densa cuelgue un barrido en silencio [TP03, p. 3].
    std::size_t max_placement_attempts{10000};
};

}  // namespace tp3
