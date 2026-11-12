from dominio.modelos import EmpresaAgropecuaria, PlantaProcesamiento, ArcoCosto, ParametrosModelo
from optimizacion import MetodoExacto, AlgoritmoGenetico

def caso():
 return ParametrosModelo((EmpresaAgropecuaria("E1","E1","X",12),EmpresaAgropecuaria("E2","E2","X",8)),(PlantaProcesamiento("P1","P1","X",15),PlantaProcesamiento("P2","P2","X",10)),(ArcoCosto("E1","P1",4),ArcoCosto("E1","P2",6),ArcoCosto("E2","P1",5),ArcoCosto("E2","P2",2)))
def test_exacto_cp01():
 r=MetodoExacto().resolver(caso());assert r.estado=="OPTIMAL";assert r.objetivo==64;assert r.verificacion["valida"]
def test_inviable_capacidad():
 p=caso(); p=ParametrosModelo(p.empresas,(PlantaProcesamiento("P1","P1","X",5),PlantaProcesamiento("P2","P2","X",10)),p.arcos);assert MetodoExacto().resolver(p).estado=="INVALID_INPUT"
def test_genetico_factible_reproducible():
 a=AlgoritmoGenetico().resolver(caso(),{"semilla":7,"poblacion":40,"generaciones":50});b=AlgoritmoGenetico().resolver(caso(),{"semilla":7,"poblacion":40,"generaciones":50});assert a.factible and a.objetivo==b.objetivo
