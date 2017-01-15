#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------
#------------------------------------------------------------------------
#---  OTRAS FUNCIONES NECESARIAS ----------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------

import numpy as np
import cv2

from Const import *

from random import randint
from random import random
from random import choice

#------------------------------------------------------------------------
#-   FUNCIONES PARA NAVEGAR ENTRE ESTADOS Y TRAYECTORIAS ----------------
#------------------------------------------------------------------------

# Size of the PLAYING COURT ---> Rectangle margin
#   ------------------------------------------> X
#   |   mUP .-------------------.          |
#   |       |                   |          |
#   |       |                   |          |
#   |       |                   |          |
#   |       .-------------------. mDOWN    |
#   |--------------------------------------
#   Y

# Update actual sector position function :
#-----------------------------------------------
def update_actual_sector_position(ix,iy,actual_sector):

    # A = Nuevo sector
    # B = Disco no se ha movido
    # C = Disco fuera

    #Si no te has salido de la matriz:
    if (mUP_X<ix<mDOWN_X) & (mUP_Y<iy<mDOWN_Y):
        newXsector = (ix-mUP_X) // SEC_SIZ
        newYsector = (iy-mUP_Y) // SEC_SIZ

        # Si el disco está en posición 700-710 --> sector X=6 no 7
        if(newXsector == NUM_SEC_X):
            newXsector = NUM_SEC_X-1

        #Si el sector ha cambiado, actualiza la variable y sennala nuevo sector
        if (actual_sector[0] is not newXsector) or (actual_sector[1] is not newYsector):
            actual_sector = (newXsector,newYsector)
            return 'A', (newXsector,newYsector) #Nuevo sector

        else:
            return 'B', actual_sector #Disco no se ha movido

    else:
        return 'C', (-1,-1) #Disco fuera

def lanzamientoCompletoDisco():

    croSectors = []

    # Genero nueva posición inicial:
    # El disco siempre empieza en borde derecho:
    ix = mDOWN_X - 11
    iy = randint(mUP_Y+2,mDOWN_Y-2)

    # Genero nuevas velocidades iniciales:
    vx = randint(-10,-5) # Random entre -10 y -1 : siempre avanza
    vy = randint(-10,10) # Random entre -10 y 10

    old_sector = (-10,-10)
    #actual_sector = (-1,-1)

    # Ejecuto trayectoria hasta que pelota esté en X = 0
    while(old_sector[0] is not 0):

        # Compruebo si se produce REBOTE y actualizo velocidades:
        if (iy + vy)<= mUP_Y:
            vy = -vy
        elif (iy + vy)>= mDOWN_Y:
            vy = -vy

        # Si velocidad es constante -->
        ix = ix + vx
        iy = iy + vy

        caso, actual_sector = update_actual_sector_position(
                                ix,iy,old_sector)

        if caso is 'A': #Nuevo sector
            croSectors.append(actual_sector)
            old_sector = actual_sector

    return croSectors


# Función para calcular la posición que tendria que tener el robot en mm para
# estar en un sector concreto.
def calcRobotPos_in_mm(pos_R):

    ix = pos_R[0]*SEC_SIZ + mUP_X + SEC_SIZ/2
    iy = pos_R[1]*SEC_SIZ + mUP_Y + SEC_SIZ/2

    return (ix,iy)

# print("Posicion para sector (1,1): ")
# print(calcRobotPos_in_mm((0,0)))

# Función que devuelve el siguiente sector del Disco
def PosDisco(croSectors,step):
    return croSectors[step]

# Función para calcular el nuevo sector del robot al realizar acción 'a'
def siguientePosRobot(pos_R, a):

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


# Función para detectar en qué trayectoria nos encontramos. (-99 si mueve atrás)
#       Ejemplo:
#            detectarTray((5,1),(4,0)) = 20  [...mirar cuaderno]
#            detectarTray((0,0),(1,1)) = -99 ERROR se ha movido hacia atrás
#
def detectarTray(pos_D0, pos_D1):

    x = 0
    y = 1
    star = 0

    # TRAYECTORIAS POSIBLES DISCO:
    #    .-----.-----.-----.-----.
    #    |     | -1\ | -2  |  ** |
    #    |     |    \|  |  |     |
    #    .-----.-----\--|--.-----.
    #    |     | 0 --- D D |  ** |
    #    |     |     | D D |     |
    #    .-----.-----/--|--.-----.
    #    |     |   / |  |  |  ** |
    #    |     | +1  | +2  |     |
    #    .-----.-----.-----.-----.

    if(pos_D1[x] > pos_D0[x]):
        return -99

    if(pos_D1[y] < pos_D0[y]): #Si esto se cumple es negativo
        if(pos_D1[x] < pos_D0[x]):
            star=-1
        else:
            star=-2
    elif(pos_D1[y] > pos_D0[y]): #Si esto se cumple es positivo
        if(pos_D1[x] < pos_D0[x]):
            star=1
        else:
            star=2

    trayectoria = star + pos_D0[y]*5 + (NUM_SEC_X-1-pos_D0[x])*TRAY_POR_NIVEL

    return trayectoria

# Función que devuelve un movimiento de disco aleatorio
def movimientoDiscoAleatorio(pos_D0):

# TRAYECTORIAS POSIBLES DISCO: 5 o 3 en los extremos.
#    .-----.-----.-----.    .-----.-----.-----.
#    |     | 2 \ |  1  |    |     | 2 \ |  1  |
#    |     |    \|  |  |    |     |    \|  |  |
#    .-----.-----\--|--.    .-----.-----\--|--.
#    |     | 3 --- D D |    |     | 3 --- D D |
#    |     |     | D D |    |     |     | D D |
#    .-----.-----/--|--.    .-----.-----.-----.
#    |     |   / |  |  |
#    |     | 4   |  5  |       ttt = 1,2,3,4,5
#    .-----.-----.-----.

    # Detecto si está pegado a los límites:
    if pos_D0[1]==0:                #Top
        ttt = randint(3,5)
    elif pos_D0[1]==(NUM_SEC_Y-1):  #Bottom
        ttt = randint(1,3)
    else:
        ttt = randint(1,5)

    if(ttt==1):
        D1 = [pos_D0[0],   pos_D0[1]-1]
    elif(ttt==2):
        D1 = [pos_D0[0]-1, pos_D0[1]-1]
    elif(ttt==3):
        D1 = [pos_D0[0]-1, pos_D0[1]]
    elif(ttt==4):
        D1 = [pos_D0[0]-1, pos_D0[1]+1]
    else:
        D1 = [pos_D0[0],   pos_D0[1]+1]

    return D1

#Distancia del robot al disco en unidades de cuadrantes:
def distancia(A, B):

    dx = B[0] - A[0]
    dy = B[1] - A[1]
    dalcuadrado = dx**2 + dy**2
    resultado = dalcuadrado**0.5  #sqrt

    return resultado


def recompensaInmediata(pos_R, pos_D):  #(S, a, S_1)

    dist = distancia(pos_R, pos_D)

    if dist == 0:
        rr = 10 #Si atrapó el disco
    else:
        rr = 1/dist
        #if pos_D[0]<pos_R[0]: #Si el disco ha pasado al robot...
        #    rr = -rr

    return rr

# Función para calcular acciones legales
def calcularAccionesLegales(pos_R):

    xminn,yminn,xmaxx,ymaxx = ROBOT_LIMITS #Posiciones límite para el robot
    xX = pos_R[0]
    yY = pos_R[1]

    # ACCIONES POSIBLES: 9        ¡Pero cuidado robot con límites!
    #    .-----.-----.-----.(X)
    #    |  0  |  3  |  5  |
    #    |     |     |     |
    #    .-----.-----.-----.        .-----.-----.-----.
    #    |  1  |  8  |  6  |        |  3  |  5  |     |
    #    |     | [R] |     |        |  |  |/    |     |
    #    .-----.-----.-----.        .--|--/-----.-----.
    #    |  2  |  4  |  7  |        | D D---- 6 |     |
    #    |     |     |     |        | D D |     |     |
    # (Y).-----.-----.-----.        .-----.-----.-----.

    acciones_posibles = []
    opciones = []
    for i in range(9):        # De 0 a 8
        opciones.append(True)   #[True, True, True, True, True, True, True, True, True]

    if xX==xminn:
        #Límite IZQ -> eliminamos 0,1,2
        for i in [0,1,2]:
            opciones[i]=False
    elif xX==xmaxx:
         #Límite DRCH -> eliminamos 5,6,7
         for i in [5,6,7]:
             opciones[i]=False

    if yY==yminn:
        #Límite TOP -> eliminamos 0,3,5
        for i in [0,3,5]:
            opciones[i]=False
    elif yY==ymaxx:
         #Límite BOT -> eliminamos 2,4,7
         for i in [2,4,7]:
             opciones[i]=False

    #De esta forma tenemos en acciones[] sólo las opciones válidas en plan: [3,5,6,8]
    for i in range(9):
        if opciones[i]==True:
            acciones_posibles.append(i)

    return acciones_posibles

#----------------------------------------------------------------------
#---    DRAWING FUNCTIONS    ------------------------------------------
#----------------------------------------------------------------------

# Draw Margin Lines & Center function:
def draw_margin_and_center(imgg):
    # Center:
    cv2.circle(imgg,(FRAME_X/2, FRAME_Y/2), 5,
                     (10, 10, 10), 2)

    # Margin table rectangle:
    cv2.rectangle(imgg,(mUP_X,mUP_Y),
                        (mDOWN_X, mDOWN_Y),
                        (255, 255, 0), 1)

# Draw Sector Lines function
#-------------------------------
def draw_sector_lines(imgg):

    # Draw lines with thickness of 'tt' px and color 'cc'
    tt = 1
    cc = (255, 255, 0)

    # Vertical lines...
    for i in range(1,NUM_SEC_X):
        pun = mUP_X+i*SEC_SIZ
        cv2.line(imgg,(pun,mUP_Y),(pun,mDOWN_Y),cc,tt)

    # Vertical lines...
    for i in range(1,NUM_SEC_Y):
        pun = mUP_Y+i*SEC_SIZ
        cv2.line(imgg,(mUP_X,pun),(mDOWN_X, pun),cc,tt)

# Colored crossed sector function
#-----------------------------------
def colored_sector(imggg, actual_sec):

    cro_secX = actual_sec[0]
    cro_secY = actual_sec[1]

    # Draw rectangles and color 'cc'
    ini = (cro_secX*SEC_SIZ+mUP_X, cro_secY*SEC_SIZ+mUP_Y)
    fin = (cro_secX*SEC_SIZ+mUP_X+SEC_SIZ, cro_secY*SEC_SIZ+mUP_Y+SEC_SIZ)

    cc = (200,255,200)
    alpha = 0.4

    overlay = imggg.copy()
    cv2.rectangle(overlay,ini,fin,cc,-1)

    # apply the overlay
    cv2.addWeighted(overlay, alpha, imggg, 1 - alpha,0, imggg)


#----------------------------------------------------------------------
#---    UPD COMMUNICATIONS    -----------------------------------------
#----------------------------------------------------------------------
def sendToRobot(socket,target,robotCoord, typo='a', vel=3):

    dataa = bytearray(15)
    dataa = setMessageUDP(target,robotCoord,typo,vel)

    try:
        socket.send(''.join(chr(x) for x in dataa))
    except Exception as e:
        print("Something's wrong with the sending...")

def setMessageUDP(target,robotCoord, typo='a', vel=3):

        target_X = target[0]
        target_Y = target[1]
        robotCoordX = robotCoord[0]
        robotCoordY = robotCoord[1]

        dato = bytearray(15) #3+12
        dato[0] = 0x6D  #m
        dato[1] = 0x6D  #m

        if(typo is 'a'):
            dato[2] = 0x61  #a
        else:
            dato[2] = 0x32  #2


        # LOS EJES DEL PROGRAMA ARDUINO ESTÁN INVERTIDOS
        # X <---> Y

        # Pos_X (high byte, low byte)
        dato[3] = (target_Y>>8)&0xFF
        dato[4] = target_Y&0xFF
        # Pos_Y (high byte, low byte)
        dato[5] = (target_X>>8)&0xFF
        dato[6] = target_X&0xFF

        #define MAX_ACCEL 275
        #define MAX_SPEED 32000
        #define MIN_ACCEL 100
        #define MIN_SPEED 5000
        if(vel is 3):       #fast playing
            accel = ACCEL_FAST  #150
            sppeed = SPEED_FAST #20000
        elif(vel is 2):     #normal training
            accel = ACCEL_SLOW  #130
            sppeed = SPEED_SLOW #10000
        else:               #very slow mode
            accel = ACCEL_SLOW  #100
            sppeed = MIN_SPEED  #5000

        # robot_speed (high byte, low byte)
        dato[7] = (sppeed>>8)&0xFF
        dato[8] = sppeed&0xFF
        # robot_accel (high byte, low byte)
        dato[9] = (accel>>8)&0xFF
        dato[10] = accel&0xFF

        # robotPos_X (high byte, low byte)
        dato[11] = (robotCoordY>>8)&0xFF
        dato[12] = robotCoordY&0xFF
        # robotPos_Y (high byte, low byte)
        dato[13] = (robotCoordX>>8)&0xFF
        dato[14] = robotCoordX&0xFF

        #print(''.join(chr(x) for x in dato))
        #s.send(''.join(chr(x) for x in dato))

            # Python 3
            #key = bytes([0x13, 0x00, 0x00, 0x00, 0x08, 0x00])

            # Python 2
            #key = ''.join(chr(x) for x in [0x13, 0x00, 0x00, 0x00, 0x08, 0x00])

        return dato

#------------------------------------------------------------------------
#-  GUARDANDO Y LEYENDO FICHEROS  ---------------------------------------
#------------------------------------------------------------------------
import pickle  # módulo para la lectura/escritura de datos

def saveData(dataa, file_name = 'dataa.dat'):

    filee = open(file_name, 'wb') # Abre archivo binario para escribir
    pickle.dump(dataa, filee)     # Escribe en archivo
    filee.close                   # Cierra archivo

def readData(file_name = 'dataa.dat'):

    archivo = open(file_name, 'rb') # Abre archivo binario para escribir
    dataa = pickle.load(archivo)    # Lee desde archivo
    archivo.close                   # Cierra archivo

    return dataa                    # Devuelve lectura


# Actualizar última experiencia
#   experiencias[-1][2] = valor nuevo
def actualizarUltimaEx(experiencias, res):

    end_episodio = True

    if(experiencias == []):
        return end_episodio, experiencias

    # print'''
    #     \t 1 - ¡PERFECTO!       :) Recompensa muy positiva
    #     \t 2 - Bien             :) Recompensa positiva
    #     \t 3 - Regular...
    #     \t 4 - Mal              :( Recompensa negativa
    #     \t 5 - ¡Muy MAL!        :( Recompensa muy negativa
    # '''
    # res = raw_input('>> ')

    if (res == '1'): #Recompensando [+20] :)
        print '¡BRAVO ROBOT! :)'
        experiencias[-1][2] = 10

    elif (res == '2'): #Recompensando [+10] :)
        print '¡Muy bien robot! :)'
        experiencias[-1][2] = 5

    elif (res == '3'): #Recompensando [+1] ~~
        print 'No está mal, pero sigue intentándolo... :/'
        experiencias[-1][2] = 1

    elif (res == '4'): #Recompensando [-5] :()
        print 'Mal robot :('
        experiencias[-1][2] = -5

    elif (res == '5'): #Recompensando [-5] :()
        print '¡Muy MAL! :('
        experiencias[-1][2] = -10

    return end_episodio, experiencias
