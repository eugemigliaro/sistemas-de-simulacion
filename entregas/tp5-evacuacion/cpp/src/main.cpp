#include <charconv>
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

#include "tp5/collision.hpp"
#include "tp5/model.hpp"
#include "tp5/output.hpp"
#include "tp5/setup.hpp"
#include "tp5/simulation.hpp"

namespace {

constexpr std::string_view usage =
    "uso: tp5 <comando> [opciones]\n"
    "\n"
    "tp5 evacuate --scheme tsdmd|edmd|hybrid [opciones] [--output <archivo>]\n"
    "  sistema:   --agents 500 --side 50 --door 0.8 --desired-speed 1.5 --radius-min 0.18 --radius-max 0.25\n"
    "             --second-target away|point --second-distance 5 --exit-distance 1 --target-fraction 0.6\n"
    "  SFM:       --mass 80 --mass-by-area 1 --reference-radius 0.215 --tau 0.5 --kn 1.2e5 --kt 2.4e5\n"
    "             --noise 0 --noise-time 0.1 (fluctuacion opcional solo en contacto, fraccion de m v_d / tau)\n"
    "  TSDMD:     --dt 1e-3\n"
    "  hibrido:   --t-star 0.5 --t-out-factor 2 --speed-bound 3 --relax-check-every 10\n"
    "  EDMD:      --relaxation kicks|analytic --kick 0.05 --aim-tolerance 0.01 --relax-tolerance 0.01\n"
    "  corrida:   --seed 0 --t-max 4000 --clog-time 300 --output-dt 0 (0: sin cuadros; solo salidas y cambios de modo)\n"
    "             --progress 0 (cada cuantos segundos simulados informar el avance por stderr)\n"
    "\n"
    "tp5 collision --dt <s> [--radius-i 0.25 --radius-j 0.18 --speed 1.5 --offset 0 --mass-by-area 1]\n"
    "  choque aislado de dos agentes con el contacto blando del SFM, sin deseo, y la regla\n"
    "  de disco duro equivalente: duracion, superposicion maxima y cocientes de velocidad.\n"
    "\n"
    "Sin --output, el estado se escribe en la salida estandar. El motor solo escribe\n"
    "estado; los observables se calculan en el post-proceso.\n";

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
        if (it == values_.end()) return std::nullopt;
        std::string value = it->second;
        values_.erase(it);
        return value;
    }

    [[nodiscard]] std::optional<double> real(const std::string& key) {
        const auto value = text(key);
        if (!value) return std::nullopt;
        // std::stod en lugar de from_chars: libc++ de macOS no siempre trae from_chars para double.
        std::size_t consumed = 0;
        double number{};
        try {
            number = std::stod(*value, &consumed);
        } catch (const std::exception&) {
            consumed = 0;
        }
        if (consumed != value->size() || std::isnan(number)) {
            throw std::invalid_argument("numero invalido en " + key + ": " + *value);
        }
        return number;
    }

    [[nodiscard]] std::optional<std::uint64_t> integer(const std::string& key) {
        const auto value = text(key);
        if (!value) return std::nullopt;
        std::uint64_t number{};
        const auto [end, error] = std::from_chars(value->data(), value->data() + value->size(), number);
        if (error != std::errc{} || end != value->data() + value->size()) {
            throw std::invalid_argument("entero invalido en " + key + ": " + *value);
        }
        return number;
    }

    void real_into(const std::string& key, double& target) {
        if (const auto value = real(key)) target = *value;
    }

    void ensure_consumed() const {
        if (!values_.empty()) throw std::invalid_argument("opcion desconocida: " + values_.begin()->first);
    }

private:
    std::map<std::string, std::string> values_;
};

class Output {
public:
    explicit Output(const std::optional<std::string>& path) {
        if (path) {
            file_.open(*path);
            if (!file_) throw std::runtime_error("no se pudo abrir " + *path);
        }
    }

    std::ostream& stream() { return file_.is_open() ? file_ : std::cout; }

    void close() {
        stream().flush();
        if (!stream()) throw std::runtime_error("error al escribir la salida");
    }

private:
    std::ofstream file_;
};

void read_model(Arguments& a, tp5::Params& p) {
    if (const auto n = a.integer("--agents")) p.agents = static_cast<int>(*n);
    a.real_into("--side", p.side);
    a.real_into("--door", p.door);
    a.real_into("--desired-speed", p.desired_speed);
    a.real_into("--radius-min", p.radius_min);
    a.real_into("--radius-max", p.radius_max);
    a.real_into("--exit-distance", p.exit_distance);
    a.real_into("--target-fraction", p.target_fraction);
    if (const auto s = a.text("--second-target")) p.second_target = tp5::parse_second_target(*s);
    a.real_into("--second-distance", p.second_target_distance);
    a.real_into("--mass", p.mass);
    if (const auto m = a.integer("--mass-by-area")) p.mass_by_area = *m != 0;
    a.real_into("--reference-radius", p.reference_radius);
    a.real_into("--tau", p.tau);
    a.real_into("--kn", p.kn);
    a.real_into("--kt", p.kt);
    a.real_into("--noise", p.noise);
    a.real_into("--noise-time", p.noise_time);
    a.real_into("--dt", p.dt);
}

void run_evacuation(Arguments& a) {
    tp5::Params p;
    p.scheme = tp5::parse_scheme(a.text("--scheme").value_or("tsdmd"));
    read_model(a, p);
    a.real_into("--t-star", p.t_star);
    a.real_into("--t-out-factor", p.t_out_factor);
    a.real_into("--speed-bound", p.speed_bound);
    if (const auto k = a.integer("--relax-check-every")) p.relax_check_every = static_cast<int>(*k);
    if (const auto r = a.text("--relaxation")) p.relaxation = tp5::parse_relaxation(*r);
    a.real_into("--kick", p.kick);
    a.real_into("--aim-tolerance", p.aim_tolerance);
    a.real_into("--relax-tolerance", p.relax_tolerance);
    if (const auto s = a.integer("--seed")) p.seed = *s;
    a.real_into("--t-max", p.t_max);
    a.real_into("--clog-time", p.clog_time);
    a.real_into("--output-dt", p.output_dt);
    a.real_into("--progress", p.progress);
    const auto path = a.text("--output");
    a.ensure_consumed();
    tp5::validate(p);

    const tp5::Room room(p);
    auto agents = tp5::initial_agents(p, room);
    Output output(path);
    tp5::Writer writer(&output.stream());
    const tp5::Summary s = tp5::simulate(p, std::move(agents), writer);
    output.close();
    std::cerr << "tp5: " << tp5::to_string(p.scheme) << " t=" << s.end_time << " s, salieron " << s.exited << ", quedan "
              << s.remaining << (s.clogged ? " (atasco)" : "") << ", pasos " << s.steps << ", eventos " << s.events
              << ", wall " << s.wall_seconds << " s\n";
}

void run_collision(Arguments& a) {
    tp5::Params p;
    read_model(a, p);
    tp5::CollisionSetup setup;
    a.real_into("--radius-i", setup.radius_i);
    a.real_into("--radius-j", setup.radius_j);
    a.real_into("--speed", setup.speed);
    a.real_into("--offset", setup.offset);
    a.ensure_consumed();
    if (!(setup.offset >= 0.0 && setup.offset < 1.0)) throw std::invalid_argument("offset debe estar en [0, 1)");
    const tp5::CollisionResult r = tp5::simulate_collision(p, setup);
    std::cout.precision(12);
    std::cout << "dt " << p.dt << " speed " << setup.speed << " offset " << setup.offset << '\n'
              << "contact_time " << r.contact_time << '\n'
              << "max_overlap " << r.max_overlap << '\n'
              << "normal_ratio " << r.normal_ratio << '\n'
              << "tangential_ratio " << r.tangential_ratio << '\n'
              << "hard_normal_ratio " << r.hard_normal_ratio << '\n'
              << "hard_tangential_ratio " << r.hard_tangential_ratio << '\n';
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
        if (command == "evacuate") {
            run_evacuation(arguments);
        } else if (command == "collision") {
            run_collision(arguments);
        } else {
            throw std::invalid_argument("comando desconocido: '" + std::string(command) + "'");
        }
        return 0;
    } catch (const std::invalid_argument& error) {
        std::cerr << "tp5: " << error.what() << "\n\n" << usage;
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "tp5: " << error.what() << '\n';
        return 1;
    }
}
