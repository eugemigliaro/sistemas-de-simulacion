#pragma once
#include "tp4/billiard.hpp"
#include <charconv>
#include <fstream>
#include <iomanip>
#include <map>
#include <sstream>
#include <string>

namespace tp4::billiard {
inline std::size_t integer(const std::string& value) {
    std::size_t number = 0;
    const auto [end, error] = std::from_chars(value.data(), value.data() + value.size(), number);
    if (error != std::errc{} || end != value.data() + value.size())
        throw std::invalid_argument("entero invalido: " + value);
    return number;
}
inline double real(const std::string& value) {
    std::size_t end = 0;
    const double number = std::stod(value, &end);
    if (end != value.size() || !std::isfinite(number)) throw std::invalid_argument("numero invalido: " + value);
    return number;
}
inline std::vector<Particle> read_initial(const std::string& filename) {
    std::ifstream in(filename);
    if (!in) throw std::invalid_argument("no se puede abrir estado inicial");
    std::string line;
    if (!std::getline(in, line) || line != "id,x,y,vx,vy")
        throw std::invalid_argument("cabecera inicial esperada: id,x,y,vx,vy");
    std::vector<Particle> particles;
    while (std::getline(in, line)) {
        if (line.empty()) throw std::invalid_argument("fila inicial vacia");
        std::stringstream row(line);
        std::vector<std::string> values;
        std::string token;
        while (std::getline(row, token, ',')) values.push_back(token);
        if (values.size() != 5 || line.back() == ',' || integer(values[0]) != particles.size())
            throw std::invalid_argument("fila inicial invalida o IDs no consecutivos");
        particles.push_back({{real(values[1]), real(values[2])}, {real(values[3]), real(values[4])}, -1});
    }
    if (!in.eof()) throw std::runtime_error("error leyendo estado inicial");
    return particles;
}
inline int cli(int argc, char** argv) {
    Config c;
    std::string output, initial;
    double requested_dt = 0;
    std::map<std::string, bool> seen;
    std::map<std::string, double*> numbers{{"--duration", &c.duration}, {"--radius", &c.radius},
        {"--particle-radius", &c.particle_radius}, {"--mass", &c.mass}, {"--stiffness", &c.stiffness},
        {"--speed", &c.speed}, {"--obstacle-x", &c.obstacle_x}, {"--dt", &requested_dt}};
    for (int i = 2; i < argc; i += 2) {
        const std::string key = argv[i];
        if (seen[key] || i + 1 >= argc) throw std::invalid_argument("opcion duplicada o sin valor: " + key);
        seen[key] = true;
        const std::string value = argv[i + 1];
        if (key == "--output") output = value;
        else if (key == "--initial") initial = value;
        else if (key == "--n") c.n = integer(value);
        else if (key == "--steps") c.steps = integer(value);
        else if (key == "--save-every") c.save_every = integer(value);
        else if (key == "--seed") c.seed = integer(value);
        else if (key == "--obstacles") {
            if (value != "0" && value != "1") throw std::invalid_argument("--obstacles debe ser 0 o 1");
            c.obstacles = value == "1";
        } else if (numbers.contains(key)) *numbers.at(key) = real(value);
        else throw std::invalid_argument("opcion desconocida: " + key);
    }
    if (seen["--dt"]) {
        if (seen["--steps"] || requested_dt <= 0) throw std::invalid_argument("usar --dt positivo o --steps");
        const double count = c.duration / requested_dt;
        if (!std::isfinite(count) || count < 1 || count >= static_cast<double>(std::numeric_limits<long long>::max()) ||
            std::abs(count - std::round(count)) > 1e-9 * std::max(1.0, std::abs(count)))
            throw std::invalid_argument("duracion debe ser un multiplo entero de dt");
        c.steps = static_cast<std::size_t>(std::round(count));
    }
    c.validate();
    if (output.empty()) throw std::invalid_argument("falta --output");
    auto particles = initial.empty() ? generate(c) : read_initial(initial);
    validate_initial(particles, c);
    std::ofstream out(output);
    out.exceptions(std::ios::badbit | std::ios::failbit);
    out << std::setprecision(17) << "step,time,id,x,y,vx,vy,used,first_contact_step\n";
    simulate(c, std::move(particles), [&](std::size_t step, double time, const auto& state) {
        for (std::size_t i = 0; i < state.size(); ++i) {
            const auto& p = state[i];
            out << step << ',' << time << ',' << i << ',' << p.position.x << ',' << p.position.y << ','
                << p.velocity.x << ',' << p.velocity.y << ',' << (p.first_contact_step >= 0) << ','
                << p.first_contact_step << '\n';
        }
    });
    out.close();
    std::ofstream metadata(output + ".json");
    metadata.exceptions(std::ios::badbit | std::ios::failbit);
    metadata << std::setprecision(17) << "{\n  \"schema_version\": 1,\n  \"n\": " << c.n
        << ",\n  \"duration\": " << c.duration << ",\n  \"steps\": " << c.steps
        << ",\n  \"dt\": " << c.dt() << ",\n  \"save_every\": " << c.save_every
        << ",\n  \"radius\": " << c.radius << ",\n  \"particle_radius\": " << c.particle_radius
        << ",\n  \"mass\": " << c.mass << ",\n  \"stiffness\": " << c.stiffness
        << ",\n  \"speed\": " << c.speed << ",\n  \"obstacles\": " << (c.obstacles ? "true" : "false")
        << ",\n  \"obstacle_x\": " << c.obstacle_x << ",\n  \"seed\": " << c.seed
        << ",\n  \"generator\": \"mt19937_64: high 53 bits / 2^53\",\n"
           "  \"initialization\": \"" << (initial.empty() ? "area-uniform sequential rejection" : "input CSV")
        << "\",\n  \"method\": \"original Verlet; centered velocities\",\n"
           "  \"used_encoding\": \"0=blue/fresh; 1=red/used\"\n}\n";
    metadata.close();
    return 0;
}
} // namespace tp4::billiard
