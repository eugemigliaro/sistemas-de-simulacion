#include <array>
#include <cmath>
#include <vector>

#include "test_support.hpp"
#include "tp4/oscillator.hpp"

namespace {

using tp4::Integrator;

constexpr std::array integrators{Integrator::Beeman, Integrator::Verlet, Integrator::VelocityVerlet,
                                 Integrator::EulerPredictorCorrector};

double exact(const tp4::Oscillator& o, double t) {
    const double beta = o.damping / (2.0 * o.mass);
    const double omega = std::sqrt(o.stiffness / o.mass - beta * beta);
    return o.amplitude * std::exp(-beta * t) * std::cos(omega * t);
}

double mean_squared_error(Integrator integrator, double dt) {
    const tp4::Oscillator o{};
    double sum = 0.0;
    std::uint64_t count = 0;
    tp4::integrate(o, integrator, dt, static_cast<std::uint64_t>(std::round(5.0 / dt)), [&](const auto& s) {
        if (s.step > 0) {
            sum += std::pow(s.position - exact(o, s.time), 2);
            ++count;
        }
    });
    return sum / static_cast<double>(count);
}

void free_particle_moves_uniformly() {
    tp4::Oscillator o{};
    o.stiffness = 0.0;
    o.damping = 0.0;
    for (const Integrator integrator : integrators) {
        tp4::integrate(o, integrator, 0.01, 100, [&](const auto& s) {
            CHECK_NEAR(s.position, o.amplitude, 1e-12);
            CHECK_NEAR(s.velocity, 0.0, 1e-12);
        });
    }
}

void samples_cover_the_whole_interval() {
    for (const Integrator integrator : integrators) {
        std::vector<tp4::OscillatorSample> samples;
        tp4::integrate(tp4::Oscillator{}, integrator, 1e-3, 5000, [&](const auto& s) { samples.push_back(s); });
        CHECK(samples.size() == 5001);
        CHECK(samples.front().position == 1.0);
        CHECK_NEAR(samples.front().velocity, -100.0 / 140.0, 1e-15);
        CHECK_NEAR(samples.back().time, 5.0, 1e-12);
        CHECK(samples[1234].step == 1234);
    }
}

// Al dividir el paso por 2, el ECM de un método de orden p baja 4^p veces.
void errors_converge_with_the_expected_order() {
    for (const Integrator integrator : integrators) {
        const double coarse = mean_squared_error(integrator, 2e-3);
        const double fine = mean_squared_error(integrator, 1e-3);
        const double ratio = coarse / fine;
        if (integrator == Integrator::EulerPredictorCorrector) {
            CHECK(ratio > 3.5 && ratio < 4.5);
        } else {
            CHECK(ratio > 14.0 && ratio < 18.0);
        }
    }
}

// Eliminando las velocidades, ambos dan la misma recurrencia de posiciones:
// solo difieren por redondeo.
void verlet_variants_share_positions() {
    std::vector<double> verlet;
    std::vector<double> velocity_verlet;
    tp4::integrate(tp4::Oscillator{}, Integrator::Verlet, 1e-3, 5000,
                   [&](const auto& s) { verlet.push_back(s.position); });
    tp4::integrate(tp4::Oscillator{}, Integrator::VelocityVerlet, 1e-3, 5000,
                   [&](const auto& s) { velocity_verlet.push_back(s.position); });
    double largest = 0.0;
    for (std::size_t i = 0; i < verlet.size(); ++i) {
        largest = std::max(largest, std::abs(verlet[i] - velocity_verlet[i]));
    }
    CHECK_NEAR(largest, 0.0, 1e-10);
}

void rejects_invalid_input() {
    const auto ignore = [](const auto&) {};
    CHECK_THROWS(std::invalid_argument, tp4::integrate(tp4::Oscillator{}, Integrator::Beeman, 0.0, 10, ignore));
    CHECK_THROWS(std::invalid_argument, tp4::integrate(tp4::Oscillator{}, Integrator::Beeman, 1e-3, 0, ignore));
    tp4::Oscillator massless{};
    massless.mass = 0.0;
    CHECK_THROWS(std::invalid_argument, tp4::integrate(massless, Integrator::Verlet, 1e-3, 10, ignore));
    CHECK_THROWS(std::invalid_argument, (void)tp4::parse_integrator("rk4"));
    CHECK(tp4::parse_integrator("euler-pc") == Integrator::EulerPredictorCorrector);
}

}  // namespace

int main() {
    free_particle_moves_uniformly();
    samples_cover_the_whole_interval();
    errors_converge_with_the_expected_order();
    verlet_variants_share_positions();
    rejects_invalid_input();
    return test::finish("oscilador");
}
