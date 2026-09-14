# Análisis Geotécnico de Zapata Combinada Irregular

**Autor:** Daniel Andres Buitrago Capera

Este repositorio contiene `geotecnia.py`, un script de Python que ejecuta un **análisis geotécnico completo de una zapata combinada irregular** (forzada por un lindero), típica en cimentaciones de edificación.

---

## 1. ¿De qué trata este código?

`geotecnia.py` define la clase **`IrregularCombinedFooting`**, la cual representa una zapata de trapecio asimétrico sujeta a un conjunto de cargas de columna, y realiza el siguiente análisis:

- **Geometría**: traza los vértices del polígono de la zapata (un trapecio irregular definido por el lindero) y calcula su **área**, **centroide** (`Xc`, `Yc`) y **momentos de inercia** (`Ix`, `Iy`).
- **Cargas**: calcula la **carga total** (`Q`) y el **punto de aplicación de la resultante** (`Xr`, `Yr`) a partir de las cargas de cada columna.
- **Excentricidades**: obtención de `ex` y `ey` como la diferencia entre el centro de cargas y el centroide geométrico.
- **Presiones de contacto**: calcula la presión en cada esquina de la zapata con la **fórmula biaxial** `q = Q/A ± Mx·y/Ix ± My·x/Iy`, y alerta si alguna presión resulta negativa (levantamiento).
- **Verificación geotécnica**: compara la presión máxima contra la **presión admisible del suelo** e indica si el diseño es aceptado o falla geotécnicamente.
- **Graficación**: genera una figura con dos vistas:
  - **Vista en planta**: geometría de la zapata, ubicación de columnas, centroide geométrico, centro de cargas y presiones en esquinas.
  - **Corte transversal (Sección A-A')**: estratigrafía del suelo (relleno, arena arcillosa, nivel freático), ubicación de la zapata a la profundidad de desplante `Df` y diagrama trapezoidal de presiones.

### Convención de ejes

- El eje **horizontal** es el eje **X** (dirección del lindero).
- El eje **vertical** es el eje **Y** (medida en metros).
- Los puntos de la zapata `(points[:, 0], points[:, 1])` se interpretan como (X, Y).

---

## 2. Requisitos e instalación

### Dependencias

El script depende de la librería `pysections/sections.py` (para la clase base `_SinglePolygonSection`) y de las bibliotecas:

- `numpy`
- `matplotlib`

### Requisitos previos

- Python 3.8 o superior.
- `pip` disponible.

### Opción A: Instalación automática desde Git

```bash
# 1. Clonar el repositorio completo
git clone <URL_DEL_REPOSITORIO> PrimerCorte
cd PrimerCorte

# 2. (Opcional) Crear y activar un entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# 3. Instalar las dependencias (numpy y matplotlib)
pip install numpy matplotlib
```

### Opción B: Instalación manual

1. Descarga/copia `geotecnia.py` y la carpeta `pysections/` (con `sections.py`) en tu proyecto, manteniendo la estructura de carpetas del repositorio.
2. Instala las dependencias:

```bash
pip install numpy matplotlib
```

3. `geotecnia.py` ya agrega la carpeta `pysections/` al `sys.path` automáticamente, así que no necesitas configurar nada más para que encuentre a `sections.py`.

---

## 3. Uso y ejemplos

### Ejemplo 1: Ejecución directa del script (análisis con datos de ejemplo)

El archivo incluye al final un bloque de ejecución con dos columnas de ejemplo. Simplemente corre:

```bash
python geotecnia.py
```

Esto calcula presiones, verifica la presión admisible y abre el gráfico de planta + corte. La salida en consola es:

```
--------------------------------------------------
RESULTADOS DEL ANÁLISIS GEOMÉTRICO Y CARGAS
--------------------------------------------------
Área de la zapata (A):     24.00 m²
Centroide Zapata (Xc, Yc): (3.25, 1.50) m
Centro de Cargas (Xr, Yr): (2.30, 1.50) m
Excentricidades (ex, ey):  (-0.95, 0.00) m
Inercias (Ix, Iy):         (34.00, 70.50) m^4
--------------------------------------------------
PRESIONES DE CONTACTO EN ESQUINAS (q = Q/A ± Mx·y/Ix ± My·x/Iy)
--------------------------------------------------
Vértice 1 [0. 0.]:  213.65 kPa
Vértice 2 [6. -1.]:  11.52 kPa
Vértice 3 [6. 4.]:   11.52 kPa
Vértice 4 [0. 3.]:   213.65 kPa
--------------------------------------------------
DISEÑO ACEPTADO: El esfuerzo máximo de 213.65 kPa es MENOR a 250.0 kPa.
```

### Ejemplo 2: Uso como biblioteca con cargas propias

Puedes importar la clase y definir tus propias columnas. **Nota:** para evitar que se ejecute el análisis de ejemplo al importar, separa el bloque de ejecución del módulo (mueve las líneas finales a un `if __name__ == "__main__":`) o copia la clase a tu propio archivo.

```python
from geotecnia import IrregularCombinedFooting

# Columnas como tuplas (coordenada X, coordenada Y, carga en kN)
columnas = [
    (1.0, 2.0, 1200),
    (4.5, 1.0,  800),
]

zapata = IrregularCombinedFooting(columnas)

# Presión de contacto en cada esquina de la zapata
presiones = zapata.corner_pressures()
for i, q in enumerate(presiones, start=1):
    print(f"Vértice {i}: {q:.2f} kPa")

# Cálculo de la resultante de cargas
Q_total, Xr, Yr = zapata.load_resultant()
print(f"Carga total: {Q_total:.0f} kN")
print(f"Resultante en ({Xr:.2f}, {Yr:.2f}) m")
```

### Ejemplo 3: Alerta de levantamiento y verificación manual

Si la carga resultante cae demasiado excéntrica, alguna esquina puede presentar **presión negativa (levantamiento)**. Accede a los parámetros geométricos expuestos por la clase base para contrastarlos con tus cálculos:

```python
from geotecnia import IrregularCombinedFooting

# Columna muy excéntrica para provocar levantamiento
columnas = [
    (5.5, 1.5, 2000),
]

zapata = IrregularCombinedFooting(columnas)

# Parámetros geométricos de la zapata
print(f"Área:        {zapata.area:.2f} m²")
print(f"Centroide X: {zapata.y:.2f} m")   # _SinglePolygonSection expone y y z
print(f"Centroide Y: {zapata.z:.2f} m")
print(f"Inercia Ix:  {zapata.Iyy:.2f} m^4")
print(f"Inercia Iy:  {zapata.Izz:.2f} m^4")

q = zapata.corner_pressures()
presion_max = max(q)
q_adm = 250.0
print(f"Presión máxima: {presion_max:.2f} kPa")

if presion_max > q_adm:
    print("FALLA GEOTÉCNICA: el esfuerzo máximo supera la presión admisible.")
elif min(q) < 0:
    print("ALERTA: existe levantamiento en al menos una esquina.")
else:
    print("DISEÑO ACEPTADO.")
```

### Ejemplo 4: Zapata irregular excepcional (6 lados y 3 columnas)

Caso especial con una zapata de **6 lados** sujeta a **tres columnas**. Para ello se crea una subclase de `IrregularCombinedFooting` que sobrescribe `_calculate_points()` con los vértices del hexágono.

Este caso usa un **perfil de suelo modificado** respecto al ejemplo de base: el estrato intermedio pasa de *arena arcillosa* a **arcilla `γ=17.0 kN/m³`** y el **nivel freático baja un metro** (de `z=2.5 m` a `z=3.5 m`). La estratigrafía se pasa como parámetros de `plot_geotechnical_analysis()` (relleno `γ=17.5 kN/m³` y profundidad de desplante `Df=1.5 m` se mantienen).

```python
import numpy as np
from geotecnia import IrregularCombinedFooting

class IrregularSixSidedFooting(IrregularCombinedFooting):
    """Zapata hexagonal irregular (6 lados)."""
    def _calculate_points(self):
        pts = np.zeros((6, 2), dtype=float)
        pts[0] = [0.0, 0.0]    # Inferior izquierda
        pts[1] = [3.0, -0.8]   # Inferior media
        pts[2] = [6.0, -1.0]   # Inferior derecha
        pts[3] = [6.0, 4.0]    # Superior derecha
        pts[4] = [3.2, 4.5]    # Superior media
        pts[5] = [0.0, 3.0]    # Superior izquierda
        return pts

# Tres columnas: (coordenada X, coordenada Y, carga en kN)
columnas = [
    (1.0, 1.0, 900),
    (3.0, 3.0, 700),
    (5.0, 1.0, 600),
]

zapata = IrregularSixSidedFooting(columnas)
presiones = zapata.corner_pressures()

# Planta + corte con arcilla (γ=17.0) y nivel freático en z=3.5 m
zapata.plot_geotechnical_analysis(material='Arcilla', gamma=17.0,
                                  material_sat='Arcilla Saturada', nf=3.5)
```

**Salida esperada (aproximada):**

```
Área de la zapata (A):     27.80 m²
Centroide Zapata (Xc, Yc): (3.22, 1.68) m
Centro de Cargas (Xr, Yr): (2.73, 1.64) m
Excentricidades (ex, ey):  (-0.50, -0.04) m
Inercias (Ix, Iy):         (53.23, 76.34) m^4
--------------------------------------------------
PRESIONES DE CONTACTO EN ESQUINAS
--------------------------------------------------
Vértice 1 [0. 0.]:    127.86 kPa
Vértice 2 [3. -0.8]:   86.31 kPa
Vértice 3 [6. -1.]:    43.80 kPa
Vértice 4 [6. 4.]:     35.73 kPa
Vértice 5 [3.2 4.5]:   74.90 kPa
Vértice 6 [0. 3.]:     123.02 kPa
```

El diseño resulta **aceptado**: la presión máxima de `127.86 kPa` es menor que la admisible de `250 kPa`, y no se presenta levantamiento en ninguna esquina (todas las presiones son positivas).

> **Consejo:** para reutilizar el análisis con otra geometría de zapata, crea una subclase de `IrregularCombinedFooting` y sobrescribe `_calculate_points()` para definir tus propios vértices; todo el análisis (centroide, inercias, presiones, gráficos) se reutiliza automáticamente.

---

## Estructura del repositorio

```
PrimerCorte/
├── README.md          ← Documentación (este archivo)
├── geotecnia.py       ← Análisis geotécnico de zapata combinada irregular
└── pysections/
    ├── sections.py    ← Librería base de cálculo de secciones (dependencia, bajo GPLv3)
    ├── README.org
    └── LICENSE        ← Licencia de la librería pysections (GPLv3)