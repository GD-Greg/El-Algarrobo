from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import relationship

from models.base import Base


class AsignacionTrabajo(Base):
    __tablename__ = "asignaciones_trabajo"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    pedido_producto_id = Column(
        Integer,
        ForeignKey("pedido_producto.id"),
        nullable=False,
        unique=True
    )

    carpintero_armado_id = Column(
        Integer,
        ForeignKey("empleados.id"),
        nullable=False
    )

    carpintero_labrado_id = Column(
        Integer,
        ForeignKey("empleados.id"),
        nullable=True
    )

    fecha_asignacion = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    estado = Column(
        String(30),
        nullable=False,
        default="asignada"
    )

    pedido_producto = relationship(
        "PedidoProducto",
        back_populates="asignacion"
    )

    carpintero_armado = relationship(
        "Empleado",
        foreign_keys=[carpintero_armado_id],
        back_populates="asignaciones_armado"
    )

    carpintero_labrado = relationship(
        "Empleado",
        foreign_keys=[carpintero_labrado_id],
        back_populates="asignaciones_labrado"
    )

    notas_produccion = relationship(
        "NotaProduccion",
        back_populates="asignacion",
        cascade="all, delete-orphan"
    )