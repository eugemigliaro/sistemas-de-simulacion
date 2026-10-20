# Registro técnico — distribución de rapidez (2.3)

Fecha: 2026-10-16. Código, datos y visualizaciones de desarrollo para revisión del estudiante.

## Estudio y estabilización

Se ejecutaron diez realizaciones N=100 **sin obstáculos**, con velocidades iniciales de módulo v0=1 m/s, m=0,025 kg, h=0,0000125 s y estados cada 0,1 s [TP04, pp. 3–4]. Las semillas son 1–10, con la inicialización por rechazo del motor existente. No se modificó el motor ni se reescalaron velocidades.

El ensayo exploratorio de 30 s no cumplió el criterio local de estabilidad: el cambio de theta entre las ventanas [20,25) y [25,30) s fue 2,80 %, mayor que el límite predefinido del 2 %. Se conservaron sus datos, fuentes y diagnóstico en [speed-pilot-30](results/speed-pilot-30/). Se amplió a 60 s y a ventanas de 10 s para reducir fluctuaciones de muestreo, manteniendo los límites. Los primeros 30 s de las diez nuevas realizaciones coinciden exactamente con los del ensayo, tanto en rapidez como en componentes energéticas.

En el estudio principal, las cuatro comparaciones sucesivas entre ventanas de [10,60) s dan distancias de variación total entre 0,00743 y 0,01036, inferiores al límite local 0,05, y cambios relativos de theta entre 0,040 % y 0,840 %, inferiores al 2 %. Se cumple el requisito de al menos tres comparaciones consecutivas en todo el sufijo. La comparación [0,10)→[10,20) da un cambio térmico de 1,84 %; la primera ventana se excluye por contener el estado inicial singular. Ver [diagnóstico por ventanas](results/speed-windows.csv).

Se usa **[10,60) s** para el ajuste. Es una ventana compatible con estacionariedad a esta resolución y con estos criterios descriptivos; no una prueba de equilibrio exacto ni la determinación del primer instante físico de relajación [COR02]. Las distribuciones instantáneas, cada una promediada entre diez realizaciones, están en [evolución temporal](figures/speed-evolution.png) y [datos](results/speed-snapshots.csv). La distribución inicial es una delta en v=1 m/s. Con bins centrados en múltiplos de 0,1 m/s, v0 cae en el centro de [0,95;1,05): el redondeo de las componentes de velocidad ya no reparte entre dos bins a las partículas que todavía no chocaron.

## Histograma y ajuste

**Reanálisis del 2026-10-20.** Los bins originales tenían un borde en v0=1 m/s y el histograma de t=0,1 s mostraba dos barras altas, de 19,5 % y 21,3 %, que eran las mismas partículas sin chocar repartidas por redondeo. Se desplazaron los bins medio ancho (`bin_offset` en la configuración) y se recalculó todo desde las muestras guardadas con `python/speed_study.py --reanalyze`, sin volver a simular: las diez corridas y sus hashes no cambiaron. El ajuste pasó de 0,0123986 J a 0,012403 J; con cuatro cifras sigue siendo 1,240×10⁻² J.

Se promedian 500 cuadros por realización dentro de [10,60) s, es decir, 50.000 velocidades por corrida. Primero se obtiene una densidad normalizada por corrida; luego se promedian las diez densidades con igual peso. Los bins son [0;0,05) y luego 40 de ancho 0,1 m/s centrados en 0,1, 0,2, …, 4,0 m/s; contienen todas las muestras. Las barras son el **desvío estándar entre diez realizaciones**, no entre 500.000 velocidades supuestamente independientes [T00, pp. 68–70] [COR03].

Se ajusta Maxwell–Boltzmann 2D con theta=kBT como único parámetro libre [TP04, p. 4]. El modelo usado para el bin [a,b] es su densidad teórica media:

`g_i(theta) = [exp(−m a²/(2 theta)) − exp(−m b²/(2 theta))] / (b−a)`.

Se minimiza `sum_i [hist_i−g_i(theta)]²` sin ponderaciones, amplitudes u offsets libres, siguiendo T00 pp. 79–80. El promedio integrado del modelo evita confundir la densidad de un bin con el valor puntual en su centro. La [figura de ajuste](figures/speed-fit.png) muestra la curva continua y el mínimo de la función objetivo. El algoritmo usa grilla logarítmica y sección áurea, sin SciPy. Ver [diseño y límites](../diseno-rapidez.md).

## Comparación energética

Resultados locales, con más dígitos disponibles en [speed-summary.json](results/speed-summary.json):

| Magnitud | Valor |
|---|---:|
| theta ajustado al histograma medio | 0,012403 J |
| Media ± desvío de los diez theta ajustados por separado | 0,01240 ± 0,00009 J |
| Referencia inicial mv0²/2 | 0,0125000 J |
| Media ± desvío entre corridas de m⟨v²⟩/2 en la ventana | 0,012323 ± 0,000008 J |
| Energía potencial media por partícula en la ventana | 0,0001765 J |
| Máximo error relativo energético **muestreado** entre las diez corridas | 0,006835 % |

El ajuste a la media está 0,78 % por debajo de la referencia inicial y 0,65 % por encima de la energía cinética media medida. La media de los ajustes individuales y el ajuste al histograma medio son operaciones diferentes; aquí dan valores muy próximos. El desvío de ajustes individuales **no es una incertidumbre formal del ajuste a la media** ni un intervalo de confianza.

**Interpretación derivada del modelo:** inicialmente no hay solapamientos y toda la energía es cinética. En el estacionario los contactos de duración finita almacenan energía potencial, por lo que no corresponde imponer que la energía cinética por partícula sea idéntica al valor inicial. La disminución cinética media del 1,41 % coincide con el aporte potencial medio; K+U por partícula permanece próximo a 0,0125 J. Esto se calcula desde estados guardados, incluyendo cada par una sola vez y la pared [TP04, pp. 2–3] [T04, p. 42].

No se atribuye exclusivamente a la energía potencial la diferencia entre theta ajustado y cinética medida: mínimos cuadrados sobre una distribución muestreada no impone la identidad del segundo momento. La curva describe bien el histograma a la resolución observada, pero no se hizo una prueba formal de bondad de ajuste. Tampoco se demuestra igualdad exacta ni se convierte kBT en una temperatura en kelvin.

## Reproducción y controles

Desde la carpeta del TP4:

```bash
make release
python/.venv/bin/python python/speed_study.py
make test PYTHON=python/.venv/bin/python
```

Esta sesión utilizó `../tp3-billar-metegol/python/.venv/bin/python`, sin modificar ese entorno. El ejecutor recupera las diez corridas mediante checkpoints compatibles y verifica las muestras NPZ. Los datos de rapidez y energía se conservan en [speed-cases](results/speed-cases/); los CSV completos quedan en `experiments/raw/speed/`, excluidos de Git por volumen.

La [configuración](configs/speed.json), el [contrato de fuentes y binario](results/speed-contract.json) y el [manifiesto de artefactos](results/speed-manifest.json) permiten verificar la procedencia. Se validaron los hashes de fuentes y artefactos, y la identidad de los diez prefijos con el ensayo de 30 s. Pasaron los tests C++ existentes y 21 pruebas Python, incluidas recuperación de un parámetro sintético, normalización y colas, integral teórica conocida y criterio de estabilidad consecutiva.

Este registro documenta asistencia de IA en código, ejecución y análisis. La revisión, explicación y elaboración de la presentación corresponden a los estudiantes [TP04, p. 4].
