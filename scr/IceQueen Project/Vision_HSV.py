#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------
#------------------------------------------------------------------------
#---  FUNCIONES DE CALIBRACIÓN DE LOS VALORES HSV -----------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------

import numpy as np
import imutils
import cv2

from Const import FRAME_X

def nothing(x):
    pass

def calibrate_HSV(camera, colorLower=(0,0,0), colorUpper=(179,255,255), nameColor='OCTARINO'):

    # Creating a window for later use
    cv2.namedWindow('Valores HSV')

    print ("""
    ....Calibrando el color %s
    ------------------------------------------------
    \t K / Esc - para Aceptar y Salir
    \n
    """ % (nameColor))

    hL = colorLower[0]
    sL = colorLower[1]
    vL = colorLower[2]
    hU = colorUpper[0]
    sU = colorUpper[1]
    vU = colorUpper[2]

    # Creating a window for later use
    cv2.namedWindow('Valores HSV')

    # Creating track bar
    cv2.createTrackbar('hL', 'Valores HSV',hL,179,nothing)
    cv2.createTrackbar('hU', 'Valores HSV',hU,179,nothing)
    cv2.createTrackbar('sL', 'Valores HSV',sL,255,nothing)
    cv2.createTrackbar('sU', 'Valores HSV',sU,255,nothing)
    cv2.createTrackbar('vL', 'Valores HSV',vL,255,nothing)
    cv2.createTrackbar('vU', 'Valores HSV',vU,255,nothing)

    while True:

        _, frame_original = camera.read()

        # Resize & crop the frame, blur it, and convert it to the HSV
        # color space
        #TAMAÑO pantalla después de resize: 640x480 --> 800x600
        frame = imutils.resize(frame_original, width=FRAME_X)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #converting to HSV
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

        # get info from track bar and appy to result
        hL = cv2.getTrackbarPos('hL','Valores HSV')
        sL = cv2.getTrackbarPos('sL','Valores HSV')
        vL = cv2.getTrackbarPos('vL','Valores HSV')
        hU = cv2.getTrackbarPos('hU','Valores HSV')
        sU = cv2.getTrackbarPos('sU','Valores HSV')
        vU = cv2.getTrackbarPos('vU','Valores HSV')

        # Normal masking algorithm
        lower_color = np.array([hL,sL,vL])
        upper_color = np.array([hU,sU,vU])

        mask = cv2.inRange(hsv,lower_color, upper_color)

        result = cv2.bitwise_and(frame,frame,mask = mask)

        cv2.imshow('Valores HSV',result)

        key = cv2.waitKey(1) & 0xFF
        if (key == 27)or(key == ord("k"))or(key == ord("q")):
            break

    cv2.destroyAllWindows()

    colorL = (hL,sL,vL)
    colorU = (hU,sU,vU)

    print "\t %s Lower = (%d,%d,%d)" % (nameColor,hL,sL,vL)
    print "\t %s Upper = (%d,%d,%d)" % (nameColor,hU,sU,vU)

    return colorL,colorU
