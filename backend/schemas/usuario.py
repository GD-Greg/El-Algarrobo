from enum import Enum

from pydantic import BaseModel, Field


class RolEnum(str, Enum):
    administrador = "administrador"
    recepcionista = "recepcionista"
    jefe_carpinteros = "jefe_carpinteros"
    carpintero = "carpintero"


class UsuarioCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    password: str = Field(
        min_length=8,
        max_length=72
    )

    rol: RolEnum


class UsuarioResponse(BaseModel):
    id: int
    username: str
    rol: RolEnum


class UsuarioUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50
    )

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=72
    )

    rol: RolEnum | None = None


class UsuarioLogin(BaseModel):
    username: str
    password: str
    captcha_id: str
    captcha: str


class UsuarioBusquedaResponse(BaseModel):
    total: int
    limit: int
    offset: int
    resultados: list[UsuarioResponse]