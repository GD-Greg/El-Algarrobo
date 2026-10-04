from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(
        Integer,
        primary_key=True,
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

    domicilio = Column(
        String(200),
        nullable=False
    )

    telefono = Column(
        String(20),
        nullable=False
    )

    tarjeta_credito = Column(
        String(30),
        nullable=False
    )

    numero_tarjeta = Column(
        String(25),
        nullable=False
    )

    numero_cuenta_bancaria = Column(
        String(34),
        nullable=False
    )

    codigo_banco = Column(
        String(20),
        nullable=False
    )

    pedidos = relationship(
        "Pedido",
        back_populates="cliente"
    )