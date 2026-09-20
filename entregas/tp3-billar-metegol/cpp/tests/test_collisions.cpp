#include "tp3/collisions.hpp"

#include <cmath>

#include "tp3/geometry.hpp"
#include "tp3/model.hpp"
#include "test_support.hpp"

namespace {

using tp3::no_collision;
using tp3::Obstacle;
using tp3::Particle;
using tp3::Table;
using tp3::Vec2;
using tp3::WallKind;

constexpr double tolerance = 1e-12;

[[nodiscard]] Particle make_particle(
    const Vec2& position,
    const Vec2& velocity,
    double radius = tp3::default_particle_radius,
    double mass = tp3::default_particle_mass
) {
    return Particle{
        .id = 0,
        .position = position,
        .velocity = velocity,
        .radius = radius,
        .mass = mass,
        .state = tp3::ParticleState::Fresh,
        .collision_count = 0,
    };
}

// --- Prediccion contra paredes ---------------------------------------------

void test_short_wall_hits_goal() {
    const Table table{};
    const double radius = tp3::default_particle_radius;

    // Desde el centro de la mesa hacia +x: el contacto conserva y = W/2, que
    // esta dentro del arco por construccion.
    const Particle particle = make_particle(
        Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
        Vec2{.x = 1.0, .y = 0.0}
    );

    const auto prediction = tp3::predict_wall_collision(table, particle);

    EXPECT_TRUE(prediction.kind == WallKind::Short);
    EXPECT_NEAR(
        prediction.time,
        table.length - radius - 0.5 * table.length,
        tolerance
    );
    EXPECT_TRUE(prediction.on_goal);
}

void test_short_wall_outside_goal() {
    const Table table{};
    const double radius = tp3::default_particle_radius;

    // Rasante al borde inferior: y se mantiene fuera del arco [0.24, 0.44].
    const Particle particle = make_particle(
        Vec2{.x = 0.5 * table.length, .y = 0.05},
        Vec2{.x = -1.0, .y = 0.0}
    );

    const auto prediction = tp3::predict_wall_collision(table, particle);

    EXPECT_TRUE(prediction.kind == WallKind::Short);
    EXPECT_NEAR(prediction.time, 0.5 * table.length - radius, tolerance);
    EXPECT_FALSE(prediction.on_goal);
}

void test_goal_depends_on_contact_not_on_start() {
    const Table table{};

    // Arranca fuera del arco pero llega a el: lo que decide es el punto de
    // contacto, no la posicion inicial.
    const Particle particle = make_particle(
        Vec2{.x = 0.5 * table.length, .y = 0.10},
        Vec2{.x = -1.0, .y = 0.4}
    );

    const auto prediction = tp3::predict_wall_collision(table, particle);
    const double contact_y = particle.position.y
        + particle.velocity.y * prediction.time;

    EXPECT_TRUE(prediction.kind == WallKind::Short);
    EXPECT_TRUE(tp3::is_on_goal(table, contact_y));
    EXPECT_TRUE(prediction.on_goal);
}

void test_long_wall_never_scores() {
    const Table table{};
    const double radius = tp3::default_particle_radius;

    const Particle particle = make_particle(
        Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
        Vec2{.x = 0.0, .y = 1.0}
    );

    const auto prediction = tp3::predict_wall_collision(table, particle);

    EXPECT_TRUE(prediction.kind == WallKind::Long);
    EXPECT_NEAR(
        prediction.time,
        table.width - radius - 0.5 * table.width,
        tolerance
    );
    EXPECT_FALSE(prediction.on_goal);
}

void test_particle_at_rest_never_hits_a_wall() {
    const Table table{};
    const Particle particle = make_particle(
        Vec2{.x = 0.5 * table.length, .y = 0.5 * table.width},
        Vec2{}
    );

    EXPECT_TRUE(tp3::predict_wall_collision(table, particle).time
                == no_collision);
}

void test_corner_hit_reports_short_wall_first() {
    const Table table{};
    const double radius = tp3::default_particle_radius;

    // Se elige la velocidad para que ambos contactos ocurran a la vez.
    const Vec2 start{.x = 0.5 * table.length, .y = 0.5 * table.width};
    const double to_short = table.length - radius - start.x;
    const double to_long = table.width - radius - start.y;
    const Particle particle = make_particle(
        start,
        Vec2{.x = to_short, .y = to_long}
    );

    const auto prediction = tp3::predict_wall_collision(table, particle);

    EXPECT_TRUE(prediction.kind == WallKind::Short);
    EXPECT_NEAR(prediction.time, 1.0, tolerance);
}

// --- Prediccion entre discos ------------------------------------------------

void test_head_on_disc_collision() {
    // Se acercan a razon de 2 m/s y deben cerrar 1 - 0.2 = 0.8 m.
    const double time = tp3::predict_disc_collision(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.0}, 0.1,
        Vec2{.x = 1.0, .y = 0.0}, Vec2{.x = -1.0, .y = 0.0}, 0.1
    );

    EXPECT_NEAR(time, 0.4, tolerance);
}

void test_receding_discs_never_collide() {
    const double time = tp3::predict_disc_collision(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = -1.0, .y = 0.0}, 0.1,
        Vec2{.x = 1.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.0}, 0.1
    );

    EXPECT_TRUE(time == no_collision);
}

void test_parallel_discs_never_collide() {
    const double time = tp3::predict_disc_collision(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.0}, 0.1,
        Vec2{.x = 0.0, .y = 1.0}, Vec2{.x = 1.0, .y = 0.0}, 0.1
    );

    EXPECT_TRUE(time == no_collision);
}

void test_discs_that_pass_by_never_collide() {
    // Se aproximan, pero el parametro de impacto supera sigma = 0.2.
    const double time = tp3::predict_disc_collision(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.0}, 0.1,
        Vec2{.x = 1.0, .y = 0.5}, Vec2{.x = -1.0, .y = 0.0}, 0.1
    );

    EXPECT_TRUE(time == no_collision);
}

void test_discs_in_contact_and_separating() {
    // Situacion inmediatamente posterior a un choque: no debe volver a
    // predecirse el mismo evento.
    const double time = tp3::predict_disc_collision(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = -1.0, .y = 0.0}, 0.1,
        Vec2{.x = 0.2, .y = 0.0}, Vec2{.x = 1.0, .y = 0.0}, 0.1
    );

    EXPECT_TRUE(time == no_collision);
}

void test_obstacle_is_a_disc_at_rest() {
    const Particle particle = make_particle(
        Vec2{.x = 0.0, .y = 0.0},
        Vec2{.x = 1.0, .y = 0.0},
        0.05
    );
    const Obstacle obstacle{
        .id = 0,
        .center = {.x = 1.0, .y = 0.0},
        .radius = 0.2,
    };

    EXPECT_NEAR(
        tp3::predict_obstacle_collision(particle, obstacle),
        1.0 - 0.25,
        tolerance
    );
}

// --- Resolucion -------------------------------------------------------------

void test_wall_reflection_flips_one_component() {
    const Vec2 velocity{.x = 1.0, .y = 2.0};

    const Vec2 off_short = tp3::resolve_wall_collision(velocity, WallKind::Short);
    EXPECT_NEAR(off_short.x, -1.0, tolerance);
    EXPECT_NEAR(off_short.y, 2.0, tolerance);

    const Vec2 off_long = tp3::resolve_wall_collision(velocity, WallKind::Long);
    EXPECT_NEAR(off_long.x, 1.0, tolerance);
    EXPECT_NEAR(off_long.y, -2.0, tolerance);
}

void test_equal_masses_head_on_exchange_velocities() {
    const Particle first = make_particle(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.0}, 0.1, 1.0
    );
    const Particle second = make_particle(
        Vec2{.x = 0.2, .y = 0.0}, Vec2{.x = -1.0, .y = 0.0}, 0.1, 1.0
    );

    const auto after = tp3::resolve_particle_collision(first, second);

    EXPECT_NEAR(after.first.x, -1.0, tolerance);
    EXPECT_NEAR(after.first.y, 0.0, tolerance);
    EXPECT_NEAR(after.second.x, 1.0, tolerance);
    EXPECT_NEAR(after.second.y, 0.0, tolerance);
}

void test_oblique_collision_conserves_momentum_and_energy() {
    // Centros a distancia exacta sigma = 0.2: 0.12^2 + 0.16^2 = 0.2^2.
    const Particle first = make_particle(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.5}, 0.1, 1.0
    );
    const Particle second = make_particle(
        Vec2{.x = 0.12, .y = 0.16}, Vec2{.x = -0.3, .y = 0.2}, 0.1, 3.0
    );

    const auto after = tp3::resolve_particle_collision(first, second);

    const Vec2 momentum_before = first.mass * first.velocity
        + second.mass * second.velocity;
    const Vec2 momentum_after = first.mass * after.first
        + second.mass * after.second;
    EXPECT_NEAR(momentum_after.x, momentum_before.x, 1e-12);
    EXPECT_NEAR(momentum_after.y, momentum_before.y, 1e-12);

    const double energy_before = 0.5 * first.mass * tp3::norm_squared(first.velocity)
        + 0.5 * second.mass * tp3::norm_squared(second.velocity);
    const double energy_after = 0.5 * first.mass * tp3::norm_squared(after.first)
        + 0.5 * second.mass * tp3::norm_squared(after.second);
    EXPECT_NEAR(energy_after, energy_before, 1e-12);
}

void test_collision_is_reciprocal() {
    // Resolver el par en el orden opuesto debe dar el mismo resultado.
    Particle first = make_particle(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.5}, 0.1, 1.0
    );
    Particle second = make_particle(
        Vec2{.x = 0.12, .y = 0.16}, Vec2{.x = -0.3, .y = 0.2}, 0.1, 3.0
    );

    const auto direct = tp3::resolve_particle_collision(first, second);
    const auto swapped = tp3::resolve_particle_collision(second, first);

    EXPECT_NEAR(swapped.second.x, direct.first.x, tolerance);
    EXPECT_NEAR(swapped.second.y, direct.first.y, tolerance);
    EXPECT_NEAR(swapped.first.x, direct.second.x, tolerance);
    EXPECT_NEAR(swapped.first.y, direct.second.y, tolerance);
}

void test_normal_incidence_on_obstacle_reverses_velocity() {
    const Obstacle obstacle{
        .id = 0,
        .center = {.x = 0.25, .y = 0.0},
        .radius = 0.2,
    };
    const Particle particle = make_particle(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.0}, 0.05
    );

    const Vec2 after = tp3::resolve_obstacle_collision(particle, obstacle);

    EXPECT_NEAR(after.x, -1.0, tolerance);
    EXPECT_NEAR(after.y, 0.0, tolerance);
}

void test_obstacle_preserves_speed_and_tangential_component() {
    // Contacto sobre la diagonal: sigma = 0.25 y el centro del obstaculo queda
    // a (0.25/sqrt(2), 0.25/sqrt(2)) de la particula.
    const double offset = 0.25 / std::sqrt(2.0);
    const Obstacle obstacle{
        .id = 0,
        .center = {.x = offset, .y = offset},
        .radius = 0.2,
    };
    const Particle particle = make_particle(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.0}, 0.05
    );

    const Vec2 after = tp3::resolve_obstacle_collision(particle, obstacle);

    // La reflexion especular sobre una normal a 45 grados intercambia las
    // componentes y les cambia el signo.
    EXPECT_NEAR(after.x, 0.0, 1e-12);
    EXPECT_NEAR(after.y, -1.0, 1e-12);
    EXPECT_NEAR(tp3::norm(after), tp3::norm(particle.velocity), 1e-12);
}

void test_obstacle_mass_does_not_matter() {
    const Obstacle obstacle{
        .id = 0,
        .center = {.x = 0.25, .y = 0.1},
        .radius = 0.2,
    };
    Particle light = make_particle(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.3}, 0.05, 0.001
    );
    Particle heavy = light;
    heavy.mass = 1000.0;

    const Vec2 after_light = tp3::resolve_obstacle_collision(light, obstacle);
    const Vec2 after_heavy = tp3::resolve_obstacle_collision(heavy, obstacle);

    EXPECT_NEAR(after_light.x, after_heavy.x, tolerance);
    EXPECT_NEAR(after_light.y, after_heavy.y, tolerance);
}

void test_obstacle_matches_infinite_mass_limit() {
    // El obstaculo debe coincidir con una particula muy pesada y quieta.
    const Particle particle = make_particle(
        Vec2{.x = 0.0, .y = 0.0}, Vec2{.x = 1.0, .y = 0.3}, 0.05, 0.025
    );
    const Obstacle obstacle{
        .id = 0,
        .center = {.x = 0.2, .y = 0.15},
        .radius = 0.2,
    };
    const Particle heavy = make_particle(
        obstacle.center, Vec2{}, obstacle.radius, 1e12
    );

    const Vec2 from_obstacle = tp3::resolve_obstacle_collision(particle, obstacle);
    const auto from_pair = tp3::resolve_particle_collision(particle, heavy);

    EXPECT_NEAR(from_obstacle.x, from_pair.first.x, 1e-9);
    EXPECT_NEAR(from_obstacle.y, from_pair.first.y, 1e-9);
}

}  // namespace

int main() {
    test_short_wall_hits_goal();
    test_short_wall_outside_goal();
    test_goal_depends_on_contact_not_on_start();
    test_long_wall_never_scores();
    test_particle_at_rest_never_hits_a_wall();
    test_corner_hit_reports_short_wall_first();

    test_head_on_disc_collision();
    test_receding_discs_never_collide();
    test_parallel_discs_never_collide();
    test_discs_that_pass_by_never_collide();
    test_discs_in_contact_and_separating();
    test_obstacle_is_a_disc_at_rest();

    test_wall_reflection_flips_one_component();
    test_equal_masses_head_on_exchange_velocities();
    test_oblique_collision_conserves_momentum_and_energy();
    test_collision_is_reciprocal();
    test_normal_incidence_on_obstacle_reverses_velocity();
    test_obstacle_preserves_speed_and_tangential_component();
    test_obstacle_mass_does_not_matter();
    test_obstacle_matches_infinite_mass_limit();

    return test::finish("test_collisions");
}
