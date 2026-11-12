"""Casos de uso: única puerta de entrada para la interfaz."""
from __future__ import annotations
from dataclasses import replace
from dominio.modelos import *
from optimizacion import MetodoExacto, AlgoritmoGenetico
from optimizacion.validacion import validar
from persistencia.base_datos import RepositorioSQLite
from .registro import logger

class ServicioOptiAgro:
 def __init__(self,repo=None): self.repo=repo or RepositorioSQLite()
 def parametros_actuales(self): return self.repo.cargar_parametros()
 def validar_escenario(self,p=None): return validar(p or self.parametros_actuales())
 def guardar_empresa(self,x): self.repo.guardar_empresa(x)
 def eliminar_empresa(self,id): self.repo.eliminar_empresa(id)
 def guardar_planta(self,x): self.repo.guardar_planta(x)
 def eliminar_planta(self,id): self.repo.eliminar_planta(id)
 def guardar_costo(self,x): self.repo.guardar_arco(x)
 def crear_escenario(self,nombre,p=None): return self.repo.guardar_escenario(nombre,p or self.parametros_actuales())
 def duplicar_escenario(self,id,nombre): return self.repo.guardar_escenario(nombre,self.repo.obtener_escenario(id))
 def ejecutar(self,p,metodo="exacto",configuracion=None,escenario_id=None):
  try: r=MetodoExacto().resolver(p) if metodo=="exacto" else AlgoritmoGenetico().resolver(p,configuracion)
  except Exception as exc:
   logger.exception("Fallo al ejecutar %s",metodo)
   raise RuntimeError("Ocurrió un error durante la optimización; consulte el registro local.") from exc
  eid=self.repo.registrar_ejecucion(escenario_id,r,configuracion or {}) if escenario_id else None
  return eid,r
 def generar_sensibilidad(self,p,variaciones):
  salida=[]
  for nombre,tipo,identificador,porcentaje in variaciones:
   factor=1+porcentaje/100
   if factor<0: continue
   if tipo=="oferta": nuevo=replace(p,empresas=tuple(replace(x,oferta=x.oferta*factor) if x.id==identificador else x for x in p.empresas))
   elif tipo=="capacidad": nuevo=replace(p,plantas=tuple(replace(x,capacidad=x.capacidad*factor) if x.id==identificador else x for x in p.plantas))
   else: nuevo=replace(p,arcos=tuple(replace(x,costo_unitario=x.costo_unitario*factor) if f"{x.empresa_id}->{x.planta_id}"==identificador else x for x in p.arcos))
   salida.append((nombre,porcentaje,MetodoExacto().resolver(nuevo),AlgoritmoGenetico().resolver(nuevo)))
  return salida
