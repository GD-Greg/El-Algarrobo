from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    codigo = Column(
        String(30),
        nullable=False,
        unique=True,
        index=True
    )

    nombre = Column(
        String(50),
        nullable=False
    )

    apellido = Column(
        String(50),
        nullable=False
    )

    email = Column(
        String(100),
        nullable=False,
        unique=True
    )

    telefono = Column(
        String(20),
        nullable=False
    )

    puesto = Column(
        String(30),
        nullable=False
    )

    tipo_carpintero = Column(
        String(20),
        nullable=True
    )

    especialidad_labrado = Column(
        String(100),
        nullable=True
    )

    disponible = Column(
        Boolean,
        nullable=False,
        default=True
    )

    activo = Column(
        Boolean,
        nullable=False,
        default=True
    )

    asignaciones_armado = relationship(
        "AsignacionTrabajo",
        foreign_keys=(
            "AsignacionTrabajo.carpintero_armado_id"
        ),
        back_populates="carpintero_armado"
    )

    asignaciones_labrado = relationship(
        "AsignacionTrabajo",
        foreign_keys=(
            "AsignacionTrabajo.carpintero_labrado_id"
        ),
        back_populates="carpintero_labrado"
    )

    notas_produccion = relationship(
        "NotaProduccion",
        back_populates="carpintero"
    )