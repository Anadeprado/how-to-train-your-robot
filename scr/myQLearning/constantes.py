#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las lineas anteriores son xa q python reconozca acentos


# Numero de sectores en la matriz. Normalmente 7x5
#   _________X
#   |
#   |
#  Y
num_secX = 7
num_secY = 5 # Numero de niveles

#
# % ESPACIO WEBCAM:
#     .-----.-----.-----.-----.-----.-----.-----.
# 0   |     |     |     |     |     |     |     |
#     |     |  D  |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
# 1   |  D  |     |     |     |     |     |     |
#     |     |     |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
# 2   |     |     |     |  D  |  D  |     |  R  |
#     |     |     |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
# 3   |     |     |     |     |     |     |     |
#     |     |     |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
# 4   |     |     |     |     |     |     |     |
#     |     |     |     |     |     |     |     |
#     .-----.-----.-----.-----.-----.-----.-----.
#
# NIVEL  0     1     2     3     4     5     6


# TRAYECTORIAS POSIBLES: 5 o 3 en los extremos
#    .-----.-----.-----.
#    |  1  |  2  |     |
#    |  |  |/    |     |
#    .--|--/-----.-----.
#    | D D---- 3 |     |
#    | D D\|     |     |
#    .--|--\-----.-----.
#    |  |  |\    |     |
#    |  5  | 4   |     |
#    .-----.-----.-----.

#    .-----.-----.-----.
#    |  1  |  2  |     |
#    |  |  |/    |     |
#    .--|--/-----.-----.
#    | D D---- 3 |     |
#    | D D |     |     |
#    .-----.-----.-----.


# Numero de trayectorias por nivel:
#tray_PorNivel = (3*num_secY)-2          #13 por nivel
tray_PorNivel = (5*num_secY)-4          #21 por nivel
tray_totales = tray_PorNivel* num_secX  #147 "capas"

# print 'Sectores en X: ', num_secX
# print 'Sectores en Y: ', num_secY
# print 'Posibles trayectorias de disco totales: ', tray_totales

# Posiciones posibles para el robot:
totalPos_robot = num_secX*num_secY #35
#print 'Posibles posiciones robot: ', totalPos_robot
    # Aunque también podemos limitar las posiciones del robot.
    # Podemos decirle que nunca pise nivel 0 ni 1 ni 2...

# Número de ESTADOS: 3185
num_ESTADOS = tray_totales * totalPos_robot
#print 'Numero ESTADOS = ', num_ESTADOS

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

num_ACCIONES = 9
# print 'Numero ACCIONES = ', num_ACCIONES
# print 'Numero total de entrenamientos necesarios = ', num_ACCIONES*num_ESTADOS
#---> 28.665 entrenamientos distintos!
