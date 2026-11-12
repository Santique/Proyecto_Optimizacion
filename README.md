# OptiAgro-Llanos

Aplicación web local para minimizar el costo logístico entre empresas agropecuarias y plantas mediante programación lineal (HiGHS) y un algoritmo genético.

## Inicio

```powershell
cd D:\Codigo_fuente\Proyecto_Optimizacion\Proyecto_Optimizacion
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

La aplicación se abre en `http://localhost:8501`. Ejecutar pruebas con `pytest`.

Los datos de demostración (10 empresas y cuatro plantas) son ficticios porque las fuentes no contienen una matriz regional completa. Cárguelos desde el Panel. Los datos reales, ejecuciones y escenarios se conservan en `datos/optiagro.sqlite3`; para respaldarlos, cierre la aplicación y copie dicho archivo.

## Resultado de pruebas

No se ejecutaron pruebas en esta sesión porque la configuración del intérprete Python fue omitida explícitamente. Las pruebas incluidas cubren el óptimo conocido CP-01 (64), capacidad insuficiente y reproducibilidad del AG; ejecute `pytest` antes de entregar.

Consulte `PLAN.md` para trazabilidad de HU y `SUPUESTOS.md` para limitaciones, decisiones y elementos pendientes de ratificación.
