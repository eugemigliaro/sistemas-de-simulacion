#include <charconv>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <fstream>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

#include "tp3/generation.hpp"
#include "tp3/io.hpp"
#include "tp3/simulation.hpp"
#include "tp3/version.hpp"

namespace {

void print_usage(std::ostream& stream) {
    stream << "uso: tp3 <comando> [opciones]\n"
           << "\n"
           << "comandos:\n"
           << "  generate     genera una condicion inicial y la escribe como\n"
           << "               un unico cuadro de trayectoria\n"
           << "  simulate     corre la dinamica dirigida por eventos y escribe\n"
           << "               la trayectoria\n"
           << "  --version    imprime nombre y version del motor\n"
           << "\n"
           << "opciones comunes:\n"
           << "  --n <entero>          cantidad de particulas (obligatorio)\n"
           << "  --seed <entero>       semilla del generador (default 0)\n"
           << "  --config <archivo>    obstaculos, una linea \"xk yk Rk\"\n"
           << "                        (si se omite, mesa vacia)\n"
           << "  --output <archivo>    destino (si se omite, salida estandar)\n"
           << "  --max-attempts <n>    tope de intentos por particula\n"
           << "\n"
           << "opciones de simulate:\n"
           << "  --tmax <real>         tiempo absoluto de corrida (obligatorio)\n"
           << "  --save-every <n>      cuadro periodico cada n eventos\n"
           << "                        (default 0: solo inicial, color y final)\n"
           << "  --max-events <n>      tope de eventos (default 0: sin tope)\n"
           << "  --engine <nombre>     naive o queue (default queue)\n"
           << "\n"
           << "El motor solo genera el estado del sistema (tiempo, posiciones,\n"
           << "velocidades y color). Los observables se calculan en el\n"
           << "post-proceso de Python.\n";
}

template <typename Integer>
[[nodiscard]] std::optional<Integer> parse_integer(std::string_view text) {
    Integer value{};
    const char* const begin = text.data();
    const char* const end = begin + text.size();
    const auto result = std::from_chars(begin, end, value);
    if (result.ec != std::errc{} || result.ptr != end) {
        return std::nullopt;
    }
    return value;
}

[[nodiscard]] std::optional<double> parse_real(std::string_view text) {
    try {
        const std::string owned(text);
        std::size_t consumed = 0;
        const double value = std::stod(owned, &consumed);
        if (consumed != owned.size()) {
            return std::nullopt;
        }
        return value;
    } catch (const std::exception&) {
        return std::nullopt;
    }
}

struct Options {
    std::size_t particle_count{};
    bool has_particle_count{false};
    std::uint64_t seed{};
    std::size_t max_attempts{10000};
    std::string config_path{};
    std::string output_path{};

    double max_time{};
    bool has_max_time{false};
    std::uint64_t save_every{0};
    std::uint64_t max_events{0};
    std::string engine{"queue"};
};

[[nodiscard]] Options parse_options(
    const std::vector<std::string_view>& arguments,
    bool simulation
) {
    Options options{};

    const auto reject_unless_simulation = [&](std::string_view flag) {
        if (!simulation) {
            throw std::invalid_argument(
                std::string(flag) + " solo aplica a simulate"
            );
        }
    };

    for (std::size_t index = 1; index < arguments.size(); ++index) {
        const std::string_view flag = arguments[index];
        if (index + 1 >= arguments.size()) {
            throw std::invalid_argument(
                "falta el valor de " + std::string(flag)
            );
        }
        const std::string_view value = arguments[++index];

        if (flag == "--n") {
            const auto parsed = parse_integer<std::size_t>(value);
            if (!parsed.has_value()) {
                throw std::invalid_argument("--n debe ser un entero no negativo");
            }
            options.particle_count = *parsed;
            options.has_particle_count = true;
        } else if (flag == "--seed") {
            const auto parsed = parse_integer<std::uint64_t>(value);
            if (!parsed.has_value()) {
                throw std::invalid_argument("--seed debe ser un entero no negativo");
            }
            options.seed = *parsed;
        } else if (flag == "--max-attempts") {
            const auto parsed = parse_integer<std::size_t>(value);
            if (!parsed.has_value()) {
                throw std::invalid_argument(
                    "--max-attempts debe ser un entero no negativo"
                );
            }
            options.max_attempts = *parsed;
        } else if (flag == "--config") {
            options.config_path = std::string(value);
        } else if (flag == "--output") {
            options.output_path = std::string(value);
        } else if (flag == "--tmax") {
            reject_unless_simulation(flag);
            const auto parsed = parse_real(value);
            if (!parsed.has_value() || !(*parsed > 0.0)) {
                throw std::invalid_argument("--tmax debe ser un real positivo");
            }
            options.max_time = *parsed;
            options.has_max_time = true;
        } else if (flag == "--save-every") {
            reject_unless_simulation(flag);
            const auto parsed = parse_integer<std::uint64_t>(value);
            if (!parsed.has_value()) {
                throw std::invalid_argument(
                    "--save-every debe ser un entero no negativo"
                );
            }
            options.save_every = *parsed;
        } else if (flag == "--max-events") {
            reject_unless_simulation(flag);
            const auto parsed = parse_integer<std::uint64_t>(value);
            if (!parsed.has_value()) {
                throw std::invalid_argument(
                    "--max-events debe ser un entero no negativo"
                );
            }
            options.max_events = *parsed;
        } else if (flag == "--engine") {
            reject_unless_simulation(flag);
            if (value != "naive" && value != "queue") {
                throw std::invalid_argument(
                    "motor desconocido: " + std::string(value)
                    + " (naive o queue)"
                );
            }
            options.engine = std::string(value);
        } else {
            throw std::invalid_argument("opcion desconocida: " + std::string(flag));
        }
    }

    if (!options.has_particle_count) {
        throw std::invalid_argument(
            std::string(arguments.front()) + " requiere --n"
        );
    }
    if (simulation && !options.has_max_time) {
        throw std::invalid_argument("simulate requiere --tmax");
    }

    return options;
}

[[nodiscard]] std::vector<tp3::Obstacle> load_obstacles(const std::string& path) {
    if (path.empty()) {
        return {};
    }
    std::ifstream file(path);
    if (!file) {
        throw std::invalid_argument("no se pudo abrir la configuracion: " + path);
    }
    return tp3::read_obstacles(file);
}

[[nodiscard]] tp3::System build_system(
    const Options& options,
    const std::vector<tp3::Obstacle>& obstacles
) {
    return tp3::generate_system(
        tp3::InitializationConfig{
            .particle_count = options.particle_count,
            .table = {},
            .particle_radius = tp3::default_particle_radius,
            .particle_mass = tp3::default_particle_mass,
            .initial_speed = tp3::default_initial_speed,
            .seed = options.seed,
            .max_placement_attempts = options.max_attempts,
        },
        obstacles
    );
}

// Abre el destino pedido, o deja la salida estandar si no se pidio archivo.
class Output {
public:
    explicit Output(const std::string& path) {
        if (path.empty()) {
            return;
        }
        file_.open(path);
        if (!file_) {
            throw std::invalid_argument("no se pudo escribir en " + path);
        }
        uses_file_ = true;
    }

    [[nodiscard]] std::ostream& stream() {
        return uses_file_ ? static_cast<std::ostream&>(file_) : std::cout;
    }

private:
    std::ofstream file_{};
    bool uses_file_{false};
};

int run_generate(const std::vector<std::string_view>& arguments) {
    const Options options = parse_options(arguments, false);
    const tp3::System system = build_system(
        options, load_obstacles(options.config_path)
    );

    Output output(options.output_path);
    tp3::write_trajectory_header(
        output.stream(),
        system,
        tp3::TrajectoryMetadata{
            .seed = options.seed,
            .initial_speed = tp3::default_initial_speed,
            .save_every = 0,
        }
    );
    tp3::write_frame(output.stream(), system, 0, 0, tp3::FrameReason::Initial);
    return 0;
}

int run_simulate(const std::vector<std::string_view>& arguments) {
    const Options options = parse_options(arguments, true);
    tp3::System system = build_system(
        options, load_obstacles(options.config_path)
    );

    Output output(options.output_path);
    tp3::write_trajectory_header(
        output.stream(),
        system,
        tp3::TrajectoryMetadata{
            .seed = options.seed,
            .initial_speed = tp3::default_initial_speed,
            .save_every = options.save_every,
        }
    );

    std::uint64_t frame_index = 0;
    const tp3::FrameSink sink = [&](
        const tp3::System& state,
        std::uint64_t processed_events,
        tp3::FrameReason reason
    ) {
        tp3::write_frame(
            output.stream(), state, frame_index, processed_events, reason
        );
        ++frame_index;
    };

    // El tiempo de ejecucion es una propiedad del programa, no del sistema
    // simulado, y es justamente lo que pide medir el punto 1.1 [TP03, p. 3].
    // Va por la salida de error para no ensuciar la trayectoria cuando esta
    // se escribe por salida estandar.
    const tp3::SimulationConfig simulation_config{
        .max_time = options.max_time,
        .save_every = options.save_every,
        .max_events = options.max_events,
    };

    const auto started = std::chrono::steady_clock::now();
    const tp3::SimulationReport report = (options.engine == "naive")
        ? tp3::simulate_naive(system, simulation_config, sink)
        : tp3::simulate_queue(system, simulation_config, sink);
    const auto finished = std::chrono::steady_clock::now();
    const double seconds =
        std::chrono::duration<double>(finished - started).count();

    std::cerr << "engine " << options.engine
              << " particles " << options.particle_count
              << " seed " << options.seed
              << " events " << report.processed_events
              << " frames " << report.written_frames
              << " final_time " << report.final_time
              << " runtime_seconds " << seconds << '\n';

    if (report.exhausted_events) {
        std::cerr << "aviso: el sistema se quedo sin eventos futuros\n";
    }
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    const std::vector<std::string_view> arguments(argv + 1, argv + argc);

    if (arguments.empty()) {
        print_usage(std::cerr);
        return 1;
    }

    try {
        if (arguments.front() == "--version") {
            std::cout << tp3::engine_name << ' ' << tp3::engine_version << '\n';
            return 0;
        }
        if (arguments.front() == "generate") {
            return run_generate(arguments);
        }
        if (arguments.front() == "simulate") {
            return run_simulate(arguments);
        }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }

    std::cerr << "comando desconocido: " << arguments.front() << "\n\n";
    print_usage(std::cerr);
    return 1;
}
