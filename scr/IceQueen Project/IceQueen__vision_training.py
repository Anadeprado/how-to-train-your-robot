#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las líneas anteriores son para que python reconozca acentos

###########################################################################
# ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
#   Author: Anita de Prado
#   Hardware: Arduino Mega2560 + JJROBOTS brain shield v3 (devia)
#
#   Date: 20/02/2017
#   Version: 3
#
# License: Open Software GPL License
###########################################################################
#   >>> TRAINING with VISION CONTROL
#       - Detect green Disc & blue Robot
#       - Send UPD packets to Arduino (Wifi: JJROBOTS_78 // pass=87654321)
#       - Update Q space
###########################################################################


# Import the necessary packages
import numpy as np
import argparse
import imutils
import cv2
import socket

import time

from random import randint
from Const import *
from Q_utils import *
from Q_space import *
from Vision_utils import *


#--------------------------------------------
# Actual & old sector positions
pos_D0 = [-2,-2] #Posición anterior disco
pos_D1 = [-1,-1] #Posición siguiente disco
pos_R  = [0,0]   #Posición robot

end_episodio = True

#If the disk moves to a new sector and does not move backward
disc_advances = False
disc_Out = False

#  _Experiencia = (estado, acción, recompensa, estado siguiente)
#       < S, a, r, S+1>
#
experiences = []
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
factorDescuento = 0.6 # gamma  0.8
num_veces = 5
epsilon_v = 99

# ----------------------------------------------
drawLines = True
drawSectors = True
# ----------------------------------------------


print("...Cargando valores HSV")
# greenLower,greenUpper,blueLower,blueUpper = readData('d_valuesHSV.dat')
# HSV_values = greenLower,greenUpper,blueLower,blueUpper
HSV_values = readData('d_valuesHSV.dat')
print("-OK")

print("...Cargando espacio Q ya entrenado")
Q = readData('d_Qspace_real.dat')

# Calculamos epsilon variable al inicio:
porcentajeEntrenamiento = calculaNivelEntrenamientoQ(Q, False)
print "......nivel entrenamiento: %d %", porcentajeEntrenamiento

print("-OK")


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# This is the IP & port number that ESP opens
HOST = "192.168.4.1"
PORT = 2222
print("...Abriendo conexion Wifi UDP en 192.168.4.1:2222")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #Socket UPD
try:
    s.connect((HOST, PORT)) #Conect socket with server
except Exception as e:
    print("something's wrong with %s:%d. Exception is %s" % (HOST, PORT, e))

print("-OK")

#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# CAMERA 1 = USB webcam
camera = cv2.VideoCapture(1)

if(camera.isOpened()==False):
    print("¡No hay camara conectada!")
    exitIceQueen(camera, s)


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
print ("""
====================================================
--VISION POR COMPUTADOR DEL PROYECTO ICE-QUEEN------
====================================================
\t 1 - TRAINING
\t 2 - Calibrar los valores HSV
\n
\t Q - Salir
\n
""")
respuesta = raw_input(">> "); # Respuesta del usuario

if(respuesta is 'Q') or (respuesta is 'q'):
    exitIceQueen(camera, s)

elif(respuesta is '2'):

    greenLower,greenUpper,blueLower,blueUpper = HSV_values

    #print("\n...Calibrando el VERDE para detectar DISCO...\n")
    greenLower, greenUpper = calibrate_HSV(camera, greenLower, greenUpper, 'VERDE')

    #print("\n...Calibrando el AZUL para detectar ROBOT...\n")
    blueLower, blueUpper = calibrate_HSV(camera, blueLower, blueUpper,'AZUL')

    HSV_values = greenLower,greenUpper,blueLower,blueUpper
    saveData(HSV_values,'d_valuesHSV.dat')

# elif(respuesta is '1'):
#     # Mostramos visión
#     #print 'Iniciamos vista...'
#     cv2.namedWindow('IceQueen Vision')
#     cv2.waitKey(1)


# Keep looping
while True:

    end_episodio = True

    print ("""
    ====================================================
    -- ¿Qué quieres hacer? -----------------------------
    ====================================================
    \t E - Nuevo Episodio (Lanzamiento)
    \t G - Guardar Q en Archivo (se borrará archivo anterior)
    \t R - Resetear Q
    \n
    \t Q - Salir
    \n
    """)
    respuesta = raw_input(">> "); # Respuesta del usuario

    if(respuesta is 'Q') or (respuesta is 'q'):
        exitIceQueen(camera, s)

    elif (respuesta is 'G') or (respuesta is 'g'):
        print 'Salvando Q...'
        saveData(Q, 'd_Qspace_real.dat')

    elif (respuesta is 'R') or (respuesta is 'r'):
        print 'Inicializamos Q...'
        Q = borraQ(Q)

    elif(respuesta is 'E') or (respuesta is 'e'):

        print 'Inicializamos epsilon y experiencias...'
        experiences = []

        # Calculamos epsilon variable al inicio:
        porcentajeEntrenamiento = calculaNivelEntrenamientoQ(Q, False)
        no_entrenadas = 100-porcentajeEntrenamiento
        epsilon_v = no_entrenadas/100

        # Robot a POSICIÓN INICIAL
        # El robot puede empezar en un sector aleatoria dentro de sus límites
        target_ini_x= randint(rxMin,rxMax)
        target_ini_y= randint(ryMin,ryMax)
        target_sector_R = (target_ini_x,target_ini_y)
        target_mm_R = calcRobotPos_in_mm(target_sector_R)
        print 'Sector inicial para robot: ',target_sector_R


        # Robot a POSICIÓN INICIAL
        colocado = False
        while(colocado == False):
            print '¿Está el robot en su posición inicial? [S = si. N = no]'
            time.sleep(.300)
            while(1):
                # Mostrando detección de disco y robot:
                center_DISC, center_ROBOT, frame = vision_Detection(camera, HSV_values)
                if(drawLines==True):
                    draw_margin_and_center(frame)
                    draw_sector_lines(frame)
                cv2.imshow("IceQueen Vision", frame)

                key = cv2.waitKey(10) & 0xFF
                if (key== ord("n")):
                    if(center_ROBOT is not None):
                        # Enviamos ordenes al Robot para que alcance la posición inicial:
                        sendToRobot(s,target_mm_R,center_ROBOT,'a',1) #very slow
                    break
                elif (key== ord("s")):
                    colocado = True
                    break

        # Disco a POSICIÓN INICIAL
        print 'Coloca el disco en la posición inicial y pulsa una tecla. OK?'
        ready = -1
        time.sleep(.300)
        while(ready is -1): #not key pressed
            # Mostrando detección de disco y robot:
            center_DISC, center_ROBOT, frame = vision_Detection(camera, HSV_values)
            if(drawLines==True):
                draw_margin_and_center(frame)
                draw_sector_lines(frame)
            cv2.imshow("IceQueen Vision", frame)

            ready = cv2.waitKey(10)


        #Comprobamos que se detecta tanto disco como robot:
        center_DISC, center_ROBOT, frame = vision_Detection(camera, HSV_values)
        if(center_ROBOT is None) or (center_DISC is None):
            print '(!) Episodio termina porque algo falla con la detección dentro de la mesa'
            print '\n center_ROBOT = ', center_ROBOT
            print ' center_DISC  = ', center_DISC
            end_episodio = True

        else:

            #print ("\n\nPosiciones iniciales fijadas.....")
            _, pos_D0 = update_actual_sector_position(
                                    center_DISC[0],center_DISC[1],pos_D0)
            _, pos_R = update_actual_sector_position(
                                    center_ROBOT[0],center_ROBOT[1],pos_R)


            print ("""
    ====================================================
    -- TRAINING ICE-QUEEN ------------------------------
    ====================================================
    \t S - Detener Episodio (Lanzamiento)
    \n
    \t 1 - ¡PERFECTO!       :) Recompensa muy positiva
    \t 2 - Bien             :) Recompensa positiva
    \t 3 - Regular...
    \t 4 - Mal              :( Recompensa negativa
    \t 5 - ¡Muy MAL!        :( Recompensa muy negativa
    \n
    \t 0 - No puntuar recompensa extra
    \n
    \t Q - Salir
    \n
            """)


            first_action = True
            end_episodio = False


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


    while(end_episodio == False):

        disc_advances = False
        disc_Out = False
        center_DISC, center_ROBOT, frame = vision_Detection(camera, HSV_values)

        #--DRAW-LINES-----------------------------------------------------------
        if(drawLines==True):
            draw_margin_and_center(frame)
            draw_sector_lines(frame)

        #--DISC SECTOR POSITION CONTROL ----------------------------------------
        if(center_DISC is not None): #Si ha detectado un disco...

            pos_D0 = pos_D1
            caso, pos_D1 = update_actual_sector_position(
                                    center_DISC[0],center_DISC[1],pos_D0)

            #Posibles casos:
            # 'A' = Nuevo sector
            # 'B' = Disco no se ha movido de sector
            # 'C' = Disco fuera
            if((drawSectors==True) and (caso is not 'C')):
                colored_sector(frame, pos_D1)

            if(caso is 'A'):
                if(pos_D1[0]<=pos_D0[0]): #actual_sector[x] <= old_sector[x]

                    disc_advances = True

                    #Si quisiésemos pintar una flecha por dónde se mueve el disco:
                    pt1 = calcRobotPos_in_mm(pos_D0)
                    pt2 = calcRobotPos_in_mm(pos_D1)
                    cv2.arrowedLine(frame, pt1, pt2, (0, 100, 255), thickness=3)

            elif(caso is 'C'):
                pos_D0 = (-2,-2)
                disc_Out = True

        #--ROBOT SECTOR POSITION CONTROL ------------------------------------------------
        if (disc_advances) and (center_ROBOT is not None):

            caso, pos_R = update_actual_sector_position(
                                    center_ROBOT[0],center_ROBOT[1],pos_R)


            S_1 = calculoEstado(pos_D0, pos_D1, pos_R)


            # Guardar experiencia si no es la primera vez
            if first_action == False:
                experience = [S,a,rr,S_1]
                experiences.append(experience)

            a = elegirAccionAleatoria(pos_R)
            #a = elegirAccion(pos_R, S, Q, epsilon_v)

            #Si se debe mover...
            if (a is not 8): #a = 8 cuando la acción es no moverse
                target_sector_R = siguientePosRobot(pos_R, a)
                target_mm_R = calcRobotPos_in_mm(target_sector_R)

                # Enviamos ordenes al Robot para que alcance la posición:
                sendToRobot(s,target_mm_R,center_ROBOT,'a',2) #slow

                pos_R = target_sector_R


            #RECOMPENSA INMEDIATA
            # Calculo recompensa --> rr
            rr = recompensaInmediata(pos_R, pos_D1)
            #rr = 0.00001 #De esta forma cuenta como "entrenado"

            pos_D0 = pos_D1
            S = S_1

            first_action = False


        # # Si detecta el disco fuera del tablero, enviamos ordenes al Robot
        # # para que vuelva hacia el lado de la portería:
        # if(disc_Out is True) and (center_ROBOT is not None):
        #
        #     caso, pos_R = update_actual_sector_position(
        #                             center_ROBOT[0],center_ROBOT[1],pos_R)
        #
        #     #Si se debe mover...
        #     if (pos_R[0] is not 0):
        #         target_sector_R = (0,pos_R[1])
        #         target_mm_R = calcRobotPos_in_mm(target_sector_R)
        #
        #         dataa = bytearray(15)
        #         dataa = setMessageUDP(target_mm_R,center_ROBOT,'t') #t = training slow
        #
        #         try:
        #             s.send(''.join(chr(x) for x in dataa))
        #         except Exception as e:
        #             print("Something's wrong with the sending...")


        # show the frame to our screen
        cv2.imshow("IceQueen Vision", frame)

        # ¿Has pulsado una tecla?
        key = cv2.waitKey(1) & 0xFF

        if (key == 27)or(key == ord("q")): #Pulsando Q/Esc para salir
            exitIceQueen(camera, s)
            break

        elif(disc_Out==True) or (key == ord("s")):# or (pos_D1[0]==0):

            if(disc_Out==True):
                print '(!) Episodio termina porque algo falla con la detección dentro de la mesa'
                print '\n center_ROBOT = ', center_ROBOT
                print ' center_DISC  = ', center_DISC
                print ' disc_Out = ', disc_Out
                print '\n'
            elif (pos_D1[0]==0):
                print 'Disco llega a nivel 0 (lado portería)'
            else:
                print 'Lanzamiento detenido'

            end_episodio = True

            print'Pulsa Recompensa (u otra tecla para no tener en cuenta el lanzamiento) >> '
            key = cv2.waitKey(0) & 0xFF
            respuesta = chr(key)

            nu = int(respuesta)

            if nu > 0: #is in range(0,6): #[0,1,2,3,4,5]
                _, experiences = actualizarUltimaEx(experiences, respuesta)
            else:
                # Borro experiencias de episodio
                experiences = []
                #salgo del bucle sin entrenar Q
                break


        elif (key == ord('1')): #Detener episodio pero recompensando [+10] :)
            end_episodio, experiences = actualizarUltimaEx(experiences, '1')
        elif (key == ord('2')): #Detener episodio pero recompensando [+5] :)
            end_episodio, experiences = actualizarUltimaEx(experiences, '2')
        elif (key == ord('3')): #Detener episodio pero recompensando [+1] ~~
            end_episodio, experiences = actualizarUltimaEx(experiences, '3')
        elif (key == ord('4')): #Detener episodio pero recompensando [-5] :(
            end_episodio, experiences = actualizarUltimaEx(experiences, '4')
        elif (key == ord('5')): #Detener episodio pero recompensando [-10] :(
            end_episodio, experiences = actualizarUltimaEx(experiences, '5')
        elif (key == ord('0')):
            print ('No hay recompensa extra...')


        if(end_episodio == True):
            # Si el episodio se ha acabado: entreno Q con las experiencias
            #print '\n Experiencias en este lanzamiento = ', experiencias

            Q = Entrena_Q_con_Experiencias(Q, experiences, velAprendizaje, factorDescuento, num_veces)

            # Borro experiencias de episodio
            experiences = []

            # Calculo porcentaje entrenamiento y muestro en pantalla
            porcentajeEntrenamiento = calculaNivelEntrenamientoQ(Q, True)

            no_entrenadas = 100-porcentajeEntrenamiento
            epsilon_v = no_entrenadas/100


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Cleanup the camera and close any open windows or socket
exitIceQueen(camera, s)
