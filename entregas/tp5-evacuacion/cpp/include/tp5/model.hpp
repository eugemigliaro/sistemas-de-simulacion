#pragma once

#include <array>
#include <cstdint>
#include <string_view>
#include <vector>

#include "tp5/vec2.hpp"

namespace tp5 {

enum class Scheme { TimeStep, EventDriven, Hybrid };

// Segundo target, una vez cruzada la línea de la puerta: alejarse de la puerta
// lo más rápido posible (-y debajo de ella) o ir a un punto común (L/2, -D).
enum class SecondTarget { Away, Point };

// Recuperación de v_d en EDMD puro: patadas cada delta o relajación analítica.
enum class Relaxation { Kicks, Analytic };

[[nodiscard]] Scheme parse_scheme(std::string_view name);
[[nodiscard]] std::string_view to_string(Scheme scheme) noexcept;
[[nodiscard]] SecondTarget parse_second_target(std::string_view name);
[[nodiscard]] std::string_view to_string(SecondTarget target) noexcept;
[[nodiscard]] Relaxation parse_relaxation(std::string_view name);
[[nodiscard]] std::string_view to_string(Relaxation relaxation) noexcept;

struct Params {
    // Sistema [TP05, p. 3].
    int agents = 500;
    double side = 50.0;          // L [m]
    double door = 0.8;           // d [m]
    double radius_min = 0.18;    // radios uniformes en [radius_min, radius_max] [m]
    double radius_max = 0.25;
    double desired_speed = 1.5;  // v_d [m/s]
    double exit_distance = 1.0;  // se retiran a esta distancia de la puerta [m]
    double target_fraction = 0.6;  // fracción central de la puerta a la que apuntan [B28, p. 4]
    SecondTarget second_target = SecondTarget::Away;
    double second_target_distance = 5.0;  // D del target común (L/2, -D) [m]

    // SFM sin fuerza social [B26, p. 2].
    double mass = 80.0;          // m [kg] para reference_radius
    bool mass_by_area = true;    // m_i = mass (r_i / reference_radius)^2; si no, mass para todos
    double reference_radius = 0.215;
    double tau = 0.5;            // tiempo de relajación [s]
    double kn = 1.2e5;           // k, rigidez normal [N/m]
    double kt = 2.4e5;           // kappa, fricción deslizante [kg/(m s)]
    // Fluctuación opcional (no está en el paper; ver docs): fuerza aleatoria gaussiana solo
    // sobre agentes en contacto, de desvío noise * m v_d / tau por componente, renovada cada noise_time.
    double noise = 0.0;
    double noise_time = 0.1;     // [s]

    // Esquema.
    Scheme scheme = Scheme::TimeStep;
    double dt = 1e-3;            // paso de TSDMD y reloj del híbrido [s]
    double t_star = 0.5;         // híbrido: pasa a TSDMD T* antes de un contacto posible [s]
    double t_out_factor = 2.0;   // híbrido: vuelve a EDMD si no hay contacto posible en t_out_factor T*
    double speed_bound = 3.0;    // híbrido: cota V_max de la rapidez de los agentes TSDMD [m/s]
    int relax_check_every = 10;  // híbrido: cada cuántos pasos se buscan agentes TSDMD que puedan volver a EDMD
    Relaxation relaxation = Relaxation::Kicks;
    double kick = 0.05;          // EDMD: intervalo delta entre patadas de relajación [s]
    double aim_tolerance = 0.01;  // EDMD analítico: reapunta si la dirección al target cambia más que esto [rad]
    double relax_tolerance = 0.01;  // relajado si |v - v_d e| <= tol v_d
    double core_reduction = 0.0;  // EDMD puro: choca a distancia r_i + r_j - core_reduction (núcleo duro reducido) [m]

    // Configuración de la corrida (no cambia la dinámica).
    double t_max = 4000.0;       // corte de seguridad [s]
    double clog_time = 300.0;    // atasco: si no sale nadie durante este tiempo, la corrida termina [s]
    double output_dt = 0.0;      // cada cuánto se escribe el estado; 0: no se escriben cuadros
    double progress = 0.0;       // cada cuánto tiempo simulado se informa el avance por stderr; 0: nunca
    std::uint64_t seed = 0;
};

void validate(const Params& params);

struct Segment {
    Vec2 a;
    Vec2 b;
};

// Sala [0, L] x [0, L] con una puerta de ancho d centrada en la pared y = 0.
struct Room {
    explicit Room(const Params& params);

    double side;
    double door_left;
    double door_right;
    double target_left;
    double target_right;
    double exit_distance;
    SecondTarget second_target;
    Vec2 second_point;
    Segment door;
    std::array<Segment, 5> walls;

    // Dirección deseada. Adentro: hacia el punto del tramo central de la puerta más
    // cercano. Afuera (segundo target): alejándose de la puerta por el camino más
    // corto (-y debajo de ella) o hacia el punto común (L/2, -D).
    [[nodiscard]] Vec2 desired_direction(const Vec2& position, bool outside) const noexcept;

    // Distancia del centro al segmento de la puerta; se retira al llegar a exit_distance.
    [[nodiscard]] double door_distance(const Vec2& position) const noexcept;
};

[[nodiscard]] Vec2 closest_point(const Segment& segment, const Vec2& point) noexcept;

// Modo de cada agente en el híbrido; en los esquemas puros es fijo.
enum class Mode : std::uint8_t { TimeStep = 0, EventDriven = 1 };

struct Agent {
    Vec2 position;       // en EDMD, posición en el instante `since`
    Vec2 velocity;
    Vec2 acceleration;   // a(t_n), para Beeman
    Vec2 previous_acceleration;  // a(t_n - dt)
    double radius = 0.0;
    double mass = 0.0;
    double since = 0.0;  // instante de referencia de la trayectoria recta (EDMD)
    std::uint32_t version = 0;  // cambia cada vez que cambia la trayectoria: invalida eventos
    bool outside = false;  // ya cruzó la puerta: usa el segundo target
    bool active = true;
    bool relaxed = true;   // EDMD: v = v_d e, sin patadas pendientes
    Mode mode = Mode::TimeStep;

    [[nodiscard]] Vec2 position_at(double time) const noexcept {
        return position + (time - since) * velocity;
    }
};

}  // namespace tp5
