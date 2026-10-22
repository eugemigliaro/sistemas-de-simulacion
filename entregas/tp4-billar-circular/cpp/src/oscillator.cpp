#include "tp4/oscillator.hpp"

#include <cmath>
#include <stdexcept>
#include <string>

namespace tp4 {
namespace {

struct State {
    double position;
    double velocity;
    double acceleration;
};

void validate(const Oscillator& oscillator, double dt, std::uint64_t steps) {
    const bool valid = std::isfinite(oscillator.mass) && oscillator.mass > 0.0
        && std::isfinite(oscillator.stiffness) && oscillator.stiffness >= 0.0
        && std::isfinite(oscillator.damping) && oscillator.damping >= 0.0
        && std::isfinite(oscillator.amplitude);
    if (!valid) {
        throw std::invalid_argument("parametros del oscilador invalidos");
    }
    if (!std::isfinite(dt) || dt <= 0.0 || steps == 0) {
        throw std::invalid_argument("el paso y la cantidad de pasos deben ser positivos");
    }
}

// Estado en t = -dt estimado con Euler hacia atrás [T04, p. 13] [T04, p. 14].
State previous_state(const Oscillator& oscillator, const State& initial, double dt) {
    const double position = initial.position - dt * initial.velocity
        + 0.5 * dt * dt * initial.acceleration;
    const double velocity = initial.velocity - dt * initial.acceleration;
    return {position, velocity, oscillator.acceleration(position, velocity)};
}

void emit(const OscillatorSink& sink, std::uint64_t step, double dt, double position, double velocity) {
    if (!std::isfinite(position) || !std::isfinite(velocity)) {
        throw std::runtime_error("el oscilador diverge: reducir el paso");
    }
    sink({step, static_cast<double>(step) * dt, position, velocity});
}

// Verlet original: r(t+dt) = 2r(t) - r(t-dt) + dt^2 a(t) con
// v(t) = [r(t+dt) - r(t-dt)] / (2dt) [T04, p. 13]. Como la fuerza depende de
// v(t), se reemplaza la velocidad centrada en a(t) y se despeja r(t+dt), que
// para el oscilador lineal queda explícito.
void verlet(const Oscillator& o, const State& initial, double dt, std::uint64_t steps, const OscillatorSink& sink) {
    const double c = o.damping * dt / (2.0 * o.mass);
    const double spring = o.stiffness * dt * dt / o.mass;
    const auto next = [&](double current, double previous) {
        return ((2.0 - spring) * current - (1.0 - c) * previous) / (1.0 + c);
    };
    double previous = previous_state(o, initial, dt).position;
    double current = initial.position;
    for (std::uint64_t step = 0; step <= steps; ++step) {
        const double following = next(current, previous);
        const double velocity = step == 0 ? initial.velocity : (following - previous) / (2.0 * dt);
        emit(sink, step, dt, current, velocity);
        previous = current;
        current = following;
    }
}

// Velocity Verlet [T04, p. 17]. La aceleración en t+dt depende de v(t+dt),
// que aparece en ambos miembros; para el oscilador lineal se despeja.
State velocity_verlet_step(const Oscillator& o, const State& s, double dt) {
    const double position = s.position + dt * s.velocity + 0.5 * dt * dt * s.acceleration;
    const double velocity = (s.velocity + 0.5 * dt * s.acceleration
                             - 0.5 * dt * o.stiffness * position / o.mass)
        / (1.0 + 0.5 * dt * o.damping / o.mass);
    return {position, velocity, o.acceleration(position, velocity)};
}

// Beeman con fuerza dependiente de la velocidad: predice v, evalúa a y corrige
// v [T04, p. 20].
State beeman_step(const Oscillator& o, const State& s, double previous_acceleration, double dt) {
    const double position = s.position + dt * s.velocity
        + dt * dt * (2.0 / 3.0 * s.acceleration - 1.0 / 6.0 * previous_acceleration);
    const double predicted_velocity = s.velocity
        + dt * (1.5 * s.acceleration - 0.5 * previous_acceleration);
    const double predicted_acceleration = o.acceleration(position, predicted_velocity);
    const double velocity = s.velocity
        + dt * (predicted_acceleration / 3.0 + 5.0 / 6.0 * s.acceleration - previous_acceleration / 6.0);
    return {position, velocity, o.acceleration(position, velocity)};
}

// Euler predictor-corrector de la teórica [T04, p. 23].
State euler_predictor_corrector_step(const Oscillator& o, const State& s, double dt) {
    const double predicted_acceleration = o.acceleration(
        s.position + dt * s.velocity, s.velocity + dt * s.acceleration);
    const double velocity = s.velocity + dt * predicted_acceleration;
    const double position = s.position + dt * velocity;
    return {position, velocity, o.acceleration(position, velocity)};
}

}  // namespace

double Oscillator::acceleration(double position, double velocity) const noexcept {
    return -(stiffness * position + damping * velocity) / mass;
}

double Oscillator::initial_velocity() const noexcept {
    return -amplitude * damping / (2.0 * mass);
}

Integrator parse_integrator(std::string_view name) {
    if (name == "beeman") return Integrator::Beeman;
    if (name == "verlet") return Integrator::Verlet;
    if (name == "velocity-verlet") return Integrator::VelocityVerlet;
    if (name == "euler-pc") return Integrator::EulerPredictorCorrector;
    throw std::invalid_argument("integrador desconocido: " + std::string(name));
}

std::string_view to_string(Integrator integrator) noexcept {
    switch (integrator) {
        case Integrator::Beeman: return "beeman";
        case Integrator::Verlet: return "verlet";
        case Integrator::VelocityVerlet: return "velocity-verlet";
        case Integrator::EulerPredictorCorrector: return "euler-pc";
    }
    return "?";
}

void integrate(
    const Oscillator& oscillator,
    Integrator integrator,
    double dt,
    std::uint64_t steps,
    const OscillatorSink& sink
) {
    validate(oscillator, dt, steps);
    const double velocity = oscillator.initial_velocity();
    State state{oscillator.amplitude, velocity, oscillator.acceleration(oscillator.amplitude, velocity)};
    if (integrator == Integrator::Verlet) {
        verlet(oscillator, state, dt, steps, sink);
        return;
    }
    double previous_acceleration = previous_state(oscillator, state, dt).acceleration;
    emit(sink, 0, dt, state.position, state.velocity);
    for (std::uint64_t step = 1; step <= steps; ++step) {
        State next{};
        switch (integrator) {
            case Integrator::Beeman:
                next = beeman_step(oscillator, state, previous_acceleration, dt);
                break;
            case Integrator::VelocityVerlet:
                next = velocity_verlet_step(oscillator, state, dt);
                break;
            default:
                next = euler_predictor_corrector_step(oscillator, state, dt);
                break;
        }
        previous_acceleration = state.acceleration;
        state = next;
        emit(sink, step, dt, state.position, state.velocity);
    }
}

}  // namespace tp4
