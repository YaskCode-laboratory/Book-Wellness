import os
import subprocess
from datetime import datetime


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Carpeta donde está este archivo: tests/
CARPETA_TESTS = os.path.dirname(os.path.abspath(__file__))

# Carpeta raíz del proyecto
CARPETA_PROYECTO = os.path.dirname(CARPETA_TESTS)

# Carpeta de resultados
CARPETA_RESULTADOS = os.path.join(CARPETA_TESTS, "resultados")

# Crear la carpeta si no existe
os.makedirs(CARPETA_RESULTADOS, exist_ok=True)


# ============================================================
# CREAR ARCHIVO DE RESULTADOS
# ============================================================

ahora = datetime.now()

fecha_hora = ahora.strftime("%Y-%m-%d_%H-%M-%S")

nombre_archivo = f"resultados_test_{fecha_hora}.txt"

ruta_resultado = os.path.join(
    CARPETA_RESULTADOS,
    nombre_archivo
)


# ============================================================
# ENCABEZADO
# ============================================================

encabezado = (
    "============================================================\n"
    "              RESULTADOS DE TESTS - BOOK WELLNESS\n"
    "============================================================\n\n"
    f"Fecha: {ahora.strftime('%d/%m/%Y')}\n"
    f"Hora: {ahora.strftime('%H:%M:%S')}\n\n"
    "============================================================\n"
    "RESULTADO DE PYTEST\n"
    "============================================================\n\n"
)

# Crear el archivo y escribir el encabezado
with open(ruta_resultado, "w", encoding="utf-8") as archivo:
    archivo.write(encabezado)


# ============================================================
# EJECUTAR PYTEST
# ============================================================

print("=" * 60)
print("EJECUTANDO PRUEBAS DE BOOK WELLNESS")
print("=" * 60)
print()

proceso = subprocess.Popen(
    ["pytest", "-v"],
    cwd=CARPETA_PROYECTO,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="replace",
    bufsize=1
)


# ============================================================
# MOSTRAR EN TIEMPO REAL Y GUARDAR
# ============================================================

with open(ruta_resultado, "a", encoding="utf-8") as archivo:

    for linea in proceso.stdout:
        # Mostrar inmediatamente en la terminal
        print(linea, end="", flush=True)

        # Guardar inmediatamente en el TXT
        archivo.write(linea)
        archivo.flush()


# Esperar a que Pytest termine
codigo_salida = proceso.wait()


# ============================================================
# GUARDAR RESULTADO FINAL
# ============================================================

with open(ruta_resultado, "a", encoding="utf-8") as archivo:
    archivo.write(
        "\n============================================================\n"
        f"CÓDIGO DE SALIDA: {codigo_salida}\n"
        "============================================================\n"
    )


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 60)
print("PRUEBAS FINALIZADAS")
print("=" * 60)
print(f"Resultados guardados en:")
print(ruta_resultado)
print("=" * 60)
