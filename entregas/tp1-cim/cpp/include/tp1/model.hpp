#pragma once

#include <cstddef>
#include <vector>

namespace tp1 {

struct Vec2 {
    double x{};
    double y{};
};

struct Particle {
    std::size_t id{};
    Vec2 position{};
    Vec2 velocity{};
    double radius{};
    double property{};
};

enum class BoundaryCondition {
    Walls,
    Periodic,
};

struct Domain {
    double side{};
    BoundaryCondition boundary{BoundaryCondition::Walls};
};

struct ParticleSystem {
    Domain domain{};
    double time{};
    std::vector<Particle> particles{};
};

}  // namespace tp1
