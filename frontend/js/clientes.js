const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

const clientesTableBody = document.getElementById(
    "clientes-table-body"
);

const clientesMensaje = document.getElementById(
    "clientes-mensaje"
);

const busquedaForm = document.getElementById(
    "busqueda-clientes-form"
);

const buscarNombre = document.getElementById("buscar-nombre");
const buscarApellido = document.getElementById(
    "buscar-apellido"
);
const buscarTelefono = document.getElementById(
    "buscar-telefono"
);
const buscarOrden = document.getElementById("buscar-orden");

const limpiarBusquedaButton = document.getElementById(
    "limpiar-busqueda-button"
);

const nuevoClienteButton = document.getElementById(
    "nuevo-cliente-button"
);

const accionesHeader = document.getElementById(
    "acciones-header"
);

const enlaceEmpleados = document.getElementById(
    "enlace-empleados"
);

const logoutButton = document.getElementById("logout-button");

const clienteModal = document.getElementById("cliente-modal");
const clienteModalTitle = document.getElementById(
    "cliente-modal-title"
);

const cerrarModalButton = document.getElementById(
    "cerrar-modal-button"
);

const cancelarClienteButton = document.getElementById(
    "cancelar-cliente-button"
);

const clienteForm = document.getElementById("cliente-form");
const clienteFormError = document.getElementById(
    "cliente-form-error"
);

const clienteId = document.getElementById("cliente-id");
const clienteNombre = document.getElementById(
    "cliente-nombre"
);
const clienteApellido = document.getElementById(
    "cliente-apellido"
);
const clienteDomicilio = document.getElementById(
    "cliente-domicilio"
);
const clienteTelefono = document.getElementById(
    "cliente-telefono"
);
const clienteTarjeta = document.getElementById(
    "cliente-tarjeta"
);
const clienteNumeroTarjeta = document.getElementById(
    "cliente-numero-tarjeta"
);
const clienteCuentaBancaria = document.getElementById(
    "cliente-cuenta-bancaria"
);
const clienteCodigoBanco = document.getElementById(
    "cliente-codigo-banco"
);

const guardarClienteButton = clienteForm.querySelector(
    'button[type="submit"]'
);

let esAdministrador = false;
let puedeGestionarClientes = false;


function cerrarSesion() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("usuario_rol");
    window.location.replace("login.html");
}


function mostrarMensaje(texto, tipo = "") {
    clientesMensaje.textContent = texto;
    clientesMensaje.className = "page-message";

    if (tipo !== "") {
        clientesMensaje.classList.add(tipo);
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


function enmascararNumero(valor) {
    const texto = String(valor ?? "");

    if (texto.length <= 4) {
        return texto;
    }

    return `•••• ${texto.slice(-4)}`;
}


function mostrarClientes(clientes) {
    clientesTableBody.innerHTML = "";

    if (clientes.length === 0) {
        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.colSpan = puedeGestionarClientes ? 10 : 9;
        celda.textContent = "No se encontraron clientes";
        celda.className = "empty-table-message";

        fila.appendChild(celda);
        clientesTableBody.appendChild(fila);

        return;
    }

    for (const cliente of clientes) {
        const fila = document.createElement("tr");

        const valores = [
            cliente.id,
            cliente.nombre,
            cliente.apellido,
            cliente.domicilio,
            cliente.telefono,
            cliente.tarjeta_credito,
            enmascararNumero(cliente.numero_tarjeta),
            enmascararNumero(
                cliente.numero_cuenta_bancaria
            ),
            cliente.codigo_banco
        ];

        for (const valor of valores) {
            const celda = document.createElement("td");
            celda.textContent = valor;
            fila.appendChild(celda);
        }

        if (puedeGestionarClientes) {
            const accionesCelda =
                document.createElement("td");

            accionesCelda.className = "table-actions";

            const editarButton =
                document.createElement("button");

            editarButton.type = "button";
            editarButton.textContent = "Editar";
            editarButton.className = "edit-button";
            editarButton.dataset.action = "editar";
            editarButton.dataset.id = cliente.id;

            accionesCelda.appendChild(editarButton);

            if (esAdministrador) {
                const eliminarButton =
                    document.createElement("button");

                eliminarButton.type = "button";
                eliminarButton.textContent = "Eliminar";
                eliminarButton.className = "delete-button";
                eliminarButton.dataset.action = "eliminar";
                eliminarButton.dataset.id = cliente.id;

                accionesCelda.appendChild(eliminarButton);
            }

            fila.appendChild(accionesCelda);
        }

        clientesTableBody.appendChild(fila);
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

    esAdministrador =
        usuario.rol === "administrador";

    puedeGestionarClientes = [
        "administrador",
        "recepcionista"
    ].includes(usuario.rol);

    if (!puedeGestionarClientes) {
        window.location.replace("dashboard.html");
        return false;
    }

    localStorage.setItem("usuario_rol", usuario.rol);

    nuevoClienteButton.hidden = false;
    accionesHeader.hidden = false;

    if (esAdministrador) {
        enlaceEmpleados.hidden = false;
    }

    return true;
}


async function cargarClientes() {
    try {
        mostrarMensaje("Cargando clientes...");

        const respuesta = await fetch(
            `${API_URL}/clientes`,
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
                "No se pudieron cargar los clientes"
            );
        }

        const clientes = await respuesta.json();

        mostrarClientes(clientes);
        mostrarMensaje("");
    } catch (error) {
        mostrarClientes([]);
        mostrarMensaje(error.message, "error");
    }
}


async function buscarClientes(event) {
    event.preventDefault();

    const nombre = buscarNombre.value.trim();
    const apellido = buscarApellido.value.trim();
    const telefono = buscarTelefono.value.trim();

    if (
        nombre === ""
        && apellido === ""
        && telefono === ""
    ) {
        await cargarClientes();
        return;
    }

    const parametros = new URLSearchParams();

    if (nombre !== "") {
        parametros.append("nombre", nombre);
    }

    if (apellido !== "") {
        parametros.append("apellido", apellido);
    }

    if (telefono !== "") {
        parametros.append("telefono", telefono);
    }

    parametros.append("orden", buscarOrden.value);

    try {
        mostrarMensaje("Buscando clientes...");

        const respuesta = await fetch(
            `${API_URL}/clientes/buscar?${parametros}`,
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

        mostrarClientes(datos.resultados);

        mostrarMensaje(
            `Se encontraron ${datos.total} clientes`,
            "success"
        );
    } catch (error) {
        mostrarClientes([]);
        mostrarMensaje(error.message, "error");
    }
}


async function limpiarBusqueda() {
    busquedaForm.reset();
    await cargarClientes();
}


function abrirModalNuevoCliente() {
    if (!puedeGestionarClientes) {
        return;
    }

    clienteForm.reset();
    clienteId.value = "";
    clienteFormError.textContent = "";
    clienteModalTitle.textContent = "Nuevo cliente";
    clienteModal.hidden = false;

    clienteNombre.focus();
}


function cerrarModalCliente() {
    clienteModal.hidden = true;
    clienteForm.reset();
    clienteId.value = "";
    clienteFormError.textContent = "";
}


async function abrirModalEditarCliente(
    clienteIdSeleccionado
) {
    if (!puedeGestionarClientes) {
        return;
    }

    try {
        const respuesta = await fetch(
            `${API_URL}/clientes/${clienteIdSeleccionado}`,
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

        const cliente = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                obtenerMensajeError(
                    cliente,
                    "No se pudo cargar el cliente"
                )
            );
        }

        clienteId.value = cliente.id;
        clienteNombre.value = cliente.nombre;
        clienteApellido.value = cliente.apellido;
        clienteDomicilio.value = cliente.domicilio;
        clienteTelefono.value = cliente.telefono;
        clienteTarjeta.value =
            cliente.tarjeta_credito;
        clienteNumeroTarjeta.value =
            cliente.numero_tarjeta;
        clienteCuentaBancaria.value =
            cliente.numero_cuenta_bancaria;
        clienteCodigoBanco.value =
            cliente.codigo_banco;

        clienteFormError.textContent = "";
        clienteModalTitle.textContent =
            "Editar cliente";

        clienteModal.hidden = false;
        clienteNombre.focus();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


async function guardarCliente(event) {
    event.preventDefault();

    if (!puedeGestionarClientes) {
        return;
    }

    clienteFormError.textContent = "";

    const datosCliente = {
        nombre: clienteNombre.value.trim(),
        apellido: clienteApellido.value.trim(),
        domicilio: clienteDomicilio.value.trim(),
        telefono: clienteTelefono.value.trim(),
        tarjeta_credito: clienteTarjeta.value.trim(),
        numero_tarjeta:
            clienteNumeroTarjeta.value.trim(),
        numero_cuenta_bancaria:
            clienteCuentaBancaria.value.trim(),
        codigo_banco:
            clienteCodigoBanco.value.trim()
    };

    const id = clienteId.value;
    const editando = id !== "";

    const url = editando
        ? `${API_URL}/clientes/${id}`
        : `${API_URL}/clientes`;

    const metodo = editando ? "PUT" : "POST";

    try {
        guardarClienteButton.disabled = true;
        guardarClienteButton.textContent =
            "Guardando...";

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(datosCliente)
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
                    "No se pudo guardar el cliente"
                )
            );
        }

        cerrarModalCliente();
        await cargarClientes();

        const accion = editando
            ? "actualizado"
            : "creado";

        mostrarMensaje(
            `Cliente "${datos.nombre} ${datos.apellido}" ` +
            `${accion} correctamente`,
            "success"
        );
    } catch (error) {
        clienteFormError.textContent = error.message;
    } finally {
        guardarClienteButton.disabled = false;
        guardarClienteButton.textContent = "Guardar";
    }
}


async function eliminarCliente(
    clienteIdSeleccionado
) {
    if (!esAdministrador) {
        return;
    }

    const confirmado = window.confirm(
        "¿Seguro que querés eliminar este cliente?"
    );

    if (!confirmado) {
        return;
    }

    try {
        const respuesta = await fetch(
            `${API_URL}/clientes/${clienteIdSeleccionado}`,
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
                    "No se pudo eliminar el cliente"
                )
            );
        }

        await cargarClientes();
        mostrarMensaje(datos.mensaje, "success");
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


async function iniciarPagina() {
    try {
        const usuarioValido = await validarUsuario();

        if (!usuarioValido) {
            return;
        }

        await cargarClientes();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


busquedaForm.addEventListener(
    "submit",
    buscarClientes
);

limpiarBusquedaButton.addEventListener(
    "click",
    limpiarBusqueda
);

nuevoClienteButton.addEventListener(
    "click",
    abrirModalNuevoCliente
);

cerrarModalButton.addEventListener(
    "click",
    cerrarModalCliente
);

cancelarClienteButton.addEventListener(
    "click",
    cerrarModalCliente
);

clienteForm.addEventListener(
    "submit",
    guardarCliente
);

clientesTableBody.addEventListener(
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
            abrirModalEditarCliente(id);
        }

        if (boton.dataset.action === "eliminar") {
            eliminarCliente(id);
        }
    }
);

clienteModal.addEventListener(
    "click",
    function (event) {
        if (event.target === clienteModal) {
            cerrarModalCliente();
        }
    }
);

logoutButton.addEventListener(
    "click",
    cerrarSesion
);

iniciarPagina();