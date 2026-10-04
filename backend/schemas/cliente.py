from pydantic import BaseModel, ConfigDict, Field


class ClienteCreate(BaseModel):
    nombre: str = Field(
        min_length=2,
        max_length=50
    )

    apellido: str = Field(
        min_length=2,
        max_length=50
    )

    domicilio: str = Field(
        min_length=5,
        max_length=200
    )

    telefono: str = Field(
        min_length=7,
        max_length=20
    )

    tarjeta_credito: str = Field(
        min_length=2,
        max_length=30
    )

    numero_tarjeta: str = Field(
        min_length=12,
        max_length=25
    )

    numero_cuenta_bancaria: str = Field(
        min_length=5,
        max_length=34
    )

    codigo_banco: str = Field(
        min_length=1,
        max_length=20
    )


class ClienteUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=50
    )

    apellido: str | None = Field(
        default=None,
        min_length=2,
        max_length=50
    )

    domicilio: str | None = Field(
        default=None,
        min_length=5,
        max_length=200
    )

    telefono: str | None = Field(
        default=None,
        min_length=7,
        max_length=20
    )

    tarjeta_credito: str | None = Field(
        default=None,
        min_length=2,
        max_length=30
    )

    numero_tarjeta: str | None = Field(
        default=None,
        min_length=12,
        max_length=25
    )

    numero_cuenta_bancaria: str | None = Field(
        default=None,
        min_length=5,
        max_length=34
    )

    codigo_banco: str | None = Field(
        default=None,
        min_length=1,
        max_length=20
    )


class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    domicilio: str
    telefono: str
    tarjeta_credito: str
    numero_tarjeta: str
    numero_cuenta_bancaria: str
    codigo_banco: str


class ClienteBusquedaResponse(BaseModel):
    total: int
    limit: int
    offset: int
    resultados: list[ClienteResponse]