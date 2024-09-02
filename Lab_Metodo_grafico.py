import tkinter as tk
from tkinter import messagebox, simpledialog
import numpy as np
import matplotlib.pyplot as plt

class LinearProgrammingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Método Gráfico de Programación Lineal")

        self.create_widgets()

    def create_widgets(self):
        # Frame para la función objetivo
        frame_obj = tk.LabelFrame(self.root, text="Función Objetivo: Max Z = ax + by", padx=10, pady=10)
        frame_obj.grid(row=0, column=0, padx=10, pady=10)

        tk.Label(frame_obj, text="a:").grid(row=0, column=0)
        tk.Label(frame_obj, text="b:").grid(row=0, column=2)

        self.entry_a = tk.Entry(frame_obj, width=5)
        self.entry_a.grid(row=0, column=1)

        self.entry_b = tk.Entry(frame_obj, width=5)
        self.entry_b.grid(row=0, column=3)

        tk.Button(self.root, text="Añadir Restricciones", command=self.ask_restrictions).grid(row=1, column=0, pady=10)

    def ask_restrictions(self):
        try:
            self.a = float(self.entry_a.get())
            self.b = float(self.entry_b.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos para a y b.")
            return

        self.num_restrictions = tk.simpledialog.askinteger("Restricciones", "¿Cuántas restricciones desea añadir?", minvalue=1, maxvalue=10)
        if self.num_restrictions:
            self.show_restriction_entries()

    def show_restriction_entries(self):
        self.restrictions = []
        for i in range(self.num_restrictions):
            frame = tk.LabelFrame(self.root, text=f"Restricción {i+1}", padx=10, pady=10)
            frame.grid(row=2+i, column=0, padx=10, pady=5)

            tk.Label(frame, text="Tipo de restricción:").grid(row=0, column=0)
            var_type = tk.StringVar(value="lineal")
            tk.Radiobutton(frame, text="ax + by <= c", variable=var_type, value="ax+by<=c").grid(row=0, column=1)
            tk.Radiobutton(frame, text="ax + by >= c", variable=var_type, value="ax+by>=c").grid(row=0, column=2)
            tk.Radiobutton(frame, text="y <= kx", variable=var_type, value="y<=kx").grid(row=0, column=3)
            tk.Radiobutton(frame, text="y >= kx", variable=var_type, value="y>=kx").grid(row=0, column=4)

            tk.Label(frame, text="a:").grid(row=1, column=0)
            entry_a = tk.Entry(frame, width=5)
            entry_a.grid(row=1, column=1)

            tk.Label(frame, text="b:").grid(row=1, column=2)
            entry_b = tk.Entry(frame, width=5)
            entry_b.grid(row=1, column=3)

            tk.Label(frame, text="c / k:").grid(row=1, column=4)
            entry_c = tk.Entry(frame, width=5)
            entry_c.grid(row=1, column=5)

            self.restrictions.append((entry_a, entry_b, entry_c, var_type))

        tk.Button(self.root, text="Resolver", command=self.solve).grid(row=2+self.num_restrictions, column=0, pady=10)

    def solve(self):
        try:
            # Extraer y validar los valores de las restricciones
            coefficients = []
            for entry_a, entry_b, entry_c, var_type in self.restrictions:
                a = float(entry_a.get()) if entry_a.get() else 0
                b = float(entry_b.get()) if entry_b.get() else 0
                c_or_k = float(entry_c.get())
                coefficients.append((a, b, c_or_k, var_type.get()))
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos para las restricciones.")
            return

        self.plot_graph(coefficients)

    def plot_graph(self, coefficients):
        x = np.linspace(0, 200, 400)
        plt.figure()

        for a, b, c_or_k, constraint_type in coefficients:
            if constraint_type in ("ax+by<=c", "ax+by>=c"):
                if b != 0:
                    y = (c_or_k - a * x) / b
                else:
                    y = np.full_like(x, c_or_k)
                plt.plot(x, y, label=f'{a}x + {b}y {constraint_type[-2:]} {c_or_k}')
                if constraint_type == "ax+by<=c":
                    plt.fill_between(x, y, y2=0, where=(y >= 0), color='gray', alpha=0.2)
                else:
                    plt.fill_between(x, y, y2=200, where=(y <= 200), color='gray', alpha=0.2)

            elif constraint_type == "y<=kx":
                y = c_or_k * x
                plt.plot(x, y, label=f'y <= {c_or_k}x')
                plt.fill_between(x, y, y2=0, color='gray', alpha=0.2)

            elif constraint_type == "y>=kx":
                y = c_or_k * x
                plt.plot(x, y, label=f'y >= {c_or_k}x')
                plt.fill_between(x, y, y2=200, color='gray', alpha=0.2)

        plt.xlim((0, 200))
        plt.ylim((0, 200))
        plt.xlabel('x')
        plt.ylabel('y')

        # Graficar la función objetivo
        z = (self.a * x + self.b * 0) / self.b
        plt.plot(x, z, 'r--', label=f'Función Objetivo: Z = {self.a}x + {self.b}y')

        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = LinearProgrammingApp(root)
    root.mainloop()
