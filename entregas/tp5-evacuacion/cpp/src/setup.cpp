#include "tp5/setup.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <random>
#include <stdexcept>

namespace tp5 {
namespace {

// Conversión explícita a [0, 1): la secuencia depende solo de la semilla y no
// de la implementación de la biblioteca estándar.
double uniform(std::mt19937_64& rng) { return static_cast<double>(rng() >> 11) * 0x1.0p-53; }

}  // namespace

std::vector<Agent> initial_agents(const Params& p, const Room& room) {
    std::mt19937_64 rng(p.seed);
    std::vector<Agent> agents(static_cast<std::size_t>(p.agents));
    for (Agent& agent : agents) {
        agent.radius = p.radius_min + (p.radius_max - p.radius_min) * uniform(rng);
        const double scale = agent.radius / p.reference_radius;
        agent.mass = p.mass_by_area ? p.mass * scale * scale : p.mass;
    }
    // Celdas de lado 2 radius_max para descartar superposiciones sin recorrer a todos.
    const double cell = 2.0 * p.radius_max;
    const int cells = std::max(1, static_cast<int>(p.side / cell));
    const double size = p.side / cells;
    std::vector<std::vector<std::size_t>> grid(static_cast<std::size_t>(cells * cells));
    auto cell_of = [&](double coordinate) {
        return std::clamp(static_cast<int>(coordinate / size), 0, cells - 1);
    };
    const std::uint64_t max_attempts = 100000ull * static_cast<std::uint64_t>(p.agents);
    std::uint64_t attempts = 0;
    for (std::size_t i = 0; i < agents.size(); ++i) {
        const double r = agents[i].radius;
        for (;;) {
            if (++attempts > max_attempts) {
                throw std::runtime_error("no se pudieron ubicar los agentes sin superposición");
            }
            const Vec2 candidate{r + (p.side - 2.0 * r) * uniform(rng), r + (p.side - 2.0 * r) * uniform(rng)};
            const int cx = cell_of(candidate.x);
            const int cy = cell_of(candidate.y);
            bool fits = true;
            for (int dy = -1; dy <= 1 && fits; ++dy) {
                for (int dx = -1; dx <= 1 && fits; ++dx) {
                    const int x = cx + dx;
                    const int y = cy + dy;
                    if (x < 0 || y < 0 || x >= cells || y >= cells) continue;
                    for (std::size_t j : grid[static_cast<std::size_t>(y * cells + x)]) {
                        const double sigma = r + agents[j].radius;
                        if (norm_squared(candidate - agents[j].position) < sigma * sigma) {
                            fits = false;
                            break;
                        }
                    }
                }
            }
            if (fits) {
                agents[i].position = candidate;
                grid[static_cast<std::size_t>(cy * cells + cx)].push_back(i);
                break;
            }
        }
        agents[i].velocity = p.desired_speed * room.desired_direction(agents[i].position, false);
    }
    return agents;
}

}  // namespace tp5
