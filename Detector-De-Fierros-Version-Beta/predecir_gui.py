import tensorflow as tf
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.preprocessing import image
from tkinter import filedialog, Tk, Label, Button, messagebox, Frame
from PIL import Image, ImageTk

# Cargar modelo base
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

# Estilos visuales
titulo_font = ("Times New Roman", 18, "bold")
texto_font = ("Times New Roman", 12)
verde_olivo = "#556b2f"
verde_crema = "#eef5e6"

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
        img_pil = Image.open(ruta).resize((250, 250))
        img_tk = ImageTk.PhotoImage(img_pil)
        lbl_imagen.config(image=img_tk)
        lbl_imagen.image = img_tk

        nuevo_embedding = obtener_embedding(ruta)
        similitudes = cosine_similarity([nuevo_embedding], embeddings_guardados)[0]
        idx = np.argmax(similitudes)
        propietario = nombres_propietarios[idx].replace("_", " ").title()
        score = similitudes[idx]

        lbl_resultado.config(text=f" Propietario más probable:\n{propietario}\n\n🔍 Similitud: {score:.4f}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

# Crear ventana
root = Tk()
root.title("Identificador de Fierros")
root.geometry("500x520")
root.configure(bg="white")

# Encabezado
Label(root, text="Identificador de Fierros", font=titulo_font, bg="white", fg=verde_olivo).pack(pady=(15, 5))
Label(root, text="Sistema de Control", font=titulo_font, bg="white", fg=verde_olivo).pack(pady=(0, 10))

# Contenedor de contenido
frame = Frame(root, bg=verde_crema, padx=20, pady=20)
frame.pack(padx=20, pady=10, fill="both", expand=True)

# Botón
btn_seleccionar = Button(frame, text="📁 Seleccionar Imagen", bg=verde_olivo, fg="white",
                         font=("Times New Roman", 12, "bold"), command=seleccionar_y_predecir)
btn_seleccionar.pack(pady=10)

# Imagen cargada
lbl_imagen = Label(frame, bg=verde_crema)
lbl_imagen.pack(pady=10)

# Resultado
lbl_resultado = Label(frame, text="", font=texto_font, bg=verde_crema, justify="left", wraplength=400)
lbl_resultado.pack(pady=10)

# Footer
Label(root, text="versión beta IS-702 04.25", font=("Times New Roman", 9, "italic"), fg="#4f4f4f", bg="white").pack(pady=5)

root.mainloop()
