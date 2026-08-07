# Sistemas, modelos y simulación

## De lo real a la simulación

La cadena conceptual de la materia parte del **sistema real**, construye un **modelo físico-matemático**, lo traduce a un **modelo o implementación computacional** y finalmente ejecuta una **simulación**. Cada etapa agrega decisiones y aproximaciones que deben explicitarse [T00, p. 7] [T00, p. 8] [T00, p. 9] [T00, p. 10].

Un sistema reúne componentes relacionados que funcionan como un todo. Se caracteriza por sus límites, componentes, entradas, salidas, procesos y observables medibles [T00, p. 13] [T00, p. 14]. Un modelo es una abstracción y simplificación del sistema real; no es único. Recibe entradas o estímulos y produce salidas o respuestas [T00, p. 16]. Modelar busca principalmente entender y predecir, y también sirve para analizar, diseñar, controlar y evaluar el funcionamiento bajo distintas condiciones [T00, p. 17] [T00, p. 18].

La caracterización experimental o computacional exige medir y registrar entradas y salidas con un muestreo definido. Del *output* directo puede derivarse un observable que evoluciona en el tiempo y, de este, un escalar que resume el comportamiento; por ejemplo, una serie de posiciones puede convertirse en un caudal [T00, p. 19] [T00, p. 22] [T00, p. 23].

## Estado y dinámica

El estado $x(t)$ reúne la información necesaria para determinar la salida futura junto con la entrada $u(t)$. Sus componentes son las variables de estado, y la dinámica expresa cómo evolucionan [T00, p. 26]. El espacio de estados contiene todos los valores posibles del estado. Una formulación general es:

$$
ẋ(t)=f(x(t),u(t),t), \quad x(t_0)=x_0,
$$

$$
y(t)=g(x(t),u(t),t).
$$

[T00, p. 27] [T00, p. 28]

Una trayectoria en el espacio de fases representa la evolución del estado; por ejemplo, posición y velocidad pueden formar los ejes de un oscilador [T00, p. 30] [T00, p. 31].

## Clasificaciones útiles

- **Estático / dinámico:** en el primero la salida no depende de entradas pasadas; el segundo tiene memoria y suele expresarse mediante ecuaciones diferenciales [T00, p. 34].
- **Lineal / no lineal:** un modelo lineal cumple superposición; un modelo no lineal no la cumple y puede mostrar sensibilidad a condiciones iniciales, mezcla y periodicidad densa [T00, p. 35] [T00, p. 37].
- **Estado continuo / discreto:** las variables pueden tomar valores continuos o pertenecer a conjuntos discretos [T00, p. 39].
- **Determinista / estocástico:** un modelo es estocástico si al menos una entrada es aleatoria; los métodos de Monte Carlo requieren números aleatorios y reportan observables agregados sobre realizaciones [T00, p. 40] [T00, p. 41].
- **Tiempo discreto / eventos:** una simulación puede actualizar el estado cada intervalo fijo o solo cuando ocurre un evento instantáneo, como un arribo o una partida en una cola [T00, p. 46] [T00, p. 48] [T00, p. 51] [T00, p. 55].

## Simulación, análisis y animación

Una simulación computacional es un programa que reproduce el comportamiento de un sistema a partir de ecuaciones, interacciones entre agentes, algoritmos o heurísticas. Puede producir una evolución temporal, pero también otros tipos de salida [T00, p. 62] [T00, p. 63]. Una animación es una representación visual: puede originarse en una simulación, pero no es la simulación, y una simulación no necesita tener animación [T00, p. 64].

La arquitectura de trabajo separa tres responsabilidades: el simulador genera el estado; una herramienta de análisis calcula observables y resultados; y un visualizador produce imágenes o videos. La cátedra pide mantener especialmente separadas la simulación y la animación [T01, p. 32] [T01, p. 33] [T01, p. 35].

## Criterio de trazabilidad

Al documentar una simulación conviene poder recorrer la cadena completa:

1. sistema real y pregunta;
2. supuestos del modelo físico-matemático;
3. variables de estado, entradas, parámetros y salidas;
4. traducción al modelo computacional;
5. protocolo de simulación;
6. definición matemática de observables;
7. análisis, incertidumbre y conclusiones.

Esta organización coincide con la estructura solicitada para comunicar los trabajos [GPRES, p. 2].
