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
    lazos = []  # Para almacenar los lazos
    for i in range(filas):
        for j in range(columnas):
            if matriz[i][j] != 0:
                if i == j:
                    # Detectar lazos (conexión de un nodo consigo mismo)
                    G.add_edge(nombres_nodos[i], nombres_nodos[j], weight=matriz[i][j], dir="self")
                    lazos.append((nombres_nodos[i], nombres_nodos[j]))
                elif matriz[i][j] == matriz[j][i] and i < j:
                    G.add_edge(nombres_nodos[i], nombres_nodos[j], weight=matriz[i][j], dir="none")  # Sin flecha
                elif matriz[i][j] != matriz[j][i]:
                    G.add_edge(nombres_nodos[i], nombres_nodos[j], weight=matriz[i][j], dir="forward")  # Flecha hacia adelante
                arcos.append((nombres_nodos[i], nombres_nodos[j]))

    conjunto_vertices = "{" + ", ".join(nombres_nodos) + "}"
    conjunto_arcos = "{" + ", ".join([f"({a[0]}, {a[1]}, {G.edges[a]['weight']})" for a in arcos if G.has_edge(a[0], a[1])]) + "}"

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
    lbl_vertices.config(
    text=f"V = {formatear_texto(conjunto_vertices, ancho_max)}",
    fg="orange"  # Color para el texto de los vértices
    )
    lbl_arcos.config(
    text=f"A = {formatear_texto(conjunto_arcos, ancho_max)}",
    fg="black"  # Color para el texto de los arcos
    )
    # Colores para los nodos y aristas (usando los colores de los conceptos)
    nodo_color = "orange"
    arista_color = "black"
    peso_color = "green"

    # Dibujar el grafo
    fig, ax = plt.subplots(figsize=(5, 5))
    pos = nx.spring_layout(G, seed=42)

    # Dibujar las aristas diferenciadas
    no_arrows = [edge for edge in G.edges(data=True) if edge[2]["dir"] == "none"]
    arrows = [edge for edge in G.edges(data=True) if edge[2]["dir"] == "forward"]
    self_loops = [edge for edge in G.edges(data=True) if edge[2]["dir"] == "self"]  # Lazos

# Dibujar nodos y conexiones generales
    nx.draw(
    G, pos, with_labels=True, node_color=nodo_color, font_weight='bold',
    node_size=700, ax=ax, arrows=False
)

# Dibujar las flechas para las conexiones dirigidas
    nx.draw_networkx_edges(
    G, pos, edgelist=arrows, arrowsize=20, edge_color=arista_color
    )

# Dibujar aristas bidireccionales como líneas sólidas sin flechas
    nx.draw_networkx_edges(
    G, pos, edgelist=no_arrows, style="solid", edge_color=arista_color, arrows=False
    )

# Dibujar los self-loops (lazos) 
    nx.draw_networkx_edges(
    G, pos, edgelist=self_loops, style="solid", edge_color=arista_color,
    connectionstyle="arc3,rad=0.2", ax=ax, arrows=False
)

# Dibujar etiquetas de pesos en las aristas
    nx.draw_networkx_edge_labels(
    G, pos,
    edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)},
    ax=ax,
    label_pos=0.3,
    font_color=peso_color
    )


    for widget in frame_grafo.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_grafo)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    # Mostrar el botón de Dijkstra y el label de resultados de Dijkstra
    global lbl_resultado
    lbl_resultado = tk.Label(frame_izquierdo, text="")
    lbl_resultado.grid(row=8, column=0, columnspan=2, pady=5)

    # Crear un nuevo Frame para los botones
    frame_botones = tk.Frame(frame_izquierdo)
    frame_botones.grid(row=9, columnspan=2, pady=10)

    # Colocar los botones dentro del frame con grid()
    btn_calcular_dijkstra = tk.Button(frame_botones, text="Calcular Dijkstra", command=lambda: ejecutar_dijkstra(matriz, nombres_nodos, G))
    btn_calcular_dijkstra.grid(row=0, column=0, padx=10)  # Espaciado horizontal

    btn_calcular_bellman = tk.Button(frame_botones, text="Calcular Bellman-Ford", command=lambda: ejecutar_bellman_ford(matriz, nombres_nodos))
    btn_calcular_bellman.grid(row=0, column=1, padx=10)  # Espaciado horizontal

    # Entrada y botón para obtener nodos adyacentes
    lbl_nodo_adyacente = tk.Label(frame_izquierdo, text="Nodo para ver adyacentes:")
    lbl_nodo_adyacente.grid(row=10, column=0)

    global entry_nodo_adyacente
    entry_nodo_adyacente = tk.Entry(frame_izquierdo)
    entry_nodo_adyacente.grid(row=10, column=1)

    btn_adyacentes = tk.Button(frame_izquierdo, text="Mostrar Adyacentes", command=lambda: mostrar_adyacentes(G, nombres_nodos))
    btn_adyacentes.grid(row=11, columnspan=2, pady=10)

    global lbl_adyacentes
    lbl_adyacentes = tk.Label(frame_izquierdo, text="")
    lbl_adyacentes.grid(row=12, column=0, columnspan=2, pady=5)

    # Hacer visibles la entrada y el label de nodo de inicio y final
    lbl_nodo_inicio.grid(row=5, column=0)
    entry_nodo_inicio.grid(row=5, column=1)
    lbl_nodo_final.grid(row=6, column=0)
    entry_nodo_final.grid(row=6, column=1)

def mostrar_adyacentes(G, nombres_nodos):
    # Limpiar el contenido del label antes de actualizar
    lbl_adyacentes.config(text="")

    nodo = entry_nodo_adyacente.get().upper()
    if nodo not in nombres_nodos:
        messagebox.showerror("Error", f"El nodo '{nodo}' no existe.")
        return

    # Obtener los nodos adyacentes
    adyacentes_ida = list(G.successors(nodo))  # Nodos con aristas salientes desde el nodo
    adyacentes_vuelta = list(G.predecessors(nodo))  # Nodos con aristas entrantes hacia el nodo
    lazos = [v for u, v, d in G.edges(data=True) if u == v and u == nodo]  # Nodos con lazo consigo mismos

    # Clasificar los nodos adyacentes según dirección
    resultado = f"Nodos adyacentes a {nodo}:\n"
    adyacentes_totales = set(adyacentes_ida + adyacentes_vuelta + lazos)
    if adyacentes_totales:
        resultado += ", ".join(adyacentes_totales) + "\n\n"

        if adyacentes_ida:
            resultado += "Nodos de ida: " + ", ".join(adyacentes_ida) + "\n"
        if adyacentes_vuelta:
            resultado += "Nodos de vuelta: " + ", ".join(adyacentes_vuelta) + "\n"
        if lazos:
            resultado += "Conexiones consigo mismo: " + ", ".join(lazos) + "\n"
    else:
        resultado += "No hay nodos adyacentes.\n"

    lbl_adyacentes.config(text=resultado)

    # Cambiar el color de los nodos adyacentes
    colores_nodos = [
        'purple' if n in adyacentes_totales or n == nodo else 'orange' for n in G.nodes()
    ]

    # Redibujar el grafo con los cambios
    fig, ax = plt.subplots(figsize=(6, 4))
    pos = nx.spring_layout(G)  # Disposición del grafo
    nx.draw(
        G, pos, with_labels=True, node_color=colores_nodos, 
        node_size=500, font_weight='bold', ax=ax
    )
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)},
        ax=ax
    )

    # Actualizar el grafo mostrado en la interfaz
    for widget in frame_grafo.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_grafo)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def dijkstra_con_ruta(matriz, inicio, fin):
    n = len(matriz)
    distancias = [float('inf')] * n
    distancias[inicio] = 0
    visitados = [False] * n
    previos = [None] * n
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
                    previos[v] = u
                    heapq.heappush(cola, (nueva_dist, v))

    # Ajustar la distancia cuando se trata de un lazo (nodo a sí mismo)
    if inicio == fin and matriz[inicio][inicio] > 0:
        distancias[fin] = matriz[inicio][inicio]

    # Reconstrucción de la ruta
    ruta = []
    actual = fin
    while actual is not None:
        ruta.insert(0, actual)
        actual = previos[actual]

    return distancias, ruta

def ejecutar_dijkstra(matriz, nombres_nodos,G):
    lbl_resultado.config(text="")
    inicio_nodo = entry_nodo_inicio.get().upper()
    fin_nodo = entry_nodo_final.get().upper()

    if inicio_nodo not in nombres_nodos or fin_nodo not in nombres_nodos:
        messagebox.showerror("Error", f"Uno de los nodos '{inicio_nodo}' o '{fin_nodo}' no existe.")
        return

    inicio = nombres_nodos.index(inicio_nodo)
    fin = nombres_nodos.index(fin_nodo)

    distancias, ruta = dijkstra_con_ruta(matriz, inicio, fin)

    if distancias[fin] == float('inf'):  # Validar si no hay conexión
        lbl_resultado.config(text=f"No hay ruta desde {inicio_nodo} hasta {fin_nodo}.")
        return

    # Mostrar resultados en el label
    resultados = f"Distancias desde {inicio_nodo}:\n" + "\n".join(
        [f"{nombres_nodos[i]}: {'∞' if dist == float('inf') else dist}" for i, dist in enumerate(distancias)]
    )
    ruta_str = " -> ".join(nombres_nodos[i] for i in ruta)
    peso_total = distancias[fin]
    resultados += f"\n\nRuta más corta de {inicio_nodo} a {fin_nodo}:\n{ruta_str}\n\nPeso total de la ruta: {peso_total}"
    lbl_resultado.config(text=resultados)

    # Resaltar los nodos en la ruta más corta
    nodos_en_ruta = set(nombres_nodos[i] for i in ruta)

    colores_nodos = ['brown' if n in nodos_en_ruta else 'orange' for n in nombres_nodos]

    # Redibujar el grafo con los cambios
    fig, ax = plt.subplots(figsize=(6, 4))
    pos = nx.spring_layout(G)  # Disposición del grafo
    nx.draw(
        G, pos, with_labels=True, node_color=colores_nodos, 
        node_size=500, font_weight='bold', ax=ax
    )
    nx.draw_networkx_edges(
        G, pos, edgelist=[(nombres_nodos[u], nombres_nodos[v]) for u, v in zip(ruta[:-1], ruta[1:])],
        edge_color="brown", width=2
    )
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)},
        ax=ax
    )

    # Actualizar el grafo mostrado en la interfaz
    for widget in frame_grafo.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_grafo)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def bellman_ford(matriz, inicio):
    n = len(matriz)
    distancias = [float('inf')] * n
    distancias[inicio] = 0
    predecesores = [None] * n

    for _ in range(n - 1):  # Relajación de las aristas n-1 veces
        for u in range(n):
            for v in range(n):
                if matriz[u][v] != 0:  # Hay una conexión
                    nueva_dist = distancias[u] + matriz[u][v]
                    if nueva_dist < distancias[v]:
                        distancias[v] = nueva_dist
                        predecesores[v] = u

    # Comprobar ciclos negativos
    for u in range(n):
        for v in range(n):
            if matriz[u][v] != 0 and distancias[u] + matriz[u][v] < distancias[v]:
                raise ValueError("El grafo contiene un ciclo de peso negativo.")

    return distancias, predecesores

def ejecutar_bellman_ford(matriz, nombres_nodos):
    lbl_resultado.config(text="")
    inicio_nodo = entry_nodo_inicio.get().upper()

    if inicio_nodo not in nombres_nodos:
        messagebox.showerror("Error", f"El nodo '{inicio_nodo}' no existe.")
        return

    inicio = nombres_nodos.index(inicio_nodo)

    try:
        distancias, predecesores = bellman_ford(matriz, inicio)
    except ValueError as e:
        lbl_resultado.config(text=str(e))
        return

    resultados = f"Distancias desde {inicio_nodo}:\n" + "\n".join(
        [f"{nombres_nodos[i]}: {'∞' if dist == float('inf') else dist}" for i, dist in enumerate(distancias)]
    )
    rutas = []
    for i in range(len(predecesores)):
        if predecesores[i] is not None or i == inicio:
            ruta = []
            actual = i
            while actual is not None:
                ruta.insert(0, nombres_nodos[actual])
                actual = predecesores[actual]
            rutas.append(f"{nombres_nodos[i]}: {' -> '.join(ruta)}")

    resultados += "\n\nRutas más cortas:\n" + "\n".join(rutas)
    lbl_resultado.config(text=resultados)

ventana = tk.Tk()
ventana.title("Editor de Matrices y Grafo")

frame_izquierdo = ttk.Frame(ventana, padding="10")
frame_izquierdo.grid(row=0, column=0, sticky="nsew")

frame_derecho = ttk.Frame(ventana, padding="10")
frame_derecho.grid(row=0, column=1, sticky="nsew")

#  conceptos del grafo
frame_conceptos = ttk.Frame(frame_derecho, padding="10", relief="ridge")
frame_conceptos.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

conceptos = {
    "Grafo": "Es una estructura compuesta por nodos y aristas que los conectan.",
    "Arista": "Representa la conexión entre dos nodos, puede tener un peso asociado.",
    "Nodo": "Es un punto en el grafo que puede estar conectado con otros nodos.",
    "Nodo adyacente": "Es un nodo que está directamente conectado a otro.",
    "Peso": "Valor asociado a una arista, puede representar distancia, costo, etc.",
    "Ruta más corta": "Camino que conecta dos nodos minimizando el peso total.",
    "Subgrafo": "Es un subconjunto de nodos y aristas extraído de un grafo más grande."
}

# Colores para cada concepto
colores = [
    "red", "black", "orange", "purple" , "green", "brown", "darkcyan"
]

# Crear etiquetas para los conceptos con colores
for i, (concepto, descripcion) in enumerate(conceptos.items()):
    lbl_concepto = tk.Label(
        frame_conceptos,
        text=f"{concepto}: {descripcion}",
        wraplength=200,  # Ajustar ancho del texto
        anchor="w",
        justify="left",
        fg=colores[i % len(colores)],  # Usar colores de forma cíclica
        font=("Arial", 10, "bold")
    )
    lbl_concepto.pack(anchor="w", pady=5, fill=tk.X)


ventana.grid_columnconfigure(0, weight=1)
ventana.grid_columnconfigure(1, weight=2)
ventana.grid_rowconfigure(0, weight=1)

lbl_tamano = tk.Label(frame_izquierdo, text="Tamaño de la matriz (n):")
lbl_tamano.grid(row=0, column=0)

entry_filas = tk.Entry(frame_izquierdo)
entry_filas.grid(row=0, column=1)

btn_generar = tk.Button(frame_izquierdo, text="Generar Matriz", command=generar_matriz)
btn_generar.grid(row=1, columnspan=2, pady=10)

lbl_vertices = tk.Label(frame_izquierdo, text="")
lbl_vertices.grid(row=2, columnspan=2, pady=5)

lbl_arcos = tk.Label(frame_izquierdo, text="")
lbl_arcos.grid(row=3, columnspan=2, pady=5)

lbl_nodo_inicio = tk.Label(frame_izquierdo, text="Nodo inicial:")
lbl_nodo_inicio.grid(row=5, column=0)

entry_nodo_inicio = tk.Entry(frame_izquierdo)
entry_nodo_inicio.grid(row=5, column=1)

lbl_nodo_inicio.grid_forget()  # Ocultar al inicio
entry_nodo_inicio.grid_forget()  # Ocultar al inicio

lbl_nodo_final = tk.Label(frame_izquierdo, text="Nodo final:")
lbl_nodo_final.grid(row=6, column=0)

entry_nodo_final = tk.Entry(frame_izquierdo)
entry_nodo_final.grid(row=6, column=1)


lbl_nodo_final.grid_forget()  # Ocultar al inicio
entry_nodo_final.grid_forget()  # Ocultar al inicio

frame_matriz = ttk.Frame(frame_derecho)
frame_matriz.pack(fill=tk.BOTH, expand=True)

frame_grafo = ttk.Frame(frame_derecho)
frame_grafo.pack(fill=tk.BOTH, expand=True)

ventana.mainloop()