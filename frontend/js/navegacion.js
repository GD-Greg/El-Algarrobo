(function () {
    const enlaceAsignaciones =
        document.getElementById(
            "enlace-asignaciones"
        );

    const enlaceProduccion =
        document.getElementById(
            "enlace-produccion"
        );

    if (
        enlaceAsignaciones === null &&
        enlaceProduccion === null
    ) {
        return;
    }

    const token = localStorage.getItem(
        "access_token"
    );

    if (token === null) {
        return;
    }

    async function configurarNavegacion() {
        try {
            const respuesta = await fetch(
                "http://127.0.0.1:8000/staff",
                {
                    headers: {
                        Authorization:
                            `Bearer ${token}`
                    }
                }
            );

            if (!respuesta.ok) {
                return;
            }

            const usuario =
                await respuesta.json();

            const rolesProduccion = [
                "administrador",
                "jefe_carpinteros",
                "carpintero"
            ];

            const puedeVerProduccion =
                rolesProduccion.includes(
                    usuario.rol
                );

            if (
                enlaceAsignaciones !== null
            ) {
                enlaceAsignaciones.hidden =
                    !puedeVerProduccion;
            }

            if (
                enlaceProduccion !== null
            ) {
                enlaceProduccion.hidden =
                    !puedeVerProduccion;
            }
        } catch (error) {
            if (
                enlaceAsignaciones !== null
            ) {
                enlaceAsignaciones.hidden = true;
            }

            if (
                enlaceProduccion !== null
            ) {
                enlaceProduccion.hidden = true;
            }
        }
    }

    configurarNavegacion();
})();