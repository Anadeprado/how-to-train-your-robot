#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las lineas anteriores son xa q python reconozca acentos

###########################################################################
# ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
#   Author: Anita de Prado
#   Hardware: Arduino Mega2560 + JJROBOTS brain shield v3 (devia)
#
#   Date: 05/01/2017
#   Version: 0.00
#
# License: Open Software GPL License
###########################################################################
#   >>> PLAY with VISION CONTROL
#       - Detect green Disc & blue Robot
#       - Send UPD packets to Arduino (Wifi: JJROBOTS_78 // pass=87654321)
###########################################################################


# Import the necessary packages
import numpy as np
import argparse
import imutils
import cv2
import socket

from Const import *
from Q_utils import *
from Q_space import *
from Vision_HSV import *


# Actual & old sector positions
pos_R = (-1,-1)
pos_D = (-1,-1)
pos_D0 = (-2,-2)

#If the disk moves to a new sector and does not move backward
disc_advances = False
disc_Out = False

# ----------------------------------------------
detectGREEN = True
detectBLUE = True
drawLines = True
drawSectors = True

# Valores de color HSV Experimentales:
greenLower = (41, 122, 29)
greenUpper = (95, 255, 138)
blueLower = (101,195,62)
blueUpper = (125,255,145)
# greenLower = (48, 100, 37)
# greenUpper = (93, 255, 100)
# blueLower = (108,200,95)
# blueUpper = (116,255,157)


# Minimun radius of the discs detected
minimimRobotRadius = 10 #10
minimimDiscRadius = 20
# ----------------------------------------------


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#Esta es la IP y el puerto que abre el ESP
HOST = "192.168.4.1"
PORT = 2222
print("...Abriendo conexion Wifi UDP en 192.168.4.1:2222")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   #Creamos socket UPD
try:
    s.connect((HOST, PORT)) #Conectamos socket al servidor

except Exception as e:
    print("something's wrong with %s:%d. Exception is %s" % (HOST, PORT, e))

print("-OK")

print("...Cargando espacio Q ya entrenado")
Q = leerQ('d_Qspace.dat')
print("-OK")


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# CAMERA 1 = USB webcam
camera = cv2.VideoCapture(1)

if(camera.isOpened()==False):
    print("¡No hay camara conectada!")

# initialize the frame counter
counter = 0


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
print ("""
====================================================
--VISION POR COMPUTADOR DEL PROYECTO ICE-QUEEN------
====================================================
\t 1 - PLAY
\t 2 - Calibrar los valores HSV
\t 3 - Salir
\n
""")
respuesta = raw_input(">> "); # Respuesta del usuario

if(respuesta is '3'):
    quit()

elif(respuesta is '2'):

    #print("\n...Calibrando el VERDE para detectar DISCO...\n")
    greenLower, greenUpper = calibrate_HSV(camera, greenLower, greenUpper, 'VERDE')

    #print("\n...Calibrando el AZUL para detectar ROBOT...\n")
    blueLower, blueUpper = calibrate_HSV(camera, blueLower, blueUpper,'AZUL')


print ("""\n\n\n
----------------------------------------------------
\nPLAYING ICE-QUEEN
----------------------------------------------------
\t Q / Esc - para Salir
\n
""")
# Keep looping
while True:
    # Grab the current frame
    _g, frame_original = camera.read()

    # Resize & crop the frame, blur it, and convert it to the HSV
    # color space
    #TAMAÑO pantalla después de resize: 640x480 --> 800x600
    frame = imutils.resize(frame_original, width=FRAME_X)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Init detect positions
    center_DISC = None
    center_ROBOT = None
    disc_advances = False
    disc_Out = False

    #--BLUE------------------------------------------------------------
    if(detectBLUE):

        # construct a mask_blue for the color "blue", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask_blue
        mask_blue = cv2.inRange(hsv, blueLower, blueUpper)
        mask_blue = cv2.erode(mask_blue, None, iterations=2)
        mask_blue = cv2.dilate(mask_blue, None, iterations=2)
        #cv2.imshow("BlueMask", mask_blue)

        # find contours in the mask_green and initialize the current
        # (x, y) center of the disc
        cnts = cv2.findContours(mask_blue.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask_blue, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            M = cv2.moments(c)
            center_ROBOT = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > minimimRobotRadius:
                # draw the blue square and centroid on the frame,
                # then update the list of tracked points
                cv2.rectangle(frame,(int(x-radius),int(y-radius)),
                                    (int(x+radius), int(y+radius)),
                                    (255, 170, 90), 2)
                cv2.circle(frame, center_ROBOT, 5, (255, 0, 0), -1)
                #pts.appendleft(center)

                # show blue Center:
                cv2.putText(frame, "ROBOT:",
                            (100, FRAME_Y - 50), cv2.FONT_HERSHEY_SIMPLEX,
                            0.70, (232,175,104), 1)
                cv2.putText(frame, "X: {}, Y: {}".format(center_ROBOT[0],center_ROBOT[1]),
                            (100, FRAME_Y - 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.70, (232,175,104), 1)

    #--GREEN------------------------------------------------------------
    if(detectGREEN):

        # construct a mask_green for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask_green
        mask_green = cv2.inRange(hsv, greenLower, greenUpper)
        mask_green = cv2.erode(mask_green, None, iterations=2)
        mask_green = cv2.dilate(mask_green, None, iterations=2)
        #cv2.imshow("GreenMask", mask_green)

        # find contours in the mask_green and initialize the current
        # (x, y) center of the disc
        cnts = cv2.findContours(mask_green.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask_green, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)

            center_DISC = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > minimimDiscRadius:
                # draw the circle blue and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (20, 193, 20), 2)
                cv2.circle(frame, center_DISC, 5, (0, 100, 255), -1)
                #pts.appendleft(center)

                # show Center:
                cv2.putText(frame, "DISC:",
                            (400, FRAME_Y - 50), cv2.FONT_HERSHEY_SIMPLEX,
                            0.70, (0, 100, 255), 1)
                cv2.putText(frame, "X: {}, Y: {}".format(center_DISC[0],center_DISC[1]),
                            (400, FRAME_Y - 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.70, (0, 100, 255), 1)


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
            tar_mm_R = calcRobotPos_in_mm(target_sector_R)

            # Enviamos ordenes al Robot:
            dataa = bytearray(15)
            dataa = setMessageUDP(tar_mm_R,center_ROBOT,'a')
            #dataa = setMessageUDP(target,robotCoord, int typo=9)
            try:
                s.send(''.join(chr(x) for x in dataa))
            except Exception as e:
                print("Something's wrong with the sending...")

    # Si detecta el disco fuera del tablero, enviamos ordenes al Robot
    # para que vuelva hacia el lado de la portería:
    if(disc_Out is True) and (center_ROBOT is not None):

        caso, pos_R = update_actual_sector_position(
                                center_ROBOT[0],center_ROBOT[1],pos_R)

        #Si se debe mover...
        if (pos_R[0] is not 0):
            target_sector_R = (0,pos_R[1])
            tar_mm_R = calcRobotPos_in_mm(target_sector_R)

            dataa = bytearray(15)
            dataa = setMessageUDP(tar_mm_R,center_ROBOT,'2')

            try:
                s.send(''.join(chr(x) for x in dataa))
            except Exception as e:
                print("Something's wrong with the sending...")


    # show the frame to our screen and increment the frame counter
    cv2.imshow("Frame", frame)
    #counter += 1

    # cropped = frame[mUP_Y-30:FRAME_Y , mUP_X-30:mDOWN_X+30]
    # cv2.imshow("Cropped", cropped)


    key = cv2.waitKey(1) & 0xFF
    if (key == 27)or(key == ord("q")): #Pulsando la Q para salir
        break


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
# Close socket
s.close()
