"""Persistencia SQLite local."""
from __future__ import annotations
import sqlite3, json
from pathlib import Path
from dominio.modelos import *

RUTA_DEFECTO=Path(__file__).resolve().parent.parent / "datos" / "optiagro.sqlite3"
class RepositorioSQLite:
 def __init__(self,ruta: str|Path=RUTA_DEFECTO):
  self.ruta=Path(ruta); self.ruta.parent.mkdir(exist_ok=True); self.inicializar()
 def conexion(self):
  c=sqlite3.connect(self.ruta); c.row_factory=sqlite3.Row; return c
 def inicializar(self):
  with self.conexion() as c: c.executescript('''
   CREATE TABLE IF NOT EXISTS empresas(id TEXT PRIMARY KEY,nombre TEXT NOT NULL,ubicacion TEXT NOT NULL,oferta REAL NOT NULL);
   CREATE TABLE IF NOT EXISTS plantas(id TEXT PRIMARY KEY,nombre TEXT NOT NULL,municipio TEXT NOT NULL,capacidad REAL NOT NULL,tipo_demanda TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS costos(empresa_id TEXT,planta_id TEXT,costo_unitario REAL NOT NULL,distancia_km REAL,tarifa_km_ton REAL,limite REAL,PRIMARY KEY(empresa_id,planta_id));
   CREATE TABLE IF NOT EXISTS escenarios(id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL,fecha TEXT DEFAULT CURRENT_TIMESTAMP,parametros TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS ejecuciones(id INTEGER PRIMARY KEY AUTOINCREMENT,escenario_id INTEGER,metodo TEXT,estado TEXT,duracion_ms REAL,parametros TEXT,resultado TEXT,fecha TEXT DEFAULT CURRENT_TIMESTAMP);
   CREATE TABLE IF NOT EXISTS asignaciones(id INTEGER PRIMARY KEY AUTOINCREMENT,ejecucion_id INTEGER,empresa_id TEXT,planta_id TEXT,cantidad REAL);
  ''')
 def guardar_empresa(self,x):
  with self.conexion() as c:c.execute('INSERT OR REPLACE INTO empresas VALUES(?,?,?,?)',(x.id,x.nombre,x.ubicacion,x.oferta))
 def eliminar_empresa(self,id):
  with self.conexion() as c:c.execute('DELETE FROM empresas WHERE id=?',(id,));c.execute('DELETE FROM costos WHERE empresa_id=?',(id,))
 def guardar_planta(self,x):
  with self.conexion() as c:c.execute('INSERT OR REPLACE INTO plantas VALUES(?,?,?,?,?)',(x.id,x.nombre,x.municipio,x.capacidad,x.tipo_demanda))
 def eliminar_planta(self,id):
  with self.conexion() as c:c.execute('DELETE FROM plantas WHERE id=?',(id,));c.execute('DELETE FROM costos WHERE planta_id=?',(id,))
 def guardar_arco(self,a):
  with self.conexion() as c:c.execute('INSERT OR REPLACE INTO costos VALUES(?,?,?,?,?,?)',(a.empresa_id,a.planta_id,a.costo_unitario,a.distancia_km,a.tarifa_km_ton,a.limite))
 def cargar_parametros(self):
  with self.conexion() as c:
   es=tuple(EmpresaAgropecuaria(**dict(x)) for x in c.execute('SELECT * FROM empresas'))
   ps=tuple(PlantaProcesamiento(**dict(x)) for x in c.execute('SELECT * FROM plantas'))
   ars=tuple(ArcoCosto(**dict(x)) for x in c.execute('SELECT * FROM costos'))
  return ParametrosModelo(es,ps,ars)
 def guardar_escenario(self,nombre,p):
  data=serializar_parametros(p)
  with self.conexion() as c:return c.execute('INSERT INTO escenarios(nombre,parametros) VALUES (?,?)',(nombre,json.dumps(data))).lastrowid
 def listar_escenarios(self):
  with self.conexion() as c:return [dict(x) for x in c.execute('SELECT id,nombre,fecha FROM escenarios ORDER BY id DESC')]
 def obtener_escenario(self,id):
  with self.conexion() as c:r=c.execute('SELECT parametros FROM escenarios WHERE id=?',(id,)).fetchone()
  return deserializar_parametros(json.loads(r['parametros'])) if r else None
 def registrar_ejecucion(self,escenario_id,resultado,parametros):
  with self.conexion() as c:
   eid=c.execute('INSERT INTO ejecuciones(escenario_id,metodo,estado,duracion_ms,parametros,resultado) VALUES(?,?,?,?,?,?)',(escenario_id,resultado.metodo,resultado.estado,resultado.duracion_ms,json.dumps(parametros),json.dumps(resultado.como_dict()))).lastrowid
   c.executemany('INSERT INTO asignaciones(ejecucion_id,empresa_id,planta_id,cantidad) VALUES(?,?,?,?)',[(eid,a['empresa_id'],a['planta_id'],a['cantidad']) for a in resultado.asignaciones]);return eid
 def listar_ejecuciones(self):
  with self.conexion() as c:return [dict(x) for x in c.execute('SELECT id,escenario_id,metodo,estado,duracion_ms,fecha FROM ejecuciones ORDER BY id DESC')]

def serializar_parametros(p): return {"empresas":[asdict(x) for x in p.empresas],"plantas":[asdict(x) for x in p.plantas],"arcos":[asdict(x) for x in p.arcos],"modo_oferta":p.modo_oferta,"unidad":p.unidad,"periodo":p.periodo,"moneda":p.moneda}
def deserializar_parametros(d): return ParametrosModelo(tuple(EmpresaAgropecuaria(**x) for x in d['empresas']),tuple(PlantaProcesamiento(**x) for x in d['plantas']),tuple(ArcoCosto(**x) for x in d['arcos']),d.get('modo_oferta','exact'),d.get('unidad','toneladas'),d.get('periodo','semana'),d.get('moneda','COP'))
