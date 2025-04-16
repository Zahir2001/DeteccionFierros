import tkinter as tk
from tkinter import filedialog, messagebox, Label, Button, Frame
from PIL import Image, ImageTk, ImageOps
import tensorflow as tf
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.preprocessing import image

# Modelo base
modelo_base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3), include_top=False, pooling='avg', weights='imagenet')

def cargar_embeddings(path="embeddings.npz"):
    datos = np.load(path)
    return datos['embeddings'], datos['nombres']

embeddings_guardados, nombres_propietarios = cargar_embeddings()

def obtener_embedding(ruta):
    img = Image.open(ruta)
    img = ImageOps.exif_transpose(img)
    img = img.resize((224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    embedding = modelo_base.predict(img_array, verbose=0)
    return embedding[0]

def name_format(nombre):
    return nombre.replace("_", " ").title()

# --- Interfaz ---
root = tk.Tk()
root.title("Identificador de Fierros - Sistema de Control")
root.geometry("600x600")
root.configure(bg="white")

verde_crema = "#eef5e6"
verde_olivo = "#556b2f"

# Estilos
font_titulo = ("Times New Roman", 18, "bold")
font_sub = ("Times New Roman", 18, "italic")
font_normal = ("Times New Roman", 12)

# Encabezado
header1 = tk.Label(root, text="\nIdentificador de Fierros", font=("Times New Roman", 20, "bold","italic"), fg="#6b8e23", bg="white", justify="center")
header2 = tk.Label(root, text="Sistema de Control Ganadero", font=("Times New Roman", 18, "bold","italic"), fg="#6b8e23", bg="white", justify="center")
header3 = tk.Label(root, text="Villa de San Antonio Comayagua", font=("Times New Roman", 15, "italic"), fg="#6b8e23", bg="white", justify="center")
header1.pack()
header2.pack()
header3.pack()

# Cuerpo principal
frm = Frame(root, bg=verde_crema, padx=40, pady=30)
frm.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)

# Imagen seleccionada
imagen_lbl = Label(frm, bg=verde_crema)
imagen_lbl.pack(pady=15)

# Resultado
resultado_lbl = Label(frm, text="", font=font_normal, bg=verde_crema, justify="left")
resultado_lbl.pack(pady=10)

# Función de predicción
def seleccionar_y_predecir():
    ruta = filedialog.askopenfilename(title="Selecciona una imagen", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if not ruta:
        return
    try:
        img_pil = Image.open(ruta)
        img_pil = ImageOps.exif_transpose(img_pil)
        img_pil = img_pil.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img_pil)
        imagen_lbl.config(image=img_tk)
        imagen_lbl.image = img_tk

        nuevo_embedding = obtener_embedding(ruta)
        similitudes = cosine_similarity([nuevo_embedding], embeddings_guardados)[0]
        top_indices = np.argsort(similitudes)[::-1][:3]

        resultado = f"\n📌 Propietario más similar:\n{name_format(nombres_propietarios[top_indices[0]])} ({similitudes[top_indices[0]]:.4f})\n\n📝 Otros posibles:"\
                    + f"\n• {name_format(nombres_propietarios[top_indices[1]])} ({similitudes[top_indices[1]]:.4f})"\
                    + f"\n• {name_format(nombres_propietarios[top_indices[2]])} ({similitudes[top_indices[2]]:.4f})"
        resultado_lbl.config(text=resultado)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

# Botón de acción
btn_predecir = Button(frm, text="📷 Seleccionar Imagen", bg=verde_olivo, fg="white", font=("Times New Roman", 12, "bold"), command=seleccionar_y_predecir)
btn_predecir.pack(pady=10)

# Footer
footer = tk.Label(root, text="versión beta IS-702 04.25", font=("Times New Roman", 9, "italic"), fg="#4f4f4f", bg="white")
footer.pack(pady=10)

root.mainloop()
