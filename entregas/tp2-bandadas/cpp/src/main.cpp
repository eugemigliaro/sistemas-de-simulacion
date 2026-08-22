#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <locale>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>

#include "tp2/runner.hpp"

namespace {

constexpr std::string_view version{"0.1.0"};

struct Arguments {
    tp2::RunConfig run{};
    double density{};
    std::filesystem::path trajectory_path{};
    std::filesystem::path observations_path{};
};

void print_help(std::ostream& output) {
    output
        << "Uso:\n"
        << "  tp2 --help\n"
        << "  tp2 --version\n"
        << "  tp2 simulate [opciones]\n\n"
        << "Opciones de simulate:\n"
        << "  --model MODELO       vicsek o voter (requerido)\n"
        << "  --rho DENSIDAD       densidad, normalmente 2, 4 u 8\n"
        << "  --eta RUIDO          valor normalizado entre 0 y 1\n"
        << "  --steps CANTIDAD     pasos a simular\n"
        << "  --seed SEMILLA       semilla reproducible\n"
        << "  --M CANTIDAD         celdas por lado (9)\n"
        << "  --L LADO             lado de caja (10)\n"
        << "  --rc RADIO           radio de interacción (1)\n"
        << "  --v RAPIDEZ          rapidez común (0.03)\n"
        << "  --dt PASO            paso temporal (1)\n"
        << "  --trajectory-every N guardar un cuadro cada N pasos (1)\n"
        << "  --trajectory RUTA    CSV opcional de partículas\n"
        << "  --observables RUTA   CSV de va, S y tiempos CIM (requerido)\n";
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
    return argv[++index];
}

template <typename Number>
Number parse_integer(std::string_view text, std::string_view option) {
    Number value{};
    const auto result = std::from_chars(
        text.data(),
        text.data() + text.size(),
        value
    );
    if (result.ec != std::errc{}
        || result.ptr != text.data() + text.size()) {
        throw std::invalid_argument{
            std::string{"invalid integer for "} + std::string{option}
        };
    }
    return value;
}

double parse_double(std::string_view text, std::string_view option) {
    double value{};
    std::istringstream input{std::string{text}};
    input.imbue(std::locale::classic());
    input >> std::noskipws >> value;
    if (!input || input.peek() != std::char_traits<char>::eof()
        || !std::isfinite(value)) {
        throw std::invalid_argument{
            std::string{"invalid number for "} + std::string{option}
        };
    }
    return value;
}

tp2::AlignmentModel parse_model(std::string_view value) {
    if (value == "vicsek") {
        return tp2::AlignmentModel::Vicsek;
    }
    if (value == "voter") {
        return tp2::AlignmentModel::Voter;
    }
    throw std::invalid_argument{"model must be vicsek or voter"};
}

Arguments parse_arguments(int argc, char* argv[]) {
    Arguments arguments{};
    bool has_model = false;
    bool has_density = false;
    bool has_eta = false;
    bool has_steps = false;
    bool has_seed = false;

    arguments.run.initialization.side = 10.0;
    arguments.run.dynamics.cutoff = 1.0;
    arguments.run.dynamics.speed = 0.03;
    arguments.run.dynamics.time_step = 1.0;
    arguments.run.cells_per_side = 9;
    arguments.run.trajectory_every = 1;

    for (int index = 2; index < argc; ++index) {
        const std::string_view option{argv[index]};
        const std::string_view value = require_value(
            index,
            argc,
            argv,
            option
        );
        if (option == "--model") {
            arguments.run.dynamics.model = parse_model(value);
            has_model = true;
        } else if (option == "--rho") {
            arguments.density = parse_double(value, option);
            has_density = true;
        } else if (option == "--eta") {
            arguments.run.dynamics.eta = parse_double(value, option);
            has_eta = true;
        } else if (option == "--steps") {
            arguments.run.steps = parse_integer<std::size_t>(value, option);
            has_steps = true;
        } else if (option == "--seed") {
            arguments.run.initialization.seed =
                parse_integer<std::uint64_t>(value, option);
            has_seed = true;
        } else if (option == "--M") {
            arguments.run.cells_per_side =
                parse_integer<std::size_t>(value, option);
        } else if (option == "--L") {
            arguments.run.initialization.side = parse_double(value, option);
        } else if (option == "--rc") {
            arguments.run.dynamics.cutoff = parse_double(value, option);
        } else if (option == "--v") {
            arguments.run.dynamics.speed = parse_double(value, option);
        } else if (option == "--dt") {
            arguments.run.dynamics.time_step = parse_double(value, option);
        } else if (option == "--trajectory-every") {
            arguments.run.trajectory_every =
                parse_integer<std::size_t>(value, option);
        } else if (option == "--trajectory") {
            arguments.trajectory_path = value;
        } else if (option == "--observables") {
            arguments.observations_path = value;
        } else {
            throw std::invalid_argument{
                std::string{"unknown option: "} + std::string{option}
            };
        }
    }

    if (!has_model || !has_density || !has_eta || !has_steps || !has_seed) {
        throw std::invalid_argument{
            "model, rho, eta, steps and seed are required"
        };
    }
    if (!(arguments.density > 0.0)) {
        throw std::invalid_argument{"rho must be positive"};
    }
    const double particle_count = arguments.density
        * arguments.run.initialization.side
        * arguments.run.initialization.side;
    const double rounded = std::round(particle_count);
    if (rounded < 1.0
        || rounded > static_cast<double>(
            std::numeric_limits<std::size_t>::max()
        )
        || std::abs(particle_count - rounded) > 1e-9) {
        throw std::invalid_argument{"rho * L^2 must be a positive integer"};
    }
    arguments.run.initialization.particle_count =
        static_cast<std::size_t>(rounded);

    if (arguments.observations_path.empty()) {
        throw std::invalid_argument{"observables path is required"};
    }
    if (!arguments.trajectory_path.empty()
        && std::filesystem::absolute(arguments.trajectory_path)
                .lexically_normal()
            == std::filesystem::absolute(arguments.observations_path)
                .lexically_normal()) {
        throw std::invalid_argument{"output paths must be different"};
    }
    if (!tp2::is_valid(arguments.run)) {
        throw std::invalid_argument{"invalid run configuration"};
    }
    return arguments;
}

std::ofstream open_output(const std::filesystem::path& path) {
    if (path.has_parent_path()) {
        std::filesystem::create_directories(path.parent_path());
    }
    std::ofstream output{path};
    if (!output) {
        throw std::runtime_error{"cannot open output: " + path.string()};
    }
    return output;
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string_view{argv[1]} == "--help") {
            print_help(std::cout);
            return 0;
        }
        if (argc == 2 && std::string_view{argv[1]} == "--version") {
            std::cout << version << '\n';
            return 0;
        }
        if (argc < 2 || std::string_view{argv[1]} != "simulate") {
            print_help(std::cerr);
            return 2;
        }

        const Arguments arguments = parse_arguments(argc, argv);
        std::ofstream observations = open_output(arguments.observations_path);
        std::optional<std::ofstream> trajectory;
        if (!arguments.trajectory_path.empty()) {
            trajectory.emplace(open_output(arguments.trajectory_path));
        }
        const tp2::RunSummary summary = tp2::run_simulation(
            arguments.run,
            observations,
            trajectory ? &*trajectory : nullptr
        );
        std::cout << "Simulación completada: "
                  << summary.observations_written << " observaciones, "
                  << summary.frames_written << " cuadros.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
