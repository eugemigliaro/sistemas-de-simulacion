#include "tp4/dense.hpp"
#include <iostream>
int main() {
    using namespace tp4::billiard;
    try {
        Config c; c.n = 650; c.obstacles = true;
        auto a = generate_dense(c, 100), repeated = generate_dense(c, 100);
        validate_initial(a.particles, c);
        if (a.particles.size() != 650 || a.acceptance <= 0 || a.mean_square_displacement <= 0)
            throw std::runtime_error("inicializacion densa no aleatorizada");
        for (std::size_t i = 0; i < c.n; ++i)
            if ((a.particles[i].position - repeated.particles[i].position).norm2() != 0 ||
                std::abs(a.particles[i].velocity.norm2() - 1) > 1e-14)
                throw std::runtime_error("semilla o rapidez incorrecta");
        c.seed = 2;
        auto other = generate_dense(c, 100);
        if ((a.particles[0].position - other.particles[0].position).norm2() == 0)
            throw std::runtime_error("semillas no cambian configuracion");
        std::cout << "Denso: N=650, sin solapamientos, semilla y movimientos MC OK\n";
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
