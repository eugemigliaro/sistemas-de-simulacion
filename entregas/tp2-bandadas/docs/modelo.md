# Modelo computacional

## Estado

Cada partícula puntual conserva un identificador, una posición bidimensional y un ángulo. La rapidez es un parámetro global constante.

Para avanzar de `t` a `t+1`:

1. se construye el CIM con las posiciones en `t`;
2. se miden `va(t)` y `S(t)`;
3. cada posición siguiente se obtiene con el ángulo en `t`;
4. Vicsek obtiene el ángulo siguiente del promedio vectorial local, mientras que el votante copia una candidata local;
5. se agrega ruido independiente y se normaliza el ángulo;
6. cuando todas las partículas tienen estado siguiente, se reemplaza el estado actual.

## Flujo previsto

```text
configuración
     |
     v
motor C++ --------> trayectoria de texto + observables de texto
                                           |
                       +-------------------+------------------+
                       v                                      v
               animación Python                       análisis Python
```

La trayectoria no se consumirá durante la simulación: la animación será independiente [TP02, p. 1].
