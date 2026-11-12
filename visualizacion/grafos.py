from __future__ import annotations
import networkx as nx
import plotly.graph_objects as go
from dominio.modelos import ParametrosModelo
def crear_grafo(parametros: ParametrosModelo, asignaciones=None):
 g=nx.DiGraph(); flujos={(x['empresa_id'],x['planta_id']):x['cantidad'] for x in (asignaciones or [])}
 for e in parametros.empresas:g.add_node(e.id,grupo='Empresa',pos=(0,-list(parametros.empresas).index(e)))
 for p in parametros.plantas:g.add_node(p.id,grupo='Planta',pos=(1,-list(parametros.plantas).index(p)))
 for a in parametros.arcos:g.add_edge(a.empresa_id,a.planta_id,costo=a.costo_calculado,flujo=flujos.get((a.empresa_id,a.planta_id),0))
 pos=nx.get_node_attributes(g,'pos'); line=[]
 for u,v in g.edges: line += [pos[u][0],pos[u][1],pos[v][0],pos[v][1],None]
 fig=go.Figure(); fig.add_trace(go.Scatter(x=sum(([pos[u][0],pos[v][0],None] for u,v in g.edges),[]),y=sum(([pos[u][1],pos[v][1],None] for u,v in g.edges),[]),mode='lines',line=dict(color='#9aa0a6')))
 for grupo,color in [('Empresa','#2e7d32'),('Planta','#1565c0')]:
  ns=[n for n,d in g.nodes(data=True) if d['grupo']==grupo];fig.add_trace(go.Scatter(x=[pos[n][0] for n in ns],y=[pos[n][1] for n in ns],mode='markers+text',text=ns,textposition='top center',name=grupo,marker=dict(size=18,color=color)))
 fig.update_layout(showlegend=True,xaxis=dict(visible=False),yaxis=dict(visible=False),margin=dict(l=10,r=10,t=20,b=10));return fig
