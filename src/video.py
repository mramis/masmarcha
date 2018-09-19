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
import logging
from time import sleep

import numpy as np
import cv2


def calculate_calibration_params(source, dest, chessboard, rate):
    w, h = chessboard
    objp = np.zeros((w*h, 3), np.float32)
    objp[:, :2] = np.mgrid[0:w, 0:h].T.reshape(-1,2)

    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    with open_video(source) as video:
        read, frame = video.read()
        while read:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (w, h), None)
            if ret:
                objpoints.append(objp)
                imgpoints.append(corners)
            next = video.get(cv2.CAP_PROP_POS_FRAMES) + int(rate)
            video.set(cv2.CAP_PROP_POS_FRAMES, next)
            read, frame = video.read()

    fw, fh = gray.shape[:2]
    __, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None)
    newcameramtx, __ = cv2.getOptimalNewCameraMatrix(
        mtx, dist, (w,h), 0, (w,h))

    np.savez(dest, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs,
             newcameramtx=newcameramtx, source=source,
             chessboard=chessboard, rate=rate)


class Video(object):

    def __init__(self, filename, cfg):
        self.vid = cv2.VideoCapture(filename)
        self.source = filename
        self.cfg = cfg
        self.calibration = False
        self.walks = []

    def __del__(self):
        self.vid.release()

    def get_fps(self):
        correction = self.cfg.getfloat('video', 'fpscorrection')
        return self.vid.get(cv2.CAP_PROP_FPS) * correction

    def read_frame(self):
        ret, frame = self.vid.read()
        if self.calibration and ret:
            frame = self.undistort_frame(frame)
        return(ret, self.vid.get(cv2.CAP_PROP_POS_FRAMES), frame)

    def jump_foward(self):
        currpos = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, currpos + self.get_fps())

    def load_calibration_params(self):
        """Carga los datos de calibración de la cámara."""
        calibrationpath = self.cfg.get('paths', 'currentcamera')
        if os.path.isfile(calibrationpath):
            calibration_setup = dict(np.load(calibrationpath).items())
            self.mtx = calibration_setup['mtx']
            self.dist = calibration_setup['dist']
            self.newmtx = calibration_setup['newcameramtx']
            self.calibration = True

    def undistort_frame(self, frame):
        return(cv2.undistort(frame, self.mtx, self.dist, None, self.newmtx))

    def new_walk(self, startposition):
        walk = Walk(len(self.walks), startposition, self.source, self.cfg)
        self.walks.append(walk)
        return(walk)

    def find_markers(self, frame):
        u"""Encuentra dentro del cuadro los contornos de los marcadores.

        :return: nmarkers, el número de contornos que se encontraron.
        :rtype: int
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

        :return: arreglo de centros de los marcadores que se encontraron.
        :rtype: np.ndarray
        """
        def contour_center(contour):
            u"""Devuelve los centros de los contorno del marcador."""
            x, y, w, h = cv2.boundingRect(contour)
            return x + w/2, y + h/2
        list_of_contour_centers = [contour_center(c) for c in contours]
        return(np.array(list_of_contour_centers, dtype=np.int16)[::-1])

    def find_walks(self):
        u"""Encuentra las caminatas dentro de un video."""
        self.walks = []
        schema = json.load(open(self.cfg.get('paths', 'schema')))
        n = sum(schema['schema'])
        walking = False
        while True:
            ret, pos, frame = self.read_frame()
            if not ret:
                break
            nmarkers, markers_contours = self.find_markers(frame)
            fullschema = (nmarkers == n)
            if not walking:
                if fullschema:
                    walk = self.new_walk(pos)
                    walk.add_framedata((fullschema, markers_contours, frame))
                    walking = True
                else:
                    self.jump_foward()

            else:
                walk.add_framedata((fullschema, markers_contours, frame))
                if nmarkers == 0:
                    walk.stop_walking(pos)
                    walking = False

    def preview(self, delay):
        width = self.cfg.getint('video', 'framewidth')
        height = self.cfg.getint('video', 'frameheight')
        windowname = 'Preview: {}'.format(self.source)

        cv2.namedWindow(windowname, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowname, width, height)

        ret = True
        while ret:
            ret, pos, frame = self.read_frame()
            contours = self.find_markers(frame)[1]
            markers = self.calculate_center_markers(contours)
            for m in markers:
                cv2.circle(frame, tuple(m), 15, (0,0,255), -1)

            cv2.imshow(windowname, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            sleep(delay)


class Walk(object):

    def __init__(self, id, startposition, source, cfg):
        self.id = id
        self.cfg = cfg
        self.source = source
        self.startpos = startposition
        self.endpos = None
        self.videodata = []

    def __repr__(self):
        return 'W{0}'.format(self.id)

    def add_framedata(self, framedata):
        """Agrega un cuadro a la caminata."""
        fullschema, markers_contours, frame = framedata
        data = {'fullschema': fullschema,
                'contours': markers_contours,
                'frame': frame}
        self.videodata.append(data)

    def stop_walking(self, lastposition):
        """Pone fin al proceso de añadir cuadros a la caminata."""
        while True:
            frame = self.videodata[-1]
            if not frame['fullschema']:
                self.videodata.pop()
                lastposition += -1
            else:
                self.lpos = lastposition
                break

    def calculate_center_markers(self, contours):
        u"""Obtiene los centros de los contornos como un arreglo de numpy.

        :return: arreglo de centros de los marcadores que se encontraron.
        :rtype: np.ndarray
        """
        def contour_center(contour):
            u"""Devuelve los centros de los contorno del marcador."""
            x, y, w, h = cv2.boundingRect(contour)
            return x + w/2, y + h/2
        list_of_contour_centers = [contour_center(c) for c in contours]
        return(np.array(list_of_contour_centers, dtype=np.int16)[::-1])

    def calculate_frame_regions(self, markers):
        """Encuentra las regiones de interes del esquema de marcadores.

        Utiliza el parámetro "roiextrapixel" que el usuario puede modificar
        desde la configuración.
        """
        # NOTE: MODIFICAR ESQUEMA
        schema = json.load(open(self.cfg.get('paths', 'schema')))

        extra = self.cfg.getint('video', 'roiextrapixel')
        regions = []
        for i, j in schema['slices']:
            regions.append(
                np.array((np.min(markers[i: j], axis=0) - extra,
                          np.max(markers[i: j], axis=0) + extra)))
        return(np.array(regions).flatten())

    def classify_markers(self):
        """Identifica los cuadros completos de la caminata"""
        self.markers = np.ndarray((len(self.videodata), 7, 2), dtype=np.int16)  # FIXME: HARDCORE
        self.umarkers = []
        self.umarkersix = []
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
                self.markers[i] = np.zeros((7, 2), dtype=np.int16)
                self.umarkersix.append(i)
                self.umarkers.append(markers)
        self.fullmarkersframerois =  np.array(fullmarkersframerois)

    def interp_uncompleted_regions(self):
        # Ahora se completan las regiones de interés
        ncols = self.fullmarkersframerois.shape[1]
        self.uregions = np.empty((len(self.umarkersix), ncols), dtype=np.int16)
        for i in range(ncols):
            self.uregions[:, i] = np.interp(self.umarkersix,
                self.fullmarkersix, self.fullmarkersframerois[:, i])

    def fill_umarkers(self):
        # NOTE: MODIFICAR ESQUEMA
        schema = json.load(open(self.cfg.get('paths', 'schema')))

        self.lostregions = defaultdict(list)

        # Ahora se completa cada uframe.
        for ii, markers, regions in zip(self.umarkersix, self.umarkers, self.uregions):
            regions = regions.reshape(3, 2, 2)  # FIXME: HARDCORE
            for jj, (m, reg) in enumerate(zip((2, 2, 3), regions)):  # FIXME: HARDCORE
                xmin, ymin, xmax, ymax = reg.flatten()
                xends = np.logical_and(markers[:, 0] > xmin, markers[:, 0] < xmax)
                yends = np.logical_and(markers[:, 1] > ymin, markers[:, 1] < ymax)
                region_markers = np.logical_and(xends, yends)
                if sum(region_markers) == m:
                    s = schema['slices'][jj]  # FIXME: UGLY
                    self.markers[ii, s[0]:s[1]] = markers[region_markers]
                else:
                    self.lostregions[jj].append(ii)

    def sort_foot_markers(self):
        u"""ordena los marcadores de pie.

        En esta función se supone que el pie siempre se encuentra en el plano
        sagital.
        """
        # FIXME: HARDCORE
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
        u"""Interpola la posición de los marcadores"""
        regions_mrows = {
            0: (0, 1),
            1: (2, 3),
            2: (4, 5, 6)}

        XP = set(np.arange(self.markers.shape[0]))
        for r, frame_indexs in self.lostregions.items():
            for row in regions_mrows[r]:
                xp = list(XP.difference(frame_indexs))
                xfp = self.markers[xp, row, 0]
                yfp = self.markers[xp, row, 1]
                self.markers[frame_indexs, row, 0] = np.interp(frame_indexs, xp, xfp)
                self.markers[frame_indexs, row, 1] = np.interp(frame_indexs, xp, yfp)

    def get_markers(self):
        self.classify_markers()
        self.interp_uncompleted_regions()
        self.fill_umarkers()
        self.sort_foot_markers()
        self.interp_markers_positions()
        return self.markers
