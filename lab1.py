import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.spatial import ConvexHull
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable

# OBTENCION DE VALORES Y OPCIONES SELECCIONADOS POR EL USUARIO
def resolver():
    seleccion = opcion.get()
    
    # Validación y obtención de valores de la función objetivo
    try:
        x1_value = float(x1.get())
        x2_value = float(x2.get())
    except ValueError:
        messagebox.showerror("Error", "Valores inválidos en la función objetivo. Asegúrate de ingresar números.")
        return
    
    # Restricciones iniciales (x1 >= 0 y x2 >= 0)
    restricciones = [(1, 0, "≥", 0), (0, 1, "≥", 0)]
    
    for i in range(cantidad_restricciones):
        try:
            res_x1 = float(res_vars_x1[i].get())
            res_x2 = float(res_vars_x2[i].get())
            signo = opcionres[i].get()
            constante = float(res_constantes[i].get())
            restricciones.append((res_x1, res_x2, signo, constante))
        except ValueError:
            messagebox.showerror("Error", f"Valores inválidos en la restricción {i+1}. Asegúrate de ingresar números.")
            return

    # SOLUCION DE PROBLEMA DE OPTIMIZACION LINEAL
    prob = LpProblem(name="Problema", sense=LpMaximize if seleccion == "Maximizar" else LpMinimize)

    x1_var = LpVariable(name="X1", lowBound=0)
    x2_var = LpVariable(name="X2", lowBound=0)

    prob += x1_value * x1_var + x2_value * x2_var

    for res in restricciones:
        if res[2] == "≤":
            prob += res[0] * x1_var + res[1] * x2_var <= res[3]
        elif res[2] == "≥":
            prob += res[0] * x1_var + res[1] * x2_var >= res[3]
        elif res[2] == "=":
            prob += res[0] * x1_var + res[1] * x2_var == res[3]

    prob.solve()

    optimal_x1 = x1_var.value()
    optimal_x2 = x2_var.value()
    optimal_value = prob.objective.value()

    A = []
    b = []

    for res in restricciones:
        if res[2] == "≤":
            A.append([res[0], res[1]])
            b.append(res[3])
        elif res[2] == "≥":
            A.append([-res[0], -res[1]])
            b.append(-res[3])
        elif res[2] == "=":
            A.append([res[0], res[1]])
            b.append(res[3])

    A = np.array(A)
    b = np.array(b)

    vertice_sol = []

    for i in range(len(A)):
        for j in range(i + 1, len(A)):
            A_sub = np.array([A[i], A[j]])
            b_sub = np.array([b[i], b[j]])
            if np.linalg.matrix_rank(A_sub) == 2:
                try:
                    vertice = np.linalg.solve(A_sub, b_sub)
                    if all(vertice >= 0):
                        valid = True
                        for k, res in enumerate(restricciones):
                            if res[2] == "≤" and not (res[0] * vertice[0] + res[1] * vertice[1] <= res[3]):
                                valid = False
                                break
                            elif res[2] == "≥" and not (res[0] * vertice[0] + res[1] * vertice[1] >= res[3]):
                                valid = False
                                break
                            elif res[2] == "=" and not np.isclose(res[0] * vertice[0] + res[1] * vertice[1], res[3]):
                                valid = False
                                break
                        if valid:
                            vertice_sol.append(vertice)
                except np.linalg.LinAlgError:
                    continue

    vertice_values = [x1_value * v[0] + x2_value * v[1] for v in vertice_sol]

    vertices_msg = "\n".join([f"Vértice {i+1}: X1 = {v[0]:.2f}, X2 = {v[1]:.2f}, Z = {vertice_values[i]:.2f}" for i, v in enumerate(vertice_sol)])
    mensaje_opt = f"{vertices_msg}\n\nLa optimización se alcanza en:\nX1 = {optimal_x1:.2f}\nX2 = {optimal_x2:.2f}\nValor óptimo = {optimal_value:.2f}"

    # Crear un frame para la gráfica y los resultados
    frame_grafica = tk.Frame(scrollable_frame, bg='#f8d7da')
    frame_grafica.grid(row=4, column=0, columnspan=5, pady=10)

    frame_resultado = tk.Frame(scrollable_frame, bg='#f8d7da')
    frame_resultado.grid(row=4, column=5, padx=10, pady=10, sticky="n")

    # GRAFICA RESTRICCIONES DENTRO DE TKINTER
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlabel('X1')
    ax.set_ylabel('X2')
    ax.set_title('Inecuaciones y región factible de soluciones')

    x1_vals = np.linspace(0, 400, 250)
    for i, res in enumerate(restricciones[2:], start=2):
        if res[1] != 0:
            x2_vals_restr = (res[3] - res[0] * x1_vals) / res[1]
            ax.plot(x1_vals, x2_vals_restr, color=plt.cm.tab10(i), lw=2, label=f'Restricción {i-1}: {int(res[0])}X1 + {int(res[1])}X2 {res[2]} {int(res[3])}')
        else:
            x1_vals_restr = np.full_like(x1_vals, res[3] / res[0])
            ax.plot(x1_vals_restr, x1_vals, color=plt.cm.tab10(i), lw=2, label=f'Restricción {i-1}: {int(res[0])}X1 + {int(res[1])}X2 {res[2]} {int(res[3])}')

    if len(vertice_sol) > 2:
        # Calcular el convex hull de los vértices (intersecciones)
        hull = ConvexHull(np.array(vertice_sol))
        region_factible = np.array(vertice_sol)[hull.vertices]
        
        # Dibujar la región factible y rellenarla de color gris
        ax.fill(region_factible[:, 0], region_factible[:, 1], color='grey', alpha=0.4, label='Región Factible')

    ax.plot(optimal_x1, optimal_x2, 'ro', label='Solución óptima')
    ax.text(optimal_x1, optimal_x2, f'({optimal_x1:.2f}, {optimal_x2:.2f})', fontsize=8)

    # Ajuste de los límites de los ejes según el máximo de las intersecciones
    if vertice_sol:
        max_x1 = max([v[0] for v in vertice_sol])
        max_x2 = max([v[1] for v in vertice_sol])
        ax.set_xlim(0, max_x1 + 20)  # Añadimos un margen
        ax.set_ylim(0, max_x2 + 20)  # Añadimos un margen
    else:
        ax.set_xlim(0, 400)  # Limites por defecto
        ax.set_ylim(0, 400)  # Limites por defecto

    ax.grid(True)
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Mostrar el resultado en un Label dentro del frame_resultado
    resultado_label = tk.Label(frame_resultado, text=mensaje_opt, bg='#f8d7da', font=("Arial", 10), justify="left")
    resultado_label.pack()


def agregar_restricciones():
    global cantidad_restricciones
    cantidad_restricciones = int(resCan.get())
    
    if cantidad_restricciones < 2:
        messagebox.showerror("Error", "Debes agregar al menos 2 restricciones.")
        return
    
    if 'restriccion_frame' in globals():
        restriccion_frame.destroy()
    
    restriccion_frame = tk.Frame(scrollable_frame, bg='#f8d7da', pady=10)
    restriccion_frame.grid(row=2, column=0, columnspan=7, padx=10, pady=10)
    
    global res_vars_x1, res_vars_x2, res_constantes, opcionres
    res_vars_x1 = []
    res_vars_x2 = []
    res_constantes = []
    opcionres = []

    for i in range(cantidad_restricciones):
        tk.Label(restriccion_frame, text=f"Restricción {i+1}:", font=("Arial", 10, "bold"), bg='#f8d7da').grid(row=i*2, column=0, padx=10, pady=5)
        res_var_x1 = tk.Entry(restriccion_frame, width=5)
        res_var_x1.grid(row=i*2, column=1, padx=2, pady=5)
        res_vars_x1.append(res_var_x1)
        tk.Label(restriccion_frame, text="X1 + ", font=("Arial", 10), bg='#f8d7da').grid(row=i*2, column=2, padx=2, pady=5)
        res_var_x2 = tk.Entry(restriccion_frame, width=5)
        res_var_x2.grid(row=i*2, column=3, padx=2, pady=5)
        res_vars_x2.append(res_var_x2)
        tk.Label(restriccion_frame, text="X2 ", font=("Arial", 10), bg='#f8d7da').grid(row=i*2, column=4, padx=2, pady=5)
        opcionres_var = tk.StringVar(ventana)
        opcionres_var.set("≤")
        menu = tk.OptionMenu(restriccion_frame, opcionres_var, "≤", "≥", "=")
        menu.config(bg='#f8d7da')
        menu.grid(row=i*2, column=5, padx=2, pady=5)
        opcionres.append(opcionres_var)
        res_constante = tk.Entry(restriccion_frame, width=5)
        res_constante.grid(row=i*2, column=6, padx=2, pady=5)
        res_constantes.append(res_constante)


# Configurar ventana principal
ventana = tk.Tk()
ventana.geometry("950x600")
ventana.title("Resolución de Problemas de Programación Lineal")
ventana.configure(bg='#f8d7da')

# Crear un canvas y un scrollbar para la ventana principal
canvas = tk.Canvas(ventana, bg='#f8d7da')
scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg='#f8d7da')

# Colocar el canvas en la ventana principal
canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# Configurar el canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Añadir widgets a la ventana scrollable_frame
opcion = tk.StringVar(ventana)
opcion.set("Maximizar")
menu = tk.OptionMenu(scrollable_frame, opcion, "Maximizar", "Minimizar")
menu.config(bg='#f8d7da')
menu.grid(row=0, column=0, padx=5, pady=5)

x1 = tk.Entry(scrollable_frame, width=7)
x1.grid(row=0, column=1, padx=5, pady=5)
x1.insert(0, " ")
tk.Label(scrollable_frame, text="X1 +", bg='#f8d7da').grid(row=0, column=2, padx=5, pady=5)

x2 = tk.Entry(scrollable_frame, width=7)
x2.grid(row=0, column=3, padx=5, pady=5)
x2.insert(0, " ")
tk.Label(scrollable_frame, text="X2", bg='#f8d7da').grid(row=0, column=4, padx=5, pady=5)

tk.Label(scrollable_frame, text="Número de restricciones", font=("Arial", 10, "bold"), bg='#f8d7da').grid(row=1, column=0, padx=10, pady=10)
resCan = tk.Entry(scrollable_frame, width=5)
resCan.grid(row=1, column=1, padx=5, pady=5)

btn_restricciones = tk.Button(scrollable_frame, text="Agregar restricciones", command=agregar_restricciones, bg='#e1a4b1')
btn_restricciones.grid(row=1, column=2, padx=5, pady=5)

btn_resolver = tk.Button(scrollable_frame, text="Resolver", command=resolver, bg='#f5c6cb')
btn_resolver.grid(row=1, column=3, padx=5, pady=5)

# Configurar filas y columnas para que el canvas se expanda
ventana.grid_rowconfigure(0, weight=1)
ventana.grid_columnconfigure(0, weight=1)

ventana.mainloop()
