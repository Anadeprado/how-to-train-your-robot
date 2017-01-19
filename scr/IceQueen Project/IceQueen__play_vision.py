#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las líneas anteriores son para que python reconozca acentos

###########################################################################
# ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
#   Author: Anita de Prado
#   Hardware: Arduino Mega2560 + JJROBOTS brain shield v3 (devia)
#
#   Date: 18/01/2017
#   Version: 2
#
# License: Open Software GPL License
###########################################################################
#   >>> PLAY with VISION CONTROL
#       - Detect green Disc & blue Robot
#       - Send UPD packets to Arduino (Wifi: JJROBOTS_78 // pass=87654321)
###########################################################################

import numpy as np
import argparse
import imutils
import cv2
import socket

from Const import *
from Q_utils import *
from Q_space import *
from Vision_utils import *

# Playing speed
#   3 = fast playing
#   2 = normal training
#   1 = very slow
vel_play = 3

# Actual & old sector positions
pos_R = (-1,-1)
pos_D = (-1,-1)
pos_D0 = (-2,-2)

# If the disk moves to a new sector and does not move backward
disc_advances = False
disc_Out = False

# ----------------------------------------------
drawLines = True
drawSectors = True
# ----------------------------------------------

print("...Cargando valores HSV")
HSV_values = readData('d_valuesHSV.dat')
print("-OK")

print("...Cargando espacio Q ya entrenado")
Q = readData('d_Qspace.dat')
print("-OK")

#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# This is the IP & port number that ESP opens
HOST = "192.168.4.1"
PORT = 2222
print("...Abriendo conexion Wifi UDP en 192.168.4.1:2222")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   #Socket UPD
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

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out_video = cv2.VideoWriter('out_video.avi',fourcc, 20.0, (FRAME_X,FRAME_Y))

video_record = False



#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
print ("""
====================================================
--VISION POR COMPUTADOR DEL PROYECTO ICE-QUEEN------
====================================================
\t 1 - PLAY
\t 2 - Calibrar los valores HSV
\t 3 - Utilizar Q del entrenamiento real
\n\t Q - Salir
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

elif(respuesta is '3'):
    print("...Cargando espacio Q ya entrenado manualmente")
    Q = readData('d_Qspace_real.dat')
    print("-OK")

print ("""\n\n\n
----------------------------------------------------
\nPLAYING ICE-QUEEN
----------------------------------------------------
\t G - START grabación
\t S - STOP grabación
\n
\t Q / Esc - para Salir
\n
""")
# Keep looping
while True:

    disc_advances = False
    disc_Out = False

    center_DISC, center_ROBOT, frame = vision_Detection(camera, HSV_values)

    #--DRAW-LINES-----------------------------------------------------------
    if(drawLines==True):

        draw_margin_and_center(frame)
        draw_sector_lines(frame)


    #--DISC SECTOR POSITION CONTROL ------------------------------------------------
    if(center_DISC is not None): #Si ha detectado un disco...

        pos_D0 = pos_D
        caso, pos_D = update_actual_sector_position(
                                center_DISC[0],center_DISC[1],pos_D)

        #Posibles casos:
        # 'A' = Nuevo sector
        # 'B' = Disco no se ha movido de sector
        # 'C' = Disco fuera
        if((drawSectors==True) and (caso is not 'C')):
            colored_sector(frame, pos_D)

        if(caso is 'A'):
            if(pos_D[0]<=pos_D0[0]): #actual_sector[x] <= old_sector[x]

                disc_advances = True

                #Si quisiésemos pintar una flecha por dónde se mueve el disco:
                pt1 = calcRobotPos_in_mm(pos_D0)
                pt2 = calcRobotPos_in_mm(pos_D)
                cv2.arrowedLine(frame, pt1, pt2, (0, 100, 255), thickness=3)


        elif(caso is 'C'):
            pos_D0 = (-2,-2)

            disc_Out = True


    #--ROBOT SECTOR POSITION CONTROL ------------------------------------------------
    if (disc_advances) and (center_ROBOT is not None):

        caso, pos_R = update_actual_sector_position(
                                center_ROBOT[0],center_ROBOT[1],pos_R)

        S = calculoEstado(pos_D0, pos_D, pos_R)
        a = elegirAccionMEJOR(pos_R, S, Q)

        #Si se debe mover...
        if (a is not 8): #a = 8 cuando la acción es no moverse
            target_sector_R = siguientePosRobot(pos_R, a)
            target_mm_R = calcRobotPos_in_mm(target_sector_R)

            # Enviamos ordenes al Robot para que alcance la posición:
            sendToRobot(s,target_mm_R,center_ROBOT,'a', vel_play) #default:fast

    # Por comodidad, si detecta el disco fuera del tablero,
    # enviamos ordenes al Robot para que vuelva hacia el lado de la portería:
    if(disc_Out is True) and (center_ROBOT is not None):

        caso, pos_R = update_actual_sector_position(
                                center_ROBOT[0],center_ROBOT[1],pos_R)
        #Si se debe mover...
        if (pos_R[0] is not 0):
            target_sector_R = (0,pos_R[1])
            target_mm_R = calcRobotPos_in_mm(target_sector_R)

            # Enviamos ordenes al Robot para que alcance la posición trasera despacio:
            sendToRobot(s,target_mm_R,center_ROBOT,'a',1) # very slow



    if video_record == True:
        out_video.write(frame)
        cv2.circle(frame, (FRAME_X-50,50), 20, (0, 255, 0), -1)

    # show the frame to our screen
    cv2.imshow("IceQueen Vision", frame)

    # cropped = frame[mUP_Y-30:FRAME_Y , mUP_X-30:mDOWN_X+30]
    # cv2.imshow("Cropped", cropped)

    key = cv2.waitKey(1) & 0xFF
    if (key == 27)or(key == ord("q")): #Pulsando la Q para salir
        break
    elif key == ord("g"):
        video_record = True
    elif key == ord("s"):
        video_record = False

#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Cleanup the camera and close any open windows or socket
out_video.release()
exitIceQueen(camera, s)
