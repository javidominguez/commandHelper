# commandHelper

Proporciona un método alternativo de ejecutar scripts para personas que tienen dificultades al pulsar combinaciones de teclado complicadas.

### Modo de uso

Al pulsar NVDA+H se activa una capa de órdenes de teclado con las siguientes opciones: 

* Flechas izquierda y derecha para elegir una categoría. 
* Cualquier letra de la A a la Z para saltar a la categoría con esa inicial. 
* Flechas arriba y abajo para seleccionar una orden de la categoría elegida. 
* Enter para ejecutar la orden. 
* Mayúsculas+enter para ejecutar la órden como si se hubiera pulsado su combinación de teclas dos veces rápidamente. 
* Control+enter para ejecutar la órden como si se hubiese pulsado su combinación de teclas tres veces. 
* F1 para informar del gesto correspondiente a la órden seleccionada. 
*  Escape abandona la capa de órdenes y restaura la funcionalidad normal del teclado.  

### Configuración 

La combinación de teclas para activar el ayudante de órdenes se puede modificar en las preferencias de NVDA > Gestos de entrada. 

Algunas otras teclas pueden personalizarse en las preferencias de NVDA > Opciones > Ayudante de órdenes. 

* Activar/desactivar el uso de la tecla control para invocar el ayudante de órdenes. 
* Seleccionar con qué tecla se abandona el ayudante. 
* Seleccionar con qué tecla se anuncia el gesto asociado a una órden. 
* Activar/desactivar el manejo del ayudante a través del teclado numérico. 

#### Uso de la tecla control para invocar el ayudante 

Con esta opción activada se  invoca el ayudante pulsando cinco veces seguidas la tecla control. Esto es útil para personas a quienes  les resulta difícil pulsar combinaciones de varias teclas a la vez. Sin embargo, puede provocar en ocasiones la activación  involuntaria del ahyudante al pulsar la tecla control para otros usos, por ejemplo control+C y control+V para copiar y pegar. Para evitarlo hay que reducir la velocidad de repetición del teclado. Esto se hace en el panel de control de Windows. En el diálogo de preferencias del complemento hay un botón que pulsándolo lleva directamente a él. También se puede  abrir pulsando la tecla Windows+R y escribiendo control.exe keyboard en el cuadro ejecutar de Windows. En el control deslizante "Velocidad de repetición" hay que poner un valor lo más bajo posible. Poniéndolo a cero nos aseguramos de que no tendremos problemas pero dejará de  funcionar la activación del ayudante manteniendo pulsada la tecla control, lo que podría ser un inconveniente para algunos usuarios con movilidad reducida a quienes les cuesta hacer pulsaciones rápidas repetidas y prefieren activarlo así. No hay una configuración universal, cada usuario deberá encontrar la más adecuada para sus necesidades o preferencias. 

#### Teclado numérico 

Con esta opción activada se puede usar el ayudante con las teclas del teclado numérico. 

* 4 y6 para elegir una categoría. 
* 2 y 8 para seleccionar una orden de la categoría elegida. 
* 5 para informar del gesto correspondiente a la órden seleccionada. 
* Enter para ejecutar la orden. 
* Signo más para ejecutar la órden como si se hubiera pulsado su combinación de teclas dos veces rápidamente. 
* Signo menos para ejecutar la órden como si se hubiese pulsado su combinación de teclas tres veces. 
*  Suprimir abandona la capa de órdenes y restaura la funcionalidad normal del teclado.  

Nota sobre compativilidad: El complemento está preparado para funcionar con versiones previas de NVDA. La más antigua con la que se ha probado es la 2018.1 pero debería funcionar con otras aún más antiguas. Sin embargo no se proporcionará soporte futuro para problemas específicos que puedan surgir en esas versiones. 

