#include "tp3/simulation.hpp"

#include <cstddef>
#include <queue>
#include <vector>

#include "tp3/geometry.hpp"

namespace tp3 {
namespace {

void consider(Event& best, const Event& candidate) noexcept {
    if (candidate.kind != EventKind::None && candidate.time < best.time) {
        best = candidate;
    }
}

}  // namespace

void advance(System& system, double interval) noexcept {
    if (!(interval > 0.0)) {
        return;
    }
    for (Particle& particle : system.particles) {
        particle.position = particle.position + interval * particle.velocity;
    }
    system.time += interval;
}

Event find_next_event(const System& system) noexcept {
    Event best{};
    const std::size_t count = system.particles.size();
    // Las predicciones son relativas al estado actual; el evento se agenda en
    // tiempo absoluto. Sumar infinito deja infinito, asi que los candidatos
    // sin choque futuro siguen perdiendo la comparacion.
    const double now = system.time;

    for (std::size_t index = 0; index < count; ++index) {
        const Particle& particle = system.particles[index];

        const WallPrediction wall = predict_wall_collision(system.table, particle);
        consider(best, Event{
            .time = now + wall.time,
            .kind = EventKind::Wall,
            .first = index,
            .second = 0,
            .wall = wall.kind,
            .on_goal = wall.on_goal,
            .first_collisions = particle.collision_count,
            .second_collisions = 0,
        });

        for (std::size_t other = 0; other < system.obstacles.size(); ++other) {
            consider(best, Event{
                .time = now + predict_obstacle_collision(
                    particle, system.obstacles[other]
                ),
                .kind = EventKind::Obstacle,
                .first = index,
                .second = other,
                .wall = WallKind::Short,
                .on_goal = false,
                .first_collisions = particle.collision_count,
                .second_collisions = 0,
            });
        }

        for (std::size_t other = index + 1; other < count; ++other) {
            consider(best, Event{
                .time = now + predict_particle_collision(
                    particle, system.particles[other]
                ),
                .kind = EventKind::ParticlePair,
                .first = index,
                .second = other,
                .wall = WallKind::Short,
                .on_goal = false,
                .first_collisions = particle.collision_count,
                .second_collisions = system.particles[other].collision_count,
            });
        }
    }

    return best;
}

bool apply_event(System& system, const Event& event) noexcept {
    switch (event.kind) {
        case EventKind::Wall: {
            Particle& particle = system.particles[event.first];
            particle.velocity = resolve_wall_collision(
                particle.velocity, event.wall
            );
            ++particle.collision_count;

            // Solo el primer contacto con el arco cambia el color. Una
            // particula usada sigue chocando normalmente [TP03, p. 2].
            if (event.on_goal && particle.state == ParticleState::Fresh) {
                particle.state = ParticleState::Used;
                return true;
            }
            return false;
        }
        case EventKind::Obstacle: {
            Particle& particle = system.particles[event.first];
            particle.velocity = resolve_obstacle_collision(
                particle, system.obstacles[event.second]
            );
            ++particle.collision_count;
            return false;
        }
        case EventKind::ParticlePair: {
            Particle& first = system.particles[event.first];
            Particle& second = system.particles[event.second];
            const VelocityPair after = resolve_particle_collision(first, second);
            first.velocity = after.first;
            second.velocity = after.second;
            ++first.collision_count;
            ++second.collision_count;
            return false;
        }
        case EventKind::None:
            return false;
    }
    return false;
}

SimulationReport simulate_naive(
    System& system,
    const SimulationConfig& config,
    const FrameSink& sink
) {
    SimulationReport report{};

    const auto emit = [&](FrameReason reason) {
        if (sink) {
            sink(system, report.processed_events, reason);
        }
        ++report.written_frames;
    };

    emit(FrameReason::Initial);

    while (system.time < config.max_time) {
        if (config.max_events > 0
            && report.processed_events >= config.max_events) {
            report.reached_max_events = true;
            break;
        }

        const Event event = find_next_event(system);

        // Sin eventos futuros, o con el proximo mas alla del horizonte, la
        // corrida termina avanzando en linea recta hasta max_time. El estado
        // final queda completo y el post-proceso puede leer el ultimo tramo.
        if (event.kind == EventKind::None) {
            report.exhausted_events = true;
            advance(system, config.max_time - system.time);
            report.reached_max_time = true;
            break;
        }
        if (event.time > config.max_time) {
            advance(system, config.max_time - system.time);
            report.reached_max_time = true;
            break;
        }

        advance(system, event.time - system.time);
        const bool changed_color = apply_event(system, event);
        ++report.processed_events;

        if (changed_color) {
            emit(FrameReason::Color);
        } else if (config.save_every > 0
                   && report.processed_events % config.save_every == 0) {
            emit(FrameReason::Periodic);
        }
    }

    if (system.time >= config.max_time) {
        report.reached_max_time = true;
    }

    report.final_time = system.time;
    emit(FrameReason::Final);
    return report;
}


// --- Motor con cola de prioridad --------------------------------------------

namespace {

struct LaterEvent {
    [[nodiscard]] bool operator()(const Event& left, const Event& right) const noexcept {
        return left.time > right.time;
    }
};

using EventQueue = std::priority_queue<Event, std::vector<Event>, LaterEvent>;

// Un evento sigue vigente si ninguno de sus participantes choco con otra cosa
// desde que se lo agendo. Comparar contadores evita tener que buscar y borrar
// los eventos invalidados dentro de la cola [B16, pp. 1, 4].
[[nodiscard]] bool is_current(const System& system, const Event& event) noexcept {
    if (system.particles[event.first].collision_count != event.first_collisions) {
        return false;
    }
    if (event.kind == EventKind::ParticlePair
        && system.particles[event.second].collision_count != event.second_collisions) {
        return false;
    }
    return true;
}

void push_if_useful(EventQueue& queue, const Event& event, double horizon) noexcept {
    // Los eventos posteriores al horizonte de la corrida no se agendan: nunca
    // se van a procesar y solo harian crecer la cola.
    if (event.kind != EventKind::None && event.time <= horizon) {
        queue.push(event);
    }
}

// Agenda todos los choques futuros de una particula: su pared, cada obstaculo
// y cada una de las otras particulas. `skip_before` evita duplicar los pares
// en la carga inicial; al reagendar despues de un choque hay que recorrer
// todas las otras particulas, no solo las de indice mayor.
void schedule_particle(
    const System& system,
    std::size_t index,
    std::size_t skip_before,
    double horizon,
    EventQueue& queue
) noexcept {
    const Particle& particle = system.particles[index];
    const double now = system.time;

    const WallPrediction wall = predict_wall_collision(system.table, particle);
    push_if_useful(queue, Event{
        .time = now + wall.time,
        .kind = EventKind::Wall,
        .first = index,
        .second = 0,
        .wall = wall.kind,
        .on_goal = wall.on_goal,
        .first_collisions = particle.collision_count,
        .second_collisions = 0,
    }, horizon);

    for (std::size_t other = 0; other < system.obstacles.size(); ++other) {
        push_if_useful(queue, Event{
            .time = now + predict_obstacle_collision(particle, system.obstacles[other]),
            .kind = EventKind::Obstacle,
            .first = index,
            .second = other,
            .wall = WallKind::Short,
            .on_goal = false,
            .first_collisions = particle.collision_count,
            .second_collisions = 0,
        }, horizon);
    }

    for (std::size_t other = skip_before; other < system.particles.size(); ++other) {
        if (other == index) {
            continue;
        }
        push_if_useful(queue, Event{
            .time = now + predict_particle_collision(particle, system.particles[other]),
            .kind = EventKind::ParticlePair,
            .first = index,
            .second = other,
            .wall = WallKind::Short,
            .on_goal = false,
            .first_collisions = particle.collision_count,
            .second_collisions = system.particles[other].collision_count,
        }, horizon);
    }
}

}  // namespace

SimulationReport simulate_queue(
    System& system,
    const SimulationConfig& config,
    const FrameSink& sink
) {
    SimulationReport report{};

    const auto emit = [&](FrameReason reason) {
        if (sink) {
            sink(system, report.processed_events, reason);
        }
        ++report.written_frames;
    };

    emit(FrameReason::Initial);

    EventQueue queue;
    for (std::size_t index = 0; index < system.particles.size(); ++index) {
        schedule_particle(system, index, index + 1, config.max_time, queue);
    }

    while (system.time < config.max_time) {
        if (config.max_events > 0
            && report.processed_events >= config.max_events) {
            report.reached_max_events = true;
            break;
        }

        // Descartar los invalidados hasta dar con uno vigente.
        while (!queue.empty() && !is_current(system, queue.top())) {
            queue.pop();
        }
        if (queue.empty()) {
            // La cola vacia no significa por si sola que no haya choques: los
            // eventos posteriores a max_time nunca se agendaron. Para no
            // confundir el final normal de la corrida con un error de
            // implementacion se confirma con la busqueda exhaustiva, que
            // cuesta un unico barrido O(N^2) al terminar.
            report.exhausted_events =
                find_next_event(system).kind == EventKind::None;
            advance(system, config.max_time - system.time);
            report.reached_max_time = true;
            break;
        }

        const Event event = queue.top();
        queue.pop();

        advance(system, event.time - system.time);
        const bool changed_color = apply_event(system, event);
        ++report.processed_events;

        // Solo cambiaron las velocidades de los participantes, asi que solo
        // sus eventos hay que reagendar. Los duplicados que aparezcan quedan
        // invalidados por los contadores en cuanto se procese el primero.
        schedule_particle(system, event.first, 0, config.max_time, queue);
        if (event.kind == EventKind::ParticlePair) {
            schedule_particle(system, event.second, 0, config.max_time, queue);
        }

        if (changed_color) {
            emit(FrameReason::Color);
        } else if (config.save_every > 0
                   && report.processed_events % config.save_every == 0) {
            emit(FrameReason::Periodic);
        }
    }

    if (system.time >= config.max_time) {
        report.reached_max_time = true;
    }

    report.final_time = system.time;
    emit(FrameReason::Final);
    return report;
}

}  // namespace tp3
