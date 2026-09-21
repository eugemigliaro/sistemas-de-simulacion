#pragma once

#include <cstdint>
#include <iosfwd>
#include <optional>
#include <string>
#include <vector>

#include "tp3/model.hpp"

namespace tp3 {

// --- Configuracion de obstaculos -------------------------------------------
//
// Formato exigido por la consigna: una linea "xk yk Rk" por obstaculo, en
// metros y separados por espacios [TP03, p. 3]. Se admiten lineas vacias y
// comentarios que empiezan con '#'; la escritura no los genera, para que el
// archivo entregado sea exactamente el formato pedido.

[[nodiscard]] std::vector<Obstacle> read_obstacles(std::istream& stream);
void write_obstacles(std::ostream& stream, const std::vector<Obstacle>& obstacles);

// --- Trayectoria ------------------------------------------------------------
//
// El motor escribe unicamente estado: tiempo, posiciones, velocidades y color
// [TP03, p. 2]. Los observables se calculan en el post-proceso de Python.
//
// El archivo tiene una cabecera de lineas '#' con los parametros del sistema y
// la lista de obstaculos, y despues una secuencia de cuadros:
//
//   frame <indice> <tiempo> <eventos_procesados> <motivo>
//   <x> <y> <vx> <vy> <estado>      (N lineas, una por particula, en orden de id)
//
// El estado es 0 para fresca y 1 para usada. El motivo indica por que se
// guardo el cuadro: "initial", "periodic", "color" o "final". Los cuadros
// "color" permiten que el post-proceso reconstruya Ng(t) y t90 con precision
// exacta sin que el motor cuente goles. El cuadro "final" cierra la corrida y
// le dice al post-proceso hasta donde llego el reloj, que es lo que distingue
// una realizacion que no alcanzo Fu = 0.9 de un archivo truncado [TP03, p. 3].

enum class FrameReason : std::uint8_t {
    Initial,
    Periodic,
    Color,
    Final,
};

[[nodiscard]] std::string to_string(FrameReason reason);

struct TrajectoryMetadata {
    std::uint64_t seed{};
    double initial_speed{default_initial_speed};
    // Cada cuantos eventos se guarda un cuadro periodico; 0 significa que no
    // se guardan cuadros periodicos. No es un parametro fisico, pero se
    // registra en la cabecera para poder reproducir la corrida.
    std::uint64_t save_every{1};
    // Horizonte y tope de eventos pedidos a simulate. Tampoco son parametros
    // fisicos: le permiten al post-proceso distinguir una realizacion que
    // llego a tmax sin alcanzar Fu = 0.9 de una cortada por el tope de
    // eventos [TP03, p. 3]. generate no los escribe.
    std::optional<double> max_time{};
    std::optional<std::uint64_t> max_events{};
};

void write_trajectory_header(
    std::ostream& stream,
    const System& system,
    const TrajectoryMetadata& metadata
);

void write_frame(
    std::ostream& stream,
    const System& system,
    std::uint64_t frame_index,
    std::uint64_t processed_events,
    FrameReason reason
);

}  // namespace tp3
