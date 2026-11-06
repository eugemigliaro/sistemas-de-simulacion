// Esquema híbrido EDMD + TSDMD por agente [TP05, p. 4].
//
// La grilla de dt es el reloj maestro. Un agente EDMD va recto y relajado
// (v = v_d e) y no interactúa: pasa a TSDMD en el paso de la grilla anterior a
// cualquier contacto posible dentro de T*. Contra otros EDMD y contra las paredes
// el contacto se predice exacto; contra los TSDMD, cuyo futuro no se conoce, con
// la cota |v_j| <= V_max. Entre t_n y t_{n+1} se procesan los eventos EDMD en
// orden, después se avanza un dt a los TSDMD (Beeman) y al final se aplican los
// cambios de esquema. Un TSDMD sin contactos y relajado vuelve a EDMD si no hay
// contacto posible en t_out_factor T* (histéresis).

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <vector>

#include "tp5/events.hpp"
#include "tp5/sfm.hpp"
#include "tp5/simulation.hpp"

namespace tp5 {
namespace {

enum class Kind : std::uint8_t { Exit, Door, Alert };

struct Event {
    double time;
    Kind kind;
    std::uint32_t i;
    std::uint32_t j;  // compañero de una alerta entre agentes, o none
    std::uint32_t version_i;
    std::uint32_t version_j;
};

struct Later {
    bool operator()(const Event& a, const Event& b) const noexcept {
        if (a.time != b.time) return a.time > b.time;
        return a.kind > b.kind;
    }
};

constexpr std::uint32_t none = static_cast<std::uint32_t>(-1);

// Revisión de la cota contra los TSDMD: siempre en un instante de la grilla, cuando
// sus posiciones son exactas, y al menos un paso después de la anterior (así no hay
// revisiones cada vez más seguidas que frenen el reloj).
struct Check {
    std::uint64_t step;
    std::uint32_t i;
    std::uint32_t version;
};

struct LaterCheck {
    bool operator()(const Check& a, const Check& b) const noexcept { return a.step > b.step; }
};

class HybridEngine {
public:
    HybridEngine(const Params& p, const Room& room, std::vector<Agent>& agents, Writer& writer)
        : p_(p), room_(room), agents_(agents), writer_(writer), beeman_(p, room), pending_(agents.size(), false),
          next_check_(agents.size(), 0), check_version_(agents.size(), 0), next_candidate_(agents.size(), 0),
          t_out_(p.t_out_factor * p.t_star) {}

    Summary run() {
        initial_modes();
        const auto output_every = p_.output_dt > 0.0 ? static_cast<std::uint64_t>(std::llround(p_.output_dt / p_.dt)) : 0;
        if (output_every) write_frame(0.0);
        std::vector<double> before(agents_.size());
        const auto start = std::chrono::steady_clock::now();
        std::uint64_t n = 0;
        double next_report = p_.progress;
        while (active_ > 0 && static_cast<double>(n) * p_.dt < p_.t_max) {
            if (static_cast<double>(n) * p_.dt - last_exit_ > p_.clog_time) {
                summary_.clogged = true;
                break;
            }
            const double next = static_cast<double>(n + 1) * p_.dt;
            // 1. Eventos EDMD hasta el próximo paso, con los TSDMD todavía en t_n.
            while (!heap_.empty() && heap_.front().time <= next) {
                std::pop_heap(heap_.begin(), heap_.end(), Later{});
                const Event e = heap_.back();
                heap_.pop_back();
                if (!valid(e)) continue;
                now_ = e.time;
                ++summary_.events;
                handle(e);
            }
            // 2. Un paso de Beeman para los TSDMD.
            for (std::size_t i : ts_) before[i] = room_.door_distance(agents_[i].position);
            if (!ts_.empty()) beeman_.step(agents_, ts_);
            summary_.agent_steps += ts_.size();
            ++n;
            grid_time_ = next;
            now_ = next;
            step_ = n;
            ts_exits(before);
            check_speeds();
            // 3. Revisiones de la cota y cambios de esquema en t_{n+1}.
            run_checks();
            apply_pending();
            if (n % static_cast<std::uint64_t>(p_.relax_check_every) == 0) return_to_event_driven();
            if (heap_.size() > 64 * (agents_.size() + 1024)) compact();
            if (output_every && n % output_every == 0) write_frame(next);
            if (p_.progress > 0.0 && next >= next_report) {
                report_progress(next, active_, summary_.events, n,
                                std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count());
                next_report += p_.progress;
            }
        }
        summary_.wall_seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
        summary_.steps = n;
        summary_.end_time = static_cast<double>(n) * p_.dt;
        summary_.remaining = active_;
        return summary_;
    }

private:
    [[nodiscard]] bool event_driven(std::size_t i) const noexcept {
        return agents_[i].active && agents_[i].mode == Mode::EventDriven;
    }

    void push(const Event& e) {
        heap_.push_back(e);
        std::push_heap(heap_.begin(), heap_.end(), Later{});
    }

    void compact() {
        std::erase_if(heap_, [&](const Event& e) { return !valid(e); });
        std::make_heap(heap_.begin(), heap_.end(), Later{});
        std::erase_if(checks_, [&](const Check& c) {
            return !event_driven(c.i) || agents_[c.i].version != c.version || c.step != next_check_[c.i];
        });
        std::make_heap(checks_.begin(), checks_.end(), LaterCheck{});
    }

    // Una sola revisión pendiente por agente: la más temprana (las demás quedan inválidas).
    void push_check(std::uint32_t i, std::uint64_t step) {
        if (next_check_[i] <= step && next_check_[i] > step_ && check_version_[i] == agents_[i].version) return;
        next_check_[i] = step;
        check_version_[i] = agents_[i].version;
        checks_.push_back({step, i, agents_[i].version});
        std::push_heap(checks_.begin(), checks_.end(), LaterCheck{});
    }

    void run_checks() {
        while (!checks_.empty() && checks_.front().step <= step_) {
            std::pop_heap(checks_.begin(), checks_.end(), LaterCheck{});
            const Check c = checks_.back();
            checks_.pop_back();
            if (!event_driven(c.i) || agents_[c.i].version != c.version || pending_[c.i] ||
                c.step != next_check_[c.i]) {
                continue;
            }
            next_check_[c.i] = 0;
            schedule_check(c.i, now_);
        }
    }

    [[nodiscard]] bool valid(const Event& e) const noexcept {
        if (!event_driven(e.i) || agents_[e.i].version != e.version_i) return false;
        if (e.kind == Kind::Alert && e.j != none) {
            return event_driven(e.j) && agents_[e.j].version == e.version_j;
        }
        return true;
    }

    // Primer contacto posible contra los TSDMD, medido desde `time`, para un agente en
    // `x` que se mueve a `speed`: brecha / (speed + V_max). Los TSDMD están en
    // grid_time_ y pueden haberse acercado V_max (time - grid_time_) desde entonces.
    [[nodiscard]] double bound_time(std::size_t i, const Vec2& x, double speed, double time) const noexcept {
        const double v = p_.speed_bound;
        const double elapsed = time - grid_time_;
        double best = never;
        for (std::size_t j : ts_) {
            if (j == i || !agents_[j].active) continue;
            const double gap = norm(x - agents_[j].position) - agents_[i].radius - agents_[j].radius - v * elapsed;
            if (gap <= 0.0) return 0.0;
            best = std::min(best, gap / (speed + v));
        }
        return best;
    }

    [[nodiscard]] double wall_time(const Vec2& x, const Vec2& v, double radius) const noexcept {
        double best = never;
        for (const Segment& wall : room_.walls) best = std::min(best, segment_contact_time(x, v, radius, wall));
        return best;
    }

    // Eventos de un agente EDMD desde `time`: alertas T* antes de cada contacto
    // posible, revisión de la cota contra los TSDMD, y cruce de la puerta o retiro.
    void schedule(std::uint32_t i, double time) {
        const Agent& a = agents_[i];
        const Vec2 x = a.position_at(time);
        for (std::uint32_t j = 0; j < agents_.size(); ++j) {
            if (j == i || !event_driven(j)) continue;
            const Agent& b = agents_[j];
            const double t = contact_time(b.position_at(time) - x, b.velocity - a.velocity, a.radius + b.radius);
            if (t < never) push({time + std::max(0.0, t - p_.t_star), Kind::Alert, i, j, a.version, b.version});
        }
        const double tw = wall_time(x, a.velocity, a.radius);
        if (tw < never) push({time + std::max(0.0, tw - p_.t_star), Kind::Alert, i, none, a.version, 0});
        schedule_check(i, time);
        if (!a.outside) {
            const double t = descent_time(x, a.velocity, 0.0);
            if (t < never) push({time + t, Kind::Door, i, none, a.version, 0});
        } else {
            const double t = capsule_exit_time(x, a.velocity, room_.door, room_.exit_distance);
            if (t < never) push({time + t, Kind::Exit, i, none, a.version, 0});
        }
    }

    // Solo en instantes de la grilla (time == grid_time_). Si el primer contacto posible
    // con un TSDMD está a menos de T*, pasa a TSDMD en este mismo instante; si no, se
    // revisa de nuevo en el último paso que deja al menos T* de margen.
    void schedule_check(std::uint32_t i, double time) {
        const Agent& a = agents_[i];
        const double s = bound_time(i, a.position_at(time), norm(a.velocity), time);
        if (s <= p_.t_star) {
            mark_pending(i);
        } else if (s < never) {
            push_check(i, step_ + later_steps(s));
        }
    }

    [[nodiscard]] std::uint64_t later_steps(double s) const noexcept {
        const double steps = std::floor((s - p_.t_star) / p_.dt);
        return steps < 1.0 ? 1 : (steps > 1e15 ? static_cast<std::uint64_t>(1e15) : static_cast<std::uint64_t>(steps));
    }

    void handle(const Event& e) {
        Agent& a = agents_[e.i];
        switch (e.kind) {
            case Kind::Alert:
                mark_pending(e.i);
                if (e.j != none) mark_pending(e.j);
                break;
            case Kind::Door: {
                a.position = a.position_at(now_);
                a.since = now_;
                a.outside = true;
                const Vec2 desired = p_.desired_speed * room_.desired_direction(a.position, true);
                if (norm(a.velocity - desired) > p_.relax_tolerance * p_.desired_speed) {
                    mark_pending(e.i);  // el segundo target le cambia la dirección: que relaje el SFM
                } else {
                    const double t = capsule_exit_time(a.position, a.velocity, room_.door, room_.exit_distance);
                    if (t < never) push({now_ + t, Kind::Exit, e.i, none, a.version, 0});
                }
                break;
            }
            case Kind::Exit:
                a.active = false;
                ++a.version;
                --active_;
                ++summary_.exited;
                writer_.exit(now_, e.i);
                last_exit_ = now_;
                break;
        }
    }

    void mark_pending(std::uint32_t i) {
        if (!pending_[i]) {
            pending_[i] = true;
            pending_list_.push_back(i);
        }
    }

    void to_time_step(std::uint32_t i, double time) {
        Agent& a = agents_[i];
        a.position = a.position_at(time);
        a.since = time;
        a.mode = Mode::TimeStep;
        // Relajado y sin contactos: la fuerza del SFM es nula, así que a = 0 es exacto.
        a.acceleration = {};
        a.previous_acceleration = {};
        ++a.version;
        pending_[i] = false;
        ts_.insert(std::upper_bound(ts_.begin(), ts_.end(), static_cast<std::size_t>(i)), i);
        writer_.mode(time, i, Mode::TimeStep);
        ++summary_.switches;
    }

    void to_event_driven(std::uint32_t i, double time, const Vec2& velocity) {
        Agent& a = agents_[i];
        a.velocity = velocity;  // redondeo a v_d e: salto menor que relax_tolerance v_d
        a.since = time;
        a.mode = Mode::EventDriven;
        ++a.version;
        writer_.mode(time, i, Mode::EventDriven);
        ++summary_.switches;
    }

    // Pasa a TSDMD a los que tienen alerta y, en cascada, a los EDMD que quedan a
    // menos de T* de un contacto posible con alguno de ellos.
    void apply_pending() {
        if (pending_list_.empty()) return;
        std::sort(pending_list_.begin(), pending_list_.end());
        pending_list_.erase(std::unique(pending_list_.begin(), pending_list_.end()), pending_list_.end());
        std::vector<std::uint32_t> fresh;
        for (std::uint32_t i : pending_list_) {
            if (pending_[i] && event_driven(i)) {
                to_time_step(i, now_);
                fresh.push_back(i);
            }
            pending_[i] = false;
        }
        pending_list_.clear();
        for (std::size_t k = 0; k < fresh.size(); ++k) {
            const Agent& b = agents_[fresh[k]];
            for (std::uint32_t j = 0; j < agents_.size(); ++j) {
                if (!event_driven(j)) continue;
                const Agent& a = agents_[j];
                const double gap = norm(a.position_at(now_) - b.position) - a.radius - b.radius;
                const double s = gap / (norm(a.velocity) + p_.speed_bound);
                if (s <= p_.t_star) {
                    to_time_step(j, now_);
                    fresh.push_back(j);
                } else {
                    push_check(j, step_ + later_steps(s));
                }
            }
        }
    }

    // TSDMD sin contactos y relajados que pueden volver a EDMD: sin contacto posible en
    // t_out con trayectoria recta a v_d e. Cuenta también los aislados sin relajar. A un
    // agente que no puede volver no se lo revisa hasta que podría: la brecha que le falta
    // no crece más rápido que 2 V_max, y la relajación no termina antes que con tau.
    void return_to_event_driven() {
        const CellGrid& grid = beeman_.forces().grid();
        const double v_max = p_.speed_bound;
        const double speed = p_.desired_speed;
        const double needed = t_out_ * (speed + v_max);  // brecha necesaria contra cada TSDMD
        std::vector<std::uint32_t> back;
        for (std::size_t i : ts_) {
            Agent& a = agents_[i];
            if (!a.active || step_ < next_candidate_[i]) continue;
            auto wait = [&](double seconds) {
                const double steps = std::ceil(std::max(seconds, 0.0) / p_.dt);
                next_candidate_[i] = step_ + std::max<std::uint64_t>(static_cast<std::uint64_t>(p_.relax_check_every),
                                                                     static_cast<std::uint64_t>(std::min(steps, 1e12)));
            };
            if (beeman_.forces().contact_count(i) > 0) {
                wait(0.0);
                continue;
            }
            const Vec2 velocity = speed * room_.desired_direction(a.position, a.outside);
            // Descarte rápido con las celdas: algún TSDMD vecino demasiado cerca.
            double nearest = never;
            const int cell = grid.cell_index(a.position);
            const int column = cell % grid.columns();
            const int row = cell / grid.columns();
            for (int dr = -2; dr <= 2; ++dr) {
                for (int dc = -2; dc <= 2; ++dc) {
                    const int c = column + dc;
                    const int r = row + dr;
                    if (c < 0 || r < 0 || c >= grid.columns() || r >= grid.rows()) continue;
                    for (int j = grid.head(r * grid.columns() + c); j >= 0; j = grid.next(static_cast<std::size_t>(j))) {
                        const auto jj = static_cast<std::size_t>(j);
                        if (jj == i || !agents_[jj].active || agents_[jj].mode != Mode::TimeStep) continue;
                        nearest = std::min(nearest, norm(a.position - agents_[jj].position) - a.radius - agents_[jj].radius);
                    }
                }
            }
            if (nearest <= needed) {
                wait((needed - nearest) / (2.0 * v_max));
                continue;
            }
            const double bound = bound_time(i, a.position, speed, now_);
            if (bound <= t_out_) {
                wait((t_out_ - bound) * (speed + v_max) / (2.0 * v_max));
                continue;
            }
            if (wall_time(a.position, velocity, a.radius) <= t_out_) {
                wait(0.0);
                continue;
            }
            bool clear = true;
            for (std::uint32_t j = 0; j < agents_.size() && clear; ++j) {
                if (!event_driven(j)) continue;
                const Agent& b = agents_[j];
                clear = contact_time(b.position_at(now_) - a.position, b.velocity - velocity, a.radius + b.radius) > t_out_;
            }
            if (!clear) {
                wait(0.0);
                continue;
            }
            const double deviation = norm(a.velocity - velocity);
            if (deviation > p_.relax_tolerance * p_.desired_speed) {
                const std::uint64_t before = step_;
                wait(p_.tau * std::log(deviation / (p_.relax_tolerance * p_.desired_speed)));
                summary_.isolated_unrelaxed_steps += next_candidate_[i] - before;
                continue;
            }
            to_event_driven(static_cast<std::uint32_t>(i), now_, velocity);
            back.push_back(static_cast<std::uint32_t>(i));
        }
        if (back.empty()) return;
        std::erase_if(ts_, [&](std::size_t i) { return agents_[i].mode != Mode::TimeStep || !agents_[i].active; });
        for (std::uint32_t i : back) schedule(i, now_);
    }

    void ts_exits(const std::vector<double>& before) {
        bool removed = false;
        for (std::size_t i : ts_) {
            Agent& a = agents_[i];
            if (!a.outside && a.position.y < 0.0) a.outside = true;
            if (!a.outside) continue;
            const double after = room_.door_distance(a.position);
            if (after >= room_.exit_distance) {
                const double fraction = std::clamp((room_.exit_distance - before[i]) / (after - before[i]), 0.0, 1.0);
                writer_.exit(now_ - p_.dt + fraction * p_.dt, i);
                last_exit_ = now_;
                a.active = false;
                ++a.version;
                --active_;
                ++summary_.exited;
                removed = true;
            }
        }
        if (removed) std::erase_if(ts_, [&](std::size_t i) { return !agents_[i].active; });
    }

    // La cota V_max sostiene la garantía de no perder contactos: se verifica en cada
    // paso y, si se viola, se revisa de inmediato a todos los EDMD.
    void check_speeds() {
        double fastest = 0.0;
        for (std::size_t i : ts_) fastest = std::max(fastest, norm_squared(agents_[i].velocity));
        fastest = std::sqrt(fastest);
        summary_.max_speed = std::max(summary_.max_speed, fastest);
        if (fastest <= p_.speed_bound) return;
        ++summary_.bound_violations;
        for (std::uint32_t j = 0; j < agents_.size(); ++j) {
            if (event_driven(j)) push_check(j, step_);
        }
    }

    // t = 0: todos van rectos y relajados. TSDMD los que tienen un contacto posible en
    // t_out (exacto, como si todos fueran EDMD) y, en cascada, los que quedan cerca de ellos.
    void initial_modes() {
        const std::size_t n = agents_.size();
        for (std::uint32_t i = 0; i < n; ++i) {
            Agent& a = agents_[i];
            a.mode = Mode::EventDriven;
            a.since = 0.0;
            a.acceleration = {};
            a.previous_acceleration = {};
            if (a.active) ++active_;
        }
        std::vector<bool> time_step(n, false);
        for (std::uint32_t i = 0; i < n; ++i) {
            const Agent& a = agents_[i];
            if (!a.active) continue;
            if (wall_time(a.position, a.velocity, a.radius) <= t_out_) time_step[i] = true;
            for (std::uint32_t j = i + 1; j < n; ++j) {
                const Agent& b = agents_[j];
                if (!b.active) continue;
                if (contact_time(b.position - a.position, b.velocity - a.velocity, a.radius + b.radius) <= t_out_) {
                    time_step[i] = true;
                    time_step[j] = true;
                }
            }
        }
        for (bool changed = true; changed;) {
            changed = false;
            for (std::uint32_t i = 0; i < n; ++i) {
                if (!agents_[i].active || time_step[i]) continue;
                for (std::uint32_t j = 0; j < n; ++j) {
                    if (!time_step[j] || !agents_[j].active) continue;
                    const double gap = norm(agents_[i].position - agents_[j].position) - agents_[i].radius - agents_[j].radius;
                    if (gap / (norm(agents_[i].velocity) + p_.speed_bound) <= t_out_) {
                        time_step[i] = true;
                        changed = true;
                        break;
                    }
                }
            }
        }
        for (std::uint32_t i = 0; i < n; ++i) {
            if (!agents_[i].active) continue;
            if (time_step[i]) {
                agents_[i].mode = Mode::TimeStep;
                ts_.push_back(i);
            }
            writer_.mode(0.0, i, agents_[i].mode);
        }
        for (std::uint32_t i = 0; i < n; ++i) {
            if (event_driven(i)) schedule(i, 0.0);
        }
    }

    void write_frame(double time) {
        positions_.resize(agents_.size());
        for (std::size_t i = 0; i < agents_.size(); ++i) {
            positions_[i] = agents_[i].mode == Mode::EventDriven ? agents_[i].position_at(time) : agents_[i].position;
        }
        writer_.frame(time, agents_, positions_);
    }

    const Params& p_;
    const Room& room_;
    std::vector<Agent>& agents_;
    Writer& writer_;
    Beeman beeman_;
    std::vector<std::size_t> ts_;
    std::vector<bool> pending_;
    std::vector<Event> heap_;
    std::vector<Check> checks_;
    std::vector<std::uint32_t> pending_list_;
    std::vector<std::uint64_t> next_check_;
    std::vector<std::uint32_t> check_version_;
    std::vector<std::uint64_t> next_candidate_;
    std::vector<Vec2> positions_;
    Summary summary_;
    std::uint64_t step_ = 0;
    double last_exit_ = 0.0;
    double t_out_;
    double now_ = 0.0;
    double grid_time_ = 0.0;
    int active_ = 0;
};

}  // namespace

Summary run_hybrid(const Params& p, const Room& room, std::vector<Agent>& agents, Writer& writer) {
    HybridEngine engine(p, room, agents, writer);
    return engine.run();
}

}  // namespace tp5
