from pydantic import BaseModel, ConfigDict, Field


class MuebleCreate(BaseModel):
    codigo: str = Field(
        min_length=1,
        max_length=30
    )

    descripcion: str = Field(
        min_length=5,
        max_length=500
    )

    tamanos_sugeridos: str = Field(
        min_length=2,
        max_length=200
    )

    labrado: bool = False

    precio: float = Field(gt=0)


class MuebleUpdate(BaseModel):
    codigo: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

    descripcion: str | None = Field(
        default=None,
        min_length=5,
        max_length=500
    )

    tamanos_sugeridos: str | None = Field(
        default=None,
        min_length=2,
        max_length=200
    )

    labrado: bool | None = None

    precio: float | None = Field(
        default=None,
        gt=0
    )


class MuebleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    descripcion: str
    tamanos_sugeridos: str
    labrado: bool
    precio: float


class MuebleBusquedaResponse(BaseModel):
    total: int
    limit: int
    offset: int
    resultados: list[MuebleResponse]