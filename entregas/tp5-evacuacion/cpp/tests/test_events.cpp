#include <cmath>

#include "test_support.hpp"
#include "tp5/events.hpp"

using namespace tp5;

int main() {
    // Dos discos de frente: se tocan cuando recorren la brecha a la velocidad relativa.
    CHECK_NEAR(contact_time({3.0, 0.0}, {-2.0, 0.0}, 1.0), 1.0, 1e-12);
    // Se alejan o pasan de largo.
    CHECK(contact_time({3.0, 0.0}, {2.0, 0.0}, 1.0) == never);
    CHECK(contact_time({3.0, 2.0}, {-2.0, 0.0}, 1.0) == never);
    // Rozando: parámetro de impacto igual a sigma.
    CHECK_NEAR(contact_time({3.0, 1.0 - 1e-9}, {-1.0, 0.0}, 1.0), 3.0, 1e-3);
    // Ya en contacto y acercándose: choque inmediato.
    CHECK(contact_time({0.9, 0.0}, {-1.0, 0.0}, 1.0) == 0.0);
    CHECK(contact_time({0.9, 0.0}, {1.0, 0.0}, 1.0) == never);

    // Pared y extremos de un segmento.
    const Segment wall{{0.0, 0.0}, {4.0, 0.0}};
    CHECK_NEAR(segment_contact_time({2.0, 3.0}, {0.0, -1.0}, 0.5, wall), 2.5, 1e-12);
    CHECK_NEAR(segment_contact_time({2.0, -3.0}, {0.0, 1.0}, 0.5, wall), 2.5, 1e-12);  // del otro lado
    // Fuera del tramo recto: choca con el extremo (marco de la puerta).
    CHECK(segment_contact_time({5.0, 3.0}, {0.0, -1.0}, 0.5, wall) == never);  // pasa a 1 m del extremo
    CHECK_NEAR(segment_contact_time({4.3, 3.0}, {0.0, -1.0}, 0.5, wall), 3.0 - 0.4, 1e-12);

    // Retiro: salir de la cápsula de radio 1 alrededor de la puerta.
    const Segment door{{-0.4, 0.0}, {0.4, 0.0}};
    CHECK_NEAR(capsule_exit_time({0.0, -0.2}, {0.0, -1.0}, door, 1.0), 0.8, 1e-12);
    CHECK_NEAR(capsule_exit_time({0.3, -0.2}, {1.0, 0.0}, door, 1.0), 0.1 + std::sqrt(1.0 - 0.04), 1e-12);
    CHECK(capsule_exit_time({0.0, -2.0}, {0.0, -1.0}, door, 1.0) == 0.0);

    Params p;
    // Restitución tangencial: exp(-2 kappa |v_n| / k) = exp(-4 v_n) con los valores del paper.
    CHECK_NEAR(tangential_restitution(p, 1.0), std::exp(-4.0), 1e-15);
    CHECK_NEAR(tangential_restitution(p, 0.0), 1.0, 0.0);

    // Choque oblicuo con masas distintas: conserva el momento, invierte la normal y
    // multiplica la tangencial.
    Vec2 vi{1.5, 0.0};
    Vec2 vj{0.0, 0.0};
    const double mi = 100.0;
    const double mj = 60.0;
    const Vec2 xi{0.0, 0.0};
    const Vec2 xj{0.3, 0.3};
    const Vec2 momentum = mi * vi + mj * vj;
    const Vec2 n = (1.0 / norm(xi - xj)) * (xi - xj);
    const Vec2 t = perpendicular(n);
    const double vn = dot(vi - vj, n);
    const double vt = dot(vi - vj, t);
    resolve_pair(p, xi, vi, mi, xj, vj, mj);
    const Vec2 after = mi * vi + mj * vj;
    CHECK_NEAR(after.x, momentum.x, 1e-12);
    CHECK_NEAR(after.y, momentum.y, 1e-12);
    CHECK_NEAR(dot(vi - vj, n), -vn, 1e-12);
    CHECK_NEAR(dot(vi - vj, t), tangential_restitution(p, vn) * vt, 1e-12);

    // Pared: refleja la normal.
    Vec2 v{1.0, -1.0};
    resolve_wall(p, {0.0, 0.2}, {0.0, 0.0}, v);
    CHECK_NEAR(v.y, 1.0, 1e-12);
    CHECK_NEAR(v.x, std::exp(-4.0), 1e-12);
    return test::finish("test_events");
}
