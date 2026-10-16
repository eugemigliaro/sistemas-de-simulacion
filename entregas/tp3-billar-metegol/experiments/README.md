# Experimentos del TP3

Este directorio preserva configuraciones, resultados tabulares y figuras de la
fase 7. Los archivos de `raw/` son trayectorias regenerables y no se versionan;
los CSV resumidos y las figuras sí se conservan para mantener la trazabilidad.

## Punto 1.1 — tiempo de ejecución en función de N

### Protocolo

- Motor: cola de prioridad (`queue`), compilado en release.
- Geometría: mesa vacía.
- Tiempo físico final: `tf = 30 s`.
- Cantidades de partículas: `N = {10, 25, 50, 100, 200, 400}`.
- Repeticiones: diez semillas independientes, de 1 a 10, por cada `N`.
- Salida de trayectoria: `/dev/null`, para excluir el costo de escritura.
- Medición: reloj monotónico alrededor de `simulate_queue`. Excluye la
  generación de la condición inicial y la apertura del archivo; incluye la
  gestión de eventos y el envío de cuadros al sumidero `/dev/null`.
- Barras de la figura: desvío estándar entre realizaciones [TP03, p. 3].

La configuración completa está en
[`configs/performance.json`](configs/performance.json). Para regenerar los
datos y la figura desde la raíz del TP3:

```bash
make performance
make performance-plot
```

El ejecutor guarda cada corrida apenas termina y reutiliza mediciones válidas.
El manifiesto impide mezclar resultados generados con otra configuración.

### Resultados

| N | tiempo medio (s) | desvío estándar (s) | repeticiones |
|---:|---:|---:|---:|
| 10 | 0,0002766 | 0,0000731 | 10 |
| 25 | 0,0016177 | 0,0001460 | 10 |
| 50 | 0,0076207 | 0,0002178 | 10 |
| 100 | 0,0542562 | 0,0005076 | 10 |
| 200 | 0,5088941 | 0,0025827 | 10 |
| 400 | 9,3919620 | 0,8716929 | 10 |

Los seis puntos alcanzaron `tf = 30 s` en todas sus realizaciones. El rango
propuesto resultó ejecutable y se conserva completo. La figura usa escalas
logarítmicas en ambos ejes porque los tiempos cubren más de cuatro órdenes de
magnitud; los ejes mantienen las magnitudes y unidades requeridas.

### Archivos

- `results/performance-raw.csv`: una fila por realización, con comando y
  diagnóstico estructurado del motor.
- `results/performance-summary.csv`: media, desvío, error estándar, extremos y
  cantidad de repeticiones por `N`.
- `results/performance-manifest.json`: contrato exacto de la corrida.
- `figures/runtime-vs-n.png`: figura final del punto 1.1.
