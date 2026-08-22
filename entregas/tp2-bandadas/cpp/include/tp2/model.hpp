#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace tp2 {

struct Vec2 {
    double x{};
    double y{};

    bool operator==(const Vec2&) const = default;
};

struct Particle {
    std::size_t id{};
    Vec2 position{};
    double angle{};

    bool operator==(const Particle&) const = default;
};

struct System {
    double side{10.0};
    double time{};
    std::vector<Particle> particles{};

    bool operator==(const System&) const = default;
};

enum class AlignmentModel {
    Vicsek,
    Voter,
};

struct DynamicsConfig {
    AlignmentModel model{AlignmentModel::Vicsek};
    double cutoff{1.0};
    double speed{0.03};
    double time_step{1.0};
    double eta{};
};

struct InitializationConfig {
    std::size_t particle_count{};
    double side{10.0};
    std::uint64_t seed{};
};

}  // namespace tp2
