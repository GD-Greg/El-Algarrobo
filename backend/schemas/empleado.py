from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator
)


class PuestoEmpleadoEnum(str, Enum):
    administrador = "administrador"
    recepcionista = "recepcionista"
    jefe_carpinteros = "jefe_carpinteros"
    carpintero = "carpintero"


class TipoCarpinteroEnum(str, Enum):
    armado = "armado"
    labrado = "labrado"


class EmpleadoCreate(BaseModel):
    codigo: str = Field(
        min_length=1,
        max_length=30
    )

    nombre: str = Field(
        min_length=2,
        max_length=50
    )

    apellido: str = Field(
        min_length=2,
        max_length=50
    )

    email: EmailStr

    telefono: str = Field(
        min_length=7,
        max_length=20
    )

    puesto: PuestoEmpleadoEnum

    tipo_carpintero: TipoCarpinteroEnum | None = None

    especialidad_labrado: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    disponible: bool = True
    activo: bool = True

    @model_validator(mode="after")
    def validar_datos_carpintero(self):
        if self.puesto == PuestoEmpleadoEnum.carpintero:
            if self.tipo_carpintero is None:
                raise ValueError(
                    "Un carpintero debe tener un tipo"
                )

            if (
                self.tipo_carpintero
                == TipoCarpinteroEnum.labrado
                and self.especialidad_labrado is None
            ):
                raise ValueError(
                    "Un carpintero de labrado debe indicar "
                    "su especialidad"
                )

            if (
                self.tipo_carpintero
                == TipoCarpinteroEnum.armado
                and self.especialidad_labrado is not None
            ):
                raise ValueError(
                    "Un carpintero de armado no debe tener "
                    "especialidad de labrado"
                )

        else:
            if self.tipo_carpintero is not None:
                raise ValueError(
                    "Solo un carpintero puede tener tipo de carpintero"
                )

            if self.especialidad_labrado is not None:
                raise ValueError(
                    "Solo un carpintero de labrado puede tener "
                    "especialidad"
                )

        return self


class EmpleadoUpdate(BaseModel):
    codigo: str | None = Field(
        default=None,
        min_length=1,
        max_length=30
    )

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

    email: EmailStr | None = None

    telefono: str | None = Field(
        default=None,
        min_length=7,
        max_length=20
    )

    puesto: PuestoEmpleadoEnum | None = None
    tipo_carpintero: TipoCarpinteroEnum | None = None

    especialidad_labrado: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    disponible: bool | None = None
    activo: bool | None = None


class EmpleadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    puesto: PuestoEmpleadoEnum
    tipo_carpintero: TipoCarpinteroEnum | None
    especialidad_labrado: str | None
    disponible: bool
    activo: bool


class EmpleadoBusquedaResponse(BaseModel):
    total: int
    limit: int
    offset: int
    resultados: list[EmpleadoResponse]