const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

const usuarioNombre = document.getElementById("usuario-nombre");
const usuarioRol = document.getElementById("usuario-rol");
const dashboardError = document.getElementById("dashboard-error");

const adminDashboard = document.getElementById("admin-dashboard");
const personalDashboard = document.getElementById(
    "personal-dashboard"
);

const personalTitulo = document.getElementById("personal-titulo");
const personalMensaje = document.getElementById(
    "personal-mensaje"
);

const enlaceProductos = document.getElementById(
    "enlace-productos"
);
const enlaceClientes = document.getElementById(
    "enlace-clientes"
);
const enlacePedidos = document.getElementById(
    "enlace-pedidos"
);
const enlaceEmpleados = document.getElementById(
    "enlace-empleados"
);

const logoutButton = document.getElementById("logout-button");


const nombresRoles = {
    administrador: "Administrador",
    recepcionista: "Recepcionista",
    jefe_carpinteros: "Jefe de carpinteros",
    carpintero: "Carpintero"
};


const mensajesRoles = {
    recepcionista: (
        "Desde este panel podés gestionar clientes y pedidos, " +
        "avisar que un pedido está terminado y registrar su retiro."
    ),
    jefe_carpinteros: (
        "Desde este panel podés consultar pedidos y carpinteros, " +
        "y organizar las asignaciones de producción."
    ),
    carpintero: (
        "Desde este panel podés consultar los trabajos asignados, " +
        "iniciar su producción y registrar las unidades terminadas."
    )
};


function cerrarSesion() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("usuario_rol");
    window.location.replace("login.html");
}


function mostrarUsuario(datos) {
    usuarioNombre.textContent = datos.usuario;
    usuarioRol.textContent =
        nombresRoles[datos.rol] ?? datos.rol;

    localStorage.setItem("usuario_rol", datos.rol);
}


function mostrarNavegacion(rol) {
    enlaceProductos.hidden = false;
    enlacePedidos.hidden = false;

    if (rol === "administrador") {
        enlaceClientes.hidden = false;
        enlaceEmpleados.hidden = false;
        return;
    }

    if (rol === "recepcionista") {
        enlaceClientes.hidden = false;
        return;
    }

    if (rol === "jefe_carpinteros") {
        enlaceEmpleados.hidden = false;
    }
}


async function cargarEstadisticas() {
    const respuesta = await fetch(
        `${API_URL}/admin/estadisticas`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    if (respuesta.status === 401) {
        cerrarSesion();
        return;
    }

    if (!respuesta.ok) {
        throw new Error(
            "No se pudieron cargar las estadísticas"
        );
    }

    const estadisticas = await respuesta.json();

    document.getElementById("total-pedidos").textContent =
        estadisticas.total_pedidos;

    document.getElementById("pedidos-pendientes").textContent =
        estadisticas.pendientes;

    document.getElementById("pedidos-asignados").textContent =
        estadisticas.asignados;

    document.getElementById(
        "pedidos-en-produccion"
    ).textContent = estadisticas.en_produccion;

    document.getElementById("pedidos-terminados").textContent =
        estadisticas.terminados;

    document.getElementById(
        "pedidos-clientes-avisados"
    ).textContent = estadisticas.clientes_avisados;

    document.getElementById("pedidos-retirados").textContent =
        estadisticas.retirados_por_cliente;

    document.getElementById("pedidos-cancelados").textContent =
        estadisticas.cancelados;
}


async function cargarAdministrador(respuesta) {
    const datos = await respuesta.json();

    mostrarUsuario(datos);
    mostrarNavegacion(datos.rol);

    document.getElementById("total-usuarios").textContent =
        datos.resumen.total_usuarios;

    document.getElementById("total-productos").textContent =
        datos.resumen.total_muebles;

    adminDashboard.hidden = false;

    await cargarEstadisticas();
}


async function cargarPersonal() {
    const respuesta = await fetch(`${API_URL}/staff`, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    if (respuesta.status === 401) {
        cerrarSesion();
        return;
    }

    if (!respuesta.ok) {
        throw new Error(
            "No se pudo cargar la información del usuario"
        );
    }

    const datos = await respuesta.json();

    mostrarUsuario(datos);
    mostrarNavegacion(datos.rol);

    personalTitulo.textContent =
        nombresRoles[datos.rol] ?? "Área del personal";

    personalMensaje.textContent =
        mensajesRoles[datos.rol] ??
        "Bienvenido al panel de El Algarrobo.";

    personalDashboard.hidden = false;
}


async function cargarDashboard() {
    if (token === null) {
        cerrarSesion();
        return;
    }

    try {
        dashboardError.textContent = "";

        const respuestaAdmin = await fetch(`${API_URL}/admin`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (respuestaAdmin.status === 401) {
            cerrarSesion();
            return;
        }

        if (respuestaAdmin.ok) {
            await cargarAdministrador(respuestaAdmin);
            return;
        }

        if (respuestaAdmin.status === 403) {
            await cargarPersonal();
            return;
        }

        throw new Error(
            "No se pudo cargar el panel principal"
        );
    } catch (error) {
        usuarioNombre.textContent = "Sin conexión";
        usuarioRol.textContent = "";
        dashboardError.textContent = error.message;
    }
}


logoutButton.addEventListener("click", cerrarSesion);

cargarDashboard();