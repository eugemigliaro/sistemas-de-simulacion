#include <cmath>
#include <numbers>
#include <random>
#include <stdexcept>
#include <vector>

#include "test_support.hpp"
#include "tp4/forces.hpp"
#include "tp4/generation.hpp"

namespace {

using tp4::Vec2;

// Referencia O(N^2) escrita directamente desde F = -k xi e [TP04, p. 2].
std::vector<Vec2> brute_force(const tp4::Billiard& b, const std::vector<tp4::Particle>& particles) {
    const double contact = 2.0 * b.particle_radius;
    std::vector<Vec2> forces(particles.size());
    const auto spring = [&](const Vec2& self, const Vec2& other) {
        const double distance = tp4::norm(other - self);
        const double overlap = contact - distance;
        return overlap > 0.0 ? (-b.stiffness * overlap / distance) * (other - self) : Vec2{};
    };
    for (std::size_t i = 0; i < particles.size(); ++i) {
        const Vec2& p = particles[i].position;
        for (std::size_t j = 0; j < particles.size(); ++j) {
            if (i != j) {
                forces[i] += spring(p, particles[j].position);
            }
        }
        for (const Vec2& obstacle : tp4::obstacle_centers(b)) {
            forces[i] += spring(p, obstacle);
        }
        const Vec2 image = ((b.radius + b.particle_radius) / tp4::norm(p)) * p;
        forces[i] += spring(p, image);
    }
    return forces;
}

void grid_matches_brute_force() {
    tp4::Billiard b{};
    b.obstacle_x = 0.0175;
    // Posiciones al azar sin evitar superposiciones, hasta R + r/2: hay
    // contactos entre pares, con la pared y con los obstáculos.
    std::mt19937_64 rng(11);
    std::uniform_real_distribution<double> uniform(0.0, 1.0);
    std::vector<tp4::Particle> particles(400);
    for (auto& p : particles) {
        const double distance = (b.radius + 0.5 * b.particle_radius) * std::sqrt(uniform(rng));
        const double angle = 2.0 * std::numbers::pi * uniform(rng);
        p.position = {distance * std::cos(angle), distance * std::sin(angle)};
    }
    tp4::ForceField field(b);
    std::vector<Vec2> forces;
    std::vector<std::uint8_t> touching;
    field.compute(particles, forces, touching);
    const auto expected = brute_force(b, particles);
    double largest = 0.0;
    std::size_t nonzero = 0;
    for (std::size_t i = 0; i < particles.size(); ++i) {
        largest = std::max(largest, tp4::norm(forces[i] - expected[i]));
        nonzero += tp4::norm(expected[i]) > 0.0 ? 1 : 0;
    }
    CHECK(largest < 1e-9);
    CHECK(nonzero > 50);
}

void wall_force_is_radial_and_proportional_to_overlap() {
    tp4::Billiard b{};
    const std::vector<tp4::Particle> particles{{{0.3, 0.4 + 1e-3}, {}, tp4::Color::Fresh}};
    tp4::ForceField field(b);
    std::vector<Vec2> forces;
    std::vector<std::uint8_t> touching;
    field.compute(particles, forces, touching);
    const Vec2 p = particles[0].position;
    const double overlap = tp4::norm(p) + b.particle_radius - b.radius;
    CHECK_NEAR(tp4::norm(forces[0]), b.stiffness * overlap, 1e-9);
    CHECK_NEAR(forces[0].x * p.y - forces[0].y * p.x, 0.0, 1e-12);
    CHECK(tp4::dot(forces[0], p) < 0.0);
    CHECK(touching[0] == 0);
}

void obstacle_contact_is_reported() {
    tp4::Billiard b{};
    b.obstacle_x = 0.1;
    const std::vector<tp4::Particle> particles{
        {{0.1 + 0.03, 0.0}, {}, tp4::Color::Fresh},
        {{-0.1, 0.04}, {}, tp4::Color::Fresh},
    };
    tp4::ForceField field(b);
    std::vector<Vec2> forces;
    std::vector<std::uint8_t> touching;
    field.compute(particles, forces, touching);
    CHECK(touching[0] == 1);
    CHECK(touching[1] == 0);
    CHECK_NEAR(forces[0].x, b.stiffness * 0.005, 1e-9);
    CHECK_NEAR(forces[1].x, 0.0, 0.0);
}

void escaped_particle_is_an_error() {
    tp4::Billiard b{};
    const std::vector<tp4::Particle> particles{{{b.radius + b.particle_radius, 0.0}, {}, tp4::Color::Fresh}};
    tp4::ForceField field(b);
    std::vector<Vec2> forces;
    std::vector<std::uint8_t> touching;
    CHECK_THROWS(std::runtime_error, field.compute(particles, forces, touching));
}

}  // namespace

int main() {
    grid_matches_brute_force();
    wall_force_is_radial_and_proportional_to_overlap();
    obstacle_contact_is_reported();
    escaped_particle_is_an_error();
    return test::finish("fuerzas");
}
