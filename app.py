"""Entrada local: streamlit run app.py"""
from __future__ import annotations
import io, json
import pandas as pd
import streamlit as st
from dominio.modelos import EmpresaAgropecuaria, PlantaProcesamiento, ArcoCosto, ParametrosModelo
from servicios import ServicioOptiAgro
from visualizacion.grafos import crear_grafo

st.set_page_config(page_title="OptiAgro-Llanos",layout="wide")
servicio=ServicioOptiAgro()
def semilla():
 # Datos ficticios para demostración: las fuentes no ofrecen una matriz regional validada.
 municipios=["Acacías","Cumaral","Guamal","San Martín","Puerto López","Castilla La Nueva","Cabuyaro","El Dorado","Lejanías","Mapiripán"]
 for i,m in enumerate(municipios,1): servicio.guardar_empresa(EmpresaAgropecuaria(f"E{i}",f"Empresa demostración {i}",m,10+i%4))
 plantas=[("P1","Villavicencio",40),("P2","Restrepo",32),("P3","Granada",30),("P4","Puerto Gaitán",34)]
 for id,m,c in plantas: servicio.guardar_planta(PlantaProcesamiento(id,f"Planta {m}",m,c))
 for i in range(1,11):
  for j in range(1,5): servicio.guardar_costo(ArcoCosto(f"E{i}",f"P{j}",10000+1700*i+900*j,25+i*7+j*5, None))
st.sidebar.title("OptiAgro-Llanos")
pagina=st.sidebar.radio("Módulo",["Panel","Empresas","Plantas","Costos","Red logística","Optimización","Sensibilidad","Reportes"])
p=servicio.parametros_actuales()
if pagina=="Panel":
 st.title("Panel de escenario")
 st.caption("Unidad: toneladas por semana · Datos de demostración marcados como ficticios")
 c1,c2,c3=st.columns(3);c1.metric("Empresas",len(p.empresas));c2.metric("Plantas",len(p.plantas));c3.metric("Oferta / capacidad",f"{sum(x.oferta for x in p.empresas):.1f} / {sum(x.capacidad for x in p.plantas):.1f}")
 if st.button("Cargar datos base de demostración (ficticios)"): semilla();st.rerun()
 st.info("Modelo base: toda la oferta se retira y cada planta tiene una capacidad máxima. La interpretación es configurable en cada planta.")
if pagina=="Empresas":
 st.title("Empresas agropecuarias");st.caption("Oferta en toneladas por semana")
 st.dataframe(pd.DataFrame([x.__dict__ for x in p.empresas]),use_container_width=True)
 with st.form("empresa"):
  a,b,c,d=st.columns(4);id=a.text_input("ID");nombre=b.text_input("Nombre");mun=c.text_input("Municipio");of=d.number_input("Oferta",min_value=0.0);ok=st.form_submit_button("Guardar empresa")
  if ok: servicio.guardar_empresa(EmpresaAgropecuaria(id,nombre,mun,of));st.rerun()
 eid=st.selectbox("Eliminar empresa",[""]+[x.id for x in p.empresas]);
 if eid and st.button("Eliminar seleccionada"):servicio.eliminar_empresa(eid);st.rerun()
if pagina=="Plantas":
 st.title("Plantas de procesamiento");st.caption("Capacidad/demanda en toneladas por semana")
 st.dataframe(pd.DataFrame([x.__dict__ for x in p.plantas]),use_container_width=True)
 with st.form("planta"):
  a,b,c,d,e=st.columns(5);id=a.text_input("ID");nombre=b.text_input("Nombre");mun=c.text_input("Municipio");cap=d.number_input("Capacidad",min_value=0.0);tipo=e.selectbox("Tipo",["capacity_max","exact","minimum"]);ok=st.form_submit_button("Guardar planta")
  if ok: servicio.guardar_planta(PlantaProcesamiento(id,nombre,mun,cap,tipo));st.rerun()
if pagina=="Costos":
 st.title("Matriz de costos");st.caption("Costo unitario COP/tonelada; distancia y tarifa son opcionales.")
 tabla=pd.DataFrame([x.__dict__|{"costo_calculado":x.costo_calculado} for x in p.arcos]);st.dataframe(tabla,use_container_width=True)
 with st.form("arco"):
  a,b,c,d,e=st.columns(5);ei=a.selectbox("Empresa",[x.id for x in p.empresas]);pi=b.selectbox("Planta",[x.id for x in p.plantas]);co=c.number_input("Costo directo COP/t",min_value=0.0);di=d.number_input("Distancia km",min_value=0.0);ta=e.number_input("Tarifa COP/(t·km)",min_value=0.0);ok=st.form_submit_button("Guardar ruta")
  if ok:servicio.guardar_costo(ArcoCosto(ei,pi,co,di if di else None,ta if ta else None));st.rerun()
if pagina=="Red logística":
 st.title("Red logística dirigida");st.plotly_chart(crear_grafo(p,st.session_state.get("ultimo",{}).get("asignaciones")),use_container_width=True)
 st.latex(r"\min Z=\sum_{(i,j)\in E}c_{ij}x_{ij};\quad \sum_jx_{ij}=s_i;\quad \sum_ix_{ij}\le d_j;\quad x_{ij}\ge0")
if pagina=="Optimización":
 st.title("Optimización")
 errores=servicio.validar_escenario(p)
 if errores: st.error("\n".join(errores))
 metodo=st.selectbox("Método",["exacto","genetico"]);a,b,c=st.columns(3);pob=a.number_input("Población AG",10,500,60);gen=b.number_input("Generaciones AG",10,1000,150);sem=c.number_input("Semilla",0,99999,42)
 if st.button("Ejecutar",disabled=bool(errores)):
  with st.spinner("Resolviendo..."): _,r=servicio.ejecutar(p,metodo,{"poblacion":pob,"generaciones":gen,"semilla":sem});st.session_state["ultimo"]=r.como_dict()
 r=st.session_state.get("ultimo")
 if r:
  st.subheader(f"{r['estado']} · {'factible' if r['factible'] else 'no factible'}");st.metric("Costo total",r['objetivo']);st.write(f"Tiempo: {r['duracion_ms']:.2f} ms");st.json(r['verificacion']);st.dataframe(pd.DataFrame(r['asignaciones']),use_container_width=True)
  if r['metricas'].get('convergencia'):st.line_chart(r['metricas']['convergencia'])
if pagina=="Sensibilidad":
 st.title("Análisis de sensibilidad")
 st.caption("Reoptimiza variaciones; los rangos exactos de base no están disponibles en SciPy/HiGHS.")
 tipo=st.selectbox("Parámetro",["oferta","capacidad","costo"]);ids=[x.id for x in p.empresas] if tipo=="oferta" else ([x.id for x in p.plantas] if tipo=="capacidad" else [f"{x.empresa_id}->{x.planta_id}" for x in p.arcos]);iden=st.selectbox("Elemento",ids);vari=st.multiselect("Variaciones (%)",[-20,-10,10,20],default=[-10,10])
 if st.button("Generar escenarios"):
  filas=[]
  for n,por,ex,ag in servicio.generar_sensibilidad(p,[(f"{tipo} {por}%",tipo,iden,por) for por in vari]):filas.append({"Escenario":n,"Variación %":por,"Exacto":ex.objetivo,"AG":ag.objetivo,"Dual":ex.duales})
  st.dataframe(pd.DataFrame(filas),use_container_width=True)
if pagina=="Reportes":
 st.title("Reportes y respaldo")
 ejec=pd.DataFrame(servicio.repo.listar_ejecuciones());st.dataframe(ejec,use_container_width=True)
 if not ejec.empty:st.download_button("Descargar historial CSV",ejec.to_csv(index=False).encode(),"historial_optiagro.csv","text/csv")
 datos=json.dumps({"empresas":[x.__dict__ for x in p.empresas],"plantas":[x.__dict__ for x in p.plantas],"costos":[x.__dict__ for x in p.arcos]},indent=2).encode();st.download_button("Exportar escenario JSON",datos,"escenario_optiagro.json","application/json")
 st.info("Para respaldar completamente, copie el archivo datos/optiagro.sqlite3 con la aplicación cerrada.")
