from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Mueble(Base):
    __tablename__ = "muebles"

    id = Column(Integer, primary_key=True, index=True)

    codigo = Column(
        String(30),
        nullable=False,
        unique=True,
        index=True
    )

    descripcion = Column(
        String(500),
        nullable=False
    )

    tamanos_sugeridos = Column(
        String(200),
        nullable=False
    )

    labrado = Column(
        Boolean,
        nullable=False,
        default=False
    )

    precio = Column(
        Float,
        nullable=False
    )

    pedidos = relationship(
        "PedidoProducto",
        back_populates="mueble"
    )

    notas_produccion = relationship(
        "NotaProduccion",
        back_populates="mueble"
    )