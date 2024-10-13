document.addEventListener('DOMContentLoaded', function () {
    console.log("Script loaded");
    const modal = new bootstrap.Modal(document.getElementById('pinModal'));
    const pinInput = document.getElementById('pinInput');
    const pinError = document.getElementById('pinError');
    const submitPin = document.getElementById('submitPin');
    const clearButton = document.getElementById('clearButton');
    const body = document.querySelector('body');

    // Función para manejar la verificación del PIN
    function verifyPin(callback) {
        const pin = pinInput.value;

        if (pin === userPin) {
            pinError.style.display = 'none'; // Ocultar mensaje de error
            modal.hide(); // Cerrar el modal
            body.style.overflow = 'auto'; // Permitir el desplazamiento después de ingresar el PIN
            if (callback) callback(); // Ejecutar la función de callback si se proporciona
        } else {
            pinError.style.display = 'block'; // Mostrar error si el PIN es incorrecto
        }
    }

    // Función para obtener el token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Asegurarte de que confirmDelete esté en el ámbito global
    window.confirmDelete = function(ventaId) {
        console.log("Script Eliminar");
        modal.show(); // Mostrar modal para ingresar el PIN
        submitPin.onclick = function() {
            verifyPin(function() {
                // Hacer una solicitud POST para eliminar el pago
                fetch(`/ventas/eliminar-venta/${ventaId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') // Obtener el token CSRF
                    },
                })
                .then(response => {
                    if (response.ok) {
                        alert('Pago eliminado correctamente.');
                        window.location.href = redirectUrl;
                    } else {
                        alert('Error al eliminar el pago.');
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        };
    };

    // Añadir evento a los botones de la calculadora
    document.querySelectorAll('.button-grid button[data-value]').forEach(button => {
        button.addEventListener('click', function () {
            pinInput.value += this.getAttribute('data-value');
            pinError.style.display = 'none'; // Ocultar mensaje de error al ingresar un nuevo valor
        });
    });

    // Limpiar el campo de entrada
    clearButton.addEventListener('click', function() {
        pinInput.value = '';
        pinError.style.display = 'none'; // Ocultar mensaje de error
    });

});

