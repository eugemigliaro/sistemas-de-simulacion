# Fase 5 — CLI del CIM y benchmark de M

## Objetivo

Esta fase vuelve utilizable el Cell Index Method desde el ejecutable y agrega el barrido reproducible de `M` requerido para preparar el punto 3 de la consigna. El análisis estadístico y los gráficos permanecen separados en Python.

La consigna pide que el CIM reciba posiciones, radios y los parámetros `N`, `L`, `M` y `rc`, y produzca la lista de vecinos y el tiempo de ejecución [TP01, p. 1]. Los archivos estático y dinámico ya contienen `N`, `L`, radios y posiciones [TP01, p. 2]; la CLI incorpora la selección del método y el valor de `M`.

## Búsqueda interactiva

El comando `neighbors` admite dos métodos:

    tp1 neighbors --method brute-force ...
    tp1 neighbors --method cim --M 10 ...

Fuerza bruta continúa siendo el valor predeterminado. `--M` es obligatorio para CIM y se rechaza con fuerza bruta para evitar parámetros silenciosamente ignorados. El límite máximo se calcula con el mismo criterio geométrico usado por el núcleo del CIM; un valor inválido produce un error antes de escribir resultados.

Ambos métodos leen los mismos archivos, miden solamente la búsqueda, escriben el mismo formato `neighbors.txt` e informan método, contorno, `rc`, pares encontrados, evaluaciones de distancia y nanosegundos.

## Barrido de M

El comando experimental es:

    tp1 benchmark-m \
      --static static.txt \
      --dynamic dynamic.txt \
      --rc 1 \
      --boundary walls \
      --seed 42 \
      --repetitions 10 \
      --output metrics.csv

`--seed` registra cómo se generó el sistema, ya que la semilla no forma parte de los archivos oficiales. `--repetitions` es obligatorio y positivo para que la decisión experimental quede explícita.

El sistema se carga una sola vez y se usa para todo el barrido [TP01, p. 1]. Para `M=1` se ejecuta fuerza bruta; desde `M=2` hasta el máximo permitido se ejecuta CIM. Antes de medir cada valor se exige igualdad exacta con la fuerza bruta y se hace una repetición de calentamiento no registrada.

El temporizador rodea únicamente el algoritmo de búsqueda. Incluye construcción de grilla, asignación de partículas, evaluación de candidatos y construcción de listas; excluye lectura, escritura y validación contra fuerza bruta.

## Formato de métricas

Cada ejecución recrea el CSV y conserva una fila por repetición:

    seed,boundary,method,N,L,M,rc,repetition,time_ns,neighbor_pairs,distance_evaluations

`method` vale `brute_force` para `M=1` y `cim` para los demás valores. `distance_evaluations` permite relacionar el tiempo con la cantidad efectiva de pares candidatos.

Las mediciones destinadas a resultados deben producirse con el ejecutable `release`; los tiempos de pruebas `debug` solo verifican el flujo.

## Verificación

Las pruebas cubren:

- cálculo del máximo `M` con desigualdad estricta y caso mínimo `M=1`;
- estructura, cantidad y serialización de mediciones;
- igualdad de `neighbors.txt` entre fuerza bruta y CIM;
- paredes y periodicidad mediante el ejecutable real;
- errores por método, `M` o repeticiones inválidas;
- encabezado, número de filas y métodos registrados en `metrics.csv`.

Esta fase no elige todavía los dos valores finales de `N`, la cantidad definitiva de repeticiones ni el `M` óptimo. Esas decisiones deben basarse en corridas piloto y en el análisis Python posterior.
