const carrito = [];
const carritoContenido = document.getElementById('carrito-contenido');
const totalElement = document.getElementById('total');

function actualizarCarrito() {
    carritoContenido.innerHTML = '';
    let total = 0;

    carrito.forEach((item, index) => {
        total += item.precio * item.cantidad;
        carritoContenido.innerHTML += `
            <div>
                ${item.nombre} - $${item.precio} x ${item.cantidad}
                <button onclick="eliminarDelCarrito(${index})" class="btn btn-eliminar btn-sm">Eliminar</button>
            </div>
        `;
    });

    totalElement.innerHTML = `Total: $${total.toFixed(2)}`;
}

function mostrarNotificacion(mensaje) {
    const notificacion = document.getElementById('notificacion');
    notificacion.innerText = mensaje;
    notificacion.classList.remove('d-none');
    notificacion.style.opacity = 1;

    setTimeout(() => {
        notificacion.style.opacity = 0;
        setTimeout(() => {
            notificacion.classList.add('d-none');
        }, 500);
    }, 2000);
}

mostrarNotificacion("Bienvenido al Menú Digital!");

document.querySelectorAll('.agregar-carrito').forEach(button => {
    button.addEventListener('click', () => {
        const nombre = button.getAttribute('data-nombre');
        const precio = parseFloat(button.getAttribute('data-precio'));
        const cantidadSelect = button.previousElementSibling; 
        const cantidad = parseInt(cantidadSelect.value);

        const itemIndex = carrito.findIndex(item => item.nombre === nombre);
        if (itemIndex > -1) {
            carrito[itemIndex].cantidad += cantidad;
        } else {
            carrito.push({ nombre, precio, cantidad });
        }

        actualizarCarrito();
        mostrarNotificacion(`${nombre} agregado al pedido.`);
    });
});

function eliminarDelCarrito(index) {
    carrito.splice(index, 1);
    actualizarCarrito();
    mostrarNotificacion(`producto eliminado del pedido.`);
}

document.getElementById('vaciar-carrito').addEventListener('click', () => {
    carrito.length = 0; // Vaciar el carrito
    actualizarCarrito();
});
