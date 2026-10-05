# Tests — Book Wellness

La carpeta `tests` contiene las pruebas automatizadas del proyecto **Book Wellness**. Su objetivo es comprobar que diferentes partes de la aplicación funcionen correctamente y detectar posibles errores antes de realizar cambios o nuevas implementaciones.

Las pruebas están realizadas utilizando **Pytest**, por lo que pueden ejecutarse directamente desde la terminal.

## 📋 Requisito

Para ejecutar las pruebas es necesario tener instalada la librería **Pytest** en Python.

```bash
pip install pytest
```

## ▶️ Ejecutar las pruebas

Existen dos formas de ejecutar las pruebas.

### 1. Ejecutar las pruebas normalmente

Si solamente quieres comprobar el funcionamiento de las pruebas y ver los resultados en la terminal:

```bash
pytest -v
```

Esto ejecutará las pruebas y mostrará su resultado directamente en la terminal.

### 2. Ejecutar las pruebas y generar un reporte TXT

Dentro de `tests` se encuentra `test.py`. Este archivo permite ejecutar las pruebas mediante Pytest y, además, guardar automáticamente los resultados en un archivo `.txt`.

Desde la **raíz del proyecto** se ejecuta:

```bash
python tests\\test.py
```

Al utilizar este comando:

- Se ejecutan todas las pruebas mediante `pytest -v`.
- Los resultados continúan mostrándose **en tiempo real** en la terminal.
- Se crea automáticamente la carpeta `tests/resultados` si no existe.
- Se genera un nuevo archivo `.txt` por cada ejecución.
- El nombre del archivo incluye la fecha y hora de la prueba.

Ejemplo:

```text
tests/
├── test.py
└── resultados/
    ├── resultados_test_2026-10-05_14-30-15.txt
    └── resultados_test_2026-10-05_15-42-08.txt
```

De esta manera, `pytest -v` puede seguir utilizándose normalmente cuando solo se quiera comprobar el funcionamiento, mientras que `test.py` permite conservar un reporte de cada ejecución.

## ⚠️ Observación sobre Google Books

Una de las pruebas relacionadas con **Google Books** utiliza una clave real de prueba para realizar una consulta sobre un libro específico.

Actualmente, esta prueba utiliza la información asociada al **libro de prueba configurado en el test**.

Si en algún momento esa clave deja de ser válida, cambia sus permisos, alcanza algún límite o deja de permitir la consulta utilizada por la prueba, **el test podría comenzar a fallar aunque el funcionamiento general de Google Books dentro de la aplicación siga siendo correcto**.

Por este motivo, si dicha prueba comienza a fallar inesperadamente, se recomienda comprobar primero la validez de la clave utilizada y la disponibilidad de la consulta del libro de prueba.

---

## 💡 Resumen rápido

| Acción | Comando |
|---|---|
| Ejecutar pruebas | `pytest -v` |
| Ejecutar pruebas + generar reporte TXT | `python tests\\test.py` |
| Instalar Pytest | `pip install pytest` |

> **Nota:** Los reportes generados por `test.py` se almacenan automáticamente dentro de `tests/resultados/`.
