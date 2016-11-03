#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las lineas anteriores son xa q python reconozca acentos


import cv2
import numpy as np
from random import randint

print('-> Pulsa Q para salir.')
print('-> Pulsa N para nueva trayectoria.')

#-------------------------------

# Numero de sectores en la matriz. Normalmente 7x5
#   ______X
#   |
#   |
#  Y
num_secX = 5
num_secY = 7

# Tamannos maximos de la matriz
sizeX = num_secX*100
sizeY = num_secY*100

new_tray = True # new trajectory

# Variable que guarda los sectores cruzados
crossedSectors = []

# Actual sector
actual_sector = (-9,-9)

# BALL initial position
ix = randint(0,sizeX) # Random entre 0 y sizeX
iy = 0

# Velocidades iniciales:
vx = randint(-10,10) # Random entre -10 y 10
vy = randint(1,10)   # Random entre   1 y 10

vx_min = 1
vy_min = 1

# Coeficiente de friccion:
DISC_FRICTION=0.1

# Tiempo simulado
time = 0

# Función para crear imagenes-matriz vacías corrigiendo coordenadas:
def imagenVacia(sizeXX, sizeYY):
    return np.zeros((sizeYY,sizeXX,3), np.uint8)

# Creamos unas imagenes vacias (de ceros)
tablero = imagenVacia(sizeX, sizeY)

# Creamos ventanas
cv2.namedWindow('Generador de Trayectorias')
cv2.moveWindow('Generador de Trayectorias',0,0)

#----------------------------------------------------------------
#----------------------------------------------------------------

# Sector Lines function
#-------------------------------
def draw_sector_lines(imgg):

    # Draw lines with thickness of 'tt' px and color 'cc'
    tt = 1
    cc = (200,200,200)

    # Horizontal lines...
    for i in range(1,num_secY):
        cv2.line(imgg,(0,i*100),(sizeX,i*100),cc,tt)

    # Vertical lines...
    for i in range(1,num_secX):
        cv2.line(imgg,(i*100,0),(i*100,sizeY),cc,tt)



# Colored crossed sectors function
#-------------------------------
def colored_crossed_sectors(imggg):
    global actual_sector

    cro_secX = actual_sector[0]
    cro_secY = actual_sector[1]

    # Draw rectangles and color 'cc'
    ini = (cro_secX*100, cro_secY*100)
    fin = (cro_secX*100 + 100, cro_secY*100 + 100)

    cc = (200,255,200)

    cv2.rectangle(imggg,ini,fin,cc,-1)



# Update actual sector position function :
#-----------------------------------------------
def update_actual_sector_position():
    global actual_sector, ix, iy

    #Si no te has salido de la matriz:
    if (0<ix<sizeX) and (0<iy<sizeY):
        actualX = ix // 100
        actualY = iy // 100

        #Si el sector ha cambiado, actualiza la variable y sennala nuevo sector
        if (actual_sector[0] is not actualX) or (actual_sector[1] is not actualY):
            actual_sector = (actualX,actualY)
            return True

        else:
            return False

    else:
        return False

#----------------------------------------------------------------
#----------------------------------------------------------------



# Programa Principal:
#---------------------------------------------
while(1):

    if new_tray is True:

        # Borramos la trayectoria anterior y los sectores
        tablero = imagenVacia(sizeX, sizeY)
        crossedSectors = []

        # Genero nueva posición inicial:
        ix = randint(0,sizeX) # Random entre 0 y sizeX
        iy = 0

        # Genero nuevas velocidades iniciales:
        vx = randint(-10,10) # Random entre -10 y 10
        vy = randint(1,10)   # Random entre   1 y 10


        # Ejecuto trayectoria hasta que pelota esté en Y maxima
        while(iy < sizeY):

            # Compruebo si se produce REBOTE y actualizo velocidades:
            if (ix + vx)<=0:
                vx = -vx
            elif (ix + vx)>=sizeX:
                vx = -vx

            # # Ejecuto una fricción en velocidad eje Y
            # vy_ = vy - DISC_FRICTION*time
            # if (abs(vy_)>vy_min):
            #     vy = int(vy_)


            # ACTUALIZO POSICION PELOTITA:
            # Si velocidad fuese constante -->
            ix = ix + vx
            iy = iy + vy

            time = time + 1


            # ACTUALIZO SECTORES:
            new_sector = update_actual_sector_position()
            if new_sector is True:
                #Pintamos y annadimos el nuevo sector
                colored_crossed_sectors(tablero)
                crossedSectors.append(actual_sector)

            cv2.circle(tablero,(ix,iy),2,(0,255,0),2)

        draw_sector_lines(tablero)
        cv2.imshow('Generador de Trayectorias',tablero)

        print ('Tiempo relativo: %d' % time)
        print ('Sectores cruzados en la trayectoria = %d' % len(crossedSectors))
        print crossedSectors

        new_tray = False

    # Pulsar 'Q' para SALIR o 'N' para siguiente trayectoria
    k = cv2.waitKey(1) & 0xFF
    if k == ord('n'):
        new_tray = True
        time = 0
    elif k == 27 or k == ord('q'):  # Pulsar 'Q' o ESC para SALIR
        break


cv2.destroyAllWindows()
