#include "tp3/io.hpp"

#include <cstddef>
#include <istream>
#include <ostream>
#include <sstream>
#include <stdexcept>
#include <string>

namespace tp3 {
namespace {

// Nueve cifras significativas alcanzan de sobra para posiciones en metros
// (resolucion del orden del nanometro) y mantienen el archivo compacto.
constexpr int output_precision = 9;

class PrecisionGuard {
public:
    explicit PrecisionGuard(std::ostream& stream)
        : stream_(stream), previous_(stream.precision(output_precision)) {}

    PrecisionGuard(const PrecisionGuard&) = delete;
    PrecisionGuard& operator=(const PrecisionGuard&) = delete;

    ~PrecisionGuard() { stream_.precision(previous_); }

private:
    std::ostream& stream_;
    std::streamsize previous_;
};

}  // namespace

std::vector<Obstacle> read_obstacles(std::istream& stream) {
    std::vector<Obstacle> obstacles;
    std::string line;
    std::size_t line_number = 0;

    while (std::getline(stream, line)) {
        ++line_number;

        const std::size_t comment = line.find('#');
        if (comment != std::string::npos) {
            line.erase(comment);
        }

        std::istringstream fields(line);
        double x = 0.0;
        double y = 0.0;
        double radius = 0.0;
        if (!(fields >> x)) {
            continue;  // linea vacia o solo comentario
        }

        if (!(fields >> y >> radius)) {
            throw std::invalid_argument(
                "linea " + std::to_string(line_number)
                + ": se esperaba el formato \"xk yk Rk\""
            );
        }

        std::string extra;
        if (fields >> extra) {
            throw std::invalid_argument(
                "linea " + std::to_string(line_number)
                + ": sobran campos, se espera \"xk yk Rk\""
            );
        }

        obstacles.push_back(Obstacle{
            .id = obstacles.size(),
            .center = {.x = x, .y = y},
            .radius = radius,
        });
    }

    return obstacles;
}

void write_obstacles(std::ostream& stream, const std::vector<Obstacle>& obstacles) {
    const PrecisionGuard guard(stream);
    for (const Obstacle& obstacle : obstacles) {
        stream << obstacle.center.x << ' '
               << obstacle.center.y << ' '
               << obstacle.radius << '\n';
    }
}

std::string to_string(FrameReason reason) {
    switch (reason) {
        case FrameReason::Initial:
            return "initial";
        case FrameReason::Periodic:
            return "periodic";
        case FrameReason::Color:
            return "color";
        case FrameReason::Final:
            return "final";
    }
    return "unknown";
}

void write_trajectory_header(
    std::ostream& stream,
    const System& system,
    const TrajectoryMetadata& metadata
) {
    const PrecisionGuard guard(stream);

    stream << "# tp3-trajectory 1\n"
           << "# length " << system.table.length << '\n'
           << "# width " << system.table.width << '\n'
           << "# goal_width " << system.table.goal_width << '\n'
           << "# particle_count " << system.particles.size() << '\n';

    if (!system.particles.empty()) {
        const Particle& first = system.particles.front();
        stream << "# particle_radius " << first.radius << '\n'
               << "# particle_mass " << first.mass << '\n';
    }

    stream << "# initial_speed " << metadata.initial_speed << '\n'
           << "# seed " << metadata.seed << '\n'
           << "# save_every " << metadata.save_every << '\n';

    if (metadata.max_time) {
        stream << "# max_time " << *metadata.max_time << '\n';
    }
    if (metadata.max_events) {
        stream << "# max_events " << *metadata.max_events << '\n';
    }

    stream << "# obstacle_count " << system.obstacles.size() << '\n';

    for (const Obstacle& obstacle : system.obstacles) {
        stream << "# obstacle " << obstacle.center.x << ' '
               << obstacle.center.y << ' '
               << obstacle.radius << '\n';
    }

    stream << "# frame_columns x y vx vy state\n";
}

void write_frame(
    std::ostream& stream,
    const System& system,
    std::uint64_t frame_index,
    std::uint64_t processed_events,
    FrameReason reason
) {
    const PrecisionGuard guard(stream);

    stream << "frame " << frame_index << ' ' << system.time << ' '
           << processed_events << ' ' << to_string(reason) << '\n';

    for (const Particle& particle : system.particles) {
        stream << particle.position.x << ' '
               << particle.position.y << ' '
               << particle.velocity.x << ' '
               << particle.velocity.y << ' '
               << (particle.state == ParticleState::Used ? 1 : 0) << '\n';
    }
}

}  // namespace tp3
