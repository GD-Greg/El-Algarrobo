# El Algarrobo

Sistema web de gestión para una fábrica de muebles.

Permite administrar muebles, clientes, empleados y pedidos, además de
organizar el trabajo de los carpinteros y registrar el avance de la
producción.

## Tecnologías utilizadas

### Backend

- Python 3.14
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT
- Passlib y bcrypt
- Pytest

### Frontend

- HTML
- CSS
- JavaScript
- LocalStorage
- Fetch API

## Funcionalidades

- Inicio de sesión mediante usuario y contraseña.
- CAPTCHA con vencimiento y uso único.
- Autenticación mediante JWT.
- Autorización según roles.
- Gestión de usuarios.
- ABM de muebles.
- ABM de clientes.
- ABM de empleados.
- Creación y seguimiento de pedidos.
- Búsqueda de muebles por código o número de pedido.
- Asignación de carpinteros a los muebles solicitados.
- Selección separada de carpinteros de armado y labrado.
- Control de disponibilidad de carpinteros.
- Registro de unidades terminadas.
- Finalización automática de asignaciones y pedidos.
- Aviso al cliente y registro del retiro.
- Estadísticas de pedidos por estado.
- Búsquedas, ordenamiento y paginación.
- Pruebas automatizadas del backend.

## Roles

### Administrador

Puede:

- Gestionar usuarios.
- Crear, consultar, modificar y eliminar muebles.
- Crear, consultar, modificar y eliminar clientes.
- Crear, consultar, modificar y eliminar empleados.
- Crear y consultar pedidos.
- Cancelar y eliminar pedidos pendientes.
- Crear asignaciones de trabajo.
- Iniciar la producción.
- Registrar unidades terminadas.
- Avisar al cliente y registrar el retiro.
- Consultar estadísticas.

### Recepcionista

Puede:

- Crear, consultar y modificar clientes.
- Crear y consultar pedidos.
- Cancelar pedidos pendientes.
- Avisar al cliente.
- Registrar el retiro del pedido.

No puede gestionar muebles, empleados, usuarios ni asignaciones.

### Jefe de carpinteros

Puede:

- Consultar muebles y pedidos.
- Consultar empleados.
- Crear y buscar asignaciones de trabajo.
- Consultar notas de producción.

No puede modificar empleados ni registrar unidades terminadas.

### Carpintero

Puede:

- Consultar muebles y pedidos.
- Consultar sus trabajos desde Asignaciones.
- Iniciar la producción.
- Registrar unidades terminadas.
- Consultar notas de producción.

## Estados de un pedido

El flujo normal es:

```text
Pendiente
→ Asignado
→ En producción
→ Terminado
→ Cliente avisado
→ Retirado por el cliente
```

Un pedido pendiente también puede pasar a:

```text
Pendiente → Cancelado
```

Los estados `Asignado`, `En producción` y `Terminado` se actualizan
automáticamente mediante las asignaciones y notas de producción.

## Estructura principal

```text
CasoMuebles/
├── backend/
│   ├── models/
│   ├── schemas/
│   ├── tests/
│   ├── crear_admin.py
│   ├── database.py
│   ├── main.py
│   ├── security.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── css/
│   ├── js/
│   ├── asignaciones.html
│   ├── clientes.html
│   ├── dashboard.html
│   ├── empleados.html
│   ├── login.html
│   ├── notas-produccion.html
│   ├── pedidos.html
│   └── productos.html
└── README.md
```

## Instalación del backend

Abrir PowerShell en la carpeta `backend`.

Crear el entorno virtual:

```powershell
python -m venv venv
```

Activarlo:

```powershell
.\venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Configuración del entorno

Crear `.env` a partir de `.env.example`:

```powershell
Copy-Item .env.example .env
```

Abrir `.env` y reemplazar la clave de ejemplo por una clave propia:

```env
SECRET_KEY=UNA_CLAVE_SECRETA_LARGA_Y_ALEATORIA
DATABASE_URL=sqlite:///./el_algarrobo.db
```

El archivo `.env` no debe publicarse en repositorios.

## Crear el primer administrador

Si se utiliza una base de datos nueva, ejecutar:

```powershell
python crear_admin.py
```

El programa solicitará los datos necesarios para crear el administrador inicial.

## Ejecutar el backend

Desde `backend`, con el entorno virtual activado:

```powershell
uvicorn main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva estará disponible en:

```text
http://127.0.0.1:8000/docs
```

## Ejecutar el frontend

1. Abrir la carpeta del proyecto en Visual Studio Code.
2. Buscar `frontend/login.html`.
3. Hacer clic derecho sobre el archivo.
4. Seleccionar **Open with Live Server**.

La dirección dependerá de la carpeta utilizada como raíz por Live Server.
Normalmente será una de estas:

```text
http://127.0.0.1:5500/login.html
```

```text
http://127.0.0.1:5500/frontend/login.html
```

## Ejecutar las pruebas

Desde `backend`, con el entorno virtual activado:

```powershell
python -m pytest -q
```

Resultado esperado:

```text
94 passed
```

Las pruebas utilizan una base de datos SQLite temporal y no modifican la base de datos principal.

## Seguridad

- Las contraseñas se guardan con hash bcrypt.
- Los tokens JWT tienen vencimiento.
- El CAPTCHA vence después de dos minutos.
- Cada CAPTCHA puede utilizarse una sola vez.
- Los endpoints verifican el rol en el backend.
- El frontend oculta acciones no permitidas según el rol.
- La clave JWT se configura mediante variables de entorno.

## Ejecución local

El sistema está preparado para ejecutarse localmente con FastAPI y Live Server.
