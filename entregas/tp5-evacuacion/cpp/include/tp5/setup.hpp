#pragma once

#include <vector>

#include "tp5/model.hpp"

namespace tp5 {

// Radios uniformes en [radius_min, radius_max] y posiciones uniformes en la sala,
// sin superposición con otros agentes ni con las paredes [TP05, p. 3]. Todos
// arrancan caminando hacia la puerta con v = v_d e, ya relajados.
[[nodiscard]] std::vector<Agent> initial_agents(const Params& params, const Room& room);

}  // namespace tp5
