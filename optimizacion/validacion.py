"""Validaciones compartidas y verificación independiente de soluciones."""
from __future__ import annotations
import math
from dominio.modelos import ParametrosModelo

def validar(parametros: ParametrosModelo) -> list[str]:
    errores: list[str] = []
    empresas, plantas, arcos = parametros.empresas, parametros.plantas, parametros.arcos
    if not empresas: errores.append("Debe existir al menos una empresa.")
    if not plantas: errores.append("Debe existir al menos una planta.")
    if len({x.id for x in empresas}) != len(empresas): errores.append("Los identificadores de empresas deben ser únicos.")
    if len({x.id for x in plantas}) != len(plantas): errores.append("Los identificadores de plantas deben ser únicos.")
    for etiqueta, elementos, campo in [("oferta", empresas, "oferta"), ("capacidad", plantas, "capacidad")]:
        for x in elementos:
            valor = getattr(x, campo)
            if not isinstance(valor, (int, float)) or not math.isfinite(valor) or valor < 0: errores.append(f"{etiqueta.capitalize()} inválida en {x.id}.")
    ids_e, ids_p = {x.id for x in empresas}, {x.id for x in plantas}
    vistos = set()
    for a in arcos:
        if (a.empresa_id, a.planta_id) in vistos: errores.append(f"Arco duplicado {a.empresa_id}→{a.planta_id}.")
        vistos.add((a.empresa_id, a.planta_id))
        if a.empresa_id not in ids_e or a.planta_id not in ids_p: errores.append(f"Arco con nodo inexistente {a.empresa_id}→{a.planta_id}.")
        if not math.isfinite(a.costo_calculado) or a.costo_calculado < 0: errores.append(f"Costo inválido en {a.empresa_id}→{a.planta_id}.")
        if a.limite is not None and (not math.isfinite(a.limite) or a.limite < 0): errores.append(f"Límite inválido en {a.empresa_id}→{a.planta_id}.")
    if parametros.modo_oferta == "exact":
        for e in empresas:
            if e.oferta > 0 and not any(a.empresa_id == e.id for a in arcos): errores.append(f"La empresa {e.id} no tiene ruta de salida.")
        for p in plantas:
            if p.tipo_demanda in ("exact", "minimum") and p.capacidad > 0 and not any(a.planta_id == p.id for a in arcos): errores.append(f"La planta {p.id} no tiene ruta de entrada.")
        total_o, total_c = sum(x.oferta for x in empresas), sum(x.capacidad for x in plantas if x.tipo_demanda != "minimum")
        if all(x.tipo_demanda == "capacity_max" for x in plantas) and total_o > total_c + 1e-9: errores.append("Oferta total superior a la capacidad total: el escenario es inviable en el modo base.")
    if parametros.unidad != "toneladas" or parametros.periodo != "semana": errores.append("La unidad y el período deben ser toneladas por semana.")
    return errores

def verificar(parametros: ParametrosModelo, asignaciones: list[dict], tolerancia: float = 1e-7) -> dict:
    flujo = {(a["empresa_id"], a["planta_id"]): float(a["cantidad"]) for a in asignaciones}
    errores=[]; maximo=0.0
    for e in parametros.empresas:
        lhs=sum(flujo.get((e.id,p.id),0) for p in parametros.plantas)
        residuo=abs(lhs-e.oferta) if parametros.modo_oferta == "exact" else max(0,lhs-e.oferta)
        maximo=max(maximo,residuo)
        if residuo > tolerancia: errores.append(f"Oferta de {e.id} no cumple: {lhs:.6g}.")
    for p in parametros.plantas:
        lhs=sum(flujo.get((e.id,p.id),0) for e in parametros.empresas)
        residuo = abs(lhs-p.capacidad) if p.tipo_demanda == "exact" else (max(0,lhs-p.capacidad) if p.tipo_demanda == "capacity_max" else max(0,p.capacidad-lhs))
        maximo=max(maximo,residuo)
        if residuo > tolerancia: errores.append(f"Restricción de planta {p.id} no cumple: {lhs:.6g}.")
    autorizados={(a.empresa_id,a.planta_id):a for a in parametros.arcos}
    for clave,cantidad in flujo.items():
        arco=autorizados.get(clave)
        exceso=max(0,cantidad-(arco.limite if arco and arco.limite is not None else float("inf")))
        if cantidad < -tolerancia or arco is None or exceso > tolerancia: errores.append(f"Flujo inválido en {clave}.")
    return {"valida": not errores, "errores": errores, "violacion_maxima": maximo}
