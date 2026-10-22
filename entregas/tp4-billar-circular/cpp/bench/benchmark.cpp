// Cronometra los motores del TP4 y del TP3 en el mismo proceso, para el punto
// 2.1.b [TP04, p. 3]. Mide solo la integración: la generación de condiciones
// iniciales y la escritura quedan fuera. No forma parte del motor entregado.
#include <chrono>
#include <cstdint>
#include <exception>
#include <iostream>
#include <string>

#include "tp3/generation.hpp"
#include "tp3/simulation.hpp"
#include "tp4/generation.hpp"
#include "tp4/simulation.hpp"

namespace {

constexpr std::size_t densest_random_layout = 430;

double tp4_seconds(std::size_t n, std::uint64_t seed, double dt, double tf) {
    tp4::Billiard billiard{};
    billiard.obstacle_x = billiard.particle_radius;
    const tp4::Generation generation{
        .particle_count = n,
        .seed = seed,
        .layout = n > densest_random_layout ? tp4::Layout::Lattice : tp4::Layout::Random,
    };
    auto particles = tp4::generate(billiard, generation);
    const auto steps = static_cast<std::uint64_t>(tf / dt + 0.5);
    const auto start = std::chrono::steady_clock::now();
    tp4::simulate(billiard, std::move(particles), {dt, steps, steps}, [](auto, double, const auto&) {});
    return std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
}

// Mesa vacía del punto 1.1 del TP3, con la red triangular por encima de 430
// partículas como en ese trabajo.
double tp3_seconds(std::size_t n, std::uint64_t seed, double tf, std::uint64_t& events) {
    auto system = tp3::generate_system(
        {.particle_count = n,
         .seed = seed,
         .layout = n > densest_random_layout ? tp3::Layout::Triangular : tp3::Layout::Random},
        {});
    const auto start = std::chrono::steady_clock::now();
    const auto report = tp3::simulate_queue(system, {.max_time = tf}, [](const auto&, auto, auto) {});
    const double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
    if (!report.reached_max_time) {
        throw std::runtime_error("el TP3 no llego a tf");
    }
    events = report.processed_events;
    return seconds;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 6) {
            std::cerr << "uso: benchmark <tp4|tp3> <N> <semilla> <dt> <tf>\n";
            return 2;
        }
        const std::string engine = argv[1];
        const auto n = static_cast<std::size_t>(std::stoull(argv[2]));
        const auto seed = static_cast<std::uint64_t>(std::stoull(argv[3]));
        const double dt = std::stod(argv[4]);
        const double tf = std::stod(argv[5]);
        std::cout.precision(9);
        if (engine == "tp4") {
            std::cout << "seconds " << tp4_seconds(n, seed, dt, tf) << '\n';
        } else if (engine == "tp3") {
            std::uint64_t events = 0;
            const double seconds = tp3_seconds(n, seed, tf, events);
            std::cout << "seconds " << seconds << "\nevents " << events << '\n';
        } else {
            std::cerr << "motor desconocido: " << engine << '\n';
            return 2;
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "benchmark: " << error.what() << '\n';
        return 1;
    }
}
