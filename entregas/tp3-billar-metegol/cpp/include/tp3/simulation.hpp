#pragma once

#include <cstddef>
#include <cstdint>
#include <functional>

#include "tp3/collisions.hpp"
#include "tp3/io.hpp"
#include "tp3/model.hpp"

namespace tp3 {

enum class EventKind : std::uint8_t {
    None,           // no hay ningun choque futuro
    Wall,           // `first` contra la pared `wall`
    Obstacle,       // `first` contra el obstaculo `second`
    ParticlePair,   // `first` contra `second`
};

// Un choque agendado. `time` es el **instante absoluto** del choque, no el
// tiempo que falta: una cola de prioridad tiene que ordenar eventos agendados
// en momentos distintos, y con tiempos relativos el orden se rompe apenas
// avanza el reloj. Las funciones `predict_*` siguen devolviendo tiempos
// relativos, porque son geometria pura y no conocen el reloj; la conversion a
// absoluto ocurre al agendar.
struct Event {
    double time{no_collision};
    EventKind kind{EventKind::None};
    std::size_t first{};
    std::size_t second{};
    WallKind wall{WallKind::Short};
    bool on_goal{false};

    // Contadores de choque de los participantes en el momento de agendar. El
    // motor ingenuo no los mira porque recalcula todo; la cola de prioridad de
    // la fase 5 los compara al extraer el evento para descartar los que otro
    // choque dejo invalidados, sin tener que borrarlos de la cola
    // [B16, p. 1] [B16, p. 4].
    std::uint64_t first_collisions{};
    std::uint64_t second_collisions{};
};

struct SimulationConfig {
    // Reloj absoluto hasta el que avanza la corrida. No es un parametro fisico:
    // el sistema no cambia de comportamiento por simular mas o menos tiempo
    // [COR02].
    double max_time{};

    // Cada cuantos eventos se escribe un cuadro periodico; 0 los desactiva.
    // Los cuadros por cambio de color se escriben siempre.
    std::uint64_t save_every{0};

    // Tope de seguridad para que una corrida patologica no gire sin fin;
    // 0 lo desactiva.
    std::uint64_t max_events{0};
};

struct SimulationReport {
    std::uint64_t processed_events{};
    std::uint64_t written_frames{};
    double final_time{};
    bool reached_max_time{false};
    bool reached_max_events{false};

    // El sistema se quedo sin choques futuros posibles. Con velocidades no
    // nulas no deberia ocurrir; es una senal de error de implementacion.
    bool exhausted_events{false};
};

// Receptor de cuadros. El motor le entrega el estado y el motivo, y no sabe
// donde termina escrito: eso deja que los tests lean los cuadros en memoria y
// que el punto 1.1, que solo mide tiempo de ejecucion, corra sin tocar disco.
//
// El motor nunca calcula Ng, Fu, t90 ni DCM: emite estado y nada mas
// [TP03, p. 2] [COR02].
using FrameSink = std::function<
    void(const System&, std::uint64_t processed_events, FrameReason)
>;

// Mueve todas las particulas en linea recta durante `interval` y adelanta el
// reloj. Entre choques el movimiento es rectilineo uniforme [T03, p. 16].
void advance(System& system, double interval) noexcept;

// Busca el primer choque recalculando todos los tiempos: N paredes, N*K
// obstaculos y N*(N-1)/2 pares. Es O(N^2) por evento, lo que la vuelve la
// referencia lenta del punto 1.1 y el oraculo contra el que se valida la
// version con cola de prioridad.
//
// Ante un empate exacto gana el primero en el orden de recorrido, que es fijo,
// de modo que la corrida es reproducible a partir de la semilla.
[[nodiscard]] Event find_next_event(const System& system) noexcept;

// Motor con cola de prioridad. Agenda los eventos de cada particula una sola
// vez y, despues de cada choque, reagenda unicamente los de las particulas que
// participaron. Los eventos que quedaron invalidados no se borran de la cola:
// se los descarta al extraerlos comparando los contadores de choque guardados
// contra los actuales [B16, pp. 1, 4].
SimulationReport simulate_queue(
    System& system,
    const SimulationConfig& config,
    const FrameSink& sink
);

// Aplica el choque: actualiza las velocidades involucradas, incrementa sus
// contadores y, si una particula fresca toco el arco, la pasa a usada.
// Devuelve si hubo cambio de color.
bool apply_event(System& system, const Event& event) noexcept;

// Motor ingenuo: recalcula todos los tiempos en cada evento. Modifica `system`
// in situ hasta `max_time` y emite los cuadros por `sink`, que puede ser vacio.
SimulationReport simulate_naive(
    System& system,
    const SimulationConfig& config,
    const FrameSink& sink
);

}  // namespace tp3
