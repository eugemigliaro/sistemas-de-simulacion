#pragma once

#include <cstdint>
#include <ostream>
#include <vector>

#include "tp5/model.hpp"

namespace tp5 {

struct Summary {
    double end_time = 0.0;           // instante simulado al terminar
    std::uint64_t steps = 0;         // pasos de TSDMD (o del reloj del híbrido)
    std::uint64_t events = 0;        // eventos EDMD procesados (válidos)
    std::uint64_t agent_steps = 0;   // pasos de TSDMD sumados sobre agentes
    std::uint64_t isolated_unrelaxed_steps = 0;  // híbrido: pasos TSDMD de agentes aislados pero sin relajar (estimado)
    std::uint64_t switches = 0;      // cambios de esquema en el híbrido
    std::uint64_t bound_violations = 0;  // pasos con algún TSDMD más rápido que V_max
    double max_speed = 0.0;          // mayor rapidez de un agente TSDMD
    int exited = 0;
    int remaining = 0;
    bool clogged = false;            // terminó por clog_time sin salidas
    double wall_seconds = 0.0;       // solo el bucle de simulación
};

// Salida de texto: solo estado [COR02]. Cabecera con '#', un renglón `agent` por
// agente (radio y masa), cuadros cada output_dt y, intercalados en orden de
// tiempo, los instantes de salida [T05, p. 21] y los cambios de modo.
//   frame <t> <adentro>          seguido de un renglón <id> <x> <y> <vx> <vy> <modo> por agente
//   exit <t> <id>
//   mode <t> <id> <modo>         0 = TSDMD, 1 = EDMD
// Avance de una corrida larga, por stderr (no es parte de la salida).
void report_progress(double time, int inside, std::uint64_t events, std::uint64_t steps, double wall_seconds);

class Writer {
public:
    explicit Writer(std::ostream* out) : out_(out) {}

    void header(const Params& params, const std::vector<Agent>& agents);
    // `positions` son las posiciones en `time` (las de EDMD se calculan sobre la recta).
    void frame(double time, const std::vector<Agent>& agents, const std::vector<Vec2>& positions);
    void exit(double time, std::size_t agent);
    void mode(double time, std::size_t agent, Mode mode);
    void footer(const Summary& summary);

private:
    std::ostream* out_;
};

}  // namespace tp5
