from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


class EstadoAsignacionEnum(str, Enum):
    asignada = "asignada"
    en_produccion = "en_produccion"
    terminada = "terminada"


class AsignacionTrabajoCreate(BaseModel):
    pedido_producto_id: int = Field(gt=0)
    carpintero_armado_id: int = Field(gt=0)

    carpintero_labrado_id: int | None = Field(
        default=None,
        gt=0
    )

    @model_validator(mode="after")
    def validar_carpinteros_diferentes(self):
        if (
            self.carpintero_labrado_id is not None
            and self.carpintero_armado_id
            == self.carpintero_labrado_id
        ):
            raise ValueError(
                "El carpintero de armado y el de labrado "
                "deben ser diferentes"
            )

        return self


class AsignacionTrabajoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pedido_producto_id: int
    carpintero_armado_id: int
    carpintero_labrado_id: int | None
    fecha_asignacion: datetime
    estado: EstadoAsignacionEnum


class AsignacionEstadoUpdate(BaseModel):
    estado: EstadoAsignacionEnum


class AsignacionBusquedaResponse(BaseModel):
    total: int
    limit: int
    offset: int
    resultados: list[AsignacionTrabajoResponse]