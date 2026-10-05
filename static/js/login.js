document.getElementById('formulario-login').addEventListener('submit', async (e) => {
    e.preventDefault(); 

    const correo = document.getElementById('correo-login').value;
    const password = document.getElementById('password-login').value;
    const alerta = document.getElementById('mensaje-alerta');

    const datosLogin = {
        correo: correo,
        password: password
    };

    try {
        
        const respuesta = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datosLogin)
        });

        const resultado = await respuesta.json();

        if (respuesta.status === 200) {

            alerta.style.color = "green";
            alerta.innerText = resultado.mensaje;

            localStorage.setItem(
                'usuario_nombre',
                resultado.usuario.nombre
            );

            localStorage.setItem(
                'usuario_id',
                resultado.usuario.id_usuario
            );

            // =====================================================
            // INICIAR RECOMENDACIÓN INICIAL
            // =====================================================

            sessionStorage.setItem(
                "recomendacion_inicial_en_proceso",
                "true"
            );
            
            fetch('/api/recomendacion-inicial',  {
                method: 'POST'
            })
            .then(async respuestaInicial => {
            
                const resultadoInicial = await respuestaInicial.json();
            
                console.log(
                    "RECOMENDACIÓN INICIAL:",
                    resultadoInicial
                );
            
                
            
            })
            .catch(error => {
            
                console.error(
                    "ERROR EN RECOMENDACIÓN INICIAL:",
                    error
                );
            
                
            
            });
            

            // =====================================================
            // ENTRAR A BOOK WELLNESS
            // =====================================================

            setTimeout(() => {
                window.location.href = "/";
            }, 1500);

        } else {

            alerta.style.color = "red";

            alerta.innerText =
                resultado.error ||
                "Credenciales incorrectas.";
        }

    } catch (error) {

        console.error("Error detectado:", error);

        alerta.style.color = "red";

        alerta.innerText =
            "No hay conexión con el servidor.";
    }
});

