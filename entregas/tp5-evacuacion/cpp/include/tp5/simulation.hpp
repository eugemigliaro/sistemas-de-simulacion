#pragma once

#include <vector>

#include "tp5/model.hpp"
#include "tp5/output.hpp"

namespace tp5 {

// Corre la evacuación con el esquema de params.scheme desde `agents` (estado
// inicial) hasta que salen todos o se llega a t_max.
Summary simulate(const Params& params, std::vector<Agent> agents, Writer& writer);

// Los tres esquemas, por separado (los usan las pruebas).
Summary run_time_step(const Params& params, const Room& room, std::vector<Agent>& agents, Writer& writer);
Summary run_event_driven(const Params& params, const Room& room, std::vector<Agent>& agents, Writer& writer);
Summary run_hybrid(const Params& params, const Room& room, std::vector<Agent>& agents, Writer& writer);

}  // namespace tp5
