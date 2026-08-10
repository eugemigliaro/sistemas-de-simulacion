#include <cmath>
#include <cstddef>
#include <limits>

#include "tp1/geometry.hpp"
#include "test_support.hpp"

namespace {

constexpr double kTolerance = 1e-12;

tp1::Particle particle(
    std::size_t id,
    double x,
    double y,
    double radius = 0.5
) {
    return tp1::Particle{
        .id = id,
        .position = {.x = x, .y = y},
        .velocity = {.x = 0.0, .y = 0.0},
        .radius = radius,
        .property = 1.0,
    };
}

void test_wall_geometry() {
    const tp1::Domain domain{
        .side = 10.0,
        .boundary = tp1::BoundaryCondition::Walls,
    };
    const auto first = particle(1, 1.0, 1.0);
    const auto second = particle(2, 4.0, 5.0);

    const tp1::Vec2 delta = tp1::displacement(first, second, domain);
    EXPECT_NEAR(delta.x, 3.0, kTolerance);
    EXPECT_NEAR(delta.y, 4.0, kTolerance);
    EXPECT_NEAR(tp1::center_distance(first, second, domain), 5.0, kTolerance);
    EXPECT_NEAR(tp1::edge_distance(first, second, domain), 4.0, kTolerance);
}

void test_strict_neighbor_threshold() {
    const tp1::Domain domain{
        .side = 10.0,
        .boundary = tp1::BoundaryCondition::Walls,
    };
    const auto first = particle(1, 2.0, 2.0, 1.0);
    const auto second = particle(2, 5.0, 2.0, 1.0);

    EXPECT_NEAR(tp1::edge_distance(first, second, domain), 1.0, kTolerance);
    EXPECT_TRUE(tp1::are_neighbors(first, second, domain, 1.000001));
    EXPECT_FALSE(tp1::are_neighbors(first, second, domain, 1.0));
    EXPECT_FALSE(tp1::are_neighbors(first, second, domain, 0.999999));

    auto same_identity = second;
    same_identity.id = first.id;
    EXPECT_FALSE(tp1::are_neighbors(first, same_identity, domain, 2.0));
}

void test_symmetry() {
    const tp1::Domain domain{
        .side = 10.0,
        .boundary = tp1::BoundaryCondition::Walls,
    };
    const auto first = particle(1, 2.0, 3.0, 0.2);
    const auto second = particle(2, 8.0, 7.0, 0.4);

    EXPECT_NEAR(
        tp1::center_distance(first, second, domain),
        tp1::center_distance(second, first, domain),
        kTolerance
    );
    EXPECT_NEAR(
        tp1::edge_distance(first, second, domain),
        tp1::edge_distance(second, first, domain),
        kTolerance
    );
    EXPECT_TRUE(
        tp1::are_neighbors(first, second, domain, 7.0)
        == tp1::are_neighbors(second, first, domain, 7.0)
    );
}

void test_periodic_geometry() {
    const tp1::Domain domain{
        .side = 8.0,
        .boundary = tp1::BoundaryCondition::Periodic,
    };
    const auto left = particle(1, 0.25, 4.0, 0.125);
    const auto right = particle(2, 7.75, 4.0, 0.125);

    const tp1::Vec2 delta = tp1::displacement(left, right, domain);
    EXPECT_NEAR(delta.x, -0.5, kTolerance);
    EXPECT_NEAR(delta.y, 0.0, kTolerance);
    EXPECT_NEAR(tp1::center_distance(left, right, domain), 0.5, kTolerance);
    EXPECT_NEAR(tp1::edge_distance(left, right, domain), 0.25, kTolerance);
    EXPECT_TRUE(tp1::are_neighbors(left, right, domain, 0.250001));
    EXPECT_FALSE(tp1::are_neighbors(left, right, domain, 0.25));

    const auto lower_left = particle(3, 0.25, 0.25, 0.125);
    const auto upper_right = particle(4, 7.75, 7.75, 0.125);
    EXPECT_NEAR(
        tp1::center_distance(lower_left, upper_right, domain),
        std::hypot(0.5, 0.5),
        kTolerance
    );
}

void test_domain_membership() {
    const tp1::Domain walls{
        .side = 10.0,
        .boundary = tp1::BoundaryCondition::Walls,
    };
    EXPECT_TRUE(tp1::is_inside_domain(particle(1, 0.5, 0.5), walls));
    EXPECT_TRUE(tp1::is_inside_domain(particle(2, 9.5, 9.5), walls));
    EXPECT_FALSE(tp1::is_inside_domain(particle(3, 0.49, 0.5), walls));
    EXPECT_FALSE(tp1::is_inside_domain(particle(4, 9.51, 9.5), walls));

    const tp1::Domain periodic{
        .side = 10.0,
        .boundary = tp1::BoundaryCondition::Periodic,
    };
    EXPECT_TRUE(tp1::is_inside_domain(particle(5, 0.1, 0.1, 0.1), periodic));
    EXPECT_TRUE(tp1::is_inside_domain(particle(6, 9.9, 9.9, 0.1), periodic));
    EXPECT_FALSE(tp1::is_inside_domain(particle(9, 0.099, 0.1, 0.1), periodic));
    EXPECT_FALSE(tp1::is_inside_domain(particle(10, 9.901, 9.9, 0.1), periodic));
    EXPECT_FALSE(tp1::is_inside_domain(particle(7, 10.0, 5.0, 0.1), periodic));
    EXPECT_FALSE(tp1::is_inside_domain(particle(8, -0.001, 5.0, 0.1), periodic));
}

void test_validation_and_errors() {
    const tp1::Domain valid_domain{
        .side = 10.0,
        .boundary = tp1::BoundaryCondition::Walls,
    };
    const auto valid_particle = particle(1, 2.0, 2.0);

    EXPECT_TRUE(tp1::is_valid(valid_domain));
    EXPECT_TRUE(tp1::is_valid(valid_particle));

    EXPECT_FALSE(tp1::is_valid(tp1::Domain{
        .side = 0.0,
        .boundary = tp1::BoundaryCondition::Walls,
    }));
    EXPECT_FALSE(tp1::is_valid(tp1::Domain{
        .side = 10.0,
        .boundary = static_cast<tp1::BoundaryCondition>(99),
    }));

    auto invalid_particle = valid_particle;
    invalid_particle.id = 0;
    EXPECT_FALSE(tp1::is_valid(invalid_particle));

    invalid_particle = valid_particle;
    invalid_particle.radius = 0.0;
    EXPECT_FALSE(tp1::is_valid(invalid_particle));

    invalid_particle = valid_particle;
    invalid_particle.position.x = std::numeric_limits<double>::quiet_NaN();
    EXPECT_FALSE(tp1::is_valid(invalid_particle));

    EXPECT_INVALID_ARGUMENT(tp1::center_distance(
        valid_particle,
        particle(2, 3.0, 3.0),
        tp1::Domain{.side = 0.0}
    ));
    EXPECT_INVALID_ARGUMENT(tp1::edge_distance(
        invalid_particle,
        particle(2, 3.0, 3.0),
        valid_domain
    ));
    EXPECT_INVALID_ARGUMENT(tp1::are_neighbors(
        valid_particle,
        particle(2, 3.0, 3.0),
        valid_domain,
        -1.0
    ));
}

}  // namespace

int main() {
    test_wall_geometry();
    test_strict_neighbor_threshold();
    test_symmetry();
    test_periodic_geometry();
    test_domain_membership();
    test_validation_and_errors();
    return test::finish("Geometry tests");
}
