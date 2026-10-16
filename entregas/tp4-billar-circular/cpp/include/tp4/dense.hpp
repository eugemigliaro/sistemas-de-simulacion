#pragma once
#include "tp4/billiard.hpp"

namespace tp4::billiard {
struct DenseResult {
    std::vector<Particle> particles;
    double acceptance = 0, mean_square_displacement = 0;
    std::size_t sweeps = 0, available_sites = 0;
};
inline DenseResult generate_dense(const Config& c, std::size_t sweeps = 500) {
    c.validate();
    if (sweeps == 0 || sweeps > 100000) throw std::invalid_argument("barridos Monte Carlo invalidos");
    std::mt19937_64 rng(c.seed);
    auto uniform = [&]() { return static_cast<double>(rng() >> 11) * 0x1.0p-53; };
    const double spacing = 2 * c.particle_radius * 1.0001;
    const int extent = static_cast<int>(std::ceil(c.radius / (spacing * .5))) + 2;
    std::vector<Vec> sites;
    // Orientacion/traslacion aleatorias; seleccionar la primera red con capacidad suficiente.
    for (int attempt = 0; attempt < 64; ++attempt) {
        sites.clear();
        const double angle = 2 * std::numbers::pi * uniform();
        const double dx = (uniform() - .5) * spacing, dy = (uniform() - .5) * spacing;
        for (int iy = -extent; iy <= extent; ++iy)
            for (int ix = -extent; ix <= extent; ++ix) {
                const double x = (ix + .5 * (std::abs(iy) % 2)) * spacing + dx;
                const double y = iy * spacing * std::sqrt(3.0) / 2 + dy;
                const Vec point{x * std::cos(angle) - y * std::sin(angle), x * std::sin(angle) + y * std::cos(angle)};
                if (fits(point, {}, c)) sites.push_back(point);
            }
        if (sites.size() >= c.n) break;
    }
    if (sites.size() < c.n) throw std::runtime_error("la red densa no tiene capacidad para N");
    // Fisher-Yates explicito: sin depender del algoritmo de std::shuffle.
    for (std::size_t i = sites.size(); i > 1; --i)
        std::swap(sites[i - 1], sites[static_cast<std::size_t>(uniform() * i)]);
    DenseResult result;
    result.available_sites = sites.size();
    result.sweeps = sweeps;
    result.particles.reserve(c.n);
    for (std::size_t i = 0; i < c.n; ++i) result.particles.push_back({sites[i], {}, -1});
    const auto start = result.particles;
    std::size_t accepted = 0;
    for (std::size_t sweep = 0; sweep < sweeps; ++sweep)
        for (std::size_t proposal = 0; proposal < c.n; ++proposal) {
            const std::size_t i = static_cast<std::size_t>(uniform() * c.n);
            const Vec old = result.particles[i].position;
            const Vec candidate = old + Vec{(uniform() - .5) * c.particle_radius / 2,
                                            (uniform() - .5) * c.particle_radius / 2};
            if (!fits(candidate, {}, c)) continue;
            bool valid = true;
            for (std::size_t j = 0; j < c.n; ++j)
                if (j != i && (candidate - result.particles[j].position).norm2() < 4 * c.particle_radius * c.particle_radius) {
                    valid = false; break;
                }
            if (valid) { result.particles[i].position = candidate; ++accepted; }
        }
    for (std::size_t i = 0; i < c.n; ++i) {
        result.mean_square_displacement += (result.particles[i].position - start[i].position).norm2() / c.n;
        const double angle = 2 * std::numbers::pi * uniform();
        result.particles[i].velocity = {c.speed * std::cos(angle), c.speed * std::sin(angle)};
    }
    result.acceptance = static_cast<double>(accepted) / (sweeps * c.n);
    validate_initial(result.particles, c);
    return result;
}
} // namespace tp4::billiard
