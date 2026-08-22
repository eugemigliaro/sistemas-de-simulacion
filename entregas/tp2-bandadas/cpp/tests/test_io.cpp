#include <algorithm>
#include <sstream>
#include <string>

#include "test_support.hpp"
#include "tp2/runner.hpp"

namespace {

void test_small_run_writes_reproducible_shape() {
    const tp2::RunConfig config{
        .initialization = {
            .particle_count = 4,
            .side = 10.0,
            .seed = 17,
        },
        .dynamics = {
            .model = tp2::AlignmentModel::Vicsek,
            .cutoff = 1.0,
            .speed = 0.03,
            .time_step = 1.0,
            .eta = 0.0,
        },
        .cells_per_side = 9,
        .steps = 2,
        .trajectory_every = 2,
    };
    std::ostringstream trajectory;
    std::ostringstream observations;
    const tp2::RunSummary summary = tp2::run_simulation(
        config,
        observations,
        &trajectory
    );

    EXPECT_TRUE(summary.frames_written == 2);
    EXPECT_TRUE(summary.observations_written == 3);
    EXPECT_TRUE(
        trajectory.str().starts_with(
            "model,density,eta,seed,time,id,x,y,vx,vy,angle\n"
        )
    );
    EXPECT_TRUE(
        observations.str().starts_with(
            "model,density,eta,seed,time,polarization,"
        )
    );

    const std::string trajectory_text = trajectory.str();
    const std::string observations_text = observations.str();
    const std::size_t trajectory_lines = static_cast<std::size_t>(
        std::count(trajectory_text.begin(), trajectory_text.end(), '\n')
    );
    const std::size_t observation_lines = static_cast<std::size_t>(
        std::count(observations_text.begin(), observations_text.end(), '\n')
    );
    EXPECT_TRUE(trajectory_lines == 1 + 2 * 4);
    EXPECT_TRUE(observation_lines == 1 + 3);

    std::ostringstream observations_only;
    const tp2::RunSummary no_trajectory = tp2::run_simulation(
        config,
        observations_only
    );
    EXPECT_TRUE(no_trajectory.frames_written == 0);
    EXPECT_TRUE(no_trajectory.observations_written == 3);
}

}  // namespace

int main() {
    test_small_run_writes_reproducible_shape();
    return test::finish("IO tests");
}
