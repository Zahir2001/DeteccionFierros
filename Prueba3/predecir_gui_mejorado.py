import tensorflow as tf
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.preprocessing import image
from tkinter import filedialog, Tk, Label, Button, messagebox
from PIL import Image, ImageTk
import subprocess

# Cargar modelo base para extracción de embeddings
modelo_base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    pooling='avg',
    weights='imagenet'
)

# Cargar embeddings y nombres
def cargar_embeddings():
    datos = np.load('embeddings.npz')
    return datos['embeddings'], datos['nombres']

embeddings_guardados, nombres_propietarios = cargar_embeddings()

# Función para obtener embedding desde imagen
def obtener_embedding(ruta):
    img = image.load_img(ruta, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    embedding = modelo_base.predict(img_array, verbose=0)
    return embedding[0]

# Mostrar Top 3 propietarios más similares
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

        top_indices = np.argsort(similitudes)[::-1][:3]  # Top 3

        resultado = f"Propietario más similar: {nombres_propietarios[top_indices[0]]} ({similitudes[top_indices[0]]:.4f})\n\nOtros posibles:"
        for i in top_indices[1:]:
            resultado += f"\n• {nombres_propietarios[i]} ({similitudes[i]:.4f})"

        lbl_resultado.config(text=resultado)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

# Ejecutar script de generación de embeddings
def actualizar_embeddings():
    try:
        subprocess.run(["python", "generar_embeddings.py"], check=True)
        global embeddings_guardados, nombres_propietarios
        embeddings_guardados, nombres_propietarios = cargar_embeddings()
        messagebox.showinfo("Actualizado", "Embeddings actualizados correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar embeddings:\n{e}")

# Crear ventana
root = Tk()
root.title("Identificador de Fierros - Mejorado")
root.geometry("450x550")

# Componentes GUI
btn_seleccionar = Button(root, text="Seleccionar Imagen", command=seleccionar_y_predecir)
btn_seleccionar.pack(pady=10)

lbl_imagen = Label(root)
lbl_imagen.pack(pady=10)

lbl_resultado = Label(root, text="", font=("Arial", 12), justify="left")
lbl_resultado.pack(pady=10)

btn_actualizar = Button(root, text="Actualizar Embeddings", command=actualizar_embeddings)
btn_actualizar.pack(pady=20)

# Ejecutar app
root.mainloop()
