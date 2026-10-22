#include <algorithm>
#include <cmath>
#include <numbers>
#include <stdexcept>
#include <vector>

#include "test_support.hpp"
#include "tp4/generation.hpp"
#include "tp4/simulation.hpp"

namespace {

using tp4::Color;
using tp4::Particle;
using tp4::Vec2;

double overlap_energy(const tp4::Billiard& b, double distance) {
    const double overlap = std::max(0.0, 2.0 * b.particle_radius - distance);
    return 0.5 * b.stiffness * overlap * overlap;
}

// Cinética más potencial de todos los resortes, cada par contado una vez [T04, p. 42].
double energy(const tp4::Billiard& b, const std::vector<Particle>& particles) {
    double total = 0.0;
    for (std::size_t i = 0; i < particles.size(); ++i) {
        const Particle& p = particles[i];
        total += 0.5 * b.particle_mass * tp4::norm_squared(p.velocity);
        const double wall = std::max(0.0, tp4::norm(p.position) + b.particle_radius - b.radius);
        total += 0.5 * b.stiffness * wall * wall;
        for (const Vec2& obstacle : tp4::obstacle_centers(b)) {
            total += overlap_energy(b, tp4::norm(p.position - obstacle));
        }
        for (std::size_t j = i + 1; j < particles.size(); ++j) {
            total += overlap_energy(b, tp4::norm(p.position - particles[j].position));
        }
    }
    return total;
}

tp4::Run run_until(double tf, double dt, std::uint64_t output_every = 1) {
    return {dt, static_cast<std::uint64_t>(std::round(tf / dt)), output_every};
}

// Choque frontal: el contacto dura medio período del resorte con masa
// reducida m/2, pi sqrt(m / 2k), y las velocidades se intercambian.
void head_on_collision_matches_the_spring_solution() {
    const tp4::Billiard b{};
    const std::vector<Particle> particles{{{-0.05, 0.0}, {1.0, 0.0}}, {{0.05, 0.0}, {-1.0, 0.0}}};
    const double first_contact = (0.1 - 2.0 * b.particle_radius) / 2.0;
    const double separation = first_contact + std::numbers::pi * std::sqrt(b.particle_mass / (2.0 * b.stiffness));
    const double tf = 0.05;
    const double e0 = energy(b, particles);
    double worst_energy = 0.0;
    double worst_momentum = 0.0;
    std::vector<Particle> last;
    tp4::simulate(b, particles, run_until(tf, 1e-6, 100), [&](auto, double, const auto& state) {
        worst_energy = std::max(worst_energy, std::abs(energy(b, state) / e0 - 1.0));
        worst_momentum = std::max(worst_momentum, std::abs(state[0].velocity.x + state[1].velocity.x));
        last = state;
    });
    CHECK(worst_energy < 1e-6);
    CHECK(worst_momentum < 1e-9);
    CHECK_NEAR(last[0].velocity.x, -1.0, 1e-6);
    CHECK_NEAR(last[0].position.x, -b.particle_radius - (tf - separation), 1e-6);
}

// Contra un obstáculo fijo el contacto dura pi sqrt(m / k) y la partícula
// rebota con la misma rapidez. Queda usada desde el primer contacto.
void obstacle_bounce_turns_the_particle_used() {
    tp4::Billiard b{};
    b.obstacle_x = 0.1;
    const std::vector<Particle> particles{{{0.2, 0.0}, {-1.0, 0.0}}};
    const double first_contact = 0.2 - 0.1 - 2.0 * b.particle_radius;
    bool reverted = false;
    bool used_early = false;
    bool seen_used = false;
    std::vector<Particle> last;
    tp4::simulate(b, particles, run_until(0.1, 1e-6, 10), [&](auto, double time, const auto& state) {
        const bool used = state[0].color == Color::Used;
        used_early = used_early || (used && time < first_contact - 1e-5);
        reverted = reverted || (seen_used && !used);
        seen_used = seen_used || used;
        last = state;
    });
    CHECK(!used_early);
    CHECK(!reverted);
    CHECK(last[0].color == Color::Used);
    CHECK_NEAR(last[0].velocity.x, 1.0, 1e-6);
    const double release = first_contact + std::numbers::pi * std::sqrt(b.particle_mass / b.stiffness);
    CHECK_NEAR(last[0].position.x, 0.1 + 2.0 * b.particle_radius + (0.1 - release), 1e-6);
}

// La fuerza de la pared es central: se conservan la energía y el momento
// angular respecto del centro aunque el choque sea oblicuo.
void oblique_wall_contact_conserves_energy_and_angular_momentum() {
    const tp4::Billiard b{};
    const std::vector<Particle> particles{{{0.48, 0.0}, {1.0, 0.3}}};
    const double e0 = energy(b, particles);
    double worst_energy = 0.0;
    double worst_angular = 0.0;
    std::vector<Particle> last;
    tp4::simulate(b, particles, run_until(0.06, 1e-6, 50), [&](auto, double, const auto& state) {
        const Particle& p = state[0];
        worst_energy = std::max(worst_energy, std::abs(energy(b, state) / e0 - 1.0));
        worst_angular = std::max(worst_angular,
                                 std::abs(p.position.x * p.velocity.y - p.position.y * p.velocity.x - 0.144));
        last = state;
    });
    CHECK(worst_energy < 1e-6);
    CHECK(worst_angular < 1e-9);
    CHECK(last[0].velocity.x < 0.0);
}

void frames_follow_the_output_interval() {
    tp4::Billiard b{};
    const auto particles = tp4::generate(b, {.particle_count = 20, .seed = 2});
    std::vector<std::uint64_t> steps;
    std::vector<double> times;
    tp4::simulate(b, particles, {1e-4, 100, 10}, [&](std::uint64_t step, double time, const auto& state) {
        steps.push_back(step);
        times.push_back(time);
        CHECK(state.size() == 20);
    });
    CHECK(steps.size() == 11);
    CHECK(steps.front() == 0 && steps.back() == 100);
    CHECK_NEAR(times.back(), 0.01, 1e-15);
}

void many_body_run_conserves_energy() {
    tp4::Billiard b{};
    b.obstacle_x = b.particle_radius;
    const auto particles = tp4::generate(b, {.particle_count = 200, .seed = 5});
    const double e0 = energy(b, particles);
    double worst = 0.0;
    std::size_t used = 0;
    tp4::simulate(b, particles, run_until(1.0, 1e-5, 1000), [&](auto, double, const auto& state) {
        worst = std::max(worst, std::abs(energy(b, state) / e0 - 1.0));
        used = static_cast<std::size_t>(std::count_if(state.begin(), state.end(),
                                                      [](const Particle& p) { return p.color == Color::Used; }));
    });
    CHECK(worst < 1e-4);
    CHECK(used > 0);
}

void rejects_invalid_runs() {
    const tp4::Billiard b{};
    const std::vector<Particle> one{{{0.0, 0.0}, {1.0, 0.0}}};
    const auto ignore = [](auto, double, const auto&) {};
    CHECK_THROWS(std::invalid_argument, tp4::simulate(b, one, {1e-4, 100, 7}, ignore));
    CHECK_THROWS(std::invalid_argument, tp4::simulate(b, one, {0.0, 100, 1}, ignore));
    CHECK_THROWS(std::invalid_argument, tp4::simulate(b, {}, {1e-4, 100, 1}, ignore));
    const std::vector<Particle> fast{{{0.4, 0.0}, {50.0, 0.0}}};
    CHECK_THROWS(std::runtime_error, tp4::simulate(b, fast, {1e-3, 1000, 1}, ignore));
}

}  // namespace

int main() {
    head_on_collision_matches_the_spring_solution();
    obstacle_bounce_turns_the_particle_used();
    oblique_wall_contact_conserves_energy_and_angular_momentum();
    frames_follow_the_output_interval();
    many_body_run_conserves_energy();
    rejects_invalid_runs();
    return test::finish("simulacion");
}
