#!/usr/bin/env python
# coding: utf-8

"""Esquemas de marcadores que se entregan por defecto."""

# Copyright (C) 2017  Mariano Ramis

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

"""
Esquema.
========

Modelo explicativo:
-------------------

schema_n = {
    "ix_groups": list, contiene los indices de los grupos del esquema. Se
    ordenan de superior a inferior. Ejemplo [0, 1, 2] = ['tronco', 'rodilla',
    'pie'].
    "num_markers": list, número de marcadores que se espera por cada grupo, por
    lo la lista tiene el mismo número de elementos que la lista de indices.
    "ft_group": int, indica cuál es el grupo de marcadores en el que se incluye
    el pié. Este grupo es especial porque se utliza para determinar la
    dirección de movimiento, situaciones de apoyo, parámetros y
    espaciotemporales.
    "ank_marker": int, es el índice del marcador de tobillo (maléolo), dentro
    del grupo de pie. Este marcador se utiliza para determinar dirección de
    movimiento y ordenar los marcadores del pie.
    "ft_order": list, el orden de los marcadores del grupo pie se establece de
    distal distal a proximal. Ejemplo [0, 1] = ['antepie', 'talon'].
    "dir_mode": int, el metodo de detección de dirección de marcha. Valores
    esperados: 0, la dirección se toma de una diferencia de posición del
    marcador de cadera, en el cuadro de video; 1, la dirección se establece a
    través de la determinación de la dirección del pie.
    "ft_mov_markers": list, los marcadores de pie que se utilizan en la
    determinación del ciclado. Debería poder editarse (##INCLUIR EN LA
    CONFIGURACIÓN##).
    "markers_codenames": list(list), códigos identificadores de los marcadores;
        "tr" = tronco,
        "fi" = femur-inferior,
        "fs" = femur-superior,
        "ts" = tibia-superior,
        "ti" = tibia-inferior,
        "pp" = pie-posterior,
        "pa" = pie-anterior.
    "kv_slice": list(list), los indices para cortar la lista de marcadores de
    kinovea.
    "tight": list, marcadores que forman el segmento de *muslo. Se definen
    ordenan de manera tal que la resta entre el primero y el segundo forme el
    segmento dirigido.
    "leg": idem *pierna.
    "foot": idem *pie.
    "segments": list, se establece el orden en el que son formados los
    segmentos.
    "joints": list, el orden en el que son formadas las articulaciones.
}
"""


schema_4 = {
    "name": "schema-4",
    "ix_groups": [0, 1, 2],
    "num_markers": [1, 1, 2],
    "ft_group": 2,
    "ank_marker": 0,  # BUG
    "ft_order": [0, 1],  # NOTE: para que?
    "dir_mode": 0,
    "ft_mov_markers": [0, 1],
    "markers_codenames": [["tr"], ["fi"], ["ti", "pa"]],  # BUG
    "kv_slice": [[0, 1], [1, 2], [2, 4]],
    "segments": ["tight", "leg", "foot"],
    "tight": ["fi", "tr"],
    "leg": ["ti", "fi"],
    "foot": ["pa", "ti"],
    "joints": ["hip", "knee", "ankle"]
}

schema_7 = {
    "ix_groups": [0, 1, 2],
    "num_markers": [2, 2, 3],
    "ft_group": 2,
    "ank_marker": 2,
    "ft_order": [0, 1, 2],  # NOTE: para que?
    "dir_mode": 0,
    "ft_mov_markers": [0, 1],
    "markers_codenames": [["fs", "tr"], ["ts", "fi"], ["pa", "pp", "ti"]],
    "kv_slice": [[0, 2], [2, 4], [4, 7]],
    "segments": ["tight", "leg", "foot"],
    "tight": ["fi", "fs"],
    "leg": ["ti", "ts"],
    "foot": ["pa", "pp"],
    "joints": ["hip", "knee", "ankle"]
}
