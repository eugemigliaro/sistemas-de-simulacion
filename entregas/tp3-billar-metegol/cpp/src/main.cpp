#include <iostream>
#include <string_view>
#include <vector>

#include "tp3/version.hpp"

namespace {

void print_usage(std::ostream& stream) {
    stream << "uso: tp3 <comando> [opciones]\n"
           << "\n"
           << "comandos:\n"
           << "  --version    imprime nombre y version del motor\n"
           << "\n"
           << "El motor solo genera el estado del sistema (tiempo, posiciones,\n"
           << "velocidades y color). Los observables se calculan en el\n"
           << "post-proceso de Python.\n";
}

}  // namespace

int main(int argc, char** argv) {
    const std::vector<std::string_view> arguments(argv + 1, argv + argc);

    if (arguments.empty()) {
        print_usage(std::cerr);
        return 1;
    }

    if (arguments.front() == "--version") {
        std::cout << tp3::engine_name << ' ' << tp3::engine_version << '\n';
        return 0;
    }

    std::cerr << "comando desconocido: " << arguments.front() << "\n\n";
    print_usage(std::cerr);
    return 1;
}
