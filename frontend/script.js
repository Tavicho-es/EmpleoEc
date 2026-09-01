const formulario =
    document.getElementById("registroForm");

const mensaje =
    document.getElementById("mensaje");


formulario.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        const nombre =
            document.getElementById("nombre").value;

        const email =
            document.getElementById("email").value;

        const password =
            document.getElementById("password").value;

        const tipo_usuario =
            document.getElementById("tipo_usuario").value;


        const datos = {

            nombre: nombre,

            email: email,

            password: password,

            tipo_usuario: tipo_usuario

        };


        try {

            const respuesta =
                await fetch(
                    "http://127.0.0.1:8000/registro",
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

                formulario.reset();

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