# Proyecto de Optimización Matemática

Un sistema completo de herramientas para resolver problemas de optimización matemática, incluyendo programación lineal y teoría de grafos.

## Descripción

Este proyecto implementa métodos fundamentales de optimización matemática con interfaces gráficas interactivas:

- **Programación Lineal**: Método Gráfico y Algoritmo Simplex
- **Teoría de Grafos**: Algoritmos Dijkstra y Bellman-Ford
- **Visualización**: Grafos interactivos y regiones factibles
- **Interfaz Gráfica**: Aplicaciones con Tkinter

## Estructura del Proyecto

```
Optimizacion/
├── proyecto.py              # Aplicación principal de grafos
├── Solucionador_PO.py       # Solucionador unificado de Programación Lineal
├── Metodo_simplex.py        # Implementación del algoritmo Simplex
├── Metodo_grafico.py        # Método gráfico para 2 variables
├── Metodo_Grafos.py         # Algoritmos de grafos (Dijkstra, Bellman-Ford)
├── puebas.py               # Pruebas de interfaz con scrollbars
├── Informe Metodo Simplex.docx  # Documentación del método Simplex
├── Cici.pdf                # Documentación adicional
└── README.md               # Este archivo
```

## Instalación

### Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Dependencias

Instala las dependencias necesarias:

```bash
pip install numpy
pip install matplotlib
pip install networkx
pip install scipy
pip install pulp
pip install tkinter
```

### Instalación Completa

1. Clona o descarga el repositorio
2. Navega al directorio del proyecto:
   ```bash
   cd Optimizacion
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### 1. Solucionador de Programación Lineal

Ejecuta el solucionador principal:

```bash
python Solucionador_PO.py
```

**Características:**
- Método Gráfico (2 variables)
- Algoritmo Simplex (n variables)
- Visualización de regiones factibles
- Cálculo de soluciones óptimas

### 2. Aplicación de Grafos

Ejecuta la aplicación de teoría de grafos:

```bash
python proyecto.py
```

**Funcionalidades:**
- Creación de grafos mediante matrices de adyacencia
- Algoritmo Dijkstra para rutas más cortas
- Algoritmo Bellman-Ford
- Visualización interactiva de grafos
- Análisis de nodos adyacentes

### 3. Métodos Individuales

#### Método Simplex
```bash
python Metodo_simplex.py
```

#### Método Gráfico
```bash
python Metodo_grafico.py
```

#### Algoritmos de Grafos
```bash
python Metodo_Grafos.py
```

## Funcionalidades Detalladas

### A. Programación Lineal

#### Método Gráfico
- **Variables**: Máximo 2 variables (X₁, X₂)
- **Restricciones**: ≤, ≥, =
- **Visualización**: Región factible y vértices óptimos
- **Solución**: Punto óptimo y valor de la función objetivo

#### Algoritmo Simplex
- **Variables**: N variables (X₁, X₂, ..., Xₙ)
- **Restricciones**: ≤, ≥, =
- **Proceso**: Tablas paso a paso
- **Resultado**: Solución óptima con valores de variables

### B. Teoría de Grafos

#### Algoritmo Dijkstra
- **Entrada**: Matriz de adyacencia
- **Salida**: Rutas más cortas desde un nodo origen
- **Visualización**: Grafo con rutas resaltadas

#### Algoritmo Bellman-Ford
- **Característica**: Maneja pesos negativos
- **Detección**: Ciclos negativos
- **Aplicación**: Grafos con restricciones complejas

#### Análisis de Grafos
- **Nodos adyacentes**: Conexiones directas
- **Matrices**: Representación de adyacencia
- **Visualización**: Grafos dirigidos y no dirigidos

## Ejemplos de Uso

### Ejemplo 1: Programación Lineal

**Problema:**
Maximizar Z = 3X₁ + 2X₂
Sujeto a:
- X₁ + X₂ ≤ 4
- 2X₁ + X₂ ≤ 6
- X₁, X₂ ≥ 0

**Solución:**
1. Ejecutar `Solucionador_PO.py`
2. Seleccionar "Método Gráfico"
3. Ingresar coeficientes de la función objetivo
4. Agregar restricciones
5. Resolver y visualizar resultado

### Ejemplo 2: Grafo con Dijkstra

**Problema:**
Encontrar la ruta más corta desde A hasta todos los nodos:

```
Matriz de adyacencia:
A  B  C  D
A  0  4  2  0
B  4  0  1  5
C  2  1  0  3
D  0  5  3  0
```

**Solución:**
1. Ejecutar `proyecto.py`
2. Ingresar tamaño de matriz (4)
3. Llenar matriz de adyacencia
4. Ejecutar Dijkstra desde nodo A

## Tecnologías Utilizadas

- **Python 3.x**: Lenguaje principal
- **Tkinter**: Interfaces gráficas
- **Matplotlib**: Visualizaciones
- **NetworkX**: Manipulación de grafos
- **NumPy**: Cálculos numéricos
- **SciPy**: Algoritmos de optimización
- **PuLP**: Programación lineal

### Conceptos Teóricos

#### Programación Lineal
- **Función Objetivo**: Función a optimizar
- **Restricciones**: Limitaciones del problema
- **Región Factible**: Conjunto de soluciones válidas
- **Solución Óptima**: Mejor solución posible

#### Teoría de Grafos
- **Nodo**: Punto en el grafo
- **Arista**: Conexión entre nodos
- **Peso**: Valor asociado a una arista
- **Ruta más Corta**: Camino con menor peso total

## Solución de Problemas

### Errores Comunes

1. **"ModuleNotFoundError"**
   - Solución: Instalar dependencias con `pip install`

2. **"Tkinter not found"**
   - Solución: Instalar tkinter según tu sistema operativo

3. **"Matplotlib backend error"**
   - Solución: Verificar instalación de matplotlib

### Validación de Entrada

- **Números**: Solo valores numéricos válidos
- **Fracciones**: Formato "a/b" (ej: "3/4")
- **Matrices**: Valores enteros para grafos
- **Restricciones**: Coeficientes y constantes válidos

## Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un pull request

## 📄 Licencia

Este proyecto está bajo licencia educativa para fines académicos.

## 👥 Autores

- **Yeimy Vanessa Lopez Terreros**
- **Michael Andres Rodriguez Estrada**

