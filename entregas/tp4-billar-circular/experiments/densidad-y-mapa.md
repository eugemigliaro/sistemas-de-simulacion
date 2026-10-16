# Registro técnico — densidad y mapa de posiciones (2.4.a–b)

Fecha: 2026-10-16. Registro reproducible de código, datos y controles; no es la presentación entregable.

## Fuentes y conjuntos comparables

El punto 2.4.a exige reutilizar las salidas del benchmark de 30 s; el 2.4.b pide un mapa de t90 o t100 sobre (x0,N) [TP04, pp. 3–4]. Se preservan las 50 corridas originales, sus cronometrajes y resultados. El [registro anterior](rendimiento-y-densidad.md) sigue describiendo correctamente ese conjunto. La presencia de tiempos no observados se trata como censura administrativa: no se descartan realizaciones ni se reemplazan sus tiempos por 30 s para calcular una media ordinaria.

Se agregan seguimientos con las mismas condiciones iniciales, pero h=0,0000125 s en lugar de 0,00005 s. Son **corridas complementarias refinadas**, no continuación bit a bit del benchmark. Se importa el estado inicial original con 17 dígitos y se verifica igualdad exacta. La comparación de rendimiento no se modifica ni se mezcla con estas ejecuciones concurrentes.

Se reutilizan nueve corridas de 100 s de 2.2 (cinco N=20 y cuatro N=100) que ya observaron t100 y tienen idénticas condiciones iniciales y h. El tiempo del primer contacto completo ya se conoce en esos casos; no es necesario seguirlos hasta 300 s. Los 41 casos restantes se simulan hasta 300 s. Después se extienden selectivamente hasta 600 s las tres realizaciones N=400 que quedaron con 399/400 convertidas; se conserva el conjunto de 300 s. Se comprueba igualdad exacta del estado a 300 s al repetir con horizonte mayor y el mismo h.

El mapa mostró un indicio de menor t90 para N=50 y x0=r. Se completaron diez realizaciones de ese grupo: las cinco del mapa más cinco nuevas hasta 300 s. Esta ampliación es exploratoria y adaptativa, no una hipótesis preespecificada. Se registró por separado y no se añadió un cronometraje N=50 al benchmark original.

## Qué se calcula

Para cada realización se ordenan los primeros contactos: t90 es el contacto número ceil(0,9N), y t100 el último cuando todas las partículas se convirtieron. Solo después se agregan los diez tiempos por grupo. Las barras son desvíos estándar muestrales entre realizaciones (ddof=1), no errores estándar ni incertidumbres sobre un óptimo [COR03] [T00, pp. 69–70].

Si falta algún tiempo, su media completa queda vacía y se publica el número de censuras y una cota inferior de la media: se sustituyen únicamente para esa **cota** los tiempos desconocidos por su tiempo de seguimiento. No se la etiqueta como tiempo medido. Como diagnóstico adicional se conserva la media restringida de min(T,tau), con tau=30 o 300 s; esta magnitud responde a otra pregunta y no estima sin supuestos la media completa de T.

**Derivación local:** una media muestral de primeros cruces no observados no es identificable a partir de un corte finito. Ni una interpolación ni un ajuste exponencial elegido por apariencia resuelve esa falta de información. Por eso se preservan las cotas y no se inventan colas de la distribución.

## Resultados del seguimiento hasta 300 s

Las filas completas indican media ± desvío de diez realizaciones. Las cotas no tienen barras de desvío de tiempos desconocidos.

| N | Densidad N/(πR²) [m⁻²] | t90 [s] | t100 [s] | Censuras t90/t100 |
|---:|---:|---:|---:|---:|
| 20 | 24,48 | 23,7 ± 4,2 | 41 ± 14 | 0/0 |
| 100 | 122,38 | 25,3 ± 3,1 | 58 ± 22 | 0/0 |
| 200 | 244,76 | 36,0 ± 2,5 | 103 ± 35 | 0/0 |
| 400 | 489,52 | 89,8 ± 4,0 | >252,6, cota de la media | 0/3 |
| 650 | 795,47 | >300, cota | >300, cota | 10/10 |

Los resultados completos sin redondear están en [density-extended-summary.csv](results/density-extended-summary.csv). Las medias del complemento no sustituyen silenciosamente las del conjunto obligatorio de 30 s: por ejemplo, N=20 tenía t90=21,1±4,2 s con el paso del benchmark. El refinamiento cambia las trayectorias a largo plazo; no corresponde concatenar estados de ambos pasos.

N=650 llega a Fu(300 s)=0,04323 en promedio: solo el **4,32 %** convertido. En cada una de sus diez realizaciones se sabe t90>300 s y t100>300 s. No se obtiene una media completa ni una predicción fiable de cuándo convertirán todas; extender el horizonte diez veces no resuelve automáticamente la censura.

## ¿Existe una densidad óptima?

El seguimiento selectivo observó los tres t100 faltantes de N=400: 328,7315; 378,9515 y 338,6179 s. La media completa de ese grupo pasa a **267±61 s**. La igualdad exacta de sus estados de 300 s quedó verificada, no solo la coincidencia de primeros contactos.

Resultados finales del complemento, **diez realizaciones por N**, incluyendo el grupo adicional N=50:

| N | t90, media ± desvío [s] | t100, media ± desvío [s] |
|---:|---:|---:|
| 20 | 23,7 ± 4,2 | 41 ± 14 |
| 50 | **20,4 ± 3,5** | 42,5 ± 8,1 |
| 100 | 25,3 ± 3,1 | 58 ± 22 |
| 200 | 36,0 ± 2,5 | 103 ± 35 |
| 400 | 89,8 ± 4,0 | 267 ± 61 |
| 650 | >300, cota de la media | >300, cota de la media |

**Conclusión muestral:** con x0=r, el menor t90 medio corresponde a N=50 (densidad 61,19 m⁻²), un mínimo interior de esta grilla ampliada. Para t100 la menor media corresponde a N=20 (24,48 m⁻²), en el borde inferior del rango, con N=50 muy próximo. Incluso las cotas del grupo censurado N=650 son mayores que ambas medias mínimas. **No hay una única densidad óptima demostrada para ambos criterios**: depende de qué umbral se minimiza. Son menores medias muestrales, no pruebas de óptimos poblacionales, de diferencias significativas ni de óptimos globales fuera de los N ensayados. La selección adaptativa de N=50 refuerza el carácter exploratorio.

Ver [resumen final combinado](results/density-complete-summary.csv), [mínimos por criterio](results/density-best-tested.json), [tiempos frente a densidad](figures/density-final-times.png) y [Fu(t)](figures/density-final-fu.png). Los paneles inferiores de tiempos usan eje vertical logarítmico; las cotas y medias tienen símbolos distintos. Las bandas de Fu son desvíos estándar entre diez realizaciones, recortadas visualmente a [0,1]. La curva media Fu no se usa para obtener los tiempos medios de cruce.

**Inferencia mecánica:** aumentar N puede favorecer cambios de trayectoria por encuentros y, a la vez, dificultar el transporte y acceso a obstáculos. t100 depende además de la última partícula, por lo que no es equivalente a un tiempo típico individual. La fuerza de la pared circular es radial y no cambia por sí sola el momento angular individual; otros contactos sí modifican las trayectorias [TP04, pp. 2–3]. La frecuencia de colisiones no se midió directamente y no se afirma que sea la causa exclusiva de las diferencias.

Para apoyar la discusión se calcula a 100 s el desplazamiento cuadrático medio de las N partículas de cada corrida, respecto a su posición inicial, y la versión radial ⟨(|r(100)|−|r(0)|)²⟩. Luego se promedian esas diez medidas por N. El dominio es acotado y no periódico: estas medidas **no son un coeficiente de difusión**. Movimiento apreciable no implica acceso frecuente al centro ni conversión rápida.

El DCM radial a 100 s es 0,00927±0,00092 m² para N=650, frente a 0,02737±0,00104 m² para N=400 (desvíos entre realizaciones). El DCM vectorial de N=650 es 0,072±0,059 m²: no está inmóvil. La menor redistribución radial es compatible con menor acceso a obstáculos cercanos al centro, sin demostrar una causa exclusiva. Datos y definición en [movilidad](results/density-mobility-100.csv).

La comparación con N=650 también cambia la familia de inicialización: red hexagonal con 500 barridos Monte Carlo, frente a rechazo secuencial para N≤400. El piloto original mostró orden residual; no se atribuye todo el cambio exclusivamente a densidad ni se afirma muestreo de equilibrio [registro de inicialización](rendimiento-y-densidad.md).

## Diseño del mapa 2.4.b

Se estudian N={20,50,100,200}, once posiciones x0 entre r=0,0175 m y R−r=0,4925 m, cinco realizaciones por celda y corte 100 s: **220 casos**. Se reutilizan 110 de 2.2 y cinco seguimientos de N=200 en x0=r, truncando los primeros contactos a 100 s; se simulan 105 casos nuevos. No se usa un contacto posterior a 100 s para completar una celda del mapa.

Cada celda presenta la media de cinco t90, con desvíos disponibles en el CSV y en los cortes t90(x0). Las líneas entre posiciones son guías visuales. Las celdas censuradas no se interpolan. Un mínimo solo se identifica entre las medias muestrales de la grilla cuando ninguna cota de una celda censurada podría mejorarlo. La resolución espacial es 0,0475 m; no es una estimación exacta del óptimo continuo ni una prueba de significancia frente a cada vecino.

Las **220 realizaciones alcanzaron t90** antes de 100 s. El [mapa de calor](figures/density-position-heatmap.png) tiene las 44 medias completas y destaca las menores por fila; los [cortes con desvíos](figures/density-position-cuts.png) permiten evaluar la dispersión.

| N | x0 de menor media en la grilla [m] | t90 [s], media ± desvío |
|---:|---:|---:|
| 20 | 0,3975 | 9,2 ± 1,1 |
| 50 | 0,3025 | 11,5 ± 2,4 |
| 100 | 0,1600 | 13,6 ± 1,0 |
| 200 | 0,2075 | 20,7 ± 1,2 |

La posición de menor media cambia con N y no sigue una tendencia monótona en estos cuatro mínimos. Los vecinos pueden ser próximos dentro de la dispersión: N=200 en x0=0,16 m da 21,2±1,4 s, cercano al mínimo de x0=0,2075 m. No se propone una ley de x0 óptimo frente a N ni significancia estadística de cada desplazamiento.

Los mínimos de 2.4.b usan **cinco** realizaciones por celda; la comparación de densidad en x0=r usa **diez** por N. Por eso el promedio N=20 en x0=r del mapa (22,9 s) no tiene que ser idéntico al del complemento de densidad (23,7 s).

## Verificación final

Se ejecutaron **154 corridas nuevas**: 41 extensiones iniciales, 105 casos nuevos del mapa, tres seguimientos selectivos y cinco realizaciones adicionales N=50. Se preservaron los 160 checkpoints fuente del benchmark TP4 y del estudio de posiciones. El motor no cambió.

En todas las corridas nuevas se controló energía total desde estados cada 1 s. El mayor error relativo máximo **muestreado** fue **0,02670 %**, inferior al criterio local 0,1 %. No garantiza el máximo continuo entre cuadros. Los nueve casos reutilizados completos conservan su control previo de extremos, sin inventarles un máximo temporal.

Pasaron las pruebas C++ existentes y **25 pruebas Python**. La [auditoría independiente](results/density-verification.json) verificó hashes de fuentes, entradas, binario, trayectorias y artefactos; 60 realizaciones finales de densidad y 220 del mapa; primeros contactos, cortes, medias, desvíos, cotas y mínimos; y series energéticas. Las figuras se revisaron visualmente. La reanudación debe recuperar checkpoints compatibles sin repetir simulaciones.

## Reproducción

Desde la carpeta del TP4, con NumPy y Matplotlib:

```bash
make release
python/.venv/bin/python python/density_study.py
python/.venv/bin/python python/density_followup.py
python/.venv/bin/python python/density_extra.py
python/.venv/bin/python python/density_plot.py
python/.venv/bin/python python/density_verify.py
```

En esta sesión se utilizó `../tp3-billar-metegol/python/.venv/bin/python`, sin modificar ese entorno. El ejecutor principal y el seguimiento selectivo admiten checkpoints compatibles. El seguimiento puede solaparse con el mapa una vez que existe `density-extended-cases.json`; no se están midiendo tiempos de ejecución comparables al benchmark.

- [Configuración](configs/density-position.json) y [diseño](../diseno-densidad-posicion.md).
- Contratos [principal](results/density-position-contract.json) y [seguimiento](results/density-followup-contract.json).
- Datos [primarios de 30 s](results/density-baseline-summary.csv), [extensión a 300 s](results/density-extended-summary.csv), [seguimiento a 600 s](results/density-final-summary.csv) y [combinación final con N=50](results/density-complete-summary.csv).
- [Resumen del mapa](results/density-heatmap-summary.csv), [mínimos por N](results/density-best-positions.json) y [tiempos por realización](results/density-position-raw.csv).
- Trayectorias completas bajo `experiments/raw/density-position/`, ignoradas por Git; checkpoints y componentes energéticas bajo `experiments/results/`.
- [Contrato N=50 adicional](results/density-extra-contract.json); manifiestos [principal](results/density-position-manifest.json), [seguimiento](results/density-followup-manifest.json), [N=50](results/density-extra-manifest.json) y [figuras](results/density-plot-manifest.json).

La intervención de IA incluye implementación, ejecución y postproceso para revisión del estudiante. La explicación y elaboración de la presentación corresponden al grupo [TP04, p. 4].
