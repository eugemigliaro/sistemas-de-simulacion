# Fase 2 — Generación y entrada/salida

## Alcance implementado

El motor C++ ya puede construir N partículas circulares con radios no nulos, distribuidos uniformemente entre los límites configurados, sin solapamientos y dentro de un dominio cuadrado. La configuración pedida por el TP usa radios entre 0.23 y 0.26 [TP01, p. 1].

Se admiten las dos condiciones de contorno requeridas [TP01, p. 1]:

- walls: el disco completo queda dentro del cuadrado;
- periodic: el centro queda en [ri,L-ri], como con paredes, y las colisiones a través de bordes opuestos se verifican mediante imagen mínima.

La secuencia pseudoaleatoria depende de una semilla explícita. Repetir todos los parámetros y la semilla con el mismo ejecutable produce exactamente los mismos archivos.

## Algoritmo de ubicación

Para cada partícula:

1. se sortea el radio;
2. se sortea una posición válida para el contorno;
3. se calcula su distancia borde-borde contra las partículas ya aceptadas;
4. se acepta si ninguna distancia es negativa;
5. se vuelve a intentar hasta el límite configurado si existe un solapamiento.

El límite evita que una configuración demasiado densa quede ejecutándose indefinidamente. Su agotamiento produce un error explícito; no se escribe silenciosamente un sistema incompleto.

## Formatos

El escritor estático produce N, L y luego N filas de radio y propiedad. El escritor dinámico produce el tiempo y N filas de x, y, vx y vy, de acuerdo con el formato general de la consigna [TP01, p. 2].

El lector conserva ese contrato y, además, acepta filas dinámicas x, y sin velocidades porque el archivo oficial Dynamic100.txt utiliza esa variante [EJ01]. En tal caso asigna vx=0 y vy=0. Los escritores usan precisión suficiente para recuperar exactamente cada double al volver a leerlo.

## Ejecución manual

Desde entregas/tp1-cim:

    make cpp-run ARGS="generate --N 100 --L 20 --seed 42 --boundary walls --static data/generated/static.txt --dynamic data/generated/dynamic.txt"

Para contorno periódico:

    make cpp-run ARGS="generate --N 100 --L 20 --seed 42 --boundary periodic --static data/generated/periodic-static.txt --dynamic data/generated/periodic-dynamic.txt"

La ayuda completa está disponible con:

    make cpp-run ARGS="--help"

## Cobertura de pruebas

- reproducibilidad exacta con igual semilla;
- cambio de configuración al cambiar la semilla;
- N, IDs, radios, propiedades y velocidades;
- pertenencia al dominio con paredes y periodicidad;
- ausencia de solapamientos para ambos contornos;
- error ante configuraciones inválidas o imposibles de ubicar;
- escritura y lectura sin pérdida;
- compatibilidad dinámica de dos y cuatro columnas;
- filas faltantes, adicionales, mal formadas o geométricamente inválidas.
