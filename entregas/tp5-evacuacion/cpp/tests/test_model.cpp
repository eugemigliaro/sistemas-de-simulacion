#include <cmath>

#include "test_support.hpp"
#include "tp5/model.hpp"
#include "tp5/setup.hpp"

using namespace tp5;

int main() {
    Params p;
    validate(p);
    const Room room(p);
    // Adentro, alineado con el tramo central: derecho hacia la puerta.
    Vec2 e = room.desired_direction({25.0, 10.0}, false);
    CHECK_NEAR(e.x, 0.0, 1e-15);
    CHECK_NEAR(e.y, -1.0, 1e-15);
    // Al costado: hacia el extremo del 60 % central (25 + 0,24).
    e = room.desired_direction({35.0, 10.0}, false);
    const Vec2 towards = Vec2{25.24, 0.0} - Vec2{35.0, 10.0};
    CHECK_NEAR(e.x, towards.x / norm(towards), 1e-12);
    CHECK_NEAR(e.y, towards.y / norm(towards), 1e-12);
    // Afuera, debajo de la puerta: se aleja en -y.
    e = room.desired_direction({25.1, -0.3}, true);
    CHECK_NEAR(e.x, 0.0, 1e-15);
    CHECK_NEAR(e.y, -1.0, 1e-15);
    // Afuera con target común en (L/2, -D).
    Params q = p;
    q.second_target = SecondTarget::Point;
    q.second_target_distance = 3.0;
    const Room room_point(q);
    e = room_point.desired_direction({25.3, -0.5}, true);
    const Vec2 to_point = Vec2{25.0, -3.0} - Vec2{25.3, -0.5};
    CHECK_NEAR(e.x, to_point.x / norm(to_point), 1e-12);
    // Distancia a la puerta.
    CHECK_NEAR(room.door_distance({25.0, -1.0}), 1.0, 1e-15);
    CHECK_NEAR(room.door_distance({25.4 + 0.6, -0.8}), 1.0, 1e-12);
    // Target común más cerca que el retiro: inválido.
    q.second_target_distance = 0.8;
    CHECK_THROWS(std::invalid_argument, validate(q));
    // T* menor que dt: inválido.
    Params r = p;
    r.t_star = 0.5 * r.dt;
    CHECK_THROWS(std::invalid_argument, validate(r));

    // Estado inicial: sin superposiciones, adentro de la sala, relajados y con la masa pedida.
    const auto agents = initial_agents(p, room);
    CHECK(agents.size() == 500);
    bool ok = true;
    for (std::size_t i = 0; i < agents.size(); ++i) {
        const Agent& a = agents[i];
        ok = ok && a.radius >= p.radius_min && a.radius <= p.radius_max;
        ok = ok && a.position.x >= a.radius && a.position.x <= p.side - a.radius;
        ok = ok && a.position.y >= a.radius && a.position.y <= p.side - a.radius;
        ok = ok && std::abs(a.mass - p.mass * (a.radius / p.reference_radius) * (a.radius / p.reference_radius)) < 1e-9;
        const Vec2 v = p.desired_speed * room.desired_direction(a.position, false);
        ok = ok && norm(a.velocity - v) < 1e-12;
        for (std::size_t j = i + 1; j < agents.size(); ++j) {
            ok = ok && norm(a.position - agents[j].position) >= a.radius + agents[j].radius;
        }
    }
    CHECK(ok);
    // Misma semilla, mismo estado.
    const auto again = initial_agents(p, room);
    CHECK(again[123].position == agents[123].position);
    return test::finish("test_model");
}
