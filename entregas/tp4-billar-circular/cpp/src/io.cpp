#include "tp4/io.hpp"

#include <array>
#include <charconv>
#include <iomanip>
#include <ostream>
#include <string_view>

namespace tp4 {
namespace {

// Diez cifras alcanzan para la energía del billar.
constexpr int billiard_digits = 10;

// Representación más corta que recupera exactamente el double: los parámetros
// se leen como se escribieron y el ECM del oscilador no pierde precisión.
class Exact {
public:
    explicit Exact(double value) {
        size_ = static_cast<std::size_t>(std::to_chars(buffer_.data(), buffer_.data() + buffer_.size(), value).ptr
                                         - buffer_.data());
    }

    friend std::ostream& operator<<(std::ostream& stream, const Exact& exact) {
        return stream << std::string_view(exact.buffer_.data(), exact.size_);
    }

private:
    std::array<char, 32> buffer_{};
    std::size_t size_{};
};

}  // namespace

void write_billiard_header(
    std::ostream& stream,
    const Billiard& billiard,
    const Generation& generation,
    const Run& run
) {
    stream << "# tp4 billiard\n"
           << "# particles " << generation.particle_count << '\n'
           << "# seed " << generation.seed << '\n'
           << "# layout " << to_string(generation.layout) << '\n'
           << "# radius " << Exact(billiard.radius) << '\n'
           << "# particle_radius " << Exact(billiard.particle_radius) << '\n'
           << "# particle_mass " << Exact(billiard.particle_mass) << '\n'
           << "# stiffness " << Exact(billiard.stiffness) << '\n'
           << "# initial_speed " << Exact(billiard.initial_speed) << '\n'
           << "# obstacle_x ";
    if (billiard.obstacle_x) {
        stream << Exact(*billiard.obstacle_x) << '\n';
    } else {
        stream << "none\n";
    }
    stream << "# dt " << Exact(run.dt) << '\n'
           << "# steps " << run.steps << '\n'
           << "# output_every " << run.output_every << '\n';
}

void write_frame(std::ostream& stream, std::uint64_t step, double time, const std::vector<Particle>& particles) {
    stream << "frame " << step << ' ' << Exact(time) << '\n' << std::setprecision(billiard_digits);
    for (const Particle& p : particles) {
        stream << p.position.x << ' ' << p.position.y << ' '
               << p.velocity.x << ' ' << p.velocity.y << ' '
               << static_cast<int>(p.color) << '\n';
    }
}

void write_oscillator_header(std::ostream& stream, const Oscillator& oscillator, Integrator integrator, double dt) {
    stream << "# tp4 oscillator\n"
           << "# integrator " << to_string(integrator) << '\n'
           << "# mass " << Exact(oscillator.mass) << '\n'
           << "# stiffness " << Exact(oscillator.stiffness) << '\n'
           << "# damping " << Exact(oscillator.damping) << '\n'
           << "# amplitude " << Exact(oscillator.amplitude) << '\n'
           << "# dt " << Exact(dt) << '\n'
           << "# columns step time position velocity\n";
}

void write_sample(std::ostream& stream, const OscillatorSample& sample) {
    stream << sample.step << ' ' << Exact(sample.time) << ' ' << Exact(sample.position) << ' '
           << Exact(sample.velocity) << '\n';
}

}  // namespace tp4
