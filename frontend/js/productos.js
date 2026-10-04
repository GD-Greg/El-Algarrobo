const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

const productosTableBody = document.getElementById(
    "productos-table-body"
);

const productosMensaje = document.getElementById(
    "productos-mensaje"
);

const busquedaForm = document.getElementById(
    "busqueda-productos-form"
);

const buscarCodigo = document.getElementById(
    "buscar-codigo"
);

const buscarNumeroPedido = document.getElementById(
    "buscar-numero-pedido"
);

const buscarOrden = document.getElementById(
    "buscar-orden"
);

const limpiarBusquedaButton = document.getElementById(
    "limpiar-busqueda-button"
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

const nuevoProductoButton = document.getElementById(
    "nuevo-producto-button"
);

const accionesHeader = document.getElementById(
    "acciones-header"
);

const productoModal = document.getElementById(
    "producto-modal"
);

const productoModalTitle = document.getElementById(
    "producto-modal-title"
);

const cerrarModalButton = document.getElementById(
    "cerrar-modal-button"
);

const cancelarProductoButton = document.getElementById(
    "cancelar-producto-button"
);

const productoForm = document.getElementById(
    "producto-form"
);

const productoFormError = document.getElementById(
    "producto-form-error"
);

const productoId = document.getElementById(
    "producto-id"
);

const productoCodigo = document.getElementById(
    "producto-codigo"
);

const productoDescripcion = document.getElementById(
    "producto-descripcion"
);

const productoTamanos = document.getElementById(
    "producto-tamanos"
);

const productoLabrado = document.getElementById(
    "producto-labrado"
);

const productoPrecio = document.getElementById(
    "producto-precio"
);

const guardarProductoButton = productoForm.querySelector(
    'button[type="submit"]'
);

let esAdministrador = false;


function cerrarSesion() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("usuario_rol");
    window.location.replace("login.html");
}


function mostrarMensaje(texto, tipo = "") {
    productosMensaje.textContent = texto;
    productosMensaje.className = "page-message";

    if (tipo !== "") {
        productosMensaje.classList.add(tipo);
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


function mostrarProductos(productos) {
    productosTableBody.innerHTML = "";

    if (productos.length === 0) {
        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.colSpan = esAdministrador ? 7 : 6;
        celda.textContent = "No se encontraron muebles";
        celda.className = "empty-table-message";

        fila.appendChild(celda);
        productosTableBody.appendChild(fila);

        return;
    }

    const formatoMoneda = new Intl.NumberFormat("es-AR", {
        style: "currency",
        currency: "ARS"
    });

    for (const producto of productos) {
        const fila = document.createElement("tr");

        const valores = [
            producto.id,
            producto.codigo,
            producto.descripcion,
            producto.tamanos_sugeridos,
            producto.labrado ? "Sí" : "No",
            formatoMoneda.format(producto.precio)
        ];

        for (const valor of valores) {
            const celda = document.createElement("td");
            celda.textContent = valor;
            fila.appendChild(celda);
        }

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
            editarButton.dataset.id = producto.id;

            const eliminarButton =
                document.createElement("button");

            eliminarButton.type = "button";
            eliminarButton.textContent = "Eliminar";
            eliminarButton.className = "delete-button";
            eliminarButton.dataset.action = "eliminar";
            eliminarButton.dataset.id = producto.id;

            accionesCelda.appendChild(editarButton);
            accionesCelda.appendChild(eliminarButton);
            fila.appendChild(accionesCelda);
        }

        productosTableBody.appendChild(fila);
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

    localStorage.setItem("usuario_rol", usuario.rol);

    if (
        usuario.rol === "administrador"
        || usuario.rol === "recepcionista"
    ) {
        enlaceClientes.hidden = false;
    }

    if (
        usuario.rol === "administrador"
        || usuario.rol === "jefe_carpinteros"
    ) {
        enlaceEmpleados.hidden = false;
    }

    if (esAdministrador) {
        nuevoProductoButton.hidden = false;
        accionesHeader.hidden = false;
    }

    return true;
}


async function cargarProductos() {
    try {
        mostrarMensaje("Cargando muebles...");

        const respuesta = await fetch(
            `${API_URL}/muebles`,
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
                "No se pudieron cargar los muebles"
            );
        }

        const productos = await respuesta.json();

        mostrarProductos(productos);
        mostrarMensaje("");
    } catch (error) {
        mostrarProductos([]);
        mostrarMensaje(error.message, "error");
    }
}


async function buscarProductos(event) {
    event.preventDefault();

    const codigo = buscarCodigo.value.trim();
    const numeroPedido = buscarNumeroPedido.value;

    if (codigo === "" && numeroPedido === "") {
        await cargarProductos();
        return;
    }

    const parametros = new URLSearchParams();

    if (codigo !== "") {
        parametros.append("codigo", codigo);
    }

    if (numeroPedido !== "") {
        parametros.append(
            "numero_pedido",
            numeroPedido
        );
    }

    parametros.append("orden", buscarOrden.value);

    try {
        mostrarMensaje("Buscando muebles...");

        const respuesta = await fetch(
            `${API_URL}/muebles/buscar?${parametros}`,
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

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                obtenerMensajeError(
                    datos,
                    "No se pudo realizar la búsqueda"
                )
            );
        }

        mostrarProductos(datos.resultados);

        mostrarMensaje(
            `Se encontraron ${datos.total} muebles`,
            "success"
        );
    } catch (error) {
        mostrarProductos([]);
        mostrarMensaje(error.message, "error");
    }
}


async function limpiarBusqueda() {
    busquedaForm.reset();
    await cargarProductos();
}


function abrirModalNuevoProducto() {
    if (!esAdministrador) {
        return;
    }

    productoForm.reset();
    productoId.value = "";
    productoLabrado.value = "false";
    productoFormError.textContent = "";
    productoModalTitle.textContent = "Nuevo mueble";
    productoModal.hidden = false;

    productoCodigo.focus();
}


function cerrarModalProducto() {
    productoModal.hidden = true;
    productoForm.reset();
    productoId.value = "";
    productoFormError.textContent = "";
}


async function guardarProducto(event) {
    event.preventDefault();

    if (!esAdministrador) {
        return;
    }

    productoFormError.textContent = "";

    const datosProducto = {
        codigo: productoCodigo.value.trim(),
        descripcion: productoDescripcion.value.trim(),
        tamanos_sugeridos:
            productoTamanos.value.trim(),
        labrado: productoLabrado.value === "true",
        precio: Number(productoPrecio.value)
    };

    const id = productoId.value;
    const editando = id !== "";

    const url = editando
        ? `${API_URL}/muebles/${id}`
        : `${API_URL}/muebles`;

    const metodo = editando ? "PUT" : "POST";

    try {
        guardarProductoButton.disabled = true;
        guardarProductoButton.textContent =
            "Guardando...";

        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(datosProducto)
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
                    "No se pudo guardar el mueble"
                )
            );
        }

        cerrarModalProducto();
        await cargarProductos();

        const accion = editando
            ? "actualizado"
            : "creado";

        mostrarMensaje(
            `Mueble "${datos.codigo}" ${accion} correctamente`,
            "success"
        );
    } catch (error) {
        productoFormError.textContent = error.message;
    } finally {
        guardarProductoButton.disabled = false;
        guardarProductoButton.textContent = "Guardar";
    }
}


async function abrirModalEditarProducto(
    productoIdSeleccionado
) {
    if (!esAdministrador) {
        return;
    }

    try {
        const respuesta = await fetch(
            `${API_URL}/muebles/${productoIdSeleccionado}`,
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

        const producto = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                obtenerMensajeError(
                    producto,
                    "No se pudo cargar el mueble"
                )
            );
        }

        productoId.value = producto.id;
        productoCodigo.value = producto.codigo;
        productoDescripcion.value =
            producto.descripcion;
        productoTamanos.value =
            producto.tamanos_sugeridos;
        productoLabrado.value =
            String(producto.labrado);
        productoPrecio.value = producto.precio;

        productoFormError.textContent = "";
        productoModalTitle.textContent =
            "Editar mueble";

        productoModal.hidden = false;
        productoCodigo.focus();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


async function eliminarProducto(
    productoIdSeleccionado
) {
    if (!esAdministrador) {
        return;
    }

    const confirmado = window.confirm(
        "¿Seguro que querés eliminar este mueble?"
    );

    if (!confirmado) {
        return;
    }

    try {
        const respuesta = await fetch(
            `${API_URL}/muebles/${productoIdSeleccionado}`,
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
                    "No se pudo eliminar el mueble"
                )
            );
        }

        await cargarProductos();
        mostrarMensaje(datos.mensaje, "success");
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


nuevoProductoButton.addEventListener(
    "click",
    abrirModalNuevoProducto
);

cerrarModalButton.addEventListener(
    "click",
    cerrarModalProducto
);

cancelarProductoButton.addEventListener(
    "click",
    cerrarModalProducto
);

productoForm.addEventListener(
    "submit",
    guardarProducto
);

productoModal.addEventListener(
    "click",
    function (event) {
        if (event.target === productoModal) {
            cerrarModalProducto();
        }
    }
);

productosTableBody.addEventListener(
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
            abrirModalEditarProducto(id);
        }

        if (boton.dataset.action === "eliminar") {
            eliminarProducto(id);
        }
    }
);

busquedaForm.addEventListener(
    "submit",
    buscarProductos
);

limpiarBusquedaButton.addEventListener(
    "click",
    limpiarBusqueda
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

        await cargarProductos();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


iniciarPagina();