#pragma once

#include <vector>

#include "tp3/model.hpp"

namespace tp3 {

// Genera las condiciones iniciales del paso A1 [T03, p. 10]: N particulas
// ubicadas de a una, con posicion uniforme en el area disponible y sin
// solaparse con las paredes, los obstaculos ni las particulas ya ubicadas.
//
// La direccion es uniforme en [0, 2*pi) y el modulo de la velocidad es
// `initial_speed` para todas las particulas [TP03, p. 2]. Todas nacen frescas.
//
// El muestreo es por rechazo, que es lo que preserva la uniformidad exigida
// por la consigna ("a azar en toda el area disponible" [TP03, p. 3]). Cuando
// se agotan `max_placement_attempts` candidatos para una misma particula se
// lanza std::runtime_error indicando cuantas se habian ubicado: se interpreta
// que la configuracion de obstaculos viola la restriccion (ii) del punto 1.2,
// que exige radios "tal que permita la generacion de las N particulas".
//
// Los obstaculos se validan con `validate_obstacles`, de modo que la lista
// vacia (mesa vacia) es aceptable.
[[nodiscard]] System generate_system(
    const InitializationConfig& config,
    const std::vector<Obstacle>& obstacles
);

}  // namespace tp3
