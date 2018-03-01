
# coding: utf-8

# In[1]:


# %matplotlib inline
import cv2
import numpy as np
import matplotlib.pyplot as plt


# In[2]:


# OK!

def findMarkers(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 240., 255., cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours[1]


def sliceHikes(buff, container, Nframes, expected_num):
    u"""Separa en caminatas el archivo.
    
    Cada caminata tiene como extremos cuadros que contienen exactamente
    el número de marcadores esperados, esto es para que en caso de tener
    que realizar una interpolación de datos, se encuentre el número total
    de marcadores.
    
    :param buff: Es el búfer de video que contiene la marcha.
    :type buff: cv2.VideoCapture
    :param container: Es el contenedor que va a almacenar los intervalos
    de los cuadros donde se encuentra cada caminata.
    :type container: collections.deque
    :param Nframes: Es el número de cuadros que se deben recorrer en el
    bucle de lectura.
    :type Nframes: int
    :param expected_num: Es el número de marcadores que se espera encontrar
    en el esquema completo.
    :type expected_num: int
    """
    hiking = False
    backward = 0
    for i in xrange(Nframes):
        __, frame = buff.read()
        n = len(findMarkers(frame))
        # Si el número de marcadores es cero, es porque todavia
        # no comenzó la caminata o acaba de terminar.
        if n == 0:
            # Si se encuentra dentro de la caminata, entonces un
            # índice cero señala el fin de la misma.
            if hiking:
                last = i - backward
                container.append((first, last))
                hiking = False
        else:
            # Si el número de marcadores es distinto de cero e
            # igual al número de marcadores, y la caminata aún
            # no empieza, entonces este es el primer cuadro que
            # se toma como activo.
            if n == expected_num:
                if not hiking:
                    first = i
                    hiking = True
                else:
                    backward = 0
            # Si no es el número esperado de marcadores entonces
            # puede suceder que los marcadores aún no consigan el
            # número esperado para iniciar la caminata, que estando
            # inciada, se pierdan marcadores en la lectura (ej.
            # ocultamiento) o que la caminata esté llegando a su fin.
            # En este último caso se debe recordar los últimos r
            # ciclos para volver al cuadro donde fueron hallados
            # el número correcto de marcadores.
            else:
                backward += 1


# In[ ]:


# Esquemas:!

global schema
# Nuevo esquema
# schema = {
#     'schema': (3, 2, 3),
#     'codes': (('M0', 'M1', 'M2'), ('M3', 'M4'), ('M5', 'M6', 'M7')),    
# }

#Anterior esquema
schema = {
    'schema': (2, 2, 3),
    'codes': (('M0', 'M1'), ('M2', 'M3'), ('M4', 'M5', 'M6')),
}

#Viejo esquema 
# schema = {
#     'schema': (1, 1, 2),
#     'codes': (('M0'), ('M1'), ('M2', 'M3')),   
# }


# In[13]:


# OK!

def markerCenter(contour):
    u"""Devuelve los centros de los contorno del marcador."""
    x, y, w, h = cv2.boundingRect(contour)
    xc = x + w/2
    yc = y + h/2
    return xc, yc


def identifyingMarkers(buff, Nframes, schema, **kwargs):
    u"""Se obtienen e identifican los arreglos de marcadores en el segmento de video.
    
    Esta función extrae los centros de marcadores ordenados en sentido descendente,
    de la forma en la que está diagramado el esquema de los mismos. La función
    también identifica los cudros y las regiones dentro del cuadro donde faltan
    datos, es decir, el número de marcadores que se encuentra no es el esperado.
    Devuelve un arreglo que contiene todos los marcadores del segmento de video que
    se le pasa como argumento, junto a una lista de cuadros y regiones que deben ser
    interpoladas.

    :param buff: stream de video para ser analizado.
    :type buff: cv2.VideoCapture
    :param Nframes: el número de cuadros que contiene el segmento de video.
    :type Nframes: int
    :param schema: es el vector que contiene la información de la cantidad de
    marcadores que contiene cada región.
    :type schema: tuple
    :return: arreglo con los arreglos de los centros del marcadores que se
    encontraron en el fragmento de video. Lista con los indices de los cuadros
    y las regiones de cada cuadro que contienen datos ausentes.
    :rtype: tuple
    """

    markers = []
    missing = []
    for i in xrange(Nframes):
        # Se lee el cuadro y se extraen los centros de los marcadores en
        # un arreglo de numpy.
        __, frame = buff.read()
        centers = np.array(map(markerCenter, findMarkers(frame)))[::-1]
        # Si el número de marcadores es el adecuado, entonces se almacena
        # en una variable temporal el arreglo de centros por si es
        # necesario en el siguiente cuadro rellenar un arreglo incompleto
        if len(centers) == sum(schema):
            # Se revisa el orden dentro de los marcadores de la región del
            # pie, puesto que en la lectura hecha por OpenCV puede haberse
            # invertido el orden de los marcadores de pie.
            centers = sortFootMarkers(centers, schema)
            temp = centers
        else:
            # Si el arreglo está incompleto entonces se rellena el arreglo
            # en las regiones donde falten marcadores. En este proceso se
            # buscan las regiones de los marcadores en el último arreglo
            # completo.
            roi = regions(temp, schema, **kwargs)
            centers, invschema = filling(centers, roi, schema)
            # se registran las regiones del cuadro donde faltaron marcadores
            # para que posteriormente sea interpoladas esas regiones.
            missing.append((i, invschema))
        markers.append(centers)
    return (np.array(markers), missing)


def sortFootMarkers(centers, schema):
    u"""Ordena los marcadores del grupo de tobillo."""
    # Por diagrama de marcadores, los que se encuentran en el pie son los
    # que están en la última región.
    i , j = (sum(schema) - schema[-1], sum(schema))
    # => foot = centers[i: j]
    # Como los marcadores que están en la región de tobillo son tres, y el
    # esquema dice que tienen que estar colocados céfalo-caudales, entonces
    # el de tobillo es el antepenúltimo, el de la parte posterior del pie
    # es el anteultimo, y el de la parte anterior del pié es el último.
    ankle, rearf, frontf = centers[i: j] 
    d0 = np.linalg.norm(ankle - rearf)
    d1 = np.linalg.norm(ankle - frontf)
    # Si la distancia entre el marcador de la parte posterior del pie y el tobillo
    # es mayor que la distancia entre la parte anterior del pie y el tobillo,
    # entonces el ciclo de la marcha se encuentra en un instante donde el marcador
    # de la parte anterior del pie está por encima del marcador que se encuentra
    # en la parte posterior del pie, y la función de encontrar los marcadores de
    # OpenCV los ha ordenado de forma distinta al que se plantea en el esquema y
    # se debe corregir.
    if d0 > d1:
        centers[i: j] = np.array((ankle, frontf, rearf))
    return centers

    
def regions(centers, schema, r=1.0):
    u"""Encuentra los centros de las regiones del esquema.
    
    Los marcadores se encuentran diagramados dentro de un esquema
    segun regiones. Esta función devuelve el centro de región junto
    con un radio. Estos dos valores se utilizan para delimitar un
    entorno donde es posible encontrar los marcadores e identificarlos en
    un grupo cuando el esquema no está completo, es decir, cuando
    se pierden marcadores.
    El valor que devuelve como centro es el valor centro de la región en
    la coordenada "y", es decir la altura del cuadro donde se encuentra
    la región.
    El valor que devuelve como radio, es la distancia que existe entre
    los marcadores de los extremos de la región, multiplicada por el valor
    del argumento r.
    
    :param centers: arreglo que contiene los centros de los marcadores.
    este arreglo es de rango completo, contienen el número de marcadores
    que espera el esquema.
    :type centers: np.ndarray
    :param schema: es el vector que contiene la información de la cantidad de
    marcadores que contiene cada región.
    :type schema: tuple
    :param r: es un escalar con el que se amplia el radio de la región.
    :type r: float
    :return: vectores con el centro y radio de cada una de las regiones
    diagramadas en el esquema.
    :rtype: list
    """
    regions = []
    i = 0
    # Se separa el arreglo de centros de marcadores según el esquema.
    for s in schema:
        roi = centers[i: i+s]
        # Se toman los valores "y" de los extremos del conjunto.
        # WARNING: Según este resultado, si el número generado
        # por el conjunto es 1, entonces no existe radio para
        # el entorno.
        y1, y2 = roi[(0, -1), 1]
        dh = (y2 - y1)
        roi_center = y1 + dh*.5
        regions.append((roi_center, dh*r))
        i += s
    return regions


def filling(centers, roi, schema):
    u"""Esta función completa el rango del arreglo de marcadores.
    
    Esta función se ejecuta cuando el rango de la matriz de marcadores
    es menor que el esperado según el esquema. Se analiza el arreglo
    por regiones, cuando en alguna de ellas existe menor cantidad de
    datos, entonces la región se rellena con valores aleatorios. Los
    valores de las regiones donde el número es el correcto se mantienen.
    
    :param centers: el arreglo de centro de marcadores.
    :type centers: np.ndarray
    :param roi: vector con valores de centro y radio de una región
    para crear un entorno de búsqueda.
    :type roi: list
    :param schema: vector con el número de marcadores esperados por
    región.
    :type schema: tuple
    :return: vector cuya primera componente es el arreglo de marcadores
    con rango completo, y segunda componete una lista de esquema
    incompleto.
    :rtype: tuple
    """
    # Las variables que se utilizan para indexar el arreglo de centros
    # marcadores. La variable j es secundaria a i, y se adapta a cuando
    # existe una región donde faltan datos.
    i, j = 0, 0
    # La variable replace es una lista que contiene el valor del vector
    # esquema al que le faltan datos.
    replace = []
    # el nuevo arreglo "vacio" que se devuelve para interpolar. Los
    # espacios que que no son ocupados por la región orignal es
    # basura, no fiarse de esos valores.
    resized_centers = np.empty((sum(schema), 2), dtype=int)
    for (c, r), s in zip(roi, schema):
        # En el arreglo rmark están los centros de los marcadores
        # que corresponden al entorno delimitado por la región.
        upper_limit = centers[:, 1] > c-r
        lower_limit = centers[:, 1] < c+r
        rmark = centers[np.logical_and(upper_limit, lower_limit)]
        if len(rmark) != s:
            # Si el número de marcadores dentro de la región no es el
            # esperado, entonces el arreglo queda "vacio" en ese lugar
            # y se reduce el número necesario en la variable secundaria
            # de indexación.
            replace.append(s)
            j = i - (s - len(rmark))
        else:
            # Los marcadores originales se mantienen.
            resized_centers[i: i+s] = centers[j: j+s]
        i += s
        j += s
    return (resized_centers, replace)


# In[ ]:


# OK!
import os
from collections import deque
from contextlib import contextmanager

# tengo que usar logging
import logging
logging.info('Encendiendo Motores')


class KinematicsEngine(object):
    u"""."""
    
    hikes = deque(maxlen=100)
    
    def __init__(self, filename, config):
        u"""."""
        self.filename = filename
        self.config = config

    @contextmanager
    def openVideo(self, path):
        u"""Context Manager para la apertura del video.
        
        Todo lo que se necesite hacer con la información del video
        debe de estar incluida dentro de la sentencia 'with' con la
        que se abre el video.
        
        :param path: La ruta del archivo de video.
        :type path: str
        """
        video = cv2.VideoCapture(path)
        yield video
        video.release()

    @contextmanager
    def openKinovea(self, path):
        u"""."""
        return NotImplemented

    def run(self):
        u"""! En desarrollo........"""
        ext = os.path.basename(self.filename).split('.')[-1]
        
        # Se el archivo de entrada es un video, entonces en el existen
        # al menos una caminata. El proceso de encontrar y extraer los
        # marcadores es mas complejo, y se necesita contexto distinto
        # al de un archivo de texto.
        if ext in self.config.get('Sys', 'videoext').split():
            with self.openVideo(self.filename) as stream:
                # Primero se buscan las caminatas dentro del video. Se
                # recorren todos los cuadros en búsqueda de caminatas.
                # A este proceso le llamo slicing.
                self.VideoProcess(stream, 'slice')
                # Si se obtuvieron caminatas, entonces el proceso
                # continua con la identificación y agrupación de los
                # marcadores. A este proceso le llamo grouping.
                self.VideoProcess(stream, 'group')

        # Si por el contrario el archivo es de texto, entonces se debe
        # comprobar que sea de kinovea, con el formato apropiado, y
        # el contexto de manejo y proceso tambien es distinto.
        elif ext in self.config.get('Sys', 'kinoveaext').split():
            manager = self.openKinovea
        
        # Si la extensión no correponde a un tipo de archivo soportado
        # entonces se lanza una excepción.
        else:
            raise Exception(u"MasMarcha: Formato de archivo NO soportado")

        # Se inicia el proceso de obtención de datos.
        # Esta parte no está clara del todo.

    def VideoProcess(self, buff, mode='slice', startFrame=0.0, endFrame=None):
        u"""Procesa el archivo de video que contiene la marcha.
        
        Se encarga de ejecutar el procesamiento de video que consta de:
         - Separar en caminatas el video. Cada caminata es una suceción
         de cuadros que contiene las coordenadas de los marcadores colo_
         cados en el cuerpo de la persona que camina frente a la cámara.
         - Extraer de cada caminata las coordenadas de los marcadores.
         - Obtener los ciclos que puedan o no hallarse dentro de cada
         caminata.
         - Corregir si es necesario el arreglo de marcadores, esto es
         interpolar y ordenar.
        """
        # En caso de que solo se quiera hacer una lectura de una porción del
        # video se pueden pasar los argumentos startFrame y endFrame. En esta
        # sección del código establece el cuadro donde debe iniciar el video
        # y cuantos cuadros debe durar.
        buff.set(cv2.CAP_PROP_POS_FRAMES, startFrame)    
        if endFrame:
            nframes = int(endFrame - startFrame)
        else:
            nframes = int(buff.get(cv2.CAP_PROP_FRAME_COUNT) - startFrame)

        # Existen dos funcionalidades distintas que se requieren de este método.
        # La primera es separar el video completo en caminatas. Para esto se
        # establece el modo en 'slice'.
        N = int(self.config.get('Kinematics', 'nmarkers'))
        if mode == 'slice':
            sliceHikes(buff, self.hikes, nframes, N)

        # La segunda extraer de cada caminata la información de ubicación de los
        # marcadores.
        elif mode == 'group':
            groupMarkers(buff, self.hikes, nframes, N)
        
        # No se contempla ninguna otra opción de modo en el procesamiento del video
        # por lo tanto se lanza una excepción en el caso no contemplado.
        else:
            raise Exception(u"Masmarcha: KinematicsEngine.VideoProcess(modo['slice' o 'group'])")


# In[ ]:


# main
from configparser import ConfigParser
from io import BytesIO

configuration_file = """
[Sys]
kinoveaext: txt
videoext: avi mp4

[Kinematics]
nmarkers: 7
"""


config = ConfigParser()
config.read_file(BytesIO(configuration_file))

path = '/home/mariano/Descargas/VID_20170720_132629833.mp4'  # Belen

K = KinematicsEngine(path, config)
K.run()
K.hikes


# In[ ]:


# path = '/home/mariano/Descargas/VID_20170720_132629833.mp4'  # Belen

# marks = []
# n = 7
# temp = np.zeros((7, 2), np.int8)
# vid = cv2.VideoCapture(path)
# fps = vid.get(cv2.CAP_PROP_FPS)
# ret, frame = vid.read()
# while ret:
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     binary = cv2.threshold(gray, 240., 255., cv2.THRESH_BINARY)[1]
#     dilation = cv2.dilate(binary, np.ones((5, 5), np.uint8), iterations=1)
#     contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     mark = np.array(map(center_of_square, contours[1]))
#     marks.append(mark)
# #     if mark.shape[0] == n:
# #         print('@'*3)
# #         if temp.all():
# #             print(np.linalg.norm(temp - mark, axis=1).round())
# #         temp = mark
#     ret, frame = vid.read()


# In[4]:


path = '/home/mariano/Descargas/VID_20170720_132629833.mp4'  # Belen
vid = cv2.VideoCapture(path)
for i in range(10):
    ret, frame = vid.read()
plt.imshow(frame)
plt.show()

centers = np.array(map(markerCenter, findMarkers(frame)))[::-1]
centers


# In[5]:


ROI = regions(centers, schema['schema'], 1.2)
for c, d in ROI:
    plt.imshow(frame)
    plt.axhline(y=c)
    plt.axhline(y=c-d, color='r')
    plt.axhline(y=c+d, color='r')
    
    plt.show()


# In[6]:


filling(centers, ROI, schema['schema'])


# In[7]:


modified = centers.copy()
modified = modified[(0,1, 2, 3, 4, 6), :]
modified


# In[12]:


filling(modified, ROI, schema['schema'])


# In[10]:


get_ipython().magic(u'pinfo np.ndarray')

