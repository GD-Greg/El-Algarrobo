from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import relationship

from models.base import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id"),
        nullable=False
    )

    fecha_pedido = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    fecha_estimada_entrega = Column(
        Date,
        nullable=False
    )

    senia = Column(
        Float,
        nullable=False,
        default=0
    )

    estado = Column(
        String(30),
        nullable=False,
        default="pendiente"
    )

    cliente = relationship(
        "Cliente",
        back_populates="pedidos"
    )

    productos = relationship(
        "PedidoProducto",
        back_populates="pedido"
    )

    notas_produccion = relationship(
        "NotaProduccion",
        back_populates="pedido"
    )