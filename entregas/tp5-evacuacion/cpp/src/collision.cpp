#include "tp5/collision.hpp"

#include <cmath>
#include <limits>
#include <vector>

#include "tp5/events.hpp"
#include "tp5/sfm.hpp"

namespace tp5 {

CollisionResult simulate_collision(const Params& base, const CollisionSetup& setup) {
    Params p = base;
    p.agents = 2;
    p.tau = std::numeric_limits<double>::infinity();  // sin término de deseo
    p.side = 100.0;
    p.door = 1.0;
    const Room room(p);
    std::vector<Agent> agents(2);
    const double sigma = setup.radius_i + setup.radius_j;
    const double scale_i = setup.radius_i / p.reference_radius;
    const double scale_j = setup.radius_j / p.reference_radius;
    agents[0].radius = setup.radius_i;
    agents[1].radius = setup.radius_j;
    agents[0].mass = p.mass_by_area ? p.mass * scale_i * scale_i : p.mass;
    agents[1].mass = p.mass_by_area ? p.mass * scale_j * scale_j : p.mass;
    // i viene por la izquierda hacia +x; j quieto, desplazado en y por el parámetro de impacto.
    const double b = setup.offset * sigma;
    const Vec2 center{50.0, 50.0};
    agents[0].position = center - Vec2{sigma * std::sqrt(1.0 - setup.offset * setup.offset) + 1e-3, 0.0};
    agents[1].position = center + Vec2{0.0, b};
    agents[0].velocity = {setup.speed, 0.0};
    agents[1].velocity = {};
    const Vec2 n0 = (1.0 / sigma) * (agents[0].position + Vec2{1e-3, 0.0} - agents[1].position);
    const Vec2 t0 = perpendicular(n0);
    const Vec2 rel0 = agents[0].velocity - agents[1].velocity;
    const double vn0 = dot(rel0, n0);
    const double vt0 = dot(rel0, t0);

    CollisionResult result;
    {
        Vec2 vi = agents[0].velocity;
        Vec2 vj = agents[1].velocity;
        resolve_pair(p, center - (sigma * std::sqrt(1.0 - setup.offset * setup.offset)) * Vec2{1.0, 0.0}, vi,
                     agents[0].mass, agents[1].position, vj, agents[1].mass);
        const Vec2 rel = vi - vj;
        result.hard_normal_ratio = dot(rel, n0) / vn0;
        result.hard_tangential_ratio = vt0 != 0.0 ? dot(rel, t0) / vt0 : 1.0;
    }

    Beeman beeman(p, room);
    const std::vector<std::size_t> both{0, 1};
    bool touching = false;
    bool done = false;
    double start = 0.0;
    double time = 0.0;
    Vec2 n_contact = n0;
    for (int step = 0; step < 10000000 && !done; ++step) {
        beeman.step(agents, both);
        time += p.dt;
        const Vec2 offset = agents[0].position - agents[1].position;
        const double overlap = sigma - norm(offset);
        if (overlap > 0.0) {
            if (!touching) {
                touching = true;
                start = time;
            }
            result.max_overlap = std::max(result.max_overlap, overlap);
            n_contact = (1.0 / norm(offset)) * offset;
        } else if (touching) {
            result.contact_time = time - start;
            done = true;
        }
    }
    // Componentes respecto de la normal del final del contacto (la del choque duro
    // es la del inicio; para choques cortos rotan poco).
    const Vec2 t_contact = perpendicular(n_contact);
    const Vec2 rel = agents[0].velocity - agents[1].velocity;
    result.normal_ratio = dot(rel, n_contact) / vn0;
    result.tangential_ratio = vt0 != 0.0 ? dot(rel, t_contact) / vt0 : 1.0;
    return result;
}

}  // namespace tp5
