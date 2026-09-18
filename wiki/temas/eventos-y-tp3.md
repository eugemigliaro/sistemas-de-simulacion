# Simulación dirigida por eventos y TP3

## Esquema de simulación

En una simulación dirigida por paso temporal el estado se actualiza cada
$\Delta t$ fijo. En una simulación dirigida por eventos el reloj avanza hasta el
próximo suceso que modifica el estado, por ejemplo una colisión [T03, p. 2]. Este
enfoque resulta adecuado cuando los choques pueden tratarse como instantáneos,
el tiempo de vuelo es mucho mayor que la duración del contacto y la densidad es
media o baja [T03, p. 5].

Para discos rígidos sin fuerzas externas, cada partícula se mueve en línea recta
y con velocidad constante entre colisiones. El ciclo básico es:

1. definir posiciones y velocidades iniciales sin superposiciones;
2. calcular todos los tiempos de choque relevantes y elegir el menor;
3. avanzar el sistema exactamente hasta ese instante;
4. guardar el estado cuando corresponda;
5. actualizar únicamente las velocidades de las partículas involucradas;
6. repetir desde el cálculo del próximo evento [T03, p. 6] [T03, p. 9] [T03, p. 10].

Una implementación puede recalcular los eventos después de cada choque o usar
una cola de prioridad. En el segundo caso, una colisión cambia las trayectorias
futuras de sus participantes y deja eventos previamente agendados inválidos. La
referencia externa propone guardar el contador de colisiones de cada partícula
al crear el evento y descartarlo al extraerlo si alguno de esos contadores cambió
[B16, p. 1] [B16, p. 4]. Esta es una estrategia de implementación posible, no un
requisito explícito del TP3.

## Predicción de colisiones

Para paredes verticales en $x_{p1}<x_{p2}$, una partícula de radio $R$, posición
$x$ y velocidad $v_x$ tiene los tiempos candidatos

$$
t_c=\frac{x_{p2}-R-x}{v_x}\quad(v_x>0),
\qquad
t_c=\frac{x_{p1}+R-x}{v_x}\quad(v_x<0),
$$

con expresiones análogas para las paredes horizontales [T03, p. 12]. Sólo se
consideran tiempos futuros y finitos.

Para dos partículas se definen
$\Delta\mathbf r=\mathbf r_j-\mathbf r_i$,
$\Delta\mathbf v=\mathbf v_j-\mathbf v_i$ y
$\sigma=R_i+R_j$. Si $\Delta\mathbf v\cdot\Delta\mathbf r\geq0$, las partículas
no se están acercando. En caso contrario se calcula

$$
d=(\Delta\mathbf v\cdot\Delta\mathbf r)^2
 -(\Delta\mathbf v\cdot\Delta\mathbf v)
  (\Delta\mathbf r\cdot\Delta\mathbf r-\sigma^2).
$$

Si $d<0$ no existe una colisión futura; en el resto de los casos,

$$
t_c=-\frac{\Delta\mathbf v\cdot\Delta\mathbf r+\sqrt d}
{\Delta\mathbf v\cdot\Delta\mathbf v}.
$$

La construcción surge de imponer que la distancia entre centros en el contacto
sea $R_i+R_j$ y resolver la ecuación cuadrática resultante [T03, p. 13]
[T03, p. 14] [B16, p. 2] [B16, p. 3]. En código hay que tratar explícitamente
velocidades relativas nulas, raíces apenas negativas por redondeo y eventos
simultáneos o casi simultáneos.

## Resolución de colisiones elásticas

Una colisión con una pared vertical cambia $(v_x,v_y)$ por $(-v_x,v_y)$; una
pared horizontal produce $(v_x,-v_y)$ [T03, p. 19]. Para dos partículas de masas
posiblemente distintas, el impulso actúa sobre la línea que une sus centros y se
aplica con signos opuestos a ambas velocidades. La actualización conserva
momento lineal y energía cinética cuando el choque es elástico [T03, p. 20]
[B16, p. 3].

Un obstáculo fijo puede modelarse como una partícula de masa infinita. La
teórica también expresa el rebote mediante un cambio a coordenadas normal y
tangencial, una matriz de restitución y la rotación de regreso al sistema global
[T03, p. 21] [T03, p. 22] [T03, p. 23] [T03, p. 24]. Para el TP3 todas las
colisiones son elásticas, por lo que no debe introducirse pérdida de energía
[TP03, p. 2].

## Desplazamiento cuadrático medio y difusión

La teórica relaciona el desplazamiento cuadrático medio de una coordenada con el
coeficiente de difusión mediante $\langle z^2\rangle=2Dt$ y pide estimar la
pendiente con varios tiempos y varias realizaciones [T03, p. 25]. El TP3 pide
promediar el DCM sobre todas las partículas móviles, frescas y usadas, ajustar
linealmente para obtener $D$ y comparar ese coeficiente con el tiempo medio
$\langle t_{90}\rangle$ [TP03, p. 3]. La convención dimensional del DCM queda
registrada como duda porque el sistema del TP es bidimensional.

## Contrato del TP3: Billar-Metegol

El dominio es una mesa rectangular de $L=1{,}20\ \mathrm m$ por
$W=0{,}68\ \mathrm m$. En el centro de cada pared corta hay un arco de longitud
$d=0{,}20\ \mathrm m$. Dentro se colocan $K>0$ obstáculos circulares fijos,
íntegramente contenidos y sin solaparse [TP03, p. 2] [TP03, p. 3].

Las partículas tienen radio $r=0{,}0175\ \mathrm m$, masa
$m=0{,}025\ \mathrm{kg}$ y rapidez inicial $v_0=1\ \mathrm{m/s}$, con posiciones
aleatorias válidas y ángulos uniformes en $[0,2\pi)$. Todas comienzan frescas. El
primer contacto de una partícula con un arco suma un gol y la marca como usada;
continúa moviéndose, pero no puede volver a sumar. Así,

$$
F_u(t)=\frac{N_g(t)}{N},
$$

y $t_{90}$ es el primer tiempo en que $F_u$ alcanza $0{,}9$. El objetivo es
encontrar y justificar la configuración que minimiza
$\langle t_{90}\rangle$ [TP03, p. 2] [TP03, p. 3].

El estudio solicitado tiene tres partes experimentales:

- sin obstáculos, medir el tiempo de ejecución hasta $t_f=30\ \mathrm s$ para
  distintos $N$, con al menos diez realizaciones y barras de desvío estándar;
- con $N=100$, explorar configuraciones de obstáculos usando al menos cinco
  realizaciones por punto, comparar $\langle t_{90}\rangle$ con la mesa vacía y
  justificar el método de búsqueda;
- estimar $D$ para la mesa vacía y las configuraciones estudiadas y analizar su
  posible correlación con $\langle t_{90}\rangle$ [TP03, p. 3].

Para la competencia se ejecutan cinco realizaciones con $N=100$ y
$t_{\max}=100\ \mathrm s$. Gana el menor $\langle t_{90}\rangle$; si no se alcanza
el 90 %, esas configuraciones se ordenan al final por el número medio de goles a
$t_{\max}$. El archivo de configuración contiene una línea `xk yk Rk` por
obstáculo y debe coincidir con la configuración usada en vivo [TP03, p. 3].

## Entregables y lista de comprobación

La entrega indicada es el 28 de septiembre de 2026 a las 13:00. Incluye una
presentación oral de 13 minutos, su PDF con enlaces explícitos a las animaciones,
un ZIP menor a 100 KB con sólo el motor final y un archivo de texto con la
configuración de obstáculos. El simulador debe escribir texto y la animación
debe leerlo como módulo independiente [TP03, p. 1].

- el motor escribe solo el estado del sistema (posiciones, velocidades y eventos); $F_u(t)$, $t_{90}$ y el DCM se calculan en un post-proceso aparte, como exigió la devolución del TP2 [COR02] [T00, p. 20];
- listar como parámetros solo los que cambian la salida del sistema; $t_f$, $t_{\max}$ o el número de realizaciones son configuración, no parámetros [COR02];
- validar ausencia de solapamientos iniciales y obstáculos admisibles;
- separar predicción, avance y resolución de eventos;
- rechazar eventos pasados, imposibles o invalidados;
- controlar conservación de energía y momento en colisiones elásticas;
- guardar suficientes estados para análisis y animación sin saturar el disco;
- repetir con semillas independientes y declarar el significado de las barras;
- calcular $t_{90}$ por realización antes de promediar;
- incluir la mesa vacía como referencia;
- entregar exactamente la configuración que se usará en la competencia.
