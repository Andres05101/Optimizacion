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

def convertir_a_numero(valor):
    try:
        return float(valor)  # Intenta convertir a decimal
    except ValueError:
        try:
            return float(Fraction(valor))  # Intenta convertir a fracción
        except ValueError:
            messagebox.showerror("Error", f"La entrada '{valor}' no es un número válido.")
            raise  # Re-lanza la excepción para que sea manejada en otro lugar

def confirmar_variables():
    global num_variables, cantidad_restricciones
    try:
        num_variables = int(numVar.get())  # Número de variables debe seguir siendo un entero
        cantidad_restricciones = int(resCan.get())  # La cantidad de restricciones también debe ser un entero
        
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

            # Menú desplegable para seleccionar ≤ o ≥
            signo_var = tk.StringVar()
            signo_var.set("≤")  # Valor por defecto
            opciones_signo = ["≤", "≥"]
            menu_signo = tk.OptionMenu(frame_izquierdo, signo_var, *opciones_signo)
            menu_signo.grid(row=i + 3, column=num_variables * 2 + 1, padx=5, pady=5)
            restricciones[i].append(signo_var)  # Guardar el valor seleccionado en restricciones

            constante_entry = tk.Entry(frame_izquierdo, width=5)
            constante_entry.grid(row=i + 3, column=num_variables * 2 + 2, padx=5, pady=5)
            restricciones_constantes.append(constante_entry)

        # Mostrar botón para resolver
        tk.Button(frame_izquierdo, bg='#f8d7da', text="Resolver", command=resolver).grid(row=cantidad_restricciones + 3, column=0, pady=10, columnspan=2)
    
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese valores válidos.")
def resolver():
    funcion_objetivo, restricciones_valores = obtener_valores()

    if tipo_seleccionado.get() == "Método Gráfico":
        metodo_grafico = Metodo_Grafico(funcion_objetivo, restricciones_valores, frame_derecho)
        metodo_grafico.graficar_restricciones()
        metodo_grafico.resolver()

    elif tipo_seleccionado.get() == "Método Simplex":
        metodo_simplex = Metodo_Simplex(cantidad_restricciones, num_variables, vars_objetivo, restricciones, restricciones_constantes, frame_derecho)
        metodo_simplex.resolver_simplex()  # Cambio aquí para llamar al método correcto

def actualizar_seleccion(value):
    global metodo_seleccionado
    metodo_seleccionado = value

def obtener_valores():
    funcion_objetivo = [float(entry.get()) for entry in vars_objetivo]
    restricciones_valores = []
    for i in range(cantidad_restricciones):
        restriccion = [float(entry.get()) for entry in restricciones[i][:-1]]  # Excluye el signo
        signo = restricciones[i][-1].get()  # Obtiene el valor del menú desplegable
        constante = float(restricciones_constantes[i].get())
        restricciones_valores.append(restriccion + [signo, constante])  # Incluye el signo y la constante
    return funcion_objetivo, restricciones_valores

class Metodo_Grafico:
    def __init__(self, funcion_objetivo, restricciones, frame_derecho):
        self.funcion_objetivo = funcion_objetivo
        self.restricciones = restricciones
        self.frame_derecho = frame_derecho

        # Añadir restricciones de no negatividad (X1 ≥ 0 y X2 ≥ 0)
        self.restricciones += [
            [1, 0, "≥", 0],  # X1 ≥ 0
            [0, 1, "≥", 0]   # X2 ≥ 0
        ]

    def graficar_restricciones(self):
        # Limpiar frame_derecho antes de mostrar nueva gráfica y resultados
        for widget in self.frame_derecho.winfo_children():
            widget.destroy()

        # Crear figura para la gráfica
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlabel('X1')
        ax.set_ylabel('X2')
        ax.set_title('Gráfico de restricciones y región factible')

        x1_vals = np.linspace(0, 25, 400)  # Asegurar que x1_vals solo sea positivo

        # Inicializamos listas para calcular las intersecciones
        intersecciones = []
        for i, restriccion in enumerate(self.restricciones):
            coef_x1, coef_x2, signo, constante = restriccion

            # Graficar restricciones solo en el primer cuadrante
            if coef_x2 != 0:
                x2_vals = (constante - coef_x1 * x1_vals) / coef_x2
                x2_vals = np.maximum(x2_vals, 0)  # Limitar X2 a valores positivos
                ax.plot(x1_vals, x2_vals, label=f'Restricción {i+1}: {coef_x1}X1 + {coef_x2}X2 {signo} {constante}')
            else:
                x1_vals_restr = np.full_like(x1_vals, constante / coef_x1)
                x1_vals_restr = np.maximum(x1_vals_restr, 0)  # Limitar X1 a valores positivos
                ax.plot(x1_vals_restr, x1_vals, label=f'Restricción {i+1}: {coef_x1}X1 {signo} {constante}')

            # Cálculo de las intersecciones con los ejes
            if coef_x1 != 0:
                interseccion_x1 = constante / coef_x1
                if interseccion_x1 >= 0:
                    intersecciones.append([interseccion_x1, 0])
            if coef_x2 != 0:
                interseccion_x2 = constante / coef_x2
                if interseccion_x2 >= 0:
                    intersecciones.append([0, interseccion_x2])

        # Encontrar los vértices factibles
        vertice_sol = self.encontrar_vertices_factibles()

        # Rellenar la región factible
        if len(vertice_sol) > 2:
            hull = ConvexHull(np.array(vertice_sol))  # Ordenar los vértices para el área convexa
            region_factible = np.array(vertice_sol)[hull.vertices]
            ax.fill(region_factible[:, 0], region_factible[:, 1], color='lightblue', alpha=0.5, label='Región factible')

        # Resolver el problema y marcar la solución óptima
        optimal_x1, optimal_x2, valor_optimo = self.resolver()
        ax.plot(optimal_x1, optimal_x2, 'ro', label=f'Óptimo (X1={optimal_x1:.2f}, X2={optimal_x2:.2f})')
        ax.text(optimal_x1, optimal_x2, f'({optimal_x1:.2f}, {optimal_x2:.2f})', fontsize=8, verticalalignment='bottom')

        ax.legend()
        ax.grid(True)

        # Mostrar la gráfica en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_derecho)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, padx=10, pady=10)

        # Mostrar las intersecciones y la solución óptima en texto a la derecha de la gráfica
        resultado_texto = tk.Text(self.frame_derecho, height=10, width=40)
        resultado_texto.pack(side=tk.RIGHT, padx=10, pady=10)
        resultado_texto.insert(tk.END, "Intersecciones:\n")
        for interseccion in vertice_sol:
            resultado_texto.insert(tk.END, f"X1 = {interseccion[0]:.2f}, X2 = {interseccion[1]:.2f}\n")
        resultado_texto.insert(tk.END, f"\nSolución óptima:\nX1 = {optimal_x1:.2f}, X2 = {optimal_x2:.2f}, Valor óptimo Z = {valor_optimo:.2f}")

    def encontrar_vertices_factibles(self):
        A = []
        b = []
        for res in self.restricciones:
            if res[2] == "≤":
                A.append([res[0], res[1]])
                b.append(res[3])
            elif res[2] == "≥":
                A.append([-res[0], -res[1]])
                b.append(-res[3])

        A = np.array(A)
        b = np.array(b)

        vertices = []
        for i in range(len(A)):
            for j in range(i + 1, len(A)):
                A_sub = np.array([A[i], A[j]])
                b_sub = np.array([b[i], b[j]])
                if np.linalg.matrix_rank(A_sub) == 2:
                    try:
                        vertice = np.linalg.solve(A_sub, b_sub)
                        if all(vertice >= 0):  # Solo considerar puntos en el primer cuadrante
                            # Verificar si el vértice cumple con las restricciones
                            factible = True
                            for k, res in enumerate(self.restricciones):
                                if res[2] == "≤" and not (res[0] * vertice[0] + res[1] * vertice[1] <= res[3]):
                                    factible = False
                                    break
                                elif res[2] == "≥" and not (res[0] * vertice[0] + res[1] * vertice[1] >= res[3]):
                                    factible = False
                                    break
                                elif res[2] == "=" and not np.isclose(res[0] * vertice[0] + res[1] * vertice[1], res[3]):
                                    factible = False
                                    break

                            if factible:
                                vertices.append(vertice)
                    except np.linalg.LinAlgError:
                        continue

        return vertices

    def resolver(self):
        # Definir problema de optimización
        prob = LpProblem(name="Problema", sense=LpMaximize)
        x1_var = LpVariable(name="X1", lowBound=0)
        x2_var = LpVariable(name="X2", lowBound=0)

        # Función objetivo
        prob += self.funcion_objetivo[0] * x1_var + self.funcion_objetivo[1] * x2_var

        # Añadir restricciones
        for res in self.restricciones:
            if res[2] == "≤":
                prob += res[0] * x1_var + res[1] * x2_var <= res[3]
            elif res[2] == "≥":
                prob += res[0] * x1_var + res[1] * x2_var >= res[3]

        # Resolver el problema
        prob.solve()

        # Devolver solución óptima
        optimal_x1 = x1_var.value()
        optimal_x2 = x2_var.value()
        valor_optimo = prob.objective.value()

        return optimal_x1, optimal_x2, valor_optimo

class Metodo_Simplex:

    def __init__(self, cantidad_restricciones, num_variables, vars_objetivo, restricciones, restricciones_constantes, frame_derecho):
        self.cantidad_restricciones = cantidad_restricciones
        self.num_variables = num_variables
        self.vars_objetivo = vars_objetivo
        self.restricciones = restricciones
        self.restricciones_constantes = restricciones_constantes
        self.frame_derecho = frame_derecho
        self.variables_basicas = []
        self.variables_holgura = []
    
        self.valores_finales = {f'X{i+1}': 0 for i in range(num_variables)}  # Inicializamos todas las Xn en 0
   
    def convertir_a_numero(self, valor):
        try:
            return float(valor)  # Intenta convertir a decimal
        except ValueError:
            try:
                return float(Fraction(valor))  # Intenta convertir a fracción
            except ValueError:
                messagebox.showerror("Error", f"La entrada '{valor}' no es un número válido.")
                raise  # Re-lanza la excepción para que sea manejada en otro lugar
    
    def obtener_valores():
        funcion_objetivo = [float(entry.get()) for entry in vars_objetivo]
        restricciones_valores = []
        for i in range(cantidad_restricciones):
            restriccion = [float(entry.get()) for entry in restricciones[i]]
            constante = float(restricciones_constantes[i].get())
            restricciones_valores.append(restriccion + ['≤', constante])
        return funcion_objetivo, restricciones_valores

    def obtener_restricciones(self):
        A = []
        b = []
        for i in range(self.cantidad_restricciones):
            restriccion = []
            for entry in self.restricciones[i][:-1]:  # Excluye el último valor (el signo de la desigualdad)
                valor = entry.get()
                if '/' in valor:  # Si hay una barra de fracción en la entrada
                    valor = float(Fraction(valor))  # Convertir a fracción
                else:
                    valor = float(valor)  # Convertir a decimal
                restriccion.append(valor)
            constante = self.restricciones_constantes[i].get()  # Constante al final de la restricción
            if '/' in constante:
                constante = float(Fraction(constante))  # Convertir fracción a decimal
            else:
                constante = float(constante)
            A.append(restriccion)
            b.append(constante)
        return A, b

    def resolver_simplex(self):
        # Limpiar el frame derecho
        for widget in self.frame_derecho.winfo_children():
            widget.destroy()

        # Obtener los coeficientes de la función objetivo
        c = [self.convertir_a_numero(var.get()) for var in self.vars_objetivo]  # Usando self.convertir_a_numero()

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
        # Diccionario para almacenar el valor de cada Xn, inicialmente todos en 0
        valores_variables = {f'X{i + 1}': 0 for i in range(self.num_variables)}

        # Guardamos los valores de las variables básicas (holguras o Xn) que están en la base
        for i in range(1, len(table)):
            variable_basica = self.variables_holgura[i - 1]
            valor = table[i, -1]

            # Si la variable básica es una variable de decisión (Xn), le asignamos su valor
            if variable_basica.startswith('X'):
                valores_variables[variable_basica] = valor

        valor_optimo = table[0, -1]  # Valor óptimo de Z

        # Crear el mensaje de solución
        mensaje = f"Valor óptimo de Z: {valor_optimo}\n\nSolución óptima alcanzada:\n"
        for var, valor in valores_variables.items():
            mensaje += f"{var} = {valor}\n"

        # Mostrar el mensaje en el frame derecho debajo de las tablas generadas
        num_filas_ocupadas = self.frame_derecho.grid_size()[1]  # Obtiene la cantidad de filas ya usadas en grid
        label_solucion = tk.Label(self.frame_derecho, text=mensaje, justify="left", font=("Helvetica", 10))
        label_solucion.grid(row=num_filas_ocupadas + 1, column=0, columnspan=10, padx=10, pady=10)

    def mostrar_tabla(self, table, paso_numero):
        if paso_numero == 1:  # Solo inicializamos las variables en la primera iteración
            self.variables_basicas = [f"X{i+1}" for i in range(self.num_variables)] + [f"S{i+1}" for i in range(self.cantidad_restricciones)]
            self.variables_holgura = [f"S{i+1}" for i in range(self.cantidad_restricciones)]

        row_start = (paso_numero - 1) * (len(table) + 4)  # Offset para la posición vertical de la tabla
        hay_valores_negativos_en_z = np.any(table[0, :-1] < 0)

        tk.Label(self.frame_derecho, bg='#f8d7da', text=f"{paso_numero}er tablero Simplex", font=("Helvetica", 12, "bold")).grid(row=row_start, column=0, columnspan=len(table[0]) + 1, pady=10)

        headers = [""] + self.variables_basicas + ["CR"]
        for j, label in enumerate(headers):
            if hay_valores_negativos_en_z and j - 1 == np.argmin(table[0, :-1]):  # Si j - 1 (ajuste por el índice de las etiquetas) es la columna pivote
                tk.Label(frame_derecho, text=label, borderwidth=1, relief="solid", width=10, bg="yellow").grid(row=row_start + 1, column=j)
            else:
                tk.Label(frame_derecho, text=label, borderwidth=1, relief="solid", width=10).grid(row=row_start + 1, column=j)

        if hay_valores_negativos_en_z:
            col_pivote = np.argmin(table[0, :-1])
            ratios = np.where(table[1:, col_pivote] > 0, table[1:, -1] / table[1:, col_pivote], np.inf)
            row_pivote = np.argmin(ratios) + 1  # +1 porque la primera fila es la fila Z
        else:
            col_pivote = None
            row_pivote = None

        for i in range(len(table)):
            label = "Z" if i == 0 else self.variables_holgura[i - 1]
            # Resaltar la primera celda de la fila pivote
            if hay_valores_negativos_en_z and i == row_pivote:
                row_label = tk.Label(frame_derecho, text=label, borderwidth=1, relief="solid", width=10, bg="yellow")
            else:
                row_label = tk.Label(frame_derecho, text=label, borderwidth=1, relief="solid", width=10)
            row_label.grid(row=row_start + i + 2, column=0)

            for j in range(len(table[i])):
                valor = round(table[i, j], 3)
                bg_color = None
                if hay_valores_negativos_en_z:
                    if j == col_pivote and i == row_pivote:
                        bg_color = "lightpink"
                    elif j == col_pivote:
                        bg_color = "lightblue"
                    elif i == row_pivote:
                        bg_color = "lightgreen"
                tk.Label(self.frame_derecho, text=valor, borderwidth=1, relief="solid", width=10, bg=bg_color).grid(row=row_start + i + 2, column=j + 1)

        if hay_valores_negativos_en_z:
            variable_entrada = f"X{col_pivote + 1}" if col_pivote < self.num_variables else f"S{col_pivote - self.num_variables + 1}"
            variable_salida = self.variables_holgura[row_pivote - 1]
            self.variables_holgura[row_pivote - 1] = variable_entrada

            tk.Label(self.frame_derecho, bg='#f8d7da', text=f"Variable de entrada: {variable_entrada}", font=("Helvetica", 10)).grid(row=row_start + len(table) + 2, column=0, columnspan=len(table[0]) + 1, pady=5)
            tk.Label(self.frame_derecho, bg='#f8d7da', text=f"Variable de salida: {variable_salida}", font=("Helvetica", 10)).grid(row=row_start + len(table) + 3, column=0, columnspan=len(table[0]) + 1, pady=5)

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

root = tk.Tk()
root.geometry("950x600")
root.title("Resolución de Problemas de Programación Lineal")
root.configure(bg='#f8d7da')

# Frame principal
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)
main_frame.config(bg="#f8d7da")

# Canvas para el scroll
canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
canvas.config(bg="#f8d7da")

# Scrollbar
scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar.config(bg="#f8d7da")

# Configurar el canvas para usar el scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Crear un Frame dentro del canvas
second_frame = tk.Frame(canvas)
second_frame.config(bg="#f8d7da")

# Añadir el frame secundario al canvas
canvas.create_window((0, 0), window=second_frame, anchor="nw")

# Crear los frames izquierdo y derecho
frame_izquierdo = tk.Frame(second_frame, bg='#f8d7da')
frame_izquierdo.pack(side=tk.LEFT, padx=10, pady=10)
frame_izquierdo.config(bg='#f8d7da')

frame_derecho = tk.Frame(second_frame, bg='#f8d7da')
frame_derecho.pack(side=tk.RIGHT, padx=10, pady=10)
frame_derecho.config(bg='#f8d7da')

# Menú desplegable para Maximización o Minimización
opciones = ["Maximizar", "Minimizar"]
metodo_seleccionado = tk.StringVar()
metodo_seleccionado.set(opciones[0])  # Valor por defecto
tk.Label(frame_izquierdo, bg='#f8d7da', text="Seleccione Maximización o Minimización:").grid(row=0, column=0, padx=10, pady=10, columnspan=2)
menu_desplegable = tk.OptionMenu(frame_izquierdo, metodo_seleccionado, *opciones)
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

# Botón para confirmar
tk.Button(frame_izquierdo, bg='#f8d7da', text="Confirmar", command=confirmar_variables).grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()
