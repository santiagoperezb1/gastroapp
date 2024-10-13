document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    const totalRestanteLabel = document.getElementById('totalRestante').querySelector('.text-value');
    const inputDescuento = document.querySelector('.descuento-field');
    const inputPropina = document.querySelector('.propina-field');
    let descuento = parseFloat(inputDescuento.value) || 0;
    let propina = parseFloat(inputPropina.value) || 0;

    // Función para ajustar el valor en incrementos de 5
    function ajustarValor(input, valor, incremento) {
        valor = Math.round(valor / incremento) * incremento;
        input.value = valor.toFixed(2);
        return valor;
    }

    // Función para actualizar el total con descuento
    function actualizarTotalConDescuento() {
        const total = parseFloat(totalRestanteLabel.textContent) || 0;
        const totalDescuento = total * (descuento / 100);
        const totalConDescuento = total - totalDescuento;
        
        totalRestanteLabel.textContent = totalConDescuento.toFixed(3);
        return totalDescuento; // Devuelve el total del descuento aplicado
    }

    // Función para actualizar el total con propina
    function actualizarTotalConPropina() {
        const total = parseFloat(totalRestanteLabel.textContent) || 0;
        const propina_value = (total * propina / 100);
        const totalConPropina = total + propina_value;
        totalRestanteLabel.textContent = totalConPropina.toFixed(3);
        
        return propina_value; 
    }
    
    // Función para bloquear un botón después de hacer clic
    function bloquearBoton(boton) {
        boton.disabled = true;
        boton.style.opacity = '0.5'; // Opcional: Cambiar la opacidad para dar feedback visual
    }

    // Botones de descuento
    document.getElementById('btnDisminuirDescuento').addEventListener('click', function() {
        descuento = Math.max(0, descuento - 5);
        descuento = ajustarValor(inputDescuento, descuento, 5);
    });

    document.getElementById('btnAumentarDescuento').addEventListener('click', function() {
        descuento += 5;
        descuento = ajustarValor(inputDescuento, descuento, 5);
    });

    // Botones de propina
    document.getElementById('btnDisminuirPropina').addEventListener('click', function() {
        propina = Math.max(0, propina - 1);
        propina = ajustarValor(inputPropina, propina, 1);
    });

    document.getElementById('btnAumentarPropina').addEventListener('click', function() {
        propina += 1;
        propina = ajustarValor(inputPropina, propina, 1);
    });

    // Aplicar descuento
    document.getElementById('btnAplicarDescuento').addEventListener('click', function() {
        const totalDescuento = actualizarTotalConDescuento();
        alert('Descuento aplicado correctamente: $' + totalDescuento.toFixed(3));
        bloquearBoton(this);
    });

    // Guardar propina
    document.getElementById('btnGuardarPropina').addEventListener('click', function() {
        const totalConPropina = actualizarTotalConPropina();
        alert('Propina registrada exitosamente: $' + totalConPropina.toFixed(3));
        bloquearBoton(this);
    });
});
