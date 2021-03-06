#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las líneas anteriores son para que python reconozca acentos

####################################################################
# ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
#   Author: Anita de Prado
#   Hardware: Arduino Mega2560 + JJROBOTS brain shield v3 (devia)
#
#   Date: 20/02/2017
#   Version: 3
#
# License: Open Software GPL License
####################################################################
#   >>> SIMULATED TRAINING
####################################################################


import cv2
import numpy as np
import matplotlib.pyplot as plt

# Plot result
plt.figure('IceQueen Q-Learning')
plt.xlabel('Numero de lanzamiento') # etiqueta eje x
plt.ylabel('Sumatorio de exitos') # etiqueta eje y

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
crossedSectors = []
step = 0

#  _Experiencia = (estado, acción, recompensa, estado siguiente)
#       < S, a, r, S+1>
#
experiences = []

S = 0       # Estado actual
S_1 = 0     # Estado siguiente
a = 0       # Acción
rr = 0      # Recompensa

Q = inicializaQ()
print '\n Inicializando Q...'

#   _Learning rate = velocidad de aprendizaje entre 0 y 1. (alpha)
#       (0 = no aprende de nuevas exp , 1 = olvida todo y aprende nuevas exp)
#
#   _Discount factor = factor de descuento (gamma)
#       (0 = solo importan refuerzos inmediatos, 1 = solo a largo plazo)
#
#   _epsilon = Probabilidad de elegir acciones mejores o explorar.
#       En este programa se actualizará con el nivel de entrenamiento
#       epsilon == 0.7 ---> se ha entrenado menos del 30%
#
velAprendizaje = 0.5  # alpha  0.3
factorDescuento = 0.7 # gamma  0.8
epsilon = 1
epsilon_limit = 0.8

end_episodio = False




#------------------------------------------------------------------------
#-   FUNCIONES SOLO PARA SIMULACION     ---------------------------------
#------------------------------------------------------------------------
# Función para simulación que elige aletoriamente unas posiciones iniciales:
def posicionesIniciales():
    global pos_R,pos_D0,crossedSectors

    # El robot puede empezar en posición aleatoria dentro de sus límites
    pos_R[0]= randint(rxMin,rxMax)
    pos_R[1]= randint(ryMin,ryMax)

    # Generamos una trayectoria aleatoria:
    crossedSectors = lanzamientoCompletoDisco()
    pos_D0 = PosDisco(crossedSectors,0)


#------------------------------------------------------------------------
#-   PRINCIPAL  ---------------------------------------------------------
#------------------------------------------------------------------------
while(1):
    print """
    ¿Qué quieres hacer?
    ----------------------------
    \t 1- ENTRENAMIENTO
    \t 2- Guardar Q en Archivo (se borrará archivo anterior)
    \t 3- Cargar Q desde Archivo
    \t 4- Resetear Q
    \n\t 7- Salir
    \n\t 0- Ejecutar Juego
    """
    respuesta = raw_input(">> "); # Respuesta del usuario


    #7- SALIR
    #-----------------------------------------
    if respuesta == '7':
        print 'Chao pescao :)'
        break


    #2- GUARDAR Q EN ARCHIVO
    #-----------------------------------------
    elif respuesta == '2':
        if len(Q)==0:
            print 'Vale, pero que sepas que tu espacio Q está vacío...'
        print '...Salvando Q'
        saveData(Q, 'd_Qspace.dat')

    #3- CARGAR Q DESDE ARCHIVO:
    #-----------------------------------------
    elif respuesta == '3':
        print("...Cargando espacio Q ya entrenado")
        Q = readData('d_Qspace.dat')

    #4- RESETEAR Q
    #-----------------------------------------
    elif respuesta == '4':
        print '...Reseteamos Q'
        Q = borraQ(Q)



    #1- ENTRENAMIENTO
    #-----------------------------------------
    elif respuesta == '1':

        print 'Inicializamos epsilon y experiencias...'
        experiences = []

        #Calculamos epsilon equivalente al porcentaje de entrenamiento de Q:
        porcentajeEntrenamiento = calculaNivelEntrenamientoQ(Q, False)
        no_entrenadas = 100-porcentajeEntrenamiento
        epsilon = no_entrenadas/100

        num_episodios = raw_input("¿Cuántos episodios seguidos quieres simular? (Lanzamientos) \n");
        print """
    Elije el MODO ENTRENAMIENTO para el comportamiento del robot:
    \t 1- EXPLORACIÓN 100'%'               (Acciones aleatorias)
    \t 2- EXPLORACIÓN + EXPLOTACIÓN        (En función de 'epsilon')
    \t 3- EXPLORACIÓN RÁPIDA + EXPLOTACIÓN (Primero acciones no-entrenadas)
    \n
    \t 4- MODO EXPLOTACIÓN PERSONALIZADO

        """
        str = raw_input(">> ");
        modo_Entrenamiento = int(str)

        if (modo_Entrenamiento >= 4):
            print 'Aun no está programado el modo (4) o has pulsado otra cosa...'
            break

        str = raw_input("¿Cuántas veces entrenamos Q cada episodio? (Repeticiones)\n");
        num_veces = int(str)

        _num_exitos = 0
        _num_paradas = 0
        _num_ataques = 0
        plotX = list()
        plotY = list()
        plotEpsi = list()
        plotY.append(0)
        plotX.append(0)
        plotEpsi.append(0)

        print ("Entrenando.....")

        for episodio in range(int(num_episodios)):
            end_episodio=False
            posicionesIniciales()

            mx_step = len(crossedSectors)

            # Se mueve el disco --> pos_D1
            #pos_D1 = movimientoDiscoAleatorio(pos_D0)
            step = 1
            pos_D1 = PosDisco(crossedSectors,step)
            step += 1
            S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

            while(end_episodio==False):
                # Estado actual
                S = S_1

                # Decido siguiente acción de robot --> a
                if modo_Entrenamiento == 1:
                    a = elegirAccionAleatoria(pos_R)
                elif modo_Entrenamiento == 2:
                    a = elegirAccion(pos_R, S, Q, epsilon,'explot_eps', epsilon_limit)
                elif modo_Entrenamiento == 3:
                    a = elegirAccion(pos_R, S, Q, epsilon,'explot_eps_fast', epsilon_limit)

                pos_R0 = pos_R

                # Ejecuto acción --> pos_R
                pos_R = siguientePosRobot(pos_R, a)

                # Calculo recompensa --> rr
                rr = recompensaInmediata(pos_R, pos_D1)

                pos_D0 = pos_D1

                # Se mueve el disco --> pos_D1
                pos_D1 = PosDisco(crossedSectors,step)
                step += 1

                # Calculo estado siguiente --> S_1
                S_1 = calculoEstado(pos_D0, pos_D1, pos_R)


                # Compruebo si se termina Episodio:
                #------------------------------------------------------

                #print '¡Robot atrapó el disco! :)'
                if rr == 10:
                    if(pos_R0[0]>pos_D0[0]): #Lo empuja pero hacia atrás
                        rr=-5 #2
                        plotY.append(plotY[-1]-1)

                    elif(pos_R0[0]==pos_D0[0]): #Lo empuja lateralmente
                        rr=5 #0
                        _num_exitos += 1
                        _num_paradas += 1
                        plotY.append(plotY[-1]+1) #El valor anterior tal cual

                    else:
                        _num_exitos += 1
                        _num_ataques += 1
                        plotY.append(plotY[-1]+1) #El valor anterior más 1

                    plotEpsi.append(porcentajeEntrenamiento)
                    end_episodio = True


                elif distancia(pos_R,pos_D1)==0:
                    #print 'Disco chocó contra robot en S_1'
                    #PARADA pero no atacada...
                    rr = 1 #2
                    _num_exitos += 1
                    _num_paradas += 1
                    plotY.append(plotY[-1]) #El valor anterior tal cual

                    plotEpsi.append(porcentajeEntrenamiento)
                    end_episodio = True

                elif (pos_D1[0]==0)  or (step == mx_step): #Disco llega al borde izquierdo

                    # #Compruebo si disco finaliza en zona de GOL:
                    # if( 0 < pos_D1[1] < (NUM_SEC_Y-1)):
                    #     rr = -1

                    plotY.append(plotY[-1]-1) #El valor anterior menos 1
                    plotEpsi.append(porcentajeEntrenamiento)
                    end_episodio = True

                #------------------------------------------------------

                # Guardo Experiencia completa:  <S,a,rr,S_1>
                experience = [S,a,rr,S_1]
                experiences.append(experience)

            # Si el episodio se ha acabado: entreno Q con las experiencias
            Q = Entrena_Q_con_Experiencias(Q, experiences, velAprendizaje, factorDescuento, num_veces)

            # Borro experiencias de episodio
            experiences = []

            porcentajeEntrenamiento = calculaNivelEntrenamientoQ(Q, False)

            no_entrenadas = 100-porcentajeEntrenamiento
            epsilon = no_entrenadas/100


            #Actualizo variables para mostrar en plot
            plotX.append(episodio)


        #tit = 'Entrenamiento tipo %d con %s lanzamientos' % (modo_Entrenamiento,num_episodios)
        #print(tit)
        ppp = calculaNivelEntrenamientoQ(Q, True)
        print 'Epsilon final: ', epsilon

        #print 'Numero de exitos generales: ', _num_exitos
        bb = int(num_episodios)
        pps = (float(_num_exitos)/bb)*100
        print 'Porcentaje exitos: ', pps

        #print '\tNumero de paradas: ', _num_paradas
        bb = int(num_episodios)
        pps = (float(_num_paradas)/bb)*100
        print '\tPorcentaje paradas: ', pps

        #print '\tNumero de ataques de robot al disco: ', _num_ataques
        bb = int(num_episodios)
        pps = (float(_num_ataques)/bb)*100
        print '\tPorcentaje ataques: ', pps


        plt.figure('IceQueen Q-Learning')
        #plt.figure(1)
        #plt.title(tit)


        plt.subplot(211)

        plt.ylabel('Frecuencia de exito') # etiqueta eje y
        plt.xlabel('')
        plt.plot(plotX,plotY,'r')

        plt.subplot(212)

        plt.ylim(0,110)  # Limitamos los valores del eje x para que vayan desde 0 a 100
        plt.ylabel('Porcentaje entrenamiento') # etiqueta eje y
        plt.xlabel('')
        plt.plot(plotX,plotEpsi,'b')
        #plt.legend()
        plt.show()


    #0- EJECUTA JUEGO
    #-----------------------------------------
    elif respuesta=='0':

        num_episodios = raw_input("¿Cuántos episodios seguidos quieres jugar? \n");

        _num_exitos = 0
        _num_paradas = 0
        _num_ataques = 0
        plot_final_X = list()
        plot_final_Y = list()
        plot_final_Y.append(0)
        plot_final_X.append(0)


        print ("Jugando.....")

        for episodio in range(int(num_episodios)):
            end_episodio=False
            posicionesIniciales()

            mx_step = len(crossedSectors)
            #print "MaxStep = ", mx_step

            # Se mueve el disco --> pos_D1
            #pos_D1 = movimientoDiscoAleatorio(pos_D0)
            step = 1
            pos_D1 = PosDisco(crossedSectors,step)
            step+=1

            S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

            while(end_episodio==False):
                S = S_1

                # Decido siguiente acción de robot --> a
                a = elegirAccionMEJOR(pos_R, S, Q)
                pos_R0 = pos_R
                pos_R = siguientePosRobot(pos_R, a)
                rr = recompensaInmediata(pos_R, pos_D1)
                pos_D0 = pos_D1
                #pos_D1 = movimientoDiscoAleatorio(pos_D0)
                pos_D1 = PosDisco(crossedSectors,step)
                step+=1
                S_1 = calculoEstado(pos_D0, pos_D1, pos_R)

                # Compruebo si se termina Episodio:
                #-------------------------------------------------------------

                #print '¡Robot atrapó el disco! :)'
                if rr == 10:

                    if(pos_R0[0]>pos_D0[0]): #Lo empuja pero desde atrás
                        plot_final_Y.append(plot_final_Y[-1]-1) #El valor anterior menos 1

                    elif(pos_R0[0]==pos_D0[0]): #Lo empuja lateralmente
                        _num_exitos += 1
                        _num_paradas += 1
                        plot_final_Y.append(plot_final_Y[-1]) #El valor anterior tal cual

                    else:
                        _num_exitos += 1
                        _num_ataques += 1
                        plot_final_Y.append(plot_final_Y[-1]+1) #El valor anterior más 1

                    end_episodio = True

                elif distancia(pos_R,pos_D1)==0:
                    #print 'Disco chocó contra robot en S_1'
                    #PARADA pero no atacada...
                    _num_exitos += 1
                    _num_paradas += 1
                    plot_final_Y.append(plot_final_Y[-1]) #El valor anterior tal cual
                    end_episodio = True

                elif (pos_D1[0]==0)  or (step == mx_step): #Disco llega al borde izquierdo

                    # #Compruebo si disco finaliza en zona de GOL:
                    # if( 0 < pos_D1[1] < (NUM_SEC_Y-1)):
                    #     rr = -1
                    plot_final_Y.append(plot_final_Y[-1]-1) #El valor anterior menos 1
                    end_episodio = True

                #-------------------------------------------------------------

            #Actualizo variables para mostrar en plot
            plot_final_X.append(episodio)


        #print 'Numero de exitos generales: ', _num_exitos
        bb = int(num_episodios)
        pps = (float(_num_exitos)/bb)*100
        print 'Porcentaje exitos JUGANDO: ', pps

        #print '\tNumero de paradas: ', _num_paradas
        bb = int(num_episodios)
        pps = (float(_num_paradas)/bb)*100
        print '\tPorcentaje paradas: ', pps

        #print '\tNumero de ataques de robot al disco: ', _num_ataques
        bb = int(num_episodios)
        pps = (float(_num_ataques)/bb)*100
        print '\tPorcentaje ataques: ', pps


        plt.figure('IceQueen Q-Learning')

        #plt.title('Frecuencia de exito ENTRENANDO')
        plt.ylabel('Frecuencia de exito JUGANDO') # etiqueta eje y
        plt.xlabel('Numero de lanzamiento')
        plt.plot(plot_final_X,plot_final_Y,'r')
        plt.show()


    else:
        print 'Escribe bien la opción... ¬¬'


cv2.destroyAllWindows()
