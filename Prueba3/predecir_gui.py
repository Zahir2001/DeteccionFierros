import tensorflow as tf
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.preprocessing import image
from tkinter import filedialog, Tk, Label, Button, messagebox
from PIL import Image, ImageTk

# Cargar modelo base para extracción de embeddings
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

# Función para obtener embedding desde imagen
def obtener_embedding(ruta):
    img = image.load_img(ruta, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    embedding = modelo_base.predict(img_array, verbose=0)
    return embedding[0]

# Función para mostrar imagen y hacer predicción
def seleccionar_y_predecir():
    ruta = filedialog.askopenfilename(title="Selecciona una imagen", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if not ruta:
        return

    try:
        # Mostrar imagen seleccionada
        img_pil = Image.open(ruta).resize((200, 200))
        img_tk = ImageTk.PhotoImage(img_pil)
        lbl_imagen.config(image=img_tk)
        lbl_imagen.image = img_tk

        # Obtener embedding y comparar
        nuevo_embedding = obtener_embedding(ruta)
        similitudes = cosine_similarity([nuevo_embedding], embeddings_guardados)[0]
        idx = np.argmax(similitudes)
        propietario = nombres_propietarios[idx]
        score = similitudes[idx]

        # Mostrar resultado
        lbl_resultado.config(text=f"Propietario: {propietario}\nSimilitud: {score:.4f}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

# Crear ventana
root = Tk()
root.title("Identificador de Fierros")
root.geometry("400x450")

# Componentes GUI
btn_seleccionar = Button(root, text="Seleccionar Imagen", command=seleccionar_y_predecir)
btn_seleccionar.pack(pady=10)

lbl_imagen = Label(root)
lbl_imagen.pack(pady=10)

lbl_resultado = Label(root, text="", font=("Arial", 12), justify="center")
lbl_resultado.pack(pady=10)

# Ejecutar app
root.mainloop()
