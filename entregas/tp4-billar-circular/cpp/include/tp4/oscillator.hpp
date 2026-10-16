#pragma once

#include <cmath>
#include <cstddef>
#include <functional>
#include <limits>
#include <stdexcept>
#include <string_view>

namespace tp4 {
enum class Method { beeman, verlet, velocity_verlet, euler_pc };
inline Method parse_method(std::string_view name) {
    if (name == "beeman") return Method::beeman;
    if (name == "verlet") return Method::verlet;
    if (name == "velocity-verlet") return Method::velocity_verlet;
    if (name == "euler-pc") return Method::euler_pc;
    throw std::invalid_argument("metodo desconocido");
}
struct Config {
    double mass = 70, stiffness = 10000, damping = 100;
    double x0 = 1, v0 = -5.0 / 7, duration = 5;
    std::size_t steps = 1000;
    double acceleration(double x, double v) const {
        return -(stiffness * x + damping * v) / mass;
    }
    void validate() const {
        for (double value : {mass, stiffness, damping, x0, v0, duration})
            if (!std::isfinite(value)) throw std::invalid_argument("configuracion no finita");
        if (mass <= 0 || stiffness < 0 || damping < 0 || duration <= 0 || steps == 0 ||
            steps == std::numeric_limits<std::size_t>::max())
            throw std::invalid_argument("masa, duracion y pasos deben ser positivos; k y gamma no negativos");
        if (!(duration / static_cast<double>(steps) > 0))
            throw std::invalid_argument("paso temporal no representable");
    }
};
struct Sample { std::size_t step; double time, position, velocity; };

// Solo genera estados. La solucion analitica y el ECM pertenecen al post-proceso.
inline void simulate(const Config& c, Method method, const std::function<void(Sample)>& emit) {
    c.validate();
    const double h = c.duration / static_cast<double>(c.steps);
    double x = c.x0, v = c.v0, a = c.acceleration(x, v);
    double previous_x = x - h * v + h * h * a / 2;
    const double jerk = -(c.stiffness * v + c.damping * a) / c.mass;
    double previous_a = c.acceleration(previous_x, v - h * a + h * h * jerk / 2);
    auto output = [&](std::size_t n, double position, double velocity) {
        if (!std::isfinite(position) || !std::isfinite(velocity))
            throw std::runtime_error("estado no finito: reducir paso o revisar configuracion");
        emit({n, n == c.steps ? c.duration : static_cast<double>(n) * h, position, velocity});
    };
    output(0, x, v);
    if (method == Method::verlet) {
        // T04 p.13: velocidad centrada sustituida en la fuerza amortiguada.
        auto next = [&](double current, double previous) {
            const double d = c.damping * h / (2 * c.mass);
            return ((2 - c.stiffness * h * h / c.mass) * current - (1 - d) * previous) / (1 + d);
        };
        double future_x = next(x, previous_x);
        previous_x = x;
        x = future_x;
        for (std::size_t n = 1; n <= c.steps; ++n) {
            future_x = next(x, previous_x); // Estado auxiliar para v en el ultimo instante.
            output(n, x, (future_x - previous_x) / (2 * h));
            previous_x = x;
            x = future_x;
        }
        return;
    }
    for (std::size_t n = 1; n <= c.steps; ++n) {
        double next_x = 0, next_v = 0;
        if (method == Method::velocity_verlet) {
            next_x = x + h * v + h * h * a / 2;
            next_v = (v + h * a / 2 - h * c.stiffness * next_x / (2 * c.mass)) /
                     (1 + h * c.damping / (2 * c.mass));
        } else if (method == Method::beeman) {
            // T04 p.20: predecir v, evaluar a, corregir v.
            next_x = x + h * v + h * h * (2 * a / 3 - previous_a / 6);
            const double predicted_v = v + h * (3 * a / 2 - previous_a / 2);
            const double predicted_a = c.acceleration(next_x, predicted_v);
            next_v = v + h * (predicted_a / 3 + 5 * a / 6 - previous_a / 6);
        } else {
            // Euler PC especifico de T04 p.23, sin promedio trapezoidal.
            const double predicted_a = c.acceleration(x + h * v, v + h * a);
            next_v = v + h * predicted_a;
            next_x = x + h * next_v;
        }
        previous_a = a;
        x = next_x;
        v = next_v;
        a = c.acceleration(x, v);
        output(n, x, v);
    }
}
} // namespace tp4
