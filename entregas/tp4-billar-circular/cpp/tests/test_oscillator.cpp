#include "tp4/oscillator.hpp"
#include <iostream>
#include <vector>

void require(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}
double exact(double t, double gamma = 100) {
    const double beta = gamma / 140;
    const double omega = std::sqrt(10000.0 / 70 - beta * beta);
    return std::exp(-beta * t) * std::cos(omega * t);
}
int main() {
    try {
        for (auto name : {"beeman", "verlet", "velocity-verlet", "euler-pc"}) {
            const auto method = tp4::parse_method(name);
            tp4::Config free;
            free.stiffness = free.damping = 0;
            free.steps = 100;
            tp4::simulate(free, method, [&](tp4::Sample s) {
                require(std::abs(s.position - (free.x0 + free.v0 * s.time)) < 1e-10, "movimiento libre");
                require(std::abs(s.velocity - free.v0) < 1e-10, "velocidad libre");
            });
            for (double damping : {0.0, 100.0}) {
                std::vector<double> errors;
                for (std::size_t steps : {1000, 2000, 4000}) {
                    tp4::Config c;
                    c.damping = damping;
                    c.v0 = -damping / 140;
                    c.steps = steps;
                    double sum = 0;
                    std::size_t count = 0;
                    tp4::simulate(c, method, [&](tp4::Sample s) {
                        require(s.step == count++, "indice de muestra");
                        require(std::abs(s.time - 5.0 * s.step / steps) < 1e-14, "timestamp");
                        if (s.step == 0) require(s.position == c.x0 && s.velocity == c.v0, "estado inicial");
                        else sum += std::pow(s.position - exact(s.time, damping), 2);
                        if (s.step == steps) require(s.time == 5, "horizonte exacto");
                    });
                    require(count == steps + 1, "cantidad de muestras");
                    errors.push_back(sum / steps);
                }
                const double minimum_ratio = method == tp4::Method::euler_pc ? 2 : 8;
                require(errors[0] / errors[1] > minimum_ratio && errors[1] / errors[2] > minimum_ratio,
                        "convergencia contra solucion analitica");
            }
        }
        // Velocidades centradas contra una referencia independiente en t=5.
        tp4::Config c;
        c.steps = 10000;
        tp4::simulate(c, tp4::Method::verlet, [&](tp4::Sample s) {
            if (s.step == c.steps) {
                const double beta = c.damping / (2 * c.mass);
                const double omega = std::sqrt(c.stiffness / c.mass - beta * beta);
                const double expected = std::exp(-beta * s.time) *
                    (-beta * std::cos(omega * s.time) - omega * std::sin(omega * s.time));
                require(std::abs(s.velocity - expected) < 1e-4, "velocidad Verlet final desfasada");
            }
        });
        c.mass = 0;
        bool rejected = false;
        try { c.validate(); } catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "masa nula aceptada");
        std::cout << "C++: movimiento libre, oscilador, convergencia y tiempos OK\n";
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
