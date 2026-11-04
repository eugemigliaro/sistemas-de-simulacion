#pragma once

#include "tp5/model.hpp"

namespace tp5 {

// Choque aislado de dos agentes con el contacto blando del SFM, sin término de
// deseo: valida el dt de TSDMD y la regla de choque del EDMD (events.hpp).
struct CollisionSetup {
    double radius_i = 0.25;
    double radius_j = 0.18;
    double speed = 1.5;       // rapidez relativa de acercamiento [m/s]
    double offset = 0.0;      // parámetro de impacto (fracción de r_i + r_j)
};

struct CollisionResult {
    double contact_time = 0.0;   // duración del contacto [s]
    double max_overlap = 0.0;    // superposición máxima [m]
    double normal_ratio = 0.0;   // v_n después / v_n antes (relativa); 1 = elástico
    double tangential_ratio = 0.0;  // v_t después / v_t antes (relativa)
    double hard_normal_ratio = 0.0;     // lo mismo con la regla de disco duro
    double hard_tangential_ratio = 0.0;
};

[[nodiscard]] CollisionResult simulate_collision(const Params& params, const CollisionSetup& setup);

}  // namespace tp5
