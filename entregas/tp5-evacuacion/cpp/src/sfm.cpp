#include "tp5/sfm.hpp"

#include <algorithm>
#include <cmath>

namespace tp5 {

CellGrid::CellGrid(const Params& p, const Room& room)
    : x0_(-1.0),
      y0_(-(room.exit_distance + 1.0)) {
    // La franja de afuera llega a exit_distance; un metro de margen alrededor.
    const double width = p.side + 2.0;
    const double height = p.side + room.exit_distance + 2.0;
    const double min_size = 2.0 * p.radius_max;
    columns_ = std::max(1, static_cast<int>(width / min_size));
    rows_ = std::max(1, static_cast<int>(height / min_size));
    size_ = std::max(width / columns_, height / rows_);
    columns_ = std::max(1, static_cast<int>(std::ceil(width / size_)));
    rows_ = std::max(1, static_cast<int>(std::ceil(height / size_)));
    head_.assign(static_cast<std::size_t>(columns_ * rows_), -1);
    next_.assign(static_cast<std::size_t>(p.agents), -1);
}

int CellGrid::cell_index(const Vec2& position) const noexcept {
    const int column = std::clamp(static_cast<int>(std::floor((position.x - x0_) / size_)), 0, columns_ - 1);
    const int row = std::clamp(static_cast<int>(std::floor((position.y - y0_) / size_)), 0, rows_ - 1);
    return row * columns_ + column;
}

void CellGrid::build(const std::vector<Agent>& agents, const std::vector<std::size_t>& indices) {
    std::fill(head_.begin(), head_.end(), -1);
    // Al revés, para que cada celda quede en orden creciente de índice.
    for (auto it = indices.rbegin(); it != indices.rend(); ++it) {
        const std::size_t i = *it;
        const auto cell = static_cast<std::size_t>(cell_index(agents[i].position));
        next_[i] = head_[cell];
        head_[cell] = static_cast<int>(i);
    }
}

ForceField::ForceField(const Params& p, const Room& room)
    : params_(p),
      room_(room),
      grid_(p, room),
      spring_(static_cast<std::size_t>(p.agents)),
      count_(static_cast<std::size_t>(p.agents), 0),
      noise_(static_cast<std::size_t>(p.agents)),
      rng_(p.seed ^ 0x9e3779b97f4a7c15ull) {}

void ForceField::refresh_noise() {
    if (params_.noise <= 0.0) return;
    // Box-Muller con la misma conversión a [0, 1) que las condiciones iniciales.
    auto uniform = [&] { return static_cast<double>(rng_() >> 11) * 0x1.0p-53; };
    for (Vec2& f : noise_) {
        const double u = 1.0 - uniform();
        const double radius = std::sqrt(-2.0 * std::log(u));
        const double angle = 2.0 * 3.14159265358979323846 * uniform();
        f = {radius * std::cos(angle), radius * std::sin(angle)};
    }
}

void ForceField::find_contacts(const std::vector<Agent>& agents, const std::vector<std::size_t>& indices) {
    contacts_.clear();
    for (std::size_t i : indices) {
        spring_[i] = {};
        count_[i] = 0;
    }
    grid_.build(agents, indices);
    grid_.for_each_pair(agents, [&](std::size_t i, std::size_t j) {
        const Vec2 offset = agents[i].position - agents[j].position;
        const double sigma = agents[i].radius + agents[j].radius;
        const double distance_squared = norm_squared(offset);
        if (distance_squared >= sigma * sigma) return;
        const double distance = std::sqrt(distance_squared);
        const Vec2 n = (1.0 / distance) * offset;
        const double xi = sigma - distance;
        contacts_.push_back({i, j, -1, n, perpendicular(n), xi});
        const Vec2 force = (params_.kn * xi) * n;
        spring_[i] += force;
        spring_[j] -= force;
        ++count_[i];
        ++count_[j];
    });
    for (std::size_t i : indices) {
        const Agent& agent = agents[i];
        // Solo las paredes cercanas pueden tocarlo: descarte barato por coordenadas.
        const Vec2& x = agent.position;
        const double r = agent.radius;
        for (int w = 0; w < static_cast<int>(room_.walls.size()); ++w) {
            const Segment& wall = room_.walls[static_cast<std::size_t>(w)];
            if (std::min(wall.a.x, wall.b.x) - r > x.x || std::max(wall.a.x, wall.b.x) + r < x.x ||
                std::min(wall.a.y, wall.b.y) - r > x.y || std::max(wall.a.y, wall.b.y) + r < x.y) {
                continue;
            }
            const Vec2 contact = closest_point(wall, x);
            const Vec2 offset = x - contact;
            const double distance = norm(offset);
            if (distance >= r || distance <= 0.0) continue;
            const Vec2 n = (1.0 / distance) * offset;
            const double xi = r - distance;
            contacts_.push_back({i, i, w, n, perpendicular(n), xi});
            spring_[i] += (params_.kn * xi) * n;
            ++count_[i];
        }
    }
}

void ForceField::accelerations(const std::vector<Agent>& agents, const std::vector<std::size_t>& indices,
                               std::vector<Vec2>& out) const {
    // out[i] acumula fuerza / m; se usa el arreglo completo indexado por agente.
    for (std::size_t i : indices) {
        out[i] = spring_[i];
    }
    for (const Contact& c : contacts_) {
        const Agent& a = agents[c.i];
        if (c.wall >= 0) {
            // Pared quieta: -kappa xi (v_i . t) t [B26, p. 2].
            out[c.i] -= (params_.kt * c.xi * dot(a.velocity, c.t)) * c.t;
        } else {
            // kappa xi (v_j - v_i) . t t sobre i, y lo opuesto sobre j [B26, pp. 1-2].
            const Agent& b = agents[c.j];
            const Vec2 friction = (params_.kt * c.xi * dot(b.velocity - a.velocity, c.t)) * c.t;
            out[c.i] += friction;
            out[c.j] -= friction;
        }
    }
    const double noise = params_.noise * params_.desired_speed / params_.tau;  // desvío de la aceleración
    for (std::size_t i : indices) {
        const Agent& a = agents[i];
        const Vec2 desired = params_.desired_speed * room_.desired_direction(a.position, a.outside);
        out[i] = (1.0 / params_.tau) * (desired - a.velocity) + (1.0 / a.mass) * out[i];
        if (noise > 0.0 && count_[i] > 0) out[i] += noise * noise_[i];
    }
}

Beeman::Beeman(const Params& p, const Room& room)
    : params_(p),
      forces_(p, room),
      noise_every_(std::max<std::uint64_t>(1, static_cast<std::uint64_t>(std::llround(p.noise_time / p.dt)))),
      old_velocity_(static_cast<std::size_t>(p.agents)),
      predicted_acceleration_(static_cast<std::size_t>(p.agents)),
      new_acceleration_(static_cast<std::size_t>(p.agents)) {}

void Beeman::step(std::vector<Agent>& agents, const std::vector<std::size_t>& indices) {
    const double h = params_.dt;
    if (steps_++ % noise_every_ == 0) forces_.refresh_noise();
    for (std::size_t i : indices) {
        Agent& a = agents[i];
        old_velocity_[i] = a.velocity;
        a.position += h * a.velocity + (h * h) * ((2.0 / 3.0) * a.acceleration - (1.0 / 6.0) * a.previous_acceleration);
        a.velocity = a.velocity + h * (1.5 * a.acceleration - 0.5 * a.previous_acceleration);  // predicción
    }
    forces_.find_contacts(agents, indices);
    forces_.accelerations(agents, indices, predicted_acceleration_);
    for (std::size_t i : indices) {
        Agent& a = agents[i];
        a.velocity = old_velocity_[i] + h * ((1.0 / 3.0) * predicted_acceleration_[i] + (5.0 / 6.0) * a.acceleration -
                                             (1.0 / 6.0) * a.previous_acceleration);
    }
    forces_.accelerations(agents, indices, new_acceleration_);
    for (std::size_t i : indices) {
        Agent& a = agents[i];
        a.previous_acceleration = a.acceleration;
        a.acceleration = new_acceleration_[i];
    }
}

}  // namespace tp5
