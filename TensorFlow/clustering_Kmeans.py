#!/usr/bin/python
# -*- coding: utf-8 -*-
# Las lineas anteriores son xa q python reconozca acentos

#Pag.54 del libro

# Se va a presentar el algoritmo de CLUSTERING llamado 'K-means',
# popular y ampliamente utilizado para agrupar automáticamente los datos en
# subconjuntos coherentes de tal manera que todos los elementos
# en un subconjunto sean más similares entre ellos que con el resto. POR ZONAS :)

# A grandes rasgos esta técnica tiene estos tres pasos:
# 0-   PASO INICIAL (paso 0): determina un conjunto inicial de K centroides.
# 1-   PASO DE ASIGNACIÓN (paso 1): asigna cada observación al grupo más cercano.
# 2-   PASO DE ACTUALIZACiÓN (paso 2): calcula los nuevos centroides basándose
#     las observaciones que han sido agrupados al grupo.


import numpy as np

# Generamos una nube de puntos aleatorios pero algo trunkados: generados
# alrededor de unas zonas en concreto para que nos sea fácil distinguir las
# dos zonas a simple vista:

num_puntos = 2000
conjunto_puntos = []
for i in xrange(num_puntos):
    #Esta sería zona A alrededor de la zona (0.0,0.9)
    if np.random.random() > 0.5:
        conjunto_puntos.append([np.random.normal(0.0, 0.9),np.random.normal(0.0, 0.9)])
    #Esta sería zona B alrededor del punto (3.0,0.5)
    else:
        conjunto_puntos.append([np.random.normal(3.0, 0.5),np.random.normal(1.0, 0.5)])


# Dibujamos los puntos con 'matplot'  también utilizaremos el paquete de
# visualización 'Seaborn' basado en matplotlib y el paquete de manipulación de
# datos 'Pandas', que permite trabajar con estructuras de datos más complejas.

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

df = pd.DataFrame({"x": [v[0] for v in conjunto_puntos],"y": [v[1] for v in conjunto_puntos]})
sns.lmplot("x", "y", data=df, fit_reg=False, size=6)
plt.show()


# Un ALGORITMO K-MEANS implementado en TensorFlow para agrupar los
# anteriores puntos en, por ejemplo, 4 clusters, puede ser el siguiente
# (basado en el propuesto por Shawn Simister en su blog
# https://gist.github.com/narphorium/d06b7ed234287e319f18 ):

# Para usar las funciones tensorFlow desde este "tf"
import tensorflow as tf

# Lo primero que tenemos que hacer es pasar todos nuestros datos a estructuras
# de datos TensorFlow, es decir, hacerlos 'tensores':
vectors = tf.constant(conjunto_puntos)

k = 4 #4 clusters o grupos

# Ahora tenemos que determinar los centroides iniciales. Se pueden elegir
# aleatoriamente K observaciones del conjunto de datos de entrada. Una forma de
# hacerlo es mezclar 'random_shuffle' aleatoriamente todos los puntos de entrada
# y quedarse con los K puntos primeros como centroides:
centroides = tf.Variable(tf.slice(tf.random_shuffle(vectors),[0,0],[k,-1]))


# Estos K puntos se guardan en un tensor 2D. Para ver como son los tensores podemos
# usar la operación 'tf.Tensor.get_shape()'
#   print vectors.get_shape()     ---> TensorShape([Dimension(2000), Dimension(2)])
#   print centroides.get_shape()  ---> TensorShape([Dimension(4), Dimension(2)])
#
# Se observa que vectors es una matriz en que la dimensión D0 contiene
# 2000 posiciones y en D1 la posición (x,y) de los puntos.

#-------------------
# Ahora viene el PASO DE ASIGNACION, consiste en calcular por cada punto su
# centroide más cercano mediante la ''Squared Euclidean Distance'':
#       distancia^2 = (Vx - Cx)^2 + (Vy - Cy)^2
# En TensorFlow es la función 'tf.sub(vectors, centroides)'.

# Pero ¡HAY PROBLEMA DE DIMENSIONES! a pesar de ser los dos vectores de 2 dimensiones,
# tienen diferentes tamanos en una de las dimensiones (2000 vs 4 en D0),
# que impide poder realizar correctamente la operación resta.
# Para solucionarlo podemos expandir ambos vectores y hacer coincidir en tamano:
expanded_vectors = tf.expand_dims(vectors, 0)
expanded_centroides = tf.expand_dims(centroides, 1)

# Hemos expandido vectors en D0 y centroides en D1 para que quede así:
#   print expanded_vectors.get_shape()     ---> TensorShape([Dimension(1), Dimension(2000), Dimension(2)])
#   print expanded_centroides.get_shape()  ---> TensorShape([Dimension(4), Dimension(1), Dimension(2)])
# El (1) significa que no tiene tamaño asignado. TensorFlow es chachi y
# su función tf.sub asume que los vectores coinciden de tamano en esos casos.

# Ahora sí podemos hacer el PASO DE ASIGNACIÓN:
#       distancia^2 = (Vx - Cx)^2 + (Vy - Cy)^2

diff=tf.sub(expanded_vectors, expanded_centroides)  #este tensor tiene 3 dimensiones
sqr= tf.square(diff)                                #este tensor tmb 3 dimensiones
#   diff.get_shape()    ---> TensorShape([Dimension(4), Dimension(2000), Dimension(2)])
#   sqr.get_shape()     ---> TensorShape([Dimension(4), Dimension(2000), Dimension(2)])

distances = tf.reduce_sum(sqr, 2) #???
#   distances.get_shape()     ---> TensorShape([Dimension(4), Dimension(2000)])


# Finalmente, la asignación se consigue con tf.argmin, que retorna el INDICE con
# el valor menor en la dimensión del tensor indicada (en nuestro caso la D0 que
# recordemos era la de los centroides).
assignments = tf.argmin(distances,0)
#   assignments.get_shape()     ---> TensorShape([Dimension(2000)])
# Este tensor contiene el indice-al-centroide-más-cercano para cada punto

#assignments = tf.argmin(tf.reduce_sum(tf.square(tf.sub(expanded_vectors,expanded_centroides)), 2), 0)

#-------------------
# PASO DE ACTUALIZACiÓN: Ahora toca calcular los nuevos centroides.
# 'Means' es el resultado de concatenar k tensores que corresponden al VALOR
# MEDIO de todos los puntos pertenecientes a cada uno de los k clusters...
means = tf.concat(0, [tf.reduce_mean(tf.gather(vectors, tf.reshape(tf.where( tf.equal(assignments, c)),[1,-1])),reduction_indices=[1]) for c in xrange(k)])

#Los nuevos centroides son estos:
update_centroides = tf.assign(centroides, means)
# operador que asigna el valor del tensor means a la variable centroids...
# (Actualiza la variable centroides con los means)


init_op = tf.initialize_all_variables()

sess = tf.Session()
sess.run(init_op)

# Ejecuto y actualizooooo sess.run()
for step in xrange(100):
    _, centroid_values, assignment_values = sess.run([update_centroides, centroides, assignments])





# Comprobamos el resultado en el tensor 'assignment_values' con este gráfico:
data = {"x": [], "y": [], "cluster": []}

for i in xrange(len(assignment_values)):
    data["x"].append(conjunto_puntos[i][0])
    data["y"].append(conjunto_puntos[i][1])
    data["cluster"].append(assignment_values[i])

df = pd.DataFrame(data)
sns.lmplot("x", "y", data=df,fit_reg=False, size=6,hue="cluster", legend=False)
plt.show()






# TENSOR = Estructura de datos básica para representar datos en TensorFlow

# Un tensor se puede como un array o lista n-dimensional q tiene como propiedades
# un tipo (type) estático de datos, que puede ser desde booleano o string
# hasta una gran variedad de tipos numéricos.

# Cada tensor tiene un rango (RANK), que es el número de dimensiones del tensor.
#           rank 0 = escalar
#           rank 1 = vector
#           rank 2 = matriz...
