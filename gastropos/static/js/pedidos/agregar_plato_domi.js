// static/js/pedidos/agregar_plato_domi.js

function agregarPlato(platoId) {
    document.getElementById('id_plato').value = platoId;
}

function changeQuantity(delta) {
    var quantityInput = document.getElementById('id_cantidad');
    var currentQuantity = parseInt(quantityInput.value);
    var newQuantity = currentQuantity + delta;
    if (newQuantity < 1) {
        newQuantity = 1;
    }
    quantityInput.value = newQuantity;
}

function agregarPlatoPedido() {
    const form = document.getElementById('agregarPlatoForm');
    const formData = new FormData(form);
    const csrfToken = '{{ csrf_token }}'; // Obtener el token CSRF

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error('Error al agregar el plato: ' + text);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Plato agregado exitosamente');
            location.reload(); // Recargar la página o actualizar la lista de items
        } else {
            alert('Error al agregar el plato');
        }
    })
    .catch(error => console.error('Error al agregar el plato:', error));
}
