#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <limits>
#include <numbers>
#include <random>
#include <stdexcept>
#include <vector>

namespace tp4::billiard {
struct Vec {
    double x = 0, y = 0;
    Vec operator+(Vec b) const { return {x + b.x, y + b.y}; }
    Vec operator-(Vec b) const { return {x - b.x, y - b.y}; }
    Vec operator*(double a) const { return {x * a, y * a}; }
    double norm2() const { return x * x + y * y; }
};
struct Particle { Vec position, velocity; long long first_contact_step = -1; };
struct Config {
    // Por defecto h=1,25e-5 s (paso validado por energia hasta 600 s) y un estado cada 0,01 s.
    std::size_t n = 300, steps = 160000, save_every = 800;
    std::uint64_t seed = 1;
    double duration = 2, radius = .51, particle_radius = .0175, mass = .025;
    double stiffness = 10000, speed = 1, obstacle_x = .0175;
    bool obstacles = false;
    double dt() const { return duration / static_cast<double>(steps); }
    void validate() const {
        for (double value : {duration, radius, particle_radius, mass, stiffness, speed, obstacle_x})
            if (!std::isfinite(value)) throw std::invalid_argument("configuracion no finita");
        if (n == 0 || steps == 0 || save_every == 0 || steps % save_every != 0 ||
            steps >= static_cast<std::size_t>(std::numeric_limits<long long>::max()) ||
            duration <= 0 || radius <= particle_radius || particle_radius <= 0 || mass <= 0 ||
            stiffness <= 0 || speed < 0 || !(dt() > 0) || !std::isfinite(stiffness / mass))
            throw std::invalid_argument("configuracion fisica o paso/cadencia invalido");
        if (obstacles && (obstacle_x < particle_radius || obstacle_x > radius - particle_radius))
            throw std::invalid_argument("obstaculos solapados o fuera del dominio");
        if (radius / particle_radius > 1000 || n > 1000000)
            throw std::invalid_argument("configuracion excede limites de memoria");
    }
};
inline bool fits(Vec p, const std::vector<Particle>& particles, const Config& c) {
    if (p.norm2() > std::pow(c.radius - c.particle_radius, 2)) return false;
    const double diameter2 = 4 * c.particle_radius * c.particle_radius;
    if (c.obstacles)
        for (double ox : {-c.obstacle_x, c.obstacle_x})
            if ((p - Vec{ox, 0}).norm2() < diameter2) return false;
    for (const auto& other : particles)
        if ((p - other.position).norm2() < diameter2) return false;
    return true;
}
inline std::vector<Particle> generate(const Config& c) {
    c.validate();
    if (static_cast<double>(c.n) * c.particle_radius * c.particle_radius > c.radius * c.radius)
        throw std::invalid_argument("area de particulas mayor al dominio");
    std::mt19937_64 rng(c.seed);
    // Conversion explicita de los 53 bits altos: reproducible sin uniform_real_distribution.
    auto uniform = [&]() { return static_cast<double>(rng() >> 11) * 0x1.0p-53; };
    std::vector<Particle> particles;
    particles.reserve(c.n);
    std::size_t rejected = 0;
    while (particles.size() < c.n) {
        const double radial = (c.radius - c.particle_radius) * std::sqrt(uniform());
        const double angle = 2 * std::numbers::pi * uniform();
        const Vec p{radial * std::cos(angle), radial * std::sin(angle)};
        if (!fits(p, particles, c)) {
            if (++rejected > 2000000)
                throw std::runtime_error("inicializacion por rechazo agotada: no se pudo ubicar N sin solapamientos");
            continue;
        }
        const double direction = 2 * std::numbers::pi * uniform();
        particles.push_back({p, {c.speed * std::cos(direction), c.speed * std::sin(direction)}, -1});
    }
    return particles;
}
struct ForceResult { std::vector<Vec> force; std::vector<bool> obstacle_contact; };
// Listas de celdas reutilizadas entre pasos para no reservar memoria en cada uno.
struct CellList { std::vector<int> head, next; };
inline void forces(const std::vector<Particle>& particles, const Config& c, ForceResult& result, CellList& grid) {
    const std::size_t n = particles.size();
    result.force.assign(n, Vec{});
    result.obstacle_contact.assign(n, false);
    const double width = 2 * c.particle_radius;
    const int cells = static_cast<int>(std::ceil(2 * c.radius / width));
    grid.head.assign(static_cast<std::size_t>(cells) * cells, -1);
    grid.next.assign(n, -1);
    auto& head = grid.head;
    auto& next = grid.next;
    auto index = [&](double coordinate) {
        return std::clamp(static_cast<int>(std::floor((coordinate + c.radius) / width)), 0, cells - 1);
    };
    for (std::size_t i = 0; i < n; ++i) {
        const Vec p = particles[i].position;
        if (!std::isfinite(p.x) || !std::isfinite(p.y) || p.norm2() > std::pow(c.radius + c.particle_radius, 2))
            throw std::runtime_error("estado fuera del dominio de contacto: reducir dt");
        const int cell = index(p.x) + cells * index(p.y);
        next[i] = head[cell];
        head[cell] = static_cast<int>(i);
    }
    for (std::size_t i = 0; i < n; ++i) {
        const Vec p = particles[i].position;
        const int cx = index(p.x), cy = index(p.y);
        for (int y = std::max(0, cy - 1); y <= std::min(cells - 1, cy + 1); ++y)
            for (int x = std::max(0, cx - 1); x <= std::min(cells - 1, cx + 1); ++x)
                for (int j = head[x + cells * y]; j >= 0; j = next[j]) {
                    if (static_cast<std::size_t>(j) <= i) continue;
                    const Vec delta = particles[j].position - p;
                    const double d2 = delta.norm2();
                    if (d2 >= width * width) continue;
                    if (d2 == 0) throw std::runtime_error("centros de particulas coincidentes");
                    const double d = std::sqrt(d2);
                    const Vec f = delta * (-c.stiffness * (width - d) / d);
                    result.force[i] = result.force[i] + f;
                    result.force[j] = result.force[j] - f;
                }
        const double distance = std::sqrt(p.norm2());
        const double overlap = distance + c.particle_radius - c.radius;
        if (overlap > 0) // Imagen (R+r)*p/|p|; fuerza radial hacia el interior.
            result.force[i] = result.force[i] + p * (-c.stiffness * overlap / distance);
        if (c.obstacles)
            for (double ox : {-c.obstacle_x, c.obstacle_x}) {
                const Vec delta = Vec{ox, 0} - p;
                const double d = std::sqrt(delta.norm2());
                if (d >= width) continue;
                if (d == 0) throw std::runtime_error("centro de particula coincide con obstaculo");
                result.force[i] = result.force[i] + delta * (-c.stiffness * (width - d) / d);
                result.obstacle_contact[i] = true;
            }
    }
}
inline ForceResult forces(const std::vector<Particle>& particles, const Config& c) {
    ForceResult result;
    CellList grid;
    forces(particles, c, result, grid);
    return result;
}
inline void validate_initial(const std::vector<Particle>& particles, const Config& c) {
    c.validate();
    if (particles.size() != c.n) throw std::invalid_argument("N incompatible con estado inicial");
    std::vector<Particle> previous;
    for (const auto& p : particles) {
        if (!std::isfinite(p.position.x) || !std::isfinite(p.position.y) ||
            !std::isfinite(p.velocity.x) || !std::isfinite(p.velocity.y) ||
            p.first_contact_step != -1 || !fits(p.position, previous, c))
            throw std::invalid_argument("estado inicial invalido, solapado o usado");
        previous.push_back(p);
    }
}
using FrameSink = std::function<void(std::size_t, double, const std::vector<Particle>&)>;
inline void simulate(const Config& c, std::vector<Particle> particles, const FrameSink& emit) {
    validate_initial(particles, c);
    ForceResult current_forces;
    CellList grid;
    forces(particles, c, current_forces, grid);
    std::vector<Vec> previous(c.n), future(c.n);
    const double h = c.dt();
    for (std::size_t i = 0; i < c.n; ++i)
        previous[i] = particles[i].position - particles[i].velocity * h + current_forces.force[i] * (h * h / (2 * c.mass));
    for (std::size_t step = 0; step <= c.steps; ++step) {
        if (step != 0) forces(particles, c, current_forces, grid);
        for (std::size_t i = 0; i < c.n; ++i) {
            if (current_forces.obstacle_contact[i] && particles[i].first_contact_step < 0)
                particles[i].first_contact_step = static_cast<long long>(step);
            future[i] = particles[i].position * 2 - previous[i] + current_forces.force[i] * (h * h / c.mass);
            if (step != 0) particles[i].velocity = (future[i] - previous[i]) * (1 / (2 * h));
            if (!std::isfinite(future[i].x) || !std::isfinite(future[i].y) ||
                !std::isfinite(particles[i].velocity.x) || !std::isfinite(particles[i].velocity.y))
                throw std::runtime_error("estado no finito: reducir dt");
        }
        if (step % c.save_every == 0)
            emit(step, step == c.steps ? c.duration : static_cast<double>(step) * h, particles);
        for (std::size_t i = 0; i < c.n; ++i) {
            previous[i] = particles[i].position;
            particles[i].position = future[i];
        }
    }
}
} // namespace tp4::billiard
