
# coding: utf-8

# In[1]:


get_ipython().magic(u'matplotlib inline')
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


# In[17]:


# Este es bloque es está en desarrollo!

def centroid(x, y, w, h):
    u"""Calula el centro de una caja.

    :param x, y: Vértice superior izquierdo.
    :param w, h: Ancho y Alto de la caja.
    """
    xc = x + w/2
    yc = y + h/2
    return xc, yc


def center_of_square(contour):
    u"""Centro de cuadrado.

    Devuelve el centro del cuadrado que encierra los marcadores de la image.
    :param contour: objeto contorno del marcador.
    :type contour: cv2.findContours
    :return: int, int: (x, y) centro del contorno.
    :rtype: tuple
    """
    return centroid(*cv2.boundingRect(contour))


def roi_center(array, amp=1.4):
    u"""Región de interes.

    Calcula límites de región según el arreglo de posiciones y la amplitud que
    se pasa en el argumento. Toma las fronteras verticales del arreglo y los
    amplia según el factor amplitud.
    :param array: grupo de centros de marcadores(posiciones).
    :type array: np.ndarray
    :return: int, int: (ya, yb) los limites superior e inferior del grupo,
    ampliados.
    :rtype: tuple
    """
    y1 = array[0][1]
    y2 = array[-1][1]
    dy = (y1 - y2)*amp
    center = (y1 + y2) / 2
    return(center - dy, center + dy)


# def knee_roi_center(array, age, amp=1.4):  # FUTURO: Cuando tengamos video con marcadores en vertex.
#     u"""Calcula el centro de la región de interés de.

#     Calcula límites de región según el arreglo de posiciones y la amplitud que
#     se pasa en el argumento. Toma las fronteras verticales del arreglo y los
#     amplia según el factor amplitud.
#     :param array: grupo de centros de marcadores(posiciones).
#     :type array: np.ndarray
#     :return: int, int: (ya, yb) los limites superior e inferior del grupo,
#     ampliados.
#     :rtype: tuple
#     """
#     height_div = {'child': (6.0, 5.5), 'adult': (8.0, 6.5)}[age]
#     ytop = array[0][1]
#     ybottom = array[-1][1]
#     dy = (ybottom - ytop) / height_div[0]
#     center = ytop - dy * height_div[1]
#     return(center - dy, center + dy)



def grouping(markers, n_expected, kroi=False):
    u"""Agrupamiento.

    Esta función agrupa los centros de marcadores, con el objetivo de disminuir
    los datos que se pierden y por tanto, los que tienen que ser interpolados.
    Los tres grupos son G0: los marcadores de tronco y muslo superior, G1: los
    marcadores de la región de rodilla, y G2: los marcadores de la región de
    tobillo.
    La función acepta como argumento opcional la zona de interes de la rodilla
    (ver roi_center) que establece los grupos cuando el número de marcadores es
    distinto al esperado.
    :param markers: marcadores(centros) obtenidos del proceso del videoframe.
    :type markers: np.ndarray
    :param n_expected: (int, int, int): arreglo con el número de marcadores
    esperados por grupos.
    :type n_expected: tuple
    :return: (list, tuple): lista de booleanos que indica los grupos que tienen
    que ser interpolados, y tupla con los grupos (G0, G1, G2) siendo Gi un
    np.ndarray.
    :rtype: tuple
    """
    if kroi:
        Y = markers[:, 1]
        upp = markers[Y < kroi[0]]
        mid = markers[np.logical_and(Y > kroi[0], Y < kroi[1])]
        low = markers[Y > kroi[1]]
    else:
        upp = markers[5:, :]
        mid = markers[3:5, :]
        low = markers[:3, :]
    n_obtained = (upp.shape[0], mid.shape[0], low.shape[0])
    boolean_interpolate = [a != b for a, b in zip(n_expected, n_obtained)]
    return(boolean_interpolate, (G0, G1, G2))

                
def groupMarkers(buff, container, Nframes, expected_num):
    u"""DESARROLLANDO."""
    
    for i in xrange(Nframes):
        __, frame = buff.read()
        contours = findMarkers(frame)
        N = len(contours)
        markers = np.array(map(center_of_square, contours))
        if N == expected_num:
            array = grouping(markers, expected_num)
            kneezone = roi_center(markers)
        else:
            array = grouping(markers, expected_num, kneezone)
        print array


# In[18]:


# OK!
import os
from collections import deque
from contextlib import contextmanager

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
            manager = self.openVideo
            process = self.VideoProcess
        
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
        with manager(self.filename) as stream:
            process(stream)
            process(stream, 'group', startFrame=self.hikes[0][0], endFrame=self.hikes[0][1])

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


# In[19]:


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





# In[3]:


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

