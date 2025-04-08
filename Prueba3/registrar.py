import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector
from PIL import Image, ImageTk
import os
from database import conectar_bd
from shutil import copyfile

# Función para guardar imagen localmente
def guardar_imagen_local(nombre_propietario, ruta_origen, fierro_id):
    carpeta = os.path.join("dataset", nombre_propietario.replace(" ", "_"))
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    ruta_destino = os.path.join(carpeta, f"fierro_{fierro_id}.jpg")
    copyfile(ruta_origen, ruta_destino)
    print(f"Imagen guardada localmente en {ruta_destino}")

# Guardar en BD y local
def guardar_datos():
    nombre_prop = entry_propietario.get().strip()
    telefono = entry_telefono.get().strip()
    direccion = entry_direccion.get().strip()
    nombre_fierro = entry_fierro.get().strip()
    ruta_imagen = entry_imagen.get().strip()

    if not (nombre_prop and nombre_fierro and ruta_imagen):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    try:
        conn = conectar_bd()
        cursor = conn.cursor()

        # Insertar propietario
        cursor.execute("INSERT INTO Propietarios (nombre, telefono, direccion) VALUES (%s, %s, %s)",
                       (nombre_prop, telefono, direccion))
        propietario_id = cursor.lastrowid

        # Leer imagen
        with open(ruta_imagen, "rb") as file:
            img_bin = file.read()

        # Insertar fierro
        cursor.execute("INSERT INTO Fierros (nombre, imagen, propietario_id) VALUES (%s, %s, %s)",
                       (nombre_fierro, img_bin, propietario_id))
        fierro_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # Guardar imagen localmente
        guardar_imagen_local(nombre_prop, ruta_imagen, fierro_id)

        messagebox.showinfo("Éxito", "Datos guardados correctamente.")
        limpiar_campos()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def seleccionar_imagen():
    ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if ruta:
        entry_imagen.delete(0, tk.END)
        entry_imagen.insert(0, ruta)
        mostrar_imagen(ruta)

def mostrar_imagen(ruta):
    imagen = Image.open(ruta)
    imagen = imagen.resize((200, 200))
    imagen = ImageTk.PhotoImage(imagen)
    label_imagen.config(image=imagen)
    label_imagen.image = imagen

def limpiar_campos():
    entry_propietario.delete(0, tk.END)
    entry_telefono.delete(0, tk.END)
    entry_direccion.delete(0, tk.END)
    entry_fierro.delete(0, tk.END)
    entry_imagen.delete(0, tk.END)
    label_imagen.config(image="")

# GUI
root = tk.Tk()
root.title("Registrar Propietario y Fierro")
root.geometry("400x500")

tk.Label(root, text="Nombre del Propietario").pack()
entry_propietario = tk.Entry(root, width=40)
entry_propietario.pack()

tk.Label(root, text="Teléfono").pack()
entry_telefono = tk.Entry(root, width=40)
entry_telefono.pack()

tk.Label(root, text="Dirección").pack()
entry_direccion = tk.Entry(root, width=40)
entry_direccion.pack()

tk.Label(root, text="Nombre del Fierro").pack()
entry_fierro = tk.Entry(root, width=40)
entry_fierro.pack()

tk.Label(root, text="Seleccionar Imagen").pack()
frame_imagen = tk.Frame(root)
entry_imagen = tk.Entry(frame_imagen, width=30)
entry_imagen.pack(side=tk.LEFT)
btn_imagen = tk.Button(frame_imagen, text="Buscar", command=seleccionar_imagen)
btn_imagen.pack(side=tk.RIGHT)
frame_imagen.pack()

label_imagen = tk.Label(root)
label_imagen.pack()

btn_guardar = tk.Button(root, text="Guardar", command=guardar_datos)
btn_guardar.pack()

root.mainloop()
