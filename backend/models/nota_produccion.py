from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from models.base import Base


class NotaProduccion(Base):
    __tablename__ = "notas_produccion"

    __table_args__ = (
        UniqueConstraint(
            "asignacion_id",
            "numero_unidad",
            name="uq_nota_asignacion_unidad"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    asignacion_id = Column(
        Integer,
        ForeignKey("asignaciones_trabajo.id"),
        nullable=False
    )

    numero_unidad = Column(
        Integer,
        nullable=False
    )

    pedido_id = Column(
        Integer,
        ForeignKey("pedidos.id"),
        nullable=False
    )

    mueble_id = Column(
        Integer,
        ForeignKey("muebles.id"),
        nullable=False
    )

    carpintero_id = Column(
        Integer,
        ForeignKey("empleados.id"),
        nullable=False
    )

    fecha_entrega = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    asignacion = relationship(
        "AsignacionTrabajo",
        back_populates="notas_produccion"
    )

    pedido = relationship(
        "Pedido",
        back_populates="notas_produccion"
    )

    mueble = relationship(
        "Mueble",
        back_populates="notas_produccion"
    )

    carpintero = relationship(
        "Empleado",
        back_populates="notas_produccion"
    )