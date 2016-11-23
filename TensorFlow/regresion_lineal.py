#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las lineas anteriores son xa q python reconozca acentos

#Pag.42 del libro


# Se han generado unos puntos que siguen la relacion y = 0.1 * x + 0.3
# que seria una recta, PERO anadiendo algo de desviacion aleatoria en cada uno
# para que no formen una recta exacta sino una nube de puntitos (cercanos a esa recta)

import numpy as np

num_puntos = 1000
conjunto_puntos = []

for i in xrange(num_puntos):
    x1= np.random.normal(0.0, 0.55)
    y1= x1 * 0.1 + 0.3 + np.random.normal(0.0, 0.03)
    conjunto_puntos.append([x1, y1])

x_data = [v[0] for v in conjunto_puntos]
y_data = [v[1] for v in conjunto_puntos]


# Dibujamos la nube de puntos. Para ello usamos matplot
import matplotlib.pyplot as plt

# plt.plot(x_data, y_data, 'ro', label='Original data')
# plt.legend()
# plt.show()

# ...................................................................
# AHORA VIENE EL TENSORFLOW
# -------------------------------------------------------------------
# Se trata de generar un codigo en TensorFlow que permita encontrar
# los mejores parametros W y b, que a partir de los datos de entrada
# x_data, ajuste de la mejor manera a los datos de salida y_data, en
# nuestro caso en forma de una recta definida por y_data = W * x_data +
# b . El lector sabe que el valor W debe ser proximo al 0.1 y b proximo a
# 0.3, pero TensorFlow no lo sabe y debe darse cuenta de ello x si solo
#
# Una forma estandar de solucionar este tipo de problemas es iterar a
# traves de cada valor del conjunto de datos e ir modificando los
# parametros W y b, para obtener una respuesta cada vez mas acertada.
# Para saber si vamos mejorando en estas iteraciones, definiremos una
# FUNCION DE COSTE (tambien llamada funcion de error) que mida como
# de 'buena' (en realidad como de 'mala') es una determinada recta.
# Esta funcion recibe como parametros el par W y b, y devuelve un
# valor de error basado en como de bien la recta ajusta a los datos. En
# nuestro ejemplo podemos usar como función de coste la que se
# conoce como "mean squared error"

# Para usar las funciones tensorFlow desde este "tf"
import tensorflow as tf

# Primero creamos tres variables sentencias:
W = tf.Variable(tf.random_uniform([1], -1.0, 1.0))
b = tf.Variable(tf.zeros([1]))
y = W * x_data + b

# Con la llamada al metodo "tensorFlow.Variable" estamos definiendo una variable
# que reside en el grafo de operaciones que construye TensorFlow internamente.

# Aqui viene la FUNCION DE COSTE (funcion de error) que necesitamos:
loss = tf.reduce_mean(tf.square(y - y_data))

# Como vemos, esta expresión calcula la media de las distancias al
# cuadrado del punto de salida y_data que conocemos y el punto y
# calculado a partir del x_data de entrada.
# En este momento, el lector ya intuye que la recta que mejor se ajusta a
# nuestros datos es la que consigue un VALOR DE ERROR MENOR. Por tanto,
# si minimizamos esta función de error, encontraremos el mejor modelo
# para nuestros datos.

# VALOR DE ERROR MENOR o minimizar el error = esto es lo que hace el algoritmo
# de optimización conocido por "GRADIENT DESCENT" o DESCENSO DE GRADIENTE

# [Ver apuntes cuaderno Anita :)  Wn_1 = Wn - a*f'(Wn) ]

#En TensorFlow, programar el "descenso de gradiente" se haría así:
optimizer = tf.train.GradientDescentOptimizer(0.5)
train = optimizer.minimize(loss)

# Optimizador es referenciado en TensorFlow por "train", un algoritmo
# gradient descent con la función de coste ya definida. ¿?
# El valor 0.5 es lo que se llama "learning rate" que ya veremos...

# Importante para ejecutar cualquier TensorFlow: Creamos la SESION
# para poder llamar a "run" y ejecutar todo. A nuestra sesión le pasaremos
# el parámetro "train"

init = tf.initialize_all_variables() #Inicia las variables
sess = tf.Session()
sess.run(init)

# Ya podemos empezar con el proceso iterativo que nos permitirá
# encontrar los valores de W y b que definen el modelo de recta que
# mejor se ajusta a los puntos de entrada. En nuestro ejemplo en
# concreto, supongamos que considerando que con unas 8 iteraciones es
# suficiente:
for step in xrange(8):      # 8 iteraciones
    sess.run(train)         # Le pasamos el parametro "train"
print step, sess.run(W), sess.run(b)

# Dibujamos el resultado:
plt.plot(x_data, y_data, 'ro', label='Original data')
plt.plot(x_data, sess.run(W) * x_data + sess.run(b), label='Resultado')
plt.legend()
plt.show()


# Podemos anadir más datos a la gráfica (antes del show) como:
# plt.xlabel('x')
# plt.xlim(-2,2)
# plt.ylim(0.1,0.6)
# plt.ylabel('y')
