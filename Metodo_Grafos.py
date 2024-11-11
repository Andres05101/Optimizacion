import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import string
import heapq

def generar_matriz():
    global entrada_matrices, filas, columnas

    filas = int(entry_filas.get())
    columnas = filas

    for widget in frame_matriz.winfo_children():
        widget.destroy()

    nombres_nodos = list(string.ascii_uppercase[:filas])
    for col, letra in enumerate(nombres_nodos):
        lbl = tk.Label(frame_matriz, text=letra, font=("Arial", 10, "bold"))
        lbl.grid(row=0, column=col + 1)

    entrada_matrices = [[None] * columnas for _ in range(filas)]
    for i in range(filas):
        lbl_fila = tk.Label(frame_matriz, text=nombres_nodos[i], font=("Arial", 10, "bold"))
        lbl_fila.grid(row=i + 1, column=0)

        for j in range(columnas):
            entrada_matrices[i][j] = tk.Entry(frame_matriz, width=5)
            entrada_matrices[i][j].grid(row=i + 1, column=j + 1)

    btn_guardar = tk.Button(frame_matriz, text="Guardar Datos y Mostrar Grafo", command=guardar_datos)
    btn_guardar.grid(row=filas + 1, columnspan=columnas)

def guardar_datos():
    matriz = np.zeros((filas, columnas), dtype=int)
    for i in range(filas):
        for j in range(columnas):
            valor = entrada_matrices[i][j].get()
            if valor == "":
                valor = 0
            matriz[i][j] = int(valor)
    print("Matriz guardada:")
    print(matriz)

    G = nx.DiGraph()  # Crear un grafo dirigido
    nombres_nodos = list(string.ascii_uppercase[:filas])
    for i in range(filas):
        G.add_node(nombres_nodos[i])

    arcos = []
    for i in range(filas):
        for j in range(columnas):
            if matriz[i][j] != 0:
                G.add_edge(nombres_nodos[i], nombres_nodos[j], weight=matriz[i][j])
                arcos.append((nombres_nodos[i], nombres_nodos[j]))

    conjunto_vertices = "{" + ", ".join(nombres_nodos) + "}"
    conjunto_arcos = "{" + ", ".join([f"({a[0]}, {a[1]})" for a in arcos]) + "}"

    def formatear_texto(texto, ancho_max):
        lineas = []
        while len(texto) > ancho_max:
            corte = texto.rfind(",", 0, ancho_max) + 1
            if corte == 0:
                corte = ancho_max
            lineas.append(texto[:corte])
            texto = texto[corte:].strip()
        lineas.append(texto)
        return "\n".join(lineas)

    ancho_max = 50
    lbl_vertices.config(text=f"V = {formatear_texto(conjunto_vertices, ancho_max)}")
    lbl_arcos.config(text=f"A = {formatear_texto(conjunto_arcos, ancho_max)}")

    fig, ax = plt.subplots(figsize=(5, 5))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', font_weight='bold', 
            node_size=700, ax=ax, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)}, ax=ax)

    for widget in frame_grafo.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_grafo)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Mostrar el botón de Dijkstra y el label de resultados de Dijkstra
    global lbl_resultado
    lbl_resultado = tk.Label(frame_izquierdo, text="")
    lbl_resultado.grid(row=6, column=0, columnspan=2, pady=5)

    btn_dijkstra = tk.Button(frame_izquierdo, text="Calcular Dijkstra", command=lambda: ejecutar_dijkstra(matriz, nombres_nodos))
    btn_dijkstra.grid(row=7, columnspan=2, pady=10)

    # Entrada y botón para obtener nodos adyacentes
    lbl_nodo_adyacente = tk.Label(frame_izquierdo, text="Nodo para ver adyacentes:")
    lbl_nodo_adyacente.grid(row=8, column=0)

    global entry_nodo_adyacente
    entry_nodo_adyacente = tk.Entry(frame_izquierdo)
    entry_nodo_adyacente.grid(row=8, column=1)

    btn_adyacentes = tk.Button(frame_izquierdo, text="Mostrar Adyacentes", command=lambda: mostrar_adyacentes(G, nombres_nodos))
    btn_adyacentes.grid(row=9, columnspan=2, pady=10)

    global lbl_adyacentes
    lbl_adyacentes = tk.Label(frame_izquierdo, text="")
    lbl_adyacentes.grid(row=10, column=0, columnspan=2, pady=5)

    # Hacer visibles la entrada y el label de nodo de inicio
    lbl_nodo_inicio.grid(row=5, column=0)
    entry_nodo_inicio.grid(row=5, column=1)

def mostrar_adyacentes(G, nombres_nodos):
    # Limpiar el contenido del label antes de actualizar
    lbl_adyacentes.config(text="")

    nodo = entry_nodo_adyacente.get().upper()
    if nodo not in nombres_nodos:
        messagebox.showerror("Error", f"El nodo '{nodo}' no existe.")
        return

    # Obtener los nodos adyacentes del grafo dirigido
    adyacentes = list(G.successors(nodo))
    resultado = f"Nodos adyacentes a {nodo}: " + ", ".join(adyacentes) if adyacentes else "No hay adyacentes"
    lbl_adyacentes.config(text=resultado)

def dijkstra(matriz, inicio):
    n = len(matriz)
    distancias = [float('inf')] * n
    distancias[inicio] = 0
    visitados = [False] * n
    cola = [(0, inicio)]

    while cola:
        (dist, u) = heapq.heappop(cola)
        if visitados[u]:
            continue
        visitados[u] = True
        for v in range(n):
            if matriz[u][v] > 0 and not visitados[v]:
                nueva_dist = dist + matriz[u][v]
                if nueva_dist < distancias[v]:
                    distancias[v] = nueva_dist
                    heapq.heappush(cola, (nueva_dist, v))
    return distancias

def ejecutar_dijkstra(matriz, nombres_nodos):
    inicio_nodo = entry_nodo_inicio.get().upper()
    if inicio_nodo not in nombres_nodos:
        messagebox.showerror("Error", f"El nodo '{inicio_nodo}' no existe.")
        return

    inicio = nombres_nodos.index(inicio_nodo)
    distancias = dijkstra(matriz, inicio)
    resultados = f"Distancias desde {inicio_nodo}:\n" + "\n".join(
        [f"{nombres_nodos[i]}: {dist}" for i, dist in enumerate(distancias)]
    )
    lbl_resultado.config(text=resultados)

ventana = tk.Tk()
ventana.title("Editor de Matrices y Grafo")

frame_izquierdo = ttk.Frame(ventana, padding="10")
frame_izquierdo.grid(row=0, column=0, sticky="nsew")

frame_derecho = ttk.Frame(ventana, padding="10")
frame_derecho.grid(row=0, column=1, sticky="nsew")

ventana.grid_columnconfigure(0, weight=1)
ventana.grid_columnconfigure(1, weight=2)
ventana.grid_rowconfigure(0, weight=1)

lbl_tamano = tk.Label(frame_izquierdo, text="Ingrese el tamaño de la matriz:")
lbl_tamano.grid(row=0, column=0)

entry_filas = tk.Entry(frame_izquierdo)
entry_filas.grid(row=0, column=1)

btn_crear_matriz = tk.Button(frame_izquierdo, text="Crear Matriz", command=generar_matriz)
btn_crear_matriz.grid(row=1, columnspan=2)

frame_matriz = ttk.Frame(frame_izquierdo, padding="10")
frame_matriz.grid(row=2, column=0, columnspan=2)

lbl_vertices = tk.Label(frame_izquierdo)
lbl_vertices.grid(row=3, column=0, columnspan=2, pady=5)

lbl_arcos = tk.Label(frame_izquierdo)
lbl_arcos.grid(row=4, column=0, columnspan=2, pady=5)

# Ocultar el label y la entrada de "Nodo de inicio para Dijkstra"
lbl_nodo_inicio = tk.Label(frame_izquierdo, text="Nodo de inicio para Dijkstra:")
lbl_nodo_inicio.grid(row=5, column=0)
entry_nodo_inicio = tk.Entry(frame_izquierdo)
entry_nodo_inicio.grid(row=5, column=1)
lbl_nodo_inicio.grid_forget()  # Ocultar la línea al inicio
entry_nodo_inicio.grid_forget()  # Ocultar la entrada al inicio

frame_grafo = ttk.Frame(frame_derecho)
frame_grafo.pack(fill=tk.BOTH, expand=True)

ventana.mainloop()