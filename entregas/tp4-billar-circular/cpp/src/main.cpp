#include "tp4/oscillator.hpp"
#include "tp4/billiard_cli.hpp"
#include <charconv>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout << "tp4 oscillator --method beeman|verlet|velocity-verlet|euler-pc --output FILE\n"
                         "  [--steps 1000 --duration 5 --mass 70 --stiffness 10000 --damping 100 --x0 1 --v0 -0.7142857142857143]\n"
                         "tp4 billiard --output FILE [--n 300 --duration 2 --dt 0.0001 --save-every 5]\n"
                         "  [--seed 1 --obstacles 0|1 --obstacle-x 0.0175 --initial FILE]\n"
                         "  [--radius 0.51 --particle-radius 0.0175 --mass 0.025 --stiffness 10000 --speed 1]\n"
                         "  --steps puede reemplazar --dt; save-every debe dividir steps.\n";
            return 0;
        }
        if (argc >= 2 && std::string_view(argv[1]) == "billiard") return tp4::billiard::cli(argc, argv);
        if (argc < 2 || std::string_view(argv[1]) != "oscillator")
            throw std::invalid_argument("usar tp4 --help");
        tp4::Config c;
        std::map<std::string, double*> numbers{{"--duration", &c.duration}, {"--mass", &c.mass},
            {"--stiffness", &c.stiffness}, {"--damping", &c.damping}, {"--x0", &c.x0}, {"--v0", &c.v0}};
        std::map<std::string, bool> seen;
        std::string method, filename;
        for (int i = 2; i < argc; i += 2) {
            const std::string key = argv[i];
            if (seen[key] || i + 1 >= argc) throw std::invalid_argument("opcion duplicada o sin valor: " + key);
            seen[key] = true;
            const std::string value = argv[i + 1];
            if (key == "--method") method = value;
            else if (key == "--output") filename = value;
            else if (key == "--steps") {
                const auto [end, error] = std::from_chars(value.data(), value.data() + value.size(), c.steps);
                if (error != std::errc{} || end != value.data() + value.size())
                    throw std::invalid_argument("numero de pasos invalido");
            } else if (numbers.contains(key)) {
                std::size_t end = 0;
                *numbers.at(key) = std::stod(value, &end);
                if (end != value.size()) throw std::invalid_argument("numero invalido: " + value);
            } else throw std::invalid_argument("opcion desconocida: " + key);
        }
        const auto selected = tp4::parse_method(method);
        c.validate();
        if (filename.empty()) throw std::invalid_argument("falta --output");
        std::ofstream out(filename);
        out.exceptions(std::ios::badbit | std::ios::failbit);
        out << std::setprecision(17) << "step,time,position,velocity\n";
        tp4::simulate(c, selected, [&](tp4::Sample s) {
            out << s.step << ',' << s.time << ',' << s.position << ',' << s.velocity << '\n';
        });
        out.close();
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "tp4: " << e.what() << '\n';
        return 2;
    }
}
