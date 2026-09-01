function cerrarSesion() {

    localStorage.removeItem("access_token");

    window.location.href = "index.html";
}


async function cargarPerfil() {

    const token = localStorage.getItem("access_token");

    // Si no hay token, no dejamos ver el dashboard
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    try {

        const respuesta = await fetch(
            "http://127.0.0.1:8000/perfil",
            {
                headers: {
                    "Authorization": "Bearer " + token
                }
            }
        );

        if (!respuesta.ok) {
            // Token vencido o inválido
            localStorage.removeItem("access_token");
            window.location.href = "login.html";
            return;
        }

        const usuario = await respuesta.json();

        const nombre = document.getElementById("nombreUsuario");

        if (nombre && usuario.nombre) {
            nombre.textContent = usuario.nombre;
        }

    } catch (error) {
        console.error(error);
        window.location.href = "login.html";
    }
}


cargarPerfil();