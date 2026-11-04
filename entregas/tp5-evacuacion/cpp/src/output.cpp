#include "tp5/output.hpp"

#include <cstdio>
#include <string>

namespace tp5 {
namespace {

// snprintf: formato fijo y rápido, igual en cualquier biblioteca estándar.
template <typename... Args>
void print(std::ostream* out, const char* format, Args... args) {
    char buffer[256];
    const int length = std::snprintf(buffer, sizeof buffer, format, args...);
    out->write(buffer, length);
}

}  // namespace

void report_progress(double time, int inside, std::uint64_t events, std::uint64_t steps, double wall_seconds) {
    std::fprintf(stderr, "tp5: t=%.1f s adentro %d eventos %llu pasos %llu wall %.1f s\n", time, inside,
                 static_cast<unsigned long long>(events), static_cast<unsigned long long>(steps), wall_seconds);
}

void Writer::header(const Params& p, const std::vector<Agent>& agents) {
    if (!out_) return;
    *out_ << "# tp5 problema 2: evacuacion con SFM sin fuerza social\n";
    print(out_, "# scheme %s agents %d side %.17g door %.17g desired_speed %.17g\n", std::string(to_string(p.scheme)).c_str(),
          p.agents, p.side, p.door, p.desired_speed);
    print(out_, "# radius_min %.17g radius_max %.17g mass %.17g mass_by_area %d reference_radius %.17g\n", p.radius_min,
          p.radius_max, p.mass, p.mass_by_area ? 1 : 0, p.reference_radius);
    print(out_, "# tau %.17g kn %.17g kt %.17g noise %.17g noise_time %.17g\n", p.tau, p.kn, p.kt, p.noise, p.noise_time);
    print(out_, "# target_fraction %.17g second_target %s second_target_distance %.17g exit_distance %.17g\n",
          p.target_fraction, std::string(to_string(p.second_target)).c_str(), p.second_target_distance, p.exit_distance);
    print(out_, "# dt %.17g t_star %.17g t_out_factor %.17g speed_bound %.17g relax_check_every %d\n", p.dt, p.t_star,
          p.t_out_factor, p.speed_bound, p.relax_check_every);
    print(out_, "# relaxation %s kick %.17g aim_tolerance %.17g relax_tolerance %.17g\n",
          std::string(to_string(p.relaxation)).c_str(), p.kick, p.aim_tolerance, p.relax_tolerance);
    print(out_, "# t_max %.17g clog_time %.17g output_dt %.17g seed %llu\n", p.t_max, p.clog_time, p.output_dt,
          static_cast<unsigned long long>(p.seed));
    for (std::size_t i = 0; i < agents.size(); ++i) {
        print(out_, "agent %zu %.6f %.6f\n", i, agents[i].radius, agents[i].mass);
    }
}

void Writer::frame(double time, const std::vector<Agent>& agents, const std::vector<Vec2>& positions) {
    if (!out_) return;
    int inside = 0;
    for (const Agent& a : agents) inside += a.active ? 1 : 0;
    print(out_, "frame %.6f %d\n", time, inside);
    for (std::size_t i = 0; i < agents.size(); ++i) {
        const Agent& a = agents[i];
        if (!a.active) continue;
        print(out_, "%zu %.5f %.5f %.4f %.4f %d\n", i, positions[i].x, positions[i].y, a.velocity.x, a.velocity.y,
              static_cast<int>(a.mode));
    }
}

void Writer::exit(double time, std::size_t agent) {
    if (!out_) return;
    print(out_, "exit %.9f %zu\n", time, agent);
}

void Writer::mode(double time, std::size_t agent, Mode mode) {
    if (!out_) return;
    print(out_, "mode %.9f %zu %d\n", time, agent, static_cast<int>(mode));
}

void Writer::footer(const Summary& s) {
    if (!out_) return;
    print(out_, "# end_time %.9f steps %llu events %llu agent_steps %llu switches %llu\n", s.end_time,
          static_cast<unsigned long long>(s.steps), static_cast<unsigned long long>(s.events),
          static_cast<unsigned long long>(s.agent_steps), static_cast<unsigned long long>(s.switches));
    print(out_, "# isolated_unrelaxed_steps %llu clogged %d\n", static_cast<unsigned long long>(s.isolated_unrelaxed_steps),
          s.clogged ? 1 : 0);
    print(out_, "# exited %d remaining %d bound_violations %llu max_speed %.6f wall_seconds %.6f\n", s.exited,
          s.remaining, static_cast<unsigned long long>(s.bound_violations), s.max_speed, s.wall_seconds);
}

}  // namespace tp5
