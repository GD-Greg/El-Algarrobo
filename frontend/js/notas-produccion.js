const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem(
    "access_token"
);

const tablaBody = document.getElementById(
    "notas-table-body"
);

const mensaje = document.getElementById(
    "notas-mensaje"
);

const busquedaForm = document.getElementById(
    "busqueda-notas-form"
);

const buscarNumeroNota = document.getElementById(
    "buscar-numero-nota"
);

const buscarNumeroPedido = document.getElementById(
    "buscar-numero-pedido"
);

const buscarCodigoMueble = document.getElementById(
    "buscar-codigo-mueble"
);

const buscarCodigoCarpintero =
    document.getElementById(
        "buscar-codigo-carpintero"
    );

const buscarOrden = document.getElementById(
    "buscar-orden"
);

const limpiarBusquedaButton =
    document.getElementById(
        "limpiar-busqueda-button"
    );

const nuevaNotaButton = document.getElementById(
    "nueva-nota-button"
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

const modal = document.getElementById(
    "nota-modal"
);

const cerrarModalButton = document.getElementById(
    "cerrar-modal-button"
);

const cancelarNotaButton = document.getElementById(
    "cancelar-nota-button"
);

const notaForm = document.getElementById(
    "nota-form"
);

const notaAsignacion = document.getElementById(
    "nota-asignacion"
);

const notaAsignacionInfo =
    document.getElementById(
        "nota-asignacion-info"
    );

const notaPedidoInfo = document.getElementById(
    "nota-pedido-info"
);

const notaMuebleInfo = document.getElementById(
    "nota-mueble-info"
);

const notaProgresoInfo = document.getElementById(
    "nota-progreso-info"
);

const formError = document.getElementById(
    "nota-form-error"
);

const guardarButton = notaForm.querySelector(
    'button[type="submit"]'
);

let rolActual = "";
let puedeRegistrar = false;

let asignaciones = [];
let pedidos = [];
let muebles = [];
let empleados = [];
let todasNotas = [];


function cerrarSesion() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("usuario_rol");

    window.location.replace("login.html");
}


function mostrarMensaje(texto, tipo = "") {
    mensaje.textContent = texto;
    mensaje.className = "page-message";

    if (tipo !== "") {
        mensaje.classList.add(tipo);
    }
}


function obtenerMensajeError(
    datos,
    predeterminado
) {
    if (typeof datos.detail === "string") {
        return datos.detail;
    }

    if (Array.isArray(datos.detail)) {
        return datos.detail
            .map(error => error.msg)
            .join(", ");
    }

    return predeterminado;
}


async function solicitarJson(
    url,
    opciones = {}
) {
    const respuesta = await fetch(url, {
        ...opciones,

        headers: {
            Authorization: `Bearer ${token}`,
            ...(opciones.headers || {})
        }
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


function formatearFecha(fecha) {
    if (!fecha) {
        return "—";
    }

    return new Date(fecha).toLocaleString(
        "es-AR"
    );
}


function obtenerMueble(muebleId) {
    return muebles.find(
        item => item.id === Number(muebleId)
    );
}


function obtenerEmpleado(empleadoId) {
    return empleados.find(
        item => item.id === Number(empleadoId)
    );
}


function nombreMueble(muebleId) {
    const mueble = obtenerMueble(muebleId);

    if (mueble === undefined) {
        return `Mueble #${muebleId}`;
    }

    return (
        `${mueble.codigo} — ` +
        `${mueble.descripcion}`
    );
}


function nombreCarpintero(carpinteroId) {
    const empleado = obtenerEmpleado(
        carpinteroId
    );

    if (empleado === undefined) {
        return `Carpintero #${carpinteroId}`;
    }

    return (
        `${empleado.codigo} — ` +
        `${empleado.nombre} ` +
        `${empleado.apellido}`
    );
}


function obtenerAsignacion(asignacionId) {
    return asignaciones.find(
        item =>
            item.id === Number(asignacionId)
    );
}


function obtenerDatosRenglon(
    pedidoProductoId
) {
    for (const pedido of pedidos) {
        const renglon = pedido.productos.find(
            producto =>
                producto.id ===
                Number(pedidoProductoId)
        );

        if (renglon !== undefined) {
            return {
                pedido: pedido,
                renglon: renglon
            };
        }
    }

    return null;
}


function ordenarNotas(lista, orden) {
    return [...lista].sort(
        (notaA, notaB) => {
            const fechaA = new Date(
                notaA.fecha_entrega
            ).getTime();

            const fechaB = new Date(
                notaB.fecha_entrega
            ).getTime();

            if (orden === "asc") {
                return fechaA - fechaB;
            }

            return fechaB - fechaA;
        }
    );
}


function mostrarNotas(lista) {
    tablaBody.innerHTML = "";

    if (lista.length === 0) {
        const fila =
            document.createElement("tr");

        const celda =
            document.createElement("td");

        celda.colSpan = 6;

        celda.textContent =
            "No se encontraron notas " +
            "de producción";

        celda.className =
            "empty-table-message";

        fila.appendChild(celda);
        tablaBody.appendChild(fila);

        return;
    }

    for (const nota of lista) {
        const fila =
            document.createElement("tr");

        const numeroCelda =
            document.createElement("td");

        numeroCelda.textContent = nota.id;

        const pedidoCelda =
            document.createElement("td");

        pedidoCelda.textContent =
            `Pedido #${nota.pedido_id}`;

        const muebleCelda =
            document.createElement("td");

        muebleCelda.textContent =
            nombreMueble(nota.mueble_id);

        const unidadCelda =
            document.createElement("td");

        unidadCelda.textContent =
            `Unidad ${nota.numero_unidad}`;

        const carpinteroCelda =
            document.createElement("td");

        carpinteroCelda.textContent =
            nombreCarpintero(
                nota.carpintero_id
            );

        const fechaCelda =
            document.createElement("td");

        fechaCelda.textContent =
            formatearFecha(
                nota.fecha_entrega
            );

        fila.appendChild(numeroCelda);
        fila.appendChild(pedidoCelda);
        fila.appendChild(muebleCelda);
        fila.appendChild(unidadCelda);
        fila.appendChild(carpinteroCelda);
        fila.appendChild(fechaCelda);

        tablaBody.appendChild(fila);
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

    const rolesPermitidos = [
        "administrador",
        "jefe_carpinteros",
        "carpintero"
    ];

    if (
        !rolesPermitidos.includes(rolActual)
    ) {
        window.location.replace(
            "dashboard.html"
        );

        return false;
    }

    puedeRegistrar = [
        "administrador",
        "carpintero"
    ].includes(rolActual);

    nuevaNotaButton.hidden =
        !puedeRegistrar;

    enlaceClientes.hidden =
        rolActual !== "administrador";

    enlaceEmpleados.hidden = ![
        "administrador",
        "jefe_carpinteros"
    ].includes(rolActual);

    return true;
}


async function cargarDatosRelacionados() {
    const solicitudes = [
        solicitarJson(
            `${API_URL}/asignaciones`
        ),

        solicitarJson(
            `${API_URL}/pedidos`
        ),

        solicitarJson(
            `${API_URL}/muebles`
        )
    ];

    if (
        [
            "administrador",
            "jefe_carpinteros"
        ].includes(rolActual)
    ) {
        solicitudes.push(
            solicitarJson(
                `${API_URL}/empleados`
            )
        );
    }

    const resultados = await Promise.all(
        solicitudes
    );

    asignaciones = resultados[0];
    pedidos = resultados[1];
    muebles = resultados[2];
    empleados = resultados[3] || [];
}


async function cargarNotas(
    orden = "desc"
) {
    try {
        mostrarMensaje(
            "Cargando notas de producción..."
        );

        todasNotas = await solicitarJson(
            `${API_URL}/notas-produccion`
        );

        mostrarNotas(
            ordenarNotas(
                todasNotas,
                orden
            )
        );

        mostrarMensaje("");
    } catch (error) {
        mostrarNotas([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


async function buscarNotas(event) {
    event.preventDefault();

    const numeroNota =
        buscarNumeroNota.value.trim();

    const numeroPedido =
        buscarNumeroPedido.value.trim();

    const codigoMueble =
        buscarCodigoMueble.value.trim();

    const codigoCarpintero =
        buscarCodigoCarpintero.value.trim();

    const orden = buscarOrden.value;

    if (
        numeroNota === "" &&
        numeroPedido === "" &&
        codigoMueble === "" &&
        codigoCarpintero === ""
    ) {
        mostrarNotas(
            ordenarNotas(
                todasNotas,
                orden
            )
        );

        mostrarMensaje("");

        return;
    }

    const parametros =
        new URLSearchParams();

    if (numeroNota !== "") {
        parametros.append(
            "numero_nota",
            numeroNota
        );
    }

    if (numeroPedido !== "") {
        parametros.append(
            "numero_pedido",
            numeroPedido
        );
    }

    if (codigoMueble !== "") {
        parametros.append(
            "codigo_mueble",
            codigoMueble
        );
    }

    if (codigoCarpintero !== "") {
        parametros.append(
            "codigo_carpintero",
            codigoCarpintero
        );
    }

    parametros.append("orden", orden);

    try {
        mostrarMensaje(
            "Buscando notas de producción..."
        );

        const datos = await solicitarJson(
            `${API_URL}/notas-produccion/buscar?` +
            parametros.toString()
        );

        mostrarNotas(datos.resultados);

        mostrarMensaje(
            `Se encontraron ${datos.total} nota(s)`,
            "success"
        );
    } catch (error) {
        mostrarNotas([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


function limpiarBusqueda() {
    busquedaForm.reset();

    mostrarNotas(
        ordenarNotas(
            todasNotas,
            "desc"
        )
    );

    mostrarMensaje("");
}


function cantidadTerminada(asignacionId) {
    return todasNotas.filter(
        nota =>
            nota.asignacion_id ===
            Number(asignacionId)
    ).length;
}


function llenarAsignacionesEnProduccion() {
    notaAsignacion.innerHTML =
        '<option value="">' +
        "Seleccionar asignación" +
        "</option>";

    for (const asignacion of asignaciones) {
        if (
            asignacion.estado !==
            "en_produccion"
        ) {
            continue;
        }

        const datos = obtenerDatosRenglon(
            asignacion.pedido_producto_id
        );

        if (datos === null) {
            continue;
        }

        const terminadas =
            cantidadTerminada(
                asignacion.id
            );

        const cantidadTotal =
            datos.renglon.cantidad;

        if (
            terminadas >= cantidadTotal
        ) {
            continue;
        }

        const mueble = obtenerMueble(
            datos.renglon.mueble_id
        );

        const codigo = mueble !== undefined
            ? mueble.codigo
            : `Mueble #${datos.renglon.mueble_id}`;

        const opcion =
            document.createElement("option");

        opcion.value = asignacion.id;

        opcion.textContent =
            `Asignación #${asignacion.id} — ` +
            `Pedido #${datos.pedido.id} — ` +
            `${codigo} ` +
            `(${terminadas}/${cantidadTotal})`;

        notaAsignacion.appendChild(opcion);
    }
}


function ocultarInformacion() {
    notaAsignacionInfo.hidden = true;

    notaPedidoInfo.textContent = "";
    notaMuebleInfo.textContent = "";
    notaProgresoInfo.textContent = "";
}


function mostrarInformacionAsignacion() {
    ocultarInformacion();

    if (notaAsignacion.value === "") {
        return;
    }

    const asignacion = obtenerAsignacion(
        Number(notaAsignacion.value)
    );

    if (asignacion === undefined) {
        return;
    }

    const datos = obtenerDatosRenglon(
        asignacion.pedido_producto_id
    );

    if (datos === null) {
        return;
    }

    const terminadas =
        cantidadTerminada(
            asignacion.id
        );

    notaPedidoInfo.textContent =
        `Pedido: #${datos.pedido.id}`;

    notaMuebleInfo.textContent =
        "Mueble: " +
        nombreMueble(
            datos.renglon.mueble_id
        );

    notaProgresoInfo.textContent =
        `Progreso: ${terminadas} de ` +
        `${datos.renglon.cantidad} ` +
        "unidades terminadas";

    notaAsignacionInfo.hidden = false;
}


function abrirModal() {
    if (!puedeRegistrar) {
        return;
    }

    notaForm.reset();

    formError.textContent = "";

    ocultarInformacion();
    llenarAsignacionesEnProduccion();

    modal.hidden = false;

    notaAsignacion.focus();
}


function cerrarModal() {
    modal.hidden = true;

    notaForm.reset();

    formError.textContent = "";

    ocultarInformacion();
}


async function guardarNota(event) {
    event.preventDefault();

    formError.textContent = "";

    if (
        notaAsignacion.value === ""
    ) {
        formError.textContent =
            "Seleccioná una asignación " +
            "en producción";

        return;
    }

    try {
        guardarButton.disabled = true;

        guardarButton.textContent =
            "Registrando...";

        const nota = await solicitarJson(
            `${API_URL}/notas-produccion`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    asignacion_id:
                        Number(
                            notaAsignacion.value
                        )
                })
            }
        );

        cerrarModal();

        await cargarDatosRelacionados();

        await cargarNotas(
            buscarOrden.value
        );

        mostrarMensaje(
            `Nota #${nota.id}: unidad ` +
            `${nota.numero_unidad} ` +
            "registrada correctamente",
            "success"
        );
    } catch (error) {
        formError.textContent =
            error.message;
    } finally {
        guardarButton.disabled = false;

        guardarButton.textContent =
            "Registrar unidad";
    }
}


busquedaForm.addEventListener(
    "submit",
    buscarNotas
);

limpiarBusquedaButton.addEventListener(
    "click",
    limpiarBusqueda
);

nuevaNotaButton.addEventListener(
    "click",
    abrirModal
);

cerrarModalButton.addEventListener(
    "click",
    cerrarModal
);

cancelarNotaButton.addEventListener(
    "click",
    cerrarModal
);

notaAsignacion.addEventListener(
    "change",
    mostrarInformacionAsignacion
);

notaForm.addEventListener(
    "submit",
    guardarNota
);

logoutButton.addEventListener(
    "click",
    cerrarSesion
);


modal.addEventListener(
    "click",
    function (event) {
        if (event.target === modal) {
            cerrarModal();
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
        await cargarNotas("desc");
    } catch (error) {
        mostrarNotas([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


iniciarPagina();