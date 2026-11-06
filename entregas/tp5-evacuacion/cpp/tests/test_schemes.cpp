#include <sstream>

#include "test_support.hpp"
#include "tp5/setup.hpp"
#include "tp5/simulation.hpp"

using namespace tp5;

namespace {

Params small(Scheme scheme) {
    Params p;
    p.scheme = scheme;
    p.agents = 40;
    p.side = 12.0;
    p.seed = 3;
    p.t_max = 400.0;
    return p;
}

// Solo los renglones de salida (la cabecera y el pie difieren entre esquemas).
std::string run(const Params& p, Summary& s) {
    std::ostringstream out;
    Writer writer(&out);
    s = simulate(p, initial_agents(p, Room(p)), writer);
    std::istringstream in(out.str());
    std::string exits;
    for (std::string line; std::getline(in, line);) {
        if (line.starts_with("exit ")) exits += line + '\n';
    }
    return exits;
}

}  // namespace

int main() {
    // Con T* enorme nadie es EDMD: el híbrido coincide exactamente con TSDMD puro.
    Summary ts;
    Summary hy;
    Params pt = small(Scheme::TimeStep);
    Params ph = small(Scheme::Hybrid);
    ph.t_star = 1e6;
    const std::string a = run(pt, ts);
    const std::string b = run(ph, hy);
    CHECK(ts.exited == pt.agents);
    CHECK(hy.switches == 0);
    CHECK(hy.end_time == ts.end_time);
    // Mismos instantes de salida, renglón por renglón.
    CHECK(!a.empty() && a == b);

    // Con T* chico hay agentes EDMD, nadie se pierde y todos salen.
    Params pc = small(Scheme::Hybrid);
    pc.t_star = 0.02;
    Summary hc;
    run(pc, hc);
    CHECK(hc.switches > 0);
    CHECK(hc.exited + hc.remaining == pc.agents);
    CHECK(hc.bound_violations == 0);
    CHECK(hc.agent_steps < ts.agent_steps);

    // EDMD puro: evacúa y procesa eventos.
    Summary ed;
    run(small(Scheme::EventDriven), ed);
    CHECK(ed.events > 0);
    CHECK(ed.exited + ed.remaining == pt.agents);

    // EDMD con relajación analítica: un choque suave entre agentes casi relajados no se
    // repite en el mismo instante (antes, redondear v a v_d e deshacía el rebote y la
    // corrida quedaba en t = 5,6357 s para siempre con esta configuración).
    Params pa;
    pa.scheme = Scheme::EventDriven;
    pa.relaxation = Relaxation::Analytic;
    pa.agents = 60;
    pa.side = 15.0;
    pa.seed = 701;
    pa.t_max = 6.0;
    Summary an;
    run(pa, an);
    CHECK(an.end_time == pa.t_max);
    return test::finish("test_schemes");
}
