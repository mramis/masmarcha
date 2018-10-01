#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2018  Mariano Ramis

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
from collections import defaultdict
from contextlib import contextmanager
import json
from time import sleep
import logging

import cv2
import numpy as np

video_logger = logging.getLogger('masmarcha.video')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
video_logger.addHandler(ch)


class Video(object):

    def __init__(self, config):
        self.calibration = False
        self.cfg = config
        self.logger = logging.getLogger('masmarcha.video.Video')
        self.vid = None

    def __del__(self):
        if self.vid is not None and self.vid.isOpened():
            self.vid.release()

    def open_video(self, source):
        u"""Abre el archivo de video."""
        self.source = source
        self.vid = cv2.VideoCapture(source)

    def get_fps(self, correction=True):
        u"""Devuelve el número de cuadros por segundos.

        Esta función utiliza un valor de corrección "fpscorrection"que, por
        defecto tiene valor unitario. Este valor puede ser accedido a través de
        la configuración para ser modificado. Esta variable, existe porque en
        algunos videos el dato de fps no es el correcto.
        :return: cuadros por segundo.
        :rtype: int
        """
        if correction:
            correction = self.cfg.getfloat('video', 'fpscorrection')
            return self.vid.get(cv2.CAP_PROP_FPS) * correction
        else:
            return self.vid.get(cv2.CAP_PROP_FPS)

    def read_frame(self):
        u"""Lectura de cuadro de video.

        Este método tiene la posibilidad de modificar la distorsión de la
        imagen o cuadro de video si han sido cargados los parámetros de
        calibración.
        :return: Un vector de tres componentes, el primer valor es un boleano
        que dice que la lectura se ha realizado con éxito, el segundo es la
        posición del cuadro relativo al video, y el tercer es la imagen o
        cuadro de video.
        :rtype: tuple
        """
        ret, frame = self.vid.read()
        if self.calibration and ret:
            frame = self.undistort_frame(frame)
        return(ret, int(self.vid.get(cv2.CAP_PROP_POS_FRAMES)), frame)

    def load_distortion_params(self):
        u"""Carga los datos de calibración de la cámara."""
        if self.cfg.getboolean('video', 'calibrate'):
            calibrationpath = self.cfg.get('paths', 'currentcamera')
            if not os.path.isfile(calibrationpath):
                self.logger.warning(u"""
                    Calibración cancelada. No se encuentra:
                    {}""".format(calibrationpath))
                return
            calibration_setup = dict(np.load(calibrationpath).items())
            self.mtx = calibration_setup['mtx']
            self.dist = calibration_setup['dist']
            self.newmtx = calibration_setup['newcameramtx']
            self.calibration = True

    def undistort_frame(self, frame):
        u"""Corrige los valores de distorsión de la cámara.

        :param frame: arreglo de cuadro de video.
        :type frame: numpy.ndarray
        :return: cuadro de video.
        :rtype: numpy.ndarray
        """
        return(cv2.undistort(frame, self.mtx, self.dist, None, self.newmtx))

    def find_markers(self, frame):
        u"""Encuentra dentro del cuadro los contornos de los marcadores.

        :param frame: arreglo de cuadro de video.
        :type frame: numpy.ndarray
        :return: un vector que contiene, 1) nmarkers, el número de contornos
        que se encontraron; 2) una lista con los contornos propiamente dichos.
        :rtype: tuple
        """
        thresh = self.cfg.getfloat('video', 'thresh')
        dilate = self.cfg.getboolean('video', 'dilate')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, thresh, 255., cv2.THRESH_BINARY)[1]
        if dilate:
            kernel = np.ones((5, 5), np.uint8)
            binary = cv2.dilate(binary, kernel, iterations=3)
        contours = cv2.findContours(binary, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[1]
        return(len(contours), contours)

    def calculate_center_markers(self, contours):
        u"""Obtiene los centros de los contornos como un arreglo de numpy.

        :param contours: contornos de los objetos detectados en el cuadro de
        video.
        :param contours: list
        :return: arreglo de centros de los marcadores que se encontraron.
        :rtype: np.ndarray
        """
        def contour_center(contour):
            u"""Devuelve los centros de los contorno del marcador."""
            x, y, w, h = cv2.boundingRect(contour)
            return x + w/2, y + h/2
        list_of_contour_centers = [contour_center(c) for c in contours]
        return(np.array(list_of_contour_centers, dtype=np.int16)[::-1])

    def set_position(self, pos=0):
        """Modifica la posición de lectura (cuadro) dentro del video."""
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, pos)

    def calculate_distortion_params(self, source, cameraname):
        """Calcula los parámetros de distorisión interna de la cámara.

        :param source: Nombre del archivo de video que contiene la captura
        del tablero de ajedrez (damero).
        :type source: str
        :param cameraname: Nombre del archivo con el que se van a escribir
        los datos de distorsión.
        :type cameraname: str
        """
        w = self.cfg.getint('video', 'chessboardwidth')
        h = self.cfg.getint('video', 'chessboardheight')
        rate = self.cfg.getint('video', 'calibframerate')

        objp = np.zeros((w*h, 3), np.float32)
        objp[:, :2] = np.mgrid[0:w, 0:h].T.reshape(-1,2)

        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.

        self.open_video(source)
        read, pos, frame = self.read_frame()
        while read:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (w, h), None)
            if ret:
                objpoints.append(objp)
                imgpoints.append(corners)
            self.set_position(pos + rate)
            read, pos, frame = self.read_frame()
        self.vid.release()

        fw, fh = gray.shape[:2]
        __, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None)
        newcameramtx, __ = cv2.getOptimalNewCameraMatrix(
            mtx, dist, (w,h), 0, (w,h))

        dirpath = self.cfg.get('paths', 'calibration')
        destpath = os.path.join(dirpath, cameraname)
        np.savez(destpath, mtx=mtx, dist=dist, newcameramtx=newcameramtx)
        self.logger.info(u'Parámetros de distorsión calculados con éxito.')

class Explorer(Video):

    def __init__(self, filename, schema, config):
        super(Explorer, self).__init__(config)
        self.sch = schema
        self.walks = []
        self.logger = logging.getLogger('masmarcha.video.Explorer')
        self.open_video(filename)
        self.load_distortion_params()

    def jump_foward(self):
        u"""Se produce un salto en el cuadro de video actual.

        El video se adelanta tantos cuadros como lo indique el método
        Video.get_fps.
        """
        currpos = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
        self.set_position(currpos + self.get_fps(correction=False))

    def new_walk(self, startpos):
        u"""El método inicia una nueva caminata.

        :param startpos: posición inicial relativa al cuadro de video.
        :type startpos: int
        :return: Caminata.
        :rtype: Walk
        """
        walk = Walk(len(self.walks), startpos, self.source, self.sch, self.cfg)
        self.walks.append(walk)
        self.logger.info(u'Nueva caminata: %s' % str(walk))
        return walk

    def find_walks(self):
        u"""Encuentra las caminatas dentro de un video."""

        walking = False
        while True:
            ret, pos, frame = self.read_frame()
            if not ret:
                break
            n, contours = self.find_markers(frame)
            fullschema = (n == self.sch['n'])
            if not walking:
                if fullschema:
                    walk = self.new_walk(pos)
                    walk.add_framedata((fullschema, contours))
                    walking = True
                else:
                    self.jump_foward()
            else:
                walk.add_framedata((fullschema, contours))
                if n == 0:
                    walk.stop_walking(pos)
                    walking = False
        self.logger.info(u'Fin de la exploración')

    def preview(self, delay, pos=0):
        u"""Se muestran los objetos detectados en el video.

        :param delay: valor de retraso de imagen en segundos.
        :type delay: float
        """
        width = self.cfg.getint('video', 'framewidth')
        height = self.cfg.getint('video', 'frameheight')
        windowname = 'Preview: {}'.format(self.source)

        cv2.namedWindow(windowname, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowname, width, height)

        self.set_position(pos)
        ret, __, frame = self.read_frame()
        while ret:
            contours = self.find_markers(frame)[1]
            markers = self.calculate_center_markers(contours)
            for m in markers:
                cv2.circle(frame, tuple(m), 10, (0,0,255), -1)

            cv2.imshow(windowname, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            sleep(delay)
            ret, __, frame = self.read_frame()

        cv2.destroyAllWindows()


class Walk(Video):

    def __init__(self, id, startpos, source, schema, config):
        super(Walk, self).__init__(config)
        self.id = id
        self.logger = logging.getLogger('masmarcha.video.Walk')
        self.sch = schema
        self.source = source
        self.startpos = startpos
        self.videodata = []

    def __repr__(self):
        return 'W{0}'.format(self.id)

    def add_framedata(self, framedata):
        u"""Agrega información del cuadro de video.

        :param framedata: es un vector que contine: 1) valor boleano que indica
        si el cuadro tiene esquema completo de marcadores; 2) la lista de
        contornos de los marcadores, el arreglo del cuadro de video.
        :type framedata: tuple
        """
        fullschema, contours = framedata
        data = {'fullschema': fullschema,
                'contours': contours}
        self.videodata.append(data)

    def stop_walking(self, lastpos):
        u"""Pone fin al proceso de añadir información de cuadros a la caminata.

        :param lastpos: valor de posción del último cuadro relativo al
        video.
        :type lastpos: int
        """
        while True:
            data = self.videodata[-1]
            if not data['fullschema']:
                self.videodata.pop()
                lastpos += -1
            else:
                self.lastpos = lastpos
                break

    def calculate_frame_regions(self, markers):
        u"""Encuentra las regiones de interes del esquema de marcadores.

        Utiliza el parámetro "roiextrapixel" que el usuario puede modificar
        desde la configuración.
        :param markers: arreglo de marcadores.
        :type markers: numpy.ndarray
        :return: arreglo con los extremos superior izquierdo, e inferior
        derecho de las rois de interés definidas en el esquema.
        :rtype: numpy.ndarray
        """

        extra = self.cfg.getint('video', 'roiextrapixel')
        nrois = len(self.sch['markersxroi'].keys())
        regions = np.ndarray((nrois, 2, 2), dtype=np.int16)
        for r in sorted(self.sch['markersxroi']):
            bounds = self.sch['markersxroi'][r]
            roimin = np.min(markers[bounds[0]: bounds[-1]+1], axis=0) - extra
            roimax = np.max(markers[bounds[0]: bounds[-1]+1], axis=0) + extra
            regions[r] = np.array((roimin, roimax))
        return regions.flatten()

    def classify_markers(self):
        u"""Realiza la indentificación de los marcadores según el esquema.

        Se crean contenedores para almacenar los datos de los marcadores.
        """
        # Arreglo de marcadores definitivo.
        nframes = len(self.videodata)
        mrows = self.sch['n']
        mcols = 2
        self.markers = np.ndarray((nframes, mrows, mcols), dtype=np.int16)
        # Lista de marcadores de esquema incompleto, y lista de índices de
        # estos respectivos marcadores.
        self.umarkers = []
        self.umindex = []
        # Lista de índices de marcadores de esquema completo, y lista (después
        # arreglo), de regiones de interés de estos respectivos marcadores.
        self.fullmarkersix = []
        fullmarkersframerois = []

        for i, framedata in enumerate(self.videodata):
            markers = self.calculate_center_markers(framedata['contours'])
            if framedata['fullschema']:
                self.markers[i] = markers
                self.fullmarkersix.append(i)
                fullmarkersframerois.append(
                    self.calculate_frame_regions(markers))
            else:
                self.markers[i] = np.zeros((mrows, mcols), dtype=np.int16)
                self.umindex.append(i)
                self.umarkers.append(markers)
        self.fullmarkersframerois =  np.array(fullmarkersframerois)

    def interp_uncompleted_regions(self):
        u"""Interpola valores de regiones de interés.

        Se obtienen los datos de los vectores que determinan las regiones de
        interés dentro del cuadro de video, que corresponden a los índices de
        los marcadores de esquema incompleto."""
        # Ahora se completan las regiones de interés
        ncols = self.fullmarkersframerois.shape[1]
        self.uregions = np.empty((len(self.umindex), ncols), dtype=np.int16)
        for i in range(ncols):
            self.uregions[:, i] = np.interp(self.umindex, self.fullmarkersix,
                self.fullmarkersframerois[:, i])

    def fill_umarkers(self):
        u"""Identifica la posición de marcadores de esquema incompleto.

        La función utiliza las regiones de interés obtenidas previamente para
        disminuir la pérdida de datos."""
        self.lostregions = defaultdict(list)
        nrois = len(self.sch['markersxroi'].keys())

        for ii, umk, rois in zip(self.umindex, self.umarkers, self.uregions):
            rois = rois.reshape(nrois, 2, 2)
            for (r, mks), points in zip(self.sch['markersxroi'].items(), rois):
                xmin, ymin, xmax, ymax = points.flatten()
                xends = np.logical_and(umk[:, 0] > xmin, umk[:, 0] < xmax)
                yends = np.logical_and(umk[:, 1] > ymin, umk[:, 1] < ymax)
                region_markers = np.logical_and(xends, yends)
                if sum(region_markers) == len(mks):
                    self.markers[ii, mks[0]:mks[-1]+1] = umk[region_markers]
                else:
                    self.lostregions[r].append(ii)

    def sort_foot_markers(self):
        u"""ordena los marcadores de pie.

        En esta función se supone que el pie siempre se encuentra en el plano
        sagital.
        """
        expected_order = [-3, -2, -1]
        distances = np.ndarray((self.markers.shape[0], 3))
        labels = []
        for i, (jj, kk) in enumerate(zip(expected_order, (-2, -1, -3))):
            diff = self.markers[:, jj, :] - self.markers[:, kk, :]
            distances[:, i] = np.linalg.norm(diff, axis=1)
            labels.append(set([jj, kk]))

        for i, dist in enumerate(distances):
            alpha, beta, gamma = sorted(zip(dist, labels))
            ankle = alpha[1].intersection(gamma[1]).pop()
            foot1 = beta[1].intersection(alpha[1]).pop()
            foot2 = gamma[1].intersection(beta[1]).pop()

            new_order = [ankle, foot1, foot2]
            if new_order != expected_order:
                self.markers[i, expected_order] = self.markers[i, new_order]

    def interp_markers_positions(self):
        u"""Interpola la posición de los marcadores de esquema incompleto.

        Las posiciones que se identificaron como ausentes en el grupo de
        marcadores de esquema incompleto se interpolan en esta función.
        """
        XP = set(np.arange(self.markers.shape[0]))
        for r, findexs in self.lostregions.items():
            for row in self.sch['markersxroi'][r]:
                xp = list(XP.difference(findexs))
                xfp = self.markers[xp, row, 0]
                yfp = self.markers[xp, row, 1]
                self.markers[findexs, row, 0] = np.interp(findexs, xp, xfp)
                self.markers[findexs, row, 1] = np.interp(findexs, xp, yfp)

    def save_markers(self):
        u"""Se escribe en disco el arreglo de marcadores."""
        sessionpath = self.cfg.get('paths', 'session')
        walkpath = os.path.join(sessionpath, '{}.npy'.format(str(self)))
        with open(walkpath, 'wb') as fh:
            np.save(fh, self.markers)
        self.logger.info(u'Se escriben marcadores en disco: %s' % str(self))

    def display(self, delay):
        u"""Se muestran los objetos detectados en el video.

        :param delay: valor de retraso de imagen en segundos.
        :type delay: float
        """
        self.load_distortion_params()

        width = self.cfg.getint('video', 'framewidth')
        height = self.cfg.getint('video', 'frameheight')
        windowname = '{}: {}'.format(str(self), self.source)

        cv2.namedWindow(windowname, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowname, width, height)

        self.open_video(self.source)
        self.set_position(self.startpos - 1)

        np.random.seed(0)
        colors = [np.random.randint(0, 255, 3) for __ in range(self.sch['n'])]

        uregionspos = 0
        nrois = len(self.sch['markersxroi'].keys())
        for pos in range(self.lastpos - self.startpos):
            __, __, frame = self.read_frame()
            # Markers
            for i, m in enumerate(self.markers[pos]):
                col = [int(c) for c in colors[i]]
                cv2.circle(frame, tuple(m), 10, col, -1)
            # uncompleted regions
            if 'uregions' in self.__dict__.keys():
                if pos in self.umindex:
                    uregions = self.uregions[uregionspos].reshape(nrois, 2, 2)
                    for p0, p1 in uregions:
                        cv2.rectangle(frame, tuple(p0),tuple(p1), (0,255,0), 3)
                    uregionspos += 1

            cv2.imshow(windowname, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            sleep(delay)
        cv2.destroyAllWindows()

    def get_markers(self):
        self.classify_markers()
        self.interp_uncompleted_regions()
        self.fill_umarkers()
        self.sort_foot_markers()
        self.interp_markers_positions()
        return self.markers
