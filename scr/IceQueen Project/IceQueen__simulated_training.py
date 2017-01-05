#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las lineas anteriores son xa q python reconozca acentos

####################################################################
# ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
#   Author: Anita de Prado
#   Hardware: Arduino Mega2560 + JJROBOTS brain shield v3 (devia)
#
#   Date: 05/01/2017
#   Version: 0.00
#
# License: Open Software GPL License
####################################################################
#   >>> SIMULATED TRAINING
####################################################################

import cv2
import numpy as np
import matplotlib.pyplot as plt

plt.figure('IceQueen Q-Learning')

plt.xlabel('Valores de x')  # Ponemos etiqueta al eje x
plt.ylabel('Valores de y') # Ponemos etiqueta al eje y

from Q_utils import *
from Q_space import *
from random import randint

from Const import *
print '\tEspacio de ', NUM_SEC_X,'x',NUM_SEC_Y
print '\tNúmero de ESTADOS = ', num_ESTADOS
print '\tNúmero de acciones totales a entrenar = ', TOTALES_A_ENTRENAR
print '\tDe las cuales no permitidas: ', num_ACCIONES_QUE_JAMAS_SE_ENTRENARAN
#print 'Además existen todos los estados en los que el disco ya ha sobrepasado al robot'


print ("""
====================================================
--ENTRENAMIENTO SIMULADO DEL PROYECTO ICE-QUEEN-----
====================================================

          0     1     2     3     4     5     6
       .-----.-----.-----.-----.-----.-----.-----.--> X
     0 |     |     |     |     |     |     |     |
       |     |  R  |     |     |     |     |     |
       .-----.-----.-----.-----.-----.-----.-----.
     1 |  R  |     |     |     |     |     |     |
       |     |     |     |     |     |  D  |     |
       .-----.-----.-----.-----.-----.-----.-----.
     2 |     |     |     |  D  |  D  |     |  D  |
       |     |     |     |     |     |     |     |
       .-----.-----.-----.-----.-----.-----.-----.
     3 |     |     |     |     |     |     |     |
       |     |     |     |     |     |     |     |
       .-----.-----.-----.-----.-----.-----.-----.
       |
       Y """)


pos_D0 = [0,0] #Posición anterior disco
pos_D1 = [0,0] #Posición siguiente disco
pos_R  = [0,0] #Posición robot


#  _Experiencia = (estado, acción, recompensa, estado siguiente)
#       < S, a, r, S+1>
#
experiencias = []
Q = inicializaQ()
S = 0       # Estado actual
S_1 = 0     # Estado siguiente
a = 0       # Acción
rr = 0      # Recompensa

#   _Learning rate = velocidad de aprendizaje entre 0 y 1. (alpha)
#       (0 = no aprende de nuevas exp , 1 = olvida todo y aprende nuevas exp)
#
#   _Discount factor = factor de descuento (gamma)
#       (0 = solo importan refuerzos inmediatos, 1 = solo a largo plazo)
#
velAprendizaje = 0.3  # alpha  0.3
factorDescuento = 0.7 # gamma  0.8
epsilon = 0.8 # Probabilidad de elegir acciones mejores o explorar
#epsilon > 0.7 ---> Aleatorio Total (ya que se ha entrenado menos del 30%)

end_episodio = False

#------------------------------------------------------------------------
#-   FUNCIONES SOLO PARA SIMULACION     ---------------------------------
#------------------------------------------------------------------------
# Función para simulación que elige aletoriamente unas posiciones iniciales:
def posicionesIniciales():
    global pos_R,pos_D0
    # El disco siempre empieza en borde derecho:
    pos_D0[0] = NUM_SEC_X-1 #x
    pos_D0[1] = randint(0,NUM_SEC_Y-1) #y

    # Posición fija inicial: [6,2]
    #pos_R = [NUM_SEC_X-1, (NUM_SEC_Y-1)/2]

    # El robot puede empezar en posición aleatoria dentro de sus límites
    pos_R[0]= randint(rxMin,rxMax)
    pos_R[1]= randint(ryMin,ryMax)



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
    ¿Qué quieres hacer?
    ----------------------------
    \t 1- Simular Episodio (generar más experiencias)
    \t 2- Guardar Experiencias en Archivo (se borrará archivo anterior)
    \t 3- Actualizar Q con Experiencias Guardadas
    \t 4- Guardar Q en Archivo (se borrará archivo anterior)
    \t 5- Resetear Experiencias
    \t 6- Resetear Q
    \t 7- Salir \n
    \t 99- Modo inteligente y contínuo (no guardando experiencias)
    \t 222- Ejecuta Juego
    """
    respuesta = raw_input(">> "); # Respuesta del usuario

    #1- NUEVO EPISODIO
    #-----------------------------------------
    if int(respuesta)==1:

        num_episodios = raw_input("¿Cuántos episodios seguidos quieres simular? (Lanzamientos)\n");

        # Modo de entrenamiento o 'policy(pi)'
        print """
        Elije el MODO ENTRENAMIENTO para el comportamiento del robot:
        \t 1- MODO EXPLORACIÓN (Acciones aleatorias)
        \t 2- MODO EXPLORACIÓN RÁPIDA (Primero acciones no-entrenadas)
        \t 3- MODO EXPLOTACIÓN (En función de 'epsilon')
        """
        str = raw_input(">> ");
        modo_Entrenamiento = int(str)

        for i in range(int(num_episodios)):
            print 'Comenzamos EPISODIO nuevo...'
            end_episodio=False

            # EJECUTANDO UN EPISODIO COMPLETO para generar EXPERIENCIAS:
            #   - Posicion inicial disco y robot --> pos_D0, pos_R
            #   -   Se mueve el disco --> pos_D1
            #   -   Calculo estado --> S_1
            #
            #   Repito lo siguiente mientras end_episodio==False
            #     -   S = S_1
            #     -   Decido siguiente acción de robot --> a
            #     -   Ejecuto acción --> pos_R
            #     -   Calculo recompensa --> rr
            #     -   pos_D0 = pos_D1
            #     -   Se mueve el disco --> pos_D1
            #     -   Calculo estado siguiente --> S_1
            #     -   Compruebo si es el final del episodio --> end_episodio = True
            #     -   Guardo experiencia completa ---> <S,a,rr,S_1>


            # Posicion inicial disco y robot --> pos_D0, pos_R
            posicionesIniciales()

            # Se mueve el disco --> pos_D1
            pos_D1 = movimientoDiscoAleatorio(pos_D0)
            S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

            while(end_episodio==False):

                # Estado actual
                S = S_1
                #print("Estado actual: %d" % (S))

                # Decido siguiente acción de robot --> a
                if modo_Entrenamiento == 1:
                    a = elegirAccionAleatoria(pos_R)
                elif modo_Entrenamiento == 2:
                    a = elegirAccionPEOR(pos_R, S, Q)
                else:
                    a = elegirAccion(pos_R, S, Q, epsilon)

                # Ejecuto acción --> pos_R
                pos_R = siguientePosRobot(pos_R, a)

                # Calculo recompensa --> rr
                rr = recompensaInmediata(pos_R, pos_D1)
                #print 'Recompensa: ', rr

                pos_D0 = pos_D1

                # Se mueve el disco --> pos_D1
                pos_D1 = movimientoDiscoAleatorio(pos_D0)

                # Calculo estado siguiente --> S_1
                S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

                # Compruebo si se termina Episodio:
                if rr == 10:
                    print '¡Robot atrapó el disco! :)'
                    end_episodio = True

                elif distancia(pos_R,pos_D1)==0:
                    print 'Disco chocó contra robot en S_1'
                    end_episodio = True
                    #!!!!!Cuando ejecute en modo real, no con movimiento random
                    #de disco, aquí puedo reforzar con una rr más positiva antes
                    #de guardar la experiencia

                elif pos_D1[0]==0: #Disco llega al borde izquierdo
                    print 'Disco llega al borde derecho: ', pos_D1
                    #Compruebo si disco finaliza en zona de GOL:
                    if( 0 < pos_D1[1] < (NUM_SEC_Y-1)):
                        rr = -1
                    end_episodio = True

                # elif pos_D1[0]>pos_R[0]:
                #     print 'Disco pasó de largo respecto robot'
                #     end_episodio = True
                # !!!Y poner recompensa negativaa

                # Guardo Experiencia completa:  <S,a,rr,S_1>
                experiencia = [S,a,rr,S_1]
                experiencias.append(experiencia)


        print 'Numero de experiencias-experimentadas hasta el momento:'
        print len(experiencias)

    #2- GUARDAR EXPERIENCIAS EN ARCHIVO
    #-----------------------------------------
    elif int(respuesta)==2:
        if len(experiencias)==0:
            print 'Aún no tienes experiencias...'
        else:
            guardarExperiencias(experiencias, 'd_experiencias.dat')

    #3- ACTUALIZAR Q CON EXPERIENCIAS GUARDADAS:
    #-----------------------------------------
    elif int(respuesta)==3:
    # Entreno mi Q actualizando las recompensas según Q-learning:
    #       num_veces = 3 repeticiones por ejemplo.

        experiencias_G = leerExperiencias('d_experiencias.dat')

        str = raw_input("¿Cuántas veces entrenamos Q con esas experiencias? (Repeticiones)\n");
        num_veces = int(str)

        Q = Entrena_Q_con_Experiencias(Q,experiencias_G,velAprendizaje,factorDescuento,num_veces)

        # Muestra nivel de entrenamiento actual:
        ppp = calculaNivelEntrenamientoQ(Q, True)


    #4- Guardar Q en Archivo (se borrará archivo anterior)
    #-----------------------------------------
    elif int(respuesta)==4:
        if len(Q)==0:
            print 'Tu espacio Q está vacío...'
        else:
            guardarQ(Q, 'd_Qspace.dat')

    #5- Resetear experiencias y Q
    #-----------------------------------------
    elif int(respuesta)==5:
        print 'Reseteamos experiencias...'
        experiencias = []

    #6- Resetear Q
    #-----------------------------------------
    elif int(respuesta)==6:
        print 'Inicializamos Q...'
        Q = borraQ(Q)

    #7- SALIR
    #-----------------------------------------
    elif int(respuesta)==7:
        print 'Chao :)'
        break



    #99- MODO INTELIGENTE y CONTINUO (no guardando experiencias)
    #-----------------------------------------
    elif int(respuesta)==99:

        # Q = borraQ(Q)

        print 'Inicializamos epsilon y experiencias...'
        experiencias = []

        #Calculamos epsilon variable al inicio:
        porcentajeEntrenamiento = calculaNivelEntrenamientoQ(Q, False)
        no_entrenadas = 100-porcentajeEntrenamiento
        epsilon_v = no_entrenadas/100

        num_episodios = raw_input("¿Cuántos episodios seguidos quieres simular? (Lanzamientos) \n");
        print """
        Elije el MODO ENTRENAMIENTO para el comportamiento del robot:
        \t 1- MODO EXPLORACIÓN (Acciones aleatorias)
        \t 2- MODO EXPLORACIÓN RÁPIDA (Primero acciones no-entrenadas)
        \t 3- MODO EXPLOTACIÓN (En función de 'epsilon')
        """
        str = raw_input(">> ");
        modo_Entrenamiento = int(str)
        str = raw_input("¿Cuántas veces entrenamos Q cada episodio? (Repeticiones)\n");
        num_veces = int(str)

        _num_exitos = 0
        plotX = list()
        plotY = list()
        plotY.append(0)
        plotX.append(0)

        print ("Entrenando.....")

        for episodio in range(int(num_episodios)):
            end_episodio=False
            posicionesIniciales()
            pos_D1 = movimientoDiscoAleatorio(pos_D0)
            S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

            while(end_episodio==False):
                S = S_1
                #print("Estado actual: %d" % (S))

                # Decido siguiente acción de robot --> a
                if modo_Entrenamiento == 1:
                    a = elegirAccionAleatoria(pos_R)
                elif modo_Entrenamiento == 2:
                    a = elegirAccionPEOR(pos_R, S, Q)
                else:
                    a = elegirAccion(pos_R, S, Q, epsilon_v)

                pos_R = siguientePosRobot(pos_R, a)
                rr = recompensaInmediata(pos_R, pos_D1)
                pos_D0 = pos_D1
                pos_D1 = movimientoDiscoAleatorio(pos_D0)
                S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

                # Compruebo si se termina Episodio:
                if rr == 10:
                    #print '¡Robot atrapó el disco! :)'
                    end_episodio = True
                    _num_exitos += 1
                    plotY.append(plotY[-1]+1)

                elif distancia(pos_R,pos_D1)==0:
                    #print 'Disco chocó contra robot en S_1'
                    end_episodio = True
                    _num_exitos += 1
                    #!!!!!Cuando ejecute en modo real, no con movimiento random
                    #de disco, aquí puedo reforzar con una rr más positiva antes
                    #de guardar la experiencia
                    plotY.append(plotY[-1])

                elif pos_D1[0]==0: #Disco llega al borde izquierdo
                    #print 'Disco llega al borde derecho: ', pos_D1
                    #Compruebo si disco finaliza en zona de GOL:
                    if( 0 < pos_D1[1] < (NUM_SEC_Y-1)):
                        rr = -1
                    end_episodio = True

                    plotY.append(plotY[-1]-1) #El valor anterior menos 1

                # Guardo Experiencia completa:  <S,a,rr,S_1>
                experiencia = [S,a,rr,S_1]
                experiencias.append(experiencia)

            #Actualizo variables para mostrar en plot
            plotX.append(episodio)


            # Si el episodio se ha acabado: entreno Q con las experiencias
            Q = Entrena_Q_con_Experiencias(Q, experiencias, velAprendizaje, factorDescuento, num_veces)

            # Borro experiencias de episodio
            experiencias = []

            porcentajeEntrenamiento = calculaNivelEntrenamientoQ(Q, False)

            no_entrenadas = 100-porcentajeEntrenamiento
            epsilon_v = no_entrenadas/100

            #print 'Nuevo epsilon: ', epsilon_v

        ppp = calculaNivelEntrenamientoQ(Q, True)
        print 'Epsilon final: ', epsilon_v
        print 'Numero de exitos: ', _num_exitos
        bb = int(num_episodios)
        pps = (float(_num_exitos)/bb)*100
        print 'Porcentaje exitos: ', pps

        plt.plot(plotX, plotY, 'ro', label='Frecuencia de exito')
        plt.legend()
        plt.show()


    #222- EJECUTA JUEGO
    #-----------------------------------------
    elif int(respuesta)==222:

        num_episodios = raw_input("¿Cuántos episodios seguidos quieres jugar? \n");
        plot_final_X = list()
        plot_final_Y = list()
        plot_final_Y.append(0)
        plot_final_X.append(0)
        _num_exitos = 0

        print ("Jugando.....")

        for episodio in range(int(num_episodios)):
            end_episodio=False
            posicionesIniciales()
            pos_D1 = movimientoDiscoAleatorio(pos_D0)
            S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

            while(end_episodio==False):
                S = S_1

                # Decido siguiente acción de robot --> a
                a = elegirAccionMEJOR(pos_R, S, Q)

                pos_R = siguientePosRobot(pos_R, a)
                rr = recompensaInmediata(pos_R, pos_D1)
                pos_D0 = pos_D1
                pos_D1 = movimientoDiscoAleatorio(pos_D0)
                S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

                # Compruebo si se termina Episodio:
                if rr == 10:
                    #print '¡Robot atrapó el disco! :)'
                    end_episodio = True
                    _num_exitos += 1
                    plot_final_Y.append(plot_final_Y[-1]+1)

                elif distancia(pos_R,pos_D1)==0:
                    #print 'Disco chocó contra robot en S_1'
                    end_episodio = True
                    _num_exitos += 1
                    #!!!!!Cuando ejecute en modo real, no con movimiento random
                    #de disco, aquí puedo reforzar con una rr más positiva antes
                    #de guardar la experiencia
                    plot_final_Y.append(plot_final_Y[-1])

                elif pos_D1[0]==0: #Disco llega al borde izquierdo
                    #print 'Disco llega al borde derecho: ', pos_D1
                    #Compruebo si disco finaliza en zona de GOL:
                    if( 0 < pos_D1[1] < (NUM_SEC_Y-1)):
                        rr = -1
                    end_episodio = True

                    plot_final_Y.append(plot_final_Y[-1]-1) #El valor anterior menos 1

            #Actualizo variables para mostrar en plot
            plot_final_X.append(episodio)

        print 'Numero de exitos: ', _num_exitos
        bb = int(num_episodios)
        pps = (float(_num_exitos)/bb)*100
        print 'Porcentaje exitos: ', pps
        #plt.plot(plot_final_X, plot_final_Y, 'ro', label='Frecuencia de exito')
        plt.plot(plot_final_X, plot_final_Y, 'b',linewidth=2.0, label='Frecuencia de exito')
        plt.legend()
        plt.show()


cv2.destroyAllWindows()

#[TAMBIEN PODRIA ACTUALIZAR Q SIEMPRE TRAS UN EPISODIO]

# USAR PORCENTAJE DE EXITO!! NO % ENTRENAMIENTO
