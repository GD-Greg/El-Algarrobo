const API_URL = "http://127.0.0.1:8000";

const loginForm = document.getElementById("login-form");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const captchaInput = document.getElementById("captcha");
const captchaCode = document.getElementById("captcha-code");
const refreshCaptchaButton = document.getElementById("refresh-captcha");
const loginButton = document.querySelector(".login-button");
const mensajeError = document.getElementById("mensaje-error");

let captchaId = null;


async function cargarCaptcha() {
    try {
        mensajeError.textContent = "";
        captchaCode.textContent = "Cargando...";
        captchaInput.value = "";

        const respuesta = await fetch(`${API_URL}/captcha`);

        if (!respuesta.ok) {
            throw new Error("No se pudo obtener el CAPTCHA");
        }

        const datos = await respuesta.json();

        captchaId = datos.captcha_id;
        captchaCode.textContent = datos.captcha;
    } catch (error) {
        captchaId = null;
        captchaCode.textContent = "Error";
        mensajeError.textContent =
            "No se pudo conectar con el servidor";
    }
}


loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    mensajeError.textContent = "";

    if (captchaId === null) {
        mensajeError.textContent =
            "Primero debe generarse un CAPTCHA";
        return;
    }

    const datosLogin = {
        username: usernameInput.value.trim(),
        password: passwordInput.value,
        captcha_id: captchaId,
        captcha: captchaInput.value.trim().toUpperCase()
    };

    try {
        loginButton.disabled = true;
        loginButton.textContent = "Ingresando...";

        const respuesta = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datosLogin)
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            let mensaje = "No se pudo iniciar sesión";

            if (typeof datos.detail === "string") {
                mensaje = datos.detail;
            }

            throw new Error(mensaje);
        }

        localStorage.setItem(
            "access_token",
            datos.access_token
        );

        window.location.href = "dashboard.html";
    } catch (error) {
        await cargarCaptcha();
        mensajeError.textContent = error.message;
    } finally {
        loginButton.disabled = false;
        loginButton.textContent = "Iniciar sesión";
    }
});


refreshCaptchaButton.addEventListener(
    "click",
    cargarCaptcha
);

cargarCaptcha();