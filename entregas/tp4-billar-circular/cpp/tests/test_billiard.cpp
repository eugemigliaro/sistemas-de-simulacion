#include "tp4/billiard.hpp"
#include <iostream>

using namespace tp4::billiard;
void require(bool ok, const char* message) { if (!ok) throw std::runtime_error(message); }
double energy(const std::vector<Particle>& p, const Config& c) {
    double e = 0;
    for (std::size_t i = 0; i < p.size(); ++i) {
        e += c.mass * p[i].velocity.norm2() / 2;
        const double wall = std::max(0.0, std::sqrt(p[i].position.norm2()) + c.particle_radius - c.radius);
        e += c.stiffness * wall * wall / 2;
        if (c.obstacles)
            for (double x : {-c.obstacle_x, c.obstacle_x}) {
                const double overlap = std::max(0.0, 2 * c.particle_radius - std::sqrt((p[i].position - Vec{x, 0}).norm2()));
                e += c.stiffness * overlap * overlap / 2;
            }
        for (std::size_t j = i + 1; j < p.size(); ++j) {
            const double overlap = std::max(0.0, 2 * c.particle_radius - std::sqrt((p[i].position - p[j].position).norm2()));
            e += c.stiffness * overlap * overlap / 2;
        }
    }
    return e;
}
int main() {
    try {
        Config c;
        auto p = generate(c), repeated = generate(c);
        validate_initial(p, c);
        require(p.size() == 300, "N inicial");
        for (std::size_t i = 0; i < p.size(); ++i) {
            require((p[i].position - repeated[i].position).norm2() == 0, "semilla no reproducible");
            require(std::abs(p[i].velocity.norm2() - 1) < 1e-14, "rapidez inicial");
        }
        // Oraculo independiente O(N²), perturbando para obtener contactos en muchas celdas.
        for (auto& particle : p) particle.position = particle.position * .8;
        const auto calculated = forces(p, c);
        std::vector<Vec> expected(p.size());
        for (std::size_t i = 0; i < p.size(); ++i)
            for (std::size_t j = i + 1; j < p.size(); ++j) {
                const Vec delta = p[i].position - p[j].position;
                const double d = std::sqrt(delta.norm2());
                if (d < 2 * c.particle_radius) {
                    const Vec f = delta * (c.stiffness * (2 * c.particle_radius - d) / d);
                    expected[i] = expected[i] + f;
                    expected[j] = expected[j] - f;
                }
            }
        Vec total;
        for (std::size_t i = 0; i < p.size(); ++i) {
            require((calculated.force[i] - expected[i]).norm2() < 1e-18, "grilla difiere del oraculo");
            total = total + calculated.force[i];
        }
        require(total.norm2() < 1e-18, "accion y reaccion");
        c.n = 1;
        for (Vec point : {Vec{.5, 0}, Vec{.3, .4}}) {
            const auto f = forces({{point, {}, -1}}, c).force[0];
            require(std::abs(f.x * point.y - f.y * point.x) < 1e-12, "pared no radial");
            require(std::abs(std::sqrt(f.norm2()) - 75) < 1e-10, "magnitud pared");
            require(f.x * point.x + f.y * point.y < 0, "pared atractiva");
        }
        require(forces({{{0, 0}, {}, -1}}, c).force[0].norm2() == 0, "fuerza espuria en el centro");
        // Choque binario: tiempo de contacto analitico pi*sqrt(m/(2k)).
        c.n = 2; c.duration = .04; c.steps = 20000; c.save_every = 1;
        std::vector<Particle> binary{{{-.04, 0}, {1, 0}, -1}, {{.04, 0}, {-1, 0}, -1}};
        const double end_contact = (.04 - c.particle_radius) + std::numbers::pi * std::sqrt(c.mass / (2 * c.stiffness));
        const double expected_left = -c.particle_radius - (c.duration - end_contact);
        const double e0 = energy(binary, c);
        double max_error = 0;
        simulate(c, binary, [&](std::size_t step, double, const auto& state) {
            max_error = std::max(max_error, std::abs(energy(state, c) / e0 - 1));
            require(std::abs(state[0].velocity.x + state[1].velocity.x) < 1e-10, "momento binario");
            if (step == c.steps) {
                require(std::abs(state[0].velocity.x + 1) < 1e-5, "intercambio velocidades");
                require(std::abs(state[0].position.x - expected_left) < 1e-6, "tiempo analitico de contacto");
            }
        });
        require(max_error < 1e-5, "energia binaria");
        // Obstaculo fijo: conversion una sola vez y reflexion elastica.
        c.n = 1; c.obstacles = true; c.obstacle_x = .1; c.duration = .08; c.steps = 40000;
        long long first = -1;
        simulate(c, {{{.2, 0}, {-1, 0}, -1}}, [&](std::size_t step, double, const auto& state) {
            const auto contact = state[0].first_contact_step;
            if (first >= 0) require(contact == first, "conversion reversible o repetida");
            if (contact >= 0 && first < 0) first = contact;
            require(state.size() == 1, "N cambio");
            if (step == c.steps) require(std::abs(state[0].velocity.x - 1) < 1e-5, "reflexion obstaculo");
        });
        require(first >= 0 && std::abs(static_cast<double>(first) * c.dt() - .065) < 2 * c.dt(), "primer contacto incorrecto");
        // Contacto oblicuo con pared: energia y momento angular, normal recalculada.
        c.obstacles = false; c.duration = .04; c.steps = 20000;
        const std::vector<Particle> oblique{{{.48, 0}, {1, .3}, -1}};
        const double initial_e = energy(oblique, c);
        simulate(c, oblique, [&](std::size_t, double, const auto& state) {
            require(std::abs(energy(state, c) / initial_e - 1) < 1e-5, "energia pared oblicua");
            const auto& q = state[0];
            require(std::abs(q.position.x * q.velocity.y - q.position.y * q.velocity.x - .144) < 1e-9,
                    "momento angular pared oblicua");
        });
        std::cout << "Billar: geometria, grilla/oraculo, choques, pared, energia y conversion OK\n";
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
