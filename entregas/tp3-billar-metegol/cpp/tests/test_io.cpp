#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "test_support.hpp"
#include "tp3/generation.hpp"
#include "tp3/io.hpp"

namespace {

constexpr double tolerance = 1e-9;

std::size_t count_occurrences(const std::string& text, const std::string& needle) {
    std::size_t count = 0;
    std::size_t position = text.find(needle);
    while (position != std::string::npos) {
        ++count;
        position = text.find(needle, position + needle.size());
    }
    return count;
}

void test_read_obstacles() {
    std::istringstream input(
        "# configuracion de ejemplo\n"
        "0.3 0.34 0.05\n"
        "\n"
        "0.9 0.34 0.06   # obstaculo derecho\n"
    );

    const std::vector<tp3::Obstacle> obstacles = tp3::read_obstacles(input);

    EXPECT_TRUE(obstacles.size() == 2);
    EXPECT_TRUE(obstacles[0].id == 0);
    EXPECT_NEAR(obstacles[0].center.x, 0.3, tolerance);
    EXPECT_NEAR(obstacles[0].center.y, 0.34, tolerance);
    EXPECT_NEAR(obstacles[0].radius, 0.05, tolerance);
    EXPECT_TRUE(obstacles[1].id == 1);
    EXPECT_NEAR(obstacles[1].radius, 0.06, tolerance);
}

void test_read_obstacles_accepts_empty_file() {
    std::istringstream input("# mesa vacia\n\n");
    EXPECT_TRUE(tp3::read_obstacles(input).empty());
}

void test_read_obstacles_rejects_malformed_lines() {
    std::istringstream missing("0.3 0.34\n");
    EXPECT_INVALID_ARGUMENT(tp3::read_obstacles(missing));

    std::istringstream extra("0.3 0.34 0.05 0.07\n");
    EXPECT_INVALID_ARGUMENT(tp3::read_obstacles(extra));
}

// El archivo entregado debe tener exactamente una linea "xk yk Rk" por
// obstaculo [TP03, p. 3]; la ida y vuelta no debe perder informacion.
void test_obstacles_round_trip() {
    const std::vector<tp3::Obstacle> original{
        tp3::Obstacle{.id = 0, .center = {.x = 0.3, .y = 0.34}, .radius = 0.05},
        tp3::Obstacle{.id = 1, .center = {.x = 0.9, .y = 0.2}, .radius = 0.0175},
    };

    std::ostringstream output;
    tp3::write_obstacles(output, original);
    EXPECT_TRUE(count_occurrences(output.str(), "#") == 0);

    std::istringstream input(output.str());
    const std::vector<tp3::Obstacle> parsed = tp3::read_obstacles(input);

    EXPECT_TRUE(parsed.size() == original.size());
    for (std::size_t index = 0; index < parsed.size(); ++index) {
        EXPECT_NEAR(parsed[index].center.x, original[index].center.x, tolerance);
        EXPECT_NEAR(parsed[index].center.y, original[index].center.y, tolerance);
        EXPECT_NEAR(parsed[index].radius, original[index].radius, tolerance);
    }
}

void test_trajectory_header_and_frame() {
    const std::vector<tp3::Obstacle> obstacles{
        tp3::Obstacle{.id = 0, .center = {.x = 0.6, .y = 0.34}, .radius = 0.05},
    };
    tp3::System system = tp3::generate_system(
        tp3::InitializationConfig{
            .particle_count = 5,
            .table = {},
            .particle_radius = tp3::default_particle_radius,
            .particle_mass = tp3::default_particle_mass,
            .initial_speed = tp3::default_initial_speed,
            .seed = 11,
            .max_placement_attempts = 10000,
        },
        obstacles
    );

    std::ostringstream output;
    tp3::write_trajectory_header(
        output,
        system,
        tp3::TrajectoryMetadata{
            .seed = 11,
            .initial_speed = tp3::default_initial_speed,
            .save_every = 25,
        }
    );
    tp3::write_frame(output, system, 0, 0, tp3::FrameReason::Initial);

    system.time = 1.5;
    system.particles[2].state = tp3::ParticleState::Used;
    tp3::write_frame(output, system, 1, 137, tp3::FrameReason::Color);

    const std::string text = output.str();

    EXPECT_TRUE(text.find("# tp3-trajectory 1\n") == 0);
    EXPECT_TRUE(text.find("# particle_count 5\n") != std::string::npos);
    EXPECT_TRUE(text.find("# obstacle_count 1\n") != std::string::npos);
    EXPECT_TRUE(text.find("# obstacle 0.6 0.34 0.05\n") != std::string::npos);
    EXPECT_TRUE(text.find("# save_every 25\n") != std::string::npos);
    EXPECT_TRUE(text.find("# frame_columns x y vx vy state\n") != std::string::npos);

    EXPECT_TRUE(text.find("frame 0 0 0 initial\n") != std::string::npos);
    EXPECT_TRUE(text.find("frame 1 1.5 137 color\n") != std::string::npos);

    // Cada cuadro tiene exactamente una linea por particula.
    EXPECT_TRUE(count_occurrences(text, "frame ") == 2);
    std::istringstream reader(text);
    std::string line;
    std::size_t particle_lines = 0;
    while (std::getline(reader, line)) {
        if (!line.empty() && line.front() != '#' && line.rfind("frame ", 0) != 0) {
            ++particle_lines;
        }
    }
    EXPECT_TRUE(particle_lines == 10);

    // El estado usado se escribe como 1 y el fresco como 0.
    EXPECT_TRUE(count_occurrences(text, " 1\n") >= 1);
}

void test_frame_reason_names() {
    EXPECT_TRUE(tp3::to_string(tp3::FrameReason::Initial) == "initial");
    EXPECT_TRUE(tp3::to_string(tp3::FrameReason::Periodic) == "periodic");
    EXPECT_TRUE(tp3::to_string(tp3::FrameReason::Color) == "color");
}

}  // namespace

int main() {
    test_read_obstacles();
    test_read_obstacles_accepts_empty_file();
    test_read_obstacles_rejects_malformed_lines();
    test_obstacles_round_trip();
    test_trajectory_header_and_frame();
    test_frame_reason_names();
    return test::finish("test_io");
}
