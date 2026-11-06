// EDMD puro: discos duros entre eventos [T03, p. 6], choques con la regla derivada
// del SFM (events.hpp) y celdas con eventos de cruce para buscar compañeros.
//
// Recuperación de v_d después de un choque, dos variantes:
//  - Patadas: movimiento rectilíneo uniforme entre eventos y, cada delta, a todos los
//    agentes sin relajar, v <- v_d e + (v - v_d e) e^{-delta/tau}.
//  - Analítica: entre eventos, la solución exacta de la relajación del SFM con la
//    dirección deseada e congelada, x(t) = x0 + u s + w tau (1 - e^{-s/tau}), con
//    u = v_d e y w = v0 - u. Termina con un evento de fin de relajación (|w e^{-s/tau}|
//    <= tol v_d: pasa a recta) o de reapuntado (la dirección al target se apartó de
//    la congelada más que aim_tolerance). Los contactos y cruces dejan de ser
//    cuadráticas: se buscan con avance conservador (pasos de brecha / rapidez máxima,
//    que no saltean la raíz).

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

#include "tp5/events.hpp"
#include "tp5/simulation.hpp"

namespace tp5 {
namespace {

enum class Kind : std::uint8_t { Output, Kick, Exit, Door, Relax, Aim, Wall, Pair, Cell };

struct Event {
    double time;
    Kind kind;
    std::uint32_t i;
    std::uint32_t j;
    std::uint32_t version_i;
    std::uint32_t version_j;
    std::int32_t extra;  // pared, o celda de destino
};

// Montículo de mínimos: ante empates de tiempo, el orden de Kind.
struct Later {
    bool operator()(const Event& a, const Event& b) const noexcept {
        if (a.time != b.time) return a.time > b.time;
        return a.kind > b.kind;
    }
};

constexpr std::uint32_t none = static_cast<std::uint32_t>(-1);
constexpr double tolerance = 1e-9;      // brecha a la que se da por alcanzado un contacto [m]
constexpr double crawl = 1e-6;          // paso mínimo mientras dos superficies en contacto se separan [s]
constexpr int max_iterations = 200000;  // tope del avance conservador
constexpr std::uint64_t stall_limit = 10000000;  // eventos seguidos en el mismo instante: error

class Cells {
public:
    Cells(const Params& p, const Room& room, std::size_t agents)
        : x0_(-1.0), y0_(-(room.exit_distance + 1.0)) {
        const double width = p.side + 2.0;
        const double height = p.side + room.exit_distance + 2.0;
        const double min_size = 2.0 * p.radius_max;
        columns_ = std::max(1, static_cast<int>(width / min_size));
        rows_ = std::max(1, static_cast<int>(height / min_size));
        size_ = std::max(width / columns_, height / rows_);
        members_.resize(static_cast<std::size_t>(columns_ * rows_));
        where_.assign(agents, -1);
    }

    [[nodiscard]] int index_of(const Vec2& x) const noexcept {
        const int c = std::clamp(static_cast<int>(std::floor((x.x - x0_) / size_)), 0, columns_ - 1);
        const int r = std::clamp(static_cast<int>(std::floor((x.y - y0_) / size_)), 0, rows_ - 1);
        return r * columns_ + c;
    }

    void insert(std::uint32_t i, int cell) {
        members_[static_cast<std::size_t>(cell)].push_back(i);
        where_[i] = cell;
    }

    void remove(std::uint32_t i) {
        auto& list = members_[static_cast<std::size_t>(where_[i])];
        list.erase(std::find(list.begin(), list.end(), i));
        where_[i] = -1;
    }

    [[nodiscard]] int cell_of(std::uint32_t i) const noexcept { return where_[i]; }

    template <typename F>
    void for_neighbors(int cell, F&& f) const {
        const int c = cell % columns_;
        const int r = cell / columns_;
        for (int dr = -1; dr <= 1; ++dr) {
            for (int dc = -1; dc <= 1; ++dc) {
                const int cc = c + dc;
                const int rr = r + dr;
                if (cc < 0 || rr < 0 || cc >= columns_ || rr >= rows_) continue;
                for (std::uint32_t j : members_[static_cast<std::size_t>(rr * columns_ + cc)]) f(j);
            }
        }
    }

    // Bordes de la celda que se pueden cruzar (los del borde de la grilla, no).
    struct Bounds {
        double lo_x, hi_x, lo_y, hi_y;
        bool left, right, down, up;
    };

    [[nodiscard]] Bounds bounds(int cell) const noexcept {
        const int c = cell % columns_;
        const int r = cell / columns_;
        return {x0_ + c * size_, x0_ + (c + 1) * size_, y0_ + r * size_, y0_ + (r + 1) * size_,
                c > 0, c + 1 < columns_, r > 0, r + 1 < rows_};
    }

    [[nodiscard]] int neighbor(int cell, int dc, int dr) const noexcept { return cell + dc + dr * columns_; }

    // Próximo cruce de borde de celda en MRU: (tiempo, celda de destino).
    [[nodiscard]] std::pair<double, int> crossing(int cell, const Vec2& x, const Vec2& v) const noexcept {
        const Bounds b = bounds(cell);
        double tx = never;
        int dc = 0;
        if (v.x > 0.0 && b.right) {
            tx = (b.hi_x - x.x) / v.x;
            dc = 1;
        } else if (v.x < 0.0 && b.left) {
            tx = (b.lo_x - x.x) / v.x;
            dc = -1;
        }
        double ty = never;
        int dr = 0;
        if (v.y > 0.0 && b.up) {
            ty = (b.hi_y - x.y) / v.y;
            dr = 1;
        } else if (v.y < 0.0 && b.down) {
            ty = (b.lo_y - x.y) / v.y;
            dr = -1;
        }
        if (tx <= ty) {
            if (tx == never) return {never, cell};
            return {std::max(0.0, tx), neighbor(cell, dc, 0)};
        }
        return {std::max(0.0, ty), neighbor(cell, 0, dr)};
    }

private:
    double x0_;
    double y0_;
    double size_;
    int columns_;
    int rows_;
    std::vector<std::vector<std::uint32_t>> members_;
    std::vector<int> where_;
};

class EventEngine {
public:
    EventEngine(const Params& p, const Room& room, std::vector<Agent>& agents, Writer& writer)
        : p_(p), room_(room), agents_(agents), writer_(writer), cells_(p, room, agents.size()),
          analytic_(p.relaxation == Relaxation::Analytic), cell_version_(agents.size(), 0),
          listed_(agents.size(), false), u_(agents.size()), w_(agents.size()), horizon_(agents.size(), never),
          touched_(agents.size(), false), noise_(agents.size()), rng_(p.seed ^ 0x9e3779b97f4a7c15ull) {}

    Summary run() {
        for (std::uint32_t i = 0; i < agents_.size(); ++i) {
            Agent& a = agents_[i];
            a.mode = Mode::EventDriven;
            a.since = 0.0;
            u_[i] = a.velocity;
            w_[i] = {};
            if (!a.active) continue;
            cells_.insert(i, cells_.index_of(a.position));
            ++active_;
            if (!a.relaxed) set_trajectory(i, a.velocity);
        }
        for (std::uint32_t i = 0; i < agents_.size(); ++i) {
            if (agents_[i].active) predict(i);
        }
        if (!analytic_) push({p_.kick, Kind::Kick, none, none, 0, 0, 0});
        if (p_.output_dt > 0.0) {
            write_frame();
            push({p_.output_dt, Kind::Output, none, none, 0, 0, 1});
        }
        const auto start = std::chrono::steady_clock::now();
        std::uint64_t stalled = 0;
        while (active_ > 0 && !heap_.empty()) {
            std::pop_heap(heap_.begin(), heap_.end(), Later{});
            const Event e = heap_.back();
            heap_.pop_back();
            if (e.time >= p_.t_max) {
                now_ = p_.t_max;
                break;
            }
            if (e.time - last_exit_ > p_.clog_time) {
                now_ = last_exit_ + p_.clog_time;
                summary_.clogged = true;
                break;
            }
            if (!valid(e)) continue;
            stalled = e.time == now_ ? stalled + 1 : 0;
            if (stalled > stall_limit) {
                throw std::runtime_error("EDMD: " + std::to_string(stall_limit) +
                                         " eventos sin que avance el tiempo, en t = " + std::to_string(now_) + " s");
            }
            now_ = e.time;
            ++summary_.events;
            handle(e);
            if (p_.progress > 0.0 && now_ >= next_report_) {
                report_progress(now_, active_, summary_.events, 0,
                                std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count());
                next_report_ += p_.progress;
            }
            if (heap_.size() > 64 * static_cast<std::size_t>(active_ + 1024)) compact();
        }
        summary_.wall_seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
        summary_.end_time = now_;
        summary_.remaining = active_;
        return summary_;
    }

private:
    // ------------------------------------------------------------- trayectorias
    [[nodiscard]] bool curved(std::uint32_t i) const noexcept { return w_[i].x != 0.0 || w_[i].y != 0.0; }

    [[nodiscard]] Vec2 position(std::uint32_t i, double t) const noexcept {
        const Agent& a = agents_[i];
        const double s = t - a.since;
        if (!curved(i)) return a.position + s * u_[i];
        return a.position + s * u_[i] + (p_.tau * -std::expm1(-s / p_.tau)) * w_[i];
    }

    [[nodiscard]] Vec2 velocity(std::uint32_t i, double t) const noexcept {
        if (!curved(i)) return u_[i];
        return u_[i] + std::exp(-(t - agents_[i].since) / p_.tau) * w_[i];
    }

    // Cota de la rapidez en lo que resta del tramo: |u| + |w| (w decae).
    [[nodiscard]] double speed_bound(std::uint32_t i) const noexcept { return norm(u_[i]) + norm(w_[i]); }

    // Lleva la referencia de la trayectoria a now_ sin cambiarla.
    void advance(std::uint32_t i) {
        Agent& a = agents_[i];
        const double s = now_ - a.since;
        const Vec2 x = position(i, now_);
        if (curved(i)) w_[i] = std::exp(-s / p_.tau) * w_[i];
        a.position = x;
        a.velocity = velocity(i, now_);
        a.since = now_;
    }

    // Nueva trayectoria desde now_ con velocidad v (el agente ya está avanzado).
    void set_trajectory(std::uint32_t i, const Vec2& v) {
        Agent& a = agents_[i];
        a.velocity = v;
        const Vec2 desired = p_.desired_speed * room_.desired_direction(a.position, a.outside);
        horizon_[i] = never;
        if (!analytic_) {
            u_[i] = v;
            w_[i] = {};
            if (norm(v - desired) > p_.relax_tolerance * p_.desired_speed) list_unrelaxed(i);
            return;
        }
        u_[i] = desired;
        w_[i] = v - desired;
        if (norm(w_[i]) <= p_.relax_tolerance * p_.desired_speed) {
            // Relajado: recta con la velocidad que tiene, sin redondearla a v_d e. Después
            // de un choque suave el redondeo puede deshacer el rebote, y el mismo choque se
            // repetiría en el mismo instante para siempre.
            u_[i] = v;
            w_[i] = {};
            a.relaxed = true;
            return;
        }
        a.relaxed = false;
        // Fin de la relajación: |w| e^{-s/tau} = tol v_d.
        const double relax = now_ + p_.tau * std::log(norm(w_[i]) / (p_.relax_tolerance * p_.desired_speed));
        // Reapuntado: primer instante en que la dirección al target se aparta de la congelada.
        const Vec2 frozen = (1.0 / p_.desired_speed) * desired;
        auto drift = [&](double t) {
            const Vec2 e = room_.desired_direction(position(i, t), a.outside);
            return std::abs(std::atan2(frozen.x * e.y - frozen.y * e.x, dot(frozen, e)));
        };
        double aim = never;
        const double step = 0.05 * p_.tau;
        for (double t0 = now_; t0 < relax; t0 += step) {
            const double t1 = std::min(relax, t0 + step);
            if (drift(t1) > p_.aim_tolerance) {
                double lo = t0;
                double hi = t1;
                for (int k = 0; k < 40; ++k) {
                    const double mid = 0.5 * (lo + hi);
                    (drift(mid) > p_.aim_tolerance ? hi : lo) = mid;
                }
                aim = hi;
                break;
            }
        }
        if (aim < relax) {
            horizon_[i] = aim;
            push({aim, Kind::Aim, i, none, a.version, 0, 0});
        } else {
            horizon_[i] = relax;
            push({relax, Kind::Relax, i, none, a.version, 0, 0});
        }
    }

    // Primer instante en [now_, horizon] en que g llega a 0 decreciendo. `eval(t)` da
    // (g, dg/dt) y `curvature` acota |d2g/dt2| en el tramo. Avance conservador de
    // segundo orden: g(t + h) >= g + g' h - curvature h^2 / 2, así que el paso
    // h = (g' + sqrt(g'^2 + 2 curvature g)) / curvature no saltea la raíz, y es largo
    // cuando las superficies se separan aunque estén casi en contacto.
    template <typename E>
    [[nodiscard]] double conservative(double horizon, double curvature, E&& eval) const {
        double t = now_;
        for (int k = 0; k < max_iterations && t <= horizon; ++k) {
            const auto [g, rate] = eval(t);
            if (g <= tolerance && rate < 0.0) return t;
            const double value = std::max(g, 0.0);
            double h;
            if (curvature > 0.0) {
                h = (rate + std::sqrt(rate * rate + 2.0 * curvature * value)) / curvature;
            } else if (rate < 0.0) {
                h = value / -rate;
            } else {
                return never;
            }
            t += std::max(h, crawl);
        }
        return never;
    }

    [[nodiscard]] double decay(std::uint32_t i) const noexcept { return norm(w_[i]) / p_.tau; }

    [[nodiscard]] double pair_time(std::uint32_t i, std::uint32_t j) const {
        const double sigma = agents_[i].radius + agents_[j].radius;
        if (!curved(i) && !curved(j)) {
            const double t = contact_time(position(j, now_) - position(i, now_), u_[j] - u_[i], sigma);
            return t < never ? now_ + t : never;
        }
        const double speed = speed_bound(i) + speed_bound(j);
        // d'' <= |dv|^2 / d + |da|, con d >= sigma / 2 mientras no haya contacto.
        const double curvature = decay(i) + decay(j) + speed * speed / (0.5 * sigma);
        return conservative(std::min(horizon_[i], horizon_[j]), curvature, [&](double t) {
            const Vec2 dx = position(i, t) - position(j, t);
            const double d = norm(dx);
            return std::pair{d - sigma, dot(dx, velocity(i, t) - velocity(j, t)) / d};
        });
    }

    [[nodiscard]] double wall_time(std::uint32_t i, int w) const {
        const Segment& wall = room_.walls[static_cast<std::size_t>(w)];
        const double r = agents_[i].radius;
        if (!curved(i)) {
            const double t = segment_contact_time(agents_[i].position, u_[i], r, wall);
            return t < never ? now_ + t : never;
        }
        const double speed = speed_bound(i);
        return conservative(horizon_[i], decay(i) + speed * speed / (0.5 * r), [&](double t) {
            const Vec2 x = position(i, t);
            const Vec2 dx = x - closest_point(wall, x);
            const double d = norm(dx);
            return std::pair{d - r, dot(dx, velocity(i, t)) / d};
        });
    }

    // ------------------------------------------------------------- cola
    void push(const Event& e) {
        heap_.push_back(e);
        std::push_heap(heap_.begin(), heap_.end(), Later{});
    }

    // Descarta los eventos inválidos acumulados (invalidación perezosa, como en el TP3).
    void compact() {
        std::erase_if(heap_, [&](const Event& e) { return !valid(e); });
        std::make_heap(heap_.begin(), heap_.end(), Later{});
    }

    [[nodiscard]] bool valid(const Event& e) const noexcept {
        switch (e.kind) {
            case Kind::Output:
            case Kind::Kick: return true;
            case Kind::Pair:
                return agents_[e.i].active && agents_[e.j].active && agents_[e.i].version == e.version_i &&
                       agents_[e.j].version == e.version_j;
            case Kind::Cell:
                return agents_[e.i].active && agents_[e.i].version == e.version_i && cell_version_[e.i] == e.version_j;
            default: return agents_[e.i].active && agents_[e.i].version == e.version_i;
        }
    }

    void list_unrelaxed(std::uint32_t i) {
        agents_[i].relaxed = false;
        if (!listed_[i]) {
            listed_[i] = true;
            unrelaxed_.push_back(i);
        }
    }

    // Todos los eventos futuros del agente i, ya avanzado a now_.
    void predict(std::uint32_t i) {
        const Agent& a = agents_[i];
        cells_.for_neighbors(cells_.cell_of(i), [&](std::uint32_t j) {
            if (j == i) return;
            const double t = pair_time(i, j);
            if (t < never) push({t, Kind::Pair, i, j, a.version, agents_[j].version, 0});
        });
        for (int w = 0; w < static_cast<int>(room_.walls.size()); ++w) {
            const double t = wall_time(i, w);
            if (t < never) push({t, Kind::Wall, i, none, a.version, 0, w});
        }
        predict_cell(i);
        predict_door(i);
    }

    void predict_door(std::uint32_t i) {
        const Agent& a = agents_[i];
        double t = never;
        if (!curved(i)) {
            const double s = !a.outside ? descent_time(a.position, u_[i], 0.0)
                                        : capsule_exit_time(a.position, u_[i], room_.door, room_.exit_distance);
            if (s < never) t = now_ + s;
        } else if (!a.outside) {
            t = conservative(horizon_[i], decay(i), [&](double s) {
                return std::pair{position(i, s).y, velocity(i, s).y};
            });
        } else {
            const double speed = speed_bound(i);
            t = conservative(horizon_[i], decay(i) + speed * speed / (0.5 * room_.exit_distance), [&](double s) {
                const Vec2 x = position(i, s);
                const Vec2 dx = x - closest_point(room_.door, x);
                const double d = norm(dx);
                return std::pair{room_.exit_distance - d, -dot(dx, velocity(i, s)) / std::max(d, 1e-12)};
            });
        }
        if (t < never) push({t, a.outside ? Kind::Exit : Kind::Door, i, none, a.version, 0, 0});
    }

    void predict_cell(std::uint32_t i) {
        const Agent& a = agents_[i];
        const int cell = cells_.cell_of(i);
        if (!curved(i)) {
            const auto [t, target] = cells_.crossing(cell, position(i, now_), u_[i]);
            if (t < never) push({now_ + t, Kind::Cell, i, none, a.version, ++cell_version_[i], target});
            return;
        }
        const Cells::Bounds b = cells_.bounds(cell);
        // Distancia al borde más cercano que se puede cruzar, y su derivada.
        auto gap = [&](double t) {
            const Vec2 x = position(i, t);
            const Vec2 v = velocity(i, t);
            std::pair<double, double> best{never, 0.0};
            auto take = [&](bool open, double d, double rate) {
                if (open && d < best.first) best = {d, rate};
            };
            take(b.left, x.x - b.lo_x, v.x);
            take(b.right, b.hi_x - x.x, -v.x);
            take(b.down, x.y - b.lo_y, v.y);
            take(b.up, b.hi_y - x.y, -v.y);
            return best;
        };
        const double t = conservative(horizon_[i], decay(i), gap);
        if (t == never) return;
        // A qué celda pasa: la del borde que alcanza, según hacia dónde va.
        const Vec2 x = position(i, t);
        const Vec2 v = velocity(i, t);
        int target = cell;
        if (b.left && x.x - b.lo_x <= tolerance && v.x < 0.0) target = cells_.neighbor(cell, -1, 0);
        else if (b.right && b.hi_x - x.x <= tolerance && v.x > 0.0) target = cells_.neighbor(cell, 1, 0);
        else if (b.down && x.y - b.lo_y <= tolerance && v.y < 0.0) target = cells_.neighbor(cell, 0, -1);
        else if (b.up && b.hi_y - x.y <= tolerance && v.y > 0.0) target = cells_.neighbor(cell, 0, 1);
        // Si roza un borde sin cruzarlo, se reintenta un instante después.
        push({std::max(t, now_ + crawl), Kind::Cell, i, none, a.version, ++cell_version_[i], target});
    }

    void changed(std::uint32_t i, const Vec2& v) {
        ++agents_[i].version;
        set_trajectory(i, v);
    }

    // ------------------------------------------------------------- eventos
    void handle(const Event& e) {
        switch (e.kind) {
            case Kind::Output: {
                write_frame();
                push({now_ + p_.output_dt, Kind::Output, none, none, 0, 0, e.extra + 1});
                break;
            }
            case Kind::Kick: kick(); break;
            case Kind::Pair: {
                advance(e.i);
                advance(e.j);
                Agent& a = agents_[e.i];
                Agent& b = agents_[e.j];
                Vec2 vi = a.velocity;
                Vec2 vj = b.velocity;
                resolve_pair(p_, a.position, vi, a.mass, b.position, vj, b.mass);
                touched_[e.i] = touched_[e.j] = true;
                changed(e.i, vi);
                changed(e.j, vj);
                predict(e.i);
                predict(e.j);
                break;
            }
            case Kind::Wall: {
                advance(e.i);
                Agent& a = agents_[e.i];
                Vec2 v = a.velocity;
                resolve_wall(p_, a.position, closest_point(room_.walls[static_cast<std::size_t>(e.extra)], a.position), v);
                touched_[e.i] = true;
                changed(e.i, v);
                predict(e.i);
                break;
            }
            case Kind::Cell: {
                // Cambia de celda sin cambiar la trayectoria: los demás eventos siguen valiendo.
                if (e.extra != cells_.cell_of(e.i)) {
                    cells_.remove(e.i);
                    cells_.insert(e.i, e.extra);
                    cells_.for_neighbors(e.extra, [&](std::uint32_t j) {
                        if (j == e.i) return;
                        const double t = pair_time(e.i, j);
                        if (t < never) push({t, Kind::Pair, e.i, j, agents_[e.i].version, agents_[j].version, 0});
                    });
                }
                predict_cell(e.i);
                break;
            }
            case Kind::Door: {
                advance(e.i);
                Agent& a = agents_[e.i];
                a.outside = true;
                // El segundo target cambia la dirección deseada: nueva trayectoria.
                changed(e.i, a.velocity);
                predict(e.i);
                break;
            }
            case Kind::Relax:
            case Kind::Aim: {
                advance(e.i);
                Agent& a = agents_[e.i];
                Vec2 v = a.velocity;
                if (e.kind == Kind::Relax) v = p_.desired_speed * room_.desired_direction(a.position, a.outside);
                changed(e.i, v);
                predict(e.i);
                break;
            }
            case Kind::Exit: {
                Agent& a = agents_[e.i];
                a.active = false;
                ++a.version;
                cells_.remove(e.i);
                --active_;
                ++summary_.exited;
                writer_.exit(now_, e.i);
                last_exit_ = now_;
                break;
            }
        }
    }

    // Patada de relajación: para cada agente sin relajar, v <- v_d e + (v - v_d e) e^{-delta/tau},
    // la solución exacta de la relajación del SFM durante delta con e fija.
    //
    // Con fluctuación (noise > 0), los agentes que chocaron desde la patada anterior
    // reciben además el impulso de la fuerza aleatoria del TSDMD integrada durante
    // delta: a delta, con a de desvío noise v_d / tau por componente, renovada cada
    // noise_time. Es el equivalente de la fluctuación "solo en contacto".
    void kick() {
        const double factor = std::exp(-p_.kick / p_.tau);
        if (p_.noise > 0.0 && now_ >= next_noise_) {
            refresh_noise();
            next_noise_ += p_.noise_time;
        }
        std::vector<std::uint32_t> kicked;
        kicked.swap(unrelaxed_);
        for (std::uint32_t i : kicked) listed_[i] = false;
        std::erase_if(kicked, [&](std::uint32_t i) { return !agents_[i].active || agents_[i].relaxed; });
        for (std::uint32_t i : kicked) {
            Agent& a = agents_[i];
            advance(i);
            const Vec2 desired = p_.desired_speed * room_.desired_direction(a.position, a.outside);
            const Vec2 deviation = a.velocity - desired;
            Vec2 v = desired + factor * deviation;
            if (p_.noise > 0.0 && touched_[i]) {
                v += (p_.noise * p_.desired_speed / p_.tau * p_.kick) * noise_[i];
            }
            touched_[i] = false;
            ++a.version;
            if (norm(v - desired) <= p_.relax_tolerance * p_.desired_speed) {
                v = desired;
                a.relaxed = true;
            }
            u_[i] = v;
            a.velocity = v;
            if (!a.relaxed) {
                listed_[i] = true;
                unrelaxed_.push_back(i);
            }
        }
        // Se predice después de patear a todos, con las velocidades nuevas de los vecinos.
        for (std::uint32_t i : kicked) predict(i);
        push({now_ + p_.kick, Kind::Kick, none, none, 0, 0, 0});
    }

    void refresh_noise() {
        // Box-Muller con la misma conversión a [0, 1) que las condiciones iniciales.
        auto uniform = [&] { return static_cast<double>(rng_() >> 11) * 0x1.0p-53; };
        for (Vec2& f : noise_) {
            const double u = 1.0 - uniform();
            const double radius = std::sqrt(-2.0 * std::log(u));
            const double angle = 2.0 * 3.14159265358979323846 * uniform();
            f = {radius * std::cos(angle), radius * std::sin(angle)};
        }
    }

    void write_frame() {
        positions_.resize(agents_.size());
        velocities_ = agents_;
        for (std::uint32_t i = 0; i < agents_.size(); ++i) {
            positions_[i] = position(i, now_);
            velocities_[i].velocity = velocity(i, now_);
        }
        writer_.frame(now_, velocities_, positions_);
    }

    const Params& p_;
    const Room& room_;
    std::vector<Agent>& agents_;
    Writer& writer_;
    Cells cells_;
    bool analytic_;
    std::vector<std::uint32_t> cell_version_;
    std::vector<Event> heap_;
    std::vector<std::uint32_t> unrelaxed_;
    std::vector<bool> listed_;
    std::vector<Vec2> u_;
    std::vector<Vec2> w_;
    std::vector<double> horizon_;
    std::vector<Vec2> positions_;
    std::vector<Agent> velocities_;
    Summary summary_;
    std::vector<bool> touched_;
    std::vector<Vec2> noise_;
    std::mt19937_64 rng_;
    double now_ = 0.0;
    double last_exit_ = 0.0;
    double next_noise_ = 0.0;
    double next_report_ = 0.0;  // el primer informe sale con el primer evento
    int active_ = 0;
};

}  // namespace

Summary run_event_driven(const Params& p, const Room& room, std::vector<Agent>& agents, Writer& writer) {
    EventEngine engine(p, room, agents, writer);
    return engine.run();
}

}  // namespace tp5
