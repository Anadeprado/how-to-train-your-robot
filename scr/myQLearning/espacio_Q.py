#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las lineas anteriores son xa q python reconozca acentos


import numpy as np
from constantes import *

from random import randint
from random import choice

#------------------------------------------------------------------------
#-   FUNCIONES PARA NAVEGAR ENTRE ESTADOS Y TRAYECTORIAS ----------------
#------------------------------------------------------------------------

# Función que devuelve un movimiento de disco aleatorio
def movimientoDiscoAleatorio(pos_D0):

    # TRAYECTORIAS POSIBLES: 5 o 3 en los extremos
    #    .-----.-----.-----.X
    #    |  1  |  2  |     |
    #    |  |  |/    |     |
    #    .--|--/-----.-----.
    #    | D D---- 3 |     |
    #    | D D\|     |     |
    #    .--|--\-----.-----.
    #    |  |  |\    |     |
    #    |  5  | 4   |     |
    #   Y.-----.-----.-----.
    #
    #    .-----.-----.-----.
    #    |  1  |  2  |     |
    #    |  |  |/    |     |
    #    .--|--/-----.-----.
    #    | D D---- 3 |     |
    #    | D D |     |     |
    #    .-----.-----.-----.

    # Detecto si está pegado a los límites:
    if pos_D0[1]==0:                #Top
        ttt = randint(3,5)
    elif pos_D0[1]==(num_secY-1):   #Bottom
        ttt = randint(1,3)
    else:
        ttt = randint(1,5)

    if(ttt==1):
        D1 = [pos_D0[0],   pos_D0[1]-1]
    elif(ttt==2):
        D1 = [pos_D0[0]+1, pos_D0[1]-1]
    elif(ttt==3):
        D1 = [pos_D0[0]+1, pos_D0[1]]
    elif(ttt==4):
        D1 = [pos_D0[0]+1, pos_D0[1]+1]
    else:
        D1 = [pos_D0[0],   pos_D0[1]+1]

    return D1

# Función para calcular la nueva posición del robot
def siguientePosRobot(pos_R, a):

    #new_posR = []
    xX = pos_R[0]
    yY = pos_R[1]

    # ACCIONES POSIBLES: 9
    #    .-----.-----.-----.(X)
    #    |  0  |  3  |  5  |
    #    |     |     |     |
    #    .-----.-----.-----.
    #    |  1  |  8  |  6  |
    #    |     | [R] |     |
    #    .-----.-----.-----.
    #    |  2  |  4  |  7  |
    #    |     |     |     |
    # (Y).-----.-----.-----.

    # Movemos en X
    if a < 3:           #0, 1, 2
        xX-=1
    elif 5 <= a <= 7:   #5, 6, 7
        xX+=1

    # Movemos en Y
    if a in [0, 3, 5]:
        yY-=1
    elif a in [2, 4, 7]:
        yY+=1

    new_posR = [xX,yY]

    return new_posR


# Función para detectar en qué trayectoria nos encontramos
#       Ejemplo:
#            detectarTray((1,1),(2,2)) = 27  [...mirar cuaderno]
#
def detectarTray(pos_D0, pos_D1):
    global tray_PorNivel

    x = 0
    y = 1
    star = 0
    # %   .-----.-----.-----. STAR ^^
    # %   |  -2 | -1  |     |
    # %   |  |  |/    |     |
    # %   .--|--/-----.-----.
    # %   | D D---- 0 |     |
    # %   | D D\|     |     |
    # %   .--|--\-----.-----.
    # %   |  |  |\    |     |
    # %   | +2  | +1  |     |
    # %   .-----.-----.-----.

    if(pos_D1[y] < pos_D0[y]): #Si esto se cumple es negativo
        if(pos_D1[x] > pos_D0[x]):
            star=-1
        else:
            star=-2
    elif(pos_D1[y]>pos_D0[y]): #Si esto se cumple es positivo
        if(pos_D1[x] > pos_D0[x]):
            star=1
        else:
            star=2

    trayectoria = pos_D0[x]*tray_PorNivel + pos_D0[y]*5 + star

        # Para 3 direcciones solo sería:
        # if(pos_D1[y]<pos_D0[y]):
        #     star=-1
        # elif(pos_D1[y]>pos_D0[y]):
        #     star=+1
        # trayectoria = pos_D0[x]*tray_PorNivel + pos_D0[y]*3 + star

    return trayectoria


# Función para detectar en qué estado nos encontramos
#       Ejemplo:
#           calculoEstado((0,0),(1,1),(1,1))
#           calculoEstado((0,0),(1,0),(1,1))
def calculoEstado(pos_D0, pos_D1, pos_R):
    global num_secX, num_secY, totalPos_robot

    x = 0
    y = 1
    trayectoria = detectarTray(pos_D0, pos_D1)
    #print trayectoria

    #estado_iker = (pos_R[0],pos_R[1],trayectoria)
    estado = trayectoria*totalPos_robot + num_secY*pos_R[x] + pos_R[y]

    return estado


# Función para elegir una acción aleatoria
def calcularAccionesLegales(pos_R, limitRR):
    #(0, 0, 6, 4)
    xminn,yminn,xmaxx,ymaxx = limitRR #Posiciones límite para el robot
    xx = pos_R[0]
    yy = pos_R[1]

    # ACCIONES POSIBLES: 9
    #    .-----.-----.-----.(X)
    #    |  0  |  3  |  5  |
    #    |     |     |     |
    #    .-----.-----.-----.
    #    |  1  |  8  |  6  |
    #    |     | [R] |     |
    #    .-----.-----.-----.
    #    |  2  |  4  |  7  |
    #    |     |     |     |
    # (Y).-----.-----.-----.

    #   ¡Pero cuidado robot con límites!
    #    .-----.-----.-----.
    #    |  3  |  5  |     |
    #    |  |  |/    |     |
    #    .--|--/-----.-----.
    #    | D D---- 6 |     |
    #    | D D |     |     |
    #    .-----.-----.-----.

    acciones_posibles = []
    opciones = []
    for i in range(9):        # De 0 a 8
        opciones.append(True)   #[True, True, True, True, True, True, True, True, True]

    if xx==xminn:
        #Límite IZQ -> eliminamos 0,1,2
        for i in [0,1,2]:
            opciones[i]=False
    elif xx==xmaxx:
         #Límite DRCH -> eliminamos 5,6,7
         for i in [5,6,7]:
             opciones[i]=False

    if yy==yminn:
        #Límite TOP -> eliminamos 0,3,5
        for i in [0,3,5]:
            opciones[i]=False
    elif yy==ymaxx:
         #Límite BOT -> eliminamos 2,4,7
         for i in [2,4,7]:
             opciones[i]=False

    #De esta forma tenemos en acciones[] sólo las opciones válidas en plan: [3,5,6,8]
    for i in range(9):
        if opciones[i]==True:
            acciones_posibles.append(i)

    return acciones_posibles


def elegirAccionAleatoria(accionesLegales):

    #accionesLegales muestra opciones válidas en plan: [3,5,6,8]

    #Ahora elegimos una al azar entre ellas:
    accion = choice(accionesLegales)

    return accion


def distancia(A, B):
    dx = B[0] - A[0]
    dy = B[1] - A[1]
    dalcuadrado = dx**2 + dy**2
    resultado = dalcuadrado**0.5  #sqrt
    return resultado


def recompensaInmediata(pos_R, pos_D):  #(S, a, S_1)

    #Distancia del robot al disco:
    dist = distancia(pos_R, pos_D)
    if dist == 0:
        rr = 2
        print('¡Atrapada!')
    else:
        rr = 1/dist

    return rr


#------------------------------------------------------------------------
# Algoritmos Q-Learning
#------------------------------------------------------------------------
#   Tabla de recompensas habitual en Q-Learning:
#       ___ __ __Acciones__ __
#       |r  r  r  r   r  r  r
#       |r  r  r  r   r  r  r
#       |
#       |
#       |
#       Estados
#
#   Tabla de Íkerbot (capas=trayectorias):
#        __ _____________ _____________ _______(X)Robot
#      /|
#     / |  [r0,r1,r2,r3] [r0,r1,r2,r3]
#  capa |  [r0,r1,r2,r3] [r0,r1,r2,r3]...
#  (Z)  |
#       |
#       (Y)Robot


# DEFINIR TABLA DE RECOMPENSAS Q
def inicializaQ():
    # Como IKERBOT sería...
    # Q_iker = np.zeros((num_secX, num_secY, tray_totales, num_ACCIONES)) #Quizá añadir,np.uint8)
    # ss = (1,1,0)
    # print QQ_iker[ss[0],ss[1],ss[2],0]

    Q0 = np.zeros((num_ESTADOS, num_ACCIONES))

    return Q0

def borraQ(Q):
    return np.zeros_like(Q)

def calculaNivelEntrenamientoQ(Q):

    cuenta_zeros = 0
    for fila in Q:
        for accion in fila:
            if accion == 0:
                cuenta_zeros += 1

    totales = num_ESTADOS*num_ACCIONES
    si_entrenadas = totales-cuenta_zeros
    porcentaje = (float(si_entrenadas)/totales)*100

    print 'Acciones entrenadas: ', si_entrenadas, '//', totales
    print 'Porcentaje entrenamiento: ', porcentaje, ' %'


# Máxima recompensa de un estado
def maxRefuerzo(Q, estado):
    maxi = max(Q[estado,:])
    return maxi

# Actualizo Q con UNA experiencia
def Entrena_Q_con_Experiencia(Q,experiencia, velAprendizaje, factorDesc):

    #estado, acción, recompensa, estado_siguiente = experiencia
    S, a, rr, S_1 = experiencia

    #Siguiente mejor recompensa del estado siguiente:
    Vst_1 = maxRefuerzo(Q, S_1)

    #Q-LEARNING:
    Q[S, a] += velAprendizaje *(rr + factorDesc * Vst_1 - Q[S, a])

    return Q

# Ejecuta entrenamiento para un episodio completo:
def Entrena_Q_con_Episodios(Q, experiencias, velAprendizaje, factorDesc, num_veces):

    for paso in range(num_veces):
       for experiencia in experiencias:
           Q = Entrena_Q_con_Experiencia(Q,experiencia, velAprendizaje, factorDesc)

    return Q



#   _Experiencia = (estado, acción, recompensa, estado siguiente)
#        < S, a, r, S+1>
#
#   _Learning rate = velocidad de aprendizaje entre 0 y 1. (alpha)
#       (0 = no aprende de nuevas exp , 1 = olvida todo y aprende nuevas exp)
#
#   _Discount factor = factor de descuento (gamma)
#       (0 = solo importan refuerzos inmediatos, 1 = solo a largo plazo)
#
    #   siguienteRefuerzoMixto = maxRefuerzo(tabla, siguienteEstado)
    #
    #   tabla[estado, accion] += velocidadAprendizaje *
    #               (refuerzo + factorDescuento * siguienteRefuerzoMixto
    #               - tabla[estado, accion]);
#
#   Si queremos refinar la tabla con las mismas experiencias podemos repetir
#   durante MAX_PASOS:

    # tabla = zeros(#estados, #acciones)
    # for paso in 1..MAX_PASOS:
    #   for experiencia in experiencias:
    #     estado, accion, refuerzo, siguienteEstado = experiencia
    #     siguienteRefuerzoMixto = maxRefuerzo(tabla, siguienteEstado)
    #     tabla[estado, accion] += velocidadAprendizaje * (
    #       refuerzo + factorDescuento * siguienteRefuerzoMixto
    #       - tabla[estado, accion]);

#
