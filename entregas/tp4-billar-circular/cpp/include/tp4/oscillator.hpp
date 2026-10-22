#pragma once

#include <cstdint>
#include <functional>
#include <string_view>

namespace tp4 {

// Oscilador amortiguado de la teórica 4: m = 70 kg, k = 10^4 N/m,
// gamma = 100 kg/s, r(0) = A y v(0) = -A gamma / (2m) [T04, p. 37].
struct Oscillator {
    double mass{70.0};
    double stiffness{1.0e4};
    double damping{100.0};
    double amplitude{1.0};

    [[nodiscard]] double acceleration(double position, double velocity) const noexcept;
    [[nodiscard]] double initial_velocity() const noexcept;
};

enum class Integrator { Beeman, Verlet, VelocityVerlet, EulerPredictorCorrector };

[[nodiscard]] Integrator parse_integrator(std::string_view name);
[[nodiscard]] std::string_view to_string(Integrator integrator) noexcept;

struct OscillatorSample {
    std::uint64_t step{};
    double time{};
    double position{};
    double velocity{};
};

using OscillatorSink = std::function<void(const OscillatorSample&)>;

// Integra desde t = 0 hasta t = steps * dt y entrega el estado inicial y el de
// cada paso, en orden.
void integrate(
    const Oscillator& oscillator,
    Integrator integrator,
    double dt,
    std::uint64_t steps,
    const OscillatorSink& sink
);

}  // namespace tp4
