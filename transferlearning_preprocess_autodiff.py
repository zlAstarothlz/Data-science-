# -*- coding: utf-8 -*-
"""Copia de TransferLearning_preprocess_autodiff.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X9z-aBxNNHL_RP-K8JnTCbY8y26rcn_l

<a href="https://colab.research.google.com/github/amalvarezme/AnaliticaDatos/blob/master/6_NN_DeepLearning/TransferLearning_preprocess_autodiff.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

Elaborado por Nicolás Pavón npavong@unal.edu.co y Andrés Álvarez amalvarezme@unal.edu.co .

# Transfer Learning (Transferencia de aprendizaje)

- $\textbf{Transfer Learning}$, nos permite el entramineto de redes neuronales profundas con la ventaja de usar menos datos para la tarea que queremos realizar.

- Por lo tanto estamos $\textbf{trasnfiriendo}$ el $\textbf{"Conocimiento"}$ aprendido por el modelo en anteriores tareas (utilizando bases de datos grandes) a nuestro modelo nuevo (depurado sobre bases de datos más pequeñas).

- La idea general del transfer learning consta en aprovechar los modelos y sus parámetros entrenados, tomarlos para resolver nuestras propias tareas

# Clasificación de imagenes con Redes Neuronales Convolucionales (CNN's)

- Como tarea vamos a realizar la clasificación de imagenes mediante CNN's utilizando las librerias de Tensorflow y Keras.

- Nuestro dataset [Cifar10] (https://www.cs.toronto.edu/~kriz/cifar.html) lo importaremos de Keras.datasets

- El conjunto de datos CIFAR-10 consta de 60.000 fotos divididas en 10 clases. Las clases incluyen objetos comunes como aviones, automóviles, aves, gatos, etc. en. El conjunto de datos se divide de forma estándar, donde se utilizan 50.000 imágenes para la formación de un modelo y los 10.000 restantes para evaluar su desempeño. Las imágenes están en RGB de 32 x 32 píxeles.

Tengamos a la mano funciones que nos ayuden a graficar tanto en escala RGB como en escala de grises.
"""

def plot_image(img):
    plt.imshow(img, cmap="gray", interpolation="nearest")
    plt.axis("off")

def plot_color_image(img):
    plt.imshow(img, interpolation="nearest")
    plt.axis("off")

def crop(images):
    return images[150:220, 130:250]

"""1. Importemos las librerias TensorFlow y Keras"""

## instalamos los paquetes de tensorflow y keras
#!pip install tensorflow
#!pip install Keras
# Google colab, ya cuenta con la version más reciente de Tensorflow y Keras

import tensorflow as tf
import keras
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# to make this notebook's output stable across runs
np.random.seed(42)
tf.random.set_seed(42)

"""2. El conjunto de datos $\textbf{Cifar10}$ lo importaremos de Keras.

    - El conjunto de datos CIFAR-10 consta de 60.000 fotos divididas en 10 clases. Las clases incluyen objetos comunes como aviones, automóviles, aves, gatos, etc. en. El conjunto de datos se divide de forma estándar, donde se utilizan 50.000 imágenes para la formación de un modelo y los 10.000 restantes para evaluar su desempeño. Las imágenes están en los 3 canales (rojo, verde y azul) y son cuadrados pequeños que miden 32 x 32 píxeles.

    - El dataset cifar10 ya se encuentra divido en los conjuntos de train y test
"""

X_data = keras.datasets.cifar10

(X_train_full, y_train_full),(X_test, y_test) = X_data.load_data()

X_train_full.shape

X_train_full.dtype

"""- Se puede ver que el conjunto de entrenamineto contiene 50.000 imágenes en los 3 canales, cada imagen de 32x32 píxeles

- Vamos a escalar la intesidad de los píxeles para tenerlas en un rango de 0-1, además de convertirlas en flotantes. Es de buena práctica trabajar con datos normalizados.
"""

X_valid, X_train = (X_train_full[:4000])/255.0 , (X_train_full[4000:])/255.0
X_test = X_test/255
y_valid, y_train = y_train_full[:4000], y_train_full[4000:]

print('Training data shape : ', X_train.shape, y_train.shape)
print('Testing data shape : ', X_test.shape, y_test.shape)

"""Podemos visuzalizar las imagenes dentro del conjunto usando la funcion imshow() del paquete Matplotlib"""

rows = 4
cols = 7
plt.figure(figsize=(cols * 1.5, rows * 1.5))
for row in range(rows):
    for col in range(cols):
        index = cols * row + col
        plt.subplot(rows, cols, index + 1)
        plt.imshow(X_train[index], interpolation="nearest")
        plt.axis('off')
plt.subplots_adjust(wspace=0.2, hspace=0.5)
plt.show()

"""- Al tener modelos pre-entrenados, probablemente las imágenes que vamos a
trabajar tienen un tamaño que no coincide con lo establecido para el modelo, veamos una función de **keras.layers**, por lo que cuando creemos el modelo vamos a ver cómo se podría agregar esta capa por si necesitamos ajustar el tamaño de imagen del **dataset**
"""

original_size = X_train.shape[1:]
W = 64
H = 64
new_size = (W, H)
# Creemos una función Lambda por si tenemos problemas en el tamaño de las imágenes
input_ = keras.layers.Input(shape=original_size)
output = keras.layers.Lambda(lambda image: tf.image.resize(image, new_size))(input_)
model_resize = keras.models.Model(input=input_, output=output)

img_resize = model_resize.predict(X_train[np.newaxis, 2,:,:])

img_resize.shape

plt.imshow(X_train[2,:,:])
plt.title('Imagen original de tamaño: {}'.format(X_train.shape[1:]))
plt.show()
plt.imshow(img_resize[0,:,:,:])
plt.title('Imagen con ajuste de tamaño: {}'.format(img_resize.shape[1:]))
plt.show()

"""## 3. Arquitectura CNN

## Trasnfer learning con modelo pre-entrenado para la extracción de característcias.

- Para este otro ejercicio vamos a aplicar algo del *trasnfer Learning*:
  - Vamos a usar el modelo en keras **ResNet50**

  - Para implementar *transfer learning*, vamos a remover la última capa de predicción del model ResNet(podemos ver en la figura) y la remplazamos con nuestras propias capas.

  - Los pesos del modelo pre-entrenado se utilizan para la extracción de caraterísticas.

  - Los pesos del modelo pre-entrenado quedan 'congelados' y no se actualizan durante el entrenamiento
"""

from keras.applications.resnet50 import ResNet50
from keras.applications.vgg16 import VGG16
from keras.models import Model, Sequential
from keras.layers import Dense, Flatten, Dropout #con el paquete tf.keras molesta con los shapes

model_pre_Res = ResNet50(include_top=False, weights='imagenet', input_shape=(32,32,3), classes = 10)
model_pre_VGG = VGG16(include_top=False,  weights='imagenet', input_shape=(32, 32, 3), classes = 10)

# Apaguemos unas capas del modelo
layer_Res = model_pre_Res.layers
for i in range(15,30):
  layer_Res[i].trainable = False

layer_VGG = model_pre_VGG.layers
for i in range(1,5):
  layer_VGG[i].trainable = False


#secuencial

model_Res = Sequential([
    model_pre_Res,
    Flatten(),
    Dense(units=1024, activation='relu', input_dim=[32,32,3]),
    Dense(units=512, activation='relu'),
    Dense(units=256, activation='relu'),
    Dropout(0.3),
    Dense(units=128, activation='relu'),
    Dropout(0.2),
    Dense(units=10, activation='softmax')
])

model_VGG = Sequential([
    model_pre_VGG,
    Flatten(),
    Dense(units=1024, activation='relu', input_dim=[32,32,3]),
    Dense(units=512, activation='relu'),
    Dense(units=256, activation='relu'),
    Dropout(0.3),
    Dense(units=128, activation='relu'),
    Dropout(0.2),
    Dense(units=10, activation='softmax')
])


'''
#funcional
#flat1_Res = Flatten()(model_pre_Res.layers[-1])
#flat1_VGG = Flatten()(model_pre_VGG.layers[-1])
f1 = Flatten()(model_pre_VGG.get_output_at(0))
h1 = Dense(1024, activation='relu', input_dim=[32,32,3])(f1)
h2 = Dense(512, activation='relu')(h1)
h3 = Dense(256, activation='relu')(h2)
d1 = Dropout(0.3)(h3)
h4 = Dense(128, activation='relu')(d1)
d2 = Dropout(0.2)(h4)
output = Dense(10, activation='softmax')(d2)
# define new model
model_VGG = Model(inputs=model_pre_VGG.inputs, outputs=output)
'''

"""### summarize"""

model_Res.summary()
#tf.keras.utils.plot_model(model_Res,show_shapes=True)

model_VGG.summary()
#tf.keras.utils.plot_model(model_VGG,show_shapes=True)

"""Analicemos cada línea de código del modelo:

- Hemos creado nuestor modelo usando transfer learning con ayuda del modelo pre-entrenado ResNet50, que si vemos ya tiene incluidas las capas de *flatten()*,*(Conv2D)* y las que hubieramos añadido a nuestro nuevo modelo.


- Luego está la red totalmente conectada (Fully-connected), compuesta de 4 capas densas, **3 ocultas** y **1 de salida**. Tenga en cuenta que **debemos aplanar sus entradas**, ya que una red densa espera una matriz 1D de características para cada instancia. También agregamos dos capas de *dropout*, con una tasa del $30\%$ y $20\%$

#### 4. Compilamos y ajustamos el modelo.
"""

model_Res.compile(loss="sparse_categorical_crossentropy", optimizer='sgd', metrics=["accuracy"])
model_VGG.compile(loss="sparse_categorical_crossentropy", optimizer='sgd', metrics=["accuracy"])

print(model_Res.input_shape)
X_train.shape
X_valid.shape
#y_train.shape
zz = model_pre_Res.predict(X_train[:30])
print(zz.shape)
model_pre_Res.outputs

print(model_VGG.input_shape)
X_train.shape
X_valid.shape
#y_train.shape
zz = model_pre_VGG.predict(X_train[:30])
print(zz.shape)
model_pre_VGG.outputs

# Entrenemo el modelo para ResNET50
hist_Res = model_Res.fit(X_train, y_train, epochs=25,
                 validation_data=(X_valid, y_valid), batch_size=32)

# Entrenemos el modelo para VGG16
hist_VGG = model_VGG.fit(X_train, y_train, epochs=25,
                 validation_data=(X_valid, y_valid), batch_size=32)

"""- Se eligió un pequeño número de épocas resolver esta tarea de forma rápida. Normalmente, el número de épocas sería entre dos o tres veces el valor escogido para resolver este tipo de tareas."""

score_Res = model_Res.evaluate(X_test, y_test, verbose=0)
score_VGG = model_VGG.evaluate(X_test, y_test, verbose=0)
print("Accuracy for ResNet50: %.2f%%" % (score_Res[1]*100))
print("Accuracy for VGG16: %.2f%%" % (score_VGG[1]*100))

"""5. Por último hacemos nuestra predicción, en este caso vamos a pretender que tenemos una nuevas imagenes que tomaremos del conjunto X_test"""

X_new = X_test[:10] # New images
y_pred_Res = model_Res.predict(X_new)
y_pred_VGG = model_VGG.predict(X_new)

print(y_pred_Res)

print(y_pred_VGG)

"""- Guardemos el modelo, para hacer transfer learning, por si en el futuro necesitamos hacer otro clasificador."""

model_Res.save("my_model_Res.h5py")
model_VGG.save("my_model_Res.h5py")

"""Otros formatos para guardar y cargar modelos de keras:

[save_load model keras](https://machinelearningmastery.com/save-load-keras-deep-learning-models/)

# Otras aplicaciones de transfer learning y visión con redes neuronales


[Semantic Segmentation](https://towardsdatascience.com/understanding-semantic-segmentation-with-unet-6be4f42d4b47)

# Autodiff en keras

La clave de la eficiencia en redes con deep learning es el autodiff

[Autodiff](https://en.wikipedia.org/wiki/Automatic_differentiation)
"""

#ejemplo simple de autodiff
#funcion a derivar
def f(w1,w2):
    return 3*w1**2 + 2 *w1*w2

w1, w2 = 5, 3
eps = 1e-6
(f(w1+eps,w2)-f(w1,w2))/eps #estimacion numerica de la derivada

(f(w1,w2+eps)-f(w1,w2))/eps #

"""La aproximación numérica funciona bien pero debe llamarse $f(\cdot)$ para calcular el gradiente de cada variable, intratable para muchos parámetros en deep learning.

El gradient tape de tensorflow (autodiff) facilita los cálculos del gradiente y lo hace eficiente para grandes cantidades de parámetros
"""

w1,w2 = tf.Variable(5.),tf.Variable(3.)
with tf.GradientTape() as tape: #crear contexto gradient tape para guardar cada operacion que envuelve una variable
    z=f(w1,w2) #funcion de perdida (loss) para salvar memoria colocar la menor cantidad de codigo en el tape

gradients = tape.gradient(z,[w1,w2]) # tape calcula  los gradientes del resultado z con respecto a [w1,w2]
gradients #gradient tape hace los calculos una sola vez de forma inversa sin importar la cantidad de variables

"""## Cuando se hace fit a un modelo secuencial o funcional en keras, utiliza gradient tape.

## Si se desea se pueden utilizar los gradientes de gradientTape y un paso personalizado fuera del ambiente model.fit() para problemas especializados sin necesidad de hacer el cálculo analítico de gradientes

## Para proyectos especializados ver:

[Custom training loop tf](https://www.tensorflow.org/tutorials/customization/custom_training_walkthrough)
"""

