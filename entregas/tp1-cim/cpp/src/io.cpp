#include "tp1/io.hpp"

#include <charconv>
#include <cmath>
#include <iomanip>
#include <istream>
#include <limits>
#include <ostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "tp1/geometry.hpp"

namespace tp1 {
namespace {

std::vector<double> parse_numbers(
    const std::string& line,
    std::string_view description
) {
    std::istringstream parser{line};
    std::vector<double> values{};
    double value{};
    while (parser >> value) {
        values.push_back(value);
    }
    if (!parser.eof()) {
        throw std::invalid_argument{
            std::string{"invalid numeric value in "} + std::string{description}
        };
    }
    return values;
}

std::string read_line(
    std::istream& input,
    std::string_view description
) {
    std::string line{};
    if (!std::getline(input, line)) {
        throw std::invalid_argument{
            std::string{"missing "} + std::string{description}
        };
    }
    return line;
}

std::vector<double> read_row(
    std::istream& input,
    std::string_view description
) {
    return parse_numbers(read_line(input, description), description);
}

void require_columns(
    const std::vector<double>& values,
    std::size_t expected,
    std::string_view description
) {
    if (values.size() != expected) {
        throw std::invalid_argument{
            std::string{description} + " has an invalid column count"
        };
    }
}

void require_finite(
    const std::vector<double>& values,
    std::string_view description
) {
    for (double value : values) {
        if (!std::isfinite(value)) {
            throw std::invalid_argument{
                std::string{description} + " contains a non-finite value"
            };
        }
    }
}

void require_end(std::istream& input, std::string_view description) {
    std::string remaining{};
    while (std::getline(input, remaining)) {
        if (remaining.find_first_not_of(" \t\r") != std::string::npos) {
            throw std::invalid_argument{
                std::string{description} + " contains extra rows"
            };
        }
    }
}

std::size_t parse_particle_count(const std::string& line) {
    std::istringstream parser{line};
    std::string token{};
    std::string extra{};
    if (!(parser >> token) || parser >> extra) {
        throw std::invalid_argument{"N must be a positive integer"};
    }

    std::size_t count{};
    const char* begin = token.data();
    const char* end = begin + token.size();
    const auto conversion = std::from_chars(begin, end, count);
    if (conversion.ec != std::errc{} || conversion.ptr != end || count == 0) {
        throw std::invalid_argument{"N must be a positive integer"};
    }
    return count;
}

void require_writable_system(const ParticleSystem& system) {
    if (!is_valid(system.domain) || !std::isfinite(system.time)
        || system.particles.empty()) {
        throw std::invalid_argument{"invalid particle system"};
    }

    for (std::size_t index = 0; index < system.particles.size(); ++index) {
        const Particle& particle = system.particles[index];
        if (!is_valid(particle) || particle.id != index + 1
            || !is_inside_domain(particle, system.domain)) {
            throw std::invalid_argument{"invalid particle system"};
        }
    }
}

}  // namespace

void write_static(std::ostream& output, const ParticleSystem& system) {
    require_writable_system(system);
    output << std::setprecision(std::numeric_limits<double>::max_digits10)
           << system.particles.size() << '\n'
           << system.domain.side << '\n';
    for (const Particle& particle : system.particles) {
        output << particle.radius << ' ' << particle.property << '\n';
    }
    if (!output) {
        throw std::runtime_error{"could not write static data"};
    }
}

void write_dynamic(std::ostream& output, const ParticleSystem& system) {
    require_writable_system(system);
    output << std::setprecision(std::numeric_limits<double>::max_digits10)
           << system.time << '\n';
    for (const Particle& particle : system.particles) {
        output << particle.position.x << ' '
               << particle.position.y << ' '
               << particle.velocity.x << ' '
               << particle.velocity.y << '\n';
    }
    if (!output) {
        throw std::runtime_error{"could not write dynamic data"};
    }
}

void write_neighbors(
    std::ostream& output,
    const NeighborList& neighbors
) {
    if (!is_valid_neighbor_list(neighbors)) {
        throw std::invalid_argument{"invalid neighbor list"};
    }

    for (std::size_t index = 0; index < neighbors.size(); ++index) {
        output << index + 1;
        for (std::size_t neighbor_id : neighbors[index]) {
            output << ',' << neighbor_id;
        }
        output << '\n';
    }
    if (!output) {
        throw std::runtime_error{"could not write neighbor data"};
    }
}

ParticleSystem read_system(
    std::istream& static_input,
    std::istream& dynamic_input,
    BoundaryCondition boundary
) {
    const std::size_t count = parse_particle_count(
        read_line(static_input, "static header N")
    );

    const std::vector<double> side_row = read_row(
        static_input,
        "static header L"
    );
    require_columns(side_row, 1, "static header L");
    require_finite(side_row, "static header L");

    ParticleSystem result{
        .domain = {.side = side_row.front(), .boundary = boundary},
        .time = 0.0,
        .particles = {},
    };
    if (!is_valid(result.domain)) {
        throw std::invalid_argument{"invalid domain in static data"};
    }
    result.particles.reserve(count);

    for (std::size_t index = 0; index < count; ++index) {
        const std::vector<double> static_row = read_row(
            static_input,
            "static particle row"
        );
        require_columns(static_row, 2, "static particle row");
        require_finite(static_row, "static particle row");
        result.particles.push_back(Particle{
            .id = index + 1,
            .position = {},
            .velocity = {},
            .radius = static_row[0],
            .property = static_row[1],
        });
    }
    require_end(static_input, "static input");

    const std::vector<double> time_row = read_row(
        dynamic_input,
        "dynamic time"
    );
    require_columns(time_row, 1, "dynamic time");
    require_finite(time_row, "dynamic time");
    result.time = time_row.front();

    for (std::size_t index = 0; index < count; ++index) {
        const std::vector<double> dynamic_row = read_row(
            dynamic_input,
            "dynamic particle row"
        );
        if (dynamic_row.size() != 2 && dynamic_row.size() != 4) {
            throw std::invalid_argument{
                "dynamic particle row must have two or four columns"
            };
        }
        require_finite(dynamic_row, "dynamic particle row");

        Particle& particle = result.particles[index];
        particle.position = {.x = dynamic_row[0], .y = dynamic_row[1]};
        if (dynamic_row.size() == 4) {
            particle.velocity = {.x = dynamic_row[2], .y = dynamic_row[3]};
        }
        if (!is_valid(particle)
            || !is_inside_domain(particle, result.domain)) {
            throw std::invalid_argument{"invalid particle in input data"};
        }
    }
    require_end(dynamic_input, "dynamic input");

    return result;
}

}  // namespace tp1
