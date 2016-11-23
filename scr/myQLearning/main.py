#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las lineas anteriores son xa q python reconozca acentos

import cv2
import numpy as np

from constantes import *
from espacio_Q import *
from random import randint

# % ESPACIO WEBCAM:
#     .-----.-----.-----.-----.-----.-----.-----.(X)
# 0   |     |     |     |     |     |     |     |
#     |     |  D  |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
# 1   |  D  |     |     |     |     |     |     |
#     |     |     |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
# 2   |     |     |     |  D  |  D  |     |  R  |
#     |     |     |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
# 3   |     |     |     |     |     |     |     |
#     |     |     |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
# 4   |     |     |     |     |     |     |  R  |
#     |     |     |     |     |     |     |     |
#  (Y).-----.-----.-----.-----.-----.-----.-----.
#
# NIVEL  0     1     2     3     4     5     6

# Variables globales de posición
pos_D0 = [0,0] #Posición anterior disco
pos_D1 = [0,0] #Posición siguiente disco
pos_R  = [0,0] #Posición robot

xmin,ymin,xmax,ymax = 0,0,num_secX-1,num_secY-1 #Posiciones límites
limitR = xmin,ymin,xmax,ymax

#   _Experiencia = (estado, acción, recompensa, estado siguiente)
#        < S, a, r, S+1>
#
#   _Learning rate = velocidad de aprendizaje entre 0 y 1. (alpha)
#       (0 = no aprende de nuevas exp , 1 = olvida todo y aprende nuevas exp)
#
#   _Discount factor = factor de descuento (gamma)
#       (0 = solo importan refuerzos inmediatos, 1 = solo a largo plazo)
#
experiencias = []
Q = []
S = 0
S_1 = 0
a = 0
rr = 0

velAprendizaje = 0.5  #alpha
factorDescuento = 0.8 #gamma

end_episodio = False

# Función que elige aletoriamente las posiciones iniciales:
def posicionesIniciales():
    global pos_D0,pos_R,vel_D,num_secX,num_secY

    pos_D0[0] = 0 #x
    pos_D0[1] = randint(0,num_secY-1) #y

    pos_R = [num_secX-1, (num_secY-1)/2]  #[6,2]
    #pos_R = # Se puede hacer random




#------------------------------------------------------------------------
#-  GUARDANDO Y LEYENDO FICHEROS  ---------------------------------------
#------------------------------------------------------------------------
import pickle  # módulo para la lectura/escritura de datos

def guardarExperiencias(experiencias, nombre_archivo = 'experiencias.dat'):

    archivo = open(nombre_archivo, 'wb') # Abre archivo binario para escribir
    pickle.dump(experiencias, archivo)   # Escribe experiencias en archivo
    archivo.close                        # Cierra archivo

def leerExperiencias(nombre_archivo = 'experiencias.dat'):

    archivo = open(nombre_archivo, 'wb') # Abre archivo binario para escribir
    lectura = pickle.load(archivo)       # Lee experiencias de archivo
    archivo.close                        # Cierra archivo

    return lectura




#------------------------------------------------------------------------
#-   DIBUJANDO EN PANTALLA  ---------------------------------------------
#------------------------------------------------------------------------
# def dibuja_Estado(img,pos_R,pos_D0,pos_D1):
#     global win_borde
#     # Robot:
#     rx = pos_R[0]*100 + win_borde
#     ry = pos_R[1]*100 + win_borde
#     cv2.circle(img,(ry,rx),20,(0,0,255),-1)
#
#     # Trayectoria Disco: Draw lines with thickness of 'tt' px and color 'cc'
#     tt = 2
#     dx0 = pos_D0[0]*100 + win_borde
#     dy0 = pos_D0[1]*100 + win_borde
#     cv2.circle(img,(dy0,dx0),10,(50,50,0),-1)
#     dx1 = pos_D1[0]*100 + win_borde
#     dy1 = pos_D1[1]*100 + win_borde
#     cv2.circle(img,(dy1,dx1),10,(200,200,0),-1)



#------------------------------------------------------------------------
#-   PRINCIPAL  ---------------------------------------------------------
#------------------------------------------------------------------------

while(1):
    print """
    \n¿Qué quieres hacer?\n
    \t 1- Nuevo Episodio (generar más experiencias)
    \t 2- Guardar Experiencias
    \t 3- Actualizar Q con Experiencias Guardadas
    \t 4- Salir
    \n
    """
    respuesta = raw_input(">> "); # Respuesta del usuario

    #1- NUEVO EPISODIO
    #-----------------------------------------
    if int(respuesta)==1:

        print 'Comenzamos EPISODIO nuevo...'
        end_episodio=False

        # EJECUTANDO UN EPISODIO COMPLETO:
        #   Posicion inicial disco y robot --> pos_D0, pos_R
        #
        #   Repito lo siguiente N veces para generar EXPERIENCIAS.
        #     -   Se mueve el disco --> pos_D1
        #     -   Calculo estado --> S_1
        #     -   ¿Actualizo anterior exp con (S_1)? <S,a,rr,S_1>
        #     -   S = S_1
        #     -   Decido siguiente acción de robot --> a
        #     -   Ejecuto acción --> pos_R
        #     -   Calculo recompensa --> rr
        #     -------Ya tengo de experiencia <S,a,rr,???> (falta el S_1)
        #     -   pos_D0 = pos_D1
        #     -   Compruebo si es el final del episodio --> end_episodio = True

        # Posicion inicial disco y robot --> pos_D0, pos_R
        posicionesIniciales()
        print 'Posicion inicial robot = ',pos_R
        print 'Posicion inicial disco = ',pos_D0

        # Se mueve el disco --> pos_D1
        pos_D1 = movimientoDiscoAleatorio(pos_D0)
        S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

        while(end_episodio==False):

            # Estado actual
            S = S_1

            # Decido siguiente acción de robot --> a
            accionesLegales = calcularAccionesLegales(pos_R, limitR)
            a = elegirAccionAleatoria(accionesLegales)

            # Ejecuto acción --> pos_R
            pos_R = siguientePosRobot(pos_R, a)

            # Calculo recompensa --> rr
            rr = recompensaInmediata(pos_R, pos_D1)
            print 'Recompensa: ', rr

            pos_D0 = pos_D1

            # Se mueve el disco --> pos_D1
            pos_D1 = movimientoDiscoAleatorio(pos_D0)

            # Calculo estado siguiente --> S_1
            S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

            # ¿Actualizo anterior exp con  <S,a,rr,S_1>
            experiencia = [S,a,rr,S_1]
            experiencias.append(experiencia)

            #¿¿Se termina el episodio??
            if rr == 2:
                print 'Robot atrapó el disco'
                end_episodio = True

            elif distancia(pos_R,pos_D1)==0:
                print 'Disco chocó contra robot en S_1'
                print 'Posicion final robot = ',pos_R
                print 'Posicion final disco = ',pos_D1
                end_episodio = True

            elif pos_D1[0]==xmax: #Disco llega al borde derecho
                print 'Disco llega al borde derecho: ', pos_D1
                end_episodio = True



        print 'Numero de experiencias-experimentadas hasta el momento:'
        print len(experiencias)

    #2- GUARDAR EXPERIENCIAS EN ARCHIVO
    #-----------------------------------------
    elif int(respuesta)==2:
        if len(experiencias)==0:
            print 'Aún no tienes experiencias...'
        else:
            guardarExperiencias(experiencias, 'experiencias.dat')

    #3- ACTUALIZAR Q CON EXPERIENCIAS GUARDADAS:
    #-----------------------------------------
    elif int(respuesta)==3:
    # Entreno mi Q actualizando las recompensas según Q-learning:
    #       num_veces = 3 repeticiones por ejemplo.

        experiencias_G = leerExperiencias('experiencias.dat')

        str = raw_input("¿Cuántas veces entrenamos Q con esas experiencias? (Repeticiones)");
        num_veces = int(str)

        Q = inicializaQ()
        Q = Entrena_Q_con_Episodios(Q,experiencias_G,velAprendizaje,factorDescuento,num_veces)

        # Muestra nivel de entrenamiento actual:
        calculaNivelEntrenamientoQ(Q)


    #4- SALIR
    #-----------------------------------------
    elif int(respuesta)==4:
        print 'Chao :)'
        break





#cv2.destroyAllWindows()
#[TAMBIEN PODRIA ACTUALIZAR Q SIEMPRE TRAS UN EPISODIO]
