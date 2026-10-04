import pytest

from models.usuario import Usuario
from security import verify_password


def obtener_captcha(client):
    response = client.get("/captcha")

    assert response.status_code == 200

    return response.json()


def iniciar_sesion(
    client,
    username,
    password
):
    captcha = obtener_captcha(client)

    return client.post(
        "/login",
        json={
            "username": username,
            "password": password,
            "captcha_id": (
                captcha["captcha_id"]
            ),
            "captcha": captcha["captcha"]
        }
    )


def test_api_funciona(client):
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "mensaje":
            "El Algarrobo API funcionando"
    }


def test_generar_captcha(client):
    response = client.get("/captcha")

    assert response.status_code == 200

    data = response.json()

    assert "captcha_id" in data
    assert "captcha" in data
    assert len(data["captcha"]) == 5


def test_login_correcto(
    client,
    crear_usuario
):
    crear_usuario(
        rol="carpintero",
        username="carpintero_login",
        password="Password123"
    )

    response = iniciar_sesion(
        client,
        "carpintero_login",
        "Password123"
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_captcha_es_de_un_solo_uso(
    client,
    crear_usuario
):
    crear_usuario(
        rol="recepcionista",
        username="captcha_un_uso",
        password="Password123"
    )

    captcha = obtener_captcha(client)

    datos_login = {
        "username": "captcha_un_uso",
        "password": "Password123",
        "captcha_id":
            captcha["captcha_id"],
        "captcha": captcha["captcha"]
    }

    primera_respuesta = client.post(
        "/login",
        json=datos_login
    )

    segunda_respuesta = client.post(
        "/login",
        json=datos_login
    )

    assert primera_respuesta.status_code == 200
    assert segunda_respuesta.status_code == 400


def test_login_password_incorrecta(
    client,
    crear_usuario
):
    crear_usuario(
        rol="recepcionista",
        username="password_incorrecta",
        password="Password123"
    )

    response = iniciar_sesion(
        client,
        "password_incorrecta",
        "PasswordEquivocada"
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Credenciales incorrectas"
    )


def test_staff_requiere_token(client):
    response = client.get("/staff")

    assert response.status_code in [
        401,
        403
    ]


def test_staff_acepta_los_cuatro_roles(
    client,
    headers_para
):
    roles = [
        "administrador",
        "recepcionista",
        "jefe_carpinteros",
        "carpintero"
    ]

    for rol in roles:
        headers = headers_para(rol=rol)

        response = client.get(
            "/staff",
            headers=headers
        )

        assert response.status_code == 200
        assert response.json()["rol"] == rol


def test_panel_admin_acepta_administrador(
    client,
    admin_headers
):
    response = client.get(
        "/admin",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["rol"] == (
        "administrador"
    )


def test_panel_admin_rechaza_recepcionista(
    client,
    recepcionista_headers
):
    response = client.get(
        "/admin",
        headers=recepcionista_headers
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "rol",
    [
        "administrador",
        "recepcionista",
        "jefe_carpinteros",
        "carpintero"
    ]
)
def test_administrador_crea_usuarios(
    client,
    admin_headers,
    rol
):
    response = client.post(
        "/usuarios",
        headers=admin_headers,
        json={
            "username": f"nuevo_{rol}",
            "password": "Password123",
            "rol": rol
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == (
        f"nuevo_{rol}"
    )

    assert data["rol"] == rol
    assert "password" not in data


def test_password_se_guarda_hasheada(
    client,
    db,
    admin_headers
):
    response = client.post(
        "/usuarios",
        headers=admin_headers,
        json={
            "username": "usuario_hash",
            "password": "Password123",
            "rol": "carpintero"
        }
    )

    assert response.status_code == 200

    usuario = db.query(Usuario).filter(
        Usuario.username == "usuario_hash"
    ).first()

    assert usuario is not None

    assert usuario.password != (
        "Password123"
    )

    assert verify_password(
        "Password123",
        usuario.password
    )


def test_recepcionista_no_crea_usuarios(
    client,
    recepcionista_headers
):
    response = client.post(
        "/usuarios",
        headers=recepcionista_headers,
        json={
            "username": "sin_permiso",
            "password": "Password123",
            "rol": "carpintero"
        }
    )

    assert response.status_code == 403


def test_crear_usuario_password_corta(
    client,
    admin_headers
):
    response = client.post(
        "/usuarios",
        headers=admin_headers,
        json={
            "username": "password_corta",
            "password": "123",
            "rol": "carpintero"
        }
    )

    assert response.status_code == 422


def test_crear_usuario_rol_invalido(
    client,
    admin_headers
):
    response = client.post(
        "/usuarios",
        headers=admin_headers,
        json={
            "username": "rol_invalido",
            "password": "Password123",
            "rol": "empleado"
        }
    )

    assert response.status_code == 422


def test_no_crear_username_duplicado(
    client,
    admin_headers,
    crear_usuario
):
    crear_usuario(
        rol="carpintero",
        username="usuario_repetido"
    )

    response = client.post(
        "/usuarios",
        headers=admin_headers,
        json={
            "username": "usuario_repetido",
            "password": "Password123",
            "rol": "recepcionista"
        }
    )

    assert response.status_code == 409


def test_obtener_usuarios(
    client,
    admin_headers,
    crear_usuario
):
    crear_usuario(
        rol="recepcionista",
        username="recepcionista_lista"
    )

    response = client.get(
        "/usuarios",
        headers=admin_headers
    )

    assert response.status_code == 200

    usernames = [
        usuario["username"]
        for usuario in response.json()
    ]

    assert "recepcionista_lista" in usernames


def test_buscar_usuario_por_rol(
    client,
    admin_headers,
    crear_usuario
):
    crear_usuario(
        rol="carpintero",
        username="carpintero_busqueda"
    )

    crear_usuario(
        rol="recepcionista",
        username="recepcion_busqueda"
    )

    response = client.get(
        "/usuarios/buscar",
        headers=admin_headers,
        params={
            "rol": "carpintero"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    assert (
        data["resultados"][0]["rol"]
        == "carpintero"
    )


def test_modificar_usuario(
    client,
    admin_headers,
    crear_usuario
):
    usuario = crear_usuario(
        rol="carpintero",
        username="usuario_original"
    )

    response = client.put(
        f"/usuarios/{usuario.id}",
        headers=admin_headers,
        json={
            "username": "usuario_modificado",
            "rol": "jefe_carpinteros"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == (
        "usuario_modificado"
    )

    assert data["rol"] == (
        "jefe_carpinteros"
    )


def test_eliminar_usuario(
    client,
    db,
    admin_headers,
    crear_usuario
):
    usuario = crear_usuario(
        rol="carpintero",
        username="usuario_eliminar"
    )

    usuario_id = usuario.id

    response = client.delete(
        f"/usuarios/{usuario_id}",
        headers=admin_headers
    )

    assert response.status_code == 200

    usuario_eliminado = db.query(
        Usuario
    ).filter(
        Usuario.id == usuario_id
    ).first()

    assert usuario_eliminado is None


# =================================================
# MUEBLES
# =================================================

def datos_mueble(
    codigo="MES-001",
    precio=275000
):
    return {
        "codigo": codigo,
        "descripcion":
            "Mesa de algarrobo artesanal",
        "tamanos_sugeridos":
            "120 x 80 cm",
        "labrado": True,
        "precio": precio
    }


def crear_mueble_api(
    client,
    admin_headers,
    codigo="MES-001"
):
    response = client.post(
        "/muebles",
        headers=admin_headers,
        json=datos_mueble(codigo=codigo)
    )

    assert response.status_code == 200

    return response.json()


def test_administrador_crea_mueble(
    client,
    admin_headers
):
    response = client.post(
        "/muebles",
        headers=admin_headers,
        json=datos_mueble(
            codigo="  mes-001  "
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["codigo"] == "MES-001"
    assert data["labrado"] is True
    assert data["precio"] == 275000


def test_todos_los_roles_consultan_muebles(
    client,
    admin_headers,
    headers_para
):
    crear_mueble_api(
        client,
        admin_headers
    )

    roles = [
        "administrador",
        "recepcionista",
        "jefe_carpinteros",
        "carpintero"
    ]

    for rol in roles:
        headers = headers_para(rol=rol)

        response = client.get(
            "/muebles",
            headers=headers
        )

        assert response.status_code == 200
        assert len(response.json()) == 1


def test_recepcionista_no_crea_mueble(
    client,
    recepcionista_headers
):
    response = client.post(
        "/muebles",
        headers=recepcionista_headers,
        json=datos_mueble()
    )

    assert response.status_code == 403


def test_no_crear_codigo_mueble_duplicado(
    client,
    admin_headers
):
    crear_mueble_api(
        client,
        admin_headers,
        codigo="MES-001"
    )

    response = client.post(
        "/muebles",
        headers=admin_headers,
        json=datos_mueble(
            codigo="MES-001"
        )
    )

    assert response.status_code == 409


def test_no_crear_mueble_precio_negativo(
    client,
    admin_headers
):
    response = client.post(
        "/muebles",
        headers=admin_headers,
        json=datos_mueble(
            precio=-100
        )
    )

    assert response.status_code == 422


def test_administrador_modifica_mueble(
    client,
    admin_headers
):
    mueble = crear_mueble_api(
        client,
        admin_headers
    )

    response = client.put(
        f"/muebles/{mueble['id']}",
        headers=admin_headers,
        json={
            "precio": 300000,
            "labrado": False
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["precio"] == 300000
    assert data["labrado"] is False


@pytest.mark.parametrize(
    "rol",
    [
        "recepcionista",
        "jefe_carpinteros",
        "carpintero"
    ]
)
def test_no_administrador_no_modifica_mueble(
    client,
    admin_headers,
    headers_para,
    rol
):
    mueble = crear_mueble_api(
        client,
        admin_headers
    )

    headers = headers_para(rol=rol)

    response = client.put(
        f"/muebles/{mueble['id']}",
        headers=headers,
        json={
            "precio": 300000
        }
    )

    assert response.status_code == 403


def test_buscar_mueble_por_codigo(
    client,
    admin_headers
):
    crear_mueble_api(
        client,
        admin_headers,
        codigo="MES-001"
    )

    crear_mueble_api(
        client,
        admin_headers,
        codigo="SIL-001"
    )

    response = client.get(
        "/muebles/buscar",
        headers=admin_headers,
        params={
            "codigo": "MES"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    assert (
        data["resultados"][0]["codigo"]
        == "MES-001"
    )


def test_buscar_mueble_sin_criterio(
    client,
    admin_headers
):
    response = client.get(
        "/muebles/buscar",
        headers=admin_headers
    )

    assert response.status_code == 400


def test_administrador_elimina_mueble(
    client,
    db,
    admin_headers
):
    from models.mueble import Mueble

    mueble = crear_mueble_api(
        client,
        admin_headers
    )

    response = client.delete(
        f"/muebles/{mueble['id']}",
        headers=admin_headers
    )

    assert response.status_code == 200

    eliminado = db.query(Mueble).filter(
        Mueble.id == mueble["id"]
    ).first()

    assert eliminado is None


# =================================================
# CLIENTES
# =================================================

def datos_cliente(
    nombre="Ana",
    apellido="Pérez",
    telefono="1123456789"
):
    return {
        "nombre": nombre,
        "apellido": apellido,
        "domicilio":
            "Avenida Siempre Viva 123",
        "telefono": telefono,
        "tarjeta_credito": "Visa",
        "numero_tarjeta":
            "4111111111111111",
        "numero_cuenta_bancaria":
            "1234567890123456789012",
        "codigo_banco": "BANCO-01"
    }


def crear_cliente_api(
    client,
    headers,
    nombre="Ana",
    apellido="Pérez",
    telefono="1123456789"
):
    response = client.post(
        "/clientes",
        headers=headers,
        json=datos_cliente(
            nombre=nombre,
            apellido=apellido,
            telefono=telefono
        )
    )

    assert response.status_code == 200

    return response.json()


def test_administrador_crea_cliente(
    client,
    admin_headers
):
    cliente = crear_cliente_api(
        client,
        admin_headers
    )

    assert cliente["nombre"] == "Ana"
    assert cliente["apellido"] == "Pérez"
    assert cliente["tarjeta_credito"] == "Visa"


def test_recepcionista_crea_cliente(
    client,
    recepcionista_headers
):
    cliente = crear_cliente_api(
        client,
        recepcionista_headers
    )

    assert cliente["nombre"] == "Ana"


@pytest.mark.parametrize(
    "rol",
    [
        "jefe_carpinteros",
        "carpintero"
    ]
)
def test_produccion_no_crea_clientes(
    client,
    headers_para,
    rol
):
    headers = headers_para(rol=rol)

    response = client.post(
        "/clientes",
        headers=headers,
        json=datos_cliente()
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "rol",
    [
        "administrador",
        "recepcionista"
    ]
)
def test_administracion_consulta_clientes(
    client,
    admin_headers,
    headers_para,
    rol
):
    crear_cliente_api(
        client,
        admin_headers
    )

    headers = headers_para(rol=rol)

    response = client.get(
        "/clientes",
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_jefe_no_consulta_clientes(
    client,
    jefe_headers
):
    response = client.get(
        "/clientes",
        headers=jefe_headers
    )

    assert response.status_code == 403


def test_recepcionista_modifica_cliente(
    client,
    admin_headers,
    recepcionista_headers
):
    cliente = crear_cliente_api(
        client,
        admin_headers
    )

    response = client.put(
        f"/clientes/{cliente['id']}",
        headers=recepcionista_headers,
        json={
            "domicilio":
                "Nueva dirección 456",
            "telefono": "1198765432"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["domicilio"] == (
        "Nueva dirección 456"
    )

    assert data["telefono"] == "1198765432"


def test_administrador_elimina_cliente(
    client,
    db,
    admin_headers
):
    from models.cliente import Cliente

    cliente = crear_cliente_api(
        client,
        admin_headers
    )

    response = client.delete(
        f"/clientes/{cliente['id']}",
        headers=admin_headers
    )

    assert response.status_code == 200

    eliminado = db.query(Cliente).filter(
        Cliente.id == cliente["id"]
    ).first()

    assert eliminado is None


def test_recepcionista_no_elimina_cliente(
    client,
    admin_headers,
    recepcionista_headers
):
    cliente = crear_cliente_api(
        client,
        admin_headers
    )

    response = client.delete(
        f"/clientes/{cliente['id']}",
        headers=recepcionista_headers
    )

    assert response.status_code == 403


def test_buscar_cliente_por_apellido(
    client,
    admin_headers
):
    crear_cliente_api(
        client,
        admin_headers,
        nombre="Ana",
        apellido="Pérez"
    )

    crear_cliente_api(
        client,
        admin_headers,
        nombre="Luis",
        apellido="Gómez",
        telefono="1111111111"
    )

    response = client.get(
        "/clientes/buscar",
        headers=admin_headers,
        params={
            "apellido": "Pér"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    assert (
        data["resultados"][0]["apellido"]
        == "Pérez"
    )


def test_buscar_cliente_por_telefono(
    client,
    recepcionista_headers
):
    crear_cliente_api(
        client,
        recepcionista_headers,
        telefono="1123456789"
    )

    response = client.get(
        "/clientes/buscar",
        headers=recepcionista_headers,
        params={
            "telefono": "2345"
        }
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_cliente_nombre_demasiado_corto(
    client,
    admin_headers
):
    response = client.post(
        "/clientes",
        headers=admin_headers,
        json=datos_cliente(
            nombre="A"
        )
    )

    assert response.status_code == 422


# =================================================
# EMPLEADOS
# =================================================

def datos_empleado(
    codigo="CAR-A01",
    email="carpintero@example.com",
    puesto="carpintero",
    tipo_carpintero="armado",
    especialidad_labrado=None
):
    return {
        "codigo": codigo,
        "nombre": "Juan",
        "apellido": "Torres",
        "email": email,
        "telefono": "1123456789",
        "puesto": puesto,
        "tipo_carpintero":
            tipo_carpintero,
        "especialidad_labrado":
            especialidad_labrado,
        "disponible": True,
        "activo": True
    }


def crear_empleado_api(
    client,
    admin_headers,
    codigo="CAR-A01",
    email="carpintero@example.com",
    tipo_carpintero="armado",
    especialidad_labrado=None
):
    response = client.post(
        "/empleados",
        headers=admin_headers,
        json=datos_empleado(
            codigo=codigo,
            email=email,
            tipo_carpintero=(
                tipo_carpintero
            ),
            especialidad_labrado=(
                especialidad_labrado
            )
        )
    )

    assert response.status_code == 200

    return response.json()


def test_administrador_crea_carpintero_armado(
    client,
    admin_headers
):
    empleado = crear_empleado_api(
        client,
        admin_headers
    )

    assert empleado["codigo"] == "CAR-A01"

    assert empleado["puesto"] == (
        "carpintero"
    )

    assert empleado["tipo_carpintero"] == (
        "armado"
    )

    assert empleado[
        "especialidad_labrado"
    ] is None

    assert empleado["disponible"] is True
    assert empleado["activo"] is True


def test_administrador_crea_carpintero_labrado(
    client,
    admin_headers
):
    empleado = crear_empleado_api(
        client,
        admin_headers,
        codigo="CAR-L01",
        email="labrado@example.com",
        tipo_carpintero="labrado",
        especialidad_labrado=(
            "Tallado artesanal"
        )
    )

    assert empleado["tipo_carpintero"] == (
        "labrado"
    )

    assert empleado[
        "especialidad_labrado"
    ] == "Tallado artesanal"


def test_carpintero_requiere_tipo(
    client,
    admin_headers
):
    response = client.post(
        "/empleados",
        headers=admin_headers,
        json=datos_empleado(
            tipo_carpintero=None
        )
    )

    assert response.status_code == 422


def test_carpintero_labrado_requiere_especialidad(
    client,
    admin_headers
):
    response = client.post(
        "/empleados",
        headers=admin_headers,
        json=datos_empleado(
            tipo_carpintero="labrado",
            especialidad_labrado=None
        )
    )

    assert response.status_code == 422


def test_no_carpintero_no_puede_tener_tipo(
    client,
    admin_headers
):
    response = client.post(
        "/empleados",
        headers=admin_headers,
        json=datos_empleado(
            puesto="recepcionista",
            tipo_carpintero="armado"
        )
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "rol",
    [
        "administrador",
        "jefe_carpinteros"
    ]
)
def test_administrador_y_jefe_consultan_empleados(
    client,
    admin_headers,
    headers_para,
    rol
):
    crear_empleado_api(
        client,
        admin_headers
    )

    headers = headers_para(rol=rol)

    response = client.get(
        "/empleados",
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recepcionista_no_consulta_empleados(
    client,
    recepcionista_headers
):
    response = client.get(
        "/empleados",
        headers=recepcionista_headers
    )

    assert response.status_code == 403


def test_jefe_no_modifica_empleados(
    client,
    admin_headers,
    jefe_headers
):
    empleado = crear_empleado_api(
        client,
        admin_headers
    )

    response = client.put(
        f"/empleados/{empleado['id']}",
        headers=jefe_headers,
        json={
            "telefono": "1199999999"
        }
    )

    assert response.status_code == 403


def test_administrador_modifica_empleado(
    client,
    admin_headers
):
    empleado = crear_empleado_api(
        client,
        admin_headers
    )

    response = client.put(
        f"/empleados/{empleado['id']}",
        headers=admin_headers,
        json={
            "nombre": "Juan Carlos",
            "telefono": "1199999999",
            "activo": False
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["nombre"] == "Juan Carlos"
    assert data["telefono"] == "1199999999"
    assert data["activo"] is False


def test_buscar_carpintero_disponible_de_armado(
    client,
    admin_headers,
    jefe_headers
):
    crear_empleado_api(
        client,
        admin_headers,
        codigo="CAR-A01",
        email="armado@example.com",
        tipo_carpintero="armado"
    )

    crear_empleado_api(
        client,
        admin_headers,
        codigo="CAR-L01",
        email="labrado@example.com",
        tipo_carpintero="labrado",
        especialidad_labrado=(
            "Tallado artesanal"
        )
    )

    response = client.get(
        "/empleados/buscar",
        headers=jefe_headers,
        params={
            "puesto": "carpintero",
            "tipo_carpintero": "armado",
            "disponible": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    assert (
        data["resultados"][0]["codigo"]
        == "CAR-A01"
    )


def test_no_crear_codigo_empleado_duplicado(
    client,
    admin_headers
):
    crear_empleado_api(
        client,
        admin_headers,
        codigo="CAR-A01",
        email="primero@example.com"
    )

    response = client.post(
        "/empleados",
        headers=admin_headers,
        json=datos_empleado(
            codigo="car-a01",
            email="segundo@example.com"
        )
    )

    assert response.status_code == 409


def test_administrador_elimina_empleado(
    client,
    db,
    admin_headers
):
    from models.empleado import Empleado

    empleado = crear_empleado_api(
        client,
        admin_headers
    )

    response = client.delete(
        f"/empleados/{empleado['id']}",
        headers=admin_headers
    )

    assert response.status_code == 200

    eliminado = db.query(Empleado).filter(
        Empleado.id == empleado["id"]
    ).first()

    assert eliminado is None


# =================================================
# PEDIDOS
# =================================================

from datetime import date, timedelta


def datos_pedido(
    cliente_id,
    mueble_id,
    cantidad=1,
    senia=50000,
    fecha_entrega=None
):
    if fecha_entrega is None:
        fecha_entrega = (
            date.today() +
            timedelta(days=7)
        )

    return {
        "cliente_id": cliente_id,
        "fecha_estimada_entrega":
            fecha_entrega.isoformat(),
        "senia": senia,
        "productos": [
            {
                "mueble_id": mueble_id,
                "cantidad": cantidad
            }
        ]
    }


def preparar_datos_pedido(
    client,
    admin_headers,
    codigo_mueble="MES-001"
):
    cliente = crear_cliente_api(
        client,
        admin_headers
    )

    mueble = crear_mueble_api(
        client,
        admin_headers,
        codigo=codigo_mueble
    )

    return cliente, mueble


def crear_pedido_api(
    client,
    headers,
    cliente_id,
    mueble_id,
    cantidad=1,
    senia=50000
):
    response = client.post(
        "/pedidos",
        headers=headers,
        json=datos_pedido(
            cliente_id=cliente_id,
            mueble_id=mueble_id,
            cantidad=cantidad,
            senia=senia
        )
    )

    assert response.status_code == 200

    return response.json()


def test_administrador_crea_pedido(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"],
        cantidad=2,
        senia=50000
    )

    assert pedido["cliente_id"] == (
        cliente["id"]
    )

    assert pedido["estado"] == "pendiente"
    assert pedido["senia"] == 50000

    assert (
        pedido["productos"][0]["mueble_id"]
        == mueble["id"]
    )

    assert (
        pedido["productos"][0]["cantidad"]
        == 2
    )


def test_recepcionista_crea_pedido(
    client,
    admin_headers,
    recepcionista_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    pedido = crear_pedido_api(
        client,
        recepcionista_headers,
        cliente["id"],
        mueble["id"]
    )

    assert pedido["estado"] == "pendiente"


@pytest.mark.parametrize(
    "rol",
    [
        "jefe_carpinteros",
        "carpintero"
    ]
)
def test_produccion_no_crea_pedidos(
    client,
    admin_headers,
    headers_para,
    rol
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    headers = headers_para(rol=rol)

    response = client.post(
        "/pedidos",
        headers=headers,
        json=datos_pedido(
            cliente["id"],
            mueble["id"]
        )
    )

    assert response.status_code == 403


def test_todos_los_roles_consultan_pedidos(
    client,
    admin_headers,
    headers_para
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    roles = [
        "administrador",
        "recepcionista",
        "jefe_carpinteros",
        "carpintero"
    ]

    for rol in roles:
        headers = headers_para(rol=rol)

        response = client.get(
            "/pedidos",
            headers=headers
        )

        assert response.status_code == 200
        assert len(response.json()) == 1


def test_pedido_rechaza_fecha_pasada(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    fecha_pasada = (
        date.today() -
        timedelta(days=1)
    )

    response = client.post(
        "/pedidos",
        headers=admin_headers,
        json=datos_pedido(
            cliente["id"],
            mueble["id"],
            fecha_entrega=fecha_pasada
        )
    )

    assert response.status_code == 422


def test_senia_no_supera_total_pedido(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    response = client.post(
        "/pedidos",
        headers=admin_headers,
        json=datos_pedido(
            cliente["id"],
            mueble["id"],
            cantidad=1,
            senia=300000
        )
    )

    assert response.status_code == 400


def test_pedido_rechaza_mueble_repetido(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    datos = datos_pedido(
        cliente["id"],
        mueble["id"]
    )

    datos["productos"].append({
        "mueble_id": mueble["id"],
        "cantidad": 2
    })

    response = client.post(
        "/pedidos",
        headers=admin_headers,
        json=datos
    )

    assert response.status_code == 400


def test_pedido_rechaza_cliente_inexistente(
    client,
    admin_headers
):
    mueble = crear_mueble_api(
        client,
        admin_headers
    )

    response = client.post(
        "/pedidos",
        headers=admin_headers,
        json=datos_pedido(
            cliente_id=999999,
            mueble_id=mueble["id"]
        )
    )

    assert response.status_code == 404


def test_buscar_pedido_por_numero_y_estado(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    response = client.get(
        "/pedidos/buscar",
        headers=admin_headers,
        params={
            "numero_pedido": pedido["id"],
            "estado": "pendiente"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    assert (
        data["resultados"][0]["id"]
        == pedido["id"]
    )


def test_buscar_mueble_por_numero_pedido(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers,
        codigo_mueble="MES-777"
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    response = client.get(
        "/muebles/buscar",
        headers=admin_headers,
        params={
            "numero_pedido": pedido["id"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    assert (
        data["resultados"][0]["codigo"]
        == "MES-777"
    )


def test_recepcionista_cancela_pedido_pendiente(
    client,
    admin_headers,
    recepcionista_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    response = client.put(
        f"/pedidos/{pedido['id']}/estado",
        headers=recepcionista_headers,
        json={
            "estado": "cancelado"
        }
    )

    assert response.status_code == 200
    assert response.json()["estado"] == (
        "cancelado"
    )


def test_transicion_pedido_invalida(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    response = client.put(
        f"/pedidos/{pedido['id']}/estado",
        headers=admin_headers,
        json={
            "estado": "cliente_avisado"
        }
    )

    assert response.status_code == 400

    consulta = client.get(
        f"/pedidos/{pedido['id']}",
        headers=admin_headers
    )

    assert consulta.json()["estado"] == (
        "pendiente"
    )


def test_jefe_no_cambia_estado_pedido(
    client,
    admin_headers,
    jefe_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    response = client.put(
        f"/pedidos/{pedido['id']}/estado",
        headers=jefe_headers,
        json={
            "estado": "cancelado"
        }
    )

    assert response.status_code == 403


def test_administrador_elimina_pedido_pendiente(
    client,
    db,
    admin_headers
):
    from models.pedido import Pedido
    from models.pedido_producto import (
        PedidoProducto
    )

    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    response = client.delete(
        f"/pedidos/{pedido['id']}",
        headers=admin_headers
    )

    assert response.status_code == 200

    pedido_eliminado = db.query(
        Pedido
    ).filter(
        Pedido.id == pedido["id"]
    ).first()

    renglones = db.query(
        PedidoProducto
    ).filter(
        PedidoProducto.pedido_id
        == pedido["id"]
    ).count()

    assert pedido_eliminado is None
    assert renglones == 0


def test_no_eliminar_pedido_cancelado(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    client.put(
        f"/pedidos/{pedido['id']}/estado",
        headers=admin_headers,
        json={
            "estado": "cancelado"
        }
    )

    response = client.delete(
        f"/pedidos/{pedido['id']}",
        headers=admin_headers
    )

    assert response.status_code == 400


def test_no_eliminar_cliente_con_pedido(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    response = client.delete(
        f"/clientes/{cliente['id']}",
        headers=admin_headers
    )

    assert response.status_code == 409


def test_no_eliminar_mueble_con_pedido(
    client,
    admin_headers
):
    cliente, mueble = preparar_datos_pedido(
        client,
        admin_headers
    )

    crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"]
    )

    response = client.delete(
        f"/muebles/{mueble['id']}",
        headers=admin_headers
    )

    assert response.status_code == 409


# =================================================
# ASIGNACIONES Y PRODUCCIÓN
# =================================================

def preparar_flujo_produccion(
    client,
    admin_headers,
    cantidad=1
):
    cliente = crear_cliente_api(
        client,
        admin_headers
    )

    mueble = crear_mueble_api(
        client,
        admin_headers,
        codigo="MES-001"
    )

    armado = crear_empleado_api(
        client,
        admin_headers,
        codigo="CAR-A01",
        email="armado@example.com",
        tipo_carpintero="armado"
    )

    labrado = crear_empleado_api(
        client,
        admin_headers,
        codigo="CAR-L01",
        email="labrado@example.com",
        tipo_carpintero="labrado",
        especialidad_labrado=(
            "Tallado artesanal"
        )
    )

    pedido = crear_pedido_api(
        client,
        admin_headers,
        cliente["id"],
        mueble["id"],
        cantidad=cantidad,
        senia=50000
    )

    return {
        "cliente": cliente,
        "mueble": mueble,
        "armado": armado,
        "labrado": labrado,
        "pedido": pedido,
        "renglon": pedido["productos"][0]
    }


def crear_asignacion_api(
    client,
    headers,
    flujo
):
    response = client.post(
        "/asignaciones",
        headers=headers,
        json={
            "pedido_producto_id":
                flujo["renglon"]["id"],

            "carpintero_armado_id":
                flujo["armado"]["id"],

            "carpintero_labrado_id":
                flujo["labrado"]["id"]
        }
    )

    assert response.status_code == 200

    return response.json()


def iniciar_asignacion_api(
    client,
    headers,
    asignacion_id
):
    response = client.put(
        f"/asignaciones/" +
        f"{asignacion_id}/iniciar",
        headers=headers
    )

    assert response.status_code == 200

    return response.json()


def registrar_nota_api(
    client,
    headers,
    asignacion_id
):
    response = client.post(
        "/notas-produccion",
        headers=headers,
        json={
            "asignacion_id": asignacion_id
        }
    )

    assert response.status_code == 200

    return response.json()


def test_administrador_crea_asignacion(
    client,
    admin_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    asignacion = crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    assert asignacion["estado"] == "asignada"

    assert (
        asignacion["pedido_producto_id"]
        == flujo["renglon"]["id"]
    )

    pedido_response = client.get(
        f"/pedidos/{flujo['pedido']['id']}",
        headers=admin_headers
    )

    assert (
        pedido_response.json()["estado"]
        == "asignado"
    )

    empleados_response = client.get(
        "/empleados",
        headers=admin_headers
    )

    empleados = empleados_response.json()

    armado = next(
        empleado
        for empleado in empleados
        if empleado["id"]
        == flujo["armado"]["id"]
    )

    labrado = next(
        empleado
        for empleado in empleados
        if empleado["id"]
        == flujo["labrado"]["id"]
    )

    assert armado["disponible"] is False
    assert labrado["disponible"] is False


def test_jefe_crea_asignacion(
    client,
    admin_headers,
    jefe_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    asignacion = crear_asignacion_api(
        client,
        jefe_headers,
        flujo
    )

    assert asignacion["estado"] == "asignada"


def test_recepcionista_no_crea_asignacion(
    client,
    admin_headers,
    recepcionista_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    response = client.post(
        "/asignaciones",
        headers=recepcionista_headers,
        json={
            "pedido_producto_id":
                flujo["renglon"]["id"],

            "carpintero_armado_id":
                flujo["armado"]["id"],

            "carpintero_labrado_id":
                flujo["labrado"]["id"]
        }
    )

    assert response.status_code == 403


def test_mueble_labrado_requiere_carpintero(
    client,
    admin_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    response = client.post(
        "/asignaciones",
        headers=admin_headers,
        json={
            "pedido_producto_id":
                flujo["renglon"]["id"],

            "carpintero_armado_id":
                flujo["armado"]["id"],

            "carpintero_labrado_id": None
        }
    )

    assert response.status_code == 400


def test_asignacion_rechaza_tipo_incorrecto(
    client,
    admin_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    response = client.post(
        "/asignaciones",
        headers=admin_headers,
        json={
            "pedido_producto_id":
                flujo["renglon"]["id"],

            "carpintero_armado_id":
                flujo["labrado"]["id"],

            "carpintero_labrado_id":
                flujo["armado"]["id"]
        }
    )

    assert response.status_code == 400


def test_roles_produccion_consultan_asignaciones(
    client,
    admin_headers,
    headers_para
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    roles = [
        "administrador",
        "jefe_carpinteros",
        "carpintero"
    ]

    for rol in roles:
        headers = headers_para(rol=rol)

        response = client.get(
            "/asignaciones",
            headers=headers
        )

        assert response.status_code == 200
        assert len(response.json()) == 1


def test_buscar_asignacion(
    client,
    admin_headers,
    jefe_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    response = client.get(
        "/asignaciones/buscar",
        headers=jefe_headers,
        params={
            "pedido_id":
                flujo["pedido"]["id"],

            "carpintero_id":
                flujo["armado"]["id"],

            "estado": "asignada"
        }
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_recepcionista_no_consulta_asignaciones(
    client,
    recepcionista_headers
):
    response = client.get(
        "/asignaciones",
        headers=recepcionista_headers
    )

    assert response.status_code == 403


def test_carpintero_inicia_produccion(
    client,
    admin_headers,
    carpintero_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    asignacion = crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    iniciada = iniciar_asignacion_api(
        client,
        carpintero_headers,
        asignacion["id"]
    )

    assert iniciada["estado"] == (
        "en_produccion"
    )

    pedido_response = client.get(
        f"/pedidos/{flujo['pedido']['id']}",
        headers=carpintero_headers
    )

    assert (
        pedido_response.json()["estado"]
        == "en_produccion"
    )


def test_jefe_no_inicia_produccion(
    client,
    admin_headers,
    jefe_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    asignacion = crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    response = client.put(
        f"/asignaciones/" +
        f"{asignacion['id']}/iniciar",
        headers=jefe_headers
    )

    assert response.status_code == 403


def test_no_registrar_nota_antes_de_iniciar(
    client,
    admin_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    asignacion = crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    response = client.post(
        "/notas-produccion",
        headers=admin_headers,
        json={
            "asignacion_id": asignacion["id"]
        }
    )

    assert response.status_code == 400


def test_dos_unidades_completan_produccion(
    client,
    admin_headers,
    carpintero_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers,
        cantidad=2
    )

    asignacion = crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    iniciar_asignacion_api(
        client,
        carpintero_headers,
        asignacion["id"]
    )

    primera_nota = registrar_nota_api(
        client,
        carpintero_headers,
        asignacion["id"]
    )

    assert primera_nota["numero_unidad"] == 1

    asignacion_intermedia = client.get(
        f"/asignaciones/{asignacion['id']}",
        headers=carpintero_headers
    ).json()

    assert asignacion_intermedia["estado"] == (
        "en_produccion"
    )

    segunda_nota = registrar_nota_api(
        client,
        carpintero_headers,
        asignacion["id"]
    )

    assert segunda_nota["numero_unidad"] == 2

    asignacion_final = client.get(
        f"/asignaciones/{asignacion['id']}",
        headers=carpintero_headers
    ).json()

    assert asignacion_final["estado"] == (
        "terminada"
    )

    pedido_final = client.get(
        f"/pedidos/{flujo['pedido']['id']}",
        headers=carpintero_headers
    ).json()

    assert pedido_final["estado"] == "terminado"

    empleados = client.get(
        "/empleados",
        headers=admin_headers
    ).json()

    armado = next(
        empleado
        for empleado in empleados
        if empleado["id"]
        == flujo["armado"]["id"]
    )

    labrado = next(
        empleado
        for empleado in empleados
        if empleado["id"]
        == flujo["labrado"]["id"]
    )

    assert armado["disponible"] is True
    assert labrado["disponible"] is True


def test_jefe_no_registra_notas(
    client,
    admin_headers,
    jefe_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    asignacion = crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    iniciar_asignacion_api(
        client,
        admin_headers,
        asignacion["id"]
    )

    response = client.post(
        "/notas-produccion",
        headers=jefe_headers,
        json={
            "asignacion_id": asignacion["id"]
        }
    )

    assert response.status_code == 403


def test_buscar_nota_produccion(
    client,
    admin_headers,
    carpintero_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    asignacion = crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    iniciar_asignacion_api(
        client,
        carpintero_headers,
        asignacion["id"]
    )

    nota = registrar_nota_api(
        client,
        carpintero_headers,
        asignacion["id"]
    )

    response = client.get(
        "/notas-produccion/buscar",
        headers=carpintero_headers,
        params={
            "numero_nota": nota["id"],
            "numero_pedido":
                flujo["pedido"]["id"],
            "codigo_mueble": "MES-001",
            "codigo_carpintero": "CAR-A01"
        }
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_recepcionista_no_consulta_notas(
    client,
    recepcionista_headers
):
    response = client.get(
        "/notas-produccion",
        headers=recepcionista_headers
    )

    assert response.status_code == 403


def test_flujo_final_cliente_y_estadisticas(
    client,
    admin_headers,
    recepcionista_headers
):
    flujo = preparar_flujo_produccion(
        client,
        admin_headers
    )

    asignacion = crear_asignacion_api(
        client,
        admin_headers,
        flujo
    )

    iniciar_asignacion_api(
        client,
        admin_headers,
        asignacion["id"]
    )

    registrar_nota_api(
        client,
        admin_headers,
        asignacion["id"]
    )

    avisado = client.put(
        f"/pedidos/{flujo['pedido']['id']}" +
        "/estado",
        headers=recepcionista_headers,
        json={
            "estado": "cliente_avisado"
        }
    )

    assert avisado.status_code == 200

    assert avisado.json()["estado"] == (
        "cliente_avisado"
    )

    retirado = client.put(
        f"/pedidos/{flujo['pedido']['id']}" +
        "/estado",
        headers=recepcionista_headers,
        json={
            "estado":
                "retirado_por_cliente"
        }
    )

    assert retirado.status_code == 200

    assert retirado.json()["estado"] == (
        "retirado_por_cliente"
    )

    estadisticas = client.get(
        "/admin/estadisticas",
        headers=admin_headers
    )

    assert estadisticas.status_code == 200

    data = estadisticas.json()

    assert data["total_pedidos"] == 1

    assert (
        data["retirados_por_cliente"]
        == 1
    )

    assert data["pendientes"] == 0
    assert data["en_produccion"] == 0