#include <sstream>
#include <string>
#include <vector>

#include "test_support.hpp"
#include "tp4/io.hpp"

namespace {

std::vector<std::string> lines(const std::string& text) {
    std::vector<std::string> result;
    std::istringstream stream(text);
    for (std::string line; std::getline(stream, line);) {
        result.push_back(line);
    }
    return result;
}

void billiard_header_lists_every_parameter() {
    tp4::Billiard b{};
    b.obstacle_x = 0.1;
    std::ostringstream stream;
    tp4::write_billiard_header(stream, b, {.particle_count = 3, .seed = 9, .layout = tp4::Layout::Lattice},
                               {1e-5, 1000, 100});
    const std::string text = stream.str();
    for (const char* expected : {"# particles 3\n", "# seed 9\n", "# layout lattice\n", "# radius 0.51\n",
                                 "# particle_radius 0.0175\n", "# obstacle_x 0.1\n", "# dt 1e-05\n",
                                 "# steps 1000\n", "# output_every 100\n"}) {
        CHECK(text.find(expected) != std::string::npos);
    }
    std::ostringstream empty;
    tp4::write_billiard_header(empty, tp4::Billiard{}, {.particle_count = 3}, {1e-5, 10, 1});
    CHECK(empty.str().find("# obstacle_x none\n") != std::string::npos);
}

void frame_has_one_line_per_particle() {
    const std::vector<tp4::Particle> particles{
        {{0.1, -0.2}, {0.5, 0.25}, tp4::Color::Fresh},
        {{-0.3, 0.4}, {-1.0, 0.0}, tp4::Color::Used},
    };
    std::ostringstream stream;
    tp4::write_frame(stream, 200, 0.002, particles);
    const auto written = lines(stream.str());
    CHECK(written.size() == 3);
    CHECK(written[0] == "frame 200 0.002");
    CHECK(written[1] == "0.1 -0.2 0.5 0.25 0");
    CHECK(written[2] == "-0.3 0.4 -1 0 1");
}

void oscillator_sample_keeps_full_precision() {
    std::ostringstream stream;
    tp4::write_sample(stream, {3, 0.003, 0.1 + 0.2, -1.0 / 3.0});
    CHECK(stream.str() == "3 0.003 0.30000000000000004 -0.3333333333333333\n");
}

}  // namespace

int main() {
    billiard_header_lists_every_parameter();
    frame_has_one_line_per_particle();
    oscillator_sample_keeps_full_precision();
    return test::finish("io");
}
