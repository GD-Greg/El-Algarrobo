const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

const tablaBody = document.getElementById(
    "asignaciones-table-body"
);

const mensaje = document.getElementById(
    "asignaciones-mensaje"
);

const busquedaForm = document.getElementById(
    "busqueda-asignaciones-form"
);

const buscarPedidoId = document.getElementById(
    "buscar-pedido-id"
);

const buscarCarpinteroId = document.getElementById(
    "buscar-carpintero-id"
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

const nuevaAsignacionButton = document.getElementById(
    "nueva-asignacion-button"
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

const modal = document.getElementById(
    "asignacion-modal"
);

const cerrarModalButton = document.getElementById(
    "cerrar-modal-button"
);

const cancelarButton = document.getElementById(
    "cancelar-asignacion-button"
);

const asignacionForm = document.getElementById(
    "asignacion-form"
);

const asignacionPedido = document.getElementById(
    "asignacion-pedido"
);

const asignacionRenglon = document.getElementById(
    "asignacion-renglon"
);

const carpinteroArmado = document.getElementById(
    "carpintero-armado"
);

const grupoCarpinteroLabrado = document.getElementById(
    "grupo-carpintero-labrado"
);

const carpinteroLabrado = document.getElementById(
    "carpintero-labrado"
);

const formError = document.getElementById(
    "asignacion-form-error"
);

const guardarButton = asignacionForm.querySelector(
    'button[type="submit"]'
);

let rolActual = "";
let puedeCrear = false;
let puedeIniciar = false;

let pedidos = [];
let muebles = [];
let empleados = [];
let todasAsignaciones = [];

const nombresEstados = {
    asignada: "Asignada",
    en_produccion: "En producción",
    terminada: "Terminada"
};


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


function nombreEmpleado(empleadoId) {
    if (
        empleadoId === null ||
        empleadoId === undefined
    ) {
        return "No requiere";
    }

    const empleado = obtenerEmpleado(
        empleadoId
    );

    if (empleado === undefined) {
        return `Carpintero #${empleadoId}`;
    }

    return (
        `${empleado.codigo} — ` +
        `${empleado.nombre} ` +
        `${empleado.apellido}`
    );
}


function obtenerDatosRenglon(renglonId) {
    for (const pedido of pedidos) {
        const renglon = pedido.productos.find(
            producto =>
                producto.id === Number(renglonId)
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


function nombreMuebleRenglon(renglonId) {
    const datos = obtenerDatosRenglon(
        renglonId
    );

    if (datos === null) {
        return `Renglón #${renglonId}`;
    }

    const mueble = obtenerMueble(
        datos.renglon.mueble_id
    );

    if (mueble === undefined) {
        return (
            `Mueble #${datos.renglon.mueble_id}`
        );
    }

    return (
        `${mueble.codigo} — ` +
        `${mueble.descripcion} × ` +
        `${datos.renglon.cantidad}`
    );
}


function numeroPedidoRenglon(renglonId) {
    const datos = obtenerDatosRenglon(
        renglonId
    );

    if (datos === null) {
        return "Pedido desconocido";
    }

    return `Pedido #${datos.pedido.id}`;
}


function crearBotonIniciar(asignacionId) {
    const boton = document.createElement(
        "button"
    );

    boton.type = "button";

    boton.textContent =
        "Iniciar producción";

    boton.className = "primary-button";

    boton.dataset.action = "iniciar";
    boton.dataset.id = asignacionId;

    return boton;
}


function mostrarAsignaciones(lista) {
    tablaBody.innerHTML = "";

    if (lista.length === 0) {
        const fila =
            document.createElement("tr");

        const celda =
            document.createElement("td");

        celda.colSpan = puedeIniciar
            ? 8
            : 7;

        celda.textContent =
            "No se encontraron asignaciones";

        celda.className =
            "empty-table-message";

        fila.appendChild(celda);
        tablaBody.appendChild(fila);

        return;
    }

    for (const asignacion of lista) {
        const fila =
            document.createElement("tr");

        const idCelda =
            document.createElement("td");

        idCelda.textContent = asignacion.id;

        const pedidoCelda =
            document.createElement("td");

        pedidoCelda.textContent =
            numeroPedidoRenglon(
                asignacion.pedido_producto_id
            );

        const muebleCelda =
            document.createElement("td");

        muebleCelda.textContent =
            nombreMuebleRenglon(
                asignacion.pedido_producto_id
            );

        const armadoCelda =
            document.createElement("td");

        armadoCelda.textContent =
            nombreEmpleado(
                asignacion.carpintero_armado_id
            );

        const labradoCelda =
            document.createElement("td");

        labradoCelda.textContent =
            nombreEmpleado(
                asignacion.carpintero_labrado_id
            );

        const fechaCelda =
            document.createElement("td");

        fechaCelda.textContent =
            formatearFecha(
                asignacion.fecha_asignacion
            );

        const estadoCelda =
            document.createElement("td");

        const estado =
            document.createElement("span");

        estado.textContent =
            nombresEstados[asignacion.estado] ||
            asignacion.estado;

        estado.className =
            `status-badge ` +
            `status-${asignacion.estado}`;

        estadoCelda.appendChild(estado);

        fila.appendChild(idCelda);
        fila.appendChild(pedidoCelda);
        fila.appendChild(muebleCelda);
        fila.appendChild(armadoCelda);
        fila.appendChild(labradoCelda);
        fila.appendChild(fechaCelda);
        fila.appendChild(estadoCelda);

        if (puedeIniciar) {
            const accionesCelda =
                document.createElement("td");

            accionesCelda.className =
                "table-actions";

            if (
                asignacion.estado ===
                "asignada"
            ) {
                accionesCelda.appendChild(
                    crearBotonIniciar(
                        asignacion.id
                    )
                );
            } else {
                const sinAcciones =
                    document.createElement(
                        "span"
                    );

                sinAcciones.textContent =
                    "Sin acciones";

                sinAcciones.className =
                    "no-actions";

                accionesCelda.appendChild(
                    sinAcciones
                );
            }

            fila.appendChild(accionesCelda);
        }

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

    puedeCrear = [
        "administrador",
        "jefe_carpinteros"
    ].includes(rolActual);

    puedeIniciar = [
        "administrador",
        "carpintero"
    ].includes(rolActual);

    nuevaAsignacionButton.hidden =
        !puedeCrear;

    accionesHeader.hidden =
        !puedeIniciar;

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
        solicitarJson(`${API_URL}/pedidos`),
        solicitarJson(`${API_URL}/muebles`)
    ];

    if (puedeCrear) {
        solicitudes.push(
            solicitarJson(
                `${API_URL}/empleados`
            )
        );
    }

    const resultados = await Promise.all(
        solicitudes
    );

    pedidos = resultados[0];
    muebles = resultados[1];

    empleados = puedeCrear
        ? resultados[2]
        : [];
}


function ordenarAsignaciones(
    lista,
    orden
) {
    return [...lista].sort(
        (asignacionA, asignacionB) => {
            const fechaA = new Date(
                asignacionA.fecha_asignacion
            ).getTime();

            const fechaB = new Date(
                asignacionB.fecha_asignacion
            ).getTime();

            if (orden === "asc") {
                return fechaA - fechaB;
            }

            return fechaB - fechaA;
        }
    );
}


async function cargarAsignaciones(
    orden = "desc"
) {
    try {
        mostrarMensaje(
            "Cargando asignaciones..."
        );

        todasAsignaciones =
            await solicitarJson(
                `${API_URL}/asignaciones`
            );

        mostrarAsignaciones(
            ordenarAsignaciones(
                todasAsignaciones,
                orden
            )
        );

        mostrarMensaje("");
    } catch (error) {
        mostrarAsignaciones([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


async function buscarAsignaciones(event) {
    event.preventDefault();

    const pedidoId =
        buscarPedidoId.value.trim();

    const carpinteroId =
        buscarCarpinteroId.value.trim();

    const estado = buscarEstado.value;
    const orden = buscarOrden.value;

    if (
        pedidoId === "" &&
        carpinteroId === "" &&
        estado === ""
    ) {
        mostrarAsignaciones(
            ordenarAsignaciones(
                todasAsignaciones,
                orden
            )
        );

        mostrarMensaje("");

        return;
    }

    const parametros =
        new URLSearchParams();

    if (pedidoId !== "") {
        parametros.append(
            "pedido_id",
            pedidoId
        );
    }

    if (carpinteroId !== "") {
        parametros.append(
            "carpintero_id",
            carpinteroId
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
            "Buscando asignaciones..."
        );

        const datos = await solicitarJson(
            `${API_URL}/asignaciones/buscar?` +
            parametros.toString()
        );

        mostrarAsignaciones(
            datos.resultados
        );

        mostrarMensaje(
            `Se encontraron ${datos.total} ` +
            "asignación(es)",
            "success"
        );
    } catch (error) {
        mostrarAsignaciones([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


function limpiarBusqueda() {
    busquedaForm.reset();

    mostrarAsignaciones(
        ordenarAsignaciones(
            todasAsignaciones,
            "desc"
        )
    );

    mostrarMensaje("");
}


function llenarCarpinteros() {
    carpinteroArmado.innerHTML =
        '<option value="">' +
        "Seleccionar carpintero" +
        "</option>";

    carpinteroLabrado.innerHTML =
        '<option value="">' +
        "Seleccionar carpintero" +
        "</option>";

    const disponibles = empleados.filter(
        empleado =>
            empleado.activo &&
            empleado.disponible &&
            empleado.puesto ===
                "carpintero"
    );

    for (const empleado of disponibles) {
        const opcion =
            document.createElement("option");

        opcion.value = empleado.id;

        opcion.textContent =
            `${empleado.codigo} — ` +
            `${empleado.nombre} ` +
            `${empleado.apellido}`;

        if (
            empleado.tipo_carpintero ===
            "armado"
        ) {
            carpinteroArmado.appendChild(
                opcion
            );
        } else if (
            empleado.tipo_carpintero ===
            "labrado"
        ) {
            carpinteroLabrado.appendChild(
                opcion
            );
        }
    }
}


function obtenerRenglonesDisponibles(
    pedido
) {
    const idsAsignados = new Set(
        todasAsignaciones.map(
            asignacion =>
                asignacion.pedido_producto_id
        )
    );

    return pedido.productos.filter(
        producto =>
            !idsAsignados.has(producto.id)
    );
}


function llenarPedidosPendientes() {
    asignacionPedido.innerHTML =
        '<option value="">' +
        "Seleccionar pedido" +
        "</option>";

    for (const pedido of pedidos) {
        if (
            pedido.estado !== "pendiente"
        ) {
            continue;
        }

        if (
            obtenerRenglonesDisponibles(
                pedido
            ).length === 0
        ) {
            continue;
        }

        const opcion =
            document.createElement("option");

        opcion.value = pedido.id;

        opcion.textContent =
            `Pedido #${pedido.id} — ` +
            `Cliente #${pedido.cliente_id}`;

        asignacionPedido.appendChild(
            opcion
        );
    }
}


function ocultarLabrado() {
    grupoCarpinteroLabrado.hidden = true;

    carpinteroLabrado.required = false;
    carpinteroLabrado.value = "";
}


function actualizarRenglonesPedido() {
    asignacionRenglon.innerHTML = "";

    ocultarLabrado();

    if (asignacionPedido.value === "") {
        asignacionRenglon.disabled = true;

        asignacionRenglon.innerHTML =
            '<option value="">' +
            "Primero seleccioná un pedido" +
            "</option>";

        return;
    }

    const pedido = pedidos.find(
        item =>
            item.id ===
            Number(asignacionPedido.value)
    );

    if (pedido === undefined) {
        return;
    }

    const renglones =
        obtenerRenglonesDisponibles(
            pedido
        );

    asignacionRenglon.disabled = false;

    asignacionRenglon.innerHTML =
        '<option value="">' +
        "Seleccionar mueble" +
        "</option>";

    for (const renglon of renglones) {
        const mueble = obtenerMueble(
            renglon.mueble_id
        );

        const opcion =
            document.createElement("option");

        opcion.value = renglon.id;

        if (mueble !== undefined) {
            opcion.textContent =
                `${mueble.codigo} — ` +
                `${mueble.descripcion} × ` +
                `${renglon.cantidad}`;
        } else {
            opcion.textContent =
                `Mueble #${renglon.mueble_id}` +
                ` × ${renglon.cantidad}`;
        }

        asignacionRenglon.appendChild(
            opcion
        );
    }
}


function actualizarRequisitoLabrado() {
    ocultarLabrado();

    if (
        asignacionRenglon.value === ""
    ) {
        return;
    }

    const datos = obtenerDatosRenglon(
        Number(asignacionRenglon.value)
    );

    if (datos === null) {
        return;
    }

    const mueble = obtenerMueble(
        datos.renglon.mueble_id
    );

    if (
        mueble !== undefined &&
        mueble.labrado
    ) {
        grupoCarpinteroLabrado.hidden =
            false;

        carpinteroLabrado.required = true;
    }
}


function abrirModal() {
    if (!puedeCrear) {
        return;
    }

    asignacionForm.reset();

    formError.textContent = "";

    ocultarLabrado();
    llenarCarpinteros();
    llenarPedidosPendientes();
    actualizarRenglonesPedido();

    modal.hidden = false;

    asignacionPedido.focus();
}


function cerrarModal() {
    modal.hidden = true;

    asignacionForm.reset();

    formError.textContent = "";

    actualizarRenglonesPedido();
}


async function guardarAsignacion(event) {
    event.preventDefault();

    formError.textContent = "";

    const datosRenglon =
        obtenerDatosRenglon(
            Number(
                asignacionRenglon.value
            )
        );

    if (datosRenglon === null) {
        formError.textContent =
            "Seleccioná un mueble del pedido";

        return;
    }

    const mueble = obtenerMueble(
        datosRenglon.renglon.mueble_id
    );

    const requiereLabrado = Boolean(
        mueble !== undefined &&
        mueble.labrado
    );

    if (
        carpinteroArmado.value === ""
    ) {
        formError.textContent =
            "Seleccioná un carpintero " +
            "de armado";

        return;
    }

    if (
        requiereLabrado &&
        carpinteroLabrado.value === ""
    ) {
        formError.textContent =
            "Este mueble requiere un " +
            "carpintero de labrado";

        return;
    }

    const datos = {
        pedido_producto_id:
            Number(
                asignacionRenglon.value
            ),

        carpintero_armado_id:
            Number(
                carpinteroArmado.value
            ),

        carpintero_labrado_id:
            requiereLabrado
                ? Number(
                    carpinteroLabrado.value
                )
                : null
    };

    try {
        guardarButton.disabled = true;

        guardarButton.textContent =
            "Creando...";

        const creada = await solicitarJson(
            `${API_URL}/asignaciones`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(datos)
            }
        );

        cerrarModal();

        await cargarDatosRelacionados();

        await cargarAsignaciones(
            buscarOrden.value
        );

        mostrarMensaje(
            `Asignación #${creada.id} ` +
            "creada correctamente",
            "success"
        );
    } catch (error) {
        formError.textContent =
            error.message;
    } finally {
        guardarButton.disabled = false;

        guardarButton.textContent =
            "Crear asignación";
    }
}


async function iniciarAsignacion(
    asignacionId
) {
    const confirmado = window.confirm(
        "¿Querés iniciar la producción " +
        "de esta asignación?"
    );

    if (!confirmado) {
        return;
    }

    try {
        await solicitarJson(
            `${API_URL}/asignaciones/` +
            `${asignacionId}/iniciar`,
            {
                method: "PUT"
            }
        );

        pedidos = await solicitarJson(
            `${API_URL}/pedidos`
        );

        await cargarAsignaciones(
            buscarOrden.value
        );

        mostrarMensaje(
            "Producción iniciada correctamente",
            "success"
        );
    } catch (error) {
        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


tablaBody.addEventListener(
    "click",
    async function (event) {
        const boton = event.target.closest(
            'button[data-action="iniciar"]'
        );

        if (boton === null) {
            return;
        }

        await iniciarAsignacion(
            Number(boton.dataset.id)
        );
    }
);


nuevaAsignacionButton.addEventListener(
    "click",
    abrirModal
);

cerrarModalButton.addEventListener(
    "click",
    cerrarModal
);

cancelarButton.addEventListener(
    "click",
    cerrarModal
);

asignacionPedido.addEventListener(
    "change",
    actualizarRenglonesPedido
);

asignacionRenglon.addEventListener(
    "change",
    actualizarRequisitoLabrado
);

asignacionForm.addEventListener(
    "submit",
    guardarAsignacion
);

busquedaForm.addEventListener(
    "submit",
    buscarAsignaciones
);

limpiarBusquedaButton.addEventListener(
    "click",
    limpiarBusqueda
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
        await cargarAsignaciones("desc");
    } catch (error) {
        mostrarAsignaciones([]);

        mostrarMensaje(
            error.message,
            "error"
        );
    }
}


iniciarPagina();