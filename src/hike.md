# Hike (caminata).

La clase Hike, fue diseñada tomando como modelo un esquema de 7 marcadores
colocados sobre el plano sagital de la persona que camina frente a una cámara.
La clase recibe los marcadores por grupos, y los almacena. Estos grupos de
marcadores pueden estár completos o incompletos, puesto que no siempre es
posible detectar todo el conjunto de marcadores, en este caso 7. Cada conjunto
de grupo es almacenado con su índice de cuadro (dentro del vídeo).
Una vez que recibió toda la caminata, completa los datos faltantes a través de
un proceso de interpolación lineal, separa la caminata en ciclos, y obtiene los
parámetros de marcha por cada ciclo.
Los parámetros que genera son: Cinemática de ángulos de cadera, rodilla y
tobillo, longitud de zancada, tiempo de ciclo, porcentaje de fases de ciclo,
velocidad media, y cadencia.
Luego son posibles calcular puntajes (scores) añadidos como el ECM.

## init:
Recibe dos parámetros:
    - FPS, cuadros por segundo. Se utiliza para el calculo de los tiempos a
    través de la cantidad de cuadros de datos.
    - Métricas, se refiere a medidas de conversión de píxeles a metros. Estas
    medidas se obtienen al principio del vídeo.

`Los métodos que se describen a continuación son utilizados por la clase que
procesa el vídeo para la adquisición de los marcadores colocados en la persona.
Su empleo se describe en la sección de esa clase.`

### add_markers_from_videoframe:
Recibe dos parámetros:
    - index, es el número de cuadro dentro del vídeo.
    - groups, conjunto de grupos *según el esquema de colocación*.
Este método agrega el conjunto de grupos en un arreglo (dict) junto con el
índice, del cuadro de vídeo.

### add_index_to_interpolate:
Recibe dos parámetros:
    - index, es el número de cuadro dentro del vídeo.
    -bgroups, es un conjunto de boleanos que indica en cuál de los grupos
    existen datos faltantes, que por lo tanto, tienen que ser arreglados por
    interpolación.
El arreglo es también un diccionario.

### rm_last_added_data:
Recibe un parámetro:
    - n, es el número de cuadros que deben ser eliminados del arreglo de
    marcadores, y del arreglo de datos a interpolar.

`Los métodos que se describen a continuación son utilizados por la misma clase
Hike para el proceso de los marcadores (agrupados).`

### fill_groups:
Este método toma cada conjunto de marcadores por cuadro, y cada grupo por
conjunto. Entonces revisa que el número de marcadores que existe en el conjunto
se igual al número esperado *según el esquema*. Si no lo es, reemplaza el grupo
de marcadores por un arreglo de ceros, con la misma dimensión que la esperada.
Cabe mencionar que el tipo de arreglo de grupo es un arreglo de Numpy.

### get_direction:
Recibe dos parámetros:
    - mod, es el modo de obtener la dirección de movimiento durante la caminata.
    Son dos las posibilidades. Modo 0, obtiene de alguno de los marcadores, del
    grupo que sea, la posición inicial y final de la caminata en su componentes
    X, luego la diferencia de las dos, determina la dirección según su signo.
    Este modo supone que ha existido algún tipo de desplazamiento en el espacio.
    Modo 1, obtiene la dirección tomando como parámetro la velocidad de
    desplazamiento del marcador de tobillo, para ser más específico de su
    componente en y *(cada esquema debe especificar cuál es este marcador)*, y
    obteniendo la dirección del pié cuando la velocidad de este desplazamiento
    es igual a cero. Este modo está pensado para cuando la marcha se realiza
    sobre una cinta (treadmill). Aún no se comprueba su eficiencia.
    - ret, boleano que indica si se desea el valor de dirección de retorno.

### sort_foot:
Este método solo ordena los marcadores del grupo de tobillo, cuando el *esquema*
proporciona tres marcadores en este grupo, y uno de ellos es de tobillo, el
otro de retropié, y otro de antepié. *Está claro que debe revisarse el método
para la utilización de un esquema que tenga este grupo con distinta
dispocisión.*
Ordena los marcadores del grupo de tobillo. Cuando el origen de los marcadores
es de vídeo, los marcadores del grupo de tobillo, pueden verse desordenados,
es decir que no siempre, la clase que los obtiene, los devuelve en el mismo
orden.

### interpolate:
Realiza una interpolación lineal de los datos faltantes tomando como extremos,
intervalos obtenidos según los índices entregados al arreglo de datos a
interpolar. Es preciso que estén ordenados todos los datos ara realizar este
proceso (ver anterior).

### fix_groups:
Lleva a cabo los procesos que involucran rellenar los grupos con datos, ordenar
los marcadores e interpolar los datos faltantes.

### cycle_definition:
Utiliza los marcadores de pie (que en este *esquema* son dos), para determinar
los límites de ciclo dentro de la caminata. Utiliza la velocidad del los
marcadores de pie, en sus dos componentes, para establecer el apoyo y el
balanceo. Existe un nivel de umbral establecido que puede ser modificado por el
usuario para poder determinar el límite de velocidad que se considera apoyo.
Esto es, que aunque teóricamente en el apoyo no existe velocidad de marcadores,
en la práctica, existen variaciones debido a la forma de adquisición de vídeo.
*Es fundamental la estabilidad de la cámara, y de foco mientras se filma a la
persona caminando*.
Luego se toman los parámetros espaciotemporales utilizando los parámetros de
referencia métrica, el valor de fps, y los obtenidos de los ciclos.

### joints_definition:
*Utiliza fuertemente el esquema de marcadores*. Define los segmentos que existen
entre los marcadores, y calcula los ángulos de las articulaciones definidas por
el esquema.

`Los siguientes métodos fueron diseñados para presentar los datos obtenidos de
forma sencilla.`

### markers_as_dataframe, joints_as_dataframe, spatiotemporal_as_dataframe:
Estos métodos devuelven los datos señalados en una estructura Pandas.DataFrame.
Están también fuertemente estructurados por el *esquema de marcadores*.
