document.addEventListener('DOMContentLoaded', function() {
    let productosSeleccionados = [];

    function agregarProducto() {
        const selectProducto = document.getElementById('producto_select');
        const cantidadAgregar = document.getElementById('cantidad_agregar').value;
        const productoId = selectProducto.value;
        const productoNombre = selectProducto.options[selectProducto.selectedIndex].text;

        if (productoId && cantidadAgregar > 0) {
            // Agregar producto a la lista de seleccionados
            productosSeleccionados.push({ id: productoId, nombre: productoNombre, cantidad: cantidadAgregar });
            actualizarLista();
        }
    }

    function actualizarLista() {
        const lista = document.getElementById('lista-productos');
        lista.innerHTML = ''; // Limpiar la lista

        const hiddenInputsContainer = document.getElementById('productos-hidden-inputs');
        hiddenInputsContainer.innerHTML = ''; // Limpiar inputs ocultos

        // Recorrer los productos seleccionados y añadir a la lista
        productosSeleccionados.forEach((producto, index) => {
            const item = document.createElement('li');
            item.className = 'list-group-item';
            item.textContent = `${producto.nombre} - Cantidad: ${producto.cantidad}`;
            lista.appendChild(item);

            // Crear inputs ocultos para enviar con el formulario
            const inputProducto = document.createElement('input');
            inputProducto.type = 'hidden';
            inputProducto.name = `productos[${index}][id]`;  // Cambiar a estructura de lista de objetos
            inputProducto.value = producto.id;
            hiddenInputsContainer.appendChild(inputProducto);

            const inputCantidad = document.createElement('input');
            inputCantidad.type = 'hidden';
            inputCantidad.name = `productos[${index}][cantidad]`;  // Cambiar a estructura de lista de objetos
            inputCantidad.value = producto.cantidad;
            hiddenInputsContainer.appendChild(inputCantidad);
        });
    }

    // Añadir el evento al botón para agregar producto
    document.getElementById('agregar_producto_btn').addEventListener('click', agregarProducto);
});
