const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

const empleadosTableBody = document.getElementById(
    "empleados-table-body"
);
const empleadosMensaje = document.getElementById(
    "empleados-mensaje"
);
const busquedaForm = document.getElementById(
    "busqueda-empleados-form"
);

const buscarCodigo = document.getElementById("buscar-codigo");
const buscarNombre = document.getElementById("buscar-nombre");
const buscarApellido = document.getElementById(
    "buscar-apellido"
);
const buscarPuesto = document.getElementById("buscar-puesto");
const buscarTipoCarpintero = document.getElementById(
    "buscar-tipo-carpintero"
);
const buscarDisponible = document.getElementById(
    "buscar-disponible"
);
const buscarActivo = document.getElementById("buscar-activo");
const buscarOrden = document.getElementById("buscar-orden");

const limpiarBusquedaButton = document.getElementById(
    "limpiar-busqueda-button"
);
const nuevoEmpleadoButton = document.getElementById(
    "nuevo-empleado-button"
);
const accionesHeader = document.getElementById(
    "acciones-header"
);
const enlaceClientes = document.getElementById(
    "enlace-clientes"
);
const logoutButton = document.getElementById("logout-button");

const empleadoModal = document.getElementById(
    "empleado-modal"
);
const empleadoModalTitle = document.getElementById(
    "empleado-modal-title"
);
const cerrarModalButton = document.getElementById(
    "cerrar-modal-button"
);
const cancelarEmpleadoButton = document.getElementById(
    "cancelar-empleado-button"
);

const empleadoForm = document.getElementById("empleado-form");
const empleadoFormError = document.getElementById(
    "empleado-form-error"
);

const empleadoId = document.getElementById("empleado-id");
const empleadoCodigo = document.getElementById(
    "empleado-codigo"
);
const empleadoNombre = document.getElementById(
    "empleado-nombre"
);
const empleadoApellido = document.getElementById(
    "empleado-apellido"
);
const empleadoEmail = document.getElementById(
    "empleado-email"
);
const empleadoTelefono = document.getElementById(
    "empleado-telefono"
);
const empleadoPuesto = document.getElementById(
    "empleado-puesto"
);
const empleadoTipoCarpintero = document.getElementById(
    "empleado-tipo-carpintero"
);
const empleadoEspecialidad = document.getElementById(
    "empleado-especialidad"
);
const empleadoDisponible = document.getElementById(
    "empleado-disponible"
);
const empleadoActivo = document.getElementById(
    "empleado-activo"
);

const grupoTipoCarpintero = document.getElementById(
    "grupo-tipo-carpintero"
);
const grupoEspecialidad = document.getElementById(
    "grupo-especialidad-labrado"
);
const grupoDisponible = document.getElementById(
    "grupo-disponible"
);

const guardarEmpleadoButton = empleadoForm.querySelector(
    'button[type="submit"]'
);

const nombresPuestos = {
    administrador: "Administrador",
    recepcionista: "Recepcionista",
    jefe_carpinteros: "Jefe de carpinteros",
    carpintero: "Carpintero"
};

const nombresTipos = {
    armado: "Armado",
    labrado: "Labrado"
};

let esAdministrador = false;


function cerrarSesion() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("usuario_rol");
    window.location.replace("login.html");
}


function mostrarMensaje(texto, tipo = "") {
    empleadosMensaje.textContent = texto;
    empleadosMensaje.className = "page-message";

    if (tipo !== "") {
        empleadosMensaje.classList.add(tipo);
    }
}


function obtenerMensajeError(
    datos,
    mensajePredeterminado
) {
    if (typeof datos.detail === "string") {
        return datos.detail;
    }

    if (Array.isArray(datos.detail)) {
        return datos.detail
            .map(error => error.msg)
            .join(", ");
    }

    return mensajePredeterminado;
}


function actualizarCamposCarpintero() {
    const esCarpintero =
        empleadoPuesto.value === "carpintero";

    grupoTipoCarpintero.hidden = !esCarpintero;
    grupoDisponible.hidden = !esCarpintero;
    empleadoTipoCarpintero.required = esCarpintero;

    if (!esCarpintero) {
        empleadoTipoCarpintero.value = "";
        empleadoEspecialidad.value = "";
        empleadoDisponible.value = "false";
    }

    const esLabrado = (
        esCarpintero
        && empleadoTipoCarpintero.value === "labrado"
    );

    grupoEspecialidad.hidden = !esLabrado;
    empleadoEspecialidad.required = esLabrado;

    if (!esLabrado) {
        empleadoEspecialidad.value = "";
    }
}


function mostrarEmpleados(empleados) {
    empleadosTableBody.innerHTML = "";

    if (empleados.length === 0) {
        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.colSpan = esAdministrador ? 11 : 10;
        celda.textContent = "No se encontraron empleados";
        celda.className = "empty-table-message";

        fila.appendChild(celda);
        empleadosTableBody.appendChild(fila);
        return;
    }

    for (const empleado of empleados) {
        const fila = document.createElement("tr");

        const disponibilidad = (
            empleado.puesto === "carpintero"
                ? (empleado.disponible ? "Sí" : "No")
                : "No aplica"
        );

        const valores = [
            empleado.id,
            empleado.codigo,
            `${empleado.nombre} ${empleado.apellido}`,
            empleado.email,
            empleado.telefono,
            nombresPuestos[empleado.puesto]
                ?? empleado.puesto,
            empleado.tipo_carpintero
                ? nombresTipos[empleado.tipo_carpintero]
                : "No aplica",
            empleado.especialidad_labrado ?? "No aplica",
            disponibilidad
        ];

        for (const valor of valores) {
            const celda = document.createElement("td");
            celda.textContent = valor;
            fila.appendChild(celda);
        }

        const estadoCelda = document.createElement("td");
        const estado = document.createElement("span");

        estado.textContent = empleado.activo
            ? "Activo"
            : "Inactivo";

        estado.className = empleado.activo
            ? "status-badge active-status"
            : "status-badge inactive-status";

        estadoCelda.appendChild(estado);
        fila.appendChild(estadoCelda);

        if (esAdministrador) {
            const accionesCelda =
                document.createElement("td");

            accionesCelda.className = "table-actions";

            const editarButton =
                document.createElement("button");

            editarButton.type = "button";
            editarButton.textContent = "Editar";
            editarButton.className = "edit-button";
            editarButton.dataset.action = "editar";
            editarButton.dataset.id = empleado.id;

            const eliminarButton =
                document.createElement("button");

            eliminarButton.type = "button";
            eliminarButton.textContent = "Eliminar";
            eliminarButton.className = "delete-button";
            eliminarButton.dataset.action = "eliminar";
            eliminarButton.dataset.id = empleado.id;

            accionesCelda.appendChild(editarButton);
            accionesCelda.appendChild(eliminarButton);
            fila.appendChild(accionesCelda);
        }

        empleadosTableBody.appendChild(fila);
    }
}


async function validarUsuario() {
    if (token === null) {
        cerrarSesion();
        return false;
    }

    const respuesta = await fetch(`${API_URL}/staff`, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    if (respuesta.status === 401) {
        cerrarSesion();
        return false;
    }

    if (!respuesta.ok) {
        throw new Error(
            "No se pudo verificar el usuario actual"
        );
    }

    const usuario = await respuesta.json();

    const puedeConsultar = [
        "administrador",
        "jefe_carpinteros"
    ].includes(usuario.rol);

    if (!puedeConsultar) {
        window.location.replace("dashboard.html");
        return false;
    }

    esAdministrador =
        usuario.rol === "administrador";

    localStorage.setItem("usuario_rol", usuario.rol);

    if (esAdministrador) {
        enlaceClientes.hidden = false;
        nuevoEmpleadoButton.hidden = false;
        accionesHeader.hidden = false;
    }

    return true;
}


async function cargarEmpleados() {
    try {
        mostrarMensaje("Cargando empleados...");

        const respuesta = await fetch(
            `${API_URL}/empleados`,
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

        if (respuesta.status === 403) {
            window.location.replace("dashboard.html");
            return;
        }

        if (!respuesta.ok) {
            throw new Error(
                "No se pudieron cargar los empleados"
            );
        }

        const empleados = await respuesta.json();

        mostrarEmpleados(empleados);
        mostrarMensaje("");
    } catch (error) {
        mostrarEmpleados([]);
        mostrarMensaje(error.message, "error");
    }
}


async function buscarEmpleados(event) {
    event.preventDefault();

    const filtros = {
        codigo: buscarCodigo.value.trim(),
        nombre: buscarNombre.value.trim(),
        apellido: buscarApellido.value.trim(),
        puesto: buscarPuesto.value,
        tipo_carpintero: buscarTipoCarpintero.value,
        disponible: buscarDisponible.value,
        activo: buscarActivo.value
    };

    const sinFiltros = Object.values(filtros).every(
        valor => valor === ""
    );

    if (sinFiltros) {
        await cargarEmpleados();
        return;
    }

    const parametros = new URLSearchParams();

    for (const [clave, valor] of Object.entries(filtros)) {
        if (valor !== "") {
            parametros.append(clave, valor);
        }
    }

    parametros.append("orden", buscarOrden.value);

    try {
        mostrarMensaje("Buscando empleados...");

        const respuesta = await fetch(
            `${API_URL}/empleados/buscar?${parametros}`,
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

        if (respuesta.status === 403) {
            window.location.replace("dashboard.html");
            return;
        }

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                obtenerMensajeError(
                    datos,
                    "No se pudo realizar la búsqueda"
                )
            );
        }

        mostrarEmpleados(datos.resultados);

        mostrarMensaje(
            `Se encontraron ${datos.total} empleados`,
            "success"
        );
    } catch (error) {
        mostrarEmpleados([]);
        mostrarMensaje(error.message, "error");
    }
}


async function limpiarBusqueda() {
    busquedaForm.reset();
    await cargarEmpleados();
}


function abrirModalNuevoEmpleado() {
    if (!esAdministrador) {
        return;
    }

    empleadoForm.reset();
    empleadoId.value = "";
    empleadoActivo.value = "true";
    empleadoDisponible.value = "true";
    empleadoFormError.textContent = "";

    actualizarCamposCarpintero();

    empleadoModalTitle.textContent = "Nuevo empleado";
    empleadoModal.hidden = false;
    empleadoCodigo.focus();
}


function cerrarModalEmpleado() {
    empleadoModal.hidden = true;
    empleadoForm.reset();
    empleadoId.value = "";
    empleadoFormError.textContent = "";
    actualizarCamposCarpintero();
}


async function abrirModalEditarEmpleado(
    empleadoIdSeleccionado
) {
    if (!esAdministrador) {
        return;
    }

    try {
        const respuesta = await fetch(
            `${API_URL}/empleados/${empleadoIdSeleccionado}`,
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

        const empleado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                obtenerMensajeError(
                    empleado,
                    "No se pudo cargar el empleado"
                )
            );
        }

        empleadoId.value = empleado.id;
        empleadoCodigo.value = empleado.codigo;
        empleadoNombre.value = empleado.nombre;
        empleadoApellido.value = empleado.apellido;
        empleadoEmail.value = empleado.email;
        empleadoTelefono.value = empleado.telefono;
        empleadoPuesto.value = empleado.puesto;
        empleadoTipoCarpintero.value =
            empleado.tipo_carpintero ?? "";

        actualizarCamposCarpintero();

        empleadoEspecialidad.value =
            empleado.especialidad_labrado ?? "";

        empleadoDisponible.value =
            String(empleado.disponible);

        empleadoActivo.value =
            String(empleado.activo);

        empleadoFormError.textContent = "";
        empleadoModalTitle.textContent =
            "Editar empleado";

        empleadoModal.hidden = false;
        empleadoCodigo.focus();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


async function guardarEmpleado(event) {
    event.preventDefault();

    if (!esAdministrador) {
        return;
    }

    empleadoFormError.textContent = "";

    const esCarpintero =
        empleadoPuesto.value === "carpintero";

    const esLabrado = (
        esCarpintero
        && empleadoTipoCarpintero.value === "labrado"
    );

    const datosEmpleado = {
        codigo: empleadoCodigo.value.trim(),
        nombre: empleadoNombre.value.trim(),
        apellido: empleadoApellido.value.trim(),
        email: empleadoEmail.value.trim(),
        telefono: empleadoTelefono.value.trim(),
        puesto: empleadoPuesto.value,
        tipo_carpintero: esCarpintero
            ? empleadoTipoCarpintero.value
            : null,
        especialidad_labrado: esLabrado
            ? empleadoEspecialidad.value.trim()
            : null,
        disponible: esCarpintero
            ? empleadoDisponible.value === "true"
            : false,
        activo: empleadoActivo.value === "true"
    };

    const id = empleadoId.value;
    const editando = id !== "";

    const url = editando
        ? `${API_URL}/empleados/${id}`
        : `${API_URL}/empleados`;

    const metodo = editando ? "PUT" : "POST";

    try {
        guardarEmpleadoButton.disabled = true;
        guardarEmpleadoButton.textContent =
            "Guardando...";

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(datosEmpleado)
        });

        const datos = await respuesta.json();

        if (respuesta.status === 401) {
            cerrarSesion();
            return;
        }

        if (!respuesta.ok) {
            throw new Error(
                obtenerMensajeError(
                    datos,
                    "No se pudo guardar el empleado"
                )
            );
        }

        cerrarModalEmpleado();
        await cargarEmpleados();

        const accion = editando
            ? "actualizado"
            : "creado";

        mostrarMensaje(
            `Empleado "${datos.codigo}" ${accion} correctamente`,
            "success"
        );
    } catch (error) {
        empleadoFormError.textContent = error.message;
    } finally {
        guardarEmpleadoButton.disabled = false;
        guardarEmpleadoButton.textContent = "Guardar";
    }
}


async function eliminarEmpleado(
    empleadoIdSeleccionado
) {
    if (!esAdministrador) {
        return;
    }

    const confirmado = window.confirm(
        "¿Seguro que querés eliminar este empleado?"
    );

    if (!confirmado) {
        return;
    }

    try {
        const respuesta = await fetch(
            `${API_URL}/empleados/${empleadoIdSeleccionado}`,
            {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
        );

        const datos = await respuesta.json();

        if (respuesta.status === 401) {
            cerrarSesion();
            return;
        }

        if (!respuesta.ok) {
            throw new Error(
                obtenerMensajeError(
                    datos,
                    "No se pudo eliminar el empleado"
                )
            );
        }

        await cargarEmpleados();
        mostrarMensaje(datos.mensaje, "success");
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


empleadoPuesto.addEventListener(
    "change",
    actualizarCamposCarpintero
);

empleadoTipoCarpintero.addEventListener(
    "change",
    actualizarCamposCarpintero
);

busquedaForm.addEventListener(
    "submit",
    buscarEmpleados
);

limpiarBusquedaButton.addEventListener(
    "click",
    limpiarBusqueda
);

nuevoEmpleadoButton.addEventListener(
    "click",
    abrirModalNuevoEmpleado
);

cerrarModalButton.addEventListener(
    "click",
    cerrarModalEmpleado
);

cancelarEmpleadoButton.addEventListener(
    "click",
    cerrarModalEmpleado
);

empleadoForm.addEventListener(
    "submit",
    guardarEmpleado
);

empleadosTableBody.addEventListener(
    "click",
    function (event) {
        const boton = event.target.closest(
            "button[data-action]"
        );

        if (boton === null) {
            return;
        }

        const id = Number(boton.dataset.id);

        if (boton.dataset.action === "editar") {
            abrirModalEditarEmpleado(id);
        }

        if (boton.dataset.action === "eliminar") {
            eliminarEmpleado(id);
        }
    }
);

empleadoModal.addEventListener(
    "click",
    function (event) {
        if (event.target === empleadoModal) {
            cerrarModalEmpleado();
        }
    }
);

logoutButton.addEventListener(
    "click",
    cerrarSesion
);


async function iniciarPagina() {
    try {
        const usuarioValido = await validarUsuario();

        if (!usuarioValido) {
            return;
        }

        await cargarEmpleados();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


iniciarPagina();