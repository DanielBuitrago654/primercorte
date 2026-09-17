import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pysections'))

from sections import Section, _SinglePolygonSection
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class IrregularCombinedFooting(_SinglePolygonSection):
    def __init__(self, columns_data):
        """
        columns_data: lista de tuplas [(Px, Py, Carga_P), ...]
        """
        self.columns = columns_data
        super().__init__() # Llama a _calculate_points

    def _calculate_points(self):
        """
        Vértices del trapecio asimétrico forzado por el lindero.
        Debe ser un polígono cerrado y ordenado (sentido antihorario).
        """
        pts = np.zeros((4, 2), dtype=float)
        pts[0] = [0.0, 0.0]   # Inferior izquierda
        pts[1] = [6.0, -1.0]  # Inferior derecha
        pts[2] = [6.0, 4.0]   # Superior derecha
        pts[3] = [0.0, 3.0]   # Superior izquierda
        return pts
    
    def load_resultant(self):
        """Calcula la carga total y el punto de aplicación (Resultante)"""
        Q_total = sum([col[2] for col in self.columns])
        
        Mx_origen = sum([col[2] * col[1] for col in self.columns])
        My_origen = sum([col[2] * col[0] for col in self.columns])
        
        Xr = My_origen / Q_total
        Yr = Mx_origen / Q_total
        return Q_total, Xr, Yr

    def corner_pressures(self, verbose=True):
        """
        Calcula las presiones en los vértices usando la fórmula general biaxial.
        """
        Q, Xr, Yr = self.load_resultant()
        
        A = self.area        
        Xc = self.y          
        Yc = self.z          
        Ix = self.Iyy        
        Iy = self.Izz        
        
        ex = Xr - Xc
        ey = Yr - Yc
        
        My = Q * ex  
        Mx = Q * ey  
        
        if verbose:
            print("-" * 50)
            print("RESULTADOS DEL ANÁLISIS GEOMÉTRICO Y CARGAS")
            print("-" * 50)
            print(f"Área de la zapata (A):     {A:.2f} m²")
            print(f"Centroide Zapata (Xc, Yc): ({Xc:.2f}, {Yc:.2f}) m")
            print(f"Centro de Cargas (Xr, Yr): ({Xr:.2f}, {Yr:.2f}) m")
            print(f"Excentricidades (ex, ey):  ({ex:.2f}, {ey:.2f}) m")
            print(f"Inercias (Ix, Iy):         ({Ix:.2f}, {Iy:.2f}) m^4")
            print("-" * 50)
            
            print("PRESIONES DE CONTACTO EN ESQUINAS (q = Q/A ± Mx·y/Ix ± My·x/Iy)")
            print("-" * 50)
        
        q_esquinas = []
        for i, punto in enumerate(self.points): 
            x_prima = punto[0] - Xc
            y_prima = punto[1] - Yc
            
            q = (Q / A) + (My * x_prima / Iy) + (Mx * y_prima / Ix)
            q_esquinas.append(q)
            
            if verbose:
                print(f"Vértice {i+1} {punto}: {q:.2f} kPa")
            
            if verbose and q < 0:
                print(f" -> ¡ALERTA! Presión negativa (Levantamiento) en vértice {i+1}.")
                
        return q_esquinas

    def plot_geotechnical_analysis(self, material='Arena Arcillosa', gamma=18.5,
                                   material_sat='Arena Arcillosa Saturada', nf=2.5,
                                   filename=None):
        """
        Genera un gráfico compuesto con la vista en planta de la zapata 
        y un corte transversal geotécnico con el diagrama de presiones.

        Parámetros del perfil de suelo (reemplazan la estratigrafía fija):
        - material: nombre del estrato intermedio (por defecto 'Arena Arcillosa').
        - gamma: peso unitario de ese estrato en kN/m³ (por defecto 18.5).
        - material_sat: nombre del mismo estrato por debajo del nivel freático.
        - nf: profundidad del nivel freático desde la superficie en m (por defecto 2.5).
        - filename: nombre del archivo (.jpg) para guardar el gráfico. Si no se indica
          o si falla/no hay entorno gráfico interactivo, se genera automáticamente como .jpg
          en la misma carpeta del script.
        """
        Q, Xr, Yr = self.load_resultant()
        Xc = self.y  
        Yc = self.z  
        q_esquinas = self.corner_pressures(verbose=False)
        
        pts = self.points 
        x_poly = np.append(pts[:, 0], pts[0, 0])
        y_poly = np.append(pts[:, 1], pts[0, 1])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Análisis Geotécnico: Zapata Combinada Irregular', fontsize=16, fontweight='bold')
        
        # --- VISTA EN PLANTA (ax1) ---
        ax1.set_title("Vista en Planta (Geometría y Presiones)")
        ax1.plot(x_poly, y_poly, color='black', linewidth=2)
        ax1.fill(x_poly, y_poly, 'lightgray', alpha=0.5)
        
        ax1.scatter(pts[:, 0], pts[:, 1], color='black', zorder=5)
        for i, (px, py) in enumerate(pts):
            q_val = q_esquinas[i]
            ax1.annotate(f'q{i+1}={q_val:.1f} kPa', (px, py), 
                         textcoords="offset points", xytext=(10, 10), 
                         ha='left', fontsize=9, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
        
        for i, col in enumerate(self.columns):
            ax1.scatter(col[0], col[1], marker='s', color='blue', s=100, zorder=6, label='Columnas' if i==0 else "")
            ax1.annotate(f'P{i+1}={col[2]}kN', (col[0], col[1]), textcoords="offset points", xytext=(-15, 15), color='blue', fontweight='bold')
            
        ax1.scatter(Xc, Yc, marker='+', color='green', s=150, zorder=7, label='Centroide Geométrico')
        ax1.scatter(Xr, Yr, marker='x', color='red', s=100, zorder=7, label='Centro de Cargas (Resultante)')
        ax1.plot([Xc, Xr], [Yc, Yr], 'r--', linewidth=1)
        
        ax1.set_xlabel("Eje X (m)")
        ax1.set_ylabel("Eje Y (m)")
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.set_aspect('equal', adjustable='box') 
        ax1.legend(loc='lower right', fontsize=8)
        
        # --- CORTE TRANSVERSAL Y ESTRATIGRAFÍA (ax2) ---
        ax2.set_title("Corte Transversal (Sección A-A')")
        x_min, x_max = min(x_poly) - 1, max(x_poly) + 1
        
        ax2.axhline(0, color='brown', linewidth=2, label="Nivel de Terreno (z=0)")
        ax2.axhspan(-1.5, 0, color='khaki', alpha=0.3, label="Relleno (γ=17.5 kN/m³)")
        ax2.axhline(-1.5, color='gray', linestyle='--')
        ax2.axhspan(-nf, -1.5, color='orange', alpha=0.2,
                    label=f"{material} (γ={gamma:.1f} kN/m³)")
        ax2.axhline(-nf, color='blue', linestyle='-.', linewidth=1.5,
                    label=f"Nivel Freático (z={nf:.1f}m)")
        ax2.axhspan(-4.5, -nf, color='cyan', alpha=0.1, label=f"{material_sat}")
        
        Df = 1.5
        espesor = 0.5
        x_zapata = [min(x_poly), max(x_poly)]
        ax2.add_patch(plt.Rectangle((x_zapata[0], -Df), x_zapata[1]-x_zapata[0], espesor, 
                                    facecolor='gray', edgecolor='black', hatch='//'))
        
        q_izq = max([q_esquinas[i] for i, p in enumerate(pts) if p[0] == min(x_poly)])
        q_der = max([q_esquinas[i] for i, p in enumerate(pts) if p[0] == max(x_poly)])
        
        escala_q = 0.005 
        ax2.plot([x_zapata[0], x_zapata[0]], [-Df, -Df - (q_izq * escala_q)], 'r-', linewidth=2)
        ax2.plot([x_zapata[1], x_zapata[1]], [-Df, -Df - (q_der * escala_q)], 'r-', linewidth=2)
        ax2.plot([x_zapata[0], x_zapata[1]], [-Df - (q_izq * escala_q), -Df - (q_der * escala_q)], 'r-', linewidth=2)
        
        ax2.fill_between([x_zapata[0], x_zapata[1]], [-Df, -Df], 
                         [-Df - (q_izq * escala_q), -Df - (q_der * escala_q)], 
                         color='red', alpha=0.2)
        
        ax2.annotate(f"{q_izq:.1f} kPa", (x_zapata[0], -Df - (q_izq * escala_q) - 0.2), color='red', ha='center', fontweight='bold')
        ax2.annotate(f"{q_der:.1f} kPa", (x_zapata[1], -Df - (q_der * escala_q) - 0.2), color='red', ha='center', fontweight='bold')
        
        ax2.set_xlabel("Distancia Eje X (m)")
        ax2.set_ylabel("Profundidad z (m)")
        ax2.set_ylim(-4.5, 1.0)
        ax2.set_xlim(x_min, x_max)
        ax2.legend(loc='lower left', fontsize=8)
        
        plt.tight_layout()

        # Determinar si el backend actual permite mostrar gráficos en ventana interactiva
        is_interactive = matplotlib.get_backend().lower() not in ['agg', 'template', 'ps', 'pdf', 'svg']
        
        target_filename = filename
        if not target_filename and not is_interactive:
            target_filename = f"{self.__class__.__name__.lower()}_analisis.jpg"

        saved_path = None
        if target_filename:
            if not target_filename.lower().endswith(('.jpg', '.jpeg')):
                target_filename += '.jpg'
            output_dir = os.path.dirname(os.path.abspath(__file__))
            saved_path = os.path.join(output_dir, target_filename) if not os.path.isabs(target_filename) else target_filename
            fig.savefig(saved_path, dpi=300, bbox_inches='tight')
            print(f"Gráfico guardado en: {saved_path}")

        if is_interactive:
            try:
                plt.show()
            except Exception as e:
                print(f"Aviso: No se pudo mostrar en ventana gráfica ({e}).")
                if not saved_path:
                    target_filename = f"{self.__class__.__name__.lower()}_analisis.jpg"
                    output_dir = os.path.dirname(os.path.abspath(__file__))
                    saved_path = os.path.join(output_dir, target_filename)
                    fig.savefig(saved_path, dpi=300, bbox_inches='tight')
                    print(f"Gráfico guardado como respaldo en: {saved_path}")
        else:
            plt.close(fig)

# ==========================================
# EJECUCIÓN DEL EJERCICIO
# ==========================================
columnas_proyecto = [
    (0.5, 1.5, 1500), 
    (5.0, 1.5, 1000)  
]

zapata_lindero = IrregularCombinedFooting(columnas_proyecto)
esfuerzos = zapata_lindero.corner_pressures()

q_max = max(esfuerzos)
q_adm = 250.0 

print("-" * 50)
if q_max > q_adm:
    print(f"FALLA GEOTÉCNICA: El esfuerzo máximo de {q_max:.2f} kPa SUPERA los {q_adm} kPa admisibles.")
else:
    print(f"DISEÑO ACEPTADO: El esfuerzo máximo de {q_max:.2f} kPa es MENOR a {q_adm} kPa.")

# AQUÍ ES DONDE SE LLAMA AL GRÁFICO
zapata_lindero.plot_geotechnical_analysis(filename='analisis_zapata_lindero.jpg')


# ==========================================
# CASO EXCEPCIONAL: ZAPATA IRREGULAR DE 6 LADOS CON 3 COLUMNAS
# ==========================================
class IrregularSixSidedFooting(IrregularCombinedFooting):
    """Zapata hexagonal irregular (6 lados). Reescribe los vértices
    heredando todo el análisis geométrico y de presiones."""

    def _calculate_points(self):
        pts = np.zeros((6, 2), dtype=float)
        pts[0] = [0.0, 0.0]    # Inferior izquierda
        pts[1] = [3.0, -0.8]   # Inferior media
        pts[2] = [6.0, -1.0]   # Inferior derecha
        pts[3] = [6.0, 4.0]    # Superior derecha
        pts[4] = [3.2, 4.5]    # Superior media
        pts[5] = [0.0, 3.0]    # Superior izquierda
        return pts


columnas_hex = [
    (1.0, 1.0, 900),
    (3.0, 3.0, 700),
    (5.0, 1.0, 600),
]

zapata_hex = IrregularSixSidedFooting(columnas_hex)
esfuerzos_hex = zapata_hex.corner_pressures()

q_max_hex = max(esfuerzos_hex)

print("-" * 50)
if min(esfuerzos_hex) < 0:
    print("ALERTA: Se presenta levantamiento en al menos una esquina.")
print(f"DISEÑO ACEPTADO: El esfuerzo máximo de {q_max_hex:.2f} kPa es MENOR a {q_adm} kPa."
      if q_max_hex <= q_adm
      else f"FALLA GEOTÉCNICA: El esfuerzo máximo de {q_max_hex:.2f} kPa SUPERA los {q_adm} kPa admisibles.")

# Estrato intermedio de arcilla (γ=17.0 kN/m³) y nivel freático en z=3.5 m
# (1 m más abajo que el del ejemplo base)
zapata_hex.plot_geotechnical_analysis(material='Arcilla', gamma=17.0,
                                      material_sat='Arcilla Saturada', nf=3.5,
                                      filename='analisis_zapata_hexagonal.jpg')