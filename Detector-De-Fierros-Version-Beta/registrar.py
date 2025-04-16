import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from database import conectar_bd
from shutil import copyfile
import os

# Guardar imagen en dataset localmente
def guardar_imagen_local(nombre_propietario, ruta_origen, fierro_id):
    carpeta = os.path.join("dataset", nombre_propietario.replace(" ", "_"))
    os.makedirs(carpeta, exist_ok=True)
    ruta_destino = os.path.join(carpeta, f"fierro_{fierro_id}.jpg")
    copyfile(ruta_origen, ruta_destino)
    print(f"✅ Imagen guardada: {ruta_destino}")

# Guardar datos en la base de datos y local
def guardar_datos():
    nombre_prop = entry_propietario.get().strip()
    telefono = entry_telefono.get().strip()
    direccion = entry_direccion.get().strip()
    nombre_fierro = entry_fierro.get().strip()
    ruta_imagen = entry_imagen.get().strip()

    if not (nombre_prop and nombre_fierro and ruta_imagen):
        messagebox.showerror("Error", "Todos los campos marcados son obligatorios.")
        return

    try:
        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Propietarios (nombre, telefono, direccion) VALUES (%s, %s, %s)",
                       (nombre_prop, telefono, direccion))
        propietario_id = cursor.lastrowid

        with open(ruta_imagen, "rb") as file:
            img_bin = file.read()

        cursor.execute("INSERT INTO Fierros (nombre, imagen, propietario_id) VALUES (%s, %s, %s)",
                       (nombre_fierro, img_bin, propietario_id))
        fierro_id = cursor.lastrowid

        conn.commit()
        conn.close()

        guardar_imagen_local(nombre_prop, ruta_imagen, fierro_id)
        messagebox.showinfo("Éxito", "Datos guardados correctamente.")
        limpiar_campos()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Seleccionar imagen desde el explorador de archivos
def seleccionar_imagen():
    ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if ruta:
        entry_imagen.delete(0, tk.END)
        entry_imagen.insert(0, ruta)
        mostrar_imagen(ruta)

# Mostrar la imagen seleccionada
def mostrar_imagen(ruta):
    img = Image.open(ruta).resize((220, 220))
    img_tk = ImageTk.PhotoImage(img)
    label_imagen.config(image=img_tk)
    label_imagen.image = img_tk

# Limpiar campos de entrada
def limpiar_campos():
    for entry in [entry_propietario, entry_telefono, entry_direccion, entry_fierro, entry_imagen]:
        entry.delete(0, tk.END)
    label_imagen.config(image="")

# Inicializar ventana principal
root = tk.Tk()
root.title("Registro de Fierros - Sistema de Control")
root.geometry("600x600")
root.configure(bg="white")

verde_crema = "#eef5e6"

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background=verde_crema, foreground="black", font=("Times New Roman", 12))
style.configure("TEntry", font=("Times New Roman", 12))
style.configure("TButton", font=("Times New Roman", 12, "bold"), padding=6)
style.map("TButton", background=[("active", "#6b8e23")], foreground=[("active", "white")])

# Encabezado
header1 = tk.Label(root, text="\nRegistro de Fierros", font=("Times New Roman", 20, "bold","italic"), fg="#6b8e23", bg="white", justify="center")
header2 = tk.Label(root, text="Sistema de Control Ganadero", font=("Times New Roman", 18, "bold","italic"), fg="#6b8e23", bg="white", justify="center")
header3 = tk.Label(root, text="Villa de San Antonio Comayagua", font=("Times New Roman", 15, "italic"), fg="#6b8e23", bg="white", justify="center")
header1.pack()
header2.pack()
header3.pack()

frm = tk.Frame(root, bg=verde_crema, padx=40, pady=25)
frm.pack(padx=40, pady=15, fill=tk.BOTH, expand=True)

def agregar_campo_grid(frm, texto, fila):
    label = tk.Label(frm, text=texto, font=("Times New Roman", 12), bg=verde_crema, anchor="w")
    label.grid(row=fila, column=0, sticky="w", pady=8, padx=(0, 15))
    entry = tk.Entry(frm, font=("Times New Roman", 12), width=40)
    entry.grid(row=fila, column=1, sticky="ew")
    return entry

frm.grid_columnconfigure(1, weight=1)

entry_propietario = agregar_campo_grid(frm, "Nombre del Propietario:", 0)
entry_telefono = agregar_campo_grid(frm, "Teléfono:", 1)
entry_direccion = agregar_campo_grid(frm, "Dirección:", 2)
entry_fierro = agregar_campo_grid(frm, "Nombre del Fierro:", 3)

# Imagen
lbl_img = tk.Label(frm, text="Seleccionar Imagen:", font=("Times New Roman", 12), bg=verde_crema, anchor="w")
lbl_img.grid(row=4, column=0, sticky="w", pady=10, padx=(0, 15))

img_frame = tk.Frame(frm, bg=verde_crema)
img_frame.grid(row=4, column=1, sticky="ew")
img_frame.grid_columnconfigure(0, weight=1)

entry_imagen = tk.Entry(img_frame, font=("Times New Roman", 12))
entry_imagen.grid(row=0, column=0, sticky="ew", padx=(0, 10))

btn_img = tk.Button(img_frame, text="Buscar", bg="#556b2f", fg="white", font=("Times New Roman", 12, "bold"), command=seleccionar_imagen)
btn_img.grid(row=0, column=1)

label_imagen = tk.Label(frm, bg=verde_crema)
label_imagen.grid(row=5, column=0, columnspan=2, pady=15)

btn_guardar = tk.Button(frm, text="Guardar Datos", bg="#556b2f", fg="white", font=("Times New Roman", 12, "bold"), command=guardar_datos)
btn_guardar.grid(row=6, column=0, columnspan=2, pady=20)

# Footer
footer = tk.Label(root, text="versión beta IS-702 04.25", font=("Times New Roman", 9, "italic"), fg="#4f4f4f", bg="white")
footer.pack(pady=10)

root.mainloop()