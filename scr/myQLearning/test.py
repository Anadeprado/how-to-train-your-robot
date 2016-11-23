#!/usr/bin/python
# -*- coding: utf-8 -*-


# PARA DIBUJAR:

# # Tamaño pantalla:
# win_borde = 50
# winX = 100*num_secX + win_borde*2
# winY = 100*num_secY + win_borde*2
#
# def imagenVacia():
#     global winX, winY
#     # Creamos una imagen vacias (de ceros)
#     vacia = np.zeros((winX,winY,3), np.uint8)
#     return vacia
#
# img = imagenVacia()
# cv2.namedWindow("BoardGame")
# cv2.imshow("BoardGame",img)
# cv2.waitKey(10)



# >>> for x in range(1,11):
# ...     print '{0:2d} {1:3d} {2:4d}'.format(x, x*x, x*x*x)
# ...
#  1   1    1
#  2   4    8
#  3   9   27
#  4  16   64
#  5  25  125
#  6  36  216
#  7  49  343
#  8  64  512
#  9  81  729
# 10 100 1000


import pickle  # módulo para la lectura/escritura de datos

list_TOT = []
lista = ['Perl', 'Python', 'Ruby']  # declara lista
list_TOT.append(lista)
lista = [0, 1, 0.17]  # declara lista
list_TOT.append(lista)
lista = [0,0,0,0,0]
list_TOT.append(lista)



archivo = open('lenguajes.dat', 'wb')  # abre archivo binario para escribir
pickle.dump(list_TOT, archivo)  # escribe lista total en archivo
archivo.close  # cierra archivo
#del lista, lista_2  # borra de memoria la lista


lista_TOT_2 = []
archivo = open('lenguajes.dat', 'rb')  # abre archivo binario para leer
lista_TOT_2 = pickle.load(archivo)  # carga lista desde archivo
print 'Lista lista_TOT_2: ',lista_TOT_2  # muestra lista
print 'Elemento lista[2]: ', lista_TOT_2[2]
archivo.close  # cierra archivo
