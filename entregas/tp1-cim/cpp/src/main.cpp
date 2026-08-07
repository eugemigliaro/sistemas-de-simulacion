#include <charconv>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

#include "tp1/generation.hpp"
#include "tp1/io.hpp"
#include "tp1/neighbors.hpp"
#include "tp1/version.hpp"

namespace {

struct GenerateArguments {
    tp1::GenerationConfig config{
        .particle_count = 100,
        .domain = {
            .side = 20.0,
            .boundary = tp1::BoundaryCondition::Walls,
        },
    };
    std::filesystem::path static_path{"static.txt"};
    std::filesystem::path dynamic_path{"dynamic.txt"};
};

struct NeighborArguments {
    std::filesystem::path static_path{"static.txt"};
    std::filesystem::path dynamic_path{"dynamic.txt"};
    std::filesystem::path output_path{"neighbors.txt"};
    double cutoff{1.0};
    tp1::BoundaryCondition boundary{tp1::BoundaryCondition::Walls};
};

void print_help(std::ostream& output) {
    output
        << "TP1 — Busqueda eficiente de particulas vecinas\n\n"
        << "Uso:\n"
        << "  tp1 --help\n"
        << "  tp1 --version\n"
        << "  tp1 generate [opciones]\n"
        << "  tp1 neighbors [opciones]\n\n"
        << "Opciones de generate:\n"
        << "  --N CANTIDAD          Numero de particulas (100)\n"
        << "  --L LADO              Lado del dominio (20)\n"
        << "  --r-min RADIO         Radio minimo (0.23)\n"
        << "  --r-max RADIO         Radio maximo (0.26)\n"
        << "  --property VALOR      Propiedad estatica (1)\n"
        << "  --seed SEMILLA        Semilla reproducible (0)\n"
        << "  --boundary TIPO       walls o periodic (walls)\n"
        << "  --attempts CANTIDAD   Intentos por particula (100000)\n"
        << "  --static RUTA         Salida estatica (static.txt)\n"
        << "  --dynamic RUTA        Salida dinamica (dynamic.txt)\n\n"
        << "Opciones de neighbors:\n"
        << "  --method METODO       brute-force (unico disponible)\n"
        << "  --static RUTA         Entrada estatica (static.txt)\n"
        << "  --dynamic RUTA        Entrada dinamica (dynamic.txt)\n"
        << "  --rc RADIO            Radio de interaccion (1)\n"
        << "  --boundary TIPO       walls o periodic (walls)\n"
        << "  --output RUTA         Lista de vecinos (neighbors.txt)\n\n"
        << "Comandos de fases posteriores:\n"
        << "  benchmark-m, benchmark-n\n";
}

std::string_view require_value(
    int& index,
    int argc,
    char* argv[],
    std::string_view option
) {
    if (index + 1 >= argc) {
        throw std::invalid_argument{
            std::string{"missing value for "} + std::string{option}
        };
    }
    ++index;
    return argv[index];
}

template <typename Number>
Number parse_integer(std::string_view text, std::string_view option) {
    Number value{};
    const char* begin = text.data();
    const char* end = begin + text.size();
    const auto result = std::from_chars(begin, end, value);
    if (result.ec != std::errc{} || result.ptr != end) {
        throw std::invalid_argument{
            std::string{"invalid integer for "} + std::string{option}
        };
    }
    return value;
}

double parse_double(std::string_view text, std::string_view option) {
    double value{};
    const char* begin = text.data();
    const char* end = begin + text.size();
    const auto result = std::from_chars(
        begin,
        end,
        value,
        std::chars_format::general
    );
    if (result.ec != std::errc{} || result.ptr != end
        || !std::isfinite(value)) {
        throw std::invalid_argument{
            std::string{"invalid number for "} + std::string{option}
        };
    }
    return value;
}

tp1::BoundaryCondition parse_boundary(std::string_view value) {
    if (value == "walls") {
        return tp1::BoundaryCondition::Walls;
    }
    if (value == "periodic") {
        return tp1::BoundaryCondition::Periodic;
    }
    throw std::invalid_argument{"boundary must be walls or periodic"};
}

GenerateArguments parse_generate(int argc, char* argv[]) {
    GenerateArguments arguments{};
    for (int index = 2; index < argc; ++index) {
        const std::string_view option{argv[index]};
        if (option == "--N") {
            arguments.config.particle_count = parse_integer<std::size_t>(
                require_value(index, argc, argv, option),
                option
            );
        } else if (option == "--L") {
            arguments.config.domain.side = parse_double(
                require_value(index, argc, argv, option),
                option
            );
        } else if (option == "--r-min") {
            arguments.config.min_radius = parse_double(
                require_value(index, argc, argv, option),
                option
            );
        } else if (option == "--r-max") {
            arguments.config.max_radius = parse_double(
                require_value(index, argc, argv, option),
                option
            );
        } else if (option == "--property") {
            arguments.config.property = parse_double(
                require_value(index, argc, argv, option),
                option
            );
        } else if (option == "--seed") {
            arguments.config.seed = parse_integer<std::uint64_t>(
                require_value(index, argc, argv, option),
                option
            );
        } else if (option == "--attempts") {
            arguments.config.max_attempts_per_particle =
                parse_integer<std::size_t>(
                    require_value(index, argc, argv, option),
                    option
                );
        } else if (option == "--boundary") {
            arguments.config.domain.boundary = parse_boundary(
                require_value(index, argc, argv, option)
            );
        } else if (option == "--static") {
            arguments.static_path = require_value(index, argc, argv, option);
        } else if (option == "--dynamic") {
            arguments.dynamic_path = require_value(index, argc, argv, option);
        } else {
            throw std::invalid_argument{
                std::string{"unknown generate option: "} + std::string{option}
            };
        }
    }

    if (!tp1::is_valid(arguments.config)) {
        throw std::invalid_argument{"invalid generation configuration"};
    }
    if (arguments.static_path.empty() || arguments.dynamic_path.empty()
        || arguments.static_path == arguments.dynamic_path) {
        throw std::invalid_argument{
            "static and dynamic output paths must be non-empty and different"
        };
    }
    return arguments;
}

std::filesystem::path normalized_absolute(
    const std::filesystem::path& path
) {
    return std::filesystem::absolute(path).lexically_normal();
}

NeighborArguments parse_neighbors(int argc, char* argv[]) {
    NeighborArguments arguments{};
    for (int index = 2; index < argc; ++index) {
        const std::string_view option{argv[index]};
        if (option == "--method") {
            const std::string_view method = require_value(
                index,
                argc,
                argv,
                option
            );
            if (method != "brute-force") {
                throw std::invalid_argument{
                    "only the brute-force method is available in this phase"
                };
            }
        } else if (option == "--static") {
            arguments.static_path = require_value(index, argc, argv, option);
        } else if (option == "--dynamic") {
            arguments.dynamic_path = require_value(index, argc, argv, option);
        } else if (option == "--output") {
            arguments.output_path = require_value(index, argc, argv, option);
        } else if (option == "--rc") {
            arguments.cutoff = parse_double(
                require_value(index, argc, argv, option),
                option
            );
        } else if (option == "--boundary") {
            arguments.boundary = parse_boundary(
                require_value(index, argc, argv, option)
            );
        } else {
            throw std::invalid_argument{
                std::string{"unknown neighbors option: "}
                + std::string{option}
            };
        }
    }

    if (arguments.cutoff < 0.0) {
        throw std::invalid_argument{"rc must be non-negative"};
    }
    if (arguments.static_path.empty() || arguments.dynamic_path.empty()
        || arguments.output_path.empty()) {
        throw std::invalid_argument{"input and output paths must be non-empty"};
    }

    const std::filesystem::path static_path = normalized_absolute(
        arguments.static_path
    );
    const std::filesystem::path dynamic_path = normalized_absolute(
        arguments.dynamic_path
    );
    const std::filesystem::path output_path = normalized_absolute(
        arguments.output_path
    );
    if (static_path == dynamic_path || output_path == static_path
        || output_path == dynamic_path) {
        throw std::invalid_argument{
            "static, dynamic and neighbor paths must be different"
        };
    }
    return arguments;
}

void ensure_parent_exists(const std::filesystem::path& path) {
    const std::filesystem::path parent = path.parent_path();
    if (!parent.empty()) {
        std::filesystem::create_directories(parent);
    }
}

void write_outputs(
    const GenerateArguments& arguments,
    const tp1::ParticleSystem& system
) {
    ensure_parent_exists(arguments.static_path);
    ensure_parent_exists(arguments.dynamic_path);

    std::ofstream static_output{arguments.static_path};
    if (!static_output) {
        throw std::runtime_error{"could not open static output"};
    }
    tp1::write_static(static_output, system);

    std::ofstream dynamic_output{arguments.dynamic_path};
    if (!dynamic_output) {
        throw std::runtime_error{"could not open dynamic output"};
    }
    tp1::write_dynamic(dynamic_output, system);
}

tp1::ParticleSystem read_inputs(const NeighborArguments& arguments) {
    std::ifstream static_input{arguments.static_path};
    if (!static_input) {
        throw std::runtime_error{"could not open static input"};
    }

    std::ifstream dynamic_input{arguments.dynamic_path};
    if (!dynamic_input) {
        throw std::runtime_error{"could not open dynamic input"};
    }

    return tp1::read_system(
        static_input,
        dynamic_input,
        arguments.boundary
    );
}

void write_neighbor_output(
    const std::filesystem::path& path,
    const tp1::NeighborList& neighbors
) {
    ensure_parent_exists(path);
    std::ofstream output{path};
    if (!output) {
        throw std::runtime_error{"could not open neighbor output"};
    }
    tp1::write_neighbors(output, neighbors);
}

std::string_view boundary_name(tp1::BoundaryCondition boundary) {
    return boundary == tp1::BoundaryCondition::Walls
        ? "walls"
        : "periodic";
}

int run_generate(int argc, char* argv[]) {
    const GenerateArguments arguments = parse_generate(argc, argv);
    const tp1::ParticleSystem system = tp1::generate_system(arguments.config);
    write_outputs(arguments, system);

    std::cout << "Generated " << system.particles.size()
              << " particles without overlaps"
              << " (boundary=" << boundary_name(system.domain.boundary)
              << ", seed=" << arguments.config.seed << ")\n"
              << "Static: " << arguments.static_path.string() << '\n'
              << "Dynamic: " << arguments.dynamic_path.string() << '\n';
    return 0;
}

int run_neighbors(int argc, char* argv[]) {
    const NeighborArguments arguments = parse_neighbors(argc, argv);
    const tp1::ParticleSystem system = read_inputs(arguments);

    const auto start = std::chrono::steady_clock::now();
    const tp1::NeighborSearchResult result = tp1::brute_force_neighbors(
        system,
        arguments.cutoff
    );
    const auto end = std::chrono::steady_clock::now();
    const auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(
        end - start
    );

    write_neighbor_output(arguments.output_path, result.neighbors);

    std::cout << "Found " << result.pair_count
              << " undirected neighbor pairs"
              << " (method=brute-force"
              << ", boundary=" << boundary_name(system.domain.boundary)
              << ", rc=" << arguments.cutoff << ")\n"
              << "Distance evaluations: " << result.distance_evaluations
              << '\n'
              << "Search time: " << elapsed.count() << " ns\n"
              << "Neighbors: " << arguments.output_path.string() << '\n';
    return 0;
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc == 1 || std::string_view{argv[1]} == "--help") {
        print_help(std::cout);
        return 0;
    }

    if (std::string_view{argv[1]} == "--version") {
        std::cout << tp1::kVersion << '\n';
        return 0;
    }

    if (argc == 3 && std::string_view{argv[2]} == "--help"
        && (std::string_view{argv[1]} == "generate"
            || std::string_view{argv[1]} == "neighbors")) {
        print_help(std::cout);
        return 0;
    }

    try {
        if (std::string_view{argv[1]} == "generate") {
            return run_generate(argc, argv);
        }
        if (std::string_view{argv[1]} == "neighbors") {
            return run_neighbors(argc, argv);
        }
        throw std::invalid_argument{
            std::string{"unknown command: "} + argv[1]
        };
    } catch (const std::invalid_argument& error) {
        std::cerr << "Error: " << error.what()
                  << "\nUse --help to inspect the interface.\n";
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
