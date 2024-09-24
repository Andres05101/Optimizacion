import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.spatial import ConvexHull
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable
import tabulate
from scipy.optimize import linprog
from fractions import Fraction

vars_objetivo = []
restricciones = []
restricciones_constantes = []
metodo_seleccionado = None
tipo_seleccionado = None

def confirmar_variables():
    global num_variables, cantidad_restricciones
    try:
        num_variables = int(numVar.get())
        cantidad_restricciones = int(resCan.get())
        
        # Validaciones del número de variables según el método seleccionado
        if num_variables < 2:
            messagebox.showerror("Error", "El número de variables no puede ser menor a 2.")
            return
        
        if tipo_seleccionado.get() == "Método Gráfico" and num_variables != 2:
            messagebox.showerror("Error", "El método gráfico solo permite exactamente 2 variables.")
            return
        elif tipo_seleccionado.get() == "Método Simplex" and num_variables < 2:
            messagebox.showerror("Error", "El método simplex requiere al menos 2 variables.")
            return

        # Limpiar el frame de entradas
        for widget in frame_izquierdo.winfo_children():
            widget.destroy()

        # Mostrar campos para la función objetivo
        tk.Label(frame_izquierdo, bg='#f8d7da', text="Función Objetivo (Z):").grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(frame_izquierdo, bg='#f8d7da', text="Z =").grid(row=1, column=0, padx=10, pady=10)
        for i in range(num_variables):
            entry = tk.Entry(frame_izquierdo, width=5)
            entry.grid(row=1, column=i * 2 + 1, padx=5, pady=5)
            vars_objetivo.append(entry)
            if i != num_variables - 1:
                tk.Label(frame_izquierdo, bg='#f8d7da', text=f"X{i + 1} +").grid(row=1, column=i * 2 + 2, padx=5, pady=5)
            else:
                tk.Label(frame_izquierdo, bg='#f8d7da', text=f"X{i + 1}").grid(row=1, column=i * 2 + 2, padx=5, pady=5)

        # Inicializar la lista de restricciones
        for i in range(cantidad_restricciones):
            restricciones.append([])

        # Mostrar campos para las restricciones
        tk.Label(frame_izquierdo, bg='#f8d7da', text="Restricciones:").grid(row=2, column=0, padx=10, pady=10, columnspan=2)
        for i in range(cantidad_restricciones):
            tk.Label(frame_izquierdo, bg='#f8d7da', text=f"Restricción {i + 1}:").grid(row=i + 3, column=0, padx=10, pady=5)
            for j in range(num_variables):
                entry = tk.Entry(frame_izquierdo, width=5)
                entry.grid(row=i + 3, column=j * 2 + 1, padx=5, pady=5)
                restricciones[i].append(entry)
                if j != num_variables - 1:
                    tk.Label(frame_izquierdo, bg='#f8d7da', text=f"X{j + 1} +").grid(row=i + 3, column=j * 2 + 2, padx=5, pady=5)
                else:
                    tk.Label(frame_izquierdo, bg='#f8d7da', text=f"X{j + 1}").grid(row=i + 3, column=j * 2 + 2, padx=5, pady=5)
            tk.Label(frame_izquierdo, bg='#f8d7da', text="≤").grid(row=i + 3, column=num_variables * 2 + 1, padx=5, pady=5)
            constante_entry = tk.Entry(frame_izquierdo, width=5)
            constante_entry.grid(row=i + 3, column=num_variables * 2 + 2, padx=5, pady=5)
            restricciones_constantes.append(constante_entry)

        # Mostrar botón para resolver
        tk.Button(frame_izquierdo, bg='#f8d7da', text="Resolver", command=Metodo_Simplex).grid(row=cantidad_restricciones + 3, column=0, pady=10, columnspan=2)
    
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese un número válido de variables y restricciones.")

def actualizar_seleccion(value):
    global metodo_seleccionado
    metodo_seleccionado = value
    print(f"Método seleccionado: {metodo_seleccionado}")

class Metodo_Grafico:
    def __init__(self, funcion_objetivo, restricciones, scrollable_frame):  # Añadir scrollable_frame como parámetro
        self.funcion_objetivo = funcion_objetivo
        self.restricciones = restricciones
        self.scrollable_frame = scrollable_frame

    def graficar_restricciones(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')

        x1_vals = np.linspace(0, 10, 400)

        for i, restriccion in enumerate(self.restricciones):
            coef_x1, coef_x2, signo, constante = restriccion
            if coef_x2 != 0:
                x2_vals_restr = (constante - coef_x1 * x1_vals) / coef_x2
                ax.plot(x1_vals, x2_vals_restr, label=f'Restricción {i+1}: {coef_x1}X1 + {coef_x2}X2 {signo} {constante}')
            else:
                x1_vals_restr = np.full_like(x1_vals, constante / coef_x1)
                ax.plot(x1_vals_restr, x1_vals, label=f'Restricción {i+1}: {coef_x1}X1 {signo} {constante}')

        ax.legend()
        ax.grid(True)

        # Crear el frame para la gráfica y los resultados
        frame_grafica = tk.Frame(self.scrollable_frame, bg='#f8d7da')
        frame_grafica.grid(row=4, column=0, columnspan=5, pady=10)

        frame_resultado = tk.Frame(self.scrollable_frame, bg='#f8d7da')
        frame_resultado.grid(row=4, column=5, padx=10, pady=10, sticky="n")

        canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def resolver(self, seleccion, x1_value, x2_value):
        prob = LpProblem(name="Problema", sense=LpMaximize if seleccion == "Maximizar" else LpMinimize)

        x1_var = LpVariable(name="X1", lowBound=0)
        x2_var = LpVariable(name="X2", lowBound=0)

        prob += x1_value * x1_var + x2_value * x2_var

        for res in self.restricciones:
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

        # Preparar datos para la gráfica
        A = []
        b = []

        for res in self.restricciones:
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

        # Encontrar los vértices de la región factible
        for i in range(len(A)):
            for j in range(i + 1, len(A)):
                A_sub = np.array([A[i], A[j]])
                b_sub = np.array([b[i], b[j]])
                if np.linalg.matrix_rank(A_sub) == 2:
                    try:
                        vertice = np.linalg.solve(A_sub, b_sub)
                        if all(vertice >= 0):
                            valid = True
                            for k, res in enumerate(self.restricciones):
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

        # Preparar el mensaje de resultados
        vertices_msg = "\n".join([f"Vértice {i+1}: X1 = {v[0]:.2f}, X2 = {v[1]:.2f}, Z = {vertice_values[i]:.2f}" for i, v in enumerate(vertice_sol)])
        mensaje_opt = f"{vertices_msg}\n\nLa optimización se alcanza en:\nX1 = {optimal_x1:.2f}\nX2 = {optimal_x2:.2f}\nValor óptimo = {optimal_value:.2f}"

        # Crear un frame para la gráfica y los resultados
        frame_grafica = tk.Frame(scrollable_frame, bg='#f8d7da')
        frame_grafica.grid(row=4, column=0, columnspan=5, pady=10)

        frame_resultado = tk.Frame(scrollable_frame, bg='#f8d7da')
        frame_resultado.grid(row=4, column=5, padx=10, pady=10, sticky="n")

        # Crear la gráfica de restricciones
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')

        x1_vals = np.linspace(0, 400, 250)
        for i, res in enumerate(self.restricciones[2:], start=2):
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

        # Marcar la solución óptima en la gráfica
        ax.plot(optimal_x1, optimal_x2, 'ro', label='Solución óptima')
        ax.text(optimal_x1, optimal_x2, f'({optimal_x1:.2f}, {optimal_x2:.2f})', fontsize=8)

        # Ajustar límites de los ejes
        if vertice_sol:
            max_x1 = max([v[0] for v in vertice_sol])
            max_x2 = max([v[1] for v in vertice_sol])
            ax.set_xlim(0, max_x1 + 20)  # Añadir un margen
            ax.set_ylim(0, max_x2 + 20)  # Añadir un margen
        else:
            ax.set_xlim(0, 400)  # Límites por defecto
            ax.set_ylim(0, 400)  # Límites por defecto

        ax.grid(True)
        ax.legend()

        # Mostrar la gráfica en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Mostrar el resultado en un Label dentro del frame_resultado
        resultado_label = tk.Label(frame_resultado, text=mensaje_opt, bg='#f8d7da', font=("Arial", 10), justify="left")
        resultado_label.pack()

        # Crear la gráfica de restricciones
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')

class Metodo_Simplex:
    def __init__(self, frame_derecho, vars_objetivo, num_variables, cantidad_restricciones):
        self.frame_derecho = frame_derecho
        self.vars_objetivo = vars_objetivo
        self.num_variables = num_variables
        self.cantidad_restricciones = cantidad_restricciones

    def convertir_a_numero(self, valor):
        try:
            return float(valor)
        except ValueError:
            return 0.0

    def obtener_restricciones(self):
        # Aquí deberías obtener las restricciones de tu interfaz gráfica
        A = []  # Matriz de restricciones
        b = []  # Lado derecho de las restricciones
        # Lógica para obtener A y b desde la interfaz gráfica
        return A, b

    def resolver_simplex(self):
        # Limpiar el frame derecho
        for widget in self.frame_derecho.winfo_children():
            widget.destroy()

        # Obtener los coeficientes de la función objetivo
        c = [self.convertir_a_numero(var.get()) for var in self.vars_objetivo]

        # Obtener las restricciones
        A, b = self.obtener_restricciones()

        # Crear la tabla inicial del Simplex
        table = self.crear_tabla_simplex(c, A, b)
        pasos = [table.copy()]

        # Ejecutar el algoritmo Simplex
        optimal, pasos = self.simplex_algorithm(table, pasos)

        if optimal:
            for i, paso in enumerate(pasos):
                self.mostrar_tabla(paso, i + 1)
            self.mostrar_solucion(pasos[-1])
        else:
            messagebox.showinfo("Optimización", "No se encontró una solución óptima.")

    def mostrar_solucion(self, table):
        solucion = [table[i, -1] for i in range(1, len(table))]
        valor_optimo = table[0, -1]  # Valor óptimo de Z

        mensaje = f"Valor óptimo de Z: {valor_optimo}\n\nSolución óptima alcanzada:\n"
        for i in range(len(solucion)):
            mensaje += f"X{i + 1} = {solucion[i]}\n"

        num_filas_ocupadas = self.frame_derecho.grid_size()[1]  # Filas usadas en grid
        label_solucion = tk.Label(self.frame_derecho, text=mensaje, justify="left", font=("Helvetica", 10))
        label_solucion.grid(row=num_filas_ocupadas + 1, column=0, columnspan=10, padx=10, pady=10)

    def mostrar_tabla(self, table, paso_numero):
        row_start = (paso_numero - 1) * (len(table) + 4)  # Offset vertical

        tk.Label(self.frame_derecho, bg='#f8d7da', text=f"{paso_numero}er tablero Simplex", font=("Helvetica", 12, "bold")).grid(row=row_start, column=0, columnspan=len(table[0]) + 1, pady=10)

        headers = [""] + [f"X{i + 1}" for i in range(self.num_variables)] + [f"S{i + 1}" for i in range(self.cantidad_restricciones)] + ["CR"]
        for j, label in enumerate(headers):
            tk.Label(self.frame_derecho, text=label, borderwidth=1, relief="solid", width=10).grid(row=row_start + 1, column=j)

        col_pivote = np.argmin(table[0, :-1])
        ratios = np.where(table[1:, col_pivote] > 0, table[1:, -1] / table[1:, col_pivote], np.inf)
        row_pivote = np.argmin(ratios) + 1

        for i in range(len(table)):
            label = "Z" if i == 0 else f"S{i}"
            row_label = tk.Label(self.frame_derecho, text=label, borderwidth=1, relief="solid", width=10, bg="lightgreen" if i == row_pivote else "")
            row_label.grid(row=row_start + i + 2, column=0)

            for j in range(len(table[i])):
                valor = round(table[i, j], 3) if isinstance(table[i, j], float) else table[i, j]
                bg_color = "lightpink" if j == col_pivote and i == row_pivote else "lightblue" if j == col_pivote else "lightgreen" if i == row_pivote else ""
                cell_label = tk.Label(self.frame_derecho, text=valor, borderwidth=1, relief="solid", width=10, bg=bg_color)
                cell_label.grid(row=row_start + i + 2, column=j + 1)

        variable_entrada = f"X{col_pivote + 1}" if col_pivote < self.num_variables else f"S{col_pivote - self.num_variables + 1}"
        variable_salida = f"S{row_pivote}"

        tk.Label(self.frame_derecho, bg='#f8d7da', text=f"Variable de entrada: {variable_entrada}", font=("Helvetica", 10)).grid(row=row_start + len(table) + 2, column=0, columnspan=len(table[0]) + 1, pady=5)
        tk.Label(self.frame_derecho, bg='#f8d7da', text=f"Variable de salida: {variable_salida}", font=("Helvetica", 10)).grid(row=row_start + len(table) + 3, column=0, columnspan=len(table[0]) + 1, pady=5)

    def crear_tabla_simplex(self, c, A, b):
        num_restricciones = len(A)
        num_variables = len(c)
        num_variables_total = num_variables + num_restricciones

        table = np.zeros((num_restricciones + 1, num_variables_total + 1))
        table[0, :num_variables] = -np.array(c)
        for i in range(num_restricciones):
            table[i + 1, :num_variables] = A[i]
            table[i + 1, num_variables + i] = 1
            table[i + 1, -1] = b[i]

        return table

    def simplex_algorithm(self, table, pasos):
        while True:
            col_pivote = np.argmin(table[0, :-1])
            if table[0, col_pivote] >= 0:
                return True, pasos

            ratios = table[1:, -1] / table[1:, col_pivote]
            row_pivote = np.argmin(np.where(ratios <= 0, np.inf, ratios)) + 1

            if ratios[row_pivote - 1] <= 0:
                messagebox.showinfo("Optimización", "El problema es no acotado.")
                return False, pasos

            table[row_pivote] /= table[row_pivote, col_pivote]
            for i in range(len(table)):
                if i != row_pivote:
                    table[i] -= table[i, col_pivote] * table[row_pivote]

            pasos.append(table.copy())
            

ventana = tk.Tk()
ventana.geometry("950x600")
ventana.title("Resolución de Problemas de Programación Lineal")
ventana.configure(bg='#f8d7da')


# Crear frames para organizar la interfaz
frame_izquierdo = tk.Frame(ventana)
frame_izquierdo.pack(side=tk.LEFT, padx=10, pady=10)
frame_izquierdo.config(bg='#f8d7da')
frame_derecho = tk.Frame(ventana)
frame_derecho.config(bg='#f8d7da')
frame_derecho.pack(side=tk.RIGHT, padx=10, pady=10)

# Crear un canvas y un scrollbar para la ventana principal
canvas = tk.Canvas(ventana, bg='#f8d7da')
scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg='#f8d7da')

# Colocar el canvas y el scrollbar en la ventana principal
# canvas.grid(row=0, column=0, sticky="nsew")
# scrollbar.grid(row=0, column=1, sticky="ns")

# Configurar el canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Configurar el peso de las columnas y filas para el canvas y el scrollbar
ventana.grid_rowconfigure(0, weight=1)
ventana.grid_columnconfigure(0, weight=1)


# # Opciones para el menú desplegable de maximización o minimización
# opciones = ["Maximizar", "Minimizar"]
# metodo_seleccionado = tk.StringVar()
# metodo_seleccionado.set(opciones[0]) 

# # Crear menú desplegable
# tk.Label(frame_izquierdo, bg='#f8d7da', text="Seleccione Maximización o Minimización:").grid(row=0, column=2, padx=10, pady=10, columnspan=2)
# menu_desplegable = tk.OptionMenu(frame_izquierdo, metodo_seleccionado, *opciones, command=actualizar_seleccion)
# menu_desplegable.grid(row=1, column=3, padx=10, pady=10, columnspan=2)

# # Entradas para la función objetivo
# z_label = tk.Label(scrollable_frame, text="Función Z: ", bg='#f8d7da')
# z_label.grid(row=0, column=2, padx=5, pady=5)

# x1 = tk.Entry(scrollable_frame, width=7)
# x1.grid(row=0, column=3, padx=5, pady=5)
# tk.Label(scrollable_frame, text="X1 +", bg='#f8d7da').grid(row=0, column=4, padx=5, pady=5)

# x2 = tk.Entry(scrollable_frame, width=7)
# x2.grid(row=0, column=5, padx=5, pady=5)
# tk.Label(scrollable_frame, text="X2", bg='#f8d7da').grid(row=0, column=6, padx=5, pady=5)

# # Campo para el número de restricciones
# tk.Label(scrollable_frame, text="Número de restricciones", font=("Arial", 10, "bold"), bg='#f8d7da').grid(row=1, column=0, padx=10, pady=10)
# resCan = tk.Entry(scrollable_frame, width=5)
# resCan.grid(row=1, column=1, padx=5, pady=5)

# # Botones para agregar restricciones y resolver
# btn_restricciones = tk.Button(scrollable_frame, text="Agregar restricciones", command=agregar_restricciones, bg='#e1a4b1')
# btn_restricciones.grid(row=1, column=2, padx=5, pady=5)

# btn_resolver = tk.Button(scrollable_frame, text="Resolver", command=resolver, bg='#f5c6cb')
# btn_resolver.grid(row=1, column=3, padx=5, pady=5)

# restriccion_frame = tk.Frame(scrollable_frame, bg='#f8d7da')
# restriccion_frame.grid(row=2, column=2, padx=5, pady=5)

# Entradas iniciales para número de variables y restricciones
# tk.Label(frame_izquierdo, text="Número de Variables:", bg='#f8d7da').grid(row=0, column=0, padx=10, pady=10)
# numVar = tk.Entry(frame_izquierdo, width=5)
# numVar.grid(row=0, column=1, padx=5, pady=5)

# tk.Label(frame_izquierdo, text="Cantidad de Restricciones:", bg='#f8d7da').grid(row=1, column=0, padx=10, pady=10)
# resCan = tk.Entry(frame_izquierdo, width=5)
# resCan.grid(row=1, column=1, padx=5, pady=5)

# tk.Button(frame_izquierdo, text="Confirmar", command=confirmar_variables, bg='#f5c6cb').grid(row=2, column=0, columnspan=2, pady=10)



# Menú desplegable para Maximización o Minimización
opciones = ["Maximizar", "Minimizar"]
metodo_seleccionado = tk.StringVar()
metodo_seleccionado.set(opciones[0])  # Valor por defecto
tk.Label(frame_izquierdo, bg='#f8d7da', text="Seleccione Maximización o Minimización:").grid(row=0, column=0, padx=10, pady=10, columnspan=2)
menu_desplegable = tk.OptionMenu(frame_izquierdo, metodo_seleccionado, *opciones, command=actualizar_seleccion)
menu_desplegable.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

# Menú desplegable para Método Gráfico o Simplex
metodos = ["Método Gráfico", "Método Simplex"]
tipo_seleccionado = tk.StringVar()
tipo_seleccionado.set(metodos[0])  # Valor por defecto
tk.Label(frame_izquierdo, bg='#f8d7da', text="Seleccione el Método:").grid(row=2, column=0, padx=10, pady=10, columnspan=2)
menu_metodo = tk.OptionMenu(frame_izquierdo, tipo_seleccionado, *metodos)
menu_metodo.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

# Campos para ingresar el número de variables y restricciones
tk.Label(frame_izquierdo, bg='#f8d7da', text="Número de Variables:").grid(row=4, column=0, padx=10, pady=10)
numVar = tk.Entry(frame_izquierdo)
numVar.grid(row=4, column=1, padx=10, pady=10)

tk.Label(frame_izquierdo, bg='#f8d7da', text="Cantidad de Restricciones:").grid(row=5, column=0, padx=10, pady=10)
resCan = tk.Entry(frame_izquierdo)
resCan.grid(row=5, column=1, padx=10, pady=10)

# Botón para confirmar variables
tk.Button(frame_izquierdo, bg='#f8d7da', text="Confirmar", command=confirmar_variables).grid(row=6, column=0, columnspan=2, pady=10)

# Iniciar el loop principal de la ventana
ventana.mainloop()







class Metodo_Grafico:
    def __init__(self, funcion_objetivo, restricciones, scrollable_frame):  # Añadir scrollable_frame como parámetro
        self.funcion_objetivo = funcion_objetivo
        self.restricciones = restricciones
        self.scrollable_frame = scrollable_frame

    def graficar_restricciones(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')

        x1_vals = np.linspace(0, 10, 400)

        for i, restriccion in enumerate(self.restricciones):
            coef_x1, coef_x2, signo, constante = restriccion
            if coef_x2 != 0:
                x2_vals_restr = (constante - coef_x1 * x1_vals) / coef_x2
                ax.plot(x1_vals, x2_vals_restr, label=f'Restricción {i+1}: {coef_x1}X1 + {coef_x2}X2 {signo} {constante}')
            else:
                x1_vals_restr = np.full_like(x1_vals, constante / coef_x1)
                ax.plot(x1_vals_restr, x1_vals, label=f'Restricción {i+1}: {coef_x1}X1 {signo} {constante}')

        ax.legend()
        ax.grid(True)

        # Crear el frame para la gráfica y los resultados
        frame_grafica = tk.Frame(self.scrollable_frame, bg='#f8d7da')
        frame_grafica.grid(row=4, column=0, columnspan=5, pady=10)

        frame_resultado = tk.Frame(self.scrollable_frame, bg='#f8d7da')
        frame_resultado.grid(row=4, column=5, padx=10, pady=10, sticky="n")

        canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def resolver(self, seleccion, x1_value, x2_value):
        prob = LpProblem(name="Problema", sense=LpMaximize if seleccion == "Maximizar" else LpMinimize)

        x1_var = LpVariable(name="X1", lowBound=0)
        x2_var = LpVariable(name="X2", lowBound=0)

        prob += x1_value * x1_var + x2_value * x2_var

        for res in self.restricciones:
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

        # Preparar datos para la gráfica
        A = []
        b = []

        for res in self.restricciones:
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

        # Encontrar los vértices de la región factible
        for i in range(len(A)):
            for j in range(i + 1, len(A)):
                A_sub = np.array([A[i], A[j]])
                b_sub = np.array([b[i], b[j]])
                if np.linalg.matrix_rank(A_sub) == 2:
                    try:
                        vertice = np.linalg.solve(A_sub, b_sub)
                        if all(vertice >= 0):
                            valid = True
                            for k, res in enumerate(self.restricciones):
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

        # Preparar el mensaje de resultados
        vertices_msg = "\n".join([f"Vértice {i+1}: X1 = {v[0]:.2f}, X2 = {v[1]:.2f}, Z = {vertice_values[i]:.2f}" for i, v in enumerate(vertice_sol)])
        mensaje_opt = f"{vertices_msg}\n\nLa optimización se alcanza en:\nX1 = {optimal_x1:.2f}\nX2 = {optimal_x2:.2f}\nValor óptimo = {optimal_value:.2f}"

        # Crear un frame para la gráfica y los resultados
        frame_grafica = tk.Frame(scrollable_frame, bg='#f8d7da')
        frame_grafica.grid(row=4, column=0, columnspan=5, pady=10)

        frame_resultado = tk.Frame(scrollable_frame, bg='#f8d7da')
        frame_resultado.grid(row=4, column=5, padx=10, pady=10, sticky="n")

        # Crear la gráfica de restricciones
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')

        x1_vals = np.linspace(0, 400, 250)
        for i, res in enumerate(self.restricciones[2:], start=2):
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

        # Marcar la solución óptima en la gráfica
        ax.plot(optimal_x1, optimal_x2, 'ro', label='Solución óptima')
        ax.text(optimal_x1, optimal_x2, f'({optimal_x1:.2f}, {optimal_x2:.2f})', fontsize=8)

        # Ajustar límites de los ejes
        if vertice_sol:
            max_x1 = max([v[0] for v in vertice_sol])
            max_x2 = max([v[1] for v in vertice_sol])
            ax.set_xlim(0, max_x1 + 20)  # Añadir un margen
            ax.set_ylim(0, max_x2 + 20)  # Añadir un margen
        else:
            ax.set_xlim(0, 400)  # Límites por defecto
            ax.set_ylim(0, 400)  # Límites por defecto

        ax.grid(True)
        ax.legend()

        # Mostrar la gráfica en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Mostrar el resultado en un Label dentro del frame_resultado
        resultado_label = tk.Label(frame_resultado, text=mensaje_opt, bg='#f8d7da', font=("Arial", 10), justify="left")
        resultado_label.pack()

        # Crear la gráfica de restricciones
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')


    def resolver(self, seleccion, x1_value, x2_value):
        prob = LpProblem(name="Problema", sense=LpMaximize if seleccion == "Maximizar" else LpMinimize)

        x1_var = LpVariable(name="X1", lowBound=0)
        x2_var = LpVariable(name="X2", lowBound=0)

        prob += x1_value * x1_var + x2_value * x2_var

        for res in self.restricciones:
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

        # Preparar datos para la gráfica
        A = []
        b = []

        for res in self.restricciones:
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

        # Encontrar los vértices de la región factible
        for i in range(len(A)):
            for j in range(i + 1, len(A)):
                A_sub = np.array([A[i], A[j]])
                b_sub = np.array([b[i], b[j]])
                if np.linalg.matrix_rank(A_sub) == 2:
                    try:
                        vertice = np.linalg.solve(A_sub, b_sub)
                        if all(vertice >= 0):
                            valid = True
                            for k, res in enumerate(self.restricciones):
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

        # Preparar el mensaje de resultados
        vertices_msg = "\n".join([f"Vértice {i+1}: X1 = {v[0]:.2f}, X2 = {v[1]:.2f}, Z = {vertice_values[i]:.2f}" for i, v in enumerate(vertice_sol)])
        mensaje_opt = f"{vertices_msg}\n\nLa optimización se alcanza en:\nX1 = {optimal_x1:.2f}\nX2 = {optimal_x2:.2f}\nValor óptimo = {optimal_value:.2f}"

        # Crear un frame para la gráfica y los resultados
        frame_grafica = tk.Frame(scrollable_frame, bg='#f8d7da')
        frame_grafica.grid(row=4, column=0, columnspan=5, pady=10)

        frame_resultado = tk.Frame(scrollable_frame, bg='#f8d7da')
        frame_resultado.grid(row=4, column=5, padx=10, pady=10, sticky="n")

        # Crear la gráfica de restricciones
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')

        x1_vals = np.linspace(0, 400, 250)
        for i, res in enumerate(self.restricciones[2:], start=2):
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

        # Marcar la solución óptima en la gráfica
        ax.plot(optimal_x1, optimal_x2, 'ro', label='Solución óptima')
        ax.text(optimal_x1, optimal_x2, f'({optimal_x1:.2f}, {optimal_x2:.2f})', fontsize=8)

        # Ajustar límites de los ejes
        if vertice_sol:
            max_x1 = max([v[0] for v in vertice_sol])
            max_x2 = max([v[1] for v in vertice_sol])
            ax.set_xlim(0, max_x1 + 20)  # Añadir un margen
            ax.set_ylim(0, max_x2 + 20)  # Añadir un margen
        else:
            ax.set_xlim(0, 400)  # Límites por defecto
            ax.set_ylim(0, 400)  # Límites por defecto

        ax.grid(True)
        ax.legend()

        # Mostrar la gráfica en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Mostrar el resultado en un Label dentro del frame_resultado
        resultado_label = tk.Label(frame_resultado, text=mensaje_opt, bg='#f8d7da', font=("Arial", 10), justify="left")
        resultado_label.pack()

        # Crear la gráfica de restricciones
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')

class Metodo_Simplex:
    def __init__(self, frame_derecho, vars_objetivo, num_variables, cantidad_restricciones):
        self.frame_derecho = frame_derecho
        self.vars_objetivo = vars_objetivo
        self.num_variables = num_variables
        self.cantidad_restricciones = cantidad_restricciones

    def convertir_a_numero(self, valor):
        try:
            return float(valor)
        except ValueError:
            return 0.0

    def obtener_restricciones(self):
        # Aquí deberías obtener las restricciones de tu interfaz gráfica
        A = []  # Matriz de restricciones
        b = []  # Lado derecho de las restricciones
        # Lógica para obtener A y b desde la interfaz gráfica
        return A, b

    def resolver_simplex(self):
        # Limpiar el frame derecho
        for widget in self.frame_derecho.winfo_children():
            widget.destroy()

        # Obtener los coeficientes de la función objetivo
        c = [self.convertir_a_numero(var.get()) for var in self.vars_objetivo]

        # Obtener las restricciones
        A, b = self.obtener_restricciones()

        # Crear la tabla inicial del Simplex
        table = self.crear_tabla_simplex(c, A, b)
        pasos = [table.copy()]

        # Ejecutar el algoritmo Simplex
        optimal, pasos = self.simplex_algorithm(table, pasos)

        if optimal:
            for i, paso in enumerate(pasos):
                self.mostrar_tabla(paso, i + 1)
            self.mostrar_solucion(pasos[-1])
        else:
            messagebox.showinfo("Optimización", "No se encontró una solución óptima.")

    def mostrar_solucion(self, table):
        solucion = [table[i, -1] for i in range(1, len(table))]
        valor_optimo = table[0, -1]  # Valor óptimo de Z

        mensaje = f"Valor óptimo de Z: {valor_optimo}\n\nSolución óptima alcanzada:\n"
        for i in range(len(solucion)):
            mensaje += f"X{i + 1} = {solucion[i]}\n"

        num_filas_ocupadas = self.frame_derecho.grid_size()[1]  # Filas usadas en grid
        label_solucion = tk.Label(self.frame_derecho, text=mensaje, justify="left", font=("Helvetica", 10))
        label_solucion.grid(row=num_filas_ocupadas + 1, column=0, columnspan=10, padx=10, pady=10)

    def mostrar_tabla(self, table, paso_numero):
        row_start = (paso_numero - 1) * (len(table) + 4)  # Offset vertical

        tk.Label(self.frame_derecho, bg='#f8d7da', text=f"{paso_numero}er tablero Simplex", font=("Helvetica", 12, "bold")).grid(row=row_start, column=0, columnspan=len(table[0]) + 1, pady=10)

        headers = [""] + [f"X{i + 1}" for i in range(self.num_variables)] + [f"S{i + 1}" for i in range(self.cantidad_restricciones)] + ["CR"]
        for j, label in enumerate(headers):
            tk.Label(self.frame_derecho, text=label, borderwidth=1, relief="solid", width=10).grid(row=row_start + 1, column=j)

        col_pivote = np.argmin(table[0, :-1])
        ratios = np.where(table[1:, col_pivote] > 0, table[1:, -1] / table[1:, col_pivote], np.inf)
        row_pivote = np.argmin(ratios) + 1

        for i in range(len(table)):
            label = "Z" if i == 0 else f"S{i}"
            row_label = tk.Label(self.frame_derecho, text=label, borderwidth=1, relief="solid", width=10, bg="lightgreen" if i == row_pivote else "")
            row_label.grid(row=row_start + i + 2, column=0)

            for j in range(len(table[i])):
                valor = round(table[i, j], 3) if isinstance(table[i, j], float) else table[i, j]
                bg_color = "lightpink" if j == col_pivote and i == row_pivote else "lightblue" if j == col_pivote else "lightgreen" if i == row_pivote else ""
                cell_label = tk.Label(self.frame_derecho, text=valor, borderwidth=1, relief="solid", width=10, bg=bg_color)
                cell_label.grid(row=row_start + i + 2, column=j + 1)

        variable_entrada = f"X{col_pivote + 1}" if col_pivote < self.num_variables else f"S{col_pivote - self.num_variables + 1}"
        variable_salida = f"S{row_pivote}"

        tk.Label(self.frame_derecho, bg='#f8d7da', text=f"Variable de entrada: {variable_entrada}", font=("Helvetica", 10)).grid(row=row_start + len(table) + 2, column=0, columnspan=len(table[0]) + 1, pady=5)
        tk.Label(self.frame_derecho, bg='#f8d7da', text=f"Variable de salida: {variable_salida}", font=("Helvetica", 10)).grid(row=row_start + len(table) + 3, column=0, columnspan=len(table[0]) + 1, pady=5)

    def crear_tabla_simplex(self, c, A, b):
        num_restricciones = len(A)
        num_variables = len(c)
        num_variables_total = num_variables + num_restricciones

        table = np.zeros((num_restricciones + 1, num_variables_total + 1))
        table[0, :num_variables] = -np.array(c)
        for i in range(num_restricciones):
            table[i + 1, :num_variables] = A[i]
            table[i + 1, num_variables + i] = 1
            table[i + 1, -1] = b[i]

        return table

    def simplex_algorithm(self, table, pasos):
        while True:
            col_pivote = np.argmin(table[0, :-1])
            if table[0, col_pivote] >= 0:
                return True, pasos

            ratios = table[1:, -1] / table[1:, col_pivote]
            row_pivote = np.argmin(np.where(ratios <= 0, np.inf, ratios)) + 1

            if ratios[row_pivote - 1] <= 0:
                messagebox.showinfo("Optimización", "El problema es no acotado.")
                return False, pasos

            table[row_pivote] /= table[row_pivote, col_pivote]
            for i in range(len(table)):
                if i != row_pivote:
                    table[i] -= table[i, col_pivote] * table[row_pivote]

            pasos.append(table.copy())