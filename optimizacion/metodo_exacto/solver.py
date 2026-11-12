"""Modelo de transporte LP resuelto por HiGHS."""
from __future__ import annotations
from time import perf_counter
import numpy as np
from scipy.optimize import linprog
from dominio.modelos import ParametrosModelo, ResultadoOptimizacion
from optimizacion.validacion import validar, verificar

class MetodoExacto:
    def resolver(self, parametros: ParametrosModelo) -> ResultadoOptimizacion:
        errores=validar(parametros)
        if errores: return ResultadoOptimizacion("exacto", "INVALID_INPUT", False, None, [], 0, errores)
        arcos=list(parametros.arcos); q=len(arcos); empresas=list(parametros.empresas); plantas=list(parametros.plantas)
        c=np.array([a.costo_calculado for a in arcos]); eq=[]; beq=[]; ub=[]; bub=[]
        for e in empresas:
            fila=[1.0 if a.empresa_id==e.id else 0.0 for a in arcos]
            if parametros.modo_oferta == "exact": eq.append(fila); beq.append(e.oferta)
            else: ub.append(fila); bub.append(e.oferta)
        for p in plantas:
            fila=[1.0 if a.planta_id==p.id else 0.0 for a in arcos]
            if p.tipo_demanda == "exact": eq.append(fila); beq.append(p.capacidad)
            elif p.tipo_demanda == "capacity_max": ub.append(fila); bub.append(p.capacidad)
            else: ub.append([-v for v in fila]); bub.append(-p.capacidad)
        limites=[(0, a.limite) for a in arcos]
        inicio=perf_counter()
        try:
            r=linprog(c, A_ub=np.array(ub) if ub else None, b_ub=np.array(bub) if bub else None, A_eq=np.array(eq) if eq else None, b_eq=np.array(beq) if beq else None, bounds=limites, method="highs")
        except Exception as exc:
            return ResultadoOptimizacion("exacto", "ERROR", False, None, [], (perf_counter()-inicio)*1000, [str(exc)])
        tiempo=(perf_counter()-inicio)*1000
        estados={2:"INFEASIBLE",3:"UNBOUNDED",1:"LIMIT_REACHED",4:"NUMERICAL_ERROR"}
        if r.status != 0:
            return ResultadoOptimizacion("exacto", estados.get(r.status,"ERROR"), False, None, [], tiempo, [r.message])
        asignaciones=[{"empresa_id":a.empresa_id,"planta_id":a.planta_id,"cantidad":float(r.x[k]),"costo_unitario":a.costo_calculado} for k,a in enumerate(arcos) if r.x[k] > 1e-9]
        comprobacion=verificar(parametros, asignaciones)
        if not comprobacion["valida"]: return ResultadoOptimizacion("exacto", "NUMERICAL_ERROR", False, None, asignaciones, tiempo, comprobacion["errores"], verificacion=comprobacion)
        duales={}
        if eq and hasattr(r, "eqlin"):
            for i,e in enumerate([e for e in empresas if parametros.modo_oferta == "exact"]): duales[f"oferta:{e.id}"]=float(r.eqlin.marginals[i])
        if ub and hasattr(r, "ineqlin"):
            indice=0
            if parametros.modo_oferta == "maximum": indice+=len(empresas)
            for p in plantas:
                if p.tipo_demanda != "exact": duales[f"planta:{p.id}"]=float(r.ineqlin.marginals[indice]); indice+=1
        return ResultadoOptimizacion("exacto", "OPTIMAL", True, float(r.fun), asignaciones, tiempo, [r.message], duales, comprobacion, {"solver":"HiGHS", "optimo_certificado":True})
