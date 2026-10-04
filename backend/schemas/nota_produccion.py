from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotaProduccionCreate(BaseModel):
    asignacion_id: int = Field(gt=0)


class NotaProduccionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asignacion_id: int
    numero_unidad: int
    pedido_id: int
    mueble_id: int
    carpintero_id: int
    fecha_entrega: datetime


class NotaProduccionBusquedaResponse(BaseModel):
    total: int
    limit: int
    offset: int
    resultados: list[NotaProduccionResponse]