document.addEventListener('DOMContentLoaded', (event) => {
    const updateTotal = () => {
        let total = 0;
        total += parseInt(document.getElementById('id_monedas_50').value || 0) * 50;
        total += parseInt(document.getElementById('id_monedas_100').value || 0) * 100;
        total += parseInt(document.getElementById('id_monedas_200').value || 0) * 200;
        total += parseInt(document.getElementById('id_monedas_500').value || 0) * 500;
        total += parseInt(document.getElementById('id_monedas_1000').value || 0) * 1000;
        total += parseInt(document.getElementById('id_billetes_2000').value || 0) * 2000;
        total += parseInt(document.getElementById('id_billetes_5000').value || 0) * 5000;
        total += parseInt(document.getElementById('id_billetes_10000').value || 0) * 10000;
        total += parseInt(document.getElementById('id_billetes_20000').value || 0) * 20000;
        total += parseInt(document.getElementById('id_billetes_50000').value || 0) * 50000;
        total += parseInt(document.getElementById('id_billetes_100000').value || 0) * 100000;

        document.getElementById('total_monedas_billetes').value = total.toFixed(2);

         // Actualiza el campo de efectivo inicial
         document.getElementById('id_efectivo_inicial').value = total.toFixed(2);
    };

    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', updateTotal);
    });

    document.querySelectorAll('button[data-action]').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const target = document.querySelector(this.getAttribute('data-target'));
            let currentValue = parseInt(target.value || 0);
            if (action === 'increase') {
                target.value = currentValue + 1;
            } else if (action === 'decrease') {
                target.value = Math.max(currentValue - 1, 0);
            }
            updateTotal();
        });
    });

    updateTotal();
});