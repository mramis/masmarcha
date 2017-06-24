#!/usr/bin/env python
# coding: utf-8

# %%
from os import path, listdir

import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import norm
from seaborn import color_palette
from pandas import DataFrame

from process import extractJointMarkersArraysFromFiles
from process import extractJointAnglesFromJointMarkersArrays
from calculo.fourier_fit import fourierfit

# %%
# Los archivos de kinovea que contienen las trayectorias
directorio = '/home/mariano/Escritorio/evaluacion-marcha/AlejandroMatiak/data/preqx/'
Matiak_PREQX = map(
    lambda ruta: path.join(directorio, ruta),
    listdir(directorio)
    )

directorio = '/home/mariano/Escritorio/evaluacion-marcha/AlejandroMatiak/data/postqx/'
Matiak_POSTQX = map(
    lambda ruta: path.join(directorio, ruta),
    listdir(directorio)
    )

directorio = '/home/mariano/Escritorio/Simposio/kinoveatxt/norm/'
REF_NORM = map(
    lambda ruta: path.join(directorio, ruta),
    listdir(directorio)
    )

# %%
Matiak_PREQX_arrays = extractJointMarkersArraysFromFiles(Matiak_PREQX)

Matiak_POSTQX_arrays = extractJointMarkersArraysFromFiles(Matiak_POSTQX)

Matiak_PREQX_angles = extractJointAnglesFromJointMarkersArrays(
    (Matiak_PREQX_arrays)
    )

Matiak_POSTQX_angles = extractJointAnglesFromJointMarkersArrays(
    (Matiak_POSTQX_arrays)
    )

Matiak_cadera_PREQX = []
Matiak_rodilla_PREQX = []
Matiak_tobillo_PREQX = []
for __, array in Matiak_PREQX_angles.iteritems():
    Matiak_cadera_PREQX.append(fourierfit(array['hip']))
    Matiak_rodilla_PREQX.append(fourierfit(array['knee']))
    Matiak_tobillo_PREQX.append(fourierfit(array['ankle']))
Matiak_cadera_PREQX = np.asarray(Matiak_cadera_PREQX).mean(axis=0)
Matiak_rodilla_PREQX = np.asarray(Matiak_rodilla_PREQX).mean(axis=0)
Matiak_tobillo_PREQX = np.asarray(Matiak_tobillo_PREQX).mean(axis=0)

Matiak_cadera_POSTQX = []
Matiak_rodilla_POSTQX = []
Matiak_tobillo_POSTQX = []
for __, array in Matiak_POSTQX_angles.iteritems():
    Matiak_cadera_POSTQX.append(fourierfit(array['hip']))
    Matiak_rodilla_POSTQX.append(fourierfit(array['knee']))
    Matiak_tobillo_POSTQX.append(fourierfit(array['ankle']))

Matiak_cadera_POSTQX_mean = np.asarray(Matiak_cadera_POSTQX).mean(axis=0)
Matiak_rodilla_POSTQX_mean = np.asarray(Matiak_rodilla_POSTQX).mean(axis=0)
Matiak_tobillo_POSTQX_mean = np.asarray(Matiak_tobillo_POSTQX).mean(axis=0)

Norm_arrays = extractJointMarkersArraysFromFiles(REF_NORM)
Norm_angles = extractJointAnglesFromJointMarkersArrays(Norm_arrays)

Norm_cadera = []
Norm_rodilla = []
Norm_tobillo = []
for __, value in Norm_angles.iteritems():
    Norm_cadera.append(fourierfit(value['hip']))
    Norm_rodilla.append(fourierfit(value['knee']))
    Norm_tobillo.append(fourierfit(value['ankle']))

Norm_cadera_mean = np.array(Norm_cadera).mean(axis=0)
Norm_rodilla_mean = np.array(Norm_rodilla).mean(axis=0)
Norm_tobillo_mean = np.array(Norm_tobillo).mean(axis=0)

SD_cadera_mean = np.array(Norm_cadera).std(axis=0)
SD_rodilla_mean = np.array(Norm_rodilla).std(axis=0)
SD_tobillo_mean = np.array(Norm_tobillo).std(axis=0)

matiak_cadera_sd = np.asarray(Matiak_cadera_POSTQX).std(axis=0)
cadera_norm = DataFrame(np.array((Norm_cadera_mean, SD_cadera_mean)).T, columns=('mean', 'std'))
cadera_muestra = DataFrame(np.array((Matiak_cadera_POSTQX_mean, matiak_cadera_sd)).T, columns=('mean', 'std'))




# %%
#def RMSE(X1, X):
#    '''Raiz del error cuadrático medio.
#    '''
#    return np.sqrt(np.sum(np.power(X1 - X, 2))/100)
#
#Errores_PREQX_vs_NORM = np.array((
#    RMSE(Matiak_cadera_PREQX, Norm_cadera_mean),
#    RMSE(Matiak_rodilla_PREQX, Norm_rodilla_mean),
#    RMSE(Matiak_tobillo_PREQX, Norm_tobillo_mean))
#    )
#
#Errores_POSTQX_vs_NORM = np.array((
#    RMSE(Matiak_cadera_POSTQX, Norm_cadera_mean),
#    RMSE(Matiak_rodilla_POSTQX, Norm_rodilla_mean),
#    RMSE(Matiak_tobillo_POSTQX, Norm_tobillo_mean))
#    )
#
#Errores_PREQX_vs_POSTQX = np.array((
#    RMSE(Matiak_cadera_PREQX, Matiak_cadera_POSTQX),
#    RMSE(Matiak_rodilla_PREQX, Matiak_rodilla_POSTQX),
#    RMSE(Matiak_tobillo_PREQX, Matiak_tobillo_POSTQX))
#    )
#
#Errores = DataFrame(
#    data=np.array((
#        Errores_PREQX_vs_NORM,
#        Errores_POSTQX_vs_NORM,
#        Errores_PREQX_vs_POSTQX)).T,
#    index=(
#        'Cadera',
#        'Rodilla',
#        'Tobillo'
#    ),
#    columns=(
#        'PRE_vs_NORM',
#        'POST_vs_NORM',
#        'PRE_vs_POST'),
#    )
#
## %%
## Las funciones para detectar el cambio de fases en el ciclo de la marcha
#def detectar_cambio(mascara):
#    '''Detecta los cambios en la velocidad, y devuelve los indices de dichos
#    cambios
#    :param mascara: arreglo de umbrales.
#    :type mascara: ndarray(dtype=bool)
#    '''
#    indices = []
#    for i, e in enumerate(mascara):
#        if i == mascara.size - 1:
#            break
#        if e != mascara[i+1]:
#            indices.append(i)
#    return indices
#
#
#def cambio_fase(arreglos):
#    '''
#    '''
#    despegue = []
#    tamano_arreglo = []
#    for __, arreglo in arreglos.iteritems():
#        xy = arreglo[-1, :, 1:]
#        dt = arreglo[-1, -1, 0] / arreglo[-1].shape[0]
#        Nabla, __ = np.gradient(xy, dt)
#        velocidad = norm(Nabla, axis=1)
#        fraccion = 0.1
#        apoyo_seguro = arreglo.shape[1] / 5  # los primeros j-esimos terminos
#        while True:                          # en los que sabemos hay apoyo
#            umbral = velocidad.max() * fraccion
#            indices = detectar_cambio(velocidad > umbral)
#            if indices[0] < apoyo_seguro:
#                indices.pop(0)
#            else:
#                break
#            fraccion += 0.1
#        tamano_arreglo.append(xy.shape[0])
#        despegue.append(indices[0])
#    percent = map(lambda N, t: t*100.0/N, tamano_arreglo, despegue)
#    return np.mean(percent).round()
#
#despegue_Norm = cambio_fase(Norm_arrays)
#despegue_PRE = cambio_fase(Matiak_PREQX_arrays)
#despegue_POST = cambio_fase(Matiak_POSTQX_arrays)
#
## %%
## PLOTS
## Goniometría
#fig, (pl1, pl2, pl3) = plt.subplots(1, 3, sharey=True)
#fig.suptitle('Rangos Articulares', fontsize=24)
#pl1.set_title('Cadera', fontsize=16)
#pl1.set_xlabel('Ciclo [%]', fontsize=16)
#pl1.set_ylabel('Angulos [grados]', fontsize=16)
#pl1.plot(Matiak_cadera_PREQX)
#pl1.axvline(despegue_PRE, ls='--', color=color_palette()[0])
#pl1.plot(Matiak_cadera_POSTQX)
#pl1.axvline(despegue_POST, ls='--', color=color_palette()[1])
#pl1.plot(Norm_cadera_mean)
#pl1.axvline(despegue_Norm, ls='--', color=color_palette()[2])
#pl1.fill_between(
#    np.arange(100),
#    Norm_cadera_mean,
#    Norm_cadera_mean + SD_cadera_mean*2,
#    color=color_palette()[2],
#    alpha=.12
#    )
#pl1.fill_between(
#    np.arange(100),
#    Norm_cadera_mean,
#    Norm_cadera_mean - SD_cadera_mean*2,
#    color=color_palette()[2],
#    alpha=.12
#    )
#pl1.axhline(0, c='k')
#pl1.legend('PRE Despegue POST Despegue NORM Despegue'.split(), loc=0)
#pl2.set_title('Rodilla', fontsize=16)
#pl2.set_xlabel('Ciclo [%]', fontsize=16)
#pl2.plot(Matiak_rodilla_PREQX)
#pl2.axvline(despegue_PRE, ls='--', color=color_palette()[0])
#pl2.plot(Matiak_rodilla_POSTQX)
#pl2.axvline(despegue_POST, ls='--', color=color_palette()[1])
#pl2.plot(Norm_rodilla_mean)
#pl2.axvline(despegue_Norm, ls='--', color=color_palette()[2])
#pl2.fill_between(
#    np.arange(100),
#    Norm_rodilla_mean,
#    Norm_rodilla_mean + SD_rodilla_mean*2,
#    color=color_palette()[2],
#    alpha=.12
#    )
#pl2.fill_between(
#    np.arange(100),
#    Norm_rodilla_mean,
#    Norm_rodilla_mean - SD_rodilla_mean*2,
#    color=color_palette()[2],
#    alpha=.12
#    )
#pl2.axhline(0, c='k')
#pl3.set_title('Tobillo', fontsize=16)
#pl3.set_xlabel('Ciclo [%]', fontsize=16)
#pl3.plot(Matiak_tobillo_PREQX)
#pl3.axvline(despegue_PRE, ls='--', color=color_palette()[0])
#pl3.plot(Matiak_tobillo_POSTQX)
#pl3.axvline(despegue_POST, ls='--', color=color_palette()[1])
#pl3.plot(Norm_tobillo_mean)
#pl3.axvline(despegue_Norm, ls='--', color=color_palette()[2])
#pl3.fill_between(
#    np.arange(100),
#    Norm_tobillo_mean,
#    Norm_tobillo_mean + SD_tobillo_mean*2,
#    color=color_palette()[2],
#    alpha=.12
#    )
#pl3.fill_between(
#    np.arange(100),
#    Norm_tobillo_mean,
#    Norm_tobillo_mean - SD_tobillo_mean*2,
#    color=color_palette()[2],
#    alpha=.12
#    )
#pl3.axhline(0, c='k')
#plt.show()
#
##%%
#def barras(arreglos, ncols, titulo='', xlab='', ylab='', ancho_barra=.2, ):
#    '''
#    '''
#    step = 0
#    plt.close()
#    plt.title(titulo, fontsize=24)
#    plt.xlabel(xlab, fontsize=16)
#    plt.ylabel(ylab, fontsize=16)
#    for i, arreglo in enumerate(arreglos):
#        plt.bar(
#            np.arange(ncols)+step,
#            arreglo,
#            width=ancho_barra,
#            color=color_palette()[i],
#            align='edge',
#            tick_label='Cadera Rodilla Tobillo'.split(),
#            )
#        plt.tick_params(labelsize='large')
#        for j, valor in enumerate(arreglo):
#            plt.text(j+step, valor+.2, '%0.2f' % valor)
#        step += ancho_barra
#
#barras(
#    (Errores_PREQX_vs_NORM, Errores_POSTQX_vs_NORM),
#    3, titulo='Root Mean Square Error (RMSE)', ylab='value'
#    )
#plt.legend('PRE~NORM POST~NORM'.split(), loc=0)
#plt.show()
#
##%%
## BONDAD DE AJUSTE
## NOTE: Necesito hacer un test que pueda dar un valor numérico en para el
## ajuste de valores de las gráficas de ángulos.
## Puedo decir que dos curvas son iguales si sea f(xi) = g(xi) y f'(xi) = g'(xi)
#
#def indice_ajuste(muestra, esperado, std):
#    '''
#
#    :param muestra:
#    :type muestra:
#    :param esperado:
#    :type esperado:
#    :param std:
#    :type std:
#    '''
#    # calculo si los valores de la muestra están en el rango de los valores
#    # esperados mas dos desvios estandares.
#    top = muestra < esperado + std*2
#    bottom = muestra > esperado - std*2
#    amplitud_normal = top == bottom
#    # calculo el signo de las pendientes para saber si la curva tienen las
#    # mismas direcciones
#    pendiente_esperado = np.sign(np.gradient(esperado))
#    pendiente_muestra = np.sign(np.gradient(muestra))
#    direccion_normal = pendiente_muestra == pendiente_esperado
#    # La intersección de los dos eventos
#    interseccion = direccion_normal.astype(int) + amplitud_normal.astype(int)
#    # se cuentan los valores que cumplen con las condiciones planteadas dentro
#    # de la muestra de datos.
#    factor_amplitud = np.count_nonzero(amplitud_normal)
#    factor_direccion = np.count_nonzero(direccion_normal)
#    factor_interseccion = np.count_nonzero(interseccion == 2)
#    # Pruebas gráficas.
#    # plt.plot(muestra)
#    # plt.plot(esperado)
#    # plt.plot(amplitud_normal.astype(int) * 2, linestyle='', marker='s')
#    # plt.plot(direccion_normal.astype(int) * 3, linestyle='', marker='s')
#    # plt.plot((interseccion > 1).astype(int) * 4, linestyle='', marker='s')
#    # plt.axhline(0, color='k')
#    # plt.legend('muestra normal amplitud direccion interseccion'.split(), loc=0)
#    # plt.show()
#    # Se devuelve el promedio de los valores.
#    return factor_interseccion, factor_amplitud, factor_direccion
#
## %%
#indices_cadera_pre = indice_ajuste(
#    Matiak_cadera_PREQX,
#    Norm_cadera_mean,
#    SD_cadera_mean
#    )
#indices_cadera_post = indice_ajuste(
#    Matiak_cadera_POSTQX,
#    Norm_cadera_mean,
#    SD_cadera_mean
#    )
#indices_rodilla_pre = indice_ajuste(
#    Matiak_rodilla_PREQX,
#    Norm_rodilla_mean,
#    SD_rodilla_mean
#    )
#indices_rodilla_post = indice_ajuste(
#    Matiak_rodilla_POSTQX,
#    Norm_rodilla_mean,
#    SD_rodilla_mean
#    )
#indices_tobillo_pre = indice_ajuste(
#    Matiak_tobillo_PREQX,
#    Norm_tobillo_mean,
#    SD_tobillo_mean
#    )
#indices_tobillo_post = indice_ajuste(
#    Matiak_tobillo_POSTQX,
#    Norm_tobillo_mean,
#    SD_tobillo_mean
#    )
#
## %%
#fig, (pl1, pl2, pl3) = plt.subplots(1, 3, sharey=True)
#fig.suptitle('Porcentajes de ajuste', fontsize=24)
#pl1.set_title('Cadera', fontsize=16)
#pl1.set_ylabel('Ajuste [%]', fontsize=16)
#pl1.set_ylim((0, 100))
#pl1.legend(('PRE', 'POST'), loc=0)
#pl1.bar(
#    np.arange(3),
#    indices_cadera_pre,
#    width=0.2,
#    color=color_palette()[0]
#    )
#pl1.bar(
#    np.arange(3) + 0.2,
#    indices_cadera_post,
#    width=0.2,
#    tick_label=u'intersección rango dirección'.split(),
#    color=color_palette()[1]
#    )
#pl1.tick_params(labelsize=16)
## Valores encimas de las barras.
#for i, (pre, post) in enumerate(zip(indices_cadera_pre, indices_cadera_post)):
#    step = 0.05
#    pl1.text(i+step, pre + .5, '%d' % pre)
#    step += 0.2
#    pl1.text(i+step, post + .5, '%d' % post)
#
#pl2.set_title('Rodilla', fontsize=16)
#pl2.bar(
#    np.arange(3),
#    indices_rodilla_pre,
#    width=0.2,
#    color=color_palette()[0]
#    )
#pl2.bar(
#    np.arange(3) + 0.2,
#    indices_rodilla_post,
#    width=0.2,
#    tick_label=u'intersección rango dirección'.split(),
#    color=color_palette()[1]
#    )
#pl2.tick_params(labelsize='large')
## Valores encimas de las barras.
#for i, (pre, post) in enumerate(zip(indices_rodilla_pre, indices_rodilla_post)):
#    step = 0.05
#    pl2.text(i+step, pre + .5, '%d' % pre)
#    step += 0.2
#    pl2.text(i+step, post + .5, '%d' % post)
#
#pl3.set_title('Tobillo', fontsize=16)
#pl3.bar(
#    np.arange(3),
#    indices_tobillo_pre,
#    width=0.2,
#    color=color_palette()[0]
#    )
#pl3.bar(
#    np.arange(3) + 0.2,
#    indices_tobillo_post,
#    width=0.2,
#    tick_label=u'intersección rango dirección'.split(),
#    color=color_palette()[1]
#    )
#pl3.tick_params(labelsize='large')
## Valores encimas de las barras.
#for i, (pre, post) in enumerate(zip(indices_tobillo_pre, indices_tobillo_post)):
#    step = 0.05
#    pl3.text(i+step, pre + .5, '%d' % pre)
#    step += 0.2
#    pl3.text(i+step, post + .5, '%d' % post)
#
#plt.show()
#
## # %% Estandarización y pruebas de hipótesis
## from scipy.stats import chisquare
## z_pre = (Matiak_cadera_PREQX - Norm_cadera_mean) / SD_cadera_mean
## z_pos = (Matiak_cadera_POSTQX - Norm_cadera_mean) / SD_cadera_mean
## plt.plot(z_pre)
## plt.plot(z_pos)
## plt.show()
## plt.hist(z_pre, 5)
## plt.show()
##
## plt.hist(z_pos, 5)
## plt.show()
