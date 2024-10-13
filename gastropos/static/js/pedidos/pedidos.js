$(document).ready(function() {
    console.log("El script se está ejecutando");
    console.log("DOM está listo");

    $('#doc_cliente').on('input', function() {
        console.log("Entrada detectada:", $(this).val()); // Verifica el valor de entrada
        var term = $(this).val();
        if (term.length > 1) {
            $.ajax({
                url: urls.buscarClientes,  // Usa la variable global aquí
                data: {'term': term},
                success: function(data) {
                    console.log("Datos recibidos:", data); // Verifica los datos recibidos
                    var resultadosBusqueda = $('#resultadosBusqueda');
                    resultadosBusqueda.empty();
                    if (data.length > 0) {
                        resultadosBusqueda.show();
                        data.forEach(function(cliente) {
                            resultadosBusqueda.append(
                                '<li class="list-group-item list-group-item-action" data-id="' + cliente.id + '" data-nombre="' + cliente.nombre + '" data-telefono="' + cliente.telefono + '" data-direccion="' + cliente.direccion + '" data-documento="' + cliente.documento + '">' + cliente.nombre + ' - ' + cliente.documento + '</li>'
                            );
                        });
                    } else {
                        resultadosBusqueda.hide();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error en la búsqueda:', xhr.responseText);
                }
            });
        } else {
            $('#resultadosBusqueda').hide();
        }
    });

    $('#resultadosBusqueda').on('click', 'li', function() {
        var nombre = $(this).data('nombre');
        var telefono = $(this).data('telefono');
        var direccion = $(this).data('direccion');
        var documento = $(this).data('documento');

        $('#nombre_cliente').val(nombre);
        $('#telefono_cliente').val(telefono);
        $('#direccion_cliente').val(direccion);
        $('#doc_cliente').val(documento);  // Actualiza el campo doc_cliente
        $('#resultadosBusqueda').hide();
    });

    $('#formPedidoDomicilio').on('submit', function(event) {
        event.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: form.serialize(),
            success: function(response) {
                $('#modalPedidoDomicilio').modal('hide');
                alert('Pedido creado exitosamente');
                if (response.success) {
                    window.location.href = response.redirect_url;
                } else {
                    alert('Ocurrió un error al crear el pedido: ' + response.errors);
                }
            },
            error: function(xhr, status, error) {
                alert('Ocurrió un error al crear el pedido: ' + xhr.responseText);
            }
        });
    });

});
