from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from database import engine, get_db
from models.base import Base
from models.mueble import Mueble
from models.usuario import Usuario
from models.empleado import Empleado
from models.cliente import Cliente
from models.pedido import Pedido
from models.pedido_producto import PedidoProducto
from models.asignacion_trabajo import AsignacionTrabajo
from models.nota_produccion import NotaProduccion

import random
import string
import uuid
from typing import Optional
from datetime import datetime, timedelta

import logging

from security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

from schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
    UsuarioLogin,
    UsuarioBusquedaResponse,
    RolEnum
)

from schemas.mueble import (
    MuebleCreate,
    MuebleUpdate,
    MuebleResponse,
    MuebleBusquedaResponse
)

from schemas.empleado import (
    EmpleadoCreate,
    EmpleadoUpdate,
    EmpleadoResponse,
    EmpleadoBusquedaResponse,
    PuestoEmpleadoEnum,
    TipoCarpinteroEnum
)

from schemas.cliente import (
    ClienteCreate,
    ClienteUpdate,
    ClienteResponse,
    ClienteBusquedaResponse
)

from schemas.pedido import (
    PedidoCreate,
    PedidoProductoCreate,
    PedidoProductoResponse,
    PedidoResponse,
    PedidoEstadoUpdate,
    PedidoBusquedaResponse,
    EstadoPedidoEnum
)

from schemas.asignacion_trabajo import (
    AsignacionTrabajoCreate,
    AsignacionTrabajoResponse,
    AsignacionBusquedaResponse,
    EstadoAsignacionEnum
)

from schemas.nota_produccion import (
    NotaProduccionCreate,
    NotaProduccionResponse,
    NotaProduccionBusquedaResponse
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="El Algarrobo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )

    user_id = token_data["user_id"]

    usuario = db.query(Usuario).filter(
        Usuario.id == user_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    return usuario

def require_role(required_role: str):
    def role_checker(
        usuario_actual: Usuario = Depends(get_current_user)
    ):
        if usuario_actual.rol != required_role:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para realizar esta acción"
            )

        return usuario_actual

    return role_checker

def require_roles(*required_roles: str):
    def role_checker(
        usuario_actual: Usuario = Depends(get_current_user)
    ):
        if usuario_actual.rol not in required_roles:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para realizar esta acción"
            )

        return usuario_actual

    return role_checker

def get_current_admin(
    usuario_actual: Usuario = Depends(get_current_user)
):
    if usuario_actual.rol != "administrador":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para realizar esta acción"
        )

    return usuario_actual


@app.get("/")
def inicio(db: Session = Depends(get_db)):
    return {"mensaje": "El Algarrobo API funcionando"}

# Login del usuario
@app.post("/login")
def login(
    datos: UsuarioLogin,
    db: Session = Depends(get_db)
):
    # Verificar captcha
    captcha_data = captchas.get(datos.captcha_id)

    if captcha_data is None:
        raise HTTPException(
            status_code=400,
            detail="CAPTCHA inválido o expirado"
        )

    codigo_correcto = captcha_data["codigo"]
    creado = captcha_data["creado"]

    if datetime.now() - creado > timedelta(minutes=2):
        del captchas[datos.captcha_id]

        raise HTTPException(
            status_code=400,
            detail="CAPTCHA expirado"
        )

    if datos.captcha != codigo_correcto:
        raise HTTPException(
            status_code=400,
            detail="CAPTCHA incorrecto"
        )

    del captchas[datos.captcha_id]

    # buscar usuario
    usuario = db.query(Usuario).filter(
        Usuario.username == datos.username
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    if not verify_password(
        datos.password,
        usuario.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    token = create_access_token(
        usuario.id,
        usuario.rol
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/admin")
def panel_admin(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    total_usuarios = db.query(Usuario).count()
    total_muebles = db.query(Mueble).count()

    return {
        "mensaje": "Bienvenido al panel de administrador",
        "usuario": usuario_actual.username,
        "rol": usuario_actual.rol,
        "secciones": [
            "empleados",
            "muebles",
            "clientes",
            "pedidos",
            "estadisticas"
        ],
        "resumen": {
            "total_usuarios": total_usuarios,
            "total_muebles": total_muebles
        }
    }


@app.get("/admin/estadisticas")
def estadisticas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    total_pedidos = db.query(Pedido).count()

    pendientes = db.query(Pedido).filter(
        Pedido.estado == "pendiente"
    ).count()

    asignados = db.query(Pedido).filter(
        Pedido.estado == "asignado"
    ).count()

    en_produccion = db.query(Pedido).filter(
        Pedido.estado == "en_produccion"
    ).count()

    terminados = db.query(Pedido).filter(
        Pedido.estado == "terminado"
    ).count()

    clientes_avisados = db.query(Pedido).filter(
        Pedido.estado == "cliente_avisado"
    ).count()

    retirados_por_cliente = db.query(Pedido).filter(
        Pedido.estado == "retirado_por_cliente"
    ).count()

    cancelados = db.query(Pedido).filter(
        Pedido.estado == "cancelado"
    ).count()

    return {
        "total_pedidos": total_pedidos,
        "pendientes": pendientes,
        "asignados": asignados,
        "en_produccion": en_produccion,
        "terminados": terminados,
        "clientes_avisados": clientes_avisados,
        "retirados_por_cliente": retirados_por_cliente,
        "cancelados": cancelados
    }



@app.get("/staff")
def staff_area(
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    return {
        "mensaje": "Bienvenido al área del personal",
        "usuario": usuario_actual.username,
        "rol": usuario_actual.rol
    }

captchas = {}

def limpiar_captchas_expirados():
    ahora = datetime.now()

    ids_expirados = []

    for captcha_id, captcha_data in captchas.items():
        creado = captcha_data["creado"]

        if ahora - creado > timedelta(minutes=2):
            ids_expirados.append(captcha_id)

    for captcha_id in ids_expirados:
        del captchas[captcha_id]

@app.get("/captcha")
def generar_captcha():
    limpiar_captchas_expirados()

    captcha_id = str(uuid.uuid4())

    codigo = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=5
        )
    )

    captchas[captcha_id] = {
        "codigo": codigo,
        "creado": datetime.now()
    }

    return {
        "captcha_id": captcha_id,
        "captcha": codigo
    }



# Crear un usuario
@app.post(
    "/usuarios",
    response_model=UsuarioResponse
)
def crear_usuario(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    username = datos.username.strip()

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario es demasiado corto"
        )

    usuario_existente = db.query(Usuario).filter(
        Usuario.username == username
    ).first()

    if usuario_existente is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un usuario con ese nombre"
        )

    usuario = Usuario(
        username=username,
        password=hash_password(datos.password),
        rol=datos.rol.value
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario

# Obtener todos los usuarios
@app.get(
    "/usuarios",
    response_model=list[UsuarioResponse]
)
def obtener_usuarios(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    return db.query(Usuario).all()

# Buscar usuarios
@app.get(
    "/usuarios/buscar",
    response_model=UsuarioBusquedaResponse
)
def buscar_usuarios(
    username: Optional[str] = None,
    rol: Optional[RolEnum] = None,
    orden: Optional[str] = "asc",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    if username is None and rol is None:
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un criterio de búsqueda"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="El límite debe estar entre 1 y 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El offset no puede ser negativo"
        )

    if orden not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="El orden debe ser 'asc' o 'desc'"
        )

    consulta = db.query(Usuario)

    if username is not None:
        consulta = consulta.filter(
            Usuario.username.ilike(
                f"%{username.strip()}%"
            )
        )

    if rol is not None:
        consulta = consulta.filter(
            Usuario.rol == rol.value
        )

    total = consulta.count()

    if orden == "asc":
        consulta = consulta.order_by(
            Usuario.username.asc()
        )
    else:
        consulta = consulta.order_by(
            Usuario.username.desc()
        )

    usuarios = consulta.limit(limit).offset(offset).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "resultados": usuarios
    }

# Obtener un usuario especifico
@app.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse
)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return usuario

# Modificar usuario
@app.put(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse
)
def modificar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    if datos.username is not None:
        nuevo_username = datos.username.strip()

        if len(nuevo_username) < 3:
            raise HTTPException(
                status_code=400,
                detail="El nombre de usuario es demasiado corto"
            )

        usuario_con_username = db.query(Usuario).filter(
            Usuario.username == nuevo_username,
            Usuario.id != usuario_id
        ).first()

        if usuario_con_username is not None:
            raise HTTPException(
                status_code=409,
                detail="Ya existe otro usuario con ese nombre"
            )

        usuario.username = nuevo_username

    if datos.password is not None:
        usuario.password = hash_password(datos.password)

    if datos.rol is not None:
        usuario.rol = datos.rol.value

    db.commit()
    db.refresh(usuario)

    return usuario

# Eliminar usuario
@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    db.delete(usuario)
    db.commit()

    return {
        "mensaje": "Usuario eliminado correctamente"
    }



@app.post(
    "/muebles",
    response_model=MuebleResponse
)
def crear_mueble(
    datos: MuebleCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    codigo = datos.codigo.strip().upper()

    if codigo == "":
        raise HTTPException(
            status_code=400,
            detail="El código del mueble no puede estar vacío"
        )

    mueble_existente = db.query(Mueble).filter(
        Mueble.codigo == codigo
    ).first()

    if mueble_existente is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un mueble con ese código"
        )

    mueble = Mueble(
        codigo=codigo,
        descripcion=datos.descripcion,
        tamanos_sugeridos=datos.tamanos_sugeridos,
        labrado=datos.labrado,
        precio=datos.precio
    )

    db.add(mueble)
    db.commit()
    db.refresh(mueble)

    return mueble

# Obtener todos los muebles
@app.get(
    "/muebles",
    response_model=list[MuebleResponse]
)
def obtener_muebles(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    return db.query(Mueble).all()

# Buscar muebles
@app.get(
    "/muebles/buscar",
    response_model=MuebleBusquedaResponse
)
def buscar_muebles(
    codigo: Optional[str] = None,
    numero_pedido: Optional[int] = None,
    orden: Optional[str] = "asc",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    if codigo is None and numero_pedido is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Debes proporcionar un código de mueble "
                "o un número de pedido"
            )
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="El límite debe estar entre 1 y 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El offset no puede ser negativo"
        )

    if orden not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="El orden debe ser 'asc' o 'desc'"
        )

    consulta = db.query(Mueble)

    if codigo is not None:
        codigo_limpio = codigo.strip().upper()

        if codigo_limpio == "":
            raise HTTPException(
                status_code=400,
                detail="El código del mueble no puede estar vacío"
            )

        consulta = consulta.filter(
            Mueble.codigo.like(f"%{codigo_limpio}%")
        )

    if numero_pedido is not None:
        if numero_pedido < 1:
            raise HTTPException(
                status_code=400,
                detail="El número de pedido debe ser mayor que cero"
            )

        consulta = consulta.join(
            PedidoProducto,
            PedidoProducto.mueble_id == Mueble.id
        ).filter(
            PedidoProducto.pedido_id == numero_pedido
        ).distinct()

    total = consulta.count()

    if orden == "asc":
        consulta = consulta.order_by(
            Mueble.codigo.asc()
        )
    else:
        consulta = consulta.order_by(
            Mueble.codigo.desc()
        )

    muebles = consulta.limit(limit).offset(offset).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "resultados": muebles
    }

# Obtener un mueble específico
@app.get(
    "/muebles/{mueble_id}",
    response_model=MuebleResponse
)
def obtener_mueble(
    mueble_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    mueble = db.query(Mueble).filter(
        Mueble.id == mueble_id
    ).first()

    if mueble is None:
        raise HTTPException(
            status_code=404,
            detail="Mueble no encontrado"
        )

    return mueble

# Modificar un mueble
@app.put(
    "/muebles/{mueble_id}",
    response_model=MuebleResponse
)
def modificar_mueble(
    mueble_id: int,
    datos: MuebleUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    mueble = db.query(Mueble).filter(
        Mueble.id == mueble_id
    ).first()

    if mueble is None:
        raise HTTPException(
            status_code=404,
            detail="Mueble no encontrado"
        )

    if datos.codigo is not None:
        codigo = datos.codigo.strip().upper()

        if codigo == "":
            raise HTTPException(
                status_code=400,
                detail="El código del mueble no puede estar vacío"
            )

        mueble_con_codigo = db.query(Mueble).filter(
            Mueble.codigo == codigo,
            Mueble.id != mueble_id
        ).first()

        if mueble_con_codigo is not None:
            raise HTTPException(
                status_code=409,
                detail="Ya existe otro mueble con ese código"
            )

        mueble.codigo = codigo

    if datos.descripcion is not None:
        mueble.descripcion = datos.descripcion

    if datos.tamanos_sugeridos is not None:
        mueble.tamanos_sugeridos = datos.tamanos_sugeridos

    if datos.labrado is not None:
        mueble.labrado = datos.labrado

    if datos.precio is not None:
        mueble.precio = datos.precio

    db.commit()
    db.refresh(mueble)

    return mueble

# Eliminar un mueble
@app.delete("/muebles/{mueble_id}")
def eliminar_mueble(
    mueble_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    mueble = db.query(Mueble).filter(
        Mueble.id == mueble_id
    ).first()

    if mueble is None:
        raise HTTPException(
            status_code=404,
            detail="Mueble no encontrado"
        )

    pedido_asociado = db.query(PedidoProducto).filter(
        PedidoProducto.mueble_id == mueble_id
    ).first()

    if pedido_asociado is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar el producto porque "
                "pertenece a uno o más pedidos"
            )
        )

    db.delete(mueble)
    db.commit()

    return {
        "mensaje": "Mueble eliminado correctamente"
    }


# Crear un empleado
@app.post(
    "/empleados",
    response_model=EmpleadoResponse
)
def crear_empleado(
    datos: EmpleadoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    codigo = datos.codigo.strip().upper()
    email = str(datos.email).strip().lower()

    if codigo == "":
        raise HTTPException(
            status_code=400,
            detail="El código del empleado no puede estar vacío"
        )

    empleado_con_codigo = db.query(Empleado).filter(
        Empleado.codigo == codigo
    ).first()

    if empleado_con_codigo is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un empleado con ese código"
        )

    empleado_con_email = db.query(Empleado).filter(
        Empleado.email == email
    ).first()

    if empleado_con_email is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un empleado con ese correo electrónico"
        )

    es_carpintero = datos.puesto.value == "carpintero"

    empleado = Empleado(
        codigo=codigo,
        nombre=datos.nombre,
        apellido=datos.apellido,
        email=email,
        telefono=datos.telefono,
        puesto=datos.puesto.value,
        tipo_carpintero=(
            datos.tipo_carpintero.value
            if datos.tipo_carpintero is not None
            else None
        ),
        especialidad_labrado=datos.especialidad_labrado,
        disponible=(
            datos.disponible
            if es_carpintero
            else False
        ),
        activo=datos.activo
    )

    db.add(empleado)
    db.commit()
    db.refresh(empleado)

    return empleado

# Obtener todos los empleados
@app.get(
    "/empleados",
    response_model=list[EmpleadoResponse]
)
def obtener_empleados(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros"
        )
    )
):
    empleados = db.query(Empleado).all()
    return empleados

# Buscar empleados
@app.get(
    "/empleados/buscar",
    response_model=EmpleadoBusquedaResponse
)
def buscar_empleados(
    codigo: Optional[str] = None,
    nombre: Optional[str] = None,
    apellido: Optional[str] = None,
    puesto: Optional[PuestoEmpleadoEnum] = None,
    tipo_carpintero: Optional[TipoCarpinteroEnum] = None,
    disponible: Optional[bool] = None,
    activo: Optional[bool] = None,
    orden: Optional[str] = "asc",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros"
        )
    )
):
    if (
        codigo is None
        and nombre is None
        and apellido is None
        and puesto is None
        and tipo_carpintero is None
        and disponible is None
        and activo is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un criterio de búsqueda"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="El límite debe estar entre 1 y 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El offset no puede ser negativo"
        )

    if orden not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="El orden debe ser 'asc' o 'desc'"
        )

    consulta = db.query(Empleado)

    if codigo is not None:
        consulta = consulta.filter(
            Empleado.codigo.like(
                f"%{codigo.strip().upper()}%"
            )
        )

    if nombre is not None:
        consulta = consulta.filter(
            Empleado.nombre.like(f"%{nombre.strip()}%")
        )

    if apellido is not None:
        consulta = consulta.filter(
            Empleado.apellido.like(f"%{apellido.strip()}%")
        )

    if puesto is not None:
        consulta = consulta.filter(
            Empleado.puesto == puesto.value
        )

    if tipo_carpintero is not None:
        consulta = consulta.filter(
            Empleado.tipo_carpintero
            == tipo_carpintero.value
        )

    if disponible is not None:
        consulta = consulta.filter(
            Empleado.disponible == disponible
        )

    if activo is not None:
        consulta = consulta.filter(
            Empleado.activo == activo
        )

    total = consulta.count()

    if orden == "asc":
        consulta = consulta.order_by(
            Empleado.codigo.asc()
        )
    else:
        consulta = consulta.order_by(
            Empleado.codigo.desc()
        )

    empleados = consulta.limit(limit).offset(offset).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "resultados": empleados
    }

# Obtener un empleado específico
@app.get(
    "/empleados/{empleado_id}",
    response_model=EmpleadoResponse
)
def obtener_empleado(
    empleado_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros"
        )
    )
):
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id
    ).first()

    if empleado is None:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    return empleado

# Modificar un empleado
@app.put(
    "/empleados/{empleado_id}",
    response_model=EmpleadoResponse
)
def modificar_empleado(
    empleado_id: int,
    datos: EmpleadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id
    ).first()

    if empleado is None:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    nuevo_codigo = empleado.codigo

    if datos.codigo is not None:
        nuevo_codigo = datos.codigo.strip().upper()

        if nuevo_codigo == "":
            raise HTTPException(
                status_code=400,
                detail="El código del empleado no puede estar vacío"
            )

        empleado_con_codigo = db.query(Empleado).filter(
            Empleado.codigo == nuevo_codigo,
            Empleado.id != empleado_id
        ).first()

        if empleado_con_codigo is not None:
            raise HTTPException(
                status_code=409,
                detail="Ya existe otro empleado con ese código"
            )

    nuevo_email = empleado.email

    if datos.email is not None:
        nuevo_email = str(datos.email).strip().lower()

        empleado_con_email = db.query(Empleado).filter(
            Empleado.email == nuevo_email,
            Empleado.id != empleado_id
        ).first()

        if empleado_con_email is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Ya existe otro empleado con ese "
                    "correo electrónico"
                )
            )

    nuevo_puesto = empleado.puesto

    if datos.puesto is not None:
        nuevo_puesto = datos.puesto.value

    nuevo_tipo = empleado.tipo_carpintero

    if "tipo_carpintero" in datos.model_fields_set:
        nuevo_tipo = (
            datos.tipo_carpintero.value
            if datos.tipo_carpintero is not None
            else None
        )

    nueva_especialidad = empleado.especialidad_labrado

    if "especialidad_labrado" in datos.model_fields_set:
        nueva_especialidad = datos.especialidad_labrado

    nueva_disponibilidad = empleado.disponible

    if datos.disponible is not None:
        nueva_disponibilidad = datos.disponible

    if nuevo_puesto == "carpintero":
        if nuevo_tipo is None:
            raise HTTPException(
                status_code=400,
                detail="Un carpintero debe tener un tipo"
            )

        if (
            nuevo_tipo == "labrado"
            and nueva_especialidad is None
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Un carpintero de labrado debe indicar "
                    "su especialidad"
                )
            )

        if (
            nuevo_tipo == "armado"
            and nueva_especialidad is not None
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Un carpintero de armado no debe tener "
                    "especialidad de labrado"
                )
            )

    else:
        nuevo_tipo = None
        nueva_especialidad = None
        nueva_disponibilidad = False

    empleado.codigo = nuevo_codigo
    empleado.email = nuevo_email
    empleado.puesto = nuevo_puesto
    empleado.tipo_carpintero = nuevo_tipo
    empleado.especialidad_labrado = nueva_especialidad
    empleado.disponible = nueva_disponibilidad

    if datos.nombre is not None:
        empleado.nombre = datos.nombre

    if datos.apellido is not None:
        empleado.apellido = datos.apellido

    if datos.telefono is not None:
        empleado.telefono = datos.telefono

    if datos.activo is not None:
        empleado.activo = datos.activo

    db.commit()
    db.refresh(empleado)

    return empleado

# Eliminar un empleado
@app.delete("/empleados/{empleado_id}")
def eliminar_empleado(
    empleado_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id
    ).first()

    if empleado is None:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    db.delete(empleado)
    db.commit()

    return {
        "mensaje": "Empleado eliminado correctamente"
    }

# Crear asignacion de trabajo
@app.post(
    "/asignaciones",
    response_model=AsignacionTrabajoResponse
)
def crear_asignacion(
    datos: AsignacionTrabajoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros"
        )
    )
):
    try:
        pedido_producto = db.query(PedidoProducto).filter(
            PedidoProducto.id == datos.pedido_producto_id
        ).first()

        if pedido_producto is None:
            raise HTTPException(
                status_code=404,
                detail="El renglón del pedido no existe"
            )

        if pedido_producto.pedido.estado != "pendiente":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Solo se pueden asignar trabajos de "
                    "pedidos pendientes"
                )
            )

        asignacion_existente = db.query(
            AsignacionTrabajo
        ).filter(
            AsignacionTrabajo.pedido_producto_id
            == datos.pedido_producto_id
        ).first()

        if asignacion_existente is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Este renglón del pedido ya tiene "
                    "una asignación"
                )
            )

        carpintero_armado = db.query(Empleado).filter(
            Empleado.id == datos.carpintero_armado_id
        ).first()

        if carpintero_armado is None:
            raise HTTPException(
                status_code=404,
                detail="El carpintero de armado no existe"
            )

        if (
            not carpintero_armado.activo
            or not carpintero_armado.disponible
            or carpintero_armado.puesto != "carpintero"
            or carpintero_armado.tipo_carpintero != "armado"
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "El empleado seleccionado no es un "
                    "carpintero de armado activo y disponible"
                )
            )

        mueble = pedido_producto.mueble
        carpintero_labrado = None

        if mueble.labrado:
            if datos.carpintero_labrado_id is None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Este mueble requiere un carpintero "
                        "de labrado"
                    )
                )

            carpintero_labrado = db.query(Empleado).filter(
                Empleado.id == datos.carpintero_labrado_id
            ).first()

            if carpintero_labrado is None:
                raise HTTPException(
                    status_code=404,
                    detail="El carpintero de labrado no existe"
                )

            if (
                not carpintero_labrado.activo
                or not carpintero_labrado.disponible
                or carpintero_labrado.puesto != "carpintero"
                or carpintero_labrado.tipo_carpintero != "labrado"
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "El empleado seleccionado no es un "
                        "carpintero de labrado activo y disponible"
                    )
                )

        elif datos.carpintero_labrado_id is not None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Este mueble no requiere un carpintero "
                    "de labrado"
                )
            )

        asignacion = AsignacionTrabajo(
            pedido_producto_id=datos.pedido_producto_id,
            carpintero_armado_id=datos.carpintero_armado_id,
            carpintero_labrado_id=(
                datos.carpintero_labrado_id
            )
        )

        db.add(asignacion)

        carpintero_armado.disponible = False

        if carpintero_labrado is not None:
            carpintero_labrado.disponible = False

        db.flush()

        renglones_sin_asignar = db.query(
            PedidoProducto
        ).outerjoin(
            AsignacionTrabajo,
            AsignacionTrabajo.pedido_producto_id
            == PedidoProducto.id
        ).filter(
            PedidoProducto.pedido_id
            == pedido_producto.pedido_id,
            AsignacionTrabajo.id.is_(None)
        ).count()

        if renglones_sin_asignar == 0:
            pedido_producto.pedido.estado = "asignado"

        db.commit()
        db.refresh(asignacion)

        return asignacion

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        logger.exception(
            "Error inesperado al crear la asignación"
        )

        raise HTTPException(
            status_code=500,
            detail="Error al crear la asignación"
        )

# Obtener todas las asignaciones
@app.get(
    "/asignaciones",
    response_model=list[AsignacionTrabajoResponse]
)
def obtener_asignaciones(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    return db.query(AsignacionTrabajo).all()

# Buscar asignaciones
@app.get(
    "/asignaciones/buscar",
    response_model=AsignacionBusquedaResponse
)
def buscar_asignaciones(
    pedido_id: Optional[int] = None,
    carpintero_id: Optional[int] = None,
    estado: Optional[EstadoAsignacionEnum] = None,
    orden: Optional[str] = "asc",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    if (
        pedido_id is None
        and carpintero_id is None
        and estado is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un criterio de búsqueda"
        )

    if pedido_id is not None and pedido_id < 1:
        raise HTTPException(
            status_code=400,
            detail="El número de pedido debe ser mayor que cero"
        )

    if carpintero_id is not None and carpintero_id < 1:
        raise HTTPException(
            status_code=400,
            detail="El identificador del carpintero debe ser positivo"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="El límite debe estar entre 1 y 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El offset no puede ser negativo"
        )

    if orden not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="El orden debe ser 'asc' o 'desc'"
        )

    consulta = db.query(AsignacionTrabajo)

    if pedido_id is not None:
        consulta = consulta.join(
            PedidoProducto,
            AsignacionTrabajo.pedido_producto_id
            == PedidoProducto.id
        ).filter(
            PedidoProducto.pedido_id == pedido_id
        )

    if carpintero_id is not None:
        consulta = consulta.filter(
            (
                AsignacionTrabajo.carpintero_armado_id
                == carpintero_id
            )
            |
            (
                AsignacionTrabajo.carpintero_labrado_id
                == carpintero_id
            )
        )

    if estado is not None:
        consulta = consulta.filter(
            AsignacionTrabajo.estado == estado.value
        )

    total = consulta.count()

    if orden == "asc":
        consulta = consulta.order_by(
            AsignacionTrabajo.fecha_asignacion.asc()
        )
    else:
        consulta = consulta.order_by(
            AsignacionTrabajo.fecha_asignacion.desc()
        )

    asignaciones = consulta.limit(limit).offset(offset).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "resultados": asignaciones
    }

# Obtener una asignacion especifica
@app.get(
    "/asignaciones/{asignacion_id}",
    response_model=AsignacionTrabajoResponse
)
def obtener_asignacion(
    asignacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    asignacion = db.query(AsignacionTrabajo).filter(
        AsignacionTrabajo.id == asignacion_id
    ).first()

    if asignacion is None:
        raise HTTPException(
            status_code=404,
            detail="Asignación no encontrada"
        )

    return asignacion

# Iniciar una asignación
@app.put(
    "/asignaciones/{asignacion_id}/iniciar",
    response_model=AsignacionTrabajoResponse
)
def iniciar_asignacion(
    asignacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "carpintero"
        )
    )
):
    asignacion = db.query(AsignacionTrabajo).filter(
        AsignacionTrabajo.id == asignacion_id
    ).first()

    if asignacion is None:
        raise HTTPException(
            status_code=404,
            detail="Asignación no encontrada"
        )

    if asignacion.estado != "asignada":
        raise HTTPException(
            status_code=400,
            detail=(
                "Solo se puede iniciar una asignación "
                "que esté asignada"
            )
        )

    pedido = asignacion.pedido_producto.pedido

    if pedido.estado not in [
        "asignado",
        "en_produccion"
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "El pedido no se encuentra en condiciones "
                "de iniciar la producción"
            )
        )

    asignacion.estado = "en_produccion"
    pedido.estado = "en_produccion"

    db.commit()
    db.refresh(asignacion)

    return asignacion

# Crear nota de producción
@app.post(
    "/notas-produccion",
    response_model=NotaProduccionResponse
)
def crear_nota_produccion(
    datos: NotaProduccionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "carpintero"
        )
    )
):
    try:
        asignacion = db.query(AsignacionTrabajo).filter(
            AsignacionTrabajo.id == datos.asignacion_id
        ).first()

        if asignacion is None:
            raise HTTPException(
                status_code=404,
                detail="Asignación no encontrada"
            )

        if asignacion.estado != "en_produccion":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Solo se pueden registrar unidades de una "
                    "asignación en producción"
                )
            )

        pedido_producto = asignacion.pedido_producto

        cantidad_terminada = db.query(
            NotaProduccion
        ).filter(
            NotaProduccion.asignacion_id == asignacion.id
        ).count()

        if cantidad_terminada >= pedido_producto.cantidad:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Todas las unidades de esta asignación "
                    "ya fueron registradas"
                )
            )

        numero_unidad = cantidad_terminada + 1

        nota = NotaProduccion(
            asignacion_id=asignacion.id,
            numero_unidad=numero_unidad,
            pedido_id=pedido_producto.pedido_id,
            mueble_id=pedido_producto.mueble_id,
            carpintero_id=(
                asignacion.carpintero_armado_id
            )
        )

        db.add(nota)

        if numero_unidad == pedido_producto.cantidad:
            asignacion.estado = "terminada"

            asignacion.carpintero_armado.disponible = (
                asignacion.carpintero_armado.activo
            )

            if asignacion.carpintero_labrado is not None:
                asignacion.carpintero_labrado.disponible = (
                    asignacion.carpintero_labrado.activo
                )

            db.flush()

            asignaciones_sin_terminar = db.query(
                AsignacionTrabajo
            ).join(
                PedidoProducto,
                AsignacionTrabajo.pedido_producto_id
                == PedidoProducto.id
            ).filter(
                PedidoProducto.pedido_id
                == pedido_producto.pedido_id,
                AsignacionTrabajo.estado != "terminada"
            ).count()

            if asignaciones_sin_terminar == 0:
                pedido_producto.pedido.estado = "terminado"

        db.commit()
        db.refresh(nota)

        return nota

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        logger.exception(
            "Error inesperado al crear la nota de producción"
        )

        raise HTTPException(
            status_code=500,
            detail="Error al crear la nota de producción"
        )

# Obtener todas las notas
@app.get(
    "/notas-produccion",
    response_model=list[NotaProduccionResponse]
)
def obtener_notas_produccion(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    return db.query(NotaProduccion).all()

# Buscar notas
@app.get(
    "/notas-produccion/buscar",
    response_model=NotaProduccionBusquedaResponse
)
def buscar_notas_produccion(
    numero_nota: Optional[int] = None,
    numero_pedido: Optional[int] = None,
    codigo_mueble: Optional[str] = None,
    codigo_carpintero: Optional[str] = None,
    orden: Optional[str] = "asc",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    if (
        numero_nota is None
        and numero_pedido is None
        and codigo_mueble is None
        and codigo_carpintero is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un criterio de búsqueda"
        )

    if numero_nota is not None and numero_nota < 1:
        raise HTTPException(
            status_code=400,
            detail="El número de nota debe ser mayor que cero"
        )

    if numero_pedido is not None and numero_pedido < 1:
        raise HTTPException(
            status_code=400,
            detail="El número de pedido debe ser mayor que cero"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="El límite debe estar entre 1 y 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El offset no puede ser negativo"
        )

    if orden not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="El orden debe ser 'asc' o 'desc'"
        )

    consulta = db.query(NotaProduccion)

    if numero_nota is not None:
        consulta = consulta.filter(
            NotaProduccion.id == numero_nota
        )

    if numero_pedido is not None:
        consulta = consulta.filter(
            NotaProduccion.pedido_id == numero_pedido
        )

    if codigo_mueble is not None:
        codigo_mueble_limpio = (
            codigo_mueble.strip().upper()
        )

        if codigo_mueble_limpio == "":
            raise HTTPException(
                status_code=400,
                detail="El código del mueble no puede estar vacío"
            )

        consulta = consulta.join(
            Mueble,
            NotaProduccion.mueble_id == Mueble.id
        ).filter(
            Mueble.codigo.like(
                f"%{codigo_mueble_limpio}%"
            )
        )

    if codigo_carpintero is not None:
        codigo_carpintero_limpio = (
            codigo_carpintero.strip().upper()
        )

        if codigo_carpintero_limpio == "":
            raise HTTPException(
                status_code=400,
                detail="El código del carpintero no puede estar vacío"
            )

        consulta = consulta.join(
            Empleado,
            NotaProduccion.carpintero_id == Empleado.id
        ).filter(
            Empleado.codigo.like(
                f"%{codigo_carpintero_limpio}%"
            )
        )

    total = consulta.count()

    if orden == "asc":
        consulta = consulta.order_by(
            NotaProduccion.fecha_entrega.asc()
        )
    else:
        consulta = consulta.order_by(
            NotaProduccion.fecha_entrega.desc()
        )

    notas = consulta.limit(limit).offset(offset).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "resultados": notas
    }

# Obtener una nota especifica
@app.get(
    "/notas-produccion/{nota_id}",
    response_model=NotaProduccionResponse
)
def obtener_nota_produccion(
    nota_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    nota = db.query(NotaProduccion).filter(
        NotaProduccion.id == nota_id
    ).first()

    if nota is None:
        raise HTTPException(
            status_code=404,
            detail="Nota de producción no encontrada"
        )

    return nota

# Crear un cliente
@app.post(
    "/clientes",
    response_model=ClienteResponse
)
def crear_cliente(
    datos: ClienteCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista"
        )
    )
):
    cliente = Cliente(
        nombre=datos.nombre,
        apellido=datos.apellido,
        domicilio=datos.domicilio,
        telefono=datos.telefono,
        tarjeta_credito=datos.tarjeta_credito,
        numero_tarjeta=datos.numero_tarjeta,
        numero_cuenta_bancaria=(
            datos.numero_cuenta_bancaria
        ),
        codigo_banco=datos.codigo_banco
    )

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente

# Obtener todos los clientes
@app.get(
    "/clientes",
    response_model=list[ClienteResponse]
)
def obtener_clientes(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista"
        )
    )
):
    clientes = db.query(Cliente).all()

    return clientes

# Buscar clientes
@app.get(
    "/clientes/buscar",
    response_model=ClienteBusquedaResponse
)
def buscar_clientes(
    nombre: Optional[str] = None,
    apellido: Optional[str] = None,
    telefono: Optional[str] = None,
    orden: Optional[str] = "asc",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista"
        )
    )
):
    if (
        nombre is None
        and apellido is None
        and telefono is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un criterio de búsqueda"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="El límite debe estar entre 1 y 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El offset no puede ser negativo"
        )

    if orden not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="El orden debe ser 'asc' o 'desc'"
        )

    consulta = db.query(Cliente)

    if nombre is not None:
        consulta = consulta.filter(
            Cliente.nombre.like(f"%{nombre.strip()}%")
        )

    if apellido is not None:
        consulta = consulta.filter(
            Cliente.apellido.like(f"%{apellido.strip()}%")
        )

    if telefono is not None:
        consulta = consulta.filter(
            Cliente.telefono.like(f"%{telefono.strip()}%")
        )

    total = consulta.count()

    if orden == "asc":
        consulta = consulta.order_by(
            Cliente.apellido.asc(),
            Cliente.nombre.asc()
        )
    else:
        consulta = consulta.order_by(
            Cliente.apellido.desc(),
            Cliente.nombre.desc()
        )

    clientes = consulta.limit(limit).offset(offset).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "resultados": clientes
    }

# Obtener un cliente específico
@app.get(
    "/clientes/{cliente_id}",
    response_model=ClienteResponse
)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista"
        )
    )
):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return cliente

# Modificar un cliente
@app.put(
    "/clientes/{cliente_id}",
    response_model=ClienteResponse
)
def modificar_cliente(
    cliente_id: int,
    datos: ClienteUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista"
        )
    )
):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    if datos.nombre is not None:
        cliente.nombre = datos.nombre

    if datos.apellido is not None:
        cliente.apellido = datos.apellido

    if datos.domicilio is not None:
        cliente.domicilio = datos.domicilio

    if datos.telefono is not None:
        cliente.telefono = datos.telefono

    if datos.tarjeta_credito is not None:
        cliente.tarjeta_credito = datos.tarjeta_credito

    if datos.numero_tarjeta is not None:
        cliente.numero_tarjeta = datos.numero_tarjeta

    if datos.numero_cuenta_bancaria is not None:
        cliente.numero_cuenta_bancaria = (
            datos.numero_cuenta_bancaria
        )

    if datos.codigo_banco is not None:
        cliente.codigo_banco = datos.codigo_banco

    db.commit()
    db.refresh(cliente)

    return cliente

# Eliminar un cliente
@app.delete("/clientes/{cliente_id}")
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    pedido_asociado = db.query(Pedido).filter(
        Pedido.cliente_id == cliente_id
    ).first()

    if pedido_asociado is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar el cliente porque "
                "tiene pedidos asociados"
            )
        )

    db.delete(cliente)
    db.commit()

    return {
        "mensaje": "Cliente eliminado correctamente"
    }


# Crear un pedido
@app.post(
    "/pedidos",
    response_model=PedidoResponse
)
def crear_pedido(
    datos: PedidoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista"
        )
    )
):
    try:
        cliente = db.query(Cliente).filter(
            Cliente.id == datos.cliente_id
        ).first()

        if cliente is None:
            raise HTTPException(
                status_code=404,
                detail="Cliente no encontrado"
            )

        muebles_ids = [
            producto.mueble_id
            for producto in datos.productos
        ]

        if len(muebles_ids) != len(set(muebles_ids)):
            raise HTTPException(
                status_code=400,
                detail="No puedes agregar el mismo mueble más de una vez"
            )

        total_pedido = 0
        muebles_verificados = []

        for producto in datos.productos:
            mueble = db.query(Mueble).filter(
                Mueble.id == producto.mueble_id
            ).first()

            if mueble is None:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Mueble con ID {producto.mueble_id} "
                        "no encontrado"
                    )
                )

            total_pedido += (
                mueble.precio * producto.cantidad
            )

            muebles_verificados.append(producto)

        if datos.senia > total_pedido:
            raise HTTPException(
                status_code=400,
                detail=(
                    "La seña no puede superar el precio "
                    "total del pedido"
                )
            )

        pedido = Pedido(
            cliente_id=datos.cliente_id,
            fecha_estimada_entrega=(
                datos.fecha_estimada_entrega
            ),
            senia=datos.senia
        )

        db.add(pedido)
        db.flush()

        for producto in muebles_verificados:
            pedido_producto = PedidoProducto(
                pedido_id=pedido.id,
                mueble_id=producto.mueble_id,
                cantidad=producto.cantidad
            )

            db.add(pedido_producto)

        db.commit()
        db.refresh(pedido)

        return pedido

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        logger.exception(
            "Error inesperado al crear el pedido"
        )

        raise HTTPException(
            status_code=500,
            detail="Error al crear el pedido"
        )

# Buscar pedidos
@app.get(
    "/pedidos/buscar",
    response_model=PedidoBusquedaResponse
)
def buscar_pedidos(
    numero_pedido: Optional[int] = None,
    cliente_id: Optional[int] = None,
    estado: Optional[EstadoPedidoEnum] = None,
    orden: Optional[str] = "asc",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    if (
        numero_pedido is None
        and cliente_id is None
        and estado is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un criterio de búsqueda"
        )

    if numero_pedido is not None and numero_pedido < 1:
        raise HTTPException(
            status_code=400,
            detail="El número de pedido debe ser mayor que cero"
        )

    if cliente_id is not None and cliente_id < 1:
        raise HTTPException(
            status_code=400,
            detail="El número de cliente debe ser mayor que cero"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="El límite debe estar entre 1 y 100"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="El offset no puede ser negativo"
        )

    if orden not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="El orden debe ser 'asc' o 'desc'"
        )

    consulta = db.query(Pedido)

    if numero_pedido is not None:
        consulta = consulta.filter(
            Pedido.id == numero_pedido
        )

    if cliente_id is not None:
        consulta = consulta.filter(
            Pedido.cliente_id == cliente_id
        )

    if estado is not None:
        consulta = consulta.filter(
            Pedido.estado == estado.value
        )

    total = consulta.count()

    if orden == "asc":
        consulta = consulta.order_by(
            Pedido.fecha_pedido.asc()
        )
    else:
        consulta = consulta.order_by(
            Pedido.fecha_pedido.desc()
        )

    pedidos = consulta.limit(limit).offset(offset).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "resultados": pedidos
    }

# Obtener un pedido específico
@app.get(
    "/pedidos/{pedido_id}",
    response_model=PedidoResponse
)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    return pedido

# Obtener todos los pedidos
@app.get(
    "/pedidos",
    response_model=list[PedidoResponse]
)
def obtener_pedidos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista",
            "jefe_carpinteros",
            "carpintero"
        )
    )
):
    pedidos = db.query(Pedido).all()

    return pedidos

# Actualizar estado de un pedido
@app.put(
    "/pedidos/{pedido_id}/estado",
    response_model=PedidoResponse
)
def actualizar_estado_pedido(
    pedido_id: int,
    datos: PedidoEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_roles(
            "administrador",
            "recepcionista"
        )
    )
):
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    transiciones_validas = {
        "pendiente": [
            "cancelado"
        ],
        "asignado": [],
        "en_produccion": [],
        "terminado": [
            "cliente_avisado"
        ],
        "cliente_avisado": [
            "retirado_por_cliente"
        ],
        "retirado_por_cliente": [],
        "cancelado": []
    }

    estado_actual = pedido.estado
    nuevo_estado = datos.estado.value

    estados_permitidos = transiciones_validas.get(
        estado_actual
    )

    if estados_permitidos is None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"El pedido posee un estado desconocido: "
                f"'{estado_actual}'"
            )
        )

    if nuevo_estado not in estados_permitidos:
        raise HTTPException(
            status_code=400,
            detail=(
                f"No se puede cambiar un pedido de "
                f"'{estado_actual}' a '{nuevo_estado}'"
            )
        )

    pedido.estado = nuevo_estado

    db.commit()
    db.refresh(pedido)

    return pedido

# Eliminar un pedido
@app.delete("/pedidos/{pedido_id}")
def eliminar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(
        require_role("administrador")
    )
):
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    if pedido.estado != "pendiente":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden eliminar pedidos pendientes"
        )

    db.query(PedidoProducto).filter(
        PedidoProducto.pedido_id == pedido_id
    ).delete()

    db.delete(pedido)
    db.commit()

    return {
        "mensaje": "Pedido eliminado correctamente"
    }