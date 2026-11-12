# Plan y trazabilidad

## Modelo implementado

Red dirigida bipartita `I × J`, variable continua `x_ij ≥ 0`, objetivo `min Σ c_ij x_ij`. En el modo base, `Σj x_ij = s_i` y `Σi x_ij ≤ d_j`; se admiten demanda exacta y mínima en el motor exacto. Los arcos son configurables y pueden tener límite.

## Trazabilidad resumida

| HU | Implementación | Prueba/estado |
|---|---|---|
| 04-17 | `app.py`, `persistencia/`, validaciones | CRUD y validación manual; CP-01/02 |
| 18,20,21 | `visualizacion/grafos.py`, vista Red | grafo y flujos |
| 22-25,54,56,57 | escenarios y ejecuciones SQLite | historial/exportación |
| 26-30 | `optimizacion/metodo_exacto/` | CP-01, CP-02 |
| 31-36 | `optimizacion/algoritmo_genetico/` | factibilidad y semilla |
| 37-43 | servicio de sensibilidad | reoptimización y duales |
| 44-49 | vista de resultados e historial CSV | costo, tiempo y datos exportables |
| 50-52,58-61 | Streamlit local, README, pruebas | adaptado/documentado |
| 01-03,53,55 | No implementadas | fuera del alcance fijo |

Los vacíos y conflictos se registran en `SUPUESTOS.md`.
