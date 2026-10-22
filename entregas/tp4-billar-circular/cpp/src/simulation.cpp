#include "tp4/simulation.hpp"

#include <cmath>
#include <stdexcept>

#include "tp4/forces.hpp"

namespace tp4 {

void validate(const Run& run) {
    if (!std::isfinite(run.dt) || run.dt <= 0.0 || run.steps == 0) {
        throw std::invalid_argument("dt y la cantidad de pasos deben ser positivos");
    }
    if (run.output_every == 0 || run.steps % run.output_every != 0) {
        throw std::invalid_argument("la cantidad de pasos debe ser multiplo de output_every");
    }
}

void simulate(const Billiard& billiard, std::vector<Particle> particles, const Run& run, const FrameSink& sink) {
    validate(billiard);
    validate(run);
    if (particles.empty()) {
        throw std::invalid_argument("no hay particulas para simular");
    }
    const std::size_t n = particles.size();
    const double dt = run.dt;
    const double factor = dt * dt / billiard.particle_mass;
    ForceField field(billiard);
    std::vector<Vec2> forces;
    std::vector<std::uint8_t> touching;
    std::vector<Vec2> previous(n);
    std::vector<Vec2> next(n);

    field.compute(particles, forces, touching);
    for (std::size_t i = 0; i < n; ++i) {
        previous[i] = particles[i].position - dt * particles[i].velocity + 0.5 * factor * forces[i];
    }
    for (std::uint64_t step = 0; step <= run.steps; ++step) {
        if (step > 0) {
            field.compute(particles, forces, touching);
        }
        for (std::size_t i = 0; i < n; ++i) {
            Particle& particle = particles[i];
            if (touching[i] != 0) {
                particle.color = Color::Used;
            }
            next[i] = 2.0 * particle.position - previous[i] + factor * forces[i];
            if (step > 0) {
                particle.velocity = (0.5 / dt) * (next[i] - previous[i]);
            }
        }
        if (step % run.output_every == 0) {
            sink(step, static_cast<double>(step) * dt, particles);
        }
        for (std::size_t i = 0; i < n; ++i) {
            previous[i] = particles[i].position;
            particles[i].position = next[i];
        }
    }
}

}  // namespace tp4
