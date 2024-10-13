document.addEventListener('DOMContentLoaded', function() {
    let lastUpdate = new Date(); // Marca de tiempo de la última actualización

    function checkForUpdates() {
        fetch(pedidosActualizadosUrl + "?last_update=" + lastUpdate.toISOString())
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error('Network response was not ok: ' + text);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.pedidos.length > 0) {
                    data.pedidos.forEach(pedido => {
                        alert(`Nuevo pedido: ${pedido.id} - ${pedido.plato__nombre || pedido.producto__nombre} (${pedido.cantidad})`);
                    });
                    lastUpdate = new Date(Math.max(...data.pedidos.map(p => new Date(p.created_at).getTime())));
                    location.reload();
                }
            })
            .catch(error => console.error('Error al obtener actualizaciones:', error));
    }

    // Revisa si hay actualizaciones cada 5 segundos
    setInterval(checkForUpdates, 5000);
});

function cambiarEstadoItem(itemId) {
    const url = cambiarEstadoUrl.replace('0', itemId);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error('Error al cambiar el estado: ' + text);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Estado actualizado exitosamente');
            location.reload();
        } else {
            alert('Error al actualizar el estado');
        }
    })
    .catch(error => console.error('Error al cambiar el estado:', error));
}

function cambiarEstadoDomiItem(itemId) {
    const url = cambiarEstadoDomiUrl.replace('0', itemId);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error('Error al cambiar el estado: ' + text);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Estado actualizado exitosamente');
            location.reload();
        } else {
            alert('Error al actualizar el estado');
        }
    })
    .catch(error => console.error('Error al cambiar el estado:', error));
}
