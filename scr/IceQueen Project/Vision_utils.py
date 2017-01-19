#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------
#------------------------------------------------------------------------
#---  FUNCIONES DE VISIÓN Y CALIBRACIÓN DE LOS VALORES HSV --------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------

import numpy as np
import imutils
import cv2

from Const import FRAME_X
from Const import FRAME_Y

# Minimun radius of the discs detected
minimimRobotRadius = 10 #10
minimimDiscRadius = 10  #20

# Valores de color HSV Experimentales:
# greenLower = (41, 122, 29)
# greenUpper = (95, 255, 138)
# blueLower = (101,195,62)
# blueUpper = (125,255,182)
# HSV_values = greenLower,greenUpper,blueLower,blueUpper
# saveData(HSV_values,'d_valuesHSV.dat')

# detectGREEN = True
# detectBLUE = True

def exitIceQueen(camera, socket):
    # Cleanup the camera and close any open windows or socket
    camera.release()
    cv2.destroyAllWindows()
    socket.close()
    quit()

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
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  #frame --> blurred

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

def vision_Detection(camera, HSV_values, detectBLUE=True, detectGREEN=True):

    greenLower,greenUpper,blueLower,blueUpper = HSV_values

    # Grab the current frame
    _g, frame_original = camera.read()

    # Resize & crop the frame, blur it, and convert it to the HSV
    # color space
    #TAMAÑO pantalla después de resize: 640x480 --> 800x600
    frame = imutils.resize(frame_original, width=FRAME_X)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #frame --> blurred

    # Init detect positions
    center_DISC = None
    center_ROBOT = None

    #--BLUE------------------------------------------------------------
    if(detectBLUE):

        # construct a mask_blue for the color "blue", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask_blue
        mask_blue = cv2.inRange(hsv, blueLower, blueUpper)
        mask_blue = cv2.erode(mask_blue, None, iterations=2)
        mask_blue = cv2.dilate(mask_blue, None, iterations=2)
        #cv2.imshow("BlueMask", mask_blue)

        # find contours in the mask_blue and initialize the current
        # (x, y) center of the robot
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
                            (100, FRAME_Y - 40), cv2.FONT_HERSHEY_SIMPLEX,
                            0.70, (255, 0, 0), 1)  #(232,175,104)
                cv2.putText(frame, "X: {}, Y: {}".format(center_ROBOT[0],center_ROBOT[1]),
                            (100, FRAME_Y - 20), cv2.FONT_HERSHEY_SIMPLEX,
                            0.70, (255, 0, 0), 1) #(232,175,104)

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
                            (600, FRAME_Y - 40), cv2.FONT_HERSHEY_SIMPLEX,
                            0.70, (0, 10, 0), 1)
                cv2.putText(frame, "X: {}, Y: {}".format(center_DISC[0],center_DISC[1]),
                            (600, FRAME_Y - 20), cv2.FONT_HERSHEY_SIMPLEX,
                            0.70, (0, 10, 0), 1)

    return center_DISC, center_ROBOT, frame
