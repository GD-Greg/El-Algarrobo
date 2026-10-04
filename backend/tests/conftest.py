import uuid

import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from main import app, captchas
from models.base import Base
from models.usuario import Usuario
from security import (
    create_access_token,
    hash_password
)


SQLALCHEMY_DATABASE_URL = "sqlite://"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)


@event.listens_for(engine, "connect")
def activar_claves_foraneas(
    dbapi_connection,
    connection_record
):
    cursor = dbapi_connection.cursor()

    cursor.execute(
        "PRAGMA foreign_keys=ON"
    )

    cursor.close()


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)

    db_test = TestingSessionLocal()

    try:
        yield db_test
    finally:
        db_test.rollback()
        db_test.close()

        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = (
        override_get_db
    )

    captchas.clear()

    with TestClient(app) as test_client:
        yield test_client

    captchas.clear()
    app.dependency_overrides.clear()


@pytest.fixture
def crear_usuario(db):
    def crear(
        rol="administrador",
        username=None,
        password="Password123"
    ):
        if username is None:
            identificador = uuid.uuid4().hex[:8]

            username = (
                f"{rol}_{identificador}"
            )

        usuario = Usuario(
            username=username,
            password=hash_password(password),
            rol=rol
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        return usuario

    return crear


@pytest.fixture
def headers_para(crear_usuario):
    def generar(
        rol="administrador",
        username=None
    ):
        usuario = crear_usuario(
            rol=rol,
            username=username
        )

        token = create_access_token(
            user_id=usuario.id,
            role=usuario.rol
        )

        return {
            "Authorization":
                f"Bearer {token}"
        }

    return generar


@pytest.fixture
def admin_headers(headers_para):
    return headers_para(
        rol="administrador"
    )


@pytest.fixture
def recepcionista_headers(headers_para):
    return headers_para(
        rol="recepcionista"
    )


@pytest.fixture
def jefe_headers(headers_para):
    return headers_para(
        rol="jefe_carpinteros"
    )


@pytest.fixture
def carpintero_headers(headers_para):
    return headers_para(
        rol="carpintero"
    )