#include "tp3/naive.hpp"

namespace tp3 {

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

}  // namespace tp3
