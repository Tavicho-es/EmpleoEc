const formulario =
    document.getElementById("loginForm");

const mensaje =
    document.getElementById("mensaje");


formulario.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        const email =
            document.getElementById("email").value;

        const password =
            document.getElementById("password").value;


        const datos = {

            email: email,

            password: password

        };


        try {

            const respuesta =
                await fetch(
                    "http://127.0.0.1:8000/login",
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(datos)

                    }
                );


            const resultado =
                await respuesta.json();


            if (respuesta.ok) {

                mensaje.textContent =
                    "✅ " + resultado.mensaje;

                // Guardamos el token, no los datos crudos
                localStorage.setItem(
                    "access_token",
                    resultado.access_token
                );

                setTimeout(() => {

                    window.location.href =
                        "dashboard.html";

                }, 1000);

            } else {

                mensaje.textContent =
                    "❌ " + resultado.detail;

            }

        }

        catch (error) {

            mensaje.textContent =
                "❌ No se pudo conectar con EmpleaEC";

            console.error(error);

        }

    }
);