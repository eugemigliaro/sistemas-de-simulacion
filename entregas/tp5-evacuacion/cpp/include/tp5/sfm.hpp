#pragma once

#include <cstddef>
#include <cstdint>
#include <random>
#include <vector>

#include "tp5/model.hpp"

namespace tp5 {

// Celdas de lado >= 2 radius_max que cubren la sala y la franja de salida (CIM del TP1).
class CellGrid {
public:
    CellGrid(const Params& params, const Room& room);

    void build(const std::vector<Agent>& agents, const std::vector<std::size_t>& indices);

    // Llama a f(i, j) una vez por cada par de agentes en celdas vecinas.
    template <typename F>
    void for_each_pair(const std::vector<Agent>& agents, F&& f) const;

    [[nodiscard]] int cell_index(const Vec2& position) const noexcept;
    [[nodiscard]] int columns() const noexcept { return columns_; }
    [[nodiscard]] int rows() const noexcept { return rows_; }
    [[nodiscard]] int head(int cell) const noexcept { return head_[static_cast<std::size_t>(cell)]; }
    [[nodiscard]] int next(std::size_t agent) const noexcept { return next_[agent]; }

private:
    double x0_;
    double y0_;
    double size_;
    int columns_;
    int rows_;
    std::vector<int> head_;
    std::vector<int> next_;
};

struct Contact {
    std::size_t i;
    std::size_t j;  // otro agente; si wall >= 0, no se usa
    int wall;       // índice de la pared, o -1 entre agentes
    Vec2 n;         // de j (o de la pared) hacia i
    Vec2 t;         // perpendicular(n)
    double xi;      // superposición
};

// Fuerzas del SFM sin fuerza social [B26, pp. 1-2] sobre un subconjunto de agentes:
// deseo m (v_d e - v)/tau, resorte k xi n y fricción kappa xi dv_t t con agentes y paredes.
class ForceField {
public:
    ForceField(const Params& params, const Room& room);

    // Busca contactos entre los agentes de `indices` (y con las paredes) en sus
    // posiciones actuales y guarda la parte de resorte, que solo depende de ellas.
    void find_contacts(const std::vector<Agent>& agents, const std::vector<std::size_t>& indices);

    // Aceleración de cada agente de `indices` con sus velocidades actuales, usando
    // los contactos de la última búsqueda.
    void accelerations(const std::vector<Agent>& agents, const std::vector<std::size_t>& indices,
                       std::vector<Vec2>& out) const;

    [[nodiscard]] const std::vector<Contact>& contacts() const noexcept { return contacts_; }
    [[nodiscard]] const CellGrid& grid() const noexcept { return grid_; }

    // Renueva la fuerza de fluctuación de todos los agentes (si noise > 0).
    void refresh_noise();
    [[nodiscard]] int contact_count(std::size_t agent) const noexcept { return count_[agent]; }

private:
    const Params& params_;
    const Room& room_;
    CellGrid grid_;
    std::vector<Contact> contacts_;
    std::vector<Vec2> spring_;
    std::vector<int> count_;
    std::vector<Vec2> noise_;
    std::mt19937_64 rng_;
};

// Un paso de Beeman predictor-corrector con fuerzas que dependen de la velocidad
// [T04, p. 20] para los agentes de `indices`. La aceleración que se guarda para el
// paso siguiente se reevalúa con la velocidad corregida, reusando los contactos.
class Beeman {
public:
    Beeman(const Params& params, const Room& room);

    void step(std::vector<Agent>& agents, const std::vector<std::size_t>& indices);

    [[nodiscard]] const ForceField& forces() const noexcept { return forces_; }

private:
    const Params& params_;
    ForceField forces_;
    std::uint64_t steps_ = 0;
    std::uint64_t noise_every_ = 1;
    std::vector<Vec2> old_velocity_;
    std::vector<Vec2> predicted_acceleration_;
    std::vector<Vec2> new_acceleration_;
};

template <typename F>
void CellGrid::for_each_pair(const std::vector<Agent>& agents, F&& f) const {
    // Media vecindad (como en el CIM): cada par se visita una sola vez.
    static constexpr int offsets[4][2] = {{1, 0}, {-1, 1}, {0, 1}, {1, 1}};
    for (int row = 0; row < rows_; ++row) {
        for (int column = 0; column < columns_; ++column) {
            const int cell = row * columns_ + column;
            for (int i = head_[static_cast<std::size_t>(cell)]; i >= 0; i = next_[static_cast<std::size_t>(i)]) {
                for (int j = next_[static_cast<std::size_t>(i)]; j >= 0; j = next_[static_cast<std::size_t>(j)]) {
                    f(static_cast<std::size_t>(i), static_cast<std::size_t>(j));
                }
                for (const auto& offset : offsets) {
                    const int c = column + offset[0];
                    const int r = row + offset[1];
                    if (c < 0 || c >= columns_ || r >= rows_) continue;
                    for (int j = head_[static_cast<std::size_t>(r * columns_ + c)]; j >= 0;
                         j = next_[static_cast<std::size_t>(j)]) {
                        f(static_cast<std::size_t>(i), static_cast<std::size_t>(j));
                    }
                }
            }
        }
    }
    (void)agents;
}

}  // namespace tp5
