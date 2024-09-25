import tkinter as tk
from tkinter import messagebox
import numpy as np
from fractions import Fraction

def confirmar_variables():
    global num_variables, cantidad_restricciones
    num_variables = int(numVar.get())
    cantidad_restricciones = int(resCan.get())

    
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
    tk.Button(frame_izquierdo, bg='#f8d7da', text="Resolver", command=resolver_simplex).grid(row=cantidad_restricciones + 3, column=0, pady=10, columnspan=2)

vars_objetivo = []
restricciones = []
restricciones_constantes = []

def convertir_a_numero(valor):
    try:
        return float(valor)  # Intenta convertir a decimal
    except ValueError:
        try:
            return float(Fraction(valor))  # Intenta convertir a fracción
        except ValueError:
            messagebox.showerror("Error", f"La entrada '{valor}' no es un número válido.")
            raise  # Re-lanza la excepción para que sea manejada en otro lugar

def obtener_restricciones():
    A = []
    b = []
    for i in range(cantidad_restricciones):
        restriccion = []
        for entry in restricciones[i]:
            valor = entry.get()
            if '/' in valor:  # Si hay una barra de fracción en la entrada
                valor = float(Fraction(valor))  # Convertir a fracción
            else:
                valor = float(valor)  # Convertir a decimal
            restriccion.append(valor)
        constante = restricciones_constantes[i].get()
        if '/' in constante:  # Si hay una barra de fracción en la entrada
            constante = float(Fraction(constante))  # Convertir a fracción
        else:
            constante = float(constante)  # Convertir a decimal
        A.append(restriccion)
        b.append(constante)
    return A, b

def resolver_simplex():
    # Limpiar el frame derecho
    for widget in frame_derecho.winfo_children():
        widget.destroy()

    # Obtener los coeficientes de la función objetivo
    c = [convertir_a_numero(var.get()) for var in vars_objetivo]

    # Obtener las restricciones
    A, b = obtener_restricciones()

    # Crear la tabla inicial del Simplex
    table = crear_tabla_simplex(c, A, b)
    pasos = [table.copy()]

    # Ejecutar el algoritmo Simplex
    optimal, pasos = simplex_algorithm(table, pasos)

    if optimal:
        for i, paso in enumerate(pasos):
            mostrar_tabla(paso, i + 1)
        mostrar_solucion(pasos[-1])
    else:
        messagebox.showinfo("Optimización", "No se encontró una solución óptima.")


def mostrar_solucion(table):
    solucion = [table[i, -1] for i in range(1, len(table))]
    valor_optimo = table[0, -1]  # Valor óptimo de Z

    # Mostrar el mensaje en el frame derecho debajo de las tablas generadas
    mensaje = f"Valor óptimo de Z: {valor_optimo}\n\nSolución óptima alcanzada:\n"
    for i in range(len(solucion)):
        mensaje += f"X{i + 1} = {solucion[i]}\n"

    # Encuentra el número de la última fila utilizada
    num_filas_ocupadas = frame_derecho.grid_size()[1]  # Obtiene la cantidad de filas ya usadas en grid

    # Agrega el mensaje debajo de las tablas
    label_solucion = tk.Label(frame_derecho, text=mensaje, justify="left", font=("Helvetica", 10))
    label_solucion.grid(row=num_filas_ocupadas + 1, column=0, columnspan=10, padx=10, pady=10)
    

def mostrar_tabla(table, paso_numero):
    
    global variables_basicas, variables_holgura  # Para que estas listas puedan ser modificadas entre iteraciones
        
    # Inicializa las variables básicas (X1, X2, ...) y las variables de holgura (S1, S2, ...)
    if paso_numero == 1:  # Solo inicializamos las variables en la primera iteración
        variables_basicas = [f"X{i+1}" for i in range(num_variables)] + [f"S{i+1}" for i in range(cantidad_restricciones)]
        variables_holgura = [f"S{i+1}" for i in range(cantidad_restricciones)]

    row_start = (paso_numero - 1) * (len(table) + 4)  # Offset para la posición vertical de la tabla
    
    # Verificar si la fila Z tiene valores negativos
    hay_valores_negativos_en_z = np.any(table[0, :-1] < 0)

    # Título para la tabla de la iteración
    tk.Label(frame_derecho, bg='#f8d7da', text=f"{paso_numero}er tablero Simplex", font=("Helvetica", 12, "bold")).grid(row=row_start, column=0, columnspan=len(table[0]) + 1, pady=10)

    # Etiquetas de las columnas
    headers = [""] + variables_basicas + ["CR"]
    for j, label in enumerate(headers):
        if hay_valores_negativos_en_z and j - 1 == np.argmin(table[0, :-1]):  # Si j - 1 (ajuste por el índice de las etiquetas) es la columna pivote
            tk.Label(frame_derecho, text=label, borderwidth=1, relief="solid", width=10, bg="yellow").grid(row=row_start + 1, column=j)
        else:
            tk.Label(frame_derecho, text=label, borderwidth=1, relief="solid", width=10).grid(row=row_start + 1, column=j)

    if hay_valores_negativos_en_z:
        # Identificar la columna pivote (mínimo valor negativo en la fila Z)
        col_pivote = np.argmin(table[0, :-1])

        # Calcular los ratios de CR/columna pivote (ignorando divisiones por cero o valores negativos)
        ratios = np.where(table[1:, col_pivote] > 0, table[1:, -1] / table[1:, col_pivote], np.inf)
        row_pivote = np.argmin(ratios) + 1  # +1 porque la primera fila es la fila Z
    else:
        col_pivote = None
        row_pivote = None

    # Etiquetas de las filas y datos de la tabla
    for i in range(len(table)):
        label = "Z" if i == 0 else variables_holgura[i - 1]

        # Resaltar la primera celda de la fila pivote
        if hay_valores_negativos_en_z and i == row_pivote:
            row_label = tk.Label(frame_derecho, text=label, borderwidth=1, relief="solid", width=10, bg="yellow")
        else:
            row_label = tk.Label(frame_derecho, text=label, borderwidth=1, relief="solid", width=10)
        row_label.grid(row=row_start + i + 2, column=0)

        # Datos de la tabla
        for j in range(len(table[i])):
            valor = round(table[i, j], 3) if isinstance(table[i, j], float) else table[i, j]

            # Resaltar solo si hay valores negativos en Z
            if hay_valores_negativos_en_z:
                if j == col_pivote and i == row_pivote:
                    # Intersección entre fila y columna pivote
                    cell_label = tk.Label(frame_derecho, text=valor, borderwidth=1, relief="solid", width=10, bg="lightpink")
                elif j == col_pivote and i != row_pivote:
                    # Columna pivote (variable de entrada), resalta la primera celda 
                    if i == 0:
                        cell_label = tk.Label(frame_derecho, text=valor, borderwidth=1, relief="solid", width=10, bg="lightblue")
                    else:
                        cell_label = tk.Label(frame_derecho, text=valor, borderwidth=1, relief="solid", width=10, bg="lightblue")
                elif i == row_pivote and j != col_pivote:
                    # Fila pivote (variable de salida), resaltar la primera celda 
                    if j == 0:
                        cell_label = tk.Label(frame_derecho, text=valor, borderwidth=1, relief="solid", width=10, bg="lightgreen")
                    else:
                        cell_label = tk.Label(frame_derecho, text=valor, borderwidth=1, relief="solid", width=10, bg="lightgreen")
                else:
                    cell_label = tk.Label(frame_derecho, text=valor, borderwidth=1, relief="solid", width=10)
            else:
                # Sin resaltar si no hay valores negativos en Z
                cell_label = tk.Label(frame_derecho, text=valor, borderwidth=1, relief="solid", width=10)
            cell_label.grid(row=row_start + i + 2, column=j + 1)

    if hay_valores_negativos_en_z:
        # Indicar la variable de entrada y salida solo si hay valores negativos en Z
        variable_entrada = f"X{col_pivote + 1}" if col_pivote < num_variables else f"S{col_pivote - num_variables + 1}"
        variable_salida = variables_holgura[row_pivote - 1]
        # Actualizar los nombres de las variables
        variables_holgura[row_pivote - 1] = variable_entrada
        

        # Etiquetas de las variables de entrada y salida
        tk.Label(frame_derecho, bg='#f8d7da', text=f"Variable de entrada: {variable_entrada}", font=("Helvetica", 10)).grid(row=row_start + len(table) + 2, column=0, columnspan=len(table[0]) + 1, pady=5)
        tk.Label(frame_derecho, bg='#f8d7da', text=f"Variable de salida: {variable_salida}", font=("Helvetica", 10)).grid(row=row_start + len(table) + 3, column=0, columnspan=len(table[0]) + 1, pady=5)


def crear_tabla_simplex(c, A, b):
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

def simplex_algorithm(table, pasos):
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

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Método Simplex")
ventana.geometry("1200x800")
ventana.configure(bg='#f8d7da')

# Crear frames para organizar la interfaz
frame_izquierdo = tk.Frame(ventana)
frame_izquierdo.pack(side=tk.LEFT, padx=10, pady=10)
frame_izquierdo.config(bg='#f8d7da')
frame_derecho = tk.Frame(ventana)
frame_derecho.config(bg='#f8d7da')
frame_derecho.pack(side=tk.RIGHT, padx=10, pady=10)

# Entradas iniciales para número de variables y restricciones
tk.Label(frame_izquierdo, text="Número de Variables:", bg='#f8d7da').grid(row=0, column=0, padx=10, pady=10)
numVar = tk.Entry(frame_izquierdo, width=5)
numVar.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_izquierdo, text="Cantidad de Restricciones:", bg='#f8d7da').grid(row=1, column=0, padx=10, pady=10)
resCan = tk.Entry(frame_izquierdo, width=5)
resCan.grid(row=1, column=1, padx=5, pady=5)

tk.Button(frame_izquierdo, text="Confirmar", command=confirmar_variables, bg='#f5c6cb').grid(row=2, column=0, columnspan=2, pady=10)

ventana.mainloop()