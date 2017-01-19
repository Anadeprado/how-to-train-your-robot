#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------
#------------------------------------------------------------------------
#---  DECLARACIÓN DE CONSTANTES -----------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------

# Velocidad y aceleración de los motores paso a paso.
#   SLOW : durante el entrenamiento
#   FAST : para jugar
ACCEL_SLOW = 100     #100 - 150*
SPEED_SLOW = 10000   #5000 - 20000
ACCEL_FAST = 130
SPEED_FAST = 16000
    #define MAX_ACCEL 275
    #define MAX_SPEED 32000
    #define MIN_ACCEL 100
    #define MIN_SPEED 5000
MIN_SPEED = 6000


# Tamaño de pantalla 800x600 para que los pixeles coincidan con mm.
# El tamaño original es de 640x480. Después de hacer resize(width=800) que
# es una proporción (1.25) del original, queda así:
FRAME_X = 800 #frame.shape[1]
FRAME_Y = 600 #frame.shape[0]

# They define the length and width of the PLAYING COURT (not the TOTAL dimension
# of the AIR HOCKEY TABLE just the playing court)
TABLELENGTH = 710 # TABLE SIZE X IN mm
TABLEWIDTH = 400 # TABLE SIZE Y IN mm

# Size of the PLAYING COURT ---> Rectangle margin
#   ------------------------------------------> X
#   |   mUP .-------------------.          |
#   |       |                   |          |
#   |       |                   |          |
#   |       |                   |          |
#   |       .-------------------. mDOWN    |
#   |--------------------------------------
#   Y
#
mUP_X = (FRAME_X-TABLELENGTH)/2
mUP_Y = (FRAME_Y-TABLEWIDTH)/2
mDOWN_X = FRAME_X-mUP_X
mDOWN_Y = FRAME_Y-mUP_Y

# Numero de sectores en la matriz. Normalmente [7x4]
# NIVEL-> 0     1     2     3     4     5     6
#     .-----.-----.-----.-----.-----.-----.-----.---> X
#   0 |     |     |     |     |     |     |     |  |
#     |     |  R  |     |     |     |     |     |  |
#     .-----.-----.-----.-----.-----.-----.-----.
#   1 |  R  |     |     |     |     |     |     |  |
#     |     |     |     |     |     |  D  |     |  |
#     .-----.-----.-----.-----.-----.-----.-----.
#   2 |     |     |     |  D  |  D  |     |  D  |  |
#     |     |     |     |     |     |     |     |  |
#     .-----.-----.-----.-----.-----.-----.-----.
#   3 |     |     |     |     |     |     |     |  |
#     |     |     |     |     |     |     |     |  |
#     .-----.-----.-----.-----.-----.-----.-----.--.mDOWN
#     |
#    Y
#
NUM_SEC_X = 7
NUM_SEC_Y = 4
SEC_SIZ = 100 #Tamaño sectores

# Posiciones límites robot: (0,0)-->(3,3)
#   Ejemplo: nunca pise nivel 4, ni 5, ni 6...
rxMin,ryMin,rxMax,ryMax = 0,0,NUM_SEC_X-4,NUM_SEC_Y-1
ROBOT_LIMITS = rxMin,ryMin,rxMax,ryMax

# Posiciones totales posibles para el robot:
ROBOT_TOTAL_POS = (rxMax-rxMin+1)*(ryMax-ryMin+1) #16



# TRAYECTORIAS POSIBLES DISCO: 5 o 3 en los extremos
#    .-----.-----.-----.    .-----.-----.-----.
#    |     | 0 \ |  3  |    |     | 0 \ |  3  |
#    |     |    \|  |  |    |     |    \|  |  |
#    .-----.-----\--|--.    .-----.-----\--|--.
#    |     | 1 --- D D |    |     | 1 --- D D |
#    |     |     | D D |    |     |     | D D |
#    .-----.-----/--|--.    .-----.-----.-----.
#    |     |   / |  |  |
#    |     | 2   |  4  |
#    .-----.-----.-----.
# Numero de trayectorias por NIVEL (columna):
#TRAY_POR_NIVEL = (3*NUM_SEC_Y)-2        #8 por nivel:  1+3+3+1
TRAY_POR_NIVEL = (5*NUM_SEC_Y)-4         #16 por nivel: 3+5+5+3
NIVELES_ENTRENADOS = NUM_SEC_X -1        #El nivel 0 no se entrena: -1
TRAY_TOTALES = TRAY_POR_NIVEL*NIVELES_ENTRENADOS  #112 "capas"


# Número de ESTADOS: 1792
num_ESTADOS = TRAY_TOTALES * ROBOT_TOTAL_POS

# ACCIONES POSIBLES EN CADA ESTADO: 9
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
num_ACCIONES = 9

sec_XR = rxMax - rxMin
sec_YR = ryMax - ryMin
# 3 por arriba, 3 por abajo + 3drch + 3izq - 4 repetidas esquinas
# 6*sec_XR + 6*sec_YR - 4 = 32
#num_ACCIONES_NO_VALIDAS = 6*sec_XR + 6*sec_YR - 4 #32
num_ACCIONES_NO_VALIDAS = 6*sec_XR + 6*sec_YR - 4 #32
num_ACCIONES_QUE_JAMAS_SE_ENTRENARAN = num_ACCIONES_NO_VALIDAS*TRAY_TOTALES

# 10 del extremo
#num_TRAYECTORIAS_NO_SE_ENTRENARÁN = 10

TOTALES_A_ENTRENAR = num_ESTADOS*num_ACCIONES
#---> 16.128 entrenamientos distintos!

TOTALES_A_ENTRENAR_REALES = TOTALES_A_ENTRENAR - num_ACCIONES_QUE_JAMAS_SE_ENTRENARAN



# print 'Espacio de ', NUM_SEC_X,'x',NUM_SEC_Y
# print 'Número de ESTADOS = ', num_ESTADOS
# print 'Número de acciones totales a entrenar = ', TOTALES_A_ENTRENAR
# print 'De las cuales no permitidas: ', num_ACCIONES_QUE_JAMAS_SE_ENTRENARAN
# print 'Además existen todos los estados en los que el disco ya ha sobrepasado al robot'
