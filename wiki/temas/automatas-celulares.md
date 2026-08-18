# Autómatas celulares

## Definición y evolución

Un autómata celular discretiza el espacio en una grilla de celdas. Cada celda toma uno entre un número finito de estados y todas se actualizan sincrónicamente mediante una regla determinista, uniforme en tiempo y espacio, que depende de un vecindario local [T02, p. 2] [T02, p. 3]. En una dimensión, si hay $k$ estados y la regla mira un radio $r$, existen $k^{2r+1}$ configuraciones locales posibles y $k^{k^{2r+1}}$ reglas; para $k=2$ y $r=1$ resultan 256 reglas elementales [T02, p. 7].

La regla puede escribirse como un mapeo no lineal desde el estado de la celda y sus vecinas hacia el estado siguiente. El material distingue, entre otras, reglas totalistas, simétricas y legales [T02, p. 6] [T02, p. 8].

## Vecindades en dos dimensiones

Para una celda $(i,j)$ y alcance $r$:

- la vecindad de von Neumann incluye $(k,l)$ tales que $|k-i|+|l-j|\le r$;
- la vecindad de Moore incluye $(k,l)$ tales que $|k-i|\le r$ y $|l-j|\le r$ [T02, p. 12] [T02, p. 13].

Las condiciones iniciales y de contorno completan la especificación de una simulación. Por ejemplo, pueden elegirse estados iniciales aleatorios o predeterminados y contornos periódicos o no periódicos [T02, p. 16].

## Juego de la Vida

El Juego de la Vida de Conway usa estados viva/muerta y vecindad de Moore de alcance 1. Una celda viva sobrevive con dos o tres vecinas vivas; una muerta nace con exactamente tres [T02, p. 15]. Aunque las reglas son locales y simples, aparecen estructuras estáticas, periódicas y móviles [T02, p. 17] [T02, p. 19].

## Complejidad emergente

La teórica presenta cuatro comportamientos cualitativos para autómatas unidimensionales: desaparición, tamaño finito estable, crecimiento indefinido a velocidad fija y crecimiento/contracción irregular [T02, p. 9]. La bibliografía de Wolfram formula una clasificación emparentada: estado homogéneo, estructuras estables o periódicas, caos aperiódico y estructuras localizadas complejas; en la clase 4 algunas estructuras almacenan y transmiten información y pueden sostener computación universal [B13, p. 2] [B13, p. 4] [B13, p. 6].

Esto ejemplifica comportamiento emergente: componentes discretos idénticos, con reglas locales sencillas, pueden producir patrones globales complejos que no se leen directamente de una celda aislada [B13, p. 2].
