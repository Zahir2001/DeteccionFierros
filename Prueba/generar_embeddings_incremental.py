import tensorflow as tf
import numpy as np
import os
import json
from tensorflow.keras.preprocessing import image

# Ruta de embeddings y log de imágenes procesadas
EMBEDDINGS_PATH = 'embeddings_incremental.npz'
PROCESADAS_JSON = 'imagenes_procesadas.json'
DATASET_PATH = 'dataset/'

# Cargar modelo MobileNetV2 (preentrenado, sin capa final)
modelo_base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    pooling='avg',
    weights='imagenet'
)

# Cargar imágenes ya procesadas (si existen)
if os.path.exists(PROCESADAS_JSON):
    with open(PROCESADAS_JSON, 'r') as f:
        imagenes_procesadas = json.load(f)
else:
    imagenes_procesadas = {}

# Cargar embeddings existentes (si hay)
if os.path.exists(EMBEDDINGS_PATH):
    data = np.load(EMBEDDINGS_PATH)
    embeddings = list(data['embeddings'])
    nombres = list(data['nombres'])
else:
    embeddings = []
    nombres = []

nuevas = 0

# Extraer embedding desde imagen RGB
def obtener_embedding(ruta):
    img = image.load_img(ruta, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    embedding = modelo_base.predict(img_array, verbose=0)
    return embedding[0]

# Recorrer el dataset y procesar solo nuevas imágenes
for propietario in sorted(os.listdir(DATASET_PATH)):
    carpeta = os.path.join(DATASET_PATH, propietario)
    if os.path.isdir(carpeta):
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith(('.jpg', '.png', '.jpeg')):
                ruta = os.path.join(carpeta, archivo)
                if ruta in imagenes_procesadas:
                    continue
                try:
                    vector = obtener_embedding(ruta)
                    embeddings.append(vector)
                    nombres.append(propietario)
                    imagenes_procesadas[ruta] = True
                    nuevas += 1
                except Exception as e:
                    print(f"⚠️ No se pudo procesar {ruta}: {e}")

# Guardar embeddings actualizados
np.savez_compressed(EMBEDDINGS_PATH, embeddings=np.array(embeddings), nombres=np.array(nombres))

# Guardar lista de imágenes procesadas
with open(PROCESADAS_JSON, 'w') as f:
    json.dump(imagenes_procesadas, f, indent=2)

print(f"✅ Embeddings actualizados. Nuevas imágenes procesadas: {nuevas}")
