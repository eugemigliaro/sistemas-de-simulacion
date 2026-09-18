# TP3 — Billar-Metegol

Resolución del Trabajo Práctico 3 de Sistemas de Simulación: dinámica molecular
dirigida por eventos sobre una mesa de metegol. El motor está implementado en
C++20; la animación y el análisis son programas independientes en Python 3, como
exige la consigna [TP03, p. 1].

## Estado

En desarrollo. Entrega: 28 de septiembre de 2026, 13:00.

Fases completadas:

- [x] Fase 1 — geometría, modelo y validación de configuraciones
- [ ] Fase 2 — generación de condiciones iniciales e I/O
- [ ] Fase 3 — predicción y resolución de colisiones
- [ ] Fase 4 — motor ingenuo (oráculo de correctitud)
- [ ] Fase 5 — motor con cola de prioridad
- [ ] Fase 6 — post-proceso (Fu, t90, DCM, D)
- [ ] Fase 7 — experimentos 1.1, 1.2 y 1.3
- [ ] Fase 8 — animación y entregables

## Separación de responsabilidades

La cátedra marcó como error importante en el TP2 que el motor calculara
observables dentro del bucle principal [COR02]. Acá la división es estricta:

| Componente | Responsabilidad |
|---|---|
| Motor C++ | Genera estado: tiempo, posiciones, velocidades y color |
| Post-proceso Python | `Ng(t)`, `Fu(t)`, `t90`, DCM, ajuste `E(c)`, `D` y barras de error |
| Animación Python | Módulo independiente que lee el archivo de texto |

El color fresca/usada es **estado**, no observable: la consigna pide imprimirlo
junto a posiciones y velocidades [TP03, p. 2].

## Convenciones principales

- Mesa de `L = 1.20` m por `W = 0.68` m; arcos de `d = 0.20` m centrados en las
  paredes cortas. Condición de gol: `|y - W/2| <= d/2` [TP03, p. 2].
- Partículas de `r = 0.0175` m, `m = 0.025` kg, `v0 = 1` m/s. Todas las
  colisiones son elásticas.
- Obstáculos circulares fijos de masa infinita, con `Rk >= r`, íntegramente
  dentro del dominio y sin solaparse [TP03, p. 3].
- El DCM se ajusta como `<|Δr|²> = 4Dt` (desplazamiento vectorial completo).

Las decisiones completas están en [`docs/decisiones.md`](docs/decisiones.md).

## Compilación y pruebas

```bash
make test
make sanitize
```

```bash
make debug && ./cpp/build/debug/tp3 --version
```
