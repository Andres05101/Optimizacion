import numpy as np
import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import string

def generar_matriz():
    global entrada_matrices, filas, columnas

    # Obtener el tamaño de la matriz
    filas = int(entry_filas.get())
    columnas = filas

    # Limpiar cualquier entrada anterior en la matriz
    for widget in frame_matriz.winfo_children():
        widget.destroy()

    # Crear matriz de entrada
    entrada_matrices = [[None]*columnas for _ in range(filas)]
    for i in range(filas):
        for j in range(columnas):
            entrada_matrices[i][j] = tk.Entry(frame_matriz, width=5)
            entrada_matrices[i][j].grid(row=i, column=j)

    # Botón para guardar los datos y generar el grafo
    btn_guardar = tk.Button(frame_matriz, text="Guardar Datos y Mostrar Grafo", command=guardar_datos)
    btn_guardar.grid(row=filas+1, columnspan=columnas)

def guardar_datos():
    # Guardar los datos ingresados en la matriz
    matriz = np.zeros((filas, columnas), dtype=int)
    for i in range(filas):
        for j in range(columnas):
            valor = entrada_matrices[i][j].get()
            if valor == "":
                valor = 0
            matriz[i][j] = int(valor)
    print("Matriz guardada:")
    print(matriz)
    
    # Crear un grafo vacío
    G = nx.Graph()

    # Generar nombres de nodos alfabéticos
    nombres_nodos = list(string.ascii_uppercase[:filas])

    # Agregar nodos al grafo con nombres alfabéticos
    for i in range(filas):
        G.add_node(nombres_nodos[i])

    # Agregar aristas al grafo según la matriz
    for i in range(filas):
        for j in range(columnas):
            if matriz[i][j] != 0:  # Si hay un valor distinto de cero, agrega una arista
                G.add_edge(nombres_nodos[i], nombres_nodos[j])

    # Dibujar el grafo en el frame derecho
    fig, ax = plt.subplots(figsize=(5, 5))
    pos = nx.spring_layout(G)  # Layout para una mejor visualización
    nx.draw(G, pos, with_labels=True, node_color='lightblue', font_weight='bold', node_size=700, ax=ax)

    # Limpiar el canvas anterior y mostrar el nuevo grafo
    for widget in frame_grafo.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_grafo)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Editor de Matrices y Grafo")

# Crear dos frames: uno para los controles de la matriz y otro para la visualización del grafo
frame_izquierdo = ttk.Frame(ventana, padding="10")
frame_izquierdo.grid(row=0, column=0, sticky="nsew")

frame_derecho = ttk.Frame(ventana, padding="10")
frame_derecho.grid(row=0, column=1, sticky="nsew")

# Expandir los frames cuando la ventana se redimensiona
ventana.grid_columnconfigure(0, weight=1)
ventana.grid_columnconfigure(1, weight=2)
ventana.grid_rowconfigure(0, weight=1)

# Frame izquierdo para los controles de la matriz
lbl_tamano = tk.Label(frame_izquierdo, text="Ingrese el tamaño de la matriz:")
lbl_tamano.grid(row=0, column=0)

entry_filas = tk.Entry(frame_izquierdo)
entry_filas.grid(row=0, column=1)

btn_crear_matriz = tk.Button(frame_izquierdo, text="Crear Matriz", command=generar_matriz)
btn_crear_matriz.grid(row=1, columnspan=2)

# Frame para la matriz
frame_matriz = ttk.Frame(frame_izquierdo, padding="10")
frame_matriz.grid(row=2, column=0, columnspan=2)

# Frame derecho para la visualización del grafo
frame_grafo = ttk.Frame(frame_derecho)
frame_grafo.pack(fill=tk.BOTH, expand=True)

ventana.mainloop()

