#pragma once

#include <cstdint>
#include <vector>

#include "tp4/billiard.hpp"

namespace tp4 {

// Fuerzas de contacto F = -k xi e sobre cada partícula, con xi > 0 la
// superposición y e la normal hacia el otro cuerpo [TP04, p. 2]. La pared se
// trata con la partícula imagen en (R + r) r/|r|, recalculada en cada
// evaluación [TP04, p. 3]. Los pares se buscan con celdas de lado >= 2r, de
// modo que cada partícula solo se compara con su celda y las vecinas.
class ForceField {
public:
    explicit ForceField(const Billiard& billiard);

    // touches_obstacle[i] vale 1 si la partícula i se superpone con algún
    // obstáculo en estas posiciones.
    void compute(
        const std::vector<Particle>& particles,
        std::vector<Vec2>& forces,
        std::vector<std::uint8_t>& touches_obstacle
    );

private:
    void sort_into_cells(const std::vector<Particle>& particles);
    [[nodiscard]] int cell_coordinate(double coordinate) const noexcept;

    Billiard billiard_;
    std::vector<Vec2> obstacles_;
    int cells_per_side_{};
    double cell_size_{};
    std::vector<std::uint32_t> cell_of_;
    std::vector<std::uint32_t> cell_start_;
    std::vector<std::uint32_t> cursor_;
    std::vector<std::uint32_t> sorted_;
};

}  // namespace tp4
