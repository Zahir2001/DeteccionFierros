import tensorflow as tf
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.preprocessing import image
from tkinter import filedialog, Tk, Label, Button, messagebox, Canvas, Frame, Scrollbar, VERTICAL, RIGHT, LEFT, Y, BOTH, CENTER, NW
from PIL import Image, ImageTk, ImageOps
import subprocess

# Cargar modelo base
modelo_base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3), include_top=False, pooling='avg', weights='imagenet')

def cargar_embeddings(path="embeddings.npz"):
    datos = np.load(path)
    return datos['embeddings'], datos['nombres']

EMBEDDING_PATH = "embeddings.npz"
embeddings_guardados, nombres_propietarios = cargar_embeddings(EMBEDDING_PATH)

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

def seleccionar_y_predecir():
    ruta = filedialog.askopenfilename(title="Selecciona una imagen", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if not ruta:
        return

    try:
        img_pil = Image.open(ruta)
        img_pil = ImageOps.exif_transpose(img_pil)
        img_pil = img_pil.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img_pil)
        lbl_imagen.config(image=img_tk)
        lbl_imagen.image = img_tk

        nuevo_embedding = obtener_embedding(ruta)
        similitudes = cosine_similarity([nuevo_embedding], embeddings_guardados)[0]
        top_indices = np.argsort(similitudes)[::-1][:3]

        resultado = f"\n🎯 Propietario más similar:\n{name_format(nombres_propietarios[top_indices[0]])} ({similitudes[top_indices[0]]:.4f})\n\n📋 Otros posibles:"
        for i in top_indices[1:]:
            resultado += f"\n• {name_format(nombres_propietarios[i])} ({similitudes[i]:.4f})"
        lbl_resultado.config(text=resultado)

        for idx, img_label, txt_label in zip(top_indices, img_labels, txt_labels):
            nombre = nombres_propietarios[idx]
            carpeta = os.path.join("dataset", nombre)
            if os.path.exists(carpeta):
                for archivo in os.listdir(carpeta):
                    if archivo.lower().endswith(('.jpg', '.png', '.jpeg')):
                        ruta_img = os.path.join(carpeta, archivo)
                        img = Image.open(ruta_img)
                        img = ImageOps.exif_transpose(img)
                        img = img.resize((100, 100))
                        img_tk = ImageTk.PhotoImage(img)
                        img_label.config(image=img_tk)
                        img_label.image = img_tk
                        txt_label.config(text=f"{name_format(nombre)} ({similitudes[idx]:.4f})")
                        break

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

def actualizar_embeddings_completo():
    try:
        subprocess.run(["python", "generar_embeddings.py"], check=True)
        global embeddings_guardados, nombres_propietarios
        embeddings_guardados, nombres_propietarios = cargar_embeddings("embeddings.npz")
        messagebox.showinfo("Actualizado", "✅ Embeddings (completo) actualizados correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar embeddings:\n{e}")

def actualizar_embeddings_incremental():
    try:
        subprocess.run(["python", "generar_embeddings_incremental.py"], check=True)
        global embeddings_guardados, nombres_propietarios
        embeddings_guardados, nombres_propietarios = cargar_embeddings("embeddings_incremental.npz")
        messagebox.showinfo("Actualizado", "✅ Embeddings (incremental) actualizados correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar embeddings:\n{e}")

root = Tk()
root.title("🧠 Identificador de Fierros - Mejorado")
root.geometry("700x700")
root.configure(bg="#f4f4f4")

canvas = Canvas(root, bg="#f4f4f4")
scroll_y = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
canvas.configure(yscrollcommand=scroll_y.set)
canvas.pack(side=LEFT, fill=BOTH, expand=True)
scroll_y.pack(side=RIGHT, fill=Y)

wrapper_frame = Frame(canvas, bg="#f4f4f4")
canvas.create_window((350, 0), window=wrapper_frame, anchor='n')  # Centramos con x=350

frame = Frame(wrapper_frame, bg="#f4f4f4")
frame.pack(anchor=CENTER)

frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

btn_seleccionar = Button(frame, text="📷 Seleccionar Imagen", font=("Arial", 11, "bold"), bg="#e0e0e0", command=seleccionar_y_predecir)
btn_seleccionar.pack(pady=12)

lbl_imagen = Label(frame, bg="#f4f4f4")
lbl_imagen.pack(pady=8)

lbl_resultado = Label(frame, text="", font=("Arial", 11), justify="center", bg="#f4f4f4")
lbl_resultado.pack(pady=8)

imagenes_frame = Frame(frame, bg="#f4f4f4")
imagenes_frame.pack(pady=10)

img_labels = []
txt_labels = []

for _ in range(3):
    col = Frame(imagenes_frame, bg="#f4f4f4")
    col.pack(side=LEFT, padx=15)
    img = Label(col, bg="#f4f4f4")
    img.pack()
    txt = Label(col, text="", font=("Arial", 10, "bold"), bg="#f4f4f4")
    txt.pack()
    img_labels.append(img)
    txt_labels.append(txt)

btn_actualizar_completo = Button(frame, text="🔄 Actualizar Embeddings (Completo)", font=("Arial", 10), bg="#d0ffd0", command=actualizar_embeddings_completo)
btn_actualizar_completo.pack(pady=10)

btn_actualizar_incremental = Button(frame, text="🔁 Actualizar Embeddings (Incremental)", font=("Arial", 10), bg="#d0e0ff", command=actualizar_embeddings_incremental)
btn_actualizar_incremental.pack(pady=5)

root.mainloop()
