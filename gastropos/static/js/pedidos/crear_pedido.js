// Definición de las URLs
var urls = {
    buscarClientes: document.getElementById('buscar-clientes-url').value,
    cargarDetallePedido: document.getElementById('cargar-detalle-pedido-url').value,
    editarPlato: document.getElementById('editar-plato-url').value,
    eliminarPlato: document.getElementById('eliminar-plato-url').value
};

// Función para mostrar los detalles del pedido
function showDetails(pedidoId) {
    $.ajax({
        url: urls.cargarDetallePedido.replace('0', pedidoId),
        type: "GET",
        success: function(data) {
            $('#modalBody').html(data.html);
            $('#pedidoDetailsModal').modal('show');
        },
        error: function() {
            alert('Error al cargar los detalles del pedido.');
        }
    });
}

// Función para editar un plato
function editarPlato(itemId, pedidoId) {
    const cantidad = document.getElementById(`cantidad_${itemId}`).value;
    $.ajax({
        url: urls.editarPlato.replace('0', itemId).replace('0', pedidoId),
        type: "POST",
        data: {
            'cantidad': cantidad,
            'csrfmiddlewaretoken': csrfToken // Asegúrate de que esto esté definido correctamente
        },
        success: function(data) {
            alert('Plato editado exitosamente.');
            $('#pedidoDetailsModal').modal('hide');
            location.reload();
        },
        error: function() {
            alert('Error al editar el plato.');
        }
    });
}

// Función para eliminar un plato
function eliminarPlato(itemId, pedidoId) {
    $.ajax({
        url: urls.eliminarPlato.replace('0', itemId).replace('0', pedidoId),
        type: "POST",
        data: {
            'csrfmiddlewaretoken': csrfToken // Asegúrate de que esto esté definido correctamente
        },
        success: function(data) {
            alert('Plato eliminado exitosamente.');
            $('#pedidoDetailsModal').modal('hide');
            location.reload();
        },
        error: function() {
            alert('Error al eliminar el plato.');
        }
    });
}
