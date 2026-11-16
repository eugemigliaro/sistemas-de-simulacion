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
//
// Con relaxation = analytic, un agente EDMD no necesita estar relajado: sigue la
// trayectoria exacta del término de deseo, x(t) = x0 + u s + tau w (1 - e^{-s/tau}),
// con u = v_d e (e congelada) y w = v0 - u, como en el EDMD puro. Tiene eventos de fin
// de relajación y de reapuntado, y sus contactos posibles se buscan con avance
// conservador. Así un TSDMD vuelve a EDMD apenas queda aislado, sin esperar a
// relajarse con el SFM.

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

enum class Kind : std::uint8_t { Exit, Door, Alert, Relax, Aim };

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
constexpr double tolerance = 1e-9;      // brecha a la que se da por alcanzado un contacto [m]
constexpr double crawl = 1e-6;          // paso mínimo del avance conservador [s]
constexpr int max_iterations = 200000;  // tope del avance conservador

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
          u_(agents.size()), w_(agents.size()), horizon_(agents.size(), never),
          analytic_(p.relaxation == Relaxation::Analytic), t_out_(p.t_out_factor * p.t_star) {}

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
            count_isolated_unrelaxed();
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
        if (!event_driven(e.i) || agents_[e.i].version != e.version_i) return false;  // incluye Relax y Aim
        if (e.kind == Kind::Alert && e.j != none) {
            return event_driven(e.j) && agents_[e.j].version == e.version_j;
        }
        return true;
    }

    // ------------------------------------------------------------- trayectorias EDMD
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

    // Cota de la rapidez desde t: |u| + |w| e^{-s/tau} (el desvío solo decae).
    [[nodiscard]] double speed_bound(std::uint32_t i, double t) const noexcept {
        if (!curved(i)) return norm(u_[i]);
        return norm(u_[i]) + std::exp(-(t - agents_[i].since) / p_.tau) * norm(w_[i]);
    }

    [[nodiscard]] double decay(std::uint32_t i) const noexcept { return norm(w_[i]) / p_.tau; }

    // Primer instante en [from, horizon] en que g llega a 0 decreciendo (avance conservador
    // de segundo orden, como en el EDMD puro): g(t + h) >= g + g' h - curvature h^2 / 2.
    template <typename E>
    [[nodiscard]] double conservative(double from, double horizon, double curvature, E&& eval) const {
        double t = from;
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

    // Primer contacto entre dos agentes EDMD desde `from` (instante absoluto, o never).
    [[nodiscard]] double pair_contact(std::uint32_t i, std::uint32_t j, double from) const {
        const double sigma = agents_[i].radius + agents_[j].radius;
        if (!curved(i) && !curved(j)) {
            const double t = contact_time(position(j, from) - position(i, from), u_[j] - u_[i], sigma);
            return t < never ? from + t : never;
        }
        const double speed = speed_bound(i, from) + speed_bound(j, from);
        const double curvature = decay(i) + decay(j) + speed * speed / (0.5 * sigma);
        return conservative(from, std::min(horizon_[i], horizon_[j]), curvature, [&](double t) {
            const Vec2 dx = position(i, t) - position(j, t);
            const double d = norm(dx);
            return std::pair{d - sigma, dot(dx, velocity(i, t) - velocity(j, t)) / d};
        });
    }

    // Primer contacto de un agente EDMD con alguna pared desde `from` (instante absoluto).
    [[nodiscard]] double wall_contact(std::uint32_t i, double from) const {
        const double r = agents_[i].radius;
        if (!curved(i)) {
            const double t = wall_time(position(i, from), u_[i], r);
            return t < never ? from + t : never;
        }
        const double speed = speed_bound(i, from);
        double best = never;
        for (const Segment& wall : room_.walls) {
            best = std::min(best, conservative(from, horizon_[i], decay(i) + speed * speed / (0.5 * r), [&](double t) {
                const Vec2 x = position(i, t);
                const Vec2 dx = x - closest_point(wall, x);
                const double d = norm(dx);
                return std::pair{d - r, dot(dx, velocity(i, t)) / d};
            }));
        }
        return best;
    }

    // Cruce de la puerta (adentro) o retiro (afuera) de un agente EDMD desde `from`.
    [[nodiscard]] double door_contact(std::uint32_t i, double from) const {
        const Agent& a = agents_[i];
        if (!curved(i)) {
            const double s = !a.outside ? descent_time(position(i, from), u_[i], 0.0)
                                        : capsule_exit_time(position(i, from), u_[i], room_.door, room_.exit_distance);
            return s < never ? from + s : never;
        }
        if (!a.outside) {
            return conservative(from, horizon_[i], decay(i), [&](double s) {
                return std::pair{position(i, s).y, velocity(i, s).y};
            });
        }
        const double speed = speed_bound(i, from);
        return conservative(from, horizon_[i], decay(i) + speed * speed / (0.5 * room_.exit_distance), [&](double s) {
            const Vec2 x = position(i, s);
            const Vec2 dx = x - closest_point(room_.door, x);
            const double d = norm(dx);
            return std::pair{room_.exit_distance - d, -dot(dx, velocity(i, s)) / std::max(d, 1e-12)};
        });
    }

    // Nueva trayectoria EDMD desde `time` con velocidad v (posición ya en a.position).
    // Sin relajación analítica: recta con v. Con ella: u = v_d e, w = v - u, y un evento
    // de fin de relajación o de reapuntado (el que llegue antes) que la renueva.
    void set_trajectory(std::uint32_t i, double time, const Vec2& v) {
        const Kind kind = prepare(i, time, v);
        if (horizon_[i] < never) push({horizon_[i], kind, i, none, agents_[i].version, 0});
    }

    // Arma la trayectoria (u, w, horizonte) sin agendar nada; devuelve qué evento la cierra.
    Kind prepare(std::uint32_t i, double time, const Vec2& v) {
        Agent& a = agents_[i];
        a.since = time;
        a.velocity = v;
        horizon_[i] = never;
        w_[i] = {};
        u_[i] = v;
        if (!analytic_) return Kind::Relax;
        const Vec2 desired = p_.desired_speed * room_.desired_direction(a.position, a.outside);
        const Vec2 deviation = v - desired;
        if (norm(deviation) <= p_.relax_tolerance * p_.desired_speed) return Kind::Relax;  // relajado: recta con v
        u_[i] = desired;
        w_[i] = deviation;
        const double relax = time + p_.tau * std::log(norm(deviation) / (p_.relax_tolerance * p_.desired_speed));
        const Vec2 frozen = (1.0 / p_.desired_speed) * desired;
        auto drift = [&](double t) {
            const Vec2 e = room_.desired_direction(position(i, t), a.outside);
            return std::abs(std::atan2(frozen.x * e.y - frozen.y * e.x, dot(frozen, e)));
        };
        double aim = never;
        const double step = 0.05 * p_.tau;
        for (double t0 = time; t0 < relax; t0 += step) {
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
        horizon_[i] = std::min(aim, relax);
        return aim < relax ? Kind::Aim : Kind::Relax;
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
        for (std::uint32_t j = 0; j < agents_.size(); ++j) {
            if (j == i || !event_driven(j)) continue;
            const double t = pair_contact(i, j, time);
            if (t < never) push({std::max(time, t - p_.t_star), Kind::Alert, i, j, a.version, agents_[j].version});
        }
        const double tw = wall_contact(i, time);
        if (tw < never) push({std::max(time, tw - p_.t_star), Kind::Alert, i, none, a.version, 0});
        schedule_check(i, time);
        const double t = door_contact(i, time);
        if (t < never) push({t, a.outside ? Kind::Exit : Kind::Door, i, none, a.version, 0});
    }

    // Solo en instantes de la grilla (time == grid_time_). Si el primer contacto posible
    // con un TSDMD está a menos de T*, pasa a TSDMD en este mismo instante; si no, se
    // revisa de nuevo en el último paso que deja al menos T* de margen.
    void schedule_check(std::uint32_t i, double time) {
        const double s = bound_time(i, position(i, time), speed_bound(i, time), time);
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
                const Vec2 v = velocity(e.i, now_);
                a.position = position(e.i, now_);
                a.since = now_;
                a.outside = true;
                const Vec2 desired = p_.desired_speed * room_.desired_direction(a.position, true);
                if (analytic_) {
                    // El segundo target le cambia la dirección: nueva trayectoria analítica.
                    ++a.version;
                    set_trajectory(e.i, now_, v);
                    schedule(e.i, now_);
                } else if (norm(v - desired) > p_.relax_tolerance * p_.desired_speed) {
                    mark_pending(e.i);  // el segundo target le cambia la dirección: que relaje el SFM
                } else {
                    const double t = door_contact(e.i, now_);
                    if (t < never) push({t, Kind::Exit, e.i, none, a.version, 0});
                }
                break;
            }
            case Kind::Relax:
            case Kind::Aim: {
                Vec2 v = velocity(e.i, now_);
                a.position = position(e.i, now_);
                if (e.kind == Kind::Relax) v = p_.desired_speed * room_.desired_direction(a.position, a.outside);
                ++a.version;
                set_trajectory(e.i, now_, v);
                schedule(e.i, now_);
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
        const double s = time - a.since;
        a.velocity = velocity(i, time);
        a.position = position(i, time);
        a.since = time;
        a.mode = Mode::TimeStep;
        // Sin contactos, la fuerza es solo el deseo: a = (u - v)/tau = -w e^{-s/tau}/tau,
        // exacta en t_n y en t_{n-1} (si iba relajado, a = 0).
        a.acceleration = (-std::exp(-s / p_.tau) / p_.tau) * w_[i];
        a.previous_acceleration = (-std::exp(-(s - p_.dt) / p_.tau) / p_.tau) * w_[i];
        w_[i] = {};
        horizon_[i] = never;
        ++a.version;
        pending_[i] = false;
        ts_.insert(std::upper_bound(ts_.begin(), ts_.end(), static_cast<std::size_t>(i)), i);
        writer_.mode(time, i, Mode::TimeStep);
        ++summary_.switches;
    }

    void to_event_driven(std::uint32_t i, double time, const Vec2& v) {
        Agent& a = agents_[i];
        a.mode = Mode::EventDriven;
        ++a.version;
        // Sin relajación analítica, v ya viene redondeada a v_d e (salto menor que
        // relax_tolerance v_d); con ella, es la velocidad del agente.
        set_trajectory(i, time, v);
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
                const double gap = norm(position(j, now_) - b.position) - a.radius - b.radius;
                const double s = gap / (speed_bound(j, now_) + p_.speed_bound);
                if (s <= p_.t_star) {
                    to_time_step(j, now_);
                    fresh.push_back(j);
                } else {
                    push_check(j, step_ + later_steps(s));
                }
            }
        }
    }

    // TSDMD sin contactos que pueden volver a EDMD: sin contacto posible en t_out con la
    // trayectoria que seguirían (recta a v_d e; con relajación analítica, la curva desde su
    // velocidad actual). Sin relajación analítica, además tienen que estar relajados. A un
    // agente que no puede volver no se lo revisa hasta que podría: la brecha que le falta
    // no crece más rápido que 2 V_max, y la relajación no termina antes que con tau.
    void return_to_event_driven() {
        const CellGrid& grid = beeman_.forces().grid();
        const double v_max = p_.speed_bound;
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
            const auto id = static_cast<std::uint32_t>(i);
            const Vec2 desired = p_.desired_speed * room_.desired_direction(a.position, a.outside);
            const Vec2 velocity = analytic_ ? a.velocity : desired;
            const Vec2 saved_velocity = a.velocity;
            const double saved_since = a.since;
            prepare(id, now_, velocity);  // trayectoria candidata (un TSDMD no usa estos campos)
            a.velocity = saved_velocity;
            a.since = saved_since;
            const double speed = analytic_ ? speed_bound(id, now_) : p_.desired_speed;
            const double needed = t_out_ * (speed + v_max);  // brecha necesaria contra cada TSDMD
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
            a.since = now_;  // para evaluar la candidata desde ahora
            const bool blocked = wall_contact(id, now_) <= now_ + t_out_ ||
                                 std::any_of(agents_.begin(), agents_.end(), [&](const Agent& b) {
                                     const auto j = static_cast<std::uint32_t>(&b - agents_.data());
                                     return event_driven(j) && pair_contact(id, j, now_) <= now_ + t_out_;
                                 });
            a.since = saved_since;
            if (blocked) {
                wait(0.0);
                continue;
            }
            if (!analytic_) {
                const double deviation = norm(a.velocity - desired);
                if (deviation > p_.relax_tolerance * p_.desired_speed) {
                    wait(p_.tau * std::log(deviation / (p_.relax_tolerance * p_.desired_speed)));
                    continue;
                }
            }
            to_event_driven(id, now_, velocity);
            back.push_back(id);
        }
        if (back.empty()) return;
        std::erase_if(ts_, [&](std::size_t i) { return agents_[i].mode != Mode::TimeStep || !agents_[i].active; });
        for (std::uint32_t i : back) schedule(i, now_);
    }

    // Pasos de agentes TSDMD sin contactos y sin relajar en este paso: lo que podría
    // ahorrar la relajación analítica (cuenta exacta, paso por paso).
    void count_isolated_unrelaxed() {
        for (std::size_t i : ts_) {
            const Agent& a = agents_[i];
            if (!a.active || beeman_.forces().contact_count(i) > 0) continue;
            const Vec2 desired = p_.desired_speed * room_.desired_direction(a.position, a.outside);
            if (norm(a.velocity - desired) > p_.relax_tolerance * p_.desired_speed) ++summary_.isolated_unrelaxed_steps;
        }
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
            u_[i] = agents_[i].velocity;  // todos arrancan rectos y relajados
        }
        for (std::uint32_t i = 0; i < n; ++i) {
            if (event_driven(i)) schedule(i, 0.0);
        }
    }

    void write_frame(double time) {
        positions_.resize(agents_.size());
        snapshot_ = agents_;
        for (std::uint32_t i = 0; i < agents_.size(); ++i) {
            if (agents_[i].mode != Mode::EventDriven) {
                positions_[i] = agents_[i].position;
                continue;
            }
            positions_[i] = position(i, time);
            snapshot_[i].velocity = velocity(i, time);
        }
        writer_.frame(time, snapshot_, positions_);
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
    std::vector<Agent> snapshot_;
    std::vector<Vec2> u_;          // EDMD: velocidad asintótica v_d e de la trayectoria
    std::vector<Vec2> w_;          // EDMD: desvío inicial v0 - u (cero si va recto)
    std::vector<double> horizon_;  // EDMD: hasta cuándo vale la trayectoria (reapuntado o fin de relajación)
    bool analytic_;
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
