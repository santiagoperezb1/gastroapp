document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    const totalRestanteLabel = document.getElementById('totalRestante').querySelector('.text-value');
    let totalRestanteValue = parseFloat(document.getElementById('totalRestanteValue').textContent) || 0; // Valor sin formato
    const inputDescuento = document.querySelector('.descuento-field');
    const inputPropina = document.querySelector('.propina-field');
    let descuento = parseFloat(inputDescuento.value) || 0;
    let propina = parseFloat(inputPropina.value) || 0;

    // Función para formatear el valor
    function formatearValor(valor) {
        return valor.toLocaleString('es-ES'); // Formato en español para incluir puntos
    }

    // Función para actualizar el total y formatearlo
    function actualizarTotal() {
        totalRestanteLabel.textContent = formatearValor(totalRestanteValue);
    }

    // Inicializar con el valor formateado
    actualizarTotal();

    // Función para ajustar el valor en incrementos de 5
    function ajustarValor(input, valor, incremento) {
        valor = Math.round(valor / incremento) * incremento;
        input.value = valor.toFixed(2);
        return valor;
    }

    // Función para actualizar el total con descuento
    function aplicarDescuento() {
        const totalDescuento = totalRestanteValue * (descuento / 100);
        const totalConDescuento = totalRestanteValue - totalDescuento;
        totalRestanteValue = totalConDescuento; // Actualizar el valor total
        actualizarTotal(); // Actualizar el texto formateado
    }

    // Botones de descuento
    document.getElementById('btnDisminuirDescuento').addEventListener('click', function() {
        descuento = Math.max(0, descuento - 5);
        ajustarValor(inputDescuento, descuento, 5);
    });

    document.getElementById('btnAumentarDescuento').addEventListener('click', function() {
        descuento += 5;
        ajustarValor(inputDescuento, descuento, 5);
    });

    // Botones de domicilio
    document.getElementById('btnDisminuirPropina').addEventListener('click', function() {
        propina = Math.max(0, propina - 1000); // Cambiar de 1 a 1000
        ajustarValor(inputPropina, propina, 1000); // Ajustar en 1000
    });

    document.getElementById('btnAumentarPropina').addEventListener('click', function() {
        propina += 1000; // Cambiar de 1 a 1000
        ajustarValor(inputPropina, propina, 1000); // Ajustar en 1000
    });

    // Aplicar descuento
    document.getElementById('btnAplicarDescuento').addEventListener('click', function() {
        aplicarDescuento();
        alert('Descuento aplicado correctamente: $' + (totalRestanteValue * (descuento / 100)).toFixed(3));
        bloquearBoton(this);
    });

    // Guardar domicilio
    document.getElementById('btnGuardarDomicilio').addEventListener('click', function() {
        totalRestanteValue += propina; // Solo sumar propina al valor total al guardar
        actualizarTotal(); // Actualizar el texto formateado
        alert('Domicilio registrado exitosamente: $' + totalRestanteValue.toFixed(3));
        bloquearBoton(this);
    });

    // Función para bloquear un botón después de hacer clic
    function bloquearBoton(boton) {
        boton.disabled = true;
        boton.style.opacity = '0.5'; // Cambiar la opacidad para dar feedback visual
    }
});

