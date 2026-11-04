#include <cmath>

#include "test_support.hpp"
#include "tp5/collision.hpp"
#include "tp5/events.hpp"

using namespace tp5;

int main() {
    Params p;
    p.dt = 1e-4;
    // Choque frontal blando: elástico, dura medio período del resorte con la masa reducida.
    CollisionSetup head_on;
    const CollisionResult r = simulate_collision(p, head_on);
    const double mi = p.mass * std::pow(head_on.radius_i / p.reference_radius, 2);
    const double mj = p.mass * std::pow(head_on.radius_j / p.reference_radius, 2);
    const double omega = std::sqrt(p.kn * (mi + mj) / (mi * mj));
    CHECK_NEAR(r.contact_time, M_PI / omega, 2e-4);
    CHECK_NEAR(r.max_overlap, head_on.speed / omega, 1e-4);
    CHECK_NEAR(r.normal_ratio, -1.0, 1e-4);
    // Choque oblicuo: la regla de disco duro reproduce la restitución tangencial del blando.
    CollisionSetup oblique;
    oblique.offset = 0.5;
    oblique.speed = 0.5;
    const CollisionResult s = simulate_collision(p, oblique);
    CHECK_NEAR(s.tangential_ratio, s.hard_tangential_ratio, 0.05 * s.hard_tangential_ratio);
    CHECK_NEAR(s.normal_ratio, -1.0, 0.05);
    return test::finish("test_collision");
}
