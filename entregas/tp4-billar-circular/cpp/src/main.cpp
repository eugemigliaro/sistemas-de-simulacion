#include <charconv>
#include <cstddef>
#include <cmath>
#include <cstdint>
#include <exception>
#include <fstream>
#include <iostream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include "tp4/billiard.hpp"
#include "tp4/generation.hpp"
#include "tp4/io.hpp"
#include "tp4/oscillator.hpp"
#include "tp4/simulation.hpp"

namespace {

constexpr std::string_view usage =
    "uso: tp4 <comando> [opciones]\n"
    "\n"
    "tp4 oscillator --integrator <nombre> --dt <s> [--tf <s>] [--output <archivo>]\n"
    "  integra el oscilador amortiguado de la teorica 4 desde t = 0 hasta tf (default 5 s)\n"
    "  integradores: beeman, verlet, velocity-verlet, euler-pc\n"
    "\n"
    "tp4 billiard --n <N> --dt <s> --tf <s> [opciones] [--output <archivo>]\n"
    "  --output-every <n>   guarda el estado cada n pasos (default 1)\n"
    "  --x0 <m>             obstaculos en (-x0, 0) y (x0, 0); sin esta opcion, billar vacio\n"
    "  --seed <entero>      semilla de las condiciones iniciales (default 0)\n"
    "  --layout <nombre>    random (default) o lattice para densidades altas\n"
    "  --sweeps <n>         barridos de Monte Carlo de lattice (default 500)\n"
    "\n"
    "Sin --output, el estado se escribe en la salida estandar. El motor solo\n"
    "escribe estado; los observables se calculan en el post-proceso.\n";

class Arguments {
public:
    Arguments(int argc, char** argv) {
        for (int i = 2; i < argc; i += 2) {
            const std::string key = argv[i];
            if (!key.starts_with("--") || i + 1 >= argc) {
                throw std::invalid_argument("opcion sin valor: " + key);
            }
            if (!values_.emplace(key, argv[i + 1]).second) {
                throw std::invalid_argument("opcion repetida: " + key);
            }
        }
    }

    [[nodiscard]] std::optional<std::string> text(const std::string& key) {
        const auto it = values_.find(key);
        if (it == values_.end()) {
            return std::nullopt;
        }
        std::string value = it->second;
        values_.erase(it);
        return value;
    }

    [[nodiscard]] std::optional<double> real(const std::string& key) {
        const auto value = text(key);
        if (!value) {
            return std::nullopt;
        }
        // std::stod en lugar de from_chars: libc++ de macOS no siempre trae
        // from_chars para double.
        std::size_t consumed = 0;
        double number{};
        try {
            number = std::stod(*value, &consumed);
        } catch (const std::exception&) {
            consumed = 0;
        }
        if (consumed != value->size() || !std::isfinite(number)) {
            throw std::invalid_argument("numero invalido en " + key + ": " + *value);
        }
        return number;
    }

    [[nodiscard]] std::optional<std::uint64_t> integer(const std::string& key) {
        const auto value = text(key);
        if (!value) {
            return std::nullopt;
        }
        std::uint64_t number{};
        const auto [end, error] = std::from_chars(value->data(), value->data() + value->size(), number);
        if (error != std::errc{} || end != value->data() + value->size()) {
            throw std::invalid_argument("entero invalido en " + key + ": " + *value);
        }
        return number;
    }

    template <typename T>
    [[nodiscard]] static T required(std::optional<T> value, const std::string& key) {
        if (!value) {
            throw std::invalid_argument("falta " + key);
        }
        return *value;
    }

    void ensure_consumed() const {
        if (!values_.empty()) {
            throw std::invalid_argument("opcion desconocida: " + values_.begin()->first);
        }
    }

private:
    std::map<std::string, std::string> values_;
};

std::uint64_t step_count(double tf, double dt) {
    const double ratio = tf / dt;
    const double steps = std::round(ratio);
    if (!(tf > 0.0) || !(dt > 0.0) || steps < 1.0 || std::abs(ratio - steps) > 1e-9 * steps) {
        throw std::invalid_argument("tf debe ser un multiplo entero positivo de dt");
    }
    return static_cast<std::uint64_t>(steps);
}

// Escribe en el archivo pedido o en la salida estándar.
class Output {
public:
    explicit Output(const std::optional<std::string>& path) {
        if (path) {
            file_.open(*path);
            if (!file_) {
                throw std::runtime_error("no se pudo abrir " + *path);
            }
        }
    }

    std::ostream& stream() { return file_.is_open() ? file_ : std::cout; }

    void close() {
        stream().flush();
        if (!stream()) {
            throw std::runtime_error("error al escribir la salida");
        }
    }

private:
    std::ofstream file_;
};

void run_oscillator(Arguments& arguments) {
    const tp4::Integrator integrator =
        tp4::parse_integrator(Arguments::required(arguments.text("--integrator"), "--integrator"));
    const double dt = Arguments::required(arguments.real("--dt"), "--dt");
    const double tf = arguments.real("--tf").value_or(5.0);
    const auto path = arguments.text("--output");
    arguments.ensure_consumed();

    const tp4::Oscillator oscillator{};
    const std::uint64_t steps = step_count(tf, dt);
    Output output(path);
    std::ostream& stream = output.stream();
    tp4::write_oscillator_header(stream, oscillator, integrator, dt);
    tp4::integrate(oscillator, integrator, dt, steps,
                   [&](const tp4::OscillatorSample& sample) { tp4::write_sample(stream, sample); });
    output.close();
}

void run_billiard(Arguments& arguments) {
    tp4::Billiard billiard{};
    billiard.obstacle_x = arguments.real("--x0");
    tp4::Generation generation{};
    generation.particle_count = Arguments::required(arguments.integer("--n"), "--n");
    generation.seed = arguments.integer("--seed").value_or(0);
    generation.layout = tp4::parse_layout(arguments.text("--layout").value_or("random"));
    generation.lattice_sweeps = arguments.integer("--sweeps").value_or(generation.lattice_sweeps);
    tp4::Run run{};
    run.dt = Arguments::required(arguments.real("--dt"), "--dt");
    run.steps = step_count(Arguments::required(arguments.real("--tf"), "--tf"), run.dt);
    run.output_every = arguments.integer("--output-every").value_or(1);
    const auto path = arguments.text("--output");
    arguments.ensure_consumed();
    tp4::validate(billiard);
    tp4::validate(run);

    std::vector<tp4::Particle> particles = tp4::generate(billiard, generation);
    Output output(path);
    std::ostream& stream = output.stream();
    tp4::write_billiard_header(stream, billiard, generation, run);
    tp4::simulate(billiard, std::move(particles), run,
                  [&](std::uint64_t step, double time, const std::vector<tp4::Particle>& state) {
                      tp4::write_frame(stream, step, time, state);
                  });
    output.close();
}

}  // namespace

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false);
    const std::string_view command = argc >= 2 ? argv[1] : "";
    try {
        if (command == "--help" || command == "-h") {
            std::cout << usage;
            return 0;
        }
        Arguments arguments(argc, argv);
        if (command == "oscillator") {
            run_oscillator(arguments);
        } else if (command == "billiard") {
            run_billiard(arguments);
        } else {
            throw std::invalid_argument("comando desconocido: '" + std::string(command) + "'");
        }
        return 0;
    } catch (const std::invalid_argument& error) {
        std::cerr << "tp4: " << error.what() << "\n\n" << usage;
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "tp4: " << error.what() << '\n';
        return 1;
    }
}
