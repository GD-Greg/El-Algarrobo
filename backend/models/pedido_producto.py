from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class PedidoProducto(Base):
    __tablename__ = "pedido_producto"

    id = Column(Integer, primary_key=True, index=True)

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

    cantidad = Column(
        Integer,
        nullable=False
    )

    pedido = relationship(
        "Pedido",
        back_populates="productos"
    )

    mueble = relationship(
        "Mueble",
        back_populates="pedidos"
    )

    asignacion = relationship(
        "AsignacionTrabajo",
        back_populates="pedido_producto",
        uselist=False,
        cascade="all, delete-orphan"
    )