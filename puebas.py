import tkinter as tk

# Crear la ventana principal
root = tk.Tk()
root.title("Ventana con Scrollbar")

# Crear un frame principal donde se añadirá todo
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

# Crear un Canvas para agregar el scrollbar
canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Añadir Scrollbar al Canvas
scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configurar el canvas para usar el scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Crear un Frame dentro del canvas para contener los frames izquierdo y derecho
second_frame = tk.Frame(canvas)

# Añadir el frame secundario al canvas
canvas.create_window((0, 0), window=second_frame, anchor="nw")

# Crear el frame izquierdo y derecho
frame_izquierdo = tk.Frame(second_frame, bg="lightblue", width=200, height=500)
frame_izquierdo.grid(row=0, column=0, padx=10, pady=10)

frame_derecho = tk.Frame(second_frame, bg="lightgreen", width=200, height=500)
frame_derecho.grid(row=0, column=1, padx=10, pady=10)

# Añadir algunos widgets en los frames para probar el desplazamiento
for i in range(20):
    tk.Label(frame_izquierdo, text=f"Elemento {i+1}").pack(pady=5)
    tk.Label(frame_derecho, text=f"Item {i+1}").pack(pady=5)

# Ejecutar la aplicación
root.mainloop()
