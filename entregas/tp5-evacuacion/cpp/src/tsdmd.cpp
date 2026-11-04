#include <algorithm>
#include <chrono>
#include <cmath>

#include "tp5/sfm.hpp"
#include "tp5/simulation.hpp"

namespace tp5 {

Summary simulate(const Params& params, std::vector<Agent> agents, Writer& writer) {
    validate(params);
    const Room room(params);
    writer.header(params, agents);
    Summary summary;
    switch (params.scheme) {
        case Scheme::TimeStep: summary = run_time_step(params, room, agents, writer); break;
        case Scheme::EventDriven: summary = run_event_driven(params, room, agents, writer); break;
        case Scheme::Hybrid: summary = run_hybrid(params, room, agents, writer); break;
    }
    writer.footer(summary);
    return summary;
}

Summary run_time_step(const Params& p, const Room& room, std::vector<Agent>& agents, Writer& writer) {
    Summary summary;
    Beeman beeman(p, room);
    std::vector<std::size_t> active;
    for (std::size_t i = 0; i < agents.size(); ++i) {
        if (agents[i].active) active.push_back(i);
        agents[i].mode = Mode::TimeStep;
    }
    const auto output_every = p.output_dt > 0.0 ? static_cast<std::uint64_t>(std::llround(p.output_dt / p.dt)) : 0;
    std::vector<Vec2> positions(agents.size());
    auto write_frame = [&](double t) {
        for (std::size_t i = 0; i < agents.size(); ++i) positions[i] = agents[i].position;
        writer.frame(t, agents, positions);
    };
    if (output_every) write_frame(0.0);

    std::vector<double> before(agents.size());
    const auto start = std::chrono::steady_clock::now();
    std::uint64_t n = 0;
    double next_report = p.progress;
    double last_exit = 0.0;
    while (!active.empty() && static_cast<double>(n) * p.dt < p.t_max) {
        if (static_cast<double>(n) * p.dt - last_exit > p.clog_time) {
            summary.clogged = true;
            break;
        }
        for (std::size_t i : active) before[i] = room.door_distance(agents[i].position);
        beeman.step(agents, active);
        summary.agent_steps += active.size();
        ++n;
        const double t = static_cast<double>(n) * p.dt;
        bool removed = false;
        for (std::size_t i : active) {
            Agent& a = agents[i];
            if (!a.outside && a.position.y < 0.0) {
                a.outside = true;  // cruzó la línea de la puerta: segundo target
            }
            if (!a.outside) continue;
            const double after = room.door_distance(a.position);
            if (after >= room.exit_distance) {
                // Instante de salida interpolado dentro del paso [T05, p. 21].
                const double fraction = std::clamp((room.exit_distance - before[i]) / (after - before[i]), 0.0, 1.0);
                writer.exit(t - p.dt + fraction * p.dt, i);
                last_exit = t;
                a.active = false;
                ++summary.exited;
                removed = true;
            }
        }
        if (removed) {
            std::erase_if(active, [&](std::size_t i) { return !agents[i].active; });
        }
        if (output_every && n % output_every == 0) write_frame(t);
        if (p.progress > 0.0 && t >= next_report) {
            report_progress(t, static_cast<int>(active.size()), 0, n,
                            std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count());
            next_report += p.progress;
        }
    }
    summary.wall_seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
    summary.steps = n;
    summary.end_time = static_cast<double>(n) * p.dt;
    summary.remaining = static_cast<int>(active.size());
    return summary;
}

}  // namespace tp5
