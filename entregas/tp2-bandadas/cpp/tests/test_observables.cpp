#include <numbers>
#include <vector>

#include "test_support.hpp"
#include "tp2/observables.hpp"

namespace {

tp2::Particle particle(std::size_t id, double angle) {
    return tp2::Particle{
        .id = id,
        .position = {.x = static_cast<double>(id), .y = 1.0},
        .angle = angle,
    };
}

void test_polarization() {
    tp2::System aligned{
        .side = 10.0,
        .particles = {
            particle(1, 0.0),
            particle(2, 0.0),
            particle(3, 0.0),
        },
    };
    EXPECT_NEAR(tp2::polarization(aligned), 1.0, 1e-12);

    tp2::System opposed{
        .side = 10.0,
        .particles = {
            particle(1, 0.0),
            particle(2, 0.0),
            particle(3, std::numbers::pi_v<double>),
            particle(4, std::numbers::pi_v<double>),
        },
    };
    EXPECT_NEAR(tp2::polarization(opposed), 0.0, 1e-12);
}

void test_largest_cluster() {
    const tp2::NeighborList neighbors{
        {1},
        {0, 2},
        {1},
        {},
    };
    EXPECT_NEAR(tp2::largest_cluster_fraction(neighbors), 0.75, 1e-12);
}

}  // namespace

int main() {
    test_polarization();
    test_largest_cluster();
    return test::finish("Observable tests");
}
