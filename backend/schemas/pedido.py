from datetime import date, datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


class PedidoProductoCreate(BaseModel):
    mueble_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    cliente_id: int = Field(gt=0)

    fecha_estimada_entrega: date

    senia: float = Field(
        ge=0
    )

    productos: list[PedidoProductoCreate] = Field(
        min_length=1
    )

    @field_validator("fecha_estimada_entrega")
    @classmethod
    def validar_fecha_estimada(cls, valor: date):
        if valor < date.today():
            raise ValueError(
                "La fecha estimada de entrega no puede estar en el pasado"
            )

        return valor


class PedidoProductoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mueble_id: int
    cantidad: int


class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    fecha_pedido: datetime
    fecha_estimada_entrega: date
    senia: float
    estado: str
    productos: list[PedidoProductoResponse]


class EstadoPedidoEnum(str, Enum):
    pendiente = "pendiente"
    asignado = "asignado"
    en_produccion = "en_produccion"
    terminado = "terminado"
    cliente_avisado = "cliente_avisado"
    retirado_por_cliente = "retirado_por_cliente"
    cancelado = "cancelado"


class PedidoEstadoUpdate(BaseModel):
    estado: EstadoPedidoEnum


class PedidoBusquedaResponse(BaseModel):
    total: int
    limit: int
    offset: int
    resultados: list[PedidoResponse]