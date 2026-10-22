#include <cmath>
#include <stdexcept>
#include <vector>

#include "test_support.hpp"
#include "tp4/generation.hpp"

namespace {

tp4::Billiard with_obstacles(double x0) {
    tp4::Billiard billiard{};
    billiard.obstacle_x = x0;
    return billiard;
}

void check_valid_layout(const tp4::Billiard& b, const std::vector<tp4::Particle>& particles) {
    const double contact = 2.0 * b.particle_radius;
    for (std::size_t i = 0; i < particles.size(); ++i) {
        const tp4::Particle& p = particles[i];
        CHECK(tp4::norm(p.position) <= b.radius - b.particle_radius);
        CHECK_NEAR(tp4::norm(p.velocity), b.initial_speed, 1e-12);
        CHECK(p.color == tp4::Color::Fresh);
        for (const tp4::Vec2& obstacle : tp4::obstacle_centers(b)) {
            CHECK(tp4::norm(p.position - obstacle) >= contact);
        }
        for (std::size_t j = i + 1; j < particles.size(); ++j) {
            CHECK(tp4::norm(p.position - particles[j].position) >= contact);
        }
    }
}

void random_layout_is_valid_and_reproducible() {
    const tp4::Billiard b = with_obstacles(0.0175);
    const tp4::Generation generation{.particle_count = 300, .seed = 7};
    const auto first = tp4::generate(b, generation);
    const auto again = tp4::generate(b, generation);
    CHECK(first.size() == 300);
    check_valid_layout(b, first);
    bool identical = true;
    for (std::size_t i = 0; i < first.size(); ++i) {
        identical = identical && first[i].position == again[i].position && first[i].velocity == again[i].velocity;
    }
    CHECK(identical);
    const auto other = tp4::generate(b, {.particle_count = 300, .seed = 8});
    CHECK(!(other[0].position == first[0].position));
}

void random_layout_fills_the_area() {
    // La mitad de las partículas debería quedar a menos de (R - r)/sqrt(2) del centro.
    const tp4::Billiard b{};
    const auto particles = tp4::generate(b, {.particle_count = 400, .seed = 3});
    const double half_area_radius = (b.radius - b.particle_radius) / std::sqrt(2.0);
    double inner = 0.0;
    for (const auto& p : particles) {
        inner += tp4::norm(p.position) < half_area_radius ? 1.0 : 0.0;
    }
    CHECK_NEAR(inner / 400.0, 0.5, 0.1);
}

void lattice_reaches_high_densities() {
    const tp4::Billiard b = with_obstacles(0.0175);
    CHECK_THROWS(std::runtime_error,
                 (void)tp4::generate(b, {.particle_count = 650, .seed = 1, .max_attempts = 20000}));
    const auto particles = tp4::generate(
        b, {.particle_count = 650, .seed = 1, .layout = tp4::Layout::Lattice, .lattice_sweeps = 50});
    CHECK(particles.size() == 650);
    check_valid_layout(b, particles);
}

void rejects_invalid_configurations() {
    CHECK_THROWS(std::invalid_argument, (void)tp4::generate(with_obstacles(0.01), {.particle_count = 10}));
    CHECK_THROWS(std::invalid_argument, (void)tp4::generate(with_obstacles(0.5), {.particle_count = 10}));
    CHECK_THROWS(std::invalid_argument, (void)tp4::generate(tp4::Billiard{}, {.particle_count = 0}));
    CHECK_THROWS(std::invalid_argument, (void)tp4::parse_layout("hexagonal"));
}

}  // namespace

int main() {
    random_layout_is_valid_and_reproducible();
    random_layout_fills_the_area();
    lattice_reaches_high_densities();
    rejects_invalid_configurations();
    return test::finish("generacion");
}
