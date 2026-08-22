#include "tp2/io.hpp"

#include <cmath>
#include <iomanip>
#include <ostream>
#include <stdexcept>

#include "tp2/geometry.hpp"

namespace tp2 {
namespace {

void require_output(std::ostream& output) {
    if (!output) {
        throw std::runtime_error{"output stream is not writable"};
    }
}

}  // namespace

void write_trajectory_header(std::ostream& output) {
    require_output(output);
    output
        << "model,density,particle_count,side,cells_per_side,cutoff,"
        << "speed,time_step,eta,seed,time,id,x,y,vx,vy,angle\n";
}

void write_observations_header(std::ostream& output) {
    require_output(output);
    output
        << "model,density,particle_count,side,cells_per_side,cutoff,"
        << "speed,time_step,eta,seed,time,polarization,"
        << "largest_cluster_fraction,cim_time_ns,neighbor_pairs,"
        << "distance_evaluations\n";
}

void write_trajectory_frame(
    std::ostream& output,
    const RunMetadata& metadata,
    const System& system,
    double speed
) {
    require_output(output);
    if (!is_valid(system) || !std::isfinite(speed) || speed <= 0.0) {
        throw std::invalid_argument{"invalid trajectory frame"};
    }

    output << std::setprecision(17);
    for (const Particle& particle : system.particles) {
        output
            << metadata.model << ','
            << metadata.density << ','
            << metadata.particle_count << ','
            << metadata.side << ','
            << metadata.cells_per_side << ','
            << metadata.cutoff << ','
            << metadata.speed << ','
            << metadata.time_step << ','
            << metadata.eta << ','
            << metadata.seed << ','
            << system.time << ','
            << particle.id << ','
            << particle.position.x << ','
            << particle.position.y << ','
            << speed * std::cos(particle.angle) << ','
            << speed * std::sin(particle.angle) << ','
            << particle.angle << '\n';
    }
    require_output(output);
}

void write_observation(
    std::ostream& output,
    const RunMetadata& metadata,
    const Observation& observation
) {
    require_output(output);
    output << std::setprecision(17)
           << metadata.model << ','
           << metadata.density << ','
           << metadata.particle_count << ','
           << metadata.side << ','
           << metadata.cells_per_side << ','
           << metadata.cutoff << ','
           << metadata.speed << ','
           << metadata.time_step << ','
           << metadata.eta << ','
           << metadata.seed << ','
           << observation.time << ','
           << observation.polarization << ','
           << observation.largest_cluster_fraction << ','
           << observation.cim_time_ns << ','
           << observation.neighbor_pairs << ','
           << observation.distance_evaluations << '\n';
    require_output(output);
}

}  // namespace tp2
