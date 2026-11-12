"""AG con cromosomas de prioridades; cada individuo se repara a flujo factible."""
from __future__ import annotations
from time import perf_counter
import random
import numpy as np
from dominio.modelos import ParametrosModelo, ResultadoOptimizacion
from optimizacion.validacion import validar, verificar

class AlgoritmoGenetico:
    def resolver(self, parametros: ParametrosModelo, configuracion: dict | None = None) -> ResultadoOptimizacion:
        errores=validar(parametros)
        if errores: return ResultadoOptimizacion("genetico", "INVALID_INPUT", False, None, [], 0, errores)
        cfg={"poblacion":60,"generaciones":150,"cruce":0.8,"mutacion":0.12,"semilla":42,"elitismo":2}; cfg.update(configuracion or {})
        rng=random.Random(cfg["semilla"]); arcos=list(parametros.arcos); n=len(arcos)
        # La reparación admite únicamente el modo principal para que el AG no presente factibilidad falsa.
        if parametros.modo_oferta != "exact" or any(p.tipo_demanda != "capacity_max" for p in parametros.plantas):
            return ResultadoOptimizacion("genetico", "INVALID_INPUT", False, None, [], 0, ["El AG actual admite el modo base: oferta exacta y capacidades máximas."])
        oferta={e.id:e.oferta for e in parametros.empresas}; capacidad={p.id:p.capacidad for p in parametros.plantas}
        def decodificar(gen):
            restante_o=oferta.copy(); restante_c=capacidad.copy(); flujos=[]
            orden=sorted(range(n), key=lambda k: gen[k])
            for k in orden:
                a=arcos[k]; disponible=min(restante_o[a.empresa_id], restante_c[a.planta_id], a.limite if a.limite is not None else float("inf"))
                if disponible>1e-10:
                    flujos.append({"empresa_id":a.empresa_id,"planta_id":a.planta_id,"cantidad":disponible,"costo_unitario":a.costo_calculado}); restante_o[a.empresa_id]-=disponible; restante_c[a.planta_id]-=disponible
            deficit=sum(restante_o.values()); costo=sum(x["cantidad"]*x["costo_unitario"] for x in flujos)
            return costo + deficit*1e12, flujos, deficit
        def aptitud(g): return decodificar(g)[0]
        poblacion=[[rng.random() for _ in range(n)] for _ in range(int(cfg["poblacion"]))]
        inicio=perf_counter(); historia=[]
        for _ in range(int(cfg["generaciones"])):
            poblacion.sort(key=aptitud); historia.append(aptitud(poblacion[0]))
            nueva=poblacion[:int(cfg["elitismo"])]
            while len(nueva)<len(poblacion):
                padres=[min(rng.sample(poblacion, min(3,len(poblacion))),key=aptitud) for _ in range(2)]
                if rng.random()<cfg["cruce"]:
                    corte=rng.randrange(1,n) if n>1 else 0; hijo=padres[0][:corte]+padres[1][corte:]
                else: hijo=padres[0].copy()
                hijo=[rng.random() if rng.random()<cfg["mutacion"] else x for x in hijo]; nueva.append(hijo)
            poblacion=nueva
        mejor=min(poblacion,key=aptitud); costo, flujos, deficit=decodificar(mejor); ver=verificar(parametros,flujos)
        tiempo=(perf_counter()-inicio)*1000
        if deficit>1e-7 or not ver["valida"]: return ResultadoOptimizacion("genetico","INFEASIBLE",False,None,flujos,tiempo,["No se halló una asignación factible."],verificacion=ver,metricas={"convergencia":historia,"semilla":cfg["semilla"]})
        return ResultadoOptimizacion("genetico","FEASIBLE",True,costo,flujos,tiempo,verificacion=ver,metricas={"convergencia":historia,"semilla":cfg["semilla"],"generaciones":cfg["generaciones"]})
