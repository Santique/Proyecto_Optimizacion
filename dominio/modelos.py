"""Entidades y contratos independientes de interfaz y persistencia."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal, Any

TipoDemanda = Literal["capacity_max", "exact", "minimum"]

@dataclass(frozen=True)
class EmpresaAgropecuaria:
    id: str; nombre: str; ubicacion: str; oferta: float
    def actualizar_oferta(self, oferta: float) -> "EmpresaAgropecuaria":
        return EmpresaAgropecuaria(self.id, self.nombre, self.ubicacion, oferta)

@dataclass(frozen=True)
class PlantaProcesamiento:
    id: str; nombre: str; municipio: str; capacidad: float; tipo_demanda: TipoDemanda = "capacity_max"
    def actualizar_capacidad(self, capacidad: float) -> "PlantaProcesamiento":
        return PlantaProcesamiento(self.id, self.nombre, self.municipio, capacidad, self.tipo_demanda)

@dataclass(frozen=True)
class ArcoCosto:
    empresa_id: str; planta_id: str; costo_unitario: float
    distancia_km: float | None = None; tarifa_km_ton: float | None = None; limite: float | None = None
    @property
    def costo_calculado(self) -> float:
        return self.costo_unitario if self.distancia_km is None or self.tarifa_km_ton is None else self.distancia_km * self.tarifa_km_ton

@dataclass(frozen=True)
class ParametrosModelo:
    empresas: tuple[EmpresaAgropecuaria, ...]; plantas: tuple[PlantaProcesamiento, ...]
    arcos: tuple[ArcoCosto, ...]; modo_oferta: Literal["exact", "maximum"] = "exact"
    unidad: str = "toneladas"; periodo: str = "semana"; moneda: str = "COP"

@dataclass
class ResultadoOptimizacion:
    metodo: str; estado: str; factible: bool; objetivo: float | None; asignaciones: list[dict[str, Any]]
    duracion_ms: float; mensajes: list[str] = field(default_factory=list); duales: dict[str, float] = field(default_factory=dict)
    verificacion: dict[str, Any] = field(default_factory=dict); metricas: dict[str, Any] = field(default_factory=dict)
    def como_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass
class MatrizCostos:
    costos: dict[tuple[str, str], float]
    def actualizar_costo(self, empresa_id: str, planta_id: str, costo: float) -> None: self.costos[(empresa_id, planta_id)] = costo
    def obtener_costo(self, empresa_id: str, planta_id: str) -> float | None: return self.costos.get((empresa_id, planta_id))

@dataclass
class RedLogistica:
    empresas: list[EmpresaAgropecuaria]; plantas: list[PlantaProcesamiento]; matriz_costos: MatrizCostos
    def construir_red(self) -> list[tuple[str, str, float]]:
        return [(i, j, c) for (i, j), c in self.matriz_costos.costos.items()]
