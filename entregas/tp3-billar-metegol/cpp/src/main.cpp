#include <charconv>
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
#include "tp3/version.hpp"

namespace {

void print_usage(std::ostream& stream) {
    stream << "uso: tp3 <comando> [opciones]\n"
           << "\n"
           << "comandos:\n"
           << "  generate     genera una condicion inicial y la escribe como\n"
           << "               un unico cuadro de trayectoria\n"
           << "  --version    imprime nombre y version del motor\n"
           << "\n"
           << "opciones de generate:\n"
           << "  --n <entero>          cantidad de particulas (obligatorio)\n"
           << "  --seed <entero>       semilla del generador (default 0)\n"
           << "  --config <archivo>    obstaculos, una linea \"xk yk Rk\"\n"
           << "                        (si se omite, mesa vacia)\n"
           << "  --output <archivo>    destino (si se omite, salida estandar)\n"
           << "  --max-attempts <n>    tope de intentos por particula\n"
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

struct GenerateOptions {
    std::size_t particle_count{};
    std::uint64_t seed{};
    std::size_t max_attempts{10000};
    std::string config_path{};
    std::string output_path{};
    bool has_particle_count{false};
};

[[nodiscard]] GenerateOptions parse_generate_options(
    const std::vector<std::string_view>& arguments
) {
    GenerateOptions options{};

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
        } else {
            throw std::invalid_argument("opcion desconocida: " + std::string(flag));
        }
    }

    if (!options.has_particle_count) {
        throw std::invalid_argument("generate requiere --n");
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

int run_generate(const std::vector<std::string_view>& arguments) {
    const GenerateOptions options = parse_generate_options(arguments);
    const std::vector<tp3::Obstacle> obstacles = load_obstacles(options.config_path);

    const tp3::System system = tp3::generate_system(
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

    const tp3::TrajectoryMetadata metadata{
        .seed = options.seed,
        .initial_speed = tp3::default_initial_speed,
        .save_every = 0,
    };

    std::ofstream file;
    if (!options.output_path.empty()) {
        file.open(options.output_path);
        if (!file) {
            throw std::invalid_argument(
                "no se pudo escribir en " + options.output_path
            );
        }
    }
    std::ostream& output = options.output_path.empty() ? std::cout : file;

    tp3::write_trajectory_header(output, system, metadata);
    tp3::write_frame(output, system, 0, 0, tp3::FrameReason::Initial);
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
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }

    std::cerr << "comando desconocido: " << arguments.front() << "\n\n";
    print_usage(std::cerr);
    return 1;
}
