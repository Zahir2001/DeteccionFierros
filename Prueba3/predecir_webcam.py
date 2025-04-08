import cv2
import tensorflow as tf
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.preprocessing import image
from datetime import datetime
import os
from tkinter import messagebox, Tk

# Cargar modelo base MobileNetV2 para extraer embeddings
modelo_base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    pooling='avg',
    weights='imagenet'
)

# Cargar embeddings y nombres
datos = np.load('embeddings.npz')
embeddings_guardados = datos['embeddings']
nombres_propietarios = datos['nombres']

# Funciona igual que antes
def obtener_embedding(ruta):
    img = image.load_img(ruta, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    embedding = modelo_base.predict(img_array, verbose=0)
    return embedding[0]

# Captura desde webcam
cap = cv2.VideoCapture(0)
print("Presiona 'Espacio' para capturar imagen o 'Esc' para salir")

root = Tk()
root.withdraw()  # Ocultar ventana principal Tkinter

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('Captura de Fierro - Presiona Espacio para identificar', frame)
    key = cv2.waitKey(1)

    if key == 27:  # ESC para salir
        break
    elif key == 32:  # Espacio para capturar
        # Guardar imagen temporal
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_imagen = f"captura_{timestamp}.jpg"
        cv2.imwrite(ruta_imagen, frame)
        print(f"📸 Imagen capturada: {ruta_imagen}")

        # Procesar e identificar
        try:
            nuevo_embedding = obtener_embedding(ruta_imagen)
            similitudes = cosine_similarity([nuevo_embedding], embeddings_guardados)[0]
            top3_indices = np.argsort(similitudes)[::-1][:3]

            resultado = f"Más similar: {nombres_propietarios[top3_indices[0]]} ({similitudes[top3_indices[0]]:.4f})\n\nOtros posibles:"\
                        f"\n- {nombres_propietarios[top3_indices[1]]} ({similitudes[top3_indices[1]]:.4f})"\
                        f"\n- {nombres_propietarios[top3_indices[2]]} ({similitudes[top3_indices[2]]:.4f})"

            messagebox.showinfo("Resultado de Identificación", resultado)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo identificar el fierro:\n{e}")

        os.remove(ruta_imagen)

cap.release()
cv2.destroyAllWindows()
