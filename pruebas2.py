import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.spatial import ConvexHull
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable
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

        # Mostrar botón para resolver, ajustado para llamar a la función resolver_problema
        tk.Button(frame_izquierdo, bg='#f8d7da', text="Resolver", command=resolver).grid(row=cantidad_restricciones + 3, column=0, pady=10, columnspan=2)
    
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese un número válido de variables y restricciones.")

def resolver():
    funcion_objetivo, restricciones_valores = obtener_valores()

    if tipo_seleccionado.get() == "Método Gráfico":
        # Crear una instancia de Metodo_Grafico y resolver
        metodo_grafico = Metodo_Grafico(funcion_objetivo, restricciones_valores, frame_derecho)
        metodo_grafico.graficar_restricciones()
        metodo_grafico.resolver(tipo_seleccionado.get(), funcion_objetivo[0], funcion_objetivo[1])
        print("metodo grafico")
              
    elif tipo_seleccionado.get() == "Método Simplex":
        # Crear una instancia de Metodo_Simplex y resolver
        metodo_simplex = Metodo_Simplex(frame_derecho, vars_objetivo, num_variables, cantidad_restricciones)
        metodo_simplex.resolver_simplex()
        print("metodo simplex")

def actualizar_seleccion(value):
    global metodo_seleccionado
    metodo_seleccionado = value

def obtener_valores():
    # Extraer la función objetivo
    funcion_objetivo = [float(entry.get()) for entry in vars_objetivo]

    # Extraer las restricciones
    restricciones_valores = []
    for i in range(cantidad_restricciones):
        restriccion = [float(entry.get()) for entry in restricciones[i]]
        constante = float(restricciones_constantes[i].get())
        restricciones_valores.append(restriccion + ['≤', constante])  # Por ahora asumo que todas son ≤

    return funcion_objetivo, restricciones_valores

class Metodo_Grafico():
    def __init__(self, funcion_objetivo, restricciones, scrollable_frame):  
        self.funcion_objetivo = funcion_objetivo  # (coef_x1, coef_x2)
        self.restricciones = restricciones  # [(coef_x1, coef_x2, signo, constante)]
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

        # Crear el frame para la gráfica en Tkinter
        frame_grafica = tk.Frame(self.scrollable_frame, bg='#f8d7da')
        frame_grafica.grid(row=4, column=0, columnspan=5, pady=10)

        canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def resolver(self, seleccion, x1_value, x2_value):
        prob = LpProblem(name="Problema", sense=LpMaximize if seleccion == "Maximizar" else LpMinimize)

        x1_var = LpVariable(name="X1", lowBound=0)
        x2_var = LpVariable(name="X2", lowBound=0)

        prob += x1_value * x1_var + x2_value * x2_var

        for res in self.restricciones:
            coef_x1, coef_x2, signo, constante = res
            if signo == "≤":
                prob += coef_x1 * x1_var + coef_x2 * x2_var <= constante
            elif signo == "≥":
                prob += coef_x1 * x1_var + coef_x2 * x2_var >= constante
            elif signo == "=":
                prob += coef_x1 * x1_var + coef_x2 * x2_var == constante

        prob.solve()

        optimal_x1 = x1_var.value()
        optimal_x2 = x2_var.value()
        optimal_value = prob.objective.value()

        # Calcular los vértices de la región factible
        A = []
        b = []

        for res in self.restricciones:
            coef_x1, coef_x2, signo, constante = res
            if signo == "≤":
                A.append([coef_x1, coef_x2])
                b.append(constante)
            elif signo == "≥":
                A.append([-coef_x1, -coef_x2])
                b.append(-constante)
            elif signo == "=":
                A.append([coef_x1, coef_x2])
                b.append(constante)

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
                            for k, res in enumerate(self.restricciones):
                                coef_x1, coef_x2, signo, constante = res
                                if signo == "≤" and not (coef_x1 * vertice[0] + coef_x2 * vertice[1] <= constante):
                                    valid = False
                                    break
                                elif signo == "≥" and not (coef_x1 * vertice[0] + coef_x2 * vertice[1] >= constante):
                                    valid = False
                                    break
                                elif signo == "=" and not np.isclose(coef_x1 * vertice[0] + coef_x2 * vertice[1], constante):
                                    valid = False
                                    break
                            if valid:
                                vertice_sol.append(vertice)
                    except np.linalg.LinAlgError:
                        continue

        # Calcular los valores de Z en cada vértice
        vertice_values = [x1_value * v[0] + x2_value * v[1] for v in vertice_sol]

        # Mostrar resultados
        vertices_msg = "\n".join([f"Vértice {i+1}: X1 = {v[0]:.2f}, X2 = {v[1]:.2f}, Z = {vertice_values[i]:.2f}" for i, v in enumerate(vertice_sol)])
        mensaje_opt = f"{vertices_msg}\n\nLa optimización se alcanza en:\nX1 = {optimal_x1:.2f}\nX2 = {optimal_x2:.2f}\nValor óptimo = {optimal_value:.2f}"

        # Crear frames para mostrar resultados y gráfica
        frame_resultado = tk.Frame(self.scrollable_frame, bg='#f8d7da')
        frame_resultado.grid(row=4, column=5, padx=10, pady=10, sticky="n")

        resultado_label = tk.Label(frame_resultado, text=mensaje_opt, bg='#f8d7da', font=("Arial", 10), justify="left")
        resultado_label.pack()

        # Mostrar la gráfica de la región factible
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Inecuaciones y región factible de soluciones')

        x1_vals = np.linspace(0, 10, 400)
        for i, res in enumerate(self.restricciones):
            coef_x1, coef_x2, signo, constante = res
            if coef_x2 != 0:
                x2_vals_restr = (constante - coef_x1 * x1_vals) / coef_x2
                ax.plot(x1_vals, x2_vals_restr, label=f'Restricción {i+1}: {coef_x1}X1 + {coef_x2}X2 {signo} {constante}')
            else:
                x1_vals_restr = np.full_like(x1_vals, constante / coef_x1)
                ax.plot(x1_vals_restr, x1_vals, label=f'Restricción {i+1}: {coef_x1}X1 {signo} {constante}')

        # Graficar la región factible
        if len(vertice_sol) > 2:
            hull = ConvexHull(np.array(vertice_sol))
            region_factible = np.array(vertice_sol)[hull.vertices]
            ax.fill(region_factible[:, 0], region_factible[:, 1], color='grey', alpha=0.4, label='Región Factible')

        # Mostrar el punto óptimo
        ax.plot(optimal_x1, optimal_x2, 'ro', label='Solución óptima')
        ax.text(optimal_x1, optimal_x2, f'({optimal_x1:.2f}, {optimal_x2:.2f})', fontsize=8)

        ax.grid(True)
        ax.legend()

        # Mostrar la gráfica en Tkinter
        frame_grafica = tk.Frame(self.scrollable_frame, bg='#f8d7da')
        frame_grafica.grid(row=4, column=0, columnspan=5, pady=10)

        canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

def convertir_a_numero(valor):
        try:
            return float(valor)  # Intenta convertir a decimal
        except ValueError:
            try:
                return float(Fraction(valor))  # Intenta convertir a fracción
            except ValueError:
                messagebox.showerror("Error", f"La entrada '{valor}' no es un número válido.")
                raise  # Re-lanza la excepción para que sea manejada en otro lugar

class Metodo_Simplex():
    def __init__(self, frame_derecho, vars_objetivo, num_variables, cantidad_restricciones):
        self.frame_derecho = frame_derecho
        self.vars_objetivo = vars_objetivo
        self.num_variables = num_variables
        self.cantidad_restricciones = cantidad_restricciones
        self.variables_basicas = []
        self.variables_holgura = []

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

        # Mostrar el mensaje en el frame derecho debajo de las tablas generadas
        mensaje = f"Valor óptimo de Z: {valor_optimo}\n\nSolución óptima alcanzada:\n"
        for i in range(len(solucion)):
            mensaje += f"X{i + 1} = {solucion[i]}\n"

        # Encuentra el número de la última fila utilizada
        num_filas_ocupadas = self.frame_derecho.grid_size()[1]  # Obtiene la cantidad de filas ya usadas en grid

        # Agrega el mensaje debajo de las tablas
        label_solucion = tk.Label(self.frame_derecho, text=mensaje, justify="left", font=("Helvetica", 10))
        label_solucion.grid(row=num_filas_ocupadas + 1, column=0, columnspan=10, padx=10, pady=10)

    def mostrar_tabla(self, table, paso_numero):
        row_start = (paso_numero - 1) * (len(table) + 4)  # Offset para la posición vertical de la tabla

        # Inicializa las variables básicas (X1, X2, ...) y las variables de holgura (S1, S2, ...)
        if paso_numero == 1:  # Solo inicializamos las variables en la primera iteración
            self.variables_basicas = [f"X{i+1}" for i in range(self.num_variables)] + [f"S{i+1}" for i in range(self.cantidad_restricciones)]
            self.variables_holgura = [f"S{i+1}" for i in range(self.cantidad_restricciones)]

        # Mostrar el tablero, destacar pivotes, entrada/salida y demás lógica (igual que antes)

    def crear_tabla_simplex(self, c, A, b):
        num_restricciones = len(A)
        num_variables = len(c)
        num_variables_total = num_variables + num_restricciones

        # Crear la tabla inicial del Simplex
        table = np.zeros((num_restricciones + 1, num_variables_total + 1))
        table[0, :num_variables] = -np.array(c)  # Fila de la función objetivo
        for i in range(num_restricciones):
            table[i + 1, :num_variables] = A[i]
            table[i + 1, num_variables + i] = 1
            table[i + 1, -1] = b[i]

        return table

    def simplex_algorithm(self, table, pasos):
        while True:
            # Identificar columna pivote
            col_pivote = np.argmin(table[0, :-1])
            if table[0, col_pivote] >= 0:
                return True, pasos

            # Identificar fila pivote
            ratios = table[1:, -1] / table[1:, col_pivote]
            row_pivote = np.argmin(np.where(ratios <= 0, np.inf, ratios)) + 1

            if ratios[row_pivote - 1] <= 0:
                messagebox.showinfo("Optimización", "El problema es no acotado.")
                return False, pasos

            # Operaciones para pivoteo
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


# Configurar el canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Configurar el peso de las columnas y filas para el canvas y el scrollbar
ventana.grid_rowconfigure(0, weight=1)
ventana.grid_columnconfigure(0, weight=1)

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

# Mostrar botón para resolver
tk.Button(frame_izquierdo, bg='#f8d7da', text="Confirmar", command=confirmar_variables).grid(row=6, column=0, columnspan=2, pady=10)
ventana.mainloop()
