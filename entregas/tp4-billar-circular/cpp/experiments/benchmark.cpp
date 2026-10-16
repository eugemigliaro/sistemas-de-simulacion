#include "tp4/billiard_cli.hpp"
#include "tp4/dense.hpp"
#include "tp3/generation.hpp"
#include "tp3/simulation.hpp"
#include <chrono>
#include <iostream>

// Harness experimental, excluido del motor de entrega. Enlaza TP3 sin modificarlo.
int main(int argc, char** argv) {
    try {
        if (argc != 8) throw std::invalid_argument("benchmark tp4|tp3|generate N seed tf steps sweeps output");
        const std::string engine = argv[1], output = argv[7];
        const auto n = tp4::billiard::integer(argv[2]), seed = tp4::billiard::integer(argv[3]);
        const double duration = tp4::billiard::real(argv[4]);
        const auto steps = tp4::billiard::integer(argv[5]), sweeps = tp4::billiard::integer(argv[6]);
        std::cout << std::setprecision(17);
        if (engine == "tp4" || engine == "generate") {
            using namespace tp4::billiard;
            Config c; c.n = n; c.seed = seed; c.duration = duration; c.steps = steps; c.save_every = steps; c.obstacles = true;
            DenseResult dense;
            auto initial = n > 400 ? (dense = generate_dense(c, sweeps), dense.particles) : generate(c);
            if (engine == "generate") {
                std::ofstream out(output); out.exceptions(std::ios::failbit | std::ios::badbit);
                out << std::setprecision(17) << "id,x,y,vx,vy\n";
                for (std::size_t i = 0; i < n; ++i) {
                    const auto& p = initial[i];
                    out << i << ',' << p.position.x << ',' << p.position.y << ',' << p.velocity.x << ',' << p.velocity.y << '\n';
                }
                out.close();
                std::cout << "{\"acceptance\":" << dense.acceptance << ",\"initial_msd\":" << dense.mean_square_displacement
                          << ",\"available_sites\":" << dense.available_sites << ",\"sweeps\":" << dense.sweeps << "}\n";
                return 0;
            }
            std::vector<Particle> final;
            const auto begin = std::chrono::steady_clock::now();
            simulate(c, initial, [&](std::size_t step, double, const auto& state) { if (step == steps) final = state; });
            const double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - begin).count();
            std::ofstream out(output); out.exceptions(std::ios::failbit | std::ios::badbit);
            out << std::setprecision(17) << "step,time,id,x,y,vx,vy,used,first_contact_step\n";
            for (int frame = 0; frame < 2; ++frame) {
                const auto& state = frame == 0 ? initial : final;
                for (std::size_t i = 0; i < n; ++i) {
                    const auto& p = state[i];
                    out << (frame == 0 ? 0 : steps) << ',' << (frame == 0 ? 0 : duration) << ',' << i << ','
                        << p.position.x << ',' << p.position.y << ',' << p.velocity.x << ',' << p.velocity.y << ','
                        << (p.first_contact_step >= 0) << ',' << p.first_contact_step << '\n';
                }
            }
            out.close();
            std::cout << "{\"runtime_seconds\":" << seconds << ",\"final_time\":" << duration
                      << ",\"acceptance\":" << dense.acceptance << ",\"initial_msd\":" << dense.mean_square_displacement
                      << ",\"sweeps\":" << dense.sweeps << ",\"available_sites\":" << dense.available_sites << "}\n";
        } else if (engine == "tp3") {
            auto system = tp3::generate_system(tp3::InitializationConfig{.particle_count=n, .seed=seed,
                .layout=n > 400 ? tp3::Layout::Triangular : tp3::Layout::Random}, {});
            const auto begin = std::chrono::steady_clock::now();
            const auto report = tp3::simulate_queue(system, tp3::SimulationConfig{.max_time=duration},
                [](const auto&, std::uint64_t, tp3::FrameReason) {});
            const double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - begin).count();
            if (!report.reached_max_time) throw std::runtime_error("TP3 no alcanzo tf");
            std::cout << "{\"runtime_seconds\":" << seconds << ",\"final_time\":" << report.final_time
                      << ",\"events\":" << report.processed_events << "}\n";
        } else throw std::invalid_argument("motor desconocido");
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 2; }
}
