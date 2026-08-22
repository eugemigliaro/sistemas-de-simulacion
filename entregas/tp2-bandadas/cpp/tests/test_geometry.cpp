#include <cmath>
#include <numbers>

#include "test_support.hpp"
#include "tp2/geometry.hpp"

namespace {

constexpr double tolerance = 1e-12;

tp2::Particle particle(std::size_t id, double x, double y, double angle = 0.0) {
    return tp2::Particle{
        .id = id,
        .position = {.x = x, .y = y},
        .angle = angle,
    };
}

void test_wrapping() {
    EXPECT_NEAR(tp2::wrap_coordinate(10.02, 10.0), 0.02, tolerance);
    EXPECT_NEAR(tp2::wrap_coordinate(-0.03, 10.0), 9.97, tolerance);
    EXPECT_NEAR(tp2::wrap_coordinate(30.25, 10.0), 0.25, tolerance);
}

void test_periodic_distance_and_cutoff() {
    const auto left = particle(1, 0.2, 4.0);
    const auto right = particle(2, 9.8, 4.0);
    const tp2::Vec2 delta = tp2::periodic_displacement(left, right, 10.0);
    EXPECT_NEAR(delta.x, -0.4, tolerance);
    EXPECT_NEAR(delta.y, 0.0, tolerance);
    EXPECT_TRUE(tp2::are_neighbors(left, right, 10.0, 0.4));
    EXPECT_FALSE(tp2::are_neighbors(left, right, 10.0, 0.399));
}

void test_angle_normalization() {
    EXPECT_NEAR(tp2::normalize_angle(0.0), 0.0, tolerance);
    EXPECT_NEAR(
        tp2::normalize_angle(std::numbers::pi_v<double>),
        -std::numbers::pi_v<double>,
        tolerance
    );
    EXPECT_NEAR(
        tp2::normalize_angle(3.0 * std::numbers::pi_v<double>),
        -std::numbers::pi_v<double>,
        tolerance
    );
}

}  // namespace

int main() {
    test_wrapping();
    test_periodic_distance_and_cutoff();
    test_angle_normalization();
    return test::finish("Geometry tests");
}
