#include "tp3/simulation.hpp"

#include <cmath>
#include <cstddef>
#include <vector>

#include "tp3/generation.hpp"
#include "tp3/geometry.hpp"
#include "tp3/model.hpp"
#include "test_support.hpp"

namespace {

using tp3::EventKind;
using tp3::FrameReason;
using tp3::Obstacle;
using tp3::Particle;
using tp3::ParticleState;
using tp3::SimulationConfig;
using tp3::System;
using tp3::Table;
using tp3::Vec2;

// Margen para comparar posiciones contra las paredes. Las colisiones dejan a
// la particula exactamente sobre el borde salvo redondeo.
constexpr double geometric_slack = 1e-9;

[[nodiscard]] Particle make_particle(
    std::size_t id,
    const Vec2& position,
    const Vec2& velocity
) {
    return Particle{
        .id = id,
        .position = position,
        .velocity = velocity,
        .radius = tp3::default_particle_radius,
        .mass = tp3::default_particle_mass,
        .state = ParticleState::Fresh,
        .collision_count = 0,
    };
}

[[nodiscard]] System make_system(std::vector<Particle> particles) {
    return System{
        .table = Table{},
        .time = 0.0,
        .particles = std::move(particles),
        .obstacles = {},
    };
}

[[nodiscard]] double kinetic_energy(const System& system) {
    double total = 0.0;
    for (const Particle& particle : system.particles) {
        total += 0.5 * particle.mass * tp3::norm_squared(particle.velocity);
    }
    return total;
}

struct Recorder {
    std::vector<FrameReason> reasons{};
    std::vector<double> times{};

    [[nodiscard]] tp3::FrameSink sink() {
        return [this](const System& system, std::uint64_t, FrameReason reason) {
            reasons.push_back(reason);
            times.push_back(system.time);
        };
    }

    [[nodiscard]] std::size_t count(FrameReason reason) const {
        std::size_t total = 0;
        for (const FrameReason recorded : reasons) {
            if (recorded == reason) {
                ++total;
            }
        }
        return total;
    }
};

// --- Avance y busqueda ------------------------------------------------------

void test_advance_moves_in_a_straight_line() {
    System system = make_system({
        make_particle(0, Vec2{.x = 0.10, .y = 0.20}, Vec2{.x = 1.0, .y = -0.5}),
    });

    tp3::advance(system, 0.25);

    EXPECT_NEAR(system.time, 0.25, 1e-15);
    EXPECT_NEAR(system.particles[0].position.x, 0.35, 1e-15);
    EXPECT_NEAR(system.particles[0].position.y, 0.075, 1e-15);
}

void test_empty_system_has_no_events() {
    const System system = make_system({});
    EXPECT_TRUE(tp3::find_next_event(system).kind == EventKind::None);
}

void test_next_event_picks_the_earliest() {
    const Table table{};
    // La primera va derecho a la pared corta; la segunda choca antes contra la
    // pared larga, que le queda mucho mas cerca.
    const System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{.x = 1.0, .y = 0.0}
        ),
        make_particle(
            1,
            Vec2{.x = 0.2, .y = 0.05},
            Vec2{.x = 0.0, .y = -1.0}
        ),
    });

    const tp3::Event event = tp3::find_next_event(system);

    EXPECT_TRUE(event.kind == EventKind::Wall);
    EXPECT_TRUE(event.first == 1);
    EXPECT_TRUE(event.wall == tp3::WallKind::Long);
}

// --- Goles y color ----------------------------------------------------------

void test_first_goal_contact_turns_the_particle_used() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{.x = -1.0, .y = 0.0}
        ),
    });

    Recorder recorder;
    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 0.7, .save_every = 0, .max_events = 0},
        recorder.sink()
    );

    EXPECT_TRUE(system.particles[0].state == ParticleState::Used);
    EXPECT_TRUE(report.processed_events == 1);
    EXPECT_TRUE(recorder.count(FrameReason::Color) == 1);
    // Cuadro inicial, cuadro de color y cuadro final.
    EXPECT_TRUE(report.written_frames == 3);
}

void test_used_particle_does_not_score_again() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{.x = -1.0, .y = 0.0}
        ),
    });

    Recorder recorder;
    // Tiempo suficiente para cruzar la mesa varias veces de arco a arco.
    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 6.0, .save_every = 0, .max_events = 0},
        recorder.sink()
    );

    EXPECT_TRUE(report.processed_events > 3);
    EXPECT_TRUE(recorder.count(FrameReason::Color) == 1);
    EXPECT_TRUE(system.particles[0].state == ParticleState::Used);
}

void test_short_wall_outside_the_goal_does_not_score() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.05},
            Vec2{.x = -1.0, .y = 0.0}
        ),
    });

    Recorder recorder;
    tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 0.7, .save_every = 0, .max_events = 0},
        recorder.sink()
    );

    EXPECT_TRUE(system.particles[0].state == ParticleState::Fresh);
    EXPECT_TRUE(recorder.count(FrameReason::Color) == 0);
}

// --- Terminacion ------------------------------------------------------------

void test_run_stops_exactly_at_max_time() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{.x = 0.6, .y = 0.8}
        ),
    });

    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 3.0, .save_every = 0, .max_events = 0},
        {}
    );

    EXPECT_NEAR(report.final_time, 3.0, 1e-12);
    EXPECT_NEAR(system.time, 3.0, 1e-12);
    EXPECT_TRUE(report.reached_max_time);
    EXPECT_FALSE(report.reached_max_events);
    EXPECT_FALSE(report.exhausted_events);
}

void test_max_events_stops_before_max_time() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{.x = 0.6, .y = 0.8}
        ),
    });

    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 100.0, .save_every = 0, .max_events = 5},
        {}
    );

    EXPECT_TRUE(report.processed_events == 5);
    EXPECT_TRUE(report.reached_max_events);
    EXPECT_FALSE(report.reached_max_time);
    EXPECT_TRUE(system.time < 100.0);
}

void test_particle_at_rest_exhausts_events() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{}
        ),
    });

    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 2.0, .save_every = 0, .max_events = 0},
        {}
    );

    EXPECT_TRUE(report.exhausted_events);
    EXPECT_TRUE(report.processed_events == 0);
    EXPECT_NEAR(system.time, 2.0, 1e-12);
}

void test_periodic_frames_follow_save_every() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.05},
            Vec2{.x = 0.6, .y = 0.8}
        ),
    });

    Recorder recorder;
    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 20.0, .save_every = 4, .max_events = 0},
        recorder.sink()
    );

    EXPECT_TRUE(report.processed_events > 8);
    // Un cuadro periodico por cada 4 eventos, salvo los que quedaron
    // desplazados por un cambio de color.
    const std::size_t expected = report.processed_events / 4;
    EXPECT_TRUE(
        recorder.count(FrameReason::Periodic) + recorder.count(FrameReason::Color)
        >= expected
    );
    EXPECT_TRUE(recorder.reasons.front() == FrameReason::Initial);
    EXPECT_TRUE(recorder.reasons.back() == FrameReason::Final);
}

// --- Geometria del rebote ---------------------------------------------------

void test_corner_hit_reverses_both_components() {
    const Table table{};
    const double radius = tp3::default_particle_radius;
    const Vec2 start{.x = 0.5 * table.length, .y = 0.5 * table.width};
    const Vec2 velocity{
        .x = table.length - radius - start.x,
        .y = table.width - radius - start.y,
    };

    System system = make_system({make_particle(0, start, velocity)});

    // Dos eventos: la pared corta y, en el mismo instante, la larga.
    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 10.0, .save_every = 0, .max_events = 2},
        {}
    );

    EXPECT_TRUE(report.processed_events == 2);
    EXPECT_NEAR(system.time, 1.0, 1e-12);
    EXPECT_NEAR(system.particles[0].velocity.x, -velocity.x, 1e-12);
    EXPECT_NEAR(system.particles[0].velocity.y, -velocity.y, 1e-12);
}

void test_obstacle_sends_the_particle_back() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.2, .y = 0.5 * table.width},
            Vec2{.x = 1.0, .y = 0.0}
        ),
    });
    system.obstacles.push_back(Obstacle{
        .id = 0,
        .center = {.x = 0.6, .y = 0.5 * table.width},
        .radius = 0.05,
    });

    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 0.5, .save_every = 0, .max_events = 1},
        {}
    );

    EXPECT_TRUE(report.processed_events == 1);
    EXPECT_NEAR(system.particles[0].velocity.x, -1.0, 1e-12);
    EXPECT_NEAR(system.particles[0].velocity.y, 0.0, 1e-12);
}

// --- Invariantes sobre una corrida completa ---------------------------------

[[nodiscard]] System generated_system(
    std::size_t count,
    std::uint64_t seed,
    const std::vector<Obstacle>& obstacles
) {
    return tp3::generate_system(
        tp3::InitializationConfig{
            .particle_count = count,
            .table = Table{},
            .particle_radius = tp3::default_particle_radius,
            .particle_mass = tp3::default_particle_mass,
            .initial_speed = tp3::default_initial_speed,
            .seed = seed,
            .max_placement_attempts = 10000,
        },
        obstacles
    );
}

void expect_physical_invariants(const System& system) {
    const double radius = tp3::default_particle_radius;

    for (const Particle& particle : system.particles) {
        EXPECT_TRUE(particle.position.x - radius >= -geometric_slack);
        EXPECT_TRUE(particle.position.x + radius <= system.table.length + geometric_slack);
        EXPECT_TRUE(particle.position.y - radius >= -geometric_slack);
        EXPECT_TRUE(particle.position.y + radius <= system.table.width + geometric_slack);
    }

    for (std::size_t index = 0; index < system.particles.size(); ++index) {
        for (std::size_t other = index + 1; other < system.particles.size(); ++other) {
            const double distance = tp3::norm(
                system.particles[other].position - system.particles[index].position
            );
            EXPECT_TRUE(distance >= 2.0 * radius - geometric_slack);
        }
        for (const Obstacle& obstacle : system.obstacles) {
            const double distance = tp3::norm(
                obstacle.center - system.particles[index].position
            );
            EXPECT_TRUE(distance >= obstacle.radius + radius - geometric_slack);
        }
    }
}

void test_many_particles_keep_energy_and_geometry() {
    System system = generated_system(60, 7, {});
    const double energy_before = kinetic_energy(system);

    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 5.0, .save_every = 0, .max_events = 0},
        {}
    );

    EXPECT_TRUE(report.processed_events > 100);
    EXPECT_NEAR(kinetic_energy(system), energy_before, 1e-9);
    expect_physical_invariants(system);
}

void test_obstacles_keep_energy_and_geometry() {
    const std::vector<Obstacle> obstacles{
        Obstacle{.id = 0, .center = {.x = 0.40, .y = 0.34}, .radius = 0.06},
        Obstacle{.id = 1, .center = {.x = 0.80, .y = 0.20}, .radius = 0.05},
        Obstacle{.id = 2, .center = {.x = 0.80, .y = 0.48}, .radius = 0.05},
    };

    System system = generated_system(40, 11, obstacles);
    const double energy_before = kinetic_energy(system);

    const auto report = tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 5.0, .save_every = 0, .max_events = 0},
        {}
    );

    EXPECT_TRUE(report.processed_events > 100);
    EXPECT_NEAR(kinetic_energy(system), energy_before, 1e-9);
    expect_physical_invariants(system);
}

void test_run_is_deterministic() {
    System first = generated_system(30, 3, {});
    System second = generated_system(30, 3, {});

    const SimulationConfig config{
        .max_time = 4.0, .save_every = 3, .max_events = 0,
    };

    Recorder first_recorder;
    Recorder second_recorder;
    const auto first_report = tp3::simulate_naive(first, config, first_recorder.sink());
    const auto second_report = tp3::simulate_naive(second, config, second_recorder.sink());

    EXPECT_TRUE(first_report.processed_events == second_report.processed_events);
    EXPECT_TRUE(first_report.written_frames == second_report.written_frames);
    EXPECT_TRUE(first == second);
    EXPECT_TRUE(first_recorder.times == second_recorder.times);
}

void test_particles_end_used_when_the_run_is_long_enough() {
    System system = generated_system(30, 5, {});

    Recorder recorder;
    tp3::simulate_naive(
        system,
        SimulationConfig{.max_time = 60.0, .save_every = 0, .max_events = 0},
        recorder.sink()
    );

    std::size_t used = 0;
    for (const Particle& particle : system.particles) {
        if (particle.state == ParticleState::Used) {
            ++used;
        }
    }

    // El conteo de goles es del post-proceso; lo que se verifica aca es que el
    // motor y los cuadros de color cuenten la misma historia.
    EXPECT_TRUE(used > 0);
    EXPECT_TRUE(recorder.count(FrameReason::Color) == used);
}


// --- Motor con cola de prioridad --------------------------------------------

// La cola no puede validarse exigiendo la trayectoria completa del motor
// ingenuo. Ambos son correctos, pero predicen desde estados de referencia
// distintos —el ingenuo recalcula desde el instante actual, la cola conserva lo
// agendado en un instante anterior— y esa diferencia de redondeo del orden de
// 1e-16 crece exponencialmente, porque un gas de discos rigidos es caotico. Lo
// que si debe cumplirse es acuerdo exacto mientras la divergencia sea
// despreciable, y las mismas invariantes fisicas siempre.
void test_queue_matches_naive_while_rounding_is_negligible() {
    System from_naive = generated_system(100, 9, {});
    System from_queue = generated_system(100, 9, {});

    const SimulationConfig config{
        .max_time = 1.0e9, .save_every = 0, .max_events = 100,
    };
    const auto naive_report = tp3::simulate_naive(from_naive, config, {});
    const auto queue_report = tp3::simulate_queue(from_queue, config, {});

    EXPECT_TRUE(naive_report.processed_events == 100);
    EXPECT_TRUE(queue_report.processed_events == 100);
    EXPECT_NEAR(queue_report.final_time, naive_report.final_time, 1e-12);

    for (std::size_t index = 0; index < from_naive.particles.size(); ++index) {
        const Particle& expected = from_naive.particles[index];
        const Particle& actual = from_queue.particles[index];
        EXPECT_NEAR(actual.position.x, expected.position.x, 1e-10);
        EXPECT_NEAR(actual.position.y, expected.position.y, 1e-10);
        EXPECT_NEAR(actual.velocity.x, expected.velocity.x, 1e-10);
        EXPECT_NEAR(actual.velocity.y, expected.velocity.y, 1e-10);
        EXPECT_TRUE(actual.collision_count == expected.collision_count);
    }
}

void test_queue_and_naive_agree_on_the_first_event() {
    // El primer evento se predice desde el mismo estado en los dos motores, sin
    // ninguna acumulacion previa: aca si vale exigir igualdad exacta.
    System from_naive = generated_system(100, 9, {});
    System from_queue = generated_system(100, 9, {});

    const SimulationConfig config{
        .max_time = 1.0e9, .save_every = 0, .max_events = 1,
    };
    tp3::simulate_naive(from_naive, config, {});
    tp3::simulate_queue(from_queue, config, {});

    EXPECT_TRUE(from_naive == from_queue);
}

void test_queue_keeps_energy_and_geometry() {
    System system = generated_system(60, 7, {});
    const double energy_before = kinetic_energy(system);

    const auto report = tp3::simulate_queue(
        system,
        SimulationConfig{.max_time = 20.0, .save_every = 0, .max_events = 0},
        {}
    );

    EXPECT_TRUE(report.processed_events > 1000);
    EXPECT_FALSE(report.exhausted_events);
    EXPECT_NEAR(kinetic_energy(system), energy_before, 1e-9);
    expect_physical_invariants(system);
}

void test_queue_keeps_energy_and_geometry_with_obstacles() {
    const std::vector<Obstacle> obstacles{
        Obstacle{.id = 0, .center = {.x = 0.40, .y = 0.34}, .radius = 0.06},
        Obstacle{.id = 1, .center = {.x = 0.80, .y = 0.20}, .radius = 0.05},
        Obstacle{.id = 2, .center = {.x = 0.80, .y = 0.48}, .radius = 0.05},
    };

    System system = generated_system(60, 11, obstacles);
    const double energy_before = kinetic_energy(system);

    const auto report = tp3::simulate_queue(
        system,
        SimulationConfig{.max_time = 20.0, .save_every = 0, .max_events = 0},
        {}
    );

    EXPECT_TRUE(report.processed_events > 1000);
    EXPECT_NEAR(kinetic_energy(system), energy_before, 1e-9);
    expect_physical_invariants(system);
}

void test_queue_is_deterministic() {
    System first = generated_system(40, 3, {});
    System second = generated_system(40, 3, {});

    const SimulationConfig config{
        .max_time = 10.0, .save_every = 7, .max_events = 0,
    };

    Recorder first_recorder;
    Recorder second_recorder;
    tp3::simulate_queue(first, config, first_recorder.sink());
    tp3::simulate_queue(second, config, second_recorder.sink());

    EXPECT_TRUE(first == second);
    EXPECT_TRUE(first_recorder.times == second_recorder.times);
}

void test_queue_scores_the_same_way() {
    const Table table{};
    System system = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{.x = -1.0, .y = 0.0}
        ),
    });

    Recorder recorder;
    const auto report = tp3::simulate_queue(
        system,
        SimulationConfig{.max_time = 6.0, .save_every = 0, .max_events = 0},
        recorder.sink()
    );

    EXPECT_TRUE(report.processed_events > 3);
    EXPECT_TRUE(system.particles[0].state == ParticleState::Used);
    EXPECT_TRUE(recorder.count(FrameReason::Color) == 1);
}

void test_queue_stops_at_max_time_and_max_events() {
    System stopped_by_time = generated_system(20, 2, {});
    const auto by_time = tp3::simulate_queue(
        stopped_by_time,
        SimulationConfig{.max_time = 3.0, .save_every = 0, .max_events = 0},
        {}
    );
    EXPECT_NEAR(by_time.final_time, 3.0, 1e-12);
    EXPECT_TRUE(by_time.reached_max_time);
    EXPECT_FALSE(by_time.reached_max_events);

    System stopped_by_events = generated_system(20, 2, {});
    const auto by_events = tp3::simulate_queue(
        stopped_by_events,
        SimulationConfig{.max_time = 1000.0, .save_every = 0, .max_events = 5},
        {}
    );
    EXPECT_TRUE(by_events.processed_events == 5);
    EXPECT_TRUE(by_events.reached_max_events);
    EXPECT_FALSE(by_events.reached_max_time);
}

void test_queue_reports_a_system_without_events() {
    // La cola vacia sola no alcanza: los eventos posteriores a max_time nunca
    // se agendan. Solo debe marcarse cuando de verdad no hay choque posible.
    const Table table{};
    System at_rest = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{}
        ),
    });
    const auto resting = tp3::simulate_queue(
        at_rest,
        SimulationConfig{.max_time = 2.0, .save_every = 0, .max_events = 0},
        {}
    );
    EXPECT_TRUE(resting.exhausted_events);
    EXPECT_NEAR(at_rest.time, 2.0, 1e-12);

    // Una particula en movimiento cuyo proximo choque cae despues del horizonte
    // vacia la cola igual, pero eso es un final normal.
    System moving = make_system({
        make_particle(
            0,
            Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
            Vec2{.x = 0.01, .y = 0.0}
        ),
    });
    const auto short_run = tp3::simulate_queue(
        moving,
        SimulationConfig{.max_time = 0.5, .save_every = 0, .max_events = 0},
        {}
    );
    EXPECT_FALSE(short_run.exhausted_events);
    EXPECT_TRUE(short_run.processed_events == 0);
    EXPECT_NEAR(moving.time, 0.5, 1e-12);
}

}  // namespace

int main() {
    test_advance_moves_in_a_straight_line();
    test_empty_system_has_no_events();
    test_next_event_picks_the_earliest();

    test_first_goal_contact_turns_the_particle_used();
    test_used_particle_does_not_score_again();
    test_short_wall_outside_the_goal_does_not_score();

    test_run_stops_exactly_at_max_time();
    test_max_events_stops_before_max_time();
    test_particle_at_rest_exhausts_events();
    test_periodic_frames_follow_save_every();

    test_corner_hit_reverses_both_components();
    test_obstacle_sends_the_particle_back();

    test_many_particles_keep_energy_and_geometry();
    test_obstacles_keep_energy_and_geometry();
    test_run_is_deterministic();
    test_particles_end_used_when_the_run_is_long_enough();

    test_queue_matches_naive_while_rounding_is_negligible();
    test_queue_and_naive_agree_on_the_first_event();
    test_queue_keeps_energy_and_geometry();
    test_queue_keeps_energy_and_geometry_with_obstacles();
    test_queue_is_deterministic();
    test_queue_scores_the_same_way();
    test_queue_stops_at_max_time_and_max_events();
    test_queue_reports_a_system_without_events();

    return test::finish("test_simulation");
}
