import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing import image

# Usar MobileNetV2 sin capa final (para obtener embeddings)
modelo_base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    pooling='avg',
    weights='imagenet'
)

DATASET_PATH = 'dataset/'
embeddings = []
nombres = []

def obtener_embedding(ruta_imagen):
    img = image.load_img(ruta_imagen, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    embedding = modelo_base.predict(img_array, verbose=0)
    return embedding[0]

for propietario in sorted(os.listdir(DATASET_PATH)):
    carpeta_propietario = os.path.join(DATASET_PATH, propietario)
    if os.path.isdir(carpeta_propietario):
        for archivo in os.listdir(carpeta_propietario):
            if archivo.lower().endswith(('.jpg', '.png', '.jpeg')):
                ruta_imagen = os.path.join(carpeta_propietario, archivo)
                vector = obtener_embedding(ruta_imagen)
                embeddings.append(vector)
                nombres.append(propietario)

# Guardar embeddings y nombres asociados
np.savez_compressed("embeddings.npz", embeddings=np.array(embeddings), nombres=np.array(nombres))
print("✅ Embeddings generados y guardados en embeddings.npz")
