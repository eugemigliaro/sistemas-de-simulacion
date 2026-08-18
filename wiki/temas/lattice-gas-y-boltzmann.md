# Lattice gas y lattice Boltzmann

## Del fluido continuo a reglas microscópicas

La descripción continua de un fluido usa conservación de masa, energía y momento, junto con condiciones de contorno; las ecuaciones de Navier–Stokes son no lineales y en general se resuelven numéricamente [T02, p. 24] [T02, p. 25]. El número de Reynolds compara efectos inerciales y viscosos: valores bajos se asocian con flujo laminar y altos con flujo turbulento [T02, p. 26].

Los modelos *lattice gas* toman un camino microscópico: partículas discretas se mueven sobre una retícula y obedecen reglas locales. El modelo FHP usa una retícula triangular con simetría hexagonal y seis velocidades hacia primeros vecinos [T02, p. 27] [T02, p. 28]. La simetría suficiente y colisiones que conservan masa y momento permiten recuperar Navier–Stokes en el límite macroscópico [B08, p. 9].

## Paso de simulación FHP

Cada nodo puede estar vacío u ocupado por varias partículas indistinguibles de masa unitaria. Un paso temporal tiene dos etapas:

1. **Propagación:** cada partícula avanza según su velocidad de retícula.
2. **Colisión:** las partículas cambian de velocidad según reglas locales [T02, p. 29] [B12, p. 5].

Las colisiones deben conservar masa y momento. En una colisión frontal de dos partículas, o una simétrica de tres, el momento total nulo debe mantenerse después de la colisión [T02, p. 30] [B12, p. 5] [B12, p. 6]. Los obstáculos pueden implementarse revirtiendo la dirección de la partícula (*bounce-back*) [T02, p. 34].

## Codificación y escala macroscópica

La implementación mostrada codifica seis direcciones, presencia de sólido y una elección aleatoria en ocho bits, por lo que hay 256 estados de celda y la colisión puede resolverse mediante una tabla de mapeo [T02, p. 32] [T02, p. 33]. Los campos macroscópicos se obtienen promediando muchas celdas y pasos temporales; la teórica propone como referencia bloques de al menos $16\times16$ celdas y 10 pasos [T02, p. 37].

## Relación con lattice Boltzmann

Los autómatas *lattice gas* fueron precursores del método lattice Boltzmann (LBM) [B12, p. 1]. En LBM se trabaja con funciones de distribución de partículas sobre velocidades discretas, en lugar de seguir ocupaciones booleanas individuales; las cantidades familiares —velocidad y presión— se recuperan como momentos macroscópicos. Esta abstracción facilita simular flujos y extender el método a otros problemas [B10, p. 1]. La bibliografía `B08` desarrolla el pasaje de LGCA a LBM, la aproximación BGK, el análisis multiescala y condiciones de contorno [B08, p. 4] [B08, p. 5].
