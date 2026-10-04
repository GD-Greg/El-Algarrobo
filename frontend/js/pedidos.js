const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

const pedidosTableBody = document.getElementById(
    "pedidos-table-body"
);

const pedidosMensaje = document.getElementById(
    "pedidos-mensaje"
);

const busquedaForm = document.getElementById(
    "busqueda-pedidos-form"
);

const buscarNumeroPedido = document.getElementById(
    "buscar-numero-pedido"
);

const buscarClienteId = document.getElementById(
    "buscar-cliente-id"
);

const buscarEstado = document.getElementById(
    "buscar-estado"
);

const buscarOrden = document.getElementById(
    "buscar-orden"
);

const limpiarBusquedaButton = document.getElementById(
    "limpiar-busqueda-button"
);

const nuevoPedidoButton = document.getElementById(
    "nuevo-pedido-button"
);

const accionesHeader = document.getElementById(
    "acciones-header"
);

const enlaceClientes = document.getElementById(
    "enlace-clientes"
);

const enlaceEmpleados = document.getElementById(
    "enlace-empleados"
);

const logoutButton = document.getElementById(
    "logout-button"
);

const pedidoModal = document.getElementById(
    "pedido-modal"
);

const cerrarModalButton = document.getElementById(
    "cerrar-modal-button"
);

const cancelarPedidoButton = document.getElementById(
    "cancelar-pedido-button"
);

const pedidoForm = document.getElementById(
    "pedido-form"
);

const pedidoCliente = document.getElementById(
    "pedido-cliente"
);

const pedidoFechaEstimada = document.getElementById(
    "pedido-fecha-estimada"
);

const pedidoSenia = document.getElementById(
    "pedido-senia"
);

const pedidoProductosContainer = document.getElementById(
    "pedido-productos-container"
);

const agregarProductoButton = document.getElementById(
    "agregar-producto-button"
);

const pedidoFormError = document.getElementById(
    "pedido-form-error"
);

const guardarPedidoButton = pedidoForm.querySelector(
    'button[type="submit"]'
);

let rolActual = "";
let esAdministrador = false;
let puedeGestionarPedidos = false;

let clientes = [];
let muebles = [];

let contadorFilasMueble = 0;

const nombresEstados = {
    pendiente: "Pendiente",
    asignado: "Asignado",
    en_produccion: "En producción",
    terminado: "Terminado",
    cliente_avisado: "Cliente avisado",
    retirado_por_cliente: "Retirado por el cliente",
    cancelado: "Cancelado"
};


function cerrarSesion() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("usuario_rol");

    window.location.replace("login.html");
}


function mostrarMensaje(texto, tipo = "") {
    pedidosMensaje.textContent = texto;
    pedidosMensaje.className = "page-message";

    if (tipo !== "") {
        pedidosMensaje.classList.add(tipo);
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


async function solicitarJson(url, opciones = {}) {
    const headers = {
        Authorization: `Bearer ${token}`,
        ...(opciones.headers || {})
    };

    const respuesta = await fetch(url, {
        ...opciones,
        headers: headers
    });

    if (respuesta.status === 401) {
        cerrarSesion();

        throw new Error("La sesión expiró");
    }

    let datos = {};

    try {
        datos = await respuesta.json();
    } catch (error) {
        datos = {};
    }

    if (!respuesta.ok) {
        throw new Error(
            obtenerMensajeError(
                datos,
                "Ocurrió un error inesperado"
            )
        );
    }

    return datos;
}


function fechaLocalActual() {
    const hoy = new Date();

    const anio = hoy.getFullYear();

    const mes = String(
        hoy.getMonth() + 1
    ).padStart(2, "0");

    const dia = String(
        hoy.getDate()
    ).padStart(2, "0");

    return `${anio}-${mes}-${dia}`;
}


function formatearFecha(fecha) {
    if (!fecha) {
        return "—";
    }

    const partes = fecha
        .slice(0, 10)
        .split("-");

    if (partes.length !== 3) {
        return fecha;
    }

    return (
        `${partes[2]}/${partes[1]}/${partes[0]}`
    );
}


function formatearFechaHora(fecha) {
    if (!fecha) {
        return "—";
    }

    return new Date(fecha).toLocaleString(
        "es-AR"
    );
}


function formatearDinero(valor) {
    return new Intl.NumberFormat(
        "es-AR",
        {
            style: "currency",
            currency: "ARS",
            minimumFractionDigits: 2
        }
    ).format(Number(valor));
}


function obtenerNombreCliente(clienteId) {
    const cliente = clientes.find(
        item => item.id === Number(clienteId)
    );

    if (cliente === undefined) {
        return `Cliente #${clienteId}`;
    }

    return (
        `${cliente.nombre} ${cliente.apellido}`
    );
}


function obtenerMueble(muebleId) {
    return muebles.find(
        item => item.id === Number(muebleId)
    );
}


function obtenerNombreMueble(muebleId) {
    const mueble = obtenerMueble(muebleId);

    if (mueble === undefined) {
        return `Mueble #${muebleId}`;
    }

    return (
        `${mueble.codigo} — ${mueble.descripcion}`
    );
}


function crearBotonAccion(
    texto,
    clase,
    accion,
    pedidoId,
    estado = ""
) {
    const boton = document.createElement("button");

    boton.type = "button";
    boton.textContent = texto;
    boton.className = clase;

    boton.dataset.action = accion;
    boton.dataset.id = pedidoId;

    if (estado !== "") {
        boton.dataset.estado = estado;
    }

    return boton;
}


function agregarAccionesPedido(celda, pedido) {
    let tieneAcciones = false;

    if (pedido.estado === "pendiente") {
        const cancelarButton = crearBotonAccion(
            "Cancelar",
            "secondary-button",
            "cambiar-estado",
            pedido.id,
            "cancelado"
        );

        celda.appendChild(cancelarButton);

        tieneAcciones = true;

        if (esAdministrador) {
            const eliminarButton = crearBotonAccion(
                "Eliminar",
                "delete-button",
                "eliminar",
                pedido.id
            );

            celda.appendChild(eliminarButton);
        }
    } else if (pedido.estado === "terminado") {
        const avisarButton = crearBotonAccion(
            "Avisar cliente",
            "primary-button",
            "cambiar-estado",
            pedido.id,
            "cliente_avisado"
        );

        celda.appendChild(avisarButton);

        tieneAcciones = true;
    } else if (
        pedido.estado === "cliente_avisado"
    ) {
        const retiroButton = crearBotonAccion(
            "Registrar retiro",
            "primary-button",
            "cambiar-estado",
            pedido.id,
            "retirado_por_cliente"
        );

        celda.appendChild(retiroButton);

        tieneAcciones = true;
    }

    if (!tieneAcciones) {
        const texto = document.createElement("span");

        texto.textContent = "Sin acciones";
        texto.className = "no-actions";

        celda.appendChild(texto);
    }
}


function mostrarPedidos(listaPedidos) {
    pedidosTableBody.innerHTML = "";

    if (listaPedidos.length === 0) {
        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.colSpan = puedeGestionarPedidos
            ? 8
            : 7;

        celda.textContent =
            "No se encontraron pedidos";

        celda.className =
            "empty-table-message";

        fila.appendChild(celda);
        pedidosTableBody.appendChild(fila);

        return;
    }

    for (const pedido of listaPedidos) {
        const fila = document.createElement("tr");

        const numeroCelda =
            document.createElement("td");

        numeroCelda.textContent = pedido.id;

        const clienteCelda =
            document.createElement("td");

        clienteCelda.textContent =
            obtenerNombreCliente(
                pedido.cliente_id
            );

        const fechaPedidoCelda =
            document.createElement("td");

        fechaPedidoCelda.textContent =
            formatearFechaHora(
                pedido.fecha_pedido
            );

        const entregaCelda =
            document.createElement("td");

        entregaCelda.textContent =
            formatearFecha(
                pedido.fecha_estimada_entrega
            );

        const seniaCelda =
            document.createElement("td");

        seniaCelda.textContent =
            formatearDinero(pedido.senia);

        const estadoCelda =
            document.createElement("td");

        const estado =
            document.createElement("span");

        estado.textContent =
            nombresEstados[pedido.estado] ||
            pedido.estado;

        estado.className =
            `status-badge status-${pedido.estado}`;

        estadoCelda.appendChild(estado);

        const mueblesCelda =
            document.createElement("td");

        const mueblesLista =
            document.createElement("ul");

        mueblesLista.className =
            "productos-list";

        for (const producto of pedido.productos) {
            const item =
                document.createElement("li");

            item.textContent =
                `${obtenerNombreMueble(
                    producto.mueble_id
                )} × ${producto.cantidad}`;

            mueblesLista.appendChild(item);
        }

        mueblesCelda.appendChild(mueblesLista);

        fila.appendChild(numeroCelda);
        fila.appendChild(clienteCelda);
        fila.appendChild(fechaPedidoCelda);
        fila.appendChild(entregaCelda);
        fila.appendChild(seniaCelda);
        fila.appendChild(estadoCelda);
        fila.appendChild(mueblesCelda);

        if (puedeGestionarPedidos) {
            const accionesCelda =
                document.createElement("td");

            accionesCelda.className =
                "table-actions";

            agregarAccionesPedido(
                accionesCelda,
                pedido
            );

            fila.appendChild(accionesCelda);
        }

        pedidosTableBody.appendChild(fila);
    }
}


async function validarUsuario() {
    if (token === null) {
        cerrarSesion();

        return false;
    }

    const usuario = await solicitarJson(
        `${API_URL}/staff`
    );

    rolActual = usuario.rol;

    esAdministrador =
        rolActual === "administrador";

    puedeGestionarPedidos = (
        esAdministrador ||
        rolActual === "recepcionista"
    );

    nuevoPedidoButton.hidden =
        !puedeGestionarPedidos;

    accionesHeader.hidden =
        !puedeGestionarPedidos;

    if (enlaceClientes !== null) {
        enlaceClientes.hidden =
            !puedeGestionarPedidos;
    }

    if (enlaceEmpleados !== null) {
        enlaceEmpleados.hidden = !(
            esAdministrador ||
            rolActual === "jefe_carpinteros"
        );
    }

    return true;
}


function llenarSelectClientes() {
    pedidoCliente.innerHTML =
        '<option value="">' +
        "Seleccionar cliente" +
        "</option>";

    for (const cliente of clientes) {
        const opcion =
            document.createElement("option");

        opcion.value = cliente.id;

        opcion.textContent =
            `${cliente.nombre} ` +
            `${cliente.apellido} ` +
            `(ID: ${cliente.id})`;

        pedidoCliente.appendChild(opcion);
    }
}


async function cargarDatosRelacionados() {
    muebles = await solicitarJson(
        `${API_URL}/muebles`
    );

    if (puedeGestionarPedidos) {
        clientes = await solicitarJson(
            `${API_URL}/clientes`
        );

        llenarSelectClientes();
    }
}


function ordenarPedidos(
    listaPedidos,
    orden
) {
    return [...listaPedidos].sort(
        (pedidoA, pedidoB) => {
            const fechaA = new Date(
                pedidoA.fecha_pedido
            ).getTime();

            const fechaB = new Date(
                pedidoB.fecha_pedido
            ).getTime();

            if (orden === "asc") {
                return fechaA - fechaB;
            }

            return fechaB - fechaA;
        }
    );
}


async function cargarPedidos(
    orden = "desc"
) {
    try {
        mostrarMensaje(
            "Cargando pedidos..."
        );

        const datos = await solicitarJson(
            `${API_URL}/pedidos`
        );

        mostrarPedidos(
            ordenarPedidos(datos, orden)
        );

        mostrarMensaje("");
    } catch (error) {
        mostrarPedidos([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


async function buscarPedidos(event) {
    event.preventDefault();

    const numeroPedido =
        buscarNumeroPedido.value.trim();

    const clienteId =
        buscarClienteId.value.trim();

    const estado = buscarEstado.value;
    const orden = buscarOrden.value;

    if (
        numeroPedido === "" &&
        clienteId === "" &&
        estado === ""
    ) {
        await cargarPedidos(orden);

        return;
    }

    const parametros =
        new URLSearchParams();

    if (numeroPedido !== "") {
        parametros.append(
            "numero_pedido",
            numeroPedido
        );
    }

    if (clienteId !== "") {
        parametros.append(
            "cliente_id",
            clienteId
        );
    }

    if (estado !== "") {
        parametros.append(
            "estado",
            estado
        );
    }

    parametros.append("orden", orden);

    try {
        mostrarMensaje(
            "Buscando pedidos..."
        );

        const datos = await solicitarJson(
            `${API_URL}/pedidos/buscar?` +
            parametros.toString()
        );

        mostrarPedidos(datos.resultados);

        mostrarMensaje(
            `Se encontraron ` +
            `${datos.total} pedido(s)`,
            "success"
        );
    } catch (error) {
        mostrarPedidos([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


async function limpiarBusqueda() {
    busquedaForm.reset();

    await cargarPedidos("desc");
}


function agregarFilaMueble() {
    contadorFilasMueble++;

    const fila =
        document.createElement("div");

    fila.className =
        "pedido-producto-row";

    const muebleGroup =
        document.createElement("div");

    muebleGroup.className = "form-group";

    const muebleLabel =
        document.createElement("label");

    muebleLabel.textContent = "Mueble";

    const muebleSelect =
        document.createElement("select");

    muebleSelect.className =
        "pedido-producto-select";

    muebleSelect.required = true;

    muebleSelect.id =
        `pedido-mueble-${contadorFilasMueble}`;

    muebleLabel.htmlFor =
        muebleSelect.id;

    const opcionInicial =
        document.createElement("option");

    opcionInicial.value = "";

    opcionInicial.textContent =
        "Seleccionar mueble";

    muebleSelect.appendChild(
        opcionInicial
    );

    for (const mueble of muebles) {
        const opcion =
            document.createElement("option");

        opcion.value = mueble.id;

        opcion.textContent =
            `${mueble.codigo} — ` +
            `${formatearDinero(
                mueble.precio
            )}`;

        muebleSelect.appendChild(opcion);
    }

    muebleGroup.appendChild(
        muebleLabel
    );

    muebleGroup.appendChild(
        muebleSelect
    );

    const cantidadGroup =
        document.createElement("div");

    cantidadGroup.className =
        "form-group";

    const cantidadLabel =
        document.createElement("label");

    cantidadLabel.textContent =
        "Cantidad";

    const cantidadInput =
        document.createElement("input");

    cantidadInput.type = "number";

    cantidadInput.className =
        "pedido-producto-cantidad";

    cantidadInput.min = "1";
    cantidadInput.step = "1";
    cantidadInput.value = "1";
    cantidadInput.required = true;

    cantidadInput.id =
        `pedido-cantidad-${contadorFilasMueble}`;

    cantidadLabel.htmlFor =
        cantidadInput.id;

    cantidadGroup.appendChild(
        cantidadLabel
    );

    cantidadGroup.appendChild(
        cantidadInput
    );

    const quitarButton =
        document.createElement("button");

    quitarButton.type = "button";
    quitarButton.textContent = "Quitar";
    quitarButton.className = "delete-button";

    quitarButton.addEventListener(
        "click",
        function () {
            if (
                pedidoProductosContainer
                    .children.length === 1
            ) {
                pedidoFormError.textContent =
                    "El pedido debe contener " +
                    "al menos un mueble";

                return;
            }

            fila.remove();

            pedidoFormError.textContent = "";
        }
    );

    fila.appendChild(muebleGroup);
    fila.appendChild(cantidadGroup);
    fila.appendChild(quitarButton);

    pedidoProductosContainer.appendChild(
        fila
    );
}


function abrirModalNuevoPedido() {
    if (!puedeGestionarPedidos) {
        return;
    }

    pedidoForm.reset();

    pedidoProductosContainer.innerHTML = "";
    pedidoFormError.textContent = "";
    contadorFilasMueble = 0;

    const hoy = fechaLocalActual();

    pedidoFechaEstimada.min = hoy;
    pedidoFechaEstimada.value = hoy;

    pedidoSenia.value = "0";

    agregarFilaMueble();

    pedidoModal.hidden = false;

    pedidoCliente.focus();
}


function cerrarModalPedido() {
    pedidoModal.hidden = true;

    pedidoForm.reset();

    pedidoProductosContainer.innerHTML = "";
    pedidoFormError.textContent = "";
}


function obtenerMueblesDelFormulario() {
    const filas =
        pedidoProductosContainer.querySelectorAll(
            ".pedido-producto-row"
        );

    if (filas.length === 0) {
        throw new Error(
            "Debés agregar al menos un mueble"
        );
    }

    const productos = [];
    const idsSeleccionados = new Set();

    let totalPedido = 0;

    for (const fila of filas) {
        const select = fila.querySelector(
            ".pedido-producto-select"
        );

        const inputCantidad =
            fila.querySelector(
                ".pedido-producto-cantidad"
            );

        const muebleId =
            Number(select.value);

        const cantidad =
            Number(inputCantidad.value);

        if (
            select.value === "" ||
            !Number.isInteger(cantidad) ||
            cantidad < 1
        ) {
            throw new Error(
                "Revisá los muebles " +
                "y sus cantidades"
            );
        }

        if (
            idsSeleccionados.has(muebleId)
        ) {
            throw new Error(
                "No podés agregar el mismo " +
                "mueble más de una vez"
            );
        }

        const mueble =
            obtenerMueble(muebleId);

        if (mueble === undefined) {
            throw new Error(
                "Uno de los muebles ya no existe"
            );
        }

        idsSeleccionados.add(muebleId);

        totalPedido +=
            Number(mueble.precio) *
            cantidad;

        productos.push({
            mueble_id: muebleId,
            cantidad: cantidad
        });
    }

    return {
        productos: productos,
        totalPedido: totalPedido
    };
}


async function guardarPedido(event) {
    event.preventDefault();

    pedidoFormError.textContent = "";

    try {
        if (pedidoCliente.value === "") {
            throw new Error(
                "Seleccioná un cliente"
            );
        }

        if (
            pedidoFechaEstimada.value === ""
        ) {
            throw new Error(
                "Seleccioná la fecha " +
                "estimada de entrega"
            );
        }

        if (
            pedidoFechaEstimada.value <
            fechaLocalActual()
        ) {
            throw new Error(
                "La fecha estimada no puede " +
                "estar en el pasado"
            );
        }

        const senia =
            Number(pedidoSenia.value);

        if (
            !Number.isFinite(senia) ||
            senia < 0
        ) {
            throw new Error(
                "La seña no puede ser negativa"
            );
        }

        const resultado =
            obtenerMueblesDelFormulario();

        if (
            senia > resultado.totalPedido
        ) {
            throw new Error(
                "La seña no puede superar " +
                "el total del pedido " +
                `(${formatearDinero(
                    resultado.totalPedido
                )})`
            );
        }

        const datosPedido = {
            cliente_id:
                Number(pedidoCliente.value),

            fecha_estimada_entrega:
                pedidoFechaEstimada.value,

            senia: senia,

            productos:
                resultado.productos
        };

        guardarPedidoButton.disabled = true;

        guardarPedidoButton.textContent =
            "Creando...";

        const pedidoCreado =
            await solicitarJson(
                `${API_URL}/pedidos`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        datosPedido
                    )
                }
            );

        cerrarModalPedido();

        await cargarPedidos(
            buscarOrden.value
        );

        mostrarMensaje(
            `Pedido #${pedidoCreado.id} ` +
            "creado correctamente",
            "success"
        );
    } catch (error) {
        pedidoFormError.textContent =
            error.message;
    } finally {
        guardarPedidoButton.disabled = false;

        guardarPedidoButton.textContent =
            "Crear pedido";
    }
}


async function cambiarEstadoPedido(
    pedidoId,
    nuevoEstado
) {
    const confirmaciones = {
        cancelado:
            "¿Querés cancelar este pedido?",

        cliente_avisado:
            "¿Confirmás que el cliente " +
            "fue avisado?",

        retirado_por_cliente:
            "¿Confirmás que el cliente " +
            "retiró el pedido?"
    };

    const confirmado = window.confirm(
        confirmaciones[nuevoEstado]
    );

    if (!confirmado) {
        return;
    }

    try {
        await solicitarJson(
            `${API_URL}/pedidos/` +
            `${pedidoId}/estado`,
            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    estado: nuevoEstado
                })
            }
        );

        await cargarPedidos(
            buscarOrden.value
        );

        mostrarMensaje(
            "Estado actualizado correctamente",
            "success"
        );
    } catch (error) {
        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


async function eliminarPedido(pedidoId) {
    const confirmado = window.confirm(
        "¿Querés eliminar este pedido " +
        "pendiente? Esta acción no se " +
        "puede deshacer."
    );

    if (!confirmado) {
        return;
    }

    try {
        await solicitarJson(
            `${API_URL}/pedidos/${pedidoId}`,
            {
                method: "DELETE"
            }
        );

        await cargarPedidos(
            buscarOrden.value
        );

        mostrarMensaje(
            "Pedido eliminado correctamente",
            "success"
        );
    } catch (error) {
        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


pedidosTableBody.addEventListener(
    "click",
    async function (event) {
        const boton = event.target.closest(
            "button[data-action]"
        );

        if (boton === null) {
            return;
        }

        const pedidoId =
            Number(boton.dataset.id);

        if (
            boton.dataset.action ===
            "cambiar-estado"
        ) {
            await cambiarEstadoPedido(
                pedidoId,
                boton.dataset.estado
            );
        } else if (
            boton.dataset.action ===
            "eliminar"
        ) {
            await eliminarPedido(pedidoId);
        }
    }
);


nuevoPedidoButton.addEventListener(
    "click",
    abrirModalNuevoPedido
);

agregarProductoButton.addEventListener(
    "click",
    agregarFilaMueble
);

cerrarModalButton.addEventListener(
    "click",
    cerrarModalPedido
);

cancelarPedidoButton.addEventListener(
    "click",
    cerrarModalPedido
);

pedidoForm.addEventListener(
    "submit",
    guardarPedido
);

busquedaForm.addEventListener(
    "submit",
    buscarPedidos
);

limpiarBusquedaButton.addEventListener(
    "click",
    limpiarBusqueda
);

logoutButton.addEventListener(
    "click",
    cerrarSesion
);


pedidoModal.addEventListener(
    "click",
    function (event) {
        if (event.target === pedidoModal) {
            cerrarModalPedido();
        }
    }
);


async function iniciarPagina() {
    try {
        const usuarioValido =
            await validarUsuario();

        if (!usuarioValido) {
            return;
        }

        await cargarDatosRelacionados();
        await cargarPedidos("desc");
    } catch (error) {
        mostrarPedidos([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


iniciarPagina();