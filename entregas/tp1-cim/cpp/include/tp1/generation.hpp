#pragma once

#include <cstddef>
#include <cstdint>

#include "tp1/model.hpp"

namespace tp1 {

struct GenerationConfig {
    std::size_t particle_count{};
    Domain domain{};
    double min_radius{0.23};
    double max_radius{0.26};
    double property{1.0};
    std::uint64_t seed{};
    std::size_t max_attempts_per_particle{100'000};
};

[[nodiscard]] bool is_valid(const GenerationConfig& config) noexcept;

[[nodiscard]] ParticleSystem generate_system(const GenerationConfig& config);

[[nodiscard]] bool has_overlaps(const ParticleSystem& system);

}  // namespace tp1
