#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------
#------------------------------------------------------------------------
#---  FUNCIONES PARA TRABAJAR EL ESPACIO Q ------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------

import numpy as np
from Const import *
from Q_utils import *

from random import randint
from random import random
from random import choice
from math import exp


# Función para detectar en qué estado nos encontramos
#       Ejemplo:
#           calculoEstado((0,0),(1,1),(1,1))
#           calculoEstado((0,0),(1,0),(1,1))
def calculoEstado(pos_D0, pos_D1, pos_R):

    x = 0
    y = 1

    trayectoria = detectTra(pos_D0, pos_D1)

    #estado_iker = (pos_R[0],pos_R[1],trayectoria)
    estado = trayectoria*ROBOT_TOTAL_POS + NUM_SEC_Y*pos_R[x] + pos_R[y]

    return estado


#----------------------------------------------------------------------
#---    Functions for decision making. POLICY of decision (pi)  -------
#----------------------------------------------------------------------

# Función para elegir una acción aleatoria de entre las posibles.
def elegirAccionAleatoria(pos_R):

    # 'accionesLegales' muestra opciones válidas. Ej: [3,5,6]
    accionesLegales = calcularAccionesLegales(pos_R)

    # Ahora elegimos una al azar entre ellas:
    accionA = choice(accionesLegales)

    return accionA

# Función para elegir la 'mejor' acción de entre las posibles.
#   Si hay empate entre varias, elegirá una aleatoria.
def elegirAccionMEJOR(pos_R, estado, Q):

    actionB = 8

    # 'accionesLegales' muestra opciones válidas en plan: [3,5,6]
    accionesLegales = calcularAccionesLegales(pos_R)

    recompensas = Q[estado,:]

    #'rr_elegidas' son las recompensas guardadas en las posiciones accionesLegales
    #   recompensas[0,0,2,0,1,0,0,0] --->
    #   accionesLegales [3,5,6] --->
    #   --->    rr_elegidas[2,1,0]
    rr_elegidas = [recompensas[i] for i in accionesLegales]
    maxQ = max(rr_elegidas)

    count = rr_elegidas.count(maxQ)
    #Si varias cumplen con ser las mejores:
    if count > 1:
        best = [i for i in range(len(rr_elegidas)) if rr_elegidas[i] == maxQ]
        i = choice(best)
    else:
        i = rr_elegidas.index(maxQ)

    actionB = accionesLegales[i]

    return actionB

# Función para elegir la 'peor' acción de entre las posibles.
#   Si hay empate entre varias, elegirá una aleatoria.
def elegirAccionPEOR(pos_R, estado, Q):

    actionP = 8

    # 'accionesLegales' muestra opciones válidas en plan: [3,5,6]
    accionesLegales = calcularAccionesLegales(pos_R)

    recompensas = Q[estado,:]

    #'rr_elegidas' son las recompensas guardadas en las posiciones accionesLegales
    #   recompensas[0,0,2,0,1,0,0,0] --->
    #   accionesLegales [3,5,6] --->
    #   --->    rr_elegidas[2,1,0]
    rr_elegidas = [recompensas[i] for i in accionesLegales]

    minQ = min(rr_elegidas)
    count = rr_elegidas.count(minQ)

    # Corrección de las líneas anteriores para no confundir "acción menos
    #recompensada" con "recompensas negativas"
    #minQ = min(abs(rr_elegidas))
    #count = rr_elegidas.count(minQ) + rr_elegidas.count(-minQ)

    #Si varias cumplen con ser las peores:
    if count > 1:
        best = [i for i in range(len(rr_elegidas)) if rr_elegidas[i] == minQ]
        i = choice(best)
    else:
        i = rr_elegidas.index(minQ)

    actionP = accionesLegales[i]

    return actionP

# Función para elegir la primero las acciones 'NO entrenadas'. O al menos las
# que tienen una recompensa guardada de '0'
#    Si hay empate entre varias, elegirá una aleatoria de entre las posibles.
def elegirAccion_PrimeroNoEntrenadas(pos_R, estado, Q):

    actionn = 8

    # 'accionesLegales' muestra opciones válidas en plan: [3,5,6]
    accionesLegales = calcularAccionesLegales(pos_R)

    recompensas = Q[estado,:]

    #'rr_elegidas' son las recompensas guardadas en las posiciones accionesLegales
    #   recompensas[0,0,2,0,1,0,0,0] --->
    #   accionesLegales [3,5,6] --->
    #   --->    rr_elegidas[2,1,0]
    rr_elegidas = [recompensas[i] for i in accionesLegales]

    # Buscamos cuántas hay con recompensa cero = '0'
    count = rr_elegidas.count(0)

    #Si no hay ninguna sin entrenar, elegimos completamente al azar.
    if count == 0:
        actionn = choice(accionesLegales)
    #Si varias son cero, elegimos al azar entre ellas:
    elif count > 1:
        best = [i for i in range(len(rr_elegidas)) if rr_elegidas[i] == 0]
        i = choice(best)
        actionn = accionesLegales[i]
    else:
        i = rr_elegidas.index(0)
        actionn = accionesLegales[i]

    return actionn



def accion_de_Explotacion(accionesLegales, estado, Q, epsilon):

    #Con probabilidad 1-epsilon Exploramos al azar.
    if random() < epsilon:
        # Al azar entre ellas:
        accionnn = choice(accionesLegales)

    # De lo contrario, elegimos la MEJOR
    else:
        recompensas = Q[estado,:]
        #print 'Recompensas para el estado ', estado, 'son: ', recompensas
        #'rr_elegidas' son las recompensas guardadas en las posiciones accionesLegales
        #   recompensas[0,0,2,0,1,0,0,0] --->
        #   accionesLegales [3,5,6] --->
        #   --->    rr_elegidas[2,1,0]
        rr_elegidas = [recompensas[i] for i in accionesLegales]
        maxQ = max(rr_elegidas)

        count = rr_elegidas.count(maxQ)
        #Si varias cumplen con ser las mejores:
        if count > 1:
            best = [i for i in range(len(rr_elegidas)) if rr_elegidas[i] == maxQ]
            i = choice(best)
        else:
            i = rr_elegidas.index(maxQ)

        accionnn = accionesLegales[i]

    return accionnn


#
def accion_de_Explotacion222(accionesLegales, estado, Q, epsilon):

    recompensas = Q[estado,:]
    #print 'Recompensas para el estado ', estado, 'son: ', recompensas

    #'rr_elegidas' son las recompensas guardadas en las posiciones accionesLegales
    #   recompensas[0,0,2,0,1,0,0,0] --->
    #   accionesLegales [3,5,6] --->
    #   --->    rr_elegidas[2,1,0]
    rr_elegidas = [recompensas[i] for i in accionesLegales]
    maxQ = max(rr_elegidas)

    # Si esto se cumple, NO cogemos la mejor acción sino que exploramos:
    if random() < epsilon:
        minQ = min(rr_elegidas)
        mag = max(abs(minQ), abs(maxQ))
        # Add random values to all the actions, recalculate maxQ
        # -->Asignamos una probabilidad a cada acción de forma que cuanto mayor sea
        # -->el valor Q de esa acción, mayor será la probabilidad de ser elegida.
        rr_elegidas = [rr_elegidas[i] + random() * mag - .5 * mag for i in range(len(rr_elegidas))]
        maxQ = max(rr_elegidas)

    count = rr_elegidas.count(maxQ)
    #Si varias cumplen con ser las mejores:
    if count > 1:
        best = [i for i in range(len(rr_elegidas)) if rr_elegidas[i] == maxQ]
        i = choice(best)
    else:
        i = rr_elegidas.index(maxQ)

    accionnn = accionesLegales[i]

    return accionnn


# tau = 1.12 #tau was selected by trial and error
# def softmax(av):
#     probs = np.zeros(n)
#     for i in range(n):
#         softm = ( np.exp(av[i] / tau) / np.sum( np.exp(av[:] / tau) ) )
#         probs[i] = softm
#     return probs

# For high temperatures (τ→∞), all actions have nearly the same probability.
# For a low temperature (τ→0+), the probability of the action with the highest
# expected reward tends to 1
#
# def play_strategy(self):
#     tau = self.tau
#     probabilities = np.zeros(self.N)
#     for i in range(self.N):
#         nom = math.exp(self.Qs[self.time_step,i] / tau)
#         denom = sum(math.exp(val/tau) for val in self.Qs[self.time_step,:])
#         probabilities[i] = float(nom / denom)
#     action = np.random.choice(range(self.N), p=probabilities)
#     return action
def accion_de_Explotacion_Softmax(accionesLegales, estado, Q, epsilon):

    recompensas = Q[estado,:]
    accionT = 8

    rr_elegidas = [recompensas[i] for i in accionesLegales]

    tau = calculaTau(epsilon)
    N = len(rr_elegidas)

    probabilities = np.zeros(N)
    for i in range(N):

        nom = exp(rr_elegidas[i] / tau)
        denom = sum(exp(val/tau) for val in rr_elegidas[:])

        probabilities[i] = float(nom / denom)

    actionT = np.random.choice(range(N), p=probabilities)

    return accionT


# Función que elige una acción siguiendo una política (POLICY) concreta:
def elegirAccion(pos_R, estado, Q, epsilon, policy='explot_eps', eps_limit = 0.80):

    accion = 8 #stop

    # 'accionesLegales' muestra opciones válidas en plan: [3,5,6]
    accionesLegales = calcularAccionesLegales(pos_R)


    if policy == 'explot_eps':

        # La política de 'explot_eps' depende si epsilon:
        #  - grande(=0.96) = EXPLO-RACIÓN: la acción se elija con mayor probabilidad al azar.
        #  - pequeño(=0.30) = EXPLO-TACIÓN: las acción se elija con menor probabilidad al azar.
        #       en este segundo caso será más probable que salga la MEJOR opción, la de mayor recompensa.
        # https://studywolf.wordpress.com/2012/11/25/reinforcement-learning-q-learning-and-exploration/
        #
        # Otra explicacion: La posibilidad más simple es elegir completamente al azar entre una opción y otra,
        # pero usaremos una opción un poco más inteligente y asignaremos una probabilidad
        # a cada acción en función del valor Q asociado, de forma que cuanto mayor sea
        # el valor Q de esa acción, mayor será la probabilidad de ser elegida.
        # De esta forma, incluso las acciones con valores Q más bajos tendrán opciones de ser elegidas.
        #
        #   Esta es mi política en concreto:
        #       epsilon > 0.80 ---> Aleatorio Total (ya que se ha entrenado menos del 20%)
        #       sino, será por probabilidades (explotación)

        if epsilon > eps_limit: #epsilon > 0.80
            accion = choice(accionesLegales) #Aleatoria
        else:
            accion = accion_de_Explotacion(accionesLegales, estado, Q, epsilon)

    # La política de 'explot_eps_fast' es igual que 'explot_eps' pero al
    # principio elige las acciones 'nunca' entrenadas
    #
    elif policy == 'explot_eps_fast':

        if epsilon > eps_limit: #epsilon > 0.80 ---> Entrenado menos del 20%
            accion = elegirAccion_PrimeroNoEntrenadas(pos_R, estado, Q)
        else:
            accion = accion_de_Explotacion(accionesLegales, estado, Q, epsilon)

    # La política de 'explot_100' es 100% explotación, sin depender de epsilon
    #
    elif policy == 'explot_softmax':

        if epsilon > eps_limit: #epsilon > 0.80
            accion = choice(accionesLegales) #Aleatoria
        else:
            accion = accion_de_Explotacion_Softmax(accionesLegales, estado, Q, epsilon)


    elif policy == 'explot_eps_1e':

        if epsilon > eps_limit:
            accion = choice(accionesLegales) #Aleatoria
        else:
            accion = accion_de_Explotacion222(accionesLegales, estado, Q, epsilon)

    else:
        print ('En ElegirAccion(): Política mal definida... robot no se mueve')

    return accion




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
    #Si quiero una matriz llena de valores 'None'
    # return np.full((num_ESTADOS, num_ACCIONES), None)

    return np.zeros((num_ESTADOS, num_ACCIONES)) #Array

def borraQ(Q):
    # return np.full_like(Q, None)
    return np.zeros_like(Q)

# Máxima recompensa de un estado
def maxRefuerzo(Q, estado):
    maxi = max(Q[estado,:])
    return maxi

# Actualizo Q con UNA experiencia
def Entrena_Q_con_UNA_Experiencia(Q,experiencia, velAprendizaje, factorDesc):

    #estado, acción, recompensa, estado_siguiente = experiencia
    S, a, rr, S_1 = experiencia

    #Siguiente mejor recompensa del estado siguiente:
    Vst_1 = maxRefuerzo(Q, S_1)

    #Valor anterior:
    Oldv = Q[S, a]

    #Q-LEARNING:
    if Oldv is 0: #None:
        Q[S, a] = rr
    else:
        Q[S, a] = Oldv + velAprendizaje *(rr + factorDesc * Vst_1 - Oldv)

    return Q

# Ejecuta entrenamiento para varias experiencias:
def Entrena_Q_con_Experiencias(Q, experiencias, velAprendizaje, factorDesc, num_veces):

    for paso in range(num_veces):
       for experiencia in experiencias:
           Q = Entrena_Q_con_UNA_Experiencia(Q,experiencia, velAprendizaje, factorDesc)

    return Q

# Calcula el nivel de entrenamiento de la matriz Q
def calculaNivelEntrenamientoQ(Q, mostrar = False):

    cuenta_zeros = 0
    for fila in Q:
        for ac in fila: #Acciones en fila
            if ac == 0:
                cuenta_zeros += 1

    si_entrenadas = TOTALES_A_ENTRENAR-cuenta_zeros

    porcentaje = (float(si_entrenadas)/TOTALES_A_ENTRENAR_REALES)*100

    if(mostrar==True):
        print 'Acciones entrenadas: ', si_entrenadas, '/', TOTALES_A_ENTRENAR_REALES
        print 'Porcentaje entrenamiento: ', porcentaje, ' %'

    return porcentaje



def mapValue(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def calculaEpsilon(porcentajeEntrenamiento):

    no_entrenadas = 100-porcentajeEntrenamiento
    pne = no_entrenadas/100

    eps = mapValue(pne, 0,70, 0,1)

    return eps


def calculaTau(epsilon):

    # maxTau = 1000000^100000
    # tau = (epsilon)*maxTau +0.1

    tau = mapValue(epsilon, 0,1, 0.1,1000000000)


    return tau

# epsilon > 0.80 ---> Aleatorio Total (ya que se ha entrenado menos del 20%)
# For high temperatures (τ→∞), all actions have nearly the same probability.
# For a low temperature (τ→0+), the probability of the action with the highest
# expected reward tends to 1
